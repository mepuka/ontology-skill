# BFO Alignment — `energy-intel`, V1 Delta

**Authored:** 2026-04-27 by `ontology-conceptualizer` (V1 iteration)
**Predecessor:** [bfo-alignment.md](bfo-alignment.md) (V0; commit `36d1952`)
**Reviewer:** Mepuka Kessy (`kokokessy@gmail.com`)
**Reviewed at:** 2026-04-27
**Consumer:** `ontology-architect` (uses BFO/IAO IRIs when asserting `rdfs:subClassOf` and `bfo:0000052` inheres-in restrictions).

BFO 2020 (ISO 21838-2:2021) IRIs used throughout. Class decisions recorded against the three decision recipes in [`_shared/bfo-decision-recipes.md`](../../../.claude/skills/_shared/bfo-decision-recipes.md).

This document is a **delta** to V0 bfo-alignment.md. V0 placements remain authoritative for everything not restated here.

---

## 0. Scope of V1 BFO changes

V1 introduces **one new local class** with a BFO placement: `ei:EnergyExpertRole`. V1 also makes **one BFO-impactful re-decision**: `ei:Expert` is recast as a defined equivalent class (still a `foaf:Person` subtype, by definition). No other V0 BFO placement changes.

| Class | V0 BFO leaf | V1 BFO leaf | Status |
|---|---|---|---|
| `ei:EnergyExpertRole` | n/a (new) | `bfo:Continuant → bfo:SpecificallyDependentContinuant → bfo:RealizableEntity → bfo:Role` (BFO_0000023) | **NEW** |
| `ei:Expert` | `bfo:Object` via foaf:Person | `bfo:Object` via foaf:Person (entailed via the EquivalentTo definition; one of the conjuncts is `foaf:Person`) | **redefined** (EquivalentTo) |
| `ei:Organization` | `bfo:ObjectAggregate` | unchanged | — |
| `ei:PublisherRole`, `ei:DataProviderRole` | `bfo:Role` | unchanged | — |
| All media classes | `bfo:GDC` via `iao:ICE` | unchanged | — |
| All measurement classes | `bfo:GDC` or `bfo:TemporalRegion` | unchanged | — |

The three new V1 imports (OEO technology subset + OEO carrier subset + QUDT slice) bring **no new local BFO placements** — they are MIREOT/BOT extracts whose internal BFO axioms have been stripped (see [reuse-report-v1.md § SQ-3](reuse-report-v1.md)). The OEO classes appear as values of `ei:aboutTechnology` via OWL 2 punning; they do not become BFO-typed local classes.

---

## 1. New class — `ei:EnergyExpertRole`

### 1.1 Decision

- **BFO leaf:** `bfo:Continuant → bfo:SpecificallyDependentContinuant → bfo:RealizableEntity → bfo:Role` (BFO_0000023).
- **Local parents:**
  - `rdfs:subClassOf bfo:0000023` (BFO Role)
  - `rdfs:subClassOf [ a owl:Restriction ; owl:onProperty bfo:0000052 ; owl:someValuesFrom foaf:Person ]` — inheres-in restriction targeting `foaf:Person`.

### 1.2 Recipe applied

Per [`_shared/bfo-decision-recipes.md`](../../../.claude/skills/_shared/bfo-decision-recipes.md) **quality / role / disposition** branch:

1. Continuant or occurrent? **Continuant.** A role persists through time.
2. Independent or dependent? **Dependent.** A role exists in virtue of its bearer; it is a Specifically-Dependent Continuant.
3. Quality, role, or disposition? **Role.**
   - Not a quality — the role is not part of the bearer's physical makeup or essence.
   - Not a disposition — a role does not need to "fire" or be realised in a single causal event to exist; it persists in virtue of the social/institutional context.
   - Role — the bearer has the role in virtue of being in a particular social/institutional context (curating energy-domain claims for public consumption). Mirrors BFO 2020 Role examples (professor-role, student-role, treasurer-role).

### 1.3 Architect axiom (Manchester sketch)

```
ei:EnergyExpertRole a owl:Class ;
  rdfs:label "energy expert role"@en ;
  rdfs:subClassOf bfo:0000023 ;
  rdfs:subClassOf [ a owl:Restriction ;
                    owl:onProperty bfo:0000052 ;
                    owl:someValuesFrom foaf:Person ] ;
  skos:definition
    "A BFO role inhering in a foaf:Person who publishes energy-domain
    claims (on social media, podcasts, or articles) that an editorial
    pipeline extracts as CanonicalMeasurementClaims."@en .
```

This mirrors V0's `PublisherRole inheresIn Organization` shape exactly. Architect can reuse the V0 [`modules/agent.ttl` PublisherRole template](../modules/agent.ttl) and substitute the bearer class.

### 1.4 Why a single role, not subroles

