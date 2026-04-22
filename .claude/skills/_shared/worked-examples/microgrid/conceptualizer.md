# Microgrid — `ontology-conceptualizer` walkthrough

Walks [`ontology-conceptualizer`](../../../ontology-conceptualizer/SKILL.md)
Steps 0–6.1 on the microgrid ontology. Goal: BFO-aligned conceptual
model covering CQ-M-001..005, with an **ambiguity register that forces
dispatch-event-vs-dispatch-role disambiguation** and a closure review
that keeps CQ-M-001 EL-safe.

## Step 0 — inbound gate

| Artifact | Status |
|---|---|
| `docs/requirements-approval.yaml` | present, reviewer ops-lead (retrofit_note: true) |
| `docs/reuse-report.md` + `imports-manifest.yaml` | OEO STAR module pinned at 1.16.0 |
| `docs/competency-questions.yaml` | 5 CQs, entailment declared per CQ |

## Step 1 — glossary (`docs/glossary.csv`, excerpt)

```
term,definition,category,source_cq,bfo_category
Microgrid,"Aggregate of power equipment interconnected at one site.",Class,CQ-M-001,bfo:ObjectAggregate
SolarArray,"Photovoltaic generation asset composed of panels and an array inverter.",Class,CQ-M-001,bfo:Object
Inverter,"Power-electronics device that converts DC to AC or vice versa.",Class,CQ-M-001/004,bfo:Object
DispatchEvent,"A process whereby generation, storage, or load changes state.",Class,CQ-M-002,bfo:Process
IslandingEvent,"A DispatchEvent that disconnects the microgrid from the utility grid.",Class,CQ-M-002,bfo:Process
TelemetryPacket,"An information content entity bearing measured values about equipment.",Class,CQ-M-003,iao:InformationContentEntity (GDC)
PrimaryInverterRole,"Realizable role assigned to exactly one inverter per subgrid.",Class,CQ-M-004,bfo:Role
hasPart,"The part-whole relation between aggregate and component.",ObjectProperty,CQ-M-001,ro:RO_0002351
locatedIn,"Spatial containment relation.",ObjectProperty,CQ-M-001,ro:RO_0001025
isAbout,"Aboutness of an ICE toward a subject.",ObjectProperty,CQ-M-003,iao:IAO_0000136
bearerOf,"A continuant bears a realizable entity.",ObjectProperty,CQ-M-004,bfo:BFO_0000196
```

## Steps 2 + 2.5 — taxonomy + layering (`docs/conceptual-model.yaml`)

```yaml
layers:
  upper:       [bfo-core, ro-core, iao-core]
  domain:      [oeo-import, qudt-unit]         # pinned OEO v1.16.0
  application: [microgrid-core, microgrid-shapes]
modules:
  microgrid-core:
    root_classes: [EnergyAsset, Microgrid, DispatchEvent, TelemetryPacket, PrimaryInverterRole]
    seed_cqs: [CQ-M-001, CQ-M-002, CQ-M-003, CQ-M-004, CQ-M-005]
    split_trigger: "If equipment class count > 150, split microgrid-equipment submodule"
```

Layer boundaries are enforced at the file level per
[`modularization-and-bridges.md § 2`](../../modularization-and-bridges.md):
upper-layer imports never reach into application-layer terms.

## Steps 3 + 3.1 — BFO ambiguity register (`docs/bfo-alignment.md`)

| Class | Candidate categories | Ambiguity | Reviewer | Decision | Rationale |
|---|---|---|---|---|---|
| `DispatchEvent` | **process**, disposition, process boundary | 2 | ops-lead@microgrid.example | process | Has non-zero temporal extent + measurable participants. Cites `bfo-decision-recipes.md § 1`. Rejected disposition: "Microgrid has the disposition to dispatch; the event is the realization, not the disposition itself." |
| `DispatchRole` | role, disposition | 2 | ops-lead@microgrid.example | **drop** | The CQ set does not require it — use `PrimaryInverterRole` (a role bearer acts in dispatches). Record to avoid reinvention. |
| `TelemetryPacket` | ICE, quality | 1 | — | ICE (IAO_0000030) | It describes battery/inverter state; it is not the state itself. |
| `StateOfCharge` | quality, process boundary | 2 | compliance-engineer@microgrid.example | quality | Intrinsic to battery; realized as quality, not process. Cites `bfo-decision-recipes.md § 3`. |

