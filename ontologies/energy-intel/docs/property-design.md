# Property Design — `energy-intel`

**Authored:** 2026-04-22 by `ontology-conceptualizer`
**Consumer:** `ontology-architect` (authors OWL axioms and SHACL shapes from this spec).

`intent:` values: `infer` (use OWL domain/range for inference), `validate` (SHACL constraint), `restrict` (per-class OWL restriction), `annotate` (annotation property, no constraint).

---

## 1. Object properties — measurement module (domain = CMC or measurement class)

| Property | Domain | Range | Cardinality on domain | Characteristics | Super-property | RO parent (if any) | Intent | Notes |
|---|---|---|---|---|---|---|---|---|
| `ei:evidences` | `ei:EvidenceSource` | `ei:CanonicalMeasurementClaim` | see note | — | — | `RO:0002558 is_evidenced_by` (inverse) | infer | Named-domain via the abstract class `ei:EvidenceSource` (conceptual-model § 8.1); invariant `CMC SubClassOf (inverse ei:evidences) min 1 ei:EvidenceSource` via CQ-009. Do NOT declare transitive. |
| `ei:references` | `ei:CanonicalMeasurementClaim` | `owl:Thing` | 0..n | — | — | `IAO:0000136 is_about` (candidate super) | annotate | Abstract super-property. Architect: do not attach cardinalities or class-level restrictions to `ei:references` itself; attach them to the five children. Consider declaring `rdfs:subPropertyOf IAO:0000136` to align with IAO's `is about` vocabulary. |
| `ei:referencesVariable` | `ei:CanonicalMeasurementClaim` | `ei:Variable` | 0..1 (max 1) | Functional | `ei:references` | `IAO:0000136` (transitive via ei:references) | infer + restrict | CQ-003/CQ-006/CQ-007/CQ-008. Cardinality axiom: `CMC SubClassOf ei:referencesVariable max 1 ei:Variable`. |
| `ei:referencesSeries` | `ei:CanonicalMeasurementClaim` | `ei:Series` | 0..1 | Functional | `ei:references` | `IAO:0000136` | infer + restrict | CQ-004. `CMC SubClassOf ei:referencesSeries max 1 ei:Series`. |
| `ei:referencesDistribution` | `ei:CanonicalMeasurementClaim` | `dcat:Distribution` | 0..1 | Functional | `ei:references` | `IAO:0000136` | infer + restrict | CQ-005. `CMC SubClassOf ei:referencesDistribution max 1 dcat:Distribution`. |
| `ei:referencesDataset` | `ei:CanonicalMeasurementClaim` | `dcat:Dataset` | 0..1 | Functional | `ei:references` | `IAO:0000136` | infer + restrict | CQ-010. |
| `ei:referencesAgent` | `ei:CanonicalMeasurementClaim` | `ei:Organization` | 0..1 | Functional | `ei:references` | `IAO:0000136` | infer + restrict | CQ-010. Note: range is `ei:Organization`, not `foaf:Agent`. `foaf:Agent` is satisfied transitively via FOAF's own `foaf:Organization ⊑ foaf:Agent`. |
| `ei:aboutTechnology` | `ei:CanonicalMeasurementClaim` | `skos:Concept` | 0..n | — | — | `IAO:0000136` | infer | CQ-013/CQ-014. Range widens to OEO classes (as individuals via punning) post-V0. Not Functional — a CMC may cover multiple technology concepts. |
| `ei:implementsVariable` | `ei:Series` | `ei:Variable` | exactly 1 | Functional | — | — | infer + restrict | `Series SubClassOf ei:implementsVariable exactly 1 ei:Variable`. SKY-316 parity with sevocab. |
| `ei:publishedInDataset` | `ei:Series` | `dcat:Dataset` | 0..1 | Functional | — | — | infer + restrict | Inverse of `ei:hasSeries`. |
| `ei:hasSeries` | `dcat:Dataset` | `ei:Series` | 0..n | — | `ei:publishedInDataset` (inverse) | — | infer | Inverse declaration. |

---

## 2. Object properties — media module (domain = media class)

