# Microgrid — `ontology-validator` walkthrough

Walks [`ontology-validator`](../../../ontology-validator/SKILL.md) Levels
0–8 on the microgrid ontology. Goal: run the canonical command order
with an **EL subset gate for fast dev feedback**, re-validate under
HermiT for the release gate, validate the microgrid ↔ OEO mapping set,
and produce the Level 7 diff vs the prior release.

## Step 0 — artifact classification

```yaml
artifact_type: ontology
handoff_id: HOF-MICROGRID-2026-04-22
also_validating:                        # companion artifacts
  - type: mapping_set
    path: ontologies/microgrid/mappings/microgrid-to-oeo.sssom.tsv
  - type: mapping_set
    path: ontologies/microgrid/mappings/microgrid-to-schemaorg.sssom.tsv
```

## Command order

`L0 → L1 → L2 → L4 → L3 → L4.5 → L5.5 → L6 → L7 (diff)` plus mapping
gates interleaved at L0 / L5.5.

## Level 0 — syntax / EL profile / import closure

```
$ robot validate --input microgrid.ttl > validation/syntax.log
  → 0 parse errors
$ .local/bin/robot validate-profile --profile EL --input validation/merged.ttl \
    --output validation/profile-validate.txt
  → "Ontology is in OWL 2 EL profile."
$ .local/bin/robot validate-profile --profile DL --input validation/merged.ttl \
    --output validation/profile-validate-dl.txt      # DL release gate (superset)
  → "Ontology is in OWL 2 DL profile."
$ robot merge --input microgrid.ttl --collapse-import-closure true \
    --output validation/merged.ttl 2> validation/import.log
```

Both EL and DL gates run: EL is the declared profile, DL is the
belt-and-braces check for release. Mapping SSSOM files also get an L0
prefix preflight via `uv run sssom validate` (captured in the mapping
gate report).

## Level 1 — reasoner (dual-gate)

```
$ robot reason --reasoner ELK --input validation/merged.ttl \
    --output validation/reasoned-el.ttl --dump-unsatisfiable validation/unsat-el.txt
  → 0 unsatisfiable; property chain hasPart∘locatedIn→locatedIn entails
    :BatteryUnit_42 locatedIn :SiteA
$ robot reason --reasoner HermiT --input validation/merged.ttl \
    --output validation/reasoned-dl.ttl --dump-unsatisfiable validation/unsat-dl.txt
  → 0 unsatisfiable (identical entailments — EL subset confirmed safe)
```

Dual-gate catches a scenario where the development team added a DL-only
axiom (e.g., `only` restriction) without updating the profile. Had that
happened, ELK would run clean but HermiT would find new entailments —
signal to widen the declared profile and downgrade the release reasoner.

## Level 2 — ROBOT report

```
$ robot report --input validation/merged.ttl --fail-on ERROR --output validation/robot-report.tsv
  → 0 ERROR; 2 WARN
    missing_synonym        mg:LoadBank
    missing_definition     mg:BalanceOfSystem
```

## Level 4 — CQ verify

```
$ robot verify --input validation/reasoned-el.ttl \
    --queries ontologies/microgrid/tests/ --output-dir test-results/
  CQ-M-001: PASS (72 rows — transitive locatedIn entailed)
  CQ-M-002: PASS (3 IslandingEvent instances, each with ≥1 equipment)
  CQ-M-003: PASS (14 telemetry packets about batteries)
  CQ-M-004: PASS (one PrimaryInverterRole bearer per subgrid)
  CQ-M-005: PASS (3 exactMatch promotion candidates flagged for review)
```

## Level 3 — SHACL

```
$ uv run pyshacl -s ontologies/microgrid/shapes/microgrid-shapes.ttl \
    --inference rdfs -f human ontologies/microgrid/microgrid.ttl > validation/shacl-results.ttl
  → Conforms: True
  (PrimaryInverterRoleShape: all subgrids have exactly 1; TelemetryPacketShape: all have xsd:dateTime)
```

