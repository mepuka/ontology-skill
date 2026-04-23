# Conceptual Model — `energy-intel`

**Authored:** 2026-04-22 by `ontology-conceptualizer`
**Inputs consumed:**
- Requirements: `scope.md` @ `f6d025d`, `use-cases.yaml` @ `f6d025d`, `competency-questions.yaml` @ `f6d025d`, `pre-glossary.csv` @ `f6d025d`, `traceability-matrix.csv` @ `f6d025d`, `requirements-approval.yaml` @ `f6d025d`.
- Scout: `reuse-report.md` @ `b4f1bf2`, `imports-manifest.yaml` @ `b4f1bf2`, `odp-recommendations.md` @ `b4f1bf2`, `scout-to-conceptualizer-handoff.md` @ `b4f1bf2`.
- External verification: OLS4 v2 `IAO_0000300` probe 2026-04-22 — **active, label "textual entity"**; Excerpt re-parents under `iao:TextualEntity`.

**Ratified decisions (locked pre-start, see skill prompt § "Decisions ratified"):**
- Namespace: `https://w3id.org/energy-intel/` (TBox) + `https://id.skygest.io/{kind}/{ulid}` (ABox, deferred).
- IAO re-parent: `Chart / Screenshot / Image → iao:Image`, `Excerpt → iao:TextualEntity`, `Post / PodcastEpisode → iao:Document`.
- Hand-seeded SKOS `ei:TemporalResolution` ConceptScheme (value-partition ODP F.1).
- `prov:Agent owl:equivalentClass foaf:Agent` via standalone bridge (`mappings/prov-foaf-bridge.ttl`).
- OEO seed-IRI verification is architect-scope; V0 `ei:aboutTechnology` range stays `skos:Concept` + OWL 2 punning.
- Expert as `foaf:Person` subclass; no `bfo:Role` on Expert in V0.

---

## 0. Overview

`energy-intel` is a four-module OWL 2 DL ontology. Classes live in exactly one module. Cross-module properties are allowed; each property is listed under its **domain module**. Module granularity follows [`_shared/modularization-and-bridges.md`](../../../.claude/skills/_shared/modularization-and-bridges.md) § 2 — small, composable, split along domain seams, not lifecycle / implementation seams.

| Module | File (architect-authored) | Architecture layer | Imports required |
|---|---|---|---|
| `measurement` | `modules/measurement.ttl` | **problem-specific** | `iao:`, `dcat:`, `skos:`, `qudt:` (V0 Units MIREOT) |
| `media` | `modules/media.ttl` | **problem-specific** | `iao:` (Document, Image, TextualEntity, ICE) |
| `agent` | `modules/agent.ttl` | **problem-specific** | `foaf:`, `bfo:` (Role, ObjectAggregate), bridge (prov↔foaf) |
| `data` | `modules/data.ttl` | **domain-dependent** (DCAT extension) | `dcat:`, `foaf:` |

Layer assignment rationale:
- `agent`, `measurement`, `media` carry Skygest-specific commitments (CMC tagged-union, expert-authoredBy-post, CMC evidences media) → problem-specific.
- `data` is almost pure DCAT-3 at full fidelity with minimal local axioms (`ei:hasSeries`, `ei:publishedInDataset` extension points); it lives one layer up from problem-specific.
- `foundational` and `domain-independent` layers are occupied by imports only (BFO, IAO, PROV, DC, SKOS, FOAF, QUDT).

Total local class count estimate: **21 local classes** (within the 20-30-in-V0 middle-out budget) + imported parents.

---

## 1. Module `agent`

**Purpose:** represent the actors whose claims `energy-intel` captures and whose data feeds it. Smallest module; architect should axiomatise it first (handoff § 7).

### 1.1 Classes

| Local class | Direct parent(s) | BFO leaf | Module | 1-sentence intent |
|---|---|---|---|---|
| `ei:Expert` | `foaf:Person` | `bfo:MaterialEntity` → `bfo:Object` | agent | A named person with a DID who publishes energy-domain claims on social media or podcasts. |
| `ei:Organization` | `foaf:Organization`, `bfo:ObjectAggregate` (BFO_0000027) | `bfo:MaterialEntity` → `bfo:ObjectAggregate` | agent | An institutional actor (agency, publisher, data provider) that bears a Publisher- or DataProvider- role. |
| `ei:PublisherRole` | `bfo:Role` (BFO_0000023) | `bfo:Continuant` → `bfo:SpecificallyDependentContinuant` → `bfo:RealizableEntity` → `bfo:Role` | agent | The role an Organization bears when it publishes editorial content. |
| `ei:DataProviderRole` | `bfo:Role` (BFO_0000023) | same as above | agent | The role an Organization bears when it publishes data distributions. |

