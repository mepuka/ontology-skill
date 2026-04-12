# Effect Algebra Mapping: Lattice Operations in TypeScript + Effect

**Date**: 2026-04-12
**Status**: Advisory document
**Prerequisite reading**: resolution-algebra.md, text-ops-and-evidence-combination.md
**Audience**: Grad students implementing the lattice algebra layer in skygest-cloudflare

---

## 1. Lattice Operations with Exact Effect Type Signatures

The four operations from the resolution algebra each have a distinct computational character. The type signatures below use the actual domain types from `src/domain/`.

```typescript
import { Array, Either, Option, Predicate, pipe } from "effect";
import type { PartialVariableShape } from "../domain/stage2Core";
import type { Variable } from "../domain/data-layer/variable";

// The facet keys that participate in the lattice.
// Excludes label, definition, basis, fixedDims -- these are metadata, not lattice dimensions.
const FACET_KEYS = [
  "measuredProperty", "domainObject", "technologyOrFuel",
  "statisticType", "aggregation", "unitFamily", "policyInstrument"
] as const;

type FacetKey = (typeof FACET_KEYS)[number];
```

**join** -- partial function, returns Either:

```typescript
type DimensionalConflict = {
  readonly _tag: "DimensionalConflict";
  readonly dimensions: ReadonlyArray<FacetKey>;
};

const join: (
  a: PartialVariableShape,
  b: PartialVariableShape
) => Either.Either<PartialVariableShape, DimensionalConflict>
```

**subsumes** -- total, pure predicate:

```typescript
const subsumes: (
  general: PartialVariableShape,
  specific: PartialVariableShape
) => boolean
```

**specificity** -- total, pure measure:

```typescript
const specificity: (v: PartialVariableShape) => number
```

**resolvable** -- total, acts as a Refinement (type guard):

```typescript
type ResolvablePartial = PartialVariableShape & {
  readonly measuredProperty: string;
  readonly statisticType: string;
};

const resolvable: Predicate.Refinement<PartialVariableShape, ResolvablePartial>
```

The key insight: `join` is the only operation that can fail, so it is the only one that needs `Either`. The others are pure functions on data. This is a categorical distinction -- `join` is a partial function on the lattice (the join of two incompatible elements is undefined), while the others are total.

---

## 2. Predicate Combinators

Effect provides `Predicate.and`, `Predicate.or`, `Predicate.compose`, and `Predicate.struct` as first-class combinator operations. These compose predicates while preserving Refinement type-narrowing. Here is how the resolution predicates compose using them.

**Standalone predicate functions** (not methods on a class):

```typescript
import { Predicate } from "effect";

// --- Atomic predicates ---

const resolvable: Predicate.Refinement<PartialVariableShape, ResolvablePartial> =
  (v): v is ResolvablePartial =>
    v.measuredProperty !== undefined && v.statisticType !== undefined;

const hasMinSpecificity = (n: number): Predicate.Predicate<PartialVariableShape> =>
  (v) => specificity(v) >= n;

const hasNoMismatch = (
  partial: PartialVariableShape
): Predicate.Predicate<PartialVariableShape> =>
  (candidate) => FACET_KEYS.every(key =>
    partial[key] === undefined ||
    candidate[key] === undefined ||
    partial[key] === candidate[key]
  );

// --- Composed predicates via Effect's Predicate module ---

// Compound gate: resolvable AND at least 2 filled dimensions
const strongCandidate = Predicate.and(resolvable, hasMinSpecificity(2));

// Subsumption as a partially-applied filter predicate
const subsumedBy = (partial: PartialVariableShape): Predicate.Predicate<PartialVariableShape> =>
  (candidate) => subsumes(partial, candidate);

// Exclusion: keep candidates with no dimensional conflicts
const compatibleWith = (partial: PartialVariableShape): Predicate.Predicate<PartialVariableShape> =>
  Predicate.and(subsumedBy(partial), hasNoMismatch(partial));
```

