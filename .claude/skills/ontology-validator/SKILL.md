---
name: ontology-validator
description: >
  Runs ontology and mapping quality gates: OWL reasoners, OWL profile
  validation, ROBOT quality reports, SHACL / pyshacl validation, CQ
  acceptance test suites, anti-pattern SPARQL, SSSOM validation,
  computes quality metrics, and generates diff reports for release
  audit. Use for comprehensive ontology validation and quality
  assurance before committing changes, releases, or after structural
  changes; when auditing an existing ontology, validating mappings,
  debugging reasoner / SHACL / CQ failures, or checking CI readiness.
---

# Ontology Validator

## Role Statement

You are responsible for the evaluation phase — comprehensive validation
across logical, structural, and documentation dimensions. You run the
full quality checklist, report results, and flag issues for upstream
skills to fix. You do NOT fix issues yourself (except trivial annotation
fixes) — you report and hand back to the appropriate skill.

## When to Activate

- User mentions "validate", "verify", "check", "quality", or "test"
- After any ontology modification (should be invoked automatically)
- Before commits or releases
- Pipeline A Step 5, Pipeline B Step 3, Pipeline C Step 2

## Shared Reference Materials

Read these files from `_shared/` before beginning work:

- `_shared/methodology-backbone.md` — lifecycle phase context (Phase 6: Evaluation)
- `_shared/quality-checklist.md` — the full validation checklist
- `_shared/anti-patterns.md` — anti-pattern detection queries
- `_shared/naming-conventions.md` — naming compliance checks
- `_shared/shacl-patterns.md` — shape severity thresholds, SPARQL-based constraints, pass/fail conventions
- `_shared/closure-and-open-world.md` — how OWA/CWA interact across reasoner and SHACL passes; explains why an axiom may satisfy OWL but fail SHACL
- `_shared/llm-verification-patterns.md` — why validator never paraphrases tool output; rules for attaching raw logs
- `_shared/cq-traceability.md` — the CQ manifest schema; validator reads to know expected-results contract per CQ
- `_shared/iteration-loopbacks.md` — validator is the primary raiser of loopbacks; see routing table for per-failure-type owners
- `_shared/mapping-evaluation.md` — pre-merge gate checklist, clique check, cross-domain exactMatch rule, OAEI metrics; the validator runs these against every mapping set

## Consistency vs. Validity (OWA vs. CWA)

Use both OWL reasoning and SHACL; they answer different questions.

- **OWL reasoning (Open World Assumption)** checks logical consistency.
  Missing facts are treated as unknown, not false.
- **SHACL validation (Closed World Assumption for the validated data)** checks
  structural validity. Missing required data is a violation.

| Check Type | Catches | Misses |
|-----------|---------|--------|
| OWL reasoner | Unsatisfiable classes, logical contradictions | Missing required annotations/data |
| SHACL | Missing properties, cardinality/datatype violations | Logical inconsistency across axioms |

A model can be logically consistent and still fail SHACL completeness checks.
It can also pass SHACL and still be logically inconsistent.

## Core Workflow

### Step 0: Artifact Type Classification

Classify the input before any gate fires. Artifact type selects which
levels apply:

| Artifact | Levels that apply |
|----------|-------------------|
| Ontology (TBox) | L0 → L6, plus L7 diff for releases |
| Mapping set | L0 (schema / prefix preflight), mapping gates per `mapping-evaluation.md`, plus L8 loopback |
| Bridge ontology | L0 → L1 on merged source + target + bridge (consistency + conservativity per `ontology-mapper § Step 8`) |
| Import closure | L0 (resolve imports), L2 report on merged closure, L7 diff vs. previous manifest |
| Release artifact | All levels, plus L7 diff and publication metadata |

Record the artifact type at the top of the validation report; missing type
triggers an immediate handback to the upstream skill.

### Command Order (mandatory)

Run gates in this exact order. Stop-on-ERROR semantics apply to each step:

```text
L0 preflight → L1 reason → L2 report → L4 verify (CQ) → L3 pyshacl → L4.5 CQ regression
                                                         ↓
                                                      L5.5 anti-pattern pack → L6 diff
```

