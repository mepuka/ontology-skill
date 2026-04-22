# Handoff — Start fresh ontology (post-refactor merge)

**Session paused:** 2026-04-22 after the skills-pack refactor landed on `main`.
**Next session goal:** Start a new ontology project using the newly-merged
pipeline, beginning with `/ontology-requirements` Step 0.

---

## TL;DR

- **Refactor complete + merged.** `refactor/skills-2026-04` squash-merged to
  `main` as `b2c4d9a`. All five wave tags preserved on the feature branch
  for historical reference.
- **Workspace cleaned.** Untracked WIP (skygest-energy-vocab, etf-filing,
  energy-news notebooks, verify csvs, critique doc) stashed at `stash@{0}`.
- **Ready for new ontology.** Invoke `/ontology-requirements` in the next
  session; answer the 5 Step 0 / Step 1 questions listed below.

---

## Current repo state

### Branch + commits
- **Branch:** `main`
- **Tip:** `b2c4d9a refactor(skills): overhaul ontology-engineering skill pack (waves 0-4)`
- `main` is 4 commits ahead of `origin/main`:
  - `b2c4d9a` — squash-merge (this session's work)
  - `215ea05` — wave-0-baseline tag / `feat(enews): add article fetcher...`
  - `e00a214` — `feat(enews): add ABox ETL pipeline for Bluesky post ingestion`
  - `09f81c7` — `docs(enews): add ABox ingestion strategy, ontology viewer, and rlm issue`

The last three are pre-existing local commits from before this session —
not our concern. Do not push without explicit user approval.

### Working tree
Clean. No tracked changes, no untracked files.

### Stashes
```
stash@{0}: outstanding work 2026-04-22 pre-fresh-ontology (skygest-energy-vocab,
           etf-filing, energy-news notebooks, verify csvs)
stash@{1}: sky-316 wip pre-refactor-branch   [from prior session]
stash@{2}: WIP on feat/energy-media-ontology [from prior session]
stash@{3}: WIP on feat/etf-filing-ontology   [from prior session]
```

Do not pop any of these unless the user asks. `stash@{0}` holds this
session's set-aside work — restore later with
`git stash pop stash@{0}` (or `git stash apply` if you want to keep the
stash after).

### Feature branch
`refactor/skills-2026-04` still exists with all 40 per-wave commits + 5
tags (`wave-0-baseline` through `wave-4-complete`). Keep it around for
per-wave diffs and review archaeology. Do not delete.

---

## What landed in the merge

The full skill pack now lives on `main`:

- **8 SKILL.md files** in `.claude/skills/{ontology-requirements, ontology-scout, ontology-conceptualizer, ontology-architect, ontology-mapper, ontology-validator, ontology-curator, sparql-expert}/`
- **24 shared reference files** in `.claude/skills/_shared/`
- **16 worked-example files** in `.claude/skills/_shared/worked-examples/{ensemble, microgrid}/`
- **Governance:** `.claude/skills/CONVENTIONS.md` (16 safety rules + iteration-loopback protocol) and `.claude/skills/SKILL-TEMPLATE.md`
- **Validator:** `scripts/validate_description_routing.py` enforces the description invariant

The pipeline: `requirements → scout → conceptualizer → architect →
validator → [release]` with `mapper` (integration), `curator`
(maintenance/refresh), and `sparql-expert` (cross-cutting) branching off.
See `docs/refactor/HANDOFF-2026-04-22-wave4-complete.md` for the full
walkthrough.

---

## Next session — first moves

### 1) Confirm state

```bash
cd /Users/pooks/Dev/ontology_skill
git branch --show-current                        # main
git log --oneline -1                             # b2c4d9a ...waves 0-4
git status --short                               # empty
git stash list | head -4                         # stash@{0} = this session's WIP

uv run python scripts/validate_description_routing.py    # OK
uv run ruff check .                                      # clean
uv run mypy src/                                         # no issues
```

### 2) Invoke the skill

```
/ontology-requirements
```

The skill will run Step 0 (scope gate) then Step 1 (domain scoping).
Be ready to answer:

| # | Question | Example answer |
|---|----------|----------------|
| 1 | **Ontology name** (becomes dir + IRI base) | `project-foo` |
| 2 | **Domain description** (one paragraph) | "X domain covers …" |
| 3 | **Use cases + stakeholders** | "Actor Y needs Z for W" |
| 4 | **In-scope vs out-of-scope (non-goals)** | "Covers A, B, C; does not cover D (rationale)" |
| 5 | **Constraints** (OWL profile, size, existing systems to integrate) | "OWL 2 DL, ~200 classes, integrate with sevocab" |

Default choices unless the user says otherwise:

- **Upper ontology:** BFO (per `CLAUDE.md`).
- **Build regime:** standalone POD (not ODK) — per `CLAUDE.md`.
- **OWL profile:** DL by default; narrow to EL/QL/RL only with a
  documented reason.
- **Namespace:** `https://w3id.org/{ontology-name}` — ask the user to
  confirm before minting the ontology header (see
  `_shared/provenance-and-publication.md § 1.3`).

### 3) Follow the pipeline end-to-end

Once Step 0 gates pass and Step 1 scope is recorded, the skill walks
Steps 1.5 → 9 producing use-cases.yaml, competency-questions.yaml,
cq-quality.csv, pre-glossary.csv, tests/cq-*.sparql preflight,
traceability-matrix.csv, and the signed `requirements-approval.yaml`.
Then handoff to `/ontology-scout` for reuse, and onward.

The worked examples at
`.claude/skills/_shared/worked-examples/ensemble/requirements.md` and
`.claude/skills/_shared/worked-examples/microgrid/requirements.md` are
the reference artifacts. Match shape, not content.

---

## Things to remember

1. **Don't push.** `main` is 4 commits ahead of `origin/main`. The user
   has not authorized pushing. Wait for explicit approval before
   `git push`.
2. **Don't touch the stashes.** `stash@{0}` holds this session's
   set-aside work. `stash@{1..3}` predate this session entirely.
3. **Safety rules still apply** — never hand-edit `.ttl` files; always
   `robot reason` after structural changes; never delete terms
   (deprecate + replacement pointer per Safety Rule #4).
4. **File paths in worked examples are fictional** — `ontologies/ensemble/`
   and `ontologies/microgrid/` do not exist. The new ontology lands at
   `ontologies/{your-name}/` and only gets created when the architect
   skill writes the first artifact.
5. **Ruff `extend-exclude`** covers `**/notebooks/`, `**/.checkpoints/`,
   `**/.cache/`. If the new ontology adds Python scripts in
   `ontologies/{name}/scripts/`, they follow the per-file-ignore rules in
   `pyproject.toml § tool.ruff.lint.per-file-ignores`.

---

## Reference paths

| Purpose | Path |
|---------|------|
| Full Wave 4 handoff (post-refactor walkthrough) | [`docs/refactor/HANDOFF-2026-04-22-wave4-complete.md`](refactor/HANDOFF-2026-04-22-wave4-complete.md) |
| Refactor CHANGELOG with per-wave detail | [`docs/refactor/CHANGELOG.md`](refactor/CHANGELOG.md) |
| Conventions + safety rules | [`.claude/skills/CONVENTIONS.md`](../.claude/skills/CONVENTIONS.md) |
| Skill template (structure of every SKILL.md) | [`.claude/skills/SKILL-TEMPLATE.md`](../.claude/skills/SKILL-TEMPLATE.md) |
| Loopback protocol + routing table | [`.claude/skills/_shared/iteration-loopbacks.md`](../.claude/skills/_shared/iteration-loopbacks.md) |
| Worked example — requirements (ensemble) | [`.claude/skills/_shared/worked-examples/ensemble/requirements.md`](../.claude/skills/_shared/worked-examples/ensemble/requirements.md) |
| Worked example — requirements (microgrid) | [`.claude/skills/_shared/worked-examples/microgrid/requirements.md`](../.claude/skills/_shared/worked-examples/microgrid/requirements.md) |
| Publication schema + Step 5.6 check | [`.claude/skills/_shared/provenance-and-publication.md`](../.claude/skills/_shared/provenance-and-publication.md) |
| CI workflow template | [`.claude/skills/_shared/github-actions-template.md`](../.claude/skills/_shared/github-actions-template.md) |
