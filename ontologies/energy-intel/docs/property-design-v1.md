# Property Design — `energy-intel`, V1 Delta

**Authored:** 2026-04-27 by `ontology-conceptualizer` (V1 iteration)
**Predecessor:** [property-design.md](property-design.md) (V0; commit `36d1952`)
**Consumer:** `ontology-architect` (authors OWL axioms and SHACL shapes from this spec).

`intent:` values: `infer` (use OWL domain/range for inference), `validate` (SHACL constraint), `restrict` (per-class OWL restriction), `annotate` (annotation property, no constraint).

This document is a **delta** to V0 property-design.md. Only V1 additions and modifications are listed. V0 properties not restated here are unchanged.

---

## 0. Scope of V1 property changes

| Change kind | Property | Module |
|---|---|---|
| **Added** | `ei:canonicalUnit` | `measurement` |
| **Range widened** | `ei:authoredBy` | `media` (range `ei:Expert` → `foaf:Person`) |
| **Range widened** | `ei:spokenBy` | `media` (range `ei:Expert` → `foaf:Person`) |
| **Range note** | `ei:aboutTechnology` | `measurement` (range stays `skos:Concept` at OWL; punning admits OEO classes — see § 3) |
| **Reused (no local addition)** | `qudt:hasQuantityKind` | imported from QUDT subset; no `ei:hasQuantityKind` minted |

No V0 property is renamed, deprecated, or deleted. No V0 cardinality is loosened.

---

## 1. New object property — `ei:canonicalUnit`

| Field | Value |
|---|---|
| Name | `ei:canonicalUnit` |
| Type | `owl:ObjectProperty`, `owl:FunctionalProperty` |
| Domain | `ei:CanonicalMeasurementClaim` |
| Range | `qudt:Unit` |
| Cardinality on domain | 0..1 (max 1; Functional gives the upper bound at the OWL level) |
| Characteristics | Functional |
| Super-property | none (top-level local property; not a sub-property of `ei:references`) |
| RO parent | none — QUDT-side relationship, no clean RO mapping; QUDT is its own vocabulary not aligned with RO |
| Intent | `infer + restrict` |
| Source CQ | CQ-016 (must_have) |

**Source axiom (Manchester sketch, for architect):**
```
ei:canonicalUnit a owl:ObjectProperty, owl:FunctionalProperty ;
  rdfs:domain ei:CanonicalMeasurementClaim ;
  rdfs:range  qudt:Unit ;
  rdfs:label "canonical unit"@en ;
  skos:definition
    "Links a CanonicalMeasurementClaim to the canonical qudt:Unit IRI
    that the claim's surface-form ei:assertedUnit string resolves to.
    Functional: a CMC has at most one canonical unit."@en .

# Optional class-level restriction (V1 ships this):
ei:CanonicalMeasurementClaim rdfs:subClassOf
  [ a owl:Restriction ;
    owl:onProperty ei:canonicalUnit ;
    owl:maxCardinality 1 ;
    owl:onClass qudt:Unit ] .
```

**Why these decisions** (CQ-Q-2 rationale; cross-ref [conceptual-model-v1.md § 4](conceptual-model-v1.md)):

1. **Range = `qudt:Unit` only**, not a union with `qudt:QuantityKind`. CQ-016 binds against a Unit IRI (`unit:GigaW`). CQ-017 walks Unit → QK via the imported `qudt:hasQuantityKind` property. There is no use case in V1 for canonicalising a CMC to a QuantityKind directly; QK is a derivation from Unit.

2. **Cardinality = 0..1 (Functional).** Per [scope-v1.md § In-scope](scope-v1.md) line 53 and scout's recommendation. The 0 lower bound supports the resolvability-gate use case: a fresh CMC may have an `ei:assertedUnit` surface string ("GW") but the canonical IRI hasn't been resolved yet. The LLM stage's job is to populate `ei:canonicalUnit`. Functional gives the reasoner the upper bound — if two distinct `ei:canonicalUnit` values are asserted on the same CMC, HermiT either fuses them via `owl:sameAs` or reports inconsistency (depending on whether they are explicitly `owl:differentFrom`).

