---
name: ontology-mapper
description: >
  Generates, verifies, evaluates, and maintains cross-ontology mapping
  and alignment using SSSOM, lexical matching via oaklib (lexmatch), and
  LLM-assisted verification and semantic review. Produces mapping sets
  with SEMAPV justification, confidence, and reviewer provenance; runs
  exactMatch clique checks and (where a gold/dev set exists) OAEI-style
  precision/recall. Use for SSSOM mapping sets, cross-references, xrefs,
  bridge ontologies, validating mappings, remapping obsolete terms, or
  reviewing exactMatch / sameAs safety.
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
- `_shared/llm-verification-patterns.md` — Class-B prompt template for verifying lexmatch candidate pairs; Class-C triggers for cross-domain exactMatch and clique > 3
- `_shared/iteration-loopbacks.md` — raises `mapping_confidence`, `missing_semapv`, `mapping_clique`, `mapping_conflict`, `cross_domain_exactMatch` loopbacks back to this skill
- `_shared/mapping-evaluation.md` — pre-merge gate checklist, confidence tiers, clique SPARQL, cross-domain exactMatch rule, OAEI precision/recall, QA report format
- `_shared/sssom-semapv-recipes.md` — required YAML header, SEMAPV catalog, lexmatch / LLM-verified / manual recipes, OWL translation presets

## Core Workflow

The mapper workflow runs in four phases. Each step below carries a phase
label so downstream skills know which gate a row has passed.

| Phase | Steps | Goal |
|-------|-------|------|
| **candidate** | 0 → 1 | Identify mapping context; generate raw candidate rows |
| **curation** | 2 → 4 | Triage, LLM-verify, and pick predicates |
| **evaluation** | 5 → 5.6 | Validate, check entities, cliques, and OAEI metrics |
| **repair** | 7 → 8 | Maintain across source/target version changes; gate bridge publication |

### Step 0: Mapping Context Classification (candidate)

Classify the mapping set before drafting rows. Context determines allowed
predicates, review class, and downstream consistency gates:

| Context | Examples | Default predicate floor | Notable gate |
|---------|----------|-------------------------|--------------|
| `same_domain` | Two music-domain ontologies | `skos:exactMatch` permitted with evidence | Clique check |
| `cross_domain` | Device class ↔ schema.org Product | Default `skos:closeMatch`; `exactMatch` requires Class C review | Cross-domain exactMatch rule |
| `bridge` | Source ⟷ target via a third bridge ontology | Bridge authoring mode | Step 8 safety gate |
| `identity` | True individual identity (rare) | `owl:sameAs` | Identity-risk review (Class C) |
| `lexical_synonym` | Label-synonym extraction, not equivalence | `skos:relatedMatch` or `skosxl:altLabel` | Document that it's not an axiom |
| `replacement` | Obsolete term ⟶ replacement | `obo:IAO_0100001` plus a SKOS mapping | Obsolete-term check (Step 5.1) |

Record the chosen context in the SSSOM YAML header (`comment:` field with
`mapping_context: {value}` plus a one-line rationale).

### Step 1: Candidate Generation (Lexical Matching) (candidate)

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

### Step 2: Confidence Triage (curation)

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

### Step 3: LLM Verification with Evidence Rubric (curation)

For each uncertain pair, evaluate with the Class-B rubric from
[`_shared/llm-verification-patterns.md § 3`](_shared/llm-verification-patterns.md):

```
Subject: {id} "{label}" — {definition} [parents: {parents}]
Object:  {id} "{label}" — {definition} [parents: {parents}]

Evidence required in the response:
- labels match: yes / partial / no (quote both labels)
- definitions align: yes / partial / no (quote relevant phrases)
- parents compatible: yes / partial / no (cite each parent IRI)
- domain match: same_domain | adjacent_domain | cross_domain

Decision:
- predicate: exactMatch / closeMatch / broadMatch / narrowMatch /
             relatedMatch / no_match
- confidence: 0.0 – 1.0
- justification: one sentence tying decision to evidence
```

Rules:

- `exactMatch` requires confidence ≥ 0.90 AND all three evidence rows = `yes`.
- Cross-domain context (from Step 0) forces `closeMatch` or lower unless
  the row is escalated to Class C review per Loopback Triggers.
- Update the SSSOM row with LLM-verified predicate + confidence +
  `mapping_justification: semapv:SemanticSimilarityThresholdMatching` and
  add a reviewer_id when Class C review applies.

