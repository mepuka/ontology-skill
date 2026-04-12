# Validation Report: skygest-energy-vocab (SKY-309)

**Date**: 2026-04-12
**Changes**: Added MeasuredPropertyScheme (15 concepts) + DomainObjectScheme (24 concepts)
**Validator**: ontology-validator skill

## Summary

- **Overall**: PASS (with known pre-existing issues)
- **Blocking issues**: 0
- **New issues introduced by SKY-309**: 0
- **Pre-existing issues**: 7 CQ test failures (provenance A-box, SSSOM mappings)

## Level 1: Logical Consistency

- **Status**: PASS
- **Reasoner**: ELK (ROBOT 1.9.8)
- **Unsatisfiable classes**: 0
- **Turtle parse**: OK (1188 triples)
- **Duplicate prefLabels within scheme**: 0
- **Concepts in multiple schemes**: 0

## Level 2: ROBOT Report

- **Status**: PASS (0 ERRORs)
- **Errors**: 0
- **Warnings**: 4 (pre-existing: SurfaceFormEntry + 3 custom properties use skos:definition not obo:IAO_0000115)
- **Info**: 1 (pre-existing: SurfaceFormEntry has no rdfs:subClassOf)
- **Note**: 14 duplicate_label ERRORs were resolved by disambiguating rdfs:label on cross-scheme concepts (prefLabel unchanged per CD-004)

## Level 3: SHACL Validation

- **Status**: PASS (Conforms: True)
- **Shapes file**: shapes/skygest-energy-vocab-shapes.ttl

## Level 4: CQ Tests

- **Total**: 40
- **Passed**: 33
- **Failed**: 7 (all pre-existing, none caused by SKY-309)
- **New CQ tests (CQ-031 to CQ-040)**: ALL 10 PASS

### Failed tests (pre-existing)

| CQ | Reason | Upstream fix needed |
|----|--------|---------------------|
| CQ-006 | Cross-concept altLabel overlap query returns 0 (collision-free build) | Revisit CQ design |
| CQ-012, CQ-013, CQ-014 | SurfaceFormEntry A-box not yet created | Architect (CD-003) |
| CQ-019, CQ-020 | No SSSOM mappings in Turtle yet | Mapper skill |
| CQ-025 | No energy-news broadMatch mappings | Mapper skill |

## Level 5: Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| rdfs:label coverage | 100% (86/86) | 100% | PASS |
| skos:prefLabel coverage | 100% (86/86) | 100% | PASS |
| skos:definition coverage | 100% (86/86) | >= 80% | PASS |
| skos:altLabel coverage | 100% (86/86) | 100% | PASS |
| Orphan classes | 0 | 0 | PASS |
| Intra-scheme collisions | 0 | 0 | PASS |
| Build collisions | 0 | 0 | PASS |
| Total entries (JSON) | 515 | — | — |

### Per-scheme breakdown

| Scheme | Concepts | EN altLabels | DE altLabels |
|--------|----------|-------------|-------------|
| StatisticTypeScheme | 5 | 15 | 6 |
| AggregationScheme | 7 | 16 | 2 |
| UnitFamilyScheme | 8 | 25 | 0 |
| TechnologyOrFuelScheme | 21 | 311 | 14 |
| MeasuredPropertyScheme | 15 | 67 | 30 |
| DomainObjectScheme | 24 | 81 | 41 |
| FrequencyScheme | 6 | 15 | 0 |
| **Total** | **86** | **530** | **93** |

## Level 6: Evaluation Dimensions

- **Semantic**: Two new schemes add measuredProperty and domainObject dimensions, modeling the full IEA energy statistics space. Cross-scheme overlap with StatisticType and TechnologyOrFuel is documented and intentional.
- **Functional**: All 10 new CQs pass. The new schemes directly address the 37 ambiguous eval observations. Domain expansion beyond cold-start adds future-proofing.
- **Model-centric**: SKOS-centric design maintained. No new OWL axioms added. BFO alignment documented as GDC (consistent with existing pattern).
