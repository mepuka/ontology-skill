# OEO Import Rebuild Plan — `energy-intel` V2

**Authored:** 2026-05-04 by `ontology-conceptualizer` (V2 iteration)
**Reviewer:** Mepuka Kessy (`kokokessy@gmail.com`)
**Reviewed at:** 2026-05-04
**Source:** [scope-v2.md § In-scope item 3](scope-v2.md), source plan §3.1, [topic-vocabulary-mapping.md](topic-vocabulary-mapping.md)

This document specifies the rebuilt OEO topic subset for V2 — `imports/oeo-topic-subset.ttl`. The architect implements the build per this spec.

---

## 1. Why a rebuild

The V1 OEO subsets — `imports/oeo-{technology,carrier}-subset-fixed.ttl` — are insufficient for the V2 editorial topic catalog. They were extracted to support `ei:aboutTechnology` upper-alignment from the V0 anti-pattern review, not the editorial topic vocabulary.

Specifically, **V1 subsets are missing**:

- `OEO_00010427` (solar power technology)
- `OEO_00010424` (wind power technology)
- `OEO_00010439` (nuclear power technology)
- `OEO_00020366` (energy storage technology)
- All grid leaves (`OEO_00000143`, `OEO_00110019`, `OEO_00110020`)
- Carbon-capture family (`OEO_00010138`, `OEO_00010139`, `OEO_00010141`, `OEO_00010455`)
- Policy / market / climate classes (~10 more)

A rebuild against the full `imports/oeo-full.owl` source is the cleanest path forward.

---

## 2. Source

**File:** `/Users/pooks/Dev/ontology_skill/ontologies/energy-intel/imports/oeo-full.owl`
**Format:** OWL/XML
**Size:** 3.7 MB
**Triple count:** 35,333 (verified this session)
**Version:** OEO 2.11.0 (per V0 conceptualizer trace; consistent with V1 imports)

The file is local; the rebuild does not require any network access.

---

## 3. Target

**Output file:** `/Users/pooks/Dev/ontology_skill/ontologies/energy-intel/imports/oeo-topic-subset.ttl`
**Format:** Turtle (.ttl), per CLAUDE.md serialization standard
**Expected size:** ~50-150 KB after BFO+RO strip (estimate based on V1 subset shapes)

The output is parallel to V1's `imports/oeo-{technology,carrier}-subset-fixed.ttl` files. V1 subsets are KEPT IN PLACE — they continue to back `ei:aboutTechnology`'s upper alignment surface. The new V2 subset is a parallel topic-grade subset for `ei:narrativeAboutTopic`'s value catalog.

---

## 4. Method — `robot extract --method BOT`

### 4.1 Step 1: Run BOT extraction

ROBOT command:

```bash
.local/bin/robot extract \
  --method BOT \
  --input ontologies/energy-intel/imports/oeo-full.owl \
  --term-file ontologies/energy-intel/imports/oeo-topic-seeds.txt \
  --output /tmp/oeo-topic-subset-raw.ttl
```

Where `oeo-topic-seeds.txt` contains the 41 verified IRIs (one per line):

