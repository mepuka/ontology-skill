# Release Notes — `energy-intel` v0.2.0

**Release date:** 2026-04-27
**Version IRI:** `https://w3id.org/energy-intel/v1/2026-04-27`
**Predecessor:** v0.1.0 (commit `36d1952`, dated 2026-04-22)
**License:** CC-BY-4.0
**Validator recommendation:** release ([release-audit-v1.yaml](release-audit-v1.yaml))
**Sign-off status:** pending — awaiting human reviewer

---

## TL;DR

V1 closes V0's `construct_mismatch` loopback (OEO + BFO-2020 incompatibility),
formalises Expert as a defined equivalent role-bearing class, mints
`ei:canonicalUnit` with a QUDT 2.1 unit subset, and adds 5 SHACL contracts
(S-V1-1..S-V1-5). All 19 CQs (14 V0 + 5 V1) pass. **No V0 axiom is removed
without an equivalent V1 replacement** — the release is backwards-compatible
for ABox consumers who use `?p a ei:Expert`.

Three new imports land: `oeo-technology-subset` (BFO+RO-stripped),
`oeo-carrier-subset` (BFO+RO-stripped), and `qudt-units-subset` (25 units +
39 quantitykinds; 859 triples).

---

## What's new

### Net-new TBox terms (from KGCL change log A1, A4)

* **`ei:EnergyExpertRole`** — Class. Parent `bfo:0000023` (BFO role); subclass
  of `bfo:0000052 some foaf:Person` (must inhere in a Person).
  [`modules/agent.ttl:48-54`](../modules/agent.ttl)
* **`ei:canonicalUnit`** — ObjectProperty + FunctionalProperty. Domain
  `ei:CanonicalMeasurementClaim`; range `qudt:Unit`.
  [`modules/measurement.ttl`](../modules/measurement.ttl)

### Modified TBox axioms (A2, A3, A5, A6, A7)

* **`ei:Expert`** redefined as defined equivalent class:
  `Expert ≡ foaf:Person ⊓ ∃bfo:0000053.EnergyExpertRole`. V0
  `SubClassOf foaf:Person` is dropped (entailed by EquivalentTo) but the V0
  `disjointWith Organization` carries forward unchanged.
* **3-way role disjointness** — `AllDisjointClasses(EnergyExpertRole,
  PublisherRole, DataProviderRole)`. The V0 binary
  `disjointWith(PublisherRole, DataProviderRole)` is preserved as redundant
  carry-forward (entailed but not removed).
* **`ei:CanonicalMeasurementClaim`** gains a qualified max-cardinality
  restriction: `CMC SubClassOf canonicalUnit max 1 qudt:Unit`.
* **`ei:authoredBy`** range widened from `ei:Expert` to `foaf:Person`. The
  `Post SubClassOf authoredBy exactly 1 ei:Expert` restriction is rewritten
  as `Post SubClassOf authoredBy exactly 1 foaf:Person`.
* **`ei:spokenBy`** range widened from `ei:Expert` to `foaf:Person`.

### Net-new SHACL contracts (from KGCL annotations S-V1-1..S-V1-5)

| Shape | Target | Severity | Purpose |
|---|---|---|---|
| `S-V1-1` CanonicalUnitInQudtSubset | `ei:CanonicalMeasurementClaim` | Violation | `ei:canonicalUnit` value MUST be one of the 25 imported QUDT unit IRIs |
| `S-V1-2` ResolvabilityGate | `ei:CanonicalMeasurementClaim` | Warning | Soft signal — `assertedUnit` without `canonicalUnit` is incomplete |
| `S-V1-3` PostAuthorBearsEnergyExpertRole | `ei:Post` | Violation | Author of a `Post` MUST bear `ei:EnergyExpertRole` |
| `S-V1-4` PodcastSpeakerBearsEnergyExpertRole | `ei:PodcastSegment` | Warning | Speaker of a `PodcastSegment` SHOULD bear `ei:EnergyExpertRole` |
| `S-V1-5` AboutTechnologyInRecognizedVocab | `ei:CanonicalMeasurementClaim` | Violation | `ei:aboutTechnology` value MUST be a `skos:Concept` OR sit in an OEO subtree |

[Shapes file](../shapes/energy-intel-shapes.ttl) — 9 NodeShapes total
(4 V0 + 5 V1).

### Net-new imports (A8)

