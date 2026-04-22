# Microgrid — `sparql-expert` walkthrough

Walks [`sparql-expert`](../../../sparql-expert/SKILL.md) Steps 0–5.5 for
CQ-M-001..005. Signature content: the **property-path query for
transitive `locatedIn`** (CQ-M-001) with its load-bearing
`entailment: owl-el` declaration, and a decomposition showing that the
same CQ phrased two different ways hits distinct traps.

## Step 0 — purpose classification (header of every file)

```sparql
# purpose: cq
# entailment: {simple|rdfs|owl-el}
# target: tests/fixtures/cq-m-00N.ttl
```

## CQ-M-001 — "Transitive parts of a microgrid, grouped by equipment type" (SIGNATURE)

**Step 2.5 entailment:** `owl-el`. The key axiom
`locatedIn SubPropertyChainOf hasPart ∘ locatedIn` expands
`ensemble hasPart battery` + `battery locatedIn siteA` into
`ensemble locatedIn siteA` — but only under EL (or stronger) reasoning.
Running against an asserted-only graph returns a fraction of the
expected rows.

### First draft — raw property path (wrong regime)

```sparql
# purpose: cq
# entailment: simple                  # ← wrong; see sanity check below
# target: tests/fixtures/cq-m-001.ttl
PREFIX mg: <http://example.org/microgrid/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?part ?type WHERE {
  mg:MainSite mg:hasPart+ ?part .        # property path: transitive closure of hasPart
  ?part a ?type .
}
```

**Step 5.5 sanity:** Returns 12 rows (direct hasPart chain). Expected
72 rows (including transitive locatedIn via the chain). `sanity_check:
fail_regime` — the fix is NOT the query but the regime.

### Corrected — via reasoned graph + chain entailment

```sparql
# purpose: cq
# entailment: owl-el
# target: tests/fixtures/cq-m-001.ttl   (reasoned via ELK before query)
PREFIX mg: <http://example.org/microgrid/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?part ?type WHERE {
  ?part mg:locatedIn mg:MainSite .       # chain entailment: hasPart ∘ locatedIn → locatedIn
  ?part a ?type .
  FILTER(?type != owl:NamedIndividual && !isBlank(?type))
}
ORDER BY ?type
```

**Contract:** `{shape: exact-rows, cardinality: 72, per_row: [part, type], order_sensitive: false}`.

**Execution protocol:** run `.local/bin/robot reason --reasoner ELK --input validation/merged.ttl --output validation/reasoned-el.ttl` **before** `robot query`; query the reasoned graph, not the edit file. The
manifest row encodes this:

```yaml
- id: CQ-M-001
  file: tests/cq-m-001.sparql
  entailment: owl-el
  reason_before_query: true
  expected_results_contract: {shape: exact-rows, cardinality: 72, per_row: [part, type]}
  sanity_check: pass
```

## CQ-M-002 — "Islanding dispatch events in the last month"

```sparql
# purpose: cq
# entailment: rdfs
# target: tests/fixtures/cq-m-002.ttl
PREFIX mg: <http://example.org/microgrid/>
PREFIX ro: <http://purl.obolibrary.org/obo/RO_>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?event ?equipment ?start ?end WHERE {
  ?event a mg:IslandingEvent ;
         mg:hasStart ?start ;
         mg:hasEnd ?end ;
         ro:0000057 ?equipment .          # has_participant
  FILTER(?start >= "2026-03-22T00:00:00Z"^^xsd:dateTime)
}
```

**Contract:** `{shape: subset, cardinality: "0..n", per_row: [event, equipment, start, end]}`. Uses RDFS entailment only — subclass
`IslandingEvent → DispatchEvent` is not needed because the query
targets the subclass directly.

## CQ-M-003 — "Telemetry packets about a given battery"

```sparql
# purpose: cq
# entailment: simple
# target: tests/fixtures/cq-m-003.ttl
PREFIX mg: <http://example.org/microgrid/>
PREFIX iao: <http://purl.obolibrary.org/obo/IAO_>

SELECT ?packet ?property WHERE {
  VALUES ?battery { mg:Battery_07 }
  ?packet a mg:TelemetryPacket ;
          iao:0000136 ?battery ;        # is_about
          mg:hasMeasuredProperty ?property .
}
```

**Contract:** `{shape: subset, cardinality: "0..n", per_row: [packet, property]}`.

## CQ-M-004 — "Primary-inverter role bearers per subgrid"

```sparql
# purpose: cq
# entailment: owl-el
# target: tests/fixtures/cq-m-004.ttl (reasoned)
PREFIX mg: <http://example.org/microgrid/>
PREFIX bfo: <http://purl.obolibrary.org/obo/BFO_>

SELECT ?inverter ?subgrid WHERE {
  ?subgrid mg:hasPart ?inverter .
  ?inverter a mg:Inverter ;
            bfo:0000196 ?role .         # bearerOf
  ?role a mg:PrimaryInverterRole .
}
```

**Contract:** `{shape: subset, cardinality: "0..n", per_row: [inverter, subgrid]}`.
SHACL shape `PrimaryInverterRoleShape` enforces at most one per
subgrid; the SPARQL side simply lists.

## CQ-M-005 — "exactMatch rows escalating to equivalentClass" (mapping-purpose)

```sparql
# purpose: mapping
# entailment: simple
# target: ontologies/microgrid/mappings/microgrid-to-oeo.sssom.ttl
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?our_class ?oeo_class ?predicate WHERE {
  ?our_class ?predicate ?oeo_class .
  FILTER(?predicate IN (skos:exactMatch, skos:closeMatch))
  FILTER(STRSTARTS(STR(?our_class), "http://example.org/microgrid/"))
  FILTER(STRSTARTS(STR(?oeo_class), "http://openenergy-platform.org/ontology/"))
}
```

**Contract:** `{shape: subset, cardinality: "0..n", per_row: [our_class, oeo_class, predicate]}`. Combined with the clique-check SPARQL
(see [`../ensemble/sparql.md#cq-e-005`](../ensemble/sparql.md)), this
drives the mapper's CQ-M-005 promotion candidacy review.

## Property-path blowup caution (CQ-M-001 variant)

A naive rewrite of CQ-M-001 using unbounded `mg:(hasPart|locatedIn)+`
property path instead of the chain-entailment approach:

```sparql
# ANTI-PATTERN — property-path blowup
SELECT ?part WHERE {
  mg:MainSite (mg:hasPart|mg:locatedIn)+ ?part .
}
```

On a cyclic graph (rare but possible — misstated part-of cycle during
editing), this query can return exponential row counts. Step 5.5
cardinality rule catches the blowup: if returned count > 10× expected,
it's a contract violation, not a query bug. Prefer the
chain-entailment + reasoner approach (CQ-M-001 corrected version).

## Manifest integration

```yaml
tests:
  - id: CQ-M-001
    entailment: owl-el
    reason_before_query: true
    expected_results_contract: {shape: exact-rows, cardinality: 72, per_row: [part, type]}
    sanity_check: pass
  - id: CQ-M-004
    entailment: owl-el
    reason_before_query: true
    expected_results_contract: {shape: subset, cardinality: "0..n", per_row: [inverter, subgrid]}
  # …
```

## Handoff

All five CQ files + manifest → `ontology-requirements` Step 7.5
preflight. Regime mismatch on CQ-M-001 (the first-draft variant) would
route as `sparql_shape` back to `sparql-expert`. The validator L4
runs the manifest against `reasoned-el.ttl` (not `microgrid.ttl`) per
the `reason_before_query: true` flag.
