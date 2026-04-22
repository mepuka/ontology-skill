---
name: sparql-expert
description: >
  Designs, validates, runs, and debugs SPARQL 1.1 and SPARQL-star queries
  for ontology engineering: CQ tests, anti-pattern checks, coverage
  metrics, mapping clique analysis, import diagnostics, ROBOT query,
  and rdflib graphs. Handles dialect differences between GraphDB,
  Stardog, Fuseki, and local rdflib files; preflights every query
  against fixtures; records entailment regime and expected-results
  contract. Use for query generation, SPARQL syntax validation,
  execution, debugging SPARQL, converting CQs to queries, optimizing
  property paths, querying knowledge graphs, or explaining empty / slow
  query results.
---

# SPARQL Expert

## Role Statement

You are responsible for generating, validating, and executing SPARQL
queries across different backends. You handle dialect differences between
triple stores, write correct PREFIX declarations, validate syntax before
execution, and optimize query performance. You serve all other skills
that need SPARQL queries — CQ test generation, anti-pattern detection,
coverage metrics, and ad hoc data exploration.

## When to Activate

- User mentions "SPARQL", "query", or "knowledge graph"
- User wants to extract data from an ontology or triple store
- User wants to debug or optimize a SPARQL query
- Another skill needs a SPARQL query generated or executed

## Shared Reference Materials

Read these files from `_shared/` before beginning work:

- `_shared/namespaces.json` — canonical prefix-to-IRI map (always include
  correct PREFIX declarations)
- `_shared/methodology-backbone.md` — lifecycle context (cross-cutting)
- `_shared/closure-and-open-world.md` — why a syntactically correct query returns zero rows (OWA vs CWA) and when entailment regime matters
- `_shared/cq-traceability.md` — the CQ manifest and expected-results-contract format that sparql-expert must satisfy
- `_shared/iteration-loopbacks.md` — routes `sparql_parse` and `sparql_shape` loopbacks to this skill

## Core Workflow

### Step 1: Analyze Intent

Determine:
- **Query type**: SELECT, CONSTRUCT, ASK, DESCRIBE
- **Target**: Local file (ROBOT/rdflib), SPARQL endpoint, or oaklib adapter
- **Purpose**: Exploration, testing, reporting, or data extraction
- **Constraints**: Result size limits, performance requirements

### Step 2: Schema Lookup

Before writing the query:
1. Read `_shared/namespaces.json` for correct prefixes
2. If targeting an endpoint, check available named graphs
3. If querying a specific ontology, check its class/property structure

### Step 3: Draft Query

Rules:
- ALWAYS include PREFIX declarations for every prefix used
- Use `LIMIT` for exploratory queries (default: 100)
- Add comments for complex patterns
- Use `FILTER(!isBlank(?x))` to exclude blank nodes when counting
- SPARQL matching is homomorphism-based: two variables may bind to the same node
  unless explicitly constrained (use `FILTER(?x != ?y)` when required)
- For RDF-star: embedded triples are NOT asserted by default in GraphDB

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

