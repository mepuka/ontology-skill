# OWL 2 Profile Playbook

**Referenced by:** `ontology-scout`, `ontology-architect`, `ontology-validator`,
`ontology-conceptualizer` (via axiom-plan review).

An OWL 2 profile is a syntactic subset of OWL 2 DL that trades expressivity
for reasoning efficiency. Choosing the wrong profile — or running a reasoner
that silently skips disallowed constructs — is one of the highest-cost
formalization failures. This file is the decision surface.

## 1. Profile decision matrix

Choose a profile before designing axioms, not after.

| Profile | Best when | Reasoner | Trade-off |
|---------|-----------|----------|-----------|
| **EL** (OWL 2 EL) | Large class hierarchies with subsumption as the main reasoning task (SNOMED-style). | ELK (fast, polytime). | No disjunction, no inverseOf, no qualified cardinalities, no negation, no universal restrictions. |
| **QL** (OWL 2 QL) | Query-rewriting over relational back-ends; ABox queries dominate. | OWL 2 QL reasoners (e.g., Ontop). | No nominals, no functional properties, no cardinalities. |
| **RL** (OWL 2 RL) | Rule-based materialization (DL-safe rules); triple-store inference. | RL reasoners (OWLIM/GraphDB, Pellet-RL). | No disjunction inside class expressions; limited use of existentials. |
| **DL** (OWL 2 DL) | Full expressivity needed (qualified cardinality, disjointness with negation, nominals). | HermiT, Pellet, Openllet. | Slower; some constructs make reasoning exponential. |

Default for this monorepo's ontologies: **DL** unless a justified reason
to narrow (documented in `docs/scope.md § Profile`).

## 2. What each profile silently skips

When a reasoner runs outside its profile, it does not error — it ignores
axioms it cannot handle. This leads to "clean reasoner run, wrong
entailments" — the hardest class of bug.

### ELK (EL) skips

- Qualified cardinality restrictions (e.g., `hasMember exactly 4 Musician`).
- `ObjectComplementOf`, `DisjointUnionOf`, `InverseObjectProperties`.
- Universal restrictions (`allValuesFrom`).
- Data-property ranges with complex datatypes.
- Nominal-based class definitions using `ObjectOneOf` with >1 individual in
  positions EL disallows.

### QL skips

- `FunctionalObjectProperty`, `InverseFunctionalObjectProperty`.
- Nominals.
- Cardinality restrictions of any kind.
- Disjointness between class expressions (only between named classes).

### RL skips

- Existential on RHS in most contexts.
- Certain cardinality forms.
- Disjunctive class expressions in positive position.

### HermiT / Pellet / Openllet (DL)

These are complete for OWL 2 DL. If the ontology is DL-valid, they compute
the correct entailments (subject to time and memory). They do NOT silently
skip; they reject with a profile violation or fail with a clear error.

## 3. Construct-support matrix (architect quick-reference)

Reference when designing the axiom plan in `docs/axiom-plan.yaml`.

| Construct | EL | QL | RL | DL |
|-----------|:--:|:--:|:--:|:--:|
| `SubClassOf` | Y | Y | Y | Y |
| `EquivalentClasses` | Y | Y | Y | Y |
| `DisjointClasses` (named) | Y | Y | Y | Y |
| `DisjointUnion` | N | N | N | Y |
| `ObjectIntersectionOf` | Y | Y | Y | Y |
| `ObjectUnionOf` | N | N | partial | Y |
| `ObjectComplementOf` | N | N | partial | Y |
| `ObjectSomeValuesFrom` | Y | Y | Y | Y |
| `ObjectAllValuesFrom` | N | N | partial | Y |
| `ObjectHasValue` | Y | Y | Y | Y |
| `ObjectMinCardinality` | N | N | partial | Y |
| `ObjectMaxCardinality` | N | N | partial | Y |
| `ObjectExactCardinality` | N | N | partial | Y |
| Qualified cardinality (e.g., `max 3 SpecificClass`) | N | N | N | Y |
| `FunctionalObjectProperty` | partial | N | Y | Y |
| `InverseFunctionalObjectProperty` | N | N | Y | Y |
| `TransitiveObjectProperty` | Y | partial | Y | Y |
| `SymmetricObjectProperty` | N | Y | Y | Y |
| `AsymmetricObjectProperty` | N | Y | Y | Y |
| `ObjectPropertyChain` (`owl:propertyChainAxiom`) | Y | N | Y | Y |
| `ObjectInverseOf` | N | Y | Y | Y |
| `ObjectOneOf` (nominals) | partial | N | partial | Y |
| Datatype restrictions | partial | Y | Y | Y |

`partial` = allowed under narrow syntactic conditions; check the profile
spec or run `robot validate-profile`.

## 4. How to pick a reasoner

```bash
# If profile targets EL:
.local/bin/robot reason --reasoner ELK --input edit.ttl --output reasoned.ttl

# If any DL-only construct exists:
.local/bin/robot reason --reasoner HermiT --input edit.ttl --output reasoned.ttl

# For release gates on non-EL ontologies, HermiT is the default.
# Pellet/Openllet are alternatives when HermiT is too slow or doesn't
# support a specific datatype/rule form.
```

Rule of thumb: if any row of the construct-support matrix shows `N` or
`partial` for ELK in your axiom plan, you need HermiT at least for
release.

## 5. Preflight: validate before reasoning

Always merge the edit graph with its imports before validating the profile.
Unmerged validation produces false positives:

```bash
# Merge first — imports matter for profile validation.
.local/bin/robot merge --input edit.ttl --output /tmp/merged.ttl

# Then validate against the target profile.
.local/bin/robot validate-profile --profile DL --input /tmp/merged.ttl
# or --profile EL, --profile QL, --profile RL
```

This pattern is encoded in `reference_robot_dl_profile_check` in the
workspace memory — merge first, then `validate-profile`; `robot measure`
on unmerged sources will report spurious violations.

## 6. Recovery workflow on profile violation

If `robot validate-profile --profile EL` fails and EL is required:

1. **Classify the violation.** Look for one of: qualified cardinality,
   universal restriction, disjunction, inverse, nominal, functional property.
2. **Refactor, don't widen silently.** Prefer:
   - Replace qualified cardinality with a value-partition + role-chain design.
   - Replace universal with a SHACL shape (closure via CWA, not OWL).
   - Replace disjunction with an enumeration class subclass structure.
3. **If refactor not feasible, widen profile.** Update `docs/scope.md §
   Profile` and run release-gate reasoner (HermiT) from that point on.
4. **Log a failure-ledger entry** per `llm-verification-patterns.md § 6`
   if the violation originated from an LLM-produced axiom.

Raising the violation as a loopback routes to `ontology-architect`
(`failure_type: profile_violation`) per
[`iteration-loopbacks.md`](iteration-loopbacks.md).

## 7. Worked examples

See (Wave 4):

- [`worked-examples/ensemble/architect.md`](worked-examples/ensemble/architect.md) — `StringQuartet hasMember exactly 4 Musician`: why ELK silently ignores it and why HermiT is required.
- [`worked-examples/microgrid/architect.md`](worked-examples/microgrid/architect.md) — property chain `hasPart ∘ locatedIn → locatedIn` stays EL-valid; EL is a viable target.

## 8. References

- [OWL 2 Profiles W3C REC](https://www.w3.org/TR/owl2-profiles/) — authoritative spec.
- [ELK documentation](https://liveontologies.github.io/elk-reasoner/) — EL reasoner.
- [ROBOT validate-profile](http://robot.obolibrary.org/validate-profile) — the command.
