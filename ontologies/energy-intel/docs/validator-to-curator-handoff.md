# Validator → Curator Handoff — `energy-intel`

**From:** `ontology-validator` (2026-04-22)
**To:** `ontology-curator`
**Release:** V0.1.0
**Release verdict:** `block-pending-fix` (SHACL S-1 reconciliation required)
**Audit artefact:** `release/release-audit.yaml`
**Validator report:** `docs/validator-report.md`

---

## What you own next

1. **Hold release until SHACL S-1 is reconciled.** Architect must either
   regenerate fixtures with raw `did:plc:` / `did:web:` IRIs or relax the
   `DidSchemeOnAuthoredBy` shape. Re-run
   `uv run python ontologies/energy-intel/scripts/run_shacl_gate.py`
   expecting 14/14 conforms. Only then flip
   `release-audit.yaml → sign_off: signed` and publish.

2. **Publish the PURL / w3id redirects.** The ontology IRI is
   `https://w3id.org/energy-intel/`. Coordinate with the w3id admins to
   register the redirect to the release TTL. Scope open question #2
   (architect handoff bullet 9) — track this.
   Until w3id is live, consumers must use `catalog-v001.xml` to resolve
   intra-project imports.

3. **Wire the gates into CI** using `_shared/github-actions-template.md`.
   The essential job steps:

   ```yaml
   - run: .local/bin/robot merge --catalog ontologies/energy-intel/catalog-v001.xml \
          --input ontologies/energy-intel/energy-intel.ttl \
          --output validation/merged-top-level.ttl
   - run: .local/bin/robot reason --reasoner hermit \
          --input validation/merged-top-level.ttl \
          --output validation/reasoned-top-level.ttl
   - run: uv run python ontologies/energy-intel/scripts/run_gates.py
   - run: uv run python ontologies/energy-intel/scripts/apply_report_allowlist.py
   - run: uv run python ontologies/energy-intel/scripts/run_shacl_gate.py
   - run: uv run pytest ontologies/energy-intel/tests/test_ontology.py
   ```

   The allow-list script exits non-zero iff a new project-origin ERROR
   appears — that's the regression gate you want.

4. **KGCL change-log seeding.** The V0 TBox + shapes + fixtures are
   the baseline. Seed `ontologies/energy-intel/energy-intel-changes.kgcl`
   with an empty header pointing at the v0 baseline commit (`dc123d4`).
   Every subsequent term add/rename/deprecate goes through the KGCL
   file first, then through ROBOT template or rdflib to apply.

5. **First-expected deprecation-refresh cadence.**
   * **BFO-2020**: 365-day cadence (stable ISO standard).
   * **IAO v2026-03-30**: 120-day cadence (active OBO development).
   * **OEO v2.11.0**: 180-day cadence (currently not imported in V0;
     if V1 lands the OEO import with the BFO-conflict remediation,
     raise the cadence to 90 days until settled).
   * **DCAT / PROV / FOAF / SKOS / DCT**: 365-day cadence (mature W3C
     recs).
   Run `uv run runoak … compare` at each refresh; any non-trivial
   diff triggers a curator-run `robot diff` + KGCL patch.

6. **OEO-punning V1 remediation ticket.** Non-blocking for V0 but
   **must be resolved before V1 can `owl:imports` the OEO subsets**:
   * Root cause: OEO v2.11.0 bundles a BFO backbone snippet that
     conflicts with the live BFO-2020 import in `modules/agent.ttl`
     (HermiT: "inconsistent ontology").
   * Option A: `robot remove --term BFO_* --axioms structural` on
     each OEO subset before import.
   * Option B: Re-root `agent.ttl` to use the OEO-embedded BFO
     snapshot instead of `<obo/bfo.owl>`.
   * Validator recommends A (keeps BFO-2020 as the authoritative
     upper ontology).

7. **Track the upstream allow-list drift.** `validation/report-allowlist.tsv`
   is signed as of 2026-04-22. When upstreams refresh (DCAT-4, FOAF 1.0,
   IAO v2027-XX), re-run `robot report` and compare new ERROR rule/subject
   combinations against the allow-list. Net-new rule/prefix pairs require
   a fresh justification + reviewer signature.

8. **V0 publication checklist (FAIR / OBO):**
   * [ ] Register PURL redirects (`https://w3id.org/energy-intel/` →
     release TTL)
   * [ ] Publish release TTL + `release-audit.yaml` + `v0-baseline-diff.md`
     as a git tag (`v0.1.0`)
   * [ ] Attach license badge (CC-BY-4.0) in repo README
   * [ ] Register with OBO registry (if appropriate; domain fit with
     energy-vocab ecosystem suggests yes)
   * [ ] Emit content-negotiation: `.ttl` for Turtle, `.owl` for
     RDF/XML, `.jsonld` for JSON-LD. `robot convert` handles the
     serialisation.

9. **Annotated stub for the V1 change log.** V1 must formalise:
   * OEO subset import (after construct_mismatch remediation);
   * The seven-facet Variable model (deferred per conceptualizer);
   * Extended SHACL shapes covering the remaining 11 rows in
     `docs/property-design.md` flagged `intent: validate`;
   * QUDT 2.1 unit-system crosswalk.

10. **Stale-CQ detection cadence.** The architect's fixtures + the
    validator's pytest harness cover 14 CQs. At every subsequent term
    rename or deprecation, re-run the CQ pytest *and* re-run
    `scripts/cq_manifest_check.py` (per `.claude/rules/ontology-testing.md`)
    to catch drift between `required_classes` / `required_properties`
    in the manifest and the live TBox.

---

## Files you inherit

| Artefact | Path |
|----------|------|
| Release audit (pending sign-off) | `release/release-audit.yaml` |
| V0 baseline self-diff | `release/v0-baseline-diff.md` |
| Validator comprehensive report | `docs/validator-report.md` |
| Upstream ERROR allow-list | `validation/report-allowlist.tsv` |
| Allow-list filter runner | `scripts/apply_report_allowlist.py` |
| SHACL fixture gate runner | `scripts/run_shacl_gate.py` |
| CQ pytest harness | `tests/test_ontology.py` |
| Per-fixture SHACL result graphs | `validation/shacl-results-cq-*.ttl` |
| SHACL summary JSON | `validation/shacl-summary.json` |
| Per-module HermiT-reasoned TBox | `validation/reasoned-*.ttl` |
| Top-level+OEO inconsistency trace | `validation/merged-top-level-with-oeo.ttl` |
| Architect handoff (your upstream) | `docs/architect-to-validator-handoff.md` |

---

## One-sentence lead

**V0 energy-intel gates pass on reasoner / CQ pytest / ROBOT report (with
allow-list) / release diff — release is blocked on one SHACL shape
reconciliation (S-1 DID-scheme pattern vs fixture URI form) and carries
a non-blocking `construct_mismatch` loopback on OEO+BFO import, which
the curator tracks as a V1 remediation ticket.**
