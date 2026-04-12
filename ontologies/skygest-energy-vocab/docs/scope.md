# Skygest Energy Vocabulary — Scope

## Domain Description

A SKOS vocabulary for matching energy chart text to canonical data variables.
The Skygest platform ingests social media posts containing energy charts
(generation, capacity, prices, emissions). Stage 2 of the resolver pipeline
decomposes chart titles, axis labels, and source lines into seven-facet
Variable descriptions. This ontology provides the surface-form-to-canonical
mappings that power that decomposition.

Four of the seven facets are attacked by Stage 2's deterministic table
lookup. Each becomes a SKOS ConceptScheme whose concepts carry
`skos:altLabel` values representing the surface forms found in real chart
text (English and German). A fifth scheme (frequency) is planned for Phase 2
when Series-level FixedDims support is added.

## Intended Use Cases

- Match chart title text ("Global wind capacity additions, 2010-2024") to a
  canonical Variable by decomposing into facets (statisticType=stock,
  technologyOrFuel=wind, unitFamily=power)
- Discriminate near-synonymous Variables: "installed capacity" (stock, power)
  vs "electricity generation" (flow, energy) vs "wholesale price" (price,
  currency_per_energy)
- Provide Stage 3 (LLM lane) with visible vocabulary evidence: every surface
  form entry carries provenance and notes so the LLM can inspect what Stage 2
  knew and override it

## Data Sources

### Demand side (what we must match)

- **23 cold-start Variables** with 7-facet descriptions in
  `skygest-cloudflare/references/cold-start/variables/`
- **289 candidate posts** referencing 19 of the 23 variables
- **37-post eval snapshot** with real chart titles (English and German)
- **76 unresolved posts** (26% of candidates) that Stage 2 must handle

### Supply side (external ontologies to import from)

| Source | Format | Facets Covered | Est. Terms |
|--------|--------|---------------|------------|
| OEO v2.11.0 | RDF/XML (3.8 MB) | technologyOrFuel | 50-80 concepts |
| ENTSO-E PSRType | 25-entry enum | technologyOrFuel | 25 codes |
| Eurostat SIEC | CSV/JSON-LD, 279 concepts | technologyOrFuel | ~120 leaf products |
| QUDT v2.1 | Turtle RDF, 2300+ units | unitFamily | ~80 energy-domain units |
| UCUM | XML, 305 units | unitFamily | ~30 energy-relevant |
| ISO 4217 | CSV, ~35 active codes | unitFamily (currency) | ~35 codes |
| Wikidata | SPARQL one-shot | technologyOrFuel (synonyms) | ~50-100 items |

### Existing Skygest ontologies

- **energy-news** ontology: ~55 SKOS topic individuals with altLabels. Has
  SSSOM mappings to OEO (7 mappings) and Wikidata (12 mappings). The topic
  scheme covers broad energy categories but not the fine-grained facets
  needed for Variable decomposition.
- **energy-media** ontology: chart type scheme, media attachment classes.
  Complements but does not overlap with this vocabulary.

## In Scope

### Six Core SKOS ConceptSchemes (Variable facets)

The first four map 1:1 to Stage 2's original deterministic lookup facets.
Schemes 5-6 were added in SKY-309 to disambiguate tied Variables:

1. **StatisticTypeScheme** — 5 concepts: `stock`, `flow`, `price`, `share`,
   `count`. Surface forms map chart language to the type of quantity measured.
   Examples: "installed capacity" -> stock, "annual generation" -> flow,
   "wholesale price" -> price, "share of electricity" -> share.

2. **AggregationScheme** — 7 concepts: `point`, `end_of_period`, `sum`,
   `average`, `max`, `min`, `settlement`. Surface forms from temporal
   qualifiers in chart text. Examples: "cumulative" -> end_of_period,
   "average price" -> average, "total generation" -> sum.

3. **UnitFamilyScheme** — 8 concepts: `power`, `energy`, `currency`,
   `currency_per_energy`, `mass_co2e`, `intensity`, `dimensionless`, `other`.
   Surface forms from axis labels and unit strings. Examples: "GW" -> power,
   "TWh" -> energy, "$/MWh" -> currency_per_energy, "MtCO2e" -> mass_co2e.

4. **TechnologyOrFuelScheme** — Open-ended, ~40-60 concepts. Surface forms
   from chart titles and source lines. Examples: "solar PV" -> solar_pv,
   "CCGT" -> gas_ccgt, "offshore wind" -> offshore_wind, "lignite" ->
   brown_coal. Hierarchy follows OEO structure (energy carriers, power
   generating units) enriched with ENTSO-E, SIEC, and Wikidata synonyms.
   Unlike the other three schemes, `technologyOrFuel` is an open
   `Schema.String` in the Variable schema — this vocabulary defines the
   curated canonical list.

