# Conceptualizer → Architect Handoff — `energy-intel`, V1

**From:** `ontology-conceptualizer` (V1 iteration; 2026-04-27)
**To:** `ontology-architect` (V1 iteration)
**Predecessor handoff:** [conceptualizer-to-architect-handoff.md](conceptualizer-to-architect-handoff.md) (V0)
**Inputs conceptualizer consumed:**
- Requirements V1 @ `36d1952`: [scope-v1.md](scope-v1.md), [competency-questions-v1.yaml](competency-questions-v1.yaml), [requirements-approval-v1.yaml](requirements-approval-v1.yaml).
- Scout V1: [reuse-report-v1.md](reuse-report-v1.md), [imports-manifest-v1.yaml](../imports-manifest-v1.yaml), [scout-to-conceptualizer-handoff-v1.md](scout-to-conceptualizer-handoff-v1.md).
- Reasoner trace: [`validation/v1-bfo-remediation/v1-hermit-reason.log`](../validation/v1-bfo-remediation/v1-hermit-reason.log) (HermiT exit=0).

**Conceptualizer V1 deliverables landed:**
- [conceptual-model-v1.md](conceptual-model-v1.md) — V1 delta covering CQ-Q-1/CQ-Q-2/CQ-Q-3 decisions.
- [property-design-v1.md](property-design-v1.md) — `ei:canonicalUnit` + range widenings.
- [bfo-alignment-v1.md](bfo-alignment-v1.md) — `ei:EnergyExpertRole` placement; `ei:Expert` redefinition.
- [anti-pattern-review-v1.md](anti-pattern-review-v1.md) — closes V0 § 2 + § 16 watches; adds disjointness obligation.
- [shacl-vs-owl-v1.md](shacl-vs-owl-v1.md) — six new OWL constraints; five new SHACL shapes.
- (No new `taxonomy-v1.md` — V1 taxonomy delta is folded into [conceptual-model-v1.md § 3, § 4, § 6](conceptual-model-v1.md). The V1 module/layer assignment is unchanged from V0; the per-module class additions are listed inline.)

---

## 1. Three blocking question decisions (recap)

| ID | Question | Decision | Where |
|---|---|---|---|
| **CQ-Q-1** | `ei:Expert` fate | **(b) keep as defined equivalent class.** `ei:Expert ≡ foaf:Person ⊓ (bfo:0000053 some ei:EnergyExpertRole)`. Drop V0 SubClassOf, keep `disjointWith ei:Organization`. | conceptual-model-v1.md § 2 |
| **CQ-Q-2** | `ei:canonicalUnit` form | Range = `qudt:Unit`; cardinality 0..1 (Functional); name `ei:canonicalUnit`; **no local `ei:hasQuantityKind`** (CQ-017 reuses imported `qudt:hasQuantityKind` on Unit). | property-design-v1.md § 1, § 2 |
| **CQ-Q-3** | Punning regression | **HermiT stays clean** at TBox stage; empirically verified by scout's V1 trace. Fallback (re-materialise OEO as plain SKOS individuals) documented but not needed. ABox stage remains a watch for V2. | conceptual-model-v1.md § 5; anti-pattern-review-v1.md § 2 |

---

## 2. Numbered V1 axiom plan (architect inherits)

The architect implements these axioms in `modules/agent.ttl`, `modules/measurement.ttl`, `modules/media.ttl`, plus the top-level `energy-intel.ttl` import wiring. Each axiom is anchored to a CQ or a defense-in-depth obligation. Manchester-syntax sketches; architect translates to ROBOT/rdflib/Turtle.

### A1. Mint `ei:EnergyExpertRole` class
- Module: `modules/agent.ttl`
- CQ source: CQ-018, CQ-019
- Source: bfo-alignment-v1.md § 1
```
ei:EnergyExpertRole a owl:Class ;
  rdfs:label "energy expert role"@en ;
  rdfs:subClassOf bfo:0000023 ;
  rdfs:subClassOf [ a owl:Restriction ;
                    owl:onProperty bfo:0000052 ;
                    owl:someValuesFrom foaf:Person ] ;
  skos:definition
    "A BFO role inhering in a foaf:Person who publishes energy-domain
    claims (on social media, podcasts, or articles) that an editorial
    pipeline extracts as CanonicalMeasurementClaims."@en .
```
Mirrors V0 PublisherRole shape. Keep `ei:EnergyExpertRole` primitive (no EquivalentTo).

