# Narrative Identity Rule — `energy-intel` V2

**Authored:** 2026-05-04 by `ontology-conceptualizer` (V2 iteration)
**Reviewer:** Mepuka Kessy (`kokokessy@gmail.com`)
**Reviewed at:** 2026-05-04
**Source:** [scope-v2.md § In-scope item 6](scope-v2.md), [source plan §S5 + §3.3](file:///Users/pooks/Dev/skygest-cloudflare/docs/plans/2026-05-04-editorial-ontology-slice.md), V2-CQ-Q-3 decision in [requirements-approval-v2.yaml](requirements-approval-v2.yaml).

This document formalizes the deterministic identity rule for `ei:Narrative` and `ei:NarrativePostMembership` IRIs. It resolves V2-CQ-Q-3 from Phase 1's requirements approval handoff.

---

## 1. Narrative IRI rule

### Rule

```
Narrative IRI = https://w3id.org/energy-intel/narrative/{story-stem}
```

Where `{story-stem}` is the filename of the markdown story file (without the `.md` extension), under the convention `narratives/{arc-slug}/stories/{story-stem}.md` in `skygest-editorial`.

**The arc directory does NOT enter the IRI.** Two stories from different arcs but with the same stem produce the same Narrative IRI — by design, this collision is an import error (see § 1.2 below).

### Examples

| Filesystem path | Story stem | Narrative IRI |
|---|---|---|
| `narratives/nuclear-economics/stories/2026-04-06-tva-nuclear-costs.md` | `2026-04-06-tva-nuclear-costs` | `https://w3id.org/energy-intel/narrative/2026-04-06-tva-nuclear-costs` |
| `narratives/global-renewables-growth/stories/2026-04-04-ember-814gw.md` | `2026-04-04-ember-814gw` | `https://w3id.org/energy-intel/narrative/2026-04-04-ember-814gw` |
| `narratives/data-center-grid-demand/stories/2026-04-12-tva-irp-2026.md` | `2026-04-12-tva-irp-2026` | `https://w3id.org/energy-intel/narrative/2026-04-12-tva-irp-2026` |

### Properties

1. **Deterministic.** Given a story stem, exactly one Narrative IRI exists.
2. **Stable.** The IRI does not change as the markdown content evolves. Editing the file updates the Narrative's content (a separate concern); the IRI is bound to the stem.
3. **Filesystem-decoupled.** Moving a story file from one arc directory to another (e.g., `nuclear-economics` → `electricity-markets-high-renewables`) does NOT change the Narrative IRI. Per source plan §S2: "the directory it lives in IS the arc."
4. **Idempotent on import.** Re-running the import pipeline against the same corpus produces zero new Narrative IRIs (every IRI hits the existing entity).

### Rationale (per source plan §S5)

The story id that `skygest-editorial` already derives from filename stems is the canonical identity. We re-use it directly as the IRI suffix; no second identifier minted.

Why arc directory is excluded:
- Arcs are filesystem-only (per source plan §S2). They are NOT ontology entities. Encoding the arc in the Narrative IRI would create a coupling between filesystem state (which arc a story lives in) and ontology identity, breaking S2's separation.
- Moving a story between arcs is an editorial operation (the editor decides "this story belongs to a different arc now"). The Narrative itself is the same — same headline, same posts, same argument pattern. Re-IRI-ing on move would force the cloudflare-side runtime to detect and replay every relationship the Narrative participates in.

### Why story-stem rename is an identity change

Renaming a story file (e.g., `2026-04-06-tva-nuclear-costs.md` → `2026-04-06-tva-nuclear-economics.md`) DOES change the Narrative IRI. Consequence: the new IRI is a different entity; the old IRI's relationships do not transfer.

Per source plan §S5: "renaming a story file is an identity change unless a later alias/redirect model is added."

**V2 ships:** the immutable-stem rule. Renames are explicit retract+recreate operations, not git-mv operations.

**V3+ may add:** an alias/redirect model (e.g., `dcterms:replaces` annotation on the new IRI pointing at the old, plus an editorial CLI flag `--rename-with-redirect`). This is out of V2 scope.

### Duplicate-stem handling

Two story files in different arcs but with the same stem produce the same Narrative IRI under this rule. Consequence: the import pipeline cannot distinguish them.

**V2 ships:** structured import error on duplicate stems. Per source plan §3.3 NarrativeImportService spec ("rejects duplicate story ids with a structured error pointing at the offending stem").

**Phase 7 step 1 precondition (cloudflare-side):** archive `/skygest-editorial/stories/story-*.md` legacy flat directory. F1 audit verified that the 6 legacy flat files would collide with 6 of the 8 nested-layout stems. After archival, all 8 nested stems are globally unique.

This is a cloudflare/editorial-side concern; the ontology only encodes the deterministic rule. The architect MUST NOT add an OWL axiom that "permits duplicate stems with arc disambiguation" — that would defeat the deterministic rule.

---

## 2. NarrativePostMembership IRI rule

### Rule (V2-CQ-Q-3 decision)

```
NarrativePostMembership IRI =
  https://w3id.org/energy-intel/narrative/{story-stem}/membership/{hash16}

hash16 = lowercase hex( sha256(narrativeIri || "\n" || postUri) )[0:16]
```

Where:
- `narrativeIri` is the canonical Narrative IRI (from § 1 above)
- `postUri` is the post identifier (e.g., `https://id.skygest.io/post/x-1886502618-status-2039766305071378920`)
- `||` is byte concatenation (UTF-8 encoded)
- `\n` (LF, byte 0x0A) is the separator
- The full sha256 digest is hex-encoded; the first 16 hex chars (= 8 bytes = 64 bits) are taken
- The result is lowercase

### Reference implementation (Python)

```python
import hashlib

def membership_iri(narrative_iri: str, post_uri: str) -> str:
    payload = (narrative_iri + "\n" + post_uri).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()  # 64 hex chars
    hash16 = digest[:16]                          # first 16 hex chars
    return f"{narrative_iri}/membership/{hash16}"

# Example:
narrative_iri = "https://w3id.org/energy-intel/narrative/2026-04-06-tva-nuclear-costs"
post_uri = "https://id.skygest.io/post/x-1886502618-status-2039766305071378920"
print(membership_iri(narrative_iri, post_uri))
# => https://w3id.org/energy-intel/narrative/2026-04-06-tva-nuclear-costs/membership/<16hex>
```

### Reference implementation (TypeScript / cloudflare worker)

```typescript
async function membershipIri(narrativeIri: string, postUri: string): Promise<string> {
  const payload = new TextEncoder().encode(`${narrativeIri}\n${postUri}`);
  const digest = await crypto.subtle.digest("SHA-256", payload);
  const hex = Array.from(new Uint8Array(digest))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
  const hash16 = hex.slice(0, 16);
  return `${narrativeIri}/membership/${hash16}`;
}
```

### Properties

1. **Deterministic.** Same `(narrativeIri, postUri)` → same IRI. Always. Cross-platform (Python, TypeScript, any other consumer).
2. **Idempotent on import.** Re-running the import pipeline produces zero new memberships per (narrative, post) pair.
3. **Roundtrip-safe.** Importing a corpus, exporting it, and re-importing yields identical IRIs.
4. **Collision-resistant.** 64 bits at the corpus scale (estimated < 10^8 memberships) gives < 10^-3 collision probability under birthday paradox. Detail in § 2.4 below.
5. **Length-balanced.** Final IRIs look like `.../narrative/{stem}/membership/a3f9c2e8b14d567f`. Readable; not bloated.

### Rationale

- **Deterministic from the inputs alone.** No timestamp, no counter, no random. The `(narrativeIri, postUri)` pair is the entire identity input. This guarantees idempotency: import the same corpus twice, get the same IRIs.
- **Hash function = sha256.** Cryptographic strength is overkill for collision avoidance, but using a standard hash is simpler than designing a custom function. sha256 is implemented in every standard library; no compatibility issues.
- **Truncation to 16 hex chars (64 bits).** See § 2.4 collision analysis.
- **Separator = LF (0x0A).** Concatenating `narrativeIri || postUri` directly without a separator is unsafe — a postUri could be a prefix of a longer one, producing the same payload. The LF separator forces a clean delimiter. Linear D3 already uses this convention for compound identity.

### Collision analysis (§ 2.4)

At the editorial corpus scale (estimated for the foreseeable future):

| Scale | Memberships per hash space | Birthday-paradox collision probability |
|---|---|---|
| Current (8 narratives × ~5 posts each = 40 memberships) | 40 / 2^64 | < 10^-17 |
| 1000 narratives × 50 posts = 50,000 memberships | 50,000 / 2^64 | < 10^-13 |
| 100,000 narratives × 1000 posts = 10^8 memberships | 10^8 / 2^64 | ≈ 5 × 10^-4 |
| 10^9 narratives × 10^4 posts = 10^13 memberships (fantasy scale) | 10^13 / 2^64 | ≈ 0.4 (collision likely) |

The 16-hex-char truncation is sufficient for any realistic editorial-corpus scale. If the system ever approaches 10^13 memberships (i.e., never), the truncation can be increased to 32 chars (128 bits) without breaking existing IRIs — the new IRIs are simply longer, and the existing ones are stable.

### Detection of collision (defense-in-depth)

Although collision probability is vanishingly low at realistic scale, the SHACL invariant CQ-N7 (`sh:qualifiedMaxCount 1` per (Narrative, Post) pair) provides a runtime check: if two distinct memberships ever resolve to the same IRI, exactly one of them gets stored (the second is rejected by D1's primary-key constraint or by the SPARQL query's deduplication), and the conflict surfaces as an inconsistency in CQ-N7.

If a collision were ever detected (e.g., the import pipeline detects the IRI already exists with a different `(narrativeIri, postUri)` pair than the current input), the recovery procedure would be: increase truncation to 32 chars (creates new IRIs for affected memberships, breaks roundtrip on those rows but preserves all others), or switch to a different hash function (sha384, sha512). Both are V3+ concerns; V2 ships the 16-char rule.

### Why not alternatives

| Alternative | Rejected because |
|---|---|
| sha256 truncated to 8 hex chars (32 bits) | At 10^5 memberships, collision probability ~ 1% (birthday paradox: 2^16 = 65,536 ≈ √2^32). Unacceptable. |
| sha256 truncated to 32 hex chars (128 bits) | Longer than necessary at editorial-corpus scale; readability trade-off (40+ char IRI suffix) without tangible benefit |
| base32 / base64 encoding | Shorter at same bit count, but introduces case-sensitivity issues in some URI parsers (URIs are case-sensitive, but base32 has `O`/`0` ambiguity). Hex is unambiguous. |
| ULID | ULIDs encode timestamps. Importing the same corpus on different days would produce different ULIDs — violates idempotency. |
| sequential integer (e.g., `/membership/1`, `/membership/2`) | Requires a runtime counter; not derivable from `(narrativeIri, postUri)` alone. The architect's primary requirement is "derivable without runtime ambiguity" — sequential breaks this. |
| UUIDv5 (name-based) | Deterministic; would work. We chose sha256-truncated because it's simpler and equivalent at 64 bits. UUIDv5 is overkill (full 128 bits encoded) and the IRI suffix is longer and less readable. |
| Composite IRI like `/membership/{post-uri-percent-encoded}` | Readable and deterministic; makes IRI suffix vary in length and contain `%xx` escapes from postUri. Less clean. The hash provides a fixed-length, fixed-format suffix. |

### Path-form considerations

The membership IRI is a *path-segmented* IRI: `{narrativeIri}/membership/{hash16}`. This means:
- Resolving the membership IRI provides hierarchical context (you can see which Narrative it belongs to from the IRI alone).
- W3ID resolution (when w3id.org redirects are configured) can serve a JSON-LD or HTML representation per IRI. The path form integrates cleanly with `.htaccess` / nginx rules.
- The membership IRI is "owned" by the Narrative — making it part of the Narrative's path makes ontology-store lifecycle clearer (e.g., deleting a Narrative could in principle cascade to its memberships, though V2 does not implement deletion).

### Trade-off: hash16 is opaque

The 16-hex-char hash is not human-readable in the sense of "I can tell which post this membership references just by looking at the IRI." This is intentional: the alternative (encoding the post-URI in the IRI) bloats the IRI and makes it dependent on the post-URI's exact form (which could change if the post is migrated between systems).

The opacity is a feature, not a bug. Tools that need to display "which post" should look up `ei:memberPost` rather than parse the IRI.

---

## 3. Argument-pattern concept IRI rule

### Rule

```
ArgumentPattern concept IRI = https://w3id.org/energy-intel/concept/argument-pattern/{pattern-stem}
```

Where `{pattern-stem}` is the filename of the pattern's reference doc (without the `.md` extension), under `/skygest-editorial/references/argument-patterns/{pattern-stem}.md`.

### The 7 V2 concepts

| Filename | IRI suffix | Concept IRI |
|---|---|---|
| `deployment-milestone.md` | `deployment-milestone` | `https://w3id.org/energy-intel/concept/argument-pattern/deployment-milestone` |
| `emergent-technology-bulletin.md` | `emergent-technology-bulletin` | `https://w3id.org/energy-intel/concept/argument-pattern/emergent-technology-bulletin` |
| `geographic-energy-project.md` | `geographic-energy-project` | `https://w3id.org/energy-intel/concept/argument-pattern/geographic-energy-project` |
| `grid-snapshot.md` | `grid-snapshot` | `https://w3id.org/energy-intel/concept/argument-pattern/grid-snapshot` |
| `learning-curve.md` | `learning-curve` | `https://w3id.org/energy-intel/concept/argument-pattern/learning-curve` |
| `methodological-critique.md` | `methodological-critique` | `https://w3id.org/energy-intel/concept/argument-pattern/methodological-critique` |
| `structural-economic-analysis.md` | `structural-economic-analysis` | `https://w3id.org/energy-intel/concept/argument-pattern/structural-economic-analysis` |

### Properties

Same as Narrative IRI rule — deterministic, stable, filesystem-decoupled (the directory `references/argument-patterns/` does not enter the IRI), idempotent on import.

### Why use the filename stem

The filename stems are already the de-facto pattern identifiers in `skygest-editorial`. The frontmatter `argument_pattern: structural-economic-analysis` in story files already references the stem. Re-using it as the IRI suffix preserves the existing identity convention.

---

## 4. Narrative-role concept IRI rule

### Rule

```
NarrativeRole concept IRI = https://w3id.org/energy-intel/concept/narrative-role/{role-name}
```

### The 4 V2 concepts

| Role | IRI |
|---|---|
| lead | `https://w3id.org/energy-intel/concept/narrative-role/lead` |
| supporting | `https://w3id.org/energy-intel/concept/narrative-role/supporting` |
| counter | `https://w3id.org/energy-intel/concept/narrative-role/counter` |
| context | `https://w3id.org/energy-intel/concept/narrative-role/context` |

### Properties

Closed enumeration. The 4 roles are stable per source plan §3.3. Adding a 5th role is an ontology PR (mint a new concept IRI; declare in `concept-schemes/narrative-role.ttl`).

---

## 5. Editorial supplement concept IRI rule

### Rule

```
Supplement concept IRI = https://w3id.org/energy-intel/concept/{slug}
```

Where `{slug}` is the editorial topic slug from `canonicalTopicOrder` (e.g., `data-center-demand`).

### Properties

- Each supplement IRI carries `skos:notation` with the legacy editorial slug for migration-period queryability (per V2-CQ-T2 / source plan §9 Q6 recommendation in scope-v2.md Open Question 4).
- Each supplement IRI is in the `https://w3id.org/energy-intel/concept/` namespace — distinguishing it from OEO IRIs (`https://openenergyplatform.org/ontology/oeo/`) at the IRI prefix level.

### The 19 V2 supplements

Per [conceptual-model-v2.md § 11 finding 3](conceptual-model-v2.md): 17 always-needed + 2 conditional, conceptualizer decision is to ship both → 19 total. Full list in [topic-vocabulary-mapping.md](topic-vocabulary-mapping.md).

---

## 6. OEO topic concept IRIs

OEO IRIs are reused as-is. No re-IRI-ing into the `ei:concept/` namespace.

```
OEO concept IRI = https://openenergyplatform.org/ontology/oeo/OEO_NNNNNNNN
```

The architect emits `oeo:OEO_xxx skos:inScheme ei:concept/oeo-topic, ei:concept/topic` in `concept-schemes/oeo-topics.ttl` to make OEO IRIs members of the runtime topic catalog. Punning makes the same IRI both an `owl:Class` (from OEO subset import) and a `skos:Concept` instance (from the `inScheme` assertion).

---

## 7. Identity rule summary table

| Entity | IRI form | Determinism source | Notes |
|---|---|---|---|
| `ei:Narrative` | `https://w3id.org/energy-intel/narrative/{story-stem}` | Filename stem | Arc directory excluded; rename = identity change |
| `ei:NarrativePostMembership` | `https://w3id.org/energy-intel/narrative/{story-stem}/membership/{sha256-16}` | sha256 of `(narrativeIri || "\n" || postUri)` | 64 bits; collision-resistant at corpus scale |
| ArgumentPattern concept | `https://w3id.org/energy-intel/concept/argument-pattern/{pattern-stem}` | Reference filename stem | 7 stable concepts |
| NarrativeRole concept | `https://w3id.org/energy-intel/concept/narrative-role/{role-name}` | Closed enumeration | 4 stable concepts |
| Editorial supplement concept | `https://w3id.org/energy-intel/concept/{slug}` | Editorial topic_slug | 19 concepts; carries skos:notation |
| OEO concept | `https://openenergyplatform.org/ontology/oeo/OEO_NNNNNNNN` | OEO upstream | 41 verified IRIs reused as-is |

---

## 8. Architect implementation guidance

The architect MUST:

1. **Implement the Narrative IRI rule** as a Python helper in `scripts/build_fixtures.py` (and/or in the cloudflare-side `narrative.ts` — per Phase 4):
   ```python
   def narrative_iri(story_stem: str) -> str:
       return f"https://w3id.org/energy-intel/narrative/{story_stem}"
   ```

2. **Implement the NarrativePostMembership IRI rule** as a Python helper:
   ```python
   import hashlib
   def membership_iri(narrative_iri: str, post_uri: str) -> str:
       payload = (narrative_iri + "\n" + post_uri).encode("utf-8")
       hash16 = hashlib.sha256(payload).hexdigest()[:16]
       return f"{narrative_iri}/membership/{hash16}"
   ```

3. **Use these helpers in V2 fixture-building.** Do NOT hard-code IRIs in fixtures; always derive them from inputs via the helpers.

4. **Document the helpers in a build-time script comment** so that the cloudflare-side TypeScript implementation can be verified against them as the canonical source.

5. **NOT add any OWL axiom that asserts the deterministic rule.** The rule is enforced by the import pipeline, not by the ontology. An axiom like "Narrative SubClassOf hasIdentifier some xsd:anyURI" is acceptable but does not encode the deterministic hash itself; the IRI minting logic stays in code.

6. **NOT add an alias/redirect axiom.** V2 ships the immutable-stem rule. V3+ may add aliases via `dcterms:replaces` or similar; that is out of V2 scope.

---

## 9. Open issues

None blocking. The 4 V2-Q questions are answered:
- V2-CQ-Q-1: split + aggregator (see [conceptual-model-v2.md § 4](conceptual-model-v2.md))
- V2-CQ-Q-2: 41/41 OEO candidates pass (see [topic-vocabulary-mapping.md](topic-vocabulary-mapping.md))
- V2-CQ-Q-3: this document, § 2 (sha256 truncated to 16 hex chars)
- V2-CQ-Q-4: SHACL-only enumeration (see [property-design-v2.md § 3](property-design-v2.md))
