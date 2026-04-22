# Iteration and Loopback Protocol

**Referenced by:** `CONVENTIONS.md` and every SKILL.md (`## Loopback Triggers`)
**Authority:** [`CONVENTIONS.md § Iteration and Loopback Protocol`](../CONVENTIONS.md)
is the normative source; this file is the operational reference.

Professional ontology work is iterative: reuse discoveries change scope;
modeling choices invalidate CQs; mappings expose conceptual mismatch;
validation results force redesign; import refreshes trigger maintenance
modeling. The pipelines in `CONVENTIONS.md § Cross-Skill Handoff Specification`
are routing heuristics, not linear process models. When a downstream skill
detects that an inbound artifact fails a declared gate, it **raises a
loopback** rather than patching the artifact locally.

## 1. Principles

1. **Reject upward, not sideways.** Failures flow back to the skill that
   produced the failing artifact, not across to a peer skill that "could
   also fix it". This preserves ownership and prevents silent scope drift.
2. **Every loopback is recorded.** The loopback record is the handoff that
   goes back; it replaces the original handoff until the source skill
   returns an updated artifact plus the passing retry gate.
3. **No depth-3 cycles.** A loopback loop that bounces the same artifact
   between the same two skills more than three times must be escalated
   with `[ESCALATE]`; continuing to loop is an anti-pattern.
4. **Waivers are explicit.** If a gate is deliberately bypassed, it is
   documented as a waiver on the artifact, not as an absent gate — and
   the waiver must name a human reviewer and an expiration date.
5. **LLM judgment does not close a gate.** See
   [`llm-verification-patterns.md`](llm-verification-patterns.md) — LLM
   verification augments but never replaces reasoner, `robot report`,
   `pyshacl`, or profile validation.

## 2. Loopback record schema

Every loopback produces a markdown record at
`docs/loopbacks/{YYYY-MM-DD}-{short-id}.md`. Short id is a 6-char slug
of the artifact + failure type (e.g., `cq006-profile-dl`).

| Field | Required | Meaning |
|-------|:-:|---------|
| `rejecting_skill` | yes | Skill that detected the gate failure |
| `source_skill` | yes | Skill responsible for the fix (see § 3) |
| `artifact` | yes | Path(s) of the failing artifact(s) |
| `failure_type` | yes | One of the failure classes in § 3 |
| `evidence` | yes | Path to log/report or direct quote showing the failure |
| `required_fix` | yes | Concrete, tool-checkable change the source skill must make |
| `retry_gate` | yes | Exact command the rejecting skill will rerun on return |
| `depth` | yes | Hop count for this artifact between this pair of skills |
| `waiver` | no | If set, names reviewer and expiration (`alice, 2026-06-30`) |
| `created_at` | yes | ISO date |
| `resolved_at` | no | Filled when the rejecting skill passes the retry gate |

A machine-readable sibling `docs/loopbacks/{id}.yaml` with the same fields
is optional but recommended for release notes and longitudinal tracking.

## 3. Failure classes and default routing

The `failure_type` values and their owner skills. Extend only by updating
this table *and* `CONVENTIONS.md § Iteration and Loopback Protocol`.

| `failure_type` | Canonical symptom | Routes to |
|----------------|-------------------|-----------|
| `missing_artifact` | Declared handoff file absent at the expected path | source skill (last one to produce it) |
| `scope_violation` | Out-of-scope term or CQ in the artifact | `ontology-requirements` |
| `missing_cq_link` | Axiom or term with no traceable CQ | `ontology-requirements` |
| `non_goal_violation` | Artifact asserts something the scope's non-goals forbid | `ontology-requirements` |
| `missing_reuse` | New term duplicates an existing ontology term | `ontology-scout` |
| `bad_module` | Wrong MIREOT/STAR/BOT/TOP choice or oversized import | `ontology-scout` |
| `import_provenance` | Import lacks source / version / extraction metadata | `ontology-scout` |
| `bfo_misalignment` | Wrong BFO parent, role/type confusion, category error | `ontology-conceptualizer` |
| `closure_gap` | Open-world default admits unintended instances | `ontology-conceptualizer` |
| `relation_semantics` | Object vs data property or characteristics wrong | `ontology-conceptualizer` |
| `anti_pattern` | Detected anti-pattern per `anti-patterns.md` | `ontology-conceptualizer` (design) or `ontology-architect` (axiom) |
| `profile_violation` | OWL 2 profile violation for the targeted reasoner | `ontology-architect` |
| `construct_mismatch` | Axiom uses construct the selected reasoner silently skips | `ontology-architect` |
| `unsatisfiable_class` | Reasoner reports unsatisfiability | `ontology-architect` |
| `robot_template_error` | Template emits 0 rows, CURIE errors, or blank IRIs | `ontology-architect` |
| `shacl_violation` | pyshacl `sh:Violation` at severity >= Warning | `ontology-architect` (axiom) or `ontology-conceptualizer` (shape design) |
| `mapping_confidence` | SSSOM row lacks confidence or below merge threshold | `ontology-mapper` |
| `missing_semapv` | SSSOM row lacks `mapping_justification` | `ontology-mapper` |
| `mapping_clique` | `skos:exactMatch` clique > 3 | `ontology-mapper` |
| `mapping_conflict` | Different predicates across tools for same pair | `ontology-mapper` |
| `cross_domain_exactMatch` | Cross-domain `exactMatch` without human review | `ontology-mapper` |
| `sparql_parse` | Query fails to parse | `sparql-expert` |
| `sparql_shape` | Query parses but returns wrong shape (no `expected_results_contract` match) | `sparql-expert` |
| `stale_import` | Import refresh triggers obsoleted terms or failed CQs | `ontology-curator` |
| `change_classification` | Change has no annotation/structural/semantic/mapping/release-infra class | `ontology-curator` |
| `release_gate` | Release lacks version IRI, CHANGELOG entry, or provenance | `ontology-curator` |
| `routing_collision` | Two skills' descriptions share too many trigger tokens | governance — update `CONVENTIONS.md` and open a tracking issue |
| `semantic_ambiguity` | Gate passes but meaning is unclear to downstream | `ontology-conceptualizer` (default) |

