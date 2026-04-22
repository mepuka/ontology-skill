# Handoff — Ontology Skills Refactor (after Wave 3)

**Session paused:** 2026-04-21 (after Wave 3c committed and tagged `wave-3-complete`).
**Branch:** `refactor/skills-2026-04`
**Next session goal:** Execute Wave 4 — 16 per-skill worked-example files + 2 publication/CI shared files + final E2E verification, tag `wave-4-complete`, then squash-merge `refactor/skills-2026-04` → `main`.

This supersedes [`HANDOFF-2026-04-21-wave3b-complete.md`](HANDOFF-2026-04-21-wave3b-complete.md). Read that doc for the original Wave 4 plan; this one is the delta since Wave 3c landed and notes a few Wave-3c-driven updates to Wave 4 scope.

---

## TL;DR of what's done

- **Waves 0–3 all landed + tagged.** Governance, 13 shared reference files, 8 skill descriptions with a routing validator, 4 new bottom sections on every SKILL.md, and full per-skill Core Workflow redlines on all 8 skills.
- **Wave 3c landed this session** (9 commits): one per-skill commit per SKILL.md, plus a CHANGELOG rollup. 38 signature new Step/Level headings land across the 8 skills, each tool-gated with a named artifact.
- **Wave 4 pending** — worked examples, publication/CI shared files, final E2E verification, then tag + squash-merge.

---

## Current state

### Branch
- **Branch:** `refactor/skills-2026-04`
- **Base:** off `main` at `215ea05`
- **Tip:** `16ce986 docs(refactor): CHANGELOG entry for wave 3c + overall wave 3 summary`
- **Tags:** `wave-0-baseline` (at `215ea05`), `wave-1-complete` (at `bb88e5c`), `wave-2-complete` (at `4323edf`), `wave-3-complete` (at `16ce986`). Wave 4 tag `wave-4-complete` pending.

### Commits since branching (19 total)
```
16ce986 docs(refactor): CHANGELOG entry for wave 3c + overall wave 3 summary   [tag: wave-3-complete]
4c23f79 refactor(skills): wave 3c.8 — ontology-architect Core Workflow redline
15503fd refactor(skills): wave 3c.7 — ontology-validator Core Workflow redline
5cf3851 refactor(skills): wave 3c.6 — ontology-conceptualizer Core Workflow redline
1b2c867 refactor(skills): wave 3c.5 — ontology-curator Core Workflow redline
3142afe refactor(skills): wave 3c.4 — ontology-mapper Core Workflow redline
043ad01 refactor(skills): wave 3c.3 — ontology-scout Core Workflow redline
a1be8da refactor(skills): wave 3c.2 — sparql-expert Core Workflow redline
e7fa93a refactor(skills): wave 3c.1 — ontology-requirements Core Workflow redline
400b3c5 docs(refactor): add wave-3b-complete handoff for next session
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

### Wave 3c — 38 signature new headings landed
Per-skill counts (verified by spot-check script):

| Skill | New Steps/Levels |
|---|---|
| `ontology-requirements` | 4 (Steps 0, 2.5, 7.5, 9) |
| `sparql-expert` | 4 (Steps 0, 2.5, 4.5, 5.5) |
| `ontology-scout` | 3 (Steps 0, 3.5, 6) |
| `ontology-mapper` | 4 (Steps 0, 5.1, 5.6, 8) |
| `ontology-curator` | 6 (Steps 0, 1.5, 3.5, 5.6, 6.5, 8) |
| `ontology-conceptualizer` | 5 (Steps 0, 3.1, 4.1, 5.1, 6.1) |
| `ontology-validator` | 6 (Step 0 + Levels 0, 3.5, 4.5, 5.5, 8) |
| `ontology-architect` | 6 (Steps 0, 2.5, 3.5, 6.5, 7.1, 8 + construct-support matrix) |

---

## What Wave 4 needs to do

Wave 4 is the last content wave before merge. Split into three groups.

### Group A — 16 worked-example files (per-skill, per-scenario)

Two scenarios already have READMEs from Wave 3a:
- `.claude/skills/_shared/worked-examples/ensemble/README.md` — music ensemble, 5 CQs (CQ-E-001..005).
- `.claude/skills/_shared/worked-examples/microgrid/README.md` — community microgrid, 5 CQs (CQ-M-001..005).

Each scenario gets 8 per-skill files for a total of **16 files**:

```
.claude/skills/_shared/worked-examples/ensemble/
├── requirements.md        # CQ elicitation, Step 9 approval.yaml stub
├── scout.md               # MIMO reuse, imports-manifest row, rejection rationale
├── conceptualizer.md      # value-partition for pitch, role for seat, N-ary for performance, closure review
├── architect.md           # StringQuartet qualified cardinality, DOSDP for instrument-family, template preflight
├── mapper.md              # MIMO↔music-ontology lexmatch + Class B review; clique violinist↔fiddler↔player
├── validator.md           # 7-level run with injected CQ-E-001 failure routed to architect
├── curator.md             # deprecation of experimental role subclass + replacement + CQ impact
└── sparql.md              # SPARQL for each CQ-E-001..005; COUNT vs row-shape pitfall on CQ-E-003

