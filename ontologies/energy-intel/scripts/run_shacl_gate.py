"""Run pyshacl against every CQ fixture with the project TBox + shapes.

For each fixture ``tests/fixtures/cq-NNN.ttl`` we:

1. Build a data graph from the top-level TBox + all module TBoxes + hand-seeded
   concept schemes + the fixture. ``pyshacl`` is told to use ``rdfs`` inference
   so ``rdfs:subClassOf`` chains materialise (Chart / Post are subClassOf
   EvidenceSource; SHACL ``sh:class`` checks need that to fire).
2. Load ``shapes/energy-intel-shapes.ttl`` as the shapes graph.
3. Run ``pyshacl.validate``; record ``conforms`` + violation count.

Outputs:
- ``validation/shacl-results-cq-NNN.ttl`` — machine-readable result graph
  per fixture (one file per fixture; gitignored).
- ``validation/shacl-summary.json`` — per-fixture pass/fail roll-up.

Exit 0 if every fixture conforms; exit 1 otherwise.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pyshacl import validate
from rdflib import Graph

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DIR = PROJECT_ROOT / "validation"
VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

TBOX_FILES = [
    PROJECT_ROOT / "energy-intel.ttl",
    PROJECT_ROOT / "modules" / "agent.ttl",
    PROJECT_ROOT / "modules" / "media.ttl",
    PROJECT_ROOT / "modules" / "measurement.ttl",
    PROJECT_ROOT / "modules" / "data.ttl",
    PROJECT_ROOT / "modules" / "concept-schemes" / "temporal-resolution.ttl",
    PROJECT_ROOT / "modules" / "concept-schemes" / "aggregation-type.ttl",
    PROJECT_ROOT / "modules" / "concept-schemes" / "technology-seeds.ttl",
]

SHAPES_FILE = PROJECT_ROOT / "shapes" / "energy-intel-shapes.ttl"
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures"


def build_data_graph(fixture: Path) -> Graph:
    """Merge TBox + fixture into a single graph for pyshacl."""
    g = Graph()
    for path in TBOX_FILES:
        g.parse(path, format="turtle")
    g.parse(fixture, format="turtle")
    return g


def run_gate() -> int:
    shapes = Graph()
    shapes.parse(SHAPES_FILE, format="turtle")

    results: list[dict[str, object]] = []
    any_fail = False

    for fixture in sorted(FIXTURE_DIR.glob("cq-*.ttl")):
        cq_id = fixture.stem  # e.g., "cq-001"
        data = build_data_graph(fixture)
        conforms, results_graph, _report_text = validate(
            data_graph=data,
            shacl_graph=shapes,
            inference="rdfs",
            abort_on_first=False,
            meta_shacl=False,
            debug=False,
        )

        # Serialize the per-fixture results graph.
        out_path = VALIDATION_DIR / f"shacl-results-{cq_id}.ttl"
        results_graph.serialize(destination=out_path, format="turtle")

        # Count violations from the results graph.
        violations = list(
            results_graph.query(
                """
                PREFIX sh: <http://www.w3.org/ns/shacl#>
                SELECT (COUNT(?r) AS ?n)
                WHERE { ?r a sh:ValidationResult ;
                           sh:resultSeverity sh:Violation . }
                """
            )
        )
        n_violations = int(violations[0][0]) if violations else 0

        status = "pass" if conforms else "fail"
        if not conforms:
            any_fail = True

        results.append(
            {
                "cq": cq_id,
                "fixture_path": str(fixture.relative_to(PROJECT_ROOT)),
                "conforms": conforms,
                "violations": n_violations,
                "status": status,
                "results_graph": str(out_path.relative_to(PROJECT_ROOT)),
            }
        )

        sym = "PASS" if conforms else f"FAIL ({n_violations} viol)"
        print(f"  {cq_id}  {sym}")

    summary_path = VALIDATION_DIR / "shacl-summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "shapes_file": str(SHAPES_FILE.relative_to(PROJECT_ROOT)),
                "fixtures_validated": len(results),
                "failures": sum(1 for r in results if r["status"] == "fail"),
                "results": results,
            },
            indent=2,
        )
    )
    print(f"\nSummary written to {summary_path}")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(run_gate())
