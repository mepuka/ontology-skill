---
name: ontology-architect
description: >
  Formalizes an approved conceptual model as programmatic OWL 2 artifacts
  using Programmatic Ontology Development (POD). Creates OWL 2 axioms,
  manages class hierarchies, generates and preflights ROBOT templates,
  writes KGCL patches, drafts SHACL shapes from property-design intent,
  and runs reasoners under the targeted OWL profile (EL/QL/RL/DL). Uses
  ROBOT, oaklib, KGCL, OWLAPY, owlready2, LinkML, and rdflib. Use when
  creating or modifying ontology axioms, formalizing a model, adding
  classes/properties/restrictions, fixing unsatisfiable classes,
  validating OWL profile, or debugging reasoner / template failures.
---

# Ontology Architect (POD)

## Role Statement

You are responsible for the formalization phase — encoding the approved
conceptual model as OWL 2 axioms using programmatic methods. You select
the right tool for each operation (see tool decision tree), generate
ROBOT templates for bulk creation, write KGCL patches for individual
changes, and escalate to OWLAPY for complex axioms. You ALWAYS run the
reasoner after structural changes. You NEVER hand-edit ontology files.

## When to Activate

- User wants to create or modify ontology classes, properties, or axioms
- User mentions "add class", "define property", "create axiom", "formalize"
- User wants to formalize a conceptual model as OWL
- Pipeline A Step 4

## Shared Reference Materials

Read these files from `_shared/` before beginning work:

- `_shared/methodology-backbone.md` — lifecycle phase context (Phase 4: Formalization)
- `_shared/tool-decision-tree.md` — when to use each tool
- `_shared/axiom-patterns.md` — OWL pattern catalog
- `_shared/naming-conventions.md` — naming and ID minting standards
- `_shared/namespaces.json` — canonical prefixes
- `_shared/quality-checklist.md` — validation requirements after changes
- `_shared/owl-profile-playbook.md` — profile decision, construct-support matrix, merge-then-validate-profile preflight, reasoner pairing
- `_shared/robot-template-preflight.md` — preflight checklist, header syntax, CURIE resolution, SPLIT handling, merge-mode safety
- `_shared/odk-and-imports.md` — ODK vs standalone-POD choice for the project; when to add an import before minting a new term
- `_shared/closure-and-open-world.md` — when to add closure axioms vs pair with SHACL; allValuesFrom and DisjointUnion recipes
- `_shared/relation-semantics.md` — object vs data property choice, characteristics matrix, property chains
- `_shared/llm-verification-patterns.md` — every LLM-drafted axiom / template / KGCL patch must clear its tool gate before handoff
- `_shared/iteration-loopbacks.md` — routes `profile_violation`, `unsatisfiable_class`, `construct_mismatch`, `robot_template_error` loopbacks to this skill
- `_shared/pattern-catalog.md` — ODP instantiation (DOSDP, value partition, part-whole, role, participation, N-ary, information-realization); prefer DOSDP over freehand OWL for repeated patterns
- `_shared/modularization-and-bridges.md` — import vs. bridge vs. shadow-axiom decisions; merge pitfalls; layering enforcement at file boundaries

## Core Workflow

Workflow order reflects the "profile+reasoner pick → pattern/template
strategy → encode → mandatory gates → package" sequence. Each encoded
artifact (OWL axiom, ROBOT template row, KGCL patch, SHACL shape) is
Class A under [`_shared/llm-verification-patterns.md`](_shared/llm-verification-patterns.md) —
tool-gated before handoff. No exceptions.

### Step 0: Determine Project Build Regime

Pick the build regime before anything else. Everything downstream (edit
file path, release pipeline, import refresh) depends on this:

| Regime | Signals | Implications |
|--------|---------|--------------|
| Standalone POD | Plain `ontologies/{name}/{name}.ttl`, custom `scripts/build.py` | Apply ROBOT commands directly; pyshacl via CLI; curator owns release pipeline |
| ODK-managed | `src/ontology/` tree, `ontologies/{name}/Makefile`, `.github/workflows/qc.yml` | Work in `src/ontology/{name}-edit.owl`; run `sh run.sh make`; ODK handles merge/release |

Record the choice in `docs/build-regime.yaml`. Standalone POD projects
stay the default; ODK is activated only when the project is already ODK-
shaped or the team commits to the full ODK pipeline.

### Step 1: Select OWL 2 Profile

Full OWL 2 is highly expressive but unrestricted reasoning can be costly.
Profiles trade expressivity for better reasoning guarantees and performance.

Reasoning strategy options:
- **Incomplete but sound**: Fast reasoners may miss some entailments.
- **Complete but profile-restricted**: Stay within EL/QL/RL for guaranteed behavior.
- **Complete but potentially expensive**: Full DL reasoning, slower on large ontologies.

| Criterion | Profile | Typical exclusions | Reasoner |
|-----------|---------|--------------------|----------|
| >100K classes, mostly taxonomic | OWL 2 EL | No full negation, universal restrictions, qualified cardinality | ELK |
| OBDA over relational data | OWL 2 QL | Limited class constructors | Ontop-compatible QL tooling |
| Full expressivity needed | OWL 2 DL | None (most expressive decidable profile) | HermiT, Pellet/Openllet |
| Rule-engine style inference | OWL 2 RL | Restricted existential patterns in subclass axioms | Rule engines / RL-compatible reasoners |

Default to OWL 2 DL unless there is a clear scalability or deployment reason
to choose a restricted profile.

#### Construct-Support Matrix (flag non-EL axioms if ELK targeted)

Before encoding any axiom, check it against the construct-support matrix
in [`_shared/owl-profile-playbook.md § 3`](_shared/owl-profile-playbook.md).
Constructs that exceed the declared profile fail silently in some
reasoners — ELK skips qualified cardinality and universals without error.

For every `axiom-plan.yaml` row, stamp the matrix column:

| Axiom pattern | EL | QL | RL | DL |
|---------------|----|----|----|----|
| SubClassOf (simple) | ✓ | ✓ | ✓ | ✓ |
| `some` / existential restriction | ✓ | ✓ | ✓ | ✓ |
| `only` / universal restriction | ✗ | ✗ | ✗ | ✓ |
| `exactly N` / qualified cardinality | ✗ | ✗ | ✗ | ✓ |
| Complement / `not` | ✗ | ✗ | ✗ | ✓ |
| DisjointClasses, DisjointUnion | partial | ✗ | ✓ | ✓ |
| Property chain | partial | ✗ | ✓ | ✓ |
| Inverse property (`inverseOf`) | ✗ | ✓ | ✓ | ✓ |

If your declared profile is EL and the plan carries `✗` rows, you have
two choices: (a) widen the profile + pair with a DL reasoner (HermiT /
Pellet) before release, or (b) refactor the pattern (e.g., universal to
DisjointUnion in EL-safe cases). Escalate as `construct_mismatch` if the
plan can't be reconciled.

### Step 2: Create Ontology Header

Every new ontology needs a Turtle header with metadata:

```turtle
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix prov: <http://www.w3.org/ns/prov#> .

<http://example.org/ontology> a owl:Ontology ;
    owl:versionIRI <http://example.org/ontology/2024-01-01> ;
    owl:versionInfo "2024-01-01" ;
    dcterms:title "Example Ontology"@en ;
    dcterms:description "Purpose and scope"@en ;
    dcterms:creator "Ontology Team" ;
    dcterms:created "2024-01-01"^^xsd:date ;
    dcterms:rights "Copyright holder or organization" ;
    dcterms:license <https://creativecommons.org/licenses/by/4.0/> ;
    prov:wasAttributedTo <https://orcid.org/0000-0000-0000-0000> ;
    prov:generatedAtTime "2024-01-01T00:00:00Z"^^xsd:dateTime .
```