Severity thresholds (applied per level):

| Severity | Meaning | Action |
|----------|---------|--------|
| ERROR | Blocks handoff; upstream skill must fix | Loopback per L8 |
| WARN  | Tracked; not blocking but must appear in report | Log and carry forward |
| INFO  | Informational | Logged only |

Exit codes from the tools are authoritative — not narrative interpretation.

### Level 0: Syntax / Profile / Import-Closure Preflight

Before any reasoner runs, confirm the artifact is parseable, declares the
intended OWL profile, and resolves its imports:

```bash
# 0a. Syntax parse
robot validate --input ontology.ttl > validation/syntax.log

# 0b. Profile validation — no reasoner, just construct check
.local/bin/robot validate-profile --profile {EL|QL|RL|DL} \
  --input ontology.ttl \
  --output validation/profile-validate.txt

# 0c. Import closure resolution
robot merge --input ontology.ttl --collapse-import-closure true \
  --output validation/merged.ttl 2> validation/import.log
```

A profile violation here is an ERROR and loops back to `ontology-architect`
(`profile_violation`). Do NOT proceed to Level 1 with an open L0 failure —
reasoning on an unresolved closure produces misleading results.

### Step 1: Logical Validation (Level 1)

```bash
# Consistency check with ELK (fast, for EL profile)
robot reason --reasoner ELK --input ontology.ttl

# Consistency check with HermiT (complete, for full DL)
robot reason --reasoner HermiT --input ontology.ttl

# Check for unsatisfiable classes
robot reason --reasoner HermiT --input ontology.ttl \
  --dump-unsatisfiable unsatisfiable.txt
```

If inconsistent:
1. Parse the reasoner explanation
2. Identify the conflicting axioms
3. Report the root cause
4. Suggest a minimal fix
5. Hand back to architect for resolution

### Step 2: Quality Report (Level 2)

```bash
robot report --input ontology.ttl \
  --fail-on ERROR \
  --output report.tsv
```

Checks: missing labels, missing definitions, multiple labels in same
language, deprecated term references, annotation whitespace issues.

### Step 3: SHACL Validation (Level 3)

```bash
uv run pyshacl -s shapes/ontology-shapes.ttl -i rdfs ontology.ttl -f human
```

Standard shapes:
- Every class has `rdfs:label` (minCount 1)
- Every class has `skos:definition` (minCount 1, severity: Warning)
- No orphan classes (every class has a parent)
- Domain/range constraints satisfied

### Level 3.5: SHACL Shape Coverage Check

Count how many property-design intent rows in
`docs/property-design.yaml` (from the conceptualizer) are covered by a
generated shape:

```bash
uv run python scripts/shacl_coverage.py \
  --property-design ontologies/{name}/docs/property-design.yaml \
  --shapes ontologies/{name}/shapes/ \
  --out validation/shacl-coverage.json
```

Rules:

- Every row with `intent: validate` MUST have a matching shape. Missing
  coverage is an ERROR and loops back to `ontology-architect`.
- `intent: infer / annotate` rows do not require shapes.
- Missing SHACL is a FAIL unless explicitly waived in
  `docs/validation-waivers.yaml` with owner, rationale, and expiry.

### Step 4: CQ Test Suite (Level 4)

```bash
# Run all CQ test queries
robot verify --input ontology.ttl \
  --queries ontologies/{name}/tests/ \
  --output-dir test-results/
```

For each test:
- Enumerative CQs: verify non-empty results
- Constraint CQs: verify zero violations (zero-result queries pass)

### Level 4.5: CQ Manifest Integrity + Stale-CQ Detection

Before declaring the CQ suite pass, audit the manifest itself:

```bash
uv run python scripts/cq_manifest_check.py \
  --manifest ontologies/{name}/tests/cq-test-manifest.yaml \
  --ontology ontologies/{name}/{name}.ttl \
  --axiom-plan ontologies/{name}/docs/axiom-plan.yaml \
  --out validation/cq-manifest-audit.json
```

