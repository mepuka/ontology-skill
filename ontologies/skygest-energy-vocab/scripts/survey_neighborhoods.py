"""Survey the graph neighborhoods of linked entities in OEO and Wikidata.

For each confirmed mapping, traverse related entities and harvest all
labels that could serve as surface forms for chart text matching.

Usage:
    uv run python scripts/survey_neighborhoods.py
"""

from __future__ import annotations

import json
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

VOCAB_DIR = Path(__file__).parent.parent
DATA_DIR = VOCAB_DIR / "data"
CONFIRMED_FILE = DATA_DIR / "wikidata-confirmed.json"
SURVEY_FILE = DATA_DIR / "neighborhood-survey.json"

ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "SkygestEnergyVocab/0.1 (ontology-skill; contact@skygest.dev)"


def sparql_query(query: str) -> list[dict]:
    """Execute a SPARQL query against Wikidata."""
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    req = urllib.request.Request(
        f"{ENDPOINT}?{params}",
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data.get("results", {}).get("bindings", [])


def survey_wikidata_neighborhood(qid: str, concept_id: str) -> list[dict]:
    """Survey the Wikidata neighborhood of a QID.

    Pulls labels from:
    - The entity itself (labels + aliases)
    - Subclasses (P279←) — "types of this thing"
    - Parent classes (P279→) — "this is a type of"
    - Has-part / part-of (P527, P361)
    - "Use" relations (P366)
    - "Facet of" (P1269)
    """
    results: list[dict] = []

    query = f"""
    SELECT DISTINCT ?relation ?related ?relatedLabel ?relatedAltLabel ?relatedDescription WHERE {{
      VALUES ?seed {{ wd:{qid} }}

      # Self labels + aliases
      {{
        BIND("self" AS ?relation)
        BIND(?seed AS ?related)
        ?seed rdfs:label ?relatedLabel .
        FILTER(LANG(?relatedLabel) = "en")
        OPTIONAL {{
          ?seed skos:altLabel ?relatedAltLabel .
          FILTER(LANG(?relatedAltLabel) = "en")
        }}
      }}
      UNION
      # Subclasses — "types of this"
      {{
        BIND("subclass" AS ?relation)
        ?related wdt:P279 ?seed .
        ?related rdfs:label ?relatedLabel .
        FILTER(LANG(?relatedLabel) = "en")
        OPTIONAL {{
          ?related skos:altLabel ?relatedAltLabel .
          FILTER(LANG(?relatedAltLabel) = "en")
        }}
      }}
      UNION
      # Parent classes — "this is a type of"
      {{
        BIND("superclass" AS ?relation)
        ?seed wdt:P279 ?related .
        ?related rdfs:label ?relatedLabel .
        FILTER(LANG(?relatedLabel) = "en")
        OPTIONAL {{
          ?related skos:altLabel ?relatedAltLabel .
          FILTER(LANG(?relatedAltLabel) = "en")
        }}
      }}
      UNION
      # Has-part
      {{
        BIND("has_part" AS ?relation)
        ?seed wdt:P527 ?related .
        ?related rdfs:label ?relatedLabel .
        FILTER(LANG(?relatedLabel) = "en")
        OPTIONAL {{
          ?related skos:altLabel ?relatedAltLabel .
          FILTER(LANG(?relatedAltLabel) = "en")
        }}
      }}
      UNION
      # Part-of
      {{
        BIND("part_of" AS ?relation)
        ?seed wdt:P361 ?related .
        ?related rdfs:label ?relatedLabel .
        FILTER(LANG(?relatedLabel) = "en")
        OPTIONAL {{
          ?related skos:altLabel ?relatedAltLabel .
          FILTER(LANG(?relatedAltLabel) = "en")
        }}
      }}
      OPTIONAL {{
        ?related schema:description ?relatedDescription .
        FILTER(LANG(?relatedDescription) = "en")
      }}
    }}
    """

    try:
        bindings = sparql_query(query)
        for b in bindings:
            related_qid = b["related"]["value"].split("/")[-1]
            label = b.get("relatedLabel", {}).get("value", "")
            alt = b.get("relatedAltLabel", {}).get("value", "")
            desc = b.get("relatedDescription", {}).get("value", "")
            relation = b.get("relation", {}).get("value", "")

            if label:
                results.append(
                    {
                        "concept_id": concept_id,
                        "source": f"wikidata:{related_qid}",
                        "relation": relation,
                        "surface_form": label,
                        "description": desc,
                        "type": "rdfs:label",
                    }
                )
            if alt:
                results.append(
                    {
                        "concept_id": concept_id,
                        "source": f"wikidata:{related_qid}",
                        "relation": relation,
                        "surface_form": alt,
                        "description": desc,
                        "type": "skos:altLabel",
                    }
                )
    except Exception as e:
        print(f"  ERROR surveying wd:{qid}: {e}")

    return results


def survey_oeo_full(oeo_curie: str, concept_id: str) -> list[dict]:
    """Deep survey of OEO neighborhood via oaklib.

    Gets descendants (2 levels), siblings, and labels for all.
    """
    results: list[dict] = []

    # Descendants (already have from harvest, but let's be thorough)
    try:
        proc = subprocess.run(
            [
                "uv",
                "run",
                "runoak",
                "-i",
                "sqlite:obo:oeo",
                "descendants",
                oeo_curie,
                "--predicates",
                "rdfs:subClassOf",
            ],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        if proc.returncode == 0:
            for line in proc.stdout.strip().split("\n"):
                if "\t" in line:
                    curie, label = line.split("\t", 1)
                    results.append(
                        {
                            "concept_id": concept_id,
                            "source": curie.strip(),
                            "relation": "descendant",
                            "surface_form": label.strip(),
                            "type": "rdfs:label",
                        }
                    )
                elif " ! " in line:
                    curie, label = line.split(" ! ", 1)
                    results.append(
                        {
                            "concept_id": concept_id,
                            "source": curie.strip(),
                            "relation": "descendant",
                            "surface_form": label.strip(),
                            "type": "rdfs:label",
                        }
                    )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Siblings (same parent)
    try:
        # Get parent first
        proc = subprocess.run(
            [
                "uv",
                "run",
                "runoak",
                "-i",
                "sqlite:obo:oeo",
                "ancestors",
                oeo_curie,
                "--predicates",
                "rdfs:subClassOf",
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if proc.returncode == 0:
            lines = proc.stdout.strip().split("\n")
            # Find the immediate parent (second line after header, sorted by depth)
            for line in lines:
                if "\t" in line:
                    parent_curie = line.split("\t")[0].strip()
                elif " ! " in line:
                    parent_curie = line.split(" ! ")[0].strip()
                else:
                    continue

                if parent_curie == oeo_curie:
                    continue
                if parent_curie.startswith("BFO:"):
                    continue

                # Get children of this parent (siblings)
                sib_proc = subprocess.run(
                    [
                        "uv",
                        "run",
                        "runoak",
                        "-i",
                        "sqlite:obo:oeo",
                        "descendants",
                        parent_curie,
                        "--predicates",
                        "rdfs:subClassOf",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    check=False,
                )
                if sib_proc.returncode == 0:
                    for sib_line in sib_proc.stdout.strip().split("\n"):
                        if " ! " in sib_line:
                            sib_curie, sib_label = sib_line.split(" ! ", 1)
                            sib_curie = sib_curie.strip()
                            if sib_curie != oeo_curie:
                                results.append(
                                    {
                                        "concept_id": concept_id,
                                        "source": sib_curie,
                                        "relation": f"sibling (via {parent_curie})",
                                        "surface_form": sib_label.strip(),
                                        "type": "rdfs:label",
                                    }
                                )
                break  # Only check first non-BFO parent
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return results


def main() -> None:
    """Run the full neighborhood survey."""
    confirmed = json.loads(CONFIRMED_FILE.read_text())
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # OEO mapping from reuse report
    oeo_map = {
        "sevocab:SolarPv": "OEO:00000034",
        "sevocab:Wind": "OEO:00000043",
        "sevocab:Battery": "OEO:00000068",
        "sevocab:Renewable": "OEO:00030004",
        "sevocab:Nuclear": "OEO:00010415",
        "sevocab:Coal": "OEO:00000088",
        "sevocab:BrownCoal": "OEO:00000251",
        "sevocab:HeatPump": "OEO:00000212",
        "sevocab:Hydrogen": "OEO:00000220",
        "sevocab:NaturalGas": "OEO:00000292",
        "sevocab:GasCcgt": "OEO:00000185",
    }

    all_results: dict[str, list[dict]] = {}

    # Survey Wikidata neighborhoods
    print("=" * 60)
    print("WIKIDATA NEIGHBORHOOD SURVEY")
    print("=" * 60)
    for concept_id, qid in confirmed.items():
        print(f"\n--- {concept_id} (wd:{qid}) ---")
        wd_results = survey_wikidata_neighborhood(qid, concept_id)
        all_results.setdefault(concept_id, []).extend(wd_results)

        # Summary
        by_relation: dict[str, int] = {}
        for r in wd_results:
            by_relation[r["relation"]] = by_relation.get(r["relation"], 0) + 1
        for rel, count in sorted(by_relation.items()):
            print(f"  {rel}: {count} labels")

        time.sleep(1.5)

    # Survey OEO neighborhoods
    print("\n" + "=" * 60)
    print("OEO NEIGHBORHOOD SURVEY")
    print("=" * 60)
    for concept_id, oeo_curie in oeo_map.items():
        print(f"\n--- {concept_id} ({oeo_curie}) ---")
        oeo_results = survey_oeo_full(oeo_curie, concept_id)
        all_results.setdefault(concept_id, []).extend(oeo_results)

        by_relation: dict[str, int] = {}
        for r in oeo_results:
            by_relation[r["relation"]] = by_relation.get(r["relation"], 0) + 1
        for rel, count in sorted(by_relation.items()):
            print(f"  {rel}: {count} labels")

    # Deduplicate and summarize
    print("\n" + "=" * 60)
    print("SURVEY SUMMARY")
    print("=" * 60)

    total = 0
    for concept_id, labels in sorted(all_results.items()):
        # Deduplicate by surface_form (case-insensitive)
        seen: set[str] = set()
        unique: list[dict] = []
        for lbl in labels:
            key = lbl["surface_form"].lower().strip()
            if key not in seen and len(key) > 1:
                seen.add(key)
                unique.append(lbl)
        all_results[concept_id] = unique
        total += len(unique)
        print(f"  {concept_id}: {len(unique)} unique surface forms")

    print(f"\n  TOTAL: {total} unique surface forms across all concepts")

    SURVEY_FILE.write_text(json.dumps(all_results, indent=2))
    print(f"\n  Wrote survey to {SURVEY_FILE}")


if __name__ == "__main__":
    main()
