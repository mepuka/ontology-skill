# Handoff — Ontology Skills Refactor (after Wave 3b)

**Session paused:** 2026-04-21 (after Wave 3a + 3b committed; no tag yet — Wave 3 is incomplete).
**Branch:** `refactor/skills-2026-04`
**Next session goal:** Execute Wave 3c (per-skill workflow enhancements to `## Core Workflow` on all 8 skills), DoD + `wave-3-complete` tag, then Wave 4 (16 worked-example files + 2 publication/CI shared files + final E2E).

This supersedes [`HANDOFF-2026-04-21-wave2-complete.md`](HANDOFF-2026-04-21-wave2-complete.md). Read that doc for Wave 3 + Wave 4 plan context; this one is the delta since Wave 3b landed.

---

## TL;DR of what's done

- **Waves 0–2 landed + tagged.** Governance, 9 OWL-strategy shared files, skill descriptions, routing validator.
- **Wave 3a landed** (`032b0a6`): 4 new shared reference files (`pattern-catalog.md`, `mapping-evaluation.md`, `sssom-semapv-recipes.md`, `modularization-and-bridges.md`) + 2 worked-example README stubs (`ensemble/`, `microgrid/`).
- **Wave 3b landed** (`fcf8cb3`): 4 new sections (`## Progress Criteria`, `## LLM Verification Required`, `## Loopback Triggers`, `## Worked Examples`) appended to every SKILL.md. Wave 3 citations applied per matrix. No skill descriptions or Core Workflow content changed.
- **Wave 3c pending** — per-skill workflow enhancements to `## Core Workflow`.
- No `wave-3-complete` tag until 3c lands and the DoD passes.

---

## Current state

### Branch
- **Branch:** `refactor/skills-2026-04`
- **Base:** off `main` at `215ea05`.
- **Tip:** `fcf8cb3 refactor(skills): wave 3b — 4 new sections + Wave 3 citations on all 8 skills`
- **Tags:** `wave-0-baseline` (at `215ea05`), `wave-1-complete` (at `bb88e5c`), `wave-2-complete` (at `4323edf`). No Wave 3 tag yet.

### Commits since branching (10 total)
```
fcf8cb3 refactor(skills): wave 3b — 4 new sections + Wave 3 citations on all 8 skills
032b0a6 refactor(skills): wave 3a — 4 shared reference files + worked-example stubs
d3d2169 docs(refactor): add wave-2-complete handoff for next session
814a60e docs(refactor): update changelog for wave 2 complete
4323edf refactor(skills): wave 2b — skill descriptions + routing validator   [tag: wave-2-complete]
43df6c6 refactor(skills): wave 2a — 9 shared reference files for OWL strategy
bb88e5c refactor(skills): wave 1 — governance foundation                     [tag: wave-1-complete]
0237715 chore: clear pre-existing ruff errors blocking wave-1 DoD
e6509ad docs(skills): add workflow-improvement research bundle and reports
215ea05 feat(enews): ...                                                      [tag: wave-0-baseline, main]
```

### Working tree
- Clean (this handoff doc will add one more commit).
- Original sky-316 work still stashed as `stash@{0}: sky-316 wip pre-refactor-branch`.

### Files landed in Wave 3a + 3b
**Wave 3a — shared files:**
- `.claude/skills/_shared/pattern-catalog.md`
- `.claude/skills/_shared/mapping-evaluation.md`
- `.claude/skills/_shared/sssom-semapv-recipes.md`
- `.claude/skills/_shared/modularization-and-bridges.md`
- `.claude/skills/_shared/worked-examples/ensemble/README.md`
- `.claude/skills/_shared/worked-examples/microgrid/README.md`

**Wave 3b — all 8 SKILL.md files gained four new bottom sections + citations per matrix:**
- `ontology-conceptualizer`: cites `pattern-catalog.md`, `modularization-and-bridges.md`.
- `ontology-architect`: cites `pattern-catalog.md`, `modularization-and-bridges.md`.
- `ontology-mapper`: cites `mapping-evaluation.md`, `sssom-semapv-recipes.md`.
- `ontology-validator`: cites `mapping-evaluation.md`.
- `ontology-scout`: cites `modularization-and-bridges.md`.
- Other 3 (`requirements`, `curator`, `sparql-expert`) got the 4 new sections but no new citations.

