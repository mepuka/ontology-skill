# Relation Semantics

**Referenced by:** `ontology-conceptualizer`, `ontology-architect`.

"Property" in OWL covers two very different constructs: **object properties**
(IRI → IRI) and **data properties** (IRI → literal). Choosing wrongly is
one of the most common modeling errors, and it is usually unrecoverable
without a migration. Alongside the choice, every property has semantic
characteristics (functional, transitive, inverse) whose mis-assignment
produces subtle reasoning errors.

## 1. Object property vs data property

| Test | Object | Data |
|------|--------|------|
| The target is identifiable and has its own attributes | yes | no |
| The target is a measurement / name / code / date | no | yes |
| The target participates in its own relations | yes | no |
| You will query "for each target, find X" | yes | no |
| You will query "count distinct values" and compare | no | yes |

Decision rule: **if the thing on the right side could be the subject of
another triple, it is an object property**. If it is a value, it is a
data property.

### Examples

| Intent | Property type | Why |
|--------|---------------|-----|
| Violin `isMadeOf` Wood | object | `Wood` has its own properties (density, subclass, etc.) |
| Violin `hasSerialNumber` "V-12345" | data | A string identifier. |
| PerformanceEvent `hasPerformer` Musician | object | A Musician has their own relations. |
| PerformanceEvent `hasDate` "2026-05-04" | data | A literal date. |
| SolarPanel `hasRatedPower` qudt:QuantityValue | object | The quantity value is an individual with a unit. |
| SolarPanel `ratingKW` 4.5 | data | A decimal; loses unit — prefer the object-valued form. |

Note the last row: for physical quantities, prefer an object property
pointing to a `qudt:QuantityValue` individual that carries the unit.
`hasRatedPower` is an object property; the value "4.5 kW" is a structured
individual. This is the `ObservedQuantity` pattern from
[`pattern-catalog.md`](pattern-catalog.md) (Wave 3).

## 2. Relation categories

Borrowed from BFO / RO semantics:

| Category | What it relates | Typical properties |
|----------|-----------------|--------------------|
| **Intrinsic** | A continuant to one of its inhering qualities | `hasQuality`, `bearerOf` |
| **Extrinsic** | A continuant to something outside it | `locatedIn`, `adjacentTo`, `memberOf` |
| **Meronymic (part-whole)** | A whole to a part | `hasPart`, `hasProperPart`, `partOf` |
| **Participation** | An occurrent to a continuant that participates | `hasParticipant`, `hasAgent`, `hasObject` |
| **Derivation** | Continuant → continuant across a process | `derivedFrom`, `produces` |
| **Spatio-temporal** | Position in space / time | `hasTemporalPart`, `locatedIn` |
| **Realization** | Role/disposition realized by a process | `realizes` (process → role/disposition) |

When designing a new property, name its category. This selects the
correct parent property (usually an RO term) and the right characteristics.

## 3. Relations Ontology (RO) cheat sheet

Import from RO (`obo:RO_*`) rather than inventing new top-level properties.

| Intent | RO term |
|--------|---------|
| Part-whole (general) | `RO:0001000` `derives from` (for continuants); `BFO:0000050` `part of` |
| Participant | `RO:0000056` `participates in` |
| Has participant | `RO:0000057` `has participant` |
| Realizes (process → role) | `RO:0000056` / `BFO:0000055` |
| Bearer of (continuant → quality) | `RO:0000053` `bearer of` |
| Inheres in (quality → continuant) | `RO:0000052` `inheres in` |
| Has role | `RO:0000087` `has role` |
| Has member (collection) | `RO:0002351` `has member` |
| Located in | `RO:0001025` `located in` |
| Capable of | `RO:0002215` `capable of` |

