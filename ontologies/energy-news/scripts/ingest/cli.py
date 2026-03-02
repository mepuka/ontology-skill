"""Click CLI for the Energy News ABox ETL pipeline.

Commands:
    fetch    — Fetch/extract article text into NDJSON sidecar cache
    resolve  — Resolve generic shortener URLs (async HTTP HEAD)
    run      — Run the full ETL pipeline (extract → transform → load)
    stats    — Query the Oxigraph store for triple counts
"""

from __future__ import annotations

import asyncio
from collections import Counter
from pathlib import Path

import click
from rdflib import Graph

from .dedup import deduplicate_articles
from .extract import extract_from_file, extract_from_skygent
from .fetcher import extract_candidate_urls, load_domain_policy, run_fetch_pipeline
from .publications import build_ref_publication_index
from .shorteners import (
    collect_shortener_urls,
    load_cache,
    resolve_generic_shorteners,
    save_cache,
)
from .store import init_store, load_abox, load_tbox
from .store import stats as store_stats
from .topics import build_topic_lookup
from .transform import transform_posts
from .validate import validate_abox

# Ontology project root
PROJECT = Path(__file__).resolve().parent.parent.parent


@click.group()
def cli() -> None:
    """Energy News ABox ETL pipeline."""


@cli.command()
@click.option(
    "--source",
    type=click.Choice(["skygent", "file"]),
    default="skygent",
    help="Data source: 'skygent' (live CLI) or 'file' (NDJSON path).",
)
@click.option("--store", default="energy-news", help="SkyGent store name (default: energy-news).")
@click.option("--file", "file_path", type=click.Path(exists=True), help="NDJSON file path.")
@click.option("--limit", type=int, default=None, help="Max posts to extract for resolution scan.")
@click.option("--concurrency", type=int, default=20, help="HTTP concurrency for resolution.")
def resolve(
    source: str, store: str, file_path: str | None, limit: int | None, concurrency: int
) -> None:
    """Resolve generic shortener URLs and populate the cache."""
    cache_path = PROJECT / "data" / "shortener-cache.json"

    print("=== Shortener Resolution ===")
    print(f"  Cache: {cache_path}")

    # Extract posts
    print("  Extracting posts...")
    if source == "file" and file_path:
        posts = list(extract_from_file(Path(file_path)))
    else:
        posts = list(extract_from_skygent(store=store, limit=limit))
    print(f"  Extracted {len(posts)} posts")

    # Collect shortener URLs
    shortener_urls = collect_shortener_urls(posts)
    print(f"  Found {len(shortener_urls)} unique generic shortener URLs")

    if not shortener_urls:
        print("  No shortener URLs to resolve.")
        return

    # Load existing cache and resolve
    cache = load_cache(cache_path)
    cache = resolve_generic_shorteners(shortener_urls, cache, concurrency=concurrency)
    save_cache(cache, cache_path)
    print(f"  Cache saved: {len(cache)} total entries")


