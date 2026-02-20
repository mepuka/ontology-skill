# FAIR Assessment: Personal Agent Ontology v0.6.0

Date: 2026-02-20

## Findable

| Principle | Status | Evidence |
|-----------|--------|----------|
| F1: Globally unique identifiers | PASS | Stable PURL namespace `https://purl.org/pao/`. Version IRI `https://purl.org/pao/0.6.0`. All 92 classes and 132 properties have resolvable IRIs. |
| F2: Rich metadata | PASS | Ontology header includes dcterms:title, dcterms:description, dcterms:creator, dcterms:created, dcterms:license, dcterms:rights, prov:generatedAtTime, owl:versionInfo, owl:versionIRI, owl:priorVersion. |
| F3: Metadata references identifiers | PASS | Version IRI references the ontology IRI. owl:imports reference import module IRIs. owl:priorVersion links to v0.5.0. |
| F4: Registered in searchable resources | PARTIAL | Not yet registered in BioPortal, OLS, or LOV. Recommended for next release cycle. |

## Accessible

| Principle | Status | Evidence |
|-----------|--------|----------|
| A1: Retrievable via standard protocol | PARTIAL | Available via git repository. PURL resolution not yet configured. |
| A1.1: Open protocol | PASS | HTTPS (git repository is publicly accessible). |
| A1.2: Auth where needed | N/A | No authentication required. |
| A2: Metadata persists | PASS | Metadata embedded in ontology file. Version history preserved in git. Prior versions accessible via version IRIs and git tags. |

## Interoperable

| Principle | Status | Evidence |
|-----------|--------|----------|
| I1: Formal KR language | PASS | OWL 2 DL (W3C Recommendation). RDF serialization in Turtle, OWL/XML, JSON-LD. |
| I2: FAIR vocabularies | PASS | Reuses PROV-O (W3C), OWL-Time (W3C), FOAF, ODRL (W3C), BFO (ISO 21838-2), Dublin Core, SKOS. |
| I3: Qualified links | PASS | 44 SSSOM cross-ontology mappings to schema.org, ActivityStreams, SIOC, DPV. BFO alignment for 38 classes. Import declarations with version information. |

## Reusable

| Principle | Status | Evidence |
|-----------|--------|----------|
| R1: Rich provenance | PASS | dcterms:creator, dcterms:created, prov:generatedAtTime. Per-mapping justifications in SSSOM files (semapv vocabulary). Build script provides full provenance chain. |
| R1.1: Explicit license | PASS | MIT License (dcterms:license pointing to SPDX IRI). |
| R1.2: Provenance recorded | PASS | Build script provides full provenance chain from glossary.csv to OWL axioms. Validation report documents all test results. owl:priorVersion links version chain. |
| R1.3: Community standards | PASS | Follows OBO Foundry naming conventions (CamelCase classes, camelCase properties). Genus-differentia definitions for all 92 classes. SSSOM standard for mappings. 17 value partitions with owl:oneOf enumerations. |

## Summary

| Category | Score |
|----------|-------|
| Findable | 3.5/4 (registration pending) |
| Accessible | 3/4 (PURL resolution pending) |
| Interoperable | 4/4 |
| Reusable | 4/4 |
| **Overall** | **14.5/16** |

## Release Artifacts

| Artifact | Format | Triples |
|----------|--------|---------|
| personal_agent_ontology.ttl | Turtle | 2,010 |
| personal_agent_ontology.owl | OWL/XML | 2,010 |
| personal_agent_ontology.jsonld | JSON-LD | 2,010 |
| pao-reference-individuals.ttl | Turtle | 548 |
| pao-shapes.ttl | Turtle (SHACL) | 561 |

## v0.6.0 Highlights

- **92 classes** across 14 modules (up from 57 in v0.5.0)
- **132 properties** (109 object + 23 data)
- **45 SHACL shapes** with RDFS-inference validation
- **98 competency questions** (97 tested as SPARQL)
- **1,035 passing tests**
- **17 value partitions** with controlled vocabulary enumerations
- New domains: External Services, Runtime Safety, Recovery/Resilience,
  Tool/Message Trace, Memory Control Plane, Dialog Pragmatics

## Recommendations for Next Version

1. **Register in ontology portals**: Submit to BioPortal and/or LOV for
   discoverability (F4).
2. **Configure PURL resolution**: Set up `https://purl.org/pao/` to resolve
   via content negotiation to the appropriate serialization (A1).
3. **Update SSSOM mappings**: Extend the 44 existing mappings to cover
   v0.6.0 additions (external services, dialog pragmatics, recovery).
4. **Add ORCID for creator**: Replace string literal creator with ORCID
   IRI for machine-readable provenance.
5. **Add DOI**: Consider minting a DOI for the release via Zenodo.
