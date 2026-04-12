"""Expand TechnologyOrFuelScheme with missing OEO power plant types.

Adds new SKOS concepts for technology/fuel types found in OEO but not
yet in our vocabulary, then harvests labels from OEO and Wikidata.

Usage:
    uv run python scripts/expand_technology_scheme.py
"""

from __future__ import annotations

import json
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, RDFS, SKOS

VOCAB_DIR = Path(__file__).parent.parent
VOCAB_FILE = VOCAB_DIR / "skygest-energy-vocab.ttl"
DATA_DIR = VOCAB_DIR / "data"

SEVOCAB = Namespace("https://skygest.dev/vocab/energy/")
ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "SkygestEnergyVocab/0.1 (ontology-skill; contact@skygest.dev)"

# New concepts to add — mapped to OEO IRIs and Wikidata search terms
NEW_CONCEPTS = [
    {
        "iri": "Geothermal",
        "prefLabel": "geothermal",
        "definition": (
            "A technologyOrFuel concept representing geothermal power generation technology"
        ),
        "parent": None,  # top-level
        "oeo": "OEO:00000192",
        "oeo_label": "geothermal power plant",
        "wd_search": "geothermal energy",
        "seed_altLabels": ["geothermal", "geothermal energy", "geothermal power"],
    },
    {
        "iri": "Hydro",
        "prefLabel": "hydro",
        "definition": (
            "A technologyOrFuel concept representing hydroelectric power generation technology"
        ),
        "parent": None,
        "oeo": "OEO:00010086",
        "oeo_label": "hydro power plant",
        "wd_search": "hydroelectric power",
        "seed_altLabels": ["hydro", "hydroelectric", "hydropower", "hydro power"],
    },
    {
        "iri": "PumpedHydro",
        "prefLabel": "pumped hydro",
        "definition": (
            "A technologyOrFuel concept representing pumped-storage hydroelectric technology"
        ),
        "parent": "Hydro",
        "oeo": "OEO:00010089",
        "oeo_label": "pumped hydro storage power plant",
        "wd_search": "pumped-storage hydroelectricity",
        "seed_altLabels": ["pumped hydro", "pumped storage", "pumped hydro storage", "PHES"],
    },
    {
        "iri": "Oil",
        "prefLabel": "oil",
        "definition": (
            "A technologyOrFuel concept representing oil-fired power generation technology"
        ),
        "parent": None,
        "oeo": "OEO:00000310",
        "oeo_label": "oil power plant",
        "wd_search": "oil-fired power station",
        "seed_altLabels": ["oil", "petroleum", "oil-fired", "fuel oil", "crude oil"],
    },
    {
        "iri": "Biomass",
        "prefLabel": "biomass",
        "definition": (
            "A technologyOrFuel concept representing"
            " biomass and bioenergy power generation technology"
        ),
        "parent": None,
        "oeo": "OEO:00000073",
        "oeo_label": "biofuel power plant",
        "wd_search": "biomass energy",
        "seed_altLabels": [
            "biomass",
            "bioenergy",
            "biogas",
            "biofuel",
            "solid biomass",
            "biopower",
            "waste-to-energy",
        ],
    },
    {
        "iri": "SolarThermal",
        "prefLabel": "solar thermal",
        "definition": (
            "A technologyOrFuel concept representing"
            " concentrated solar thermal power generation technology"
        ),
        "parent": None,
        "oeo": "OEO:00000389",
        "oeo_label": "solar thermal power plant",
        "wd_search": "concentrated solar power",
        "seed_altLabels": [
            "solar thermal",
            "CSP",
            "concentrated solar",
            "concentrated solar power",
            "solar thermal power",
            "parabolic trough",
            "solar tower",
        ],
    },
    {
        "iri": "Marine",
        "prefLabel": "marine",
        "definition": (
            "A technologyOrFuel concept representing marine energy"
            " technologies including wave, tidal, and current"
        ),
        "parent": None,
        "oeo": "OEO:00010113",
        "oeo_label": "marine wave energy power plant",
        "wd_search": "marine energy",
        "seed_altLabels": [
            "marine",
            "tidal",
            "wave energy",
            "tidal energy",
            "ocean energy",
            "marine energy",
            "tidal power",
        ],
    },
    {
        "iri": "Waste",
        "prefLabel": "waste",
        "definition": (
            "A technologyOrFuel concept representing waste-to-energy power generation technology"
        ),
        "parent": None,
        "oeo": "OEO:00000440",
        "oeo_label": "waste power plant",
        "wd_search": "waste-to-energy",
        "seed_altLabels": [
            "waste",
            "waste-to-energy",
            "WtE",
            "incineration",
            "energy from waste",
            "EfW",
            "municipal solid waste",
        ],
    },
]


