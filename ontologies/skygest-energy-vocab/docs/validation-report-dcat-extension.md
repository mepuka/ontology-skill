# Validation Report: DCAT Structural Extension

**Date**: 2026-04-12
**Changes**: 3 OWL classes, 1 ObjectProperty, 7 qb:DimensionProperty,
1 DataStructureDefinition, 10 OWL restrictions, 1 disjointness axiom,
3 SHACL shapes, 4 import stubs
**Validator**: ontology-validator skill

## Summary

- **Overall**: PASS
- **Blocking issues**: 0
- **New issues introduced by extension**: 0
- **Pre-existing issues**: 7 CQ failures (provenance A-box, SSSOM mappings)

## Level 1: Logical Consistency

- **Status**: PASS
- **Reasoner**: HermiT (ROBOT 1.9.8) — full OWL 2 DL
- **Unsatisfiable classes**: 0
- **Notes**: ELK also passes. HermiT required for qualified cardinality
  restrictions (maxQualifiedCardinality 1 on facet dimensions).

## Level 2: ROBOT Report

- **Status**: PASS (0 ERRORs)
- **Errors**: 0
- **Warnings**: 24 (all `missing_definition` using IAO property; sevocab
  uses `skos:definition` instead — consistent, not a real gap)
- **Info**: 7 (`missing_superclass` on imported external classes — expected
  for minimal stubs)

## Level 3: SHACL Validation

- **Status**: PASS (Conforms: True) — with `-a` advanced mode
- **Violations**: 0
- **Notes**: Validated against existing vocabulary shapes + 3 new structural
  shapes (EnergyVariableShape, EnergyDatasetShape, EnergyAgentShape).
  SHACL shapes are TBox-only; ABox validation will apply when registry
  instances are created.

### SHACL Shapes Inventory (new structural shapes)

| Shape | Target | Constraints | Status |
|-------|--------|------------|--------|
| EnergyVariableShape | EnergyVariable | label, 7 facet dims (2 required), maxCount 1 | PASS |
| EnergyDatasetShape | EnergyDataset | title, publisher (EnergyAgent), hasVariable | PASS |
| EnergyAgentShape | EnergyAgent | label | PASS |

## Level 4: CQ Tests

- **Total**: 68
- **Passed**: 61
- **Failed**: 7 (all pre-existing)

### New DCAT CQs (CQ-054 to CQ-068): 15/15 PASS

| CQ | Result | Description |
|----|--------|-------------|
| CQ-054 | PASS | 7 facet dimensions in DataStructureDefinition |
| CQ-055 | PASS | MeasuredPropertyScheme is code list for measuredProperty |
| CQ-056 | PASS | All dimensions typed as qb:DimensionProperty (0 violations) |
| CQ-057 | PASS | EnergyVariable rdfs:subClassOf schema:StatisticalVariable |
| CQ-058 | PASS | EnergyDataset has dct:publisher restriction to EnergyAgent |
| CQ-059 | PASS | hasVariable declared with domain/range |
| CQ-060 | PASS | Variable → Dataset → Agent traversal path exists |
| CQ-061 | PASS | EnergyDataset rdfs:subClassOf dcat:Dataset |
| CQ-062 | PASS | EnergyAgent rdfs:subClassOf foaf:Agent |
| CQ-063 | PASS | measuredProperty maxQualifiedCardinality 1 |
| CQ-064 | PASS | 2 required facets (measuredProperty, statisticType) + label |
| CQ-065 | PASS | EnergyDataset has dcat:distribution restriction |
| CQ-066 | PASS | hasVariable domain/range correct |
| CQ-067 | PASS | Full facet → Variable → Dataset → Agent chain declared |
| CQ-068 | PASS | DataStructureDefinition has exactly 7 components |

### Pre-existing failures (unchanged — no regressions)

| CQ | Reason | Upstream fix |
|----|--------|-------------|
| CQ-006 | Collision query returns 0 (build prevents collisions) | Revisit CQ |
| CQ-012/013/014 | SurfaceFormEntry A-box not created | Architect |
| CQ-019/020 | No SSSOM mappings in Turtle | Mapper skill |
| CQ-025 | No energy-news broadMatch mappings | Mapper skill |

## Level 5: Coverage Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total triples | 1855 | — | — |
| SKOS Concepts | 114 | — | — |
| OWL Classes (sevocab) | 4 | — | — |
| ObjectProperties (sevocab) | 9 | — | 8 new (7 dims + hasVariable) + 1 pre-existing |
| ConceptSchemes | 8 | — | — |
| EN altLabels | 815 | — | — |
| rdfs:label coverage | 100% (118/118) | 100% | PASS |
| skos:definition coverage | 100% (118/118) | >= 80% | PASS |
| skos:prefLabel coverage | 100% (114/114) | 100% | PASS |
| SHACL conformance (adv.) | Conforms | Conforms | PASS |
| Build collisions | 0 | 0 | PASS |
| Orphan classes | 1 (SurfaceFormEntry) | 0 | WARN (pre-existing) |

## Level 6: Evaluation Dimensions

- **Semantic**: The structural extension adds a clean architectural layer
  without disturbing the existing SKOS vocabulary. The Data Cube dimensional
  model is precisely the right abstraction for facet-based variable
  composition. The DCAT chain (Agent → Dataset → Distribution → Variable)
  is standards-aligned and expressive enough for the resolution use case.

- **Functional**: All 15 Must-Have and Should-Have CQs pass. The ontology
  now formally answers structural questions that previously existed only as
  ad-hoc TypeScript logic: "what dimensions compose a Variable?", "which
  Dataset does a Variable belong to?", "who published it?". The SHACL
  shapes enforce completeness constraints (required facets) that OWL's
  open-world assumption cannot express.

- **Model-centric**: The extension follows W3C standards (DCAT 3, Data Cube,
  schema.org) rather than inventing custom structural patterns. The minimal
  import stub approach avoids transitive dependency chains while preserving
  semantic alignment. The 135 new triples in the ontology + 75 triples in
  import stubs represent a compact, focused addition.

## Level 7: Impact Assessment

### JSON Build Pipeline
- **Status**: UNAFFECTED
- Output: 800 entries across 7 JSON files, 0 collisions
- The build script reads only SKOS altLabels; structural OWL triples are
  invisible to it.

### Existing CQ Tests
- **Regressions**: 0
- 46 of 53 original CQs continue to pass (same as before extension)
- 7 original failures are pre-existing and unrelated to this extension

### New Artifacts

| Artifact | Path |
|----------|------|
| Import stubs (4) | `imports/{dcat,datacube,schema,foaf}-extract.ttl` |
| XML catalog | `catalog-v001.xml` |
| SHACL shapes (3 new) | `shapes/skygest-energy-vocab-shapes.ttl` |
| CQ tests (15 new) | `tests/cq-054.sparql` through `cq-068.sparql` |
| Build script | `scripts/add_dcat_structural_layer.py` |
| SHACL script | `scripts/add_dcat_shacl_shapes.py` |
