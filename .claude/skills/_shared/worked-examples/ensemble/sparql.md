# Ensemble — `sparql-expert` walkthrough

Walks [`sparql-expert`](../../../sparql-expert/SKILL.md) Steps 0–5.5 for
CQ-E-001..005. Goal: produce each CQ query with a declared entailment
regime + expected-results contract, preflight via `prepareQuery`, and
surface the **COUNT vs row-shape** pitfall on CQ-E-003.

## Step 0 — purpose classification (header of every file)

Every CQ file opens:

```sparql
# purpose: cq
# entailment: {simple|owl-el|owl-dl}
# target: tests/fixtures/cq-e-00N.ttl
```

## CQ-E-001 — "Which ensembles consist of exactly four string players?"

**Step 2.5 entailment:** `owl-dl` — classification via
`hasMember exactly 4 Musician` is DL-only (ELK silently skips).

**Step 3 draft (`tests/cq-e-001.sparql`):**

```sparql
# purpose: cq
# entailment: owl-dl
# target: tests/fixtures/cq-e-001.ttl
PREFIX ens: <http://example.org/ensemble/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?ensemble ?label WHERE {
  ?ensemble a ens:StringQuartet ;
            rdfs:label ?label .
}
```

**Step 4.5 contract (manifest row):**

```yaml
cq_id: CQ-E-001
entailment: owl-dl
expected_results_contract: {shape: subset, cardinality: "1..n", per_row: [ensemble, label]}
```

**Step 5.5 sanity:** `sanity_check: pass` when run against the reasoned
graph (`robot reason --reasoner HermiT` first); returns zero rows on the
asserted file — that is a regime mismatch, not a query bug (see the
Step 5.5 *entailment mismatch* pitfall).

## CQ-E-002 — "What instruments does a given musician play?"

**Entailment:** `rdfs` (subclass/subproperty only — no complex
axioms).

```sparql
# purpose: cq
# entailment: rdfs
# target: tests/fixtures/cq-e-002.ttl
PREFIX ens: <http://example.org/ensemble/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?musician ?instrument ?label WHERE {
  VALUES ?musician { ens:Alice }
  ?musician ens:plays ?instrument .
  ?instrument rdfs:label ?label .
}
```

**Contract:** `{shape: subset, cardinality: "0..n", per_row: [musician, instrument, label]}`.

## CQ-E-003 — "Which 2024 performances featured a specific composition?" (SIGNATURE pitfall)

First draft used `(COUNT(*) AS ?n)` to answer "how many", but the CQ
actually asks for the *list*. Two shape contracts are possible:

### Wrong — COUNT aggregate returns 1 row

```sparql
# FAIL: aggregate row-count mismatch
SELECT (COUNT(*) AS ?n) WHERE {
  ?perf a ens:Performance ;
        ens:hasDate ?d ;
        ens:hasPiece ens:OpusA .
  FILTER(YEAR(?d) = 2024)
}
```

Expected-results contract `{shape: exact-rows, cardinality: 5}` fails
because this query returns **one row with a single integer column**, not
five rows. Pitfall source: `_shared/anti-patterns.md` aggregate
row-count mismatch (referenced from SKILL.md Step 5.5).

### Right — rowful SELECT

```sparql
# purpose: cq
# entailment: simple
# target: tests/fixtures/cq-e-003.ttl
PREFIX ens: <http://example.org/ensemble/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?perf ?date WHERE {
  ?perf a ens:Performance ;
        ens:hasDate ?date ;
        ens:hasPiece ens:OpusA .
  FILTER(YEAR(?date) = 2024)
}
```

**Contract:** `{shape: exact-rows, cardinality: 5, per_row: [perf, date], order_sensitive: false}`.

**Step 5.5 result:** `sanity_check: pass` with 5 rows on the fixture.
If one wants the count alongside, split into a second query with
`shape: count, cardinality: 1`.

## CQ-E-004 — "Which ensemble types are defined by their instrumentation?"

```sparql
# purpose: cq
# entailment: owl-dl
# target: tests/fixtures/cq-e-004.ttl
PREFIX ens: <http://example.org/ensemble/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?class ?expr WHERE {
  ?class a owl:Class ;
         owl:equivalentClass ?expr .
  ?expr owl:onProperty ens:hasMember .   # reaching through the restriction
}
```

**Contract:** `{shape: subset, cardinality: "1..n", per_row: [class, expr]}`. Expected row: `ens:StringEnsemble` with the qualified
restriction blank node.

## CQ-E-005 — "Which MIMO terms map to our ensemble instrument classes, and where does schema.org exactMatch risk a clique > 3?"

```sparql
# purpose: mapping
# entailment: simple
# target: ontologies/ensemble/mappings/ensemble-to-mimo.sssom.ttl
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?start ?mid ?end WHERE {
  ?start skos:exactMatch+ ?mid .
  ?mid skos:exactMatch+ ?end .
  FILTER(?start != ?mid && ?mid != ?end && ?start != ?end)
}
```

**Contract:** `{shape: zero-rows}` — any row is a clique violation per
[`mapper.md`](mapper.md) Step 5.5 threshold. Non-zero rows → loopback to
`ontology-mapper` (`mapping_clique`).

## Step 5 — execution contract record (`tests/cq-test-manifest.yaml` excerpt)

```yaml
tests:
  - id: CQ-E-001
    file: tests/cq-e-001.sparql
    entailment: owl-dl
    expected_results_contract: {shape: subset, cardinality: "1..n", per_row: [ensemble, label]}
    parse_status: ok
    fixture_run_status: pass
    sanity_check: pass
  - id: CQ-E-003
    file: tests/cq-e-003.sparql
    entailment: simple
    expected_results_contract: {shape: exact-rows, cardinality: 5, per_row: [perf, date]}
    parse_status: ok
    fixture_run_status: pass
    sanity_check: pass
  # …
```

## Property-path caution

CQ-E-002 intentionally uses a bound subject (`VALUES ?musician`) before
the `plays` triple. Without the `VALUES`, the query would match every
musician × instrument pair in the graph — property-path blowup is real
for cyclic ontologies (though `plays` isn't transitive here, the caution
is preserved for the pattern's microgrid counterpart, see
[`../microgrid/sparql.md`](../microgrid/sparql.md)).

## Handoff

Preflighted CQ-E-001..005 + manifest → `ontology-requirements` Step 7.5
(parse_status, fixture_run_status, entailment, sanity_check). Regime
mismatch on CQ-E-001 asserted graph surfaces as `sparql_shape` loopback
to `sparql-expert` via `cq-manifest-audit.json` (see
[`validator.md`](validator.md) L4.5).
