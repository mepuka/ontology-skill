# Release Notes — `energy-intel` v0.3.0

**Release date:** 2026-05-04
**Version IRI:** `https://w3id.org/energy-intel/v2/2026-05-04`
**Predecessor:** v0.2.0 (commit `1d8f9da`, dated 2026-04-27)
**License:** CC-BY-4.0
**Validator recommendation:** release ([release-audit-v2.yaml](release-audit-v2.yaml))
**Curator endorsement:** signed (curator-log-v2.md)
**Sign-off:** signed by kokokessy@gmail.com on 2026-05-04

---

## TL;DR

**V2 ships the editorial extension.** Two net-new classes
(`ei:Narrative`, `ei:NarrativePostMembership`), six net-new object
properties (the editorial graph), three new SKOS schemes
(`argument-pattern`, `narrative-role`, `oeo-topics`), the rebuilt OEO
topic subset (41 seed IRIs, BFO+RO-stripped), and four SHACL editorial
shapes (S-V2-1..S-V2-4). All 30 CQs pass (14 V0 + 5 V1 + 11 V2). HermiT
exit 0 on the merged closure.

**No breaking changes for ABox consumers.** V2 is **strictly additive**
at the project namespace — no `ei:*` term is deleted, deprecated, or
semantically narrowed. The V0/V1 `technology-seeds.ttl` is retired
from `owl:imports` (replaced by `oeo-topics.ttl` as runtime topic
authority); the file is preserved on disk per safety rule #4 and
remains dereferenceable via direct file load. v0.4.0 deprecation cycle
will add `owl:deprecated true` + replacement pointers to each of its 5
SKOS Concepts.

**Non-goal #5 retracted.** The V0 scope.md non-goal "no narrative
modeling in V0/V1" is explicitly retracted in V2 to enable the
editorial extension. See [`docs/scope-v2.md`](../docs/scope-v2.md).

---

## What's new

### Net-new TBox terms (axiom plan A1..A12)

#### Classes (2)

| IRI | Parent | Source axiom |
|---|---|---|
| `ei:Narrative` | `iao:0000310` (Document) | A1 |
| `ei:NarrativePostMembership` | `iao:0000310` (Document) | A2 |

[`modules/editorial.ttl`](../modules/editorial.ttl) declares both. A3
seals pairwise project-disjointness:
`AllDisjointClasses(Narrative, Post, PodcastEpisode, NarrativePostMembership)`.

#### Object properties (6)

| IRI | Domain | Range | Char | Axiom |
|---|---|---|---|---|
| `ei:hasNarrativePostMembership` | `ei:Narrative` | `ei:NarrativePostMembership` | — | A4 |
| `ei:memberPost` | `ei:NarrativePostMembership` | `ei:Post` | Functional | A5 |
| `ei:memberRole` | `ei:NarrativePostMembership` | `skos:Concept` | Functional | A6 |
| `ei:narrativeMentionsExpert` | `ei:Narrative` | `foaf:Person` | — | A9 |
| `ei:narrativeAppliesPattern` | `ei:Narrative` | `skos:Concept` | — | A10 |
| `ei:narrativeAboutTopic` | `ei:Narrative` | `owl:Thing` | — | A11 |

Cardinality restrictions (A7, A8, A12):
- `NarrativePostMembership SubClassOf memberPost qualifiedCardinality 1 Post`
- `NarrativePostMembership SubClassOf memberRole qualifiedCardinality 1 skos:Concept`
- `Narrative SubClassOf narrativeAppliesPattern maxQualifiedCardinality 1 skos:Concept`

The `NarrativePostMembership` reified n-ary relation pattern was chosen
over role-named predicates per source plan §3.3 / multi-agent
BFO/OEO modeling review (avoids the System Blueprint anti-pattern).

### Net-new SHACL contracts (S-V2-1..S-V2-4)

