"""Programmatic Wikidata linker via SPARQL.

Searches Wikidata by concept label, filters to energy-domain entities,
and returns candidate QIDs with descriptions for review. Then harvests
English labels and aliases from confirmed matches.

Usage:
    uv run python scripts/wikidata_linker.py discover   # Find QID candidates
    uv run python scripts/wikidata_linker.py harvest     # Harvest labels from confirmed QIDs
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

VOCAB_DIR = Path(__file__).parent.parent
DATA_DIR = VOCAB_DIR / "data"
CANDIDATES_FILE = DATA_DIR / "wikidata-candidates.json"
CONFIRMED_FILE = DATA_DIR / "wikidata-confirmed.json"
HARVEST_FILE = DATA_DIR / "wikidata-harvested-labels.json"

ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "SkygestEnergyVocab/0.1 (ontology-skill; contact@skygest.dev)"

# Our concepts and their search terms for Wikidata discovery
CONCEPTS = {
    "sevocab:SolarPv": {
        "search_terms": ["solar photovoltaic", "photovoltaic energy"],
        "expected_domain": "energy technology",
    },
    "sevocab:Wind": {
        "search_terms": ["wind energy", "wind power"],
        "expected_domain": "energy",
    },
    "sevocab:OnshoreWind": {
        "search_terms": ["onshore wind power"],
        "expected_domain": "energy technology",
    },
    "sevocab:OffshoreWind": {
        "search_terms": ["offshore wind power"],
        "expected_domain": "energy technology",
    },
    "sevocab:Battery": {
        "search_terms": ["battery storage", "battery energy storage"],
        "expected_domain": "energy storage",
    },
    "sevocab:Renewable": {
        "search_terms": ["renewable energy"],
        "expected_domain": "energy",
    },
    "sevocab:Nuclear": {
        "search_terms": ["nuclear power", "nuclear energy"],
        "expected_domain": "energy",
    },
    "sevocab:Coal": {
        "search_terms": ["coal", "coal energy"],
        "expected_domain": "energy/fuel",
    },
    "sevocab:BrownCoal": {
        "search_terms": ["lignite", "brown coal"],
        "expected_domain": "fuel",
    },
    "sevocab:HeatPump": {
        "search_terms": ["heat pump"],
        "expected_domain": "energy technology",
    },
    "sevocab:Hydrogen": {
        "search_terms": ["hydrogen energy", "hydrogen fuel"],
        "expected_domain": "energy/fuel",
    },
    "sevocab:NaturalGas": {
        "search_terms": ["natural gas"],
        "expected_domain": "fuel",
    },
    "sevocab:GasCcgt": {
        "search_terms": ["combined cycle gas turbine", "combined cycle power plant"],
        "expected_domain": "power plant type",
    },
}


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


def discover_candidates() -> dict[str, list[dict]]:
    """Search Wikidata for candidate QIDs for each concept."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    all_candidates: dict[str, list[dict]] = {}

    for concept_id, config in CONCEPTS.items():
        print(f"\n--- {concept_id} ---")
        candidates: list[dict] = []

        for term in config["search_terms"]:
            # Use Wikidata's label service + text search
            query = f"""
            SELECT DISTINCT ?item ?itemLabel ?itemDescription ?instanceOfLabel WHERE {{
              SERVICE wikibase:mwapi {{
                bd:serviceParam wikibase:endpoint "www.wikidata.org" ;
                                wikibase:api "EntitySearch" ;
                                mwapi:search "{term}" ;
                                mwapi:language "en" .
                ?item wikibase:apiOutputItem mwapi:item .
              }}
              OPTIONAL {{
                ?item wdt:P31 ?instanceOf .
                ?instanceOf rdfs:label ?instanceOfLabel .
                FILTER(LANG(?instanceOfLabel) = "en")
              }}
              SERVICE wikibase:label {{
                bd:serviceParam wikibase:language "en" .
              }}
            }}
            LIMIT 8
            """
            try:
                results = sparql_query(query)
                for r in results:
                    qid = r["item"]["value"].split("/")[-1]
                    label = r.get("itemLabel", {}).get("value", "")
                    desc = r.get("itemDescription", {}).get("value", "")
                    instance_of = r.get("instanceOfLabel", {}).get("value", "")

                    # Skip if it's clearly wrong domain
                    if any(
                        skip in desc.lower()
                        for skip in [
                            "album",
                            "film",
                            "song",
                            "band",
                            "person",
                            "village",
                            "municipality",
                            "district",
                            "ship",
                            "video game",
                            "novel",
                            "tv series",
                        ]
                    ):
                        continue

                    candidates.append(
                        {
                            "qid": qid,
                            "label": label,
                            "description": desc,
                            "instance_of": instance_of,
                            "search_term": term,
                        }
                    )
                    print(f"  {qid}: {label} — {desc} [{instance_of}]")

            except Exception as e:
                print(f"  ERROR querying '{term}': {e}")

            time.sleep(1.5)  # Be polite to the endpoint

        # Deduplicate by QID
        seen_qids: set[str] = set()
        unique: list[dict] = []
        for c in candidates:
            if c["qid"] not in seen_qids:
                seen_qids.add(c["qid"])
                unique.append(c)
        all_candidates[concept_id] = unique

    CANDIDATES_FILE.write_text(json.dumps(all_candidates, indent=2))
    print(f"\nWrote candidates to {CANDIDATES_FILE}")
    return all_candidates


