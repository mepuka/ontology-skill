# Ontology-Skills Refactor — CHANGELOG

Tracks each wave's commits and gotchas for the 2026-04 refactor. Source of
truth for what landed, when, and why. Paired with the implementation plan
at `~/.claude/plans/users-pooks-dev-ontology-skill-docs-res-bubbly-flamingo.md`
and the session handoff at [`HANDOFF-2026-04-21.md`](HANDOFF-2026-04-21.md).

**Branch:** `refactor/skills-2026-04` (off `main` at `215ea05`)
**Tags:** `wave-0-baseline`, `wave-1-complete`, `wave-2-complete`,
`wave-3-complete`, `wave-4-complete`.

---

## Wave 0 — Baseline

| Commit | Summary |
|--------|---------|
| `215ea05` | `main` tip at branch creation: `feat(enews): add article fetcher, extraction pipeline, and domain policies`. |
| `2794b4c` | On `sky-316-…` — `docs(skills): add workflow-improvement research bundle and reports`. Research context bundle (8,250 lines) + long report (1,600 lines) + short report (712 lines) + prompt + generator script. |
| `e6509ad` | Cherry-picked `2794b4c` onto `refactor/skills-2026-04` so the research files travel with the refactor too. |

Tag: `wave-0-baseline` (at `215ea05`).

### Gotchas
- Research commit lives on *both* `sky-316-…` and `refactor/skills-2026-04`. When these eventually merge to `main`, the second merge is a no-op (identical file content).
- `scripts/build_research_bundle.py` has file-level `# ruff: noqa` for E501/RUF001 on the narrative string tables, plus fixes for F841 / PERF401 / DTZ011.

---

## Wave 1 — Governance foundation

_Status: in progress. This section is appended to as commits land._

### Files created
- `.claude/skills/_shared/iteration-loopbacks.md` — loopback record schema, failure-type routing table, retry gates, anti-thrash guard, waiver handling, 2 worked loopback examples (ensemble + microgrid).
- `docs/refactor/CHANGELOG.md` — this file.

### Files modified
- `.claude/skills/CONVENTIONS.md`
  - § Skill Authoring Standard: expanded 10 → 14 required sections (added Progress Criteria, LLM Verification Required, Loopback Triggers, Worked Examples).
  - § Shared Terminology: added `maintain / maintenance`, `curate`, `evolve / evolution` synonym rows pointing to `ontology-curator`.
  - § Safety Rules: appended rules 11–16 (LLM-artifact gates, CQ link requirement, SSSOM provenance, clique-size review, import-refresh regression, silent-acceptance ban).
  - New § Iteration and Loopback Protocol: loopback record fields, default routing table, depth-3 escalation rule.
- `.claude/skills/SKILL-TEMPLATE.md` — full rewrite. Every Core Workflow step now pairs with an Artifact and a Checked-by command. Added 4 new section placeholders: Progress Criteria, LLM Verification Required, Loopback Triggers, Worked Examples. Handoff checklist upgraded to reference Progress Criteria explicitly.
- `.claude/rules/ontology-safety.md` — re-synced to match `CONVENTIONS.md § Safety Rules` rules 1–16. Header links to the authoritative copy.

### Definition-of-done checks
Run from repo root:
```bash
grep -cE '^[0-9]+\.' .claude/skills/CONVENTIONS.md                    # ≥ 16
for s in "Progress Criteria" "LLM Verification Required" "Loopback Triggers" "Worked Examples"; do
  grep -q "^## $s" .claude/skills/SKILL-TEMPLATE.md || echo "MISSING: $s"
done
test -f .claude/skills/_shared/iteration-loopbacks.md
grep -q iteration-loopbacks .claude/skills/CONVENTIONS.md
uv run ruff check .
```

