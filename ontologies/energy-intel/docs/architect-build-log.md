# Architect Build Log — `energy-intel`

**Architect session:** 2026-04-22
**Skill:** `ontology-architect`
**Target profile:** OWL 2 DL
**Primary reasoner:** HermiT
**ROBOT:** 1.9.8 (jar `.local/share/robot.jar` via wrapper `.local/bin/robot`)
**Python:** strictly `uv run` (deps in `pyproject.toml`)

Per-step outcomes land here chronologically. Every `robot merge / reason / report`
gate is logged with exit status + key metric.

---

## Step A — OEO namespace patch

**Scope of change.** Corrected the OEO namespace from
`http://openenergy-platform.org/ontology/oeo/` (HTTP + hyphen) to
`https://openenergyplatform.org/ontology/oeo/` (HTTPS + no hyphen) across
the live-use artifacts. Root cause: scout phase pulled the legacy
PURL / mirror form; OEO v2.11.0 mints under the canonical HTTPS form.
Verified in `imports/oeo-seed-verification.md`.

Files patched:

- `ontologies/energy-intel/imports-manifest.yaml` — all three OEO rows
  (source_iri + seed_terms + extraction_command).
- `ontologies/energy-intel/docs/competency-questions.yaml` — prefix
  declaration header.
- `ontologies/energy-intel/docs/reuse-report.md` — A.1, A.2, A.3, A.5
  rows.
- `ontologies/energy-intel/tests/cq-013.sparql`, `cq-014.sparql` —
  already free of concrete OEO IRIs (they query `ei:` wind concept via
  property path); no literal OEO namespace appears. No patch needed.

Files intentionally NOT patched:

- `ontologies/energy-intel/imports/oeo-seed-verification.md` — verification
  report documenting the bug itself; the wrong-namespace occurrences are
  documentary (they describe what scout had wrong).
- `.claude/skills/_shared/worked-examples/microgrid/*.md`,
  `ontologies/energy-news/...` — out of scope for this session.

Verification: `grep -n "openenergy-platform\.org/ontology/oeo"
ontologies/energy-intel/` returns zero hits outside the verification
report.

## Step B — imports-manifest.yaml update

Rewrote three OEO rows:

- **`oeo-technology-2.11.0`** — dual-root BOT extract
  (`OEO_00020267` energy technology + `OEO_00000011` energy converting
  component). Combined target ~90 OEO classes (plus transitive
  upper-ontology ancestors). `extraction_command` pivoted from
  `--input-iri` + fetched stream to `--input oeo-full.owl` + local file
  (prior agent built OEO v2.11.0 `oeo-full.owl` via `robot merge` on the
  OMN source tree; file now lives at
  `ontologies/energy-intel/imports/oeo-full.owl`, gitignored).
- **`oeo-carrier-2.11.0`** — unchanged single-root (`OEO_00020039`
  energy carrier), namespace-patched + `--input-iri` → `--input` flip.
- **`oeo-aggregation-2.11.0`** — **DROPPED**. Replaced by new
  hand-seeded row `ei-aggregation-type-v0`
  (`modules/concept-schemes/aggregation-type.ttl`) mirroring the
  temporal-resolution hand-seed pattern. Rationale: OEO v2.11.0
  asserted subtree of 1 (just the root) — importing gives nothing.

`.gitignore` updated with `ontologies/*/imports/oeo-full.owl` — the
full upstream snapshot is rebuilt on-demand from the pinned v2.11.0
tag, not committed.

## Step C — BOT extracts

Both extracts ran cleanly against the local `oeo-full.owl` (3.8 MB
merged OMN tree). Exit status 0 for both.

| Subset | Input IRI(s) | Output | Classes | Axioms |
|---|---|---|---|---|
| oeo-technology-subset | `OEO_00020267` + `OEO_00000011` | `imports/oeo-technology-subset.ttl` | 319 (incl. BFO/IAO ancestors; ~90 OEO-specific) | 5059 |
| oeo-carrier-subset | `OEO_00020039` | `imports/oeo-carrier-subset.ttl` | 317 (incl. BFO/IAO ancestors) | 5046 |