---

## What Wave 3c needs to do

Wave 3c is the substantive redline. Each skill's `## Core Workflow` section needs restructuring per the research report (`docs/research/2026-04-21-workflow-improvement-report.md` §§ A.1–A.8). These are *not* cosmetic — they change step ordering, add mandatory gates, and require new artifacts.

Recommended commit split: one commit per skill, or cluster by pipeline (A = requirements/scout/conceptualizer/architect/validator; B = mapper; C = curator; cross-cut = sparql-expert). Per-skill is cleaner for review; cluster is faster to commit.

### Per-skill redline summary (what to add to `## Core Workflow`)

| Skill | Workflow changes |
|---|---|
| `ontology-requirements` | Add **Step 0: Scope test** — is this ontology vs mapping vs app-logic? Explicit non-goals section. CQ matrix w/ priority, expected-answer shape, testability, owner. Require `docs/requirements-approval.yaml` before handoff. |
| `ontology-scout` | Add **reuse-decision matrix** (scope fit, license, maintenance, import size, identifier policy, profile implications). Add **module-vs-import-vs-bridge** step citing `modularization-and-bridges.md § 6`. Require a **rejection rationale** for every non-selected candidate. |
| `ontology-conceptualizer` | Add **mandatory BFO ambiguity checkpoint** w/ confidence escalation (ambiguity ≥ 2 → Class C human review). Add **relation-semantics sheet step** per `relation-semantics.md`. Add **closure/open-world review** per `closure-and-open-world.md`. Add **CQ coverage map** (every Must-Have CQ appears in `axiom-plan.yaml`). |
| `ontology-architect` | **Reorder:** profile+reasoner pick → pattern/template strategy → encode → mandatory gates → package. Add **construct-support matrix** (flag non-EL axioms if ELK targeted) per `owl-profile-playbook.md § 3`. **Prefer ROBOT templates / DOSDP** over freehand OWL. Make `robot validate-profile` + `robot reason` + `robot report` **mandatory before handoff** (already in Progress Criteria, enforce in workflow order). |
| `ontology-mapper` | **Formalize phases:** candidate → curation → evaluation → repair. Require full SSSOM metadata per `sssom-semapv-recipes.md § 2`. Add **consistency + conservativity checks** before merge (runs reasoner on merged source + target + bridge). Expand quality report w/ OAEI metrics when gold set exists. |
| `sparql-expert` | Add **CQ decomposition step** (if a CQ has multiple variables, decompose to a query plan). Make **preflight execution mandatory** (not just parse). Pair every query with an **expected-results contract** per `cq-traceability.md`. |
| `ontology-validator` | **Explicit command order:** `validate-profile` → `reason` → `report` → `verify` (CQ) → `pyshacl` → CQ regression. **Severity thresholds:** ERROR blocks; WARN is tracked; INFO is logged. **Loopback target per failure type** (already in Loopback Triggers, enforce in workflow). |
| `ontology-curator` | Add **Step 0: Change classification** (annotation / structural / semantic / mapping / release-infra) — drives which downstream skills are activated. On upstream change → **ODK import-refresh + full CQ regression** per `odk-and-imports.md`. Add **release-note provenance step** (diff → notes, with citation to each structural change). |

### Wave 3 DoD (run before tagging `wave-3-complete`)

```bash
# 4 new shared files exist (already landed in 3a)
for f in pattern-catalog mapping-evaluation sssom-semapv-recipes modularization-and-bridges; do
  test -f ".claude/skills/_shared/$f.md" || echo "MISSING: $f"
done
# 4 new sections present in every SKILL.md (already landed in 3b)
for skill in ontology-{requirements,scout,conceptualizer,architect,mapper,validator,curator} sparql-expert; do
  for section in "Progress Criteria" "LLM Verification Required" "Loopback Triggers" "Worked Examples"; do
    grep -q "^## $section" ".claude/skills/$skill/SKILL.md" || echo "MISSING: $skill / $section"
  done
done
# Worked-example stubs present
test -d .claude/skills/_shared/worked-examples/ensemble
test -d .claude/skills/_shared/worked-examples/microgrid
# Routing + lint still pass
uv run python scripts/validate_description_routing.py
uv run ruff check .
# (Wave 3c specific) Core Workflow sections show the redline — read each visually.
```