**Inverse pitfall caveat.** Had the microgrid ABox lacked a
`PrimaryInverterRole` assignment on one subgrid, OWL reasoning would
still succeed (OWA says "unknown, not false") while SHACL would fail
`sh:qualifiedMinCount 1`. This is the SHACL/OWL inverse-pitfall
scenario — see SKILL.md "Consistency vs Validity" table.

## Level 3.5 — SHACL shape coverage

```
$ uv run python scripts/shacl_coverage.py \
    --property-design docs/property-design.yaml \
    --shapes shapes/ --out validation/shacl-coverage.json
  {
    "intent_validate_rows": 1,
    "covered": 1,
    "missing": []
  }
```

`recordedAt` (`intent: validate`) is covered by `TelemetryPacketShape`.

## Level 4.5 — CQ manifest audit

```
$ uv run python scripts/cq_manifest_check.py \
    --manifest tests/cq-test-manifest.yaml \
    --ontology microgrid.ttl --axiom-plan docs/axiom-plan.yaml \
    --out validation/cq-manifest-audit.json
  { "missing_files": [], "must_have_covered": true, "stale_refs": [], "entailment_regime_mismatches": [] }
```

## Level 5.5 — anti-pattern pack (ontology + mapping)

```
$ # Per-probe SPARQL against reasoned-el.ttl
  singleton-hierarchy.csv: 1 row — mg:BalanceOfSystem
  orphan-class.csv: empty
  missing-disjointness.csv: 0 rows (fix from conceptualizer anti-pattern-review applied)
  role-as-subclass.csv: empty
  process-as-material.csv: empty
$ # Mapping gates — mapping-evaluation.md § 1 on both SSSOM sets
  mapping clique (microgrid-to-oeo): 0 violations
  cross_domain_exactMatch (microgrid-to-schemaorg): 0 flags (all downgraded per mapper.md)
```

`mg:BalanceOfSystem` singleton traces back to conceptualizer's
open-items list — already resolved in `anti-pattern-review.md`; no
fresh loopback.

## Level 6 — evaluation dimensions

| Dimension | Finding |
|---|---|
| Semantic | Expressivity EL supports all Must-Have CQs. |
| Functional | All 5 CQs pass; SHACL enforces the per-subgrid cap that OWL EL cannot express. |
| Model-centric | Layer boundaries enforced; OEO pin dated 2026-02-15; quarterly refresh scheduled. |

## Level 7 — diff vs prior release

```
$ robot diff --left release/microgrid-2026-03-15.ttl --right microgrid.ttl \
    --format markdown --output validation/diff.md
```

Excerpt:

```
+ :IslandingEvent rdfs:subClassOf :DispatchEvent
+ :TelemetryPacket rdfs:subClassOf iao:IAO_0000030
+ :recordedAt rdfs:range xsd:dateTime
- :BalanceOfSystem rdfs:subClassOf :EnergyAsset   (moved to :AncillaryEquipment; see CHG-2026-04-20-003)
```

Every line cites back to a change-log entry per
[`curator.md`](curator.md) Step 6.5. Unannotated diff lines would fire
an L7 loopback to curator.

## Level 8 — loopback routing table (excerpt)

| Failure | Owner skill | Fix | Retry gate |
|---|---|---|---|
| (none this run) | — | — | — |

All levels pass or are within WARN threshold. Mapping gates pass both
sets. Diff fully annotated.

## Pitfall walk — mapping-set validation interleaved with ontology validation

A previous run neglected the mapping-set gates (Level 0 prefix
preflight + Level 5.5 clique / cross-domain check). The ontology
validated clean, but a subsequent release contained a
cross-domain `exactMatch` that the validator had never checked. Fix:
the Level 0 + Level 5.5 interleave is canonical per `mapping-
evaluation.md § 1`. The `also_validating` block in the Step 0 header
is load-bearing — it tells the validator which companion artifacts to
gate. Silent omission of this block is a bug.

## Handoff

Full validation report → user approval → release pipeline
(curator Step 5.6 publication check). No loopbacks raised.
