# LLM Verification Patterns

**Referenced by:** every SKILL.md's `## LLM Verification Required` section.
**Rule:** LLM verification augments tool gates; it never replaces them.

An ontology artifact produced or proposed by an LLM (axiom, SHACL shape,
ROBOT template row, KGCL patch, SPARQL query, SSSOM mapping row,
definition text, BFO placement) must clear one or more of the verification
classes below before it is merged. LLM judgment alone is never sufficient;
the reasoner, `robot report`, `pyshacl`, `robot validate-profile`, and
`sssom-py validate` are the authoritative gates.

## 1. Why LLM verification exists

LLMs are fluent at producing ontology-shaped text. They fail differently
from humans:

- Confident, syntactically clean output that violates the intended semantics.
- Correct-looking CURIEs that resolve to the wrong term (hallucinated IRIs).
- Definitions that conflate role, type, and process.
- Mapping predicates that are plausible but not supported by the labels and
  parents of the terms on either side.
- Axiom patterns that work in one profile and silently mis-reason in another.

Tool gates catch most structural and logical errors. LLM verification
catches semantic errors that the tools would accept as valid.

## 2. Four verification classes

Each step in every skill's workflow that produces LLM output must name one
of these classes in its `## LLM Verification Required` table.

### Class A — Tool-gated generation

The LLM proposes, the tool certifies. Examples: ROBOT template rows, KGCL
patches, SHACL shapes, SPARQL queries.

**Acceptance:** tool exits zero **and** the structural check (e.g.,
reasoner, pyshacl) is clean **and** the downstream effect matches the
expected-results contract.

**If the tool rejects:** quarantine the artifact to `work/failed/{date}-{id}/`,
raise a loopback to the source skill per
[`iteration-loopbacks.md`](iteration-loopbacks.md), and attach the raw
tool output as evidence.

### Class B — LLM-verified candidate

The LLM generates candidates; a second LLM pass or a rubric reviews each
candidate against evidence. Examples: SSSOM mapping rows proposed by
lexmatch then LLM-reviewed, reuse recommendations from `ontology-scout`.

**Acceptance:** each candidate carries structured evidence (labels,
definitions, parents, surrounding axioms), an explicit decision, a
confidence, and a `mapping_justification` (for mappings) or a
rejection-rationale (for reuse candidates).

**If evidence is missing:** the candidate is not accepted, even if the
LLM is "confident".

### Class C — Human review required

The LLM decision is advisory; a human curator signs off before the artifact
leaves the skill. Examples: cross-domain `skos:exactMatch`, clique > 3,
BFO placement at ambiguity level ≥ 2, non-goal scope expansions, `skos:sameAs`
between classes.

**Acceptance:** named reviewer, ISO-formatted date, brief rationale.
Waiver rules per `iteration-loopbacks.md § 6`.

### Class D — No LLM output permitted

Some operations must be tool-driven only. Examples: `robot reason` output,
`pyshacl` violations, `robot report` rows, `robot diff` output, reasoner
inconsistency traces. Do not paraphrase; attach the raw tool output.

## 3. Standard prompt template for Class B

Use this template whenever a skill asks an LLM to verify a candidate
artifact. Variants appear in worked examples for `ontology-mapper` and
`ontology-scout`.

```text
You are reviewing a candidate {ontology artifact type}.

Evidence:
- Source term: {iri} | label: {label} | definition: {def} | parents: [{p1, p2}]
- Target term: {iri} | label: {label} | definition: {def} | parents: [{p1, p2}]
- Tool-proposed relation: {predicate}
- Tool confidence: {n}
- Additional context: {surrounding axioms / sibling terms / usage examples}

Task:
1. Decide whether the proposed relation is supported by the evidence.
2. Classify confidence: {HIGH | MEDIUM | LOW}.
3. Supply a `mapping_justification` from SEMAPV (or equivalent).
4. If rejecting, propose an alternative relation or mark the candidate
   for human review.

Output (strict JSON):
{
  "decision": "accept | reject | human-review",
  "confidence": "HIGH | MEDIUM | LOW",
  "justification": "semapv:...",
  "rationale": "1-2 sentences referencing the evidence",
  "alternative": "optional: predicate + brief reason"
}
```

