"""Stamp owl:versionIRI on V2 module ontology files (programmatic, rdflib).

V2 architect-build emits modules with `owl:versionInfo "v2 (2026-05-04)"` but
without `owl:versionIRI`. The top-level `energy-intel.ttl` already carries the
versionIRI <https://w3id.org/energy-intel/v2/2026-05-04>; this script aligns
each module file by setting versionIRI on every ontology header in:

- modules/editorial.ttl
- modules/concept-schemes/argument-pattern.ttl
- modules/concept-schemes/narrative-role.ttl
- modules/concept-schemes/oeo-topics.ttl
- shapes/editorial.ttl

Each module's versionIRI is `<ontology-iri>/v2/{ISO-date}`.

This is idempotent: running again with the same date is a no-op (rdflib graph
adds the same triple). Running with a different date replaces the prior
versionIRI for that ontology.

Run via: uv run python ontologies/energy-intel/scripts/stamp_version_iri.py
"""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF, XSD

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# V2 release: 2026-05-04 — matches top-level energy-intel.ttl + release-audit-v2.yaml.
# Note: validator handoff specified this date; today's UTC date is 2026-05-05 but
# the V2 versionIRI was set on 2026-05-04 by architect, and we preserve it here
# for consistency with the merged closure already validated.
V2_DATE = "2026-05-04"

# Each entry: (file path, ontology IRI, versionIRI suffix `/v2/{date}`)
TARGETS: list[tuple[str, str]] = [
    # (relative file path, ontology IRI)
    ("modules/editorial.ttl", "https://w3id.org/energy-intel/modules/editorial"),
    (
        "modules/concept-schemes/argument-pattern.ttl",
        "https://w3id.org/energy-intel/modules/concept-schemes/argument-pattern",
    ),
    (
        "modules/concept-schemes/narrative-role.ttl",
        "https://w3id.org/energy-intel/modules/concept-schemes/narrative-role",
    ),
    (
        "modules/concept-schemes/oeo-topics.ttl",
        "https://w3id.org/energy-intel/modules/concept-schemes/oeo-topics",
    ),
    ("shapes/editorial.ttl", "https://w3id.org/energy-intel/shapes/editorial"),
    # imports/oeo-topic-subset.ttl is a generated artifact; its header is
    # written by extract_oeo_topic_subset.py. We DO stamp it here for
    # consistency, but the next extract_oeo_topic_subset.py rebuild will
    # need to either preserve the stamp or call this script as a final step.
    (
        "imports/oeo-topic-subset.ttl",
        "https://w3id.org/energy-intel/imports/oeo-topic-subset",
    ),
]


def version_iri_for(ontology_iri: str, date: str) -> URIRef:
    """Compute the versionIRI for a module ontology IRI.

    Pattern: insert `/v2/{date}` between the `https://w3id.org/energy-intel`
    prefix and the rest of the ontology IRI path. For the imports/* and
    modules/* IRIs we want a flat `/v2/{date}` suffix.

    Examples:
      modules/editorial -> modules/editorial/v2/2026-05-04
      shapes/editorial -> shapes/editorial/v2/2026-05-04
    """
    return URIRef(f"{ontology_iri}/v2/{date}")


def stamp_file(rel_path: str, ontology_iri: str, date: str) -> bool:
    """Add or update owl:versionIRI on the given module's ontology header.

    Returns True if the file was modified, False if already up-to-date.
    """
    path = PROJECT_ROOT / rel_path
    if not path.exists():
        print(f"  SKIP (missing): {rel_path}")
        return False

    g = Graph()
    g.parse(path, format="turtle")

    onto_uri = URIRef(ontology_iri)
    target_v_iri = version_iri_for(ontology_iri, date)

    # Confirm the file declares this ontology.
    declared = (onto_uri, RDF.type, OWL.Ontology) in g
    if not declared:
        print(f"  SKIP (no owl:Ontology declaration for {ontology_iri}): {rel_path}")
        return False

    # Drop any existing versionIRI on this ontology.
    existing_v_iris = list(g.objects(onto_uri, OWL.versionIRI))
    for v_iri in existing_v_iris:
        if v_iri == target_v_iri:
            print(f"  no-op  {rel_path}  (versionIRI already <{target_v_iri}>)")
            return False
        g.remove((onto_uri, OWL.versionIRI, v_iri))

    # Stamp.
    g.add((onto_uri, OWL.versionIRI, target_v_iri))

    # Also (re-)stamp dcterms:modified if the file uses it.
    dcterms_modified = URIRef("http://purl.org/dc/terms/modified")
    existing_modified = list(g.objects(onto_uri, dcterms_modified))
    for old in existing_modified:
        g.remove((onto_uri, dcterms_modified, old))
    g.add((onto_uri, dcterms_modified, Literal(date, datatype=XSD.date)))

    g.serialize(destination=path, format="turtle")
    print(f"  stamped {rel_path}  versionIRI=<{target_v_iri}>  modified={date}")
    return True


def main() -> int:
    print(f"=== stamp_version_iri.py — V2 release ({V2_DATE}) ===")
    modified = 0
    for rel, iri in TARGETS:
        if stamp_file(rel, iri, V2_DATE):
            modified += 1
    print(f"\nDone. {modified} file(s) updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
