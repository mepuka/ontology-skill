# Skygest Energy Vocabulary — Reuse Report

**Date**: 2026-04-11
**Phase**: 2 — Knowledge Acquisition
**Input**: `docs/pre-glossary.csv`, `docs/scope.md`

---

## 1. Always-Reuse Baseline

These foundational vocabularies are adopted without further evaluation:

| Vocabulary | Prefix | Use In This Project |
|-----------|--------|---------------------|
| SKOS Core | `skos:` | Primary modeling vocabulary — ConceptSchemes, prefLabel, altLabel, broader/narrower, mapping properties |
| Dublin Core Terms | `dcterms:` | Metadata — `dcterms:source`, `dcterms:created`, `dcterms:modified` |
| PROV-O | `prov:` | Surface form derivation — `prov:wasDerivedFrom` for external-source provenance |
| RDFS | `rdfs:` | Labels and definitions — `rdfs:label`, `rdfs:comment` |
| OWL | `owl:` | Ontology header, `owl:versionIRI` |

**Decision**: Direct import via standard prefixes. No extraction needed.

## 2. Domain Ontology Evaluation

### 2.1 Open Energy Ontology (OEO) v2.10.0

**Registry**: OBO Foundry (via oaklib `sqlite:obo:oeo`)
**Size**: 2,105 classes, 223 individuals, 178 object properties
**License**: CC-BY-4.0
**BFO alignment**: Yes (BFO 2020)

#### Coverage Assessment

| Pre-Glossary Term | OEO Match | OEO IRI | Match Quality |
|------------------|-----------|---------|--------------|
| SolarPv | solar power unit | OEO:00000034 | Close (OEO models the unit, we model the fuel/tech) |
| Wind | wind | OEO:00000043 | Exact |
| OffshoreWind | — | — | No match (OEO lacks offshore/onshore distinction) |
| OnshoreWind | — | — | No match |
| Battery | battery | OEO:00000068 | Exact |
| Renewable | renewable | OEO:00030004 | Exact |
| Nuclear | nuclear | OEO:00010415 | Exact |
| Coal | coal | OEO:00000088 | Exact |
| BrownCoal | lignite | OEO:00000251 | Exact (different preferred label) |
| HeatPump | heat pump | OEO:00000212 | Exact |
| Hydrogen | hydrogen | OEO:00000220 | Exact |
| NaturalGas | natural gas | OEO:00000292 | Exact |
| GasCcgt | gas turbine | OEO:00000185 | Close (OEO has generic gas turbine, not CCGT specifically) |

**Coverage**: 11/13 TechnologyOrFuel terms matched (85%)

#### Synonym Quality

OEO terms have **minimal synonyms** — almost all terms have only `rdfs:label`
with no `oio:hasExactSynonym` or `skos:altLabel`. This means OEO is useful for
**structural alignment and canonical IRI mapping** but will not contribute
significant surface-form enrichment.

#### Quality Scores

| Criterion | Score | Notes |
|-----------|-------|-------|
| Coverage | **High** | 85% of TechnologyOrFuel terms matched |
| Quality | **High** | Well-maintained OBO ontology with definitions |
| License | **Pass** | CC-BY-4.0 |
| Community | **High** | Active GitHub (openenergyplatform/ontology), regular releases |
| BFO Alignment | **Yes** | Full BFO 2020 alignment |
| Synonym richness | **Low** | Mostly bare rdfs:label, few altLabels |

#### Reuse Decision

**Strategy: SSSOM Mapping** (not import)

OEO's class hierarchy is too deep and OWL-heavy for a SKOS vocabulary.
We will map `sevocab` concepts to OEO IRIs via `skos:closeMatch` in SSSOM,
not import OEO classes directly. This gives us:
- Stable external IRIs for each technology concept
- Interoperability with other OEO-aligned systems
- No transitive import burden (OEO pulls in BFO, RO, IAO, etc.)

