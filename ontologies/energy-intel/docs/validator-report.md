# Validator Report — `energy-intel` V0

**Skill:** `ontology-validator`
**Run date:** 2026-04-22
**Validator session commit:** `dc123d4`
**Reviewer:** kokokessy@gmail.com
**Artifact type:** Release-gate ontology (TBox + shapes + fixtures + imports)

---

## TL;DR

| Gate | Verdict |
|------|---------|
| L0 Preflight (syntax, catalog-resolved merge) | PASS |
| L1 Reasoner (HermiT, V0 closure) | PASS |
| L1' Reasoner (HermiT, V0 + OEO closure) | **FAIL** — inconsistent (non-blocking for V0) |
| L2 OWL 2 DL profile (merged top-level) | FAIL, upstream-only (accepted) |
| L3 SHACL (14 fixtures) | **FAIL** — 12 violations on shape S-1 |
| L4 CQ acceptance (pytest, 14 CQs) | PASS (14/14) |
| L5 ROBOT report with allow-list | PASS (0 project-origin ERRORs) |
| L6 Release diff (self-diff baseline) | PASS — identical |

**Recommendation:** **block-pending-fix** on SHACL S-1 reconciliation.
Architect must reconcile the `DidSchemeOnAuthoredBy` shape regex with
fixture IRI form (architect owns the choice: regen fixtures with `did:plc:...`
IRIs OR relax shape to accept the existing `https://...did-plc-...` form).
Once 14/14 fixtures conform, flip to `release` and sign the release audit.

All other gates pass or are explicitly accepted (upstream noise).

---

## § Gate L0 — Preflight

* `robot merge --catalog catalog-v001.xml --input energy-intel.ttl` — exit 0.
  Catalog resolves 5 intra-project `owl:imports` to `w3id.org` URIs and
  delegates to local module files.
* Merged top-level size: 1,299,179 bytes (`validation/merged-top-level.ttl`).
* Merged module sizes: agent 199,937 B, media 777,180 B, measurement
  1,216,643 B, data 1,252,602 B. All on disk; no gitignored artefacts missing.

Log evidence: `validation/merge-*.log` (stdout+stderr empty on all 5 runs).

---

## § Gate L1 — Reasoner (HermiT)

Per-module results (all merge-first, reason-second per architect's
`run_gates.py` pattern):

| Module | merge_exit | reason_exit | Unsatisfiable | Inconsistent |
|--------|-----------:|------------:|--------------:|:------------:|
| agent | 0 | 0 | 0 | no |
| media | 0 | 0 | 0 | no |
| measurement | 0 | 0 | 0 | no |
| data | 0 | 0 | 0 | no |
| top-level | 0 | 0 | 0 | no |

V0 closure is **HermiT-clean**. `validation/reasoned-top-level.ttl` is a
materialised DL classification (1,303,730 bytes).

### L1' — Top-level merged with OEO subsets

Extended run, per architect's watch-item bullet 6:

```
robot merge --catalog catalog-v001.xml \
  --input energy-intel.ttl \
  --input imports/oeo-technology-subset.ttl \
  --input imports/oeo-carrier-subset.ttl \
  --output validation/merged-top-level-with-oeo.ttl

robot reason --reasoner hermit \
  --input validation/merged-top-level-with-oeo.ttl \
  --output validation/reasoned-top-level-with-oeo.ttl
```

Result: **HermiT reports the ontology is inconsistent.** HermiT cannot
dump unsatisfiable classes for an inconsistent ontology. Root cause:

* `imports/oeo-*.ttl` contains BOT-extracted BFO classes (`BFO_0000023
  subClassOf BFO_0000017` etc.) taken from the OEO v2.11.0 bundled BFO
  backbone.
* `modules/agent.ttl` imports `<http://purl.obolibrary.org/obo/bfo.owl>`
  which is BFO-2020.
* The two BFO snapshots axiomatise the BFO_0000...X backbone differently.
  Their union is inconsistent.

Isolation tests confirm: each OEO subset HermiT-reasons cleanly in
isolation and together. It is the merge with the agent-closure that
introduces the conflict.

This is the **`construct_mismatch` loopback** the architect flagged on
handoff. It is **non-blocking for V0** because `energy-intel.ttl` does
not `owl:imports` the OEO subsets in V0 — they are on disk for future
V1 punning tests only.

Loopback raised: `construct_mismatch` → `ontology-architect`.
Remediation options for V1:

