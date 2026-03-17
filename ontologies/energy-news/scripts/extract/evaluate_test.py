"""Evaluate extraction results from effect-langextract.

Compares single or multiple result files, producing metrics on:
  1. Entity count distribution by class
  2. Relationship extraction rate
  3. Character grounding quality (% with valid charInterval)
  4. Structured field parsing (capacity/price regex success rate)
  5. Per-article extraction density

Usage:
    uv run python scripts/extract/evaluate_test.py results.jsonl
    uv run python scripts/extract/evaluate_test.py results1.jsonl results2.jsonl
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ENTITY_CLASSES = frozenset(
    {
        "Organization",
        "RegulatoryBody",
        "GeographicEntity",
        "GridZone",
        "EnergyProject",
        "PowerPlant",
        "RenewableInstallation",
        "EnergyTechnology",
        "PolicyInstrument",
        "CapacityMeasurement",
        "PriceDataPoint",
        "EnergyEvent",
        "Person",
    }
)

CAPACITY_RE = re.compile(
    r"([\d,.]+)\s*(MW|GW|MWh|GWh|kW|kWh|TW|TWh)",
    re.IGNORECASE,
)

PRICE_RE = re.compile(
    r"[\$€£¥][\d,.]+|[\d,.]+\s*(?:USD|EUR|GBP|JPY|CNY|per\s*MWh|/MWh|/kWh)",
    re.IGNORECASE,
)


def load_results(path: Path) -> list[dict]:
    """Load JSONL extraction results."""
    results = []
    with path.open() as f:
        for raw_line in f:
            stripped = raw_line.strip()
            if stripped:
                results.append(json.loads(stripped))
    return results


def evaluate_results(results: list[dict]) -> dict:
    """Compute evaluation metrics for a set of extraction results."""
    metrics: dict = {}
    class_counts: Counter[str] = Counter()
    per_article_counts: list[int] = []
    articles_with_relationships = 0
    total_extractions = 0
    extractions_with_char_interval = 0
    valid_char_intervals = 0
    capacity_extractions = 0
    capacity_parseable = 0
    price_extractions = 0
    price_parseable = 0
    relationship_type_counts: Counter[str] = Counter()

    for doc in results:
        extractions = doc.get("extractions", [])
        text = doc.get("text", "")
        per_article_counts.append(len(extractions))
        has_relationship = False

        for ext in extractions:
            total_extractions += 1
            ext_class = ext.get("extractionClass", "")
            ext_text = ext.get("extractionText", "")
            class_counts[ext_class] += 1

            # charInterval quality
            ci = ext.get("charInterval")
            if ci and ci.get("startPos") is not None and ci.get("endPos") is not None:
                extractions_with_char_interval += 1
                start = ci["startPos"]
                end = ci["endPos"]
                if text and 0 <= start < end <= len(text):
                    actual = text[start:end]
                    if actual == ext_text:
                        valid_char_intervals += 1

            # Capacity parsing
            if ext_class == "CapacityMeasurement":
                capacity_extractions += 1
                # Check attributes first
                attrs = ext.get("attributes", {})
                if attrs.get("valueInMW") or CAPACITY_RE.search(ext_text):
                    capacity_parseable += 1

            # Price parsing
            if ext_class == "PriceDataPoint":
                price_extractions += 1
                attrs = ext.get("attributes", {})
                if attrs.get("priceValue") or PRICE_RE.search(ext_text):
                    price_parseable += 1

            # Relationships
            if ext_class == "Relationship":
                has_relationship = True
                attrs = ext.get("attributes", {})
                rt = attrs.get("relationshipType", "unknown")
                relationship_type_counts[rt] += 1

        if has_relationship:
            articles_with_relationships += 1

    n_articles = len(results)
    metrics["article_count"] = n_articles
    metrics["total_extractions"] = total_extractions
    metrics["avg_extractions_per_article"] = total_extractions / n_articles if n_articles else 0

    # Per-article distribution
    if per_article_counts:
        s = sorted(per_article_counts)
        metrics["extractions_per_article"] = {
            "min": s[0],
            "p25": s[len(s) // 4],
            "median": s[len(s) // 2],
            "p75": s[3 * len(s) // 4],
            "max": s[-1],
        }
        metrics["articles_with_zero_extractions"] = sum(1 for c in s if c == 0)

    # Class distribution
    metrics["class_distribution"] = dict(class_counts.most_common())
    metrics["entity_classes_found"] = len(ENTITY_CLASSES & set(class_counts.keys()))
    metrics["entity_classes_total"] = len(ENTITY_CLASSES)

    # Relationship metrics
    metrics["relationship_rate"] = articles_with_relationships / n_articles if n_articles else 0
    metrics["relationship_type_distribution"] = dict(relationship_type_counts.most_common())

    # charInterval quality
    metrics["char_interval_rate"] = (
        extractions_with_char_interval / total_extractions if total_extractions else 0
    )
    metrics["char_interval_valid_rate"] = (
        valid_char_intervals / extractions_with_char_interval
        if extractions_with_char_interval
        else 0
    )

    # Structured field parsing
    metrics["capacity_parseable_rate"] = (
        capacity_parseable / capacity_extractions if capacity_extractions else 0
    )
    metrics["price_parseable_rate"] = (
        price_parseable / price_extractions if price_extractions else 0
    )

    return metrics


def print_report(label: str, metrics: dict) -> None:
    """Print a formatted evaluation report."""
    print(f"\n{'=' * 70}")
    print(f"  {label}")
    print(f"{'=' * 70}")

    print(f"\n  Articles: {metrics['article_count']}")
    print(f"  Total extractions: {metrics['total_extractions']}")
    print(f"  Avg per article: {metrics['avg_extractions_per_article']:.1f}")
    print(f"  Zero-extraction articles: {metrics.get('articles_with_zero_extractions', 0)}")

    dist = metrics.get("extractions_per_article", {})
    if dist:
        print(
            f"  Distribution: min={dist['min']} p25={dist['p25']} "
            f"med={dist['median']} p75={dist['p75']} max={dist['max']}"
        )

    found = metrics["entity_classes_found"]
    total = metrics["entity_classes_total"]
    print(f"\n  Entity classes found: {found}/{total}")
    print("  Class distribution:")
    for cls, count in sorted(metrics["class_distribution"].items(), key=lambda x: -x[1]):
        bar = "#" * min(count, 50)
        entity_mark = "" if cls in ENTITY_CLASSES or cls == "Relationship" else " (?)"
        print(f"    {cls:30s} {count:5d}  {bar}{entity_mark}")

    print(f"\n  Relationship rate: {metrics['relationship_rate']:.1%} of articles")
    if metrics["relationship_type_distribution"]:
        print("  Relationship types:")
        for rt, count in sorted(
            metrics["relationship_type_distribution"].items(), key=lambda x: -x[1]
        ):
            print(f"    {rt:30s} {count:5d}")

    print(f"\n  charInterval coverage: {metrics['char_interval_rate']:.1%}")
    print(f"  charInterval accuracy: {metrics['char_interval_valid_rate']:.1%}")

    print(f"\n  Capacity parseable: {metrics['capacity_parseable_rate']:.1%}")
    print(f"  Price parseable: {metrics['price_parseable_rate']:.1%}")


def main() -> None:
    """CLI entrypoint."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <results.jsonl> [results2.jsonl ...]", file=sys.stderr)
        sys.exit(2)

    for path_str in sys.argv[1:]:
        path = Path(path_str)
        if not path.exists():
            print(f"File not found: {path}", file=sys.stderr)
            continue

        results = load_results(path)
        if not results:
            print(f"No results in: {path}", file=sys.stderr)
            continue

        metrics = evaluate_results(results)
        print_report(path.name, metrics)

    # Comparison table if multiple files
    if len(sys.argv) > 2:
        print(f"\n{'=' * 70}")
        print("  Comparison Summary")
        print(f"{'=' * 70}")
        cols = f"{'Extr/Art':>9s} {'Cls':>4s} {'Rel%':>5s} {'CI%':>5s} {'CIacc':>6s}"
        header = f"{'Model':40s} {cols}"
        print(f"  {header}")
        print(f"  {'-' * len(header)}")

        for path_str in sys.argv[1:]:
            path = Path(path_str)
            if not path.exists():
                continue
            results = load_results(path)
            if not results:
                continue
            m = evaluate_results(results)
            print(
                f"  {path.stem:40s} "
                f"{m['avg_extractions_per_article']:9.1f} "
                f"{m['entity_classes_found']:4d} "
                f"{m['relationship_rate']:5.1%} "
                f"{m['char_interval_rate']:5.1%} "
                f"{m['char_interval_valid_rate']:6.1%}"
            )


if __name__ == "__main__":
    main()
