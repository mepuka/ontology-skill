# Scope — `energy-intel` Ontology, V1

**Short name:** `energy-intel` (prefix `ei:`, TBox namespace `https://w3id.org/energy-intel/`)
**Predecessor:** v0.1.0 (released 2026-04-22, audit at [release/release-audit.yaml](../release/release-audit.yaml))
**Date:** 2026-04-27
**Product owner / sole reviewer:** Mepuka Kessy (`kokokessy@gmail.com`)
**Inherits unchanged from V0:** modelling assumptions in [scope.md](scope.md), conceptual model in [conceptual-model.md](conceptual-model.md), V0 competency questions in [competency-questions.yaml](competency-questions.yaml), V0 use cases in [use-cases.yaml](use-cases.yaml).

This document captures the V1 **delta** only. V0 scope is the baseline; everything not restated here is unchanged.

---

## Step 0 — scope gate

| Gate | Verdict | Evidence |
|---|---|---|
| Scope fit | **approved** | V1 is an iteration on the released V0 TBox: closes two known V0 deferrals (OEO import, QUDT crosswalk) and corrects one acknowledged anti-pattern (Expert as class). All three are vocabulary / axiom changes — squarely an ontology problem. |
| Retrofit check | **false** | V1-specific modelling has not started. V0 release artefacts are frozen at commit `36d1952`. The two `imports/oeo-*-subset.ttl` files exist on disk from the V0 architect phase but are not yet `owl:imports`-ed and not yet remediated for the BFO conflict — they enter V1 through scout / architect, not as retrofit. |
| Stakeholder availability | **true** | Single-stakeholder model continues; product owner is `kokokessy@gmail.com`. |

---

## Purpose + framing

V1 closes the largest V0 deferrals that block downstream consumption:

1. **OEO MIREOT import + BFO conflict fix.** V0 ships with `imports/oeo-technology-subset.ttl` and `imports/oeo-carrier-subset.ttl` on disk but does NOT `owl:imports` them — merging them with the V0 BFO-2020 closure produces a HermiT "inconsistent ontology" verdict because OEO 2.11.0 ships its own BFO snippet. V1 lands the validator-recommended remediation: `robot remove --term BFO_* --axioms structural` on each OEO subset before import. Result: `ei:aboutTechnology` value-set widens from a placeholder `skos:Concept` to real OEO technology / energy-carrier classes (admitted as values via OWL 2 punning).

2. **QUDT 2.1 unit crosswalk.** V0 has `ei:assertedUnit` as `xsd:string` (raw token: `"GW"`, `"TWh"`). V1 adds a path from the surface token to a canonical `qudt:Unit` IRI, so two CMCs whose extractors typed `"GW"` and `"gigawatt"` resolve to the same canonical unit in cross-expert queries.

3. **Expert role refactor.** V0 collapsed `ei:Expert` to a `foaf:Person` subclass — the [V0 anti-pattern review](anti-pattern-review.md) flagged this as the role-type anti-pattern but the product owner ratified the simplification because no V0 CQ needed role-transience. V1 re-models Expert as the BFO Role pattern: a single `ei:EnergyExpertRole subClassOf bfo:0000023`, borne by a `foaf:Person` via `bfo:0000053`. This brings the agent module into line with the existing `PublisherRole` / `DataProviderRole` shape on `Organization`.

V1 stays TBox-only. ABox is still deferred.

---

## In-scope (V1 additions to the four-module TBox)

### 1. OEO MIREOT import (touches `measurement` module)

| Item | What lands |
|---|---|
| Imports remediation | `imports/oeo-technology-subset-fixed.ttl` and `imports/oeo-carrier-subset-fixed.ttl` produced via `robot remove --term BFO_* --axioms structural` over the existing V0 subsets. The validator-recommended option (A) per [validator-to-curator-handoff.md § 6](validator-to-curator-handoff.md). |
| `owl:imports` wiring | Top-level `energy-intel.ttl` adds the two fixed OEO subsets to its imports list. Catalog file (`catalog-v001.xml`) updates. |
| Range widening | `ei:aboutTechnology` value-set is no longer just `skos:Concept` placeholders — admits OEO technology classes (e.g., `oeo:EOL_solar_PV_*`) and energy-carrier classes as values via OWL 2 punning. SPARQL path `(skos:broader \| rdfs:subClassOf)*` already in CQ-013/CQ-014 continues to work. |
| Scout deliverable | Concrete OEO seed-IRI list (one of the V0 [scope § Open questions](scope.md) items). Scout phase deliverable. |

### 2. QUDT 2.1 unit crosswalk (touches `measurement` module)