def sparql_query(query: str) -> list[dict]:
    """Execute SPARQL against Wikidata."""
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    req = urllib.request.Request(
        f"{ENDPOINT}?{params}",
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data.get("results", {}).get("bindings", [])


def harvest_oeo_descendants(oeo_curie: str) -> list[str]:
    """Get labels from OEO descendants."""
    labels = []
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
                    _, label = line.split(" ! ", 1)
                    label = label.strip()
                    if label and label != "None":
                        labels.append(label)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return labels


def harvest_wikidata(search_term: str) -> list[str]:
    """Search Wikidata and get labels + aliases for top energy-domain result."""
    query = f"""
    SELECT DISTINCT ?item ?label ?altLabel WHERE {{
      SERVICE wikibase:mwapi {{
        bd:serviceParam wikibase:endpoint "www.wikidata.org" ;
                        wikibase:api "EntitySearch" ;
                        mwapi:search "{search_term}" ;
                        mwapi:language "en" .
        ?item wikibase:apiOutputItem mwapi:item .
      }}
      ?item rdfs:label ?label .
      FILTER(LANG(?label) = "en")
      OPTIONAL {{
        ?item skos:altLabel ?altLabel .
        FILTER(LANG(?altLabel) = "en")
      }}
    }}
    LIMIT 15
    """
    labels = []
    try:
        results = sparql_query(query)
        for r in results:
            label = r.get("label", {}).get("value", "")
            alt = r.get("altLabel", {}).get("value", "")
            if label:
                labels.append(label)
            if alt:
                labels.append(alt)
    except Exception as e:
        print(f"  Wikidata error for '{search_term}': {e}")
    return labels


def main() -> None:
    """Add new concepts and harvest labels."""
    g = Graph()
    g.parse(VOCAB_FILE, format="turtle")
    g.bind("sevocab", SEVOCAB)

    initial_triples = len(g)
    initial_alt = len(list(g.triples((None, SKOS.altLabel, None))))

    for concept in NEW_CONCEPTS:
        iri = SEVOCAB[concept["iri"]]
        print(f"\n--- Adding {concept['iri']} ---")

        # Add concept
        g.add((iri, RDF.type, SKOS.Concept))
        g.add((iri, RDFS.label, Literal(concept["prefLabel"], lang="en")))
        g.add((iri, SKOS.prefLabel, Literal(concept["prefLabel"], lang="en")))
        g.add((iri, SKOS.definition, Literal(concept["definition"], lang="en")))
        g.add((iri, SKOS.inScheme, SEVOCAB.TechnologyOrFuelScheme))

        if concept["parent"]:
            g.add((iri, SKOS.broader, SEVOCAB[concept["parent"]]))
        else:
            g.add((iri, SKOS.topConceptOf, SEVOCAB.TechnologyOrFuelScheme))

        # Collect all altLabels
        all_labels: set[str] = set()

        # Seed altLabels
        for label in concept["seed_altLabels"]:
            all_labels.add(label)

        # OEO descendants
        oeo_labels = harvest_oeo_descendants(concept["oeo"])
        print(f"  OEO: {len(oeo_labels)} labels from {concept['oeo']}")
        for label in oeo_labels:
            all_labels.add(label)

        # Wikidata
        wd_labels = harvest_wikidata(concept["wd_search"])
        print(f"  Wikidata: {len(wd_labels)} labels for '{concept['wd_search']}'")
        for label in wd_labels:
            # Basic noise filter
            lower = label.lower()
            if any(
                skip in lower
                for skip in [
                    "patent",
                    "film",
                    "album",
                    "village",
                    "municipality",
                    "wikimedia",
                    "journal",
                    "article",
                    "person",
                ]
            ):
                continue
            if len(label) <= 1:
                continue
            all_labels.add(label)

        # Add altLabels (skip the prefLabel itself)
        added = 0
        for label in sorted(all_labels):
            if label.lower() != concept["prefLabel"].lower():
                g.add((iri, SKOS.altLabel, Literal(label, lang="en")))
                added += 1
        print(f"  Added {added} altLabels")

        time.sleep(1.5)  # Polite to Wikidata

    final_triples = len(g)
    final_alt = len(list(g.triples((None, SKOS.altLabel, None))))

    print(f"\n{'=' * 60}")
    print(f"Triples: {initial_triples} -> {final_triples} (+{final_triples - initial_triples})")
    print(f"altLabels: {initial_alt} -> {final_alt} (+{final_alt - initial_alt})")

    g.serialize(VOCAB_FILE, format="turtle")
    print(f"Wrote updated vocabulary to {VOCAB_FILE}")


if __name__ == "__main__":
    main()
