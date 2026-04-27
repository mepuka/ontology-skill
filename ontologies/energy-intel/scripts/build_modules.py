"""Build the four energy-intel TBox modules + top-level ontology.

Modules (strict authoring order per conceptualizer handoff bullet 1):

1. ``modules/agent.ttl`` — Expert, Organization, PublisherRole,
   DataProviderRole (BFO Role pattern + FOAF parents).
2. ``modules/media.ttl`` — Post, MediaAttachment (+ Chart, Screenshot,
   Excerpt, GenericImageAttachment), Conversation (+ SocialThread,
   PodcastEpisode), PodcastSegment, EvidenceSource abstract.
3. ``modules/measurement.ttl`` — CMC, Observation, Variable, Series,
   ClaimTemporalWindow, references* properties.
4. ``modules/data.ttl`` — DCAT extension only.

Top-level ``energy-intel.ttl`` ``owl:imports`` the four modules + every
row in ``imports-manifest.yaml``.

All axiom sketches come from ``docs/axiom-plan.md``. No axiom is invented
here — one-to-one implementation of the approved plan.

Run: ``uv run python ontologies/energy-intel/scripts/build_modules.py``
"""

from __future__ import annotations

from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

# -------------------------------------------------------------------
# Namespaces
# -------------------------------------------------------------------

EI = Namespace("https://w3id.org/energy-intel/")
BFO = Namespace("http://purl.obolibrary.org/obo/BFO_")
IAO = Namespace("http://purl.obolibrary.org/obo/IAO_")
OEO = Namespace("https://openenergyplatform.org/ontology/oeo/")
RO = Namespace("http://purl.obolibrary.org/obo/RO_")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
PROV = Namespace("http://www.w3.org/ns/prov#")
QUDT = Namespace("http://qudt.org/schema/qudt/")

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# -------------------------------------------------------------------
# V1 ontology version metadata (set 2026-04-27)
# -------------------------------------------------------------------
V1_VERSION_INFO = "v1 (2026-04-27)"
V1_CREATED = "2026-04-22"  # original V0 created date carried forward
V1_MODIFIED = "2026-04-27"
V1_TOP_VERSION_IRI = "https://w3id.org/energy-intel/v1/2026-04-27"

# -------------------------------------------------------------------
# Shared axiom helpers
# -------------------------------------------------------------------


def bind_common(g: Graph) -> None:
    g.bind("", EI)
    g.bind("ei", EI)
    g.bind("bfo", BFO)
    g.bind("iao", IAO)
    g.bind("oeo", OEO)
    g.bind("ro", RO)
    g.bind("foaf", FOAF)
    g.bind("dcat", DCAT)
    g.bind("prov", PROV)
    g.bind("qudt", QUDT)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("rdf", RDF)
    g.bind("xsd", XSD)
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)


def module_header(
    g: Graph,
    ontology_iri: URIRef,
    title: str,
    description: str,
    imports: list[URIRef] | None = None,
) -> None:
    g.add((ontology_iri, RDF.type, OWL.Ontology))
    g.add((ontology_iri, DCTERMS.title, Literal(title, lang="en")))
    g.add((ontology_iri, DCTERMS.description, Literal(description, lang="en")))
    g.add((ontology_iri, OWL.versionInfo, Literal(V1_VERSION_INFO)))
    g.add((ontology_iri, DCTERMS.created, Literal(V1_CREATED, datatype=XSD.date)))
    g.add((ontology_iri, DCTERMS.modified, Literal(V1_MODIFIED, datatype=XSD.date)))
    g.add(
        (
            ontology_iri,
            DCTERMS.creator,
            Literal("energy-intel / ontology-architect", lang="en"),
        )
    )
    g.add(
        (
            ontology_iri,
            DCTERMS.license,
            URIRef("https://creativecommons.org/licenses/by/4.0/"),
        )
    )
    if imports:
        for imp in imports:
            g.add((ontology_iri, OWL.imports, imp))


def declare_class(
    g: Graph,
    iri: URIRef,
    label: str,
    definition: str,
    parents: list[URIRef] | None = None,
) -> None:
    g.add((iri, RDF.type, OWL.Class))
    g.add((iri, RDFS.label, Literal(label, lang="en")))
    g.add((iri, SKOS.definition, Literal(definition, lang="en")))
    if parents:
        for p in parents:
            g.add((iri, RDFS.subClassOf, p))


