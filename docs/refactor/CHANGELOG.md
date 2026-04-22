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

_Complete — tagged `wave-3-complete`. Split into 3a (4 shared files + 2 worked-example stubs), 3b (4 new bottom sections on all 8 skills + Wave 3 citations), 3c (Core Workflow redlines on all 8 skills). 10 commits in this wave._

**Wave 3 summary:** Added 4 new shared reference files (pattern-catalog, mapping-evaluation, sssom-semapv-recipes, modularization-and-bridges). Added 4 new bottom sections (Progress Criteria, LLM Verification Required, Loopback Triggers, Worked Examples) to all 8 SKILL.md files with Wave 3 citations applied per matrix. Restructured `## Core Workflow` on all 8 skills per research report §§ A.1–A.8 — 38 new Step / Level headings landed across the 8 skills, each tool-gated with a named artifact.

### Wave 3c — Core Workflow redlines on all 8 skills

### Files modified
One per-skill commit per SKILL.md; all changes confined to each skill's
`## Core Workflow` section and adjacent Outputs/Handoff rows.

- `ontology-requirements` (`e7fa93a`) — adds Step 0 (scope/retrofit gate),
  explicit non-goals in Step 1, Step 2.5 (CQ quality scoring), updated
  Step 5 schema (priority + owner + testability + expected_answer_shape),
  Step 7.5 (SPARQL preflight via sparql-expert), Step 9 (approval artifact).
- `sparql-expert` (`a1be8da`) — adds Step 0 (query purpose), CQ
  decomposition in Step 1, Step 2.5 (entailment regime), Step 4.5
  (expected-results contract), mandatory Step 5 execution, Step 5.5
  (result sanity check); removes the old standalone "Entailment Regime
  Awareness" section (subsumed).
- `ontology-scout` (`043ad01`) — adds Step 0 (source availability),
  reframed Step 2 as 6-dimension Reuse-Decision Matrix with mandatory
  rejection rationale, Step 3.5 (module vs import vs bridge), Step 5
  upgraded to ODP/DOSDP selection with variable bindings, Step 6
  (imports-manifest update).
- `ontology-mapper` (`3142afe`) — phase banner (candidate → curation →
  evaluation → repair), Step 0 (mapping context), Step 3 LLM verification
  with evidence rubric, Step 5 SSSOM metadata gate, Step 5.1 (entity
  existence + obsolete-term), Step 5.6 (OAEI), Step 7 (mapping
  maintenance), Step 8 (bridge safety gate).
- `ontology-curator` (`1b2c867`) — Step 0 (change intake + impact scope
  with 6 categories), Step 1.5 (CQ + mapping impact analysis), Step 3.5
  (approval artifact blocks apply-changes), Step 5.6 (publication
  metadata check), Step 6.5 (consumer release notes with diff
  provenance), Step 8 (import-refresh workflow as orchestration chain).
- `ontology-conceptualizer` (`5cf3851`) — Step 0 (inbound gate), Step 3.1
  (BFO ambiguity register with Class C escalation), Step 4.1
  (relation-semantics sheet), Step 5.1 (closure / OWA review + CQ
  coverage map), Step 6.1 (anti-pattern review artifact).
- `ontology-validator` (`15503fd`) — Step 0 (artifact type), explicit
  mandatory Command Order and severity thresholds (ERROR/WARN/INFO),
  Level 0 (syntax + profile + import-closure preflight), Level 3.5
  (SHACL coverage), Level 4.5 (CQ manifest integrity + stale detection),
  Level 5.5 (anti-pattern pack), Level 8 (loopback routing table).
- `ontology-architect` (`4c23f79`) — Step 0 (build regime: standalone
  POD vs ODK), construct-support matrix in Step 1, Step 2.5
  (import/declaration preflight), "prefer ROBOT/DOSDP" note on Step 3,
  Step 3.5 (ROBOT template preflight), Step 6.5 (SHACL from
  property-design intent), Step 7.1 (profile-specific reasoner gate with
  pairing table), Step 8 (handoff packaging manifest).