Then tag: `git tag wave-3-complete`.

---

## Decisions locked (do not re-litigate)

All Wave 2 decisions still apply. In addition, from Wave 3a/3b:

| Decision | Choice |
|---|---|
| Wave 3a shared-file split | Kept `pattern-catalog.md` (ODPs) separate from `axiom-patterns.md` (axioms); they cross-reference. |
| Mapping authoring vs evaluation split | `sssom-semapv-recipes.md` = producing; `mapping-evaluation.md` = gate-checking. Mapper reads both; validator reads only evaluation. |
| `modularization-and-bridges.md` scope | When/why modularize (complements *how* in `odk-and-imports.md`). |
| New-section content depth | ~20 lines each, offload to shared files (per CONVENTIONS.md § Skill Authoring Standard). |
| Class taxonomy in `## LLM Verification Required` | Every skill labels each operation A / B / C / D per `llm-verification-patterns.md § 2`. Validator is D-heavy (never paraphrase tool output). |
| Loopback Triggers table structure | Two directions recorded: *incoming* (what this skill receives) vs. *raised* (what this skill sends upstream). Matches routing table in CONVENTIONS.md. |
| Wave 3 commit cadence | Split into 3a / 3b / 3c. 3a + 3b are complete. No intermediate tags — only `wave-3-complete` once 3c lands. |
| Worked-example links | Marked `*(Wave 4)*` inline so readers don't chase 404s. Paths fixed now; files land in Wave 4. |

---

## Gotchas (new since Wave 2 handoff)

1. **Pre-commit hooks didn't reformat anything in Wave 3a/3b.** The Wave 2 handoff warned about ruff-format retry; that didn't trigger on these markdown-only commits. If a future commit touches `.py` files, expect the first attempt to fail.

2. **Worked-example links in SKILL.md point to Wave 4 files that don't exist yet.** Each is marked `*(Wave 4)*`. Do not try to follow them — they're stubs on purpose. Wave 4 populates the 16 files.

3. **`ontology-validator` Loopback Triggers table is the routing hub.** Other skills raise loopbacks *to* validator rarely; validator raises *from* every failure class. When extending `iteration-loopbacks.md` routing, validator's table is the canonical reference.

4. **Wave 3b added `Progress Criteria` items that reference Wave 4 artifacts.** E.g., `docs/requirements-approval.yaml`, `mappings/reports/{date}-{set-id}.md`. The skills reference these by path — those paths land when Wave 4 worked examples show them in context. Until Wave 4, they're specification-only.

5. **CHANGELOG Wave 3 entry is ordered 3b-first, 3a-second.** This is intentional (newer edits on top) and follows the pattern set by Wave 2 (`2b` before `2a`). If manually re-reading, start with the Wave 3a section for context.

6. **Wave 3c will be the largest single content lift.** Each Core Workflow rewrite is non-trivial — plan for it to be a full session, or split into ~3 commits (pipeline-A skills, pipeline-B+C, cross-cutting). Unlike 3a/3b which were mostly additive, 3c *restructures* existing content.

7. **Research report is the source of truth for Wave 3c redlines.** Read `docs/research/2026-04-21-workflow-improvement-report.md` §§ A.1 through A.8 before editing each skill. The per-skill redline summary in this handoff is a pointer, not a substitute.

---

## Critical file paths (as of wave-3b)

**Plan & handoff:**
- `~/.claude/plans/users-pooks-dev-ontology-skill-docs-res-bubbly-flamingo.md` — approved plan.
- [`HANDOFF-2026-04-21.md`](HANDOFF-2026-04-21.md) — original handoff (pre-Wave-1).
- [`HANDOFF-2026-04-21-wave2-complete.md`](HANDOFF-2026-04-21-wave2-complete.md) — Wave 2 handoff.
- This file — current handoff.
- [`CHANGELOG.md`](CHANGELOG.md) — per-wave log (now has Wave 3a + 3b entries).