def declare_object_property(
    g: Graph,
    iri: URIRef,
    label: str,
    domain: URIRef | None,
    range_: URIRef | None,
    functional: bool = False,
    asymmetric: bool = False,
    irreflexive: bool = False,
    sub_property_of: list[URIRef] | None = None,
    comment: str | None = None,
) -> None:
    g.add((iri, RDF.type, OWL.ObjectProperty))
    g.add((iri, RDFS.label, Literal(label, lang="en")))
    if comment:
        g.add((iri, RDFS.comment, Literal(comment, lang="en")))
    if domain is not None:
        g.add((iri, RDFS.domain, domain))
    if range_ is not None:
        g.add((iri, RDFS.range, range_))
    if functional:
        g.add((iri, RDF.type, OWL.FunctionalProperty))
    if asymmetric:
        g.add((iri, RDF.type, OWL.AsymmetricProperty))
    if irreflexive:
        g.add((iri, RDF.type, OWL.IrreflexiveProperty))
    if sub_property_of:
        for s in sub_property_of:
            g.add((iri, RDFS.subPropertyOf, s))


def declare_data_property(
    g: Graph,
    iri: URIRef,
    label: str,
    domain: URIRef | None,
    range_: URIRef | list[URIRef] | None,
    functional: bool = False,
    comment: str | None = None,
) -> None:
    g.add((iri, RDF.type, OWL.DatatypeProperty))
    g.add((iri, RDFS.label, Literal(label, lang="en")))
    if comment:
        g.add((iri, RDFS.comment, Literal(comment, lang="en")))
    if domain is not None:
        g.add((iri, RDFS.domain, domain))
    if functional:
        g.add((iri, RDF.type, OWL.FunctionalProperty))
    if range_ is None:
        return
    if isinstance(range_, list):
        # Datatype union via rdfs:Datatype + owl:unionOf.
        dt = BNode()
        g.add((dt, RDF.type, RDFS.Datatype))
        list_node = BNode()
        Collection(g, list_node, list(range_))
        g.add((dt, OWL.unionOf, list_node))
        g.add((iri, RDFS.range, dt))
    else:
        g.add((iri, RDFS.range, range_))


def subclass_some(g: Graph, cls: URIRef, prop: URIRef, filler: URIRef) -> None:
    """``cls rdfs:subClassOf (prop some filler)``."""
    r = BNode()
    g.add((r, RDF.type, OWL.Restriction))
    g.add((r, OWL.onProperty, prop))
    g.add((r, OWL.someValuesFrom, filler))
    g.add((cls, RDFS.subClassOf, r))


def subclass_qcr(
    g: Graph,
    cls: URIRef,
    prop: URIRef,
    filler: URIRef,
    kind: str,
    n: int,
) -> None:
    """Qualified cardinality restriction.

    ``kind`` in {"min", "max", "exactly"}.
    """
    r = BNode()
    g.add((r, RDF.type, OWL.Restriction))
    g.add((r, OWL.onProperty, prop))
    g.add((r, OWL.onClass, filler))
    prop_map = {
        "min": OWL.minQualifiedCardinality,
        "max": OWL.maxQualifiedCardinality,
        "exactly": OWL.qualifiedCardinality,
    }
    g.add(
        (
            r,
            prop_map[kind],
            Literal(str(n), datatype=XSD.nonNegativeInteger),
        )
    )
    g.add((cls, RDFS.subClassOf, r))


def subclass_qcr_inverse(
    g: Graph,
    cls: URIRef,
    prop: URIRef,
    filler: URIRef,
    kind: str,
    n: int,
) -> None:
    """``cls rdfs:subClassOf ((inverse prop) {kind} N filler)``."""
    inv = BNode()
    g.add((inv, OWL.inverseOf, prop))
    r = BNode()
    g.add((r, RDF.type, OWL.Restriction))
    g.add((r, OWL.onProperty, inv))
    g.add((r, OWL.onClass, filler))
    prop_map = {
        "min": OWL.minQualifiedCardinality,
        "max": OWL.maxQualifiedCardinality,
        "exactly": OWL.qualifiedCardinality,
    }
    g.add(
        (
            r,
            prop_map[kind],
            Literal(str(n), datatype=XSD.nonNegativeInteger),
        )
    )
    g.add((cls, RDFS.subClassOf, r))


def subclass_intersection(g: Graph, cls: URIRef, members: list[URIRef]) -> None:
    """``cls rdfs:subClassOf (owl:intersectionOf ( ... ))``."""
    inter = BNode()
    g.add((inter, RDF.type, OWL.Class))
    list_node = BNode()
    Collection(g, list_node, members)
    g.add((inter, OWL.intersectionOf, list_node))
    g.add((cls, RDFS.subClassOf, inter))


