# V1 Architect Build Log — `energy-intel`

**Authored:** 2026-04-27 by `ontology-architect` (V1 iteration)
**Architect session:** single sitting, 2026-04-27
**Build regime:** Standalone POD (custom `scripts/build_*.py`), unchanged from V0

This log records the order of operations the V1 architect performed, including reasoner / report / pyshacl results at each step. Raw tool outputs are in `validation/v1/`.

---

## Step 1 — Read upstream V1 inputs

Sources read (in this order):
1. `docs/conceptualizer-to-architect-handoff-v1.md` (blueprint with 8 obligations)
2. `docs/conceptual-model-v1.md` (CQ-Q-1/2/3 decisions)
3. `docs/property-design-v1.md`
4. `docs/bfo-alignment-v1.md`
5. `docs/anti-pattern-review-v1.md`
6. `docs/shacl-vs-owl-v1.md`
7. `imports-manifest-v1.yaml`
8. V0 baseline: `energy-intel.ttl`, `modules/*.ttl`, `shapes/energy-intel-shapes.ttl`, `tests/test_ontology.py`, `tests/cq-test-manifest.yaml`, `tests/fixtures/cq-001..014.ttl`, `tests/cq-015..019.sparql`, `validation/report-allowlist.tsv`, `scripts/build_modules.py`, `scripts/build_shapes.py`, `scripts/build_fixtures.py`, `scripts/build_v1_imports.py`.

V0 baseline state: HermiT-clean, 0 project-origin ERRORs after allow-list, pytest 14/14.

---

## Step 2 — Re-annotate OEO subset ontology IRIs

**Discovery:** Both V0 OEO subsets (technology + carrier) declare the same upstream OEO root IRI `<https://openenergyplatform.org/ontology/oeo/>` as their ontology IRI. If we wire both into the V1 top-level via `owl:imports`, OWLAPI / ROBOT cannot disambiguate.

**Action:** Extended `scripts/build_v1_imports.py` with a `reannotate_ontology_iri` step that runs after the BFO+RO strip. The step:
1. Locates the single owl:Ontology node in each fixed subset.
2. Migrates every triple from old_iri to a project-namespaced IRI.
3. Adds a versionIRI, dcterms:title, dcterms:description, owl:versionInfo.

New IRIs:
- `imports/oeo-technology-subset-fixed.ttl` -> `https://w3id.org/energy-intel/imports/oeo-technology-subset`
- `imports/oeo-carrier-subset-fixed.ttl` -> `https://w3id.org/energy-intel/imports/oeo-carrier-subset`

The QUDT subset already declared `https://w3id.org/energy-intel/imports/qudt-units-subset` (built fresh by `build_v1_imports.py`); no migration needed.

**Build:** `uv run python ontologies/energy-intel/scripts/build_v1_imports.py`
- Phase 1 (BFO+RO strip): OK (both fixed files written).
- Phase 1.5 (re-annotate): OK (both ontology IRIs migrated).
- Phase 2 (QUDT slice): cached source used; 25 units + 39 quantitykinds pulled.
- Phase 3 (merge + HermiT reasoner gate): merge OK; HermiT clean.
- Logs: `validation/v1-bfo-remediation/v1-merge.log`, `validation/v1-bfo-remediation/v1-hermit-reason.log`.

---

## Step 3 — Update `catalog-v001.xml`

Hand-edited `catalog-v001.xml` with three new `<uri>` rows mapping the project-namespaced V1 import IRIs to the local file paths. This lets `robot merge --catalog catalog-v001.xml` resolve V1 imports without HTTP fetches.

---

## Step 4 — Implement A1..A8 in `build_modules.py`

Helpers added:
- `equivalent_class_intersection_of(g, cls, members)` — equivalent-class as `intersectionOf` for A2.
- `restriction_some(g, prop, filler) -> BNode` — returns a fresh BNode for an existential restriction (so we can compose it inside an intersection list).

V1 metadata constants:
- `V1_VERSION_INFO = "v1 (2026-04-27)"`
- `V1_MODIFIED = "2026-04-27"`
- `V1_TOP_VERSION_IRI = "https://w3id.org/energy-intel/v1/2026-04-27"`