Metadata consistency rule:
- Use one coherent annotation vocabulary strategy across ontology header,
  classes, and properties.
- Required minimum for terms is defined in `_shared/naming-conventions.md`;
  use the same conventions in generated templates and KGCL patches.
- Include PROV-O fields when provenance tracking is required by the project.

### Step 2.5: Import / Declaration Preflight

Before minting any new term, confirm every IRI you will reference is
either (a) already declared in the project, (b) resolvable through an
already-imported module, or (c) added as a new import via the scout's
`imports-manifest.yaml`.

Preflight checks:

```bash
# 1. List every IRI that the axiom plan references
uv run python scripts/axiom_plan_iri_extract.py \
  --plan ontologies/{name}/docs/axiom-plan.yaml \
  > /tmp/referenced-iris.txt

# 2. Resolve each through the merged import closure
robot merge --input ontologies/{name}/{name}.ttl \
  --input ontologies/{name}/imports/*.owl \
  --output /tmp/merged-for-preflight.ttl

# 3. Check every reference exists (via oaklib)
while read iri; do
  uv run runoak -i /tmp/merged-for-preflight.ttl info "$iri" \
    > /dev/null 2>&1 || echo "MISSING: $iri"
done < /tmp/referenced-iris.txt
```

If a reference is MISSING: either add an import row via `ontology-scout`
(`missing_reuse` loopback) or mint a new term within the project
namespace. Do not silently fall through — a silent reference that
doesn't resolve becomes an ERROR at validator Level 0.

### Step 3: Bulk Term Creation via ROBOT Template (or DOSDP)

**Prefer ROBOT templates and DOSDP over freehand OWL.** Templates are
easier to review, round-trip through TSV/YAML, and leave audit rows that
map CQ → pattern → axiom. Freehand `rdflib` or OWLAPY (Step 5) is an
escape hatch for patterns that neither ROBOT templates nor DOSDP
support — use it, but record the rationale in the axiom plan.

For adding >5 terms from the glossary, generate a ROBOT template TSV:

```tsv
ID	LABEL	SC %	DEFINITION	DEFINITION SOURCE
ID	A rdfs:label	SC %	A obo:IAO_0000115	A obo:IAO_0000119
EX:0001	piano	EX:0000	A keyboard instrument that produces sound by striking strings	glossary
EX:0002	violin	EX:0000	A string instrument played with a bow	glossary
```

Execute:

```bash
robot template --template instruments-template.tsv \
  --input ontology.ttl \
  --output ontology.ttl
```

### ROBOT Template Pitfalls

These issues are learned through experience and not well-documented:

- **Column header syntax is fragile**: The second row defines semantics
  (e.g., `SC %`, `A rdfs:label`). A typo or extra space causes silent
  failures, not errors. Double-check headers before running.
- **The `%` placeholder in expressions**: `SC 'has part' some %` must have
  exact quoting and spacing. This is where most template errors occur.
- **Merge vs replace**: `--merge-before` and `--merge-after` control whether
  template output merges with the input or replaces it. Getting this wrong
  can delete your entire ontology. Default behavior is merge.
- **IRI resolution**: Template values must be full IRIs or CURIEs that
  resolve via the ontology's prefix declarations. Undeclared prefixes
  produce blank or invalid output with no error.
- **Multi-value columns**: To put multiple superclasses or annotations on
  one term, use `SPLIT=|` in the column header. Not obvious from docs.
- **Empty cells skip silently**: Empty cells in required columns skip the
  row rather than raising an error. Terms can be partially created (label
  but no definition).
- **Language tags**: Use `A rdfs:label@en` to add a language tag. Without
  it, labels are untagged string literals, causing issues with tools that
  filter by language.

### Step 3.5: ROBOT Template Preflight (mandatory before `robot template`)