def equivalent_class_intersection_of(g: Graph, cls: URIRef, members: list) -> None:
    """``cls owl:equivalentClass [ owl:intersectionOf ( m1 m2 ... ) ]``.

    ``members`` may be a heterogeneous list of named classes (URIRefs) and
    anonymous restrictions (BNodes). Used for V1 A2: the
    ``ei:Expert ≡ foaf:Person ⊓ (bfo:0000053 some ei:EnergyExpertRole)`` axiom.
    """
    inter = BNode()
    g.add((inter, RDF.type, OWL.Class))
    list_node = BNode()
    Collection(g, list_node, members)
    g.add((inter, OWL.intersectionOf, list_node))
    g.add((cls, OWL.equivalentClass, inter))


def restriction_some(g: Graph, prop: URIRef, filler: URIRef) -> BNode:
    """Return a BNode for ``[ a owl:Restriction ; owl:onProperty P ; owl:someValuesFrom F ]``."""
    r = BNode()
    g.add((r, RDF.type, OWL.Restriction))
    g.add((r, OWL.onProperty, prop))
    g.add((r, OWL.someValuesFrom, filler))
    return r


def disjoint_classes(g: Graph, members: list[URIRef]) -> None:
    """``DisjointClasses(c1, c2, ..., cn)`` via owl:AllDisjointClasses."""
    bn = BNode()
    g.add((bn, RDF.type, OWL.AllDisjointClasses))
    list_node = BNode()
    Collection(g, list_node, members)
    g.add((bn, OWL.members, list_node))


# -------------------------------------------------------------------
# Module 1 — agent
# -------------------------------------------------------------------


def build_agent() -> Path:
    g = Graph()
    bind_common(g)

    ont = URIRef("https://w3id.org/energy-intel/modules/agent")
    module_header(
        g,
        ont,
        "energy-intel — agent module",
        "Expert, Organization, and the BFO-role pattern for publisher / data-provider roles.",
        imports=[
            URIRef("http://purl.obolibrary.org/obo/bfo.owl"),
            URIRef("http://xmlns.com/foaf/0.1/"),
        ],
    )

    # Classes -------------------------------------------------------

    # V1 A1: mint EnergyExpertRole as a BFO role inhering in foaf:Person.
    declare_class(
        g,
        EI.EnergyExpertRole,
        "energy expert role",
        "A BFO role inhering in a foaf:Person who publishes energy-domain "
        "claims (on social media, podcasts, or articles) that an editorial "
        "pipeline extracts as CanonicalMeasurementClaims.",
        parents=[BFO["0000023"]],  # bfo:Role
    )
    subclass_some(g, EI.EnergyExpertRole, BFO["0000052"], FOAF.Person)  # inheres_in

    # V1 A2: ei:Expert is the defined kind = (foaf:Person ⊓ ∃bfo:0000053.EnergyExpertRole).
    # Expert is no longer asserted ``rdfs:subClassOf foaf:Person`` — that
    # subsumption is entailed by the equivalent-class axiom.
    declare_class(
        g,
        EI.Expert,
        "Expert",
        "A foaf:Person who bears at least one ei:EnergyExpertRole. Defined "
        "(equivalent-class) so the reasoner classifies any role-bearer as an "
        "Expert. V1 redefinition supersedes V0 ``rdfs:subClassOf foaf:Person``.",
    )
    expert_role_restriction = restriction_some(g, BFO["0000053"], EI.EnergyExpertRole)
    equivalent_class_intersection_of(
        g,
        EI.Expert,
        [FOAF.Person, expert_role_restriction],
    )

    declare_class(
        g,
        EI.Organization,
        "Organization",
        "An organized group of persons (company, agency, research "
        "institute) that can bear a PublisherRole or DataProviderRole. "
        "Modeled as a FOAF Organization that is also a BFO ObjectAggregate.",
    )
    # Organization SubClassOf (foaf:Organization and bfo:ObjectAggregate)
    subclass_intersection(g, EI.Organization, [FOAF.Organization, BFO["0000027"]])

    declare_class(
        g,
        EI.PublisherRole,
        "publisher role",
        "A BFO role inhering in an Organization that publishes Posts or "
        "Distributions that evidence CMCs.",
        parents=[BFO["0000023"]],
    )
    subclass_some(g, EI.PublisherRole, BFO["0000052"], EI.Organization)  # inheres_in

    declare_class(
        g,
        EI.DataProviderRole,
        "data provider role",
        "A BFO role inhering in an Organization that acts as the authoritative "
        "data source referenced by one or more CMCs.",
        parents=[BFO["0000023"]],
    )
    subclass_some(g, EI.DataProviderRole, BFO["0000052"], EI.Organization)

    # Disjointness --------------------------------------------------
    # Expert DisjointWith Organization  (persons vs aggregates) — carry forward from V0.
    g.add((EI.Expert, OWL.disjointWith, EI.Organization))
    # PublisherRole DisjointWith DataProviderRole — V0 binary disjointness retained.
    g.add((EI.PublisherRole, OWL.disjointWith, EI.DataProviderRole))
    # V1 A3: three-way role disjointness (defense-in-depth per
    # anti-pattern-review-v1.md § 3). Subsumes the V0 binary axiom but does
    # not contradict it.
    disjoint_classes(
        g,
        [EI.EnergyExpertRole, EI.PublisherRole, EI.DataProviderRole],
    )

    out = PROJECT_ROOT / "modules" / "agent.ttl"
    out.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=out, format="turtle")
    print(f"wrote {out} ({len(g)} triples)")
    return out


