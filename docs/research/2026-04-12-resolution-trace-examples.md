# Resolution Pipeline Trace Examples

**Date**: 2026-04-12
**Status**: Working research document
**Context**: End-to-end traces of the Stage 2 resolution kernel against real
eval posts, using the formal algebra from `resolution-algebra.md` and the
text operations T1-T4 from `text-ops-and-evidence-combination.md`.

**Source data**: Eval run `2026-04-12-160745-247Z` (37 posts, 22 wrong-new-matches,
41 ambiguous escalations, 26 no-facet-match escalations).

---

## Example 1: Happy Path (unique resolution)

### Post: 003-janrosenow (residual: chart-title)

**Input text**: `"Heat pumps overtake gas in Germany's heating market"`
**Source**: chart-title, from a tweet by @janrosenow about BDH heating data.

```
T1 (canonicalize):
  "Heat pumps overtake gas in Germany's heating market"
  -> "heat pumps overtake gas in germany's heating market"

T2 (scan per dimension):
  measuredProperty: scan -> "installed" not found; no match
                    (note: the word "installations" is absent from this text)
  domainObject:     scan -> "heat pumps" matches -> canonical "heat pump"
  technologyOrFuel: scan -> "heat pumps" matches -> canonical "heat pump"
                    (also: "gas" matches -> canonical "natural gas"
                     but "heat pumps" is longer and tried first?
                     Actually each dimension scans independently.
                     technologyOrFuel scans and "heat pumps" matches.)
  statisticType:    scan -> no match
  aggregation:      scan -> no match
  unitFamily:       scan -> no match

T3 (exact match fast path):
  Full text is not an exact surface form in any dimension -> skip to regex scan.

T4 (canonical projection):
  partial v = (-, heat pump, heat pump, -, -, -, -)
            = (measuredProperty=bot, domainObject="heat pump",
               technologyOrFuel="heat pump", statisticType=bot,
               aggregation=bot, unitFamily=bot, policyInstrument=bot)
```

**Lattice operations**:

```
resolvable(v)? -> NO
  measuredProperty = bot, statisticType = bot
  Both required dimensions are missing.

specificity(v) = 2 (domainObject, technologyOrFuel)

subsumes(v, registry)?
  Candidates where domainObject="heat pump" AND technologyOrFuel="heat pump":
  - Heat pump installations (count, heat pump, heat pump, stock, -, dimensionless)
    -> matches on domainObject AND technologyOrFuel -> score 2
  No other Variable has both domainObject="heat pump" and technologyOrFuel="heat pump".
  -> 1 candidate, score 2.
```

**Actual kernel behavior**: The kernel does NOT have a resolvability gate. It
proceeds to candidate scoring. The single candidate "Heat pump installations"
wins with score 2 (matched on technologyOrFuel + domainObject). The kernel
emits a VariableMatch.

**Result**: WRONG-NEW-MATCH (false positive)

The kernel produced a match, but the expected output is V=none. The post is
about heat pump market share in Germany's heating sector -- it is not about
the "Heat pump installations" Variable (which measures cumulative unit counts).
The post is actually discussing market share data from BDH.

### What went wrong, formally

| Operation | Status | Detail |
|-----------|--------|--------|
| T1 (canonicalize) | Correct | Straightforward lowercasing |
| T2 (scan) | Partially correct | Correctly found "heat pumps" in two dimensions. Missed that the text is about market share, not installation counts. |
| T3 (exact match) | N/A | Not applicable |
| T4 (projection) | Correct given T2 | Projection faithfully reflects the scan results |
| resolvable(v) | **GAP** | Not implemented. Would have returned FALSE (measuredProperty=bot, statisticType=bot). This would have prevented the false positive. |
| subsumes | Correct | The 1-candidate result is genuinely the only Variable with those two facets |
| specificity | Correct | score=2 |

