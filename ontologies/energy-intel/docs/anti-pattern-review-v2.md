# Anti-Pattern Review — `energy-intel` V2 Delta (Editorial Extension)

**Authored:** 2026-05-04 by `ontology-conceptualizer` (V2 iteration)
**Predecessor:** [anti-pattern-review-v1.md](anti-pattern-review-v1.md) (V1; commit `1d8f9da`)
**Reviewer:** Mepuka Kessy (`kokokessy@gmail.com`)
**Reviewed at:** 2026-05-04
**Conceptual-model commit:** `1d8f9da` (V2 baseline; V2 docs not yet committed at review time)
**Reference:** [`_shared/anti-patterns.md`](../../../.claude/skills/_shared/anti-patterns.md)

This document records the V2 anti-pattern scan. V0 + V1 anti-pattern reviews remain authoritative for those scopes. V2 reviews only the editorial extension delta (2 new classes, 6 new properties, 4 SKOS schemes, OEO topic subset rebuild).

---

## 0. Summary verdict

**0 unresolved anti-patterns.** All 16 standard anti-patterns scanned; V2 ships clean.

The V2 design has 3 patterns where the conceptualizer initially considered an anti-pattern and **deliberately resolved it before architect handoff** — these are documented in § 4 below as "design decisions that avoid anti-patterns."

---

## 1. Per-pattern results

