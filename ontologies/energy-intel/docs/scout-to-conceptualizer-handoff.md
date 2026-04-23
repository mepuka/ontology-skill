# Scout → Conceptualizer Handoff — `energy-intel`

**From:** `ontology-scout` (2026-04-22)
**To:** `ontology-conceptualizer`
**Inputs scout consumed:** `scope.md` @ f6d025d, `pre-glossary.csv` @ f6d025d,
`competency-questions.yaml` @ f6d025d, `requirements-approval.yaml` @ f6d025d.
**Scout deliverables landed:** `docs/reuse-report.md`, `imports-manifest.yaml`,
`docs/odp-recommendations.md`, this file.

Five crisp bullets for the conceptualizer to action before architect starts:

1. **Re-parent Chart / Screenshot / Excerpt under `iao:Image` (or `iao:TextualEntity`),
   not `iao:Document`.** scope.md § Decisions resolved / BFO upper alignment
   routes `Chart`, `Screenshot`, `Excerpt` under `iao:Document`, but IAO defines
   Document as *a collection* of ICEs. Scout's recommended mapping (reuse-report
   § B.2): `Chart / Screenshot / Image → iao:Image (IAO_0000101)`, `Excerpt →
   iao:InformationContentEntity (IAO_0000030)` or `iao:TextualEntity (IAO_0000300)`
   if that class survives in v2026-03-30, `Post / PodcastEpisode → iao:Document
   (IAO_0000310)`, `PodcastSegment → iao:InformationContentEntity`. Conceptualizer
   confirms or overrides; loopback `missing_reuse` if overridden.

2. **Adopt the three core ODPs explicitly in the axiom plan:** F.3
   **Information realization** (CMC ↔ evidences ↔ references), F.2 **Role**
   (PublisherRole + DataProviderRole on Organization), F.4 **Participation**
   (authoredBy + spokenBy, binary-shortcut form for V0). F.1 **Value partition**
   is additionally required for the hand-seeded `ei:TemporalResolution` scheme
   (OEO has no temporal-resolution branch — reuse-report § A.4). F.5
   **Part-whole** covers PodcastSegment `partOf` PodcastEpisode. Full ODP
   details — including variable bindings and axiom-pattern rows — in
   `docs/odp-recommendations.md`.

3. **OWL 2 punning strategy for OEO technology values:** scope.md § Reasoning
   already enables punning workspace-wide. Conceptualizer must record the
   punning commitment in `docs/conceptual-model.yaml` (Step "Axiom plan")
   because `ei:aboutTechnology`'s range is `skos:Concept` in V0 but widens
   to OEO technology **classes-as-individuals** in a later phase. The V0
   SPARQL path `(skos:broader | rdfs:subClassOf)*` on CQ-013 / CQ-014
   already accommodates both views, but the punning constraint affects
   architect's `rdfs:range` choice — defer to keeping range `skos:Concept`
   and relying on punning to admit OEO class IRIs as values.

4. **PROV/FOAF Agent alignment is a bridge, not an import.** scope.md § Open
   q #3 asked whether `dcat:Agent` / `foaf:Agent` / `prov:Agent` should be
   `owl:equivalentClass`. Scout's answer (reuse-report § C): `dcat:Agent`
   is not a published class; the only alignment needed is
   `prov:Agent owl:equivalentClass foaf:Agent` in a standalone bridge file
   at `mappings/prov-foaf-bridge.ttl`. `ei:Organization` does not need a
   direct `rdfs:subClassOf foaf:Agent` — FOAF already asserts
   `foaf:Organization rdfs:subClassOf foaf:Agent` so the chain closes.
   Conceptualizer confirms this shape; mapper authors the bridge file in
   Pipeline B. Run Step 3.5 bridge-safety gate (merge + reason + check for
   unsatisfiables) before publishing.

5. **OEO MIREOT seed list is PROVISIONAL until architect verifies against
   v2.11.0.** scope.md § Open q #1 named `OEO_00000030` as the candidate
   energy-technology root; that IRI actually labels "oil power unit"
   (reuse-report § G, § A). Scout's revised candidates (both to be verified
   on the live v2.11.0 file before `robot extract` runs):
   - Energy-technology root: `OEO_00000011` (energy converting component) OR
     `OEO_00010385` (energy transformation function).
   - Energy-carrier root: `OEO_00020039` (energy carrier).
   - Aggregation-type root: `OEO_00140068` (aggregation type).
   - Temporal-resolution: **hand-seed** a five-value SKOS scheme in `ei:`
     namespace (no OEO equivalent); `odp-recommendations.md` F.1 for
     instantiation.
   - Quantity-kind: **do not** MIREOT from OEO (OEO_00000350 is a value,
     not a kind); use `qudt:QuantityKind` from the QUDT units MIREOT
     (V1; V0 is units-only).

   Conceptualizer decides the final seed list (may request additional
   subtrees) and hands to architect. Architect runs `robot query` on
   v2.11.0 to confirm every seed IRI still exists and still has the
   expected label; extraction runs only after verification.

---

## Things that stay as scope.md committed them (no conceptualizer action)

- CMC → `iao:InformationContentEntity` (correct)
- Observation → `iao:InformationContentEntity` (correct)
- Variable / Series / Conversation / PodcastSegment → `iao:InformationContentEntity` (correct)
- Expert → `foaf:Person` subclass (correct)
- Organization → dual parent `foaf:Organization` + `bfo:ObjectAggregate` (BFO 2020, correct)
- PublisherRole / DataProviderRole → `bfo:Role` (correct)
- CMC `owl:disjointWith` Observation (correct)
- V0 Variable is thin (seven-facet deferred) (correct)
- Resolution-state enum dropped (correct; derivable)
- Source-modality enum dropped (correct; derivable from `ei:evidences` range)

## Things conceptualizer may want to revisit (non-blocking)

- **Scope.md non-goal #6** ("Runtime RDF / SPARQL / SHACL execution in the
  Worker") interacts with SHACL design: conceptualizer draws SHACL from
  property-design intent (per skill description), which the architect then
  authors in `ontologies/energy-intel/shapes/`. Non-goal #6 does NOT preclude
  SHACL; it says SHACL does not execute *in the Worker*. Build-time SHACL is
  still in-scope.
- **Scope.md non-goal #5** ("Narrative / Story / ArgumentPattern / Edition")
  — conceptualizer can confirm V0 does not need any aggregation class over
  CMCs. V0 `ei:evidences` + `ei:references*` are sufficient.

---

## Loopback triggers raised

- None — scout findings are all compatible with scope.md freezes. The five
  bullets above are *recommended refinements*; if conceptualizer agrees,
  the downstream chain proceeds. If conceptualizer disagrees on any bullet,
  scout re-routes to:
  - Bullet 1 (IAO re-parenting) → `missing_reuse` to conceptualizer;
    re-scout if conceptualizer proposes a non-IAO parent.
  - Bullet 5 (OEO seeds) → `bad_module` from architect if the seed verification
    finds labels don't match or roots are obsolete; scout re-investigates.
- Loopback-to-requirements: five gaps are noted in `reuse-report.md § Gaps for
  requirements loopback`. They are non-blocking for the conceptualizer pass;
  next `ontology-requirements` refresh should fold them in.