Module changes:
- **`build_agent`**: A1 (mint EnergyExpertRole + role-inheres-in-Person restriction); A2 (Expert as EquivalentTo, drop V0 SubClassOf foaf:Person); A3 (3-way disjointness).
- **`build_media`**: A6 (authoredBy range to foaf:Person; Post restriction onClass updated); A7 (spokenBy range to foaf:Person).
- **`build_measurement`**: A4 (canonicalUnit functional object property); A5 (CMC SubClassOf canonicalUnit max 1 qudt:Unit); QUDT subset added to module imports.
- **`build_top_level`**: 3 V1 imports wired; versionIRI bumped to V1.

**Build:** `uv run python ontologies/energy-intel/scripts/build_modules.py` -> all five modules regenerated.

---

## Step 5 — Run reasoner + report gates per module

`uv run python ontologies/energy-intel/scripts/run_gates.py` -> all merge/reason exit 0.

Per-module errors (raw, pre-allowlist):

| Module | Merge | Reason | Errors | Warns | Infos |
|---|---|---|---|---|---|
| agent | 0 | 0 | 4 | 153 | 26 |
| media | 0 | 0 | 6 | 196 | 61 |
| measurement | 0 | 0 | 641 | 432 | 86 |
| data | 0 | 0 | 641 | 433 | 86 |
| top-level | 0 | 0 | 687 | 469 | 180 |

Errors at measurement / data / top-level are dominated by upstream-origin QUDT / OEO / IAO / UO / dcterms multiple_labels, duplicate_label, multiple_definitions, missing_label rule hits — all upstream W3C/OBO patterns.

`uv run python ontologies/energy-intel/scripts/apply_report_allowlist.py` (with V1 allow-list extensions): **687 ERRORs allow-listed; 0 project-origin ERRORs.**

Allow-list extensions added (justified per row in `validation/report-allowlist.tsv`):
1. `duplicate_label https://w3id.org/energy-intel/concept/aggregation-type` — APOLLO_SV cross-namespace collision class (parallel to existing `/count` row).
2. `duplicate_label http://qudt.org/vocab/quantitykind/` — upstream QUDT.
3. `multiple_labels http://qudt.org/vocab/quantitykind/` — upstream QUDT.
4. `multiple_labels http://qudt.org/vocab/unit/` — upstream QUDT multilingual labels.
5. `duplicate_label https://openenergyplatform.org/ontology/oeo/` — upstream OEO.
6. `multiple_labels https://openenergyplatform.org/ontology/oeo/` — upstream OEO.
7. `multiple_definitions https://openenergyplatform.org/ontology/oeo/` — upstream OEO+ENVO merge.
8. `multiple_definitions IAO:` — upstream OBO.
9. `multiple_definitions UO:` — upstream UO.
10. `missing_label rdf:` — `rdf:PlainLiteral` (upstream W3C).

---

## Step 6 — `validate-profile DL` on top-level merged closure

```bash
.local/bin/robot validate-profile --profile DL \
  --input validation/merged-top-level.ttl \
  --output validation/v1/profile-validate-dl.txt
```

Output (V1, `validation/v1/profile-validate-dl.txt`): 743 lines, all "Cannot pun between properties" violations. The 41 distinct punned IRIs are exclusively upstream:
- `dcterms:` (alternative, available, bibliographicCitation, created, date, dateAccepted, dateCopyrighted, dateSubmitted, identifier, issued, modified, title, valid)
- `skos:` (closeMatch, exactMatch, relatedMatch)
- `dcat:` (compressFormat, distribution, hasCurrentVersion, hasVersion, inSeries, last, mediaType, packageFormat, resource)
- `foaf:` (msnChatID, yahooChatID, icqChatID, etc.)
- `prov:` (wasDerivedFrom, etc.)

**0 project-namespaced (`https://w3id.org/energy-intel/`) punning.** Confirms conceptualizer's CQ-Q-3 prediction (V0 punning warnings carry forward; no NEW V1 violations).

---

## Step 7 — Implement S-V1-1 .. S-V1-5 in `build_shapes.py`

Added imports: `Collection` (for `sh:in` lists), `SKOS` (for the skos:Concept-or-OEO check).
Added namespaces: QUDT, UNIT, OEO, BFO.
Added constants: `QUDT_UNIT_SUBSET_LOCAL_NAMES` (25 unit names), `OEO_TECHNOLOGY_ROOTS` (3 OEO seed IRIs).
Added helper `add_v1_prefixes_decl` (declares ei:, xsd:, rdf:, rdfs:, skos:, foaf:, bfo:, oeo:, qudt:, unit: for V1 SPARQL constraints).
V1 prefix-decl ontology IRI: `https://w3id.org/energy-intel/shapes/prefix-decl-v1`.