**Why standalone functions, not methods.** The lattice operations are functions on data, not behaviors of objects. `PartialVariableShape` is a `Schema.Struct` -- a plain data type. Attaching methods would mean wrapping it in a class, which contradicts Effect's data-first design. The `Predicate` module's combinators (`and`, `or`, `compose`) work on standalone functions and compose naturally with `pipe` and `Array.filter`.

**Why not `Match`.** The `Match` module is for exhaustive pattern matching on discriminated unions -- it narrows a union type by eliminating cases. The lattice predicates do not narrow a union; they test properties of a single type. `Match.valueTags` is already used correctly in `Stage2.ts` (line 723) to dispatch on residual `_tag`. The lattice predicates belong to a different concern.

**Predicate.struct for compound checks.** When you need to test multiple fields simultaneously (e.g., "has both measuredProperty and a valid statisticType"), `Predicate.struct` assembles field-level checks into a single Refinement that narrows the whole record:

```typescript
const hasRequiredFields = Predicate.struct({
  measuredProperty: Predicate.isNotUndefined,
  statisticType: Predicate.isNotUndefined
});
// Type: Refinement<{ measuredProperty: unknown; statisticType: unknown },
//                   { measuredProperty: string; statisticType: string }>
```

This is structurally identical to `resolvable` but derives the type narrowing automatically from the field predicates.

---

## 3. The Filter Pipeline

The resolution pipeline is a narrowing funnel. Each step takes a collection and produces a smaller collection. In Effect, this composes as a `pipe` chain over `Array` combinators -- not `Effect.gen`, because the pipeline itself is pure (no services, no async, no errors until you reach the LLM feedback loop).

```typescript
import { Array, Either, Option, Order, pipe } from "effect";
import type { Variable } from "../domain/data-layer/variable";
import type { DataLayerRegistryLookup } from "../resolution/dataLayerRegistry";
import { Chunk } from "effect";

type VariableCandidateScore = {
  readonly variable: Variable;
  readonly matched: ReadonlyArray<FacetKey>;
  readonly mismatched: ReadonlyArray<FacetKey>;
  readonly subsumptionRatio: number;
};

// Step 0: Extract all Variables from registry
const allVariables = (lookup: DataLayerRegistryLookup): ReadonlyArray<Variable> =>
  Chunk.toReadonlyArray(lookup.entities).filter(
    (e): e is Variable => e._tag === "Variable"
  );

// The pure pipeline: PartialVariableShape -> ranked candidates or escalation
const resolveCandidates = (
  partial: PartialVariableShape,
  lookup: DataLayerRegistryLookup
): Either.Either<
  ReadonlyArray<VariableCandidateScore>,
  { readonly _tag: "NotResolvable"; readonly missing: ReadonlyArray<string> }
    | { readonly _tag: "NoCandidates" }
> => {
  // Step 1: Resolvability gate
  if (!resolvable(partial)) {
    return Either.left({
      _tag: "NotResolvable" as const,
      missing: [
        ...(partial.measuredProperty === undefined ? ["measuredProperty"] : []),
        ...(partial.statisticType === undefined ? ["statisticType"] : [])
      ]
    });
  }

  const result = pipe(
    allVariables(lookup),
    // Step 2: Subsumption filter -- keep only candidates where partial <= candidate
    Array.filter(subsumedBy(partial)),
    // Step 3: Score each candidate (matched, mismatched, ratio)
    Array.map((variable) => scoreCandidate(partial, variable)),
    // Step 4: Reject candidates with any dimensional mismatch
    Array.filter((c) => c.mismatched.length === 0),
    // Step 5: Sort by matched count descending, then label for stability
    Array.sort(
      Order.combine(
        Order.mapInput(Order.reverse(Order.number), (c: VariableCandidateScore) => c.matched.length),
        Order.mapInput(Order.string, (c: VariableCandidateScore) => c.variable.label)
      )
    )
  );

  return result.length === 0
    ? Either.left({ _tag: "NoCandidates" as const })
    : Either.right(result);
};
```

