# BFO Alignment -- Personal Agent Ontology (PAO)

**Date**: 2026-02-18
**Phase**: Conceptualization (Pipeline A, Step 3)
**Upper Ontology**: BFO 2020 (ISO 21838-2)

---

## Alignment Strategy

Every top-level PAO class is aligned to a BFO category using the decision
procedure from `_shared/bfo-categories.md`. Where a class cross-cuts BFO
categories, the alignment rationale is documented and a pragmatic resolution
is provided.

PAO imports PROV-O, which is not itself BFO-aligned. Where PROV-O classes
serve as PAO superclasses, we document the BFO alignment of the PAO class
independently and note the PROV-O relationship.

---

## Category Summary

| BFO Category | PAO Classes |
|---|---|
| Object (BFO:0000030) | HumanUser |
| Generically Dependent Continuant (BFO:0000031) | AIAgent, SubAgent, ToolDefinition, Message, MemoryItem, MemoryTier, WorkingMemory, EpisodicMemory, SemanticMemory, ProceduralMemory, Episode, Claim, Goal, Plan, Task, PermissionPolicy, SafetyConstraint |
| Role (BFO:0000023) | AgentRole |
| Process (BFO:0000015) | Conversation, Session, Turn, ToolInvocation, CompactionEvent, ErasureEvent, Event, Action, MemoryOperation, Encoding, Retrieval, Consolidation, Forgetting |
| Cross-cutting (documented) | Agent (umbrella for Object + GDC subtypes) |
| Value Partition (no BFO parent) | Status, SessionStatus, TaskStatus, ComplianceStatus |
| Named Individuals | Active, Ended, Interrupted, Pending, InProgress, Completed, Blocked, Compliant, NonCompliant, AssistantRole, UserRole, UserPreference, PersonalData |

---

## Detailed Alignment Decisions

### 1. Agent (cross-cutting)

**Decision**: Agent is a domain-level umbrella class aligned with `prov:Agent`.
It cross-cuts BFO categories because its subclasses span both Material Entity
(humans) and GDC (software).

**Rationale**: BFO does not have a native "agent" category. The concept of
agency cross-cuts the continuant/occurrent divide. PROV-O defines `prov:Agent`
as "something that bears some form of responsibility for an activity taking
place," which is the semantics PAO needs.

**Resolution**:
- `pao:Agent rdfs:subClassOf prov:Agent`
- BFO alignment is provided at the subclass level (HumanUser, AIAgent)
- Agent itself is not directly subclassed under a single BFO leaf category
- This is a documented deviation from strict BFO single-inheritance,
  justified by the need for a unified agent concept in the domain

**Alternative considered**: Model Agent as a Role (BFO:0000023) borne by
material entities or GDCs. Rejected because it would require all CQs to
query through a role indirection, adding unnecessary complexity.

---

### 2. HumanUser -> Object (BFO:0000030)

**Decision**: Material Entity > Object

**Rationale**: A human user is a physical person -- a maximally self-connected
material entity that persists through time. Aligns with `prov:Person` and
`foaf:Person`.

**Decision path**: Continuant > Independent Continuant > Material Entity >
Object.

---

### 3. AIAgent -> Generically Dependent Continuant (BFO:0000031)

**Decision**: GDC (information content entity)

**Rationale**: A software agent is an information artifact -- it can be
copied, transferred between hardware, and exists as pattern rather than
matter. Per the BFO known ambiguities table: "Software, algorithms: GDC
(information content entity pattern)."

**Decision path**: Continuant > Dependent Continuant > GDC.

**Note**: The AI agent depends on computational infrastructure (its bearer)
for execution, but its identity as an information entity is independent of
any specific hardware instance.

---

### 4. SubAgent -> Generically Dependent Continuant (BFO:0000031)

**Decision**: GDC, same as AIAgent.

**Rationale**: A sub-agent is a specialized AI agent spawned for delegated
work. It inherits the GDC classification from AIAgent.

---

### 5. AgentRole -> Role (BFO:0000023)

**Decision**: Specifically Dependent Continuant > Realizable Entity > Role

**Rationale**: A role played by an agent in a conversation is a social/
contextual property. It exists because of the conversational context, not
because of the agent's physical or informational makeup. An agent can play
different roles in different conversations.

**Decision path**: Continuant > Dependent > SDC > Realizable > Role.

**Individuals**: `AssistantRole` and `UserRole` are named individuals of
type `AgentRole`, forming a closed set via `owl:oneOf`.

---

### 6. ToolDefinition -> Generically Dependent Continuant (BFO:0000031)

**Decision**: GDC

**Rationale**: A tool definition is an information artifact that specifies
the interface, capabilities, and constraints of an available tool. It can
be shared, copied, and versioned independently of the tool implementation.