| Shape | Target | Severity | Purpose |
|---|---|---|---|
| `S-V2-1` `NarrativePostMembershipShape` (+ closed-shape `NarrativeUniqueMembershipShape` SPARQL) | `ei:NarrativePostMembership` / `ei:Narrative` | Violation | `memberPost` minCount/maxCount 1 `ei:Post`; `memberRole` minCount/maxCount 1 in `nrole:{lead,supporting,counter,context}`; at-most-one-membership-per-(N,P)-pair |
| `S-V2-2` `NarrativeShape` (sh:sparql) | `ei:Narrative` | Violation | `narrativeAppliesPattern` value MUST be in `ei:concept/argument-pattern` scheme |
| `S-V2-3` `NarrativeShape` (sh:or) | `ei:Narrative` | Violation | `narrativeAboutTopic` value MUST be `owl:Class` OR `skos:Concept` (granularity contract; bare NamedIndividual rejected) |
| `S-V2-4` `NarrativeLeadUniquenessShape` (sh:sparql) | `ei:Narrative` | Warning¹ | At-most-one-lead-membership-per-Narrative |

¹ `pyshacl` mis-renders S-V2-4 severity as `sh:Violation` due to a
known propagation quirk when `sh:severity` is nested inside
`sh:SPARQLConstraint` (V2-CUR-1, non-blocking). Shape fires correctly.

[Shapes file](../shapes/editorial.ttl) — 4 NodeShapes total (4 V2 +
9 V0/V1 in `shapes/energy-intel-shapes.ttl`).

### Net-new SKOS ConceptSchemes (3 explicit + 2 derived)

| Scheme IRI | Concepts | Source |
|---|---:|---|
| `ei:concept/argument-pattern` | 7 | [`modules/concept-schemes/argument-pattern.ttl`](../modules/concept-schemes/argument-pattern.ttl) |
| `ei:concept/narrative-role` | 4 | [`modules/concept-schemes/narrative-role.ttl`](../modules/concept-schemes/narrative-role.ttl) |
| `ei:concept/oeo-topic` (split) | 41 (OEO IRIs via punning) | [`modules/concept-schemes/oeo-topics.ttl`](../modules/concept-schemes/oeo-topics.ttl) |
| `ei:concept/editorial-supplement` (split) | 19 (project supplements) | same |
| `ei:concept/topic` (aggregator) | 60 (41 + 19) | same |

The split + aggregator scheme structure was chosen so that consumers
filtering on "OEO-only" or "editorial-only" topics get clean signals
while the aggregator backs `ei:narrativeAboutTopic` enumeration.

### Net-new imports

| Import IRI | File | Triples |
|---|---|---:|
| [`https://w3id.org/energy-intel/imports/oeo-topic-subset`](../imports/oeo-topic-subset.ttl) | imports/oeo-topic-subset.ttl | 7,729 |

Source: `imports/oeo-full.owl` (OEO 2.11.0). Method:
`robot extract --method BOT` against 41 seeds in
`imports/oeo-topic-seeds.txt`, then `robot remove` with
`imports/upper-axiom-leak-terms.txt` (57 V1 terms) +
`imports/v2-extra-leak-terms.txt` (6 V2 BFO terms missed by V1 strip).
Granularity verifier in `extract_oeo_topic_subset.py` confirms all 41
seeds remain `owl:Class` post-strip and zero BFO references survive.

### Net-new CQs (11; CQ-N1..N8 + CQ-T1..T3)

All 11 land with passing fixtures and `expected_results_contract`:

| CQ | Contract |
|---|---|
| CQ-N1..N8 | Narrative + NarrativePostMembership shape and instance contracts |
| CQ-T1..T3 | OEO topic punning + granularity + supplement coverage contracts |

[Test manifest](../tests/cq-test-manifest.yaml) — 30 entries total
(14 V0 + 5 V1 + 11 V2).

### Imports retired from owl:imports closure

| Module | Disposition |
|---|---|
| `modules/concept-schemes/technology-seeds.ttl` | Retired from `owl:imports`; **file preserved on disk** per safety rule #4. Replaced by `oeo-topics.ttl` as runtime topic authority. v0.4.0 deprecation cycle: add `owl:deprecated true` + `dcterms:isReplacedBy oeo:OEO_xxx` to each of its 5 SKOS Concepts (V2-CUR-4). |

