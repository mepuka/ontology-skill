"""Assemble RDF N-Triples from post-processed extraction results.

Converts enriched JSONL (from postprocess.py) into RDF triples following
the Energy News Ontology schema. Produces:
  - Article individuals with metadata + topics
  - Entity individuals (Organization, GeographicEntity, etc.) with labels
  - Relationship triples (operatedBy, locatedIn, hasCapacity, etc.)
  - CapacityMeasurement / PriceDataPoint individuals with datatype properties

Usage:
    uv run python scripts/extract/assemble_triples.py data/postprocessed.jsonl
    uv run python scripts/extract/assemble_triples.py input.jsonl --output data/extracted-triples.nt
"""

from __future__ import annotations

import contextlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ingest.namespaces import DATA, ENEWS, bind_abox_prefixes

# ---------------------------------------------------------------------------
# Extraction class → OWL class mapping
# ---------------------------------------------------------------------------

CLASS_MAP: dict[str, URIRef] = {
    "Organization": ENEWS.Organization,
    "RegulatoryBody": ENEWS.RegulatoryBody,
    "GeographicEntity": ENEWS.GeographicEntity,
    "GridZone": ENEWS.GridZone,
    "EnergyProject": ENEWS.EnergyProject,
    "PowerPlant": ENEWS.PowerPlant,
    "RenewableInstallation": ENEWS.RenewableInstallation,
    "EnergyTechnology": ENEWS.EnergyTechnology,
    "PolicyInstrument": ENEWS.PolicyInstrument,
    "CapacityMeasurement": ENEWS.CapacityMeasurement,
    "PriceDataPoint": ENEWS.PriceDataPoint,
    "EnergyEvent": ENEWS.EnergyEvent,
    "Person": ENEWS.Person,
}

# Object property mapping for relationships
RELATIONSHIP_PROPS: dict[str, URIRef] = {
    "operatedBy": ENEWS.operatedBy,
    "locatedIn": ENEWS.hasGeographicFocus,
    "hasCapacity": ENEWS.hasCapacity,
    "hasStatus": ENEWS.hasStatus,
    "jurisdiction": ENEWS.jurisdiction,
    "developedThrough": ENEWS.developedThrough,
    "hasTechnology": ENEWS.hasTechnology,
    "mentionsOrganization": ENEWS.mentionsOrganization,
}

# Project status mapping
STATUS_MAP: dict[str, URIRef] = {
    "planning": ENEWS.status_Planning,
    "planned": ENEWS.status_Planning,
    "under review": ENEWS.status_UnderReview,
    "review": ENEWS.status_UnderReview,
    "under construction": ENEWS.status_UnderConstruction,
    "construction": ENEWS.status_UnderConstruction,
    "operational": ENEWS.status_Operational,
    "operating": ENEWS.status_Operational,
    "mothballed": ENEWS.status_Mothballed,
    "decommissioned": ENEWS.status_Decommissioned,
    "retired": ENEWS.status_Decommissioned,
}


def _slug_uri(text: str, prefix: str = "entity") -> URIRef:
    """Create a DATA namespace URI from text."""
    slug = unicodedata.normalize("NFKD", text)
    slug = slug.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", slug.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)[:80]
    return DATA[f"{prefix}/{slug}"]


def assemble_document(doc: dict, graph: Graph, *, stats: Counter) -> None:
    """Add triples for a single post-processed document to the graph."""
    url = doc.get("url", "")
    if not url:
        return

    article_uri = URIRef(url)

    # Article type + metadata
    graph.add((article_uri, RDF.type, ENEWS.Article))
    graph.add((article_uri, ENEWS.url, Literal(url, datatype=XSD.anyURI)))

    title = doc.get("title")
    if title:
        graph.add((article_uri, ENEWS.title, Literal(title, datatype=XSD.string)))

    date = doc.get("date")
    if date:
        graph.add((article_uri, ENEWS.publishedDate, Literal(date, datatype=XSD.dateTime)))

    # Publication
    pub_iri = doc.get("publicationIRI")
    if pub_iri:
        graph.add((article_uri, ENEWS.publishedBy, URIRef(pub_iri)))

    # Topics
    for topic_uri in doc.get("topics", []):
        graph.add((article_uri, ENEWS.coversTopic, URIRef(topic_uri)))
        stats["topic_links"] += 1

    # Process extractions
    seen_entities: set[str] = set()

    for ext in doc.get("extractions", []):
        ext_class = ext.get("extractionClass", "")
        ext_text = ext.get("extractionText", "")
        linked_iri = ext.get("linkedIRI")
        attrs = ext.get("attributes") or {}

        if ext_class == "Relationship":
            _assemble_relationship(ext, article_uri, graph, stats)
            continue

        if ext_class not in CLASS_MAP:
            continue

        owl_class = CLASS_MAP[ext_class]

        # Entity IRI (from linking or mint)
        if linked_iri:
            entity_uri = URIRef(linked_iri)
        else:
            entity_uri = _slug_uri(ext_text, _type_prefix(ext_class))

        # Only emit entity triples once per document
        entity_key = str(entity_uri)
        if entity_key not in seen_entities:
            seen_entities.add(entity_key)
            graph.add((entity_uri, RDF.type, owl_class))
            graph.add((entity_uri, RDFS.label, Literal(ext_text, lang="en")))
            stats["entities"] += 1

        # Article-level object properties
        if ext_class in ("Organization", "RegulatoryBody"):
            graph.add((article_uri, ENEWS.mentionsOrganization, entity_uri))
        elif ext_class in ("GeographicEntity", "GridZone"):
            graph.add((article_uri, ENEWS.hasGeographicFocus, entity_uri))
        elif ext_class == "EnergyProject":
            graph.add((article_uri, ENEWS.aboutProject, entity_uri))
        elif ext_class == "EnergyTechnology":
            graph.add((article_uri, ENEWS.coversTechnology, entity_uri))

        # Structured datatype properties
        if ext_class == "CapacityMeasurement":
            _add_capacity_triples(entity_uri, attrs, graph)
            stats["capacity_triples"] += 1
        elif ext_class == "PriceDataPoint":
            _add_price_triples(entity_uri, attrs, graph)
            stats["price_triples"] += 1

    stats["articles"] += 1


