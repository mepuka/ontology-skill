"""Hand-seed a minimal energy-technology SKOS tree for V0 CQ-013/014.

The BOT-extracted OEO technology module supplies canonical plan-spec
classes (e.g., ``OEO_00020267`` energy technology). In V0 we also want a
tiny local ``ei:concept/wind`` hierarchy so CQ-013/CQ-014 fixtures can
demonstrate the transitive property-path walk without depending on the
punned OEO class tree landing first.

Output: ``modules/concept-schemes/technology-seeds.ttl``.

These concepts act as ``skos:Concept`` individuals under a top
``ei:concept/technology`` scheme. Narrower ``wind`` has two
``skos:narrower`` children (``onshore-wind``, ``offshore-wind``) so
CQ-013's ``(skos:broader|rdfs:subClassOf)*`` property path has
something to traverse.
"""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

EI_CONCEPT = Namespace("https://w3id.org/energy-intel/concept/")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT = PROJECT_ROOT / "modules" / "concept-schemes" / "technology-seeds.ttl"


def main() -> None:
    g = Graph()
    g.bind("ei-concept", EI_CONCEPT)
    g.bind("skos", SKOS)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("dcterms", DCTERMS)
    g.bind("xsd", XSD)

    ont = URIRef("https://w3id.org/energy-intel/modules/concept-schemes/technology-seeds")
    g.add((ont, RDF.type, OWL.Ontology))
    g.add(
        (
            ont,
            DCTERMS.title,
            Literal("energy-intel — Technology SKOS seeds (V0)", lang="en"),
        )
    )
    g.add(
        (
            ont,
            DCTERMS.description,
            Literal(
                "Minimal V0 technology SKOS tree (wind branch) for CQ-013/CQ-014 "
                "fixtures. Complements the BOT-extracted OEO plan-spec classes.",
                lang="en",
            ),
        )
    )
    g.add((ont, OWL.versionInfo, Literal("v0 (2026-04-22)")))
    g.add((ont, DCTERMS.created, Literal("2026-04-22", datatype=XSD.date)))

    scheme = EI_CONCEPT["technology"]
    g.add((scheme, RDF.type, SKOS.ConceptScheme))
    g.add((scheme, RDF.type, OWL.NamedIndividual))
    g.add((scheme, RDFS.label, Literal("energy technology concepts", lang="en")))
    g.add((scheme, SKOS.prefLabel, Literal("energy technology concepts", lang="en")))
    g.add(
        (
            scheme,
            SKOS.definition,
            Literal(
                "Local energy-technology SKOS scheme used as codomain of ei:aboutTechnology in V0.",
                lang="en",
            ),
        )
    )

    concepts = [
        ("wind", "wind", None, "Wind-based energy technology (top-level)."),
        ("onshore-wind", "onshore wind", "wind", "Wind technology installed on land."),
        (
            "offshore-wind",
            "offshore wind",
            "wind",
            "Wind technology installed on bodies of water.",
        ),
        ("solar", "solar", None, "Solar-based energy technology (top-level)."),
        (
            "solar-pv",
            "solar photovoltaic",
            "solar",
            "Solar PV cells generating electricity directly from sunlight.",
        ),
    ]

    concept_iris: dict[str, URIRef] = {}
    for short, label, parent, definition in concepts:
        iri = EI_CONCEPT[short]
        concept_iris[short] = iri
        g.add((iri, RDF.type, SKOS.Concept))
        g.add((iri, RDF.type, OWL.NamedIndividual))
        g.add((iri, RDFS.label, Literal(label, lang="en")))
        g.add((iri, SKOS.prefLabel, Literal(label, lang="en")))
        g.add((iri, SKOS.definition, Literal(definition, lang="en")))
        g.add((iri, SKOS.inScheme, scheme))
        if parent is None:
            g.add((iri, SKOS.topConceptOf, scheme))
            g.add((scheme, SKOS.hasTopConcept, iri))
        else:
            parent_iri = concept_iris[parent]
            g.add((iri, SKOS.broader, parent_iri))
            g.add((parent_iri, SKOS.narrower, iri))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=OUT, format="turtle")
    print(f"wrote {OUT} ({len(g)} triples)")


if __name__ == "__main__":
    main()
