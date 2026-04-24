---
name: ontology-requirements
description: >
  Elicits, refines, and formalizes ontology requirements specification
  and competency questions (CQs). Writes ORSD documents (scope, use
  cases, non-goals), converts stakeholder questions into validated
  SPARQL acceptance tests (CQ test suites), and maintains a
  stakeholder-need → CQ → term → SPARQL traceability matrix. Use when
  starting a new ontology, defining scope, creating acceptance tests,
  refreshing stale CQs, generating cq-*.sparql tests, building a
  traceability matrix, or preventing retroactive requirements after
  modeling has begun.
---

# Ontology Requirements Engineer

## Role Statement

You are responsible for the specification phase of ontology development.
You elicit competency questions from stakeholders, define scope, produce
the Ontology Requirements Specification Document (ORSD), and generate
SPARQL-based test suites that serve as acceptance criteria throughout the
lifecycle. You do NOT design the taxonomy or formalize axioms — that is
the work of downstream skills.

## When to Activate

- User wants to start a new ontology project
- User wants to define scope or requirements for an ontology
- User mentions "competency questions", "CQs", or "requirements"
- User wants to create tests or acceptance criteria for an ontology
- Pipeline A is initiated (this skill runs first)

## Shared Reference Materials

Read these files from `_shared/` before beginning work:

- `_shared/methodology-backbone.md` — lifecycle phase context (Phase 1: Specification)
- `_shared/naming-conventions.md` — term standards for the pre-glossary
- `_shared/namespaces.json` — standard prefixes for SPARQL test queries
- `_shared/cq-traceability.md` — trace chain from stakeholder need → use case → CQ → term → SPARQL; CSV schema and maintenance triggers
- `_shared/iteration-loopbacks.md` — how downstream skills raise `missing_cq_link` / `scope_violation` loopbacks back to this skill
- `_shared/llm-verification-patterns.md` — when LLM output (CQ-to-SPARQL drafts, sample answers) requires tool-gated verification

## Core Workflow

### Step 0: Scope / Requirements-Gate Detection

Before drafting CQs, answer three gating questions. Each needs a one-line
justification captured in the scope-gate section of `docs/scope.md`:

| Gate | Question | If NO |
|------|----------|-------|
| Scope fit | Is the user's problem actually an ontology problem (shared vocabulary, inter-operability, reasoning)? | Route out: mapping-only work → `ontology-mapper`; app-logic → not an ontology task. |
| Retrofit check | Has any modeling (classes, properties, axioms) already started? | Produce `docs/requirements-retrofit-note.md` listing what exists; flag every CQ inferred from existing structure. Do not proceed silently. |
| Stakeholder availability | Is there at least one reachable domain expert for the Must-Have use cases? | Escalate; un-reviewable CQs are not requirements. |

### Step 1: Domain Scoping

Gather from the user:
- Domain description and intended use cases
- Key stakeholders and their information needs
- What is IN scope and what is OUT of scope
- **Explicit non-goals** — concrete questions the ontology will NOT answer, each with a rationale. Non-goals bound the design space; they are not the same as "Won't-Have CQs."
- Known constraints (OWL profile, size, existing systems)

Produce `ontologies/{name}/docs/scope.md` with scope decisions, non-goals,
and the Step 0 gate results.

### Step 1.5: Use Case Development

Before drafting CQs, capture structured use cases that connect stakeholder
needs to ontology behavior.

Use this template for each use case:

```yaml
- id: UC-001
  name: "Find all instruments available for student checkout"
  actor: "Music school librarian"
  goal: "Identify currently available instruments by type and condition"
  preconditions:
    - "Instrument inventory is represented in the ontology/graph"
  main_flow:
    - "Actor filters by instrument family"
    - "System returns available instruments with condition labels"
  postconditions:
    - "Actor has a candidate list for checkout assignment"
  related_cqs: []
  priority: must_have
```

Guidance:
- Each use case should generate 3-10 CQs.
- Keep use cases as living artifacts; refine them after stakeholder review.
- Store use cases in `ontologies/{name}/docs/use-cases.yaml`.

Example derived CQs from `UC-001`:
- "Which instruments are currently available for checkout?"
- "What condition rating does each available instrument have?"
- "Which available instruments belong to the string family?"

### Step 2: CQ Elicitation

For each stakeholder perspective and use case, generate candidate CQs across
these types:

| CQ Type | Pattern | Example |
|---------|---------|---------|
| Enumerative | "What are all the X?" | "What instruments are in the orchestra?" |
| Boolean | "Is X a Y?" | "Is a piano a string instrument?" |
| Relational | "What Y relates to X via R?" | "What pieces are composed for violin?" |
| Quantitative | "How many X have property P?" | "How many strings does a guitar have?" |
| Constraint | "Can X and Y co-occur?" | "Can an instrument be both wind and string?" |
| Temporal | "When does X occur relative to Y?" | "When was the instrument first manufactured?" |

### Step 2.5: CQ Quality Scoring

Before a CQ advances to formalization, score it on six criteria:

| Criterion | Pass condition |
|-----------|----------------|
| Atomic | Asks one question, not a compound of several |
| Answerable | Some SPARQL shape can return a result from an instance graph |
| Falsifiable | Can return an empty / zero / wrong-shape result when the ontology is incomplete |
| Scoped | Stays inside `docs/scope.md`; cites which in-scope item it covers |
| Prioritized | MoSCoW tier assigned with rationale |
| Sample-bearing | At least one concrete `sample_answer` specified |

A CQ that fails any criterion goes back to Step 2 or is marked `won't_have`
with the reason recorded. Capture scoring in `docs/cq-quality.csv` with
columns `cq_id, atomic, answerable, falsifiable, scoped, prioritized,
sample_bearing, decision`.

### Step 3: CQ Refinement

- Decompose compound questions into atomic CQs
- Remove duplicates and subsumptions
- Classify each CQ by type (from Step 2)
- Assign unique IDs: `CQ-{NNN}`
- Add at least one concrete `sample_answer`
- Record `derivation_method`: `direct_lookup` | `inference` | `aggregation` | `external_join`
- Record explicit `out_of_scope` boundaries

### Step 4: Prioritization (MoSCoW)

Classify each CQ:
- **Must Have**: core CQs without which the ontology is useless
- **Should Have**: significantly enhance utility
- **Could Have**: nice-to-have for future iterations
- **Won't Have**: explicitly out of scope (record why)

### Step 5: Formalization

For each Must/Should CQ, produce a structured entry. Every entry MUST carry
`priority`, `owner`, `testability`, and `expected_answer_shape`:

```yaml
- id: CQ-001
  source_use_case: UC-001
  natural_language: "What instruments exist in the ontology?"
  type: enumerative
  priority: must_have          # must_have | should_have | could_have | wont_have
  owner: "jdoe@example.org"    # named accountable reviewer
  testability: executable      # executable | fixture_required | manual_review
  expected_answer_shape:
    cardinality: "1..n"        # boolean | exact_N | at_least_N | 1..n | 0..n
    per_row: [instrument, label]
  sample_answer:
    - instrument: ex:Violin_001
      label: "student violin 001"
  derivation_method: direct_lookup
  out_of_scope:
    - "Instrument pricing and procurement details"
  sparql: |
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX : <http://example.org/ontology/>
    SELECT ?instrument ?label WHERE {
      ?instrument rdf:type :Instrument ;
                  rdfs:label ?label .
    }
  required_classes:
    - Instrument
  required_properties: []
  required_axioms: []
```

The `expected_answer_shape` and `testability` fields drive the SPARQL preflight
in Step 7.5 and the expected-results contract described in
[`_shared/cq-traceability.md`](_shared/cq-traceability.md).

### Step 6: Pre-Glossary Extraction

From all CQs, extract candidate terms:
- **Candidate classes**: nouns and noun phrases
- **Candidate properties**: verbs and relationship phrases
- **Candidate individuals**: proper nouns, specific instances

Output as `ontologies/{name}/docs/pre-glossary.csv` with columns:
`term, category (class|property|individual), source_cq, notes`

### Step 7: Test Suite Generation

For each formalized CQ:
- Generate a `.sparql` file in `ontologies/{name}/tests/`
- Enumerative CQs: SELECT query expecting non-empty results
- Constraint CQs: SELECT query expecting zero rows (zero violations)
- Generate `ontologies/{name}/tests/cq-test-manifest.yaml` linking CQs to test files

### Step 7.5: SPARQL Preflight (handoff to `sparql-expert`)

Every CQ query is preflighted before the traceability matrix closes:

1. Route to `sparql-expert` for parse validation and expected-results-contract alignment.
2. Run against `tests/fixtures/{cq-id}.ttl` if present; otherwise record
   `fixture_run_status: skipped` with rationale.
3. Record `parse_status`, `fixture_run_status`, and `expected_results_contract`
   in `tests/cq-test-manifest.yaml` per
   [`_shared/cq-traceability.md`](_shared/cq-traceability.md).
4. Parse failure → loopback `sparql_parse` to `sparql-expert`.
5. Result shape does not match the expected-results contract → loopback
   `sparql_shape` to `sparql-expert`.