V0/V1 fixtures (`cq-013`, `cq-015`) still bind via direct file load
through `tests/test_ontology.py:TBOX_FILES`; no test regression.

---

## V1 → V2 migration analysis

### For ABox consumers (no breaking changes)

V2 introduces new TBox classes / properties / schemes additively. No
V1 axiom is removed; no `ei:*` term is renamed or deleted. Existing
ABox triples continue to type-check unchanged.

### For ontology editors

If you maintain a downstream ontology that imports `energy-intel`:

1. Update your `owl:imports` IRI from
   `https://w3id.org/energy-intel/v1/2026-04-27` to
   `https://w3id.org/energy-intel/v2/2026-05-04`.
2. If you use `dcterms:isVersionOf <https://w3id.org/energy-intel/>`,
   no change.
3. If you bind to specific module versionIRIs, update each per
   `imports-manifest-v2.yaml` § module_iri rows.

### For Skygest Cloudflare KG (consumer)

1. Repoint `ontologyRoot` in your Cloudflare DSL from
   `https://w3id.org/energy-intel/v1/2026-04-27` to
   `https://w3id.org/energy-intel/v2/2026-05-04` (after PURL refresh).
2. Re-run codegen. Editorial pipeline now first-class:
   - `?n a ei:Narrative ; ei:hasNarrativePostMembership ?m ; ei:narrativeAboutTopic ?t .`
   - `?m ei:memberPost ?p ; ei:memberRole nrole:lead .`
   - SHACL S-V2-1 ensures membership shape; S-V2-2 ensures pattern is
     in scheme; S-V2-3 ensures topic granularity (class or concept).
3. The 5 retired technology-seeds concepts (`solar`, `solar-pv`,
   `wind`, `onshore-wind`, `offshore-wind`) remain dereferenceable via
   `technology-seeds.ttl` direct load. Update KG queries to bind
   `ei:concept/oeo-topic` or `ei:concept/topic` aggregator scheme
   (recommended) or `oeo:OEO_xxx` IRIs (canonical).

### Migration table

| Consumer pattern | V1 behaviour | V2 behaviour | Migration |
|---|---|---|---|
| `?cmc ei:authoredBy ?p` | works | works | none |
| `?cmc ei:canonicalUnit ?u` | works | works | none |
| `?n a ei:Narrative` | not admissible | first-class | optional adopt |
| Direct-load `technology-seeds.ttl` for `ei:concept/solar` etc. | works | works | none (still on disk) |
| `?cmc ei:aboutTechnology oeo:OEO_xxx` | works | works | none (V1 imports preserved) |

---

## V1 loopback closures (V1-CUR-* disposition)

| V1 carry-forward | V2 status | Evidence |
|---|---|---|
| V1-CUR-1 OEO subset upward-only | PARTIALLY ADDRESSED — V2's `oeo-topic-subset` rebuilt with 41 seed IRIs (vs V1's narrower technology+carrier seeds). Subset still upward-only (BOT extract) but now covers policy/market/climate axes that CQ-N4/T1/T3 exercise. Full TOP+BOT extension remains a v0.4.0 candidate. | `imports/oeo-topic-seeds.txt` (41 seeds); `imports-manifest-v2.yaml` |
| V1-CUR-2 validation-waivers.yaml | CLOSED in v0.2.0 | `docs/validation-waivers.yaml` |
| V1-CUR-3 ABox-stage punning watch | CLOSED at TBox+module level — V2 closure (top-level + editorial + oeo-topics + oeo-topic-subset) HermiT-clean (exit 0). First ABox-style fixtures (CQ-N4, CQ-T1, cq-editorial-granularity) bind `oeo:OEO_xxx` with HermiT-clean closure. Live ABox runtime ingestion is downstream codegen scope. | `validation/v2/validator-rerun/reason/hermit.log` (empty); `tests/fixtures/cq-editorial-{N4,T1,granularity}.ttl` |
| V1-CUR-4 QUDT unit naming bug | UNCHANGED — V1 fix in place; V2 inherits without regression. | `tests/cq-016.sparql` (unchanged) |
| V1-CUR-5 Allow-list size | HELD STEADY at 49 rows; V2 added 0. | `validation/report-allowlist.tsv` |
| V1-CUR-6 DL profile-validate advisory | UNCHANGED — V2 reproduces V1's 41 distinct upstream-only punned IRIs. Project policy stands. | `validation/v2/validator-rerun/profile/profile-validate-dl.txt` |

