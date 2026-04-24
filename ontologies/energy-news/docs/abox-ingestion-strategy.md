# ABox Ingestion Strategy for the Energy News Ontology

**Ontology:** Energy News Ontology v0.3.0 (`enews:`)
**Namespace:** `http://example.org/ontology/energy-news#`
**Data namespace:** `http://example.org/data/`
**Date:** 2026-02-28
**Status:** Strategy Document

---

## 1. Data-to-Ontology Mapping Analysis

### 1.1 Source Data Profile

The Bluesky data store (via SkyGent CLI) contains:

- **36,714 posts** from **5,234 authors** across **33 sources** (11 feeds + 22 author handles)
- **Date range:** 2018-11-15 to 2026-02-28
- **Top authors by volume:** reuters.com (5,155), electrek.co (1,702), canarymedia.com (1,655), theguardian.com (1,545), nytimes.com (1,510)

Each post is a JSON object with the following field paths:

```
uri, author, text, createdAt, embedSummary.type,
embedSummary.external.{uri, title, description, thumb},
embedSummary.imageSummary.{imageCount, hasAltText, thumbnailUrl},
embedSummary.record.{uri, authorHandle},
embedSummary (video — empty object)
```

### 1.2 Embed Type Distribution (827-post sample)

| Embed Type | Count | Percentage | Ontology Mapping |
|---|---|---|---|
| `external` | 554 | 67.0% | `enews:EmbeddedExternalLink` via `enews:hasEmbed` |
| `images` | 148 | 17.9% | `enews:MediaAttachment` via `enews:hasMedia` |
| `none` | 72 | 8.7% | Text-only `enews:Post` |
| `video` | 30 | 3.6% | Unmappable (empty `videoSummary` object) |
| `record` | 19 | 2.3% | `enews:isReplyTo` (quote post) |
| `record_with_media` | 4 | 0.5% | `enews:isReplyTo` + `enews:hasMedia` |

### 1.3 Comprehensive Field-by-Field Mapping Table

| # | Field Path | Present | Target Class | Target Property | Handling | Notes |
|---|---|---|---|---|---|---|
| 1 | `uri` | 827/827 | `enews:Post` | (IRI subject) | IRI_MINT | AT-URI `at://did:plc:XXX/app.bsky.feed.post/YYY` -- extract rkey `YYY` for IRI |
| 2 | `author` | 827/827 | `enews:AuthorAccount` | `enews:postedBy` | LOOKUP | Bluesky handle string; lookup or create `enews:AuthorAccount`; link via `enews:postedBy` |
| 3 | `text` | 827/827 | `enews:Post` | `enews:postText` | LITERAL_COPY | Full post body as `xsd:string` |
| 4 | `createdAt` | 827/827 | `enews:Post` | `enews:createdAt` | LITERAL_COPY | ISO 8601 to `xsd:dateTime` |
| 5 | `embedSummary.type` | 755/827 | -- | -- | SKIP | Discriminator only; used in code dispatch |
| 6 | `embedSummary.external.uri` | 554/827 | `enews:EmbeddedExternalLink` | `enews:linkUri` | LITERAL_COPY | External URL as `xsd:anyURI` |
| 7 | `embedSummary.external.title` | 554/827 | `enews:EmbeddedExternalLink` | `enews:linkTitle` | LITERAL_COPY | Preview title as `xsd:string` |
| 8 | `embedSummary.external.description` | 554/827 | `enews:EmbeddedExternalLink` | `enews:linkDescription` | LITERAL_COPY | Preview description as `xsd:string` |
| 9 | `embedSummary.external.thumb` | ~420/554 | `enews:EmbeddedExternalLink` | `enews:thumbnailUri` | LITERAL_COPY | Thumbnail URL as `xsd:anyURI`; optional (~76% of external embeds) |
| 10 | `embedSummary.imageSummary.imageCount` | 148/827 | `enews:MediaAttachment` | -- | CODE_ITERATE | Create N `enews:MediaAttachment` individuals (1..imageCount) |
| 11 | `embedSummary.imageSummary.hasAltText` | 148/827 | `enews:MediaAttachment` | `enews:altText` | GAP | Boolean flag only; actual alt text not in payload |
| 12 | `embedSummary.imageSummary.thumbnailUrl` | 148/827 | `enews:MediaAttachment` | `enews:mediaUri` | LITERAL_COPY | Thumbnail URL as `xsd:anyURI` |
| 13 | `embedSummary.record.uri` | 19/827 | `enews:Post` | `enews:isReplyTo` | IRI_MINT | Quoted post AT-URI; mint IRI for target Post |
| 14 | `embedSummary.record.authorHandle` | 19/827 | -- | -- | SKIP | Informational; parent URI encodes author |
| 15 | `embedSummary.video` (empty) | 30/827 | `enews:MediaAttachment` | -- | SKIP | Empty object; no URI, MIME type, or duration available |
| 16 | `record_with_media.record` | 4/827 | `enews:Post` | `enews:isReplyTo` | CONDITIONAL | Process if `record.uri` is present |
| 17 | `record_with_media.imageSummary` | 4/827 | `enews:MediaAttachment` | `enews:mediaUri` | LITERAL_COPY | Same handling as images embed type |

**Handling key:**
- **LITERAL_COPY** -- direct copy to datatype property with appropriate XSD type
- **IRI_MINT** -- value becomes or resolves to an individual IRI
- **LOOKUP** -- resolve against existing reference individuals, create if absent
- **CODE_ITERATE** -- programmatic expansion (e.g., create N individuals from count)
- **SKIP** -- no ontology target; metadata-only or discriminator field
- **GAP** -- ontology property exists but data is insufficient
- **CONDITIONAL** -- process only if prerequisite data is present

### 1.4 Coverage Gap Analysis

#### A) Post data fields with NO ontology mapping

| Field | Issue | Impact |
|---|---|---|
| `embedSummary.imageSummary.hasAltText` | Boolean flag only; actual alt text not in payload | Cannot populate `enews:altText` (`xsd:string`) without AT Protocol image fetch |
| `embedSummary.video` | Empty object `{}` with no metadata | Cannot create `enews:MediaAttachment` for video -- no URI, MIME type, or duration |
| `embedSummary.record.authorHandle` | Informational only | Redundant; author is encoded in the quoted post's AT-URI |
| Engagement counts | `likeCount`, `replyCount`, `repostCount` exist in the TBox but are NOT present in the pre-processed JSON payload | Properties `enews:likeCount`, `enews:replyCount`, `enews:repostCount` remain unpopulated |

#### B) Ontology classes with NO direct data source (require NLP/LLM extraction)