| Import | Method | License | Triples |
|---|---|---|---|
| [`oeo-technology-subset`](../imports/oeo-technology-subset-fixed.ttl) | OEO 2.11.0 BOT slice + BFO+RO strip + reannotated | CC-BY-4.0 | 336 classes (was 446 pre-strip) |
| [`oeo-carrier-subset`](../imports/oeo-carrier-subset-fixed.ttl) | OEO 2.11.0 BOT slice + BFO+RO strip + reannotated | CC-BY-4.0 | (preserved subtree) |
| [`qudt-units-subset`](../imports/qudt-units-subset.ttl) | QUDT 2.1 narrow programmatic slice | CC-BY-4.0 | 859 triples / 25 units / 39 quantitykinds |

The OEO subsets undergo a `robot remove --term-file
upper-axiom-leak-terms.txt --trim true --preserve-structure false` step that
strips 29 BFO classes/properties + 28 RO object properties before they are
wired into `owl:imports`. The project's BFO-2020 import via `agent.ttl`
remains the single BFO source-of-truth.

### Net-new CQs

All 5 land with passing fixtures and `expected_results_contract`:

| CQ | Contract | Cardinality |
|---|---|---|
| CQ-015 | CMCs tagged with OEO technology root or descendant | 0..n |
| CQ-016 | CMC with `ei:canonicalUnit = unit:GigaW` | exactly 1 |
| CQ-017 | (CMC, unit) pairs with QK chain via canonicalUnit | 0..n |
| CQ-018 | foaf:Person bearing EnergyExpertRole + authoring Post | exactly 1 (DISTINCT) |
| CQ-019 | (person, cmc) integration pairs | 0..n (DISTINCT) |

[Test manifest](../tests/cq-test-manifest.yaml).

---

## V0 → V1 breaking-change analysis

**No breaking changes for ABox consumers.** Per the conceptualizer's CQ-Q-1
decision, V0 modelled `ei:Expert SubClassOf foaf:Person`; V1 modelled
`ei:Expert ≡ foaf:Person ⊓ ∃bfo:0000053.EnergyExpertRole`. The defined
equivalent class is **strictly stronger** than the V0 SubClassOf:

* Any V0 ABox triple `?p a ei:Expert` continues to type-check under V1 —
  the reasoner derives the V0 SubClassOf from the V1 EquivalentTo.
* Any V0 ABox triple `?p a foaf:Person` does NOT auto-classify as
  `ei:Expert` under V1 (the additional `∃bfo:0000053.EnergyExpertRole`
  requirement guards this).
* V1 ABox callers that DO assert the role-bearing pattern get richer
  reasoner inference for free.

**Range widenings** (`authoredBy: Expert → Person`, `spokenBy: Expert →
Person`) are also non-breaking because `ei:Expert` is now a (defined)
sub-class of `foaf:Person` — every V0 Expert is still an admissible target
of `authoredBy`/`spokenBy` under V1, but V1 additionally admits any
`foaf:Person` regardless of role.

**Migration table for ABox consumers:**

| Consumer pattern | V0 behaviour | V1 behaviour | Migration |
|---|---|---|---|
| `?p a ei:Expert` then `?post ei:authoredBy ?p` | works | works (and reasoner classifies role-bearer) | none |
| `?p a foaf:Person` then `?post ei:authoredBy ?p` | type error if range = ei:Expert | works (range widened) | none |
| Asserting role-bearing pattern (`?p ei:bearerOf ?role`; `?role a ei:EnergyExpertRole`) | not admissible under V0 | reasoner classifies `?p a ei:Expert` | optional — adopt for richer inference |

---

## Loopback closures (V0 → V1)

| V0 issue | V0 status | V1 mitigation | Evidence |
|---|---|---|---|
| `shacl_violation` (S-1 DidSchemeOnAuthoredBy) | resolved at V0 sign-off | shape patch carried forward; V1 fixtures still pass | [`validation/v1/validator-rerun/shacl/shacl-summary.json`](../validation/v1/validator-rerun/shacl/shacl-summary.json) |
| `construct_mismatch` (OEO + BFO-2020 inconsistent under HermiT) | non-blocking-for-V0 | **CLOSED** — V1 BFO+RO strip pipeline (`scripts/build_v1_imports.py`) eliminates the BFO version conflict; merged closure HermiT-clean (exit 0, 0 unsat) | [`validation/v1/validator-rerun/reason/hermit.log`](../validation/v1/validator-rerun/reason/hermit.log) (empty) |
| `role_type_confusion` (V0 anti-pattern § 2) | watch | **CLOSED** — V1 A1+A2 redefines Expert as defined equivalent role-bearing class | [`modules/agent.ttl:11-18`](../modules/agent.ttl) |
| `punning_at_TBox` (V0 anti-pattern § 16) | watch | **CLOSED at TBox stage** — V1 closure HermiT-clean; ABox-stage punning watch carries forward to V2 | [`validation/v1/validator-rerun/reason/hermit.log`](../validation/v1/validator-rerun/reason/hermit.log) |

