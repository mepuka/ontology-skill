# OEO v2.11.0 Seed IRI Verification Report

**Phase:** ontology-architect, Step 2.5 (Import / Declaration Preflight)
**Date:** 2026-04-22
**Author:** ontology-architect skill
**OEO version:** v2.11.0 (commit `863baadfbe95cb6f50409d820c7ac73fb6550276`,
tarball `https://api.github.com/repos/OpenEnergyPlatform/ontology/tarball/refs/tags/v2.11.0`)
**Merged artifact (local only, not committed):** `/tmp/oeo-v2.11.0/oeo-full.owl` (3.7 MB)

## Method

OEO v2.11.0 does not ship a prebuilt `oeo-full.owl` release artifact. The
source distribution is a set of Manchester-Syntax OMN edit files under
`src/ontology/edits/` plus OWL import extracts under `src/ontology/imports/`
plus a catalog at `src/ontology/catalog-v001.xml`. The Makefile builds
`oeo-full.owl` via `robot merge` on these inputs.

We replicated the merge locally:

```bash
cd src/ontology && robot merge --catalog catalog-v001.xml \
  --input oeo.omn \
  --input edits/oeo-physical.omn --input edits/oeo-physical-axioms.owl \
  --input edits/oeo-sector.omn   --input edits/oeo-social.omn \
  --input edits/oeo-model.omn    --input edits/oeo-import-edits.owl \
  --input edits/oeo-shared.omn   --input edits/oeo-shared-axioms.omn \
  --input edits/oeo-tasks.omn    --input edits/oeo-co-sim.omn \
  --output /tmp/oeo-v2.11.0/oeo-full.owl
```

Candidate IRIs were queried with `robot query` (SPARQL). Subtree sizes are
**asserted only** (no reasoning; asserted subsumption chains only).

## CRITICAL: Namespace correction

The `imports-manifest.yaml` scout row uses the namespace
`http://openenergy-platform.org/ontology/oeo/` (HTTP scheme, HYPHEN in the
domain). OEO v2.11.0 actually mints IRIs under
**`https://openenergyplatform.org/ontology/oeo/`** (HTTPS, NO hyphen).

- Wrong: `http://openenergy-platform.org/ontology/oeo/OEO_00000011`
- Right: `https://openenergyplatform.org/ontology/oeo/OEO_00000011`

This manifest must be patched before `robot extract` is run. The architect
will correct the manifest `source_iri` and all `seed_terms` URIs as part of
the first `modules/*.ttl` slice commit.

Additionally, some edit modules mint IRIs under a sub-namespace
(e.g., `https://openenergyplatform.org/ontology/oeo/oeo-physical/OEO_00080002`).
The `robot extract --method BOT` will pick these up transitively, so no
special handling is required for the extract call itself — but the
manifest `seed_terms` list is unaffected (root IRIs live under the main
namespace).

## Verification table

| # | Candidate IRI | exists? | label | definition (1st sentence) | subtree size (asserted) | verdict |
|---|---|---|---|---|---|---|
| 1 | `oeo:OEO_00000011` | YES | "energy converting component" | An energy converting component is an artificial object that is usually a discrete part of an energy transformation unit with the function of transforming, transferring or changing a certain type of energy. | 50 | **OK as narrow-scope root** — parents in `oeo:OEO_00000061` (artificial object). Material-entity level. Too narrow for "energy technology" (misses storage, grid, renewables-at-site level). |
| 2 | `oeo:OEO_00010385` | YES | "energy transformation function" | An energy transformation function is the function of an artificial object that has been engineered to transform input energy into usable output energy of a different type. | 4 | **REJECT as technology root** — this is a BFO `function` (a realizable entity). 4 subclasses. Wrong tier for `ei:aboutTechnology` (which needs a plan/type, not a function disposition). |
| 3 | `oeo:OEO_00020039` | YES | "energy carrier" | An energy carrier is a material entity that has an energy carrier disposition. | 5 | **OK as carrier root** — parent is `bfo:BFO_0000040` (material entity). Subtree is small (coal, oil, natural gas, etc.); will extend via BOT extraction. Scout estimate was 20-60 — actual 5 asserted root subclasses is at the low end, but BOT extract with transitive closure will bring in coal-type, heating-oil-type, etc. |
| 4 | `oeo:OEO_00140068` | YES | "aggregation type" | An aggregation type is a data descriptor that contains information on the aggregation method applied on a data set. | 1 | **ON WATCH** — subtree of 1 (just the root) means no asserted narrower aggregation-type concepts in v2.11.0. Scout estimate was 5-20. Recommend architect hand-seeds an ei-local `AggregationType` value partition (sum/avg/max/min/count) rather than importing an empty branch. |
| 5 | `oeo:OEO_00000030` (original scope.md candidate) | YES | "oil power unit" | An oil power unit is a power generating unit using oil as fuel. | 1 | **REJECTED** — scout already flagged this; it's a leaf instance, not a root. Excluded from manifest. |

## Additional candidates discovered during verification