**Why `pipe` + `Array` combinators, not `Effect.gen`.** The pipeline reads from in-memory data (`lookup.entities`). No service calls, no async, no error channel. This is a pure computation on arrays. Using `Effect.gen` here would add ceremony without benefit -- you would yield nothing, because nothing is effectful. The `pipe` + `Array.filter` + `Array.map` + `Array.sort` chain is the idiomatic Effect way to express a pure data transformation pipeline.

**Where `Effect.gen` enters.** The boundary between pure and effectful is at the `Stage2Resolver.resolve` call. Inside `Stage2Resolver.layer` (line 22 of `Stage2Resolver.ts`), `Effect.gen` yields the `DataLayerRegistry` and `FacetVocabulary` services. The pure pipeline receives the `lookup` and `vocabulary` objects and runs without effects. This is the correct architecture -- the Layer provides the services, the pure functions consume the data.

**Agent narrowing as an additional filter step.** When Stage 1 resolved an Agent, add a filter between steps 2 and 3:

```typescript
// Step 2b: Structural narrowing via Agent (if available)
const agentVariableIds = getVariableIdsForAgent(agentId, lookup);
Array.filter((v) => agentVariableIds.has(v.id)),
```

This composes cleanly because every step has the same shape: `ReadonlyArray<A> -> ReadonlyArray<A>`.

---

## 4. The Algebra-to-Effect Correspondence

The students' suspected correspondence is partially real and partially a category error. Let me be precise about each mapping.

**Real correspondences:**

| Algebra | Effect | Why it works |
|---------|--------|-------------|
| V (product lattice with optional dimensions) | `PartialVariableShape` as `Schema.Struct` with `optionalKey` fields | Both represent the same thing: a record where each field is either present (a value in F_i) or absent (bottom). The `Schema.Struct` with `optionalKey` is literally the TypeScript encoding of the product of pointed sets (F_i union {undefined}). |
| bottom (all dimensions undefined) | `{}` (empty object matching `PartialVariableShape`) | Not `Option.none()`. Bottom in the product lattice is the element with all components at bottom -- the empty partial assignment. `Option` is for single values; the lattice bottom is a record-level concept. |
| join yielding conflict | `Either.left(DimensionalConflict)` | This is genuine. The lattice join is a partial function -- it is undefined when two elements have incompatible values on the same dimension. `Either` is the standard encoding of a partial function's codomain: `Either<A, E>` where `A` is the success and `E` is the failure. |
| Evidence accumulation | `Array.map` + `Array.filter` pipeline | The sequential evidence combination (scan dimension 1, scan dimension 2, ..., join results) is a fold over the evidence array. Each piece of evidence produces a projection; the fold joins them. This is `Array.reduce` with `join` as the accumulator. |

**Superficial or misleading correspondences:**

| Proposed mapping | Why it breaks down |
|------------------|--------------------|
| Registry functor R as Effect `Layer` | A `Layer` is a dependency injection mechanism -- it constructs and provides service implementations. The registry functor R : C -> FinSet is a mathematical functor mapping schema objects to their data sets. The `Layer` constructs the `DataLayerRegistry` service, but the functor R is the `PreparedDataLayerRegistry` data structure itself (the maps, the indices, the `Chunk<Entity>`). The `Layer` is plumbing; R is the data. |
| Tiered evidence as `Match` exhaustive pattern matching | `Match` dispatches on a discriminated union's `_tag`. Evidence tiers are not a union type -- they are a ranking over a single `Stage2Evidence` union. The tier is an ordinal property of each evidence variant, not a structural discriminant for pattern matching. The right representation is a `tier` field on each evidence variant (as proposed in the advisory), queried with plain comparisons, not `Match`. |
| bottom as `Option.none()` | `Option` represents a single value that may or may not exist. Lattice bottom is a *record* where every field is absent. These are different shapes. A `PartialVariableShape` where all fields are `undefined` is already bottom -- no wrapping needed. `Option` would be appropriate if the entire partial assignment might not exist (e.g., when facet decomposition found zero matches), but that is a different concept from the lattice bottom element. |