### Disambiguation Schemes (SKY-309, added 2026-04-12)

These two schemes address the 37 ambiguous eval observations where Variables
tied on the four core facets. They add two discriminating dimensions:

5. **MeasuredPropertyScheme** — 8 concepts: `generation`, `capacity`,
   `demand`, `emissions`, `investment`, `price`, `share`, `count`. Surface
   forms map chart language to WHAT is being measured. Examples: "generation"
   -> generation, "installed" -> capacity, "demand" -> demand, "emissions" ->
   emissions. Cross-scheme overlap with StatisticTypeScheme is intentional
   ("generation" fires both Flow and Generation).

6. **DomainObjectScheme** — 16 concepts matching cold-start Variable
   domainObject values: `electricity`, `battery storage`, `clean energy`,
   `data center`, `electrolyzer`, `energy consumption`, `energy transition`,
   `heat pump`, `interconnection queue`, `lithium-ion battery pack`,
   `nuclear reactor`, `offshore wind farm`, `offshore wind turbine`,
   `renewable power`, `solar photovoltaic`, `wind turbine`. Surface forms
   map chart language to WHAT DOMAIN OBJECT is being measured. Examples:
   "electricity" -> electricity, "battery" -> battery storage, "data center"
   -> data center.

### Phase 2 Extension Scheme (FixedDims, not Variable facet)

7. **FrequencyScheme** — 6 concepts: `hourly`, `daily`, `weekly`, `monthly`,
   `quarterly`, `annual`. Surface forms from x-axis labels and temporal
   qualifiers. Examples: "monthly data" -> monthly, "Q1 2024" -> quarterly.
   > **Note**: Frequency is not a Variable facet. It belongs to the
   > Series-level FixedDims model. This scheme is planned for Phase 2
   > when the resolver expands beyond Variable decomposition.

### Cross-ontology mappings (SSSOM)

- TechnologyOrFuelScheme concepts -> OEO IRIs via `skos:closeMatch`
- TechnologyOrFuelScheme concepts -> ENTSO-E PSRType codes via `skos:exactMatch`
- TechnologyOrFuelScheme concepts -> SIEC codes via `skos:broadMatch`
- TechnologyOrFuelScheme concepts -> Wikidata QIDs via `skos:closeMatch`
- UnitFamilyScheme concepts -> QUDT unit IRIs via `skos:closeMatch`
- UnitFamilyScheme concepts -> UCUM codes via `skos:exactMatch`

### JSON export for Skygest Stage 2

A custom `build_surface_form_json()` step in `scripts/build.py` reads the
built ontology graph and emits five JSON files matching the Skygest
`SurfaceFormEntry` schema:

```
references/vocabulary/statistic-type.json
references/vocabulary/aggregation.json
references/vocabulary/unit-family.json
references/vocabulary/technology-or-fuel.json
references/vocabulary/frequency.json          # Phase 2 — FixedDims, not Variable facet
```

Each row has: `surfaceForm`, `normalizedSurfaceForm`, `canonical`,
`provenance` (one of: `cold-start-corpus`, `hand-curated`, `oeo-derived`,
`ucum-derived`, `wikidata-derived`, `agent-curated`, `eval-feedback`),
`notes` (required when provenance is `agent-curated` or `eval-feedback`),
`addedAt`, optional `source`.

> **Note**: The `SurfaceFormProvenance` enum in `skygest-cloudflare` defines
> exactly these 7 values (SKY-305 added `wikidata-derived`). Additional
> provenance tags (e.g., `entsoe-derived`, `qudt-derived`) would require a
> code change to `src/domain/surfaceForm.ts`.

### Normalization contract

`normalizedSurfaceForm` must exactly equal
`normalizeLookupText(surfaceForm)` — i.e., Unicode NFKC normalization,
collapse whitespace, lowercase. The build script must enforce this invariant.

### Collision constraint

`buildVocabularyIndex()` raises `VocabularyCollisionError` if two different
canonical values claim the same `normalizedSurfaceForm` within a single
vocabulary file. The ontology must not produce surface forms that violate
this constraint.

## Out of Scope

- The three deferred facets (`measuredProperty`, `domainObject`, `basis`) —
  these are Stage 3 LLM concerns, not deterministic vocabulary
- Series resolution (`FixedDims`: place, sector, market) — separate slice
- Full article text or post body parsing
- Embedding-based matching (Stage 2.5, deferred per SD-Q12)
- Runtime ontology queries — the Worker consumes flat JSON, not RDF

