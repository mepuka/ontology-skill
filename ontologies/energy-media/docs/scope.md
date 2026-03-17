# Energy Media Ontology — Scope

## Domain Description

An ontology extension for modeling media attachments (charts, screenshots, photos,
infographics) in energy expert discourse on Bluesky. Extends the energy-news
ontology with structured media semantics, multi-layer attribution, and chart
description capabilities. Enables agents to reason about chart content, trace data
provenance, and assess media richness without requiring vision capabilities.

## Intended Use Cases

- Classify media attachments by type (chart, screenshot, photo, infographic, video)
- Describe chart semantics: chart type, axes, units, time range, geographic scope, key data points
- Trace multi-layer attribution: who posted the image, where the chart appeared (article/report), where the underlying data comes from (dataset/API)
- Distinguish alt text provenance: author-provided, vision-generated, or absent
- Score posts by media richness as a curation/ranking signal
- Link chart visualizations to known energy data providers for claim verification

## Data Source

- **Primary**: Bluesky post embeds from energy experts, collected via the Skygest ingest pipeline
- **Scope of data**: Image CDN URLs (thumb + fullsize), alt text, external link metadata
  (title, description, domain), video playlist URLs, quote post content
- **Enrichment data**: Vision model output (Gemini 2.5 Flash) producing structured chart descriptions
- **Reference data**: Known energy data sources (GridStatus, EIA, ENTSO-E, provincial hydro authorities)

## Relationship to Energy-News Ontology

This ontology **extends** the energy-news ontology. It imports energy-news concepts
(Post, Article, EnergyTopic, Author) and adds media-specific classes and properties.
It does not duplicate or replace energy-news modeling.

## In Scope

- Media type taxonomy (chart, screenshot, photo, diagram, infographic, video)
- Chart type taxonomy (~15-20 types: bar, line, scatter, area, heatmap, map, Sankey, etc.)
- Chart semantic description (axes, units, scales, series, data points, trends, title)
- Multi-layer attribution model:
  - Image source (who posted the embed)
  - Content source (article/report the chart appears in)
  - Data source (underlying dataset cited in the chart)
- Alt text provenance (original, synthetic, absent)
- Temporal metadata on charts (time range covered, data currency, forecast horizon)
- Spatial metadata on charts (geographic scope, grid region, ISO/RTO jurisdiction)
- Media richness scoring model (chart count, embed type diversity)
- Energy data source registry (known providers with API endpoints and coverage areas)

## Out of Scope

- Full OCR/data extraction from chart images (downstream pipeline concern, not ontology)
- Image file storage or CDN management
- Vision model selection or configuration
- Detailed grid topology (CIM-level equipment modeling)
- Financial data or market pricing models
- Sentiment analysis of chart commentary
- Non-energy media classification

## Constraints

- **Profile**: OWL 2 DL (lightweight; primarily taxonomic with some object properties)
- **Size**: Small-medium (~30-60 classes, ~30-40 properties)
- **Serialization**: Turtle (.ttl)
- **Upper ontology**: Minimal BFO alignment where natural; consistent with energy-news decisions
- **Naming**: CamelCase classes, camelCase properties, English labels
- **Reuse strategy**:
  - SKOS for chart-type and grid-jurisdiction taxonomies
  - Dublin Core for basic metadata properties
  - Schema.org for ImageObject/Dataset alignment
  - PROV-O Entity-Activity-Agent pattern for attribution chains
  - OWL-Time vocabulary for temporal coverage
  - VISO (reference only) for chart type taxonomy design
  - CIM/ENTSO-E (reference only) for spatial hierarchy design