Both well under the 400-class abort threshold for OEO-specific
classes.

> Note on class counts: BOT traces every axiom-supporting IRI upwards,
> so the raw class count includes BFO 2020 + IAO ancestors. Post-merge
> with the top-level `energy-intel.ttl` this redundancy collapses
> (same BFO / IAO axioms appear in `imports/bfo-2020.ttl` and
> `imports/iao-subset.ttl`).

---

## Step D — SKOS concept schemes (hand-seeded)

Three hand-seeded schemes written via `rdflib` through
`scripts/build_concept_schemes.py` and `scripts/build_technology_seeds.py`.
All three carry explicit `owl:Ontology` headers so `robot merge` sees
them as named modules.

| File | Root | Concepts | Triples |
|---|---|---|---|
| `modules/concept-schemes/temporal-resolution.ttl` | `ei:concept/temporal-resolution` | hourly / daily / monthly / quarterly / annual | 84 |
| `modules/concept-schemes/aggregation-type.ttl` | `ei:concept/aggregation-type` | sum / average / minimum / maximum / count | 84 |
| `modules/concept-schemes/technology-seeds.ttl` | `ei:concept/technology` | wind {onshore, offshore}, solar {solar-pv} | 50 |

Value Partition ODP F.1 encoded via: five concepts per scheme,
pairwise `skos:related` (non-hierarchical association), and
`owl:AllDifferent` for DL-safe mutual distinctness. The
technology-seeds scheme also carries `skos:broader`/`skos:narrower`
edges so CQ-013/CQ-014 have a non-trivial property path to traverse.

---

## Step E — Module authoring

All four modules + the top-level ontology built via
`scripts/build_modules.py` using `rdflib` (raw triple-level
authoring). Every axiom implements a line from `docs/axiom-plan.md`;
no new axioms invented at implementation time. Internal imports
resolved at `robot merge` time via `catalog-v001.xml`.

| Module | File | Triples | Classes minted | Properties minted |
|---|---|---|---|---|
| agent | `modules/agent.ttl` | 41 | 4 (Expert, Organization, PublisherRole, DataProviderRole) | 0 |
| media | `modules/media.ttl` | 148 | 12 (Post, Conversation, SocialThread, PodcastEpisode, PodcastSegment, MediaAttachment, Chart, Screenshot, GenericImageAttachment, Excerpt, EvidenceSource, + punned `owl:NamedIndividual`) | 8 OP + 1 DP |
| measurement | `modules/measurement.ttl` | 176 | 5 (CMC, Observation, Variable, Series, ClaimTemporalWindow) | 12 OP + 6 DP |
| data | `modules/data.ttl` | 15 | 0 (DCAT extension only) | 1 OP (`ei:hasSeries` + inverse decl) |
| top-level | `energy-intel.ttl` | 22 | `owl:Ontology` with 14 `owl:imports` | — |

Notable axioms (per `axiom-plan.md`):

- `ei:Organization SubClassOf (foaf:Organization ⊓ bfo:ObjectAggregate)`
  — intersection expressed as `owl:intersectionOf` blank node.
- `ei:PublisherRole SubClassOf bfo:Role ⊓ (BFO_0000052 some ei:Organization)`
  — BFO role pattern per ODP F.2.
- `ei:Post SubClassOf (ei:authoredBy exactly 1 ei:Expert)` — qualified
  cardinality forces OWL 2 DL.
- `ei:CanonicalMeasurementClaim SubClassOf ((inverse ei:evidences) min 1 ei:EvidenceSource)`
  — CQ-009 invariant; inverse-property expression (DL-only).
- `ei:PodcastSegment SubClassOf (ei:partOfEpisode exactly 1 ei:PodcastEpisode)`
  — `ei:partOfEpisode rdfs:subPropertyOf bfo:BFO_0000050` inherits
  transitivity per ODP F.5.
- `ei:Chart / Screenshot / GenericImageAttachment / Excerpt` pairwise
  disjoint; `ei:Post / MediaAttachment / PodcastSegment` pairwise
  disjoint (`owl:AllDisjointClasses`).
