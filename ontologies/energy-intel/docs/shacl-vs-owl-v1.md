# SHACL vs OWL Intent — `energy-intel`, V1 Delta

**Authored:** 2026-04-27 by `ontology-conceptualizer` (V1 iteration)
**Predecessor:** [shacl-vs-owl.md](shacl-vs-owl.md) (V0; commit `36d1952`)
**Consumer:** `ontology-architect` (writes OWL axioms AND drafts SHACL shapes for V1; build-time SHACL is in scope per V0 carry-forward).

**Decision framework** (unchanged from V0; from `_shared/closure-and-open-world.md` + `_shared/anti-patterns.md` § 10):
- **OWL** = ontological truth that SHOULD drive classification / inference.
- **SHACL** = validation constraint that SHOULD NOT drive classification.

This document is a **delta** to V0 shacl-vs-owl.md. V0 constraints O-1..O-10 and S-1..S-10 remain in force unchanged. V1 adds new constraints below.

---

## 0. V1 additions summary

| New OWL constraint | New SHACL shape | Trigger CQ |
|---|---|---|
| O-V1-1 — `ei:Expert ≡ foaf:Person ⊓ ∃bfo:0000053.ei:EnergyExpertRole` | — | CQ-018 |
| O-V1-2 — `ei:EnergyExpertRole ⊑ ∃bfo:0000052.foaf:Person` | — | CQ-018 |
| O-V1-3 — `ei:CMC ⊑ ei:canonicalUnit max 1 qudt:Unit` | — | CQ-016 |
| O-V1-4 — `AllDisjointClasses(EnergyExpertRole, PublisherRole, DataProviderRole)` | — | (defense-in-depth; not directly CQ-tested) |
| O-V1-5 — `ei:authoredBy rdfs:range foaf:Person` (V0 was `ei:Expert`) | — | CQ-018; CQ-002 V0 carry |
| O-V1-6 — `ei:spokenBy rdfs:range foaf:Person` | — | CQ-011 V0 carry |
| — | S-V1-1 — `ei:canonicalUnit` value MUST be in QUDT-subset frozen list | CQ-016 |
| — | S-V1-2 — if `ei:assertedUnit` present, `ei:canonicalUnit` SHOULD be present (severity Warning) | UC-007 resolvability gate |
| — | S-V1-3 — `ei:Post.authoredBy` value MUST `bfo:0000053 some ei:EnergyExpertRole` | CQ-018 + scope-v1.md § In-scope |
| — | S-V1-4 — `ei:PodcastSegment.spokenBy` value SHOULD `bfo:0000053 some ei:EnergyExpertRole` (severity Warning) | optional; defense-in-depth on podcast layer |
| — | S-V1-5 — `ei:aboutTechnology` value MUST be `skos:Concept` (after punning) OR appear in the imported OEO subset | CQ-015 |

Six new OWL constraints. Five new SHACL shapes. V1 boundary cases discussed in § 3.

---

## 1. V1 OWL-only constraints (extend V0 § 1)

| # | Constraint | Axiom form | Why OWL |
|---|---|---|---|
| **O-V1-1** | `ei:Expert` is the kind defined as Person + role-bearer | `ei:Expert owl:equivalentClass [ owl:intersectionOf ( foaf:Person [ a owl:Restriction ; owl:onProperty bfo:0000053 ; owl:someValuesFrom ei:EnergyExpertRole ] ) ]` | Definitional. Identifies the kind by its bearer + role profile. The reasoner classifies role-bearers as Experts (V0 CQ revalidation guarantee). |
| **O-V1-2** | EnergyExpertRole inheres in Person | `ei:EnergyExpertRole rdfs:subClassOf [ a owl:Restriction ; owl:onProperty bfo:0000052 ; owl:someValuesFrom foaf:Person ]` | BFO axiomatisation: a Role with no bearer cannot exist (BFO 2020 invariant). Mirrors V0 O-7 for PublisherRole/DataProviderRole. |
| **O-V1-3** | CMC has at most one canonical unit | `ei:CanonicalMeasurementClaim rdfs:subClassOf [ a owl:Restriction ; owl:onProperty ei:canonicalUnit ; owl:maxCardinality 1 ; owl:onClass qudt:Unit ]` | Definitional — resolution-grain invariant. A single CMC cannot canonicalize to two distinct units. Functional characteristic on the property gives the reasoner a second reason to fuse `owl:sameAs`-equivalent values. |
| **O-V1-4** | Three-way role disjointness | `AllDisjointClasses(ei:EnergyExpertRole, ei:PublisherRole, ei:DataProviderRole)` | Ontological — Expert/Publisher/DataProvider roles are categorically different role-kinds with different bearer classes. |
| **O-V1-5** | `ei:authoredBy` ranges over Person | `ei:authoredBy rdfs:range foaf:Person` (replaces V0 `range ei:Expert`) | Inference: any `ei:authoredBy` arrow classifies its target as `foaf:Person`. The role-bearing is then either entailed (via the V0 fixture asserting `?p a ei:Expert`) or explicitly added (V1 fixtures). |
| **O-V1-6** | `ei:spokenBy` ranges over Person | `ei:spokenBy rdfs:range foaf:Person` (replaces V0 `range ei:Expert`) | Symmetric to O-V1-5 for podcast segments. |

