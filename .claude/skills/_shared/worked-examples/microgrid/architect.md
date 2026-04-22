# Microgrid — `ontology-architect` walkthrough

Walks [`ontology-architect`](../../../ontology-architect/SKILL.md) Steps
0–8 on the microgrid ontology. Signature content: the property chain
`hasPart ∘ locatedIn → locatedIn` stays **EL-safe**, letting ELK ride
the dev cycle; SHACL picks up the per-subgrid cardinality the conceptual
model deferred. Also walks an **equivalence-bridge failure** (OEO vs a
hypothetical device ontology that treats inverter as function, not
object).

## Step 0 — build regime

```yaml
regime: standalone_pod
edit_file: ontologies/microgrid/microgrid.ttl
justfile_target: just build-microgrid
```

## Step 1 — profile + reasoner

Declared profile: **OWL 2 EL** (contrast with ensemble's DL). Per the
construct-support matrix (`owl-profile-playbook.md § 3`):

| CQ | axiom | EL | Reason |
|---|---|---|---|
| CQ-M-001 | `locatedIn SubPropertyChainOf hasPart ∘ locatedIn` | ✓ | Simple chain (single composition, R appears only at end) |
| CQ-M-002 | `IslandingEvent SubClassOf DispatchEvent and hasParticipant some EnergyAsset` | ✓ | Existential only |
| CQ-M-003 | `TelemetryPacket SubClassOf isAbout some EnergyAsset` | ✓ | Existential only |
| CQ-M-004 | `Inverter SubClassOf bearerOf some PrimaryInverterRole` | ✓ | Existential only |

Reasoner: **ELK** for dev + release gate (the whole TBox is EL). HermiT
is still used by `ontology-validator` Level 1 as a belt-and-braces check
but does not alter the declared profile.

## Step 2.5 — import / declaration preflight

```
$ .local/bin/robot merge --input microgrid.ttl --input imports/*.ttl --output /tmp/merged-preflight.ttl
$ uv run python scripts/axiom_plan_iri_extract.py --plan docs/axiom-plan.yaml > /tmp/iris.txt
$ while read iri; do uv run runoak -i /tmp/merged-preflight.ttl info "$iri" >/dev/null 2>&1 || echo "MISSING: $iri"; done < /tmp/iris.txt
  (no output — all IRIs resolve)
```

## Step 3 + 3.5 — ROBOT template + preflight (equipment taxonomy)

`ontologies/microgrid/microgrid-template.tsv`:

```tsv
ID	LABEL	SC %	DEFINITION
ID	A rdfs:label@en	SC %	A obo:IAO_0000115@en
mg:SolarArray	solar array	mg:GenerationAsset	A photovoltaic generation asset composed of panels and an array inverter.
mg:Battery	battery	mg:StorageAsset	A storage asset that holds chemical energy for dispatch.
mg:Inverter	inverter	mg:PowerElectronicsDevice	A power-electronics device that converts DC and AC forms.
mg:LoadBank	load bank	mg:LoadAsset	A dispatchable load element.
```

Preflight log: clean — all required cells, all CURIEs resolve, merge
mode set to `--merge-after` (additive template).

## Step 5 — property chain via rdflib (for CQ-M-001)

Property chains require a list; ROBOT template can express simple
subPropertyOf but chain composition needs triple-level control:

```python
from rdflib import Graph, BNode, URIRef
from rdflib.namespace import RDF, OWL
from rdflib.collection import Collection

g = Graph().parse("ontologies/microgrid/microgrid.ttl", format="turtle")
MG = "http://example.org/microgrid/"
has_part = URIRef(MG + "hasPart")
located_in = URIRef(MG + "locatedIn")

chain = BNode()
Collection(g, chain, [has_part, located_in])     # rdf:List of R1, R2
g.add((located_in, OWL.propertyChainAxiom, chain))
g.serialize("ontologies/microgrid/microgrid.ttl", format="turtle")
```

## Step 6.5 — SHACL shapes (from `intent: validate`)

`ontologies/microgrid/shapes/microgrid-shapes.ttl`:

```ttl
# Per-subgrid PrimaryInverterRole cardinality (deferred from CQ-M-004)
:PrimaryInverterRoleShape a sh:NodeShape ;
  sh:targetClass :Subgrid ;
  sh:property [
    sh:path (:hasPart/:bearerOf) ;
    sh:qualifiedValueShape [ sh:class :PrimaryInverterRole ] ;
    sh:qualifiedMinCount 1 ;
    sh:qualifiedMaxCount 1 ;
    sh:severity sh:Violation ;
    sh:message "Each subgrid must have exactly one PrimaryInverterRole." ;
  ] .

# Telemetry timestamp datatype
:TelemetryPacketShape a sh:NodeShape ;
  sh:targetClass :TelemetryPacket ;
  sh:property [ sh:path :recordedAt ; sh:datatype xsd:dateTime ; sh:minCount 1 ;
                sh:severity sh:Violation ;
                sh:message "TelemetryPacket.recordedAt must be an xsd:dateTime." ] .
```

OWL restrictions on `bearerOf some PrimaryInverterRole` ensure the
existential; SHACL enforces the uniqueness per subgrid.

## Step 7.1 — profile + reasoner + report (EL gate)

```
$ .local/bin/robot merge --input microgrid.ttl --input imports/*.ttl --output validation/merged.ttl
$ .local/bin/robot validate-profile --profile EL --input validation/merged.ttl --output validation/profile-validate.txt
  → "Ontology is in OWL 2 EL profile."
$ .local/bin/robot reason --reasoner ELK --input validation/merged.ttl --output validation/reasoned.ttl
  → 0 unsatisfiable classes
  → chain entailment: :BatteryUnit_42 locatedIn :SiteA (derived from hasPart + site locatedIn)
$ .local/bin/robot report --input validation/merged.ttl --fail-on ERROR --output validation/robot-report.tsv
  → 0 ERROR; 2 WARN (missing skos:altLabel on :LoadBank; :BalanceOfSystem subclass singleton)
```

## Equivalence-bridge failure walk (SIGNATURE pitfall)

A downstream consumer requested an equivalence bridge to a hypothetical
`devon:Inverter` (device ontology) via
`sssom parse --preset exact-owl`. Applying the preset to an SSSOM row
`mg:Inverter skos:exactMatch devon:Inverter` emits
`mg:Inverter owl:equivalentClass devon:Inverter` into a bridge TTL.
**Reasoner on merged source + target + bridge fails:**

```
$ .local/bin/robot merge --input validation/merged.ttl \
    --input imports/devon-import.ttl \
    --input mappings/microgrid-to-devon-bridge.ttl --output /tmp/bridged.ttl
$ .local/bin/robot reason --reasoner HermiT --input /tmp/bridged.ttl \
    --dump-unsatisfiable /tmp/unsat-with-bridge.txt
  → UNSATISFIABLE: mg:Inverter
```

Root cause: `devon:Inverter` is a `bfo:Function` (dependent continuant)
while `mg:Inverter` is `bfo:Object` (independent continuant). The
equivalence bridge forces a class to be both, which contradicts
BFO's disjointness between continuant subcategories.

**Resolution.** Downgrade the bridge predicate from
`owl:equivalentClass` to `skos:exactMatch` (kept as SKOS, no OWL
identity assertion) per `modularization-and-bridges.md § 5.1`. Record
as a mapper loopback (`unsatisfiable_class`, routed to mapper). The
bridge ships as SSSOM only; consumers that want OWL identity must
opt-in via a separate reviewed equivalence bridge (§ 5.2) after
resolving the BFO category mismatch upstream.

## Step 8 — handoff manifest

```yaml
handoff_id: HOF-MICROGRID-2026-04-22
artifact_under_test: ontologies/microgrid/microgrid.ttl
merged_artifact: validation/merged.ttl
declared_profile: OWL-EL
reasoner: ELK
raw_logs:
  profile_validate: validation/profile-validate.txt
  reasoner_log: validation/reasoner.log
  robot_report: validation/robot-report.tsv
  pyshacl: validation/shacl-results.ttl
cq_implementation_matrix: ontologies/microgrid/docs/cq-implementation-matrix.csv
```

## Handoff

Merged artifact + manifest → `ontology-validator`. Bridge failure route
→ `ontology-mapper` (downgrade to SKOS per § 5.1). SHACL shapes carry
the cardinality gate the EL profile cannot express.