- `ei:ClaimTemporalWindow SubClassOf bfo:TemporalRegion` (BFO_0000008)
  — NOT an ICE (LOCKED per `bfo-alignment.md`).
- Datatype union `xsd:decimal ∪ xsd:string` on `ei:assertedValue` via
  `rdfs:Datatype` + `owl:unionOf` blank-node construction.

---

## Step F — Quality gates per module

Ran via `scripts/run_gates.py`, which invokes `robot merge` (with
`--catalog catalog-v001.xml`), `robot reason --reasoner hermit`, and
`robot report` for each module plus the top-level. All logs archived
to `validation/`.

| Module | merge exit | HermiT reason exit | unsat classes | inconsistency | report ERRORs | report WARNs | report INFOs |
|---|---|---|---|---|---|---|---|
| agent | 0 | 0 | 0 | no | 4 (all `duplicate_label` on FOAF upstream — `foaf:givenName/givenname`, `foaf:account/holdsAccount`) | 152 | 25 |
| media | 0 | 0 | 0 | no | 6 (FOAF duplicates + 2 additional IAO upstream) | 195 | 60 |
| measurement | 0 | 0 | 0 | no | 325 (DCAT multilingual labels flagged duplicate; PROV/FOAF `Person/Organization` label collisions; upstream `missing_label` on DCAT/PROV utility properties) | 414 | 85 |
| data | 0 | 0 | 0 | no | 325 (same as measurement — transitive via import) | 415 | 85 |
| top-level | 0 | 0 | 0 | no | 329 (+4 upstream edge cases) | 415 | 85 |

**Verdict: reasoner-clean on every module.** Zero unsatisfiable
classes; zero inconsistency detected by HermiT on any module. All
ERROR-level `robot report` violations are **upstream artifacts** of
DCAT, PROV, FOAF, SKOS, and IAO (duplicate labels across languages,
FOAF's historical `givenName`/`givenname` pair, PROV/FOAF
`Person`/`Organization` label collision). Zero ERROR originates from
`ei:` or `ei:concept/*` terms — verified by grep on the report TSVs.

Artifacts for validator ingestion (under `validation/`):
- `merged-{agent,media,measurement,data,top-level}.ttl`
- `reasoned-{agent,media,measurement,data,top-level}.ttl`
- `report-{agent,media,measurement,data,top-level}.tsv`
- `merge-*.log`, `reason-*.log`, `report-*.log`

---

## Step G — SHACL shapes

Built via `scripts/build_shapes.py` → `shapes/energy-intel-shapes.ttl`
(45 triples). Four shapes per conceptualizer handoff bullet 6:

- **S-1 DidSchemeOnAuthoredBy** — `sh:targetClass ei:Post`,
  `sh:path ei:authoredBy`, `sh:nodeKind sh:IRI`,
  `sh:pattern "^did:(plc|web):[A-Za-z0-9._:%-]+$"`.
- **S-2 JsonParseableRawDims** — `sh:sparql` constraint on CMC
  checking that `ei:rawDims` value starts with `{` or `[` (JSON
  heuristic; runtime validators can do full `json.loads` round-trip).
- **S-3 IntervalOrdering** — `sh:sparql` on `ei:ClaimTemporalWindow`
  asserting `?end < ?start` returns no rows.
- **CMCEvidenceSource (CQ-009 companion)** — `sh:targetClass
  ei:CanonicalMeasurementClaim`, `sh:path [sh:inversePath ei:evidences]`,
  `sh:minCount 1 ; sh:class ei:EvidenceSource`. Defense in depth
  against the OWL invariant for closed-ABox validation.

`pyshacl --shacl shapes/energy-intel-shapes.ttl --data shapes/energy-intel-shapes.ttl` parses 4 NodeShapes, finds no focus nodes in the
self-data graph, and exits conformant. Shapes compile cleanly against
pyshacl's parser.

---

## Step H — CQ fixtures

