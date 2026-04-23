"""Build the energy-intel SHACL shapes file.

Generates ``shapes/energy-intel-shapes.ttl`` covering the four
first-batch shapes from conceptualizer handoff bullet 6:

- **S-1 DID-scheme URI** on ``ei:authoredBy`` values.
- **S-2 JSON-parseable** on ``ei:rawDims``.
- **S-3 interval ordering** (``ei:intervalEnd >= ei:intervalStart``) via
  SPARQL constraint.
- **CQ-009 SHACL companion** — every CMC must have an inbound
  ``ei:evidences`` from an ``ei:EvidenceSource``.

Runs via ``uv run python ontologies/energy-intel/scripts/build_shapes.py``.
"""

from __future__ import annotations

from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SH, XSD

EI = Namespace("https://w3id.org/energy-intel/")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT = PROJECT_ROOT / "shapes" / "energy-intel-shapes.ttl"


def add_prefixes_decl(g: Graph, sparql_node: BNode | URIRef) -> None:
    """Attach a shared ei: + xsd: prefix declaration to a SPARQLConstraint.

    Represented as ``sh:prefixes`` → an owl:Ontology node that declares
    one ``sh:declare`` triple per prefix. This is the canonical pattern
    used by pyshacl.
    """
    decl_ont = URIRef("https://w3id.org/energy-intel/shapes/prefix-decl")
    g.add((sparql_node, SH.prefixes, decl_ont))
    g.add((decl_ont, RDF.type, OWL.Ontology))

    # Only add the inner declarations once per graph — idempotent:
    if (decl_ont, SH.declare, None) not in g:
        ei_decl = BNode()
        g.add((decl_ont, SH.declare, ei_decl))
        g.add((ei_decl, SH.prefix, Literal("ei")))
        g.add((ei_decl, SH.namespace, Literal(str(EI), datatype=XSD.anyURI)))

        xsd_decl = BNode()
        g.add((decl_ont, SH.declare, xsd_decl))
        g.add((xsd_decl, SH.prefix, Literal("xsd")))
        g.add(
            (
                xsd_decl,
                SH.namespace,
                Literal("http://www.w3.org/2001/XMLSchema#", datatype=XSD.anyURI),
            )
        )


