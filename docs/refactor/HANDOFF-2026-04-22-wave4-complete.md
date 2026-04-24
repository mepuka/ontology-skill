# Handoff — Ontology Skills Refactor (after Wave 4)

**Session paused:** 2026-04-22 (after Wave 4 committed and tagged `wave-4-complete`).
**Branch:** `refactor/skills-2026-04`
**Next session goal:** squash-merge `refactor/skills-2026-04` → `main` after human review.

This supersedes [`HANDOFF-2026-04-21-wave3-complete.md`](HANDOFF-2026-04-21-wave3-complete.md).

---

## TL;DR of what's done

- **Waves 0–4 all landed + tagged.** All governance, shared reference
  files (15), skill descriptions (8), Core Workflow redlines (38
  signature headings), worked-example files (16), and the two new
  shared files for publication + CI.
- **Wave 4 landed this session** (19 commits): 16 per-file worked-
  example commits + 1 bundle for Group B shared files + CHANGELOG +
  this handoff.
- **All DoD checks passing.** Routing validator OK, ruff clean, mypy
  no issues, Wave 3c signature headings preserved, Wave 4 file-
  existence check clean.
- **Ready for squash-merge** to `main` pending human review.

---

## Current state

### Branch
- **Branch:** `refactor/skills-2026-04`
- **Base:** off `main` at `215ea05`
- **Tip:** `d456222 docs(refactor): CHANGELOG entry for wave 4 — worked examples + pub/CI` (plus this handoff commit = `d456222 + 1`).
- **Tags:** `wave-0-baseline`, `wave-1-complete`, `wave-2-complete`,
  `wave-3-complete`, `wave-4-complete` (tagged at the handoff commit).

### Commits since wave-3-complete (19 total)

```
d456222 docs(refactor): CHANGELOG entry for wave 4 — worked examples + pub/CI
fe2404e refactor(skills): wave 4.B — provenance-and-publication + github-actions-template
131ca57 refactor(skills): wave 4.A.16 — microgrid/sparql.md worked example
6bbb0d8 refactor(skills): wave 4.A.15 — microgrid/curator.md worked example
6d0ef94 refactor(skills): wave 4.A.14 — microgrid/validator.md worked example
0e7a6d1 refactor(skills): wave 4.A.13 — microgrid/mapper.md worked example
1de3fa9 refactor(skills): wave 4.A.12 — microgrid/architect.md worked example
552a183 refactor(skills): wave 4.A.11 — microgrid/conceptualizer.md worked example
516c336 refactor(skills): wave 4.A.10 — microgrid/scout.md worked example
442a939 refactor(skills): wave 4.A.9 — microgrid/requirements.md worked example
9a6a79e refactor(skills): wave 4.A.8 — ensemble/sparql.md worked example
79a7f5e refactor(skills): wave 4.A.7 — ensemble/curator.md worked example
04311dc refactor(skills): wave 4.A.6 — ensemble/validator.md worked example
308f72e refactor(skills): wave 4.A.5 — ensemble/mapper.md worked example
c390ff9 refactor(skills): wave 4.A.4 — ensemble/architect.md worked example
d5b8502 refactor(skills): wave 4.A.3 — ensemble/conceptualizer.md worked example
2ee8687 refactor(skills): wave 4.A.2 — ensemble/scout.md worked example
6050a9a refactor(skills): wave 4.A.1 — ensemble/requirements.md worked example
(+this handoff)
```

Total commits on the branch since `wave-0-baseline`: 39 (20 prior + 19
this session).

### Working tree
- Clean (this handoff doc will add one more commit).

### Wave 4 DoD checks (all pass)

```bash
# 16 worked-example files present with reasonable line counts (108-199)
$ for scenario in ensemble microgrid; do
    for skill in requirements scout conceptualizer architect mapper validator curator sparql; do
      test -f ".claude/skills/_shared/worked-examples/$scenario/$skill.md" || echo "MISSING"
    done
  done
# 0 MISSING

# 2 new shared files
$ test -f .claude/skills/_shared/provenance-and-publication.md         # OK (226 lines)
$ test -f .claude/skills/_shared/github-actions-template.md            # OK (306 lines)

# Wave 3c signature headings preserved
$ git diff --stat wave-3-complete..HEAD -- '.claude/skills/*/SKILL.md' # empty (no SKILL.md change)

# Routing + lint + types
$ uv run python scripts/validate_description_routing.py   # OK — all 8 descriptions preserve baseline tokens
$ uv run ruff check .                                     # All checks passed!
$ uv run mypy src/                                        # Success: no issues found
```

---

## What's left — squash-merge to `main`

The implementation is complete. The remaining work is a single human-
reviewed squash-merge:

```bash
# 1. Review the branch locally
git checkout refactor/skills-2026-04
git log --oneline wave-0-baseline..wave-4-complete            # 39 commits
git diff main..wave-4-complete --stat                         # total files touched

# 2. Squash-merge to main
git checkout main
git merge --squash refactor/skills-2026-04
# Commit with a message like:
#   refactor(skills): overhaul ontology-engineering skill pack (waves 0-4)
# Body = CHANGELOG summary (already written).

# 3. Tag the squashed release commit on main
git tag skills-pack-2026-04-release

# 4. Clean up the feature branch
# (Optional — keep the branch + tags for historical reference)
```

**Do not fast-forward merge.** The 39 commits are fine-grained for
reviewability but coarsen nicely into a single squash commit on `main`.
The `wave-*-complete` tags on the feature branch preserve the per-wave
history.

---

## Artifacts overview

### Skills directory structure

```
.claude/skills/
├── CONVENTIONS.md                       # Wave 1 — governance authority
├── SKILL-TEMPLATE.md                    # Wave 1 — skill template (14 sections)
├── _shared/                             # 15 reference files (13 Wave 2/3 + 2 Wave 4)
│   ├── anti-patterns.md
│   ├── axiom-patterns.md
│   ├── bfo-categories.md
│   ├── bfo-decision-recipes.md          # Wave 2
│   ├── closure-and-open-world.md        # Wave 2
│   ├── cq-traceability.md               # Wave 2
│   ├── github-actions-template.md       # Wave 4 (NEW)
│   ├── iteration-loopbacks.md           # Wave 1
│   ├── llm-verification-patterns.md     # Wave 2
│   ├── mapping-evaluation.md            # Wave 3a
│   ├── methodology-backbone.md
│   ├── modularization-and-bridges.md    # Wave 3a
│   ├── namespaces.json
│   ├── naming-conventions.md
│   ├── odk-and-imports.md               # Wave 2
│   ├── owl-profile-playbook.md          # Wave 2
│   ├── pattern-catalog.md               # Wave 3a
│   ├── provenance-and-publication.md    # Wave 4 (NEW)
│   ├── quality-checklist.md
│   ├── relation-semantics.md            # Wave 2
│   ├── robot-template-preflight.md      # Wave 2
│   ├── shacl-patterns.md                # Wave 2
│   ├── sssom-semapv-recipes.md          # Wave 3a
│   ├── tool-decision-tree.md
│   └── worked-examples/
│       ├── ensemble/                    # 1 README + 8 per-skill walkthroughs (Wave 4)
│       │   ├── README.md                # Wave 3a
│       │   ├── requirements.md          # Wave 4
│       │   ├── scout.md                 # Wave 4
│       │   ├── conceptualizer.md        # Wave 4
│       │   ├── architect.md             # Wave 4
│       │   ├── mapper.md                # Wave 4
│       │   ├── validator.md             # Wave 4
│       │   ├── curator.md               # Wave 4
│       │   └── sparql.md                # Wave 4
│       └── microgrid/                   # mirror structure
└── {8 skill directories with SKILL.md each}
```

### Wave 4 worked-example signature pitfalls

Each file embeds at least one concrete pitfall the worker must navigate.
The signature ones (called out in commit messages):

| Skill | Ensemble | Microgrid |
|---|---|---|
| requirements | bad-CQ-retrofit (falsifiability) | retrofit-gate trip |
| scout | weak-vocab rejection + bridge decision | BFO leak via IAO_0000030 |
| conceptualizer | role-type confusion + closure review | dispatch-event-vs-role ambiguity |
| architect | **ELK skips qualified cardinality** | **equivalence-bridge failure** |
| mapper | **clique contamination** | **cross-domain exactMatch floor** |
| validator | injected CQ-E-001 regime fail | dual-reasoner + mapping gates |
| curator | deprecate-not-delete (Safety Rule #4) | **OEO import-refresh chain** |
| sparql | **COUNT aggregate vs row-shape** | **regime mismatch + chain entailment** |

Bold = pitfalls called out in research report §§ A.1–A.8 as high-value
worked examples. All 8 research-report pitfalls are covered across the
16 files.

---

## Gotchas for the merge reviewer

1. **File sizes exceed handoff's 40-80 target.** Worked-example files
   are 108-199 lines. The increase is justified: each file walks 6-10
   Core Workflow steps with concrete artifact fragments (YAML, CSV,
   SPARQL, TTL). A 40-line file would have devolved to prose. Per-file
   commits give clean rollback points if any single file needs
   shortening.

2. **Commit cadence: per-file (16) over per-scenario (2).** The
   alternative was two big commits. Per-file makes each signature pitfall
   independently reviewable. Each commit's body explains the pitfall
   + artifacts + cross-skill round-trips.

3. **No SKILL.md changes in Wave 4.** All 8 skill files are frozen
   since `wave-3-complete`. Worked examples cite Step/Level numbers
   into them but do not modify them. This is verified by
   `git diff --stat wave-3-complete..HEAD -- '.claude/skills/*/SKILL.md'`
   returning empty.

4. **Wave 3c artifact cross-references now round-trip.** Several Wave 3c
   redlines referenced artifacts Wave 4 would populate:
   - `docs/requirements-approval.yaml` → ensemble/requirements.md
   - `validation/handoff-manifest.yaml` → ensemble/architect.md
   - `docs/change-approval.yaml` → ensemble/curator.md
   - ambiguity register → microgrid/conceptualizer.md
   - `release/{version}-publication-check.yaml` → provenance-and-publication.md
   - `cq-implementation-matrix.csv` → ensemble/architect.md Step 8
   No dangling specification-only artifacts remain.

5. **Two new shared files close the last Wave 3c citation gaps.**
   `provenance-and-publication.md` (curator Step 5.6) and
   `github-actions-template.md` (validator L0–L6 in CI). Prior to
   Wave 4, these were cited-but-missing; now they are concrete.

6. **Research report pitfalls are distributed, not copied.** The research
   report (§§ A.1–A.8) had a list of 16 standalone "worked examples to
   add" that were narrower than the 16 Wave 4 files. Instead of authoring
   16 more narrow files, the Wave 4 files *embed* each pitfall as a
   callout within a scenario-organized walkthrough. The crosswalk is
   in the CHANGELOG Wave 4 signature-pitfall table.

7. **CI template is template-only.** `github-actions-template.md`
   gives a ready-to-paste workflow, but it references helper scripts
   that don't all exist yet (`read_declared_profile.py`,
   `read_declared_reasoner.py`, `publication_check.py`,
   `assert_publication_check_passes.py`, `assert_anti_pattern_zero.py`,
   `cq_manifest_check.py`, `shacl_coverage.py`). Creating these helpers
   is deliberately out of scope for Wave 4 — they are follow-up work
   tracked for the next milestone.

