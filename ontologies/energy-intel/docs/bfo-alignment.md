# BFO Alignment — `energy-intel`

**Authored:** 2026-04-22 by `ontology-conceptualizer`
**Reviewer:** Mepuka Kessy (`kokokessy@gmail.com`)
**Reviewed at:** 2026-04-22
**Consumer:** `ontology-architect` (uses BFO/IAO IRIs when asserting `rdfs:subClassOf`).

BFO 2020 (ISO 21838-2:2021) IRIs used throughout. Class decisions recorded against the three decision recipes in [`_shared/bfo-decision-recipes.md`](../../../.claude/skills/_shared/bfo-decision-recipes.md).

---

## 1. Per-class BFO decisions — agent module

### 1.1 `ei:Expert`

- **Decision:** `bfo:Continuant → bfo:IndependentContinuant → bfo:MaterialEntity → bfo:Object` via `foaf:Person`.
- **Recipe applied:** continuant / occurrent → continuant (persists through time); independent / dependent → independent (exists independently of other entities); material / immaterial → material (has mass). Lands at `bfo:Object`. FOAF's `foaf:Person` is the canonical label-level commitment; BFO placement is implicit via the FOAF-to-BFO alignment that many downstream consumers (CIDOC-CRM, Person-OBO) rely on.
- **Rationale:** scope § Decisions explicitly chooses `foaf:Person` over a `bfo:Role` on Expert. Product owner's directive.
- **Ambiguity score:** **0**. Obvious placement.

### 1.2 `ei:Organization`

- **Decision:** `bfo:MaterialEntity → bfo:ObjectAggregate (BFO_0000027)`, with second asserted parent `foaf:Organization`.
- **Recipe applied:** an Organization is a *collection of members that persists while membership changes*. BFO 2020's `ObjectAggregate` is defined for this exact pattern (EIA gains and loses employees without ceasing to be EIA).
- **Rationale:** scope § Decisions dual-parent.
- **Ambiguity score:** **1**. Not fully obvious — an Organization could plausibly be modelled as an `iao:ICE` (legal fiction / information entity) rather than material. BFO 2020 chooses material; we follow. Reviewer: Mepuka Kessy. Decision documented; no escalation.

### 1.3 `ei:PublisherRole`, `ei:DataProviderRole`

- **Decision:** `bfo:Continuant → bfo:SpecificallyDependentContinuant → bfo:RealizableEntity → bfo:Role (BFO_0000023)`, each inhering-in `ei:Organization`.
- **Recipe applied:** quality / role / disposition → **role**. A role exists because its bearer is in a particular social/institutional context; it is not part of the bearer's physical makeup (BFO definition). Publishing is exactly this: EIA bears DataProvider-role because it is an institution engaged in the social activity of releasing datasets.
- **Axiom to architect:** `ei:PublisherRole SubClassOf (BFO:0000052 inheres_in some ei:Organization)` (same for DataProviderRole). The `inheres_in` relation is BFO-provided; architect confirms prefix.
- **Ambiguity score:** **0**. Role placement matches every reference example in BFO 2020 (professor, nurse, student).

### 1.4 Agent-layer ambiguity register

| Class | Candidate categories | Ambiguity | Reviewer | Decision | Rationale |
|---|---|---|---|---|---|
| `ei:Expert` | `bfo:Object` (via foaf:Person) | 0 | — | `bfo:Object` | Person is canonical Object example. |
| `ei:Organization` | `bfo:ObjectAggregate`, `iao:ICE` (legal-fiction framing) | 1 | kokokessy@gmail.com | `bfo:ObjectAggregate` | Scope § Decisions ratified; matches BFO 2020 examples. |
| `ei:PublisherRole` | `bfo:Role` | 0 | — | `bfo:Role` | Textbook role placement. |
| `ei:DataProviderRole` | `bfo:Role` | 0 | — | `bfo:Role` | Same. |

No ambiguity ≥ 2 in agent module.

---

## 2. Per-class BFO decisions — media module