3. **Naming = `ei:canonicalUnit`.** Alternatives considered:
   - `ei:hasUnit` — too generic; conflates surface and canonical forms.
   - `ei:assertedQudtUnit` — confusing, suggests it is the asserted form (it is the resolved form).
   - `ei:canonicalUnit` — descriptive of its semantic role and aligns with the resolvability vocabulary already in scope-v1.md.

4. **Pair with `ei:assertedUnit`.** V0's `ei:assertedUnit xsd:string` stays unchanged. The pair (`ei:assertedUnit` token + `ei:canonicalUnit` IRI) implements the surface-form-to-canonical-IRI link cleanly. CQ-016 fixture binds the IRI; SPARQL needs no string normalisation.

**Closure / OWA implications:**
- A CMC with `ei:assertedUnit "GW"` and no `ei:canonicalUnit` is a legitimate ABox state — the resolvability gate has not fired yet. SHACL S-V1-2 (see [shacl-vs-owl-v1.md](shacl-vs-owl-v1.md) § 2) optionally validates the resolvability gate at runtime; the OWL TBox does not require canonicalUnit to be present.
- The Functional property characteristic interacts with OWA: under OWA, two distinct asserted `ei:canonicalUnit` values default to "they might be the same; let's try to fuse them via `owl:sameAs`" rather than "this is inconsistent." This is the desired behavior — extractor pipelines may temporarily produce two candidate canonicalisations that the resolver later merges. Inconsistency arises only with an explicit `owl:differentFrom`.

**SHACL companion shapes** (defense-in-depth; see [shacl-vs-owl-v1.md](shacl-vs-owl-v1.md)):
- S-V1-1: `ei:canonicalUnit` value MUST be in the imported QUDT 2.1 unit subset (i.e., have `rdf:type qudt:Unit` AND be one of the 25 imported individuals). `sh:in` shape on the frozen subset.
- S-V1-2 (optional): if `ei:assertedUnit` is present, `ei:canonicalUnit` SHOULD also be present (severity = `sh:Warning`, not `sh:Violation` — supports resolvability gate).

---

## 2. Rejected property — `ei:hasQuantityKind`

**Proposal:** Add `ei:hasQuantityKind` (range `qudt:QuantityKind`, on `ei:Variable`, 0..1) per scope-v1.md § 2 line 54 + scout SQ-2 + manifest open question V1-IM-Q3.

**Decision: REJECTED for V1.**

**Rationale:**

1. **CQ-017 SPARQL already routes through Unit.** The committed [`tests/cq-017.sparql`](../tests/cq-017.sparql) reads:
   ```
   ?cmc ei:canonicalUnit ?unit .
   ?unit qudt:hasQuantityKind quantitykind:Power .
   ```
   The QK is reached **via the unit**, using the imported `qudt:hasQuantityKind` property. No `ei:hasQuantityKind` is needed.

2. **Two sources of truth anti-pattern.** A local `ei:hasQuantityKind` on Variable would duplicate the QK information already available on Unit (each imported `qudt:Unit` declares ≥ 1 `qudt:hasQuantityKind`). Scout's handoff [§ CQ-Q-2](scout-to-conceptualizer-handoff-v1.md) explicitly warned against this: "putting `hasQuantityKind` on CMC creates two sources of truth (CMC's declared QK and Variable's QK)." The same argument applies to Variable.

3. **Variable stays thin in V1** per V0's [scope.md § Variable seven-facet deferral](scope.md). Adding QK to Variable would be a Variable-facet decision — that's V2 work, not V1 unit-crosswalk work.

4. **The property characteristics scout proposed don't fit V1's chain.** Scout's recommended placement was Variable; CQ-017 does not query Variable. If Variable had `ei:hasQuantityKind`, CQ-017 would need to walk CMC → Variable → QK and bypass Unit, which loses the canonical-unit grounding.

**What this means for the architect:** Do NOT mint `ei:hasQuantityKind`. Use the imported `qudt:hasQuantityKind` directly in the CQ-017 path. The QUDT subset import is sufficient — every imported unit carries its `qudt:hasQuantityKind` triples.

