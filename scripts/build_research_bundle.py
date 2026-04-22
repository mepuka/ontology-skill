#!/usr/bin/env python3
# ruff: noqa: E501, RUF001
"""Build the ontology workspace workflow-improvement research bundle.

Assembles a single self-contained markdown document intended for a
GPT-5.4 Pro research session. The bundle contains:

  Part I  — Synthesis: what this workspace is, why it exists, what has
            been built, what the current 8-skill architecture looks
            like, and where it diverges from professional ontologist
            practice.

  Part II — Verbatim reference material: all 8 SKILL.md files, shared
            reference materials under `.claude/skills/_shared/`, the
            skill authoring conventions (`CONVENTIONS.md`) and template,
            the root `CLAUDE.md`, and the in-repo practitioner-insights
            document that surfaces real-world gaps.

Regenerate with:

    uv run python scripts/build_research_bundle.py

Output path (stable):

    docs/research/2026-04-21-workflow-improvement-context.md

The companion research prompt lives at:

    docs/research/2026-04-21-workflow-improvement-prompt.md
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs/research/2026-04-21-workflow-improvement-context.md"


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def read(rel: str) -> str:
    return (REPO / rel).read_text()


def fenced(rel: str, heading: str | None = None) -> str:
    """Embed a repo file verbatim inside a fenced block, with a heading."""
    body = read(rel)
    ext = Path(rel).suffix.lstrip(".")
    lang = {
        "md": "markdown",
        "json": "json",
        "yaml": "yaml",
        "yml": "yaml",
        "py": "python",
        "ttl": "turtle",
        "sparql": "sparql",
    }.get(ext, "")
    return (
        f"\n\n### `{rel}`" + (f" — {heading}" if heading else "") + f"\n\n```{lang}\n{body}\n```\n"
    )


def section(title: str, body: str, level: int = 2) -> str:
    return f"\n\n{'#' * level} {title}\n\n{body.strip()}\n"


# --------------------------------------------------------------------------
# Front matter (synthesis authored for the research session)
# --------------------------------------------------------------------------

HEADER = """\
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
"""

PART_I_OVERVIEW = """\
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
"""


PART_I_INTELLECTUAL = """\
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
"""


PART_I_ARCHITECTURE = """\
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
"""


PART_I_TOOLING = """\
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
  matches `(sed|awk|perl).*\\.(ttl|owl|rdf|ofn|owx)`, deny execution
  with a message instructing the agent to use ROBOT / oaklib /
  Python instead. Enforces Safety Rule #1.
