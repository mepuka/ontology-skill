"""Hashtag/keyword → EnergyTopic matching for Article topic classification."""

from __future__ import annotations

import re

from rdflib import Graph, URIRef
from rdflib.namespace import RDFS, SKOS

from .namespaces import ENEWS


class TopicLookup:
    """Index of EnergyTopic individuals by label and altLabel for fast matching."""

    def __init__(self) -> None:
        self._by_keyword: dict[str, URIRef] = {}

    def add(self, keyword: str, uri: URIRef) -> None:
        """Register a topic URI for a keyword (lowercased)."""
        self._by_keyword[keyword.lower()] = uri

    def get(self, keyword: str) -> URIRef | None:
        """Look up a topic URI by keyword (case-insensitive)."""
        return self._by_keyword.get(keyword.lower())

    @property
    def keywords(self) -> set[str]:
        """All registered keywords."""
        return set(self._by_keyword.keys())


def build_topic_lookup(ref_graph: Graph) -> TopicLookup:
    """Build a topic lookup index from reference individuals.

    Indexes all 92 EnergyTopic individuals by:
    - rdfs:label
    - skos:altLabel

    Args:
        ref_graph: Graph containing reference individuals with EnergyTopic instances.

    Returns:
        A TopicLookup indexed by label and altLabel keywords.
    """
    lookup = TopicLookup()

    for topic in ref_graph.subjects(SKOS.inScheme, ENEWS.EnergyTopicScheme):
        if not isinstance(topic, URIRef):
            continue

        # Index by rdfs:label
        for label in ref_graph.objects(topic, RDFS.label):
            lookup.add(str(label), topic)

        # Index by skos:altLabel
        for alt_label in ref_graph.objects(topic, SKOS.altLabel):
            lookup.add(str(alt_label), topic)

    return lookup


def match_topics(
    text: str,
    hashtags: list[str],
    lookup: TopicLookup,
) -> set[URIRef]:
    """Match post text and hashtags to EnergyTopic individuals.

    Strategy:
    1. Direct hashtag match (e.g., #CCS → CarbonCapture via altLabel "CCS")
    2. Keyword match in text (case-insensitive word boundary matching)

    Args:
        text: Post text content.
        hashtags: List of hashtag strings from the post (with or without #).
        lookup: TopicLookup index from build_topic_lookup().

    Returns:
        Set of matched EnergyTopic URIs.
    """
    matched: set[URIRef] = set()

    # 1. Hashtag matching — strip # prefix and look up directly
    for tag in hashtags:
        clean = tag.lstrip("#").rstrip(":").strip()
        if not clean:
            continue
        topic = lookup.get(clean)
        if topic:
            matched.add(topic)

    # 2. Keyword matching in text — check each topic keyword against text
    text_lower = text.lower()
    for keyword in lookup.keywords:
        if len(keyword) < 3:
            continue  # Skip very short keywords to avoid false positives
        # Use word boundary matching for multi-word keywords
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, text_lower):
            topic = lookup.get(keyword)
            if topic:
                matched.add(topic)

    return matched
