# BFO Alignment — `energy-intel`, V2 Delta (Editorial Extension)

**Authored:** 2026-05-04 by `ontology-conceptualizer` (V2 iteration)
**Predecessor:** [bfo-alignment-v1.md](bfo-alignment-v1.md) (V1; commit `1d8f9da`)
**Reviewer:** Mepuka Kessy (`kokokessy@gmail.com`)
**Reviewed at:** 2026-05-04
**Consumer:** `ontology-architect` (uses BFO/IAO IRIs when asserting `rdfs:subClassOf`).

BFO 2020 (ISO 21838-2:2021) IRIs throughout. Class decisions recorded against the three decision recipes in [`_shared/bfo-decision-recipes.md`](../../../.claude/skills/_shared/bfo-decision-recipes.md).

This document is a **delta** to V1 bfo-alignment-v1.md. V0/V1 placements remain authoritative for everything not restated here.

---

## 0. Scope of V2 BFO changes

V2 introduces **two new local classes** with BFO placements:
- `ei:Narrative`
- `ei:NarrativePostMembership`

V2 does NOT modify any V0 or V1 BFO placement. The four V0 modules + V1 `EnergyExpertRole` keep their BFO leaves unchanged.

| Class | V0/V1 BFO leaf | V2 BFO leaf | Status |
|---|---|---|---|
| `ei:Narrative` | n/a (new) | `bfo:Continuant → bfo:GenericallyDependentContinuant → iao:InformationContentEntity → iao:Document` (IAO_0000310) | **NEW** |
| `ei:NarrativePostMembership` | n/a (new) | `bfo:Continuant → bfo:GenericallyDependentContinuant → iao:InformationContentEntity → iao:Document` (IAO_0000310) | **NEW** |
| All V0 + V1 classes | (unchanged) | (unchanged) | — |

The new SKOS schemes (`argument-pattern`, `narrative-role`, `oeo-topic`, `editorial-supplement`, `topic`) are **not BFO-typed**: SKOS is a separate W3C vocabulary (BFO-orthogonal) per V0 [scope.md § Reasoning](scope.md). The 7 argument-pattern concepts, 4 narrative-role concepts, and 19 supplement concepts are `skos:Concept` instances, not subclasses with BFO leaves.

The rebuilt OEO topic subset (`imports/oeo-topic-subset.ttl`) brings **no new local BFO placements** — it is a MIREOT/BOT extract from `oeo-full.owl` whose internal BFO axioms are stripped before import (same pattern as V1). OEO classes appear as values of `ei:narrativeAboutTopic` via OWL 2 punning; they do not become BFO-typed local classes.

---

## 1. New class — `ei:Narrative`

### 1.1 Decision

- **BFO leaf:** `bfo:Continuant → bfo:GenericallyDependentContinuant → iao:InformationContentEntity → iao:Document` (IAO_0000310).
- **Local parents:** `rdfs:subClassOf iao:0000310` (one parent; no multiple inheritance).

### 1.2 Recipe applied

Per [`_shared/bfo-decision-recipes.md`](../../../.claude/skills/_shared/bfo-decision-recipes.md) **continuant / occurrent** branch:

1. **Continuant or occurrent?** **Continuant.** A Narrative is a written editorial unit; it persists through time as the same entity. Editing the markdown does not destroy the Narrative — it is the *concretization* (file content) that changes; the Narrative IRI is stable. Rule of thumb: if you can ask "is the same X still there?" five minutes apart and the answer is yes by default, it's a continuant.

2. **Independent or dependent?** **Dependent (generically).** A Narrative has no independent existence — it depends on bearers (filesystems, databases, AI Search indices) that concretize its content. But its identity is independent of any *specific* bearer (the same Narrative can be exported to PDF, pulled from D1, queried from AI Search — same content, different bearers). This is the textbook GDC pattern (Generically Dependent Continuant) — like a "novel" in IAO terms.

3. **Information artefact?** **Yes.** A Narrative is *about* events (TVA's IRP, Germany's grid, etc.) but is not the events themselves. It is editorial commentary. This places it under `iao:InformationContentEntity` via the IAO MIREOT chain.

4. **Identifiable boundaries?** **Yes.** A Narrative has a deterministic IRI (story-stem-derived) and a definite text content (the markdown). It is not abstract — it has identity over time, content over time, and structural fields (headline, question, posts, argument-pattern, topics). Rule of thumb: if it has identifiable start+end markers and is bound to a single IRI, it goes under `iao:Document`, not abstract `iao:InformationContentEntity`.

### 1.3 Architect axiom (Manchester sketch)

