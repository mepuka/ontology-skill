# V2 Diff vs V1 Baseline — `energy-intel` (v0.3.0)

**Predecessor:** v0.2.0 (commit `1d8f9da`, 2026-04-27)
**Current:** v0.3.0 (release-candidate; commit pending)
**V1 versionIRI:** `https://w3id.org/energy-intel/v1/2026-04-27`
**V2 versionIRI:** `https://w3id.org/energy-intel/v2/2026-05-04`

**ROBOT 1.9.8** `diff` between V1 and V2 merged top-level closures
(`validation/merged-top-level.ttl` (V1, 27,113 lines) vs
`validation/v2/merged-top-level.ttl` (V2, 33,343 lines)).

Raw diff cached at `/tmp/curator-v2-rerun/v2-diff-raw.md` (12,748 lines;
mostly upstream LatexString whitespace re-serialization noise from QUDT
2.1 across runs). This file is the curator-categorized digest.

---

## TL;DR

**Additive structural extension.** V2 adds **2 net-new project classes
(`ei:Narrative`, `ei:NarrativePostMembership`)**, **6 net-new project
object properties** (the editorial graph), **5 net-new SKOS
ConceptSchemes**, **30 net-new project SKOS Concepts**, **4 net-new
SHACL NodeShapes** (S-V2-1..4 in `shapes/editorial.ttl`), and one
**net-new owl:imports row** (`oeo-topic-subset`).

**5 SKOS Concepts dropped from import closure** — the V1 hand-seeded
technology terms (`solar`, `solar-pv`, `wind`, `onshore-wind`,
`offshore-wind`) are no longer imported because `oeo-topics.ttl`
replaces `technology-seeds.ttl` as runtime authority. The
`technology-seeds.ttl` file is **preserved on disk** per safety rule #4
(never delete terms); the concepts remain dereferenceable. Tracked as
**V2-CUR-4** for V0.4.0 deprecation cycle.

**1 SKOS ConceptScheme dropped from import closure**:
`https://w3id.org/energy-intel/concept/technology` (the parent scheme
of the 5 concepts above). Same disposition.

**No project terms deleted, deprecated, or semantically narrowed.** The
release is **strictly additive at the project namespace** for ABox
consumers.

---

## 1. Project namespace delta (`ei:` axioms)

Computed by direct rdflib inspection of the V1 and V2 merged TTL
closures (`tools/curator-summary.py` — see appendix).

| Bucket | V1 | V2 | Net |
|---|---:|---:|---:|
| `ei:` `owl:Class` | 21 | 23 | **+2** |
| `ei:` `owl:ObjectProperty` + `owl:DatatypeProperty` | 28 | 34 | **+6** |
| `ei:` `skos:ConceptScheme` | 3 | 7 (in closure)¹ | **+5, -1** |
| `ei:` `skos:Concept` | 15 | 40 | **+30, -5** |
| `ei:` `sh:NodeShape` (in `shapes/editorial.ttl`)² | 0 | 4 | **+4** |
| OEO punned `skos:Concept` (in closure) | 0 | 41³ | **+41** |

¹ V1 had 3 schemes in closure (`temporal-resolution`, `aggregation-type`,
implicit `technology` scheme via `technology-seeds.ttl`). V2 closure has
7 schemes including the V2 net-new (`argument-pattern`, `narrative-role`,
`oeo-topic`, `editorial-supplement`, `topic` aggregator). The
`technology` scheme drops out of closure with `technology-seeds.ttl`
removal; the file is preserved on disk.

² `shapes/editorial.ttl` is a separate SHACL shapes graph (not in TBox
import closure); the count is from direct file inspection.

³ Counted as OEO classes that received SKOS punning (`skos:inScheme`)
via `oeo-topics.ttl`. Per V1-CUR-3 the TBox-stage punning watch is closed
(HermiT exit 0 on V2 closure).

---

## 2. Net-new project axioms (V2 additions)

### 2.1 Classes (2 new)

| IRI | Parent | Source axiom |
|---|---|---|
| `ei:Narrative` | `iao:0000310` (Document) | A1 (axiom-plan-v2.md) |
| `ei:NarrativePostMembership` | `iao:0000310` (Document) | A2 |

Plus `AllDisjointClasses(Narrative, Post, PodcastEpisode, NarrativePostMembership)`
(A3) — pairwise project-disjointness sealed.

### 2.2 Object properties (6 new)

| IRI | Domain | Range | Char | Axiom |
|---|---|---|---|---|
| `ei:hasNarrativePostMembership` | `ei:Narrative` | `ei:NarrativePostMembership` | — | A4 |
| `ei:memberPost` | `ei:NarrativePostMembership` | `ei:Post` | Functional | A5 |
| `ei:memberRole` | `ei:NarrativePostMembership` | `skos:Concept` | Functional | A6 |
| `ei:narrativeMentionsExpert` | `ei:Narrative` | `foaf:Person` | — | A9 |
| `ei:narrativeAppliesPattern` | `ei:Narrative` | `skos:Concept` | — | A10 |
| `ei:narrativeAboutTopic` | `ei:Narrative` | `owl:Thing`* | — | A11 |

