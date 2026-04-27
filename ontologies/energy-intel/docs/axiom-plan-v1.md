# V1 Axiom Plan — `energy-intel`

**Authored:** 2026-04-27 by `ontology-architect` (V1 iteration)
**Status:** All eight obligations (A1..A8) implemented; reasoner-clean; reports clean; pyshacl clean; pytest 19/19.
**Source:** [conceptualizer-to-architect-handoff-v1.md § 2](conceptualizer-to-architect-handoff-v1.md)
**Materialised by:** `scripts/build_modules.py` (modules), `scripts/build_shapes.py` (shapes), `scripts/build_v1_imports.py` (imports).
**KGCL log:** [`../energy-intel-changes-v1.kgcl`](../energy-intel-changes-v1.kgcl)

This document is the implementation form of the conceptualizer's eight numbered axiom obligations and five SHACL shape contracts. Each row pins to its V1 input source, the build-script function that produces the axiom, and the gate evidence file confirming HermiT / report / pyshacl conformance.

---

## 1. OWL axiom additions (A1..A8)

### A1 — Mint `ei:EnergyExpertRole`

| Aspect | Value |
|---|---|
| Module | `modules/agent.ttl` |
| Build site | `build_modules.py:build_agent()` |
| CQ source | CQ-018, CQ-019 |
| Construct | SubClassOf (simple) + SubClassOf existential restriction |
| Profile | OWL 2 DL (existential restriction is also EL-safe) |
| Reasoner pairing | HermiT (per workspace project profile) |

**Axiom:**
```turtle
ei:EnergyExpertRole a owl:Class ;
  rdfs:label "energy expert role"@en ;
  rdfs:subClassOf bfo:0000023 ;
  rdfs:subClassOf [ a owl:Restriction ;
                    owl:onProperty bfo:0000052 ;
                    owl:someValuesFrom foaf:Person ] ;
  skos:definition "..." .
```

**Evidence:** `validation/v1/reason-agent.log` (HermiT exit 0); `validation/v1/report-agent.tsv` (4 ERRORs all upstream-allow-listed); generated TTL: `modules/agent.ttl` lines 48-54.

---

### A2 — Redefine `ei:Expert` as defined equivalent class

| Aspect | Value |
|---|---|
| Module | `modules/agent.ttl` |
| Build site | `build_modules.py:build_agent()` (uses `equivalent_class_intersection_of` helper) |
| CQ source | CQ-018; revalidates V0 CQ-002, CQ-007, CQ-008, CQ-011 |
| Construct | EquivalentTo (DL); ObjectIntersectionOf (EL+); existential restriction (EL+) |
| Profile | OWL 2 DL |

**Axiom:**
```turtle
ei:Expert owl:equivalentClass [
  a owl:Class ;
  owl:intersectionOf (
    foaf:Person
    [ a owl:Restriction ;
      owl:onProperty bfo:0000053 ;
      owl:someValuesFrom ei:EnergyExpertRole ]
  )
] .
```

V0 `ei:Expert rdfs:subClassOf foaf:Person` is **dropped** — entailed by the EquivalentTo. V0 `ei:Expert owl:disjointWith ei:Organization` is **kept** as carry-forward.

**Evidence:** `validation/v1/reason-agent.log` (HermiT exit 0; reasoner classifies role-bearers as Expert); `validation/v1/pytest-cq-suite.log` confirms V0 CQ-002/007/008/011 still PASS under V1 fixtures (which now carry explicit role-bearer triples).

---

### A3 — Three-way role disjointness

| Aspect | Value |
|---|---|
| Module | `modules/agent.ttl` |
| Build site | `build_modules.py:build_agent()` (uses `disjoint_classes` helper) |
| CQ source | Defense-in-depth (anti-pattern-review-v1.md § 3) |
| Construct | DisjointClasses |
| Profile | OWL 2 DL (DisjointClasses partial-EL; safe in DL) |

**Axiom:**
```turtle
[] a owl:AllDisjointClasses ;
   owl:members ( ei:EnergyExpertRole ei:PublisherRole ei:DataProviderRole ) .
```

V0 binary `ei:PublisherRole owl:disjointWith ei:DataProviderRole` is preserved (subsumed by the V1 ternary).

**Evidence:** `validation/v1/reason-agent.log` (HermiT exit 0; no inconsistency from disjointness).

---

### A4 — Mint `ei:canonicalUnit`

| Aspect | Value |
|---|---|
| Module | `modules/measurement.ttl` |
| Build site | `build_modules.py:build_measurement()` |
| CQ source | CQ-016 (must_have); CQ-017 chains through it |
| Construct | ObjectProperty + FunctionalProperty + domain + range |
| Profile | OWL 2 DL |

