"""Build the energy-intel SHACL shapes file.

Generates ``shapes/energy-intel-shapes.ttl`` covering V0 + V1 shapes:

V0 first-batch (from conceptualizer V0 handoff):

- **S-1 DID-scheme URI** on ``ei:authoredBy`` values.
- **S-2 JSON-parseable** on ``ei:rawDims``.
- **S-3 interval ordering** (``ei:intervalEnd >= ei:intervalStart``) via
  SPARQL constraint.
- **CQ-009 SHACL companion** — every CMC must have an inbound
  ``ei:evidences`` from an ``ei:EvidenceSource``.

V1 additions (from shacl-vs-owl-v1.md § 2; conceptualizer-to-architect-handoff-v1.md § 3):

- **S-V1-1** ``ei:canonicalUnit`` value MUST be in the imported QUDT subset.
- **S-V1-2** Resolvability gate: if ``ei:assertedUnit`` is present, ``ei:canonicalUnit``
  SHOULD also be present (severity Warning).
- **S-V1-3** ``ei:Post.authoredBy`` value MUST bear an ``ei:EnergyExpertRole`` via
  ``bfo:0000053``. Defense-in-depth on the V1 Expert refactor.
- **S-V1-4** ``ei:PodcastSegment.spokenBy`` value SHOULD bear an ``ei:EnergyExpertRole``
  (severity Warning).
- **S-V1-5** ``ei:aboutTechnology`` values MUST be either a ``skos:Concept`` (V0
  hand-seeded scheme) OR an imported OEO subtree class.

Runs via ``uv run python ontologies/energy-intel/scripts/build_shapes.py``.
"""

from __future__ import annotations

from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SH, SKOS, XSD

EI = Namespace("https://w3id.org/energy-intel/")
QUDT = Namespace("http://qudt.org/schema/qudt/")
UNIT = Namespace("http://qudt.org/vocab/unit/")
OEO = Namespace("https://openenergyplatform.org/ontology/oeo/")
BFO = Namespace("http://purl.obolibrary.org/obo/BFO_")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT = PROJECT_ROOT / "shapes" / "energy-intel-shapes.ttl"

# QUDT 2.1 vocab/unit IRIs that the V1 imports actually pulled in. Mirrors
# build_v1_imports.py:QUDT_UNIT_SEEDS. Kept in sync at refresh time.
QUDT_UNIT_SUBSET_LOCAL_NAMES: tuple[str, ...] = (
    "GigaW",
    "MegaW",
    "TeraW",
    "KiloW",
    "W",
    "TeraW-HR",
    "GigaW-HR",
    "MegaW-HR",
    "KiloW-HR",
    "PetaJ",
    "TeraJ",
    "GigaJ",
    "J",
    "BTU_IT",
    "TON_Metric",
    "KiloGM",
    "GM",
    "BBL",
    "BBL_UK_PET",
    "KiloGM-PER-J",
    "HZ",
    "V",
    "A",
    "PERCENT",
    "KiloMOL",
)

# OEO subtree roots whose transitive descendants are valid ei:aboutTechnology
# fillers per S-V1-5. Sourced from imports-manifest-v1.yaml seed_terms.
OEO_TECHNOLOGY_ROOTS: tuple[str, ...] = (
    "OEO_00020267",  # energy technology
    "OEO_00000011",  # energy converting component
    "OEO_00020039",  # energy carrier
)


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


def add_v1_prefixes_decl(g: Graph, sparql_node: BNode | URIRef) -> None:
    """Like ``add_prefixes_decl`` but also declares OEO + qudt + qudt-unit + bfo + skos prefixes.

    Some of the V1 SPARQL constraints reference imported namespaces that the
    V0 prefix-decl ontology does not list.
    """
    decl_ont = URIRef("https://w3id.org/energy-intel/shapes/prefix-decl-v1")
    g.add((sparql_node, SH.prefixes, decl_ont))
    g.add((decl_ont, RDF.type, OWL.Ontology))

    if (decl_ont, SH.declare, None) in g:
        return  # already populated for this graph

    pairs: list[tuple[str, str]] = [
        ("ei", str(EI)),
        ("xsd", "http://www.w3.org/2001/XMLSchema#"),
        ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
        ("rdfs", "http://www.w3.org/2000/01/rdf-schema#"),
        ("skos", "http://www.w3.org/2004/02/skos/core#"),
        ("foaf", "http://xmlns.com/foaf/0.1/"),
        ("bfo", str(BFO)),
        ("oeo", str(OEO)),
        ("qudt", str(QUDT)),
        ("unit", str(UNIT)),
    ]
    for prefix, namespace in pairs:
        decl = BNode()
        g.add((decl_ont, SH.declare, decl))
        g.add((decl, SH.prefix, Literal(prefix)))
        g.add((decl, SH.namespace, Literal(namespace, datatype=XSD.anyURI)))


