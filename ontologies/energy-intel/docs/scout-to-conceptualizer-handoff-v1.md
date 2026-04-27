# Scout → Conceptualizer Handoff — V1 (`energy-intel`)

**From:** ontology-scout (Phase 2, V1 iteration)
**To:** ontology-conceptualizer (Phase 3, V1 iteration)
**Predecessor handoff:** [docs/scout-to-conceptualizer-handoff.md](scout-to-conceptualizer-handoff.md) (V0)
**Date:** 2026-04-27
**Status:** READY FOR CONCEPTUALIZER

---

## One-paragraph lead

V1's three blocking scout questions are answered with empirical evidence.
The OEO seed-IRI list does **not** change between V0 and V1; the BFO
import conflict is resolved by extending the validator's strip list to
**BFO + RO** (validator's literal `--axioms structural` flag is invalid
in ROBOT 1.9.8 but the intent maps cleanly to `--trim true
--preserve-structure false` over a 57-IRI term file); QUDT depth
recommendation is **Unit + QuantityKind** (CQ-017 stays must_have-able,
not dropped). HermiT reasons cleanly (0 unsat) over the V0 top-level
closure merged with the BFO+RO-stripped OEO subsets and the narrow QUDT
slice. Conceptualizer can land the property design without further
scout input.

---

## SQ answers (cross-reference reuse-report-v1.md)

### SQ-1 — OEO seeds

**Verdict:** Carry V0 seeds forward unchanged. All three verified
non-deprecated against the local `imports/oeo-full.owl` (3.7 MB,
authoritative for v2.11.0).

| Seed IRI | Use in V1 |
|---|---|
| `https://openenergyplatform.org/ontology/oeo/OEO_00020267` (energy technology) | Primary range root for `ei:aboutTechnology` (CQ-015 walk). |
| `https://openenergyplatform.org/ontology/oeo/OEO_00000011` (energy converting component) | Secondary tier — admits component-level claims like "fuel cell" or "solar cell" via punning + the existing `(skos:broader \| rdfs:subClassOf)*` SPARQL path. |
| `https://openenergyplatform.org/ontology/oeo/OEO_00020039` (energy carrier) | Carrier root — admits "electricity", "natural gas", "hydrogen", "coal" claim values. |

**Concrete OEO IRIs the conceptualizer should weave into property-design-v1.md:**

```turtle
ei:aboutTechnology
  rdfs:domain ei:CanonicalMeasurementClaim ;
  rdfs:range  [ owl:unionOf (
                  oeo:OEO_00020267    # energy technology subtree
                  oeo:OEO_00000011    # energy converting component subtree
                  oeo:OEO_00020039    # energy carrier subtree
                  skos:Concept        # V0 carry-forward for hand-seeded schemes
                ) ] .
```

…or equivalent SHACL union via `sh:in` on a frozen value set if you
prefer the SHACL-validation route over OWL closure. Trade-offs are
identical to V0 anti-pattern review § 16.

### SQ-2 — QUDT depth

**Verdict:** Extract **`qudt:Unit` + `qudt:QuantityKind`** (Strategy B in
reuse-report-v1.md). Final subset: 25 units, 39 quantitykinds, 859
triples, 56 KB.

**What conceptualizer decides:**

1. **`ei:canonicalUnit` exact form.** Scope-v1.md § 2 line 53 says
   "(range `qudt:Unit`, on CMC, 0..1)". Scout endorses this. Use a
   `owl:FunctionalProperty` if you want the 0..1 cardinality enforced at
   the OWL level (HermiT will catch CMCs that assert two
   `ei:canonicalUnit` values); otherwise SHACL `sh:maxCount 1`.
