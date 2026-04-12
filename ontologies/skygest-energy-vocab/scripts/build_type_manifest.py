"""Build a deterministic SHACL manifest for the Skygest energy profile."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import QB

if TYPE_CHECKING:
    from collections.abc import Iterable

SH = Namespace("http://www.w3.org/ns/shacl#")
SEVOCAB = Namespace("https://skygest.dev/vocab/energy/")
SEVOCAB_SHAPES = Namespace("https://skygest.dev/vocab/energy/shapes/")

REPO_ROOT = Path(__file__).resolve().parents[3]
VOCAB_DIR = Path(__file__).resolve().parents[1]
ONTOLOGY_FILE = VOCAB_DIR / "skygest-energy-vocab.ttl"
SHAPES_FILE = VOCAB_DIR / "shapes" / "skygest-energy-vocab-shapes.ttl"
DEFAULT_OUTPUT = VOCAB_DIR / "build" / "shacl-manifest.json"

FACET_KEYS = [
    "measuredProperty",
    "domainObject",
    "technologyOrFuel",
    "statisticType",
    "aggregation",
    "unitFamily",
    "policyInstrument",
]
REQUIRED_FACET_KEYS = ["measuredProperty", "statisticType"]

CLOSED_ENUMS = {
    "StatisticType": {
        "shape": URIRef(SEVOCAB_SHAPES.StatisticTypeConceptShape),
        "expected": ["stock", "flow", "price", "share", "count"],
    },
    "Aggregation": {
        "shape": URIRef(SEVOCAB_SHAPES.AggregationConceptShape),
        "expected": [
            "point",
            "end_of_period",
            "sum",
            "average",
            "max",
            "min",
            "settlement",
        ],
    },
    "UnitFamily": {
        "shape": URIRef(SEVOCAB_SHAPES.UnitFamilyConceptShape),
        "expected": [
            "power",
            "energy",
            "currency",
            "currency_per_energy",
            "mass_co2e",
            "intensity",
            "dimensionless",
            "other",
        ],
    },
}

PATH_TO_FACET = {
    str(SEVOCAB.measuredProperty): "measuredProperty",
    str(SEVOCAB.domainObject): "domainObject",
    str(SEVOCAB.technologyOrFuel): "technologyOrFuel",
    str(SEVOCAB.statisticType): "statisticType",
    str(SEVOCAB.aggregation): "aggregation",
    str(SEVOCAB.unitFamily): "unitFamily",
    str(SEVOCAB.policyInstrument): "policyInstrument",
}


def git_output(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()


def compute_input_hash(paths: Iterable[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path.relative_to(REPO_ROOT)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def extract_closed_enum_values(graph: Graph, shape: URIRef) -> list[str]:
    for prop_shape in graph.objects(shape, SH.property):
        in_list_head = graph.value(prop_shape, SH["in"])
        if in_list_head is None:
            continue
        return [str(item) for item in Collection(graph, in_list_head) if isinstance(item, Literal)]
    raise ValueError(f"No sh:in list found for {shape}")


def extract_required_facets(graph: Graph) -> set[str]:
    required: set[str] = set()
    energy_variable_shape = URIRef(SEVOCAB_SHAPES.EnergyVariableShape)
    for prop_shape in graph.objects(energy_variable_shape, SH.property):
        min_count = graph.value(prop_shape, SH.minCount)
        path = graph.value(prop_shape, SH.path)
        if min_count is None or path is None:
            continue
        try:
            count = int(min_count)
        except (TypeError, ValueError):
            continue
        facet = PATH_TO_FACET.get(str(path))
        if facet is not None and count >= 1:
            required.add(facet)
    return required


def extract_dsd_facets(graph: Graph) -> set[str]:
    facets: set[str] = set()
    for component in graph.objects(SEVOCAB.EnergyVariableStructure, QB.component):
        dimension = graph.value(component, QB.dimension)
        if dimension is None:
            continue
        facet = PATH_TO_FACET.get(str(dimension))
        if facet is not None:
            facets.add(facet)
    return facets


def build_manifest() -> dict[str, object]:
    shapes_graph = Graph()
    shapes_graph.parse(SHAPES_FILE, format="turtle")

    ontology_graph = Graph()
    ontology_graph.parse(ONTOLOGY_FILE, format="turtle")

    dsd_facets = extract_dsd_facets(ontology_graph)
    if dsd_facets != set(FACET_KEYS):
        raise ValueError(
            f"EnergyVariableStructure dimensions {sorted(dsd_facets)} "
            f"do not match expected {FACET_KEYS}"
        )

    required_facets = extract_required_facets(shapes_graph)
    if required_facets != set(REQUIRED_FACET_KEYS):
        raise ValueError(
            f"EnergyVariableShape required facets {sorted(required_facets)} "
            f"do not match expected {REQUIRED_FACET_KEYS}"
        )

    closed_enums: dict[str, object] = {}
    for name, config in CLOSED_ENUMS.items():
        values = extract_closed_enum_values(shapes_graph, config["shape"])
        expected = config["expected"]
        if values != expected:
            raise ValueError(f"{name} values {values} do not match expected order {expected}")
        closed_enums[name] = {
            "shapeIri": str(config["shape"]),
            "values": values,
        }

    source_commit = git_output("rev-parse", "HEAD")
    generated_at = git_output("show", "-s", "--format=%cI", "HEAD")
    input_hash = compute_input_hash([ONTOLOGY_FILE, SHAPES_FILE])

    return {
        "manifestVersion": 1,
        "sourceCommit": source_commit,
        "generatedAt": generated_at,
        "inputHash": input_hash,
        "facetKeys": FACET_KEYS,
        "requiredFacetKeys": REQUIRED_FACET_KEYS,
        "closedEnums": closed_enums,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = build_manifest()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
