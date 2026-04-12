# Skygest Energy Vocabulary — Mapping QA Report

**Date**: 2026-04-11
**Phase**: 5 — Integration & Mapping

---

## 1. Mapping File Summary

| File | Target | Mappings | Predicates | Avg Confidence |
|------|--------|----------|------------|----------------|
| sevocab-to-oeo.sssom.tsv | OEO v2.10.0 | 11 | 11 closeMatch | 0.87 |
| sevocab-to-entsoe.sssom.tsv | ENTSO-E PSRType | 8 | 3 exactMatch, 3 broadMatch, 2 exactMatch | 0.88 |
| sevocab-to-wikidata.sssom.tsv | Wikidata | 13 | 13 closeMatch | 0.84 |
| sevocab-to-qudt.sssom.tsv | QUDT v2.1 | 4 | 3 closeMatch, 1 broadMatch | 0.79 |
| **Total** | | **36** | | **0.85** |

## 2. Predicate Distribution

| Predicate | Count | % |
|-----------|-------|---|
| skos:closeMatch | 27 | 75% |
| skos:exactMatch | 5 | 14% |
| skos:broadMatch | 4 | 11% |
| skos:narrowMatch | 0 | 0% |
| skos:relatedMatch | 0 | 0% |

**Assessment**: Healthy distribution. `closeMatch` is the default for
cross-domain mappings where ontological category differs (SKOS concept
vs OWL class). `exactMatch` reserved for ENTSO-E codes with strict 1:1
correspondence. No transitivity concerns — no exactMatch chains span
multiple mapping sets.

## 3. Confidence Distribution

| Range | Count | % |
|-------|-------|---|
| 0.90-1.00 | 11 | 31% |
| 0.80-0.89 | 17 | 47% |
| 0.70-0.79 | 6 | 17% |
| 0.60-0.69 | 2 | 6% |
| < 0.60 | 0 | 0% |

**Assessment**: No low-confidence mappings. The 2 entries at 0.65-0.70
are the MassCo2e→QUDT:Mass broadMatch (inherently imprecise) and
Renewable→ENTSO-E:B15 broadMatch (B15 is a residual category).

## 4. Source Coverage

### TechnologyOrFuelScheme (13 concepts)

| Concept | OEO | ENTSO-E | Wikidata | Total Mappings |
|---------|-----|---------|----------|----------------|
| SolarPv | yes | yes | yes | 3 |
| Wind | yes | — | yes | 2 |
| OnshoreWind | — | yes | yes | 2 |
| OffshoreWind | — | yes | yes | 2 |
| Battery | yes | — | yes | 2 |
| Renewable | yes | yes | yes | 3 |
| Nuclear | yes | yes | yes | 3 |
| Coal | yes | yes | yes | 3 |
| BrownCoal | yes | yes | yes | 3 |
| HeatPump | yes | — | yes | 2 |
| Hydrogen | yes | — | yes | 2 |
| NaturalGas | yes | yes | yes | 3 |
| GasCcgt | yes | — | yes | 2 |

**Coverage**: 13/13 (100%) — every TechnologyOrFuel concept has at least
2 external mappings.

### UnitFamilyScheme (8 concepts)

| Concept | QUDT | Mapped? |
|---------|------|---------|
| PowerUnit | yes | closeMatch |
| EnergyUnit | yes | closeMatch |
| DimensionlessUnit | yes | closeMatch |
| MassCo2eUnit | yes | broadMatch |
| CurrencyUnit | — | no (QUDT doesn't model currencies well) |
| CurrencyPerEnergyUnit | — | no (compound ratio, not a QUDT kind) |
| IntensityUnit | — | no (compound ratio) |
| OtherUnit | — | no (catch-all, unmappable) |

**Coverage**: 4/8 (50%) — expected. QUDT models physical quantities, not
compound energy-market ratios or currencies.

## 5. Clique Analysis (exactMatch transitivity)

5 `skos:exactMatch` mappings exist, all in sevocab-to-entsoe.sssom.tsv:
- OnshoreWind → B19
- OffshoreWind → B18
- Nuclear → B14
- BrownCoal → B02
- NaturalGas → B04

**No exactMatch chains cross mapping files.** No cliques larger than 2.
No transitivity concerns.

## 6. Validation Results

| Check | Result |
|-------|--------|
| sssom validate (all 4 files) | **Pass** (warnings only — unregistered source URIs) |
| CURIEs resolvable | **Pass** — all prefixes defined in curie_map |
| Self-mappings | **None** |
| Duplicate mappings | **None** |
| Missing justification | **None** — all rows have mapping_justification |
| Missing confidence | **None** — all rows have confidence scores |

## 7. Recommendations

1. **Wikidata label harvesting**: Use the 13 Wikidata mappings to SPARQL-harvest
   German labels. This is the primary enrichment path for German surface forms.
   Tag harvested labels with `provenance: "wikidata-derived"` (SKY-305).

2. **OEO label harvesting**: OEO labels are sparse (mostly bare rdfs:label).
   Low enrichment value — primarily useful for structural alignment reference.
   Tag any harvested labels with `provenance: "oeo-derived"`.

3. **ENTSO-E code as altLabel**: Add ENTSO-E PSRType codes (B16, B19, etc.)
   as altLabels on the relevant concepts for chart text that references
   ENTSO-E codes directly.

4. **Future: UCUM unit code harvesting**: UCUM codes (GW, MW, TWh, etc.) are
   already present as altLabels from cold-start corpus. A systematic UCUM
   harvest could add missed units and tag them `provenance: "ucum-derived"`.
