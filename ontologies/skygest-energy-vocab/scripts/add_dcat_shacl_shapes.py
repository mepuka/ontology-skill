"""Add SHACL shapes for the DCAT structural extension.

Creates EnergyVariableShape, EnergyDatasetShape, and EnergyAgentShape
to validate structural constraints.

Usage:
    uv run python scripts/add_dcat_shacl_shapes.py
"""

from __future__ import annotations

from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace
from rdflib.namespace import DCTERMS, FOAF, RDF, RDFS, XSD

SEVOCAB = Namespace("https://skygest.dev/vocab/energy/")
SEVOCAB_SHAPES = Namespace("https://skygest.dev/vocab/energy/shapes/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
QB = Namespace("http://purl.org/linked-data/cube#")
SH = Namespace("http://www.w3.org/ns/shacl#")

SHAPES_DIR = Path("ontologies/skygest-energy-vocab/shapes")
SHAPES_FILE = SHAPES_DIR / "skygest-energy-vocab-shapes.ttl"

# Facet dimensions: (property local name, code list scheme, required?)
FACET_DIMS = [
    ("measuredProperty", "MeasuredPropertyScheme", True),
    ("statisticType", "StatisticTypeScheme", True),
    ("domainObject", "DomainObjectScheme", False),
    ("technologyOrFuel", "TechnologyOrFuelScheme", False),
    ("aggregation", "AggregationScheme", False),
    ("unitFamily", "UnitFamilyScheme", False),
    ("policyInstrument", "PolicyInstrumentScheme", False),
]


def add_structural_shapes(g: Graph) -> int:
    """Add SHACL shapes for the DCAT structural layer."""
    before = len(g)

    g.bind("sevocab", SEVOCAB)
    g.bind("sevocab-shapes", SEVOCAB_SHAPES)
    g.bind("dcat", DCAT)
    g.bind("qb", QB)
    g.bind("sh", SH)
    g.bind("foaf", FOAF)
    g.bind("dcterms", DCTERMS)

    # ── EnergyVariableShape ─────────────────────────────────────────────
    ev_shape = SEVOCAB_SHAPES.EnergyVariableShape
    g.add((ev_shape, RDF.type, SH.NodeShape))
    g.add((ev_shape, SH.targetClass, SEVOCAB.EnergyVariable))
    g.add(
        (
            ev_shape,
            RDFS.comment,
            Literal(
                "Validates EnergyVariable instances: required facets and cardinality.",
                lang="en",
            ),
        )
    )

    # Required: rdfs:label
    label_prop = BNode()
    g.add((ev_shape, SH.property, label_prop))
    g.add((label_prop, SH.path, RDFS.label))
    g.add((label_prop, SH.minCount, Literal(1, datatype=XSD.integer)))
    g.add((label_prop, SH.name, Literal("label")))
    g.add(
        (
            label_prop,
            SH.message,
            Literal("Every EnergyVariable must have an rdfs:label"),
        )
    )

    # Facet dimension constraints
    for prop_local, _scheme_local, required in FACET_DIMS:
        prop_shape = BNode()
        g.add((ev_shape, SH.property, prop_shape))
        g.add((prop_shape, SH.path, SEVOCAB[prop_local]))
        g.add((prop_shape, SH.maxCount, Literal(1, datatype=XSD.integer)))
        g.add((prop_shape, SH.nodeKind, SH.IRI))
        g.add((prop_shape, SH.name, Literal(prop_local)))
        g.add(
            (
                prop_shape,
                SH.message,
                Literal(f"EnergyVariable.{prop_local} must be at most 1 IRI"),
            )
        )
        if required:
            g.add((prop_shape, SH.minCount, Literal(1, datatype=XSD.integer)))

    # ── EnergyDatasetShape ──────────────────────────────────────────────
    ed_shape = SEVOCAB_SHAPES.EnergyDatasetShape
    g.add((ed_shape, RDF.type, SH.NodeShape))
    g.add((ed_shape, SH.targetClass, SEVOCAB.EnergyDataset))
    g.add(
        (
            ed_shape,
            RDFS.comment,
            Literal(
                "Validates EnergyDataset instances: publisher, variables.",
                lang="en",
            ),
        )
    )

    # Required: dct:title
    title_prop = BNode()
    g.add((ed_shape, SH.property, title_prop))
    g.add((title_prop, SH.path, DCTERMS.title))
    g.add((title_prop, SH.minCount, Literal(1, datatype=XSD.integer)))
    g.add((title_prop, SH.name, Literal("title")))
    g.add(
        (
            title_prop,
            SH.message,
            Literal("Every EnergyDataset must have a dct:title"),
        )
    )

    # Required: dct:publisher
    pub_prop = BNode()
    g.add((ed_shape, SH.property, pub_prop))
    g.add((pub_prop, SH.path, DCTERMS.publisher))
    g.add((pub_prop, SH.minCount, Literal(1, datatype=XSD.integer)))
    g.add((pub_prop, SH["class"], SEVOCAB.EnergyAgent))
    g.add((pub_prop, SH.name, Literal("publisher")))
    g.add(
        (
            pub_prop,
            SH.message,
            Literal("Every EnergyDataset must have a dct:publisher of type EnergyAgent"),
        )
    )

    # EnergyDataset must have at least one Variable
    var_prop = BNode()
    g.add((ed_shape, SH.property, var_prop))
    g.add((var_prop, SH.path, SEVOCAB.hasVariable))
    g.add((var_prop, SH.minCount, Literal(1, datatype=XSD.integer)))
    g.add((var_prop, SH["class"], SEVOCAB.EnergyVariable))
    g.add((var_prop, SH.name, Literal("has variable")))
    g.add(
        (
            var_prop,
            SH.message,
            Literal("Every EnergyDataset must have at least one EnergyVariable"),
        )
    )

    # ── EnergyAgentShape ────────────────────────────────────────────────
    ea_shape = SEVOCAB_SHAPES.EnergyAgentShape
    g.add((ea_shape, RDF.type, SH.NodeShape))
    g.add((ea_shape, SH.targetClass, SEVOCAB.EnergyAgent))
    g.add(
        (
            ea_shape,
            RDFS.comment,
            Literal("Validates EnergyAgent instances: label required.", lang="en"),
        )
    )

    # Required: rdfs:label
    agent_label = BNode()
    g.add((ea_shape, SH.property, agent_label))
    g.add((agent_label, SH.path, RDFS.label))
    g.add((agent_label, SH.minCount, Literal(1, datatype=XSD.integer)))
    g.add((agent_label, SH.name, Literal("label")))
    g.add(
        (
            agent_label,
            SH.message,
            Literal("Every EnergyAgent must have an rdfs:label"),
        )
    )

    return len(g) - before


def main() -> None:
    """Add DCAT SHACL shapes to the shapes file."""
    print(f"Reading: {SHAPES_FILE}")
    g = Graph()
    g.parse(SHAPES_FILE, format="turtle")
    print(f"  Triples before: {len(g)}")

    # Check if structural shapes already exist
    if (SEVOCAB_SHAPES.EnergyVariableShape, RDF.type, SH.NodeShape) in g:
        print("  Structural shapes already present -- skipping.")
        return

    added = add_structural_shapes(g)
    print(f"  Triples added: {added}")

    g.serialize(destination=str(SHAPES_FILE), format="turtle")
    print(f"  Saved: {SHAPES_FILE}")

    print()
    print("Shapes added:")
    print("  EnergyVariableShape: label + 7 facet dims (2 required)")
    print("  EnergyDatasetShape: title + publisher + hasVariable")
    print("  EnergyAgentShape: label")


if __name__ == "__main__":
    main()
