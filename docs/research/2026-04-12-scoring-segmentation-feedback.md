# Scoring, Segmentation, and Feedback: Formalizing Three Abstraction Gaps

**Date**: 2026-04-12
**Status**: Advisory document
**Prerequisite reading**: resolution-algebra.md, text-ops-and-evidence-combination.md, resolution-trace-examples.md
**Audience**: Grad students implementing the Skygest Stage 2 resolution kernel

---

## 1. The Scoring Model: Subsumption Ratio, Not Match Count

### The problem

`scoreVariableCandidate` (Stage2.ts, lines 239-292) computes a single number: how many of the partial assignment's non-bottom dimensions equal the candidate Variable's corresponding dimension. This is an intersection count. It conflates two categorically different situations:

**Case A** -- partial has 3 filled dimensions, candidate matches all 3. The partial *subsumes* the candidate on those dimensions. The candidate is fully compatible with everything the text told us.

**Case B** -- partial has 3 filled dimensions, candidate matches 1 of 3. Two dimensions that the text explicitly resolved have values *incompatible* with this candidate. The candidate contradicts 2/3 of the evidence.

Under the current scoring, Case B looks identical to a partial with 1 filled dimension matching on that 1. Both score 1. The system discards the information about how specific the partial was.

### The formal model

Define two quantities for a (partial, candidate) pair:

```
matched(p, c) = |{ i : p[i] != bot AND p[i] = c[i] }|
mismatched(p, c) = |{ i : p[i] != bot AND c[i] != bot AND p[i] != c[i] }|
```

And recall:

```
specificity(p) = |{ i : p[i] != bot }|
```

The **subsumption ratio** is:

```
subsumptionRatio(p, c) = matched(p, c) / specificity(p)
```

This is 1.0 when the candidate is fully compatible with the partial (subsumption), and approaches 0 when most filled dimensions conflict. A ratio of 1.0 means `p <= c` in the lattice (the partial subsumes the candidate on all filled dimensions). A ratio below 1.0 means the candidate *contradicts* some evidence.

The **mismatch count** is the complementary signal: it tells you how many dimensions actively disagree (as opposed to being unspecified on one side).

### What the kernel should compute

Replace `ScoredVariableCandidate` with a richer type:

```typescript
// In Stage2.ts or a new partialVariableAlgebra.ts

const FACET_KEYS = [
  "measuredProperty", "domainObject", "technologyOrFuel",
  "statisticType", "aggregation", "unitFamily"
] as const satisfies ReadonlyArray<FacetField>;

type VariableCandidateScore = {
  readonly variable: Variable;
  readonly matched: ReadonlyArray<FacetField>;
  readonly mismatched: ReadonlyArray<FacetField>;
  readonly partialSpecificity: number;
  readonly subsumptionRatio: number;  // matched.length / partialSpecificity
};
```

The scoring function becomes:

```typescript
const scoreVariableCandidate = (
  partial: PartialVariableShape,
  variable: Variable
): VariableCandidateScore => {
  const matched: Array<FacetField> = [];
  const mismatched: Array<FacetField> = [];

  for (const key of FACET_KEYS) {
    const pv = partial[key];
    const cv = variable[key];
    if (pv === undefined) continue;        // partial is bot on this dim
    if (pv === cv) matched.push(key);
    else if (cv !== undefined) mismatched.push(key);
    // If cv is undefined (Variable unspecified), neither match nor mismatch.
    // The Variable's dimension is unconstrained -- no contradiction.
  }

  const partialSpecificity = matched.length + mismatched.length
    + FACET_KEYS.filter(k => partial[k] !== undefined && variable[k] === undefined).length;

  return {
    variable,
    matched,
    mismatched,
    partialSpecificity: FACET_KEYS.filter(k => partial[k] !== undefined).length,
    subsumptionRatio: partialSpecificity > 0
      ? matched.length / FACET_KEYS.filter(k => partial[k] !== undefined).length
      : 0
  };
};
```

### Candidate filtering rule

The current filter is `candidate.score > 0` (line 495). Replace it with:

```typescript
const candidates = allScored
  .filter(c => c.mismatched.length === 0)  // strict: no contradictions
  .sort((a, b) =>
    b.matched.length - a.matched.length ||
    a.variable.label.localeCompare(b.variable.label)
  );
```