---

## V2 residual concerns (V2-CUR-* tracking)

All non-blocking; tracked for v0.4.0:

| ID | Severity | Decision | Owner |
|---|---|---|---|
| V2-CUR-1 pyshacl S-V2-4 severity rendering | info | accept-as-known-issue | architect (v0.4.0) |
| V2-CUR-2 fold v2-extra-leak-terms.txt | info | defer | curator (v0.4.0) |
| V2-CUR-3 DL profile-validate stays advisory | info | documented-and-accepted | curator (ongoing) |
| V2-CUR-4 deprecate technology-seeds concepts | info | defer | curator (v0.4.0) |
| V2-CUR-5 allow-list size monitor | info | track-no-action | curator (ongoing) |
| V2-CUR-6 promote negative-case fixtures | info | defer | architect (v0.4.0) |

Full dispositions in [`release-audit-v2.yaml § curator_endorsement.residual_items_disposition`](release-audit-v2.yaml).

---

## Validation summary

All 11 validator gates pass on independent re-run + curator
re-verification. Cite paths from
[`docs/validator-report-v2.md`](../docs/validator-report-v2.md):

| Gate | Verdict | Evidence |
|---|---|---|
| L0 syntax / catalog merge | PASS | `validation/v2/validator-rerun/preflight/` |
| L1 DL profile-validate | WARN-accepted, upstream-only | 41 distinct upstream-only punned IRIs; 0 project-origin |
| L2 HermiT (top-level merged closure with V2 imports) | PASS, exit 0, 0 unsat | `validation/v2/validator-rerun/reason/hermit.log` (empty) |
| L3 ROBOT report + allow-list | PASS, 0 project-origin ERRORs | `validation/v2/validator-rerun/report/report-project-errors.tsv` (header only) |
| L3.5 pyshacl (11 V2 fixtures × 4 shapes) | PASS, 11/11, 0 Violations | `validation/v2/validator-rerun/shacl/shacl-summary.json` |
| L3.5 negative-case probe (defense-in-depth) | PASS w/ V2-CUR-1 note | `validation/v2/validator-rerun/negative-shacl/` |
| L4 CQ pytest | PASS, 30/30 (14 V0 + 5 V1 + 11 V2) | `validation/v2/validator-rerun/cqs/pytest-cq-suite.log` |
| L4.5 CQ manifest integrity | PASS, 30/30 entries clean | scripted audit |
| L5 coverage metrics | PASS, 23 ei: classes, 100% label/def, 0 orphans | `validation/v2/validator-rerun/coverage/metrics.json` |
| L5.5 anti-patterns | PASS, V1-CUR-3 closed at TBox stage | inline § L5.5 |
| L7 diff vs V1 | PASS, categorized | [`v2-diff-vs-v1.md`](v2-diff-vs-v1.md) |

`validate-profile DL` is treated as **advisory**; HermiT exit code is
the release-gate. See workspace memory `reference_robot_dl_profile_check.md`.

---

## Diff at a glance (vs V1)

[`release/v2-diff-vs-v1.md`](v2-diff-vs-v1.md) is the curator-categorized
digest of the full `robot diff` output (12,748 raw lines, mostly
upstream LatexString re-serialization noise).