### 1.2 Intent notes

- **Expert is NOT role-bearing in V0.** Product-owner directive. The editorial-role pattern (expert as analyst vs journalist vs academic) is a V1 concern.
- **Organization has dual parent.** `foaf:Organization` supplies social semantics (name, homepage, member); `bfo:ObjectAggregate` supplies part-aggregate semantics (an Organization persists while individual members come and go). Both parents are consistent — BFO 2020 ObjectAggregate is material, and foaf:Organization is a foaf:Agent whose instances are material institutions. See § BFO alignment file.
- **Publisher/DataProvider-Role separation is deliberate.** EIA is *both* a DataProvider (publishes `dcat:Distribution` records) and occasionally a Publisher (publishes narrative reports). Encoding these as roles on a single Organization is more expressive than splitting the Organization into two classes.
- **No team / bot accounts in V0.** scope.md non-goal; product-owner ratified.

---

## 2. Module `media`

**Purpose:** represent the bearers of expert discourse — the posts, podcast segments, and attached visual/textual artefacts that CMCs evidence.

### 2.1 Classes

| Local class | Direct parent(s) | BFO leaf | Module | 1-sentence intent |
|---|---|---|---|---|
| `ei:Post` | `iao:Document` (IAO_0000310) | `bfo:GenericallyDependentContinuant` (GDC) | media | A single authored unit on a social platform (Bluesky `at://` or Twitter `x://`) that bundles text and attached media. |
| `ei:Conversation` (abstract) | `iao:InformationContentEntity` (IAO_0000030) | `bfo:GDC` | media | Abstract supertype for multi-participant discourse units. Not instantiated directly. |
| `ei:SocialThread` | `ei:Conversation` | `bfo:GDC` | media | A reply-tree over `ei:Post` instances on a social platform. |
| `ei:PodcastEpisode` | `iao:Document` (IAO_0000310), `ei:Conversation` | `bfo:GDC` | media | A complete audio recording composed of ordered PodcastSegments. |
| `ei:PodcastSegment` | `iao:InformationContentEntity` (IAO_0000030) | `bfo:GDC` | media | A timestamped portion of a PodcastEpisode, spoken by one or more Experts. |
| `ei:MediaAttachment` (abstract) | `iao:InformationContentEntity` (IAO_0000030) | `bfo:GDC` | media | Abstract supertype for chart/screenshot/excerpt/image payloads attached to a Post. |
| `ei:Chart` | `iao:Image` (IAO_0000101), `ei:MediaAttachment` | `bfo:GDC` | media | A data visualisation (bar, line, pie, etc.) embedded in or screenshotted into a post. |
| `ei:Screenshot` | `iao:Image` (IAO_0000101), `ei:MediaAttachment` | `bfo:GDC` | media | A raster capture of external content (news article, report, PDF, external post). |
| `ei:Excerpt` | `iao:TextualEntity` (IAO_0000300), `ei:MediaAttachment` | `bfo:GDC` | media | A quoted text block from an external source — pull-quote, transcribed report snippet. |
| `ei:GenericImageAttachment` | `iao:Image` (IAO_0000101), `ei:MediaAttachment` | `bfo:GDC` | media | First-class sibling of Chart / Screenshot / Excerpt for image attachments that are not one of those three — photos, diagrams, logos, slides, memes, infographics. Renamed from `ei:Image` 2026-04-22 to avoid short-name collision with `iao:Image`. |

### 2.2 Intent notes

