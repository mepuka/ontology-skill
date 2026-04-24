# Ensemble — `ontology-architect` walkthrough

Walks [`ontology-architect`](../../../ontology-architect/SKILL.md) Steps
0–8 for the ensemble ontology. Goal: formalize the signed axiom plan
from [`conceptualizer.md`](conceptualizer.md), pass the Step 7.1 three-
gate, and package a validator handoff showing **why ELK alone fails**
the Step 1 construct-support matrix.

## Step 0 — build regime (`docs/build-regime.yaml`)

```yaml
regime: standalone_pod           # custom scripts/build.py, no ODK
edit_file: ontologies/ensemble/ensemble.ttl
justfile_target: just build-ensemble
```

## Step 1 — profile + reasoner pairing

Declared profile: **OWL 2 DL**. Axiom plan contains non-EL constructs,
per the construct-support matrix (`owl-profile-playbook.md § 3`):

| CQ | axiom | EL | Reason |
|---|---|---|---|
| CQ-E-001 | `hasMember exactly 4 Musician` | ✗ | Qualified cardinality is DL-only |
| CQ-E-004 | `hasMember only (plays some StringInstrument)` | ✗ | Universal restriction non-EL |

Reasoner pairing: ELK for development (fast feedback), **HermiT for the
release gate**. ELK-only on this ontology silently drops CQ-E-001 and
CQ-E-004 — the signature architect pitfall.

## Step 2.5 — import preflight

```
$ uv run python scripts/axiom_plan_iri_extract.py --plan docs/axiom-plan.yaml > /tmp/referenced-iris.txt
$ .local/bin/robot merge --input ensemble.ttl --input imports/mimo-import.owl --input imports/ro-core.owl --output /tmp/merged-for-preflight.ttl
$ while read iri; do uv run runoak -i /tmp/merged-for-preflight.ttl info "$iri" >/dev/null 2>&1 || echo "MISSING: $iri"; done < /tmp/referenced-iris.txt
MISSING: mimo:Hornbostel-SachsCategory
```

Resolution: raise `missing_reuse` loopback to `ontology-scout` — the
hyphen drops through to a typo (`mimo:HornbostelSachsCategory` is the
canonical IRI). Scout fixes the term list + re-extracts.

## Step 3 + 3.5 — ROBOT template + preflight

`ontologies/ensemble/ensemble-template.tsv`:

```tsv
ID	LABEL	SC %	DEFINITION
ID	A rdfs:label@en	SC %	A obo:IAO_0000115@en
ens:Violin	violin	mimo:BowedStringInstrument	A bowed string instrument with four strings tuned in fifths.
ens:Viola	viola	mimo:BowedStringInstrument	A bowed string instrument slightly larger than a violin.
ens:Cello	cello	mimo:BowedStringInstrument	A large bowed string instrument played seated.
ens:Piano		mimo:KeyboardInstrument	A keyboard instrument producing sound by hammered strings.
```

Preflight log (`validation/robot-template-preflight/ensemble.log`) catches
the empty `LABEL` cell on `ens:Piano`:

```
FAIL  row 6: column LABEL is empty but directive is 'A rdfs:label@en'
```

Fix cell → rerun preflight → clean → run `robot template`. Without the
preflight, ROBOT would have emitted a label-less `ens:Piano` (pitfall
§ 4.1 *Empty cell under `SC %` / required annotation column*).

## Step 5 — complex axiom via rdflib (for CQ-E-001)

Qualified cardinality cannot be authored in a ROBOT template column
directly (the `%` substitution does not support `exactly N`); drop to
rdflib:

```python
from rdflib import Graph, BNode, URIRef, Namespace
from rdflib.namespace import OWL, RDF, RDFS, XSD

g = Graph().parse("ontologies/ensemble/ensemble.ttl", format="turtle")
ENS = Namespace("http://example.org/ensemble/")
r = BNode()
g.add((r, RDF.type, OWL.Restriction))
g.add((r, OWL.onProperty, ENS.hasMember))
g.add((r, OWL.qualifiedCardinality, XSD.nonNegativeInteger))  # value 4
g.add((r, OWL.onClass, ENS.Musician))
g.add((ENS.StringQuartet, OWL.equivalentClass, r))
g.serialize("ontologies/ensemble/ensemble.ttl", format="turtle")
```

## Step 6.5 — SHACL from property-design intent

Only properties with `intent: validate` in `property-design.yaml` get
shapes. `hasOpusNumber` is `validate`:

```ttl
:OpusNumberShape a sh:NodeShape ;
  sh:targetClass :Composition ;
  sh:property [ sh:path :hasOpusNumber ; sh:datatype xsd:string ; sh:maxCount 1 ;
                sh:severity sh:Violation ; sh:message "Opus number is a string, one per work." ] .
```

`hasMember` stays `intent: infer` → OWL restriction only; no shape.

## Step 7.1 — three-gate run (mandatory before handoff)

```
$ .local/bin/robot merge --input ensemble.ttl --input imports/*.owl --output validation/merged.ttl
$ .local/bin/robot validate-profile --profile DL --input validation/merged.ttl --output validation/profile-validate.txt
 → "Ontology is in OWL 2 DL profile."
$ .local/bin/robot reason --reasoner HermiT --input validation/merged.ttl --output validation/reasoned.ttl --dump-unsatisfiable validation/unsatisfiable.txt
 → 0 unsatisfiable classes; StringQuartet classified as subclass of Ensemble
$ .local/bin/robot report --input validation/merged.ttl --fail-on ERROR --output validation/robot-report.tsv
 → 0 ERROR; 3 WARN (missing skos:altLabel on three new MIMO leaves)
```

**Contrast — ELK alone misses CQ-E-001.** Running `robot reason --reasoner
ELK` on the same input produces an empty `unsatisfiable.txt` *and* a
reasoned file where `ens:BeethovenQuartetInstance a StringQuartet` is
**not** entailed, because ELK silently ignored the qualified
cardinality. This is the signature architect pitfall (owl-profile-
playbook.md § 2 "ELK skips"). Only HermiT is a valid release-gate
reasoner for this ontology.

## Step 8 — handoff package (`validation/handoff-manifest.yaml`)

```yaml
handoff_id: HOF-ENSEMBLE-2026-04-22
artifact_under_test: ontologies/ensemble/ensemble.ttl
merged_artifact: validation/merged.ttl
declared_profile: OWL-DL
reasoner: HermiT
raw_logs:
  profile_validate: validation/profile-validate.txt
  reasoner_log: validation/reasoner.log
  robot_report: validation/robot-report.tsv
  pyshacl: validation/shacl-results.ttl
  robot_template_preflight: [validation/robot-template-preflight/ensemble.log]
cq_implementation_matrix: ontologies/ensemble/docs/cq-implementation-matrix.csv
```

`cq-implementation-matrix.csv` maps CQ-E-001..005 to axioms, shapes, and
SPARQL tests — read by `ontology-validator` Level 4 (see
[`validator.md`](validator.md)).

## Handoff

Manifest + merged artifact → `ontology-validator`. Loopback hooks:
`profile_violation` or `construct_mismatch` routes back here per
[`iteration-loopbacks.md § 3`](../../iteration-loopbacks.md).
