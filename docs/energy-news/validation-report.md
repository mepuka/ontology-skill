# Validation Report: Energy News Ontology

Date: 2026-02-11
Ontology: `ontologies/energy-news/energy-news.ttl`
Version: 0.1.0
Validator: ontology-validator skill (Phase 5/6)

## Summary

- **Overall: PASS**
- Blocking issues: 0
- Warnings: 0
- Observations: 0

## Level 1: Logical Consistency

- **Status: PASS**
- Reasoner: HermiT (OWL 2 DL, complete)
- Consistency: PASS
- Unsatisfiable classes: 0
- Command: `robot reason --reasoner HermiT --input energy-news-merged.ttl`

No logical contradictions detected. The ontology is consistent under full
DL reasoning.

## Level 2: ROBOT Report

- **Status: PASS**
- Profile: custom (`ontologies/energy-news/robot-report-profile.txt`)
- Errors: 0
- Warnings: 0
- Info: 0

The custom `robot-missing-skos-definition` query filters by project namespace,
so external terms (schema.org, SIOC, SKOS, BFO) are excluded from checks.

## Level 3: SHACL Validation

- **Status: PASS**
- Shapes file: `ontologies/energy-news/shapes/energy-news-shapes.ttl`
- Conforms: true
- Violations: 0
- Warnings: 0

Shapes validated:
- `EnergyTopicInstanceShape`: rdfs:label min 1, skos:definition min 1, skos:inScheme min 1
- `ArticleShape`: coversTopic min 1, url exactly 1, publishedBy max 1, title max 1,
  publishedDate max 1, description max 1
- `PostShape`: postedBy exactly 1, sharesArticle max 1
- `AuthorAccountShape`: handle exactly 1
- `PublicationShape`: siteDomain exactly 1

## Level 4: CQ Tests

- **Status: PASS**
- Test runner: pytest (`tests/unit/test_energy_news_ontology.py`)
- Total tests: 85
- Passed: 85
- Failed: 0

### CQ Test Breakdown

| Category | Count | Passed | Notes |
|----------|-------|--------|-------|
| CQ tests (TBox-only: cq-001, cq-002, cq-010) | 3 | 3 | Enumerative + ASK queries |
| CQ tests (ABox-dependent: cq-003 through cq-016) | 13 | 13 | Require sample data |
| TBox structure (tbox-001, tbox-002, tbox-003) | 3 | 3 | Class declaration checks |
| Non-entailment (neg-001, neg-002) | 2 | 2 | Solar not broader Fossil; Nuclear not under Renewable |
| Structural tests (classes, properties, axioms) | 30+ | 30+ | owl:Class declarations, functional properties, HasKey, etc. |
| SHACL conformance (in-process) | 1 | 1 | pyshacl validate |
| SPARQL CQ tests (rdflib) | 21 | 21 | All manifest queries |

### ROBOT verify Constraint Queries

6 constraint queries are available for ROBOT verify (zero-result = pass):

| Query | Checks | Status |
|-------|--------|--------|
| `verify-missing-label.sparql` | All domain classes have rdfs:label | PASS |
| `verify-missing-definition.sparql` | All domain classes have skos:definition | PASS |
| `verify-missing-parent.sparql` | All domain classes have named parent | PASS |
| `verify-missing-domain-range.sparql` | All properties have domain + range | PASS |
| `verify-topic-completeness.sparql` | All topics have label, definition, scheme | PASS |
| `verify-class-individual-mixing.sparql` | No class/individual confusion | PASS |

For enumerative CQ tests (expecting non-empty results) and ASK queries, the
pytest harness is the authoritative test runner.

## Level 5: Metrics

