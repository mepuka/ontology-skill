# Architect -> Validator Handoff — `energy-intel`, V1

**From:** `ontology-architect` (V1 iteration; 2026-04-27)
**To:** `ontology-validator` (V1 iteration)
**Predecessor handoff:** [architect-to-validator-handoff.md](architect-to-validator-handoff.md) (V0)
**Inputs the architect consumed:**
- [conceptualizer-to-architect-handoff-v1.md](conceptualizer-to-architect-handoff-v1.md) (8 obligations, 5 SHACL contracts)
- [conceptual-model-v1.md](conceptual-model-v1.md), [property-design-v1.md](property-design-v1.md), [bfo-alignment-v1.md](bfo-alignment-v1.md), [shacl-vs-owl-v1.md](shacl-vs-owl-v1.md), [anti-pattern-review-v1.md](anti-pattern-review-v1.md)
- [imports-manifest-v1.yaml](../imports-manifest-v1.yaml)
- V0 baseline at `36d1952`

---

## 1. What was built

Eight V1 axiom obligations (A1..A8) and five V1 SHACL shape contracts (S-V1-1..S-V1-5) implemented. Full implementation report in [`axiom-plan-v1.md`](axiom-plan-v1.md). Build sequence + tool gate results in [`architect-build-log-v1.md`](architect-build-log-v1.md). KGCL log: [`../energy-intel-changes-v1.kgcl`](../energy-intel-changes-v1.kgcl).

| Obligation | Status | Evidence |
|---|---|---|
| A1 — `ei:EnergyExpertRole` | Implemented | `modules/agent.ttl:48-54` |
| A2 — `ei:Expert` EquivalentTo | Implemented | `modules/agent.ttl:11-18`; V0 SubClassOf foaf:Person dropped; disjointWith Organization preserved |
| A3 — 3-way role disjointness | Implemented | `modules/agent.ttl:62-63` |
| A4 — `ei:canonicalUnit` | Implemented | `modules/measurement.ttl` |
| A5 — CMC max-1 canonicalUnit restriction | Implemented | `modules/measurement.ttl` |
| A6 — `ei:authoredBy` range -> foaf:Person + Post restriction update | Implemented | `modules/media.ttl` |
| A7 — `ei:spokenBy` range -> foaf:Person | Implemented | `modules/media.ttl` |
| A8 — 3 V1 imports + catalog + V1 versionIRI | Implemented | `energy-intel.ttl`; `catalog-v001.xml` |
| S-V1-1 — canonicalUnit in QUDT subset | Implemented | `shapes/energy-intel-shapes.ttl` (sh:in over 25 IRIs) |
| S-V1-2 — resolvability gate (Warning) | Implemented | `shapes/...` (severity at NodeShape) |
| S-V1-3 — Post.authoredBy bears EnergyExpertRole | Implemented | `shapes/...` (SPARQL constraint) |
| S-V1-4 — PodcastSegment.spokenBy bears EnergyExpertRole (Warning) | Implemented | `shapes/...` (SPARQL constraint) |
| S-V1-5 — aboutTechnology in skos:Concept OR OEO subtree | Implemented | `shapes/...` (SPARQL constraint with subClassOf*/broader* walk) |

---

## 2. How to re-run all gates

The validator should re-run every gate the architect ran, in this order. All commands are run from `/Users/pooks/Dev/ontology_skill`.

### 2.1 Regenerate V1 imports (idempotent)

```bash
uv run python ontologies/energy-intel/scripts/build_v1_imports.py
```

Phases: BFO+RO strip + reannotate ontology IRIs + QUDT slice + merge + HermiT gate. Final stdout line is `V1 imports build COMPLETE — all gates green.`. Logs: `validation/v1-bfo-remediation/`.

### 2.2 Regenerate the four module TTLs + top-level

```bash
uv run python ontologies/energy-intel/scripts/build_modules.py
```

Output: `modules/agent.ttl`, `modules/media.ttl`, `modules/measurement.ttl`, `modules/data.ttl`, `energy-intel.ttl`.

### 2.3 Regenerate SHACL shapes

```bash
uv run python ontologies/energy-intel/scripts/build_shapes.py
```

Output: `shapes/energy-intel-shapes.ttl` (172 triples; 9 NodeShapes; V0 + V1 prefix-decl ontologies).

### 2.4 Regenerate fixtures + verify SPARQL contracts

```bash
uv run python ontologies/energy-intel/scripts/build_fixtures.py
```

Should print 19/19 OK rows.

### 2.5 Run robot reason / report gates per module + top-level

```bash
uv run python ontologies/energy-intel/scripts/run_gates.py
```