```turtle
ei:Narrative a owl:Class ;
  rdfs:label "narrative"@en ;
  rdfs:subClassOf iao:0000310 ;
  skos:definition
    "A written editorial unit about energy-domain events that have been
    curated by an editor. A Narrative groups posts that share an
    editorial through-line (a single argument or question) and applies
    an argument pattern to frame the discussion. Narratives are
    identified by a deterministic IRI derived from the story stem;
    the directory hierarchy on disk does not enter the IRI."@en .
```

Mirrors V0's `ei:Post` and `ei:PodcastEpisode` placement under `iao:Document` exactly. Architect can reuse the V0 [`modules/media.ttl`](../modules/media.ttl) Post/PodcastEpisode template; substitute the class name.

### 1.4 Why iao:Document and not abstract iao:InformationContentEntity

The handoff §"What's coming in" notes that source plan multi-agent BFO/OEO modeling review explicitly upgraded Narrative from abstract `iao:InformationContentEntity` to `iao:Document`. Three reasons:

1. **Existing precedent.** V0 places Post and PodcastEpisode under `iao:Document` (in `modules/media.ttl`). The Narrative shares the same documentary character: a written textual unit with start/end and a stable IRI. Splitting Narrative under abstract ICE while Post is under Document creates inconsistency for no semantic gain.