Gate checks:

- Every `.sparql` test file referenced in the manifest actually exists.
- Every Must-Have CQ from `competency-questions.yaml` is referenced by the
  manifest (missing → `missing_cq_link` loopback to `ontology-requirements`).
- Every CQ carries `parse_status: ok`, `expected_results_contract`, and
  `entailment` (absent/invalid → `sparql_shape` loopback to `sparql-expert`).
- Stale-CQ detection: flag CQs whose `required_classes` / `required_properties`
  no longer exist in the ontology. Upstream term renames should surface here.

### Step 5: Coverage Metrics (Level 5)

Calculate and report:

| Metric | Target | Method |
|--------|--------|--------|
| Consistency | PASS | `robot reason` |
| Label coverage | 100% | Count classes with `rdfs:label` |
| Definition coverage | ≥ 80% | Count classes with `skos:definition` |
| CQ test pass rate | 100% (Must-Have) | `robot verify` |
| SHACL conformance | PASS | `pyshacl` |
| Unsatisfiable classes | 0 | `robot reason` |
| Orphan classes | 0 | SPARQL check |

### Level 5.5: Anti-Pattern Detection Pack

Run the full SPARQL anti-pattern pack from
[`_shared/anti-patterns.md`](_shared/anti-patterns.md) against the reasoned
ontology. Each probe produces a results file even when empty:

```bash
mkdir -p validation/anti-pattern-results
for probe in singleton-hierarchy orphan-class missing-disjointness \
             domain-range-overcommit quality-as-class \
             role-as-subclass process-as-material; do
  robot query --input validation/merged.ttl \
    --query sparql/anti-patterns/${probe}.sparql \
    --output validation/anti-pattern-results/${probe}.csv
done
```

Rules:

- Every probe runs and produces a CSV (including empty CSVs for zero
  hits). Absent results file → `anti_pattern` loopback to
  `ontology-conceptualizer`.
- Anti-pattern hits are ERRORs unless the conceptualizer's
  `docs/anti-pattern-review.md` explicitly lists a resolution for that
  class. Unresolved hits block handoff.

### Step 6: Evaluation Dimensions (Level 6)

Document qualitative assessments in the validation report:

- **Semantic**: expressivity, complexity, granularity, epistemological adequacy
- **Functional**: relevance to CQs, rigor of evidence, automation support
- **Model-centric**: authoritativeness, structural coherence, formality level

These notes are not pass/fail automation checks; they are explicit review
judgments with rationale.

### Step 7: Diff Report (for PRs/releases)

```bash
robot diff --left previous.ttl --right ontology.ttl \
  --format markdown --output diff.md
```

### Level 8: Loopback Routing

The validator does not fix anything (except trivial annotation gaps). For
every ERROR and every WARN above threshold, the validation report carries
a routing row pointing to the owner skill and the required fix artifact.
This is how the report hands work back to the pipeline instead of trying
to fix it locally.

| Failure class (from the levels above) | Owner skill | Required fix artifact |
|----------------------------------------|-------------|-----------------------|
| L0 syntax / profile violation | `ontology-architect` | Updated axiom or profile declaration |
| L0 unresolved import | `ontology-curator` | Regenerated `imports-manifest.yaml` + extracted module |
| L1 unsatisfiable class | `ontology-architect` | Axiom diff that eliminates the contradiction |
| L2 ROBOT report ERROR | source skill of the offending axiom | New KGCL patch with fix |
| L3 SHACL violation | `ontology-architect` | Updated shape OR ontology fix |
| L3.5 SHACL missing | `ontology-architect` | Shapes for every `intent: validate` row |
| L4 CQ fail | `ontology-architect` (axiom) or `sparql-expert` (query) — classify from the failure | Per-CQ delta report |
| L4.5 missing CQ link | `ontology-requirements` | Manifest row + traceability update |
| L4.5 stale CQ | `ontology-requirements` | Refreshed `required_classes` / `required_properties` |
| L5.5 anti-pattern hit | `ontology-conceptualizer` | Updated `anti-pattern-review.md` with resolution |
| Mapping gate fail | `ontology-mapper` | Updated SSSOM row or mapping-evaluation report |
| L7 unannotated breaking change | `ontology-curator` | Updated release notes (Step 6.5) |