.claude/skills/_shared/worked-examples/microgrid/
├── requirements.md        # stakeholder-need traceability for dispatch-event CQ-M-002
├── scout.md               # OEO import vs schema.org bridge; manifest row for pinned OEO
├── conceptualizer.md      # part-whole topology; BFO placement for dispatch event vs dispatch role; OEO layering
├── architect.md           # hasPart ∘ locatedIn → locatedIn EL-safe; SHACL for telemetry; equivalence-bridge failure
├── mapper.md              # cross-domain exactMatch between device class and schema.org/Product caught by the rule
├── validator.md           # EL-safe subset + DL release gate; mapping-set validation; diff vs prior release
├── curator.md             # OEO import refresh; obsolete-term cascade to mapper; release-notes provenance
└── sparql.md              # property-path query for transitive locatedIn; entailment-regime declaration for CQ-M-001
```

Each file should be ~40–80 lines, cite the relevant Core Workflow steps by number, and show the actual artifact each step produces (not just prose).

### Group B — 2 new shared files

```
.claude/skills/_shared/provenance-and-publication.md
  # Publication + FAIR/OBO publishing checklist from ontology-curator Step 5.6.
  # PURL setup, content negotiation, versioned IRIs, registry entries (OBO Foundry,
  # BioPortal, OLS), publication-metadata check rows. Cited by curator + validator.

.claude/skills/_shared/github-actions-template.md
  # CI template: routing validator, ruff, robot validate-profile / reason / report,
  # pyshacl, CQ regression, SSSOM validate, mapping gates. Hooks into validator's
  # L0-L6 command order. Cited by validator + curator.
```

### Group C — Final E2E verification + squash-merge

```bash
# All 4 new sections present + Wave 3 citations + Wave 3c signature headings
# (reuse the Wave 3c verification script from the CHANGELOG)

# Every worked-example file exists
for scenario in ensemble microgrid; do
  for skill in requirements scout conceptualizer architect mapper validator curator sparql; do
    test -f ".claude/skills/_shared/worked-examples/$scenario/$skill.md" \
      || echo "MISSING: $scenario/$skill.md"
  done
done

# New shared files exist
test -f .claude/skills/_shared/provenance-and-publication.md
test -f .claude/skills/_shared/github-actions-template.md

# Routing + lint still pass
uv run python scripts/validate_description_routing.py
uv run ruff check .
uv run mypy src/

