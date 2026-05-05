# Handoff — `energy-intel` editorial extension (Phase 1–3)

**Session start:** 2026-05-04 (post-multi-agent design review).
**Goal:** Extend the `energy-intel` ontology to absorb editorial concepts from the sibling `skygest-editorial` repo, retire the local 30-topic / ~92-concept catalog in favor of OEO-derived concept IRIs (with a small Skygest supplement set), and produce TTL + SHACL + CQ tests that codegen consumes back into `skygest-cloudflare/packages/ontology-store/`.
**Source plan (canonical):** `/Users/pooks/Dev/skygest-cloudflare/docs/plans/2026-05-04-editorial-ontology-slice.md` — read this end-to-end before doing any modeling work. Everything below restates and operationalizes that plan for the `ontology_skill` side.

---

## TL;DR

1. Run `/ontology-requirements` against the editorial extension scope. Output `docs/scope-v2.md` retracts existing scope.md non-goal #5.
2. Run `/ontology-conceptualizer` to lock BFO leaves and predicate design (most decisions are pre-ratified in §3 of the source plan; conceptualizer's job is to BFO-justify them and produce the OEO mapping decisions).
3. Run `/ontology-architect` to author the new TTL modules (editorial.ttl + 3 SKOS scheme files) and SHACL shapes.
4. Validator gate green; release-audit signed; ready for downstream codegen.
5. Hand over to skygest-cloudflare for Phase 4 codegen (handled there, not in this repo).

Total estimated effort: 3 working days (Phases 1–3, one per skill phase).

---

## What's coming in (context state)

### From `skygest-cloudflare`

- The plan doc named above is the contract. It captures all locked decisions (Q1–Q3 + S1–S5) plus risks, acceptance criteria, and open questions for design review.
- **Three multi-agent design reviews already ran** against an earlier draft and their findings are baked into the plan. Critical findings that affected the modeling:
  - Narrative re-parented to `iao:Document` (was abstract `iao:InformationContentEntity`) to match existing `Post`/`PodcastEpisode` placement in `modules/media.ttl`.
  - ArgumentPattern shifted from `owl:Class` + ABoxed individuals to a `skos:ConceptScheme` with `skos:Concept` instances, matching the existing `EnergyTopic` pattern.
  - Narrative→Post relationships use a **reified n-ary relation** (`NarrativePostMembership` ICE class) rather than 4 role-named predicates. The reasoning: 4 role predicates would smuggle storage state into predicate names; reified relations integrate cleanly with future first-class qualifier storage.
  - 3 candidate OEO IRIs were dropped after spot-checking against `oeo-full.owl`: `OEO_00000308` (offshore wind farm, granularity mismatch — installation not topic), `OEO_00010415` ("nuclear", polysemous), `OEO_00010048` (NamedIndividual, fails granularity contract).
- 45 OEO IRIs remain as Phase 2 verification candidates. The full extraction must happen against `oeo-full.owl`; the existing `imports/oeo-{technology,carrier}-subset-fixed.ttl` files are insufficient (they miss solar, wind, nuclear, storage technology classes).

### From `skygest-editorial`

- Editorial corpus: 8 nested-layout stories under `narratives/{arc-slug}/stories/{story-stem}.md` (5 arcs total). Verified: all 8 stems globally unique (date-prefixed `YYYY-MM-DD-…`).
- Legacy flat directory `/skygest-editorial/stories/story-*.md` (6 files) is a duplicate of the nested layout pre-migration. Plan's Phase 7 step 1 archives it; not your concern, but referenced because the cloudflare side gates Gate C on this archival.
- Editorial vocabulary captured in audit: question, trigger, argument pattern, narrative, narrative-arc (filesystem-only this slice), story (= the new ontology Narrative), edition (out of scope), post-annotation (filesystem-only this slice), 7 stable argument patterns.

### From this repo (`ontology_skill`)

- Active product is `energy-intel` v0.2.0. Current modules: `agent.ttl`, `media.ttl`, `measurement.ttl`, `data.ttl` plus 3 SKOS schemes in `concept-schemes/`. Read `ontologies/energy-intel/docs/scope.md` and `ontologies/energy-intel/docs/conceptual-model.md` for the existing modeling pattern.
- The 8-skill pipeline is canonical. Do not skip skills, do not hand-edit TTL — everything goes through ROBOT / oaklib / KGCL / OWLAPY per `.claude/skills/CONVENTIONS.md`.
- Existing OEO imports: `imports/oeo-technology-subset-fixed.ttl` and `imports/oeo-carrier-subset-fixed.ttl` (BFO+RO-stripped subsets, used for upper alignment only). Full ontology source: `imports/oeo-full.owl`.

---

## What needs to be produced (Phase 1–3 deliverables)

### Phase 1 — `/ontology-requirements`

Skill: `.claude/skills/ontology-requirements/SKILL.md`. Methodology: CQ-Driven (Gruninger & Fox).

**Deliverables (under `ontologies/energy-intel/docs/`):**

1. `scope-v2.md` — extends current `scope.md`. Retracts non-goal #5 ("Narrative / Story / Arc / ArgumentPattern / Edition classes") with rationale referencing the cloudflare plan doc. Declares the editorial extension as in-scope. Re-states the topic-vocabulary cutover as in-scope.
2. `use-cases-v2.yaml` — adds the editorial use cases:
   - "Editor wants to spawn a Narrative from picks → ontology has a Narrative entity with deterministic IRI from story stem."
   - "Editor wants to attach a post in a specific role (lead/supporting/counter/context) → ontology has a NarrativePostMembership entity with role qualifier."
   - "Editor wants to classify a Narrative by argument pattern → ontology has a SKOS scheme of patterns; Narrative `ei:narrativeAppliesPattern → skos:Concept`."
   - "Editor wants to filter Narratives by topic → topics resolve to OEO IRIs (where present) or `ei:concept/...` supplement IRIs."
   - "Editor wants to import existing markdown corpus → import is atomic per batch; idempotent on re-import; rejects duplicate stems."
3. `competency-questions-v2.yaml` — adds CQs for each use case. Examples (must-have):
   - CQ-N1: "Given a story stem `S`, return the Narrative entity (deterministic IRI lookup)."
   - CQ-N2: "Given a Narrative, return all (Post, role) pairs from its memberships."
   - CQ-N3: "Given a Post, return all Narratives that include it and the role it plays in each."
   - CQ-N4: "Given a topic IRI (OEO or supplement), return all Narratives classified by it."
   - CQ-N5: "Given an argument pattern, return all Narratives applying it."
   - CQ-N6: "Given a Narrative, return all Experts mentioned (auto-derived from contained posts)."
   - CQ-N7: "SHACL: at most one NarrativePostMembership per (Narrative, Post) pair."
   - CQ-N8: "SHACL: at most one membership with role=`lead` per Narrative (warning, not error)."
   - CQ-T1: "Given a topic IRI, return its label, alt-labels, broader/narrower in the SKOS scheme."
   - CQ-T2: "Given an editorial slug from the legacy `canonicalTopicOrder`, return its canonical replacement IRI(s)."
4. `cq-quality-v2.csv` — quality scores per CQ.
5. `pre-glossary-v2.csv` — adds editorial vocabulary terms: `Narrative`, `NarrativePostMembership`, `NarrativePostRole`, `ArgumentPattern`, `EnergyTopic` (refined to OEO+supplement).
6. `requirements-approval-v2.yaml` — signed approval.

**Phase 1 acceptance:**
- `scope-v2.md` retraction is explicit and references the source plan doc.
- All CQs above appear in `competency-questions-v2.yaml` with priority and expected SPARQL shape.
- Granularity contract for topic IRIs (see §3.4 of source plan) is encoded as a CQ that any candidate IRI must pass.

### Phase 2 — `/ontology-conceptualizer`

Skill: `.claude/skills/ontology-conceptualizer/SKILL.md`. Methodology: METHONTOLOGY + BFO alignment.

Most modeling decisions are pre-ratified by the source plan + design review. The conceptualizer's job here is to BFO-justify them, lock the OEO mapping decisions, and produce the conceptual-model docs.

**Deliverables (under `ontologies/energy-intel/docs/`):**

1. `conceptual-model-v2.md` — adds the editorial extension:
   - `ei:Narrative` ⊑ `iao:0000310` (`iao:Document`).
   - `ei:NarrativePostMembership` ⊑ `iao:0000310` (`iao:Document`) — a membership record is an information artifact.
   - `ei:ArgumentPattern` is a `skos:ConceptScheme` (`ei:concept/argument-pattern`); the 7 patterns are `skos:Concept` instances.
   - `ei:NarrativePostRole` is a `skos:ConceptScheme` (`ei:concept/narrative-role`); the 4 instances are `lead`, `supporting`, `counter`, `context`.
2. `bfo-alignment-v2.md` — runs each new class through the BFO decision tree per `_shared/bfo-decision-recipes.md`. Documents the choice of `iao:Document` over abstract ICE for both Narrative and NarrativePostMembership, citing the existing `Post` / `PodcastEpisode` precedent in `modules/media.ttl`.
3. `property-design-v2.md` — declares the predicates in §3.3 of the source plan:
   - `ei:hasNarrativePostMembership` (Narrative → NarrativePostMembership, many)
   - `ei:memberPost` (NarrativePostMembership → Post, functional 1)
   - `ei:memberRole` (NarrativePostMembership → skos:Concept in `ei:concept/narrative-role`, functional 1)
   - `ei:narrativeMentionsExpert` (Narrative → Expert, many)
   - `ei:narrativeAppliesPattern` (Narrative → skos:Concept in `ei:concept/argument-pattern`, 0..1)
   - `ei:narrativeAboutTopic` (Narrative → EnergyTopic, many)
   - Reuse `skos:related` for argument-pattern relations (lifts the phantom `related_patterns` from BuildGraph.ts without minting a custom predicate).
4. `narrative-identity-rule.md` — documents §S5 of source plan: deterministic Narrative IRI = `https://w3id.org/energy-intel/narrative/{story-stem}`. Story stem is the filename without extension; arc directory does NOT enter the IRI; duplicate stems are import errors. Also: deterministic NarrativePostMembership IRI = `https://w3id.org/energy-intel/narrative/{story-stem}/membership/{post-uri-hash}` (or similar — your design call, but it must be derivable from `(narrativeIri, postUri)` without runtime ambiguity).
5. `topic-vocabulary-mapping.md` — the canonical OEO mapping decisions.

   **Method (run this before writing the doc):**
   1. Read §3.4 of the source plan. It contains the 30-row verification queue with candidate IRIs.
   2. For each candidate IRI, verify against `imports/oeo-full.owl`:
      - Class exists at the IRI? (must be `owl:Class`, not `owl:NamedIndividual` per granularity contract)
      - `rdfs:label` matches the editorial intent?
      - Granularity is correct (technology-class > carrier-class >> material/installation/inventory-record)?
      - One canonical IRI per editorial slug. Alternates become `skos:closeMatch` annotations.
   3. For each row, decide: OEO (clean fit), Local (supplement only), Mixed (umbrella supplement + OEO leaves).
   4. Record the decision with source label, source line in `oeo-full.owl`, confidence score, and supplement IRI if applicable.
6. `oeo-import-rebuild-plan.md` — specification for the rebuilt OEO topic subset (see §"OEO topic subset rebuild" below).
7. `conceptualizer-to-architect-handoff-v2.md` — handoff to Phase 3.

**Phase 2 acceptance:**
- BFO leaf for every new class documented and runs through `_shared/bfo-decision-recipes.md` deterministically.
- Every accepted topic IRI passes the granularity contract (§3.4 of source plan).
- The mapping table in `topic-vocabulary-mapping.md` covers all 30 umbrellas + decisions on each of the ~92 leaf concepts in the legacy `conceptToCanonicalTopicSlug`.
- §9 question 7 from source plan resolved: pick single SKOS scheme `ei:concept/topic` OR split into `ei:concept/oeo-topic` + `ei:concept/editorial-supplement` + aggregator. Document the choice with rationale.

### Phase 3 — `/ontology-architect`

Skill: `.claude/skills/ontology-architect/SKILL.md`. Methodology: POD (Programmatic Ontology Development) — ROBOT / KGCL / OWLAPY.

**Deliverables:**

1. `ontologies/energy-intel/imports/oeo-topic-subset.ttl` (rebuilt from `oeo-full.owl` per the spec in §"OEO topic subset rebuild" below) — `robot extract` output, BFO+RO-stripped.
2. `ontologies/energy-intel/modules/editorial.ttl` (new) — declares `ei:Narrative` ⊑ `iao:0000310`, `ei:NarrativePostMembership` ⊑ `iao:0000310`, and the predicates from §3.3.
3. `ontologies/energy-intel/modules/concept-schemes/oeo-topics.ttl` (new) — replaces `technology-seeds.ttl`; declares the topic SKOS scheme(s) per Phase 2 decision; lifts accepted OEO IRIs and supplement individuals.
4. `ontologies/energy-intel/modules/concept-schemes/argument-pattern.ttl` (new) — declares the `ei:concept/argument-pattern` SKOS scheme + 7 `skos:Concept` instances with `skos:prefLabel`, `skos:definition`, optional `skos:related` between patterns. Status field uses `owl:deprecated` (for `deprecated` patterns) plus `skos:editorialNote` for `draft`/`active` annotations.
5. `ontologies/energy-intel/modules/concept-schemes/narrative-role.ttl` (new) — declares `ei:concept/narrative-role` SKOS scheme + 4 `skos:Concept` instances (`lead`, `supporting`, `counter`, `context`) with definitions.
6. `ontologies/energy-intel/shapes/editorial.ttl` (new) — SHACL shapes for the new module:
   - `ei:NarrativeShape` — closed shape for Narrative; required fields per `Story`-derived schema.
   - `ei:NarrativePostMembershipShape` — `sh:qualifiedMaxCount 1` per (Narrative, Post) pair.
   - SHACL warning: at most one membership with `memberRole = ei:concept/narrative-role/lead` per Narrative.
   - Topic-IRI granularity validator: every `ei:narrativeAboutTopic` value MUST resolve to an `owl:Class` (in OEO scheme) or `skos:Concept` (in supplement scheme); MUST NOT be a `owl:NamedIndividual`.
7. `ontologies/energy-intel/tests/cq-editorial-N1.sparql` … `cq-editorial-N8.sparql` (new) — one SPARQL test per CQ from Phase 1. Plus `cq-editorial-T1.sparql`, `cq-editorial-T2.sparql` for topic CQs.
8. `ontologies/energy-intel/tests/cq-editorial-granularity.sparql` (new) — asserts no `owl:NamedIndividual` is reachable via `ei:narrativeAboutTopic`.
9. `ontologies/energy-intel/scripts/build-editorial.py` (new) — build script orchestrating ROBOT merge + reason (HermiT) + report + pyshacl + pytest. Mirrors `scripts/build_*.py` from existing modules.
10. `ontologies/energy-intel/scripts/extract-oeo-topic-subset.py` (new) — runs the `robot extract` job per the rebuild spec; produces `imports/oeo-topic-subset.ttl`.
11. `ontologies/energy-intel/Justfile` updates — add `build-editorial`, `validate-editorial`, `extract-oeo-topics` recipes alongside existing `validate-energy-news`/`validate-pao`.
12. `ontologies/energy-intel/release/editorial-v0-changes.kgcl` (new) — KGCL change log for the slice.
13. `ontologies/energy-intel/docs/architect-build-log-v2.md` — what was built, what failed, what was deferred.
14. `ontologies/energy-intel/docs/architect-to-validator-handoff-v2.md` — handoff to validator.

**Phase 3 acceptance (Gate A from source plan):**
- `just build-editorial` runs ROBOT merge → reason (HermiT) → report → pyshacl → pytest, all green.
- Every accepted OEO IRI in `oeo-topics.ttl` resolves to its intended `rdfs:label` in `oeo-full.owl` (verified by extraction script).
- Rebuilt `oeo-topic-subset.ttl` contains every accepted runtime term.
- `ontology_skill`'s validator gate is green; release-audit signed.
- `skygest-cloudflare/packages/ontology-store/` drift gate test (when run after the next codegen pass) recognizes the new TTL modules without metadata-key drift.

---

## OEO topic subset rebuild — concrete spec

This is the most technically substantial Phase 2/3 task. The current `imports/oeo-{technology,carrier}-subset-fixed.ttl` files do not contain the topic leaves the editorial vocabulary needs (verified: missing `OEO_00010427` solar tech, `OEO_00010424` wind, `OEO_00010439` nuclear tech, `OEO_00020366` storage tech).

**Source:** `/Users/pooks/Dev/ontology_skill/ontologies/energy-intel/imports/oeo-full.owl` (~100MB).
**Target:** `/Users/pooks/Dev/ontology_skill/ontologies/energy-intel/imports/oeo-topic-subset.ttl`.

**Method:** `robot extract` in BOT (Bottom-up Term-extraction) mode against the IRI list below. After extraction, run the BFO+RO-stripping pass that produced the existing `*-fixed.ttl` files (see `imports/upper-axiom-leak-terms.txt` and `imports/bfo-terms-to-remove.txt` for the strip list).

**Seed IRI list (from §3.4 of source plan, verified to exist in `oeo-full.owl`):**

```
oeo:OEO_00000020  # greenhouse gas
oeo:OEO_00000088  # coal
oeo:OEO_00000115  # crude oil
oeo:OEO_00000143  # electricity grid
oeo:OEO_00000146  # electric vehicle
oeo:OEO_00000191  # geothermal energy
oeo:OEO_00000199  # greenhouse gas emission
oeo:OEO_00000212  # heat pump
oeo:OEO_00000220  # hydrogen
oeo:OEO_00000292  # natural gas
oeo:OEO_00000384  # solar energy
oeo:OEO_00000446  # wind energy
oeo:OEO_00010138  # carbon capture
oeo:OEO_00010139  # direct air capture
oeo:OEO_00010141  # carbon capture and storage
oeo:OEO_00010212  # decarbonisation pathway
oeo:OEO_00010214  # biomass
oeo:OEO_00010258  # bioenergy
oeo:OEO_00010424  # wind power technology
oeo:OEO_00010426  # offshore wind power technology
oeo:OEO_00010427  # solar power technology
oeo:OEO_00010428  # photovoltaic technology
oeo:OEO_00010430  # geothermal power technology
oeo:OEO_00010431  # hydro power technology
oeo:OEO_00010438  # pumped storage hydro power technology
oeo:OEO_00010439  # nuclear power technology
oeo:OEO_00010455  # carbon capture and storage technology
oeo:OEO_00010485  # manufacturing technology
oeo:OEO_00020063  # emission certificate
oeo:OEO_00020065  # energy market exchange
oeo:OEO_00020069  # market exchange
oeo:OEO_00020075  # emission market exchange
oeo:OEO_00020366  # energy storage technology
oeo:OEO_00050000  # manufacturing process
oeo:OEO_00110019  # transmission grid
oeo:OEO_00110020  # distribution grid
oeo:OEO_00140049  # energy conversion efficiency
oeo:OEO_00140150  # policy
oeo:OEO_00140151  # policy instrument
oeo:OEO_00240030  # mineral
oeo:OEO_00310000  # data center
```

41 IRIs total. Verify each against `oeo-full.owl` during Phase 2 mapping work — flag any that don't resolve, are NamedIndividuals, or have unexpected labels. Drop or replace per the granularity contract.

**Validator:** SPARQL ASK that fails if any IRI in `oeo-topics.ttl` is `owl:NamedIndividual`. Lives at `ontologies/energy-intel/tests/cq-editorial-granularity.sparql`. Wired into `just validate-editorial`.

---

## Editorial supplement IRIs (Local / Mixed rows from §3.4)

These are Skygest-coined `ei:concept/...` supplement IRIs that exist because OEO has no clean editorial equivalent. All declared in `concept-schemes/oeo-topics.ttl` (or split per Phase 2 decision on §9 Q7):

- `ei:concept/distributed-energy`
- `ei:concept/grid-and-infrastructure` (umbrella + OEO leaves for grid components)
- `ei:concept/electrification` (umbrella + OEO leaves for electric vehicle, heat pump)
- `ei:concept/energy-efficiency` (umbrella; `OEO_00140049` is too narrow)
- `ei:concept/data-center-demand` (umbrella + OEO `OEO_00310000` leaf)
- `ei:concept/energy-policy` (umbrella + OEO policy/instrument leaves)
- `ei:concept/energy-markets` (umbrella + OEO market leaves)
- `ei:concept/energy-finance`
- `ei:concept/energy-geopolitics`
- `ei:concept/critical-minerals` (umbrella + OEO mineral leaves)
- `ei:concept/climate-and-emissions` (umbrella + OEO emission leaves)
- `ei:concept/carbon-markets` (umbrella + OEO emission-market leaves)
- `ei:concept/environment-and-land-use` (Local only — dropped land-use sector NamedIndividuals)
- `ei:concept/energy-justice`
- `ei:concept/sectoral-decarbonization` (umbrella + OEO decarbonisation pathway leaf)
- `ei:concept/workforce-and-manufacturing` (umbrella + OEO manufacturing leaves)
- `ei:concept/research-and-innovation`
- `ei:concept/energy-storage` (only if the editorial umbrella needs broader scope than OEO `OEO_00020366` — Phase 2 decision)
- `ei:concept/biomass` (only if the editorial umbrella needs broader scope than OEO `OEO_00010258`/`OEO_00010214` — Phase 2 decision)

Each supplement gets `skos:prefLabel`, `skos:definition`, optional `skos:exactMatch` / `skos:closeMatch` to OEO IRIs where the relationship is explicit, and `skos:hasTopConcept` from the scheme.

---

## Codegen target (downstream — for situational awareness only)

After Phase 3 ships, `skygest-cloudflare` (Phase 4 of the source plan) will:

1. Run `/Users/pooks/Dev/skygest-cloudflare/src/scripts/build-ontology-snapshot.ts` to regenerate `config/ontology/energy-snapshot.json` from your new TTL modules. **The script's `ontologyRoot` constant will be repointed from `energy-news` to `energy-intel`** — this is a hard blocker the cloudflare side owns, but worth knowing because if your TTL files don't follow the existing module shape (one `Ontology` declaration per file, named class/property declarations, `skos:Concept` instances with `skos:inScheme` and `skos:prefLabel`), the snapshot script breaks.
2. Run codegen against your TTL modules to produce:
   - `packages/ontology-store/src/generated/editorial.ts` — IRI brands + thin Schema.Class for `Narrative`, `NarrativePostMembership`.
   - `packages/ontology-store/src/generated/concepts.ts` — rewritten to source from your new SKOS scheme files.
3. Hand-write per-entity modules at `packages/ontology-store/src/editorial/narrative.ts` and `narrative-post-membership.ts`.

You don't need to make those changes; just be aware the TTL is the contract.

---

## Skill workflow guidance

Per `.claude/skills/CONVENTIONS.md`:

1. **Invoke `/ontology-requirements` first.** Don't skip to architect just because §3 of the source plan looks pre-decided. The skill produces the artifacts that gate Phase 2.
2. **Hand off to `/ontology-conceptualizer`.** Run the OEO mapping verification here, not in architect. Conceptualizer is where modeling decisions happen; architect just encodes them.
3. **Hand off to `/ontology-architect`.** TTL/SHACL/CQ files. Use `robot extract` for the OEO subset rebuild, KGCL patches for incremental edits, OWLAPY for axioms. **Do not hand-edit TTL.**
4. **`/ontology-validator`** runs the gates independently after architect.
5. **`/ontology-curator`** signs the release-audit.

Methodology backbone is in `_shared/methodology-backbone.md`. BFO recipes are in `_shared/bfo-decision-recipes.md`. Anti-patterns are in `_shared/anti-patterns.md`.

**Loopback triggers** (per `_shared/iteration-loopbacks.md`): if Phase 2 surfaces a CQ that can't be answered, loop back to Phase 1 to revise. Depth-3 anti-thrash guard applies — no more than 3 loopback cycles on any single decision.

---

## Open questions to surface during Phase 1/2

These are pre-existing open questions from the source plan §9 that the skill phases should resolve:

1. **§9 Q3 (signal preservation):** Does any current consumer in `skygest-cloudflare` rely on the *original* leaf concept granularity that the umbrella collapse would lose? If yes, `topic-vocabulary-mapping.md` (Phase 2) must preserve the leaf concept as well as the umbrella. (Answer requires reading the cloudflare consumer code, which is out of scope here — flag in the requirements doc as a question for the cloudflare side.)
2. **§9 Q5 (`attach_post_to_narrative` bulk):** Should the import batch accept multiple posts per narrative in one transaction? Affects only `NarrativeImportBatch` schema design on the cloudflare side, but the ontology should not constrain it either way. Note in `conceptual-model-v2.md` that the cardinality of `ei:hasNarrativePostMembership` is `many` and order is not preserved.
3. **§9 Q6 (slug system co-residence):** After the Pattern A migration window, is the legacy `topic_slug` column dropped or retained indefinitely? Affects the `oeo-topics.ttl` declaration: does it need legacy-slug `skos:notation` annotations for the migration period? Recommend yes — annotate every supplement IRI with the legacy slug as `skos:notation` so the migration map is queryable from the ontology itself.
4. **§9 Q7 (SKOS scheme split):** Single `ei:concept/topic` scheme, or `ei:concept/oeo-topic` + `ei:concept/editorial-supplement` + aggregator? **Decide in Phase 2.** The cleaner pattern (split + aggregator) avoids claiming OEO IRIs as members of an `ei:concept/...` scheme they don't natively belong to. My recommendation: split + aggregator. Document the decision in `conceptual-model-v2.md`.

---

## Out of scope (this slice)

These are explicitly NOT modeled in this Phase 1–3:

- `Edition` (newsletter compile) — deferred. No TTL.
- `EditorialPick` — stays a D1 row + future `entity_link_evidence` row on the cloudflare side; not an ontology entity.
- `PostAnnotation` — filesystem markdown only; not an ontology entity.
- `Trigger` — stays free text on Narrative; not a typed enum or class.
- `Narrative.entities` and `Narrative.data_refs` — stay as opaque string arrays until the Post→Entity resolver workflow lands (next slice).
- Provenance taxonomy (editorial / hydratable / derived / cache) as a first-class meta-property — captured in PROV-O annotations only when convenient; not enforced.
- Reindex propagation runtime — slice 4+.
- Post→Entity linking workflow — next slice (depends on this one landing).

---

## References

### Source plan and design review artifacts (in `skygest-cloudflare`)

- `/Users/pooks/Dev/skygest-cloudflare/docs/plans/2026-05-04-editorial-ontology-slice.md` — **canonical source plan** (read end-to-end before any work).
- The three multi-agent design review reports (BFO/OEO modeling, system integration, migration safety) are not committed but their findings are baked into the plan doc.

### Editorial repo (in `skygest-editorial`)

- `/Users/pooks/Dev/skygest-editorial/CLAUDE.md` and `AGENTS.md` for editorial workflow context.
- `/Users/pooks/Dev/skygest-editorial/references/argument-patterns/*.md` — the 7 stable argument patterns (one file each).
- `/Users/pooks/Dev/skygest-editorial/references/argument-patterns.md` — index.
- `/Users/pooks/Dev/skygest-editorial/references/frontmatter-provenance.md` — provenance taxonomy (informational, not modeled this slice).
- `/Users/pooks/Dev/skygest-editorial/references/clustering-heuristics.md` — explains the question-vs-topic discipline.
- `/Users/pooks/Dev/skygest-editorial/narratives/nuclear-economics/` — canonical fixture for testing.

### This repo (`ontology_skill`)

- `.claude/skills/CONVENTIONS.md` — the methodology backbone.
- `.claude/skills/_shared/bfo-decision-recipes.md` — BFO leaf decision tree.
- `.claude/skills/_shared/axiom-patterns.md` — pattern #9 (n-ary relation reification) is directly relevant.
- `.claude/skills/_shared/anti-patterns.md` — System Blueprint anti-pattern (#14) is what we're avoiding by reifying the Narrative-Post relation.
- `ontologies/energy-intel/docs/scope.md` — current scope; non-goal #5 needs retraction in `scope-v2.md`.
- `ontologies/energy-intel/docs/conceptual-model.md` — current modeling; extend it.
- `ontologies/energy-intel/modules/media.ttl` — Post / PodcastEpisode placement under `iao:0000310` is the precedent for Narrative.
- `ontologies/energy-intel/modules/concept-schemes/technology-seeds.ttl` — current SKOS pattern; oeo-topics.ttl replaces this.
- `ontologies/energy-intel/imports/oeo-full.owl` — OEO source of truth for verification.

### Cloudflare-side downstream consumers (informational)

- `/Users/pooks/Dev/skygest-cloudflare/packages/ontology-store/src/concept/energy-topic.ts` — current EnergyTopic schema; IRI brand pattern `^https?:\/\/\S+$/` already accepts OEO IRIs.
- `/Users/pooks/Dev/skygest-cloudflare/packages/ontology-store/src/agent/expert.ts` — canonical reference for hand-written entity modules; what `narrative.ts` will look like.

---

## Concrete first action

Invoke `/ontology-requirements` in this repo with the following prompt skeleton:

> Run Phase 1 — `/ontology-requirements` Step 0 + Step 1 — for the editorial extension to `energy-intel`. Source plan: `/Users/pooks/Dev/skygest-cloudflare/docs/plans/2026-05-04-editorial-ontology-slice.md`. Handoff: `/Users/pooks/Dev/ontology_skill/docs/HANDOFF-2026-05-04-editorial-extension.md`. Produce `scope-v2.md`, `use-cases-v2.yaml`, `competency-questions-v2.yaml`, `cq-quality-v2.csv`, `pre-glossary-v2.csv`, `requirements-approval-v2.yaml` under `ontologies/energy-intel/docs/`. Retract scope.md non-goal #5 explicitly. Encode the granularity contract for topic IRIs as a CQ. Sign approval.

Once Phase 1 is signed, hand off to `/ontology-conceptualizer` with the Phase 2 acceptance list above as the deliverable contract.

---

*This handoff is the input to Phase 1. Do not modify it during Phase 1–3 execution; treat it as immutable. If a decision needs revisiting, surface it as an open question in `scope-v2.md` or `requirements-approval-v2.yaml` rather than amending this doc.*