Browse [Relation Ontology](http://obofoundry.org/ontology/ro.html) for
the full catalogue. `runoak search` is the fast way to find a candidate.

## 4. Characteristics matrix

Set property characteristics only when the semantics demand it. Each
adds entailments; getting one wrong produces ghost entailments.

| Characteristic | Meaning | Ghost entailment if wrong |
|----------------|---------|---------------------------|
| `FunctionalObjectProperty` | At most one value per subject | If not actually functional, reasoner will merge individuals via owl:sameAs |
| `InverseFunctionalObjectProperty` | At most one subject per value | Same, in reverse |
| `TransitiveObjectProperty` | If a R b and b R c then a R c | Explodes the deductive closure — don't set on `part of` unless your query logic expects it |
| `SymmetricObjectProperty` | If a R b then b R a | Every statement is bidirectional |
| `AsymmetricObjectProperty` | If a R b then not b R a | Reasoner will reject any data row that contradicts |
| `ReflexiveObjectProperty` | a R a for every a in the domain | Rarely correct; most relations aren't reflexive |
| `IrreflexiveObjectProperty` | Never a R a | Usually safe; enforces no self-loop |

### Quick rules

- Default: **no characteristic set**. Add only with a written justification
  in `docs/property-design.yaml`.
- `part of` and `has part` are **transitive**, but you usually want a
  direct-parent variant (`directly part of`) for navigation; don't rely
  on transitive closure alone.
- `inverseOf` is a characteristic *pair* between properties (e.g.,
  `hasPart inverseOf partOf`). Defining both and asserting the inverse
  makes the reasoner materialize both directions — cost is doubled
  storage, benefit is symmetric query.

## 5. Domain and range

`rdfs:domain` and `rdfs:range` are *entailment* axioms, not constraints:

- Setting `hasPerformer rdfs:domain Performance` entails that anything
  with an asserted `hasPerformer` link becomes a `Performance`. If the
  subject is actually a non-`Performance`, classification fails.
- This is **not** the same as "must be". For constraint semantics, use
  SHACL (see [`shacl-patterns.md`](shacl-patterns.md)).

Use `rdfs:domain` / `rdfs:range` only when the entailment is desired
(classification). Use SHACL when you want a validation error instead.

## 6. Property chains

Object-property chains (`owl:propertyChainAxiom`) let you compose new
relations:

```ttl
:locatedIn owl:propertyChainAxiom (:hasPart :locatedIn) .
# If X hasPart Y and Y locatedIn Z, then X locatedIn Z.
```

Useful for:

- Propagating `locatedIn` along part-whole.
- Propagating role participation through sub-processes.

Note: chains are OWL-2-EL-compatible *under restrictions* — the chain
must be simple (no property occurs twice). See
[`owl-profile-playbook.md`](owl-profile-playbook.md) § 3.

## 7. Anti-patterns

- **Object property where data property is correct.** Results in phantom
  individuals and broken count queries.
- **Data property where object property is correct.** Results in lossy
  modeling; cannot relate the target to anything.
- **Misnamed direction.** `partOf` with a `rdfs:domain Whole` is almost
  always wrong (the domain should be the `Part`).
- **Transitive by default.** Never mark a property transitive without
  checking that `a R a R a R a` is the intended entailment.
- **Inverse pair without `owl:inverseOf`.** Silently asymmetric reasoning.
- **Missing characteristics for real-world constraints.** A
  `hasBirthDate` without `Functional` admits multiple birth dates.

## 8. Worked examples

- [`worked-examples/ensemble/conceptualizer.md`](worked-examples/ensemble/conceptualizer.md) — `hasMember`, `hasPerformer`, `hasInstrument` property design.
- [`worked-examples/microgrid/architect.md`](worked-examples/microgrid/architect.md) — property chain `hasPart ∘ locatedIn → locatedIn`.

## 9. References

- [OWL 2 Primer § Object and Data Properties](https://www.w3.org/TR/owl2-primer/)
- [Relation Ontology](http://obofoundry.org/ontology/ro.html)
- [`shacl-patterns.md`](shacl-patterns.md) — SHACL for constraint semantics.