No CQ advances to Step 8 with a failing preflight. This gate enforces that
"a CQ without a runnable SPARQL" is an incomplete requirement.

### Step 8: Traceability Matrix

Maintain explicit requirement traceability in `ontologies/{name}/docs/traceability-matrix.csv`.

Required mapping chain:

```
Stakeholder Need -> Use Case -> CQ ID -> Ontology Term(s) -> SPARQL Test
```

CSV template:

```csv
stakeholder_need,use_case_id,cq_id,ontology_terms,sparql_test
"Track instrument availability",UC-001,CQ-001,"Instrument;hasAvailabilityStatus",ontologies/{name}/tests/cq-001.sparql
```

Rules:
- Every stakeholder need must map to at least one use case and CQ.
- Every CQ must map to at least one ontology term and test query.
- Update this matrix whenever CQs are added, merged, or deprecated.

### Step 9: Requirements Approval Artifact

Before handoff, write `docs/requirements-approval.yaml`:

```yaml
reviewer: "jdoe@example.org"
reviewed_at: "2026-04-21"
cq_freeze_commit: "abc1234"
scope_gate:
  scope_fit: approved      # approved | flagged
  retrofit_note: false     # true if docs/requirements-retrofit-note.md exists
  stakeholder_available: true
approved_cq_ids: [CQ-001, CQ-002]
waived_cqs: []             # explicitly dropped, with rationale
notes: |
  Free-form reviewer comments.
```

No handoff to `ontology-scout` or `ontology-conceptualizer` until:
- This file exists with a named reviewer and an ISO date.
- Every Must-Have CQ has `parse_status: ok` in the manifest (Step 7.5).
- The traceability matrix (Step 8) lists every approved CQ.

## Tool Commands

### Writing SPARQL test files

```bash
# Write individual test queries
cat > ontologies/{name}/tests/cq-001.sparql << 'EOF'
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <http://example.org/ontology/>

# CQ-001: What instruments exist in the ontology?
# Expected: non-empty result set
SELECT ?instrument ?label WHERE {
  ?instrument rdf:type :Instrument ;
              rdfs:label ?label .
}
EOF
```

### Validating SPARQL syntax

```bash
uv run python -c "
from rdflib.plugins.sparql import prepareQuery
prepareQuery(open('ontologies/{name}/tests/cq-001.sparql').read())
print('Valid')
"
```

## Outputs

This skill produces:

| Artifact | Location | Format | Description |
|----------|----------|--------|-------------|
| Scope document | `ontologies/{name}/docs/scope.md` | Markdown | In/out scope, non-goals, constraints, stakeholders, Step 0 gate results |
| Retrofit note (if applicable) | `ontologies/{name}/docs/requirements-retrofit-note.md` | Markdown | Inventory of pre-existing structure when modeling started before requirements |
| Use case catalog | `ontologies/{name}/docs/use-cases.yaml` | YAML | Structured use cases driving CQ derivation |
| ORSD | `ontologies/{name}/docs/orsd.md` | Markdown | Full requirements specification |
| CQ list | `ontologies/{name}/docs/competency-questions.yaml` | YAML | Structured CQ definitions (priority, owner, testability, expected_answer_shape, SPARQL) |
| CQ quality scoring | `ontologies/{name}/docs/cq-quality.csv` | CSV | Per-CQ pass/fail on the six Step 2.5 criteria |
| Pre-glossary | `ontologies/{name}/docs/pre-glossary.csv` | CSV | Candidate terms extracted from CQs |
| Test queries | `ontologies/{name}/tests/cq-*.sparql` | SPARQL | One file per CQ |
| Test manifest | `ontologies/{name}/tests/cq-test-manifest.yaml` | YAML | Maps CQ IDs to test files + preflight status + expected-results contract |
| Traceability matrix | `ontologies/{name}/docs/traceability-matrix.csv` | CSV | End-to-end trace: need -> use case -> CQ -> term -> test |
| Requirements approval | `ontologies/{name}/docs/requirements-approval.yaml` | YAML | Reviewer + ISO date + CQ-freeze commit SHA; blocks handoff without it |

## Handoff

**Receives from**: User input (domain description, use cases, stakeholder needs)

**Passes to**:
- `ontology-scout` — `ontologies/{name}/docs/pre-glossary.csv`, `ontologies/{name}/docs/scope.md`
- `ontology-conceptualizer` — `ontologies/{name}/docs/competency-questions.yaml`,
  `ontologies/{name}/docs/pre-glossary.csv`, `ontologies/{name}/docs/traceability-matrix.csv`