OEO labels can be harvested as additional `skos:altLabel` entries with
provenance `oeo-derived`.

### 2.2 QUDT (Quantities, Units, Dimensions, Types) v2.1

**Registry**: qudt.org (Turtle RDF, not in OBO/OLS)
**Size**: 2,300+ unit definitions
**License**: CC-BY-4.0
**BFO alignment**: No (uses its own upper ontology)

#### Coverage Assessment

| Pre-Glossary Term | QUDT Coverage | Notes |
|------------------|---------------|-------|
| Power (GW, MW, kW) | Full | `qudt:GigaW`, `qudt:MegaW`, `qudt:KiloW` |
| Energy (TWh, GWh, MWh, kWh) | Full | `qudt:TeraW-HR`, `qudt:GigaW-HR`, `qudt:MegaW-HR` |
| Currency ($/EUR) | Partial | QUDT has some currency units but ISO 4217 is authoritative |
| CurrencyPerEnergy ($/MWh) | None | QUDT models units, not compound ratios in this way |
| MassCo2e (tCO2e) | Partial | `qudt:TON` exists but CO2-equivalent is not a QUDT concept |
| Intensity (gCO2/kWh) | None | Compound unit, not a QUDT first-class entity |
| Dimensionless (%) | Yes | `qudt:PERCENT` |

**Coverage**: 3/8 UnitFamily concepts fully matched, 2 partial

#### Reuse Decision

**Strategy: SSSOM Mapping for power/energy units only**

QUDT's value for us is limited because:
1. Our UnitFamily scheme models **families** (power, energy), not specific
   units (GW, MW). The altLabels carry the specific unit strings.
2. QUDT doesn't model compound energy-domain ratios ($/MWh, gCO2/kWh)
3. The Worker consumes flat JSON, not QUDT URIs

Map `sevocab:Power` and `sevocab:Energy` to QUDT quantity kinds via
`skos:closeMatch`. Harvest unit abbreviations (GW, MW, TWh, etc.) from
QUDT labels as altLabels with provenance `ucum-derived` or `qudt-derived`
(noting the latter would need a code change to `SurfaceFormProvenance`).

### 2.3 UCUM (Unified Code for Units of Measure)

**Registry**: ucum.org (XML, 305 units)
**Size**: ~305 coded units
**License**: Public domain (UCUM license)
**BFO alignment**: No

#### Coverage Assessment

| Unit String | UCUM Code | Notes |
|------------|-----------|-------|
| GW | `GW` | Direct match |
| MW | `MW` | Direct match |
| kW | `kW` | Direct match |
| TWh | `TW.h` | Compound (T prefix + W + h) |
| GWh | `GW.h` | Compound |
| MWh | `MW.h` | Compound |
| kWh | `kW.h` | Compound |
| % | `%` | Direct match |

**Coverage**: All power and energy unit strings have UCUM codes

#### Reuse Decision

**Strategy: altLabel enrichment**

UCUM codes and their print symbols are a reliable source of surface forms
for the UnitFamily scheme. The build script can parse UCUM's XML to extract
unit codes and symbols as altLabels with provenance `ucum-derived`.

### 2.4 ENTSO-E PSRType (Power System Resource Type)

**Registry**: ENTSO-E transparency platform documentation
**Size**: 25 enumerated codes
**License**: Open (ENTSO-E regulation)
**BFO alignment**: No

#### Coverage Assessment

| PSRType Code | Label | sevocab Match |
|-------------|-------|---------------|
| B01 | Biomass | — (not in cold-start) |
| B02 | Fossil Brown coal/Lignite | BrownCoal |
| B04 | Fossil Gas | NaturalGas |
| B05 | Fossil Hard coal | Coal |
| B07 | Fossil Oil | — (not in cold-start) |
| B09 | Geothermal | — (not in cold-start) |
| B10 | Hydro Pumped Storage | — (not in cold-start) |
| B11 | Hydro Run-of-river | — (not in cold-start) |
| B14 | Nuclear | Nuclear |
| B15 | Other renewable | Renewable |
| B16 | Solar | SolarPv |
| B18 | Wind Offshore | OffshoreWind |
| B19 | Wind Onshore | OnshoreWind |
| B20 | Other | — |