@cli.command()
@click.option(
    "--concurrency",
    type=int,
    default=20,
    show_default=True,
    help="Global HTTP concurrency.",
)
@click.option(
    "--domain-delay",
    type=float,
    default=1.0,
    show_default=True,
    help="Seconds between requests to same domain.",
)
@click.option(
    "--request-timeout",
    type=float,
    default=20.0,
    show_default=True,
    help="Connect/read/write/pool timeout in seconds.",
)
@click.option(
    "--max-retries",
    type=int,
    default=3,
    show_default=True,
    help="Retry attempts for retryable failures.",
)
@click.option(
    "--max-bytes",
    type=int,
    default=2_000_000,
    show_default=True,
    help="Max response body bytes per URL.",
)
@click.option(
    "--queue-size",
    type=int,
    default=200,
    show_default=True,
    help="Bounded queue size for pipeline backpressure.",
)
@click.option(
    "--user-agent",
    type=str,
    default="energy-news-fetcher/1.0",
    show_default=True,
    help="HTTP User-Agent string.",
)
@click.option("--limit", type=int, default=None, help="Max URLs to fetch.")
@click.option("--domain", type=str, default=None, help="Fetch only this domain (or subdomains).")
@click.option(
    "--resume/--no-resume",
    default=True,
    show_default=True,
    help="Resume using cache state.",
)
@click.option(
    "--cache-path",
    type=click.Path(path_type=Path),
    default=None,
    help="NDJSON cache path (default: data/article-text-cache.ndjson).",
)
@click.option(
    "--policy-path",
    type=click.Path(path_type=Path),
    default=None,
    help="Domain policy YAML path (default: scripts/ingest/policy/domains.yml).",
)
@click.option(
    "--fail-fast-threshold",
    type=click.FloatRange(min=0.0, max=1.0),
    default=0.95,
    show_default=True,
    help="Abort when sustained failure ratio reaches this threshold.",
)
@click.option(
    "--progress-every",
    type=click.IntRange(min=0),
    default=50,
    show_default=True,
    help="Print progress every N processed events (0 disables progress logs).",
)
def fetch(
    concurrency: int,
    domain_delay: float,
    request_timeout: float,
    max_retries: int,
    max_bytes: int,
    queue_size: int,
    user_agent: str,
    limit: int | None,
    domain: str | None,
    resume: bool,
    cache_path: Path | None,
    policy_path: Path | None,
    fail_fast_threshold: float,
    progress_every: int,
) -> None:
    """Fetch article text from article URLs in the Oxigraph ABox."""
    store_path = PROJECT / "data" / "oxigraph"
    resolved_cache_path = cache_path or (PROJECT / "data" / "article-text-cache.ndjson")
    resolved_policy_path = policy_path or (
        PROJECT / "scripts" / "ingest" / "policy" / "domains.yml"
    )

    if not store_path.exists():
        raise click.ClickException("No Oxigraph store found. Run 'ingest run' first.")

    print("=== Article Fetch ===")
    print(f"  Store: {store_path}")
    print(f"  Cache: {resolved_cache_path}")
    print(f"  Policy: {resolved_policy_path}")
    print(f"  Concurrency: {concurrency}")
    print(f"  Domain delay: {domain_delay}s")
    print(f"  Request timeout: {request_timeout}s")
    print(f"  Max retries: {max_retries}")
    print(f"  Progress interval: {progress_every}")

    policy = load_domain_policy(resolved_policy_path)
    urls = extract_candidate_urls(store_path, domain=domain, limit=limit)
    print(f"  Candidate URLs: {len(urls)}")

    if not urls:
        print("  No candidate URLs to fetch.")
        return

    try:
        stats = asyncio.run(
            run_fetch_pipeline(
                urls=urls,
                cache_path=resolved_cache_path,
                concurrency=concurrency,
                domain_delay=domain_delay,
                request_timeout=request_timeout,
                max_retries=max_retries,
                max_bytes=max_bytes,
                queue_size=queue_size,
                user_agent=user_agent,
                resume=resume,
                domain_policy=policy,
                fail_fast_threshold=fail_fast_threshold,
                progress_every=progress_every,
            )
        )
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc

    print("--- Summary ---")
    print(f"  Processed events: {stats.processed}")
    print(f"  Succeeded: {stats.succeeded}")
    print(f"  Retryable failures: {stats.retryable_failed}")
    print(f"  Terminal failures: {stats.terminal_failed}")
    print(f"  Skipped by policy: {stats.skipped_policy}")
    print(f"  Skipped by resume terminal state: {stats.skipped_terminal_resume}")
    print(f"  Malformed resume lines: {stats.malformed_resume_lines}")
    print(f"  Bytes fetched: {stats.bytes_fetched}")


