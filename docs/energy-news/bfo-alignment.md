# BFO Alignment — Energy News Ontology

## Alignment Strategy

Per scope constraint: **"Minimal BFO alignment where natural; not forced."**

BFO (ISO 21838-2) is used as a reference frame for documenting ontological
commitments, not as an imported dependency. BFO categories are recorded in the
glossary for each class but no `owl:imports` of BFO is declared. This keeps the
ontology lightweight while maintaining interoperability documentation.

## Top-Level Class Alignment

### EnergyTopic (and all subclasses)

**BFO Category**: None (classification category)

**Rationale**: EnergyTopic and its 55+ subclasses (Solar, Wind, Nuclear, etc.)
are topical classification categories used to tag news articles. They function
as a controlled vocabulary modeled as OWL classes to enable `rdfs:subClassOf`
inference chains (e.g., an article covering Solar also covers Renewable).

These are not entities that exist in the physical world — they are categories
in a classification scheme. They do not naturally map to any BFO category:
- Not Continuants (they don't persist through time as individual entities)
- Not Occurrents (they don't unfold in time)
- Not GDCs (they are universals/types, not information content entities)

The closest BFO-adjacent pattern would be modeling them as instances of
IAO:0000030 (information content entity) representing concept definitions,
but this would add complexity without benefit for our CQs. We model them
as OWL classes and annotate with SKOS properties.

### Article

**BFO Category**: Generically Dependent Continuant (BFO:0000031)

**Rationale**: An Article is an information content entity — a piece of
news content that can be concretized in multiple physical forms (web page,
PDF, cached copy). It depends on physical carriers for its existence but
can migrate between them. This aligns with the IAO:0000030 (information
content entity) pattern, which is a subclass of GDC.

**schema.org alignment**: `enews:Article rdfs:subClassOf schema:NewsArticle`

### Publication

**BFO Category**: Object (BFO:0000030)

**Rationale**: A Publication (e.g., Bloomberg, Reuters, Canary Media) is a
news media organization — a persistent entity with identity that survives
changes in staff and content. Per BFO 2020, organizations are modeled as
Objects (not Object Aggregates), since their identity persists through
membership changes.

**schema.org alignment**: `enews:Publication rdfs:subClassOf schema:NewsMediaOrganization`

### Post

**BFO Category**: Generically Dependent Continuant (BFO:0000031)

**Rationale**: A Bluesky Post is an information content entity — text and
metadata created by an author on the Bluesky platform. It is concretized
in the AT Protocol data store and potentially cached in multiple locations.

**schema.org alignment**: `enews:Post owl:equivalentClass schema:SocialMediaPosting`

### Author

**BFO Category**: Generically Dependent Continuant (BFO:0000031)

**Rationale**: In our ontology, Author represents a Bluesky account
(handle + profile), not a natural person. A Bluesky account is an
information entity — it exists in the AT Protocol identity system and
depends on infrastructure for its existence. One natural person may have
multiple Author accounts.

Note: This is a deliberate divergence from schema.org's `Person` (which is
an Independent Continuant / Object). We declare `rdfs:subClassOf schema:Person`
as a loose alignment, acknowledging the impedance mismatch.

**SIOC alignment**: `enews:Author owl:equivalentClass sioc:UserAccount`

### Feed

**BFO Category**: Generically Dependent Continuant (BFO:0000031)

**Rationale**: A Bluesky Feed is a curated algorithm/configuration that
defines a collection of posts. It is an information artifact — a set of
rules concretized in the AT Protocol feed generator system.

### Organization

**BFO Category**: Object (BFO:0000030)

**Rationale**: Organizations mentioned in energy news (CATL, Tesla, FERC,
OPEC, etc.) are persistent entities with identity. Per BFO 2020, organizations
are Objects. Their identity persists through changes in membership, location,
and leadership.

**schema.org alignment**: `enews:Organization owl:equivalentClass schema:Organization`

### GeographicEntity

**BFO Category**: Site (BFO:0000029)

**Rationale**: Countries, regions, and states are immaterial entities that
serve as geographic containers. In BFO, a Site is a three-dimensional
immaterial entity bounded by material entities or fiat boundaries. Countries
and regions fit this category — they are bounded spaces, not material
objects themselves.

**schema.org alignment**: `enews:GeographicEntity rdfs:subClassOf schema:Place`

## Summary Table

| Class | BFO Category | BFO ID | Alignment Strength |
|-------|-------------|--------|-------------------|
| EnergyTopic (+ subtypes) | None | — | N/A (classification category) |
| Article | GDC | BFO:0000031 | Natural |
| Publication | Object | BFO:0000030 | Natural |
| Post | GDC | BFO:0000031 | Natural |
| Author | GDC | BFO:0000031 | Natural (account, not person) |
| Feed | GDC | BFO:0000031 | Natural |
| Organization | Object | BFO:0000030 | Natural (per BFO 2020) |
| GeographicEntity | Site | BFO:0000029 | Natural |
