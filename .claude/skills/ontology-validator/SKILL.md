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