# -------------------------------------------------------------------
# Module 2 — media
# -------------------------------------------------------------------


def build_media() -> Path:
    g = Graph()
    bind_common(g)

    ont = URIRef("https://w3id.org/energy-intel/modules/media")
    module_header(
        g,
        ont,
        "energy-intel — media module",
        "Post, MediaAttachment (Chart / Screenshot / Excerpt / "
        "GenericImageAttachment), Conversation / SocialThread / "
        "PodcastEpisode / PodcastSegment, and the abstract EvidenceSource.",
        imports=[
            URIRef("https://w3id.org/energy-intel/modules/agent"),
            URIRef("http://purl.obolibrary.org/obo/iao.owl"),
        ],
    )

    # Abstract parent: EvidenceSource
    declare_class(
        g,
        EI.EvidenceSource,
        "evidence source",
        "Abstract parent of any information content entity that can "
        "stand as the evidencing artefact for a CanonicalMeasurementClaim. "
        "Three asserted subclasses in V0: Post, MediaAttachment, PodcastSegment.",
        parents=[IAO["0000030"]],  # information content entity
    )

    # Post ----------------------------------------------------------
    declare_class(
        g,
        EI.Post,
        "post",
        "A social-media or short-form document authored by an Expert that "
        "may evidence CMCs. Re-parented to iao:Document and ei:EvidenceSource.",
        parents=[IAO["0000310"], EI.EvidenceSource],
    )

    # Conversation tree ---------------------------------------------
    declare_class(
        g,
        EI.Conversation,
        "conversation",
        "Abstract parent of multi-turn communicative artefacts (social threads, podcast episodes).",
        parents=[IAO["0000030"]],
    )

    declare_class(
        g,
        EI.SocialThread,
        "social thread",
        "A directed sequence of Posts forming a reply / quote / repost graph on a social platform.",
        parents=[EI.Conversation],
    )

    declare_class(
        g,
        EI.PodcastEpisode,
        "podcast episode",
        "A discrete podcast episode, modeled as both an iao:Document and a Conversation.",
        parents=[IAO["0000310"], EI.Conversation],
    )

    # MediaAttachment tree ------------------------------------------
    declare_class(
        g,
        EI.MediaAttachment,
        "media attachment",
        "Abstract parent of image/text artefacts attached to a Post and "
        "potentially evidencing a CMC.",
        parents=[IAO["0000030"], EI.EvidenceSource],
    )

    declare_class(
        g,
        EI.Chart,
        "chart",
        "A data-visualisation image attached to a Post. Re-parented to iao:Image.",
        parents=[IAO["0000101"], EI.MediaAttachment],
    )

    declare_class(
        g,
        EI.Screenshot,
        "screenshot",
        "A raster capture of a displayed document, UI, or data table.",
        parents=[IAO["0000101"], EI.MediaAttachment],
    )

    declare_class(
        g,
        EI.GenericImageAttachment,
        "generic image attachment",
        "Catch-all image attachment not classifiable as Chart or "
        "Screenshot (renamed from ei:Image 2026-04-22).",
        parents=[IAO["0000101"], EI.MediaAttachment],
    )

    declare_class(
        g,
        EI.Excerpt,
        "excerpt",
        "A text excerpt (quote / paragraph / table cell) embedded in or "
        "attached to a Post. Re-parented to iao:TextualEntity.",
        parents=[IAO["0000300"], EI.MediaAttachment],
    )

    # PodcastSegment -----------------------------------------------
    declare_class(
        g,
        EI.PodcastSegment,
        "podcast segment",
        "A bounded temporal span of a PodcastEpisode that can evidence "
        "a CMC and can be spoken by one or more Experts.",
        parents=[IAO["0000030"], EI.EvidenceSource],
    )

    # Disjointness --------------------------------------------------
    disjoint_classes(g, [EI.Post, EI.MediaAttachment, EI.PodcastSegment])
    disjoint_classes(g, [EI.Chart, EI.Screenshot, EI.Excerpt, EI.GenericImageAttachment])
    disjoint_classes(g, [EI.SocialThread, EI.PodcastEpisode])

    # Object properties --------------------------------------------
    # V1 A6: ei:authoredBy range widened from ei:Expert to foaf:Person.
    # The Post-level restriction is also updated (was: exactly 1 ei:Expert;
    # now: exactly 1 foaf:Person). This matches the V1 ontological reality
    # — Posts on the platform are authored by Persons, and the SHACL shape
    # S-V1-3 carries the runtime-level "must bear EnergyExpertRole" check.
    declare_object_property(
        g,
        EI.authoredBy,
        "authored by",
        domain=EI.Post,
        range_=FOAF.Person,
        functional=True,
        comment=(
            "Shortcut form of participation (ODP F.4). Every Post has exactly "
            "one author. V1: range widened from ei:Expert to foaf:Person; the "
            "role-bearing companion check moves to SHACL S-V1-3."
        ),
    )
    subclass_qcr(g, EI.Post, EI.authoredBy, FOAF.Person, "exactly", 1)

    # V1 A7: ei:spokenBy range widened from ei:Expert to foaf:Person.
    declare_object_property(
        g,
        EI.spokenBy,
        "spoken by",
        domain=EI.PodcastSegment,
        range_=FOAF.Person,
        comment=(
            "Binary participation shortcut for podcast speakers (multi-speaker "
            "segments allowed; no cardinality axiom). V1: range widened to "
            "foaf:Person; SHACL S-V1-4 carries the EnergyExpertRole-bearer "
            "warning at runtime."
        ),
    )

    declare_object_property(
        g,
        EI.presents,
        "presents",
        domain=EI.Post,
        range_=EI.MediaAttachment,
        comment="A Post presents one or more MediaAttachments.",
    )

    declare_object_property(
        g,
        EI.inConversation,
        "in conversation",
        domain=EI.Post,
        range_=EI.Conversation,
        comment="A Post belongs to a Conversation (SocialThread in V0).",
    )

    declare_object_property(
        g,
        EI.repliesTo,
        "replies to",
        domain=EI.Post,
        range_=EI.Post,
        comment=(
            "Reply edge in a SocialThread. Irreflexive and asymmetric (a Post "
            "cannot reply to itself)."
        ),
        asymmetric=True,
        irreflexive=True,
    )

    declare_object_property(
        g,
        EI.partOfEpisode,
        "part of episode",
        domain=EI.PodcastSegment,
        range_=EI.PodcastEpisode,
        functional=True,
        asymmetric=True,
        irreflexive=True,
        sub_property_of=[BFO["0000050"]],  # BFO:part_of
        comment=(
            "Part-whole for podcast segments. Renamed from ei:partOf 2026-04-22 "
            "per property-design § 8. Transitivity inherited from bfo:BFO_0000050."
        ),
    )
    subclass_qcr(g, EI.PodcastSegment, EI.partOfEpisode, EI.PodcastEpisode, "exactly", 1)

    declare_object_property(
        g,
        EI.screenshotOf,
        "screenshot of",
        domain=EI.Screenshot,
        range_=IAO["0000030"],  # information content entity
        comment="Optional pointer from a screenshot to the ICE it captures.",
    )

    declare_object_property(
        g,
        EI.excerptFrom,
        "excerpt from",
        domain=EI.Excerpt,
        range_=IAO["0000030"],
        comment="Optional pointer from an excerpt to the source document.",
    )

    # Data properties -----------------------------------------------
    declare_data_property(
        g,
        EI.hasSegmentIndex,
        "has segment index",
        domain=EI.PodcastSegment,
        range_=XSD.integer,
        functional=True,
        comment="0-based ordinal position of the segment within its episode.",
    )

    out = PROJECT_ROOT / "modules" / "media.ttl"
    g.serialize(destination=out, format="turtle")
    print(f"wrote {out} ({len(g)} triples)")
    return out


