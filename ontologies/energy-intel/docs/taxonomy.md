# Taxonomy — `energy-intel`

**Authored:** 2026-04-22 by `ontology-conceptualizer`
**Consumer:** `ontology-architect` (hierarchy to realise in OWL).

Every local class appears under its asserted parents, with the BFO upper category rolled up at every level. Node format:

```
local:Class  :  direct-parent(s)  :  bfo-root
```

Multiple asserted parents are shown comma-separated. Classes with dual-parent membership that could cause reasoner friction under OWL 2 DL are annotated `[MI]` and discussed in § 3.

---

## 1. Module `agent`

```
bfo:Entity
└── bfo:Continuant
    ├── bfo:IndependentContinuant
    │   ├── bfo:MaterialEntity
    │   │   ├── bfo:Object
    │   │   │   └── foaf:Person
    │   │   │       └── ei:Expert                        : foaf:Person : bfo:Object : bfo:MaterialEntity
    │   │   └── bfo:ObjectAggregate (BFO_0000027)
    │   │       └── ei:Organization [MI]                 : foaf:Organization, bfo:ObjectAggregate
    │   └── (foaf:Organization is also under bfo:ObjectAggregate via scope-ratified dual parent)
    └── bfo:SpecificallyDependentContinuant
        └── bfo:RealizableEntity
            └── bfo:Role (BFO_0000023)
                ├── ei:PublisherRole                     : bfo:Role : bfo:RealizableEntity
                └── ei:DataProviderRole                  : bfo:Role : bfo:RealizableEntity
```

**Sibling-disjointness obligations:**
- `ei:PublisherRole owl:disjointWith ei:DataProviderRole` — an Organization *bears* both distinct roles, but an individual role-instance is one or the other. (Architect asserts the disjointness.)
- `ei:Expert` and `ei:Organization` are not siblings (different BFO leaves — Object vs ObjectAggregate) but a sanity disjointness (`ei:Expert owl:disjointWith ei:Organization`) is recommended to catch accidental conflation.

---

## 2. Module `media`

```
iao:InformationContentEntity (GDC)
├── iao:Document (IAO_0000310)
│   ├── ei:Post                           : iao:Document : bfo:GDC
│   └── ei:PodcastEpisode [MI]            : iao:Document, ei:Conversation : bfo:GDC
├── iao:Image (IAO_0000101)
│   ├── ei:Chart [MI]                           : iao:Image, ei:MediaAttachment
│   ├── ei:Screenshot [MI]                      : iao:Image, ei:MediaAttachment
│   └── ei:GenericImageAttachment [MI]          : iao:Image, ei:MediaAttachment
├── iao:TextualEntity (IAO_0000300)
│   └── ei:Excerpt [MI]                   : iao:TextualEntity, ei:MediaAttachment
├── ei:Conversation (abstract)             : iao:ICE : bfo:GDC
│   ├── ei:SocialThread                   : ei:Conversation
│   └── ei:PodcastEpisode [MI]            : ei:Conversation, iao:Document   (also listed above; single class, two parents)
├── ei:MediaAttachment (abstract)          : iao:ICE : bfo:GDC
│   ├── ei:Chart [MI]
│   ├── ei:Screenshot [MI]
│   ├── ei:Excerpt [MI]
│   └── ei:GenericImageAttachment [MI]
├── ei:EvidenceSource (abstract, primitive): iao:ICE : bfo:GDC    (§ conceptual-model 8.1)
│   ├── ei:Post                           (asserted subclass)
│   ├── ei:MediaAttachment                (asserted subclass — covers Chart/Screenshot/Excerpt/Image)
│   └── ei:PodcastSegment                 (asserted subclass)
└── ei:PodcastSegment                      : iao:ICE : bfo:GDC
```

**Sibling-disjointness obligations:**
- `ei:Chart`, `ei:Screenshot`, `ei:Excerpt`, `ei:GenericImageAttachment` are pairwise disjoint under `ei:MediaAttachment` (a chart is not a screenshot, a screenshot is not a text excerpt). Architect writes `AllDisjointClasses` over the four.
- `ei:Post owl:disjointWith ei:MediaAttachment` — a post is the container, an attachment is the content bundled into it. Sibling under `ei:EvidenceSource`; disjointness supports reasoner classification.
- `ei:Post`, `ei:MediaAttachment`, `ei:PodcastSegment` pairwise disjoint under `ei:EvidenceSource`.
- `ei:Conversation` subclasses (`ei:SocialThread`, `ei:PodcastEpisode`) — disjoint. A social-media thread is not a podcast episode.
- `ei:Post owl:disjointWith ei:PodcastEpisode` — neighbour-domain sanity.
- `ei:Post owl:disjointWith ei:PodcastSegment` — the evidence-source trio are all disjoint.
- `ei:Chart owl:disjointWith ei:Post` — cross-branch sanity.

---

## 3. Module `measurement`

```
iao:InformationContentEntity (GDC)
├── ei:CanonicalMeasurementClaim          : iao:ICE : bfo:GDC     [disjoint Observation]
├── ei:Observation                        : iao:ICE : bfo:GDC     [disjoint CMC]
├── ei:Variable                           : iao:ICE : bfo:GDC
└── ei:Series                             : iao:ICE : bfo:GDC

bfo:TemporalRegion (BFO_0000008)
└── ei:ClaimTemporalWindow                : bfo:TemporalRegion   (flipped 2026-04-22)
```

