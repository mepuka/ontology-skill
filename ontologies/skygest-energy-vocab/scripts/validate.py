"""Validate the skygest-energy-vocab Turtle file."""

from pathlib import Path

from rdflib import Graph

VOCAB_DIR = Path(__file__).parent.parent
VOCAB_FILE = VOCAB_DIR / "skygest-energy-vocab.ttl"
SHAPES_FILE = VOCAB_DIR / "shapes" / "skygest-energy-vocab-shapes.ttl"

SKOS_IN_SCHEME = "http://www.w3.org/2004/02/skos/core#inScheme"
SKOS_ALT_LABEL = "http://www.w3.org/2004/02/skos/core#altLabel"


def main() -> None:
    """Parse and validate the vocabulary."""
    g = Graph()
    g.parse(VOCAB_FILE, format="turtle")
    print(f"Parsed OK: {len(g)} triples")

    # Count concepts per scheme
    from collections import Counter

    counts: Counter[str] = Counter()
    for _s, _p, o in g.triples((None, None, None)):
        if str(_p) == SKOS_IN_SCHEME:
            counts[str(o).split("/")[-1]] += 1
    for scheme, count in sorted(counts.items()):
        print(f"  {scheme}: {count} concepts")

    # Count altLabels
    alt_count = sum(1 for _ in g.triples((None, None, None)) if str(_[1]) == SKOS_ALT_LABEL)
    print(f"  Total altLabels: {alt_count}")

    # Parse shapes
    sg = Graph()
    sg.parse(SHAPES_FILE, format="turtle")
    print(f"\nShapes parsed OK: {len(sg)} triples")

    # Run pyshacl
    try:
        from pyshacl import validate

        conforms, _results_graph, results_text = validate(g, shacl_graph=sg, inference="none")
        print(f"\nSHACL validation: {'CONFORMS' if conforms else 'VIOLATIONS FOUND'}")
        if not conforms:
            print(results_text)
    except ImportError:
        print("\npyshacl not installed — skipping SHACL validation")


if __name__ == "__main__":
    main()
