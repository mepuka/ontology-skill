# Validator -> Curator Handoff — `energy-intel` V1

**From:** `ontology-validator` (V1 iteration; 2026-04-27)
**To:** `ontology-curator` (V1 release + ongoing maintenance)
**Predecessor:** [validator-to-curator-handoff.md](validator-to-curator-handoff.md) (V0; signing v0.1.0)
**Validator report:** [`validator-report-v1.md`](validator-report-v1.md)
**Release audit:** [`../release/release-audit-v1.yaml`](../release/release-audit-v1.yaml)
**Diff vs V0:** [`../release/v1-diff-vs-v0.md`](../release/v1-diff-vs-v0.md)

---

## 1. TL;DR — release readiness

**Recommendation: release v0.2.0.**

All 8 validator gates (L0..L7 plus L3.5 / L4.5 / L5.5) pass on independent re-run. No loopbacks. V0's open `construct_mismatch` loopback (OEO + BFO-2020 incompatibility) is closed by V1's BFO+RO strip pipeline. V0's role-type-confusion and punning anti-pattern watches are closed at the TBox stage.

Curator must:

1. Sign the release audit (`release-audit-v1.yaml: sign_off → signed`).
2. Tag the release `v0.2.0` after architect's V1 changes are committed.
3. Address the six residual concerns listed in § 4 below; none are release-blocking but each carries a clear curator owner.

---

## 2. Final gate state (V1 validator-rerun)

| Gate | Verdict | Evidence |
|---|---|---|
| L0 syntax / catalog merge | PASS | `validation/v1/validator-rerun/preflight/merge.log` (exit 0) |
| L0 DL profile | WARN-accepted, upstream-only | `validation/v1/validator-rerun/profile/profile-validate-dl.txt` (41 distinct, 0 project) |
| L1 HermiT (per module + top-level closure with V1 imports) | PASS, exit 0 | `validation/v1/validator-rerun/reason/hermit.log` |
| L2 ROBOT report + allow-list | PASS, 0 project-origin ERRORs | `validation/v1/validator-rerun/report/allowlist-runner.log` (687 suppressed; 0 project) |
| L3 pyshacl (19 fixtures × 9 shapes) | PASS, 19/19, 0 Violations, 1 Warning | `validation/v1/validator-rerun/shacl/shacl-summary.json` |
| L3.5 SHACL coverage | PASS, V1 intent: validate 100% | `shapes/energy-intel-shapes.ttl` (9 NodeShapes) |
| L4 CQ pytest | PASS, 19/19 (14 V0 + 5 V1) | `validation/v1/validator-rerun/cqs/pytest-cq-suite.log` |
| L4.5 CQ manifest integrity | PASS, 19/19 entries clean | scripted audit |
| L5 coverage metrics | PASS, 21 classes, 100% label / def, 0 orphans | `validation/v1/validator-rerun/coverage/*.csv` |
| L5.5 anti-patterns | PASS, V0 § 2 / § 16 closed; V1 § 4 implemented | `validation/v1/validator-rerun/anti-patterns/*.csv` |
| L7 diff vs V0 | PASS, categorised | `release/v1-diff-vs-v0.md` |

Loopbacks raised: **0.**

---

## 3. V0 loopbacks closed by V1 (curator must verify each on release)

| V0 loopback | V0 status | V1 closure |
|---|---|---|
| `shacl_violation` (V0 S-1 DidSchemeOnAuthoredBy) | resolved at V0 sign-off via shape patch | carried forward; V1 fixtures still pass |
| `construct_mismatch` (OEO + BFO-2020 inconsistent under HermiT) | non-blocking-for-V0 | **CLOSED — V1 BFO+RO strip eliminates the BFO version conflict; merged closure HermiT-clean** |
| `role_type_confusion` (V0 anti-pattern § 2) | watch | **CLOSED — V1 A1+A2: ei:Expert ≡ foaf:Person ⊓ ∃bfo:0000053.EnergyExpertRole replaces V0 SubClassOf** |
| `punning_at_TBox` (V0 anti-pattern § 16) | watch | **CLOSED at TBox stage — V1 closure HermiT-clean; ABox-stage punning watch carries forward to V2** |

Curator recordkeeping: each closure should be reflected in the V0->V1 release notes as "issue → V0 finding → V1 mitigation → evidence path".

---

## 4. Residual curator items (none blocking release)

### V1-CUR-1 — OEO subset is upward-only

**Severity:** info. **Blocking:** no.

**Description:** The V0 BOT extract pulls only the parent path of seed terms. `OEO_00020267` (energy-technology), `OEO_00020039` (energy-carrier), and `OEO_00000011` (energy-converting-component) all have 0 descendants in the subset. CQ-015 / CQ-019 fixtures bind the root directly (the empty-path case in the property-path walk).

