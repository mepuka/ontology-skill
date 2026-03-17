"""Deterministic post-processing of LLM extraction results.

Transforms raw effect-langextract JSONL output into structured, linked records:
  1. Capacity parsing — regex on extractionText → {valueInMW, capacityUnit}
  2. Price parsing — regex → {priceValue, priceCurrency}
  3. Entity linking — rapidfuzz against reference individuals (orgs, geos, pubs)
  4. Topic classification — keyword matching against 92 SKOS topics
  5. Publication linking — domain lookup
  6. IRI minting — deterministic slugify
  7. Cross-article entity dedup — global registry by normalized key

Usage:
    uv run python scripts/extract/postprocess.py results.jsonl
    uv run python scripts/extract/postprocess.py input.jsonl --output out.jsonl
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from rdflib import Graph, URIRef

# Reuse existing infrastructure from the ingest pipeline
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ingest.namespaces import ENEWS
from ingest.publications import PublicationIndex, build_ref_publication_index
from ingest.topics import TopicLookup, build_topic_lookup

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
REF_INDIVIDUALS = PROJECT_DIR / "energy-news-reference-individuals.ttl"

CAPACITY_RE = re.compile(
    r"([\d,]+(?:\.\d+)?)\s*(MW|GW|MWh|GWh|kW|kWh|TW|TWh)\b",
    re.IGNORECASE,
)

PRICE_RE = re.compile(
    r"(?:"
    r"(?P<sym>[\$€£¥])\s*(?P<val1>[\d,]+(?:\.\d+)?)\s*(?P<unit1>billion|million|thousand|per\s*MWh|/MWh|/kWh)?"
    r"|"
    r"(?P<val2>[\d,]+(?:\.\d+)?)\s*(?P<cur>USD|EUR|GBP|JPY|CNY|CAD|AUD)"
    r")",
    re.IGNORECASE,
)

CURRENCY_SYMBOLS = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "CNY"}

UNIT_MULTIPLIERS = {
    "mw": 1.0,
    "gw": 1000.0,
    "tw": 1_000_000.0,
    "kw": 0.001,
    "mwh": 1.0,
    "gwh": 1000.0,
    "twh": 1_000_000.0,
    "kwh": 0.001,
}


# ---------------------------------------------------------------------------
# Slugify
# ---------------------------------------------------------------------------


def slugify(text: str, *, max_length: int = 80) -> str:
    """Deterministic slug for IRI local names.

    Lowercases, strips accents, replaces non-alnum with hyphens, deduplicates.
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    text = re.sub(r"-{2,}", "-", text)
    return text[:max_length]


# ---------------------------------------------------------------------------
# Capacity / Price Parsing
# ---------------------------------------------------------------------------


def parse_capacity(text: str, attrs: dict | None = None) -> dict | None:
    """Parse a capacity measurement from text or pre-existing attributes."""
    # Try attributes first (from LLM output)
    if attrs and attrs.get("valueInMW"):
        try:
            return {
                "valueInMW": float(str(attrs["valueInMW"]).replace(",", "")),
                "capacityUnit": str(attrs.get("capacityUnit", "MW")),
            }
        except ValueError:
            pass

    m = CAPACITY_RE.search(text)
    if not m:
        return None

    raw_value = float(m.group(1).replace(",", ""))
    unit = m.group(2)
    multiplier = UNIT_MULTIPLIERS.get(unit.lower(), 1.0)

    return {
        "valueInMW": raw_value * multiplier,
        "capacityUnit": unit,
    }


def parse_price(text: str, attrs: dict | None = None) -> dict | None:
    """Parse a price/cost from text or pre-existing attributes."""
    if attrs and attrs.get("priceValue"):
        try:
            return {
                "priceValue": float(str(attrs["priceValue"]).replace(",", "")),
                "priceCurrency": str(attrs.get("priceCurrency", "USD")),
            }
        except ValueError:
            pass

    m = PRICE_RE.search(text)
    if not m:
        return None

    if m.group("sym"):
        currency = CURRENCY_SYMBOLS.get(m.group("sym"), "USD")
        raw_value = float(m.group("val1").replace(",", ""))
        unit_str = (m.group("unit1") or "").lower()
        if "billion" in unit_str:
            raw_value *= 1_000_000_000
        elif "million" in unit_str:
            raw_value *= 1_000_000
        elif "thousand" in unit_str:
            raw_value *= 1_000
        return {"priceValue": raw_value, "priceCurrency": currency}

    if m.group("val2"):
        return {
            "priceValue": float(m.group("val2").replace(",", "")),
            "priceCurrency": m.group("cur").upper(),
        }

    return None


# ---------------------------------------------------------------------------
# Entity Linking (rapidfuzz)
# ---------------------------------------------------------------------------