All media classes land under `iao:InformationContentEntity` (IAO_0000030), which is BFO 2020's `bfo:GenericallyDependentContinuant (GDC)`. An ICE is a GDC that is *about* some thing; media artefacts fit (a chart is *about* a measurement; a post is *about* whatever the expert says).

### 2.1 `ei:Post`

- **Decision:** `iao:Document (IAO_0000310) → iao:ICE → bfo:GDC`. Second parent: `ei:EvidenceSource` (local abstract under `iao:ICE`).
- **Recipe applied:** continuant / occurrent → continuant (a post persists on the platform); independent / dependent → dependent (requires the platform as bearer); quality / role / disposition → none of those (it's information, not a dependency on a material bearer's substance). Lands on ICE; narrows to Document because a post "bundles" text + media into a collection understood together (matches IAO Document definition).
- **Ambiguity score:** **1**. Candidate was `iao:Image` (some posts are single images), but Posts can include text + multiple attachments → Document is correct. Reviewer: kokokessy@gmail.com; decision ratified.

### 2.2 `ei:Conversation`, `ei:SocialThread`, `ei:PodcastEpisode`

- **Decision:** all under `iao:ICE`. `ei:PodcastEpisode` additionally under `iao:Document` (an episode collects segments + description).
- **Ambiguity score:** **0** for Conversation/SocialThread, **1** for PodcastEpisode (Document-vs-ICE narrower choice). Reviewer ratified.

### 2.3 `ei:PodcastSegment`

- **Decision:** `iao:ICE` direct (not `iao:Document` — a segment is a unit, not a collection).
- **Ambiguity score:** **0**.

### 2.4 `ei:MediaAttachment`

- **Decision:** `iao:ICE` abstract.
- **Ambiguity score:** **0**. Umbrella class.

### 2.5 `ei:Chart`, `ei:Screenshot`, `ei:GenericImageAttachment`

- **Decision:** `iao:Image (IAO_0000101) → iao:ICE → bfo:GDC`. Second parent: `ei:MediaAttachment`.
- **Recipe applied:** IAO Image is defined as "an affine projection to a two-dimensional surface, of measurements of some quality... represented as color and luminosity on the projected-on surface". Charts, screenshots, and generic image attachments all fit.
- **Renamed 2026-04-22:** local `ei:Image` → `ei:GenericImageAttachment` per product-owner directive ("address the image gap; we want a concept of images"). Avoids short-name collision with `iao:Image` (IAO_0000101) and makes the catch-all role explicit in the class name.
- **Ambiguity score:** **0**. IAO Image is the textbook placement.

### 2.6 `ei:Excerpt`

- **Decision:** `iao:TextualEntity (IAO_0000300) → iao:ICE → bfo:GDC`. Second parent: `ei:MediaAttachment`.
- **Verification:** OLS4 v2 probe 2026-04-22 confirms `IAO_0000300` is active, label "textual entity", not deprecated, definition: "A textual entity is a part of a manifestation (FRBR sense), a generically dependent continuant whose concretizations are patterns of glyphs intended to be interpreted as words, formulas, etc."
- **Ambiguity score:** **0**. Textbook fit.

### 2.7 `ei:EvidenceSource`

- **Decision:** `iao:ICE → bfo:GDC`, abstract primitive.
- **Rationale:** a named container for the three things (Post, MediaAttachment, PodcastSegment) that can evidence a CMC. See conceptual-model § 8.1.
- **Ambiguity score:** **0**. Abstract umbrella, BFO-innocent.

### 2.8 Media-layer ambiguity register

| Class | Candidate categories | Ambiguity | Reviewer | Decision | Rationale |
|---|---|---|---|---|---|
| `ei:Post` | `iao:Document`, `iao:ICE`, `iao:Image` | 1 | kokokessy@gmail.com | `iao:Document` | Posts bundle text + media → Document matches the IAO definition. |
| `ei:PodcastEpisode` | `iao:Document`, `iao:ICE` | 1 | kokokessy@gmail.com | `iao:Document` + `ei:Conversation` | Episode collects segments → Document fits. |
| `ei:Chart` | `iao:Image`, `iao:DataItem` | 1 | kokokessy@gmail.com | `iao:Image` | Chart is primarily a 2D visual projection; data-item would apply to the numbers inside. |
| Others | — | 0 | — | — | Obvious. |

