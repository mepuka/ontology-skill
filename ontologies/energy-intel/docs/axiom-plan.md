# Axiom Plan — `energy-intel`

**Authored:** 2026-04-22 by `ontology-conceptualizer`
**Target profile:** OWL 2 DL (scope § Constraints).
**Consumer:** `ontology-architect` implements every axiom below. No SHACL in this file — SHACL obligations live in `shacl-vs-owl.md`.

One section per Must-Have / Should-Have CQ (CQ-001 … CQ-014). Each section cites the ODP from scout's `odp-recommendations.md` and the axiom-pattern row from [`_shared/axiom-patterns.md`](../../../.claude/skills/_shared/axiom-patterns.md). Manchester syntax sketches are inside fenced code blocks; architect realises them in ROBOT templates or hand-written Turtle.

Prefixes assumed: `ei:`, `iao:`, `bfo:`, `foaf:`, `dcat:`, `skos:`, `prov:`, `xsd:`, `RO:` (as in `competency-questions.yaml`).

---

## Foundational axioms (no CQ; prerequisite for all CQs)

These are structural scaffolding — the architect writes them before touching any CQ axiom.

```manchester
# Disjointness
Class: ei:CanonicalMeasurementClaim
  DisjointWith: ei:Observation

Class: ei:PublisherRole
  DisjointWith: ei:DataProviderRole

Class: ei:Expert
  DisjointWith: ei:Organization

# Evidence-source named class
Class: ei:EvidenceSource
  SubClassOf: iao:InformationContentEntity
Class: ei:Post           SubClassOf: ei:EvidenceSource
Class: ei:MediaAttachment SubClassOf: ei:EvidenceSource
Class: ei:PodcastSegment  SubClassOf: ei:EvidenceSource

# Media-attachment pairwise disjointness
DisjointClasses: ei:Chart, ei:Screenshot, ei:Excerpt, ei:GenericImageAttachment

# Evidence-source pairwise disjointness
DisjointClasses: ei:Post, ei:MediaAttachment, ei:PodcastSegment

# Conversation children disjoint
DisjointClasses: ei:SocialThread, ei:PodcastEpisode

# Measurement module pairwise disjoint
DisjointClasses: ei:CanonicalMeasurementClaim, ei:Observation, ei:Variable, ei:Series, ei:ClaimTemporalWindow

# Role pattern — roles inhere in Organization
Class: ei:PublisherRole
  SubClassOf: bfo:Role, (BFO:0000052 some ei:Organization)   # inheres_in
Class: ei:DataProviderRole
  SubClassOf: bfo:Role, (BFO:0000052 some ei:Organization)

# References super-property linkage
ObjectProperty: ei:references
  SubPropertyOf: IAO:0000136     # is about (architect verifies import)

ObjectProperty: ei:referencesVariable    SubPropertyOf: ei:references
ObjectProperty: ei:referencesSeries      SubPropertyOf: ei:references
ObjectProperty: ei:referencesDistribution SubPropertyOf: ei:references
ObjectProperty: ei:referencesDataset     SubPropertyOf: ei:references
ObjectProperty: ei:referencesAgent       SubPropertyOf: ei:references
```

---

## CQ-001 — "For a given Post, which CMCs does it evidence?"

- **UC:** UC-001. **Priority:** must_have. **ODP:** F.3 Information Realization (`odp-recommendations.md § F.3`).
- **Axiom pattern:** `_shared/axiom-patterns.md § 2 Existential` + `§ 10 Property characteristics`.
- **Closure required:** no. **OWA trap:** no (CQ is relational enumeration; empty is a valid answer).
- **Profile impact:** none (simple domain/range).

```manchester
ObjectProperty: ei:evidences
  Domain: ei:EvidenceSource
  Range:  ei:CanonicalMeasurementClaim
```

---

## CQ-002 — "For a given Post, which Expert authored it?"