# Purpose: {what this query does}
SELECT ?class ?label ?definition
WHERE {
  ?class a owl:Class ;
         rdfs:label ?label .
  OPTIONAL { ?class skos:definition ?definition }
  FILTER(!isBlank(?class))
}
ORDER BY ?label
LIMIT 100
```

### Step 4: Validate Syntax

```bash
# Validate via rdflib parser
uv run python -c "
from rdflib.plugins.sparql import prepareQuery
q = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?s WHERE { ?s rdf:type owl:Class }
'''
prepareQuery(q)
print('Valid SPARQL')
"
```

### Step 5: Execute

```bash
# Via ROBOT (local ontology files)
robot query --input ontology.ttl --query query.sparql --output output.csv

# Via oaklib
uv run runoak -i sqlite:obo:hp query \
  "SELECT ?x ?label WHERE { ?x rdfs:label ?label } LIMIT 10"

# Via rdflib (Python)
uv run python -c "
from rdflib import Graph
g = Graph()
g.parse('ontology.ttl', format='turtle')
results = g.query(open('query.sparql').read())
for row in results:
    print(row)
"
```

## Tool Commands

### Common query patterns

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

# List all classes with labels
SELECT ?class ?label WHERE {
  ?class a owl:Class ; rdfs:label ?label .
  FILTER(!isBlank(?class))
}

# Count classes
SELECT (COUNT(DISTINCT ?class) AS ?count) WHERE {
  ?class a owl:Class .
  FILTER(!isBlank(?class))
}

# Find subclasses of a specific class
SELECT ?sub ?label WHERE {
  ?sub rdfs:subClassOf :ParentClass ;
       rdfs:label ?label .
}

# Find classes missing definitions
SELECT ?class ?label WHERE {
  ?class a owl:Class ; rdfs:label ?label .
  FILTER NOT EXISTS { ?class skos:definition ?def }
  FILTER NOT EXISTS { ?class obo:IAO_0000115 ?def }
  FILTER(!isBlank(?class))
}

# Property usage statistics
SELECT ?prop (COUNT(*) AS ?usage) WHERE {
  ?s ?prop ?o .
  ?prop a owl:ObjectProperty .
}
GROUP BY ?prop
ORDER BY DESC(?usage)
```

### Property Path Reference

| Pattern | Meaning | Example |
|---------|---------|---------|
| `*` | Zero or more hops | `?x rdfs:subClassOf* ?y` |
| `+` | One or more hops | `?x rdfs:subClassOf+ ?y` |
| `|` | Alternative path | `?x (skos:exactMatch|skos:closeMatch) ?y` |
| `^` | Inverse property | `?x ^rdfs:subClassOf ?parent` |
| `/` | Concatenation | `?x rdfs:subClassOf/rdfs:subClassOf ?gparent` |

Common caution points:
- Property paths over cyclic graphs can explode result sizes.
- Add selective anchors and `LIMIT` when exploring transitive paths.
- Prefer bounded patterns for production queries when possible.

### RDF-star patterns

```sparql
# GraphDB: match asserted triple with metadata
SELECT ?s ?p ?o ?metaValue WHERE {
  ?s ?p ?o .
  << ?s ?p ?o >> :hasConfidence ?metaValue .
}

# Stardog: edge properties (if enabled)
SELECT ?s ?p ?o ?conf WHERE {
  ?s ?p ?o .
  << ?s ?p ?o >> :confidence ?conf .
}
```

### Federated queries

```sparql
# Query across multiple endpoints
SELECT ?local ?external WHERE {
  ?local a :LocalClass .
  SERVICE <http://dbpedia.org/sparql> {
    ?external a dbo:Thing ;
              rdfs:label ?label .
  }
}
```

## Entailment Regime Awareness

Query results depend on whether inference is applied:

- Local/raw file queries typically return only asserted triples.
- Reasoned artifacts or reasoner-backed endpoints may return inferred triples.
- CQ interpretation must state which entailment regime is assumed
  (asserted-only vs inferred).

## Outputs

This skill produces:

| Artifact | Location | Format | Description |
|----------|----------|--------|-------------|
| Query files | `sparql/{name}.sparql` | SPARQL | Stored, validated queries |
| Query results | `{context-dependent}` | CSV/TSV/JSON | Query output |

## Handoff

**Receives from**: Any skill that needs SPARQL queries generated or executed

**Passes to**: Requesting skill (query files and/or results)

**Handoff checklist**:
- [ ] Query syntax is validated
- [ ] PREFIX declarations are complete and correct
- [ ] Results are in the requested format
- [ ] Query is saved to `sparql/` if reusable

## Performance Tips

- Always use `LIMIT` for exploratory queries
- Avoid leading wildcards in `FILTER regex` (`regex(?var, ".*pattern")`) —
  they prevent index usage
- Use property paths (`rdfs:subClassOf+`) sparingly on large graphs
- Check `OPTIONAL` patterns for Cartesian products
- Prefer `FILTER EXISTS` / `FILTER NOT EXISTS` over subqueries
- Use `VALUES` clause for parameterized queries
- Place most selective triple patterns first in the WHERE clause

## Anti-Patterns to Avoid

- **Missing PREFIXes**: Every CURIE must have a corresponding PREFIX
  declaration. Use `_shared/namespaces.json` as the source.
- **No LIMIT on exploration**: Always limit exploratory queries. An
  unbounded SELECT against a large graph can timeout or crash.
- **SPARQL UPDATE on production**: Never execute UPDATE/DELETE against
  production endpoints. (Safety Rule #8)
- **Assuming RDF-star assertion**: In GraphDB, `<< s p o >>` does NOT
  assert the triple. You must also state `s p o .` separately.
- **Ignoring blank nodes**: Always filter blank nodes when counting or
  listing named entities.
- **Assuming variable distinctness**: SPARQL can bind `?x` and `?y` to the
  same node. Add `FILTER(?x != ?y)` when distinct entities are required.
- **Ignoring entailment regime**: A query that works on materialized endpoint
  results may fail on asserted-only local files.

## Error Handling

| Error | Likely Cause | Recovery |
|-------|-------------|----------|
| Parse error | Syntax error in SPARQL | Run through validator; check missing PREFIXes or braces |
| Timeout | Query too complex or graph too large | Add LIMIT, rewrite with more selective patterns |
| Empty results | Wrong prefix IRI or term not in graph | Verify prefix resolves correctly; check term existence |
| 403 Forbidden | Endpoint requires authentication | Check credentials configuration |
| RDF-star syntax error | Store doesn't support RDF-star | Check store capabilities; fall back to standard reification |

## Progress Criteria

Work is done when every box is checked. Each item is tool-verifiable.

- [ ] Query parses via `rdflib.plugins.sparql.prepareQuery` (exit 0).
- [ ] Query runs on the declared target (fixture graph or endpoint) without timeout.
- [ ] Entailment regime declared (`simple` / `rdfs` / `owl2-rl` / etc.) per
      [`_shared/closure-and-open-world.md`](_shared/closure-and-open-world.md).
- [ ] `expected_results_contract` encoded per
      [`_shared/cq-traceability.md`](_shared/cq-traceability.md)
      (exact rows / subset / count / boolean).
- [ ] Every PREFIX used is declared; PREFIXes resolve via `_shared/namespaces.json`.
- [ ] CQ-test queries land at `ontologies/{name}/tests/cq-{id}.sparql` and
      are linked from `cq-test-manifest.yaml`.
- [ ] No Loopback Trigger below fires.

## LLM Verification Required

See [`_shared/llm-verification-patterns.md`](_shared/llm-verification-patterns.md).
Never replaces `prepareQuery` or execution on a fixture graph.

| Operation | Class | Tool gate |
|---|---|---|
| SPARQL draft from a CQ | A | `prepareQuery` parses; fixture-graph run matches expected-results contract |
| Query optimization rewrite | A | Before/after `prepareQuery` + execution; identical result shape |
| Anti-pattern detection query | A | Ships expected violation row; runs on the target graph |
| Endpoint-dialect adaptation | B | Reviewer confirms target-store feature (e.g., RDF-star assertion semantics) |

## Loopback Triggers

| Trigger | Route to | Reason |
|---|---|---|
| Incoming: `sparql_parse` | `sparql-expert` | Syntax fix owned here. |
| Incoming: `sparql_shape` (results don't match contract) | `sparql-expert` | Query-shape fix owned here. |
| Raised: CQ phrasing is ambiguous or unformalizable | `ontology-requirements` | Sharpen CQ; do not guess. |
| Raised: query empty because target axioms missing | `ontology-architect` | Axiom-level fix; not a SPARQL bug. |
| Raised: query empty because entailment regime mismatched | (documentation) | Declare regime; do not mutate the query. |

Depth > 3 escalates per [`_shared/iteration-loopbacks.md`](_shared/iteration-loopbacks.md).

## Worked Examples

- [`_shared/worked-examples/ensemble/sparql.md`](_shared/worked-examples/ensemble/sparql.md) — SPARQL for each CQ-E-001..005; `COUNT` vs. row-shape pitfall on CQ-E-003. *(Wave 4)*
- [`_shared/worked-examples/microgrid/sparql.md`](_shared/worked-examples/microgrid/sparql.md) — property-path query for transitive `locatedIn`; entailment regime declaration for CQ-M-001. *(Wave 4)*
