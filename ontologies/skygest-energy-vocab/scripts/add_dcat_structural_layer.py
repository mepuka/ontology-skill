"""Add DCAT structural layer to skygest-energy-vocab.

Extends the existing SKOS vocabulary with:
- 3 OWL classes: EnergyVariable, EnergyDataset, EnergyAgent
- 1 object property: hasVariable
- 7 qb:DimensionProperty instances (one per facet scheme)
- 1 qb:DataStructureDefinition (EnergyVariableStructure)
- OWL restrictions: existential (someValuesFrom) and qualified cardinality
- Disjointness axioms
- Import declarations for external vocabulary stubs

This is an additive extension — existing SKOS content is not modified.
The JSON build pipeline (build.py) is unaffected.

Phase: 4 — Formalization (ontology-architect skill)
Input: conceptual-model-dcat-extension.yaml, axiom-plan-dcat-extension.yaml
Output: Updated skygest-energy-vocab.ttl

Usage:
    uv run python scripts/add_dcat_structural_layer.py
"""

from __future__ import annotations

from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, FOAF, OWL, RDF, RDFS, SKOS, XSD

# ── Namespaces ──────────────────────────────────────────────────────────────

SEVOCAB = Namespace("https://skygest.dev/vocab/energy/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
QB = Namespace("http://purl.org/linked-data/cube#")
SCHEMA = Namespace("https://schema.org/")
SH = Namespace("http://www.w3.org/ns/shacl#")

VOCAB_DIR = Path(__file__).parent.parent
VOCAB_FILE = VOCAB_DIR / "skygest-energy-vocab.ttl"
IMPORTS_DIR = VOCAB_DIR / "imports"

# ── Facet dimension specifications ──────────────────────────────────────────

FACET_DIMENSIONS = [
    {
        "local": "measuredProperty",
        "label": "measured property",
        "definition": "The physical or economic quantity being measured.",
        "codeList": "MeasuredPropertyScheme",
    },
    {
        "local": "domainObject",
        "label": "domain object",
        "definition": "The entity or system the measurement is about.",
        "codeList": "DomainObjectScheme",
    },
    {
        "local": "technologyOrFuel",
        "label": "technology or fuel",
        "definition": "The energy technology or fuel type.",
        "codeList": "TechnologyOrFuelScheme",
    },
    {
        "local": "statisticType",
        "label": "statistic type",
        "definition": "The kind of statistical measure.",
        "codeList": "StatisticTypeScheme",
    },
    {
        "local": "aggregation",
        "label": "aggregation",
        "definition": "The temporal aggregation method.",
        "codeList": "AggregationScheme",
    },
    {
        "local": "unitFamily",
        "label": "unit family",
        "definition": "The family of measurement units.",
        "codeList": "UnitFamilyScheme",
    },
    {
        "local": "policyInstrument",
        "label": "policy instrument",
        "definition": "The policy mechanism involved.",
        "codeList": "PolicyInstrumentScheme",
    },
]


def _add_max_cardinality_restriction(
    g: Graph,
    cls: URIRef,
    prop: URIRef,
    max_card: int,
    on_class: URIRef,
) -> None:
    """Add maxQualifiedCardinality restriction as a superclass of cls."""
    restriction = BNode()
    g.add((restriction, RDF.type, OWL.Restriction))
    g.add((restriction, OWL.onProperty, prop))
    g.add(
        (
            restriction,
            OWL.maxQualifiedCardinality,
            Literal(max_card, datatype=XSD.nonNegativeInteger),
        )
    )
    g.add((restriction, OWL.onClass, on_class))
    g.add((cls, RDFS.subClassOf, restriction))


def _add_some_values_restriction(
    g: Graph,
    cls: URIRef,
    prop: URIRef,
    filler: URIRef,
) -> None:
    """Add existential (someValuesFrom) restriction as a superclass of cls."""
    restriction = BNode()
    g.add((restriction, RDF.type, OWL.Restriction))
    g.add((restriction, OWL.onProperty, prop))
    g.add((restriction, OWL.someValuesFrom, filler))
    g.add((cls, RDFS.subClassOf, restriction))


def add_structural_layer(g: Graph) -> int:
    """Add the DCAT structural layer to the graph. Returns count of triples added."""
    before = len(g)

    # ── Bind new prefixes ───────────────────────────────────────────────
    g.bind("dcat", DCAT)
    g.bind("qb", QB)
    g.bind("schema", SCHEMA)
    g.bind("foaf", FOAF)
    g.bind("sh", SH)

    ontology_iri = URIRef("https://skygest.dev/vocab/energy")

    # ── owl:imports for external stubs ──────────────────────────────────
    for import_iri in [
        URIRef("https://skygest.dev/vocab/energy/imports/dcat-extract"),
        URIRef("https://skygest.dev/vocab/energy/imports/datacube-extract"),
        URIRef("https://skygest.dev/vocab/energy/imports/schema-extract"),
        URIRef("https://skygest.dev/vocab/energy/imports/foaf-extract"),
    ]:
        g.add((ontology_iri, OWL.imports, import_iri))

    # ── Class: EnergyVariable ───────────────────────────────────────────
    ev = SEVOCAB.EnergyVariable
    g.add((ev, RDF.type, OWL.Class))
    g.add((ev, RDFS.subClassOf, SCHEMA.StatisticalVariable))
    g.add((ev, RDFS.label, Literal("energy variable", lang="en")))
    g.add(
        (
            ev,
            SKOS.definition,
            Literal(
                "A statistical variable that is composed of up to seven facet "
                "dimensions drawn from sevocab concept schemes.",
                lang="en",
            ),
        )
    )

    # ── Class: EnergyDataset ────────────────────────────────────────────
    ed = SEVOCAB.EnergyDataset
    g.add((ed, RDF.type, OWL.Class))
    g.add((ed, RDFS.subClassOf, DCAT.Dataset))
    g.add((ed, RDFS.label, Literal("energy dataset", lang="en")))
    g.add(
        (
            ed,
            SKOS.definition,
            Literal(
                "A DCAT dataset that contains one or more energy variables "
                "and is published by an energy agent.",
                lang="en",
            ),
        )
    )

    # ── Class: EnergyAgent ──────────────────────────────────────────────
    ea = SEVOCAB.EnergyAgent
    g.add((ea, RDF.type, OWL.Class))
    g.add((ea, RDFS.subClassOf, FOAF.Agent))
    g.add((ea, RDFS.label, Literal("energy agent", lang="en")))
    g.add(
        (
            ea,
            SKOS.definition,
            Literal(
                "A FOAF agent that publishes one or more energy datasets.",
                lang="en",
            ),
        )
    )

    # ── Disjointness: EnergyVariable, EnergyDataset, EnergyAgent ───────
    disjoint_bnode = BNode()
    g.add((disjoint_bnode, RDF.type, OWL.AllDisjointClasses))
    member_list = BNode()
    Collection(g, member_list, [ev, ed, ea])
    g.add((disjoint_bnode, OWL.members, member_list))

    # ── ObjectProperty: hasVariable ─────────────────────────────────────
    hv = SEVOCAB.hasVariable
    g.add((hv, RDF.type, OWL.ObjectProperty))
    g.add((hv, RDFS.domain, ed))
    g.add((hv, RDFS.range, ev))
    g.add((hv, RDFS.label, Literal("has variable", lang="en")))
    g.add(
        (
            hv,
            SKOS.definition,
            Literal(
                "Links an energy dataset to a constituent energy variable.",
                lang="en",
            ),
        )
    )

    # ── EnergyDataset restrictions ──────────────────────────────────────
    # Every EnergyDataset has at least one publisher (EnergyAgent)
    _add_some_values_restriction(g, ed, DCTERMS.publisher, ea)
    # Every EnergyDataset has at least one distribution
    _add_some_values_restriction(g, ed, DCAT.distribution, DCAT.Distribution)
    # Every EnergyDataset has at least one variable
    _add_some_values_restriction(g, ed, hv, ev)

    # ── 7 Dimension Properties ──────────────────────────────────────────
    for dim in FACET_DIMENSIONS:
        dim_iri = SEVOCAB[dim["local"]]
        code_list_iri = SEVOCAB[dim["codeList"]]

        # Type as both qb:DimensionProperty and owl:ObjectProperty
        g.add((dim_iri, RDF.type, QB.DimensionProperty))
        g.add((dim_iri, RDF.type, OWL.ObjectProperty))
        g.add((dim_iri, QB.codeList, code_list_iri))
        g.add((dim_iri, RDFS.label, Literal(dim["label"], lang="en")))
        g.add((dim_iri, SKOS.definition, Literal(dim["definition"], lang="en")))

        # Add maxQualifiedCardinality 1 restriction on EnergyVariable
        _add_max_cardinality_restriction(g, ev, dim_iri, 1, SKOS.Concept)

    # ── DataStructureDefinition: EnergyVariableStructure ────────────────
    dsd = SEVOCAB.EnergyVariableStructure
    g.add((dsd, RDF.type, QB.DataStructureDefinition))
    g.add((dsd, RDFS.label, Literal("energy variable structure", lang="en")))
    g.add(
        (
            dsd,
            SKOS.definition,
            Literal(
                "The data structure definition declaring the seven facet "
                "dimensions that compose an energy variable.",
                lang="en",
            ),
        )
    )

    for dim in FACET_DIMENSIONS:
        dim_iri = SEVOCAB[dim["local"]]
        comp = BNode()
        g.add((comp, RDF.type, QB.ComponentSpecification))
        g.add((comp, QB.dimension, dim_iri))
        g.add((dsd, QB.component, comp))

    after = len(g)
    return after - before


def main() -> None:
    """Add DCAT structural layer to the vocabulary Turtle."""
    print(f"Reading: {VOCAB_FILE}")
    g = Graph()
    g.parse(VOCAB_FILE, format="turtle")
    print(f"  Triples before: {len(g)}")

    # Check if structural layer already exists
    if (SEVOCAB.EnergyVariable, RDF.type, OWL.Class) in g:
        print("  Structural layer already present — skipping.")
        return

    added = add_structural_layer(g)
    print(f"  Triples added: {added}")
    print(f"  Triples after: {len(g)}")

    # Serialize
    g.serialize(destination=str(VOCAB_FILE), format="turtle")
    print(f"  Saved: {VOCAB_FILE}")

    # Summary
    print()
    print("Structural layer added:")
    print("  Classes: EnergyVariable, EnergyDataset, EnergyAgent")
    print("  Property: hasVariable")
    print("  Dimensions: 7 qb:DimensionProperty instances")
    print("  DSD: EnergyVariableStructure (7 components)")
    print("  Restrictions: 7 maxQualifiedCardinality + 3 someValuesFrom")
    print("  Disjointness: EnergyVariable ⊥ EnergyDataset ⊥ EnergyAgent")
    print("  Imports: 4 external vocabulary stubs")


if __name__ == "__main__":
    main()
