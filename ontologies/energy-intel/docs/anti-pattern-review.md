# Anti-Pattern Review — `energy-intel`

**Reviewer:** Mepuka Kessy (`kokokessy@gmail.com`) — self-reviewer (single-stakeholder phase)
**Reviewed at:** 2026-04-22
**Conceptual-model commit:** (this change-set; pre-architect)
**Catalogue:** [`_shared/anti-patterns.md`](../../../.claude/skills/_shared/anti-patterns.md) — 16 patterns.

Severity legend: `info` = note only; `warn` = address before architect finalises axioms; `block` = must resolve before architect starts.

---

## Per-pattern results

| # | Pattern | Detection mode | Finding | Severity | Resolution |
|---|---|---|---|---|---|
| 1 | Singleton hierarchy | taxonomy scan (taxonomy.md § 1-4) | **Variable has no subclasses in V0** (thin class by design). **Series has no subclasses**. **Observation has no subclasses**. **Conversation has two (SocialThread, PodcastEpisode) — OK.** | `info` | Documented. Seven-facet Variable deferred to V1 (scope § Variable seven-facet deferral). Thin classes are intentional; they are *leaves*, not singleton intermediates. Mitigated by the four classes being siblings of CMC under `iao:ICE` (disjoint siblings, not lonely). `ClaimTemporalWindow` is the fifth measurement-module class; as of 2026-04-22 it's a `bfo:TemporalRegion`, disjoint-by-BFO-category from the other four. |
| 2 | Role-type confusion | manual review — naming scan | **Expert is modelled as a class** (`foaf:Person` subclass) rather than a `bfo:Role` borne by a Person. This is the role-type anti-pattern in principle. | `info` | **Product owner ratified** this simplification (scope § Decisions F1; bfo-alignment.md § 5). Known trade-off: V0 collapses EnergyExpertRole into the class `ei:Expert`. Mitigated by: (a) no V0 CQ depends on role-transience; (b) V1 gets proper `EnergyExpertRole` on Person if editorial-role discourse-type ("analyst vs journalist") is needed. Recorded; move on. |
| 2 (cont) | Role-type confusion — Publisher/DataProvider | manual review | `ei:PublisherRole` and `ei:DataProviderRole` **correctly** modelled as `bfo:Role`, NOT as subclasses of `ei:Organization`. | `info` | Good. Confirms scout ODP F.2 (odp-recommendations.md) was applied. No fix needed. |
| 3 | Process-object confusion | manual review — BFO scan | **CMC was a candidate for being modelled as a Process** (see bfo-alignment.md § 3.1 ambiguity register — ambiguity score 2). Product owner reviewed and chose ICE. | `info` | Documented in bfo-alignment.md § 3.1 with reviewer signature. The "act of asserting" (Process) is captured in the ABox via `prov:wasGeneratedBy → prov:Activity`, not as a TBox class. |
| 4 | Missing disjointness | taxonomy scan (taxonomy.md §§ 1, 2, 3) | Disjointness obligations enumerated for every sibling group: measurement (CMC/Obs/Var/Series/Window pairwise), media (Chart/Screenshot/Excerpt/Image; Post/MediaAttachment/PodcastSegment; SocialThread/PodcastEpisode), agent (PublisherRole/DataProviderRole; Expert/Organization). | `warn` → resolved | Architect must write each `DisjointClasses` / `owl:disjointWith` axiom per the taxonomy.md § sibling-disjointness-obligations lists. Axiom-plan.md § "Foundational axioms" records all of them. Downgraded to `info` on implementation. |
| 5 | Circular definition | axiom-plan scan | `ei:references` super-property references `ei:references*` subproperties; no `owl:EquivalentProperty` cycles. No class has an EquivalentTo-with-circular expansion. | `info` | No circularity. |
| 6 | Quality-as-class | taxonomy scan | `ei:TemporalResolution` is hand-seeded as a SKOS ConceptScheme (value-partition ODP F.1), NOT as an OWL class hierarchy. | `info` | Correct — this is exactly the pattern the anti-pattern flags as the *fix*. |
| 7 | Information-physical conflation | taxonomy scan | **Charts, Screenshots, Images are modelled as ICEs (`iao:Image`)**, not as physical PNG-on-disk bearers. A chart-as-a-PNG-file is NOT modelled in V0. | `info` — confirmed correct omission | Product owner confirmed: physical-file bearers are explicitly out-of-scope (scope § Non-goal #1 "chart rendering / pixel geometry / image processing"). If V-future needs file-on-disk semantics, architect adds a `ei:ImageFile` class under `bfo:Object` that `concretizes` an `ei:Image` — this is the canonical IAO Information-Realization triangle. Not in V0. |
| 8 | Orphan class | orphan scan (taxonomy.md § 6) | Every local class has a named parent (agent module: foaf or bfo roots; media: iao roots; measurement: iao:ICE). `ei:EvidenceSource` has `iao:ICE` parent. | `info` | No orphans. |
| 9 | Polysemy / overloaded term | naming review | ~~**`ei:Image` (local) vs `iao:Image`**~~ **Resolved 2026-04-22:** local class renamed to `ei:GenericImageAttachment` per product-owner directive. No short-name collision remains. **`dcat:DatasetSeries` vs `ei:Series`** is also flagged in conceptual-model § 10; kept distinct by design, not polysemous. | `info` — resolved | Renamed + documented. |
| 10 | Domain/range overcommitment | property-design scan | **`ei:evidences` was at risk** — the CQ-stated union domain `(Post ∪ MediaAttachment ∪ PodcastSegment)` would classify any subject-of-evidences into that union and potentially propagate wrong types. **Resolved** by introducing the named abstract class `ei:EvidenceSource` with explicit subclass assertions. | `warn` → resolved | See property-design.md § 6 and conceptual-model § 8.1. Named domain cleaner than union. **Other properties checked:** `ei:authoredBy` domain = `ei:Post`, range = `ei:Expert`, both reasonable (not over-narrow). `ei:references*` family domains = `ei:CanonicalMeasurementClaim` (specific leaf) — **the domain is the intended type; this is NOT overcommitment** because every subject of `ei:referencesVariable` must be a CMC. SHACL-side validation (see shacl-vs-owl.md S-6) handles range referential integrity. |
| 11 | Individuals in T-box | taxonomy / axiom-plan scan | No V0 TBox individuals. `ei:TemporalResolution` SKOS concepts ARE individuals by SKOS design — they live in `modules/concept-schemes/temporal-resolution.ttl` (a separate file), which is the correct TBox/ABox seam for SKOS schemes. | `info` | No TBox pollution. |
| 12 | Negative universals / complement overuse | axiom-plan scan | No `owl:complementOf` axioms in the plan. Disjointness expressed positively via `DisjointClasses`. | `info` | No issue. |
| 13 | False is-a from OO inheritance | naming + OO-origin review | Class names are domain-sourced (CanonicalMeasurementClaim, PodcastSegment, Expert), NOT implementation-flavoured (*Manager, *Service, *Controller). | `info` | No issue. |
| 14 | System blueprint instead of domain | naming review | No `*TableRow`, `*Payload`, `*DTO` classes. The ontology models the discourse domain (posts, claims, experts), not the runtime plumbing (Cloudflare Workers, D1 tables) — per Linear Architecture Principle 4 (scope § Non-goal #8). | `info` | No issue. |
| 15 | Technical perspective over domain | review | Every class traces to a CQ (traceability-matrix.csv) or a scope-ratified design decision. Variable/Series kept thin because *the domain says so* (Linear D2 deferral), not because of storage convenience. | `info` | No issue. |
| 16 | Mixing individuals with classes | punning review | **OWL 2 punning is enabled workspace-wide** (scope § Reasoning). `ei:aboutTechnology` will admit OEO class IRIs as `skos:Concept` individuals via punning (phase 2). This is *intentional*, not a mix-up. | `info` → watch | Architect must verify HermiT accepts the punned graph when OEO subset is imported. If punning breaks reasoning in practice, the fallback is to extract OEO technology classes as plain `skos:Concept` individuals (not punned). Tracked for architect. |

---

## Closure / OWA considerations

Two CQs carry closure obligations addressed via OWL cardinality:

- **CQ-009 (CMC evidence invariant)** — `min 1` on inverse `ei:evidences` to `ei:EvidenceSource`. Closure encoded in the SubClassOf restriction. SHACL companion shape (shacl-vs-owl.md § 3.3) covers runtime validation.
- **CQ-002 (Post has exactly 1 Expert)** — `exactly 1` closure. Same treatment.

Neither CQ is an OWA-trap: we *want* the reasoner to enforce these invariants, and we accept that an incomplete ABox snapshot will simply not have the triple (not that the absence is allowed forever).

No CQ returns "empty because missing-not-false" — escalation back to requirements is unnecessary.

---

## Open items

- **Pattern #9 rename** — resolved 2026-04-22. Local class is now `ei:GenericImageAttachment`. No further architect action.
- **Pattern #16 punning** — watch on OEO import. If HermiT misbehaves, fall back to plain SKOS individuals (re-materialise OEO class hierarchy as `skos:broader` chain in the MIREOT extract). Tracked for architect.

No `warn` or `block` items remain unresolved. All flagged concerns either have a ratified resolution or are downgraded to `info` after the conceptual-model design.

---

## Severity summary

| Severity | Count |
|---|---|
| `block` | 0 |
| `warn` (unresolved) | 0 |
| `warn` → resolved by design | 2 (patterns #4, #10) |
| `info` | 14 |

Clean slate for the architect.