Expected: every module status `ok`; merge_exit=0; reason_exit=0.

### 2.6 Apply allow-list filter to top-level report

```bash
uv run python ontologies/energy-intel/scripts/apply_report_allowlist.py
```

Expected stdout:
```
allow-listed ERRORs suppressed: 687
rows passing through filter:   649
project-origin ERRORs:         0
```

Exit 0. **0 project-origin ERRORs is the architect-to-validator gate.**

### 2.7 OWL 2 DL profile validation (top-level merged)

```bash
.local/bin/robot validate-profile --profile DL \
  --input ontologies/energy-intel/validation/merged-top-level.ttl \
  --output ontologies/energy-intel/validation/v1/profile-validate-dl.txt
```

Expected: 41 distinct punned IRIs, all upstream (no `https://w3id.org/energy-intel/...` IRIs in the punned-IRI list). 743 violation lines total (ROBOT counts each occurrence; the 41 distinct names is the architect-asserted invariant).

### 2.8 pyshacl gate

```bash
uv run python ontologies/energy-intel/scripts/run_shacl_gate.py
```

Expected:
- 19/19 fixtures conform with 0 Violations.
- cq-008 has 1 Warning (S-V1-2 firing on bare CMC by design).
- Summary written to `validation/shacl-summary.json`.

### 2.9 pytest CQ acceptance suite

```bash
uv run pytest ontologies/energy-intel/tests/test_ontology.py -v
```

Expected: **19 passed.**

### 2.10 Ruff lint + format

```bash
uv run ruff check ontologies/energy-intel/scripts/
uv run ruff format --check ontologies/energy-intel/scripts/
```

Both clean.

---

## 3. Final gate state (V1 architect handoff)

| Gate | Status | Evidence |
|---|---|---|
| OWL 2 DL profile (project-namespaced punning = 0) | PASS | `validation/v1/profile-validate-dl.txt` |
| HermiT reasoner (per module + top-level) | PASS (exit 0; 0 unsat) | `validation/v1/reason-*.log`; `validation/v1/reasoned-top-level.ttl` |
| ROBOT report (project-origin ERRORs = 0) | PASS | `validation/v1/report-project-errors.tsv` (0 rows) |
| pyshacl (19/19 conform, 0 Violations) | PASS | `validation/v1/shacl-summary.json` |
| pytest CQ suite (19/19) | PASS | `validation/v1/pytest-cq-suite.log` |
| Ruff lint / format | clean | n/a |

---

## 4. V1 import manifest state

