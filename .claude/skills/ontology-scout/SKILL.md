---
name: ontology-scout
description: >
  Searches, finds, evaluates, and imports reusable ontological resources
  before new term creation. Queries OLS, BioPortal, OBO Foundry, LOV,
  schema.org, and domain registries; checks term existence, license,
  maintenance cadence, BFO/RO fit; picks an import strategy
  (MIREOT/STAR/BOT/TOP) and extracts ontology modules via ROBOT;
  recommends applicable Ontology Design Patterns (ODP) / DOSDP patterns.
  Use when looking for existing ontologies to reuse or align with, for
  import planning, upstream term checks, ODP selection, or
  import-refresh triage.
---

# Ontology Scout (Reuse Advisor)

## Role Statement

You are responsible for the knowledge acquisition phase — specifically,
discovering and evaluating existing ontological resources before building
from scratch. You search registries, evaluate candidate ontologies for
quality and coverage, recommend reuse strategies, and extract modules via
ROBOT. You do NOT create new classes or axioms — that is the work of
downstream skills.

## When to Activate

- User wants to find existing ontologies covering their domain
- User mentions "reuse", "import", "alignment", or "existing ontology"
- Starting conceptualization (always check what exists first)
- Pipeline A Step 2 or Pipeline B Step 1

## Shared Reference Materials

Read these files from `_shared/` before beginning work:

- `_shared/methodology-backbone.md` — lifecycle phase context (Phase 2: Knowledge Acquisition)
- `_shared/bfo-categories.md` — needed to evaluate BFO alignment of candidates
- `_shared/naming-conventions.md` — to assess naming quality of candidates
- `_shared/namespaces.json` — standard prefixes for search queries
- `_shared/odk-and-imports.md` — ODK vs standalone-POD choice; MIREOT/STAR/BOT/TOP extraction methods; imports-manifest.yaml schema and refresh cadence
- `_shared/owl-profile-playbook.md` — profile constraints inform import-size and term-selection trade-offs
- `_shared/iteration-loopbacks.md` — raises `missing_reuse`, `bad_module`, `import_provenance` loopbacks back to scout
- `_shared/llm-verification-patterns.md` — when reuse recommendations and ODP picks require LLM-verified evidence
- `_shared/modularization-and-bridges.md` — when to split, when to merge, import vs. bridge vs. copy decision tree (complements the MIREOT/STAR mechanics in `odk-and-imports.md`)

## Core Workflow

### Step 0: Tool / Source Availability Check

Before searching, confirm which sources are reachable. Registry outages are
common; reuse analysis done against a stale or unreachable registry must be
declared, not silently degraded.

| Source | How to probe | Fallback when down |
|--------|--------------|--------------------|
| OLS | `runoak -i ols: search` (one cheap term) | Local SQLite OBO cache (`sqlite:obo:{id}`) |
| BioPortal | `runoak -i bioportal: search` (requires API key) | Cached mirror or skip — document skip |
| OBO Foundry | `runoak -i obo: ontologies` | Local OBO cache |
| LOV / schema.org | `curl` a canonical IRI | Snapshot in `imports/` if previously fetched |
| Domain registries (OEO, MIMO, etc.) | canonical endpoints | Pinned local copy |

Record each source queried, access timestamp, and status
(`up` / `cached` / `unavailable`) in the reuse report header. A reuse report
with no source-freshness record is incomplete.

### Always-Reuse Baseline

Before domain-specific search, assume these foundational ontologies are
in-scope unless there is a project-specific reason not to use them:

- **Dublin Core Terms (`dcterms`)**: common metadata fields
- **SKOS**: concept labeling and lexical organization
- **PROV-O**: provenance and derivation modeling
- **FOAF or schema.org**: people/organization basics

Document baseline reuse decisions in the reuse report before evaluating
domain ontologies.

### Step 1: Search Registries

For each candidate term from the pre-glossary, search multiple registries:

```bash
# Search via oaklib (OLS backend)
uv run runoak -i ols: search "TERM"

# Search via oaklib (BioPortal backend, if API key configured)
uv run runoak -i bioportal: search "TERM"

# Search OBO Foundry ontologies specifically
uv run runoak -i sqlite:obo:{ontology_id} search "TERM"
```

Also check specialized repositories when relevant:
- OMG specifications catalog
- COLORE repository
- Schema.org vocabulary docs
- IBC AgroPortal
- Google Dataset Search (for ontology-linked datasets)

### Step 2: Evaluate Candidates (Reuse-Decision Matrix)

Every candidate is scored on six decision dimensions. Each dimension is
recorded with evidence in `docs/reuse-report.md` as a row per candidate.

