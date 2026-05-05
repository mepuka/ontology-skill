# Property Design — `energy-intel`, V2 Delta (Editorial Extension)

**Authored:** 2026-05-04 by `ontology-conceptualizer` (V2 iteration)
**Predecessor:** [property-design-v1.md](property-design-v1.md) (V1; commit `1d8f9da`)
**Consumer:** `ontology-architect` (authors OWL axioms and SHACL shapes from this spec).

`intent:` values: `infer` (use OWL domain/range for inference), `validate` (SHACL constraint), `restrict` (per-class OWL restriction), `annotate` (annotation property, no constraint).

This document is a **delta** to V1 property-design-v1.md. Only V2 additions are listed. V0/V1 properties not restated here are unchanged.

---

## 0. Scope of V2 property changes

V2 adds **6 new object properties**. No V0 or V1 property is modified, deprecated, or deleted.

| Change kind | Property | Module |
|---|---|---|
| **Added** | `ei:hasNarrativePostMembership` | `editorial` (NEW) |
| **Added** | `ei:memberPost` | `editorial` |
| **Added** | `ei:memberRole` | `editorial` |
| **Added** | `ei:narrativeMentionsExpert` | `editorial` |
| **Added** | `ei:narrativeAppliesPattern` | `editorial` |
| **Added** | `ei:narrativeAboutTopic` | `editorial` |
| **Reused (no local addition)** | `skos:related` (between argument-pattern concepts) | imported |
| **Reused (no local addition)** | `skos:notation` (on supplement IRIs) | imported |

---

## 1. New object property — `ei:hasNarrativePostMembership`

| Field | Value |
|---|---|
| Name | `ei:hasNarrativePostMembership` |
| Type | `owl:ObjectProperty` |
| Domain | `ei:Narrative` |
| Range | `ei:NarrativePostMembership` |
| Cardinality on domain | 0..n (a Narrative has 0 or more memberships; order is not preserved per scope-v2.md Open Question 3) |
| Characteristics | none |
| Inverse | (no named inverse property in V2; reverse walks use SPARQL `^` operator or rebound triples) |
| RO parent | `RO:0002351` (has member) — closest match; the membership is a "member" of the narrative in the editorial sense. Architect may choose to omit the RO parent if it adds reasoner overhead with no CQ benefit. |
| Intent | `infer + restrict` (domain/range for inference; SHACL closed-shape constraint for the qualified cardinality invariant on (Narrative, Post)) |
| Source CQ | CQ-N2, CQ-N3, CQ-N6, CQ-N7, CQ-N8 |

**Source axiom (Manchester sketch, for architect):**
```turtle
ei:hasNarrativePostMembership a owl:ObjectProperty ;
  rdfs:domain ei:Narrative ;
  rdfs:range  ei:NarrativePostMembership ;
  rdfs:label "has narrative-post membership"@en ;
  skos:definition
    "Links a Narrative to a NarrativePostMembership record. A Narrative
    has zero or more memberships, one per post it includes. Order is not
    preserved; cardinality `many`. The closed-shape invariant
    sh:qualifiedMaxCount 1 per (Narrative, Post) pair is enforced via
    SHACL ei:NarrativePostMembershipShape."@en .
```

---

## 2. New object property — `ei:memberPost`

| Field | Value |
|---|---|
| Name | `ei:memberPost` |
| Type | `owl:ObjectProperty`, `owl:FunctionalProperty` |
| Domain | `ei:NarrativePostMembership` |
| Range | `ei:Post` |
| Cardinality on domain | exactly 1 (Functional gives upper bound) + `sh:minCount 1` via SHACL |
| Characteristics | Functional |
| Inverse | (none in V2) |
| RO parent | none — this is the "subject" component of a reified n-ary relation, no clean RO mapping |
| Intent | `infer + restrict + validate` |
| Source CQ | CQ-N2, CQ-N3, CQ-N6, CQ-N7 |

