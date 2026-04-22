# Ensemble — `ontology-mapper` walkthrough

Walks [`ontology-mapper`](../../../ontology-mapper/SKILL.md) Steps 0–6
across the four mapper phases (**candidate → curation → evaluation →
repair**). Goal: produce a MIMO ↔ ensemble SSSOM set that passes the
pre-merge gates, handles the `violinist ↔ fiddler ↔ player` clique, and
respects the cross-domain rule on schema.org.

## Step 0 (candidate) — mapping context

```yaml
# SSSOM header comment
mapping_context: same_domain      # MIMO ↔ ensemble (both music)
# The schema.org alignment is a SEPARATE set tagged cross_domain
```

Two output sets:
1. `ontologies/ensemble/mappings/ensemble-to-mimo.sssom.tsv` — same-domain.
2. `ontologies/ensemble/mappings/ensemble-to-schemaorg.sssom.tsv` — cross-domain (triggers the Step 3 cross-domain predicate floor).

## Step 1 (candidate) — lexmatch via oaklib

```bash
uv run runoak -i ontologies/ensemble/ensemble.ttl lexmatch \
  --add ontologies/ensemble/imports/mimo-import.owl \
  --rules-file ontologies/ensemble/mappings/lexmatch-rules.yaml \
  -o ontologies/ensemble/mappings/ensemble-to-mimo.candidate.sssom.tsv
```

Raw output (truncated, header elided):

```tsv
subject_id  subject_label  predicate_id       object_id       object_label       confidence  mapping_justification
ens:Violin  violin         skos:exactMatch    mimo:BVM001     violin             0.99        semapv:LexicalMatching
ens:Cello   cello          skos:exactMatch    mimo:BVM004     cello              0.97        semapv:LexicalMatching
ens:Violinist violinist    skos:exactMatch    mimo:Perf011    fiddler            0.82        semapv:LexicalMatching
ens:Piano   piano          skos:exactMatch    mimo:KB001      pianoforte         0.78        semapv:LexicalMatching
```

## Step 2 (curation) — confidence triage

| Row | Confidence | Tier | Action |
|---|---|---|---|
| `ens:Violin ↔ mimo:BVM001` | 0.99 | auto-accept | Promote with `semapv:LexicalMatching` |
| `ens:Cello ↔ mimo:BVM004` | 0.97 | auto-accept | Promote |
| `ens:Violinist ↔ mimo:Perf011 (fiddler)` | 0.82 | LLM-verify (0.7–0.98) | Class B review |
| `ens:Piano ↔ mimo:KB001 (pianoforte)` | 0.78 | LLM-verify | Class B review |

## Step 3 (curation) — Class B LLM review on MEDIUM rows

Evidence rubric output for `ens:Violinist ↔ mimo:Perf011`:

```
labels match: partial — "violinist" vs "fiddler"
definitions align: partial — ens:Violinist "Musician playing violin classically"
                             mimo:Perf011 "performer on fiddle in folk contexts"
parents compatible: yes — both subclass of Musician role
domain match: same_domain (music)
decision: skos:closeMatch, confidence 0.78, justification: "Role overlap but style distinct"
```

Row updated:

```tsv
ens:Violinist  violinist  skos:closeMatch  mimo:Perf011  fiddler  semapv:LexicalMatching  0.78  reviewer:orcid.org/0000-…  reviewer_date:2026-04-22  comment:"LLM Class B; style distinction"
```

`ens:Piano ↔ mimo:KB001` review promoted to exactMatch (label drift
`piano / pianoforte` is historical aliasing; both term definitions
agree on the instrument).

## Step 4 (curation) — predicate selection

Applying the decision guide:

- Classical equivalents (`Violin`, `Cello`, `Piano`) → `skos:exactMatch`.
- Role vs role variants (`Violinist ↔ Fiddler`) → `skos:closeMatch`.
- schema.org set defaults to `skos:closeMatch` floor (cross-domain).

## Step 5 + 5.1 (evaluation) — validate + entity-existence

```
$ uv run sssom validate ontologies/ensemble/mappings/ensemble-to-mimo.sssom.tsv
  → 0 errors
$ # Entity check report at mappings/reports/2026-04-22-ensemble-to-mimo-entity-check.csv
  row_id,subject_resolves,subject_deprecated,object_resolves,object_deprecated,action
  01,true,false,true,false,keep
  02,true,false,true,false,keep
  03,true,false,true,false,keep
  04,true,false,true,false,keep
```

## Step 5.5 (evaluation) — clique analysis (SIGNATURE pitfall)

Run the clique-check SPARQL from the SKILL.md Step 5.5:

```
$ robot query --input mappings/ensemble-to-mimo.sssom.ttl \
    --query sparql/clique-check.sparql --output clique-report.csv
start,mid,end
ens:Violinist,mimo:Perf011,mimo:Player
mimo:Perf011,mimo:Player,ens:Violinist
```

Transitive closure forms a 3-clique `ens:Violinist ↔ mimo:Perf011(fiddler) ↔ mimo:Player`.
The clique is = 3 (threshold), but one upstream upgrade could push it
past. Reviewer note recorded in the QA report: **had we kept the draft
`skos:exactMatch` on `violinist ↔ fiddler`, the clique would transitively
claim `violinist ≡ player`, contaminating every player subclass**. The
Step 3 closeMatch downgrade prevents the contamination.

## Cross-domain set — `ensemble-to-schemaorg.sssom.tsv`

```tsv
# mapping_context: cross_domain
# comment: All rows default to skos:closeMatch per Step 0; any exactMatch requires Class C review.
subject_id        predicate_id     object_id                     mapping_justification         confidence  reviewer_id
ens:MusicInstrument skos:closeMatch schema:MusicInstrument        semapv:ManualMappingCuration  0.90        reviewer:coordinator@…
ens:Composition   skos:closeMatch schema:MusicComposition        semapv:ManualMappingCuration  0.85        reviewer:coordinator@…
```

Attempting `skos:exactMatch` on `ens:MusicInstrument ↔ schema:MusicInstrument`
would fire `cross_domain_exactMatch` loopback back to mapper per
[`iteration-loopbacks.md § 3`](../../iteration-loopbacks.md). Held to
closeMatch intentionally.

## Step 6 (evaluation) — QA report (`mappings/ensemble-to-mimo-qa.md`)

| Metric | Value |
|---|---|
| predicates | 3 exactMatch, 1 closeMatch |
| confidence histogram | 0.7–0.8: 1; 0.8–0.9: 1; 0.9–1.0: 2 |
| source coverage | 4 / 7 ensemble leaf instruments (57 %) |
| clique max | 3 — at threshold, see § 5.5 note |
| OAEI | skipped (no gold set) |

## Handoff

Both SSSOM files + QA reports → `ontology-validator` Level 0 (entity
check) + Level 5.5 (anti-pattern clique probe). Cross-domain set carries
reviewer signature satisfying Step 3 LLM-verification Class C row in the
SKILL.md LLM Verification table.