The V1 architect did NOT modify scout's V1 imports. The three V1 import files are unchanged from scout's output:
- `imports/oeo-technology-subset-fixed.ttl` (BFO+RO-stripped + V1 architect re-annotated ontology IRI; the structural axioms inside are still scout's output)
- `imports/oeo-carrier-subset-fixed.ttl` (same)
- `imports/qudt-units-subset.ttl` (unchanged)

The architect's `reannotate_ontology_iri` step appended to `build_v1_imports.py` only rewrites the ontology header IRI (a few triples on the owl:Ontology node) — no structural change to the OWL axioms inside.

V1 imports manifest: [`../imports-manifest-v1.yaml`](../imports-manifest-v1.yaml). Three entries with `v1_change_type: status_changed`. V0 imports (BFO, IAO, DCAT, PROV, SKOS, FOAF, dcterms, hand-seeded SKOS schemes) carry forward unchanged.

---

## 5. Open watches for validator + curator

### 5.1 OEO subset is upward-only

The V0 BOT extract pulls upward parent path of the seed terms. `OEO_00020267` (energy technology), `OEO_00000011` (energy converting component), `OEO_00020039` (energy carrier) all have **0 descendants** in the subset. The CQ-015 / CQ-019 SPARQL property paths therefore match only when CMCs tag directly with one of these root IRIs (the empty-path case).

**Curator action:** evaluate whether to re-extract the OEO subset with TOP+BOT (drag descendants), or extend the seed list with concrete technologies (solar-PV, onshore-wind, etc.) — see `imports-manifest-v1.yaml § open_questions V1-IM-Q1`.

### 5.2 Two upstream-origin bug classes flagged in this iteration

1. **OEO prefix bug (V0-class):** Conceptualizer flagged the V1 CQ-015 / CQ-019 SPARQL files used `http://openenergy-platform.org/ontology/oeo/` (HTTP + hyphen). System reminder confirms this was already corrected before architect started; verified prefix is `https://openenergyplatform.org/ontology/oeo/`.
2. **`unit:GW` IRI bug (V1-class):** V0 imports manifest seeds (`unit:GW`, `unit:MW`, `unit:TW-HR`) do not exist in QUDT 2.1; correct names use SI-prefix-as-word (`unit:GigaW`, `unit:MegaW`, `unit:TeraW-HR`). `imports-manifest-v1.yaml` already corrected this in the seed list. The cq-016 SPARQL had not yet been corrected — V1 architect updated it to use `unit:GigaW`.

### 5.3 V0 fixtures additively migrated for SHACL S-V1-3 conformance

V0 fixtures previously asserted `?expert a ei:Expert` only. Under V1's `Expert ≡ Person ⊓ ∃bfo:0000053.EnergyExpertRole`, the role-bearer triples are entailed by classification — but **not** under pyshacl's `inference="rdfs"` regime. To keep S-V1-3 conformant on V0 fixtures, `_post()` was extended additively with:
```turtle
?expert a foaf:Person ; bfo:0000053 ?role .
?role a ei:EnergyExpertRole .
```

V0 SPARQL CQ tests still pass because `?expert a ei:Expert` is preserved.

If validator wants to test the EquivalentTo classification path explicitly (i.e., assert `?expert a ei:Expert` only and verify the reasoner classifies), they should swap pyshacl for `pyshacl --inference owlrl` or run a HermiT pre-pass + pyshacl on the materialised closure.

### 5.4 Punning at TBox stage stays clean (CQ-Q-3)

Conceptualizer's CQ-Q-3 prediction held: V1 brings no new punning beyond V0's upstream punning. HermiT exits 0 on the merged closure. Validator should re-confirm with their own HermiT run; the architect's evidence is in `validation/v1/reasoned-top-level.ttl` (1.3 MB).

The ABox-stage punning watch (V2+) is not yet relevant — V1 ships TBox-only.

### 5.5 11 new allow-list rows added with rationale

`validation/report-allowlist.tsv` grew from 40 rows to 51 rows. Every new row has rule + subject_prefix + justification + reviewer + reviewed_at. Validator should audit the rationale of each row (none of them silence project-origin issues; all are upstream rule hits from the V1 imports).

---

## 6. Files validator should review (in priority order)

1. `docs/axiom-plan-v1.md` — 8 axiom obligations + 5 shapes implementation report
2. `docs/architect-build-log-v1.md` — order of operations + tool gate results per step
3. `energy-intel-changes-v1.kgcl` — abstract change spec
4. `validation/v1/` — all raw evidence files
5. `validation/report-allowlist.tsv` — V1 additions (rows 41-51)
6. Modified build scripts: `scripts/build_modules.py`, `scripts/build_shapes.py`, `scripts/build_fixtures.py`, `scripts/build_v1_imports.py`, `scripts/run_shacl_gate.py`
7. Generated TTL: `modules/*.ttl`, `shapes/energy-intel-shapes.ttl`, `energy-intel.ttl`, `tests/fixtures/cq-*.ttl`
8. Updated tests: `tests/test_ontology.py`, `tests/cq-test-manifest.yaml`, `tests/cq-016.sparql`

---

## 7. Loopback paths

| Issue validator might find | Loopback to | Reason |
|---|---|---|
| HermiT regression in validator's environment | `ontology-architect` | Re-check helper functions; verify rdflib Collection / BNode bookkeeping |
| Unexpected upstream-origin ERROR not in allow-list | `ontology-architect` | Add a justified row; or escalate to scout if the import dragged in unexpected upstream content |
| pyshacl regression (a fixture starts producing Violations) | `ontology-architect` | Trace to fixture-builder vs shape-builder; usually a missing role-bearer triple in the V0 fixture migration |
| Punning regression (project-namespaced IRI shows up) | `ontology-conceptualizer` | New TBox punning would re-trigger CQ-Q-3 and potentially require fallback (re-materialise OEO as plain SKOS) |
| OEO subset is too small (validator finds a missing technology class needed for a real-world fixture) | `ontology-scout` | Extend seed list in `build_v1_imports.py:QUDT_UNIT_SEEDS` and OEO seeds — full TOP+BOT extract may be needed |
| QUDT subset is too small (a unit needed isn't there) | `ontology-scout` | Extend `QUDT_UNIT_SEEDS` and re-run `build_v1_imports.py` |

Depth > 3 escalates per `_shared/iteration-loopbacks.md`.

---

## 8. Confidence note

Everything above is derived from V1 inputs frozen on 2026-04-27 (requirements approval, scout output, conceptualizer V1 deliverables) plus the V1 architect's build outputs landed 2026-04-27. Reasoner, report, pyshacl, and pytest gates ran in this single sitting and re-ran clean on idempotency check.

Validator can proceed.