**Sibling-disjointness obligations:**
- `ei:CanonicalMeasurementClaim owl:disjointWith ei:Observation` — the core tagged-union axiom (scope § Decisions D7). **Ratified.**
- `ei:Variable`, `ei:Series`, `ei:CanonicalMeasurementClaim`, `ei:Observation` should all be pairwise disjoint (a Variable is not a claim, not an observation; a Series is not a Variable). Architect writes `AllDisjointClasses` over the four.
- `ei:ClaimTemporalWindow` is disjoint with the other four **by BFO category** (it's a `bfo:TemporalRegion`, the others are `iao:ICE` / `bfo:GDC` — different branches under `bfo:Entity`). The explicit `DisjointClasses` assertion is optional but recommended for reasoner clarity; architect decides.

---

## 4. Module `data`

```
owl:Thing
├── dcat:Catalog              (imported)
├── dcat:CatalogRecord        (imported)
├── dcat:Dataset              (imported)
│   └── dcat:DatasetSeries    (imported — dcat 3 subclass path, verify on architect's import)
├── dcat:Distribution         (imported)
└── dcat:DataService          (imported)
```

No local DCAT subclasses. Extension properties only (`ei:hasSeries`, `ei:publishedInDataset`); see `property-design.md`.

---

## 5. Multiple inheritance `[MI]` review

Every `[MI]` node has two asserted parents. OWL 2 DL allows arbitrary multiple inheritance; the concern is *whether the reasoner classifies consistently*. Review:

| Class | Parents | Consistency argument | Flag |
|---|---|---|---|
| `ei:Organization` | `foaf:Organization`, `bfo:ObjectAggregate` | `foaf:Organization` is a FOAF-defined class with no axioms restricting its BFO placement. `bfo:ObjectAggregate` is a `bfo:MaterialEntity` subclass. Both are "thing-like material entities"; no axiomatic conflict. | OK |
| `ei:PodcastEpisode` | `iao:Document`, `ei:Conversation` | `iao:Document` is `iao:ICE`; `ei:Conversation` is `iao:ICE` (local). The intersection (`iao:ICE ⊓ iao:ICE = iao:ICE`) is consistent. No BFO-level conflict. | OK |
| `ei:Chart` | `iao:Image`, `ei:MediaAttachment` | `iao:Image` is `iao:ICE`. `ei:MediaAttachment` is `iao:ICE` (local). Consistent. | OK |
| `ei:Screenshot` | `iao:Image`, `ei:MediaAttachment` | Same as Chart. | OK |
| `ei:GenericImageAttachment` | `iao:Image`, `ei:MediaAttachment` | Same. | OK |
| `ei:Excerpt` | `iao:TextualEntity`, `ei:MediaAttachment` | `iao:TextualEntity` is `iao:ICE` (confirmed active IAO_0000300 via OLS4 probe 2026-04-22). `ei:MediaAttachment` is `iao:ICE`. Consistent. | OK |

**Recommendation:** no MI collapse needed. The reasoner will accept all six dual-parent classes under OWL 2 DL. Architect's `robot reason` pass is the verification gate.

One precaution for the architect:
- Do NOT assert `ei:MediaAttachment owl:disjointWith iao:Document`. `ei:Post` is `iao:Document`, `ei:MediaAttachment` is not — but the two branches are siblings under `iao:ICE`, not disjoint-by-BFO. Asserting disjointness would drive a reasoner contradiction if anyone later wants a class that is both (e.g., a social-media post that IS itself the evidence, as Chart/Excerpt do). Keep them siblings, not disjoint.

---

## 6. Parent-path preview tables (architect copy-paste starter)

These are the full path preview for each local class. Architect copies this table into the ROBOT template starter.

### 6.1 agent

| Class | Parent 1 | Parent 2 | Notes |
|---|---|---|---|
| `ei:Expert` | `foaf:Person` | — | |
| `ei:Organization` | `foaf:Organization` | `bfo:ObjectAggregate` | [MI] dual-parent |
| `ei:PublisherRole` | `bfo:Role` | — | |
| `ei:DataProviderRole` | `bfo:Role` | — | |

### 6.2 media

| Class | Parent 1 | Parent 2 | Notes |
|---|---|---|---|
| `ei:Post` | `iao:Document` | `ei:EvidenceSource` | |
| `ei:Conversation` | `iao:InformationContentEntity` | — | abstract |
| `ei:SocialThread` | `ei:Conversation` | — | |
| `ei:PodcastEpisode` | `iao:Document` | `ei:Conversation` | [MI] |
| `ei:PodcastSegment` | `iao:InformationContentEntity` | `ei:EvidenceSource` | |
| `ei:MediaAttachment` | `iao:InformationContentEntity` | `ei:EvidenceSource` | abstract |
| `ei:Chart` | `iao:Image` | `ei:MediaAttachment` | [MI] |
| `ei:Screenshot` | `iao:Image` | `ei:MediaAttachment` | [MI] |
| `ei:Excerpt` | `iao:TextualEntity` | `ei:MediaAttachment` | [MI] |
| `ei:GenericImageAttachment` | `iao:Image` | `ei:MediaAttachment` | [MI] |
| `ei:EvidenceSource` | `iao:InformationContentEntity` | — | abstract, primitive (see conceptual-model § 8.1) |

### 6.3 measurement

| Class | Parent 1 | Parent 2 | Notes |
|---|---|---|---|
| `ei:CanonicalMeasurementClaim` | `iao:InformationContentEntity` | — | disjoint Observation |
| `ei:Observation` | `iao:InformationContentEntity` | — | disjoint CMC |
| `ei:Variable` | `iao:InformationContentEntity` | — | thin |
| `ei:Series` | `iao:InformationContentEntity` | — | thin |
| `ei:ClaimTemporalWindow` | `bfo:TemporalRegion` (BFO_0000008) | — | flipped 2026-04-22 |

### 6.4 data

No local classes. Imported DCAT classes only.