def main() -> None:
    g = Graph()
    g.bind("ei", EI)
    g.bind("sh", SH)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    g.bind("dcterms", DCTERMS)
    g.bind("skos", SKOS)
    g.bind("bfo", BFO)
    g.bind("qudt", QUDT)
    g.bind("unit", UNIT)
    g.bind("oeo", OEO)

    ont = URIRef("https://w3id.org/energy-intel/shapes/energy-intel-shapes")
    g.add((ont, RDF.type, OWL.Ontology))
    g.add(
        (
            ont,
            DCTERMS.title,
            Literal("energy-intel — SHACL shapes (V0 + V1)", lang="en"),
        )
    )
    g.add(
        (
            ont,
            DCTERMS.description,
            Literal(
                "SHACL shapes for energy-intel V0 + V1. V0: DID-scheme URIs "
                "on authors, JSON-parseable raw dimensions, interval ordering, "
                "and CQ-009 CMC-evidence invariant. V1 (per shacl-vs-owl-v1.md "
                "§ 2): canonicalUnit-in-QUDT-subset, resolvability-gate, "
                "Post.authoredBy bears EnergyExpertRole, PodcastSegment.spokenBy "
                "bears EnergyExpertRole, and aboutTechnology-in-recognized-vocab.",
                lang="en",
            ),
        )
    )
    g.add((ont, OWL.versionInfo, Literal("v1 (2026-04-27)")))
    g.add((ont, DCTERMS.modified, Literal("2026-04-27", datatype=XSD.date)))

    # ---------------------------------------------------------------
    # S-1: Skygest-namespaced DID-embedded URI on ei:authoredBy values
    #
    # Per Linear D3 ABox policy, Expert individuals live at
    # https://id.skygest.io/expert/did-{plc|web}-<slug>; raw did:plc:... /
    # did:web:... URIs are NOT the deployed form. The shape enforces the
    # Skygest-wrapped form and still guarantees a DID is embedded in the
    # slug so downstream resolvers can recover the source DID.
    # ---------------------------------------------------------------
    s1 = EI["shape/DidSchemeOnAuthoredBy"]
    g.add((s1, RDF.type, SH.NodeShape))
    g.add((s1, RDFS.label, Literal("S-1: Skygest-DID URI on authoredBy", lang="en")))
    g.add((s1, SH.targetClass, EI.Post))
    s1_prop = BNode()
    g.add((s1, SH.property, s1_prop))
    g.add((s1_prop, SH.path, EI.authoredBy))
    g.add((s1_prop, SH.nodeKind, SH.IRI))
    g.add(
        (
            s1_prop,
            SH.pattern,
            Literal(r"^https://id\.skygest\.io/expert/did-(plc|web)-[A-Za-z0-9._-]+$"),
        )
    )
    g.add(
        (
            s1_prop,
            SH.message,
            Literal(
                "ei:authoredBy value must be a Skygest-namespaced Expert IRI "
                "with an embedded DID (e.g., https://id.skygest.io/expert/"
                "did-plc-<slug>), per Linear D3 ABox policy.",
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

    # ===================================================================
    # V1 shapes (S-V1-1 .. S-V1-5)
    # ===================================================================

    # ---------------------------------------------------------------
    # S-V1-1: ei:canonicalUnit value MUST be in the imported QUDT subset.
    # Closed-world enumeration via sh:in over the 25 unit IRIs.
    # ---------------------------------------------------------------
    s_v1_1 = EI["shape/CanonicalUnitInQudtSubset"]
    g.add((s_v1_1, RDF.type, SH.NodeShape))
    g.add(
        (
            s_v1_1,
            RDFS.label,
            Literal(
                "S-V1-1: ei:canonicalUnit value must be one of the imported QUDT 2.1 units",
                lang="en",
            ),
        )
    )
    g.add((s_v1_1, SH.targetClass, EI.CanonicalMeasurementClaim))
    s_v1_1_prop = BNode()
    g.add((s_v1_1, SH.property, s_v1_1_prop))
    g.add((s_v1_1_prop, SH.path, EI.canonicalUnit))
    g.add((s_v1_1_prop, SH.nodeKind, SH.IRI))
    in_list = BNode()
    g.add((s_v1_1_prop, SH["in"], in_list))
    Collection(g, in_list, [UNIT[name] for name in QUDT_UNIT_SUBSET_LOCAL_NAMES])
    g.add(
        (
            s_v1_1_prop,
            SH.message,
            Literal(
                "ei:canonicalUnit value must be one of the imported QUDT 2.1 unit "
                "IRIs (25 frozen values per imports-manifest-v1.yaml). Use "
                "unit:GigaW (not unit:GW); the V0 manifest's IRIs were wrong.",
                lang="en",
            ),
        )
    )
    g.add((s_v1_1_prop, SH.severity, SH.Violation))

    # ---------------------------------------------------------------
    # S-V1-2: Resolvability-gate hint. If ei:assertedUnit is present,
    # ei:canonicalUnit SHOULD also be present (severity Warning).
    # SPARQL-based "if A then B" check with NOT EXISTS.
    # ---------------------------------------------------------------
    s_v1_2 = EI["shape/ResolvabilityGate"]
    g.add((s_v1_2, RDF.type, SH.NodeShape))
    g.add(
        (
            s_v1_2,
            RDFS.label,
            Literal(
                "S-V1-2: assertedUnit-without-canonicalUnit resolvability hint",
                lang="en",
            ),
        )
    )
    g.add((s_v1_2, SH.targetClass, EI.CanonicalMeasurementClaim))
    # sh:severity on the NodeShape so pyshacl propagates it to validation
    # results. SHACL spec allows it on either the shape or the constraint;
    # shape-level is the canonical place.
    g.add((s_v1_2, SH.severity, SH.Warning))
    s_v1_2_sparql = BNode()
    g.add((s_v1_2, SH.sparql, s_v1_2_sparql))
    g.add((s_v1_2_sparql, RDF.type, SH.SPARQLConstraint))
    g.add(
        (
            s_v1_2_sparql,
            SH.message,
            Literal(
                "CMC has ei:assertedUnit set but no ei:canonicalUnit — the "
                "resolvability stage has not yet promoted this claim. UC-007.",
                lang="en",
            ),
        )
    )
    g.add(
        (
            s_v1_2_sparql,
            SH.select,
            Literal(
                "SELECT $this WHERE { "
                "$this ei:assertedUnit ?au . "
                "FILTER NOT EXISTS { $this ei:canonicalUnit ?cu . } "
                "}"
            ),
        )
    )
    add_v1_prefixes_decl(g, s_v1_2_sparql)

    # ---------------------------------------------------------------
    # S-V1-3: ei:Post.authoredBy value MUST bear an ei:EnergyExpertRole
    # via bfo:0000053. Implemented as a SPARQLConstraint targeting Post,
    # because qualifiedValueShape on a property path is awkward and the
    # SPARQL form is what the conceptualizer's worked example aligns with.
    # ---------------------------------------------------------------
    s_v1_3 = EI["shape/PostAuthorBearsEnergyExpertRole"]
    g.add((s_v1_3, RDF.type, SH.NodeShape))
    g.add(
        (
            s_v1_3,
            RDFS.label,
            Literal(
                "S-V1-3: Post.authoredBy value bears an ei:EnergyExpertRole",
                lang="en",
            ),
        )
    )
    g.add((s_v1_3, SH.targetClass, EI.Post))
    s_v1_3_sparql = BNode()
    g.add((s_v1_3, SH.sparql, s_v1_3_sparql))
    g.add((s_v1_3_sparql, RDF.type, SH.SPARQLConstraint))
    g.add(
        (
            s_v1_3_sparql,
            SH.message,
            Literal(
                "Post.authoredBy must point to a foaf:Person who bears at least "
                "one ei:EnergyExpertRole via bfo:0000053. Required for Skygest "
                "ingest (CQ-018, scope-v1.md § In-scope).",
                lang="en",
            ),
        )
    )
    g.add(
        (
            s_v1_3_sparql,
            SH.select,
            Literal(
                "SELECT $this ?author WHERE { "
                "$this ei:authoredBy ?author . "
                "FILTER NOT EXISTS { ?author bfo:0000053 ?role . ?role a ei:EnergyExpertRole . } "
                "}"
            ),
        )
    )
    g.add((s_v1_3_sparql, SH.severity, SH.Violation))
    add_v1_prefixes_decl(g, s_v1_3_sparql)

    # ---------------------------------------------------------------
    # S-V1-4: PodcastSegment.spokenBy value SHOULD bear an EnergyExpertRole
    # (severity Warning). Symmetric to S-V1-3 but soft.
    # ---------------------------------------------------------------
    s_v1_4 = EI["shape/PodcastSpeakerBearsEnergyExpertRole"]
    g.add((s_v1_4, RDF.type, SH.NodeShape))
    g.add(
        (
            s_v1_4,
            RDFS.label,
            Literal(
                "S-V1-4: PodcastSegment.spokenBy value should bear an ei:EnergyExpertRole",
                lang="en",
            ),
        )
    )
    g.add((s_v1_4, SH.targetClass, EI.PodcastSegment))
    g.add((s_v1_4, SH.severity, SH.Warning))
    s_v1_4_sparql = BNode()
    g.add((s_v1_4, SH.sparql, s_v1_4_sparql))
    g.add((s_v1_4_sparql, RDF.type, SH.SPARQLConstraint))
    g.add(
        (
            s_v1_4_sparql,
            SH.message,
            Literal(
                "PodcastSegment.spokenBy points to a foaf:Person without an "
                "ei:EnergyExpertRole (warning). Hosts and non-expert guests "
                "can speak in segments, so this is informational only.",
                lang="en",
            ),
        )
    )
    g.add(
        (
            s_v1_4_sparql,
            SH.select,
            Literal(
                "SELECT $this ?speaker WHERE { "
                "$this ei:spokenBy ?speaker . "
                "FILTER NOT EXISTS { ?speaker bfo:0000053 ?role . ?role a ei:EnergyExpertRole . } "
                "}"
            ),
        )
    )
    add_v1_prefixes_decl(g, s_v1_4_sparql)

    # ---------------------------------------------------------------
    # S-V1-5: ei:aboutTechnology values must be either a skos:Concept (V0
    # hand-seeded scheme) OR an imported OEO subtree class. SPARQL-form
    # because sh:or with rdfs:subClassOf* property paths is awkward.
    # ---------------------------------------------------------------
    s_v1_5 = EI["shape/AboutTechnologyInRecognizedVocab"]
    g.add((s_v1_5, RDF.type, SH.NodeShape))
    g.add(
        (
            s_v1_5,
            RDFS.label,
            Literal(
                "S-V1-5: ei:aboutTechnology value is in a recognised vocabulary",
                lang="en",
            ),
        )
    )
    g.add((s_v1_5, SH.targetClass, EI.CanonicalMeasurementClaim))
    s_v1_5_sparql = BNode()
    g.add((s_v1_5, SH.sparql, s_v1_5_sparql))
    g.add((s_v1_5_sparql, RDF.type, SH.SPARQLConstraint))

    # SPARQL-1.1 query: walk subClassOf* / broader* up to either a project
    # skos:Concept root or one of the OEO subtree roots.
    oeo_root_filter = " || ".join([f"?root = <{OEO[name]}>" for name in OEO_TECHNOLOGY_ROOTS])
    select = (
        "SELECT $this ?value WHERE { "
        "$this ei:aboutTechnology ?value . "
        "FILTER NOT EXISTS { ?value a skos:Concept . } "
        "FILTER NOT EXISTS { "
        "  ?value (rdfs:subClassOf|skos:broader)* ?root . "
        f"  FILTER ({oeo_root_filter}) "
        "} "
        "}"
    )
    g.add((s_v1_5_sparql, SH.select, Literal(select)))
    g.add(
        (
            s_v1_5_sparql,
            SH.message,
            Literal(
                "ei:aboutTechnology value is neither a skos:Concept (V0 "
                "hand-seeded scheme) nor a transitive descendant of an "
                "imported OEO subtree root (energy-technology, "
                "energy-converting-component, energy-carrier).",
                lang="en",
            ),
        )
    )
    g.add((s_v1_5_sparql, SH.severity, SH.Violation))
    add_v1_prefixes_decl(g, s_v1_5_sparql)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=OUT, format="turtle")
    print(f"wrote {OUT} ({len(g)} triples)")


if __name__ == "__main__":
    main()
