# Scope: DCAT Structural Extension

**Parent**: skygest-energy-vocab
**Date**: 2026-04-12

## Purpose

Extend sevocab with a structural layer that models how its 7 facet schemes
compose into statistical variables and how those variables relate to DCAT
catalog entities (Agent, Dataset, Distribution). This is an additive
extension — the existing SKOS vocabulary and JSON build pipeline are
unaffected.

## Domain

The structural model covers:
- **Variable composition** — 7 sevocab schemes as qb:DimensionProperty
  instances with codeList references to the existing ConceptSchemes
- **DCAT chain** — Agent → Dataset → Distribution with the standard DCAT 3
  properties, plus a sky:hasVariable link from Dataset to Variable
- **DataStructureDefinition** — a W3C Data Cube structure declaring the
  complete dimensional model in one place

## Stakeholders

| Stakeholder | Information Need |
|-------------|------------------|
| Resolution kernel (Stage 2) | Variable composition rules, DCAT traversal for disambiguation |
| Platform engineers | Formal model to derive/validate TypeScript types |
| Eval loop | Structural signals to reduce ambiguous bucket (41 cases) |

## In Scope

- sky:EnergyAgent rdfs:subClassOf foaf:Agent
- sky:EnergyDataset rdfs:subClassOf dcat:Dataset
- sky:EnergyVariable rdfs:subClassOf schema:StatisticalVariable
- 7 qb:DimensionProperty declarations with qb:codeList → sevocab schemes
- sky:hasVariable linking Dataset to Variable
- dct:publisher linking Dataset to Agent
- dcat:distribution linking Dataset to Distribution
- Cardinality restrictions (each facet at most 1 per Variable)
- qb:DataStructureDefinition for the dimensional model
- SHACL shapes for structural validation
- Minimal DCAT property coverage: accessURL, mediaType, title, description

## Out of Scope

- Modifying existing SKOS concepts or altLabels
- ABox individuals (specific Agents, Datasets, Variables)
- Temporal/series structure (future work)
- BFO alignment (application ontology, not reference)
- Full DCAT 3 property coverage
- Data quality, provenance, or access control metadata

## Constraints

- OWL 2 DL — classifiable by ELK/HermiT
- Additive only — existing SKOS content and build.py untouched
- External vocab fragments via ROBOT extract (minimal imports/)
- Turtle serialization

## Namespace

Structural classes and properties use the existing sevocab namespace:
```
Base:    https://skygest.dev/vocab/energy/
Prefix:  sevocab:
```

This avoids introducing a second namespace. The structural layer is part of
the same ontology, just a different concern within it.

## Impact on Existing Artifacts

| Artifact | Impact |
|----------|--------|
| skygest-energy-vocab.ttl | Extended with new classes, properties, restrictions |
| data/vocabulary/*.json | None — build.py only reads SKOS altLabels |
| shapes/*.ttl | Extended with new structural shapes |
| tests/cq-*.sparql | New CQs added for structural layer |
| imports/ | New — DCAT/qb/schema.org/FOAF extracts |