**Where Effect adds something the algebra does not capture:**

The algebra describes the lattice and the deterministic pipeline. Effect adds three capabilities the algebra is silent about:

1. **Error typing.** The algebra says "join can fail." Effect's `Either<PartialVariableShape, DimensionalConflict>` captures the failure *type* -- the specific dimensions that conflicted. This is richer than the algebra's binary "defined / undefined."

2. **Service composition.** The algebra assumes the registry R and lexicon L exist. Effect's `Layer` + `ServiceMap.Service` pattern makes the construction of R and L explicit, composable, and testable. `makeResolverLayer` in `resolver/Layer.ts` composes `DataLayerRegistry`, `FacetVocabulary`, `Stage1Resolver`, and `Stage2Resolver` into a single dependency graph. The algebra has no notation for this.

3. **Concurrency.** `Effect.forEach` with `{ concurrency: 8 }` (used in `resolveBulk`, line 234 of `ResolverService.ts`) parallelizes resolution across posts. The algebra describes single-post resolution; Effect handles the operational concern of running many resolutions concurrently with bounded parallelism.

---

## 5. Module Structure

Two modules with a hard boundary between pure and effectful:

### `src/domain/partialVariableAlgebra.ts` (pure -- no Effect imports beyond data types)

Contains the four lattice operations and predicate combinators. Zero service dependencies. Testable with plain unit tests.

```typescript
// src/domain/partialVariableAlgebra.ts
import { Array, Either, Predicate } from "effect";
import type { PartialVariableShape } from "./stage2Core";

export const FACET_KEYS = [ ... ] as const;
export type FacetKey = (typeof FACET_KEYS)[number];

// --- Lattice operations ---
export type DimensionalConflict = { ... };
export const join: (a: PartialVariableShape, b: PartialVariableShape)
  => Either.Either<PartialVariableShape, DimensionalConflict> = ...;
export const subsumes: (general: PartialVariableShape, specific: PartialVariableShape)
  => boolean = ...;
export const specificity: (v: PartialVariableShape) => number = ...;

// --- Type guard ---
export type ResolvablePartial = PartialVariableShape
  & { readonly measuredProperty: string; readonly statisticType: string };
export const resolvable: Predicate.Refinement<PartialVariableShape, ResolvablePartial> = ...;

// --- Predicate combinators ---
export const subsumedBy: (partial: PartialVariableShape)
  => Predicate.Predicate<PartialVariableShape> = ...;
export const hasMinSpecificity: (n: number)
  => Predicate.Predicate<PartialVariableShape> = ...;

// --- Scoring ---
export type VariableCandidateScore = { ... };
export const scoreCandidate: (
  partial: PartialVariableShape,
  variable: PartialVariableShape
) => VariableCandidateScore = ...;
```

### `src/resolution/Stage2.ts` (effectful -- consumes services, orchestrates pipeline)

Imports from `partialVariableAlgebra.ts` and uses the pure functions inside the resolution pipeline. The `handleFacetDecomposition` function calls `resolvable()` as a gate, `subsumes()` via `subsumedBy()` as a filter, and `scoreCandidate()` for ranking. All effectful concerns (reading from `DataLayerRegistryLookup`, accumulating state into `Stage2State`) stay here.

The boundary rule: **if a function takes only `PartialVariableShape` arguments (no services, no state, no registry), it belongs in the algebra module. If it reads from `lookup`, `vocabulary`, or mutates `state`, it belongs in `Stage2.ts`.**

### `src/domain/stage2Evidence.ts` (extended with tier)

Add `confidence` and `tier` fields as proposed in the advisory:

```typescript
// Add to the base of each tagged struct in stage2Evidence.ts:
confidence: ZeroToOneScore,
tier: Schema.Literal("entailment", "strong-heuristic", "weak-heuristic")
```

The `confidence` for `FacetDecompositionEvidence` is computed as `matchedFacets.length / FACET_KEYS.length`. The `tier` is derived from whether the facet decomposition uniquely resolved (entailment) or required fuzzy matching (heuristic). This decouples the evidence-production logic from the decision logic.