**Dispatch-event vs dispatch-role resolution.** The register records
both candidates explicitly so that CQ-M-002's "which dispatch events
participated …" unambiguously targets a process (occurrent), not a role
(continuant). Conflation would make the CQ untestable — participation is
an occurrent predicate.

## Steps 4 + 4.1 — property design + relation semantics

```yaml
- name: hasPart
  type: ObjectProperty
  domain: Microgrid
  range: EnergyAsset
  ro_parent: RO:0002351 has_member
  characteristics: [transitive]
  intent: infer
- name: locatedIn
  type: ObjectProperty
  domain: EnergyAsset
  range: SpatialRegion
  ro_parent: RO:0001025 located_in
  characteristics: [transitive]
  intent: infer
- name: participatesIn
  type: ObjectProperty
  domain: EnergyAsset
  range: DispatchEvent
  ro_parent: RO:0000056
  inverse_of: hasParticipant
  intent: infer
- name: isAbout
  type: ObjectProperty
  domain: TelemetryPacket
  range: EnergyAsset
  ro_parent: IAO:0000136
  intent: infer
- name: recordedAt
  type: DatatypeProperty
  range: xsd:dateTime
  intent: validate                       # SHACL xsd:dateTime constraint
```

## Steps 5 + 5.1 — axiom plan + closure review (`docs/axiom-plan.yaml`)

```yaml
- cq_id: CQ-M-001
  pattern: property_chain                # pattern-catalog § 3.2 part-whole
  axiom: "locatedIn SubPropertyChainOf hasPart ∘ locatedIn"
  profile: OWL-EL                        # EL supports simple chains
  closure_required: false
- cq_id: CQ-M-002
  pattern: n_ary_participation           # pattern-catalog § 3.4 / § 3.5
  axiom: "IslandingEvent SubClassOf DispatchEvent and (hasParticipant some EnergyAsset)"
  profile: OWL-EL
- cq_id: CQ-M-003
  pattern: information_realization       # pattern-catalog § 3.6
  axiom: "TelemetryPacket SubClassOf isAbout some EnergyAsset and hasMeasuredValue some xsd:decimal"
  profile: OWL-EL
- cq_id: CQ-M-004
  pattern: role                          # pattern-catalog § 3.3
  axiom: "Inverter SubClassOf bearerOf some PrimaryInverterRole"
  profile: OWL-EL                        # bearerOf existential only
- cq_id: CQ-M-005
  pattern: mapping_not_axiom
  axiom: null
```

**Closure review (§ 5.1):** Every CQ except CQ-M-005 declared
`profile: OWL-EL`. CQ-M-004 is the subtle one — adding a cardinality
`bearerOf exactly 1 PrimaryInverterRole per subgrid` would push out of
EL. Decision: keep CQ-M-004 existential in OWL; defer the **exactly 1
per subgrid** constraint to SHACL (`sh:maxCount 1` on a path-scoped
shape). This keeps the reasoner EL-safe while the deployment validator
still enforces the per-subgrid cap. OWA trap: without SHACL, an
inverter bearing two PrimaryInverterRoles would be silently valid.

## Steps 6 + 6.1 — anti-pattern review (`docs/anti-pattern-review.md`)

| # | Pattern | Detection | Finding | Resolution |
|---|---|---|---|---|
| 1 | Process-object confusion | manual | draft-TTL had `DispatchEvent SubClassOf bfo:Object` | Refactored to `bfo:Process`; Step 3.1 register tracks. |
| 2 | Role-type confusion | manual | `PrimaryInverter` class mistakenly a subclass of `Inverter` | Role pattern: `Inverter bearerOf some PrimaryInverterRole`. Cites `bfo-decision-recipes.md § 3 classic mistake`. |
| 3 | Information-physical conflation | SPARQL probe | none found (TelemetryPacket separated from battery sensor) | — |
| 4 | Missing disjointness | SPARQL probe | `GenerationAsset`, `StorageAsset`, `LoadAsset` not declared disjoint | Add `DisjointClasses`; routed to architect Step 3. |

## Handoff

All five artifacts + signed `conceptual-model-review.md` →
`ontology-architect` (see [`architect.md`](architect.md)). Architect
will instantiate the property chain (CQ-M-001) + role pattern (CQ-M-004)
and run the EL profile gate. If architect's Step 2.5 preflight catches
the dispatch-role ambiguity resurfacing in a new term proposal,
`bfo_misalignment` loopback routes back here.