The routing table mirrors `## Loopback Triggers` at the bottom of this
skill and the canonical routing in
[`_shared/iteration-loopbacks.md`](_shared/iteration-loopbacks.md).

## Tool Commands

### Anti-pattern detection queries

Run SPARQL queries from `_shared/anti-patterns.md`:

```bash
# Singleton hierarchy detection
robot query --input ontology.ttl --query singleton-check.sparql --output singletons.csv

# Orphan class detection
robot query --input ontology.ttl --query orphan-check.sparql --output orphans.csv

# Missing disjointness detection
robot query --input ontology.ttl --query disjoint-check.sparql --output missing-disjoint.csv
```

### SSSOM validation (when applicable)

```bash
uv run sssom validate ontologies/{name}/mappings/source-to-target.sssom.tsv
```

### Naming convention compliance

```bash
# Check CamelCase class names (custom query)
robot query --input ontology.ttl --query naming-check.sparql --output naming-issues.csv
```

## Outputs

This skill produces:

| Artifact | Location | Format | Description |
|----------|----------|--------|-------------|
| Validation report | `ontologies/{name}/docs/validation-report.md` | Markdown | Summary: pass/fail per check, metrics |
| ROBOT report | `{name}-report.tsv` | TSV | Detailed quality report |
| Test results | `test-results/` | Directory | Per-CQ test outputs |
| Diff report | `ontologies/{name}/docs/diff.md` | Markdown | Changes between versions |
| Unsatisfiable list | `unsatisfiable.txt` | Text | List of unsatisfiable classes (if any) |

## Handoff

**Receives from**:
- `ontology-architect` — `ontologies/{name}/{name}.ttl`,
  `ontologies/{name}/shapes/{name}-shapes.ttl`, `ontologies/{name}/tests/*.sparql`,
  `ontologies/{name}/tests/cq-test-manifest.yaml` (CQ tests originate from
  `ontology-requirements` and are forwarded through `ontology-architect`)
- `ontology-mapper` — `ontologies/{name}/mappings/*.sssom.tsv`
- `ontology-curator` — modified `ontology.ttl`, KGCL change log

**Passes to**: User (validation report) or back to upstream skill for fixes

**Handoff checklist**:
- [ ] All Level 1-6 checks have been executed
- [ ] Validation report is generated and accessible
- [ ] Any failures are clearly documented with root cause
- [ ] Recommendations for fixes reference the appropriate upstream skill

## Quality Report Format

```markdown
# Validation Report: {name}
Date: {date}

## Summary
- Overall: PASS / FAIL
- Blocking issues: {count}
- Warnings: {count}

## Level 1: Logical Consistency
- Status: PASS / FAIL
- Reasoner: {ELK/HermiT}
- Unsatisfiable classes: {count}

## Level 2: ROBOT Report
- Status: PASS / FAIL
- Errors: {count}
- Warnings: {count}

## Level 3: SHACL Validation
- Status: PASS / FAIL
- Violations: {count}

## Level 4: CQ Tests
- Total: {count}
- Passed: {count}
- Failed: {count}
- Failed tests: {list}

## Level 5: Metrics
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Label coverage | X% | 100% | PASS/FAIL |
| Definition coverage | X% | ≥80% | PASS/FAIL |
| Orphan classes | N | 0 | PASS/FAIL |

## Level 6: Evaluation Dimensions
- Semantic: {notes}
- Functional: {notes}
- Model-centric: {notes}

## Level 7: Diff Review
- Status: PASS / FAIL
- Summary: {high-level changes}
```

## Anti-Patterns to Avoid

- **Shallow validation**: Don't just run the reasoner and declare success.
  All six validation levels (plus diff review for releases/PRs) must be checked.
- **Ignoring warnings**: WARNINGs don't block commit but should be tracked
  and addressed.
