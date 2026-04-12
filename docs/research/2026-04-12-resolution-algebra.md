# Resolution Algebra: Formalizing the Skygest Resolution Kernel

**Date**: 2026-04-12
**Status**: Working research document
**Context**: skygest-energy-vocab DCAT structural extension + Stage 2 resolution kernel

## Overview

The Skygest resolution kernel resolves natural-language chart text into
structured entity references (Variable, Dataset, Agent). This document
formalizes the mathematical structure of that resolution process, grounded
in the concrete ontology (skygest-energy-vocab) and TypeScript implementation
(skygest-cloudflare).

The system is a **three-layer resolution architecture**: a lexicon (weighted
relation), a faceted constraint space (product lattice), and a typed entity
graph (DCAT catalog). Each layer has distinct mathematical structure and
distinct operations.

## Layer 1: The Lexicon — a weighted relation

### Definition

Let **S** be the set of normalized surface forms (strings after NFKC
normalization, whitespace collapse, and lowercasing).

Let **F** = F₁ + F₂ + ... + F₇ be the disjoint union of the seven facet
value sets, where:

| i | Fᵢ | ConceptScheme |
|---|-----|---------------|
| 1 | MeasuredProperty values | MeasuredPropertyScheme |
| 2 | DomainObject values | DomainObjectScheme |
| 3 | TechnologyOrFuel values | TechnologyOrFuelScheme |
| 4 | StatisticType values | StatisticTypeScheme |
| 5 | Aggregation values | AggregationScheme |
| 6 | UnitFamily values | UnitFamilyScheme |
| 7 | PolicyInstrument values | PolicyInstrumentScheme |

The **lexicon** is a relation:

```
L  :  S  →  P(F)
```

where P(F) is the powerset of F. Each surface form maps to one or more
facet values, each tagged with its dimension index.

### Properties

- L is many-to-many: multiple surface forms can map to the same facet value,
  and one surface form can map to multiple facet values.
- Each entry in the JSON vocabulary files is a witness to a single element
  of L: `SurfaceFormEntry ~ (s ∈ S, f ∈ Fᵢ, provenance, timestamp)`.
- The normalization function `norm : String → S` is idempotent:
  `norm(norm(x)) = norm(x)`.

### Compound concepts

A **compound concept** is a surface form s where |L(s)| > 1 and L(s) spans
multiple dimension indices. Example:

```
L("henry hub") = { (domainObject, NaturalGas),
                   (measuredProperty, Price),
                   (aggregation, Spot) }
```

This is a single string that projects onto 3 dimensions simultaneously.
In faceted classification this is called a **synthesized subject**. The
current TypeScript architecture does not support compound concepts — each
`SurfaceFormEntry` lives in exactly one scheme.

### TypeScript mapping

| Formal | TypeScript |
|--------|-----------|
| S | `normalizedSurfaceForm` field |
| F | Canonical values across all JSON vocabulary files |
| L(s) | `vocabulary.match*(text)` — per-scheme lookup |
| norm | `normalizeLookupText()` in `normalize.ts` |
| SurfaceFormEntry | `SurfaceFormEntryAny` / `SurfaceFormEntry<Canonical>` |

## Layer 2: The Product Lattice — constraint assembly

### Definition

The **variable space** is the product:

```
V  =  (F₁ ∪ {⊥}) × (F₂ ∪ {⊥}) × ... × (F₇ ∪ {⊥})
```

where ⊥ ("bottom" / unspecified) represents an unassigned facet. Each
factor Fᵢ ∪ {⊥} is a flat lattice where ⊥ ≤ everything and all elements
of Fᵢ are incomparable. V is a **product lattice**.

The ordering on V is componentwise:

```
v₁ ≤ v₂   iff   for all i:  v₁[i] = ⊥  or  v₁[i] = v₂[i]
```

### Key operations

**Projection**: For a facet value f ∈ Fᵢ, define project(f) as the element
of V that is ⊥ everywhere except position i:

```
project(f ∈ Fᵢ) = (⊥, ..., ⊥, f, ⊥, ..., ⊥)
                              ↑ position i
```

**Join** (least upper bound): For two partial assignments v₁, v₂ ∈ V:

```
join(v₁, v₂)[i] =
  | v₁[i]     if v₂[i] = ⊥
  | v₂[i]     if v₁[i] = ⊥
  | v₁[i]     if v₁[i] = v₂[i]
  | CONFLICT   if v₁[i] ≠ v₂[i] and neither is ⊥
```

**Facet decomposition**: The core resolution operation:

```
decompose(text) = join { project(f) | s ∈ matches(text), f ∈ L(s) }
```

**Specificity**: Count of non-⊥ dimensions:

```
specificity(v) = |{ i : v[i] ≠ ⊥ }|
```

**Subsumption**: v₁ subsumes v₂ if v₁ ≤ v₂ (v₁ is more general):

```
subsumes(general, specific) = general ≤ specific
```

**Resolvability gate** (from SHACL): A partial assignment is resolvable
only if the required dimensions are non-⊥:

```
resolvable(v) = v[1] ≠ ⊥ ∧ v[4] ≠ ⊥    (measuredProperty, statisticType)
```

### TypeScript mapping

| Formal | TypeScript |
|--------|-----------|
| V | `PartialVariableShape` (all optionalKey fields) |
| ⊥ | `undefined` (absent key) |
| project(f) | Constructing a `PartialVariableShape` with one field set |
| join(v₁, v₂) | **GAP** — implicit in lane logic, no explicit function |
| specificity(v) | **GAP** — counted ad-hoc, not a named operation |
| subsumes(v₁, v₂) | **GAP** — not implemented |
| resolvable(v) | **GAP** — not implemented as a predicate |

## Layer 3: The DCAT Graph — typed navigation

### Definition

Define a schema category **C** with:

- **Objects**: {Distribution, Dataset, Agent, Variable, ConceptScheme, Concept}
- **Morphisms** (the DCAT/sevocab relations):
  - `datasetOf : Distribution → Dataset`
  - `publisherOf : Dataset → Agent`
  - `hasVariable : Dataset → Variable`
  - `facetᵢ : Variable → Concept` (for each dimension i)
  - `inScheme : Concept → ConceptScheme`

The registry is a **functor R : C → FinSet** — it assigns to each object a
finite set of entities, and to each morphism a function between those sets.

### Path composition

Resolution is path composition through R:

```
facet match → Variable → Dataset → Agent
```

Forward navigation (top-down): Given a Variable, follow hasVariable⁻¹ to
find its Dataset, then publisherOf to find its Agent.

Inverse navigation (bottom-up): Given an Agent (from post source URL),
follow publisherOf⁻¹ to find its Datasets, then hasVariable to find
candidate Variables.

### TypeScript mapping

| Formal | TypeScript |
|--------|-----------|
| R(Distribution) | Distribution entities in registry |
| R(Dataset) | Dataset entities in registry |
| R(Agent) | Agent entities in registry |
| R(Variable) | Variable entities in registry |
| R(publisherOf) | `publisherAgentId` foreign key on Dataset |
| R(hasVariable) | Variable's implicit Dataset membership |
| R(datasetOf) | `datasetId` foreign key on Distribution |
| Inverse navigation | **GAP** — no pre-built inverse indices |

## Ontology Change Taxonomy

Every modification to the ontology falls into one of three categories,
each with a formally distinct effect on the resolution space.

### Type 1: New Leaf (widen a domain)

**Definition**: Extend Fᵢ to Fᵢ' = Fᵢ ∪ {new_value}.

**Effect on V**: The product lattice gains new points — V' is strictly
larger than V.

**Effect on L**: New entries mapping surface forms to new_value.

**Effect on C**: No change to morphisms.

**Example**: Adding "Geothermal" to TechnologyOrFuelScheme.