# Read each worked-example file visually for plausibility (no LLM paraphrase of
# tool output; show real artifact shapes)
```

Then tag `wave-4-complete` and squash-merge `refactor/skills-2026-04` → `main`.

---

## Decisions locked (carried forward + new from Wave 3c)

All prior-wave decisions still apply. New decisions from Wave 3c:

| Decision | Choice |
|---|---|
| Wave 3c commit granularity | One commit per skill (8 commits) + one CHANGELOG commit. Cleanest for review; easy per-skill rollback. |
| "New shared-reference dependencies" from research report §§ A.1–A.8 | Many were consolidated into existing Wave 2 shared files. No new shared files created in Wave 3c. Wave 4 adds the remaining 2 (`provenance-and-publication.md`, `github-actions-template.md`). |
| Wave 3c additions vs restructuring | 7 of 8 skills are additive (new Steps/Levels inserted). sparql-expert removed the standalone "Entailment Regime Awareness" section because Step 2.5 subsumes it. |
| Phase labeling | Only ontology-mapper got explicit phase labels (candidate → curation → evaluation → repair). Other skills kept implicit ordering. |
| Step numbering conventions | Used `.0 / .1 / .5` subscripts to insert between existing steps without renumbering existing content. Preserves commit blame clarity. |
| Wave 3c references Wave 4 artifacts | Several redlines reference artifacts Wave 4 worked examples will show in context (e.g., `docs/requirements-approval.yaml`, `validation/handoff-manifest.yaml`). These are specification-only until Group A files land. |

---

## Gotchas (new since Wave 3b handoff)

1. **Wave 3c commit messages carry the detail.** Each of the 8 per-skill commits has a multi-paragraph body explaining exactly what changed and why. `git log --oneline wave-2-complete..HEAD` gives the summary; `git show {sha}` gives the full rationale per skill. Read the commit bodies, not just the CHANGELOG, when reviewing.

2. **Cross-references between Wave 3c redlines and Wave 4 files.** Several Wave 3c headings explicitly cite artifacts Wave 4 worked examples will produce — e.g., architect's Step 8 "Handoff Packaging" references `cq-implementation-matrix.csv`, and curator's Step 6.5 references the release-notes template. When authoring a Wave 4 worked-example file, pattern-match the exact YAML / path shape from the corresponding Core Workflow step so the cross-link round-trips.

3. **The validator skill's Level 8 loopback routing table is now the canonical cross-skill routing map.** It mirrors `_shared/iteration-loopbacks.md` and the CONVENTIONS.md routing. When Wave 4 worked examples show loopback paths, they should route per this table — not invent new owners.

4. **Wave 3c introduced "Command Order" as a first-class concept in validator.** The validator SKILL.md now specifies an exact L0 → L1 → L2 → L4 → L3 → L4.5 → L5.5 → L6 sequence. Wave 4 worked examples that simulate a full validator run should walk through this order literally and show each level's raw output.

5. **Several new Step-numbered artifacts are YAML stubs that don't exist in any real ontology yet.** Requirements' `requirements-approval.yaml`, conceptualizer's ambiguity register format, curator's `change-approval.yaml`, architect's `validation/handoff-manifest.yaml`. Wave 4 is the first place these get concrete examples. Keep the YAML keys consistent with what the SKILL.md shows — don't drift.

6. **`mapper.md` has four phase labels on Steps 2-8.** If Wave 4's mapper worked-example files walk steps, carry the phase label through so readers see `Step 5.1 (evaluation)` in both the skill file and the worked example.

7. **Research report recommended 16 new worked-example files for specific ontology-engineering pitfalls** (e.g., ELK silently skipping qualified cardinality, exactMatch clique contamination, aggregate row-count mismatch). These aren't the same as the 16 Wave 4 worked-example files — they're narrower. The Wave 4 scenario-organized files should *include* several of these pitfalls embedded in the worked flow; they don't need standalone files. See research report §§ A.1–A.8 "Worked examples to add" sub-sections for the list.

8. **No `wave-3-complete` DoD gotchas surfaced.** All structural checks pass: 4 shared files exist, 4 bottom sections on all 8 skills, 38/38 signature Wave 3c headings present, routing validator passes, ruff clean. Branch is in a safe state to tag and pause.

---

## Critical file paths (as of wave-3-complete)

**Plan & handoff:**
- `~/.claude/plans/users-pooks-dev-ontology-skill-docs-res-bubbly-flamingo.md` — approved plan (full through Wave 4).
- [`HANDOFF-2026-04-21.md`](HANDOFF-2026-04-21.md) — original handoff (pre-Wave-1).
- [`HANDOFF-2026-04-21-wave2-complete.md`](HANDOFF-2026-04-21-wave2-complete.md) — Wave 2 handoff (has full Wave 3 + Wave 4 plan context).
- [`HANDOFF-2026-04-21-wave3b-complete.md`](HANDOFF-2026-04-21-wave3b-complete.md) — Wave 3b handoff (has Wave 3c plan).
- This file — current handoff (Wave 3 complete, Wave 4 plan).
- [`CHANGELOG.md`](CHANGELOG.md) — per-wave log. Wave 3 section is now complete with Wave 3c rollup.

**Research (source for Wave 4 detail):**
- `docs/research/2026-04-21-workflow-improvement-report.md` — per-skill worked-example lists live in the "Worked examples to add" sub-sections of §§ A.1–A.8.

**Wave 4 targets (to create):**
- `.claude/skills/_shared/provenance-and-publication.md` (new)
- `.claude/skills/_shared/github-actions-template.md` (new)
- 16 files under `.claude/skills/_shared/worked-examples/{ensemble,microgrid}/{requirements,scout,conceptualizer,architect,mapper,validator,curator,sparql}.md` (new)

**Post-Wave-4:**
- Squash-merge `refactor/skills-2026-04` → `main`. Single commit titled e.g. `refactor(skills): overhaul ontology-engineering skill pack (waves 0-4)` with the CHANGELOG summary as the body.

---

## Todo state at pause

1. ✅ Wave 1 — complete and tagged `wave-1-complete`.
2. ✅ Wave 2 — complete and tagged `wave-2-complete`.
3. ✅ Wave 3a — 4 shared files + 2 worked-example README stubs.
4. ✅ Wave 3b — 4 new sections + Wave 3 citations on all 8 skills.
5. ✅ Wave 3c — per-skill Core Workflow redlines on all 8 skills (38 new headings).
6. ✅ Wave 3 DoD + tag `wave-3-complete`.
7. ⬜ **Wave 4** — Author 8 ensemble worked-example files.
8. ⬜ **Wave 4** — Author 8 microgrid worked-example files.
9. ⬜ **Wave 4** — Create `provenance-and-publication.md` + `github-actions-template.md`.
10. ⬜ **Wave 4** — Final E2E verification, tag `wave-4-complete`.
11. ⬜ Post-Wave-4 — squash-merge `refactor/skills-2026-04` → `main`.

---

## Quick-start for the new session

```bash
# 1) Confirm state
cd /Users/pooks/Dev/ontology_skill
git branch --show-current                        # refactor/skills-2026-04
git log --oneline wave-0-baseline..HEAD          # 19 commits (plus this handoff = 20)
git status --short                               # clean
uv run python scripts/validate_description_routing.py   # OK
uv run ruff check .                              # clean
git tag --list | grep wave                       # wave-0..wave-3 complete