The V0 anti-pattern review § 2 flagged that a future V1 *could* introduce subroles (`AnalystRole`, `JournalistRole`, `AcademicRole`, `CommentatorRole`) under `EnergyExpertRole` if discourse-type discrimination were needed. The product-owner directive 2026-04-26 ("let's do a single row class for now") chose the single-role shape for V1. Subroles are V2+. This V1 design supports the future extension cleanly: `AnalystRole subClassOf ei:EnergyExpertRole` would inherit the inheres-in restriction.

### 1.5 Disjointness obligations

`ei:EnergyExpertRole` is a `bfo:Role`. So are `ei:PublisherRole` and `ei:DataProviderRole`. Disjointness:

| Pair | Disjoint? | Rationale |
|---|---|---|
| `EnergyExpertRole` vs `PublisherRole` | **Yes** | EnergyExpertRole inheres in foaf:Person; PublisherRole inheres in ei:Organization. Different bearer types. The architect should write `DisjointClasses(EnergyExpertRole, PublisherRole, DataProviderRole)` to make this explicit (defence-in-depth — BFO doesn't enforce role-class disjointness automatically). |
| `EnergyExpertRole` vs `DataProviderRole` | **Yes** | Same reasoning. |
| `PublisherRole` vs `DataProviderRole` | yes (V0 — unchanged) | V0 already declares this. |

Architect axiom:
```
[ a owl:AllDisjointClasses ;
  owl:members ( ei:EnergyExpertRole ei:PublisherRole ei:DataProviderRole ) ] .
```

### 1.6 Ambiguity score

**0.** Textbook role placement. No reviewer escalation required (per [`_shared/llm-verification-patterns.md`](../../../.claude/skills/_shared/llm-verification-patterns.md), only ambiguity ≥ 2 requires Class C reviewer signature).

---

## 2. `ei:Expert` redefinition

### 2.1 V0 form

```
ei:Expert rdfs:subClassOf foaf:Person ;
          owl:disjointWith ei:Organization .
```

### 2.2 V1 form

```
ei:Expert owl:equivalentClass
  [ owl:intersectionOf (
      foaf:Person
      [ a owl:Restriction ;
        owl:onProperty bfo:0000053 ;
        owl:someValuesFrom ei:EnergyExpertRole ] ) ] ;
  owl:disjointWith ei:Organization .
```

The V0 `rdfs:subClassOf foaf:Person` assertion is **dropped** — the EquivalentTo entails it. The `owl:disjointWith ei:Organization` assertion is **kept**.

### 2.3 BFO entailment chain

Under HermiT the EquivalentTo definition entails:

```
ei:Expert rdfs:subClassOf foaf:Person                              # implied by intersection
ei:Expert rdfs:subClassOf bfo:Object via foaf:Person → BFO_0000040 # V0 chain unchanged
∀x. (ei:Expert ⊑ ∃ bfo:0000053 . ei:EnergyExpertRole)              # bearer-of role
```

Therefore:
- `ei:Expert` is **still** a `bfo:Object` (Material Entity → Object). V0 BFO placement preserved.
- Every `ei:Expert` instance bears an `ei:EnergyExpertRole`. The role **inheres-in** that Person via `bfo:0000052` (inheres-in is the inverse direction of `bfo:0000053` bearer-of).

### 2.4 Ambiguity score

**0** (decision change, but the ambiguity is zero). The V0 ambiguity register placed `ei:Expert` at score 0; the V1 redefinition does not introduce new BFO ambiguity.

### 2.5 Why this remains BFO-clean

- The V1 definition uses only `foaf:Person` (already V0) and `bfo:0000053` (in BFO 2020 import) and `ei:EnergyExpertRole` (new local; placed at `bfo:0000023`).
- No new BFO category appears.
- The bearer-of/inheres-in pattern is BFO 2020's standard mechanism for relating an independent continuant (the Person) to a specifically-dependent continuant (the Role).

---

## 3. Updated agent-layer ambiguity register

| Class | Candidate categories | Ambiguity | Reviewer | Decision | Rationale |
|---|---|---|---|---|---|
| `ei:Expert` | `bfo:Object` via foaf:Person; alternatives explored in V0 register | 0 | — | `bfo:Object` (entailed via foaf:Person; V1 keeps via EquivalentTo) | V0 placement preserved |
| `ei:Organization` | `bfo:ObjectAggregate`, `iao:ICE` | 1 | kokokessy@gmail.com (V0) | `bfo:ObjectAggregate` | V0 unchanged |
| `ei:PublisherRole` | `bfo:Role` | 0 | — | `bfo:Role` | V0 unchanged |
| `ei:DataProviderRole` | `bfo:Role` | 0 | — | `bfo:Role` | V0 unchanged |
| **`ei:EnergyExpertRole`** | **`bfo:Role`** | **0** | — | **`bfo:Role`** | **NEW: same shape as Publisher/DataProvider; bearer is foaf:Person, not Organization** |

No ambiguity ≥ 2 in V1 agent module. No reviewer escalation needed for V1 BFO placements.

---

## 4. Imports impact on BFO chain

The three new V1 imports do **not** introduce new local BFO placements:

### 4.1 OEO subsets (BFO+RO-stripped)

- `imports/oeo-technology-subset-fixed.ttl` and `imports/oeo-carrier-subset-fixed.ttl` carry zero BFO axioms post-strip (verified: `grep -cE "BFO_[0-9]+" oeo-technology-subset-fixed.ttl` returns 0).
- They still carry IAO axioms (`IAO_0000027`, `IAO_0000030`, `IAO_0000033`, etc.). Under V0's IAO MIREOT, these IAO classes are subClassOf `iao:ICE → bfo:GDC`. That chain is preserved when V0 IAO + V1 OEO subset are both imported.
- **Implication:** OEO classes that subClassOf an IAO class (e.g., `OEO_xxx subClassOf IAO_0000027 data item`) inherit the BFO-GDC chain via IAO. This is **intentional** and matches the OEO upstream semantics.
- **Conceptualizer concern:** if an OEO class is subClassOf both `iao:DataItem (IAO_0000027)` (which is a GDC) and a punned `skos:Concept` individual, does that create disjointness pressure with `bfo:IndependentContinuant`? **No** — `skos:Concept` is not BFO-typed in our import (SKOS is BFO-orthogonal). Punning a class IRI as a skos:Concept individual asserts only `oeo:OEO_xxx a skos:Concept`; it does NOT assert the IRI is an `iao:ICE` instance. The two views (class-as-class via OEO subset, individual-as-skos:Concept via punning) coexist cleanly under OWL 2 punning semantics.
- See [conceptual-model-v1.md § 5](conceptual-model-v1.md) for the full punning prediction with empirical reasoner trace.

### 4.2 QUDT slice

- `qudt:Unit` and `qudt:QuantityKind` are imported as `owl:Class` declarations from QUDT 2.1.
- QUDT's classes are **not** BFO-typed (QUDT has its own upper structure independent of BFO). This is consistent with V0 [scope.md § Reasoning](scope.md) — workspace-wide policy admits non-BFO-aligned imports.
- Local impact: `ei:canonicalUnit` ranges over `qudt:Unit`. The CMC subClassOf restriction `ei:canonicalUnit max 1 qudt:Unit` does not propagate any BFO commitment to QUDT.
- **No conflict with V0 BFO rule.** V0 [scope.md](scope.md) reads "Upper ontology: BFO" but the workspace policy admits *some* non-BFO-aligned imports as long as they don't conflict (QUDT is in this category).

### 4.3 Summary

The three V1 imports are reasoner-clean (HermiT exit=0) per the scout's empirical trace. No BFO placement decision is impacted.

---

## 5. Updated BFO leaf counts

| BFO leaf | V0 count | V1 count | V1 change |
|---|---|---|---|
| `bfo:Object` | 1 (`ei:Expert`) | 1 (`ei:Expert`) | unchanged (definition redefined; placement preserved) |
| `bfo:ObjectAggregate` | 1 (`ei:Organization`) | 1 | unchanged |
| `bfo:Role` | 2 (Publisher, DataProvider) | **3** (+ `ei:EnergyExpertRole`) | **+1** |
| `bfo:GDC` (via `iao:ICE`) | 15 | 15 | unchanged |
| `bfo:TemporalRegion` | 1 (`ei:ClaimTemporalWindow`) | 1 | unchanged |

**Total local class count: V0 = 21, V1 = 22.** Within the middle-out budget. Imports add OEO + QUDT classes but those are not local.

No `bfo:Process`, `bfo:Quality`, `bfo:Function`, `bfo:Disposition`, or `bfo:ImmaterialEntity` classes in V1.

---

## 6. Architect inheritance summary

| Action | Module | Note |
|---|---|---|
| Add `ei:EnergyExpertRole` class | `modules/agent.ttl` | Use V0 PublisherRole template; substitute bearer `ei:Organization` → `foaf:Person` |
| Add `bfo:0000052 some foaf:Person` inheres-in restriction on `ei:EnergyExpertRole` | `modules/agent.ttl` | Mirror the V0 PublisherRole shape exactly |
| Replace `ei:Expert rdfs:subClassOf foaf:Person` with the EquivalentTo definition | `modules/agent.ttl` | Keep `owl:disjointWith ei:Organization` |
| Add `AllDisjointClasses(EnergyExpertRole, PublisherRole, DataProviderRole)` | `modules/agent.ttl` | New disjointness obligation per § 1.5 |
| Run `robot reason --reasoner hermit` after agent module change | validation | V1 closure must remain HermiT-clean |
| No imports change (BFO already imported) | — | The three new V1 imports are at the top-level `energy-intel.ttl`, not at agent module level |

V1 BFO alignment is a small, surgical change. The architect's biggest task in BFO-alignment land is the `ei:Expert` EquivalentTo rewrite; everything else is additive role-class boilerplate.