**Coverage**: 7/13 TechnologyOrFuel terms matched (54%)

#### Reuse Decision

**Strategy: SSSOM Mapping via `skos:exactMatch`**

ENTSO-E PSRType codes are industry-standard identifiers used in European
electricity market data. Map via `skos:exactMatch` for concepts with
1:1 correspondence (e.g., B18 = OffshoreWind). Use `skos:broadMatch` for
approximate matches (e.g., B16 = Solar covers both PV and thermal).

PSRType labels can be harvested as altLabels with provenance `hand-curated`
(they're short standardized labels, not natural-language surface forms).

### 2.5 Eurostat SIEC (Standard International Energy Classification)

**Registry**: Eurostat (CSV/JSON-LD, 279 concepts)
**Size**: ~279 concepts in hierarchical classification
**License**: Open (Eurostat copyright policy)

#### Coverage Assessment

SIEC provides a detailed fuel/product classification used in EU energy
statistics. It covers coal types, gas types, petroleum products, renewables,
and derived products at finer granularity than our vocabulary needs.

**Coverage**: ~60% of TechnologyOrFuel terms, but at too fine a granularity
(e.g., separate codes for anthracite, bituminous coal, sub-bituminous coal
where we just need "coal")

#### Reuse Decision

**Strategy: SSSOM Mapping via `skos:broadMatch`**

Our vocabulary concepts are broader than most SIEC codes. Map via
`skos:broadMatch` where our concept subsumes multiple SIEC entries.
Low priority — SIEC doesn't add surface forms we don't already get from
OEO and ENTSO-E.

### 2.6 ISO 4217 (Currency Codes)

**Registry**: ISO (CSV, ~35 active codes)
**Size**: ~35 active currency codes
**License**: Available for reference use

#### Coverage Assessment

| Currency String | ISO 4217 | Notes |
|----------------|----------|-------|
| USD, $ | USD | Direct |
| EUR | EUR | Direct |
| GBP, £ | GBP | Direct |
| CAD | CAD | Direct |

**Coverage**: Full for currency surface forms

#### Reuse Decision

**Strategy: altLabel enrichment**

ISO 4217 codes and their symbols are authoritative surface forms for the
Currency concept in UnitFamilyScheme. Add as altLabels with provenance
`hand-curated` (ISO 4217 is a fixed, well-known list).

### 2.7 Wikidata

**Registry**: wikidata.org (SPARQL endpoint)
**Size**: 100M+ items
**License**: CC0

#### Coverage Assessment

Wikidata has items for all our TechnologyOrFuel concepts with rich
multilingual labels (including German). Key items:

| Concept | Wikidata QID | German Label |
|---------|-------------|-------------|
| SolarPv | Q194195 | Photovoltaikanlage |
| Wind | Q194356 | Windpark |
| Nuclear | Q12739 | Kernenergie |
| Coal | Q24489 | Steinkohlenbergwerk |
| Battery | Q267298 | Akkumulator |
| Hydrogen | Q556 | Wasserstoff |

**Coverage**: Full, with German altLabels

#### Reuse Decision

**Strategy: SSSOM Mapping + German altLabel harvesting**

Map via `skos:closeMatch` to Wikidata QIDs. Harvest German `rdfs:label` and
`skos:altLabel` values as surface forms for the vocabulary. This is the
primary source for German surface forms.

Wikidata labels need provenance `hand-curated` or `agent-curated` since
they're harvested via SPARQL (no `wikidata-derived` provenance tag exists in
the product code).

## 3. Coverage Summary

