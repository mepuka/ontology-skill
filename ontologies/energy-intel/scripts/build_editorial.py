# ruff: noqa: E501, SLF001
"""V2 editorial-extension build script (programmatic, rdflib-based).

Produces all V2 architect deliverables in one pass per
docs/conceptualizer-to-architect-handoff-v2.md and docs/axiom-plan-v2.md:

- modules/editorial.ttl
- modules/concept-schemes/argument-pattern.ttl   (7 SKOS Concepts)
- modules/concept-schemes/narrative-role.ttl     (4 SKOS Concepts)
- modules/concept-schemes/oeo-topics.ttl         (3 schemes + 19 supplements)
- shapes/editorial.ttl                           (S-V2-1..S-V2-4 SHACL shapes)
- tests/fixtures/cq-editorial-{N1..N8,T1,T2,granularity}.ttl

E501 is suppressed for this file because the EDITORIAL_SUPPLEMENTS data
table and SHACL SPARQL string literals are deliberately long for
readability. SLF001 is suppressed because rdflib's SH namespace exposes
the namespace base via the conventional `SH._NS` private accessor.

Run via: uv run python ontologies/energy-intel/scripts/build_editorial.py
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, FOAF, OWL, RDF, RDFS, SH, SKOS, XSD

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
CONCEPT_SCHEMES_DIR = MODULES_DIR / "concept-schemes"
SHAPES_DIR = PROJECT_ROOT / "shapes"
TESTS_DIR = PROJECT_ROOT / "tests"
FIXTURES_DIR = TESTS_DIR / "fixtures"

EI = Namespace("https://w3id.org/energy-intel/")
NROLE = Namespace("https://w3id.org/energy-intel/concept/narrative-role/")
APAT = Namespace("https://w3id.org/energy-intel/concept/argument-pattern/")
EICONCEPT = Namespace("https://w3id.org/energy-intel/concept/")
OEO = Namespace("https://openenergyplatform.org/ontology/oeo/")
IAO = Namespace("http://purl.obolibrary.org/obo/IAO_")
BFO = Namespace("http://purl.obolibrary.org/obo/BFO_")
PROV = Namespace("http://www.w3.org/ns/prov#")

ARG_PATTERN_SCHEME = URIRef("https://w3id.org/energy-intel/concept/argument-pattern")
NARR_ROLE_SCHEME = URIRef("https://w3id.org/energy-intel/concept/narrative-role")
OEO_TOPIC_SCHEME = URIRef("https://w3id.org/energy-intel/concept/oeo-topic")
EDITORIAL_SUPP_SCHEME = URIRef("https://w3id.org/energy-intel/concept/editorial-supplement")
TOPIC_AGGREGATOR_SCHEME = URIRef("https://w3id.org/energy-intel/concept/topic")

V2_VERSION = "v2 (2026-05-04)"
V2_CREATED = "2026-05-04"


# =============================================================================
# Common header
# =============================================================================


def _bind_common(g: Graph) -> None:
    g.bind("ei", EI)
    g.bind("owl", OWL)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("skos", SKOS)
    g.bind("xsd", XSD)
    g.bind("dcterms", DCTERMS)
    g.bind("foaf", FOAF)
    g.bind("iao", IAO)
    g.bind("bfo", BFO)
    g.bind("prov", PROV)


def _add_module_header(
    g: Graph,
    iri: URIRef,
    title: str,
    description: str,
    imports: list[URIRef] | None = None,
) -> None:
    g.add((iri, RDF.type, OWL.Ontology))
    g.add((iri, DCTERMS.title, Literal(title, lang="en")))
    g.add((iri, DCTERMS.description, Literal(description, lang="en")))
    g.add((iri, DCTERMS.created, Literal(V2_CREATED, datatype=XSD.date)))
    g.add((iri, DCTERMS.modified, Literal(V2_CREATED, datatype=XSD.date)))
    g.add((iri, DCTERMS.creator, Literal("energy-intel / ontology-architect", lang="en")))
    g.add((iri, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by/4.0/")))
    g.add((iri, OWL.versionInfo, Literal(V2_VERSION)))
    for imp in imports or []:
        g.add((iri, OWL.imports, imp))


def _add_class(
    g: Graph,
    cls: URIRef,
    label: str,
    parents: list[URIRef],
    definition: str,
) -> None:
    g.add((cls, RDF.type, OWL.Class))
    g.add((cls, RDFS.label, Literal(label, lang="en")))
    g.add((cls, SKOS.definition, Literal(definition, lang="en")))
    for p in parents:
        g.add((cls, RDFS.subClassOf, p))


def _add_object_property(
    g: Graph,
    prop: URIRef,
    label: str,
    domain: URIRef,
    range_: URIRef,
    definition: str,
    *,
    functional: bool = False,
    extra_types: list[URIRef] | None = None,
) -> None:
    g.add((prop, RDF.type, OWL.ObjectProperty))
    if functional:
        g.add((prop, RDF.type, OWL.FunctionalProperty))
    for t in extra_types or []:
        g.add((prop, RDF.type, t))
    g.add((prop, RDFS.label, Literal(label, lang="en")))
    g.add((prop, RDFS.domain, domain))
    g.add((prop, RDFS.range, range_))
    g.add((prop, SKOS.definition, Literal(definition, lang="en")))


def _add_cardinality_restriction(
    g: Graph,
    cls: URIRef,
    on_property: URIRef,
    cardinality: int,
    on_class: URIRef,
    *,
    qualified: bool = True,
) -> None:
    """Add a SubClassOf qualified-cardinality restriction."""
    from rdflib import BNode

    r = BNode()
    g.add((r, RDF.type, OWL.Restriction))
    g.add((r, OWL.onProperty, on_property))
    if qualified:
        g.add((r, OWL.qualifiedCardinality, Literal(cardinality, datatype=XSD.nonNegativeInteger)))
        g.add((r, OWL.onClass, on_class))
    else:
        g.add((r, OWL.cardinality, Literal(cardinality, datatype=XSD.nonNegativeInteger)))
    g.add((cls, RDFS.subClassOf, r))


def _add_max_cardinality_restriction(
    g: Graph,
    cls: URIRef,
    on_property: URIRef,
    max_cardinality: int,
    on_class: URIRef,
) -> None:
    from rdflib import BNode

    r = BNode()
    g.add((r, RDF.type, OWL.Restriction))
    g.add((r, OWL.onProperty, on_property))
    g.add(
        (r, OWL.maxQualifiedCardinality, Literal(max_cardinality, datatype=XSD.nonNegativeInteger))
    )
    g.add((r, OWL.onClass, on_class))
    g.add((cls, RDFS.subClassOf, r))


# =============================================================================
# 1. modules/editorial.ttl
# =============================================================================


def build_editorial_module() -> Path:
    g = Graph()
    _bind_common(g)

    iri = URIRef("https://w3id.org/energy-intel/modules/editorial")
    _add_module_header(
        g,
        iri,
        title="energy-intel — editorial module",
        description=(
            "V2 editorial extension. Declares ei:Narrative and "
            "ei:NarrativePostMembership classes (both ⊑ iao:Document) and "
            "the six object properties that compose the editorial graph: "
            "hasNarrativePostMembership, memberPost, memberRole, "
            "narrativeMentionsExpert, narrativeAppliesPattern, "
            "narrativeAboutTopic. NarrativePostMembership is a reified "
            "n-ary relation per source plan §3.3 / multi-agent BFO/OEO "
            "modeling review (avoids System Blueprint anti-pattern from "
            "role-named predicates)."
        ),
        imports=[
            URIRef("http://purl.obolibrary.org/obo/iao.owl"),
            URIRef("https://w3id.org/energy-intel/modules/agent"),
            URIRef("https://w3id.org/energy-intel/modules/media"),
        ],
    )

    # A1 — Narrative class
    _add_class(
        g,
        EI.Narrative,
        "narrative",
        [IAO["0000310"]],
        (
            "A written editorial unit about energy-domain events that have "
            "been curated by an editor. A Narrative groups posts that share "
            "an editorial through-line (a single argument or question) and "
            "applies an argument pattern to frame the discussion. "
            "Identified by a deterministic IRI derived from the story stem; "
            "the directory hierarchy on disk does not enter the IRI."
        ),
    )

    # A2 — NarrativePostMembership class
    _add_class(
        g,
        EI.NarrativePostMembership,
        "narrative post membership",
        [IAO["0000310"]],
        (
            "An information artefact recording that a Narrative includes a "
            "Post in a specific role (lead, supporting, counter, or "
            "context). One individual per (Narrative, Post) pair. "
            "Identified by a deterministic IRI = "
            "{narrativeIri}/membership/{sha256(narrativeIri \\n postUri)[0:16]}. "
            "Reified rather than four role-named predicates because "
            "role-named predicates would smuggle storage state into "
            "predicate names (System Blueprint anti-pattern), would not "
            "absorb future first-class qualifier storage cleanly, and "
            "would block the SHACL closed-shape invariant "
            "sh:qualifiedMaxCount 1 per (Narrative, Post)."
        ),
    )

    # A3 — DisjointClasses (defense-in-depth)
    from rdflib import BNode
    from rdflib.collection import Collection

    bn = BNode()
    g.add((bn, RDF.type, OWL.AllDisjointClasses))
    members_list = BNode()
    Collection(
        g,
        members_list,
        [
            EI.Narrative,
            EI.Post,
            EI.PodcastEpisode,
            EI.NarrativePostMembership,
        ],
    )
    g.add((bn, OWL.members, members_list))

    # A4 — hasNarrativePostMembership
    _add_object_property(
        g,
        EI.hasNarrativePostMembership,
        "has narrative-post membership",
        EI.Narrative,
        EI.NarrativePostMembership,
        (
            "Links a Narrative to a NarrativePostMembership record. A "
            "Narrative has zero or more memberships, one per post it "
            "includes. Order is not preserved; cardinality `many`. The "
            "closed-shape invariant sh:qualifiedMaxCount 1 per "
            "(Narrative, Post) pair is enforced via SHACL "
            "ei:NarrativePostMembershipShape."
        ),
    )

    # A5 — memberPost (Functional)
    _add_object_property(
        g,
        EI.memberPost,
        "member post",
        EI.NarrativePostMembership,
        EI.Post,
        (
            "Functional pointer from a NarrativePostMembership to the Post "
            "it references. Each membership has exactly one post."
        ),
        functional=True,
    )

    # A6 — memberRole (Functional)
    _add_object_property(
        g,
        EI.memberRole,
        "member role",
        EI.NarrativePostMembership,
        SKOS.Concept,
        (
            "Functional role qualifier of a NarrativePostMembership. "
            "Constrained at the SHACL layer to values in the "
            "ei:concept/narrative-role scheme (lead, supporting, counter, "
            "context). Each membership has exactly one role."
        ),
        functional=True,
    )

    # A7 — Cardinality restriction on NarrativePostMembership for memberPost
    _add_cardinality_restriction(
        g,
        EI.NarrativePostMembership,
        EI.memberPost,
        cardinality=1,
        on_class=EI.Post,
    )

    # A8 — Cardinality restriction on NarrativePostMembership for memberRole
    _add_cardinality_restriction(
        g,
        EI.NarrativePostMembership,
        EI.memberRole,
        cardinality=1,
        on_class=SKOS.Concept,
    )

    # A9 — narrativeMentionsExpert
    _add_object_property(
        g,
        EI.narrativeMentionsExpert,
        "narrative mentions expert",
        EI.Narrative,
        FOAF.Person,
        (
            "Links a Narrative to an Expert mentioned in it. Auto-derived "
            "from contained posts at import time by walking "
            "hasNarrativePostMembership/memberPost/authoredBy. The fallback "
            "walk in CQ-N6 covers the case where auto-derivation has not "
            "run."
        ),
    )

    # A10 — narrativeAppliesPattern
    _add_object_property(
        g,
        EI.narrativeAppliesPattern,
        "narrative applies pattern",
        EI.Narrative,
        SKOS.Concept,
        (
            "Optional pointer from a Narrative to the argument pattern it "
            "applies. Range is broad skos:Concept; SHACL constrains the "
            "value to be a member of ei:concept/argument-pattern."
        ),
    )

    # A11 — narrativeAboutTopic
    _add_object_property(
        g,
        EI.narrativeAboutTopic,
        "narrative about topic",
        EI.Narrative,
        OWL.Thing,
        (
            "Links a Narrative to one or more topics. Topic IRIs are "
            "either OEO class IRIs (admitted via OWL 2 punning) or "
            "Skygest editorial supplement IRIs in the ei:concept/ "
            "namespace. SHACL granularity contract forbids bare "
            "owl:NamedIndividual values."
        ),
    )

    # A12 — Max-cardinality on Narrative for narrativeAppliesPattern
    _add_max_cardinality_restriction(
        g,
        EI.Narrative,
        EI.narrativeAppliesPattern,
        max_cardinality=1,
        on_class=SKOS.Concept,
    )

    output = MODULES_DIR / "editorial.ttl"
    g.serialize(output, format="turtle")
    print(f"  wrote {output} ({len(g):,} triples)")
    return output


# =============================================================================
# 2. modules/concept-schemes/argument-pattern.ttl
# =============================================================================


ARGUMENT_PATTERNS = [
    {
        "stem": "deployment-milestone",
        "label": "deployment milestone",
        "definition": (
            "Expert or institution posts new deployment figures — record "
            "capacity additions, market share thresholds, or cumulative "
            "installation milestones — to argue about the pace and scale "
            "of the energy transition. The editorial act is framing: "
            "which comparison metric the poster uses to contextualize "
            "the raw number."
        ),
        "variants": [
            "annual record",
            "market share threshold",
            "displacement comparison",
            "geopolitical framing",
        ],
        "status": "active",
    },
    {
        "stem": "emergent-technology-bulletin",
        "label": "emergent technology bulletin",
        "definition": (
            "New technology entering production. Signals not stories: "
            "an editorial flag that a previously-research-stage technology "
            "is reaching commercialization."
        ),
        "variants": [],
        "status": "active",
    },
    {
        "stem": "geographic-energy-project",
        "label": "geographic energy project",
        "definition": (
            "Specific projects defined by location and physical "
            "parameters. Editorial framing typically emphasizes the "
            "geographic context, local economy, or grid-integration "
            "specifics."
        ),
        "variants": [],
        "status": "active",
    },
    {
        "stem": "grid-snapshot",
        "label": "grid snapshot",
        "definition": (
            "Short-term generation/price data used to make structural "
            "points. The editor extracts a representative slice of "
            "spot-market data and uses it to argue about a longer-running "
            "structural condition."
        ),
        "variants": ["spot market analysis"],
        "status": "active",
    },
    {
        "stem": "learning-curve",
        "label": "learning curve",
        "definition": (
            "Decades-long cost or deployment curves arguing inevitability. "
            "Editorial framing emphasizes the historical trajectory as "
            "evidence for future trends."
        ),
        "variants": ["historical trend"],
        "status": "active",
    },
    {
        "stem": "methodological-critique",
        "label": "methodological critique",
        "definition": (
            "Revealing how measurement/accounting choices shape political "
            "narratives. The editorial act is to surface that a debate "
            "hinges on methodology, not just ideology."
        ),
        "variants": [],
        "status": "active",
    },
    {
        "stem": "structural-economic-analysis",
        "label": "structural economic analysis",
        "definition": (
            "Institutional data dissecting market mechanisms or policy. "
            "Editorial framing typically draws on utility planning "
            "documents, regulatory filings, or other primary economic "
            "sources to argue about underlying structural dynamics."
        ),
        "variants": [],
        "status": "active",
    },
]


def build_argument_pattern_scheme() -> Path:
    g = Graph()
    _bind_common(g)
    g.bind("apat", APAT)

    iri = URIRef("https://w3id.org/energy-intel/modules/concept-schemes/argument-pattern")
    _add_module_header(
        g,
        iri,
        title="energy-intel — Argument Pattern ConceptScheme",
        description=(
            "V2 SKOS ConceptScheme declaring the 7 stable argument "
            "patterns used by skygest-editorial to frame energy-domain "
            "narratives. Replaces the prior owl:Class + ABoxed individuals "
            "modeling per source plan §S4 / multi-agent design review. "
            "Adding a pattern is an ontology PR, not a runtime mutation."
        ),
    )

    # ConceptScheme
    g.add((ARG_PATTERN_SCHEME, RDF.type, SKOS.ConceptScheme))
    g.add((ARG_PATTERN_SCHEME, RDF.type, OWL.NamedIndividual))
    g.add((ARG_PATTERN_SCHEME, RDFS.label, Literal("argument pattern", lang="en")))
    g.add((ARG_PATTERN_SCHEME, SKOS.prefLabel, Literal("argument pattern", lang="en")))
    g.add(
        (
            ARG_PATTERN_SCHEME,
            SKOS.definition,
            Literal(
                "Controlled vocabulary of stable argument patterns the "
                "editorial pipeline uses to frame how an expert is using "
                "data to make a point. Each pattern's reference doc lives "
                "at /skygest-editorial/references/argument-patterns/{stem}.md.",
                lang="en",
            ),
        )
    )

    pattern_iris = []
    for pat in ARGUMENT_PATTERNS:
        iri_pat = URIRef(APAT[pat["stem"]])
        pattern_iris.append(iri_pat)
        g.add((iri_pat, RDF.type, SKOS.Concept))
        g.add((iri_pat, RDF.type, OWL.NamedIndividual))
        g.add((iri_pat, RDFS.label, Literal(pat["label"], lang="en")))
        g.add((iri_pat, SKOS.prefLabel, Literal(pat["label"], lang="en")))
        g.add((iri_pat, SKOS.definition, Literal(pat["definition"], lang="en")))
        g.add((iri_pat, SKOS.inScheme, ARG_PATTERN_SCHEME))
        g.add((iri_pat, SKOS.topConceptOf, ARG_PATTERN_SCHEME))
        g.add((ARG_PATTERN_SCHEME, SKOS.hasTopConcept, iri_pat))
        for variant in pat["variants"]:
            g.add((iri_pat, SKOS.altLabel, Literal(variant, lang="en")))
        g.add((iri_pat, SKOS.editorialNote, Literal(f"status: {pat['status']}", lang="en")))

    output = CONCEPT_SCHEMES_DIR / "argument-pattern.ttl"
    g.serialize(output, format="turtle")
    print(f"  wrote {output} ({len(g):,} triples)")
    return output


# =============================================================================
# 3. modules/concept-schemes/narrative-role.ttl
# =============================================================================


NARRATIVE_ROLES = [
    {
        "stem": "lead",
        "label": "lead",
        "definition": (
            "The primary post the Narrative is built around. Typically the "
            "post that gives the Narrative its headline data point or "
            "argument. At most one lead per Narrative under SHACL S-V2-4 "
            "(warning, not violation)."
        ),
    },
    {
        "stem": "supporting",
        "label": "supporting",
        "definition": (
            "A post that reinforces the Narrative's argument with "
            "additional evidence, parallel data, or corroborating analysis."
        ),
    },
    {
        "stem": "counter",
        "label": "counter",
        "definition": (
            "A post that represents an opposing or alternative view to "
            "the Narrative's main argument. Editorial value: surfacing "
            "the disagreement is part of how the Narrative frames the "
            "debate."
        ),
    },
    {
        "stem": "context",
        "label": "context",
        "definition": (
            "A post that provides background information that helps the "
            "reader understand the Narrative — historical context, "
            "definitions, prior events — without itself being the central "
            "claim."
        ),
    },
]


def build_narrative_role_scheme() -> Path:
    g = Graph()
    _bind_common(g)
    g.bind("nrole", NROLE)

    iri = URIRef("https://w3id.org/energy-intel/modules/concept-schemes/narrative-role")
    _add_module_header(
        g,
        iri,
        title="energy-intel — Narrative Role ConceptScheme",
        description=(
            "V2 SKOS ConceptScheme declaring the 4 stable narrative-role "
            "concepts used as values of ei:memberRole on "
            "ei:NarrativePostMembership. Closed enumeration per source "
            "plan §3.3."
        ),
    )

    g.add((NARR_ROLE_SCHEME, RDF.type, SKOS.ConceptScheme))
    g.add((NARR_ROLE_SCHEME, RDF.type, OWL.NamedIndividual))
    g.add((NARR_ROLE_SCHEME, RDFS.label, Literal("narrative role", lang="en")))
    g.add((NARR_ROLE_SCHEME, SKOS.prefLabel, Literal("narrative role", lang="en")))
    g.add(
        (
            NARR_ROLE_SCHEME,
            SKOS.definition,
            Literal(
                "Closed enumeration of role qualifiers a Post can play in "
                "a Narrative: lead, supporting, counter, context.",
                lang="en",
            ),
        )
    )

    for role in NARRATIVE_ROLES:
        iri_role = URIRef(NROLE[role["stem"]])
        g.add((iri_role, RDF.type, SKOS.Concept))
        g.add((iri_role, RDF.type, OWL.NamedIndividual))
        g.add((iri_role, RDFS.label, Literal(role["label"], lang="en")))
        g.add((iri_role, SKOS.prefLabel, Literal(role["label"], lang="en")))
        g.add((iri_role, SKOS.definition, Literal(role["definition"], lang="en")))
        g.add((iri_role, SKOS.inScheme, NARR_ROLE_SCHEME))
        g.add((iri_role, SKOS.topConceptOf, NARR_ROLE_SCHEME))
        g.add((NARR_ROLE_SCHEME, SKOS.hasTopConcept, iri_role))

    output = CONCEPT_SCHEMES_DIR / "narrative-role.ttl"
    g.serialize(output, format="turtle")
    print(f"  wrote {output} ({len(g):,} triples)")
    return output


# =============================================================================
# 4. modules/concept-schemes/oeo-topics.ttl
# =============================================================================


# Editorial supplements — 19 total per [conceptual-model-v2.md § 11 finding 3]
# Format: (slug, label, definition, optional [oeo close/exact match leaves])
EDITORIAL_SUPPLEMENTS = [
    (
        "data-center-demand",
        "data center demand",
        "Editorial umbrella for narratives about data center energy consumption and grid impact, including AI-workload framing.",
        ["OEO_00310000"],
    ),
    (
        "distributed-energy",
        "distributed energy",
        "Editorial umbrella for distributed energy resources (DERs), demand-response, microgrids, and virtual power plants.",
        [],
    ),
    (
        "grid-and-infrastructure",
        "grid and infrastructure",
        "Editorial umbrella for transmission, distribution, interconnection, and grid operations.",
        ["OEO_00000143", "OEO_00110019", "OEO_00110020"],
    ),
    (
        "electrification",
        "electrification",
        "Editorial umbrella for transport, building, and end-use electrification.",
        ["OEO_00000146", "OEO_00000212"],
    ),
    (
        "energy-efficiency",
        "energy efficiency",
        "Editorial umbrella for efficiency retrofits, demand reduction, and performance gains. OEO_00140049 (energy conversion efficiency) is too narrow.",
        [],
    ),
    (
        "energy-policy",
        "energy policy",
        "Editorial umbrella for energy policy, regulation, permitting, and government strategy.",
        ["OEO_00140150", "OEO_00140151"],
    ),
    (
        "energy-markets",
        "energy markets",
        "Editorial umbrella for power, fuel, and wholesale market structure and pricing.",
        ["OEO_00020065", "OEO_00020069"],
    ),
    (
        "energy-finance",
        "energy finance",
        "Editorial umbrella for project finance, M&A, public funding, and clean-tech capital.",
        [],
    ),
    (
        "energy-geopolitics",
        "energy geopolitics",
        "Editorial umbrella for energy security, sanctions, trade, and supply-chain strategy.",
        [],
    ),
    (
        "critical-minerals",
        "critical minerals",
        "Editorial umbrella for critical-mineral extraction, processing, and market competition. Narrows OEO's bare 'mineral' to lithium / cobalt / rare-earth scope.",
        ["OEO_00240030"],
    ),
    (
        "climate-and-emissions",
        "climate and emissions",
        "Editorial umbrella for climate policy outcomes, emissions tracking, and net-zero commitments.",
        ["OEO_00000020", "OEO_00000199"],
    ),
    (
        "carbon-markets",
        "carbon markets",
        "Editorial umbrella for carbon-credit and emissions-trading markets.",
        ["OEO_00020075", "OEO_00020063"],
    ),
    (
        "environment-and-land-use",
        "environment and land use",
        "Editorial umbrella for land use, environmental review, water, and pollution impacts. OEO land-use sector NamedIndividuals dropped per granularity contract.",
        [],
    ),
    (
        "energy-justice",
        "energy justice",
        "Editorial umbrella for affordability, access, community energy, and just-transition concerns.",
        [],
    ),
    (
        "sectoral-decarbonization",
        "sectoral decarbonization",
        "Editorial umbrella for industrial, aviation, maritime, and cross-sector decarbonization pathways.",
        ["OEO_00010212"],
    ),
    (
        "workforce-and-manufacturing",
        "workforce and manufacturing",
        "Editorial umbrella for energy jobs, industrial buildout, and manufacturing capacity.",
        ["OEO_00010485", "OEO_00050000"],
    ),
    (
        "research-and-innovation",
        "research and innovation",
        "Editorial umbrella for R&D, patents, and early-stage energy technology breakthroughs.",
        [],
    ),
    (
        "energy-storage",
        "energy storage",
        "Editorial umbrella for energy storage, broader than OEO_00020366 (technology only) — covers markets, policy, geopolitics of storage.",
        ["OEO_00020366", "OEO_00010438"],
    ),
    (
        "biomass",
        "biomass (editorial umbrella)",
        "Editorial umbrella for biomass and bioenergy, broader than OEO_00010258/_00010214 alone — covers materials, conversion, and sustainability debates. Label disambiguated from OEO_00010214 (biomass material) and OEO_00010258 (bioenergy).",
        ["OEO_00010258", "OEO_00010214"],
    ),
]

# OEO IRIs accepted as runtime topic catalog members per topic-vocabulary-mapping.md
# (the same 41 IRIs verified clean against oeo-full.owl)
OEO_TOPIC_IRIS = [
    "OEO_00000020",
    "OEO_00000088",
    "OEO_00000115",
    "OEO_00000143",
    "OEO_00000146",
    "OEO_00000191",
    "OEO_00000199",
    "OEO_00000212",
    "OEO_00000220",
    "OEO_00000292",
    "OEO_00000384",
    "OEO_00000446",
    "OEO_00010138",
    "OEO_00010139",
    "OEO_00010141",
    "OEO_00010212",
    "OEO_00010214",
    "OEO_00010258",
    "OEO_00010424",
    "OEO_00010426",
    "OEO_00010427",
    "OEO_00010428",
    "OEO_00010430",
    "OEO_00010431",
    "OEO_00010438",
    "OEO_00010439",
    "OEO_00010455",
    "OEO_00010485",
    "OEO_00020063",
    "OEO_00020065",
    "OEO_00020069",
    "OEO_00020075",
    "OEO_00020366",
    "OEO_00050000",
    "OEO_00110019",
    "OEO_00110020",
    "OEO_00140049",
    "OEO_00140150",
    "OEO_00140151",
    "OEO_00240030",
    "OEO_00310000",
]

# Legacy slug → canonical IRI(s) for skos:notation (signal preservation
# per topic-vocabulary-mapping.md § 5). Notation is the V1 conceptToCanonicalTopicSlug
# key, lower-camel-cased.
LEGACY_SLUGS_TO_CANONICAL = {
    # umbrella slugs ↔ canonical IRI (single-IRI cases)
    "carbon-capture": ["OEO_00010138"],  # OEO is the umbrella
    "coal": ["OEO_00000088"],
    "geothermal": ["OEO_00010430", "OEO_00000191"],
    "hydro": ["OEO_00010431", "OEO_00010438"],
    "hydrogen": ["OEO_00000220"],
    "natural-gas": ["OEO_00000292"],
    "nuclear": ["OEO_00010439"],
    "offshore-wind": ["OEO_00010426"],
    "oil": ["OEO_00000115"],
    "solar": ["OEO_00010427", "OEO_00000384", "OEO_00010428"],
    "wind": ["OEO_00010424", "OEO_00000446"],
}

# Editorial supplement slugs map to their own IRI (slug = stem)
for s in EDITORIAL_SUPPLEMENTS:
    LEGACY_SLUGS_TO_CANONICAL[s[0]] = [None]  # marker; resolved below


def build_oeo_topics_scheme() -> Path:
    g = Graph()
    _bind_common(g)
    g.bind("oeo", OEO)

    iri = URIRef("https://w3id.org/energy-intel/modules/concept-schemes/oeo-topics")
    _add_module_header(
        g,
        iri,
        title="energy-intel — OEO topics + editorial supplement ConceptSchemes",
        description=(
            "V2 SKOS ConceptScheme module declaring the runtime topic "
            "catalog. Per V2-CQ-Q-1 (split + aggregator decision in "
            "conceptual-model-v2.md § 4), this module declares 3 schemes: "
            "ei:concept/oeo-topic (OEO IRIs admitted via punning), "
            "ei:concept/editorial-supplement (Skygest-coined umbrella "
            "concepts), and ei:concept/topic (aggregator). 19 supplement "
            "IRIs declared with skos:notation carrying legacy slug for "
            "migration. 41 OEO IRIs admitted via skos:inScheme + "
            "skos:topConceptOf assertions."
        ),
        imports=[
            URIRef("https://w3id.org/energy-intel/imports/oeo-topic-subset"),
        ],
    )

    # ----- 3 ConceptSchemes -----
    for scheme, label, defn in [
        (
            OEO_TOPIC_SCHEME,
            "OEO topic",
            "OEO classes admitted as runtime topic catalog members. Each member is an OEO class IRI, admitted as a skos:Concept individual via OWL 2 punning.",
        ),
        (
            EDITORIAL_SUPP_SCHEME,
            "editorial supplement topic",
            "Skygest-coined umbrella topic concepts. Each member is a skos:Concept individual in the https://w3id.org/energy-intel/concept/ namespace, carrying a skos:notation with the legacy editorial topic_slug.",
        ),
        (
            TOPIC_AGGREGATOR_SCHEME,
            "energy topic (aggregator)",
            "Aggregator scheme over ei:concept/oeo-topic and ei:concept/editorial-supplement. Runtime queries (CQ-N4) target this scheme.",
        ),
    ]:
        g.add((scheme, RDF.type, SKOS.ConceptScheme))
        g.add((scheme, RDF.type, OWL.NamedIndividual))
        g.add((scheme, RDFS.label, Literal(label, lang="en")))
        g.add((scheme, SKOS.prefLabel, Literal(label, lang="en")))
        g.add((scheme, SKOS.definition, Literal(defn, lang="en")))

    # ----- OEO IRIs admitted to oeo-topic + topic aggregator -----
    for code in OEO_TOPIC_IRIS:
        oeo_iri = URIRef(OEO[code])
        g.add((oeo_iri, SKOS.inScheme, OEO_TOPIC_SCHEME))
        g.add((oeo_iri, SKOS.inScheme, TOPIC_AGGREGATOR_SCHEME))
        # Don't declare topConcept here — let the aggregator/sub-scheme
        # handle their own top concepts; OEO IRIs participate as
        # concepts but are not necessarily top concepts.

    # ----- 19 supplements -----
    for slug, label, defn, oeo_close in EDITORIAL_SUPPLEMENTS:
        supp_iri = URIRef(EICONCEPT[slug])
        g.add((supp_iri, RDF.type, SKOS.Concept))
        g.add((supp_iri, RDF.type, OWL.NamedIndividual))
        g.add((supp_iri, RDFS.label, Literal(label, lang="en")))
        g.add((supp_iri, SKOS.prefLabel, Literal(label, lang="en")))
        g.add((supp_iri, SKOS.definition, Literal(defn, lang="en")))
        g.add((supp_iri, SKOS.inScheme, EDITORIAL_SUPP_SCHEME))
        g.add((supp_iri, SKOS.inScheme, TOPIC_AGGREGATOR_SCHEME))
        g.add((supp_iri, SKOS.topConceptOf, EDITORIAL_SUPP_SCHEME))
        g.add((EDITORIAL_SUPP_SCHEME, SKOS.hasTopConcept, supp_iri))
        g.add((supp_iri, SKOS.notation, Literal(slug)))
        for oeo_code in oeo_close:
            g.add((supp_iri, SKOS.closeMatch, URIRef(OEO[oeo_code])))

    # ----- Legacy slug → IRI notations for OEO-fit umbrellas -----
    # These 11 slugs are V1 canonicalTopicOrder umbrellas that resolve
    # cleanly to OEO IRIs (no Skygest supplement minted). Carry the slug
    # as skos:notation on each OEO IRI so CQ-T2 can resolve.
    for slug, oeo_codes in LEGACY_SLUGS_TO_CANONICAL.items():
        for oeo_code in oeo_codes:
            if oeo_code is None:
                continue  # Skygest supplement; notation already added above
            target_iri = URIRef(OEO[oeo_code])
            g.add((target_iri, SKOS.notation, Literal(slug)))

    output = CONCEPT_SCHEMES_DIR / "oeo-topics.ttl"
    g.serialize(output, format="turtle")
    print(f"  wrote {output} ({len(g):,} triples)")
    return output


# =============================================================================
# 5. shapes/editorial.ttl  (S-V2-1..S-V2-4)
# =============================================================================


def build_editorial_shapes() -> Path:
    g = Graph()
    _bind_common(g)
    g.bind("sh", SH)
    g.bind("nrole", NROLE)

    iri = URIRef("https://w3id.org/energy-intel/shapes/editorial")
    _add_module_header(
        g,
        iri,
        title="energy-intel — editorial SHACL shapes",
        description=(
            "V2 SHACL shapes for the editorial extension. Encodes 4 invariants: "
            "(S-V2-1) NarrativePostMembership uniqueness per (Narrative, Post) "
            "and memberPost / memberRole minCount + maxCount + memberRole "
            "value enumeration; "
            "(S-V2-2) narrativeAppliesPattern scheme membership "
            "(must be in ei:concept/argument-pattern); "
            "(S-V2-3) narrativeAboutTopic granularity contract "
            "(value MUST be owl:Class or skos:Concept; never bare NamedIndividual); "
            "(S-V2-4) at most one lead-role membership per Narrative (warning)."
        ),
    )

    # ---- S-V2-1 ----
    npm_shape = URIRef(EI.NarrativePostMembershipShape)
    g.add((npm_shape, RDF.type, SH.NodeShape))
    g.add((npm_shape, SH.targetClass, EI.NarrativePostMembership))

    from rdflib import BNode

    # memberPost property shape
    pp_post = BNode()
    g.add((npm_shape, SH.property, pp_post))
    g.add((pp_post, SH.path, EI.memberPost))
    g.add((pp_post, SH["class"], EI.Post))
    g.add((pp_post, SH.minCount, Literal(1)))
    g.add((pp_post, SH.maxCount, Literal(1)))
    g.add((pp_post, SH.severity, SH.Violation))
    g.add(
        (
            pp_post,
            SH.message,
            Literal(
                "memberPost: exactly 1 ei:Post required per NarrativePostMembership", lang="en"
            ),
        )
    )

    # memberRole property shape (sh:in enumeration)
    pp_role = BNode()
    g.add((npm_shape, SH.property, pp_role))
    g.add((pp_role, SH.path, EI.memberRole))
    g.add((pp_role, SH.minCount, Literal(1)))
    g.add((pp_role, SH.maxCount, Literal(1)))
    g.add((pp_role, SH.severity, SH.Violation))
    g.add(
        (
            pp_role,
            SH.message,
            Literal(
                "memberRole: exactly 1 value required, must be in ei:concept/narrative-role",
                lang="en",
            ),
        )
    )
    role_list = BNode()
    from rdflib.collection import Collection

    Collection(
        g,
        role_list,
        [
            URIRef(NROLE.lead),
            URIRef(NROLE.supporting),
            URIRef(NROLE.counter),
            URIRef(NROLE.context),
        ],
    )
    g.add((pp_role, SH["in"], role_list))

    # NarrativeUniqueMembershipShape (closed-shape per (Narrative, Post))
    narr_unique = URIRef(EI.NarrativeUniqueMembershipShape)
    g.add((narr_unique, RDF.type, SH.NodeShape))
    g.add((narr_unique, SH.targetClass, EI.Narrative))
    sparql_node = BNode()
    g.add((narr_unique, SH["sparql"], sparql_node))
    g.add((sparql_node, RDF.type, SH.SPARQLConstraint))
    g.add(
        (
            sparql_node,
            SH.select,
            Literal(
                """PREFIX ei: <https://w3id.org/energy-intel/>