**Source axiom (Manchester sketch):**
```turtle
ei:memberPost a owl:ObjectProperty, owl:FunctionalProperty ;
  rdfs:domain ei:NarrativePostMembership ;
  rdfs:range  ei:Post ;
  rdfs:label "member post"@en ;
  skos:definition
    "Functional pointer from a NarrativePostMembership to the Post it
    references. Each membership has exactly one post."@en .

ei:NarrativePostMembership rdfs:subClassOf
  [ a owl:Restriction ;
    owl:onProperty ei:memberPost ;
    owl:cardinality 1 ;
    owl:onClass ei:Post ] .
```

**Why Functional + cardinality 1:**
- Functional gives the OWL upper bound (at most 1).
- Without the cardinality 1 restriction, OWA would allow a membership without a post (lower bound 0). The SHACL `sh:minCount 1` and the OWL `owl:cardinality 1` together enforce exactly 1.

---

## 3. New object property — `ei:memberRole`

| Field | Value |
|---|---|
| Name | `ei:memberRole` |
| Type | `owl:ObjectProperty`, `owl:FunctionalProperty` |
| Domain | `ei:NarrativePostMembership` |
| Range | `skos:Concept` (broad at OWL; SHACL constrained to ei:concept/narrative-role members per V2-CQ-Q-4) |
| Cardinality on domain | exactly 1 (Functional gives upper bound) + `sh:minCount 1` + `sh:maxCount 1` via SHACL |
| Characteristics | Functional |
| Inverse | (none) |
| RO parent | none |
| Intent | `infer + restrict + validate` |
| Source CQ | CQ-N2, CQ-N3, CQ-N8 |

**Source axiom (Manchester sketch):**
```turtle
ei:memberRole a owl:ObjectProperty, owl:FunctionalProperty ;
  rdfs:domain ei:NarrativePostMembership ;
  rdfs:range  skos:Concept ;
  rdfs:label "member role"@en ;
  skos:definition
    "Functional role qualifier of a NarrativePostMembership. Constrained
    at the SHACL layer to values in the ei:concept/narrative-role
    scheme (lead, supporting, counter, context). Each membership has
    exactly one role."@en .

ei:NarrativePostMembership rdfs:subClassOf
  [ a owl:Restriction ;
    owl:onProperty ei:memberRole ;
    owl:cardinality 1 ;
    owl:onClass skos:Concept ] .
```

**SHACL companion** (V2-CQ-Q-4 decision: SHACL-only enumeration):
```turtle
ei:NarrativePostMembershipShape
  sh:targetClass ei:NarrativePostMembership ;
  sh:property [
    sh:path ei:memberRole ;
    sh:in (
      <https://w3id.org/energy-intel/concept/narrative-role/lead>
      <https://w3id.org/energy-intel/concept/narrative-role/supporting>
      <https://w3id.org/energy-intel/concept/narrative-role/counter>
      <https://w3id.org/energy-intel/concept/narrative-role/context>
    ) ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
    sh:severity sh:Violation ;
  ] .
```

**Why SHACL-only (V2-CQ-Q-4 rationale):**

1. **OWA fit.** `owl:allValuesFrom` over a closed enumeration would force closure at the OWL level. Any `ei:memberRole` value not declared in the closed enumeration would either trigger an OWL inconsistency (under closure) or get classified as a member of the enumeration (without closure). Both behaviors are wrong for a SKOS scheme that may grow over time (e.g., a future "background" role).
2. **Convention from V0+V1.** `ei:narrativeAppliesPattern` (V2 — § 5 below) and `ei:aboutTechnology` (V0/V1) both keep their OWL ranges broad (`skos:Concept`) and use SHACL for scheme membership. V2-Q-4 follows this established pattern.
3. **SHACL is closed-world.** SHACL validation runs over a known graph snapshot; `sh:in` enumeration is a clean closed-world check. This is the right tool for "value MUST be in this enumeration."
4. **Functional + sh:maxCount 1 alignment.** `ei:memberRole` is `owl:FunctionalProperty` at the OWL level (gives reasoner-side fusing — two distinct roles on the same membership force `owl:sameAs` or inconsistency) AND `sh:maxCount 1` at the SHACL level (gives validator-side detection of multi-value violations). Defense-in-depth.