| Item | What lands |
|---|---|
| Imports | `imports/qudt-units-subset.ttl` — narrow extract of `qudt:Unit` individuals actually referenced by V0 sample claims (`unit:GW`, `unit:TW-HR`, `unit:MW-HR`, `unit:KG-PER-J`, etc.). Possibly `qudt:QuantityKind` classes (decision deferred to scout). |
| New property | `ei:canonicalUnit` (range `qudt:Unit`, on CMC, 0..1) — the link from an asserted surface token to its canonical IRI. Property name and exact form locked by conceptualizer + architect. The existing `ei:assertedUnit xsd:string` stays as the raw surface form; `ei:canonicalUnit` is the resolved form. |
| Optional new property | `ei:hasQuantityKind` (range `qudt:QuantityKind`, on Variable, 0..1) — only if scout recommends importing QuantityKind. |
| Resolved scope question | Closes V0 [scope § Open question 4](scope.md): "Reuse `qudt:Unit` individuals only, or also `qudt:QuantityKind` classes?" — scout recommends, conceptualizer decides. |

### 3. Expert role refactor (touches `agent` module + several CQ fixtures)

| Item | What lands |
|---|---|
| New class | `ei:EnergyExpertRole subClassOf bfo:0000023` (BFO Role), with `bfo:0000052 some foaf:Person` restriction (analogue of `PublisherRole inheresIn Organization`). |
| `ei:Expert` fate | **Deferred to conceptualizer.** Two options: (a) deprecate via `owl:deprecated true` + `dcterms:isReplacedBy`, migrate fixtures; (b) keep as a defined class via `ei:Expert ≡ foaf:Person ⊓ (bfo:0000053 some ei:EnergyExpertRole)`. Conceptualizer evaluates trade-offs against safety rule "Never delete terms — deprecate with replacement pointer" and the V0 fixture compatibility cost. |
| Range widening | `ei:authoredBy` and `ei:spokenBy` ranges change from `ei:Expert` to `foaf:Person`. Existing axioms (`Post SubClassOf authoredBy exactly 1 ei:Expert`) update to `exactly 1 foaf:Person`. SHACL companion shape requires the Person to be `bfo:bearerOf` an `ei:EnergyExpertRole`. |
| SHACL S-1 | Stays unchanged in *intent* — `Post.authoredBy` value must still match the Linear D3 `https://id.skygest.io/expert/did-{plc\|web}-<slug>` URI form. Only the OWL-side typing changes. |
| New SHACL shape | `ei:Post`'s `authoredBy` value must `bfo:0000053 some ei:EnergyExpertRole`. Defense-in-depth on role-bearing. |

### Sign-off cadence

V1 ships as **v0.2.0** (minor version bump, additive — V0 CQs continue to pass). Curator releases tag, refreshes diff against v0.1.0 baseline.

---

## Out-of-scope (V1 non-goals)

Restated for clarity. Some are V0 carry-forwards; some are explicit V1 deferrals.

1. **Seven-facet Variable identity model.** Still V2+. Variable and Series remain thin in V1. The V1 OEO + QUDT additions land at the CMC level (`ei:aboutTechnology` widens to OEO; `ei:canonicalUnit` on CMC), NOT as Variable facets.
2. **Expert subrole taxonomy** (`AnalystRole` / `JournalistRole` / `AcademicRole` / `CommentatorRole`). V1 lands a single `ei:EnergyExpertRole`. The V0 anti-pattern review flagged subroles as the V1 unlock IF discourse-type distinction is needed; product-owner directive 2026-04-26 chose the single-role shape ("let's do a single row class for now"). Subrole taxonomy is V2+.
3. **SHACL coverage backfill** for the seven `intent: validate` properties not yet shaped (`assertedValue` datatype, `intervalStart` / `intervalEnd` date format, `hasSegmentIndex >= 0`, `screenshotOf` / `excerptFrom` URI well-formedness). Tracked in [validator-to-curator-handoff.md § 9](validator-to-curator-handoff.md). Defers to V1.1 or V2.
4. **Full QUDT vocabulary import.** V1 imports a narrow `qudt:Unit` extract (and possibly `qudt:QuantityKind` per scout recommendation). QUDT's full ~hundreds of MB stays out.
5. **OEO Process / Observation / QuantityValue machinery.** V1 imports OEO technology + carrier subtrees only. OEO's process / observation / quantity classes stay out — the V0 decision to model claims at the CMC level (not as Observations) is unchanged.
6. **ABox individuals.** Still TBox-only. URIs at `https://id.skygest.io/{kind}/{ulid}` remain a deferred concern.
7. **Narrative / Story / ArgumentPattern / Edition classes.** Carry-forward V0 non-goal; editorial workflow still in flux.
8. **Schema.org export codec** (Linear D6) and **JSON-LD `@context` generation strategy** — both still open V0 questions, both still deferred.

---

## Constraints