Shape implementations (in order they fire):
- S-V1-1: `sh:in (...)` over the 25 unit IRIs.
- S-V1-2: SPARQL constraint `assertedUnit without canonicalUnit`; severity at NodeShape (not on the SPARQLConstraint).
- S-V1-3: SPARQL constraint `?author lacks bfo:0000053 ?role . ?role a EnergyExpertRole`.
- S-V1-4: SPARQL constraint same shape as S-V1-3 but on PodcastSegment.spokenBy with severity Warning.
- S-V1-5: SPARQL constraint walking `(rdfs:subClassOf|skos:broader)*` to one of the 3 OEO roots, OR matching `skos:Concept`.

**Build:** `uv run python ontologies/energy-intel/scripts/build_shapes.py` -> 172 triples written. V0 prefix-decl preserved for V0 shapes; V1 prefix-decl added.

---

## Step 8 — Implement V1 fixtures + extend V0 fixtures

`build_fixtures.py` extended:
- New namespaces: FOAF, BFO, QUDT, UNIT, QK, OEO.
- `_base_graph()` binds all V1 prefixes.
- `_post()` extended additively with role-bearer triples (`?expert a foaf:Person ; bfo:0000053 ?role . ?role a ei:EnergyExpertRole`); deterministic role IRI per expert (suffix `#energy-expert-role`).
- `cq011()` extended to add role-bearer triples for podcast speakers.
- New builders: `cq015()` (OEO root), `cq016()` (unit:GigaW), `cq017()` (unit:GigaW + qudt:hasQuantityKind chain), `cq018()` (Person+role+Post triangle), `cq019()` (compose).
- CONTRACTS dict extended with V1 row-count contracts.

**Note on cq-015/019 OEO binding:** The V0 OEO BOT extract pulls the *upward* parent path of the seeds, not descendants. `OEO_00020267` (energy technology) has no descendants in the subset. The CQ-015 SPARQL uses `(skos:broader|rdfs:subClassOf)*` which matches the empty path (a value reaches itself). Tagging the CMC directly with `OEO_00020267` satisfies the property-path walk. When V1.x extends the OEO seed list with concrete technologies, fixtures rebind to specific descendants without changing SPARQL.

**Note on `unit:GW` -> `unit:GigaW` SPARQL fix in cq-016:** QUDT 2.1 vocab/unit uses SI-prefix-as-word naming (`unit:GigaW`, `unit:MegaW`, `unit:TeraW-HR`). The V0 manifest's seed list had `unit:GW` / `unit:MW` / `unit:TW-HR` which do not exist in QUDT 2.1. `imports-manifest-v1.yaml` confirms the corrected names. Architect updated `tests/cq-016.sparql` to use `unit:GigaW`. This is the same bug class as the OEO prefix bug the conceptualizer flagged — independent. cq-015 / cq-019 OEO prefix already correct (`https://openenergyplatform.org/ontology/oeo/`).

**Build:** `uv run python ontologies/energy-intel/scripts/build_fixtures.py` -> 19 fixtures verified, 19/19 row-count contracts pass.

---

## Step 9 — Run pyshacl gate on all 19 fixtures

`uv run python ontologies/energy-intel/scripts/run_shacl_gate.py`:

```
  cq-001  PASS              cq-008  PASS (1 warn)
  cq-002  PASS              cq-009  PASS
  cq-003  PASS              cq-010  PASS
  cq-004  PASS              cq-011  PASS
  cq-005  PASS              cq-012  PASS
  cq-006  PASS              cq-013  PASS
  cq-007  PASS              cq-014  PASS
  cq-015  PASS              cq-016  PASS
  cq-017  PASS              cq-018  PASS
  cq-019  PASS
```

**19/19 conform with 0 Violations.** cq-008 has 1 Warning (S-V1-2 resolvability gate firing on the bare CMC, which has assertedUnit "GW" but no canonicalUnit — this is **the intended behaviour** of S-V1-2; cq-008 fixture exists to test cross-expert join under partial resolution).

Per-fixture results: `validation/shacl-results-cq-NNN.ttl`.
Summary: `validation/v1/shacl-summary.json`.

`scripts/run_shacl_gate.py` was patched to count Warnings separately and only fail on Violations (V0 version failed on `pyshacl.conforms == False`, which fires on any result regardless of severity).

