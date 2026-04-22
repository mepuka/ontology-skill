# Worked Example — Community Microgrid Ontology

**Status:** stub (Wave 3a). Wave 4 adds per-skill walkthroughs.
**Domain:** Community-scale microgrid: generation, storage, inverters,
loads, dispatch events, telemetry, and tariffs.
**Referenced by:** every SKILL.md's `## Worked Examples` section.

Where the ensemble example is small and familiar, the microgrid example
is more structurally involved: part-whole topology, dispatch processes,
measurement information entities, and a cross-domain mapping to an
energy-domain ontology. It exercises the pipeline on territory closer
to the production use case (the `skygest-energy-vocab` ontology in this
workspace).

## Scope

- **Classes (~60):** equipment (`SolarArray`, `Inverter`, `Battery`,
  `Load`, `Breaker`), aggregates (`Microgrid`, `SubGrid`), dispatch
  processes (`DispatchEvent`, `ChargingEvent`, `IslandingEvent`),
  information artifacts (`TelemetryPacket`, `SetpointCommand`,
  `TariffDocument`), roles (`PrimaryInverterRole`,
  `BackupInverterRole`).
- **Properties:** `hasPart`, `locatedIn`, `participatesIn`, `isAbout`,
  `hasSetpoint`, `hasTariff`, `hasMeasurement`, `triggeredBy`.
- **Non-goals:** utility-scale grid, transmission-level modeling,
  market bidding, carbon accounting (beyond a single data property on
  tariff documents).
- **Target OWL profile:** DL for closure + qualified cardinality; a
  subset of the ontology (equipment-only) is authored EL-safe for fast
  subsumption.
- **Reuse:** OEO (Open Energy Ontology) for energy-domain terms,
  BFO/RO/IAO, QUDT for units, PROV for dispatch provenance.

## Driving competency questions

Five CQs drive the example; each surfaces a different class of
structural or modeling problem.

| ID | Priority | Question | Highlights |
|---|---|---|---|
| CQ-M-001 | Must | For a given microgrid, what are all its parts transitively, grouped by equipment type? | Part-whole topology; `hasPart ∘ locatedIn → locatedIn` property chain; EL-safe. |
| CQ-M-002 | Must | Which dispatch events participated in islanding the grid in the last month, and which equipment participated in each? | Participation pattern; N-ary via reified event; time filter. |
| CQ-M-003 | Should | Which telemetry packets are about a given battery, and what measured properties do they record? | Information-realization ODP; IAO `is about`. |
| CQ-M-004 | Should | Which inverters are currently assigned the primary-inverter role for their subgrid? | Role pattern (BFO role) — not a subclass of Inverter. |
| CQ-M-005 | Nice | For the mapping from our microgrid ontology to OEO, which `skos:exactMatch` rows would escalate to `owl:equivalentClass` and which must stay SKOS? | SSSOM promotion rules; cross-domain rule (continuant vs. occurrent). |

## Target axiom patterns

The example exercises the following entries from
[`axiom-patterns.md`](../../axiom-patterns.md) and
[`pattern-catalog.md`](../../pattern-catalog.md):

- § 2 Existential + § 12 Property chain (CQ-M-001).
- § 9 N-ary relation (CQ-M-002).
- ODP § 3.2 Part-whole (CQ-M-001).
- ODP § 3.3 Role (CQ-M-004).
- ODP § 3.4 Participation (CQ-M-002).
- ODP § 3.6 Information-realization (CQ-M-003).

## Per-skill walkthroughs

Each file below will be filled in during Wave 4. The structure is:

- `requirements.md` — CQs, non-goals, `requirements-approval.yaml`.
- `scout.md` — reuse evaluation (OEO, QUDT, BFO, RO, IAO, PROV), import
  vs. bridge decision for OEO.
- `conceptualizer.md` — BFO placement for dispatch event vs. dispatch
  role vs. dispatch capability; closure review on `hasPart`; axiom plan.
- `architect.md` — ROBOT templates for equipment taxonomy, property
  chain for transitive location, SHACL for telemetry-packet structure,
  EL-vs-DL split.
- `mapper.md` — SSSOM set against OEO; cross-domain cases that must stay
  SKOS; one row that promotes to equivalence bridge.
- `validator.md` — seven-level run including profile preflight (EL
  subset) + full DL reasoner (HermiT) on the core ontology.
- `curator.md` — import refresh against an upstream OEO release;
  deprecation cascade; release notes.
- `sparql.md` — SPARQL for each CQ, expected-results contract, entailment
  regime declared per query.

## Expected artifacts (Wave 4 lands these)

```
.claude/skills/_shared/worked-examples/microgrid/
├── README.md                # this file
├── requirements.md          # Wave 4
├── scout.md                 # Wave 4
├── conceptualizer.md        # Wave 4
├── architect.md             # Wave 4
├── mapper.md                # Wave 4
├── validator.md             # Wave 4
├── curator.md               # Wave 4
└── sparql.md                # Wave 4
```

Like the ensemble example, the worked-example docs cite fragments inline
rather than publishing a separate TTL build. If fuller integration is
needed, the full build lives in `ontologies/microgrid/`.
