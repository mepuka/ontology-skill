# Anti-Pattern Review: DCAT Structural Extension

**Date**: 2026-04-12
**Reviewer**: ontology-conceptualizer
**Result**: 0 unresolved issues

## Checks Performed

### 1. Singleton Hierarchy
**Status**: Acknowledged, acceptable.

EnergyVariable, EnergyDataset, and EnergyAgent each have exactly one
named parent (schema:StatisticalVariable, dcat:Dataset, foaf:Agent).
Normally this is a smell, but here these are application-specific
specializations of well-known standard classes. Adding sibling classes
(e.g., ClimatVariable, FinanceVariable) would be speculative. No fix
needed.

### 2. Role-Type Confusion
**Status**: Clean.

EnergyAgent models the entity type (a publisher), not a role. An Agent
does not "stop being" an Agent. No confusion.

### 3. Process-Object Confusion
**Status**: N/A.

No processes in this extension. All three classes are continuant-like
entities (information artifacts and agents).

### 4. Missing Disjointness
**Status**: Fixed in axiom plan.

EnergyVariable, EnergyDataset, and EnergyAgent are declared pairwise
disjoint. A Variable cannot be a Dataset or an Agent.

### 5. Circular Definitions
**Status**: Clean.

No definition references its own term.

### 6. Quality-as-Class
**Status**: N/A.

Facet values are SKOS Concepts in existing schemes, not modeled as OWL
classes. The Value Partition pattern (via qb:codeList) is correctly
applied.

### 7. Information-Physical Conflation
**Status**: Clean.

All three classes are information/social entities. No physical entities
mixed in.

### 8. Orphan Classes
**Status**: Clean.

All classes have a named parent.

### 9. Polysemy
**Status**: Clean.

No term has multiple meanings. "Variable" could theoretically be ambiguous
(programming variable vs statistical variable), but the class name
"EnergyVariable" and parent "StatisticalVariable" make the intended sense
unambiguous.

### 10. Domain/Range Overcommitment
**Status**: Mitigated.

- `hasVariable`: domain/range declared in OWL. Safe because both classes
  are sevocab-specific — no external entity would accidentally gain a type.
- `dct:publisher`: NOT redeclared globally. Modeled as a local restriction
  on EnergyDataset. This avoids overcommitting DCTerms' property.
- Facet dimensions: Local OWL restrictions on EnergyVariable, not global
  domain/range. SHACL handles validation.

## Additional Checks

### Blank Node Proliferation
The DataStructureDefinition uses 7 blank-node ComponentSpecifications.
This is standard Data Cube practice and acceptable — these are structural
connectors not referenced externally.

### Namespace Collision
The 7 facet dimension property names (measuredProperty, domainObject, etc.)
live in the sevocab namespace. These do NOT collide with any existing
sevocab terms because existing terms are SKOS Concepts (nouns), while these
are properties (verb-like). Verified: no existing sevocab entity uses
these local names.