Failures that touch multiple owners are routed to the *first* owner in
this ordering:
`ontology-requirements → ontology-scout → ontology-conceptualizer →
ontology-architect → ontology-mapper → ontology-validator →
ontology-curator → sparql-expert`.

## 4. Retry gates

A retry gate is a single command the rejecting skill will rerun when the
source skill returns. It must be:

- **Deterministic** — same command, same input, same exit code.
- **Local** — runnable from repo root with `uv run` or `robot`.
- **Fast** — sub-minute for most cases; full regression is for CI, not
  per-loopback retries.

Common retry gates:

| Failure class | Retry gate |
|---------------|-----------|
| `profile_violation` / `construct_mismatch` | `.local/bin/robot merge --input {edit} --output /tmp/merged.ttl && .local/bin/robot validate-profile --profile {DL\|EL\|QL\|RL} --input /tmp/merged.ttl` |
| `unsatisfiable_class` | `.local/bin/robot reason --reasoner {ELK\|HermiT} --input {edit} --output /tmp/reasoned.ttl` |
| `shacl_violation` | `uv run pyshacl -s {shapes} -f human {ontology}` |
| `robot_template_error` | `.local/bin/robot template --template {tsv} --output /tmp/out.ttl` |
| `missing_cq_link` | `uv run python scripts/validate_cq_traceability.py` |
| `mapping_clique` | `uv run python scripts/validate_sssom.py --clique-check {sssom}` |
| `sparql_parse` / `sparql_shape` | `uv run python ontologies/{name}/scripts/run_cq_tests.py --only {cq-id}` |
| `stale_import` | `just refresh-imports && uv run python ontologies/{name}/scripts/run_cq_tests.py` |

## 5. Anti-thrash guard (depth-3)

Track `depth` on every loopback for each `(artifact, rejecting_skill,
source_skill)` triple. If `depth > 3`, stop:

1. Append `[ESCALATE]` to the loopback record.
2. Add a `RESOLUTION NEEDED` entry to `docs/loopbacks/ESCALATIONS.md`
   with a one-paragraph summary.
3. Surface the escalation in the next daily stand-up or next PR on the
   relevant branch.

Common depth-3 escalation triggers:

- BFO placement disagreement between architect and conceptualizer.
- Mapping target scope disagreement between mapper and requirements.
- CQ wording that no SPARQL query can answer ambiguously (needs human).

## 6. Waivers

A waiver is recorded when a declared gate is knowingly bypassed. It must
specify: the exact gate, the reason, the reviewer (name or GitHub handle),
and the expiration date. Example (inside a loopback record):

```yaml
waiver:
  gate: "robot validate-profile --profile EL"
  reason: "Temporary nominal-required class. Bridge ontology ticket MG-42 tracks removal."
  reviewer: "@koko"
  expires: "2026-06-30"
```

Waivers are visible in `docs/loopbacks/` and auto-swept by a future
`scripts/check_waivers.py` helper (out of scope for Wave 1).

## 7. Worked loopback — ensemble example

- **Setup:** `ontology-architect` added
  `StringQuartet SubClassOf hasMember exactly 4 Musician` targeting ELK.
- **Failure detected by:** `ontology-validator` running
  `robot validate-profile --profile EL`.
- **failure_type:** `profile_violation` (qualified cardinality restriction
  is not in OWL 2 EL).
- **Routes to:** `ontology-architect`.
- **Required fix:** switch reasoner to HermiT for this module or refactor
  the axiom (value partition + role-chain) to stay in EL.
- **Retry gate:** `.local/bin/robot validate-profile --profile EL --input ensemble.ttl`.

See [`worked-examples/ensemble/validator.md`](worked-examples/ensemble/validator.md)
for the full walk-through (Wave 4).

## 8. Worked loopback — microgrid example

- **Setup:** `ontology-mapper` produced a SSSOM file that maps
  `mg:StateOfCharge` `skos:exactMatch` three different QUDT terms.
- **Failure detected by:** `ontology-validator` running clique check.
- **failure_type:** `mapping_clique`.
- **Routes to:** `ontology-mapper`.
- **Required fix:** demote two of the three to `skos:closeMatch`,
  document justification, rerun sssom-py.
- **Retry gate:** `uv run python scripts/validate_sssom.py --clique-check`.

See [`worked-examples/microgrid/validator.md`](worked-examples/microgrid/validator.md)
for the full walk-through (Wave 4).