| Property | Domain | Range | Cardinality | Characteristics | Super-property | RO parent | Intent | Notes |
|---|---|---|---|---|---|---|---|---|
| `ei:presents` | `ei:Post` | `ei:MediaAttachment` | 0..n | — | — | — | infer | A Post presents 0..n media attachments. Range widened from Chart per scope § Decisions media-layer expansion. |
| `ei:authoredBy` | `ei:Post` | `ei:Expert` | exactly 1 | Functional | — | `RO:0002352 input_of` (weak fit); see `_shared/relation-semantics.md` rationale | infer + restrict | CQ-002. `Post SubClassOf ei:authoredBy exactly 1 ei:Expert`. |
| `ei:inConversation` | `ei:Post` | `ei:SocialThread` | 0..1 | Functional | — | — | infer | Post belongs to 0..1 SocialThread. |
| `ei:repliesTo` | `ei:Post` | `ei:Post` | 0..1 | Functional, Irreflexive, Asymmetric | — | — | infer + restrict | Reply partial-order. Irreflexive because a post cannot reply to itself; asymmetric because a reply-chain has a direction. |
| `ei:spokenBy` | `ei:PodcastSegment` | `ei:Expert` | 0..n | — | — | `RO:0000057 has_participant` (specialised) | infer | CQ-011. Multi-speaker segments permitted. |
| `ei:partOf` (podcast) | `ei:PodcastSegment` | `ei:PodcastEpisode` | exactly 1 | Functional, Transitive? see note | — | `BFO:0000050 part_of` | infer + restrict | Note: **do NOT assert Transitive** here. Scope.md constrains part-of to PodcastSegment → PodcastEpisode one-hop; no two-hop nesting in V0. If architect wants BFO's transitive `BFO:0000050`, declare `ei:partOfPodcast rdfs:subPropertyOf BFO:0000050` and let the parent's transitivity propagate inferentially. |
| `ei:bearerOf` | `ei:Organization` | `bfo:Role` | 0..n | — | — | `BFO:0000053 bearer_of` | infer | For role attribution: `Organization ei:bearerOf ei:PublisherRole` or `ei:DataProviderRole`. Super-property `BFO:0000053` gives BFO alignment. Not used in any V0 CQ but required by ODP F.2 (Role pattern). |

---

## 3. Data properties — measurement module

| Property | Domain | Range | Cardinality | Characteristics | Intent | Notes |
|---|---|---|---|---|---|---|
| `ei:assertedValue` | `ei:CanonicalMeasurementClaim` | `xsd:decimal` ∪ `xsd:string` (datatype union) | 0..1 | Functional | infer + validate | Scope § Decisions locks this datatype union. Architect: `rdfs:range [ owl:unionOf ( xsd:decimal xsd:string ) ]`. SHACL shape validates format ("decimal or string only"). |
| `ei:assertedUnit` | `ei:CanonicalMeasurementClaim` | `xsd:string` | 0..1 | Functional | infer | Surface token (GW, TWh, etc.) in V0. Canonical `qudt:Unit` IRI linkage deferred. |
| `ei:assertedTime` | `ei:CanonicalMeasurementClaim` | `ei:ClaimTemporalWindow` | 0..1 | Functional | infer + restrict | Note: `ei:assertedTime` is an **object property**, not data property — its range is a class. Keeping it in the measurement section for locality; architect declares as `owl:ObjectProperty`. |
| `ei:rawLabel` | `ei:CanonicalMeasurementClaim` | `xsd:string` | 0..1 | Functional | annotate | Surface text fragment. No semantic constraint. |
| `ei:rawDims` | `ei:CanonicalMeasurementClaim` | `xsd:string` | 0..1 | Functional | validate | JSON-literal in V0. SHACL shape validates JSON-parseability (see `shacl-vs-owl.md` § 3). |
| `ei:intervalStart` | `ei:ClaimTemporalWindow` | `xsd:date` ∪ `xsd:dateTime` (union) | 0..1 | Functional | infer + validate | Window start. SHACL validates date or datetime format. |
| `ei:intervalEnd` | `ei:ClaimTemporalWindow` | `xsd:date` ∪ `xsd:dateTime` (union) | 0..1 | Functional | infer + validate | Window end. SHACL validates `intervalEnd >= intervalStart` if both present (cross-property constraint, SHACL-only). |

---

## 4. Data properties — media module

| Property | Domain | Range | Cardinality | Characteristics | Intent | Notes |
|---|---|---|---|---|---|---|
| `ei:hasSegmentIndex` | `ei:PodcastSegment` | `xsd:integer` | 0..1 | Functional | infer + validate | Ordering within Episode. SHACL validates `sh:minInclusive 0`. |
| `ei:screenshotOf` | `ei:Screenshot` | `xsd:anyURI` | 0..1 | Functional | infer + validate | URL of captured external content. SHACL validates URI-well-formedness. |
| `ei:excerptFrom` | `ei:Excerpt` | `xsd:anyURI` | 0..1 | Functional | infer + validate | URL of the quoted source. |

---

## 5. Annotation properties

| Property | Domain | Range | Intent | Notes |
|---|---|---|---|---|
| `prov:wasGeneratedBy` | `ei:CanonicalMeasurementClaim` | `prov:Activity` | annotate | Applied as an annotation property in V0 (full Activity individuals deferred to ABox). Scope § Decisions. |
| `skos:altLabel` | any class | literal | annotate | Used on `ei:CanonicalMeasurementClaim` ("Candidate") and `ei:Variable` ("CanonicalMeasurementSeries") for cross-codebase naming continuity (pre-glossary § comments). |
| `skos:exactMatch`, `closeMatch`, `broadMatch`, `narrowMatch` | any class | `skos:Concept` | annotate | For alias relations per Linear D4. Applied by mapper phase, not conceptualizer. |
| `rdfs:label`, `rdfs:comment`, `skos:definition` | any class/property | literal | annotate | Standard metadata. `skos:definition` preferred over `rdfs:comment` for formal definitions per CLAUDE.md. |
| `dcterms:title`, `description`, `modified`, `license`, `creator`, `publisher` | ontology / dataset individuals | various | annotate | DCAT-native metadata. Architect applies on `dcat:Dataset` / `dcat:Distribution` instances when ABox arrives. |

