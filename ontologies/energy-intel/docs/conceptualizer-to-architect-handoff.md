# Conceptualizer → Architect Handoff — `energy-intel`

**From:** `ontology-conceptualizer` (2026-04-22)
**To:** `ontology-architect`
**Inputs conceptualizer consumed:** scope.md / CQs / pre-glossary @ `f6d025d`, reuse-report / imports-manifest / odp-recommendations / scout handoff @ `b4f1bf2`.
**Conceptualizer deliverables landed:**
- `docs/conceptual-model.md` — per-module classes, BFO leaves, module placement, intent, ODP citations, modelling resolutions.
- `docs/taxonomy.md` — hierarchy per module with BFO roll-up at every node + MI review.
- `docs/property-design.md` — 30+ properties with domain, range, cardinality, characteristics, RO super-property, intent (infer / validate / restrict / annotate).
- `docs/bfo-alignment.md` — BFO decisions + ambiguity register (two ≥ 2 rows signed by reviewer).
- `docs/axiom-plan.md` — CQ-by-CQ axiom plan in Manchester-syntax sketch; foundational axioms section; CQ coverage map (14/14).
- `docs/shacl-vs-owl.md` — ten OWL constraints, ten SHACL constraints, boundary cases discussed.
- `docs/anti-pattern-review.md` — 16 patterns reviewed; 0 `block`, 0 unresolved `warn`.

---

## Ten crisp bullets for architect to action

1. **Axiomatise in module order: `agent` first, then `media`, then `measurement`, then `data`.** Rationale: `agent` is the smallest (4 classes + 1 Role-inheres-in pattern), contains no cardinality restrictions beyond role-bearer, and unblocks `media` (Post needs Expert for `ei:authoredBy exactly 1`). `media` unblocks `measurement` (CMC needs `ei:EvidenceSource` for CQ-009). `data` is mostly imports + 2 extension properties. See `conceptual-model.md § 0` for layer/module map.

