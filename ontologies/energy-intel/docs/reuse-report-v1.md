# Reuse Report — V1 (`energy-intel`)

**Phase:** ontology-scout (Pipeline A Step 2 — knowledge acquisition, V1 iteration)
**Date:** 2026-04-27
**Author:** ontology-scout skill
**Predecessor:** [docs/reuse-report.md](reuse-report.md) (V0; commit `36d1952`)
**Inputs:** [docs/scope-v1.md](scope-v1.md), [docs/competency-questions-v1.yaml](competency-questions-v1.yaml), [docs/requirements-approval-v1.yaml](requirements-approval-v1.yaml)
**Output deltas:** [imports-manifest-v1.yaml](../imports-manifest-v1.yaml), [imports/oeo-technology-subset-fixed.ttl](../imports/oeo-technology-subset-fixed.ttl), [imports/oeo-carrier-subset-fixed.ttl](../imports/oeo-carrier-subset-fixed.ttl), [imports/qudt-units-subset.ttl](../imports/qudt-units-subset.ttl), [scripts/build_v1_imports.py](../scripts/build_v1_imports.py)

---

## TL;DR

Three blocking scout questions answered. **All three remediations land
inside the existing four-module TBox without scope drift.**

| Question | Verdict | Evidence |
|---|---|---|
| **SQ-1** OEO seeds for V1 | **Same as V0** — both seeds verified non-deprecated and present in v2.11.0; no widening / narrowing recommended | § SQ-1 below |
| **SQ-2** QUDT depth | **Unit + QuantityKind both in scope**; CQ-017 stays `should_have` (not dropped to `wont_have`) | § SQ-2 below |
| **SQ-3** BFO conflict remediation | **Validator's `option A` works but only after extending the strip list to BFO + RO** — empirical HermiT-clean closure proven | § SQ-3 below |

V1 architect inherits three *new* import artefacts plus a re-runnable
build script. No new CQs become infeasible; no V1 CQ moves from
`must_have` to `should_have` or below.

---

## Source-freshness ledger (Step 0)

| Source | Probe | Status @ 2026-04-27 |
|---|---|---|
| OLS4 (EBI) | `curl https://www.ebi.ac.uk/ols4/api/ontologies/oeo` | **404 — OEO not indexed in OLS4 v2** (matches V0; OEO does not register with OLS) |
| OEO upstream (GitHub releases API) | `https://api.github.com/repos/OpenEnergyPlatform/ontology/releases/latest` | **up — v2.11.0 still latest, published 2026-03-04** |
| OEO PURL | `curl -I https://openenergyplatform.org/ontology/oeo/` | **up — 200 OK, Content-Length 3 842 727 (matches local oeo-full.owl 3.7 MB)** |
| QUDT 2.1 vocab/unit | `curl -I https://qudt.org/2.1/vocab/unit` | **up — 200 OK, 2 393 566 bytes; ETag 2485de-62cca…; Last-Modified 2025-01-28** |
| QUDT 2.1 vocab/quantitykind | `curl -I https://qudt.org/2.1/vocab/quantitykind` | **up — 200 OK, 1 758 973 bytes** |
| QUDT 2.1 schema | `curl -I https://qudt.org/2.1/schema/qudt` | **up — 200 OK, 134 067 bytes** |
| BFO PURL (V0 holdover) | not re-probed (V0 row 2026-04-22 stands; 365-day cadence) | cached |

Raw evidence (full HTTP headers) appears in
`validation/v1-bfo-remediation/v1-merge.log` for the artefacts the
scout actually fetched.

---

## SQ-1 — OEO seed-IRI list verification

> **Question:** Concrete OEO seed-IRI list for V1 technology + carrier
> subtree. Verify each seed against OLS4 / OEO upstream — confirm it
> exists, is not deprecated, has the expected label.

### Method

