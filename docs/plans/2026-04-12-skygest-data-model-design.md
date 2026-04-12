# Design: DCAT Structural Extension for skygest-energy-vocab

**Date**: 2026-04-12
**Status**: Approved
**Scope**: Extend sevocab with DCAT 3 structural model and Variable composition
**Decision**: Add structural layer directly into sevocab (additive, no impact on existing JSON build)

## Problem

The skygest-energy-vocab (sevocab) provides a flat SKOS vocabulary of surface
forms organized into 7 facet schemes. The skygest-cloudflare resolution kernel
composes those facets into Variables, which belong to Datasets published by
Agents — the full DCAT chain. But that structural knowledge lives only in
TypeScript code. The ontology has no idea that its schemes are facet dimensions
of a StatisticalVariable, or that Variables relate to Datasets and Agents.

This causes two problems:
1. The resolution kernel's composition logic is ad-hoc, not grounded in formal
   semantics. TypeScript types diverge from the ontology over time.
2. The "ambiguous" eval bucket (41 cases) has candidates tying on facet counts
   because there's no structural traversal (Agent → Dataset → Variable) to
   break ties.

## Solution

A new structural ontology (`skygest-data-model.ttl`) that:
- Imports DCAT 3, W3C Data Cube, schema.org, and sevocab
- Declares the full DCAT chain: Agent → Dataset → Distribution → Variable
- Declares Variable composition: 7 sevocab schemes as `qb:DimensionProperty`
- Provides the formal model that TypeScript types should derive from

## Design

### Entity Hierarchy

```
sky:EnergyAgent       rdfs:subClassOf  foaf:Agent
sky:EnergyDataset     rdfs:subClassOf  dcat:Dataset
sky:EnergyVariable    rdfs:subClassOf  schema:StatisticalVariable
dcat:Distribution     (used directly, no subclass needed)
```

### DCAT Chain (Structural Relationships)

```turtle
sky:EnergyDataset
    rdfs:subClassOf dcat:Dataset ;
    rdfs:subClassOf [
        a owl:Restriction ;
        owl:onProperty dct:publisher ;
        owl:someValuesFrom sky:EnergyAgent
    ] ;
    rdfs:subClassOf [
        a owl:Restriction ;
        owl:onProperty dcat:distribution ;
        owl:someValuesFrom dcat:Distribution
    ] ;
    rdfs:subClassOf [
        a owl:Restriction ;
        owl:onProperty sky:hasVariable ;
        owl:someValuesFrom sky:EnergyVariable
    ] .
```

### Variable Composition (Dimensional Model)

Each sevocab scheme becomes a `qb:DimensionProperty` with a `qb:codeList`:

```turtle
sky:measuredProperty  a qb:DimensionProperty ;
    rdfs:range         skos:Concept ;
    qb:codeList        sevocab:MeasuredPropertyScheme ;
    rdfs:label         "measured property" ;
    skos:definition    "The physical or economic quantity being measured." .

sky:domainObject      a qb:DimensionProperty ;
    qb:codeList        sevocab:DomainObjectScheme .

sky:technologyOrFuel  a qb:DimensionProperty ;
    qb:codeList        sevocab:TechnologyOrFuelScheme .

sky:statisticType     a qb:DimensionProperty ;
    qb:codeList        sevocab:StatisticTypeScheme .

sky:aggregation       a qb:DimensionProperty ;
    qb:codeList        sevocab:AggregationScheme .

sky:unitFamily        a qb:DimensionProperty ;
    qb:codeList        sevocab:UnitFamilyScheme .

sky:policyInstrument  a qb:DimensionProperty ;
    qb:codeList        sevocab:PolicyInstrumentScheme .
```

`sky:EnergyVariable` declares restrictions on all 7 dimensions:

```turtle
sky:EnergyVariable
    rdfs:subClassOf schema:StatisticalVariable ;
    rdfs:subClassOf [
        a owl:Restriction ;
        owl:onProperty sky:measuredProperty ;
        owl:maxQualifiedCardinality "1"^^xsd:nonNegativeInteger ;
        owl:onClass skos:Concept
    ] ;
    # ... (same pattern for all 7 facets)
    .
```

### Data Structure Definition (qb:DataStructureDefinition)

Declares the complete dimensional structure in one place:

```turtle
sky:EnergyVariableStructure a qb:DataStructureDefinition ;
    qb:component [ qb:dimension sky:measuredProperty ] ;
    qb:component [ qb:dimension sky:domainObject ] ;
    qb:component [ qb:dimension sky:technologyOrFuel ] ;
    qb:component [ qb:dimension sky:statisticType ] ;
    qb:component [ qb:dimension sky:aggregation ] ;
    qb:component [ qb:dimension sky:unitFamily ] ;
    qb:component [ qb:dimension sky:policyInstrument ] .
```

### Imports Strategy

Avoid importing full external ontologies (bloat). Use ROBOT extract to pull
only the needed classes and properties:

| Source | Extract |
|--------|---------|
| DCAT 3 | `dcat:Dataset`, `dcat:Distribution`, `dcat:distribution`, `dcat:accessURL`, `dcat:mediaType` |
| Data Cube | `qb:DimensionProperty`, `qb:codeList`, `qb:DataStructureDefinition`, `qb:component` |
| schema.org | `schema:StatisticalVariable` |
| FOAF | `foaf:Agent` |
| DCTerms | `dct:publisher`, `dct:title`, `dct:description` |

Extracted declarations go in `imports/` as minimal Turtle stubs.

### File Layout

```
ontologies/skygest-data-model/
├── skygest-data-model.ttl          # Main structural ontology (TBox)
├── imports/
│   ├── dcat-extract.ttl            # DCAT 3 minimal extract
│   ├── datacube-extract.ttl        # W3C Data Cube extract
│   ├── schema-extract.ttl          # schema.org extract
│   └── foaf-extract.ttl            # FOAF extract
├── shapes/
│   └── data-model-shapes.ttl       # SHACL shapes for structural validation
├── docs/
│   └── scope.md                    # Scope and requirements
├── tests/
│   ├── cq/                         # SPARQL competency question tests
│   └── test_data_model.py          # Python unit tests
└── scripts/
    └── build.py                    # Build + extract script
```

### Resolution Kernel Impact

Once modeled, the TypeScript resolution kernel can:
1. Use facet composition formally: matched facets → partial Variable shape
2. Traverse structurally: Variable → Dataset → Agent for disambiguation
3. Generate TypeScript types from the ontology (future)
4. Validate registry entries against the ontology structure

### What This Does NOT Change

- sevocab stays a clean SKOS vocabulary (no structural changes)
- The JSON surface form export pipeline stays the same
- The resolution kernel's surface form matching stays the same
- Only the *composition and disambiguation* logic gets structural grounding

## Standards Used

| Standard | Role |
|----------|------|
| DCAT 3 (W3C) | Catalog structure: Dataset, Distribution, Agent |
| W3C Data Cube (qb:) | Dimensional model: facets as DimensionProperty |
| SDMX | Statistical concepts (aligned via Data Cube) |
| schema.org | StatisticalVariable type |
| SKOS | Vocabulary structure (sevocab) |
| OWL 2 | Restrictions, class hierarchy |
| SHACL | Structural validation |
