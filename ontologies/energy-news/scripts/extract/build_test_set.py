"""Build a stratified 50-article test set from the article cache.

Stratification:
  - Proportional across top 10 succeeded domains
  - Spanning p25/p50/p75/p90 size buckets within each domain
  - Pre-filtered to articles with text > 100 chars

Usage:
    uv run python scripts/extract/build_test_set.py
    uv run python scripts/extract/build_test_set.py --count 100
    uv run python scripts/extract/build_test_set.py --output data/test-set-100.ndjson
"""

from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path

# Defaults
DEFAULT_COUNT = 50
DEFAULT_CACHE = Path("data/article-text-cache.ndjson")
DEFAULT_OUTPUT = Path("data/test-set-50.ndjson")
SEED = 42


def load_succeeded_articles(cache_path: Path) -> list[dict]:
    """Load all succeeded articles with text > 100 chars."""
    articles = []
    with cache_path.open() as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("state") == "succeeded" and rec.get("text") and len(rec["text"]) > 100:
                articles.append(rec)
    return articles


def compute_size_bucket(text_len: int, percentiles: dict[str, int]) -> str:
    """Assign a size bucket label based on percentile thresholds."""
    if text_len <= percentiles["p25"]:
        return "small"
    if text_len <= percentiles["p50"]:
        return "medium"
    if text_len <= percentiles["p75"]:
        return "large"
    return "xlarge"


def stratified_sample(
    articles: list[dict],
    count: int,
    *,
    seed: int = SEED,
) -> list[dict]:
    """Sample articles stratified by domain and size bucket."""
    rng = random.Random(seed)

    # Group by domain
    by_domain: defaultdict[str, list[dict]] = defaultdict(list)
    for a in articles:
        by_domain[a["domain"]].append(a)

    # Top domains by count
    domain_counts = Counter(a["domain"] for a in articles)
    top_domains = [d for d, _ in domain_counts.most_common(10)]

    # Compute global size percentiles
    sizes = sorted(len(a["text"]) for a in articles)
    percentiles = {
        "p25": sizes[len(sizes) // 4],
        "p50": sizes[len(sizes) // 2],
        "p75": sizes[3 * len(sizes) // 4],
    }

    # Allocate quota per domain proportional to its share of the corpus
    total_top = sum(domain_counts[d] for d in top_domains)
    domain_quotas: dict[str, int] = {}
    allocated = 0
    for d in top_domains:
        quota = max(2, round(count * domain_counts[d] / total_top))
        domain_quotas[d] = quota
        allocated += quota

    # Adjust to hit target count
    while allocated > count:
        largest = max(domain_quotas, key=lambda d: domain_quotas[d])
        domain_quotas[largest] -= 1
        allocated -= 1
    while allocated < count:
        smallest = min(domain_quotas, key=lambda d: domain_quotas[d])
        domain_quotas[smallest] += 1
        allocated += 1

    # Sample within each domain, stratified by size bucket
    selected: list[dict] = []
    for domain in top_domains:
        quota = domain_quotas[domain]
        domain_articles = by_domain[domain]

        # Group by size bucket
        buckets: defaultdict[str, list[dict]] = defaultdict(list)
        for a in domain_articles:
            bucket = compute_size_bucket(len(a["text"]), percentiles)
            buckets[bucket].append(a)

        # Try to sample evenly across buckets
        per_bucket = max(1, quota // max(len(buckets), 1))
        domain_selected: list[dict] = []

        for bucket_name in ["small", "medium", "large", "xlarge"]:
            pool = buckets.get(bucket_name, [])
            if not pool:
                continue
            n = min(per_bucket, len(pool))
            domain_selected.extend(rng.sample(pool, n))

        # Fill remaining quota from any bucket
        remaining = quota - len(domain_selected)
        if remaining > 0:
            already = {a["url"] for a in domain_selected}
            pool = [a for a in domain_articles if a["url"] not in already]
            if pool:
                domain_selected.extend(rng.sample(pool, min(remaining, len(pool))))

        selected.extend(domain_selected[:quota])

    return selected


def main() -> None:
    """CLI entrypoint."""
    import argparse

    parser = argparse.ArgumentParser(description="Build stratified test set")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT, help="Number of articles")
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE, help="Article cache path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output NDJSON path")
    parser.add_argument("--seed", type=int, default=SEED, help="Random seed")
    args = parser.parse_args()

    print(f"Loading articles from {args.cache}...")
    articles = load_succeeded_articles(args.cache)
    print(f"  {len(articles)} succeeded articles with text > 100 chars")

    print(f"Sampling {args.count} articles (seed={args.seed})...")
    selected = stratified_sample(articles, args.count, seed=args.seed)

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        for a in selected:
            # Output only the fields needed for extraction
            out = {
                "url": a["url"],
                "title": a.get("title", ""),
                "date": a.get("date", ""),
                "domain": a["domain"],
                "text": a["text"],
            }
            f.write(json.dumps(out) + "\n")

    # Summary
    domain_counts = Counter(a["domain"] for a in selected)
    sizes = [len(a["text"]) for a in selected]
    print(f"\nWrote {len(selected)} articles to {args.output}")
    print(f"  Domains: {dict(domain_counts.most_common())}")
    print(f"  Size range: {min(sizes):,} - {max(sizes):,} chars")
    print(f"  Median size: {sorted(sizes)[len(sizes) // 2]:,} chars")


if __name__ == "__main__":
    main()
