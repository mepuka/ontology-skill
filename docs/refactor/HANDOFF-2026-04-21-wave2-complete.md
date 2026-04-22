# Handoff — Ontology Skills Refactor (after Wave 2)

**Session paused:** 2026-04-21 (after `wave-2-complete` tagged)
**Branch:** `refactor/skills-2026-04`
**Next session goal:** Execute Wave 3 (per-skill section additions + 4 shared files + per-skill workflow enhancements), then Wave 4 (16 worked-example files + publication/CI shared files + final E2E verification).

This supersedes [`HANDOFF-2026-04-21.md`](HANDOFF-2026-04-21.md). Read that doc for original plan context; this one is the delta since Wave 2 landed.

---

## TL;DR of what's done

- **Waves 0–2 landed.** Tags: `wave-0-baseline`, `wave-1-complete`, `wave-2-complete`.
- Governance (CONVENTIONS.md + SKILL-TEMPLATE.md + ontology-safety.md + iteration-loopbacks.md + CHANGELOG.md) is in place.
- 9 OWL-strategy shared files created and cited from skills per the plan's Wave 2 matrix.
- All 8 skill `description:` blocks rewritten; every baseline trigger keyword preserved (validated automatically by `scripts/validate_description_routing.py`).
- All 8 skills' `## Shared Reference Materials` sections updated with Wave 2 citations.
- Routing validator + failure-ledger-pattern + loopback protocol in use.

---

## Current state

### Branch
- **Branch:** `refactor/skills-2026-04`
- **Base:** off `main` at `215ea05` (the tip when branching).
- **Tip:** `814a60e docs(refactor): update changelog for wave 2 complete`
- **Tags:** `wave-0-baseline` (at `215ea05`), `wave-1-complete` (at `bb88e5c`), `wave-2-complete` (at `4323edf`).

### Commits since branching (7 total)
```
814a60e docs(refactor): update changelog for wave 2 complete
4323edf refactor(skills): wave 2b — skill descriptions + routing validator   [tag: wave-2-complete]
43df6c6 refactor(skills): wave 2a — 9 shared reference files for OWL strategy
bb88e5c refactor(skills): wave 1 — governance foundation                     [tag: wave-1-complete]
0237715 chore: clear pre-existing ruff errors blocking wave-1 DoD
e6509ad docs(skills): add workflow-improvement research bundle and reports
215ea05 feat(enews): ...                                                      [tag: wave-0-baseline, main]
```

### Working tree
- Clean (no uncommitted changes).
- Research docs available at `docs/research/` (cherry-picked onto refactor in `e6509ad`).
- Original sky-316 work is stashed: `stash@{0}: sky-316 wip pre-refactor-branch`.

### Files created/modified so far
- `.claude/skills/CONVENTIONS.md` (modified — safety rules 11–16, Iteration/Loopback Protocol, 14-item authoring standard, maintain/curate/evolve synonyms).
- `.claude/skills/SKILL-TEMPLATE.md` (rewritten — 4 new section placeholders, artifact+command-per-step).
- `.claude/rules/ontology-safety.md` (modified — rules 1–16 in sync with CONVENTIONS.md).
- `.claude/skills/_shared/iteration-loopbacks.md` (new — 27-class failure routing table, retry gates, anti-thrash guard).
- `.claude/skills/_shared/llm-verification-patterns.md` (new — 4 verification classes, Class-B prompt template, per-skill matrix).
- `.claude/skills/_shared/owl-profile-playbook.md` (new — EL/QL/RL/DL decision + construct-support matrix + merge-then-validate-profile preflight).
- `.claude/skills/_shared/closure-and-open-world.md` (new — OWA vs CWA, closure patterns, SHACL complement).
- `.claude/skills/_shared/shacl-patterns.md` (new — shape templates, severity, pass/fail).
- `.claude/skills/_shared/robot-template-preflight.md` (new — preflight checklist, Python helper, failure patterns).
- `.claude/skills/_shared/odk-and-imports.md` (new — ODK vs POD, extraction methods, manifest schema).
- `.claude/skills/_shared/relation-semantics.md` (new — obj-vs-data property, RO cheat sheet, characteristics matrix).
- `.claude/skills/_shared/bfo-decision-recipes.md` (new — 3 decision recipes, ambiguity register).
- `.claude/skills/_shared/cq-traceability.md` (new — trace-chain CSV schema, expected-results contract).
- All 8 `.claude/skills/*/SKILL.md` — description rewritten + new citations in Shared Reference Materials.
- `scripts/validate_description_routing.py` (new — enforces trigger-keyword preservation).
- `docs/refactor/CHANGELOG.md` (new — wave-by-wave log).
- `docs/refactor/HANDOFF-2026-04-21.md` (new — previous handoff).
- This file.