**TypeScript**: Add entries to JSON vocabulary file. Extend enum type
if the facet uses a closed `Schema.Literals` array.

### Type 2: New Path (add edges to the lexicon)

**Definition**: Extend L to L' by adding new pairs (s, f).

**Effect on V**: No change — the lattice itself doesn't change.

**Effect on L**: New edges in the bipartite graph between S and F.

**Sub-cases**:
- **Simple mapping**: One surface form → one facet value in one dimension.
  Adds one edge.
- **Compound concept**: One surface form → values in multiple dimensions.
  Adds multiple edges from one s. Equivalent to defining a "macro" that
  fills multiple lattice positions at once.

**Example (simple)**: Adding "natgas" as an altLabel for NaturalGas.

**Example (compound)**: Adding "Henry Hub" mapping to
{domainObject: NaturalGas, measuredProperty: Price, aggregation: Spot}.

**TypeScript**: Add entries to JSON vocabulary files. For compound concepts,
the current architecture requires adding the surface form to each relevant
scheme independently — no single-entry compound concept representation
exists (gap).

### Type 3: New Dimension (extend the product)

**Definition**: Add a new factor to the product: V' = V × (F₈ ∪ {⊥}).

**Effect on V**: The lattice gains a new axis — dimensionality increases.

**Effect on L**: New entries mapping surface forms to F₈ values.

**Effect on C**: New morphism facet₈ : Variable → Concept.

**Example**: Adding "geographicRegion" as an 8th facet dimension.

**TypeScript**: Schema migration — new optionalKey field on
PartialVariableShape, new JSON vocabulary file, new qb:DimensionProperty
in the ontology.

## Identified Gaps

### Gap 1: No explicit lattice algebra

`PartialVariableShape` represents lattice elements, but the operations
`join()`, `subsumes()`, `specificity()`, and `resolvable()` are not
defined as functions. They are implicit in application logic.

**Recommendation**: Define these as pure functions on `PartialVariableShape`.

### Gap 2: No compound concept type

A compound concept like "Henry Hub" that simultaneously constrains
domainObject and technologyOrFuel has no first-class representation. Each
SurfaceFormEntry belongs to exactly one scheme.

**Recommendation**: Either a cross-scheme surface form table, or a
`CompoundSurfaceForm` type that maps one string to a
`PartialVariableShape` directly.

**Ontology representation**: A SKOS Concept with `skos:exactMatch` or
`skos:closeMatch` to an external concept that carries multi-dimensional
semantics. Or a sevocab concept that participates in multiple schemes
via `skos:inScheme`.

### Gap 3: No conflict/ambiguity model

When two surface forms assign conflicting values to the same dimension
(join is undefined), or when the partial assignment matches multiple
registry Variables equally well, the type system does not distinguish
these failure modes.

**Recommendation**: Distinguish dimensional conflicts (contradictory
evidence within V) from structural ambiguity (multiple valid paths
through R).

### Gap 4: No SSSOM bridge at runtime

SSSOM mappings to external vocabularies (OEO, Wikidata, UCUM) are
provenance tags on surface form entries, not typed edges in L.

**Recommendation**: When adding SSSOM mappings, propagate them as typed
edges in L with confidence scores, not just provenance labels.

### Gap 5: No inverse navigation indices

The DCAT graph is navigated top-down (Variable → Dataset → Agent), but
disambiguation often needs bottom-up queries: "given this Agent, what
Variables appear in its Datasets?"

**Recommendation**: Pre-build inverse indices during registry
initialization.

## Lattice Operations: Dual Representation (Ontology ↔ TypeScript)

The lattice operations are the **proof layer** — the bridge between the
ontology's formal model and the TypeScript kernel's runtime behavior. Each
operation has two representations that must be provably equivalent: a
SPARQL query (or OWL axiom) on the ontology side, and a pure function on
the TypeScript side.

If the ontology can answer a composition question via SPARQL, and the
TypeScript can answer the same question via a pure function, and both give
the same result, the loop is closed.

