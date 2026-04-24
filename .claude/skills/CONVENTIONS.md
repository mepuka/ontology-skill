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
11. **Progress Criteria** — Checklist of artifacts and validation commands
    that must pass before the skill hands off. Replaces advisory phrasing
    ("ensure", "consider") with tool-checkable conditions.
12. **LLM Verification Required** — Table of operations where LLM judgment
    is used and the tool gates that must still run. LLM verification NEVER
    replaces `robot reason`, `robot report`, or `pyshacl` — see
    `_shared/llm-verification-patterns.md`.
13. **Loopback Triggers** — Table mapping failure conditions observed by
    this skill to the upstream skill that owns the fix. See
    `_shared/iteration-loopbacks.md` for the depth-3 anti-thrash guard.
14. **Worked Examples** — Concrete walkthroughs for both the Music Ensemble
    and Community Microgrid domains under
    `_shared/worked-examples/{ensemble,microgrid}/`.

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
| maintain / maintenance | housekeeping, upkeep | Ongoing curatorial work (deprecation, import refresh, release, release-note provenance). Routes to `ontology-curator`. |
| curate | groom, tend | Any of: deprecate, replace, refresh imports, publish release. Routes to `ontology-curator`. |
| evolve / evolution | update, change, revise | Versioned structural or mapping change. Routes to `ontology-curator` (change classification), then `ontology-architect` or `ontology-mapper` per change type. |
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
11. **LLM-generated artifacts must pass their tool gates before handoff.**
    OWL axioms, SHACL shapes, ROBOT templates, KGCL patches, SPARQL tests,
    and SSSOM mappings produced or proposed by an LLM are never accepted
    on LLM confidence alone. The gate is: reasoner passes for OWL; pyshacl
    passes for SHACL; `robot template` emits the expected TTL with zero
    CURIE-resolution errors; `kgcl-apply` round-trips cleanly; SPARQL
    parses and returns the expected-results shape; `sssom-py validate`
    passes plus required metadata present.
12. **Every satisfied CQ links to an executable check.** A CQ cannot be
    marked satisfied unless it is paired with an executable SPARQL query
    (for ABox CQs) or an entailment check (for TBox CQs). See
    `_shared/cq-traceability.md`.
13. **Accepted SSSOM mappings carry provenance.** Every row in a merged
    mapping set must have `mapping_justification` (SEMAPV CURIE),
    `confidence`, `creator_id` / `reviewer_id`, `mapping_date`, and
    `mapping_tool` populated. LLM-only rows require human review before
    promotion to the main mapping file.
14. **`skos:exactMatch` clique size > 3 requires human review before merge.**
    Cliques indicate either true equivalence (rare across ontologies) or
    an identifier collision. See `_shared/mapping-evaluation.md`.
15. **Import refresh regenerates manifest and reruns CQ regression.**
    Any change to `imports/*.ttl` or the import module list must (a)
    regenerate `imports-manifest.yaml` capturing each import's source,
    extraction method, and date; (b) rerun the full CQ test suite
    against the refreshed ontology. Stale imports are a curation bug,
    not a ROBOT-report warning to defer.
16. **No skill silently accepts an upstream artifact that failed a
    declared gate.** If a prior skill's Progress Criteria checklist is
    incomplete or any declared verification gate is failed/skipped, the
    downstream skill must refuse and loop back via the protocol in
    `_shared/iteration-loopbacks.md` — never "fix it quietly" in its
    own phase.

## Iteration and Loopback Protocol

Skills are not strictly linear. When a downstream skill detects that an
upstream artifact fails a declared gate, it raises a **loopback** rather
than patching the artifact locally. See
[`_shared/iteration-loopbacks.md`](_shared/iteration-loopbacks.md) for
the full protocol, anti-thrash guard, and examples.

### Loopback record

Every loopback produces an entry in `docs/loopbacks/{date}-{short-id}.md`
with these fields:

| Field | Meaning |
|-------|---------|
| `rejecting_skill` | Skill that detected the gate failure |
| `source_skill` | Skill that produced the failing artifact |
| `artifact` | Path to the failing artifact |
| `failure_type` | One of: *unsatisfiable class*, *scope violation*, *missing CQ link*, *profile violation*, *SHACL violation*, *mapping conflict*, *missing provenance*, *stale import*, *routing collision* |
| `evidence` | Log/report path that demonstrates the failure |
| `required_fix` | Concrete change the source skill must make |
| `retry_gate` | Exact command the downstream skill will rerun on return |

### Default routing table

The downstream skill routes loopbacks to these owners unless an explicit
override is specified in `_shared/iteration-loopbacks.md`:

| Failure type | Routes to |
|--------------|-----------|
| scope ambiguity, missing CQ, non-goal violation | `ontology-requirements` |
| missing reuse, bad module selection, import provenance | `ontology-scout` |
| role/type confusion, BFO misalignment, taxonomy error, closure gap | `ontology-conceptualizer` |
| axiom-level issue: unsatisfiability, profile violation, construct/reasoner mismatch, ROBOT-template failure | `ontology-architect` |
| mapping confidence, SEMAPV missing, clique > 3, cross-domain exactMatch | `ontology-mapper` |
| CQ query fails to parse or returns wrong shape | `sparql-expert` |
| change classification, release gate, stale import trigger | `ontology-curator` |
| quality-report violation with severity ≥ ERROR | source skill of the violating axiom (validator raises; architect or mapper fixes) |

### Anti-thrash guard

A loopback cycle that exceeds depth 3 between the same two skills must
be escalated to human review (append `[ESCALATE]` to the loopback
record). Common causes: disagreement on BFO placement, mapping target
scope, or CQ wording. Do not continue looping.

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
