# Ontology Design Pattern Catalog

**Referenced by:** `ontology-conceptualizer`, `ontology-architect`.
**Complements:** [`axiom-patterns.md`](axiom-patterns.md) (axiom-level building blocks).

An Ontology Design Pattern (ODP) is a reusable solution to a recurring
modeling problem, composed of multiple OWL axioms. This file catalogs the
design patterns the conceptualizer selects from and the architect instantiates;
`axiom-patterns.md` catalogs the axiom-level primitives that each ODP
compiles down to.

Use this file when:

- Choosing a pattern to model a CQ (conceptualizer, Step "Axiom Pattern Selection").
- Instantiating a DOSDP template (architect, Step "Bulk term creation via ROBOT/DOSDP").
- Deciding whether a CQ calls for value partition vs data property vs nominal set.
- Reviewing whether a draft encoding follows an established ODP or invents a new one.

## 1. DOSDP — the preferred pattern format

Dead-Simple OWL Design Patterns (DOSDP) separate the pattern from the fillers.
A `.yaml` pattern file declares variables and axioms; a `.tsv` filler file
supplies values for each instantiation. `dosdp-tools` expands the pair to OWL.

| Artifact | Role |
|---|---|
| `pattern.yaml` | Pattern skeleton: variables, axioms, annotations, readable definition template. |
| `pattern.tsv` | One row per instantiation; columns match pattern variables. |
| `dosdp-tools generate --template pattern.yaml --infile pattern.tsv --outfile out.ttl` | Expansion command. |

Prefer DOSDP over freehand OWL or raw ROBOT templates when: the pattern
will be used more than 3 times; the pattern requires a generated
`rdfs:label` / `skos:definition` template; the team wants an auditable
pattern library under `patterns/`. See
[`robot-template-preflight.md`](robot-template-preflight.md) for the
preflight that applies to both ROBOT-template and DOSDP-expanded output.

## 2. Pattern selection matrix (CQ → pattern)

Map a CQ wording to a candidate ODP before selecting axiom patterns.

| CQ wording | Recommended ODP | Axioms (see [`axiom-patterns.md`](axiom-patterns.md)) |
|---|---|---|
| "X has high/medium/low Y" | **Value partition** | § 5 Disjoint, § 6 Covering, § 8 Value partition |
| "X has N parts of type Y" | **Part-whole** (mereology) | § 2 Existential, § 7 Qualified cardinality, § 12 Property chain |
| "X plays the role of Y in context C" | **Role** (realizable entity) | § 2 Existential, § 4 Equivalent class, participation |
| "X participates in process P" | **Participation** | § 2 Existential, § 9 N-ary if multi-participant |
| "Document D is about topic T" | **Information-realization** | § 2 Existential, IAO `is about` |
| "X was observed/measured as Y" | **Observation/measurement** | § 9 N-ary relation |
| "A, B, C are the only kinds of Q" | **Exhaustive classification** | § 6 Covering axiom |
| "Thing identified by P" | **HasKey / Natural identifier** | § 11 HasKey |
| "X did Y at time T in place P" | **N-ary relation** | § 9 N-ary relation |

The left column is a user-facing phrasing; the middle column is the pattern
name; the right column cites the atomic axiom patterns the ODP composes.

## 3. Core patterns — when to use each

### 3.1 Value partition

Represent a quality value space as a closed set of value classes under an
exhaustive, disjoint partition. Prefer over (a) free-text data property,
(b) individuals in a `rdf:List`, (c) nominals.

**Use when:** values are a finite, stable, named set (high/medium/low; primary
colors; traffic-light states). **Do not use when:** values are naturally
numeric or arbitrary strings.

**Compiles to:** § 5 Disjoint + § 6 Covering + subclass axioms on each value
+ a property-some restriction on each bearing class.

### 3.2 Part-whole

Model aggregate structure using `BFO:0000050 part of` or a domain-specific
sub-property with explicit cardinality (`hasMember exactly 4`) and/or a
property chain for transitive location (`hasPart ∘ locatedIn → locatedIn`).

