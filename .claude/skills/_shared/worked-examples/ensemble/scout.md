# Ensemble — `ontology-scout` walkthrough

Walks [`ontology-scout`](../../../ontology-scout/SKILL.md) Core Workflow
Steps 0–6 using the approved `requirements-approval.yaml` from
[`requirements.md`](requirements.md) as the inbound artifact. Goal: decide
reuse shapes for MIMO + baseline ontologies, reject a weak alternative,
and produce a signed `imports-manifest.yaml`.

## Step 0 — source availability (reuse-report header)

```yaml
source_freshness:
  - {source: OLS, probe: "runoak -i ols: search Violin", status: up, ts: "2026-04-22T14:10Z"}
  - {source: OBO Foundry, probe: "runoak -i obo: ontologies", status: up, ts: "2026-04-22T14:10Z"}
  - {source: MIMO (SPARQL endpoint), probe: "curl -I http://www.mimo-international.com/MIMO", status: cached, ts: "2026-04-14"}
  - {source: schema.org, probe: "curl -I https://schema.org/MusicInstrument", status: up, ts: "2026-04-22T14:11Z"}
```

## Always-reuse baseline (recorded before domain search)

| Candidate | Strategy | Rationale |
|---|---|---|
| BFO 2020 (`obo:bfo.owl`) | SUBSET | Upper ontology for Ensemble, Musician, Performance. |
| RO (core relations) | MIREOT | `BFO:0000050 part of`, `RO:0000057 has participant`. |
| IAO | MIREOT | `IAO:0000136 is about` for Composition ↔ Performance link (CQ-E-003). |
| SKOS | full_import | Concept labels + `skos:exactMatch` for CQ-E-005 mapping work. |
| PROV-O | MIREOT | Performance provenance (`prov:wasGeneratedBy`). |

## Step 2 — candidate matrix (`docs/reuse-report.md`)

| Candidate | Scope fit | License | Maintenance | Import size | Profile | Decision |
|---|---|---|---|---|---|---|
| **MIMO** (Musical Instruments Museum Online) | 78 % of instrument pre-glossary (Violin, Viola, Cello, Piano, Drum, …) matched via MIMO-core | CC-BY-SA-3.0 (compatible) | Active, last release 2025-11 | 12 k classes full, ~120 after STAR on leaf list | DL (cardinality on Hornbostel-Sachs facets) | **select (module extraction)** |
| **`weak-music-vocab`** (imaginary legacy SKOS list) | 40 % (lists 60 instruments but as skos:Concept only) | CC-BY-ND-4.0 | **rejected** — last release 2019-07 | 2 k triples | N/A | **reject** (license ND + unmaintained) |
| `schema.org/MusicInstrument` | 35 % (no Hornbostel-Sachs families) | CC-BY-SA | Active | negligible if linked via SSSOM | QL-ish | route to `ontology-mapper` as SSSOM target (Step 3.5 "bridge") |

## Step 3 + 3.5 — shape decision

- MIMO coverage is 78 % → falls in the 40–80 % band → **module extraction** via STAR (captures `hasHornbostelSachsCategory` axioms the reasoner needs for CQ-E-004's `EquivalentTo` probe).
- schema.org → **bridge** per [`modularization-and-bridges.md § 6`](../../modularization-and-bridges.md); hand off the MIMO ↔ schema.org `exactMatch` question to `ontology-mapper` (see [`mapper.md`](mapper.md)).
- `weak-music-vocab` → **reject** with rationale (mandatory per Step 2).

## Step 4 — extraction command + term file

```bash
# imports/mimo-terms.txt
mimo:Violin
mimo:Viola
mimo:Cello
mimo:Piano
mimo:Drum
mimo:Flute
```

```bash
.local/bin/robot extract --method STAR \
  --input-iri http://www.mimo-international.com/mimo-core.owl \
  --term-file ontologies/ensemble/imports/mimo-terms.txt \
  --output ontologies/ensemble/imports/mimo-import.owl
```

## Step 5 — ODP recommendations (`docs/odp-recommendations.md`)

| pattern_name | applicable_cqs | variables | example_instantiation | downstream_axiom_pattern | source |
|---|---|---|---|---|---|
| `value-partition` | CQ-E-004 (instrumentation-defined) | `{Family: owl:Class, Member: owl:Class}` | `{Family: StringFamily, Member: Violin}` | axiom-patterns § 3 + § 6 | `pattern-catalog.md § 3.1` |
| `role` | CQ-E-002 | `{Bearer: Musician, Role: StringPlayer}` | `{Bearer: ex:Alice, Role: :SoloistRole}` | axiom-patterns § 2 | `pattern-catalog.md § 3.3` |
| `n-ary-relation` | CQ-E-003 | `{Event: Performance, Part: {Composition, Date, Venue}}` | `{Event: ex:Perf2024, Piece: ex:OpusA}` | axiom-patterns § 9 | `pattern-catalog.md § 3.5` |

## Step 6 — `docs/imports-manifest.yaml`

```yaml
imports:
  - id: mimo-core
    source: http://www.mimo-international.com/mimo-core.owl
    version_iri: http://www.mimo-international.com/mimo-core/2025-11
    retrieval_date: 2026-04-22
    extraction_method: STAR
    term_file: imports/mimo-terms.txt
    module_file: imports/mimo-import.owl
    refresh_cadence_days: 90
    license: CC-BY-SA-3.0
  - id: bfo-core
    source: https://raw.githubusercontent.com/BFO-ontology/BFO/v2.0/bfo.owl
    version_iri: http://purl.obolibrary.org/obo/bfo/2020/bfo.owl
    retrieval_date: 2026-04-22
    extraction_method: SUBSET
    refresh_cadence_days: 365
  - id: weak-music-vocab
    extraction_method: rejected
    rejection_rationale: "ND license + unmaintained since 2019-07. Logged for audit only."
```

## Pitfall walk — "not-invented-here" vs weak reuse

The `weak-music-vocab` candidate matched ~40 % of the pre-glossary and
was tempting to adopt for rapid coverage. Step 2's license + maintenance
columns are **blocking**: a ND license forbids derivative works, and an
unmaintained source fails the maintenance gate. Silent exclusion would
have violated the "rejection rationale is mandatory" rule. Log the row
anyway so a future audit sees the candidate was considered and rejected.

## Handoff

Reuse report + ODP recs + `imports/mimo-import.owl` + signed
`imports-manifest.yaml` → `ontology-conceptualizer` (see
[`conceptualizer.md`](conceptualizer.md)); the schema.org bridge hook →
`ontology-mapper` (see [`mapper.md`](mapper.md)).