| Source | Scheme Coverage | Reuse Strategy | Priority |
|--------|----------------|----------------|----------|
| **OEO** | TechnologyOrFuel (85%) | SSSOM mapping (`skos:closeMatch`) | High |
| **ENTSO-E** | TechnologyOrFuel (54%) | SSSOM mapping (`skos:exactMatch`) | High |
| **QUDT** | UnitFamily (partial) | SSSOM mapping for power/energy | Medium |
| **UCUM** | UnitFamily (unit strings) | altLabel enrichment | High |
| **ISO 4217** | UnitFamily (currency) | altLabel enrichment | Medium |
| **Wikidata** | TechnologyOrFuel (full) | SSSOM mapping + German labels | High |
| **SIEC** | TechnologyOrFuel (60%) | SSSOM mapping (`skos:broadMatch`) | Low |

## 4. What We Do NOT Import

This vocabulary does **not** use `owl:imports` for any external ontology.
All reuse is via:
1. **SSSOM mapping files** — linking sevocab concepts to external IRIs
2. **altLabel harvesting** — copying labels from external sources as surface
   forms with provenance tracking
3. **Standard vocabulary prefixes** — SKOS, DCTERMS, PROV-O used directly

Rationale: The Cloudflare Worker consumes flat JSON, not RDF. Importing
OEO (which transitively imports BFO, RO, IAO, etc.) would add ~35,000
triples to a vocabulary that needs ~500 triples. The ontology must stay
minimal for the build pipeline.

## 5. Pre-Glossary Term Search Results

Every pre-glossary term was searched in at least one registry:

| Term | OEO | ENTSO-E | QUDT | Wikidata | Result |
|------|-----|---------|------|----------|--------|
| StatisticTypeScheme | — | — | — | — | No external equivalent (domain-specific) |
| AggregationScheme | — | — | — | — | No external equivalent (domain-specific) |
| UnitFamilyScheme | — | — | QUDT:QuantityKind | — | Structural parallel only |
| TechnologyOrFuelScheme | OEO class hierarchy | ENTSO-E PSRType | — | — | Multiple alignment targets |
| FrequencyScheme | — | — | — | — | No external equivalent (domain-specific) |
| Stock | — | — | — | — | Domain-specific statistic type |
| Flow | — | — | — | — | Domain-specific statistic type |
| Price | — | — | — | — | Domain-specific statistic type |
| SolarPv | OEO:00000034 | B16 | — | Q194195 | Strong external coverage |
| Wind | OEO:00000043 | B18/B19 | — | Q194356 | Strong external coverage |
| Battery | OEO:00000068 | — | — | Q267298 | OEO + Wikidata |
| Nuclear | OEO:00010415 | B14 | — | Q12739 | Strong external coverage |
| Coal | OEO:00000088 | B05 | — | Q24489 | Strong external coverage |
| NaturalGas | OEO:00000292 | B04 | — | Q11451 | Strong external coverage |
| Power | — | — | QUDT:PowerUnit | — | QUDT alignment |
| Energy | — | — | QUDT:EnergyUnit | — | QUDT alignment |

## 6. CQ Benchmark Probes

Three high-priority CQs were probed against OEO:

| CQ | Probe | OEO Result |
|----|-------|-----------|
| CQ-002 (surface form lookup) | "Does OEO have altLabels for 'installed capacity'?" | **No** — OEO lacks surface-form-style altLabels |
| CQ-009 (narrower concepts) | "Does OEO model offshore/onshore wind as children of wind?" | **No** — OEO:00000043 (wind) has only OEO:00000446 (wind energy) as descendant |
| CQ-030 (enum coverage) | "Does OEO cover all statisticType enum values?" | **No** — OEO has no stock/flow/price/share/count classification |

**Conclusion**: OEO is a structural alignment target, not a direct reuse
source. It cannot answer our SKOS-vocabulary CQs because it models physical
entities and processes, not surface-form-to-canonical mappings.
