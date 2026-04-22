# Ensemble — `ontology-conceptualizer` walkthrough

Walks [`ontology-conceptualizer`](../../../ontology-conceptualizer/SKILL.md)
Steps 0–6.1 after inbound gates from [`requirements.md`](requirements.md) and
[`scout.md`](scout.md). Goal: BFO-aligned conceptual model + axiom plan
covering all five ensemble CQs, with ambiguity and anti-pattern registers
signed by a reviewer.

## Step 0 — inbound gate

| Artifact | Status |
|---|---|
| `docs/requirements-approval.yaml` | present, signed 2026-04-22 |
| `docs/reuse-report.md` + `docs/imports-manifest.yaml` | MIMO STAR module + baseline manifest rows |
| `docs/competency-questions.yaml` | 5 Must-Have CQs with `expected_answer_shape` |

Gate passes — no loopback.

## Step 1 — glossary (`docs/glossary.csv`)

```
term,synonyms,definition,category,source_cq,bfo_category
Ensemble,musical ensemble,"An aggregate of Musicians that performs Compositions as a unit.",Class,CQ-E-001/004,bfo:ObjectAggregate
Musician,performer,"A Person who bears a PerformerRole.",Class,CQ-E-002,bfo:Object
PerformerRole,,"A role borne by a Musician while participating in a Performance.",Class,CQ-E-002,bfo:Role
MusicInstrument,instrument,"An Object used by a Musician to realize a Composition.",Class,CQ-E-002/005,bfo:Object
Performance,concert,"A Process in which Musicians realize a Composition at a time and place.",Class,CQ-E-003,bfo:Process
hasMember,,"Relates an Ensemble to a Musician that belongs to it.",ObjectProperty,CQ-E-001/002,ro:has_member
plays,,"Relates a Musician to the MusicInstrument they handle during a Performance.",ObjectProperty,CQ-E-002,ro:uses
```

## Steps 2 + 2.5 — taxonomy + layering (`docs/conceptual-model.yaml`)

```yaml
layers:
  foundational:   [bfo-core, ro-core, iao-core, skos, prov]
  domain_dependent: [mimo-core]                          # from scout
  problem_specific: [ensemble-core]
modules:
  ensemble-core:
    root_classes: [Ensemble, Musician, PerformerRole, MusicInstrument, Performance, Composition]
    seed_cqs: [CQ-E-001, CQ-E-002, CQ-E-003, CQ-E-004, CQ-E-005]
    split_trigger: "> 150 concepts — then split PerformerRole into ConductorRole/SoloistRole submodule"
```

## Steps 3 + 3.1 — BFO alignment + ambiguity register (`docs/bfo-alignment.md`)

| Class | Candidate categories | Ambiguity | Reviewer | Decision | Rationale |
|---|---|---|---|---|---|
| `Ensemble` | material entity, **object aggregate**, social role | 2 | coordinator@ensemble.example | object aggregate | Ensemble persists while membership changes (cf. Orchestra). Cites `bfo-decision-recipes.md § 2` Recipe 2. |
| `PerformerRole` | role, disposition | 1 | — | role | Externally imposed by hiring context; realized in `Performance`. |
| `Performance` | process, process boundary | 0 | — | process | Non-zero temporal extent. |
| `Composition` | GDC (ICE), object | 1 | coordinator@ensemble.example | GDC (ICE) | The *work* persists across copies; copies are objects that bear it. |

## Steps 4 + 4.1 — property design + relation-semantics (`docs/property-design.yaml`)

```yaml
- name: hasMember
  type: ObjectProperty
  domain: Ensemble
  range: Musician
  ro_parent: RO:0002351 has_member
  characteristics: [inverseFunctional, irreflexive]
  intent: infer                            # OWL rdfs:domain/range
- name: plays
  type: ObjectProperty
  domain: Musician
  range: MusicInstrument
  ro_parent: RO:0002233 uses
  intent: infer
- name: hasOpusNumber
  type: DatatypeProperty
  range: xsd:string
  intent: validate                         # SHACL sh:datatype; not OWL range
```

## Steps 5 + 5.1 — axiom plan + closure + CQ coverage (`docs/axiom-plan.yaml`)

```yaml
- cq_id: CQ-E-001
  pattern: qualified_cardinality            # axiom-patterns § 7
  axiom: "StringQuartet EquivalentTo (Ensemble and hasMember exactly 4 Musician that bears some StringPlayerRole)"
  profile: OWL-DL                           # forces out of EL — ELK will silently skip
  closure_required: false
- cq_id: CQ-E-002
  pattern: role                             # pattern-catalog § 3.3
  axiom: "Musician SubClassOf bfo:bearerOf some PerformerRole"
  profile: OWL-EL
- cq_id: CQ-E-003
  pattern: n_ary_relation                   # axiom-patterns § 9
  axiom: "Performance SubClassOf (hasParticipant some Musician) and (hasPiece some Composition) and (hasDate some xsd:date)"
  profile: OWL-EL
- cq_id: CQ-E-004
  pattern: equivalent_class                 # axiom-patterns § 4
  axiom: "StringEnsemble EquivalentTo Ensemble and hasMember only (Musician and (plays some StringInstrument))"
  profile: OWL-DL                           # universal — non-EL
  closure_required: true                    # see § 5.1
- cq_id: CQ-E-005
  pattern: mapping_not_axiom                # defer to mapper; record here for traceability
  axiom: null
  profile: n/a
```

**Closure-review note (§ 5.1).** CQ-E-004's answer depends on the
`hasMember` list being *closed* per ensemble: otherwise OWA lets a
non-string member hide in the open world and the CQ silently passes
for any ensemble. Record the decision to add a closure axiom
(`hasMember only Musician and (plays some StringInstrument)`) rather
than deferring to SHACL — the CQ is used for reasoner-based
classification, not instance validation.

## Steps 6 + 6.1 — anti-pattern review (`docs/anti-pattern-review.md`)

| # | Pattern | Detection mode | Finding | Resolution |
|---|---|---|---|---|
| 1 | Role-type confusion | manual | draft had `StringPlayer SubClassOf Musician` | Refactor to `StringPlayerRole SubClassOf bfo:Role`; `Musician bfo:bearerOf some StringPlayerRole`. Cites `bfo-decision-recipes.md § 3 classic mistake`. |
| 2 | Quality-as-class | SPARQL probe | none found | — |
| 3 | Domain/range overcommitment | manual | draft had `plays rdfs:domain Musician` narrow | Kept — Musician is the broad parent; no narrower leaf. |
| 4 | Missing disjointness | SPARQL probe | `StringEnsemble`, `WindEnsemble` siblings not disjoint | Add `DisjointClasses`. Routed to architect Step 3. |

## Handoff

All five artifacts + `conceptual-model-review.md` signature →
`ontology-architect` (see [`architect.md`](architect.md)). If architect
surfaces a `closure_gap` on CQ-E-004, it loops back here per
[`iteration-loopbacks.md § 3`](../../iteration-loopbacks.md).