### Coverage Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Class label coverage | 8/8 = 100% | 100% | PASS |
| Class definition coverage | 8/8 = 100% | >= 80% | PASS |
| Property label coverage | 13/13 = 100% | 100% | PASS |
| Property definition coverage | 13/13 = 100% | >= 80% | PASS |
| Topic label coverage | 66/66 = 100% | 100% | PASS |
| Topic definition coverage | 66/66 = 100% | >= 80% | PASS |
| Topic in-scheme coverage | 66/66 = 100% | 100% | PASS |
| Orphan classes | 0 | 0 | PASS |
| Disjointness coverage | 8/8 = 100% | 100% | PASS |
| Singleton hierarchies | 0 | 0 | PASS |
| Domain/range completeness | 13/13 = 100% | 100% | PASS |
| Duplicate labels | 0 | 0 | PASS |
| Class/individual mixing | 0 | 0 | PASS |
| Individuals in TBox | 0 | 0 | PASS |
| CQ test pass rate (Must-Have) | 100% | 100% | PASS |
| SHACL conformance | true | true | PASS |

### Orphan Classes — Resolved

All 8 domain classes now have named `rdfs:subClassOf` parents via BFO
MIREOT-style alignment (`imports/bfo-declarations.ttl`):

| Class | BFO Parent | Schema.org Parent |
|-------|-----------|-------------------|
| EnergyTopic | BFO:0000031 (GDC) | — |
| Article | BFO:0000031 (GDC) | schema:NewsArticle |
| Post | BFO:0000031 (GDC) | schema:SocialMediaPosting (equiv) |
| AuthorAccount | BFO:0000031 (GDC) | sioc:UserAccount (equiv) |
| Feed | BFO:0000031 (GDC) | — |
| Publication | BFO:0000030 (Object) | schema:NewsMediaOrganization |
| Organization | BFO:0000030 (Object) | schema:Organization (equiv) |
| GeographicEntity | BFO:0000029 (Site) | schema:Place |

ROBOT verify `verify-missing-parent.sparql` confirms 0 orphan classes.

### Ontology Size

| Metric | Value |
|--------|-------|
| Domain classes | 8 |
| Object properties | 7 |
| Data properties | 6 |
| EnergyTopic individuals | 66 |
| AllDisjointClasses axioms | 1 (covering all 8 classes) |
| AllDifferent axioms | 16 (sibling topic groups) |
| HasKey axioms | 3 (Article, AuthorAccount, Publication) |
| Functional properties | 9 |
| TBox triples | 170 |
| Reference individuals triples | 740 |
| Total triples (merged) | 910+ |

### Naming Convention Compliance

| Check | Status |
|-------|--------|
| Class names CamelCase | PASS (8/8) |
| Property names camelCase | PASS (13/13) |
| Labels lowercase | PASS (8/8) |
| Definitions genus-differentia | PASS (8/8) |
| Labels have `@en` tag | PASS (8/8) |
| Definitions have `@en` tag | PASS (8/8) |

## Level 6: Evaluation Dimensions

### Semantic

- **Expressivity**: OWL 2 DL (full). Uses existential restrictions,
  functional properties, HasKey, AllDisjointClasses, equivalentClass,
  equivalentProperty, subPropertyOf. No qualified cardinality, role chains,
  or class complements. ELK-compatible for development; HermiT for release.
- **Complexity**: Low-moderate. 8 classes with clear separation of concerns.
  Conceptual model is accessible to domain experts.
- **Granularity**: Appropriate for scope. 66 energy topics provide
  fine-grained coverage. 8 core classes capture the article-topic-author
  domain without over-modeling.
- **Epistemological adequacy**: Definitions follow BFO categories
  (GenericallyDependentContinuant for information entities, Object for
  physical/institutional entities, Site for geographic). Topic vocabulary
  covers renewable, fossil, nuclear, grid, policy, finance, climate,
  workforce, and emerging technology domains.

### Functional

- **CQ relevance**: All 16 competency questions are answerable. 3 are
  TBox-only (answerable without instance data), 13 require ABox population.
- **Rigor**: Every CQ has a formalized SPARQL test with expected results.
  Non-entailment tests verify correct classification boundaries.
