---
paths:
  - "ontologies/**/*.ttl"
  - "ontologies/**/*.owl"
  - "ontologies/**/*.rdf"
---

# Ontology Safety Rules (Non-Negotiable)

These rules apply to ALL ontology file modifications. Violations are never acceptable.
Rules 1–10 are the original non-negotiables. Rules 11–16 were added in the
2026-04 skills refactor to close gates around LLM-generated artifacts,
SSSOM provenance, and import-refresh regressions. The authoritative copy is
[`.claude/skills/CONVENTIONS.md § Safety Rules`](../skills/CONVENTIONS.md); this
file stays in sync with that one.

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
8. **Never execute SPARQL UPDATE/DELETE** against production endpoints
9. **Read before modifying** — always read the existing ontology file before making changes
10. **Back up before bulk operations** — create a checkpoint before ROBOT template or
    batch KGCL application
11. **LLM-generated artifacts must pass their tool gates before handoff.** OWL axioms,
    SHACL shapes, ROBOT templates, KGCL patches, SPARQL tests, and SSSOM mappings
    produced or proposed by an LLM are not accepted on LLM confidence alone. The
    required gates are: reasoner (`robot reason`) for OWL; `pyshacl` for SHACL;
    `robot template` must emit expected TTL with zero CURIE-resolution errors;
    `kgcl-apply` must round-trip cleanly; SPARQL must parse and return the
    expected-results shape; `sssom-py validate` plus required metadata for SSSOM.
12. **Every satisfied CQ links to an executable check.** A CQ cannot be marked
    satisfied unless paired with an executable SPARQL query (ABox CQs) or an
    entailment check (TBox CQs). See `.claude/skills/_shared/cq-traceability.md`.
13. **Accepted SSSOM mappings carry provenance.** Every merged mapping row must
    have `mapping_justification` (SEMAPV CURIE), `confidence`, `creator_id` /
    `reviewer_id`, `mapping_date`, and `mapping_tool` populated. LLM-only rows
    require human review before promotion.
14. **`skos:exactMatch` clique size > 3 requires human review** before merge.
15. **Import refresh regenerates manifest and reruns CQ regression.** Any change to
    `imports/*.ttl` or the import module list must regenerate
    `imports-manifest.yaml` and rerun the full CQ test suite.
16. **No skill silently accepts an upstream artifact that failed a declared gate.**
    If prior Progress Criteria are incomplete or a gate is failed/skipped, the
    downstream skill refuses and loops back via
    [`.claude/skills/_shared/iteration-loopbacks.md`](../skills/_shared/iteration-loopbacks.md).

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