### A2. Redefine `ei:Expert` as defined equivalent class
- Module: `modules/agent.ttl`
- CQ source: CQ-018; V0 CQ-002/007/008/011 revalidation
- Source: conceptual-model-v1.md § 2; bfo-alignment-v1.md § 2
```
ei:Expert owl:equivalentClass
  [ a owl:Class ;
    owl:intersectionOf (
      foaf:Person
      [ a owl:Restriction ;
        owl:onProperty bfo:0000053 ;
        owl:someValuesFrom ei:EnergyExpertRole ] ) ] .

ei:Expert owl:disjointWith ei:Organization .                # V0 carry-forward; KEEP
```
**Drop** the V0 `ei:Expert rdfs:subClassOf foaf:Person` assertion (entailed by the EquivalentTo).

### A3. Add three-way role disjointness
- Module: `modules/agent.ttl`
- Source: anti-pattern-review-v1.md § 3 (V1 additive obligation)
```
[ a owl:AllDisjointClasses ;
  owl:members ( ei:EnergyExpertRole ei:PublisherRole ei:DataProviderRole ) ] .
```

### A4. Mint `ei:canonicalUnit` object property
- Module: `modules/measurement.ttl`
- CQ source: CQ-016 (must_have); CQ-017 walks through it
- Source: property-design-v1.md § 1
```
ei:canonicalUnit a owl:ObjectProperty, owl:FunctionalProperty ;
  rdfs:domain ei:CanonicalMeasurementClaim ;
  rdfs:range  qudt:Unit ;
  rdfs:label "canonical unit"@en ;
  skos:definition
    "Links a CanonicalMeasurementClaim to the canonical qudt:Unit IRI
    that the claim's surface-form ei:assertedUnit string resolves to.
    Functional: a CMC has at most one canonical unit."@en .
```

### A5. Add CMC max-cardinality restriction for `ei:canonicalUnit`
- Module: `modules/measurement.ttl`
- CQ source: CQ-016
- Source: property-design-v1.md § 1; shacl-vs-owl-v1.md § 1 O-V1-3
```
ei:CanonicalMeasurementClaim rdfs:subClassOf
  [ a owl:Restriction ;
    owl:onProperty ei:canonicalUnit ;
    owl:maxCardinality 1 ;
    owl:onClass qudt:Unit ] .
```

### A6. Widen `ei:authoredBy` range from `ei:Expert` to `foaf:Person`
- Module: `modules/media.ttl`
- CQ source: CQ-018; V0 CQ-002 revalidation
- Source: property-design-v1.md § 3.1
```
ei:authoredBy rdfs:range foaf:Person .                       # was: ei:Expert
```
**Update** the V0 `ei:Post SubClassOf authoredBy exactly 1 ei:Expert` restriction to `... exactly 1 foaf:Person`.

### A7. Widen `ei:spokenBy` range from `ei:Expert` to `foaf:Person`
- Module: `modules/media.ttl`
- CQ source: CQ-011 V0 carry
- Source: property-design-v1.md § 3.2
```
ei:spokenBy rdfs:range foaf:Person .                         # was: ei:Expert
```

### A8. Wire three new `owl:imports` at top-level
- File: `energy-intel.ttl` (top-level ontology declaration)
- File: `catalog-v001.xml` (catalog mapping)
- Source: scout-to-conceptualizer-handoff-v1.md § Imports the V1 architect inherits
```
<https://w3id.org/energy-intel/> a owl:Ontology ;
  owl:imports
    <https://openenergyplatform.org/ontology/oeo/oeo-technology-subset-fixed> ,    # via catalog
    <https://openenergyplatform.org/ontology/oeo/oeo-carrier-subset-fixed> ,        # via catalog
    <https://qudt.org/2.1/vocab/qudt-units-subset> ;                                # via catalog
  ...
```