- **PodcastEpisode has two asserted parents** (`iao:Document` + `ei:Conversation`). Multiple inheritance is OWL 2 DL-safe here because `iao:Document` is an `iao:InformationContentEntity` and `ei:Conversation` is an `iao:InformationContentEntity` — the intersection is consistent. Flagged in `taxonomy.md` for reasoner review.
- **MediaAttachment subclasses also have two asserted parents** (the IAO image/text parent + `ei:MediaAttachment`). Same consistency argument: both are ICE specialisations.
- **`ei:GenericImageAttachment` is a first-class sibling** under `ei:MediaAttachment` — architect does NOT need to pre-seed subclasses. A photo, diagram, logo, slide, meme, or infographic attached to a post that is not a chart, not a screenshot of external content, and not a textual excerpt, lands here.
- **Conversation is abstract** (no direct individuals expected). Kept as a named class so downstream consumers can query "all multi-participant artefacts" in one hop.
- **No `ei:AudioFile` / `ei:ImageFile` bearer class in V0.** We model the information content, not the MP3/PNG on disk (see anti-pattern review § 7 Information-Physical Conflation). The runtime ABox can carry file URLs as data-property attachments when needed.

---

## 3. Module `measurement`

**Purpose:** represent the tagged-union of expert claims (CMC) and data observations (Observation), and the three "join grain" classes (Variable, Series) + Distribution reference path.

### 3.1 Classes

| Local class | Direct parent(s) | BFO leaf | Module | 1-sentence intent |
|---|---|---|---|---|
| `ei:CanonicalMeasurementClaim` | `iao:InformationContentEntity` (IAO_0000030) | `bfo:GDC` | measurement | An editorial claim extracted from a media artefact that asserts a measurement about the energy domain. |
| `ei:Observation` | `iao:InformationContentEntity` (IAO_0000030) | `bfo:GDC` | measurement | A fully-resolved data point ingested from a `dcat:Distribution`. Thin in V0 — no CQs hit it yet. |
| `ei:Variable` | `iao:InformationContentEntity` (IAO_0000030) | `bfo:GDC` | measurement | A reference-grain identifier for a measured quantity (e.g., "solar installed capacity, US, monthly"). Thin in V0 — seven-facet identity deferred to V1. |
| `ei:Series` | `iao:InformationContentEntity` (IAO_0000030) | `bfo:GDC` | measurement | A concrete realization of a Variable published in a Dataset. Thin in V0. |
| `ei:ClaimTemporalWindow` | `bfo:TemporalRegion` (BFO_0000008) | `bfo:TemporalRegion` | measurement | The temporal region denoted by a CMC (e.g., "2025 YTD", "March 2024"). Product-owner ratified 2026-04-22: `bfo:TemporalRegion` is the correct BFO placement; `intervalStart` and `intervalEnd` data properties give the region its extent. |

### 3.2 Intent notes

- **CMC and Observation are disjoint.** Both are ICE; the disjointness axiom lives in the axiom plan (CQ-009 neighbour) — it encodes the Linear D7 tagged-union decision.
- **Variable and Series are deliberately thin.** V0 carries IRI + `rdfs:label` + optional `rdfs:comment` only. No `hasMeasuredProperty`, no `hasStatisticType`, no `owl:hasKey`. The axiom plan keeps Variable as the range of `ei:referencesVariable` and Series as the range of `ei:referencesSeries`; the architect adds no more.
- **`ei:ClaimTemporalWindow` is `bfo:TemporalRegion` (flipped 2026-04-22).** See `bfo-alignment.md` § 3.4 for the rationale. Short version: the window denotes a region of time, not a description of one; data properties `intervalStart` / `intervalEnd` give the region its extent. Future OWL-Time MIREOT can specialise under `time:ProperInterval` without re-parenting.
- **`ei:Observation` is thin-with-intent.** Kept as a named, disjoint-from-CMC class so the data-ingest lane (post-V0) can subclass and constrain without touching CMC axioms.

### 3.3 Properties (domain = CMC or measurement class)

Full property tables live in `property-design.md` § 3. Summary of what lives here:
- `ei:evidences` (domain-union; domain-module = measurement — see § 8 on the union domain).
- `ei:references`, `ei:referencesVariable`, `ei:referencesSeries`, `ei:referencesDistribution`, `ei:referencesDataset`, `ei:referencesAgent`.
- `ei:aboutTechnology` (range `skos:Concept`, widens to OEO via punning).
- `ei:assertedValue`, `ei:assertedUnit`, `ei:assertedTime`.
- `ei:rawLabel`, `ei:rawDims`.
- `ei:implementsVariable`, `ei:publishedInDataset`, `ei:hasSeries`.
- `ei:intervalStart`, `ei:intervalEnd`.

---

## 4. Module `data`