# -------------------------------------------------------------------
# Module 3 — measurement
# -------------------------------------------------------------------


def build_measurement() -> Path:
    g = Graph()
    bind_common(g)

    ont = URIRef("https://w3id.org/energy-intel/modules/measurement")
    module_header(
        g,
        ont,
        "energy-intel — measurement module",
        "CanonicalMeasurementClaim, Observation, Variable (thin), Series "
        "(thin), ClaimTemporalWindow, and the ei:references* family of "
        "resolution properties. V1 adds ei:canonicalUnit -> qudt:Unit.",
        imports=[
            URIRef("https://w3id.org/energy-intel/modules/media"),
            URIRef("http://www.w3.org/ns/dcat"),
            URIRef("http://www.w3.org/2004/02/skos/core"),
            # V1 — QUDT units subset for ei:canonicalUnit range.
            URIRef("https://w3id.org/energy-intel/imports/qudt-units-subset"),
        ],
    )

    # Classes -------------------------------------------------------
    declare_class(
        g,
        EI.CanonicalMeasurementClaim,
        "canonical measurement claim",
        "A numeric / categorical claim about an energy variable extracted "
        "from a post or podcast segment, with its source evidence, "
        "asserted value / unit / time, and (optionally) resolved references "
        "to a Variable, Series, Distribution, Dataset, Agent.",
        parents=[IAO["0000030"]],
    )

    declare_class(
        g,
        EI.Observation,
        "observation",
        "A single time-indexed numeric reading belonging to a Series. "
        "Thin in V0 (no CQs hit Observation directly).",
        parents=[IAO["0000030"]],
    )

    declare_class(
        g,
        EI.Variable,
        "variable",
        "A measurable energy quantity (e.g., 'installed solar PV capacity, "
        "United States, monthly'). Thin in V0 — the seven-facet form is "
        "deferred to V1.",
        parents=[IAO["0000030"]],
    )

    declare_class(
        g,
        EI.Series,
        "series",
        "A time-indexed sequence of Observations implementing a Variable. "
        "Thin in V0 — full seven-facet form deferred to V1.",
        parents=[IAO["0000030"]],
    )

    declare_class(
        g,
        EI.ClaimTemporalWindow,
        "claim temporal window",
        "The temporal region a CMC refers to (a single year, a range of "
        "months, an exact timestamp). Per bfo-alignment.md parented to "
        "bfo:TemporalRegion, NOT an ICE.",
        parents=[BFO["0000008"]],  # temporal region
    )

    # Disjointness --------------------------------------------------
    disjoint_classes(
        g,
        [
            EI.CanonicalMeasurementClaim,
            EI.Observation,
            EI.Variable,
            EI.Series,
            EI.ClaimTemporalWindow,
        ],
    )
    g.add((EI.CanonicalMeasurementClaim, OWL.disjointWith, EI.Observation))

    # Super-property: ei:references (aligned to IAO:is_about IAO_0000136)
    declare_object_property(
        g,
        EI.references,
        "references",
        domain=EI.CanonicalMeasurementClaim,
        range_=None,
        sub_property_of=[IAO["0000136"]],  # is about
        comment="Parent of every CMC-level resolution property.",
    )

    # Five references* properties
    declare_object_property(
        g,
        EI.referencesVariable,
        "references variable",
        domain=EI.CanonicalMeasurementClaim,
        range_=EI.Variable,
        functional=True,
        sub_property_of=[EI.references],
    )
    subclass_qcr(
        g,
        EI.CanonicalMeasurementClaim,
        EI.referencesVariable,
        EI.Variable,
        "max",
        1,
    )

    declare_object_property(
        g,
        EI.referencesSeries,
        "references series",
        domain=EI.CanonicalMeasurementClaim,
        range_=EI.Series,
        functional=True,
        sub_property_of=[EI.references],
    )
    subclass_qcr(
        g,
        EI.CanonicalMeasurementClaim,
        EI.referencesSeries,
        EI.Series,
        "max",
        1,
    )

    declare_object_property(
        g,
        EI.referencesDistribution,
        "references distribution",
        domain=EI.CanonicalMeasurementClaim,
        range_=DCAT.Distribution,
        functional=True,
        sub_property_of=[EI.references],
    )
    subclass_qcr(
        g,
        EI.CanonicalMeasurementClaim,
        EI.referencesDistribution,
        DCAT.Distribution,
        "max",
        1,
    )

    declare_object_property(
        g,
        EI.referencesDataset,
        "references dataset",
        domain=EI.CanonicalMeasurementClaim,
        range_=DCAT.Dataset,
        functional=True,
        sub_property_of=[EI.references],
    )
    subclass_qcr(
        g,
        EI.CanonicalMeasurementClaim,
        EI.referencesDataset,
        DCAT.Dataset,
        "max",
        1,
    )

    declare_object_property(
        g,
        EI.referencesAgent,
        "references agent",
        domain=EI.CanonicalMeasurementClaim,
        range_=EI.Organization,
        functional=True,
        sub_property_of=[EI.references],
    )
    subclass_qcr(
        g,
        EI.CanonicalMeasurementClaim,
        EI.referencesAgent,
        EI.Organization,
        "max",
        1,
    )

    # ei:aboutTechnology -------------------------------------------
    declare_object_property(
        g,
        EI.aboutTechnology,
        "about technology",
        domain=EI.CanonicalMeasurementClaim,
        range_=SKOS.Concept,
        comment=(
            "CMC-level technology classification. Range skos:Concept; OEO "
            "technology classes appear as punned individuals post-MIREOT "
            "(see docs/axiom-plan.md § CQ-013)."
        ),
    )

    # ei:evidences -------------------------------------------------
    declare_object_property(
        g,
        EI.evidences,
        "evidences",
        domain=EI.EvidenceSource,
        range_=EI.CanonicalMeasurementClaim,
        comment=(
            "An EvidenceSource (Post, MediaAttachment, PodcastSegment) "
            "evidences one or more CMCs extracted from it."
        ),
    )

    # CQ-009 invariant: CMC SubClassOf (inverse ei:evidences) min 1 EvidenceSource
    subclass_qcr_inverse(
        g,
        EI.CanonicalMeasurementClaim,
        EI.evidences,
        EI.EvidenceSource,
        "min",
        1,
    )

    # ei:assertedTime ----------------------------------------------
    declare_object_property(
        g,
        EI.assertedTime,
        "asserted time",
        domain=EI.CanonicalMeasurementClaim,
        range_=EI.ClaimTemporalWindow,
        functional=True,
        comment="The temporal region the CMC's value refers to.",
    )

    # ei:implementsVariable ----------------------------------------
    declare_object_property(
        g,
        EI.implementsVariable,
        "implements variable",
        domain=EI.Series,
        range_=EI.Variable,
        functional=True,
        comment=(
            "A Series implements exactly one Variable. Thin V0 relation; "
            "full seven-facet form deferred."
        ),
    )

    # ei:publishedInDataset ----------------------------------------
    declare_object_property(
        g,
        EI.publishedInDataset,
        "published in dataset",
        domain=EI.Series,
        range_=DCAT.Dataset,
        comment=(
            "A Series is published within a DCAT Dataset. Inverse of "
            "ei:hasSeries (declared in data module)."
        ),
    )

    # Data properties on CMC ---------------------------------------
    declare_data_property(
        g,
        EI.assertedValue,
        "asserted value",
        domain=EI.CanonicalMeasurementClaim,
        range_=[XSD.decimal, XSD.string],
        functional=True,
        comment=(
            "The raw asserted value of the claim, preserving either the "
            "numeric form (xsd:decimal) or the source string form (xsd:string)."
        ),
    )

    declare_data_property(
        g,
        EI.assertedUnit,
        "asserted unit",
        domain=EI.CanonicalMeasurementClaim,
        range_=XSD.string,
        functional=True,
        comment="Raw asserted unit token (e.g., 'GW', 'TWh').",
    )

    # V1 A4: ei:canonicalUnit -- functional object property linking a CMC
    # to the canonical qudt:Unit IRI its assertedUnit string resolves to.
    declare_object_property(
        g,
        EI.canonicalUnit,
        "canonical unit",
        domain=EI.CanonicalMeasurementClaim,
        range_=QUDT.Unit,
        functional=True,
        comment=(
            "Links a CanonicalMeasurementClaim to the canonical qudt:Unit IRI "
            "that the claim's surface-form ei:assertedUnit string resolves to. "
            "Functional: a CMC has at most one canonical unit."
        ),
    )
    # V1 A5: CMC SubClassOf (canonicalUnit max 1 qudt:Unit). Although the
    # property is Functional (max-1 globally), the qualified-cardinality
    # restriction makes the resolution-grain invariant explicit at the CMC
    # level and lines up with the existing references* restrictions.
    subclass_qcr(
        g,
        EI.CanonicalMeasurementClaim,
        EI.canonicalUnit,
        QUDT.Unit,
        "max",
        1,
    )

    # ei:intervalStart / ei:intervalEnd (on ClaimTemporalWindow)
    declare_data_property(
        g,
        EI.intervalStart,
        "interval start",
        domain=EI.ClaimTemporalWindow,
        range_=XSD.dateTime,
        functional=True,
    )
    declare_data_property(
        g,
        EI.intervalEnd,
        "interval end",
        domain=EI.ClaimTemporalWindow,
        range_=XSD.dateTime,
        functional=True,
    )

    # Raw provenance properties on CMC -----------------------------
    declare_data_property(
        g,
        EI.rawLabel,
        "raw label",
        domain=EI.CanonicalMeasurementClaim,
        range_=XSD.string,
        functional=True,
        comment="Verbatim surface-form label captured at extraction time.",
    )
    declare_data_property(
        g,
        EI.rawDims,
        "raw dimensions",
        domain=EI.CanonicalMeasurementClaim,
        range_=XSD.string,
        functional=True,
        comment=(
            "JSON-encoded dictionary of free-form dimensional annotations "
            "from the extractor (e.g., region, subsector). Parseability "
            "validated by SHACL shape S-2."
        ),
    )

    out = PROJECT_ROOT / "modules" / "measurement.ttl"
    g.serialize(destination=out, format="turtle")
    print(f"wrote {out} ({len(g)} triples)")
    return out