**Only candidates with zero mismatches survive.** This is the lattice subsumption filter: `p <= c` requires that every non-bot dimension in p equals the corresponding dimension in c. The `mismatched.length === 0` check *is* the subsumption test, restricted to dimensions where both sides are non-bot.

This change eliminates the Case B problem entirely. A candidate that contradicts any dimension the partial filled is rejected, regardless of how many other dimensions it matches.

### Diagnostic value of mismatch

When `candidates.length === 0` and the partial has high specificity, the mismatch data tells the curator *why* no Variable fit. If every candidate has 1+ mismatches, the partial describes a Variable the registry does not contain. The mismatched dimensions pinpoint which facet values need a new Variable definition. Include the top-scoring rejected candidates (sorted by `mismatched.length` ascending) in the escalation payload.

---

## 2. The Multi-Variable Model

### The problem

The parallel independent scan (T2) returns at most one match per dimension. When a post describes "solar generation, wind generation, and gas generation in Germany," the scan picks one technology (longest match) and loses the others. The formal model assumes the input describes one Variable, but real chart text often describes a *table* -- multiple Variables sharing some dimensions but differing on others.

### Formal model: Cartesian decomposition

Define a **multi-partial** as a set of partial assignments derived from a single text:

```
multiDecompose(text) = { v_1, v_2, ..., v_n }   where each v_i in V
```

The key insight: in multi-Variable text, some dimensions are **shared** (the same value appears in every v_i) and some are **varying** (different values per v_i). In the example "Solar and wind generation in EU-27 (TWh)":

- Shared: measuredProperty=generation, unitFamily=energy
- Varying: technologyOrFuel in {solar PV, wind}

The multi-partial is the **Cartesian product of the shared partial with the varying dimension's value set**:

```
shared = (generation, bot, bot, bot, bot, energy, bot)
varying_technologyOrFuel = {solar PV, wind}

multiDecompose = { join(shared, project(t)) | t in varying_technologyOrFuel }
               = { (generation, bot, solar PV, bot, bot, energy, bot),
                   (generation, bot, wind, bot, bot, energy, bot) }
```

Each element of the multi-partial is then independently run through the candidate filtering pipeline.

### Implementation: matchAll variant

The minimum change is to add a `matchAll` variant alongside the existing single-match functions. The current `matchTechnologyOrFuel(text)` returns `Option<Entry>` (one winner). A new `matchAllTechnologyOrFuel(text)` returns `Array<Entry>` (all matches that do not overlap):

```typescript
// In SurfaceFormEntry.ts, alongside matchSurfaceForm:
const matchAllSurfaceForms = (
  lookup: SurfaceFormLookup,
  normalizedText: string
): ReadonlyArray<SurfaceFormEntry> => {
  const results: Array<SurfaceFormEntry> = [];
  let remaining = normalizedText;

  for (const matcher of lookup.orderedMatchers) {
    if (matcher.test(remaining)) {
      results.push(matcher.entry);
      // Mark matched region to prevent overlapping matches
      remaining = remaining.replace(matcher.pattern, " ".repeat(matcher.surfaceForm.length));
    }
  }

  return results;
};
```

Then in `handleFacetDecomposition`, after the single-match scan, detect when multiple matches exist:

```typescript
// After the existing single-match scan (lines 410-445):
const allTechMatches = vocabulary.matchAllTechnologyOrFuel(residual.text);

if (allTechMatches.length > 1) {
  // Multi-Variable path: generate one partial per technology
  for (const techMatch of allTechMatches) {
    const variant = { ...partial, technologyOrFuel: techMatch.canonical };
    // Run candidate scoring independently for each variant
    handleSinglePartial(state, postContext, residual, lookup, variant, ...);
  }
  return;
}
```

### Trade-offs

| Approach | Complexity | Coverage | Risk |
|----------|-----------|----------|------|
| Single match (status quo) | Low | Single-Variable text only | Loses multi-topic posts |
| matchAll + Cartesian | Medium | Handles "X and Y generation" pattern | Combinatorial explosion if multiple dimensions vary (2 techs x 3 domains = 6 partials) |
| Text segmentation (see section 3) | High | Handles tabular text, mixed-topic posts | Requires structural parsing |

**Recommendation**: Implement matchAll for `technologyOrFuel` only as a first step. This is the dimension that most frequently has multiple values in a single text (the traced examples confirm this: Example 2 has wind/solar/coal/gas, Example 5 has solar/wind-onshore/wind-offshore). Defer Cartesian products across multiple dimensions until eval data shows it is needed.

