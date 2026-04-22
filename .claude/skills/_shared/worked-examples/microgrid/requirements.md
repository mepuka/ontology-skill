# Microgrid — `ontology-requirements` walkthrough

Walks [`ontology-requirements`](../../../ontology-requirements/SKILL.md)
Steps 0–9 for the community microgrid ontology. Goal: produce five
Must-Have CQs (CQ-M-001..005) with **explicit stakeholder-need traceability
for CQ-M-002 (dispatch events)** and a signed `requirements-approval.yaml`.

## Step 0 — scope gate (`docs/scope.md`)

| Gate | Verdict | Evidence |
|---|---|---|
| Scope fit | approved | Microgrid interoperability needs a shared TBox for equipment + dispatch + telemetry. |
| Retrofit check | **true** | `ontologies/microgrid/microgrid-draft.ttl` from a prior spike exists → `docs/requirements-retrofit-note.md` inventories 14 draft classes (each will be flagged in Step 3 as inferred-from-structure). |
| Stakeholder available | true | One operations lead + one compliance engineer confirmed. |

## Step 1.5 — use cases with stakeholder needs (`docs/use-cases.yaml`)

```yaml
- id: UC-M-002
  name: "Audit dispatch events that islanded the grid last month"
  actor: "Operations lead"
  stakeholder_needs:
    - id: SN-MG-014
      text: "Compliance requires a full provenance trail on any islanding event within 30 days."
      source: "compliance-engineer@microgrid.example"
  goal: "List dispatch events of type IslandingEvent with participants + temporal bounds"
  preconditions:
    - "Telemetry stream parsed into DispatchEvent reifications"
  main_flow:
    - "Filter DispatchEvents by type :IslandingEvent + hasDate within 30d"
    - "Join participants via RO:0000057"
  postconditions:
    - "Actor can produce audit report PDF within one business day"
  related_cqs: [CQ-M-002]
  priority: must_have
```

## Step 5 — formalized CQs (`docs/competency-questions.yaml`)

```yaml
- id: CQ-M-001
  source_use_case: UC-M-001
  natural_language: "For a given microgrid, what are all its parts transitively, grouped by equipment type?"
  type: enumerative
  priority: must_have
  testability: executable
  expected_answer_shape: {cardinality: "1..n", per_row: [part, equipment_type]}
  derivation_method: inference          # property chain hasPart ∘ locatedIn → locatedIn
- id: CQ-M-002
  source_use_case: UC-M-002
  natural_language: "Which dispatch events participated in islanding the grid in the last month, and which equipment participated in each?"
  type: relational
  priority: must_have
  owner: "ops-lead@microgrid.example"
  expected_answer_shape: {cardinality: "0..n", per_row: [event, equipment, start, end]}
- id: CQ-M-003
  natural_language: "Which telemetry packets are about a given battery, and what measured properties do they record?"
  priority: should_have
  expected_answer_shape: {cardinality: "0..n", per_row: [packet, property]}
- id: CQ-M-004
  natural_language: "Which inverters are currently assigned the primary-inverter role for their subgrid?"
  priority: should_have
  expected_answer_shape: {cardinality: "0..n", per_row: [inverter, subgrid]}
- id: CQ-M-005
  natural_language: "For the OEO mapping, which exactMatch rows escalate to owl:equivalentClass and which must stay SKOS?"
  priority: could_have
  expected_answer_shape: {cardinality: "0..n", per_row: [our_class, oeo_class, predicate]}
```

## Step 2.5 — CQ quality scoring (`docs/cq-quality.csv`)

```
cq_id,atomic,answerable,falsifiable,scoped,prioritized,sample_bearing,decision
CQ-M-001,pass,pass,pass,pass,pass,pass,advance
CQ-M-002,pass,pass,pass,pass,pass,pass,advance
CQ-M-003,pass,pass,pass,pass,pass,pass,advance
CQ-M-004,pass,pass,pass,pass,pass,pass,advance
CQ-M-005,pass,pass,pass,pass,pass,pass,advance
```

## Step 6 — pre-glossary (`docs/pre-glossary.csv`, excerpt)