### Operation 1: `join(v₁, v₂)` — combine two partial assignments

The most fundamental operation. Every time the kernel matches a surface
form, it joins a new projection into the existing partial assignment.

**Ontology side**: The OWL `maxQualifiedCardinality 1` axiom on each facet
dimension guarantees the join is well-defined — a Variable cannot have two
values for the same dimension. This is the constraint that makes join a
partial function (it can fail with a conflict).

**TypeScript side**:

```typescript
const FACET_KEYS = [
  "measuredProperty", "domainObject", "technologyOrFuel",
  "statisticType", "aggregation", "unitFamily", "policyInstrument"
] as const;

type JoinResult =
  | { _tag: "ok"; value: PartialVariableShape }
  | { _tag: "conflict"; dimensions: string[] };

function joinPartials(
  a: PartialVariableShape,
  b: PartialVariableShape
): JoinResult {
  const result: Record<string, string | undefined> = {};
  const conflicts: string[] = [];

  for (const key of FACET_KEYS) {
    const av = a[key], bv = b[key];
    if (av !== undefined && bv !== undefined && av !== bv) {
      conflicts.push(key);
    } else {
      result[key] = av ?? bv;
    }
  }

  return conflicts.length > 0
    ? { _tag: "conflict", dimensions: conflicts }
    : { _tag: "ok", value: result as PartialVariableShape };
}
```

**Equivalence proof**: The OWL axiom and the TypeScript conflict check
express the same constraint — one in open-world logic, one in closed-world
code. The ontology proves the constraint is correct; the TypeScript
enforces it at runtime.

