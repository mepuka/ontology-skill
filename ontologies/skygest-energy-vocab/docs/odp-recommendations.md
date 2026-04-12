# Skygest Energy Vocabulary — ODP Recommendations

**Date**: 2026-04-11
**Phase**: 2 — Knowledge Acquisition

---

## Applicable Ontology Design Patterns

### 1. Value Partition Pattern (primary)

**Relevance**: High — this is the core pattern for the entire vocabulary

The Value Partition pattern models a quality space as a set of exhaustive,
mutually exclusive values. Each ConceptScheme in sevocab is a value partition:

- `StatisticTypeScheme` partitions the "type of quantity" space into
  {stock, flow, price, share, count}
- `AggregationScheme` partitions temporal aggregation into
  {point, end_of_period, sum, average, max, min, settlement}
- `UnitFamilyScheme` partitions measurement units into
  {power, energy, currency, currency_per_energy, mass_co2e, intensity,
  dimensionless, other}

**Instantiation**: Already naturally expressed as SKOS ConceptSchemes with
`skos:inScheme`. The scheme membership constraint (CQ-023: every concept
in exactly one scheme) enforces the partition invariant.

**Note**: In OWL this would be a covering axiom
(`StatisticType ≡ Stock ⊔ Flow ⊔ Price ⊔ Share ⊔ Count`). In SKOS
we express this structurally: the scheme lists its members, and the
constraint CQ ensures no concept escapes.

### 2. N-ary Relation Pattern (for provenance)

**Relevance**: High — needed for CQ-012 through CQ-014, CQ-028

The standard `skos:altLabel` triple cannot carry provenance metadata.
The N-ary Relation pattern reifies the relationship:

```
sevocab:SolarPv  sevocab:hasProvenanceAnnotation  _:entry1 .
_:entry1  sevocab:surfaceFormValue  "photovoltaic"@en .
_:entry1  sevocab:provenance        "oeo-derived" .
_:entry1  skos:note                 "Harvested from OEO:00000034 label" .
_:entry1  dcterms:created           "2026-04-11"^^xsd:date .
```

**Alternative considered**: RDF-star (`<<sevocab:SolarPv skos:altLabel
"photovoltaic"@en>> sevocab:provenance "oeo-derived"`) — more concise but
less SPARQL 1.1 portable and not supported by all triple stores.

**Recommendation**: Use the N-ary pattern (reified SurfaceFormEntry
individuals). The CQ SPARQL drafts already assume this pattern.

### 3. Lexical Sense / Ontolex Pattern (considered, not recommended)

**Relevance**: Low

The Ontolex-Lemon model provides rich lexical entry modeling
(`ontolex:LexicalEntry`, `ontolex:writtenRep`, `ontolex:sense`). It would
be ideal for a general-purpose multilingual vocabulary.

**Not recommended because**:
- The Worker consumes flat JSON with a specific `SurfaceFormEntry` schema
- Ontolex would add modeling complexity that doesn't map to the product
  contract
- SKOS altLabel + the N-ary provenance pattern gives us everything we need
- Ontolex would require additional tooling for the build pipeline

### 4. Concept Hierarchy Pattern (for TechnologyOrFuelScheme)

**Relevance**: Medium

`skos:broader` / `skos:narrower` for the TechnologyOrFuel hierarchy:

```
sevocab:OnshoreWind  skos:broader  sevocab:Wind .
sevocab:OffshoreWind skos:broader  sevocab:Wind .
sevocab:BrownCoal    skos:broader  sevocab:Coal .
sevocab:GasCcgt      skos:broader  sevocab:NaturalGas .
```

**Depth constraint**: Maximum 2 levels per scope doc. This is a simple
polyhierarchy — no complex diamond inheritance or multiple broader parents.

**Note**: `skos:broader` is not transitive by default. If the resolver needs
to match "wind" surface forms against both Wind and its children, the build
script must propagate surface forms down (or up) the hierarchy explicitly.

## Non-Applicable Patterns

| Pattern | Why Not |
|---------|---------|
| Part-Whole | No mereological relationships in a SKOS vocabulary |
| Participation | No process modeling (this is a vocabulary, not a domain ontology) |
| Information Realization (GDC/ICE) | Surface forms are strings, not information artifacts requiring concretization |
| Role | No social/contextual roles in the facet decomposition domain |

## Summary for Architect Phase

The architect should implement:
1. **Value Partition** via SKOS ConceptSchemes (already the natural fit)
2. **N-ary Relation** via SurfaceFormEntry reification for provenance
3. **Simple hierarchy** via `skos:broader` for TechnologyOrFuelScheme

No OWL-level ODPs (covering axioms, qualified cardinality, role chains)
are needed. This is a SKOS vocabulary with one custom extension
(SurfaceFormEntry provenance).