| Bucket | V1 | V2 | Net |
|---|---:|---:|---:|
| `ei:` Classes | 21 | 23 | +2 |
| `ei:` Properties | 28 | 34 | +6 |
| `ei:` ConceptSchemes (in closure) | 3 | 7 | +5, -1 |
| `ei:` SKOS Concepts | 15 | 40 | +30, -5 |
| SHACL NodeShapes | 9 | 13 | +4 |
| OEO punned `skos:Concept` (in closure) | 0 | 41 | +41 |

---

## Reproducibility

V2 build is fully reproducible. Curator re-ran:

```bash
uv run python ontologies/energy-intel/scripts/extract_oeo_topic_subset.py
uv run python ontologies/energy-intel/scripts/build_editorial.py
uv run python ontologies/energy-intel/scripts/stamp_version_iri.py
uv run pytest ontologies/energy-intel/tests/test_ontology.py
```

All 6 V2-built TTL files are graph-isomorphic to in-tree post-rebuild
(rdflib `isomorphic` check; curator-log-v2.md § 1.1). HermiT exit 0
on merged closure post-stamp; pytest 30/30 PASS.

---

## FAIR / OBO publication checklist

Manual operations the user must execute before/around the v0.3.0
publication:

### Pre-tag verification

- [ ] Re-run V2 build pipeline on a fresh worktree
  (`uv run python ontologies/energy-intel/scripts/extract_oeo_topic_subset.py`,
  `uv run python ontologies/energy-intel/scripts/build_editorial.py`,
  `uv run pytest ontologies/energy-intel/tests/test_ontology.py`).
  Expect every step exits 0 and pytest reports 30/30 PASS.
- [ ] Confirm `release-audit-v2.yaml` reads `sign_off: signed`
  with `signed_by: kokokessy@gmail.com` and recommendation `release`.
- [ ] Review [`docs/curator-log-v2.md`](../docs/curator-log-v2.md).

### Git tagging

- [ ] Stage and commit V2 source files per
  [`docs/validator-to-curator-handoff-v2.md` § 5](../docs/validator-to-curator-handoff-v2.md).
- [ ] Tag and push:
  ```bash
  git tag -a v0.3.0 -m "energy-intel v0.3.0: V2 editorial extension (Narrative + NarrativePostMembership; OEO topic subset rebuild; 3 SKOS schemes; 4 SHACL shapes)"
  git push origin main
  git push --tags
  ```

### PURL / w3id redirect refresh

- [ ] Coordinate with w3id admins to point
  `https://w3id.org/energy-intel/v2/2026-05-04` at the v0.3.0 release TTL.
- [ ] Update `https://w3id.org/energy-intel/` (latest) to redirect to
  v0.3.0.
- [ ] Verify with `curl -I https://w3id.org/energy-intel/v2/2026-05-04`.
- [ ] **NOTE (deferred):** PURL configuration for V2 module IRIs (e.g.
  `https://w3id.org/energy-intel/modules/editorial/v2/2026-05-04`) is
  carried as a v0.4.0+ open item per scope.md open question #2 (V0
  carry-forward). Local catalog (`catalog-v001.xml`) maps each ontology
  IRI to its file path; this is sufficient for local builds and the
  initial Cloudflare KG ingestion. Public dereferencing of every
  module versionIRI awaits the PURL/W3ID v0.4.0 batch.

### Content negotiation

- [ ] Confirm content negotiation is configured for the release IRI:
  - `curl -H "Accept: text/turtle" https://w3id.org/energy-intel/v2/2026-05-04`
  - `curl -H "Accept: application/rdf+xml" https://w3id.org/energy-intel/v2/2026-05-04`
  - `curl -H "Accept: application/ld+json" https://w3id.org/energy-intel/v2/2026-05-04`
- [ ] If not yet configured, add to repo CI publish step:
  ```bash
  .local/bin/robot convert --input release/energy-intel.ttl --output release/energy-intel.owl
  .local/bin/robot convert --input release/energy-intel.ttl --output release/energy-intel.jsonld --format json-ld
  ```

### License + metadata

- [ ] CC-BY-4.0 badge in `README.md`.
- [ ] Confirm `dcterms:license` is set on top-level + every module +
  every import (verified in `release-audit-v2.yaml`).

### Linear / project tracker

