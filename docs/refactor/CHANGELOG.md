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

_Pending._

---

## Wave 3 — Per-skill section additions + quality gates

_Pending._

---

## Wave 4 — Worked examples + publication/provenance + GitHub Actions

_Pending._
