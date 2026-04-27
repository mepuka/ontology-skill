# Anti-Pattern Review — `energy-intel`, V1 Delta

**Reviewer:** Mepuka Kessy (`kokokessy@gmail.com`) — self-reviewer (single-stakeholder phase)
**Reviewed at:** 2026-04-27
**Conceptual-model commit:** V1 (this change-set; pre-architect)
**Catalogue:** [`_shared/anti-patterns.md`](../../../.claude/skills/_shared/anti-patterns.md) — 16 patterns.
**Predecessor:** [anti-pattern-review.md](anti-pattern-review.md) (V0; commit `36d1952`)

Severity legend: `info` = note only; `warn` = address before architect finalises axioms; `block` = must resolve before architect starts.

This document is a **delta** to V0 anti-pattern-review.md. Only patterns whose status changes in V1, or new patterns introduced by V1 additions, are restated here. V0 findings remain authoritative for everything else.

---

## 0. Summary of V1 status changes

| # | Pattern | V0 status | V1 status | Change |
|---|---|---|---|---|
| 1 | Singleton hierarchy | `info` (Variable thin by design) | `info` (unchanged; Variable still thin in V1) | none |
| **2** | **Role-type confusion (Expert)** | `info` (product-owner ratified V0 simplification) | **`info` — RESOLVED via V1 refactor** | **CLOSED** |
| 3 | Process-object confusion | `info` (CMC at ICE per ratified review) | `info` (unchanged) | none |
| 4 | Missing disjointness | `warn` → resolved | + new disjointness obligation: `AllDisjointClasses(EnergyExpertRole, PublisherRole, DataProviderRole)` | additive |
| 5 | Circular definition | `info` | `info` (V1 EquivalentTo on `ei:Expert` introduces no circularity — RHS does not reference Expert) | none |
| 6 | Quality-as-class | `info` | `info` (no V1 quality-as-class) | none |
| 7 | Information-physical conflation | `info` | `info` — explicit V1 check: `qudt:Unit` is a QUDT-side ICE/concept, not a physical bearer (no conflation introduced) | confirmed clean |
| 8 | Orphan class | `info` | `info` — `ei:EnergyExpertRole` has named parent (`bfo:0000023`); no V1 orphan | confirmed clean |
| 9 | Polysemy / overloaded term | `info` | `info` — V1 `ei:canonicalUnit` does not collide with any imported QUDT property (QUDT's namespace is distinct) | confirmed clean |
| 10 | Domain/range overcommitment | `warn` → resolved | `info` — V1 `ei:canonicalUnit` domain = `ei:CanonicalMeasurementClaim` (a leaf); range = `qudt:Unit` (an imported class, not a leaf). § 4 below explains why this is NOT overcommitment | additive check |
| 11 | Individuals in T-box | `info` | `info` — V1 introduces no TBox individuals | confirmed clean |
| 12 | Negative universals / complement overuse | `info` | `info` (V1 uses no `owl:complementOf`) | none |
| 13 | False is-a from OO inheritance | `info` | `info` (no V1 OO-flavoured names) | none |
| 14 | System blueprint instead of domain | `info` | `info` | none |
| 15 | Technical perspective over domain | `info` | `info` | none |
| **16** | **Mixing individuals with classes (punning)** | **`info` → watch (pending OEO import test)** | **`info` — RESOLVED with empirical evidence** | **CLOSED at TBox stage; ABox stage remains a watch** |

V1 closes the two V0 watch-items (§ 2 role-type confusion, § 16 punning watch) and introduces no new anti-patterns.

---

## 1. Pattern 2 — Role-type confusion: V0 → V1 closure

### V0 finding (carried forward verbatim from [anti-pattern-review.md § Pattern 2](anti-pattern-review.md))

> Expert is modelled as a class (`foaf:Person` subclass) rather than a `bfo:Role` borne by a Person. This is the role-type anti-pattern in principle. Severity: `info` — product owner ratified the V0 simplification (no V0 CQ depends on role-transience).

V0 mitigation was acceptance: "V1 gets proper EnergyExpertRole on Person if editorial-role discourse-type is needed."

### V1 resolution

V1 adopts the proper role-bearing pattern. `ei:Expert` is recast as a defined equivalent class:

```
ei:Expert ≡ foaf:Person ⊓ (bfo:0000053 some ei:EnergyExpertRole)
```

`ei:EnergyExpertRole` is a `bfo:0000023 (Role)`, with the inheres-in restriction `bfo:0000052 some foaf:Person`. The role-bearing pattern now mirrors the V0 `PublisherRole inheresIn Organization` shape exactly.

### Why this resolves the anti-pattern

The role-type confusion anti-pattern (per [`_shared/anti-patterns.md`](../../../.claude/skills/_shared/anti-patterns.md) § 2) reads: "modelling a role as a subclass of the bearer class." V0 had `ei:Expert subClassOf foaf:Person` — that *was* the anti-pattern. V1 has `ei:Expert ≡ foaf:Person ⊓ ∃bfo:0000053.ei:EnergyExpertRole` — the role is now a separate class, and `ei:Expert` is the *bearer-of-role* defined kind. This is the canonical "role pattern" fix from [`_shared/pattern-catalog.md`](../../../.claude/skills/_shared/pattern-catalog.md) § F.2.

### Evidence

- [conceptual-model-v1.md § 2](conceptual-model-v1.md) — full Expert refactor decision with rationale.
- [bfo-alignment-v1.md § 1, § 2](bfo-alignment-v1.md) — BFO placement of `ei:EnergyExpertRole` and `ei:Expert` redefinition.
- [property-design-v1.md § 3.1](property-design-v1.md) — `ei:authoredBy` range widened to `foaf:Person` (the Person can bear EnergyExpertRole or not — the SHACL companion shape requires it).

### Verification (pre-architect, conceptualizer-side)

| Check | Method | Verdict |
|---|---|---|
| `EnergyExpertRole` is `bfo:Role` (BFO_0000023) | bfo-alignment-v1.md § 1.1 | yes |
| `EnergyExpertRole` has bearer restriction (`bfo:0000052 some foaf:Person`) | bfo-alignment-v1.md § 1.3 | yes |
| `ei:Expert` is no longer a direct subclass of `foaf:Person` (subclass entailed via EquivalentTo) | conceptual-model-v1.md § 2 | yes |
| V0 CQs binding `?expert` continue to satisfy under HermiT | conceptual-model-v1.md § 7 (V0 CQ revalidation guarantee analysis) | yes (entailed) |

### Status: **CLOSED.** Severity downgrade: `info` → `info-resolved` (the workspace catalogue does not have a "resolved" severity; recording explicitly as resolved-with-evidence).

---

## 2. Pattern 16 — Mixing individuals with classes (OWL 2 punning): V0 → V1 closure (TBox stage)

### V0 finding

> OWL 2 punning is enabled workspace-wide. `ei:aboutTechnology` will admit OEO class IRIs as `skos:Concept` individuals via punning (phase 2). This is intentional, not a mix-up. Severity: `info → watch`. Architect must verify HermiT accepts the punned graph when OEO subset is imported.

### V1 resolution (TBox stage)

The scout's V1 phase empirically merged V0 top-level + BFO+RO-stripped OEO subsets + QUDT slice and ran HermiT. Result: **exit=0, zero unsatisfiable classes.** Trace at [`validation/v1-bfo-remediation/v1-hermit-reason.log`](../validation/v1-bfo-remediation/v1-hermit-reason.log).

### Why this resolves the V0 watch (TBox stage only)

The V0 anti-pattern review § 16 fallback plan ("if HermiT misbehaves, materialise OEO classes as plain SKOS individuals") is **not needed at the TBox stage.** The actual cause of the V0 punning concern — the BFO chain that OEO imports drag in — has been remediated by the BFO+RO strip ([reuse-report-v1.md § SQ-3](reuse-report-v1.md), [conceptual-model-v1.md § 5](conceptual-model-v1.md)). The OEO subset post-strip carries 0 BFO references and 0 RO references; OEO classes can be punned as `skos:Concept` instances without dragging any BFO disjointness.

### V1 ABox-stage carry-forward (still a watch — but a different one)

V1 ships **TBox-only**. When V2+ ABox lands and fixtures assert `?cmc ei:aboutTechnology oeo:OEO_xxx`, validator must re-confirm HermiT stays clean over the TBox + ABox closure. The TBox-stage proof is necessary but not sufficient for ABox-stage cleanliness.

**Forward-looking risk register** (carried into V2):

| Risk | Likelihood | Mitigation |
|---|---|---|
| ABox assertion `?x a skos:Concept ; a iao:ICE` (where IAO is from OEO subset's preserved IAO chain) creates BFO disjointness | medium | Fixture authoring rule: only declare `oeo:OEO_xxx a skos:Concept` punning, NEVER assert OEO IRIs as `iao:ICE` instances. Document in V2 fixture authoring guide. |
| OEO upstream introduces NEW BFO IRIs not in the strip-list | low (curator refresh checks at every import refresh) | `imports/upper-axiom-leak-terms.txt` extension via curator |
| Architect adds an axiom that types OEO IRIs as `iao:ICE` | low (architect handoff explicitly forbids) | Architect handoff § "What architect must NOT do" |

### Status: **CLOSED at TBox stage.** Recorded as a continuing watch for V2 ABox stage.

---

## 3. Pattern 4 — Missing disjointness: V1 additive obligation

### V0 finding

> Disjointness obligations enumerated for every sibling group: measurement (CMC/Obs/Var/Series/Window), media (Chart/Screenshot/Excerpt/Image; Post/MediaAttachment/PodcastSegment; SocialThread/PodcastEpisode), agent (PublisherRole/DataProviderRole; Expert/Organization). Severity: `warn` → resolved on architect implementation.

V0 architect implemented the disjointness axioms; validator confirmed.

### V1 additive obligation

`ei:EnergyExpertRole` is a new sibling under `bfo:Role`. The V0 disjointness `DisjointClasses(PublisherRole, DataProviderRole)` should be extended to a three-way `AllDisjointClasses`:

```
[ a owl:AllDisjointClasses ;
  owl:members ( ei:EnergyExpertRole ei:PublisherRole ei:DataProviderRole ) ] .
```

**Why three-way disjointness:**
- `EnergyExpertRole` inheres-in `foaf:Person`; `Publisher/DataProviderRole` inheres-in `ei:Organization`. Different bearer types — no individual can simultaneously be inhering in a Person and an Organization (and `ei:Expert disjointWith ei:Organization` enforces this disjointness at the bearer-class level too).
- A single Role individual cannot be both an EnergyExpertRole and a PublisherRole — they are different role-kinds with different bearer constraints.

### Status

`warn` (architect must implement before V1 finalisation) → resolved upon architect axiom implementation. Architect inherits this in [conceptualizer-to-architect-handoff-v1.md § 3](conceptualizer-to-architect-handoff-v1.md).

---

## 4. Pattern 10 — Domain/range overcommitment: V1 additive check

### Check 1: `ei:canonicalUnit`

| Property | Domain | Range | Risk? |
|---|---|---|---|
| `ei:canonicalUnit` | `ei:CanonicalMeasurementClaim` | `qudt:Unit` | low |

**Analysis:**
- Domain = a leaf class (CMC has no subclasses in V0/V1). Asserting `?x ei:canonicalUnit ?u` infers `?x a ei:CanonicalMeasurementClaim`. This is the intended classification — no overcommitment.
- Range = `qudt:Unit`, a class with 25 imported individuals. Asserting `?x ei:canonicalUnit ?u` infers `?u a qudt:Unit`. The 25 imported units already carry this typing; the inference is redundant-but-harmless on the canonical individuals.
- Risk: if a fixture asserts `?cmc ei:canonicalUnit "GW"` (string instead of IRI), HermiT will report a range violation. SHACL S-V1-1 catches this earlier with `sh:nodeKind sh:IRI + sh:in (the 25 imported units)`. Defense-in-depth.

### Check 2: `ei:authoredBy` range widening (Expert → Person)

| Property | V0 Domain | V0 Range | V1 Range | Risk? |
|---|---|---|---|---|
| `ei:authoredBy` | `ei:Post` | `ei:Expert` | `foaf:Person` | low (V1 is BROADER than V0 — strictly less overcommitting) |

**Analysis:**
- V1 widens from `ei:Expert` (a Person + role) to `foaf:Person` (a Person). The widening is correct: a Post's author is fundamentally a Person; the role-bearing is a defense-in-depth check via SHACL S-V1-3.
- Inference: `?p ei:authoredBy → ?p a foaf:Person`. The role-bearer pattern is enforced by SHACL, not OWL, so a Person without an asserted EnergyExpertRole is not OWL-inconsistent (correct under OWA).

### Check 3: `ei:spokenBy` range widening (same as Check 2)

Symmetric. No risk.

### Status

No new domain/range overcommitment. V1 changes either narrow correctly (`ei:canonicalUnit` is leaf-leaf) or broaden correctly (`ei:authoredBy/spokenBy` Expert → Person, removing the V0 over-narrow inference).

---

## 5. New checks introduced by V1 imports

### 5.1 Does the BFO+RO strip introduce a "missing axiom" issue with OEO that breaks any V0 CQ?

**Walk of V0 CQs against the V1 OEO subset:**

| V0 CQ | OEO interaction | Risk under V1 BFO+RO strip? |
|---|---|---|
| CQ-001..CQ-008 | none (Post/Expert/Variable layer) | no |
| CQ-009 | none (CMC evidence invariant) | no |
| CQ-010 | none (DCAT references) | no |
| CQ-011 | none (PodcastSegment/Expert) | no |
| CQ-012 | none (rest of podcast layer) | no |
| **CQ-013** | `ei:aboutTechnology` walk via `(skos:broader \| rdfs:subClassOf)*` | **none** — the SPARQL walk does NOT use any RO property. The BFO+RO strip removes only the upper-ontology axioms (BFO_*, RO_*); OEO's intra-namespace `rdfs:subClassOf` chains are preserved (verified via post-strip class count of 336 from 446; the lost 110 are upper-ontology declarations, not OEO-class subclassings). |
| **CQ-014** | similar `(skos:broader \| rdfs:subClassOf)*` walk | **none** (same reasoning) |

**Conclusion:** the BFO+RO strip is safe for all V0 CQs. The strip removes axioms about *upper-ontology* classes and properties, not about OEO classes themselves. CQ-013/CQ-014 remain executable.

**Caveat for future V2+ CQs:** if a future CQ wants to walk via RO properties (e.g., `ro:has_role`), the strip-list is too aggressive and curator must extend the strip-list more surgically (e.g., strip only `ro:has_role` and `ro:role_of`, not all 28 RO IRIs). [Reuse-report-v1.md § SQ-3](reuse-report-v1.md) flags this. V1 CQs do not use RO walks.

### 5.2 Does adding `ei:canonicalUnit` (CMC → qudt:Unit) introduce information-physical conflation (Pattern 7)?

**Pattern 7 reading:** modelling an information artefact (e.g., a chart-as-PNG) and a physical artefact (the PNG file on disk) as the same class.

**`ei:canonicalUnit` analysis:**
- `qudt:Unit` is QUDT's class for physical measurement units. QUDT itself models units as concepts/individuals, not as physical entities. There is no physical bearer of "GigaW" — it is an abstract unit definition.
- `ei:CanonicalMeasurementClaim` is an `iao:ICE` (information content entity, `bfo:GDC`).
- Linking `CMC -[canonicalUnit]-> Unit` is ICE-to-concept, not ICE-to-physical-bearer. No conflation.

**Status: no Pattern 7 violation introduced.** V0 [scope.md § Non-goal #1](scope.md) "chart rendering / pixel geometry / image processing" remains the workspace policy on physical bearers; V1 does not reverse this.

### 5.3 Pattern 9 (polysemy) check — `ei:canonicalUnit` vs imported QUDT properties

QUDT does NOT define `qudt:canonicalUnit`. The closest QUDT properties are `qudt:hasUnit` and `qudt:hasQuantityKind`. `ei:canonicalUnit` is in the `ei:` namespace and does not collide.

`qudt:hasQuantityKind` is reused unchanged (no local minting). [Property-design-v1.md § 4](property-design-v1.md).

**Status: no polysemy.**

### 5.4 Pattern 11 (TBox individuals) check — QUDT subset

QUDT 2.1's vocab/unit and vocab/quantitykind define **individuals** (specific units like `unit:GigaW` are `qudt:Unit` instances, not subclasses). When we import the QUDT subset, these individuals enter our ontology.

Are these "TBox individuals"? The pattern flags TBox pollution by individuals that should live in the ABox.

**Analysis:**
- The QUDT individuals are **upstream** TBox-level vocabulary individuals (analogous to SKOS concepts in a `skos:ConceptScheme`). They are not the project's own ABox.
- This is the same shape as the V0 hand-seeded `ei:TemporalResolution` SKOS scheme (V0 anti-pattern review Pattern 11 explicitly accepts this as not-a-violation).
- V0 Pattern 11 finding: "No V0 TBox individuals. `ei:TemporalResolution` SKOS concepts ARE individuals by SKOS design — they live in `modules/concept-schemes/temporal-resolution.ttl` (a separate file), which is the correct TBox/ABox seam for SKOS schemes."
- V1 follows the same convention: QUDT individuals live in the imported subset file `imports/qudt-units-subset.ttl`, not in the local TBox modules. The local TBox modules contain only class and property declarations.

**Status: no Pattern 11 violation.**

---

## 6. Closure / OWA additions for V1

V1 introduces no new OWL closure axioms beyond the existing V0 closures. The V1 axiom additions are:

| V1 axiom | Closure type | Notes |
|---|---|---|
| `ei:Expert ≡ foaf:Person ⊓ ∃bfo:0000053.ei:EnergyExpertRole` | EquivalentTo (defined class) | OWA-friendly — a Person without an asserted role is not classified as `ei:Expert` |
| `ei:EnergyExpertRole ⊑ ∃bfo:0000052.foaf:Person` | existential restriction | OWA — every role *must* have a Person bearer (BFO-level invariant) |
| `ei:CMC ⊑ ei:canonicalUnit max 1 qudt:Unit` | qualified max-cardinality | OWA — at most one canonical unit; absence is permitted (CQ-016 is 0..n cardinality) |
| `AllDisjointClasses(EnergyExpertRole, PublisherRole, DataProviderRole)` | disjointness | classification check — a single Role individual cannot be more than one of these |

No V1 axiom is an OWA trap (a CQ that returns "no" because of missing-not-false rather than because of factually-false). All V1 CQs are positive lookups (CQ-015..CQ-019 all return `0..n` rows).

---

## 7. Severity summary

| Severity | V0 count | V1 count | V1 change |
|---|---|---|---|
| `block` | 0 | 0 | — |
| `warn` (unresolved) | 0 | 0 | — |
| `warn` → resolved by design | 2 (#4, #10) | + 1 (Pattern 4 additive disjointness) | +1 (architect must implement) |
| `info` | 14 | 14 | — |
| `info-resolved` (V1 explicit closures) | — | 2 (#2 role-type, #16 punning at TBox stage) | +2 |

V1 adds zero `block` items. The single `warn` is the additive disjointness obligation, which architect resolves at axiom-write time.

---

## 8. Open items

- **Pattern #16 ABox stage watch.** Carried forward from V0 anti-pattern review § Pattern 16 (TBox stage closed; ABox stage remains a watch for V2+).
- **OEO RO-strip surgical re-scope** (informational, not blocking): if a future CQ wants to walk OEO classes via RO properties, the strip-list is too aggressive. § 5.1 above flags this. Curator scope.
- **OEO prefix bug in V1 CQ test SPARQL files** ([conceptual-model-v1.md § 8 item 1](conceptual-model-v1.md)): not an anti-pattern violation, but a test-authoring discovery. Architect must correct prefixes before validator runs.

No `warn` (unresolved) or `block` items remain.

---

## 9. Clean slate for the architect

V1's anti-pattern footprint:
- **Closes** two V0 watches (Pattern 2, Pattern 16 at TBox stage).
- **Adds** one disjointness obligation (Pattern 4 additive — three-way disjointness across the role classes).
- **Introduces zero new anti-patterns.**

The architect can proceed.
