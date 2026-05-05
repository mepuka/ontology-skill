# Scope — `energy-intel` Ontology, V2 (Editorial Extension)

**Short name:** `energy-intel` (prefix `ei:`, TBox namespace `https://w3id.org/energy-intel/`)
**Predecessor:** v0.2.0 (V1 released 2026-04-27, audit at [release/release-audit.yaml](../release/release-audit.yaml))
**Date:** 2026-05-04
**Product owner / sole reviewer:** Mepuka Kessy (`kokokessy@gmail.com`)
**Source plan (canonical):** [`/Users/pooks/Dev/skygest-cloudflare/docs/plans/2026-05-04-editorial-ontology-slice.md`](file:///Users/pooks/Dev/skygest-cloudflare/docs/plans/2026-05-04-editorial-ontology-slice.md) — locked decisions Q1–Q3 + S1–S5, pressure-tested by three multi-agent design reviews before this requirements phase.
**Handoff:** [`docs/HANDOFF-2026-05-04-editorial-extension.md`](../../../docs/HANDOFF-2026-05-04-editorial-extension.md)
**Inherits unchanged from V0/V1:** modelling assumptions in [scope.md](scope.md) and [scope-v1.md](scope-v1.md), conceptual model in [conceptual-model.md](conceptual-model.md), V0+V1 CQs CQ-001..CQ-019, V0+V1 use cases UC-001..UC-008.

This document captures the V2 **delta** only. V1 is the baseline; everything not restated here is unchanged.

---

## Step 0 — scope gate

| Gate | Verdict | Evidence |
|---|---|---|
| Scope fit | **approved** | V2 lifts a workflow's central unit (`Narrative`) into the ontology spine, replaces a hand-rolled 30-topic / 92-concept catalog with OEO-derived IRIs + a small Skygest supplement set, and adds two SKOS controlled vocabularies (argument-pattern, narrative-role). All four are vocabulary / axiom changes — squarely an ontology problem (shared vocabulary, downstream codegen contract, reasoning over a reified n-ary relation, SHACL constraints over membership cardinality). |
| Retrofit check | **false** | No editorial-extension modelling has started inside `ontologies/energy-intel/`. The current `modules/concept-schemes/technology-seeds.ttl` is V1's hand-seeded SKOS scheme that V2 retires; that's V1 release output, not V2 retrofit. Pre-ratified design decisions in source plan §3 came from a multi-agent design review that pressure-tested the design *before* this requirements phase — they enter V2 through scope / conceptualizer, not as retrofit modelling. No `docs/requirements-retrofit-note.md` needed. |
| Stakeholder availability | **true** | Single-stakeholder model continues; product owner is `kokokessy@gmail.com`. All Must-Have CQs reviewable in this session. |

---

## Purpose + framing

V2 closes the largest editorial-side gap remaining after V0 + V1:

1. **Editorial extension — Narrative, NarrativePostMembership, ArgumentPattern, NarrativeRole.**
   `skygest-editorial`'s central unit `Story` becomes the ontology entity `ei:Narrative`. The narrative ↔ post relationship is reified as `ei:NarrativePostMembership` carrying a role qualifier — required because four role-named predicates (`leadPost` / `supportingPost` / `counterPost` / `contextPost`) would smuggle storage state into predicate names (System Blueprint anti-pattern), break the SHACL closed-shape constraint, and not absorb future first-class qualifier storage cleanly. The 7 stable argument patterns become a SKOS controlled vocabulary `ei:concept/argument-pattern`; the 4 narrative roles become a SKOS controlled vocabulary `ei:concept/narrative-role`. Decision Q1 / S2 / S4 / §3.3 of source plan, ratified by multi-agent review.

2. **Topic vocabulary cutover — OEO IRIs + Skygest supplement set.**
   Retire `canonicalTopicOrder` and `conceptToCanonicalTopicSlug` (in `skygest-cloudflare/src/ontology/canonical.ts`) as runtime authority. Replace with two layers: (1) OEO IRIs where they cleanly fit the editorial granularity contract (most fuels, most technologies, most carriers), and (2) local `ei:concept/...` supplement IRIs where OEO has no clean editorial equivalent (umbrella themes like `grid-and-infrastructure`, `energy-justice`, `data-center-demand`). Decision Q2 of source plan.

3. **OEO topic subset rebuild from `oeo-full.owl`.**
   The current `imports/oeo-{technology,carrier}-subset-fixed.ttl` files (V1 BFO-stripped subsets) are insufficient — they miss solar (`OEO_00010427`), wind (`OEO_00010424`), nuclear (`OEO_00010439`), and storage (`OEO_00020366`) technology classes that the editorial vocabulary needs. V2 rebuilds the topic subset from `imports/oeo-full.owl` against the 41-IRI seed list in the handoff §"OEO topic subset rebuild" and writes the result to `imports/oeo-topic-subset.ttl`. The existing V1 subsets stay in place (used for upper alignment in `aboutTechnology`); V2 adds a parallel topic subset.

4. **Retraction of V0 non-goal #5.**
   V0 scope.md non-goal #5 ("Narrative / Story / Arc / ArgumentPattern / Edition classes — editorial process is in active flux") is **explicitly retracted by V2** (see § Non-goal retraction below). V1 inherited it as carry-forward (V1 scope-v1.md non-goal #7) — V2 supersedes that carry-forward. The flux has stabilised: source plan §1 captures the locked decisions plus a ratified review of risks and acceptance criteria, and the editorial corpus has crystallised into a stable 5-arc / 8-narrative / 7-pattern shape.

V2 stays TBox-only. ABox is still deferred. V2 ships as **v0.3.0** (minor version bump, additive — V0+V1 CQs continue to pass).

---

## Non-goal retraction

### V0 scope.md non-goal #5 — RETRACTED in V2

**Original (V0 scope.md):**
> "5. Narrative / Story / Arc / ArgumentPattern / Edition classes. The editorial process is in active flux and these concepts are better captured as *aggregations over curated CMCs* later (via skill `ontology-curator` or a follow-on module). *Rationale:* locking in editorial process classes now would ossify a workflow that is still being iterated in `skygest-editorial`."

**V0 carry-forward (V1 scope-v1.md non-goal #7):**
> "Narrative / Story / ArgumentPattern / Edition classes. Carry-forward V0 non-goal; editorial workflow still in flux."

**V2 status:** **RETRACTED for `Narrative`, `NarrativePostMembership`, `ArgumentPattern`, and `NarrativeRole`.** `Edition` and `Story` (as separate from Narrative) remain non-goals in V2.

**Retraction rationale:**

1. **The workflow has crystallised.** Editorial corpus audit (source plan §1, F1 audit) shows: 5 arcs (`data-center-grid-demand`, `electricity-markets-high-renewables`, `emissions-accounting-policy`, `global-renewables-growth`, `nuclear-economics`), 8 nested-layout stories (all stems globally unique under `narratives/{arc-slug}/stories/{story-stem}.md`), 7 stable argument patterns (`deployment-milestone`, `emergent-technology-bulletin`, `geographic-energy-project`, `grid-snapshot`, `learning-curve`, `methodological-critique`, `structural-economic-analysis`), 4 stable post roles (`lead`, `supporting`, `counter`, `context`). The shape has been stable across the last several editorial cycles. The "active flux" risk that justified the V0 non-goal is no longer present for these four concepts.

2. **Three multi-agent design reviews have pressure-tested the design.** The locked decisions Q1, Q2, Q3, S1, S2, S4, S5 in source plan §1 are the output of the BFO/OEO modeling review, the system integration review, and the migration safety review. Critical findings already baked into the design: Narrative re-parented to `iao:Document` (not abstract `iao:InformationContentEntity`) to match existing `Post`/`PodcastEpisode` placement; `ArgumentPattern` shifted from `owl:Class` + ABoxed individuals to a `skos:ConceptScheme` matching the `EnergyTopic` pattern; Narrative→Post relationships use a reified n-ary relation rather than 4 role-named predicates.

3. **Downstream consumers are blocked on this shape.** `skygest-cloudflare/packages/ontology-store/` codegen and `skygest-editorial`'s `hydrate-story` / `import-narratives` CLIs need a stable contract to migrate against. Continuing to defer this would calcify the V1 hand-rolled `canonicalTopicOrder` runtime catalog, which is the largest piece of "ontology-shaped TS that is not actually ontology" in the consuming repo.

4. **`Edition` and `Story` (separate from Narrative) remain non-goals.** Edition (newsletter compile) is genuinely still iterating; the source plan §2 keeps it explicitly out of scope. `Story` is collapsed *into* `Narrative` rather than being its own entity — Q1 of source plan ("Story → ontology Narrative; arc index stays filesystem"). So this retraction does not reopen those.

---

## In-scope (V2 additions to the four-module TBox)

### 1. Editorial module (new) — `modules/editorial.ttl`

| Item | What lands |
|---|---|
| New class | `ei:Narrative` ⊑ `iao:0000310` (`iao:Document`). A written editorial unit *about* the events it narrates; not the events themselves. Matches the existing `Post` and `PodcastEpisode` placement in `modules/media.ttl`. |
| New class | `ei:NarrativePostMembership` ⊑ `iao:0000310`. A membership record is an information artifact — it is the storage shape for the role-qualified narrative→post link. One individual per `(narrative, post)` pair. |
| New object property | `ei:hasNarrativePostMembership` (Narrative → NarrativePostMembership, many). Domain `ei:Narrative`, range `ei:NarrativePostMembership`. |
| New object property | `ei:memberPost` (NarrativePostMembership → Post, functional 1). `owl:FunctionalProperty`, `owl:ObjectProperty`. Domain `ei:NarrativePostMembership`, range `ei:Post`. |
| New object property | `ei:memberRole` (NarrativePostMembership → skos:Concept, functional 1). `owl:FunctionalProperty`, `owl:ObjectProperty`. Range constrained by SHACL to concepts in scheme `ei:concept/narrative-role`. |
| New object property | `ei:narrativeMentionsExpert` (Narrative → Expert, many). Auto-derived from contained posts on import; reviewable via MCP. |
| New object property | `ei:narrativeAppliesPattern` (Narrative → skos:Concept, 0..1). Range constrained by SHACL to concepts in scheme `ei:concept/argument-pattern`. Mirrors current `Story.argument_pattern`. |
| New object property | `ei:narrativeAboutTopic` (Narrative → EnergyTopic, many). Topic now = OEO IRI ∪ supplement IRI. |
| Reused predicate | `skos:related` between `skos:Concept` instances in `ei:concept/argument-pattern` — lifts the phantom `related_patterns` from `BuildGraph.ts` without minting a custom predicate. |

### 2. Concept-scheme modules (new) — `modules/concept-schemes/`

| Item | What lands |
|---|---|
| `concept-schemes/argument-pattern.ttl` | New SKOS scheme `ei:concept/argument-pattern`. Declares 7 `skos:Concept` instances: `deployment-milestone`, `emergent-technology-bulletin`, `geographic-energy-project`, `grid-snapshot`, `learning-curve`, `methodological-critique`, `structural-economic-analysis`. Each with `skos:prefLabel`, `skos:definition`, optional `skos:related`, optional `skos:editorialNote` (for `status: draft` / `active` annotations). Status field uses `owl:deprecated` for any `deprecated` patterns plus `skos:editorialNote` for `draft` / `active` annotations — matches the existing pattern from V1 `EnergyTopic` SKOS scheme. |
| `concept-schemes/narrative-role.ttl` | New SKOS scheme `ei:concept/narrative-role`. Declares 4 `skos:Concept` instances: `lead`, `supporting`, `counter`, `context`. Each with `skos:prefLabel` and `skos:definition`. |
| `concept-schemes/oeo-topics.ttl` | New SKOS scheme(s) — replaces V1 `concept-schemes/technology-seeds.ttl` as the runtime topic source. Declares accepted OEO IRIs + Skygest supplement individuals. **Per-scheme split (single vs. split + aggregator) is decided in Phase 2 — see Open Question 1 below.** Each `skos:Concept` carries `skos:prefLabel`, `skos:definition`, optional `skos:exactMatch` / `skos:closeMatch` to OEO IRIs where the relationship is explicit, `skos:hasTopConcept` from the scheme, and `skos:notation` carrying the legacy `topic_slug` for migration-period queryability (recommended per source plan §9 Q6). |

### 3. OEO topic subset rebuild — `imports/oeo-topic-subset.ttl`

| Item | What lands |
|---|---|
| Source | `imports/oeo-full.owl` (~100MB). |
| Method | `robot extract --method BOT` against the 41-IRI seed list in handoff §"OEO topic subset rebuild" and source plan §3.4. After extraction, the BFO+RO-stripping pass (per existing `imports/upper-axiom-leak-terms.txt` and `imports/bfo-terms-to-remove.txt`) produces the runtime-importable subset. |
| Validator | SPARQL ASK that fails if any IRI in `oeo-topic-subset.ttl` resolves to `owl:NamedIndividual` (excludes inventory bookkeeping records, e.g. `OEO_00010048`). Lives at `tests/cq-editorial-granularity.sparql`. |
| Granularity contract (every accepted topic IRI MUST satisfy ALL three) | (a) Is `owl:Class` (preferred) **or** `skos:Concept` in an editorial supplement scheme. **Never `owl:NamedIndividual`.** (b) Sits at editorial granularity: technology-class > carrier-class >> material/installation/inventory-record. A "topic" describes a kind of thing, not a specific instance. (c) Has exactly one canonical IRI per editorial slug. Alternates appear as `skos:closeMatch` annotations, never as parallel topic memberships. |

### 4. Editorial supplement IRIs (Local / Mixed rows)

Skygest-coined `ei:concept/...` supplement IRIs that exist because OEO has no clean editorial equivalent. All declared in `concept-schemes/oeo-topics.ttl` (or whichever scheme split Phase 2 chooses):

`ei:concept/distributed-energy`, `ei:concept/grid-and-infrastructure`, `ei:concept/electrification`, `ei:concept/energy-efficiency`, `ei:concept/data-center-demand`, `ei:concept/energy-policy`, `ei:concept/energy-markets`, `ei:concept/energy-finance`, `ei:concept/energy-geopolitics`, `ei:concept/critical-minerals`, `ei:concept/climate-and-emissions`, `ei:concept/carbon-markets`, `ei:concept/environment-and-land-use`, `ei:concept/energy-justice`, `ei:concept/sectoral-decarbonization`, `ei:concept/workforce-and-manufacturing`, `ei:concept/research-and-innovation`, optionally `ei:concept/energy-storage` and `ei:concept/biomass` (only if the editorial umbrella needs broader scope than OEO offers — Phase 2 decision).

Each supplement gets `skos:prefLabel`, `skos:definition`, optional `skos:exactMatch` / `skos:closeMatch` to OEO IRIs, `skos:hasTopConcept` from the scheme, and `skos:notation` for the legacy `topic_slug`.

### 5. SHACL editorial shapes — `shapes/editorial.ttl`

| Item | What lands |
|---|---|
| `ei:NarrativeShape` | Closed shape for `ei:Narrative`; required fields per `Story`-derived schema. |
| `ei:NarrativePostMembershipShape` | `sh:qualifiedMaxCount 1` per `(Narrative, Post)` pair — at most one membership record per pair. |
| Lead-uniqueness warning | SHACL warning (not error): at most one `NarrativePostMembership` with `memberRole = ei:concept/narrative-role/lead` per Narrative. Warning, not error, because draft narratives may legitimately be in flux. |
| Topic-IRI granularity validator | Every `ei:narrativeAboutTopic` value MUST resolve to an `owl:Class` (in OEO scheme) or `skos:Concept` (in supplement scheme); MUST NOT be a `owl:NamedIndividual`. |

### 6. Narrative identity rule

Deterministic Narrative IRI = `https://w3id.org/energy-intel/narrative/{story-stem}`. Story stem is the filename without extension; arc directory does NOT enter the IRI; duplicate stems are import errors. Per source plan §S5.

Deterministic NarrativePostMembership IRI = `https://w3id.org/energy-intel/narrative/{story-stem}/membership/{post-uri-hash}`. Conceptualizer's design call on the exact derivation; the constraint is that it must be derivable from `(narrativeIri, postUri)` without runtime ambiguity. Phase 2 deliverable.

### 7. Acceptance suite — V2 CQs

CQ-N1..CQ-N8 cover the editorial extension; CQ-T1..CQ-T2 cover topic resolution; granularity contract is encoded as `cq-editorial-granularity.sparql`. See [`competency-questions-v2.yaml`](competency-questions-v2.yaml).

### Sign-off cadence

V2 ships as **v0.3.0** (minor version bump, additive — V0+V1 CQs continue to pass). Curator releases tag, refreshes diff against v0.2.0 baseline.

---

## Out-of-scope (V2 non-goals)

Restated for clarity. Some are V0+V1 carry-forwards; some are explicit V2 deferrals from source plan §2.

1. **Edition (newsletter compile) as an ontology entity.** Deferred. No TTL.
2. **EditorialPick.** Stays a D1 row + future `entity_link_evidence` row with `assertion_kind: "picked"` on the cloudflare side; not an ontology entity.
3. **PostAnnotation.** Filesystem markdown only; not an ontology entity.
4. **Trigger as a typed enum or class.** Stays free text on `Narrative`.
5. **`Narrative.entities` and `Narrative.data_refs` as typed edges.** Stay as opaque string arrays until the Post→Entity resolver workflow lands (next slice).
6. **Narrative arc as an ontology entity.** Per S2: a `Narrative` carries no `arc` field. The directory it lives in IS the arc. Moving the file moves the arc. No DB column, no frontmatter field, no `ei:Arc` class. *(Future-self check addressed in source plan §9 Q1: future Arc as `iao:0000310` with `ei:hasNarrativePart` would integrate without breaking changes; not blocking V2.)*
7. **Provenance taxonomy (editorial / hydratable / derived / cache) as a first-class meta-property.** Captured in PROV-O annotations only when convenient; not enforced.
8. **Reindex propagation runtime.** Slice 4+.
9. **Post→Entity linking workflow.** Next slice (depends on V2 landing).
10. **Filesystem migration of legacy flat narratives.** `/skygest-editorial/stories/story-*.md` archival is the cloudflare-side / editorial-side concern (Phase 7 step 1); not the ontology's concern.
11. **Carry-forward V1 non-goals (unchanged):** Seven-facet Variable identity model (still V2+ for the *data* layer; this V2 slice is *editorial* only), Expert subrole taxonomy, SHACL coverage backfill for the seven `intent: validate` properties not yet shaped, full QUDT vocabulary, OEO Process / Observation / QuantityValue machinery, ABox individuals, schema.org export codec, JSON-LD `@context` generation strategy.

---

## Constraints

| Constraint | Value | Source |
|---|---|---|
| Upper ontology | BFO (ISO 21838-2) | unchanged from V0 |
| OWL profile | OWL 2 DL (with punning) | unchanged from V0+V1; V2 SKOS schemes for argument-pattern and narrative-role do not introduce new punning surface (concepts are individuals only, not used as classes) |
| Reasoner | HermiT (release gate); ELK fast-path | unchanged |
| TBox namespace | `https://w3id.org/energy-intel/` | unchanged |
| Version IRI for V2 | `https://w3id.org/energy-intel/v2/2026-XX-XX` | curator stamps on release |
| Backwards compat | V0 CQs CQ-001..CQ-014 + V1 CQs CQ-015..CQ-019 must still pass under V2 model | hard gate at validator |
| Build regime | Standalone POD (no ODK) | unchanged |
| Narrative IRI form | `https://w3id.org/energy-intel/narrative/{story-stem}` (deterministic) | source plan §S5 |
| NarrativePostMembership IRI form | `https://w3id.org/energy-intel/narrative/{story-stem}/membership/{post-uri-hash}` (deterministic from `(narrativeIri, postUri)`) | source plan §3.3 + Phase 2 design call |
| Topic IRI source | OEO IRIs ∪ supplement IRIs in `ei:concept/...` namespace | source plan Q2 |
| Topic granularity | `owl:Class` or `skos:Concept`; never `owl:NamedIndividual` | source plan §3.4 + this scope §"Granularity contract" |

---

## V0 + V1 CQ revalidation guarantee

V2 must NOT break the V0+V1 acceptance suite (CQ-001..CQ-019). The risk surface is small:

- V2 adds a new module (`editorial.ttl`) and three new SKOS schemes; it does not modify any V0+V1 class or property.
- The retired `concept-schemes/technology-seeds.ttl` (V1) is replaced by `concept-schemes/oeo-topics.ttl` — this affects only `ei:aboutTechnology`'s value-set surface. CQ-013, CQ-014, CQ-015 (which walk `ei:aboutTechnology/(skos:broader|rdfs:subClassOf)*`) must continue to pass against the new topic subset. This is a fixture refresh, not a structural change.

Validator's L4 pytest must report **14/14 V0 CQs PASS** + **5/5 V1 CQs PASS** + **all V2 CQs PASS** before sign-off.

---

## Reused external ontologies — V2 changes

V2 does not add any new top-level imports. It reorganises the OEO subset surface:

| Ontology | V1 status | V2 status |
|---|---|---|
| **OEO** (Open Energy Ontology) | `owl:imports` two BFO-stripped subsets (`imports/oeo-{technology,carrier}-subset-fixed.ttl`) | Adds parallel topic subset `imports/oeo-topic-subset.ttl` rebuilt from `imports/oeo-full.owl` against the 41-IRI editorial topic seed list. V1 subsets stay (used for `ei:aboutTechnology` upper alignment); V2 subset is the runtime topic source. |
| BFO 2020 | full import | unchanged |
| IAO v2026-03-30 | MIREOT | unchanged (already supplies `iao:0000310` `iao:Document` parent for V2's `ei:Narrative` and `ei:NarrativePostMembership`) |
| QUDT 2.1 | narrow `qudt:Unit` extract + `qudt:QuantityKind` | unchanged |
| DCAT 3 | full import | unchanged |
| SKOS | full import | unchanged (V2 declares two new schemes against existing SKOS vocabulary) |
| PROV-O / FOAF / DCT | full import | unchanged |

Imports manifest is regenerated by curator after architect lands the new modules.

---

## Open questions — V2 (carried to conceptualizer)

These flow to Phase 2; each has a sensible default.

1. **SKOS scheme split for topic vocabulary (source plan §9 Q7).** Single `ei:concept/topic` scheme, OR `ei:concept/oeo-topic` + `ei:concept/editorial-supplement` + aggregator? **Recommendation:** split + aggregator, because claiming OEO IRIs as members of a Skygest-namespaced `ei:concept/...` scheme they don't natively belong to is semantically off. Document the choice in `conceptual-model-v2.md` and `topic-vocabulary-mapping.md`.
2. **Signal preservation under umbrella collapse (source plan §9 Q3).** The migration map collapses 92 leaf concepts into 30 umbrellas, then re-distributes to OEO + supplements. Does any current consumer in `skygest-cloudflare` rely on the *original* leaf concept granularity? **Action:** flag in `requirements-approval-v2.yaml` as a question for the cloudflare side. If yes, Phase 2 `topic-vocabulary-mapping.md` must preserve the leaf concept as well as the umbrella.
3. **`attach_post_to_narrative` bulk shape (source plan §9 Q5).** Should the import batch accept multiple posts per narrative in one transaction? **Recommendation:** ontology should not constrain it either way. Note in `conceptual-model-v2.md` that the cardinality of `ei:hasNarrativePostMembership` is `many` and order is not preserved. Cloudflare side decides batch shape.
4. **Slug system co-residence post-migration (source plan §9 Q6).** Should the legacy `topic_slug` column drop or stay indefinitely? **Recommendation:** annotate every supplement IRI with `skos:notation` carrying the legacy slug, so the migration map is queryable from the ontology itself for at least one release window. Cloudflare side decides drop date.
5. **NarrativePostMembership IRI derivation.** `https://w3id.org/energy-intel/narrative/{story-stem}/membership/{post-uri-hash}` is the recommended shape. Conceptualizer's design call on hash function (sha256 truncated to 16 chars? base32 of full sha256?). Constraint: must be deterministic from `(narrativeIri, postUri)` without runtime ambiguity, must round-trip to the same IRI on re-import, and must not collide for distinct `(narrativeIri, postUri)` pairs at any reasonable scale.

These are tracked under `handoff_to_conceptualizer.blocking_questions` in `requirements-approval-v2.yaml`.

---

## Definition of done (this scope phase)

- [x] `docs/scope-v2.md` exists with Step 0 verdicts and explicit retraction of V0 non-goal #5
- [ ] `docs/use-cases-v2.yaml` adds V2 use cases (UC-009 .. UC-013)
- [ ] `docs/competency-questions-v2.yaml` adds V2 CQs (CQ-N1..CQ-N8, CQ-T1, CQ-T2)
- [ ] `docs/cq-quality-v2.csv` scores every V2 CQ on the six Step 2.5 criteria
- [ ] `docs/pre-glossary-v2.csv` extracts V2 candidate terms
- [ ] `tests/cq-editorial-{N1..N8,T1,T2,granularity}.sparql` preflight via `prepareQuery`
- [ ] `tests/cq-test-manifest.yaml` updated to include V2 entries
- [ ] `docs/traceability-matrix-v2.csv` closes need → use case → CQ → term → test for V2
- [ ] `docs/requirements-approval-v2.yaml` signed with reviewer + ISO date + cq_freeze_commit SHA