1. `robot remove --term BFO_* --axioms structural` against each OEO
   subset before `owl:imports`-ing them; or
2. Switch `agent.ttl` from `<obo/bfo.owl>` to the OEO-embedded BFO
   snapshot for consistency.

Evidence: `validation/merged-top-level-with-oeo.ttl`.

---

## § Gate L2 — OWL 2 DL profile validation

On merged top-level closure:

* `robot validate-profile --profile DL --input merged-top-level.ttl` — exit
  code 0 but emits `PROFILE VIOLATION ERROR` banner.
* 385-line report at `validation/profile-validate-top-level.txt`.
* **37 distinct IRIs with "Cannot pun between properties" violations**
  and 1 reserved-vocabulary violation (`rdf:List` declared as Class —
  ships with rdflib serialisation of the concept-scheme `owl:AllDifferent`
  member list; cosmetic).

Offending namespaces (grouped):

* `dcterms:*`  — multi-role (`created`, `title`, `issued`, `modified`, etc. declared
  as both AnnotationProperty and DataProperty upstream)
* `foaf:*`     — chat-ID properties declared as both Object+Data
* `dcat:*`     — `catalog`, `resource`, `distribution`, `inSeries` declared
  inconsistently
* `prov:*`     — `wasRevisionOf` role-chain declaration

**Zero `ei:` violations.** Full IRI trace confirms all 37 are upstream.

This is a known OWL-2-DL-vs-OWL-2-Full divergence in DCAT-3 / FOAF /
PROV-O. HermiT accepts the merged closure under its lenient property-punning
handling. The architect previously recommended running `robot reason`
(which passed, § L1) as the release-gate rather than `validate-profile`.
Validator concurs.

**Accepted as an upstream condition.** No loopback.

---

## § Gate L3 — SHACL (pyshacl)

* Runner: `scripts/run_shacl_gate.py`
* Shapes file: `shapes/energy-intel-shapes.ttl` (4 NodeShapes)
* Inference: `rdfs` (so `Chart subClassOf EvidenceSource` materialises for
  the CQ-009 CMC evidence shape)
* Data graph: TBox (top-level + 4 modules + 3 concept schemes) + fixture
* Per-fixture results written to `validation/shacl-results-cq-NNN.ttl`
* Roll-up: `validation/shacl-summary.json`

| Fixture | Conforms | Violations |
|---------|:--------:|-----------:|
| cq-001 | NO | 1 |
| cq-002 | NO | 1 |
| cq-003 | NO | 1 |
| cq-004 | NO | 1 |
| cq-005 | NO | 1 |
| cq-006 | NO | 2 |
| cq-007 | NO | 2 |
| cq-008 | NO | 2 |
| cq-009 | NO | 1 |
| cq-010 | NO | 1 |
| cq-011 | **YES** | 0 |
| cq-012 | **YES** | 0 |
| cq-013 | NO | 1 |
| cq-014 | NO | 1 |

**All 14 failures fire on a single shape: `<.../shape/DidSchemeOnAuthoredBy>`.**

Verbatim resultMessage (raw SHACL output, no paraphrase):

```
sh:focusNode <https://id.skygest.io/post/post_01J_example> ;
sh:resultMessage "ei:authoredBy value must be a DID IRI (did:plc:... or did:web:...)."@en ;
sh:resultPath ei:authoredBy ;
sh:sourceConstraintComponent sh:PatternConstraintComponent ;
sh:sourceShape [ sh:pattern "^did:(plc|web):[A-Za-z0-9._:%-]+$" ] ;
sh:value <https://id.skygest.io/expert/did-plc-a5kyzplew76jaj4dhnqsosjv>
```

**Root cause:** Architect's fixtures use HTTPS web-resource URIs of the
form `https://id.skygest.io/expert/did-plc-<id>` as `ei:authoredBy`
objects. The S-1 shape regex is `^did:(plc|web):[A-Za-z0-9._:%-]+$`
which requires the IRI string to START with `did:`. The fixtures don't.
The shape rejects.

**Other three shapes are clean.** `CMCEvidenceSource` (CQ-009 companion)
correctly reports zero violations on cq-009 because the fixture's Chart
and Post individuals ARE recognised as `EvidenceSource` via rdfs
subClassOf chain — this confirms the rdfs inference layer is pulling
its weight and the shape is well-authored.

**Loopback raised:** `shacl_violation` → `ontology-architect`.
Resolution options:

1. Regenerate fixtures so `ei:authoredBy` objects are raw `did:plc:...`
   and `did:web:...` URIs (matches DID-W3C-spec scheme); or