SELECT $this ?post WHERE {
  $this ei:hasNarrativePostMembership ?m1 ;
        ei:hasNarrativePostMembership ?m2 .
  ?m1 ei:memberPost ?post .
  ?m2 ei:memberPost ?post .
  FILTER(?m1 != ?m2)
}"""
            ),
        )
    )
    g.add((sparql_node, SH.severity, SH.Violation))
    g.add(
        (
            sparql_node,
            SH.message,
            Literal(
                "At most one NarrativePostMembership per (Narrative, Post) pair (S-V2-1).",
                lang="en",
            ),
        )
    )

    # ---- S-V2-2 ----  narrativeAppliesPattern scheme membership
    narr_shape = URIRef(EI.NarrativeShape)
    g.add((narr_shape, RDF.type, SH.NodeShape))
    g.add((narr_shape, SH.targetClass, EI.Narrative))

    pp_pat = BNode()
    g.add((narr_shape, SH.property, pp_pat))
    g.add((pp_pat, SH.path, EI.narrativeAppliesPattern))
    g.add((pp_pat, SH.maxCount, Literal(1)))
    g.add((pp_pat, SH.nodeKind, SH.IRI))
    pat_sparql = BNode()
    g.add((pp_pat, SH["sparql"], pat_sparql))
    g.add((pat_sparql, RDF.type, SH.SPARQLConstraint))
    g.add(
        (
            pat_sparql,
            SH.select,
            Literal(
                """PREFIX ei: <https://w3id.org/energy-intel/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT $this ?value WHERE {
  $this ei:narrativeAppliesPattern ?value .
  FILTER NOT EXISTS {
    ?value skos:inScheme <https://w3id.org/energy-intel/concept/argument-pattern> .
  }
}"""
            ),
        )
    )
    g.add((pat_sparql, SH.severity, SH.Violation))
    g.add(
        (
            pat_sparql,
            SH.message,
            Literal(
                "narrativeAppliesPattern value MUST be in scheme ei:concept/argument-pattern (S-V2-2).",
                lang="en",
            ),
        )
    )

    # ---- S-V2-3 ----  narrativeAboutTopic granularity contract
    pp_topic = BNode()
    g.add((narr_shape, SH.property, pp_topic))
    g.add((pp_topic, SH.path, EI.narrativeAboutTopic))
    g.add((pp_topic, SH.nodeKind, SH.IRI))
    or_list = BNode()
    cls_node = BNode()
    g.add((cls_node, SH["class"], OWL.Class))
    concept_node = BNode()
    g.add((concept_node, SH["class"], SKOS.Concept))
    Collection(g, or_list, [cls_node, concept_node])
    g.add((pp_topic, URIRef(SH._NS + "or"), or_list))
    g.add((pp_topic, SH.severity, SH.Violation))
    g.add(
        (
            pp_topic,
            SH.message,
            Literal(
                "narrativeAboutTopic value MUST be owl:Class or skos:Concept (granularity contract S-V2-3 / CQ-T3).",
                lang="en",
            ),
        )
    )

    # ---- S-V2-4 ----  Lead-uniqueness warning
    lead_shape = URIRef(EI.NarrativeLeadUniquenessShape)
    g.add((lead_shape, RDF.type, SH.NodeShape))
    g.add((lead_shape, SH.targetClass, EI.Narrative))
    lead_sparql = BNode()
    g.add((lead_shape, SH["sparql"], lead_sparql))
    g.add((lead_sparql, RDF.type, SH.SPARQLConstraint))
    g.add(
        (
            lead_sparql,
            SH.select,
            Literal(
                """PREFIX ei: <https://w3id.org/energy-intel/>