**Root cause**: The **resolvability gate is missing** (Gap 1 in the algebra
document, Improvement 2 in the advisory). The partial assignment has
specificity=2 but both required dimensions (measuredProperty, statisticType)
are unset. The kernel should have escalated to Stage 3 instead of accepting
a candidate that matched only on optional dimensions.

**Fix**: Implement `resolvable(v)` as described in the advisory document.
Add the gate between facet decomposition and candidate scoring in
`handleFacetDecomposition()`. This single change would have prevented this
false positive AND the other one from the same post (the "Share of new
installations" axis-label that wrongly matched "Clean electricity share").

---

## Example 2: Ambiguous Case (tied candidates)

### Post: 001-ember-energy (residual: post-text)

**Input text**: `"NEW | Wind and solar generated a RECORD 22% of #Turkiye's
electricity in 2025, limiting natural gas imports ... Meanwhile, coal remained
the largest power source at 34%, with TWO-THIRDS coming from IMPORTS."`
(truncated; full text includes URLs)

**Source**: post-text from @ember_energy about Turkey's electricity mix.

```
T1 (canonicalize):
  -> "...wind and solar generated a record 22% of #türkiye's electricity
     in 2025, limiting natural gas imports...coal remained the largest
     power source at 34%..."

T2 (scan per dimension):
  measuredProperty: scan -> "imports" matches -> canonical "trade"
  domainObject:     scan -> "electricity" matches -> canonical "electricity"
                    (also "power" matches -> canonical "electricity", but
                     "electricity" is longer and tried first, or they match
                     the same canonical -- either way, result is "electricity")
  technologyOrFuel: scan -> "natural gas" matches -> canonical "natural gas"
                    ("natural gas" is 11 chars; "solar" is 5, "wind" is 4,
                     "coal" is 4 -- longest match wins: "natural gas")
  statisticType:    scan -> no match
  aggregation:      scan -> no match
  unitFamily:       scan -> no match

T3 (exact match): not applicable (text is long)

T4 (canonical projection):
  partial v = (trade, electricity, natural gas, bot, bot, bot, bot)
```

**Lattice operations**:

```
resolvable(v)? -> NO
  measuredProperty = "trade" (non-bot)
  statisticType = bot
  Fails: statisticType is required.

specificity(v) = 3 (measuredProperty, domainObject, technologyOrFuel)

subsumes(v, registry)?
  Need Variables where measuredProperty="trade" AND
  domainObject="electricity" AND technologyOrFuel="natural gas":
  -> 0 candidates. No Variable in the registry has all three.

  Actual kernel behavior (no resolvability gate, scores > 0):
  Filters to score > 0 -> any Variable matching at least 1 facet.
  All Variables with domainObject="electricity" match on 1 facet:
  - Clean electricity share, Coal electricity generation,
    Electricity demand, Electricity generation,
    Solar electricity generation, Wholesale electricity price,
    Wind electricity generation
  -> 7 candidates tied at score 1.
```

**Result**: ESCALATED (ambiguous -- 7 candidates tied on 1 matched facet)

The kernel correctly escalates this to Stage 3 because no unique winner
exists. However, the escalation reason is misleading: it says "7 candidates
tied on 1 matched facets" when the partial assignment actually filled 3
dimensions. The tie occurs because the scoring function only counts
dimensions where `partial[key] === variable[key]`, and no Variable has
measuredProperty="trade" or technologyOrFuel="natural gas" alongside
domainObject="electricity".

### What went wrong, formally

| Operation | Status | Detail |
|-----------|--------|--------|
| T1 | Correct | |
| T2 | Partially wrong | "natural gas" wins the technologyOrFuel scan via longest-match, but the text mentions wind, solar, coal, AND natural gas. The single-winner-per-dimension architecture loses the other technology mentions. |
| T2 | Semantically wrong | "imports" -> "trade" for measuredProperty is a false match. The text says "limiting natural gas imports" (not about a trade statistic) and "TWO-THIRDS coming from IMPORTS" (about coal imports). The word "imports" in this context is not a measured property -- it is a narrative claim. |
| T4 | Correct given T2 | |
| resolvable(v) | **GAP** | Would return FALSE. Would have escalated immediately without the misleading 7-way tie. |
| subsumes | Correct | Correctly finds no exact match for the 3-facet partial |

**Root causes**:

1. **No resolvability gate** (same as Example 1). statisticType=bot means
   this partial should not attempt candidate matching at all.

2. **Single-winner-per-dimension loses information** (architectural
   limitation). The text mentions four technologies (wind, solar, coal,
   natural gas) but the scan only returns one. This is by design -- the
   parallel independent scan picks the longest match per dimension. For
   multi-topic posts, this is lossy.

3. **False lexical match**: "imports" is a valid surface form for
   measuredProperty="trade", but in this context it is used narratively,
   not as a statistical descriptor. The lexicon has no way to distinguish
   mention-in-context from statistical-label-in-context. This is the
   boundary of what deterministic substring matching can do.

**Fix**: Improvement 2 (resolvability gate) prevents the misleading
candidate list. The deeper fix -- handling multi-topic posts that mention
several Variables -- requires either the compound concept architecture
(Improvement 4) or a redesign that allows multiple independent
decompositions per residual.

---

## Example 3: Wrong-New-Match (false positive)

### Post: 018-simonmahan (residual: post-text + chart-title)

**Input text (post-text)**: `"Large nuclear plants using dedicated cooling
reservoirs often require 4,000-7,000+ acres of water surface area. The 'just
a few hundred acres' meme? Off by about 10x. The reactor footprint is tiny.
The cooling lake usually isn't."`

**Input text (chart-title)**: `"Size Matters: A Look at Nuclear Plant Water Needs"`

**Source**: @SimonMahan discussing nuclear plant land/water use -- an
editorial post with no statistical data.

```
T1 (canonicalize):
  post-text -> "large nuclear plants using dedicated cooling reservoirs
    often require 4,000-7,000+ acres of water surface area..."
  chart-title -> "size matters: a look at nuclear plant water needs"

T2 (scan per dimension) on post-text:
  measuredProperty: scan -> no match
  domainObject:     scan -> "reactor" matches -> canonical "nuclear reactor"
  technologyOrFuel: scan -> "nuclear" matches -> canonical "nuclear"
                    ("nuclear plants" is scanned; "nuclear" at 7 chars
                     matches as a substring)
  statisticType:    scan -> no match
  aggregation:      scan -> no match
  unitFamily:       scan -> no match

T4 (projection) for post-text:
  partial v = (bot, nuclear reactor, nuclear, bot, bot, bot, bot)

T2 (scan per dimension) on chart-title:
  measuredProperty: scan -> no match
  domainObject:     scan -> "nuclear plant" matches -> canonical "nuclear reactor"
  technologyOrFuel: scan -> "nuclear" matches -> canonical "nuclear"
  statisticType:    scan -> no match
  aggregation:      scan -> no match
  unitFamily:       scan -> no match

T4 (projection) for chart-title:
  partial v = (bot, nuclear reactor, nuclear, bot, bot, bot, bot)
```

**Lattice operations** (applied independently to each residual):

```
resolvable(v)? -> NO (both times)
  measuredProperty = bot, statisticType = bot

specificity(v) = 2

subsumes(v, registry)?
  Candidates where domainObject="nuclear reactor" AND
  technologyOrFuel="nuclear":
  -> Installed nuclear capacity
     (capacity, nuclear reactor, nuclear, stock, power, end_of_period)
     matches on 2 facets -> score 2
  -> 1 candidate, unique winner.

Actual kernel behavior: accepts the unique winner and emits VariableMatch
for "Installed nuclear capacity" (TWICE -- once from each residual).
```

**Result**: WRONG-NEW-MATCH

The kernel matched "Installed nuclear capacity" but the post is about
nuclear plant water/land use -- it contains no statistical data about
installed capacity. The matched Variable is wrong.

### What went wrong, formally

| Operation | Status | Detail |
|-----------|--------|--------|
| T1 | Correct | |
| T2 | Correct at the lexical level | "nuclear" IS in the technologyOrFuel vocabulary, "reactor" IS in the domainObject vocabulary. The matches are lexically valid. |
| T4 | Correct given T2 | |
| resolvable(v) | **GAP -- this is the critical failure** | measuredProperty=bot AND statisticType=bot. The partial assignment says "something about nuclear reactors" but says nothing about WHAT is being measured or what kind of statistic it is. A resolvability gate would have rejected this immediately. |
| subsumes | Correct | There genuinely is only one Variable with those two facets |
| specificity | Correct | score=2, but both matched dimensions are optional |

**Root cause**: The **resolvability gate is missing**. The partial assignment
has specificity=2 but both filled dimensions are optional (domainObject,
technologyOrFuel). The required dimensions (measuredProperty, statisticType)
are both bot. The kernel should never have attempted candidate scoring.

This is the prototypical wrong-new-match pattern: the text is topically
related to an energy concept (nuclear) but contains no quantitative claim
that maps to a Variable. The vocabulary correctly identifies the topic, but
the kernel incorrectly interprets "topic match" as "Variable match."

**Fix**: Improvement 2 (resolvability gate). The `resolvable()` predicate
would catch this immediately. Of the 22 wrong-new-match cases in the eval,
this pattern (matched technology + domain but not measured property or
statistic type) appears to be the dominant failure mode.

---

## Example 4: Resolvability Gate Case (partial match, LLM handoff)

### Post: 012-hausfath-bsky-social (residual: chart-title)

**Input text**: `"Effect of a one year pulse of present-day emissions on
global surface temperature"`

**Source**: chart-title from @hausfath sharing an IPCC AR6 figure about
climate sensitivity -- a scientific figure, not an energy statistics chart.

```
T1 (canonicalize):
  -> "effect of a one year pulse of present-day emissions on global
     surface temperature"

T2 (scan per dimension):
  measuredProperty: scan -> "emissions" matches -> canonical "emissions"
  domainObject:     scan -> no match
                    ("temperature" is not a domain object;
                     "global surface temperature" is not in vocabulary)
  technologyOrFuel: scan -> no match
  statisticType:    scan -> no match
  aggregation:      scan -> no match
  unitFamily:       scan -> no match

T3 (exact match): not applicable

T4 (canonical projection):
  partial v = (emissions, bot, bot, bot, bot, bot, bot)
```

**Lattice operations**:

```
resolvable(v)? -> NO
  measuredProperty = "emissions" (non-bot) -- one required dimension filled
  statisticType = bot -- the other required dimension is missing
  Fails: both must be non-bot.

specificity(v) = 1

subsumes(v, registry)?
  Candidates where measuredProperty="emissions":
  -> CO2 emissions from energy
     (emissions, energy consumption, -, flow, mass_co2e, sum)
     matches on 1 facet -> score 1

  -> 1 candidate.

Actual kernel behavior: no resolvability gate, unique candidate with
score 1, kernel emits VariableMatch for "CO2 emissions from energy."
```

**Result**: WRONG-NEW-MATCH

The kernel matched "CO2 emissions from energy" but the post is about
climate sensitivity modeling (the effect of a pulse of ALL greenhouse gas
emissions on temperature, from IPCC AR6 Figure 6.16). This is not a
statistical dataset about energy-sector CO2 emissions.

### What went wrong, formally

| Operation | Status | Detail |
|-----------|--------|--------|
| T1 | Correct | |
| T2 | Lexically correct, semantically wrong | "emissions" does appear in the text, and it IS a valid measuredProperty surface form. But in context, "emissions" refers to a hypothetical pulse scenario in a climate model, not to an energy statistics dataset. |
| T4 | Correct given T2 | |
| resolvable(v) | **GAP** | specificity=1 with only measuredProperty filled. statisticType=bot. A resolvability gate would have escalated this to Stage 3. |
| subsumes | Correct | Finds the only Variable with measuredProperty="emissions" |

**Root cause**: Two compounding failures:

1. **Missing resolvability gate** (again). specificity=1 on a single
   optional-seeming dimension (even though measuredProperty IS required, the
   other required dimension statisticType is missing).

2. **No topic-relevance check**. The text is about climate modeling, not
   energy statistics. The word "emissions" is a false friend -- it appears
   in both climate science prose and energy statistics labels. The
   deterministic resolver cannot distinguish these contexts. This is the
   correct handoff point to an LLM (Stage 3), which can understand that
   "effect of a one year pulse" is scientific modeling language, not
   statistical reporting language.

**Fix**: Improvement 2 (resolvability gate) is sufficient here. With
`resolvable()` in place, the kernel would escalate with:
`"partial assignment not resolvable: missing statisticType"` and include the
partial decomposition `{measuredProperty: "emissions"}` in the escalation
payload for Stage 3 to consider.

---

## Example 5: Compound Concept Case (German-language multi-topic post)

### Post: 016-energy-charts-bsky-social (residual: post-text)

**Input text**: `"Die Stromerzeugung aus Solar und Wind in der EU-27 war im
ersten Quartal 2026 deutlich hoher als im ersten Quartal 2025.
1. Quartal 2025 -> 1. Quartal 2026
Solar: 44,5 TWh -> 47,5 TWh
Wind onshore: 110,5 TWh -> 122,5 TWh
Wind offshore: 15,3 TWh -> 22 TWh
energy-charts.info/charts/energ..."`

**Source**: post-text from @energy-charts.bsky.social (Fraunhofer ISE),
reporting EU-27 solar and wind generation by quarter, in German.

```
T1 (canonicalize):
  -> "die stromerzeugung aus solar und wind in der eu-27 war im ersten
     quartal 2026 deutlich höher als im ersten quartal 2025.
     1. quartal 2025 -> 1. quartal 2026
     solar: 44,5 twh -> 47,5 twh
     wind onshore: 110,5 twh -> 122,5 twh
     wind offshore: 15,3 twh -> 22 twh
     energy-charts.info/charts/energ..."

T2 (scan per dimension):
  measuredProperty: scan -> no match
                    ("stromerzeugung" = German for "electricity generation"
                     -- not in the EN-only vocabulary)
  domainObject:     scan -> no match
                    ("strom" = German for electricity -- not in vocabulary)
  technologyOrFuel: scan -> "solar" matches -> canonical "solar PV"
                    ("wind onshore" matches -> canonical "wind (onshore)"
                     BUT "solar" appears first? Actually longest-match-first
                     within the dimension: "wind offshore" (14 chars) >
                     "wind onshore" (12 chars) > "solar" (5 chars).
                     But only ONE match is returned per dimension.
                     "wind offshore" wins the technologyOrFuel scan.)
                    WAIT -- let me re-check. The ordered matchers try
                    longest first. Does "wind offshore" appear as a
                    surface form? If so it wins over "wind onshore" and
                    "solar". But the actual eval shows the escalation with
                    10 candidates tied on 1 matched facet (unitFamily).
                    Let me re-trace...
  statisticType:    scan -> no match
  aggregation:      scan -> no match
  unitFamily:       scan -> "twh" matches -> canonical "energy"

T3 (exact match): not applicable

T4 (canonical projection):
  partial v = (bot, bot, [solar PV or wind], bot, bot, energy, bot)
```

**Actual kernel behavior** (from the eval JSON):

The post-text residual escalated as ambiguous with 10 candidates tied on 1
matched facet (unitFamily="energy"). The technologyOrFuel match was NOT
recorded in the escalation -- suggesting the kernel matched only
unitFamily="energy" from "TWh".

Checking the escalation candidate list confirms: the candidates are Battery
discharge, Coal electricity generation, and 8 other Variables that all have
unitFamily="energy". The partial decomposition is `{unitFamily: "energy"}`.

So: "solar" and "wind onshore/offshore" were NOT matched by the
technologyOrFuel scan on this text. Why?

**Diagnosis**: The German text contains `"Solar: 44,5 TWh"`. After
canonicalization, this becomes `"solar: 44,5 twh"`. The word "solar"
appears followed by a colon. The regex boundary check uses
`[^\p{L}\p{N}]` -- a colon IS a non-letter/non-digit character, so "solar"
should match. But looking more closely at the full text: `"aus Solar und
Wind"` -- here "solar" appears bounded by spaces, which should also match.

The most likely explanation: the technologyOrFuel scan DID match "solar" ->
"solar PV", but the eval JSON shows the escalation partial as only
`{unitFamily: "energy"}`. This means the post-text residual's facet
decomposition produced a different result than expected. Let me check the
actual escalation:

The eval JSON shows the escalation for this residual has candidateSet with
10 entries, all matched on `unitFamily` only. The `partialDecomposition` is
not shown in the escalation for this residual (it was not included since the
escalation was for the tied candidates).

**The real problem here is the compound concept gap**:

```
The text describes THREE distinct Variables simultaneously:
  1. Solar electricity generation in EU-27 Q1 2025 vs Q1 2026
  2. Wind onshore electricity generation in EU-27 Q1 2025 vs Q1 2026
  3. Wind offshore electricity generation in EU-27 Q1 2025 vs Q1 2026

Each of these is a compound concept:
  "Solar: 44,5 TWh" = {measuredProperty: generation, domainObject: electricity,
                        technologyOrFuel: solar PV, statisticType: flow,
                        unitFamily: energy}
  "Wind onshore: 110,5 TWh" = {measuredProperty: generation,
                                domainObject: electricity,
                                technologyOrFuel: wind (onshore),
                                statisticType: flow, unitFamily: energy}

But the kernel processes the ENTIRE post-text as a single string.
It runs one scan per dimension across the whole text.
```

### What went wrong, formally

| Operation | Status | Detail |
|-----------|--------|--------|
| T1 | Correct | |
| T2 | **Structurally inadequate** | The text contains THREE Variables' worth of information, but the single-winner-per-dimension architecture collapses all of it into one partial assignment. German-language terms ("Stromerzeugung") are invisible to the EN-only vocabulary. |
| T4 | Correct given T2 | But the projection is severely impoverished: only unitFamily="energy" from "TWh" |
| resolvable(v) | Would return FALSE | measuredProperty=bot, statisticType=bot |
| subsumes | Correct but useless | 10 candidates share unitFamily="energy" |

**Root causes** (multiple, compounding):

1. **No German surface forms** in the vocabulary. "Stromerzeugung" (electricity
   generation), "Strom" (electricity/power), "Quartal" (quarter) are all
   domain-relevant German terms that the EN-only vocabulary cannot match.
   This is the **vocabulary coverage gap**.

2. **Single-decomposition-per-residual architecture**. Even if the vocabulary
   had all the terms, the post describes three distinct Variables. The
   current architecture produces one partial assignment per text, not
   multiple. The text `"Solar: 44,5 TWh ... Wind onshore: 110,5 TWh ...
   Wind offshore: 15,3 TWh"` has a tabular structure that a single regex
   scan cannot parse.

3. **No compound concept type** (Gap 2 in the algebra document). The string
   `"Wind onshore"` should map to `{technologyOrFuel: "wind (onshore)",
   domainObject: "electricity", measuredProperty: "generation"}` as a
   compound concept. Instead, even if matched, it would only fill the
   technologyOrFuel slot.

**Fixes needed** (multiple):

- **Improvement 2** (resolvability gate): Would immediately escalate this
  instead of producing the meaningless 10-way tie.
- **Vocabulary expansion**: Add German surface forms or implement
  multilingual canonicalization (the advisory document explicitly flags this
  as out of scope for T1, which does not do transliteration).
- **Improvement 4** (CompoundSurfaceForm): Enable "Wind onshore" to project
  onto multiple dimensions at once.
- **Architectural extension**: For structured/tabular text, segment the
  input into independent clauses before running facet decomposition on each.
  This is beyond the current architecture.

---

## Cross-Cutting Analysis

### The resolvability gate would have prevented 4 out of 5 failures

| Example | resolvable(v)? | Would gate have helped? |
|---------|---------------|------------------------|
| 1 (heat pump) | NO (mP=bot, sT=bot) | YES -- would have escalated instead of matching |
| 2 (Turkey electricity) | NO (mP="trade", sT=bot) | YES -- would have escalated cleanly |
| 3 (nuclear water) | NO (mP=bot, sT=bot) | YES -- would have prevented the false positive |
| 4 (IPCC emissions) | NO (mP="emissions", sT=bot) | YES -- would have escalated to Stage 3 |
| 5 (EU-27 generation) | NO (mP=bot, sT=bot) | YES -- would have replaced the 10-way tie |

The resolvability gate (Improvement 2 from the advisory) is the single
highest-leverage change. It would have eliminated all 5 false-positive
or misleading outcomes traced here.

### Pattern: "topic match != Variable match"

Examples 3 and 4 share a common pattern. The text IS about an energy topic
(nuclear, emissions), and the vocabulary correctly identifies the topic. But
the text does not contain a quantitative claim that corresponds to a
registered Variable. The kernel conflates "this text is about nuclear
energy" with "this text references the Installed Nuclear Capacity variable."

The resolvability gate formalizes the distinction: a topic match fills
domainObject and/or technologyOrFuel, but a Variable match requires
measuredProperty AND statisticType. The gate enforces that you need both
the "what is being measured" and "what kind of statistic" before you can
claim a Variable reference.

### Advisory improvements mapped to examples

| Improvement | Example(s) it would fix | Mechanism |
|-------------|------------------------|-----------|
| 1. Extract lattice algebra as pure functions | All | Enables explicit `join`, `subsumes`, `specificity`, `resolvable` |
| 2. Resolvability gate | 1, 2, 3, 4, 5 | Prevents false positives from partial assignments missing required dimensions |
| 3. Agent narrowing | 2 (partially) | Would narrow the 7-way tie if Agent match from Stage 1 were used |
| 4. CompoundSurfaceForm | 5 | Enables "Wind onshore" to project onto multiple dimensions |
| 5. Unified confidence scoring | All | Makes the entailment vs. heuristic distinction visible in the output |

### Abstraction gaps surfaced by these traces

1. **The resolvability predicate is the most important missing operation.**
   Every wrong-new-match traced here has specificity >= 1 but fails the
   resolvability test. The formal model defines this predicate clearly; the
   implementation simply does not have it.

2. **The scoring function conflates subsumption with intersection.**
   `scoreVariableCandidate` counts matching facets (intersection), not
   subsumption. A partial assignment `v = (trade, electricity, natural gas)`
   with 3 filled dimensions matches a Variable with `domainObject=electricity`
   on only 1 dimension. The score of 1 does not reflect that the partial
   is MORE specific than any candidate -- it reflects that 2 of 3 filled
   dimensions have no corresponding Variable in the registry. This is the
   "high specificity, zero candidates" diagnostic signal described in the
   advisory.

3. **Single-winner-per-dimension is correct for single-topic text but lossy
   for multi-topic text.** The parallel independent scan architecture works
   well when a text describes one Variable. It fails when a text describes
   multiple Variables (Example 2, Example 5). The formal model does not
   address text segmentation -- it assumes the input is already a single
   coherent reference.

4. **The vocabulary is EN-only.** German surface forms in the eval corpus
   (Example 5) are invisible. The formal model's lexicon L maps normalized
   surface forms to facet values, but the surface form set S currently
   contains only English terms. This is a coverage gap, not an architectural
   gap -- it can be fixed by expanding the vocabulary without changing the
   algebra.