- **`protect-ontology-files.sh`** (PreToolUse:Edit|Write) — If the
  target is under `ontologies/` and matches
  `\\.(ttl|owl|rdf|xml)`, emit an advisory
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
"""


PART_I_ONTOLOGIES = """\
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
"""


PART_I_GAPS = """\
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
"""


PART_I_SKILL_QUALITY = """\
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
"""


PART_I_QUESTIONS = """\
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
"""


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------


def build() -> str:
    parts: list[str] = []
    parts.append(HEADER)
    parts.append(PART_I_OVERVIEW)
    parts.append(PART_I_INTELLECTUAL)
    parts.append(PART_I_ARCHITECTURE)
    parts.append(PART_I_TOOLING)
    parts.append(PART_I_ONTOLOGIES)
    parts.append(PART_I_GAPS)
    parts.append(PART_I_SKILL_QUALITY)
    parts.append(PART_I_QUESTIONS)

    # -----------------------------------------------------------------
    # Appendix A: skill files (verbatim)
    # -----------------------------------------------------------------
    parts.append(
        "\n\n---\n\n# Appendix A: Skill Authoring Conventions and Skill Files (Verbatim)\n"
    )
    parts.append(
        "\nThe following files are embedded verbatim. They are the "
        "canonical source; any synthesis above should be cross-checked "
        "against them.\n"
    )
    parts.append(fenced(".claude/skills/CONVENTIONS.md", "Skill authoring standard"))
    parts.append(fenced(".claude/skills/SKILL-TEMPLATE.md", "Template for new skills"))
    parts.extend(
        fenced(f".claude/skills/{skill}/SKILL.md", f"{skill} skill")
        for skill in [
            "ontology-requirements",
            "ontology-scout",
            "ontology-conceptualizer",
            "ontology-architect",
            "ontology-mapper",
            "ontology-validator",
            "ontology-curator",
            "sparql-expert",
        ]
    )

    # -----------------------------------------------------------------
    # Appendix B: shared reference materials (verbatim)
    # -----------------------------------------------------------------
    parts.append("\n\n---\n\n# Appendix B: Shared Reference Materials (Verbatim)\n")
    parts.extend(
        fenced(f".claude/skills/_shared/{shared}", heading)
        for shared, heading in [
            ("methodology-backbone.md", "Lifecycle phase mapping and pipelines"),
            ("tool-decision-tree.md", "Tool selection flowchart and limitations"),
            ("bfo-categories.md", "BFO decision procedure and known ambiguities"),
            ("axiom-patterns.md", "16 OWL 2 axiom patterns"),
            ("anti-patterns.md", "16 modeling anti-patterns with SPARQL detection"),
            ("naming-conventions.md", "Term naming, IRI governance, definitions"),
            ("quality-checklist.md", "Pre-commit/pre-release quality gates"),
            ("namespaces.json", "Canonical prefix-to-IRI map"),
        ]
    )

    # -----------------------------------------------------------------
    # Appendix C: root project instructions
    # -----------------------------------------------------------------
    parts.append("\n\n---\n\n# Appendix C: Root Project Instructions\n")
    parts.append(fenced("CLAUDE.md", "Root CLAUDE.md"))

    # -----------------------------------------------------------------
    # Appendix D: practitioner insights
    # -----------------------------------------------------------------
    parts.append("\n\n---\n\n# Appendix D: Practitioner Insights\n")
    parts.append(
        "\nThis document is the in-repo record of real-world OBO Foundry / "
        "ontology engineering practice and where current skill guidance "
        "diverges from it.\n"
    )
    parts.append(fenced("docs/practitioner-insights.md", "17 themes + priority gap table"))

    # -----------------------------------------------------------------
    # Appendix E: auto-loading rules
    # -----------------------------------------------------------------
    parts.append("\n\n---\n\n# Appendix E: Auto-Loading Rules (Verbatim)\n")
    parts.append(
        "\nThese files attach to file-path patterns and get injected "
        "into agent context when relevant files are opened.\n"
    )
    parts.extend(
        fenced(f".claude/rules/{rule}", f"{rule} rule")
        for rule in [
            "ontology-safety.md",
            "ontology-build-scripts.md",
            "ontology-testing.md",
        ]
    )

    # -----------------------------------------------------------------
    # Appendix F: hooks
    # -----------------------------------------------------------------
    parts.append("\n\n---\n\n# Appendix F: Safety Hooks (Verbatim)\n")
    parts.extend(
        fenced(f".claude/hooks/{hook}")
        for hook in [
            "post-ontology-write.sh",
            "guard-sed-ontology.sh",
            "protect-ontology-files.sh",
        ]
    )

    # -----------------------------------------------------------------
    # Appendix G: active ontology — skygest-energy-vocab docs (selected)
    # -----------------------------------------------------------------
    parts.append("\n\n---\n\n# Appendix G: Active Ontology Reference — skygest-energy-vocab\n")
    parts.append(
        "\nSelected documents from the mature exemplar ontology. These "
        "show what a real POD project in this workspace looks like in "
        "practice, including the CQ suite, validation report, and DCAT "
        "structural extension axiom plan.\n"
    )
    for path, heading in [
        (
            "ontologies/skygest-energy-vocab/docs/scope.md",
            "skygest-energy-vocab scope and in/out-of-scope",
        ),
        (
            "ontologies/skygest-energy-vocab/docs/validation-report-2026-04-14.md",
            "Most recent validation report",
        ),
        (
            "ontologies/skygest-energy-vocab/docs/axiom-plan-dcat-extension.yaml",
            "DCAT structural extension axiom plan",
        ),
        ("ontologies/skygest-energy-vocab/tests/cq-test-manifest.yaml", "CQ test manifest"),
    ]:
        try:
            parts.append(fenced(path, heading))
        except FileNotFoundError:
            parts.append(
                f"\n### `{path}`\n\n*(file not found at build time — may have "
                f"moved; check `git log -- {path}`.)*\n"
            )

    # Footer
    parts.append(
        "\n\n---\n\n"
        f"**End of bundle.** Regenerated {_dt.datetime.now(_dt.UTC).date().isoformat()} "
        "from `scripts/build_research_bundle.py`.\n"
    )
    return "".join(parts)


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    text = build()
    OUT.write_text(text)
    print(f"wrote {OUT} ({len(text):,} chars, {text.count(chr(10)):,} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