---

## 6. Domain-disjunction decision — `ei:evidences`

**Question from skill prompt:** should `ei:evidences` domain be `(Post ∪ MediaAttachment ∪ PodcastSegment)` inline, or promoted to a named abstract class `ei:EvidenceSource`?

**Decision (see conceptual-model.md § 8.1):** named abstract class `ei:EvidenceSource` under `iao:InformationContentEntity`, with `ei:Post`, `ei:MediaAttachment`, `ei:PodcastSegment` asserted as `rdfs:subClassOf ei:EvidenceSource`. Then `ei:evidences rdfs:domain ei:EvidenceSource`.

Anti-pattern mitigations this buys:
- **§ 10 Domain/range overcommitment** (`_shared/anti-patterns.md`) — a named class is easier to audit than a union.
- **§ 4 Missing disjointness** — with named siblings we can write `AllDisjointClasses(ei:Post, ei:MediaAttachment, ei:PodcastSegment)` under `ei:EvidenceSource`, which would be awkward at the union level.
- **Invariant simplicity** — CQ-009 becomes `CMC SubClassOf (inverse ei:evidences) min 1 ei:EvidenceSource` (simple) instead of `CMC SubClassOf (inverse ei:evidences) min 1 (Post ⊔ MediaAttachment ⊔ PodcastSegment)` (verbose; drifts).

---

## 7. Characteristics audit (per-property explicit declaration)

Per [`_shared/relation-semantics.md`](../../../.claude/skills/_shared/relation-semantics.md): silent omission is not "not applicable". Every object property has its characteristics record:

| Property | Functional | InvFunctional | Transitive | Symmetric | Asymmetric | Reflexive | Irreflexive |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `ei:evidences` | no | no | no | no | no | no | no |
| `ei:references` (super) | no | no | no | no | no | no | no |
| `ei:referencesVariable` | **yes** | no | no | no | no | no | no |
| `ei:referencesSeries` | **yes** | no | no | no | no | no | no |
| `ei:referencesDistribution` | **yes** | no | no | no | no | no | no |
| `ei:referencesDataset` | **yes** | no | no | no | no | no | no |
| `ei:referencesAgent` | **yes** | no | no | no | no | no | no |
| `ei:aboutTechnology` | no | no | no | no | no | no | no |
| `ei:implementsVariable` | **yes** | no | no | no | no | no | no |
| `ei:publishedInDataset` | **yes** | no | no | no | no | no | no |
| `ei:hasSeries` | no | **yes** | no | no | no | no | no |
| `ei:presents` | no | no | no | no | no | no | no |
| `ei:authoredBy` | **yes** | no | no | no | no | no | no |
| `ei:inConversation` | **yes** | no | no | no | no | no | no |
| `ei:repliesTo` | **yes** | no | no | no | **yes** | no | **yes** |
| `ei:spokenBy` | no | no | no | no | no | no | no |
| `ei:partOf` (podcast) | **yes** | no | see note | no | **yes** | no | **yes** |
| `ei:bearerOf` | no | no | no | no | no | no | no |

**`ei:partOf` (podcast) transitivity note:** declared `rdfs:subPropertyOf BFO:0000050 part of`, which IS Transitive upstream. Do not re-declare Transitive locally — that's the parent's property. Inheritance handles it.

**`ei:hasSeries` InverseFunctional:** yes — a Series is published in at most one Dataset (Series side is Functional), so the inverse `Dataset hasSeries` is inverse-functional: if two Datasets `hasSeries` the same Series, they must be equal.

---

## 8. Open property-design questions (conceptualizer records; architect resolves)

1. Whether `ei:references` should be declared `rdfs:subPropertyOf IAO:0000136` (IAO `is about`). Recommendation: **yes**, but architect verifies IAO import contains the property and pin matches.
2. Whether `ei:evidences` should be declared `rdfs:subPropertyOf` an RO-level "is evidenced by" inverse. Candidate: `RO:0002558 is_evidenced_by` (if the direction is `evidence → claim`, our `ei:evidences` matches the inverse). Architect confirms direction against RO v2025 release.
3. Whether `ei:partOf` (podcast) should be renamed to `ei:partOfEpisode` to avoid confusion with a future generic part-of (e.g., segment of transcript-of-segment). Recommendation: **yes, rename now** — avoids future refactor. Architect applies.