def _build_ref_index(ref_graph: Graph) -> dict[str, dict[str, str]]:
    """Build label→URI indexes for organizations and geographic entities."""
    from rdflib.namespace import RDF, RDFS

    index: dict[str, dict[str, str]] = {"Organization": {}, "GeographicEntity": {}}

    for org in ref_graph.subjects(RDF.type, ENEWS.Organization):
        for label in ref_graph.objects(org, RDFS.label):
            index["Organization"][str(label).lower()] = str(org)

    for reg in ref_graph.subjects(RDF.type, ENEWS.RegulatoryBody):
        for label in ref_graph.objects(reg, RDFS.label):
            index["Organization"][str(label).lower()] = str(reg)

    for geo in ref_graph.subjects(RDF.type, ENEWS.GeographicEntity):
        for label in ref_graph.objects(geo, RDFS.label):
            index["GeographicEntity"][str(label).lower()] = str(geo)

    for gz in ref_graph.subjects(RDF.type, ENEWS.GridZone):
        for label in ref_graph.objects(gz, RDFS.label):
            index["GeographicEntity"][str(label).lower()] = str(gz)

    return index


class EntityLinker:
    """Fuzzy entity linker using rapidfuzz for matching against reference individuals."""

    def __init__(self, ref_graph: Graph, *, threshold: int = 85) -> None:
        self._threshold = threshold
        self._ref_index = _build_ref_index(ref_graph)
        self._global_registry: dict[str, str] = {}  # norm_key → IRI

    def link(self, ext_class: str, ext_text: str) -> str | None:
        """Try to link an extraction to a reference individual.

        Returns the URI string if matched, None otherwise.
        """
        try:
            from rapidfuzz import fuzz
        except ImportError:
            return self._exact_link(ext_class, ext_text)

        # Map extraction class to index category
        category = self._class_to_category(ext_class)
        if not category or category not in self._ref_index:
            return None

        candidates = self._ref_index[category]
        if not candidates:
            return None

        ext_lower = ext_text.lower().strip()

        # Exact match first
        if ext_lower in candidates:
            return candidates[ext_lower]

        # Fuzzy match
        best_score = 0
        best_uri = None
        for label, uri in candidates.items():
            score = fuzz.ratio(ext_lower, label)
            if score > best_score:
                best_score = score
                best_uri = uri

        if best_score >= self._threshold and best_uri:
            return best_uri

        return None

    def _exact_link(self, ext_class: str, ext_text: str) -> str | None:
        """Fallback exact matching when rapidfuzz is not installed."""
        category = self._class_to_category(ext_class)
        if not category or category not in self._ref_index:
            return None
        return self._ref_index[category].get(ext_text.lower().strip())

    def mint_or_reuse(self, ext_class: str, ext_text: str) -> str:
        """Get or create a stable IRI for an entity."""
        norm_key = f"{ext_class}:{ext_text.lower().strip()}"

        # Check global dedup registry
        if norm_key in self._global_registry:
            return self._global_registry[norm_key]

        # Try reference linking
        linked = self.link(ext_class, ext_text)
        if linked:
            self._global_registry[norm_key] = linked
            return linked

        # Mint new IRI
        type_prefix = self._type_prefix(ext_class)
        slug = slugify(ext_text)
        iri = f"http://example.org/data/{type_prefix}/{slug}"
        self._global_registry[norm_key] = iri
        return iri

    @staticmethod
    def _class_to_category(ext_class: str) -> str | None:
        if ext_class in ("Organization", "RegulatoryBody"):
            return "Organization"
        if ext_class in ("GeographicEntity", "GridZone"):
            return "GeographicEntity"
        return None

    @staticmethod
    def _type_prefix(ext_class: str) -> str:
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
            "EnergyEvent": "event",
            "Person": "person",
        }
        return prefixes.get(ext_class, "entity")


# ---------------------------------------------------------------------------
# Post-process a single document
# ---------------------------------------------------------------------------


