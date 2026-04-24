# SSSOM + SEMAPV Recipes

**Referenced by:** `ontology-mapper`.
**Related:** [`mapping-evaluation.md`](mapping-evaluation.md) (merge gates),
[`llm-verification-patterns.md`](llm-verification-patterns.md) (Class B prompt template).

This file is the authoring-side companion to
[`mapping-evaluation.md`](mapping-evaluation.md): it shows how to *produce*
a valid SSSOM mapping set with the right SEMAPV `mapping_justification`.
Evaluation happens on the downstream side; this file covers the writer's
obligations.

## 1. What a valid SSSOM file looks like

An SSSOM file is a TSV with a YAML header delimited by `#` at the top.
Each data row is one mapping.

```tsv
# curie_map:
#   skos: http://www.w3.org/2004/02/skos/core#
#   semapv: https://w3id.org/semapv/vocabulary/
#   MUSIC: https://example.org/music/
#   WIKIDATA: http://www.wikidata.org/entity/
# mapping_set_id: https://example.org/mappings/music-to-wikidata
# mapping_set_version: 2026-04-21
# license: https://creativecommons.org/publicdomain/zero/1.0/
# mapping_tool: oaklib.lexmatch
# creator_id: https://orcid.org/0000-0000-0000-0000
# mapping_date: 2026-04-21
subject_id	subject_label	predicate_id	object_id	object_label	mapping_justification	confidence	creator_id	mapping_date	mapping_tool
MUSIC:Violin	violin	skos:exactMatch	WIKIDATA:Q8355	violin	semapv:LexicalMatching	0.95	https://orcid.org/0000-0000-0000-0000	2026-04-21	oaklib.lexmatch
MUSIC:Cello	cello	skos:exactMatch	WIKIDATA:Q76239	cello	semapv:ManualMappingCuration	1.0	https://orcid.org/0000-0000-0000-0000	2026-04-21	manual
```

Validate before commit:

```bash
uv run sssom validate ontologies/{name}/mappings/music-to-wikidata.sssom.tsv
# Exit 0 on success; lists missing columns and CURIE errors on failure.
```

## 2. Required YAML header

