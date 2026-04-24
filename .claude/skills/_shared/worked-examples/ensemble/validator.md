# Ensemble — `ontology-validator` walkthrough

Walks [`ontology-validator`](../../../ontology-validator/SKILL.md) Levels
0–8 for the ensemble ontology, consuming the handoff-manifest from
[`architect.md`](architect.md). Goal: run the canonical command order,
show a realistic mixed pass/fail, and route one injected CQ-E-001
failure back to `ontology-architect` via the Level 8 routing table.

## Step 0 — artifact classification

```yaml
artifact_type: ontology           # TBox; Levels L0→L6 apply, plus L7 diff
handoff_id: HOF-ENSEMBLE-2026-04-22
```

## Command order (canonical)

`L0 → L1 → L2 → L4 → L3 → L4.5 → L5.5 → L6` — per SKILL.md Core Workflow
command order; deviation is a loopback.

## Level 0 — syntax / profile / import-closure preflight

```
$ robot validate --input ensemble.ttl > validation/syntax.log
  → 0 parse errors
$ .local/bin/robot validate-profile --profile DL --input validation/merged.ttl --output validation/profile-validate.txt
  → "Ontology is in OWL 2 DL profile."
$ robot merge --input ensemble.ttl --collapse-import-closure true --output validation/merged.ttl 2> validation/import.log
  → 0 unresolved imports
```

L0 passes. (Had the architect committed without the Step 2.5 import
preflight, a missing `mimo:HornbostelSachsCategory` would surface here
as `missing_reuse` → route to `ontology-scout`, per `iteration-
loopbacks.md § 3`.)

## Level 1 — reasoner

```
$ robot reason --reasoner HermiT --input validation/merged.ttl \
    --output validation/reasoned.ttl --dump-unsatisfiable validation/unsatisfiable.txt
  → 0 unsatisfiable classes
  → :BeethovenOp18No1 classified as :StringQuartet (via hasMember exactly 4 Musician)
```

## Level 2 — ROBOT report

```
$ robot report --input validation/merged.ttl --fail-on ERROR --output validation/robot-report.tsv
  → 0 ERROR; 3 WARN
```

WARN rows (from `robot-report.tsv`):

```
Rule Name               Subject                Message
missing_synonym         ens:Cello              No skos:altLabel
missing_synonym         ens:Viola              No skos:altLabel
missing_synonym         ens:Violin             No skos:altLabel
```

WARN thresholded per `shacl-patterns.md § 8` — logged, not blocking.

## Level 4 — CQ verify

```
$ robot verify --input validation/reasoned.ttl --queries ontologies/ensemble/tests/ --output-dir test-results/
  CQ-E-001: FAIL — 0 rows, expected non-empty
  CQ-E-002: PASS — 1 row
  CQ-E-003: PASS — 1 row
  CQ-E-004: PASS — 1 row
  CQ-E-005: PASS — 0 rows (fixture has no schema.org cross-domain rows; expected empty)
```

### Injected failure analysis (CQ-E-001)

The CQ SPARQL (`tests/cq-e-001.sparql`) asks for ensembles satisfying
`hasMember exactly 4 Musician that bears StringPlayerRole`. The fixture
`tests/fixtures/cq-e-001.ttl` has two quartets. `BeethovenOp18No1` has
four members, all bearing `StringPlayerRole`; `MozartK465` has four
members but one is annotated with `ConductorRole` instead. Reasoner
classifies `BeethovenOp18No1` as `StringQuartet`, not `MozartK465`. The
query returns 0 rows because the entailment regime in the manifest is
declared `asserted` not `hermit`:

```yaml
# excerpt from cq-test-manifest.yaml
- id: CQ-E-001
  entailment: asserted       # ← wrong: classification requires reasoned graph
```

**Root cause class.** Not an axiom defect; the query runs against an
unreasoned graph so the classification entailment is invisible. Route
per Level 8 table: `sparql-expert` (entailment regime fix). Fix:
update the manifest row to `entailment: hermit` and re-run. Had this
instead been a missing axiom, Level 8 routes to `ontology-architect`.

## Level 3 — SHACL

```
$ uv run pyshacl -s ontologies/ensemble/shapes/ensemble-shapes.ttl \
    --inference rdfs -f human ontologies/ensemble/ensemble.ttl \
    > validation/shacl-results.ttl
  → Conforms: True
```

## Level 4.5 — CQ manifest integrity

```
$ uv run python scripts/cq_manifest_check.py --manifest tests/cq-test-manifest.yaml \
    --ontology ensemble.ttl --axiom-plan docs/axiom-plan.yaml \
    --out validation/cq-manifest-audit.json
  {
    "missing_files": [],
    "must_have_covered": true,
    "stale_refs": [],
    "entailment_regime_mismatches": ["CQ-E-001: declared asserted, classification requires hermit"]
  }
```

Stale-CQ check surfaces the same root cause — double-gate confirmation.

## Level 5.5 — anti-pattern pack

```
$ mkdir -p validation/anti-pattern-results
$ for probe in singleton-hierarchy orphan-class missing-disjointness ...; do
    robot query --input validation/merged.ttl --query sparql/anti-patterns/${probe}.sparql \
      --output validation/anti-pattern-results/${probe}.csv
  done
```

Results: all empty except `missing-disjointness.csv` — siblings
`StringEnsemble`, `WindEnsemble` missing `DisjointClasses` (already
flagged in conceptualizer anti-pattern-review; resolution row exists →
no fresh loopback).

## Level 6 — evaluation dimensions (notes)

| Dimension | Finding |
|---|---|
| Semantic | Expressivity OWL-DL; classification gives CQ-E-001 power when query runs under reasoned regime. |
| Functional | 4/5 Must-Have CQs pass without change; CQ-E-001 is a regime fix, not an axiom gap. |
| Model-centric | Layering honored (foundational/domain/problem); MIMO import is a bottleneck for upstream refresh cadence — curator note. |

## Level 8 — loopback routing table (excerpt from validation-report.md)

| Failure | Owner skill | Required fix artifact | Retry gate |
|---|---|---|---|
| CQ-E-001 returns 0 rows under asserted regime | `sparql-expert` | manifest row: `entailment: hermit` | `uv run python ontologies/ensemble/scripts/run_cq_tests.py --only CQ-E-001` |

No other failures route out. The WARN rows from L2 carry forward to
`ontology-curator` release-notes backlog per the Level 8 canonical map.

## Pitfall callout — shacl-pass / owl-fail inverse

Had the SHACL shapes included a `sh:minCount 4` shape on `Ensemble`,
and the architect omitted the qualified-cardinality axiom, SHACL would
**pass** on any ensemble with ≥ 4 members while the OWL classification
of `StringQuartet` would still fail. The validator always runs both —
see "Consistency vs Validity" table in SKILL.md.

## Handoff

Validation report → architect (CQ-E-001 regime fix) + user. On fix,
re-run from L4 (retry gate) per the Level 8 routing row.