Built via `scripts/build_fixtures.py`. Each fixture is a minimal
ABox authored through `rdflib` using plausible
`https://id.skygest.io/{kind}/{ulid}` IRIs (per Linear D3). The
script immediately re-executes every `tests/cq-NNN.sparql` against
its matching fixture and classifies the row shape against the
manifest's `expected_results_contract`.

| CQ | expected | rows returned | status |
|---|---|---|---|
| CQ-001 | exactly_1 | 1 | pass |
| CQ-002 | exactly_1 | 1 | pass |
| CQ-003 | exactly_1 | 1 | pass |
| CQ-004 | exactly_1 | 1 | pass |
| CQ-005 | exactly_1 | 1 | pass |
| CQ-006 | eq_2 (two CMCs on one Variable) | 2 | pass |
| CQ-007 | eq_2 (two distinct Experts) | 2 | pass |
| CQ-008 | eq_2 (full payload, one fully-annotated + one bare) | 2 | pass |
| CQ-009 | exactly_0 (invariant holds) | 0 | pass |
| CQ-010 | exactly_1 (all five references resolved) | 1 | pass |
| CQ-011 | eq_2 (multi-speaker segment) | 2 | pass |
| CQ-012 | exactly_1 | 1 | pass |
| CQ-013 | ge_1 (transitive path through technology-seeds) | 1 | pass |
| CQ-014 | ge_1 (two-hop Post → CMC → concept walk) | 1 | pass |

**14/14 fixture queries pass their acceptance contracts.**

`tests/cq-test-manifest.yaml` updated: every row flipped from
`fixture_run_status: skipped` to `pass`; preflight summary now reports
14 built / 14 passing / 0 skipped.

---

## Step I — Profile validation note (upstream FOAF / DCAT / DC Terms)

`robot validate-profile --profile DL` on the merged top-level reports
profile violations, but **every single violation originates in the
imported upstream vocabularies** — FOAF, DCAT 3, DC Terms. The three
families are:

- `Cannot pun between properties` on FOAF `msnChatID`, `icqChatID`,
  `jabberID`, `yahooChatID`, `page`, `mbox_sha1sum` and on DCAT
  `resource`, `distribution`, `inSeries`, `hasCurrentVersion`,
  `compressFormat`, and on DC Terms `created`, `title`, `issued`,
  `modified`, `available`, `dateSubmitted`, `dateAccepted`,
  `valid`, `bibliographicCitation` (these vocabularies
  declare the same IRI as both annotation and object/data property —
  canonical OWL 2 DL "punning across properties" violation).
- `Use of reserved vocabulary for class IRI: rdfs:Resource, rdf:List`
  (upstream DCAT declaring RDFS-reserved IRIs as classes).
- `Use of undeclared object property: <http://xmlns.com/foaf/0.1/nick>`
  — bug in FOAF 0.99.

Every reproducible with just `robot validate-profile --profile DL
--input modules/agent.ttl` (agent module imports only BFO + FOAF —
FOAF alone triggers the violations). **None of these violations
originate from `ei:` terms.** HermiT continues to classify and
reason without error because the violations occur on annotation /
utility properties, not on class-level axioms relevant to
subsumption.

For release-gate purposes, the validator has two options:

1. **Strict DL (recommended for downstream consumers):** ship a
   "profile-check" variant that drops FOAF / DC-Terms annotation-property
   punning (e.g., treat DC Terms `created` strictly as AnnotationProperty)
   via a ROBOT `reduce`/`materialize` recipe before `validate-profile`.
2. **Pragmatic DL (what we do for V0 reasoning):** accept upstream
   profile noise; rely on HermiT's graceful-degradation reasoning.
   Document the accepted upstream violations in the validator's
   allow-list.

**Validator decision point**: tag as
`construct_mismatch-upstream-only` and treat as accepted debt. No
loopback back to architect.

## Loopback status

No triggers raised against architect scope. All three architect-owned
gates (reasoner soundness, report severity on project terms, fixture
acceptance) cleared. One upstream profile-debt item (Step I)
forwarded to validator as a documented watch-item, not a blocking
loopback.

## Deliverables summary

See `docs/architect-to-validator-handoff.md` for the final file
manifest and validator entry points.
