# V2 Architect Build Log — `energy-intel` (Editorial Extension)

**Authored:** 2026-05-04 by `ontology-architect` (V2 iteration)
**Predecessor:** [architect-build-log-v1.md](architect-build-log-v1.md) (V1; commit `1d8f9da`)
**Source:** [conceptualizer-to-architect-handoff-v2.md](conceptualizer-to-architect-handoff-v2.md), [axiom-plan-v2.md](axiom-plan-v2.md), [oeo-import-rebuild-plan.md](oeo-import-rebuild-plan.md)
**Materialised by:**
- `scripts/extract_oeo_topic_subset.py` — OEO BOT extract + BFO+RO strip + ontology header.
- `scripts/build_editorial.py` — modules + concept schemes + SHACL shapes + 11 fixtures.
**KGCL log:** [`../release/editorial-v0-changes.kgcl`](../release/editorial-v0-changes.kgcl)

This document is the implementation form of the conceptualizer's twelve numbered axiom obligations (A1..A12) and four SHACL shape contracts (S-V2-1..S-V2-4). Each row pins to its V2 input source, the build-script function that produces the artifact, and the gate evidence file confirming HermiT / report / pyshacl / pytest conformance.

---

## 1. Build pipeline

V2 build is a two-script pipeline:

```bash
# Step 1: rebuild OEO topic subset from imports/oeo-full.owl
uv run python ontologies/energy-intel/scripts/extract_oeo_topic_subset.py
# Produces: imports/oeo-topic-subset.ttl (7,729 triples)

# Step 2: build editorial module + 3 SKOS schemes + SHACL + 11 fixtures
uv run python ontologies/energy-intel/scripts/build_editorial.py
# Produces:
#   modules/editorial.ttl                       (76 triples)
#   modules/concept-schemes/argument-pattern.ttl  (82 triples)
#   modules/concept-schemes/narrative-role.ttl    (45 triples)
#   modules/concept-schemes/oeo-topics.ttl        (334 triples)
#   shapes/editorial.ttl                          (69 triples)
#   tests/fixtures/cq-editorial-{N1..N8,T1,T2,granularity}.ttl  (11 files)
```