def harvest_from_confirmed() -> list[dict]:
    """Harvest English labels and aliases from confirmed QIDs."""
    if not CONFIRMED_FILE.exists():
        print(f"No confirmed file at {CONFIRMED_FILE}")
        print("Run 'discover' first, review candidates, then create confirmed file.")
        return []

    confirmed = json.loads(CONFIRMED_FILE.read_text())

    # Build VALUES clause
    qid_map: dict[str, str] = {qid: cid for cid, qid in confirmed.items()}

    if not qid_map:
        print("No confirmed QIDs to harvest.")
        return []

    values = " ".join(f"wd:{qid}" for qid in qid_map)

    query = f"""
    SELECT ?item ?label ?altLabel WHERE {{
      VALUES ?item {{ {values} }}
      {{
        ?item rdfs:label ?label .
        FILTER(LANG(?label) = "en")
      }}
      UNION
      {{
        ?item skos:altLabel ?altLabel .
        FILTER(LANG(?altLabel) = "en")
      }}
    }}
    """

    print("Querying Wikidata for labels...")
    results = sparql_query(query)

    harvested: list[dict] = []
    for r in results:
        qid = r["item"]["value"].split("/")[-1]
        concept_id = qid_map.get(qid, "unknown")

        label = r.get("label", {}).get("value")
        alt_label = r.get("altLabel", {}).get("value")

        surface_form = label or alt_label
        relation = "rdfs:label" if label else "skos:altLabel"

        if surface_form:
            harvested.append(
                {
                    "concept_id": concept_id,
                    "qid": qid,
                    "surface_form": surface_form,
                    "language": "en",
                    "provenance": "wikidata-derived",
                    "relation": relation,
                }
            )

    # Deduplicate
    seen: set[tuple[str, str]] = set()
    deduped: list[dict] = []
    for h in harvested:
        key = (h["concept_id"], h["surface_form"].lower())
        if key not in seen:
            seen.add(key)
            deduped.append(h)

    # Group and display
    by_concept: dict[str, list[dict]] = {}
    for h in deduped:
        by_concept.setdefault(h["concept_id"], []).append(h)

    for concept_id, labels in sorted(by_concept.items()):
        print(f"\n{concept_id}:")
        for lbl in labels:
            print(f'  [{lbl["relation"]}] "{lbl["surface_form"]}"  ← wd:{lbl["qid"]}')

    HARVEST_FILE.write_text(json.dumps(deduped, indent=2))
    print(f"\nWrote {len(deduped)} labels to {HARVEST_FILE}")
    return deduped


def main() -> None:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/wikidata_linker.py [discover|harvest]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "discover":
        discover_candidates()
    elif command == "harvest":
        harvest_from_confirmed()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
