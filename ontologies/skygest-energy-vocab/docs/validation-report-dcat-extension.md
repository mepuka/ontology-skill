# Validation Report: DCAT Structural Extension

**Date**: 2026-04-13
**Scope**: DCAT structural extension (initial), plus SKY-316 Series spine,
plus SKY-318 Series CQs + SeriesShape validation coverage.
**Changes since 2026-04-12 baseline**:
- +1 OWL class (`sevocab:Series`)
- +3 ObjectProperties (`hasSeries`, `implementsVariable`, `publishedInDataset`)
- +2 FunctionalProperty characteristics (on `implementsVariable` and `publishedInDataset`)
- +1 owl:inverseOf axiom (hasSeries ↔ publishedInDataset)
- Series added to the existing `owl:AllDisjointClasses` axiom
- +1 SHACL NodeShape (`sevocab-shapes:SeriesShape`) enforcing minCount 1 on
  both structural links
- +6 competency questions (CQ-069 to CQ-074) + 6 SPARQL test fixtures
- +1 use case (UC-DM-007 "Validate Series chain integrity")
**Validator**: ontology-validator skill + `scripts/run_cq_tests.py` + `scripts/validate.py`

## Summary

- **Overall**: PASS
- **Blocking issues**: 0
- **New issues introduced by SKY-316 / SKY-318**: 0
- **Pre-existing failures resolved as a side effect**: 1 (CQ-064 — runner now
  loads shapes graph, so SHACL-targeting CQs can resolve their constraints)
- **Remaining pre-existing failures**: 7 (SurfaceFormEntry ABox + SSSOM mappings)

## Level 1: Logical Consistency

- **Status**: PASS (reasoned during SKY-316 formalization in commit
  `458c5e4`, re-verified via rdflib parse on 2026-04-13; no TTL changes
  since that commit)
- **Reasoner**: HermiT (ROBOT 1.9.8) — full OWL 2 DL
- **ELK**: EL profile consistent
- **Unsatisfiable classes**: 0
- **Notes**: HermiT required for qualified cardinality restrictions
  (`maxQualifiedCardinality 1` on facet dimensions). The 4-class
  `AllDisjointClasses` (EnergyVariable, EnergyDataset, EnergyAgent, Series)
  is logically consistent because Series occupies its own disjointness
  partition — nothing else in the ontology claims to be both a Series and
  one of the other three.

## Level 2: ROBOT Report

- **Status**: PASS (0 ERRORs, run during SKY-316 formalization)
- **Errors**: 0
- **Warnings**: 28 (`missing_definition` using IAO property; sevocab
  uses `skos:definition` instead — consistent authoring convention, not a
  real gap. +4 on the 2026-04-12 baseline: Series + 3 new object properties.)
- **Info**: 8 (`missing_superclass`; +1 on baseline: Series has no declared
  rdfs:subClassOf by deliberate scope cut — it is a top-level structural
  node in this slice, not a subclass of qb:Slice or dcat:DatasetSeries).

## Level 3: SHACL Validation

- **Status**: PASS (Conforms: True) — via pyshacl 2026-04-13
- **Violations**: 0
- **Total shape triples**: 509 (up from 485 at the 2026-04-12 baseline)
- **Notes**: SHACL shapes remain TBox-only; ABox validation applies when
  registry instances land (runtime-side, SKY-317 / SKY-330).

### SHACL Shapes Inventory (structural)

| Shape | Target | Constraints | Status |
|-------|--------|------------|--------|
| EnergyVariableShape | EnergyVariable | label, 7 facet dims (2 required), maxCount 1 | PASS |
| EnergyDatasetShape | EnergyDataset | title, publisher (EnergyAgent), hasVariable | PASS |
| EnergyAgentShape | EnergyAgent | label | PASS |
| SeriesShape (NEW, SKY-316) | Series | label, implementsVariable (min/max 1, class EnergyVariable), publishedInDataset (min/max 1, class EnergyDataset) | PASS |

Total NodeShapes in the shapes graph (structural + concept value
constraints): 16.

