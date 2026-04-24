"""Article URL deduplication — merge Articles sharing the same enews:url."""

from __future__ import annotations

from rdflib import Graph, URIRef
from rdflib.namespace import RDF

from .namespaces import ENEWS


def deduplicate_articles(graph: Graph) -> int:
    """Merge Article individuals that share the same enews:url.

    When multiple Posts share the same external link, each may create an
    Article stub. This function merges duplicates by keeping the first-seen
    Article URI and rewriting all references to duplicates.

    Args:
        graph: The ABox graph to deduplicate (modified in place).

    Returns:
        Number of duplicate Articles merged.
    """
    # Build url → list of Article URIs
    url_to_articles: dict[str, list[URIRef]] = {}
    for article in graph.subjects(RDF.type, ENEWS.Article):
        if not isinstance(article, URIRef):
            continue
        url_val = graph.value(article, ENEWS.url)
        if url_val:
            url_str = str(url_val)
            url_to_articles.setdefault(url_str, []).append(article)

    merged_count = 0
    for articles in url_to_articles.values():
        if len(articles) <= 1:
            continue

        # Keep the first, merge the rest
        canonical = articles[0]
        for duplicate in articles[1:]:
            _merge_article(graph, canonical, duplicate)
            merged_count += 1

    return merged_count


def _merge_article(graph: Graph, canonical: URIRef, duplicate: URIRef) -> None:
    """Merge a duplicate Article into the canonical one.

    - Copy any triples from duplicate that canonical doesn't have
    - Rewrite all references pointing to duplicate → canonical
    - Remove the duplicate individual entirely

    Args:
        graph: The ABox graph.
        canonical: The Article URI to keep.
        duplicate: The Article URI to merge away.
    """
    # Copy additional coversTopic links from duplicate
    for topic in graph.objects(duplicate, ENEWS.coversTopic):
        graph.add((canonical, ENEWS.coversTopic, topic))

    # Fill in missing single-valued properties from duplicate (title, description)
    for prop in (ENEWS.title, ENEWS.description, ENEWS.publishedDate, ENEWS.publishedBy):
        if not graph.value(canonical, prop) and graph.value(duplicate, prop):
            graph.add((canonical, prop, graph.value(duplicate, prop)))

    # Rewrite incoming references (e.g., Post sharesArticle duplicate → canonical)
    for s, p in list(graph.subject_predicates(duplicate)):
        graph.remove((s, p, duplicate))
        graph.add((s, p, canonical))

    # Remove all outgoing triples from the duplicate
    for p, o in list(graph.predicate_objects(duplicate)):
        graph.remove((duplicate, p, o))