2. **OEO seed-IRI verification is your first blocking task.** Scout provisional candidates (in `imports-manifest.yaml` + `scout-to-conceptualizer-handoff.md § bullet 5`):
   - Technology root: `OEO_00000011` (energy converting component) **OR** `OEO_00010385` (energy transformation function).
   - Carrier root: `OEO_00020039` (energy carrier).
   - Aggregation root: `OEO_00140068` (aggregation type).
   Before `robot extract`, run `robot query` against OEO v2.11.0 to:
   - Confirm each IRI exists.
   - Confirm each label matches (scout flagged that `OEO_00000030` in the original scope.md Open q #1 was wrong — it is "oil power unit").
   - Measure subtree sizes (scout gave rough upper bounds: technology 150–400, carrier 20–60, aggregation 5–20). Abort extract if technology > 400.
   Log verified IRIs + label + size in `imports-manifest.yaml` rows for each OEO subset. This is architect's task, not conceptualizer's — confirmed.

3. **Hand-seed the `ei:TemporalResolution` SKOS ConceptScheme per ODP F.1 (odp-recommendations.md § F.1).** Five concepts: hourly, daily, monthly, quarterly, annual. File path: `modules/concept-schemes/temporal-resolution.ttl` (per `imports-manifest.yaml` row `ei-temporal-resolution-v0`). Use `skos:ConceptScheme`, `skos:topConceptOf`, `skos:inScheme`, and (optionally) an `owl:DisjointUnion` for reasoner-visible covering. ODP F.1's axiom sketch is in `odp-recommendations.md`; no conceptualizer-side boilerplate to add.

4. **Introduce the named abstract class `ei:EvidenceSource`** before axiomatising CMC. Rationale + Manchester sketch: `conceptual-model.md § 8.1`, `property-design.md § 6`, `axiom-plan.md § Foundational axioms`. Three asserted subclasses: `ei:Post`, `ei:MediaAttachment`, `ei:PodcastSegment`. All pairwise disjoint. `ei:evidences rdfs:domain ei:EvidenceSource`. CQ-009 invariant becomes `CMC SubClassOf (inverse ei:evidences) min 1 ei:EvidenceSource`.

5. **Re-parent the media classes per the IAO corrections** — this is LOCKED upstream but worth restating:
   - `ei:Chart`, `ei:Screenshot`, `ei:GenericImageAttachment` → `iao:Image` (IAO_0000101).
   - `ei:Excerpt` → `iao:TextualEntity` (IAO_0000300). **Verified 2026-04-22 via OLS4 v2: IAO_0000300 is active, not deprecated, label "textual entity".** Use it; no fallback needed.
   - `ei:Post`, `ei:PodcastEpisode` → `iao:Document` (IAO_0000310).
   - `ei:PodcastSegment`, `ei:MediaAttachment`, `ei:Conversation`, `ei:EvidenceSource` → `iao:InformationContentEntity` (IAO_0000030) direct.
   See `taxonomy.md § 6.2` for the copy-paste parent-path table.

6. **SHACL shapes to draft first (before CQ SHACL shapes):**
   - **S-1 DID-scheme URI** on `ei:authoredBy` values (`did:plc:...` / `did:web:...` regex).
   - **S-2 JSON-parseable `ei:rawDims`**.
   - **S-3 cross-property interval check** `ei:intervalEnd >= ei:intervalStart` when both present — SPARQL-based SHACL constraint.
   - **CQ-009 SHACL companion** — `sh:targetClass ei:CanonicalMeasurementClaim ; sh:property [ sh:path [ sh:inversePath ei:evidences ] ; sh:minCount 1 ; sh:class ei:EvidenceSource ]`. Paired with the OWL invariant (defense in depth for closed-ABox validation).
   Full shape list: `shacl-vs-owl.md § 2`. File target: `ontologies/energy-intel/shapes/energy-intel-shapes.ttl`.

7. **ODP boilerplate to apply verbatim:**
   - **F.2 Role pattern:** `ei:PublisherRole SubClassOf bfo:Role, (BFO:0000052 some ei:Organization)` (same for `ei:DataProviderRole`). Single existential on `inheres_in`. No equivalentclass axioms (keep primitive).
   - **F.3 Information realization:** CQ-009's `min 1` on inverse of `ei:evidences` to `ei:EvidenceSource` is the pattern's hard invariant. See `axiom-plan.md § CQ-009` for Manchester + Turtle forms.
   - **F.4 Participation:** binary-shortcut form in V0 (`ei:authoredBy`, `ei:spokenBy`). Full reified form is V1.
   - **F.5 Part-whole:** `ei:partOfEpisode rdfs:subPropertyOf BFO:0000050` — do NOT redeclare Transitive locally; inherit from `BFO:0000050`.

8. **OWL 2 punning for `ei:aboutTechnology`:** range stays `skos:Concept` in V0. When OEO MIREOT subset lands, OEO technology classes appear as values via punning. Architect must verify HermiT accepts the punned graph (see `anti-pattern-review.md § Pattern 16`). If HermiT misbehaves, fallback is to materialise OEO technology classes as plain SKOS individuals (re-target the MIREOT extract as a `skos:broader` chain, not a class hierarchy).

9. **Rename `ei:partOf` → `ei:partOfEpisode` now** (property-design.md § 8). Avoids a future refactor when a second part-of relation (e.g., segment-of-transcript) lands. Scope of change: the property declaration + one SubClassOf restriction. Architect applies in the `media` module first pass.

10. **Profile lock: OWL 2 DL.** HermiT is the reasoner for profile-DL gates; ELK is permitted for fast-path subsumption only (ELK cannot handle qualified cardinality, inverse expressions, or datatype unions — axioms the plan uses throughout). Scope § Reasoning confirms this. Axiom-plan.md § Profile declaration spells out the DL-forcing axioms.

---

## What you do NOT need from conceptualizer

- **OEO class-IRI resolution.** Scope-locked as architect's job.
- **Full Turtle draft.** axiom-plan.md is Manchester-syntax sketches; you translate to ROBOT templates / rdflib / OWLAPY as you prefer.
- **W3ID PR.** Scope Open q #2; curator-scope, not architect blocker.
- **JSON-LD context.** Scope Open q #6; post-architect concern.

---

## Loopback paths (if you hit an issue)

- **`bfo_misalignment`** → back to conceptualizer (bfo-alignment.md owns the placement; reviewer signoff required to change).
- **`closure_gap`** → back to conceptualizer (closure intent is a conceptualization decision; revisit `axiom-plan.md § CQ coverage map`).
- **`anti_pattern`** → back to conceptualizer (anti-pattern scan is owned here; update `anti-pattern-review.md`).
- **OEO seed-verification fails** → back to `ontology-scout` (re-investigate OEO v2.11.0 class labels; not conceptualizer's lane).
- **HermiT fails on punning** → tag in a design-decision note; conceptualizer + architect co-resolve (punning workspace-wide was ratified by product owner; changing it reopens scope).

---

## Checklist (for you to tick off at your end)

- [ ] OEO seed-IRI verification run; `imports-manifest.yaml` updated.
- [ ] Hand-seeded `ei:TemporalResolution` ConceptScheme in place.
- [ ] `ei:EvidenceSource` abstract class declared; Post/MediaAttachment/PodcastSegment subclassed.
- [ ] All foundational disjointness axioms from `axiom-plan.md § Foundational axioms` written.
- [ ] Agent module axiomatised (`rdfs:subClassOf`, role-inheres-in).
- [ ] Media module axiomatised (IAO re-parents applied, MediaAttachment subclasses disjoint).
- [ ] Measurement module axiomatised (CMC disjoint Observation, `ei:references*` cardinalities, CQ-009 invariant).
- [ ] Data module axiomatised (`ei:hasSeries`, `ei:publishedInDataset` inverse declaration).
- [ ] Bridge file authored by mapper skill (prov-foaf-bridge.ttl); Step 3.5 safety gate run.
- [ ] SHACL shapes file seeded with the four "first" shapes from bullet 6.
- [ ] `robot reason --reasoner hermit` passes on merged TBox.
- [ ] `robot report` passes; no unexpected errors (warnings OK if documented).
- [ ] Every CQ's fixture (`tests/fixtures/cq-*.ttl`) built and its SPARQL returns the expected shape per `competency-questions.yaml`.

---

## Confidence note

Everything above is derived from frozen inputs (scope @ f6d025d, scout @ b4f1bf2) and the ratified decisions in the skill prompt. No silent scope edits. Three items the conceptualizer could NOT lock:

1. **OEO seed IRI** — explicitly architect-scope; conceptualizer flagged scout's provisional list for architect verification.
2. **`ei:Image` rename** — resolved 2026-04-22; class is now `ei:GenericImageAttachment`. No architect decision needed.
3. **HermiT on punning** — only testable post-OEO-import; non-blocking for V0 axiomatisation but flagged as watch-item.

Architect can proceed.
