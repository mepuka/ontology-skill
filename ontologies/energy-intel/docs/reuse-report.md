# Reuse Report — `energy-intel` Ontology

**Scout run:** 2026-04-22
**Scout:** ontology-scout (automated)
**Inputs frozen at:** `f6d025d` (`requirements-approval.yaml`, 14 CQs, 55-row pre-glossary)
**Downstream:** `ontology-conceptualizer`, `ontology-architect`

## Source freshness header

Per scout Step 0. All registry probes executed from this session; OLS4 v2 classes
endpoint returned for every IAO/BFO term probed, ols4 /api/ontologies/oeo
route was 404 (current OLS4 does not expose the legacy v1 terms endpoint for
OEO under the same path; v2 returned empty `elements` on direct-IRI
lookup for OEO). Compensated via live OEO ontology file + LOD archivo mirror.

| Source | Probe | Access timestamp | Status | Version / notes |
|---|---|---|---|---|
| OLS4 v2 classes (IAO) | `GET /api/v2/ontologies/iao/classes?iri=…` | 2026-04-22 | **up** | IAO 2026-03-30; labels/defs returned for IAO_0000030, _0000101, _0000310, _0000027 |
| OLS4 v2 classes (BFO) | `GET /api/v2/ontologies/bfo/classes?iri=…` | 2026-04-22 | **up** | BFO labels/defs returned for BFO_0000023, _0000027 |
| OLS4 v2 classes (OEO) | direct-IRI lookup | 2026-04-22 | **degraded** | Empty `elements` on the v2 route; fell back to (a) OEO GitHub CHANGELOG for release, (b) DBpedia Archivo mirror for class hierarchy |
| OEO release channel (GitHub `OpenEnergyPlatform/ontology`) | WebFetch CHANGELOG | 2026-04-22 | **up** | Latest release **v2.11.0 (2026-03-04)**; v2.10.0 (2025-12-10); v2.9.0 (2025-10-01) |
| OEO term reference (DBpedia Archivo 2023-02-01 snapshot of `oeo-full`) | WebFetch generated doc | 2026-04-22 | **cached** | Snapshot is ~14 months stale but gives trustworthy IRIs + labels for core classes; architect MUST re-verify against v2.11.0 before `robot extract` |
| W3ID registration docs (`perma-id/w3id.org`) | WebFetch README | 2026-04-22 | **up** | Manual PR workflow; no SLA published |
| W3C DCAT-3 spec | WebFetch | 2026-04-22 | **up** | DCAT 3 Rec does NOT define `dcat:Agent`; recommends `foaf:Agent` as value |
| DCAT-AP 3.0.0 (SEMICeu) | WebFetch | 2026-04-22 | **up** | No `owl:equivalentClass` declarations; references `foaf:Agent`; uses `prov:qualifiedAttribution` |
| QUDT schema | WebFetch | 2026-04-22 | **up** | v3.2.1; modular ontology (imports `coordinateSystems`, `datatype`, etc.) |
| ODP portal (`ontologydesignpatterns.org`) | WebFetch Submissions pages | 2026-04-22 | **degraded** | `Submissions:Role`, `Submissions:Participation`, `Submissions:Information_Realization` all timed out or 404'd from the automation. Fell back to catalog references in `_shared/pattern-catalog.md` + published BFO/IAO equivalents |
| BioPortal | not queried | — | **skipped** | No domain-specific energy ontology on BioPortal would outrank OEO for this scope; skip documented |
| LOV | not queried | — | **skipped** | Baseline DCAT/FOAF/PROV/SKOS choices already locked in scope.md § Reused external ontologies; no LOV-level discovery gap remains |

**Overall verdict:** the scout-phase evidence is sufficient to recommend import strategies, IAO/BFO seed IRIs, DCAT/QUDT alignment, and ODPs. The OEO
MIREOT seed list is *provisional pending architect verification against the v2.11.0 file* — one of the IRIs used in scope.md (`OEO_00000030`) is wrong (it labels "oil power unit", not "energy technology"). Fix is in § A below.

---

## Always-reuse baseline

The following are already committed in `scope.md § Reused external ontologies`; scout confirms them:

| Ontology | IRI | Version | License | Verdict |
|---|---|---|---|---|
| Dublin Core Terms | `http://purl.org/dc/terms/` | 2020-01-20 (stable) | public domain / no-restriction | Confirmed. Use as-is. |
| SKOS | `http://www.w3.org/2004/02/skos/core` | W3C REC 2009-08-18 (stable) | W3C Document Licence | Confirmed. |
| PROV-O | `http://www.w3.org/ns/prov-o` | W3C REC 2013-04-30 (stable) | W3C Document Licence | Confirmed. |
| FOAF | `http://xmlns.com/foaf/0.1/` | 0.99 (stable) | CC-BY 1.0 | Confirmed. CC-BY is compatible with any downstream publication license. |
| schema.org | n/a (not adopted in V0) | — | CC-BY-SA 3.0 (terms), CC0 (vocab) | Reviewed; not imported. DCAT + FOAF cover the agent/document slots; re-evaluate if/when schema.org-JSON-LD export is needed (scope.md § Open q #5). |

---

## A. OEO MIREOT seed IRIs (scope.md Open question #1)

**Authoritative source probed:** OEO v2.11.0 (released 2026-03-04), CHANGELOG confirmed from GitHub.
**Caveat — critical:** the scope.md § Open questions line "Candidate: `OEO_00000030`" is **wrong**. `OEO_00000030` is labelled **"oil power unit"** (DBpedia Archivo mirror 2023-02-01 snapshot, confirmed against OEO class-IRI convention). The architect must NOT use `OEO_00000030` as the energy-technology root. Revised candidate list below; architect re-verifies against the v2.11.0 file via `robot query` before extraction.

Recommended seed IRIs (provisional; verify with `robot` before extraction):

| Subtree | Candidate IRI | Label (as recorded) | Status | Action |
|---|---|---|---|---|
| A.1 Energy technology (transformation) root | `http://openenergy-platform.org/ontology/oeo/OEO_00000011` | "energy converting component" | **candidate, unverified** | Architect: `robot query` on v2.11.0 for classes whose rdfs:label contains "energy transformation" or "energy converting" to nail down the true root. Alternative candidate: `OEO_00010385` (`energy transformation function`). |
| A.2 Energy carrier root | `http://openenergy-platform.org/ontology/oeo/OEO_00020039` | "energy carrier" | **candidate** | Parent class is `OEO_00000151` "energy carrier disposition". Architect decides whether to extract the noun class (`_00020039`) or also the disposition (`_00000151`). Recommendation: noun class only; dispositions only matter after ABox lands. |
| A.3 Aggregation type root | `http://openenergy-platform.org/ontology/oeo/OEO_00140068` | "aggregation type" | **candidate** | Likely maps to point / end-of-period / sum / average / settlement descendants but sub-count not yet verified. Size probe via `robot query`. |
| A.4 Temporal-resolution root | *none found in OEO* | — | **gap** | OEO v2.9–v2.11 has `OEO_00020121 "resolution"` (generic) and `OEO_00020099 "meteorological year"` (a concrete duration), but **no dedicated temporal-resolution taxonomy**. Recommendation: hand-seed a small `skos:Concept` scheme (`ei:TemporalResolution` with hourly/daily/monthly/quarterly/annual `skos:Concept` children) in V0; revisit OEO upstream if/when they add one. This is a mini-ConcreteCase of the `value-partition` ODP; see § F.1. |
| A.5 Quantity-kind root | `http://openenergy-platform.org/ontology/oeo/OEO_00000350` | "quantity value" | **candidate** | Note: OEO `_00000350` is "quantity *value*", semantically closer to an instance than a QUDT-style `qudt:QuantityKind`. **Recommendation: do not MIREOT this subtree; use `qudt:QuantityKind` directly.** See § D. |

**Transitive subtree size:** not countable from the mirror snapshot. Architect must run `robot query --format csv --query tests/scout/subtree-count.rq oeo.owl` before cutting the module. Rough upper bounds from OEO release notes (v2.11.0 adds infrastructure classes — power lines, gas turbines, voltage classes, battery chemistries — on top of v2.9/v2.10 additions):

| Subtree | Rough size estimate | Extraction method rationale |
|---|---|---|
| Energy technology (A.1) | 150–400 classes | `BOT` from a single root pulls descendants + ancestors; keep root tight (OEO_00000011 or `energy transformation`) to stay well under the 400-class upper bound. |
| Energy carrier (A.2) | 20–60 classes | `BOT` keeps disposition + noun + concrete carriers. Small. |
| Aggregation type (A.3) | 5–20 classes | `BOT` trivial. |
| Temporal resolution (A.4) | **0 from OEO** | Hand-seed in `ei:` namespace; no MIREOT. |
| Quantity-kind (A.5) | avoid OEO | Use QUDT (see § D). |

**License:** OEO is released under **CC-BY 4.0** (confirmed on the GitHub repo). Compatible with any downstream publication.

---

## B. BFO + IAO alignment (confirm scope.md § Decisions resolved leans)

OLS4 v2 IAO terms probed 2026-04-22; BFO 2020 terms probed directly.

### B.1 Confirmed IRIs

| Scope.md decision | IRI | Verified label | Verified definition (OLS4) | Verdict |
|---|---|---|---|---|
| `iao:InformationContentEntity` as parent of CMC, Observation, Variable, Series, Conversation, PodcastEpisode, PodcastSegment | `http://purl.obolibrary.org/obo/IAO_0000030` | "information content entity" | "A generically dependent continuant that is about some thing." | **Confirmed.** |
| `iao:Document` as parent of Post, Chart, Screenshot, Excerpt, Image | `http://purl.obolibrary.org/obo/IAO_0000310` | "document" | "A collection of information content entities intended to be understood together as a whole." Example: journal article, patent application, laboratory notebook, book. | **Partially correct — see B.2 flag for Chart/Screenshot.** |
| `iao:Image` (scope mentions as narrower candidate for Chart) | `http://purl.obolibrary.org/obo/IAO_0000101` | "image" | "An affine projection to a two dimensional surface, of measurements of some quality of an entity or entities repeated at regular intervals across a spatial range, where the measurements are represented as color and luminosity on the projected on surface." | **Confirmed.** |
| `iao:DataItem` (scope mentions as narrower candidate for Chart) | `http://purl.obolibrary.org/obo/IAO_0000027` | "data entity" (alt labels: "data item", "data") | "An information content entity that is intended to be one or more truthful statement(s) about something…" | **Confirmed.** Note the canonical label is "data entity", not "data item"; alt labels are permitted. |
| `bfo:ObjectAggregate` as co-parent of Organization | `http://purl.obolibrary.org/obo/BFO_0000027` | "object aggregate" | "A material entity consisting of multiple objects as member parts. … can gain and lose parts while maintaining numerical identity." | **Confirmed.** Note: this is BFO 2020; BFO 1.0 also has the same class. |
| `bfo:Role` as parent of PublisherRole, DataProviderRole | `http://purl.obolibrary.org/obo/BFO_0000023` | "role" | "A role is a realizable entity that exists because some bearer is in special physical, social, or institutional circumstances… a role is not such that if it ceases to exist, the bearer's physical makeup changes." | **Confirmed.** Examples include professor, nurse, student — analogous to Publisher / DataProvider. |
| `foaf:Person` as parent of Expert | `http://xmlns.com/foaf/0.1/Person` | "Person" | FOAF Person. | **Confirmed.** |
| `foaf:Organization` as co-parent of Organization | `http://xmlns.com/foaf/0.1/Organization` | "Organization" | FOAF Organization. | **Confirmed.** |

### B.2 Audit flag — `iao:Document` as parent of `Chart` and `Screenshot`

`iao:Document` is defined as "**A collection of** information content entities intended to be understood together as a whole", with examples "journal article, patent application, laboratory notebook, book." A Chart (a single data visualisation) or a Screenshot (a single raster capture) is more naturally a **single** information content entity, not a *collection*.

**Recommendation:** re-route the media taxonomy under `iao:InformationContentEntity` with narrower IAO specialisations:

| `ei:` class | Recommended BFO/IAO parent | Rationale |
|---|---|---|
| `ei:Post` | `iao:Document` (`IAO_0000310`) | A post often *does* bundle text + media into a single understand-together unit → fits Document semantics. Keep scope.md's current alignment. |
| `ei:PodcastEpisode` | `iao:Document` (`IAO_0000310`) | An episode is a collection of segments, text description, and media. Document fits. Re-align from scope.md (scope has it on `iao:InformationContentEntity`). |
| `ei:PodcastSegment` | `iao:InformationContentEntity` (`IAO_0000030`) | A segment is a unit of information; not a collection-of-documents. Keep. |
| `ei:Chart` | `iao:Image` (`IAO_0000101`) | Chart is a 2-D graphical projection; `iao:Image` IS defined for this. Re-parent away from `iao:Document`. |
| `ei:Screenshot` | `iao:Image` (`IAO_0000101`) | Same reasoning; a screenshot is a raster projection. Re-parent. |
| `ei:Excerpt` | `iao:InformationContentEntity` (`IAO_0000030`) or `iao:TextualEntity` if present | An Excerpt is a quoted text fragment — a single ICE, not a Document. (`iao:TextualEntity` / `IAO_0000300` exists in some IAO releases; architect to verify against v2026-03-30.) |
| `ei:Image` | `iao:Image` (`IAO_0000101`) | Direct match. |
| `ei:MediaAttachment` (abstract) | `iao:InformationContentEntity` (`IAO_0000030`) | Abstract umbrella; keep at the ICE level so the five subclasses can pick their narrower IAO parent. |

**Loopback to conceptualizer:** this is a routing change, not an invariant change. Route: `missing_reuse` → conceptualizer → confirm IAO re-parenting for Chart/Screenshot/Excerpt. Low risk; addresses scope.md audit item explicitly.

### B.3 Confirmed: no BFO 2020 vs 1.0 divergence on target classes

`BFO:0000023 role`, `BFO:0000027 object aggregate`, `BFO:0000020 specifically dependent continuant` are identical between BFO 2.0 (Arp/Smith/Spear 2015) and BFO 2020 (ISO 21838-2:2021). No architect-visible divergence. Scope.md uses BFO 2020 terminology ("BFO 2020 category for institutional wholes") — OK.

---

## C. DCAT Agent unification (scope.md Open q #3)

**Finding:** DCAT 3 W3C Rec (2024 publication date, still current) **does not define `dcat:Agent` at all**. It recommends `foaf:Agent` as the range for `dcterms:creator` / `dcterms:publisher`. DCAT-AP 3.0 (SEMICeu) likewise does not assert any `owl:equivalentClass` between `dcat:Agent`, `foaf:Agent`, and `prov:Agent`; it references FOAF for generic agents and recommends the W3C Organization Ontology (`http://www.w3.org/ns/org#`) when the agent is an organisation.

**Recommendation for `energy-intel`:**

1. **Do not declare `owl:equivalentClass` between `dcat:Agent` and `foaf:Agent`.** `dcat:Agent` is not a published class; asserting equivalence would create a term the spec doesn't recognise.
2. **Declare `prov:Agent owl:equivalentClass foaf:Agent`** in a small **bridge** file (`ontologies/energy-intel/imports/prov-foaf-bridge.ttl`). This is the de-facto alignment used by every PROV-O consumer that also ships FOAF (W3C PROV-O spec itself notes "foaf:Agent is a `prov:Agent`" in informative text, and dozens of vocabularies including SPAR, DCAT-AP reference implementations, and data.gov catalogs rely on this equivalence).
3. **Align `ei:Organization` under FOAF.** Keep `ei:Organization rdfs:subClassOf foaf:Organization` from scope.md. `foaf:Organization rdfs:subClassOf foaf:Agent` is asserted by FOAF upstream, so `ei:Organization` reaches `foaf:Agent` transitively — no direct `rdfs:subClassOf foaf:Agent` needed on `ei:Organization`.
4. **CQ-010 `required_classes: [foaf:Agent]`** is satisfied by this setup: the `ei:referencesAgent` range is `ei:Organization`; `foaf:Agent` is the FOAF root reachable via FOAF's own taxonomy.

The bridge file goes through the Step 3.5 bridge-safety gate (run reasoner on merged bridge + FOAF + PROV; expect no unsatisfiables since FOAF and PROV define Agent compatibly).

**Reuse shape for this decision:** **bridge** (`prov-foaf-bridge.ttl`), not extra imports. Bridge is standalone and addable to `mappings/` per the scout skill convention.

---

## D. QUDT import depth (scope.md Open q #4)

**QUDT baseline facts:**

- QUDT v3.2.1 schema is modular (imports `qudt:schema/coordinateSystems`, `qudt:schema/datatype`, W3C standards).
- Core classes (always needed): `qudt:Unit`, `qudt:QuantityKind`, `qudt:Quantity`, `qudt:SystemOfUnits`, `qudt:QuantityKindDimensionVector`.
- License: **CC-BY 4.0**. Compatible.

**Three import scopes, ranked smallest to largest:**

| Option | What it pulls | Triple count estimate | Use when |
|---|---|---|---|
| **D.1 Units-only MIREOT** | `qudt:Unit` class + ~30 `unit:*` individuals actually referenced by CMC `ei:assertedUnit` surface tokens (GW, TWh, MW, kWh, Hz, V, MWh, t, kg, km³, bbl, BOE, bcm, PJ, tce, tonCO2e, gCO2/kWh, etc.) | ~500–1000 triples | **V0 default.** Covers CMC unit normalisation (the scope.md commitment for `assertedUnit` surface tokens). No quantity-kind reasoning needed. |
| **D.2 Units + QuantityKinds subset MIREOT** | D.1 + `qudt:QuantityKind` class + the ~50 quantity kinds ei will index (Power, Energy, Mass, Volume, Rate, etc.) + `qudt:hasQuantityKind` property | ~2500–4000 triples | V1+ when Variable gets the facet model (deferred; see scope.md Variable seven-facet deferral). Architect re-MIREOTs when V1 lands. |
| **D.3 Full QUDT schema + units vocabulary** | Full QUDT (~100k+ triples) | 100k–300k triples | **Do NOT pick.** Bloats reasoner, adds `qudt:CurrencyUnit`, `qudt:CoordinateSystem`, `qudt:PhysicalConstant` that are not in scope. |

**Recommendation:** **D.1 for V0**, revisit on V1. Term file: `ontologies/energy-intel/imports/qudt-terms.txt`, one unit IRI per line, starting with the 20-odd units observable in Skygest corpus. Architect runs `robot extract --method MIREOT` against `http://qudt.org/2.1/vocab/unit` pinning `2.1`.

**Reuse shape:** **module extraction (MIREOT)**, not full import.

---

## E. Namespace registration (scope.md Open q #2)

Trade-off between `https://w3id.org/energy-intel/` and `https://vocab.skygest.io/`:

| Dimension | `w3id.org/energy-intel/` | `vocab.skygest.io/` |
|---|---|---|
| Registration cost | One-time PR to `perma-id/w3id.org`. No SLA; typical community PRs merged in days to weeks. | Zero external dep; Skygest controls DNS. |
| Governance | Community-owned, PURL-like redirects. Re-registration blocked if Skygest abandons (good for downstream consumers). | Skygest-controlled; if Skygest shuts down, IRIs dereference fails. |
| Fits Skygest conventions | Fits nothing; introduces a second identity system alongside `id.skygest.io`. | Matches Linear D3 decision (`id.skygest.io/{kind}/{ulid}`) — ABox lives under Skygest domain; TBox also under Skygest domain is consistent. |
| Content negotiation | w3id.org supports `.htaccess`-driven content negotiation; architect / curator needs a separate GitHub-Pages or similar endpoint to serve Turtle/JSON-LD. | Skygest can serve content negotiation directly from the Worker; simpler ops. |
| Stability over decades | **Stronger** — w3id.org is a W3C-community-supported indirection layer designed precisely for this. | Depends on Skygest as an organisation. |
| FAIR scoring | Higher (w3id.org is an accepted FAIR vocabulary registry). | Lower until/unless Skygest publishes a stability commitment. |
| Downstream consumer trust | Higher for academic / gov integrations. | Higher for Skygest-internal integrations. |

**Recommendation: `https://w3id.org/energy-intel/`** for the TBox namespace, with the ABox staying at `https://id.skygest.io/{kind}/{ulid}` (per Linear D3).

Rationale: the TBox is the *contract* that external consumers depend on; it deserves the strongest stability guarantee. The ABox is runtime Skygest data and belongs under the Skygest-controlled domain. This is the split every mature ontology uses (PROV-O vocabulary at `http://www.w3.org/ns/prov#` but PROV data at whatever-you-like URIs; FOAF terms at `xmlns.com/foaf` but FOAF data at person-controlled URIs; DCAT at `w3.org/ns/dcat` but catalogues at publisher URIs).

**Action for architect:** file PR against `perma-id/w3id.org` establishing the `/energy-intel/` redirect to the GitHub-Pages or Cloudflare-Pages site that hosts the Turtle artefact. Not blocking V0 TBox authoring — the namespace can be minted and artefact-hosted before the PR merges; the PR just establishes the persistent redirect.

---

## F. Ontology Design Patterns (ODPs) to adopt

Sourced from `_shared/pattern-catalog.md` (project-internal catalog) + `ontologydesignpatterns.org` (ODP portal, partial — three Submissions pages timed out at automation time; architect to re-verify after resolving portal access). Each pattern includes variable bindings and the downstream axiom pattern row.

See [`docs/odp-recommendations.md`](odp-recommendations.md) for the full one-pager per pattern. Summary:

| # | ODP | Source | Serves CQs | Key variable bindings |
|---|---|---|---|---|
| F.1 | **Value partition** | `_shared/pattern-catalog.md § 3.1` | CQ-013, CQ-014 (temporal-resolution hand-seed); CQ-010 (resolution-grain-derived-from-which-references-populated is not a pure value partition but adjacent) | `{Quality: ei:TemporalResolution, Values: {hourly, daily, monthly, quarterly, annual}}` |
| F.2 | **Role** (BFO realizable) | `_shared/pattern-catalog.md § 3.3`; BFO 2020 axiom library | Implicit in every CQ that walks through Organization's publisher/data-provider behavior (extends to CQ-007/CQ-008 audit questions) | `{Bearer: ei:Organization, Role: ei:PublisherRole \| ei:DataProviderRole}`. Role inheres in Organization; realized in a publication/data-release process (ABox phase). |
| F.3 | **Information realization (IAO)** | `_shared/pattern-catalog.md § 3.6`; ODP portal `Submissions:Information_Realization` (timed out; `_shared` is authoritative mirror) | CQ-001, CQ-009, CQ-012 (`ei:evidences` triangle); CQ-005 (CMC → Distribution) | `{InformationEntity: ei:CanonicalMeasurementClaim, AboutEntity: ei:Variable \| Series \| Dataset \| Distribution \| ei:Organization, Bearer: ei:Post \| MediaAttachment \| PodcastSegment}`. The `ei:evidences` relation is the "concretizedBy / informationBearer" arrow; `ei:references*` is the "isAbout" arrow. |
| F.4 | **Participation** | `_shared/pattern-catalog.md § 3.4`; BFO 2020 | CQ-002 (`ei:authoredBy`), CQ-007 (Expert-reference join), CQ-011 (`ei:spokenBy`) | `{Participant: ei:Expert, Process: authoring / speaking-in-podcast}`. V0 uses binary shortcut properties (`authoredBy`, `spokenBy`) per scope Decisions; V1+ may reify into Process individuals. |
| F.5 | **Part-whole (mereology)** | `_shared/pattern-catalog.md § 3.2` | CQ-012 (PodcastSegment `partOf` PodcastEpisode); Thread reply-tree (CQ-none in V0 but referenced by scope.md SocialThread design) | `{Whole: ei:PodcastEpisode, Part: ei:PodcastSegment}`. Ordering via `ei:hasSegmentIndex xsd:integer` (scope.md). |

*Not recommended:* Sequence / ordered list pattern for SocialThread (reply partial-order was locked in scope.md § Conversation shape — `ei:repliesTo` is a plain binary, not a list).

*Not recommended:* N-ary reification ODP in V0. Scope.md dropped both the resolution-state enum and the source-modality enum; the current CMC model stays binary. Reserve N-ary for V1 when the seven-facet Variable or the extraction-activity individuals land.

---

## G. Conflicts / warnings

| Conflict | Severity | Scope.md reference | Recommendation |
|---|---|---|---|
| **`OEO_00000030` is wrong** — scope Open q #1 uses it as the energy-technology root candidate; it actually labels "oil power unit". | **High — blocking for architect's first OEO extract** | scope.md § Open questions #1 | Use `OEO_00000011` (energy converting component) or `OEO_00010385` (energy transformation function) as provisional candidate; architect verifies via `robot query` on v2.11.0 and logs the verified root in `imports-manifest.yaml`. Log this fix as a scope-amendment for the next requirements refresh (see "Gaps for requirements loopback" below). |
| **No temporal-resolution taxonomy in OEO.** Scope open q #1 assumes OEO has one. | **Medium — requires conceptualizer decision** | scope.md § Open questions #1 | Hand-seed a five-value `skos:Concept` partition in V0 (value-partition ODP F.1). Track as "propose upstream to OEO" work item in `ontology-curator` backlog. |
| **OEO `quantity value` (`OEO_00000350`) is not a `qudt:QuantityKind` equivalent** — it's a value, not a kind. | **Low — informational** | scope.md § Open questions #1 mentions "quantity-kind root … linkable to `qudt:QuantityKind`" | Use QUDT (D.1 above) for quantity kinds; do not import OEO quantity tree. Any cross-ref lives as a SSSOM mapping in the mapper phase. |
| **`iao:Document` parent for `Chart` / `Screenshot` / `Excerpt`** conflicts with IAO's own definition of Document as a *collection*. | **Medium — conceptualizer re-parenting** | scope.md § Decisions resolved / BFO upper alignment | Re-parent per § B.2 table: Chart / Screenshot / Image → `iao:Image`; Excerpt → `iao:InformationContentEntity` or `iao:TextualEntity`; Post, PodcastEpisode → `iao:Document`. Non-blocking loopback to conceptualizer. |
| **`ei:Organization rdfs:subClassOf foaf:Organization + bfo:ObjectAggregate`** — dual parent is allowed in OWL 2 DL and consistent with BFO 2020's `object aggregate` definition. | **None — confirmed** | scope.md § Decisions resolved / Agent layer | Ship as-is. Note in `scope.md § Decisions` already captures why BFO 2020 vs 1.0 doesn't matter here. |
| **`dcat:Agent`** mentioned in scope.md as a thing to unify — DCAT 3 does not define `dcat:Agent`. | **Low — spec gap, not ontology bug** | scope.md § Open questions #3 | Drop `dcat:Agent` from the alignment discussion; treat the PROV/FOAF equivalence as the only alignment needed (§ C above). |

---

## H. Reuse-decision matrix (every candidate, scored on six dimensions)

Per scout skill Step 2. Scored on 1–5 (5=best) where applicable; "n/a" where the dimension doesn't resolve.

### H.1 Selected candidates

| # | Candidate | Scope fit | License | Maintenance | Import size | Identifier policy | Profile implications | Import shape | Rationale |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|---|---|
| 1 | **BFO 2020** | 5 | CC-BY 4.0 | 5 (ISO 21838-2 standardised; yearly cadence) | 5 (small) | 5 (PURLs, versioning, obsolete marks) | 5 (OWL 2 DL native) | **Full import** | Already committed in scope. Small, stable, normative. |
| 2 | **IAO v2026-03-30** | 5 | CC-BY 4.0 | 4 (active, quarterly cadence) | 4 (moderate) | 5 | 5 | **MIREOT / STAR** (seeds: IAO_0000030, _0000310, _0000101, _0000027; optionally _0000300 if TextualEntity survives) | Scope commits to IAO for Document / ICE parents. MIREOT keeps footprint tight. |
| 3 | **OEO v2.11.0** (4 subtree extracts) | 4 (technology + carrier + aggregation type covered; temporal resolution missing) | CC-BY 4.0 | 5 (monthly-to-quarterly releases; v2.11.0 2026-03-04) | 3 (4 BOT extracts ~250–500 classes total) | 5 (strong PURLs, obsolete handling) | 5 (OEO itself is OWL 2 DL) | **BOT module extraction** (4 seed files in `imports/oeo-*-terms.txt`) | Scope committed. Verify energy-technology root before extract (see § G). |
| 4 | **QUDT 2.1 units vocabulary** | 4 (units covered; quantity kinds deferred) | CC-BY 4.0 | 4 (v3.2.1 2025; active) | 2 (full QUDT huge; MIREOT ~500 triples) | 5 | 5 | **MIREOT** (units only — D.1) | Do NOT import full QUDT; MIREOT 20–30 unit individuals + `qudt:Unit` class. |
| 5 | **DCAT 3** | 5 (full DCAT 7-entity set needed) | W3C Document Licence (permissive) | 5 (W3C Rec, stable) | 5 (small vocab, ~100 terms) | 5 | 5 | **Full import** | Scope committed; full fidelity per user directive. |
| 6 | **PROV-O** | 5 | W3C Document Licence | 5 (W3C Rec, stable since 2013) | 5 (small) | 5 | 5 | **Full import** | Scope committed. Used for CMC provenance annotations. |
| 7 | **SKOS** | 5 | W3C Document Licence | 5 (W3C Rec) | 5 (small) | 5 | 5 | **Full import** | Scope committed. Alias semantics + value-partition concepts (CQ-013/CQ-014). |
| 8 | **FOAF 0.99** | 4 (Agent / Organization / Person covered) | CC-BY 1.0 | 3 (stable but low release cadence; 2014 last substantive update) | 5 (tiny) | 4 | 5 | **Full import** | Scope committed. |
| 9 | **Dublin Core Terms** | 5 | Public domain | 5 | 5 | 5 | 5 | **Full import** | Scope committed. Metadata backbone. |
| 10 | **PROV/FOAF bridge** (scout-authored in mapper phase) | 5 (resolves CQ-010 `foaf:Agent` requirement via transitive FOAF subclass) | inherits CC-BY | n/a | 5 (<10 triples) | n/a | 5 | **Bridge ontology** (`mappings/prov-foaf-bridge.ttl`) | See § C. Run Step 3.5 safety gate before publish. |

### H.2 Rejected candidates (rejection rationale mandatory per scout convention)

| # | Candidate | Why rejected |
|---|---|---|
| R1 | **Full QUDT schema** (not the units MIREOT) | >100k triples, bloats reasoner, includes out-of-scope domains (coordinate systems, physical constants). Units-only MIREOT (H.1 #4) satisfies CQ-008 without the bloat. |
| R2 | **schema.org `DataCatalog` / `Dataset`** | Redundant with DCAT 3; scope.md § Reused external ontologies explicitly prefers DCAT. schema.org re-enters as a *projection target* (Linear D6) not as an imported vocabulary. |
| R3 | **oeo-extended (OEOX)** | Active experiment repo, not yet release-cadenced. OEO core is sufficient for V0. Re-evaluate on scope-refresh if OEOX stabilises. |
| R4 | **schema.org `Article` / `SocialMediaPosting`** | Overlaps with Post + Document from IAO; scope.md § Reused external ontologies doesn't include schema.org. Keep out; revisit when the codec export (Linear D6) lands. |
| R5 | **Open Content in Creation (OCCO)** or other podcast-specific ontologies | None surveyed has the BFO alignment energy-intel requires; FOAF + IAO + our own `PodcastEpisode`/`PodcastSegment` classes suffice. |
| R6 | **OWL-Time** (`http://www.w3.org/2006/time#`) | Not imported in V0. `ei:ClaimTemporalWindow` with `ei:intervalStart`/`ei:intervalEnd` (scope.md § CMC / Observation details) is sufficient for CQ-008. If CQ-future demands transitive temporal reasoning, re-MIREOT OWL-Time's `time:ProperInterval` + `time:intervalBefore` family in that later phase. |
| R7 | **qb (RDF Data Cube)** | Scope.md non-goal #6 takes SPARQL/SHACL/RDF runtime off the table. qb adds DataStructureDefinition complexity that the V0 TBox does not need. Mention in curator backlog for V1+. |
| R8 | **Semantic Sensor Network (SOSA/SSN)** | Observation modelling overlaps with `ei:Observation` (thin in V0). SOSA could be adopted when the data-ingest lane lands; in V0 it's not paying for itself. |

---

## Gaps for requirements loopback (non-silent, per scout skill)

Scout was told not to edit scope.md; flagging these for the next `ontology-requirements` refresh:

1. **scope.md § Open questions #1** uses `OEO_00000030` as the candidate energy-technology root. That IRI labels "oil power unit"; it is wrong. Propose replacement: "Candidate: `OEO_00000011` (energy converting component) OR `OEO_00010385` (energy transformation function); architect to verify against v2.11.0 before extraction."
2. **scope.md § Open questions #1 "temporal-resolution root"** — OEO v2.11.0 has no such root. Hand-seed as a `skos:Concept` scheme in `ei:` namespace; document the upstream-OEO gap.
3. **scope.md § Open questions #1 "quantity-kind root"** — OEO's `quantity value` (`OEO_00000350`) is not the right abstraction for `qudt:QuantityKind`. Drop "OEO quantity tree" from the MIREOT plan; use QUDT directly.
4. **scope.md § Open questions #3 "DCAT Agent unification"** — clarify that `dcat:Agent` is not a published class. The unification we care about is `prov:Agent ≡ foaf:Agent`, via a bridge.
5. **`iao:Document` re-parenting for Chart/Screenshot/Excerpt** — recommendation in § B.2 changes scope.md § Decisions resolved BFO upper alignment bullet for the media subclasses. Conceptualizer decides; `missing_reuse` loopback raised to conceptualizer only if they disagree.

These are loopback triggers but **not blocking** for conceptualizer to start. Architect is blocked on (1) and (2) until conceptualizer signs off the OEO seed list and the hand-seeded temporal-resolution scheme.

---

## Handoff to conceptualizer + architect

**To conceptualizer** (`docs/scout-to-conceptualizer-handoff.md`): five bullets on BFO/IAO re-parenting decisions, hand-seed `TemporalResolution` value partition, PROV/FOAF bridge decision, OEO seed-IRI confirmation.

**To architect (direct, after conceptualizer signs off)**:
- `imports-manifest.yaml` with 10 pinned import rows.
- `imports/oeo-*-terms.txt` seed files (3 of 4 subtrees; temporal-resolution has no file — architect hand-builds in `ei:` namespace).
- `imports/qudt-terms.txt` with 20–30 unit IRIs (architect tightens from Skygest corpus observations).
- `imports/iao-terms.txt` with IAO_0000030, _0000310, _0000101, _0000027 (and optionally _0000300 if TextualEntity is wanted for Excerpt).
- Bridge spec in `mappings/prov-foaf-bridge.ttl` (mapper skill authors; scout flags).

No OWL axioms authored by scout. Architect owns all `.ttl` / `.owl` writes per scout anti-patterns and scope constraints.