8. **Worked examples name real artifacts in fictional ontologies.**
   The ensemble and microgrid scenarios reference files under
   `ontologies/ensemble/` and `ontologies/microgrid/`, but those
   directories do not exist in the repo. The walkthroughs are
   instructional; if the user later exercises one end-to-end, the
   build will need to land at those paths. Not a blocker for merge.

---

## Critical file paths (as of wave-4-complete)

**Plan & handoffs:**
- `~/.claude/plans/users-pooks-dev-ontology-skill-docs-res-bubbly-flamingo.md` — approved plan (full through Wave 4).
- [`HANDOFF-2026-04-21.md`](HANDOFF-2026-04-21.md) — pre-Wave 1 baseline.
- [`HANDOFF-2026-04-21-wave2-complete.md`](HANDOFF-2026-04-21-wave2-complete.md) — had full Wave 3 + 4 plan context.
- [`HANDOFF-2026-04-21-wave3b-complete.md`](HANDOFF-2026-04-21-wave3b-complete.md) — Wave 3c plan.
- [`HANDOFF-2026-04-21-wave3-complete.md`](HANDOFF-2026-04-21-wave3-complete.md) — Wave 4 plan (superseded by this file).
- This file — current handoff (Wave 4 complete, squash-merge pending).
- [`CHANGELOG.md`](CHANGELOG.md) — per-wave log, Wave 4 entry complete.

**Research report (historical):**
- `docs/research/2026-04-21-workflow-improvement-report.md` — cited
  by Wave 3c + 4. Pitfall sub-sections §§ A.1–A.8 distributed across
  Wave 4 files per the crosswalk in the CHANGELOG.

---

## Quick-start for the next session (merge review)

```bash
# 1. Confirm state
cd /Users/pooks/Dev/ontology_skill
git branch --show-current                               # refactor/skills-2026-04
git log --oneline wave-0-baseline..HEAD                 # ~39 commits + handoff
git status --short                                      # clean
git tag --list | grep wave                              # 0-baseline..4-complete

# 2. Re-run all DoD checks
uv run python scripts/validate_description_routing.py   # OK
uv run ruff check .                                     # clean
uv run mypy src/                                        # no issues
for s in ensemble microgrid; do
  for k in requirements scout conceptualizer architect mapper validator curator sparql; do
    test -f ".claude/skills/_shared/worked-examples/$s/$k.md" || echo "MISSING"
  done
done
test -f .claude/skills/_shared/provenance-and-publication.md
test -f .claude/skills/_shared/github-actions-template.md

# 3. Read the worked examples for plausibility (spot-check — no LLM paraphrase
#    of tool output; real artifact shapes)
cat .claude/skills/_shared/worked-examples/ensemble/architect.md
cat .claude/skills/_shared/worked-examples/microgrid/curator.md

# 4. Squash-merge refactor/skills-2026-04 → main (after human review)
git checkout main
git merge --squash refactor/skills-2026-04
git commit -m "refactor(skills): overhaul ontology-engineering skill pack (waves 0-4)"
# Body: use the Wave 4 summary from CHANGELOG.md.

# 5. Optional — preserve feature branch + tags for historical reference
# (no action needed; the tags already live on the pre-squash commits)
```