*Granularity gate enforced via SHACL S-V2-3 (`sh:or owl:Class /
skos:Concept`); bare NamedIndividual rejected.

Cardinality restrictions:
- `NarrativePostMembership SubClassOf memberPost qualifiedCardinality 1 Post` (A7)
- `NarrativePostMembership SubClassOf memberRole qualifiedCardinality 1 skos:Concept` (A8)
- `Narrative SubClassOf narrativeAppliesPattern maxQualifiedCardinality 1 skos:Concept` (A12)

### 2.3 SHACL shapes (4 new — in `shapes/editorial.ttl`)

| Shape IRI | Severity | Contract |
|---|---|---|
| `ei:NarrativePostMembershipShape` (S-V2-1 + closed-shape SPARQL) | Violation | `memberPost` minCount/maxCount 1 `ei:Post`; `memberRole` minCount/maxCount 1 in `nrole:{lead,supporting,counter,context}`; plus `NarrativeUniqueMembershipShape` (sh:sparql) at-most-one-membership-per-(N,P)-pair |
| `ei:NarrativeShape` (S-V2-2 sh:sparql) | Violation | `narrativeAppliesPattern` value MUST be in `ei:concept/argument-pattern` scheme |
| `ei:NarrativeShape` (S-V2-3 sh:or) | Violation | `narrativeAboutTopic` value MUST be `owl:Class` OR `skos:Concept` (granularity contract) |
| `ei:NarrativeLeadUniquenessShape` (S-V2-4 sh:sparql) | Warning¹ | At-most-one-lead-membership-per-Narrative |

¹ Severity rendering quirk in pyshacl (V2-CUR-1, non-blocking) — shape
fires correctly but rendered severity is `sh:Violation` despite the
SPARQLConstraint declaring `sh:Warning`. Resolved by other SHACL
processors that read `sh:sourceConstraint -> sh:severity`.

### 2.4 SKOS ConceptSchemes (5 new in import closure)

| IRI | Concepts | Source |
|---|---:|---|
| `ei:concept/argument-pattern` | 7 | `modules/concept-schemes/argument-pattern.ttl` |
| `ei:concept/narrative-role` | 4 | `modules/concept-schemes/narrative-role.ttl` |
| `ei:concept/oeo-topic` | 41 (OEO IRIs via punning) | `modules/concept-schemes/oeo-topics.ttl` |
| `ei:concept/editorial-supplement` | 19 (project supplements) | `modules/concept-schemes/oeo-topics.ttl` |
| `ei:concept/topic` (aggregator) | 60 (41 OEO + 19 supplements) | `modules/concept-schemes/oeo-topics.ttl` |

### 2.5 Imports (1 net-new in owl:imports closure)

| Import IRI | File | Triples |
|---|---|---:|
| `https://w3id.org/energy-intel/imports/oeo-topic-subset` | `imports/oeo-topic-subset.ttl` | 7,729 |

Source: `imports/oeo-full.owl` (OEO 2.11.0). Method:
`robot extract --method BOT` against 41 seed IRIs in
`imports/oeo-topic-seeds.txt`, then `robot remove` with combined
strip-list (`imports/upper-axiom-leak-terms.txt` 57 terms +
`imports/v2-extra-leak-terms.txt` 6 terms; the latter consolidates per
V2-CUR-2). Granularity verifier `extract_oeo_topic_subset.py:verify_*`
confirms all 41 seeds remain `owl:Class` post-strip and zero BFO
references survive.

### 2.6 Concept Schemes for V2 added at top-level `owl:imports`

`energy-intel.ttl` `owl:imports` rows (per top-level TTL inspection):
- `https://w3id.org/energy-intel/modules/editorial`
- `https://w3id.org/energy-intel/modules/concept-schemes/argument-pattern`
- `https://w3id.org/energy-intel/modules/concept-schemes/narrative-role`
- `https://w3id.org/energy-intel/modules/concept-schemes/oeo-topics`
- `https://w3id.org/energy-intel/imports/oeo-topic-subset`

---

## 3. Net-removed from import closure (file preserved on disk)

Removed by **dropping `technology-seeds.ttl` from
`owl:imports`** in `energy-intel.ttl` (per architect-build-log § 8.3):

| IRI | Type | V2 Replacement |
|---|---|---|
| `ei:concept/technology` | `skos:ConceptScheme` | `ei:concept/oeo-topic` (oeo-topics.ttl scheme) |
| `ei:concept/solar` | `skos:Concept` | `oeo:OEO_00000384` (OEO solar) via `oeo-topics.ttl` |
| `ei:concept/solar-pv` | `skos:Concept` | OEO solar-PV equivalent (in `oeo-topic-subset` BOT closure) |
| `ei:concept/wind` | `skos:Concept` | OEO wind equivalent |
| `ei:concept/onshore-wind` | `skos:Concept` | OEO onshore-wind equivalent |
| `ei:concept/offshore-wind` | `skos:Concept` | OEO offshore-wind equivalent |