No ambiguity ≥ 2 in media module.

---

## 3. Per-class BFO decisions — measurement module

All under `iao:InformationContentEntity`. The measurement module is the ICE-heavy core.

### 3.1 `ei:CanonicalMeasurementClaim`

- **Decision:** `iao:ICE → bfo:GDC`. Disjoint with `ei:Observation`.
- **Recipe applied:** continuant / occurrent → continuant (the claim persists as a graph node); independent / dependent → generically dependent (requires a bearer — the Post, Chart, etc.); ICE is the narrowing because the claim is *about* a Variable/Series.
- **Ambiguity score:** **2**. Genuine tension. Alternative readings:
  - (a) `bfo:Process` — "an assertion is an act of asserting" — would promote CMC to occurrent.
  - (b) `iao:ICE` (current) — the claim as an information content entity.
  - (c) Reified-speech-act — a quaternary with speaker, asserted-content, time, proposition.
- **Reviewer:** kokokessy@gmail.com. **Resolution:** (b) `iao:ICE`. Rationale: Linear D7 frames CMC as a *noun* (claim content extracted), not an act; the extractor produces a CMC node in the graph, not an action-record. The "act of asserting" is captured separately via `prov:wasGeneratedBy → prov:Activity` in the ABox phase. Cite: Linear D7 tagged-union + scope § Decisions CMC.
- **Escalation:** none — reviewer signed off.

### 3.2 `ei:Observation`

- **Decision:** `iao:ICE → bfo:GDC`. Disjoint with CMC.
- **Ambiguity score:** **1**. Alternative: `SOSA Observation` (which has both ICE-like and event-like aspects). We side with ICE because V0 doesn't import SOSA (reuse-report § R8 rejected SOSA) and the thin-Observation class in V0 carries no event semantics.
- **Reviewer:** kokokessy@gmail.com.

### 3.3 `ei:Variable`, `ei:Series`

- **Decision:** `iao:ICE → bfo:GDC`.
- **Recipe applied:** both are identifiers for measured concepts; they are *about* a reference grain. ICE-appropriate.
- **Ambiguity score:** **1** each. Alternative reading: Variable could be a `iao:DataItem (IAO_0000027)` if we consider the Variable IRI as a data-identifier. We stay at ICE because the seven-facet model (deferred) treats Variable as a composed descriptor; at V0 the thin class fits ICE more naturally than DataItem.
- **Reviewer:** kokokessy@gmail.com.

### 3.4 `ei:ClaimTemporalWindow`

- **Decision (flipped 2026-04-22):** `bfo:TemporalRegion (BFO_0000008)`. Product owner ratified: "temporal region would make sense."
- **Prior framing (superseded):** the class was tentatively parked under `iao:ICE → bfo:GDC` treating the window as a *description* of time. Conceptualizer scored ambiguity 2, escalated for ratification.
- **Recipe applied:** continuant / occurrent → occurrent temporal; the window denotes an interval in time itself. BFO `TemporalRegion` is the native category for occurrent time intervals.
- **Rationale for the flip:**
  - Two distinct CMCs asserting "2025 YTD" should resolve to the same (or a `sameAs`-linked) temporal region; the region **is** the time, and `intervalStart` / `intervalEnd` give the region its extent.
  - Future OWL-Time MIREOT can specialise `ei:ClaimTemporalWindow` under `time:ProperInterval` without re-parenting.
  - The "surface form" concern (`2025 YTD` is a string) is addressed via `rdfs:label` annotation, not by misplacing the class under ICE.
- **Ambiguity score (historical):** 2. Now resolved.
- **Reviewer:** kokokessy@gmail.com (ratified 2026-04-22 in product-owner interview).
- **Escalation:** none.