- **Fixing in the wrong skill**: The validator reports; the architect or
  curator fixes. Don't modify the ontology from the validator unless the
  fix is trivial (e.g., adding a missing label).
- **Skipping CQ tests**: CQ tests are acceptance criteria. A passing
  reasoner with failing CQ tests means the ontology is logically consistent
  but functionally incomplete.

## Error Handling

| Error | Likely Cause | Recovery |
|-------|-------------|----------|
| Reasoner timeout | Ontology too large or complex for HermiT | Switch to ELK; profile the ontology for complexity hotspots |
| SHACL shapes file missing | Architect didn't generate shapes | Create minimal shapes or defer SHACL check |
| CQ test files missing | Requirements skill output not available | Generate tests from `ontologies/{name}/docs/competency-questions.yaml` if available |
| ROBOT report fails to parse | Corrupt or malformed Turtle | Run `robot validate --input ontology.ttl` to find syntax errors |

## Progress Criteria

Work is done when every box is checked. All check outputs are saved to
`ontologies/{name}/validation/` as machine-readable files; no claim of pass
without the artifact.

- [ ] `validation/reasoner.log` from `robot reason` (reasoner name declared).
- [ ] `validation/robot-report.tsv` with `--fail-on ERROR` exit 0.
- [ ] `validation/profile-validate.txt` from `robot validate-profile --profile {…}`.
- [ ] `validation/shacl-results.ttl` from `pyshacl` (empty violations list).
- [ ] `validation/cq-results.json` — every Must-Have CQ executed, pass/fail recorded.
- [ ] `validation/anti-pattern-results/` — each `_shared/anti-patterns.md` probe run.
- [ ] Mapping sets (if present) pass gates 1–10 of [`_shared/mapping-evaluation.md § 1`](_shared/mapping-evaluation.md).
- [ ] `validation/diff.md` vs. prior release (or main) for release-gate runs.
- [ ] No Loopback Trigger below fires.

## LLM Verification Required

See [`_shared/llm-verification-patterns.md`](_shared/llm-verification-patterns.md).
Validator NEVER paraphrases tool output — raw log is the evidence.

| Operation | Class | Tool gate |
|---|---|---|
| Root-cause interpretation of a reasoner failure | D | Attach raw reasoner log; no paraphrase. |
| SHACL violation explanation | D | Attach `shacl-results.ttl` row verbatim. |
| Mapping QA narrative | D | Cite gate rows from [`_shared/mapping-evaluation.md § 1`](_shared/mapping-evaluation.md) + raw output. |

## Loopback Triggers

Validator is the primary raiser of loopbacks. Route per failure class:

| Trigger | Route to | Reason |
|---|---|---|
| Unsatisfiable class / profile violation | `ontology-architect` | Axiom-level fix. |
| BFO misalignment / anti-pattern | `ontology-conceptualizer` | Conceptual model owns BFO + anti-patterns. |
| Scope violation / missing CQ link | `ontology-requirements` | Requirements artifact is the source of truth. |
| Missing reuse / stale import | `ontology-scout` / `ontology-curator` | Scout on module pick; curator on refresh. |
| Mapping gate fail (`mapping-evaluation.md § 1`) | `ontology-mapper` | Mapper owns SSSOM + clique + gold-set QA. |
| CQ SPARQL fails to parse / wrong shape | `sparql-expert` | Query author fix. |
| Report severity ≥ ERROR | source skill of the offending axiom | Raise; do not fix locally. |

Depth > 3 escalates per [`_shared/iteration-loopbacks.md`](_shared/iteration-loopbacks.md).

## Worked Examples

- [`_shared/worked-examples/ensemble/validator.md`](_shared/worked-examples/ensemble/validator.md) — seven-level run; injected failure on CQ-E-001 routes to architect (qualified cardinality not satisfied). *(Wave 4)*
- [`_shared/worked-examples/microgrid/validator.md`](_shared/worked-examples/microgrid/validator.md) — EL-safe subset plus DL release gate; mapping-set validation using `mapping-evaluation.md` gates; diff against prior release. *(Wave 4)*