---

## 4. New object property — `ei:narrativeMentionsExpert`

| Field | Value |
|---|---|
| Name | `ei:narrativeMentionsExpert` |
| Type | `owl:ObjectProperty` |
| Domain | `ei:Narrative` |
| Range | `foaf:Person` (V1-widened from `ei:Expert`; consistent with V1 § 3.1 widening) |
| Cardinality on domain | 0..n |
| Characteristics | none |
| Inverse | (none in V2) |
| RO parent | `IAO:0000136` (is about) — the Narrative is *about* the experts it mentions. |
| Intent | `infer` |
| Source CQ | CQ-N6 |

**Source axiom (Manchester sketch):**
```turtle
ei:narrativeMentionsExpert a owl:ObjectProperty ;
  rdfs:domain ei:Narrative ;
  rdfs:range  foaf:Person ;
  rdfs:label "narrative mentions expert"@en ;
  skos:definition
    "Links a Narrative to an Expert mentioned in it. Auto-derived from
    contained posts at import time by walking
    hasNarrativePostMembership/memberPost/authoredBy. The fallback
    walk in CQ-N6 covers the case where auto-derivation has not run.
    Range is foaf:Person (V1-widened from ei:Expert), matching the
    V1 widening of authoredBy/spokenBy."@en .
```

**Why a separate predicate vs. just walking the chain:**
- Performance: a direct edge avoids a 3-hop walk (`Narrative → Membership → Post → authoredBy`) at query time. Materialising the edge at import time turns CQ-N6 into a 1-hop lookup.
- Override: the editorial pipeline may want to assert "this Narrative mentions Expert X" even when X is not in any contained post (e.g., contextual mention in the Narrative body text). The explicit edge supports this case.
- Defense-in-depth: CQ-N6 uses `UNION` of explicit edge + property-path fallback, so the edge is optional but recommended.

**No SHACL constraint** on this property; auto-derivation is best-effort, and missing edges should not block validation.

---

## 5. New object property — `ei:narrativeAppliesPattern`

| Field | Value |
|---|---|
| Name | `ei:narrativeAppliesPattern` |
| Type | `owl:ObjectProperty` |
| Domain | `ei:Narrative` |
| Range | `skos:Concept` (broad at OWL; SHACL constrained to ei:concept/argument-pattern members) |
| Cardinality on domain | 0..1 |
| Characteristics | none (NOT Functional — see below) |
| Inverse | (none) |
| RO parent | `IAO:0000136` (is about) — distant, not perfect. Could be left without an RO parent. |
| Intent | `infer + restrict + validate` |
| Source CQ | CQ-N5 |

**Source axiom (Manchester sketch):**
```turtle
ei:narrativeAppliesPattern a owl:ObjectProperty ;
  rdfs:domain ei:Narrative ;
  rdfs:range  skos:Concept ;
  rdfs:label "narrative applies pattern"@en ;
  skos:definition
    "Optional pointer from a Narrative to the argument pattern it
    applies. Range is broad skos:Concept; SHACL constrains the value
    to be a member of ei:concept/argument-pattern."@en .

ei:Narrative rdfs:subClassOf
  [ a owl:Restriction ;
    owl:onProperty ei:narrativeAppliesPattern ;
    owl:maxCardinality 1 ;
    owl:onClass skos:Concept ] .
```

