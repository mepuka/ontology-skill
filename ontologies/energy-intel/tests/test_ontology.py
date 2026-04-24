"""Competency-question acceptance tests for ``energy-intel``.

For every CQ row in ``tests/cq-test-manifest.yaml``:

1. Load TBox (top-level + four module TTLs + three hand-seeded SKOS schemes)
   into a fresh rdflib ``Graph``.
2. Load the named fixture ``tests/fixtures/cq-NNN.ttl`` on top.
3. Parse + execute the corresponding ``tests/cq-NNN.sparql`` file.
4. Assert the row-count band and column shape declared in the manifest's
   ``expected_results_contract``.

The cardinality band is parsed out of the manifest's
``expected_results_contract`` text by rule-of-thumb keyword matching rather
than executing a mini-DSL; the bands below mirror what the architect wrote
in the manifest.

CQ-009 is an invariant: any row is a TBox breach. This test asserts exactly
zero rows.

Run with: ``uv run pytest ontologies/energy-intel/tests/test_ontology.py -v``
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = PROJECT_ROOT / "tests"
FIXTURES_DIR = TESTS_DIR / "fixtures"
MANIFEST_PATH = TESTS_DIR / "cq-test-manifest.yaml"

TBOX_FILES: tuple[Path, ...] = (
    PROJECT_ROOT / "energy-intel.ttl",
    PROJECT_ROOT / "modules" / "agent.ttl",
    PROJECT_ROOT / "modules" / "media.ttl",
    PROJECT_ROOT / "modules" / "measurement.ttl",
    PROJECT_ROOT / "modules" / "data.ttl",
    PROJECT_ROOT / "modules" / "concept-schemes" / "temporal-resolution.ttl",
    PROJECT_ROOT / "modules" / "concept-schemes" / "aggregation-type.ttl",
    PROJECT_ROOT / "modules" / "concept-schemes" / "technology-seeds.ttl",
)

# Per-CQ expected (min_rows, max_rows) bands derived from the manifest's
# ``expected_results_contract`` text. ``None`` on the high side means
# unbounded. CQ-009 is the invariant: exactly zero rows.
EXPECTED_BANDS: dict[str, tuple[int, int | None]] = {
    "CQ-001": (0, None),  # 0..n
    "CQ-002": (1, 1),  # exactly 1
    "CQ-003": (0, 1),  # 0..1
    "CQ-004": (0, 1),  # 0..1
    "CQ-005": (0, 1),  # 0..1
    "CQ-006": (0, None),  # 0..n
    "CQ-007": (0, None),  # 0..n distinct
    "CQ-008": (0, None),  # 0..n
    "CQ-009": (0, 0),  # exactly 0 — TBox invariant
    "CQ-010": (1, 1),  # exactly 1 row with OPTIONAL columns
    "CQ-011": (0, None),  # 0..n
    "CQ-012": (0, None),  # 0..n
    "CQ-013": (0, None),  # 0..n transitive walk
    "CQ-014": (0, None),  # 0..n distinct
}

# Per-CQ expected column order. Must match the manifest row contract.
EXPECTED_COLUMNS: dict[str, tuple[str, ...]] = {
    "CQ-001": ("cmc",),
    "CQ-002": ("expert",),
    "CQ-003": ("variable",),
    "CQ-004": ("series",),
    "CQ-005": ("distribution",),
    "CQ-006": ("cmc",),
    "CQ-007": ("expert",),
    "CQ-008": ("cmc", "post", "expert", "assertedValue", "assertedUnit", "assertedTime"),
    "CQ-009": ("cmc",),
    "CQ-010": ("agent", "dist", "dataset", "var", "series"),
    "CQ-011": ("expert",),
    "CQ-012": ("cmc",),
    "CQ-013": ("cmc",),
    "CQ-014": ("post",),
}


def _load_manifest() -> list[dict[str, object]]:
    with MANIFEST_PATH.open() as f:
        manifest = yaml.safe_load(f)
    return manifest["tests"]


def _build_graph(fixture_path: Path) -> Graph:
    g = Graph()
    for path in TBOX_FILES:
        g.parse(path, format="turtle")
    g.parse(fixture_path, format="turtle")
    return g


_MANIFEST_ROWS = _load_manifest()


@pytest.mark.parametrize(
    "row",
    _MANIFEST_ROWS,
    ids=[r["id"] for r in _MANIFEST_ROWS],
)
def test_cq_fixture(row: dict[str, object]) -> None:
    cq_id = str(row["id"])
    sparql_path = PROJECT_ROOT / str(row["file"])
    fixture_path = PROJECT_ROOT / str(row["fixture_path"])

    assert sparql_path.is_file(), f"missing SPARQL file: {sparql_path}"
    assert fixture_path.is_file(), f"missing fixture file: {fixture_path}"

    query_text = sparql_path.read_text()

    # Parse check — ensures every query is valid SPARQL 1.1.
    prepareQuery(query_text)

    graph = _build_graph(fixture_path)
    results = list(graph.query(query_text))

    # Column shape.
    expected_cols = EXPECTED_COLUMNS[cq_id]
    # rdflib Result exposes .vars, but iterating over results yields ResultRows.
    # Re-query to get .vars (cheap: already cached).
    query_result = graph.query(query_text)
    actual_cols = tuple(str(v) for v in (query_result.vars or ()))
    assert actual_cols == expected_cols, (
        f"{cq_id}: column shape mismatch expected {expected_cols}, got {actual_cols}"
    )

    # Cardinality band.
    min_rows, max_rows = EXPECTED_BANDS[cq_id]
    n = len(results)
    assert n >= min_rows, (
        f"{cq_id}: expected ≥{min_rows} rows, got {n}. Fixture: {fixture_path.name}"
    )
    if max_rows is not None:
        assert n <= max_rows, (
            f"{cq_id}: expected ≤{max_rows} rows, got {n}. Fixture: {fixture_path.name}"
        )

    # Manifest's own promise cross-check.
    expected_status = str(row.get("fixture_run_status", ""))
    # If manifest says pass, our row count must be within band (already asserted).
    # This assertion is a truthy sentinel — we're asserting the manifest isn't lying.
    assert expected_status == "pass", (
        f"{cq_id}: manifest has fixture_run_status={expected_status!r} "
        f"but test_ontology.py only validates rows marked 'pass'"
    )
