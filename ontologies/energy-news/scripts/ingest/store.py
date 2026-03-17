"""Oxigraph triple store management — init, load, query, stats."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pyoxigraph

from .namespaces import GRAPH_ABOX, GRAPH_REFERENCE, GRAPH_SHAPES, GRAPH_TBOX

if TYPE_CHECKING:
    from pathlib import Path

    from rdflib import Graph


def init_store(path: Path) -> pyoxigraph.Store:
    """Create or open an Oxigraph persistent store.

    Args:
        path: Directory for the Oxigraph store files.

    Returns:
        An open Oxigraph Store instance.
    """
    path.mkdir(parents=True, exist_ok=True)
    return pyoxigraph.Store(str(path))


def load_tbox(store: pyoxigraph.Store, ontology_dir: Path) -> dict[str, int]:
    """Load TBox, reference individuals, and shapes into named graphs.

    Args:
        store: The Oxigraph store.
        ontology_dir: Path to the ontology project directory.

    Returns:
        Dict of graph_name → triple count loaded.
    """
    counts: dict[str, int] = {}

    graph_files = {
        GRAPH_TBOX: ontology_dir / "energy-news.ttl",
        GRAPH_REFERENCE: ontology_dir / "energy-news-reference-individuals.ttl",
        GRAPH_SHAPES: ontology_dir / "shapes" / "energy-news-shapes.ttl",
    }

    for graph_name, file_path in graph_files.items():
        if not file_path.exists():
            print(f"  Warning: {file_path} not found, skipping")
            continue

        named_graph = pyoxigraph.NamedNode(graph_name)
        ttl = file_path.read_text(encoding="utf-8")
        store.load(
            ttl.encode("utf-8"),
            "text/turtle",
            to_graph=named_graph,
        )
        count = _count_triples_in_graph(store, graph_name)
        counts[graph_name] = count
        print(f"  Loaded {file_path.name}: {count} triples → <{graph_name}>")

    return counts


def load_abox(store: pyoxigraph.Store, abox_graph: Graph) -> int:
    """Load an rdflib ABox graph into the Oxigraph abox named graph.

    Args:
        store: The Oxigraph store.
        abox_graph: rdflib Graph with ABox triples.

    Returns:
        Number of triples loaded.
    """
    named_graph = pyoxigraph.NamedNode(GRAPH_ABOX)
    ttl = abox_graph.serialize(format="turtle")
    store.load(
        ttl.encode("utf-8") if isinstance(ttl, str) else ttl,
        "text/turtle",
        to_graph=named_graph,
    )
    return _count_triples_in_graph(store, GRAPH_ABOX)


def query(store: pyoxigraph.Store, sparql: str) -> list[pyoxigraph.QuerySolution]:
    """Run a SPARQL SELECT query against the store.

    Args:
        store: The Oxigraph store.
        sparql: SPARQL query string.

    Returns:
        List of query solution rows.
    """
    results = store.query(sparql)
    return list(results)


def stats(store: pyoxigraph.Store) -> dict[str, int]:
    """Get triple counts per named graph.

    Args:
        store: The Oxigraph store.

    Returns:
        Dict of graph_name → triple count, plus 'total'.
    """
    graph_names = [GRAPH_TBOX, GRAPH_REFERENCE, GRAPH_SHAPES, GRAPH_ABOX]
    counts: dict[str, int] = {}

    for name in graph_names:
        counts[name] = _count_triples_in_graph(store, name)

    # Total across all named graphs
    total_sparql = "SELECT (COUNT(*) AS ?n) WHERE { GRAPH ?g { ?s ?p ?o } }"
    for row in store.query(total_sparql):
        counts["total"] = int(row[0].value)
        break

    return counts


def _count_triples_in_graph(store: pyoxigraph.Store, graph_name: str) -> int:
    """Count triples in a specific named graph."""
    sparql = f"SELECT (COUNT(*) AS ?n) WHERE {{ GRAPH <{graph_name}> {{ ?s ?p ?o }} }}"
    for row in store.query(sparql):
        return int(row[0].value)
    return 0
