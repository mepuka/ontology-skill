# V2 Axiom Plan — `energy-intel`

**Authored:** 2026-05-04 by `ontology-conceptualizer` (V2 iteration)
**Predecessor:** [axiom-plan-v1.md](axiom-plan-v1.md) (V1; commit `1d8f9da`)
**Consumer:** `ontology-architect` (lands the axioms in V2 architect session)

This document is the **CQ coverage map** for V2: every Must-Have CQ from [`competency-questions-v2.yaml`](competency-questions-v2.yaml) appears here with its target axiom pattern, OWL profile, closure decision, and OWA trap analysis. Validator reads this as the contract that no Must-Have CQ has been forgotten.

---

## 1. CQ coverage map

Per [`_shared/closure-and-open-world.md`](../../../.claude/skills/_shared/closure-and-open-world.md) and [`_shared/pattern-catalog.md`](../../../.claude/skills/_shared/pattern-catalog.md).

### CQ-N1 — Deterministic Narrative IRI lookup

| Aspect | Value |
|---|---|
| Source CQ | CQ-N1 (must_have) |
| Pattern | Class declaration (#1) + identity-rule encoded outside ontology |
| Axiom | `ei:Narrative a owl:Class ; rdfs:subClassOf iao:0000310 .` |
| Profile | OWL 2 EL safe (also DL) |
| Closure required | No |
| OWA trap | No — the SPARQL `BIND(IRI(CONCAT(...)) AS ?narrative) ; ?narrative a ei:Narrative` returns 0 rows iff the entity does not exist (correct OWA: absence of fact ≠ negation) |

### CQ-N2 — Forward walk Narrative → memberships → (Post, role)

| Aspect | Value |
|---|---|
| Source CQ | CQ-N2 (must_have) |
| Pattern | Reified n-ary relation (#9) |
| Axioms | `ei:NarrativePostMembership a owl:Class ; rdfs:subClassOf iao:0000310 .` plus 3 object property declarations: `ei:hasNarrativePostMembership`, `ei:memberPost` (Functional), `ei:memberRole` (Functional). Class-level cardinality restrictions on NarrativePostMembership: `memberPost cardinality 1`, `memberRole cardinality 1`. |
| Profile | OWL 2 DL (Functional + cardinality is DL-safe) |
| Closure required | No (the CQ is a SELECT over an enumerated walk; it does not require closure) |
| OWA trap | No — empty result is a legitimate outcome (a Narrative may have no posts attached yet) |

### CQ-N3 — Reverse walk Post → memberships → Narrative

| Aspect | Value |
|---|---|
| Source CQ | CQ-N3 (must_have) |
| Pattern | Same as CQ-N2 (reified n-ary relation walks bidirectionally via SPARQL) |
| Axioms | Same as CQ-N2 (no new axioms) |
| Profile | OWL 2 DL |
| Closure required | No |
| OWA trap | No |

### CQ-N4 — Filter Narratives by topic

| Aspect | Value |
|---|---|
| Source CQ | CQ-N4 (must_have) |
| Pattern | Object property + range constraint (SHACL) (#3 + value partition variant) |
| Axioms | `ei:narrativeAboutTopic a owl:ObjectProperty ; rdfs:domain ei:Narrative ; rdfs:range owl:Thing .` plus SHACL `sh:or` enumeration (`owl:Class ∪ skos:Concept`) for granularity contract |
| Profile | OWL 2 DL |
| Closure required | No (the SHACL granularity is closed-world by definition) |
| OWA trap | No — empty result is legitimate (a Narrative may have no topics) |

### CQ-N5 — Filter Narratives by argument pattern

| Aspect | Value |
|---|---|
| Source CQ | CQ-N5 (must_have) |
| Pattern | Object property + range constraint (SHACL `sh:sparql` for scheme membership) |
| Axioms | `ei:narrativeAppliesPattern a owl:ObjectProperty ; rdfs:domain ei:Narrative ; rdfs:range skos:Concept .` plus class-level max-cardinality restriction (`max 1 skos:Concept`). SHACL: `sh:sparql` checks the value is `skos:inScheme ei:concept/argument-pattern` |
| Profile | OWL 2 DL |
| Closure required | No |
| OWA trap | No |

### CQ-N6 — Auto-derived expert mentions

| Aspect | Value |
|---|---|
| Source CQ | CQ-N6 (should_have) |
| Pattern | Object property declaration + property-path fallback (#1 + cross-walk) |
| Axioms | `ei:narrativeMentionsExpert a owl:ObjectProperty ; rdfs:domain ei:Narrative ; rdfs:range foaf:Person .` |
| Profile | OWL 2 EL safe |
| Closure required | No |
| OWA trap | No — UNION of explicit + property-path fallback covers both populated and unpopulated cases |

### CQ-N7 — SHACL invariant on membership uniqueness per (Narrative, Post)

| Aspect | Value |
|---|---|
| Source CQ | CQ-N7 (must_have) |
| Pattern | SHACL closed-shape constraint with `sh:qualifiedMaxCount 1` |
| Axioms | OWL: none beyond CQ-N2's class declarations. SHACL `ei:NarrativePostMembershipShape`: `sh:targetClass ei:NarrativePostMembership ; sh:property [ sh:path [sh:inversePath ei:hasNarrativePostMembership] ; ... ; sh:qualifiedValueShape [ sh:property [ sh:path ei:memberPost ; sh:hasValue ?post ] ] ; sh:qualifiedMaxCount 1 ]` |
| Profile | OWL 2 DL (SHACL is layered on top; not part of OWL profile) |
| Closure required | Yes — the invariant is closed-world (every Membership pair is either single or in violation; absence of a competing membership means the constraint holds) |
| OWA trap | No (SHACL is closed-world by definition) — SHACL is the right tool for this invariant; OWL `owl:cardinality 1` would not capture "per (Narrative, Post) pair" semantics |

### CQ-N8 — SHACL warning on multi-lead per Narrative

| Aspect | Value |
|---|---|
| Source CQ | CQ-N8 (should_have) |
| Pattern | SHACL constraint with `sh:severity sh:Warning` |
| Axioms | OWL: none beyond CQ-N2. SHACL warning shape on `ei:Narrative`: at most one membership where `memberRole = ei:concept/narrative-role/lead` |
| Profile | OWL 2 DL (SHACL layered) |
| Closure required | Yes (closed-world for SHACL) |
| OWA trap | No |

### CQ-T1 — Topic-metadata lookup by IRI

| Aspect | Value |
|---|---|
| Source CQ | CQ-T1 (must_have) |
| Pattern | OPTIONAL-laced direct lookup over SKOS metadata (#1) |
| Axioms | None new — uses imported SKOS properties (`skos:prefLabel`, `skos:altLabel`, `skos:broader`, `skos:narrower`). Architect emits `skos:prefLabel` etc. on every supplement IRI in `concept-schemes/oeo-topics.ttl`. |
| Profile | OWL 2 EL safe |
| Closure required | No |
| OWA trap | No — OPTIONAL columns may legitimately be null |

### CQ-T2 — Legacy slug → canonical IRI(s)

| Aspect | Value |
|---|---|
| Source CQ | CQ-T2 (should_have) |
| Pattern | `skos:notation` annotation lookup (annotation property pattern) |
| Axioms | None new — uses imported `skos:notation`. Architect emits `?supplementIri skos:notation "{legacy-slug}"` on every supplement IRI. |
| Profile | OWL 2 EL safe |
| Closure required | No |
| OWA trap | No — empty result for an unrecognized slug is legitimate (the slug was never mapped, e.g., `Renewable` which V1 maps to null) |

### CQ-T3 — Granularity contract validator

| Aspect | Value |
|---|---|
| Source CQ | CQ-T3 (must_have) |
| Pattern | SHACL constraint with `sh:or` enumeration over `owl:Class ∪ skos:Concept` |
| Axioms | OWL: none. SHACL `ei:NarrativeShape` property shape on `ei:narrativeAboutTopic`: `sh:nodeKind sh:IRI ; sh:or ([sh:class owl:Class] [sh:class skos:Concept]) ; sh:severity sh:Violation` |
| Profile | OWL 2 DL (SHACL layered) |
| Closure required | Yes — SHACL is closed-world; the constraint is "every value MUST be one of these types" |
| OWA trap | No |

---

## 2. Coverage summary

| CQ | Priority | Pattern | Architect deliverable |
|---|---|---|---|
| CQ-N1 | must_have | Class declaration + identity-rule code | A1 (class), code (helper) |
| CQ-N2 | must_have | Reified n-ary | A2 (class), A4-A6 (3 props), A7-A8 (cardinality restrictions) |
| CQ-N3 | must_have | (same as CQ-N2) | (no new) |
| CQ-N4 | must_have | Object property + SHACL granularity | A11 (prop), S-V2-3 (SHACL granularity) |
| CQ-N5 | must_have | Object property + SHACL scheme membership | A10 (prop), A12 (max-cardinality), S-V2-2 (SHACL sparql) |
| CQ-N6 | should_have | Object property + property-path fallback | A9 (prop) |
| CQ-N7 | must_have | SHACL closed-shape qualified | S-V2-1 (SHACL qualifiedMaxCount) |
| CQ-N8 | should_have | SHACL warning | S-V2-4 (SHACL warning) |
| CQ-T1 | must_have | SKOS direct lookup | (concept-scheme content; no axiom layer) |
| CQ-T2 | should_have | SKOS notation lookup | (concept-scheme content; supplement IRIs carry skos:notation) |
| CQ-T3 | must_have | SHACL granularity enumeration | S-V2-3 (same as CQ-N4 but at granularity level) |

**11/11 V2 CQs covered.** No `missing_cq_link` would be raised. Must-Have CQs have all axioms identified; Should-Have CQs are covered by additive shapes.

---

## 3. Numbered architect axiom obligations (A1..A12)

The architect lands these as numbered axiom obligations (mirroring the V1 A1..A8 numbering). Each lives in `modules/editorial.ttl` (new file).

### A1 — Mint `ei:Narrative` class

| Aspect | Value |
|---|---|
| Module | `modules/editorial.ttl` (new) |
| CQ source | CQ-N1; supports CQ-N2..N6, N8 |
| Construct | SubClassOf (simple) |
| Profile | OWL 2 EL (also DL) |
| Reasoner pairing | HermiT |

```turtle
ei:Narrative a owl:Class ;
  rdfs:label "narrative"@en ;
  rdfs:subClassOf iao:0000310 ;
  skos:definition "A written editorial unit about energy-domain events that have been curated by an editor."@en .
```

### A2 — Mint `ei:NarrativePostMembership` class

| Aspect | Value |
|---|---|
| Module | `modules/editorial.ttl` |
| CQ source | CQ-N2, CQ-N3, CQ-N6, CQ-N7, CQ-N8 |
| Construct | SubClassOf (simple) |
| Profile | OWL 2 EL (also DL) |
| Reasoner pairing | HermiT |

```turtle
ei:NarrativePostMembership a owl:Class ;
  rdfs:label "narrative post membership"@en ;
  rdfs:subClassOf iao:0000310 ;
  skos:definition "An information artefact recording that a Narrative includes a Post in a specific role."@en .
```

### A3 — (Optional) DisjointClasses for documentary siblings

| Aspect | Value |
|---|---|
| Module | `modules/editorial.ttl` |
| CQ source | Defense-in-depth (no specific CQ; consistency aid) |
| Construct | DisjointClasses (binary or all-disjoint) |
| Profile | OWL 2 DL |

```turtle
[ a owl:AllDisjointClasses ;
  owl:members ( ei:Narrative ei:Post ei:PodcastEpisode ei:NarrativePostMembership ) ] .
```

Optional but recommended. Already-existing `ei:Post`, `ei:PodcastEpisode` from V0 are siblings under `iao:0000310`; V2 adds two more siblings. Disjointness is enforced informally by deterministic IRI rules (each class has a different IRI prefix), so this axiom is defense-in-depth.

### A4 — Mint `ei:hasNarrativePostMembership`

| Aspect | Value |
|---|---|
| Module | `modules/editorial.ttl` |
| CQ source | CQ-N2, CQ-N3, CQ-N6, CQ-N7, CQ-N8 |
| Construct | ObjectProperty + domain + range |
| Profile | OWL 2 DL (DL-safe; range is a class, not an enumeration) |

```turtle
ei:hasNarrativePostMembership a owl:ObjectProperty ;
  rdfs:domain ei:Narrative ;
  rdfs:range  ei:NarrativePostMembership ;
  rdfs:label "has narrative-post membership"@en .
```

### A5 — Mint `ei:memberPost` (FunctionalProperty)

| Aspect | Value |
|---|---|
| Module | `modules/editorial.ttl` |
| CQ source | CQ-N2, CQ-N3, CQ-N6, CQ-N7 |
| Construct | ObjectProperty + FunctionalProperty + domain + range |
| Profile | OWL 2 DL (Functional is DL-safe and EL-safe) |

```turtle
ei:memberPost a owl:ObjectProperty, owl:FunctionalProperty ;
  rdfs:domain ei:NarrativePostMembership ;
  rdfs:range  ei:Post ;
  rdfs:label "member post"@en .
```

### A6 — Mint `ei:memberRole` (FunctionalProperty)

| Aspect | Value |
|---|---|
| Module | `modules/editorial.ttl` |
| CQ source | CQ-N2, CQ-N3, CQ-N8 |
| Construct | ObjectProperty + FunctionalProperty + domain + range |
| Profile | OWL 2 DL |

```turtle
ei:memberRole a owl:ObjectProperty, owl:FunctionalProperty ;
  rdfs:domain ei:NarrativePostMembership ;
  rdfs:range  skos:Concept ;
  rdfs:label "member role"@en .
```

Range is broad `skos:Concept`; SHACL S-V2-2 below constrains to the 4 narrative-role concepts.

### A7 — Cardinality restriction on NarrativePostMembership for memberPost

| Aspect | Value |
|---|---|
| Module | `modules/editorial.ttl` |
| CQ source | CQ-N2, CQ-N3 |
| Construct | SubClassOf cardinality restriction |
| Profile | OWL 2 DL |

```turtle
ei:NarrativePostMembership rdfs:subClassOf
  [ a owl:Restriction ;
    owl:onProperty ei:memberPost ;
    owl:cardinality 1 ;
    owl:onClass ei:Post ] .
```

### A8 — Cardinality restriction on NarrativePostMembership for memberRole

| Aspect | Value |
|---|---|
| Module | `modules/editorial.ttl` |
| CQ source | CQ-N2, CQ-N3, CQ-N8 |
| Construct | SubClassOf cardinality restriction |
| Profile | OWL 2 DL |

```turtle
ei:NarrativePostMembership rdfs:subClassOf
  [ a owl:Restriction ;
    owl:onProperty ei:memberRole ;
    owl:cardinality 1 ;
    owl:onClass skos:Concept ] .
```

### A9 — Mint `ei:narrativeMentionsExpert`

| Aspect | Value |
|---|---|
| Module | `modules/editorial.ttl` |
| CQ source | CQ-N6 |
| Construct | ObjectProperty + domain + range |
| Profile | OWL 2 EL |

```turtle
ei:narrativeMentionsExpert a owl:ObjectProperty ;
  rdfs:domain ei:Narrative ;
  rdfs:range  foaf:Person ;
  rdfs:label "narrative mentions expert"@en .
```

### A10 — Mint `ei:narrativeAppliesPattern`

| Aspect | Value |
|---|---|
| Module | `modules/editorial.ttl` |
| CQ source | CQ-N5 |
| Construct | ObjectProperty + domain + range |
| Profile | OWL 2 DL |

```turtle
ei:narrativeAppliesPattern a owl:ObjectProperty ;
  rdfs:domain ei:Narrative ;
  rdfs:range  skos:Concept ;
  rdfs:label "narrative applies pattern"@en .
```

### A11 — Mint `ei:narrativeAboutTopic`

| Aspect | Value |
|---|---|
| Module | `modules/editorial.ttl` |
| CQ source | CQ-N4, CQ-T3 |
| Construct | ObjectProperty + domain + range |
| Profile | OWL 2 DL |

```turtle
ei:narrativeAboutTopic a owl:ObjectProperty ;
  rdfs:domain ei:Narrative ;
  rdfs:range  owl:Thing ;
  rdfs:label "narrative about topic"@en .
```

### A12 — Max-cardinality on Narrative for narrativeAppliesPattern

| Aspect | Value |
|---|---|
| Module | `modules/editorial.ttl` |
| CQ source | CQ-N5 |
| Construct | SubClassOf max-cardinality restriction |
| Profile | OWL 2 DL |

```turtle
ei:Narrative rdfs:subClassOf
  [ a owl:Restriction ;
    owl:onProperty ei:narrativeAppliesPattern ;
    owl:maxCardinality 1 ;
    owl:onClass skos:Concept ] .
```

---

## 4. SHACL shape obligations (S-V2-1..4)

Located in `shapes/editorial.ttl` (new file).

### S-V2-1 — NarrativePostMembership uniqueness per (Narrative, Post)

CQ source: CQ-N7 (must_have). Severity: `sh:Violation`.

```turtle
ei:NarrativePostMembershipShape
  a sh:NodeShape ;
  sh:targetClass ei:NarrativePostMembership ;
  sh:property [
    sh:path ei:memberPost ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
    sh:class ei:Post ;
    sh:severity sh:Violation ;
  ] ;
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

# Closed-shape constraint on (Narrative, Post) pair via SPARQL
ei:NarrativeUniqueMembershipShape
  a sh:NodeShape ;
  sh:targetClass ei:Narrative ;
  sh:sparql [
    sh:select """
      PREFIX ei: <https://w3id.org/energy-intel/>
      SELECT $this ?post WHERE {
        $this ei:hasNarrativePostMembership ?m1 ;
              ei:hasNarrativePostMembership ?m2 .
        ?m1 ei:memberPost ?post .
        ?m2 ei:memberPost ?post .
        FILTER(?m1 != ?m2)
      }
    """ ;
    sh:severity sh:Violation ;
    sh:message "At most one NarrativePostMembership per (Narrative, Post) pair."
  ] .
```

### S-V2-2 — narrativeAppliesPattern scheme membership

CQ source: CQ-N5 (must_have). Severity: `sh:Violation`.

```turtle
ei:NarrativeShape
  a sh:NodeShape ;
  sh:targetClass ei:Narrative ;
  sh:property [
    sh:path ei:narrativeAppliesPattern ;
    sh:maxCount 1 ;
    sh:nodeKind sh:IRI ;
    sh:sparql [
      sh:select """
        PREFIX ei: <https://w3id.org/energy-intel/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT $this ?value WHERE {
          $this ei:narrativeAppliesPattern ?value .
          FILTER NOT EXISTS {
            ?value skos:inScheme <https://w3id.org/energy-intel/concept/argument-pattern> .
          }
        }
      """ ;
      sh:severity sh:Violation ;
      sh:message "narrativeAppliesPattern value MUST be in scheme ei:concept/argument-pattern"
    ]
  ] .
```

### S-V2-3 — narrativeAboutTopic granularity contract

CQ source: CQ-N4, CQ-T3 (must_have). Severity: `sh:Violation`.

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
    sh:message "narrativeAboutTopic value MUST be owl:Class or skos:Concept; never bare owl:NamedIndividual"
  ] .
```

### S-V2-4 — Lead-uniqueness warning

CQ source: CQ-N8 (should_have). Severity: `sh:Warning` (NOT Violation; draft narratives may legitimately have multiple lead candidates).

```turtle
ei:NarrativeLeadUniquenessShape
  a sh:NodeShape ;
  sh:targetClass ei:Narrative ;
  sh:sparql [
    sh:select """
      PREFIX ei: <https://w3id.org/energy-intel/>
      SELECT $this WHERE {
        $this ei:hasNarrativePostMembership ?m1 ;
              ei:hasNarrativePostMembership ?m2 .
        ?m1 ei:memberRole <https://w3id.org/energy-intel/concept/narrative-role/lead> .
        ?m2 ei:memberRole <https://w3id.org/energy-intel/concept/narrative-role/lead> .
        FILTER(?m1 != ?m2)
      }
    """ ;
    sh:severity sh:Warning ;
    sh:message "More than one lead-role NarrativePostMembership on this Narrative (warning, not violation — draft narratives may legitimately have multiple lead candidates)"
  ] .
```

---

## 5. Closure / open-world summary

V2 introduces no new closure obligations on V0 or V1 axioms. The 4 SHACL shapes provide closed-world checks for invariants that OWL OWA cannot express (`per (Narrative, Post)` uniqueness, scheme-membership constraints).

Per [`_shared/closure-and-open-world.md`](../../../.claude/skills/_shared/closure-and-open-world.md):

- All 11 V2 CQs are answerable in OWA without closure axioms — a CQ returning empty is a legitimate outcome (no Narrative matches the criteria), not an OWA trap.
- The constraint CQs (CQ-N7, CQ-N8, CQ-T3) are closed-world by their nature (SHACL); they do not require OWL universal restrictions to be correct.
- No V2 CQ requires `owl:DisjointUnion` or universal restriction closure.

---

## 6. Profile summary

All V2 axioms (A1..A12) are OWL 2 DL safe. Subset of those (A1, A2, A4, A9) are also OWL 2 EL safe (simple class + property declarations + range). The cardinality restrictions (A7, A8, A12) push the closure into OWL 2 DL but are reasoner-safe under HermiT.

**Reasoner contract:** HermiT (V0/V1 default) on the V2 closure must:
1. Exit 0 (no parse errors).
2. Report zero unsatisfiable classes.
3. Maintain V0+V1 reasoner trace clean status (HermiT's V1 trace was clean per `validation/v1-bfo-remediation/v1-hermit-reason.log`; V2 adds no new BFO axioms).

If HermiT regresses, the **fallback plan** is documented in [oeo-import-rebuild-plan.md § 4.3](oeo-import-rebuild-plan.md): fall back to STAR extraction with `skos:broader` materialization in place of `rdfs:subClassOf` chains, drop the OEO punning surface.

---

## 7. Coverage validator

A future validation script `scripts/validate_axiom_plan.py` should:

1. Parse `competency-questions-v2.yaml` and extract every Must-Have CQ.
2. Parse `axiom-plan-v2.md` (this document) and extract every CQ ID in § 1.
3. Assert: every Must-Have CQ from the YAML appears in this document.
4. Assert: every architect obligation A* + S-V2-* listed in §§ 3-4 has a `cq_source` field that maps to at least one CQ in `competency-questions-v2.yaml`.

Pre-commit hook for this script is V3+ infrastructure; manual verification at conceptualizer-handoff time is sufficient for V2.

**This session's manual verification:**

| Must-Have CQ | Listed in § 1 | Architect obligation |
|---|---|---|
| CQ-N1 | yes | A1 |
| CQ-N2 | yes | A2, A4-A8 |
| CQ-N3 | yes | (covered by A2, A4-A8) |
| CQ-N4 | yes | A11, S-V2-3 |
| CQ-N5 | yes | A10, A12, S-V2-2 |
| CQ-N7 | yes | S-V2-1 |
| CQ-T1 | yes | (concept-scheme content; no axiom obligation) |
| CQ-T3 | yes | S-V2-3 |

**8/8 Must-Have CQs covered. Zero `missing_cq_link` issues.**

Should-Have CQs (CQ-N6, CQ-N8, CQ-T2) also covered: A9, S-V2-4, and concept-scheme content respectively.