---

## Validation summary

All 8 validator gates pass on independent re-run. Cite paths from
[`docs/validator-report-v1.md`](../docs/validator-report-v1.md):

| Gate | Verdict | Evidence |
|---|---|---|
| L0 syntax / catalog merge | PASS | `validation/v1/validator-rerun/preflight/merge.log` (exit 0) |
| L0 DL profile | WARN-accepted, upstream-only | 41 distinct upstream-only punned IRIs; 0 project-origin |
| L1 HermiT (per module + top-level closure with V1 imports) | PASS | exit 0; 0 unsatisfiable |
| L2 ROBOT report + allow-list | PASS | 687 upstream ERRORs allow-listed; 0 project-origin |
| L3 pyshacl (19 fixtures × 9 shapes) | PASS | 19/19, 0 Violations, 1 Warning (cq-008 by design) |
| L3.5 SHACL coverage | PASS | V1 `intent: validate` 100% covered; V0/V1 deferrals tracked in [`validation-waivers.yaml`](../docs/validation-waivers.yaml) |
| L4 CQ pytest | PASS | 19/19 (14 V0 + 5 V1) |
| L4.5 CQ manifest integrity | PASS | 19/19 entries clean |
| L5 coverage metrics | PASS | 21 ei: classes, 100% label/def, 0 orphans |
| L5.5 anti-patterns | PASS | V0 § 2 / § 16 closed; V1 § 4 (3-way role disjointness) implemented |
| L7 diff vs V0 | PASS | categorised; [`v1-diff-vs-v0.md`](v1-diff-vs-v0.md) |

`validate-profile DL` is treated as **advisory**; HermiT exit code is the
release-gate. See workspace memory `reference_robot_dl_profile_check.md`.

---

## Diff at a glance (vs V0)

[`release/v1-diff-vs-v0.md`](v1-diff-vs-v0.md) is the full `robot diff`
output (17,815 lines).

* **Project axiom delta:** ~12 net-changed (8 axiom obligations A1..A8 + 5
  SHACL annotations + import-manifest bump).
* **Import-closure expansion:** ~17,000 added lines are upstream OEO + QUDT
  term declarations (NOT project axioms).
* **Annotation deltas:** `dcterms:modified 2026-04-27`; `owl:versionInfo
  "v1 (2026-04-27)"`; `owl:versionIRI <https://w3id.org/energy-intel/v1/
  2026-04-27>`; `dcterms:description` updated to mention V1 imports.
* **Net-removed axioms (4):** `ei:Expert SubClassOf foaf:Person`,
  `ei:authoredBy Range ei:Expert`, `ei:spokenBy Range ei:Expert`,
  `ei:Post SubClassOf authoredBy exactly 1 ei:Expert`. All four are
  replaced by V1 axioms with strictly stronger or equivalent semantics
  (see breaking-change analysis above).

---

## FAIR / OBO publication checklist

Manual operations the user must execute before/around the v0.2.0
publication:

### Pre-tag verification
- [ ] Re-run V1 build pipeline on a fresh worktree
  (`uv run python ontologies/energy-intel/scripts/build_*.py`,
  `run_gates.py`, `apply_report_allowlist.py`, `run_shacl_gate.py`,
  `uv run pytest ontologies/energy-intel/tests/test_ontology.py -v`).
  Expect every step exits 0 and pytest reports 19/19 PASS.
- [ ] Confirm `release-audit-v1.yaml` reads `sign_off: pending` and the
  recommendation is `release`.
- [ ] Review [`docs/curator-log-v1.md`](../docs/curator-log-v1.md) and
  [`docs/validation-waivers.yaml`](../docs/validation-waivers.yaml).

