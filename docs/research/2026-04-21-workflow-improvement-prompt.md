---
title: Ontology Skills Workflow Improvement — Research Prompt
date: 2026-04-21
audience: GPT-5.4 Pro (deep research session)
companion_bundle: docs/research/2026-04-21-workflow-improvement-context.md
---

# Research Prompt: Refine the Ontology-Engineering Skill Suite

You are an expert in ontology engineering, OBO Foundry practice,
Description Logic, and **also** in agent-harness design — specifically
the Anthropic Claude Code skill format (YAML-frontmatter markdown files
that get loaded as LLM context on trigger). You have been given a
complete context bundle for a Programmatic Ontology Development (POD)
workspace at
`docs/research/2026-04-21-workflow-improvement-context.md`. Treat that
bundle as your source of truth; skim the synthesis, then read the
verbatim skill files, shared materials, `CONVENTIONS.md`, `CLAUDE.md`,
and `practitioner-insights.md` in full before producing your
recommendations.

Your task has two halves, and you must deliver both.

## Half 1 — Critique

Produce an explicit, rigorous critique of the current skill suite
along the following dimensions. For every point, cite the file and
section you are critiquing.

### 1. Skill-authoring quality (Anthropic-style)

Evaluate each of the 8 `SKILL.md` files and the `CONVENTIONS.md` /
`SKILL-TEMPLATE.md` governing them against Anthropic skill-creator
best practice:

- **Description field quality.** Is the `description` rich enough that
  a routing LLM will consistently pick this skill for relevant
  intents? Does it include the non-obvious trigger phrases that users
  will actually say? Are there ambiguities that overlap with other
  skills?
- **Progressive disclosure.** Anthropic skills favor a compact
  SKILL.md that references deeper material. Is the split between
  SKILL.md and `_shared/` correct? Are there SKILL.md sections that
  duplicate shared content, or shared content that should be
  inlined for a specific skill?
- **Workflow actionability.** Does each Core Workflow step give the
  agent enough to execute it? Are there steps that read as guidance
  rather than instructions? Are there steps that would fail silently
  if the agent skipped a sub-detail?
