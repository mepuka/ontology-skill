# Provenance and Publication

**Referenced by:** `ontology-curator` (Step 5.5 FAIR + Step 5.6 publication
metadata check), `ontology-validator` (release-gate artifact classification).
**Related:** [`odk-and-imports.md`](odk-and-imports.md) (upstream import
provenance), [`sssom-semapv-recipes.md`](sssom-semapv-recipes.md) (mapping
provenance).

Publishing an ontology is more than copying a file to a URL. Consumers
need stable identifiers, content-negotiation plumbing, registry entries,
and a provenance trail from source → release. This file collects the
operational patterns for each and defines the publication-check rows the
curator must fill before a release ships.

## 1. Identifier strategy

### 1.1 Ontology IRI + versionIRI

Every ontology has:

- A **canonical IRI** (the un-versioned form) that always resolves to
  the current release: `https://w3id.org/ensemble`.
- A **version IRI** naming a specific frozen release:
  `https://w3id.org/ensemble/2026-04-22`.

Authors SHOULD declare the unversioned IRI as the ontology IRI and stamp
every release with a `owl:versionIRI`:

```ttl
<https://w3id.org/ensemble> a owl:Ontology ;
    owl:versionIRI <https://w3id.org/ensemble/2026-04-22> ;
    owl:versionInfo "2026-04-22" ;
    owl:priorVersion <https://w3id.org/ensemble/2026-03-15> ;
    dcterms:license <https://creativecommons.org/licenses/by/4.0/> ;
    prov:wasDerivedFrom <http://purl.obolibrary.org/obo/bfo/2020/bfo.owl> .
```

See [`odk-and-imports.md § 3`](odk-and-imports.md) for the
`imports-manifest.yaml` fields that pin upstream provenance; every
upstream version that shaped this release appears via
`prov:wasDerivedFrom`.

### 1.2 Term IRI policy

Term IRIs are immutable once published. A release NEVER rewrites a
previously-shipped term IRI. Deprecation is the only exit path per
`ontology-curator` Step 2 (`obsolete` with `obo:IAO_0100001`
replacement pointer). This is also recorded in workspace memory
`feedback_deprecated_classes_are_terminal`.

### 1.3 Namespace choice

| Namespace | When | Stability |
|---|---|---|
| `w3id.org/{name}` | General-purpose projects | Community-hosted; high durability |
| `purl.obolibrary.org/obo/{NAME}_` | OBO-aligned ontologies | Requires OBO Foundry registration |
| Custom domain | Project-specific under org control | Only as durable as the DNS + HTTPS renewal |

Favor `w3id.org` or `purl.obolibrary.org` for public ontologies. A
custom domain with a 1-year-expiry TLS cert is not a stable IRI base.

## 2. Content negotiation

Clients ask for different serializations via the HTTP `Accept` header.
The publishing host must redirect `versionIRI` → artifact per MIME.

| Accept | Artifact | Why |
|---|---|---|
| `text/turtle` | `{version}.ttl` | Default for humans + ROBOT |
| `application/rdf+xml` | `{version}.owl` | Legacy tooling, Protégé default |
| `application/ld+json` | `{version}.jsonld` | JSON-tooling consumers |
| `text/html` | WIDOCO / Pylode HTML docs | Human landing page |

Example Apache redirect for `w3id.org/ensemble`:

```apache
# /etc/apache2/sites-enabled/ensemble.conf
RewriteEngine On
RewriteCond %{HTTP_ACCEPT} text/turtle
RewriteRule ^/ensemble/(.*)$ https://raw.githubusercontent.com/.../ensemble/$1.ttl [R=303,L]
RewriteCond %{HTTP_ACCEPT} application/rdf\+xml
RewriteRule ^/ensemble/(.*)$ https://raw.githubusercontent.com/.../ensemble/$1.owl [R=303,L]
RewriteCond %{HTTP_ACCEPT} application/ld\+json
RewriteRule ^/ensemble/(.*)$ https://raw.githubusercontent.com/.../ensemble/$1.jsonld [R=303,L]
# default → HTML docs
RewriteRule ^/ensemble/(.*)$ https://example.org/docs/ensemble/$1.html [R=303,L]
```

303-See-Other is the correct status for dereferenceable ontology IRIs
(W3C Cool URIs note). `robot convert` produces `.ttl`, `.owl`, and
`.jsonld` from a single edit file; pylode / widoco produce the HTML.

## 3. PURL + w3id.org management

`w3id.org` is a redirect-only service; configuration lives in a
per-namespace `.htaccess` committed to the `perma-id/w3id.org`
repository. Pull request the redirect rules there for every new
ontology:

```
# /ensemble/.htaccess (in perma-id/w3id.org)
RewriteEngine On
RewriteRule ^$                https://example.org/docs/ensemble/index.html [R=303,L]
RewriteCond %{HTTP_ACCEPT} text/turtle
RewriteRule ^(.*)$            https://raw.githubusercontent.com/org/ensemble/$1.ttl [R=303,L]
# ...
```

`purl.obolibrary.org` entries are controlled by the OBO PURL config
repo (github.com/OBOFoundry/purl.obolibrary.org). Submit a pull
request for each new ontology / version. Content negotiation is
handled centrally.

## 4. Registry entries

Registering ontologies widens discoverability and anchors the release
under a community-maintained index.