### Type changes in FacetVocabularyShape

Add `matchAll` variants to the vocabulary interface (`facetVocabulary/index.ts`, line 119):

```typescript
export type FacetVocabularyShape = {
  // ... existing single-match methods ...
  readonly matchAllTechnologyOrFuel: (
    text: string
  ) => ReadonlyArray<TechnologyOrFuelSurfaceForm>;
};
```

---

## 3. Text Segmentation Strategy

### The problem

The system treats input text as an atomic string. But chart titles like "Solar and wind generation in Europe (TWh)" contain two Variables that share dimensions. Tabular text like "Solar: 44.5 TWh / Wind onshore: 110.5 TWh" contains structurally delimited segments.

### Minimum viable segmentation: structural delimiters

Full NLP segmentation (dependency parsing, clause boundary detection) is overkill and introduces a model dependency the deterministic resolver explicitly avoids. Instead, exploit the structural patterns that *actually appear* in chart text and social media posts.

**Three delimiter classes** cover the common cases:

1. **Line breaks**: `\n` splits tabular data ("Solar: 44.5 TWh\nWind: 110.5 TWh")
2. **Bullet/list markers**: `•`, `-`, numbered lists ("1. Solar 2. Wind")
3. **Conjunction splitting**: " and ", " & ", " / ", " vs " between known vocabulary terms

```typescript
type TextSegment = {
  readonly text: string;
  readonly index: number;          // position in original text
  readonly delimiter: "line" | "list" | "conjunction" | "whole";
};

const segmentText = (text: string): ReadonlyArray<TextSegment> => {
  // Try line-based splitting first (most reliable)
  const lines = text.split(/\n+/).map(l => l.trim()).filter(l => l.length > 0);
  if (lines.length > 1) {
    return lines.map((line, i) => ({ text: line, index: i, delimiter: "line" }));
  }

  // Try conjunction splitting for "X and Y" patterns
  // Only split on conjunctions that appear between vocabulary-matchable terms
  const conjunctionPattern = /\b(and|&|\/|vs\.?)\b/gi;
  // ... split logic with vocabulary-awareness ...

  // Fallback: treat as single segment
  return [{ text, index: 0, delimiter: "whole" }];
};
```

### Composition with the lattice

Segmentation composes with the existing pipeline as a pre-processing step:

```
text
  -> segmentText(text)                    // NEW: structural segmentation
  -> for each segment:
       decompose(segment)                 // existing: T1-T4 per segment
       -> check resolvable(partial)       // existing: SHACL gate
       -> filter by subsumes()            // existing: candidate matching
  -> deduplicate results across segments  // NEW: merge identical Variable matches
```

The key property: **segmentation is idempotent with the single-segment case**. If `segmentText` returns one segment (the whole text), the pipeline behaves identically to today. This means segmentation can be added without changing any existing behavior for single-Variable text.

### When NOT to segment

Segmentation should be skipped for residual types where the text is already a focused label:

- `chart-title`: Usually one concept. Do NOT segment on conjunctions here -- "Wind and solar generation" is one title, not two segments.
- `axis-label`: Already atomic. Never segment.
- `post-text`: Segment on line breaks. This is where tabular data appears.
- `key-finding`: May contain multiple claims. Segment on line breaks.

Add a `segmentable` flag to the residual type or decide based on `residual.kind`:

```typescript
const shouldSegment = (residual: DeferredToStage2Residual): boolean =>
  residual.kind === "post-text" || residual.kind === "key-finding";
```

For non-segmentable residuals, use `matchAll` (section 2) instead. Chart titles like "Solar and wind generation" should trigger the multi-match path, not the segmentation path.

---

## 4. The LLM Feedback Loop

### The formal model

The resolution pipeline is currently linear: Stage 1 -> Stage 2 -> escalate to Stage 3. The students observed that the `resolvable()` gate creates a clean contract: when the deterministic resolver fills measuredProperty but not statisticType, the LLM's job is specifically to fill that gap.

This is a **fixpoint computation**. Define:

```
resolve : PartialVariableShape -> PartialVariableShape | Resolved | Escalated
enrich  : PartialVariableShape -> PartialVariableShape   (LLM fills gaps)
```

The feedback loop is:

```
p_0 = decompose(text)                     // initial partial from T1-T4
p_1 = resolve(p_0)                        // deterministic resolution attempt
if p_1 is Escalated with gaps:
  p_2 = enrich(p_1)                       // LLM fills missing dimensions
  p_3 = resolve(p_2)                      // re-run deterministic resolution
  if p_3 is Resolved: done
  if p_3 is Escalated: final escalation   // LLM could not help enough
```

The loop terminates in at most 2 iterations because: (a) the LLM either fills gaps or it does not, and (b) the deterministic resolver is a pure function -- same input always gives the same output.

### Effect types

The feedback loop maps naturally to Effect's `Either` for the resolution result and a simple pipeline for the loop:

```typescript
import { Effect, Either, pipe } from "effect";

// The gap report tells the LLM exactly what to fill
type ResolutionGap = {
  readonly partial: PartialVariableShape;
  readonly missingRequired: ReadonlyArray<"measuredProperty" | "statisticType">;
  readonly candidates: ReadonlyArray<CandidateEntry>;
  readonly context: {
    readonly text: string;
    readonly matchedSurfaceForms: ReadonlyArray<SurfaceFormEntryAny>;
  };
};

// Resolution outcome: either resolved or needs LLM help
type DeterministicOutcome = Either.Either<
  Stage1Match,      // Right: resolved
  ResolutionGap     // Left: needs enrichment
>;

// The deterministic resolver as a pure function
const deterministicResolve = (
  partial: PartialVariableShape,
  lookup: DataLayerRegistryLookup
): DeterministicOutcome => {
  if (!resolvable(partial)) {
    return Either.left({
      partial,
      missingRequired: [
        ...(partial.measuredProperty === undefined ? ["measuredProperty" as const] : []),
        ...(partial.statisticType === undefined ? ["statisticType" as const] : [])
      ],
      candidates: [],
      context: { text: "", matchedSurfaceForms: [] }
    });
  }
  // ... subsumption filtering, scoring ...
};

// LLM enrichment as an effectful function (it calls an external API)
const llmEnrich = (
  gap: ResolutionGap
): Effect.Effect<PartialVariableShape, LlmEnrichmentError> =>
  Effect.gen(function* () {
    // Call LLM with structured prompt:
    // "Given this text and these matched facets, what is the measuredProperty?
    //  Choose from: [list of valid canonical values]"
    // The LLM returns a PartialVariableShape with gaps filled.
    const enriched = yield* callLlmForGapFilling(gap);
    return enriched;
  });

// The feedback loop
const resolveWithFeedback = (
  text: string,
  lookup: DataLayerRegistryLookup,
  vocabulary: FacetVocabularyShape
): Effect.Effect<Stage1Match | Stage3Input, LlmEnrichmentError> =>
  Effect.gen(function* () {
    const initial = decompose(text, vocabulary);
    const firstAttempt = deterministicResolve(initial, lookup);

    if (Either.isRight(firstAttempt)) {
      return firstAttempt.right;  // resolved on first pass
    }

    // LLM enrichment pass
    const enriched = yield* llmEnrich(firstAttempt.left);
    const secondAttempt = deterministicResolve(enriched, lookup);

    if (Either.isRight(secondAttempt)) {
      return secondAttempt.right;  // resolved after LLM help
    }

    // Still unresolved: final escalation
    return buildEscalation(secondAttempt.left, "unresolved after LLM enrichment");
  });
```

### The contract between stages

The `ResolutionGap` type is the contract. It tells the LLM:

1. **What is already known** (`partial` -- the filled dimensions)
2. **What is missing** (`missingRequired` -- which specific dimensions to fill)
3. **What the options are** (`candidates` -- the registry Variables to choose from)
4. **The raw evidence** (`context.text`, `context.matchedSurfaceForms`)

This is dramatically better than the current `Stage3Input` which bundles everything into a flat escalation. The LLM gets a structured gap description instead of "here is some text and some candidates, figure it out."

### Where this lives in the architecture

The feedback loop does NOT belong inside `runStage2`. Stage 2 is the deterministic kernel -- it should remain pure and stateless. The loop belongs in the *orchestrator* that calls Stage 2, which is currently the data-ref resolution workflow.

In `resolution.ts`, the `ResolvePostResponse` already has optional `stage2` and `stage3` fields. The feedback loop adds an optional `stage2b` (re-resolution after LLM enrichment):

