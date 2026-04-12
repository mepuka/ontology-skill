"""Resolve intra-scheme surface form collisions.

Removes ambiguous altLabels from the less-specific concept to ensure
buildVocabularyIndex() won't raise VocabularyCollisionError.

Resolution strategy:
- Child concept wins over parent (offshore wind > wind for "offshore wind power")
- More-specific concept wins (brown coal > coal for "lignite")
- Domain-appropriate concept wins (renewable > nuclear for "clean energy")
- If genuinely ambiguous, remove from both (let Stage 3 decide)

Usage:
    uv run python scripts/resolve_collisions.py
"""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import SKOS

VOCAB_DIR = Path(__file__).parent.parent
VOCAB_FILE = VOCAB_DIR / "skygest-energy-vocab.ttl"

SEVOCAB = Namespace("https://skygest.dev/vocab/energy/")

# Resolution rules: (surface_form_lower, keep_on_concept, remove_from_concept)
# "keep" = the concept that should own this surface form
RESOLUTIONS = [
    # Child wins over parent
    ("lignite", "BrownCoal", "Coal"),
    ("offshore wind power", "OffshoreWind", "Wind"),
    ("offshore wind energy", "OffshoreWind", "Wind"),
    ("offshorewind", "OffshoreWind", "Wind"),
    ("wind power", "Wind", "OffshoreWind"),  # Wind owns the generic term
    ("wind power energy", "Wind", "OffshoreWind"),
    # Hydro children — child wins
    ("pumped hydro storage power plant", "PumpedHydro", "Hydro"),
    ("closed-loop pumped hydro storage power plant", "PumpedHydro", "Hydro"),
    ("open-loop pumped hydro storage power plant", "PumpedHydro", "Hydro"),
    ("marine wave energy power plant", "Marine", "Hydro"),
    # Renewable owns the generic green/clean terms
    ("clean energy", "Renewable", "Nuclear"),
    ("clean power", "Renewable", "Nuclear"),
    ("green energy", "Renewable", "Nuclear"),
    ("green power", "Renewable", "Nuclear"),
    ("green electricity", "Renewable", "Nuclear"),
    ("ecological energy", "Renewable", "Nuclear"),
    ("ecological power", "Renewable", "Nuclear"),
    ("low-carbon energy", "Renewable", "Nuclear"),
    ("sustainable energy", "Renewable", "Nuclear"),
    ("alternative energy", "Renewable", "Nuclear"),
    ("alternative energy", "Renewable", "Wind"),
    # Bioenergy → Biomass (not Wind — Wind got it from Wikidata superclass noise)
    ("bioenergy", "Biomass", "Wind"),
    # Waste-to-energy → Waste (not Biomass)
    ("waste-to-energy", "Waste", "Biomass"),
]


def main() -> None:
    """Apply collision resolutions."""
    g = Graph()
    g.parse(VOCAB_FILE, format="turtle")

    removed = 0
    for surface_form_lower, keep_concept, remove_concept in RESOLUTIONS:
        concept_iri = SEVOCAB[remove_concept]

        # Find and remove the matching altLabel
        to_remove = []
        for s, p, o in g.triples((concept_iri, SKOS.altLabel, None)):
            if str(o).lower().strip() == surface_form_lower:
                to_remove.append((s, p, o))

        for triple in to_remove:
            g.remove(triple)
            removed += 1
            print(
                f'  Removed "{surface_form_lower}" from {remove_concept} (kept on {keep_concept})'
            )

    g.serialize(VOCAB_FILE, format="turtle")
    print(f"\nRemoved {removed} colliding altLabels")
    print(f"Wrote updated vocabulary to {VOCAB_FILE}")


if __name__ == "__main__":
    main()