All six are ontological claims that drive classification and inference. None should be relegated to SHACL.

### Closure / OWA notes for the V1 OWL constraints

- **O-V1-1 (Expert EquivalentTo).** OWA-friendly: a Person without an asserted role is not classified as Expert (correct — they may not be an energy expert).
- **O-V1-2 (Role inheres in Person).** Existential restriction. Under OWA, an EnergyExpertRole individual must be related to *some* Person. If none exists in the ABox, the reasoner attempts to construct one (anonymous individual). This is BFO-correct: a role logically requires a bearer. SHACL closed-world check S-V1-3 catches the runtime case.
- **O-V1-3 (CMC max 1 canonicalUnit).** Qualified max-cardinality. OWA-friendly: a CMC with 0 canonical units is not violating; a CMC with 2 canonical units triggers reasoner-side `owl:sameAs` fusion (or inconsistency if explicit `owl:differentFrom`).
- **O-V1-4 (three-way disjointness).** Classical: a Role individual cannot belong to two of the three role-classes simultaneously.

---

## 2. V1 SHACL-only constraints (extend V0 § 2)

| # | Constraint | SHACL shape sketch | Why SHACL (not OWL) |
|---|---|---|---|
| **S-V1-1** | `ei:canonicalUnit` value MUST be one of the imported QUDT 2.1 units | `sh:targetClass ei:CanonicalMeasurementClaim ; sh:property [ sh:path ei:canonicalUnit ; sh:nodeKind sh:IRI ; sh:in ( unit:GigaW unit:MegaW unit:TeraW unit:KiloW unit:W unit:TeraW-HR unit:GigaW-HR unit:MegaW-HR unit:KiloW-HR unit:PetaJ unit:TeraJ unit:GigaJ unit:J unit:BTU_IT unit:TON_Metric unit:KiloGM unit:GM unit:BBL unit:BBL_UK_PET unit:KiloGM-PER-J unit:HZ unit:V unit:A unit:PERCENT unit:KiloMOL ) ]` | Closed-world enumeration of the 25 imported units. OWL `oneOf` is awkward over imported individuals and risks unintended inference. SHACL `sh:in` is the canonical fit. |
| **S-V1-2** | Resolvability-gate hint: if `ei:assertedUnit` present, `ei:canonicalUnit` SHOULD be populated | `sh:targetClass ei:CanonicalMeasurementClaim ; sh:sparql [ sh:select "SELECT $this WHERE { $this ei:assertedUnit ?au . FILTER NOT EXISTS { $this ei:canonicalUnit ?cu . } }" ; sh:severity sh:Warning ]` | Soft constraint — does not block ingest. Drives the LLM resolvability stage. OWL cannot express "if A then B" SHOULD; SHACL severity gives the right control. |
| **S-V1-3** | `ei:Post.authoredBy` value MUST bear an `ei:EnergyExpertRole` | `sh:targetClass ei:Post ; sh:property [ sh:path ei:authoredBy ; sh:qualifiedValueShape [ sh:property [ sh:path bfo:0000053 ; sh:qualifiedValueShape [ sh:class ei:EnergyExpertRole ] ; sh:qualifiedMinCount 1 ] ] ; sh:qualifiedMinCount 1 ]` | Defense-in-depth on the V1 Expert refactor. OWL's `Post SubClassOf authoredBy exactly 1 foaf:Person` is the broad ontological claim; SHACL adds the role-bearer check at runtime. Without SHACL, a Person who happens not to bear EnergyExpertRole could be a Post author at the OWL level — this is by design (the OWL-side is broader; the SHACL-side is the validation layer that says "for Skygest's purposes, the Person must be an EnergyExpertRole bearer"). |
| **S-V1-4** | `ei:PodcastSegment.spokenBy` value SHOULD bear an `ei:EnergyExpertRole` | similar SHACL shape; `sh:severity sh:Warning` | Optional symmetric check. PodcastSegment may be from a non-expert speaker (e.g., a host without expert role), so this is a Warning, not a Violation. |
| **S-V1-5** | `ei:aboutTechnology` values MUST be either a `skos:Concept` (V0 hand-seeded scheme) OR an imported OEO class | `sh:targetClass ei:CanonicalMeasurementClaim ; sh:property [ sh:path ei:aboutTechnology ; sh:nodeKind sh:IRI ; sh:or ( [ sh:class skos:Concept ] [ sh:sparql [ sh:select "SELECT $this WHERE { $value rdfs:subClassOf* oeo:OEO_00020267 } UNION { $value rdfs:subClassOf* oeo:OEO_00000011 } UNION { $value rdfs:subClassOf* oeo:OEO_00020039 }" ] ] ) ]` | Closed-world membership check. The V0 hand-seeded SKOS scheme is one allowed source; the V1 OEO subsets are the other. SHACL is the right place because OWL `oneOf` over imported class IRIs is awkward and the punning view (OEO IRIs as `skos:Concept` instances) is asserted at fixture-write time, not at OWL-ontology-load time. |