Open follow-up issues for V2-CUR-1..V2-CUR-6 per validator handoff:

- V2-CUR-1: pyshacl S-V2-4 severity rendering quirk (architect, v0.4.0)
- V2-CUR-2: fold v2-extra-leak-terms.txt (curator, v0.4.0)
- V2-CUR-3: DL profile-validate stays advisory (curator, ongoing)
- V2-CUR-4: deprecate technology-seeds concepts (curator, v0.4.0)
- V2-CUR-5: allow-list size monitor (curator, ongoing)
- V2-CUR-6: promote negative-case fixtures (architect, v0.4.0)

---

## Carry-forward V0.4.0+ items

These are NOT release blockers; they are V3+ watch-items:

* **Promote negative-case fixtures** (V2-CUR-6). Validator's
  defense-in-depth probe (6 fixtures, 6/6 catch) at
  `validation/v2/validator-rerun/negative-shacl/` should land as
  permanent test corpus.
* **Deprecate technology-seeds concepts** (V2-CUR-4). 5 concepts
  should get `owl:deprecated true` + `dcterms:isReplacedBy
  oeo:OEO_xxx`.
* **Fix pyshacl S-V2-4 severity rendering** (V2-CUR-1).
  `build_editorial.py` 2-line edit to declare `sh:severity
  sh:Warning` at NodeShape level.
* **Fold v2-extra-leak-terms.txt** (V2-CUR-2).
* **OEO TOP+BOT descendants extraction** (V1-CUR-1 carry-forward).
  Currently upward-only.