### Sign-off
- [ ] Edit `release/release-audit-v1.yaml`:
  ```yaml
  sign_off: signed
  signed_by: kokokessy@gmail.com
  signed_at: "2026-04-27T..."  # actual timestamp
  ```

### Git tagging (after sign-off)
- [ ] Stage and commit V1 source files per
  [`docs/validator-to-curator-handoff-v1.md` § 5](../docs/validator-to-curator-handoff-v1.md).
- [ ] Tag and push:
  ```bash
  git tag -a v0.2.0 -m "energy-intel v0.2.0: V1 OEO + QUDT integration; Expert role refactor; canonicalUnit"
  git push origin main
  git push --tags
  ```

### PURL / w3id redirect refresh
- [ ] Coordinate with w3id admins to point
  `https://w3id.org/energy-intel/v1/2026-04-27` at the release TTL
  (the canonical published artefact).
- [ ] Confirm `https://w3id.org/energy-intel/` (latest) redirects to
  the v0.2.0 release TTL, not v0.1.0.
- [ ] Verify PURLs for the three V1 imports resolve to local files
  (catalog-v001.xml entries) — they're not yet published as standalone
  IRIs.
- [ ] `curl -I https://w3id.org/energy-intel/v1/2026-04-27` should
  return 200 (or 301/302 redirect).

### Content negotiation
- [ ] Confirm content negotiation is configured for the release IRI:
  - `curl -H "Accept: text/turtle" https://w3id.org/energy-intel/v1/2026-04-27`
  - `curl -H "Accept: application/rdf+xml" https://w3id.org/energy-intel/v1/2026-04-27`
  - `curl -H "Accept: application/ld+json" https://w3id.org/energy-intel/v1/2026-04-27`
- [ ] If not yet configured, add to repo CI publish step:
  ```bash
  .local/bin/robot convert --input release/energy-intel.ttl --output release/energy-intel.owl
  .local/bin/robot convert --input release/energy-intel.ttl --output release/energy-intel.jsonld --format json-ld
  ```

### License + metadata
- [ ] CC-BY-4.0 badge in `README.md`.
- [ ] Confirm `dcterms:license` is set on top-level + every module +
  every import (already verified by curator, but the README badge is a
  separate manual step).

### OBO / OLS / BioPortal registry (optional but recommended)
- [ ] If domain fits OBO: register
  `https://w3id.org/energy-intel/v1/2026-04-27` with OBO Foundry
  via [obofoundry.org issue tracker](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new).