All five SHACL shapes are runtime / build-time integrity checks. They live in `ontologies/energy-intel/shapes/energy-intel-shapes.ttl` (architect appends to V0 file) or a V1 sibling shape file.

### Closure / OWA notes for the V1 SHACL shapes

- **S-V1-1.** Closed-world enumeration. Any unit IRI not in the 25 listed triggers a violation. This is the guardrail against fixtures that mistakenly use `unit:GW` (the wrong V0 IRI) or `unit:CentigramPerSquareMeter` (a unit not in the V1 subset).
- **S-V1-2.** Closed-world existence check. The V0 anti-pattern review § Pattern 8 (Orphan class) reasoning applies: SHACL-based "presence required given another property is present" is the canonical SPARQL constraint shape.
- **S-V1-3.** Closed-world classification check. The OWL side is intentionally broad (range = Person); SHACL closes the loop for runtime ABox conformance.
- **S-V1-5.** Closed-world membership-in-recognized-set. Same shape as S-V1-1 but for technology concepts.

---

## 3. V1 boundary cases discussed

### 3.1 Why is `ei:Expert` defined in OWL (not SHACL-validated)?

The Expert refactor (CQ-Q-1, [conceptual-model-v1.md § 2](conceptual-model-v1.md)) keeps `ei:Expert` as a defined class (EquivalentTo), which is OWL-only — SHACL has no equivalent of `owl:equivalentClass` (it only validates instances against shapes; it does not define classes).

The reason `ei:Expert` belongs in OWL:
- Reasoners need to classify role-bearers as Expert instances (V0 CQ revalidation).
- The class identifies a meaningful kind (Person + role-bearer); SHACL-side validation cannot create class membership at the reasoner level.
- The shape `S-V1-3` (Post author MUST bear EnergyExpertRole) is the SHACL companion that locks runtime conformance, but the *kind* itself lives in OWL.

### 3.2 Why is `S-V1-3` (Post author bears EnergyExpertRole) in SHACL, not OWL?

The OWL-side could express this with:
```
ei:Post rdfs:subClassOf
  [ a owl:Restriction ;
    owl:onProperty ei:authoredBy ;
    owl:someValuesFrom ei:Expert ] .
```

