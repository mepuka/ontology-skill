# Microgrid — `ontology-curator` walkthrough

Walks [`ontology-curator`](../../../ontology-curator/SKILL.md) Steps 0–8
on an **OEO import refresh** scenario — the canonical `import_refresh`
workflow (Step 8). Goal: ingest OEO 1.17.0, detect obsolete-term cascade
to the mapper, re-run downstream gates, and publish consumer release
notes with full provenance.

## Step 0 — change intake (`docs/change-log/2026-04-22-007.md`)

```yaml
change_id: CHG-2026-04-22-007
category: import_refresh              # triggers the full scout → mapper → validator chain
triggered_by: "OEO release notification 2026-04-18: v1.17.0 deprecates oeo:PhotovoltaicPowerUnit in favor of oeo:PVSystem"
downstream_skills: [scout, mapper, validator]
```

## Step 1.5 — impact analysis (`docs/change-impact/CHG-2026-04-22-007.md`)

```yaml
change_id: CHG-2026-04-22-007
affected_cqs: []                       # CQ-M-001 uses mg:SolarArray, not the OEO term directly
affected_mappings:
  - file: mappings/microgrid-to-oeo.sssom.tsv
    rows: [01]                         # mg:SolarArray ↔ oeo:PhotovoltaicPowerUnit (now obsolete)
affected_consumers:
  - "downstream audit dashboards using SPARQL against the mapping set"
risk_summary: |
  Low risk to ontology; mapper must remap one row to the replacement term.
  No CQ regression expected because microgrid classes are stable.
```

## Step 8 — import-refresh sequence

Per SKILL.md Step 8 diagram (scout → manifest → mapper → validator →
notes). Each step yields an artifact; silent skipping is a safety
violation.

### 8.1 Curator opens change log

Change log category `import_refresh` triggers the chain. Commit SHA
`0x7a...` for the staging branch recorded.

### 8.2 Hand off to `ontology-scout`

Scout re-runs Step 0 source availability and Step 6 manifest
regeneration against OEO v1.17.0:

```
$ uv run runoak -i obo: ontologies | grep oeo
  oeo 1.17.0 (released 2026-04-18)
$ .local/bin/robot extract --method STAR \
    --input-iri https://.../ontology/v1.17.0/oeo.owl \
    --term-file ontologies/microgrid/imports/oeo-terms.txt \
    --output ontologies/microgrid/imports/oeo-import.ttl
```

Scout updates `imports-manifest.yaml`:

```yaml
- id: oeo
  source: https://raw.githubusercontent.com/OpenEnergyPlatform/ontology/v1.17.0/oeo.owl
  version_iri: http://openenergy-platform.org/ontology/oeo/1.17.0
  retrieval_date: 2026-04-22
  extraction_method: STAR
  refresh_cadence_days: 90
  known_obsolete:
    - curie: oeo:PhotovoltaicPowerUnit
      replaced_by: oeo:PVSystem
      noticed_on: 2026-04-22
```

### 8.3 Curator regenerates manifest

Already regenerated in 8.2; curator commits the manifest change and
records the commit SHA in the change log.

### 8.4 Hand off to `ontology-mapper`

Mapper re-runs Step 5.1 entity-existence + obsolete check on every
mapping set referencing OEO. Output `mappings/reports/2026-04-22-
microgrid-to-oeo-entity-check.csv`:

```
row_id,subject_resolves,subject_deprecated,object_resolves,object_deprecated,replacement_iri,action
01,true,false,false,true,oeo:PVSystem,remap
02,true,false,true,false,,keep
03,true,false,true,false,,keep
04,true,false,true,false,,keep
```

Mapper emits a KGCL patch on the SSSOM file:

```kgcl
# microgrid-to-oeo-changes.kgcl
delete mapping mg:SolarArray skos:exactMatch oeo:PhotovoltaicPowerUnit
create mapping mg:SolarArray skos:exactMatch oeo:PVSystem \
  confidence 0.94 \
  mapping_justification semapv:MappingReview \
  comment "Remapped on upstream OEO 1.17.0 refresh"
```

Re-run Step 5.5 clique check: still 0 violations. Confidence stays at
0.94 (a review-class justification now tracks the row, per
`sssom-semapv-recipes.md § 5`).

### 8.5 Hand off to `ontology-validator`

Validator runs the full pipeline (see [`validator.md`](validator.md))
with the new OEO module + remapped SSSOM row. Result: all CQs pass; no
new loopbacks raised.

### 8.6 Curator writes consumer release notes

`release/notes/2026-05-01.md`:

```markdown
# Microgrid ontology 2026-05-01

## Summary
Refreshed OEO import to v1.17.0. One mapping row remapped to a
replacement term. No structural change to microgrid classes.

## Breaking changes
- (none)

## Additions
- (none)

## Import refresh
- OEO: v1.16.0 → v1.17.0 (released 2026-04-18)
  - `oeo:PhotovoltaicPowerUnit` deprecated upstream; now `oeo:PVSystem`.
  - Our mapping updated: row 01 of `mappings/microgrid-to-oeo.sssom.tsv`.
  - Source: [CHG-2026-04-22-007](../../docs/change-log/2026-04-22-007.md)

## Migration guidance
Consumers reading the mapping file directly should remap any queries that
match `oeo:PhotovoltaicPowerUnit` to `oeo:PVSystem`. Queries against
microgrid classes (`mg:SolarArray`) are unchanged.
```

## Step 5 — version bump

PATCH-level bump (refresh is an additive/maintenance change with no
structural impact):

```ttl
<http://example.org/microgrid> a owl:Ontology ;
    owl:versionIRI <http://example.org/microgrid/2026-05-01> ;
    owl:versionInfo "2026-05-01" ;
    owl:priorVersion <http://example.org/microgrid/2026-04-22> ;
    prov:wasDerivedFrom <http://openenergy-platform.org/ontology/oeo/1.17.0> .
```

## Step 5.5 + 5.6 — FAIR + publication metadata

```yaml
# release/2026-05-01-publication-check.yaml
- versionIRI_resolves: true
- PURL_to_versioned_IRI: true
- content_negotiation: {ttl: ok, rdfxml: ok, jsonld: ok}
- license_resolves: true
- registry: "n/a (internal)"
- artifact_sha_match: true
- import_refresh_chain_complete: true       # all 6 steps recorded in change log
```

## Pitfall walk — "import pull is not a refresh"

An earlier workflow attempt was: `robot extract` on the new upstream
version, commit, done. This **skips** steps 8.4 (mapper re-gate), 8.5
(validator regression), and 8.6 (release notes). The resulting ship
had a stale SSSOM row pointing at a now-obsolete OEO IRI — consumers'
queries returned zero rows, and the CQ regression suite had never been
re-run. The corrected workflow (above) is mandatory: every import
refresh records a commit SHA at each of the six hand-offs.

## Handoff

Validator full regression → consumer notes shipped via Step 5.6 check.
Upstream refresh tracked under `prov:wasDerivedFrom` so downstream
consumers' CI can pin releases correctly.
