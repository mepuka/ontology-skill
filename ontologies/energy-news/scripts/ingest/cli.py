"""Click CLI for the Energy News ABox ETL pipeline.

Commands:
    resolve  — Resolve generic shortener URLs (async HTTP HEAD)
    run      — Run the full ETL pipeline (extract → transform → load)
    stats    — Query the Oxigraph store for triple counts
"""

from __future__ import annotations

from pathlib import Path

import click
from rdflib import Graph

from .dedup import deduplicate_articles
from .extract import extract_from_file, extract_from_skygent
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
@click.option("--file", "file_path", type=click.Path(exists=True), help="NDJSON file path.")
@click.option("--limit", type=int, default=None, help="Max posts to extract for resolution scan.")
@click.option("--concurrency", type=int, default=20, help="HTTP concurrency for resolution.")
def resolve(source: str, file_path: str | None, limit: int | None, concurrency: int) -> None:
    """Resolve generic shortener URLs and populate the cache."""
    cache_path = PROJECT / "data" / "shortener-cache.json"

    print("=== Shortener Resolution ===")
    print(f"  Cache: {cache_path}")

    # Extract posts
    print("  Extracting posts...")
    if source == "file" and file_path:
        posts = list(extract_from_file(Path(file_path)))
    else:
        posts = list(extract_from_skygent(limit=limit))
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
    "--source",
    type=click.Choice(["skygent", "file"]),
    default="skygent",
    help="Data source.",
)
@click.option("--file", "file_path", type=click.Path(exists=True), help="NDJSON file path.")
@click.option("--limit", type=int, default=None, help="Max posts to ingest.")
@click.option("--validate/--no-validate", default=True, help="Run SHACL validation.")
@click.option("--snapshot/--no-snapshot", default=True, help="Write Turtle snapshot file.")
def run(
    source: str,
    file_path: str | None,
    limit: int | None,
    validate: bool,
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
        posts = list(extract_from_skygent(limit=limit))
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
        print("\n[5/6] Running SHACL validation (warn mode)...")
        merged = Graph()
        merged.parse(str(tbox_path), format="turtle")
        merged.parse(str(ref_path), format="turtle")
        merged += abox_graph

        shapes = Graph()
        shapes.parse(str(shapes_path), format="turtle")

        conforms, results_text = validate_abox(merged, shapes)
        if conforms:
            print("  SHACL: passed (warn mode)")
        else:
            print(f"  SHACL issues:\n{results_text}")
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
