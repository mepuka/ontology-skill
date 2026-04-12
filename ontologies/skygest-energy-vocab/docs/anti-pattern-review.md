# Skygest Energy Vocabulary — Anti-Pattern Review

**Date**: 2026-04-11
**Phase**: 3 — Conceptualization
**Model reviewed**: `docs/conceptual-model.yaml`

---

## Review Results

| # | Anti-Pattern | Status | Notes |
|---|-------------|--------|-------|
| 1 | Singleton hierarchy | **Pass** | Wind has 2 children, Coal has 1, NaturalGas has 1 — see finding below |
| 2 | Role-type confusion | **Pass** | No roles in the model. Concepts are reference data, not role-bearing entities |
| 3 | Process-object confusion | **Pass** | No processes modeled. All concepts are information entities |
| 4 | Missing disjointness | **N/A** | SKOS concepts are individuals, not classes. Disjointness doesn't apply. Scheme membership (CQ-023) serves the same purpose |
| 5 | Circular definitions | **Pass** | No EquivalentTo axioms. skos:broader is acyclic by construction (2-level max) |
| 6 | Quality-as-class | **Pass** | Value partition is expressed via SKOS ConceptSchemes, not OWL class hierarchies |
| 7 | Information-physical conflation | **Pass** | All concepts are explicitly information entities (GDC). SSSOM mappings to OEO bridge to physical-entity classes cleanly |
| 8 | Orphan classes | **Pass** | Only one OWL class (SurfaceFormEntry) — it's under owl:Thing, which is acceptable for a single utility class |
| 9 | Polysemy | **Pass** | No overloaded terms. Each concept has a single clear definition |
| 10 | Domain/range overcommitment | **Pass** | No OWL domain/range declared. All constraints via SHACL |
| 11 | Individuals in T-box | **Pass** | Concept individuals go in the main .ttl (they ARE the vocabulary). SurfaceFormEntry instances go in a separate provenance module |
| 12 | Complement overuse | **Pass** | No complements used |
| 13 | False is-a from OO | **Pass** | No OO inheritance patterns. skos:broader is a conceptual narrowing, not implementation inheritance |
| 14 | System blueprint | **Pass** | Model reflects domain concepts (energy technologies, statistic types), not system artifacts. SurfaceFormEntry could be flagged here — see finding below |
| 15 | Technical perspective | **Pass** | Concepts driven by CQs and domain analysis, not storage concerns |
| 16 | Mixing individuals/classes | **Pass** | Clean separation: SKOS concepts are individuals, SurfaceFormEntry is a class. No dual-typing |

## Findings

### Finding 1: Singleton hierarchies under Coal and NaturalGas

**Anti-pattern #1 (Singleton Hierarchy)**

- `Coal` has only one child: `BrownCoal`
- `NaturalGas` has only one child: `GasCcgt`

**Assessment**: Acceptable. These are not lazy taxonomy design — they
reflect genuine domain structure:
- Coal legitimately has sub-types (brown coal, hard coal, anthracite),
  but only lignite/brown coal appears in the cold-start corpus.
  Additional children (HardCoal) can be added when demand requires.
- NaturalGas has sub-types by plant technology (CCGT, OCGT, peaker),
  but only CCGT appears in the cold-start corpus.

**Decision**: Keep as-is. The singletons are demand-driven, not structural
defects. Document as "growth points" for future expansion.

### Finding 2: SurfaceFormEntry as potential system blueprint

**Anti-pattern #14 (System Blueprint)**

`SurfaceFormEntry` mirrors the `SurfaceFormEntryValue<Canonical>` TypeScript
type in skygest-cloudflare. Is this a system blueprint leaking into the
domain model?

**Assessment**: No — this is the right call. SurfaceFormEntry is an
information artifact (provenance record) that exists independently of any
particular system. The fact that it aligns with the TypeScript type is a
feature, not a bug — the ontology and the product code model the same
real-world concept (a surface form annotation). The N-ary relation pattern
was chosen for SPARQL queryability (CQ-012 through CQ-014), not because
of the TypeScript schema.

**Decision**: Keep. The alignment with the product code is intentional
and correct.

### Finding 3: MeasuredProperty / StatisticType polysemy risk (SKY-309)

**Anti-pattern #9 (Polysemy)**

Three MeasuredProperty concepts share names with StatisticType concepts:
- "price" (sevocab:Price in StatisticType, sevocab:PriceMeasure in MeasuredProperty)
- "share" (sevocab:Share in StatisticType, sevocab:ShareMeasure in MeasuredProperty)
- "count" (sevocab:Count in StatisticType, sevocab:CountMeasure in MeasuredProperty)

**Assessment**: Controlled polysemy, not a defect. The same English word
"price" correctly names two distinct concepts in two different schemes:
- StatisticType "price" = the TYPE of statistic (as opposed to flow, stock)
- MeasuredProperty "price" = WHAT is being measured (the price of something)

The IRI disambiguation (CD-008) prevents technical collision. The same
surface form correctly fires BOTH facets in different lookup tables — this
is the intended cross-scheme overlap behavior (CD-006).

**Decision**: Keep. Document in CD-008. IRIs use suffix disambiguation;
prefLabels match canonical strings.

### Finding 4: DomainObject / TechnologyOrFuel overlap (SKY-309)

**Anti-pattern #9 (Polysemy)**

Multiple DomainObject concepts overlap with TechnologyOrFuel concepts:
- "solar photovoltaic" / "solar PV"
- "wind turbine" / "wind"
- "battery storage" / "battery"
- "heat pump" / "heat pump"

**Assessment**: Controlled overlap, not polysemy. These are genuinely
different facets that happen to share referents:
- TechnologyOrFuel "solar PV" = the technology PRODUCING energy
- DomainObject "solar photovoltaic" = the thing BEING MEASURED

Example: "Installed solar PV capacity" has technologyOrFuel=solar PV
AND domainObject=solar photovoltaic. But "Solar electricity generation"
has technologyOrFuel=solar PV AND domainObject=electricity (different!).

**Decision**: Keep. Document in CD-007. Surface forms should be
differentiated where possible to reduce noise.

### Finding 5: DomainObjectScheme mixed abstraction levels (SKY-309)

**Anti-pattern: granularity inconsistency (not in standard 16, but relevant)**

DomainObjectScheme mixes broad sectors ("electricity", "transport",
"industry") with specific equipment ("lithium-ion battery pack",
"offshore wind turbine"). This is a granularity inconsistency.

**Assessment**: Acceptable and intentional. The scheme's purpose is to
match the domainObject field on Variables, which itself mixes
granularities because Variables represent different kinds of statistics.
Forcing uniform granularity would lose discriminating power. The
sub-groups in the conceptual model (energy carriers, sectors, technology
domains, product-specific) document the granularity layers clearly.

**Decision**: Keep. The conceptual model's sub-grouping provides
organizational clarity without constraining the flat SKOS scheme.

## Summary (updated 2026-04-12)

**Zero unresolved anti-patterns.** Five findings reviewed and accepted:
1. Singleton hierarchies are demand-driven growth points (not defects)
2. SurfaceFormEntry alignment with TypeScript is intentional (not a system blueprint leak)
3. MeasuredProperty/StatisticType name overlap is controlled polysemy with IRI disambiguation (CD-008)
4. DomainObject/TechnologyOrFuel overlap is by design — different facets, same referents (CD-007)
5. DomainObjectScheme mixed granularity is intentional and documented via sub-groups