Every ROBOT template or DOSDP pattern MUST clear the preflight in
[`_shared/robot-template-preflight.md`](_shared/robot-template-preflight.md)
before `robot template` runs:

| Preflight row | Check |
|----------------|-------|
| Header syntax | Column-definition row parses; no typos in `SC %`, `A rdfs:label`, `EC %`, etc. |
| CURIE resolution | Every CURIE in the template resolves against declared prefixes |
| Required cells | No row in a required column is empty (silent-skip anti-pattern) |
| SPLIT delimiters | Multi-value columns declare `SPLIT=\|` if applicable |
| Language tags | `A rdfs:label@en` where language is required |
| Merge mode | `--merge-before` or `--merge-after` chosen explicitly; default merge is deletion-safe |

Record the preflight results as
`validation/robot-template-preflight/{template-name}.log`. Skipping the
preflight is a safety violation — `robot template` on an unchecked TSV
can silently drop rows or produce blank IRIs.

### Step 4: Individual Changes via KGCL

For single additions, modifications, or reparenting. **Important**: For
changes to shared ontologies, write KGCL commands to a `.kgcl` file and
present for review BEFORE applying (Safety Rule #5).

```bash
# Add a class
uv run runoak -i ontology.ttl apply "create class EX:0001 'piano'"

# Add subclass relationship
uv run runoak -i ontology.ttl apply "create edge EX:0001 rdfs:subClassOf EX:0000"

# Add definition
uv run runoak -i ontology.ttl apply "create definition 'A keyboard instrument that produces sound by striking strings' for EX:0001"

# Rename
uv run runoak -i ontology.ttl apply "rename EX:0001 from 'Old Name' to 'New Name'"

# Batch changes from file
uv run runoak -i ontology.ttl apply --changes-input changes.kgcl
```

### Step 5: Complex Axioms via OWLAPY or rdflib

When ROBOT templates and KGCL cannot express the needed axiom (qualified
cardinality, role chains, nested class expressions).

**Tool choice**: Most OBO community practitioners use **rdflib** for
programmatic OWL work in Python (triple-level manipulation). **OWLAPY**
provides a higher-level OWL API but has a smaller community and requires
a JVM. Use whichever fits your team's stack — examples of both follow.

OWLAPY example:

```python
from owlapy.model import (
    OWLClass, OWLObjectProperty,
    OWLSubClassOfAxiom, OWLObjectSomeValuesFrom,
    OWLObjectAllValuesFrom, OWLObjectIntersectionOf,
)
from owlapy.model import IRI
from owlapy.owlready2 import OWLOntologyManager_Owlready2

manager = OWLOntologyManager_Owlready2()
onto = manager.load_ontology(IRI.create("file:///path/to/ontology.owl"))

# Example: StringInstrument EquivalentTo Instrument and hasComponent some String
instrument = OWLClass(IRI.create("http://ex.org/#Instrument"))
string_cls = OWLClass(IRI.create("http://ex.org/#String"))
has_comp = OWLObjectProperty(IRI.create("http://ex.org/#hasComponent"))

restriction = OWLObjectSomeValuesFrom(has_comp, string_cls)
intersection = OWLObjectIntersectionOf([instrument, restriction])
# ... add as equivalent class axiom

manager.save_ontology(onto, IRI.create("file:///path/to/ontology.owl"))
```

rdflib alternative (no JVM required):

```python
from rdflib import Graph, Namespace, OWL, RDF, RDFS, URIRef, BNode
from rdflib.collection import Collection

g = Graph()
g.parse("ontology.ttl", format="turtle")

EX = Namespace("http://example.org/")

# Add existential restriction: StringInstrument SubClassOf hasComponent some String
restriction = BNode()
g.add((restriction, RDF.type, OWL.Restriction))
g.add((restriction, OWL.onProperty, EX.hasComponent))
g.add((restriction, OWL.someValuesFrom, EX.String))
g.add((EX.StringInstrument, RDFS.subClassOf, restriction))

g.serialize("ontology.ttl", format="turtle")
```

### Step 5.5: Individual Management

Handle individuals as A-box content with explicit module boundaries:

- Reference individuals (for example country codes, fixed enumerations) belong
  in a dedicated reference-individuals module.
- Test individuals belong in a separate test ontology/module.
- Production individuals belong in a knowledge graph dataset, not in the core
  ontology schema file.
- If reference individuals exceed about 50, split into a separate file and
  import it explicitly.

### Step 6: Schema-First via LinkML (for data model schemas)

LinkML excels at defining data schemas that generate multiple artifact types.
Use it when the primary deliverable is a **data model** (JSON Schema, SHACL,
Python dataclasses) rather than a **rich OWL ontology**.

**Best for**: ABox validation schemas, data exchange formats, projects where
domain experts review YAML rather than OWL.

**Not ideal for**: Rich TBox ontologies with complex axioms (qualified
cardinality, role chains, nested class expressions). LinkML-generated OWL
is relatively flat and typically needs enrichment with ROBOT or OWLAPY.

When starting from scratch with a schema-first approach:

```yaml
id: https://example.org/music-ontology
name: music-ontology
prefixes:
  linkml: https://w3id.org/linkml/
  music: https://example.org/music-ontology/

classes:
  Instrument:
    description: A device used to produce music
    attributes:
      name:
        range: string
        required: true
      instrument_family:
        range: InstrumentFamily
```

Generate artifacts:

```bash
uv run gen-owl schema.yaml > ontology.owl
uv run gen-shacl schema.yaml > shapes.ttl
uv run gen-python schema.yaml > models.py
```

### Step 6.5: Generate SHACL Shapes from Property-Design Intent

Every row in `docs/property-design.yaml` with `intent: validate` gets a
SHACL shape. Shapes come from the property-design intent — do not invent
them at release time. Output to `ontologies/{name}/shapes/{name}-shapes.ttl`.

Pattern:

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix : <http://example.org/ontology/> .

:InstrumentShape a sh:NodeShape ;
    sh:targetClass :Instrument ;
    sh:property [
        sh:path :hasIdentifier ;
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "Every Instrument must have exactly one identifier" ;
    ] .
```

Rules:

- Every `intent: validate` row in `property-design.yaml` must have a
  matching `sh:property` entry. Missing coverage is caught by validator
  L3.5.
- `intent: infer` rows do NOT get shapes — they get OWL restrictions
  (Step 3 / Step 5).
- Run `pyshacl --data ontology.ttl --shapes shapes.ttl` before handoff.
  Any violation is either an ontology bug or a shape bug; fix before
  release.

### Step 7: Verify (after structural changes)

Reasoning strategy depends on context:

| Context | Reasoner | Frequency | Time Budget |
|---------|----------|-----------|-------------|
| Active development | ELK | After each batch of changes | Seconds (10K classes) |
| Pre-commit / CI | ELK | Every commit | < 2 minutes |
| Pre-release validation | HermiT or Pellet | Before each release | Minutes to hours |

**Important**: ELK only supports OWL 2 EL. If your ontology uses qualified
cardinality, universal restrictions, or class complements, ELK will silently
ignore those axioms. Run HermiT at least before releases to catch what ELK
misses.

```bash
# Fast classification (ELK — use during development and CI)
robot reason --reasoner ELK --input ontology.ttl --output classified.ttl

# Full DL classification (HermiT — use pre-release)
robot reason --reasoner HermiT --input ontology.ttl --output classified.ttl

# Quality report
robot report --input ontology.ttl --fail-on ERROR --output report.tsv

# SHACL validation (if shapes exist)
uv run pyshacl -s shapes/ontology-shapes.ttl -i rdfs ontology.ttl -f human
```

**Materialization decision**: The ODK default is to include inferred axioms
in the release file (`robot reason --output`). If consumers will reason
independently, ship asserted-only and document this in the release notes.

### Step 7.1: Profile-Specific Reasoner Gate (mandatory before handoff)

Before handoff to `ontology-validator`, the architect MUST show that the
ontology passes all three gates against the merged artifact, in order:

```bash
# merged artifact for all three gates
robot merge --input ontologies/{name}/{name}.ttl \
  --input ontologies/{name}/imports/*.owl \
  --output validation/merged.ttl

# Gate 1: profile validation (per declared OWL profile)
.local/bin/robot validate-profile --profile {EL|QL|RL|DL} \
  --input validation/merged.ttl \
  --output validation/profile-validate.txt

# Gate 2: reasoner classification (pair reasoner to profile)
robot reason --reasoner {ELK|HermiT} \
  --input validation/merged.ttl \
  --output validation/reasoned.ttl \
  --dump-unsatisfiable validation/unsatisfiable.txt

# Gate 3: quality report, fail on ERROR
robot report --input validation/merged.ttl \
  --fail-on ERROR \
  --output validation/robot-report.tsv
```

Reasoner pairing (from `owl-profile-playbook.md`):

| Declared profile | Approved reasoners | Why |
|------------------|---------------------|-----|
| OWL 2 EL | ELK | Fast, profile-complete |
| OWL 2 DL | HermiT, Pellet, Openllet | Full DL closure; catches what ELK silently skips |
| OWL 2 RL | Rule engines, RL-compatible reasoners | Rule-style inference |
| OWL 2 QL | Ontop | OBDA rewriting |

Using an ELK-only gate on a DL ontology is an anti-pattern. If non-EL
axioms exist (per Step 1 construct-support matrix), either widen the
profile or re-run Gate 2 with HermiT before handoff.

### Step 8: Handoff Packaging

Validator handoff is a package, not a file. Produce
`validation/handoff-manifest.yaml`:

```yaml
handoff_id: HOF-2026-04-21-001
artifact_under_test: ontologies/{name}/{name}.ttl
merged_artifact: validation/merged.ttl
declared_profile: OWL-DL
reasoner: HermiT
raw_logs:
  profile_validate: validation/profile-validate.txt
  reasoner_log: validation/reasoner.log
  robot_report: validation/robot-report.tsv
  pyshacl: validation/shacl-results.ttl
  robot_template_preflight:
    - validation/robot-template-preflight/instruments.log
generated_artifacts:
  templates:
    - ontologies/{name}/{name}-template.tsv
  shapes:
    - ontologies/{name}/shapes/{name}-shapes.ttl
  kgcl_patches:
    - ontologies/{name}/{name}-changes.kgcl
  reference_individuals:
    - ontologies/{name}/{name}-reference-individuals.ttl
cq_implementation_matrix: ontologies/{name}/docs/cq-implementation-matrix.csv
```

Rules:

- Raw logs are attached verbatim — the validator (Class D) never paraphrases.
- Every Must-Have CQ appears in `cq-implementation-matrix.csv` with the
  axioms / shapes / tests that implement it.
- Missing package fields block validator ingestion.

## Tool Commands

### ODK Awareness

If the project uses the Ontology Development Kit (ODK), understand these
conventions:

- **Edit file**: Work in `src/ontology/{name}-edit.owl` — never touch
  release artifacts directly
- **Makefile pipeline**: `sh run.sh make` runs the full build (merge,
  reason, report, release) reproducibly via Docker
- **Import management**: `src/ontology/imports/{source}_terms.txt` lists
  imported IRIs; `make refresh-imports` regenerates `*_import.owl` modules
- **DOSDP patterns**: YAML pattern files generate OWL from TSV data — more
  structured than raw ROBOT templates for pattern-based term creation
- **Release**: `make prepare_release` produces multi-format release artifacts

When working in a non-ODK project, the ROBOT commands below apply directly.

### ROBOT operations

```bash
# Merge imports
robot merge --input edit-ontology.ttl --input imports/*.owl --output merged.ttl

# Convert formats
robot convert --input ontology.ttl --output ontology.owl
robot convert --input ontology.ttl --output ontology.json --format json-ld

# Annotate with version
robot annotate --input ontology.ttl \
  --annotation owl:versionInfo "$(date +%Y-%m-%d)" \
  --output ontology.ttl
```

### oaklib operations

```bash
# Search before creating (always!)
uv run runoak -i sqlite:obo:bfo search "material entity"

# Get term info
uv run runoak -i ontology.ttl info EX:0001

# Visualize hierarchy
uv run runoak -i ontology.ttl tree --root EX:0000
```

## Outputs

This skill produces:

| Artifact | Location | Format | Description |
|----------|----------|--------|-------------|
| Main ontology | `ontologies/{name}/{name}.ttl` | Turtle | The formalized OWL 2 ontology |
| SHACL shapes | `ontologies/{name}/shapes/{name}-shapes.ttl` | Turtle | Structural validation shapes |
| ROBOT templates | `ontologies/{name}/{name}-template.tsv` | TSV | Templates used for term creation |
| KGCL patches | `ontologies/{name}/{name}-changes.kgcl` | KGCL | Applied change log |
| Quality report | `ontologies/{name}/{name}-report.tsv` | TSV | Latest ROBOT report |
| Reference individuals (optional) | `ontologies/{name}/{name}-reference-individuals.ttl` | Turtle | A-box reference instances kept separate from schema |

## Handoff

**Receives from**:
- `ontology-conceptualizer` — `ontologies/{name}/docs/glossary.csv`,
  `ontologies/{name}/docs/conceptual-model.yaml`, `ontologies/{name}/docs/bfo-alignment.md`,
  `ontologies/{name}/docs/property-design.yaml`, `ontologies/{name}/docs/axiom-plan.yaml`
- `ontology-requirements` (indirect, via pipeline) — `ontologies/{name}/tests/*.sparql`,
  `ontologies/{name}/tests/cq-test-manifest.yaml` (CQ test suite to forward to validator)

**Passes to**: `ontology-validator` — `ontologies/{name}/{name}.ttl`,
`ontologies/{name}/shapes/{name}-shapes.ttl`, `ontologies/{name}/tests/*.sparql`,
`ontologies/{name}/tests/cq-test-manifest.yaml`

**Handoff checklist**:
- [ ] Ontology passes `robot reason` with zero unsatisfiable classes
- [ ] Ontology passes `robot report` with zero ERRORs
- [ ] All glossary terms are present in the ontology
- [ ] All axiom plan entries have been implemented
- [ ] SHACL shapes exist for core structural constraints

## Anti-Patterns to Avoid

- **Hand-editing Turtle**: Never manually edit `.ttl` files. Use ROBOT,
  oaklib, or Python tools. (Safety Rule #1)
- **Skipping the reasoner**: Always run `robot reason` after structural
  changes. (Safety Rule #2)
- **Deleting terms**: Never delete — deprecate with `owl:deprecated true`.
  (Safety Rule #4)
- **Over-engineering tools**: Don't use OWLAPY for simple SubClassOf. Use
  ROBOT template or KGCL instead. (See tool decision tree)
- **Missing metadata**: Every class needs `rdfs:label` and `skos:definition`
  at minimum.
- **Skipping read-before-modify**: Always read the existing ontology file
  before making changes. (Safety Rule #9)
- **No backup before bulk**: Create a checkpoint before running ROBOT
  template or batch KGCL application. (Safety Rule #10)

## Error Handling

| Error | Likely Cause | Recovery |
|-------|-------------|----------|
| Reasoner reports INCONSISTENT | Conflicting axioms (often disjointness + subclass) | Parse explanation, identify conflicting axioms, propose minimal fix |
| Unsatisfiable classes found | Over-constrained class (contradictory restrictions) | List unsatisfiable classes, trace disjointness axioms |
| ROBOT template fails | Column headers don't match expected format | Check ROBOT template documentation for column syntax |
| KGCL apply fails | Term not found or invalid KGCL syntax | Verify term exists with `runoak info`; check KGCL grammar |
| OWLAPY JVM bridge error | Java not installed or JVM not found | Ensure JDK is installed and JAVA_HOME is set |

## Progress Criteria

Work is done when every box is checked. All gates are mandatory before handoff.

- [ ] `.local/bin/robot validate-profile --profile {EL|QL|RL|DL}` passes on
      the merged ontology — see [`_shared/owl-profile-playbook.md § 5`](_shared/owl-profile-playbook.md).
- [ ] `.local/bin/robot reason --reasoner {ELK|HermiT}` passes; reasoner choice
      matches declared profile + construct-support matrix.
- [ ] `.local/bin/robot report --fail-on ERROR` passes on the merged ontology.
- [ ] `pyshacl` passes for every shape graph drafted from property-design intent.
- [ ] ROBOT / DOSDP templates cleared the preflight in
      [`_shared/robot-template-preflight.md`](_shared/robot-template-preflight.md).
- [ ] `cq-implementation-matrix.csv` maps every Must-Have CQ to implemented
      axioms / shapes / tests.
- [ ] Every ODP instantiation cites the row in [`_shared/pattern-catalog.md § 2`](_shared/pattern-catalog.md).
- [ ] No Loopback Trigger below fires.

## LLM Verification Required

See [`_shared/llm-verification-patterns.md`](_shared/llm-verification-patterns.md).
Every LLM-drafted artifact is Class A (tool-gated). No exceptions.

| Operation | Class | Tool gate |
|---|---|---|
| OWL axiom draft | A | `robot validate-profile` → `robot reason` → `robot report` |
| ROBOT / DOSDP template row | A | Preflight checks per [`_shared/robot-template-preflight.md`](_shared/robot-template-preflight.md) + `robot template` exit 0 |
| KGCL patch | A | `kgcl-apply` round-trip; `robot diff` confirms intended change only |
| SHACL shape draft | A | `pyshacl --data ontology.ttl --shapes shapes.ttl` exit 0 |

## Loopback Triggers

| Trigger | Route to | Reason |
|---|---|---|
| Incoming: `profile_violation` | `ontology-architect` | Axiom-level issue; fix pattern or widen profile in scope doc. |
| Incoming: `unsatisfiable_class` | `ontology-architect` | Axiom-level conflict; trace disjointness + restrictions. |
| Incoming: `construct_mismatch` | `ontology-architect` | Reasoner choice wrong for construct; switch to HermiT or drop construct. |
| Incoming: `robot_template_error` | `ontology-architect` | Preflight the template, fix the offending row. |
| Raised: axiom plan calls for a term not in conceptual model | `ontology-conceptualizer` | Conceptual model must be updated first; do not mint silently. |
| Raised: no reusable term found for a needed concept | `ontology-scout` | Rescout before minting; architect does not search registries. |

Depth > 3 escalates per [`_shared/iteration-loopbacks.md`](_shared/iteration-loopbacks.md).

## Worked Examples

- [`_shared/worked-examples/ensemble/architect.md`](_shared/worked-examples/ensemble/architect.md) — `StringQuartet hasMember exactly 4 Musician`: ELK silently skips qualified cardinality, HermiT catches; DOSDP for instrument-family. *(Wave 4)*
- [`_shared/worked-examples/microgrid/architect.md`](_shared/worked-examples/microgrid/architect.md) — `hasPart ∘ locatedIn → locatedIn` stays EL-safe; SHACL for telemetry-packet structure; equivalence-bridge failure. *(Wave 4)*
