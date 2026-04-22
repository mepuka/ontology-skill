# Competency Question Traceability

**Referenced by:** `ontology-requirements`, `ontology-architect`, `ontology-validator`,
`ontology-curator`, `sparql-expert`.

Every competency question (CQ) in an ontology must trace through a chain:
**stakeholder need → use case → CQ → term → SPARQL (or entailment check)**.
Safety rule 12 forbids marking any CQ satisfied without an executable check.
This file gives the schema and maintenance rules.

## 1. The trace chain

```
stakeholder need
  ↓ elicited in
use case (who/what/why)
  ↓ refined into
competency question (natural language)
  ↓ mapped to
terms (classes/properties the CQ exercises)
  ↓ formalized as
SPARQL query  (or TBox entailment check)
  ↓ verified by
pass/fail result recorded in `cq-test-manifest.yaml`
```

Every row in the chain has a stable identifier and is pointed to by the
rows below it.

## 2. CSV schema — `docs/cq-traceability.csv`

Store one row per CQ at `ontologies/{name}/docs/cq-traceability.csv`.
Tab-separated (or comma-separated if no tabs in cells):

| Column | Type | Example |
|--------|------|---------|
| `cq_id` | string | `cq-006` |
| `priority` | enum | `must \| should \| could` |
| `stakeholder` | string | `platform-eng` |
| `use_case_id` | string | `UC-ingestion-catalog-validation` |
| `question_text` | string | "Which datasets publish a given variable at a given resolution?" |
| `expected_answer_shape` | string | "A set of `dcat:Dataset` IRIs, possibly empty." |
| `required_terms` | CURIE list | `sevocab:Dataset, sevocab:Variable, sevocab:TemporalResolution` |
| `sparql_path` | path | `tests/cq-006.sparql` |
| `kind` | enum | `select \| ask \| entailment` |
| `test_manifest_id` | string | `cq-006` |
| `status` | enum | `draft \| implemented \| passing \| failing \| deprecated` |
| `last_verified` | ISO date | `2026-04-14` |
| `loopback_records` | path list | `docs/loopbacks/2026-03-15-cq006-profile.md` |

## 3. CQ-test-manifest linkage

Each row's `sparql_path` must appear in
`ontologies/{name}/tests/cq-test-manifest.yaml`:

```yaml
tests:
  - id: cq-006
    file: tests/cq-006.sparql
    kind: select               # or ask, verify
    expected: non-empty        # or empty, true, false, zero-rows
    expected_results_contract: |
      Columns: ?dataset ?variable ?resolution
      At least one row per dataset.variable.resolution triple matching the scope.
    categories: [cq]
    depends_on_imports: [qudt-unit]
    tags: [dcat, variable, resolution]
```

`cq-test-manifest.yaml` is the executable contract; `cq-traceability.csv`
is the audit trail.

## 4. Maintenance triggers

Update the CSV whenever:

- A CQ is added, refined, or retired (status change).
- A term in `required_terms` is renamed, deprecated, or replaced.
- The SPARQL file is renamed or moved.
- A loopback record cites the CQ (append the path).
- A release ships (update `last_verified`).

Update `cq-test-manifest.yaml` whenever:

- A SPARQL test is added, moved, renamed.
- The expected shape changes (also note this in the loopback record).
- A test's category or dependency list changes.

## 5. Automated checks

A helper `scripts/validate_cq_traceability.py` (future Wave 2+) should:

- Parse `cq-traceability.csv` and `cq-test-manifest.yaml`.
- Assert every `cq_id` in the CSV has a matching `tests[].id`.
- Assert every `sparql_path` references a file that exists.
- Assert every `required_terms` CURIE resolves via `namespaces.json`.
- Assert every `passing` row has a `last_verified` within the refresh
  cadence (default 90 days).

Add to pre-commit once authored.

## 6. CQ classes

Different CQs need different verification kinds:

| Kind | What it checks | Gate |
|------|----------------|------|
| `select` | Returns the set the CQ asks for | Non-empty result set on fixture or live graph |
| `ask` | Returns True/False | Expected boolean matches |
| `verify` | Returns zero rows (integrity check) | Empty result set means pass |
| `entailment` | TBox entailment check | Reasoner derives the expected subsumption / equivalence |

Use `verify` for negative CQs ("nothing should match X") rather than
inventing new logic; see
[`ontologies/skygest-energy-vocab/scripts/run_cq_tests.py`](../../../ontologies/skygest-energy-vocab/scripts/run_cq_tests.py)
for the reference runner.

## 7. Expected-results contract

Every CQ SPARQL file starts with a block comment documenting:

```sparql
# CQ: cq-006
# Kind: select
# Expected: non-empty
# Expected shape:
#   Columns: ?dataset ?variable ?resolution
#   At least one row per declared (dataset, variable, resolution) triple in scope.
# Depends on imports: qudt-unit
# Loopback history: docs/loopbacks/2026-03-15-cq006-profile.md

PREFIX dcat: <http://www.w3.org/ns/dcat#>
# ... query ...
```

This block is parsed by the CQ runner to verify the returned shape
matches the contract. It also serves as documentation.

## 8. CQ decomposition

When a CQ is too broad for a single SPARQL query, decompose it:

- Keep the parent CQ in the CSV with `status: draft` and
  `sparql_path` = `tests/cq-006-parent.md` (a markdown with prose).
- Add child rows (`cq-006.1`, `cq-006.2`, …) each with its own SPARQL
  and its own shape contract.
- The parent is `passing` only when all children pass.

## 9. Anti-patterns

- **CQ without SPARQL.** Safety rule 12 prohibits.
- **SPARQL without CQ.** A test nobody can trace back to a requirement
  is dead code; either link it or delete it.
- **"Close enough" satisfaction.** A CQ is satisfied only when the
  SPARQL result matches the expected-results contract.
- **Stale `last_verified`.** A CQ that hasn't been verified in six
  months is not known to pass — re-run before claiming.
- **CQ text drift from use case.** When the CQ wording gets refined,
  update the use case too, or raise a `scope_violation` loopback.

## 10. Worked examples

- [`worked-examples/ensemble/requirements.md`](worked-examples/ensemble/requirements.md) — five ensemble CQs with trace CSV rows.
- [`worked-examples/microgrid/sparql.md`](worked-examples/microgrid/sparql.md) — property-chain CQ decomposed into three SELECTs.

## 11. References

- [`ontologies/skygest-energy-vocab/docs/competency-questions.yaml`](../../../ontologies/skygest-energy-vocab/docs/competency-questions.yaml) — live example of the schema applied.
- Gruninger & Fox, "Methodology for the Design and Evaluation of Ontologies" — the original CQ methodology.