@cli.command()
@click.option(
    "--source",
    type=click.Choice(["skygent", "file"]),
    default="skygent",
    help="Data source.",
)
@click.option("--store", default="energy-news", help="SkyGent store name (default: energy-news).")
@click.option("--file", "file_path", type=click.Path(exists=True), help="NDJSON file path.")
@click.option("--limit", type=int, default=None, help="Max posts to ingest.")
@click.option("--validate/--no-validate", default=True, help="Run SHACL validation.")
@click.option("--strict/--no-strict", default=False, help="SHACL strict mode (fail on violations).")
@click.option("--snapshot/--no-snapshot", default=True, help="Write Turtle snapshot file.")
def run(
    source: str,
    store: str,
    file_path: str | None,
    limit: int | None,
    validate: bool,
    strict: bool,
    snapshot: bool,
) -> None:
    """Run the full ETL pipeline: extract → transform → dedup → validate → load."""
    ref_path = PROJECT / "energy-news-reference-individuals.ttl"
    tbox_path = PROJECT / "energy-news.ttl"
    shapes_path = PROJECT / "shapes" / "energy-news-shapes.ttl"
    cache_path = PROJECT / "data" / "shortener-cache.json"
    store_path = PROJECT / "data" / "oxigraph"
    snapshot_path = PROJECT / "data" / "abox-snapshot.ttl"

    print("=== Energy News ABox ETL Pipeline ===\n")
    print(f"  SkyGent store: {store}")

    # --- Load reference data ---
    print("[1/6] Loading reference data...")
    ref_graph = Graph()
    ref_graph.parse(str(ref_path), format="turtle")
    print(f"  Reference individuals: {len(ref_graph)} triples")

    pub_index = build_ref_publication_index(ref_graph)
    print(f"  Publication index: {len(pub_index.domains)} reference domains")

    topic_lookup = build_topic_lookup(ref_graph)
    print(f"  Topic lookup: {len(topic_lookup.keywords)} keywords")

    shortener_cache = load_cache(cache_path)
    print(f"  Shortener cache: {len(shortener_cache)} entries")

    # --- Extract ---
    print("\n[2/6] Extracting posts...")
    if source == "file" and file_path:
        posts = list(extract_from_file(Path(file_path)))
    else:
        posts = list(extract_from_skygent(store=store, limit=limit))
    print(f"  Extracted {len(posts)} posts")

    # --- Transform ---
    print("\n[3/6] Transforming posts → RDF...")
    abox_graph, stats = transform_posts(posts, pub_index, topic_lookup, shortener_cache)
    print(f"  Posts: {stats.posts}")
    print(f"  Authors: {stats.authors}")
    print(f"  External embeds: {stats.embeds_external}")
    print(f"  Image embeds: {stats.embeds_images}")
    print(f"  Video embeds: {stats.embeds_video}")
    print(f"  Record embeds: {stats.embeds_record}")
    print(f"  RecordWithMedia: {stats.embeds_record_with_media}")
    print(f"  No embed: {stats.embeds_none}")
    print(f"  Articles: {stats.articles}")
    print(f"  Media attachments: {stats.media_attachments}")
    print(f"  Topics matched: {stats.topics_matched}")
    print(f"  ABox triples: {len(abox_graph)}")

    # --- Dedup ---
    print("\n[4/6] Deduplicating articles...")
    merged_count = deduplicate_articles(abox_graph)
    print(f"  Merged {merged_count} duplicate articles")
    print(f"  ABox triples after dedup: {len(abox_graph)}")

    # --- Validate ---
    if validate:
        mode_label = "strict" if strict else "warn"
        print(f"\n[5/6] Running SHACL validation ({mode_label} mode)...")
        # Parse TBox/ref into the ABox graph in-place to avoid doubling memory
        pre_count = len(abox_graph)
        abox_graph.parse(str(tbox_path), format="turtle")
        abox_graph.parse(str(ref_path), format="turtle")
        print(f"  Merged TBox+ref into ABox: {pre_count} → {len(abox_graph)} triples")

        shapes = Graph()
        shapes.parse(str(shapes_path), format="turtle")

        conforms, results_text = validate_abox(abox_graph, shapes, strict=strict)
        if conforms:
            print(f"  SHACL: passed ({mode_label} mode)")
        else:
            # Summarize violations instead of dumping the full report
            report_lines = results_text.strip().split("\n")
            result_count = sum(
                1 for line in report_lines if line.startswith("Constraint Violation")
            )
            print(f"  SHACL: {result_count} violations found ({mode_label} mode)")
            # Group by path
            paths = [
                line.strip() for line in report_lines if line.strip().startswith("Result Path:")
            ]
            for path, count in Counter(paths).most_common():
                print(f"    {path}: {count}")
            msgs = [line.strip() for line in report_lines if line.strip().startswith("Message:")]
            for msg, count in Counter(msgs).most_common(5):
                print(f"    {msg} (x{count})")
    else:
        print("\n[5/6] Skipping SHACL validation")

    # --- Load into Oxigraph ---
    print("\n[6/6] Loading into Oxigraph store...")
    store = init_store(store_path)
    load_tbox(store, PROJECT)
    abox_count = load_abox(store, abox_graph)
    print(f"  ABox loaded: {abox_count} triples → <urn:enews:graph:abox>")

    # --- Snapshot ---
    if snapshot:
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        abox_graph.serialize(destination=str(snapshot_path), format="turtle")
        print(f"  Snapshot: {snapshot_path}")

    # --- Summary ---
    print("\n=== Store Statistics ===")
    for name, count in store_stats(store).items():
        print(f"  {name}: {count}")

    store.flush()
    print("\nDone.")


@cli.command()
def stats() -> None:
    """Query the Oxigraph store for triple counts and sample data."""
    store_path = PROJECT / "data" / "oxigraph"
    if not store_path.exists():
        print("No Oxigraph store found. Run 'ingest run' first.")
        return

    store = init_store(store_path)
    counts = store_stats(store)

    print("=== Oxigraph Store Statistics ===")
    for name, count in counts.items():
        print(f"  {name}: {count:,}")

    # Sample queries (use GRAPH ?g to query across named graphs)
    print("\n--- Top 10 Publications by Article Count ---")
    sparql = """
    PREFIX enews: <http://example.org/ontology/energy-news#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?pub ?label (COUNT(?article) AS ?count)
    WHERE {
        GRAPH ?g1 { ?article a enews:Article ; enews:publishedBy ?pub . }
        GRAPH ?g2 { ?pub rdfs:label ?label . }
    }
    GROUP BY ?pub ?label
    ORDER BY DESC(?count)
    LIMIT 10
    """
    results = store.query(sparql)
    for row in results:
        print(f"  {row[1].value}: {row[2].value}")

    print("\n--- Entity Counts ---")
    sparql_counts = """
    PREFIX enews: <http://example.org/ontology/energy-news#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?type (COUNT(?x) AS ?count)
    WHERE {
        GRAPH ?g {
            ?x rdf:type ?type .
            FILTER(?type IN (
                enews:Post, enews:AuthorAccount, enews:Article,
                enews:EmbeddedExternalLink, enews:MediaAttachment,
                enews:Publication
            ))
        }
    }
    GROUP BY ?type
    ORDER BY DESC(?count)
    """
    results = store.query(sparql_counts)
    for row in results:
        type_name = str(row[0].value).split("#")[-1]
        print(f"  {type_name}: {row[1].value}")


if __name__ == "__main__":
    cli()
