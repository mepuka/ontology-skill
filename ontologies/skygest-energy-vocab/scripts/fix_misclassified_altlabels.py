"""Remove misclassified altLabels surfaced by eval run 2026-04-12.

SKY-308: Fix 3 surface forms causing wrong-new-match false positives:

1. sevocab:Coal  — remove "carbon"@en
   Reason: "carbon" in chart text refers to CO2 emissions, not coal as fuel.
   Triggered wrong match on post 020-lightbucket ("Carbon Intensity of Electricity").

2. sevocab:Flow  — remove "production"@en
   Reason: "production" is ambiguous (manufacturing vs electricity generation).
   Triggered wrong match on post 009-irena ("module production cost").
   Remaining altLabels "generation" and "output" cover the flow concept adequately.

3. sevocab:DimensionlessUnit  — remove "%"@en
   Reason: "%" appears in virtually every chart with statistics; too generic to
   discriminate. Remaining altLabel "percent" is sufficient.

Usage:
    uv run python scripts/fix_misclassified_altlabels.py
"""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import SKOS

VOCAB_DIR = Path(__file__).parent.parent
VOCAB_FILE = VOCAB_DIR / "skygest-energy-vocab.ttl"

SEVOCAB = Namespace("https://skygest.dev/vocab/energy/")

# (concept IRI, altLabel value, language tag)
REMOVALS: list[tuple[str, str, str]] = [
    ("Coal", "carbon", "en"),
    ("Flow", "production", "en"),
    ("DimensionlessUnit", "%", "en"),
]


def main() -> None:
    """Remove misclassified altLabels from the vocabulary Turtle."""
    g = Graph()
    g.parse(VOCAB_FILE, format="turtle")

    for concept_local, label_text, lang in REMOVALS:
        concept = SEVOCAB[concept_local]
        triple = (concept, SKOS.altLabel, Literal(label_text, lang=lang))

        if triple in g:
            g.remove(triple)
            print(f'  Removed: {concept_local} skos:altLabel "{label_text}"@{lang}')
        else:
            print(f'  NOT FOUND: {concept_local} skos:altLabel "{label_text}"@{lang}')

    # Serialize back — rdflib Turtle serializer with sorted output
    g.serialize(destination=str(VOCAB_FILE), format="turtle")
    print(f"\nSaved: {VOCAB_FILE}")


if __name__ == "__main__":
    main()
