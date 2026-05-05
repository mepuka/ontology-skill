"""Build imports/oeo-topic-subset.ttl from imports/oeo-full.owl.

V2 architect deliverable per:
- /Users/pooks/Dev/ontology_skill/ontologies/energy-intel/docs/oeo-import-rebuild-plan.md
- /Users/pooks/Dev/ontology_skill/docs/HANDOFF-2026-05-04-editorial-extension.md

Pipeline:
1. ROBOT extract --method BOT against the 41-IRI seed list.
2. ROBOT remove pass to strip BFO+RO leak terms (per imports/upper-axiom-leak-terms.txt).
   Mirrors V1's build_v1_imports.py:run_robot_remove (--trim true --preserve-structure false).
3. Add owl:Ontology header so robot merge sees a named module.
4. Verify all 41 seed IRIs survived the strip and remain owl:Class.
5. Run granularity contract validator (CQ-T3) — fail if any value is
   bare owl:NamedIndividual without owl:Class or skos:Concept typing.

Run via: uv run python ontologies/energy-intel/scripts/extract_oeo_topic_subset.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, SKOS, XSD

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parents[1]
IMPORTS_DIR = PROJECT_ROOT / "imports"
ROBOT = WORKSPACE_ROOT / ".local" / "bin" / "robot"

OEO_FULL = IMPORTS_DIR / "oeo-full.owl"
SEEDS = IMPORTS_DIR / "oeo-topic-seeds.txt"
BFO_STRIP = IMPORTS_DIR / "bfo-terms-to-remove.txt"
UPPER_STRIP = IMPORTS_DIR / "upper-axiom-leak-terms.txt"

OUTPUT = IMPORTS_DIR / "oeo-topic-subset.ttl"

ONTOLOGY_IRI = URIRef("https://w3id.org/energy-intel/imports/oeo-topic-subset")
OEO = Namespace("https://openenergyplatform.org/ontology/oeo/")


def _run_robot(*args: str | Path) -> None:
    cmd = [str(ROBOT), *map(str, args)]
    print(f"$ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, check=True)  # noqa: S603


def step1_extract(seeds: Path, output: Path) -> None:
    """ROBOT BOT extraction against the 41-IRI seed list."""
    print(f"\n[1/5] BOT extraction: {len(seeds.read_text().strip().splitlines())} seed IRIs")
    _run_robot(
        "extract",
        "--method",
        "BOT",
        "--input",
        OEO_FULL,
        "--term-file",
        seeds,
        "--output",
        output,
    )
    print(f"    wrote {output}")


def step2_strip(input_path: Path, output: Path) -> None:
    """Strip BFO+RO leak terms (single pass, mirrors V1 build_v1_imports)
    plus V2-specific extras (BFO leak terms not in the V1 list)."""
    v2_extra = IMPORTS_DIR / "v2-extra-leak-terms.txt"
    upper_count = len(UPPER_STRIP.read_text().strip().splitlines())
    extra_count = len(v2_extra.read_text().strip().splitlines()) if v2_extra.exists() else 0
    print(f"\n[2/4] BFO+RO strip: {upper_count} V1 + {extra_count} V2 leak terms to remove")

    args = [
        "remove",
        "--input",
        input_path,
        "--term-file",
        UPPER_STRIP,
    ]
    if v2_extra.exists():
        args.extend(["--term-file", str(v2_extra)])
    args.extend(
        [
            "--trim",
            "true",
            "--preserve-structure",
            "false",
            "--output",
            str(output),
        ]
    )
    _run_robot(*args)
    print(f"    wrote {output}")


def step3_add_header(input_path: Path, output: Path) -> None:
    """Add owl:Ontology header so robot merge sees a named module."""
    print("\n[3/4] Add owl:Ontology header")
    g = Graph()
    g.parse(input_path)
    g.bind("oeo", OEO)
    g.bind("owl", OWL)
    g.bind("dcterms", DCTERMS)

    g.add((ONTOLOGY_IRI, RDF.type, OWL.Ontology))
    g.add((ONTOLOGY_IRI, DCTERMS.title, Literal("energy-intel — OEO topic subset", lang="en")))
    g.add(
        (
            ONTOLOGY_IRI,
            DCTERMS.description,
            Literal(
                "BFO+RO-stripped subset of the Open Energy Ontology, "
                "extracted from imports/oeo-full.owl via robot extract --method BOT "
                "against the 41-IRI seed list in imports/oeo-topic-seeds.txt. "
                "Used as the runtime topic catalog for the V2 editorial extension. "
                "OEO IRIs are admitted as values of ei:narrativeAboutTopic; "
                "skos:inScheme membership is asserted in modules/concept-schemes/oeo-topics.ttl.",
                lang="en",
            ),
        )
    )
    g.add((ONTOLOGY_IRI, DCTERMS.created, Literal("2026-05-04", datatype=XSD.date)))
    g.add((ONTOLOGY_IRI, DCTERMS.modified, Literal("2026-05-04", datatype=XSD.date)))
    g.add(
        (
            ONTOLOGY_IRI,
            DCTERMS.creator,
            Literal("energy-intel / ontology-architect", lang="en"),
        )
    )
    g.add((ONTOLOGY_IRI, OWL.versionInfo, Literal("v2 (2026-05-04)")))
    g.add(
        (
            ONTOLOGY_IRI,
            DCTERMS.license,
            URIRef("https://creativecommons.org/licenses/by/4.0/"),
        )
    )

    g.serialize(output, format="turtle")
    print(f"    wrote {output} ({len(g):,} triples)")


def step4_verify(output: Path, seeds: Path) -> None:
    """Verify the 41 seed IRIs survived and CQ-T3 granularity contract holds."""
    print("\n[4/4] Verification")
    g = Graph()
    g.parse(output)

    seed_iris = [URIRef(line.strip()) for line in seeds.read_text().splitlines() if line.strip()]

    missing = [iri for iri in seed_iris if (iri, RDF.type, OWL.Class) not in g]
    if missing:
        print(f"  FAIL: {len(missing)} seed IRIs missing owl:Class typing after strip:")
        for iri in missing[:5]:
            print(f"    - {iri}")
        sys.exit(1)
    print(f"  ok: all {len(seed_iris)} seed IRIs are owl:Class")

    bfo_count = sum(1 for s, _, o in g if "BFO_" in str(s) or "BFO_" in str(o))
    if bfo_count > 0:
        print(f"  WARN: {bfo_count} triples still reference BFO terms after strip")
    else:
        print("  ok: zero BFO references")

    individuals = [iri for iri in seed_iris if (iri, RDF.type, OWL.NamedIndividual) in g]
    if individuals:
        print(f"  WARN: {len(individuals)} seed IRIs typed as owl:NamedIndividual:")
        for iri in individuals[:3]:
            print(f"    - {iri}")
    else:
        print("  ok: zero seed IRIs are owl:NamedIndividual")

    # Granularity contract dry-run (CQ-T3): every seed must be Class or skos:Concept
    bare_individuals = [
        iri
        for iri in seed_iris
        if (iri, RDF.type, OWL.NamedIndividual) in g
        and (iri, RDF.type, OWL.Class) not in g
        and (iri, RDF.type, SKOS.Concept) not in g
    ]
    if bare_individuals:
        print(f"  FAIL: {len(bare_individuals)} bare NamedIndividual seeds violate CQ-T3:")
        for iri in bare_individuals[:5]:
            print(f"    - {iri}")
        sys.exit(1)
    print("  ok: granularity contract (CQ-T3) holds for all seeds")


def main() -> None:
    if not ROBOT.exists():
        print(f"FATAL: ROBOT wrapper not found at {ROBOT}")
        sys.exit(1)
    if not OEO_FULL.exists():
        print(f"FATAL: oeo-full.owl not found at {OEO_FULL}")
        sys.exit(1)
    if not SEEDS.exists():
        print(f"FATAL: seed list not found at {SEEDS}")
        sys.exit(1)

    raw = IMPORTS_DIR / "_oeo-topic-subset-raw.ttl"
    stripped = IMPORTS_DIR / "_oeo-topic-subset-stripped.ttl"

    step1_extract(SEEDS, raw)
    step2_strip(raw, stripped)
    step3_add_header(stripped, OUTPUT)
    step4_verify(OUTPUT, SEEDS)

    for tmp in (raw, stripped):
        tmp.unlink(missing_ok=True)

    print(f"\nDone. Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
