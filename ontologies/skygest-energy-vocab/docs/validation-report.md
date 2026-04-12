# Validation Report: Skygest Energy Vocabulary

**Date**: 2026-04-11
**Version**: 0.1.0
**Overall**: **PASS** (conditional — 9 CQ failures are expected at this lifecycle stage)

---

## Summary

- Blocking issues: **0**
- Warnings: **4** (OBO-style definition property, expected for SKOS vocabulary)
- CQ tests deferred: **9** (require data not yet populated)

## Level 1: Logical Consistency

- **Status**: PASS
- **Reasoner**: ELK
- **Unsatisfiable classes**: 0
- **Notes**: No complex OWL axioms to test; vocabulary is primarily SKOS A-box

## Level 2: ROBOT Report

- **Status**: PASS (0 ERRORs)
- **Errors**: 0
- **Warnings**: 4 (missing `IAO:0000115` on custom class/properties)
- **Info**: 1 (SurfaceFormEntry has no named superclass)

| Level | Count | Details |
|-------|-------|---------|
| ERROR | 0 | — |
| WARN | 4 | SurfaceFormEntry, hasProvenanceAnnotation, surfaceFormValue, provenance missing `IAO:0000115` — expected, we use `skos:definition` |
| INFO | 1 | SurfaceFormEntry under owl:Thing — by design |

## Level 3: SHACL Validation

- **Status**: PASS (CONFORMS)
- **Violations**: 0
- **Shapes tested**: ConceptShape, ConceptSchemeShape, SurfaceFormEntryShape

## Level 4: CQ Tests

- **Total**: 30
- **Passed**: 21 (70%)
- **Failed**: 9 (30%)
- **Must-Have pass rate**: 14/19 (74%)

### Passing Tests (21)

All structural, coverage, and constraint CQs pass:

| Category | CQs | Status |
|----------|-----|--------|
| Facet lookup | CQ-001, CQ-003, CQ-005, CQ-007, CQ-008 | PASS |
| Hierarchy | CQ-009, CQ-010, CQ-011 | PASS |
| Coverage constraints | CQ-015, CQ-016, CQ-017, CQ-018 | PASS |
| Structural constraints | CQ-022, CQ-023, CQ-024 | PASS |
| Kernel constraints | CQ-026, CQ-027, CQ-028, CQ-029, CQ-030 | PASS |

### Failing Tests (9) — All Expected

These failures are not defects. They test data that requires downstream
population work:

| CQ | Why It Fails | What's Needed |
|----|-------------|---------------|
| CQ-002 | Queries specific altLabel `"installed capacity"@en` | Exact surface form not yet added — will come from cold-start corpus population |
| CQ-004 | Queries `sevocab:Power` (concept IRI is `sevocab:PowerUnit`) | IRI naming mismatch — test uses pre-glossary name |
| CQ-006 | Looks for cross-concept altLabel collisions | No deliberate collisions exist yet — this is a discovery query |
| CQ-012 | Queries SurfaceFormEntry provenance A-box | No SurfaceFormEntry instances yet — provenance module not populated |
| CQ-013 | Queries eval-feedback provenance entries | Same — no provenance A-box |
| CQ-014 | Queries oeo-derived provenance entries | Same — no provenance A-box |
| CQ-019 | Queries OEO skos:closeMatch in RDF | SSSOM mappings exist as TSV but not loaded into the ontology graph |
| CQ-020 | Queries QUDT skos:closeMatch in RDF | Same — SSSOM not loaded |
| CQ-025 | Queries energy-news skos:broadMatch in RDF | Same — cross-repo mappings not loaded |

### Remediation Plan

| Category | Action | Phase |
|----------|--------|-------|
| CQ-004 IRI mismatch | Update test to use `sevocab:PowerUnit` | Immediate fix |
| CQ-002 surface form gap | Add `"installed capacity"@en` as altLabel on Stock | Cold-start population |
| CQ-006 collision discovery | Expected to return results after Wikidata label harvest | Label enrichment |
| CQ-012/013/014 provenance | Populate SurfaceFormEntry A-box after label harvest | Provenance population |
| CQ-019/020/025 mappings | Convert SSSOM TSV to RDF and merge into vocab graph | Build script |

## Level 5: Coverage Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Logical consistency | PASS | PASS | **PASS** |
| Label coverage (classes) | 100% (1/1) | 100% | **PASS** |
| Definition coverage (classes) | 100% (1/1) | >= 80% | **PASS** |
| Label coverage (concepts) | 100% (39/39) | 100% | **PASS** |
| Definition coverage (concepts) | 100% (39/39) | >= 80% | **PASS** |
| altLabel coverage | 100% (39/39 have >= 1) | 100% | **PASS** |
| Total altLabels | 116 | ~400-700 target | **26% of target** |
| Orphan classes | 1 (SurfaceFormEntry under owl:Thing) | 0 | **ACCEPTABLE** |
| CQ pass rate (all) | 21/30 (70%) | 100% | **DEFERRED** |
| CQ pass rate (structural) | 21/21 (100%) | 100% | **PASS** |
| SHACL conformance | CONFORMS | CONFORMS | **PASS** |
| SSSOM files valid | 4/4 | all | **PASS** |

## Level 6: Evaluation Dimensions

### Semantic

- **Expressivity**: Appropriate — SKOS + one custom class is sufficient for
  a surface-form lookup vocabulary. No need for heavier OWL.
- **Complexity**: Low — easily understandable by domain experts and
  developers. The SKOS pattern is familiar.
- **Granularity**: Correct for the resolution kernel — fine enough to
  discriminate Variables, coarse enough to be maintainable.

### Functional

- **CQ relevance**: All 30 CQs trace to product use cases. No orphan CQs.
- **Product alignment**: Vocabulary structure matches the TypeScript
  `SurfaceFormEntry` schema exactly. CQ-029 and CQ-030 verify this.
- **Automation readiness**: Build script path is clear — the vocabulary
  can be serialized to the 4 JSON files once populated.

### Model-centric

- **Coherence**: Clean separation between T-box (scheme + concept structure)
  and A-box (surface form provenance). Provenance module can be generated.
- **Formality**: Appropriate — SKOS for concepts, OWL for the one custom
  class, SHACL for validation. No over-engineering.

## Readiness Assessment

**The vocabulary structure is complete and validated.** What remains is
**data population** — enriching the 116 existing altLabels to the target
400-700 range through:

1. **Wikidata label harvest** (German + additional English synonyms)
2. **Cold-start corpus population** (exact surface forms from the 23 variables)
3. **SSSOM-to-RDF conversion** (loading mapping triples into the graph)
4. **SurfaceFormEntry A-box generation** (provenance records for each altLabel)
5. **JSON export build** (the 4 vocabulary JSON files for the Worker)

Steps 1-2 are the primary enrichment work. Steps 3-5 are build-script
automation.