SELECT $this WHERE {
  $this ei:hasNarrativePostMembership ?m1 ;
        ei:hasNarrativePostMembership ?m2 .
  ?m1 ei:memberRole <https://w3id.org/energy-intel/concept/narrative-role/lead> .
  ?m2 ei:memberRole <https://w3id.org/energy-intel/concept/narrative-role/lead> .
  FILTER(?m1 != ?m2)
}"""
            ),
        )
    )
    g.add((lead_sparql, SH.severity, SH.Warning))
    g.add(
        (
            lead_sparql,
            SH.message,
            Literal(
                "More than one lead-role NarrativePostMembership on this "
                "Narrative (warning, not violation — draft narratives may "
                "legitimately have multiple lead candidates) (S-V2-4).",
                lang="en",
            ),
        )
    )

    output = SHAPES_DIR / "editorial.ttl"
    SHAPES_DIR.mkdir(exist_ok=True)
    g.serialize(output, format="turtle")
    print(f"  wrote {output} ({len(g):,} triples)")
    return output


# =============================================================================
# 6. Fixtures for the 11 V2 CQ tests
# =============================================================================


# Canonical fixture story-stem and post URI for V2 tests.
# Drawn from /skygest-editorial/narratives/nuclear-economics/stories/2026-04-06-tva-nuclear-costs.md
SAMPLE_STEM = "2026-04-06-tva-nuclear-costs"
SAMPLE_NARRATIVE = URIRef(f"https://w3id.org/energy-intel/narrative/{SAMPLE_STEM}")
SAMPLE_POST = URIRef("https://id.skygest.io/post/x-1886502618-status-2039766305071378920")
SAMPLE_POST2 = URIRef("https://id.skygest.io/post/x-1886502618-status-other")
SAMPLE_EXPERT = URIRef("https://id.skygest.io/expert/did-x-1886502618")


def membership_iri(narrative_iri: URIRef, post_uri: URIRef) -> URIRef:
    """Reference implementation of the V2 deterministic membership IRI rule."""
    payload = (str(narrative_iri) + "\n" + str(post_uri)).encode("utf-8")
    hash16 = hashlib.sha256(payload).hexdigest()[:16]
    return URIRef(f"{narrative_iri}/membership/{hash16}")


def _fixture_header(g: Graph, iri: URIRef, title: str) -> None:
    """Add a minimal ontology header to a fixture file."""
    g.add((iri, RDF.type, OWL.Ontology))
    g.add((iri, DCTERMS.title, Literal(title, lang="en")))
    g.add(
        (
            iri,
            DCTERMS.description,
            Literal(
                "V2 fixture for CQ acceptance testing. Asserts the minimum "
                "ABox needed for the corresponding cq-editorial-*.sparql "
                "to return its expected result shape.",
                lang="en",
            ),
        )
    )


def _add_canonical_narrative_with_two_memberships(g: Graph) -> tuple[URIRef, URIRef, URIRef]:
    """Add a Narrative with 2 memberships (1 lead, 1 supporting) referencing 2 posts."""
    g.add((SAMPLE_NARRATIVE, RDF.type, EI.Narrative))
    g.add((SAMPLE_POST, RDF.type, EI.Post))
    g.add((SAMPLE_POST2, RDF.type, EI.Post))
    g.add(
        (SAMPLE_POST, FOAF.maker, SAMPLE_EXPERT)
    )  # Avoid using ei:authoredBy without proper Person typing
    g.add((SAMPLE_POST, EI.authoredBy, SAMPLE_EXPERT))
    g.add((SAMPLE_EXPERT, RDF.type, FOAF.Person))

    m1 = membership_iri(SAMPLE_NARRATIVE, SAMPLE_POST)
    m2 = membership_iri(SAMPLE_NARRATIVE, SAMPLE_POST2)

    g.add((SAMPLE_NARRATIVE, EI.hasNarrativePostMembership, m1))
    g.add((m1, RDF.type, EI.NarrativePostMembership))
    g.add((m1, EI.memberPost, SAMPLE_POST))
    g.add((m1, EI.memberRole, NROLE.lead))

    g.add((SAMPLE_NARRATIVE, EI.hasNarrativePostMembership, m2))
    g.add((m2, RDF.type, EI.NarrativePostMembership))
    g.add((m2, EI.memberPost, SAMPLE_POST2))
    g.add((m2, EI.memberRole, NROLE.supporting))

    return m1, m2, SAMPLE_EXPERT


def build_fixture_n1() -> Path:
    """CQ-N1: deterministic Narrative IRI lookup."""
    g = Graph()
    _bind_common(g)
    iri = URIRef(EI["fixtures/cq-editorial-N1"])
    _fixture_header(g, iri, "CQ-N1 fixture")
    g.add((SAMPLE_NARRATIVE, RDF.type, EI.Narrative))
    g.add(
        (SAMPLE_NARRATIVE, RDFS.label, Literal("TVA's 2026 IRP: nuclear at $14,235/kW", lang="en"))
    )
    output = FIXTURES_DIR / "cq-editorial-N1.ttl"
    g.serialize(output, format="turtle")
    print(f"  wrote {output}")
    return output


def build_fixture_n2() -> Path:
    """CQ-N2: forward walk Narrative → memberships → (Post, role)."""
    g = Graph()
    _bind_common(g)
    g.bind("nrole", NROLE)
    iri = URIRef(EI["fixtures/cq-editorial-N2"])
    _fixture_header(g, iri, "CQ-N2 fixture")
    _add_canonical_narrative_with_two_memberships(g)
    output = FIXTURES_DIR / "cq-editorial-N2.ttl"
    g.serialize(output, format="turtle")
    print(f"  wrote {output}")
    return output


def build_fixture_n3() -> Path:
    """CQ-N3: reverse walk Post → memberships → Narrative."""
    g = Graph()
    _bind_common(g)
    g.bind("nrole", NROLE)
    iri = URIRef(EI["fixtures/cq-editorial-N3"])
    _fixture_header(g, iri, "CQ-N3 fixture")
    _add_canonical_narrative_with_two_memberships(g)
    output = FIXTURES_DIR / "cq-editorial-N3.ttl"
    g.serialize(output, format="turtle")
    print(f"  wrote {output}")
    return output


def build_fixture_n4() -> Path:
    """CQ-N4: filter Narratives by topic (OEO IRI)."""
    g = Graph()
    _bind_common(g)
    g.bind("oeo", OEO)
    iri = URIRef(EI["fixtures/cq-editorial-N4"])
    _fixture_header(g, iri, "CQ-N4 fixture")
    g.add((SAMPLE_NARRATIVE, RDF.type, EI.Narrative))
    g.add(
        (SAMPLE_NARRATIVE, EI.narrativeAboutTopic, OEO["OEO_00010439"])
    )  # nuclear power technology
    g.add((OEO["OEO_00010439"], RDF.type, OWL.Class))
    output = FIXTURES_DIR / "cq-editorial-N4.ttl"
    g.serialize(output, format="turtle")
    print(f"  wrote {output}")
    return output


def build_fixture_n5() -> Path:
    """CQ-N5: filter Narratives by argument pattern."""
    g = Graph()
    _bind_common(g)
    g.bind("apat", APAT)
    iri = URIRef(EI["fixtures/cq-editorial-N5"])
    _fixture_header(g, iri, "CQ-N5 fixture")
    g.add((SAMPLE_NARRATIVE, RDF.type, EI.Narrative))
    g.add((SAMPLE_NARRATIVE, EI.narrativeAppliesPattern, APAT["structural-economic-analysis"]))
    g.add((APAT["structural-economic-analysis"], RDF.type, SKOS.Concept))
    g.add((APAT["structural-economic-analysis"], SKOS.inScheme, ARG_PATTERN_SCHEME))
    output = FIXTURES_DIR / "cq-editorial-N5.ttl"
    g.serialize(output, format="turtle")
    print(f"  wrote {output}")
    return output


def build_fixture_n6() -> Path:
    """CQ-N6: auto-derived expert mentions (UNION)."""
    g = Graph()
    _bind_common(g)
    g.bind("nrole", NROLE)
    iri = URIRef(EI["fixtures/cq-editorial-N6"])
    _fixture_header(g, iri, "CQ-N6 fixture")
    # Path B: walk through membership chain
    _add_canonical_narrative_with_two_memberships(g)
    # Path A: explicit ei:narrativeMentionsExpert (defense-in-depth)
    g.add((SAMPLE_NARRATIVE, EI.narrativeMentionsExpert, SAMPLE_EXPERT))
    output = FIXTURES_DIR / "cq-editorial-N6.ttl"
    g.serialize(output, format="turtle")
    print(f"  wrote {output}")
    return output


def build_fixture_n7() -> Path:
    """CQ-N7: SHACL invariant — well-formed corpus, expects 0 violations."""
    g = Graph()
    _bind_common(g)
    g.bind("nrole", NROLE)
    iri = URIRef(EI["fixtures/cq-editorial-N7"])
    _fixture_header(g, iri, "CQ-N7 fixture (well-formed: 0 violations)")
    _add_canonical_narrative_with_two_memberships(g)  # 1 lead + 1 supporting; no duplicates
    output = FIXTURES_DIR / "cq-editorial-N7.ttl"
    g.serialize(output, format="turtle")
    print(f"  wrote {output}")
    return output


def build_fixture_n8() -> Path:
    """CQ-N8: SHACL warning — well-formed corpus, expects 0 lead-conflicts."""
    g = Graph()
    _bind_common(g)
    g.bind("nrole", NROLE)
    iri = URIRef(EI["fixtures/cq-editorial-N8"])
    _fixture_header(g, iri, "CQ-N8 fixture (well-formed: single lead)")
    _add_canonical_narrative_with_two_memberships(g)  # 1 lead only
    output = FIXTURES_DIR / "cq-editorial-N8.ttl"
    g.serialize(output, format="turtle")
    print(f"  wrote {output}")
    return output


def build_fixture_t1() -> Path:
    """CQ-T1: topic-metadata lookup by IRI (OEO leaf)."""
    g = Graph()
    _bind_common(g)
    g.bind("oeo", OEO)
    iri = URIRef(EI["fixtures/cq-editorial-T1"])
    _fixture_header(g, iri, "CQ-T1 fixture")
    target = OEO["OEO_00010427"]  # solar power technology
    g.add((target, RDF.type, OWL.Class))
    g.add((target, SKOS.prefLabel, Literal("solar power technology", lang="en")))
    g.add((target, SKOS.broader, OEO["OEO_00020267"]))  # parent in OEO subtree
    g.add((target, SKOS.narrower, OEO["OEO_00010428"]))  # photovoltaic
    g.add((target, SKOS.altLabel, Literal("solar generation technology", lang="en")))
    output = FIXTURES_DIR / "cq-editorial-T1.ttl"
    g.serialize(output, format="turtle")
    print(f"  wrote {output}")
    return output


def build_fixture_t2() -> Path:
    """CQ-T2: legacy slug → canonical IRI(s)."""
    g = Graph()
    _bind_common(g)
    iri = URIRef(EI["fixtures/cq-editorial-T2"])
    _fixture_header(g, iri, "CQ-T2 fixture")
    supp = URIRef(EICONCEPT["data-center-demand"])
    g.add((supp, RDF.type, SKOS.Concept))
    g.add((supp, SKOS.prefLabel, Literal("data center demand", lang="en")))
    g.add((supp, SKOS.notation, Literal("data-center-demand")))
    output = FIXTURES_DIR / "cq-editorial-T2.ttl"
    g.serialize(output, format="turtle")
    print(f"  wrote {output}")
    return output


def build_fixture_granularity() -> Path:
    """CQ-T3: granularity validator — well-formed corpus, expects 0 violations."""
    g = Graph()
    _bind_common(g)
    g.bind("oeo", OEO)
    iri = URIRef(EI["fixtures/cq-editorial-granularity"])
    _fixture_header(g, iri, "CQ-T3 fixture (well-formed: all topics typed correctly)")
    g.add((SAMPLE_NARRATIVE, RDF.type, EI.Narrative))
    # OEO topic value: typed as owl:Class (passes)
    g.add((SAMPLE_NARRATIVE, EI.narrativeAboutTopic, OEO["OEO_00010439"]))
    g.add((OEO["OEO_00010439"], RDF.type, OWL.Class))
    # Supplement topic value: typed as skos:Concept (passes)
    supp = URIRef(EICONCEPT["data-center-demand"])
    g.add((SAMPLE_NARRATIVE, EI.narrativeAboutTopic, supp))
    g.add((supp, RDF.type, SKOS.Concept))
    output = FIXTURES_DIR / "cq-editorial-granularity.ttl"
    g.serialize(output, format="turtle")
    print(f"  wrote {output}")
    return output


# =============================================================================
# Main orchestration
# =============================================================================


def main() -> None:
    print("\n=== V2 editorial extension build ===\n")

    print("[1/3] Modules")
    build_editorial_module()
    build_argument_pattern_scheme()
    build_narrative_role_scheme()
    build_oeo_topics_scheme()

    print("\n[2/3] Shapes")
    build_editorial_shapes()

    print("\n[3/3] Fixtures (11 files)")
    FIXTURES_DIR.mkdir(exist_ok=True)
    build_fixture_n1()
    build_fixture_n2()
    build_fixture_n3()
    build_fixture_n4()
    build_fixture_n5()
    build_fixture_n6()
    build_fixture_n7()
    build_fixture_n8()
    build_fixture_t1()
    build_fixture_t2()
    build_fixture_granularity()

    print("\nDone.")


if __name__ == "__main__":
    main()