**SHACL companion:**
```turtle
ei:NarrativeShape
  sh:targetClass ei:Narrative ;
  sh:property [
    sh:path ei:narrativeAppliesPattern ;
    sh:maxCount 1 ;
    sh:nodeKind sh:IRI ;
    sh:sparql [
      sh:select """
        SELECT $this ?value WHERE {
          $this ei:narrativeAppliesPattern ?value .
          FILTER NOT EXISTS {
            ?value skos:inScheme <https://w3id.org/energy-intel/concept/argument-pattern> .
          }
        }
      """ ] ;
    sh:severity sh:Violation ;
  ] .
```

**Why max-cardinality-1 (not Functional):**
- A Narrative may legitimately apply *no* argument pattern (during early draft state); cardinality 0..1.
- Functional would mean "if two values are asserted, fuse via owl:sameAs". For SKOS concepts that's wrong — two distinct argument patterns are different concepts, not aliases. Better to use `owl:maxCardinality 1` which prohibits two distinct values without forcing fusion.
- The decision diverges from `ei:memberRole` (which IS Functional) because `memberRole` is a required slot (every membership has exactly 1 role) whereas `narrativeAppliesPattern` is optional (a Narrative may have 0 patterns).

**Why SHACL for scheme membership:** Same V2-CQ-Q-4 rationale as `ei:memberRole` (§ 3) — SHACL closed-world `sh:sparql` check is the right tool for "value MUST be in this scheme".

---

## 6. New object property — `ei:narrativeAboutTopic`

| Field | Value |
|---|---|
| Name | `ei:narrativeAboutTopic` |
| Type | `owl:ObjectProperty` |
| Domain | `ei:Narrative` |
| Range | `owl:Thing` (broadest; SHACL constrained to `owl:Class ∪ skos:Concept` per granularity contract — see CQ-T3) |
| Cardinality on domain | 0..n |
| Characteristics | none |
| Inverse | (none) |
| RO parent | `IAO:0000136` (is about) — the Narrative is *about* the topics it covers. |
| Intent | `infer + validate` |
| Source CQ | CQ-N4, CQ-T3 |

**Source axiom (Manchester sketch):**
```turtle
ei:narrativeAboutTopic a owl:ObjectProperty ;
  rdfs:domain ei:Narrative ;
  rdfs:range  owl:Thing ;
  rdfs:label "narrative about topic"@en ;
  skos:definition
    "Links a Narrative to one or more topics. Topic IRIs are either
    OEO class IRIs (admitted via OWL 2 punning) or Skygest editorial
    supplement IRIs in the ei:concept/ namespace. SHACL granularity
    contract forbids bare owl:NamedIndividual values (every value
    must resolve to owl:Class or skos:Concept)."@en .
```

**SHACL companion (granularity contract — CQ-T3):**
```turtle
ei:NarrativeShape
  sh:property [
    sh:path ei:narrativeAboutTopic ;
    sh:nodeKind sh:IRI ;
    sh:or (
      [ sh:class owl:Class ]
      [ sh:class skos:Concept ]
    ) ;
    sh:severity sh:Violation ;
    sh:message "narrativeAboutTopic value must be owl:Class or skos:Concept; never bare owl:NamedIndividual" ;
  ] .
```

**Why range owl:Thing (broadest):**
- Range `skos:Concept` would be too narrow — OEO IRIs are `owl:Class` (under the OEO subset import), not `skos:Concept`. Punning makes them *also* skos:Concept individuals when the architect emits `oeo:OEO_xxx skos:inScheme ei:concept/oeo-topic` — but the punning is one-directional (the IRI denotes both, but the OEO subset declares only `owl:Class`).
- Range `owl:Class` would exclude Skygest supplement IRIs (which are `skos:Concept` instances, not classes).
- Range `owl:Thing` is the union; SHACL `sh:or` enumeration enforces the granularity contract precisely.
- The granularity contract is a strict invariant of the editorial domain: a "topic" must describe a *kind of thing* (a class or a concept), never a specific instance. The contract is encoded in CQ-T3.