**Disposition:** file `modules/concept-schemes/technology-seeds.ttl`
preserved on disk (safety rule #4). V0/V1 fixtures (`cq-013`, `cq-015`)
still bind via direct `tests/test_ontology.py:TBOX_FILES` load. Concepts
**not yet deprecated**; deprecation deferred to V0.4.0 per **V2-CUR-4**
(curator action: add `owl:deprecated true` + `dcterms:isReplacedBy
oeo:OEO_xxx` per concept before any deletion).

---

## 4. Annotation deltas (top-level)

| Field | V1 | V2 |
|---|---|---|
| `owl:versionIRI` | `https://w3id.org/energy-intel/v1/2026-04-27` | `https://w3id.org/energy-intel/v2/2026-05-04` |
| `owl:versionInfo` | `"v1 (2026-04-27)"` | `"v2 (2026-05-04)"` |
| `dcterms:modified` | `"2026-04-27"^^xsd:date` | `"2026-05-04"^^xsd:date` |
| `dcterms:description` | V1 string (4 modules + V1 imports) | V2 string (5 modules incl. editorial; 3 new SKOS schemes; OEO topic subset; SHACL editorial shapes; technology-seeds retired note) |

Top-level `owl:imports` row count: V1 = 12; V2 = 19 (+5 V2 module IRIs;
+1 OEO topic subset; +1 net change for argument-pattern).

---

## 5. Reasoner / closure verdict

| Gate | V1 (validator-rerun) | V2 (curator re-run, this audit) |
|---|---|---|
| HermiT exit code | 0 | 0 |
| Unsatisfiable classes | 0 | 0 |
| Inconsistent | false | false |
| Reasoned closure size | 2.36 MB | ~2.69 MB |
| Project-origin ROBOT report ERRORs | 0 (after allowlist) | 0 (after allowlist; no V2 additions) |
| pytest CQ suite | 19/19 | 30/30 (+5 V1 + 11 V2 = 30) |

V2 reproducibility: graph-isomorphism check on regenerated
`oeo-topic-subset.ttl`, `editorial.ttl`, `argument-pattern.ttl`,
`narrative-role.ttl`, `oeo-topics.ttl`, `shapes/editorial.ttl` against
in-tree files: **all 6 isomorphic** (curator-log-v2.md § 1.1).

---

## 6. Diff noise / known cosmetic deltas

The raw `robot diff` output contains ~12,500 lines of which the vast
majority are **upstream-only re-serialization deltas** that occur
naturally when the V1 baseline merged TTL is re-emitted at V2-build
time:

- QUDT `LatexString` whitespace normalization (trailing space and
  blank-line variations between QUDT 2.1 dumps).
- Anonymous blank-node renumbering (`_:genid21474836xx` reshuffles
  between V1 and V2 ROBOT runs; not semantic).
- OEO upstream `skos:altLabel` ordering variance.

These are **not** project-axiom changes and have no consumer impact.
The categorization in §§1-5 above is the canonical project-axiom
delta.

---

## 7. Cross-reference

- Architect axiom plan: [`docs/axiom-plan-v2.md`](../docs/axiom-plan-v2.md)
  (A1..A12 + S-V2-1..4)
- Architect build log: [`docs/architect-build-log-v2.md`](../docs/architect-build-log-v2.md) §8 (changes)
- Validator report: [`docs/validator-report-v2.md`](../docs/validator-report-v2.md)
- Validator handoff: [`docs/validator-to-curator-handoff-v2.md`](../docs/validator-to-curator-handoff-v2.md)
- Release audit: [`release-audit-v2.yaml`](release-audit-v2.yaml)
- Release notes: [`release-notes-v0.3.0.md`](release-notes-v0.3.0.md)
- KGCL change-record: [`editorial-v0-changes.kgcl`](editorial-v0-changes.kgcl)

---

## 8. Migration impact (consumers)

**Cloudflare KG (skygest-cloudflare):**
- Repoint `ontologyRoot` from V1 `https://w3id.org/energy-intel/v1/2026-04-27`
  to V2 `https://w3id.org/energy-intel/v2/2026-05-04` after PURL
  refresh.
- Re-run codegen. The V2 additions are strictly additive at TBox; V1
  triples (`?cmc ei:authoredBy ?p`, `?cmc ei:canonicalUnit ?u`, etc.)
  continue to type-check.
- New editorial pipeline: `?n a ei:Narrative ; ei:hasNarrativePostMembership ?m
  ; ei:narrativeAboutTopic ?t .` is now first-class.

**Direct ontology consumers** (OWL-API, OLS, BioPortal): no breaking
changes. Range widenings absent. No `ei:` term removed; 5 ei:concept/*
entities preserved on disk via `technology-seeds.ttl` (still
dereferenceable).

---

End of V2 diff document.
