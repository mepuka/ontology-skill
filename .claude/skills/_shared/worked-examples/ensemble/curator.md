# Ensemble — `ontology-curator` walkthrough

Walks [`ontology-curator`](../../../ontology-curator/SKILL.md) Steps 0–7
for a concrete deprecation: the experimental role class
`:StringPlayerSoloRole` is being retired in favor of
`:StringPlayerRole` + `:SoloistRole`. Goal: produce a signed
`change-approval.yaml`, apply the KGCL patch under review, bump version,
and write consumer release notes with migration guidance.

## Step 0 — change intake (`docs/change-log/2026-04-22-004.md`)

```yaml
change_id: CHG-2026-04-22-004
category: structural          # reparent + deprecate — not purely annotation
triggered_by: "Architect Step 3 revealed StringPlayerSoloRole composes role + role — redundant"
downstream_skills: [architect, validator]
severity: MINOR               # deprecation, not deletion
```

## Step 1 — classification

| Action | KGCL command | Severity |
|---|---|---|
| Deprecate `:StringPlayerSoloRole` | `obsolete` | MINOR |
| Add replacement pointer | `create edge … obo:IAO_0100001 …` | PATCH |
| Reparent one subclass `:LeadViolinRole` from deprecated to `:SoloistRole` | `move` | MINOR |

Combined release bump: **MINOR**.

## Step 1.5 — impact analysis (`docs/change-impact/CHG-2026-04-22-004.md`)

```yaml
change_id: CHG-2026-04-22-004
affected_cqs: [CQ-E-002]            # uses bearer/role pattern
affected_mappings:
  - file: mappings/ensemble-to-mimo.sssom.tsv
    rows: [3]                        # ens:Violinist ↔ mimo:Perf011 (Class B reviewed; unaffected)
affected_consumers:
  - "test fixtures at tests/fixtures/cq-e-002.ttl (one instance uses StringPlayerSoloRole)"
risk_summary: |
  Low risk. Replacement pointer preserves reasoning; mapping row stays valid.
  CQ-E-002 SPARQL references the parent `bfo:Role`, not the deprecated leaf.
```

## Step 2 + 3 — KGCL patch (`changes/ensemble-changes.kgcl`)

```kgcl
# changes.kgcl — Proposed changes for review
# CHG-2026-04-22-004
# Author: koko
# Reason: StringPlayerSoloRole conflates String player role + Soloist role

obsolete ens:StringPlayerSoloRole
create synonym 'OBSOLETE StringPlayerSoloRole' for ens:StringPlayerSoloRole
create edge ens:StringPlayerSoloRole obo:IAO_0100001 ens:SoloistRole
create annotation ens:StringPlayerSoloRole obo:IAO_0000231 "term merged into SoloistRole+StringPlayerRole"

move ens:LeadViolinRole from ens:StringPlayerSoloRole to ens:SoloistRole
```

Dry-run:
```
$ uv run runoak -i ontologies/ensemble/ensemble.ttl apply-changes --dry-run \
    --changes-input changes/ensemble-changes.kgcl
  → 4 changes would apply; 0 errors
```

## Step 3.5 — approval (`docs/change-approval.yaml`)

```yaml
change_id: CHG-2026-04-22-004
reviewer: "coordinator@ensemble.example"
reviewed_at: "2026-04-22"
approved_patch_sha: "sha256:7f8c…"    # hash of ensemble-changes.kgcl
approved_impact_file: "docs/change-impact/CHG-2026-04-22-004.md"
notes: "Deprecation preserves classifications; migration is one-line for known consumer."
```

Without this file the Step 4 apply is blocked per Safety Rule #5.

## Step 4 — apply

```
$ uv run runoak -i ontologies/ensemble/ensemble.ttl apply-changes \
    --changes-input changes/ensemble-changes.kgcl \
    --output ontologies/ensemble/ensemble.ttl
  → applied 4 changes
```