def _add_capacity_triples(entity_uri: URIRef, attrs: dict, graph: Graph) -> None:
    """Add valueInMW and capacityUnit triples for a CapacityMeasurement."""
    value_mw = attrs.get("valueInMW")
    unit = attrs.get("capacityUnit")
    if value_mw:
        with contextlib.suppress(ValueError, TypeError):
            graph.add(
                (
                    entity_uri,
                    ENEWS.valueInMW,
                    Literal(float(value_mw), datatype=XSD.float),
                )
            )
    if unit:
        graph.add((entity_uri, ENEWS.capacityUnit, Literal(unit, datatype=XSD.string)))


def _add_price_triples(entity_uri: URIRef, attrs: dict, graph: Graph) -> None:
    """Add priceValue and priceCurrency triples for a PriceDataPoint."""
    price_val = attrs.get("priceValue")
    currency = attrs.get("priceCurrency")
    if price_val:
        with contextlib.suppress(ValueError, TypeError):
            graph.add(
                (
                    entity_uri,
                    ENEWS.priceValue,
                    Literal(float(price_val), datatype=XSD.float),
                )
            )
    if currency:
        graph.add((entity_uri, ENEWS.priceCurrency, Literal(currency, datatype=XSD.string)))


def _assemble_relationship(
    ext: dict,
    _article_uri: URIRef,
    graph: Graph,
    stats: Counter,
) -> None:
    """Assemble triples for a Relationship extraction."""
    attrs = ext.get("attributes") or {}
    rel_type = attrs.get("relationshipType", "")
    subject_text = attrs.get("subject", "")
    object_text = attrs.get("object", "")

    if not rel_type or not subject_text or not object_text:
        stats["relationship_skipped"] += 1
        return

    prop = RELATIONSHIP_PROPS.get(rel_type)
    if not prop:
        stats["relationship_unknown_type"] += 1
        return

    # Special handling for hasStatus — map to reference individual
    if rel_type == "hasStatus":
        status_uri = STATUS_MAP.get(object_text.lower().strip())
        if status_uri:
            subject_uri = _slug_uri(subject_text, "project")
            graph.add((subject_uri, prop, status_uri))
            stats["relationships"] += 1
        return

    # Generic relationship: subject → property → object
    subject_uri = _slug_uri(subject_text, "entity")
    object_uri = _slug_uri(object_text, "entity")
    graph.add((subject_uri, prop, object_uri))
    stats["relationships"] += 1


def _type_prefix(ext_class: str) -> str:
    """Map extraction class to IRI path prefix."""
    prefixes = {
        "Organization": "org",
        "RegulatoryBody": "org",
        "GeographicEntity": "geo",
        "GridZone": "geo",
        "EnergyProject": "project",
        "PowerPlant": "plant",
        "RenewableInstallation": "installation",
        "EnergyTechnology": "tech",
        "PolicyInstrument": "policy",
        "CapacityMeasurement": "measurement",
        "PriceDataPoint": "price",
        "EnergyEvent": "event",
        "Person": "person",
    }
    return prefixes.get(ext_class, "entity")


def assemble_file(input_path: Path, output_path: Path) -> dict:
    """Assemble all documents from a JSONL file into an RDF graph."""
    graph = Graph()
    bind_abox_prefixes(graph)
    stats: Counter[str] = Counter()

    with input_path.open() as f:
        for raw_line in f:
            stripped = raw_line.strip()
            if not stripped:
                continue
            doc = json.loads(stripped)
            assemble_document(doc, graph, stats=stats)

    # Serialize
    output_path.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=str(output_path), format="nt")

    stats["total_triples"] = len(graph)
    return dict(stats)


def main() -> None:
    """CLI entrypoint."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <postprocessed.jsonl> [--output <output.nt>]", file=sys.stderr)
        sys.exit(2)

    input_path = Path(sys.argv[1])
    output_path = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = Path(sys.argv[idx + 1])

    if output_path is None:
        output_path = Path("data/extracted-triples.nt")

    if not input_path.exists():
        print(f"Input not found: {input_path}", file=sys.stderr)
        sys.exit(2)

    print(f"Assembling triples from {input_path}...")
    stats = assemble_file(input_path, output_path)

    print("\nResults:")
    for key, value in sorted(stats.items()):
        print(f"  {key}: {value}")
    print(f"\nOutput: {output_path}")
    print(f"Total triples: {stats.get('total_triples', 0)}")


if __name__ == "__main__":
    main()