**Curator action:** at the next import refresh, choose:
1. Re-extract with TOP+BOT (drag descendants), OR
2. Extend the seed list in `scripts/build_v1_imports.py:OEO_*_SEEDS` with concrete technologies (`solar-pv`, `onshore-wind`, `offshore-wind`, `lithium-ion-battery`, etc.).

Decision is captured as `imports-manifest-v1.yaml § open_questions V1-IM-Q1`.

### V1-CUR-2 — `docs/validation-waivers.yaml` does not exist

**Severity:** warn. **Blocking:** no.

**Description:** The carry-forward V0/V1 deferred SHACL items live only inside `property-design.md` / `property-design-v1.md` / `anti-pattern-review-v1.md`. The validator workflow expects a single `docs/validation-waivers.yaml` listing each deferred shape with `owner`, `rationale`, `expiry`.

**Curator action:** create `docs/validation-waivers.yaml` with at minimum the following 4 rows, each carrying owner + rationale + expiry:

```yaml
waivers:
  - shape: assertedValue_datatype
    owner: ontology-architect
    rationale: "V1 stays string/literal on ei:assertedValue; richer datatype check deferred to V2 numeric-vs-categorical refactor"
    expiry: "v0.3.0"
  - shape: intervalStart_intervalEnd_format
    owner: ontology-architect
    rationale: "xsd:dateTime format check deferred; current V1 fixtures use string surface form"
    expiry: "v0.3.0"
  - shape: hasSegmentIndex_integer_monotonic
    owner: ontology-architect
    rationale: "PodcastSegment.hasSegmentIndex shape deferred until V2 podcast-ingest lane"
    expiry: "v0.3.0"
  - shape: screenshotOf_excerptFrom_uri_well_formedness
    owner: ontology-architect
    rationale: "URI well-formedness on media attachment links deferred until V2"
    expiry: "v0.3.0"
```

### V1-CUR-3 — ABox-stage punning watch (forward-looking, V2)

**Severity:** info. **Blocking:** no (V1 ships TBox-only).

**Description:** When V2 ships its first ABox fixtures asserting `?cmc ei:aboutTechnology oeo:OEO_xxx`, the validator must re-confirm HermiT stays clean over the TBox + ABox closure. The TBox-stage proof (V1) is necessary but not sufficient.

**Curator action:** add a V2 release-gate item: "Run HermiT on TBox + first ABox fixture batch; confirm exit 0 and 0 unsatisfiable."

Anti-pattern review V1 § 2 / § 5 record this watch.

### V1-CUR-4 — QUDT unit naming bug class (V0 manifest legacy)

**Severity:** info. **Blocking:** no.

**Description:** V0 `imports-manifest.yaml` seeds had `unit:GW` / `unit:MW` / `unit:TW-HR` — these IRIs do not exist in QUDT 2.1, which uses SI-prefix-as-word naming (`unit:GigaW` / `unit:MegaW` / `unit:TeraW-HR`). `imports-manifest-v1.yaml` already corrected this. Architect updated `tests/cq-016.sparql` from `unit:GW` to `unit:GigaW` during V1.

**Curator action:** at the next import refresh, verify all references in test SPARQL files, fixtures, and any new content use SI-prefix-as-word form. Add a CI check or pre-commit lint that greps for the bad forms (`unit:[GMTk]W(\b|[^a-zA-Z])` excluding `unit:Giga|unit:Mega|unit:Tera|unit:Kilo`).

### V1-CUR-5 — Allow-list size monitor

**Severity:** info. **Blocking:** no.

**Description:** `validation/report-allowlist.tsv` grew from 33 V0 rows (post-V0-fix) → 40 (V0 release-time) → 51 (V1). Each row is justified, signed, and dated.

**Curator action:** track allow-list size at every release. Revisit at >75 rows — that's the threshold where upstream-noise suppression starts to hide legitimate project-origin issues. At each revisit, audit a sample of 10 rows and confirm each justification still applies.

### V1-CUR-6 — DL profile-validate is advisory

**Severity:** info. **Blocking:** no.

**Description:** `robot validate-profile DL` flags 41 distinct upstream punned IRIs. HermiT exits 0 on the same closure. Per workspace memory `reference_robot_dl_profile_check.md`, the project policy is to treat HermiT exit code as ground truth and `validate-profile` as advisory.

**Curator action:** document this policy in the release notes. Add to the README / CONVENTIONS.md a short note: "`validate-profile DL` is advisory; HermiT exit code is the release-gate." This prevents the next validator iteration from raising it as a fresh loopback.

---

## 5. What curator must execute for v0.2.0 release

In order:

1. **Verify the V1 build is reproducible.** Re-run on a fresh worktree:
   ```bash
   uv run python ontologies/energy-intel/scripts/build_v1_imports.py
   uv run python ontologies/energy-intel/scripts/build_modules.py
   uv run python ontologies/energy-intel/scripts/build_shapes.py
   uv run python ontologies/energy-intel/scripts/build_fixtures.py
   uv run python ontologies/energy-intel/scripts/run_gates.py
   uv run python ontologies/energy-intel/scripts/apply_report_allowlist.py
   uv run python ontologies/energy-intel/scripts/run_shacl_gate.py
   uv run pytest ontologies/energy-intel/tests/test_ontology.py -v
   uv run ruff check ontologies/energy-intel/scripts/
   uv run ruff format --check ontologies/energy-intel/scripts/
   ```
   Expected: every step exits 0; pytest 19/19 PASS; allow-list `0 project-origin ERRORs`.

2. **Stage and commit V1 source files.**
   ```
   ontologies/energy-intel/energy-intel.ttl
   ontologies/energy-intel/catalog-v001.xml
   ontologies/energy-intel/imports-manifest-v1.yaml
   ontologies/energy-intel/imports/oeo-technology-subset-fixed.ttl
   ontologies/energy-intel/imports/oeo-carrier-subset-fixed.ttl
   ontologies/energy-intel/imports/qudt-units-subset.ttl
   ontologies/energy-intel/modules/{agent,media,measurement,data}.ttl
   ontologies/energy-intel/shapes/energy-intel-shapes.ttl
   ontologies/energy-intel/tests/{test_ontology.py,cq-test-manifest.yaml,cq-016.sparql,fixtures/cq-*.ttl}
   ontologies/energy-intel/scripts/{build_modules,build_shapes,build_fixtures,build_v1_imports,run_shacl_gate}.py
   ontologies/energy-intel/validation/report-allowlist.tsv
   ontologies/energy-intel/energy-intel-changes-v1.kgcl
   ontologies/energy-intel/docs/{axiom-plan-v1,architect-build-log-v1,architect-to-validator-handoff-v1,validator-report-v1,validator-to-curator-handoff-v1}.md
   ontologies/energy-intel/release/{release-audit-v1.yaml,v1-diff-vs-v0.md}
   ```

   Conventional commit suggestions:
   - `feat(energy-intel): land V1 axioms (A1..A8) and SHACL contracts (S-V1-1..S-V1-5)`
   - `feat(energy-intel): wire 3 V1 imports (OEO technology, OEO carrier, QUDT units subset)`
   - `test(energy-intel): add CQ-015..019 fixtures and SPARQL tests; extend pytest harness`
   - `docs(energy-intel): land V1 validator report, release audit, curator handoff`

3. **Tag v0.2.0.** After the commits land on `main`:
   ```bash
   git tag -a v0.2.0 -m "energy-intel v0.2.0: V1 OEO + QUDT integration; Expert role refactor; canonicalUnit"
   git push --tags
   ```

4. **Sign release-audit-v1.yaml.** Flip:
   ```yaml
   sign_off: signed
   signed_by: kokokessy@gmail.com
   signed_at: "2026-04-27T..."  # actual timestamp
   ```

5. **Address V1-CUR-1 / V1-CUR-2 in the next sprint.** V1-CUR-2 (validation-waivers.yaml) is the most concrete item and should land before the v0.3.0 prep cycle. V1-CUR-1 (OEO descendants) requires re-extraction work on the import pipeline.

6. **Update Linear / project tracker.** Each V1-CUR-* item should become a tracked issue with `severity` + `expiry` + `owner_skill`.

---

## 6. Files validator produced this session

* [`docs/validator-report-v1.md`](validator-report-v1.md) — comprehensive per-gate report with raw evidence cites.
* [`release/release-audit-v1.yaml`](../release/release-audit-v1.yaml) — release audit; `sign_off: pending`; recommendation `release`.
* [`release/v1-diff-vs-v0.md`](../release/v1-diff-vs-v0.md) — robot diff V0 (commit `36d1952`) vs V1 (current).
* [`docs/validator-to-curator-handoff-v1.md`](validator-to-curator-handoff-v1.md) — this document.
* `validation/v1/validator-rerun/` — the validator's independent re-run evidence (separate from architect's `validation/v1/`).

---

## 7. Confidence note

This validator pass independently re-ran every gate the architect ran. Architect's recorded results agree with validator's re-run on every numeric: 41 distinct punned IRIs, 687 ROBOT report ERRORs, 687 allow-list suppressions, 0 project-origin ERRORs, 19/19 SHACL conform, 1 Warning on cq-008, 19/19 pytest pass, 0 unsatisfiable classes, 21 ei: classes, 100% label / definition coverage, 0 orphans, 0 mixed class+individual.

The V1 release is ready to ship. Curator can proceed.
