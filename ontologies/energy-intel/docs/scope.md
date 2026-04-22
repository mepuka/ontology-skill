# Scope — `energy-intel` Ontology

**Short name:** `energy-intel` (prefix `ei:`, TBox namespace `https://w3id.org/energy-intel/`)
**Full label:** Energy Intelligence Ontology (EIO)
**Build:** standalone POD at `ontologies/energy-intel/`
**Date:** 2026-04-22
**Product owner / sole reviewer:** Mepuka Kessy (`kokokessy@gmail.com`)

## Step 0 — scope gate

| Gate | Verdict | Evidence |
|---|---|---|
| Scope fit | **approved** | Unified TBox vocabulary for cross-repo integration (agentology, skygest-cloudflare, skygest-editorial). Target graph-store backing queryable expert-claim → data resolution. Classic ontology problem (shared vocabulary, inter-op, reasoning over multi-grain resolution). |
| Retrofit check | **false** | No modeling has started at `ontologies/energy-intel/`. Prior art in sibling repos is explicitly treated as **reference, not retrofit**: we read design decisions from sevocab (`ontologies/skygest-energy-vocab/`), agentology (`packages/ontology/ontologies/source/skygest-canonical.ttl`), and Linear docs, but do not extend or import any of them. No `docs/requirements-retrofit-note.md` needed. |
| Stakeholder available | **true** | Single-stakeholder model for this iteration: product owner is also the domain expert and sole reviewer. All Must-Have CQs will be reviewed in this session. |

## Purpose + framing

`energy-intel` is the TBox vocabulary backbone of the Skygest Discourse
Engine. It formalizes the classes and properties needed to represent,
resolve, and reason about **expert claims that cite energy data**: a chart
posted to Bluesky, a figure cited in a podcast segment, a paragraph of
post text referencing a specific dataset — all resolve through the same
measurement → variable → series → dataset → distribution chain.

The ontology's job is threefold:

1. **Give a stable resolution target** for expert claim references (per
   H-DL-5 from the April 8 Linear design session: "expert claims are the
   demand-pull, not a kind of observation").
2. **Enable the cross-expert join** — two experts citing different
   sources landing on the same canonical `Series` (per H-DL-6:
   "optimize for the join, not the average row").
3. **Serve as the source of truth for runtime data shapes** — the
   runtime consumes generated TypeScript from ontology-derived
   manifests (per the 2026-04-13 Series + Ontology-Driven Runtime
   Alignment spec). The Worker does not ship an RDF stack.

TBox-first for this phase. An ABox (individuals at
`https://id.skygest.io/{kind}/{ulid}` per Linear D3) lands in a future
phase when the graph store is stood up.

## In-scope (classes + properties live in four modules)

| Module | File | Owns |
|---|---|---|
| `measurement` | `ontologies/energy-intel/modules/measurement.ttl` | `CanonicalMeasurementClaim`, `Observation`, **thin** `Variable`, **thin** `Series`. Seven-facet Variable identity **deferred to V1** (see § Decisions resolved). Includes `ei:aboutTechnology` on CMC as the V0 grain for technology classification. |
| `media` | `ontologies/energy-intel/modules/media.ttl` | `Post`, `PodcastEpisode`, `PodcastSegment`, `Conversation` abstract supertype, `SocialThread`. `MediaAttachment` abstract class with subclasses `Chart`, `Screenshot`, `Excerpt`, `Image`. Posts present MediaAttachments; any MediaAttachment can evidence a CMC. |
| `agent` | `ontologies/energy-intel/modules/agent.ttl` | `Organization` (parent), `Expert` (strict `foaf:Person` subclass), role classes (`PublisherRole`, `DataProviderRole`). Reuses `foaf:Agent` / `prov:Agent`. |
| `data` | `ontologies/energy-intel/modules/data.ttl` | Full DCAT-3 seven-entity set (`Catalog`, `CatalogRecord`, `Dataset`, `Distribution`, `DataService`, `DatasetSeries`, `Agent`) with **minimal local axioms** (extension points only; full DCAT vocab imported). |

Top-level rollup: `ontologies/energy-intel/energy-intel.ttl` imports all
four modules.

### Key properties to land (preview — full list in `pre-glossary.csv` after Step 6)

| Property | Domain → Range | Purpose |
|---|---|---|
| `ei:presents` | `Post` → `MediaAttachment` | A post presents 0..n media attachments (Chart, Screenshot, Excerpt, Image). |
| `ei:authoredBy` | `Post` → `Expert` | Post-to-expert attribution; exactly 1. |
| `ei:spokenBy` | `PodcastSegment` → `Expert` | Speaker attribution; 0..n (multi-speaker segments). |
| `ei:inConversation` | `Post` → `SocialThread` | Post belongs to a thread (0..1). |
| `ei:repliesTo` | `Post` → `Post` | Reply-tree partial order within a SocialThread (0..1). |
| `ei:evidences` | `Post ∪ MediaAttachment ∪ PodcastSegment` → `CanonicalMeasurementClaim` | The media artefact(s) a CMC was extracted from; 1..n per CMC. |
| `ei:references` | `CanonicalMeasurementClaim` → `owl:Thing` | Abstract super-property over the five specific `ei:references*` properties (D7). |
| `ei:referencesVariable` | `CanonicalMeasurementClaim` → `Variable` | 0..1 — resolution may be partial. |
| `ei:referencesSeries` | `CanonicalMeasurementClaim` → `Series` | 0..1. |
| `ei:referencesDistribution` | `CanonicalMeasurementClaim` → `Distribution` | 0..1. |
| `ei:referencesDataset` | `CanonicalMeasurementClaim` → `Dataset` | 0..1. |
| `ei:referencesAgent` | `CanonicalMeasurementClaim` → `Organization` | 0..1. |
| `ei:aboutTechnology` | `CanonicalMeasurementClaim` → `skos:Concept` | 0..n — claim-level technology / topic classification. V0 range is `skos:Concept`; OEO MIREOT subtree imports later (see § Open questions). |
| `ei:implementsVariable` | `Series` → `Variable` | Series implements exactly one Variable (per Linear SKY-316). |
| `ei:publishedInDataset` | `Series` → `Dataset` | Series lives in exactly one Dataset (inverse of `hasSeries`). |
| `ei:screenshotOf` | `Screenshot` → `xsd:anyURI` | 0..1 — URL of the external source the screenshot captures (news article, report, external post). |
| `ei:excerptFrom` | `Excerpt` → `xsd:anyURI` | 0..1 — URL of the quoted source. |

Variable and Series are **thin classes** in V0 (IRI + `rdfs:label` + optional
`rdfs:comment`). The seven-facet Variable composition from Linear D2 is
**deferred to V1** — V0 keeps the join-grain plumbing but not the facet
semantics. CMC naming keeps the `CanonicalMeasurementClaim` label; a
`skos:altLabel "Candidate"` will align with runtime naming in
`skygest-cloudflare`.

## Out-of-scope (non-goals)

Each non-goal bounds the design space and will be restated on the final
ORSD under an explicit "Non-goals" heading.

1. **Chart rendering / pixel geometry / image processing.**
   *Rationale:* visual-layout concerns live in the vision enrichment
   pipeline and downstream rendering; the ontology models the claim, not
   the image.
2. **Full social graph** — followers, likes, DMs, reposts, mutes, lists.
   *Rationale:* Skygest models *what an expert said*, not the
   attention-economy graph around them. Keeping social primitives out
   prevents the ontology from drifting into becoming a social-network
   schema.
3. **Authentication, billing, subscription, user accounts** beyond the
   `Expert` and organizational-role classes needed to attribute claims.
   *Rationale:* product runtime concerns, not domain semantics.
4. **Full OEO fidelity.** The ontology *depends on* OEO via a minimal
   MIREOT extract (technology, fuel, aggregation, temporal-resolution
   subtrees only) and does not redefine OEO's process / observation /
   quantity machinery. *Rationale:* shallow-extract reduces maintenance
   surface and keeps us aligned without re-owning the upstream model.
5. **Narrative / Story / Arc / ArgumentPattern / Edition classes.** The
   editorial process is in active flux and these concepts are better
   captured as *aggregations over curated CMCs* later (via skill
   `ontology-curator` or a follow-on module). *Rationale:* locking in
   editorial process classes now would ossify a workflow that is still
   being iterated in `skygest-editorial`.
6. **Runtime RDF / SPARQL / SHACL execution in the Worker.**
   *Rationale:* per the Apr 13 "Series + Ontology-Driven Runtime
   Alignment" locked decision #1. The ontology is build-time input; the
   runtime consumes generated TypeScript and plain JSON.
7. **ABox (individuals) in this phase.** TBox classes + properties
   only. Individual IRIs at `https://id.skygest.io/{kind}/{ulid}` stay a
   deferred concern; the ontology must be *capable* of receiving an ABox
   later but need not land one now.
8. **Entity registry content as ontology individuals.** Per Linear
   Architecture Principle 4: FERC, EIA, `@mepuka` are not ontology
   classes or individuals in this phase — they are rows in the runtime
   D1 registry, typed against `energy-intel` classes when the ABox
   eventually comes online. The ontology draws the TBox/ABox line here
   explicitly.
9. **Seven-facet Variable identity model (Linear D2).** Deferred to
   V1. *Rationale (from 2026-04-22 interview):* the facet
   axiomatisation adds substantial complexity (seven required
   properties, `owl:hasKey` over a seven-tuple, facet-value enum
   classes, null-vs-sentinel semantics) for a feature that is not
   essential to the V0 cross-expert-join product query. Variable and
   Series stay thin; CMCs reference them as opaque join grains. The
   facet model lands in V1 once the V0 loop closes.

## Constraints

| Constraint | Value | Source |
|---|---|---|
| Upper ontology | BFO (ISO 21838-2) | `CLAUDE.md` default |
| OWL profile | **OWL 2 DL** | `CLAUDE.md` default; no EL / QL / RL narrowing without documented reason |
| TBox namespace | `https://w3id.org/energy-intel/` (prefix `ei:`) | This doc |
| ABox namespace (deferred) | `https://id.skygest.io/{kind}/{ulid}` | Linear D3 (Apr 8 Data Intelligence Layer session) |
| Build regime | Standalone POD (no ODK) | `CLAUDE.md` |
| Serialization | Turtle (.ttl) canonical; Manchester syntax for review | `CLAUDE.md` |
| Naming | CamelCase classes, camelCase properties | `CLAUDE.md` |
| Target size | ~80–150 classes (4 local modules + MIREOT imports) | Estimate from module plan |
| Reasoner | HermiT for OWL 2 DL profile validation + ELK for fast-path during iteration | tooling default |

## Reused external ontologies (MIREOT-minimal)

| Ontology | Scope imported | Strategy | Why |
|---|---|---|---|
| **BFO** | Full | `owl:imports` | Upper ontology, small, stable. |
| **OEO** (Open Energy Ontology) | Technology subtree + fuel subtree + temporal-resolution subtree + aggregation-type subtree | `robot extract --method BOT` into `imports/oeo-subset.ttl` | User directive: "lean on OEO for technology concepts, be as minimal as possible at the beginning." |
| **QUDT** | `qudt:QuantityKind`, `qudt:Unit`, `unit:*` individuals actually referenced | `robot extract` narrow slice into `imports/qudt-subset.ttl` | Units are required (user directive) but full QUDT is ~hundreds of MB — trim aggressively. |
| **DCAT 3** | Full | `owl:imports` | DCAT 7-entity set at full fidelity (user directive); vocabulary is small. |
| **PROV-O** | Full | `owl:imports` | Provenance chain for CMCs; `prov:Entity`, `prov:Activity`, `prov:wasDerivedFrom`, `prov:wasAttributedTo`. Small vocab, standard. |
| **SKOS** | Core | `owl:imports` | Alias semantics (`skos:exactMatch`, `closeMatch`, `broadMatch`, `narrowMatch`) per Linear D4. |
| **FOAF** | Core | `owl:imports` | `foaf:Agent`, `foaf:Organization`, `foaf:Person` as root for the agent module. |
| **Dublin Core Terms** | Core | `owl:imports` | `dcterms:title`, `dcterms:description`, `dcterms:modified`, `dcterms:license`. Required by DCAT. |

An import manifest will be maintained at
`ontologies/energy-intel/imports-manifest.yaml` so `ontology-curator`
can refresh versions without re-running the extracts.

## Prior art (reference only — not imported)

These sources informed the modeling but are **not** imported or extended.
Tracked here so reviewers can cross-check design decisions.

| Source | What we take | What we leave |
|---|---|---|
| `ontologies/skygest-energy-vocab/` (sevocab) | DCAT-7 shape + Variable/Series/Observation three-tier seam + SKY-316 structural properties | sevocab as a build target — `energy-intel` is a parallel greenfield, not a sevocab extension |
| `agentology/packages/ontology/ontologies/source/skygest-canonical.ttl` | `CanonicalMeasurementClaim` naming, 7-field Series identity, OEO value-class alignment pattern | No upper-ontology alignment (no BFO), no DCAT, no PROV — we add those |
| `skygest-editorial` (schemas in `@skygest/domain/*`) | `Post`, `PodcastEpisode`, `PodcastSegment`, `Expert`, `Publisher` shapes | Narrative / Story / ArgumentPattern / Edition classes (per non-goal #5) |
| Linear "Newsletter & Story Intelligence" project | Architecture Principles 1–7 (Apr 2), Data Intelligence Layer D1–D12 + H-DL-1..8 (Apr 8), Resolution Flow D-A1..A5 (Apr 9), Series/Ontology-Driven Runtime Alignment (Apr 13) | Runtime concerns (Cloudflare Workers, D1 tables, Effect-TS services) — those are ABox consumers, not TBox modeling |

## Stakeholders

| Role | Who | Input |
|---|---|---|
| Product owner + domain expert + sole reviewer | Mepuka Kessy | All decisions, CQ priority, final sign-off on `requirements-approval.yaml` |
| Downstream consumers (future) | Runtime codegen (`skygest-cloudflare/src/domain/generated/`), editorial skill suite (`skygest-editorial/.claude/skills/`), graph-store ABox loader (TBD) | Contract stability: TBox class and property names must match generated TS field names verbatim |

## Use cases

Structured use-case catalog lives at `docs/use-cases.yaml` (Step 1.5). A
preview of the five planned use cases:

| UC ID | Name | Priority |
|---|---|---|
| `UC-001` | Extract a `CanonicalMeasurementClaim` from a Bluesky post that embeds an energy chart | must_have |
| `UC-002` | Resolve a `CanonicalMeasurementClaim` to a `Variable` / `Series` / `Distribution` at multi-grain | must_have |
| `UC-003` | Find all CMCs across experts that reference the same `Variable` (cross-expert join) | must_have |
| `UC-004` | Attribute a `PodcastSegment` to the `Expert` who spoke it and link to any CMC it evidences | should_have |
| `UC-005` | Classify a `Post` by energy `technologyOrFuel` via OEO and return posts covering a topic | should_have |

## Decisions resolved — 2026-04-22 (interview w/ product owner)

All Tier 1 and Tier 2 open questions from the first pass of this scope
were resolved in a follow-up interview. Decisions are recorded here so
that the downstream skills (scout, conceptualizer, architect) can treat
them as closed.

### BFO upper alignment
- **CMC** → `iao:InformationContentEntity` (ICE).
- **Post / MediaAttachment subclasses / PodcastEpisode / PodcastSegment** → `iao:Document` (for Post, Chart, Screenshot, Excerpt) and `iao:InformationContentEntity` (for PodcastEpisode, PodcastSegment).
- **Expert** → strict `foaf:Person` subclass. No `bfo:Role` on the expert side in V0; discourse-roles are represented on `Organization`, not on `Expert`. Team / bot accounts are out of V0 scope.
- **Organization** → `ei:Organization rdfs:subClassOf foaf:Organization` and `rdfs:subClassOf bfo:ObjectAggregate` (BFO 2020).
- **PublisherRole / DataProviderRole** → `bfo:Role` specialisations inhering in `Organization`.

### CMC / Observation details
- **CMC** `owl:disjointWith` **Observation** (Linear D7 tagged union).
- **Observation** retained as a **thin** TBox class in V0 (no CQs hit it; lands as a foundational hook for the future data-ingest lane).
- `ei:assertedValue` range = `rdfs:Datatype` union of `xsd:decimal ∪ xsd:string`.
- `ei:assertedTime` range = `ei:ClaimTemporalWindow` (subclass with `ei:intervalStart`, `ei:intervalEnd`, `rdfs:label`).
- `ei:rawDims` range = `xsd:string` (single JSON literal) in V0.
- **Resolution-state enum DROPPED.** No `ei:ResolutionState` class. Client callers can infer resolution grain from which of the `ei:references*` properties are populated (CQ-010 serves this query).
- **Source-modality enum DROPPED.** Redundant with the media-class discriminator: if a CMC evidences a `Chart`, its modality is chart. Derivable from `ei:evidences` range.
- `ei:references` introduced as an abstract **super-property** over the five concrete `ei:references*` properties (D7).
- `ei:evidences` cardinality on CMC: **1..n** — a CMC may cite both a Post and the Chart / Screenshot it embeds.
- `prov:wasGeneratedBy` annotation on CMC records the extraction activity (full `prov:Activity` individuals deferred to ABox phase).

### Agent layer
- **Expert** = `foaf:Person` subclass, DID-based identity.
- **Publisher** = `PublisherRole` (bfo:Role) borne by Organization — **not** a class.
- **DataProvider** = `DataProviderRole` (bfo:Role) borne by Organization — **not** a class.
- **Organization** = own class with dual parent (`foaf:Organization` + `bfo:ObjectAggregate`).

### Variable — seven-facet deferral
- **Seven-facet Variable identity model from Linear D2 is deferred to V1.** Variable and Series remain in V0 as **thin classes** (IRI + `rdfs:label` + optional `rdfs:comment`); CMCs reference them as opaque join grains. This preserves the cross-expert-join CQs (CQ-006 / CQ-007 / CQ-008) without taking on the facet axiomatisation.
- Reason (from the interview): "variables are our own concept, which we don't model well; I actually don't want that complexity right now."
- Technology classification moves from a Variable facet to a **claim-level** property: `ei:aboutTechnology` on CMC with range `skos:Concept`. Range widens to the imported OEO subtree in a later phase.
- `ei:hasMeasuredProperty`, `ei:hasDomainObject`, `ei:hasStatisticType`, `ei:hasAggregation`, `ei:hasBasis`, `ei:hasUnitFamily`, and `ei:hasTechnologyOrFuel` (as a Variable facet) are **not in V0**.
- Enum classes `ei:StatisticType`, `ei:Aggregation`, `ei:BasisType` are **not in V0**.

### Media layer — expanded per interview
- `ei:MediaAttachment` abstract superclass added.
- Subclasses: `ei:Chart`, `ei:Screenshot`, `ei:Excerpt`, `ei:Image`.
- **Rationale (from interview):** "people very often do a screenshot of an actual report or a news article — we want to be able to resolve those." Screenshot and Excerpt handle the news-article-screenshot, report-excerpt, and quote-screenshot patterns visible across Bluesky and X.
- `Screenshot` has `ei:screenshotOf` (0..1 `xsd:anyURI`) pointing at the external source URL.
- `Excerpt` has `ei:excerptFrom` (0..1 `xsd:anyURI`).
- `ei:presents` range widens from `Chart` to `MediaAttachment`; `ei:evidences` domain widens accordingly.

### Conversation shape
- `Conversation` kept as abstract supertype.
- `SocialThread` modelled via `ei:repliesTo` partial-order (not ordered-list). Reply-trees are the native shape on AT-Protocol and Twitter.
- `PodcastSegment` ordering via `ei:hasSegmentIndex xsd:integer` alongside `ei:partOf`.

### Reasoning / profile
- Profile: **OWL 2 DL** (confirmed; no EL narrowing).
- Default CI reasoner: **HermiT** for validation; ELK permitted as a fast-path iteration reasoner when build time grows.
- **OWL 2 punning allowed** workspace-wide (needed once OEO technology classes are imported and appear as values of `ei:aboutTechnology`).
- SHACL shapes authored in `ontologies/energy-intel/shapes/` by `ontology-architect`; executed by `ontology-validator`.

## Open questions — remaining (non-blocking)

Carried to `ontology-scout` and later phases. Each has a sensible
default captured in this doc; the scout / architect can proceed.

1. **OEO MIREOT seed IRI list.** Concrete seed classes for
   `robot extract --method BOT` → `imports/oeo-subset.ttl`. Scout output.
   Target subtrees: energy-technology root, energy-carrier root,
   aggregation-type, temporal-resolution, quantity-kind. **Deferred to
   scout phase per user directive**: "capture the semantic breadth of
   energy technology... that's gonna come later." V0 uses `skos:Concept`
   as the placeholder range for `ei:aboutTechnology`.
2. **W3ID registration.** `https://w3id.org/energy-intel/` needs a
   registration PR against `perma-id/w3id.org`, or we switch to
   `https://vocab.skygest.io/` to match Linear D3's Skygest-controlled-domain
   strategy. Not blocking V0 TBox authoring; resolve before first release.
3. **DCAT Agent unification.** `dcat:Agent` vs `foaf:Agent` vs
   `ei:Organization` — declare as `owl:equivalentClass` or align via
   `rdfs:subClassOf`? Scout surveys the alignment literature and recommends.
4. **Unit model depth.** Reuse `qudt:Unit` individuals only, or also
   `qudt:QuantityKind` classes? Scout recommendation.
5. **`schema.org` export codec** (Linear D6) — architect-scope or
   curator-scope ticket? Resolve at architect hand-off.
6. **JSON-LD `@context`** generation — ontology-native or LinkML
   projection? Resolve at architect hand-off.
7. **Graph-store selection** for eventual ABox — GraphDB / Stardog /
   Fuseki / Oxigraph. Impacts which SPARQL 1.1 extensions we can rely on
   for SHACL and path queries. Deferred to first ABox workstream.
8. **Narrative / Story / ArgumentPattern** revisit cadence — after N
   months of editorial use, re-run `ontology-requirements` with updated
   stakeholder input. No action in V0.

## Definition of done (for this scope phase)

- [x] `docs/scope.md` exists with all three Step 0 gate verdicts recorded
- [ ] `docs/use-cases.yaml` lists `UC-001` through `UC-005` with actor,
      goal, preconditions, main flow, postconditions, related CQs
- [ ] `docs/competency-questions.yaml` formalizes Must-Have CQs (Step 5)
- [ ] `docs/cq-quality.csv` scores every CQ on the six Step 2.5 criteria
- [ ] `docs/pre-glossary.csv` extracts candidate terms from every CQ
- [ ] `tests/cq-*.sparql` preflights via `prepareQuery` on every
      Must-Have CQ (Step 7.5)
- [ ] `docs/traceability-matrix.csv` closes the chain:
      stakeholder-need → use case → CQ → term → test
- [ ] `docs/requirements-approval.yaml` signed with `reviewer: kokokessy@gmail.com`,
      `reviewed_at: 2026-04-22`, `cq_freeze_commit: <sha>`