---

### 7. Conversation -> Process (BFO:0000015)

**Decision**: Occurrent > Process

**Rationale**: A conversation unfolds over time, has temporal parts (sessions,
turns), and involves participants. It does not persist as a continuant --
it happens.

**Decision path**: Occurrent > Process.

**Note**: A conversation has participants (agents) who are continuants.
The `participates_in` relation (RO:0000056) links continuants to processes.

---

### 8. Session -> Process (BFO:0000015)

**Decision**: Process (temporal part of a Conversation)

**Rationale**: A session is a bounded period of agent-user interaction.
It unfolds in time, has beginning and end points, and is a temporal part
of a conversation.

---

### 9. Turn -> Process (BFO:0000015)

**Decision**: Process (temporal part of a Session)

**Rationale**: A turn is a single contribution by one participant. It is
an event with temporal extent (however brief) and is a proper temporal part
of a session.

---

### 10. Message -> Generically Dependent Continuant (BFO:0000031)

**Decision**: GDC

**Rationale**: A message is the information content of a turn. It can be
stored, copied, and transmitted. The message content (GDC) is distinct from
the turn (Process) that produced it. This follows the information-physical
distinction (anti-pattern #7).

---

### 11. ToolInvocation -> Process (BFO:0000015)

**Decision**: Process

**Rationale**: A tool invocation unfolds in time: request is issued,
execution occurs, response is returned. It has temporal parts and
participants (the invoking agent, the tool definition).

---

### 12. CompactionEvent -> Process (BFO:0000015)

**Decision**: Process

**Rationale**: Context compaction is something that happens -- the agent's
working memory is compressed, producing a summary. It has a start, duration,
and end.

---

### 13. MemoryItem -> Generically Dependent Continuant (BFO:0000031)

**Decision**: GDC

**Rationale**: Memory items are information artifacts persisted in agent
memory. They can be stored, copied, consolidated, and deleted. This aligns
with the IAO pattern (ODP-4: Information Realization) and BFO's treatment
of information entities as GDCs.

**Note**: The `storedIn` property links MemoryItem (GDC) to MemoryTier
(GDC), modeling the realization/bearer relationship from ODP-4.

---

### 14. MemoryTier -> Generically Dependent Continuant (BFO:0000031)

**Decision**: GDC

**Rationale**: A memory tier is an information structure that defines
storage, access, and lifecycle characteristics for a layer of the agent's
memory architecture. It is a specification/schema, not a physical entity.

**Subclasses**: WorkingMemory, EpisodicMemory, SemanticMemory,
ProceduralMemory -- all GDCs, forming a disjoint covering of MemoryTier.

---

### 15. Episode -> Generically Dependent Continuant (BFO:0000031)

**Decision**: GDC (subclass of MemoryItem)

**Rationale**: In PAO, an Episode is primarily a memory artifact that
records a temporally bounded cluster of related events. The pre-glossary
noted dual nature ("subclass of MemoryItem and Event"), but in BFO,
GDC (Continuant) and Process (Occurrent) are disjoint -- a class cannot
be both.

**Resolution**: Episode is a GDC (memory item). It records events but is
not itself an event. The temporal metadata (when the recorded events
occurred) is attached via `hasTemporalExtent` as descriptive metadata, not
as an ontological commitment to being a process.

**Consequence**: The property linking events to episodes is `recordedInEpisode`
(Event -> Episode), not mereological `partOf`. Events are processes that
the episode describes; the episode is the information record.

**Alternative considered**: Dual-nature (Process + GDC). Rejected because
it violates BFO disjointness between Continuant and Occurrent.

---

### 16. Claim -> Generically Dependent Continuant (BFO:0000031)

**Decision**: GDC (subclass of MemoryItem)

**Rationale**: A claim is an agent-held proposition -- an information
artifact with metadata (confidence, evidence, provenance). It follows the
N-ary Relation pattern (ODP-1) and the Information Realization pattern
(ODP-4).

---

### 17. MemoryOperation -> Process (BFO:0000015)

**Decision**: Process

**Rationale**: Memory operations (encoding, retrieval, consolidation,
forgetting) are things that happen over time. They transform or access
memory items.

**Subclasses**: Encoding, Retrieval, Consolidation, Forgetting -- all
Processes, forming a disjoint covering of MemoryOperation.

---

### 18. Event -> Process (BFO:0000015)

**Decision**: Process

**Rationale**: BFO uses "Process" for what many domain vocabularies call
"Event." In PAO, Event is the top-level class for all things that happen
in the agent system. It aligns directly with BFO:Process.

**Note**: PAO uses the label "Event" rather than "Process" to match
domain vocabulary (agent developers think in terms of "events"). The
`rdfs:label` is "event" but the BFO alignment is to Process.

---

### 19. Action -> Process (BFO:0000015)

**Decision**: Process (subclass of Event)

**Rationale**: An action is an intentional event caused by an agent. It
is a process with a designated agent participant. Aligns with schema:Action
via SSSOM mapping.

---

### 20. Goal -> Generically Dependent Continuant (BFO:0000031)

**Decision**: GDC

**Rationale**: In PAO, a goal is an information content entity specifying a
desired state the agent works toward. It can be created, modified, shared,
and tracked.

**Alternative considered**: Realizable Entity (BFO:0000017), as suggested
in the ORSD. A goal-as-disposition would be an SDC that gets realized through
plan execution. However, BFO Realizable Entities inhere in Independent
Continuants, and software agents are GDCs -- SDCs cannot inhere in GDCs.
The GDC classification avoids this category mismatch while still capturing
the goal's information content nature.

**Note**: The intentional/motivational aspect of goals (BDI "desire") is
captured through the `pursuedBy` relation and `hasStatus` property, not
through the BFO categorization.

---

### 21. Plan -> Generically Dependent Continuant (BFO:0000031)

**Decision**: GDC

**Rationale**: A plan is an information artifact specifying an ordered
sequence of intended actions. Aligns with `prov:Plan` (which is a subclass
of `prov:Entity`). Plans are documents/specifications, not the execution of
those specifications.

---

### 22. Task -> Generically Dependent Continuant (BFO:0000031)

**Decision**: GDC

**Rationale**: A task is a concrete work item specification within a plan.
It has status, dependencies, and descriptive content. It is the specification
of work to be done, not the doing itself.

---

### 23. PermissionPolicy -> Generically Dependent Continuant (BFO:0000031)

**Decision**: GDC

**Rationale**: A permission policy is an information artifact (a rule
document) governing agent behavior. Aligns with ODRL `odrl:Policy`.

---

### 24. SafetyConstraint -> Generically Dependent Continuant (BFO:0000031)

**Decision**: GDC

**Rationale**: A safety constraint is an information artifact specifying
non-negotiable behavioral limits. Similar to PermissionPolicy but with
stronger enforcement semantics.

---

### 25. ErasureEvent -> Process (BFO:0000015)

**Decision**: Process (subclass of Event)

**Rationale**: An erasure event is something that happens -- memory items
are identified and deleted. It has temporal extent and participants
(the requesting agent, the affected memory items).

---

### 26. Status (Value Partition) -> No direct BFO parent

**Decision**: Modeled using the Value Partition pattern (ODP-6) with
named individuals. Not directly aligned to a single BFO category.

**Rationale**: BFO Quality (BFO:0000019) is a specifically dependent
continuant -- each quality instance inheres in one specific bearer. But
PAO status values (Active, Completed, etc.) are shared reference values
used across multiple entities. This does not fit BFO's particular-quality
model. The Value Partition pattern is the standard OWL solution for
controlled vocabularies that don't need BFO quality alignment.

**Note**: If future BFO alignment is needed, status values could be
modeled as quality universals with the value partition interpreted as
a classification of quality instances.

---

## ConversationParticipation (Removed)

The pre-glossary included `ConversationParticipation` as an n-ary relation
class (ODP-1). During conceptualization, this was replaced by PROV-O's
qualified association pattern (ODP-2):

- `prov:qualifiedAssociation` links activities to `prov:Association` nodes
- `prov:agent` links the association to the participating agent
- `prov:hadRole` links the association to the agent's role

This eliminates a custom reification class in favor of standard PROV-O
vocabulary. CQ-004 ("What role does each agent play?") is still answerable
via the PROV-O pattern.

---

## Cross-Cutting Concerns

### Information vs. Process Distinction

PAO consistently separates:
- **Information artifacts** (GDC): things that carry content (messages,
  memory items, plans, policies)
- **Processes**: things that happen (conversations, tool invocations,
  memory operations, erasure events)

This follows anti-pattern #7 (Information-Physical Conflation) and the
BFO Continuant/Occurrent disjointness.

### Episode Resolution

The pre-glossary listed Episode as dual-natured (MemoryItem + Event).
This was resolved by treating Episode as purely a GDC (memory item) that
records events. The relationship between events and episodes uses
`recordedInEpisode` rather than mereological `partOf`, respecting the
BFO category boundary.

### Agent Hierarchy

The Agent class cross-cuts BFO categories:
- HumanUser -> Object (Material Entity)
- AIAgent, SubAgent -> GDC

This is a pragmatic decision documented as a known trade-off. The
alternative (Agent-as-Role) was rejected for CQ usability reasons.
