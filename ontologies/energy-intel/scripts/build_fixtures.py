"""Build one minimal ABox fixture per CQ and verify its SPARQL return shape.

Each fixture is written to ``tests/fixtures/cq-NNN.ttl``. Immediately
after authoring we execute ``tests/cq-NNN.sparql`` against the fixture
and check the row shape matches the ``expected_results_contract`` in
``tests/cq-test-manifest.yaml``.

Records pass/fail into a dict the caller uses to update the manifest.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, OWL, RDF, RDFS, SKOS, XSD

EI = Namespace("https://w3id.org/energy-intel/")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures"
SPARQL_DIR = PROJECT_ROOT / "tests"
CONCEPT_SEEDS = PROJECT_ROOT / "modules" / "concept-schemes" / "technology-seeds.ttl"

# -------------------------------------------------------------------
# Canonical ABox IRIs (match the ones in tests/cq-*.sparql)
# -------------------------------------------------------------------

POST_MAIN = URIRef("https://id.skygest.io/post/post_01J_example")
CMC_MAIN = URIRef("https://id.skygest.io/cmc/cmc_01J_example")
EXPERT_MAIN = URIRef("https://id.skygest.io/expert/did-plc-a5kyzplew76jaj4dhnqsosjv")
VAR_MAIN = URIRef("https://id.skygest.io/variable/var_01J_solar_installed_capacity")
SER_MAIN = URIRef("https://id.skygest.io/series/ser_01J_solar_us_monthly")
DIST_MAIN = URIRef("https://id.skygest.io/distribution/dist_01J_eia_pv_monthly")
DATASET_MAIN = URIRef("https://id.skygest.io/dataset/ds_01J_eia_pv")
AGENT_MAIN = URIRef("https://id.skygest.io/agent/ag_01J_eia")
CTW_MAIN = URIRef("https://id.skygest.io/temporal-window/tw_01J_2025")
SEG_MAIN = URIRef("https://id.skygest.io/podcast-segment/seg_01J_example")


def _base_graph() -> Graph:
    g = Graph()
    g.bind("ei", EI)
    g.bind("dcat", DCAT)
    g.bind("skos", SKOS)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    g.bind("rdfs", RDFS)
    g.bind("dcterms", DCTERMS)
    return g


def add_header(g: Graph, cq_id: str, description: str) -> None:
    ont = URIRef(f"https://w3id.org/energy-intel/tests/fixtures/{cq_id}")
    g.add((ont, RDF.type, OWL.Ontology))
    g.add((ont, DCTERMS.title, Literal(f"{cq_id} fixture", lang="en")))
    g.add((ont, DCTERMS.description, Literal(description, lang="en")))
    g.add((ont, DCTERMS.created, Literal("2026-04-22", datatype=XSD.date)))


def _post(g: Graph, post: URIRef, expert: URIRef) -> None:
    """Add a Post + author + type triples."""
    g.add((post, RDF.type, EI.Post))
    g.add((post, RDF.type, OWL.NamedIndividual))
    g.add((post, EI.authoredBy, expert))
    g.add((expert, RDF.type, EI.Expert))
    g.add((expert, RDF.type, OWL.NamedIndividual))


def _cmc(g: Graph, cmc: URIRef) -> None:
    g.add((cmc, RDF.type, EI.CanonicalMeasurementClaim))
    g.add((cmc, RDF.type, OWL.NamedIndividual))


def _variable(g: Graph, v: URIRef) -> None:
    g.add((v, RDF.type, EI.Variable))
    g.add((v, RDF.type, OWL.NamedIndividual))


def _series(g: Graph, s: URIRef) -> None:
    g.add((s, RDF.type, EI.Series))
    g.add((s, RDF.type, OWL.NamedIndividual))


# -------------------------------------------------------------------
# Fixture builders, one per CQ
# -------------------------------------------------------------------


def cq001() -> None:
    g = _base_graph()
    add_header(g, "cq-001", "Post evidences a CMC.")
    _post(g, POST_MAIN, EXPERT_MAIN)
    _cmc(g, CMC_MAIN)
    g.add((POST_MAIN, EI.evidences, CMC_MAIN))
    g.serialize(FIXTURE_DIR / "cq-001.ttl", format="turtle")


def cq002() -> None:
    g = _base_graph()
    add_header(g, "cq-002", "Post authored by an Expert (did:plc).")
    _post(g, POST_MAIN, EXPERT_MAIN)
    g.serialize(FIXTURE_DIR / "cq-002.ttl", format="turtle")


def cq003() -> None:
    g = _base_graph()
    add_header(g, "cq-003", "CMC references a Variable.")
    _cmc(g, CMC_MAIN)
    _variable(g, VAR_MAIN)
    g.add((CMC_MAIN, EI.referencesVariable, VAR_MAIN))
    # CMC invariant: every CMC must have an evidencing source.
    _post(g, POST_MAIN, EXPERT_MAIN)
    g.add((POST_MAIN, EI.evidences, CMC_MAIN))
    g.serialize(FIXTURE_DIR / "cq-003.ttl", format="turtle")


def cq004() -> None:
    g = _base_graph()
    add_header(g, "cq-004", "CMC references a Series.")
    _cmc(g, CMC_MAIN)
    _series(g, SER_MAIN)
    g.add((CMC_MAIN, EI.referencesSeries, SER_MAIN))
    _post(g, POST_MAIN, EXPERT_MAIN)
    g.add((POST_MAIN, EI.evidences, CMC_MAIN))
    g.serialize(FIXTURE_DIR / "cq-004.ttl", format="turtle")


def cq005() -> None:
    g = _base_graph()
    add_header(g, "cq-005", "CMC references a DCAT Distribution.")
    _cmc(g, CMC_MAIN)
    g.add((DIST_MAIN, RDF.type, DCAT.Distribution))
    g.add((DIST_MAIN, RDF.type, OWL.NamedIndividual))
    g.add((CMC_MAIN, EI.referencesDistribution, DIST_MAIN))
    _post(g, POST_MAIN, EXPERT_MAIN)
    g.add((POST_MAIN, EI.evidences, CMC_MAIN))
    g.serialize(FIXTURE_DIR / "cq-005.ttl", format="turtle")


def cq006() -> None:
    g = _base_graph()
    add_header(g, "cq-006", "Two CMCs reference the same Variable (inverse walk).")
    _variable(g, VAR_MAIN)
    for _i, suffix in enumerate(("a", "b")):
        cmc = URIRef(f"https://id.skygest.io/cmc/cmc_01J_claim_{suffix}")
        post = URIRef(f"https://id.skygest.io/post/post_01J_{suffix}")
        expert = URIRef(f"https://id.skygest.io/expert/did-plc-{suffix}author")
        _cmc(g, cmc)
        g.add((cmc, EI.referencesVariable, VAR_MAIN))
        _post(g, post, expert)
        g.add((post, EI.evidences, cmc))
    g.serialize(FIXTURE_DIR / "cq-006.ttl", format="turtle")


def cq007() -> None:
    g = _base_graph()
    add_header(
        g,
        "cq-007",
        "Two distinct Experts have claimed about the same Variable.",
    )
    _variable(g, VAR_MAIN)
    for suffix in ("a", "b"):
        cmc = URIRef(f"https://id.skygest.io/cmc/cmc_01J_claim_{suffix}")
        post = URIRef(f"https://id.skygest.io/post/post_01J_{suffix}")
        expert = URIRef(f"https://id.skygest.io/expert/did-plc-{suffix}author")
        _cmc(g, cmc)
        g.add((cmc, EI.referencesVariable, VAR_MAIN))
        _post(g, post, expert)
        g.add((post, EI.evidences, cmc))
    g.serialize(FIXTURE_DIR / "cq-007.ttl", format="turtle")


def cq008() -> None:
    g = _base_graph()
    add_header(
        g,
        "cq-008",
        "Two CMCs on the same Variable — one fully resolved, one bare — cross-expert join payload.",
    )
    _variable(g, VAR_MAIN)
    # Claim A — fully annotated
    cmc_a = URIRef("https://id.skygest.io/cmc/cmc_01J_claim_a")
    post_a = URIRef("https://id.skygest.io/post/post_01J_a")
    expert_a = URIRef("https://id.skygest.io/expert/did-plc-aauthor")
    ctw_a = URIRef("https://id.skygest.io/temporal-window/tw_2025_a")
    _cmc(g, cmc_a)
    g.add((cmc_a, EI.referencesVariable, VAR_MAIN))
    g.add((cmc_a, EI.assertedValue, Literal("814", datatype=XSD.decimal)))
    g.add((cmc_a, EI.assertedUnit, Literal("GW")))
    g.add((cmc_a, EI.assertedTime, ctw_a))
    g.add((ctw_a, RDF.type, EI.ClaimTemporalWindow))
    g.add((ctw_a, RDF.type, OWL.NamedIndividual))
    _post(g, post_a, expert_a)
    g.add((post_a, EI.evidences, cmc_a))
    # Claim B — bare (no asserted*)
    cmc_b = URIRef("https://id.skygest.io/cmc/cmc_01J_claim_b")
    post_b = URIRef("https://id.skygest.io/post/post_01J_b")
    expert_b = URIRef("https://id.skygest.io/expert/did-plc-bauthor")
    _cmc(g, cmc_b)
    g.add((cmc_b, EI.referencesVariable, VAR_MAIN))
    _post(g, post_b, expert_b)
    g.add((post_b, EI.evidences, cmc_b))
    g.serialize(FIXTURE_DIR / "cq-008.ttl", format="turtle")


def cq009() -> None:
    """Well-formed fixture: every CMC has an evidencing source.

    CQ-009 SPARQL expects exactly 0 rows on a clean fixture.
    """
    g = _base_graph()
    add_header(
        g,
        "cq-009",
        "Every CMC in this fixture has an evidencing EvidenceSource. "
        "CQ-009 SPARQL must return 0 rows (invariant holds).",
    )
    _cmc(g, CMC_MAIN)
    _post(g, POST_MAIN, EXPERT_MAIN)
    g.add((POST_MAIN, EI.evidences, CMC_MAIN))
    # Second CMC also evidenced (by a chart this time)
    cmc_2 = URIRef("https://id.skygest.io/cmc/cmc_01J_chartclaim")
    chart = URIRef("https://id.skygest.io/chart/ch_01J")
    _cmc(g, cmc_2)
    g.add((chart, RDF.type, EI.Chart))
    g.add((chart, RDF.type, OWL.NamedIndividual))
    g.add((chart, EI.evidences, cmc_2))
    g.serialize(FIXTURE_DIR / "cq-009.ttl", format="turtle")


def cq010() -> None:
    g = _base_graph()
    add_header(
        g,
        "cq-010",
        "Full resolution fixture for CMC_MAIN: all five references populated.",
    )
    _cmc(g, CMC_MAIN)
    _variable(g, VAR_MAIN)
    _series(g, SER_MAIN)
    g.add((DIST_MAIN, RDF.type, DCAT.Distribution))
    g.add((DATASET_MAIN, RDF.type, DCAT.Dataset))
    g.add((AGENT_MAIN, RDF.type, EI.Organization))
    for x in (DIST_MAIN, DATASET_MAIN, AGENT_MAIN):
        g.add((x, RDF.type, OWL.NamedIndividual))
    g.add((CMC_MAIN, EI.referencesVariable, VAR_MAIN))
    g.add((CMC_MAIN, EI.referencesSeries, SER_MAIN))
    g.add((CMC_MAIN, EI.referencesDistribution, DIST_MAIN))
    g.add((CMC_MAIN, EI.referencesDataset, DATASET_MAIN))
    g.add((CMC_MAIN, EI.referencesAgent, AGENT_MAIN))
    _post(g, POST_MAIN, EXPERT_MAIN)
    g.add((POST_MAIN, EI.evidences, CMC_MAIN))
    g.serialize(FIXTURE_DIR / "cq-010.ttl", format="turtle")


def cq011() -> None:
    g = _base_graph()
    add_header(
        g,
        "cq-011",
        "Podcast segment with two distinct speakers (multi-speaker case).",
    )
    g.add((SEG_MAIN, RDF.type, EI.PodcastSegment))
    g.add((SEG_MAIN, RDF.type, OWL.NamedIndividual))
    for suffix in ("host", "guest"):
        expert = URIRef(f"https://id.skygest.io/expert/did-plc-{suffix}")
        g.add((expert, RDF.type, EI.Expert))
        g.add((expert, RDF.type, OWL.NamedIndividual))
        g.add((SEG_MAIN, EI.spokenBy, expert))
    # Segment needs a parent episode for ei:partOfEpisode exactly 1
    episode = URIRef("https://id.skygest.io/podcast-episode/ep_01J")
    g.add((episode, RDF.type, EI.PodcastEpisode))
    g.add((episode, RDF.type, OWL.NamedIndividual))
    g.add((SEG_MAIN, EI.partOfEpisode, episode))
    g.serialize(FIXTURE_DIR / "cq-011.ttl", format="turtle")


def cq012() -> None:
    g = _base_graph()
    add_header(
        g,
        "cq-012",
        "Podcast segment evidences one CMC.",
    )
    g.add((SEG_MAIN, RDF.type, EI.PodcastSegment))
    g.add((SEG_MAIN, RDF.type, OWL.NamedIndividual))
    episode = URIRef("https://id.skygest.io/podcast-episode/ep_01J")
    g.add((episode, RDF.type, EI.PodcastEpisode))
    g.add((episode, RDF.type, OWL.NamedIndividual))
    g.add((SEG_MAIN, EI.partOfEpisode, episode))
    cmc = URIRef("https://id.skygest.io/cmc/cmc_01J_from_segment")
    _cmc(g, cmc)
    g.add((SEG_MAIN, EI.evidences, cmc))
    g.serialize(FIXTURE_DIR / "cq-012.ttl", format="turtle")


def cq013() -> None:
    """Technology-classification fixture.

    Imports the hand-seeded technology-seeds SKOS tree so the
    ``(skos:broader|rdfs:subClassOf)*`` property path has something to
    traverse. One CMC is tagged with ``ei:concept/onshore-wind``, which
    is ``skos:broader`` of ``ei:concept/wind``. CQ-013 asks for CMCs
    classified under wind (transitively), so we expect the
    onshore-wind-tagged CMC to come back.
    """
    g = _base_graph()
    add_header(
        g,
        "cq-013",
        "CMC tagged with onshore-wind (skos:broader of wind). Transitive "
        "property-path walk to wind returns this CMC.",
    )
    # Inline the concept hierarchy so the fixture is self-contained.
    g.parse(CONCEPT_SEEDS, format="turtle")

    _cmc(g, CMC_MAIN)
    onshore_wind = URIRef("https://w3id.org/energy-intel/concept/onshore-wind")
    g.add((CMC_MAIN, EI.aboutTechnology, onshore_wind))
    # Ensure CMC has an evidencing source to keep CQ-009 invariant happy
    _post(g, POST_MAIN, EXPERT_MAIN)
    g.add((POST_MAIN, EI.evidences, CMC_MAIN))
    g.serialize(FIXTURE_DIR / "cq-013.ttl", format="turtle")


def cq014() -> None:
    g = _base_graph()
    add_header(
        g,
        "cq-014",
        "Two-hop walk: Post evidences a CMC tagged onshore-wind; transitive "
        "walk returns the Post when querying for wind.",
    )
    g.parse(CONCEPT_SEEDS, format="turtle")
    _cmc(g, CMC_MAIN)
    onshore_wind = URIRef("https://w3id.org/energy-intel/concept/onshore-wind")
    g.add((CMC_MAIN, EI.aboutTechnology, onshore_wind))
    _post(g, POST_MAIN, EXPERT_MAIN)
    g.add((POST_MAIN, EI.evidences, CMC_MAIN))
    g.serialize(FIXTURE_DIR / "cq-014.ttl", format="turtle")


# -------------------------------------------------------------------
# Verification
# -------------------------------------------------------------------


@dataclass
class FixtureVerdict:
    cq: str
    parsed: bool
    rowcount: int
    status: str  # "pass" | "fail"
    detail: str


def verify(cq_id: str, expected: str) -> FixtureVerdict:
    fixture = FIXTURE_DIR / f"{cq_id}.ttl"
    sparql = SPARQL_DIR / f"{cq_id}.sparql"
    if not fixture.exists() or not sparql.exists():
        return FixtureVerdict(cq_id, False, -1, "fail", "file missing")
    try:
        g = Graph()
        g.parse(fixture, format="turtle")
    except Exception as e:
        return FixtureVerdict(cq_id, False, -1, "fail", f"parse error: {e}")
    query = sparql.read_text()
    try:
        results = list(g.query(query))
    except Exception as e:
        return FixtureVerdict(cq_id, True, -1, "fail", f"sparql error: {e}")
    rowcount = len(results)
    status = "pass"
    detail = f"{rowcount} row(s)"
    if expected == "exactly_0":
        if rowcount != 0:
            status = "fail"
    elif expected == "exactly_1":
        if rowcount != 1:
            status = "fail"
    elif expected == "ge_1":
        if rowcount < 1:
            status = "fail"
    elif expected.startswith("eq_"):
        want = int(expected.split("_", 1)[1])
        if rowcount != want:
            status = "fail"
    return FixtureVerdict(cq_id, True, rowcount, status, detail)


CONTRACTS = {
    "cq-001": "exactly_1",
    "cq-002": "exactly_1",
    "cq-003": "exactly_1",
    "cq-004": "exactly_1",
    "cq-005": "exactly_1",
    "cq-006": "eq_2",
    "cq-007": "eq_2",
    "cq-008": "eq_2",
    "cq-009": "exactly_0",
    "cq-010": "exactly_1",
    "cq-011": "eq_2",
    "cq-012": "exactly_1",
    "cq-013": "ge_1",
    "cq-014": "ge_1",
}


def main() -> int:
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    builders = [
        cq001,
        cq002,
        cq003,
        cq004,
        cq005,
        cq006,
        cq007,
        cq008,
        cq009,
        cq010,
        cq011,
        cq012,
        cq013,
        cq014,
    ]
    for b in builders:
        b()

    print()
    print("=== fixture verification ===")
    failures = 0
    verdicts: list[FixtureVerdict] = []
    for cq in sorted(CONTRACTS):
        v = verify(cq, CONTRACTS[cq])
        verdicts.append(v)
        status_sym = "OK  " if v.status == "pass" else "FAIL"
        print(
            f"  {status_sym}  {cq:<7} expected={CONTRACTS[cq]:<12} rows={v.rowcount:<3}  {v.detail}"
        )
        if v.status == "fail":
            failures += 1

    # Emit a JSON-ish summary for downstream manifest update
    (FIXTURE_DIR / "_verdicts.txt").write_text(
        "\n".join(f"{v.cq}\t{v.status}\t{v.rowcount}\t{v.detail}" for v in verdicts)
    )

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