* **PURL configuration for module versionIRIs** (V0/V1 carry-forward
  open question #2). v0.4.0 batch.
* **Seven-facet Variable model** (V0/V1 carry-forward). Conceptualizer
  deferred.
* **Expert subrole taxonomy** (V0/V1 carry-forward). V2 didn't
  refine; v0.4.0+ when corpus signals warrant.

---

## Files released

### Source (TBox + shapes + imports)

- [`energy-intel.ttl`](../energy-intel.ttl) — top-level (V2 versionIRI stamped by architect)
- [`modules/agent.ttl`](../modules/agent.ttl) (V1 carry-forward)
- [`modules/media.ttl`](../modules/media.ttl) (V1 carry-forward)
- [`modules/measurement.ttl`](../modules/measurement.ttl) (V1 carry-forward)
- [`modules/data.ttl`](../modules/data.ttl) (V1 carry-forward)
- [`modules/editorial.ttl`](../modules/editorial.ttl) — **NEW V2** (versionIRI stamped by curator)
- [`modules/concept-schemes/argument-pattern.ttl`](../modules/concept-schemes/argument-pattern.ttl) — **NEW V2**
- [`modules/concept-schemes/narrative-role.ttl`](../modules/concept-schemes/narrative-role.ttl) — **NEW V2**
- [`modules/concept-schemes/oeo-topics.ttl`](../modules/concept-schemes/oeo-topics.ttl) — **NEW V2**
- [`modules/concept-schemes/aggregation-type.ttl`](../modules/concept-schemes/aggregation-type.ttl) (V1 carry-forward)
- [`modules/concept-schemes/temporal-resolution.ttl`](../modules/concept-schemes/temporal-resolution.ttl) (V1 carry-forward)
- [`modules/concept-schemes/technology-seeds.ttl`](../modules/concept-schemes/technology-seeds.ttl) — RETIRED FROM `owl:imports`; preserved on disk
- [`shapes/energy-intel-shapes.ttl`](../shapes/energy-intel-shapes.ttl) (V0/V1 carry-forward; 9 shapes)
- [`shapes/editorial.ttl`](../shapes/editorial.ttl) — **NEW V2** (4 shapes; versionIRI stamped)
- [`imports/oeo-topic-subset.ttl`](../imports/oeo-topic-subset.ttl) — **NEW V2** (7,729 triples; versionIRI stamped)
- [`imports/oeo-topic-seeds.txt`](../imports/oeo-topic-seeds.txt) — **NEW V2** (41 seed IRIs)
- [`imports/v2-extra-leak-terms.txt`](../imports/v2-extra-leak-terms.txt) — **NEW V2** (6 BFO IRIs)
- [`imports/oeo-technology-subset-fixed.ttl`](../imports/oeo-technology-subset-fixed.ttl) (V1 carry-forward)
- [`imports/oeo-carrier-subset-fixed.ttl`](../imports/oeo-carrier-subset-fixed.ttl) (V1 carry-forward)
- [`imports/qudt-units-subset.ttl`](../imports/qudt-units-subset.ttl) (V1 carry-forward)
- [`catalog-v001.xml`](../catalog-v001.xml) (updated)

### Tests

- [`tests/test_ontology.py`](../tests/test_ontology.py) (V2: 30 CQ tests)
- [`tests/cq-test-manifest.yaml`](../tests/cq-test-manifest.yaml) (30 entries)
- 11 V2 fixture files: `tests/fixtures/cq-editorial-{N1..N8,T1,T2,granularity}.ttl`
- 11 V2 SPARQL files: `tests/cq-editorial-*.sparql`

### Docs (V2)

- [`docs/scope-v2.md`](../docs/scope-v2.md)
- [`docs/competency-questions-v2.yaml`](../docs/competency-questions-v2.yaml)
- [`docs/conceptual-model-v2.md`](../docs/conceptual-model-v2.md)
- [`docs/property-design-v2.md`](../docs/property-design-v2.md)
- [`docs/axiom-plan-v2.md`](../docs/axiom-plan-v2.md)
- [`docs/architect-build-log-v2.md`](../docs/architect-build-log-v2.md)
- [`docs/validator-report-v2.md`](../docs/validator-report-v2.md)
- [`docs/validator-to-curator-handoff-v2.md`](../docs/validator-to-curator-handoff-v2.md)
- [`docs/curator-log-v2.md`](../docs/curator-log-v2.md)

### Release artefacts (V2)

- [`release/release-audit-v2.yaml`](release-audit-v2.yaml) (signed)
- [`release/v2-diff-vs-v1.md`](v2-diff-vs-v1.md) — curator-categorized robot diff
- [`release/release-notes-v0.3.0.md`](release-notes-v0.3.0.md) (this file)
- [`release/editorial-v0-changes.kgcl`](editorial-v0-changes.kgcl) — V2 KGCL change record (16 blocks)

### Imports manifests

- [`imports-manifest.yaml`](../imports-manifest.yaml) (V0 baseline)
- [`imports-manifest-v1.yaml`](../imports-manifest-v1.yaml) (V1 delta)
- [`imports-manifest-v2.yaml`](../imports-manifest-v2.yaml) — **NEW V2** delta
- [`imports-manifest-INDEX.yaml`](../imports-manifest-INDEX.yaml) — refreshed for V2

### Build / helper scripts

- `scripts/extract_oeo_topic_subset.py` — V2 OEO topic subset builder
- `scripts/build_editorial.py` — V2 editorial extension builder
- `scripts/stamp_version_iri.py` — **NEW** programmatic versionIRI stamp helper

### Validation evidence

- [`validation/v2/validator-rerun/`](../validation/v2/validator-rerun/) —
  validator's independent re-run evidence (per-gate artefacts)
- [`validation/v2/merged-top-level.ttl`](../validation/v2/merged-top-level.ttl) —
  V2 merged closure (33,343 lines)
- [`validation/report-allowlist.tsv`](../validation/report-allowlist.tsv) —
  upstream-ERROR allow-list (49 rows; V2 added 0)

---

## Acknowledgements

Architect: `ontology-architect` (V2 iteration, 2026-05-04).
Validator: `ontology-validator` (independent re-run, 2026-05-04).
Curator: `ontology-curator` (V2 release-prep, 2026-05-04).
Reviewer: kokokessy@gmail.com.

ROBOT 1.9.8 + HermiT + pyshacl. uv-managed Python 3.12+. rdflib for
KGCL-equivalent programmatic edits.