---

## 6. Property-Based Test Strategy

Install fast-check as a dev dependency (`@effect/vitest` already provides the test harness; fast-check provides the generators):

```bash
# from skygest-cloudflare root
pnpm add -D fast-check
```

### Arbitrary generators for PartialVariableShape

```typescript
// tests/partialVariableAlgebra.test.ts
import { describe, it, expect } from "@effect/vitest";
import * as fc from "fast-check";
import { Either } from "effect";
import {
  join, subsumes, specificity, resolvable,
  FACET_KEYS, type FacetKey
} from "../../src/domain/partialVariableAlgebra";
import type { PartialVariableShape } from "../../src/domain/stage2Core";

// Canonical values per dimension (sampled from actual vocabulary)
const CANONICAL_VALUES: Record<FacetKey, ReadonlyArray<string>> = {
  measuredProperty: ["generation", "capacity", "emissions", "price", "trade"],
  domainObject: ["electricity", "heat pump", "nuclear reactor"],
  technologyOrFuel: ["solar PV", "wind", "nuclear", "natural gas", "coal"],
  statisticType: ["stock", "flow", "price", "share", "count"],
  aggregation: ["point", "sum", "average", "end_of_period"],
  unitFamily: ["power", "energy", "currency", "mass_co2e", "dimensionless"],
  policyInstrument: ["carbon tax", "emissions trading"]
};

// Generator: a PartialVariableShape with 0-7 randomly filled dimensions
const arbPartial: fc.Arbitrary<PartialVariableShape> =
  fc.record(
    Object.fromEntries(
      FACET_KEYS.map((key) => [
        key,
        fc.option(fc.constantFrom(...CANONICAL_VALUES[key]), { nil: undefined })
      ])
    ) as Record<FacetKey, fc.Arbitrary<string | undefined>>
  ) as fc.Arbitrary<PartialVariableShape>;
```

### Algebraic law tests

**Law 1: join is commutative.** `join(a, b)` and `join(b, a)` must produce the same result (both succeed with the same value, or both fail with conflicts on the same dimensions).

```typescript
it("join is commutative", () => {
  fc.assert(
    fc.property(arbPartial, arbPartial, (a, b) => {
      const ab = join(a, b);
      const ba = join(b, a);
      if (Either.isRight(ab) && Either.isRight(ba)) {
        expect(ab.right).toEqual(ba.right);
      } else if (Either.isLeft(ab) && Either.isLeft(ba)) {
        expect(new Set(ab.left.dimensions)).toEqual(new Set(ba.left.dimensions));
      } else {
        throw new Error("commutativity violated: one succeeded, other failed");
      }
    })
  );
});
```

**Law 2: join is associative.** `join(join(a, b), c) = join(a, join(b, c))` when all intermediate joins succeed.

```typescript
it("join is associative", () => {
  fc.assert(
    fc.property(arbPartial, arbPartial, arbPartial, (a, b, c) => {
      const ab = join(a, b);
      const bc = join(b, c);
      if (Either.isLeft(ab) || Either.isLeft(bc)) return; // skip conflicting cases

      const ab_c = join(ab.right, c);
      const a_bc = join(a, bc.right);

      if (Either.isRight(ab_c) && Either.isRight(a_bc)) {
        expect(ab_c.right).toEqual(a_bc.right);
      } else if (Either.isLeft(ab_c) && Either.isLeft(a_bc)) {
        // Both fail -- associativity of failure
      } else {
        throw new Error("associativity violated");
      }
    })
  );
});
```

**Law 3: bottom is the identity for join.** `join(bottom, v) = v` for all `v`.

```typescript
it("bottom is the identity element for join", () => {
  const bottom: PartialVariableShape = {};
  fc.assert(
    fc.property(arbPartial, (v) => {
      const result = join(bottom, v);
      expect(Either.isRight(result)).toBe(true);
      if (Either.isRight(result)) {
        for (const key of FACET_KEYS) {
          expect(result.right[key]).toBe(v[key]);
        }
      }
    })
  );
});
```