# -------------------------------------------------------------------
# Module 4 — data (DCAT extension)
# -------------------------------------------------------------------


def build_data() -> Path:
    g = Graph()
    bind_common(g)

    ont = URIRef("https://w3id.org/energy-intel/modules/data")
    module_header(
        g,
        ont,
        "energy-intel — data module",
        "DCAT 3 extension: ei:hasSeries (Dataset → Series) and the inverse "
        "declaration of ei:publishedInDataset. No local DCAT subclasses.",
        imports=[
            URIRef("https://w3id.org/energy-intel/modules/measurement"),
            URIRef("http://www.w3.org/ns/dcat"),
        ],
    )

    declare_object_property(
        g,
        EI.hasSeries,
        "has series",
        domain=DCAT.Dataset,
        range_=EI.Series,
        comment=(
            "Extension property: a DCAT Dataset exposes one or more "
            "energy-intel Series. Inverse of ei:publishedInDataset."
        ),
    )
    g.add((EI.hasSeries, OWL.inverseOf, EI.publishedInDataset))

    out = PROJECT_ROOT / "modules" / "data.ttl"
    g.serialize(destination=out, format="turtle")
    print(f"wrote {out} ({len(g)} triples)")
    return out


# -------------------------------------------------------------------
# Top-level energy-intel.ttl
# -------------------------------------------------------------------