| Dimension | What to assess | How to measure |
|-----------|----------------|----------------|
| Scope fit (coverage) | Does the candidate cover the pre-glossary terms you need? | % of pre-glossary matched; CQ-probe answer rate from Step 3 |
| License | Is the license compatible with the project license? | `dcterms:license` header + project policy; blocking if incompatible |
| Maintenance | Is it actively maintained? | Last-release date, issue cadence, publication trail |
| Import size | What footprint does reuse drag in? | Triple count, transitive-import count, class count after `robot extract` |
| Identifier policy | Stable IRIs? Deprecation policy? Version IRIs? | Check `owl:versionIRI`, PURL stability, `obo:IAO_0100001` use on obsoletes |
| Profile implications | Does it push the project off its target OWL profile? | `robot validate-profile` on a merged sample; watch non-EL axioms if ELK-targeted |

Run the quality / consistency / metadata checks alongside the matrix — they
surface issues that populate the matrix rows:

- `robot validate --input candidate.owl` (syntactic correctness)
- `robot reason --reasoner ELK --input candidate.owl` (logical consistency)
- `robot report --input candidate.owl` (quality + metadata)
- `runoak -i candidate.owl statistics` (label / definition coverage)
- BFO / RO alignment: does it subclass BFO and use RO relations?

**Rejection rationale is mandatory.** Every candidate that is not selected
MUST have a written rejection rationale row in the matrix. Silent exclusion
is an anti-pattern (see anti-patterns below). Even rejected candidates may
serve as benchmark references — record why and keep the link.

### Step 3: Reuse Decision

Apply the NeOn reuse decision tree:

| Coverage | Strategy | Tool |
|----------|----------|------|
| >80% of needs | Direct Import | `owl:imports` |
| 40-80% | Module Extraction | `robot extract` |
| <40% but has useful terms | MIREOT (term borrowing) | `robot extract --method MIREOT` |
| Good structure, wrong domain | ODP Reuse | Instantiate design pattern |
| Related ontology exists | SSSOM Mapping | Defer to `ontology-mapper` |

#### CQ Benchmark Probe

Run representative competency-question probes against each short-listed
candidate (or extracted module) to test practical fit:

- Select 3-5 high-priority CQs from requirements.
- Draft quick probe queries (or adapt existing CQ drafts).
- Record whether the candidate can answer each probe fully, partially, or not
  at all.

### Step 3.5: Module vs Import vs Bridge

Before extracting, decide the reuse shape for each selected candidate.
Consult [`_shared/modularization-and-bridges.md § 6`](_shared/modularization-and-bridges.md)
for the full decision tree. Record the choice per candidate in the reuse
report:

| Reuse shape | When to pick it | Downstream skill impact |
|-------------|-----------------|-------------------------|
| Full import (`owl:imports`) | Candidate is cohesive, small-to-moderate, and aligned with the target profile | Architect imports IRI; curator tracks upstream version |
| Module extraction | Candidate covers needed terms but the full footprint violates scope / profile / size | Architect imports the extracted module; manifest records extraction method |
| Bridge ontology | Two ontologies must stay separate but need equivalence / subclass links | Hand off to `ontology-mapper` for SSSOM bridge authoring |
| Copy (last resort) | Upstream is unmaintained / license-blocked, terms are copied with attribution | Curator owns maintenance; record why import was rejected |

A recorded decision is mandatory. "Full import" without justification is
treated the same as silent exclusion — it fails the Progress Criteria.

### Step 4: Module Extraction

#### Extraction Method Trade-offs

| Method | What It Extracts | Best For | Watch Out |
|--------|-----------------|----------|-----------|
| MIREOT | Term + ancestors only | Large ontologies (GO, ChEBI) — fast, minimal | Loses sibling context and some axioms |
| STAR | All axioms involving the term | Small/medium ontologies — most complete | Can pull in unexpected classes via axiom references |
| BOT | Term + all ancestors (bottom module) | Good middle ground | May include more than needed for deep hierarchies |
| TOP | Term + all descendants (top module) | Extracting a subtree | Large result if term has many descendants |

**Import management pitfalls**:
- **Transitive import chains**: Importing one OBO ontology can pull in dozens
  of transitive imports. Check what you are actually loading.
- **Import freshness**: Upstream ontologies release on their own schedule. Pin
  versions and use a refresh workflow (see curator skill).
- **Circular imports**: Occasionally A imports B imports C imports A. This
  causes reasoner failures. Check for cycles before committing.
- **Stale term files**: The `*_terms.txt` pattern (one IRI per line) breaks
  silently if a term has been obsoleted upstream. Validate term existence
  during import refresh.