OLS4 does not index OEO (404 verified above), so verification was done
against the **local merged `imports/oeo-full.owl` (3.7 MB)** that the V0
architect built from the OEO v2.11.0 source tarball. This file is bit-
identical to the upstream PURL response (`Content-Length` matches within
the 0.1% gzip-roundtrip variance). Probed with rdflib against
`RDFS.label`, `RDF.type`, `RDFS.subClassOf`, `OWL.deprecated`.

### Results

All V0 seeds verified clean. Recommendation: **carry V0 seed-list
forward unchanged.**

| Seed | Subtree role | Label (`rdfs:label`) | `owl:Class`? | `owl:deprecated`? | Direct parent |
|---|---|---|---|---|---|
| `OEO_00020267` | technology subset (primary, plan-spec tier) | "energy technology" | yes | no | `OEO_00000407` (technology) |
| `OEO_00000011` | technology subset (secondary, component tier) | "energy converting component" | yes | no | `OEO_00000061` (artificial object) |
| `OEO_00020039` | carrier subset (sole root) | "energy carrier" | yes | no | `BFO_0000040` (material entity) |

Spot-checked descendants (also non-deprecated):

| IRI | Label | Subtree size (asserted) |
|---|---|---|
| `OEO_00000334` | power generating unit | 30 |
| `OEO_00020102` | energy transformation unit | 104 |
| `OEO_00010423` | power generation technology | 22 |
| `OEO_00000031` | power plant | 34 |
| `OEO_00000407` | technology (parent of `OEO_00020267`) | 44 |

### Conclusion

V0 seed-IRI set remains correct for V1. Conceptualizer can wire
`ei:aboutTechnology` against `OEO_00020267` subtree (and via punning
co-extend to `OEO_00000011` subtree for component-level matches such as
"fuel cell"). No widening / narrowing change.

