# Energy News Ontology — Changelog

## v0.2.0 (2026-02-12)

**Release type**: MINOR (backward-compatible additions)
**Prior version**: v0.1.0 (2026-02-11)

### New

- **SocialMediaPlatform class** — models platforms as named individuals
  (Bluesky, Twitter/X) rather than subclasses. Enables multi-platform
  support per DD-008.
- **onPlatform object property** — links AuthorAccount and Feed to their
  SocialMediaPlatform. Functional property, range `SocialMediaPlatform`.
  Domain intentionally omitted to avoid type inference conflicts with
  AllDisjointClasses.
- **Platform individuals** — `enews:Bluesky`, `enews:Twitter` with
  `rdfs:label`, `skos:definition`, and `skos:altLabel` annotations.
- **CQ-017** — "Which platforms have the most energy news posts?"
- **CQ-018** — "Which authors share energy news on a given platform?"
- **CQ-019** — "Which publication published an article based on its URL
  domain?" Derives `publishedBy` from URL domain extraction.
- **SHACL SPARQL constraint** — first SPARQL-based SHACL constraint;
  validates that an Article's URL domain matches its Publication's
  `siteDomain`.
- **URL-Publication linking** — `publishedBy` now derived from URL domain
  extraction in the build script (was hardcoded).
- **Sample data labels** — all ABox individuals (articles, authors, posts)
  now have `rdfs:label`.
- **Feed EnergyX** — cross-platform feed on Twitter for testing
  multi-platform queries.

### Changed

- Ontology description updated: "Bluesky social media posts" →
  "social media posts" (platform-agnostic).
- Class definitions updated: AuthorAccount, Post, Feed changed from
  Bluesky-specific to platform-agnostic wording.
- `handle` property definition: "Bluesky handle" → "handle or username".
- `AuthorAccount` HasKey changed from `(handle)` to `(handle, onPlatform)`
  — composite key ensures uniqueness across platforms.
- AllDisjointClasses expanded from 8 to 9 members (added
  SocialMediaPlatform).
- AllDifferent: +1 group (Bluesky, Twitter platform individuals).

### Fixed

- **B-001**: `description` property `rdfs:range xsd:string` conflicted with
  `Literal(text, lang="en")` producing `rdf:langString`. HermiT correctly
  flagged inconsistency. Fixed by removing `lang="en"` from description
  literals.
- **W-001**: 10 ABox sample individuals lacked `rdfs:label`, causing ROBOT
  report `missing_label` ERRORs. Fixed by adding labels in the build
  script.

### Metrics

| Metric | v0.1.0 | v0.2.0 | Delta |
|--------|--------|--------|-------|
| Domain classes | 8 | 9 | +1 |
| Object properties | 7 | 8 | +1 |
| Data properties | 6 | 6 | — |
| Topic individuals | 66 | 66 | — |
| Platform individuals | 0 | 2 | +2 |
| TBox triples | 170 | 192 | +22 |
| Ref individuals triples | 740 | 757 | +17 |
| ABox data triples | 75 | 99 | +24 |
| Total triples (merged) | 985 | 1048 | +63 |
| CQ tests (pytest) | 85 | 99 | +14 |
| HermiT consistency | PASS | PASS | — |
| ROBOT report (custom) | 0 ERR | 0 ERR | — |
| SHACL conformance | PASS | PASS | — |