---

## Step 10 — Run pytest CQ acceptance suite

`tests/test_ontology.py` extended:
- `EXPECTED_BANDS` extended with CQ-015..019 (all `(0, None)` in line with `0..n` cardinality contracts).
- `EXPECTED_COLUMNS` extended with CQ-015..019 column names matching the SPARQL projections.

`tests/cq-test-manifest.yaml`:
- `preflight_summary` updated: 19 fixtures built, 19 passing, 0 skipped.
- CQ-015..019 entries flipped from `fixture_run_status: skipped` to `pass`.
- `fixture_path` and `fixture_rationale` updated.

**Run:** `uv run pytest ontologies/energy-intel/tests/test_ontology.py -v` -> **19 passed.**
Log: `validation/v1/pytest-cq-suite.log`.

---

## Step 11 — Final ruff lint + format

`uv run ruff check ontologies/energy-intel/scripts/` -> All checks passed.
`uv run ruff format --check ontologies/energy-intel/scripts/` -> 9 files already formatted.

---

## Step 12 — Idempotency verification

Re-ran `build_modules.py`, `build_shapes.py`, `build_fixtures.py` — all produced identical output. Re-ran `pytest` — 19/19 PASS unchanged.

---

## Final state — gate evidence summary

| Gate | Result | Evidence |
|---|---|---|
| OWL profile (DL) | All upstream-origin punning; 0 project-namespaced | `validation/v1/profile-validate-dl.txt` |
| HermiT reasoner (per module) | exit 0; 0 unsatisfiable | `validation/v1/reason-{agent,media,measurement,data,top-level}.log` |
| HermiT reasoner (top-level merged) | exit 0; reasoned closure 1.3 MB | `validation/v1/reason-top-level.log`; `validation/v1/reasoned-top-level.ttl` |
| ROBOT report (top-level) | 687 ERRORs (raw); **0** project-origin after allow-list | `validation/v1/report-top-level.tsv`; `validation/v1/report-top-level-filtered.tsv`; `validation/v1/report-project-errors.tsv` |
| pyshacl (19 fixtures) | 19/19 conform; 0 Violations; 1 Warning (cq-008 by design) | `validation/v1/shacl-summary.json`; `validation/shacl-results-cq-*.ttl` |
| pytest CQ suite | 19/19 PASS | `validation/v1/pytest-cq-suite.log` |
| Ruff lint + format | clean | (no error output) |

---

## Anomalies + watch items

1. **OEO subset is upward-only.** The V0 BOT extract drags parents, not descendants. CQ-015 / CQ-019 fixtures bind directly to the energy-technology root because that's the only OEO class in the subset that the SPARQL pattern can hit. V1.x curator should either re-extract with TOP+BOT (drag descendants) or extend the seed list with specific technologies (solar-PV, onshore-wind) — see `imports-manifest-v1.yaml § open_questions`.

2. **`unit:GW` -> `unit:GigaW` bug class is wider than the conceptualizer flagged.** The handoff called out the OEO prefix bug in cq-015/cq-019 SPARQL. There was a parallel `unit:GW` bug in cq-016 SPARQL that needed the SI-prefix-as-word correction (the V0 imports manifest seed list was *also* wrong but `build_v1_imports.py` already uses the corrected names). Now fixed in `tests/cq-016.sparql`.

3. **pyshacl `sh:severity` placement.** pyshacl ignores `sh:severity` placed on the SPARQLConstraint blank node — it must be on the NodeShape itself. Fixed for S-V1-2 and S-V1-4 (both Warnings).

4. **V0 fixture migration is additive.** V0 fixtures now carry explicit role-bearer triples for every author Expert. V0 SPARQL still passes because it binds `?expert a ei:Expert` (which V0 fixtures still assert). This deviates slightly from the conceptualizer's "no migration needed" note — strictly true for the SPARQL CQ tests, but pyshacl S-V1-3 needs the explicit role-bearer triples because pyshacl runs with `inference="rdfs"`, not OWL-DL classification.

5. **HermiT clean despite OWL 2 DL profile violations.** The 41 punned IRIs are upstream property-pun cases (annotation/data/object/class). They pre-date V1 and were already present in V0. HermiT reasoner doesn't reject these (it operates on a more permissive subset) but `validate-profile DL` flags them strictly. Per workspace memory `reference_robot_dl_profile_check.md`, this is the expected V0+V1 baseline.
