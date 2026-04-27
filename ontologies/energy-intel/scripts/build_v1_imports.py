"""Build energy-intel V1 imports: BFO-stripped OEO subsets + QUDT extract.

V1 acquires three artefacts:

1. ``imports/oeo-technology-subset-fixed.ttl`` — V0 BOT subset with all
   structural axioms referencing BFO and RO terms removed (the validator's
   ``construct_mismatch`` remediation, refined per scout SQ-3 evidence).
2. ``imports/oeo-carrier-subset-fixed.ttl`` — same treatment.
3. ``imports/qudt-units-subset.ttl`` — narrow extract of ``qudt:Unit`` and
   ``qudt:QuantityKind`` individuals used by the V1 sample claims.

The script is deterministic and re-runnable. It does NOT modify the V0
unfixed subsets; it produces fresh outputs alongside.

Run via:

```bash
uv run python ontologies/energy-intel/scripts/build_v1_imports.py
```

Pre-conditions:

* ``imports/oeo-technology-subset.ttl`` and ``imports/oeo-carrier-subset.ttl``
  exist (produced by V0 architect).
* ``.local/bin/robot`` is on disk (ROBOT 1.9.8).
* ``imports/upper-axiom-leak-terms.txt`` lists every BFO + RO IRI to strip.
* QUDT 2.1 vocab/unit and vocab/quantitykind reachable on the public web
  (https://qudt.org/2.1/vocab/{unit,quantitykind}). On HTTP failure, the
  script falls back to a cached copy under ``imports/qudt-source/`` if
  present.

Outputs are validated:

* ``robot merge`` of (V0 top-level + the two BFO-stripped OEO subsets +
  the QUDT subset) is run, and
* ``robot reason --reasoner hermit`` is run on the merge — exit 0 with no
  ``inconsistent ontology`` line is the gate. The reasoner output and
  trace are written under ``validation/v1-bfo-remediation/``.

The validator's V1 gate re-runs this script (or a CI-equivalent).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parent.parent
ROBOT = WORKSPACE_ROOT / ".local" / "bin" / "robot"

IMPORTS_DIR = PROJECT_ROOT / "imports"
QUDT_CACHE_DIR = IMPORTS_DIR / "qudt-source"
VALIDATION_DIR = PROJECT_ROOT / "validation" / "v1-bfo-remediation"

OEO_TECH_SRC = IMPORTS_DIR / "oeo-technology-subset.ttl"
OEO_CARRIER_SRC = IMPORTS_DIR / "oeo-carrier-subset.ttl"
OEO_TECH_FIXED = IMPORTS_DIR / "oeo-technology-subset-fixed.ttl"
OEO_CARRIER_FIXED = IMPORTS_DIR / "oeo-carrier-subset-fixed.ttl"
UPPER_LEAK_TERMS = IMPORTS_DIR / "upper-axiom-leak-terms.txt"
QUDT_OUT = IMPORTS_DIR / "qudt-units-subset.ttl"

V0_TOP_LEVEL = PROJECT_ROOT / "energy-intel.ttl"
V0_CATALOG = PROJECT_ROOT / "catalog-v001.xml"

QUDT_UNIT_URL = "https://qudt.org/2.1/vocab/unit"
QUDT_QK_URL = "https://qudt.org/2.1/vocab/quantitykind"
QUDT_UNIT_CACHE = QUDT_CACHE_DIR / "qudt-vocab-unit-2.1.ttl"
QUDT_QK_CACHE = QUDT_CACHE_DIR / "qudt-vocab-quantitykind-2.1.ttl"

# QUDT namespaces.
QUDT = Namespace("http://qudt.org/schema/qudt/")
UNIT = Namespace("http://qudt.org/vocab/unit/")
QK = Namespace("http://qudt.org/vocab/quantitykind/")
EI = Namespace("https://w3id.org/energy-intel/")

# V1 sample-unit seed list (corrected — V0 manifest had wrong IRIs).
# CQ-016 needs every unit a CMC could canonicalize to. CQ-017 needs the
# qudt:hasQuantityKind triple from each.
#
# Categories: power, watt-hour energy, joule energy, mass, volume,
# emission intensity, frequency / electrical, dimensionless / amount.
QUDT_UNIT_SEEDS: tuple[str, ...] = (
    "GigaW",
    "MegaW",
    "TeraW",
    "KiloW",
    "W",
    "TeraW-HR",
    "GigaW-HR",
    "MegaW-HR",
    "KiloW-HR",
    "PetaJ",
    "TeraJ",
    "GigaJ",
    "J",
    "BTU_IT",
    "TON_Metric",
    "KiloGM",
    "GM",
    "BBL",
    "BBL_UK_PET",
    "KiloGM-PER-J",
    "HZ",
    "V",
    "A",
    "PERCENT",
    "KiloMOL",
)

# Annotation properties to keep on each Unit (drop the rest to keep size tight).
KEEP_UNIT_PROPS: frozenset[URIRef] = frozenset(
    [
        RDF.type,
        RDFS.label,
        QUDT.symbol,
        QUDT.conversionMultiplier,
        QUDT.conversionOffset,
        QUDT.hasQuantityKind,
        QUDT.hasDimensionVector,
        QUDT.applicableSystem,
        QUDT.expression,
        QUDT.plainTextDescription,
        DCTERMS.description,
        SKOS.altLabel,
    ]
)

KEEP_QK_PROPS: frozenset[URIRef] = frozenset(
    [
        RDF.type,
        RDFS.label,
        QUDT.hasDimensionVector,
        QUDT.symbol,
        SKOS.broader,
        SKOS.exactMatch,
        SKOS.altLabel,
        DCTERMS.description,
        QUDT.plainTextDescription,
    ]
)


@dataclass(frozen=True)
class StepResult:
    label: str
    ok: bool
    detail: str


def info(msg: str) -> None:
    sys.stdout.write(f"[v1-imports] {msg}\n")
    sys.stdout.flush()


# --------------------------------------------------------------------- #
# OEO BFO/RO axiom strip                                                #
# --------------------------------------------------------------------- #


def run_robot_remove(src: Path, dst: Path, term_file: Path) -> StepResult:
    """Run ``robot remove --trim true --preserve-structure false``."""

    if not src.exists():
        return StepResult("robot-remove", False, f"missing source: {src}")
    if not term_file.exists():
        return StepResult("robot-remove", False, f"missing terms file: {term_file}")

    cmd = [
        str(ROBOT),
        "remove",
        "--input",
        str(src),
        "--term-file",
        str(term_file),
        "--trim",
        "true",
        "--preserve-structure",
        "false",
        "--output",
        str(dst),
    ]
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)  # noqa: S603
    if proc.returncode != 0:
        return StepResult("robot-remove", False, proc.stderr or proc.stdout)
    return StepResult("robot-remove", True, f"wrote {dst.name} ({dst.stat().st_size} bytes)")


# Stable ontology IRIs for the two BFO-stripped OEO subsets. Both V0 subsets
# share the same upstream OEO root IRI; we re-annotate them post-strip with
# project-namespaced IRIs so the V1 top-level can owl:imports each one
# independently and the catalog can resolve each to a distinct local file.
OEO_TECH_FIXED_ONT_IRI = "https://w3id.org/energy-intel/imports/oeo-technology-subset"
OEO_CARRIER_FIXED_ONT_IRI = "https://w3id.org/energy-intel/imports/oeo-carrier-subset"


def reannotate_ontology_iri(target: Path, new_iri: str, version_iri: str) -> StepResult:
    """Rewrite the ontology header IRI + add a version IRI in-place via rdflib.

    ROBOT's ``annotate --ontology-iri`` would also work, but doing it in
    rdflib lets us strip the old ontology declaration cleanly (avoiding a
    dual-Ontology-node trap that some serialisers leave behind).
    """

    if not target.exists():
        return StepResult("reannotate", False, f"missing: {target}")
    g = Graph()
    g.parse(target, format="turtle")

    # Find the existing ontology node (there should be exactly one).
    ontology_nodes = [s for s in g.subjects(RDF.type, OWL.Ontology) if isinstance(s, URIRef)]
    if not ontology_nodes:
        return StepResult("reannotate", False, f"no owl:Ontology node in {target}")
    if len(ontology_nodes) > 1:
        return StepResult(
            "reannotate",
            False,
            f"multiple owl:Ontology nodes in {target}: {ontology_nodes}",
        )
    old_iri = ontology_nodes[0]
    new_iri_ref = URIRef(new_iri)

    # Migrate every triple with old_iri as subject onto new_iri_ref.
    triples = list(g.triples((old_iri, None, None)))
    for s, p, o in triples:
        g.remove((s, p, o))
        g.add((new_iri_ref, p, o))

    # Add a version IRI + project provenance triples.
    g.add((new_iri_ref, OWL.versionIRI, URIRef(version_iri)))
    g.add(
        (
            new_iri_ref,
            DCTERMS.title,
            Literal(f"energy-intel — V1 import: {target.stem}", lang="en"),
        )
    )
    g.add(
        (
            new_iri_ref,
            DCTERMS.description,
            Literal(
                "BFO+RO-stripped OEO subset. Re-annotated with a project-"
                "namespaced ontology IRI so the energy-intel V1 top-level "
                "can owl:imports both technology and carrier subsets without "
                "IRI collision (both upstream files share the OEO root IRI).",
                lang="en",
            ),
        )
    )
    g.add((new_iri_ref, OWL.versionInfo, Literal("v1 (2026-04-27)")))

    g.serialize(destination=str(target), format="turtle")
    return StepResult(
        "reannotate",
        True,
        f"{target.name}: {old_iri} -> {new_iri}",
    )


def strip_bfo_ro_from_oeo() -> list[StepResult]:
    """Strip BFO + RO axioms from both V0 OEO subsets, then re-annotate IRIs."""

    results: list[StepResult] = []
    info("Stripping BFO + RO axioms from oeo-technology-subset.ttl ...")
    results.append(run_robot_remove(OEO_TECH_SRC, OEO_TECH_FIXED, UPPER_LEAK_TERMS))
    info("Stripping BFO + RO axioms from oeo-carrier-subset.ttl ...")
    results.append(run_robot_remove(OEO_CARRIER_SRC, OEO_CARRIER_FIXED, UPPER_LEAK_TERMS))

    if all(r.ok for r in results):
        info("Re-annotating OEO subset ontology IRIs ...")
        results.append(
            reannotate_ontology_iri(
                OEO_TECH_FIXED,
                OEO_TECH_FIXED_ONT_IRI,
                f"{OEO_TECH_FIXED_ONT_IRI}/v1/2026-04-27",
            )
        )
        results.append(
            reannotate_ontology_iri(
                OEO_CARRIER_FIXED,
                OEO_CARRIER_FIXED_ONT_IRI,
                f"{OEO_CARRIER_FIXED_ONT_IRI}/v1/2026-04-27",
            )
        )
    return results


# --------------------------------------------------------------------- #
# QUDT extract                                                          #
# --------------------------------------------------------------------- #


def fetch_qudt_source() -> StepResult:
    """Download QUDT 2.1 vocab/unit + vocab/quantitykind into the local cache."""

    QUDT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    pairs = [(QUDT_UNIT_URL, QUDT_UNIT_CACHE), (QUDT_QK_URL, QUDT_QK_CACHE)]
    for url, dst in pairs:
        if dst.exists() and dst.stat().st_size > 0:
            info(f"  cached: {dst.name}")
            continue
        info(f"  fetching {url} -> {dst.name}")
        request = urllib.request.Request(  # noqa: S310 — public registry
            url,
            headers={
                "Accept": "text/turtle",
                "User-Agent": "energy-intel/v1 ontology-scout",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as resp:  # noqa: S310
                dst.write_bytes(resp.read())
        except (OSError, urllib.error.URLError) as exc:
            return StepResult("fetch-qudt", False, f"{url} -> {exc}")
    return StepResult("fetch-qudt", True, "qudt vocabularies cached")


def build_qudt_subset() -> StepResult:
    """Slice qudt:Unit + qudt:QuantityKind into ``imports/qudt-units-subset.ttl``."""

    src_unit = Graph()
    src_qk = Graph()
    src_unit.parse(str(QUDT_UNIT_CACHE), format="turtle")
    src_qk.parse(str(QUDT_QK_CACHE), format="turtle")

    out = Graph()
    out.bind("qudt", QUDT)
    out.bind("unit", UNIT)
    out.bind("qkind", QK)
    out.bind("ei", EI)
    out.bind("dcterms", DCTERMS)
    out.bind("skos", SKOS)

    # Ontology header.
    ontology = URIRef("https://w3id.org/energy-intel/imports/qudt-units-subset")
    out.add((ontology, RDF.type, OWL.Ontology))
    out.add(
        (
            ontology,
            DCTERMS.title,
            Literal("energy-intel — QUDT units + quantity kinds (V1 subset)", lang="en"),
        )
    )
    out.add(
        (
            ontology,
            DCTERMS.description,
            Literal(
                "Narrow MIREOT-style slice of QUDT 2.1 vocab/unit and "
                "vocab/quantitykind covering every unit referenced by V1 "
                "sample claims, plus the qudt:QuantityKind individual that "
                "each unit declares via qudt:hasQuantityKind. Built by "
                "scripts/build_v1_imports.py.",
                lang="en",
            ),
        )
    )
    out.add((ontology, OWL.versionInfo, Literal("v1 (2026-04-27)")))
    out.add((ontology, DCTERMS.created, Literal("2026-04-27", datatype=XSD.date)))
    out.add((ontology, DCTERMS.source, URIRef(QUDT_UNIT_URL)))
    out.add((ontology, DCTERMS.source, URIRef(QUDT_QK_URL)))
    out.add(
        (
            ontology,
            DCTERMS.license,
            URIRef("https://creativecommons.org/licenses/by/4.0/"),
        )
    )

    # Type-declare qudt:Unit and qudt:QuantityKind so HermiT punning resolves.
    out.add((QUDT.Unit, RDF.type, OWL.Class))
    out.add((QUDT.QuantityKind, RDF.type, OWL.Class))
    # qudt:hasQuantityKind is a property linking a Unit individual to a
    # QuantityKind individual; we declare it as ObjectProperty in the subset.
    out.add((QUDT.hasQuantityKind, RDF.type, OWL.ObjectProperty))
    out.add(
        (
            QUDT.hasQuantityKind,
            RDFS.label,
            Literal("has quantity kind", lang="en"),
        )
    )

    qks_to_pull: set[URIRef] = set()
    units_pulled: list[str] = []
    units_missing: list[str] = []

    for seed in QUDT_UNIT_SEEDS:
        unit_iri = UNIT[seed]
        if (unit_iri, RDF.type, QUDT.Unit) not in src_unit:
            units_missing.append(seed)
            continue
        units_pulled.append(seed)
        # Copy filtered triples for the unit.
        for predicate, obj in src_unit.predicate_objects(unit_iri):
            if predicate in KEEP_UNIT_PROPS:
                out.add((unit_iri, predicate, obj))
                if predicate == QUDT.hasQuantityKind and isinstance(obj, URIRef):
                    qks_to_pull.add(obj)
        # Always assert rdf:type qudt:Unit (in case it was filtered).
        out.add((unit_iri, RDF.type, QUDT.Unit))

    qks_pulled: list[str] = []
    qks_missing: list[str] = []
    for qk_iri in sorted(qks_to_pull, key=str):
        if (qk_iri, RDF.type, QUDT.QuantityKind) not in src_qk:
            qks_missing.append(str(qk_iri))
            continue
        qks_pulled.append(str(qk_iri).split("/")[-1])
        for predicate, obj in src_qk.predicate_objects(qk_iri):
            if predicate in KEEP_QK_PROPS:
                out.add((qk_iri, predicate, obj))
        out.add((qk_iri, RDF.type, QUDT.QuantityKind))

    out.serialize(destination=str(QUDT_OUT), format="turtle")

    detail_lines = [
        f"wrote {QUDT_OUT.name} ({QUDT_OUT.stat().st_size} bytes, {len(out)} triples)",
        f"units pulled ({len(units_pulled)}): {', '.join(units_pulled)}",
        f"quantitykinds pulled ({len(qks_pulled)}): {', '.join(qks_pulled)}",
    ]
    if units_missing:
        detail_lines.append(f"units MISSING: {', '.join(units_missing)}")
    if qks_missing:
        detail_lines.append(f"qks MISSING: {', '.join(qks_missing)}")
    ok = not units_missing and not qks_missing
    return StepResult("build-qudt-subset", ok, "\n  ".join(detail_lines))


# Validation block: merge + reason --------------------------------- #


def validate_merge_and_reason() -> list[StepResult]:
    """Merge V0 + V1 imports and reason with HermiT.

    Hermit must exit 0 with no 'inconsistent ontology' line in stderr.
    """

    results: list[StepResult] = []
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    merged = VALIDATION_DIR / "v1-merged-closure.ttl"
    reasoned = VALIDATION_DIR / "v1-reasoned-closure.ttl"
    merge_log = VALIDATION_DIR / "v1-merge.log"
    reason_log = VALIDATION_DIR / "v1-hermit-reason.log"

    # Step 1: merge V0 top-level (bringing all V0 imports via catalog) + V1 OEO + QUDT.
    info(f"Merging V0 top-level + V1 OEO subsets + QUDT subset -> {merged.name}")
    cmd = [
        str(ROBOT),
        "merge",
        "--catalog",
        str(V0_CATALOG),
        "--input",
        str(V0_TOP_LEVEL),
        "--input",
        str(OEO_TECH_FIXED),
        "--input",
        str(OEO_CARRIER_FIXED),
        "--input",
        str(QUDT_OUT),
        "--output",
        str(merged),
    ]
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)  # noqa: S603
    merge_log.write_text(
        f"$ {' '.join(cmd)}\nexit={proc.returncode}\n--- stdout ---\n{proc.stdout}"
        f"\n--- stderr ---\n{proc.stderr}"
    )
    if proc.returncode != 0:
        results.append(StepResult("merge", False, "see v1-merge.log"))
        return results
    results.append(
        StepResult(
            "merge",
            True,
            f"wrote {merged.name} ({merged.stat().st_size} bytes)",
        )
    )

    # Step 2: reason with HermiT.
    info(f"Running HermiT on {merged.name} -> {reasoned.name}")
    cmd = [
        str(ROBOT),
        "reason",
        "--reasoner",
        "hermit",
        "--input",
        str(merged),
        "--output",
        str(reasoned),
    ]
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)  # noqa: S603
    combined_log = (
        f"$ {' '.join(cmd)}\nexit={proc.returncode}\n--- stdout ---\n{proc.stdout}"
        f"\n--- stderr ---\n{proc.stderr}"
    )
    reason_log.write_text(combined_log)

    inconsistent_marker = "inconsistent ontology"
    inconsistent = inconsistent_marker in (proc.stderr.lower() + proc.stdout.lower())
    if proc.returncode != 0 or inconsistent or not reasoned.exists():
        results.append(
            StepResult(
                "reason-hermit",
                False,
                (
                    "HermiT reported inconsistency or did not produce output"
                    " (see v1-hermit-reason.log)"
                ),
            )
        )
        return results
    results.append(
        StepResult(
            "reason-hermit",
            True,
            f"HermiT clean; wrote {reasoned.name} ({reasoned.stat().st_size} bytes)",
        )
    )
    return results


# --------------------------------------------------------------------- #
# Main                                                                  #
# --------------------------------------------------------------------- #


def main() -> int:
    if shutil.which(str(ROBOT)) is None and not ROBOT.is_file():
        info(f"FATAL: cannot find ROBOT at {ROBOT}")
        return 2

    info("=" * 72)
    info("PHASE 1 — strip BFO + RO axioms from OEO subsets")
    info("=" * 72)
    results = strip_bfo_ro_from_oeo()
    for r in results:
        info(f"  {r.label}: {'OK' if r.ok else 'FAIL'} — {r.detail}")
    if not all(r.ok for r in results):
        return 1

    info("=" * 72)
    info("PHASE 2 — fetch + slice QUDT 2.1")
    info("=" * 72)
    fetch = fetch_qudt_source()
    info(f"  fetch-qudt: {'OK' if fetch.ok else 'FAIL'} — {fetch.detail}")
    if not fetch.ok:
        return 1
    qudt_result = build_qudt_subset()
    info(f"  build-qudt-subset: {'OK' if qudt_result.ok else 'FAIL'}")
    info(f"  {qudt_result.detail}")
    if not qudt_result.ok:
        return 1

    info("=" * 72)
    info("PHASE 3 — merge + HermiT reasoner gate")
    info("=" * 72)
    val_results = validate_merge_and_reason()
    for r in val_results:
        info(f"  {r.label}: {'OK' if r.ok else 'FAIL'} — {r.detail}")
    if not all(r.ok for r in val_results):
        return 1

    info("=" * 72)
    info("V1 imports build COMPLETE — all gates green.")
    info("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