But this would over-constrain at the OWL level. Under OWA, a Post with `ei:authoredBy ?p` where `?p a foaf:Person` (no role asserted) would either:
- (a) be HermiT-classified as having an Expert author *anonymously* (the reasoner constructs an anonymous Expert, which is unhelpful and noisy), OR
- (b) the Post becomes unsatisfiable if HermiT is forced to satisfy the existential and cannot find a bearer.

Neither is what we want. The correct semantics is: at the *runtime* layer, all Skygest Posts MUST have authors who bear the role; at the *ontology* layer, the broader `range foaf:Person` is the ontological truth. SHACL S-V1-3 is the runtime gate.

### 3.3 Why is `S-V1-1` (canonical unit value MUST be in QUDT subset) in SHACL, not OWL?

- OWL `oneOf` over imported individuals would freeze the QUDT subset into the V1 ontology. When V1.1 expands the QUDT subset (e.g., adds `unit:CentigramPerSquareMeter`), every fixture would need the OWL ontology version to match.
- SHACL `sh:in` is a separable validation file. The QUDT subset can grow without re-rev'ing the OWL ontology.
- SHACL also catches typos earlier — `ei:canonicalUnit unit:GW` (wrong V0 IRI) fails SHACL with a clean error message; OWL would either silently accept or report a confusing "individual not in oneOf" violation.

### 3.4 CQ-009 evidence invariant (V0 carry-forward) — unchanged

V0 [shacl-vs-owl.md § 3.3](shacl-vs-owl.md) reasoning unchanged. CQ-009 is OWL (definitional) + SHACL (runtime gate).

---

## 4. Updated summary table (V1 totals)

| Constraint category | OWL (V0+V1) | SHACL (V0+V1) |
|---|:-:|:-:|
| Disjointness (tagged-union, role disjointness) | **11** (V0 = 10; V1 + 1 three-way disjointness) | — |
| Cardinality on class definitions | **11** (V0 = 10; V1 + 1 canonicalUnit max-1) | — |
| Inherent property characteristics | **11** (V0 = 10; V1 + 1 canonicalUnit Functional) | — |
| Domain/range inference | **12** (V0 = 10; V1 + 2 range widenings on authoredBy/spokenBy) | — |
| Subclass / subproperty hierarchy | **11** (V0 = 10; V1 + 1 EnergyExpertRole subClassOf bfo:Role) | — |
| BFO Role-inheres-in | **11** (V0 = 10; V1 + 1 EnergyExpertRole inheres in Person) | — |
| EquivalentTo defined kind | **11** (V0 = 10; V1 + 1 ei:Expert EquivalentTo) | — |
| DID-scheme URI regex | — | yes (V0 S-1) |
| JSON-parseability of `rawDims` | — | yes (V0 S-2) |
| Cross-property inequality | — | yes (V0 S-3) |
| Referential integrity to ABox registry | — | yes (V0 S-6) |
| Closed-world presence checks | — | yes (V0 S-9; V1 S-V1-2 resolvability gate) |
| Business-policy numeric ranges | — | yes (V0 S-7) |
| URI-well-formedness on `xsd:anyURI` values | — | yes (V0 S-5) |
| ConceptScheme-scoped label uniqueness | — | yes (V0 S-10) |
| Frozen-vocabulary membership (QUDT, OEO) | — | **yes (V1 S-V1-1, S-V1-5)** |
| Role-bearing companion check on V1 properties | — | **yes (V1 S-V1-3, S-V1-4)** |

V1 totals: **16 OWL constraints; 15 SHACL shapes** (V0 had 10 + 10).

---

## 5. Architect inheritance — SHACL companion file

V1 shape file plan:
- Append to V0 [`ontologies/energy-intel/shapes/energy-intel-shapes.ttl`](../shapes/) OR create sibling file `energy-intel-v1-shapes.ttl` per architect's preference.
- Architect runs `pyshacl --inference rdfs --shapes <file> --data <energy-intel.ttl>` against fresh V1 fixtures during validation.
- All five new shapes are independent — they can be added incrementally.

The V0 shape file template is the architect's reference. V1 introduces no new SHACL feature beyond what V0 already uses (`sh:property`, `sh:path`, `sh:class`, `sh:in`, `sh:sparql`, `sh:severity`, `sh:qualifiedValueShape`). All five V1 shapes are pyshacl-compatible.
