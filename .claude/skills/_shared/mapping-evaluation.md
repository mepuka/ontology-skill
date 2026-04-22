# Mapping Evaluation

**Referenced by:** `ontology-mapper`, `ontology-validator`.
**Related:** [`sssom-semapv-recipes.md`](sssom-semapv-recipes.md) (authoring),
[`llm-verification-patterns.md`](llm-verification-patterns.md) (Class B/C review).

A mapping set is never trusted on generation-time confidence alone. This file
defines the evaluation gates a mapping set must pass before merge and the
quality metrics that apply when a gold/dev set is available. Per
[`CONVENTIONS.md § Safety Rules`](../CONVENTIONS.md#safety-rules-non-negotiable)
rules 13–14, every row carries justification + confidence, and any
`skos:exactMatch` clique > 3 is human-review gated.

## 1. Pre-merge gate checklist

Before merging a mapping set into `ontologies/{name}/mappings/*.sssom.tsv`
(or promoting a candidate file to the main mapping set), run every check
below. Failure routes back to `ontology-mapper` per
[`iteration-loopbacks.md`](iteration-loopbacks.md) with
`failure_type: mapping conflict` or `missing provenance`.

| # | Check | Tool | Failure mode |
|---|---|---|---|
| 1 | SSSOM schema validation | `sssom-py validate file.sssom.tsv` | Missing required columns / invalid header. |
| 2 | Required metadata present | [`sssom-semapv-recipes.md § 2`](sssom-semapv-recipes.md#2-required-yaml-header) | Missing `creator_id`, `license`, `mapping_set_id`, `mapping_tool`, `mapping_date`. |
| 3 | Every row carries `mapping_justification`, `confidence`, reviewer/author, `mapping_date`, `mapping_tool` | SPARQL or pandas filter | LLM-only row without reviewer. |
| 4 | Subject and object CURIEs resolve | `runoak info <CURIE>` per side | Dangling CURIE → obsolete or typo. |
| 5 | Obsolete-term check | `runoak obsoletes -i <source>` | Mapping a deprecated term without a replacement note. |
| 6 | `exactMatch` clique size ≤ 3 | SPARQL (§ 3) | Any clique of size > 3 → human review required. |
| 7 | Cross-domain `exactMatch` → reviewer signature | Review record | Cross-domain identity assertion lacks human approval. |
| 8 | Predicate-conflict check | SPARQL (§ 4) | Same pair mapped with contradictory predicates. |
| 9 | Entity-existence in both ontologies | `sssom-py parse + lookup` | Source or target IRI not declared. |
| 10 | OAEI-style metrics where gold/dev set exists | § 5 | Precision or recall below threshold. |

Checks 1–9 are binary (pass/fail). Check 10 applies only when a reviewed
gold/dev set exists in `ontologies/{name}/mappings/gold/`.

## 2. Confidence tiers

Mapping rows from `sssom-py`, lexmatch, and LLM verification carry a
`confidence` float. Per [`llm-verification-patterns.md § 5`](llm-verification-patterns.md#5-confidence-reconciliation),
reconcile as follows before promotion.

| Tier | Range | Predicate scope | Review gate |
|---|---|---|---|
| HIGH | 0.90 – 1.00 | `skos:exactMatch`, `skos:narrowMatch`, `skos:broadMatch` allowed | Auto-accept if checks 1–9 pass and mapping is intra-domain. |
| MEDIUM | 0.70 – 0.89 | `skos:closeMatch`, `skos:relatedMatch` preferred; `exactMatch` requires reviewer | Curator sign-off (Class C) before merge. |
| LOW | < 0.70 | `skos:relatedMatch` only, or quarantine | Do not auto-merge. Write to `mappings/candidates/` for triage. |

Never round a LOW confidence up to justify a stronger predicate — refactor
to a weaker predicate instead, or drop the row.

## 3. Clique check (exactMatch transitivity)

`skos:exactMatch` is reflexive-symmetric-transitive in practice (and is
minted as OWL `owl:sameAs` by `sssom-py to-owl --preset exact-owl`).
A merged mapping set whose `exactMatch` relation forms a clique of size
≥ 4 either (a) witnesses true multi-ontology equivalence (rare) or (b)
has been contaminated by a single wrong edge. Detect cliques with:

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

# Count exactMatch-reachable members per starting term.
SELECT ?term (COUNT(DISTINCT ?reachable) AS ?clique_size) WHERE {
  ?term (skos:exactMatch|^skos:exactMatch)* ?reachable .
}
GROUP BY ?term
HAVING (?clique_size > 3)
ORDER BY DESC(?clique_size)
```

Run against the reasoned closure of the mapping set merged with both
source and target ontologies. Any row with `clique_size > 3` must be
escalated to human review per
[`CONVENTIONS.md § Safety Rule 14`](../CONVENTIONS.md#safety-rules-non-negotiable).

**Cross-domain rule.** Even a clique of size 2 must be human-reviewed if
the two terms sit under different BFO categories (e.g., continuant vs.
occurrent, object vs. role). The review artifact lives at
`docs/mapping-reviews/{date}-{short-id}.md` and names the reviewer,
evidence, and decision.

## 4. Predicate-conflict check

A row-pair `(subject, object)` cannot carry contradictory predicates
(e.g., `exactMatch` in one file, `narrowMatch` in another) in the merged
mapping set:

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?s ?o ?p1 ?p2 WHERE {
  ?s ?p1 ?o . ?s ?p2 ?o .
  FILTER (?p1 != ?p2)
  FILTER (?p1 IN (skos:exactMatch, skos:closeMatch, skos:broadMatch,
                   skos:narrowMatch, skos:relatedMatch))
  FILTER (?p2 IN (skos:exactMatch, skos:closeMatch, skos:broadMatch,
                   skos:narrowMatch, skos:relatedMatch))
}
```

A non-empty result is a merge-blocker. The owning skill
(`ontology-mapper`) must reconcile before re-running the gate.

## 5. OAEI-style metrics (gold set present)

If `ontologies/{name}/mappings/gold/*.sssom.tsv` exists — curated by a
domain expert, treated as the reference — compute:

```
precision = |M ∩ G|  /  |M|
recall    = |M ∩ G|  /  |G|
F1        = 2 · P · R / (P + R)
```

where `M` is the produced mapping set and `G` is the gold set. Intersection
is defined over `(subject_id, predicate_id, object_id)` triples (i.e., a
row is in the intersection iff both files agree on all three).

```bash
uv run python scripts/sssom_metrics.py \
  --produced ontologies/{name}/mappings/music-to-wikidata.sssom.tsv \
  --gold     ontologies/{name}/mappings/gold/music-to-wikidata.sssom.tsv
# Emits precision, recall, F1 to stdout and a breakdown per predicate.
```

Thresholds (default; tune per project in `docs/scope.md § Mapping QA`):

| Metric | Floor | Action below floor |
|---|---|---|
| Precision | 0.85 | Route back to mapper with false-positive list. |
| Recall | 0.70 | Route back to mapper; likely missing lexmatch candidates. |
| F1 | 0.80 | Combined trigger; re-evaluate predicate tier policy. |

If no gold set exists, note `no_gold_set: true` in the QA report. Metric
thresholds are not required — but clique and predicate-conflict checks are
still mandatory.

## 6. QA report format

The mapper emits one QA report per mapping set to
`ontologies/{name}/mappings/reports/{date}-{set-id}.md` with these
sections:

1. **Header:** source ontology, target ontology, versions, mapping tool,
   mapping date, gold-set path if present.
2. **Gate results:** one line per check from § 1, each with pass/fail.
3. **Confidence distribution:** histogram HIGH/MEDIUM/LOW per predicate.
4. **Clique report:** any clique size > 1; flag cliques > 3.
5. **Obsolete-term report:** any row referencing an obsolete term + replacement status.
6. **OAEI metrics** (if gold set present).
7. **Review decisions:** table of rows requiring Class C review + reviewer + outcome.
8. **Open issues / loopbacks raised:** entries that blocked merge, each linking to `docs/loopbacks/`.

This file is the artifact the validator inspects; it is not regenerated
on merge, only on mapping-set refresh.

## 7. Anti-patterns

| Anti-pattern | Symptom | Detection |
|---|---|---|
| **Metric-free QA** | Mapping set merged with only gate 1–3 run. | Missing `precision` / `recall` in report when gold set exists. |
| **Confidence round-up** | `0.68` relabelled as `0.75` to clear the tier. | Review diff against raw lexmatch / LLM output. |
| **Unscoped exactMatch** | `exactMatch` across BFO categories with no reviewer signature. | Cross-domain rule in § 3. |
| **Clique ignored** | Clique > 3 present but no review artifact. | Gate 6 in § 1. |
| **One-off reviewer** | Same person as author and reviewer. | `creator_id == reviewer_id` across the set. |
| **Stale mapping** | Source or target version advanced without refresh. | Compare `mapping_set_version` to current source/target versions. |

## 8. Worked examples

See (Wave 4):

- [`worked-examples/ensemble/mapper.md`](worked-examples/ensemble/mapper.md) — promoting a 0.86 lexmatch candidate after LLM review; clique check on violinist↔fiddler↔player.
- [`worked-examples/microgrid/mapper.md`](worked-examples/microgrid/mapper.md) — cross-domain `exactMatch` between a domain device class and a schema.org `Product` caught by the cross-domain rule.

## 9. References

- [SSSOM specification](https://mapping-commons.github.io/sssom/) — standardized TSV mappings, metadata, and OWL translation.
- [SEMAPV (Semantic Mapping Vocabulary)](https://mapping-commons.github.io/semantic-mapping-vocabulary/) — justification CURIEs.
- [OAEI (Ontology Alignment Evaluation Initiative)](https://oaei.ontologymatching.org/) — precision/recall/F1 conventions for alignment evaluation.
- [`CONVENTIONS.md § Safety Rules`](../CONVENTIONS.md#safety-rules-non-negotiable) — rules 13–14 (SSSOM provenance, clique > 3 review).