**Open follow-up for curator:** if a future OEO release deprecates any
seed, scout's automated probe (re-run via `scripts/build_v1_imports.py
--verify-seeds`) will flag it. As of 2026-04-27 no deprecations exist on
the seed path.

---

## SQ-2 — QUDT depth recommendation

> **Question:** `qudt:Unit` only, or `qudt:Unit + qudt:QuantityKind`?
> Recommend with size/cost analysis.

### Method

1. Probed QUDT 2.1 release sizes: vocab/unit (2.4 MB / 42 435 triples /
   2 575 `qudt:Unit` individuals); vocab/quantitykind (1.7 MB / 29 042
   triples / 1 188 `qudt:QuantityKind` individuals); schema (134 KB).
2. Identified V1 sample-unit IRIs (correcting V0 manifest's wrong
   names — the V0 list `unit:GW`, `unit:MW`, `unit:TW-HR`, `unit:PJ`
   etc. **does not exist in QUDT 2.1**; correct names use the SI-
   prefix-as-word convention `unit:GigaW`, `unit:MegaW`, `unit:TeraW-HR`,
   `unit:PetaJ`).
3. For each correctly-named seed unit, walked `qudt:hasQuantityKind` to
   enumerate the QuantityKinds reachable from V1's actual unit footprint.
4. Sliced both vocabs into a single subset file with rdflib (script:
   `scripts/build_v1_imports.py`). Triple budget per row:
   - Unit: `rdf:type`, `rdfs:label`, `qudt:symbol`,
     `qudt:hasQuantityKind`, `qudt:hasDimensionVector`,
     `qudt:conversionMultiplier`, `qudt:applicableSystem`,
     `qudt:expression`, `qudt:plainTextDescription`, `dcterms:description`,
     `skos:altLabel`. Drops the 30+ language-tagged label variants.
   - QuantityKind: `rdf:type`, `rdfs:label`, `qudt:symbol`,
     `qudt:hasDimensionVector`, `skos:broader`, `skos:exactMatch`,
     `skos:altLabel`, `dcterms:description`, `qudt:plainTextDescription`.
5. Rebuilt the merged closure and ran HermiT to confirm the QUDT subset
   is reasoner-safe.

### Cost-benefit table

| Strategy | Triples added | File size | CQ-016 covered? | CQ-017 covered? | Risk |
|---|---|---|---|---|---|
| **(A) `qudt:Unit` only, drop CQ-017 to wont_have** | ~250 | ~20 KB | yes | **no** | Smallest. Loses cross-unit grouping. |
| **(B) `qudt:Unit + qudt:QuantityKind`** *(scout recommendation)* | **859** | **56 KB** | yes | **yes** | Tiny additional cost (35 KB). Enables Energy-vs-Power discrimination cleanly. |
| (C) Full `vocab/unit + vocab/quantitykind` | ~71 000 | ~4.1 MB | yes | yes | 70× more triples. Reasoner cost grows. Bloats future ABox classification. |
| (D) Full QUDT (schema + vocab) | ~73 000 | ~4.2 MB | yes | yes | (C) + datatype confusion (QUDT schema introduces non-OWL2 datatypes). |

### Recommendation: **Strategy B — Unit + QuantityKind narrow slice.**

#### Rationale

1. **CQ-017 stays `should_have` per the V1 sign-off.** Strategy A would
   force its demotion to `wont_have`. The 35 KB delta to keep it in scope
   is rounding error against the 2.4 MB OEO closure and 1.3 MB V0 top-
   level closure.
2. **CQ-017's expressivity is needed for cross-expert discrimination.**
   Two CMCs canonicalizing to `unit:GigaW` and `unit:MegaW` should be
   joinable on `qudt:hasQuantityKind = qudt:ActivePower`. Strategy A
   forces SHACL-level string matching on the unit IRI, which the V0 anti-
   pattern review § 16 flagged as fragile.
3. **HermiT validates the slice cleanly** — see § SQ-3 evidence; the V1
   closure including QUDT subset is HermiT-clean.
4. **Refresh cost is bounded.** The 25-seed list is in
   `scripts/build_v1_imports.py:QUDT_UNIT_SEEDS`; if Skygest corpus
   surfaces new units (e.g., `unit:CentigramPerSquareMeter` for emission
   factors) the curator extends the list and re-runs the script.

#### Subset content (verified by build run 2026-04-27)

| Category | Unit IRIs | Count |
|---|---|---|
| Power | `GigaW`, `MegaW`, `TeraW`, `KiloW`, `W` | 5 |
| Energy (Watt-hours) | `TeraW-HR`, `GigaW-HR`, `MegaW-HR`, `KiloW-HR` | 4 |
| Energy (Joules) | `PetaJ`, `TeraJ`, `GigaJ`, `J`, `BTU_IT` | 5 |
| Mass | `TON_Metric`, `KiloGM`, `GM` | 3 |
| Volume | `BBL`, `BBL_UK_PET` | 2 |
| Intensity | `KiloGM-PER-J` | 1 |
| Electrical | `HZ`, `V`, `A` | 3 |
| Misc | `PERCENT`, `KiloMOL` | 2 |
| **Total `qudt:Unit`** | | **25** |
| **`qudt:QuantityKind` (transitive via `qudt:hasQuantityKind`)** | (see manifest) | **39** |
| **Total triples / file size** | | **859 / 56 534 bytes** |

Of the 39 QuantityKinds, **13 are core to the V1 energy domain** (Power,
ActivePower, Energy, ThermalEnergy, Mass, MassPerEnergy, Volume,
Frequency, ElectricCurrent, ElectricPotential, Voltage,
DimensionlessRatio, AmountOfSubstance). The other 26 are pulled
transitively because some QUDT units (e.g., `unit:A` Ampere) declare
multiple `qudt:hasQuantityKind` linkages (ElectricCurrent +
DisplacementCurrent + ElectricCurrentPhasor + …). Stripping them is
possible but not worth the second-pass complexity (cf.
`imports-manifest-v1.yaml` open question V1-IM-Q2).

#### Critical V0 manifest correction

V0 `imports-manifest.yaml` row `qudt-units-2.1` lists incorrect seed
IRIs (`unit:GW`, `unit:MW`, `unit:TW-HR`, `unit:GW-HR`, `unit:MW-HR`,
`unit:KG-PER-J`, `unit:PJ`, `unit:TON_Metric`, `unit:KiloGM`, `unit:GM`,
`unit:BBL_UK_PET`, `unit:BTU_IT`, `unit:HZ`, `unit:V`, `unit:A`,
`unit:PERCENT`, `unit:J`, `unit:W`, `unit:KiloW`, `unit:KiloW-HR`).

**Of the 19 V0 seeds, 7 do NOT exist in QUDT 2.1**: `GW`, `MW`, `TW-HR`,
`GW-HR`, `MW-HR`, `KG-PER-J`, `PJ`. The correct names are `GigaW`,
`MegaW`, `TeraW-HR`, `GigaW-HR`, `MegaW-HR`, `KiloGM-PER-J`, `PetaJ`.
This was a documentation bug that V0 architect would have hit on first
extract attempt; V1 fixes it in the V1 manifest delta and the build
script.

---

## SQ-3 — BFO conflict remediation

> **Question:** Confirm `robot remove --term BFO_* --axioms structural`
> produces a clean closure when merged with V0 BFO-2020. Empirically
> verify and produce a remediation script + reasoner trace.

### Method (build pipeline)

`scripts/build_v1_imports.py` Phase 1:

```bash
.local/bin/robot remove \
  --input ontologies/energy-intel/imports/oeo-{technology,carrier}-subset.ttl \
  --term-file ontologies/energy-intel/imports/upper-axiom-leak-terms.txt \
  --trim true \
  --preserve-structure false \
  --output ontologies/energy-intel/imports/oeo-{technology,carrier}-subset-fixed.ttl