| Constraint | Value | Source |
|---|---|---|
| Upper ontology | BFO (ISO 21838-2) | unchanged from V0 |
| OWL profile | OWL 2 DL (with punning) | unchanged from V0; V1 OEO imports rely on punning for `ei:aboutTechnology` value-set |
| Reasoner | HermiT (release gate); ELK fast-path | unchanged from V0 |
| TBox namespace | `https://w3id.org/energy-intel/` | unchanged |
| Version IRI for V1 | `https://w3id.org/energy-intel/v1/2026-XX-XX` | curator stamps on release |
| Backwards compat | V0 CQs CQ-001..CQ-014 must still pass under V1 model | hard gate at validator |
| Build regime | Standalone POD (no ODK) | unchanged |

---

## V0 CQ revalidation guarantee

V1 must NOT break the V0 acceptance suite. The V1 architect refactor of `ei:Expert` is the highest-risk change; every V0 CQ that names `ei:Expert` (CQ-002, CQ-007, CQ-008, CQ-011) must continue to pass against fresh V1 fixtures.

Two paths get there:
- If conceptualizer chooses `ei:Expert ≡ foaf:Person ⊓ bearerOf-some-ei:EnergyExpertRole`, V0 fixtures keep working as-is — the reasoner classifies role-bearers as Experts.
- If conceptualizer chooses clean deprecation, V1 fixtures must be regenerated with the role-bearing pattern AND the V0 CQ SPARQL queries are unchanged but bind `?expert` to a Person who bears the role.

Either way, the validator's L4 pytest must report **14/14 V0 CQs PASS** + **all V1 CQs PASS** before sign-off.

---

## Reused external ontologies — V1 changes

V1 adds two imports to the V0 manifest:

| Ontology | V0 status | V1 status |
|---|---|---|
| **OEO** (Open Energy Ontology) | BOT extract on disk, not imported | **`owl:imports` two BFO-stripped subsets** via remediation step |
| **QUDT 2.1** | scope.md projected; not yet imported | **narrow `qudt:Unit` extract** imported; `qudt:QuantityKind` decision pending scout |
| BFO 2020 | full import | unchanged |
| IAO v2026-03-30 | MIREOT | unchanged |
| DCAT 3 | full import | unchanged |
| PROV-O / FOAF / SKOS / DCT | full import | unchanged |

Imports manifest is regenerated by curator after architect lands the new modules.

---

## Open questions — V1 (carried to scout / conceptualizer)

1. **Concrete OEO seed-IRI list** (carry-forward of V0 open question #1). Scout phase deliverable. Target subtrees: energy-technology root + immediate descendants (solar PV, wind, nuclear, etc.); energy-carrier root + immediate descendants (electricity, hydrogen, natural gas, etc.); aggregation-type and temporal-resolution if not already covered by V0 hand-seeded SKOS schemes.
2. **QUDT depth** (carry-forward of V0 open question #4). `qudt:Unit` only, or `qudt:Unit` + `qudt:QuantityKind`? Scout recommendation; impacts whether V1 has `ei:hasQuantityKind` on Variable.
3. **`ei:Expert` deprecation strategy.** Conceptualizer evaluates: (a) deprecate cleanly with migration vs. (b) keep as defined equivalent class. Architect lands the decision.
4. **`ei:canonicalUnit` vs. renaming `ei:assertedUnit` to `qudt:Unit`-typed.** Conceptualizer property-design call. Recommendation in scope: keep `ei:assertedUnit` as the surface-token data-property and add a *new* `ei:canonicalUnit` object-property for the resolved IRI — preserves V0 contract while extending it.
5. **Punning regression test.** Architect must verify HermiT stays clean once OEO classes appear as values of `ei:aboutTechnology`. The V0 anti-pattern review § 16 flagged this as "watch on OEO import." If HermiT misbehaves, fall back to materialising OEO class hierarchy as `skos:broader` chain — no more punning. Validator confirms.

---

## Definition of done (this scope phase)

- [ ] `docs/scope-v1.md` exists with Step 0 verdicts
- [ ] `docs/use-cases-v1.yaml` adds V1 use cases (UC-006 .. UC-010 estimated)
- [ ] `docs/competency-questions-v1.yaml` adds V1 CQs (CQ-015 .. CQ-019 estimated)
- [ ] `docs/cq-quality-v1.csv` scores every V1 CQ on the six Step 2.5 criteria
- [ ] `docs/pre-glossary-v1.csv` extracts V1 candidate terms
- [ ] `tests/cq-{015..019}.sparql` preflights via `prepareQuery`
- [ ] `tests/cq-test-manifest.yaml` updated to include V1 entries
- [ ] `docs/traceability-matrix-v1.csv` closes need → use case → CQ → term → test for V1
- [ ] `docs/requirements-approval-v1.yaml` signed with reviewer + ISO date + cq_freeze_commit SHA
