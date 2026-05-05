# Conceptual Model — `energy-intel`, V2 Delta (Editorial Extension)

**Authored:** 2026-05-04 by `ontology-conceptualizer` (V2 iteration)
**Predecessor:** [conceptual-model-v1.md](conceptual-model-v1.md) (V1; commit `1d8f9da`)
**Reviewer:** Mepuka Kessy (`kokokessy@gmail.com`)
**Reviewed at:** 2026-05-04
**Source plan (canonical):** [`/Users/pooks/Dev/skygest-cloudflare/docs/plans/2026-05-04-editorial-ontology-slice.md`](file:///Users/pooks/Dev/skygest-cloudflare/docs/plans/2026-05-04-editorial-ontology-slice.md)
**Handoff:** [`docs/HANDOFF-2026-05-04-editorial-extension.md`](../../../docs/HANDOFF-2026-05-04-editorial-extension.md)

**Inputs consumed:**
- Requirements V2: [`scope-v2.md`](scope-v2.md), [`competency-questions-v2.yaml`](competency-questions-v2.yaml), [`use-cases-v2.yaml`](use-cases-v2.yaml), [`requirements-approval-v2.yaml`](requirements-approval-v2.yaml).
- Design review: 3 multi-agent design reviews (BFO/OEO modeling, system integration, migration safety) — findings baked into source plan §1.
- OEO seed-IRI verification: this session, all 41 candidates verified against `imports/oeo-full.owl` (owl:Class typing, label match, no deprecation).

This document is a **delta** to V1. V1 conceptual-model-v1.md remains authoritative for V1 scope; V0 conceptual-model.md remains authoritative for V0 scope. V2 lands the editorial extension (Narrative + NarrativePostMembership + ArgumentPattern SKOS scheme + NarrativeRole SKOS scheme + topic vocabulary cutover) and answers the four blocking questions [V2-CQ-Q-1 / V2-CQ-Q-2 / V2-CQ-Q-3 / V2-CQ-Q-4](requirements-approval-v2.yaml).

---

## 0. Inbound gate verification

| Artifact | Owner | Verified |
|---|---|---|
| `requirements-approval-v2.yaml` | requirements | signed by `kokokessy@gmail.com` 2026-05-04, `cq_freeze_commit: 1d8f9da` |
| `imports-manifest.yaml` | scout (V0+V1 baseline) | V2 adds no top-level imports; existing manifest covers BFO+IAO+OEO subsets+QUDT+SKOS+FOAF+DCAT+PROV-O+DCT |
| `competency-questions-v2.yaml` | requirements | 11 V2 CQs (CQ-N1..N8, CQ-T1..T3) — every Must-Have has priority + owner + testability + expected_answer_shape |

Inbound gate: **PASS**. No upstream loopback raised.

---

## 1. Scope of V2 conceptual changes

V2 adds **two new local classes**, **six new object properties**, **declares three new SKOS schemes**, **rebuilds the OEO topic subset**, and **retires one V1 SKOS scheme** (`technology-seeds.ttl`). No V0 or V1 class is renamed or deleted. No V0 or V1 axiom is invalidated.

| Change kind | Item | Module | Status |
|---|---|---|---|
| New local class | `ei:Narrative` | `editorial` (new module) | additive |
| New local class | `ei:NarrativePostMembership` | `editorial` (new module) | additive |
| New object property | `ei:hasNarrativePostMembership` | `editorial` | additive |
| New object property | `ei:memberPost` (FunctionalProperty) | `editorial` | additive |
| New object property | `ei:memberRole` (FunctionalProperty) | `editorial` | additive |
| New object property | `ei:narrativeMentionsExpert` | `editorial` | additive |
| New object property | `ei:narrativeAppliesPattern` | `editorial` | additive |
| New object property | `ei:narrativeAboutTopic` | `editorial` | additive |
| New SKOS scheme | `ei:concept/argument-pattern` (7 concepts) | `concept-schemes/argument-pattern.ttl` | additive |
| New SKOS scheme | `ei:concept/narrative-role` (4 concepts) | `concept-schemes/narrative-role.ttl` | additive |
| New SKOS scheme(s) | `ei:concept/oeo-topic` + `ei:concept/editorial-supplement` + `ei:concept/topic` (aggregator) | `concept-schemes/oeo-topics.ttl` | additive (split + aggregator decision per V2-CQ-Q-1 below) |
| New import subset | `imports/oeo-topic-subset.ttl` (rebuilt from `oeo-full.owl` against the 41-IRI seed list) | imports/ | additive |
| Retired | `concept-schemes/technology-seeds.ttl` (V1 hand-seeded scheme) | `concept-schemes/` | replaced by oeo-topics.ttl; CQ-013/CQ-014/CQ-015 fixtures rebind to OEO IRIs |

Total local class count after V2: **24 local classes** (V1's 22 + `ei:Narrative` + `ei:NarrativePostMembership`). Within the 20-30 module budget; **module split required** — see § 2 below. Layer assignments unchanged at the architecture-layering level (still all in problem-specific layer).

---

## 2. New module — `editorial`

### Decision: a fifth local module is created

V2 adds a fifth module alongside `agent`, `media`, `measurement`, `data`. Rationale per [`_shared/modularization-and-bridges.md § split triggers`](../../../.claude/skills/_shared/modularization-and-bridges.md):

1. **Behavioral vs functional view.** Editorial classes (`Narrative`, `NarrativePostMembership`) describe an editorial *workflow* — a deliberate authoring process by which experts and posts are curated into a narrative. The four V0+V1 modules describe data structures (claims, media artefacts, agents, datasets). Editorial is an editorial-process layer, not a data-structure layer.
2. **Lifecycle slice.** Narratives are *as-curated* artefacts; CMCs are *as-extracted*; Datasets are *as-published*. These are different lifecycle slices and the module split prevents a future change to editorial workflow from forcing changes in the data-structure modules.
3. **Independent stakeholder community.** Editorial-extension classes are owned by the editorial pipeline (`skygest-editorial`'s `hydrate-story` / `import-narratives` CLIs). The data-structure modules are owned by the cloudflare runtime resolver. Module split mirrors the consumer split.

Module count after V2: **5** (agent, media, measurement, data, editorial). Architecture layers unchanged: all five are problem-specific.

### Editorial module composition

| Item | Type | Defined by |
|---|---|---|
| `ei:Narrative` | Class | new in V2 |
| `ei:NarrativePostMembership` | Class | new in V2 |
| `ei:hasNarrativePostMembership` | ObjectProperty | new in V2 |
| `ei:memberPost` | ObjectProperty (FunctionalProperty) | new in V2 |
| `ei:memberRole` | ObjectProperty (FunctionalProperty) | new in V2 |
| `ei:narrativeMentionsExpert` | ObjectProperty | new in V2 |
| `ei:narrativeAppliesPattern` | ObjectProperty | new in V2 |
| `ei:narrativeAboutTopic` | ObjectProperty | new in V2 |

Reuses (no local mints): `iao:0000310` (Document, V0 import), `foaf:Person` (V0/V1 import), `ei:Post` (V0 from `media`), `ei:Expert` (V0/V1 from `agent`), `skos:Concept` + `skos:ConceptScheme` (V0 import), `bfo:0000023` (BFO Role; only relevant to existing role classes, not new in V2).

---

## 3. Taxonomy delta — V2 additions

### 3.1 Narrative

```
iao:InformationContentEntity (BFO_GDC)
  └── iao:Document (IAO_0000310)
        ├── ei:Post                       (V0; modules/media.ttl)
        ├── ei:PodcastEpisode             (V0; modules/media.ttl)
        ├── ei:PodcastSegment             (V0; modules/media.ttl)
        ├── ei:Chart, Screenshot, Excerpt, Image (V0; subclasses of MediaAttachment which is iao:ICE)
        ├── ei:Narrative                  (V2; modules/editorial.ttl)  ← NEW
        └── ei:NarrativePostMembership    (V2; modules/editorial.ttl)  ← NEW
```

### 3.2 BFO leaf decision (preview — full rationale in [bfo-alignment-v2.md](bfo-alignment-v2.md))

Both new classes sit at `iao:Document` (`IAO_0000310`). This matches existing `Post`/`PodcastEpisode` placement in `modules/media.ttl`. Critical pre-ratified design decision from source plan §3.2 + multi-agent BFO/OEO modeling review: a Narrative is a *written editorial unit about events, not the events themselves*. A NarrativePostMembership is *an information artefact recording a (narrative, post, role) tuple, not the social act of attaching*. Both are document-like ICEs.

Why `iao:Document` rather than abstract `iao:InformationContentEntity`:
- An abstract ICE leaves the BFO leaf under-specified, and the existing precedent in `modules/media.ttl` is to use `iao:Document` for any class that has identifiable boundaries (a Post has start+end characters, a Narrative has start+end markdown, a NarrativePostMembership is a single record with a deterministic IRI).
- Source plan multi-agent BFO/OEO modeling review explicitly upgraded this from "abstract ICE" to "iao:Document" — a critical finding baked into the locked decisions in §1.

Source plan §1 design-review critical findings (re-stated for traceability):
- Narrative re-parented from abstract ICE to `iao:Document` to match existing Post/PodcastEpisode.
- ArgumentPattern shifted from `owl:Class` + ABoxed individuals to a `skos:ConceptScheme` with `skos:Concept` instances (matches existing EnergyTopic SKOS pattern).
- Narrative→Post relationships use a reified n-ary relation (`NarrativePostMembership`) rather than 4 role-named predicates.

---

## 4. SKOS scheme split — V2-CQ-Q-1 decision

**Question:** Single `ei:concept/topic` scheme, OR split into `ei:concept/oeo-topic` + `ei:concept/editorial-supplement` + aggregator?

### Decision: **(b) Split + aggregator.**

Three SKOS ConceptSchemes:

```
ei:concept/oeo-topic
  ├── (the 41 verified OEO class IRIs — admitted via OWL 2 punning as
  │    skos:Concept individuals when used as values of ei:narrativeAboutTopic)
  └── (no new IRIs minted; OEO IRIs are reused as-is)

ei:concept/editorial-supplement
  ├── ei:concept/data-center-demand
  ├── ei:concept/distributed-energy
  ├── ei:concept/grid-and-infrastructure
  ├── ei:concept/electrification
  ├── ei:concept/energy-efficiency
  ├── ei:concept/energy-policy
  ├── ei:concept/energy-markets
  ├── ei:concept/energy-finance
  ├── ei:concept/energy-geopolitics
  ├── ei:concept/critical-minerals
  ├── ei:concept/climate-and-emissions
  ├── ei:concept/carbon-markets
  ├── ei:concept/environment-and-land-use
  ├── ei:concept/energy-justice
  ├── ei:concept/sectoral-decarbonization
  ├── ei:concept/workforce-and-manufacturing
  └── ei:concept/research-and-innovation

ei:concept/topic   (aggregator scheme)
  ├── (transitively contains every member of ei:concept/oeo-topic
  │    via skos:inScheme)
  └── (transitively contains every member of ei:concept/editorial-supplement)
```

### Rationale

1. **Semantic correctness.** Source plan §9 Q7 captures the concern: claiming OEO IRIs as members of a Skygest-namespaced `ei:concept/...` scheme they don't natively belong to is semantically off. The OEO IRIs already live in their own namespace (`https://openenergyplatform.org/ontology/oeo/`); they should not be relabelled as Skygest concepts. The split scheme separates "this is an OEO topic" (handled via punning + `skos:inScheme ei:concept/oeo-topic`) from "this is a Skygest-coined editorial umbrella" (handled directly by individuals in `ei:concept/editorial-supplement`).

2. **Aggregator-driven runtime.** The runtime queries (CQ-N4, CQ-T1) target *any* topic IRI regardless of source. The aggregator scheme `ei:concept/topic` provides the single SPARQL filter point: `?concept skos:inScheme ei:concept/topic` returns both OEO and supplement topics. Without the aggregator, runtime queries would need `UNION` or `VALUES` clauses to combine schemes, which is more brittle and slower.

3. **Cleaner skos:topConceptOf.** Each sub-scheme can declare its own `skos:hasTopConcept` set (technology vs umbrella). The aggregator inherits these via `skos:inScheme`. Mixing all 60+ topics into one scheme would produce a flat top-concept list that does not reflect the natural domain split.

4. **Future-friendly.** Adding a new scheme (e.g., `ei:concept/newsletter-edition` once Edition becomes ontologized) is a straightforward additive change — declare the new scheme, link it via `ei:concept/topic` aggregation. With a single scheme this would be a breaking change.

### Architect axioms (Manchester sketch)

```turtle
ei:concept/oeo-topic a skos:ConceptScheme ;
  rdfs:label "energy topics from the Open Energy Ontology"@en ;
  skos:definition "Topic concepts sourced from OEO. Each member is an
    OEO class IRI admitted as a skos:Concept individual via OWL 2 punning."@en .

ei:concept/editorial-supplement a skos:ConceptScheme ;
  rdfs:label "editorial topic supplements"@en ;
  skos:definition "Topic concepts coined by Skygest editorial because
    OEO has no clean equivalent. Each member is a skos:Concept individual
    in the https://w3id.org/energy-intel/concept/ namespace, carrying
    a skos:notation with the legacy editorial topic_slug."@en .

ei:concept/topic a skos:ConceptScheme ;
  rdfs:label "energy topics (aggregator)"@en ;
  skos:definition "Aggregator scheme over ei:concept/oeo-topic and
    ei:concept/editorial-supplement. Runtime queries target this scheme."@en .

# Membership pattern:
# - OEO IRIs become members of ei:concept/oeo-topic via punning + skos:inScheme
# - Supplement IRIs become members of ei:concept/editorial-supplement directly
# - Both transitively become members of ei:concept/topic via skos:inScheme

# Example (architect emits per OEO IRI):
oeo:OEO_00010427 skos:inScheme ei:concept/oeo-topic ,
                                ei:concept/topic .

# Example (architect emits per supplement IRI):
ei:concept/data-center-demand a skos:Concept ;
  skos:prefLabel "data center demand"@en ;
  skos:definition "Editorial umbrella for narratives about data center
    energy consumption and grid impact."@en ;
  skos:notation "data-center-demand" ;
  skos:inScheme ei:concept/editorial-supplement , ei:concept/topic ;
  skos:closeMatch oeo:OEO_00310000 .  # OEO 'data center' class
```

### Closure / OWA implications

- A topic IRI not asserted as `skos:inScheme` of any Skygest scheme is **not** classified as `ei:concept/topic`. This is correct OWA: presence in the aggregator is an explicit assertion, not a default.
- For OEO IRIs, the architect emits `oeo:OEO_xxx skos:inScheme ei:concept/oeo-topic, ei:concept/topic` once at build time. The OEO subset import is unchanged — these are local additions in `oeo-topics.ttl`.
- Granularity contract (CQ-T3) is enforced at the SHACL layer: every value of `ei:narrativeAboutTopic` must resolve to `owl:Class` (OEO IRI under punning) or `skos:Concept` (supplement IRI). Members of `ei:concept/topic` automatically satisfy one of these.

---

## 5. ArgumentPattern SKOS scheme

```
ei:concept/argument-pattern (skos:ConceptScheme)
  ├── apat:deployment-milestone           (skos:Concept)
  ├── apat:emergent-technology-bulletin   (skos:Concept)
  ├── apat:geographic-energy-project      (skos:Concept)
  ├── apat:grid-snapshot                  (skos:Concept)
  ├── apat:learning-curve                 (skos:Concept)
  ├── apat:methodological-critique        (skos:Concept)
  └── apat:structural-economic-analysis   (skos:Concept)
```

Each of the 7 patterns is a `skos:Concept` instance carrying:
- `skos:prefLabel` (the canonical English label, derived from each pattern's `title:` frontmatter in `/skygest-editorial/references/argument-patterns/{stem}.md`)
- `skos:definition` (the `description:` frontmatter)
- `skos:altLabel` (the `variants:` list — the 4 deployment-milestone variants etc. become altLabels)
- `skos:editorialNote` carrying the `editorial_value:` frontmatter and `status: active|draft|deprecated`
- `skos:related` for non-empty `related_patterns:` frontmatter (currently empty for all 7)
- `skos:inScheme ei:concept/argument-pattern`

Pattern lifecycle:
- `status: active` → no special handling
- `status: draft` → `skos:editorialNote "draft"@en`; reasoner classifies as Concept normally
- `status: deprecated` → `skos:editorialNote "deprecated"@en` + `owl:deprecated true`; reasoner still classifies but downstream consumers SHOULD filter

This matches V0+V1 patterns exactly — same shape as `concept-schemes/aggregation-type.ttl` and `concept-schemes/temporal-resolution.ttl`. Source plan §S4 confirms the multi-agent design review ratified this approach over the original `owl:Class` + ABoxed individuals design.

---

## 6. NarrativeRole SKOS scheme

```
ei:concept/narrative-role (skos:ConceptScheme)
  ├── nrole:lead         (skos:Concept) — the post the Narrative is built around
  ├── nrole:supporting   (skos:Concept) — reinforces the narrative's argument
  ├── nrole:counter      (skos:Concept) — represents an opposing or alternative view
  └── nrole:context      (skos:Concept) — provides background
```

Each instance carries `skos:prefLabel`, `skos:definition`, `skos:inScheme`. No `skos:altLabel`, no lifecycle annotations (the 4 roles are stable). Source plan §3.3 ratifies the closed enumeration.

The `ei:memberRole` property is constrained at the SHACL layer (not OWL) to require values from this scheme. See [property-design-v2.md § 3](property-design-v2.md) for the V2-CQ-Q-4 decision rationale.

---

## 7. NarrativePostMembership identity rule — V2-CQ-Q-3 decision

**Question:** What is the deterministic hash function for the NarrativePostMembership IRI?

### Decision: **sha256 truncated to 16 hex characters of `(narrativeIri || "\n" || postUri)`.**

```
NarrativePostMembership IRI =
  https://w3id.org/energy-intel/narrative/{story-stem}/membership/{hash16}

hash16 = lowercase hex( sha256(narrativeIri || "\n" || postUri) )[0:16]
```

Where:
- `narrativeIri` is the canonical Narrative IRI (`https://w3id.org/energy-intel/narrative/{story-stem}`)
- `postUri` is the post identifier (e.g., `https://id.skygest.io/post/x-1886502618-status-2039766305071378920`)
- `||` is byte concatenation
- `\n` (LF) is the separator (matches Linear D3 convention for compound identity)
- The full sha256 digest is hex-encoded; the first 16 hex chars (= 8 bytes = 64 bits) are taken

### Rationale

1. **Determinism.** Same `(narrativeIri, postUri)` always yields the same membership IRI. Re-importing the same editorial graph produces zero new entities (UC-013 idempotency).
2. **Collision resistance.** 64 bits = 2^64 possible IRIs. At Narrative-corpus scale (estimated < 10^5 narratives × < 10^3 posts/narrative = < 10^8 total memberships), collision probability under birthday paradox is < 10^-3. Detailed in [narrative-identity-rule.md](narrative-identity-rule.md).
3. **Roundtrip-friendly.** The hash is deterministic and the algorithm is simple enough to implement identically in Python (rdflib pre-import), TypeScript (cloudflare worker), and any other consumer.
4. **Length-balanced.** 16 hex chars is short enough to keep IRIs readable (`.../membership/a3f9c2e8b14d567f`) but long enough that collisions are vanishingly rare.
5. **Separator.** `\n` (LF) prevents pathological cases where a postUri prefix could collide with a longer postUri. Concatenating without a separator would mean `("foo", "barbaz") == ("foobar", "baz")` — the LF separator forces a clean delimiter.

### Why not alternatives

| Alternative | Rejected because |
|---|---|
| sha256 truncated to 8 chars | 32 bits — collision probability ~ 1% at 10^5 memberships, unacceptable |
| sha256 truncated to 32 chars | longer than necessary; readability trade-off |
| base32 encoding | shorter but introduces case sensitivity issues in some URI parsers |
| ULID | ULIDs encode timestamps, breaking determinism on re-import |
| sequential integer | requires runtime counter; not derivable from `(narrativeIri, postUri)` alone |
| UUIDv5 | would work, but sha256 truncation is simpler and equivalent for our use case |

Full identity rule + collision analysis: see [narrative-identity-rule.md](narrative-identity-rule.md).

---

## 8. ei:memberRole range constraint — V2-CQ-Q-4 decision

**Question:** Range constraint of `ei:memberRole` — SHACL-only or `owl:allValuesFrom` too?

### Decision: **SHACL-only.**

OWL-level: `ei:memberRole rdfs:range skos:Concept` (broad).

SHACL-level: `ei:memberRole` value MUST be in `ei:concept/narrative-role` scheme:

```turtle
ei:NarrativePostMembershipShape
  sh:targetClass ei:NarrativePostMembership ;
  sh:property [
    sh:path ei:memberRole ;
    sh:in ( <https://w3id.org/energy-intel/concept/narrative-role/lead>
            <https://w3id.org/energy-intel/concept/narrative-role/supporting>
            <https://w3id.org/energy-intel/concept/narrative-role/counter>
            <https://w3id.org/energy-intel/concept/narrative-role/context> ) ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
  ] .
```

### Rationale

1. **OWA fit.** `owl:allValuesFrom` over an enumeration class would force closure: any `ei:memberRole` value not declared in the closed enumeration would either trigger an OWL inconsistency or get classified as a member of the enumeration. Both are wrong for a SKOS scheme that may grow over time.
2. **Convention from V0+V1.** `ei:narrativeAppliesPattern` (V2) and `ei:aboutTechnology` (V0/V1) both keep their OWL ranges broad (skos:Concept) and use SHACL for scheme membership. V2-Q-4 follows this established pattern.
3. **SHACL is closed-world.** SHACL validation runs over a known graph snapshot; `sh:in` enumeration is a clean closed-world check. This is the right tool for "value MUST be in this enumeration."
4. **Functional + sh:maxCount 1 alignment.** `ei:memberRole` is `owl:FunctionalProperty` at the OWL level (gives reasoner-side fusing) AND `sh:maxCount 1` at the SHACL level (gives validator-side detection of multi-value violations). Defense-in-depth.

### What V2 ships

OWL-level (in `modules/editorial.ttl`):
```turtle
ei:memberRole a owl:ObjectProperty, owl:FunctionalProperty ;
  rdfs:domain ei:NarrativePostMembership ;
  rdfs:range  skos:Concept ;
  rdfs:label "member role"@en ;
  skos:definition "Functional role qualifier of a NarrativePostMembership.
    Constrained at the SHACL layer to values in the
    ei:concept/narrative-role scheme."@en .
```

SHACL-level (in `shapes/editorial.ttl`): `sh:in` enumeration as shown above.

---

## 9. Module summary — post-V2

| Module | V2 additions | V2 imports | Layer |
|---|---|---|---|
| `agent` | none | unchanged | problem-specific |
| `media` | none | unchanged | problem-specific |
| `measurement` | none | unchanged | problem-specific |
| `data` | none | unchanged | problem-specific |
| `editorial` (NEW) | 2 classes (Narrative, NarrativePostMembership) + 6 object properties | iao:Document (already imported via measurement parent); foaf:Person (already imported via agent parent); skos (already imported); ei:Post (already imported via media); ei:Expert / foaf:Person (already imported via agent) | problem-specific |

Module count: **5** (was 4 in V0+V1). Architecture layers unchanged.

---

## 10. Coverage sanity check — V2 CQs to commitments

| CQ | Priority | Commitment in this V2 model |
|---|---|---|
| CQ-N1 | must_have | `ei:Narrative` class + deterministic IRI rule (§ 7 + [narrative-identity-rule.md](narrative-identity-rule.md)) |
| CQ-N2 | must_have | `ei:hasNarrativePostMembership` + `ei:memberPost` + `ei:memberRole` (§ 9 + [property-design-v2.md](property-design-v2.md) § 3-5) |
| CQ-N3 | must_have | reverse walk over the same predicates (no new modeling; reasoner does the inverse via SPARQL) |
| CQ-N4 | must_have | `ei:narrativeAboutTopic` + topic SKOS scheme aggregator (§ 4) |
| CQ-N5 | must_have | `ei:narrativeAppliesPattern` + argument-pattern SKOS scheme (§ 5) |
| CQ-N6 | should_have | `ei:narrativeMentionsExpert` + property-path fallback (§ 9) |
| CQ-N7 | must_have | SHACL `ei:NarrativePostMembershipShape` with `sh:qualifiedMaxCount 1` (§ 8 + [property-design-v2.md](property-design-v2.md) § 5) |
| CQ-N8 | should_have | SHACL warning on multi-lead per Narrative (§ 8) |
| CQ-T1 | must_have | SKOS scheme metadata via `skos:prefLabel` etc. (§ 4) |
| CQ-T2 | should_have | `skos:notation` on supplement IRIs (§ 4) |
| CQ-T3 | must_have | SHACL granularity validator on `ei:narrativeAboutTopic` (§ 8) |

V0+V1 CQ revalidation guarantee from [scope-v2.md § V0 + V1 CQ revalidation guarantee](scope-v2.md): **upheld**. The V2 changes are purely additive — V0+V1 classes/properties are unchanged. The retired `concept-schemes/technology-seeds.ttl` is replaced by `concept-schemes/oeo-topics.ttl`, which affects only the value-set of `ei:aboutTechnology` (CQ-013/014/015 walk via property paths). V2 architect rebuilds these CQ fixtures to bind against the new OEO topic subset; the SPARQL itself is unchanged.

---

## 11. Discoveries (for upstream artefacts; record-only)

These are findings during conceptualization that may affect upstream phases. None block conceptualizer handoff.

1. **All 41 OEO seed IRIs verified `owl:Class`.** This session ran a pre-import verification: every candidate from handoff §"OEO topic subset rebuild" parses cleanly in `imports/oeo-full.owl`, types as `owl:Class`, has the expected label, is not deprecated, and is not `owl:NamedIndividual`. Granularity contract (CQ-T3): PASS for the seed list. The architect's `robot extract --method BOT` job operates on a verified-safe seed list.

2. **Label variant on OEO_00010438.** Label is "pumped hydro storage power technology" (not "pumped storage hydro power technology" as written in the handoff). Semantically equivalent; the architect's downstream verification should use the actual OEO label.

3. **Editorial supplement count: 17 stable + 2 conditional.** The 17 always-needed supplements: distributed-energy, grid-and-infrastructure, electrification, energy-efficiency, data-center-demand, energy-policy, energy-markets, energy-finance, energy-geopolitics, critical-minerals, climate-and-emissions, carbon-markets, environment-and-land-use, energy-justice, sectoral-decarbonization, workforce-and-manufacturing, research-and-innovation. The 2 conditional ones (`ei:concept/energy-storage` and `ei:concept/biomass`) ship only if the editorial umbrella's intended scope is broader than OEO_00020366 / OEO_00010258 respectively. **Conceptualizer decision: SHIP BOTH.** Editorial umbrellas at the magazine level need a broader-than-tech-class scope — `energy-storage` covers the markets, policy, and geopolitical aspects (not just battery technology); `biomass` covers materials, conversion processes, and sustainability debates (not just bioenergy). The marginal cost of two extra concepts is < 50 triples; the alternative (forcing editorial to point at OEO_00020366 alone) loses the umbrella semantics. Total supplements: **19**.

4. **`ei:concept/topic` aggregator scheme is V2-only structure.** The aggregator is purely for runtime convenience — it does not exist in OEO and would not benefit from being declared in `oeo-full.owl`. It is a Skygest-side construct, declared only in `modules/concept-schemes/oeo-topics.ttl`.

---

## 12. Decision summary (for architect)

| Decision | Verdict | Lives in |
|---|---|---|
| V2-CQ-Q-1: SKOS scheme split | **(b) split + aggregator**: 3 schemes (`ei:concept/oeo-topic`, `ei:concept/editorial-supplement`, `ei:concept/topic`) | this doc § 4 |
| V2-CQ-Q-2: OEO topic IRI verification | **All 41 candidates pass**; 1 label variant (OEO_00010438) noted; granularity contract holds | this doc § 11 + [topic-vocabulary-mapping.md](topic-vocabulary-mapping.md) |
| V2-CQ-Q-3: NarrativePostMembership IRI derivation | **sha256 of `(narrativeIri || "\n" || postUri)`, hex-encoded, truncated to 16 chars** | this doc § 7 + [narrative-identity-rule.md](narrative-identity-rule.md) |
| V2-CQ-Q-4: ei:memberRole range constraint | **SHACL-only**: OWL range `skos:Concept`; SHACL `sh:in` enumeration over the 4 narrative-role concepts | this doc § 8 + [property-design-v2.md](property-design-v2.md) § 4 |

Architect inherits a concrete, axiom-ready blueprint via [conceptualizer-to-architect-handoff-v2.md](conceptualizer-to-architect-handoff-v2.md).
