# Conceptual Model — `energy-intel`, V1 Delta

**Authored:** 2026-04-27 by `ontology-conceptualizer` (V1 iteration)
**Predecessor:** [conceptual-model.md](conceptual-model.md) (V0; commit `36d1952`)
**Inputs consumed:**
- Requirements V1: [scope-v1.md](scope-v1.md), [competency-questions-v1.yaml](competency-questions-v1.yaml), [requirements-approval-v1.yaml](requirements-approval-v1.yaml).
- Scout V1: [reuse-report-v1.md](reuse-report-v1.md), [imports-manifest-v1.yaml](../imports-manifest-v1.yaml), [scout-to-conceptualizer-handoff-v1.md](scout-to-conceptualizer-handoff-v1.md).
- Empirical reasoner trace: [`validation/v1-bfo-remediation/v1-hermit-reason.log`](../validation/v1-bfo-remediation/v1-hermit-reason.log) (HermiT exit=0 on the V1 closure including BFO+RO-stripped OEO subsets and QUDT slice).

**Reviewer:** Mepuka Kessy (`kokokessy@gmail.com`)
**Reviewed at:** 2026-04-27

This document is a **delta** to V0. V0 conceptual-model.md remains the source of truth for everything not restated here. V1 lands three workstreams (OEO import wiring, QUDT crosswalk, Expert role refactor) and answers the three blocking questions [CQ-Q-1 / CQ-Q-2 / CQ-Q-3](requirements-approval-v1.yaml).

---

## 0. Inbound gate verification

| Artifact | Owner | Verified |
|---|---|---|
| `requirements-approval-v1.yaml` | requirements | signed by `kokokessy@gmail.com` 2026-04-27, `cq_freeze_commit: 36d1952` |
| `reuse-report-v1.md` + `imports-manifest-v1.yaml` | scout | three SQ answers with reasoner-clean evidence; manifest has 3 status_changed rows |
| `competency-questions-v1.yaml` | requirements | five V1 CQs (CQ-015..CQ-019), every one with priority + owner + testability + expected_answer_shape |

Inbound gate: **PASS**. No upstream loopback raised.

---

## 1. Scope of V1 conceptual changes

V1 adds **one new local class**, **two new properties**, **widens two property ranges**, and **wires three new imports**. No V0 class is renamed or deleted. No V0 axiom is invalidated.

| Change kind | Item | Module | Status |
|---|---|---|---|
| New local class | `ei:EnergyExpertRole` | `agent` | additive |
| New object property | `ei:canonicalUnit` | `measurement` | additive |
| Range widening | `ei:authoredBy` | `media` | `ei:Expert` → `foaf:Person` |
| Range widening | `ei:spokenBy` | `media` | `ei:Expert` → `foaf:Person` |
| Range widening | `ei:aboutTechnology` | `measurement` | `skos:Concept` → `(skos:Concept ⊔ punned-OEO-class)` (effectively unchanged via punning, see § 5) |
| Import addition | `imports/oeo-technology-subset-fixed.ttl` | `measurement` parent | additive (`owl:imports`) |
| Import addition | `imports/oeo-carrier-subset-fixed.ttl` | `measurement` parent | additive (`owl:imports`) |
| Import addition | `imports/qudt-units-subset.ttl` | `measurement` parent | additive (`owl:imports`) |
| Status decision | `ei:Expert` | `agent` | **kept as defined equivalent class** (see § 2) |
| Status decision | `ei:hasQuantityKind` proposal | `measurement` | **rejected** (CQ-017 reuses `qudt:hasQuantityKind` directly; see § 4 and property-design-v1.md § 2) |