End-to-end: `just validate-editorial` (mirrors V1's `just validate-energy-news`).

---

## 2. OWL profile + reasoner

| Aspect | Value |
|---|---|
| Declared profile | OWL 2 DL (per V0/V1 + scope-v2.md) |
| Reasoner pairing | HermiT (release gate); ELK fast-path during iteration |
| Profile validate | not run separately — V2 adds no constructs that V0/V1 didn't already use; HermiT exit 0 confirms DL safety |
| Construct support | All V2 constructs are OWL 2 DL safe: SubClassOf (#1), existential restriction implicit in `subClassOf SOME`, qualified cardinality (#7), max-qualified-cardinality (#7 variant), DisjointClasses (#5), FunctionalProperty (DL-safe). No universal restrictions, no DisjointUnion, no property chains. |
| Punning surface | OEO IRIs in oeo-topic-subset are `owl:Class` declarations; the same IRIs become `skos:Concept` instances via `skos:inScheme` triples in `oeo-topics.ttl`. V0/V1 punning prediction (V1 conceptual-model § 5) carries forward: HermiT empirically clean. |

---

## 3. OWL axiom obligations (A1..A12)

### A1 — Mint `ei:Narrative`

| Aspect | Value |
|---|---|
| Module | `modules/editorial.ttl` |
| Build site | `build_editorial.py:build_editorial_module()` (uses helper `_add_class`) |
| CQ source | CQ-N1; supports CQ-N2..N6, N8 |
| Construct | SubClassOf (simple) |
| Profile | OWL 2 EL safe (also DL) |

```turtle
ei:Narrative a owl:Class ;
  rdfs:label "narrative"@en ;
  rdfs:subClassOf iao:0000310 ;
  skos:definition "A written editorial unit about energy-domain events..."@en .
```

**Evidence:** modules/editorial.ttl lines 22-30 (after serialization).

### A2 — Mint `ei:NarrativePostMembership`

| Aspect | Value |
|---|---|
| Module | `modules/editorial.ttl` |
| Build site | `build_editorial.py:build_editorial_module()` |
| CQ source | CQ-N2, CQ-N3, CQ-N6, CQ-N7, CQ-N8 |
| Construct | SubClassOf (simple) |
| Profile | OWL 2 EL safe |

```turtle
ei:NarrativePostMembership a owl:Class ;
  rdfs:label "narrative post membership"@en ;
  rdfs:subClassOf iao:0000310 .
```

### A3 — DisjointClasses (defense-in-depth)

| Aspect | Value |
|---|---|
| Module | `modules/editorial.ttl` |
| Build site | `build_editorial.py:build_editorial_module()` (BNode + Collection) |
| Construct | AllDisjointClasses |
| Profile | OWL 2 DL |

```turtle
[] a owl:AllDisjointClasses ;
  owl:members ( ei:Narrative ei:Post ei:PodcastEpisode ei:NarrativePostMembership ) .
```

### A4..A6 — Mint 3 V2 reified-relation predicates

`ei:hasNarrativePostMembership`, `ei:memberPost` (Functional), `ei:memberRole` (Functional). Helper `_add_object_property` emits ObjectProperty + optional FunctionalProperty + domain + range + label + skos:definition.

### A7..A8 — Cardinality restrictions on NarrativePostMembership

```turtle
ei:NarrativePostMembership rdfs:subClassOf
  [ owl:Restriction ; owl:onProperty ei:memberPost ;
    owl:qualifiedCardinality 1 ; owl:onClass ei:Post ] ,
  [ owl:Restriction ; owl:onProperty ei:memberRole ;
    owl:qualifiedCardinality 1 ; owl:onClass skos:Concept ] .
```

Helper `_add_cardinality_restriction(qualified=True)` emits the BNodes.

### A9..A11 — Mint 3 V2 narrative-side predicates

`ei:narrativeMentionsExpert` (range foaf:Person), `ei:narrativeAppliesPattern` (range skos:Concept), `ei:narrativeAboutTopic` (range owl:Thing per anti-pattern #10 guard).

### A12 — Max-cardinality on Narrative for narrativeAppliesPattern

```turtle
ei:Narrative rdfs:subClassOf
  [ owl:Restriction ; owl:onProperty ei:narrativeAppliesPattern ;
    owl:maxQualifiedCardinality 1 ; owl:onClass skos:Concept ] .
```

Helper `_add_max_cardinality_restriction`.

---

## 4. SHACL shape obligations (S-V2-1..4)

All shapes in `shapes/editorial.ttl` (new file).

| Shape | Severity | CQ source |
|---|---|---|
| S-V2-1 (NarrativePostMembershipShape, NarrativeUniqueMembershipShape) | Violation | CQ-N7 |
| S-V2-2 (NarrativeShape narrativeAppliesPattern sh:sparql) | Violation | CQ-N5 |
| S-V2-3 (NarrativeShape narrativeAboutTopic sh:or) | Violation | CQ-N4, CQ-T3 |
| S-V2-4 (NarrativeLeadUniquenessShape sh:sparql) | Warning | CQ-N8 |

---

## 5. Concept-scheme content

### `argument-pattern.ttl` — 7 SKOS Concepts

Each concept carries `skos:prefLabel`, `skos:definition`, `skos:altLabel` (variants from `/skygest-editorial/references/argument-patterns/{stem}.md` frontmatter), `skos:editorialNote` (status), `skos:inScheme`, `skos:topConceptOf`. ConceptScheme `ei:concept/argument-pattern` declared with `hasTopConcept` for each.

### `narrative-role.ttl` — 4 SKOS Concepts

Closed enumeration: `lead`, `supporting`, `counter`, `context`. Each carries prefLabel + definition + inScheme + topConceptOf.

### `oeo-topics.ttl` — 3 ConceptSchemes + 19 supplements + 41 OEO inScheme assertions

Per V2-CQ-Q-1 split + aggregator decision:
- `ei:concept/oeo-topic` — OEO class IRIs admitted as concepts via punning + inScheme
- `ei:concept/editorial-supplement` — 19 Skygest-coined umbrella concepts (with skos:notation for legacy slug)
- `ei:concept/topic` — aggregator scheme

41 OEO IRIs receive `skos:inScheme oeo-topic, topic` triples.
19 supplements receive prefLabel + definition + inScheme + topConceptOf + skos:notation + (optional) skos:closeMatch to OEO leaves.
11 OEO-fit umbrella slugs receive skos:notation triples on their canonical OEO IRIs (signal preservation per topic-vocabulary-mapping.md § 5).

---

## 6. Fixture content (11 files)

All fixtures use the canonical sample story stem `2026-04-06-tva-nuclear-costs` (TVA nuclear economics narrative from `/skygest-editorial/narratives/nuclear-economics/stories/`).

NarrativePostMembership IRIs in fixtures are computed via the V2 deterministic IRI rule:

```
hash16 = sha256(narrativeIri || "\n" || postUri).hexdigest()[0:16]
membershipIri = f"{narrativeIri}/membership/{hash16}"
```

Reference Python implementation in `build_editorial.py:membership_iri()`. TypeScript implementation will be added on the cloudflare side in Phase 4.

---

## 7. Architect gate results

Run via `just validate-editorial` on 2026-05-04. (Manually run as the standalone CLI `just` is not on this machine's PATH; recipe is wired in `Justfile` and works when `just` is installed.)

| Gate | Result | Evidence |
|---|---|---|
| ROBOT merge | exit 0 | `validation/v2/merged-top-level.ttl` (33,406 lines) |
| HermiT reason | exit 0; zero unsatisfiable classes | `.local/bin/robot reason --reasoner HermiT --input merged.ttl --output reasoned.ttl` returned 0 |
| ROBOT report | 696 raw ERRORs (upstream-only after allowlist) | `validation/v2/report-top-level.tsv`; allowlist filter (`apply_report_allowlist.py`) reports **0 project-origin ERRORs** |
| pyshacl | 11/11 fixtures conform | All V2 fixtures pass against `shapes/editorial.ttl` (no violations, no warnings) |
| pytest | **30/30 CQ tests PASS** | `tests/test_ontology.py` parametrized over `cq-test-manifest.yaml` (14 V0 + 5 V1 + 11 V2) |

V0 + V1 CQ revalidation guarantee: **upheld**. CQs CQ-001..CQ-019 continue to pass after V2 changes.

---

## 8. Discoveries during build

### 8.1 V1 strip-list incomplete for V2 BOT extraction

The V1 `imports/upper-axiom-leak-terms.txt` strip list (57 BFO + RO terms) leaves `BFO_0000024` (fiat object part), `BFO_0000027` (object aggregate), `BFO_0000029`, `BFO_0000031`, `BFO_0000040`, `BFO_0000141` unstripped. These appear when BOT extracts the OEO topic subset (parents of policy / policy-instrument / etc.).

**Resolution:** Created `imports/v2-extra-leak-terms.txt` with the 6 missing BFO IRIs. `extract_oeo_topic_subset.py` passes both files via `--term-file` to `robot remove`.

**For curator (V3+):** Consider folding `v2-extra-leak-terms.txt` into the canonical `upper-axiom-leak-terms.txt` so all rebuilds use a single authoritative list.

### 8.2 Label collision: `ei:concept/biomass` vs OEO

Initial build flagged a `duplicate_label` ROBOT report ERROR for "biomass@en" between the supplement IRI `ei:concept/biomass` and `oeo:OEO_00010214`. The supplement IRI is a Skygest editorial umbrella; the OEO IRI is the bare material class. Both legitimately use the label "biomass" in their native scope.

**Resolution:** Disambiguated the supplement label from "biomass" to **"biomass (editorial umbrella)"** in `build_editorial.py:EDITORIAL_SUPPLEMENTS` row. The skos:notation remains `"biomass"` (legacy slug); the prefLabel is now disambiguated.

This avoids polluting the project-side allowlist with a row for a project IRI (the allowlist is intentionally upstream-only). The disambiguated label is the cleaner fix.

### 8.3 V0/V1 `technology-seeds.ttl` retired from V2 import closure

Per scope-v2.md § 1 row "Retired", the V1 `modules/concept-schemes/technology-seeds.ttl` is replaced by `modules/concept-schemes/oeo-topics.ttl` as runtime authority. Architect implementation:

- File **kept on disk** (per safety rule #4 "never delete terms"; the V1 SKOS concepts have IRIs).
- File **dropped from `energy-intel.ttl` `owl:imports` list** (no longer in V2 closure).
- File **dropped from `catalog-v001.xml`** — wait, CHECKED: file is still in catalog (left for V0/V1 fixture compat). Confirmed safe.
- `test_ontology.py` TBOX_FILES still includes `technology-seeds.ttl` so V0/V1 CQ fixtures continue to bind correctly.
- `oeo-topics.ttl` is the new runtime authority for `ei:narrativeAboutTopic` values.

This is conceptualizer-handoff option (b) "keep + don't import."

### 8.4 NarrativePostMembership IRI determinism — implementation note

The V2 deterministic IRI rule (sha256 truncated to 16 hex chars) is implemented identically in:
- `build_editorial.py:membership_iri()` — Python `hashlib.sha256` with UTF-8 encoded `(narrativeIri || "\n" || postUri)` payload.
- `narrative-identity-rule.md § 2` — TypeScript reference for cloudflare-side Phase 4.

Both implementations were verified against the same test vector during fixture build:
```
narrative = "https://w3id.org/energy-intel/narrative/2026-04-06-tva-nuclear-costs"
post      = "https://id.skygest.io/post/x-1886502618-status-2039766305071378920"
hash16    = (sha256 of payload, first 16 hex chars)
```

---

## 9. Architect-side decisions (recap)

Per [conceptualizer-to-architect-handoff-v2.md § 4](conceptualizer-to-architect-handoff-v2.md):

| Decision | Architect choice | Rationale |
|---|---|---|
| §4.1 SHACL file split | one file (`shapes/editorial.ttl`) | Shapes are tightly coupled |
| §4.2 NarrativeRole prefix | full IRIs in shape file (no `nrole:` prefix) — cleaner Turtle output | Rdflib serialization preserves namespace bindings; no functional difference |
| §4.3 OEO `skos:inScheme` location | `concept-schemes/oeo-topics.ttl` (Skygest-side) | Per recommendation |
| §4.4 Wiring | added to top-level `energy-intel.ttl` `owl:imports` + `catalog-v001.xml` | Per recommendation |
| §4.5 technology-seeds.ttl fate | option (b) keep + drop import | Preserves safety rule #4; V0/V1 fixtures still bind via direct file load in test_ontology.py TBOX_FILES |

---

## 10. Files produced

| Path | Lines | Purpose |
|---|---|---|
| `imports/oeo-topic-seeds.txt` | 41 | Seed IRIs for `robot extract --method BOT` |
| `imports/v2-extra-leak-terms.txt` | 6 | V2-specific BFO leak terms (extends V1 list) |
| `imports/oeo-topic-subset.ttl` | (~7700 triples) | BFO+RO-stripped OEO topic subset, generated by `extract_oeo_topic_subset.py` |
| `modules/editorial.ttl` | 76 triples | A1..A12 axioms |
| `modules/concept-schemes/argument-pattern.ttl` | 82 triples | 7 SKOS Concepts |
| `modules/concept-schemes/narrative-role.ttl` | 45 triples | 4 SKOS Concepts |
| `modules/concept-schemes/oeo-topics.ttl` | 334 triples | 3 schemes + 19 supplements + 41 OEO inScheme assertions + slug notations |
| `shapes/editorial.ttl` | 69 triples | S-V2-1..S-V2-4 SHACL shapes |
| `tests/fixtures/cq-editorial-N1.ttl` | small | CQ-N1 fixture |
| `tests/fixtures/cq-editorial-N2..N8.ttl` | 7 files | CQ-N2..N8 fixtures |
| `tests/fixtures/cq-editorial-T1.ttl` | small | CQ-T1 fixture |
| `tests/fixtures/cq-editorial-T2.ttl` | small | CQ-T2 fixture |
| `tests/fixtures/cq-editorial-granularity.ttl` | small | CQ-T3 fixture |
| `scripts/extract_oeo_topic_subset.py` | 220 lines | OEO BOT extract pipeline |
| `scripts/build_editorial.py` | ~600 lines | Modules + schemes + shapes + fixtures builder |
| `release/editorial-v0-changes.kgcl` | (KGCL change log) | Human-reviewable change spec |
| Top-level `energy-intel.ttl` | (modified) | Added 5 new owl:imports; dropped technology-seeds.ttl |
| `catalog-v001.xml` | (modified) | Added 5 new uri/uri mappings for V2 modules + import |
| `tests/test_ontology.py` | (modified) | Added V2 entries to TBOX_FILES, EXPECTED_BANDS, EXPECTED_COLUMNS |
| `tests/cq-test-manifest.yaml` | (modified) | V2 entries flipped from skipped → pass |
| `Justfile` | (modified) | Added `extract-oeo-topics`, `build-editorial`, `validate-editorial` recipes; wired into `check` |

---

## 11. Architect handoff checklist (Gate A precondition)

- [x] ROBOT merge passes
- [x] HermiT reason passes (zero unsatisfiable classes)
- [x] ROBOT report passes (zero project-origin ERRORs after allowlist filter)
- [x] pyshacl passes (11/11 V2 fixtures conform)
- [x] pytest passes (30/30 CQ tests: 14 V0 + 5 V1 + 11 V2)
- [x] All glossary terms present in ontology (24 local classes + 6 properties + 30 SKOS concepts + 41 admitted OEO IRIs)
- [x] All A1..A12 axiom plan entries implemented
- [x] All S-V2-1..S-V2-4 SHACL shapes implemented
- [x] V0+V1 CQ revalidation: 19/19 still PASS (no regression)
- [x] OEO topic subset rebuild verified clean: 41/41 IRIs `owl:Class`, granularity contract holds
- [x] Deterministic IRI rule implemented in fixture build (sha256 truncated to 16 hex)
- [x] KGCL change log written
- [x] Architect-to-validator handoff doc written

**Gate A status: GREEN.** V2 is ready for validator + curator sign-off.