def main() -> None:
    g = Graph()
    g.bind("ei", EI)
    g.bind("sh", SH)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    g.bind("dcterms", DCTERMS)

    ont = URIRef("https://w3id.org/energy-intel/shapes/energy-intel-shapes")
    g.add((ont, RDF.type, OWL.Ontology))
    g.add(
        (
            ont,
            DCTERMS.title,
            Literal("energy-intel — SHACL shapes (V0)", lang="en"),
        )
    )
    g.add(
        (
            ont,
            DCTERMS.description,
            Literal(
                "First-batch SHACL shapes for energy-intel V0 — DID-scheme "
                "URIs on authors, JSON-parseable raw dimensions, interval "
                "ordering, and CQ-009 CMC-evidence invariant.",
                lang="en",
            ),
        )
    )
    g.add((ont, OWL.versionInfo, Literal("v0 (2026-04-22)")))

    # ---------------------------------------------------------------
    # S-1: DID-scheme URI on ei:authoredBy values
    # ---------------------------------------------------------------
    s1 = EI["shape/DidSchemeOnAuthoredBy"]
    g.add((s1, RDF.type, SH.NodeShape))
    g.add((s1, RDFS.label, Literal("S-1: DID-scheme URI on authoredBy", lang="en")))
    g.add((s1, SH.targetClass, EI.Post))
    s1_prop = BNode()
    g.add((s1, SH.property, s1_prop))
    g.add((s1_prop, SH.path, EI.authoredBy))
    g.add((s1_prop, SH.nodeKind, SH.IRI))
    g.add(
        (
            s1_prop,
            SH.pattern,
            Literal("^did:(plc|web):[A-Za-z0-9._:%-]+$"),
        )
    )
    g.add(
        (
            s1_prop,
            SH.message,
            Literal(
                "ei:authoredBy value must be a DID IRI (did:plc:... or did:web:...).",
                lang="en",
            ),
        )
    )
    g.add((s1_prop, SH.severity, SH.Violation))

    # ---------------------------------------------------------------
    # S-2: JSON-parseable on ei:rawDims (SPARQL regex heuristic)
    # ---------------------------------------------------------------
    s2 = EI["shape/JsonParseableRawDims"]
    g.add((s2, RDF.type, SH.NodeShape))
    g.add(
        (
            s2,
            RDFS.label,
            Literal("S-2: JSON-parseable rawDims on CMC", lang="en"),
        )
    )
    g.add((s2, SH.targetClass, EI.CanonicalMeasurementClaim))
    s2_sparql = BNode()
    g.add((s2, SH.sparql, s2_sparql))
    g.add((s2_sparql, RDF.type, SH.SPARQLConstraint))
    g.add(
        (
            s2_sparql,
            SH.message,
            Literal(
                "ei:rawDims must be a JSON object or array literal (leading brace or bracket).",
                lang="en",
            ),
        )
    )
    g.add(
        (
            s2_sparql,
            SH.select,
            Literal(
                "SELECT $this ?value WHERE { "
                "$this ei:rawDims ?value . "
                "FILTER(! regex(str(?value), '^\\\\s*[\\\\{\\\\[]')) "
                "}"
            ),
        )
    )
    add_prefixes_decl(g, s2_sparql)

    # ---------------------------------------------------------------
    # S-3: ClaimTemporalWindow interval ordering
    # ---------------------------------------------------------------
    s3 = EI["shape/IntervalOrdering"]
    g.add((s3, RDF.type, SH.NodeShape))
    g.add(
        (
            s3,
            RDFS.label,
            Literal("S-3: ClaimTemporalWindow interval ordering", lang="en"),
        )
    )
    g.add((s3, SH.targetClass, EI.ClaimTemporalWindow))
    s3_sparql = BNode()
    g.add((s3, SH.sparql, s3_sparql))
    g.add((s3_sparql, RDF.type, SH.SPARQLConstraint))
    g.add(
        (
            s3_sparql,
            SH.message,
            Literal(
                "ei:intervalEnd must be >= ei:intervalStart when both are present.",
                lang="en",
            ),
        )
    )
    g.add(
        (
            s3_sparql,
            SH.select,
            Literal(
                "SELECT $this ?start ?end WHERE { "
                "$this ei:intervalStart ?start ; ei:intervalEnd ?end . "
                "FILTER(?end < ?start) "
                "}"
            ),
        )
    )
    add_prefixes_decl(g, s3_sparql)

    # ---------------------------------------------------------------
    # CQ-009 SHACL companion
    # ---------------------------------------------------------------
    s_cq9 = EI["shape/CMCEvidenceSource"]
    g.add((s_cq9, RDF.type, SH.NodeShape))
    g.add(
        (
            s_cq9,
            RDFS.label,
            Literal(
                "CQ-009: CMC has inbound ei:evidences from EvidenceSource",
                lang="en",
            ),
        )
    )
    g.add((s_cq9, SH.targetClass, EI.CanonicalMeasurementClaim))
    s_cq9_prop = BNode()
    g.add((s_cq9, SH.property, s_cq9_prop))
    inv_path = BNode()
    g.add((s_cq9_prop, SH.path, inv_path))
    g.add((inv_path, SH.inversePath, EI.evidences))
    g.add((s_cq9_prop, SH.minCount, Literal("1", datatype=XSD.integer)))
    g.add((s_cq9_prop, SH["class"], EI.EvidenceSource))
    g.add(
        (
            s_cq9_prop,
            SH.message,
            Literal(
                "Every CanonicalMeasurementClaim must be evidenced by at "
                "least one ei:EvidenceSource (CQ-009 invariant).",
                lang="en",
            ),
        )
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=OUT, format="turtle")
    print(f"wrote {OUT} ({len(g)} triples)")


if __name__ == "__main__":
    main()