Searching for classes with "energy / power / technology / unit" in their
labels and ≥10 transitive subclasses, we found broader roots that better
match the `ei:aboutTechnology` semantics (SKOS concept for the "type of
energy technology an observation is about"):

| IRI | label | subtree | definition (short) |
|---|---|---|---|
| `oeo:OEO_00020102` | "energy transformation unit" | **104** | An energy transformation unit is an artificial object that transforms, changes or transfers a certain type of energy. |
| `oeo:OEO_00000407` | "technology" | 44 | A technology is a plan specification that describes how to combine artificial objects or other material entities and processes. |
| `oeo:OEO_00020267` | "energy technology" | 37 | An energy technology is a technology that describes how to combine energy transformation units, energy transformations, energy carriers and energy in a specific way. |
| `oeo:OEO_00000031` | "power plant" | 34 | A power plant is an energy transformation unit consisting of power generating units... |
| `oeo:OEO_00000334` | "power generating unit" | 30 | A power generating unit is an energy transformation unit that has the function to produce electrical energy. |
| `oeo:OEO_00010423` | "power generation technology" | 22 | A power generation technology is an energy technology that describes how to combine power generating units and energy carriers... |

### Semantic analysis

OEO draws a clean BFO-style distinction:

- **Technology** (`OEO_00000407`) → `iao:plan specification` → `bfo:generically dependent continuant`. The blueprint / information content.
- **Energy transformation unit** (`OEO_00020102`) → `oeo:artificial object` → `bfo:material entity`. The physical thing.

For energy-intel, `ei:aboutTechnology` is intended to let a CMC say
"this claim is about *solar PV*" — where *solar PV* is a **type / kind
of technology**, not a specific physical power plant. That is semantically
a plan-specification, i.e., under `OEO_00020267` "energy technology", not
a material-entity root. **Per BFO alignment, the technology-concept layer
belongs under `energy technology` (plan specification), and the
material-entity layer (`energy transformation unit`) is a parallel
dimension we do NOT need for V0.**

Note also: energy-intel uses OWL-2 punning — `ei:aboutTechnology` has
range `skos:Concept`, and OEO classes can be asserted as
`skos:Concept` instances without violating DL (punning on same IRI across
`owl:Class` + `owl:NamedIndividual`). This keeps the ABox simple ("CMC
is about OEO:energy technology") without forcing full instance-of-class
semantics.

## Recommended seed IRIs (for manifest update)

### oeo-technology subset (root for `ei:aboutTechnology` codomain)

- **Primary root: `oeo:OEO_00020267`** — "energy technology" (37 subtree
  classes, covers renewable generation, nuclear, fossil, storage
  technology, transmission technology, efficiency technology types).
- **Secondary root: `oeo:OEO_00000011`** — "energy converting component"
  (50 subs; overlaps partially; brings in solar cells, fuel cells, heat
  pumps at the *component* tier so downstream SKOS queries don't need
  to alias "solar cell" to "solar PV technology" manually). Pull because
  Skygest posts mix both tiers (e.g., "fuel cell" in one post, "fuel
  cell technology" in another).
- **Optional backup: `oeo:OEO_00000334`** — "power generating unit" (30
  subs; material-entity tier, useful if a V1 post mentions a specific
  plant name that needs a type-of assertion).

**Combined subtree size:** ~90 classes (allowing for some overlap
between technology plan specifications and their component material
entities). Comfortably under the 400-class abort threshold.

### oeo-carrier subset

- **Primary root: `oeo:OEO_00020039`** — "energy carrier" (5 asserted
  subs; BOT extract will pull the full transitive tree including
  coal-kind, gas-kind, etc.). Keep as-scouted.

### oeo-aggregation subset

- **DROP `oeo:OEO_00140068` from OEO import.** The asserted subtree is 1
  (just the root). Instead, **hand-seed** an ei-local value partition
  like `modules/concept-schemes/aggregation-type.ttl` with 4-5 SKOS
  concepts (sum, average, min, max, count). Reasoning: we'd import
  zero useful subclasses; a hand-seeded scheme is more auditable. File a
  curator upstream issue with OEO requesting aggregation-type concepts
  be added.

### Reject (do not include)

- **`oeo:OEO_00010385`** "energy transformation function" — wrong BFO
  tier (function, not plan-spec). Only 4 asserted subs.
- **`oeo:OEO_00000030`** "oil power unit" — already rejected by scout.

## Open points for parent confirmation

1. **Dual root for technology subset (plan + component)** — including
   *both* `OEO_00020267` (technology plan) and `OEO_00000011` (energy
   converting component) in a single BOT extract will import the plan-
   specification axioms AND the component material-entity axioms. This
   means merged-OEO will carry both tiers even though `ei:aboutTechnology
   range skos:Concept` only binds to the plan tier. The downstream
   reasoner impact is negligible (no cross-tier axioms in v2.11.0), but
   the merged ontology footprint grows. **Recommend accepting: the two
   roots together cover the Skygest post vocabulary.**

2. **Drop `oeo-aggregation-2.11.0` import, hand-seed instead** — this is
   a deviation from the scout manifest. Recorded above. Requires
   curator-file upstream-request to OEO.

3. **Manifest patch required** — `source_iri`, `extraction_command
   --input-iri`, and every `seed_terms` URI in the three OEO rows must
   migrate from `http://openenergy-platform.org/ontology/oeo/` to
   `https://openenergyplatform.org/ontology/oeo/`. This is a
   non-behavioral fix (the PURL resolves to the same content) but
   required for `robot extract` to succeed. Will be included in the
   first architect commit.

## Next step

**PAUSE.** Awaiting parent confirmation of:
- Seed-IRI set above (two technology roots, one carrier root, drop the
  OEO aggregation root in favor of hand-seeded value partition).
- Manifest namespace patch.

On confirmation, proceed to:
1. Rewrite `imports-manifest.yaml` OEO rows with corrected namespace and
   updated seed_terms.
2. Run the three `robot extract --method BOT` calls to produce
   `imports/oeo-technology-subset.ttl`, `imports/oeo-carrier-subset.ttl`.
3. Hand-seed `modules/concept-schemes/aggregation-type.ttl` (and the
   already-planned `modules/concept-schemes/temporal-resolution.ttl`).
4. Begin TBox authoring per the module-order rule (agent → media →
   measurement → data).