- **Traceability**: Full chain from stakeholder needs through use cases,
  CQs, ontology terms, to SPARQL tests documented in
  `docs/energy-news/traceability-matrix.csv`.
- **Automation**: pytest test suite runs in < 1 second. ROBOT pipeline
  (merge + reason + report) runs in ~15 seconds.

### Model-centric

- **Authoritativeness**: Aligned to schema.org (6 classes, 10 properties)
  and SIOC (1 class). Uses SKOS for topic vocabulary. Definitions cite
  BFO categories.
- **Structural coherence**: Single inheritance in asserted hierarchy.
  Clean T-box/A-box separation (reference individuals in separate file).
  Disjointness declared for all 8 domain classes. HasKey axioms for
  identity-bearing classes.
- **Formality level**: Semi-formal to formal. OWL 2 DL with SHACL
  structural constraints. SKOS vocabulary for controlled topic terms.
  Schema.org alignment for web interoperability.

## Level 7: Diff Review

- **Status: N/A** (first version)
- No prior version exists for comparison.
- `robot diff` will be used starting from version 0.2.0.

## Anti-Pattern Detection

All 16 anti-patterns from `_shared/anti-patterns.md` were checked:

| # | Anti-Pattern | Status | Notes |
|---|-------------|--------|-------|
| 1 | Singleton hierarchy | PASS | 0 found |
| 2 | Role-type confusion | PASS | No role patterns in domain |
| 3 | Process-object confusion | PASS | All classes correctly categorized per BFO |
| 4 | Missing disjointness | PASS | AllDisjointClasses covers all 8 |
| 5 | Circular definition | PASS | No EquivalentTo chains |
| 6 | Quality-as-class | N/A | No quality values in domain |
| 7 | Information-physical conflation | PASS | Article/Post are GDC; Organization/Publication are Objects |
| 8 | Orphan class | PASS | 0 (all classes have BFO parent) |
| 9 | Polysemy | PASS | No overloaded terms |
| 10 | Domain/range overcommitment | PASS | All domain/range appropriate and complete |
| 11 | Individuals in TBox | PASS | 0 in TBox; 66 in separate reference file |
| 12 | Negative universals | PASS | No complement classes used |
| 13 | False is-a (OO inheritance) | PASS | Domain-grounded hierarchy |
| 14 | System blueprint | PASS | Domain model, not system artifacts |
| 15 | Technical perspective | PASS | CQ-driven design |
| 16 | Class/individual mixing | PASS | 0 found |

## Resolved Recommendations

All 4 recommendations from the initial validation pass have been implemented:

1. **Filter external terms from ROBOT report** — DONE. Namespace filter added
   to `sparql/robot-missing-skos-definition.rq`. ROBOT report now shows 0 warnings.

2. **BFO alignment** — DONE. MIREOT-style declarations in
   `imports/bfo-declarations.ttl` (3 BFO classes: Site, Object, GDC). All 8
   domain classes have explicit `rdfs:subClassOf` to BFO categories. Zero
   orphan classes.

3. **ROBOT verify constraint queries** — DONE. 6 constraint queries in
   `tests/energy-news/verify-*.sparql`. All pass with zero violations.

4. **Metadata completeness** — DONE. `dcterms:modified` added to all 3
   ontology headers (TBox, reference individuals, data).

### For Next Version (0.2.0)

- Add `owl:priorVersion` when releasing 0.2.0
- Consider importing full BFO if downstream consumers expect it
- Add population completeness checks once production ABox data exists

## Handoff Checklist

- [x] All Level 1-6 checks have been executed
- [x] Validation report is generated and accessible
- [x] Level 7 (diff) documented as N/A for first version
- [x] No blocking failures detected
- [x] Observations and recommendations documented with rationale
- [x] Anti-pattern detection complete (16/16 checked)
- [x] Coverage metrics computed and documented
- [x] Naming convention compliance verified
- [x] Recommendations reference appropriate upstream actions