**Axiom:**
```turtle
ei:canonicalUnit a owl:ObjectProperty, owl:FunctionalProperty ;
  rdfs:domain ei:CanonicalMeasurementClaim ;
  rdfs:range  qudt:Unit ;
  rdfs:label "canonical unit"@en ;
  skos:definition "..." .
```

**Evidence:** `validation/v1/reason-measurement.log` (HermiT exit 0); generated TTL contains the property at `modules/measurement.ttl`.

---

### A5 — CMC max-cardinality restriction for `ei:canonicalUnit`

| Aspect | Value |
|---|---|
| Module | `modules/measurement.ttl` |
| Build site | `build_modules.py:build_measurement()` (`subclass_qcr` helper) |
| CQ source | CQ-016 |
| Construct | Qualified max-cardinality |
| Profile | OWL 2 DL (qualified cardinality is non-EL) |

**Axiom:**
```turtle
ei:CanonicalMeasurementClaim rdfs:subClassOf [
  a owl:Restriction ;
  owl:onProperty ei:canonicalUnit ;
  owl:maxQualifiedCardinality 1 ;
  owl:onClass qudt:Unit
] .
```

The Functional characteristic on the property already implies global max-1; the qualified-cardinality restriction makes the resolution-grain invariant explicit at the CMC level (parallel to existing `referencesVariable` / `referencesSeries` patterns).

**Evidence:** `validation/v1/reason-measurement.log` (HermiT exit 0).

---

### A6 — Widen `ei:authoredBy` range (Expert -> foaf:Person)

| Aspect | Value |
|---|---|
| Module | `modules/media.ttl` (range + Post restriction) |
| Build site | `build_modules.py:build_media()` |
| CQ source | CQ-018; revalidates V0 CQ-002 |
| Construct | rdfs:range; SubClassOf qualified-cardinality restriction |
| Profile | OWL 2 DL |

**Changes:**
1. `ei:authoredBy rdfs:range foaf:Person` (was `ei:Expert`).
2. `ei:Post SubClassOf (authoredBy exactly 1 foaf:Person)` (was `exactly 1 ei:Expert`).

The Skygest-level "author must bear EnergyExpertRole" check moves from OWL to SHACL S-V1-3.

**Evidence:** `validation/v1/reason-media.log` (HermiT exit 0); V0 CQ-002 still PASS in `validation/v1/pytest-cq-suite.log`.

---

### A7 — Widen `ei:spokenBy` range (Expert -> foaf:Person)

| Aspect | Value |
|---|---|
| Module | `modules/media.ttl` |
| Build site | `build_modules.py:build_media()` |
| CQ source | CQ-011 V0 carry |
| Construct | rdfs:range |
| Profile | OWL 2 DL |

**Change:** `ei:spokenBy rdfs:range foaf:Person`. SHACL S-V1-4 (Warning) carries the role-bearer hint.

---

### A8 — Wire three new `owl:imports`

| Aspect | Value |
|---|---|
| File | `energy-intel.ttl` (top-level); `modules/measurement.ttl` (QUDT only); `catalog-v001.xml` |
| Build site | `build_modules.py:build_top_level()`; `build_modules.py:build_measurement()`; `catalog-v001.xml` hand-edited |
| CQ source | CQ-015..019 (every V1 CQ) |
| Construct | owl:imports (DL); catalog mapping |

**Imports added (top-level):**
1. `https://w3id.org/energy-intel/imports/oeo-technology-subset` -> `imports/oeo-technology-subset-fixed.ttl`
2. `https://w3id.org/energy-intel/imports/oeo-carrier-subset` -> `imports/oeo-carrier-subset-fixed.ttl`
3. `https://w3id.org/energy-intel/imports/qudt-units-subset` -> `imports/qudt-units-subset.ttl`

**Imports added (measurement):**
- `https://w3id.org/energy-intel/imports/qudt-units-subset` (the QUDT subset is needed at measurement-module merge to resolve `qudt:Unit`).

**OEO subset re-annotation:** Both V0 OEO subset files originally declared the upstream OEO root `<https://openenergyplatform.org/ontology/oeo/>` as their ontology IRI — making them indistinguishable to `owl:imports`. `scripts/build_v1_imports.py:reannotate_ontology_iri` rewrites both with project-namespaced IRIs at the end of the strip pass.

**versionIRI bump:** `ei:energy-intel owl:versionIRI <https://w3id.org/energy-intel/v1/2026-04-27>` (was `v0/2026-04-22`).