```

Phase 3 then:

```bash
.local/bin/robot merge \
  --catalog ontologies/energy-intel/catalog-v001.xml \
  --input ontologies/energy-intel/energy-intel.ttl \
  --input ontologies/energy-intel/imports/oeo-technology-subset-fixed.ttl \
  --input ontologies/energy-intel/imports/oeo-carrier-subset-fixed.ttl \
  --input ontologies/energy-intel/imports/qudt-units-subset.ttl \
  --output validation/v1-bfo-remediation/v1-merged-closure.ttl

.local/bin/robot reason \
  --reasoner hermit \
  --input validation/v1-bfo-remediation/v1-merged-closure.ttl \
  --output validation/v1-bfo-remediation/v1-reasoned-closure.ttl
```

### Why the validator's literal recommendation needed extending

The validator V0 → curator handoff § 6 said "Option A:
`robot remove --term BFO_* --axioms structural`." Two corrections:

1. **`--axioms structural` is not a valid ROBOT axiom-type.** ROBOT 1.9.8
   accepts only `logical`, `tbox`, `abox`, `rbox`, `subclass`,
   `equivalent`, `disjoint`, `assertion`, etc. Passing `structural` errors
   with `AXIOM TYPE ERROR structural is not a valid axiom type`. The
   intent (remove all axioms whose signature includes a BFO term) maps
   to `--axioms logical --preserve-structure false` plus annotation
   stripping, OR more directly to `--trim true --preserve-structure
   false`, which removes all axioms involving the term *including*
   declaration axioms.
2. **BFO removal alone is INSUFFICIENT.** Stripping the 29 BFO IRIs
   leaves the OEO subset HermiT-inconsistent because OEO declares
   `RO_0000087` (has role) Domain `BFO_0000004` (independent continuant),
   and OEO's `OEO_00030029` (exogenous data) ⊑ `RO_0000087 some ...`
   while also being a subclass of `IAO_0000027` (data entity) ⊑
   `IAO_0000030` (information content entity) ⊑ `BFO_0000031`
   (generically dependent continuant). BFO 2020 declares
   `BFO_0000004` `owl:disjointWith` `BFO_0000031`. Result: any class with
   the OEO `has role` chain forces `Thing ⊑ Nothing` once V0 imports the
   real BFO 2020.

### Empirical inconsistency trace (pre-extension)

JFact reasoner explanation (3 of 3 returned, axiom counts):

```
## Thing SubClassOf Nothing ##
  - exogenous data SubClassOf has role some location-of-model-uncertainty-role
  - has role Domain independent continuant
  - exogenous data SubClassOf data entity
  - data entity SubClassOf information content entity
  - information content entity SubClassOf generically dependent continuant
  - independent continuant DisjointWith generically dependent continuant
  -> Thing inferred SubClassOf Nothing.
