"""Publication discovery and matching — 3-tier lookup from URL domains."""

from __future__ import annotations

import re

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS

from .namespaces import DATA, ENEWS
from .shorteners import BRAND_SHORTENERS, extract_domain, is_brand_shortener


def _slugify_domain(domain: str) -> str:
    """Convert a domain name to a safe IRI slug.

    E.g. 'nytimes.com' -> 'nytimes_com'
    """
    return re.sub(r"[^a-zA-Z0-9]", "_", domain).strip("_")


class PublicationIndex:
    """Index of known publications by domain for fast lookup."""

    def __init__(self) -> None:
        self._by_domain: dict[str, URIRef] = {}

    def add(self, domain: str, uri: URIRef) -> None:
        """Register a publication URI for a domain."""
        self._by_domain[domain] = uri

    def get(self, domain: str) -> URIRef | None:
        """Look up a publication URI by domain."""
        return self._by_domain.get(domain)

    @property
    def domains(self) -> set[str]:
        """All registered domains."""
        return set(self._by_domain.keys())


def build_ref_publication_index(ref_graph: Graph) -> PublicationIndex:
    """Build a publication index from reference individuals.

    Loads the 10 reference Publications by their enews:siteDomain values.

    Args:
        ref_graph: Graph containing reference individuals.

    Returns:
        A PublicationIndex with reference publications indexed by domain.
    """
    index = PublicationIndex()
    for pub in ref_graph.subjects(RDF.type, ENEWS.Publication):
        if not isinstance(pub, URIRef):
            continue
        site_domain = ref_graph.value(pub, ENEWS.siteDomain)
        if site_domain:
            index.add(str(site_domain), pub)
    return index


def _resolve_domain(
    url: str,
    shortener_cache: dict[str, str] | None,
) -> str | None:
    """Resolve a URL to its effective domain through shortener expansion.

    Args:
        url: The original URL.
        shortener_cache: Cache of shortened URL → resolved URL mappings.

    Returns:
        The effective domain, or None if unparseable.
    """
    effective_url = url

    # Check shortener cache for generic shorteners
    if shortener_cache and url in shortener_cache:
        effective_url = shortener_cache[url]

    # Check brand shortener on effective URL
    brand_domain = is_brand_shortener(effective_url)
    if brand_domain:
        return brand_domain

    # Check original URL's domain via brand map
    orig_domain = extract_domain(url)
    if orig_domain and orig_domain in BRAND_SHORTENERS:
        resolved_domain = BRAND_SHORTENERS[orig_domain]
        if resolved_domain != orig_domain:
            return resolved_domain

    # Use domain from effective URL
    return extract_domain(effective_url)


def resolve_publication(
    url: str,
    index: PublicationIndex,
    graph: Graph,
    shortener_cache: dict[str, str] | None = None,
) -> URIRef | None:
    """Resolve a URL to a Publication URI via 3-tier lookup.

    Tier 1: Reference match — check if URL domain matches a reference publication.
    Tier 2: Brand shortener — static domain→domain map.
    Tier 3: New domain discovery — mint a new data:pub/{slug} Publication.

    Args:
        url: The URL to resolve.
        index: Publication index with reference publications.
        graph: ABox graph to add new Publication triples to.
        shortener_cache: Cache of shortened URL → resolved URL mappings.

    Returns:
        The Publication URI, or None if URL is unparseable.
    """
    domain = _resolve_domain(url, shortener_cache)
    if not domain:
        return None

    # Check existing (reference or previously minted)
    pub = index.get(domain)
    if pub:
        return pub

    # Mint new publication
    return _mint_publication(domain, index, graph)


def _mint_publication(domain: str, index: PublicationIndex, graph: Graph) -> URIRef:
    """Mint a new Publication individual for a discovered domain.

    Args:
        domain: The site domain.
        index: Publication index (updated in place).
        graph: Graph to add triples to.

    Returns:
        The new Publication URI.
    """
    slug = _slugify_domain(domain)
    uri = DATA[f"pub/{slug}"]
    graph.add((uri, RDF.type, ENEWS.Publication))
    graph.add((uri, ENEWS.siteDomain, Literal(domain)))
    graph.add((uri, RDFS.label, Literal(domain, lang="en")))
    index.add(domain, uri)
    return uri
