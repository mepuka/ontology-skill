"""Prune overly broad surface forms flagged by SKY-311.

Background
----------
After SKY-309 Part C wired `measuredProperty` and `domainObject` into the
Stage 2 kernel, the Stage 1+2 comparative eval run showed +12 resolved
residuals but +7 wrong-new-match false positives. The 7 new cases all
traced to two bare, polysemous surface forms:

1. `sevocab:EmissionsMeasure` altLabel "emissions" (measured-property)
   -- matched on IPCC climate figures and household gas bills that
   mention "emissions" without referring to an energy measured
   property.

2. `sevocab:ElectricityDomain` altLabel "power" (domain-object)
   -- matched on a solar-panel specific-power (W/kg) chart because
   "power" is polysemous: electrical power, specific power, political
   power, computing power.

The ticket also called out `gas` on both `sevocab:NaturalGasDomain`
(domain-object) and `sevocab:NaturalGas` (technology-or-fuel) as
polysemous (natural gas vs greenhouse gas vs gasoline), and flagged
`generation` on `sevocab:Generation` as ambiguous with "next
generation" / "demographic generation".

This script removes the five bare polysemous altLabels and adds six
anchored replacements that preserve productive matching for the same
concepts. The canonical prefLabels are untouched; only searchable
altLabels change.

Removals (5)
------------
- EmissionsMeasure  skos:altLabel "emissions"@en
- Generation        skos:altLabel "generation"@en
- ElectricityDomain skos:altLabel "power"@en
- NaturalGasDomain  skos:altLabel "gas"@en   (DomainObjectScheme)
- NaturalGas        skos:altLabel "gas"@en   (TechnologyOrFuelScheme)

Additions (6)
-------------
- EmissionsMeasure  skos:altLabel "energy sector emissions"@en
- EmissionsMeasure  skos:altLabel "power sector emissions"@en
- EmissionsMeasure  skos:altLabel "emissions factor"@en
- Generation        skos:altLabel "electricity generation"@en
- Generation        skos:altLabel "power generation"@en
- Generation        skos:altLabel "energy generation"@en

Version bump
------------
owl:versionInfo 0.2.0 -> 0.2.1 (PATCH: curation fix, no semantic
changes).

Usage
-----
    uv run python scripts/prune_broad_surface_forms.py
"""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, SKOS

VOCAB_DIR = Path(__file__).parent.parent
VOCAB_FILE = VOCAB_DIR / "skygest-energy-vocab.ttl"

SEVOCAB = Namespace("https://skygest.dev/vocab/energy/")

REMOVALS: list[tuple[str, str, str]] = [
    ("EmissionsMeasure", "emissions", "en"),
    ("Generation", "generation", "en"),
    ("ElectricityDomain", "power", "en"),
    ("NaturalGasDomain", "gas", "en"),
    ("NaturalGas", "gas", "en"),
]

ADDITIONS: list[tuple[str, str, str]] = [
    ("EmissionsMeasure", "energy sector emissions", "en"),
    ("EmissionsMeasure", "power sector emissions", "en"),
    ("EmissionsMeasure", "emissions factor", "en"),
    ("Generation", "electricity generation", "en"),
    ("Generation", "power generation", "en"),
    ("Generation", "energy generation", "en"),
]

ONTOLOGY_IRI = URIRef("https://skygest.dev/vocab/energy")
OLD_VERSION = "0.2.0"
NEW_VERSION = "0.2.1"
OLD_VERSION_IRI = URIRef("https://skygest.dev/vocab/energy/0.2.0")
NEW_VERSION_IRI = URIRef("https://skygest.dev/vocab/energy/0.2.1")


def main() -> None:
    """Apply the SKY-311 curation patch to the sevocab Turtle."""
    g = Graph()
    g.parse(VOCAB_FILE, format="turtle")

    print("Removals:")
    for concept_local, label_text, lang in REMOVALS:
        concept = SEVOCAB[concept_local]
        triple = (concept, SKOS.altLabel, Literal(label_text, lang=lang))
        if triple in g:
            g.remove(triple)
            print(f'  - {concept_local} skos:altLabel "{label_text}"@{lang}')
        else:
            print(f'  ! NOT FOUND: {concept_local} skos:altLabel "{label_text}"@{lang}')

    print("\nAdditions:")
    for concept_local, label_text, lang in ADDITIONS:
        concept = SEVOCAB[concept_local]
        triple = (concept, SKOS.altLabel, Literal(label_text, lang=lang))
        if triple in g:
            print(f'  = ALREADY PRESENT: {concept_local} skos:altLabel "{label_text}"@{lang}')
        else:
            g.add(triple)
            print(f'  + {concept_local} skos:altLabel "{label_text}"@{lang}')

    # Version bump
    old_info = (ONTOLOGY_IRI, OWL.versionInfo, Literal(OLD_VERSION))
    new_info = (ONTOLOGY_IRI, OWL.versionInfo, Literal(NEW_VERSION))
    old_iri = (ONTOLOGY_IRI, OWL.versionIRI, OLD_VERSION_IRI)
    new_iri = (ONTOLOGY_IRI, OWL.versionIRI, NEW_VERSION_IRI)

    if old_info in g:
        g.remove(old_info)
        g.add(new_info)
        print(f"\nVersion: {OLD_VERSION} -> {NEW_VERSION}")
    else:
        current = list(g.objects(ONTOLOGY_IRI, OWL.versionInfo))
        print(
            f"\n! versionInfo bump skipped: expected {OLD_VERSION!r}, "
            f"found={[str(c) for c in current]}"
        )

    if old_iri in g:
        g.remove(old_iri)
        g.add(new_iri)
        print(f"versionIRI: .../{OLD_VERSION} -> .../{NEW_VERSION}")
    else:
        current = list(g.objects(ONTOLOGY_IRI, OWL.versionIRI))
        print(
            f"! versionIRI bump skipped: expected .../{OLD_VERSION}, "
            f"found={[str(c) for c in current]}"
        )

    g.serialize(destination=str(VOCAB_FILE), format="turtle")
    print(f"\nSaved: {VOCAB_FILE}")


if __name__ == "__main__":
    main()