### 3.5 Measurement-layer ambiguity register

| Class | Candidate categories | Ambiguity | Reviewer | Decision | Rationale |
|---|---|---|---|---|---|
| `ei:CanonicalMeasurementClaim` | `iao:ICE`, `bfo:Process`, reified speech act | **2** | kokokessy@gmail.com | `iao:ICE` | Linear D7 + scope § Decisions. Act-of-asserting is in ABox via PROV, not TBox class. |
| `ei:Observation` | `iao:ICE`, SOSA-style event | 1 | kokokessy@gmail.com | `iao:ICE` | SOSA not imported in V0. |
| `ei:Variable` | `iao:ICE`, `iao:DataItem` | 1 | kokokessy@gmail.com | `iao:ICE` | Seven-facet deferred; thin class fits ICE. |
| `ei:Series` | `iao:ICE`, `iao:DataItem` | 1 | kokokessy@gmail.com | `iao:ICE` | Same reasoning. |
| `ei:ClaimTemporalWindow` | `iao:ICE`, `bfo:TemporalRegion` | **2** (resolved) | kokokessy@gmail.com | `bfo:TemporalRegion` | Ratified 2026-04-22: the window denotes a time region, not a description of one. |

Both ambiguity-≥-2 rows have named reviewer and cite the decision recipe.

---

## 4. Per-class BFO decisions — data module

No local classes. Imported DCAT + FOAF only. DCAT's own BFO alignment is out-of-scope for `energy-intel` (DCAT does not commit to BFO).

---

## 5. Expert-as-Person modelling choice (flagged in skill prompt)

**Ratified (scope § Decisions F1; product-owner reiterated 2026-04-22):** Expert = `foaf:Person` subclass, no `bfo:Role` on Expert in V0.

**Trade-off recorded:**
- If Expert carried an `EnergyExpertRole` (a `bfo:Role` inhering in a Person), the ontology would capture the role-transience: someone *becomes* an energy expert when they start publishing energy claims; the Person identity persists independently.
- V0 collapses the role into the class `ei:Expert` itself. This is the "role-type confusion" anti-pattern (`_shared/anti-patterns.md` § 2) **in principle**, but mitigated in practice because:
  - Skygest treats Expert as a stable attribute tied to DID registration; an Expert stays an Expert.
  - No V0 CQ depends on transient expert-role semantics.
  - The product owner explicitly does NOT want V0 complexity.
- **Move on.** Record this as a known simplification and pick it up in V1 when editorial-role discourse-type ("analyst vs journalist vs academic") needs modelling.

See anti-pattern review § 2 for the corresponding anti-pattern entry and severity (`info`, not `warn`/`block`).

---

## 6. Summary — BFO leaf counts

| BFO leaf | Count | Local classes |
|---|---|---|
| `bfo:Object` | 1 | `ei:Expert` (via foaf:Person) |
| `bfo:ObjectAggregate` | 1 | `ei:Organization` |
| `bfo:Role` | 2 | `ei:PublisherRole`, `ei:DataProviderRole` |
| `bfo:GDC` (via `iao:ICE`) | 15 | `ei:CanonicalMeasurementClaim`, `ei:Observation`, `ei:Variable`, `ei:Series`, `ei:Conversation`, `ei:SocialThread`, `ei:PodcastEpisode`, `ei:PodcastSegment`, `ei:Post`, `ei:MediaAttachment`, `ei:Chart`, `ei:Screenshot`, `ei:Excerpt`, `ei:GenericImageAttachment`, `ei:EvidenceSource` |
| `bfo:TemporalRegion` | 1 | `ei:ClaimTemporalWindow` |

(Count = 15 in GDC + 1 in TemporalRegion; Organization is material; Expert is Object; 2 Roles. Total local = 21.)

No `bfo:Process`, `bfo:Quality`, `bfo:Function`, `bfo:Disposition`, or `bfo:ImmaterialEntity` classes in V0.
