# Microgrid — `ontology-mapper` walkthrough

Walks [`ontology-mapper`](../../../ontology-mapper/SKILL.md) Steps 0–6
across the four phases (**candidate → curation → evaluation → repair**).
Signature content: the **cross-domain rule** blocks an `exactMatch` from
`mg:Battery` to `schema.org/Product`, demonstrating how the same-domain
vs cross-domain classification of a mapping set determines the predicate
floor and the reviewer gate.

## Step 0 (candidate) — mapping context

Two mapping sets from the microgrid ontology — different contexts:

```yaml
# Set A — SAME DOMAIN
mapping_context: same_domain      # microgrid ↔ OEO (both energy-domain)
# Set B — CROSS DOMAIN
mapping_context: cross_domain     # microgrid ↔ schema.org
```

## Step 1 (candidate) — lexmatch for same-domain (microgrid ↔ OEO)

```bash
uv run runoak -i ontologies/microgrid/microgrid.ttl lexmatch \
  --add ontologies/microgrid/imports/oeo-import.ttl \
  -o ontologies/microgrid/mappings/microgrid-to-oeo.candidate.sssom.tsv
```

Excerpt:

```tsv
subject_id           subject_label   predicate_id     object_id                           object_label                         confidence  mapping_justification
mg:SolarArray        solar array     skos:exactMatch  oeo:PhotovoltaicPowerUnit          photovoltaic power unit             0.94        semapv:LexicalMatching
mg:Battery           battery         skos:exactMatch  oeo:BatteryEnergyStorageSystem     battery energy storage system       0.88        semapv:LexicalMatching
mg:IslandingEvent    islanding       skos:exactMatch  oeo:Islanding                      islanding                           0.99        semapv:LexicalMatching
mg:Inverter          inverter        skos:exactMatch  oeo:Inverter                       inverter                            0.99        semapv:LexicalMatching
```

## Step 2 (curation) — confidence triage (same-domain set)

| Row | Confidence | Tier | Action |
|---|---|---|---|
| `mg:Inverter ↔ oeo:Inverter` | 0.99 | auto-accept | Promote exactMatch |
| `mg:IslandingEvent ↔ oeo:Islanding` | 0.99 | auto-accept | Promote exactMatch |
| `mg:SolarArray ↔ oeo:PhotovoltaicPowerUnit` | 0.94 | auto-accept | Labels/parents compatible; promote exactMatch |
| `mg:Battery ↔ oeo:BatteryEnergyStorageSystem` | 0.88 | LLM-verify | Class B review |

## Step 3 (curation) — Class B LLM review (one MEDIUM row)

Row: `mg:Battery ↔ oeo:BatteryEnergyStorageSystem`.

```
labels match: partial — "battery" vs "battery energy storage system"
definitions align: yes — both "storage asset holding chemical energy for dispatch"
parents compatible: yes — both bfo:Object
domain match: same_domain
decision: skos:exactMatch, confidence 0.92, justification: "definition + parent alignment compensates for label truncation"
```

Row updated — predicate stays `exactMatch`, confidence raised to 0.92,
`reviewer_id` + `reviewer_date` recorded.

## Cross-domain set — the SIGNATURE pitfall

Draft rows for `microgrid-to-schemaorg`:

```tsv
# mapping_context: cross_domain
subject_id           predicate_id     object_id                 confidence  mapping_justification
mg:Battery           skos:exactMatch  schema:Product            0.82        semapv:LexicalMatching   # DRAFT
mg:EnergyAsset       skos:exactMatch  schema:Product            0.75        semapv:LexicalMatching   # DRAFT
mg:Microgrid         skos:closeMatch  schema:Place              0.70        semapv:ManualMappingCuration
```

### What the cross-domain rule does (Step 0 + Step 3)

Step 0 classifies this set as `cross_domain`; the predicate floor is
`skos:closeMatch`. Any `exactMatch` in this set **requires Class C
reviewer signature** per the LLM-verification table in the SKILL.md.
Without a signed reviewer row, the Step 3 curation gate raises:

```
cross_domain_exactMatch: row 01 (mg:Battery ↔ schema:Product)
cross_domain_exactMatch: row 02 (mg:EnergyAsset ↔ schema:Product)
```

Route per `iteration-loopbacks.md § 3`: `mapper` owns the fix. Two
options:
1. **Downgrade both** to `skos:closeMatch`. Acceptable — `schema.org/Product`
   is far broader (physical and digital goods, services); it is not a
   truthful equivalent for a physical energy asset.
2. **Request Class C review** from a domain architect who can sign off
   the cross-domain exactMatch. For this project, option 1 is chosen —
   no reviewer is willing to assert `Battery ≡ Product`.

Post-fix rows:

```tsv
mg:Battery       skos:closeMatch  schema:Product    0.82  semapv:ManualMappingCuration  reviewer_id:ops-lead@…  comment:"Cross-domain rule; refused exactMatch"
mg:EnergyAsset   skos:closeMatch  schema:Product    0.75  semapv:ManualMappingCuration  reviewer_id:ops-lead@…
mg:Microgrid     skos:closeMatch  schema:Place      0.70  semapv:ManualMappingCuration  reviewer_id:ops-lead@…
```

## Step 5 + 5.1 (evaluation)

```
$ uv run sssom validate ontologies/microgrid/mappings/microgrid-to-oeo.sssom.tsv
  → 0 errors
$ # Entity check
  row_id,subject_resolves,subject_deprecated,object_resolves,object_deprecated,action
  01,true,false,true,false,keep
  02,true,false,true,false,keep
  03,true,false,true,false,keep
  04,true,false,true,false,keep
```

## Step 5.5 (evaluation) — clique analysis

```
$ robot query --input mappings/microgrid-to-oeo.sssom.ttl \
    --query sparql/clique-check.sparql --output clique-report.csv
(empty — no clique > 1 on exactMatch in same-domain set)
```

Cross-domain set is all `skos:closeMatch`, so no transitive
contamination.

## Step 5.6 (evaluation) — OAEI (no gold set)

```
oaei: skipped (no gold set available for microgrid-to-oeo)
```

Absence explicitly recorded — silent omission would fail progress
criteria.

## Step 6 (evaluation) — QA report

```
predicate distribution: 4 exactMatch (same-domain), 3 closeMatch (cross-domain)
source coverage: 4/18 microgrid equipment classes → 22 % OEO
clique max: 1 (no transitive issues)
cross_domain_exactMatch_flags: 0 (all downgraded per Step 3)
```

## Handoff

Both SSSOM sets + QA reports → `ontology-validator` (Level 0 + Level
5.5 clique probe). Cross-domain-rule enforcement keeps the
`cross_domain_exactMatch` loopback closed; had it not, the validator
would raise it per the Level 8 routing table. Curator refresh
(see [`curator.md`](curator.md)) re-runs these gates on every OEO
upstream release.