Deprecation triple set in Turtle:

```ttl
ens:StringPlayerSoloRole owl:deprecated true ;
    obo:IAO_0000231 "term merged into SoloistRole+StringPlayerRole" ;
    obo:IAO_0100001 ens:SoloistRole .
```

## Step 5 — version update

```ttl
<http://example.org/ensemble> a owl:Ontology ;
    owl:versionIRI <http://example.org/ensemble/2026-04-22> ;
    owl:versionInfo "2026-04-22" ;
    owl:priorVersion <http://example.org/ensemble/2026-03-15> .
```

MINOR bump under OBO date-based scheme (ensemble project uses date
versioning per `docs/scope.md § Versioning`).

## Step 5.5 — FAIR assessment (`release/ensemble-fair.md`)

| Principle | Outcome |
|---|---|
| F1 stable IRIs | PASS — versionIRI + versioned PURL both resolve |
| I2 FAIR vocabularies | PASS — dcterms + skos + PROV present on header |
| R1.2 release provenance | PASS — `prov:wasDerivedFrom` points to prior version |

## Step 5.6 — publication metadata check (`release/2026-04-22-publication-check.yaml`)

```yaml
- versionIRI_resolves: true
- PURL_to_versioned_IRI: true          # purl.org/ensemble/2026-04-22 → artifact
- content_negotiation: {ttl: ok, rdfxml: ok, jsonld: ok}
- license_resolves: true                # CC-BY-SA-4.0
- registry: "not applicable (internal monorepo ontology)"
- artifact_sha_match: true
```

## Step 6 + 6.5 — diff + consumer release notes (`release/notes/2026-04-22.md`)

`robot diff` excerpt:

```
- ens:StringPlayerSoloRole rdfs:subClassOf bfo:Role
+ ens:StringPlayerSoloRole owl:deprecated true
+ ens:StringPlayerSoloRole obo:IAO_0100001 ens:SoloistRole
- ens:LeadViolinRole rdfs:subClassOf ens:StringPlayerSoloRole
+ ens:LeadViolinRole rdfs:subClassOf ens:SoloistRole
```

Consumer notes:

```markdown
# Ensemble ontology 2026-04-22

## Breaking changes
- Deprecated `ens:StringPlayerSoloRole`. Replaced by `ens:SoloistRole`
  (primary) with bearers optionally also bearing `ens:StringPlayerRole`.
  **Migration:** any consumer asserting `a ens:StringPlayerSoloRole` must
  split the assertion into two role-bearing triples.
  ```sparql
  # before
  ?bearer ens:bearerOf ?r . ?r a ens:StringPlayerSoloRole .
  # after
  ?bearer ens:bearerOf ?r1 . ?r1 a ens:SoloistRole .
  ?bearer ens:bearerOf ?r2 . ?r2 a ens:StringPlayerRole .
  ```
  Source: [CHG-2026-04-22-004](../../docs/change-log/2026-04-22-004.md)

## Additions
- (none this release)

## Internal refactors
- `ens:LeadViolinRole` reparented to `ens:SoloistRole`.
```

## Step 7 — revalidate

Hand off back to `ontology-validator` (Level 0 + Level 1 + Level 4 CQ
regression). CQ-E-002 must still pass; reasoner must still classify
roles correctly.

## Pitfall callout — deprecate-not-delete

A draft PR from a contributor had `delete ens:StringPlayerSoloRole` in
the patch. This violates Safety Rule #4 (never delete; always
deprecate). The Step 1 classification rejects `delete` — the canonical
command is `obsolete`, which preserves downstream queries and provides
the replacement pointer. The deprecated class remains terminal (no new
subclass edges accepted), per workspace memory
`feedback_deprecated_classes_are_terminal`.

## Handoff

`ontology-validator` full regression → user ack → release artifact
ships via Step 5.6 check. On CQ regression, route back to architect
(axiom) or requirements (CQ wording).
