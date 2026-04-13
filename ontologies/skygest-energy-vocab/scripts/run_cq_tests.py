"""Run CQ test suite against the vocabulary."""

from pathlib import Path

import yaml
from rdflib import Graph

VOCAB_DIR = Path(__file__).parent.parent
VOCAB_FILE = VOCAB_DIR / "skygest-energy-vocab.ttl"
SHAPES_FILE = VOCAB_DIR / "shapes" / "skygest-energy-vocab-shapes.ttl"
TEST_DIR = VOCAB_DIR / "tests"
MANIFEST_FILE = TEST_DIR / "cq-test-manifest.yaml"


def main() -> None:
    """Execute all CQ tests and report results."""
    g = Graph()
    g.parse(VOCAB_FILE, format="turtle")
    # SHACL shapes live in a sibling file; merge them so SHACL-inspecting
    # CQs (e.g. CQ-064, CQ-073) can see the shape graph.
    if SHAPES_FILE.exists():
        g.parse(SHAPES_FILE, format="turtle")

    manifest = yaml.safe_load(MANIFEST_FILE.read_text())
    tests = manifest["tests"]

    passed = 0
    failed = 0
    skipped = 0
    failures: list[str] = []

    for test in tests:
        cq_id = test["cq_id"]
        test_file = TEST_DIR / test["file"]
        expected = test["expected_result"]
        query_type = test["type"]

        if not test_file.exists():
            print(f"  SKIP  {cq_id}: {test_file.name} not found")
            skipped += 1
            continue

        query_text = test_file.read_text()

        try:
            if query_type == "ASK":
                result = bool(g.query(query_text))
                if expected == "true" and result:
                    print(f"  PASS  {cq_id}: ASK returned true")
                    passed += 1
                elif expected == "false" and not result:
                    print(f"  PASS  {cq_id}: ASK returned false")
                    passed += 1
                else:
                    print(f"  FAIL  {cq_id}: ASK returned {result}, expected {expected}")
                    failed += 1
                    failures.append(cq_id)
            else:
                results = list(g.query(query_text))
                count = len(results)

                if expected == "empty" and count == 0:
                    print(f"  PASS  {cq_id}: empty (0 rows) — constraint satisfied")
                    passed += 1
                elif expected == "empty" and count > 0:
                    print(f"  FAIL  {cq_id}: expected empty but got {count} rows")
                    failed += 1
                    failures.append(cq_id)
                elif expected == "non_empty" and count > 0:
                    print(f"  PASS  {cq_id}: non-empty ({count} rows)")
                    passed += 1
                elif expected == "non_empty" and count == 0:
                    print(f"  FAIL  {cq_id}: expected non-empty but got 0 rows")
                    failed += 1
                    failures.append(cq_id)
                else:
                    print(f"  SKIP  {cq_id}: unknown expected_result '{expected}'")
                    skipped += 1
        except Exception as e:
            print(f"  ERROR {cq_id}: {e}")
            failed += 1
            failures.append(cq_id)

    print(f"\n{'=' * 60}")
    print(f"CQ Test Results: {passed} passed, {failed} failed, {skipped} skipped")
    print(f"Total: {passed + failed + skipped} tests")
    if failures:
        print(f"Failures: {', '.join(failures)}")


if __name__ == "__main__":
    main()