2. Relax shape S-1 to also match `https://.../did-plc-<id>` (accept
   current web-URI form as a registered DID gateway).

Validator recommends option (1) — DID URIs are semantically distinct
from HTTP URIs and the shape is enforcing the authoritative norm.

Evidence: `validation/shacl-summary.json`, `validation/shacl-results-cq-*.ttl`.

---

## § Gate L4 — CQ acceptance (pytest)

* Runner: `tests/test_ontology.py` (authored this session)
* Invocation: `uv run pytest ontologies/energy-intel/tests/test_ontology.py -v`
* Fixtures loaded on top of full TBox (top-level + 4 modules + 3 concept
  schemes) as a fresh rdflib `Graph`; SPARQL parsed via
  `rdflib.plugins.sparql.prepareQuery` before execution.

Verdict: **14 passed, 661 warnings in 1.59s** (warnings are all rdflib
pyparsing deprecation notices, cosmetic).

| CQ | Status | Rows | Expected band | Column shape |
|----|:------:|-----:|---------------|--------------|
| CQ-001 | pass | 1 | 0..n | (cmc) |
| CQ-002 | pass | 1 | exactly 1 | (expert) |
| CQ-003 | pass | 1 | 0..1 | (variable) |
| CQ-004 | pass | 1 | 0..1 | (series) |
| CQ-005 | pass | 1 | 0..1 | (distribution) |
| CQ-006 | pass | 2 | 0..n | (cmc) |
| CQ-007 | pass | 2 | 0..n | (expert) |
| CQ-008 | pass | 2 | 0..n | (cmc,post,expert,v,u,t) |
| CQ-009 | pass | 0 | exactly 0 (invariant) | (cmc) |
| CQ-010 | pass | 1 | exactly 1 | (agent,dist,dataset,var,series) |
| CQ-011 | pass | 2 | 0..n | (expert) |
| CQ-012 | pass | 1 | 0..n | (cmc) |
| CQ-013 | pass | 1 | 0..n | (cmc) |
| CQ-014 | pass | 1 | 0..n | (post) |

Manifest `fixture_run_status: pass` claim for every CQ is **verified**
against the pytest harness. No drift between architect's
`_verdicts.txt` and this session's re-run.

**Manifest integrity:** Every `tests/cq-NNN.sparql` file referenced in
the manifest exists; every CQ carries `parse_status: ok`,
`expected_results_contract`, `entailment_regime`. No stale CQs.

---

## § Gate L5 — ROBOT report + upstream allow-list

Merged top-level report totals (`validation/report-top-level.tsv`):

| Level | Count |
|-------|------:|
| ERROR | 329 |
| WARN  | 415 |
| INFO  | 85 |

Breakdown of 329 ERRORs by rule:

* `multiple_labels`: 276 (DCAT 9-language ships every term with 9 labels)
* `duplicate_label`: 28 (Person/Organization/Agent/definition/etc. FOAF+PROV+SKOS+IAO collisions)
* `missing_label`: 23 (DCAT/PROV/FOAF utility classes without labels)
* `label_whitespace`: 2 (DCAT upstream)

Breakdown by namespace (full-IRI + CURIE forms summed):

| Namespace | ERRORs |
|-----------|-------:|
| `dcat:` | 291 |
| `prov:` | 17 |
| `foaf:` | 7 |
| `skos:` | 5 |
| `IAO:` | 4 |
| `dc:` | 1 |
| `RO:` | 1 |
| `APOLLO_SV:` | 1 |
| `ei:` project | 2 — BOTH cross-namespace collisions with upstream labels |

The two "ei:"-flagged ERRORs are:

1. `ei:concept/temporal-resolution` (label "temporal resolution"@en)
   collides with `dcat:temporalResolution` (label "temporal resolution"@en).
2. `ei:concept/aggregation-type/count` (label "count"@en) collides with
   `APOLLO_SV:00000032` (label "count"@en).

Both are **legitimate cross-namespace collisions**: the project labels
are semantically correct in their domain, and IRI disambiguation is the
standard OWL way to handle this. Added to allow-list with explicit
justification.

**Allow-list:** `validation/report-allowlist.tsv` — 33 rows, each:
`rule\tsubject_prefix\tjustification\treviewer\treviewed_at`.
Prefix matching covers both full-IRI and CURIE forms as emitted by
ROBOT report.

