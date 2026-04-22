# Microgrid — `ontology-scout` walkthrough

Walks [`ontology-scout`](../../../ontology-scout/SKILL.md) Steps 0–6 for
the microgrid ontology. Goal: pin OEO as the domain import, reject a
full schema.org import in favor of a SSSOM bridge, and produce an
`imports-manifest.yaml` with pinned OEO version + quarterly refresh.

## Step 0 — source availability (reuse-report header)

```yaml
source_freshness:
  - {source: OLS (OEO search), status: up, ts: "2026-04-22T15:02Z"}
  - {source: OBO Foundry, probe: "runoak -i obo: ontologies", status: up, ts: "2026-04-22T15:02Z"}
  - {source: QUDT 2.1 endpoint, probe: "curl -I http://qudt.org/2.1/vocab/unit", status: up, ts: "2026-04-22T15:03Z"}
  - {source: schema.org, status: up, ts: "2026-04-22T15:03Z"}
  - {source: OEO GitHub release feed, pinned: "oeo-1.16.0 (2026-02-15)", status: cached, ts: "2026-04-22"}
```

## Always-reuse baseline

| Candidate | Strategy | Rationale |
|---|---|---|
| BFO 2020 | SUBSET | Upper ontology for equipment/process/role. |
| RO | MIREOT | `RO:0000057 has_participant`, `BFO:0000050 part_of`, `RO:0002351 has_member`. |
| IAO | MIREOT | `IAO:0000136 is_about` for telemetry packets (CQ-M-003). |
| QUDT 2.1 | STAR | Units + quantity kinds for battery SOC, inverter power. |
| PROV-O | MIREOT | Dispatch-event provenance (CQ-M-002). |

## Step 2 — candidate matrix (`docs/reuse-report.md`)

| Candidate | Scope fit | License | Maintenance | Import size | Profile | Decision |
|---|---|---|---|---|---|---|
| **OEO 1.16.0** (Open Energy Ontology) | 68 % (generation, storage, inverter, dispatch) | CC-BY-4.0 (compatible) | Quarterly release cadence, active | 8.5 k triples full; ~350 after STAR on leaf list | DL (bearer_of, has_part chains) | **select** (STAR extraction) |
| `schema.org/Product` ↔ our `EnergyAsset` | Broad, ~20 % | CC-BY-SA | active; too broad for direct import | negligible | QL-ish | **bridge** (SSSOM, not import — cross-domain scope per `modularization-and-bridges.md § 6`) |
| `oeo-module` (community subset) | 62 % (near-duplicate of OEO slim) | CC-BY-4.0 | stale since 2024-09; parents `IAO:0000030` under BFO → leaks upper cats | — | — | **reject** (BFO leak risk; see workspace memory `feedback_bfo_leak_guard_iao`) |

## Step 3 + 3.5 — reuse shape decision

- OEO → **STAR module extraction** on 42 leaf terms (equipment,
  dispatch, telemetry). Full import would drag in 8k transitive triples
  we don't use.
- schema.org → **bridge** per `modularization-and-bridges.md § 5.1`
  SKOS-mapping bridge; floor at `skos:closeMatch` per cross-domain rule
  (see [`mapper.md`](mapper.md)).
- `oeo-module` → **reject** with explicit BFO-leak rationale.

## Step 4 — extraction

```bash
cat > ontologies/microgrid/imports/oeo-terms.txt <<'EOF'
oeo:PhotovoltaicPowerUnit
oeo:Inverter
oeo:BatteryEnergyStorageSystem
oeo:DispatchOperation
oeo:Islanding
oeo:TelemetryPacket
# …42 total
EOF

.local/bin/robot extract --method STAR \
  --input-iri https://raw.githubusercontent.com/OpenEnergyPlatform/ontology/v1.16.0/oeo.owl \
  --term-file ontologies/microgrid/imports/oeo-terms.txt \
  --output ontologies/microgrid/imports/oeo-import.ttl
```

## Step 5 — ODP recommendations (`docs/odp-recommendations.md`)

| pattern_name | applicable_cqs | example_instantiation | downstream_axiom_pattern |
|---|---|---|---|
| `part-whole` | CQ-M-001 | `{Whole: Microgrid, Part: SolarArray}` | axiom-patterns § 2 + § 12 property chain |
| `participation` | CQ-M-002 | `{Process: DispatchEvent, Participant: Inverter}` | axiom-patterns § 2 + § 9 N-ary |
| `information-realization` | CQ-M-003 | `{ICE: TelemetryPacket, About: Battery}` | IAO `is_about` + axiom-patterns § 2 |
| `role` | CQ-M-004 | `{Bearer: Inverter, Role: PrimaryInverterRole}` | axiom-patterns § 2 |

## Step 6 — `docs/imports-manifest.yaml`

```yaml
imports:
  - id: oeo
    source: https://raw.githubusercontent.com/OpenEnergyPlatform/ontology/v1.16.0/oeo.owl
    version_iri: http://openenergy-platform.org/ontology/oeo/1.16.0
    retrieval_date: 2026-04-22
    extraction_method: STAR
    term_file: imports/oeo-terms.txt
    module_file: imports/oeo-import.ttl
    refresh_cadence_days: 90
    license: CC-BY-4.0
  - id: qudt-unit
    source: http://qudt.org/2.1/vocab/unit
    version_iri: http://qudt.org/2.1/vocab/unit
    retrieval_date: 2026-04-22
    extraction_method: STAR
    refresh_cadence_days: 90
    license: CC-BY-4.0
  - id: bfo-core
    source: https://raw.githubusercontent.com/BFO-ontology/BFO/v2.0/bfo.owl
    version_iri: http://purl.obolibrary.org/obo/bfo/2020/bfo.owl
    retrieval_date: 2026-04-22
    extraction_method: SUBSET
    refresh_cadence_days: 365
  - id: oeo-module
    extraction_method: rejected
    rejection_rationale: "BFO leak risk: oeo-module parents IAO_0000030 under BFO; cross-checked against workspace memory feedback_bfo_leak_guard_iao."
```

## Pitfall walk — BFO leak via `IAO:0000030` (SIGNATURE)

The `oeo-module` community subset is superficially attractive (62%
coverage, overlapping scope), but its `IAO_0000030 information content
entity` is parented under `BFO:material_entity`. Importing it would
contaminate our `TelemetryPacket` classification — our model wants
`TelemetryPacket` as `IAO_0000030` in the **dependent continuant**
branch. This is the exact scenario flagged in workspace memory
`feedback_bfo_leak_guard_iao`: when in doubt, parent information
entities to `prov:Entity` instead, or carry the upstream BFO structure
directly via a controlled OEO import (which this scout chose instead).

## Handoff

Reuse report + `oeo-import.ttl` + pinned manifest + ODP recs →
`ontology-conceptualizer` (see [`conceptualizer.md`](conceptualizer.md)).
schema.org bridge target → `ontology-mapper` (see
[`mapper.md`](mapper.md)). Quarterly refresh cadence → curator
(`import_refresh` workflow, see [`curator.md`](curator.md)).