- **UC:** UC-001. **Priority:** must_have. **ODP:** F.4 Participation (binary shortcut).
- **Axiom pattern:** `§ 2 Existential` + `§ 7 Qualified cardinality`.
- **Closure required:** yes — every Post has an author. Encoded via `exactly 1`. **OWA trap:** mitigated by the cardinality axiom (reasoner treats absence as inconsistency only on a closed ABox; SHACL complements for runtime validation — see `shacl-vs-owl.md`).
- **Profile impact:** qualified cardinality forces OWL 2 DL (out of EL).

```manchester
ObjectProperty: ei:authoredBy
  Domain:         ei:Post
  Range:          ei:Expert
  Characteristics: Functional

Class: ei:Post
  SubClassOf: ei:authoredBy exactly 1 ei:Expert
```

---

## CQ-003 — "For a given CMC, which Variable does it reference (if any)?"

- **UC:** UC-002. **Priority:** must_have. **ODP:** F.3 Information Realization.
- **Axiom pattern:** `§ 2` + `§ 7 (max 1)` + `§ 10 Functional`.
- **Closure required:** no — "if any"; 0..1 explicit.
- **Profile impact:** DL.

```manchester
ObjectProperty: ei:referencesVariable
  Domain:          ei:CanonicalMeasurementClaim
  Range:           ei:Variable
  SubPropertyOf:   ei:references
  Characteristics: Functional

Class: ei:CanonicalMeasurementClaim
  SubClassOf: ei:referencesVariable max 1 ei:Variable
```

---

## CQ-004 — "For a given CMC, which Series does it reference (if any)?"

Same shape as CQ-003 with Series substituted.

```manchester
ObjectProperty: ei:referencesSeries
  Domain:          ei:CanonicalMeasurementClaim
  Range:           ei:Series
  SubPropertyOf:   ei:references
  Characteristics: Functional

Class: ei:CanonicalMeasurementClaim
  SubClassOf: ei:referencesSeries max 1 ei:Series
```

---

## CQ-005 — "For a given CMC, which Distribution does it reference (if any)?"

```manchester
ObjectProperty: ei:referencesDistribution
  Domain:          ei:CanonicalMeasurementClaim
  Range:           dcat:Distribution
  SubPropertyOf:   ei:references
  Characteristics: Functional

Class: ei:CanonicalMeasurementClaim
  SubClassOf: ei:referencesDistribution max 1 dcat:Distribution
```

---

## CQ-006 — "For a given Variable, which CMCs reference it?"

- **UC:** UC-003. **Priority:** must_have.
- **Axiom pattern:** inverse walk of CQ-003. No new axioms beyond CQ-003's declaration.
- `competency-questions.yaml` lists `required_axioms: []` for this CQ. Correct — the walk is satisfied by the domain/range declaration of `ei:referencesVariable` authored for CQ-003.

No new axioms.

---

## CQ-007 — "For a given Variable, which distinct Experts have claimed about it?"

- **UC:** UC-003. **Priority:** must_have.
- **Axiom pattern:** chained walk `Variable ← referencesVariable ← CMC ← evidences ← Post → authoredBy → Expert`. Reasoner does the inference via three domain/range declarations already authored (CQ-001, CQ-002, CQ-003). `required_axioms: []` in CQ-007.

No new axioms.

---

## CQ-008 — "For a given Variable, return cross-expert join payload"

- **UC:** UC-003. **Priority:** must_have.
- **Axiom pattern:** same walk as CQ-007 + data-property reads for `assertedValue`, `assertedUnit`, `assertedTime`.

```manchester
DataProperty: ei:assertedValue
  Domain: ei:CanonicalMeasurementClaim
  Range:  xsd:decimal or xsd:string
  Characteristics: Functional

DataProperty: ei:assertedUnit
  Domain: ei:CanonicalMeasurementClaim
  Range:  xsd:string
  Characteristics: Functional

ObjectProperty: ei:assertedTime
  Domain: ei:CanonicalMeasurementClaim
  Range:  ei:ClaimTemporalWindow
  Characteristics: Functional
```