**What this means for V2:** If V2 reopens the seven-facet Variable model and there is a use case for asserting "this Variable measures quantities of QuantityKind X" *independent* of any specific Unit, that is a V2 design decision. It is not in V1 scope.

---

## 3. Range widenings on V0 properties

### 3.1 `ei:authoredBy` (media module)

| Field | V0 | V1 |
|---|---|---|
| Domain | `ei:Post` | `ei:Post` (unchanged) |
| Range | `ei:Expert` | **`foaf:Person`** |
| Cardinality | exactly 1 | exactly 1 (unchanged) |
| Characteristics | Functional | Functional (unchanged) |
| Source CQ | CQ-002 | CQ-002 (unchanged) + CQ-018 (V1) |
| Intent | `infer + restrict` | `infer + restrict` (unchanged) |

**V1 axiom rewrite (architect to apply):**
```
ei:authoredBy rdfs:range foaf:Person .                 # was: ei:Expert

ei:Post rdfs:subClassOf
  [ a owl:Restriction ;
    owl:onProperty ei:authoredBy ;
    owl:cardinality 1 ;
    owl:onClass foaf:Person ] .                         # was: onClass ei:Expert
```

**Why:** the V1 Expert refactor (CQ-Q-1, conceptual-model-v1.md § 2) keeps `ei:Expert` as a defined equivalent class of `foaf:Person ⊓ (bfo:0000053 some ei:EnergyExpertRole)`. The reasoner classifies any role-bearer as `ei:Expert`. The OWL range `foaf:Person` is therefore the correct canonical range — it is the broader, BFO-grounded class. A SHACL companion shape (S-V1-3, see [shacl-vs-owl-v1.md](shacl-vs-owl-v1.md)) requires the Person to bear an `ei:EnergyExpertRole` for defense-in-depth.

**V0 CQ-002 continues to pass:**
- V0 fixtures assert `?p a ei:Expert`. Under the V1 EquivalentTo, any individual classified as `ei:Expert` is **also** a `foaf:Person` (via the intersection). So `Post ei:authoredBy ?p` with `?p a ei:Expert` still satisfies `range foaf:Person`.
- The `exactly 1 foaf:Person` restriction is satisfied: a Post has one author who is a Person. The Person may or may not bear an EnergyExpertRole (it must, in canonical fixtures, but the OWL-level cardinality only requires Personhood).

### 3.2 `ei:spokenBy` (media module)

| Field | V0 | V1 |
|---|---|---|
| Domain | `ei:PodcastSegment` | `ei:PodcastSegment` (unchanged) |
| Range | `ei:Expert` | **`foaf:Person`** |
| Cardinality | 0..n | 0..n (unchanged — multi-speaker permitted) |
| Characteristics | none | none (unchanged) |
| Source CQ | CQ-011 | CQ-011 (unchanged) |
| Intent | `infer` | `infer` (unchanged) |

**V1 axiom rewrite (architect to apply):**
```
ei:spokenBy rdfs:range foaf:Person .                    # was: ei:Expert
```

**Why:** symmetric to § 3.1. No cardinality restriction on PodcastSegment (segment may have any number of speakers).

### 3.3 `ei:aboutTechnology` (measurement module) — range note

| Field | V0 | V1 |
|---|---|---|
| Domain | `ei:CanonicalMeasurementClaim` | unchanged |
| Range | `skos:Concept` | **`skos:Concept`** (unchanged at OWL; OEO classes admitted via punning) |
| Cardinality | 0..n | unchanged |
| Characteristics | none | unchanged |
| Source CQ | CQ-013, CQ-014 | + CQ-015, CQ-019 (V1) |
| Intent | `infer` | `infer` (unchanged) |

**No axiom change needed.** OEO IRIs become punned individuals (each IRI denotes both an `owl:Class` from the OEO subset import and a `skos:Concept` from the V0 hand-seeded SKOS scheme + V1 OEO punning). The CQ-015 SPARQL walks `(skos:broader|rdfs:subClassOf)*` which traverses both views.

