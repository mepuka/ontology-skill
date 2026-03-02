"""Validate RLM-generated extraction examples for effect-langextract.

Checks:
  1. charInterval positions match extractionText exactly
  2. All 13+1 extraction classes covered across examples
  3. No duplicate extractions within an article
  4. Span lengths are reasonable
  5. Structured attributes present where expected

Usage:
    uv run python scripts/extract/validate_examples.py /tmp/extraction-examples.json
"""

from __future__ import annotations

import json
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
ALL_CLASSES = ENTITY_CLASSES | {"Relationship"}

RELATIONSHIP_TYPES = frozenset(
    {
        "operatedBy",
        "locatedIn",
        "hasCapacity",
        "hasStatus",
        "jurisdiction",
        "developedThrough",
        "hasTechnology",
        "mentionsOrganization",
    }
)


def validate_examples(examples: list[dict]) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) from validating extraction examples."""
    errors: list[str] = []
    warnings: list[str] = []
    class_counts: Counter[str] = Counter()
    rel_type_counts: Counter[str] = Counter()
    total_extractions = 0

    if not isinstance(examples, list):
        errors.append(f"Top-level must be a JSON array, got {type(examples).__name__}")
        return errors, warnings

    for i, example in enumerate(examples):
        label = f"Example {i + 1}"

        # Check required fields
        if "text" not in example:
            errors.append(f"{label}: missing 'text' field")
            continue
        if "extractions" not in example:
            errors.append(f"{label}: missing 'extractions' field")
            continue

        text = example["text"]
        extractions = example["extractions"]

        if not isinstance(text, str) or len(text) < 100:
            tlen = len(text) if isinstance(text, str) else 0
            errors.append(f"{label}: text too short ({tlen})")
            continue
        if not isinstance(extractions, list):
            errors.append(f"{label}: extractions must be an array")
            continue

        if len(extractions) < 10:
            warnings.append(f"{label}: only {len(extractions)} extractions (target: 15+)")
        if len(extractions) < 5:
            errors.append(f"{label}: too few extractions ({len(extractions)})")

        seen_spans: set[tuple[str, str]] = set()

        for j, ext in enumerate(extractions):
            ext_label = f"{label}, extraction {j + 1}"
            total_extractions += 1

            # Required fields
            ext_class = ext.get("extractionClass", "")
            ext_text = ext.get("extractionText", "")

            if not ext_class:
                errors.append(f"{ext_label}: missing extractionClass")
                continue
            if not ext_text:
                errors.append(f"{ext_label}: missing extractionText")
                continue

            # Class validation
            if ext_class not in ALL_CLASSES:
                warnings.append(f"{ext_label}: unknown class '{ext_class}'")
            class_counts[ext_class] += 1

            # charInterval validation
            ci = ext.get("charInterval")
            if ci is None:
                warnings.append(f"{ext_label}: missing charInterval for '{ext_text[:40]}'")
            elif isinstance(ci, dict):
                start = ci.get("startPos")
                end = ci.get("endPos")
                if start is not None and end is not None:
                    if not (0 <= start < end <= len(text)):
                        errors.append(
                            f"{ext_label}: charInterval [{start}:{end}] out of bounds "
                            f"(text length: {len(text)})"
                        )
                    else:
                        actual = text[start:end]
                        if actual != ext_text:
                            errors.append(
                                f"{ext_label}: charInterval mismatch\n"
                                f"  expected: {ext_text!r}\n"
                                f"  actual:   {actual!r}\n"
                                f"  at [{start}:{end}]"
                            )
                else:
                    warnings.append(f"{ext_label}: charInterval missing startPos/endPos")

            # Verify extractionText is in the article text
            if ext_text not in text:
                errors.append(f"{ext_label}: extractionText not found in text: {ext_text!r}")

            # Duplicate check
            span_key = (ext_class, ext_text)
            if span_key in seen_spans:
                warnings.append(f"{ext_label}: duplicate extraction ({ext_class}: {ext_text!r})")
            seen_spans.add(span_key)

            # Span length checks
            if len(ext_text) > 200:
                warnings.append(f"{ext_label}: very long span ({len(ext_text)} chars)")
            if len(ext_text) < 2 and ext_class != "Person":
                warnings.append(f"{ext_label}: very short span: {ext_text!r}")

            # Structured attribute checks
            attrs = ext.get("attributes", {})
            if ext_class == "CapacityMeasurement" and not attrs.get("valueInMW"):
                warnings.append(f"{ext_label}: CapacityMeasurement missing valueInMW attribute")
            if ext_class == "PriceDataPoint" and not attrs.get("priceValue"):
                warnings.append(f"{ext_label}: PriceDataPoint missing priceValue attribute")
            if ext_class == "Relationship":
                if not attrs.get("relationshipType"):
                    warnings.append(f"{ext_label}: Relationship missing relationshipType attribute")
                if not attrs.get("subject"):
                    warnings.append(f"{ext_label}: Relationship missing subject attribute")
                if not attrs.get("object"):
                    warnings.append(f"{ext_label}: Relationship missing object attribute")
                rt = attrs.get("relationshipType", "")
                if rt:
                    rel_type_counts[rt] += 1

    # Coverage checks
    missing_classes = ENTITY_CLASSES - set(class_counts.keys())
    if missing_classes:
        warnings.append(f"Missing entity classes: {sorted(missing_classes)}")

    if class_counts.get("Relationship", 0) == 0:
        warnings.append("No Relationship extractions found")

    if len(rel_type_counts) < 3:
        warnings.append(
            f"Only {len(rel_type_counts)} relationship types found "
            f"({sorted(rel_type_counts.keys())}), target: 5+"
        )

    return errors, warnings


def print_summary(examples: list[dict], errors: list[str], warnings: list[str]) -> None:
    """Print validation summary."""
    class_counts: Counter[str] = Counter()
    for ex in examples:
        for ext in ex.get("extractions", []):
            class_counts[ext.get("extractionClass", "unknown")] += 1

    print(f"\n{'=' * 60}")
    print("Extraction Examples Validation Report")
    print(f"{'=' * 60}")
    print(f"Examples: {len(examples)}")
    print(f"Total extractions: {sum(class_counts.values())}")
    print(f"Avg per example: {sum(class_counts.values()) / max(len(examples), 1):.1f}")

    print("\nClass distribution:")
    for cls, count in sorted(class_counts.items(), key=lambda x: -x[1]):
        marker = " *" if cls not in ALL_CLASSES else ""
        print(f"  {cls:30s} {count:4d}{marker}")

    per_example = []
    for i, ex in enumerate(examples):
        n = len(ex.get("extractions", []))
        text_len = len(ex.get("text", ""))
        per_example.append((i + 1, n, text_len))
    print("\nPer-example counts:")
    for idx, n, tlen in per_example:
        status = "OK" if n >= 15 else "LOW" if n >= 10 else "VERY LOW"
        print(f"  Example {idx:2d}: {n:3d} extractions, {tlen:,} chars [{status}]")

    if errors:
        print(f"\n--- ERRORS ({len(errors)}) ---")
        for e in errors:
            print(f"  [ERROR] {e}")
    if warnings:
        print(f"\n--- WARNINGS ({len(warnings)}) ---")
        for w in warnings:
            print(f"  [WARN]  {w}")

    if not errors:
        print("\n  PASS — no errors found")
    else:
        print(f"\n  FAIL — {len(errors)} error(s) found")


def main() -> None:
    """CLI entrypoint."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <examples.json>", file=sys.stderr)
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(2)

    with path.open() as f:
        examples = json.load(f)

    errors, warnings = validate_examples(examples)
    print_summary(examples, errors, warnings)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
