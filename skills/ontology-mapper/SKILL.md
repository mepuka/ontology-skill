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
  -R sqlite:obo:{target} \
  -o mappings/{source}-to-{target}.sssom.tsv
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
  -R sqlite:obo:{target} \
  --rules lexmatch-rules.yaml \
  -o mappings/{source}-to-{target}.sssom.tsv
```

### Step 2: Confidence Triage

Sort candidates into three tiers:

| Tier | Confidence | Action |
|------|-----------|--------|
| Auto-accept | ≥ 0.95 AND exact label match | Accept with `semapv:LexicalMatching` justification |
| LLM-verify | 0.7 – 0.95 | Present to LLM for semantic evaluation |
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
uv run sssom validate mappings/{source}-to-{target}.sssom.tsv
```

Check:
- Schema conformance (valid SSSOM TSV)
- CURIE resolution (all prefixes in curie_map)
- Entity existence (subjects/objects exist in source/target)
- Predicate consistency (no contradictory predicates for same pair)
- No self-mappings (subject ≠ object)
- No duplicate mappings

### Step 6: Quality Report

Generate a quality assessment:

- Predicate distribution (how many of each type)
- Confidence distribution (histogram)
- Source coverage (% of source terms mapped)
- Target coverage (% of target terms mapped)
- Potential conflicts (same subject mapped to multiple objects with
  exactMatch)
- Clique analysis (transitive closure of exactMatch)

## Tool Commands

### SSSOM operations

```bash
# Validate
uv run sssom validate mappings/file.sssom.tsv

# Merge mapping sets
uv run sssom merge \
  -i set1.sssom.tsv set2.sssom.tsv \
  -o merged.sssom.tsv

# Deduplicate
uv run sssom dedupe -i merged.sssom.tsv -o final.sssom.tsv

# Convert to OWL (bridge ontology)
uv run sssom convert -i mappings/file.sssom.tsv -o bridge.owl -O owl
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
| Mapping file | `mappings/{source}-to-{target}.sssom.tsv` | SSSOM TSV | Complete mapping set with metadata |
| Quality report | `mappings/{source}-to-{target}-qa.md` | Markdown | Quality assessment with statistics |
| Human review queue | `mappings/{source}-to-{target}-review.tsv` | TSV | Low-confidence pairs for expert review |
| KGCL changes | `mappings/{source}-to-{target}-changes.kgcl` | KGCL | Mapping update changes |
| Bridge ontology | `mappings/{source}-to-{target}-bridge.owl` | OWL/XML | OWL axioms from mappings (optional) |

## Handoff

**Receives from**: `ontology-scout` — target ontology identifiers,
reuse recommendations

**Passes to**: `ontology-validator` — `mappings/*.sssom.tsv`

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