### Gotchas / decisions
- `ontology-safety.md` rule numbering was previously out of sync with `CONVENTIONS.md` (it omitted the SPARQL UPDATE/DELETE rule). Now both files list identical rules 1–16 in identical order. Sync is maintained manually until a linter catches drift (tracked as a Wave 2+ follow-up).
- Did not introduce `docs/loopbacks/` yet; that directory is created on first real loopback. `iteration-loopbacks.md` documents the expected path.
- No skill files (`.claude/skills/*/SKILL.md`) were touched in Wave 1 by design — governance precedes content (invariant #10).

---

## Wave 2 — OWL-strategy shared files + skill descriptions

| Commit | Summary |
|--------|---------|
| `43df6c6` | `refactor(skills): wave 2a — 9 shared reference files for OWL strategy` |
| `4323edf` | `refactor(skills): wave 2b — skill descriptions + routing validator` |

Tag: `wave-2-complete`.

### Files created
- **Shared reference files (9):** `llm-verification-patterns.md`, `owl-profile-playbook.md`, `closure-and-open-world.md`, `shacl-patterns.md`, `robot-template-preflight.md`, `odk-and-imports.md`, `relation-semantics.md`, `bfo-decision-recipes.md`, `cq-traceability.md`.
- **`scripts/validate_description_routing.py`** — enforces invariant #4 (baseline trigger tokens preserved) and warns on routing collisions.

### Files modified
- All 8 `SKILL.md` descriptions rewritten (preserving every baseline trigger keyword; validated automatically).
- All 8 `SKILL.md` `## Shared Reference Materials` sections extended with citations per the Wave 2 matrix.

### Decisions / gotchas
- Hyphenated phrases like `upper-ontology` are tokenized as a single token by the routing validator. Normalized to `upper ontology` (space-separated) in the conceptualizer description to preserve the `upper` trigger word.
- `EXPECTED_OVERLAP` raised to 10 for `architect ↔ conceptualizer` and `architect ↔ validator` pairs — they share the largest legitimate vocabulary (axioms, profile, reasoner, SHACL) and the routing validator treats those as expected rather than collisions.
- `via` added to `GENERIC_TOKENS` — it's filler, not a trigger.

### Definition-of-done checks (all pass)
```bash
# All 9 shared files exist and are cited from ≥1 SKILL.md
for f in llm-verification-patterns owl-profile-playbook closure-and-open-world \
         shacl-patterns robot-template-preflight odk-and-imports relation-semantics \
         bfo-decision-recipes cq-traceability; do
  test -f ".claude/skills/_shared/$f.md" && grep -l "$f" .claude/skills/*/SKILL.md >/dev/null
done
# All 8 descriptions changed since wave-1-complete
[ "$(git diff --stat wave-1-complete..HEAD -- '.claude/skills/*/SKILL.md' | grep -c 'SKILL.md')" -eq 8 ]
# Routing validator passes
uv run python scripts/validate_description_routing.py
# ruff clean
uv run ruff check .
```


---

## Wave 3 — Per-skill section additions + quality gates

_In progress. Split into 3a (shared files + stubs), 3b (4 new sections on all 8 skills), 3c (per-skill workflow enhancements)._

### Wave 3a — 4 new shared files + worked-example stubs

### Files created
- **Shared reference files (4):**
  - `.claude/skills/_shared/pattern-catalog.md` — ODP catalog (DOSDP, value partition, part-whole, role, participation, N-ary, information-realization) with CQ→pattern matrix and profile-compatibility quick-check. Referenced by conceptualizer + architect.
  - `.claude/skills/_shared/mapping-evaluation.md` — pre-merge gate checklist, confidence tiers, clique SPARQL, cross-domain exactMatch rule, OAEI-style precision/recall with thresholds, QA report format. Referenced by mapper + validator.
  - `.claude/skills/_shared/sssom-semapv-recipes.md` — required YAML header, SEMAPV justification catalog, lexmatch→SSSOM recipe, Class B LLM-verified recipe, manual curation recipe, OWL translation. Referenced by mapper.
  - `.claude/skills/_shared/modularization-and-bridges.md` — module granularity rules, split triggers, layering, import vs. bridge vs. copy decision tree, bridge patterns (SKOS / equivalence / alignment), bridge safety gate. Referenced by scout + conceptualizer + architect.
- **Worked-example stubs (2 dirs + 2 READMEs):**
  - `.claude/skills/_shared/worked-examples/ensemble/README.md` — Music Ensemble scope, 5 CQs (CQ-E-001..005), target axiom patterns. Wave 4 fills in 8 per-skill files.
  - `.claude/skills/_shared/worked-examples/microgrid/README.md` — Community Microgrid scope, 5 CQs (CQ-M-001..005), target axiom patterns. Wave 4 fills in 8 per-skill files.

### Files modified
- None in Wave 3a. Skill-file modifications land in Wave 3b (4 new sections) and Wave 3c (per-skill enhancements).

### Decisions / gotchas
- `pattern-catalog.md` is intentionally ODP-level and *complements* the existing `axiom-patterns.md`. No duplication: the pattern catalog cites the axiom catalog for the atomic building blocks.
- `mapping-evaluation.md` and `sssom-semapv-recipes.md` split the mapping surface into **authoring** (recipes) and **evaluation** (gates). Both cite `llm-verification-patterns.md` for the Class B prompt template.
- `modularization-and-bridges.md` is the *when/why* file; `odk-and-imports.md` remains the *how* file (MIREOT/STAR/BOT/TOP mechanics).
- Wave 3a cites are **not yet** added to the 8 SKILL.md files — that lands in Wave 3b together with the 4 new sections. This keeps the commit scope clean.

### Definition-of-done checks (all pass)
```bash
# 4 new shared files exist
for f in pattern-catalog mapping-evaluation sssom-semapv-recipes modularization-and-bridges; do
  test -f ".claude/skills/_shared/$f.md" || echo "MISSING: $f"
done
# Worked-example stubs present
test -d .claude/skills/_shared/worked-examples/ensemble
test -f .claude/skills/_shared/worked-examples/ensemble/README.md
test -d .claude/skills/_shared/worked-examples/microgrid
test -f .claude/skills/_shared/worked-examples/microgrid/README.md
# Routing still passes
uv run python scripts/validate_description_routing.py
# ruff clean
uv run ruff check .
```

---

## Wave 4 — Worked examples + publication/provenance + GitHub Actions

_Pending._