### Step 4: Mapping Predicate Selection (curation)

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

### Step 5: Validate (evaluation)

```bash
# Validate SSSOM schema conformance
uv run sssom validate ontologies/{name}/mappings/{source}-to-{target}.sssom.tsv
```

Check:
- Schema conformance (valid SSSOM TSV).
- CURIE resolution (all prefixes in curie_map).
- Predicate consistency (no contradictory predicates for same pair).
- No self-mappings (subject ≠ object).
- No duplicate mappings.
- Full SSSOM metadata per
  [`_shared/sssom-semapv-recipes.md § 2`](_shared/sssom-semapv-recipes.md)
  (header completeness is a validator prerequisite).

### Step 5.1: Entity Existence + Obsolete-Term Check (evaluation)

Every `subject_id` and `object_id` MUST resolve in its source ontology,
and the check MUST record whether the target term is current or obsolete:

```bash
# Per-row existence and obsolete probe (via oaklib)
uv run runoak -i sqlite:obo:{source} info {subject_id}
uv run runoak -i sqlite:obo:{target} info {object_id}
```

Produce `mappings/reports/{date}-{set-id}-entity-check.csv` with columns:
`row_id, subject_resolves, subject_deprecated, object_resolves,
object_deprecated, replacement_iri, action`.

Actions:

| Condition | Action |
|-----------|--------|
| Both resolve, neither deprecated | `keep` |
| Target obsolete WITH `obo:IAO_0100001` replacement | `remap` — update row to replacement IRI and add `comment` noting refresh |
| Target obsolete WITHOUT replacement | `loopback_curator` (stale_import) |
| Subject or object does not resolve | `loopback_scout` (bad_module) or fix CURIE |

No mapping set passes evaluation with unresolved CURIEs or silent
obsolete-target rows.

### Step 5.5: Clique Analysis (evaluation, mandatory for exactMatch)

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

### Step 5.6: OAEI-Style Evaluation (evaluation, when gold / dev set exists)

When a gold set or held-out dev set is available, compute OAEI-style
precision / recall / F1 per
[`_shared/mapping-evaluation.md § 5`](_shared/mapping-evaluation.md):

```bash
uv run python scripts/mapping_oaei_metrics.py \
  --predicted mappings/{set}.sssom.tsv \
  --gold mappings/gold/{set}.sssom.tsv \
  --out mappings/reports/{date}-{set-id}-metrics.json
```

Record in the QA report:

- Precision ≥ 0.85, Recall ≥ 0.70, F1 ≥ 0.80 are the Progress-Criteria
  thresholds for maintained mapping sets.
- Below threshold: treat as a mapping-confidence loopback to mapper, not
  a validator report.
- Without a gold set, record `oaei: skipped (no gold set)` in the QA
  report — absence of a gold set is not a failure, but silent absence is.

### Step 6: Quality Report (evaluation)

Generate a quality assessment:

- Predicate distribution (how many of each type)
- Confidence distribution (histogram)
- Source coverage (% of source terms mapped)
- Target coverage (% of target terms mapped)
- Potential conflicts (same subject mapped to multiple objects with
  exactMatch)
- Clique analysis (transitive closure of exactMatch — flag cliques > 3)

### Step 7: Mapping Maintenance (repair)

When the source or target ontology releases a new version, re-run Steps 5 →
5.6 against the updated artifacts. The curator raises this loopback via
`stale_import`; the mapper owns the response.

Maintenance checklist:

1. Pull the new pinned version from the scout's `imports-manifest.yaml`.
2. Re-run Step 5.1 entity / obsolete check — every row gets a fresh action.
3. Remap obsolete targets to their `obo:IAO_0100001` replacement where
   present; drop rows where the obsolete term has no replacement and open a
   follow-up.
4. Re-run Step 5.5 clique analysis; new upstream exactMatch edges may have
   extended a clique past the threshold.
5. Re-run Step 5.6 OAEI metrics if a gold set exists.
6. Bump `mapping_set_version` in the SSSOM header; add a `prov:wasRevisionOf`
   pointer to the prior version.

### Step 8: Bridge Ontology Safety Gate (repair, bridge context only)

When Step 0 classified the mapping context as `bridge`, a bridge OWL
ontology was converted from the SSSOM rows (see "Tool Commands" below).
Before the bridge ships, it must pass both a consistency check and a
conservativity check:

```bash
# 1. Consistency: reasoner on merged source + target + bridge
robot merge --input source.owl --input target.owl --input bridge.owl \
  --output merged-with-bridge.owl
robot reason --reasoner HermiT --input merged-with-bridge.owl \
  --dump-unsatisfiable unsat-with-bridge.txt

# 2. Conservativity: reasoner on source + target WITHOUT the bridge, diff
robot merge --input source.owl --input target.owl --output merged-no-bridge.owl
robot reason --reasoner HermiT --input merged-no-bridge.owl \
  --dump-unsatisfiable unsat-no-bridge.txt

# Both unsat lists should be identical.  Any class unsatisfiable only in the
# with-bridge merge means the bridge introduced a contradiction.
```

Conservativity sanity: any *new* class subsumption between source terms
that is introduced only when the bridge is loaded must be intended — not an
accident. Record each such entailment in the QA report; unannotated
accidental entailments block publication.

If either check fails, do NOT publish. Raise an `unsatisfiable_class`
loopback; the mapper rewrites / downgrades the offending rows (typically
downgrading `owl:equivalentClass` or `exactMatch` to `closeMatch`).

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

## Progress Criteria

Work is done when every box is checked. Each item is tool-verifiable.

- [ ] `sssom-py validate` passes; required YAML header present per
      [`_shared/sssom-semapv-recipes.md § 2`](_shared/sssom-semapv-recipes.md).
- [ ] Every row carries `mapping_justification`, `confidence`, reviewer/author,
      `mapping_date`, `mapping_tool` per safety rule 13.
- [ ] Entity-existence check passes: every CURIE resolves via `runoak info`.
- [ ] Obsolete-term report generated; any row pointing to a deprecated term
      carries a replacement note.
- [ ] Clique report generated; no clique > 3 promoted without human review per
      [`_shared/mapping-evaluation.md § 3`](_shared/mapping-evaluation.md).
- [ ] Cross-domain `exactMatch` rows carry a reviewer signature.
- [ ] If a gold/dev set exists: precision ≥ 0.85, recall ≥ 0.70, F1 ≥ 0.80.
- [ ] QA report at `mappings/reports/{date}-{set-id}.md` per § 6.
- [ ] No Loopback Trigger below fires.

## LLM Verification Required

See [`_shared/llm-verification-patterns.md`](_shared/llm-verification-patterns.md).
Never replaces `sssom validate`, entity-existence, or clique checks.

| Operation | Class | Tool gate |
|---|---|---|
| Mapping predicate selection | B | Class B prompt + evidence (labels, defs, parents); `confidence ≥ 0.90` for `exactMatch` |
| Cross-domain `exactMatch` | C | Named reviewer, ISO date, rationale in `mapping-reviews/` |
| Bridge-ontology conversion | A | `robot reason` on merged source + target + bridge; no new unsatisfiables |
| Confidence override | B | Written rationale + diff against raw tool output |

## Loopback Triggers

| Trigger | Route to | Reason |
|---|---|---|
| Incoming: `mapping_confidence` | `ontology-mapper` | Mapper owns confidence tier policy. |
| Incoming: `missing_semapv` | `ontology-mapper` | SEMAPV gap is a mapper artifact bug. |
| Incoming: `mapping_clique` (> 3) | `ontology-mapper` | Clique resolution is a mapper decision. |
| Incoming: `mapping_conflict` | `ontology-mapper` | Predicate conflict reconciled here. |
| Incoming: `cross_domain_exactMatch` | `ontology-mapper` | Cross-domain rule owned here; Class C review. |
| Raised: source or target term is obsolete in upstream | `ontology-curator` | Import refresh is curator's job; wait for refresh, then remap. |

Depth > 3 escalates per [`_shared/iteration-loopbacks.md`](_shared/iteration-loopbacks.md).

## Worked Examples

- [`_shared/worked-examples/ensemble/mapper.md`](_shared/worked-examples/ensemble/mapper.md) — MIMO↔music-ontology lexmatch + Class B review on one MEDIUM row; clique check on violinist↔fiddler↔player. *(Wave 4)*
- [`_shared/worked-examples/microgrid/mapper.md`](_shared/worked-examples/microgrid/mapper.md) — cross-domain `exactMatch` between device class and `schema.org` Product caught by the cross-domain rule. *(Wave 4)*