For recommended imports:

```bash
# Create term list file
echo "http://purl.obolibrary.org/obo/GO_0008150" > imports/go_terms.txt
echo "http://purl.obolibrary.org/obo/GO_0003674" >> imports/go_terms.txt

# Extract module (STAR method — most complete)
robot extract --method STAR \
  --input-iri http://purl.obolibrary.org/obo/go.owl \
  --term-file imports/go_terms.txt \
  --output imports/go_import.owl

# Extract module (MIREOT — minimal, just term + parents)
robot extract --method MIREOT \
  --input-iri http://purl.obolibrary.org/obo/go.owl \
  --term-file imports/go_terms.txt \
  --output imports/go_import.owl
```

### Step 5: ODP / DOSDP Selection

Map each CQ onto an Ontology Design Pattern (ODP) or DOSDP pattern. Pattern
name-dropping is not a recommendation — each pick needs an instantiation
template with variable bindings, an example row, and the downstream axiom
pattern it will implement.

For each recommended pattern, record:

| Field | Content |
|-------|---------|
| `source` | Catalog row: [`_shared/pattern-catalog.md § 2`](_shared/pattern-catalog.md) or external DOSDP URL |
| `pattern_name` | `value-partition`, `part-whole`, `role`, `participation`, `n-ary-relation`, `information-realization`, etc. |
| `applicable_cqs` | CQ IDs that this pattern serves |
| `variables` | Named variables with types (e.g. `{Whole: owl:Class, Part: owl:Class}`) |
| `example_instantiation` | One concrete binding (e.g. `Whole: :Orchestra, Part: :Musician`) |
| `downstream_axiom_pattern` | Which axiom pattern from [`_shared/axiom-patterns.md`](_shared/axiom-patterns.md) the architect will use |
| `tool_template` | DOSDP YAML file path if available, else "freehand OWL" |

Output to `docs/odp-recommendations.md`. Patterns without all fields fail
Progress Criteria.

### Step 6: Import Manifest Update

Every selected candidate and module extraction updates
`docs/imports-manifest.yaml` per
[`_shared/odk-and-imports.md`](_shared/odk-and-imports.md):

```yaml
imports:
  - source_iri: http://purl.obolibrary.org/obo/ro.owl
    pinned_version: 2024-04-24
    extraction_method: STAR          # full_import | STAR | MIREOT | BOT | TOP | bridge | copy
    term_file: imports/ro_terms.txt
    license: CC0-1.0
    refresh_policy: quarterly        # manual | monthly | quarterly | on_upstream_release
    source_freshness: "2026-04-21 up"  # from Step 0
    rejection_rationale: null        # populated only for rejected candidates
  - source_iri: http://example.org/weak-music-vocab.owl
    pinned_version: 2019-07-01
    extraction_method: rejected
    rejection_rationale: "Unmaintained since 2019; license ND; no BFO alignment"
```

The curator's refresh workflow reads this manifest. A scout report without a
manifest update — or a manifest row missing `pinned_version` — fails the
Progress Criteria.

## Tool Commands

### Registry search

```bash
# OLS search with result limit
uv run runoak -i ols: search "musical instrument" -l 20

# Get term details from a specific ontology
uv run runoak -i sqlite:obo:go info GO:0008150

# Get ancestors of a term
uv run runoak -i sqlite:obo:go ancestors GO:0008150

# Check if ontology is in OBO Foundry
uv run runoak -i obo: ontologies
```

### ROBOT extraction

```bash
# BOT extraction (bottom module — term + all ancestors)
robot extract --method BOT \
  --input source.owl \
  --term "http://example.org/Term" \
  --output module.owl

# TOP extraction (top module — term + all descendants)
robot extract --method TOP \
  --input source.owl \
  --term "http://example.org/Term" \
  --output module.owl
```

### Quality assessment of candidate

```bash
# Syntax validation
robot validate --input candidate.owl

# Logical consistency
robot reason --reasoner ELK --input candidate.owl

# Run ROBOT report on candidate ontology
robot report --input candidate.owl --output candidate-report.tsv

# Check label coverage
uv run runoak -i candidate.owl statistics

# Run representative CQ probes (if available)
robot verify --input candidate.owl --queries ontologies/{name}/tests/candidate-probes/
```

## Outputs

This skill produces:

| Artifact | Location | Format | Description |
|----------|----------|--------|-------------|
| Reuse report | `ontologies/{name}/docs/reuse-report.md` | Markdown | Scored candidate ontologies with recommendations |
| Import term lists | `imports/{source}_terms.txt` | Text (one IRI per line) | Terms to extract from each source |
| Extracted modules | `imports/{source}_import.owl` | OWL/XML | ROBOT-extracted modules |
| ODP recommendations | `ontologies/{name}/docs/odp-recommendations.md` | Markdown | Applicable design patterns with instantiation guidance |