**Evidence:** `validation/v1/reason-top-level.log` (HermiT exit 0 on the full V1 closure); `imports-manifest-v1.yaml` for refresh policy.

---

### A9 — (no-op) `qudt:hasQuantityKind` reused

Action: **NONE.** Architect uses imported `qudt:hasQuantityKind` directly in the CQ-017 SPARQL chain. No local `ei:hasQuantityKind` minted.

---

## 2. SHACL shape additions (S-V1-1 .. S-V1-5)

| Shape | Target | Severity | Build site | Companion to |
|---|---|---|---|---|
| **S-V1-1** `ei:shape/CanonicalUnitInQudtSubset` | `ei:CanonicalMeasurementClaim` (path `ei:canonicalUnit`) | Violation | `build_shapes.py:main()` — sh:in over 25 unit IRIs | A4, A5 |
| **S-V1-2** `ei:shape/ResolvabilityGate` | `ei:CanonicalMeasurementClaim` (SPARQL: assertedUnit without canonicalUnit) | Warning | `build_shapes.py:main()` — sh:SPARQLConstraint, severity at NodeShape | A4 |
| **S-V1-3** `ei:shape/PostAuthorBearsEnergyExpertRole` | `ei:Post` (SPARQL: authoredBy without role-bearer triple) | Violation | `build_shapes.py:main()` | A2, A6 |
| **S-V1-4** `ei:shape/PodcastSpeakerBearsEnergyExpertRole` | `ei:PodcastSegment` (SPARQL: spokenBy without role-bearer triple) | Warning | `build_shapes.py:main()` | A2, A7 |
| **S-V1-5** `ei:shape/AboutTechnologyInRecognizedVocab` | `ei:CanonicalMeasurementClaim` (path `ei:aboutTechnology`; sh:or skos:Concept OR OEO subtree) | Violation | `build_shapes.py:main()` — SPARQL with subClassOf*/broader* walk | A8 |

All five share the new prefix-decl ontology `<https://w3id.org/energy-intel/shapes/prefix-decl-v1>` which declares `ei:`, `xsd:`, `rdf:`, `rdfs:`, `skos:`, `foaf:`, `bfo:`, `oeo:`, `qudt:`, `unit:`. The V0 prefix-decl is preserved for V0 shapes (S-1..S-3 + CQ-009 companion).

**pyshacl evidence:** `validation/v1/shacl-summary.json`. All 19 fixtures conform with 0 Violations; cq-008 has 1 Warning (S-V1-2 firing on the bare CMC, which has assertedUnit but no canonicalUnit by design).

---

## 3. V1 fixtures (cq-015..cq-019)

| Fixture | Purpose | Imports inlined | Row count contract |
|---|---|---|---|
| `tests/fixtures/cq-015.ttl` | CMC tagged with OEO energy-technology root | OEO technology subset | `ge_1` |
| `tests/fixtures/cq-016.ttl` | CMC with `ei:canonicalUnit unit:GigaW` | QUDT subset | `exactly_1` |
| `tests/fixtures/cq-017.ttl` | CMC -> ei:canonicalUnit -> qudt:hasQuantityKind chain | QUDT subset (declares hasQuantityKind on units) | `ge_1` |
| `tests/fixtures/cq-018.ttl` | Person + EnergyExpertRole + Post triangle | (none) | `exactly_1` |
| `tests/fixtures/cq-019.ttl` | Compose CQ-018 + CQ-015 | OEO technology subset | `ge_1` |