def build_top_level() -> Path:
    g = Graph()
    bind_common(g)

    ont = URIRef("https://w3id.org/energy-intel/energy-intel")
    module_header(
        g,
        ont,
        "energy-intel — top-level ontology",
        "Top-level energy-intel ontology. Imports the four authored modules "
        "(agent, media, measurement, data), the hand-seeded SKOS schemes, "
        "and the declared external ontologies (V1 adds three: BFO+RO-stripped "
        "OEO technology / carrier subsets and a narrow QUDT 2.1 unit subset).",
        imports=[
            # Four authored modules
            URIRef("https://w3id.org/energy-intel/modules/agent"),
            URIRef("https://w3id.org/energy-intel/modules/media"),
            URIRef("https://w3id.org/energy-intel/modules/measurement"),
            URIRef("https://w3id.org/energy-intel/modules/data"),
            # Hand-seeded SKOS schemes
            URIRef("https://w3id.org/energy-intel/modules/concept-schemes/temporal-resolution"),
            URIRef("https://w3id.org/energy-intel/modules/concept-schemes/aggregation-type"),
            URIRef("https://w3id.org/energy-intel/modules/concept-schemes/technology-seeds"),
            # External (full imports)
            URIRef("http://purl.obolibrary.org/obo/bfo.owl"),
            URIRef("http://purl.obolibrary.org/obo/iao.owl"),
            URIRef("http://www.w3.org/ns/dcat"),
            URIRef("http://www.w3.org/ns/prov-o"),
            URIRef("http://www.w3.org/2004/02/skos/core"),
            URIRef("http://xmlns.com/foaf/0.1/"),
            URIRef("http://purl.org/dc/terms/"),
            # V1 imports (per imports-manifest-v1.yaml).
            URIRef("https://w3id.org/energy-intel/imports/oeo-technology-subset"),
            URIRef("https://w3id.org/energy-intel/imports/oeo-carrier-subset"),
            URIRef("https://w3id.org/energy-intel/imports/qudt-units-subset"),
        ],
    )
    g.add((ont, OWL.versionIRI, URIRef(V1_TOP_VERSION_IRI)))

    out = PROJECT_ROOT / "energy-intel.ttl"
    g.serialize(destination=out, format="turtle")
    print(f"wrote {out} ({len(g)} triples)")
    return out


def main() -> None:
    print("--- agent module ---")
    build_agent()
    print("--- media module ---")
    build_media()
    print("--- measurement module ---")
    build_measurement()
    print("--- data module ---")
    build_data()
    print("--- top-level ---")
    build_top_level()


if __name__ == "__main__":
    main()
