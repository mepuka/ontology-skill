# BFO Alignment: DCAT Structural Extension

**Decision**: No BFO alignment for this extension.

## Rationale

This is an application ontology extension that bridges two W3C standards
(DCAT and Data Cube) with a domain vocabulary. The three new classes
subclass external standard classes, not BFO categories:

| Class | Parent | Why not BFO |
|-------|--------|-------------|
| EnergyVariable | schema:StatisticalVariable | Statistical abstraction, not a BFO entity |
| EnergyDataset | dcat:Dataset | Information artifact — would align to IAO, not BFO directly |
| EnergyAgent | foaf:Agent | Social entity — BFO Agent is debated and context-dependent |

BFO alignment would add complexity without benefit for the eval loop use
case. If the ontology later needs interoperability with BFO-aligned
scientific ontologies (e.g., OEO), alignment can be added via the mapper
skill without modifying the structural layer.

## If alignment were needed

For reference, the most likely BFO categories would be:

- EnergyVariable → BFO:GenericallyDependentContinuant (information content entity)
- EnergyDataset → BFO:GenericallyDependentContinuant (via IAO:DataSet)
- EnergyAgent → BFO:MaterialEntity (if organization) or Role (if agent-as-role)
