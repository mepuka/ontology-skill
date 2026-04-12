# Ontology Requirements Specification Document (ORSD)

## Skygest Energy Vocabulary (`sevocab`)

**Version**: 0.2.0-draft
**Date**: 2026-04-11
**Status**: Draft — revised after product-code review

---

## 1. Purpose

This document specifies the requirements for the **Skygest Energy Vocabulary**
(`sevocab`), a SKOS vocabulary that maps natural-language surface forms found
in energy chart text to canonical data-variable facets. It serves as the
acceptance-criteria contract between the requirements phase and all downstream
ontology engineering phases.

## 2. Scope

### 2.1 Domain

The Skygest platform ingests social media posts containing energy charts
(generation, capacity, prices, emissions). The Stage 2 resolver pipeline
decomposes chart titles, axis labels, and source lines into seven-facet
Variable descriptions. This vocabulary provides the surface-form-to-canonical
mappings that power four of those facets via deterministic table lookup.

### 2.2 In Scope

- **Four core SKOS ConceptSchemes** (1:1 with Stage 2 Variable facets):
  StatisticType, Aggregation, UnitFamily, TechnologyOrFuel
- **One Phase 2 extension scheme**: Frequency (FixedDims, not a Variable facet)
- Surface forms as `skos:altLabel` values (English + German)
- Per-surface-form provenance tracking (6 provenance tags matching product code)
- Concept hierarchy within TechnologyOrFuelScheme (`skos:broader`)
- SSSOM cross-ontology mappings to OEO, ENTSO-E, SIEC, QUDT, UCUM,
  ISO 4217, Wikidata
- JSON export for Cloudflare Worker consumption

### 2.3 Out of Scope

- Three deferred facets: `measuredProperty`, `domainObject`, `basis`
  (Stage 3 LLM concerns)
- Series resolution (`FixedDims`: place, sector, market) — except frequency
  which is slated for Phase 2
- Full article/post body parsing
- Embedding-based matching (Stage 2.5)
- Runtime ontology queries (Worker consumes flat JSON, not RDF)

### 2.4 Constraints

| Constraint | Value |
|-----------|-------|
| OWL Profile | OWL 2 DL (primarily SKOS annotation properties) |
| Size | ~60-80 SKOS concepts across 4 core schemes, ~400-700 altLabels |
| Serialization | Turtle (.ttl) |
| Naming | CamelCase concepts, English primary labels |
| Export | JSON decoding against `makeSurfaceFormEntry<Canonical>` |
| Provenance | 6 values: `cold-start-corpus`, `hand-curated`, `oeo-derived`, `ucum-derived`, `agent-curated`, `eval-feedback` |
| Notes constraint | `notes` field required when provenance is `agent-curated` or `eval-feedback` |
| Collision constraint | No two concepts in the same scheme may share a `normalizedSurfaceForm` |
| Normalization | `normalizedSurfaceForm` must equal `normalizeLookupText(surfaceForm)` — NFKC + lowercase + collapse whitespace |
| Principle | H-S2-1: "Stage 2 advises, Stage 3 decides" |

## 3. Stakeholders

| Stakeholder | Role | Primary Concern |
|------------|------|-----------------|
| Stage 2 resolver pipeline | Consumer | Fast, accurate surface form lookup |
| Stage 3 LLM lane | Consumer | Evidence inspection, override capability |
| Vocabulary maintainer | Curator | Surface form curation, provenance tracking |
| Eval/QA engineer | Validator | Accuracy measurement, regression detection |
| Ontology engineer | Integrator | Cross-ontology alignment, interoperability |

## 4. Use Cases

Eight use cases are defined in `docs/use-cases.yaml`:

| ID | Name | Priority | Actor |
|----|------|----------|-------|
| UC-001 | Decompose chart text into canonical facets | Must Have | Stage 2 pipeline |
| UC-002 | Discriminate near-synonymous Variables | Must Have | Stage 2 pipeline |
| UC-003 | Provide evidence for Stage 3 LLM override | Must Have | Stage 3 LLM |
| UC-004 | Curate surface forms from new chart text | Should Have | Maintainer |
| UC-005 | Validate resolver accuracy against eval snapshot | Should Have | Eval engineer |
| UC-006 | Align vocabulary concepts to external standards | Should Have | Ontology engineer |
| UC-007 | Match German-language chart text | Must Have | Stage 2 pipeline |
| UC-008 | Verify vocabulary covers cold-start Variable corpus | Must Have | Ontology engineer |

## 5. Competency Questions Summary

30 competency questions are defined in `docs/competency-questions.yaml`.

### 5.1 Distribution by Priority

| Priority | Count | CQ IDs |
|----------|-------|--------|
| Must Have | 19 | CQ-001 through CQ-009, CQ-011, CQ-015, CQ-018, CQ-022 through CQ-024, CQ-026 through CQ-030 |
| Should Have | 9 | CQ-010, CQ-013, CQ-014, CQ-016, CQ-017, CQ-019, CQ-020, CQ-021 |
| Could Have | 1 | CQ-025 |
| Won't Have | 0 | — |

### 5.2 Distribution by Type