def postprocess_document(
    doc: dict,
    *,
    entity_linker: EntityLinker,
    topic_lookup: TopicLookup,
    pub_index: PublicationIndex,
) -> dict:
    """Post-process a single extraction result document.

    Enriches extractions with parsed fields, linked IRIs, and topics.
    """
    url = doc.get("documentId", doc.get("url", ""))
    text = doc.get("text", "")
    ctx = doc.get("additionalContext", "")
    domain = ctx.split(",")[0].strip() if ctx else ""

    # Topic classification from full article text
    topics = match_topics_from_text(text, topic_lookup)

    # Publication linking from domain
    pub_uri = None
    if domain:
        pub_uri = pub_index.get(domain)

    enriched_extractions = []
    for ext in doc.get("extractions", []):
        ext_class = ext.get("extractionClass", "")
        ext_text = ext.get("extractionText", "")
        attrs = ext.get("attributes") or {}
        enriched = dict(ext)  # shallow copy

        # Parse capacity
        if ext_class == "CapacityMeasurement":
            parsed = parse_capacity(ext_text, attrs)
            if parsed:
                enriched.setdefault("attributes", {}).update(
                    {
                        "valueInMW": str(parsed["valueInMW"]),
                        "capacityUnit": parsed["capacityUnit"],
                    }
                )

        # Parse price
        if ext_class == "PriceDataPoint":
            parsed = parse_price(ext_text, attrs)
            if parsed:
                enriched.setdefault("attributes", {}).update(
                    {
                        "priceValue": str(parsed["priceValue"]),
                        "priceCurrency": parsed["priceCurrency"],
                    }
                )

        # Entity linking
        if ext_class in (
            "Organization",
            "RegulatoryBody",
            "GeographicEntity",
            "GridZone",
            "EnergyProject",
            "PowerPlant",
            "RenewableInstallation",
            "EnergyTechnology",
            "PolicyInstrument",
            "EnergyEvent",
            "Person",
        ):
            iri = entity_linker.mint_or_reuse(ext_class, ext_text)
            enriched["linkedIRI"] = iri

        enriched_extractions.append(enriched)

    result = {
        "url": url,
        "text": text,
        "extractions": enriched_extractions,
        "topics": [str(t) for t in sorted(topics)],
    }
    if pub_uri:
        result["publicationIRI"] = str(pub_uri)
    if domain:
        result["domain"] = domain

    # Preserve original metadata
    for key in ("title", "date"):
        val = doc.get(key)
        if not val and doc.get("additionalContext"):
            # additionalContext may contain "domain, date"
            parts = doc["additionalContext"].split(",")
            if key == "date" and len(parts) > 1:
                val = parts[1].strip()
        if val:
            result[key] = val

    return result


def match_topics_from_text(text: str, lookup: TopicLookup) -> set[URIRef]:
    """Match article text against topic keywords (no hashtags for articles)."""
    matched: set[URIRef] = set()
    text_lower = text.lower()

    for keyword in lookup.keywords:
        if len(keyword) < 3:
            continue
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, text_lower):
            topic = lookup.get(keyword)
            if topic:
                matched.add(topic)

    return matched


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def postprocess_file(
    input_path: Path,
    output_path: Path,
    *,
    ref_graph: Graph,
) -> dict:
    """Post-process all documents in a JSONL file."""
    entity_linker = EntityLinker(ref_graph, threshold=85)
    topic_lookup = build_topic_lookup(ref_graph)
    pub_index = build_ref_publication_index(ref_graph)

    stats: Counter[str] = Counter()
    with input_path.open() as fin, output_path.open("w") as fout:
        for raw_line in fin:
            stripped = raw_line.strip()
            if not stripped:
                continue
            doc = json.loads(stripped)
            enriched = postprocess_document(
                doc,
                entity_linker=entity_linker,
                topic_lookup=topic_lookup,
                pub_index=pub_index,
            )
            fout.write(json.dumps(enriched) + "\n")
            stats["documents"] += 1
            stats["extractions"] += len(enriched["extractions"])
            stats["topics"] += len(enriched["topics"])
            if enriched.get("publicationIRI"):
                stats["pub_linked"] += 1
            for ext in enriched["extractions"]:
                if ext.get("linkedIRI"):
                    stats["entity_linked"] += 1

    return dict(stats)


def main() -> None:
    """CLI entrypoint."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input.jsonl> [--output <output.jsonl>]", file=sys.stderr)
        sys.exit(2)

    input_path = Path(sys.argv[1])
    output_path = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = Path(sys.argv[idx + 1])

    if output_path is None:
        stem = input_path.stem
        output_path = input_path.parent / f"{stem}-postprocessed.jsonl"

    if not input_path.exists():
        print(f"Input not found: {input_path}", file=sys.stderr)
        sys.exit(2)

    # Load reference individuals
    print(f"Loading reference individuals from {REF_INDIVIDUALS}...")
    ref_graph = Graph()
    ref_graph.parse(REF_INDIVIDUALS, format="turtle")
    print(f"  {len(ref_graph)} triples loaded")

    print(f"Post-processing {input_path} → {output_path}...")
    stats = postprocess_file(input_path, output_path, ref_graph=ref_graph)

    print("\nResults:")
    for key, value in sorted(stats.items()):
        print(f"  {key}: {value}")
    print(f"\nOutput: {output_path}")


if __name__ == "__main__":
    main()