## Level 4: CQ Tests

- **Total**: 74 (+6 vs 2026-04-12 baseline)
- **Passed**: 65 (+7 — the 6 new Series CQs + CQ-064 recovered)
- **Failed**: 7 (down from 8 — all pre-existing, unrelated to SKY-316/318)
- **Skipped**: 2 (CQ-054, CQ-068 — `exactly_7` expected_result value the
  runner does not yet understand; these are pre-existing and scoped for
  a separate runner-enhancement follow-up, not part of SKY-316/318)

### New DCAT / Series CQs (CQ-054 to CQ-074): 19/21 PASS, 2 SKIP

| CQ | Result | Description |
|----|--------|-------------|
| CQ-054 | SKIP | 7 facet dimensions in DataStructureDefinition (runner lacks `exactly_7`) |
| CQ-055 | PASS | MeasuredPropertyScheme is code list for measuredProperty |
| CQ-056 | PASS | All dimensions typed as qb:DimensionProperty (0 violations) |
| CQ-057 | PASS | EnergyVariable rdfs:subClassOf schema:StatisticalVariable |
| CQ-058 | PASS | EnergyDataset has dct:publisher restriction to EnergyAgent |
| CQ-059 | PASS | hasVariable declared with domain/range |
| CQ-060 | PASS | Variable → Dataset → Agent traversal path exists |
| CQ-061 | PASS | EnergyDataset rdfs:subClassOf dcat:Dataset |
| CQ-062 | PASS | EnergyAgent rdfs:subClassOf foaf:Agent |
| CQ-063 | PASS | measuredProperty maxQualifiedCardinality 1 |
| CQ-064 | **PASS** (recovered) | 3 required facets via SHACL minCount > 0 (label, measuredProperty, statisticType) |
| CQ-065 | PASS | EnergyDataset has dcat:distribution restriction |
| CQ-066 | PASS | hasVariable domain/range correct |
| CQ-067 | PASS | Full facet → Variable → Dataset → Agent chain declared |
| CQ-068 | SKIP | DataStructureDefinition has exactly 7 components (runner lacks `exactly_7`) |
| **CQ-069** (NEW) | PASS | hasSeries declared EnergyDataset → Series |
| **CQ-070** (NEW) | PASS | implementsVariable declared as FunctionalProperty, Series → EnergyVariable |
| **CQ-071** (NEW) | PASS | All three chain properties (hasSeries, implementsVariable, hasVariable) declared for entailment-agnostic UNION query |
| **CQ-072** (NEW) | PASS | implementsVariable is FunctionalProperty but not InverseFunctionalProperty (many-Series-to-one-Variable dedup is legal and observable) |
| **CQ-073** (NEW, **must-have integrity guard**) | PASS | SeriesShape enforces sh:minCount ≥ 1 on publishedInDataset (missing-link guard behind the SKY-317 incident) |
| **CQ-074** (NEW) | PASS | Per-Agent Series + Variable chain declared via dct:publisher + hasSeries + implementsVariable |

### Pre-existing failures (unchanged — no new regressions)

| CQ | Reason | Upstream fix |
|----|--------|-------------|
| CQ-006 | Collision query returns 0 (build prevents collisions) | Revisit CQ |
| CQ-012/013/014 | SurfaceFormEntry A-box not created | Architect |
| CQ-019/020 | No SSSOM mappings in Turtle | Mapper skill |
| CQ-025 | No energy-news broadMatch mappings | Mapper skill |