### Decisions / gotchas
- Some "new shared-reference dependencies" listed in research report §§ A.1–A.8 were consolidated into existing Wave 2 shared files (e.g., `odk-and-imports.md` subsumes the `imports-management.md`/`odk-integration.md` split the report suggested). No new shared files were created in Wave 3c.
- Wave 3c references artifacts that Wave 4 will populate (e.g., `docs/requirements-approval.yaml`, `docs/bfo-alignment.md` ambiguity register, `validation/handoff-manifest.yaml`). These are specification-only until worked examples show them in context.
- Every Wave 3c commit is one skill at a time per the handoff's recommended split. Reviewing diffs one-skill-at-a-time gives clean rollback points.
- The sparql-expert redline is the only one that removes existing content (the old "Entailment Regime Awareness" standalone section, now subsumed by Step 2.5). All other redlines are additive to the Core Workflow.

### Definition-of-done checks (all pass)
```bash
# All 38 Wave 3c signature headings land in their skills (see verification script)
# Core Workflow order makes sense when read top-to-bottom for each skill
# Routing + lint clean
uv run python scripts/validate_description_routing.py
uv run ruff check .
```

### Wave 3b — 4 new sections + Wave 3 citations on all 8 skills

### Files modified
- All 8 `.claude/skills/*/SKILL.md` files gained four new sections at the bottom, in order: `## Progress Criteria`, `## LLM Verification Required`, `## Loopback Triggers`, `## Worked Examples`. Each section is capped at ~20 lines and offloads detail to shared reference files.
- Wave 3 citation matrix applied to Shared Reference Materials:
  - `ontology-conceptualizer`: `pattern-catalog.md`, `modularization-and-bridges.md`
  - `ontology-architect`: `pattern-catalog.md`, `modularization-and-bridges.md`
  - `ontology-mapper`: `mapping-evaluation.md`, `sssom-semapv-recipes.md`
  - `ontology-validator`: `mapping-evaluation.md`
  - `ontology-scout`: `modularization-and-bridges.md`

### Decisions / gotchas
- Progress Criteria items are tool-verifiable (paired command, artifact path) per CONVENTIONS.md § 11 — no advisory language.
- LLM Verification tables classify each operation per the Class A/B/C/D taxonomy in `llm-verification-patterns.md § 2`.
- Loopback Triggers distinguish *incoming* (what this skill receives) from *raised* (what this skill sends upstream).
- Worked-Examples links point to Wave 4 files not yet created; every link is marked `*(Wave 4)*` for clarity.
- `ontology-validator` Loopback Triggers table is the primary raiser; it routes failures per class to architect / conceptualizer / requirements / scout / curator / mapper / sparql-expert.

### Definition-of-done checks (all pass)
```bash
# All 4 new sections present in every SKILL.md
for skill in ontology-{requirements,scout,conceptualizer,architect,mapper,validator,curator} sparql-expert; do
  for section in "Progress Criteria" "LLM Verification Required" "Loopback Triggers" "Worked Examples"; do
    grep -q "^## $section" ".claude/skills/$skill/SKILL.md" || echo "MISSING: $skill / $section"
  done
done
# Wave 3 citations present in the matching skills
grep -l "pattern-catalog" .claude/skills/ontology-{conceptualizer,architect}/SKILL.md
grep -l "modularization-and-bridges" .claude/skills/ontology-{scout,conceptualizer,architect}/SKILL.md
grep -l "mapping-evaluation" .claude/skills/ontology-{mapper,validator}/SKILL.md
grep -l "sssom-semapv-recipes" .claude/skills/ontology-mapper/SKILL.md
# Routing still passes, ruff clean
uv run python scripts/validate_description_routing.py
uv run ruff check .
```

---

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

_Complete — tagged `wave-4-complete`. Split into 3 groups: 4.A (16 worked-
example files), 4.B (2 new shared files), 4.C (final E2E verification +
tag). 19 commits in this wave: 16 per-file commits for Group A + 1 bundle
commit for Group B + CHANGELOG + handoff._

**Wave 4 summary:** Populated all 16 worked-example files (ensemble ×
8 + microgrid × 8), added two new shared reference files
(`provenance-and-publication.md`, `github-actions-template.md`) that
Wave 3c SKILL.md redlines cite, and ran the final E2E verification.
Branch is now ready for squash-merge to `main`.

### Group A — 16 worked-example files

Each file walks 6–10 Core Workflow steps from its skill's SKILL.md, shows
concrete artifact fragments (YAML, CSV, SPARQL, TTL) for each step, and
includes a pitfall callout tied to research report §§ A.1–A.8.