**Purpose:** extend DCAT 3 with the two extension points (`ei:hasSeries`, `ei:publishedInDataset`) needed by the resolver, and nothing else. No local class declarations beyond the DCAT classes that are already imported.

### 4.1 Classes (imported, listed for traceability)

| Imported class | IRI | Referenced by |
|---|---|---|
| `dcat:Catalog` | `http://www.w3.org/ns/dcat#Catalog` | scope.md modules |
| `dcat:CatalogRecord` | `http://www.w3.org/ns/dcat#CatalogRecord` | scope.md modules |
| `dcat:Dataset` | `http://www.w3.org/ns/dcat#Dataset` | CQ-010 |
| `dcat:Distribution` | `http://www.w3.org/ns/dcat#Distribution` | CQ-005, CQ-010 |
| `dcat:DataService` | `http://www.w3.org/ns/dcat#DataService` | scope.md modules |
| `dcat:DatasetSeries` | `http://www.w3.org/ns/dcat#DatasetSeries` | scope.md modules (distinct from `ei:Series`) |

### 4.2 Intent notes

- **No local DCAT subclasses in V0.** DCAT 3 is imported at full fidelity; `ei:` adds extension properties only.
- **`dcat:DatasetSeries` and `ei:Series` are not equivalent.** `dcat:DatasetSeries` is "a set of datasets released as a series" (e.g., Form 860 2023, 2024, 2025 releases); `ei:Series` is a time-indexed measurement series implementing a Variable. Distinct concepts; both kept.
- **`ei:publishedInDataset` range is `dcat:Dataset`**, not `dcat:DatasetSeries` — the resolver points to the concrete `dcat:Dataset` that contains a series.

---

## 5. Property design — high-level rationale

Full spec: `property-design.md`. Conceptualizer intent highlights:

- **`ei:references` is an abstract super-property** over five `ei:references*` children. It exists so downstream consumers can write `SELECT ?x WHERE { ?cmc ei:references ?x }` to get the full reference set without union; axioms are attached to the five children, not to the parent (scope § Decisions D7).
- **`ei:evidences` has a union domain.** `(ei:Post ∪ ei:MediaAttachment ∪ ei:PodcastSegment)`. See § 8 below and `property-design.md` § 4 for the decision: introduce an **abstract named class `ei:EvidenceSource`** OR keep the union domain inline.
- **All `ei:references*` carry `max 1` cardinality on CMC.** That's the resolution-grain invariant (scope.md § Decisions: resolution state is derivable from which properties are populated). A CMC cannot reference two Variables; if it would, it's two CMCs.
- **`ei:evidences` carries `min 1` on CMC** (CQ-009). That's the only hard existential CMC invariant.

---

## 6. BFO alignment summary

Full rationale: `bfo-alignment.md`. Summary:

| BFO leaf | Local classes |
|---|---|
| `bfo:MaterialEntity → bfo:Object` | `ei:Expert` (via `foaf:Person`) |
| `bfo:MaterialEntity → bfo:ObjectAggregate` | `ei:Organization` |
| `bfo:SpecificallyDependentContinuant → bfo:Role` | `ei:PublisherRole`, `ei:DataProviderRole` |
| `bfo:GenericallyDependentContinuant (via iao:ICE)` | `ei:CanonicalMeasurementClaim`, `ei:Observation`, `ei:Variable`, `ei:Series`, `ei:Conversation`, `ei:SocialThread`, `ei:PodcastEpisode`, `ei:PodcastSegment`, `ei:Post`, `ei:MediaAttachment`, `ei:Chart`, `ei:Screenshot`, `ei:Excerpt`, `ei:GenericImageAttachment`, `ei:EvidenceSource` |
| `bfo:TemporalRegion` | `ei:ClaimTemporalWindow` |

No local class is a `bfo:Process`, `bfo:Quality`, `bfo:Function`, or `bfo:Disposition` in V0. Processes (extraction activity, publication, speaking) are represented as `prov:Activity` individuals in the ABox phase, not TBox classes.

---

## 7. ODP instantiations

Per scout's `odp-recommendations.md` — five ODPs adopted. Conceptualizer confirms:

| ODP | scout ref | Uses |
|---|---|---|
| F.1 Value partition | `odp-recommendations.md § F.1` | Hand-seeded `ei:TemporalResolution` ConceptScheme (5 SKOS concepts). Architect seeds; conceptualizer confirms binding. |
| F.2 Role | `odp-recommendations.md § F.2` | `ei:PublisherRole`, `ei:DataProviderRole`. Bearer = `ei:Organization`. |
| F.3 Information realization | `odp-recommendations.md § F.3` | CMC (ICE) ↔ `ei:evidences` (concretizedBy arrow) ↔ Post/MediaAttachment/PodcastSegment (bearer); `ei:references*` (isAbout arrow) ↔ Variable/Series/Distribution/Dataset/Organization. |
| F.4 Participation | `odp-recommendations.md § F.4` | `ei:authoredBy` (Expert participates in authoring a Post); `ei:spokenBy` (Expert participates in speaking a Segment). Binary-shortcut form in V0. |
| F.5 Part-whole | `odp-recommendations.md § F.5` | `ei:PodcastSegment partOf ei:PodcastEpisode` + `ei:hasSegmentIndex` ordering. |

All five ODPs: license compatible (CC-BY 4.0 upstream for BFO/IAO; W3C-Document for SKOS; all permissive). ODP portal `Submissions:*` pages inaccessible at scout run; `_shared/pattern-catalog.md` is the authoritative mirror — licensing inherits from mirror, which inherits the workspace license (project-internal reuse).

---

## 8. Key modelling resolutions

### 8.1 `ei:evidences` union domain — recommend abstract class `ei:EvidenceSource`

**Scout and CQ-009 both state** the domain is `(ei:Post ∪ ei:MediaAttachment ∪ ei:PodcastSegment)`. Two encoding options:

**Option A — union domain inline:**
```
ei:evidences rdfs:domain [ owl:unionOf ( ei:Post ei:MediaAttachment ei:PodcastSegment ) ] .
```
Valid OWL 2 DL. But: (1) every validator tool must render the union; (2) the CQ-009 invariant `CMC SubClassOf (inverse ei:evidences) min 1 (Post ∪ MediaAttachment ∪ PodcastSegment)` repeats the union, risking drift; (3) no reusable handle for the "things that can evidence a CMC" class.

**Option B — named abstract class `ei:EvidenceSource`:**
```
ei:EvidenceSource  rdfs:subClassOf iao:InformationContentEntity .
ei:Post            rdfs:subClassOf ei:EvidenceSource .
ei:MediaAttachment rdfs:subClassOf ei:EvidenceSource .
ei:PodcastSegment  rdfs:subClassOf ei:EvidenceSource .
ei:evidences       rdfs:domain     ei:EvidenceSource .
ei:CanonicalMeasurementClaim rdfs:subClassOf ( (inverse ei:evidences) min 1 ei:EvidenceSource ) .
```

**Recommendation: Option B.**

- It gives a single, reusable class handle for CQ-009's invariant and for any future SPARQL ("find every artefact that can serve as evidence").
- It avoids union-domain repetition drift.
- It's DL-clean. `ei:EvidenceSource` is a *primitive* ICE subclass (not an EquivalentTo-with-union); its three asserted subclasses are exhaustive by convention, not by covering axiom. If V0 needs to assert exhaustiveness, add a covering axiom later: `ei:EvidenceSource EquivalentTo (ei:Post ⊔ ei:MediaAttachment ⊔ ei:PodcastSegment)`. V0 keeps it primitive (OWA-friendly).
- Cost: one extra class. Benefit: clarity + single source of truth for the invariant.

**Decision: adopt `ei:EvidenceSource` as a named abstract class in module `media`.** Architect implements. Anti-pattern review § 10 (Domain/range overcommitment) benefits from this: a named domain is clearer than a union at domain level.

### 8.2 CMC / Observation disjointness

**Ratified:** `ei:CanonicalMeasurementClaim owl:disjointWith ei:Observation` (scope.md § Decisions D7 + Linear D7 tagged-union).

Both are `iao:InformationContentEntity`. Disjointness is necessary because:
- CMC lives in the editorial lane (evidenced by a media artefact).
- Observation lives in the data lane (ingested from a Distribution).
- A single entity cannot be both simultaneously without violating the tagged-union.

Anti-pattern review § 4 (Missing Disjointness) satisfied.

### 8.3 OWL 2 punning for `ei:aboutTechnology`

**Ratified:** range stays `skos:Concept` in V0; later phase admits OEO technology classes as values via OWL 2 punning (scope.md § Reasoning).

