"""Proof-of-concept: generate TypeScript type information from SHACL shapes.

Reads the SHACL shapes file, extracts sh:in lists from per-scheme shapes,
and outputs a summary showing what TypeScript types would be generated.
This demonstrates that SHACL can serve as the canonical schema bridging
the RDF ontology and the TypeScript product code.

Usage:
    uv run python scripts/generate_types_from_shacl.py
"""

from __future__ import annotations

import json
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection

SH = Namespace("http://www.w3.org/ns/shacl#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SEVOCAB_SHAPES = Namespace("https://skygest.dev/vocab/energy/shapes/")
SEVOCAB = Namespace("https://skygest.dev/vocab/energy/")

SHAPES_FILE = Path(__file__).parent.parent / "shapes" / "skygest-energy-vocab-shapes.ttl"

# Maps shape IRIs to TypeScript type names and whether they are closed enums
SHAPE_TO_TS_TYPE: dict[str, dict[str, str | bool]] = {
    str(SEVOCAB_SHAPES.StatisticTypeConceptShape): {
        "tsName": "StatisticType",
        "closedEnum": True,
        "schemaLiterals": True,
    },
    str(SEVOCAB_SHAPES.AggregationConceptShape): {
        "tsName": "Aggregation",
        "closedEnum": True,
        "schemaLiterals": True,
    },
    str(SEVOCAB_SHAPES.UnitFamilyConceptShape): {
        "tsName": "UnitFamily",
        "closedEnum": True,
        "schemaLiterals": True,
    },
    str(SEVOCAB_SHAPES.TechnologyOrFuelConceptShape): {
        "tsName": "TechnologyOrFuel",
        "closedEnum": False,
        "schemaLiterals": False,
    },
    str(SEVOCAB_SHAPES.MeasuredPropertyConceptShape): {
        "tsName": "MeasuredProperty",
        "closedEnum": False,
        "schemaLiterals": False,
    },
    str(SEVOCAB_SHAPES.DomainObjectConceptShape): {
        "tsName": "DomainObject",
        "closedEnum": False,
        "schemaLiterals": False,
    },
    str(SEVOCAB_SHAPES.FrequencyConceptShape): {
        "tsName": "Frequency",
        "closedEnum": False,
        "schemaLiterals": False,
    },
}


def extract_sh_in_values(g: Graph) -> dict[str, list[str]]:
    """Extract sh:in lists from per-scheme NodeShapes.

    Returns a dict mapping shape IRI -> sorted list of canonical string values.
    """
    result: dict[str, list[str]] = {}

    for shape_iri_str in SHAPE_TO_TS_TYPE:
        shape = URIRef(shape_iri_str)

        # Find property shapes with sh:in
        for prop_shape in g.objects(shape, SH.property):
            in_list_head = g.value(prop_shape, SH["in"])
            if in_list_head is None:
                continue

            # Parse the RDF collection (list)
            values: list[str] = [
                str(item) for item in Collection(g, in_list_head) if isinstance(item, Literal)
            ]

            if values:
                result[shape_iri_str] = sorted(values)

    return result


def generate_typescript_summary(
    shape_values: dict[str, list[str]],
) -> str:
    """Generate a summary of TypeScript types that would be produced."""
    lines: list[str] = []
    lines.append("// =============================================================")
    lines.append("// Generated from SHACL shapes (proof-of-concept)")
    lines.append("// Source: shapes/skygest-energy-vocab-shapes.ttl")
    lines.append("// =============================================================")
    lines.append("")
    lines.append('import { Schema } from "effect";')
    lines.append("")

    for shape_iri, config in SHAPE_TO_TS_TYPE.items():
        ts_name = config["tsName"]
        values = shape_values.get(shape_iri, [])

        if not values:
            lines.append(f"// WARNING: No sh:in values found for {ts_name}")
            lines.append("")
            continue

        if config["schemaLiterals"]:
            # Closed enum: generate Schema.Literals
            quoted = ", ".join(f'"{v}"' for v in values)
            lines.append(f"export const {ts_name} = Schema.Literals([")
            lines.append(f"  {quoted}")
            lines.append("]);")
            lines.append(f"export type {ts_name} = Schema.Schema.Type<typeof {ts_name}>;")
        else:
            # Open vocabulary: generate type union + const array
            lines.append("// Open vocabulary — canonical values from SHACL sh:in")
            lines.append(f"export const {ts_name}Canonicals = [")
            lines.extend(f'  "{v}",' for v in values)
            lines.append("] as const;")
            lines.append(f"export type {ts_name}Canonical = typeof {ts_name}Canonicals[number];")

        lines.append("")

    return "\n".join(lines)


def generate_json_manifest(shape_values: dict[str, list[str]]) -> dict[str, object]:
    """Generate a JSON manifest of scheme -> canonical values for build tooling."""
    manifest: dict[str, object] = {}
    for shape_iri, config in SHAPE_TO_TS_TYPE.items():
        ts_name = str(config["tsName"])
        values = shape_values.get(shape_iri, [])
        manifest[ts_name] = {
            "canonicalValues": values,
            "closedEnum": config["closedEnum"],
            "count": len(values),
        }
    return manifest


def main() -> None:
    """Read SHACL shapes and output code generation summary."""
    g = Graph()
    g.parse(SHAPES_FILE, format="turtle")

    shape_values = extract_sh_in_values(g)

    # Print summary
    print("=" * 70)
    print("SHACL-to-TypeScript Code Generation Proof-of-Concept")
    print("=" * 70)
    print()

    total_values = 0
    for shape_iri, config in SHAPE_TO_TS_TYPE.items():
        ts_name = config["tsName"]
        values = shape_values.get(shape_iri, [])
        total_values += len(values)
        is_closed = config["schemaLiterals"]
        enum_type = "closed enum (Schema.Literals)" if is_closed else "open vocabulary"
        print(f"  {ts_name}: {len(values)} canonical values ({enum_type})")
        for v in values:
            print(f"    - {v}")
        print()

    print(f"Total canonical values across all schemes: {total_values}")
    print()

    # Generate TypeScript preview
    print("-" * 70)
    print("TypeScript output preview:")
    print("-" * 70)
    ts_output = generate_typescript_summary(shape_values)
    print(ts_output)

    # Generate JSON manifest
    print()
    print("-" * 70)
    print("JSON manifest (for build tooling):")
    print("-" * 70)
    manifest = generate_json_manifest(shape_values)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
