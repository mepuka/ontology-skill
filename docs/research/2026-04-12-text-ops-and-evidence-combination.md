# Text Operations and Evidence Combination: Advisory for the Resolution Kernel

**Date**: 2026-04-12
**Status**: Advisory document (companion to resolution-algebra.md)
**Audience**: Grad students implementing the Skygest Stage 2 resolution kernel

---

## Part 1: Naming the Text Operations

The pipeline from raw chart text to facet values involves four formally
distinct operations. Each has a standard name in the CS/NLP literature, and
each maps to concrete code.

### Operation T1: Canonicalization (Unicode normalization + case folding)

**Formal name**: *Text canonicalization* (or *orthographic normalization*).
The composition of Unicode NFKC normalization, case folding, and whitespace
collapse is a standard preprocessing step in information retrieval called
*canonicalization*. It produces an equivalence class of strings that should
be treated as identical for matching purposes.

**Code**: `normalizeLookupText()` in `src/resolution/normalize.ts`:

```typescript
export const normalizeLookupText = (value: string) =>
  collapseWhitespace(value.normalize("NFKC").toLowerCase());
```

**Formal property**: This is a *surjective, idempotent* function
`norm : String -> S` where S is the set of canonical surface forms.
Idempotency (`norm(norm(x)) = norm(x)`) is guaranteed by the composition
of NFKC (idempotent) with lowercase (idempotent) with whitespace collapse
(idempotent). The resolution algebra document already names this correctly.

**What it is NOT**: This is not *stemming* (no morphological reduction),
not *lemmatization* (no dictionary lookup), and not *transliteration*
(no script conversion). Those would be future extensions.

### Operation T2: Boundary-delimited substring scanning

**Formal name**: *Anchored substring matching with word-boundary constraints*,
a restricted form of *pattern matching over strings*. In computational
linguistics, this sits between full tokenization (segmenting text into a
token sequence) and sliding-window matching (trying every substring). The
system uses neither.

**Code**: `buildSurfaceFormMatcher()` in
`src/resolution/facetVocabulary/SurfaceFormEntry.ts`:

```typescript
const buildSurfaceFormMatcher = (normalizedSurfaceForm: string) => {
  const pattern = new RegExp(
    `(^|[^\\p{L}\\p{N}])${escapeRegExp(normalizedSurfaceForm)}(?=$|[^\\p{L}\\p{N}])`,
    "u"
  );
  return (normalizedText: string) => pattern.test(normalizedText);
};
```

**What this actually does**: For each surface form in the vocabulary, it
compiles a regex that tests whether the surface form appears in the input
text as a *whole-word substring* (bounded by non-alphanumeric characters or
string boundaries). This is not tokenize-then-lookup; it is
regex-scan-per-vocabulary-entry.

**Matching strategy**: The `orderedMatchers` array is sorted by descending
surface form length, and `matchSurfaceForm()` returns the *first* match
found. This implements a **longest-match-first** (or **greedy leftmost
longest**) strategy -- the standard approach in lexical analysis (cf.
maximal munch in compiler theory). However, there is a critical subtlety:
the system returns only **one match per facet dimension**. Each of the six
`vocabulary.match*()` calls runs independently and returns `Option<Entry>`.

**Formal model**: For each dimension i, define `scan_i : S -> Option(F_i)`
as: normalize the input, try each compiled pattern in descending length
order, return the first hit. The full scan is the product:

```
scan(text) = (scan_1(text), scan_2(text), ..., scan_6(text))
```

This is a **parallel independent scan** -- each dimension scans the same
input independently. This means the system never needs to "consume" tokens
or worry about overlapping matches across dimensions. Two dimensions can
match the same substring (e.g., "generation" could match both a
measuredProperty and a statisticType), and that is correct -- it fills two
lattice positions from one piece of text evidence.

### Operation T3: Exact-match dictionary lookup (the fast path)

**Formal name**: *Dictionary lookup* or *lexicon probe*. Before running
the regex scan, `matchSurfaceForm()` first checks the normalized text
against the `entryByNormalizedSurfaceForm` map as an exact equality test.

**Code** (in `SurfaceFormEntry.ts`):

```typescript
const exact = lookup.entryByNormalizedSurfaceForm.get(normalizedText);
if (exact !== undefined) {
  return Option.some(exact);
}
```