Punning caveat for architect (recorded here, not enforced):
- When OEO technology classes appear as values of `ei:aboutTechnology`, each OEO IRI denotes both a `skos:Concept` (individual) and an `owl:Class`. OWL 2 punning permits this.
- The SPARQL path `(skos:broader | rdfs:subClassOf)*` on CQ-013/CQ-014 works under both views — this was the scout's rationale and it holds.
- **DL profile:** punning is OWL 2 DL compliant; the architect's reasoner (HermiT) accepts it.

### 8.4 Thin Variable / Series

**Ratified:** V0 Variable = IRI + `rdfs:label` + optional `rdfs:comment`. Same for Series with `ei:implementsVariable exactly 1` and `ei:publishedInDataset max 1`. No seven-facet identity in V0.

Conceptualizer note: this creates an anti-pattern-neighbour with § 1 (Singleton hierarchy) — Variable has no subclasses in V0. That's intentional and documented. When V1 lands the facet model, Variable grows subclasses or faceted sub-restrictions; no premature depth.

### 8.5 Thread reply-tree via `ei:repliesTo`

**Ratified:** `SocialThread` uses `ei:repliesTo` as a binary reply-tree partial order, NOT part-whole or ordered-list. A Post has `ei:repliesTo max 1 Post`; the implicit root of a thread has zero `repliesTo`.

Not part-whole because: a reply is not a "part" of its parent (a reply is an independent Post referring to another Post). Not ordered-list because: reply trees branch; a list would flatten.

---

## 9. Coverage sanity check

Every Must-Have CQ has a concept-level commitment in this model:

| CQ | Commitment in this doc |
|---|---|
| CQ-001 | `ei:evidences` (§ 3.3, § 8.1) |
| CQ-002 | `ei:authoredBy` (§ 7 F.4, property-design.md) |
| CQ-003, CQ-004, CQ-005, CQ-010 | `ei:references*` family (§ 3.3, § 5) |
| CQ-006, CQ-007, CQ-008 | join grain classes Variable + Expert + Post (§ 1.1, § 3.1) |
| CQ-009 | CMC `min 1` evidence via `ei:EvidenceSource` (§ 8.1, § 8.2) |
| CQ-011, CQ-012 | PodcastSegment + `ei:spokenBy` + `ei:evidences` (§ 2.1, § 7 F.4/F.3) |
| CQ-013, CQ-014 | `ei:aboutTechnology` + punning on `skos:Concept` (§ 8.3) |

Every pre-glossary term has a module assignment (see per-module § 1.1 / 2.1 / 3.1 / 4.1 above).

---

## 10. Gaps for requirements / scout loopback

Record-only; conceptualizer does not amend upstream artefacts.

1. ~~**`ei:Image` overlaps `iao:Image`**~~ **Resolved 2026-04-22:** renamed local class to `ei:GenericImageAttachment` per product-owner directive ("address the image gap; we want a concept of images"). No further action.
2. **`dcat:DatasetSeries` vs `ei:Series` naming collision** noted in § 4.2. No action needed (distinct concepts), but the architect's ROBOT report will flag similar labels; curator refresh may propose a clarifying `skos:altLabel` on `ei:Series`.
3. **Seven-facet Variable deferral leaves Variable as an effectively unconstrained ICE subclass.** The `max 1` and `implementsVariable exactly 1` cardinalities on related properties give *some* reasoner traction, but a Variable individual with no label still satisfies the TBox. If the SHACL shapes file wants to enforce "every Variable has `rdfs:label`", that's a SHACL concern (see `shacl-vs-owl.md` § 2). Non-blocking.
4. **CQ-010 returns `per_row: [agent, dist, dataset, var, series]` but CQ lists no `referencesVariable`-to-Expert or `referencesSeries`-to-Post path.** That's intentional — CQ-010 is single-CMC enumeration. If a stakeholder later asks "for each resolved-grain of a CMC, who is the publishing Organization of that Distribution?", that would extend the walk but is not in V0. Non-blocking; captured for possible CQ addition in next requirements refresh.
5. **Scout's scope.md loopback § Gaps for requirements loopback is inherited.** Conceptualizer adds no new items there beyond the four above; scout's five gaps (OEO_00000030 fix, temporal-resolution hand-seed, OEO quantity-value vs QUDT, DCAT Agent not-a-class, IAO re-parenting) stand and are all addressed in this conceptual model.
