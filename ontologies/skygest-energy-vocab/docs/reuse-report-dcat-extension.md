# Reuse Report: DCAT Structural Extension

**Date**: 2026-04-12
**Phase**: 2 — Knowledge Acquisition
**Input**: `pre-glossary-dcat-extension.csv` (22 terms: 10 new, 12 reused)

## Baseline Reuse Decisions

| Vocabulary | Already Used by sevocab | Decision |
|------------|----------------------|----------|
| DCTerms | Yes (title, description, created, license) | Continue — add publisher |
| SKOS | Yes (entire vocabulary layer) | No change |
| OWL | Yes (Ontology declaration) | Extend usage for restrictions |
| RDFS | Yes (label, subClassOf) | Extend usage for domain/range |

## Candidate Evaluation

### 1. DCAT 3 (W3C)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Coverage | High | Dataset, Distribution, Resource — all 3 needed classes present |
| Quality | High | W3C Recommendation, stable since 2020, DCAT 3 update 2024 |
| License | CC-BY 4.0 | Compatible |
| Community | Active | W3C DXWG maintains it |
| BFO Alignment | N/A | Application ontology, BFO not applicable |
| Consistency | Consistent | No unsatisfiable classes |
| Modularization | Poor | owl:imports DCTerms + SKOS + PROV-O transitively |

**Needed terms** (6):
- `dcat:Dataset` — class
- `dcat:Distribution` — class
- `dcat:Resource` — class (parent of Dataset)
- `dcat:distribution` — property (Dataset → Distribution)
- `dcat:accessURL` — property (Distribution → URL)
- `dcat:mediaType` — property (Distribution → media type)

**Reuse strategy**: Minimal declaration stub. Full import would pull in
1695 triples plus transitive imports (DCTerms, SKOS, PROV-O). We only
need 6 terms. Create `imports/dcat-extract.ttl` with class and property
declarations only.

### 2. W3C Data Cube (qb:)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Coverage | High | DimensionProperty, codeList, DataStructureDefinition — all present |
| Quality | High | W3C Recommendation (2014), widely used in statistical data |
| License | W3C Document License | Open, compatible |
| Community | Stable | Mature standard, low change rate |
| BFO Alignment | N/A | Different domain |
| Consistency | Consistent | No unsatisfiable classes |
| Modularization | Good | No owl:imports, self-contained (265 triples) |

**Needed terms** (8):
- `qb:DimensionProperty` — class
- `qb:ComponentProperty` — class (parent of DimensionProperty)
- `qb:CodedProperty` — class (parent of DimensionProperty)
- `qb:DataStructureDefinition` — class
- `qb:ComponentSpecification` — class
- `qb:codeList` — property (DimensionProperty → code list)
- `qb:component` — property (DSD → ComponentSpecification)
- `qb:dimension` — property (ComponentSpecification → DimensionProperty)

**Reuse strategy**: Minimal declaration stub. Data Cube has no transitive
imports and is only 265 triples, but we still only need 8 terms. The
class hierarchy matters: `DimensionProperty rdfs:subClassOf ComponentProperty,
CodedProperty`. Create `imports/datacube-extract.ttl`.

### 3. schema.org

| Criterion | Score | Notes |
|-----------|-------|-------|
| Coverage | Exact | StatisticalVariable is exactly what we need |
| Quality | High | Google/W3C community standard |
| License | CC-BY-SA 3.0 | Compatible |
| Community | Active | schema.org community group |
| BFO Alignment | N/A | Different paradigm |
| Consistency | N/A | Not OWL-axiomatized |
| Modularization | N/A | Single term needed |

**Needed terms** (1):
- `schema:StatisticalVariable` — class

**Reuse strategy**: Single-term declaration stub. schema.org is 9000+
terms in a flat vocabulary. We need exactly one class. Create
`imports/schema-extract.ttl`.

**Namespace note**: schema.org officially uses `https://schema.org/` but
the workspace `namespaces.json` has `http://schema.org/`. The cloudflare
codebase uses `https://`. The extract will use `https://` (canonical) and
document this discrepancy for the architect.

### 4. FOAF

| Criterion | Score | Notes |
|-----------|-------|-------|
| Coverage | Exact | foaf:Agent is the standard agent class |
| Quality | Medium | Stable but unmaintained since 2014 |
| License | CC-BY 1.0 | Compatible |
| Community | Low | No active maintenance; but universally adopted |
| BFO Alignment | N/A | Different paradigm |
| Consistency | Consistent | 631 triples, no issues |
| Modularization | Moderate | No transitive imports |

**Needed terms** (1):
- `foaf:Agent` — class

**Reuse strategy**: Single-term declaration stub. Create
`imports/foaf-extract.ttl`.

## ODP Recommendations

### 1. N-ary Relation Pattern (Variable Composition)

The EnergyVariable is essentially an N-ary relation — a single entity
relating 7 independent dimensions. The W3C Data Cube vocabulary is itself
an instantiation of this pattern: the `qb:DataStructureDefinition` +
`qb:ComponentSpecification` structure reifies each dimension as a
component, allowing independent specification.

**Instantiation**: Use `qb:DataStructureDefinition` with 7
`qb:ComponentSpecification` instances, each pointing to a
`qb:DimensionProperty` with a `qb:codeList`.

### 2. Value Partition Pattern (Facet Dimensions)

Each facet dimension has a controlled set of valid values (a SKOS
ConceptScheme). The `qb:codeList` property implements the Value Partition
pattern: the dimension property's range is constrained to concepts within
a specific scheme.

**Instantiation**: Already modeled — each `qb:DimensionProperty` has
`qb:codeList` pointing to a sevocab ConceptScheme.

## Summary of Reuse Decisions

| Source | Terms | Strategy | Output File |
|--------|-------|----------|-------------|
| DCAT 3 | 6 | Minimal stub | `imports/dcat-extract.ttl` |
| W3C Data Cube | 8 | Minimal stub | `imports/datacube-extract.ttl` |
| schema.org | 1 | Minimal stub | `imports/schema-extract.ttl` |
| FOAF | 1 | Minimal stub | `imports/foaf-extract.ttl` |
| DCTerms | 1 (publisher) | Direct use | No import needed (already used) |

All stubs declare only the class/property type, label, and necessary
subclass relationships. No full axiom import — keeps the ontology lean
and avoids transitive import chains.

## CQ Benchmark Probes

CQ probes will be verifiable after the architect creates the structural
layer. The TBox-only SPARQL tests (CQ-054 through CQ-068) serve as the
acceptance criteria. No ABox probes needed at this phase since the
structural extension is TBox-only.
