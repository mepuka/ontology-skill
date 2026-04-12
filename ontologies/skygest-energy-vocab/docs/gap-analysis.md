# Skygest Energy Vocabulary — Gap Analysis

**Date**: 2026-04-12
**Source**: Corpus analysis of 5,000 posts from `energy-news-filtered` store
(34,646 total posts from 2,371 energy-focused authors), cross-referenced
with IEA/OEO/SDMX domain structure.

**Methodology**: Extracted energy-domain n-grams from post text, classified
as COVERED (surface form exists in vocabulary) or GAP (no concept or surface
form). Organized by priority based on corpus frequency and domain importance.

---

## Priority Tiers

### Tier 1: High-frequency gaps (>20 occurrences in 5K sample)

These terms appear regularly in energy discourse and represent significant
vocabulary blind spots.

| Term | Corpus Count | Gap Type | Recommended Action |
|------|-------------|----------|-------------------|
| ETS / emissions trading | 195 | Missing concept | Add to DomainObjectScheme: `carbon market` |
| LNG | 117 | Missing surface form | Add as altLabel on NaturalGasDomain or new concept |
| fossil fuel | 113 | Missing concept | Add to TechnologyOrFuelScheme: `fossil fuel` (parent) |
| electric vehicle / EV | 110 | Thin surface forms | Enrich TransportDomain altLabels + consider EV-specific concept |
| FIT (feed-in tariff) | 87 | Missing concept | Add to new PolicyInstrumentScheme or MeasuredPropertyScheme |
| auction | 51 | Missing concept | Policy/market mechanism — consider scope |
| methane | 36 | Missing concept | Add to TechnologyOrFuelScheme or DomainObjectScheme |
| carbon capture / CCS / CCUS | 34+28+10 | Missing concept | Add to TechnologyOrFuelScheme: `carbon capture` |
| decarbonization / net zero | 31+18 | Missing concept | Add to DomainObjectScheme: `decarbonization` |
| SMR / small modular reactor | 24+20 | Missing surface form | Add as altLabels on Nuclear concept |
| rooftop solar | 23 | Covered (solar PV) | Verify "rooftop solar" is an altLabel |
| outage / blackout | 21+15 | Missing concept | Add to DomainObjectScheme: `grid reliability` |

### Tier 2: Medium-frequency gaps (5-20 occurrences)

| Term | Corpus Count | Gap Type | Recommended Action |
|------|-------------|----------|-------------------|
| PPA / power purchase agreement | 19 | Missing concept | Market mechanism — DomainObjectScheme or new scheme |
| interconnection | 19 | Thin surface forms | Enrich InterconnectionQueueDomain or GridDomain |
| energy storage | 16 | Covered (BatteryStorage) | Verify "energy storage" altLabel exists |
| utility-scale | 13 | Missing surface form | Add as altLabel context qualifier |
| carbon removal | 11 | Missing concept | Related to CCS but distinct (DAC, BECCS) |
| carbon market / credit / tax | 10+9+3 | Missing concept | Add carbon market as DomainObject concept |
| virtual power plant | 8 | Missing concept | Add to DomainObjectScheme |
| EV charging / charging station | 7+6 | Missing concept | Add to DomainObjectScheme |
| grid reliability | 7 | Surface form gap | Add "reliability" surface forms to GridDomain |

### Tier 3: Low-frequency but domain-important gaps

| Term | Corpus Count | Gap Type | Recommended Action |
|------|-------------|----------|-------------------|
| fuel cell | 3 | Missing concept | Add to TechnologyOrFuelScheme |
| microgrid | 3 | Covered (grid) | Verify altLabel |
| community solar | 3 | Covered (solar PV) | Verify altLabel |
| just transition | 3 | Missing concept | Social/policy domain — scope decision |
| wholesale market / spot market | 2 | Missing surface form | Add to existing Price/market concepts |
| e-fuel / synthetic fuel | 2+1 | Missing concept | Add to TechnologyOrFuelScheme |
| retrofit / repowering | 4 | Missing concept | MeasuredProperty or DomainObject |
| decommissioning | 2 | Missing concept | MeasuredProperty (lifecycle stage) |
| LCOE / levelized cost | 1 | Missing surface form | Already an altLabel on PriceMeasure? Verify |
| floating offshore wind | 1 | Missing surface form | Add to OffshoreWind altLabels |
| stranded asset | 1 | Missing concept | Financial/risk domain — scope decision |
| behind the meter | 1 | Missing concept | Installation-type qualifier |
| day-ahead market | 1 | Missing surface form | Add to Aggregation or market concepts |

---

## Recommended Concept Additions by Scheme

### TechnologyOrFuelScheme (currently 21 concepts)

| New Concept | prefLabel | Key Surface Forms | Justification |
|-------------|-----------|-------------------|---------------|
| CarbonCapture | carbon capture | CCS, CCUS, carbon capture and storage, DAC | 72 corpus hits; critical energy transition tech |
| FossilFuel | fossil fuel | fossil fuels, fossil, conventional | 113 hits; parent concept for coal/gas/oil |
| FuelCell | fuel cell | fuel cells, SOFC, PEMFC, hydrogen fuel cell | 3 hits but growing domain |
| Methane | methane | methane, CH4, fugitive emissions | 36 hits; distinct from natural gas (emissions focus) |
| SyntheticFuel | synthetic fuel | e-fuel, efuel, synthetic fuel, SAF | Emerging tech; 3 hits |
| CHP | combined heat and power | CHP, cogeneration, cogen | Standard IEA technology category |
| Diesel | diesel | diesel, fuel oil, heavy fuel oil | IEA fuel category, missing |