**Use when:** the CQ mentions "parts of", "members of", "consists of".
Mandatory cardinality requires OWL 2 DL (see
[`owl-profile-playbook.md § 3`](owl-profile-playbook.md#3-construct-support-matrix-architect-quick-reference)).

**Anti-pattern warning:** do not conflate `part of` with `member of` or
`subclass of`. See [`anti-patterns.md`](anti-patterns.md) § OO-inheritance leakage.

### 3.3 Role

A role is a realizable entity (BFO `role`) that an independent continuant
plays in a context. The entity is not the role; the entity *bears* the role.
Student is not a subclass of Person; Student is a role borne by Person.

**Use when:** the CQ uses relational identity ("as a patient", "as an
employer"). **Do not use when:** the category is intrinsic (Mammal, Liquid).

**Cross-reference:** [`bfo-decision-recipes.md`](bfo-decision-recipes.md)
§ "role vs type" recipe.

### 3.4 Participation

Participants and processes are modeled via participation relations
(`RO:0000057 has participant` / `BFO:0000056 participates in`). The process
is a first-class entity, not an attribute of the participant.

**Use when:** a CQ asks "who/what participated in P?", "when did P occur?",
"what was produced by P?". If the process has more than two participants or
carries additional context (time, role, quality), promote to an N-ary
relation pattern (§ 3.5).

### 3.5 N-ary relation (reification)

When a "relation" involves >2 participants or carries context
(time, role, certainty, observer), reify as a class. See
[`axiom-patterns.md § 9`](axiom-patterns.md).

**Use when:** CQ has ≥ 3 variables tied together by one event/state.
**Avoid:** faking N-ary with a chain of binary properties whose endpoints
are disconnected ("lost arguments").

### 3.6 Information-realization

An information artifact (IAO `information content entity`) is *about* some
entity, *concretized by* a bearer (file, page), and may be *realized in*
some process (reading, executing). The pattern separates the information,
its about-ness, and its physical bearer — three distinct classes.

**Use when:** the CQ mentions documents, reports, datasets, instructions,
measurements. Relevant IAO terms: `IAO:0000030 information content entity`,
`IAO:0000136 is about`, `IAO:0000219 denotes`.

## 4. Profile compatibility quick-check

Selecting a pattern affects profile reachability. Quick reference — see
[`owl-profile-playbook.md § 3`](owl-profile-playbook.md#3-construct-support-matrix-architect-quick-reference)
for the full matrix.

| Pattern | EL | QL | RL | DL | Notes |
|---|:--:|:--:|:--:|:--:|---|
| Value partition (disjoint union) | N | N | N | Y | Needs DL for `DisjointUnion`. |
| Part-whole w/ qualified cardinality | N | N | N | Y | ELK silently ignores qualified cardinality. |
| Role (existential only) | Y | Y | Y | Y | Stays EL-safe if restricted to `some`. |
| Participation (binary) | Y | Y | Y | Y | EL-safe. |
| N-ary (reified) | Y | Y | Y | Y | The reification trick is specifically to stay in any profile. |
| Property chain | Y | N | Y | Y | QL disallows chains. |
| Closure axiom (`some` + `only`) | N | N | partial | Y | `only` is non-EL. |

Rule of thumb: if a pattern row shows `N` for your target profile, either
(a) pick a different pattern, or (b) widen the profile and document in
`docs/scope.md § Profile`. Do **not** encode the pattern and let the
reasoner silently ignore parts of it.

## 5. Anti-patterns specific to ODP selection

| Anti-pattern | Symptom | Fix |
|---|---|---|
| **Pattern name-dropping** | "We used the role pattern" — no axioms present. | Require an axiom-plan entry naming the ODP and citing the axiom-patterns rows used. |
| **Invent-over-reuse** | Team creates a custom pattern for a case an ODP covers. | Cross-check against § 2 before creating new classes; cite the ODP source. |
| **Value partition via data property** | Quality modeled as `xsd:string` with informal values. | Refactor to value-partition ODP (§ 3.1). |
| **Binary chain as fake N-ary** | Two participants linked through a free-floating middle term. | Promote to N-ary reification (§ 3.5). |
| **Role leak** | Role modeled as a subclass of the independent continuant (`Student SubClassOf Person`). | Role as realizable entity; `Person` *bears* `Student` (§ 3.3). |

Each anti-pattern above should be detectable via a SPARQL probe in
[`anti-patterns.md`](anti-patterns.md); if the probe does not exist, add it
when the anti-pattern is first observed in the wild.

## 6. Sources and further reading

- [Ontology Design Patterns portal (ontologydesignpatterns.org)](http://ontologydesignpatterns.org/wiki/Main_Page) — ODP catalog, participation, role, information-realization.
- [DOSDP specification](https://incatools.github.io/dead_simple_owl_design_patterns/) — dosdp-tools, pattern YAML schema, TSV filler format.
- [OBO Foundry patterns (odk/patterns)](https://github.com/INCATools/ontology-development-kit) — ODK ships with a `patterns/` convention.
- [BFO 2020 axiom library](https://github.com/BFO-ontology/BFO-2020) — participation and role grounding in a top-level ontology.

## 7. Worked examples

See (Wave 4):

- [`worked-examples/ensemble/conceptualizer.md`](worked-examples/ensemble/conceptualizer.md) — picking value-partition for pitch range, role for ensemble seat, N-ary for performance.
- [`worked-examples/microgrid/conceptualizer.md`](worked-examples/microgrid/conceptualizer.md) — picking part-whole for array→inverter→battery topology, participation for dispatch event, information-realization for telemetry packet.
