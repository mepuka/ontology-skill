# Closure and the Open-World Assumption

**Referenced by:** `ontology-conceptualizer`, `ontology-architect`,
`ontology-validator`, `sparql-expert`.

OWL reasons under the **Open-World Assumption (OWA)**: what is not asserted
is unknown, not false. SHACL validates under the **Closed-World Assumption
(CWA)**: missing data is a violation. Mixing these up produces ontologies
that "pass the reasoner" but admit instances the modeler intended to
exclude. This file gives the decision rules and patterns.

## 1. OWA vs CWA quick table

| Concern | OWA (OWL reasoner) | CWA (SHACL / SPARQL tests) |
|---------|-------------------|-----------------------------|
| Missing value | Unknown | Violation |
| Unknown type | Class membership stays uncertain | Shape constraint violated |
| Enumeration coverage | Must add closure explicitly (e.g., `owl:oneOf` or `DisjointUnion`) | `sh:in` enforces the enumeration |
| Cardinality | Counts only asserted instances | Counts all instances in the data graph |
| Property domain/range | Entails type, does not reject | Rejects if type mismatch |
| Negative assertion | `owl:NegativePropertyAssertion` (rarely enough) | `sh:not` / `sh:disjoint` |
| Typical use | Subsumption, classification, consistency | Data-shape / publication validation |

## 2. When each assumption is the right tool

Use **OWA (OWL)** for:

- Subsumption (is `StringQuartet` a kind of `ChamberEnsemble`?)
- Consistency (are the disjointness axioms mutually satisfiable?)
- Classification (move individuals into their most specific inferred class)
- Term definition (genus-differentia, necessary-and-sufficient conditions)

Use **CWA (SHACL)** for:

- Data-shape validation on an ABox (every `SolarPanel` must have
  `qudt:hasUnit`).
- Publication gates (every class must have `rdfs:label` and
  `skos:definition`).
- Ensuring counts reflect actual data (every `PerformanceEvent` has
  exactly one `hasPerformer`).
- Enumerations where the set of valid values is fixed.

## 3. Closure axioms (the OWL side)

When you need OWL to reject "unknown" rather than "unassertable", add
explicit closure. Three common patterns:

### 3.1 `DisjointUnion` of subclasses

```ttl
:EnergyAsset owl:equivalentClass [
  a owl:Class ;
  owl:disjointUnionOf ( :GenerationAsset :StorageAsset :LoadAsset )
] .
```

Entails: every `EnergyAsset` is exactly one of the three subclasses, and
the three are pairwise disjoint. A reasoner can now rule out membership.

### 3.2 `owl:oneOf` for value-bounded enumerations

```ttl
:ChargeState a owl:Class ;
  owl:equivalentClass [ owl:oneOf ( :LowCharge :NominalCharge :HighCharge ) ] .
```

Closes the `ChargeState` extension to exactly three individuals.

### 3.3 `only` (universal restriction) with care

Example intent: a `VegetarianPizza` has *only* vegetarian toppings.

```ttl
:VegetarianPizza rdfs:subClassOf
  [ owl:onProperty :hasTopping ; owl:allValuesFrom :VegetarianTopping ] .
```

**Pitfalls:**

- Universal alone does not require any topping to exist (`allValuesFrom`
  is vacuously true with zero toppings).
- In OWL 2 EL, `allValuesFrom` is not supported — use a SHACL shape
  instead, or widen the profile.
- The axiom still relies on OWA: adding a `MeatTopping` asserted as
  `hasTopping` of a `VegetarianPizza` makes the ontology inconsistent;
  silence is not information.

## 4. SHACL shapes (the CWA complement)

For every "must have" intent captured in `docs/property-design.yaml`,
generate a SHACL shape — not only a universal restriction. The shape is
the one that will catch missing data at publication time.

```ttl
:PerformanceEventShape a sh:NodeShape ;
  sh:targetClass :PerformanceEvent ;
  sh:property [
    sh:path :hasPerformer ;
    sh:minCount 1 ;
    sh:class :Performer ;
    sh:message "Every performance event needs at least one performer." ;
  ] .
```

See [`shacl-patterns.md`](shacl-patterns.md) for the full pattern catalogue.

## 5. Anti-patterns

- **Universal as cardinality.** `allValuesFrom` does not assert existence;
  pair with `someValuesFrom` or a SHACL `sh:minCount`.
- **SHACL-only when OWL is required.** If the reasoner needs to infer
  class membership, a SHACL shape will not help — add a proper OWL axiom.
- **Open enumeration assumed closed.** Adding three individuals doesn't
  make a class enumerate to those three; use `owl:oneOf` or `DisjointUnion`.
- **Closure without disjointness.** `DisjointUnion` bundles both; plain
  `unionOf` + `SubClassOf` leaves the children overlapping.
- **Contradictory pairings.** `allValuesFrom :X` combined with
  `someValuesFrom :Y` where `X` and `Y` are disjoint makes the class
  unsatisfiable.

## 6. Decision flow

```
Intent captured in property-design.yaml →
  is this about inferring membership / classifying instances?
    yes → OWL axiom (closure, disjointness, equivalent class)
    no  → SHACL shape in shapes/{name}-shapes.ttl
  does the reasoner need to reject otherwise-consistent models?
    yes → closure axiom (DisjointUnion / oneOf / allValuesFrom)
    no  → leave OWA in place
  is the constraint about data presence / counts at publication time?
    yes → SHACL with severity
    no  → OWL only
```

## 7. Worked examples

- [`worked-examples/ensemble/architect.md`](worked-examples/ensemble/architect.md) — `VegetarianTopping` only-axiom with SHACL complement.
- [`worked-examples/microgrid/conceptualizer.md`](worked-examples/microgrid/conceptualizer.md) — `ChargeState` value partition with `owl:oneOf`.

## 8. References

- [OWL 2 Profiles](https://www.w3.org/TR/owl2-profiles/) — which closure
  constructs are available in each profile.
- [SHACL REC](https://www.w3.org/TR/shacl/) — shapes and data graph.
- [`shacl-patterns.md`](shacl-patterns.md) — concrete shape templates.