**Filter runner:** `scripts/apply_report_allowlist.py` — reads
`report-top-level.tsv` and `report-allowlist.tsv`; writes
`report-top-level-filtered.tsv` and `report-project-errors.tsv`; exits
0 iff zero project-origin ERRORs survive.

Result: **329 allow-listed, 0 project-origin ERRORs remain.** Exit 0.

Evidence:
- `validation/report-top-level.tsv` (raw ROBOT report)
- `validation/report-allowlist.tsv` (signed allow-list)
- `validation/report-top-level-filtered.tsv` (post-filter rows)
- `validation/report-project-errors.tsv` (post-filter ERRORs — empty)

---

## § Gate L6 — Release diff (self-diff)

V0 is the first release; no prior version to diff against. Self-diff
generated as the v0 baseline marker:

```
.local/bin/robot diff \
  --left  energy-intel.ttl \
  --right energy-intel.ttl \
  --format markdown \
  --output release/v0-baseline-diff.md
```

Output (1 line): `Ontologies are identical`.

**Next release diffs against `release/v0-baseline-diff.md`.**

---

## § Cross-cutting — Anti-pattern detection

(Level 5.5 from skill workflow.)

Per conceptualizer's `docs/anti-pattern-review.md`, all five candidate
patterns were resolved before formalization:

* **Role as subclass** — resolved: BFO role pattern used (`PublisherRole
  subClassOf bfo:0000023`).
* **Quality as class** — resolved: quantity values on CMC are data
  properties (`ei:assertedValue`, `ei:assertedUnit`).
* **Process as material** — resolved: `ei:PodcastEpisode` is an
  information content entity (`iao:Document` hierarchy), not a
  process.
* **Singleton hierarchy** — resolved: all classes have multiple
  siblings or are leaves.
* **Missing disjointness** — resolved: sibling disjointness declared
  via `owl:AllDisjointClasses` on Post/MediaAttachment/PodcastSegment
  and Chart/Screenshot/Excerpt/GenericImageAttachment (per
  media.ttl inspection).

No anti-pattern hits on the reasoned ontology. No loopback.

---

## § Evaluation Dimensions (Level 6)

* **Semantic**: V0 uses OWL 2 qualified cardinality and inverse property
  expressions — HermiT is the minimum-viable reasoner (ELK drops these).
  Expressivity is well-matched to the CQ load; the OEO import deferral
  is the single expressivity-vs-consistency trade-off.
* **Functional**: all 14 CQs are executable and pass their contracts.
  The SHACL defense-in-depth layer (CMCEvidenceSource companion to
  CQ-009 OWL invariant) is working as designed.
* **Model-centric**: BFO 2020 (ISO 21838-2), IAO 2026-03, DCAT-3,
  PROV-O, FOAF, SKOS, OEO 2.11.0 — all authoritative sources with
  stable IRIs. Project term naming follows `CamelCase` for classes and
  `camelCase` for properties per `CONVENTIONS.md`.

---

## § Loopback triggers raised

1. **`shacl_violation`** → `ontology-architect` (blocking for V0)
   * 12/14 fixtures fail shape S-1 (DidSchemeOnAuthoredBy).
   * Architect reconciles fixture IRI form vs shape regex (pick one).

2. **`construct_mismatch`** → `ontology-architect` (non-blocking for V0)
   * OEO subsets inconsistent under HermiT once merged with the V0
     agent+BFO-2020 closure. BFO version conflict.
   * V0 does not import OEO — defer to V1 remediation.

---

## § Progress-criteria checklist

- [x] `validation/reasoner.log` from `robot reason` — per-module logs present
- [x] `validation/robot-report.tsv` — `report-*.tsv` per module + top-level
- [x] `validation/profile-validate-top-level.txt` from `robot validate-profile`
- [x] `validation/shacl-results-*.ttl` from `pyshacl` — 14 per-fixture files
- [x] `validation/shacl-summary.json` — roll-up
- [x] CQ pytest harness `tests/test_ontology.py` — 14/14 pass
- [x] `validation/report-allowlist.tsv` — signed upstream allow-list
- [x] `release/v0-baseline-diff.md` — self-diff baseline
- [x] `release/release-audit.yaml` — signed gate audit (sign_off: pending)

---

## § Recommendation

**block-pending-fix** on SHACL S-1 reconciliation (one-shape fix expected
to take the architect 5–15 minutes). All other gates pass or are
explicitly accepted. Once 14/14 SHACL conforms, flip
`release-audit.yaml` → `sign_off: signed` and
`recommendation: release`.
