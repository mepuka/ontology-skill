"""Shared namespace constants for the Energy News ABox ETL pipeline."""

from __future__ import annotations

from rdflib import Graph, Namespace
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

ENEWS = Namespace("http://example.org/ontology/energy-news#")
DATA = Namespace("http://example.org/data/")
SCHEMA = Namespace("https://schema.org/")
SIOC = Namespace("http://rdfs.org/sioc/ns#")
SH = Namespace("http://www.w3.org/ns/shacl#")
OBO = Namespace("http://purl.obolibrary.org/obo/")

# Named graph URIs for Oxigraph
GRAPH_TBOX = "urn:enews:graph:tbox"
GRAPH_REFERENCE = "urn:enews:graph:reference"
GRAPH_SHAPES = "urn:enews:graph:shapes"
GRAPH_ABOX = "urn:enews:graph:abox"


def bind_abox_prefixes(g: Graph) -> None:
    """Bind standard prefixes plus the data namespace to a graph."""
    g.bind("enews", ENEWS)
    g.bind("data", DATA)
    g.bind("owl", OWL)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    g.bind("schema", SCHEMA)
    g.bind("sioc", SIOC)
    g.bind("obo", OBO)