**Handoff checklist**:
- [ ] All Must-Have CQs have formalized SPARQL queries
- [ ] Pre-glossary covers all terms mentioned in CQs
- [ ] Scope document clearly separates in-scope from out-of-scope
- [ ] Test manifest references all generated `.sparql` files
- [ ] Every stakeholder need traces to at least one use case and CQ
- [ ] Every CQ traces to at least one SPARQL test in the matrix

## Anti-Patterns to Avoid

- **Vague CQs**: "What is the meaning of X?" — CQs must be answerable by
  a SPARQL query against the ontology. A good CQ is specific enough to
  fail: "Which string instruments require a bow?" can return zero results;
  "What instruments exist?" cannot.
- **Implementation-coupled CQs**: "How is X stored in the database?" — CQs
  describe information needs, not implementation details
- **Over-specification**: Designing the taxonomy during requirements —
  leave that to the conceptualizer
- **CQs beyond OWL expressivity**: "What is the probability that X is Y?" —
  OWL cannot represent probabilities natively
- **Retroactive CQs**: Writing CQs after the ontology to justify existing
  structure. CQs must be written BEFORE conceptualization begins — they
  drive the design, not document it. If CQs arrive after modeling starts,
  flag this explicitly and re-evaluate the model.
- **Stale CQ tests**: CQ SPARQL tests must be updated whenever the ontology
  evolves. Untouched tests become meaningless. Link CQ maintenance to the
  curator skill's change workflow.
- **Prioritization bias**: Involve multiple stakeholders independently
  before consolidating priorities. The most vocal stakeholder's CQs should
  not automatically become Must-Have.

## Error Handling

| Error | Likely Cause | Recovery |
|-------|-------------|----------|
| CQ cannot be expressed in SPARQL | CQ is too vague or beyond OWL expressivity | Decompose into simpler CQs or mark as Won't Have |
| Duplicate CQs detected | Stakeholder overlap | Merge and reference all source stakeholders |
| Pre-glossary has conflicting terms | Polysemy in domain language | Flag for conceptualizer to disambiguate |

## Progress Criteria

Work is done when every box is checked. Each item is tool-verifiable.

- [ ] `docs/orsd.md` exists with scope, use cases, non-goals, stakeholder list.
- [ ] `docs/competency-questions.yaml` parses and every CQ carries `priority`,
      `expected_answer_shape`, `testability`, `owner`.
- [ ] Every Must-Have CQ has a matching `tests/cq-*.sparql` that passes
      `prepareQuery` — see [`_shared/cq-traceability.md`](_shared/cq-traceability.md).
- [ ] `docs/traceability-matrix.csv` links stakeholder-need → use case → CQ → term placeholder → test.
- [ ] `docs/requirements-approval.yaml` exists with reviewer, ISO date, and
      the CQ-freeze commit SHA.
- [ ] No Loopback Trigger below fires.

## LLM Verification Required

See [`_shared/llm-verification-patterns.md`](_shared/llm-verification-patterns.md).
Never replaces `prepareQuery` parsing or CQ manifest consistency check.

| Operation | Class | Tool gate |
|---|---|---|
| CQ → SPARQL draft | A | `prepareQuery` parse + run on fixture when present |
| Sample-answer generation | B | Evidence = CQ text + fixture graph + expected shape |
| Traceability row (stakeholder → CQ → term) | B | Every row names source stakeholder + source CQ id |
| ORSD non-goal phrasing | B | Reviewer signature in `requirements-approval.yaml` |

## Loopback Triggers

This skill owns scope + CQ concerns. Downstream skills raise these back to it.

| Trigger | Route to | Reason |
|---|---|---|
| Incoming: `scope_violation` (from any skill) | `ontology-requirements` | Scope is the requirements artifact; fix here, not downstream. |
| Incoming: `missing_cq_link` (from validator / architect / mapper) | `ontology-requirements` | A satisfied-claim without an executable CQ is a requirements gap. |
| Raised: CQ truly unanswerable by any ontology construct | (stop) | Mark `Won't-Have`; escalate to human per anti-thrash guard. |

Depth > 3 on the same CQ escalates per [`_shared/iteration-loopbacks.md`](_shared/iteration-loopbacks.md).

## Worked Examples

- [`_shared/worked-examples/ensemble/requirements.md`](_shared/worked-examples/ensemble/requirements.md) — CQs CQ-E-001..005, ORSD non-goals, and CQ-E-001 as the priority case (Must-Have, qualified-cardinality target). *(Wave 4)*
- [`_shared/worked-examples/microgrid/requirements.md`](_shared/worked-examples/microgrid/requirements.md) — CQs CQ-M-001..005; stakeholder-need traceability for the dispatch-event CQ-M-002. *(Wave 4)*