---

## Decisions locked (do not re-litigate)

All decisions from the original handoff still apply. In addition:

| Decision | Choice |
|---|---|
| Tokenizer for routing validator | Keeps hyphens as intra-token characters; so `upper-ontology` is one token. Use spaces in descriptions where individual words are trigger keywords (e.g., `BFO upper ontology` not `BFO upper-ontology`). |
| `EXPECTED_OVERLAP` thresholds | architect↔conceptualizer = 10, architect↔validator = 10. These pairs share the largest legitimate vocabulary; other pairs default to 6–8. |
| `GENERIC_TOKENS` filter | Added `via` alongside `a/an/and/the/etc`. Inflected forms (`validates` vs `validate`) are both in the list. |
| Routing validator deployment | Not yet wired into pre-commit. Wave 4 DoD adds it to CI. For now, run manually: `uv run python scripts/validate_description_routing.py`. |
| Cherry-pick of research bundle | `e6509ad` intentional — research files live on both `sky-316` and `refactor/skills-2026-04`. When both merge to `main`, the second merge is a no-op (identical content). |

---

## Immediate next steps

### Step 0 — Resume discovery
```bash
cd /Users/pooks/Dev/ontology_skill
git branch --show-current                        # should be refactor/skills-2026-04
git log --oneline wave-0-baseline..HEAD          # should show 7 commits
git tag | grep wave-                             # should list 3 wave tags
git status --short                               # should be clean
uv run python scripts/validate_description_routing.py   # should print OK
```

### Step 1 — Begin Wave 3

Wave 3 is the largest content wave. Per the plan:

**Goal:** Add 4 required sections to every SKILL.md, create 4 more shared files, seed worked-example directories, apply per-skill workflow enhancements.

**Files to create (4 shared + 2 worked-example READMEs + 2 stub dirs):**

| Path | Purpose |
|---|---|
| `.claude/skills/_shared/pattern-catalog.md` | DOSDP; value partition; n-ary relation; part-whole; role; participation; info-realization. Cited by conceptualizer + architect. |
| `.claude/skills/_shared/mapping-evaluation.md` | Confidence tiers; clique SPARQL; cross-domain exactMatch rule; precision/recall. Cited by mapper + validator. |
| `.claude/skills/_shared/sssom-semapv-recipes.md` | SEMAPV justification catalog; lexmatch→SSSOM recipe; LLM-verified recipe; required YAML header. Cited by mapper. |
| `.claude/skills/_shared/modularization-and-bridges.md` | Module granularity; split triggers; bridge patterns; merge pitfalls. Cited by scout + conceptualizer + architect. |
| `.claude/skills/_shared/worked-examples/ensemble/README.md` | Scope, 5 CQs, target axiom patterns (stub). |
| `.claude/skills/_shared/worked-examples/microgrid/README.md` | Scope, 5 CQs, target axiom patterns (stub). |
| (dirs) `.claude/skills/_shared/worked-examples/ensemble/` and `.../microgrid/` | Empty directories for Wave 4 to populate. |

**Files to modify (all 8 SKILL.md):**