## 4. Verification by skill

Redline summary. Full workflow detail lives in each SKILL.md and its
worked examples.

| Skill | Operations requiring LLM verification | Required tool/check before acceptance |
|-------|---------------------------------------|---------------------------------------|
| `ontology-requirements` | CQ-to-SPARQL, sample-answer generation, traceability rows | `rdflib.plugins.sparql.prepareQuery` parse; run against fixture when present; CQ manifest consistency |
| `ontology-scout` | Reuse recommendation; import term list; ODP recommendation | `runoak info` term existence; license metadata; `robot extract`; `robot validate`; candidate CQ probes |
| `ontology-conceptualizer` | BFO alignment, genus-differentia definitions, axiom-plan draft, property design | anti-pattern scan; BFO ambiguity register; domain/range decision record; human gate at ambiguity ≥ 2 |
| `ontology-architect` | OWL axioms, ROBOT templates, KGCL patches, SHACL shape drafts | `robot validate-profile` → `robot reason` (matched reasoner) → `robot report` → `pyshacl` → template preflight |
| `ontology-mapper` | Mapping predicate selection, confidence, bridge-ontology conversion | `sssom-py validate`; entity existence; predicate-conflict check; exactMatch clique report; OAEI metrics where gold set exists |
| `ontology-validator` | Natural-language root-cause interpretation | Raw reasoner / report / pyshacl / CQ logs attached — never paraphrase |
| `ontology-curator` | KGCL change plan, deprecation rationale, release notes, import refresh | KGCL dry-run/apply log; `robot diff`; reason/report; obsolete-term + replacement check; import-manifest regeneration |
| `sparql-expert` | SPARQL generation and optimization | `prepareQuery` parse; run on fixture or target graph; entailment regime declared; `expected_results_contract` match |

## 5. Confidence reconciliation

When multiple evidence sources disagree (e.g., lexmatch says 0.86 but an
LLM rationale is weak), use the following order of precedence:

1. Tool-computed metric that is grounded in source text (lexmatch similarity,
   `robot report` severity, `pyshacl` severity).
2. Authoritative axioms in the source ontology (disjointness, parents).
3. LLM rubric output with evidence.
4. LLM confidence string alone.

Never merge on level 4 without a level 2 corroboration.

## 6. Failure ledger

Every LLM-produced artifact that a tool later rejects is logged to
`docs/llm-failure-ledger.md` with: generated text, failed check, tool
output excerpt, root cause, correction, and a prevention rule (e.g., add
a regression CQ, tighten the preflight, add an anti-pattern).

The ledger is read at the start of each skill session as part of its
Shared Reference Materials — lessons from past failures raise the cost of
repeating them.

## 7. What LLM verification does NOT replace

These tool gates are non-negotiable regardless of LLM verification output:

- `robot validate-profile --profile {DL|EL|QL|RL}` for OWL artifacts.
- `robot reason --reasoner {ELK|HermiT|Pellet|Openllet}` after structural change.
- `robot report --fail-on ERROR` before release.
- `pyshacl` for every shape graph.
- `sssom-py validate` for every mapping file.
- `prepareQuery` parse for every SPARQL test.
- `runoak info` for every CURIE an LLM claims exists.

LLM verification is a check added on top of these gates, never in place of them.

## 8. Worked examples

See (created in Wave 4):

- [`worked-examples/ensemble/mapper.md`](worked-examples/ensemble/mapper.md) — Class B prompt over a lexmatch candidate pair.
- [`worked-examples/microgrid/mapper.md`](worked-examples/microgrid/mapper.md) — Class C human-review trigger on a cross-domain exactMatch.
- [`worked-examples/ensemble/architect.md`](worked-examples/ensemble/architect.md) — Class A tool gate catching a Class B confident-but-wrong axiom.