**Research (source for Wave 3c redlines):**
- `docs/research/2026-04-21-workflow-improvement-report.md` §§ A.1–A.8.

**Wave 3c targets (to modify):**
- `.claude/skills/ontology-requirements/SKILL.md` — Core Workflow.
- `.claude/skills/ontology-scout/SKILL.md` — Core Workflow.
- `.claude/skills/ontology-conceptualizer/SKILL.md` — Core Workflow.
- `.claude/skills/ontology-architect/SKILL.md` — Core Workflow (largest redline).
- `.claude/skills/ontology-mapper/SKILL.md` — Core Workflow.
- `.claude/skills/ontology-validator/SKILL.md` — Core Workflow (explicit command order).
- `.claude/skills/ontology-curator/SKILL.md` — Core Workflow.
- `.claude/skills/sparql-expert/SKILL.md` — Core Workflow.

**Wave 4 targets (unchanged from prior handoff):**
- `.claude/skills/_shared/provenance-and-publication.md`
- `.claude/skills/_shared/github-actions-template.md`
- 16 files under `.claude/skills/_shared/worked-examples/{ensemble,microgrid}/{requirements,scout,conceptualizer,architect,mapper,validator,curator,sparql}.md`

---

## Todo state at pause

1. ✅ Wave 1 — complete and tagged.
2. ✅ Wave 2 — complete and tagged `wave-2-complete`.
3. ✅ Wave 3a — 4 shared files + worked-example stubs.
4. ✅ Wave 3b — 4 new sections + Wave 3 citations on all 8 skills.
5. ⬜ **Wave 3c** — per-skill workflow enhancements to `## Core Workflow` on all 8 skills (redline summary above; source in research report §§ A.1–A.8).
6. ⬜ Wave 3 DoD + tag `wave-3-complete`.
7. ⬜ Wave 4 — Author 8 ensemble worked-example files.
8. ⬜ Wave 4 — Author 8 microgrid worked-example files.
9. ⬜ Wave 4 — Create `provenance-and-publication.md` + `github-actions-template.md`.
10. ⬜ Wave 4 — Final E2E verification, tag `wave-4-complete`.
11. ⬜ Post-Wave-4 — squash-merge `refactor/skills-2026-04` → `main`.

---

## Quick-start for the new session

```bash
# 1) Confirm state
cd /Users/pooks/Dev/ontology_skill
git branch --show-current                        # refactor/skills-2026-04
git log --oneline wave-0-baseline..HEAD          # 10 commits (plus this handoff = 11)
git status --short                               # clean
uv run python scripts/validate_description_routing.py   # OK
uv run ruff check .                              # clean

# 2) Read the active handoff (this file) + prior ones if needed
cat docs/refactor/HANDOFF-2026-04-21-wave3b-complete.md
cat docs/refactor/HANDOFF-2026-04-21-wave2-complete.md   # Wave 3 + 4 plan
cat docs/refactor/CHANGELOG.md                            # Wave-by-wave log

# 3) Read per-skill redlines (source of truth for Wave 3c edits)
cat docs/research/2026-04-21-workflow-improvement-report.md | sed -n '/^#### A.1/,/^---/p'
# (repeat for §§ A.2 through A.8)

# 4) Begin Wave 3c: restructure Core Workflow in one skill at a time.
#    Recommended order (smallest redline first):
#      1. ontology-requirements
#      2. sparql-expert
#      3. ontology-scout
#      4. ontology-mapper
#      5. ontology-curator
#      6. ontology-conceptualizer
#      7. ontology-validator
#      8. ontology-architect (largest)
#    Commit per skill or per cluster (see above).
#
# 5) When 3c is done:
uv run python scripts/validate_description_routing.py
uv run ruff check .
# Update CHANGELOG with Wave 3c entry + overall Wave 3 summary.
git tag wave-3-complete
# Then begin Wave 4.
```
