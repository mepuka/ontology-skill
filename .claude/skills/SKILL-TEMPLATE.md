<!-- SKILL-TEMPLATE.md — Copy this file to create a new SKILL.md -->
<!-- Replace all {placeholders} with actual values -->
<!-- Delete this comment block in the final SKILL.md -->
<!-- Sections must appear in this exact order (CONVENTIONS.md § Skill Authoring Standard) -->

---
name: {skill-name}
description: >
  {One to three sentence description of the skill's purpose. Include
  every keyword that currently triggers activation (preserve existing
  trigger vocabulary). Name the artifact this skill produces, and the
  tool gate that certifies it.}
---

# {Skill Title}

## Role Statement

{What this skill is, what it is responsible for, and what it is NOT
responsible for. 2-3 sentences. Call out the neighbouring skill(s) the
user might confuse this one with and why this skill owns the current
question.}

## When to Activate

- {Trigger condition 1: user keywords or phrases}
- {Trigger condition 2: pipeline stage or prerequisite}
- {Trigger condition 3: specific user intent}

## Shared Reference Materials

Read these files from `_shared/` before beginning work:

- `_shared/methodology-backbone.md` — lifecycle phase context
- `_shared/iteration-loopbacks.md` — loopback protocol and depth-3 guard
- `_shared/llm-verification-patterns.md` — when LLM judgment is used
- `_shared/{relevant-reference}.md` — {why this skill needs it}

## Core Workflow

Each step ends in an artifact plus a checkable command. Replace
advisory verbs ("consider", "ensure") with tool-checkable conditions.

### Step 1: {Step Name}

{Description of what to do.}

```bash
{Concrete command example}
```

**Artifact:** `{path}` — **Checked by:** `{command}`

### Step 2: {Step Name}

{Description of what to do.}

**Artifact:** `{path}` — **Checked by:** `{command}`

### Step N: {Step Name}

{Description of what to do.}

**Artifact:** `{path}` — **Checked by:** `{command}`

## Tool Commands

{Concrete CLI and Python examples for every operation this skill
performs. Group by operation type. Include exact flags and arguments.
Prefer `uv run python` or `robot`; never `sed`/`awk` against `.ttl`,
`.owl`, `.rdf`, `.ofn`, or `.owx` (blocked by
`guard-sed-ontology.sh`).}

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

**Receives from:** {previous skill(s)} — {what artifacts are expected
as input, and the Progress-Criteria checklist this skill requires to
be complete before it begins work}

**Passes to:** {next skill(s)} — {what artifacts are produced for the
next stage}

**Handoff checklist:**
- [ ] {Required artifact 1 exists at `{path}` and validates with `{command}`}
- [ ] {Required artifact 2 exists at `{path}` and validates with `{command}`}
- [ ] All Progress Criteria below are satisfied
- [ ] All Loopback Triggers below were evaluated; none fire

## Anti-Patterns to Avoid

- {Anti-pattern 1}: {why it's wrong, what to do instead, and what tool
  detects it}
- {Anti-pattern 2}: {why it's wrong, what to do instead, and what tool
  detects it}

## Error Handling

| Error | Likely Cause | Recovery |
|-------|-------------|----------|
| {Error type} | {Common cause} | {What to do} |

## Progress Criteria

Work is done when every box is checked. No advisory language: each
item must be verifiable by running the paired command.

- [ ] {Artifact 1} exists at `{path}` and passes `{command}`
- [ ] {Artifact 2} exists at `{path}` and is referenced from the handoff
- [ ] Every CQ claimed satisfied links to an executable check
      (`_shared/cq-traceability.md`)
- [ ] No items in the Loopback Triggers table below fire

## LLM Verification Required

Prompt templates and acceptance conditions live in
[`_shared/llm-verification-patterns.md`](_shared/llm-verification-patterns.md).
LLM verification NEVER replaces `robot reason`, `robot report`,
`pyshacl`, or `robot validate-profile`.

| Operation | Why LLM verification is used | Replaces | Does NOT replace |
|-----------|------------------------------|----------|------------------|
| {op 1} | {risk that requires a second look} | {prior step it replaces} | reasoner, ROBOT report, pyshacl |

## Loopback Triggers

When one of these conditions fires, raise a loopback per
[`_shared/iteration-loopbacks.md`](_shared/iteration-loopbacks.md)
rather than patching locally. Cycles of depth > 3 escalate to human
review.

| Trigger | Route to | Reason |
|---------|----------|--------|
| {condition 1: e.g., unsatisfiable class detected} | `{upstream-skill}` | {why that skill owns the fix} |
| {condition 2: e.g., CQ fails with no candidate term} | `{upstream-skill}` | {why that skill owns the fix} |

## Worked Examples

Both domains are monorepo-local under
`.claude/skills/_shared/worked-examples/`. Cite specific sections when
answering, not whole files.

- [`_shared/worked-examples/ensemble/{this-skill}.md`](_shared/worked-examples/ensemble/{this-skill}.md) — {one-line summary of what the ensemble walk-through demonstrates for this skill}
- [`_shared/worked-examples/microgrid/{this-skill}.md`](_shared/worked-examples/microgrid/{this-skill}.md) — {one-line summary of what the microgrid walk-through demonstrates for this skill}