Insert 4 new sections at the bottom of each SKILL.md, using the placeholder templates from SKILL-TEMPLATE.md and CONVENTIONS.md § Skill Authoring Standard items 11–14:
1. `## Progress Criteria` — checkable-command list.
2. `## LLM Verification Required` — per-operation verification table.
3. `## Loopback Triggers` — failure→upstream-skill routing table.
4. `## Worked Examples` — two concrete links (ensemble + microgrid); in Wave 3 these are placeholders, Wave 4 fills them in.

Cap each section at ~20 lines (offload to `_shared/*.md`).

Also add Wave 3 citations per this matrix (additive on top of Wave 2):

| Skill | Wave 3 citations |
|---|---|
| `ontology-conceptualizer` | `pattern-catalog.md`, `modularization-and-bridges.md` |
| `ontology-architect` | `pattern-catalog.md`, `modularization-and-bridges.md` |
| `ontology-mapper` | `mapping-evaluation.md`, `sssom-semapv-recipes.md` |
| `ontology-validator` | `mapping-evaluation.md` |
| `ontology-scout` | `modularization-and-bridges.md` |

**Per-skill workflow enhancements (applied to the `## Core Workflow` section of each skill):**

- `ontology-requirements` — add Step 0 (ontology-vs-mapping-vs-app-logic scope test); require CQ matrix with priority, expected answer shape, testability, owner; require non-goals section; require approval artifact.
- `ontology-scout` — add reuse-decision matrix (scope fit, license, maintenance, import size, identifier policy, profile implications); add module-vs-import-vs-bridge step; require rejection rationale for non-selected candidates.
- `ontology-conceptualizer` — add mandatory BFO ambiguity checkpoint with confidence-level escalation; add relation-semantics sheet step; add closure/open-world review; add CQ coverage map.
- `ontology-architect` — reorder: profile+reasoner → pattern/template strategy → encode → mandatory gates → package. Add construct-support matrix (flag non-EL if ELK targeted); prefer ROBOT templates/DOSDP over freehand OWL; make `robot validate-profile` + `robot reason` mandatory before handoff.
- `ontology-mapper` — formalize phases (candidate / curation / evaluation / repair); require SSSOM metadata; add consistency/conservativity checks before merge; expand quality report with OAEI-style precision/recall.
- `sparql-expert` — add CQ decomposition step; make preflight execution mandatory; pair every query with expected-results contract.
- `ontology-validator` — explicit command order (`validate-profile` → `reason` → `report` → `verify` → `pyshacl` → CQ regression); severity thresholds; loopback target per failure type.
- `ontology-curator` — add Step 0 (change classification: annotation/structural/semantic/mapping/release-infra); require ODK import-refresh + full regression on upstream change; add release-note provenance step.

**Split Wave 3 into commits:**

Recommended approach:
- **Wave 3a:** 4 shared files + 2 worked-example READMEs + directory creation.
- **Wave 3b:** Add 4 new sections to all 8 skills (stub links for Wave 4); update citations per matrix.
- **Wave 3c:** Apply per-skill workflow enhancements (one commit per skill or grouped by cluster; 8 skills is a lot).
- **Wave 3 DoD:** run checks, update CHANGELOG, tag `wave-3-complete`.

**Wave 3 DoD (from plan):**
```bash
# Every SKILL.md has all 4 new sections in order
for skill in ontology-{requirements,scout,conceptualizer,architect,mapper,validator,curator} sparql-expert; do
  for section in "Progress Criteria" "LLM Verification Required" "Loopback Triggers" "Worked Examples"; do
    grep -q "^## $section" ".claude/skills/$skill/SKILL.md" || echo "MISSING: $skill / $section"
  done
done
# 4 new shared files exist and are referenced
for f in pattern-catalog mapping-evaluation sssom-semapv-recipes modularization-and-bridges; do
  test -f ".claude/skills/_shared/$f.md" && grep -l "$f" .claude/skills/*/SKILL.md >/dev/null
done
# Worked-example stubs present
test -d .claude/skills/_shared/worked-examples/ensemble
test -d .claude/skills/_shared/worked-examples/microgrid
# Routing still passes
uv run python scripts/validate_description_routing.py
# ruff clean
uv run ruff check .
```

