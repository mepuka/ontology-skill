# ODP Recommendations — `energy-intel`

**Authored:** 2026-04-22 by `ontology-scout`
**Consumer:** `ontology-conceptualizer` (pattern selection), `ontology-architect`
(axiom instantiation).
**Source pattern catalog:** [`_shared/pattern-catalog.md`](../../../.claude/skills/_shared/pattern-catalog.md)
(project-internal authoritative mirror) + [`_shared/axiom-patterns.md`](../../../.claude/skills/_shared/axiom-patterns.md)
(axiom rows each ODP compiles to).

Five ODPs recommended. Each entry carries: source, pattern name, applicable
CQs, variables, example instantiation, downstream axiom-pattern rows, tool
template. Per scout skill Step 5, every field is required — patterns without
the full set fail the scout Progress Criteria.

---

## F.1 — Value partition: `ei:TemporalResolution`

| Field | Content |
|---|---|
| `source` | `_shared/pattern-catalog.md § 3.1` |
| `pattern_name` | `value-partition` |
| `applicable_cqs` | CQ-013, CQ-014 (temporal-resolution filters on CMC-about-technology queries extend to a similar partition); future CQs asking "show me daily CMCs about solar" |
| `variables` | `{Quality: ei:TemporalResolution (skos:Concept parent), Values: {hourly, daily, monthly, quarterly, annual}}` |
| `example_instantiation` | `Quality: ei:TemporalResolution, Values: {ei:concept/temporal-resolution/hourly, ei:concept/temporal-resolution/daily, ei:concept/temporal-resolution/monthly, ei:concept/temporal-resolution/quarterly, ei:concept/temporal-resolution/annual}` |
| `downstream_axiom_pattern` | `_shared/axiom-patterns.md § 5 Disjoint` + `§ 6 Covering` + `§ 8 Value partition` (composed). Exposed to V0 as a `skos:ConceptScheme` with `skos:topConceptOf` + `skos:inScheme` on the five members. Full disjoint-union / covering axioms authored by architect in V1 if temporal-resolution becomes a CMC-side data property that carries reasoning obligations. |
| `tool_template` | Freehand OWL in V0 (5 SKOS individuals = trivial). Upgrade to a DOSDP `value-partition.yaml` template if more than one hand-seeded scheme lands (e.g., if a similar `ei:SeriesBasis` partition is authored). |
| `profile_notes` | SKOS Concept tree alone is OWL 2 DL safe. Upgrade to `owl:DisjointUnion` only if architect needs reasoner-visible covering; that keeps DL. |

**Why this ODP:** OEO has no temporal-resolution taxonomy (reuse-report § A.4);
hand-seeding the five concepts as a value partition gives architect a
stable range for any future `ei:hasTemporalResolution` property without
re-authoring when OEO eventually ships a temporal-resolution branch.

---

## F.2 — Role pattern: `ei:PublisherRole` / `ei:DataProviderRole`

| Field | Content |
|---|---|
| `source` | `_shared/pattern-catalog.md § 3.3` + BFO 2020 role axiomatisation (`BFO_0000023`) |
| `pattern_name` | `role` (realizable entity) |
| `applicable_cqs` | No V0 CQ directly queries roles, but every V0 CQ that crosses an `ei:Organization` boundary (CQ-005 via `ei:referencesDistribution` → DCAT `dcat:publisher` → Organization, CQ-010 via `ei:referencesAgent`) implicitly assumes the role structure. Architect authors the roles now so scope.md § Agent layer stays consistent. |
| `variables` | `{Bearer: ei:Organization, Role: ei:PublisherRole \| ei:DataProviderRole, RealizedInProcess: (ABox-phase) publication / data-release}` |
| `example_instantiation` | `Bearer: ei:Organization/EIA, Role: ei:DataProviderRole, RealizedInProcess: (deferred to ABox phase — use prov:Activity individual at that point)` |
| `downstream_axiom_pattern` | `_shared/axiom-patterns.md § 2 Existential` (`ei:PublisherRole SubClassOf (RO:inheresIn some ei:Organization)`) + `§ 4 Equivalent class` if the role is realized. Keep to § 2 only in V0; add realization axioms when ABox `prov:Activity` individuals land. |
| `tool_template` | Freehand OWL. Two classes, two SubClassOf axioms each, no DOSDP needed. |
| `profile_notes` | Role as existential `some` restriction is EL-safe. The full realizable-entity axiomatisation (disposition-type dependency) requires DL; scope.md § Reasoning locks OWL 2 DL so no profile risk. |