## Handoff

**Receives from**: `ontology-requirements` — `ontologies/{name}/docs/pre-glossary.csv`, `ontologies/{name}/docs/scope.md`

**Passes to**:
- `ontology-conceptualizer` — reuse report, import term lists, ODP recommendations
- `ontology-mapper` (Pipeline B) — target ontology identifiers, reuse recommendations

**Handoff checklist**:
- [ ] Every pre-glossary term has been searched in at least one registry
- [ ] Reuse report includes scored candidates with clear recommendations
- [ ] Extracted modules load without errors (`robot validate`)
- [ ] ODP recommendations reference specific pattern templates

## Anti-Patterns to Avoid

- **Not-invented-here syndrome**: Always search before creating new terms.
  Reuse is preferred over reinvention.
- **Uncritical reuse**: Don't import entire large ontologies (e.g., all of
  GO) when only a handful of terms are needed. Use module extraction.
- **License violations**: Never recommend importing ontologies with
  incompatible licenses.
- **Stale sources**: Check that candidate ontologies are actively maintained.
  An unmaintained ontology is a liability.

## Error Handling

| Error | Likely Cause | Recovery |
|-------|-------------|----------|
| OLS API unreachable | Network issue or rate limit | Retry with backoff; fall back to local SQLite cache |
| ROBOT extract fails | Invalid IRI or unreachable source | Download ontology locally first, then extract |
| No candidates found | Domain is niche or uses non-standard terminology | Broaden search terms; try synonyms from pre-glossary |
| Candidate has no license | License not declared in metadata | Contact maintainers or choose alternatives |

## Progress Criteria

Work is done when every box is checked. Each item is tool-verifiable.

- [ ] `docs/reuse-report.md` lists every registry searched with access date + status.
- [ ] Every recommended external term has IRI, label, source ontology version, license.
- [ ] `docs/imports-manifest.yaml` updated per [`_shared/odk-and-imports.md`](_shared/odk-and-imports.md)
      (source, version, extraction method, term file, refresh policy).
- [ ] Each rejected candidate has a written rejection rationale (not silent exclusion).
- [ ] Import-vs-bridge-vs-copy decision recorded per
      [`_shared/modularization-and-bridges.md § 6`](_shared/modularization-and-bridges.md).
- [ ] ODP recommendations cite an instantiation template from
      [`_shared/pattern-catalog.md`](_shared/pattern-catalog.md) *or* an
      external DOSDP source.
- [ ] No Loopback Trigger below fires.

## LLM Verification Required

See [`_shared/llm-verification-patterns.md`](_shared/llm-verification-patterns.md).
Never replaces `runoak info`, license metadata check, or `robot extract`.

| Operation | Class | Tool gate |
|---|---|---|
| Reuse-candidate ranking | B | Evidence = label, definition, parents, license; explicit decision + rationale |
| ODP applicability picks | B | Cite pattern source + variable binding table |
| Candidate CQ-probe interpretation | B | Attach raw query output; never paraphrase |
| Import-vs-bridge decision | B | Cite the § 6 decision-tree branch; bridge choice triggers mapper loopback |

## Loopback Triggers

| Trigger | Route to | Reason |
|---|---|---|
| Incoming: `missing_reuse` (from conceptualizer / architect) | `ontology-scout` | A new term was minted when a reusable existed; rescout before proceeding. |
| Incoming: `bad_module` (from architect / validator) | `ontology-scout` | Module extraction method was wrong; re-extract with correct MIREOT/STAR/BOT. |
| Incoming: `import_provenance` (from curator) | `ontology-scout` | Manifest row missing or stale; regenerate the row before curator continues. |
| Raised: cross-domain `skos:exactMatch` candidate surfaces in reuse | `ontology-mapper` | Mapping work belongs to mapper, not scout. |

Depth > 3 escalates per [`_shared/iteration-loopbacks.md`](_shared/iteration-loopbacks.md).

## Worked Examples

- [`_shared/worked-examples/ensemble/scout.md`](_shared/worked-examples/ensemble/scout.md) — MIMO reuse: MIREOT vs. full-import choice; rejecting a weak music vocabulary on license. *(Wave 4)*
- [`_shared/worked-examples/microgrid/scout.md`](_shared/worked-examples/microgrid/scout.md) — OEO import vs. schema.org bridge; manifest row for a pinned OEO version. *(Wave 4)*