V0 fixtures were extended (additively) with explicit role-bearer triples for every author Expert. SPARQL CQ contracts unchanged — V0 SPARQL still binds `?expert a ei:Expert`. SHACL S-V1-3 now passes on V0 fixtures because role-bearer triples are explicit (pyshacl runs with `inference="rdfs"`, not OWL-DL classification, so the Expert EquivalentTo can't materialise the role triple at SHACL-time).

---

## 4. V1 ABox URI policy

V1 fixtures use the Linear D3 ABox policy:

```
https://id.skygest.io/{kind}/{ulid}
```

Examples actually shipped in V1 fixtures:
- `https://id.skygest.io/cmc/cmc_01J_example`
- `https://id.skygest.io/post/post_01J_example`
- `https://id.skygest.io/expert/did-plc-a5kyzplew76jaj4dhnqsosjv`
- `https://id.skygest.io/expert/did-plc-a5kyzplew76jaj4dhnqsosjv#energy-expert-role` (deterministic role IRI per expert)

---

## 5. Profile + reasoner pairing

- **Declared profile:** OWL 2 DL.
- **Reasoner pairing:** HermiT (workspace memory `reference_robot_dl_profile_check.md` enforces merge-then-validate-profile).
- **DL profile-validate evidence:** `validation/v1/profile-validate-dl.txt`. 41 distinct punned IRIs reported, **all upstream** (dcterms, dcat, foaf, prov, skos, oeo, IAO, RO, BFO, UO, ENVO, SWO). 0 project-namespaced punning. This matches the V0 baseline + conceptualizer's CQ-Q-3 prediction (TBox punning unchanged from V0).
- **HermiT reasoner gate:** `validation/v1/reason-top-level.log` exit 0; 0 unsatisfiable classes; reasoned closure at `validation/v1/reasoned-top-level.ttl`.

---

## 6. ROBOT report state

`validation/v1/report-top-level.tsv`: 687 ERRORs, 469 WARNs, 180 INFOs.
After the upstream-prefix allow-list filter (`scripts/apply_report_allowlist.py`):
- **Allow-listed ERRORs suppressed:** 687
- **Project-origin ERRORs:** **0**
- Filter output: `validation/v1/report-top-level-filtered.tsv`
- Project-origin error file: `validation/v1/report-project-errors.tsv` (0 rows).

V1 added 11 new allow-list rows (justified per row in `validation/report-allowlist.tsv`):
1. `duplicate_label https://w3id.org/energy-intel/concept/aggregation-type` (APOLLO_SV cross-namespace)
2. `duplicate_label http://qudt.org/vocab/quantitykind/` (upstream QUDT)
3. `multiple_labels http://qudt.org/vocab/quantitykind/` (upstream QUDT)
4. `multiple_labels http://qudt.org/vocab/unit/` (upstream QUDT multilingual)
5. `duplicate_label https://openenergyplatform.org/ontology/oeo/` (upstream OEO)
6. `multiple_labels https://openenergyplatform.org/ontology/oeo/` (upstream OEO)
7. `multiple_definitions https://openenergyplatform.org/ontology/oeo/` (upstream OEO+ENVO merge)
8. `multiple_definitions IAO:` (upstream OBO duplicate IAO_0000010 etc.)
9. `multiple_definitions UO:` (upstream UO transitively imported via OEO)
10. `missing_label rdf:` (rdf:PlainLiteral upstream W3C)
11. (Implicit) the existing concept/aggregation-type/count row stays.

---

## 7. Outputs (files modified or created)

**Build scripts (modified):**
- `scripts/build_modules.py` — A1..A8 axioms; helpers `equivalent_class_intersection_of`, `restriction_some`; QUDT namespace; V1 metadata constants.
- `scripts/build_shapes.py` — S-V1-1..S-V1-5 + new prefix-decl-v1.
- `scripts/build_fixtures.py` — V1 fixtures cq015..cq019; `_post` helper extended with role-bearer triples.
- `scripts/build_v1_imports.py` — `reannotate_ontology_iri` step appended to OEO BFO+RO strip phase.
- `scripts/run_shacl_gate.py` — Warnings counted separately; gate fails only on Violations.

**Generated artifacts (regenerated by build scripts):**
- `energy-intel.ttl` — V1 versionIRI; 3 new V1 imports.
- `modules/agent.ttl` — A1, A2, A3 applied.
- `modules/media.ttl` — A6, A7 applied; Post restriction onClass updated to foaf:Person.
- `modules/measurement.ttl` — A4, A5 applied; QUDT import added.
- `modules/data.ttl` — V1 versionInfo (no axiom changes).
- `shapes/energy-intel-shapes.ttl` — V0 + V1 shapes (4 + 5 = 9 shapes).
- `tests/fixtures/cq-001.ttl` ... `cq-014.ttl` — additively extended with role-bearer triples.
- `tests/fixtures/cq-015.ttl` ... `cq-019.ttl` — new V1 fixtures.

**Hand-edited:**
- `catalog-v001.xml` — 3 new V1 entries.
- `validation/report-allowlist.tsv` — 11 new V1 rows.
- `tests/test_ontology.py` — bands + columns extended for CQ-015..019.
- `tests/cq-test-manifest.yaml` — V1 entries flipped from `skipped` to `pass`.
- `tests/cq-016.sparql` — `unit:GW` -> `unit:GigaW` (V0 manifest IRI bug class fix).

**Documentation:**
- `docs/axiom-plan-v1.md` (this file).
- `docs/architect-build-log-v1.md`.
- `docs/architect-to-validator-handoff-v1.md`.
- `energy-intel-changes-v1.kgcl`.

**Evidence:** All raw tool outputs under `validation/v1/`.