```
https://openenergyplatform.org/ontology/oeo/OEO_00000020
https://openenergyplatform.org/ontology/oeo/OEO_00000088
https://openenergyplatform.org/ontology/oeo/OEO_00000115
https://openenergyplatform.org/ontology/oeo/OEO_00000143
https://openenergyplatform.org/ontology/oeo/OEO_00000146
https://openenergyplatform.org/ontology/oeo/OEO_00000191
https://openenergyplatform.org/ontology/oeo/OEO_00000199
https://openenergyplatform.org/ontology/oeo/OEO_00000212
https://openenergyplatform.org/ontology/oeo/OEO_00000220
https://openenergyplatform.org/ontology/oeo/OEO_00000292
https://openenergyplatform.org/ontology/oeo/OEO_00000384
https://openenergyplatform.org/ontology/oeo/OEO_00000446
https://openenergyplatform.org/ontology/oeo/OEO_00010138
https://openenergyplatform.org/ontology/oeo/OEO_00010139
https://openenergyplatform.org/ontology/oeo/OEO_00010141
https://openenergyplatform.org/ontology/oeo/OEO_00010212
https://openenergyplatform.org/ontology/oeo/OEO_00010214
https://openenergyplatform.org/ontology/oeo/OEO_00010258
https://openenergyplatform.org/ontology/oeo/OEO_00010424
https://openenergyplatform.org/ontology/oeo/OEO_00010426
https://openenergyplatform.org/ontology/oeo/OEO_00010427
https://openenergyplatform.org/ontology/oeo/OEO_00010428
https://openenergyplatform.org/ontology/oeo/OEO_00010430
https://openenergyplatform.org/ontology/oeo/OEO_00010431
https://openenergyplatform.org/ontology/oeo/OEO_00010438
https://openenergyplatform.org/ontology/oeo/OEO_00010439
https://openenergyplatform.org/ontology/oeo/OEO_00010455
https://openenergyplatform.org/ontology/oeo/OEO_00010485
https://openenergyplatform.org/ontology/oeo/OEO_00020063
https://openenergyplatform.org/ontology/oeo/OEO_00020065
https://openenergyplatform.org/ontology/oeo/OEO_00020069
https://openenergyplatform.org/ontology/oeo/OEO_00020075
https://openenergyplatform.org/ontology/oeo/OEO_00020366
https://openenergyplatform.org/ontology/oeo/OEO_00050000
https://openenergyplatform.org/ontology/oeo/OEO_00110019
https://openenergyplatform.org/ontology/oeo/OEO_00110020
https://openenergyplatform.org/ontology/oeo/OEO_00140049
https://openenergyplatform.org/ontology/oeo/OEO_00140150
https://openenergyplatform.org/ontology/oeo/OEO_00140151
https://openenergyplatform.org/ontology/oeo/OEO_00240030
https://openenergyplatform.org/ontology/oeo/OEO_00310000
```

**Why BOT (Bottom-up Term-extraction):** BOT preserves the ancestry chain (every superclass of each seed is included), so the SPARQL `(skos:broader|rdfs:subClassOf)*` walk has a complete hierarchy to traverse. Alternative methods like STAR (specific term + relations) would not pull in the parent chain.

The output `/tmp/oeo-topic-subset-raw.ttl` will be larger than the final subset because BOT includes:
- All 41 seed classes
- Every superclass of each seed (transitively)
- Some IAO classes (data item, etc.) inherited from OEO's upper structure
- Some BFO classes (Continuant, IndependentContinuant, etc.) inherited from OEO's upper structure
- Some RO properties

Estimated raw size: 200-500 KB.

### 4.2 Step 2: BFO+RO strip

The raw extract carries BFO and RO axioms that conflict with V0's BFO 2020 import (the V0 anti-pattern review § 16 documented this). The strip pass removes them, mirroring V1's `imports/oeo-{technology,carrier}-subset-fixed.ttl` build.

ROBOT commands:

```bash
.local/bin/robot remove \
  --input /tmp/oeo-topic-subset-raw.ttl \
  --term-file ontologies/energy-intel/imports/bfo-terms-to-remove.txt \
  --select complement \
  --output /tmp/oeo-topic-subset-bfo-stripped.ttl

.local/bin/robot remove \
  --input /tmp/oeo-topic-subset-bfo-stripped.ttl \
  --term-file ontologies/energy-intel/imports/upper-axiom-leak-terms.txt \
  --select complement \
  --output ontologies/energy-intel/imports/oeo-topic-subset.ttl
```

Where `bfo-terms-to-remove.txt` and `upper-axiom-leak-terms.txt` are the V1-built strip lists already in the repo. (The V1 `imports/oeo-technology-subset-fixed.ttl` build used these same lists; reusing them ensures consistency with the V1 import pattern.)

### 4.3 Step 3: Verify reasoner-clean

After the strip, the architect runs HermiT on the merged closure:

```bash
.local/bin/robot merge \
  --input ontologies/energy-intel/energy-intel.ttl \
  --output /tmp/v2-merged.ttl
.local/bin/robot reason \
  --reasoner hermit \
  --input /tmp/v2-merged.ttl \
  --output /tmp/v2-reasoned.ttl
```

**Expected outcome:** HermiT exit 0; zero unsatisfiable classes. Per V1 § 5 punning prediction, this is the same shape that V1 already runs cleanly. The new topic subset adds 41 more class declarations; no new BFO/RO axioms; should not break the closure.

If HermiT reports unsatisfiable classes (low likelihood per V1 prediction), the **fallback plan** is V1's documented escape hatch:

1. Re-extract with `robot extract --method STAR --intermediates none` (drops parent chain; admits OEO IRIs as bare class declarations).
2. The downside is loss of `rdfs:subClassOf` chains within the OEO namespace, which would weaken CQ-N4 and CQ-T1's ability to walk topic hierarchy.
3. Materialise the subClassOf chain as `skos:broader` triples instead — the architect emits `oeo:OEO_xxx skos:broader oeo:OEO_yyy` based on the OEO upstream hierarchy, but in the local Skygest namespace control.
4. CQ-T1 SPARQL paths walk only `skos:broader` (no `rdfs:subClassOf` branch needed under this fallback).

This fallback is empirically not expected to be needed (V1 trace HermiT-clean) but is documented for completeness.

---

## 5. Verification (granularity contract — CQ-T3)

After the strip, before architect-side use, the build script runs the granularity validator:

```sparql
# CQ-T3 (granularity contract) on imports/oeo-topic-subset.ttl
SELECT ?topic WHERE {
  ?topic a ?cls .
  FILTER(?cls = owl:NamedIndividual)
  FILTER NOT EXISTS { ?topic a owl:Class . }
  FILTER NOT EXISTS { ?topic a skos:Concept . }
}
```

**Expected:** zero rows. Any row indicates a granularity violation that must be removed from the topic subset before V2 ships.

The architect's `scripts/extract-oeo-topic-subset.py` (Phase 3 deliverable) performs this verification automatically. If any row is returned, the script fails and reports the violating IRI.

---

## 6. Implementation note: `oeo:OEO_xxx skos:inScheme ei:concept/oeo-topic`

The OEO topic subset (`imports/oeo-topic-subset.ttl`) declares classes only — it does NOT declare `skos:inScheme` triples. SKOS scheme membership is asserted in `modules/concept-schemes/oeo-topics.ttl` (a separate file the architect builds in Phase 3).

This separation is intentional:
- `imports/oeo-topic-subset.ttl` is a verbatim subset of `oeo-full.owl` (BFO+RO-stripped). It carries OEO upstream axioms only. Edits to the file would be re-overwritten on import refresh.
- `modules/concept-schemes/oeo-topics.ttl` is Skygest-side ownership: it declares the runtime topic catalog, the SKOS scheme structure, and the `skos:inScheme` triples that admit each OEO IRI to the catalog. This file is editable and queryable independently of the upstream OEO subset.

---

## 7. Imports manifest update

The architect updates `imports-manifest.yaml` to add a new row:

```yaml
- name: oeo-topic-subset
  source: imports/oeo-full.owl   # local build
  upstream_uri: https://openenergyplatform.org/ontology/oeo/oeo-full.owl
  version: 2.11.0
  extracted_at: "2026-05-DD"     # build date
  extraction_method: "robot extract --method BOT + bfo+ro-strip"
  seed_iris: 41
  output_path: imports/oeo-topic-subset.ttl
  refresh_policy: "Re-extract when oeo-full.owl is upgraded; verify all 41 IRIs still resolve cleanly."
```

The V1 subsets (`oeo-technology-subset-fixed.ttl`, `oeo-carrier-subset-fixed.ttl`) stay in the manifest unchanged.

---

## 8. Architect implementation guidance

The architect MUST produce `scripts/extract-oeo-topic-subset.py` in Phase 3. Required behavior:

1. Read seed IRIs from `imports/oeo-topic-seeds.txt`.
2. Run `robot extract --method BOT` with the seed list against `imports/oeo-full.owl`.
3. Run two `robot remove` passes for BFO+RO strip.
4. Run granularity validator (CQ-T3 SPARQL); fail with structured error if any violation.
5. Verify all 41 seed IRIs resolve cleanly in the output (rdflib parse + label check); fail if any seed missing.
6. Write the result to `imports/oeo-topic-subset.ttl`.
7. Optionally update `imports-manifest.yaml` (or leave for curator).

The architect MUST also:

- Wire `imports/oeo-topic-subset.ttl` into the top-level `energy-intel.ttl` via `owl:imports`.
- Update `catalog-v001.xml` to map the new IRI to the local file (V0/V1 catalog convention).
- Run `robot reason --reasoner hermit` on the V2 closure and confirm exit 0 + zero unsatisfiables.

---

## 9. Open issues

None blocking.

The conceptualizer flags one V3+ consideration:

- **OEO upstream version drift.** When OEO releases v2.12 or later, the seed IRIs may have new labels, new parents, or be deprecated. The curator's import-refresh workflow must re-run the verification (this session's verification script) and surface any candidate that fails the 4-check granularity contract. Not a V2 concern.