### Step 2 — Wave 4

Wave 4 is the worked-examples content lift. Per plan:

**Files created:**

| Path | Purpose |
|---|---|
| `.claude/skills/_shared/provenance-and-publication.md` | PROV-O basics; versioning (OBO date vs semver); content negotiation; FAIR; dereferenceable IRI. |
| `.claude/skills/_shared/github-actions-template.md` | Monorepo CI skeleton targeting `ontologies/{name}/` layout; reason + report + CQ + pyshacl + release jobs. |

**16 worked-example files (8 ensemble + 8 microgrid)** under `.claude/skills/_shared/worked-examples/{ensemble,microgrid}/`. One file per skill. Content per plan § Wave 4.

**Final E2E verification** per plan § Verification. Tag `wave-4-complete`. Squash-merge to `main`.

### Post-Wave-4 options (deferred decisions)

- Wave 5 (skill-level evaluation harness) — still deferred.
- Conditional `ontology-architect` split — decide only if post-Wave-4 routing observations show overload.
- Helper skills (`ontology-build-engineer`, `ontology-reasoning-debugger`) — revisit if needed.

---

## Gotchas (new since Wave 1)

1. **Pre-commit ruff-format reformats files and fails the first commit.** `git status` after a failed commit will show `AM` / `MM` — just `git add <file>` again and re-commit.

2. **The routing validator uses `git show wave-0-baseline:...`.** The tag must exist locally. If the new session is on a fresh clone, fetch tags first or use `--skip-missing-baseline`.

3. **Skills use hyphenated phrases like `BFO-aligned`.** The tokenizer in `validate_description_routing.py` treats `BFO-aligned` as a single token, not `BFO` + `aligned`. If you need a specific trigger word to survive validation, use spaces: e.g., `BFO upper ontology`, not `BFO upper-ontology`.

4. **CONVENTIONS.md safety rule ordering.** Rules 1–10 in the file's `§ Safety Rules` are the original non-negotiables (unchanged). Rules 11–16 are the new ones added in Wave 1. `ontology-safety.md` mirrors this exactly. If you need to add a new rule, append at rule 17+ — do not renumber.

5. **Sevocab-to-refactor-branch migration.** The `sky-316-...` branch has active uncommitted work stashed (`stash@{0}: sky-316 wip pre-refactor-branch`). When sky-316 eventually merges to main, rebase `refactor/skills-2026-04` on main rather than trying to merge. The research-artifacts commit on both branches will dedupe cleanly.

6. **Pre-existing ruff fix from Wave 1.** Commit `0237715` quieted 4 pre-existing ruff errors on main (generate_viewer.py, run_cq_tests.py, validate_sssom.py). Those fixes are additive, not a blocker to track.

7. **`ontology-curator` still NOT renamed.** The plan reports sometimes say `ontology-maintainer`. Keep `ontology-curator`. Synonyms are handled in CONVENTIONS.md § Shared Terminology.

---

## Critical file paths (as of wave-2-complete)

**Plan & handoff:**
- `~/.claude/plans/users-pooks-dev-ontology-skill-docs-res-bubbly-flamingo.md` — approved plan (canonical).
- [`HANDOFF-2026-04-21.md`](HANDOFF-2026-04-21.md) — original handoff (pre-Wave-1).
- This file — current handoff.
- [`CHANGELOG.md`](CHANGELOG.md) — per-wave log.

**Research (now on refactor branch):**
- `docs/research/2026-04-21-workflow-improvement-report.md` — long report.
- `docs/research/deep-research-report.md` — short report.
- (plus context bundle and prompt)

**Governance (Wave 1 — done):**
- `.claude/skills/CONVENTIONS.md`
- `.claude/skills/SKILL-TEMPLATE.md`
- `.claude/rules/ontology-safety.md`
- `.claude/skills/_shared/iteration-loopbacks.md`