These fields are mandatory per [`CONVENTIONS.md § Safety Rule 13`](../CONVENTIONS.md#safety-rules-non-negotiable)
and cannot be defaulted from tool output:

| Field | Example | Why required |
|---|---|---|
| `curie_map:` | `skos: http://www.w3.org/2004/02/skos/core#` | Every prefix used in any row must be declared. |
| `mapping_set_id:` | `https://example.org/mappings/music-to-wikidata` | Stable IRI for the set as a whole. |
| `mapping_set_version:` | `2026-04-21` | ISO date or semver; must advance on refresh. |
| `license:` | `https://creativecommons.org/publicdomain/zero/1.0/` | Required for downstream reuse. |
| `mapping_tool:` | `oaklib.lexmatch` or `manual` | Default tool, per-row overrides permitted. |
| `creator_id:` | `https://orcid.org/0000-…` | Default creator, per-row overrides permitted. |
| `mapping_date:` | `2026-04-21` | Default date, per-row overrides permitted. |

Every **row** must have: `subject_id`, `predicate_id`, `object_id`,
`mapping_justification`, `confidence`, plus either header-level or
row-level `creator_id`, `mapping_date`, and `mapping_tool`. If the row
was LLM-reviewed or human-reviewed, add `reviewer_id` and
`reviewer_date`.

## 3. SEMAPV justification catalog

SEMAPV (Semantic Mapping Vocabulary) enumerates the process that produced
a row. Use the CURIE below as the `mapping_justification` value.

| SEMAPV CURIE | When to use |
|---|---|
| `semapv:LexicalMatching` | Produced by lexmatch / string similarity over labels. Confidence ≤ 1.0 from the matcher. |
| `semapv:ManualMappingCuration` | Human curator proposed and confirmed. Confidence = 1.0 unless curator downgrades. |
| `semapv:LogicalReasoning` | Inferred by reasoner (e.g., a subsumption entailment over imported bridge axioms). |
| `semapv:CompositeMatching` | Combination of two or more methods (e.g., lexmatch + embedding). Declare the stack in `mapping_tool`. |
| `semapv:SemanticSimilarityThresholdMatching` | Embedding / vector similarity above a declared threshold. Note the threshold in `comment`. |
| `semapv:MappingReview` | A review decision on a prior row (not the initial authoring method). Pair with the original justification via `see_also`. |
| `semapv:UnspecifiedMatching` | Last resort. Only if the provenance was lost. Review before promotion. |

LLM-verified candidates take the justification of their **origin** method
(e.g., `semapv:LexicalMatching` for a reviewed lexmatch row) *plus* a
`reviewer_id` and `reviewer_date` capturing the LLM or human review step.
The review alone is not the justification.

## 4. Recipe A — lexmatch to SSSOM

For same-domain mapping where both source and target are local TTL files
(or a graph runoak can load).

```bash
# 1. Run lexmatch against both ontologies, normalized labels only.
uv run runoak -i ontologies/music/music.ttl \
  lexmatch -R ontologies/music/mappings/lexmatch-rules.yaml \
  -o ontologies/music/mappings/music-to-wikidata.candidate.sssom.tsv \
  @ sqlite:obo:wikidata

# 2. Prepend the YAML header (curie_map, mapping_set_id, etc.).
#    Use scripts/prepend_sssom_header.py if available, or edit by hand.

# 3. Validate the candidate.
uv run sssom validate ontologies/music/mappings/music-to-wikidata.candidate.sssom.tsv

# 4. Apply confidence-tier policy (see mapping-evaluation.md § 2).
#    HIGH → auto-accept; MEDIUM → Class B LLM review; LOW → quarantine.

# 5. Run the pre-merge gate (mapping-evaluation.md § 1).
#    On pass, rename candidate → final:
mv ontologies/music/mappings/music-to-wikidata.candidate.sssom.tsv \
   ontologies/music/mappings/music-to-wikidata.sssom.tsv
```

Notes:

- `lexmatch` emits `semapv:LexicalMatching` by default. Do not overwrite it.
- Rows under the MEDIUM threshold go to
  `mappings/candidates/*.sssom.tsv` for LLM review; do not merge them to the
  main file until the reviewer gate clears (see recipe B).

## 5. Recipe B — LLM-verified candidate

For cross-domain mapping or where lexmatch confidence sits in MEDIUM.

```python
# Pseudocode — not a runnable script; illustrates the round-trip.
import pandas as pd
from ontology_skill.sssom import load_sssom, save_sssom
from ontology_skill.llm_review import class_b_review   # § 3 of llm-verification-patterns.md

candidates = load_sssom("mappings/candidates/music-to-wikidata.sssom.tsv")

for _, row in candidates.iterrows():
    evidence = gather_evidence(row.subject_id, row.object_id)
    decision = class_b_review(row, evidence)
    row["confidence"] = decision.confidence_numeric
    row["mapping_justification"] = row["mapping_justification"]  # preserve origin
    row["reviewer_id"] = decision.reviewer_id
    row["reviewer_date"] = decision.iso_date
    row["comment"] = decision.rationale
    if decision.outcome == "accept":
        promote(row, "mappings/music-to-wikidata.sssom.tsv")
    elif decision.outcome == "human-review":
        write(row, "mappings/review-queue.sssom.tsv")
    else:
        write(row, "mappings/rejected.sssom.tsv")
```

The Class B prompt template lives in
[`llm-verification-patterns.md § 3`](llm-verification-patterns.md#3-standard-prompt-template-for-class-b).
The reviewer output is a strict JSON object (decision / confidence /
justification / rationale); the recipe above maps each field into the
SSSOM row.

**Abstention rule.** If the LLM output is not strict JSON or omits any
field, mark the row `human-review` rather than guessing. Silent
promotion with partial evidence is a safety-rule violation.

## 6. Recipe C — manual curation

Manual curation rows carry `semapv:ManualMappingCuration` and
`confidence: 1.0` *only* if the curator genuinely asserts certainty.
For "probable but unconfirmed", use `0.85` and pair with
`comment: "<curator note>"`.

```tsv
subject_id	predicate_id	object_id	mapping_justification	confidence	creator_id	mapping_date	mapping_tool	comment
MUSIC:Cello	skos:exactMatch	WIKIDATA:Q76239	semapv:ManualMappingCuration	1.0	https://orcid.org/…	2026-04-21	manual	curator confirmed against MIMO label
```

## 7. Translation to OWL

For downstream reasoning (bridge ontologies, consistency checks), convert
the validated SSSOM to OWL:

```bash
uv run sssom parse --output-format owl \
  --preset exact-owl \
  ontologies/music/mappings/music-to-wikidata.sssom.tsv \
  --output ontologies/music/mappings/music-to-wikidata.owl.ttl
```

`--preset exact-owl` maps `skos:exactMatch` to `owl:equivalentClass`. This
is a strong semantic commitment; see [`mapping-evaluation.md § 3`](mapping-evaluation.md#3-clique-check-exactmatch-transitivity)
on the clique risk. For weaker predicates, use `--preset dbpedia-rewrite`
or leave as SKOS; do not blanket-promote to `owl:equivalentClass`.

Once converted, run the reasoner against the merged source + target +
bridge graph before publishing. A failed reason is a bridge-level
loopback to `ontology-mapper`, not a local fix.

## 8. Anti-patterns

| Anti-pattern | Fix |
|---|---|
| Missing YAML header on a file that validates against SSSOM schema | Most validators accept header-less files; the **convention** (not the schema) requires the header. Add it. |
| `mapping_justification` = `semapv:UnspecifiedMatching` on new rows | Either pick the real method or reject the row. |
| Reviewer filled in before actual review happened | Enforce reviewer_date ≥ mapping_date and require an independent signature. |
| `skos:exactMatch` with confidence < 0.90 | Downgrade the predicate (`closeMatch`) or escalate to review. |
| Per-row `mapping_tool` contradicts header `mapping_tool` and no comment | Either align or set header to `mapping_tool: mixed` and note in `comment`. |

## 9. Worked examples

See (Wave 4):

- [`worked-examples/ensemble/mapper.md`](worked-examples/ensemble/mapper.md) — producing a MIMO↔local-music-ontology mapping set via Recipe A + Class B LLM review on one MEDIUM row.
- [`worked-examples/microgrid/mapper.md`](worked-examples/microgrid/mapper.md) — cross-domain candidate between a domain device and schema.org `Product`; recipe C manual curation plus cross-domain reviewer signature.

## 10. References

- [SSSOM specification](https://mapping-commons.github.io/sssom/) — schema, required fields, SKOS/OWL translation.
- [SEMAPV vocabulary](https://mapping-commons.github.io/semantic-mapping-vocabulary/) — justification CURIEs.
- [oaklib `lexmatch`](https://incatools.github.io/ontology-access-kit/) — lexical matching CLI.
- [`CONVENTIONS.md § Safety Rule 13`](../CONVENTIONS.md#safety-rules-non-negotiable) — mapping provenance requirements.
