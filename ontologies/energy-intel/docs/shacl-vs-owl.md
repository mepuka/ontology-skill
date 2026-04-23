# SHACL vs OWL Intent — `energy-intel`

**Authored:** 2026-04-22 by `ontology-conceptualizer`
**Consumer:** `ontology-architect` (writes OWL axioms AND drafts SHACL shapes per `scout-to-conceptualizer-handoff.md` § "Things conceptualizer may want to revisit" — build-time SHACL is in scope even though runtime SHACL is a non-goal).

**Decision framework** (from `_shared/closure-and-open-world.md` + `_shared/anti-patterns.md § 10`):
- **OWL** = ontological truth that SHOULD drive classification / inference. Use when the claim is true-in-the-domain and the reasoner should derive subclass membership or unsatisfiability from violation.
- **SHACL** = validation constraint that SHOULD NOT drive classification. Use when the claim is "data-shape correctness" (format, referential integrity, cross-property invariants) rather than ontological truth.

---

## 1. OWL-only constraints (ontological truth, reasoner-visible)

These are axioms from `axiom-plan.md`. Listed here to make the OWL-vs-SHACL boundary explicit.

| # | Constraint | Axiom form | Why OWL |
|---|---|---|---|
| O-1 | CMC is disjoint with Observation | `ei:CMC owl:disjointWith ei:Observation` | Ontological: a single entity cannot be both (tagged-union invariant). Reasoner must flag violation. |
| O-2 | CMC has at least one evidencing source | `ei:CMC SubClassOf (inverse ei:evidences) min 1 ei:EvidenceSource` (CQ-009) | Definitional: a CMC without evidence is conceptually incoherent. Belongs in the class intension. |
| O-3 | Post has exactly 1 author | `ei:Post SubClassOf ei:authoredBy exactly 1 ei:Expert` | Ontological: in the Skygest domain, every Post *has* an attributable author (scope § Non-goals excludes anonymous posts). Classification of Post must require an Expert. |
| O-4 | Each `ei:references*` max 1 | `ei:CMC SubClassOf ei:referencesVariable max 1 ei:Variable` (and ×4 siblings) | Definitional: resolution-grain invariant (a CMC cannot reference two Variables). |
| O-5 | Series implements exactly 1 Variable | `ei:Series SubClassOf ei:implementsVariable exactly 1 ei:Variable` | Definitional (SKY-316 parity): a Series without a Variable is incoherent. |
| O-6 | PodcastSegment part-of exactly 1 PodcastEpisode | `ei:PodcastSegment SubClassOf ei:partOfEpisode exactly 1 ei:PodcastEpisode` | Definitional: a segment belongs to one episode. |
| O-7 | PublisherRole / DataProviderRole inhere in Organization | `Role SubClassOf (BFO:0000052 some ei:Organization)` | BFO axiomatisation: a role with no bearer cannot exist. |
| O-8 | Pairwise disjointness of sibling classes | `DisjointClasses(...)` across measurement, media, agent | Ontological: siblings are mutually exclusive kinds. |
| O-9 | Property domains/ranges that drive inference | `ei:evidences rdfs:domain ei:EvidenceSource`, `rdfs:range ei:CanonicalMeasurementClaim` | OWL domain/range used as inference (the scout's property-usage classifies subjects into EvidenceSource). |
| O-10 | Functional characteristics where cardinality is 0..1 or exactly 1 | `ei:authoredBy a owl:FunctionalProperty`, etc. | Reasoner uses Functional to fuse individuals and detect inconsistency. |

All ten O-items are ontological claims. None of them should be relegated to SHACL — doing so would leave the reasoner unable to detect violations at build-time.

---

## 2. SHACL-only constraints (validation, classification-neutral)

These constraints would create unwanted inferences if expressed in OWL, or describe data-shape correctness that is outside the TBox's remit.

| # | Constraint | SHACL shape shape | Why SHACL (not OWL) |
|---|---|---|---|
| S-1 | `ei:Post` `ei:authoredBy` value must have DID-scheme URI | `sh:targetClass ei:Post ; sh:property [ sh:path ei:authoredBy ; sh:pattern "^did:(plc|web):[a-z0-9:.\\-]+$" ]` | DID-scheme is a data-format constraint (string pattern on an IRI), not an ontological class-membership assertion. Expressing it in OWL would require an enumerated datatype that the reasoner does not actually use. |
| S-2 | `ei:rawDims` must parse as valid JSON | `sh:targetClass ei:CanonicalMeasurementClaim ; sh:property [ sh:path ei:rawDims ; sh:pattern "^\\{.*\\}$" ]` + external JSON validation | JSON-well-formedness is a syntactic property of the literal value. OWL has no native JSON validator. |
| S-3 | `ei:intervalEnd >= ei:intervalStart` when both present | `sh:sparql` constraint on `ei:ClaimTemporalWindow` | OWL 2 cannot express cross-data-property inequalities. This is a classic SHACL-SPARQL target. |
| S-4 | `ei:hasSegmentIndex` ≥ 0 | `sh:minInclusive 0` on the segment-index shape | OWL 2 datatype restrictions can express `xsd:nonNegativeInteger`, but that's tighter than intended (the index should be `xsd:integer` nominally; the non-negative constraint is a business rule). SHACL keeps classification semantics neutral. |
| S-5 | `ei:screenshotOf`, `ei:excerptFrom` values are well-formed URIs | `sh:nodeKind sh:IRI` + `sh:pattern "^https?://..."` | URI-format is a SHACL concern; OWL's `xsd:anyURI` accepts any string literal. |
| S-6 | `ei:Organization` referenced via `ei:referencesAgent` must exist in the registry (referential integrity) | `sh:class ei:Organization` + ABox registry-lookup SPARQL constraint | Referential integrity is closed-world; OWL OWA cannot express "this IRI must be present". SHACL with SPARQL target does it. |
| S-7 | `ei:assertedValue` if a decimal, must be ≥ 0 (for capacity-like variables) | `sh:or (...)` + `sh:minInclusive 0` for the decimal branch | Business constraint (non-negative capacities). Does not drive classification. |
| S-8 | Every `ei:Post` should have either `ei:presents` or non-empty text (closed-world shape check) | `sh:or ( [ sh:minCount 1 on ei:presents ] [ sh:minCount 1 on text data property ] )` — SHACL | OWL OWA would permit this silently; closed-world presence check is SHACL territory. |
| S-9 | `ei:Variable` should carry `rdfs:label` (V0 SHACL-side requirement; OWL-side would over-constrain if V1 unpacks Variable) | `sh:minCount 1` on `rdfs:label` | V0-only validation; OWL-side `Variable SubClassOf rdfs:label exactly 1 xsd:string` would bake a commitment that V1 might renegotiate. |
| S-10 | SKOS `altLabel` uniqueness scoped to a ConceptScheme (e.g., `ei:TemporalResolution`) | `sh:uniqueLang` or `sh:SPARQLConstraint` | Uniqueness across siblings is SHACL-native; OWL can express `InverseFunctional` on `skos:prefLabel` but not scheme-scoped uniqueness. |

All ten S-items describe validation concerns. They should NOT live in the OWL file because:
- **They do not drive classification.** A missing `rdfs:label` does not change the kind of thing a Variable is.
- **They are runtime / build-time integrity checks**, not domain truths.
- **They may vary by deployment** (S-6's registry-lookup depends on which registry instance we're validating against).

---

## 3. Boundary cases — discussed explicitly

### 3.1 "Post has exactly 1 author" — O-3 above

- **Why OWL (not SHACL):** the Skygest domain definition of Post *requires* an author. A Post without an author is not a Post. This is an ontological definition, not a shape rule.
- **OWA trap:** OWL `exactly 1` on an open-world ABox means "at most 1 distinct author, plus we can't assert a specific author until one is given." A Post individual with zero `authoredBy` triples is not inconsistent under OWA until the ABox is closed.
- **Resolution:** OWL carries the definitional claim (O-3). SHACL carries the runtime validation (every Post *in our ABox* must have the triple materialised). Both are authored; they serve different gates.

### 3.2 "CMC must reference something" — NOT in the axiom plan

Scope does NOT require a CMC to have at least one `ei:references*` populated — resolution is explicitly partial (UC-002 main flow). Source-only CMCs are legitimate (`ei:resolutionState = source_only` from early drafts, now derivable). No OWL or SHACL constraint here.

### 3.3 CMC evidence invariant (CQ-009) — OWL, not SHACL

- **Why OWL:** it is the *definitional* invariant of CMC. A CMC without evidence is not a CMC; it is a speculation. The reasoner should declare an unmanned CMC (if any ever reaches the graph) as violating the class definition.
- **Why *also* SHACL:** OWA would let the reasoner accept a CMC with no asserted `ei:evidences` triple at build-time without flagging it (the missing triple could just be missing from this snapshot). A SHACL shape `sh:targetClass ei:CanonicalMeasurementClaim ; sh:property [ sh:path [ sh:inversePath ei:evidences ] ; sh:minCount 1 ]` catches it at validation time on a closed ABox.
- **Pattern recorded in `axiom-plan.md § CQ-009` as OWL; SHACL companion shape is in scope for the architect's shapes file.**

### 3.4 DID-URI format on Expert — S-1

- **Why SHACL (not OWL):** the DID format (`did:plc:...` / `did:web:...`) is a string pattern. OWL 2 datatype facets could express a regex, but the regex is a policy choice (Skygest requires DIDs today; some future consumer might not), not an ontological truth.

### 3.5 Data-property datatype unions (e.g., `ei:assertedValue`)

- **Why OWL:** the union `xsd:decimal ∪ xsd:string` is a datatype range declaration, directly OWL-expressible. It drives inference (a decimal value classifies the CMC's `assertedValue` at the expected type).
- **Why *also* SHACL for the SHACL-side checks:** specific regex constraints on the string form (e.g., "if string, must match a numeric-with-unit pattern") belong in SHACL.

---

## 4. Summary table

| Constraint category | OWL | SHACL |
|---|:-:|:-:|
| Disjointness (tagged-union) | yes | — |
| Cardinality on class definitions (`exactly`, `max`, `min`) | yes | — |
| Inherent property characteristics (Functional, Transitive, etc.) | yes | — |
| Domain/range inference | yes | — |
| Subclass / subproperty hierarchy | yes | — |
| BFO Role-inheres-in | yes | — |
| DID-scheme URI regex | — | yes |
| JSON-parseability of `rawDims` | — | yes |
| Cross-property inequality (e.g., `intervalEnd >= intervalStart`) | — | yes |
| Referential integrity to ABox registry | — | yes |
| Closed-world presence checks (`Variable has label`) | — | yes |
| Business-policy numeric ranges (non-negative capacity) | — | yes |
| URI-well-formedness on `xsd:anyURI` values | — | yes |
| ConceptScheme-scoped label uniqueness | — | yes |

Ten OWL concerns; ten SHACL concerns. The architect authors OWL axioms (per `axiom-plan.md`) and drafts SHACL shapes (per the ten rows in § 2 above) in `ontologies/energy-intel/shapes/`. Validator runs both.