# 2) Read the active handoff (this file) + prior ones if needed
cat docs/refactor/HANDOFF-2026-04-21-wave3-complete.md
cat docs/refactor/HANDOFF-2026-04-21-wave2-complete.md   # Wave 3 + 4 plan
cat docs/refactor/CHANGELOG.md                            # Wave-by-wave log

# 3) Read the per-scenario READMEs + Core Workflow redlines in each skill
cat .claude/skills/_shared/worked-examples/ensemble/README.md
cat .claude/skills/_shared/worked-examples/microgrid/README.md
# Then glance at each SKILL.md ## Core Workflow for the Step/Level numbers you
# will cite from the worked-example file.

# 4) Read the research report's "Worked examples to add" sub-sections for per-
#    skill pitfall examples the worked-example files should showcase
cat docs/research/2026-04-21-workflow-improvement-report.md | sed -n '/Worked examples to add/,/---/p'

# 5) Begin Wave 4 — Group A (worked examples) is the biggest chunk.
#    Recommended order:
#      - Ensemble scenario (8 files), working skill-by-skill through the pipeline:
#          requirements → scout → conceptualizer → architect → mapper → validator
#          → curator → sparql
#      - Microgrid scenario (8 files), same order.
#      - Group B: provenance-and-publication.md + github-actions-template.md.
#      - Group C: final E2E + tag.
#
#    Commit cadence: one per scenario-skill pair (16 commits for Group A), or
#    cluster by scenario (2 commits). Per-pair is cleaner for review.

# 6) When Wave 4 is done:
uv run python scripts/validate_description_routing.py
uv run ruff check .
uv run mypy src/
# Update CHANGELOG with Wave 4 entry.
git tag wave-4-complete
# Then: squash-merge refactor/skills-2026-04 → main (human review before merge).
```