2. **Bounded artefact.** A Narrative has a definite content boundary (the markdown file's content). `iao:Document` is the ICE subclass intended for bounded artefacts; abstract `iao:InformationContentEntity` is intended for content that doesn't have a single canonical bearer (e.g., a name like "Plato"). The Narrative has a canonical bearer (the markdown file) plus derived bearers (D1, AI Search) — that is the Document pattern.

3. **Reasoner consistency.** Under HermiT, classifying Narrative under `iao:Document` enables future axioms like `Narrative SubClassOf hasIdentifier some xsd:anyURI` to land cleanly. Under abstract ICE, such axioms either land or don't depending on whether IAO's chain reaches Document — keeping Narrative at Document is the safer placement.

### 1.5 Disjointness obligations

`ei:Narrative` is disjoint from all bfo:IndependentContinuant subclasses (e.g., `ei:Organization` which is `bfo:ObjectAggregate`). This disjointness is **inherited** from BFO: GDC and IndependentContinuant are disjoint at the BFO level. No new local disjointness axioms needed.

`ei:Narrative` is **not** disjoint from `ei:Post` or `ei:PodcastEpisode` — all three are siblings under `iao:Document`. They are however *different*: a Narrative IRI cannot be a Post IRI (deterministic IRI rule). This non-overlap is enforced by IRI minting convention (different IRI prefixes), not by an `owl:disjointWith` axiom.

If the architect wants explicit IAO-level disjointness for defense-in-depth: `DisjointClasses(ei:Narrative, ei:Post, ei:PodcastEpisode, ei:NarrativePostMembership)` would assert that no individual is two of these at once. Recommended but not strictly required (the deterministic IRI rule already enforces this informally).

### 1.6 Ambiguity score

**0.** Textbook iao:Document placement, mirroring existing V0 precedent. No reviewer escalation required (per [`_shared/llm-verification-patterns.md`](../../../.claude/skills/_shared/llm-verification-patterns.md), only ambiguity ≥ 2 requires Class C reviewer signature).

---

## 2. New class — `ei:NarrativePostMembership`

### 2.1 Decision

- **BFO leaf:** `bfo:Continuant → bfo:GenericallyDependentContinuant → iao:InformationContentEntity → iao:Document` (IAO_0000310).
- **Local parents:** `rdfs:subClassOf iao:0000310` (one parent).

### 2.2 Recipe applied

Per [`_shared/bfo-decision-recipes.md`](../../../.claude/skills/_shared/bfo-decision-recipes.md):

1. **Continuant or occurrent?** **Continuant.** A NarrativePostMembership is a *record* — a database / triple-store entry — that persists. It is not the social act of attaching the post; that act is an occurrent (a Process), but the *membership record* the act creates is a continuant.

2. **Independent or dependent?** **Dependent (generically).** Same reasoning as Narrative — it depends on bearers (D1 row, RDF triple) but its identity is independent of any specific bearer.

3. **Information artefact?** **Yes.** It is an explicit record of "Narrative N includes Post P in role R." It is a structured information artefact, not the relationship itself.

4. **Identifiable boundaries?** **Yes.** It has a deterministic IRI derived from sha256 of `(narrativeIri || "\n" || postUri)`, a definite content (3 RDF triples: `memberPost`, `memberRole`, plus the `hasNarrativePostMembership` link from the Narrative), and a bounded structural shape. It is documentary.

### 2.3 Architect axiom (Manchester sketch)

```turtle
ei:NarrativePostMembership a owl:Class ;
  rdfs:label "narrative post membership"@en ;
  rdfs:subClassOf iao:0000310 ;
  skos:definition
    "An information artefact recording that a Narrative includes a Post
    in a specific role (lead, supporting, counter, or context). One
    individual per (Narrative, Post) pair. Identified by a deterministic
    IRI derived from sha256 of (narrativeIri, postUri).

    Reified rather than four role-named predicates because role-named
    predicates would smuggle storage state into predicate names (System
    Blueprint anti-pattern), would not absorb future first-class
    qualifier storage cleanly, and would block the SHACL closed-shape
    invariant sh:qualifiedMaxCount 1 per (Narrative, Post)."@en .
```

### 2.4 Why a reified relation, not 4 role-named predicates

Critical pre-ratified design decision from source plan §3.3 + multi-agent BFO/OEO modeling review. Three reasons (re-stated for traceability):

1. **System Blueprint anti-pattern (anti-patterns.md #14).** Four role-named predicates (`leadPost`, `supportingPost`, `counterPost`, `contextPost`) would encode storage state in predicate names. Adding a new role would require minting a new predicate and migrating all consumers. The reified relation absorbs new roles via SKOS scheme extension — adding `skos:Concept` instances, not predicates.

2. **Future qualifier storage.** A NarrativePostMembership is the natural place to attach future qualifiers (annotation reference, attached-by Expert, attached-at timestamp, confidence score). Four role-named predicates would force these qualifiers to be on the predicate (impossible in standard OWL) or on a separate join graph (much more complex).

3. **SHACL closed-shape invariant.** The contract is "at most one membership per (Narrative, Post) pair" — easily expressed as `sh:qualifiedMaxCount 1` over the reified class. With four role-named predicates the invariant becomes "at most one of these four predicates from Narrative N to Post P" — a multi-predicate constraint that is harder to express and less efficient to validate.

### 2.5 Why iao:Document and not abstract iao:InformationContentEntity

Same rationale as Narrative § 1.4. A NarrativePostMembership is a bounded, IRI-identified information record — it is the prototypical Document-pattern under IAO. Under abstract ICE the placement would lose the bounded-artefact semantics.

### 2.6 Why not bfo:Process or bfo:Role

- **Why not bfo:Process?** A Process is an occurrent — it unfolds in time. The *act of attaching* a post to a narrative IS a process (instantaneous event in the editorial workflow), but the *resulting membership record* is the continuant outcome of that process. Modeling the act is out of scope; modeling the record is in scope. Recording an event is GDC; the event itself is a Process.
- **Why not bfo:Role?** Role is for a continuant that is borne by an entity in a social/institutional context (e.g., student-role borne by a Person). A NarrativePostMembership is a *record* of which role a Post plays in a Narrative — but the record is not itself a role-bearer. The role qualifier (`ei:memberRole → skos:Concept`) is the role-pointer; the membership record carries it.

### 2.7 Disjointness obligations

Same as Narrative § 1.5. `ei:NarrativePostMembership` is disjoint from BFO IndependentContinuant siblings via BFO inheritance. Not disjoint from sibling Documents (`ei:Narrative`, `ei:Post`, `ei:PodcastEpisode`) at the OWL level by default. Optional `DisjointClasses(...)` for defense-in-depth (see § 1.5).

### 2.8 Ambiguity score

**1.** This is the highest-ambiguity placement in V2. Score 1 (not 2) because the multi-agent BFO/OEO modeling review pre-ratified it. The candidate categories considered (and rejected) are documented in § 2.6 above. The genuine alternative was *what kind* of GDC — `iao:Document` vs abstract `iao:InformationContentEntity` — and the resolution mirrors Narrative (iao:Document for bounded artefacts).

No reviewer escalation needed (ambiguity < 2). The pre-ratification by multi-agent design review is recorded in the source plan §1; no Class C reviewer signature required by the LLM verification policy.

---

## 3. SKOS schemes — no new BFO placements

The 4 new SKOS schemes (`ei:concept/argument-pattern`, `ei:concept/narrative-role`, `ei:concept/editorial-supplement`, `ei:concept/topic` aggregator) declare `skos:Concept` instances. SKOS is BFO-orthogonal — `skos:Concept` is not BFO-typed in our import, so the 30 new concept instances (7 patterns + 4 roles + 19 supplements) carry no BFO placements.

This is consistent with V0/V1: `concept-schemes/aggregation-type.ttl` and `concept-schemes/temporal-resolution.ttl` declare `skos:Concept` instances without BFO leaves. The architect should NOT add `rdfs:subClassOf bfo:0000023` or similar to any of the 30 new concepts.

---

## 4. OEO topic subset — no new BFO placements

The rebuilt `imports/oeo-topic-subset.ttl` is a `robot extract --method BOT` output from `oeo-full.owl`, BFO+RO-stripped per the V1 remediation pattern (using `imports/upper-axiom-leak-terms.txt` + `imports/bfo-terms-to-remove.txt`). After stripping:
- 41 OEO classes admitted as `owl:Class` declarations
- BFO axioms stripped: 0 BFO references
- RO axioms stripped: 0 RO references
- IAO axioms preserved (some OEO classes inherit IAO ICE / data-item parents, e.g., `OEO_xxx subClassOf IAO_0000027`)

The IAO chain is preserved intentionally — this is the same pattern as V1's `imports/oeo-{technology,carrier}-subset-fixed.ttl`. Empirical reasoner trace from V1 confirmed HermiT stays clean with this configuration.

The new V2 import does NOT introduce new local BFO placements. The 41 OEO classes appear as values of `ei:narrativeAboutTopic` via OWL 2 punning (each IRI denotes both an `owl:Class` from the OEO subset import and a `skos:Concept` individual when the architect emits `oeo:OEO_xxx skos:inScheme ei:concept/oeo-topic, ei:concept/topic` in `oeo-topics.ttl`).

---

## 5. V2 BFO ambiguity register

| Class | Candidate categories | Ambiguity | Reviewer | Decision | Rationale |
|---|---|---|---|---|---|
| `ei:Narrative` | iao:Document; abstract iao:InformationContentEntity | 0 | — | iao:Document | Mirrors V0 Post/PodcastEpisode; bounded artefact with stable IRI |
| `ei:NarrativePostMembership` | iao:Document; abstract iao:ICE; bfo:Process; bfo:Role | 1 | — | iao:Document | Pre-ratified by source plan §3.3 multi-agent review; alternatives explored in § 2.6 above |
| All V2 `skos:Concept` instances (7 + 4 + 19 = 30) | not BFO-typed | 0 | — | not BFO-typed | SKOS is BFO-orthogonal; matches V0/V1 SKOS scheme pattern |

No ambiguity ≥ 2 in V2. No reviewer escalation required for V2 BFO placements. The pre-ratification of `NarrativePostMembership` by multi-agent design review is recorded in source plan §1 as a critical finding.

---

## 6. Updated BFO leaf counts

| BFO leaf | V0 count | V1 count | V2 count | V2 change |
|---|---|---|---|---|
| `bfo:Object` | 1 (`ei:Expert`) | 1 | 1 | unchanged |
| `bfo:ObjectAggregate` | 1 (`ei:Organization`) | 1 | 1 | unchanged |
| `bfo:Role` | 2 | 3 | 3 | unchanged |
| `bfo:GDC` (via `iao:ICE` / `iao:Document`) | 15 | 15 | **17** | **+2** (Narrative, NarrativePostMembership) |
| `bfo:TemporalRegion` | 1 | 1 | 1 | unchanged |

**Total local class count: V0 = 21, V1 = 22, V2 = 24.** Within the middle-out budget. Imports add OEO + QUDT + topic-OEO classes but those are not local.

No `bfo:Process`, `bfo:Quality`, `bfo:Function`, `bfo:Disposition`, or `bfo:ImmaterialEntity` classes in V2. The 30 new SKOS Concepts are not BFO-typed (consistent with V0/V1 SKOS pattern).

---

## 7. Architect inheritance summary

| Action | Module | Note |
|---|---|---|
| Mint `ei:Narrative` class | `modules/editorial.ttl` (NEW module) | Use V0 Post template; substitute name; parent `iao:0000310` |
| Mint `ei:NarrativePostMembership` class | `modules/editorial.ttl` | Use V0 Post template; substitute name; parent `iao:0000310` |
| (Optional) Add `DisjointClasses(ei:Narrative, ei:Post, ei:PodcastEpisode, ei:NarrativePostMembership)` | `modules/editorial.ttl` | Defense-in-depth disjointness |
| Run `robot reason --reasoner hermit` after editorial module added | validation | V2 closure must remain HermiT-clean |
| No imports change at the BFO level | — | iao:0000310 already imported via V0 IAO MIREOT; no new BFO axioms needed |

V2 BFO alignment is a small, additive change. The architect's task is to mint two `iao:Document`-subtyped classes following the V0 Post template; no V0/V1 BFO placements are touched.