2. **`ei:hasQuantityKind` location.** Scope-v1.md § 2 line 54 says "on
   Variable, 0..1." Scout endorses this. Reasoning: V0 already routes
   CMC -> Variable for cross-expert join (Linear D7), and putting
   `hasQuantityKind` on CMC creates two sources of truth (CMC's
   declared QK and Variable's QK). Variable is the canonical home for
   join-grain semantics.
3. **CQ-017 priority.** `should_have` is the right level — V0 + V1
   regression suite still passes if CQ-017 is empty (no Variable has a
   `hasQuantityKind` yet). Architect lands the property; ABox phase
   populates.
4. **V0 manifest IRI bug.** V0 `imports-manifest.yaml` row
   `qudt-units-2.1` has wrong unit IRIs (`unit:GW`, `unit:MW`,
   `unit:TW-HR`, `unit:GW-HR`, `unit:MW-HR`, `unit:KG-PER-J`, `unit:PJ`
   — 7 of 19 do not exist in QUDT 2.1). V1 manifest corrects them.
   Conceptualizer's property-design.md should reference the corrected
   names; if any V0 doc references the old names, those need a
   conceptualizer note.

### SQ-3 — BFO conflict remediation

**Verdict:** Validator's option A *concept* works after extending the
strip list. The build script `scripts/build_v1_imports.py` is
re-runnable and produces HermiT-clean output; reasoner trace at
`validation/v1-bfo-remediation/v1-hermit-reason.log` shows zero unsat.

**What conceptualizer decides:**

* Nothing — this is purely an import-shape concern. Architect uses the
  fixed subsets directly. Conceptualizer's only touchpoint is to
  acknowledge the closure is reasoner-safe in property-design-v1.md.

**Caveat conceptualizer must read:** the strip removed all axioms with
RO_* properties from the OEO subsets. This means OEO restrictions like
"`exogenous data` ⊑ `RO:has role some uncertainty role`" are **gone**
from the V1 closure. If a future CQ wants to walk OEO classes via RO
properties, the strip is too aggressive and we'll need a more surgical
fix (e.g., only strip `RO:has role` and `RO:role of`, not all 28 RO
properties). V1 CQs do not use RO walks, so this is acceptable for now.

---

## Conceptualizer's conceptual-model-v1.md decision points

The V1 requirements approval lists three blocking conceptualizer
questions ([CQ-Q-1, CQ-Q-2, CQ-Q-3](requirements-approval-v1.yaml)).
Scout's evidence-backed input on each:

### CQ-Q-1: `ei:Expert` fate (deprecate vs. keep as defined class)

**Scout has no opinion on the deprecation policy** — that's a
conceptualizer / architect call. But scout flags one V0 fixture-impact
note: V0 has fixtures naming `ei:Expert` IRIs (paths `expert/did-plc-*`
and `expert/did-web-*`). Either path requires fixture regeneration
(deprecation: rebind `?expert` to `foaf:Person` who bears
`ei:EnergyExpertRole`; equivalent class: nothing changes at the SPARQL
level because the reasoner classifies role-bearers as Experts). The V0
test_ontology.py at `tests/test_ontology.py` reads URIs verbatim from
`tests/fixtures/`, so any change to the URI form is breaking. Recommend:
**equivalent class path** to minimise V0 CQ regression.

### CQ-Q-2: `ei:canonicalUnit` cardinality + range

Already addressed above (functional, range `qudt:Unit`). One nuance:
scope-v1.md line 53 says "max 1 on CMC" (so 0..1, allowing CMCs with no
canonical unit yet — useful for the LLM-stage resolvability gate). If
conceptualizer wants strict 1..1 (every CMC must canonicalize), that's
an additional constraint that will fail SHACL on partially-resolved
fixtures. Scout recommends 0..1.

### CQ-Q-3: Punning regression

Already passes. HermiT trace at `validation/v1-bfo-remediation/v1-hermit-reason.log`
proves the closure is consistent with the OEO subsets imported. The
trace also supports the scope-v1.md § Open question 5 "watch on OEO
import" — scout's empirical run is the watch.

---

## Imports the V1 architect inherits

| Path | Role | Action |
|---|---|---|
| `imports/oeo-technology-subset-fixed.ttl` | OEO technology subtree (BFO+RO-stripped) | Add to `energy-intel.ttl` `owl:imports` list |
| `imports/oeo-carrier-subset-fixed.ttl` | OEO carrier subtree (BFO+RO-stripped) | Add to `energy-intel.ttl` `owl:imports` list |
| `imports/qudt-units-subset.ttl` | QUDT 2.1 units + quantitykinds | Add to `energy-intel.ttl` `owl:imports` list |
| `catalog-v001.xml` | catalog mappings | Add 3 rows mapping `https://w3id.org/energy-intel/imports/{oeo-technology,oeo-carrier,qudt-units}-subset` to the local TTL paths |
| `scripts/build_v1_imports.py` | re-runnable build | Curator runs at every OEO/QUDT refresh |

The fixed subset files are written with their natural OEO base IRI
(`https://openenergyplatform.org/ontology/oeo/`), not a w3id-energy-intel
IRI. If the architect prefers to register them under
`https://w3id.org/energy-intel/imports/...`, a one-line `robot annotate
--ontology-iri ...` step can be appended to `scripts/build_v1_imports.py`
on architect handoff back. Scout did not pre-register because the
catalog mapping suffices for resolution.

---

## Open questions inherited by conceptualizer (NOT scout-blocking)

1. **Should `ei:hasQuantityKind` go on `Variable`, on `CanonicalMeasurementClaim`, or on both?**
   Scout recommends Variable per scope-v1.md § 2 (single source of truth
   for join-grain semantics). Conceptualizer property-design call.
2. **Should V0 `imports/oeo-{technology,carrier}-subset.ttl` (the
   unfixed pair) be deprecated immediately or left in place for one
   release cycle as forensic baseline?** Scout recommends one-cycle
   grace, deprecation tag at v0.3.0. Curator concurs (manifest open
   question V1-IM-Q1).
3. **Should the 25 transitively-pulled low-priority QuantityKinds in
   `imports/qudt-units-subset.ttl` (Reflectance, RotationalVelocity,
   etc.) be stripped to keep the subset minimal?** Scout recommends
   KEEP (manifest open question V1-IM-Q2): they cost <100 triples and
   never appear in CMC range constraints. Conceptualizer property-design
   call if disagreed.
4. **OEO punning IRI form** — `ei:aboutTechnology` admits OEO classes as
   `skos:Concept` instances. The OWL 2 punning permission was given
   workspace-wide in V0 (scope.md § Reasoning / profile). If
   conceptualizer wants to materialize the OEO class hierarchy as a
   parallel `skos:broader` chain to avoid punning entirely, the SPARQL
   path stays `(skos:broader | rdfs:subClassOf)*` and the architect
   builds a small materialization script. Scout default: keep punning.

---

## What to read next

In order:

1. [`docs/reuse-report-v1.md`](reuse-report-v1.md) — full scout evidence.
2. [`imports-manifest-v1.yaml`](../imports-manifest-v1.yaml) — manifest delta.
3. [`scripts/build_v1_imports.py`](../scripts/build_v1_imports.py) — pipeline reference.
4. [`validation/v1-bfo-remediation/v1-hermit-reason.log`](../validation/v1-bfo-remediation/v1-hermit-reason.log) — reasoner trace.
5. V0 carry-overs:
   * [`docs/property-design.md`](property-design.md) — V0 property catalog (V1 extends).
   * [`docs/anti-pattern-review.md`](anti-pattern-review.md) — V0 anti-pattern review (§ 16 covers OEO-import punning).
   * [`docs/conceptual-model.md`](conceptual-model.md) — V0 conceptual model (V1 layers on top).

---

## Loopback triggers (none fire)

| Possible trigger | Status |
|---|---|
| `missing_reuse` (conceptualizer would have minted a term that already exists upstream) | Not raised. Conceptualizer hasn't started. Scout has identified all reuse candidates upfront. |
| `bad_module` (architect / validator says the extracted module is wrong) | Not raised. Architect hasn't started V1. |
| `import_provenance` (curator says manifest is stale) | Not raised. V1 manifest is fresh; OEO + QUDT both verified up. |
| Validator's V0 `construct_mismatch` (the trigger that motivated this scout phase) | **RESOLVED** — empirical HermiT-clean closure proves remediation works. |

Conceptualizer can proceed without further scout input.