Note on `ei:assertedValue`: the datatype-union range `xsd:decimal or xsd:string` is expressed in OWL 2 via `rdfs:range` pointing to a datatype union (`_:x rdf:type rdfs:Datatype ; owl:unionOf (xsd:decimal xsd:string)`). Architect constructs the blank-node datatype.

---

## CQ-009 — CMC invariant: every CMC must evidence ≥ 1 media artefact

- **UC:** UC-001. **Priority:** must_have. **ODP:** F.3 Information Realization (invariant form).
- **Axiom pattern:** `§ 2` + `§ 7 (min 1)` on inverse property.
- **Closure required:** yes — the invariant is the closure.
- **Profile impact:** qualified cardinality + inverse property expression → OWL 2 DL.

**Manchester form** (this is the axiom the skill prompt asked us to verify):

```manchester
Class: ei:CanonicalMeasurementClaim
  SubClassOf: (inverse ei:evidences) min 1 ei:EvidenceSource
```

Equivalent Turtle skeleton:

```turtle
ei:CanonicalMeasurementClaim
  rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty [ owl:inverseOf ei:evidences ] ;
    owl:minQualifiedCardinality "1"^^xsd:nonNegativeInteger ;
    owl:onClass ei:EvidenceSource
  ] .
```

**Why `ei:EvidenceSource` instead of the union `(Post ⊔ MediaAttachment ⊔ PodcastSegment)`:**
- The named class is DL-cleaner (single onClass filler).
- The same axiom works if future extensions add another `ei:EvidenceSource` subclass (e.g., `ei:BookExcerpt`) without rewriting the invariant.
- Matches conceptual-model § 8.1 decision.

**Union form (alternative, NOT chosen):**

```manchester
Class: ei:CanonicalMeasurementClaim
  SubClassOf: (inverse ei:evidences) min 1 (ei:Post or ei:MediaAttachment or ei:PodcastSegment)
```

This is also OWL 2 DL — class expressions are allowed as `onClass` fillers — but the named-class form is preferred.

---

## CQ-010 — "Full resolved-reference set for a CMC"

- **UC:** UC-002. **Priority:** must_have.
- **Axiom pattern:** `§ 2 + § 7 (max 1)` on each `ei:references*` child. Already covered by CQ-003 / CQ-004 / CQ-005 plus the three below.

```manchester
ObjectProperty: ei:referencesDataset
  Domain:        ei:CanonicalMeasurementClaim
  Range:         dcat:Dataset
  SubPropertyOf: ei:references
  Characteristics: Functional

ObjectProperty: ei:referencesAgent
  Domain:        ei:CanonicalMeasurementClaim
  Range:         ei:Organization
  SubPropertyOf: ei:references
  Characteristics: Functional

Class: ei:CanonicalMeasurementClaim
  SubClassOf: ei:referencesDataset max 1 dcat:Dataset
Class: ei:CanonicalMeasurementClaim
  SubClassOf: ei:referencesAgent   max 1 ei:Organization
```

Note: CQ-010 expects `foaf:Agent` in `required_classes`. The chain `ei:Organization rdfs:subClassOf foaf:Organization rdfs:subClassOf foaf:Agent` (FOAF upstream) plus the PROV/FOAF bridge (mapper phase) satisfies this without a direct `rdfs:subClassOf foaf:Agent` on `ei:Organization`.

---

## CQ-011 — "For a given PodcastSegment, which Expert(s) spoke it?"

- **UC:** UC-004. **Priority:** should_have. **ODP:** F.4 Participation.

```manchester
ObjectProperty: ei:spokenBy
  Domain: ei:PodcastSegment
  Range:  ei:Expert
```

No cardinality on domain (0..n; multi-speaker segments permitted).

---

## CQ-012 — "For a given PodcastSegment, which CMCs does it evidence?"

- **UC:** UC-004. **Priority:** should_have. **ODP:** F.3 + F.5 (Part-whole).
- The `ei:evidences` domain already covers PodcastSegment via `ei:EvidenceSource`.
- Part-whole for podcast segments:

```manchester
ObjectProperty: ei:partOfEpisode   # renamed from ei:partOf per property-design § 8
  Domain:          ei:PodcastSegment
  Range:           ei:PodcastEpisode
  SubPropertyOf:   BFO:0000050    # part_of
  Characteristics: Functional, Asymmetric, Irreflexive

Class: ei:PodcastSegment
  SubClassOf: ei:partOfEpisode exactly 1 ei:PodcastEpisode
```

Plus segment-index data property:

```manchester
DataProperty: ei:hasSegmentIndex
  Domain: ei:PodcastSegment
  Range:  xsd:integer
  Characteristics: Functional
```

---

## CQ-013 — "CMCs classified under a given energy-technology concept (transitively)"

- **UC:** UC-005. **Priority:** should_have. **ODP:** F.1 Value Partition (for temporal resolution) + F.3 (CMC-is-about-Concept).
- **Note from skill prompt:** union property paths `(skos:broader | rdfs:subClassOf)*` are **query-side**, not axiom-side. Architect's job is only to declare the domain/range of `ei:aboutTechnology`:

```manchester
ObjectProperty: ei:aboutTechnology
  Domain: ei:CanonicalMeasurementClaim
  Range:  skos:Concept
```

**Punning caveat:** when OEO technology classes appear as values of `ei:aboutTechnology`, the OEO IRI is *both* a class and a `skos:Concept` individual (OWL 2 punning). HermiT accepts this; the SPARQL property path walks both directions because the class hierarchy under `rdfs:subClassOf` and the concept hierarchy under `skos:broader` are both materialised in the merged graph. See conceptual-model § 8.3.

**No axiom needed for the transitive walk.** SPARQL 1.1 property paths handle `*` at query time; OWL does not need `skos:broader` to be declared Transitive (SKOS does so upstream; architect verifies the `skos:broader rdf:type owl:TransitiveProperty` declaration propagates).

---

## CQ-014 — "Posts classified under a given energy-technology concept (transitively)"

- **UC:** UC-005. **Priority:** should_have.
- **Axiom requirement:** none beyond CQ-001 (`ei:evidences`) and CQ-013 (`ei:aboutTechnology`).

No new axioms. Two-hop walk `Post → evidences → CMC → aboutTechnology → Concept` is already covered.

---

## Cross-cutting: hierarchy axioms (parents and media-module subclass declarations)

These are bulk `rdfs:subClassOf` declarations the architect must emit; captured once at the end to avoid repetition:

```manchester
# --- agent ---
Class: ei:Expert           SubClassOf: foaf:Person
Class: ei:Organization     SubClassOf: foaf:Organization, bfo:ObjectAggregate
Class: ei:PublisherRole    SubClassOf: bfo:Role
Class: ei:DataProviderRole SubClassOf: bfo:Role

# --- measurement ---
Class: ei:CanonicalMeasurementClaim SubClassOf: iao:InformationContentEntity
Class: ei:Observation               SubClassOf: iao:InformationContentEntity
Class: ei:Variable                  SubClassOf: iao:InformationContentEntity
Class: ei:Series                    SubClassOf: iao:InformationContentEntity
Class: ei:ClaimTemporalWindow       SubClassOf: bfo:TemporalRegion

# --- media ---
Class: ei:Post             SubClassOf: iao:Document, ei:EvidenceSource
Class: ei:Conversation     SubClassOf: iao:InformationContentEntity
Class: ei:SocialThread     SubClassOf: ei:Conversation
Class: ei:PodcastEpisode   SubClassOf: iao:Document, ei:Conversation
Class: ei:PodcastSegment   SubClassOf: iao:InformationContentEntity, ei:EvidenceSource
Class: ei:MediaAttachment  SubClassOf: iao:InformationContentEntity, ei:EvidenceSource
Class: ei:Chart            SubClassOf: iao:Image, ei:MediaAttachment
Class: ei:Screenshot       SubClassOf: iao:Image, ei:MediaAttachment
Class: ei:GenericImageAttachment SubClassOf: iao:Image, ei:MediaAttachment
Class: ei:Excerpt          SubClassOf: iao:TextualEntity, ei:MediaAttachment
Class: ei:EvidenceSource   SubClassOf: iao:InformationContentEntity
```