Catalog rows (append to `catalog-v001.xml`):
```
<uri name="https://w3id.org/energy-intel/imports/oeo-technology-subset"
     uri="imports/oeo-technology-subset-fixed.ttl"/>
<uri name="https://w3id.org/energy-intel/imports/oeo-carrier-subset"
     uri="imports/oeo-carrier-subset-fixed.ttl"/>
<uri name="https://w3id.org/energy-intel/imports/qudt-units-subset"
     uri="imports/qudt-units-subset.ttl"/>
```

(Architect is free to choose canonical IRI form for the three imports — either re-annotate the subset files via a `robot annotate --ontology-iri ...` step appended to `scripts/build_v1_imports.py` (per scout's note), or use the OEO/QUDT natural IRIs with catalog mapping. Scout default and conceptualizer default: catalog mapping suffices.)

### A9. (No mint) `qudt:hasQuantityKind` reused
- Source: property-design-v1.md § 4
- Action: NONE. Architect uses the imported `qudt:hasQuantityKind` directly in the CQ-017 SPARQL chain. Do NOT mint a local `ei:hasQuantityKind`.

**Total V1 axioms architect implements: 8 axiom additions/modifications (A1–A8).** A9 is a no-op (reuse confirmation).

---

## 3. SHACL shape stubs (architect drafts)

Append to `ontologies/energy-intel/shapes/energy-intel-shapes.ttl` (or create sibling V1 file). Five new shapes per [shacl-vs-owl-v1.md § 2](shacl-vs-owl-v1.md):

| Shape | Path | Severity | Companion to |
|---|---|---|---|
| **S-V1-1** — canonicalUnit value in QUDT subset | `ei:CanonicalMeasurementClaim`, path `ei:canonicalUnit`, `sh:in (...)` | Violation | A4, A5 |
| **S-V1-2** — resolvability gate | `ei:CanonicalMeasurementClaim`, SPARQL `assertedUnit present without canonicalUnit` | Warning | A4 |
| **S-V1-3** — Post author bears EnergyExpertRole | `ei:Post`, path `ei:authoredBy / bfo:0000053`, `sh:class ei:EnergyExpertRole` | Violation | A2, A6 |
| **S-V1-4** — Podcast speaker bears EnergyExpertRole (optional) | `ei:PodcastSegment`, path `ei:spokenBy / bfo:0000053`, `sh:class ei:EnergyExpertRole` | Warning | A2, A7 |
| **S-V1-5** — aboutTechnology in recognized vocab | `ei:CanonicalMeasurementClaim`, path `ei:aboutTechnology`, `sh:or (skos:Concept | OEO subtree)` | Violation | A8 |

Architect tests with `pyshacl --inference rdfs --shapes <shape> --data <fixtures>`.

---

## 4. Fixtures architect must add or migrate

V1 ships TBox-only. Fixture work for the V1 architect phase is the minimum required to revalidate V0 + V1 CQs:

| Fixture | Action |
|---|---|
| Existing V0 fixtures asserting `?p a ei:Expert` | **No migration required.** Under the V1 EquivalentTo, the reasoner classifies the V0 form as Expert via the role-bearer pattern. (V0 fixtures don't currently assert the role-bearer triples; the EquivalentTo means the reasoner does NOT classify them as Expert *unless* role triples are added.) **However**, V0 CQ-002/007/008/011 SPARQL bind `?expert` by `?expert a ei:Expert` — V0 fixtures *do* assert `?p a ei:Expert` directly. Under V1: those direct-class-membership assertions still satisfy the SPARQL pattern (the EquivalentTo means class membership infers role-bearer, but the reverse direction also holds — explicitly asserted class membership still satisfies the class). No migration needed. |
| New V1 fixture for CQ-018 | Add a fixture: `?p a foaf:Person ; bfo:0000053 ?role . ?role a ei:EnergyExpertRole . ?post ei:authoredBy ?p` to validate the role-bearing path. |
| New V1 fixture for CQ-016 | Add: `?cmc a ei:CanonicalMeasurementClaim ; ei:canonicalUnit unit:GigaW` (or another imported unit). |
| New V1 fixture for CQ-017 | Add: `?cmc ei:canonicalUnit ?u . ?u qudt:hasQuantityKind quantitykind:Power` (the QUDT subset already declares `qudt:hasQuantityKind` on imported units; fixture only adds the CMC-side triple). |
| New V1 fixture for CQ-015 | Add: `?cmc ei:aboutTechnology oeo:OEO_xxx` where `oeo:OEO_xxx rdfs:subClassOf* oeo:OEO_00020267`. |
| New V1 fixture for CQ-019 | Compose CQ-018 + CQ-015 fixtures into one Post. |

**Important: correct OEO prefix in fixtures.** The OEO subset uses `https://openenergyplatform.org/ontology/oeo/` (HTTPS, no hyphen). Use this exact form. Conceptualizer's discovery: V1 CQ-015 and CQ-019 SPARQL files have the wrong prefix (HTTP + hyphen, see § 6 below).

---

## 5. Architect's first-pass checklist

In execution order:

- [ ] Read [conceptual-model-v1.md](conceptual-model-v1.md), [property-design-v1.md](property-design-v1.md), [bfo-alignment-v1.md](bfo-alignment-v1.md).
- [ ] Run `robot reason --reasoner hermit` against V0 closure (sanity baseline). Confirm baseline still HermiT-clean.
- [ ] Modify `modules/agent.ttl`:
  - [ ] Add A1 (`ei:EnergyExpertRole`).
  - [ ] Replace V0 `ei:Expert rdfs:subClassOf foaf:Person` with A2 EquivalentTo.
  - [ ] Add A3 three-way disjointness.
- [ ] Run `robot reason` after agent module change. Confirm 0 unsat.
- [ ] Modify `modules/measurement.ttl`:
  - [ ] Add A4 (`ei:canonicalUnit`).
  - [ ] Add A5 CMC max-cardinality restriction.
- [ ] Modify `modules/media.ttl`:
  - [ ] Apply A6 (`ei:authoredBy` range widening + restriction update).
  - [ ] Apply A7 (`ei:spokenBy` range widening).
- [ ] Run `robot reason` after media module change. Confirm 0 unsat.
- [ ] Modify `energy-intel.ttl` (top-level):
  - [ ] Add A8 (`owl:imports` for the three new V1 imports).
- [ ] Update `catalog-v001.xml` with three new mappings.
- [ ] Run `robot merge --catalog ... --input energy-intel.ttl --output v1-merged.ttl`.
- [ ] Run `robot reason --reasoner hermit --input v1-merged.ttl`. **Expected: 0 unsat** (matches scout's V1 trace).
- [ ] Run `robot validate-profile --profile DL`. Expected: V0 punning warnings carry forward; no NEW V1 violations.
- [ ] Append five new SHACL shapes (S-V1-1..S-V1-5) to `shapes/energy-intel-shapes.ttl`.
- [ ] Run `pyshacl` against fresh fixtures.
- [ ] Run `robot report` against the merged closure. Expected: no NEW errors.
- [ ] Build V1 fixtures per § 4.
- [ ] Run validator's L4 pytest. Expected: 14/14 V0 CQs PASS + 5/5 V1 CQs PASS.
- [ ] Address the OEO prefix bug in V1 SPARQL files (see § 6).

---

## 6. Discoveries (action items for architect)

### 6.1 OEO prefix bug in V1 CQ test SPARQL files

Conceptualizer discovered that V1 CQ-015 and CQ-019 SPARQL files use the wrong OEO prefix:

```
PREFIX oeo: <http://openenergy-platform.org/ontology/oeo/>     # WRONG (HTTP + hyphen)
```

The actual OEO PURL and the imported subsets use:

```
@prefix : <https://openenergyplatform.org/ontology/oeo/>        # CORRECT (HTTPS, no hyphen)
```

Files with the bug:
- [`tests/cq-015.sparql`](../tests/cq-015.sparql)
- [`tests/cq-019.sparql`](../tests/cq-019.sparql)

**Action for architect:** before validator's L4 pytest, correct the prefix in both SPARQL files. This is the same bug class as the V0 commit `bf2bb31` "fix(energy-intel): correct OEO namespace (https + no hyphen)" mentioned in the workspace memory. A fresh `sed -i` or rdflib normalisation pass is sufficient.

### 6.2 CQ-017 routes through Unit, not Variable

Documented in [conceptual-model-v1.md § 4](conceptual-model-v1.md) and [property-design-v1.md § 2](property-design-v1.md). The CQ-017 SPARQL uses `?cmc ei:canonicalUnit ?u . ?u qudt:hasQuantityKind ?qk`. **Do not** mint `ei:hasQuantityKind`. The QUDT import already provides `qudt:hasQuantityKind` on every imported unit. This closes manifest open question V1-IM-Q3 in a way the scout did not anticipate.

### 6.3 No restructure of `ei:assertedUnit`

V0 has `ei:assertedUnit xsd:string` on CMC. V1 keeps it. The pair (`ei:assertedUnit` raw token + `ei:canonicalUnit` IRI) implements the surface-form-to-canonical-IRI link. No deprecation of `ei:assertedUnit`.

### 6.4 Watch-item carry-forward to V2 (informational)

The OEO punning prediction is empirically verified at TBox stage (HermiT exit=0 on V1 closure). The ABox stage (V2+) remains a watch — when fixtures assert `?cmc ei:aboutTechnology oeo:OEO_xxx`, validator must re-confirm. See [anti-pattern-review-v1.md § 2](anti-pattern-review-v1.md).

---

## 7. What you do NOT need from conceptualizer

- **OEO IRI verification.** Scout did this; subset files are reasoner-safe. Use them as-is.
- **Full Turtle draft.** This handoff has Manchester-syntax sketches; architect translates.
- **`ei:hasQuantityKind` axiom.** Rejected; do not mint.
- **Variable-side QK link.** Rejected; CQ-017 routes through Unit.

## 8. What you do NOT do (no scope drift)

- Do NOT change V0 module boundaries. V1 keeps the four-module structure.
- Do NOT mint local subroles of `ei:EnergyExpertRole` (Analyst/Journalist/etc.). V2+.
- Do NOT modify `ei:assertedUnit` (V0 datatype property — keep as-is).
- Do NOT add SHACL shapes for V0 backfill items (S-1..S-10) — that's V1.1+ scope.
- Do NOT touch `imports/oeo-{technology,carrier}-subset.ttl` (the V0 unfixed pair). Curator decides on deprecation per V1-IM-Q1.
- Do NOT seed ABox fixtures asserting `oeo:OEO_xxx a iao:ICE` (would re-trigger BFO-leak at ABox stage; only `a skos:Concept` punning is safe).

---

## 9. Loopback paths (if architect hits an issue)

| Issue | Loopback to | Reason |
|---|---|---|
| HermiT reports unsat after wiring V1 imports | `ontology-conceptualizer` | Re-evaluate punning prediction; consider re-materialise OEO as plain SKOS (fallback in conceptual-model-v1.md § 5) |
| Scope drift — architect wants to mint a subrole | `ontology-requirements` | Subroles are V2+; reopen scope is a requirements decision |
| V0 CQ regression (V0 fixture stops passing) | `ontology-conceptualizer` | Likely the EquivalentTo definition needs adjustment |
| QUDT subset insufficient (a unit needed isn't imported) | `ontology-scout` | Curator extends `scripts/build_v1_imports.py:QUDT_UNIT_SEEDS` |
| OEO subset insufficient (a tech class needed isn't imported) | `ontology-scout` | Scout re-runs `scripts/build_v1_imports.py` with extended seed list |
| `imports/upper-axiom-leak-terms.txt` insufficient (new BFO/RO leak surfaces) | `ontology-scout` | Extend strip list |

Depth > 3 escalates per [`_shared/iteration-loopbacks.md`](../../../.claude/skills/_shared/iteration-loopbacks.md).

---

## 10. Confidence note

Everything above is derived from frozen V1 inputs: requirements approval signed `2026-04-27` at `cq_freeze_commit: 36d1952`, scout outputs at `2026-04-27`, conceptualizer V1 deliverables at `2026-04-27`. The empirical reasoner trace at [`validation/v1-bfo-remediation/v1-hermit-reason.log`](../validation/v1-bfo-remediation/v1-hermit-reason.log) provides the evidence basis for the punning prediction.

V1 conceptualizer is unblocked by:
- All three blocking questions answered (CQ-Q-1/2/3).
- All five V1 CQs have an axiom-level commitment.
- All V0 CQs have a revalidation path (zero migration cost via the EquivalentTo definition).
- Anti-pattern footprint reviewed; § 2 and § 16 V0 watches are closed.
- SHACL companion shapes drafted for defense-in-depth.

Architect can proceed.
