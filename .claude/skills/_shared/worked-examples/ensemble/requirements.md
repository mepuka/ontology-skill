# Ensemble — `ontology-requirements` walkthrough

Walks [`ontology-requirements`](../../../ontology-requirements/SKILL.md) Core
Workflow Steps 0–9 on the ensemble ontology. Goal of this run: land five
frozen CQs (`CQ-E-001..005`), a traceability matrix, and a signed
`requirements-approval.yaml` that `ontology-scout` and
`ontology-conceptualizer` can accept as an inbound gate.

## Step 0 — scope gate (`docs/scope.md`)

| Gate | Verdict | Evidence |
|---|---|---|
| Scope fit | approved | Cross-stakeholder vocabulary for ensemble membership + instrument typology is an ontology problem. |
| Retrofit check | false | No prior `ontologies/ensemble/*.ttl` exists; `docs/requirements-retrofit-note.md` not created. |
| Stakeholder available | true | One conservatory librarian + one ensemble coordinator confirmed for Must-Have review. |

## Step 1.5 — use case (`docs/use-cases.yaml`)

```yaml
- id: UC-E-001
  name: "Identify string quartets on a concert programme"
  actor: "Programme coordinator"
  goal: "Filter ensembles that satisfy the exactly-four-string-players constraint"
  related_cqs: [CQ-E-001, CQ-E-004]
  priority: must_have
```

## Steps 2.5 + 5 — CQ quality + formalized CQ (`docs/competency-questions.yaml`)

```yaml
- id: CQ-E-001
  source_use_case: UC-E-001
  natural_language: "Which ensembles consist of exactly four string players?"
  type: quantitative
  priority: must_have
  owner: "coordinator@ensemble.example"
  testability: executable
  expected_answer_shape:
    cardinality: "0..n"
    per_row: [ensemble, label]
  sample_answer: [{ensemble: "ex:BeethovenOp18No1", label: "String Quartet No. 1"}]
  derivation_method: inference           # classification via qualified cardinality
  required_axioms: ["hasMember exactly 4 StringPlayer"]
```

Step 2.5 scoring row in `docs/cq-quality.csv`: `CQ-E-001,pass,pass,pass,pass,pass,pass,advance`.

## Step 6 — pre-glossary (`docs/pre-glossary.csv`)

```
term,category,source_cq,notes
Ensemble,class,CQ-E-001..005,parent of StringQuartet, Orchestra, JazzCombo
StringPlayer,class,CQ-E-001,role borne by Musician — not subclass of Person
hasMember,property,CQ-E-001/CQ-E-002,domain: Ensemble; range: Musician
Performance,class,CQ-E-003,N-ary reification target; holds date + composition
MusicInstrument,class,CQ-E-005,target of MIMO exactMatch cross-domain check
```

## Step 7 + 7.5 — test manifest (`tests/cq-test-manifest.yaml`)

```yaml
tests:
  - id: CQ-E-001
    file: tests/cq-e-001.sparql
    kind: select
    expected: non-empty
    expected_results_contract: |
      Columns: ?ensemble ?label.
      Non-empty on the fixture tests/fixtures/cq-e-001.ttl (contains 2 quartets, 1 quintet decoy).
    parse_status: ok
    fixture_run_status: pass
    entailment: hermit     # qualified cardinality needs DL, not ELK
```

Preflight loops back to `sparql-expert` if `parse_status: fail` — see
`../../iteration-loopbacks.md § 3` failure class `sparql_parse`.

## Step 8 — traceability (`docs/traceability-matrix.csv`)

```
stakeholder_need,use_case_id,cq_id,ontology_terms,sparql_test
"Programme quartets",UC-E-001,CQ-E-001,"Ensemble;StringPlayer;hasMember",tests/cq-e-001.sparql
"Player-vs-instrument separation",UC-E-002,CQ-E-002,"Musician;plays;MusicInstrument",tests/cq-e-002.sparql
"2024 performances by work",UC-E-003,CQ-E-003,"Performance;hasPiece;hasDate",tests/cq-e-003.sparql
"Instrumentation-defined ensembles",UC-E-001,CQ-E-004,"Ensemble;EquivalentTo",tests/cq-e-004.sparql
"MIMO reuse safety",UC-E-005,CQ-E-005,"MusicInstrument;exactMatch",tests/cq-e-005.sparql
```

## Step 9 — approval (`docs/requirements-approval.yaml`)

```yaml
reviewer: "coordinator@ensemble.example"
reviewed_at: "2026-04-22"
cq_freeze_commit: "abc1234"
scope_gate: {scope_fit: approved, retrofit_note: false, stakeholder_available: true}
approved_cq_ids: [CQ-E-001, CQ-E-002, CQ-E-003, CQ-E-004, CQ-E-005]
waived_cqs: []
```

## Pitfall walk — bad-CQ retrofit (anti-pattern § A.1)

Candidate CQ "What instruments exist?" scores **fail** on Step 2.5's
*falsifiable* criterion: it cannot return an empty set unless the graph
is empty, so it cannot fail. Rewrite as CQ-E-004 "Which ensemble types
are defined by their instrumentation (not their size)?" which *can*
return zero rows when no class has an `EquivalentTo` axiom referencing
an instrument property. Record the rejection in `cq-quality.csv` with
`decision: rewrite` and link the replacement CQ in
`docs/traceability-matrix.csv`.

## Handoff

Step 9 approval + `pre-glossary.csv` → `ontology-scout` (see
[`scout.md`](scout.md)); `competency-questions.yaml` + traceability matrix
→ `ontology-conceptualizer` (see [`conceptualizer.md`](conceptualizer.md)).