---

## CQ coverage map

Per skill progress criteria — every Must-Have CQ must appear in this plan:

| cq_id | Pattern | Axioms added | Profile | Closure required | OWA trap? |
|---|---|---|---|---|---|
| CQ-001 | § 2 Existential | 1 (domain/range on `ei:evidences`) | OWL 2 DL | no | no |
| CQ-002 | § 2 + § 7 qualified-cardinality | 1 domain/range + 1 SubClassOf restriction | OWL 2 DL | yes (exactly 1) | mitigated |
| CQ-003 | § 2 + § 7 (max 1) | domain/range + SubClassOf + Functional | OWL 2 DL | no (0..1) | no |
| CQ-004 | § 2 + § 7 (max 1) | same | OWL 2 DL | no | no |
| CQ-005 | § 2 + § 7 (max 1) | same | OWL 2 DL | no | no |
| CQ-006 | inverse walk | 0 (covered by CQ-003) | — | no | no |
| CQ-007 | chained walk | 0 | — | no | no |
| CQ-008 | chained walk + data properties | 3 data/object properties | OWL 2 DL | no | no |
| CQ-009 | § 2 + § 7 (min 1) on inverse | 1 SubClassOf restriction on CMC | OWL 2 DL | yes — the invariant | **closure is the CQ** |
| CQ-010 | § 2 + § 7 (max 1) × 5 | 2 new domain/range + Functional (Dataset, Agent) | OWL 2 DL | no | no |
| CQ-011 | § 2 | 1 domain/range on `ei:spokenBy` | OWL 2 DL | no | no |
| CQ-012 | § 2 + § 7 (exactly 1) | 1 domain/range on `ei:partOfEpisode` + SubClassOf | OWL 2 DL | yes (exactly 1) | mitigated |
| CQ-013 | § 2 | 1 domain/range on `ei:aboutTechnology` | OWL 2 DL + punning | no | no |
| CQ-014 | chained walk | 0 | — | no | no |

All 14 CQs covered. No Must-Have CQ is in "deferred" status.

---

## Profile declaration

**Target profile:** OWL 2 DL throughout. No axiom in this plan requires OWL 2 Full. Several axioms (qualified cardinality, inverse-property expressions, datatype union) push out of OWL 2 EL / QL / RL — scope § Constraints locked DL, so that is intentional.

**HermiT compatibility note:** all axioms above are HermiT 1.4.x compatible. The datatype union on `ei:assertedValue` is a known HermiT edge-case for some OWL API versions; architect should verify ROBOT's HermiT wrapper handles it (`robot reason --reasoner hermit`). ELK cannot reason about qualified cardinality or inverse property expressions; validator skill must use HermiT for the full profile-DL check, and ELK is fast-path for the simple subsumption test only.

---

## License audit (ODP citations)

Per skill prompt, confirm ODP-license compatibility:

| ODP | Source | License | Compatible with energy-intel ecosystem (CC-BY 4.0, W3C Document, permissive)? |
|---|---|---|---|
| F.1 Value Partition | `_shared/pattern-catalog.md § 3.1` (workspace-internal mirror of ODP-portal catalog) | inherits workspace license (project-internal) + SKOS (W3C Document) | **yes** |
| F.2 Role | `_shared/pattern-catalog.md § 3.3` + BFO 2020 role axiomatisation | BFO: CC-BY 4.0 | **yes** |
| F.3 Information Realization | `_shared/pattern-catalog.md § 3.6` + IAO (`IAO:0000136`) | IAO: CC-BY 4.0 | **yes** |
| F.4 Participation | `_shared/pattern-catalog.md § 3.4` + BFO | BFO: CC-BY 4.0 | **yes** |
| F.5 Part-Whole (mereology) | `_shared/pattern-catalog.md § 3.2` + BFO `BFO:0000050` | BFO: CC-BY 4.0 | **yes** |

All five ODPs licensed CC-BY 4.0 or W3C Document (permissive). No conflict.
