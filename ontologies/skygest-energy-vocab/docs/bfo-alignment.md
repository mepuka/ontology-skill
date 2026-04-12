# Skygest Energy Vocabulary — BFO Alignment

**Date**: 2026-04-11
**Phase**: 3 — Conceptualization

---

## Alignment Strategy

This vocabulary has **minimal BFO alignment** by design. It is a SKOS
vocabulary, not an OWL domain ontology. The concepts are reference-data
individuals (lookup entries), not types that participate in BFO-style
ontological distinctions.

BFO alignment applies to only two questions:
1. What kind of thing is a SKOS concept in this vocabulary?
2. What kind of thing is a SurfaceFormEntry?

## Alignment Decisions

### SKOS Concepts → Generically Dependent Continuant (GDC)

**BFO category**: `BFO:0000031` (Generically Dependent Continuant)

**Rationale**: Each SKOS concept (e.g., `sevocab:Stock`, `sevocab:SolarPv`)
represents an **information entity** — a canonical category used to classify
chart data. It:
- Does not exist independently (depends on the vocabulary as a bearer)
- Can migrate between bearers (can be stored in RDF, JSON, a database)
- Is not a physical thing, not a process, not a quality

This aligns with the IAO (Information Artifact Ontology) pattern where
classification schemes and their entries are GDCs.

**Practical impact**: None. We do not assert `sevocab:Stock rdf:type
BFO:0000031` in the ontology. The alignment is documented here for
conceptual clarity only. The vocabulary's OWL profile is SKOS-centric.

### SurfaceFormEntry → Generically Dependent Continuant (GDC)

**BFO category**: `BFO:0000031` (Generically Dependent Continuant)

**Rationale**: A SurfaceFormEntry is an information record — it describes
the provenance of a specific surface form string. It:
- Depends on the concept it annotates (no independent existence)
- Can be serialized in RDF or JSON (migrates between bearers)
- Has no temporal parts (not a process)

**Practical impact**: We do not subclass `BFO:0000031`. SurfaceFormEntry
is declared as `owl:Class` with no BFO parent. If a future integration
requires BFO typing, it can be added as:
```turtle
sevocab:SurfaceFormEntry rdfs:subClassOf obo:BFO_0000031 .
```

### ConceptSchemes → Not Aligned

**Rationale**: `skos:ConceptScheme` is a SKOS organizational construct.
It has no natural BFO correspondent. Attempting to place it in BFO would
be anti-pattern #15 (technical perspective over domain perspective).

## Summary

| Entity | BFO Category | Asserted in OWL? |
|--------|-------------|------------------|
| SKOS Concepts (Stock, SolarPv, ...) | GDC (`BFO:0000031`) | No — documented only |
| SurfaceFormEntry | GDC (`BFO:0000031`) | No — can be added later if needed |
| ConceptSchemes | Not aligned | No |
| Properties | N/A | N/A |

## Known Ambiguity: Concepts vs. Real-World Referents

A potential confusion: `sevocab:SolarPv` is a **concept** (information
entity), not a solar panel (material entity). The concept refers to the
category of solar PV technology, not to any physical instance. This
distinction is clean in SKOS (concepts are always information entities)
but could be confusing if the vocabulary were merged with a domain ontology
where `SolarPV` is a material entity class.

The SSSOM mappings to OEO handle this: `sevocab:SolarPv skos:closeMatch
obo:OEO_00000034` — the OEO term *is* a material entity class, while the
sevocab term is a SKOS concept. The `skos:closeMatch` relation correctly
bridges this ontological gap.
