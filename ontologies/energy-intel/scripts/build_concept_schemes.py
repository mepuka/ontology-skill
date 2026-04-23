"""Generate the two hand-seeded SKOS ConceptSchemes for energy-intel V0.

Builds Value Partition-style schemes per ODP F.1:

- ``modules/concept-schemes/temporal-resolution.ttl``
  five concepts: hourly, daily, monthly, quarterly, annual.
- ``modules/concept-schemes/aggregation-type.ttl``
  five concepts: sum, average, minimum, maximum, count.

Each scheme:

- Declares ``skos:ConceptScheme``
- Adds five ``skos:Concept`` instances
- Uses ``skos:topConceptOf`` / ``skos:hasTopConcept`` + ``skos:inScheme``
- Declares the five concepts pairwise ``skos:related`` (Value Partition
  indicator) AND ``owl:AllDifferent`` so the HermiT reasoner treats them
  as distinct individuals under UNA.
- Emits an explicit ``owl:Ontology`` header so ``robot merge`` sees a
  named module.

Run via ``uv run python ontologies/energy-intel/scripts/build_concept_schemes.py``.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

if TYPE_CHECKING:
    from collections.abc import Iterable

EI = Namespace("https://w3id.org/energy-intel/")
PROV = Namespace("http://www.w3.org/ns/prov#")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules" / "concept-schemes"


def _graph_header(ontology_iri: URIRef, title: str, description: str) -> Graph:
    g = Graph()
    g.bind("", EI)
    g.bind("ei", EI)
    g.bind("owl", OWL)
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    g.bind("prov", PROV)
    g.add((ontology_iri, RDF.type, OWL.Ontology))
    g.add((ontology_iri, DCTERMS.title, Literal(title, lang="en")))
    g.add((ontology_iri, DCTERMS.description, Literal(description, lang="en")))
    g.add((ontology_iri, OWL.versionInfo, Literal("v0 (2026-04-22)")))
    g.add((ontology_iri, DCTERMS.created, Literal("2026-04-22", datatype=XSD.date)))
    g.add(
        (
            ontology_iri,
            RDFS.comment,
            Literal(
                "Hand-seeded SKOS ConceptScheme per Value Partition ODP F.1. "
                "See docs/axiom-plan.md Foundational section and imports-manifest.yaml.",
                lang="en",
            ),
        )
    )
    return g


def _add_scheme(
    g: Graph,
    scheme: URIRef,
    label: str,
    definition: str,
    concepts: Iterable[tuple[URIRef, str, str]],
) -> None:
    g.add((scheme, RDF.type, SKOS.ConceptScheme))
    g.add((scheme, RDF.type, OWL.NamedIndividual))
    g.add((scheme, RDFS.label, Literal(label, lang="en")))
    g.add((scheme, DCTERMS.title, Literal(label, lang="en")))
    g.add((scheme, SKOS.prefLabel, Literal(label, lang="en")))
    g.add((scheme, SKOS.definition, Literal(definition, lang="en")))

    concept_iris: list[URIRef] = []
    for iri, c_label, c_def in concepts:
        g.add((iri, RDF.type, SKOS.Concept))
        g.add((iri, RDF.type, OWL.NamedIndividual))
        g.add((iri, RDFS.label, Literal(c_label, lang="en")))
        g.add((iri, SKOS.prefLabel, Literal(c_label, lang="en")))
        g.add((iri, SKOS.definition, Literal(c_def, lang="en")))
        g.add((iri, SKOS.inScheme, scheme))
        g.add((iri, SKOS.topConceptOf, scheme))
        g.add((scheme, SKOS.hasTopConcept, iri))
        concept_iris.append(iri)

    # Pairwise skos:related (non-hierarchical association; all siblings)
    # Per ODP F.1 value partition semantics.
    for i, a in enumerate(concept_iris):
        for b in concept_iris[i + 1 :]:
            g.add((a, SKOS.related, b))
            g.add((b, SKOS.related, a))

    # AllDifferent — DL-safe mutual distinctness for HermiT.
    diff = URIRef(str(scheme) + "/AllDifferent")
    g.add((diff, RDF.type, OWL.AllDifferent))
    list_node = URIRef(str(scheme) + "/AllDifferent/members")
    Collection(g, list_node, concept_iris)
    g.add((diff, OWL.distinctMembers, list_node))


def build_temporal_resolution() -> None:
    scheme = URIRef("https://w3id.org/energy-intel/concept/temporal-resolution")
    ont = URIRef("https://w3id.org/energy-intel/modules/concept-schemes/temporal-resolution")
    g = _graph_header(
        ont,
        "energy-intel — Temporal Resolution ConceptScheme",
        "Value Partition ODP F.1 scheme enumerating the five canonical "
        "temporal-resolution concepts used on CMC and Series.",
    )
    base = "https://w3id.org/energy-intel/concept/temporal-resolution/"
    concepts = [
        (
            URIRef(base + "hourly"),
            "hourly",
            "A temporal resolution of one hour per observation bucket.",
        ),
        (
            URIRef(base + "daily"),
            "daily",
            "A temporal resolution of one day per observation bucket.",
        ),
        (
            URIRef(base + "monthly"),
            "monthly",
            "A temporal resolution of one calendar month per observation bucket.",
        ),
        (
            URIRef(base + "quarterly"),
            "quarterly",
            "A temporal resolution of one calendar quarter per observation bucket.",
        ),
        (
            URIRef(base + "annual"),
            "annual",
            "A temporal resolution of one calendar year per observation bucket.",
        ),
    ]
    _add_scheme(
        g,
        scheme,
        "temporal resolution",
        "The canonical temporal-resolution kind of an observation or claim.",
        concepts,
    )
    out = MODULES_DIR / "temporal-resolution.ttl"
    out.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=out, format="turtle")
    print(f"wrote {out} ({len(g)} triples)")


def build_aggregation_type() -> None:
    scheme = URIRef("https://w3id.org/energy-intel/concept/aggregation-type")
    ont = URIRef("https://w3id.org/energy-intel/modules/concept-schemes/aggregation-type")
    g = _graph_header(
        ont,
        "energy-intel — Aggregation Type ConceptScheme",
        "Value Partition ODP F.1 scheme enumerating the five canonical "
        "aggregation-type concepts. Replaces dropped oeo-aggregation-2.11.0 "
        "import (OEO v2.11.0 asserted subtree of 1 — see "
        "imports/oeo-seed-verification.md).",
    )
    base = "https://w3id.org/energy-intel/concept/aggregation-type/"
    concepts = [
        (
            URIRef(base + "sum"),
            "sum",
            "An aggregation that returns the additive total of the input values.",
        ),
        (
            URIRef(base + "average"),
            "average",
            "An aggregation that returns the arithmetic mean of the input values.",
        ),
        (
            URIRef(base + "minimum"),
            "minimum",
            "An aggregation that returns the smallest value among the input values.",
        ),
        (
            URIRef(base + "maximum"),
            "maximum",
            "An aggregation that returns the largest value among the input values.",
        ),
        (
            URIRef(base + "count"),
            "count",
            "An aggregation that returns the cardinality of the input sample.",
        ),
    ]
    _add_scheme(
        g,
        scheme,
        "aggregation type",
        "The canonical aggregation kind applied when producing a "
        "summary value from an input sample.",
        concepts,
    )
    out = MODULES_DIR / "aggregation-type.ttl"
    out.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=out, format="turtle")
    print(f"wrote {out} ({len(g)} triples)")


def main() -> None:
    build_temporal_resolution()
    build_aggregation_type()


if __name__ == "__main__":
    main()
