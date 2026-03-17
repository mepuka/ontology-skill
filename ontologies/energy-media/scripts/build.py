"""Build the Energy Media Ontology from conceptual model artifacts.

Reads glossary.csv and conceptual-model.yaml to produce:
  - energy-media.ttl (TBox: classes, properties, axioms, alignment)
  - energy-media-chart-types.ttl (SKOS ChartTypeScheme individuals)
  - energy-media-providers.ttl (SKOS AltTextProvenanceScheme +
                                 EnergyDataProvider individuals)
  - shapes/energy-media-shapes.ttl (SHACL structural shapes)

Usage:
    uv run python ontologies/energy-media/scripts/build.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

if TYPE_CHECKING:
    from rdflib.term import Node

# ---------------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------------

EMEDIA = Namespace("http://example.org/ontology/energy-media#")
ENEWS = Namespace("http://example.org/ontology/energy-news#")
SCHEMA = Namespace("https://schema.org/")
SH = Namespace("http://www.w3.org/ns/shacl#")
OBO = Namespace("http://purl.obolibrary.org/obo/")
PROV = Namespace("http://www.w3.org/ns/prov#")

# Ontology IRIs
TBOX_IRI = URIRef("http://example.org/ontology/energy-media")
CHART_TYPES_IRI = URIRef("http://example.org/ontology/energy-media/chart-types")
PROVIDERS_IRI = URIRef("http://example.org/ontology/energy-media/providers")
ENEWS_IRI = URIRef("http://example.org/ontology/energy-news")

TBOX_VERSION_IRI = URIRef("http://example.org/ontology/energy-media/0.1.0")
CHART_TYPES_VERSION_IRI = URIRef("http://example.org/ontology/energy-media/chart-types/0.1.0")
PROVIDERS_VERSION_IRI = URIRef("http://example.org/ontology/energy-media/providers/0.1.0")

# Ontology project root (ontologies/energy-media/)
PROJECT = Path(__file__).resolve().parent.parent
DOCS = PROJECT / "docs"
OUT = PROJECT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def bind_common_prefixes(g: Graph) -> None:
    """Bind standard prefixes to a graph."""
    g.bind("emedia", EMEDIA)
    g.bind("enews", ENEWS)
    g.bind("owl", OWL)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    g.bind("schema", SCHEMA)
    g.bind("obo", OBO)
    g.bind("prov", PROV)


def load_glossary() -> list[dict[str, str]]:
    """Load glossary.csv and return rows as dicts."""
    path = DOCS / "glossary.csv"
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader if row.get("Term")]


def load_yaml(name: str) -> dict[str, Any]:
    """Load a YAML file from the project docs/ directory."""
    path = DOCS / name
    with path.open(encoding="utf-8") as f:
        result: dict[str, Any] = yaml.safe_load(f)
    return result


def to_label(term: str) -> str:
    """Convert CamelCase term to lowercase label with spaces.

    E.g. 'EnergyTopic' -> 'energy topic', 'SMR' -> 'smr',
    'EVCharging' -> 'ev charging'.
    """
    result: list[str] = []
    for i, ch in enumerate(term):
        if ch.isupper() and i > 0:
            prev = term[i - 1]
            if prev.islower() or (prev.isupper() and i + 1 < len(term) and term[i + 1].islower()):
                result.append(" ")
        result.append(ch.lower())
    return "".join(result)


# ---------------------------------------------------------------------------
# TBox Builder
# ---------------------------------------------------------------------------


def build_tbox(glossary: list[dict[str, str]], model: dict) -> Graph:
    """Build the TBox graph with classes, properties, and axioms."""
    g = Graph()
    bind_common_prefixes(g)

    # --- Ontology header ---
    g.add((TBOX_IRI, RDF.type, OWL.Ontology))
    g.add((TBOX_IRI, OWL.versionIRI, TBOX_VERSION_IRI))
    g.add((TBOX_IRI, OWL.imports, ENEWS_IRI))
    g.add((TBOX_IRI, OWL.imports, CHART_TYPES_IRI))
    g.add((TBOX_IRI, OWL.imports, PROVIDERS_IRI))
    g.add((TBOX_IRI, DCTERMS.title, Literal("Energy Media Ontology", lang="en")))
    g.add(
        (
            TBOX_IRI,
            DCTERMS.description,
            Literal(
                "A lightweight OWL 2 DL ontology modeling media attachments, chart "
                "semantics, and energy data provenance for social media posts in the "
                "energy domain.",
                lang="en",
            ),
        )
    )
    g.add((TBOX_IRI, OWL.versionInfo, Literal("0.1.0")))
    g.add((TBOX_IRI, DCTERMS.created, Literal("2026-03-17")))
    g.add((TBOX_IRI, DCTERMS.modified, Literal("2026-03-17")))
    g.add((TBOX_IRI, DCTERMS.creator, Literal("ontology-architect skill")))
    g.add((TBOX_IRI, DCTERMS.license, URIRef("https://spdx.org/licenses/MIT")))

    # --- Classes ---
    class_glossary = {row["Term"]: row for row in glossary if row["Category"] == "Class"}

    _add_classes(g, class_glossary, model)
    _add_properties(g, glossary)

    return g


def _add_classes(g: Graph, class_glossary: dict[str, dict[str, str]], model: dict) -> None:
    """Add OWL classes, alignment axioms, BFO alignment, and disjointness."""
    class_hierarchy = model["class_hierarchy"]

    # Schema alignment mapping (from conceptual model)
    schema_alignment: dict[str, URIRef] = {
        "MediaAttachment": SCHEMA.MediaObject,
        "Chart": SCHEMA.ImageObject,
        "Photo": SCHEMA.ImageObject,
        "VideoAttachment": SCHEMA.VideoObject,
        "EnergyDataProvider": SCHEMA.Organization,
        "EnergyDataset": SCHEMA.Dataset,
    }

    # BFO alignment mapping
    bfo_map: dict[str, URIRef] = {
        "MediaAttachment": OBO.BFO_0000031,  # GDC
        "Chart": OBO.BFO_0000031,  # GDC
        "DocumentExcerpt": OBO.BFO_0000031,  # GDC
        "Photo": OBO.BFO_0000031,  # GDC
        "Infographic": OBO.BFO_0000031,  # GDC
        "VideoAttachment": OBO.BFO_0000031,  # GDC
        "ChartAxis": OBO.BFO_0000031,  # GDC
        "ChartSeries": OBO.BFO_0000031,  # GDC
        "ChartSourceLine": OBO.BFO_0000031,  # GDC
        "EnergyDataProvider": OBO.BFO_0000030,  # Object
        "EnergyDataset": OBO.BFO_0000031,  # GDC
    }

    # Parent class mapping
    parent_map: dict[str, URIRef | None] = {
        "MediaAttachment": None,  # parent is owl:Thing (no explicit subClassOf)
        "Chart": EMEDIA.MediaAttachment,
        "DocumentExcerpt": EMEDIA.MediaAttachment,
        "Photo": EMEDIA.MediaAttachment,
        "Infographic": EMEDIA.MediaAttachment,
        "VideoAttachment": EMEDIA.MediaAttachment,
        "ChartAxis": None,
        "ChartSeries": None,
        "ChartSourceLine": None,
        "EnergyDataProvider": None,
        "EnergyDataset": None,
    }

    for entry in class_hierarchy:
        cls_name = entry["class"]
        cls_uri = EMEDIA[cls_name]
        g.add((cls_uri, RDF.type, OWL.Class))
        g.add((cls_uri, RDFS.label, Literal(to_label(cls_name), lang="en")))

        # Definition from glossary
        if cls_name in class_glossary:
            defn = class_glossary[cls_name]["Definition"]
            g.add((cls_uri, SKOS.definition, Literal(defn, lang="en")))

        # Parent class (subClassOf)
        parent = parent_map.get(cls_name)
        if parent is not None:
            g.add((cls_uri, RDFS.subClassOf, parent))

        # Schema alignment (rdfs:subClassOf)
        if cls_name in schema_alignment:
            g.add((cls_uri, RDFS.subClassOf, schema_alignment[cls_name]))

        # BFO alignment
        if cls_name in bfo_map:
            g.add((cls_uri, RDFS.subClassOf, bfo_map[cls_name]))

    # --- AllDisjointClasses ---
    disjoint_groups = model["top_level_disjoint_groups"]
    for group in disjoint_groups:
        class_names = group["classes"]
        disjoint_node = BNode()
        g.add((disjoint_node, RDF.type, OWL.AllDisjointClasses))
        class_uris: list[Node] = [EMEDIA[name] for name in class_names]
        class_list = BNode()
        Collection(g, class_list, class_uris)
        g.add((disjoint_node, OWL.members, class_list))


def _add_properties(g: Graph, glossary: list[dict[str, str]]) -> None:
    """Add object properties and datatype properties to the TBox."""
    # Build glossary lookup for definitions
    prop_glossary = {
        row["Term"]: row
        for row in glossary
        if row["Category"] in ("ObjectProperty", "DataProperty")
    }

    # --- Object Properties ---
    object_properties: list[dict[str, Any]] = [
        {
            "name": "hasMediaAttachment",
            "domain": ("enews", "Post"),
            "range": ("emedia", "MediaAttachment"),
            "characteristics": [],
        },
        {
            "name": "chartType",
            "domain": ("emedia", "Chart"),
            "range": ("skos", "Concept"),
            "characteristics": ["functional"],
        },
        {
            "name": "hasXAxis",
            "domain": ("emedia", "Chart"),
            "range": ("emedia", "ChartAxis"),
            "characteristics": ["functional"],
        },
        {
            "name": "hasYAxis",
            "domain": ("emedia", "Chart"),
            "range": ("emedia", "ChartAxis"),
            "characteristics": ["functional"],
        },
        {
            "name": "hasSeries",
            "domain": ("emedia", "Chart"),
            "range": ("emedia", "ChartSeries"),
            "characteristics": [],
        },
        {
            "name": "hasSourceLine",
            "domain": ("emedia", "Chart"),
            "range": ("emedia", "ChartSourceLine"),
            "characteristics": [],
        },
        {
            "name": "altTextProvenance",
            "domain": ("emedia", "MediaAttachment"),
            "range": ("skos", "Concept"),
            "characteristics": ["functional"],
        },
        {
            "name": "providedBy",
            "domain": ("emedia", "EnergyDataset"),
            "range": ("emedia", "EnergyDataProvider"),
            "characteristics": ["functional"],
        },
    ]

    ns_map: dict[str, Namespace] = {
        "emedia": EMEDIA,
        "enews": ENEWS,
        "skos": SKOS,
    }

    for prop in object_properties:
        prop_uri = EMEDIA[prop["name"]]
        g.add((prop_uri, RDF.type, OWL.ObjectProperty))
        g.add((prop_uri, RDFS.label, Literal(to_label(prop["name"]), lang="en")))

        # Definition from glossary
        if prop["name"] in prop_glossary:
            defn = prop_glossary[prop["name"]]["Definition"]
            g.add((prop_uri, SKOS.definition, Literal(defn, lang="en")))

        # Domain
        if prop.get("domain"):
            ns_prefix, local_name = prop["domain"]
            g.add((prop_uri, RDFS.domain, ns_map[ns_prefix][local_name]))

        # Range
        if prop.get("range"):
            ns_prefix, local_name = prop["range"]
            g.add((prop_uri, RDFS.range, ns_map[ns_prefix][local_name]))

        # Characteristics
        if "functional" in prop.get("characteristics", []):
            g.add((prop_uri, RDF.type, OWL.FunctionalProperty))

    # --- Reused external properties (declare as ObjectProperty in our graph) ---
    # prov:wasAttributedTo, prov:wasDerivedFrom
    for ext_prop in [PROV.wasAttributedTo, PROV.wasDerivedFrom]:
        g.add((ext_prop, RDF.type, OWL.ObjectProperty))

    # dcterms:source, dcterms:temporal, dcterms:spatial
    for ext_prop in [DCTERMS.source, DCTERMS.temporal, DCTERMS.spatial]:
        g.add((ext_prop, RDF.type, OWL.ObjectProperty))

    # --- Datatype Properties ---
    xsd_type_map = {
        "xsd:string": XSD.string,
        "xsd:anyURI": XSD.anyURI,
    }

    datatype_properties: list[dict[str, str | list[str]]] = [
        {
            "name": "altText",
            "domain": "MediaAttachment",
            "range": "xsd:string",
            "characteristics": ["functional"],
        },
        {
            "name": "mediaUrl",
            "domain": "MediaAttachment",
            "range": "xsd:anyURI",
            "characteristics": ["functional"],
        },
        {
            "name": "thumbnailUrl",
            "domain": "MediaAttachment",
            "range": "xsd:anyURI",
            "characteristics": ["functional"],
        },
        {
            "name": "axisLabel",
            "domain": "ChartAxis",
            "range": "xsd:string",
            "characteristics": ["functional"],
        },
        {
            "name": "axisUnit",
            "domain": "ChartAxis",
            "range": "xsd:string",
            "characteristics": ["functional"],
        },
        {
            "name": "seriesUnit",
            "domain": "ChartSeries",
            "range": "xsd:string",
            "characteristics": ["functional"],
        },
        {
            "name": "legendLabel",
            "domain": "ChartSeries",
            "range": "xsd:string",
            "characteristics": ["functional"],
        },
        {
            "name": "sourceText",
            "domain": "ChartSourceLine",
            "range": "xsd:string",
            "characteristics": ["functional"],
        },
        {
            "name": "keyFinding",
            "domain": "Chart",
            "range": "xsd:string",
            "characteristics": [],
        },
    ]

    for prop in datatype_properties:
        prop_name = str(prop["name"])
        prop_uri = EMEDIA[prop_name]
        g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
        g.add((prop_uri, RDFS.label, Literal(to_label(prop_name), lang="en")))

        # Definition from glossary
        if prop_name in prop_glossary:
            defn = prop_glossary[prop_name]["Definition"]
            g.add((prop_uri, SKOS.definition, Literal(defn, lang="en")))

        g.add((prop_uri, RDFS.domain, EMEDIA[str(prop["domain"])]))
        g.add((prop_uri, RDFS.range, xsd_type_map[str(prop["range"])]))

        characteristics = prop.get("characteristics", [])
        if isinstance(characteristics, list) and "functional" in characteristics:
            g.add((prop_uri, RDF.type, OWL.FunctionalProperty))

    # --- Existential Restrictions ---
    # Chart SubClassOf chartType some skos:Concept
    _add_existential(g, EMEDIA.Chart, EMEDIA.chartType, SKOS.Concept)
    # MediaAttachment SubClassOf hasMediaAttachment^- some enews:Post (inverse)
    # Instead: Post SubClassOf hasMediaAttachment some MediaAttachment
    # (this is implicit from the domain/range; add explicit restriction on Chart)
    _add_existential(g, EMEDIA.Chart, EMEDIA.hasXAxis, EMEDIA.ChartAxis)
    _add_existential(g, EMEDIA.Chart, EMEDIA.hasYAxis, EMEDIA.ChartAxis)
    _add_existential(g, EMEDIA.EnergyDataset, EMEDIA.providedBy, EMEDIA.EnergyDataProvider)


def _add_existential(g: Graph, cls: URIRef, prop: URIRef, filler: URIRef) -> None:
    """Add: cls SubClassOf prop some filler (OWL existential restriction)."""
    restriction = BNode()
    g.add((restriction, RDF.type, OWL.Restriction))
    g.add((restriction, OWL.onProperty, prop))
    g.add((restriction, OWL.someValuesFrom, filler))
    g.add((cls, RDFS.subClassOf, restriction))


# ---------------------------------------------------------------------------
# Chart Types Builder (SKOS Individuals)
# ---------------------------------------------------------------------------


def build_chart_types(model: dict) -> Graph:
    """Build the ChartTypeScheme SKOS concept scheme with chart type individuals."""
    g = Graph()
    bind_common_prefixes(g)

    # --- Ontology header ---
    g.add((CHART_TYPES_IRI, RDF.type, OWL.Ontology))
    g.add((CHART_TYPES_IRI, OWL.versionIRI, CHART_TYPES_VERSION_IRI))
    g.add(
        (
            CHART_TYPES_IRI,
            DCTERMS.title,
            Literal("Energy Media Ontology — Chart Type Scheme", lang="en"),
        )
    )
    g.add(
        (
            CHART_TYPES_IRI,
            DCTERMS.description,
            Literal(
                "SKOS concept scheme classifying chart and visualization structural "
                "forms for the Energy Media Ontology.",
                lang="en",
            ),
        )
    )
    g.add((CHART_TYPES_IRI, OWL.versionInfo, Literal("0.1.0")))
    g.add((CHART_TYPES_IRI, DCTERMS.created, Literal("2026-03-17")))
    g.add((CHART_TYPES_IRI, DCTERMS.modified, Literal("2026-03-17")))
    g.add((CHART_TYPES_IRI, DCTERMS.creator, Literal("ontology-architect skill")))
    g.add((CHART_TYPES_IRI, DCTERMS.license, URIRef("https://spdx.org/licenses/MIT")))

    # Find the ChartTypeScheme in conceptual model
    chart_type_scheme = _find_scheme(model, "emedia:ChartTypeScheme")

    # --- Concept Scheme ---
    scheme_uri = EMEDIA.ChartTypeScheme
    g.add((scheme_uri, RDF.type, SKOS.ConceptScheme))
    g.add((scheme_uri, RDFS.label, Literal(chart_type_scheme["label"], lang="en")))
    g.add(
        (
            scheme_uri,
            SKOS.definition,
            Literal(chart_type_scheme["description"].strip(), lang="en"),
        )
    )

    # --- Individuals ---
    all_names: list[str] = []
    for ind in chart_type_scheme["individuals"]:
        name = ind["individual"]
        all_names.append(name)
        _add_skos_individual(g, name, ind, scheme_uri)

    # --- AllDifferent ---
    if len(all_names) > 1:
        diff_node = BNode()
        g.add((diff_node, RDF.type, OWL.AllDifferent))
        members: list[Node] = [EMEDIA[n] for n in all_names]
        member_list = BNode()
        Collection(g, member_list, members)
        g.add((diff_node, OWL.distinctMembers, member_list))

    return g


# ---------------------------------------------------------------------------
# Providers Builder (AltTextProvenanceScheme + EnergyDataProvider individuals)
# ---------------------------------------------------------------------------


def build_providers(model: dict) -> Graph:
    """Build the providers graph with AltTextProvenanceScheme
    and EnergyDataProvider individuals."""
    g = Graph()
    bind_common_prefixes(g)

    # --- Ontology header ---
    g.add((PROVIDERS_IRI, RDF.type, OWL.Ontology))
    g.add((PROVIDERS_IRI, OWL.versionIRI, PROVIDERS_VERSION_IRI))
    g.add(
        (
            PROVIDERS_IRI,
            DCTERMS.title,
            Literal("Energy Media Ontology — Providers & Alt Text Provenance", lang="en"),
        )
    )
    g.add(
        (
            PROVIDERS_IRI,
            DCTERMS.description,
            Literal(
                "SKOS concept scheme for alt text provenance "
                "and EnergyDataProvider individuals for the Energy Media Ontology.",
                lang="en",
            ),
        )
    )
    g.add((PROVIDERS_IRI, OWL.versionInfo, Literal("0.1.0")))
    g.add((PROVIDERS_IRI, DCTERMS.created, Literal("2026-03-17")))
    g.add((PROVIDERS_IRI, DCTERMS.modified, Literal("2026-03-17")))
    g.add((PROVIDERS_IRI, DCTERMS.creator, Literal("ontology-architect skill")))
    g.add((PROVIDERS_IRI, DCTERMS.license, URIRef("https://spdx.org/licenses/MIT")))

    # --- AltTextProvenanceScheme ---
    alt_scheme_data = _find_scheme(model, "emedia:AltTextProvenanceScheme")
    alt_scheme_uri = EMEDIA.AltTextProvenanceScheme
    g.add((alt_scheme_uri, RDF.type, SKOS.ConceptScheme))
    g.add(
        (
            alt_scheme_uri,
            RDFS.label,
            Literal(alt_scheme_data["label"], lang="en"),
        )
    )
    g.add(
        (
            alt_scheme_uri,
            SKOS.definition,
            Literal(alt_scheme_data["description"].strip(), lang="en"),
        )
    )

    alt_names: list[str] = []
    for ind in alt_scheme_data["individuals"]:
        name = ind["individual"]
        alt_names.append(name)
        _add_skos_individual(g, name, ind, alt_scheme_uri)

    # AllDifferent for alt text provenance
    if len(alt_names) > 1:
        diff_node = BNode()
        g.add((diff_node, RDF.type, OWL.AllDifferent))
        members_alt: list[Node] = [EMEDIA[n] for n in alt_names]
        member_list_alt = BNode()
        Collection(g, member_list_alt, members_alt)
        g.add((diff_node, OWL.distinctMembers, member_list_alt))

    # --- EnergyDataProvider individuals ---
    _add_data_provider_individuals(g)

    return g


def _add_data_provider_individuals(g: Graph) -> None:
    """Add well-known EnergyDataProvider individuals."""
    providers: list[dict[str, Any]] = [
        {
            "name": "provider_gridstatus",
            "label": "GridStatus",
            "definition": (
                "An energy data aggregator providing real-time"
                " and historical grid data for North American"
                " ISOs/RTOs."
            ),
        },
        {
            "name": "provider_eia",
            "label": "EIA",
            "definition": (
                "The U.S. Energy Information Administration,"
                " providing comprehensive energy statistics"
                " and analysis."
            ),
        },
        {
            "name": "provider_aeso",
            "label": "AESO",
            "definition": (
                "Alberta Electric System Operator, managing the Alberta electricity market."
            ),
        },
        {
            "name": "provider_ieso",
            "label": "IESO",
            "definition": (
                "Independent Electricity System Operator, managing Ontario's electricity market."
            ),
        },
        {
            "name": "provider_bchydro",
            "label": "BC Hydro",
            "definition": (
                "British Columbia's primary electric utility,"
                " providing generation and transmission data."
            ),
        },
        {
            "name": "provider_entsoe",
            "label": "ENTSO-E",
            "definition": (
                "European Network of Transmission System"
                " Operators for Electricity, providing"
                " pan-European grid data."
            ),
        },
    ]

    provider_uris: list[Node] = []
    for prov in providers:
        uri = EMEDIA[prov["name"]]
        provider_uris.append(uri)
        g.add((uri, RDF.type, EMEDIA.EnergyDataProvider))
        g.add((uri, RDFS.label, Literal(prov["label"], lang="en")))
        g.add((uri, SKOS.definition, Literal(prov["definition"], lang="en")))

    # AllDifferent for providers
    if len(provider_uris) > 1:
        diff_node = BNode()
        g.add((diff_node, RDF.type, OWL.AllDifferent))
        member_list = BNode()
        Collection(g, member_list, provider_uris)
        g.add((diff_node, OWL.distinctMembers, member_list))


# ---------------------------------------------------------------------------
# SKOS Individual Helpers
# ---------------------------------------------------------------------------


def _find_scheme(model: dict, iri: str) -> dict[str, Any]:
    """Find a concept scheme definition in the conceptual model by IRI."""
    for scheme in model["concept_schemes"]:
        if scheme["iri"] == iri:
            return scheme
    msg = f"Concept scheme {iri} not found in conceptual model"
    raise ValueError(msg)


def _add_skos_individual(
    g: Graph,
    name: str,
    ind: dict[str, Any],
    scheme_uri: URIRef,
) -> None:
    """Add a single SKOS concept individual to the graph."""
    uri = EMEDIA[name]
    g.add((uri, RDF.type, SKOS.Concept))
    g.add((uri, SKOS.inScheme, scheme_uri))

    # Use the explicit label from the YAML if provided, otherwise derive from name
    label = ind.get("label", to_label(name))
    g.add((uri, RDFS.label, Literal(label, lang="en")))

    if ind.get("definition"):
        g.add((uri, SKOS.definition, Literal(ind["definition"], lang="en")))

    # Alt labels
    alt_labels = ind.get("altLabel", [])
    if alt_labels:
        for alt in alt_labels:
            g.add((uri, SKOS.altLabel, Literal(alt, lang="en")))

    # Broader relationship
    broader = ind.get("broader")
    if broader:
        g.add((uri, SKOS.broader, EMEDIA[broader]))
    else:
        # Top concept
        g.add((uri, SKOS.topConceptOf, scheme_uri))
        g.add((scheme_uri, SKOS.hasTopConcept, uri))


# ---------------------------------------------------------------------------
# SHACL Shapes Builder
# ---------------------------------------------------------------------------


def build_shacl_shapes() -> Graph:
    """Build SHACL shapes for structural validation."""
    g = Graph()
    bind_common_prefixes(g)
    g.bind("sh", SH)

    # --- MediaAttachmentShape ---
    _add_shape(
        g,
        EMEDIA.MediaAttachmentShape,
        EMEDIA.MediaAttachment,
        [
            _property_shape(g, EMEDIA.mediaUrl, min_count=1, max_count=1, datatype=XSD.anyURI),
            _property_shape(g, EMEDIA.altText, max_count=1, datatype=XSD.string),
            _property_shape(g, EMEDIA.altTextProvenance, max_count=1),
        ],
    )

    # --- ChartShape ---
    _add_shape(
        g,
        EMEDIA.ChartShape,
        EMEDIA.Chart,
        [
            _property_shape(
                g,
                EMEDIA.chartType,
                min_count=1,
                max_count=1,
                class_constraint=SKOS.Concept,
            ),
            _property_shape(g, EMEDIA.hasXAxis, max_count=1),
            _property_shape(g, EMEDIA.hasYAxis, max_count=1),
            _property_shape(g, EMEDIA.hasSeries),
        ],
    )

    # --- ChartAxisShape ---
    _add_shape(
        g,
        EMEDIA.ChartAxisShape,
        EMEDIA.ChartAxis,
        [
            _property_shape(g, EMEDIA.axisLabel, min_count=1, max_count=1, datatype=XSD.string),
            _property_shape(g, EMEDIA.axisUnit, max_count=1, datatype=XSD.string),
        ],
    )

    # --- ChartSeriesShape ---
    _add_shape(
        g,
        EMEDIA.ChartSeriesShape,
        EMEDIA.ChartSeries,
        [
            _min_count_property(g, RDFS.label, 1),
        ],
    )

    # --- EnergyDataProviderShape ---
    _add_shape(
        g,
        EMEDIA.EnergyDataProviderShape,
        EMEDIA.EnergyDataProvider,
        [
            _min_count_property(g, RDFS.label, 1),
        ],
    )

    # --- EnergyDatasetShape ---
    _add_shape(
        g,
        EMEDIA.EnergyDatasetShape,
        EMEDIA.EnergyDataset,
        [
            _min_count_property(g, RDFS.label, 1),
            _property_shape(
                g,
                EMEDIA.providedBy,
                min_count=1,
                max_count=1,
                class_constraint=EMEDIA.EnergyDataProvider,
            ),
        ],
    )

    # --- ChartSourceLineShape ---
    _add_shape(
        g,
        EMEDIA.ChartSourceLineShape,
        EMEDIA.ChartSourceLine,
        [
            _property_shape(g, EMEDIA.sourceText, min_count=1, datatype=XSD.string),
        ],
    )

    # --- DocumentExcerptShape ---
    _add_shape(
        g,
        EMEDIA.DocumentExcerptShape,
        EMEDIA.DocumentExcerpt,
        [],
    )

    # --- InfographicShape ---
    _add_shape(
        g,
        EMEDIA.InfographicShape,
        EMEDIA.Infographic,
        [],
    )

    # --- PhotoShape ---
    _add_shape(
        g,
        EMEDIA.PhotoShape,
        EMEDIA.Photo,
        [],
    )

    # --- VideoAttachmentShape ---
    _add_shape(
        g,
        EMEDIA.VideoAttachmentShape,
        EMEDIA.VideoAttachment,
        [],
    )

    return g


def _add_shape(g: Graph, shape_uri: URIRef, target_class: URIRef, prop_shapes: list[BNode]) -> None:
    """Add a NodeShape targeting a class with property constraints."""
    g.add((shape_uri, RDF.type, SH.NodeShape))
    g.add((shape_uri, SH.targetClass, target_class))
    for ps in prop_shapes:
        g.add((shape_uri, SH.property, ps))


def _min_count_property(g: Graph, path: URIRef, min_count: int) -> BNode:
    """Create a simple min-count property shape."""
    ps = BNode()
    g.add((ps, SH.path, path))
    g.add((ps, SH.minCount, Literal(min_count)))
    return ps


def _property_shape(
    g: Graph,
    path: URIRef,
    min_count: int | None = None,
    max_count: int | None = None,
    datatype: URIRef | None = None,
    class_constraint: URIRef | None = None,
) -> BNode:
    """Create a property shape with optional constraints."""
    ps = BNode()
    g.add((ps, SH.path, path))
    if min_count is not None:
        g.add((ps, SH.minCount, Literal(min_count)))
    if max_count is not None:
        g.add((ps, SH.maxCount, Literal(max_count)))
    if datatype is not None:
        g.add((ps, SH.datatype, datatype))
    if class_constraint is not None:
        g.add((ps, SH["class"], class_constraint))
    return ps


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Build all Energy Media Ontology artifacts."""
    print("Loading input artifacts...")
    glossary = load_glossary()
    model = load_yaml("conceptual-model.yaml")

    print(f"  Glossary: {len(glossary)} terms")
    print(f"  Class hierarchy: {len(model['class_hierarchy'])} classes")
    print(f"  Concept schemes: {len(model['concept_schemes'])} schemes")

    # Ensure output directories exist
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "shapes").mkdir(parents=True, exist_ok=True)

    # Build TBox
    print("\nBuilding TBox (energy-media.ttl)...")
    tbox = build_tbox(glossary, model)
    tbox_path = OUT / "energy-media.ttl"
    tbox.serialize(destination=str(tbox_path), format="turtle")
    print(f"  Written: {tbox_path} ({len(tbox)} triples)")

    # Build Chart Types
    print("Building chart types (energy-media-chart-types.ttl)...")
    chart_types = build_chart_types(model)
    chart_types_path = OUT / "energy-media-chart-types.ttl"
    chart_types.serialize(destination=str(chart_types_path), format="turtle")
    print(f"  Written: {chart_types_path} ({len(chart_types)} triples)")

    # Build Providers
    print("Building providers (energy-media-providers.ttl)...")
    providers = build_providers(model)
    providers_path = OUT / "energy-media-providers.ttl"
    providers.serialize(destination=str(providers_path), format="turtle")
    print(f"  Written: {providers_path} ({len(providers)} triples)")

    # Build SHACL Shapes
    print("Building SHACL shapes (shapes/energy-media-shapes.ttl)...")
    shapes = build_shacl_shapes()
    shapes_path = OUT / "shapes" / "energy-media-shapes.ttl"
    shapes.serialize(destination=str(shapes_path), format="turtle")
    print(f"  Written: {shapes_path} ({len(shapes)} triples)")

    print("\nBuild complete.")


if __name__ == "__main__":
    main()