| Registry | Who benefits | Entry requirements | Fallback if unregistered |
|---|---|---|---|
| **OBO Foundry** | OBO-aligned biomedical / life-science ontologies | BFO-aligned, CC-BY license, English term labels, clear scope | Use `w3id.org` PURL and register with community indexes (e.g., LOV). |
| **BioPortal** | Biomedical ontologies + mappings | Upload release, set metadata, assign category | Link from project README. |
| **OLS (EBI)** | General-purpose ontology browsing | OBO Foundry alignment, public URL, metadata annotations | OLS4 accepts submissions from non-OBO projects with a flag. |
| **LOV** (Linked Open Vocabularies) | RDF/OWL general-purpose vocabularies | Stable IRI, dereferenceable, license declared | Link from project README. |
| **AgroPortal / EcoPortal** | Agricultural / environmental ontologies | Domain fit; CC-BY compatible | Link from project README. |

Registry submission is a one-time setup per ontology, but **each
release needs re-indexing**. Most registries poll the `versionIRI`
monthly; if your release moved within that cadence, the registry entry
silently lags. Record the registry's last-seen version in
`release/notes/{version}.md` under a "Registry state" sub-section.

## 5. Publication metadata check (curator Step 5.6)

Every release writes `release/{version}-publication-check.yaml`. This
file closes Step 5.6. A release ships only when every row is `true` or
carries a named waiver.

```yaml
# release/2026-04-22-publication-check.yaml
- versionIRI_resolves: true                     # curl -I returns 200/303 → artifact
- PURL_to_versioned_IRI: true                   # purl.obolibrary.org or w3id resolves
- content_negotiation:
    text/turtle: ok
    application/rdf+xml: ok
    application/ld+json: ok
    text/html: ok                               # landing page
- license_resolves: true                        # dcterms:license URL returns 200
- prior_version_linked: true                    # owl:priorVersion set
- prov_derived_from_present: true               # prov:wasDerivedFrom for every upstream
- registry_current:
    obo_foundry: "n/a (not registered)"
    bioportal:   "n/a (not registered)"
    ols:         "n/a (not registered)"
    lov:         "2026-04-22"                   # registry entry visible
- artifact_sha256_match: true                   # release/*.ttl sha matches published
- download_bytes_match: true                    # published bytes == artifact bytes
- widoco_docs_generated: true                   # HTML landing page regenerated
- waivers: []                                   # any row false requires a named waiver here
```

Sample waiver block (carried in the same YAML when a row legitimately
fails):

```yaml
- waivers:
    - row: "obo_foundry"
      reason: "Ontology is internal to the monorepo; not intended for public OBO registration."
      reviewer: "@koko"
      expires: "2027-04-22"
```

## 6. Provenance triples — what to emit on every release

Each release artifact stamps its provenance in the ontology header via
PROV-O. Curator Step 5 writes these fields; validator L0 checks them.

```ttl
<https://w3id.org/ensemble/2026-04-22>
    prov:generatedAtTime "2026-04-22T14:05:00Z"^^xsd:dateTime ;
    prov:wasAttributedTo <https://orcid.org/0000-…> ;
    prov:wasDerivedFrom
      <http://purl.obolibrary.org/obo/bfo/2020/bfo.owl> ,
      <http://www.mimo-international.com/mimo-core/2025-11> ,
      <https://w3id.org/ensemble/2026-03-15> ;
    dcterms:hasVersion "2026-04-22" ;
    dcterms:license <https://creativecommons.org/licenses/by/4.0/> .
```

Each `prov:wasDerivedFrom` IRI MUST appear in
`imports-manifest.yaml` with the same `version_iri`. The validator's
L0 import-closure check verifies the round-trip.

## 7. SSSOM release provenance

Mapping sets ship with their own `mapping_set_version` under
[`sssom-semapv-recipes.md § 2`](sssom-semapv-recipes.md). On a
curator import refresh (see
[`worked-examples/microgrid/curator.md`](worked-examples/microgrid/curator.md)),
the mapper bumps the mapping-set version and records
`prov:wasRevisionOf` pointing to the prior mapping set.

## 8. Anti-patterns

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Versioned IRI points at latest-only artifact | Consumers pinned to a date find it has moved | Make `{versionIRI}` immutable; `{canonicalIRI}` is the only mutable redirect. |
| Content negotiation missing | `curl -H "Accept: text/turtle"` returns HTML | Configure `.htaccess` per § 2 / § 3. |
| License field points to 404 | `dcterms:license` URL stale | Use SPDX license URL (`creativecommons.org`) not a project docs page. |
| No `prov:wasDerivedFrom` | Consumer cannot verify upstream alignment | Curator Step 5 must emit PROV triples per § 6. |
| Registry entry lags release | Consumers pull stale term via registry search | Record `registry_current` row in publication check; contact registry if > 1 release behind. |
| Term IRI rewritten across release | Consumer `SPARQL SELECT` against old IRI returns zero rows | Never rewrite. Deprecate and point replacement IRI. |

## 9. Worked examples

- [`worked-examples/ensemble/curator.md`](worked-examples/ensemble/curator.md) — Step 5.6 publication-check on a MINOR release with OBO date versioning.
- [`worked-examples/microgrid/curator.md`](worked-examples/microgrid/curator.md) — OEO import refresh triggers a PATCH bump with `prov:wasDerivedFrom` pointing at the new upstream.

## 10. References

- [W3C Cool URIs](https://www.w3.org/TR/cooluris/) — dereferenceable identifier patterns.
- [OBO Foundry PURLs](http://obofoundry.org/id-policy.html) — OBO ID policy.
- [w3id.org repo](https://github.com/perma-id/w3id.org) — where to submit `w3id` redirects.
- [PROV-O](https://www.w3.org/TR/prov-o/) — provenance ontology.
- [OLS4 submission guide](https://www.ebi.ac.uk/ols4/help) — ontology indexing.
- [WIDOCO](https://github.com/dgarijo/Widoco) — HTML ontology documentation.
