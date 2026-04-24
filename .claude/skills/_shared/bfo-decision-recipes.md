# BFO Decision Recipes

**Referenced by:** `ontology-conceptualizer`, `ontology-architect`.

BFO 2020 is this monorepo's default upper ontology. It is two-dimensional:
the **continuant / occurrent** distinction and the **independent /
dependent** distinction. Placing a new term under BFO is the highest-
stakes modeling choice — it governs what relations the term can enter.
This file gives three decision recipes that handle most cases, plus an
ambiguity register for the rest.

Read [`bfo-categories.md`](bfo-categories.md) first for BFO's full class
tree. This file is the decision surface for new terms.

## 1. Recipe 1 — Continuant vs Occurrent

A **continuant** persists through time, maintaining identity across
multiple time points. An **occurrent** happens / unfolds in time; it has
temporal parts.

### Decision questions

1. Can you meaningfully ask "where is it *now*?" → Continuant.
2. Can you ask "when did it start / end?" → Occurrent.
3. Does it have temporal parts (beginning, middle, end)? → Occurrent.
4. Is it the *same thing* at two different times? → Continuant.

### Examples

| Term | Answer | BFO class |
|------|--------|-----------|
| `SolarPanel` | Where is it? | Continuant → Independent → Material Entity |
| `PerformanceEvent` | When did it happen? | Occurrent → Process |
| `MaintenanceProcedure` | Temporal parts | Occurrent → Process |
| `Musician` | Same person over time | Continuant → Material Entity → Object |
| `PerformerRole` | Same role over time; realized in a process | Continuant → Dependent → Specifically Dependent |
| `ChargeState` at time t | A snapshot at t | Occurrent (process boundary) or specifically dependent continuant (quality at t) — see Recipe 3 |

### Ambiguity level

- **Level 0** — clear (Material Entity, Process). No flag needed.
- **Level 1** — intuitive but requires thought (Role, Quality, Function).
  Document the decision in `docs/bfo-alignment.md`.
- **Level 2** — genuinely ambiguous; escalate per `iteration-loopbacks.md`
  (routes to `ontology-conceptualizer`, and at depth 2 to a human
  reviewer).

## 2. Recipe 2 — Independent vs Dependent

A **continuant** is independent if it does not require another entity to
exist. It is dependent if it does.

### Decision questions

1. Could it exist with no other entity present? → Independent (Object,
   Material Entity).
2. Does it require a bearer (it inheres in something)? → Specifically
   Dependent Continuant (Quality, Role, Disposition).
3. Does it refer to / describe / generally depend on bearers in a class?
   → Generically Dependent Continuant (Information Content Entity).

### Decision diagram (text)

```
Is this a continuant?
  yes:
    does it need a specific bearer?
      yes → Specifically Dependent Continuant (SDC)
        is it intrinsic (inheres and cannot change without bearer changing)?
          yes → Quality
          no  → Role (externally imposed) or Disposition (internally realized)
      no → Generically Dependent Continuant (GDC, e.g., Information Content Entity)
  no → Occurrent (Process / Process Boundary)
```

### Examples

| Term | Classification |
|------|----------------|
| `Violin` (the physical instrument) | Independent Continuant → Object |
| `MassOfViolin` | Specifically Dependent Continuant → Quality |
| `LutenistRole` | Specifically Dependent Continuant → Role |
| `MusicalScore` (the work) | Generically Dependent Continuant → ICE |
| `MusicalScoreCopy` (a printed copy) | Independent Continuant → Object (bearer of the ICE) |
| `BatteryStateOfCharge` | Quality (inheres in the battery) |
| `WorkOrder` | Generically Dependent Continuant → ICE (the instructions are what persist; copies bear them) |

## 3. Recipe 3 — Quality vs Role vs Disposition

These are the three most-confused specifically dependent continuants.

| | Quality | Role | Disposition |
|-|---------|------|-------------|
| **Inheres in** | Its bearer | Its bearer | Its bearer |
| **Origin** | Intrinsic; the bearer exemplifies it | Externally imposed by context | Intrinsic; bears the potential for a specific process |
| **Realized in** | Not realized (it just *is*) | A process that the role-bearer participates in | A process that the disposition-bearer undergoes / causes |
| **Test** | "What is it like?" | "What does it act as?" | "What is it capable of?" |
| **Example** | `Mass`, `Color`, `TemperatureValue` | `LutenistRole`, `MaintainerRole`, `BackupSupplyRole` | `Flammability`, `Conductivity`, `CapacityToStore` |

### The classic mistake — role-as-class

`LutePlayer` is NOT a class of Person. `LutePlayer` is a role that a Person
bears during a musical performance. Modeling it as a subclass of Person
produces "the same person becomes a different instance when they switch
instruments" — a role-type confusion anti-pattern.

Correct pattern:

```ttl
:Musician rdfs:subClassOf :Person .
:LutenistRole rdfs:subClassOf bfo:Role .
:Alice a :Musician ; bfo:hasRole :AliceAsLutenist .
:AliceAsLutenist a :LutenistRole ; bfo:inheresIn :Alice .
```

Now Alice remains a single Musician across time; the role is a separate
entity with its own start/end.

### Role vs Disposition decision

- If the capacity is context-dependent (Alice *can* play the lute *when
  hired to perform*) and is realized in a particular process: Role.
- If the capacity is intrinsic and can be realized regardless of context
  (this battery *can* discharge even with no use): Disposition.

## 4. Common failure modes

- **Class for a role.** "`LutePlayer SubClassOf Person`." Fix: add a
  `*Role` class inhering in Person.
- **Process as continuant.** "`Performance SubClassOf Object`." Fix:
  align to `bfo:Process`.
- **Quality as value.** "`TemperatureValue SubClassOf Quality` with
  `hasValue "99.5"`." The Quality is distinct from the *value* held at
  a time; use a `QuantityValue` pattern.
- **Information content confused with its bearer.** `MusicalScore` is
  GDC; copies are Objects that bear it. Don't fold them.
- **Class as GDC.** Classes are not themselves GDCs in OWL; they are
  `owl:Class`. But they may *describe* GDC types.

## 5. Ambiguity register

For every Level 1/2 BFO decision, record in
`ontologies/{name}/docs/bfo-alignment.md`:

```yaml
- term: :PerformerRole
  bfo_parent: bfo:Role
  level: 1
  rationale: "Role externally imposed during a performance; realized in
              bfo:Process (the performance event)."
  alternatives_considered:
    - bfo:Disposition: "Rejected — capacity is context-dependent on
                        being hired to perform."
  decided_by: "conceptualizer session 2026-03-15"
```

Raise ambiguity Level 2 as a loopback (`failure_type: bfo_misalignment`)
per `iteration-loopbacks.md`; depth > 2 escalates to human review.

## 6. Worked examples

- [`worked-examples/ensemble/conceptualizer.md`](worked-examples/ensemble/conceptualizer.md) — PerformerRole vs Musician; Ensemble object vs object-aggregate ambiguity.
- [`worked-examples/microgrid/conceptualizer.md`](worked-examples/microgrid/conceptualizer.md) — MaintainerRole vs Maintainer class; StateOfCharge as Quality.

## 7. References

- [BFO 2020 ISO 21838-2](https://www.iso.org/standard/74572.html)
- [BFO GitHub](https://github.com/BFO-ontology/BFO) — authoritative class definitions.
- [`bfo-categories.md`](bfo-categories.md) — full BFO class map.