**Wave 2 shared files (done):**
- `.claude/skills/_shared/llm-verification-patterns.md`
- `.claude/skills/_shared/owl-profile-playbook.md`
- `.claude/skills/_shared/closure-and-open-world.md`
- `.claude/skills/_shared/shacl-patterns.md`
- `.claude/skills/_shared/robot-template-preflight.md`
- `.claude/skills/_shared/odk-and-imports.md`
- `.claude/skills/_shared/relation-semantics.md`
- `.claude/skills/_shared/bfo-decision-recipes.md`
- `.claude/skills/_shared/cq-traceability.md`

**Wave 3 targets (to create):**
- `.claude/skills/_shared/pattern-catalog.md`
- `.claude/skills/_shared/mapping-evaluation.md`
- `.claude/skills/_shared/sssom-semapv-recipes.md`
- `.claude/skills/_shared/modularization-and-bridges.md`
- `.claude/skills/_shared/worked-examples/ensemble/README.md`
- `.claude/skills/_shared/worked-examples/microgrid/README.md`
- (plus the 8 skill files, all modified with 4 new sections + per-skill enhancements)

**Wave 4 targets (to create):**
- `.claude/skills/_shared/provenance-and-publication.md`
- `.claude/skills/_shared/github-actions-template.md`
- `.claude/skills/_shared/worked-examples/ensemble/{requirements,scout,conceptualizer,architect,mapper,validator,curator,sparql}.md` × 8
- `.claude/skills/_shared/worked-examples/microgrid/{requirements,scout,conceptualizer,architect,mapper,validator,curator,sparql}.md` × 8

**Routing / validation:**
- `scripts/validate_description_routing.py`

---

## Todo state at pause

1. ✅ Wave 1 — complete and tagged.
2. ✅ Wave 2 — complete and tagged `wave-2-complete`.
3. ⬜ Wave 3 — Create 4 shared files (pattern-catalog, mapping-evaluation, sssom-semapv-recipes, modularization-and-bridges).
4. ⬜ Wave 3 — Create worked-example stubs (ensemble + microgrid READMEs).
5. ⬜ Wave 3 — Add 4 new sections (Progress Criteria / LLM Verification / Loopback Triggers / Worked Examples) to all 8 SKILL.md files.
6. ⬜ Wave 3 — Apply per-skill workflow enhancements.
7. ⬜ Wave 3 — Run DoD, commit, tag `wave-3-complete`.
8. ⬜ Wave 4 — Author 8 ensemble worked-example files.
9. ⬜ Wave 4 — Author 8 microgrid worked-example files.
10. ⬜ Wave 4 — Create `provenance-and-publication.md` + `github-actions-template.md`.
11. ⬜ Wave 4 — Final E2E verification, tag `wave-4-complete`.
12. ⬜ Post-Wave-4 — squash-merge `refactor/skills-2026-04` → `main`.

---

## Quick-start for the new session

```bash
# 1) Confirm state
cd /Users/pooks/Dev/ontology_skill
git branch --show-current                        # refactor/skills-2026-04
git log --oneline wave-0-baseline..HEAD          # 7 commits
uv run python scripts/validate_description_routing.py   # OK

# 2) Read the active handoff (this file) and the plan
cat docs/refactor/HANDOFF-2026-04-21-wave2-complete.md
cat ~/.claude/plans/users-pooks-dev-ontology-skill-docs-res-bubbly-flamingo.md

# 3) Read the two research reports for per-skill redline detail
#    (docs/research/2026-04-21-workflow-improvement-report.md §§ A.1-A.8 are the
#     per-skill workflow redlines you'll implement in Wave 3c.)

# 4) Begin Wave 3a: create the 4 new shared files + worked-example stubs
#    (pattern-catalog, mapping-evaluation, sssom-semapv-recipes,
#     modularization-and-bridges, ensemble/README, microgrid/README).
```