```
term,category,source_cq,notes
Microgrid,class,CQ-M-001,part-whole aggregate root; see scout for OEO candidate
SolarArray,class,CQ-M-001,bfo:Object — generation equipment
Inverter,class,CQ-M-001/004,bearer of PrimaryInverterRole
DispatchEvent,class,CQ-M-002,bfo:Process; reified for N-ary participation
IslandingEvent,class,CQ-M-002,subclass of DispatchEvent
TelemetryPacket,class,CQ-M-003,IAO:information_content_entity
hasPart,property,CQ-M-001,RO:0002351 has_member specialization
locatedIn,property,CQ-M-001,part of the EL-safe property chain
participatesIn,property,CQ-M-002,RO:0000056
isAbout,property,CQ-M-003,IAO:0000136
bearerOf,property,CQ-M-004,BFO:0000196
```

## Step 7.5 — SPARQL preflight (manifest excerpt)

```yaml
- id: CQ-M-001
  file: tests/cq-m-001.sparql
  entailment: owl-el                 # property chain stays EL
  parse_status: ok
  fixture_run_status: pass
- id: CQ-M-002
  file: tests/cq-m-002.sparql
  entailment: rdfs                   # n-ary reification + subClassOf
  parse_status: ok
  fixture_run_status: pass
```

CQ-M-001 is deliberately kept EL-safe — a DL-only cardinality axiom
here would wreck the fast ELK dev-cycle. See [`architect.md`](architect.md)
for the property-chain instantiation.

## Step 8 — traceability (`docs/traceability-matrix.csv`)

```
stakeholder_need,use_case_id,cq_id,ontology_terms,sparql_test
SN-MG-001,UC-M-001,CQ-M-001,"Microgrid;SolarArray;Inverter;hasPart;locatedIn",tests/cq-m-001.sparql
SN-MG-014,UC-M-002,CQ-M-002,"DispatchEvent;IslandingEvent;participatesIn",tests/cq-m-002.sparql
SN-MG-021,UC-M-003,CQ-M-003,"TelemetryPacket;Battery;isAbout",tests/cq-m-003.sparql
SN-MG-030,UC-M-004,CQ-M-004,"Inverter;PrimaryInverterRole;bearerOf",tests/cq-m-004.sparql
SN-MG-041,UC-M-005,CQ-M-005,"OEOClass;skos:exactMatch;owl:equivalentClass",tests/cq-m-005.sparql
```

CQ-M-002's row is the canonical full-chain demo: compliance stakeholder
need `SN-MG-014` → UC-M-002 → CQ-M-002 → four ontology terms → SPARQL test.

## Step 9 — approval (`docs/requirements-approval.yaml`)

```yaml
reviewer: "ops-lead@microgrid.example"
reviewed_at: "2026-04-22"
cq_freeze_commit: "def5678"
scope_gate: {scope_fit: approved, retrofit_note: true, stakeholder_available: true}
approved_cq_ids: [CQ-M-001, CQ-M-002, CQ-M-003, CQ-M-004, CQ-M-005]
notes: |
  Retrofit-note flag is set because a draft TBox exists. Conceptualizer
  must treat draft as evidence, not axioms; CQs drive the formal model.
```

## Pitfall walk — retrofit detection

Step 0's retrofit gate triggered on the existing draft TTL. Had the
team silently proceeded, they would have ratified a CQ list inferred
from existing classes — "retroactive CQs" anti-pattern (SKILL.md
Anti-Patterns § Retroactive CQs). Instead, the retrofit-note inventory
is produced and every draft class that becomes a CQ term is flagged
with `derived_from_existing_structure: true` so the conceptualizer can
challenge it. Pure additive CQs (e.g., CQ-M-005) carry no such flag.

## Handoff

Step 9 approval + pre-glossary → `ontology-scout` (OEO reuse, see
[`scout.md`](scout.md)); competency-questions.yaml + traceability →
`ontology-conceptualizer` (BFO placement for dispatch-event, see
[`conceptualizer.md`](conceptualizer.md)).