| Ontology Class | Data Gap | Extraction Approach | Feasibility |
|---|---|---|---|
| `enews:Article` | Partial via `enews:EmbeddedExternalLink` metadata; full Article needs URL fetch for `enews:publishedDate`, `enews:publishedBy` | Domain extraction + optional HTTP fetch | YELLOW |
| `enews:Publication` | Not directly present; derivable from `embedSummary.external.uri` domain | Domain extraction from `enews:linkUri` | GREEN |
| `enews:Organization` | Mentioned in post text but not structured | spaCy NER + reference individual matching | YELLOW |
| `enews:EnergyProject` | Mentioned in post text ("Gorgon CCS", "Hornsea 3") | LLM extraction from text | RED |
| `enews:EnergyTechnology` | Partial via hashtags/keywords (#CCS, solar, hydrogen) | Keyword + LLM extraction | YELLOW |
| `enews:EnergyTopic` linkage | Hashtags + keyword presence; 92 SKOS concepts exist as targets | Hashtag mapping + keyword matching + LLM classification | YELLOW |
| `enews:GeographicEntity` | Location mentions in text ("UK", "California", "Texas") | spaCy NER + gazetteer matching | YELLOW |
| `enews:RegulatoryBody` | Mentioned in text ("DOE", "CPUC", "FERC") | NER + alias matching against reference individuals | YELLOW |
| `enews:GridZone` | Mentioned in text ("PJM", "ERCOT", "MISO") | Alias matching against `enews:org_pjm`, `enews:org_ercot`, `enews:org_miso` | GREEN |
| `enews:RenewableInstallation` | Individual projects mentioned in text | LLM extraction | RED |
| `enews:PowerPlant` | Power plants mentioned but not extracted with capacity/fuel data | LLM extraction | RED |
| `enews:CapacityMeasurement` | Capacity values in text ("500 MW", "2 GW") | Regex extraction for `\d+(\.\d+)?\s*(MW|GW|MWh|GWh)` | YELLOW |
| `enews:PriceDataPoint` | Price mentions ("$76/barrel", "5 cents/kWh") | Regex extraction for currency + numeric patterns | YELLOW |
| `enews:PolicyInstrument` | Policy references ("IRA", "REPowerEU") | LLM extraction + reference matching | RED |
| `enews:MarketInstrument` | Market mechanisms ("PPA", "REC", "carbon credit") | Keyword + LLM extraction | RED |
| `enews:EnergyEvent` | Events implicit in content ("COP30", "outage") | LLM classification | RED |
| `enews:ProjectStatus` | Status inferred from text context | LLM classification against 6 reference individuals | RED |

### 1.5 Example Turtle Snippets by Embed Type

#### Type 1: Text-only post (no embed, 72/827 posts)

```turtle
@prefix enews: <http://example.org/ontology/energy-news#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix data: <http://example.org/data/> .

data:post/3lbw4qlfg2b2y a enews:Post ;
    enews:postText "Our response to the Energy Security Strategy..."^^xsd:string ;
    enews:createdAt "2022-04-07T14:31:04.000Z"^^xsd:dateTime ;
    enews:postedBy data:author/chrisstark_bsky_social .

data:author/chrisstark_bsky_social a enews:AuthorAccount ;
    enews:handle "chrisstark.bsky.social"^^xsd:string ;
    enews:onPlatform enews:Bluesky .
```

#### Type 2: External link embed (554/827 posts)

```turtle
@prefix enews: <http://example.org/ontology/energy-news#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix data: <http://example.org/data/> .

data:post/3lbphn3qxk22l a enews:Post ;
    enews:postText "Some big news for UK #CCS: @Draxnews is working on a second carbon capture project..."^^xsd:string ;
    enews:createdAt "2020-06-24T11:55:27.000Z"^^xsd:dateTime ;
    enews:postedBy data:author/garethsimkins_bsky_social ;
    enews:hasEmbed data:embed/3lbphn3qxk22l .

data:embed/3lbphn3qxk22l a enews:EmbeddedExternalLink ;
    enews:linkUri "https://www.endsreport.com/article/1687613/drax-pioneers-negative-emissions-sse-plans-ccs-power-station"^^xsd:anyURI ;
    enews:linkTitle "Drax pioneers negative emissions while SSE plans CCS power station"^^xsd:string ;
    enews:linkDescription "Britain's largest power station will capture carbon dioxide..."^^xsd:string .

data:author/garethsimkins_bsky_social a enews:AuthorAccount ;
    enews:handle "garethsimkins.bsky.social"^^xsd:string ;
    enews:onPlatform enews:Bluesky .
```

With derived Article and Publication (Phase 2 enrichment):

```turtle
data:post/3lbphn3qxk22l enews:sharesArticle data:article/endsreport_1687613 .

data:article/endsreport_1687613 a enews:Article ;
    enews:url "https://www.endsreport.com/article/1687613/drax-pioneers-negative-emissions-sse-plans-ccs-power-station"^^xsd:anyURI ;
    enews:title "Drax pioneers negative emissions while SSE plans CCS power station"^^xsd:string ;
    enews:description "Britain's largest power station will capture carbon dioxide..."^^xsd:string ;
    enews:publishedBy data:pub/endsreport_com ;
    enews:coversTopic enews:CarbonCapture .

data:pub/endsreport_com a enews:Publication ;
    enews:siteDomain "endsreport.com"^^xsd:string .
```

#### Type 3: Images embed (148/827 posts)

```turtle
@prefix enews: <http://example.org/ontology/energy-news#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix data: <http://example.org/data/> .

data:post/3lfsrh6kenj2u a enews:Post ;
    enews:postText "Uses of biomass need to change over time..."^^xsd:string ;
    enews:createdAt "2018-11-15T16:14:06.000Z"^^xsd:dateTime ;
    enews:postedBy data:author/thecccuk_bsky_social ;
    enews:hasMedia data:media/3lfsrh6kenj2u_1 ,
                   data:media/3lfsrh6kenj2u_2 .

data:media/3lfsrh6kenj2u_1 a enews:MediaAttachment ;
    enews:mediaUri "https://cdn.bsky.app/img/feed_thumbnail/plain/did:plc:co6xmmhz3vm5cxmv5bdathxa/bafkreigosvqg4wbyx6i2lgum35wfll2kmez47u7wrgonj6o6qih56ankpm@jpeg"^^xsd:anyURI ;
    enews:mimeType "image/jpeg"^^xsd:string .

data:media/3lfsrh6kenj2u_2 a enews:MediaAttachment ;
    enews:mimeType "image/jpeg"^^xsd:string .

data:author/thecccuk_bsky_social a enews:AuthorAccount ;
    enews:handle "thecccuk.bsky.social"^^xsd:string ;
    enews:onPlatform enews:Bluesky .
```

Note: Only `thumbnailUrl` for the first image is available; additional images have no individual URIs in the pre-processed payload. The `imageCount` field drives the creation of N blank-node or sequentially-numbered `MediaAttachment` individuals.

#### Type 4: Quote post / record embed (19/827 posts)

```turtle
@prefix enews: <http://example.org/ontology/energy-news#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix data: <http://example.org/data/> .

data:post/3k7scfwbsbo2g a enews:Post ;
    enews:postText "A little news from me earlier. See the whole thread for more details, but this is the TLDR."^^xsd:string ;
    enews:createdAt "2023-09-20T03:37:21.381Z"^^xsd:dateTime ;
    enews:postedBy data:author/aleach_ca ;
    enews:isReplyTo data:post/3k7rfvrtlb42r .

data:post/3k7rfvrtlb42r a enews:Post ;
    enews:postedBy data:author/aleach_ca .

data:author/aleach_ca a enews:AuthorAccount ;
    enews:handle "aleach.ca"^^xsd:string ;
    enews:onPlatform enews:Bluesky .
```

#### Type 5: Video embed (30/827 posts)

```turtle
@prefix enews: <http://example.org/ontology/energy-news#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix data: <http://example.org/data/> .

# Video posts produce only Post triples -- no MediaAttachment possible
# because embedSummary.video is an empty object {} with no metadata.
data:post/3lr2ll35yhk2t a enews:Post ;
    enews:postText "Federal immigration agents in riot gear squared off..."^^xsd:string ;
    enews:createdAt "2025-06-08T00:17:05.005Z"^^xsd:dateTime ;
    enews:postedBy data:author/nytimes_com .
```

#### Type 6: Record with media (4/827 posts)

```turtle
@prefix enews: <http://example.org/ontology/energy-news#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix data: <http://example.org/data/> .

data:post/3mdbrdnlufs2l a enews:Post ;
    enews:postText "A thread of MAGA protesting..."^^xsd:string ;
    enews:createdAt "2026-01-25T22:22:25.788Z"^^xsd:dateTime ;
    enews:postedBy data:author/sarahlongwell25_bsky_social ;
    enews:hasMedia data:media/3mdbrdnlufs2l_1 .

data:media/3mdbrdnlufs2l_1 a enews:MediaAttachment ;
    enews:mediaUri "https://cdn.bsky.app/img/feed_thumbnail/plain/did:plc:yj2yzzvnylclt3ghwjnkcxxz/bafkreignfu2sqkgvker6cwnyg633n6sa3sx5omnorkfxhk43a36o46spry@jpeg"^^xsd:anyURI ;
    enews:mimeType "image/jpeg"^^xsd:string .

# Note: record.uri is empty in all 4 record_with_media samples,
# so enews:isReplyTo cannot be asserted here.
```

### 1.6 Triple Count Estimates

| Post Type | Count (est. full store) | Triples/Post | Subtotal |
|---|---|---|---|
| Text-only | ~3,200 | 4 | 12,800 |
| External link | ~24,600 | 9 (post + embed + article stub) | 221,400 |
| Images | ~6,600 | 5 + 2*N (N=avg 1.5 images) | 52,800 |
| Video | ~1,300 | 4 | 5,200 |
| Record (quote) | ~850 | 6 | 5,100 |
| Record with media | ~180 | 7 | 1,260 |
| AuthorAccount (unique) | ~5,234 | 3 | 15,702 |
| Publication (unique) | ~200 est. | 2 | 400 |
| **Phase 1 subtotal** | | | **~314,662** |
| NLP-derived entities (Phase 2-3) | ~50K est. | 3-5 avg | ~175,000 |
| **Grand total** | | | **~490,000** |

---

## 2. Entity Extraction Strategy

### 2.1 Extraction Tier Classification

Entity extraction falls into four confidence tiers based on the data source and technique required:

| Tier | Technique | Confidence | Human Review | Entities |
|---|---|---|---|---|
| **T1: Direct** | Field copy, IRI mint | 99%+ | None | `enews:Post`, `enews:AuthorAccount`, `enews:EmbeddedExternalLink`, `enews:MediaAttachment`, `enews:SocialMediaPlatform` |
| **T2: Derived** | Regex, domain extraction | 95%+ | Spot-check | `enews:Publication`, `enews:Article` (stub), `enews:CapacityMeasurement`, `enews:PriceDataPoint` |
| **T3: NER** | spaCy NER + gazetteer | 80-90% | Sample audit | `enews:Organization`, `enews:GeographicEntity`, `enews:RegulatoryBody`, `enews:GridZone` |
| **T4: LLM** | Claude API extraction | 70-85% | Required | `enews:EnergyProject`, `enews:EnergyTechnology`, `enews:PolicyInstrument`, `enews:MarketInstrument`, `enews:EnergyEvent`, `enews:RenewableInstallation`, `enews:PowerPlant`, `enews:ProjectStatus` |

### 2.2 Per-Entity Extraction Approach

#### T1: Direct Field Mapping (no extraction needed)

**enews:Post** -- One-to-one from JSON. Every post object creates exactly one `enews:Post` individual.

**enews:AuthorAccount** -- Deduplicate by `handle` string. Create on first encounter, reuse on subsequent posts. All accounts linked to `enews:Bluesky` via `enews:onPlatform`.

**enews:EmbeddedExternalLink** -- Created for every `embedSummary.type == "external"` post. Four properties directly from the JSON.

**enews:MediaAttachment** -- Created for `images` and `record_with_media` embed types. The `imageCount` field drives creation of N individuals. Only the first image has a thumbnail URL; subsequent images get no `enews:mediaUri` (SHACL `enews:MediaAttachmentShape` requires `sh:minCount 1` for `enews:mediaUri`, so only the first image passes validation).

#### T2: Derived Entities (regex/domain extraction)

**enews:Publication** -- Extract domain from `embedSummary.external.uri`:

```python
from urllib.parse import urlparse

def extract_publication_domain(link_uri: str) -> str:
    """Extract canonical domain from external link URI."""
    parsed = urlparse(link_uri)
    domain = parsed.hostname or ""
    if domain.startswith("www."):
        domain = domain[4:]
    return domain
```

Match against existing `enews:Publication` reference individuals via `enews:siteDomain`:
- `enews:pub_reuters` ("reuters.com"), `enews:pub_electrek` ("electrek.co"), `enews:pub_guardian` ("theguardian.com"), etc.
- New domains create new `enews:Publication` instances with `enews:siteDomain` and an `rdfs:label` derived from the domain.

**enews:Article (stub)** -- For every external link embed, create a minimal Article linked to the Post via `enews:sharesArticle`:
- `enews:url` = `embedSummary.external.uri`
- `enews:title` = `embedSummary.external.title`
- `enews:description` = `embedSummary.external.description`
- `enews:publishedBy` = resolved Publication from domain
- `enews:coversTopic` = deferred to T3/T4 extraction (REQUIRED by `enews:ArticleShape`)

**enews:CapacityMeasurement** -- Regex extraction from post text:

```python
import re

CAPACITY_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(MW|GW|MWh|GWh|kW|kWh)\b",
    re.IGNORECASE,
)

def extract_capacities(text: str) -> list[dict]:
    """Extract capacity measurements from post text."""
    results = []
    for match in CAPACITY_PATTERN.finditer(text):
        value_str = match.group(1).replace(",", "")
        unit = match.group(2).upper()
        value_mw = float(value_str)
        # Normalize to MW
        if unit == "GW":
            value_mw *= 1000
        elif unit in ("KW", "KWH"):
            value_mw /= 1000
        results.append({"value_mw": value_mw, "unit": unit, "raw": match.group(0)})
    return results
```

**enews:PriceDataPoint** -- Regex extraction for currency + numeric patterns:

```python
PRICE_PATTERN = re.compile(
    r"\$\s*(\d+(?:[.,]\d+)?)\s*(?:per\s+|/)?(barrel|MWh|kWh|ton(?:ne)?)\b",
    re.IGNORECASE,
)
```

#### T3: NER-Based Extraction (spaCy + gazetteer)

**enews:Organization** -- Two-pass extraction:
1. **spaCy NER** (`en_core_web_trf` model, `ORG` entity type) on `enews:postText`
2. **Alias matching** against reference individual `skos:altLabel` values:
   - `"DOE"` / `"Department of Energy"` --> `enews:org_doe`
   - `"CPUC"` / `"California PUC"` --> `enews:org_cpuc`
   - `"PJM"` --> `enews:org_pjm`
   - `"Ørsted"` / `"Orsted"` --> `enews:org_orsted`
3. **New organizations** not matching reference data get a new IRI minted with `enews:org_` prefix.

**enews:GeographicEntity** -- Two-pass extraction:
1. **spaCy NER** (`GPE`, `LOC` entity types)
2. **Gazetteer matching** against reference individuals:
   - `"California"` / `"CA"` --> `enews:geo_california`
   - `"Texas"` / `"TX"` --> `enews:geo_texas`
   - `"UK"` / `"Britain"` --> `enews:geo_uk`
   - `"EU"` / `"European Union"` --> `enews:geo_eu`
   - etc. (10 reference geographic entities)
3. New locations get `enews:geo_` prefix IRIs.

**enews:RegulatoryBody** -- Subset of Organization extraction; classify using `enews:RegulatoryBody` type when the entity is one of the 3 existing reference individuals (`enews:org_doe`, `enews:org_cpuc`, `enews:org_interior`) or matches regulatory body keywords ("commission", "department", "agency", "FERC", "NERC", "EPA").

**enews:GridZone** -- Keyword matching against known grid operators:
- Match `"PJM"`, `"ERCOT"`, `"MISO"`, `"CAISO"`, `"SPP"`, `"NYISO"` in post text
- Link to corresponding `enews:Organization` via `enews:operatedBy`

#### T4: LLM-Based Extraction (Claude API)

For entities requiring semantic understanding of post text, use a structured LLM extraction prompt. Batch posts for cost efficiency.

**Prompt template for batch extraction:**

```
You are an energy sector entity extractor. For each post, extract:

1. ENERGY_TOPICS: Which of these 92 topics does the post discuss?
   [list of enews:EnergyTopic labels and altLabels]

2. ORGANIZATIONS: Company/agency names mentioned
3. GEOGRAPHIC_ENTITIES: Countries, states, regions
4. ENERGY_PROJECTS: Named infrastructure projects
5. ENERGY_TECHNOLOGIES: Specific technologies (not just topics)
6. POLICY_INSTRUMENTS: Named policies, laws, regulations
7. PROJECT_STATUS: If a project is mentioned, what is its status?
   One of: planning, under_review, under_construction, operational, mothballed, decommissioned

Return JSON for each post.
```

**Cost estimate for full extraction:**
- 36,714 posts at ~200 tokens input + ~100 tokens output each
- Batched at 10 posts/request = ~3,672 API calls
- At Claude Haiku pricing: ~$1.10 per 1M input tokens
- Estimated total: ~$8-12 for full corpus extraction

### 2.3 EnergyTopic Linkage Strategy

The ontology contains 92 `enews:EnergyTopic` SKOS concepts organized in a 2-level hierarchy under `enews:EnergyTopicScheme` with 23 top-level concepts:

```
enews:Renewable
  ├── enews:Solar, enews:Wind, enews:OffshoreWind, enews:Hydro, enews:Geothermal
enews:Fossil
  ├── enews:Coal, enews:NaturalGas, enews:Oil
enews:EnergyStorage
  ├── enews:BatteryRecycling, enews:LongDurationStorage, enews:PumpedHydroStorage
enews:CarbonCapture
  ├── enews:DirectAirCapture
enews:Hydrogen
  ├── enews:GreenHydrogen, enews:FuelCell
enews:Nuclear
  ├── enews:SMR, enews:Fusion
... (23 top-level, 69 narrower concepts)
```

**Three-layer topic matching:**

1. **Hashtag mapping** (highest confidence) -- Map `#solar` --> `enews:Solar`, `#CCS` --> `enews:CarbonCapture`, `#hydrogen` --> `enews:Hydrogen`, etc. Build a lookup table from `skos:altLabel` values:

```python
def build_hashtag_topic_map(topic_graph: rdflib.Graph) -> dict[str, rdflib.URIRef]:
    """Build hashtag-to-EnergyTopic lookup from SKOS altLabels."""
    ENEWS = rdflib.Namespace("http://example.org/ontology/energy-news#")
    SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
    mapping = {}
    for topic in topic_graph.subjects(rdflib.RDF.type, ENEWS.EnergyTopic):
        for label in topic_graph.objects(topic, SKOS.altLabel):
            key = str(label).lower().strip("#").strip()
            mapping[key] = topic
        for label in topic_graph.objects(topic, rdflib.RDFS.label):
            key = str(label).lower()
            mapping[key] = topic
    return mapping
```

2. **Keyword matching** (medium confidence) -- Scan `enews:postText` for `skos:altLabel` strings. For example, a post containing "battery storage" matches `enews:EnergyStorage` (altLabel: "battery storage", "BESS", "storage").

3. **LLM classification** (for ambiguous posts) -- Posts that match no hashtag or keyword are sent to the LLM extraction pipeline with the full topic list. The LLM selects 1-3 most relevant topics.

**Article topic requirement:** `enews:ArticleShape` has `sh:minCount 1` on `enews:coversTopic`. Every Article must have at least one topic. If no topic can be determined, assign the broadest applicable top-level topic or flag for human review.

---

## 3. ETL Pipeline Architecture

### 3.1 Pipeline Overview

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Stage 1     │     │  Stage 2     │     │  Stage 3     │     │  Stage 4     │
│  EXTRACT     │────▶│  TRANSFORM   │────▶│  ENRICH      │────▶│  LOAD        │
│  (SkyGent)   │     │  (Direct)    │     │  (NLP/LLM)   │     │  (Oxigraph)  │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
    No LLM              No LLM            NER + LLM             No LLM

  JSON posts       Post, Author,       Organization,         Named graphs,
  from store       Embed, Media,       GeographicEntity,     SHACL validation,
                   Publication,        EnergyProject,        CQ test suite
                   Article (stub)      Topic linkage
```

### 3.2 Stage 1: Extract (No LLM)

**Input:** SkyGent CLI data store (JSON)
**Output:** Normalized post records

```python
from pathlib import Path
import json

def extract_posts(store_path: Path) -> list[dict]:
    """Load all posts from SkyGent store."""
    posts = json.loads(store_path.read_text())
    # Normalize: ensure all expected fields exist
    for post in posts:
        post.setdefault("embedSummary", None)
        post.setdefault("author", "unknown")
        post.setdefault("text", "")
    return posts
```

**Batch strategy:** Process all 36,714 posts in memory (est. ~100 MB JSON). No pagination needed.

### 3.3 Stage 2: Transform -- Direct Mapping (No LLM)

Transform each JSON post into RDF triples using `rdflib`. This stage handles all T1 and T2 entities.

```python
import rdflib
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD, SKOS
from urllib.parse import urlparse

ENEWS = Namespace("http://example.org/ontology/energy-news#")
DATA = Namespace("http://example.org/data/")

def transform_post(g: Graph, post: dict, author_cache: dict, pub_cache: dict) -> None:
    """Transform a single Bluesky post JSON into RDF triples."""
    # Extract rkey from AT-URI
    rkey = post["uri"].rsplit("/", 1)[-1]
    post_iri = DATA[f"post/{rkey}"]

    # Post
    g.add((post_iri, RDF.type, ENEWS.Post))
    g.add((post_iri, ENEWS.postText, Literal(post["text"], datatype=XSD.string)))
    g.add((post_iri, ENEWS.createdAt, Literal(post["createdAt"], datatype=XSD.dateTime)))

    # Author (deduplicated)
    handle = post["author"]
    author_slug = handle.replace(".", "_").replace("-", "_")
    author_iri = DATA[f"author/{author_slug}"]
    g.add((post_iri, ENEWS.postedBy, author_iri))
    if handle not in author_cache:
        g.add((author_iri, RDF.type, ENEWS.AuthorAccount))
        g.add((author_iri, ENEWS.handle, Literal(handle, datatype=XSD.string)))
        g.add((author_iri, ENEWS.onPlatform, ENEWS.Bluesky))
        author_cache[handle] = author_iri

    embed = post.get("embedSummary")
    if not embed:
        return

    embed_type = embed.get("type")

    # External link
    if embed_type == "external":
        ext = embed.get("external", {})
        embed_iri = DATA[f"embed/{rkey}"]
        g.add((post_iri, ENEWS.hasEmbed, embed_iri))
        g.add((embed_iri, RDF.type, ENEWS.EmbeddedExternalLink))
        if ext.get("uri"):
            g.add((embed_iri, ENEWS.linkUri, Literal(ext["uri"], datatype=XSD.anyURI)))
        if ext.get("title"):
            g.add((embed_iri, ENEWS.linkTitle, Literal(ext["title"], datatype=XSD.string)))
        if ext.get("description"):
            g.add((embed_iri, ENEWS.linkDescription, Literal(ext["description"], datatype=XSD.string)))
        if ext.get("thumb"):
            g.add((embed_iri, ENEWS.thumbnailUri, Literal(ext["thumb"], datatype=XSD.anyURI)))

        # Derive Publication from domain
        if ext.get("uri"):
            domain = extract_publication_domain(ext["uri"])
            if domain and domain not in pub_cache:
                pub_iri = DATA[f"pub/{domain.replace('.', '_')}"]
                g.add((pub_iri, RDF.type, ENEWS.Publication))
                g.add((pub_iri, ENEWS.siteDomain, Literal(domain, datatype=XSD.string)))
                pub_cache[domain] = pub_iri

            # Article stub
            article_iri = DATA[f"article/{rkey}"]
            g.add((post_iri, ENEWS.sharesArticle, article_iri))
            g.add((article_iri, RDF.type, ENEWS.Article))
            g.add((article_iri, ENEWS.url, Literal(ext["uri"], datatype=XSD.anyURI)))
            if ext.get("title"):
                g.add((article_iri, ENEWS.title, Literal(ext["title"], datatype=XSD.string)))
            if ext.get("description"):
                g.add((article_iri, ENEWS.description, Literal(ext["description"], datatype=XSD.string)))
            if domain in pub_cache:
                g.add((article_iri, ENEWS.publishedBy, pub_cache[domain]))

    # Images
    elif embed_type in ("images", "record_with_media"):
        img_summary = embed.get("imageSummary", {})
        image_count = img_summary.get("imageCount", 0)
        thumbnail = img_summary.get("thumbnailUrl")
        for i in range(1, image_count + 1):
            media_iri = DATA[f"media/{rkey}_{i}"]
            g.add((post_iri, ENEWS.hasMedia, media_iri))
            g.add((media_iri, RDF.type, ENEWS.MediaAttachment))
            g.add((media_iri, ENEWS.mimeType, Literal("image/jpeg", datatype=XSD.string)))
            if i == 1 and thumbnail:
                g.add((media_iri, ENEWS.mediaUri, Literal(thumbnail, datatype=XSD.anyURI)))

    # Record (quote post)
    if embed_type in ("record", "record_with_media"):
        record = embed.get("record", {})
        quoted_uri = record.get("uri")
        if quoted_uri:
            quoted_rkey = quoted_uri.rsplit("/", 1)[-1]
            quoted_iri = DATA[f"post/{quoted_rkey}"]
            g.add((post_iri, ENEWS.isReplyTo, quoted_iri))
```

**Batch execution:**

```python
def transform_all(posts: list[dict]) -> Graph:
    """Transform all posts to RDF. Runs ~36K posts in <30 seconds."""
    g = Graph()
    g.bind("enews", ENEWS)
    g.bind("data", DATA)
    author_cache: dict[str, URIRef] = {}
    pub_cache: dict[str, URIRef] = {}

    for post in posts:
        transform_post(g, post, author_cache, pub_cache)

    return g
```

### 3.4 Stage 3: Enrich -- NLP/LLM Extraction

This stage adds T3 and T4 entities. It operates on the graph produced by Stage 2.

**Sub-stage 3a: EnergyTopic linkage (No LLM for high-confidence matches)**

```python
def link_topics_to_articles(
    g: Graph,
    topic_map: dict[str, URIRef],
) -> int:
    """Link Articles to EnergyTopics via hashtag/keyword matching on associated Post text."""
    linked = 0
    for post, _, article in g.triples((None, ENEWS.sharesArticle, None)):
        text = str(g.value(post, ENEWS.postText) or "").lower()
        title = str(g.value(article, ENEWS.title) or "").lower()
        combined = f"{text} {title}"
        matched_topics = set()
        for keyword, topic_iri in topic_map.items():
            if keyword in combined:
                matched_topics.add(topic_iri)
        for topic_iri in matched_topics:
            g.add((article, ENEWS.coversTopic, topic_iri))
            linked += 1
    return linked
```

**Sub-stage 3b: spaCy NER extraction**

```python
import spacy

def extract_ner_entities(
    g: Graph,
    nlp: spacy.Language,
    org_gazetteer: dict[str, URIRef],
    geo_gazetteer: dict[str, URIRef],
) -> None:
    """Run spaCy NER on all post texts to extract Organizations and GeographicEntities."""
    for post_iri in g.subjects(RDF.type, ENEWS.Post):
        text = str(g.value(post_iri, ENEWS.postText) or "")
        if not text:
            continue
        doc = nlp(text)
        article = g.value(post_iri, ENEWS.sharesArticle)
        if not article:
            continue

        for ent in doc.ents:
            if ent.label_ == "ORG":
                org_iri = resolve_or_mint_org(ent.text, org_gazetteer, g)
                g.add((article, ENEWS.mentionsOrganization, org_iri))
            elif ent.label_ in ("GPE", "LOC"):
                geo_iri = resolve_or_mint_geo(ent.text, geo_gazetteer, g)
                g.add((article, ENEWS.hasGeographicFocus, geo_iri))
```

**Sub-stage 3c: LLM batch extraction**

For T4 entities, batch 10 posts per LLM call:

```python
import anthropic

async def llm_extract_batch(
    posts: list[dict],
    topic_labels: list[str],
) -> list[dict]:
    """Extract structured entities from a batch of posts using Claude."""
    client = anthropic.AsyncAnthropic()
    prompt = build_extraction_prompt(posts, topic_labels)
    response = await client.messages.create(
        model="claude-haiku-4-20250414",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return parse_extraction_response(response.content[0].text)
```

### 3.5 Stage 4: Load (No LLM)

Load the enriched graph into Oxigraph (see Section 6).

### 3.6 Incremental Sync Strategy

SkyGent provides incremental sync for new posts. The pipeline handles this with:

1. **Delta detection:** Compare `uri` field against existing `data:post/{rkey}` IRIs in Oxigraph
2. **Append-only processing:** New posts go through Stages 2-4; existing posts are not reprocessed
3. **Author/Publication dedup:** Check `author_cache` and `pub_cache` against Oxigraph before creating new individuals
4. **Named graph isolation:** New batch loaded into a timestamped named graph (see Section 6)

```python
def find_new_posts(posts: list[dict], store: pyoxigraph.Store) -> list[dict]:
    """Filter posts not already in the triple store."""
    existing_rkeys = set()
    for result in store.query("SELECT ?rkey WHERE { ?p a enews:Post . BIND(REPLACE(STR(?p), '.*/post/', '') AS ?rkey) }"):
        existing_rkeys.add(str(result["rkey"]))
    return [p for p in posts if p["uri"].rsplit("/", 1)[-1] not in existing_rkeys]
```

### 3.7 Error Handling and Recovery

| Failure Mode | Recovery Strategy |
|---|---|
| Malformed JSON post | Log and skip; continue batch |
| Missing required field (`uri`, `author`, `createdAt`) | Log warning; skip post |
| spaCy NER failure | Degrade gracefully; skip NER for that post |
| LLM API timeout/error | Retry with exponential backoff (3 attempts); skip batch on permanent failure |
| SHACL validation failure | Log failing individual; continue loading valid triples |
| Oxigraph write failure | Atomic transaction per batch; rollback on failure |

---

## 4. IRI Minting and Deduplication

### 4.1 IRI Naming Scheme

All ABox IRIs use the data namespace `http://example.org/data/` with entity-type-specific path segments. Reference individuals from the ontology retain the `enews:` namespace.

| Entity Type | IRI Pattern | Example | Minting Strategy |
|---|---|---|---|
| `enews:Post` | `data:post/{rkey}` | `data:post/3lbphn3qxk22l` | Extract rkey from AT-URI: `at://did:plc:XXX/app.bsky.feed.post/{rkey}` |
| `enews:AuthorAccount` | `data:author/{slug}` | `data:author/garethsimkins_bsky_social` | Slugify handle: replace `.` and `-` with `_` |
| `enews:EmbeddedExternalLink` | `data:embed/{rkey}` | `data:embed/3lbphn3qxk22l` | Same rkey as parent Post (1:1 relationship) |
| `enews:MediaAttachment` | `data:media/{rkey}_{n}` | `data:media/3lfsrh6kenj2u_1` | Post rkey + sequential image index |
| `enews:Article` | `data:article/{rkey}` | `data:article/3lbphn3qxk22l` | Same rkey as source Post; deduplicated by `enews:url` |
| `enews:Publication` | `data:pub/{domain_slug}` | `data:pub/reuters_com` | Slugify canonical domain: replace `.` with `_` |
| `enews:Organization` | `data:org/{slug}` | `data:org/drax` | Slugify normalized name; check reference individuals first |
| `enews:GeographicEntity` | `data:geo/{slug}` | `data:geo/north_yorkshire` | Slugify name; check reference individuals first |
| `enews:EnergyProject` | `data:project/{slug}` | `data:project/gorgon_ccs` | Slugify project name from LLM extraction |
| `enews:CapacityMeasurement` | `data:capacity/{post_rkey}_{n}` | `data:capacity/3lbphn3qxk22l_1` | Post rkey + extraction index |
| `enews:PriceDataPoint` | `data:price/{post_rkey}_{n}` | `data:price/3lbphn3qxk22l_1` | Post rkey + extraction index |
| `enews:EnergyEvent` | `data:event/{slug}` | `data:event/cop30` | Slugify event name |

**Slugification function:**

```python
import re
import unicodedata

def slugify(name: str) -> str:
    """Convert a name to a URL-safe IRI local name."""
    # Normalize unicode
    normalized = unicodedata.normalize("NFKD", name)
    # Remove non-ASCII
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    # Lowercase, replace non-alphanum with underscore
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_name.lower())
    return slug.strip("_")
```

### 4.2 Reference Individual Resolution

Before minting new IRIs for Organizations, GeographicEntities, and RegulatoryBodies, check against existing reference individuals using multi-strategy matching:

```python
def build_alias_index(ref_graph: Graph) -> dict[str, URIRef]:
    """Build a normalized alias -> IRI index from reference individuals."""
    index = {}
    for entity_class in [ENEWS.Organization, ENEWS.GeographicEntity, ENEWS.RegulatoryBody]:
        for entity in ref_graph.subjects(RDF.type, entity_class):
            # Index by rdfs:label
            for label in ref_graph.objects(entity, RDFS.label):
                index[str(label).lower()] = entity
            # Index by skos:altLabel
            for alt in ref_graph.objects(entity, SKOS.altLabel):
                index[str(alt).lower()] = entity
    return index
```

**Existing reference individuals to match against:**

| Type | Count | Examples |
|---|---|---|
| `enews:Organization` | 15 | `enews:org_pjm` ("PJM"), `enews:org_doe` ("DOE"), `enews:org_orsted` ("Orsted"/"Ørsted") |
| `enews:RegulatoryBody` | 3 | `enews:org_doe`, `enews:org_cpuc`, `enews:org_interior` |
| `enews:GeographicEntity` | 10 | `enews:geo_california` ("CA"), `enews:geo_texas` ("TX"), `enews:geo_uk` ("Britain"/"UK") |
| `enews:Publication` | 10 | `enews:pub_reuters` ("reuters.com"), `enews:pub_electrek` ("electrek.co") |
| `enews:SocialMediaPlatform` | 2 | `enews:Bluesky`, `enews:Twitter` |
| `enews:ProjectStatus` | 6 | `enews:status_Planning`, `enews:status_UnderReview`, `enews:status_UnderConstruction`, `enews:status_Operational`, `enews:status_Mothballed`, `enews:status_Decommissioned` |
| `enews:EnergyTopic` | 92 | All SKOS concepts in `enews:EnergyTopicScheme` |

### 4.3 Deduplication Strategy

#### Article Deduplication

Multiple posts can share the same article URL. The `owl:hasKey (enews:url)` declaration on `enews:Article` means URL is the identity key.

```python
def deduplicate_articles(g: Graph) -> int:
    """Merge Article individuals with the same enews:url."""
    url_to_articles: dict[str, list[URIRef]] = {}
    for article in g.subjects(RDF.type, ENEWS.Article):
        url = g.value(article, ENEWS.url)
        if url:
            url_str = str(url)
            url_to_articles.setdefault(url_str, []).append(article)

    merged = 0
    for url_str, articles in url_to_articles.items():
        if len(articles) > 1:
            canonical = articles[0]
            for duplicate in articles[1:]:
                # Redirect all references to the duplicate -> canonical
                for s, p, _ in g.triples((None, None, duplicate)):
                    g.remove((s, p, duplicate))
                    g.add((s, p, canonical))
                # Merge properties from duplicate into canonical
                for _, p, o in g.triples((duplicate, None, None)):
                    if not g.value(canonical, p):
                        g.add((canonical, p, o))
                    g.remove((duplicate, p, o))
                merged += 1
    return merged
```

#### Author Deduplication

`enews:AuthorAccount` has `owl:hasKey (enews:handle enews:onPlatform)`. Since all current data is from Bluesky, the handle alone is the effective dedup key. The in-memory `author_cache` dict in Stage 2 prevents duplicates at creation time.

#### Organization Variant Name Handling

Organizations appear under many names. The alias index handles common variants:
- `"DOE"` / `"Department of Energy"` / `"U.S. Department of Energy"` --> `enews:org_doe`
- `"Ørsted"` / `"Orsted"` / `"Ørsted A/S"` --> `enews:org_orsted`
- `"PJM"` / `"PJM Interconnection"` --> `enews:org_pjm`

For LLM-extracted organizations not in the alias index, apply fuzzy matching as a second pass:

```python
from rapidfuzz import fuzz

def fuzzy_match_org(
    name: str,
    alias_index: dict[str, URIRef],
    threshold: int = 85,
) -> URIRef | None:
    """Fuzzy match an organization name against the alias index."""
    name_lower = name.lower()
    best_score = 0
    best_match = None
    for alias, iri in alias_index.items():
        score = fuzz.ratio(name_lower, alias)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = iri
    return best_match
```

---

## 5. Validation and Quality Strategy

### 5.1 SHACL Validation Pipeline

The ontology defines 15 SHACL shapes in `shapes/energy-news-shapes.ttl`. Validation runs after each pipeline stage to catch errors early.

| Shape | Target Class | Required Properties | Stage Validated |
|---|---|---|---|
| `enews:PostShape` | `enews:Post` | `enews:postedBy` (1..1), `enews:postText` (0..1), `enews:createdAt` (0..1), `enews:sharesArticle` (0..1) | Stage 2 |
| `enews:AuthorAccountShape` | `enews:AuthorAccount` | `enews:handle` (1..1, `xsd:string`), `enews:onPlatform` (1..1, class `enews:SocialMediaPlatform`) | Stage 2 |
| `enews:EmbeddedExternalLinkShape` | `enews:EmbeddedExternalLink` | `enews:linkUri` (1..1, `xsd:anyURI`), `enews:linkTitle` (0..1), `enews:linkDescription` (0..1), `enews:thumbnailUri` (0..1) | Stage 2 |
| `enews:MediaAttachmentShape` | `enews:MediaAttachment` | `enews:mediaUri` (1..1, `xsd:anyURI`), `enews:mimeType` (0..1), `enews:altText` (0..1) | Stage 2 |
| `enews:ArticleShape` | `enews:Article` | `enews:url` (1..1, `xsd:anyURI`), `enews:coversTopic` (1..*, class `enews:EnergyTopic`), `enews:title` (0..1), `enews:description` (0..1), `enews:publishedBy` (0..1), `enews:publishedDate` (0..1). Also has a SPARQL constraint checking URL domain matches Publication `siteDomain`. | Stage 3 (after topic linkage) |
| `enews:PublicationShape` | `enews:Publication` | `enews:siteDomain` (1..1, `xsd:string`) | Stage 2 |
| `enews:FeedShape` | `enews:Feed` | `rdfs:label` (1..*), `enews:onPlatform` (1..1, class `enews:SocialMediaPlatform`) | Reference data (pre-loaded) |
| `enews:SocialMediaPlatformShape` | `enews:SocialMediaPlatform` | `rdfs:label` (1..*) | Reference data (pre-loaded) |
| `enews:EnergyTopicInstanceShape` | `enews:EnergyTopic` | `rdfs:label` (1..*), `skos:definition` (1..*), `skos:inScheme` (1..*) | Reference data (pre-loaded) |
| `enews:OrganizationShape` | `enews:Organization` | `rdfs:label` (1..*), `skos:definition` (1..*) | Stage 3 |
| `enews:GeographicEntityShape` | `enews:GeographicEntity` | `rdfs:label` (1..*) | Stage 3 |
| `enews:EnergyProjectShape` | `enews:EnergyProject` | `rdfs:label` (1..*), `enews:hasStatus` (0..1, class `enews:ProjectStatus`), `enews:hasCapacity` (0..*, class `enews:CapacityMeasurement`) | Stage 3 |
| `enews:PowerPlantShape` | `enews:PowerPlant` | `rdfs:label` (1..*), `enews:hasTechnology` (0..*, class `enews:EnergyTechnology`), `enews:operatedBy` (0..*, class `enews:Organization`) | Stage 3 |
| `enews:RenewableInstallationShape` | `enews:RenewableInstallation` | `rdfs:label` (1..*), `enews:hasTechnology` (0..*, class `enews:EnergyTechnology`), `enews:operatedBy` (0..*, class `enews:Organization`) | Stage 3 |
| `enews:CapacityMeasurementShape` | `enews:CapacityMeasurement` | `enews:valueInMW` (1..1, `xsd:float`), `enews:capacityUnit` (1..1, `xsd:string`), `enews:measurementDate` (0..1, `xsd:dateTime`) | Stage 3 |

**Validation execution:**

```python
from pyshacl import validate as shacl_validate

def validate_abox(
    data_graph: rdflib.Graph,
    shapes_path: Path,
    tbox_path: Path,
) -> tuple[bool, rdflib.Graph, str]:
    """Run SHACL validation against the shapes graph."""
    shapes_graph = rdflib.Graph().parse(shapes_path, format="turtle")
    ont_graph = rdflib.Graph().parse(tbox_path, format="turtle")
    conforms, results_graph, results_text = shacl_validate(
        data_graph,
        shacl_graph=shapes_graph,
        ont_graph=ont_graph,
        inference="rdfs",
        abort_on_first=False,
    )
    return conforms, results_graph, results_text
```

**Known validation exceptions:**

1. **`enews:MediaAttachmentShape`** requires `enews:mediaUri` (`sh:minCount 1`), but only the first image in a multi-image post has a URL. Images 2..N will fail validation. **Mitigation:** Only create `enews:MediaAttachment` individuals for images with a URL, or relax the shape to `sh:minCount 0` for batch-ingested data.

2. **`enews:ArticleShape`** requires `enews:coversTopic` (`sh:minCount 1`). Articles without topic assignment will fail validation. **Mitigation:** Articles are only validated after Stage 3 topic enrichment. Articles with no topic after enrichment are flagged for human review.

### 5.2 Confidence Scoring

Every NLP/LLM-extracted entity gets a confidence annotation using a custom annotation property:

```turtle
@prefix enews: <http://example.org/ontology/energy-news#> .
@prefix data: <http://example.org/data/> .

# Example: LLM-extracted organization with confidence
data:org/drax a enews:Organization ;
    rdfs:label "Drax"@en ;
    enews:hasSector enews:Fossil ;
    data:extractionConfidence "0.92"^^xsd:float ;
    data:extractionSource "spacy-ner"^^xsd:string .
```

Confidence thresholds for automated acceptance:

| Tier | Threshold | Action |
|---|---|---|
| High | >= 0.90 | Auto-accept; no review |
| Medium | 0.70 - 0.89 | Accept with flag; batch review weekly |
| Low | < 0.70 | Queue for human review before loading |

### 5.3 CQ Test Plan

The 30 competency questions (CQ-001 through CQ-030) serve as acceptance tests. Each CQ is a SPARQL query that must return expected results after ABox ingestion.

**CQ classification by data source requirement:**

| Category | CQs | Pipeline Dependency |
|---|---|---|
| **REFERENCE_DATA** (answerable from existing reference individuals) | CQ-001, CQ-002, CQ-009, CQ-010, CQ-020, CQ-021, CQ-023, CQ-024, CQ-025, CQ-026, CQ-027, CQ-028, CQ-029, CQ-030 | None -- pass immediately with TBox + reference individuals |
| **DIRECT_FIELD** (answerable from post metadata) | CQ-007, CQ-017, CQ-018 | Stage 2 (direct mapping) |
| **DERIVED** (require Article + Publication linkage) | CQ-003, CQ-004, CQ-005, CQ-006, CQ-008, CQ-019 | Stage 2 + Stage 3a (topic linkage) |
| **NLP_REQUIRED** (require entity extraction) | CQ-011, CQ-012, CQ-013, CQ-014, CQ-015, CQ-016, CQ-022 | Stage 3b-3c (NER + LLM) |

**Test execution:**

```python
def run_cq_tests(
    store: pyoxigraph.Store,
    cq_file: Path,
) -> dict[str, bool]:
    """Execute all CQ SPARQL queries and check expected results."""
    import yaml

    cqs = yaml.safe_load(cq_file.read_text())
    results = {}
    for cq in cqs:
        cq_id = cq["id"]
        sparql = cq["sparql"]
        expected = cq["expected_result"]
        try:
            query_results = list(store.query(sparql))
            if expected == "non_empty":
                results[cq_id] = len(query_results) > 0
            elif expected in ("true", "false"):
                results[cq_id] = len(query_results) > 0 if expected == "true" else len(query_results) == 0
            else:
                results[cq_id] = len(query_results) > 0
        except Exception as e:
            results[cq_id] = False
    return results
```

**Phase 1 target:** 14 REFERENCE_DATA CQs + 3 DIRECT_FIELD CQs = 17/30 CQs passing.
**Phase 2 target:** +6 DERIVED CQs = 23/30 CQs passing.
**Phase 3 target:** +7 NLP_REQUIRED CQs = 30/30 CQs passing.

---

## 6. Triple Store Strategy

### 6.1 Oxigraph Setup

Use Oxigraph via `pyoxigraph` (Python bindings) for the triple store. Oxigraph provides:
- SPARQL 1.1 query and update
- Named graph support
- Persistent storage
- No external server required (embedded)

```python
import pyoxigraph

def init_store(store_path: Path) -> pyoxigraph.Store:
    """Initialize or open an Oxigraph store."""
    store_path.mkdir(parents=True, exist_ok=True)
    return pyoxigraph.Store(str(store_path))

def load_turtle(store: pyoxigraph.Store, ttl_path: Path, graph_name: str) -> int:
    """Load a Turtle file into a named graph."""
    graph_iri = pyoxigraph.NamedNode(graph_name)
    with open(ttl_path, "rb") as f:
        store.load(f, "text/turtle", to_graph=graph_iri)
    count = 0
    for _ in store.quads_for_pattern(None, None, None, graph_iri):
        count += 1
    return count

def load_rdflib_graph(
    store: pyoxigraph.Store,
    g: rdflib.Graph,
    graph_name: str,
) -> int:
    """Load an rdflib Graph into a named Oxigraph graph."""
    import tempfile
    graph_iri = pyoxigraph.NamedNode(graph_name)
    with tempfile.NamedTemporaryFile(suffix=".ttl", mode="wb", delete=False) as f:
        g.serialize(f, format="turtle")
        tmp_path = f.name
    with open(tmp_path, "rb") as f:
        store.load(f, "text/turtle", to_graph=graph_iri)
    Path(tmp_path).unlink()
    return len(g)
```

### 6.2 Named Graph Organization

```
oxigraph-store/
  ├── <urn:enews:graph:tbox>                    # TBox (energy-news.ttl)
  ├── <urn:enews:graph:reference>               # Reference individuals
  ├── <urn:enews:graph:shapes>                  # SHACL shapes
  ├── <urn:enews:graph:abox:phase1>             # Phase 1: direct mapping (Posts, Authors, Embeds, Media)
  ├── <urn:enews:graph:abox:phase2>             # Phase 2: derived entities (Articles, Publications)
  ├── <urn:enews:graph:abox:phase3>             # Phase 3: NLP/LLM entities (Orgs, Geos, Projects)
  ├── <urn:enews:graph:abox:batch:2026-02-28>   # Incremental batch by date
  └── <urn:enews:graph:abox:batch:2026-03-01>   # Next incremental batch
```

**Graph loading sequence:**

```python
def initialize_store(store: pyoxigraph.Store, ontology_dir: Path) -> None:
    """Load TBox, reference individuals, and shapes into named graphs."""
    load_turtle(store, ontology_dir / "energy-news.ttl", "urn:enews:graph:tbox")
    load_turtle(store, ontology_dir / "energy-news-reference-individuals.ttl", "urn:enews:graph:reference")
    load_turtle(store, ontology_dir / "shapes" / "energy-news-shapes.ttl", "urn:enews:graph:shapes")
    # Import declarations
    for imp in (ontology_dir / "imports").glob("*.ttl"):
        load_turtle(store, imp, f"urn:enews:graph:imports:{imp.stem}")
```

### 6.3 Query Patterns

**Cross-graph queries** use the default (union) graph, which merges all named graphs:

```sparql
# CQ-007: Top authors by post count
PREFIX enews: <http://example.org/ontology/energy-news#>
SELECT ?author ?handle (COUNT(?post) AS ?postCount) WHERE {
    ?post a enews:Post ;
          enews:postedBy ?author .
    ?author enews:handle ?handle .
}
GROUP BY ?author ?handle
ORDER BY DESC(?postCount)
LIMIT 20
```

**Graph-scoped queries** for debugging or auditing:

```sparql
# Count triples per named graph
SELECT ?g (COUNT(*) AS ?triples) WHERE {
    GRAPH ?g { ?s ?p ?o }
}
GROUP BY ?g
ORDER BY DESC(?triples)
```

**Topic hierarchy traversal** using `skos:broader*`:

```sparql
# CQ-010: Is Solar classified as renewable?
PREFIX enews: <http://example.org/ontology/energy-news#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
ASK {
    enews:Solar skos:broader* enews:Renewable .
}
```

### 6.4 Incremental Update Strategy

```python
from datetime import date

def incremental_load(
    store: pyoxigraph.Store,
    new_posts: list[dict],
    ontology_dir: Path,
) -> str:
    """Process and load new posts into a date-stamped named graph."""
    today = date.today().isoformat()
    graph_name = f"urn:enews:graph:abox:batch:{today}"

    # Stage 2: Transform
    g = transform_all(new_posts)

    # Stage 3: Enrich (topic linkage, NER)
    topic_map = build_hashtag_topic_map(
        rdflib.Graph().parse(ontology_dir / "energy-news-reference-individuals.ttl")
    )
    link_topics_to_articles(g, topic_map)

    # Stage 3b: NER (if spaCy model loaded)
    # extract_ner_entities(g, nlp, org_gazetteer, geo_gazetteer)

    # Validate
    conforms, _, report = validate_abox(
        g,
        ontology_dir / "shapes" / "energy-news-shapes.ttl",
        ontology_dir / "energy-news.ttl",
    )
    if not conforms:
        print(f"SHACL validation warnings:\n{report}")

    # Load
    count = load_rdflib_graph(store, g, graph_name)
    print(f"Loaded {count} triples into {graph_name}")
    return graph_name
```

---

## 7. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Goal:** Direct field mapping; 17/30 CQs passing.

**Deliverables:**
1. Oxigraph store initialized with TBox, reference individuals, and SHACL shapes
2. Stage 2 transform pipeline: Post, AuthorAccount, EmbeddedExternalLink, MediaAttachment
3. Article stubs from external embeds (without `enews:coversTopic`)
4. Publication instances derived from link domains
5. SHACL validation for PostShape, AuthorAccountShape, EmbeddedExternalLinkShape, MediaAttachmentShape, PublicationShape
6. CQ test runner for all 30 CQs

**Python dependencies:**
```
rdflib >= 7.0
pyshacl >= 0.26
pyoxigraph >= 0.4
pyyaml >= 6.0
```

**CQs expected to pass:** CQ-001, CQ-002, CQ-007, CQ-009, CQ-010, CQ-017, CQ-018, CQ-020, CQ-021, CQ-023, CQ-024, CQ-025, CQ-026, CQ-027, CQ-028, CQ-029, CQ-030 (17 total).

**Estimated triples:** ~315,000

### Phase 2: Topic Enrichment (Weeks 3-4)

**Goal:** EnergyTopic linkage; 23/30 CQs passing.

**Deliverables:**
1. Hashtag-to-EnergyTopic mapping table from 92 SKOS concepts and their `skos:altLabel` values
2. Keyword matching engine scanning `enews:postText` and `enews:linkTitle`
3. `enews:coversTopic` assertions on Article individuals (satisfying `enews:ArticleShape` `sh:minCount 1`)
4. `enews:sharesArticle` linkage between Posts and Articles
5. LLM-based topic classification for posts with no hashtag/keyword match
6. Article deduplication by URL
7. ArticleShape SHACL validation (including URL-domain SPARQL constraint)

**Additional Python dependencies:**
```
anthropic >= 0.40  # For Claude API topic classification
```

**CQs expected to pass (additional):** CQ-003, CQ-004, CQ-005, CQ-006, CQ-008, CQ-019 (+6 = 23 total).

**Estimated new triples:** ~75,000 (topic linkages + article dedup adjustments)

### Phase 3: Entity Extraction (Weeks 5-8)

**Goal:** NLP/LLM entity extraction; 30/30 CQs passing.

**Deliverables:**
1. spaCy NER pipeline for Organization and GeographicEntity extraction
2. Reference individual alias matching (15 Organizations, 10 GeographicEntities, 3 RegulatoryBodies)
3. `enews:mentionsOrganization` and `enews:hasGeographicFocus` assertions on Articles
4. CapacityMeasurement regex extraction
5. LLM batch extraction for EnergyProject, EnergyTechnology, PolicyInstrument
6. Confidence scoring annotations
7. OrganizationShape, GeographicEntityShape validation

**Additional Python dependencies:**
```
spacy >= 3.7
en_core_web_trf  # spaCy transformer model
rapidfuzz >= 3.0  # Fuzzy matching
```

**CQs expected to pass (additional):** CQ-011, CQ-012, CQ-013, CQ-014, CQ-015, CQ-016, CQ-022 (+7 = 30 total).

**Estimated new triples:** ~100,000 (entities + relationships)

### Phase 4: Advanced Enrichment and Operations (Weeks 9-12)

**Goal:** Full ABox with all entity types; production-grade pipeline.

**Deliverables:**
1. LLM extraction for remaining T4 entities: EnergyEvent, PowerPlant, RenewableInstallation, MarketInstrument, ProjectStatus linkage
2. Incremental sync pipeline (SkyGent delta detection + append-only processing)
3. Human review workflow for low-confidence extractions
4. Query optimization (Oxigraph indices for frequent CQ patterns)
5. Full SHACL validation pass across all 15 shapes
6. Dashboard queries: topic trends over time, publication coverage, author specialization
7. EnergyProjectShape, PowerPlantShape, RenewableInstallationShape, CapacityMeasurementShape validation

**Estimated final triple count:** ~490,000

### Dependency Graph

```
Phase 1 (Foundation)
  ├── Oxigraph store setup
  ├── TBox + reference individuals loaded
  ├── Stage 2 transform pipeline
  └── SHACL validation (5 shapes)
      │
Phase 2 (Topics)
  ├── Hashtag/keyword topic matching
  ├── LLM topic classification
  ├── Article deduplication
  └── ArticleShape validation
      │
Phase 3 (Entities)
  ├── spaCy NER pipeline
  ├── Reference individual matching
  ├── Regex extraction (capacity, price)
  ├── LLM batch extraction
  └── Organization/Geo shape validation
      │
Phase 4 (Advanced)
  ├── Remaining T4 entities
  ├── Incremental sync
  ├── Human review workflow
  └── Full SHACL validation (15 shapes)
```

### Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM extraction quality too low | Medium | High | Start with T1/T2 entities; use LLM only for T4; confidence thresholds + human review |
| SHACL validation blocks loading | Medium | Medium | Validate per-shape; load valid triples; quarantine failing individuals |
| Article URL deduplication misses | Low | Medium | Normalize URLs (strip tracking params, www prefix); use `owl:hasKey` enforcement |
| spaCy NER false positives | Medium | Low | Gazetteer matching as primary; NER as secondary; confidence scoring |
| Oxigraph performance at 500K triples | Low | Low | Oxigraph handles millions; add indices for frequent query patterns |
| Pre-processed JSON missing fields | Low | Medium | Defensive coding with `.get()` and defaults; skip malformed posts |