- **Handoff specification.** Are the handoff artifacts and checklists
  precise enough that the next skill can deterministically verify the
  inbound state? Are there implicit assumptions (e.g., "conceptual
  model has been approved by user" — how?) that should be explicit
  process gates?
- **Anti-patterns and error handling.** Are anti-patterns just
  warnings, or do they have detection mechanisms (SPARQL,
  preflight checks, hook triggers)? Are error-handling tables
  comprehensive and actionable?

Call out the top 3 weakest and top 3 strongest skill files, with
concrete quote-level evidence.

### 2. Methodology-to-agent fidelity

The workspace claims to mirror professional ontology engineering
(METHONTOLOGY, NeOn, CQ-driven, Kendall–McGuinness, Arp/Smith/Spear
BFO, Hogan Knowledge Graphs). Where does the agent-first
reformulation succeed, and where does it distort the methodology?
Specific questions:

- Does the lifecycle phase mapping in
  `_shared/methodology-backbone.md` faithfully represent Kendall &
  McGuinness's 9-phase workflow? What is lost in translation?
- Is the three-pipeline model (A: new ontology, B: mapping, C:
  evolution) the right decomposition, or does it artificially
  linearize work that practitioners do iteratively?
- Is the CQ through-line — specification → reuse guidance →
  conceptualization → axioms → acceptance tests → maintenance —
  actually sustained across skills, or does it degrade into
  optional nice-to-have guidance in later phases?
- Does the BFO alignment procedure in `_shared/bfo-categories.md`
  acknowledge the known ambiguities sufficiently, and does the
  conceptualizer skill route the agent to them when encountering
  ambiguous concepts?

### 3. Professional-ontologist parity

The in-repo `practitioner-insights.md` identifies 17 themes. Several
have been partially addressed; several remain open (see Part I §6 of
the bundle). Your job is **not** to restate that list; your job is to
go deeper:

- What **additional** professional practices are missing that the
  document does not mention? Examples to investigate: pattern-based
  modeling with OWL Expansion patterns, ontology alignment evaluation
  metrics (OAEI-style), modularization via the E-connections approach,
  closure-axiom discipline, provenance modeling with PROV-O in
  realistic granularity, bridge-ontology maintenance, ontology-as-a-service
  endpoints with content negotiation, schema.org JSON-LD export for
  SEO/discoverability.
- Where in the current skill suite would each of these additions
  land (which skill, which shared reference, which section)?
- For each, what is the minimum viable addition (a paragraph of
  guidance, a new shared material, a new workflow step, a new
  skill) vs. the complete treatment?

### 4. Agent-specific failure modes

LLMs do some ontology-engineering tasks well (CQ-to-SPARQL
translation, definition drafting, mapping verification, synonym
generation) and others badly (complex DL axiom syntax, reasoner
behavior simulation, large-scale ontology coherence, nuanced BFO
alignment). The current skills encode some of this awareness but
not systematically:

- Which skills need explicit "LLM verification required" markers
  before a step's output is accepted? How should that marker be
  encoded in the SKILL.md format?
- Where should the skill force the agent to invoke a secondary
  tool (ROBOT reason, pyshacl, SPARQL preflight) before claiming
  completion? Are any such checks currently implicit and should
  be made explicit?
- How should skills handle the "confident but wrong" problem
  (LLM emits an axiom with high confidence that fails
  reasoning)? What is the recommended recovery workflow?

### 5. Architectural coherence

- Is 8 the right number of skills? Should `ontology-architect` be
  split (e.g., ROBOT-template skill, KGCL skill, OWL-axiom skill,
  reasoning skill)? Should `sparql-expert` and `ontology-validator`
  stay as cross-cutting skills or be subsumed?
- Are the pipelines the right decomposition, or should there be
  additional named pipelines (e.g., "audit existing ontology",
  "add N classes to an existing ontology", "refresh imports after
  upstream release")?
- Is the shared reference set complete? Missing candidates
  surfaced by `practitioner-insights.md`: `shacl-patterns.md`,
  `odk-integration.md`, `imports-manifest.md`,
  `github-actions-template.md`, `llm-verification-patterns.md`,
  `worked-examples/` (per domain: music, astronomy, energy).

## Half 2 — Concrete Recommendations

Produce an actionable, prioritized improvement plan. Use this
structure:

### A. Per-skill redline

For each of the 8 skills, produce a short "redline" that lists:

- Description field (proposed new text, with rationale).
- Activation triggers (proposed new list, deduplicated against
  other skills).
- Structural changes to the workflow (steps added, removed,
  reordered, merged, split).
- New shared-reference dependencies, if any.
- Worked examples to add (name the example, specify what it
  demonstrates, e.g., "StringQuartet qualified cardinality →
  ELK silent ignore → HermiT fix").
- Handoff-checklist changes.
- Anti-patterns to add/remove.

Output each per-skill redline as a compact spec (target: one page
of text per skill, max).

### B. Shared-material changes

For each existing `_shared/*.md` file, specify:

- What should be kept.
- What should be expanded (with the expansion summarized).
- What should be extracted into a new shared file.

Propose the specific new shared-reference files that should
exist, with a one-paragraph description of each and a list of
which skills will reference them.

### C. Governance changes

For `CONVENTIONS.md`:

- Are the ten non-negotiable safety rules the right set? Any to
  add (e.g., "LLM-generated axioms must be reasoned before
  handoff"; "cross-ontology mappings must be clique-checked before
  merge")? Any to relax (e.g., the hand-edit exception for
  annotation-only changes is already relaxed — is there anything
  else that should be tightened or loosened)?
- Should there be an "iteration and loopback" section codifying
  when a downstream skill can reject a handoff and loop back?
- Should the authoring standard add required sections for
  "Examples", "LLM verification required", or "Progress criteria"?

For `SKILL-TEMPLATE.md`, propose updated boilerplate reflecting
all governance changes.

### D. New skills or merged skills

If you recommend any reshaping of the 8-skill set (split or
merge), provide:

- The new skill boundary and YAML frontmatter for each affected
  skill.
- The handoff diff (which artifacts move between which skills).
- The migration plan (what needs to be extracted from existing
  files to populate the new ones).

### E. Worked-example library

Design a small worked-example library (a "demo domain") that
exercises all 8 skills end-to-end. Criteria:

- Small enough to be auditable in one research session
  (≤ 30 classes, ≤ 10 CQs).
- Covers at least one each of: BFO Object, Role, Quality,
  Process, GDC; qualified cardinality; property chain; disjoint
  union; value partition.
- Serves as both pedagogy (users learn the skills) and
  eval harness (future skill changes can be tested against it).

Propose the domain, the seed term list, the five highest-priority
CQs, and the axiom patterns the demo should exercise.

### F. Evaluation harness

Propose a concrete evaluation harness the workspace should
implement to measure whether proposed skill changes improve
agent performance. Minimum viable version:

- A held-out set of ontology-engineering tasks (e.g., "given
  these 20 natural-language CQs, generate SPARQL and axiom
  plans"; "given this ontology, detect anti-patterns").
- Automated scoring (reasoner, ROBOT report, CQ test pass
  rate, anti-pattern detection F1).
- A baseline (current skills, frozen) so regression can be
  detected.

### G. Prioritized roadmap

Rank all recommendations by (impact × confidence ÷ effort) and
present the top-20 as a sequenced plan. For each, specify:

- Exact file(s) to change.
- Summary of the change.
- Estimated effort (XS / S / M / L).
- Blocking dependencies.

## Output Format

Return a single markdown document with this structure:

```
# Ontology Skills Improvement — Research Output

## Part I — Critique

### 1. Skill-authoring quality
### 2. Methodology-to-agent fidelity
### 3. Professional-ontologist parity
### 4. Agent-specific failure modes
### 5. Architectural coherence

## Part II — Recommendations

### A. Per-skill redlines (one subsection per skill, 8 total)
### B. Shared-material changes
### C. Governance changes (CONVENTIONS.md, SKILL-TEMPLATE.md)
### D. New or merged skills
### E. Worked-example library design
### F. Evaluation harness design
### G. Prioritized roadmap (top-20)

## Appendix — Open questions back to the repo owner
```

Length: go as long as needed for rigor. This will feed a
multi-session implementation effort; completeness is more
valuable than brevity.

## Non-goals and constraints

- **Do not** propose abandoning BFO as the default upper
  ontology. The workspace is committed to BFO for the skygest
  energy exemplar; you may propose pluggable upper-ontology
  support but not removal.
- **Do not** propose moving away from ROBOT / oaklib as the
  primary tools. They are load-bearing.
- **Do not** propose rewriting the workspace in another language
  (Rust, TypeScript). Python + uv is set.
- **Do** challenge assumptions elsewhere: iteration model, skill
  decomposition, description style, worked-example depth,
  governance scope.
- **Do** ground every recommendation in either the bundle's
  primary source material or in explicitly-named external
  authorities (OBO Foundry principles, FAIR Data Principles,
  ISO 21838-2, Gruninger & Fox 1995, Kendall & McGuinness 2019,
  Arp/Smith/Spear 2015, Hogan et al. 2021, SSSOM spec,
  relevant OAEI papers).

## Style

- Direct, technical, specific. No hedging without reason.
- When you disagree with a design choice in the current
  workspace, say so and explain why, with evidence.
- Prefer precise diff-style recommendations over abstract
  exhortations. "Add a 'Progress criteria' subsection to
  `ontology-conceptualizer/SKILL.md` between Step 2.5 and
  Step 3 with the following content: ..." beats "add more
  rigor to progress criteria."
- Use file paths with line references where helpful.

Begin.