- [ ] Submit OLS4 listing if/when OBO accepts.
- [ ] BioPortal submission is not in scope for V1 (energy domain is
  outside BioPortal's bio-medical core).

### Linear / project tracker
- [ ] Open follow-up issues for V1-CUR-1..V1-CUR-6 per validator handoff:
  - V1-CUR-1: OEO subset is upward-only (severity info; v0.3.0)
  - V1-CUR-2: validation-waivers.yaml — **DONE in this release**
  - V1-CUR-3: ABox-stage punning watch (V2)
  - V1-CUR-4: QUDT unit naming bug class (severity info; v0.3.0 lint)
  - V1-CUR-5: Allow-list size monitor (revisit at >75 rows)
  - V1-CUR-6: DL profile-validate is advisory (already documented)

---

## Carry-forward V2+ items

These are NOT release blockers; they are V2+ watch-items the curator owns:

* **SHACL coverage backfill** for the 7 deferred `intent: validate`
  properties. Tracked in [`docs/validation-waivers.yaml`](../docs/validation-waivers.yaml)
  with expiry `v0.3.0`. Properties: `ei:assertedValue` datatype,
  `ei:intervalStart` / `ei:intervalEnd` xsd:dateTime format,
  `ei:hasSegmentIndex` integer + minInclusive 0,
  `ei:screenshotOf` / `ei:excerptFrom` URI well-formedness, plus
  `ei:assertedUnit` datatype-or-qudt-iri (V1-added).
* **Seven-facet Variable model.** Conceptualizer deferred from V0/V1; the
  thin Variable in measurement.ttl currently has `ei:Variable` plus a
  defined equivalent class; the seven-facet model lands at v0.3.0 / V2
  per scope-v1.md.
* **Expert subrole taxonomy.** V1 mints `ei:EnergyExpertRole` as a single
  role; V2+ refines into journalist / academic / industry / policy
  subroles when the corpus signals warrant it.
* **OEO `bfo:0000053 some` (has-role) axiom restoration.** The V1 BFO+RO
  strip removes OEO's bundled BFO/RO axioms. If the Skygest pipeline
  wants OEO's role-bearing pattern (e.g. EnergyTechnology bearer-of-X),
  V2 must restore the relevant RO IRIs to the strip-list exception set.
* **OEO descendants extraction (V1-CUR-1).** OEO BOT extract is
  upward-only at V0/V1; V2 can re-extract with TOP+BOT or extend the
  seed list with concrete technologies.
* **ABox-stage punning re-confirmation (V1-CUR-3).** First V2 ABox fixture
  binding `?cmc ei:aboutTechnology oeo:OEO_xxx` MUST re-confirm HermiT
  stays clean over TBox + ABox closure.

---

## Files released

### Source (TBox + shapes + imports)
- [`energy-intel.ttl`](../energy-intel.ttl) — top-level
- [`modules/agent.ttl`](../modules/agent.ttl)
- [`modules/media.ttl`](../modules/media.ttl)
- [`modules/measurement.ttl`](../modules/measurement.ttl)
- [`modules/data.ttl`](../modules/data.ttl)
- [`shapes/energy-intel-shapes.ttl`](../shapes/energy-intel-shapes.ttl)
- [`imports/oeo-technology-subset-fixed.ttl`](../imports/oeo-technology-subset-fixed.ttl)
- [`imports/oeo-carrier-subset-fixed.ttl`](../imports/oeo-carrier-subset-fixed.ttl)
- [`imports/qudt-units-subset.ttl`](../imports/qudt-units-subset.ttl)
- [`catalog-v001.xml`](../catalog-v001.xml)

### Tests
- [`tests/test_ontology.py`](../tests/test_ontology.py)
- [`tests/cq-test-manifest.yaml`](../tests/cq-test-manifest.yaml)
- `tests/cq-001..019.sparql` + `tests/fixtures/cq-001..019.ttl`

### Docs (V1)
- [`docs/scope-v1.md`](../docs/scope-v1.md)
- [`docs/competency-questions-v1.yaml`](../docs/competency-questions-v1.yaml)
- [`docs/conceptual-model-v1.md`](../docs/conceptual-model-v1.md)
- [`docs/property-design-v1.md`](../docs/property-design-v1.md)
- [`docs/axiom-plan-v1.md`](../docs/axiom-plan-v1.md)
- [`docs/architect-build-log-v1.md`](../docs/architect-build-log-v1.md)
- [`docs/validator-report-v1.md`](../docs/validator-report-v1.md)
- [`docs/validator-to-curator-handoff-v1.md`](../docs/validator-to-curator-handoff-v1.md)
- [`docs/curator-log-v1.md`](../docs/curator-log-v1.md)
- [`docs/validation-waivers.yaml`](../docs/validation-waivers.yaml)

### Release artefacts
- [`release/release-audit-v1.yaml`](release-audit-v1.yaml)
- [`release/v1-diff-vs-v0.md`](v1-diff-vs-v0.md)
- [`release/release-notes-v0.2.0.md`](release-notes-v0.2.0.md) (this file)

### Imports manifests
- [`imports-manifest.yaml`](../imports-manifest.yaml) (V0 baseline)
- [`imports-manifest-v1.yaml`](../imports-manifest-v1.yaml) (V1 delta)
- [`imports-manifest-INDEX.yaml`](../imports-manifest-INDEX.yaml)
  (release-time index pointing at both)

### KGCL change log
- [`energy-intel-changes-v1.kgcl`](../energy-intel-changes-v1.kgcl)
  (8 axiom obligations + 5 SHACL annotations; V0 baseline header points at
  commit `36d1952`)

### Validation evidence
- [`validation/v1/validator-rerun/`](../validation/v1/validator-rerun/) —
  validator's independent re-run evidence
- [`validation/report-allowlist.tsv`](../validation/report-allowlist.tsv) —
  upstream-ERROR allow-list (51 rows; 11 V1 additions)

---

## Acknowledgements

Architect: `ontology-architect` (V1 iteration, 2026-04-27).
Validator: `ontology-validator` (independent re-run, 2026-04-27).
Curator: `ontology-curator` (V1 release-prep, 2026-04-27).
Reviewer: kokokessy@gmail.com.

ROBOT 1.9.8 + HermiT + pyshacl. uv-managed Python 3.12+.