**Why this ODP:** scope.md § Agent layer explicitly chose Role over subclassing
Person/Organization. The role pattern is the canonical BFO mechanism; see
[`_shared/bfo-decision-recipes.md`](../../../.claude/skills/_shared/bfo-decision-recipes.md)
§ "role vs type" recipe.

**Anti-pattern checked:** scope.md does NOT collapse `Publisher` into a class
that subclasses `Organization`. That would be the "Role leak" anti-pattern
in `_shared/anti-patterns.md`. scope.md § Decisions resolved already
rejects this ("Publisher = PublisherRole (bfo:Role) borne by Organization
— not a class").

---

## F.3 — Information realization: CMC ↔ `ei:evidences` ↔ `ei:references*`

| Field | Content |
|---|---|
| `source` | `_shared/pattern-catalog.md § 3.6` (Information-Realization). ODP portal canonical: `http://www.ontologydesignpatterns.org/cp/owl/informationrealization.owl` (Submissions:Information_Realization timed out at 2026-04-22; catalog mirror is authoritative). |
| `pattern_name` | `information-realization` |
| `applicable_cqs` | CQ-001 (`ei:evidences` post-to-CMC), CQ-009 (CMC invariant — at least one evidencing artefact), CQ-012 (segment-to-CMC), CQ-005 (CMC → Distribution, reading Distribution as the bearer of the data-item that the CMC is *about*) |
| `variables` | `{InformationEntity: ei:CanonicalMeasurementClaim, AboutEntity: ei:Variable \| ei:Series \| dcat:Dataset \| dcat:Distribution \| ei:Organization, Bearer: ei:Post \| ei:Chart \| ei:Screenshot \| ei:Excerpt \| ei:Image \| ei:PodcastSegment}` |
| `example_instantiation` | `InformationEntity: ei:CanonicalMeasurementClaim/cmc_ember_814gw, AboutEntity: ei:Variable/var_solar_installed_capacity, Bearer: ei:Chart/chart_ember_814gw_bsky` |
| `downstream_axiom_pattern` | `_shared/axiom-patterns.md § 2 Existential` (`ei:CanonicalMeasurementClaim SubClassOf (inverse ei:evidences) min 1 (ei:Post ∪ ei:MediaAttachment ∪ ei:PodcastSegment)`, which is CQ-009's invariant). Plus IAO's own `is about` (`IAO:0000136`) can be asserted as a super-property of the `ei:references*` family to give the architecture portability. Not required in V0 but ODP-compliant if added. |
| `tool_template` | Freehand OWL for V0. Promote to a DOSDP template only if a second ICE-type (e.g., `Observation`) lands that needs the same triangle. |
| `profile_notes` | All three axioms stay in EL if restricted to `some` restrictions. CQ-009's closure (`min 1`) is cardinality — requires OWL 2 DL. scope.md locks DL so safe. |

**Why this ODP:** this is the single most important pattern for
`energy-intel`. The entire CMC architecture is a specialisation of
Information Realization: the claim (ICE) is *about* a Variable / Series
/ Dataset / Distribution / Organization, and is *concretized by* a Post /
Chart / Screenshot / Excerpt / Image / PodcastSegment (the media bearer).
Using the pattern names explicitly in the conceptual model lets
downstream consumers recognise the shape.

**Semantics note:** the pattern's "realized in" arrow (a process) is NOT
modelled in V0 (scope.md defers `prov:Activity` individuals to ABox).
The pattern degrades gracefully to the two-arrow form (about + concretised)
in V0; the third arrow lights up at ABox time.

---

## F.4 — Participation: `ei:authoredBy`, `ei:spokenBy`

| Field | Content |
|---|---|
| `source` | `_shared/pattern-catalog.md § 3.4`. ODP portal canonical: `http://www.ontologydesignpatterns.org/cp/owl/participation.owl` (Submissions:Participation timed out at 2026-04-22; catalog mirror is authoritative). |
| `pattern_name` | `participation` |
| `applicable_cqs` | CQ-002 (`ei:authoredBy`), CQ-007 (cross-expert join via authoredBy), CQ-011 (`ei:spokenBy`) |
| `variables` | `{Participant: ei:Expert, Process: authoring (for Post), speaking-in-podcast (for PodcastSegment)}` |
| `example_instantiation` | `Participant: ei:Expert/did-plc-a5kyzplew76jaj4dhnqsosjv, Process: authoring, MaterialBearer: ei:Post/post_01J_example` |
| `downstream_axiom_pattern` | `_shared/axiom-patterns.md § 2 Existential`. V0 collapses the process to a binary shortcut: `ei:Post SubClassOf ei:authoredBy exactly 1 ei:Expert` (CQ-002 `required_axioms`). The full reified form (author individual + Process individual + ro:hasParticipant) lands in V1 when editorial-role provenance matters. |
| `tool_template` | Freehand OWL; two properties with domain/range + cardinality. |
| `profile_notes` | Binary shortcut form is EL-safe. Full reification stays OWL 2 DL. Scope.md § Reasoning locks DL. |

**Why this ODP:** scope.md's Decision resolved "Expert → strict foaf:Person
subclass. No bfo:Role on the expert side in V0" means we are NOT modelling
authorship as a role. That's consistent with Participation-lite: the
Expert participates in the authoring process, shortcut to `ei:authoredBy`
in V0. Keep the ODP named in the architect's axiom plan so the expansion
path is explicit.

**Anti-pattern checked:** binary shortcut without a path to N-ary
reification is the "lost arguments" trap from `_shared/anti-patterns.md`.
Calling out the Participation ODP here means the N-ary expansion path is
documented, not hidden.

---

## F.5 — Part-whole: `ei:PodcastSegment partOf ei:PodcastEpisode`

| Field | Content |
|---|---|
| `source` | `_shared/pattern-catalog.md § 3.2` (part-whole / mereology), composed with the `BFO:0000050 part of` relation. |
| `pattern_name` | `part-whole` |
| `applicable_cqs` | CQ-011, CQ-012 (both query PodcastSegment); implicit in scope.md's Conversation shape for SocialThread (though thread uses `ei:repliesTo`, not part-of — flagged below) |
| `variables` | `{Whole: ei:PodcastEpisode, Part: ei:PodcastSegment, OrderingKey: ei:hasSegmentIndex xsd:integer}` |
| `example_instantiation` | `Whole: ei:PodcastEpisode/ep_01J_volts_winter, Part: ei:PodcastSegment/seg_01J_04_interview_utility_ceo, OrderingKey: 4` |
| `downstream_axiom_pattern` | `_shared/axiom-patterns.md § 2 Existential` (`ei:PodcastSegment SubClassOf ei:partOf some ei:PodcastEpisode`) + `§ 7 Qualified cardinality` (`ei:PodcastSegment SubClassOf ei:partOf exactly 1 ei:PodcastEpisode` per scope.md). The `ei:hasSegmentIndex` is a data property outside the part-whole pattern proper; it provides a total-order projection over siblings. |
| `tool_template` | Freehand OWL; one property with domain/range + cardinality + one data property. |
| `profile_notes` | Qualified cardinality is NOT in OWL 2 EL; it IS in OWL 2 DL. scope.md locks DL so safe. If architect ever retargets EL, drop the `exactly 1` → `some` and lose the cardinality closure. |

**Why this ODP:** PodcastSegment is genuine mereology (a segment is a
temporal part of an episode, not a member). Using the part-whole ODP name
clarifies this against the Thread case where reply-tree is a partial
order, NOT a part-whole. The two patterns must not be conflated.

**Not used for SocialThread:** scope.md § Conversation shape: "SocialThread
modelled via ei:repliesTo partial-order (not ordered-list)". `ei:repliesTo`
is a plain binary property; no part-whole or sequence ODP applies. Noting
this explicitly so the conceptualizer does not accidentally promote
SocialThread to a List/Sequence ODP when they scan the CQs.

---

## Pattern-selection table (CQ → ODP → axiom pattern)

Cross-reference for `ontology-conceptualizer` Step "Axiom Pattern Selection":

| CQ | Primary ODP | Secondary ODP | Axiom-pattern rows |
|---|---|---|---|
| CQ-001 | F.3 Information realization | — | § 2 Existential |
| CQ-002 | F.4 Participation | — | § 2 Existential + § 7 Qualified cardinality (`exactly 1`) |
| CQ-003 | F.3 Information realization | — | § 2 Existential + § 7 (`max 1`) |
| CQ-004 | F.3 Information realization | — | § 2 Existential + § 7 (`max 1`) |
| CQ-005 | F.3 Information realization | — | § 2 Existential + § 7 (`max 1`) |
| CQ-006 | F.3 Information realization (inverse view) | — | § 2 Existential (on inverse) |
| CQ-007 | F.3 + F.4 | — | § 2 Existential chain (evidences + authoredBy) |
| CQ-008 | F.3 + F.4 | — | § 2 Existential + § 10 Data property |
| CQ-009 | F.3 Information realization (invariant) | — | § 2 Existential + § 7 (`min 1`) — this is the pattern's hard invariant |
| CQ-010 | F.3 Information realization (enumeration of references) | — | § 10 or § 2 on each `ei:references*` + `max 1` on each |
| CQ-011 | F.4 Participation | — | § 2 Existential |
| CQ-012 | F.3 Information realization (segment as bearer) + F.5 Part-whole | — | § 2 Existential + § 7 (`exactly 1` on partOf) |
| CQ-013 | F.1 Value partition (via skos:broader transitive closure) + F.3 | — | Property path on `skos:broader \| rdfs:subClassOf` — SPARQL 1.1 property path; not a reasoner axiom |
| CQ-014 | F.1 + F.3 | — | Property path (SPARQL); architect keeps aboutTechnology as annotation-like property with `owl:ObjectProperty` type |

---

## Sources

- [`_shared/pattern-catalog.md`](../../../.claude/skills/_shared/pattern-catalog.md) — project-internal ODP catalog (authoritative mirror).
- [`_shared/axiom-patterns.md`](../../../.claude/skills/_shared/axiom-patterns.md) — axiom-row index compiled by ODPs.
- [`_shared/modularization-and-bridges.md`](../../../.claude/skills/_shared/modularization-and-bridges.md) — import-vs-bridge-vs-copy decision tree.
- [`_shared/bfo-decision-recipes.md`](../../../.claude/skills/_shared/bfo-decision-recipes.md) — role-vs-type recipe used by F.2.
- [Ontology Design Patterns portal](http://ontologydesignpatterns.org/wiki/Main_Page) — external ODP source; Submissions:{Role, Participation, Information_Realization} pages timed out on 2026-04-22; `_shared/pattern-catalog.md` is authoritative mirror. Architect re-verifies portal access during the conceptualizer loop.
- [BFO 2020](http://purl.obolibrary.org/obo/bfo.owl) — role / participation axiomatisation.
- [IAO v2026-03-30](https://github.com/information-artifact-ontology/IAO) — `IAO:0000136` `is about`, used by F.3.

## LLM verification note (scout skill Class B)

Each ODP pick above cites its pattern source + gives an instantiation table with variable bindings. Per [`_shared/llm-verification-patterns.md`](../../../.claude/skills/_shared/llm-verification-patterns.md) § "ODP applicability picks", that is the minimum evidence gate; this document meets it.