**Law 4: subsumes is reflexive.** `subsumes(v, v) = true` for all `v`.

```typescript
it("subsumes is reflexive", () => {
  fc.assert(
    fc.property(arbPartial, (v) => {
      expect(subsumes(v, v)).toBe(true);
    })
  );
});
```

**Law 5: subsumes is transitive.** If `subsumes(a, b)` and `subsumes(b, c)`, then `subsumes(a, c)`.

```typescript
it("subsumes is transitive", () => {
  fc.assert(
    fc.property(arbPartial, arbPartial, arbPartial, (a, b, c) => {
      if (subsumes(a, b) && subsumes(b, c)) {
        expect(subsumes(a, c)).toBe(true);
      }
    })
  );
});
```

**Law 6: subsumes and specificity are consistent.** If `subsumes(a, b)` and `a !== b`, then `specificity(a) <= specificity(b)`.

```typescript
it("subsumption implies non-decreasing specificity", () => {
  fc.assert(
    fc.property(arbPartial, arbPartial, (a, b) => {
      if (subsumes(a, b)) {
        expect(specificity(a)).toBeLessThanOrEqual(specificity(b));
      }
    })
  );
});
```

**Law 7: resolvable implies minimum specificity of 2.**

```typescript
it("resolvable implies specificity >= 2", () => {
  fc.assert(
    fc.property(arbPartial, (v) => {
      if (resolvable(v)) {
        expect(specificity(v)).toBeGreaterThanOrEqual(2);
      }
    })
  );
});
```

**Law 8: join followed by subsumption.** If `join(a, b)` succeeds with result `c`, then `subsumes(a, c)` and `subsumes(b, c)`.

```typescript
it("successful join is subsumed by both operands", () => {
  fc.assert(
    fc.property(arbPartial, arbPartial, (a, b) => {
      const result = join(a, b);
      if (Either.isRight(result)) {
        expect(subsumes(a, result.right)).toBe(true);
        expect(subsumes(b, result.right)).toBe(true);
      }
    })
  );
});
```

These eight laws are the complete algebraic specification. If `join`, `subsumes`, `specificity`, and `resolvable` satisfy these properties, the resolution pipeline is algebraically correct regardless of implementation details. The fast-check generators explore the space of partial assignments (including edge cases like all-bottom, all-filled, single-dimension) far more thoroughly than hand-written test cases.

---

## Summary

| Concern | Location | Effect types used |
|---------|----------|-------------------|
| Lattice operations (pure) | `src/domain/partialVariableAlgebra.ts` | `Either`, `Predicate`, `Predicate.Refinement` |
| Predicate combinators (pure) | same file | `Predicate.and`, `Predicate.compose`, partial application |
| Filter pipeline (pure) | `src/resolution/Stage2.ts` (refactored `handleFacetDecomposition`) | `Array.filter`, `Array.map`, `Array.sort`, `pipe`, `Order` |
| Service wiring (effectful) | `src/resolution/Stage2Resolver.ts` | `Effect.gen`, `Layer`, `ServiceMap.Service` |
| Orchestration (effectful) | `src/resolver/ResolverService.ts` | `Effect.gen`, `Effect.fn`, `Effect.forEach`, `Result` |
| Evidence typing | `src/domain/stage2Evidence.ts` | `Schema.TaggedStruct`, `Schema.Literal` |
| Algebraic law tests | `tests/partialVariableAlgebra.test.ts` | `@effect/vitest`, `fast-check` |

The hard boundary: everything in `partialVariableAlgebra.ts` is a pure function. It imports `Either`, `Predicate`, and `Array` from Effect (data types and combinators), but never `Effect`, `Layer`, or `ServiceMap`. The resolution service consumes these pure functions inside `Effect.gen` generators where the service dependencies are available. This separation means the algebraic laws can be tested without constructing any Layer or mocking any service.