Per-file size: 108–199 lines. Larger than the handoff's initial 40–80-line
target — the increase is justified because each file walks 6–10 steps
with artifact fragments rather than prose summaries. Per-file commits
give clean rollback points for any reviewer concerns.

| Commit | File | Signature pitfall |
|--------|------|-------------------|
| `6050a9a` | `ensemble/requirements.md` | Bad-CQ retrofit (falsifiable criterion) |
| `2ee8687` | `ensemble/scout.md` | Weak-vocab license-rejection; schema.org → bridge |
| `d5b8502` | `ensemble/conceptualizer.md` | Role-type confusion (StringPlayer); OWA closure review |
| `c390ff9` | `ensemble/architect.md` | **ELK silently skips qualified cardinality** |
| `308f72e` | `ensemble/mapper.md` | **exactMatch clique contamination** (violinist↔fiddler↔player) |
| `04311dc` | `ensemble/validator.md` | Canonical L0→L1→L2→L4→L3→L4.5→L5.5→L6 order; injected CQ-E-001 regime fail |
| `79a7f5e` | `ensemble/curator.md` | Deprecate-not-delete (Safety Rule #4) |
| `9a6a79e` | `ensemble/sparql.md` | **COUNT aggregate vs row-shape mismatch** |
| `442a939` | `microgrid/requirements.md` | Retrofit-gate trip prevents retroactive CQs |
| `516c336` | `microgrid/scout.md` | **BFO leak via IAO_0000030** (workspace memory) |
| `552a183` | `microgrid/conceptualizer.md` | Dispatch-event vs dispatch-role ambiguity; EL-safe closure |
| `1de3fa9` | `microgrid/architect.md` | **Equivalence-bridge failure** (BFO category mismatch) |
| `0e7a6d1` | `microgrid/mapper.md` | **Cross-domain exactMatch floor** (schema:Product refused) |
| `6d0ef94` | `microgrid/validator.md` | Dual-reasoner (ELK + HermiT); mapping-gates interleaved |
| `6bbb0d8` | `microgrid/curator.md` | **OEO import-refresh chain** (6-step sequence) |
| `131ca57` | `microgrid/sparql.md` | **Entailment regime mismatch** on CQ-M-001 chain |

### Group B — 2 new shared reference files

| Commit | File | Cited by |
|--------|------|----------|
| `fe2404e` | `_shared/provenance-and-publication.md` | curator Step 5.5 / 5.6, validator release-gate |
| `fe2404e` | `_shared/github-actions-template.md` | validator L0–L6, curator release-infra |

`provenance-and-publication.md` gives concrete shape to curator Step 5.6's
`release/{version}-publication-check.yaml` (previously specification-only)
plus PURL / w3id / content-negotiation / registry guidance.

`github-actions-template.md` is a paste-able `.github/workflows/` template
that implements validator's L0–L6 command order, SSSOM validate + clique
check, release-publication check on tagged commits, and Level 8 failure-
routing hints in the job names.

### Decisions / gotchas
- Per-file commits for Group A (16 commits) vs clustered per-scenario
  (2 commits). Chose per-file for reviewability — each file stands alone
  with a thematic commit message. Total Wave 4 commit count: 19.
- Every worked-example file cites the exact Step / Level numbers from the
  corresponding SKILL.md, carries the artifact shapes as code fences
  (not prose paraphrase), and embeds ≥ 1 pitfall per the research
  report's "Worked examples to add" sub-sections.
- Cross-skill round-trips work: ensemble/architect.md's handoff-manifest
  shape matches Wave 3c's architect Step 8 spec; microgrid/curator.md's
  import-refresh chain matches Wave 3c's curator Step 8 diagram;
  ensemble/mapper.md's clique SPARQL matches validator L5.5 probe output.
- The two new shared files close the last open citations from Wave 3c
  (curator Step 5.6 reference to `provenance-and-publication.md` + `github-
  actions-template.md`). No dangling citations remain.

### Definition-of-done checks (all pass)
```bash
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

# Wave 3c signature headings preserved (SKILL.md files unchanged since wave-3-complete)
git diff --stat wave-3-complete..HEAD -- '.claude/skills/*/SKILL.md'   # empty

# Routing + lint + types still pass
uv run python scripts/validate_description_routing.py                   # OK
uv run ruff check .                                                     # clean
uv run mypy src/                                                        # no issues
```

---