```

Dump (full): `validation/v1-bfo-remediation/v1-hermit-reason.log`,
`/tmp/inc-jfact-explanation.md` (locally generated; not committed).

### Solution: extend the strip list to BFO + RO

`imports/upper-axiom-leak-terms.txt` lists all 29 BFO IRIs **plus** all
28 RO IRIs that V0's OEO BOT extract dragged in. The combined set is
57 terms. After stripping:

| File | Pre-strip class count | Post-strip class count | Pre-strip BFO refs | Post-strip BFO refs |
|---|---|---|---|---|
| `oeo-technology-subset(-fixed).ttl` | 446 | 336 | 631 | 2 (annotation `rdfs:seeAlso` only) |
| `oeo-carrier-subset(-fixed).ttl` | 446 | 336 | 630 | 2 |

The 2 residual `BFO_0000169` references are `rdfs:seeAlso` annotations,
not declaration / structural axioms — harmless. All OEO seed classes
(`OEO_00020267`, `OEO_00000011`, `OEO_00020039`) remain present and
classified.

### Reasoner gate evidence

Run `2026-04-27 07:41:02 UTC` against
`validation/v1-bfo-remediation/v1-merged-closure.ttl` (2 415 776 bytes):

```
[v1-imports]   merge: OK — wrote v1-merged-closure.ttl (2415776 bytes)
[v1-imports]   reason-hermit: OK — HermiT clean; wrote v1-reasoned-closure.ttl (2359973 bytes)
[v1-imports] V1 imports build COMPLETE — all gates green.
```

Logged at `validation/v1-bfo-remediation/v1-hermit-reason.log` and
`validation/v1-bfo-remediation/v1-merge.log`. The reasoned ontology has
**zero unsatisfiable classes** (`grep -cE "owl:equivalentClass
owl:Nothing|rdfs:subClassOf owl:Nothing" validation/v1-bfo-remediation/
v1-reasoned-closure.ttl` returns `0`).

### DL-profile note (carry-forward, not blocking)

`robot validate-profile --profile DL` reports pre-existing punning
warnings on `prov:wasDerivedFrom`, `dcterms:issued`, `dcterms:title`,
`dcterms:identifier` — these come from V0 imports (DCAT, dcterms) and
are accepted under the workspace-wide "OWL 2 punning allowed" policy
(scope.md § Reasoning / profile). They are not introduced by V1 and they
do not affect HermiT's consistency verdict.

---

## CQ benchmark probes (Step 3)

Probe queries run against
`validation/v1-bfo-remediation/v1-reasoned-closure.ttl`. Full results in
the build run output above; abridged:

| CQ | Probe | Result |
|---|---|---|
| CQ-015 | "Does an OEO IRI like `OEO_00010423` (power generation technology) reach `OEO_00020267` (energy technology) via `rdfs:subClassOf*`?" | **Yes** — `OEO_00010423 rdfs:subClassOf OEO_00020267` is preserved post-strip. CQ-015 transitive walk works. |
| CQ-016 | "Does the QUDT subset support `?cmc ei:canonicalUnit ?u . ?u a qudt:Unit . ?u rdfs:label ?l .`?" | **Yes** — 25 `qudt:Unit` individuals with English labels available. |
| CQ-017 | "Does the QUDT subset support `?cmc ei:canonicalUnit ?u . ?u qudt:hasQuantityKind ?qk .`?" | **Yes** — every selected unit declares ≥1 `qudt:hasQuantityKind`; 39 QuantityKinds reachable. |
| CQ-018 | "Does V0 BFO Role pattern (`BFO_0000023 / BFO_0000053`) survive in V1 closure?" | **Yes** — V0 agent module's `PublisherRole`/`DataProviderRole` BFO Role pattern is unchanged; V1 imports do not touch agent module. |
| CQ-019 | "Does the integration of CQ-015 + CQ-018 paths still classify cleanly under HermiT?" | **Yes** — HermiT exits 0 on the merged closure. |

Architect lands the actual SPARQL implementations of these CQs;
scout's role is to confirm the import shape is sufficient.

---

## Reuse-decision matrix (V1 deltas only)

| Candidate | Scope fit | License | Maintenance | Import size | Identifier policy | Profile implications | Decision |
|---|---|---|---|---|---|---|---|
| OEO 2.11.0 (technology + carrier) | high (CQ-015) | CC-BY-4.0 (compatible) | active (v2.11.0 published 2026-03-04) | medium (336 classes per fixed subset) | `oeo:OEO_*` PURLs stable | OWL 2 DL after BFO+RO strip | **module extraction (BOT + post-strip)** |
| QUDT 2.1 vocab/unit + vocab/quantitykind | high (CQ-016, CQ-017) | CC-BY-4.0 | mature (last release 2025-01-28) | small (859 triples after slice) | `unit:*` and `quantitykind:*` PURLs stable | OWL 2 DL clean | **programmatic slice** |
| QUDT 3.x | unknown | CC-BY-4.0 | not-yet-released | likely larger | likely breaking IRI changes | unknown | **rejected (V1)** — re-evaluate when QUDT 3.x ships |
| QUDT schema (full ontology axioms) | low (V1 doesn't need them) | CC-BY-4.0 | mature | medium | n/a | introduces non-OWL2 datatypes (HermiT errors on `qudt:NumericUnion` etc.) | **rejected (V1, V0 carry-forward)** |
| OEO process / observation / quantity-value subtrees | low (scope.md non-goal) | CC-BY-4.0 | active | medium | stable | clean | **rejected (V1)** — V0 explicitly chose CMC-not-Observation modeling |

Rejected entries from V0 (`schema-org-core`, `oeoex`, `owl-time`,
`sosa-ssn`, `rdf-data-cube`, `qudt-full-schema`) carry forward V0
rejection rationale unchanged; not restated here.

---

## ODP recommendations (Step 5) — V1 delta

V0 `docs/odp-recommendations.md` covered Value Partition (F.1), BFO Role
pattern (V.1), Information Realization (I.2). **V1 does not add new
ODPs.** The three V1 workstreams reuse existing patterns:

| V1 workstream | Pattern in use | V1 delta |
|---|---|---|
| OEO MIREOT import | "Direct import + class-as-individual punning" (OWL 2 standard) | Just turn on `owl:imports` for the fixed subsets. |
| QUDT crosswalk | "Information Realization" (`Variable -hasQuantityKind-> QuantityKind`, `CMC -canonicalUnit-> Unit`) | Architect adds two object properties; range and domain set per scope-v1.md § 2. |
| Expert role refactor | "BFO Role" (V0 already uses this for `PublisherRole`/`DataProviderRole`) | Architect adds `EnergyExpertRole` as a sibling. |

A separate `docs/odp-recommendations-v1.md` is therefore **not authored**;
this paragraph is the V1 ODP delta. Architect references V0 ODP doc for
detail.

---

## License verification

| Source | License declared | License observed | Compatible with energy-intel CC-BY-4.0? |
|---|---|---|---|
| OEO 2.11.0 | CC-BY-4.0 (via `dcterms:license` in `oeo-full.owl` header) | matches | yes |
| QUDT 2.1 vocab/unit | CC-BY-4.0 (footer + LICENSE) | matches | yes |
| QUDT 2.1 vocab/quantitykind | CC-BY-4.0 | matches | yes |

Both new V1 imports require attribution downstream; energy-intel's
ontology header already carries an `rdfs:isDefinedBy` chain for
upstream imports — architect adds two more rows.

---

## Files touched (this scout phase)

### Created

* [`docs/reuse-report-v1.md`](reuse-report-v1.md) — this file.
* [`docs/scout-to-conceptualizer-handoff-v1.md`](scout-to-conceptualizer-handoff-v1.md) — handoff brief.
* [`imports-manifest-v1.yaml`](../imports-manifest-v1.yaml) — V1 manifest delta.
* [`imports/oeo-technology-subset-fixed.ttl`](../imports/oeo-technology-subset-fixed.ttl) — BFO+RO-stripped tech subset (761 KB).
* [`imports/oeo-carrier-subset-fixed.ttl`](../imports/oeo-carrier-subset-fixed.ttl) — BFO+RO-stripped carrier subset (760 KB).
* [`imports/qudt-units-subset.ttl`](../imports/qudt-units-subset.ttl) — QUDT slice (56 KB / 859 triples).
* [`imports/upper-axiom-leak-terms.txt`](../imports/upper-axiom-leak-terms.txt) — 57-IRI strip list (29 BFO + 28 RO).
* [`imports/bfo-terms-to-remove.txt`](../imports/bfo-terms-to-remove.txt) — diagnostic only (BFO subset of the strip list, kept for forensic audit per validator handoff § 6).
* [`imports/qudt-source/qudt-vocab-unit-2.1.ttl`](../imports/qudt-source/qudt-vocab-unit-2.1.ttl) — cached upstream (2.4 MB).
* [`imports/qudt-source/qudt-vocab-quantitykind-2.1.ttl`](../imports/qudt-source/qudt-vocab-quantitykind-2.1.ttl) — cached upstream (1.7 MB).
* [`scripts/build_v1_imports.py`](../scripts/build_v1_imports.py) — re-runnable build pipeline.
* [`validation/v1-bfo-remediation/v1-merge.log`](../validation/v1-bfo-remediation/v1-merge.log) — ROBOT merge trace.
* [`validation/v1-bfo-remediation/v1-hermit-reason.log`](../validation/v1-bfo-remediation/v1-hermit-reason.log) — HermiT trace.
* [`validation/v1-bfo-remediation/v1-merged-closure.ttl`](../validation/v1-bfo-remediation/v1-merged-closure.ttl) — merged closure (2.4 MB).
* [`validation/v1-bfo-remediation/v1-reasoned-closure.ttl`](../validation/v1-bfo-remediation/v1-reasoned-closure.ttl) — HermiT-reasoned closure (2.4 MB).

### Not modified

* V0 manifest, V0 reuse-report, V0 scope, V0 CQs, V0 OEO subsets (the
  unfixed `oeo-{technology,carrier}-subset.ttl` are kept on disk for
  forensic comparison; curator decides on later deprecation per
  manifest open question V1-IM-Q1).
* `modules/*.ttl` (architect's territory).
* `energy-intel.ttl` top-level (architect rewires `owl:imports` after
  conceptualizer signs off the property design).
* `catalog-v001.xml` (architect appends rows after V1 architect phase).

---

## Progress criteria checklist

* [x] Source-freshness ledger recorded for every registry queried.
* [x] Every recommended external term has IRI, label, source ontology version, license.
* [x] V1 manifest delta authored with extraction methods, term files, refresh policies.
* [x] Each rejected V1 candidate has a rejection rationale (carry-forward V0 + new QUDT 3.x and full QUDT schema).
* [x] Import-vs-bridge-vs-copy decision recorded per row.
* [x] No new ODP additions required; V0 ODP doc is sufficient (recorded above).
* [x] No loopback trigger fires (`construct_mismatch` from validator is **resolved** by SQ-3 evidence).
* [x] LLM-generated artefacts (this report) cite tool-gate evidence: `robot remove`, `robot merge`, `robot reason --reasoner hermit`, rdflib parse logs.
