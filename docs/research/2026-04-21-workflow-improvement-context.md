---
title: Ontology Skills Workflow Improvement — Research Bundle
date: 2026-04-21
audience: GPT-5.4 Pro research session
generated_by: scripts/build_research_bundle.py
source_repo: /Users/pooks/Dev/ontology_skill
---

# Ontology Skills Workflow Improvement — Research Bundle

> This is a self-contained context bundle. Everything below is either
> synthesis authored specifically for this research session or verbatim
> excerpts from the repository. The intent is that a reader who has
> never seen this repo can understand:
>
> 1. The ambition (agent-first programmatic ontology development),
> 2. The current architecture (8 skills + shared materials + safety
>    hooks + lifecycle pipelines),
> 3. What has been built, what remains, and where practitioners have
>    already flagged gaps, and
> 4. Enough primary source material (all SKILL.md files, shared
>    references, conventions, practitioner insights) to do a rigorous
>    critique and propose improvements.
>
> The companion research prompt lives at
> `docs/research/2026-04-21-workflow-improvement-prompt.md`.
## 1. Executive Summary

This repository is a workspace for building, maintaining, and
integrating OWL 2 ontologies using an **agent-first, programmatic
ontology development (POD)** workflow. Everything is code: ontologies
are generated from structured inputs (YAML, CSV, ROBOT templates,
KGCL patches), changes are auditable, and Claude Code skills encode
the professional ontologist's lifecycle as eight discrete, composable
capabilities.

The long-term ambition is to translate what a senior ontologist does
— scoping, requirements elicitation, reuse evaluation,
conceptualization with BFO alignment, formalization in OWL 2,
mapping with SSSOM, validation with reasoners and SHACL, and
maintenance with KGCL/deprecation — into a workflow that an LLM
agent can execute reliably, with human review at the right gates.

Current state (2026-04-21):

- **8 skill files** under `.claude/skills/` covering the full
  lifecycle, plus a shared skill-authoring standard
  (`CONVENTIONS.md`) and template (`SKILL-TEMPLATE.md`).
- **8 shared reference materials** under `.claude/skills/_shared/`
  (methodology backbone, tool decision tree, BFO categories, axiom
  patterns, anti-patterns, naming conventions, quality checklist,
  and canonical namespaces).
- **3 auto-loading rules files** under `.claude/rules/` (ontology
  safety, build scripts, testing) that attach to file-path patterns.
- **3 Claude Code hooks** under `.claude/hooks/` that enforce
  turtle-syntax validation after writes, block `sed`/`awk` on
  ontology files, and warn on direct edits to `.ttl`/`.owl`/`.rdf`.
- **5 ontology projects** under `ontologies/`, of which
  `skygest-energy-vocab` is the mature exemplar (92 CQ tests with
  91.3% pass rate, 34 build scripts, recent full validation report
  from 2026-04-14).
- **Research scaffolding** under `docs/` including an extracted
  BFO textbook summary, extracted Kendall-McGuinness methodology
  summary, extracted Knowledge Graphs (Hogan et al.) summary, a
  proposal document describing the 8-skill design rationale, and a
  17-theme `practitioner-insights.md` that already identifies
  priority gaps relative to real-world OBO Foundry practice.

The goal of the forthcoming research session is to take this bundle
and produce a concrete plan for refining the skills, the shared
materials, the activation triggers, the iteration/feedback loops,
and the worked examples — so that the workflow consistently
produces ontologies of the quality that a professional ontologist
would sign off on.
## 2. Intellectual Foundations

The workspace explicitly synthesizes four methodological traditions.
See `Appendix B` for the verbatim shared-reference materials; this
section is a map of the ideas.

### 2.1 Programmatic Ontology Development (POD)

Ontologies are software artifacts. Instead of clicking through
Protégé, the canonical workflow is:

- Ontology content lives in structured inputs (glossary CSV, YAML
  conceptual model, YAML axiom plan, ROBOT template TSVs, KGCL
  patch files) under version control.
- Build scripts (Python + rdflib, orchestrated from `scripts/build.py`
  per ontology) read those inputs and emit the target `.ttl`.
- Quality gates (`robot reason`, `robot report`, `pyshacl`, `robot
  verify` against a CQ test suite) run in CI and via `just check`.
- Changes flow through auditable artifacts: KGCL patches for
  individual edits, ROBOT templates for bulk creation, and
  Python scripts for complex transforms.

Literate ontology programming — keeping formal code and human-readable
rationale in the same artifact — is explicit in the
`conceptual-model.yaml` and `axiom-plan.yaml` formats.

### 2.2 Basic Formal Ontology (BFO)

BFO (ISO 21838-2) is the default upper ontology. The shared
`bfo-categories.md` encodes a decision procedure: is an entity a
Continuant or an Occurrent; if Continuant, Independent or
Dependent; etc. It also documents known ambiguities
(Disease-as-Disposition vs Process, Organization-as-Object vs
Aggregate, Information as GDC with a three-hop concretization
chain, Role vs Disposition for social/regulatory concepts) with
recommended defaults and when to choose alternatives.

Practitioner-insights Theme 5 calls BFO alignment the #1 source of
community confusion. The shared doc acknowledges this and the
conceptualizer skill references the doc, but worked examples end-to-end
are thin.

### 2.3 NeOn / Kendall–McGuinness / METHONTOLOGY

These methodologies supply the lifecycle phases:

- **Specification** (CQs, ORSD, scope, traceability) — the
  `ontology-requirements` skill.
- **Knowledge acquisition** (reuse first, extract via ROBOT,
  apply Ontology Design Patterns) — the `ontology-scout` skill.
- **Conceptualization** (glossary, taxonomy, BFO alignment,
  property design, axiom plan) — the `ontology-conceptualizer`
  skill.
- **Formalization** (OWL 2 axioms, ROBOT templates, KGCL patches,
  reasoner) — the `ontology-architect` skill.
- **Integration** (SSSOM mappings, lexmatch, LLM verification,
  clique analysis) — the `ontology-mapper` skill.
- **Evaluation** (reasoner, SHACL, ROBOT report, CQ tests,
  coverage metrics) — the `ontology-validator` skill.
- **Maintenance/evolution** (KGCL changes, deprecation, versioning,
  release, FAIR assessment) — the `ontology-curator` skill.

### 2.4 CQ-Driven Development (TDOD)

Competency questions are the connective tissue. They are:

