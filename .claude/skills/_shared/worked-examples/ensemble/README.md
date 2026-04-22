# Worked Example — Music Ensemble Ontology

**Status:** stub (Wave 3a). Wave 4 adds per-skill walkthroughs.
**Domain:** Western music ensembles, their instruments, performers, and performances.
**Referenced by:** every SKILL.md's `## Worked Examples` section.

This example runs the full pipeline (requirements → scout → conceptualizer
→ architect → mapper → validator → curator, plus sparql-expert) on a
small, familiar domain. Each skill's per-example file demonstrates one
or two key operations from that skill's workflow against the same
ontology artifacts.

## Scope

- **Classes (~30):** instruments (`Violin`, `Cello`, `Piano`, `Drum`,
  …), ensembles (`StringQuartet`, `Orchestra`, `JazzCombo`), performers
  (`Musician`, roles like `Soloist`, `Conductor`), performances
  (`Concert`, `Rehearsal`), works (`Composition`, `Arrangement`).
- **Properties:** `hasMember`, `hasInstrument`, `performedBy`,
  `performedAt`, `hasComposer`, `hasArrangement`.
- **Non-goals:** recordings, venues (except as participants), ticketing,
  music theory beyond instrument classification.
- **Target OWL profile:** DL (to accommodate qualified cardinality on
  ensemble membership).
- **Reuse:** MIMO (Musical Instruments Museum Online) for instrument
  taxonomy, BFO/RO for upper structure, PROV for performance provenance.

## Driving competency questions

Five CQs drive the example; each surfaces a modeling choice the pipeline
has to make.

| ID | Priority | Question | Highlights |
|---|---|---|---|
| CQ-E-001 | Must | Which ensembles consist of exactly four string players? | Qualified cardinality → DL profile; `hasMember` + player-role. |
| CQ-E-002 | Must | What instruments does a given musician play? | Role-vs-type: musician is not a subclass of instrument. |
| CQ-E-003 | Should | Which performances occurred in 2024 and featured a specific composition? | N-ary reification; time-interval modeling. |
| CQ-E-004 | Should | Which ensemble types are defined by their instrumentation (not their size)? | `EquivalentClass` vs `SubClassOf` boundary. |
| CQ-E-005 | Nice | Which MIMO terms map to our ensemble instrument classes, and where does a cross-domain `exactMatch` to schema.org `MusicInstrument` risk a clique > 3? | SSSOM + clique check + cross-domain rule. |

## Target axiom patterns

The example exercises the following entries from
[`axiom-patterns.md`](../../axiom-patterns.md) and
[`pattern-catalog.md`](../../pattern-catalog.md):

- § 7 Qualified cardinality (CQ-E-001).
- § 4 Equivalent class (CQ-E-004).
- § 9 N-ary relation (CQ-E-003).
- § 3 Value partition + § 8 closure axiom (for instrument family).
- ODP § 3.3 Role (CQ-E-002).
- ODP § 3.5 N-ary relation (CQ-E-003).

## Per-skill walkthroughs

Each file below will be filled in during Wave 4. The structure is:

- `requirements.md` — CQs, ORSD, `requirements-approval.yaml`.
- `scout.md` — reuse evaluation (MIMO, BFO, RO, schema.org), import manifest.
- `conceptualizer.md` — glossary, taxonomy, BFO alignment, axiom plan, closure review.
- `architect.md` — ROBOT templates for instrument/ensemble terms, qualified
  cardinality axiom for string quartet, ELK-vs-HermiT choice, SHACL for `hasMember` lower bound.
- `mapper.md` — SSSOM set against MIMO; Class B LLM review on one MEDIUM row; clique check.
- `validator.md` — seven-level run, failure injection, loopback routing.
- `curator.md` — deprecation of an experimental role subclass with replacement pointer.
- `sparql.md` — SPARQL for each CQ with expected-results contract.

## Expected artifacts (Wave 4 lands these)

```
.claude/skills/_shared/worked-examples/ensemble/
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

No TTL or SPARQL files live here — the worked-example docs cite fragments
inline. The full build lives in `ontologies/ensemble/` if/when the example
is exercised end-to-end.