**Why no Functional:** A Narrative may legitimately be about multiple topics (cardinality `many`).

---

## 7. Reused properties (no new local mints)

### 7.1 `skos:related` (between argument-pattern concepts)

| Field | Value |
|---|---|
| Source | imported (V0 SKOS import) |
| Local use | between `skos:Concept` instances in `ei:concept/argument-pattern` to express related-pattern relationships |
| Local axiom | none — the relation is asserted between concepts, not against a local property |

The `related_patterns:` frontmatter in `/skygest-editorial/references/argument-patterns/{stem}.md` (currently empty for all 7) maps to `skos:related` triples between concepts. This lifts the phantom `related_patterns` from `BuildGraph.ts` without minting a custom predicate.

### 7.2 `skos:notation` (on supplement IRIs)

| Field | Value |
|---|---|
| Source | imported (V0 SKOS import) |
| Local use | on Skygest supplement IRIs (`ei:concept/data-center-demand` etc.) to carry the legacy editorial topic_slug for migration-period queryability |
| Local axiom | none — `skos:notation` is asserted as a literal on each supplement individual |

Per V2-CQ-Q-3 recommendation in scope-v2.md Open Question 4. Used by CQ-T2 (legacy slug → canonical IRI lookup).

---

## 8. Property-design summary table

| Property | Type | Domain | Range | Cardinality | Characteristics | Intent | RO parent |
|---|---|---|---|---|---|---|---|
| `ei:hasNarrativePostMembership` | ObjectProperty | Narrative | NarrativePostMembership | 0..n | — | infer + restrict | RO:0002351 (or omit) |
| `ei:memberPost` | ObjectProperty, FunctionalProperty | NarrativePostMembership | Post | exactly 1 | Functional | infer + restrict + validate | (none) |
| `ei:memberRole` | ObjectProperty, FunctionalProperty | NarrativePostMembership | skos:Concept | exactly 1 | Functional | infer + restrict + validate | (none) |
| `ei:narrativeMentionsExpert` | ObjectProperty | Narrative | foaf:Person | 0..n | — | infer | IAO:0000136 |
| `ei:narrativeAppliesPattern` | ObjectProperty | Narrative | skos:Concept | 0..1 | — | infer + restrict + validate | (optional IAO:0000136) |
| `ei:narrativeAboutTopic` | ObjectProperty | Narrative | owl:Thing | 0..n | — | infer + validate | IAO:0000136 |

---

## 9. Relation-semantics sheet (per [`_shared/relation-semantics.md`](../../../.claude/skills/_shared/relation-semantics.md))

| Property | Object vs Data | RO parent (or rationale) | Characteristics | Intent | Notes |
|----------|-----------------|--------------------------|-----------------|--------|-------|
| `ei:hasNarrativePostMembership` | object | RO:0002351 (has member) — closest match; can be omitted if reasoner overhead | none | infer + restrict | Many: a Narrative has 0..n memberships; SHACL closed-shape per (Narrative, Post) |
| `ei:memberPost` | object | none — reified-relation subject component, no clean RO parent | Functional | infer + restrict + validate | Exactly 1 per membership |
| `ei:memberRole` | object | none — reified-relation qualifier component | Functional | infer + restrict + validate | Exactly 1 per membership; SHACL `sh:in` enumeration over 4 roles |
| `ei:narrativeMentionsExpert` | object | IAO:0000136 (is about) | none | infer | Auto-derived at import; explicit assertion + property-path fallback in CQ-N6 |
| `ei:narrativeAppliesPattern` | object | IAO:0000136 (is about) — distant; can be omitted | none | infer + restrict + validate | 0..1; SHACL `sh:sparql` for scheme membership |
| `ei:narrativeAboutTopic` | object | IAO:0000136 (is about) | none | infer + validate | 0..n; SHACL granularity contract (`owl:Class ∪ skos:Concept`) |

All six are object properties (no data properties added in V2). All Characteristics columns are explicitly stated — silent omission would not match the workspace policy.

