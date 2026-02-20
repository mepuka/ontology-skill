"""Build the Personal Agent Ontology from conceptual model artifacts.

Loads glossary.csv for class and individual definitions. Axiom patterns
and property designs are encoded directly in Python functions, informed
by axiom-plan.yaml and property-design.yaml documentation.

Produces:
  - personal_agent_ontology.ttl (TBox: classes, properties, axioms)
  - pao-reference-individuals.ttl (Status values, roles, classifiers)
  - pao-data.ttl (Sample ABox data for CQ test execution)
  - shapes/pao-shapes.ttl (SHACL structural shapes)

Usage:
    uv run python ontologies/personal_agent_ontology/scripts/build.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

if TYPE_CHECKING:
    from rdflib.term import Node

# ---------------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------------

PAO = Namespace("https://purl.org/pao/")
PROV = Namespace("http://www.w3.org/ns/prov#")
TIME = Namespace("http://www.w3.org/2006/time#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
SH = Namespace("http://www.w3.org/ns/shacl#")
OBO = Namespace("http://purl.obolibrary.org/obo/")

# Ontology IRIs
TBOX_IRI = URIRef("https://purl.org/pao/")
REF_IRI = URIRef("https://purl.org/pao/reference-individuals")
DATA_IRI = URIRef("https://purl.org/pao/data")
PROV_DECL_IRI = URIRef("https://purl.org/pao/prov-declarations")
TIME_DECL_IRI = URIRef("https://purl.org/pao/time-declarations")
FOAF_DECL_IRI = URIRef("https://purl.org/pao/foaf-declarations")
ODRL_DECL_IRI = URIRef("https://purl.org/pao/odrl-declarations")
BFO_DECL_IRI = URIRef("https://purl.org/pao/bfo-declarations")
TBOX_VERSION_IRI = URIRef("https://purl.org/pao/0.2.0")
REF_VERSION_IRI = URIRef("https://purl.org/pao/reference-individuals/0.2.0")
DATA_VERSION_IRI = URIRef("https://purl.org/pao/data/0.2.0")

# Ontology project root (ontologies/personal_agent_ontology/)
PROJECT = Path(__file__).resolve().parent.parent
DOCS = PROJECT / "docs"
OUT = PROJECT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def bind_common_prefixes(g: Graph) -> None:
    """Bind standard prefixes to a graph."""
    g.bind("pao", PAO)
    g.bind("owl", OWL)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    g.bind("prov", PROV)
    g.bind("time", TIME)
    g.bind("foaf", FOAF)
    g.bind("odrl", ODRL)
    g.bind("obo", OBO)


def bind_shacl_prefix(g: Graph) -> None:
    """Bind SHACL prefix."""
    g.bind("sh", SH)


def load_glossary() -> list[dict[str, str]]:
    """Load glossary.csv and return rows as dicts."""
    path = DOCS / "glossary.csv"
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader if row.get("term")]


def load_yaml(name: str) -> dict[str, Any]:
    """Load a YAML file from the project docs/ directory."""
    path = DOCS / name
    with path.open(encoding="utf-8") as f:
        result: dict[str, Any] = yaml.safe_load(f)
    return result


def to_label(term: str) -> str:
    """Convert CamelCase term to lowercase label with spaces."""
    result: list[str] = []
    for i, ch in enumerate(term):
        if ch.isupper() and i > 0:
            prev = term[i - 1]
            if prev.islower() or (prev.isupper() and i + 1 < len(term) and term[i + 1].islower()):
                result.append(" ")
        result.append(ch.lower())
    return "".join(result)


# ---------------------------------------------------------------------------
# OWL Axiom Helpers
# ---------------------------------------------------------------------------


def _add_existential(g: Graph, cls: URIRef, prop: URIRef, filler: URIRef) -> None:
    """Add: cls SubClassOf prop some filler."""
    r = BNode()
    g.add((r, RDF.type, OWL.Restriction))
    g.add((r, OWL.onProperty, prop))
    g.add((r, OWL.someValuesFrom, filler))
    g.add((cls, RDFS.subClassOf, r))


def _add_universal(g: Graph, cls: URIRef, prop: URIRef, filler: URIRef) -> None:
    """Add: cls SubClassOf prop only filler."""
    r = BNode()
    g.add((r, RDF.type, OWL.Restriction))
    g.add((r, OWL.onProperty, prop))
    g.add((r, OWL.allValuesFrom, filler))
    g.add((cls, RDFS.subClassOf, r))


def _add_qualified_cardinality(
    g: Graph,
    cls: URIRef,
    prop: URIRef,
    filler: URIRef,
    n: int,
    *,
    kind: str = "exact",
) -> None:
    """Add qualified cardinality restriction.

    kind: 'exact', 'min', or 'max'
    """
    r = BNode()
    g.add((r, RDF.type, OWL.Restriction))
    g.add((r, OWL.onProperty, prop))
    g.add((r, OWL.onClass, filler))
    pred_map = {
        "exact": OWL.qualifiedCardinality,
        "min": OWL.minQualifiedCardinality,
        "max": OWL.maxQualifiedCardinality,
    }
    g.add((r, pred_map[kind], Literal(n, datatype=XSD.nonNegativeInteger)))
    g.add((cls, RDFS.subClassOf, r))


def _add_data_exact_cardinality(
    g: Graph, cls: URIRef, prop: URIRef, datatype: URIRef, n: int
) -> None:
    """Add qualified cardinality on a data property."""
    r = BNode()
    g.add((r, RDF.type, OWL.Restriction))
    g.add((r, OWL.onProperty, prop))
    g.add((r, OWL.onDataRange, datatype))
    g.add((r, OWL.qualifiedCardinality, Literal(n, datatype=XSD.nonNegativeInteger)))
    g.add((cls, RDFS.subClassOf, r))


def _add_enumeration(g: Graph, cls: URIRef, individuals: list[URIRef]) -> None:
    """Add: cls EquivalentTo owl:oneOf(individuals)."""
    list_node = BNode()
    items: list[Node] = list(individuals)
    Collection(g, list_node, items)
    anon_cls = BNode()
    g.add((anon_cls, OWL.oneOf, list_node))
    g.add((cls, OWL.equivalentClass, anon_cls))


def _add_disjoint_union(g: Graph, parent: URIRef, children: list[URIRef]) -> None:
    """Add: parent DisjointUnionOf children."""
    list_node = BNode()
    items: list[Node] = list(children)
    Collection(g, list_node, items)
    g.add((parent, OWL.disjointUnionOf, list_node))


def _add_all_disjoint_classes(g: Graph, classes: list[URIRef]) -> None:
    """Add AllDisjointClasses axiom."""
    node = BNode()
    g.add((node, RDF.type, OWL.AllDisjointClasses))
    list_node = BNode()
    items: list[Node] = list(classes)
    Collection(g, list_node, items)
    g.add((node, OWL.members, list_node))


def _add_all_different(g: Graph, individuals: list[URIRef]) -> None:
    """Add AllDifferent axiom for named individuals."""
    node = BNode()
    g.add((node, RDF.type, OWL.AllDifferent))
    list_node = BNode()
    items: list[Node] = list(individuals)
    Collection(g, list_node, items)
    g.add((node, OWL.distinctMembers, list_node))


def _add_inverse_pair(g: Graph, prop1: URIRef, prop2: URIRef) -> None:
    """Declare prop1 owl:inverseOf prop2."""
    g.add((prop1, OWL.inverseOf, prop2))


# ---------------------------------------------------------------------------
# TBox Builder
# ---------------------------------------------------------------------------


def build_tbox(glossary: list[dict[str, str]]) -> Graph:
    """Build the TBox graph with classes, properties, and axioms."""
    g = Graph()
    bind_common_prefixes(g)

    # --- Ontology header ---
    g.add((TBOX_IRI, RDF.type, OWL.Ontology))
    g.add((TBOX_IRI, OWL.versionIRI, TBOX_VERSION_IRI))
    g.add((TBOX_IRI, OWL.imports, REF_IRI))
    g.add((TBOX_IRI, OWL.imports, PROV_DECL_IRI))
    g.add((TBOX_IRI, OWL.imports, TIME_DECL_IRI))
    g.add((TBOX_IRI, OWL.imports, FOAF_DECL_IRI))
    g.add((TBOX_IRI, OWL.imports, ODRL_DECL_IRI))
    g.add((TBOX_IRI, OWL.imports, BFO_DECL_IRI))
    g.add((TBOX_IRI, DCTERMS.title, Literal("Personal Agent Ontology", lang="en")))
    g.add(
        (
            TBOX_IRI,
            DCTERMS.description,
            Literal(
                "An OWL 2 DL ontology modeling AI agent architecture including "
                "conversations, memory systems, goals, plans, and governance.",
                lang="en",
            ),
        )
    )
    g.add((TBOX_IRI, OWL.versionInfo, Literal("0.2.0")))
    g.add((TBOX_IRI, DCTERMS.created, Literal("2026-02-19")))
    g.add((TBOX_IRI, DCTERMS.creator, Literal("ontology-architect skill")))
    g.add((TBOX_IRI, DCTERMS.license, URIRef("https://spdx.org/licenses/MIT")))
    g.add((TBOX_IRI, DCTERMS.rights, Literal("MIT License")))
    g.add(
        (
            TBOX_IRI,
            PROV.generatedAtTime,
            Literal("2026-02-18T00:00:00Z", datatype=XSD.dateTime),
        )
    )

    # Build glossary lookup
    class_glossary = {row["term"]: row for row in glossary if row["category"] == "class"}

    # --- Declare all 51 classes ---
    _add_classes(g, class_glossary)

    # --- Declare all properties ---
    _add_object_properties(g)
    _add_data_properties(g)

    # --- Property hierarchy ---
    _add_property_hierarchy(g)

    # --- Inverse pairs ---
    _add_inverse_pairs(g)

    # --- Existential restrictions ---
    _add_existential_restrictions(g)

    # --- Universal restrictions ---
    _add_universal_restrictions(g)

    # --- Qualified cardinality restrictions ---
    _add_cardinality_restrictions(g)

    # --- DisjointUnion axioms ---
    _add_disjoint_unions(g)

    # --- AllDisjointClasses axioms ---
    _add_disjointness_axioms(g)

    # --- HasKey identity contracts ---
    _add_has_key_axioms(g)

    # --- Add IAO_0000115 aliases for OBO tool compatibility ---
    _add_iao_definitions(g)

    return g


def _add_classes(g: Graph, class_glossary: dict[str, dict[str, str]]) -> None:
    """Declare all 51 PAO classes with labels, definitions, and subclass axioms."""
    # Class hierarchy: (class_name, parent_uri, bfo_uri_or_none)
    class_defs: list[tuple[str, URIRef | None, URIRef | None]] = [
        # pao-core
        ("Agent", PROV.Agent, None),  # cross-cuts BFO
        ("AIAgent", PAO.Agent, OBO.BFO_0000031),
        ("HumanUser", PAO.Agent, OBO.BFO_0000030),
        ("SubAgent", PAO.AIAgent, None),  # inherits GDC from AIAgent
        ("AgentRole", PROV.Role, OBO.BFO_0000023),
        ("Organization", PAO.Agent, OBO.BFO_0000030),
        ("Persona", PROV.Entity, OBO.BFO_0000031),
        # pao-event
        ("Event", PROV.Activity, OBO.BFO_0000015),
        ("Action", PAO.Event, None),
        ("Status", None, None),  # Value partition, no BFO parent
        ("SessionStatus", PAO.Status, None),
        ("TaskStatus", PAO.Status, None),
        ("ComplianceStatus", PAO.Status, None),
        ("ItemFate", PAO.Status, None),  # Value Partition
        # pao-conversation
        ("Conversation", PAO.Event, None),
        ("Session", PAO.Event, None),
        ("Turn", PAO.Event, None),
        ("Message", PROV.Entity, OBO.BFO_0000031),
        ("ToolDefinition", PROV.Entity, OBO.BFO_0000031),
        ("ToolInvocation", PAO.Action, None),
        ("CompactionEvent", PAO.Event, None),
        ("CompactionDisposition", PROV.Entity, OBO.BFO_0000031),
        ("Observation", PAO.Event, None),  # inherits Process from Event
        ("StatusTransition", PAO.Event, None),  # inherits Process from Event
        ("SessionStatusTransition", PAO.StatusTransition, None),
        ("TaskStatusTransition", PAO.StatusTransition, None),
        # pao-memory
        ("MemoryItem", PROV.Entity, OBO.BFO_0000031),
        ("MemoryTier", PROV.Entity, OBO.BFO_0000031),
        ("WorkingMemory", PAO.MemoryTier, None),
        ("EpisodicMemory", PAO.MemoryTier, None),
        ("SemanticMemory", PAO.MemoryTier, None),
        ("ProceduralMemory", PAO.MemoryTier, None),
        ("Episode", PAO.MemoryItem, None),
        ("Claim", PAO.MemoryItem, None),
        ("MemoryOperation", PAO.Event, None),
        ("Encoding", PAO.MemoryOperation, None),
        ("Retrieval", PAO.MemoryOperation, None),
        ("Consolidation", PAO.MemoryOperation, None),
        ("Forgetting", PAO.MemoryOperation, None),
        ("Rehearsal", PAO.MemoryOperation, None),
        ("MemoryBlock", PAO.MemoryItem, None),
        # pao-planning
        ("Goal", PROV.Entity, OBO.BFO_0000031),
        ("Plan", PROV.Plan, None),  # prov:Plan is subclass of prov:Entity
        ("Task", PROV.Entity, OBO.BFO_0000031),
        ("Intention", PROV.Entity, OBO.BFO_0000031),
        # pao-governance
        ("PermissionPolicy", ODRL.Policy, OBO.BFO_0000031),
        ("SafetyConstraint", PROV.Entity, OBO.BFO_0000031),
        ("ErasureEvent", PAO.Event, None),
        ("SensitivityLevel", PAO.Status, None),  # Value Partition
        ("ConsentRecord", PROV.Entity, OBO.BFO_0000031),
        ("RetentionPolicy", PROV.Entity, OBO.BFO_0000031),
    ]

    # Additional parent axioms (multiple inheritance)
    additional_parents: dict[str, list[URIRef]] = {
        "AIAgent": [PROV.SoftwareAgent],
        "HumanUser": [PROV.Person, FOAF.Person],
    }

    for cls_name, parent, bfo in class_defs:
        cls_uri = PAO[cls_name]
        g.add((cls_uri, RDF.type, OWL.Class))
        g.add((cls_uri, RDFS.label, Literal(to_label(cls_name), lang="en")))

        if cls_name in class_glossary:
            defn = class_glossary[cls_name]["definition"]
            g.add((cls_uri, SKOS.definition, Literal(defn, lang="en")))

        if parent is not None:
            g.add((cls_uri, RDFS.subClassOf, parent))

        if bfo is not None:
            g.add((cls_uri, RDFS.subClassOf, bfo))

        for extra_parent in additional_parents.get(cls_name, []):
            g.add((cls_uri, RDFS.subClassOf, extra_parent))


def _add_object_properties(g: Graph) -> None:
    """Declare all 64 object properties."""
    # Each tuple: (name, domain, range, characteristics, definition)
    obj_props: list[tuple[str, URIRef | None, URIRef | None, list[str], str]] = [
        # pao-core: generic part-whole
        (
            "partOf",
            OWL.Thing,
            OWL.Thing,
            ["transitive"],
            "A transitive relation linking an entity to a whole it is part of.",
        ),
        (
            "hasPart",
            OWL.Thing,
            OWL.Thing,
            ["transitive"],
            "A transitive relation linking a whole to one of its parts.",
        ),
        # pao-core: identity & actors
        (
            "hasAvailableTool",
            PAO.Agent,
            PAO.ToolDefinition,
            [],
            "Links an agent to a tool definition available for invocation.",
        ),
        (
            "availableToAgent",
            PAO.ToolDefinition,
            PAO.Agent,
            [],
            "Links a tool definition to an agent that may invoke it.",
        ),
        (
            "spawnedBy",
            PAO.SubAgent,
            PAO.Agent,
            ["functional"],
            "Links a sub-agent to the parent agent that spawned it.",
        ),
        (
            "hasParticipant",
            PAO.Event,
            PAO.Agent,
            [],
            "Links an event to an agent that participates in it.",
        ),
        (
            "participatesIn",
            PAO.Agent,
            PAO.Event,
            [],
            "Links an agent to an event it participates in.",
        ),
        (
            "hasRole",
            PAO.Agent,
            PAO.AgentRole,
            [],
            "Links an agent to a role it bears in some context.",
        ),
        (
            "performedBy",
            PAO.Action,
            PAO.Agent,
            ["functional"],
            "Links an action to the agent that intentionally performed it.",
        ),
        # pao-event
        (
            "hasTemporalExtent",
            None,
            TIME.TemporalEntity,
            ["functional"],
            "Links an event to its temporal extent.",
        ),
        (
            "hasStatus",
            OWL.Thing,
            PAO.Status,
            ["functional"],
            "Links an entity to its current status value.",
        ),
        # pao-conversation
        (
            "partOfConversation",
            PAO.Event,
            PAO.Conversation,
            ["functional"],
            "Links a session to the conversation it is a temporal part of.",
        ),
        (
            "inConversation",
            PAO.Event,
            PAO.Conversation,
            ["functional"],
            "Links an event to its containing conversation.",
        ),
        (
            "partOfSession",
            PAO.Event,
            PAO.Session,
            ["functional"],
            "Links a turn to the session it is a temporal part of.",
        ),
        (
            "inSession",
            PAO.Event,
            PAO.Session,
            ["functional"],
            "Links an event to its containing session.",
        ),
        (
            "invokesTool",
            PAO.ToolInvocation,
            PAO.ToolDefinition,
            ["functional"],
            "Links a tool invocation to the tool definition invoked.",
        ),
        (
            "invokedIn",
            PAO.ToolDefinition,
            PAO.ToolInvocation,
            [],
            "Links a tool definition to invocations in which it was used.",
        ),
        (
            "invokedBy",
            PAO.ToolInvocation,
            PAO.Agent,
            ["functional"],
            "Links a tool invocation to the agent that initiated it.",
        ),
        (
            "hasInput",
            PAO.ToolInvocation,
            PROV.Entity,
            [],
            "Links a tool invocation to the input data provided.",
        ),
        (
            "hasOutput",
            PAO.ToolInvocation,
            PROV.Entity,
            [],
            "Links a tool invocation to the output data returned.",
        ),
        (
            "producedSummary",
            PAO.CompactionEvent,
            PAO.MemoryItem,
            ["functional"],
            "Links a compaction event to the summary it generated.",
        ),
        (
            "delegatedTask",
            PAO.SubAgent,
            PAO.Task,
            [],
            "Links a sub-agent to the task it was spawned to perform.",
        ),
        # pao-memory
        (
            "storedIn",
            None,
            PAO.MemoryTier,
            [],
            "Links a memory item to the memory tier where it is stored.",
        ),
        (
            "stores",
            PAO.MemoryTier,
            None,
            [],
            "Links a memory tier to a memory item it currently holds.",
        ),
        (
            "hasTopic",
            PAO.MemoryItem,
            SKOS.Concept,
            [],
            "Links a memory item to a topic concept describing its subject.",
        ),
        (
            "aboutAgent",
            PAO.MemoryItem,
            PAO.Agent,
            [],
            "Links a memory item to the agent it describes.",
        ),
        (
            "hasEvidence",
            PAO.Claim,
            PROV.Entity,
            [],
            "Links a claim to the evidence entities that support it.",
        ),
        (
            "recordedInEpisode",
            PAO.Event,
            PAO.Episode,
            [],
            "Links an event to the episode that records it.",
        ),
        ("recordsEvent", PAO.Episode, PAO.Event, [], "Links an episode to an event it records."),
        (
            "operatesOn",
            PAO.MemoryOperation,
            PAO.MemoryItem,
            [],
            "Links a memory operation to the memory item it acts upon.",
        ),
        # pao-planning
        (
            "pursuedBy",
            PAO.Goal,
            PAO.Agent,
            [],
            "Links a goal to the agent that is actively pursuing it.",
        ),
        (
            "pursuesGoal",
            PAO.Agent,
            PAO.Goal,
            [],
            "Links an agent to a goal it is actively pursuing.",
        ),
        (
            "achievesGoal",
            PAO.Plan,
            PAO.Goal,
            [],
            "Links a plan to the goal it is designed to achieve.",
        ),
        (
            "partOfPlan",
            PAO.Task,
            PAO.Plan,
            ["functional"],
            "Links a task to the plan it belongs to as a component.",
        ),
        (
            "hasTask",
            PAO.Plan,
            PAO.Task,
            [],
            "Links a plan to a task that is one of its component steps.",
        ),
        (
            "blockedBy",
            PAO.Task,
            PAO.Task,
            [],
            "Links a task to another task that must complete before it can proceed.",
        ),
        (
            "blocks",
            PAO.Task,
            PAO.Task,
            [],
            "Links a task to another task that depends on its completion.",
        ),
        # pao-governance
        (
            "appliesTo",
            PROV.Entity,
            PAO.Agent,
            [],
            "Links a policy or constraint to the agent it governs.",
        ),
        (
            "grantsPermission",
            PAO.PermissionPolicy,
            ODRL.Permission,
            [],
            "Links a permission policy to the specific permission it grants.",
        ),
        (
            "hasComplianceStatus",
            PAO.ToolInvocation,
            PAO.ComplianceStatus,
            ["functional"],
            "Links a tool invocation to its compliance status.",
        ),
        (
            "governedByPolicy",
            PAO.ToolInvocation,
            PAO.PermissionPolicy,
            [],
            "Links a tool invocation to the permission policy that governed it.",
        ),
        (
            "restrictsToolUse",
            PAO.PermissionPolicy,
            PAO.ToolDefinition,
            [],
            "Links a permission policy to a tool whose use it restricts.",
        ),
        (
            "requestedBy",
            PAO.ErasureEvent,
            PAO.Agent,
            ["functional"],
            "Links an erasure event to the agent who requested deletion.",
        ),
        # v0.2.0: Identity additions
        (
            "belongsTo",
            PAO.Agent,
            PAO.Organization,
            ["functional"],
            "Links an agent to the organization it belongs to.",
        ),
        (
            "hasMember",
            PAO.Organization,
            PAO.Agent,
            [],
            "Links an organization to its member agents.",
        ),
        (
            "hasPersona",
            PAO.AIAgent,
            PAO.Persona,
            ["functional"],
            "Links an AI agent to its configured persona.",
        ),
        # v0.2.0: Planning additions
        (
            "intendedBy",
            PAO.Intention,
            PAO.Agent,
            [],
            "Links an intention to the agent that holds it.",
        ),
        (
            "derivedFromGoal",
            PAO.Intention,
            PAO.Goal,
            [],
            "Links an intention to the goal it was derived from.",
        ),
        # v0.2.0: Governance additions
        (
            "consentSubject",
            PAO.ConsentRecord,
            PAO.Agent,
            ["functional"],
            "Links a consent record to the data subject agent.",
        ),
        (
            "consentPurpose",
            PAO.ConsentRecord,
            PROV.Entity,
            [],
            "Links a consent record to the entity describing the purpose.",
        ),
        (
            "governedByRetention",
            PAO.MemoryItem,
            PAO.RetentionPolicy,
            [],
            "Links a memory item to the retention policy that governs it.",
        ),
        # v0.2.0: hasSensitivityLevel migrated from DataProperty
        (
            "hasSensitivityLevel",
            PAO.MemoryItem,
            PAO.SensitivityLevel,
            ["functional"],
            "Links a memory item to its privacy sensitivity classification.",
        ),
        # v0.3.0: Compaction trace
        (
            "compactedItem",
            PAO.CompactionEvent,
            PROV.Entity,
            [],
            "Links a compaction event to an item that was in scope for compaction.",
        ),
        (
            "hasCompactionDisposition",
            PAO.CompactionEvent,
            PAO.CompactionDisposition,
            [],
            "Links a compaction event to a disposition record for one of its items.",
        ),
        (
            "dispositionOf",
            PAO.CompactionDisposition,
            PROV.Entity,
            ["functional"],
            "Links a compaction disposition to the item it describes.",
        ),
        (
            "hasItemFate",
            PAO.CompactionDisposition,
            PAO.ItemFate,
            ["functional"],
            "Links a compaction disposition to the fate of the item.",
        ),
        # v0.3.0: Cross-session resume
        (
            "continuedFrom",
            PAO.Session,
            PAO.Session,
            ["functional"],
            "Links a session to the prior session it continues.",
        ),
        (
            "continuedBy",
            PAO.Session,
            PAO.Session,
            [],
            "Links a session to a subsequent session that continues its work.",
        ),
        # v0.3.0: Lifecycle transitions
        (
            "fromStatus",
            PAO.StatusTransition,
            PAO.Status,
            ["functional"],
            "The status value before the transition.",
        ),
        (
            "toStatus",
            PAO.StatusTransition,
            PAO.Status,
            ["functional"],
            "The status value after the transition.",
        ),
        (
            "transitionSubject",
            PAO.StatusTransition,
            OWL.Thing,
            ["functional"],
            "The entity whose status changed in this transition.",
        ),
        (
            "triggeredBy",
            PAO.StatusTransition,
            PAO.Event,
            [],
            "The event that caused this status transition.",
        ),
        (
            "previousTransition",
            PAO.StatusTransition,
            PAO.StatusTransition,
            ["functional"],
            "Links to the preceding status transition for the same subject.",
        ),
        (
            "nextTransition",
            PAO.StatusTransition,
            PAO.StatusTransition,
            ["functional"],
            "Links to the following status transition for the same subject.",
        ),
    ]

    for name, domain, range_, chars, defn in obj_props:
        uri = PAO[name]
        g.add((uri, RDF.type, OWL.ObjectProperty))
        g.add((uri, RDFS.label, Literal(to_label(name), lang="en")))
        g.add((uri, SKOS.definition, Literal(defn, lang="en")))
        if domain is not None:
            g.add((uri, RDFS.domain, domain))
        if range_ is not None:
            g.add((uri, RDFS.range, range_))
        if "functional" in chars:
            g.add((uri, RDF.type, OWL.FunctionalProperty))
        if "transitive" in chars:
            g.add((uri, RDF.type, OWL.TransitiveProperty))


def _add_data_properties(g: Graph) -> None:
    """Declare all 14 data properties."""
    data_props: list[tuple[str, URIRef | None, URIRef, list[str], str]] = [
        (
            "hasTimestamp",
            None,
            XSD.dateTime,
            ["functional"],
            "A convenience timestamp for point-in-time events.",
        ),
        (
            "hasTurnIndex",
            PAO.Turn,
            XSD.nonNegativeInteger,
            ["functional"],
            "The zero-based ordinal position of a turn within its session.",
        ),
        (
            "hasContent",
            PROV.Entity,
            XSD.string,
            ["functional"],
            "The textual or structured content of an information artifact.",
        ),
        (
            "hasConfidence",
            PAO.Claim,
            XSD.decimal,
            ["functional"],
            "The confidence level of a claim, between 0.0 and 1.0.",
        ),
        (
            "claimType",
            PAO.Claim,
            XSD.string,
            ["functional"],
            "A classifier string indicating the kind of claim.",
        ),
        # v0.2.0: Memory block properties
        (
            "hasBlockKey",
            PAO.MemoryBlock,
            XSD.string,
            [],
            "A key in a memory block's key-value store.",
        ),
        (
            "hasBlockValue",
            PAO.MemoryBlock,
            XSD.string,
            [],
            "A value in a memory block's key-value store.",
        ),
        # v0.2.0: Governance properties
        (
            "retentionPeriodDays",
            PAO.RetentionPolicy,
            XSD.nonNegativeInteger,
            ["functional"],
            "The number of days a memory item should be retained.",
        ),
        # v0.3.0: Compaction trace
        (
            "fateReason",
            PAO.CompactionDisposition,
            XSD.string,
            [],
            "A textual reason for the compaction disposition decision.",
        ),
        # v0.3.0: Eviction eligibility
        (
            "hasLastAccessTime",
            PAO.MemoryItem,
            XSD.dateTime,
            ["functional"],
            "The timestamp of the most recent access to this memory item.",
        ),
        (
            "isEvictionCandidate",
            PAO.MemoryItem,
            XSD.boolean,
            ["functional"],
            "Whether this memory item is eligible for eviction from its tier.",
        ),
        # v0.3.0: HasKey identity
        (
            "hasAgentId",
            PAO.AIAgent,
            XSD.string,
            ["functional"],
            "The unique string identifier for this AI agent.",
        ),
        (
            "hasSessionId",
            PAO.Session,
            XSD.string,
            ["functional"],
            "The unique string identifier for this session.",
        ),
        (
            "hasConversationId",
            PAO.Conversation,
            XSD.string,
            ["functional"],
            "The unique string identifier for this conversation.",
        ),
    ]

    for name, domain, range_, chars, defn in data_props:
        uri = PAO[name]
        g.add((uri, RDF.type, OWL.DatatypeProperty))
        g.add((uri, RDFS.label, Literal(to_label(name), lang="en")))
        g.add((uri, SKOS.definition, Literal(defn, lang="en")))
        if domain is not None:
            g.add((uri, RDFS.domain, domain))
        g.add((uri, RDFS.range, range_))
        if "functional" in chars:
            g.add((uri, RDF.type, OWL.FunctionalProperty))


def _add_property_hierarchy(g: Graph) -> None:
    """Add rdfs:subPropertyOf axioms."""
    # partOf hierarchy
    g.add((PAO.partOfConversation, RDFS.subPropertyOf, PAO.partOf))
    g.add((PAO.partOfSession, RDFS.subPropertyOf, PAO.partOf))
    g.add((PAO.partOfPlan, RDFS.subPropertyOf, PAO.partOf))
    # hasPart hierarchy
    g.add((PAO.hasTask, RDFS.subPropertyOf, PAO.hasPart))
    # hasParticipant hierarchy
    g.add((PAO.performedBy, RDFS.subPropertyOf, PAO.hasParticipant))
    g.add((PAO.invokedBy, RDFS.subPropertyOf, PAO.performedBy))
    # hasStatus hierarchy
    g.add((PAO.hasComplianceStatus, RDFS.subPropertyOf, PAO.hasStatus))
    # compactedItem is subPropertyOf prov:used
    g.add((PAO.compactedItem, RDFS.subPropertyOf, PROV.used))


def _add_inverse_pairs(g: Graph) -> None:
    """Declare owl:inverseOf pairs."""
    pairs = [
        (PAO.partOf, PAO.hasPart),
        (PAO.hasAvailableTool, PAO.availableToAgent),
        (PAO.hasParticipant, PAO.participatesIn),
        (PAO.invokesTool, PAO.invokedIn),
        (PAO.storedIn, PAO.stores),
        (PAO.recordedInEpisode, PAO.recordsEvent),
        (PAO.pursuedBy, PAO.pursuesGoal),
        (PAO.partOfPlan, PAO.hasTask),
        (PAO.blockedBy, PAO.blocks),
        (PAO.belongsTo, PAO.hasMember),
        (PAO.continuedFrom, PAO.continuedBy),
        (PAO.previousTransition, PAO.nextTransition),
        (PAO.achievesGoal, None),  # no inverse defined
    ]
    for p1, p2 in pairs:
        if p2 is not None:
            _add_inverse_pair(g, p1, p2)


def _add_existential_restrictions(g: Graph) -> None:
    """Add SubClassOf someValuesFrom restrictions."""
    restrictions: list[tuple[URIRef, URIRef, URIRef]] = [
        # CQ-002: AIAgent has at least one tool
        (PAO.AIAgent, PAO.hasAvailableTool, PAO.ToolDefinition),
        # CQ-003: SubAgent was spawned and has delegated task
        (PAO.SubAgent, PAO.spawnedBy, PAO.AIAgent),
        (PAO.SubAgent, PAO.delegatedTask, PAO.Task),
        # CQ-005: Session belongs to conversation and has temporal extent
        (PAO.Session, PAO.partOfConversation, PAO.Conversation),
        (PAO.Session, PAO.hasTemporalExtent, TIME.Interval),
        # CQ-006: Turn belongs to session and has participant
        (PAO.Turn, PAO.partOfSession, PAO.Session),
        (PAO.Turn, PAO.hasParticipant, PAO.Agent),
        # CQ-007: ToolInvocation links
        (PAO.ToolInvocation, PAO.invokesTool, PAO.ToolDefinition),
        (PAO.ToolInvocation, PAO.invokedBy, PAO.Agent),
        (PAO.ToolInvocation, PAO.inSession, PAO.Session),
        # CQ-008: ToolInvocation has input/output
        (PAO.ToolInvocation, PAO.hasInput, PROV.Entity),
        (PAO.ToolInvocation, PAO.hasOutput, PROV.Entity),
        # CQ-006: Turn belongs to conversation
        (PAO.Turn, PAO.partOfConversation, PAO.Conversation),
        # CQ-009: Session has participant
        (PAO.Session, PAO.hasParticipant, PAO.Agent),
        # CQ-010: CompactionEvent
        (PAO.CompactionEvent, PAO.inConversation, PAO.Conversation),
        (PAO.CompactionEvent, PAO.producedSummary, PAO.MemoryItem),
        # CQ-011: MemoryItem stored in tier
        (PAO.MemoryItem, PAO.storedIn, PAO.MemoryTier),
        # CQ-012: Episode stored in tier, has topic and temporal extent
        (PAO.Episode, PAO.storedIn, PAO.MemoryTier),
        (PAO.Episode, PAO.hasTopic, SKOS.Concept),
        (PAO.Episode, PAO.hasTemporalExtent, TIME.Interval),
        # CQ-013: Claim has content and confidence (object existentials)
        (PAO.Claim, PAO.storedIn, PAO.MemoryTier),
        # CQ-015: Claim about agent
        (PAO.Claim, PAO.aboutAgent, PAO.Agent),
        # CQ-014: MemoryItem provenance
        (PAO.MemoryItem, PROV.wasAttributedTo, PAO.Agent),
        (PAO.MemoryItem, PROV.wasGeneratedBy, PROV.Activity),
        # CQ-021: Event has temporal extent
        (PAO.Event, PAO.hasTemporalExtent, TIME.TemporalEntity),
        # CQ-019: MemoryOperation targets
        (PAO.MemoryOperation, PAO.operatesOn, PAO.MemoryItem),
        # CQ-023: Action has performer
        (PAO.Action, PAO.performedBy, PAO.Agent),
        # CQ-026: Goal has pursuer and status
        (PAO.Goal, PAO.pursuedBy, PAO.Agent),
        (PAO.Goal, PAO.hasStatus, PAO.TaskStatus),
        # CQ-027: Task in plan and has status
        (PAO.Task, PAO.partOfPlan, PAO.Plan),
        (PAO.Task, PAO.hasStatus, PAO.TaskStatus),
        # CQ-028: Plan achieves goal
        (PAO.Plan, PAO.achievesGoal, PAO.Goal),
        # CQ-030: PermissionPolicy
        (PAO.PermissionPolicy, PAO.appliesTo, PAO.Agent),
        (PAO.PermissionPolicy, PAO.grantsPermission, ODRL.Permission),
        # CQ-031: ToolInvocation compliance
        (PAO.ToolInvocation, PAO.hasComplianceStatus, PAO.ComplianceStatus),
        # CQ-031: ToolInvocation governed by policy
        (PAO.ToolInvocation, PAO.governedByPolicy, PAO.PermissionPolicy),
        # CQ-034: ErasureEvent
        (PAO.ErasureEvent, PAO.requestedBy, PAO.Agent),
        # CQ-035: SafetyConstraint
        (PAO.SafetyConstraint, PAO.appliesTo, PAO.Agent),
        # CQ-038: Session has status
        (PAO.Session, PAO.hasStatus, PAO.SessionStatus),
        # CQ-039: PermissionPolicy restricts tools
        (PAO.PermissionPolicy, PAO.restrictsToolUse, PAO.ToolDefinition),
        # CQ-041: Organization has members
        (PAO.Organization, PAO.hasMember, PAO.Agent),
        # CQ-042: AIAgent has persona
        (PAO.AIAgent, PAO.hasPersona, PAO.Persona),
        # CQ-043: Observation in session
        (PAO.Observation, PAO.inSession, PAO.Session),
        # CQ-046: Intention has intender
        (PAO.Intention, PAO.intendedBy, PAO.Agent),
        # CQ-047: Intention derived from goal
        (PAO.Intention, PAO.derivedFromGoal, PAO.Goal),
        # CQ-048: MemoryItem has sensitivity level (migrated)
        (PAO.MemoryItem, PAO.hasSensitivityLevel, PAO.SensitivityLevel),
        # CQ-049: ConsentRecord has subject
        (PAO.ConsentRecord, PAO.consentSubject, PAO.Agent),
        # CQ-050: MemoryItem governed by retention
        (PAO.MemoryItem, PAO.governedByRetention, PAO.RetentionPolicy),
        # CQ-052: CompactionEvent uses items
        (PAO.CompactionEvent, PAO.compactedItem, PROV.Entity),
        # CQ-058: StatusTransition has from/to/subject
        (PAO.StatusTransition, PAO.fromStatus, PAO.Status),
        (PAO.StatusTransition, PAO.toStatus, PAO.Status),
        (PAO.StatusTransition, PAO.transitionSubject, OWL.Thing),
        # CQ-052: CompactionDisposition has item and fate
        (PAO.CompactionDisposition, PAO.dispositionOf, PROV.Entity),
        (PAO.CompactionDisposition, PAO.hasItemFate, PAO.ItemFate),
    ]
    for cls, prop, filler in restrictions:
        _add_existential(g, cls, prop, filler)


def _add_universal_restrictions(g: Graph) -> None:
    """Add SubClassOf allValuesFrom restrictions."""
    # CQ-012: Episodes can only be stored in EpisodicMemory
    _add_universal(g, PAO.Episode, PAO.storedIn, PAO.EpisodicMemory)


def _add_cardinality_restrictions(g: Graph) -> None:
    """Add qualified cardinality restrictions."""
    # CQ-006: Turn has exactly 1 participant (Agent)
    _add_qualified_cardinality(g, PAO.Turn, PAO.hasParticipant, PAO.Agent, 1, kind="exact")
    # CQ-006: Turn has exactly 1 turn index
    _add_data_exact_cardinality(g, PAO.Turn, PAO.hasTurnIndex, XSD.nonNegativeInteger, 1)
    # CQ-018: MemoryItem stored in exactly 1 tier
    _add_qualified_cardinality(g, PAO.MemoryItem, PAO.storedIn, PAO.MemoryTier, 1, kind="exact")


def _add_disjoint_unions(g: Graph) -> None:
    """Add DisjointUnion axioms (exhaustive covering)."""
    # MemoryTier DisjointUnionOf 4 subtypes
    _add_disjoint_union(
        g,
        PAO.MemoryTier,
        [
            PAO.WorkingMemory,
            PAO.EpisodicMemory,
            PAO.SemanticMemory,
            PAO.ProceduralMemory,
        ],
    )
    # MemoryOperation DisjointUnionOf 5 subtypes
    _add_disjoint_union(
        g,
        PAO.MemoryOperation,
        [
            PAO.Encoding,
            PAO.Retrieval,
            PAO.Consolidation,
            PAO.Forgetting,
            PAO.Rehearsal,
        ],
    )


def _add_disjointness_axioms(g: Graph) -> None:
    """Add AllDisjointClasses axioms."""
    # Agent subtypes
    _add_all_disjoint_classes(g, [PAO.AIAgent, PAO.HumanUser, PAO.Organization])
    # Event subtypes (9-way)
    _add_all_disjoint_classes(
        g,
        [
            PAO.Action,
            PAO.Conversation,
            PAO.Session,
            PAO.Turn,
            PAO.CompactionEvent,
            PAO.ErasureEvent,
            PAO.MemoryOperation,
            PAO.Observation,
            PAO.StatusTransition,
        ],
    )
    # StatusTransition subtypes
    _add_all_disjoint_classes(g, [PAO.SessionStatusTransition, PAO.TaskStatusTransition])
    # MemoryItem subtypes
    _add_all_disjoint_classes(g, [PAO.Episode, PAO.Claim, PAO.MemoryBlock])
    # Status subtypes
    _add_all_disjoint_classes(
        g,
        [
            PAO.SessionStatus,
            PAO.TaskStatus,
            PAO.ComplianceStatus,
            PAO.SensitivityLevel,
            PAO.ItemFate,
        ],
    )
    # Governance types
    _add_all_disjoint_classes(
        g,
        [PAO.PermissionPolicy, PAO.SafetyConstraint, PAO.ConsentRecord, PAO.RetentionPolicy],
    )
    # Cross-module GDC disjointness: information artifacts
    _add_all_disjoint_classes(
        g,
        [
            PAO.Message,
            PAO.ToolDefinition,
            PAO.MemoryItem,
            PAO.MemoryTier,
            PAO.Goal,
            PAO.Plan,
            PAO.Task,
            PAO.PermissionPolicy,
            PAO.SafetyConstraint,
            PAO.Persona,
            PAO.Intention,
            PAO.ConsentRecord,
            PAO.RetentionPolicy,
            PAO.CompactionDisposition,
        ],
    )
    # MemoryTier subtypes (covered by DisjointUnion, but explicit for clarity)
    _add_all_disjoint_classes(
        g,
        [
            PAO.WorkingMemory,
            PAO.EpisodicMemory,
            PAO.SemanticMemory,
            PAO.ProceduralMemory,
        ],
    )
    # MemoryOperation subtypes (covered by DisjointUnion, but explicit)
    _add_all_disjoint_classes(
        g,
        [
            PAO.Encoding,
            PAO.Retrieval,
            PAO.Consolidation,
            PAO.Forgetting,
            PAO.Rehearsal,
        ],
    )


def _add_has_key_axioms(g: Graph) -> None:
    """Add owl:hasKey axioms for identity contracts (DN-05)."""
    for cls, key_prop in [
        (PAO.AIAgent, PAO.hasAgentId),
        (PAO.Session, PAO.hasSessionId),
        (PAO.Conversation, PAO.hasConversationId),
    ]:
        key_list = BNode()
        Collection(g, key_list, [key_prop])
        g.add((cls, OWL.hasKey, key_list))


def _add_iao_definitions(g: Graph) -> None:
    """Copy skos:definition to obo:IAO_0000115 for OBO tool compatibility."""
    iao_def = OBO["IAO_0000115"]
    for subj, obj in g.subject_objects(SKOS.definition):
        g.add((subj, iao_def, obj))


# ---------------------------------------------------------------------------
# Reference Individuals Builder
# ---------------------------------------------------------------------------


def build_reference_individuals(glossary: list[dict[str, str]]) -> Graph:
    """Build named individuals: status values, roles, classifiers."""
    g = Graph()
    bind_common_prefixes(g)

    # --- Ontology header ---
    g.add((REF_IRI, RDF.type, OWL.Ontology))
    g.add((REF_IRI, OWL.versionIRI, REF_VERSION_IRI))
    g.add(
        (
            REF_IRI,
            DCTERMS.title,
            Literal(
                "Personal Agent Ontology — Reference Individuals",
                lang="en",
            ),
        )
    )
    g.add(
        (
            REF_IRI,
            DCTERMS.description,
            Literal(
                "Named individuals for status values, agent roles, and classifiers.",
                lang="en",
            ),
        )
    )
    g.add((REF_IRI, OWL.versionInfo, Literal("0.2.0")))
    g.add((REF_IRI, DCTERMS.created, Literal("2026-02-19")))
    g.add((REF_IRI, DCTERMS.creator, Literal("ontology-architect skill")))
    g.add((REF_IRI, DCTERMS.license, URIRef("https://spdx.org/licenses/MIT")))

    # Build lookup for individual definitions
    ind_lookup = {row["term"]: row for row in glossary if row["category"] == "individual"}

    def _add_individual(name: str, cls: URIRef) -> URIRef:
        uri = PAO[name]
        g.add((uri, RDF.type, OWL.NamedIndividual))
        g.add((uri, RDF.type, cls))
        g.add((uri, RDFS.label, Literal(to_label(name), lang="en")))
        if name in ind_lookup:
            defn = ind_lookup[name].get("definition", "")
            if defn:
                g.add((uri, SKOS.definition, Literal(defn, lang="en")))
        return uri

    # --- Session status individuals ---
    active = _add_individual("Active", PAO.SessionStatus)
    ended = _add_individual("Ended", PAO.SessionStatus)
    interrupted = _add_individual("Interrupted", PAO.SessionStatus)
    _add_all_different(g, [active, ended, interrupted])

    # --- Task status individuals ---
    pending = _add_individual("Pending", PAO.TaskStatus)
    in_progress = _add_individual("InProgress", PAO.TaskStatus)
    completed = _add_individual("Completed", PAO.TaskStatus)
    blocked = _add_individual("Blocked", PAO.TaskStatus)
    _add_all_different(g, [pending, in_progress, completed, blocked])

    # --- Compliance status individuals ---
    compliant = _add_individual("Compliant", PAO.ComplianceStatus)
    non_compliant = _add_individual("NonCompliant", PAO.ComplianceStatus)
    _add_all_different(g, [compliant, non_compliant])

    # --- Agent role individuals ---
    assistant_role = _add_individual("AssistantRole", PAO.AgentRole)
    user_role = _add_individual("UserRole", PAO.AgentRole)
    _add_all_different(g, [assistant_role, user_role])

    # --- Sensitivity level individuals (v0.2.0) ---
    public = _add_individual("Public", PAO.SensitivityLevel)
    internal = _add_individual("Internal", PAO.SensitivityLevel)
    confidential = _add_individual("Confidential", PAO.SensitivityLevel)
    restricted = _add_individual("Restricted", PAO.SensitivityLevel)
    _add_all_different(g, [public, internal, confidential, restricted])

    # --- Item fate individuals (v0.3.0) ---
    preserved = _add_individual("Preserved", PAO.ItemFate)
    dropped = _add_individual("Dropped", PAO.ItemFate)
    summarized = _add_individual("Summarized", PAO.ItemFate)
    archived = _add_individual("Archived", PAO.ItemFate)
    _add_all_different(g, [preserved, dropped, summarized, archived])

    # --- Classifier individuals (used as string property values) ---
    # UserPreference is a reference label, NOT an instance of a domain class.
    for cname in ("UserPreference",):
        uri = PAO[cname]
        g.add((uri, RDF.type, OWL.NamedIndividual))
        g.add((uri, RDFS.label, Literal(to_label(cname), lang="en")))
        if cname in ind_lookup:
            defn = ind_lookup[cname].get("definition", "")
            if defn:
                g.add((uri, SKOS.definition, Literal(defn, lang="en")))

    # --- Enumeration axioms (owl:oneOf) ---
    # These are on the classes, so they go in the TBox conceptually,
    # but individuals must exist first. We add the equivalentClass axioms here
    # since this module is imported by the TBox.
    _add_enumeration(g, PAO.SessionStatus, [active, ended, interrupted])
    _add_enumeration(g, PAO.TaskStatus, [pending, in_progress, completed, blocked])
    _add_enumeration(g, PAO.ComplianceStatus, [compliant, non_compliant])
    _add_enumeration(g, PAO.AgentRole, [assistant_role, user_role])
    _add_enumeration(g, PAO.SensitivityLevel, [public, internal, confidential, restricted])
    _add_enumeration(g, PAO.ItemFate, [preserved, dropped, summarized, archived])

    return g


# ---------------------------------------------------------------------------
# ABox Data Builder (sample individuals for CQ tests)
# ---------------------------------------------------------------------------


def build_abox_data() -> Graph:
    """Build sample ABox data for CQ test execution."""
    g = Graph()
    bind_common_prefixes(g)

    # --- Ontology header ---
    g.add((DATA_IRI, RDF.type, OWL.Ontology))
    g.add((DATA_IRI, OWL.versionIRI, DATA_VERSION_IRI))
    g.add((DATA_IRI, OWL.imports, TBOX_IRI))
    g.add(
        (
            DATA_IRI,
            DCTERMS.title,
            Literal(
                "Personal Agent Ontology — Sample Data",
                lang="en",
            ),
        )
    )
    g.add(
        (
            DATA_IRI,
            DCTERMS.description,
            Literal(
                "Representative ABox individuals for CQ/SPARQL test execution.",
                lang="en",
            ),
        )
    )
    g.add((DATA_IRI, OWL.versionInfo, Literal("0.2.0")))
    g.add((DATA_IRI, DCTERMS.created, Literal("2026-02-19")))
    g.add((DATA_IRI, DCTERMS.creator, Literal("ontology-architect skill")))
    g.add((DATA_IRI, DCTERMS.license, URIRef("https://spdx.org/licenses/MIT")))

    _add_sample_agents(g)
    _add_sample_tools(g)
    _add_sample_conversation(g)
    _add_sample_memory(g)
    _add_sample_planning(g)
    _add_sample_governance(g)
    _add_sample_organization(g)
    _add_sample_persona(g)
    _add_sample_observation(g)
    _add_sample_rehearsal(g)
    _add_sample_memory_block(g)
    _add_sample_intention(g)
    _add_sample_governance_v2(g)
    _add_sample_compaction_trace(g)
    _add_sample_eviction(g)
    _add_sample_session_continuation(g)
    _add_sample_identity(g)
    _add_sample_transitions(g)

    return g


def _add_sample_agents(g: Graph) -> None:
    """Add agent individuals."""
    # AI agent
    claude = PAO.claude_agent
    g.add((claude, RDF.type, PAO.AIAgent))
    g.add((claude, RDF.type, OWL.NamedIndividual))
    g.add((claude, RDFS.label, Literal("Claude", lang="en")))
    g.add((claude, PROV.wasAttributedTo, claude))

    # Human user
    alice = PAO.alice_user
    g.add((alice, RDF.type, PAO.HumanUser))
    g.add((alice, RDF.type, OWL.NamedIndividual))
    g.add((alice, RDFS.label, Literal("Alice", lang="en")))

    # Sub-agent
    sub = PAO.search_subagent
    g.add((sub, RDF.type, PAO.SubAgent))
    g.add((sub, RDF.type, OWL.NamedIndividual))
    g.add((sub, RDFS.label, Literal("search subagent", lang="en")))
    g.add((sub, PAO.spawnedBy, claude))

    # Roles
    g.add((claude, PAO.hasRole, PAO.AssistantRole))
    g.add((alice, PAO.hasRole, PAO.UserRole))


def _add_sample_tools(g: Graph) -> None:
    """Add tool definition and invocation individuals."""
    # Tool definitions
    read_tool = PAO.read_tool
    g.add((read_tool, RDF.type, PAO.ToolDefinition))
    g.add((read_tool, RDF.type, OWL.NamedIndividual))
    g.add((read_tool, RDFS.label, Literal("Read Tool", lang="en")))
    g.add((read_tool, PAO.hasContent, Literal("Read file contents")))

    bash_tool = PAO.bash_tool
    g.add((bash_tool, RDF.type, PAO.ToolDefinition))
    g.add((bash_tool, RDF.type, OWL.NamedIndividual))
    g.add((bash_tool, RDFS.label, Literal("Bash Tool", lang="en")))
    g.add((bash_tool, PAO.hasContent, Literal("Execute shell commands")))

    # Agent has tools
    g.add((PAO.claude_agent, PAO.hasAvailableTool, read_tool))
    g.add((PAO.claude_agent, PAO.hasAvailableTool, bash_tool))

    # Sub-agent has delegated task (will be defined in planning)
    g.add((PAO.search_subagent, PAO.hasAvailableTool, read_tool))


def _add_sample_conversation(g: Graph) -> None:
    """Add conversation, session, turn, message, and compaction individuals."""
    conv = PAO.conv_001
    g.add((conv, RDF.type, PAO.Conversation))
    g.add((conv, RDF.type, OWL.NamedIndividual))
    g.add((conv, RDFS.label, Literal("conversation 001", lang="en")))
    g.add((conv, PAO.hasParticipant, PAO.claude_agent))
    g.add((conv, PAO.hasParticipant, PAO.alice_user))
    g.add((conv, PAO.hasTimestamp, Literal("2026-02-18T10:00:00", datatype=XSD.dateTime)))

    # Qualified association (CQ-004: role in conversation)
    assoc1 = BNode()
    g.add((conv, PROV.qualifiedAssociation, assoc1))
    g.add((assoc1, RDF.type, PROV.Association))
    g.add((assoc1, PROV.agent, PAO.claude_agent))
    g.add((assoc1, PROV.hadRole, PAO.AssistantRole))

    assoc2 = BNode()
    g.add((conv, PROV.qualifiedAssociation, assoc2))
    g.add((assoc2, RDF.type, PROV.Association))
    g.add((assoc2, PROV.agent, PAO.alice_user))
    g.add((assoc2, PROV.hadRole, PAO.UserRole))

    # Session
    sess = PAO.session_001
    g.add((sess, RDF.type, PAO.Session))
    g.add((sess, RDF.type, OWL.NamedIndividual))
    g.add((sess, RDFS.label, Literal("session 001", lang="en")))
    g.add((sess, PAO.partOfConversation, conv))
    g.add((sess, PAO.hasStatus, PAO.Active))
    g.add((sess, PAO.hasParticipant, PAO.alice_user))
    g.add((sess, PAO.hasParticipant, PAO.claude_agent))
    g.add((sess, PAO.hasTimestamp, Literal("2026-02-18T10:00:00", datatype=XSD.dateTime)))

    # Temporal extent for session (CQ-005, CQ-009, CQ-021)
    interval = PAO.session_001_interval
    g.add((interval, RDF.type, TIME.Interval))
    g.add((sess, PAO.hasTemporalExtent, interval))
    begin = PAO.session_001_begin
    g.add((begin, RDF.type, TIME.Instant))
    g.add((begin, TIME.inXSDDateTime, Literal("2026-02-18T10:00:00Z", datatype=XSD.dateTime)))
    end = PAO.session_001_end
    g.add((end, RDF.type, TIME.Instant))
    g.add((end, TIME.inXSDDateTime, Literal("2026-02-18T11:00:00Z", datatype=XSD.dateTime)))
    g.add((interval, TIME.hasBeginning, begin))
    g.add((interval, TIME.hasEnd, end))

    # Second session for CQ-009 (most recent)
    sess2 = PAO.session_002
    g.add((sess2, RDF.type, PAO.Session))
    g.add((sess2, RDF.type, OWL.NamedIndividual))
    g.add((sess2, RDFS.label, Literal("session 002", lang="en")))
    g.add((sess2, PAO.partOfConversation, conv))
    g.add((sess2, PAO.hasStatus, PAO.Ended))
    g.add((sess2, PAO.hasParticipant, PAO.alice_user))
    g.add((sess2, PAO.hasTimestamp, Literal("2026-02-18T12:00:00", datatype=XSD.dateTime)))
    interval2 = PAO.session_002_interval
    g.add((interval2, RDF.type, TIME.Interval))
    g.add((sess2, PAO.hasTemporalExtent, interval2))
    begin2 = PAO.session_002_begin
    g.add((begin2, RDF.type, TIME.Instant))
    g.add((begin2, TIME.inXSDDateTime, Literal("2026-02-18T12:00:00Z", datatype=XSD.dateTime)))
    end2 = PAO.session_002_end
    g.add((end2, RDF.type, TIME.Instant))
    g.add((end2, TIME.inXSDDateTime, Literal("2026-02-18T13:00:00Z", datatype=XSD.dateTime)))
    g.add((interval2, TIME.hasBeginning, begin2))
    g.add((interval2, TIME.hasEnd, end2))

    # Turns (CQ-006)
    turn1 = PAO.turn_001
    g.add((turn1, RDF.type, PAO.Turn))
    g.add((turn1, RDF.type, OWL.NamedIndividual))
    g.add((turn1, RDFS.label, Literal("turn 001", lang="en")))
    g.add((turn1, PAO.partOfSession, sess))
    g.add((turn1, PAO.partOfConversation, conv))
    g.add((turn1, PAO.hasParticipant, PAO.alice_user))
    g.add((turn1, PAO.hasTurnIndex, Literal(0, datatype=XSD.nonNegativeInteger)))
    g.add((turn1, PAO.hasTimestamp, Literal("2026-02-18T10:01:00", datatype=XSD.dateTime)))
    g.add((turn1, PAO.inSession, sess))

    turn2 = PAO.turn_002
    g.add((turn2, RDF.type, PAO.Turn))
    g.add((turn2, RDF.type, OWL.NamedIndividual))
    g.add((turn2, RDFS.label, Literal("turn 002", lang="en")))
    g.add((turn2, PAO.partOfSession, sess))
    g.add((turn2, PAO.partOfConversation, conv))
    g.add((turn2, PAO.hasParticipant, PAO.claude_agent))
    g.add((turn2, PAO.hasTurnIndex, Literal(1, datatype=XSD.nonNegativeInteger)))
    g.add((turn2, PAO.hasTimestamp, Literal("2026-02-18T10:02:00", datatype=XSD.dateTime)))
    g.add((turn2, PAO.inSession, sess))

    # Messages (CQ-006 content)
    msg1 = PAO.msg_001
    g.add((msg1, RDF.type, PAO.Message))
    g.add((msg1, RDF.type, OWL.NamedIndividual))
    g.add((msg1, RDFS.label, Literal("message 001", lang="en")))
    g.add((msg1, PAO.hasContent, Literal("Hello, can you help me?")))
    g.add((msg1, PROV.wasGeneratedBy, turn1))
    g.add((msg1, PROV.wasAttributedTo, PAO.alice_user))
    g.add((msg1, PAO.storedIn, PAO.working_memory_instance))

    msg2 = PAO.msg_002
    g.add((msg2, RDF.type, PAO.Message))
    g.add((msg2, RDF.type, OWL.NamedIndividual))
    g.add((msg2, RDFS.label, Literal("message 002", lang="en")))
    g.add((msg2, PAO.hasContent, Literal("Of course! What do you need?")))
    g.add((msg2, PROV.wasGeneratedBy, turn2))
    g.add((msg2, PROV.wasAttributedTo, PAO.claude_agent))
    g.add((msg2, PAO.storedIn, PAO.working_memory_instance))

    # Tool invocations (CQ-007, CQ-008, CQ-037)
    inv1 = PAO.invocation_001
    g.add((inv1, RDF.type, PAO.ToolInvocation))
    g.add((inv1, RDF.type, OWL.NamedIndividual))
    g.add((inv1, RDFS.label, Literal("tool invocation 001", lang="en")))
    g.add((inv1, PAO.invokesTool, PAO.read_tool))
    g.add((inv1, PAO.invokedBy, PAO.claude_agent))
    g.add((inv1, PAO.performedBy, PAO.claude_agent))
    g.add((inv1, PAO.inSession, sess))
    g.add((inv1, PAO.hasTimestamp, Literal("2026-02-18T10:02:30", datatype=XSD.dateTime)))
    g.add((inv1, PAO.hasComplianceStatus, PAO.Compliant))

    # Input/output for CQ-008
    inv1_input = PAO.invocation_001_input
    g.add((inv1_input, RDF.type, PROV.Entity))
    g.add((inv1_input, RDF.type, OWL.NamedIndividual))
    g.add((inv1_input, RDFS.label, Literal("invocation 001 input", lang="en")))
    g.add((inv1_input, PAO.hasContent, Literal('{"path": "/tmp/test.txt"}')))
    g.add((inv1, PAO.hasInput, inv1_input))

    inv1_output = PAO.invocation_001_output
    g.add((inv1_output, RDF.type, PROV.Entity))
    g.add((inv1_output, RDF.type, OWL.NamedIndividual))
    g.add((inv1_output, RDFS.label, Literal("invocation 001 output", lang="en")))
    g.add((inv1_output, PAO.hasContent, Literal("file contents here")))
    g.add((inv1, PAO.hasOutput, inv1_output))

    # Second invocation for CQ-037 counting
    inv2 = PAO.invocation_002
    g.add((inv2, RDF.type, PAO.ToolInvocation))
    g.add((inv2, RDF.type, OWL.NamedIndividual))
    g.add((inv2, RDFS.label, Literal("tool invocation 002", lang="en")))
    g.add((inv2, PAO.invokesTool, PAO.bash_tool))
    g.add((inv2, PAO.invokedBy, PAO.claude_agent))
    g.add((inv2, PAO.performedBy, PAO.claude_agent))
    g.add((inv2, PAO.inSession, sess))
    g.add((inv2, PAO.hasTimestamp, Literal("2026-02-18T10:03:00", datatype=XSD.dateTime)))
    g.add((inv2, PAO.hasComplianceStatus, PAO.Compliant))

    # Governance links (CQ-031: governedByPolicy)
    g.add((inv1, PAO.governedByPolicy, PAO.policy_001))
    g.add((inv2, PAO.governedByPolicy, PAO.policy_001))

    # CompactionEvent (CQ-010)
    comp = PAO.compaction_001
    g.add((comp, RDF.type, PAO.CompactionEvent))
    g.add((comp, RDF.type, OWL.NamedIndividual))
    g.add((comp, RDFS.label, Literal("compaction event 001", lang="en")))
    g.add((comp, PAO.inConversation, conv))
    g.add((comp, PAO.hasTimestamp, Literal("2026-02-18T10:30:00", datatype=XSD.dateTime)))
    g.add((comp, PAO.producedSummary, PAO.summary_001))

    summary = PAO.summary_001
    g.add((summary, RDF.type, PAO.MemoryItem))
    g.add((summary, RDF.type, OWL.NamedIndividual))
    g.add((summary, RDFS.label, Literal("compaction summary", lang="en")))
    g.add((summary, PAO.hasContent, Literal("Summary of first 10 turns...")))
    g.add((summary, PAO.storedIn, PAO.working_memory_instance))
    g.add((summary, PROV.wasAttributedTo, PAO.claude_agent))
    g.add((summary, PROV.wasGeneratedBy, comp))


def _add_sample_memory(g: Graph) -> None:
    """Add memory tier instances, episodes, claims, and operations."""
    # Memory tier instances (explicit MemoryTier superclass for non-inference SPARQL)
    wm = PAO.working_memory_instance
    g.add((wm, RDF.type, PAO.WorkingMemory))
    g.add((wm, RDF.type, PAO.MemoryTier))
    g.add((wm, RDF.type, OWL.NamedIndividual))
    g.add((wm, RDFS.label, Literal("working memory instance", lang="en")))

    em = PAO.episodic_memory_instance
    g.add((em, RDF.type, PAO.EpisodicMemory))
    g.add((em, RDF.type, PAO.MemoryTier))
    g.add((em, RDF.type, OWL.NamedIndividual))
    g.add((em, RDFS.label, Literal("episodic memory instance", lang="en")))

    sm = PAO.semantic_memory_instance
    g.add((sm, RDF.type, PAO.SemanticMemory))
    g.add((sm, RDF.type, PAO.MemoryTier))
    g.add((sm, RDF.type, OWL.NamedIndividual))
    g.add((sm, RDFS.label, Literal("semantic memory instance", lang="en")))

    pm = PAO.procedural_memory_instance
    g.add((pm, RDF.type, PAO.ProceduralMemory))
    g.add((pm, RDF.type, PAO.MemoryTier))
    g.add((pm, RDF.type, OWL.NamedIndividual))
    g.add((pm, RDFS.label, Literal("procedural memory instance", lang="en")))

    # Episode (CQ-012, CQ-025)
    ep = PAO.episode_001
    g.add((ep, RDF.type, PAO.Episode))
    g.add((ep, RDF.type, PAO.MemoryItem))
    g.add((ep, RDF.type, OWL.NamedIndividual))
    g.add((ep, RDFS.label, Literal("episode 001", lang="en")))
    g.add((ep, PAO.storedIn, em))
    topic = PAO.topic_dark_mode
    g.add((topic, RDF.type, SKOS.Concept))
    g.add((topic, RDFS.label, Literal("dark mode implementation", lang="en")))
    g.add((ep, PAO.hasTopic, topic))
    g.add((ep, PROV.wasAttributedTo, PAO.claude_agent))
    g.add((ep, PROV.wasGeneratedBy, PAO.conv_001))

    # Temporal extent for episode
    ep_interval = PAO.episode_001_interval
    g.add((ep_interval, RDF.type, TIME.Interval))
    g.add((ep, PAO.hasTemporalExtent, ep_interval))
    ep_begin = PAO.episode_001_begin
    g.add((ep_begin, RDF.type, TIME.Instant))
    g.add((ep_begin, TIME.inXSDDateTime, Literal("2026-02-18T10:00:00Z", datatype=XSD.dateTime)))
    ep_end = PAO.episode_001_end
    g.add((ep_end, RDF.type, TIME.Instant))
    g.add((ep_end, TIME.inXSDDateTime, Literal("2026-02-18T10:30:00Z", datatype=XSD.dateTime)))
    g.add((ep_interval, TIME.hasBeginning, ep_begin))
    g.add((ep_interval, TIME.hasEnd, ep_end))

    # Events recorded in episode (CQ-025)
    g.add((PAO.turn_001, PAO.recordedInEpisode, ep))
    g.add((PAO.turn_002, PAO.recordedInEpisode, ep))

    # Claims (CQ-013, CQ-015, CQ-016, CQ-017)
    claim1 = PAO.claim_001
    g.add((claim1, RDF.type, PAO.Claim))
    g.add((claim1, RDF.type, PAO.MemoryItem))
    g.add((claim1, RDF.type, OWL.NamedIndividual))
    g.add((claim1, RDFS.label, Literal("user preference: dark mode", lang="en")))
    g.add((claim1, PAO.hasContent, Literal("User prefers dark mode")))
    g.add((claim1, PAO.hasConfidence, Literal("0.9", datatype=XSD.decimal)))
    g.add((claim1, PAO.claimType, Literal("UserPreference")))
    g.add((claim1, PAO.hasTimestamp, Literal("2026-02-18T10:10:00", datatype=XSD.dateTime)))
    g.add((claim1, PAO.aboutAgent, PAO.alice_user))
    g.add((claim1, PAO.storedIn, sm))
    g.add((claim1, PROV.wasAttributedTo, PAO.claude_agent))
    g.add((claim1, PROV.wasGeneratedBy, PAO.conv_001))
    g.add((claim1, PROV.wasDerivedFrom, ep))
    g.add((claim1, PAO.hasEvidence, ep))

    # Revised claim for CQ-017
    claim2 = PAO.claim_002
    g.add((claim2, RDF.type, PAO.Claim))
    g.add((claim2, RDF.type, PAO.MemoryItem))
    g.add((claim2, RDF.type, OWL.NamedIndividual))
    g.add((claim2, RDFS.label, Literal("user preference: dark mode (revised)", lang="en")))
    g.add((claim2, PAO.hasContent, Literal("User strongly prefers dark mode with high contrast")))
    g.add((claim2, PAO.hasConfidence, Literal("0.95", datatype=XSD.decimal)))
    g.add((claim2, PAO.claimType, Literal("UserPreference")))
    g.add((claim2, PAO.aboutAgent, PAO.alice_user))
    g.add((claim2, PAO.storedIn, sm))
    g.add((claim2, PROV.wasAttributedTo, PAO.claude_agent))
    g.add((claim2, PROV.wasGeneratedBy, PAO.conv_001))
    g.add((claim2, PROV.wasRevisionOf, claim1))
    g.add((claim2, PROV.wasDerivedFrom, claim1))
    g.add((claim2, PAO.hasTimestamp, Literal("2026-02-18T11:00:00", datatype=XSD.dateTime)))

    # Memory operations (CQ-019)
    enc = PAO.encoding_001
    g.add((enc, RDF.type, PAO.Encoding))
    g.add((enc, RDF.type, PAO.MemoryOperation))
    g.add((enc, RDF.type, OWL.NamedIndividual))
    g.add((enc, RDFS.label, Literal("encoding 001", lang="en")))
    g.add((enc, PAO.operatesOn, claim1))
    g.add((enc, PAO.hasTimestamp, Literal("2026-02-18T10:15:00", datatype=XSD.dateTime)))

    ret = PAO.retrieval_001
    g.add((ret, RDF.type, PAO.Retrieval))
    g.add((ret, RDF.type, PAO.MemoryOperation))
    g.add((ret, RDF.type, OWL.NamedIndividual))
    g.add((ret, RDFS.label, Literal("retrieval 001", lang="en")))
    g.add((ret, PAO.operatesOn, claim1))
    g.add((ret, PAO.hasTimestamp, Literal("2026-02-18T10:20:00", datatype=XSD.dateTime)))

    consol = PAO.consolidation_001
    g.add((consol, RDF.type, PAO.Consolidation))
    g.add((consol, RDF.type, PAO.MemoryOperation))
    g.add((consol, RDF.type, OWL.NamedIndividual))
    g.add((consol, RDFS.label, Literal("consolidation 001", lang="en")))
    g.add((consol, PAO.operatesOn, ep))
    g.add((consol, PAO.hasTimestamp, Literal("2026-02-18T10:35:00", datatype=XSD.dateTime)))

    # Derivation chain for CQ-032
    g.add((claim1, PROV.wasDerivedFrom, PAO.msg_001))


def _add_sample_planning(g: Graph) -> None:
    """Add goal, plan, and task individuals."""
    # Goal (CQ-026)
    goal = PAO.goal_001
    g.add((goal, RDF.type, PAO.Goal))
    g.add((goal, RDF.type, OWL.NamedIndividual))
    g.add((goal, RDFS.label, Literal("implement dark mode", lang="en")))
    g.add((goal, PAO.pursuedBy, PAO.claude_agent))
    g.add((goal, PAO.hasStatus, PAO.InProgress))
    g.add((goal, PROV.wasAttributedTo, PAO.alice_user))
    g.add((goal, PAO.storedIn, PAO.semantic_memory_instance))
    g.add((goal, PROV.wasGeneratedBy, PAO.conv_001))

    # Plan (CQ-027, CQ-028)
    plan = PAO.plan_001
    g.add((plan, RDF.type, PAO.Plan))
    g.add((plan, RDF.type, OWL.NamedIndividual))
    g.add((plan, RDFS.label, Literal("dark mode implementation plan", lang="en")))
    g.add((plan, PAO.achievesGoal, goal))
    g.add((plan, PROV.wasAttributedTo, PAO.claude_agent))
    g.add((plan, PAO.storedIn, PAO.semantic_memory_instance))
    g.add((plan, PROV.wasGeneratedBy, PAO.conv_001))

    # Tasks (CQ-027, CQ-029)
    task1 = PAO.task_001
    g.add((task1, RDF.type, PAO.Task))
    g.add((task1, RDF.type, OWL.NamedIndividual))
    g.add((task1, RDFS.label, Literal("update CSS theme", lang="en")))
    g.add((task1, PAO.partOfPlan, plan))
    g.add((task1, PAO.hasStatus, PAO.Completed))
    g.add((task1, PROV.wasAttributedTo, PAO.claude_agent))
    g.add((task1, PAO.storedIn, PAO.semantic_memory_instance))
    g.add((task1, PROV.wasGeneratedBy, PAO.conv_001))

    task2 = PAO.task_002
    g.add((task2, RDF.type, PAO.Task))
    g.add((task2, RDF.type, OWL.NamedIndividual))
    g.add((task2, RDFS.label, Literal("add toggle button", lang="en")))
    g.add((task2, PAO.partOfPlan, plan))
    g.add((task2, PAO.hasStatus, PAO.InProgress))
    g.add((task2, PAO.blockedBy, task1))
    g.add((task2, PROV.wasAttributedTo, PAO.claude_agent))
    g.add((task2, PAO.storedIn, PAO.semantic_memory_instance))
    g.add((task2, PROV.wasGeneratedBy, PAO.conv_001))

    task3 = PAO.task_003
    g.add((task3, RDF.type, PAO.Task))
    g.add((task3, RDF.type, OWL.NamedIndividual))
    g.add((task3, RDFS.label, Literal("write tests", lang="en")))
    g.add((task3, PAO.partOfPlan, plan))
    g.add((task3, PAO.hasStatus, PAO.Blocked))
    g.add((task3, PAO.blockedBy, task2))
    g.add((task3, PROV.wasAttributedTo, PAO.claude_agent))
    g.add((task3, PAO.storedIn, PAO.semantic_memory_instance))
    g.add((task3, PROV.wasGeneratedBy, PAO.conv_001))

    # SubAgent delegated task (CQ-003)
    g.add((PAO.search_subagent, PAO.delegatedTask, task1))


def _add_sample_governance(g: Graph) -> None:
    """Add permission policy, safety constraint, and erasure event individuals."""
    # PermissionPolicy (CQ-030, CQ-039)
    policy = PAO.policy_001
    g.add((policy, RDF.type, PAO.PermissionPolicy))
    g.add((policy, RDF.type, OWL.NamedIndividual))
    g.add((policy, RDFS.label, Literal("file read policy", lang="en")))
    g.add((policy, PAO.appliesTo, PAO.claude_agent))
    g.add((policy, PAO.restrictsToolUse, PAO.bash_tool))
    g.add((policy, PROV.wasAttributedTo, PAO.alice_user))
    g.add((policy, PAO.storedIn, PAO.procedural_memory_instance))
    g.add((policy, PROV.wasGeneratedBy, PAO.conv_001))

    # Permission individual
    perm = PAO.permission_001
    g.add((perm, RDF.type, ODRL.Permission))
    g.add((perm, RDF.type, OWL.NamedIndividual))
    g.add((perm, RDFS.label, Literal("allow file reading", lang="en")))
    g.add((policy, PAO.grantsPermission, perm))

    # SafetyConstraint (CQ-035)
    sc = PAO.safety_001
    g.add((sc, RDF.type, PAO.SafetyConstraint))
    g.add((sc, RDF.type, OWL.NamedIndividual))
    g.add((sc, RDFS.label, Literal("no destructive commands", lang="en")))
    g.add((sc, PAO.appliesTo, PAO.claude_agent))
    g.add((sc, PAO.hasContent, Literal("Never run rm -rf or similar destructive commands")))
    g.add((sc, PROV.wasAttributedTo, PAO.alice_user))
    g.add((sc, PAO.storedIn, PAO.procedural_memory_instance))
    g.add((sc, PROV.wasGeneratedBy, PAO.conv_001))

    # ErasureEvent (CQ-034)
    erasure = PAO.erasure_001
    g.add((erasure, RDF.type, PAO.ErasureEvent))
    g.add((erasure, RDF.type, OWL.NamedIndividual))
    g.add((erasure, RDFS.label, Literal("erasure event 001", lang="en")))
    g.add((erasure, PAO.requestedBy, PAO.alice_user))
    g.add((erasure, PAO.hasTimestamp, Literal("2026-02-18T14:00:00", datatype=XSD.dateTime)))

    # Action for CQ-023 (agent actions in time period)
    action = PAO.action_001
    g.add((action, RDF.type, PAO.Action))
    g.add((action, RDF.type, OWL.NamedIndividual))
    g.add((action, RDFS.label, Literal("action 001", lang="en")))
    g.add((action, PAO.performedBy, PAO.claude_agent))
    g.add((action, PAO.hasTimestamp, Literal("2026-02-18T10:05:00", datatype=XSD.dateTime)))
    g.add((action, PAO.inSession, PAO.session_001))

    # Event for CQ-020, CQ-024
    g.add((PAO.turn_001, PAO.inSession, PAO.session_001))
    g.add((PAO.turn_002, PAO.inSession, PAO.session_001))

    # CQ-036: agent generated memory item through activity
    g.add((PAO.claim_001, PROV.wasGeneratedBy, PAO.conv_001))
    g.add((PAO.conv_001, PROV.wasAssociatedWith, PAO.claude_agent))


def _add_sample_organization(g: Graph) -> None:
    """Add organization and membership data (CQ-041)."""
    org = PAO.acme_corp
    g.add((org, RDF.type, PAO.Organization))
    g.add((org, RDF.type, OWL.NamedIndividual))
    g.add((org, RDFS.label, Literal("Acme Corp", lang="en")))
    g.add((PAO.claude_agent, PAO.belongsTo, org))
    g.add((PAO.alice_user, PAO.belongsTo, org))
    # Explicit inverse for SHACL (SHACL doesn't infer owl:inverseOf)
    g.add((org, PAO.hasMember, PAO.claude_agent))
    g.add((org, PAO.hasMember, PAO.alice_user))


def _add_sample_persona(g: Graph) -> None:
    """Add persona data (CQ-042)."""
    persona = PAO.persona_claude
    g.add((persona, RDF.type, PAO.Persona))
    g.add((persona, RDF.type, OWL.NamedIndividual))
    g.add((persona, RDFS.label, Literal("Claude coding assistant persona", lang="en")))
    g.add((persona, PAO.hasContent, Literal("You are a helpful coding assistant.")))
    g.add((persona, PROV.wasAttributedTo, PAO.alice_user))
    g.add((persona, PAO.storedIn, PAO.procedural_memory_instance))
    g.add((persona, PROV.wasGeneratedBy, PAO.conv_001))
    g.add((PAO.claude_agent, PAO.hasPersona, persona))


def _add_sample_observation(g: Graph) -> None:
    """Add observation data (CQ-043)."""
    obs = PAO.observation_001
    g.add((obs, RDF.type, PAO.Observation))
    g.add((obs, RDF.type, OWL.NamedIndividual))
    g.add((obs, RDFS.label, Literal("observation 001", lang="en")))
    g.add((obs, PAO.inSession, PAO.session_001))
    g.add((obs, PAO.hasTimestamp, Literal("2026-02-18T10:04:00", datatype=XSD.dateTime)))
    g.add((obs, PAO.hasContent, Literal("User appears to prefer concise responses")))


def _add_sample_rehearsal(g: Graph) -> None:
    """Add rehearsal data (CQ-044)."""
    reh = PAO.rehearsal_001
    g.add((reh, RDF.type, PAO.Rehearsal))
    g.add((reh, RDF.type, PAO.MemoryOperation))
    g.add((reh, RDF.type, OWL.NamedIndividual))
    g.add((reh, RDFS.label, Literal("rehearsal 001", lang="en")))
    g.add((reh, PAO.operatesOn, PAO.claim_001))
    g.add((reh, PAO.hasTimestamp, Literal("2026-02-18T10:40:00", datatype=XSD.dateTime)))

    reh2 = PAO.rehearsal_002
    g.add((reh2, RDF.type, PAO.Rehearsal))
    g.add((reh2, RDF.type, PAO.MemoryOperation))
    g.add((reh2, RDF.type, OWL.NamedIndividual))
    g.add((reh2, RDFS.label, Literal("rehearsal 002", lang="en")))
    g.add((reh2, PAO.operatesOn, PAO.claim_001))
    g.add((reh2, PAO.hasTimestamp, Literal("2026-02-18T11:30:00", datatype=XSD.dateTime)))


def _add_sample_memory_block(g: Graph) -> None:
    """Add memory block data (CQ-045)."""
    block = PAO.memory_block_001
    g.add((block, RDF.type, PAO.MemoryBlock))
    g.add((block, RDF.type, PAO.MemoryItem))
    g.add((block, RDF.type, OWL.NamedIndividual))
    g.add((block, RDFS.label, Literal("core memory block", lang="en")))
    g.add((block, PAO.hasBlockKey, Literal("user_name")))
    g.add((block, PAO.hasBlockValue, Literal("Alice")))
    g.add((block, PAO.storedIn, PAO.working_memory_instance))
    g.add((block, PROV.wasAttributedTo, PAO.claude_agent))
    g.add((block, PROV.wasGeneratedBy, PAO.conv_001))
    g.add((block, PAO.hasSensitivityLevel, PAO.Internal))


def _add_sample_intention(g: Graph) -> None:
    """Add intention data (CQ-046, CQ-047)."""
    intention = PAO.intention_001
    g.add((intention, RDF.type, PAO.Intention))
    g.add((intention, RDF.type, OWL.NamedIndividual))
    g.add((intention, RDFS.label, Literal("implement dark mode intention", lang="en")))
    g.add((intention, PAO.intendedBy, PAO.claude_agent))
    g.add((intention, PAO.derivedFromGoal, PAO.goal_001))
    g.add((intention, PROV.wasAttributedTo, PAO.claude_agent))
    g.add((intention, PAO.storedIn, PAO.semantic_memory_instance))
    g.add((intention, PROV.wasGeneratedBy, PAO.conv_001))


def _add_sample_governance_v2(g: Graph) -> None:
    """Add v0.2.0 governance data: consent, retention, migrated sensitivity (CQ-048--CQ-051)."""
    # Migrate existing sensitivity levels from strings to individuals
    # Update claim_001 and claim_002 to use SensitivityLevel individuals
    # (The old string literals are replaced by adding the object property)
    g.add((PAO.claim_001, PAO.hasSensitivityLevel, PAO.Confidential))
    g.add((PAO.claim_002, PAO.hasSensitivityLevel, PAO.Confidential))
    g.add((PAO.summary_001, PAO.hasSensitivityLevel, PAO.Public))

    # ConsentRecord (CQ-049)
    consent = PAO.consent_001
    g.add((consent, RDF.type, PAO.ConsentRecord))
    g.add((consent, RDF.type, OWL.NamedIndividual))
    g.add((consent, RDFS.label, Literal("memory storage consent", lang="en")))
    g.add((consent, PAO.consentSubject, PAO.alice_user))
    # Purpose: memory storage (using a generic entity as purpose)
    purpose = PAO.purpose_memory_storage
    g.add((purpose, RDF.type, PROV.Entity))
    g.add((purpose, RDF.type, OWL.NamedIndividual))
    g.add((purpose, RDFS.label, Literal("memory storage", lang="en")))
    g.add((consent, PAO.consentPurpose, purpose))
    g.add((consent, PROV.wasAttributedTo, PAO.alice_user))
    g.add((consent, PAO.storedIn, PAO.procedural_memory_instance))
    g.add((consent, PROV.wasGeneratedBy, PAO.conv_001))

    # RetentionPolicy (CQ-050, CQ-051)
    retention = PAO.retention_policy_30day
    g.add((retention, RDF.type, PAO.RetentionPolicy))
    g.add((retention, RDF.type, OWL.NamedIndividual))
    g.add((retention, RDFS.label, Literal("30-day retention policy", lang="en")))
    g.add((retention, PAO.retentionPeriodDays, Literal(30, datatype=XSD.nonNegativeInteger)))
    g.add((retention, PROV.wasAttributedTo, PAO.alice_user))
    g.add((retention, PAO.storedIn, PAO.procedural_memory_instance))
    g.add((retention, PROV.wasGeneratedBy, PAO.conv_001))

    # Link memory items to retention policy
    g.add((PAO.claim_001, PAO.governedByRetention, retention))
    g.add((PAO.claim_002, PAO.governedByRetention, retention))

    # Expired item for CQ-051 (old timestamp that exceeds 30-day retention)
    expired = PAO.expired_memory_001
    g.add((expired, RDF.type, PAO.MemoryItem))
    g.add((expired, RDF.type, OWL.NamedIndividual))
    g.add((expired, RDFS.label, Literal("expired memory item", lang="en")))
    g.add((expired, PAO.hasContent, Literal("Old data that should be deleted")))
    g.add((expired, PAO.storedIn, PAO.semantic_memory_instance))
    g.add((expired, PROV.wasAttributedTo, PAO.claude_agent))
    g.add((expired, PROV.wasGeneratedBy, PAO.conv_001))
    g.add((expired, PAO.hasSensitivityLevel, PAO.Restricted))
    g.add((expired, PAO.governedByRetention, retention))
    # Timestamp 60 days ago to ensure it's expired under 30-day policy
    g.add((expired, PAO.hasTimestamp, Literal("2025-12-20T10:00:00", datatype=XSD.dateTime)))


def _add_sample_compaction_trace(g: Graph) -> None:
    """Add compaction trace data linking items to preservation/drop fates (CQ-052, CQ-053)."""
    compaction = PAO.compaction_001  # existing individual
    # Mark items as compacted inputs
    g.add((compaction, PAO.compactedItem, PAO.turn_001))
    g.add((compaction, PAO.compactedItem, PAO.turn_002))
    g.add((compaction, PAO.compactedItem, PAO.claim_001))
    # Dropped items: invalidated by compaction
    g.add((PAO.turn_001, PROV.wasInvalidatedBy, compaction))
    g.add((PAO.turn_002, PROV.wasInvalidatedBy, compaction))
    # Preserved item: derived into summary
    g.add((PAO.summary_001, PROV.wasDerivedFrom, PAO.claim_001))
    # Dispositions with metadata
    disp1 = PAO.disp_turn_001
    g.add((disp1, RDF.type, PAO.CompactionDisposition))
    g.add((disp1, RDF.type, OWL.NamedIndividual))
    g.add((disp1, RDFS.label, Literal("disposition of turn 001", lang="en")))
    g.add((disp1, PAO.dispositionOf, PAO.turn_001))
    g.add((disp1, PAO.hasItemFate, PAO.Dropped))
    g.add((disp1, PAO.fateReason, Literal("Low relevance to active goals")))
    g.add((compaction, PAO.hasCompactionDisposition, disp1))
    disp2 = PAO.disp_claim_001
    g.add((disp2, RDF.type, PAO.CompactionDisposition))
    g.add((disp2, RDF.type, OWL.NamedIndividual))
    g.add((disp2, RDFS.label, Literal("disposition of claim 001", lang="en")))
    g.add((disp2, PAO.dispositionOf, PAO.claim_001))
    g.add((disp2, PAO.hasItemFate, PAO.Preserved))
    g.add((disp2, PAO.fateReason, Literal("Active user preference")))
    g.add((compaction, PAO.hasCompactionDisposition, disp2))


def _add_sample_eviction(g: Graph) -> None:
    """Add last-access timestamps and eviction candidacy to memory items (CQ-054, CQ-055)."""
    g.add(
        (
            PAO.claim_001,
            PAO.hasLastAccessTime,
            Literal("2026-02-19T08:00:00Z", datatype=XSD.dateTime),
        )
    )
    g.add((PAO.claim_001, PAO.isEvictionCandidate, Literal(False)))
    g.add(
        (
            PAO.episode_001,
            PAO.hasLastAccessTime,
            Literal("2025-01-15T10:00:00Z", datatype=XSD.dateTime),
        )
    )
    g.add((PAO.episode_001, PAO.isEvictionCandidate, Literal(True)))


def _add_sample_session_continuation(g: Graph) -> None:
    """Link sessions in a continuation chain (CQ-056)."""
    g.add((PAO.session_002, PAO.continuedFrom, PAO.session_001))
    g.add((PAO.session_001, PAO.continuedBy, PAO.session_002))


def _add_sample_identity(g: Graph) -> None:
    """Add unique identifiers to key entities (CQ-057)."""
    g.add((PAO.claude_agent, PAO.hasAgentId, Literal("agent-claude-001")))
    g.add((PAO.session_001, PAO.hasSessionId, Literal("sess-001")))
    g.add((PAO.session_002, PAO.hasSessionId, Literal("sess-002")))
    g.add((PAO.conv_001, PAO.hasConversationId, Literal("conv-001")))


def _add_sample_transitions(g: Graph) -> None:
    """Add sample status transition chains (CQ-058, CQ-059, CQ-060)."""
    # Task transitions: Pending -> InProgress -> Completed
    tt1 = PAO.task_transition_001
    g.add((tt1, RDF.type, PAO.TaskStatusTransition))
    g.add((tt1, RDF.type, OWL.NamedIndividual))
    g.add((tt1, RDFS.label, Literal("task transition 001", lang="en")))
    g.add((tt1, PAO.transitionSubject, PAO.task_001))
    g.add((tt1, PAO.fromStatus, PAO.Pending))
    g.add((tt1, PAO.toStatus, PAO.InProgress))
    g.add((tt1, PAO.hasTimestamp, Literal("2026-02-19T10:00:00Z", datatype=XSD.dateTime)))
    tt2 = PAO.task_transition_002
    g.add((tt2, RDF.type, PAO.TaskStatusTransition))
    g.add((tt2, RDF.type, OWL.NamedIndividual))
    g.add((tt2, RDFS.label, Literal("task transition 002", lang="en")))
    g.add((tt2, PAO.transitionSubject, PAO.task_001))
    g.add((tt2, PAO.fromStatus, PAO.InProgress))
    g.add((tt2, PAO.toStatus, PAO.Completed))
    g.add((tt2, PAO.hasTimestamp, Literal("2026-02-19T11:30:00Z", datatype=XSD.dateTime)))
    g.add((tt1, PAO.nextTransition, tt2))
    g.add((tt2, PAO.previousTransition, tt1))
    # Session transition: Active -> Ended
    st1 = PAO.session_transition_001
    g.add((st1, RDF.type, PAO.SessionStatusTransition))
    g.add((st1, RDF.type, OWL.NamedIndividual))
    g.add((st1, RDFS.label, Literal("session transition 001", lang="en")))
    g.add((st1, PAO.transitionSubject, PAO.session_001))
    g.add((st1, PAO.fromStatus, PAO.Active))
    g.add((st1, PAO.toStatus, PAO.Ended))
    g.add((st1, PAO.hasTimestamp, Literal("2026-02-19T12:00:00Z", datatype=XSD.dateTime)))
    g.add((st1, PAO.triggeredBy, PAO.compaction_001))


# ---------------------------------------------------------------------------
# SHACL Shapes Builder
# ---------------------------------------------------------------------------


def build_shacl_shapes() -> Graph:
    """Build SHACL shapes for structural validation."""
    g = Graph()
    bind_common_prefixes(g)
    bind_shacl_prefix(g)

    # --- SubAgentShape ---
    _add_shape(
        g,
        PAO.SubAgentShape,
        PAO.SubAgent,
        [
            _property_shape(g, PAO.spawnedBy, min_count=1, max_count=1, class_constraint=PAO.Agent),
        ],
    )

    # --- AIAgentShape ---
    _add_shape(
        g,
        PAO.AIAgentShape,
        PAO.AIAgent,
        [
            _property_shape(
                g, PAO.hasAvailableTool, min_count=1, class_constraint=PAO.ToolDefinition
            ),
        ],
    )

    # --- ConversationShape ---
    _add_shape(
        g,
        PAO.ConversationShape,
        PAO.Conversation,
        [
            _property_shape(g, PAO.hasParticipant, min_count=1, class_constraint=PAO.Agent),
        ],
    )

    # --- SessionShape ---
    _add_shape(
        g,
        PAO.SessionShape,
        PAO.Session,
        [
            _property_shape(
                g,
                PAO.partOfConversation,
                min_count=1,
                max_count=1,
                class_constraint=PAO.Conversation,
            ),
            _property_shape(
                g, PAO.hasStatus, min_count=1, max_count=1, class_constraint=PAO.SessionStatus
            ),
        ],
    )

    # --- TurnShape ---
    _add_shape(
        g,
        PAO.TurnShape,
        PAO.Turn,
        [
            _property_shape(
                g, PAO.partOfSession, min_count=1, max_count=1, class_constraint=PAO.Session
            ),
            _property_shape(
                g, PAO.hasTurnIndex, min_count=1, max_count=1, datatype=XSD.nonNegativeInteger
            ),
        ],
    )

    # --- ToolInvocationShape ---
    _add_shape(
        g,
        PAO.ToolInvocationShape,
        PAO.ToolInvocation,
        [
            _property_shape(
                g, PAO.invokesTool, min_count=1, max_count=1, class_constraint=PAO.ToolDefinition
            ),
            _property_shape(g, PAO.invokedBy, min_count=1, max_count=1, class_constraint=PAO.Agent),
        ],
    )

    # --- ActionShape ---
    _add_shape(
        g,
        PAO.ActionShape,
        PAO.Action,
        [
            _property_shape(
                g, PAO.performedBy, min_count=1, max_count=1, class_constraint=PAO.Agent
            ),
        ],
    )

    # --- ClaimShape ---
    _add_shape(
        g,
        PAO.ClaimShape,
        PAO.Claim,
        [
            _property_shape(g, PAO.hasContent, min_count=1, max_count=1, datatype=XSD.string),
            _property_shape(
                g,
                PAO.hasConfidence,
                min_count=0,
                max_count=1,
                datatype=XSD.decimal,
                min_inclusive="0.0",
                max_inclusive="1.0",
            ),
        ],
    )

    # --- TaskShape ---
    _add_shape(
        g,
        PAO.TaskShape,
        PAO.Task,
        [
            _property_shape(g, PAO.partOfPlan, min_count=1, max_count=1, class_constraint=PAO.Plan),
            _property_shape(
                g, PAO.hasStatus, min_count=1, max_count=1, class_constraint=PAO.TaskStatus
            ),
        ],
    )

    # --- PlanShape ---
    _add_shape(
        g,
        PAO.PlanShape,
        PAO.Plan,
        [
            _property_shape(g, PAO.achievesGoal, min_count=1, class_constraint=PAO.Goal),
        ],
    )

    # --- MemoryOperationShape ---
    _add_shape(
        g,
        PAO.MemoryOperationShape,
        PAO.MemoryOperation,
        [
            _property_shape(g, PAO.operatesOn, min_count=1, class_constraint=PAO.MemoryItem),
        ],
    )

    # --- ErasureEventShape ---
    _add_shape(
        g,
        PAO.ErasureEventShape,
        PAO.ErasureEvent,
        [
            _property_shape(
                g, PAO.requestedBy, min_count=1, max_count=1, class_constraint=PAO.Agent
            ),
        ],
    )

    # --- OrganizationShape (v0.2.0) ---
    _add_shape(
        g,
        PAO.OrganizationShape,
        PAO.Organization,
        [
            _property_shape(g, PAO.hasMember, min_count=1, class_constraint=PAO.Agent),
        ],
    )

    # --- ObservationShape (v0.2.0) ---
    _add_shape(
        g,
        PAO.ObservationShape,
        PAO.Observation,
        [
            _property_shape(
                g, PAO.inSession, min_count=1, max_count=1, class_constraint=PAO.Session
            ),
        ],
    )

    # --- MemoryBlockShape (v0.2.0) ---
    _add_shape(
        g,
        PAO.MemoryBlockShape,
        PAO.MemoryBlock,
        [
            _property_shape(g, PAO.hasBlockKey, min_count=1, datatype=XSD.string),
            _property_shape(g, PAO.hasBlockValue, min_count=1, datatype=XSD.string),
        ],
    )

    # --- IntentionShape (v0.2.0) ---
    _add_shape(
        g,
        PAO.IntentionShape,
        PAO.Intention,
        [
            _property_shape(g, PAO.intendedBy, min_count=1, class_constraint=PAO.Agent),
            _property_shape(g, PAO.derivedFromGoal, min_count=1, class_constraint=PAO.Goal),
        ],
    )

    # --- ConsentRecordShape (v0.2.0) ---
    _add_shape(
        g,
        PAO.ConsentRecordShape,
        PAO.ConsentRecord,
        [
            _property_shape(
                g, PAO.consentSubject, min_count=1, max_count=1, class_constraint=PAO.Agent
            ),
        ],
    )

    # --- RetentionPolicyShape (v0.2.0) ---
    _add_shape(
        g,
        PAO.RetentionPolicyShape,
        PAO.RetentionPolicy,
        [
            _property_shape(
                g,
                PAO.retentionPeriodDays,
                min_count=1,
                max_count=1,
                datatype=XSD.nonNegativeInteger,
            ),
        ],
    )

    # --- GoalShape (v0.2.0) ---
    _add_shape(
        g,
        PAO.GoalShape,
        PAO.Goal,
        [
            _property_shape(g, PAO.pursuedBy, min_count=1, class_constraint=PAO.Agent),
            _property_shape(
                g, PAO.hasStatus, min_count=1, max_count=1, class_constraint=PAO.TaskStatus
            ),
        ],
    )

    # --- MemoryItemShape (v0.2.0) ---
    _add_shape(
        g,
        PAO.MemoryItemShape,
        PAO.MemoryItem,
        [
            _property_shape(
                g, PAO.storedIn, min_count=1, max_count=1, class_constraint=PAO.MemoryTier
            ),
            _property_shape(
                g,
                PAO.hasSensitivityLevel,
                min_count=0,
                max_count=1,
                class_constraint=PAO.SensitivityLevel,
            ),
            _property_shape(g, PAO.hasLastAccessTime, max_count=1, datatype=XSD.dateTime),
        ],
    )

    # --- EpisodeShape (v0.2.0) ---
    _add_shape(
        g,
        PAO.EpisodeShape,
        PAO.Episode,
        [
            _property_shape(g, PAO.hasTemporalExtent, min_count=1),
            _property_shape(g, PAO.hasTopic, min_count=1),
        ],
    )

    # --- CompactionEventShape (v0.2.0) ---
    _add_shape(
        g,
        PAO.CompactionEventShape,
        PAO.CompactionEvent,
        [
            _property_shape(g, PAO.producedSummary, min_count=1, class_constraint=PAO.MemoryItem),
        ],
    )

    # --- MessageShape (v0.2.0) ---
    _add_shape(
        g,
        PAO.MessageShape,
        PAO.Message,
        [
            _property_shape(g, PAO.hasContent, min_count=1, max_count=1, datatype=XSD.string),
        ],
    )

    # --- PersonaShape (v0.2.0) ---
    _add_shape(
        g,
        PAO.PersonaShape,
        PAO.Persona,
        [
            _property_shape(g, PAO.hasContent, min_count=1, max_count=1, datatype=XSD.string),
        ],
    )

    # --- StatusTransitionShape (v0.3.0) ---
    _add_shape(
        g,
        PAO.StatusTransitionShape,
        PAO.StatusTransition,
        [
            _property_shape(
                g, PAO.fromStatus, min_count=1, max_count=1, class_constraint=PAO.Status
            ),
            _property_shape(g, PAO.toStatus, min_count=1, max_count=1, class_constraint=PAO.Status),
            _property_shape(g, PAO.transitionSubject, min_count=1, max_count=1),
        ],
    )

    # --- CompactionDispositionShape (v0.3.0) ---
    _add_shape(
        g,
        PAO.CompactionDispositionShape,
        PAO.CompactionDisposition,
        [
            _property_shape(g, PAO.dispositionOf, min_count=1, max_count=1),
            _property_shape(
                g, PAO.hasItemFate, min_count=1, max_count=1, class_constraint=PAO.ItemFate
            ),
        ],
    )

    return g


def _add_shape(g: Graph, shape_uri: URIRef, target_class: URIRef, prop_shapes: list[BNode]) -> None:
    """Add a NodeShape targeting a class with property constraints."""
    g.add((shape_uri, RDF.type, SH.NodeShape))
    g.add((shape_uri, SH.targetClass, target_class))
    for ps in prop_shapes:
        g.add((shape_uri, SH.property, ps))


def _property_shape(
    g: Graph,
    path: URIRef,
    min_count: int | None = None,
    max_count: int | None = None,
    datatype: URIRef | None = None,
    class_constraint: URIRef | None = None,
    min_inclusive: str | None = None,
    max_inclusive: str | None = None,
) -> BNode:
    """Create a property shape with optional constraints."""
    ps = BNode()
    g.add((ps, SH.path, path))
    if min_count is not None:
        g.add((ps, SH.minCount, Literal(min_count)))
    if max_count is not None:
        g.add((ps, SH.maxCount, Literal(max_count)))
    if datatype is not None:
        g.add((ps, SH.datatype, datatype))
    if class_constraint is not None:
        g.add((ps, SH["class"], class_constraint))
    if min_inclusive is not None:
        g.add((ps, SH.minInclusive, Literal(min_inclusive, datatype=XSD.decimal)))
    if max_inclusive is not None:
        g.add((ps, SH.maxInclusive, Literal(max_inclusive, datatype=XSD.decimal)))
    return ps


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Build all Personal Agent Ontology artifacts."""
    print("Loading input artifacts...")
    glossary = load_glossary()

    class_count = sum(1 for r in glossary if r["category"] == "class")
    ind_count = sum(1 for r in glossary if r["category"] == "individual")
    print(f"  Glossary: {len(glossary)} terms ({class_count} classes, {ind_count} individuals)")

    # Ensure output directories exist
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "shapes").mkdir(parents=True, exist_ok=True)

    # Build Reference Individuals (must come first since TBox imports it)
    print("\nBuilding reference individuals (pao-reference-individuals.ttl)...")
    ref = build_reference_individuals(glossary)
    ref_path = OUT / "pao-reference-individuals.ttl"
    ref.serialize(destination=str(ref_path), format="turtle")
    print(f"  Written: {ref_path} ({len(ref)} triples)")

    # Build TBox
    print("Building TBox (personal_agent_ontology.ttl)...")
    tbox = build_tbox(glossary)
    tbox_path = OUT / "personal_agent_ontology.ttl"
    tbox.serialize(destination=str(tbox_path), format="turtle")
    print(f"  Written: {tbox_path} ({len(tbox)} triples)")

    # Build SHACL Shapes
    print("Building SHACL shapes (shapes/pao-shapes.ttl)...")
    shapes = build_shacl_shapes()
    shapes_path = OUT / "shapes" / "pao-shapes.ttl"
    shapes.serialize(destination=str(shapes_path), format="turtle")
    print(f"  Written: {shapes_path} ({len(shapes)} triples)")

    # Build sample ABox data
    print("Building sample ABox data (pao-data.ttl)...")
    data = build_abox_data()
    data_path = OUT / "pao-data.ttl"
    data.serialize(destination=str(data_path), format="turtle")
    print(f"  Written: {data_path} ({len(data)} triples)")

    print("\nBuild complete.")


if __name__ == "__main__":
    main()