```typescript
export const ResolvePostResponse = Schema.Struct({
  postUri: PostUri,
  stage1: Stage1Result,
  stage2: Schema.optionalKey(Stage2Result),
  stage2b: Schema.optionalKey(Stage2Result),   // NEW: re-resolution pass
  stage3: Schema.optionalKey(ResolveStage3Result),
  resolverVersion: ResolverVersion,
  latencyMs: ResolveLatencyMs
});
```

---

## 5. Implementation Priority

### Phase 1: Scoring fix + resolvability gate (immediate, highest leverage)

**Changes**:

1. Add `resolvable()` as a pure function. Two lines of code.
2. Add the gate in `handleFacetDecomposition` (Stage2.ts, after line 447, before line 492).
3. Replace `scoreVariableCandidate` with the subsumption-ratio version. Add `mismatched` tracking.
4. Change the candidate filter from `score > 0` to `mismatched.length === 0`.

**Files touched**: `Stage2.ts` (lines 239-292 for scoring, ~line 492 for gate). Optionally extract to a new `partialVariableAlgebra.ts`.

**Eval impact**: The trace examples show this prevents all 5 traced false positives. The resolvability gate alone addresses the 22 wrong-new-match cases in the eval.

**Risk**: Near zero. The gate only prevents matches that lack required dimensions -- it cannot cause a correct match to be lost. The subsumption filter is strictly more conservative than the current intersection filter.

### Phase 2: Multi-match for technologyOrFuel (next sprint)

**Changes**:

1. Add `matchAllSurfaceForms` to the SurfaceFormEntry module.
2. Add `matchAllTechnologyOrFuel` to `FacetVocabularyShape`.
3. In `handleFacetDecomposition`, detect multi-match and fork into per-variant scoring.

**Files touched**: `SurfaceFormEntry.ts`, `technologyOrFuel.ts`, `facetVocabulary/index.ts`, `Stage2.ts`.

**Eval impact**: Directly addresses Example 2 (Turkey wind/solar/coal/gas) and Example 5 (EU-27 solar/wind). Expected to convert some ambiguous escalations into correct resolutions.

**Risk**: Low-medium. The multi-match path is additive -- single-match text follows the existing code path unchanged. Risk is in the Cartesian product: if text mentions 4 technologies, we generate 4 partials and run 4 candidate scorings. This is O(T * V) where T = technology matches and V = registry variables, which is fine at current registry size (~30 variables).

### Phase 3: Text segmentation for post-text (future)

**Changes**:

1. Add `segmentText()` function.
2. Call it in `handleFacetDecomposition` for segmentable residual types.
3. Run the full decomposition pipeline per segment, deduplicate results.

**Depends on**: Phase 1 (the resolvability gate must exist before segmentation makes sense, otherwise each segment produces its own false positives).

**Risk**: Medium. Segmentation can split text at the wrong boundary, producing impoverished partials that resolve to wrong Variables. Must be tested against the full eval corpus.

### Phase 4: LLM feedback loop (future, requires Stage 3 implementation)

**Changes**:

1. Define `ResolutionGap` type in domain layer.
2. Implement `llmEnrich` as an Effect that calls the LLM with a structured gap-filling prompt.
3. Wire the feedback loop into the resolution orchestrator.

**Depends on**: Phase 1 (the gap detection requires `resolvable()`), and a working Stage 3 LLM pipeline.

**Risk**: Medium-high. The LLM may hallucinate facet values not in the vocabulary. Mitigation: constrain the LLM's output to valid canonical values using a closed-choice prompt (provide the list of valid values for each missing dimension). Validate the enriched partial against the vocabulary before re-resolution.

---

## Summary of Operations

| Operation | Status | Phase | Location |
|-----------|--------|-------|----------|
| `resolvable(v)` | **Gap** | 1 | New pure function, gate in Stage2.ts ~line 492 |
| `subsumptionRatio(p, c)` | **Gap** (conflated with intersection) | 1 | Replace `scoreVariableCandidate`, Stage2.ts lines 239-292 |
| `mismatched(p, c)` | **Gap** | 1 | Add to scoring, use as filter |
| `matchAll` per dimension | **Gap** | 2 | New function in SurfaceFormEntry.ts |
| `segmentText(text)` | **Gap** | 3 | New function, pre-processing step |
| `ResolutionGap` type | **Gap** | 4 | New type in domain layer |
| `llmEnrich(gap)` | **Gap** | 4 | New effectful function in resolution orchestrator |
| `resolveWithFeedback` | **Gap** | 4 | Orchestrator-level composition |