**Why this matters**: The exact-match path handles the case where the
*entire* input text is itself a surface form (e.g., the axis label IS
"electricity generation" and that is a known surface form for
measuredProperty). The regex path handles the case where a surface form
is *embedded* in longer text (e.g., chart title "German electricity
generation by fuel type" contains "electricity generation").

The two-tier strategy (exact first, then regex scan) is a standard
optimization in *dictionary-based named entity recognition*. Formally:

```
match_i(text) = exactLookup_i(norm(text))  |>  orElse(regexScan_i(norm(text)))
```

### Operation T4: Canonical projection (surface form to lattice element)

**Formal name**: *Lexical grounding* or *concept resolution*. The mapping
from a matched surface form entry to its `canonical` value, which becomes
the lattice coordinate. In ontology engineering, this is the mapping from a
*lexical entry* to a *concept identifier* -- what SKOS calls the
relationship between `skos:altLabel`/`skos:prefLabel` and the concept URI.

**Code**: The `.canonical` field on every `SurfaceFormEntry`, used in
`handleFacetDecomposition()`:

```typescript
if (Option.isSome(statisticType)) {
  partialDraft.statisticType = statisticType.value.canonical;
}
```

**What IS a canonical value**: Formally, it is the *representative element*
of an equivalence class in F_i. All surface forms that map to canonical
value c are in the same equivalence class -- they are different ways of
saying the same thing. The canonical value is the class representative
chosen by convention (typically the `skos:prefLabel`). In the lattice, it
is the *coordinate label* for that position on axis i.

---

## Composition: The Text-to-Lattice Pipeline

The four operations compose into a formal pipeline. Using the notation from
the resolution algebra document:

```
text                                         : String
  |
  v
norm(text)                                   : S          [T1: canonicalize]
  |
  v
(match_1(text), ..., match_6(text))          : Option(Entry)^6   [T2+T3: parallel scan]
  |
  v
(canonical_1, ..., canonical_6)              : (F_1|bot) x ... x (F_6|bot)   [T4: project]
  =
partial assignment v in V                    : V          [lattice element]
```

**Key insight**: The text operations and the lattice operations are
*stratified* -- all text operations complete before any lattice operation
begins. The `handleFacetDecomposition()` function runs all six
`vocabulary.match*()` calls, collects results into `partialDraft`, and only
then does candidate scoring (which is the lattice `subsumes` operation).

**Does text matching order matter?** No, because the six scans are
*independent* (each dimension scans the full input) and the lattice join
is commutative and associative. The parallel scan architecture guarantees
order-independence. This is a design strength, not an accident.

**Where the layers interact**: The only coupling point is the
`orderedMatchers` sort. Within a single dimension, longer surface forms
are tried first. If "natural gas" and "gas" are both surface forms for
domainObject, "natural gas" wins because it is longer. This is the
*maximal munch* property and it is local to each dimension -- it does not
cross dimensions.

---

## Part 2: Evidence Combination Framework

### Recommendation: Ranked-tier fusion with deterministic precedence

Do **not** use Dempster-Shafer, Bayesian combination, or any probabilistic
framework. Here is why:

1. **Your signals are not independent.** Dempster-Shafer and Bayesian
   combination both assume (or require correction for) independence of
   evidence sources. But facet decomposition and fuzzy dataset title
   matching are correlated -- if the text mentions "electricity prices,"
   the facet decomposition finds measuredProperty=Price, and the fuzzy
   title match finds a dataset called "Electricity Prices Monthly." These
   are not independent observations.

2. **Your deterministic signals are categorically stronger.** A facet
   decomposition that fills 4 dimensions and uniquely subsumes exactly one
   registry Variable is *certain* (modulo vocabulary errors). A fuzzy
   Jaccard score of 0.72 is *uncertain*. Mixing these in a probabilistic
   framework forces you to assign a "probability" to the deterministic
   signal, which is epistemically wrong -- it is not 0.99 probable, it is
   *logically entailed* by the vocabulary.

3. **Your system is small and auditable.** You have three evidence types
   and a finite registry. The value of probabilistic combination is in
   large-scale systems with hundreds of noisy signals. At your scale,
   explicit ranked tiers are more debuggable and more correct.

**The right framework: Tiered evidence with deterministic precedence.**

Define three tiers:

| Tier | Signal type | Resolution mode |
|------|------------|-----------------|
| 1 (entailment) | Facet decomposition with unique subsumption | Deterministic: the lattice algebra proves the answer |
| 2 (strong heuristic) | Fuzzy match above confident threshold (0.85) | High-confidence shortcut: accept if no Tier 1 conflict |
| 3 (weak heuristic) | Fuzzy match above candidate threshold (0.60) | Candidate generation only: escalate for confirmation |

**Combination rule**: Tier 1 beats Tier 2 beats Tier 3. Within a tier,
if signals agree, accept. If signals conflict, escalate. Across tiers,
a higher tier overrides a lower tier, but a lower tier can *corroborate*
a higher tier (increasing confidence in the audit trail without changing
the decision).

This is formally a **lexicographic order on evidence strength**, which is
the standard approach in entity resolution systems that mix deterministic
and probabilistic signals (see Fellegi-Sunter model, where the "clerical
review" region is exactly your Tier 3 escalation).

### Disambiguation under partial information

When the partial assignment matches N candidates equally (tied score in
`scoreVariableCandidate`), use **structural disambiguation via the DCAT
chain**, which you already have the infrastructure for but do not exploit:

1. **Agent narrowing**: If Stage 1 resolved an Agent, filter candidates
   to Variables belonging to Datasets published by that Agent. This uses
   the path `Agent <-publisherOf- Dataset -hasVariable-> Variable` --
   exactly the inverse navigation described in Gap 5 of the algebra
   document.

2. **Distribution narrowing**: If Stage 1 resolved a Distribution, follow
   `Distribution -datasetOf-> Dataset -hasVariable-> Variable` to narrow.

3. **FixedDims narrowing**: If the text contains place names, frequency
   terms, or sector references, match against `fixedDims` on candidate
   Variables. This is a second product lattice (over the fixed dimensions)
   that you can join with the semantic facet lattice.

### The closed-world problem

You asked: how do you distinguish "no match because the Variable does not
exist in the registry" from "no match because the vocabulary is incomplete"?

**You cannot distinguish them from within the resolution kernel alone.**
This is a fundamental limitation of closed-world reasoning over an
incomplete knowledge base. But you can provide *diagnostic signals* that
help the human curator distinguish them:

- **High specificity, zero candidates**: The partial assignment has 4+
  non-bottom dimensions, yet no registry Variable is subsumed by it.
  This strongly suggests a *missing Variable* -- the vocabulary is
  working fine, but the registry is incomplete.

- **Low specificity, many candidates**: The partial assignment has 1-2
  dimensions filled. This suggests *vocabulary gaps* -- the text contains
  domain concepts the vocabulary does not recognize.

- **Non-zero unmatched tokens**: The `unmatchedSurfaceForms` array in the
  escalation payload already carries this signal. If unmatched tokens look
  like domain terms (not stopwords), they are vocabulary gap evidence.

---

## Part 3: The Five Most Impactful Improvements

Ordered by implementation impact (highest leverage first).

### 1. Extract the lattice algebra as pure functions

**Impact**: Eliminates the four gaps identified in the algebra document.
Every other improvement depends on having `join`, `subsumes`, `specificity`,
and `resolvable` as named, tested, callable functions.

**Concrete change**: Create a new file
`src/domain/partialVariableAlgebra.ts` with the four functions from the
algebra document (the TypeScript snippets are already correct). Then
refactor `scoreVariableCandidate()` in `Stage2.ts` to use `subsumes()`
instead of its current per-field equality checks.

In `src/resolution/Stage2.ts`, the function `scoreVariableCandidate`
(lines 239-292) manually checks each facet field. Replace it with:

```typescript
const scoreVariableCandidate = (
  partial: PartialVariableShape,
  variable: Variable
): ScoredVariableCandidate => {
  const matchedFacets = FACET_KEYS.filter(
    key => partial[key] !== undefined && partial[key] === variable[key]
  );
  return {
    variable,
    matchedFacets,
    score: matchedFacets.length
  };
};
```

And add a `resolvable()` gate before candidate scoring so that partial
assignments lacking measuredProperty or statisticType never produce
matches.

### 2. Add the resolvability gate to the facet decomposition lane

**Impact**: Directly addresses the "wrong-new-match" eval bucket. This is
the single change most likely to improve precision.

**Concrete change**: In `src/resolution/Stage2.ts`, in
`handleFacetDecomposition()`, after building `partial` (line 447) and
before candidate scoring (line 492), add:

```typescript
if (!resolvable(partial)) {
  appendEscalation(state, buildFacetDecompositionEscalation(
    postContext, residual,
    hasPartialDecomposition(partial) ? partial : undefined,
    [], matchedSurfaceForms, unmatchedSurfaceForms,
    `partial assignment not resolvable: missing ${
      partial.measuredProperty === undefined ? "measuredProperty" : "statisticType"
    }`
  ));
  return;
}
```

### 3. Structural disambiguation via Agent narrowing

**Impact**: Breaks ties in the most common ambiguity case -- multiple
Variables share the same facet decomposition but belong to different
publishers.

**Concrete change**: In `src/resolution/Stage2.ts`, after the
`topCandidates.length > 1` check (line 522), before escalating, look for
an Agent match in `state.matches` or `state.stage1MatchKeys`. If found,
build an inverse index from the registry: Agent -> Dataset IDs ->
Variable IDs. Filter `topCandidates` to those whose Variable appears in a
Dataset published by the matched Agent. This requires adding a
`datasetIdsByAgentId` and `variableIdsByDatasetId` inverse map to
`DataLayerRegistryLookup` in `src/resolution/dataLayerRegistry.ts` (Gap 5).

In `dataLayerRegistry.ts`, in `buildPreparedRegistry()`, after the
existing index-building loops, add:

```typescript
const datasetIdsByAgentId = new Map<string, Set<string>>();
for (const dataset of seed.datasets) {
  if (dataset.publisherAgentId) {
    const set = datasetIdsByAgentId.get(dataset.publisherAgentId) ?? new Set();
    set.add(dataset.id);
    datasetIdsByAgentId.set(dataset.publisherAgentId, set);
  }
}
```

### 4. Add a CompoundSurfaceForm type for cross-dimension entries

**Impact**: Enables "Henry Hub" to project onto 3 dimensions in a single
vocabulary entry instead of requiring three separate entries in three
different scheme files.

**Concrete change**: Create
`src/resolution/facetVocabulary/compoundSurfaceForm.ts` with a schema
that maps one normalized surface form to a `PartialVariableShape` (not
a single canonical value). Add a `matchCompound()` function that runs
the same boundary-delimited scan but returns a partial assignment directly.
Call it in `handleFacetDecomposition()` before the per-dimension scans,
and join its result into `partialDraft`.

The entry schema:

```typescript
export const CompoundSurfaceFormEntry = Schema.Struct({
  surfaceForm: Schema.String,
  normalizedSurfaceForm: Schema.String,
  projection: PartialVariableShape,  // the multi-dimension mapping
  provenance: SurfaceFormProvenance,
  addedAt: IsoTimestamp
});
```

### 5. Unified confidence scoring on Stage2Evidence

**Impact**: Enables the tiered evidence framework described above and
makes the corroboration/escalation decision auditable.

**Concrete change**: Add a `confidence` field to the `Stage2Evidence`
union. For `FacetDecompositionEvidence`, compute it as
`matchedFacets.length / FACET_KEYS.length` (a [0,1] score reflecting
specificity as a fraction). For fuzzy evidence, the `score` field already
exists. Then the combination rule becomes: accept if max confidence across
all evidence exceeds 0.85 and no evidence conflicts; escalate if max
confidence is in [0.60, 0.85); reject if below 0.60.

In `src/domain/stage2Evidence.ts`, add to the base of each tagged struct:

```typescript
confidence: ZeroToOneScore,
tier: Schema.Literals(["entailment", "strong-heuristic", "weak-heuristic"])
```

This lets `Stage2Result` consumers sort and filter evidence by tier without
inspecting the signal type, which decouples the decision logic from the
evidence-production logic.

---

## Summary of formal terms for the students' reference

| Their concept | Proper CS/NLP term | Key citation |
|---------------|-------------------|-------------|
| Normalization | Text canonicalization | Unicode TR15 (NFKC) |
| Substring matching | Boundary-delimited pattern scan (maximal munch) | Aho & Ullman, compiler lexical analysis |
| Surface form lookup | Dictionary-based NER / lexicon probe | Jurafsky & Martin, ch. 17 |
| canonical value | Equivalence class representative | SKOS reference (W3C) |
| Facet decomposition | Parallel independent scan + lattice join | Ranganathan (faceted classification) |
| Evidence combination | Tiered fusion with lexicographic precedence | Fellegi-Sunter (record linkage) |
| Fuzzy matching | Jaccard bag similarity | Jaccard 1912, standard IR |
| Closed-world gap | Open/closed world mismatch | Reiter 1978, CWA |
