# SHACL Patterns

**Referenced by:** `ontology-conceptualizer`, `ontology-architect`,
`ontology-validator`, `sparql-expert`.

SHACL is the closed-world complement to OWL. Use it for data-shape
validation, publication gates, and enumerations that SHOULD reject
unknowns. This file collects the shape templates most used in this
monorepo.

Prerequisite: read [`closure-and-open-world.md`](closure-and-open-world.md)
first — it covers when SHACL is the right tool vs OWL.

## 1. Required-annotation shape

Every class must have `rdfs:label` and `skos:definition`. This shape is a
publication gate (severity ERROR).

```ttl
:RequiredAnnotationsShape a sh:NodeShape ;
  sh:targetClass owl:Class ;
  sh:property [
    sh:path rdfs:label ;
    sh:minCount 1 ;
    sh:datatype xsd:string ;
    sh:severity sh:Violation ;
    sh:message "Every class requires an rdfs:label." ;
  ] ;
  sh:property [
    sh:path skos:definition ;
    sh:minCount 1 ;
    sh:datatype xsd:string ;
    sh:severity sh:Violation ;
    sh:message "Every class requires a skos:definition (genus-differentia)." ;
  ] .
```

## 2. Cardinality on a property path

```ttl
:PerformanceEventShape a sh:NodeShape ;
  sh:targetClass :PerformanceEvent ;
  sh:property [
    sh:path :hasPerformer ;
    sh:minCount 1 ;
    sh:class :Performer ;
    sh:severity sh:Violation ;
    sh:message "A performance event must have at least one performer." ;
  ] .
```

## 3. Disjoint node shapes (XOR constraint)

Use when an individual must be of exactly one of several types.

```ttl
:AssetKindShape a sh:NodeShape ;
  sh:targetClass :EnergyAsset ;
  sh:xone (
    [ sh:class :GenerationAsset ]
    [ sh:class :StorageAsset ]
    [ sh:class :LoadAsset ]
  ) ;
  sh:message "An EnergyAsset must be exactly one of GenerationAsset, StorageAsset, or LoadAsset." .
```

## 4. SPARQL-based constraint (custom predicate check)

When the constraint cannot be expressed with property shapes alone:

```ttl
:NoSelfMappingShape a sh:NodeShape ;
  sh:targetClass owl:Class ;
  sh:sparql [
    sh:message "A class cannot have skos:exactMatch to itself." ;
    sh:prefixes [ sh:declare [ sh:prefix "skos" ; sh:namespace "http://www.w3.org/2004/02/skos/core#"^^xsd:anyURI ] ] ;
    sh:select """
      SELECT $this WHERE {
        $this skos:exactMatch $this .
      }
    """ ;
  ] .
```

## 5. Class range enforcement

```ttl
:HasUnitRangeShape a sh:NodeShape ;
  sh:targetClass :QuantityValue ;
  sh:property [
    sh:path qudt:hasUnit ;
    sh:class qudt:Unit ;
    sh:severity sh:Violation ;
    sh:message "QuantityValue.hasUnit must reference a qudt:Unit." ;
  ] .
```

## 6. Datatype enforcement

```ttl
:SOCRangeShape a sh:NodeShape ;
  sh:targetClass :StateOfCharge ;
  sh:property [
    sh:path :socPercent ;
    sh:datatype xsd:decimal ;
    sh:minInclusive 0.0 ;
    sh:maxInclusive 100.0 ;
    sh:severity sh:Violation ;
    sh:message "State-of-charge must be a decimal in [0, 100]." ;
  ] .
```

## 7. Scheme membership (SKOS concepts)

```ttl
:MapsToQUDTScheme a sh:NodeShape ;
  sh:targetClass qudt:Unit ;
  sh:property [
    sh:path skos:inScheme ;
    sh:hasValue qudt:UnitsScheme ;
    sh:severity sh:Warning ;
    sh:message "Every qudt:Unit should declare skos:inScheme qudt:UnitsScheme." ;
  ] .
```

## 8. Severity conventions

Use the authoritative severity levels. Pair with `--fail-on` in CI.

| Level | When | Build gate |
|-------|------|------------|
| `sh:Violation` | Publication-blocking: missing required annotation, wrong datatype, broken range | ERROR — `pyshacl --fail-on Violation` fails the build |
| `sh:Warning` | Recommended practice violated: missing `inScheme`, nonstandard label language | WARN — surfaces in report; does not block |
| `sh:Info` | Style/hygiene: suggested pattern not used | INFO — not displayed in default report |

## 9. Validation command

```bash
# Validate an ontology against its shapes.
uv run pyshacl -s ontologies/{name}/shapes/{name}-shapes.ttl \
               -f human \
               --inference rdfs \
               ontologies/{name}/{name}.ttl
```

`--inference rdfs` is the recommended minimum; use `owlrl` only when you
need a lightweight OWL RL materialization for the shape to see entailed
triples. Do NOT rely on pyshacl for full DL inference — run `robot reason`
first and validate the reasoned graph.

## 10. Pass/fail conventions in CI

The ontology CI job should:

1. Run `robot merge` + `robot reason` first.
2. Run `pyshacl -f human --fail-on Violation` on the reasoned graph.
3. Exit non-zero on Violation; exit zero with warnings recorded on Warning.
4. Upload the report as a build artifact for downstream inspection.

## 11. Anti-patterns

- **Shape without `sh:severity`.** Defaults to Violation but implicit —
  always state the severity.
- **Shape without `sh:message`.** A failure the author cannot read is a
  debug session waiting to happen.
- **SHACL where OWL is needed.** If the reasoner must classify instances,
  SHACL does not help. See `closure-and-open-world.md § 2`.
- **OWL universal where SHACL is needed.** See the same section.

## 12. Worked examples

- [`worked-examples/ensemble/architect.md`](worked-examples/ensemble/architect.md) — `VegetarianPizza` universal + SHACL count shape.
- [`worked-examples/microgrid/validator.md`](worked-examples/microgrid/validator.md) — `SolarPanel hasRatedPower` datatype + unit check.

## 13. References

- [SHACL REC](https://www.w3.org/TR/shacl/) — specification.
- [pyshacl](https://github.com/RDFLib/pySHACL) — the validator used here.
