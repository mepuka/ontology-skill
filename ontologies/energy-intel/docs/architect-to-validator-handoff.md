# Architect → Validator Handoff — `energy-intel`

**From:** `ontology-architect` (2026-04-22, post-OEO-verification session)
**To:** `ontology-validator`
**Build log:** `docs/architect-build-log.md`
**Session summary:** V0 TBox landed; 14/14 CQ fixtures pass; shapes drafted.

---

## Ten crisp bullets for the validator to action

1. **Four TBox modules + top-level are ready.** Validator entry point is
   `ontologies/energy-intel/energy-intel.ttl` (top-level `owl:imports`
   the four modules, three hand-seeded SKOS schemes, and the seven
   upstream ontologies per `imports-manifest.yaml`). Internal IRI
   resolution uses `catalog-v001.xml` — pass `--catalog
   catalog-v001.xml` to every `robot merge` call. The gate runner at
   `scripts/run_gates.py` shows the exact invocation pattern.

2. **Reasoner verdict: HermiT-clean on every module (including the
   top-level merge).** Zero unsatisfiable classes, zero inconsistency
   under `robot reason --reasoner hermit`. ELK is unsuitable for
   releases because the ontology uses qualified cardinality, inverse
   property expressions, and datatype unions — ELK silently drops
   these. Keep HermiT as the release gate.

3. **`robot report` ERRORs are all upstream.** 329 ERRORs on the
   top-level report; every single one originates from an imported
   vocabulary (DCAT multilingual duplicate labels,
   FOAF `givenName`/`givenname`, PROV/FOAF `Person`/`Organization`
   label collision, SKOS/IAO/RO label overlaps, DCAT/PROV utility
   properties missing `rdfs:label`). Zero ERRORs from `ei:` or
   `ei:concept/*` terms. Validator should continue to `--fail-on ERROR`
   but pass an upstream-allowlist or run the report on the un-merged
   `energy-intel.ttl` (where only our terms land) to see a clean
   ERROR-free report. Suggested flag: `robot report --fail-on ERROR
   --input energy-intel.ttl` (no merge) yields 0 ERRORs.

4. **14/14 CQ fixtures pass their acceptance contracts.** Every fixture
   at `tests/fixtures/cq-NNN.ttl` makes its `tests/cq-NNN.sparql`
   return rows matching the `expected_results_contract` in
   `tests/cq-test-manifest.yaml`. The builder script
   `scripts/build_fixtures.py` is idempotent; re-running it rebuilds
   the fixtures and reports verdicts. CQ-009 correctly returns 0 rows
   on a well-formed fixture (the invariant holds); any non-zero answer
   is a spec violation.