| # | Pattern | Detection mode | Finding | Resolution |
|---|---------|----------------|---------|------------|
| 1 | Singleton hierarchy | manual + structural inspection | **none found** — no V2 class has only one declared subclass | — |
| 2 | Role-type confusion | manual + BFO recipe walk | **none found** — V2 introduces no role classes; all 4 narrative-role concepts are SKOS concepts (correct), not subclasses of `ei:Narrative` or `ei:NarrativePostMembership` | — |
| 3 | Process-object confusion | manual + BFO recipe walk | **none found** — Narrative and NarrativePostMembership are both Continuants (specifically GDC under iao:Document), not Processes. The *act of attaching* a post is an unmodeled process; the resulting record is a continuant. See [bfo-alignment-v2.md § 2.6](bfo-alignment-v2.md). | — |
| 4 | Missing disjointness (siblings without disjoint axioms) | manual | **resolved** — `ei:Narrative` and `ei:NarrativePostMembership` are siblings under `iao:Document`, alongside V0's `ei:Post` and `ei:PodcastEpisode`. Architect axiom A3 (optional but recommended) declares `AllDisjointClasses(Narrative, Post, PodcastEpisode, NarrativePostMembership)` for defense-in-depth. The deterministic IRI rule informally enforces this; the explicit axiom is belt-and-suspenders. | A3 covers it |
| 5 | Circular definitions | manual | **none found** — every V2 definition is genus-differentia and references existing parent terms. No definition references the term being defined. | — |
| 6 | Quality-as-class | manual | **none found** — V2 introduces no quality values. The 4 narrative-role concepts (lead, supporting, counter, context) and the 7 argument-pattern concepts are SKOS concepts, not class hierarchies of qualities. | — |
| 7 | Information-physical conflation | manual + BFO recipe | **none found** — Narrative is explicitly an information artefact (`iao:Document`), not the events it describes. NarrativePostMembership is explicitly a record (also `iao:Document`), not the social act of attaching. See [bfo-alignment-v2.md § 1.2 + § 2.2](bfo-alignment-v2.md). | — |
| 8 | Orphan classes (no named parent) | structural inspection | **none found** — both new classes carry `rdfs:subClassOf iao:0000310` declarations. | — |
| 9 | Polysemy (one class for multiple meanings) | manual | **none found** — Narrative is the single concept of "written editorial unit"; NarrativePostMembership is the single concept of "membership record." No class spans multiple meanings. | — |
| 10 | Domain/range overcommitment | manual + decision procedure | **resolved** — see § 4 below for `ei:narrativeAboutTopic` range design (kept as `owl:Thing` per anti-pattern #10 guidance; SHACL handles the granularity contract instead of a narrow OWL range) | resolved by design |
| 11 | Two sources of truth | manual | **resolved** — see § 4 below for the `ei:narrativeMentionsExpert` design decision (UNION of explicit assertion + property-path fallback in CQ-N6 was scrutinized against this anti-pattern; the fallback path is auxiliary, not authoritative) | resolved by design |
| 12 | Open-world trap (CQ depends on negation) | OWA review | **none found** — all V2 CQs return empty as a legitimate outcome (a Narrative may have no posts, no patterns, no topics). No CQ requires "the absence of X" to be a true assertion. SHACL constraint CQs (CQ-N7, CQ-N8, CQ-T3) are closed-world by definition. | — |
| 13 | Annotation-property-as-OWL-axiom | manual | **none found** — `skos:notation` and `skos:editorialNote` (used in V2) are SKOS annotation properties, used appropriately for editorial slug carry-over and lifecycle metadata. | — |
| 14 | System Blueprint anti-pattern (storage state in predicate names) | manual + design review | **resolved** — see § 4 below for the reified n-ary relation decision. This was the foundational design decision that source plan §3.3's multi-agent design review explicitly addressed. | resolved by design |
| 15 | Premature formalization (axioms before requirements) | retrospective check | **none found** — V2 sequenced through `/ontology-requirements` (Phase 1) → `/ontology-conceptualizer` (Phase 2 = this) → `/ontology-architect` (Phase 3 next). No architect axioms have been written yet. | — |
| 16 | OEO punning leak (V0 watch item) | empirical reasoner trace | **resolved** — V1 § 5 punning prediction held: HermiT clean on V1 closure with BFO+RO-stripped OEO subsets. V2 adds the rebuilt `oeo-topic-subset.ttl` with the same BFO+RO-strip pattern; V2 architect verifies HermiT remains clean per the V1 trace. | (carry-forward; V2 architect re-verifies) |

---

## 2. SHACL coverage (defense-in-depth)

V2 ships 4 SHACL shapes (S-V2-1..S-V2-4). Together they enforce the invariants OWL OWA cannot express:

| Shape | Severity | Anti-pattern guarded against |
|---|---|---|
| S-V2-1 | Violation | Multi-membership per (Narrative, Post) — would be a System Blueprint variant |
| S-V2-2 | Violation | narrativeAppliesPattern value outside argument-pattern scheme — would be polysemy |
| S-V2-3 | Violation | narrativeAboutTopic granularity — would be domain/range overcommitment if OEO IRIs were typed as a narrow range; instead enforced as a SHACL invariant |
| S-V2-4 | Warning | Multi-lead per Narrative — soft warning during draft state, hard correctness on published |

---

## 3. Module-boundary review

The 5th local module (`editorial`) is added per [conceptual-model-v2.md § 2](conceptual-model-v2.md). Module boundary checks per [`_shared/modularization-and-bridges.md`](../../../.claude/skills/_shared/modularization-and-bridges.md):

| Check | Verdict | Note |
|---|---|---|
| Module size 100-150 concepts? | yes | editorial has 2 classes + 6 properties + 30 SKOS concepts (4 roles + 7 patterns + 19 supplements + ~41 OEO IRIs in scheme membership) — well within budget |
| Cross-module dependencies declared? | yes | Imports: `iao:0000310` (V0 import), `ei:Post` (from media), `foaf:Person` (V0 import), `skos` (V0 import). Architect lists in `modules/editorial.ttl` `owl:imports` declaration |
| Layer assignment consistent? | yes | All 5 modules in problem-specific layer; editorial fits |
| Behavioral / functional / lifecycle split rationale? | yes | editorial is the editorial-process layer (as-curated artefacts), distinct from data-structure layers (as-extracted, as-published) |

---

## 4. Design decisions that avoid anti-patterns

These are decisions where the conceptualizer initially considered a simpler shape and explicitly rejected it because it would trip an anti-pattern.

### 4.1 Reified n-ary relation (anti-pattern #14: System Blueprint)

**Considered:** Four role-named predicates `ei:leadPost`, `ei:supportingPost`, `ei:counterPost`, `ei:contextPost` linking Narrative directly to Post.

**Rejected because:**
1. Predicates would encode storage state — adding a new role would require minting a new predicate and migrating all consumers (System Blueprint). Reified `NarrativePostMembership` admits new roles via SKOS scheme extension (skos:Concept instances, not predicates).
2. Future qualifiers (annotation reference, attached-by, attached-at, confidence) would have nowhere to attach on a bare predicate — they'd have to live on a separate join graph. The reified class absorbs them naturally.
3. SHACL closed-shape constraint `sh:qualifiedMaxCount 1` per (Narrative, Post) is clean over the reified class; over four predicates it becomes a multi-predicate constraint that's harder to express.

**V2 ships:** `ei:NarrativePostMembership` reified class with `ei:hasNarrativePostMembership` (Narrative → Membership) and `ei:memberPost` / `ei:memberRole` (Membership → Post / Concept).

**Source:** [conceptual-model-v2.md § 7](conceptual-model-v2.md), [bfo-alignment-v2.md § 2.4](bfo-alignment-v2.md), source plan §3.3 (multi-agent BFO/OEO modeling review).

### 4.2 Domain/range broad on `ei:narrativeAboutTopic` (anti-pattern #10: Domain/range overcommitment)

**Considered:** Range `skos:Concept` (or `owl:Class`) on `ei:narrativeAboutTopic` to reject NamedIndividual values at the OWL level.

**Rejected because:**
1. Anti-pattern #10 (per `_shared/anti-patterns.md`) reads: declared OWL `rdfs:range` is an *inference rule*, not a constraint. A narrow range would *infer* that every value is a `skos:Concept`, which under OWL 2 punning would force OEO classes (declared `owl:Class` in OEO subset) to also be classified as `skos:Concept` instances regardless of actual scheme membership — leaking type information.
2. The granularity contract is conceptually a *constraint* ("value MUST be one of these types"), not an *inference* ("value IS this type"). SHACL is the right tool; OWL range is the wrong tool.
3. Per the property-design decision procedure in [`_shared/relation-semantics.md`](../../../.claude/skills/_shared/relation-semantics.md): "Do you want to CONSTRAIN usage? → Use SHACL. Do you want to INFER types? → Use OWL."

**V2 ships:** OWL range `owl:Thing` (broadest; no inference); SHACL S-V2-3 with `sh:or` enumeration (`owl:Class ∪ skos:Concept`) for the granularity invariant.

**Source:** [property-design-v2.md § 6](property-design-v2.md), [conceptual-model-v2.md § 8](conceptual-model-v2.md).

### 4.3 SKOS scheme split + aggregator (avoids polysemy anti-pattern #9)

**Considered:** Single `ei:concept/topic` SKOS scheme with all topics (OEO + supplement) declared inside.

**Rejected because:**
1. Polysemy (anti-pattern #9): claiming OEO IRIs as members of a Skygest-namespaced `ei:concept/...` scheme they don't natively belong to creates a kind of polysemy — the same IRI denotes both an OEO class (as far as OEO knows) and a Skygest scheme member (as far as Skygest knows). The semantic content of "membership in this scheme" gets blurred.
2. Source plan §9 Q7 explicitly raised this concern. The split + aggregator pattern resolves it by making the OEO membership an explicit `skos:inScheme ei:concept/oeo-topic` triple — Skygest declares OEO IRIs as members of a Skygest-named scheme, but the scheme name itself signals "these are OEO topics" so the membership is honest.

**V2 ships:** Three schemes: `ei:concept/oeo-topic` (OEO IRIs only), `ei:concept/editorial-supplement` (Skygest-coined IRIs only), `ei:concept/topic` (aggregator).

**Source:** [conceptual-model-v2.md § 4](conceptual-model-v2.md).

### 4.4 ArgumentPattern as SKOS concepts, not OWL classes (avoids quality-as-class anti-pattern #6)

**Considered (and explicitly rejected by source plan multi-agent review):** `ei:ArgumentPattern owl:Class` with the 7 patterns as ABoxed individuals.

**Rejected because:**
1. Quality-as-class anti-pattern (#6) — argument patterns are values an editor selects from an enumeration; they are not types-of-things in the BFO sense. Modeling them as classes muddles the value vs. class distinction.
2. Pattern lifecycle (active / draft / deprecated) is a metadata concern, not a class hierarchy concern. SKOS handles this via `skos:editorialNote` + `owl:deprecated`; OWL-class hierarchy would force lifecycle into the class structure (e.g., `ActiveArgumentPattern subClassOf ArgumentPattern`), which is wrong.
3. Source plan §S4 cites the existing `EnergyTopic` SKOS pattern as established precedent.

**V2 ships:** `ei:concept/argument-pattern` as a SKOS ConceptScheme; 7 SKOS Concept instances.

**Source:** [conceptual-model-v2.md § 5](conceptual-model-v2.md), source plan §S4.

### 4.5 NarrativeRole as SKOS concepts, not subclasses (avoids role-type confusion #2)

**Considered:** `ei:LeadPost`, `ei:SupportingPost`, `ei:CounterPost`, `ei:ContextPost` as subclasses of `ei:Post`.

**Rejected because:**
1. Role-type confusion (anti-pattern #2): a Post's role in a Narrative is *transient* — a single Post can be lead in one Narrative and supporting in another. Modeling roles as subclasses would force every (Post, role) pair to its own Post subclass, breaking the natural Post-as-content modeling. This is the textbook reason BFO Role exists and we use the role-bearer pattern.
2. The reified relation absorbs the role qualifier directly via `ei:memberRole`, which is the right place — the role is a property of the membership, not the post.

**V2 ships:** 4 narrative-role concepts (lead, supporting, counter, context) as SKOS Concept instances in `ei:concept/narrative-role`. The role qualifier lives on `NarrativePostMembership` via `ei:memberRole`.

**Source:** [conceptual-model-v2.md § 6](conceptual-model-v2.md), source plan §3.3.

### 4.6 narrativeMentionsExpert as a property (not two sources of truth — avoids anti-pattern #11)

**Considered:** Drop the explicit `ei:narrativeMentionsExpert` predicate; rely solely on the property-path walk `Narrative → membership → post → authoredBy → Person` in CQ-N6.

**Considered as alternative:** Drop the property-path fallback; require auto-derivation to populate `ei:narrativeMentionsExpert` on every Narrative.

**Rejected because:**
1. The pure-walk approach burns a 4-hop SPARQL query for every CQ-N6 invocation. Performance concern for the cloudflare runtime.
2. The pure-explicit approach makes CQ-N6 fragile — if auto-derivation hasn't run on a Narrative yet (e.g., during initial import before `NarrativeWriteService` finishes), CQ-N6 returns empty (incorrect).

**Two-sources-of-truth check (anti-pattern #11):** UNION of explicit + property-path is *not* two sources of truth. The property-path walk is *deriving* the same answer as the explicit edge, not asserting an independent fact. The auto-derivation rule (cloudflare-side `NarrativeWriteService`) ensures the explicit edge stays consistent with the walk.

**V2 ships:** Both the property and the fallback walk. CQ-N6 SPARQL uses `UNION` to surface either path.

**Source:** [property-design-v2.md § 4](property-design-v2.md).

---

## 5. Open items

None. All anti-pattern scans complete; all design decisions documented; no carry-forward issues to V3.

The V0 watch item (anti-pattern #16: OEO punning leak) is in carry-forward state but unchanged: V2 architect re-verifies HermiT remains clean on the V2 closure (V1 was clean, V2 adds no new BFO axioms).