**Runtime composition**: join is associative and commutative (order of
surface form matches doesn't matter). This means the kernel can process
matches in any order and get the same partial assignment.

### Operation 2: `subsumes(general, specific)` — candidate filtering

The candidate filtering operation. Given a partial assignment from
decomposition, check it against registry Variables to find matches.

**Ontology side**: Direct SPARQL query. The partial assignment becomes a
WHERE clause — each non-⊥ dimension adds a triple pattern:

```sparql
# "Find Variables matching {measuredProperty: Price, technologyOrFuel: NaturalGas}"
SELECT ?variable WHERE {
  ?variable a sevocab:EnergyVariable ;
            sevocab:measuredProperty sevocab:Price ;
            sevocab:technologyOrFuel sevocab:NaturalGas .
}
```

Dimensions that are ⊥ are simply absent from the query — the open-world
assumption does the right thing (missing = don't care).

**TypeScript side**:

```typescript
function subsumes(
  general: PartialVariableShape,
  specific: PartialVariableShape
): boolean {
  return FACET_KEYS.every(key =>
    general[key] === undefined || general[key] === specific[key]
  );
}

// Usage: filter registry Variables
const candidates = registry.variables.filter(v =>
  subsumes(partial, v.facets)
);
```

**Equivalence**: The SPARQL query and `subsumes()` return the same set of
Variables. Open-world "missing = unknown" and closed-world
"undefined = wildcard" produce identical filtering behavior when the
registry is complete (all Variables have their facets fully specified).

### Operation 3: `specificity(v)` — resolution quality scoring

Count of non-⊥ dimensions. A partial assignment with 4 filled dimensions
is a stronger signal than one with 1.

**Ontology side**:

```sparql
SELECT ?variable (COUNT(?facetValue) AS ?specificity) WHERE {
  ?variable a sevocab:EnergyVariable .
  VALUES ?facetProp {
    sevocab:measuredProperty sevocab:domainObject
    sevocab:technologyOrFuel sevocab:statisticType
    sevocab:aggregation sevocab:unitFamily
    sevocab:policyInstrument
  }
  OPTIONAL { ?variable ?facetProp ?facetValue }
}
GROUP BY ?variable
```

**TypeScript side**:

```typescript
function specificity(v: PartialVariableShape): number {
  return FACET_KEYS.filter(key => v[key] !== undefined).length;
}
```

**Usage in ranking**: When multiple candidates subsume the partial
assignment, rank by specificity. Higher specificity = more constrained =
less likely to be a false positive. Two candidates with equal specificity
are genuinely ambiguous and need Layer 3 (structural) disambiguation.

### Operation 4: `resolvable(v)` — the SHACL gate

Derived directly from the SHACL shape. The ontology declares
measuredProperty and statisticType as required (minCount 1). If the
partial assignment is ⊥ on either, the kernel should not emit a Variable
match.

**Ontology side** — the SHACL shape IS the definition:

```turtle
sevocab-shapes:EnergyVariableShape sh:property [
    sh:path sevocab:measuredProperty ;
    sh:minCount 1
] , [
    sh:path sevocab:statisticType ;
    sh:minCount 1
] .
```

**TypeScript side**:

```typescript
function resolvable(v: PartialVariableShape): boolean {
  return v.measuredProperty !== undefined
      && v.statisticType !== undefined;
}
```

**Eval impact**: This operation directly addresses the **wrong-new-match**
bucket (22 cases in the latest eval). The kernel currently has no
resolvability gate — it will emit a Variable match even if it only matched
`unitFamily: Energy`. With `resolvable()`, weak matches get filtered
before they become false positives.

### Full Composition: The Resolution Pipeline

The four operations compose into the complete deterministic resolution path:

```
text
  → matches(text)                        // Layer 1: lexicon lookup
  → project each match to V              // Layer 2: project to lattice
  → join all projections                 // Layer 2: compose constraints
  → check resolvable(partial)            // Layer 2: SHACL gate
       if false → escalate to Stage 3
  → filter registry by subsumes()        // Layer 2→3: lattice meets graph
  → rank candidates by specificity()     // Layer 2: scoring
  → if single candidate → resolved
  → if tied → traverse DCAT chain        // Layer 3: structural disambiguation
       Agent match → narrow candidates
  → if still tied → escalate to Stage 3
```

Each step has:
- A formal definition (lattice/graph operation)
- An ontology-side CQ or SHACL shape that tests it
- A TypeScript pure function that implements it
- A provable equivalence between the ontology and TypeScript representations

### Why This Matters for the Deterministic Resolver

The lattice operations make the resolution kernel **algebraically
predictable**. Given the same lexicon L and registry R, the same input
text always produces the same output — no ML models, no learned
parameters, no stochastic behavior.

More importantly, every component is **independently testable**:
- Lexicon correctness: CQ tests on surface form coverage
- Join correctness: conflict detection tests
- Subsumption correctness: SPARQL ↔ TypeScript equivalence tests
- Gate correctness: SHACL shape ↔ `resolvable()` equivalence
- Ranking correctness: specificity comparison tests

When the eval shows a wrong-new-match, you can trace it back to exactly
which operation produced the error: was it a bad lexicon entry (Layer 1),
a missing resolvability gate (Layer 2), or a missing structural signal
(Layer 3)?

## Terminology Reference

| Term | Definition | Context |
|------|-----------|---------|
| Faceted information space | The product lattice V | Standard term from information retrieval (Ranganathan) |
| Facet decomposition | L followed by join | The core resolution operation |
| Partial assignment | Element of V with ⊥ components | Not "partial variable" — it is a complete constraint |
| Subsumption | v₁ ≤ v₂ in the lattice | Standard DL term |
| Compound concept | Surface form spanning multiple dimensions | Also called "synthesized subject" in faceted classification |
| Specificity | Count of non-⊥ dimensions | Resolution quality metric |
| Resolution | Full pipeline from text to entity identity | Entity resolution sense |
| Evidence accumulation | Collecting corroborating signals | Dempster-Shafer territory for principled combination |
| Schema category | The typed entity graph C | Objects = entity types, morphisms = relationships |
| Registry functor | R : C → FinSet | Maps schema to actual data |
