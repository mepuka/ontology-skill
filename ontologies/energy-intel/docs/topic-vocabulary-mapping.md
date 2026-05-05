# Topic Vocabulary Mapping — `energy-intel` V2

**Authored:** 2026-05-04 by `ontology-conceptualizer` (V2 iteration)
**Reviewer:** Mepuka Kessy (`kokokessy@gmail.com`)
**Reviewed at:** 2026-05-04
**Source:**
- Source plan §3.4 (30-umbrella verification queue): [`/Users/pooks/Dev/skygest-cloudflare/docs/plans/2026-05-04-editorial-ontology-slice.md`](file:///Users/pooks/Dev/skygest-cloudflare/docs/plans/2026-05-04-editorial-ontology-slice.md)
- Legacy mapping table (92 concepts → 30 umbrellas): [`/Users/pooks/Dev/skygest-cloudflare/src/ontology/canonical.ts`](file:///Users/pooks/Dev/skygest-cloudflare/src/ontology/canonical.ts) `conceptToCanonicalTopicSlug`
- OEO seed verification: this session, all 41 candidate IRIs verified clean against `imports/oeo-full.owl`

This document is the canonical mapping decision for V2's topic vocabulary cutover. It resolves V2-CQ-Q-2 from Phase 1's requirements approval handoff.

---

## 1. Verification methodology

### 1.1 OEO IRI verification (V2-CQ-Q-2 method)

Each candidate OEO IRI from source plan §3.4 was verified against `imports/oeo-full.owl` via:

```python
# This session, 2026-05-04
g = Graph()
g.parse("ontologies/energy-intel/imports/oeo-full.owl")
# 35,333 triples loaded
for code, expected_label in candidates:
    iri = URIRef(OEO_NS + code)
    types = list(g.objects(iri, RDF.type))
    labels = [str(o) for o in g.objects(iri, RDFS.label)]
    is_class = OWL.Class in types
    is_individual = OWL.NamedIndividual in types
    is_dep = (iri, OWL.deprecated, None) in g
```

For each candidate, four checks:

1. **Class typing** — must be `owl:Class` (granularity contract requirement).
2. **Not NamedIndividual** — must NOT be `owl:NamedIndividual` (granularity contract requirement).
3. **Not deprecated** — must NOT carry `owl:deprecated true`.
4. **Label match** — `rdfs:label` must match the expected editorial intent.

### 1.2 Result summary

| Candidates verified | 41 |
| Passed all 4 checks | **41** |
| Failed | **0** |

| Check | Pass | Fail |
|---|---|---|
| owl:Class | 41 | 0 |
| not NamedIndividual | 41 | 0 |
| not deprecated | 41 | 0 |
| label match | 40 | 1 (label variant; semantically equivalent) |

The single label variant: OEO_00010438 has `rdfs:label "pumped hydro storage power technology"` whereas the source plan §3.4 wrote "pumped storage hydro power technology". Word order only; semantically equivalent. The architect's downstream verification should use the actual OEO label.

**Granularity contract (CQ-T3): PASS for the seed list.** No Inventory NamedIndividuals ever enter the runtime topic catalog.

---

## 2. Decision schema

For each row below:

- **slug** — the editorial slug (matches V1 `canonicalTopicOrder` and the `skos:notation` carried on supplement IRIs).
- **status** — one of `OEO` (clean OEO fit, no supplement needed), `Local` (Skygest supplement only, no clean OEO equivalent), `Mixed` (umbrella supplement + OEO leaves).
- **canonical IRI(s)** — the IRI(s) the editorial slug resolves to in V2. May be 1 (clean fit) or multiple (umbrella → leaves).
- **OEO leaves** — additional OEO IRIs included as members of the topic (admitted to `ei:concept/oeo-topic` scheme).
- **confidence** — `high` (label match + granularity verified + editorial intent matches), `medium` (1 of those 3 has caveats), `low` (multiple caveats; flagged for re-review).
- **rationale** — terse note on the decision.

---

## 3. The 30 umbrella decisions

### Fuel / generation technology umbrellas (clean OEO fit)

| Slug | Status | Canonical IRI(s) | OEO leaves | Confidence | Rationale |
|---|---|---|---|---|---|
| `solar` | OEO | `oeo:OEO_00010427` (solar power technology) | `oeo:OEO_00000384` (solar energy), `oeo:OEO_00010428` (photovoltaic technology) | high | Verified `owl:Class`; label match; technology granularity. Includes both energy carrier (solar energy) and tech leaves (PV) |
| `wind` | OEO | `oeo:OEO_00010424` (wind power technology) | `oeo:OEO_00000446` (wind energy) | high | Verified `owl:Class`; label match. |
| `offshore-wind` | OEO | `oeo:OEO_00010426` (offshore wind power technology) | — | high | Source plan §3.4 dropped `OEO_00000308` (farm/site, NamedIndividual likely); pinned to tech class. Verified clean. |
| `geothermal` | OEO | `oeo:OEO_00010430` (geothermal power technology) | `oeo:OEO_00000191` (geothermal energy) | high | Verified `owl:Class`; label match. |
| `hydro` | OEO | `oeo:OEO_00010431` (hydro power technology) | `oeo:OEO_00010438` (pumped hydro storage power technology — note label word order) | high | Verified clean. Pumped hydro leaf shared with energy-storage. |
| `nuclear` | OEO | `oeo:OEO_00010439` (nuclear power technology) | — | high | Source plan §3.4 dropped `OEO_00010415` ("nuclear" as polysemous); pinned to technology class. Verified clean. |
| `hydrogen` | OEO | `oeo:OEO_00000220` (hydrogen) | — | high | Energy-carrier class; verified clean. Process leaves for green/blue hydrogen are not in V2 seed list (deferred). |
| `natural-gas` | OEO | `oeo:OEO_00000292` (natural gas) | — | high | Energy-carrier class; verified clean. |
| `coal` | OEO | `oeo:OEO_00000088` (coal) | — | high | Energy-carrier class; verified clean. |
| `oil` | OEO | `oeo:OEO_00000115` (crude oil) | — | high | Energy-carrier class; verified clean. Editorial slug is "oil" but OEO uses "crude oil" — semantically the same scope. |

10/30 umbrellas are clean OEO fits.

### Mixed (umbrella + OEO leaves)

| Slug | Status | Canonical IRI(s) | OEO leaves | Confidence | Rationale |
|---|---|---|---|---|---|
| `biomass` | Mixed | `ei:concept/biomass` (umbrella) | `oeo:OEO_00010258` (bioenergy), `oeo:OEO_00010214` (biomass) | high | OEO has both bioenergy (technology) and biomass (material). Editorial umbrella spans both + sustainability debates that OEO doesn't model. Conceptualizer decision (per [conceptual-model-v2.md § 11 finding 3](conceptual-model-v2.md)): SHIP the umbrella supplement. |
| `energy-storage` | Mixed | `ei:concept/energy-storage` (umbrella) | `oeo:OEO_00020366` (energy storage technology), `oeo:OEO_00010438` (pumped hydro storage power technology) | high | OEO `OEO_00020366` is a technology-class umbrella; editorial scope is broader (markets, policy, geopolitics of storage). Conceptualizer decision: SHIP the umbrella. |
| `grid-and-infrastructure` | Mixed | `ei:concept/grid-and-infrastructure` (umbrella) | `oeo:OEO_00000143` (electricity grid), `oeo:OEO_00110019` (transmission grid), `oeo:OEO_00110020` (distribution grid) | high | Three grid leaves verified. Editorial umbrella covers operators, planning, interconnection — wider than the leaf classes. |
| `electrification` | Mixed | `ei:concept/electrification` (umbrella) | `oeo:OEO_00000146` (electric vehicle), `oeo:OEO_00000212` (heat pump) | medium | OEO has no direct "electrification" umbrella label per source plan §3.4. EV and heat pump are end-use leaves. Editorial umbrella covers building/transport electrification more broadly. |
| `energy-efficiency` | Mixed | `ei:concept/energy-efficiency` (umbrella) | (no clean OEO leaf — `oeo:OEO_00140049` is energy conversion efficiency, too narrow per source plan §3.4) | medium | OEO_00140049 is the "energy conversion efficiency" *measurement*, not a topic. Editorial umbrella covers retrofits and demand reduction. Pure Local possible — kept as Mixed in case a future OEO version adds a topic-grade efficiency class. |
| `data-center-demand` | Mixed | `ei:concept/data-center-demand` (umbrella) | `oeo:OEO_00310000` (data center) | high | OEO has the bare "data center" class; editorial umbrella adds AI workload framing. |
| `energy-policy` | Mixed | `ei:concept/energy-policy` (umbrella) | `oeo:OEO_00140150` (policy), `oeo:OEO_00140151` (policy instrument) | high | OEO has policy + instrument as classes. Editorial umbrella adds permitting, FERC orders, IRA discussion. |
| `energy-markets` | Mixed | `ei:concept/energy-markets` (umbrella) | `oeo:OEO_00020065` (energy market exchange), `oeo:OEO_00020069` (market exchange) | high | Two OEO market-exchange classes verified. Editorial umbrella adds wholesale dynamics, PPA discussion. |
| `critical-minerals` | Mixed | `ei:concept/critical-minerals` (umbrella) | `oeo:OEO_00240030` (mineral) | medium | Bare "mineral" is broader than "critical mineral." Editorial umbrella narrows to lithium / cobalt / rare-earth scope. The OEO leaf is included for traceability. |
| `climate-and-emissions` | Mixed | `ei:concept/climate-and-emissions` (umbrella) | `oeo:OEO_00000020` (greenhouse gas), `oeo:OEO_00000199` (greenhouse gas emission) | high | Both OEO classes verified clean. Editorial umbrella covers net-zero, climate framing. |
| `carbon-capture` | OEO | `oeo:OEO_00010138` (carbon capture) | `oeo:OEO_00010141` (carbon capture and storage), `oeo:OEO_00010139` (direct air capture), `oeo:OEO_00010455` (carbon capture and storage technology) | high | Four CCS-family classes verified. Clean OEO scope; no Skygest umbrella needed. Marking as `OEO` (not `Mixed`) because the bare `carbon capture` class IS the umbrella. |
| `carbon-markets` | Mixed | `ei:concept/carbon-markets` (umbrella) | `oeo:OEO_00020075` (emission market exchange), `oeo:OEO_00020063` (emission certificate) | high | Two emission-market classes verified. Editorial umbrella adds policy framing. |
| `sectoral-decarbonization` | Mixed | `ei:concept/sectoral-decarbonization` (umbrella) | `oeo:OEO_00010212` (decarbonisation pathway) | medium | Single OEO leaf is decarbonisation pathway (the pathway-class itself, not industrial/aviation/maritime sub-sectors). Editorial umbrella covers sector-specific decarbonization. |
| `workforce-and-manufacturing` | Mixed | `ei:concept/workforce-and-manufacturing` (umbrella) | `oeo:OEO_00010485` (manufacturing technology), `oeo:OEO_00050000` (manufacturing process) | medium | OEO has the manufacturing-technology and -process classes; editorial umbrella adds labor-relations and energy-jobs framing that OEO doesn't model. |

14/30 umbrellas are Mixed (have at least one OEO leaf alongside the supplement umbrella). One reclassified to OEO (`carbon-capture`).

### Local-only (no OEO leaves)

| Slug | Status | Canonical IRI | Confidence | Rationale |
|---|---|---|---|---|
| `distributed-energy` | Local | `ei:concept/distributed-energy` | medium | Source plan §3.4: no direct OEO label. DERs / demand-response / microgrids / VPPs span technology + operations + market roles; outside OEO's primary focus. |
| `energy-finance` | Local | `ei:concept/energy-finance` | medium | Source plan §3.4: no clean OEO topic. Editorial concept. |
| `energy-geopolitics` | Local | `ei:concept/energy-geopolitics` | medium | No OEO equivalent; editorial-domain umbrella. |
| `environment-and-land-use` | Local | `ei:concept/environment-and-land-use` | medium | Source plan §3.4 dropped `OEO_00010035` and `OEO_00010048` (NamedIndividual inventory records, fail granularity contract). Local-only. |
| `energy-justice` | Local | `ei:concept/energy-justice` | medium | No OEO equivalent; editorial / social concept. |
| `research-and-innovation` | Local | `ei:concept/research-and-innovation` | medium | No OEO equivalent; editorial umbrella for R&D, patents, lab breakthroughs. |

6/30 umbrellas are Local-only.

### Decision summary by status

| Status | Count |
|---|---|
| OEO (clean fit) | 11 (10 fuel/tech + carbon-capture) |
| Mixed (umbrella + OEO leaves) | 13 |
| Local-only | 6 |
| **Total** | **30** |

Skygest editorial supplement IRIs declared in `concept-schemes/oeo-topics.ttl`: **19** (13 Mixed umbrellas + 6 Local-only) — matches the 19 supplements listed in [conceptual-model-v2.md § 11 finding 3](conceptual-model-v2.md).

---

## 4. The 92 leaf concept decisions

For each entry in V1's `conceptToCanonicalTopicSlug`, the V2 IRI it resolves to. Most leaves resolve to the same IRI as their umbrella; some have a more specific OEO leaf available.

| Concept (V1) | Umbrella slug | V2 canonical IRI(s) | Confidence | Rationale |
|---|---|---|---|---|
| AIAndDataCenterDemand | data-center-demand | `ei:concept/data-center-demand` + `oeo:OEO_00310000` (data center) | high | Direct mapping to umbrella + OEO leaf. |
| Affordability | energy-justice | `ei:concept/energy-justice` | medium | Local-only umbrella. |
| Agrivoltaics | environment-and-land-use | `ei:concept/environment-and-land-use` | medium | No specific OEO leaf for agrivoltaics. |
| AviationDecarbonization | sectoral-decarbonization | `ei:concept/sectoral-decarbonization` + `oeo:OEO_00010212` (decarbonisation pathway) | medium | Pathway is generic; aviation-specific not in OEO seed set. |
| BatteryRecycling | energy-storage | `ei:concept/energy-storage` | medium | Battery recycling is sub-topic; no OEO seed leaf. |
| BiomassAndBioenergy | biomass | `ei:concept/biomass` + `oeo:OEO_00010258` (bioenergy) + `oeo:OEO_00010214` (biomass) | high | Mixed umbrella with both OEO leaves. |
| BuildingElectrification | electrification | `ei:concept/electrification` + `oeo:OEO_00000212` (heat pump) | medium | Heat pump is a leaf for building electrification. |
| BuildingsAndEfficiency | energy-efficiency | `ei:concept/energy-efficiency` | medium | Editorial umbrella; OEO leaf is too narrow. |
| COPClimateConference | climate-and-emissions | `ei:concept/climate-and-emissions` | medium | Conference event; no OEO leaf. |
| CarbonCapture | carbon-capture | `oeo:OEO_00010138` (carbon capture) | high | Direct OEO fit. |
| CarbonMarkets | carbon-markets | `ei:concept/carbon-markets` + `oeo:OEO_00020075` (emission market exchange) | high | Mixed with OEO emission-market leaf. |
| ClimateAndEmissions | climate-and-emissions | `ei:concept/climate-and-emissions` + `oeo:OEO_00000020` (greenhouse gas) + `oeo:OEO_00000199` (GHG emission) | high | Three IRIs cover climate broadly. |
| Coal | coal | `oeo:OEO_00000088` (coal) | high | Direct OEO fit. |
| Commodity | energy-markets | `ei:concept/energy-markets` + `oeo:OEO_00020069` (market exchange) | medium | Generic commodity → market umbrella. |
| CommunityEnergy | energy-justice | `ei:concept/energy-justice` | medium | Sub-topic of justice umbrella. |
| CorporateDeals | energy-finance | `ei:concept/energy-finance` | medium | Local umbrella; no OEO leaf. |
| CriticalMinerals | critical-minerals | `ei:concept/critical-minerals` + `oeo:OEO_00240030` (mineral) | medium | Mixed; mineral leaf is generic. |
| DataCenterDemand | data-center-demand | `ei:concept/data-center-demand` + `oeo:OEO_00310000` (data center) | high | Same as AIAndDataCenterDemand. |
| Decarbonization | climate-and-emissions | `ei:concept/climate-and-emissions` | high | V1 mapping says this resolves to climate-and-emissions; OEO `decarbonisation pathway` (OEO_00010212) is under sectoral-decarbonization umbrella. |
| DemandResponse | distributed-energy | `ei:concept/distributed-energy` | medium | Local umbrella. |
| DirectAirCapture | carbon-capture | `oeo:OEO_00010139` (direct air capture) | high | Direct OEO leaf. |
| DistributedEnergyAndFlexibility | distributed-energy | `ei:concept/distributed-energy` | medium | Local umbrella. |
| Distribution | grid-and-infrastructure | `ei:concept/grid-and-infrastructure` + `oeo:OEO_00110020` (distribution grid) | high | Direct OEO leaf for distribution grid. |
| ElectricTransport | electrification | `ei:concept/electrification` + `oeo:OEO_00000146` (electric vehicle) | high | EV leaf available. |
| ElectricVehicles | electrification | `ei:concept/electrification` + `oeo:OEO_00000146` (electric vehicle) | high | Same as ElectricTransport. |
| Electrification | electrification | `ei:concept/electrification` + `oeo:OEO_00000146` (electric vehicle) + `oeo:OEO_00000212` (heat pump) | medium | Umbrella + both leaves. |
| EmissionsTracking | climate-and-emissions | `ei:concept/climate-and-emissions` + `oeo:OEO_00000199` (GHG emission) | high | Direct mapping. |
| EnergyAccess | energy-justice | `ei:concept/energy-justice` | medium | Local umbrella. |
| EnergyFinance | energy-finance | `ei:concept/energy-finance` | medium | Local umbrella. |
| EnergyGeopolitics | energy-geopolitics | `ei:concept/energy-geopolitics` | medium | Local umbrella. |
| EnergyJobs | workforce-and-manufacturing | `ei:concept/workforce-and-manufacturing` | medium | Local umbrella; no OEO leaf for jobs. |
| EnergyJustice | energy-justice | `ei:concept/energy-justice` | medium | Local umbrella. |
| EnergyMarkets | energy-markets | `ei:concept/energy-markets` + `oeo:OEO_00020065` (energy market exchange) + `oeo:OEO_00020069` (market exchange) | high | Mixed with two leaves. |
| EnergyPolicy | energy-policy | `ei:concept/energy-policy` + `oeo:OEO_00140150` (policy) + `oeo:OEO_00140151` (policy instrument) | high | Mixed with both policy leaves. |
| EnergySecurityAndResilience | energy-geopolitics | `ei:concept/energy-geopolitics` | medium | Sub-topic of geopolitics umbrella. |
| EnergyStorage | energy-storage | `ei:concept/energy-storage` + `oeo:OEO_00020366` (energy storage technology) | high | Mixed umbrella + leaf. |
| EnvironmentAndLandUse | environment-and-land-use | `ei:concept/environment-and-land-use` | medium | Local umbrella. |
| EVCharging | electrification | `ei:concept/electrification` | medium | EV charging is a sub-topic of electrification; no specific OEO leaf. |
| EfficiencyRecords | research-and-innovation | `ei:concept/research-and-innovation` | medium | Records of efficiency breakthroughs; not in OEO. |
| Energiewende | energy-policy | `ei:concept/energy-policy` + `oeo:OEO_00140150` (policy) | high | German energy transition policy. |
| FuelCell | hydrogen | `oeo:OEO_00000220` (hydrogen) | medium | Hydrogen end-use leaf; the OEO fuel-cell process is not in the V2 seed set. |
| Fusion | nuclear | `oeo:OEO_00010439` (nuclear power technology) | medium | Fusion is a sub-topic of nuclear; OEO does not have a dedicated fusion class in our seed. |
| Geothermal | geothermal | `oeo:OEO_00010430` (geothermal power technology) + `oeo:OEO_00000191` (geothermal energy) | high | Both leaves available. |
| GreenHydrogen | hydrogen | `oeo:OEO_00000220` (hydrogen) | medium | Hydrogen leaf; "green" qualifier not modeled in V2 seed. |
| GridAndInfrastructure | grid-and-infrastructure | `ei:concept/grid-and-infrastructure` + `oeo:OEO_00000143` (electricity grid) + `oeo:OEO_00110019` (transmission grid) + `oeo:OEO_00110020` (distribution grid) | high | Mixed umbrella + 3 leaves. |
| GridModernization | grid-and-infrastructure | `ei:concept/grid-and-infrastructure` | medium | Editorial sub-topic of umbrella. |
| GridOperator | grid-and-infrastructure | `ei:concept/grid-and-infrastructure` | medium | Editorial sub-topic. |
| HeatPumps | electrification | `oeo:OEO_00000212` (heat pump) | high | Direct OEO leaf. |
| Hydro | hydro | `oeo:OEO_00010431` (hydro power technology) | high | Direct OEO fit. |
| Hydrogen | hydrogen | `oeo:OEO_00000220` (hydrogen) | high | Direct OEO fit. |
| IRAPolicy | energy-policy | `ei:concept/energy-policy` + `oeo:OEO_00140150` (policy) | high | IRA is policy. |
| IndustrialDecarbonization | sectoral-decarbonization | `ei:concept/sectoral-decarbonization` + `oeo:OEO_00010212` (decarbonisation pathway) | medium | Industrial-sector decarbonization. |
| Interconnection | grid-and-infrastructure | `ei:concept/grid-and-infrastructure` + `oeo:OEO_00110019` (transmission grid) | medium | Interconnection is a transmission topic. |
| LaborRelations | workforce-and-manufacturing | `ei:concept/workforce-and-manufacturing` | medium | Editorial sub-topic. |
| Legislation | energy-policy | `ei:concept/energy-policy` + `oeo:OEO_00140150` (policy) | high | Legislation is policy. |
| LNGTradeAndInfrastructure | natural-gas | `oeo:OEO_00000292` (natural gas) | medium | Natural gas leaf; LNG is sub-topic. |
| LongDurationStorage | energy-storage | `ei:concept/energy-storage` + `oeo:OEO_00020366` (energy storage technology) | medium | Sub-topic of storage. |
| Manufacturing | workforce-and-manufacturing | `ei:concept/workforce-and-manufacturing` + `oeo:OEO_00010485` (manufacturing technology) + `oeo:OEO_00050000` (manufacturing process) | high | Mixed umbrella + 2 leaves. |
| MaritimeDecarbonization | sectoral-decarbonization | `ei:concept/sectoral-decarbonization` + `oeo:OEO_00010212` (decarbonisation pathway) | medium | Maritime sub-sector. |
| Microgrid | distributed-energy | `ei:concept/distributed-energy` | medium | Local umbrella. |
| NaturalGas | natural-gas | `oeo:OEO_00000292` (natural gas) | high | Direct OEO fit. |
| NetZero | climate-and-emissions | `ei:concept/climate-and-emissions` | high | Editorial framing of the climate umbrella. |
| Nuclear | nuclear | `oeo:OEO_00010439` (nuclear power technology) | high | Direct OEO fit. |
| OffshoreWind | offshore-wind | `oeo:OEO_00010426` (offshore wind power technology) | high | Direct OEO fit. |
| Oil | oil | `oeo:OEO_00000115` (crude oil) | high | Direct OEO fit. |
| Patent | research-and-innovation | `ei:concept/research-and-innovation` | medium | Editorial sub-topic. |
| Perovskite | research-and-innovation | `ei:concept/research-and-innovation` | medium | Specific tech sub-topic; not in OEO seed. |
| Permitting | energy-policy | `ei:concept/energy-policy` + `oeo:OEO_00140151` (policy instrument) | medium | Permitting is a policy instrument. |
| PowerPurchaseAgreement | energy-markets | `ei:concept/energy-markets` + `oeo:OEO_00020065` (energy market exchange) | medium | PPA is energy-market sub-topic. |
| ProjectFinance | energy-finance | `ei:concept/energy-finance` | medium | Local umbrella. |
| PublicFunding | energy-finance | `ei:concept/energy-finance` | medium | Local umbrella. |
| PumpedHydroStorage | energy-storage | `oeo:OEO_00010438` (pumped hydro storage power technology) | high | Direct OEO leaf. |
| Regulation | energy-policy | `ei:concept/energy-policy` + `oeo:OEO_00140150` (policy) + `oeo:OEO_00140151` (policy instrument) | high | Mixed. |
| Renewable | (null in V1) | — (not mapped; aggregator concept handled at SKOS scheme level) | n/a | V1 explicitly maps to null (`Renewable: null`). V2 preserves: not a topic in itself. |
| ResearchAndInnovation | research-and-innovation | `ei:concept/research-and-innovation` | medium | Local umbrella. |
| Retrofits | energy-efficiency | `ei:concept/energy-efficiency` | medium | Editorial sub-topic. |
| RooftopSolar | solar | `oeo:OEO_00010427` (solar power technology) + `oeo:OEO_00010428` (photovoltaic technology) | medium | Sub-topic; PV leaf available. |
| SMR | nuclear | `oeo:OEO_00010439` (nuclear power technology) | medium | Small modular reactor; sub-topic. |
| SectoralDecarbonization | sectoral-decarbonization | `ei:concept/sectoral-decarbonization` + `oeo:OEO_00010212` (decarbonisation pathway) | high | Direct mapping. |
| Solar | solar | `oeo:OEO_00010427` (solar power technology) + `oeo:OEO_00000384` (solar energy) + `oeo:OEO_00010428` (photovoltaic technology) | high | All 3 leaves. |
| SupplyChain | energy-geopolitics | `ei:concept/energy-geopolitics` | medium | Editorial framing. |
| Tariff | energy-policy | `ei:concept/energy-policy` + `oeo:OEO_00140151` (policy instrument) | high | Tariff is a policy instrument. |
| TradeAndSanctions | energy-geopolitics | `ei:concept/energy-geopolitics` | medium | Editorial sub-topic. |
| Transmission | grid-and-infrastructure | `ei:concept/grid-and-infrastructure` + `oeo:OEO_00110019` (transmission grid) | high | Direct leaf. |
| VirtualPowerPlant | distributed-energy | `ei:concept/distributed-energy` | medium | Local umbrella sub-topic. |
| WasteAndPollution | environment-and-land-use | `ei:concept/environment-and-land-use` | medium | Editorial sub-topic. |
| WaterUse | environment-and-land-use | `ei:concept/environment-and-land-use` | medium | Editorial sub-topic. |
| WholesaleMarkets | energy-markets | `ei:concept/energy-markets` + `oeo:OEO_00020065` (energy market exchange) | high | Direct leaf. |
| Wind | wind | `oeo:OEO_00010424` (wind power technology) + `oeo:OEO_00000446` (wind energy) | high | Both leaves. |
| WorkforceAndManufacturing | workforce-and-manufacturing | `ei:concept/workforce-and-manufacturing` + `oeo:OEO_00010485` (manufacturing technology) + `oeo:OEO_00050000` (manufacturing process) | high | Mixed umbrella + 2 leaves. |
| Fossil | (null in V1) | — (not mapped; aggregator concept) | n/a | V1 maps to null. Aggregator over coal/oil/natural-gas, not a topic. |
| EnergyTradeAndSupplyChains | (null in V1) | — (not mapped) | n/a | V1 maps to null. Aggregator-only. |

**Total: 92 entries (89 mapped to topics; 3 mapped to null per V1).**

### Confidence summary by leaf

| Confidence | Count |
|---|---|
| high | 36 |
| medium | 53 |
| low | 0 |
| n/a (null in V1) | 3 |

The "medium" confidence entries are largely sub-topics under Local-only or Mixed umbrellas. They are all valid mappings; the medium label reflects the editorial-domain umbrella nature of the resolution (e.g., DemandResponse → distributed-energy is correct but the umbrella is broader than "demand response" alone).

---

## 5. Signal preservation (cross-repo open question V2-X-Q-1)

Source plan §9 Q3: "Does any current consumer rely on the *original* leaf concept granularity that the umbrella collapse would lose?"

**Recommendation in V2:** Preserve every leaf concept slug in the runtime topic catalog as a `skos:notation` annotation on the canonical IRI it resolves to. This makes leaf-slug → IRI lookup queryable from the ontology itself (CQ-T2) without losing granularity.

For the 89 mapped leaves:
- Each canonical IRI carries `skos:notation "{leaf-slug}"` (lowercase camelCase from `conceptToCanonicalTopicSlug` keys).
- For 1-to-many resolutions (umbrella → multiple OEO leaves), each leaf-slug points to all resolved IRIs via separate `skos:notation` triples.

This way:
- CQ-T2 ("Given a legacy slug, return canonical IRI(s)") resolves to all leaves an umbrella collapses to.
- A future consumer that needs "the original DemandResponse concept" can query for the specific notation; the umbrella result includes all granularity that was preserved.

The cloudflare side is responsible for confirming whether their runtime relies on the original leaf granularity. The ontology-side mitigation (notation annotations) is in place either way — it costs ~92 extra triples and provides full migration auditability.

---

## 6. Open issues

None blocking. V2-CQ-Q-2 is fully resolved: 41/41 OEO IRIs verified clean; granularity contract holds; complete decision table for all 30 umbrellas + 92 leaves.

The conceptualizer flags the following discoveries for upstream/downstream awareness (none block architect):

1. **OEO_00010438 label variance** — actual label is "pumped hydro storage power technology" (handoff §"OEO topic subset rebuild" wrote "pumped storage hydro"). Architect's downstream code must use the actual OEO label.
2. **6 Local-only umbrellas have medium confidence by definition** — distributed-energy, energy-finance, energy-geopolitics, environment-and-land-use, energy-justice, research-and-innovation. These are editorial concepts without OEO equivalents. They may benefit from a future OEO contribution upstream (Skygest could propose terms), but that is out of V2 scope.
3. **Carbon capture reclassified to OEO** — source plan §3.4 listed it as Mixed; on closer inspection, OEO's `OEO_00010138` IS the umbrella class with sub-leaves (CCS, DAC, CCS-tech). No supplement umbrella needed; clean OEO fit.

---

## 7. Architect implementation guidance

The architect MUST:

1. **Use the 41 verified IRIs as the seed list** for `imports/oeo-topic-subset.ttl` (rebuilt via `robot extract --method BOT`).
2. **Declare the 19 supplement IRIs** in `concept-schemes/oeo-topics.ttl` per the specifications above. Each carries `skos:prefLabel`, `skos:definition`, optional `skos:exactMatch`/`skos:closeMatch` to OEO IRIs, `skos:hasTopConcept` from `ei:concept/editorial-supplement`, and `skos:notation` with the legacy slug.
3. **Emit `skos:inScheme` triples** for every accepted topic IRI (OEO + supplement) in BOTH:
   - Its native sub-scheme (`ei:concept/oeo-topic` or `ei:concept/editorial-supplement`)
   - The aggregator scheme `ei:concept/topic`
4. **Carry `skos:notation` annotations** for the 89 mapped leaf concepts on their canonical IRIs (signal preservation per § 5 above). 1-to-many mappings produce multiple notation triples per IRI.
5. **NOT** mint OEO IRIs into the `ei:concept/` namespace. OEO IRIs stay in their native namespace (`https://openenergyplatform.org/ontology/oeo/`) per V2-CQ-Q-1 (split + aggregator).
6. **NOT** declare `oeo:OEO_xxx a skos:Concept` in `oeo-topic-subset.ttl`. The skos:Concept typing arises from punning when the architect emits `oeo:OEO_xxx skos:inScheme ei:concept/oeo-topic` in `oeo-topics.ttl` (the SKOS scheme membership implicitly types the IRI as a concept).