| Type | Count | CQ IDs |
|------|-------|--------|
| Enumerative | 10 | CQ-001, CQ-003, CQ-005, CQ-009, CQ-011, CQ-013, CQ-014, CQ-015, CQ-016, CQ-021 |
| Relational | 8 | CQ-002, CQ-004, CQ-006, CQ-007, CQ-008, CQ-019, CQ-020, CQ-025 |
| Constraint | 8 | CQ-022, CQ-023, CQ-024, CQ-026, CQ-027, CQ-028, CQ-029, CQ-030 |
| Quantitative | 2 | CQ-017, CQ-018 |
| Boolean | 1 | CQ-010 |

### 5.3 Distribution by Use Case

| Use Case | CQ IDs |
|----------|--------|
| UC-001 | CQ-001, CQ-002, CQ-003, CQ-004, CQ-008, CQ-009, CQ-011, CQ-022, CQ-023, CQ-026 |
| UC-002 | CQ-006, CQ-007, CQ-008, CQ-010 |
| UC-003 | CQ-012, CQ-014, CQ-024, CQ-028 |
| UC-004 | CQ-013 |
| UC-005 | CQ-015, CQ-016, CQ-017, CQ-018, CQ-029, CQ-030 |
| UC-006 | CQ-019, CQ-020, CQ-021, CQ-025 |
| UC-007 | CQ-005 |
| UC-008 | CQ-026, CQ-027, CQ-028, CQ-029, CQ-030 |

## 6. Key Design Decisions for Downstream Phases

### 6.1 Provenance Modeling (for Architect)

CQ-012 through CQ-014 and CQ-028 require per-altLabel provenance. The
product code defines exactly 6 provenance values in `SurfaceFormProvenance`:
`cold-start-corpus`, `hand-curated`, `oeo-derived`, `ucum-derived`,
`agent-curated`, `eval-feedback`.

Additional provenance tags (e.g., `entsoe-derived`, `qudt-derived`) would
require a code change to `src/domain/surfaceForm.ts` in skygest-cloudflare.

Three implementation options exist:
1. **RDF-star** — annotate `skos:altLabel` triples directly
2. **Reified SurfaceFormEntry individuals** — most SPARQL-friendly
3. **JSON-only provenance** — not queryable in RDF

Recommendation: Option 2 (SurfaceFormEntry reification) for the SPARQL test
suite to work. The CQ SPARQL drafts assume this pattern.

### 6.2 Concept Naming (for Conceptualizer)

- ConceptScheme names: `{FacetName}Scheme` (e.g., `StatisticTypeScheme`)
- Concept names: CamelCase matching the canonical value
  (e.g., `SolarPv`, `Stock`, `CurrencyPerEnergy`)
- Namespace: `sevocab: https://skygest.dev/vocab/energy/`

### 6.3 Hierarchy Depth (for Conceptualizer)

Only TechnologyOrFuelScheme has hierarchy (e.g., Wind > OnshoreWind,
OffshoreWind). Other schemes are flat. Maximum depth: 2 levels.

### 6.4 TechnologyOrFuel Canonical List (for Architect)

Unlike `statisticType`, `aggregation`, and `unitFamily` (closed TypeScript
enums), `technologyOrFuel` is `Schema.String` — this vocabulary defines
the curated canonical list. CQ-029 and CQ-030 ensure the list covers the
23 cold-start variables and all enum members respectively.

### 6.5 FrequencyScheme Deferral

Frequency is not a Variable facet — it belongs to the Series-level FixedDims
model. FrequencyScheme is included as a Phase 2 extension and should be
modeled but not prioritized for the initial release. Its 6 concepts are
Could Have, not Must Have.

### 6.6 Normalization and Collision (for Build Script)

CQ-027 is only partially testable in SPARQL (SPARQL lacks NFKC). The build
script (`scripts/build.py`) must:
1. Compute `normalizeLookupText(surfaceForm)` for every altLabel
2. Verify no two different canonical values collide on the same normalized
   form within a scheme
3. Emit the correct `normalizedSurfaceForm` in the JSON export

`test_ontology.py` should include a Python-level test for normalization
consistency.

## 7. Acceptance Criteria

The vocabulary passes the requirements phase when:

- [ ] All 19 Must-Have CQs have passing SPARQL tests
- [ ] All 4 core ConceptSchemes are populated per scope counts
- [ ] Every concept has at least one `skos:altLabel`
- [ ] Tier 1 surface forms (scope section "Priority Surface Forms") are present
- [ ] Constraint CQs (CQ-022 through CQ-024, CQ-026, CQ-028 through CQ-030) return empty result sets
- [ ] JSON export builds without error
- [ ] JSON export passes `makeSurfaceFormEntry` schema validation
- [ ] `buildVocabularyIndex()` raises no `VocabularyCollisionError`
- [ ] Cold-start variable facet values are all covered (CQ-029, CQ-030)

## 8. References

- Scope document: `docs/scope.md`
- Use cases: `docs/use-cases.yaml`
- Competency questions: `docs/competency-questions.yaml`
- Pre-glossary: `docs/pre-glossary.csv`
- Test suite: `tests/cq-*.sparql`
- Test manifest: `tests/cq-test-manifest.yaml`
- Traceability matrix: `docs/traceability-matrix.csv`
- Product code: `skygest-cloudflare/src/domain/surfaceForm.ts` (SurfaceFormEntry)
- Product code: `skygest-cloudflare/src/domain/data-layer/variable.ts` (Variable schema)
- Product code: `skygest-cloudflare/src/resolution/normalize.ts` (normalizeLookupText)
- Product code: `skygest-cloudflare/src/resolution/facetVocabulary/SurfaceFormEntry.ts` (buildVocabularyIndex)
