# Conceptualizer → Architect Handoff — `energy-intel` V2 (Editorial Extension)

**Authored:** 2026-05-04 by `ontology-conceptualizer` (V2 iteration)
**Predecessor:** [conceptualizer-to-architect-handoff-v1.md](conceptualizer-to-architect-handoff-v1.md) (V1; commit `1d8f9da`)
**Reviewer:** Mepuka Kessy (`kokokessy@gmail.com`)
**Reviewed at:** 2026-05-04
**Source plan:** [`/Users/pooks/Dev/skygest-cloudflare/docs/plans/2026-05-04-editorial-ontology-slice.md`](file:///Users/pooks/Dev/skygest-cloudflare/docs/plans/2026-05-04-editorial-ontology-slice.md)
**Handoff doc:** [`/Users/pooks/Dev/ontology_skill/docs/HANDOFF-2026-05-04-editorial-extension.md`](../../../docs/HANDOFF-2026-05-04-editorial-extension.md)

This document is the architect's V2 contract. Phase 2 is signed; Phase 3 (`/ontology-architect`) inherits a concrete, axiom-ready blueprint.

---

## 1. Inputs to architect

The architect reads these V2 artefacts:

| Artefact | Purpose |
|---|---|
| [`scope-v2.md`](scope-v2.md) | Scope, non-goal #5 retraction, V2 in-scope items |
| [`use-cases-v2.yaml`](use-cases-v2.yaml) | UC-009..UC-014 |
| [`competency-questions-v2.yaml`](competency-questions-v2.yaml) | 11 V2 CQs |
| [`requirements-approval-v2.yaml`](requirements-approval-v2.yaml) | Phase 1 sign-off |
| [`conceptual-model-v2.md`](conceptual-model-v2.md) | Taxonomy, module split decision, 4 V2-Q resolutions |
| [`bfo-alignment-v2.md`](bfo-alignment-v2.md) | BFO leaf decisions; ambiguity register |
| [`property-design-v2.md`](property-design-v2.md) | 6 properties + relation semantics |
| [`narrative-identity-rule.md`](narrative-identity-rule.md) | Deterministic IRI rules (Narrative + Membership + concepts) |
| [`topic-vocabulary-mapping.md`](topic-vocabulary-mapping.md) | 30 umbrellas + 92 leaves resolution table |
| [`oeo-import-rebuild-plan.md`](oeo-import-rebuild-plan.md) | OEO topic subset rebuild spec |
| [`axiom-plan-v2.md`](axiom-plan-v2.md) | A1..A12 numbered axiom obligations + S-V2-1..4 SHACL shapes |
| [`anti-pattern-review-v2.md`](anti-pattern-review-v2.md) | 0 unresolved anti-patterns |

Per [`_shared/iteration-loopbacks.md § 1.1`](../../../.claude/skills/_shared/iteration-loopbacks.md): the architect MUST raise a loopback (not patch silently) if any of these is missing or inconsistent.

---

## 2. Phase 2 sign-off

| Decision | Verdict | Reference |
|---|---|---|
| V2-CQ-Q-1 (SKOS scheme split) | **Split + aggregator** (3 schemes) | [conceptual-model-v2.md § 4](conceptual-model-v2.md) |
| V2-CQ-Q-2 (OEO topic IRI verification) | **All 41/41 candidates pass**; granularity contract holds | [topic-vocabulary-mapping.md § 1.2](topic-vocabulary-mapping.md) |
| V2-CQ-Q-3 (NarrativePostMembership IRI) | **sha256(narrativeIri ‖ "\n" ‖ postUri), truncated to 16 hex chars** | [narrative-identity-rule.md § 2](narrative-identity-rule.md) |
| V2-CQ-Q-4 (memberRole range constraint) | **SHACL-only** (`sh:in` enumeration); OWL range stays broad `skos:Concept` | [property-design-v2.md § 3](property-design-v2.md) |
| V2-A-Q-1 (OEO topic subset DL-clean) | **Mirrors V1 BFO+RO-strip pattern**; empirically expected to remain HermiT-clean | [oeo-import-rebuild-plan.md § 4.3](oeo-import-rebuild-plan.md) |
| Module split | **5th local module: `editorial`** | [conceptual-model-v2.md § 2](conceptual-model-v2.md) |
| Anti-pattern scan | **0 unresolved** | [anti-pattern-review-v2.md](anti-pattern-review-v2.md) |
| BFO ambiguity register | **No score ≥ 2; no Class C reviewer needed** | [bfo-alignment-v2.md § 5](bfo-alignment-v2.md) |
| CQ coverage map | **11/11 V2 CQs covered** (8 must-have + 3 should-have) | [axiom-plan-v2.md § 7](axiom-plan-v2.md) |

---

## 3. Architect deliverables (Phase 3)

Per [HANDOFF-2026-05-04-editorial-extension.md § "Phase 3 — `/ontology-architect`"](../../../docs/HANDOFF-2026-05-04-editorial-extension.md), the architect ships 13 deliverables:

| # | Deliverable | Path | Source axiom obligations |
|---|---|---|---|
| 1 | OEO topic subset (rebuilt) | `imports/oeo-topic-subset.ttl` | [oeo-import-rebuild-plan.md § 4](oeo-import-rebuild-plan.md) |
| 2 | Editorial module | `modules/editorial.ttl` | A1..A12 (axiom-plan-v2.md § 3) |
| 3 | OEO topics SKOS scheme | `modules/concept-schemes/oeo-topics.ttl` | conceptual-model-v2.md § 4 (split + aggregator) |
| 4 | Argument pattern SKOS scheme | `modules/concept-schemes/argument-pattern.ttl` | conceptual-model-v2.md § 5 |
| 5 | Narrative role SKOS scheme | `modules/concept-schemes/narrative-role.ttl` | conceptual-model-v2.md § 6 |
| 6 | Editorial SHACL shapes | `shapes/editorial.ttl` | S-V2-1..S-V2-4 (axiom-plan-v2.md § 4) |
| 7 | V2 CQ tests | `tests/cq-editorial-{N1..N8,T1,T2,granularity}.sparql` | already shipped in Phase 1; architect ensures fixtures land |
| 8 | Granularity validator (alongside #7) | `tests/cq-editorial-granularity.sparql` | shipped in Phase 1 |
| 9 | Build script | `scripts/build-editorial.py` | new in V2 |
| 10 | OEO topic subset extraction script | `scripts/extract-oeo-topic-subset.py` | per oeo-import-rebuild-plan.md § 8 |
| 11 | Justfile updates | `Justfile` | add `build-editorial`, `validate-editorial`, `extract-oeo-topics` recipes |
| 12 | KGCL change log | `release/editorial-v0-changes.kgcl` | conceptualizer notes apply: documents class additions, property additions, scheme additions |
| 13 | Architect build log | `docs/architect-build-log-v2.md` | what was built, what failed, what was deferred |
| 14 | Architect → validator handoff | `docs/architect-to-validator-handoff-v2.md` | hand off to validator |

The validator (Phase 4 in the standard pipeline; not in scope for the cloudflare 12-day plan, where Phase 4 is codegen) will then run the V2 closure under HermiT + ROBOT report + pyshacl + pytest.

---

## 4. Architect-side decisions (left to architect)

Per the conceptualizer-architect responsibility split, the architect decides these:

### 4.1 SHACL-shape file split

Question: should `shapes/editorial.ttl` be one file (all 4 V2 shapes) or four files (one per shape)?

Recommendation: one file. The shapes are tightly coupled (all targeting Narrative + NarrativePostMembership + their predicates). Splitting would create import overhead with no benefit.

### 4.2 Role-property naming on `concept-schemes/narrative-role.ttl`

The 4 narrative-role concept IRIs are documented in [narrative-identity-rule.md § 4](narrative-identity-rule.md): `nrole:lead`, `nrole:supporting`, `nrole:counter`, `nrole:context`. The architect MAY introduce a prefix `nrole:` for `https://w3id.org/energy-intel/concept/narrative-role/` if that helps readability of the SHACL `sh:in` enumeration in `shapes/editorial.ttl`, or use the full IRIs.

### 4.3 OEO `skos:inScheme` location

Question: emit `oeo:OEO_xxx skos:inScheme ei:concept/oeo-topic, ei:concept/topic` in `modules/concept-schemes/oeo-topics.ttl` (Skygest-side ownership), OR in `imports/oeo-topic-subset.ttl` (verbatim subset)?

Recommendation: in `concept-schemes/oeo-topics.ttl`. The subset is upstream-derived and should be re-overwritten on import refresh; the scheme membership is Skygest-side ownership and should not be lost on refresh. See [oeo-import-rebuild-plan.md § 6](oeo-import-rebuild-plan.md).

### 4.4 Wiring `imports/oeo-topic-subset.ttl` into `energy-intel.ttl`

The architect adds a new `owl:imports` declaration at the top-level `energy-intel.ttl`:

```turtle
<https://w3id.org/energy-intel/>
  owl:imports <https://w3id.org/energy-intel/imports/oeo-topic-subset> .
```

And an entry in `catalog-v001.xml` mapping the IRI to the local file (V0/V1 catalog convention).

### 4.5 Whether to retire `modules/concept-schemes/technology-seeds.ttl` outright in V2

Per scope-v2.md § 1, the V1 hand-seeded scheme is retired in favor of `oeo-topics.ttl`. The architect choice:
- **Option a** (clean retire): delete `technology-seeds.ttl`. CQ-013/014/015 rebuild fixtures to bind against new OEO IRIs.
- **Option b** (keep + deprecate): keep the file with an `owl:deprecated true` annotation; don't import it. CQ-013/014/015 fixtures unchanged.

**Recommendation:** Option (a) — clean retire. Per CLAUDE.md `.claude/rules/ontology-safety.md`: "Never delete ontology terms — deprecate with `owl:deprecated true`." But `technology-seeds.ttl` is NOT shipped as terms in the published ontology — it is a local fixture-source for V0/V1 CQ tests. Removing the file is fine; the architect rebuilds the V0/V1 fixtures (cq-013.ttl, cq-014.ttl, cq-015.ttl) to bind against the new OEO IRIs.

If concerned about the safety rule, the architect can keep `technology-seeds.ttl` in place but stop importing it (option b). Architect decides based on whether file deletion vs. unused-file conflicts with the team's preference.

---

## 5. Acceptance criteria (Gate A from source plan §7)

The architect's Phase 3 work is complete when:

1. ✅ `just build-editorial` runs the full pipeline cleanly: ROBOT merge → reason (HermiT) → report → pyshacl → pytest. Zero unsatisfiable classes; zero ROBOT report ERRORs (or all ERRORs upstream-allowlisted); zero pyshacl violations on the V2 fixtures; 11/11 V2 CQ tests pass.

2. ✅ Every accepted OEO IRI in `concept-schemes/oeo-topics.ttl` resolves to its intended `rdfs:label` in `imports/oeo-full.owl`. Verified by `extract-oeo-topic-subset.py` script.

3. ✅ Rebuilt `imports/oeo-topic-subset.ttl` contains every accepted runtime term (41 IRIs verified).

4. ✅ V0+V1 CQ revalidation: 14/14 V0 CQs PASS + 5/5 V1 CQs PASS + 11/11 V2 CQs PASS = 30/30 total.

5. ✅ Validator gate green; release-audit signed by curator.

6. ✅ `skygest-cloudflare/packages/ontology-store/` drift gate test (when run after the next codegen pass) recognises the new TTL modules without metadata-key drift. *(This is a cloudflare-side concern run after Phase 4 codegen; the architect just needs to ensure TTL modules follow the expected shape.)*

---

## 6. Cross-repo open questions (informational)

These are flagged in [requirements-approval-v2.yaml § cross_repo_open_questions](requirements-approval-v2.yaml). The architect does NOT resolve them; they are flagged for cloudflare-side or future-iteration attention.

| ID | Question | Status |
|---|---|---|
| V2-X-Q-1 | Signal preservation under umbrella collapse — does cloudflare consumer need the original 92 leaf concepts? | Mitigated ontology-side: every leaf slug carries `skos:notation` annotation on its canonical IRI. Cloudflare side decides whether to use it. |
| V2-X-Q-2 | Should `attach_post_to_narrative` accept multiple posts per call? | Ontology stays neutral. `ei:hasNarrativePostMembership` cardinality is `many`; order not preserved. |
| V2-X-Q-3 | After Pattern A migration window, drop legacy topic_slug column or retain? | Mitigated ontology-side: `skos:notation` annotations make the migration map queryable from the ontology. Cloudflare decides drop date. |

---

## 7. What the architect must NOT do

These are explicit prohibitions per the conceptualizer's design decisions:

1. **NOT** mint a `ei:Arc` class. Arcs are filesystem-only per source plan §S2; an `ei:Arc` class would break the locked decision.

2. **NOT** mint role-named predicates (`ei:leadPost`, `ei:supportingPost`, etc.). Use the reified `ei:NarrativePostMembership` class with `ei:memberRole` qualifier per [conceptual-model-v2.md § 2.2](conceptual-model-v2.md). This is the System Blueprint anti-pattern guard.

3. **NOT** type OEO IRIs as `iao:ICE` or `iao:Document` instances. OEO IRIs stay as `owl:Class` declarations from the OEO subset import; SKOS scheme membership is the only Skygest-side typing. Per [bfo-alignment-v2.md § 4](bfo-alignment-v2.md).

4. **NOT** mint OEO IRIs into the `ei:concept/` namespace. OEO IRIs stay in their native namespace per V2-CQ-Q-1 (split + aggregator).

5. **NOT** declare `owl:allValuesFrom` over a closed enumeration on `ei:memberRole`, `ei:narrativeAppliesPattern`, or `ei:narrativeAboutTopic`. Per V2-CQ-Q-4 + property-design-v2.md § 3,5,6: SHACL-only enumeration.

6. **NOT** delete or rename `ei:Expert` (V0/V1 class). V2 does not touch the agent module.

7. **NOT** add an OWL axiom that "permits duplicate stems with arc disambiguation." The deterministic IRI rule is enforced by the import pipeline, not by the ontology. Per [narrative-identity-rule.md § 1](narrative-identity-rule.md).

8. **NOT** add an alias/redirect axiom for renamed Narratives. V2 ships the immutable-stem rule. V3+ may add aliases.

9. **NOT** use the wrong OEO prefix in V2 SPARQL files. The canonical OEO PURL is `https://openenergyplatform.org/ontology/oeo/` (HTTPS, no hyphen). The V1 anti-pattern review § 8 noted V1 SPARQL had `http://openenergy-platform.org/ontology/oeo/` (HTTP, with hyphen); architect must verify V2 uses the correct form. (Already verified at conceptualizer time: V2 SPARQL files in `tests/cq-editorial-*.sparql` use the correct HTTPS form.)

---

## 8. Architect-side risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| HermiT regresses on V2 closure | low (V1 trace clean; V2 adds no BFO axioms) | Run `robot reason --reasoner hermit` after each module is added; if regression, follow the V1 § 5 fallback (skos:broader materialization, drop punning) |
| Granularity-contract violation (CQ-T3) on rebuilt OEO subset | very low (41/41 verified clean by conceptualizer) | `extract-oeo-topic-subset.py` runs CQ-T3 SPARQL validation as part of build; fails if any violation. |
| Stem collision in test fixture | low (8 nested-layout stems globally unique per F1 audit) | Architect's CQ-N1 fixture binds to a known-unique stem (`2026-04-06-tva-nuclear-costs`); fixture-time stem uniqueness is the cloudflare-side concern post-Phase 7-step-1 archival |
| `oeo-full.owl` lookup vs. import-subset divergence | medium | The conceptualizer verified candidates against `oeo-full.owl`; the architect re-verifies against the rebuilt `imports/oeo-topic-subset.ttl` post-extract |
| ROBOT report ERRORs on the new module | medium | Architect's build script allow-lists known upstream OEO ERRORs (mirrors V1 build); investigates any new V2 ERRORs |

---

## 9. Sign-off

| Field | Value |
|---|---|
| Conceptualizer reviewer | `kokokessy@gmail.com` |
| Reviewed at | 2026-05-04 |
| Phase 2 status | **signed** |
| Hand-off to | `/ontology-architect` (Phase 3) |
| CQ freeze commit | `1d8f9da` (Phase 1 baseline; Phase 2 docs not yet committed at this writing) |
| Architect can proceed | **YES** — all 4 V2-Q questions answered, all 11 V2 CQs covered, anti-pattern scan clean, BFO ambiguity register clean. |
