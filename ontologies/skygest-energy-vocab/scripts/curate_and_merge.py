"""Curate harvested labels and merge into vocabulary Turtle.

Filters the neighborhood survey to high-signal surface forms,
then adds them as skos:altLabel triples to the vocabulary graph.

Usage:
    uv run python scripts/curate_and_merge.py
"""

from __future__ import annotations

import json
from pathlib import Path

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import SKOS

VOCAB_DIR = Path(__file__).parent.parent
VOCAB_FILE = VOCAB_DIR / "skygest-energy-vocab.ttl"
SURVEY_FILE = VOCAB_DIR / "data" / "neighborhood-survey.json"
OUTPUT_FILE = VOCAB_DIR / "skygest-energy-vocab.ttl"

SEVOCAB = Namespace("https://skygest.dev/vocab/energy/")

# Concept IRI mapping (sevocab:X -> full IRI)
CONCEPT_IRIS = {
    "sevocab:SolarPv": SEVOCAB.SolarPv,
    "sevocab:Wind": SEVOCAB.Wind,
    "sevocab:OnshoreWind": SEVOCAB.OnshoreWind,
    "sevocab:OffshoreWind": SEVOCAB.OffshoreWind,
    "sevocab:Battery": SEVOCAB.Battery,
    "sevocab:Renewable": SEVOCAB.Renewable,
    "sevocab:Nuclear": SEVOCAB.Nuclear,
    "sevocab:Coal": SEVOCAB.Coal,
    "sevocab:BrownCoal": SEVOCAB.BrownCoal,
    "sevocab:HeatPump": SEVOCAB.HeatPump,
    "sevocab:Hydrogen": SEVOCAB.Hydrogen,
    "sevocab:NaturalGas": SEVOCAB.NaturalGas,
    "sevocab:GasCcgt": SEVOCAB.GasCcgt,
}

# Noise filters — reject surface forms matching these patterns
REJECT_EXACT = {
    "none",
    "change",
    "changing",
    "tech",
    "technologies",
    "technology",
    "technology sector",
    "sector",
    "economic sector",
    "carbone",
    "element 1",
    "element 6",
    "₆c",
    "sedimentary rock",
    "group in classification of productive activities",
    "thermodynamic cycle",
    "heat exchange",
    "heat transfer",
    "source of energy",
    "energy sources",
    "energy source",
    "energy resources",
    "energy resource",
    "energy generating resource",
    "energy-generating resource",
    "nuclear science",
    "technological science",
    "technological sciences",
    "technicology",
}

REJECT_PREFIXES = [
    "nuclear power in ",
    "nuclear energy in ",
    "nuclear industry in ",
    "wind power in ",
    "renewable energy in ",
    "2006 ",
    "waroona",  # specific projects
    "isic ",
    "nace ",  # classification codes (not chart text)
    "05.2 ",  # NACE codes
]

REJECT_SUFFIXES = [
    " by country",
    " by region",
    " by country or region",
    " quality assurance",
]

# Too-specific or off-domain terms
REJECT_CONTAINS = [
    "wikimedia",
    "congressional",
    "wall street",
    "patent",
    "argentina",
    "journal",
    "article",
]


def is_noise(surface_form: str, _relation: str) -> bool:
    """Return True if this surface form should be rejected."""
    sf_lower = surface_form.lower().strip()

    if sf_lower in REJECT_EXACT:
        return True

    for prefix in REJECT_PREFIXES:
        if sf_lower.startswith(prefix):
            return True

    for suffix in REJECT_SUFFIXES:
        if sf_lower.endswith(suffix):
            return True

    for term in REJECT_CONTAINS:
        if term in sf_lower:
            return True

    # Reject very short forms (single char) except known abbreviations
    if len(sf_lower) <= 1:
        return True

    # Reject forms that are just QID references
    return sf_lower.startswith("q") and sf_lower[1:].isdigit()


def main() -> None:
    """Curate and merge labels into vocabulary."""
    survey = json.loads(SURVEY_FILE.read_text())

    # Load existing graph
    g = Graph()
    g.parse(VOCAB_FILE, format="turtle")

    # Collect existing altLabels to avoid duplicates
    existing: set[tuple[str, str]] = set()
    for s, _p, o in g.triples((None, SKOS.altLabel, None)):
        existing.add((str(s), str(o).lower().strip()))

    initial_count = len(list(g.triples((None, SKOS.altLabel, None))))

    added = 0
    rejected_noise = 0
    rejected_dup = 0

    for concept_id, labels in survey.items():
        concept_iri = CONCEPT_IRIS.get(concept_id)
        if not concept_iri:
            continue

        for lbl in labels:
            sf = lbl["surface_form"].strip()
            relation = lbl.get("relation", "")

            if is_noise(sf, relation):
                rejected_noise += 1
                continue

            key = (str(concept_iri), sf.lower().strip())
            if key in existing:
                rejected_dup += 1
                continue

            # Add as English altLabel
            g.add((concept_iri, SKOS.altLabel, Literal(sf, lang="en")))
            existing.add(key)
            added += 1

    final_count = len(list(g.triples((None, SKOS.altLabel, None))))

    print(f"Existing altLabels: {initial_count}")
    print(f"Candidates reviewed: {sum(len(v) for v in survey.values())}")
    print(f"Rejected (noise): {rejected_noise}")
    print(f"Rejected (duplicate): {rejected_dup}")
    print(f"Added: {added}")
    print(f"Final altLabel count: {final_count}")

    # Serialize back
    g.serialize(OUTPUT_FILE, format="turtle")
    print(f"\nWrote updated vocabulary to {OUTPUT_FILE}")

    # Show what was added per concept
    print("\n=== Added surface forms ===")
    # Re-parse to get clean diff
    new_g = Graph()
    new_g.parse(OUTPUT_FILE, format="turtle")
    new_count = len(new_g)
    print(f"Total triples: {new_count}")


if __name__ == "__main__":
    main()