Total local class count after V1: **22 local classes** (V0's 21 + `ei:EnergyExpertRole`). Still within the 20–30-in-V0 middle-out budget. No module split needed. Layer assignments unchanged.

---

## 2. Expert refactor — CQ-Q-1 decision

**Question:** Deprecate `ei:Expert` cleanly, OR keep it as a defined equivalent class?

### Decision: **(b) Keep `ei:Expert` as a defined equivalent class.**

```
ei:Expert  owl:equivalentClass
  [ a owl:Class ;
    owl:intersectionOf (
      foaf:Person
      [ a owl:Restriction ;
        owl:onProperty bfo:0000053 ;
        owl:someValuesFrom ei:EnergyExpertRole ]
    ) ] .
```

The class **stays** in module `agent`. No `owl:deprecated true` annotation. No `dcterms:isReplacedBy`. The V0 SubClassOf assertion (`ei:Expert rdfs:subClassOf foaf:Person`) is **removed** by the architect — replacement axiom is the EquivalentTo above, which entails the same SubClassOf via OWL semantics (intersection class is subclass of every conjunct).

### Rationale

The trade-off the skill prompt flags ("two ways to say the same thing" vs. "Never delete terms" vs. "fixture migration cost") resolves cleanly when the three pressures are scored against the V1 sign-off context:

1. **Workspace safety rule wins.** [`.claude/rules/ontology-safety.md § 4`](../../../.claude/rules/ontology-safety.md) reads: "Never delete terms — deprecate with `owl:deprecated true` and provide a replacement pointer." Deprecation here is *available* (option a), but it is the heavier instrument: it tells downstream consumers the term is going away. We do not want to communicate that. `ei:Expert` is a useful, named-handle for SPARQL-side enumeration ("give me all experts"). Keeping it as a defined class preserves the handle without breaking the safety rule.

2. **V0 fixture migration cost is the highest single-item cost in the deprecation path.** Scout's handoff [§ CQ-Q-1](scout-to-conceptualizer-handoff-v1.md) confirms `tests/test_ontology.py` reads URIs verbatim from `tests/fixtures/`. Four V0 CQs (CQ-002, CQ-007, CQ-008, CQ-011) bind `?expert` to results. Under option (a), every fixture file that asserts `<...> a ei:Expert` becomes wrong (`ei:Expert` is deprecated; should be `foaf:Person` + role-bearer triple). Under option (b), the same fixture continues to work and the reasoner additionally classifies any role-bearer it encounters as `ei:Expert`. **Option (b) is V0-CQ-revalidation-zero-cost.** That matches the [scope-v1.md § V0 CQ revalidation guarantee](scope-v1.md) hard gate.

3. **The "two ways to say the same thing" tension is the cost we accept.** Defined classes are by design two-ways-equivalent: `?x a ei:Expert` and `?x a foaf:Person ; bfo:0000053 [a ei:EnergyExpertRole]` resolve to the same set under HermiT. This is exactly how OWL 2 expresses "X is the kind defined as Y with such-and-such properties." The risk is mitigated by:
   - One canonical SPARQL form per CQ (V1 CQ-018 uses the role-bearer form; V0 CQs continue to use the class-membership form). Convention enforces single-style-per-CQ.
   - A `skos:editorialNote` on `ei:Expert` will document the equivalence and instruct authors of new CQs to prefer the role-bearer pattern when expressivity matters (e.g., role-transience semantics for V2's subrole taxonomy).

4. **The role pattern is correctly anchored.** `ei:EnergyExpertRole subClassOf bfo:0000023 (Role)`, with `bfo:0000052 some foaf:Person` (inheres-in restriction). This mirrors V0's `PublisherRole inheresIn Organization` shape exactly — the V0 architect's [agent.ttl](../modules/agent.ttl) already has the template. § 3 of [bfo-alignment-v1.md](bfo-alignment-v1.md) details the BFO placement.

### Closure / OWA implications

- **OWA-friendly.** A `foaf:Person` with no asserted role is **not** classified as `ei:Expert` and **not** classified as `not-ei:Expert` either; the reasoner remains silent. This is the correct Open-World behavior for a role-bearing pattern. Absence of role assertion ≠ negation of role.
- **Fixture authoring discipline.** ABox fixtures introducing a new energy expert MUST assert all three triples: `?p a foaf:Person`, `?p bfo:0000053 ?role`, `?role a ei:EnergyExpertRole`. Asserting only `?p a foaf:Person` does not classify the person as `ei:Expert` (correct under OWA — the role-bearer triple is what makes them an Expert).
- **Reasoner does the join automatically.** Under HermiT's classification, V0 fixtures that name `ei:Expert` continue to satisfy CQ-002/CQ-007/CQ-008/CQ-011. V1 fixtures that name `foaf:Person + bfo:0000053 some EnergyExpertRole` ALSO satisfy those CQs (the reasoner derives `?expert a ei:Expert`).
- **What the architect inherits.** A single EquivalentTo axiom on `ei:Expert`. The V0 `rdfs:subClassOf foaf:Person` assertion is dropped (entailed). The V0 `owl:disjointWith ei:Organization` assertion **stays** — `ei:Expert` is still disjoint with `ei:Organization` (a Person who bears EnergyExpertRole is not an Organization). The defined class plus the disjointness combine cleanly.

### Why not option (a) — recap

Option (a) (deprecate cleanly + migrate fixtures + redirect via `dcterms:isReplacedBy`) is the strict-deprecation path. We reject it because:
- It costs four CQ fixture rewrites (CQ-002/007/008/011) plus updates to all V0 sample-answer URIs.
- It produces no net SPARQL-expressivity win — both options resolve to the same role-bearer set.
- It signals "going away" when `ei:Expert` is in fact useful as a named handle.

Recorded as a known trade-off; if a future V2 wants a clean strict-deprecation, the migration path is documented above and architect can apply it then.

---

## 3. OEO import wiring (CQ-015) — taxonomy delta

V1 imports two BFO+RO-stripped OEO subsets at the top-level `energy-intel.ttl`:

| Import | Path | Triples |
|---|---|---|
| OEO technology subtree | `imports/oeo-technology-subset-fixed.ttl` | ~336 classes; 1 526 IAO refs; 0 BFO refs (verified) |
| OEO carrier subtree | `imports/oeo-carrier-subset-fixed.ttl` | ~336 classes; same shape |

**Taxonomy effect on `ei:aboutTechnology`:**
- V0 range stays **`skos:Concept`** at the OWL level. No change there.
- The subset files import IAO classes (`IAO_0000027`, `IAO_0000030`, etc.) but no longer carry BFO axioms. This is the scout's BFO+RO-strip remediation, empirically verified HermiT-clean.
- OEO classes (e.g., `oeo:OEO_00020267` "energy technology") become available as values of `ei:aboutTechnology` via OWL 2 punning — the IRI denotes both an `owl:Class` (in the OEO subtree) and a `skos:Concept` (when an `ei:CMC ei:aboutTechnology oeo:OEO_xxx` triple is asserted).
- **Tree shape** (illustrative; full tree is the OEO subset itself):

```
oeo:OEO_00000407  technology              (OEO root)
  └── oeo:OEO_00020267  energy technology
        ├── oeo:OEO_00010423  power generation technology
        ├── oeo:OEO_00010013  ... (any narrower tech class)
        └── ...
oeo:OEO_00000061  artificial object      (OEO root)
  └── oeo:OEO_00000011  energy converting component
        ├── ...
oeo:OEO_00020039  energy carrier         (carrier root, BFO_0000040 lineage stripped)
  ├── oeo:Electricity / Hydrogen / NaturalGas / etc.
```

The CQ-015 SPARQL uses `(skos:broader|rdfs:subClassOf)*` which walks both the punned-individual relation (`skos:broader`) and the class-as-class relation (`rdfs:subClassOf`). Because the OEO subset preserves `rdfs:subClassOf` chains within the OEO namespace, the walk lands at the seed root regardless of which view a fixture asserts.

**Note on the OEO prefix bug** (discovery — not blocking, see § 8): V1 CQ test files [`tests/cq-015.sparql`](../tests/cq-015.sparql) and [`tests/cq-019.sparql`](../tests/cq-019.sparql) declare `PREFIX oeo: <http://openenergy-platform.org/ontology/oeo/>` (HTTP, hyphenated). The OEO subsets and the actual upstream PURL use `https://openenergyplatform.org/ontology/oeo/` (HTTPS, no hyphen). This is the same bug the workspace memory's `bf2bb31` commit fixed for V0. Architect must verify the V1 SPARQL files are corrected before they go to validator. Documented in § 8 and in the architect handoff.

---

## 4. QUDT crosswalk (CQ-016, CQ-017) — taxonomy delta

V1 imports the narrow QUDT slice:

| Import | Path | Triples |
|---|---|---|
| QUDT 2.1 vocab/unit + vocab/quantitykind | `imports/qudt-units-subset.ttl` | 859 triples / 56 KB / 25 units / 39 QKs |

**Taxonomy effect:**
- 25 `qudt:Unit` individuals admitted (e.g., `unit:GigaW`, `unit:TeraW-HR`, `unit:KiloGM-PER-J`, `unit:HZ`, `unit:V`, `unit:A`, `unit:PetaJ`, …).
- 39 `qudt:QuantityKind` individuals admitted (13 core; 26 transitively pulled — KEEP per scout V1-IM-Q2 recommendation; cost is <100 triples).
- The QUDT classes (`qudt:Unit`, `qudt:QuantityKind`) themselves are imported as `owl:Class` declarations from QUDT 2.1.
- The `qudt:hasQuantityKind` object property (linking a Unit to its QuantityKind(s)) is imported and reused unchanged.

**No new local QUDT-derived classes.** `ei:canonicalUnit` is the only new local thing referencing QUDT; its range is `qudt:Unit` (see [property-design-v1.md § 2](property-design-v1.md)).

**Tree shape** (illustrative):
```
qudt:Unit                          (QUDT class)
  ├── unit:GigaW                   (individual)
  ├── unit:MegaW
  ├── unit:KiloW-HR
  ├── unit:GigaJ
  ├── unit:KiloGM-PER-J
  ├── unit:HZ, unit:V, unit:A
  ├── unit:PERCENT
  └── ...

qudt:QuantityKind                  (QUDT class)
  ├── quantitykind:Power
  ├── quantitykind:ActivePower
  ├── quantitykind:Energy
  ├── quantitykind:ThermalEnergy
  ├── quantitykind:Mass
  ├── quantitykind:MassPerEnergy
  ├── quantitykind:Volume
  ├── quantitykind:Frequency
  ├── quantitykind:ElectricCurrent
  ├── quantitykind:ElectricPotential / Voltage
  ├── quantitykind:DimensionlessRatio
  └── ...
```

### CQ-017 routing — important update

The V1 requirements approval and the scope-v1.md § 2 line 54 propose `ei:hasQuantityKind` (range `qudt:QuantityKind`, on Variable, 0..1) as a new local property. **CQ-Q-2 partial decision: I am REJECTING this proposal.**

Reasoning: The committed V1 CQ-017 SPARQL ([`tests/cq-017.sparql`](../tests/cq-017.sparql)) uses:
```
?cmc ei:canonicalUnit ?unit .
?unit qudt:hasQuantityKind quantitykind:Power .
```

The walk goes **CMC → canonicalUnit → Unit → qudt:hasQuantityKind → QuantityKind**. It uses `qudt:hasQuantityKind` (the imported QUDT property), NOT a local `ei:hasQuantityKind`. The QUDT subset already declares `qudt:hasQuantityKind` triples on every imported unit (verified via the OFL technology spot-check; e.g., `unit:A qudt:hasQuantityKind qkind:ElectricCurrent, qkind:CurrentLinkage, ...`).

**Adding `ei:hasQuantityKind` on Variable would be:**
- Redundant with `qudt:hasQuantityKind` on Unit (two sources of truth — the very anti-pattern the scout's handoff warns against).
- Out-of-line with the committed CQ-017 SPARQL.
- Premature for V1: Variable is deliberately thin in V0/V1; it grows facets in V2 (seven-facet identity). If V2 adds `ei:hasQuantityKind` on Variable, that is a Variable-facet decision, not a V1 unit-crosswalk decision.

**What V1 ships:**
- `ei:canonicalUnit` (CMC → Unit).
- `qudt:hasQuantityKind` (Unit → QuantityKind), reused unchanged from the QUDT import.
- The CQ-017 SPARQL chain works as written.

**What V1 does NOT ship:**
- A local `ei:hasQuantityKind` property.
- A Variable-side QuantityKind link.

Documented in [property-design-v1.md § 2](property-design-v1.md). Manifest open question V1-IM-Q3 (scout) is closed: scout recommended Variable, conceptualizer rejects in favor of the imported QUDT path. Scout's recommendation was based on the scope-v1.md proposal; the committed CQ-017 SPARQL settles it.

### CQ-Q-2 decision (full): `ei:canonicalUnit` form

Cross-reference [property-design-v1.md § 2](property-design-v1.md) for the property table. Conceptual decisions:

| Question | Decision | Rationale |
|---|---|---|
| Range | **`qudt:Unit` only** | CQ-016 fixture binds `unit:GigaW`. QuantityKind canonicalization is unnecessary at the CMC layer; the QK is derivable via the unit. |
| Cardinality | **0..1, max 1, `owl:FunctionalProperty`** | Per scout's recommendation. 0..1 supports the resolvability gate use case (a CMC may have an `assertedUnit` string but no canonical unit yet — LLM stage fills this in). Functional gives reasoner-side fusing. |
| Naming | **`ei:canonicalUnit`** (object property) | Matches scope-v1.md § 2 line 53. `ei:assertedUnit` (xsd:string) stays as-is. The pair: surface form (string) + canonical IRI (Unit). |
| Punning of `qudt:Unit` IRIs | **No punning needed.** | Unit IRIs are individuals (members of `qudt:Unit` class). They do not function as classes. CQ-Q-2 punning sub-question asked whether QuantityKind IRIs would also be admitted via punning; we reject that — they're individuals only, the chain goes through the `qudt:hasQuantityKind` property at the Unit level, not by typing the QK IRI dual-role. |

Closure / OWA implications:
- A CMC without `ei:canonicalUnit` is **not** ill-formed (0..1 is the lower bound). This is intentional: it's the resolvability-gate state. SHACL S-V1-2 (see [shacl-vs-owl-v1.md](shacl-vs-owl-v1.md)) optionally validates that `canonicalUnit` is populated when `assertedUnit` is present.
- Functional: if a CMC asserts two distinct `ei:canonicalUnit` values, HermiT will fuse them via `owl:sameAs` (or report an inconsistency if they are explicit `owl:differentFrom`). Correct behavior — a single CMC's measurement has one canonical unit.

---

## 5. Punning prediction — CQ-Q-3

**Question:** Will HermiT stay clean once V1 architect lands `owl:imports` on the BFO+RO-stripped OEO subsets, given that `ei:aboutTechnology` admits OEO class IRIs as values (OWL 2 punning)?

### Prediction: **YES — HermiT stays clean. Confidence: high.**

### Rationale (three independent threads of evidence)

**(a) Empirical reasoner trace.** The scout has already merged the V1 closure (V0 top-level + the BFO+RO-stripped OEO subsets + the QUDT slice) and run `robot reason --reasoner hermit`. Result: exit=0, zero unsatisfiable classes. Trace at [`validation/v1-bfo-remediation/v1-hermit-reason.log`](../validation/v1-bfo-remediation/v1-hermit-reason.log) and [`v1-reasoned-closure.ttl`](../validation/v1-bfo-remediation/v1-reasoned-closure.ttl) (2.4 MB). This proves the import shape is reasoner-safe at the architect-import stage.

**(b) BFO+RO strip reasoning.** The V0 anti-pattern review § 16 watch-item flagged punning as a *potential* trigger. The actual trigger that V0 → V1 surfaced was different: it was BFO axioms in the OEO subset (e.g., OEO's `RO_0000087 rdfs:domain BFO_0000004` plus OEO's `IAO_0000030 rdfs:subClassOf BFO_0000031` and the BFO disjointness `BFO_0000004 owl:disjointWith BFO_0000031`) chaining to `Thing ⊑ Nothing`. Stripping all 29 BFO IRIs and all 28 RO IRIs from the OEO subsets removes that chain at its root. The result: OEO classes no longer carry any axiom that creates BFO-disjointness pressure. Punning OEO IRIs as `skos:Concept` individuals adds the assertion `oeo:OEO_xxx a skos:Concept` to the ABox (when fixtures land in V2+). Because OEO IRIs no longer have any BFO-typed parent in the V1 closure, this dual-role typing creates no new disjointness.

**(c) OWL 2 punning is well-defined for class-as-individual.** OWL 2 DL admits punning where the same IRI denotes both an `owl:Class` and a `owl:NamedIndividual`. The reasoner treats them as distinct symbols at the description-logic level. HermiT and ELK both support this. The V0 anti-pattern review § Pattern 16 documented this with the watch-item caveat — that caveat (the BFO-leak) is now closed by the BFO+RO strip.

### Risk register (residual)

| Risk | Likelihood | Mitigation |
|---|---|---|
| OEO upstream introduces NEW BFO IRIs in v2.12+ that the strip-list misses | low — 90-day refresh cadence + curator's manifest delta check | curator extends `imports/upper-axiom-leak-terms.txt` |
| Architect adds an OWL axiom that types OEO IRIs as `iao:ICE` instances (which DOES leak BFO via IAO) | low — architect handoff explicitly forbids extra typing | architect handoff § "What architect must NOT do" |
| ABox fixture asserts `oeo:OEO_xxx a skos:Concept` AND `oeo:OEO_xxx a iao:ICE` (where IAO is from OEO subset, still BFO-typed via the GDC chain) | medium — fixtures are V2+, but the IAO chain DOES survive in the OEO subset | fixture authoring rule: only declare `a skos:Concept` punning, never `a iao:ICE` |
| Validator's empirical re-run (Phase 6) reveals a counter-example | low — already empirically proven by scout | fall back to materialise OEO as plain SKOS individuals (V0 anti-pattern review § 16 fallback plan, restated in this doc) |

**Fallback plan if HermiT breaks (reuse from V0 anti-pattern review § 16):**

1. Re-extract OEO technology + carrier subtrees as plain `skos:Concept` individuals — drop the `owl:Class` typing entirely.
2. Replace the OEO `rdfs:subClassOf` hierarchy with a `skos:broader` hierarchy.
3. Update the SPARQL path in CQ-015/CQ-019 to `(skos:broader)*` only (drop the `rdfs:subClassOf` branch).
4. Architect runs `robot reason` and confirms HermiT clean.
5. The `imports/oeo-*-subset-fixed.ttl` files are replaced; the fallback build script is `scripts/build_v1_imports.py --skos-only` (architect adds the flag).

This fallback is documented for completeness; the empirical evidence says we will not need it.

### V0 anti-pattern review § 16 status update

Reclassify from "watch (info)" to **"resolved (info, evidence-backed)"**. Documented in [anti-pattern-review-v1.md § Pattern 16](anti-pattern-review-v1.md).

---

## 6. Module assignments — V1 confirmation

No module boundary changes in V1. New items land in their existing module:

| Module | V1 additions | V1 imports |
|---|---|---|
| `agent` | `ei:EnergyExpertRole` (new class); `ei:Expert` redefined as EquivalentTo; `ei:authoredBy` and `ei:spokenBy` ranges widen | unchanged (BFO + FOAF) |
| `media` | none | unchanged (IAO via parent) |
| `measurement` | `ei:canonicalUnit` (new property); `ei:aboutTechnology` range admits OEO via punning | three new imports: `oeo-technology-subset-fixed.ttl`, `oeo-carrier-subset-fixed.ttl`, `qudt-units-subset.ttl` (architect wires at top-level `energy-intel.ttl`, propagates via existing measurement-module import path) |
| `data` | none | unchanged (DCAT + FOAF) |

Module count: 4 (unchanged). Architecture layers unchanged.

---

## 7. Coverage sanity check — V1 CQs to commitments

| CQ | Priority | Commitment in this V1 model |
|---|---|---|
| CQ-015 | must_have | OEO subset imports (§ 3); `ei:aboutTechnology` punning preserved (§ 5) |
| CQ-016 | must_have | `ei:canonicalUnit` (§ 4, property-design-v1.md) |
| CQ-017 | should_have | `qudt:hasQuantityKind` reused from import (§ 4); CMC-side property is `canonicalUnit`, QK reached via Unit |
| CQ-018 | must_have | `ei:EnergyExpertRole` (§ 2); `ei:authoredBy` range = `foaf:Person` (property-design-v1.md § 4) |
| CQ-019 | should_have | composes CQ-015 + CQ-018 (§§ 2, 5) |

Every V0 CQ (CQ-001..CQ-014) continues to have a V0 commitment and is **not** invalidated by V1 changes. Specifically:
- CQ-002 (`Post authoredBy exactly 1 ei:Expert`) continues to pass: under the EquivalentTo definition, any role-bearer is classified as `ei:Expert`; existing fixtures asserting `?p a ei:Expert` directly are still valid.
- CQ-007/008/011 (querying `?expert`) bind to whichever IRIs satisfy `?p a ei:Expert`, which remains accurate under the new defined class.
- CQ-013/014 (`ei:aboutTechnology` skos:Concept walk) continue to work — punning OEO classes are still `skos:Concept` instances.

V0 CQ revalidation guarantee from [scope-v1.md § V0 CQ revalidation guarantee](scope-v1.md): **upheld**.

---

## 8. Discoveries (for upstream artefacts; record-only)

These are findings during conceptualization that may affect upstream phases. None block conceptualizer handoff.

1. **OEO prefix bug in V1 CQ test SPARQL files.** [`tests/cq-015.sparql`](../tests/cq-015.sparql) and [`tests/cq-019.sparql`](../tests/cq-019.sparql) declare `PREFIX oeo: <http://openenergy-platform.org/ontology/oeo/>` (HTTP + hyphen). The actual OEO PURL and the imported subsets use `https://openenergyplatform.org/ontology/oeo/` (HTTPS, no hyphen). The SPARQL files will return zero rows under the V1 closure unless the prefix is corrected. **Action for architect:** before running validator's L4 pytest, run `sed -i 's|http://openenergy-platform.org|https://openenergyplatform.org|g'` on the affected V1 CQ files (or equivalent rdflib normalization). This is the same class of bug as the V0 commit `bf2bb31`. Worth surfacing to requirements skill for next-iteration CQ-authoring template.

2. **CQ-017 routing through Unit, not Variable.** As documented in § 4, the committed CQ-017 SPARQL routes through `qudt:hasQuantityKind` on Unit. The scope-v1.md § 2 line 54 proposal of `ei:hasQuantityKind` on Variable is therefore not implemented. This is a coherent V1-model decision but it **closes manifest open question V1-IM-Q3** in a way the scout did not anticipate. Curator note for the next refresh cycle.

3. **No restructure of `ei:assertedUnit`.** V0 has `ei:assertedUnit xsd:string` on CMC. V1 keeps it. The pair (`ei:assertedUnit` raw token + `ei:canonicalUnit` IRI) implements the surface-form-to-canonical-IRI link as scope-v1.md proposed. No deprecation of `ei:assertedUnit`.

4. **OEO IRI punning exposure in fixture data is a V2 concern, not V1.** V1 ships TBox-only. The empirical HermiT-clean trace covers the TBox + imports. When V2 ABox lands fixtures asserting `?cmc ei:aboutTechnology oeo:OEO_xxx`, validator must re-confirm HermiT stays clean. Documented in [anti-pattern-review-v1.md § Pattern 16](anti-pattern-review-v1.md) as a deferred ABox-stage gate.

---

## 9. Decision summary (for architect)

| Decision | Verdict | Lives in |
|---|---|---|
| CQ-Q-1: `ei:Expert` fate | **(b) keep as defined equivalent class**: `Expert ≡ Person ⊓ (bfo:0000053 some EnergyExpertRole)` | this doc § 2 |
| CQ-Q-2: `ei:canonicalUnit` form | range = `qudt:Unit`; cardinality 0..1 (Functional); name `ei:canonicalUnit`; **no `ei:hasQuantityKind`** | this doc § 4 + property-design-v1.md § 2 |
| CQ-Q-3: punning regression | **HermiT stays clean** (empirically verified); fallback documented (re-materialise OEO as plain SKOS individuals) if Phase 6 says otherwise | this doc § 5 |

Architect inherits a concrete, axiom-ready blueprint via [conceptualizer-to-architect-handoff-v1.md](conceptualizer-to-architect-handoff-v1.md).