**Important: the architect does NOT add an axiom typing OEO IRIs as `skos:Concept` instances.** That typing arises from punning when a fixture asserts `?cmc ei:aboutTechnology oeo:OEO_xxx`. At the TBox-only V1 stage, no such fixture exists; the V1 TBox does not introduce any new triple about OEO IRIs.

---

## 4. Reused QUDT property — `qudt:hasQuantityKind`

| Field | Value |
|---|---|
| Name | `qudt:hasQuantityKind` |
| Type | `owl:ObjectProperty` |
| Source | imported from `imports/qudt-units-subset.ttl` |
| Domain (per QUDT) | `qudt:Unit` (and other QUDT classes; not constrained locally) |
| Range (per QUDT) | `qudt:QuantityKind` |
| Cardinality on Unit | 1..n in QUDT data (most units link to ≥ 1 QK) |
| Local reuse | Used in CQ-017 SPARQL chain: `?cmc ei:canonicalUnit ?u . ?u qudt:hasQuantityKind ?qk` |

**No local axiom on this property.** The QUDT import declares it; we use it as-is.

---

## 5. Updated characteristics audit (V1 deltas only)

Cross-reference V0 [property-design.md § 7](property-design.md) for the full V0 audit. V1 additions / changes:

| Property | Functional | InvFunctional | Transitive | Symmetric | Asymmetric | Reflexive | Irreflexive |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `ei:canonicalUnit` (new) | **yes** | no | no | no | no | no | no |
| `ei:authoredBy` | yes (V0; unchanged) | no | no | no | no | no | no |
| `ei:spokenBy` | no (V0; unchanged) | no | no | no | no | no | no |

`ei:canonicalUnit` is Functional (the source of the 0..1 upper bound). InvFunctional is **NOT** declared — multiple CMCs may share the same canonical unit (this is precisely CQ-016's join shape).

---

## 6. Open property-design questions (none for V1)

V0 [property-design.md § 8](property-design.md) had three open items, all resolved in V0 architect phase. V1 introduces no new open property-design questions.

The scout-handoff open questions (V1-IM-Q1, V1-IM-Q2, V1-IM-Q3) are answered:
- V1-IM-Q1 (deprecate V0 unfixed OEO subsets): curator scope, not property design.
- V1-IM-Q2 (strip 25 transitively-pulled QKs): KEEP per scout recommendation; conceptualizer concurs (cost <100 triples; never appears in CMC range constraints).
- V1-IM-Q3 (`ei:hasQuantityKind` location): **CLOSED** per § 2 above; no local property minted; QK reached via imported `qudt:hasQuantityKind`.

---

## 7. Architect handoff summary

| Action | Where | Notes |
|---|---|---|
| Mint `ei:canonicalUnit` ObjectProperty + Functional + range `qudt:Unit` | `modules/measurement.ttl` | Add SubClassOf restriction on CMC: `ei:canonicalUnit max 1 qudt:Unit` |
| Widen `ei:authoredBy` range to `foaf:Person` | `modules/media.ttl` | Update the existing CMC SubClassOf restriction's `onClass` from `ei:Expert` to `foaf:Person` |
| Widen `ei:spokenBy` range to `foaf:Person` | `modules/media.ttl` | No cardinality restriction to update |
| Do NOT mint `ei:hasQuantityKind` | — | Use imported `qudt:hasQuantityKind` directly in CQ-017 SPARQL |
| Wire three new `owl:imports` at `energy-intel.ttl` top-level | `energy-intel.ttl` + `catalog-v001.xml` | Imports: `oeo-technology-subset-fixed.ttl`, `oeo-carrier-subset-fixed.ttl`, `qudt-units-subset.ttl`; catalog rows append |
| Re-run `robot reason --reasoner hermit` | validation | Empirically clean per scout's V1 trace; architect re-runs on the actual local module integration |

See [conceptualizer-to-architect-handoff-v1.md](conceptualizer-to-architect-handoff-v1.md) for the integrated architect plan.