## Constraints

- **Profile**: OWL 2 DL (primarily SKOS concept schemes with annotation properties)
- **Size**: Small (~60-80 SKOS concepts across 4 core schemes, ~400-700 altLabels; +6 frequency concepts in Phase 2)
- **Serialization**: Turtle (.ttl)
- **Upper ontology**: Minimal BFO alignment where natural (inherits from energy-news)
- **Naming**: CamelCase concepts, English labels as primary, German altLabels for energy-charts.info surface forms
- **Export constraint**: The JSON export must decode cleanly against `makeSurfaceFormEntry<Canonical>` from `skygest-cloudflare/src/domain/surfaceForm.ts`
- **H-S2-1 principle**: "Stage 2 advises, Stage 3 decides." Every surface form entry must carry enough provenance for Stage 3 to inspect and override.

## Priority Surface Forms (from demand-side analysis)

### Tier 1 — Discriminates top 10 Variables (85%+ of 289 candidates)

| Facet | Surface Forms | Canonical |
|-------|--------------|-----------|
| technologyOrFuel | solar, solar PV, PV, photovoltaic | solar_pv |
| technologyOrFuel | wind, wind power, onshore wind, Windkraft | wind |
| technologyOrFuel | battery, batteries, BESS, energy storage | battery |
| technologyOrFuel | renewable, renewables, clean energy, erneuerbare Energien | renewable |
| unitFamily | GW, MW, kW, gigawatt, megawatt | power |
| unitFamily | TWh, GWh, MWh, kWh, Wh | energy |
| unitFamily | $/MWh, EUR/MWh, ct/kWh | currency_per_energy |
| statisticType | installed, cumulative, total, nameplate | stock |
| statisticType | generation, output, Erzeugung, Stromerzeugung | flow |
| statisticType | price, cost, tariff, rate, Strompreis | price |

### Tier 2 — Remaining Variables

| Facet | Surface Forms | Canonical |
|-------|--------------|-----------|
| technologyOrFuel | nuclear, atomic, Kernkraft | nuclear |
| technologyOrFuel | coal, coal-fired, Kohle, lignite | coal |
| technologyOrFuel | offshore wind | offshore_wind |
| technologyOrFuel | heat pump, heat pumps | heat_pump |
| technologyOrFuel | hydrogen, electrolyzer, electrolysis | hydrogen |
| technologyOrFuel | natural gas, gas, CCGT, OCGT, Erdgas | natural_gas |
| unitFamily | $, USD, EUR, CAD, GBP | currency |
| unitFamily | tCO2, tCO2e, MtCO2e, gCO2/kWh | mass_co2e |
| unitFamily | %, share, proportion | dimensionless |
| statisticType | share, percentage, proportion, Anteil | share |
| aggregation | average, mean, weighted average | average |
| aggregation | cumulative, end of period, as of | end_of_period |
| aggregation | total, sum, annual total | sum |

### Tier 3 — German language (energy-charts.info posts)

| Surface Form | Canonical |
|-------------|-----------|
| Stromerzeugung, Nettostromerzeugung | flow (statisticType) |
| Stromverbrauch | flow (statisticType) — demand context |
| Kapazitat | stock (statisticType) |
| Solarenergie, Photovoltaik | solar_pv (technologyOrFuel) |
| Windenergie | wind (technologyOrFuel) |

## Key Discriminator Pairs

These are the Variable pairs that Stage 2 must distinguish. The vocabulary
must provide surface forms that resolve the ambiguity:

1. **capacity vs generation** — unitFamily (power vs energy) is the strongest signal
2. **stock vs flow** — "installed"/"cumulative" -> stock; "annual"/"monthly" output -> flow
3. **parent renewable vs child tech** — technologyOrFuel presence selects child; absence selects parent
4. **share vs absolute** — "%"/"share" -> share; absolute units -> flow/stock
5. **investment vs generation** — measuredProperty is the only discriminator (deferred to Stage 3)

## Relationship to Existing Ontologies in This Repo

This vocabulary extends the energy-news ontology's topic coverage into
fine-grained facets. Where energy-news has `enews:Solar` as a broad topic,
this vocabulary has `sevocab:solar_pv` as a `technologyOrFuel` concept with
specific surface forms for chart matching. SSSOM mappings link the two:
`sevocab:solar_pv skos:broadMatch enews:Solar`.

The energy-media ontology's `ChartTypeScheme` is complementary — it classifies
chart visual types (bar, line, area), while this vocabulary classifies chart
content (what the data represents).
