# Changelog

All notable changes to the Personal Agent Ontology will be documented here.

This project uses [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-02-19

### Added

**9 New Classes**
- Identity: Organization, Persona
- Conversation: Observation
- Memory: Rehearsal, MemoryBlock
- Planning: Intention (BDI model)
- Governance: SensitivityLevel (controlled vocabulary), ConsentRecord, RetentionPolicy

**12 New Properties**
- Object properties: belongsTo, hasMember, hasPersona, intendedBy, derivedFromGoal,
  consentSubject, consentPurpose, governedByRetention
- Data properties: hasBlockKey, hasBlockValue, retentionPeriodDays

**11 New Competency Questions (CQ-041 through CQ-051)**
- Identity: organizational affiliation (CQ-041), persona assignment (CQ-042)
- Conversation: observations (CQ-043)
- Memory: rehearsal tracking (CQ-044), memory blocks (CQ-045)
- Planning: intentions (CQ-046, CQ-047)
- Governance: sensitivity levels (CQ-048), consent (CQ-049), retention (CQ-050, CQ-051)

**7 New Use Cases (UC-020 through UC-026)**

### Changed

- **hasSensitivityLevel migrated** from DatatypeProperty(xsd:string) to
  ObjectProperty(SensitivityLevel) with controlled vocabulary enum
  (Public, Internal, Confidential, Restricted)
- SHACL shapes expanded from 12 to 24 NodeShapes
- MemoryOperation DisjointUnion expanded to 5 subtypes (added Rehearsal)
- AllDisjointClasses axioms expanded to 9 groups
- Design notes DN-01, DN-02, DN-03 resolved

### Metrics

| Metric | v0.1.0 | v0.2.0 |
|--------|--------|--------|
| Classes | 37 | 46 |
| Object properties | 43 | 52 |
| Data properties | 6 | 8 |
| SHACL shapes | 12 | 24 |
| Named individuals | 13 | 17 |
| CQ tests | 39 | 50 |
| Total tests | 377 | 480 |
| TBox triples | 810 | 999 |

## [0.1.0] - 2026-02-18

### Added

**Ontology Core (37 classes, 48 properties)**
- Agent hierarchy: Agent, AIAgent, HumanUser, SubAgent
- Conversation model: Conversation, Session, Turn, Message, CompactionEvent
- Memory architecture: MemoryItem, MemoryTier, Episode, Claim, and 4 memory
  tiers (Working, Episodic, Semantic, Procedural)
- Memory operations: Encoding, Retrieval, Consolidation, Forgetting
- Planning: Goal, Plan, Task with status tracking and dependency management
- Governance: PermissionPolicy, SafetyConstraint, ErasureEvent
- Event hierarchy: Event, Action, ToolInvocation
- Status value partitions: SessionStatus, TaskStatus, ComplianceStatus
- Agent roles: AgentRole with AssistantRole and UserRole individuals

**External Alignments**
- BFO 2020 upper ontology alignment for all 37 classes
- PROV-O import for provenance (Agent, Activity, Entity, Plan, Role)
- OWL-Time import for temporal reasoning (Instant, Interval)
- FOAF import for person modeling
- ODRL 2.2 import for permission/policy modeling

**Axioms and Constraints**
- 42 object properties with domain/range, 6 datatype properties
- 37 existential restrictions linking classes to required relations
- 8 AllDisjointClasses axioms covering all sibling groups
- 2 DisjointUnion covering axioms (MemoryOperation, MemoryTier subtypes)
- Property hierarchy with 5 subPropertyOf relationships
- 9 inverse property pairs
- 20 functional properties, 2 transitive properties

**Quality Artifacts**
- 12 SHACL NodeShapes for structural validation
- 374 unit tests (100% pass rate)
- 40 competency questions, 39 formalized as SPARQL acceptance tests
- ROBOT quality report: 0 ERRORs, 29 WARNs (external terms only)

**SSSOM Mappings (44 total)**
- schema.org: 14 mappings (actions, conversations, messages)
- ActivityStreams 2.0: 12 mappings (activity/actor model)
- SIOC: 10 mappings (conversation threading)
- DPV: 8 mappings (privacy/governance compliance)

**Documentation**
- ORSD with scope document and use cases
- Glossary (50 terms), conceptual model, BFO alignment rationale
- Property design specification and axiom plan
- Anti-pattern review, ODP recommendations, reuse report
- Validation report with 6-level quality assessment

### Release Artifacts

| Format | File | Size |
|--------|------|------|
| Turtle | `personal_agent_ontology.ttl` | 62 KB |
| OWL/XML | `personal_agent_ontology.owl` | 88 KB |
| JSON-LD | `personal_agent_ontology.jsonld` | 123 KB |
| SHACL shapes | `pao-shapes.ttl` | 3.2 KB |
| Reference individuals | `pao-reference-individuals.ttl` | 3.7 KB |