---

## 10. Updated characteristics audit (V2 deltas only)

Cross-reference V0 [property-design.md § 7](property-design.md) and V1 [property-design-v1.md § 5](property-design-v1.md) for prior audit. V2 additions:

| Property | Functional | InvFunctional | Transitive | Symmetric | Asymmetric | Reflexive | Irreflexive |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `ei:hasNarrativePostMembership` (new) | no | no | no | no | no | no | no |
| `ei:memberPost` (new) | **yes** | no | no | no | no | no | no |
| `ei:memberRole` (new) | **yes** | no | no | no | no | no | no |
| `ei:narrativeMentionsExpert` (new) | no | no | no | no | no | no | no |
| `ei:narrativeAppliesPattern` (new) | no | no | no | no | no | no | no |
| `ei:narrativeAboutTopic` (new) | no | no | no | no | no | no | no |

Two Functional properties added in V2 (`memberPost`, `memberRole`). InverseFunctional is **NOT** declared on either — multiple memberships may share the same Post (when a Post is in multiple Narratives via CQ-N3) or the same role (when many memberships are role=lead across different Narratives). Both are intentional.

---

## 11. Open property-design questions (none for V2)

The four V2-Q questions in [requirements-approval-v2.yaml § handoff_to_conceptualizer.blocking_questions](requirements-approval-v2.yaml) are answered:

- **V2-CQ-Q-1** (SKOS scheme split): split + aggregator. See [conceptual-model-v2.md § 4](conceptual-model-v2.md).
- **V2-CQ-Q-2** (OEO topic IRI verification): all 41 candidates pass. See [topic-vocabulary-mapping.md](topic-vocabulary-mapping.md).
- **V2-CQ-Q-3** (NarrativePostMembership IRI derivation): sha256 truncated to 16 hex chars. See [narrative-identity-rule.md](narrative-identity-rule.md).
- **V2-CQ-Q-4** (`ei:memberRole` range constraint): SHACL-only. See § 3 above.

V2 introduces no new open property-design questions.

---

## 12. Architect handoff summary

| Action | Where | Notes |
|---|---|---|
| Mint 6 V2 object properties | `modules/editorial.ttl` | Use property templates from V0 `modules/media.ttl`; substitute names |
| Add Functional characteristic to `ei:memberPost` and `ei:memberRole` | `modules/editorial.ttl` | Two `owl:FunctionalProperty` declarations |
| Add SubClassOf cardinality restrictions on NarrativePostMembership for memberPost (exactly 1) and memberRole (exactly 1) | `modules/editorial.ttl` | Two `owl:Restriction` axioms |
| Add SubClassOf max-cardinality restriction on Narrative for narrativeAppliesPattern (max 1) | `modules/editorial.ttl` | One `owl:maxCardinality 1` restriction |
| Wire SHACL `ei:NarrativePostMembershipShape` and `ei:NarrativeShape` | `shapes/editorial.ttl` | New file; see § 3, 5, 6 above for shape sketches |
| Encode granularity contract (CQ-T3) as SHACL `sh:or` enumeration on narrativeAboutTopic | `shapes/editorial.ttl` | See § 6 SHACL companion |
| Encode SHACL `sh:in` enumeration on memberRole over 4 narrative-role concepts | `shapes/editorial.ttl` | See § 3 SHACL companion |
| Encode SHACL `sh:sparql` scheme-membership check on narrativeAppliesPattern | `shapes/editorial.ttl` | See § 5 SHACL companion |
| Run `robot reason --reasoner hermit` after editorial module added | validation | V2 closure must remain HermiT-clean |
| Run `pyshacl` after editorial shapes added | validation | All 4 SHACL invariants must pass on a well-formed fixture |

See [conceptualizer-to-architect-handoff-v2.md](conceptualizer-to-architect-handoff-v2.md) for the integrated architect plan.
