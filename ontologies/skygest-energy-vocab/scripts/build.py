"""Build JSON vocabulary files from the Turtle ontology.

Reads the SKOS vocabulary, extracts all concepts and altLabels per scheme,
computes normalizedSurfaceForm (matching normalizeLookupText() from
skygest-cloudflare/src/resolution/normalize.ts), checks for collisions,
and emits JSON files matching the SurfaceFormEntry<Canonical> schema.

Usage:
    uv run python scripts/build.py

Output:
    data/vocabulary/statistic-type.json
    data/vocabulary/aggregation.json
    data/vocabulary/unit-family.json
    data/vocabulary/technology-or-fuel.json
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from datetime import UTC, datetime
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import SKOS

VOCAB_DIR = Path(__file__).parent.parent
VOCAB_FILE = VOCAB_DIR / "skygest-energy-vocab.ttl"
OUTPUT_DIR = VOCAB_DIR / "data" / "vocabulary"

SEVOCAB = Namespace("https://skygest.dev/vocab/energy/")

# Map scheme IRIs to output filenames and TypeScript canonical types
SCHEME_CONFIG = {
    str(SEVOCAB.StatisticTypeScheme): {
        "filename": "statistic-type.json",
        "name": "StatisticType",
    },
    str(SEVOCAB.AggregationScheme): {
        "filename": "aggregation.json",
        "name": "Aggregation",
    },
    str(SEVOCAB.UnitFamilyScheme): {
        "filename": "unit-family.json",
        "name": "UnitFamily",
    },
    str(SEVOCAB.TechnologyOrFuelScheme): {
        "filename": "technology-or-fuel.json",
        "name": "TechnologyOrFuel",
    },
    str(SEVOCAB.MeasuredPropertyScheme): {
        "filename": "measured-property.json",
        "name": "MeasuredProperty",
    },
    str(SEVOCAB.DomainObjectScheme): {
        "filename": "domain-object.json",
        "name": "DomainObject",
    },
    str(SEVOCAB.PolicyInstrumentScheme): {
        "filename": "policy-instrument.json",
        "name": "PolicyInstrument",
    },
}

# Default timestamp for bootstrap entries
BOOTSTRAP_TIMESTAMP = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def normalize_lookup_text(value: str) -> str:
    """Match normalizeLookupText() from skygest-cloudflare.

    Applies: Unicode NFKC normalization -> collapse whitespace -> lowercase.
    """
    # NFKC normalization (compatibility decomposition + canonical composition)
    nfkc = unicodedata.normalize("NFKC", value)
    # Collapse whitespace
    collapsed = re.sub(r"\s+", " ", nfkc).strip()
    # Lowercase
    return collapsed.lower()


def build_vocabulary() -> None:
    """Build JSON vocabulary files from Turtle."""
    g = Graph()
    g.parse(VOCAB_FILE, format="turtle")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_entries = 0
    total_collisions = 0

    for scheme_iri, config in SCHEME_CONFIG.items():
        scheme_ref = URIRef(scheme_iri)
        entries: list[dict[str, str]] = []
        collision_index: dict[str, str] = {}  # normalized -> canonical
        collisions: list[dict[str, str]] = []

        # Find all concepts in this scheme
        for concept in g.subjects(SKOS.inScheme, scheme_ref):
            # Get canonical value (prefLabel)
            pref_labels = list(g.objects(concept, SKOS.prefLabel))
            if not pref_labels:
                print(f"  WARNING: {concept} has no prefLabel, skipping")
                continue
            canonical = str(pref_labels[0])

            # Get all altLabels
            for alt_label in g.objects(concept, SKOS.altLabel):
                surface_form = str(alt_label)
                lang = alt_label.language if isinstance(alt_label, Literal) else None

                # Only process English labels for now
                if lang and lang != "en":
                    continue

                normalized = normalize_lookup_text(surface_form)

                # Check for collisions
                if normalized in collision_index:
                    existing_canonical = collision_index[normalized]
                    if existing_canonical != canonical:
                        collisions.append(
                            {
                                "normalizedSurfaceForm": normalized,
                                "surfaceForm": surface_form,
                                "canonicalA": existing_canonical,
                                "canonicalB": canonical,
                            }
                        )
                        continue  # Skip the collision — keep first
                else:
                    collision_index[normalized] = canonical

                entry = {
                    "surfaceForm": surface_form,
                    "normalizedSurfaceForm": normalized,
                    "canonical": canonical,
                    "provenance": "cold-start-corpus",
                    "addedAt": BOOTSTRAP_TIMESTAMP,
                }
                entries.append(entry)

        # Sort by canonical then surfaceForm for stable output
        entries.sort(key=lambda e: (e["canonical"], e["surfaceForm"].lower()))

        # Write JSON
        output_file = OUTPUT_DIR / config["filename"]
        output_file.write_text(json.dumps(entries, indent=2, ensure_ascii=False))

        total_entries += len(entries)
        total_collisions += len(collisions)

        print(f"{config['name']}:")
        print(f"  Concepts: {len({e['canonical'] for e in entries})}")
        print(f"  Entries: {len(entries)}")
        if collisions:
            print(f"  COLLISIONS: {len(collisions)}")
            for c in collisions:
                print(f"    '{c['normalizedSurfaceForm']}': {c['canonicalA']} vs {c['canonicalB']}")
        print(f"  -> {output_file}")
        print()

    print(f"{'=' * 60}")
    print(f"Total entries: {total_entries}")
    print(f"Total collisions: {total_collisions}")
    if total_collisions > 0:
        print(
            "WARNING: Collisions detected! These would cause "
            "VocabularyCollisionError in buildVocabularyIndex()."
        )
        sys.exit(1)
    else:
        print("No collisions — safe to deploy.")


if __name__ == "__main__":
    build_vocabulary()