5. **SHACL shapes drafted, not yet validated against rich ABox data.**
   `shapes/energy-intel-shapes.ttl` contains 4 NodeShapes
   (S-1 DID, S-2 JSON rawDims, S-3 interval ordering, CQ-009 companion).
   pyshacl accepts the shapes file. Validator should add a test that
   runs pyshacl against each fixture and confirms zero violations for
   fixtures 1–14 (they're well-formed). CQ-009's SHACL companion is the
   interesting one: a malformed fixture with a CMC lacking an
   `ei:evidences` inbound edge should produce exactly one violation.

6. **OEO subsets were extracted but NOT imported by energy-intel.ttl
   in V0.** `imports/oeo-technology-subset.ttl` and
   `imports/oeo-carrier-subset.ttl` are on disk (~1.1 MB each, ~90
   OEO-specific classes each). The top-level `owl:imports` deliberately
   does not pull them in V0 because the `ei:aboutTechnology` codomain
   is `skos:Concept` and CQ-013/CQ-014 punning behavior is not yet
   tested under HermiT on the full merged graph. Validator should:
   (a) add the two OEO subsets to the merge closure in a separate
   validation-only graph, (b) re-run HermiT, (c) confirm still
   reasoner-clean. If HermiT misbehaves on OEO+FOAF+PROV+punning, raise
   `construct_mismatch` back to architect.

7. **Namespace patch applied.** Scout phase used the wrong OEO namespace
   (`http://openenergy-platform.org/ontology/oeo/`). Verification
   confirmed canonical is `https://openenergyplatform.org/ontology/oeo/`
   (HTTPS, no hyphen). All live-use artifacts patched — manifest, CQ
   prefix header, reuse-report table. The wrong form still appears in
   `imports/oeo-seed-verification.md` only because that file documents
   the bug. If the validator ever greps for the wrong form outside
   that file, it's a regression.

8. **Three loopback risks to watch.**
   - **`construct_mismatch` on OEO punning** — pending step 6 above.
   - **SHACL-vs-OWL double-coverage** — the CQ-009 SHACL companion
     intentionally duplicates the OWL invariant (`docs/shacl-vs-owl.md`
     § defense-in-depth). Validator should not flag this as anti-pattern.
   - **`duplicate_label` upstream noise** — these are FOAF/DCAT
     historical artifacts; propose a project allow-list in the
     ROBOT report policy file rather than silencing them wholesale.

9. **Internal-catalog pattern for merges.** Because inter-module
   `owl:imports` targets are `https://w3id.org/energy-intel/modules/*`
   and w3id isn't live yet (scope open q #2), all `robot merge` calls
   must go through `catalog-v001.xml`. If the validator runs `robot`
   without `--catalog`, it gets
   `Could not load imported ontology` errors. See
   `scripts/run_gates.py` for a working invocation.

10. **Build scripts to re-run for reproducibility.**
    - `uv run python scripts/build_concept_schemes.py` — two SKOS
      schemes.
    - `uv run python scripts/build_technology_seeds.py` — wind / solar
      SKOS tree.
    - `uv run python scripts/build_modules.py` — four TBox modules +
      top-level.
    - `uv run python scripts/build_shapes.py` — SHACL shapes.
    - `uv run python scripts/build_fixtures.py` — 14 CQ fixtures with
      in-line SPARQL verification.
    - `uv run python scripts/run_gates.py` — per-module merge / reason
      / report gates, writes logs to `validation/`.

---

## File manifest (architect deliverables)

### TBox
- `energy-intel.ttl` — top-level ontology (22 triples, 14 `owl:imports`)
- `modules/agent.ttl` — 41 triples
- `modules/media.ttl` — 148 triples
- `modules/measurement.ttl` — 176 triples
- `modules/data.ttl` — 15 triples

### Hand-seeded schemes
- `modules/concept-schemes/temporal-resolution.ttl`
- `modules/concept-schemes/aggregation-type.ttl`
- `modules/concept-schemes/technology-seeds.ttl`

### Imports / MIREOT artifacts
- `imports/oeo-technology-subset.ttl` (BOT extract, dual root)
- `imports/oeo-carrier-subset.ttl` (BOT extract, single root)
- `imports/oeo-full.owl` (upstream snapshot; gitignored, rebuilt from
  OEO v2.11.0 source tarball)
- `imports/oeo-seed-verification.md` (verification report; documentary)

### Shapes
- `shapes/energy-intel-shapes.ttl` (45 triples, 4 NodeShapes)

### Tests
- `tests/fixtures/cq-001.ttl` … `tests/fixtures/cq-014.ttl` — one per CQ
- `tests/cq-test-manifest.yaml` — updated with pass status
- `tests/fixtures/_verdicts.txt` — machine-readable fixture verdicts

### Build + validation
- `catalog-v001.xml` — ROBOT catalog mapping internal `w3id.org`
  imports to local module files
- `scripts/build_*.py` — reproducible artifact generators
- `scripts/run_gates.py` — per-module merge/reason/report runner
- `validation/merged-*.ttl`, `reasoned-*.ttl`, `report-*.tsv`, logs
- `docs/architect-build-log.md` — step-by-step build + gate log
- `docs/architect-to-validator-handoff.md` — this file

### Documentation patches
- `imports-manifest.yaml` — OEO rows rewritten (dual root; aggregation
  row dropped; hand-seeded aggregation-type row added; namespace
  corrected)
- `docs/competency-questions.yaml` — `oeo:` prefix corrected
- `docs/reuse-report.md` — A.1/A.2/A.3/A.5 rows updated with verified
  IRIs + corrected namespace
- `.gitignore` — `ontologies/*/imports/oeo-full.owl` added

---

## Validator entry-point suggestion

```bash
# Level-0 pre-flight
.local/bin/robot merge \
  --catalog ontologies/energy-intel/catalog-v001.xml \
  --input ontologies/energy-intel/energy-intel.ttl \
  --output /tmp/energy-intel-merged.ttl

# Gate 1: profile validation
.local/bin/robot validate-profile --profile DL \
  --input /tmp/energy-intel-merged.ttl \
  --output /tmp/energy-intel-profile.txt

# Gate 2: reasoner classification
.local/bin/robot reason --reasoner hermit \
  --input /tmp/energy-intel-merged.ttl \
  --output /tmp/energy-intel-reasoned.ttl \
  --dump-unsatisfiable /tmp/energy-intel-unsat.txt

# Gate 3: ROBOT report (energy-intel-only, no merge)
.local/bin/robot report --fail-on ERROR \
  --input ontologies/energy-intel/energy-intel.ttl \
  --output /tmp/energy-intel-report.tsv

# Gate 4: CQ fixtures
uv run python ontologies/energy-intel/scripts/build_fixtures.py

# Gate 5: SHACL on each fixture
for f in ontologies/energy-intel/tests/fixtures/cq-*.ttl; do
  uv run pyshacl -s ontologies/energy-intel/shapes/energy-intel-shapes.ttl \
    -d "$f" -f human || echo "VIOLATION in $f"
done
```

---

## One-sentence lead

**V0 `energy-intel` TBox is HermiT-reasoner-clean, ROBOT-report-clean on
project-native terms, and 14/14 CQ fixtures pass their acceptance
contracts — validator should focus on the OEO-punning construct_mismatch
watch (handoff bullet 6) and on codifying the upstream-error allowlist
for `robot report` under merged imports (handoff bullet 3).**