### DomainObjectScheme (currently 24 concepts)

| New Concept | prefLabel | Key Surface Forms | Justification |
|-------------|-----------|-------------------|---------------|
| CarbonMarket | carbon market | ETS, emissions trading, carbon credit, carbon tax, cap and trade, allowance | 195+ corpus hits combined |
| EVCharging | EV charging | EV charging, charging station, charging infrastructure, EVSE | 13 hits; distinct infrastructure domain |
| Decarbonization | decarbonization | decarbonization, net zero, carbon neutral, climate target | 49 hits combined |
| VirtualPowerPlant | virtual power plant | VPP, virtual power plant, aggregator | 8 hits; emerging grid concept |
| GridReliability | grid reliability | grid reliability, outage, blackout, brownout, SAIDI | 36+ hits combined |
| WholesaleMarket | wholesale market | wholesale market, spot market, day-ahead, balancing market | Market structure domain |
| CommunityEnergy | community energy | community solar, community energy, energy cooperative | Distributed energy domain |
| DistributedGeneration | distributed generation | behind the meter, rooftop, distributed, DER | Installation-type domain |

### MeasuredPropertyScheme (currently 15 concepts)

| New Concept | prefLabel | Key Surface Forms | Justification |
|-------------|-----------|-------------------|---------------|
| CapacityFactor | capacity factor | capacity factor, load factor, utilization rate, availability | Standard power plant metric |
| LevelizedCost | levelized cost | LCOE, LCOS, levelized cost | Key economic metric for renewables |
| Decommissioning | decommissioning | decommissioning, retirement, phase-out, shutdown | Lifecycle stage metric |
| Subsidy | subsidy | subsidy, incentive, feed-in tariff, FIT, tax credit, PTC, ITC | 87+ hits (FIT alone); policy mechanism |

### Surface Form Enrichment (existing concepts)

| Concept | Missing Surface Forms | Source |
|---------|----------------------|--------|
| Nuclear | SMR, small modular reactor, advanced nuclear, Gen IV | 44 corpus hits |
| NaturalGasDomain | LNG, liquefied natural gas, gas pipeline, gas infrastructure | 117+14 hits |
| SolarPhotovoltaic | rooftop solar, utility-scale solar, community solar, floating solar | 23+ hits |
| OffshoreWind | floating wind, floating offshore, bottom-fixed | Emerging sub-category |
| GridDomain | grid reliability, grid stability, frequency regulation, ancillary services | 7+ hits |
| TransportDomain | electric vehicle, EV, charging, e-mobility, zero-emission vehicle | 110 hits |
| PriceMeasure | LCOE, levelized cost, wholesale price, spot price, day-ahead price | Market terminology |
| BatteryStorage | grid-scale storage, utility-scale battery, behind-the-meter storage | Installation qualifiers |

---

## Scope Decisions (Resolved 2026-04-12)

1. **Policy instruments** → **New PolicyInstrumentScheme** (~10 concepts).
   FIT, PPA, auction, subsidy, carbon tax, ETS are a distinct dimension —
   the mechanism through which energy is priced, procured, or incentivized.

2. **Market structure** → **DomainObjectScheme**. Wholesale market, spot
   market, day-ahead are venues/contexts where measurements happen, not
   policies or aggregation methods. "Day-ahead electricity prices" →
   domainObject: wholesale market, not aggregation: day-ahead.

3. **Social/governance** → **DomainObjectScheme, lower priority**. Add
   `energy access` and `energy poverty` as domain expansion concepts.
   Skip "just transition" (policy framing, not a chartable metric).

4. **Lifecycle stages** → **MeasuredPropertyScheme**. Decommissioning,
   repowering, deployment are WHAT you measure about a technology, same
   pattern as generation/capacity/demand. Also add `deployment` (additions,
   new build, commissioning) to distinguish what's BEING ADDED from what
   EXISTS (capacity).

5. **Installation types** → **Surface form enrichment on existing
   TechnologyOrFuel concepts**. "Rooftop solar" is a qualifier on SolarPV,
   not a separate concept. Add as altLabels. Avoid combinatorial explosion
   of installation-type × technology pairs. Exception: "distributed
   generation" may become a DomainObject later if corpus signal grows.

---

## Next Steps

1. User decision on scope questions above
2. Implement Tier 1 concept additions (highest corpus frequency)
3. Enrich surface forms on existing concepts (Tier 3 table)
4. Re-run corpus analysis after additions to measure coverage improvement
5. Run full 477K corpus mining for long-tail surface forms

---

## Corpus Statistics

- **Store**: energy-news-filtered (34,646 posts, 2,371 authors)
- **Sample size**: 5,000 posts
- **Top authors**: grist.org, electrek.co, canarymedia.com, cleantechnica, carbonbrief
- **Date range**: 2018-11-15 to 2026-02-28
- **Full store** (energy-news): 477,889 posts, 24,424 authors, 2008-2026