- Elicited with types (enumerative, boolean, relational,
  quantitative, constraint, temporal) and MoSCoW priorities
  (Must/Should/Could/Won't).
- Formalized as SPARQL with expected-result assertions
  (non_empty / zero / count_equals / binds_exactly).
- Registered in a `tests/cq-test-manifest.yaml` per ontology, and
  executed with `robot verify`.
- Traced end-to-end via `docs/traceability-matrix.csv`: stakeholder
  need → use case → CQ → ontology term → SPARQL test.

Practitioner-insights Theme 11 warns about cargo-culting (CQs
written after the ontology, CQs too vague to fail, CQ tests that go
stale). The requirements skill includes anti-pattern guards, but
the "process gate enforcing CQs-before-conceptualization" is
guidance, not automation.

### 2.5 Knowledge Graph Quality (Hogan et al.)

`_shared/quality-checklist.md` encodes a layered quality model:

- Accuracy (syntactic, semantic, timeliness).
- Coverage (schema completeness, property completeness,
  population completeness, representativeness).
- Coherency (consistency via reasoner under OWA; validity via
  SHACL under local CWA — these are different and complementary).
- Succinctness (intensional, extensional, representational).
- Evaluation dimensions (expressivity, complexity, granularity,
  epistemological adequacy) as qualitative release-readiness notes.

The validator skill drives a 7-level pipeline: logical consistency
→ ROBOT report → SHACL → CQ tests → metrics → qualitative
evaluation → diff.
## 3. The 8-Skill Architecture

Each skill is a single `SKILL.md` file with YAML frontmatter
(`name`, `description`), a role statement, a "When to Activate"
section, references to shared materials, a numbered workflow,
concrete tool commands, output artifacts, handoff specifications
(including a checklist), anti-patterns, and an error-handling
table. The standard is enforced by
`.claude/skills/CONVENTIONS.md`.

### 3.1 Phase-to-skill map

| Lifecycle phase | Skill | Primary methodology |
|-----------------|-------|---------------------|
| 1. Specification | `ontology-requirements` | CQ-driven (Gruninger & Fox) |
| 2. Knowledge acquisition | `ontology-scout` | NeOn scenarios 1–4 |
| 3. Conceptualization | `ontology-conceptualizer` | METHONTOLOGY + BFO alignment |
| 4. Formalization | `ontology-architect` | Programmatic Ontology Development |
| 5. Integration | `ontology-mapper` | SSSOM + NeOn scenario 5 |
| 6. Evaluation | `ontology-validator` | Test-Driven Ontology Development |
| Cross-cutting: querying | `sparql-expert` | SPARQL 1.1 / SPARQL-star |
| Cross-cutting: maintenance | `ontology-curator` | NeOn scenario 9 |

### 3.2 Pipelines

Three pipelines compose the skills into workflows:

```
Pipeline A (new ontology):
  requirements → scout → conceptualizer → architect → validator

Pipeline B (mapping):
  scout → mapper → validator

Pipeline C (evolution):
  curator → validator
```

Cross-cutting: `sparql-expert` is called by any skill that needs
SPARQL generated or executed; `validator` is called by
`architect`, `curator`, and `mapper` to close the loop before
commit or release.

### 3.3 Handoff artifacts (from `CONVENTIONS.md`)

| From | To | Artifacts passed |
|------|----|------------------|
| requirements | scout | `docs/pre-glossary.csv`, `docs/scope.md` |
| requirements | conceptualizer | `docs/competency-questions.yaml`, `docs/pre-glossary.csv`, `docs/traceability-matrix.csv` |
| scout | conceptualizer | `docs/reuse-report.md`, import term lists, ODP recommendations |
| conceptualizer | architect | `docs/glossary.csv`, `docs/conceptual-model.yaml`, `docs/bfo-alignment.md`, `docs/axiom-plan.yaml`, `docs/property-design.yaml` |
| architect | validator | `{name}.ttl`, `shapes/{name}-shapes.ttl`, `tests/*.sparql`, `tests/cq-test-manifest.yaml` |
| mapper | validator | `mappings/*.sssom.tsv` |
| curator | validator | modified `{name}.ttl`, KGCL change log |

### 3.4 Handoff checklists

Each SKILL.md ends with a checklist of what the next skill should
be able to verify in the inbound artifacts. E.g., the
conceptualizer handoff requires:

- Glossary covers all pre-glossary terms (with additions/removals
  justified).
- Every class is aligned to a BFO category.
- Every Must-Have CQ has a corresponding axiom plan entry.
- Anti-pattern review is complete with zero unresolved issues.
- User has reviewed and approved the conceptual model.

### 3.5 The shared reference materials

These are the knowledge base that individual skills pull in:

- `methodology-backbone.md` — lifecycle phase mapping, pipelines,
  CQ through-line, phase boundaries.
- `tool-decision-tree.md` — which tool for which operation, with
  reasoner-selection guidance and known limitations (oaklib adapter
  inconsistencies, KGCL incompleteness, ELK silently ignoring non-EL
  axioms, etc.).
- `bfo-categories.md` — continuant/occurrent decision tree, common
  mistakes, known ambiguities.
- `axiom-patterns.md` — 16 OWL 2 patterns with Manchester Syntax,
  ROBOT template snippets, notes on when reasoners can't handle
  them (ELK + qualified cardinality, etc.).
- `anti-patterns.md` — 16 modeling anti-patterns with SPARQL
  detection queries.
- `naming-conventions.md` — class/property/individual naming,
  IRI governance, labels, definitions (genus-differentia).
- `quality-checklist.md` — the pre-commit/pre-release quality
  checklist (reasoner, ROBOT report, SHACL, CQ tests, coverage
  metrics, succinctness checks, evaluation dimensions).
- `namespaces.json` — canonical prefix-to-IRI map.

### 3.6 Safety rules (non-negotiable)

From `CONVENTIONS.md`:

1. Never hand-edit structural axioms.
2. Always run `robot reason` after structural changes.
3. Always run `robot report` before committing.
4. Never delete terms — deprecate with `owl:deprecated true` and a
   replacement pointer.
5. Propose KGCL patches for human review before applying to shared
   ontologies.
6. Validate SPARQL syntax before execution.
7. Check for existing terms before creating new ones.
8. Never execute SPARQL UPDATE/DELETE against production endpoints.
9. Read before modifying.
10. Back up before bulk operations (ROBOT template, batch KGCL).

These are enforced partially by Claude Code hooks (see §4.3 below)
and partially by skill-level discipline.
## 4. Tooling and Automation Layer

### 4.1 Python environment (uv-only)

`pyproject.toml` targets Python 3.12+ with strict dependencies:

- Production: `oaklib`, `rdflib`, `pyshacl`, `owlready2`, `sssom`,
  `curies`, `prefixmaps`, `linkml`, `linkml-runtime`,
  `SPARQLWrapper`, `pandas`, `pyyaml`, `click`, `httpx`,
  `trafilatura`, `pyoxigraph`.
- Dev: `ruff` (lint + format), `mypy`, `pytest`, `pytest-asyncio`,
  `pytest-cov`, `respx`, `pip-audit`, `pre-commit`, `pylode`.

Ruff ruleset: E, W, F, I (isort), N, UP, B, A, ASYNC, COM, C4, DTZ,
T10, ISC, ICN, PIE, PT, RSE, RET, SLF, SIM, TID, TCH, ARG, PTH,
ERA, PL, TRY, FLY, PERF, RUF, S.

The `uv run` prefix is mandatory for all Python invocations.

### 4.2 Justfile targets

- `just check` — the quality gate: ruff lint + format check + mypy
  + pytest + validate both active ontologies.
- `just test`, `just test-cov`, `just test-unit`,
  `just test-integration`.
- `just build-energy-news`, `just validate-energy-news`,
  `just build-pao`, `just validate-pao` — per-ontology pipelines.
- `just robot-install` — install ROBOT jar + wrapper locally under
  `.local/bin/robot` (no global pollution). ROBOT version in use is
  1.9.8.

### 4.3 Claude Code hooks (`.claude/hooks/`)

Three shell hooks enforce safety at tool-call time:

- **`post-ontology-write.sh`** (PostToolUse:Write) — After any
  write, if the target is `.ttl`, parse it with rdflib; if
  parsing fails, return `{"decision": "block"}` with the error.
  Prevents syntactically broken TTL from reaching disk.
- **`guard-sed-ontology.sh`** (PreToolUse:Bash) — If the command
  matches `(sed|awk|perl).*\.(ttl|owl|rdf|ofn|owx)`, deny execution
  with a message instructing the agent to use ROBOT / oaklib /
  Python instead. Enforces Safety Rule #1.
- **`protect-ontology-files.sh`** (PreToolUse:Edit|Write) — If the
  target is under `ontologies/` and matches
  `\.(ttl|owl|rdf|xml)`, emit an advisory
  `additionalContext` reminding the agent to prefer programmatic
  modification. Warns but does not block (to allow bootstrapping
  and hand-edit exceptions for annotations / merge conflicts per
  the refined rule).

### 4.4 Auto-loading rules (`.claude/rules/`)

Path-matched rule files that get injected into context when the
agent touches files under the matching paths:

- **`ontology-safety.md`** — triggers on
  `ontologies/**/*.{ttl,owl,rdf}`. Enumerates the 10 non-negotiable
  rules, the tool priority, and serialization/naming standards.
- **`ontology-build-scripts.md`** — triggers on
  `scripts/**/*.py` and `ontologies/*/scripts/**/*.py`. Documents
  the 6-phase lifecycle, rdflib patterns, and quality gates that
  must pass after modifying build scripts.
- **`ontology-testing.md`** — triggers on
  `ontologies/*/tests/**` and `docs/competency-questions.yaml`.
  Encodes TDOD conventions, SPARQL standards, SHACL validation,
  and test organization.

### 4.5 Pre-commit hooks

`.pre-commit-config.yaml` runs at commit time:

- Ruff lint (with `--fix`) and Ruff format.
- pre-commit-hooks: trailing whitespace, end-of-file,
  `check-yaml`, `check-toml`, `check-added-large-files`,
  `check-merge-conflict`, `debug-statements`.
- Custom local hooks: `validate_turtle.py` (rdflib parse every
  staged `.ttl`), `validate_sssom.py` (sssom-cli validate every
  staged `.sssom.tsv`).
- mypy mirror (1.14.1) on `src/`.

### 4.6 Tool priority (from `tool-decision-tree.md`)

Primary (always try first):

1. ROBOT CLI — bulk build operations, merge, reason, report,
   template, verify, diff, convert, extract, annotate.
2. oaklib (`runoak`) — navigation, search, KGCL apply, lexmatch.
3. KGCL — human-reviewable change proposals.

Secondary (escalation criteria documented):

4. OWLAPY — complex DL axioms requiring OWL API.
5. owlready2 — ORM-style Python interaction, SQLite quadstore.
6. LinkML — schema-first modeling, polyglot artifact generation.
7. rdflib — raw triple manipulation, custom serialization.
8. pyshacl — SHACL validation.
9. sssom-py — SSSOM file management.
## 5. Active Ontology Projects

The workspace hosts five ontology projects. They range from
placeholder stubs to the mature, actively-developed
`skygest-energy-vocab`.

### 5.1 `skygest-energy-vocab` — mature exemplar

The production-ready SKOS/OWL vocabulary for the Skygest energy
chart resolver pipeline. Models seven facets of an
`EnergyVariable` — statistic type, aggregation, unit family,
technology/fuel, measured property, domain object, frequency —
plus the DCAT citation chain (`EnergyAgent`, `EnergyDataset`,
`Series`, distribution).

- **Main TBox**: `ontologies/skygest-energy-vocab/skygest-energy-vocab.ttl`
  (87.6 KB, pure-generative from structured specs).
- **CQ suite**: 92 CQs with 91.3% pass rate (84/92) as of
  validation 2026-04-14. 8 non-blocking failures due to test data
  scoping (SurfaceFormEntry deprecated, pruning eliminated expected
  collisions, cross-repo data not loaded into test graph).
- **Build scripts**: 34 Python scripts under `scripts/`.
  Core: `build.py`, `add_dcat_structural_layer.py`,
  `add_semantic_extension_layer.py`, `add_new_schemes.py`,
  `harvest_labels.py`, `prune_broad_surface_forms.py`,
  `build_sevocab_individuals.py`, `extract_imports.py`,
  `validate.py`, `run_cq_tests.py`. Maintenance (from 2026-04-14
  session): `fix_declaration_hygiene.py` (37.4 KB, 2115 DL
  violations → 0), `fix_native_orphans.py`, `fix_deprecated_subclass_axiom.py`,
  `add_has_variable_property_chain.py`.
- **Imports**: 11 declaration stubs (not full module imports) for
  BFO, FOAF, schema.org, DCAT/DCTerms/PROV, W3C Data Cube, IAO,
  SKOS, OEO (Open Energy Ontology v2.11.0), QUDT QuantityKind, and
  QUDT Unit.
- **Validation report**: `docs/validation-report-2026-04-14.md`.
  After a full hygiene pass: OWL 2 DL profile violations
  2115 → 0, valid imports 4/8 → 10/10, ROBOT report ERRORs 0,
  native orphans 3 → 0, HermiT consistency PASS.
- **Gaps**: no formal `release/` directory (version only in
  `owl:versionInfo 0.2.1`); 23 `missing_definition` ROBOT warnings
  (skos:definition present but not `obo:IAO_0000115`);
  KGCL change proposals not used (Python scripts only).

### 5.2 `personal_agent_ontology` — mature, frozen

Agent capabilities, memory, planning ontology. Full lifecycle:
conceptual model, 9 versioned releases (v0.1.0–v0.9.0), 133 CQ
tests, SHACL shapes. 117 KB TBox. Frozen since Feb 2024.

### 5.3 `energy-news` — WIP active

News/media classification for energy topics. 49 CQ tests,
17 build scripts, 14-version release history, 4 import stubs,
SSSOM mappings. More mature than energy-media, less than
skygest-energy-vocab.

### 5.4 `etf-filing` — early/WIP

SEC ETF filing ontology. Scope, docs, scripts, tests directories.
Nascent.

### 5.5 `energy-media` — placeholder

Directory stub only.
## 6. Known Gaps (Practitioner-Identified)

The in-repo `docs/practitioner-insights.md` (verbatim in Appendix D)
enumerates 17 themes where current skill guidance diverges from
professional OBO Foundry practice. The top-ranked actionable
gaps:

| # | Gap | Affected skills | Effort |
|---|-----|-----------------|--------|
| 1 | No ODK (Ontology Development Kit) awareness or integration | architect, validator, curator | Medium |
| 2 | ROBOT template gotchas undocumented | architect | Low |
| 3 | oaklib/KGCL limitations undocumented | architect, curator | Low |
| 4 | Import management underspecified | scout, architect, curator | Medium |
| 5 | BFO alignment ambiguities not acknowledged | conceptualizer, bfo-categories | Low |
| 6 | SSSOM mapping challenges underestimated | mapper | Medium |
| 7 | Reasoner performance not contextualized | architect, validator | Low |
| 8 | Domain/range confusion needs more emphasis | conceptualizer, architect | Low |
| 9 | LinkML scope too broadly stated | architect, tool-decision-tree | Low |
| 10 | SHACL authoring guidance missing | architect, validator | Medium |
| 11 | "Never hand-edit" rule too absolute | CONVENTIONS.md | Low |
| 12 | CI/CD patterns need GitHub Actions examples | validator, curator | Medium |
| 13 | CQ failure modes undocumented | requirements | Low |
| 14 | OWLAPY/owlready2 prominence overstated | architect, tool-decision-tree | Low |
| 15 | Multi-ontology coordination missing | curator, scout | Medium |
| 16 | LLM limitations for ontology work undocumented | all skills | Low |
| 17 | OBO date-based versioning missing | curator | Low |

Several of these have been addressed in current skill versions
(e.g., ROBOT template gotchas are now documented in the architect
skill; BFO known ambiguities section was added to
`bfo-categories.md`; oaklib adapter inconsistency notes are in
`tool-decision-tree.md`; Domain/range decision procedure is in
the conceptualizer). Others remain open:

- **ODK integration**: no documentation of edit-release split,
  `{name}-edit.owl`, `make prepare_release`, DOSDP patterns,
  GitHub Actions templates.
- **Multi-ontology coordination**: no workspace-level
  `imports-manifest.yaml` or cross-ontology consistency checks.
- **SHACL authoring**: templates and patterns absent; the
  architect skill acknowledges shapes as outputs but does not
  teach shape generation.
- **Mapping maintenance lifecycle**: when source/target ontology
  releases a new version, there is no automated "re-validate and
  re-map obsoleted terms" flow linking curator → mapper.
## 7. Current-State Quality Assessment of the 8 Skills

A structural audit of the SKILL.md files (lengths: 254–412 lines;
total skills 2,335 lines + shared materials 1,967 lines ≈ 4,302
lines total). The key observations:

### 7.1 Strengths

- **Methodological grounding**: every skill traces back to
  METHONTOLOGY / NeOn / CQ-driven / Kendall-McGuinness. The
  pipelines (A/B/C) are explicit and non-overlapping.
- **Handoff specificity**: not vague — explicit artifact lists
  with file paths, formats, and checklists. This prevents quality
  debt from cascading downstream.
- **Safety culture**: 10 explicit rules + hook-level enforcement +
  repeated callouts in every skill.
- **Real-world pragmatism**: addresses ELK's silent ignoring of
  non-EL axioms, ROBOT template silent failures,
  oaklib serialization instability, lexical-match false positive
  rates, `skos:exactMatch` transitivity contamination.
- **Progressive disclosure**: shared materials carry the depth
  (BFO decision tree, 16 axiom patterns, 16 anti-patterns);
  skills reference rather than duplicate.

### 7.2 Weaknesses

- **Activation triggers are thin**. Most skills list 3–5 trigger
  phrases in "When to Activate". Anthropic skill-creator convention
  favors rich, specific descriptions in the YAML `description`
  field that match natural user intents. Several skills have
  generic descriptions that may under-trigger
  (`sparql-expert`: "SPARQL", "query", "knowledge graph"; `mapper`:
  "mapping", "alignment", "SSSOM"). Missing variants include
  "write SPARQL", "test CQ", "validate mapping", "check mapping
  quality", "find obsoleted terms", "update ontology", "manage
  import freshness".
- **Examples are thin**. BFO decision trees show categories but
  have few worked end-to-end examples (e.g., "Is an orchestra an
  Object or Object Aggregate?" walkthrough). Axiom patterns show
  Manchester Syntax but only 1–2 examples per pattern.
  Conceptualizer Step 3 doesn't show a complete BFO alignment for
  a domain concept. Mapper Step 3 (LLM verification) lacks a
  sample evaluation prompt or output.
- **Iteration guidance missing**. Phases appear linear, but in
  practice conceptualizer may need scout to re-extract a module,
  or architect may need conceptualizer to resolve an ambiguous
  BFO alignment. No explicit "loopback" protocol in
  CONVENTIONS.md.
- **Reasoner strategy fragmented**. ELK vs HermiT guidance is
  scattered: architect says "ELK for dev, HermiT for pre-release",
  validator says "escalate to HermiT if ELK seems incomplete"
  without criteria, conceptualizer doesn't specify. Needs a
  unified "reasoner strategy by phase" table.
- **SHACL underdeveloped**. Quality checklist prescribes SHACL
  validation; architect lists shapes as an output artifact; but no
  skill teaches shape generation, and there is no
  `shacl-patterns.md` shared material.
- **Mapping maintenance workflow unclear**. Curator describes
  import refresh (detecting obsoleted upstream terms) but doesn't
  specify the handoff to mapper for re-mapping.
- **Progress criteria vague**. Handoff checklists are lists, not
  thresholds. "Glossary covers all pre-glossary terms" doesn't
  define coverage %. "Every class is aligned to BFO" doesn't
  define what rationale is required.
- **SPARQL validation invocation inconsistent**. `sparql-expert`
  prescribes validation; requirements Step 7 generates test
  queries without an explicit `sparql-expert` call; scout's CQ
  benchmark probe runs SPARQL without invoking the validator.
- **ODK conventions absent** (as noted in §6).
- **No "getting started" narrative**. A new user or agent has no
  multi-page walkthrough of a small ontology from requirements
  through release demonstrating all 8 skills in sequence on a
  concrete domain (say, a small music or astronomy vocab).

### 7.3 Skill-by-skill summary

| Skill | Lines | Key strengths | Key gaps |
|-------|-------|---------------|----------|
| `ontology-requirements` | 277 | 6-type CQ taxonomy, traceability matrix, use-case template, MoSCoW + anti-pattern guards | No worked ORSD; "process gate enforcing CQs-before-conceptualization" is guidance only |
| `ontology-scout` | 267 | Always-reuse baseline, NeOn decision tree, CQ benchmark probe, MIREOT vs STAR vs BOT trade-offs, import pitfalls | ODP section is superficial (lists 7 patterns, no templates); no fallback if registries unreachable; license compatibility matrix absent |
| `ontology-conceptualizer` | 255 | Middle-out strategy, architecture layering, BFO procedure, domain/range decision procedure, 10 anti-patterns to check | Axiom pattern selection has a table but no when/why; architecture layering introduced but not revisited in outputs |
| `ontology-architect` | 413 | OWL 2 profile table, ROBOT template pitfalls (7), KGCL workflow, LinkML scope note, rdflib as OWLAPY alternative, reasoner escalation, ODK awareness box | SHACL step is a bullet, not a workflow; LinkML + ROBOT integration unclear |
| `ontology-mapper` | 282 | Confidence triage with thresholds, LLM verification, clique analysis, cross-domain predicate defaults | No concrete LLM verification prompt template; mapping maintenance workflow underspecified |
| `ontology-validator` | 273 | 7-level pipeline, OWA-vs-CWA framing, coverage metrics, diff report, evaluation-dimensions distinction | No explicit pass/fail criteria for Levels 5–6; diff timing vs reasoning unclear |
| `ontology-curator` | 300 | Deprecation propose-then-apply, KGCL command mapping, OBO date-based versioning alongside semver, FAIR assessment table, release pipeline | Async review workflow not specified; mapping maintenance not linked to mapper |
| `sparql-expert` | 276 | Property path table, RDF-star patterns, entailment regime awareness, performance tips | No endpoint authentication; federated SERVICE example not integrated into workflow |
## 8. Open Questions the Research Session Should Answer

These are the decision-level questions that block further
iteration. The research prompt (in the companion file) asks the
research session to produce explicit recommendations for each.

1. **Skill description quality for triggering.** The Anthropic
   skill-creator convention is that the `description` field
   should be rich enough that a model consistently routes
   relevant intents to the skill. Are the current descriptions
   strong? What would Anthropic-style best practice look like
   for these 8 skills?

2. **Progressive disclosure balance.** Right now ~45% of
   material lives in shared references. Is the balance right,
   or are the SKILL.md files carrying duplicate content that
   should be factored out?

3. **Worked examples and pedagogy.** For each of the 16 axiom
   patterns, 16 anti-patterns, and the BFO decision tree, what
   worked-example format maximizes agent performance? (Candidates:
   "Before / After" examples, "Wrong / Right" examples, full
   case studies, running thread through a small domain.)

4. **Iteration / feedback loops.** The pipelines are currently
   described as linear. How should we specify iteration points,
   loopback protocols, and escalation paths between skills? What
   belongs in CONVENTIONS.md vs per-skill vs a new
   `iteration-patterns.md`?

5. **Professional ontologist parity.** What do senior OBO
   Foundry ontologists actually do that is not yet represented?
   (From Appendix D we know ODK, DOSDP, GitHub Actions, import
   refresh, OBO Dashboard; what else?)

6. **Agent-specific design considerations.** Where do LLMs add
   value (CQ-to-SPARQL, definition writing, mapping verification),
   where do they need guardrails (complex DL axioms, reasoner
   simulation, large-scale ontology understanding, BFO alignment
   nuance)? How should skill files encode "LLM verification
   required" markers?

7. **Skill decomposition.** Are there skills that should be split
   (architect currently handles ROBOT templates + KGCL + OWLAPY +
   LinkML + reasoning — this is 412 lines)? Are there skills that
   should be merged?

8. **Activation precision.** Should the workspace adopt a
   stricter "process skills first, implementation skills second"
   priority (like Anthropic's using-superpowers skill)? How
   should we handle cross-cutting skills like `sparql-expert`
   and `ontology-validator`?

9. **Skill-authoring conventions.** Is the `CONVENTIONS.md`
   standard itself at the right level of detail? What is missing
   (e.g., "examples" as a required section, "LLM verification
   required" markers, "iteration entry points")?

10. **Evaluation loop.** How should we measure whether these
    improvements actually work? What eval harness would validate
    that a refined skill does better on real ontology-engineering
    tasks than the current version?


---

# Appendix A: Skill Authoring Conventions and Skill Files (Verbatim)

The following files are embedded verbatim. They are the canonical source; any synthesis above should be cross-checked against them.


### `.claude/skills/CONVENTIONS.md` — Skill authoring standard

```markdown
# Ontology Skill Conventions

Governing document for all 8 ontology skills. Every SKILL.md must conform
to the standards defined here.

## Methodology Backbone

The 8 skills map to the ontology engineering lifecycle as defined in
`_shared/methodology-backbone.md`:

| Lifecycle Phase | Skill | Primary Methodology |
|----------------|-------|-------------------|
| 1. Specification | `ontology-requirements` | CQ-Driven (Gruninger & Fox) |
| 2. Knowledge Acquisition | `ontology-scout` | NeOn Scenarios 1-4 |
| 3. Conceptualization | `ontology-conceptualizer` | METHONTOLOGY + BFO alignment |
| 4. Formalization | `ontology-architect` | POD (Programmatic Ontology Development) |
| 5. Integration | `ontology-mapper` | SSSOM + NeOn Scenario 5 |
| 6. Evaluation | `ontology-validator` | TDOD (Test-Driven Ontology Development) |
| X. Querying | `sparql-expert` | Cross-cutting |
| X. Maintenance | `ontology-curator` | NeOn Scenario 9 |

## Skill Authoring Standard

Every SKILL.md must contain these sections, in this order:

1. **YAML Front Matter** — `name`, `description`
2. **Role Statement** — What this skill is and what it is responsible for
3. **When to Activate** — Trigger conditions (user keywords, pipeline stage)
4. **Shared Reference Materials** — List of `_shared/` files this skill reads
5. **Core Workflow** — Numbered steps with concrete commands
6. **Tool Commands** — Exact CLI/Python examples for each operation
7. **Outputs** — Files produced, naming conventions, formats
8. **Handoff** — What the next skill in the pipeline expects to receive
9. **Anti-Patterns to Avoid** — Skill-specific mistakes
10. **Error Handling** — What to do when things fail

See `SKILL-TEMPLATE.md` for the skeleton.

## Shared Terminology

All skills must use these canonical terms consistently:

| Canonical Term | Do NOT Use | Definition |
|---------------|-----------|-----------|
| class | concept, type, category | An OWL class (set of individuals) |
| property | relation, attribute, predicate | OWL object or data property |
| individual | instance, entity, thing | A member of a class |
| axiom | rule, statement, assertion | A logical sentence in the ontology |
| restriction | constraint (in OWL context) | An OWL class expression (SomeValuesFrom, etc.) |
| competency question (CQ) | use case, requirement | A question the ontology must be able to answer |
| CURIE | short IRI, prefixed name | Compact URI (e.g., `BFO:0000001`) |
| IRI | URL, URI | Internationalized Resource Identifier |
| taxonomy | hierarchy, tree | The SubClassOf structure |
| ontology | knowledge graph (when referring to TBox) | The formal model (TBox + ABox) |
| deprecate | delete, remove, obsolete (as verb) | Mark term as `owl:deprecated true` |
| mapping | alignment, cross-reference | A correspondence between terms (SSSOM) |
| reasoner | classifier, inference engine | Software that computes entailments (ELK, HermiT) |

## Tool Selection Rules

### Primary tools (always try first)

1. **ROBOT CLI** — for build operations (merge, reason, report, template,
   verify, diff, convert, extract, annotate)
2. **oaklib (runoak)** — for navigation, search, KGCL change application,
   lexmatch
3. **KGCL** — for human-reviewable change proposals

### Secondary tools (escalate when primary cannot handle)

4. **OWLAPY** — complex DL axioms requiring OWL API (qualified cardinality,
   role chains, nested expressions)
5. **owlready2** — rapid prototyping, ORM-style interaction, SQLite quadstore
6. **LinkML** — schema-first modeling, multi-format artifact generation
7. **rdflib** — raw RDF triple manipulation, custom serialization
8. **pyshacl** — SHACL shape validation
9. **sssom-py** — SSSOM file management and validation

### Escalation criteria

Escalate to a secondary tool only when:
- The primary tool lacks the required expressivity
- The operation is not supported by any primary tool
- Performance requirements demand a specialized tool

See `_shared/tool-decision-tree.md` for the full decision flowchart.

## Cross-Skill Handoff Specification

### Pipeline A — New Ontology

```
requirements ──→ scout ──→ conceptualizer ──→ architect ──→ validator
```

| From | To | Artifacts Passed |
|------|----|-----------------|
| requirements | scout | `ontologies/{name}/docs/pre-glossary.csv`, `ontologies/{name}/docs/scope.md` |
| requirements | conceptualizer | `ontologies/{name}/docs/competency-questions.yaml`, `ontologies/{name}/docs/pre-glossary.csv` |
| scout | conceptualizer | reuse report, import term lists, ODP recommendations |
| conceptualizer | architect | `ontologies/{name}/docs/glossary.csv`, `ontologies/{name}/docs/conceptual-model.yaml`, `ontologies/{name}/docs/bfo-alignment.md`, `ontologies/{name}/docs/axiom-plan.yaml`, `ontologies/{name}/docs/property-design.yaml` |
| architect | validator | `ontologies/{name}/{name}.ttl`, `ontologies/{name}/shapes/{name}-shapes.ttl`, `ontologies/{name}/tests/*.sparql`, `ontologies/{name}/tests/cq-test-manifest.yaml` |

### Pipeline B — Mapping

| From | To | Artifacts Passed |
|------|----|-----------------|
| scout | mapper | Target ontology identifiers, reuse recommendations |
| mapper | validator | `ontologies/{name}/mappings/*.sssom.tsv` |

### Pipeline C — Evolution

| From | To | Artifacts Passed |
|------|----|-----------------|
| curator | validator | Modified `ontology.ttl`, KGCL change log |

### Cross-cutting handoffs

| Skill | Can Be Called By | Provides |
|-------|-----------------|----------|
| sparql-expert | Any skill | SPARQL queries, query results |
| validator | architect, curator, mapper | Validation reports |

## Safety Rules (Non-Negotiable)

These rules apply to every skill. Violations are never acceptable.

1. **Never hand-edit structural axioms** (SubClassOf, EquivalentClass,
   DisjointClasses, property assertions) in `.owl`, `.ttl`, or `.rdf`
   files — always use ROBOT, oaklib, or Python tools. Annotation-only
   edits (labels, definitions, synonyms) may be hand-edited if followed
   by `robot report` validation. Merge conflict resolution inherently
   requires hand-editing — always run `robot reason` afterward.
2. **Always run the reasoner** (`robot reason`) after any structural change
   to the ontology
3. **Always run quality report** (`robot report`) before committing
   ontology changes
4. **Never delete terms** — deprecate with `owl:deprecated true` and
   provide a replacement pointer (`obo:IAO_0100001`)
5. **Propose KGCL patches** for human review before applying changes
   to shared ontologies
6. **Validate SPARQL syntax** before execution
7. **Check for existing terms** (via `runoak search`) before creating
   new ones
8. **Never execute** SPARQL UPDATE/DELETE against production endpoints
9. **Read before modifying** — always read the existing ontology file
   before making changes
10. **Back up before bulk operations** — create a checkpoint before
    ROBOT template or batch KGCL application

## Output Artifact Standards

### File Naming

| Artifact Type | Naming Pattern | Example |
|--------------|---------------|---------|
| Main ontology | `{name}.ttl` | `music.ttl` |
| Working copy | `{name}-edit.ttl` | `music-edit.ttl` |
| SHACL shapes | `{name}-shapes.ttl` | `music-shapes.ttl` |
| SSSOM mappings | `{source}-to-{target}.sssom.tsv` | `music-to-wikidata.sssom.tsv` |
| CQ tests | `cq-{id}.sparql` | `cq-001.sparql` |
| ROBOT templates | `{name}-template.tsv` | `instruments-template.tsv` |
| KGCL patches | `{name}-changes.kgcl` | `music-v2-changes.kgcl` |
| Quality reports | `{name}-report.tsv` | `music-report.tsv` |

### Serialization

- **Default format**: Turtle (`.ttl`)
- **Manchester Syntax**: for human review and LLM interaction
- **OWL/XML**: only when required by tooling (ROBOT intermediate)
- **JSON-LD**: for web integration and APIs

### Metadata Requirements

Every ontology file must include in its header:
- `owl:versionIRI` — versioned IRI
- `owl:versionInfo` — version string (date or semver)
- `dcterms:title` — human-readable title
- `dcterms:description` — purpose and scope
- `dcterms:license` — license URI
- `dcterms:creator` — creator(s)
- `owl:imports` — all imported ontologies

```


### `.claude/skills/SKILL-TEMPLATE.md` — Template for new skills

```markdown
<!-- SKILL-TEMPLATE.md — Copy this file to create a new SKILL.md -->
<!-- Replace all {placeholders} with actual values -->
<!-- Delete this comment block in the final SKILL.md -->

---
name: {skill-name}
description: >
  {One to three sentence description of the skill's purpose. Include
  keywords that trigger activation.}
---

# {Skill Title}

## Role Statement

{What this skill is, what it is responsible for, and what it is NOT
responsible for. 2-3 sentences.}

## When to Activate

- {Trigger condition 1: user keywords or phrases}
- {Trigger condition 2: pipeline stage or prerequisite}
- {Trigger condition 3: specific user intent}

## Shared Reference Materials

Read these files from `_shared/` before beginning work:

- `_shared/methodology-backbone.md` — lifecycle phase context
- `_shared/{relevant-reference}.md` — {why this skill needs it}
- `_shared/{relevant-reference}.md` — {why this skill needs it}

## Core Workflow

### Step 1: {Step Name}

{Description of what to do.}

```bash
{Concrete command example}
```

### Step 2: {Step Name}

{Description of what to do.}

### Step N: {Step Name}

{Description of what to do.}

## Tool Commands

{Concrete CLI and Python examples for every operation this skill performs.
Group by operation type. Include exact flags and arguments.}

### {Operation Category}

```bash
{command with real flags and arguments}
```

### {Operation Category}

```python
{Python snippet with imports and real function calls}
```

## Outputs

This skill produces:

| Artifact | Location | Format | Description |
|----------|----------|--------|-------------|
| {artifact name} | `{path/to/file}` | {format} | {what it contains} |

## Handoff

**Receives from**: {previous skill(s)} — {what artifacts are expected as input}

**Passes to**: {next skill(s)} — {what artifacts are produced for the next stage}

**Handoff checklist**:
- [ ] {Required artifact 1 exists and is valid}
- [ ] {Required artifact 2 exists and is valid}

## Anti-Patterns to Avoid

- {Anti-pattern 1}: {why it's wrong and what to do instead}
- {Anti-pattern 2}: {why it's wrong and what to do instead}

## Error Handling

| Error | Likely Cause | Recovery |
|-------|-------------|----------|
| {Error type} | {Common cause} | {What to do} |

```


### `.claude/skills/ontology-requirements/SKILL.md` — ontology-requirements skill

```markdown
---
name: ontology-requirements
description: >
  Manages ontology requirements specification. Elicits, refines, and
  formalizes competency questions (CQs). Generates ORSD documents and
  CQ test suites. Use when starting a new ontology, defining scope, or
  creating acceptance tests.
---

# Ontology Requirements Engineer

## Role Statement

You are responsible for the specification phase of ontology development.
You elicit competency questions from stakeholders, define scope, produce
the Ontology Requirements Specification Document (ORSD), and generate
SPARQL-based test suites that serve as acceptance criteria throughout the
lifecycle. You do NOT design the taxonomy or formalize axioms — that is
the work of downstream skills.

## When to Activate

- User wants to start a new ontology project
- User wants to define scope or requirements for an ontology
- User mentions "competency questions", "CQs", or "requirements"
- User wants to create tests or acceptance criteria for an ontology
- Pipeline A is initiated (this skill runs first)

## Shared Reference Materials

Read these files from `_shared/` before beginning work:

- `_shared/methodology-backbone.md` — lifecycle phase context (Phase 1: Specification)
- `_shared/naming-conventions.md` — term standards for the pre-glossary
- `_shared/namespaces.json` — standard prefixes for SPARQL test queries

## Core Workflow

### Step 1: Domain Scoping

Gather from the user:
- Domain description and intended use cases
- Key stakeholders and their information needs
- What is IN scope and what is OUT of scope
- Known constraints (OWL profile, size, existing systems)

Produce `ontologies/{name}/docs/scope.md` documenting scope decisions.

### Step 1.5: Use Case Development

Before drafting CQs, capture structured use cases that connect stakeholder
needs to ontology behavior.

Use this template for each use case:

```yaml
- id: UC-001
  name: "Find all instruments available for student checkout"
  actor: "Music school librarian"
  goal: "Identify currently available instruments by type and condition"
  preconditions:
    - "Instrument inventory is represented in the ontology/graph"
  main_flow:
    - "Actor filters by instrument family"
    - "System returns available instruments with condition labels"
  postconditions:
    - "Actor has a candidate list for checkout assignment"
  related_cqs: []
  priority: must_have
```

Guidance:
- Each use case should generate 3-10 CQs.
- Keep use cases as living artifacts; refine them after stakeholder review.
- Store use cases in `ontologies/{name}/docs/use-cases.yaml`.

Example derived CQs from `UC-001`:
- "Which instruments are currently available for checkout?"
- "What condition rating does each available instrument have?"
- "Which available instruments belong to the string family?"

### Step 2: CQ Elicitation

For each stakeholder perspective and use case, generate candidate CQs across
these types:

| CQ Type | Pattern | Example |
|---------|---------|---------|
| Enumerative | "What are all the X?" | "What instruments are in the orchestra?" |
| Boolean | "Is X a Y?" | "Is a piano a string instrument?" |
| Relational | "What Y relates to X via R?" | "What pieces are composed for violin?" |
| Quantitative | "How many X have property P?" | "How many strings does a guitar have?" |
| Constraint | "Can X and Y co-occur?" | "Can an instrument be both wind and string?" |
| Temporal | "When does X occur relative to Y?" | "When was the instrument first manufactured?" |

### Step 3: CQ Refinement

- Decompose compound questions into atomic CQs
- Remove duplicates and subsumptions
- Classify each CQ by type (from Step 2)
- Assign unique IDs: `CQ-{NNN}`
- Add at least one concrete `sample_answer`
- Record `derivation_method`: `direct_lookup` | `inference` | `aggregation` | `external_join`
- Record explicit `out_of_scope` boundaries

### Step 4: Prioritization (MoSCoW)

Classify each CQ:
- **Must Have**: core CQs without which the ontology is useless
- **Should Have**: significantly enhance utility
- **Could Have**: nice-to-have for future iterations
- **Won't Have**: explicitly out of scope (record why)

### Step 5: Formalization

For each Must/Should CQ, produce a structured entry:

```yaml
- id: CQ-001
  source_use_case: UC-001
  natural_language: "What instruments exist in the ontology?"
  type: enumerative
  priority: must_have
  sample_answer:
    - instrument: ex:Violin_001
      label: "student violin 001"
  derivation_method: direct_lookup
  out_of_scope:
    - "Instrument pricing and procurement details"
  sparql: |
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX : <http://example.org/ontology/>
    SELECT ?instrument ?label WHERE {
      ?instrument rdf:type :Instrument ;
                  rdfs:label ?label .
    }
  expected_result: non_empty
  required_classes:
    - Instrument
  required_properties: []
  required_axioms: []
```

### Step 6: Pre-Glossary Extraction

From all CQs, extract candidate terms:
- **Candidate classes**: nouns and noun phrases
- **Candidate properties**: verbs and relationship phrases
- **Candidate individuals**: proper nouns, specific instances

Output as `ontologies/{name}/docs/pre-glossary.csv` with columns:
`term, category (class|property|individual), source_cq, notes`

### Step 7: Test Suite Generation

For each formalized CQ:
- Generate a `.sparql` file in `ontologies/{name}/tests/`
- Enumerative CQs: SELECT query expecting non-empty results
- Constraint CQs: SELECT query expecting zero rows (zero violations)
- Generate `ontologies/{name}/tests/cq-test-manifest.yaml` linking CQs to test files

### Step 8: Traceability Matrix

Maintain explicit requirement traceability in `ontologies/{name}/docs/traceability-matrix.csv`.

Required mapping chain:

```
Stakeholder Need -> Use Case -> CQ ID -> Ontology Term(s) -> SPARQL Test
```

CSV template:

```csv
stakeholder_need,use_case_id,cq_id,ontology_terms,sparql_test
"Track instrument availability",UC-001,CQ-001,"Instrument;hasAvailabilityStatus",ontologies/{name}/tests/cq-001.sparql
```

Rules:
- Every stakeholder need must map to at least one use case and CQ.
- Every CQ must map to at least one ontology term and test query.
- Update this matrix whenever CQs are added, merged, or deprecated.

## Tool Commands

### Writing SPARQL test files

```bash
# Write individual test queries
cat > ontologies/{name}/tests/cq-001.sparql << 'EOF'
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <http://example.org/ontology/>

# CQ-001: What instruments exist in the ontology?
# Expected: non-empty result set
SELECT ?instrument ?label WHERE {
  ?instrument rdf:type :Instrument ;
              rdfs:label ?label .
}
EOF
```

### Validating SPARQL syntax

```bash
uv run python -c "
from rdflib.plugins.sparql import prepareQuery
prepareQuery(open('ontologies/{name}/tests/cq-001.sparql').read())
print('Valid')
"
```

## Outputs

This skill produces:

| Artifact | Location | Format | Description |
|----------|----------|--------|-------------|
| Scope document | `ontologies/{name}/docs/scope.md` | Markdown | In/out scope, constraints, stakeholders |
| Use case catalog | `ontologies/{name}/docs/use-cases.yaml` | YAML | Structured use cases driving CQ derivation |
| ORSD | `ontologies/{name}/docs/orsd.md` | Markdown | Full requirements specification |
| CQ list | `ontologies/{name}/docs/competency-questions.yaml` | YAML | Structured CQ definitions with SPARQL |
| Pre-glossary | `ontologies/{name}/docs/pre-glossary.csv` | CSV | Candidate terms extracted from CQs |
| Test queries | `ontologies/{name}/tests/cq-*.sparql` | SPARQL | One file per CQ |
| Test manifest | `ontologies/{name}/tests/cq-test-manifest.yaml` | YAML | Maps CQ IDs to test files and expectations |
| Traceability matrix | `ontologies/{name}/docs/traceability-matrix.csv` | CSV | End-to-end trace: need -> use case -> CQ -> term -> test |

## Handoff

**Receives from**: User input (domain description, use cases, stakeholder needs)

**Passes to**:
- `ontology-scout` — `ontologies/{name}/docs/pre-glossary.csv`, `ontologies/{name}/docs/scope.md`
- `ontology-conceptualizer` — `ontologies/{name}/docs/competency-questions.yaml`,
  `ontologies/{name}/docs/pre-glossary.csv`, `ontologies/{name}/docs/traceability-matrix.csv`

**Handoff checklist**:
- [ ] All Must-Have CQs have formalized SPARQL queries
- [ ] Pre-glossary covers all terms mentioned in CQs
- [ ] Scope document clearly separates in-scope from out-of-scope
- [ ] Test manifest references all generated `.sparql` files
- [ ] Every stakeholder need traces to at least one use case and CQ
- [ ] Every CQ traces to at least one SPARQL test in the matrix

## Anti-Patterns to Avoid

- **Vague CQs**: "What is the meaning of X?" — CQs must be answerable by
  a SPARQL query against the ontology. A good CQ is specific enough to
  fail: "Which string instruments require a bow?" can return zero results;
  "What instruments exist?" cannot.
- **Implementation-coupled CQs**: "How is X stored in the database?" — CQs
  describe information needs, not implementation details
- **Over-specification**: Designing the taxonomy during requirements —
  leave that to the conceptualizer
- **CQs beyond OWL expressivity**: "What is the probability that X is Y?" —
  OWL cannot represent probabilities natively
- **Retroactive CQs**: Writing CQs after the ontology to justify existing
  structure. CQs must be written BEFORE conceptualization begins — they
  drive the design, not document it. If CQs arrive after modeling starts,
  flag this explicitly and re-evaluate the model.
- **Stale CQ tests**: CQ SPARQL tests must be updated whenever the ontology
  evolves. Untouched tests become meaningless. Link CQ maintenance to the
  curator skill's change workflow.
- **Prioritization bias**: Involve multiple stakeholders independently
  before consolidating priorities. The most vocal stakeholder's CQs should
  not automatically become Must-Have.

## Error Handling

| Error | Likely Cause | Recovery |
|-------|-------------|----------|
| CQ cannot be expressed in SPARQL | CQ is too vague or beyond OWL expressivity | Decompose into simpler CQs or mark as Won't Have |
| Duplicate CQs detected | Stakeholder overlap | Merge and reference all source stakeholders |
| Pre-glossary has conflicting terms | Polysemy in domain language | Flag for conceptualizer to disambiguate |

```


### `.claude/skills/ontology-scout/SKILL.md` — ontology-scout skill

```markdown
---
name: ontology-scout
description: >
  Searches for and evaluates reusable ontological resources. Queries
  OLS, BioPortal, OBO Foundry, and LOV. Extracts ontology modules via
  ROBOT. Finds applicable Ontology Design Patterns. Use when looking
  for existing ontologies to reuse or align with.
---

# Ontology Scout (Reuse Advisor)

## Role Statement

You are responsible for the knowledge acquisition phase — specifically,
discovering and evaluating existing ontological resources before building
from scratch. You search registries, evaluate candidate ontologies for
quality and coverage, recommend reuse strategies, and extract modules via
ROBOT. You do NOT create new classes or axioms — that is the work of
downstream skills.

## When to Activate

- User wants to find existing ontologies covering their domain
- User mentions "reuse", "import", "alignment", or "existing ontology"
- Starting conceptualization (always check what exists first)
- Pipeline A Step 2 or Pipeline B Step 1

## Shared Reference Materials

Read these files from `_shared/` before beginning work:

- `_shared/methodology-backbone.md` — lifecycle phase context (Phase 2: Knowledge Acquisition)
- `_shared/bfo-categories.md` — needed to evaluate BFO alignment of candidates
- `_shared/naming-conventions.md` — to assess naming quality of candidates
- `_shared/namespaces.json` — standard prefixes for search queries

## Core Workflow

### Always-Reuse Baseline

Before domain-specific search, assume these foundational ontologies are
in-scope unless there is a project-specific reason not to use them:

- **Dublin Core Terms (`dcterms`)**: common metadata fields
- **SKOS**: concept labeling and lexical organization
- **PROV-O**: provenance and derivation modeling
- **FOAF or schema.org**: people/organization basics

Document baseline reuse decisions in the reuse report before evaluating
domain ontologies.

### Step 1: Search Registries

For each candidate term from the pre-glossary, search multiple registries:

```bash
# Search via oaklib (OLS backend)
uv run runoak -i ols: search "TERM"

# Search via oaklib (BioPortal backend, if API key configured)
uv run runoak -i bioportal: search "TERM"

# Search OBO Foundry ontologies specifically
uv run runoak -i sqlite:obo:{ontology_id} search "TERM"
```

Also check specialized repositories when relevant:
- OMG specifications catalog
- COLORE repository
- Schema.org vocabulary docs
- IBC AgroPortal
- Google Dataset Search (for ontology-linked datasets)

### Step 2: Evaluate Candidates

Score each candidate ontology on nine dimensions:

| Criterion | Weight | How to Assess |
|-----------|--------|--------------|
| Coverage | High | % of pre-glossary terms found in the ontology |
| Quality | High | OBO Dashboard score, label/definition coverage, ROBOT report |
| License | Required | Must be open (CC-BY or CC0 preferred) |
| Community | Medium | Active maintenance, GitHub activity, publications |
| BFO Alignment | Medium | Already aligned to BFO? Uses RO relations? |
| Syntactic correctness | Required | `robot validate --input candidate.owl` |
| Logical consistency | Required | `robot reason --reasoner ELK --input candidate.owl` |
| Modularization | Medium | Can modules be imported independently? |
| Metadata completeness | Medium | `robot report --input candidate.owl` + header metadata checks |

Even when a candidate is not reusable, keep it as a benchmark reference for
coverage and modeling comparison.

### Step 3: Reuse Decision

Apply the NeOn reuse decision tree:

| Coverage | Strategy | Tool |
|----------|----------|------|
| >80% of needs | Direct Import | `owl:imports` |
| 40-80% | Module Extraction | `robot extract` |
| <40% but has useful terms | MIREOT (term borrowing) | `robot extract --method MIREOT` |
| Good structure, wrong domain | ODP Reuse | Instantiate design pattern |
| Related ontology exists | SSSOM Mapping | Defer to `ontology-mapper` |

#### CQ Benchmark Probe

Run representative competency-question probes against each short-listed
candidate (or extracted module) to test practical fit:

- Select 3-5 high-priority CQs from requirements.
- Draft quick probe queries (or adapt existing CQ drafts).
- Record whether the candidate can answer each probe fully, partially, or not
  at all.

### Step 4: Module Extraction

#### Extraction Method Trade-offs

| Method | What It Extracts | Best For | Watch Out |
|--------|-----------------|----------|-----------|
| MIREOT | Term + ancestors only | Large ontologies (GO, ChEBI) — fast, minimal | Loses sibling context and some axioms |
| STAR | All axioms involving the term | Small/medium ontologies — most complete | Can pull in unexpected classes via axiom references |
| BOT | Term + all ancestors (bottom module) | Good middle ground | May include more than needed for deep hierarchies |
| TOP | Term + all descendants (top module) | Extracting a subtree | Large result if term has many descendants |

**Import management pitfalls**:
- **Transitive import chains**: Importing one OBO ontology can pull in dozens
  of transitive imports. Check what you are actually loading.
- **Import freshness**: Upstream ontologies release on their own schedule. Pin
  versions and use a refresh workflow (see curator skill).
- **Circular imports**: Occasionally A imports B imports C imports A. This
  causes reasoner failures. Check for cycles before committing.
- **Stale term files**: The `*_terms.txt` pattern (one IRI per line) breaks
  silently if a term has been obsoleted upstream. Validate term existence
  during import refresh.

For recommended imports:

```bash
# Create term list file
echo "http://purl.obolibrary.org/obo/GO_0008150" > imports/go_terms.txt
echo "http://purl.obolibrary.org/obo/GO_0003674" >> imports/go_terms.txt

# Extract module (STAR method — most complete)
robot extract --method STAR \
  --input-iri http://purl.obolibrary.org/obo/go.owl \
  --term-file imports/go_terms.txt \
  --output imports/go_import.owl

# Extract module (MIREOT — minimal, just term + parents)
robot extract --method MIREOT \
  --input-iri http://purl.obolibrary.org/obo/go.owl \
  --term-file imports/go_terms.txt \
  --output imports/go_import.owl
```

### Step 5: ODP Search

Search for applicable Ontology Design Patterns:

- **Part-Whole**: Modeling mereological relationships
- **N-ary Relation**: Relations with >2 participants
- **Value Partition**: Quality values as controlled vocabularies
- **Participation**: Continuant participation in processes
- **Information Realization**: GDC/ICE patterns
- **Role**: Social/contextual properties

Document which ODPs apply and how they should be instantiated.

## Tool Commands

### Registry search

```bash
# OLS search with result limit
uv run runoak -i ols: search "musical instrument" -l 20

# Get term details from a specific ontology
uv run runoak -i sqlite:obo:go info GO:0008150

# Get ancestors of a term
uv run runoak -i sqlite:obo:go ancestors GO:0008150

# Check if ontology is in OBO Foundry
uv run runoak -i obo: ontologies
```

### ROBOT extraction

```bash
# BOT extraction (bottom module — term + all ancestors)
robot extract --method BOT \
  --input source.owl \
  --term "http://example.org/Term" \
  --output module.owl

# TOP extraction (top module — term + all descendants)
robot extract --method TOP \
  --input source.owl \
  --term "http://example.org/Term" \
  --output module.owl
```

### Quality assessment of candidate

```bash
# Syntax validation
robot validate --input candidate.owl

# Logical consistency
robot reason --reasoner ELK --input candidate.owl

# Run ROBOT report on candidate ontology
robot report --input candidate.owl --output candidate-report.tsv

# Check label coverage
uv run runoak -i candidate.owl statistics

# Run representative CQ probes (if available)
robot verify --input candidate.owl --queries ontologies/{name}/tests/candidate-probes/
```

## Outputs

This skill produces:

| Artifact | Location | Format | Description |
|----------|----------|--------|-------------|
| Reuse report | `ontologies/{name}/docs/reuse-report.md` | Markdown | Scored candidate ontologies with recommendations |
| Import term lists | `imports/{source}_terms.txt` | Text (one IRI per line) | Terms to extract from each source |
| Extracted modules | `imports/{source}_import.owl` | OWL/XML | ROBOT-extracted modules |
| ODP recommendations | `ontologies/{name}/docs/odp-recommendations.md` | Markdown | Applicable design patterns with instantiation guidance |

## Handoff

**Receives from**: `ontology-requirements` — `ontologies/{name}/docs/pre-glossary.csv`, `ontologies/{name}/docs/scope.md`

**Passes to**:
- `ontology-conceptualizer` — reuse report, import term lists, ODP recommendations
- `ontology-mapper` (Pipeline B) — target ontology identifiers, reuse recommendations

**Handoff checklist**:
- [ ] Every pre-glossary term has been searched in at least one registry
- [ ] Reuse report includes scored candidates with clear recommendations
- [ ] Extracted modules load without errors (`robot validate`)
- [ ] ODP recommendations reference specific pattern templates

## Anti-Patterns to Avoid

- **Not-invented-here syndrome**: Always search before creating new terms.
  Reuse is preferred over reinvention.
- **Uncritical reuse**: Don't import entire large ontologies (e.g., all of
  GO) when only a handful of terms are needed. Use module extraction.
- **License violations**: Never recommend importing ontologies with
  incompatible licenses.
- **Stale sources**: Check that candidate ontologies are actively maintained.
  An unmaintained ontology is a liability.

## Error Handling

| Error | Likely Cause | Recovery |
|-------|-------------|----------|
| OLS API unreachable | Network issue or rate limit | Retry with backoff; fall back to local SQLite cache |
| ROBOT extract fails | Invalid IRI or unreachable source | Download ontology locally first, then extract |
| No candidates found | Domain is niche or uses non-standard terminology | Broaden search terms; try synonyms from pre-glossary |
| Candidate has no license | License not declared in metadata | Contact maintainers or choose alternatives |

```


### `.claude/skills/ontology-conceptualizer/SKILL.md` — ontology-conceptualizer skill

```markdown
---
name: ontology-conceptualizer
description: >
  Builds conceptual models from requirements. Creates glossaries,
  taxonomies, and property designs. Aligns to BFO upper ontology.
  Detects modeling anti-patterns. Use when designing the structure
  of an ontology before formalization.
---

# Ontology Conceptualizer

## Role Statement

You are responsible for the conceptualization phase — transforming
requirements and knowledge acquisition outputs into a semi-formal
conceptual model. You design the taxonomy, align to BFO, specify
properties, select axiom patterns, and detect anti-patterns. You produce
a blueprint that the architect skill will formalize as OWL 2. You do
NOT write OWL axioms or run the reasoner — that is the architect's job.

## When to Activate

- After requirements are gathered (CQs defined)
- User wants to design a class hierarchy or relations
- User mentions "model", "conceptualize", "taxonomy", or "hierarchy"
- User asks about BFO alignment or upper ontology decisions
- Pipeline A Step 3

## Shared Reference Materials

Read these files from `_shared/` before beginning work:

- `_shared/methodology-backbone.md` — lifecycle phase context (Phase 3: Conceptualization)
- `_shared/bfo-categories.md` — BFO decision procedure for alignment
- `_shared/axiom-patterns.md` — OWL pattern catalog for axiom planning
- `_shared/anti-patterns.md` — modeling mistakes to detect and prevent
- `_shared/naming-conventions.md` — term naming standards

## Core Workflow

### Step 1: Glossary of Terms

From the pre-glossary, refine each term:

| Field | Description |
|-------|------------|
| Term | Preferred label (following naming conventions) |
| Synonyms | Alternative labels |
| Definition | Genus-differentia: "A [parent] that [differentia]" |
| Category | Class / ObjectProperty / DataProperty / Individual |
| Source CQ | Which competency question requires this term |
| BFO Category | Alignment to BFO (from Step 3) |

Output as `ontologies/{name}/docs/glossary.csv`.

### Step 2: Taxonomy Design (Middle-Out Strategy)

Build the class hierarchy using the middle-out approach:

1. **Start in the middle**: Identify the most salient domain concepts
   (the terms stakeholders talk about most)
2. **Generalize upward**: Find appropriate parent classes, aligning to
   BFO where possible
3. **Specialize downward**: Add important sub-distinctions needed by CQs
4. **Single inheritance**: Assert single parent for each class in the
   asserted hierarchy; use defined classes (EquivalentTo) for multiple
   classification paths

#### Modularization Rules

- Start with the 20-30 highest-priority terms grounded in Must-Have CQs.
- Target module size: roughly 100-150 concepts before splitting.
- Seed shared metadata/provenance dependencies early (Dublin Core, SKOS,
  PROV-O) so downstream modules stay consistent.
- Split modules along clear criteria when needed:
  behavioral vs functional vs structural views, or lifecycle slices such as
  as-designed / as-built / as-configured / as-maintained.
- Record module boundaries directly in `ontologies/{name}/docs/conceptual-model.yaml`.

### Step 2.5: Architecture Layering

Assign each module to one architecture layer:

1. **Foundational**: metadata/provenance and upper-level support
2. **Domain-independent**: reusable cross-domain modules (time, geo, units)
3. **Domain-dependent**: domain standards and reference models
4. **Problem-specific**: project ontology modules tailored to current CQs

Document layer assignment for every module in the conceptual model.

### Step 3: Upper Ontology Alignment

For each top-level domain class, apply the BFO decision procedure from
`_shared/bfo-categories.md`:

1. **Continuant or Occurrent?** Does it persist or unfold in time?
2. **If Continuant**: Independent or Dependent?
3. **If Independent**: Material Entity, Immaterial Entity?
4. **If Dependent**: Quality, Role, Disposition, Function, or GDC?
5. **If Occurrent**: Process, Process Boundary, or Temporal Region?

Document each alignment decision with rationale in `ontologies/{name}/docs/bfo-alignment.md`.

### Step 4: Property Design

For each property:

| Field | Value |
|-------|-------|
| Name | camelCase verb phrase |
| Type | ObjectProperty or DataProperty |
| Domain | Source class |
| Range | Target class or datatype |
| Cardinality | min/max or exact |
| Characteristics | functional, inverse-functional, transitive, symmetric |
| Inverse | Inverse property name (if applicable) |
| BFO/RO relation | Which standard relation it specializes |

#### Property Categories Reference

Use this categorization to avoid mixed semantics in one property:

| Category | Typical Example | Preferred Construct |
|----------|------------------|---------------------|
| Intrinsic | `hasMass`, `hasColor` | DataProperty or quality pattern |
| Extrinsic | `locatedIn`, `adjacentTo` | ObjectProperty |
| Meronymic | `hasPart`, `partOf` | ObjectProperty with mereology constraints |
| Spatio-temporal | `occursDuring`, `hasLocationAtTime` | ObjectProperty + temporal indexing pattern |
| Object property (entity-to-entity) | `hasParticipant` | `owl:ObjectProperty` |
| Data property (entity-to-literal) | `hasIdentifier` | `owl:DatatypeProperty` |

#### Domain/Range Decision Procedure

OWL `rdfs:domain` and `rdfs:range` are **inference rules**, not constraints.
Before declaring domain/range on any property, use this decision:

```
Do you want to CONSTRAIN usage (reject invalid data)?
  → Use SHACL:
    - Object properties: sh:class on a property shape
    - Data properties: sh:datatype (and sh:nodeKind sh:Literal)

Do you want to INFER types (classify subjects/objects)?
  → Use OWL: rdfs:domain / rdfs:range
  → But keep domain/range BROAD (parent classes, not leaves)

Do you want to RESTRICT per-class usage?
  → Use local OWL restrictions: SubClassOf hasP some/only C
```

See anti-pattern #10 in `_shared/anti-patterns.md` for the full explanation
of why narrow domain/range declarations cause unintended classification.

Output as `ontologies/{name}/docs/property-design.yaml`.

### Step 5: Axiom Pattern Selection

For each CQ, determine the needed axiom pattern from
`_shared/axiom-patterns.md`:

| CQ Pattern | Axiom Pattern |
|-----------|--------------|
| "Every X has a Y" | Existential restriction (#2) |
| "X can only have Y" | Universal restriction / closure (#3) |
| "X is defined as Y with Z" | Equivalent class (#4) |
| "X and Y never overlap" | Disjoint classes (#5) |
| "X is exactly A, B, or C" | Covering axiom (#6) |
| "X has exactly N of Y" | Qualified cardinality (#7) |
| "X has high/medium/low Z" | Value partition (#8) |
| "X did Y to Z at time T" | N-ary relation (#9) |

Output as `ontologies/{name}/docs/axiom-plan.yaml`.

### Step 6: Anti-Pattern Detection

Review the conceptual model against `_shared/anti-patterns.md`. Check for:

1. Singleton hierarchies (only one subclass)
2. Role-type confusion (roles as subclasses)
3. Process-object confusion (processes as material entities)
4. Missing disjointness (siblings without disjoint axioms)
5. Circular definitions
6. Quality-as-class (quality values as class hierarchies)
7. Information-physical conflation
8. Orphan classes (no named parent)
9. Polysemy (one class for multiple meanings)
10. Domain/range overcommitment

Flag any detected anti-patterns and recommend corrections.

## Tool Commands

### Checking for existing terms

```bash
# Before creating any new class, search for existing terms
uv run runoak -i sqlite:obo:bfo info BFO:0000040  # Material Entity
uv run runoak -i ols: search "instrument"
```

### Visualizing taxonomy (for review)

```bash
# Get tree view of a hierarchy
uv run runoak -i ontology.ttl tree --root EX:0000
```

## Outputs

This skill produces:

| Artifact | Location | Format | Description |
|----------|----------|--------|-------------|
| Glossary | `ontologies/{name}/docs/glossary.csv` | CSV | Complete term glossary with categories and BFO alignment |
| Conceptual model | `ontologies/{name}/docs/conceptual-model.yaml` | YAML | Structured model: classes, hierarchy, module boundaries, layer assignments |
| BFO alignment | `ontologies/{name}/docs/bfo-alignment.md` | Markdown | Alignment rationale for each top-level class |
| Property design | `ontologies/{name}/docs/property-design.yaml` | YAML | Property specifications with domain/range/characteristics |
| Axiom plan | `ontologies/{name}/docs/axiom-plan.yaml` | YAML | Planned axiom patterns per CQ |

## Handoff

**Receives from**:
- `ontology-requirements` — `ontologies/{name}/docs/competency-questions.yaml`, `ontologies/{name}/docs/pre-glossary.csv`
- `ontology-scout` — reuse report, import term lists, ODP recommendations

**Passes to**: `ontology-architect` — all five output artifacts listed above

**Handoff checklist**:
- [ ] Glossary covers all pre-glossary terms (with additions/removals justified)
- [ ] Every class is aligned to a BFO category
- [ ] Every Must-Have CQ has a corresponding axiom plan entry
- [ ] Anti-pattern review is complete with zero unresolved issues
- [ ] User has reviewed and approved the conceptual model

## Anti-Patterns to Avoid

- **Premature formalization**: Don't start writing OWL or ROBOT templates.
  Produce a conceptual model, not axioms.
- **Ignoring BFO**: Every top-level domain class should align to BFO. If
  alignment is unclear, consult `_shared/bfo-categories.md` and document
  the ambiguity for user decision.
- **Over-modeling**: Don't create classes or properties that no CQ requires.
  Every term must trace back to a competency question.
- **Under-specifying relations**: Don't leave domain/range as "to be
  determined." Specify even if provisional — the architect needs this.

## Error Handling

| Error | Likely Cause | Recovery |
|-------|-------------|----------|
| Term doesn't fit any BFO category | Polysemy or category mismatch | Disambiguate the term; consult BFO common mistakes table |
| Conflicting CQ requirements | Stakeholder disagreement | Escalate to user for priority decision |
| Anti-pattern cannot be resolved | Genuine modeling dilemma | Document the trade-off and let user decide |
| Pre-glossary terms missing from reuse report | Scout didn't find matches | Mark as "new term needed" in glossary |

```


### `.claude/skills/ontology-architect/SKILL.md` — ontology-architect skill

```markdown
---
name: ontology-architect
description: >
  Specializes in Programmatic Ontology Development (POD). Creates OWL 2
  axioms, manages class hierarchies, generates ROBOT templates, runs
  reasoners. Uses ROBOT, oaklib, KGCL, OWLAPY, owlready2, and LinkML.
  Use when creating or modifying ontology axioms.
---

# Ontology Architect (POD)

## Role Statement

You are responsible for the formalization phase — encoding the approved
conceptual model as OWL 2 axioms using programmatic methods. You select
the right tool for each operation (see tool decision tree), generate
ROBOT templates for bulk creation, write KGCL patches for individual
changes, and escalate to OWLAPY for complex axioms. You ALWAYS run the
reasoner after structural changes. You NEVER hand-edit ontology files.

## When to Activate

- User wants to create or modify ontology classes, properties, or axioms
- User mentions "add class", "define property", "create axiom", "formalize"
- User wants to formalize a conceptual model as OWL
- Pipeline A Step 4

## Shared Reference Materials

Read these files from `_shared/` before beginning work:

- `_shared/methodology-backbone.md` — lifecycle phase context (Phase 4: Formalization)
- `_shared/tool-decision-tree.md` — when to use each tool
- `_shared/axiom-patterns.md` — OWL pattern catalog
- `_shared/naming-conventions.md` — naming and ID minting standards
- `_shared/namespaces.json` — canonical prefixes
- `_shared/quality-checklist.md` — validation requirements after changes

## Core Workflow

### Step 1: Select OWL 2 Profile

Full OWL 2 is highly expressive but unrestricted reasoning can be costly.
Profiles trade expressivity for better reasoning guarantees and performance.

Reasoning strategy options:
- **Incomplete but sound**: Fast reasoners may miss some entailments.
- **Complete but profile-restricted**: Stay within EL/QL/RL for guaranteed behavior.
- **Complete but potentially expensive**: Full DL reasoning, slower on large ontologies.

| Criterion | Profile | Typical exclusions | Reasoner |
|-----------|---------|--------------------|----------|
| >100K classes, mostly taxonomic | OWL 2 EL | No full negation, universal restrictions, qualified cardinality | ELK |
| OBDA over relational data | OWL 2 QL | Limited class constructors | Ontop-compatible QL tooling |
| Full expressivity needed | OWL 2 DL | None (most expressive decidable profile) | HermiT, Pellet/Openllet |
| Rule-engine style inference | OWL 2 RL | Restricted existential patterns in subclass axioms | Rule engines / RL-compatible reasoners |

Default to OWL 2 DL unless there is a clear scalability or deployment reason
to choose a restricted profile.

### Step 2: Create Ontology Header

Every new ontology needs a Turtle header with metadata:

```turtle
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix prov: <http://www.w3.org/ns/prov#> .

<http://example.org/ontology> a owl:Ontology ;
    owl:versionIRI <http://example.org/ontology/2024-01-01> ;
    owl:versionInfo "2024-01-01" ;
    dcterms:title "Example Ontology"@en ;
    dcterms:description "Purpose and scope"@en ;
    dcterms:creator "Ontology Team" ;
    dcterms:created "2024-01-01"^^xsd:date ;
    dcterms:rights "Copyright holder or organization" ;
    dcterms:license <https://creativecommons.org/licenses/by/4.0/> ;
    prov:wasAttributedTo <https://orcid.org/0000-0000-0000-0000> ;
    prov:generatedAtTime "2024-01-01T00:00:00Z"^^xsd:dateTime .
```

Metadata consistency rule:
- Use one coherent annotation vocabulary strategy across ontology header,
  classes, and properties.
- Required minimum for terms is defined in `_shared/naming-conventions.md`;
  use the same conventions in generated templates and KGCL patches.
- Include PROV-O fields when provenance tracking is required by the project.

### Step 3: Bulk Term Creation via ROBOT Template

For adding >5 terms from the glossary, generate a ROBOT template TSV:

```tsv
ID	LABEL	SC %	DEFINITION	DEFINITION SOURCE
ID	A rdfs:label	SC %	A obo:IAO_0000115	A obo:IAO_0000119
EX:0001	piano	EX:0000	A keyboard instrument that produces sound by striking strings	glossary
EX:0002	violin	EX:0000	A string instrument played with a bow	glossary
```

Execute:

```bash
robot template --template instruments-template.tsv \
  --input ontology.ttl \
  --output ontology.ttl
```

### ROBOT Template Pitfalls

These issues are learned through experience and not well-documented:

- **Column header syntax is fragile**: The second row defines semantics
  (e.g., `SC %`, `A rdfs:label`). A typo or extra space causes silent
  failures, not errors. Double-check headers before running.
- **The `%` placeholder in expressions**: `SC 'has part' some %` must have
  exact quoting and spacing. This is where most template errors occur.
- **Merge vs replace**: `--merge-before` and `--merge-after` control whether
  template output merges with the input or replaces it. Getting this wrong
  can delete your entire ontology. Default behavior is merge.
- **IRI resolution**: Template values must be full IRIs or CURIEs that
  resolve via the ontology's prefix declarations. Undeclared prefixes
  produce blank or invalid output with no error.
- **Multi-value columns**: To put multiple superclasses or annotations on
  one term, use `SPLIT=|` in the column header. Not obvious from docs.
- **Empty cells skip silently**: Empty cells in required columns skip the
  row rather than raising an error. Terms can be partially created (label
  but no definition).
- **Language tags**: Use `A rdfs:label@en` to add a language tag. Without
  it, labels are untagged string literals, causing issues with tools that
  filter by language.

**Pre-flight check**: Before running `robot template`, verify that all column
headers parse correctly and all CURIEs resolve against declared prefixes.

### Step 4: Individual Changes via KGCL

For single additions, modifications, or reparenting. **Important**: For
changes to shared ontologies, write KGCL commands to a `.kgcl` file and
present for review BEFORE applying (Safety Rule #5).

```bash
# Add a class
uv run runoak -i ontology.ttl apply "create class EX:0001 'piano'"

# Add subclass relationship
uv run runoak -i ontology.ttl apply "create edge EX:0001 rdfs:subClassOf EX:0000"

# Add definition
uv run runoak -i ontology.ttl apply "create definition 'A keyboard instrument that produces sound by striking strings' for EX:0001"

# Rename
uv run runoak -i ontology.ttl apply "rename EX:0001 from 'Old Name' to 'New Name'"

# Batch changes from file
uv run runoak -i ontology.ttl apply --changes-input changes.kgcl
```

### Step 5: Complex Axioms via OWLAPY or rdflib

When ROBOT templates and KGCL cannot express the needed axiom (qualified
cardinality, role chains, nested class expressions).

**Tool choice**: Most OBO community practitioners use **rdflib** for
programmatic OWL work in Python (triple-level manipulation). **OWLAPY**
provides a higher-level OWL API but has a smaller community and requires
a JVM. Use whichever fits your team's stack — examples of both follow.

OWLAPY example:

```python
from owlapy.model import (
    OWLClass, OWLObjectProperty,
    OWLSubClassOfAxiom, OWLObjectSomeValuesFrom,
    OWLObjectAllValuesFrom, OWLObjectIntersectionOf,
)
from owlapy.model import IRI
from owlapy.owlready2 import OWLOntologyManager_Owlready2

manager = OWLOntologyManager_Owlready2()
onto = manager.load_ontology(IRI.create("file:///path/to/ontology.owl"))

# Example: StringInstrument EquivalentTo Instrument and hasComponent some String
instrument = OWLClass(IRI.create("http://ex.org/#Instrument"))
string_cls = OWLClass(IRI.create("http://ex.org/#String"))
has_comp = OWLObjectProperty(IRI.create("http://ex.org/#hasComponent"))

restriction = OWLObjectSomeValuesFrom(has_comp, string_cls)
intersection = OWLObjectIntersectionOf([instrument, restriction])
# ... add as equivalent class axiom

manager.save_ontology(onto, IRI.create("file:///path/to/ontology.owl"))
```

rdflib alternative (no JVM required):

```python
from rdflib import Graph, Namespace, OWL, RDF, RDFS, URIRef, BNode
from rdflib.collection import Collection

g = Graph()
g.parse("ontology.ttl", format="turtle")

EX = Namespace("http://example.org/")

# Add existential restriction: StringInstrument SubClassOf hasComponent some String
restriction = BNode()
g.add((restriction, RDF.type, OWL.Restriction))
g.add((restriction, OWL.onProperty, EX.hasComponent))
g.add((restriction, OWL.someValuesFrom, EX.String))
g.add((EX.StringInstrument, RDFS.subClassOf, restriction))

g.serialize("ontology.ttl", format="turtle")
```

### Step 5.5: Individual Management

Handle individuals as A-box content with explicit module boundaries:

- Reference individuals (for example country codes, fixed enumerations) belong
  in a dedicated reference-individuals module.
- Test individuals belong in a separate test ontology/module.
- Production individuals belong in a knowledge graph dataset, not in the core
  ontology schema file.
- If reference individuals exceed about 50, split into a separate file and
  import it explicitly.

### Step 6: Schema-First via LinkML (for data model schemas)

LinkML excels at defining data schemas that generate multiple artifact types.
Use it when the primary deliverable is a **data model** (JSON Schema, SHACL,
Python dataclasses) rather than a **rich OWL ontology**.

**Best for**: ABox validation schemas, data exchange formats, projects where
domain experts review YAML rather than OWL.

**Not ideal for**: Rich TBox ontologies with complex axioms (qualified
cardinality, role chains, nested class expressions). LinkML-generated OWL
is relatively flat and typically needs enrichment with ROBOT or OWLAPY.

When starting from scratch with a schema-first approach:

```yaml
id: https://example.org/music-ontology
name: music-ontology
prefixes:
  linkml: https://w3id.org/linkml/
  music: https://example.org/music-ontology/

classes:
  Instrument:
    description: A device used to produce music
    attributes:
      name:
        range: string
        required: true
      instrument_family:
        range: InstrumentFamily
```

Generate artifacts:

```bash
uv run gen-owl schema.yaml > ontology.owl
uv run gen-shacl schema.yaml > shapes.ttl
uv run gen-python schema.yaml > models.py
```

### Step 7: Verify (after structural changes)

Reasoning strategy depends on context:

| Context | Reasoner | Frequency | Time Budget |
|---------|----------|-----------|-------------|
| Active development | ELK | After each batch of changes | Seconds (10K classes) |
| Pre-commit / CI | ELK | Every commit | < 2 minutes |
| Pre-release validation | HermiT or Pellet | Before each release | Minutes to hours |

**Important**: ELK only supports OWL 2 EL. If your ontology uses qualified
cardinality, universal restrictions, or class complements, ELK will silently
ignore those axioms. Run HermiT at least before releases to catch what ELK
misses.

```bash
# Fast classification (ELK — use during development and CI)
robot reason --reasoner ELK --input ontology.ttl --output classified.ttl

# Full DL classification (HermiT — use pre-release)
robot reason --reasoner HermiT --input ontology.ttl --output classified.ttl

# Quality report
robot report --input ontology.ttl --fail-on ERROR --output report.tsv

# SHACL validation (if shapes exist)
uv run pyshacl -s shapes/ontology-shapes.ttl -i rdfs ontology.ttl -f human
```

**Materialization decision**: The ODK default is to include inferred axioms
in the release file (`robot reason --output`). If consumers will reason
independently, ship asserted-only and document this in the release notes.

## Tool Commands

### ODK Awareness

If the project uses the Ontology Development Kit (ODK), understand these
conventions:

- **Edit file**: Work in `src/ontology/{name}-edit.owl` — never touch
  release artifacts directly
- **Makefile pipeline**: `sh run.sh make` runs the full build (merge,
  reason, report, release) reproducibly via Docker
- **Import management**: `src/ontology/imports/{source}_terms.txt` lists
  imported IRIs; `make refresh-imports` regenerates `*_import.owl` modules
- **DOSDP patterns**: YAML pattern files generate OWL from TSV data — more
  structured than raw ROBOT templates for pattern-based term creation
- **Release**: `make prepare_release` produces multi-format release artifacts

When working in a non-ODK project, the ROBOT commands below apply directly.

### ROBOT operations

```bash
# Merge imports
robot merge --input edit-ontology.ttl --input imports/*.owl --output merged.ttl

# Convert formats
robot convert --input ontology.ttl --output ontology.owl
robot convert --input ontology.ttl --output ontology.json --format json-ld

# Annotate with version
robot annotate --input ontology.ttl \
  --annotation owl:versionInfo "$(date +%Y-%m-%d)" \
  --output ontology.ttl
```

### oaklib operations

```bash
# Search before creating (always!)
uv run runoak -i sqlite:obo:bfo search "material entity"

# Get term info
uv run runoak -i ontology.ttl info EX:0001

# Visualize hierarchy
uv run runoak -i ontology.ttl tree --root EX:0000
```

## Outputs

This skill produces:

| Artifact | Location | Format | Description |
|----------|----------|--------|-------------|
| Main ontology | `ontologies/{name}/{name}.ttl` | Turtle | The formalized OWL 2 ontology |
| SHACL shapes | `ontologies/{name}/shapes/{name}-shapes.ttl` | Turtle | Structural validation shapes |
| ROBOT templates | `ontologies/{name}/{name}-template.tsv` | TSV | Templates used for term creation |
| KGCL patches | `ontologies/{name}/{name}-changes.kgcl` | KGCL | Applied change log |
| Quality report | `ontologies/{name}/{name}-report.tsv` | TSV | Latest ROBOT report |
| Reference individuals (optional) | `ontologies/{name}/{name}-reference-individuals.ttl` | Turtle | A-box reference instances kept separate from schema |

## Handoff

**Receives from**:
- `ontology-conceptualizer` — `ontologies/{name}/docs/glossary.csv`,
  `ontologies/{name}/docs/conceptual-model.yaml`, `ontologies/{name}/docs/bfo-alignment.md`,
  `ontologies/{name}/docs/property-design.yaml`, `ontologies/{name}/docs/axiom-plan.yaml`
- `ontology-requirements` (indirect, via pipeline) — `ontologies/{name}/tests/*.sparql`,
  `ontologies/{name}/tests/cq-test-manifest.yaml` (CQ test suite to forward to validator)

**Passes to**: `ontology-validator` — `ontologies/{name}/{name}.ttl`,
`ontologies/{name}/shapes/{name}-shapes.ttl`, `ontologies/{name}/tests/*.sparql`,
`ontologies/{name}/tests/cq-test-manifest.yaml`

**Handoff checklist**:
- [ ] Ontology passes `robot reason` with zero unsatisfiable classes
- [ ] Ontology passes `robot report` with zero ERRORs
- [ ] All glossary terms are present in the ontology
- [ ] All axiom plan entries have been implemented
- [ ] SHACL shapes exist for core structural constraints

## Anti-Patterns to Avoid

- **Hand-editing Turtle**: Never manually edit `.ttl` files. Use ROBOT,
  oaklib, or Python tools. (Safety Rule #1)
- **Skipping the reasoner**: Always run `robot reason` after structural
  changes. (Safety Rule #2)
- **Deleting terms**: Never delete — deprecate with `owl:deprecated true`.
  (Safety Rule #4)
- **Over-engineering tools**: Don't use OWLAPY for simple SubClassOf. Use
  ROBOT template or KGCL instead. (See tool decision tree)
- **Missing metadata**: Every class needs `rdfs:label` and `skos:definition`
  at minimum.
- **Skipping read-before-modify**: Always read the existing ontology file
  before making changes. (Safety Rule #9)
- **No backup before bulk**: Create a checkpoint before running ROBOT
  template or batch KGCL application. (Safety Rule #10)

## Error Handling

| Error | Likely Cause | Recovery |
|-------|-------------|----------|
| Reasoner reports INCONSISTENT | Conflicting axioms (often disjointness + subclass) | Parse explanation, identify conflicting axioms, propose minimal fix |
| Unsatisfiable classes found | Over-constrained class (contradictory restrictions) | List unsatisfiable classes, trace disjointness axioms |
| ROBOT template fails | Column headers don't match expected format | Check ROBOT template documentation for column syntax |
| KGCL apply fails | Term not found or invalid KGCL syntax | Verify term exists with `runoak info`; check KGCL grammar |
| OWLAPY JVM bridge error | Java not installed or JVM not found | Ensure JDK is installed and JAVA_HOME is set |

```


### `.claude/skills/ontology-mapper/SKILL.md` — ontology-mapper skill

```markdown
---
name: ontology-mapper
description: >
  Manages cross-ontology mapping and alignment. Generates, validates, and
  maintains SSSOM mapping sets. Runs lexical matching via oaklib and
  LLM-assisted verification. Use when working with ontology mappings,
  alignment, or cross-references.
---

# Ontology Mapper

## Role Statement

You are responsible for the integration phase — creating, validating, and
maintaining cross-ontology mappings using the SSSOM standard. You generate
mapping candidates via lexical matching, triage by confidence, apply LLM
verification for uncertain pairs, and validate the final mapping set. You
produce SSSOM TSV files and quality reports. You do NOT modify the source
or target ontologies — that is the architect's or curator's job.

## When to Activate

- User mentions "mapping", "alignment", "cross-reference", or "SSSOM"
- User wants to connect two ontologies
- User wants to validate or update existing mappings
- Pipeline B

## Shared Reference Materials

Read these files from `_shared/` before beginning work:

- `_shared/methodology-backbone.md` — lifecycle phase context (Phase 5: Integration)
- `_shared/namespaces.json` — canonical prefixes including sssom and semapv
- `_shared/naming-conventions.md` — to understand label standards for matching

## Core Workflow

### Step 1: Candidate Generation (Lexical Matching)

```bash
# Using oaklib lexmatch
uv run runoak -i sqlite:obo:{source} lexmatch \
  --add sqlite:obo:{target} \
  -o ontologies/{name}/mappings/{source}-to-{target}.sssom.tsv
```

With custom match rules:

```yaml
# lexmatch-rules.yaml
rules:
  - match_fields: [rdfs:label, oio:hasExactSynonym]
    predicate: skos:exactMatch
    weight: 0.9
  - match_fields: [rdfs:label, oio:hasRelatedSynonym]
    predicate: skos:closeMatch
    weight: 0.7
```

```bash
uv run runoak -i sqlite:obo:{source} lexmatch \
  --add sqlite:obo:{target} \
  --rules-file lexmatch-rules.yaml \
  -o ontologies/{name}/mappings/{source}-to-{target}.sssom.tsv
```

### Step 2: Confidence Triage

**Practitioner warning**: Lexical matching at the 0.7-0.95 confidence level
produces 40-60% false positives in practice. Labels match but meanings differ
(homonyms across domains). The LLM verification step is not optional — it is
essential for this tier.

Sort candidates into three tiers:

| Tier | Confidence | Action |
|------|-----------|--------|
| Auto-accept | ≥ 0.98 AND exact label match AND compatible parent classes | Accept with `semapv:LexicalMatching` justification |
| LLM-verify | 0.7 – 0.98 | Present to LLM for semantic evaluation |
| Human queue | < 0.7 | Flag for manual expert review |

### Step 3: LLM Verification (for uncertain mappings)

For each uncertain pair, evaluate:

```
Subject: {id} "{label}" — {definition} [parents: {parents}]
Object:  {id} "{label}" — {definition} [parents: {parents}]

Determine:
- predicate: exactMatch / closeMatch / broadMatch / narrowMatch /
             relatedMatch / no_match
- confidence: 0.0 – 1.0
- justification: reasoning for the decision
```

Update the SSSOM file with LLM-verified results, using
`semapv:SemanticSimilarityThresholdMatching` as the mapping justification.

### Step 4: Mapping Predicate Selection

Apply the predicate decision guide:

```
Logically equivalent with formal proof? → owl:equivalentClass
High-confidence equivalence?            → skos:exactMatch
Subject more general than object?       → skos:broadMatch
Subject more specific than object?      → skos:narrowMatch
Similar but not fully interchangeable?  → skos:closeMatch
Merely associated?                      → skos:relatedMatch
```

**Critical**: `skos:exactMatch` is TRANSITIVE. Avoid mapping chains that
create unintended equivalences (A exactMatch B, B exactMatch C implies
A exactMatch C).

**Critical**: Treat `owl:sameAs` as a last-resort identity assertion only when
true identity is proven. One incorrect `owl:sameAs` can trigger transitive
merges across multiple graphs and collapse distinct entities.

### Step 5: Validate

```bash
# Validate SSSOM schema conformance
uv run sssom validate ontologies/{name}/mappings/{source}-to-{target}.sssom.tsv
```

Check:
- Schema conformance (valid SSSOM TSV)
- CURIE resolution (all prefixes in curie_map)
- Entity existence (subjects/objects exist in source/target)
- Predicate consistency (no contradictory predicates for same pair)
- No self-mappings (subject ≠ object)
- No duplicate mappings

### Step 5.5: Clique Analysis (mandatory for exactMatch)

After validation, compute the transitive closure of `skos:exactMatch` and
flag any clique larger than 3 terms for human review. One bad exactMatch
link contaminates an entire clique.

```sparql
# Inline clique detection: find terms reachable via exactMatch chains > 3
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?start ?mid ?end WHERE {
  ?start skos:exactMatch+ ?mid .
  ?mid skos:exactMatch+ ?end .
  FILTER(?start != ?end)
}
```

```bash
# Run against the mapping file (convert SSSOM to RDF first if needed)
robot query --input ontologies/{name}/mappings/{source}-to-{target}.sssom.ttl \
  --query sparql/clique-check.sparql --output clique-report.csv
```

For cross-domain mappings (source and target are in different domains),
default to `skos:relatedMatch` or `skos:closeMatch`, not `skos:exactMatch`.

### Step 6: Quality Report

Generate a quality assessment:

- Predicate distribution (how many of each type)
- Confidence distribution (histogram)
- Source coverage (% of source terms mapped)
- Target coverage (% of target terms mapped)
- Potential conflicts (same subject mapped to multiple objects with
  exactMatch)
- Clique analysis (transitive closure of exactMatch — flag cliques > 3)

## Tool Commands

### SSSOM operations

```bash
# Validate
uv run sssom validate ontologies/{name}/mappings/file.sssom.tsv

# Merge mapping sets
uv run sssom merge \
  set1.sssom.tsv set2.sssom.tsv \
  -o merged.sssom.tsv

# Deduplicate
uv run sssom dedupe merged.sssom.tsv -o final.sssom.tsv

# Convert to OWL (bridge ontology)
uv run sssom convert ontologies/{name}/mappings/file.sssom.tsv -o bridge.owl -O owl
```

Before publishing bridge ontologies, review any generated identity axioms:
- Confirm whether conversion introduced `owl:sameAs` assertions.
- Downgrade uncertain links to SKOS predicates before release.

### Updating mappings for new ontology version

```bash
# Find obsoleted terms in target
uv run runoak -i sqlite:obo:{target} query \
  "PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT ?term WHERE { ?term owl:deprecated true }"

# Generate replacement KGCL
# For each obsoleted target with a replacement:
# delete mapping {subject} {predicate} {obsolete_target}
# create mapping {subject} {predicate} {replacement_target}
```

## Outputs

This skill produces:

| Artifact | Location | Format | Description |
|----------|----------|--------|-------------|
| Mapping file | `ontologies/{name}/mappings/{source}-to-{target}.sssom.tsv` | SSSOM TSV | Complete mapping set with metadata |
| Quality report | `ontologies/{name}/mappings/{source}-to-{target}-qa.md` | Markdown | Quality assessment with statistics |
| Human review queue | `ontologies/{name}/mappings/{source}-to-{target}-review.tsv` | TSV | Low-confidence pairs for expert review |
| KGCL changes | `ontologies/{name}/mappings/{source}-to-{target}-changes.kgcl` | KGCL | Mapping update changes |
| Bridge ontology | `ontologies/{name}/mappings/{source}-to-{target}-bridge.owl` | OWL/XML | OWL axioms from mappings (optional) |

## Handoff

**Receives from**: `ontology-scout` — target ontology identifiers,
reuse recommendations

**Passes to**: `ontology-validator` — `ontologies/{name}/mappings/*.sssom.tsv`

**Handoff checklist**:
- [ ] SSSOM file passes `sssom validate`
- [ ] All CURIEs resolve via curie_map
- [ ] Every mapping has a `mapping_justification` (SEMAPV term)
- [ ] Confidence scores present for all automated mappings
- [ ] Quality report generated and reviewed

## SSSOM File Requirements

Every SSSOM file must include in its YAML header:

```yaml
curie_map:
  # All prefixes used in subject_id and object_id
mapping_set_id: https://example.org/mappings/{source}-to-{target}
license: https://creativecommons.org/licenses/by/4.0/
subject_source: {source ontology IRI}
object_source: {target ontology IRI}
```

Every mapping row must include:
- `subject_id`, `subject_label`
- `predicate_id`
- `object_id`, `object_label`
- `mapping_justification` (SEMAPV term)
- `confidence` (for automated mappings)

## Anti-Patterns to Avoid

- **Mapping without context**: Don't match by label alone. Consider
  definitions, parent classes, and domain context.
- **exactMatch overuse**: Default to `closeMatch` when unsure. Upgrading
  later is safe; downgrading after reasoning has propagated equivalence
  is not.
- **sameAs overuse**: Never use `owl:sameAs` for "close enough" mappings.
  Reserve it for strict identity only.
- **Ignoring transitivity**: `skos:exactMatch` is transitive. Check that
  chains don't create unintended equivalences.
- **Missing justification**: Every mapping needs a SEMAPV justification.
  `semapv:LexicalMatching`, `semapv:ManualMappingCuration`,
  `semapv:SemanticSimilarityThresholdMatching`.
- **Stale mappings**: When source or target ontology is updated, mappings
  must be rechecked for obsoleted terms.

## Error Handling

| Error | Likely Cause | Recovery |
|-------|-------------|----------|
| `sssom validate` fails | Missing required fields or invalid CURIEs | Fix curie_map, add missing justifications |
| Lexmatch produces no candidates | Vocabularies use different naming conventions | Try synonym matching, broaden match rules |
| Transitive closure creates false equivalences | Over-use of exactMatch | Downgrade to closeMatch for uncertain pairs |
| Target term is obsoleted | Target ontology was updated | Find replacement via `obo:IAO_0100001` property |

```


### `.claude/skills/ontology-validator/SKILL.md` — ontology-validator skill

```markdown
---
name: ontology-validator
description: >
  Comprehensive ontology validation and quality assurance. Runs OWL
  reasoners, SHACL validation, CQ test suites, and ROBOT quality reports.
  Computes quality metrics and generates diff reports. Use when checking
  ontology quality or before committing changes.
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

```


### `.claude/skills/ontology-curator/SKILL.md` — ontology-curator skill

```markdown
---
name: ontology-curator
description: >
  Manages ontology maintenance, evolution, and versioning. Handles term
  deprecation, KGCL change management, diff generation, and release
  workflows. Use when maintaining, updating, versioning, or documenting
  an existing ontology.
---

# Ontology Curator

## Role Statement

You are responsible for the maintenance and evolution phase — managing
ongoing changes to existing ontologies. You handle deprecation (never
deletion), structural changes via KGCL, version management, diff
generation, and release pipelines. You ensure all changes are auditable,
reviewable, and validated before merging.

## When to Activate

- User mentions "deprecate", "version", "release", "maintain"
  (Note: "obsolete" is the KGCL command name, but the canonical term
  for the action is "deprecate" per CONVENTIONS.md)
- User wants to rename, reparent, or restructure existing terms
- User wants to generate changelogs or documentation
- Pipeline C

## Shared Reference Materials

Read these files from `_shared/` before beginning work:

- `_shared/methodology-backbone.md` — lifecycle context (Maintenance phase)
- `_shared/tool-decision-tree.md` — tool selection for changes
- `_shared/naming-conventions.md` — naming standards for renames
- `_shared/quality-checklist.md` — validation requirements after changes
- `_shared/namespaces.json` — canonical prefixes

## Core Workflow

### Step 1: Analyze Change Request

Classify the requested change:

| Change Type | KGCL Command | Severity |
|-------------|-------------|----------|
| Rename label | `rename` | PATCH |
| Add synonym | `create synonym` | PATCH |
| Fix definition | `change definition` | PATCH |
| Reparent class | `move` | MINOR |
| Add new class | `create class` + `create edge` | MINOR |
| Deprecate term | `obsolete` | MINOR |
| Remove axiom | `delete edge` | MAJOR (review required) |
| Change semantics | Multiple commands | MAJOR (review required) |

### Step 2: Generate KGCL Patch

Compose KGCL commands for the change:

```bash
# Deprecation (NEVER delete — always deprecate)
uv run runoak -i ontology.ttl apply "obsolete EX:0042"
uv run runoak -i ontology.ttl apply \
  "create synonym 'OBSOLETE old term name' for EX:0042"

# Add replacement pointer
uv run runoak -i ontology.ttl apply \
  "create edge EX:0042 obo:IAO_0100001 EX:0099"
```

Required deprecation metadata:
- `owl:deprecated true`
- `obo:IAO_0000231` (has obsolescence reason)
- `obo:IAO_0100001` (term replaced by)

### Step 3: Propose Patch for Review

Write the KGCL patch file and present to user BEFORE applying:

```kgcl
# changes.kgcl — Proposed changes for review
# Date: {date}
# Author: {agent}
# Reason: {description of why these changes are needed}

obsolete EX:0042
create synonym 'OBSOLETE Widget' for EX:0042
create edge EX:0042 obo:IAO_0100001 EX:0099

rename EX:0001 from 'Old Name' to 'New Name'
move EX:0010 from EX:0001 to EX:0002
```

### Step 4: Apply Approved Changes

```bash
# Apply batch changes
uv run runoak -i ontology.ttl apply --changes-input changes.kgcl

# Or apply individual changes
uv run runoak -i ontology.ttl apply "rename EX:0001 from 'Old' to 'New'"
```

### Step 5: Version Update

Update the ontology header:

```turtle
<http://example.org/onto> a owl:Ontology ;
    owl:versionIRI <http://example.org/onto/2024-06-01> ;
    owl:versionInfo "2024-06-01" ;
    owl:priorVersion <http://example.org/onto/2024-03-01> .
```

Versioning rules (choose one scheme per project):

**OBO date-based versioning** (preferred for OBO Foundry ontologies):
- Format: `YYYY-MM-DD` (e.g., `2024-06-01`)
- Stable PURL resolves to latest release
- Versioned IRI: `http://purl.obolibrary.org/obo/{name}/2024-06-01/{name}.owl`

**Semantic versioning** (for project-specific ontologies):
- **MAJOR**: Backward-incompatible changes (removing axioms, changing
  semantics of existing terms)
- **MINOR**: Backward-compatible additions (new classes/properties)
- **PATCH**: Backward-compatible fixes (label corrections, definition
  improvements, synonym additions)

### Step 5.5: FAIR Assessment

Assess release readiness against FAIR sub-principles and record outcomes in
the release notes.

| Principle | Ontology Action | Tool/Vocabulary |
|----------|------------------|-----------------|
| F1 | Assign stable globally unique ontology and term IRIs | IRI policy, `owl:versionIRI` |
| F2 | Ensure rich metadata on ontology header and key terms | `dcterms:*`, `skos:*` |
| F3 | Include metadata that references released artifact identifiers | `dcterms:identifier`, version IRI |
| F4 | Register/index ontology in searchable resources | OBO Foundry, BioPortal, OLS |
| A1 | Publish via open, standardized retrieval protocol | HTTPS, content negotiation |
| A1.1 | Keep protocol open and implementable | HTTP/HTTPS |
| A1.2 | Support auth where needed without breaking protocol | token-based repository APIs |
| A2 | Preserve metadata availability across versions | versioned metadata files |
| I1 | Use formal, shared KR language | RDF/OWL |
| I2 | Use FAIR vocabularies where possible | DCMI, SKOS, PROV-O, OBO/RO |
| I3 | Include qualified links to related resources | `dcterms:references`, mapping predicates |
| R1 | Provide rich provenance and context metadata | `prov:*`, `dcterms:*` |
| R1.1 | Publish explicit usage license | `dcterms:license` |
| R1.2 | Record provenance of terms and releases | `prov:wasDerivedFrom`, changelog |
| R1.3 | Follow community standards | OBO principles, SSSOM for mappings |

#### Release Publishing

- Publish dereferenceable ontology IRIs with content negotiation (Turtle,
  RDF/XML, JSON-LD as needed).
- Register releases in relevant repositories (for example OBO Foundry,
  BioPortal, OLS) when applicable.
- Publish diffs/changelog between releases, not just latest snapshot.

### Step 6: Generate Diff

```bash
robot diff --left previous.ttl --right ontology.ttl \
  --format markdown --output CHANGELOG.md
```

### Step 7: Validate

Hand off to `ontology-validator` for full validation, or run quick checks:

```bash
robot reason --reasoner ELK --input ontology.ttl
robot report --input ontology.ttl --fail-on ERROR
```

## Tool Commands

### KGCL operations via oaklib

```bash
# Rename
uv run runoak -i onto.ttl apply "rename EX:0001 from 'Old Name' to 'New Name'"

# Reparent
uv run runoak -i onto.ttl apply "move EX:0010 from EX:0001 to EX:0002"

# Add synonym
uv run runoak -i onto.ttl apply "create synonym 'Alternative Name' for EX:0001"

# Change definition
uv run runoak -i onto.ttl apply \
  "change definition of EX:0001 to 'Updated definition here'"

# Deprecate
uv run runoak -i onto.ttl apply "obsolete EX:0042"
```

### Release pipeline

```bash
# Full release pipeline
robot merge --input edit-ontology.ttl \
  --input imports/*.owl \
  --output merged.ttl && \
robot reason --reasoner ELK --input merged.ttl --output reasoned.ttl && \
robot report --input reasoned.ttl --fail-on ERROR && \
robot annotate --input reasoned.ttl \
  --annotation owl:versionInfo "$(date +%Y-%m-%d)" \
  --output release/ontology.ttl && \
robot convert --input release/ontology.ttl --output release/ontology.owl && \
robot convert --input release/ontology.ttl --output release/ontology.json \
  --format json-ld
```

### Import refresh

When upstream ontologies release new versions:

```bash
# Check for obsoleted terms and re-extract each import
for f in imports/*_terms.txt; do
  ontology=$(basename "$f" _terms.txt)

  # Check for stale terms
  while IFS= read -r iri; do
    uv run runoak -i "sqlite:obo:${ontology}" info "$iri" 2>/dev/null | \
      grep -q "OBSOLETE" && echo "STALE: $iri in $f"
  done < "$f"

  # Re-extract this import module
  robot extract --method MIREOT \
    --input-iri "http://purl.obolibrary.org/obo/${ontology}.owl" \
    --term-file "imports/${ontology}_terms.txt" \
    --output "imports/${ontology}_import.owl"
done
```

### Diff operations

```bash
# Markdown diff for PR descriptions
robot diff --left old.ttl --right new.ttl --format markdown

# Plain text diff
robot diff --left old.ttl --right new.ttl
```

## Outputs

This skill produces:

| Artifact | Location | Format | Description |
|----------|----------|--------|-------------|
| KGCL patch | `{name}-changes.kgcl` | KGCL | Human-reviewable change proposals |
| Updated ontology | `ontologies/{name}/{name}.ttl` | Turtle | Ontology with applied changes |
| Diff report | `CHANGELOG.md` | Markdown | Changes between versions |
| Release artifacts | `release/` | TTL, OWL, JSON-LD | Multi-format release files |
| FAIR assessment notes | `release/{name}-fair.md` | Markdown | FAIR principle checks per release |

## Handoff

**Receives from**: User (change requests, deprecation needs, release triggers)

**Passes to**: `ontology-validator` — modified `ontology.ttl`, KGCL change log

**Handoff checklist**:
- [ ] KGCL patch was reviewed and approved by user before applying
- [ ] Deprecations include all required metadata (deprecated flag,
  obsolescence reason, replacement pointer)
- [ ] Version IRI and version info are updated
- [ ] Diff report is generated
- [ ] Changes are ready for validation

## Anti-Patterns to Avoid

- **Deleting terms**: NEVER delete an ontology term. Always deprecate with
  `owl:deprecated true` and provide a replacement pointer. (Safety Rule #4)
- **Silent changes**: ALWAYS propose KGCL patches for review before applying
  to shared ontologies. (Safety Rule #5)
- **Skipping version update**: Every change to a released ontology must
  increment the version.
- **Incomplete deprecation**: Deprecation requires three pieces: the
  deprecated flag, the obsolescence reason, and the replacement pointer.
  Missing any one leaves consumers without migration guidance.
- **Breaking changes without MAJOR version**: Removing axioms or changing
  term semantics requires a MAJOR version bump and explicit communication.
- **Skipping read-before-modify**: Always read the existing ontology file
  before making changes. (Safety Rule #9)
- **No backup before bulk**: Create a checkpoint before batch KGCL
  application. (Safety Rule #10)

## Error Handling

| Error | Likely Cause | Recovery |
|-------|-------------|----------|
| KGCL apply fails | Term not found | Verify term exists with `runoak info EX:XXXX` |
| oaklib cannot parse ontology | Malformed Turtle | Run `robot validate` to find syntax errors |
| Reasoner fails after changes | Change introduced inconsistency | Review KGCL patch; revert problematic change |
| No replacement term for deprecation | Gap in the ontology | Create the replacement term first (via architect), then deprecate |

```


### `.claude/skills/sparql-expert/SKILL.md` — sparql-expert skill

```markdown
---
name: sparql-expert
description: >
  Expert system for SPARQL 1.1 and SPARQL-star query generation,
  validation, and execution. Handles differences between GraphDB,
  Stardog, Fuseki, and local rdflib graphs. Use when querying
  knowledge graphs or debugging SPARQL.
---

# SPARQL Expert

## Role Statement

You are responsible for generating, validating, and executing SPARQL
queries across different backends. You handle dialect differences between
triple stores, write correct PREFIX declarations, validate syntax before
execution, and optimize query performance. You serve all other skills
that need SPARQL queries — CQ test generation, anti-pattern detection,
coverage metrics, and ad hoc data exploration.

## When to Activate

- User mentions "SPARQL", "query", or "knowledge graph"
- User wants to extract data from an ontology or triple store
- User wants to debug or optimize a SPARQL query
- Another skill needs a SPARQL query generated or executed

## Shared Reference Materials

Read these files from `_shared/` before beginning work:

- `_shared/namespaces.json` — canonical prefix-to-IRI map (always include
  correct PREFIX declarations)
- `_shared/methodology-backbone.md` — lifecycle context (cross-cutting)

## Core Workflow

### Step 1: Analyze Intent

Determine:
- **Query type**: SELECT, CONSTRUCT, ASK, DESCRIBE
- **Target**: Local file (ROBOT/rdflib), SPARQL endpoint, or oaklib adapter
- **Purpose**: Exploration, testing, reporting, or data extraction
- **Constraints**: Result size limits, performance requirements

### Step 2: Schema Lookup

Before writing the query:
1. Read `_shared/namespaces.json` for correct prefixes
2. If targeting an endpoint, check available named graphs
3. If querying a specific ontology, check its class/property structure

### Step 3: Draft Query

Rules:
- ALWAYS include PREFIX declarations for every prefix used
- Use `LIMIT` for exploratory queries (default: 100)
- Add comments for complex patterns
- Use `FILTER(!isBlank(?x))` to exclude blank nodes when counting
- SPARQL matching is homomorphism-based: two variables may bind to the same node
  unless explicitly constrained (use `FILTER(?x != ?y)` when required)
- For RDF-star: embedded triples are NOT asserted by default in GraphDB

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

# Purpose: {what this query does}
SELECT ?class ?label ?definition
WHERE {
  ?class a owl:Class ;
         rdfs:label ?label .
  OPTIONAL { ?class skos:definition ?definition }
  FILTER(!isBlank(?class))
}
ORDER BY ?label
LIMIT 100
```

### Step 4: Validate Syntax

```bash
# Validate via rdflib parser
uv run python -c "
from rdflib.plugins.sparql import prepareQuery
q = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?s WHERE { ?s rdf:type owl:Class }
'''
prepareQuery(q)
print('Valid SPARQL')
"
```

### Step 5: Execute

```bash
# Via ROBOT (local ontology files)
robot query --input ontology.ttl --query query.sparql --output output.csv

# Via oaklib
uv run runoak -i sqlite:obo:hp query \
  "SELECT ?x ?label WHERE { ?x rdfs:label ?label } LIMIT 10"

# Via rdflib (Python)
uv run python -c "
from rdflib import Graph
g = Graph()
g.parse('ontology.ttl', format='turtle')
results = g.query(open('query.sparql').read())
for row in results:
    print(row)
"
```

## Tool Commands

### Common query patterns

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

# List all classes with labels
SELECT ?class ?label WHERE {
  ?class a owl:Class ; rdfs:label ?label .
  FILTER(!isBlank(?class))
}

# Count classes
SELECT (COUNT(DISTINCT ?class) AS ?count) WHERE {
  ?class a owl:Class .
  FILTER(!isBlank(?class))
}

# Find subclasses of a specific class
SELECT ?sub ?label WHERE {
  ?sub rdfs:subClassOf :ParentClass ;
       rdfs:label ?label .
}

# Find classes missing definitions
SELECT ?class ?label WHERE {
  ?class a owl:Class ; rdfs:label ?label .
  FILTER NOT EXISTS { ?class skos:definition ?def }
  FILTER NOT EXISTS { ?class obo:IAO_0000115 ?def }
  FILTER(!isBlank(?class))
}

# Property usage statistics
SELECT ?prop (COUNT(*) AS ?usage) WHERE {
  ?s ?prop ?o .
  ?prop a owl:ObjectProperty .
}
GROUP BY ?prop
ORDER BY DESC(?usage)
```

### Property Path Reference

| Pattern | Meaning | Example |
|---------|---------|---------|
| `*` | Zero or more hops | `?x rdfs:subClassOf* ?y` |
| `+` | One or more hops | `?x rdfs:subClassOf+ ?y` |
| `|` | Alternative path | `?x (skos:exactMatch|skos:closeMatch) ?y` |
| `^` | Inverse property | `?x ^rdfs:subClassOf ?parent` |
| `/` | Concatenation | `?x rdfs:subClassOf/rdfs:subClassOf ?gparent` |

Common caution points:
- Property paths over cyclic graphs can explode result sizes.
- Add selective anchors and `LIMIT` when exploring transitive paths.
- Prefer bounded patterns for production queries when possible.

### RDF-star patterns

```sparql
# GraphDB: match asserted triple with metadata
SELECT ?s ?p ?o ?metaValue WHERE {
  ?s ?p ?o .
  << ?s ?p ?o >> :hasConfidence ?metaValue .
}

# Stardog: edge properties (if enabled)
SELECT ?s ?p ?o ?conf WHERE {
  ?s ?p ?o .
  << ?s ?p ?o >> :confidence ?conf .
}
```

### Federated queries

```sparql
# Query across multiple endpoints
SELECT ?local ?external WHERE {
  ?local a :LocalClass .
  SERVICE <http://dbpedia.org/sparql> {
    ?external a dbo:Thing ;
              rdfs:label ?label .
  }
}
```

## Entailment Regime Awareness

Query results depend on whether inference is applied:

- Local/raw file queries typically return only asserted triples.
- Reasoned artifacts or reasoner-backed endpoints may return inferred triples.
- CQ interpretation must state which entailment regime is assumed
  (asserted-only vs inferred).

## Outputs

This skill produces:

| Artifact | Location | Format | Description |
|----------|----------|--------|-------------|
| Query files | `sparql/{name}.sparql` | SPARQL | Stored, validated queries |
| Query results | `{context-dependent}` | CSV/TSV/JSON | Query output |

## Handoff

**Receives from**: Any skill that needs SPARQL queries generated or executed

**Passes to**: Requesting skill (query files and/or results)

**Handoff checklist**:
- [ ] Query syntax is validated
- [ ] PREFIX declarations are complete and correct
- [ ] Results are in the requested format
- [ ] Query is saved to `sparql/` if reusable

## Performance Tips

- Always use `LIMIT` for exploratory queries
- Avoid leading wildcards in `FILTER regex` (`regex(?var, ".*pattern")`) —
  they prevent index usage
- Use property paths (`rdfs:subClassOf+`) sparingly on large graphs
- Check `OPTIONAL` patterns for Cartesian products
- Prefer `FILTER EXISTS` / `FILTER NOT EXISTS` over subqueries
- Use `VALUES` clause for parameterized queries
- Place most selective triple patterns first in the WHERE clause

## Anti-Patterns to Avoid

- **Missing PREFIXes**: Every CURIE must have a corresponding PREFIX
  declaration. Use `_shared/namespaces.json` as the source.
- **No LIMIT on exploration**: Always limit exploratory queries. An
  unbounded SELECT against a large graph can timeout or crash.
- **SPARQL UPDATE on production**: Never execute UPDATE/DELETE against
  production endpoints. (Safety Rule #8)
- **Assuming RDF-star assertion**: In GraphDB, `<< s p o >>` does NOT
  assert the triple. You must also state `s p o .` separately.
- **Ignoring blank nodes**: Always filter blank nodes when counting or
  listing named entities.
- **Assuming variable distinctness**: SPARQL can bind `?x` and `?y` to the
  same node. Add `FILTER(?x != ?y)` when distinct entities are required.
- **Ignoring entailment regime**: A query that works on materialized endpoint
  results may fail on asserted-only local files.

## Error Handling

| Error | Likely Cause | Recovery |
|-------|-------------|----------|
| Parse error | Syntax error in SPARQL | Run through validator; check missing PREFIXes or braces |
| Timeout | Query too complex or graph too large | Add LIMIT, rewrite with more selective patterns |
| Empty results | Wrong prefix IRI or term not in graph | Verify prefix resolves correctly; check term existence |
| 403 Forbidden | Endpoint requires authentication | Check credentials configuration |
| RDF-star syntax error | Store doesn't support RDF-star | Check store capabilities; fall back to standard reification |

```


---

# Appendix B: Shared Reference Materials (Verbatim)


### `.claude/skills/_shared/methodology-backbone.md` — Lifecycle phase mapping and pipelines

```markdown
# Methodology Backbone

How the 8 ontology skills map to established ontology engineering lifecycle
phases. Every skill operates within this shared framework.

## Methodology Foundations

This workspace synthesizes four complementary methodologies:

- **METHONTOLOGY** (Fernandez-Lopez et al., 1997) — structured lifecycle with
  explicit activities: specification, knowledge acquisition, conceptualization,
  formalization, integration, implementation, evaluation, maintenance
- **NeOn Methodology** (Suarez-Figueroa et al., 2012) — scenario-based,
  emphasizes reuse, collaboration, and modular development
- **CQ-Driven Development** (Gruninger & Fox, 1995) — competency questions as
  acceptance criteria, formalized as SPARQL tests (Test-Driven Ontology
  Development, TDOD)
- **Kendall & McGuinness Lifecycle** (Ontology Engineering, section 7.3) —
  emphasizes phased term extraction, use case development, and explicit review

## K&M Phase Mapping

How K&M's 9-phase workflow maps onto this workspace's lifecycle:

| K&M Phase | Workspace Mapping |
|----------|-------------------|
| 1. Preparatory | Phase 1: Specification |
| 2. Initial term excerption | Phase 2: Knowledge Acquisition |
| 3. Business architecture | Phase 3: Conceptualization |
| 4. Subsequent term excerption | Phase 2 (iterative revisit) |
| 5. Use case development | Phase 1 (requirements refinement) |
| 6. Term curation | Phase 3: Conceptualization |
| 7. Ontology development | Phase 4: Formalization & Implementation |
| 8. Review | Phase 6: Evaluation |
| 9. Deployment | Cross-cutting release/maintenance workflow |

## Lifecycle Phases and Skill Mapping

```
Phase 1: SPECIFICATION
  └── ontology-requirements
        Elicit competency questions, define scope, produce ORSD

Phase 2: KNOWLEDGE ACQUISITION & REUSE
  └── ontology-scout
        Search registries, evaluate existing ontologies, extract modules

Phase 3: CONCEPTUALIZATION
  └── ontology-conceptualizer
        Build glossary, design taxonomy, align to BFO, select axiom patterns

Phase 4: FORMALIZATION & IMPLEMENTATION
  └── ontology-architect
        Encode OWL 2 axioms via ROBOT templates, KGCL, OWLAPY, LinkML

Phase 5: INTEGRATION & MAPPING
  └── ontology-mapper
        Create SSSOM mappings, lexmatch, LLM verification, bridge ontologies

Phase 6: EVALUATION
  └── ontology-validator
        Reasoner, SHACL, ROBOT report, CQ test suites

Cross-Cutting: QUERYING
  └── sparql-expert
        SPARQL generation, validation, execution across backends

Cross-Cutting: MAINTENANCE & EVOLUTION
  └── ontology-curator
        Deprecation, KGCL changes, versioning, releases
```

## Pipelines

Skills compose into three primary pipelines:

### Pipeline A — New Ontology (full lifecycle)

```
requirements → scout → conceptualizer → architect → validator
```

1. **requirements** produces: CQs, ORSD, pre-glossary, scope definition
2. **scout** consumes pre-glossary, produces: reuse report, import term lists,
   ODP recommendations
3. **conceptualizer** consumes CQs + reuse report, produces: glossary,
   conceptual model, BFO alignment, axiom plan
4. **architect** consumes approved conceptual model, produces: ontology files
   (.ttl), SHACL shapes
5. **validator** consumes ontology + shapes + CQ tests, produces: validation
   report (pass/fail)

### Pipeline B — Mapping

```
scout → mapper → validator
```

1. **scout** identifies target ontologies for alignment
2. **mapper** generates SSSOM mappings via lexmatch + LLM verification
3. **validator** validates mapping file and checks logical consistency

### Pipeline C — Evolution

```
curator → validator
```

1. **curator** proposes KGCL changes (deprecations, renames, restructuring)
2. **validator** verifies changes maintain consistency

## The CQ Through-Line

Competency questions are the connective tissue across all phases:

| Phase | CQ Role |
|-------|---------|
| Specification | CQs are elicited and prioritized |
| Knowledge Acquisition | CQs guide what to look for in existing ontologies |
| Conceptualization | CQs determine what classes and relations are needed |
| Formalization | CQ SPARQL drafts (from Specification) guide axiom implementation |
| Evaluation | CQ-SPARQL tests serve as acceptance criteria |
| Maintenance | New CQs trigger evolution; deprecated CQs are retired |

## Phase Boundaries

Each phase has explicit entry and exit criteria:

| Phase | Entry Condition | Exit Condition |
|-------|----------------|----------------|
| Specification | User request or domain need | ORSD approved, CQs prioritized |
| Knowledge Acquisition | Pre-glossary available | Reuse report complete |
| Conceptualization | CQs + reuse findings | Conceptual model approved by user |
| Formalization | Approved conceptual model | Ontology passes reasoner |
| Integration | Source and target ontologies identified | SSSOM file validated |
| Evaluation | Any ontology artifact exists | All quality checks pass |
| Maintenance | Change request or version trigger | KGCL changes validated |

```


### `.claude/skills/_shared/tool-decision-tree.md` — Tool selection flowchart and limitations

```markdown
# Tool Decision Tree

When to use each ontology tool. Primary tools should be attempted first;
escalate to secondary tools only when the primary tool cannot handle the task.

## Decision Flowchart

```
What do you need to do?
│
├── Create/modify ontology terms in BULK (>5 terms)?
│   └── ROBOT template
│
├── Make a SINGLE change (rename, reparent, add synonym, deprecate)?
│   └── KGCL via oaklib (runoak apply)
│
├── Search for existing terms or navigate hierarchy?
│   └── oaklib (runoak search, runoak ancestors, runoak descendants)
│
├── Run quality checks or generate reports?
│   └── ROBOT (reason, report, verify, diff)
│
├── Validate data against structural constraints?
│   └── pyshacl
│
├── Build complex Description Logic axioms?
│   │   (qualified cardinality, role chains, nested class expressions)
│   └── OWLAPY
│
├── Rapid prototype or explore ontology as Python objects?
│   └── owlready2
│
├── Define a schema that generates multiple artifact types?
│   │   (OWL + SHACL + JSON Schema + Python classes)
│   └── LinkML
│
├── Manipulate raw RDF triples or custom serialization?
│   └── rdflib
│
├── Create or validate SSSOM mapping files?
│   └── sssom-py
│
└── Generate SPARQL queries or query a triple store?
    └── See sparql-expert skill
```

## Primary Tools (use first)

### ROBOT CLI

| Operation | Command | When to Use |
|-----------|---------|-------------|
| Bulk term creation | `robot template` | Adding >5 terms from tabular data |
| Merge modules | `robot merge` | Combining imports or components |
| Classify ontology | `robot reason` | After any structural change |
| Quality report | `robot report` | Before every commit |
| Run CQ tests | `robot verify` | Checking SPARQL-based acceptance tests |
| Compare versions | `robot diff` | PR descriptions, changelogs |
| Convert formats | `robot convert` | Turtle ↔ OWL/XML ↔ JSON-LD |
| Extract module | `robot extract` | Importing subset of external ontology |
| Annotate | `robot annotate` | Adding version info, metadata |

#### Reasoner Selection

| Reasoner | Strengths | Trade-offs | Use When |
|----------|-----------|------------|----------|
| ELK | Very fast on EL ontologies | Incomplete for full OWL DL features | Large taxonomies, frequent CI checks |
| HermiT | Complete OWL DL reasoning | Slower on large/complex models | Pre-release validation, full DL constructs |
| Pellet/Openllet | Full DL + useful explanations | Slower/heavier runtime | Need explanation support or DL completeness checks |

Practical guidance:
- ELK is the workhorse for OBO ontologies — use it for daily development and CI.
- ELK handles OWL 2 EL only. It silently ignores axioms outside EL (qualified
  cardinality, universal restrictions, complements). This can cause missed
  inferences that are hard to debug.
- Escalate to HermiT or Pellet/Openllet for pre-release validation, when using
  full DL features, or when ELK results seem incomplete.
- Timing expectations: ELK on 10K classes takes seconds; HermiT on the same
  ontology may take minutes to hours.
- Incremental reasoning is not widely supported — reasoners re-classify the
  entire ontology even for a single axiom change. Reason at commit time or CI,
  not after every edit during active development.

### oaklib (runoak)

| Operation | Command | When to Use |
|-----------|---------|-------------|
| Term search | `runoak search` | Finding existing terms before creating |
| Hierarchy nav | `runoak ancestors` / `runoak descendants` | Exploring taxonomy |
| Apply change | `runoak apply` | Single KGCL changes |
| Batch changes | `runoak apply --changes-input` | Applying KGCL patch files |
| Lexical match | `runoak lexmatch` | Generating mapping candidates |
| Term info | `runoak info` | Retrieving term metadata |
| Validate | `runoak validate` | OBO-specific validation |

#### Known Limitations

oaklib is powerful but has rough edges that practitioners regularly encounter:

- **Adapter inconsistency**: Operations that work on one backend (SQLite,
  OLS, local OWL) may fail or return different results on another. Test
  commands against your specific adapter.
- **KGCL implementation is incomplete**: `obsolete` and `rename` work
  reliably, but complex operations like `create axiom` with full Manchester
  Syntax may fail. When KGCL fails, fall back to ROBOT or rdflib.
- **SQLite cache staleness**: The `sqlite:obo:` adapter caches downloaded
  ontologies. Clear `~/.data/oaklib/` to force refresh after upstream
  ontology releases.
- **Serialization instability**: Applying KGCL changes to local `.ttl` files
  can produce different prefix ordering or serialization format than the
  input. Run `robot convert --input file.ttl --output file.ttl` afterward
  to normalize serialization before committing.
- **Large batch performance**: oaklib's SQLite adapter is fast for search
  but slow for bulk KGCL application. For >20 changes, consider ROBOT
  template or direct rdflib manipulation instead.

### KGCL (Knowledge Graph Change Language)

Not a tool itself — a language processed by oaklib. Use for:

- Human-reviewable change proposals
- Auditable change history
- Batch changes via `.kgcl` files
- Changes that need user approval before applying

Common KGCL commands:
```
create class EX:0001 'New Term'
obsolete EX:0042
rename EX:0001 from 'Old Name' to 'New Name'
move EX:0010 from EX:0001 to EX:0002
create synonym 'Alt Name' for EX:0001
create edge EX:0001 rdfs:subClassOf EX:0002
create definition 'A thing that...' for EX:0001
```

## Secondary Tools (escalation criteria)

### OWLAPY — When to escalate

Use when ROBOT templates cannot express the axiom AND you need the full OWL
API (e.g., computing entailments, DL learners). Requires a JVM.

- Qualified cardinality restrictions (`ObjectMinCardinality 2 hasWheel`)
- Role chains (`hasParent o hasParent SubPropertyOf hasGrandparent`)
- Nested class expressions (`A and (B or (C and hasP some D))`)
- Complex equivalent class definitions
- Property characteristics requiring OWL API (asymmetric, reflexive)
- Programmatic axiom generation from external data with complex logic

**Note**: Most OBO community practitioners use **rdflib** (triple-level
manipulation, no JVM) rather than OWLAPY for programmatic Python work.
Consider rdflib first unless you specifically need the OWL API abstraction.

### owlready2 — When to escalate

Use for:

- Loading and exploring ontology as Python object graph
- Rapid prototyping where ORM-style access is faster than axiom manipulation
- Working with the built-in SQLite quadstore for large ontologies
- Accessing and modifying individual-level data (ABox operations)

### LinkML — When to escalate

Best for **data model schemas**, not rich OWL ontologies:

- Primary deliverable is a data schema (JSON Schema, SHACL, Python classes)
- Needing multiple artifact types from one source (OWL + SHACL + JSON Schema)
- Data models with strong tabular/JSON structure
- When domain experts need to review YAML rather than OWL

**Not ideal when**: The ontology requires complex axioms (qualified cardinality,
property chains, nested class expressions). LinkML-generated OWL is flat and
needs post-processing with ROBOT or OWLAPY for rich TBox content.

### rdflib — When to escalate

Use for:

- Custom RDF serialization or parsing
- Graph-level operations (merge, diff at triple level)
- SPARQL query execution against local files
- RDF-star triple manipulation
- When you need fine-grained control over individual triples

### sssom-py — When to escalate

Use for:

- SSSOM file validation (`sssom validate`)
- Mapping file merge and deduplication
- Converting between SSSOM formats (TSV ↔ JSON ↔ OWL)
- Programmatic mapping creation and analysis

### pyshacl — When to escalate

Use for:

- Validating RDF data against SHACL shapes
- Checking structural constraints (label coverage, definition coverage)
- Custom validation rules beyond what ROBOT report covers
- Data quality assessment for populated ontologies (ABox validation)

## Anti-Patterns in Tool Selection

| Anti-Pattern | Problem | Correct Approach |
|-------------|---------|-----------------|
| Hand-editing .ttl files | Bypasses validation, error-prone | Use ROBOT, oaklib, or Python tools |
| Using OWLAPY for simple SubClassOf | Over-engineering | Use ROBOT template or KGCL |
| Using owlready2 for production builds | Not designed for CI/CD pipelines | Use ROBOT for build workflows |
| Using rdflib to add classes | Too low-level for ontology operations | Use oaklib or ROBOT |
| Skipping reasoner after changes | May introduce inconsistencies | Always run `robot reason` |

```


### `.claude/skills/_shared/bfo-categories.md` — BFO decision procedure and known ambiguities

```markdown
# BFO Categories — Decision Procedure

Reference for aligning domain concepts to Basic Formal Ontology (BFO, ISO
21838-2). Used during conceptualization and architecture phases.

## The Top-Level Split

Every entity falls into exactly one of two disjoint categories:

```
Entity (BFO:0000001)
├── Continuant (BFO:0000002) — persists through time, has no temporal parts
└── Occurrent (BFO:0000003) — unfolds in time, has temporal parts
```

**Decision question**: Does this entity persist through time while
maintaining its identity, or does it unfold/happen over a period of time?

- "A person **exists** at each moment" → Continuant
- "A surgery **happens** over time" → Occurrent

## Continuant Decision Tree

```
Is it a Continuant?
│
├── Does it exist independently (not dependent on a bearer)?
│   ├── YES → Independent Continuant (BFO:0000004)
│   │   ├── Is it a material thing with mass?
│   │   │   ├── YES → Material Entity (BFO:0000040)
│   │   │   │   ├── Maximally self-connected? → Object (BFO:0000030)
│   │   │   │   │   Examples: person, cell, planet, violin
│   │   │   │   ├── Collection of objects? → Object Aggregate (BFO:0000027)
│   │   │   │   │   Examples: orchestra, cell population, fleet
│   │   │   │   └── Part of an object, not self-connected? → Fiat Object Part (BFO:0000024)
│   │   │   │       Examples: upper lobe of lung, headstock of guitar
│   │   │   └── NO → Immaterial Entity (BFO:0000141)
│   │   │       ├── Bounded three-dimensional? → Site (BFO:0000029)
│   │   │       │   Examples: concert hall interior, body cavity
│   │   │       ├── Region of space? → Spatial Region (BFO:0000006)
│   │   │       │   Examples: coordinate region, boundary surface
│   │   │       └── Boundary of a material entity? → Continuant Fiat Boundary (BFO:0000140)
│   │   │           Examples: equator, state border, property line
│   │
│   └── NO → It depends on a bearer (some Independent Continuant)
│       └── Specifically/Generically Dependent Continuant
│
├── Does it depend on ONE specific bearer?
│   └── YES → Specifically Dependent Continuant (BFO:0000020)
│       ├── Is it a measurable/observable property?
│       │   └── YES → Quality (BFO:0000019)
│       │       Examples: color, mass, temperature, pitch
│       ├── Is it a capacity/tendency that may or may not be realized?
│       │   └── YES → Realizable Entity (BFO:0000017)
│       │       ├── Exists because of the bearer's physical makeup?
│       │       │   ├── Tendency toward a process? → Disposition (BFO:0000016)
│       │       │   │   Examples: fragility, solubility, disease susceptibility
│       │       │   └── Selected/designed purpose? → Function (BFO:0000034)
│       │       │       Examples: heart's pumping function, gene's coding function
│       │       └── Exists because of social/contextual factors?
│       │           └── Role (BFO:0000023)
│       │               Examples: student role, employer role, patient role
│       └── (Other SDC subcategories are rarely needed)
│
└── Does it depend on one or more bearers but can migrate between them?
    └── YES → Generically Dependent Continuant (BFO:0000031)
        Examples: PDF document, musical score, software program, recipe
        (See "GDC concretization pattern" below)
```

## Occurrent Decision Tree

```
Is it an Occurrent?
│
├── Does it have temporal extent (duration)?
│   ├── YES → Process (BFO:0000015)
│   │   Examples: surgery, concert performance, chemical reaction, running
│   │   └── Is it a proper temporal part of another process?
│   │       └── YES → Process (still — processes can have process parts)
│   │
│   └── Is it a region of time itself?
│       └── YES → Temporal Region (BFO:0000008)
│           ├── Has duration? → One-Dimensional Temporal Region (BFO:0000038)
│           │   Examples: time interval, historical period
│           └── Instantaneous? → Zero-Dimensional Temporal Region (BFO:0000148)
│               Examples: instant, time point
│
├── Is it an instantaneous boundary of a process?
│   └── YES → Process Boundary (BFO:0000035)
│       Examples: birth (as instantaneous event), moment of impact
│
├── Is it the complete lifecycle of processes involving one material entity?
│   └── YES → History (BFO history class)
│       Example: the full disease history of one patient
│
└── Is it a region of spacetime?
    └── YES → Spatiotemporal Region (BFO:0000011)
        Examples: the spacetime region occupied by a process
```

## Common Mistakes

| Mistake | Why It's Wrong | Correct Classification |
|---------|---------------|----------------------|
| "Student" as a subclass of Person | Student is a **role** played by a person | Student is a **Role** (BFO:0000023); a Person **bears** a Student role |
| "Surgery" as a Material Entity | Surgery unfolds in time | Surgery is a **Process** (BFO:0000015) |
| "Red" as a subclass of Color | Red is an instance of the color quality | Red is a **particular Quality** value, or use a value partition pattern |
| "Information" as Independent Continuant | Information depends on a physical carrier | Information content entity is a **GDC** (BFO:0000031) |
| "Location" as a Quality | Locations are regions, not dependent qualities | Use **Site** (BFO:0000029) or **Spatial Region** (BFO:0000006) |
| Using `part_of` for containment | `part_of` is mereological; containment/location is different | Use `located_in` for location and `part_of` only for genuine parthood |
| "Disease" as a Process | Disease is a disposition toward pathological processes | Disease is a **Disposition** (BFO:0000016) |
| "Gene" as information | A gene is a physical segment of DNA | Gene is a **Material Entity**; the sequence is a GDC |
| "Organization" as Object | Organizations have members that change | Organization is an **Object Aggregate** (BFO:0000027). Note: BFO 2020 treats organizations as Objects; many biomedical ontologies model them as Object Aggregates. Choose based on your domain's conventions and document the rationale. |

## Key BFO Relations (from RO)

| Relation | Domain | Range | Use When |
|----------|--------|-------|----------|
| `RO:0000052` (inheres in) | SDC | IC | Quality/disposition/role inheres in its bearer |
| `RO:0000053` (bearer of) | IC | SDC | Inverse of inheres in |
| `RO:0000056` (participates in) | Continuant | Process | A continuant takes part in a process |
| `RO:0000057` (has participant) | Process | Continuant | Inverse of participates in |
| `BFO:0000050` (part of) | — | — | Parthood (mereological) |
| `BFO:0000051` (has part) | — | — | Inverse of part of |
| `RO:0000087` (has role) | IC | Role | Entity bears a role |
| `RO:0000080` (has quality) | IC | Quality | Entity has a quality |
| `BFO:0000054` (realized in) | Realizable | Process | Disposition/function realized in a process |
| `BFO:0000055` (realizes) | Process | Realizable | Process realizes a disposition/function |

## Temporal Indexing Rules

Some relations require explicit time indexing to avoid category mistakes.

- **Continuant-continuant relations** (for example `part_of`, `located_in`)
  can change over time and should be interpreted with a time parameter.
- **Occurrent-occurrent relations** are fixed once the occurrent exists and
  usually do not need additional temporal indexing.

Verbal quantification templates:

- Universal-level relation:
  "For every instance of class A, there exists some instance of class B such
  that relation R holds at time t."
- Time-sensitive parthood:
  "A cell is part_of an organ at t1" does not entail "part_of at t2".

## GDC Concretization Pattern

For information entities and other GDCs, model concretization explicitly:

- A **GDC** is concretized in a **specifically dependent continuant**.
- That specifically dependent continuant inheres in a **material entity**.
- Use an explicit concretization relation such as `isConcretizationOf`.

Example:
"This PDF file" (material bearer) concretizes an information content entity
(the document content) via a concretization chain.

## Perspectives

The same real-world thing can be modeled from different perspectives:

- **Continuant perspective**: anatomy/structure ("what it is")
- **Occurrent perspective**: physiology/process ("what happens")

Use this to avoid false disjointness between structural and process views.

## BFO-OBO Alignment Matrix

Indicative mapping between granularity, BFO category, and common OBO sources.

| Granularity | BFO Category | Typical OBO Ontology |
|------------|--------------|----------------------|
| Molecular | Material Entity / Object | ChEBI, PRO |
| Cellular | Material Entity / Object | CL (Cell Ontology) |
| Anatomical structure | Material Entity / Fiat Object Part | UBERON |
| Biological process | Process | GO Biological Process |
| Phenotype/quality | Quality / Disposition | PATO, HPO |
| Information artifact | GDC | OBI, IAO |

## Known Ambiguities

The decision trees above present clean categories, but practitioners regularly
encounter entities where the correct BFO alignment is genuinely debated. When
you hit one of these, document your choice and rationale explicitly.

| Entity | Debate | Recommended Default | Alternative | Choose Alternative When |
|--------|--------|--------------------:|-------------|------------------------|
| Disease | Disposition vs Process | **Disposition** (per OGMS) — a tendency toward pathological processes | Process | Your domain treats disease as something that "happens" rather than something an organism "has" |
| Organization | Object vs Object Aggregate | **Object** (per BFO 2020) — identity persists through member changes | Object Aggregate | Your domain defines the organization by its members (e.g., a research consortium) |
| Information entity | GDC with concretization chain | **GDC** (per IAO pattern) — model the 3-hop chain: GDC → concretized in → SDC → inheres in → Material Entity | Skip concretization, model as GDC directly | Concretization detail is not relevant to your CQs |
| "Being toxic" | Disposition vs Role | **Disposition** — arises from physical makeup | Role | Toxicity is context-dependent (e.g., a substance toxic only to certain organisms) |
| "Being a drug" | Function vs Disposition vs Role | **Role** — exists because of social/regulatory designation | Function | Your domain defines drugs by their biochemical mechanism, not regulatory status |
| Software, algorithms | Does not fit BFO cleanly | **GDC** (information content entity pattern) | No BFO alignment | Your domain is purely computational; BFO may not add value |
| Legal entities, money, prices | Social constructs with no BFO consensus | **GDC** or **Role** depending on perspective | Consider DOLCE or no upper ontology | Social/legal domains where BFO categories cause more confusion than clarity |

**BFO version note**: The published book (Arp, Smith, Spear 2015) is based on
BFO 2.0. The ISO standard (ISO 21838-2:2021) reflects BFO 2020, which has some
differences in category names and relation definitions. Always check which
version your target community uses. OBO Foundry ontologies generally follow
BFO 2020.

## Quick Reference: "Is it a...?"

| If your concept is... | Then it's probably... |
|----------------------|----------------------|
| A physical thing you can touch | Object or Object Aggregate |
| A property you can measure | Quality |
| A capacity that may be exercised | Disposition or Function |
| A social position or status | Role |
| Something written/recorded | Generically Dependent Continuant |
| Something that happens over time | Process |
| A point in time | Temporal Region |
| A place or container | Site |

```


### `.claude/skills/_shared/axiom-patterns.md` — 16 OWL 2 axiom patterns

```markdown
# Axiom Patterns

16 core OWL 2 axiom patterns with when-to-use guidance, ROBOT template
syntax, and Manchester Syntax examples. Reference for the conceptualizer
and architect skills.

## 1. Simple SubClassOf (Primitive Class)

**When**: Asserting that one class is a subtype of another.

**Manchester Syntax**:
```
Class: Piano
  SubClassOf: KeyboardInstrument
```

**ROBOT Template**:
```tsv
ID	LABEL	SC %
ID	A rdfs:label	SC %
EX:0001	piano	EX:0010
```

**Notes**: The foundation of taxonomy. Every class should have at least one
named superclass (no orphans except owl:Thing).

---

## 2. Existential Restriction (SomeValuesFrom)

**When**: "Every X has at least one Y" — expressing necessary conditions.

**Pattern**: `X SubClassOf R some Y`

**Manchester Syntax**:
```
Class: Guitar
  SubClassOf: hasComponent some String
```

**ROBOT Template**:
```tsv
ID	LABEL	SC %	REL
ID	A rdfs:label	SC %	'hasComponent' some %
EX:0002	guitar	EX:0010	EX:0030
```

**Notes**: The most common restriction pattern. Use for necessary conditions
that define what members of the class must have.

---

## 3. Universal Restriction (AllValuesFrom / Closure Axiom)

**When**: "The only Y that X can have are Z" — constraining the range of a
relation for a specific class.

**Pattern**: `X SubClassOf R only Y`

**Manchester Syntax**:
```
Class: VegetarianPizza
  SubClassOf: hasTopping only VegetableTopping
```

**Notes**: Often combined with an existential restriction to form a
**closure axiom**: "has at least one, and only these." Without a
corresponding `some`, the universal restriction alone is satisfied by
having no values at all (vacuous truth).

**Worked closure example**:
```
Class: VegetarianPizza
  SubClassOf: hasTopping some VegetableTopping
  SubClassOf: hasTopping only VegetableTopping
```

---

## 4. Equivalent Class (Defined Class)

**When**: Providing necessary AND sufficient conditions — enabling automatic
classification by the reasoner.

**Pattern**: `X EquivalentTo Y and R some Z`

**Manchester Syntax**:
```
Class: StringInstrument
  EquivalentTo: MusicalInstrument and hasComponent some String
```

**ROBOT Template**:
```tsv
ID	LABEL	EC %
ID	A rdfs:label	EC %
EX:0020	string instrument	EX:0010 and ('hasComponent' some EX:0030)
```

**Notes**: Defined classes are the heart of reasoning. Any individual (or
class) that satisfies the conditions will be automatically classified.
Use sparingly — not every class needs to be defined.

**Design decision: `SubClassOf` vs `EquivalentClass`**
- Use `SubClassOf` when you are asserting only necessary conditions.
- Use `EquivalentClass` when you are confident the condition set is both
  necessary and sufficient.
- Default to `SubClassOf` if domain consensus is incomplete; premature
  equivalence often causes misclassification cascades.

---

## 5. Disjoint Classes

**When**: Two sibling classes under the same parent share no instances.

**Pattern**: `DisjointClasses: A, B, C`

**Manchester Syntax**:
```
DisjointClasses: WindInstrument, StringInstrument, PercussionInstrument
```

**ROBOT Template**:
```tsv
ID	LABEL	SC %	DISJOINT_WITH
ID	A rdfs:label	SC %	DC %
EX:0020	string instrument	EX:0010	EX:0021
EX:0021	wind instrument	EX:0010	EX:0020
```

**Notes**: Disjointness is critical for reasoning — without it, the
reasoner cannot detect classification errors. Siblings under the same
parent SHOULD be declared disjoint unless there is a specific reason
not to. For >2 classes, use `DisjointClasses` (pairwise disjointness)
or `DisjointUnion`.

---

## 6. Covering Axiom (Disjoint Union / Exhaustive Partition)

**When**: A parent class is fully partitioned into its children — "X is
exactly A, B, or C, and nothing else."

**Pattern**: `X DisjointUnionOf A, B, C`

**Manchester Syntax**:
```
Class: InstrumentFamily
  DisjointUnionOf: StringFamily, WindFamily, PercussionFamily, KeyboardFamily
```

**Notes**: Combines SubClassOf + DisjointClasses + Covering in one axiom.
Use when the enumeration is exhaustive and stable. Be cautious — adding
a new sibling later requires updating the union.

---

## 7. Qualified Cardinality Restriction

**When**: "X has exactly/at least/at most N values of type Y for relation R."

**Pattern**: `X SubClassOf R exactly N Y`

**Manchester Syntax**:
```
Class: StringQuartet
  SubClassOf: hasMember exactly 4 Musician
```

**ROBOT Template** (requires `EC %` or `SC %` with full expression):
```tsv
ID	LABEL	SC %
ID	A rdfs:label	SC %
EX:0050	string quartet	'hasMember' exactly 4 EX:0060
```

**Notes**: Requires OWL 2 DL. Unqualified cardinality (`R exactly 3`) is
simpler but less expressive. ELK does not support cardinality — use
HermiT or Pellet.

---

## 8. Value Partition Pattern

**When**: Modeling quality values as a controlled vocabulary (e.g., sizes,
grades, severity levels).

**Pattern**: Quality class with exhaustive partition of value classes.

**Manchester Syntax**:
```
Class: PitchRange
  DisjointUnionOf: HighPitch, MediumPitch, LowPitch

Class: HighPitch
  SubClassOf: PitchRange

Class: Cello
  SubClassOf: hasPitchRange some LowPitch
```

**Notes**: Preferred over data properties with string values. Enables
reasoning over quality values. Each value is a class, not an individual.

---

## 9. N-ary Relation Pattern

**When**: A relation involves more than two participants (e.g., "Person X
prescribed Drug Y for Condition Z at Time T").

**Pattern**: Reify the relation as a class.

**Manchester Syntax**:
```
Class: MusicalPerformance
  SubClassOf: Process
  SubClassOf: hasPerformer some Musician
  SubClassOf: hasPiece some MusicalWork
  SubClassOf: hasVenue some Site
  SubClassOf: hasDate some xsd:date
```

**Notes**: OWL only supports binary relations. For n-ary, create a
"connector" class representing the event/situation. The connector class
holds all the participants via binary relations.

---

## 10. Self-Restriction Pattern

**When**: "Every X is related to itself via R" (reflexive for a specific class).

**Pattern**: `X SubClassOf R Self`

**Manchester Syntax**:
```
Class: NarcissisticEntity
  SubClassOf: admires Self
```

**Notes**: Rarely needed. More common is to declare the property reflexive
globally (`ReflexiveObjectProperty: partOf`).

---

## 11. HasKey Axiom

**When**: Defining a unique identifier for individuals of a class — analogous
to a database primary key.

**Pattern**: `HasKey(C, P1, P2, ...)`

**Manchester Syntax**:
```
Class: Person
  HasKey: hasSSN
```

**Notes**: OWL 2 feature. Individuals of class C are considered identical
if they share values for all key properties. Useful for instance matching
and data integration.

---

## 12. Property Chain (SubPropertyChain)

**When**: Inferring a relation from a sequence of relations — "if A R1 B
and B R2 C, then A R3 C."

**Pattern**: `R3 SubPropertyChainOf R1 o R2`

**Manchester Syntax**:
```
ObjectProperty: hasGrandparent
  SubPropertyChain: hasParent o hasParent
```

**Notes**: Powerful for transitive-like inference paths. OWL 2 allows
chains of arbitrary length but regularity restrictions apply (R can
appear at most once and only at the end of its own chain). ELK supports
simple chains.

---

## 13. Negation (Negative Property Assertion)

**When**: You must explicitly state that a specific relation does not hold
between two named individuals.

**Pattern**: `NegativeObjectPropertyAssertion( R a b )`

**Manchester Syntax**:
```
Individual: Alice
  Facts: not hasParent Bob
```

**Notes**: Assertion-level construct. Use sparingly; in OWA, absence of a
triple is not equivalent to negation.

---

## 14. Identity Links (`owl:sameAs` / `owl:differentFrom`)

**When**: Asserting strict identity (or non-identity) between individuals.

**Pattern**:
- `a owl:sameAs b`
- `a owl:differentFrom b`

**Manchester Syntax**:
```
Individual: ex:PatientRecord123
  SameAs: ex:NationalRegistryPerson987
```

**Notes**: `owl:sameAs` is very strong and transitive. One incorrect link can
merge large identity clusters and propagate unintended inferences.

---

## 15. Enumeration (`owl:oneOf`)

**When**: Representing a genuinely closed, finite set of named individuals.

**Pattern**: `Class: C EquivalentTo {a, b, c}`

**Manchester Syntax**:
```
Class: TrafficLightState
  EquivalentTo: {RedState, YellowState, GreenState}
```

**Notes**: Use only for stable closed sets. If the set changes frequently,
prefer a normal class hierarchy or controlled vocabulary approach.

---

## 16. Complement (`owl:complementOf`)

**When**: Defining a class as the complement of another class.

**Pattern**: `A EquivalentTo not B`

**Manchester Syntax**:
```
Class: NonSmoker
  EquivalentTo: not Smoker
```

**Notes**: Use cautiously. Complement-heavy modeling can indicate missing
positive class definitions or insufficient partition design.

---

## Pattern Selection Guide

| CQ Pattern | Axiom Pattern | # |
|-----------|--------------|---|
| "Every X has a Y" | Existential restriction | 2 |
| "X can only have Y" | Universal restriction / closure | 3 |
| "X is defined as Y with Z" | Equivalent class | 4 |
| "X and Y never overlap" | Disjoint classes | 5 |
| "X is exactly A, B, or C" | Covering axiom | 6 |
| "X has exactly N of Y" | Qualified cardinality | 7 |
| "X has high/medium/low Z" | Value partition | 8 |
| "X did Y to Z at time T" | N-ary relation | 9 |
| "X is identified by P" | HasKey | 11 |
| "if R1 then R2" (chained) | Property chain | 12 |
| "These two identifiers are the same individual" | Identity links | 14 |
| "Class is exactly this finite set" | Enumeration | 15 |

```


### `.claude/skills/_shared/anti-patterns.md` — 16 modeling anti-patterns with SPARQL detection

```markdown
# Anti-Patterns

16 common ontology modeling anti-patterns with descriptions, examples, why
they are wrong, how to fix them, and SPARQL detection queries. Reference
for the conceptualizer and validator skills.

## 1. Singleton Hierarchy (Lazy Taxonomy)

**Description**: A class has exactly one subclass. The intermediate class
adds no meaningful distinction.

**Example**:
```
MusicalInstrument → StringInstrument → Guitar
```
(Where `StringInstrument` has only `Guitar` as a subclass.)

**Why it's wrong**: Adds unnecessary depth without information. Violates
the principle that classification should reflect real distinctions.

**Fix**: Either add sibling classes to `StringInstrument` (Violin, Cello)
or collapse the hierarchy: `Guitar SubClassOf MusicalInstrument`.

**Detection (SPARQL)**:
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?parent (COUNT(?child) AS ?childCount) WHERE {
  ?child rdfs:subClassOf ?parent .
  FILTER(?parent != owl:Thing)
  FILTER(!isBlank(?child))
  FILTER(!isBlank(?parent))
}
GROUP BY ?parent
HAVING (COUNT(?child) = 1)
```

---

## 2. Role-Type Confusion

**Description**: Modeling a role as a subclass instead of using the role
pattern. The entity changes "type" depending on context.

**Example** (wrong):
```
Person → Student
Person → Teacher
```

**Why it's wrong**: A person can be both a student and a teacher, and can
stop being either without changing identity. If Student and Teacher are
disjoint subclasses of Person, a Person cannot be both simultaneously.

**Fix**: Use BFO's Role pattern:
```
Person bearerOf some StudentRole
StudentRole SubClassOf Role
```

**Detection**: Look for classes whose names suggest roles (ending in -er,
-or, -ist, -ant) that are modeled as subclasses of their bearer.

---

## 3. Process-Object Confusion

**Description**: Modeling a process (something that unfolds in time) as a
material entity, or vice versa.

**Example** (wrong):
```
Surgery SubClassOf MaterialEntity
```

**Why it's wrong**: Surgery has temporal parts (incision, closure) and
participants — it's a Process, not an Object.

**Fix**: `Surgery SubClassOf Process`, with `hasParticipant some Surgeon`.

**Detection**: Check class names against BFO categories. Terms ending in
-tion, -ment, -sis, -ing typically denote processes.

---

## 4. Missing Disjointness

**Description**: Sibling classes under the same parent are not declared
disjoint, even though they clearly cannot overlap.

**Example** (incomplete):
```
Animal → Mammal
Animal → Reptile
# No disjoint axiom between Mammal and Reptile
```

**Why it's wrong**: Without disjointness, the reasoner cannot detect
classification errors. An individual could be asserted as both Mammal
and Reptile without triggering inconsistency.

**Fix**: `DisjointClasses: Mammal, Reptile, Amphibian, ...`

**Detection (SPARQL)**:
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

# Finds sibling classes missing pairwise disjointness.
# Note: also check owl:AllDisjointClasses declarations,
# which cover multi-way disjointness more concisely.
SELECT ?parent ?child1 ?child2 WHERE {
  ?child1 rdfs:subClassOf ?parent .
  ?child2 rdfs:subClassOf ?parent .
  FILTER(STR(?child1) < STR(?child2))
  FILTER NOT EXISTS { ?child1 owl:disjointWith ?child2 }
  FILTER NOT EXISTS { ?child2 owl:disjointWith ?child1 }
  FILTER NOT EXISTS {
    ?disj a owl:AllDisjointClasses ;
          owl:members ?list .
    ?list rdf:rest*/rdf:first ?child1 .
    ?list rdf:rest*/rdf:first ?child2 .
  }
  FILTER(!isBlank(?child1))
  FILTER(!isBlank(?child2))
  FILTER(?parent != owl:Thing)
}
```

---

## 5. Circular Definition

**Description**: A class is defined in terms of itself, directly or
through a chain of definitions.

**Example** (wrong):
```
Parent EquivalentTo Person and hasChild some Person
Child EquivalentTo Person and hasParent some Parent
Parent EquivalentTo Person and hasChild some Child
```

**Why it's wrong**: Circular definitions are logically uninformative —
they don't constrain the extension of the class.

**Fix**: Ground at least one class in the chain as a primitive (SubClassOf
only, not EquivalentTo).

**Detection**: Trace EquivalentTo chains — if a class appears in its own
expansion, it's circular.

---

## 6. Quality-as-Class (Reified Attribute)

**Description**: Modeling a quality value as a standalone class in the
hierarchy instead of using the value partition or quality pattern.

**Example** (wrong):
```
Color → Red
Color → Blue
Thing → RedThing  (EquivalentTo Thing and hasColor value Red)
```

**Why it's wrong**: Conflates the quality (color) with the quality value
(red). Leads to proliferation of classes like RedCar, BlueCar.

**Fix**: Use value partition pattern (see axiom-patterns.md #8):
```
Color DisjointUnionOf Red, Blue, Green
Car SubClassOf hasColor some Color
```

---

## 7. Information-Physical Conflation

**Description**: Treating information content and its physical carrier as
the same entity.

**Example** (wrong):
```
Book SubClassOf InformationContentEntity
# But Book also has physical properties like weight, location
```

**Why it's wrong**: A book (physical) and the text it contains
(information) are distinct entities. The text can exist in multiple
physical copies.

**Fix** (BFO pattern):
```
BookCopy SubClassOf MaterialEntity (Object)
TextualWork SubClassOf GenericallyDependentContinuant
BookCopy isConcretizationOf some TextualWork
```

---

## 8. Orphan Class

**Description**: A class has no named superclass (other than `owl:Thing`).

**Example** (wrong):
```
Class: SpecialWidget
  # No SubClassOf assertion
```

**Why it's wrong**: Disconnected from the taxonomy. Cannot benefit from
inherited axioms or be found through hierarchical navigation.

**Fix**: Place the class under an appropriate parent. If no parent
exists, it may indicate a gap in the upper-level alignment.

**Detection (SPARQL)**:
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?orphan WHERE {
  ?orphan a owl:Class .
  FILTER NOT EXISTS {
    ?orphan rdfs:subClassOf ?parent .
    FILTER(?parent != owl:Thing)
    FILTER(!isBlank(?parent))
  }
  FILTER(?orphan != owl:Thing)
  FILTER(?orphan != owl:Nothing)
  FILTER(!isBlank(?orphan))
}
```

---

## 9. Polysemy / Overloaded Term

**Description**: A single class is used to represent multiple distinct
concepts, causing logical confusion.

**Example** (wrong):
```
Class: Bank
  # Sometimes means financial institution, sometimes river bank
```

**Why it's wrong**: Creates ambiguous reasoning results. Axioms appropriate
for one sense are incorrectly applied to the other.

**Fix**: Mint separate classes with disambiguated labels:
```
Class: FinancialInstitution  (label: "bank (financial)")
Class: RiverBank             (label: "bank (geographic)")
```

**Detection**: Look for classes with multiple, semantically divergent
definitions or synonyms. Check for classes with disjoint parent candidates.

---

## 10. Property Domain/Range Overcommitment

**Description**: Setting overly broad or overly narrow domain/range on
a property, causing unintended classification.

**Example** (wrong):
```
ObjectProperty: prescribes
  Domain: Physician
  Range: Drug
```

If you assert `NurseJane prescribes Aspirin`, the reasoner will infer
`NurseJane rdf:type Physician` — probably not intended.

**Why it's wrong**: OWL domain/range axioms are NOT constraints — they
are inference rules. Any use of the property triggers classification
of subject/object into the declared domain/range.

**The key misconception**: Most newcomers (and many experienced practitioners)
treat domain/range like SQL foreign keys. They are not — they are inference
rules. This is the single most common OWL "gotcha" in practice.

**The "too narrow domain" cascade**: Setting domain to a leaf class causes
everything that uses the property to be classified as that leaf class. This
is a major source of unexpected unsatisfiable classes in real-world ontologies.

**Fix** — use this decision procedure:

1. **Want to constrain?** Use SHACL `sh:class` on a property shape.
2. **Want to infer?** Use OWL domain/range, but keep it BROAD (parent
   classes, not leaves).
3. **Want per-class restrictions?** Use local OWL restrictions:
   `Physician SubClassOf prescribes only Drug`

**Detection (SPARQL)**:
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

# Find properties with domain or range set to leaf classes (high risk)
SELECT ?prop ?narrowClass ?position WHERE {
  {
    ?prop rdfs:domain ?narrowClass .
    BIND("domain" AS ?position)
  } UNION {
    ?prop rdfs:range ?narrowClass .
    FILTER(isIRI(?narrowClass))
    BIND("range" AS ?position)
  }
  FILTER NOT EXISTS {
    ?child rdfs:subClassOf ?narrowClass .
    FILTER(?child != ?narrowClass)
    FILTER(!isBlank(?child))
  }
  FILTER(?narrowClass != owl:Thing)
}
```

---

## 11. Individuals in the T-box

**Description**: Placing many instance assertions directly in the ontology's
schema module and treating A-box data as if it were T-box structure.

**Example** (wrong):
```
# In core ontology file
Class: Country
Individual: USA
Individual: Canada
... (hundreds of instances)
```

**Why it's wrong**: Blurs schema/data boundaries, increases maintenance burden,
and makes modular reuse harder.

**Fix**: Keep schema in the T-box module. Move reference and test individuals
to dedicated A-box modules (for example `reference-individuals.ttl`,
`test-individuals.ttl`).

**Detection (SPARQL)**:
```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT (COUNT(?i) AS ?individualCount) WHERE {
  ?i a owl:NamedIndividual .
}
```

---

## 12. Negative Universals / Class Complements Overuse

**Description**: Modeling classes primarily by negation (for example, broad
use of `owl:complementOf`) instead of positive domain semantics.

**Example** (risky):
```
Class: NonMammal
  EquivalentTo: not Mammal
```

**Why it's wrong**: Under OWA, negative definitions are often too weak or too
broad, and can hide modeling gaps.

**Fix**: Prefer positive classes and explicit disjointness/partitions. Use
complements only when there is a clear closed conceptual boundary.

**Detection**: Review classes using `owl:complementOf` and confirm each has
clear, documented justification.

---

## 13. False is-a from OO Inheritance

**Description**: Translating software inheritance directly into ontology
subclassing without checking ontological subsumption.

**Example** (wrong):
```
Class: PersistenceManager
  SubClassOf: Manager
```

**Why it's wrong**: Programming abstractions encode implementation reuse, not
necessarily real-world category structure.

**Fix**: Assert `is-a` only when every instance of child is necessarily an
instance of parent in the domain, independent of software architecture.

**Detection**: Flag classes that look implementation-specific (`*Manager`,
`*Service`, `*Controller`) and verify domain grounding.

---

## 14. System Blueprint Instead of Domain Model

**Description**: Modeling database tables, APIs, or screens rather than the
domain reality the ontology should represent.

**Example** (wrong):
```
Class: UserTableRow
Class: ApiResponsePayload
```

**Why it's wrong**: Produces brittle ontologies coupled to one system and
invalidates reuse across projects.

**Fix**: Model domain entities and relations first; map technical artifacts in
separate integration layers if needed.

**Detection**: Search for class names tied to implementation artifacts
(`Table`, `Row`, `DTO`, `API`, `Payload`).

---

## 15. Technical Perspective Over Domain Perspective

**Description**: Prioritizing storage/query convenience over correct domain
semantics.

**Example** (risky):
```
Class: FlattenedEventRecord
```

**Why it's wrong**: Convenience-first modeling can introduce semantic drift and
break CQ traceability.

**Fix**: Start from stakeholder questions and domain consensus; optimize
storage/querying after semantic design is stable.

**Detection**: Review terms and axioms justified only by performance or schema
constraints, not by domain meaning.

---

## 16. Mixing Individuals with Classes

**Description**: Confusing class-level and instance-level entities.

**Example** (wrong):
```
Class: Beethoven
Individual: Composer
```

**Why it's wrong**: Breaks reasoning semantics and causes erroneous
inferences.

**Fix**: Keep universals as classes and particulars as individuals. If a term
must be both, use explicit metamodeling only when required and documented.

**Detection (SPARQL)**:
```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?x WHERE {
  ?x a owl:Class .
  ?x a owl:NamedIndividual .
}
```

---

## Summary Checklist

Before finalizing any ontology design, verify:

- [ ] No singleton hierarchies (every parent has ≥2 children, or is a leaf)
- [ ] Roles modeled as roles, not subtypes
- [ ] Processes separated from objects (BFO alignment)
- [ ] Sibling classes are disjoint where appropriate
- [ ] No circular definitions in equivalence chains
- [ ] Quality values use value partition, not standalone class hierarchies
- [ ] Information content distinguished from physical carriers
- [ ] No orphan classes (every class has a named parent)
- [ ] No polysemous terms (one class = one concept)
- [ ] Domain/range used intentionally, not as constraints
- [ ] A-box individuals separated from T-box schema where feasible
- [ ] Complement/negation classes used only with explicit justification
- [ ] Class hierarchy reflects domain subsumption, not OO inheritance
- [ ] Domain model is not replaced by system blueprint artifacts
- [ ] Technical constraints do not drive primary semantic modeling
- [ ] No unintended class/individual mixing

```


### `.claude/skills/_shared/naming-conventions.md` — Term naming, IRI governance, definitions

```markdown
# Naming Conventions

Standards for naming ontology entities, minting identifiers, writing
definitions, and managing labels and synonyms. All skills must follow
these conventions.

## Class Names

- **Format**: `CamelCase` (e.g., `MusicalInstrument`, `StringQuartet`)
- **Rule**: Singular nouns, never plural (`Instrument` not `Instruments`)
- **Compound terms**: No underscores or hyphens in class names
- **Avoid**: Abbreviations unless universally understood in the domain

### Mass Nouns

- **Rule**: Avoid bare mass nouns as class labels. Convert to count-compatible
  forms, typically with "portion of ...".
- **Examples**: `PortionOfBlood`, `PortionOfTissue`, `PortionOfWater`
- **Why**: OWL classes represent universals whose instances are countable
  particulars; mass terms are often ambiguous without individuation.

## Property Names

- **Object properties**: `camelCase` verb phrases (e.g., `hasComponent`,
  `partOf`, `participatesIn`)
- **Data properties**: `camelCase`. Use `has` prefix for domain-specific or
  ambiguous attributes (e.g., `hasWeight`, `hasStartDate`). Bare names are
  acceptable when aligned to a well-known vocabulary (e.g., schema.org) and
  unambiguous in context (e.g., `title`, `url`, `publishedDate`). Avoid bare
  names that collide with OWL/RDFS keywords — e.g., use `siteDomain` instead
  of `domain` to avoid confusion with `rdfs:domain`.
- **Inverse naming**: Use symmetric pairs — `hasPart` / `partOf`,
  `produces` / `producedBy`

### Property Naming Anti-Patterns

- **Anti-pattern**: Encoding class/domain/range in the property name
  (`plantHasBloomColor`, `patientHasBodyTemperature`)
- **Why it's wrong**: Over-specialized names reduce reuse and encourage
  duplicate properties for each class.
- **Preferred**: Keep relation names generic and constrain usage with
  domain/range or class restrictions (`hasColor`, `hasTemperature`).

## Individual Names

- **Named individuals**: `CamelCase` proper nouns (e.g., `Stradivarius1721`)
- **Test individuals**: Prefix with `test_` (e.g., `test_Piano01`)

## Identifier Minting

### OBO-style IDs (preferred for biomedical/scientific ontologies)

- Format: `{PREFIX}_{7-digit-number}` (e.g., `MYONT_0000001`)
- Prefix registered with OBO Foundry (or local prefix for project ontologies)
- IDs are opaque — never encode semantics in the numeric part
- Never reuse IDs, even after deprecation

### IRI-style IDs (for project-specific ontologies)

- Format: `{base-iri}/{ClassName}` or `{base-iri}#{ClassName}`
- Use `#` fragment for small ontologies (single-document retrieval)
- Use `/` path for large ontologies (per-term dereferencing)
- Base IRI must be a stable, resolvable URL when possible

## IRI Governance

Use a stable, documented IRI policy for long-term persistence.

- **Entity IRI pattern**: `https://<authority>/<domain>/<module>/<name>`
- **Document IRI pattern**: `https://<authority>/<domain>/<release-artifact>`
- **Versioning**: Keep entity IRIs immutable; version ontology documents using
  `owl:versionIRI` and `owl:versionInfo`
- **Do not change published entity IRIs**: deprecate terms instead
- **Persistence options**: use PURL or redirect-capable hostname management
- **Skolemization**: minimize blank nodes in released artifacts; mint stable
  IRIs when entities need external reference
- **Best-practice criteria**: availability, understandability, simplicity,
  persistence, manageability

## Labels and Annotations

Every entity MUST have:

| Annotation | Property | Requirement |
|-----------|----------|-------------|
| Label | `rdfs:label` | Exactly one per language tag |
| Definition | `skos:definition` | Required for classes and properties |
| Definition source | `dcterms:source` or `obo:IAO_0000119` | Required when definition is sourced |

### Label Rules

- Lowercase unless proper noun (e.g., "musical instrument", not "Musical Instrument")
- No abbreviations without expansion in synonym
- English (`@en`) is the default language tag
- One preferred label per language; additional forms go in synonyms

## Synonyms

Use OBO-in-OWL synonym properties:

| Property | Use When |
|----------|----------|
| `oio:hasExactSynonym` | Fully interchangeable in all contexts |
| `oio:hasRelatedSynonym` | Related but not interchangeable |
| `oio:hasBroadSynonym` | Synonym is broader than the term |
| `oio:hasNarrowSynonym` | Synonym is narrower than the term |

For production ontologies with multiple user communities, add context
annotations for labels/synonyms (for example `:prefLabelContext` and
`:altLabelContext`) and define those annotation properties in the ontology.

## Definitions: Genus-Differentia Pattern

All definitions MUST follow the genus-differentia pattern:

> "A **[parent class]** that **[differentia]**."

Examples:

| Term | Definition |
|------|-----------|
| Piano | A keyboard instrument that produces sound by hammers striking strings |
| Violin | A string instrument that is played with a bow |
| Jazz Trio | A musical ensemble that consists of exactly three performers playing jazz |

### Definition Quality Criteria

- Necessary and sufficient: captures exactly the intended extension
- No circular references (don't use the term being defined)
- No negation-only definitions ("an X that is not Y")
- Specific differentia (not "a type of X" or "a kind of X")

## Full Vocabulary Entry (Extended)

Use this two-tier approach:

- **Minimum required**: `rdfs:label`, `skos:definition`, `dcterms:source`
- **Recommended for production**: extended annotation set below

| Field | Suggested Annotation Property |
|------|-------------------------------|
| abbreviation | `skos:altLabel` (mark abbreviation in note/profile) |
| explanatoryNote | `skos:note` |
| usageNote | `skos:usageNote` |
| dependsOn | `schema:isBasedOn` |
| termOrigin | `dcterms:source` |
| definitionOrigin | `prov:wasDerivedFrom` |
| adaptedFrom | `prov:wasDerivedFrom` |
| conceptStatus | `owl:deprecated` (boolean) plus status note |
| conceptStatusDate | `dcterms:modified` |
| steward | `dcterms:creator` or `dcterms:contributor` |

## Namespace Usage

- Always use prefixed CURIEs in human-readable contexts (e.g., `BFO:0000001`)
- Always declare prefixes — see `_shared/namespaces.json` for canonical map
- Never use bare IRIs in documentation or KGCL patches
- Project-specific prefixes must be registered in the ontology header and
  in `namespaces.json`

```


### `.claude/skills/_shared/quality-checklist.md` — Pre-commit/pre-release quality gates

```markdown
# Quality Checklist

Universal pre-commit checklist for ontology artifacts. Run these checks
before committing any ontology change. Used by the validator, architect,
and curator skills.

## Required Checks (must all pass)

### 1. Logical Consistency

```bash
robot reason --reasoner ELK --input ontology.ttl
```

- Ontology must be consistent (no logical contradictions)
- No unsatisfiable classes (classes that can have no instances)
- If ELK is insufficient, escalate to HermiT:
  ```bash
  robot reason --reasoner HermiT --input ontology.ttl
  ```

**Failure action**: Do NOT commit. Identify conflicting axioms and fix.

### 2. ROBOT Quality Report

```bash
robot report --input ontology.ttl --fail-on ERROR --output report.tsv
```

Must pass with zero ERRORs. Checks:
- Missing `rdfs:label` on classes
- Missing definitions
- Multiple labels in same language
- Deprecated term references
- Whitespace issues in annotations

**Failure action**: Fix all ERRORs. WARNINGs should be reviewed but do not
block commit.

### 3. SHACL Shape Validation

```bash
pyshacl -s shapes/ontology-shapes.ttl -i rdfs ontology.ttl -f human
```

Must conform to all SHACL shapes. Standard shapes:
- Every class has `rdfs:label` (minCount 1)
- Every class has `skos:definition` (minCount 1, severity: Warning).
  SHACL Warnings are non-blocking but must be tracked. They indicate
  documentation gaps that should be addressed before release.
- No orphan classes (every class has at least one named parent)
- Domain/range constraints are satisfied

**Failure action**: Fix all Violations (severity `sh:Violation`). Track
Warnings (severity `sh:Warning`) as technical debt — they do not block
commit but should be resolved before release.

### 4. CQ Test Suite

```bash
robot verify --input ontology.ttl --queries tests/
```

All competency question SPARQL tests must pass:
- Enumerative CQs: return expected results
- Constraint CQs: return zero violations

**Failure action**: If a CQ test fails after intentional changes, update
the test. If unintentional, revert the change.

## Recommended Checks (should pass)

### 5. Label Coverage

Target: 100% of classes have `rdfs:label`.

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT (COUNT(?c) AS ?total)
       (COUNT(?label) AS ?labeled)
WHERE {
  ?c a owl:Class .
  FILTER(!isBlank(?c))
  OPTIONAL { ?c rdfs:label ?label }
}
```

### 6. Definition Coverage

Target: ≥80% of classes have `skos:definition` or `obo:IAO_0000115`.

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

SELECT (COUNT(?c) AS ?total)
       (COUNT(?def) AS ?defined)
WHERE {
  ?c a owl:Class .
  FILTER(!isBlank(?c))
  OPTIONAL {
    { ?c skos:definition ?def }
    UNION
    { ?c obo:IAO_0000115 ?def }
  }
}
```

### 7. Naming Convention Compliance

Verify against `_shared/naming-conventions.md`:
- Class names are CamelCase
- Property names are camelCase
- Labels are lowercase (unless proper nouns)
- Definitions follow genus-differentia pattern

### 8. No Orphan Classes

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?orphan WHERE {
  ?orphan a owl:Class .
  FILTER NOT EXISTS {
    ?orphan rdfs:subClassOf ?parent .
    FILTER(?parent != owl:Thing)
    FILTER(!isBlank(?parent))
  }
  FILTER(?orphan != owl:Thing)
  FILTER(?orphan != owl:Nothing)
  FILTER(!isBlank(?orphan))
}
```

Target: zero results (except intentional top-level domain classes aligned
directly under BFO categories).

### 9. Disjointness Coverage

Sibling classes should be declared disjoint. Check for missing disjointness
(see `_shared/anti-patterns.md` #4).

### 10. Diff Review (for PRs)

```bash
robot diff --left previous.ttl --right ontology.ttl --format markdown
```

Review the diff for unintended changes before committing.

## Extended Quality Dimensions (recommended before release)

### 11. Accuracy Checks

#### 11.1 Syntactic Accuracy (`sh:datatype`)

Ensure SHACL shapes include datatype constraints for data properties:

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ex: <http://example.org/ontology/> .

ex:AgeShape
  a sh:NodeShape ;
  sh:targetClass ex:Person ;
  sh:property [
    sh:path ex:hasAge ;
    sh:datatype xsd:integer ;
    sh:minCount 1 ;
  ] .
```

Validate:

```bash
pyshacl -s shapes/ontology-shapes.ttl -i rdfs ontology.ttl -f human
```

#### 11.2 Semantic Accuracy

Cross-check a sample of definitions against authoritative domain sources
(standards, curated vocabularies, normative specs). Record source links in the
validation report for any changed definitions.

#### 11.3 Timeliness

Verify ontology metadata freshness (`dcterms:modified`):

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?ontology ?modified WHERE {
  ?ontology a owl:Ontology .
  OPTIONAL { ?ontology dcterms:modified ?modified }
}
```

Failure conditions:
- `dcterms:modified` missing.
- `dcterms:modified` older than the project's release cycle policy.

### 12. Coverage Checks

#### 12.1 Schema Completeness (missing definitions)

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

SELECT ?class WHERE {
  ?class a owl:Class .
  FILTER(!isBlank(?class))
  FILTER NOT EXISTS { ?class skos:definition ?def }
  FILTER NOT EXISTS { ?class obo:IAO_0000115 ?def }
}
```

#### 12.2 Property Completeness (missing domain/range)

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?property WHERE {
  ?property a ?type .
  VALUES ?type { owl:ObjectProperty owl:DatatypeProperty }
  OPTIONAL { ?property rdfs:domain ?domain }
  OPTIONAL { ?property rdfs:range ?range }
  FILTER(!BOUND(?domain) || !BOUND(?range))
}
```

#### 12.3 Population Completeness (when instances exist)

For populated ontologies/graphs, measure representative instance coverage for
high-priority classes (from CQs). Document gaps in the report.

#### 12.4 Representativeness

Run distribution checks for key dimensions (e.g., geography, time period,
subdomain). Flag obvious skew where it would bias CQ outcomes.

### 13. Succinctness Checks

#### 13.1 Intensional Conciseness (redundant subclass assertions)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?child ?parent WHERE {
  ?child rdfs:subClassOf ?parent .
  FILTER EXISTS {
    ?child rdfs:subClassOf ?mid .
    ?mid rdfs:subClassOf+ ?parent .
    FILTER(?mid != ?parent)
  }
}
```

Use this as a review query: some matches are intentional for readability.

#### 13.2 Extensional Conciseness (duplicate individuals)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?label (COUNT(DISTINCT ?ind) AS ?count) WHERE {
  ?ind rdfs:label ?label .
}
GROUP BY ?label
HAVING (COUNT(DISTINCT ?ind) > 1)
```

#### 13.3 Representational Conciseness (unused vocabulary)

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?class WHERE {
  ?class a owl:Class .
  FILTER NOT EXISTS { ?x a ?class }
  FILTER(!isBlank(?class))
}
```

Review against intended design before deleting terms.

### 14. Evaluation Dimensions (qualitative)

Capture release-readiness notes for:
- **Expressivity**: Is the chosen OWL profile sufficient for CQ demands?
- **Complexity**: Is the model understandable by target users/maintainers?
- **Granularity**: Is detail level appropriate for scope and CQ set?
- **Epistemological adequacy**: Does it reflect domain consensus?

## Check Execution Order

Run checks in this order (fast-fail):

1. **Logical consistency** — if the ontology is inconsistent, nothing else
   matters
2. **ROBOT report** — catches annotation-level issues quickly
3. **SHACL validation** — structural constraint checking
4. **CQ tests** — functional acceptance testing
5. **Coverage metrics** — informational, non-blocking
6. **Extended quality dimensions** — accuracy, coverage, succinctness, qualitative review before release

## SSSOM Mapping Checks (when applicable)

```bash
sssom validate mappings/source-to-target.sssom.tsv
```

- Valid SSSOM schema conformance
- All CURIEs resolvable via curie_map
- No self-mappings (subject = object)
- No duplicate mappings
- Every mapping has `mapping_justification`
- Confidence scores present for automated mappings

## Automation

These checks should be integrated into pre-commit hooks. The Justfile
provides `just check` for running all quality gates:

```bash
uv run ruff check .              # Python linting
uv run ruff format --check .     # Python formatting
uv run mypy src/                 # Type checking
uv run pytest                    # Python tests
# Plus ontology-specific checks above for any modified .ttl/.owl files
```

```


### `.claude/skills/_shared/namespaces.json` — Canonical prefix-to-IRI map

```json
{
  "prefixes": {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "dcterms": "http://purl.org/dc/terms/",
    "sh": "http://www.w3.org/ns/shacl#",
    "obo": "http://purl.obolibrary.org/obo/",
    "BFO": "http://purl.obolibrary.org/obo/BFO_",
    "RO": "http://purl.obolibrary.org/obo/RO_",
    "IAO": "http://purl.obolibrary.org/obo/IAO_",
    "OBI": "http://purl.obolibrary.org/obo/OBI_",
    "sssom": "https://w3id.org/sssom/",
    "semapv": "https://w3id.org/semapv/vocab/",
    "linkml": "https://w3id.org/linkml/",
    "oio": "http://www.geneontology.org/formats/oboInOwl#",
    "pav": "http://purl.org/pav/",
    "schema": "http://schema.org/",
    "prov": "http://www.w3.org/ns/prov#"
  },
  "notes": {
    "obo": "OBO PURL base — class IRIs are obo:{ONTOLOGY}_{ID} (e.g., obo:BFO_0000001)",
    "BFO": "Basic Formal Ontology — upper ontology (ISO 21838-2)",
    "RO": "OBO Relation Ontology — standard cross-ontology relations",
    "IAO": "Information Artifact Ontology — metadata properties (definitions, deprecation)",
    "oio": "OBO in OWL annotations — synonyms, xrefs, subsets",
    "sssom": "Simple Standard for Sharing Ontological Mappings",
    "semapv": "Semantic Mapping Vocabulary — mapping justification terms"
  }
}

```


---

# Appendix C: Root Project Instructions


### `CLAUDE.md` — Root CLAUDE.md

```markdown
# Ontology Engineering Workspace

## Project Overview

Programmatic Ontology Development (POD) workspace for building, maintaining,
and integrating OWL 2 ontologies using Python tooling and CLI tools. All
ontology modifications are performed through code, never by hand-editing
serialized files.

## Python Environment -- STRICTLY UV

**uv is the ONLY package manager for this project. Never use pip, pip-tools,
pipenv, poetry, conda, or any other package manager.**

### Commands

| Task | Command |
|------|---------|
| Install deps | `uv sync --group dev` |
| Add a dependency | `uv add <package>` |
| Add a dev dependency | `uv add --group dev <package>` |
| Remove a dependency | `uv remove <package>` |
| Run any Python command | `uv run <command>` |
| Run a script | `uv run python scripts/foo.py` |
| Run tests | `uv run pytest` |
| Run linter | `uv run ruff check .` |
| Run formatter | `uv run ruff format .` |
| Run type checker | `uv run mypy src/` |

### Rules

- ALWAYS prefix Python commands with `uv run` (e.g., `uv run pytest`, `uv run python`)
- NEVER run bare `python`, `pip`, or `pytest` -- always go through uv
- NEVER create requirements.txt -- dependencies live in pyproject.toml
- NEVER manually edit uv.lock -- it is auto-generated
- Use `uv add <pkg>` to add dependencies, not manual pyproject.toml edits
- Use dependency groups: production deps in `[project.dependencies]`,
  dev tools in `[dependency-groups] dev`

## Python Standards

- **Target**: Python 3.12+
- **Style**: Ruff for both linting AND formatting (no black, no isort, no flake8)
- **Types**: Use type hints on all function signatures. mypy for checking.
- **Pathlib**: Use `pathlib.Path` not `os.path` (enforced by Ruff PTH rules)
- **Modern syntax**: Use `|` union types not `Union`, `X | None` not `Optional[X]`,
  f-strings not `.format()`, `match` statements where appropriate
- **Imports**: sorted by Ruff (isort rules). First-party package is `ontology_skill`.
- **Line length**: 100 characters
- **Quotes**: double quotes
- **Docstrings**: Google style. Required on public modules, classes, and functions.

## Project Layout

```
ontologies/{name}/         # Self-contained ontology projects
  ├── {name}.ttl           #   Main ontology (TBox)
  ├── imports/             #   Imported declarations
  ├── shapes/              #   SHACL shapes
  ├── docs/                #   Specification, glossary, conceptual model
  ├── tests/               #   SPARQL CQ tests + Python unit tests
  ├── scripts/             #   Build scripts
  ├── mappings/            #   SSSOM mapping files
  └── release/             #   Frozen release artifacts
src/ontology_skill/        # Shared library code (importable package)
scripts/                   # General validation scripts
tests/unit/                # General tests (not ontology-specific)
tests/integration/         # Tests requiring external services
docs/                      # General research and methodology docs
sparql/                    # General shared SPARQL queries
.claude/skills/            # Ontology engineering skills (8 slash commands)
.claude/rules/             # Path-specific rules (auto-loaded by file context)
.claude/hooks/             # Safety hooks (ontology file protection)
```

## Ontology Engineering Skills

Eight skills map to the ontology engineering lifecycle. Invoke with
`/skill-name` or let Claude activate them automatically based on context:

| Skill | Phase | Use When |
|-------|-------|----------|
| `/ontology-requirements` | 1. Specification | Eliciting CQs, writing ORSD, generating test suites |
| `/ontology-scout` | 2. Acquisition | Finding reusable ontologies, ODPs, imports |
| `/ontology-conceptualizer` | 3. Conceptualization | Designing taxonomy, BFO alignment, anti-pattern review |
| `/ontology-architect` | 4. Formalization | Creating OWL axioms, ROBOT templates, KGCL patches |
| `/ontology-mapper` | 5. Integration | SSSOM mappings, lexmatch, cross-ontology alignment |
| `/ontology-validator` | 6. Evaluation | Reasoner, SHACL, CQ tests, ROBOT report |
| `/sparql-expert` | Cross-cutting | Query generation, validation, execution |
| `/ontology-curator` | Maintenance | Deprecation, versioning, releases |

Skills reference shared materials in `.claude/skills/_shared/` (methodology,
axiom patterns, anti-patterns, naming conventions, BFO categories, tool
decision tree). See `.claude/skills/CONVENTIONS.md` for the full standard.

## Quality Gates (run before committing)

```bash
uv run ruff check .              # Lint passes
uv run ruff format --check .     # Formatting consistent
uv run mypy src/                 # Type checks pass
uv run pytest                    # Tests pass
```

Or use the Justfile: `just check`

## Ontology Tool Strategy

Primary tools (use first):
- **ROBOT CLI**: build operations (merge, reason, report, convert, template, verify, diff)
- **oaklib** (`uv run runoak`): navigation, search, KGCL changes, lexmatch
- **KGCL**: human-reviewable change proposals

Secondary tools (specialized use):
- **OWLAPY**: complex DL axioms requiring OWL API (qualified cardinality, role chains)
- **owlready2**: rapid prototyping, ORM-style ontology interaction
- **LinkML**: schema-first modeling, polyglot artifact generation
- **rdflib**: RDF graph manipulation, serialization
- **pyshacl**: SHACL shape validation
- **sssom-py**: ontology mapping management

## Ontology Safety Rules

- NEVER hand-edit .owl or .ttl files -- use ROBOT, oaklib, or Python libraries
- ALWAYS run `robot reason` after structural changes
- ALWAYS run `robot report` before committing ontology changes
- NEVER delete ontology terms -- deprecate with `owl:deprecated true`
- Propose KGCL patches for human review before applying
- Validate SPARQL syntax before execution
- Check for existing terms (via oaklib search) before creating new ones

## Git Conventions

- Commits: `<type>(<scope>): <description>`
- Types: feat, fix, refactor, docs, test, chore
- Scope: ontology name or component
- Pre-commit hooks are installed -- they run Ruff lint, Ruff format, and mypy automatically

## Namespace Prefixes

Standard prefixes (always use):
- rdf, rdfs, owl, skos, sh, xsd, dcterms
- obo: http://purl.obolibrary.org/obo/
- BFO: http://purl.obolibrary.org/obo/BFO_
- RO: http://purl.obolibrary.org/obo/RO_
- IAO: http://purl.obolibrary.org/obo/IAO_

## Serialization

- Default format: Turtle (.ttl)
- Manchester Syntax for human review / LLM interaction
- Use CamelCase for class names, camelCase for properties
- All new classes require: rdfs:label, skos:definition, rdfs:subClassOf
- Follow genus-differentia pattern: "A [parent] that [differentia]"

```


---

# Appendix D: Practitioner Insights

This document is the in-repo record of real-world OBO Foundry / ontology engineering practice and where current skill guidance diverges from it.


### `docs/practitioner-insights.md` — 17 themes + priority gap table

```markdown
# Practitioner Insights: Real-World Ontology Engineering

Research findings from professional ontology engineering communities,
synthesized to ground our 8-skill workspace in actual practice rather
than academic theory.

**Date**: 2026-02-10
**Scope**: OBO Foundry, ROBOT/ODK, oaklib, SSSOM, LinkML, BFO, and
broader semantic web practitioner communities.

---

## Theme 1: The ODK is the De Facto Standard -- and We Are Not Using It

### Key Insight

The Ontology Development Kit (ODK) is not just a convenience tool; it
is the standard workflow for the entire OBO Foundry ecosystem and
increasingly for non-OBO ontologies. Virtually every actively maintained
OBO ontology uses the ODK Makefile-driven pattern. Our workspace
describes ROBOT commands in isolation but does not acknowledge or
integrate with the ODK pattern, which is how professionals actually
structure their projects.

### What Practitioners Actually Do

- ODK provides a Docker container with all tools pre-installed (ROBOT,
  oaklib, owltools, fastobo-validator, etc.). Teams run `sh run.sh make`
  and get reproducible builds regardless of local environment.
- The ODK generates a complete project skeleton including:
  - A `src/ontology/` directory with an `-edit.owl` working file
  - A `Makefile` (auto-generated from `{name}-odk.yaml`) handling the
    full release pipeline: merge, reason, report, release artifacts
  - Import management: `src/ontology/imports/` with `*_import.owl` and
    `*_terms.txt` files, auto-refreshed via make targets
  - CI/CD via GitHub Actions (`.github/workflows/`)
  - A `SPARQL/` directory for quality checks as SPARQL queries
- The edit-release split is fundamental: developers edit `{name}-edit.owl`
  and never touch release artifacts. The Makefile generates the release
  ontology by merging imports, running the reasoner, and producing
  multi-format outputs.
- Pattern-based term creation uses DOSDP (Dead Simple OWL Design
  Patterns) -- YAML pattern files that generate OWL from TSV data. This
  is more structured than raw ROBOT templates.

### Relevance to Our Skills

- **ontology-architect**: Should understand the ODK edit-release
  pattern, not just isolated ROBOT commands. The skill should know about
  `{name}-edit.owl` vs `{name}.owl` and the Makefile pipeline.
- **ontology-validator**: ODK already runs `robot report`, `robot reason`,
  and custom SPARQL checks in CI. Our validator should integrate with,
  not duplicate, existing ODK pipelines.
- **ontology-curator**: ODK has built-in release workflows. Our curator
  skill should understand `make prepare_release` and similar targets.

### Actionable Recommendations

1. Add an ODK awareness section to `ontology-architect/SKILL.md`
   explaining the edit-release pattern and when to use ODK vs standalone
   ROBOT commands.
2. Add DOSDP pattern support to the architect skill as an alternative to
   raw ROBOT templates for pattern-based term generation.
3. Consider adding `odk-integration.md` to `_shared/` documenting how
   our skills interact with an ODK-managed project vs a standalone
   project.

---

## Theme 2: ROBOT Template Gotchas That Trip Up Everyone

### Key Insight

ROBOT templates are powerful but have numerous subtle pitfalls that are
not documented in the official docs and are learned through painful
experience. The OBO community has accumulated significant tribal
knowledge about these issues.

### What Practitioners Actually Say

- **Column header syntax is fragile**: The second row of a ROBOT
  template defines the column semantics (e.g., `SC %`, `A rdfs:label`,
  `EC %`). A single typo or extra space causes silent failures or
  incorrect output rather than errors.
- **The `%` placeholder**: `SC %` means "SubClassOf with value from this
  column." But `SC 'has part' some %` (with an embedded relation) is
  where most mistakes happen -- the quoting and spacing must be exact.
- **Merge vs replace semantics**: `robot template --merge-before` and
  `--merge-after` control whether the template output is merged with the
  input ontology or replaces it. Getting this wrong can delete your
  entire ontology.
- **IRI resolution**: Template values must be full IRIs or CURIEs that
  resolve via the ontology's prefix declarations. Undeclared prefixes
  produce blank or invalid output.
- **Multi-value columns**: To put multiple superclasses or annotations
  on one term, use `SPLIT=|` in the column header syntax. This is not
  obvious from the documentation.
- **Empty cells**: Empty cells in required columns silently skip the row
  rather than raising an error. This can cause terms to be partially
  created (label but no definition, for example).
- **Annotation language tags**: To add a language tag to a label or
  definition, use `A rdfs:label@en` in the header. Without the tag,
  labels are untagged string literals, which causes problems with tools
  that filter by language.

### Relevance to Our Skills

- **ontology-architect**: The ROBOT template workflow (Step 3) needs
  explicit warnings about these pitfalls.
- **ontology-validator**: Should check for common ROBOT template output
  issues (missing language tags, partially-created terms).

### Actionable Recommendations

1. Add a "ROBOT Template Pitfalls" subsection to the architect skill
   with the specific gotchas listed above.
2. Add a SPARQL check for terms missing language tags on labels to the
   quality checklist.
3. Include a template validation step before running `robot template`:
   check that all column headers parse correctly and all CURIEs resolve.

---

## Theme 3: oaklib/runoak Is More Fragile Than Advertised

### Key Insight

oaklib is a powerful tool but has significant rough edges that
practitioners regularly encounter. The community reports frequent issues
with adapter inconsistencies, KGCL limitations, and version
compatibility.

### What Practitioners Actually Report

- **Adapter inconsistency**: oaklib supports multiple backends (SQLite,
  OLS, BioPortal, local OWL files, Ubergraph). But operations that work
  on one adapter may fail or return different results on another. For
  example, `runoak -i sqlite:obo:go search "cell"` returns different
  result formats than `runoak -i ols: search "cell"`.
- **KGCL implementation is incomplete**: Not all KGCL commands are fully
  implemented in oaklib. `obsolete` works reliably, but some complex
  operations like `create axiom` with full Manchester Syntax may fail or
  produce unexpected results. The KGCL parser is actively developed and
  can be version-sensitive.
- **SQLite adapter caching**: The `sqlite:obo:` adapter downloads and
  caches SQLite versions of OBO ontologies. These can become stale, and
  there is no automatic cache invalidation. Practitioners manually
  delete `~/.data/oaklib/` to force refresh.
- **Local file editing via runoak**: Applying KGCL changes to local
  `.ttl` or `.owl` files via oaklib can produce output in a different
  serialization format or with different prefix ordering than the input.
  This causes noisy diffs in version control.
- **Performance on large ontologies**: oaklib's SQLite adapter is fast
  for search and navigation but slow for bulk KGCL application. For
  large batch changes, practitioners often fall back to ROBOT or direct
  rdflib manipulation.

### Relevance to Our Skills

- **ontology-architect** and **ontology-curator**: Both skills recommend
  KGCL via oaklib for individual changes. They need to document
  limitations and fallback strategies.
- **ontology-scout**: The search workflow relies heavily on oaklib
  adapters and needs to account for adapter inconsistencies.

### Actionable Recommendations

1. Add an "oaklib Limitations" subsection to `_shared/tool-decision-tree.md`
   documenting known adapter issues and KGCL implementation gaps.
2. Add a fallback strategy: for KGCL commands that fail via oaklib,
   fall back to direct rdflib manipulation or ROBOT operations.
3. Document the serialization instability issue and recommend using
   `robot convert` after oaklib edits to normalize serialization before
   committing.
4. Add cache management guidance: when to clear the oaklib SQLite cache.

---

## Theme 4: SSSOM Mapping Is Harder Than the Spec Suggests

### Key Insight

The SSSOM specification is well-designed, but real-world mapping
practice involves challenges that the spec does not address. The
mapping-commons community and Monarch Initiative practitioners have
accumulated significant practical knowledge about mapping workflows.

### What Practitioners Actually Encounter

- **Lexical matching produces massive false positive rates**: oaklib's
  lexmatch generates many candidates, but in practice, 40-60% of
  matches at the 0.7-0.95 confidence level are incorrect. Labels match
  but meanings differ (homonyms across domains). The LLM verification
  step is not optional -- it is essential.
- **The exactMatch transitivity trap is real and dangerous**: If you
  declare A exactMatch B and B exactMatch C, then A exactMatch C is
  implied. In large mapping sets, this creates "mapping cliques" where
  terms from 5+ ontologies are all declared equivalent to each other.
  Practitioners regularly find that one bad mapping in a clique
  contaminates all the others.
- **SSSOM metadata is burdensome but critical**: In practice, teams
  often skip the `mapping_justification` field or use a single value
  for all mappings. This makes it impossible to audit mappings later.
  The SEMAPV vocabulary for justifications is not well-known.
- **Version management of mappings is unsolved**: When source or target
  ontologies release new versions, existing mappings can break silently.
  There is no standard workflow for "mapping maintenance." Teams
  typically re-run lexmatch and diff the results, which is error-prone.
- **Cross-species and cross-domain mappings are qualitatively different**:
  Mapping between two ontologies in the same domain (e.g., two disease
  ontologies) is very different from mapping across domains (e.g.,
  disease to phenotype). The predicate selection guidance needs to
  account for this.
- **The sssom-py tool has rough edges**: Validation can be overly strict
  on some fields and too lenient on others. The merge operation does not
  always handle conflicting metadata headers gracefully.

### Relevance to Our Skills

- **ontology-mapper**: This is our most practice-sensitive skill.
  Several workflow assumptions need updating.

### Actionable Recommendations

1. Increase the LLM verification threshold: change auto-accept from
   >= 0.95 to >= 0.98, and require exact label match AND compatible
   parent classes.
2. Add a mandatory "clique analysis" step after mapping: compute the
   transitive closure of exactMatch and flag cliques larger than 3 for
   human review.
3. Add a "Mapping Maintenance" workflow (Workflow 3) for handling
   ontology version updates -- the current Workflow 2 covers this but
   needs more detail on the full re-validation process.
4. Add cross-domain mapping guidance: when mapping across domains, default
   to `skos:relatedMatch` or `skos:closeMatch`, not `skos:exactMatch`.
5. Add sssom-py version pinning guidance and document known validation
   quirks.

---

## Theme 5: BFO Alignment Is the #1 Source of Practitioner Confusion

### Key Insight

BFO alignment is theoretically clean but practically contentious. The
OBO Foundry community has years of debates about specific alignment
decisions, and many of these have no clear resolution. Our BFO
categories reference is good but misses the areas of genuine ambiguity.

### What Practitioners Actually Debate

- **Disease as Disposition vs Process**: BFO classifies disease as a
  Disposition (a tendency toward pathological processes), but many
  practitioners (especially from clinical backgrounds) think of disease
  as something that "happens" (a process) or something you "have" (an
  independent continuant). The OGMS (Ontology for General Medical
  Science) interpretation is that a disease is a Disposition, but this
  is not universally accepted.
- **Organization as Object vs Object Aggregate**: BFO 2020 treats
  organizations as Objects, but many biomedical ontologies model them as
  Object Aggregates (collections of people). The correct answer depends
  on whether you consider the organization's identity to persist through
  member changes (Object) or to be constituted by its members
  (Aggregate). There is no consensus.
- **Information entities are always tricky**: The ICE (Information
  Content Entity) pattern from IAO requires modeling information as a
  Generically Dependent Continuant (GDC) that is concretized in a
  Specifically Dependent Continuant (SDC) which inheres in a Material
  Entity. This three-hop pattern is correct but confusing to implement.
  Many practitioners skip the concretization step.
- **Roles vs Dispositions**: The distinction between Role (exists due to
  social/contextual factors) and Disposition (exists due to physical
  makeup) is theoretically clear but practically ambiguous. Is "being
  toxic" a disposition or a role? Is "being a drug" a function, a
  disposition, or a role? These questions have been debated for years.
- **The "what about X?" problem**: Practitioners regularly encounter
  entities that do not fit cleanly into BFO categories: algorithms,
  software, social conventions, legal entities, money, prices. BFO was
  designed for natural science ontologies and can be awkward for social,
  legal, or computational domains.
- **BFO 2020 vs BFO 2.0**: There are differences between the published
  book (2015, based on BFO 2.0) and the ISO standard (BFO 2020). Some
  category names and relations have changed. Practitioners must know
  which version they are aligning to.

### Relevance to Our Skills

- **ontology-conceptualizer**: The BFO alignment step needs to
  acknowledge genuine ambiguity and provide guidance for disputed cases.
- **_shared/bfo-categories.md**: Needs to document the common
  controversy areas, not just the clean decision tree.

### Actionable Recommendations

1. Add a "Known Ambiguities" section to `bfo-categories.md` documenting
   the disease, organization, information, and role/disposition debates
   with the current community consensus (or lack thereof).
2. For each ambiguous case, provide the recommended default alignment
   AND the alternative, with guidance on when to choose each.
3. Add a note about BFO version differences (2015 book vs 2020 ISO).
4. For non-natural-science domains (social, legal, computational), add
   guidance on when BFO alignment may not be appropriate and what
   alternatives exist (DOLCE, GFO, or no upper ontology).

---

## Theme 6: The Import Problem Is Everyone's Biggest Pain Point

### Key Insight

Ontology imports are the #1 source of build failures, performance
problems, and maintenance burden in real-world ontology projects. The
OBO community has developed extensive workarounds, but the fundamental
problems remain.

### What Practitioners Actually Experience

- **Import chains can be enormous**: Importing one OBO ontology can pull
  in dozens of transitive imports, each with its own imports. GO imports
  pull in RO, BFO, CHEBI fragments, etc. A "simple" import can add
  hundreds of thousands of axioms.
- **Import freshness**: OBO ontologies are released on different
  schedules. When you import GO, you import a specific version. When GO
  updates and changes a term you depend on, your import is stale. The
  ODK handles this with `make refresh-imports`, but it can break things.
- **MIREOT vs STAR vs BOT extraction**: The extraction method matters
  enormously.
  - MIREOT: minimal (just the term and its ancestors). Fast but you lose
    sibling context and some axioms.
  - STAR: includes all axioms involving the term. More complete but can
    pull in unexpected classes.
  - BOT: bottom module, includes term and all ancestors. Good middle
    ground.
  Most practitioners use MIREOT for large ontologies and STAR for small
  ones, but the choice is project-specific.
- **Circular imports**: Occasionally, ontology A imports B which imports
  C which imports A (or a fragment of A). This causes reasoner failures
  and is surprisingly common in the OBO ecosystem.
- **Import curation files**: The `*_terms.txt` file pattern (one IRI per
  line listing which terms to import) is easy to maintain but easy to
  break. Adding a term that has been obsoleted in the source ontology
  causes silent failures during import refresh.

### Relevance to Our Skills

- **ontology-scout**: The module extraction step (Step 4) needs much
  more detail about extraction method trade-offs and import management.
- **ontology-architect**: Needs guidance on managing imports over time.
- **ontology-curator**: Needs an "import refresh" workflow.

### Actionable Recommendations

1. Add extraction method comparison table to the scout skill with
   concrete guidance on when to use MIREOT vs STAR vs BOT.
2. Add an "Import Management" section to the architect skill covering:
   term file maintenance, import refresh workflow, circular import
   detection.
3. Add an "Import Refresh" workflow to the curator skill for handling
   upstream ontology updates.
4. Add a SPARQL check to the validator for detecting references to
   obsoleted imported terms.

---

## Theme 7: Reasoner Performance Is a Real Engineering Constraint

### Key Insight

Reasoner performance is not just a "nice to have" concern -- it is a
hard engineering constraint that shapes ontology design decisions.
Practitioners regularly make modeling trade-offs specifically to keep
reasoning tractable.

### What Practitioners Actually Do

- **ELK is the workhorse, not HermiT**: In practice, most OBO ontologies
  use ELK as their primary reasoner because HermiT is too slow on large
  ontologies (10K+ classes). ELK handles the OWL 2 EL profile, which
  covers most taxonomic reasoning needs. HermiT is reserved for
  pre-release validation or small ontologies.
- **Reasoner timeout is a common CI failure**: Many ontology CI pipelines
  have a 30-60 minute timeout. Complex ontologies (especially those with
  qualified cardinality restrictions or heavy use of universal
  restrictions) can exceed this. Teams restructure axioms to stay within
  time budgets.
- **Materialization vs on-demand**: Some teams pre-compute the reasoner
  output ("materialize" inferred axioms into the release file) while
  others ship the asserted ontology and let consumers reason. The ODK
  default is to materialize (robot reason --output includes inferred
  axioms).
- **Incremental reasoning is not widely supported**: Unlike compilers,
  OWL reasoners typically re-classify the entire ontology even for a
  single axiom change. This makes the "reason after every change"
  guidance impractical for interactive development. In practice, teams
  reason at commit time (pre-commit hook or CI), not after every edit.
- **Profile violations cause silent degradation**: If you use OWL 2 DL
  features (like qualified cardinality) but run ELK (which only supports
  EL), the reasoner silently ignores the unsupported axioms. This can
  cause missed inferences that are hard to debug.

### Relevance to Our Skills

- **ontology-architect**: The "ALWAYS run reasoner after changes"
  guidance is aspirational but impractical for large ontologies during
  active development. Need to provide more nuanced guidance.
- **ontology-validator**: Needs to understand reasoner limitations and
  profile-specific behavior.
- **_shared/tool-decision-tree.md**: Already has reasoner selection
  guidance but needs the performance context.

### Actionable Recommendations

1. Refine the "always run reasoner" guidance: distinguish between
   lightweight CI reasoning (ELK, every commit) and heavyweight
   validation reasoning (HermiT, pre-release only).
2. Add timing expectations: ELK on a 10K-class ontology takes seconds;
   HermiT on the same may take minutes to hours.
3. Add guidance on profile compliance checking: recommend running
   `robot validate-profile` (or equivalent) to detect axioms that will
   be ignored by the chosen reasoner.
4. Document the materialization decision: when to include inferred
   axioms in the release vs ship asserted-only.

---

## Theme 8: CI/CD for Ontologies Is Not Like CI/CD for Code

### Key Insight

While our workspace correctly advocates for CI/CD, ontology CI/CD has
unique characteristics that differ from software CI/CD in important
ways. The OBO community has evolved specific patterns.

### What Practitioners Actually Implement

- **GitHub Actions are standard**: Almost all OBO ontologies use GitHub
  Actions for CI. The typical workflow:
  1. On PR: run `robot report`, check for ERRORs
  2. On PR: run `robot reason`, check consistency
  3. On PR: run custom SPARQL checks
  4. On merge to main: run full release pipeline
  5. On tag: create GitHub release with multi-format artifacts
- **The "dashboard" pattern**: The OBO Foundry runs a community-wide
  dashboard (http://dashboard.obofoundry.org/) that scores every OBO
  ontology on quality metrics. Ontologies that fall below thresholds get
  flagged. This is a powerful social incentive for quality.
- **Pre-commit hooks for ontologies are rare**: Unlike code linting,
  ontology pre-commit hooks are uncommon because reasoning takes too
  long. Most teams rely on CI rather than pre-commit.
- **Diff-based review is hard**: `robot diff` produces output, but
  reviewing OWL diffs is much harder than reviewing code diffs. Changes
  to blank nodes, IRI reordering, and serialization changes create noise.
  Teams use `robot diff --format markdown` for human-readable output
  but it still requires ontology expertise to review.
- **Release management follows OBO conventions**: OBO ontologies use
  date-based versioning (YYYY-MM-DD), not semver. The release artifact
  is always at a stable PURL (e.g., http://purl.obolibrary.org/obo/go.owl)
  with versioned IRIs for each release.

### Relevance to Our Skills

- **ontology-validator**: Should understand the GitHub Actions patterns
  and dashboard metrics.
- **ontology-curator**: The release pipeline should follow OBO
  conventions (date-based versioning, PURL management).
- **CLAUDE.md**: Pre-commit hook expectations need to be realistic.

### Actionable Recommendations

1. Add a GitHub Actions workflow template to the workspace (or
   reference the ODK-generated one).
2. Document the OBO dashboard metrics and how they map to our quality
   checklist.
3. Revise expectations about pre-commit hooks: Python linting hooks are
   fine, but ontology reasoning should be in CI, not pre-commit.
4. Add `robot diff --format markdown` as the standard diff format for
   PR descriptions.
5. Document OBO date-based versioning alongside semver in the curator
   skill (currently only semver is documented).

---

## Theme 9: LinkML Is Great for Data Models, Awkward for Rich Ontologies

### Key Insight

LinkML is increasingly popular but has a specific sweet spot. The
community has learned where it excels and where it causes problems.
Our workspace treats it as a general-purpose ontology tool, which
overstates its scope.

### What Practitioners Actually Report

- **LinkML excels at data modeling**: It is outstanding for defining
  data schemas that need to be expressed in multiple formats (JSON
  Schema, SHACL, Python dataclasses, SQL DDL). The Monarch Initiative
  and NMDC use it extensively for data models.
- **LinkML is not ideal for rich OWL ontologies**: The OWL generator
  from LinkML produces relatively flat ontologies. Complex axiom
  patterns (qualified cardinality, property chains, complex equivalent
  class expressions) cannot be expressed in LinkML YAML and require
  post-processing with ROBOT or OWLAPY.
- **Schema-first vs ontology-first is a real design choice**: Some
  projects start with LinkML and generate OWL (schema-first). Others
  start with OWL and generate data validation artifacts. The choice
  depends on whether the primary artifact is a data schema or a domain
  ontology.
- **LinkML and OWL can coexist**: Some projects use LinkML for the data
  model (ABox validation) and a separate hand-crafted OWL ontology for
  the domain model (TBox). The two are linked via prefix alignment.
- **LinkML versioning and ecosystem churn**: The LinkML toolchain is
  actively evolving, and breaking changes between versions are not
  uncommon. Practitioners pin versions carefully.

### Relevance to Our Skills

- **ontology-architect**: The LinkML step (Step 6) is positioned as
  "for new ontologies" but should be more clearly scoped.
- **_shared/tool-decision-tree.md**: LinkML escalation criteria need
  refinement.

### Actionable Recommendations

1. Refine LinkML guidance in the architect skill: recommend it for data
   model schemas (ABox validation artifacts) rather than rich TBox
   ontologies.
2. Add a note that LinkML-generated OWL typically needs enrichment with
   ROBOT or OWLAPY for complex axioms.
3. In the tool decision tree, clarify that LinkML is best when the
   primary deliverable is a data schema, not a formal ontology.

---

## Theme 10: Domain/Range Is the Most Misunderstood OWL Feature

### Key Insight

Our anti-patterns document (#10) correctly identifies domain/range
overcommitment, but the depth of confusion in the community suggests
this needs even more emphasis. This is the single most common "gotcha"
that practitioners encounter.

### What Practitioners Actually Get Wrong

- **Domain/range as constraints vs inference**: Most newcomers (and many
  experienced practitioners) treat `rdfs:domain` and `rdfs:range` as
  constraints (like SQL foreign keys). They are not. They are inference
  rules. If you declare `prescribes rdfs:domain Physician`, then ANY
  subject of a `prescribes` triple is inferred to be a Physician -- even
  if it is a nurse or a veterinarian.
- **The SHACL alternative is underused**: When you actually want to
  constrain usage, SHACL `sh:class` on a property shape is the correct
  approach. But many ontology engineers do not know SHACL well enough
  to use it for this purpose.
- **Global vs local restrictions**: OWL domain/range are global (apply
  everywhere the property is used). Class-level restrictions
  (SubClassOf hasP some/only C) are local (apply only to that class).
  This distinction is fundamental but poorly taught.
- **The "too narrow domain" cascade**: Setting domain to a leaf class
  causes everything that uses the property to be classified as that leaf
  class. This is a major source of unexpected unsatisfiable classes.

### Relevance to Our Skills

- **ontology-conceptualizer**: The property design step needs explicit
  guidance on when to use domain/range vs local restrictions vs SHACL.
- **ontology-architect**: Needs concrete examples of the domain/range
  pitfall and the correct alternatives.
- **ontology-validator**: Should detect overly narrow domain/range
  declarations.

### Actionable Recommendations

1. Elevate the domain/range warning from anti-pattern #10 to a
   prominent callout in both the conceptualizer and architect skills.
2. Add a decision procedure: "Do you want inference or validation? If
   inference, use OWL domain/range. If validation, use SHACL sh:class."
3. Add a SPARQL query to the quality checklist that detects properties
   with domain/range set to leaf classes (high risk of misclassification).

---

## Theme 11: Competency Questions Are Often Cargo-Culted

### Key Insight

While CQ-driven development is methodologically sound, in practice many
teams treat CQs as a checkbox exercise rather than a genuine design
driver. Our requirements skill is strong but could benefit from
awareness of how CQs fail in practice.

### What Practitioners Actually Experience

- **CQs are written after the ontology, not before**: Many teams build
  the ontology first and then retroactively write CQs to justify it.
  This defeats the purpose of CQ-driven design.
- **CQs are too vague to be testable**: "What types of instruments
  exist?" is answerable by anything with a class hierarchy. Good CQs
  are specific enough to fail: "Which string instruments require a bow?"
- **CQ-to-SPARQL translation is non-trivial**: Even experienced
  practitioners struggle to formalize natural language CQs as SPARQL.
  The gap between "What is X?" and a correct SPARQL query is large.
  LLM assistance here is genuinely valuable.
- **CQ tests are rarely maintained**: Teams write CQ SPARQL tests during
  initial development but do not update them as the ontology evolves.
  Tests become stale and are eventually ignored.
- **CQ prioritization is political**: MoSCoW prioritization depends on
  stakeholder power dynamics. The most vocal stakeholder's CQs become
  "Must Have" regardless of actual importance.

### Relevance to Our Skills

- **ontology-requirements**: The CQ workflow is well-structured but
  should include warnings about these failure modes.

### Actionable Recommendations

1. Add an explicit process check: CQs must be written BEFORE
   conceptualization begins. Include a gate/checkpoint.
2. Add CQ quality criteria: every CQ must be specific enough that a
   reasonable SPARQL query could return zero results (i.e., it can fail).
3. Emphasize that the LLM (our agent) is well-suited for CQ-to-SPARQL
   translation -- this is a high-value use case for the skill.
4. Add CQ maintenance guidance: CQ tests must be reviewed and updated
   with every ontology version change (link to curator skill).
5. Add a note about prioritization bias and recommend involving multiple
   stakeholders independently before consolidation.

---

## Theme 12: OWLAPY/owlready2 Are Not Widely Used in the OBO Community

### Key Insight

Our workspace treats OWLAPY and owlready2 as key secondary tools, but
in the OBO community, they are rarely used. The community relies almost
entirely on ROBOT + oaklib + rdflib for programmatic ontology work.

### What Practitioners Actually Use

- **ROBOT + oaklib cover 95% of use cases**: Between ROBOT templates,
  ROBOT operations, and oaklib KGCL, there is very little need for
  Python-level OWL manipulation in typical ontology engineering.
- **rdflib is the Python escape hatch**: When practitioners need to
  manipulate ontologies programmatically in Python, they typically use
  rdflib directly (working at the triple level) rather than OWLAPY or
  owlready2 (working at the axiom level).
- **OWLAPY has a small community**: The OWLAPY project (dice-group) is
  primarily used by the DICE research group for ML-on-ontologies work,
  not by the broader ontology engineering community.
- **owlready2 is used for specific tasks**: owlready2 has a niche for
  Python applications that need to load and reason over ontologies at
  runtime (e.g., clinical decision support). It is not commonly used
  for ontology building.
- **The JVM dependency is a blocker**: OWLAPY requires a JVM, which
  adds complexity to Python environments. Many practitioners avoid it
  for this reason alone.

### Relevance to Our Skills

- **ontology-architect**: The tool decision tree correctly positions
  OWLAPY and owlready2 as secondary, but the OWLAPY code example in
  the architect skill may set unrealistic expectations.
- **_shared/tool-decision-tree.md**: The escalation to OWLAPY should
  note that most practitioners would use rdflib or ROBOT instead.

### Actionable Recommendations

1. Add rdflib as a more prominent secondary tool for programmatic OWL
   manipulation. Show a rdflib example for adding complex axioms
   alongside (or instead of) the OWLAPY example.
2. Note in the tool decision tree that OWLAPY is primarily for use cases
   requiring the full OWL API (e.g., computing entailments, working with
   DL learners) rather than for building ontologies.
3. Keep owlready2 for the specific use case of runtime ontology
   interaction in Python applications.

---

## Theme 13: SHACL Adoption Is Growing But SHACL Shape Authoring Is Hard

### Key Insight

SHACL is increasingly used in ontology workflows, but writing good SHACL
shapes is a distinct skill that ontology engineers often lack. The gap
between "we should use SHACL" and "here are our shapes" is significant.

### What Practitioners Actually Report

- **SHACL shape libraries are rare**: Unlike OWL ontologies (which have
  extensive reuse ecosystems), reusable SHACL shape libraries are still
  uncommon. Each project writes shapes from scratch.
- **SHACL-SPARQL is powerful but complex**: Advanced SHACL shapes
  (using `sh:sparql`) can express arbitrary constraints, but they are
  harder to write and debug than simple property shapes.
- **SHACL targets are tricky**: Getting the targeting right (which nodes
  should a shape apply to?) is error-prone. `sh:targetClass` seems
  simple but interacts with OWL reasoning in non-obvious ways (does it
  target asserted or inferred class membership?).
- **pyshacl has limitations**: pyshacl is the standard Python SHACL
  validator but can be slow on large graphs and does not support all
  SHACL-SPARQL features. Some teams use Apache Jena's SHACL validator
  instead.
- **OWL and SHACL can conflict**: It is possible to write SHACL shapes
  that contradict OWL axioms (e.g., SHACL says max 1, OWL says
  functional). Understanding the interaction between the two systems
  requires expertise in both.

### Relevance to Our Skills

- **ontology-architect**: The skill mentions generating SHACL shapes
  but does not provide templates or patterns.
- **ontology-validator**: Uses pyshacl but does not discuss its
  limitations.

### Actionable Recommendations

1. Add a "Standard SHACL Shape Templates" section to the architect skill
   or a new `_shared/shacl-patterns.md` reference, with copy-paste
   templates for common shapes (label required, definition recommended,
   no orphans, datatype constraints).
2. Document pyshacl limitations in the validator skill and provide Jena
   SHACL as an alternative for large graphs.
3. Add guidance on SHACL-OWL interaction: "SHACL validates data; OWL
   infers from data. Run reasoning first, then validate the
   reasoned output."

---

## Theme 14: The "Never Hand-Edit" Rule Has Practical Exceptions

### Key Insight

Our workspace has a strict "never hand-edit .owl or .ttl files" rule.
While this is a good default, practitioners in the OBO community
regularly hand-edit Turtle files for specific tasks, and the tools
sometimes require it.

### What Practitioners Actually Do

- **Quick annotation fixes**: Fixing a typo in a label or adding a
  missing annotation is often fastest done by editing the Turtle file
  directly. Running a full ROBOT pipeline for a one-character label
  fix is overhead that slows down development.
- **ODK edit files are meant to be edited**: The `{name}-edit.owl` file
  in an ODK project is the working copy. While ODK encourages using
  Protege or ROBOT for structural changes, small annotation edits are
  commonly done directly.
- **Prefix management**: Prefix declarations in Turtle files sometimes
  need manual adjustment, especially after ROBOT operations that add or
  reorder prefixes.
- **Merge conflict resolution**: When two developers edit the same
  ontology file, Git merge conflicts must be resolved manually. This
  inherently involves hand-editing the file.

### Relevance to Our Skills

- **CONVENTIONS.md** and **CLAUDE.md**: The absolute prohibition on
  hand-editing is too strict for practical use.

### Actionable Recommendations

1. Refine the rule to: "Never hand-edit structural axioms (SubClassOf,
   EquivalentClass, DisjointClasses, property assertions). Annotation
   edits (labels, definitions, synonyms) may be hand-edited if followed
   by `robot report` validation."
2. This keeps the safety benefit (structural integrity) while allowing
   practical flexibility for metadata.

---

## Theme 15: LLM-Assisted Ontology Engineering Is Emerging but Immature

### Key Insight

The use of LLMs for ontology engineering is a hot topic but is still in
early stages. The OBO Academy has introduced Claude Code tutorials, and
several research groups are experimenting with LLM-based ontology tools.

### What Practitioners Are Exploring

- **Term suggestion and definition writing**: LLMs are good at
  suggesting terms, writing genus-differentia definitions, and
  identifying synonyms. This is the most mature use case.
- **CQ-to-SPARQL translation**: LLMs can translate natural language CQs
  to SPARQL with reasonable accuracy, especially with few-shot examples.
  This is our requirements skill's strongest LLM use case.
- **Mapping verification**: LLMs can evaluate mapping pairs (given
  labels, definitions, and hierarchical context) and provide predicate
  recommendations. This is the mapper skill's core LLM application.
- **Anti-pattern detection**: LLMs can review ontology structures and
  identify potential anti-patterns, though they need to be guided with
  specific patterns to look for.
- **What LLMs struggle with**: LLMs have difficulty with:
  - Complex DL axiom construction (they hallucinate axiom syntax)
  - Reasoner behavior prediction (they cannot mentally simulate a
    reasoner)
  - Large-scale ontology understanding (they lose context with
    thousands of classes)
  - Nuanced BFO alignment (they default to common-sense classification
    rather than BFO-specific categories)
- **The "confident but wrong" problem**: LLMs generate ontology axioms
  with high confidence even when the axioms are logically incorrect.
  This makes the post-generation validation step absolutely critical.

### Relevance to Our Skills

- **All skills**: Understanding where LLM assistance adds value and
  where it requires verification.

### Actionable Recommendations

1. For each skill, document the specific LLM-assisted steps and the
   specific verification requirements for LLM-generated output.
2. Emphasize that LLM-generated axioms MUST be validated by the reasoner
   -- this is not optional.
3. Add "LLM Verification Required" markers in skill workflows where
   the agent generates ontology content (axioms, definitions, mappings).
4. For BFO alignment, provide the decision tree IN the prompt context
   rather than relying on the LLM's pre-trained knowledge of BFO.

---

## Theme 16: Multi-Ontology Projects Need Explicit Coordination

### Key Insight

Real-world ontology projects rarely involve a single ontology. Most
projects work with 5-20 ontologies (imports, mappings, bridge
ontologies) simultaneously. Our workspace's Pipeline A (new ontology)
assumes a single-ontology focus.

### What Practitioners Actually Manage

- **Import dependency graphs**: A project ontology typically imports
  from 3-10 external ontologies. Managing these imports (version
  pinning, refresh cycles, term list curation) is a significant ongoing
  effort.
- **Bridge ontologies**: When two ontologies need to be connected but
  neither should import the other, a bridge ontology provides the
  linking axioms. Bridge ontology maintenance is a distinct task.
- **Ontology registries**: Projects need to track which ontologies they
  use, which version, and what terms they import. This metadata is
  typically managed in the ODK's `{name}-odk.yaml` configuration.
- **Cross-ontology consistency**: When multiple ontologies are loaded
  together (for reasoning or querying), inconsistencies can arise from
  conflicting axioms across ontologies. This is hard to debug.

### Relevance to Our Skills

- **ontology-scout** and **ontology-mapper**: These skills handle
  cross-ontology work but could benefit from more explicit coordination
  guidance.
- **ontology-curator**: Needs import dependency management.

### Actionable Recommendations

1. Add a "Multi-Ontology Coordination" section to the curator skill
   covering import dependency tracking, bridge ontology maintenance,
   and cross-ontology consistency checking.
2. Consider a workspace-level `imports-manifest.yaml` tracking all
   external ontology dependencies, versions, and refresh dates.

---

## Theme 17: Documentation and Communication Matter More Than Tools

### Key Insight

The most common complaint from ontology practitioners is not about tools
but about communication: between ontology engineers and domain experts,
between ontology consumers and producers, and between team members
working on the same ontology.

### What Practitioners Actually Struggle With

- **Domain experts cannot read OWL**: Manchester Syntax is the most
  readable OWL serialization, but it still requires training. Most
  domain experts can only review natural language definitions, not
  axioms.
- **Ontology documentation is typically poor**: Most ontologies have
  minimal documentation beyond labels and definitions. WIDOCO
  (auto-generated HTML docs) helps but produces verbose output that
  domain experts do not read.
- **Change communication is hard**: When an ontology changes (especially
  deprecations), downstream consumers need to be notified. There is no
  standard notification mechanism.
- **Visualization is essential for review**: Tree views, graph
  visualizations, and tabular summaries are how domain experts actually
  review ontologies. Raw Turtle or OWL files are not reviewable.

### Relevance to Our Skills

- **ontology-conceptualizer**: The conceptual model should be in a
  format that domain experts can review (YAML, tables, diagrams).
- **ontology-curator**: Change communication needs formalization.

### Actionable Recommendations

1. For each skill that produces output, specify the "domain expert
   review format" alongside the machine-readable format. For example:
   the conceptualizer produces `conceptual-model.yaml` (machine) AND
   a summary table (human).
2. Add visualization commands to the conceptualizer and architect skills
   (oaklib `tree` command, mermaid diagrams from SPARQL queries).
3. Add a "Release Notes" template to the curator skill that is written
   for ontology consumers (not developers).

---

## Summary: Top Priority Gaps in Our Current Skills

Ranked by impact on real-world usability:

| # | Gap | Affected Skills | Effort |
|---|-----|----------------|--------|
| 1 | No ODK awareness or integration | architect, validator, curator | Medium |
| 2 | ROBOT template gotchas undocumented | architect | Low |
| 3 | oaklib/KGCL limitations undocumented | architect, curator | Low |
| 4 | Import management underspecified | scout, architect, curator | Medium |
| 5 | BFO alignment ambiguities not acknowledged | conceptualizer, bfo-categories | Low |
| 6 | SSSOM mapping challenges underestimated | mapper | Medium |
| 7 | Reasoner performance not contextualized | architect, validator | Low |
| 8 | Domain/range confusion needs more emphasis | conceptualizer, architect | Low |
| 9 | LinkML scope too broadly stated | architect, tool-decision-tree | Low |
| 10 | SHACL authoring guidance missing | architect, validator | Medium |
| 11 | "Never hand-edit" rule too absolute | CONVENTIONS.md | Low |
| 12 | CI/CD patterns need GitHub Actions examples | validator, curator | Medium |
| 13 | CQ failure modes undocumented | requirements | Low |
| 14 | OWLAPY/owlready2 prominence overstated | architect, tool-decision-tree | Low |
| 15 | Multi-ontology coordination missing | curator, scout | Medium |
| 16 | LLM limitations for ontology work undocumented | all skills | Low |
| 17 | OBO date-based versioning missing | curator | Low |

---

## Cross-Reference: How Findings Map to Our 8 Skills

| Skill | Themes with Actionable Impact |
|-------|-------------------------------|
| ontology-requirements | 11 (CQ cargo-culting) |
| ontology-scout | 1 (ODK), 6 (imports), 16 (multi-ontology) |
| ontology-conceptualizer | 5 (BFO ambiguity), 10 (domain/range), 17 (documentation) |
| ontology-architect | 1 (ODK), 2 (ROBOT gotchas), 3 (oaklib), 7 (reasoner), 9 (LinkML), 12 (OWLAPY), 13 (SHACL), 14 (hand-edit) |
| ontology-mapper | 4 (SSSOM challenges) |
| ontology-validator | 1 (ODK), 7 (reasoner), 8 (CI/CD), 13 (SHACL) |
| sparql-expert | (no major gaps from practitioner perspective) |
| ontology-curator | 1 (ODK), 6 (imports), 8 (CI/CD), 16 (multi-ontology), 17 (documentation) |

```


---

# Appendix E: Auto-Loading Rules (Verbatim)

These files attach to file-path patterns and get injected into agent context when relevant files are opened.


### `.claude/rules/ontology-safety.md` — ontology-safety.md rule

```markdown
---
paths:
  - "ontologies/**/*.ttl"
  - "ontologies/**/*.owl"
  - "ontologies/**/*.rdf"
---

# Ontology Safety Rules (Non-Negotiable)

These rules apply to ALL ontology file modifications. Violations are never acceptable.

1. **Never hand-edit structural axioms** (SubClassOf, EquivalentClass, DisjointClasses,
   property assertions) in `.owl`, `.ttl`, or `.rdf` files — always use ROBOT, oaklib,
   rdflib, or Python build scripts
2. **Always run the reasoner** (`robot reason`) after any structural change
3. **Always run quality report** (`robot report`) before committing ontology changes
4. **Never delete terms** — deprecate with `owl:deprecated true` and provide a
   replacement pointer (`obo:IAO_0100001`)
5. **Propose KGCL patches** for human review before applying changes to shared ontologies
6. **Validate SPARQL syntax** before execution
7. **Check for existing terms** (via `runoak search`) before creating new ones
8. **Read before modifying** — always read the existing ontology file before making changes
9. **Back up before bulk operations** — create a checkpoint before ROBOT template or
   batch KGCL application

## Tool Priority

Always try primary tools first:
1. **ROBOT CLI** — build operations (merge, reason, report, template, verify, diff)
2. **oaklib** (`uv run runoak`) — navigation, search, KGCL changes, lexmatch
3. **KGCL** — human-reviewable change proposals
4. **rdflib** — programmatic triple manipulation (as in build scripts)

Escalate to secondary tools (OWLAPY, owlready2, LinkML) only when primary tools
lack the required expressivity.

## Serialization Standards

- Default format: Turtle (`.ttl`)
- CamelCase for class names, camelCase for properties
- All new classes require: `rdfs:label`, `skos:definition`, `rdfs:subClassOf`
- Follow genus-differentia pattern for definitions: "A [parent] that [differentia]"
- Use standard namespace prefixes (see `.claude/skills/_shared/namespaces.json`)

```


### `.claude/rules/ontology-build-scripts.md` — ontology-build-scripts.md rule

```markdown
---
paths:
  - "scripts/**/*.py"
  - "ontologies/*/scripts/**/*.py"
  - "src/ontology_skill/**/*.py"
---

# Ontology Build Script Conventions

When modifying Python scripts that generate or manipulate ontology files:

## Methodology

- Follow the ontology engineering lifecycle: Specification > Acquisition > Conceptualization > Formalization > Integration > Evaluation
- Use the skill workflows defined in `.claude/skills/` for the appropriate phase
- Consult `.claude/skills/CONVENTIONS.md` for cross-skill handoff specifications

## Build Script Patterns

- Use `rdflib` for programmatic triple manipulation in build scripts
- Bind standard prefixes via a shared helper (see `bind_common_prefixes()`)
- Keep TBox (schema), ABox (data), reference individuals, and SHACL shapes in separate graphs/files
- Derive relationships programmatically where possible (e.g., `publishedBy` from URL domain)
- Document all changes in the KGCL change log (`ontologies/{name}/{name}-changes.kgcl`)

## Quality Gates

After modifying build scripts, always run:
```bash
uv run python ontologies/{name}/scripts/build.py  # Rebuild artifacts
uv run pytest ontologies/{name}/tests/             # Run tests
uv run ruff check .                           # Lint
uv run ruff format --check .                  # Format check
```

```


### `.claude/rules/ontology-testing.md` — ontology-testing.md rule

```markdown
---
paths:
  - "ontologies/*/tests/**/*.sparql"
  - "ontologies/*/tests/**/*.py"
  - "ontologies/*/tests/**/*.yaml"
  - "ontologies/*/docs/competency-questions.yaml"
---

# Ontology Testing Conventions (TDOD)

Follow Test-Driven Ontology Development (Keet & Lawrynowicz, 2016):

## Competency Questions

- Every ontology capability must be expressed as a competency question (CQ)
- CQs are formalized as SPARQL queries in `ontologies/{name}/tests/cq-{NNN}.sparql`
- CQs must be registered in both:
  - `ontologies/{name}/docs/competency-questions.yaml` (full specification)
  - `ontologies/{name}/tests/cq-test-manifest.yaml` (test runner manifest)
- CQ SPARQL tests must be added to the parametrized test list in
  `ontologies/{name}/tests/test_ontology.py`

## SPARQL Query Standards

- All queries must include PREFIX declarations (no implicit prefixes)
- Use the canonical `enews:` prefix for the energy-news namespace
- Validate syntax before committing
- SELECT queries must return non-empty results on sample data
- ASK queries document expected boolean result

## SHACL Validation

- Shapes live in `ontologies/{name}/shapes/{name}-shapes.ttl`
- SHACL conformance test must pass with `inference="none"`
- SPARQL-based constraints (`sh:SPARQLConstraint`) for cross-property validation

## Test Organization

- `tests/unit/` — Fast tests (rdflib in-memory graphs, no external services)
- `tests/integration/` — Tests requiring ROBOT, reasoners, or endpoints
- Parametrize CQ tests where possible for maintainability

```


---

# Appendix F: Safety Hooks (Verbatim)


### `.claude/hooks/post-ontology-write.sh`

```
#!/usr/bin/env bash
# Claude Code PostToolUse hook: validate Turtle syntax after writes.
# If Claude writes a .ttl file, immediately check it parses correctly.

set -euo pipefail

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Only validate .ttl files
if [[ "$FILE_PATH" =~ \.ttl$ ]] && [[ -f "$FILE_PATH" ]]; then
  # Quick rdflib parse check
  RESULT=$(uv run python -c "
from rdflib import Graph
try:
    Graph().parse('$FILE_PATH', format='turtle')
    print('OK')
except Exception as e:
    print(f'FAIL: {e}')
" 2>&1)

  if [[ "$RESULT" == FAIL* ]]; then
    jq -n --arg reason "Turtle syntax error in $FILE_PATH: $RESULT. Please fix the syntax." '{
      decision: "block",
      reason: $reason
    }'
    exit 0
  fi
fi

exit 0

```


### `.claude/hooks/guard-sed-ontology.sh`

```
#!/usr/bin/env bash
# Claude Code PreToolUse hook: block sed/awk/perl edits to ontology files.
# This enforces Safety Rule #1: never hand-edit .owl or .ttl files.

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [[ -z "$COMMAND" ]]; then
  exit 0
fi

# Check if command uses text manipulation tools targeting ontology files
if echo "$COMMAND" | grep -qE '(sed|awk|perl\s+-[pe])' && \
   echo "$COMMAND" | grep -qE '\.(ttl|owl|rdf|ofn|owx)'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Safety Rule #1: Never hand-edit ontology files (.ttl, .owl). Use ROBOT, oaklib (runoak apply), or Python libraries instead. See skills/_shared/tool-decision-tree.md for the right tool."
    }
  }'
  exit 0
fi

exit 0

```


### `.claude/hooks/protect-ontology-files.sh`

```
#!/usr/bin/env bash
# Claude Code PreToolUse hook: warn when directly editing ontology files.
# Fires on Edit and Write tool calls targeting .ttl/.owl/.rdf files.
# Returns a warning (not a block) so bootstrapping new ontologies still works.

set -euo pipefail

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only check Edit and Write tools
if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Check if the file is an ontology serialization format
if [[ "$FILE_PATH" =~ \.(ttl|owl|rdf|xml)$ ]]; then
  # If it's under ontologies/, warn about using programmatic tools
  if [[ "$FILE_PATH" =~ ontologies/ ]]; then
    jq -n '{
      hookSpecificOutput: {
        additionalContext: "REMINDER: Ontology files should be modified via ROBOT, oaklib (runoak), or Python libraries — not direct file edits. If you are bootstrapping a new ontology header, this is acceptable. Otherwise, use the programmatic tools from the tool-decision-tree."
      }
    }'
    exit 0
  fi
fi

exit 0

```


---

# Appendix G: Active Ontology Reference — skygest-energy-vocab

Selected documents from the mature exemplar ontology. These show what a real POD project in this workspace looks like in practice, including the CQ suite, validation report, and DCAT structural extension axiom plan.


### `ontologies/skygest-energy-vocab/docs/scope.md` — skygest-energy-vocab scope and in/out-of-scope

```markdown
# Skygest Energy Vocabulary — Scope

## Domain Description

A SKOS vocabulary for matching energy chart text to canonical data variables.
The Skygest platform ingests social media posts containing energy charts
(generation, capacity, prices, emissions). Stage 2 of the resolver pipeline
decomposes chart titles, axis labels, and source lines into seven-facet
Variable descriptions. This ontology provides the surface-form-to-canonical
mappings that power that decomposition.

Four of the seven facets are attacked by Stage 2's deterministic table
lookup. Each becomes a SKOS ConceptScheme whose concepts carry
`skos:altLabel` values representing the surface forms found in real chart
text (English and German). A fifth scheme (frequency) is planned for Phase 2
when Series-level FixedDims support is added.

## Intended Use Cases

- Match chart title text ("Global wind capacity additions, 2010-2024") to a
  canonical Variable by decomposing into facets (statisticType=stock,
  technologyOrFuel=wind, unitFamily=power)
- Discriminate near-synonymous Variables: "installed capacity" (stock, power)
  vs "electricity generation" (flow, energy) vs "wholesale price" (price,
  currency_per_energy)
- Provide Stage 3 (LLM lane) with visible vocabulary evidence: every surface
  form entry carries provenance and notes so the LLM can inspect what Stage 2
  knew and override it

## Data Sources

### Demand side (what we must match)

- **23 cold-start Variables** with 7-facet descriptions in
  `skygest-cloudflare/references/cold-start/variables/`
- **289 candidate posts** referencing 19 of the 23 variables
- **37-post eval snapshot** with real chart titles (English and German)
- **76 unresolved posts** (26% of candidates) that Stage 2 must handle

### Supply side (external ontologies to import from)

| Source | Format | Facets Covered | Est. Terms |
|--------|--------|---------------|------------|
| OEO v2.11.0 | RDF/XML (3.8 MB) | technologyOrFuel | 50-80 concepts |
| ENTSO-E PSRType | 25-entry enum | technologyOrFuel | 25 codes |
| Eurostat SIEC | CSV/JSON-LD, 279 concepts | technologyOrFuel | ~120 leaf products |
| QUDT v2.1 | Turtle RDF, 2300+ units | unitFamily | ~80 energy-domain units |
| UCUM | XML, 305 units | unitFamily | ~30 energy-relevant |
| ISO 4217 | CSV, ~35 active codes | unitFamily (currency) | ~35 codes |
| Wikidata | SPARQL one-shot | technologyOrFuel (synonyms) | ~50-100 items |

### Existing Skygest ontologies

- **energy-news** ontology: ~55 SKOS topic individuals with altLabels. Has
  SSSOM mappings to OEO (7 mappings) and Wikidata (12 mappings). The topic
  scheme covers broad energy categories but not the fine-grained facets
  needed for Variable decomposition.
- **energy-media** ontology: chart type scheme, media attachment classes.
  Complements but does not overlap with this vocabulary.

## In Scope

### Six Core SKOS ConceptSchemes (Variable facets)

The first four map 1:1 to Stage 2's original deterministic lookup facets.
Schemes 5-6 were added in SKY-309 to disambiguate tied Variables:

1. **StatisticTypeScheme** — 5 concepts: `stock`, `flow`, `price`, `share`,
   `count`. Surface forms map chart language to the type of quantity measured.
   Examples: "installed capacity" -> stock, "annual generation" -> flow,
   "wholesale price" -> price, "share of electricity" -> share.

2. **AggregationScheme** — 7 concepts: `point`, `end_of_period`, `sum`,
   `average`, `max`, `min`, `settlement`. Surface forms from temporal
   qualifiers in chart text. Examples: "cumulative" -> end_of_period,
   "average price" -> average, "total generation" -> sum.

3. **UnitFamilyScheme** — 8 concepts: `power`, `energy`, `currency`,
   `currency_per_energy`, `mass_co2e`, `intensity`, `dimensionless`, `other`.
   Surface forms from axis labels and unit strings. Examples: "GW" -> power,
   "TWh" -> energy, "$/MWh" -> currency_per_energy, "MtCO2e" -> mass_co2e.

4. **TechnologyOrFuelScheme** — Open-ended, ~40-60 concepts. Surface forms
   from chart titles and source lines. Examples: "solar PV" -> solar_pv,
   "CCGT" -> gas_ccgt, "offshore wind" -> offshore_wind, "lignite" ->
   brown_coal. Hierarchy follows OEO structure (energy carriers, power
   generating units) enriched with ENTSO-E, SIEC, and Wikidata synonyms.
   Unlike the other three schemes, `technologyOrFuel` is an open
   `Schema.String` in the Variable schema — this vocabulary defines the
   curated canonical list.

### Disambiguation Schemes (SKY-309, added 2026-04-12)

These two schemes address the 37 ambiguous eval observations where Variables
tied on the four core facets. They add two discriminating dimensions:

5. **MeasuredPropertyScheme** — 8 concepts: `generation`, `capacity`,
   `demand`, `emissions`, `investment`, `price`, `share`, `count`. Surface
   forms map chart language to WHAT is being measured. Examples: "generation"
   -> generation, "installed" -> capacity, "demand" -> demand, "emissions" ->
   emissions. Cross-scheme overlap with StatisticTypeScheme is intentional
   ("generation" fires both Flow and Generation).

6. **DomainObjectScheme** — 16 concepts matching cold-start Variable
   domainObject values: `electricity`, `battery storage`, `clean energy`,
   `data center`, `electrolyzer`, `energy consumption`, `energy transition`,
   `heat pump`, `interconnection queue`, `lithium-ion battery pack`,
   `nuclear reactor`, `offshore wind farm`, `offshore wind turbine`,
   `renewable power`, `solar photovoltaic`, `wind turbine`. Surface forms
   map chart language to WHAT DOMAIN OBJECT is being measured. Examples:
   "electricity" -> electricity, "battery" -> battery storage, "data center"
   -> data center.

### Phase 2 Extension Scheme (FixedDims, not Variable facet)

7. **FrequencyScheme** — 6 concepts: `hourly`, `daily`, `weekly`, `monthly`,
   `quarterly`, `annual`. Surface forms from x-axis labels and temporal
   qualifiers. Examples: "monthly data" -> monthly, "Q1 2024" -> quarterly.
   > **Note**: Frequency is not a Variable facet. It belongs to the
   > Series-level FixedDims model. This scheme is planned for Phase 2
   > when the resolver expands beyond Variable decomposition.

### Cross-ontology mappings (SSSOM)

- TechnologyOrFuelScheme concepts -> OEO IRIs via `skos:closeMatch`
- TechnologyOrFuelScheme concepts -> ENTSO-E PSRType codes via `skos:exactMatch`
- TechnologyOrFuelScheme concepts -> SIEC codes via `skos:broadMatch`
- TechnologyOrFuelScheme concepts -> Wikidata QIDs via `skos:closeMatch`
- UnitFamilyScheme concepts -> QUDT unit IRIs via `skos:closeMatch`
- UnitFamilyScheme concepts -> UCUM codes via `skos:exactMatch`

### JSON export for Skygest Stage 2

A custom `build_surface_form_json()` step in `scripts/build.py` reads the
built ontology graph and emits five JSON files matching the Skygest
`SurfaceFormEntry` schema:

```
references/vocabulary/statistic-type.json
references/vocabulary/aggregation.json
references/vocabulary/unit-family.json
references/vocabulary/technology-or-fuel.json
references/vocabulary/frequency.json          # Phase 2 — FixedDims, not Variable facet
```

Each row has: `surfaceForm`, `normalizedSurfaceForm`, `canonical`,
`provenance` (one of: `cold-start-corpus`, `hand-curated`, `oeo-derived`,
`ucum-derived`, `wikidata-derived`, `agent-curated`, `eval-feedback`),
`notes` (required when provenance is `agent-curated` or `eval-feedback`),
`addedAt`, optional `source`.

> **Note**: The `SurfaceFormProvenance` enum in `skygest-cloudflare` defines
> exactly these 7 values (SKY-305 added `wikidata-derived`). Additional
> provenance tags (e.g., `entsoe-derived`, `qudt-derived`) would require a
> code change to `src/domain/surfaceForm.ts`.

### Normalization contract

`normalizedSurfaceForm` must exactly equal
`normalizeLookupText(surfaceForm)` — i.e., Unicode NFKC normalization,
collapse whitespace, lowercase. The build script must enforce this invariant.

### Collision constraint

`buildVocabularyIndex()` raises `VocabularyCollisionError` if two different
canonical values claim the same `normalizedSurfaceForm` within a single
vocabulary file. The ontology must not produce surface forms that violate
this constraint.

## Out of Scope

- The three deferred facets (`measuredProperty`, `domainObject`, `basis`) —
  these are Stage 3 LLM concerns, not deterministic vocabulary
- Series resolution (`FixedDims`: place, sector, market) — separate slice
- Full article text or post body parsing
- Embedding-based matching (Stage 2.5, deferred per SD-Q12)
- Runtime ontology queries — the Worker consumes flat JSON, not RDF

## Constraints

- **Profile**: OWL 2 DL (primarily SKOS concept schemes with annotation properties)
- **Size**: Small (~60-80 SKOS concepts across 4 core schemes, ~400-700 altLabels; +6 frequency concepts in Phase 2)
- **Serialization**: Turtle (.ttl)
- **Upper ontology**: Minimal BFO alignment where natural (inherits from energy-news)
- **Naming**: CamelCase concepts, English labels as primary, German altLabels for energy-charts.info surface forms
- **Export constraint**: The JSON export must decode cleanly against `makeSurfaceFormEntry<Canonical>` from `skygest-cloudflare/src/domain/surfaceForm.ts`
- **H-S2-1 principle**: "Stage 2 advises, Stage 3 decides." Every surface form entry must carry enough provenance for Stage 3 to inspect and override.

## Priority Surface Forms (from demand-side analysis)

### Tier 1 — Discriminates top 10 Variables (85%+ of 289 candidates)

| Facet | Surface Forms | Canonical |
|-------|--------------|-----------|
| technologyOrFuel | solar, solar PV, PV, photovoltaic | solar_pv |
| technologyOrFuel | wind, wind power, onshore wind, Windkraft | wind |
| technologyOrFuel | battery, batteries, BESS, energy storage | battery |
| technologyOrFuel | renewable, renewables, clean energy, erneuerbare Energien | renewable |
| unitFamily | GW, MW, kW, gigawatt, megawatt | power |
| unitFamily | TWh, GWh, MWh, kWh, Wh | energy |
| unitFamily | $/MWh, EUR/MWh, ct/kWh | currency_per_energy |
| statisticType | installed, cumulative, total, nameplate | stock |
| statisticType | generation, output, Erzeugung, Stromerzeugung | flow |
| statisticType | price, cost, tariff, rate, Strompreis | price |

### Tier 2 — Remaining Variables

| Facet | Surface Forms | Canonical |
|-------|--------------|-----------|
| technologyOrFuel | nuclear, atomic, Kernkraft | nuclear |
| technologyOrFuel | coal, coal-fired, Kohle, lignite | coal |
| technologyOrFuel | offshore wind | offshore_wind |
| technologyOrFuel | heat pump, heat pumps | heat_pump |
| technologyOrFuel | hydrogen, electrolyzer, electrolysis | hydrogen |
| technologyOrFuel | natural gas, gas, CCGT, OCGT, Erdgas | natural_gas |
| unitFamily | $, USD, EUR, CAD, GBP | currency |
| unitFamily | tCO2, tCO2e, MtCO2e, gCO2/kWh | mass_co2e |
| unitFamily | %, share, proportion | dimensionless |
| statisticType | share, percentage, proportion, Anteil | share |
| aggregation | average, mean, weighted average | average |
| aggregation | cumulative, end of period, as of | end_of_period |
| aggregation | total, sum, annual total | sum |

### Tier 3 — German language (energy-charts.info posts)

| Surface Form | Canonical |
|-------------|-----------|
| Stromerzeugung, Nettostromerzeugung | flow (statisticType) |
| Stromverbrauch | flow (statisticType) — demand context |
| Kapazitat | stock (statisticType) |
| Solarenergie, Photovoltaik | solar_pv (technologyOrFuel) |
| Windenergie | wind (technologyOrFuel) |

## Key Discriminator Pairs

These are the Variable pairs that Stage 2 must distinguish. The vocabulary
must provide surface forms that resolve the ambiguity:

1. **capacity vs generation** — unitFamily (power vs energy) is the strongest signal
2. **stock vs flow** — "installed"/"cumulative" -> stock; "annual"/"monthly" output -> flow
3. **parent renewable vs child tech** — technologyOrFuel presence selects child; absence selects parent
4. **share vs absolute** — "%"/"share" -> share; absolute units -> flow/stock
5. **investment vs generation** — measuredProperty is the only discriminator (deferred to Stage 3)

## Relationship to Existing Ontologies in This Repo

This vocabulary extends the energy-news ontology's topic coverage into
fine-grained facets. Where energy-news has `enews:Solar` as a broad topic,
this vocabulary has `sevocab:solar_pv` as a `technologyOrFuel` concept with
specific surface forms for chart matching. SSSOM mappings link the two:
`sevocab:solar_pv skos:broadMatch enews:Solar`.

The energy-media ontology's `ChartTypeScheme` is complementary — it classifies
chart visual types (bar, line, area), while this vocabulary classifies chart
content (what the data represents).

## Architectural Zones

The vocabulary has grown into three distinguishable zones. Future changes
should be routed to the correct zone — the zones have different runtime
coupling, different review gates, and different lifecycles.

### Zone A — DCAT Metadata Spine (live)

The DCAT-aligned structural backbone that the `skygest-cloudflare` runtime
consumes. Every item in this zone has a D1 repo consumer under
`skygest-cloudflare/src/services/d1/*` and is referenced by the generated
data-layer manifest at
`skygest-cloudflare/src/domain/generated/dataLayerSpine.ts`.

**sevocab classes**
- `sevocab:EnergyAgent` — an organization, person, or software system that
  publishes energy data (subclass of `foaf:Agent`).
- `sevocab:EnergyDataset` — a DCAT dataset published by an EnergyAgent and
  containing one or more EnergyVariables (subclass of `dcat:Dataset`).
- `sevocab:EnergyVariable` — a 7-facet statistical variable; carries the
  `owl:maxQualifiedCardinality 1` restrictions that enforce the facet
  constraint (subclass of `schema:StatisticalVariable`).
- `sevocab:Series` — the intra-dataset structural node that pairs a
  Variable with a Dataset (subclass of `prov:Entity` — parented to PROV
  rather than IAO specifically to avoid a BFO leak through Zone C).

**DCAT/PROV/schema.org classes reused**
- `dcat:Dataset`, `dcat:Distribution`, `dcat:DataService` — the standard
  DCAT triad the runtime distribution layer mirrors.
- `prov:Entity` — parent of `sevocab:Series`.
- `schema:StatisticalVariable` — parent of `sevocab:EnergyVariable`.

**sevocab structural properties**
- `sevocab:hasSeries` (Dataset → Series), `sevocab:publishedInDataset`
  (inverse), `sevocab:implementsVariable` (Series → Variable,
  `owl:FunctionalProperty`), `sevocab:hasVariable` (Dataset → Variable;
  denormalized view, now formalized via
  `owl:propertyChainAxiom ( hasSeries implementsVariable )`).

**External structural/annotation properties reused**
- `dcterms:publisher`, `dcterms:identifier`, `dcat:distribution`,
  `dcat:accessURL`, `foaf:homepage`.

### Zone B — SKOS Facet Shelf (live, under review per SKY-348)

The eight SKOS concept schemes that the Stage 1 / Stage 2 resolver consumes
as flat JSON lookup dictionaries via
`skygest-cloudflare/src/resolution/facetVocabulary/*`. The runtime consumes
these as JSON, not as RDF — the ontology is the build-time source of truth,
the JSON emitted by `scripts/build.py` is what the Worker reads.

- `sevocab:StatisticTypeScheme` — stock / flow / price / share / count.
- `sevocab:AggregationScheme` — point / end_of_period / sum / average /
  max / min / settlement.
- `sevocab:UnitFamilyScheme` — power / energy / currency /
  currency_per_energy / mass_co2e / intensity / dimensionless / other.
- `sevocab:TechnologyOrFuelScheme` — the open-ended fuel/technology
  taxonomy (~40-60 concepts) aligned to OEO + ENTSO-E + SIEC + Wikidata.
- `sevocab:MeasuredPropertyScheme` — what is being measured.
- `sevocab:DomainObjectScheme` — what domain object the measurement is
  about.
- `sevocab:FrequencyScheme` — hourly / daily / weekly / monthly /
  quarterly / annual (Phase 2, FixedDims-level).
- `sevocab:PolicyInstrumentScheme` — feed-in tariff / contract-for-
  difference / auction / renewable portfolio standard / tax credit / ...

SKY-348 plans to re-architect this zone around OEO as the upstream source
of truth for technology/fuel terms; expect the shelf surface to change
(while the JSON export contract stays stable).

### Zone C — Semantic Reasoning Extension (decorative, pending activation)

OEO/BFO/QUDT-aligned OWL classes that prototype "how the vocabulary would
look if the runtime ever consumed it as RDF with a reasoner." **This zone
has zero TypeScript consumers today.** It is retained as a proof-of-concept
for SKY-346 (crude oil exemplar → generalize across commodities).

- `sevocab:CrudeOil` — a natural liquid hydrocarbon mixture (subclass of
  `oeo:OEO_00000115`).
- `sevocab:CrudeOilGrade` — a tradeable crude oil benchmark (e.g. WTI,
  Brent) distinguished by API gravity, sulfur, and delivery point.
- `sevocab:Price` — both `owl:Class` and `skos:Concept` (OWL 2 punning),
  parented to OEO's monetary value ICE.
- `sevocab:PriceOfCommodity` — specialization of Price scoped to a named
  commodity.
- `sevocab:CostPerVolume` — price quoted per volumetric unit (oil
  benchmarks).
- `sevocab:WindEnergyConvertingUnit`, `sevocab:OnshoreWindUnit`,
  `sevocab:OffshoreWindUnit` — OEO-aligned wind turbine specializations.
- `sevocab:NaturalGasHub` — physical or virtual gas trading hub.
- `sevocab:PowerMarket` — a wholesale electricity market (exchange or
  balancing area).

Three load-bearing design choices keep Zone C isolated from Zones A and B:

1. **OWL 2 punning.** Several terms (notably `sevocab:Price`,
   `sevocab:Generation`, `sevocab:Capacity`, `sevocab:Demand`,
   `sevocab:Coal`, `sevocab:NaturalGas`) are simultaneously `owl:Class`
   AND `skos:Concept`. The class lives in Zone C; the concept lives in
   Zone B. The JSON build pipeline reads the SKOS face; the (future)
   reasoner reads the OWL face.

2. **CQ-086 as the BFO leak guard.** A standing SPARQL guard asserts that
   no term reachable from Zone A's DCAT spine transitively climbs into
   BFO. If Zone C is extended and accidentally drags a Zone A class into
   BFO, CQ-086 fails.

3. **`sevocab:Series` is parented to `prov:Entity`, not
   `iao:IAO_0000030`.** The natural IAO parent would climb to BFO via
   GenericallyDependentContinuant. Choosing PROV keeps the Zone A spine
   BFO-free.

### What this boundary means for you

When adding a new class, first decide which zone it belongs to.

- **Zone A changes** require a corresponding `skygest-cloudflare` manifest
  update (`references/data-layer-spine/manifest.json`) and generally a D1
  schema/repo change. A Zone A change that does not land a TS consumer is
  a regression — you have just added dead structural weight.
- **Zone B changes** require updating the SHACL shapes manifest
  (`references/energy-profile/shacl-manifest.json`) and the JSON export
  contract. Surface-form additions must respect the
  `VocabularyCollisionError` invariant.
- **Zone C changes** are ontology-only until SKY-346 activation lands.
  They should not block Zone A/B work, must not leak BFO into Zone A
  (CQ-086), and should include a note explaining which future consumer
  justifies the addition.

```


### `ontologies/skygest-energy-vocab/docs/validation-report-2026-04-14.md` — Most recent validation report

```markdown
# Validation Report — skygest-energy-vocab

**Date**: 2026-04-14
**Reviewer**: ontology-validator + ontology-architect
**Trigger**: user-requested comprehensive review ("make sure it's robust, coherent, professionally maintained")
**Scope**: TBox logical soundness, OWL 2 DL profile conformance, label/definition coverage, orphan analysis, DCAT chain integrity, CQ acceptance tests, alignment with sister-directory (`/Users/pooks/Dev/skygest-cloudflare`)

---

## Summary

**Overall**: ✅ **PASS**

All blocking issues identified in the initial review were resolved in this
session. The ontology now passes the full validation stack end-to-end.

| Dimension | Before | After |
|---|---|---|
| HermiT consistency | ✅ | ✅ |
| OWL 2 DL profile | ❌ 2115 violations | ✅ **In profile** (merged check) |
| Valid imports (closure) | 4 of 8 | **10 of 10** |
| SHACL validation | ✅ | ✅ |
| ROBOT report ERRORs | 0 | 0 |
| ROBOT report WARNs | 51 | **23** (all `missing_definition`, IAO-vs-SKOS style choice) |
| Native orphan classes | 3 | **0** |
| CQ test pass rate | 83/92 (90.2%) | **84/92** (91.3%) |
| CQ-068 (DSD structure) | ❌ query bug | ✅ |
| CQ-086 (BFO leak guard) | ✅ | ✅ (preserved through re-parenting) |

---

## Phase 1 — Declaration hygiene

**Root cause of the 2115 profile violations**: the ontology used entities
from SKOS, QUDT, IAO, dcterms, dcat, foaf, and prov without declaring them.
None of these vocabularies had declaration stubs covering the entities
referenced in axioms, annotations, or property assertions.

**Fix**: one Python/rdflib build script
(`scripts/fix_declaration_hygiene.py`) that performs all declaration work
programmatically. No hand-editing.

### What it did

| Step | Target | Effect |
|---|---|---|
| 1a | Add `owl:Ontology` headers to `foaf-extract`, `schema-extract`, `datacube-extract` | Stubs now register as valid imports |
| 1b | Expand `dcat-extract.ttl` to declare every DCAT / dct / prov / foaf entity the `skygest-cloudflare` manifest expects sevocab to recognize | ~35 new declarations (dct:title, description, license, creator, publisher, temporal, prov:wasDerivedFrom, generatedAtTime, wasAttributedTo, dcat:Catalog, CatalogRecord, DataService, DatasetSeries, accessURL, accessService, mediaType, landingPage, inSeries, record, keyword, theme, foaf:Agent, name, homepage, primaryTopic) |
| 1c | Create `imports/skos-extract.ttl` | Declares 30+ SKOS terms (resolves ~1437 violations) |
| 1d | Create `imports/iao-extract.ttl` | Declares IAO_0000030 (InformationContentEntity), IAO_0000115 (definition), IAO_0000116 (editor note), IAO_0000119 (definition source), IAO_0000231 (obsolescence reason) |
| 1e | Extend both QUDT stubs | Declares ~25 qudt schema entities (applicableUnit, hasQuantityKind, hasDimensionVector, symbol, conversionMultiplier, UCUM/IEC/UNECE code props, etc.) |
| 1f | Update `catalog-v001.xml` | skos-extract + iao-extract resolvable via catalog |
| 1g | Update main `owl:imports` list | All 10 stubs explicitly imported |
| 1h | Fix `cq-068.sparql` | Query was emitting a COUNT/HAVING row; `exactly_7` semantics compared 1 row vs 7 and always failed. Rewrote to `SELECT ?comp ?dim` returning one row per component |
| 1i | Update `run_cq_tests.py` | Loads all 10 import stubs (previously only 4 semantic-extension stubs) |

### Follow-up script (`fix_declaration_hygiene_followup.py`)

A second pass removed two real DL violations that survived the first fix:

- `qb:ComponentProperty rdfs:subClassOf rdf:Property` — reserved-vocabulary-as-class
  axiom that leaked from the upstream Data Cube vocabulary. Removed.
- `"..."^^rdf:HTML` typed literals in `qudt-unit.ttl` — OWLAPI does not
  recognize `rdf:HTML` as an OWL 2 DL datatype. Four literals in the unit
  descriptions were retyped to `xsd:string`.

### Verification

```
robot merge --input skygest-energy-vocab.ttl --output merged.ttl
robot validate-profile --profile DL --input merged.ttl

→ OWL 2 DL Profile Report: [Ontology and imports closure in profile]
```

**Important caveat**: `robot measure` and `robot validate-profile` run
directly on the unmerged `.ttl` still report profile violations. This is
an OWLAPI quirk in how imports are resolved for profile checks on unmerged
input. The authoritative check is merge-then-validate, which reports clean.

---

## Phase 2 — Native orphans

Three native `owl:Class` entities lacked `rdfs:subClassOf` axioms and were
flagged as `missing_superclass` by ROBOT report.

**Fix**: `scripts/fix_native_orphans.py` + `scripts/fix_deprecated_subclass_axiom.py`
+ `scripts/fix_obsolete_labels.py` + `scripts/fix_series_parent.py`.

### `sevocab:Series`

**Decision**: parent to **`prov:Entity`** (W3C PROV-O upper class for
records, digital/conceptual/physical entities).

**First attempt**: parent to `iao:IAO_0000030` (InformationContentEntity).
This is the textbook OBO answer, but `imports/oeo-module.ttl:167` declares
`IAO_0000030 rdfs:subClassOf BFO_0000031`. Series therefore inherited BFO
via transitive closure, breaking **CQ-086** (BFO category leak guard —
DCAT-layer classes must never reach BFO).

**Final fix**: re-parent to `prov:Entity` instead. PROV-O has no BFO
alignment, is a W3C standard, and the DCAT layer already uses PROV-O for
`prov:wasDerivedFrom`. A minimal `prov:Entity` declaration was added to
`dcat-extract.ttl` so the parent is available in the imports closure.

### `sevocab:SurfaceFormEntry` + `sevocab:hasProvenanceAnnotation` + `sevocab:surfaceFormValue`

**Decision**: **deprecate** via `owl:deprecated true` + `IAO_0000231`
obsolescence reason annotation. Labels renamed to OBO convention
(`obsolete surface form entry`, etc.). No structural axioms remain
(deprecation is terminal per OBO practice).

**Rationale**: reconnaissance of `skygest-cloudflare` confirmed the class
was added speculatively. `skygest-cloudflare` tracks surface-form
provenance in a TypeScript runtime codec at `src/domain/surfaceForm.ts`
rather than in RDF. Zero instances of the class exist in sevocab.

The `owl:deprecated true` + `IAO_0000231` tombstone pattern preserves the
IRI for traceability. If a future RDF-emitting consumer needs to
materialize surface-form provenance, un-deprecate and formalize under a
proper parent class.

### `sevocab:PriceOfCommodity`

**Decision**: assert `rdfs:subClassOf sevocab:Price` alongside the
existing `owl:equivalentClass` intersection axiom.

**Rationale**: this class was technically not a real orphan — its
equivalence with `sevocab:Price ⊓ (appliesToDomainObject some CrudeOil)`
means the reasoner infers `⊑ sevocab:Price`. But `robot report` only
inspects asserted parents, so the warning fired. Asserting the parent
directly silences the warning without changing semantics (reasoner output
is identical).

---

## Phase 3 — DSD wiring (CQ-068)

**No wiring bug existed**. The `qb:DataStructureDefinition`
(`sevocab:EnergyVariableStructure`) already contained all 7 components.

The bug was in `cq-068.sparql`: it used `SELECT (COUNT(?comp) AS ?count)`
with a `HAVING` clause, which returns at most 1 row. The test runner's
`exactly_7` semantics compare result-row count, so the query always
returned 1 row and always failed (even with the DSD correct).

**Fix**: rewrote to `SELECT ?comp ?dim` — one row per component. Passes.

---

## Sister-directory alignment

Verified against `/Users/pooks/Dev/skygest-cloudflare` canonical sources:

- `references/data-layer-spine/manifest.json` — confirms all sevocab class
  IRIs (`EnergyAgent`, `EnergyDataset`, `EnergyVariable`, `Series`) match
  what skygest-cloudflare emits
- `src/domain/data-layer/graph-ontology-mapping.ts` — confirms all
  sevocab property IRIs (`hasVariable`, `publishedInDataset`,
  `implementsVariable`) match what skygest-cloudflare references
- `src/domain/data-layer/variable.ts` — confirms the 7-facet
  `EnergyVariable` model matches exactly (measuredProperty, domainObject,
  technologyOrFuel, statisticType, aggregation, unitFamily, policyInstrument)

**Series naming collision** (flagged in the review as a confusion point):
resolved by the sister-directory manifest's own classComment, which
explicitly documents the dual model:

- `dcat:DatasetSeries` (IRI prefix `dser_`) — curated publisher-side
  grouping of related dataset editions
- `sevocab:Series` (IRI prefix `ser_`) — intra-dataset structural node
  naming how one EnergyVariable is realized inside one EnergyDataset

Both are correct. The collision is purely lexical. Both manifest and
ontology make the distinction explicit in their respective class comments.

---

## Remaining known issues (non-blocking)

### ROBOT report — 23 `missing_definition` warnings

All 23 are on native sevocab `owl:Class` / `owl:ObjectProperty` entities.
Every one of them has a `skos:definition`, but ROBOT report's
`missing_definition` rule checks for `obo:IAO_0000115`. This is a style
choice, not a gap.

**Recommended fix** (future work, non-urgent): add a build-script pass
that mirrors every `skos:definition` value into `obo:IAO_0000115`. The
two properties are semantically equivalent in practice. Alternatively,
customize ROBOT's report profile to accept `skos:definition`.

### CQ test failures — 8 of 92

| CQ | Test | Cause |
|---|---|---|
| CQ-006 | Ambiguous altLabels shared by multiple concepts | Pruning job has eliminated intra-scheme collisions — expected non-empty result no longer reflects the curated state |
| CQ-012, CQ-013, CQ-014 | Provenance queries against `SurfaceFormEntry` | SurfaceFormEntry is now deprecated and has no instances; these CQs should be retired or rewritten |
| CQ-019, CQ-020 | OEO / QUDT mappings for facet concepts | External mapping data is not populated in the test graph |
| CQ-025 | Cross-repo `broadMatch` to energy-news | Cross-repo data not loaded by `run_cq_tests.py` |
| CQ-053 | Every active concept has ≥3 English surface forms | 3 concepts still fall below the threshold — feed back to `prune_broad_surface_forms.py` or `harvest_labels.py` |

All are ABox / data / test-scoping issues, not TBox correctness issues.
None are introduced by this review's changes.

### `robot measure` unmerged profile-check quirk

`robot measure` on the unmerged TTL reports `owl2_dl: false`. This is a
known OWLAPI artifact: the profile check on unmerged input does not
properly walk the imports closure for declarations. The authoritative
check is `robot merge` → `robot validate-profile`, which confirms the
ontology **is** in OWL 2 DL profile.

---

## Files touched

### New

- `imports/skos-extract.ttl`
- `imports/iao-extract.ttl`
- `docs/validation-report-2026-04-14.md` (this file)
- `scripts/fix_declaration_hygiene.py`
- `scripts/fix_declaration_hygiene_followup.py`
- `scripts/fix_native_orphans.py`
- `scripts/fix_deprecated_subclass_axiom.py`
- `scripts/fix_obsolete_labels.py`
- `scripts/fix_series_parent.py`

### Modified

- `skygest-energy-vocab.ttl` — Series parent, PriceOfCommodity parent, SurfaceFormEntry trio deprecation + label rename, owl:imports list
- `catalog-v001.xml` — skos-extract + iao-extract entries
- `imports/dcat-extract.ttl` — full rewrite with 35+ DCAT/dct/prov/foaf declarations + prov:Entity
- `imports/datacube-extract.ttl` — rewrite, rdf:Property superclass removed
- `imports/schema-extract.ttl` — rewrite with ontology header
- `imports/foaf-extract.ttl` — rewrite with ontology header
- `imports/qudt-quantitykind.ttl` — extended with ~25 qudt schema declarations + ontology header
- `imports/qudt-unit.ttl` — extended with ~25 qudt schema declarations + ontology header + 4 rdf:HTML literals retyped
- `tests/cq-068.sparql` — query rewritten
- `scripts/run_cq_tests.py` — load all 10 import stubs

### Checkpoint

- `.checkpoints/pre-hygiene-2026-04-14/` — snapshot of every file modified in this session. Diff against this snapshot to review the full change set.

```


### `ontologies/skygest-energy-vocab/docs/axiom-plan-dcat-extension.yaml` — DCAT structural extension axiom plan

```yaml
# Axiom Plan: DCAT Structural Extension
# Maps CQs to OWL axiom patterns from _shared/axiom-patterns.md

# =============================================================================
# Class Hierarchy Axioms (Pattern #1: Simple SubClassOf)
# =============================================================================

- cq: CQ-057
  pattern: "1. Simple SubClassOf"
  manchester: |
    Class: EnergyVariable
      SubClassOf: schema:StatisticalVariable
  notes: "Direct subclass assertion"

- cq: CQ-061
  pattern: "1. Simple SubClassOf"
  manchester: |
    Class: EnergyDataset
      SubClassOf: dcat:Dataset
  notes: "Direct subclass assertion"

- cq: CQ-062
  pattern: "1. Simple SubClassOf"
  manchester: |
    Class: EnergyAgent
      SubClassOf: foaf:Agent
  notes: "Direct subclass assertion"

# =============================================================================
# Disjointness (Pattern #5: Disjoint Classes)
# =============================================================================

- cq: implicit
  pattern: "5. Disjoint Classes"
  manchester: |
    DisjointClasses: EnergyVariable, EnergyDataset, EnergyAgent, Series
  notes: >
    A Variable cannot be a Dataset, an Agent, or a Series. Series is
    added to the AllDisjointClasses axiom in SKY-316 so the reasoner
    detects misclassification between Series and the other spine
    classes. Pairwise disjointness enables the reasoner to detect
    misclassification errors.

# =============================================================================
# DCAT Chain — Existential Restrictions (Pattern #2: SomeValuesFrom)
# =============================================================================

- cq: CQ-058
  pattern: "2. Existential Restriction"
  manchester: |
    Class: EnergyDataset
      SubClassOf: dct:publisher some EnergyAgent
  notes: "Every EnergyDataset has at least one publisher that is an EnergyAgent"

- cq: CQ-065
  pattern: "2. Existential Restriction"
  manchester: |
    Class: EnergyDataset
      SubClassOf: dcat:distribution some dcat:Distribution
  notes: "Every EnergyDataset has at least one Distribution"

- cq: CQ-059
  pattern: "2. Existential Restriction"
  manchester: |
    Class: EnergyDataset
      SubClassOf: hasVariable some EnergyVariable
  notes: "Every EnergyDataset has at least one Variable"

# =============================================================================
# Variable Composition — Qualified Cardinality (Pattern #7)
# =============================================================================

- cq: CQ-063
  pattern: "7. Qualified Cardinality Restriction"
  manchester: |
    Class: EnergyVariable
      SubClassOf: measuredProperty max 1 skos:Concept
      SubClassOf: domainObject max 1 skos:Concept
      SubClassOf: technologyOrFuel max 1 skos:Concept
      SubClassOf: statisticType max 1 skos:Concept
      SubClassOf: aggregation max 1 skos:Concept
      SubClassOf: unitFamily max 1 skos:Concept
      SubClassOf: policyInstrument max 1 skos:Concept
  notes: >
    Each facet dimension has at most one value per Variable. This is
    maxQualifiedCardinality 1, not exact cardinality — Variables can have
    missing facets (partial composition during resolution).

# =============================================================================
# Data Structure Definition — RETIRED 2026-04-14
# =============================================================================
# The sevocab:EnergyVariableStructure qb:DataStructureDefinition was removed
# during the Tier 1 cleanup pass. Rationale:
#   - Zero runtime consumers in skygest-cloudflare (the 7-facet Variable
#     shape is enforced by the TypeScript schema, not a qb:DSD read from RDF).
#   - The 7-facet cardinality constraint is already carried by the
#     owl:maxQualifiedCardinality 1 restrictions on sevocab:EnergyVariable
#     (see the class-level axiom section above), so the DSD was duplicative.
#   - CQ-054 and CQ-068 have been rewritten to probe those restrictions
#     directly instead of walking the DSD components.
# See docs/validation-report-2026-04-14.md and the module docstring of
# scripts/add_dcat_structural_layer.py for the full rationale.

- cq: CQ-054
  status: retired
  retirement_date: "2026-04-14"
  retirement_note: >
    DSD individual emission removed; CQ-054 now probes the 7
    owl:maxQualifiedCardinality restrictions on sevocab:EnergyVariable
    directly. The qb:DataStructureDefinition approach is preserved here
    as historical design record only — do not re-emit.
  pattern: "Individual assertions (not a class axiom pattern) — RETIRED"
  description: |
    HISTORICAL: EnergyVariableStructure was a named individual
    (qb:DataStructureDefinition) with 7 qb:component links, each pointing
    to a blank-node qb:ComponentSpecification that referenced one of the 7
    dimension properties. Retained here for audit traceability only; the
    runtime ontology no longer contains this construct.
  turtle_sketch: |
    # RETIRED — do not emit. Retained as historical record.
    # sevocab:EnergyVariableStructure a qb:DataStructureDefinition ;
    #   qb:component [ qb:dimension sevocab:measuredProperty ] ;
    #   qb:component [ qb:dimension sevocab:domainObject ] ;
    #   qb:component [ qb:dimension sevocab:technologyOrFuel ] ;
    #   qb:component [ qb:dimension sevocab:statisticType ] ;
    #   qb:component [ qb:dimension sevocab:aggregation ] ;
    #   qb:component [ qb:dimension sevocab:unitFamily ] ;
    #   qb:component [ qb:dimension sevocab:policyInstrument ] .
  notes: >
    Blank nodes for ComponentSpecification were acceptable structurally,
    but the whole construct was decorative — not load-bearing in either the
    ontology semantics or the runtime. Removed in Tier 1 cleanup.

- cq: CQ-055
  pattern: "Individual assertions"
  description: |
    Each dimension property is a named individual with a qb:codeList.
  turtle_sketch: |
    sevocab:measuredProperty a qb:DimensionProperty, owl:ObjectProperty ;
      qb:codeList sevocab:MeasuredPropertyScheme ;
      rdfs:label "measured property"@en ;
      skos:definition "The physical or economic quantity being measured."@en .
  notes: "Repeated for all 7 dimensions with their respective code lists."

# =============================================================================
# hasVariable Property Declaration
# =============================================================================

- cq: CQ-059
  pattern: "Property declaration"
  manchester: |
    ObjectProperty: hasVariable
      Domain: EnergyDataset
      Range: EnergyVariable
  notes: >
    Domain/range safe here — both are sevocab-specific classes. No risk
    of unintended classification of external entities. Retained as the
    higher-level denormalized view; structural source of truth is the
    hasSeries + implementsVariable chain.

# =============================================================================
# Series Structural Chain — SKY-316
# =============================================================================

- cq: implicit  # structural prerequisite for SKY-318 CQs
  pattern: "Property declaration"
  manchester: |
    ObjectProperty: hasSeries
      Domain: EnergyDataset
      Range: Series
      InverseOf: publishedInDataset
  notes: >
    Not functional on the Dataset side — one Dataset can have many
    Series. Deliberately not declared as a subproperty of qb:dataSet
    in this first slice.

- cq: implicit  # structural prerequisite for SKY-318 CQs
  pattern: "Property declaration + 6. Functional Property"
  manchester: |
    ObjectProperty: implementsVariable
      Domain: Series
      Range: EnergyVariable
      Characteristics: Functional
  notes: >
    owl:FunctionalProperty. Each Series realizes exactly one Variable;
    this is the semantic anchor that makes the structural chain
    deterministic.

- cq: implicit  # structural prerequisite for SKY-318 CQs
  pattern: "Property declaration + 6. Functional Property"
  manchester: |
    ObjectProperty: publishedInDataset
      Domain: Series
      Range: EnergyDataset
      Characteristics: Functional
      InverseOf: hasSeries
  notes: >
    owl:FunctionalProperty and inverse of hasSeries. Each Series is
    published in exactly one Dataset. Deliberately not declared as a
    subproperty of dcterms:isPartOf or qb:dataSet in this first slice.

- cq: implicit
  pattern: "Class declaration"
  manchester: |
    Class: Series
  notes: >
    Top-level OWL class with no superclass in this slice (no qb:Slice
    subclassing). No existential restriction on EnergyDataset requiring
    hasSeries someValuesFrom Series — a dataset with zero Series is
    explicitly legal in this slice. SHACL SeriesShape (see SHACL
    section below) enforces the Series-side exactly-one cardinalities
    for implementsVariable and publishedInDataset.

# =============================================================================
# SeriesShape — SKY-316 SHACL plan
# =============================================================================

- cq: implicit  # validation prerequisite for SKY-318
  pattern: "SHACL shape (not OWL)"
  description: |
    SeriesShape validates sevocab:Series instances:
    - sh:targetClass sevocab:Series
    - sh:property on sevocab:implementsVariable
        sh:class sevocab:EnergyVariable, sh:minCount 1, sh:maxCount 1, sh:nodeKind sh:IRI
    - sh:property on sevocab:publishedInDataset
        sh:class sevocab:EnergyDataset, sh:minCount 1, sh:maxCount 1, sh:nodeKind sh:IRI
    - sh:property on rdfs:label (minCount 1)
  notes: >
    Closed-world structural cardinality enforcement. OWL
    owl:FunctionalProperty on implementsVariable and publishedInDataset
    handles the max-one side (via inconsistency detection under
    HermiT); SHACL SeriesShape handles the min-one side and the
    structural targeting.

# =============================================================================
# SHACL Validation (not OWL axioms, but planned here)
# =============================================================================

- cq: CQ-064
  pattern: "SHACL shape (not OWL)"
  description: |
    EnergyVariableShape validates that required dimensions are present.
    measuredProperty and statisticType are required (minCount 1).
    All others are optional.
  notes: >
    SHACL handles closed-world validation that OWL cannot express.
    The shape also constrains facet values to concepts within the
    correct scheme (sh:class or SPARQL constraint).

```


### `ontologies/skygest-energy-vocab/tests/cq-test-manifest.yaml` — CQ test manifest

```yaml
# Skygest Energy Vocabulary — CQ Test Manifest
# Maps CQ IDs to SPARQL test files and expected results.
# Date: 2026-04-11

tests:

  # Facet Lookup
  - cq_id: CQ-001
    file: cq-001.sparql
    type: SELECT
    expected_result: non_empty
    description: "All concepts in a given ConceptScheme"

  - cq_id: CQ-002
    file: cq-002.sparql
    type: SELECT
    expected_result: non_empty
    description: "Canonical concept for a surface form"

  - cq_id: CQ-003
    file: cq-003.sparql
    type: SELECT
    expected_result: non_empty
    description: "Surface forms for SolarPv"

  - cq_id: CQ-004
    file: cq-004.sparql
    type: SELECT
    expected_result: non_empty
    description: "ConceptScheme for Power"

  - cq_id: CQ-005
    file: cq-005.sparql
    type: SELECT
    expected_result: non_empty
    description: "German surface forms across vocabulary"

  # Disambiguation
  - cq_id: CQ-006
    file: cq-006.sparql
    type: SELECT
    expected_result: empty
    description: "No intra-scheme ambiguous altLabels remain after pruning (invariant check)"

  - cq_id: CQ-007
    file: cq-007.sparql
    type: SELECT
    expected_result: non_empty
    description: "Unique discriminator forms for stock vs flow"

  - cq_id: CQ-008
    file: cq-008.sparql
    type: SELECT
    expected_result: non_empty
    description: "UnitFamily concept for 'GW'"

  # Hierarchy
  - cq_id: CQ-009
    file: cq-009.sparql
    type: SELECT
    expected_result: non_empty
    description: "Narrower concepts of Wind"

  - cq_id: CQ-010
    file: cq-010.sparql
    type: ASK
    expected_result: "true"
    description: "OffshoreWind is narrower than Wind"

  - cq_id: CQ-011
    file: cq-011.sparql
    type: SELECT
    expected_result: non_empty
    description: "All five ConceptSchemes"

  # Provenance
  # CQ-012, CQ-013, CQ-014 RETIRED 2026-04-14 — depended on the
  # sevocab:SurfaceFormEntry / hasProvenanceAnnotation / surfaceFormValue
  # reification trio, which has been deprecated (never instantiated in sevocab,
  # not consumed by skygest-cloudflare which tracks surface-form provenance in
  # its TypeScript runtime codec). See docs/validation-report-2026-04-14.md.

  # Coverage
  - cq_id: CQ-015
    file: cq-015.sparql
    type: SELECT
    expected_result: empty
    description: "Concepts with no altLabels (should be zero)"

  - cq_id: CQ-016
    file: cq-016.sparql
    type: SELECT
    expected_result: non_empty
    description: "TechnologyOrFuel concepts lacking German forms"

  - cq_id: CQ-017
    file: cq-017.sparql
    type: SELECT
    expected_result: non_empty
    description: "Surface form count per concept"

  - cq_id: CQ-018
    file: cq-018.sparql
    type: SELECT
    expected_result: non_empty
    description: "Concept count per ConceptScheme"

  # Cross-ontology
  - cq_id: CQ-019
    file: cq-019.sparql
    type: SELECT
    expected_result: non_empty
    description: "OEO mappings for TechnologyOrFuel concepts"

  - cq_id: CQ-020
    file: cq-020.sparql
    type: SELECT
    expected_result: non_empty
    description: "QUDT mappings for UnitFamily concepts"

  - cq_id: CQ-021
    file: cq-021.sparql
    type: SELECT
    expected_result: non_empty
    description: "Concepts with no external mappings"

  # Constraints
  - cq_id: CQ-022
    file: cq-022.sparql
    type: SELECT
    expected_result: empty
    description: "No concept with altLabels should lack a prefLabel"

  - cq_id: CQ-023
    file: cq-023.sparql
    type: SELECT
    expected_result: empty
    description: "Every concept in exactly one scheme"

  - cq_id: CQ-024
    file: cq-024.sparql
    type: SELECT
    expected_result: empty
    description: "Every concept has rdfs:label and skos:definition"

  # Cross-repo
  - cq_id: CQ-025
    file: cq-025.sparql
    type: SELECT
    expected_result: non_empty
    description: "energy-news broadMatch mappings"

  # Resolution kernel constraints (product-code alignment)
  - cq_id: CQ-026
    file: cq-026.sparql
    type: SELECT
    expected_result: empty
    description: "No intra-scheme surface form collisions (VocabularyCollisionError)"

  - cq_id: CQ-027
    file: cq-027.sparql
    type: SELECT
    expected_result: non_empty
    description: "Surface forms with uppercase (normalization awareness; real test is in build.py)"

  - cq_id: CQ-028
    file: cq-028.sparql
    type: SELECT
    expected_result: empty
    description: "Notes required for agent-curated/eval-feedback provenance"

  - cq_id: CQ-029
    file: cq-029.sparql
    type: SELECT
    expected_result: empty
    description: "TechnologyOrFuel covers all cold-start variable values"

  - cq_id: CQ-030
    file: cq-030.sparql
    type: SELECT
    expected_result: empty
    description: "Vocabulary covers all closed-enum facet values from Variable schema"

  # MeasuredProperty / DomainObject resolution (UC-009)
  - cq_id: CQ-031
    file: cq-031.sparql
    type: SELECT
    expected_result: non_empty
    description: "Canonical measuredProperty for surface form 'generation'"

  - cq_id: CQ-032
    file: cq-032.sparql
    type: SELECT
    expected_result: non_empty
    description: "Canonical domainObject for surface form 'electricity'"

  - cq_id: CQ-033
    file: cq-033.sparql
    type: SELECT
    expected_result: non_empty
    description: "Surface forms for measuredProperty concept Capacity"

  - cq_id: CQ-034
    file: cq-034.sparql
    type: SELECT
    expected_result: non_empty
    description: "Generation concept exists in MeasuredPropertyScheme"

  - cq_id: CQ-035
    file: cq-035.sparql
    type: ASK
    expected_result: "true"
    description: "Three-facet resolution concepts exist (generation + electricity + solar PV)"

  - cq_id: CQ-036
    file: cq-036.sparql
    type: SELECT
    expected_result: non_empty
    description: "Distinguishing surface forms between generation and demand"

  - cq_id: CQ-037
    file: cq-037.sparql
    type: SELECT
    expected_result: empty
    description: "MeasuredPropertyScheme covers all cold-start measuredProperty values"

  - cq_id: CQ-038
    file: cq-038.sparql
    type: SELECT
    expected_result: empty
    description: "DomainObjectScheme covers all cold-start domainObject values"

  - cq_id: CQ-039
    file: cq-039.sparql
    type: SELECT
    expected_result: non_empty
    description: "All ConceptSchemes in the vocabulary (supersedes CQ-011)"

  - cq_id: CQ-040
    file: cq-040.sparql
    type: SELECT
    expected_result: empty
    description: "No intra-scheme surface form collisions in MeasuredProperty/DomainObject schemes"

  # PolicyInstrumentScheme (UC-010)
  - cq_id: CQ-041
    file: cq-041.sparql
    type: SELECT
    expected_result: non_empty
    description: "Canonical policy instrument for 'ETS'"

  - cq_id: CQ-042
    file: cq-042.sparql
    type: SELECT
    expected_result: non_empty
    description: "Surface forms for FeedInTariff concept"

  - cq_id: CQ-043
    file: cq-043.sparql
    type: SELECT
    expected_result: empty
    description: "PolicyInstrumentScheme covers all corpus-identified instruments"

  - cq_id: CQ-044
    file: cq-044.sparql
    type: SELECT
    expected_result: empty
    description: "No intra-scheme collisions in PolicyInstrumentScheme"

  # Gap expansion (UC-011)
  - cq_id: CQ-045
    file: cq-045.sparql
    type: SELECT
    expected_result: empty
    description: "TechnologyOrFuelScheme includes Tier 1 gap concepts"

  - cq_id: CQ-046
    file: cq-046.sparql
    type: SELECT
    expected_result: empty
    description: "DomainObjectScheme covers market and grid reliability concepts"

  - cq_id: CQ-047
    file: cq-047.sparql
    type: SELECT
    expected_result: empty
    description: "MeasuredPropertyScheme includes lifecycle and performance metrics"

  - cq_id: CQ-048
    file: cq-048.sparql
    type: SELECT
    expected_result: non_empty
    description: "All ConceptSchemes after gap expansion (expects 8)"

  - cq_id: CQ-049
    file: cq-049.sparql
    type: SELECT
    expected_result: non_empty
    description: "'SMR' resolves to nuclear concept"

  - cq_id: CQ-050
    file: cq-050.sparql
    type: SELECT
    expected_result: non_empty
    description: "'LNG' resolves to natural gas concept"

  - cq_id: CQ-051
    file: cq-051.sparql
    type: SELECT
    expected_result: non_empty
    description: "'rooftop solar' resolves to solar PV concept"

  - cq_id: CQ-052
    file: cq-052.sparql
    type: SELECT
    expected_result: non_empty
    description: "'LCOE' resolves to measuredProperty concept"

  - cq_id: CQ-053
    file: cq-053.sparql
    type: SELECT
    expected_result: empty
    description: "Every active concept has at least 3 English surface forms"

  # ==========================================================================
  # DCAT Structural Extension (CQ-054 to CQ-068)
  # Variable composition + DCAT chain + structural validation
  # ==========================================================================

  # Variable Composition (UC-DM-001)
  - cq_id: CQ-054
    file: cq-054.sparql
    type: SELECT
    expected_result: exactly_7
    description: "Facet dimensions of EnergyVariable (7 qb:DimensionProperty)"

  - cq_id: CQ-055
    file: cq-055.sparql
    type: SELECT
    expected_result: non_empty
    description: "Code list for measuredProperty dimension"

  - cq_id: CQ-056
    file: cq-056.sparql
    type: SELECT
    expected_result: empty
    description: "All facet dimensions typed as qb:DimensionProperty (no violations)"

  - cq_id: CQ-057
    file: cq-057.sparql
    type: SELECT
    expected_result: non_empty
    description: "EnergyVariable is subclass of schema:StatisticalVariable"

  # DCAT Chain (UC-DM-002, UC-DM-005)
  - cq_id: CQ-058
    file: cq-058.sparql
    type: SELECT
    expected_result: non_empty
    description: "EnergyDataset has dct:publisher restriction to EnergyAgent"

  - cq_id: CQ-059
    file: cq-059.sparql
    type: SELECT
    expected_result: non_empty
    description: "hasVariable property declared with domain/range"

  - cq_id: CQ-060
    file: cq-060.sparql
    type: SELECT
    expected_result: non_empty
    description: "Variable → Dataset → Agent traversal path declared"

  - cq_id: CQ-061
    file: cq-061.sparql
    type: SELECT
    expected_result: non_empty
    description: "EnergyDataset is subclass of dcat:Dataset"

  - cq_id: CQ-062
    file: cq-062.sparql
    type: SELECT
    expected_result: non_empty
    description: "EnergyAgent is subclass of foaf:Agent"

  # Facet Completeness (UC-DM-003)
  - cq_id: CQ-063
    file: cq-063.sparql
    type: SELECT
    expected_result: non_empty
    description: "measuredProperty has maxQualifiedCardinality 1"

  - cq_id: CQ-064
    file: cq-064.sparql
    type: SELECT
    expected_result: non_empty
    description: "Required facet dimensions (SHACL minCount > 0)"

  # Dataset Discovery (UC-DM-004)
  - cq_id: CQ-065
    file: cq-065.sparql
    type: SELECT
    expected_result: non_empty
    description: "EnergyDataset has dcat:distribution restriction"

  - cq_id: CQ-066
    file: cq-066.sparql
    type: SELECT
    expected_result: non_empty
    description: "hasVariable domain/range check"

  # Full Chain Traversal (UC-DM-005)
  - cq_id: CQ-067
    file: cq-067.sparql
    type: SELECT
    expected_result: non_empty
    description: "Full facet → Variable → Dataset → Agent chain declared"

  - cq_id: CQ-068
    file: cq-068.sparql
    type: SELECT
    expected_result: exactly_7
    description: "DataStructureDefinition has exactly 7 components"

  # ==========================================================================
  # Series Chain Integrity (CQ-069 to CQ-074) — SKY-318
  # Dataset → Series → Variable structural spine introduced in SKY-316.
  # Tests are TBox/SHACL-level: they prove the ontology declares the links,
  # functional characteristics, and minCount guards that enforce the chain.
  # ABox-level consumer queries are documented inline in each fixture.
  # ==========================================================================

  - cq_id: CQ-069
    file: cq-069.sparql
    type: SELECT
    expected_result: non_empty
    description: "hasSeries object property declared with EnergyDataset domain and Series range"

  - cq_id: CQ-070
    file: cq-070.sparql
    type: SELECT
    expected_result: non_empty
    description: "implementsVariable declared as FunctionalProperty from Series to EnergyVariable"

  - cq_id: CQ-071
    file: cq-071.sparql
    type: SELECT
    expected_result: non_empty
    description: "All three chain properties (hasSeries, implementsVariable, hasVariable) declared for agreement query"

  - cq_id: CQ-072
    file: cq-072.sparql
    type: SELECT
    expected_result: non_empty
    description: "implementsVariable is FunctionalProperty but not InverseFunctionalProperty (dedup-legal many-to-one)"

  - cq_id: CQ-073
    file: cq-073.sparql
    type: SELECT
    expected_result: non_empty
    description: "SeriesShape enforces sh:minCount ≥ 1 on publishedInDataset (missing-link guard)"

  - cq_id: CQ-074
    file: cq-074.sparql
    type: SELECT
    expected_result: non_empty
    description: "Per-Agent Series + Variable chain declared (dct:publisher + hasSeries + implementsVariable)"

  # ==========================================================================
  # Semantic Reasoning Extension (CQ-075 to CQ-087)
  # BFO / OEO / QUDT alignment for domain-object reasoning. See
  # docs/competency-questions-semantic-extension.yaml for the full spec.
  # ==========================================================================

  - cq_id: CQ-075
    file: cq-075.sparql
    type: SELECT
    expected_result: non_empty
    description: "Class ancestor walk for sevocab:WTI reaches CrudeOil / OEO crude oil / BFO material entity"

  - cq_id: CQ-076
    file: cq-076.sparql
    type: SELECT
    expected_result: at_least_6
    description: "All six crude oil grade individuals enumerated from sidecar ABox"

  - cq_id: CQ-077
    file: cq-077.sparql
    type: SELECT
    expected_result: non_empty
    description: "External alignment for sevocab:WTI (owl:sameAs wd:Q1049071)"

  - cq_id: CQ-078
    file: cq-078.sparql
    type: SELECT
    expected_result: non_empty
    description: "Price_CrudeOil binds to sevocab:CostPerVolume quantity kind"

  - cq_id: CQ-079
    file: cq-079.sparql
    type: SELECT
    expected_result: non_empty
    description: "PriceOfCommodity equivalence axiom declared (Price ⊓ appliesToDomainObject some CrudeOil)"

  - cq_id: CQ-080
    file: cq-080.sparql
    type: SELECT
    expected_result: empty
    description: "STUB until CD-009 compound-concepts vocabulary is integrated (sevocab:hasComponent not yet declared)"

  - cq_id: CQ-081
    file: cq-081.sparql
    type: SELECT
    expected_result: non_empty
    description: "At least one promoted class or individual binds sevocab:hasQuantityKind"

  - cq_id: CQ-082
    file: cq-082.sparql
    type: SELECT
    expected_result: non_empty
    description: "Price_CrudeOil has a canonical unit assertion"

  - cq_id: CQ-083
    file: cq-083.sparql
    type: SELECT
    expected_result: empty
    description: "QUDT binding round-trip integrity — every subject with hasQuantityKind has exactly one value"

  - cq_id: CQ-084
    file: cq-084.sparql
    type: SELECT
    expected_result: empty
    description: "Dual-typing invariant — every CrudeOilGrade individual is also a skos:Concept in DomainObjectScheme"

  - cq_id: CQ-085
    file: cq-085.sparql
    type: SELECT
    expected_result: empty
    description: "Disjointness of CrudeOilGrade / NaturalGasHub / PowerMarket shim classes (no individual types under two)"

  - cq_id: CQ-086
    file: cq-086.sparql
    type: SELECT
    expected_result: empty
    description: "BFO leak guard — no DCAT-layer class has a BFO ancestor (CRITICAL — must return 0)"

  - cq_id: CQ-087
    file: cq-087.sparql
    type: SELECT
    expected_result: empty
    description: "Onshore/offshore wind disjointness (no individual is both)"

  # ──────────────────────────────────────────────────────────────────────
  # TBox integrity assertions (CQ-088..092)
  # Added after Phase 4 professor review caught IRI and BFO alignment
  # errors that slipped past Phase 3 validation. These CQs encode the
  # structural commitments of the alignment doc so future changes to the
  # ontology cannot silently drift from the documented intent.
  # All five MUST return empty — they assert invariants, not queries.
  # ──────────────────────────────────────────────────────────────────────

  - cq_id: CQ-088
    file: cq-088.sparql
    type: SELECT
    expected_result: empty
    description: "TBox integrity: asserted OEO parents have the expected upstream labels"

  - cq_id: CQ-089
    file: cq-089.sparql
    type: SELECT
    expected_result: empty
    description: "TBox integrity: inferred BFO classification matches alignment doc for every promoted class"

  - cq_id: CQ-090
    file: cq-090.sparql
    type: SELECT
    expected_result: empty
    description: "TBox integrity: no sevocab class classifies under two BFO-disjoint categories"

  - cq_id: CQ-091
    file: cq-091.sparql
    type: SELECT
    expected_result: empty
    description: "TBox integrity: every sevocab:hasQuantityKind target is an actual qudt:QuantityKind"

  - cq_id: CQ-092
    file: cq-092.sparql
    type: SELECT
    expected_result: empty
    description: "TBox integrity: no dangling external IRI references in sevocab subClassOf parents"

```


---

**End of bundle.** Regenerated 2026-04-21 from `scripts/build_research_bundle.py`.
