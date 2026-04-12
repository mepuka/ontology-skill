"""Harvest labels from linked ontologies (OEO, Wikidata) via SSSOM mappings.

This script reads the SSSOM mapping files, queries the linked ontologies
for labels and synonyms, and proposes new altLabels for the vocabulary.

Usage:
    uv run python scripts/harvest_labels.py
"""

from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

VOCAB_DIR = Path(__file__).parent.parent
MAPPINGS_DIR = VOCAB_DIR / "mappings"
OUTPUT_FILE = VOCAB_DIR / "data" / "harvested-labels.json"


@dataclass
class HarvestedLabel:
    """A label harvested from an external ontology."""

    concept_id: str
    concept_label: str
    surface_form: str
    language: str
    provenance: str
    source_id: str
    source_label: str
    relation: str


def parse_sssom(filepath: Path) -> list[dict[str, str]]:
    """Parse an SSSOM TSV file, skipping comment header lines."""
    with filepath.open() as f:
        lines = [line for line in f if not line.startswith("#")]
    reader = csv.DictReader(lines, delimiter="\t")
    return list(reader)


def harvest_oeo_labels() -> list[HarvestedLabel]:
    """Harvest labels from OEO via oaklib for mapped concepts."""
    sssom_file = MAPPINGS_DIR / "sevocab-to-oeo.sssom.tsv"
    if not sssom_file.exists():
        print("  SKIP: sevocab-to-oeo.sssom.tsv not found")
        return []

    mappings = parse_sssom(sssom_file)
    harvested: list[HarvestedLabel] = []

    for mapping in mappings:
        subject_id = mapping["subject_id"]
        subject_label = mapping["subject_label"]
        object_id = mapping["object_id"]
        object_label = mapping["object_label"]
        predicate = mapping["predicate_id"]

        # The OEO label itself is a surface form
        harvested.append(
            HarvestedLabel(
                concept_id=subject_id,
                concept_label=subject_label,
                surface_form=object_label,
                language="en",
                provenance="oeo-derived",
                source_id=object_id,
                source_label=object_label,
                relation=predicate,
            )
        )

        # Get descendants of the OEO term to harvest more labels
        oeo_curie = object_id.replace("OEO:", "OEO:")
        try:
            result = subprocess.run(
                ["uv", "run", "runoak", "-i", "sqlite:obo:oeo", "descendants", oeo_curie],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if " ! " in line:
                        _curie, label = line.split(" ! ", 1)
                        label = label.strip()
                        if label != object_label and len(label) > 1:
                            harvested.append(
                                HarvestedLabel(
                                    concept_id=subject_id,
                                    concept_label=subject_label,
                                    surface_form=label,
                                    language="en",
                                    provenance="oeo-derived",
                                    source_id=_curie.strip(),
                                    source_label=label,
                                    relation=f"descendant of {object_id}",
                                )
                            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return harvested


def harvest_wikidata_labels() -> list[HarvestedLabel]:
    """Harvest English labels and aliases from Wikidata via SPARQL."""
    sssom_file = MAPPINGS_DIR / "sevocab-to-wikidata.sssom.tsv"
    if not sssom_file.exists():
        print("  SKIP: sevocab-to-wikidata.sssom.tsv not found")
        return []

    mappings = parse_sssom(sssom_file)
    harvested: list[HarvestedLabel] = []

    # Build SPARQL VALUES clause from QIDs
    qid_to_concept: dict[str, tuple[str, str]] = {}
    for mapping in mappings:
        qid = mapping["object_id"].replace("wikidata:", "")
        qid_to_concept[qid] = (mapping["subject_id"], mapping["subject_label"])

    if not qid_to_concept:
        return []

    values = " ".join(f"wd:{qid}" for qid in qid_to_concept)

    # Query for English labels AND aliases (altLabels)
    sparql = f"""
    SELECT ?item ?itemLabel ?altLabel WHERE {{
      VALUES ?item {{ {values} }}
      ?item rdfs:label ?itemLabel .
      FILTER(LANG(?itemLabel) = "en")
      OPTIONAL {{
        ?item skos:altLabel ?altLabel .
        FILTER(LANG(?altLabel) = "en")
      }}
    }}
    """

    try:
        import urllib.parse
        import urllib.request

        endpoint = "https://query.wikidata.org/sparql"
        params = urllib.parse.urlencode(
            {
                "query": sparql,
                "format": "json",
            }
        )
        req = urllib.request.Request(
            f"{endpoint}?{params}",
            headers={"User-Agent": "SkygestEnergyVocab/0.1 (ontology harvest)"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())

        for binding in data.get("results", {}).get("bindings", []):
            item_uri = binding["item"]["value"]
            qid = item_uri.split("/")[-1]
            if qid not in qid_to_concept:
                continue

            concept_id, concept_label = qid_to_concept[qid]

            # Main label
            item_label = binding.get("itemLabel", {}).get("value", "")
            if item_label:
                harvested.append(
                    HarvestedLabel(
                        concept_id=concept_id,
                        concept_label=concept_label,
                        surface_form=item_label,
                        language="en",
                        provenance="wikidata-derived",
                        source_id=f"wikidata:{qid}",
                        source_label=item_label,
                        relation="rdfs:label",
                    )
                )

            # Alt labels
            alt_label = binding.get("altLabel", {}).get("value", "")
            if alt_label:
                harvested.append(
                    HarvestedLabel(
                        concept_id=concept_id,
                        concept_label=concept_label,
                        surface_form=alt_label,
                        language="en",
                        provenance="wikidata-derived",
                        source_id=f"wikidata:{qid}",
                        source_label=alt_label,
                        relation="skos:altLabel",
                    )
                )

    except Exception as e:
        print(f"  WARNING: Wikidata SPARQL failed: {e}")

    return harvested


def deduplicate(labels: list[HarvestedLabel]) -> list[HarvestedLabel]:
    """Remove duplicates by (concept_id, normalized surface_form)."""
    seen: set[tuple[str, str]] = set()
    deduped: list[HarvestedLabel] = []
    for label in labels:
        key = (label.concept_id, label.surface_form.lower().strip())
        if key not in seen:
            seen.add(key)
            deduped.append(label)
    return deduped


def main() -> None:
    """Run the harvest pipeline."""
    print("Harvesting labels from linked ontologies...\n")

    print("1. OEO (via oaklib sqlite cache)...")
    oeo_labels = harvest_oeo_labels()
    print(f"   Harvested {len(oeo_labels)} labels from OEO\n")

    print("2. Wikidata (via SPARQL endpoint)...")
    wikidata_labels = harvest_wikidata_labels()
    print(f"   Harvested {len(wikidata_labels)} labels from Wikidata\n")

    all_labels = oeo_labels + wikidata_labels
    deduped = deduplicate(all_labels)
    print(f"Total: {len(all_labels)} raw, {len(deduped)} after dedup\n")

    # Group by concept for review
    by_concept: dict[str, list[HarvestedLabel]] = {}
    for label in deduped:
        by_concept.setdefault(label.concept_id, []).append(label)

    print("=== Harvested labels by concept ===\n")
    for concept_id, labels in sorted(by_concept.items()):
        concept_label = labels[0].concept_label
        print(f"{concept_id} ({concept_label}):")
        for lbl in labels:
            print(f'  [{lbl.provenance}] "{lbl.surface_form}"@{lbl.language}  ← {lbl.source_id}')
        print()

    # Write output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output_data = [
        {
            "concept_id": entry.concept_id,
            "concept_label": entry.concept_label,
            "surface_form": entry.surface_form,
            "language": entry.language,
            "provenance": entry.provenance,
            "source_id": entry.source_id,
            "source_label": entry.source_label,
            "relation": entry.relation,
        }
        for entry in deduped
    ]
    OUTPUT_FILE.write_text(json.dumps(output_data, indent=2))
    print(f"Wrote {len(deduped)} harvested labels to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