## Level 5: Coverage Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total triples (TBox) | 1809 | — | — |
| Total shape triples | 509 | — | — |
| SKOS Concepts | 114 | — | — |
| **OWL Classes (sevocab, structural)** | **4** (EnergyAgent, EnergyDataset, EnergyVariable, **Series**) | — | +1 vs baseline |
| OWL Classes (sevocab, incl. SurfaceFormEntry) | 5 | — | — |
| **ObjectProperties (sevocab)** | **12** | — | +3 vs baseline (hasSeries, implementsVariable, publishedInDataset) |
| **FunctionalProperties (structural)** | **2** (implementsVariable, publishedInDataset) | — | new in SKY-316 |
| owl:inverseOf axioms (structural) | 1 (hasSeries ↔ publishedInDataset) | — | new |
| **SHACL NodeShapes (structural)** | **4** | — | +1 (SeriesShape) |
| SHACL NodeShapes (total) | 16 | — | — |
| AllDisjointClasses members | 4 | — | +1 (Series added) |
| ConceptSchemes | 8 | — | — |
| EN altLabels | 908 | — | — |
| rdfs:label coverage | 100% | 100% | PASS |
| skos:definition coverage | 100% | ≥ 80% | PASS |
| skos:prefLabel coverage | 100% | 100% | PASS |
| SHACL conformance (pyshacl) | Conforms | Conforms | PASS |
| Build collisions | 0 | 0 | PASS |
| Orphan classes | 1 (SurfaceFormEntry) | 0 | WARN (pre-existing) |

## Level 6: Evaluation Dimensions

- **Semantic**: The Series class fills the structural gap between Dataset
  and Variable cleanly. The runtime concept of a concrete published
  series now has a first-class ontological node, and the functional
  characteristics on `implementsVariable` + `publishedInDataset`
  encode exactly the runtime invariants (one Variable per Series, one
  Dataset per Series). `hasVariable` is preserved as a denormalized
  higher-level view and explicitly documented as not sufficient for
  property-chain entailment under simple SPARQL — consumers must
  traverse the explicit path.

- **Functional**: The 6 new CQs (CQ-069–074) cover: structural presence
  (CQ-069, CQ-070), entailment-agnostic chain agreement (CQ-071),
  many-to-one dedup observability (CQ-072), the must-have missing-link
  integrity guard (CQ-073), and per-Agent chain aggregation (CQ-074).
  All six pass against the TBox. UC-DM-007 hosts them.

- **Model-centric**: The Series class is deliberately distinguished from
  `dcat:DatasetSeries` (which groups editions of a dataset, not
  intra-dataset variable realizations) and from the pre-existing
  `dataset-series` family concepts used in Skygest runtime data. Both
  disambiguations live in the Series rdfs:comment and the SKY-316
  scope doc. The deliberate scope cuts (no qb:Slice subclassing, no
  Distribution→Series linkage, no fixedDims bag semantics) are
  recorded in `scope-dcat-extension.md`.

## Level 7: Impact Assessment

### JSON Build Pipeline
- **Status**: UNAFFECTED. The build script reads only SKOS altLabels;
  structural OWL triples and the new Series class are invisible to it.

### Existing CQ Tests
- **Regressions**: 0
- **Recovered failures**: 1 (CQ-064, via runner enhancement to load the
  shapes graph — this was a latent bug, not a SKY-316/318 effect)
- Pre-existing failures remain unchanged

### Runtime alignment (SKY-317 / SKY-330 handoff)
- The TTL IRIs exactly match the shape of the prepared runtime registry
  in `skygest-cloudflare/src/domain` (Series entity, `implementsVariable`
  functional semantics, `publishedInDataset` minCount-1 invariant).
- Runtime capability probes C7–C11 for these CQs are tracked on SKY-330
  (separate repo, separate branch).

### New Artifacts

| Artifact | Path |
|----------|------|
| Series class + 3 properties | `skygest-energy-vocab.ttl` |
| SeriesShape (SHACL) | `shapes/skygest-energy-vocab-shapes.ttl` |
| CQ specifications (6 new) | `docs/competency-questions-dcat-extension.yaml` |
| CQ test fixtures (6 new) | `tests/cq-069.sparql` .. `tests/cq-074.sparql` |
| Use case UC-DM-007 | `docs/use-cases-dcat-extension.yaml` |
| Traceability rows (6 new) | `docs/traceability-matrix-dcat-extension.csv` |
| CQ manifest entries (6 new) | `tests/cq-test-manifest.yaml` |
| Runner shapes-graph fix | `scripts/run_cq_tests.py` |
