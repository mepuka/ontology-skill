# Modularization and Bridges

**Referenced by:** `ontology-scout`, `ontology-conceptualizer`, `ontology-architect`.
**Complements:** [`odk-and-imports.md`](odk-and-imports.md) (import *mechanics*
via MIREOT/STAR/BOT/TOP + ODK).

`odk-and-imports.md` answers *how to extract an import module*. This file
answers the prior questions: *when to split*, *when to merge*, *when to
bridge*, and *what goes wrong when the module boundary is wrong*.

Use this when:

- Scoping a new ontology and deciding whether to single-file it or split it.
- Choosing between import vs. bridge vs. copy.
- Reviewing whether an existing module has drifted into overreach.
- Debugging a broken merge.

## 1. Module granularity — how big should one ontology be?

A module is *one* ontology file (plus imports). Size is less a line count
than a conceptual count. Rule of thumb:

| Module scope | Size signal | Verdict |
|---|---|---|
| One BFO sibling branch (e.g., music instruments under material entity) | 50–500 classes | Healthy — keep as one module. |
| Two unrelated branches sharing a file | e.g., instruments + composers + performances all in one file | Split: separate modules per branch, bridge via shared parent. |
| Imports dominate edit file (> 80% imported) | edit file contains few original terms | Likely over-modularized; consider folding back. |
| Edit file grew past ~1500 classes | Hard to reason, review, diff | Split by subgraph. |
| A term is used only by one consumer | no other module refers to it | Keep it in the consumer's module, not the shared one. |

**Split triggers** (any one is enough to warrant splitting):

1. **Distinct domain experts** maintain different parts (e.g., strings vs. percussion).
2. **Distinct licenses** apply (rare but decisive).
3. **Distinct release cadences** (e.g., a stable core + experimental extensions).
4. **Distinct profiles** (e.g., an EL-safe core + a DL-only extension for reasoning).
5. **Reuse shape asymmetry**: one part is imported widely, another is not.
6. **Reasoner wall-clock**: if HermiT takes > 60s, split before adding more axioms.

A *decomposition is not free*: each module needs its own metadata block,
CI job, versioning trail, and release. Do not split for aesthetic reasons;
split when a trigger fires.

## 2. Layering within a module

When a module is large enough to have internal structure, layer it rather
than splitting, until a split trigger fires. Three layers are common:

| Layer | Contents | Depends on |
|---|---|---|
| **Upper** | BFO/RO/IAO imports, domain-neutral parent classes | External only |
| **Domain** | Domain-specific classes and properties | Upper |
| **Application** | Site-specific subclasses, SHACL shapes, ABox templates | Upper + Domain |

Record layer assignment in `docs/conceptual-model.yaml` under `layers:`.
Each class names its layer; import directives flow *down* only (upper ←
domain ← application). An upper-layer class must never import a
domain-layer class.

**Anti-pattern:** layers declared but not enforced at file boundaries.
If all three layers live in one TTL file with no import separation, the
layering is decorative, not structural.

## 3. Import vs. bridge vs. copy

When two ontologies overlap, pick one mechanism — mixing them is the
single most common merge failure.

| Mechanism | When | Cost | See |
|---|---|---|---|
| **Import** | You need their axioms; you trust their stability | Their axioms affect your reasoner. Version drift risk. | [`odk-and-imports.md`](odk-and-imports.md) |
| **Bridge ontology** | You need mappings to their terms but cannot absorb their axioms | Separate mapping file + its own release cycle. | § 5 below |
| **Copy (MIREOT a single term)** | You need one or two terms and nothing else | Manual refresh burden. | [`odk-and-imports.md § 3`](odk-and-imports.md) |

Rule of thumb: **import when you need reasoning, bridge when you need
identity, copy when you need a label**.

## 4. Merge pitfalls

Every merge (`robot merge`) operates on the raw union of triples. Without
care, merges produce one of these failure modes.

| Pitfall | Symptom | Fix |
|---|---|---|
| **Same CURIE, different axioms** | Two imports define `BFO:0000001` with incompatible parents | Pin one version in `imports-manifest.yaml`; fix or reject the other. |
| **Duplicate IRI, different label** | `obo:RO_0000057` has `has participant` in one source and `hasParticipant` in another | Canonicalize label; keep one import; file upstream issue. |
| **Shadow axiom on an imported term** | Your edit file adds `SubClassOf` to an imported class | Usually wrong — refactor as a subclass of your own. See § 4.1. |
| **Profile break on merge** | `validate-profile` passes per-file but fails merged | Merge-first preflight (see [`owl-profile-playbook.md § 5`](owl-profile-playbook.md#5-preflight-validate-before-reasoning)). |
| **Unsatisfiable after merge only** | Reasoner passes pre-merge, fails post-merge | Cross-module disjointness collision; isolate with `robot relax` + diff. |
| **Namespace pollution** | Many blank nodes and unnamed classes | One import is using anonymous axioms over classes you also assert; normalize to named classes. |

### 4.1 Shadow axioms on imported terms

Adding axioms to an imported term is allowed (OWL semantics are
monotone), but is almost always a symptom of poor modularization. If
your ontology adds `SubClassOf X` to an imported class, one of:

- You should have subclassed your own term under X, not modified X.
- You should propose the axiom upstream (file an issue in the source).
- You should bridge, not import.

See § 5 below for bridge patterns.

## 5. Bridge ontology patterns

A **bridge ontology** is a standalone module whose only purpose is to
assert cross-ontology relations. It imports both sources (or declarations
from both) and contains only *bridge axioms*: equivalences, mappings, or
aligning restrictions.

Convention: `{src}-to-{target}-bridge.ttl` under
`ontologies/{name}/mappings/` with its own `mapping_set_id`.

### 5.1 SKOS-mapping bridge (weak identity)

The simplest bridge is a SSSOM set converted to OWL with
`skos:exactMatch`/`closeMatch`/etc. preserved. No OWL identity claim.
Downstream tools that care about identity must opt in.

See [`sssom-semapv-recipes.md § 7`](sssom-semapv-recipes.md#7-translation-to-owl).

### 5.2 Equivalence bridge (strong identity)

For same-domain mapping with curator confirmation, translate
`skos:exactMatch` to `owl:equivalentClass`. This *will* be picked up by
the reasoner. Run consistency and clique checks before publishing.

```bash
uv run sssom parse --preset exact-owl \
  music-to-wikidata.sssom.tsv \
  --output music-to-wikidata.owl.ttl
.local/bin/robot reason --reasoner HermiT \
  --input merged-with-bridge.ttl \
  --output /tmp/reasoned.ttl
# If reasoner reports unsatisfiable classes, the bridge is too strong.
```

### 5.3 Alignment bridge (structural)

When two ontologies differ in granularity or modeling style, align
structurally rather than asserting equivalence:

```
OurOntology:CelloRole
    SubClassOf: rdfs:subClassOf bfo:Role ;
                owl:equivalentClass [ RO:borneBy some MIMO:Cello ] .
```

This says "our CelloRole is instantiated exactly when a MIMO cello bears
it" — stronger than SKOS, weaker than class equivalence. Use when the
same *extension* is modeled as role vs. type across the two ontologies.

### 5.4 Bridge safety gate

Before publishing any bridge:

1. **Reason with source + target + bridge merged.** Failure = the bridge
   has introduced an incoherence.
2. **Clique check** per [`mapping-evaluation.md § 3`](mapping-evaluation.md#3-clique-check-exactmatch-transitivity).
3. **Disjointness smoke test:** if source asserts `DisjointClasses(A, B)`
   and the bridge equates `A ≡ A'` and `B ≡ A'`, unsatisfiability follows.
4. **Release under its own `versionIRI`**; do not piggyback on a source's IRI.

Failures route back to `ontology-mapper` with
`failure_type: mapping conflict`. See
[`iteration-loopbacks.md`](iteration-loopbacks.md).

## 6. Decision tree — import, bridge, or copy?

```
Need only a term label / CURIE for display?
  └─ yes → copy (MIREOT a single term) or use a lookup table; do not import.

Need reasoner to use their axioms?
  └─ yes → import.
      ├─ Stable, small: direct import.
      ├─ Large: ROBOT extract (MIREOT / STAR / BOT / TOP per odk-and-imports.md).
      └─ Unstable upstream: pin version in imports-manifest; refresh on curator's schedule.

Need only to say "our term is the same as theirs"?
  └─ yes → bridge (SKOS-mapping bridge § 5.1).
      ├─ Intra-domain, curator-confirmed: equivalence bridge § 5.2.
      ├─ Cross-domain: stay SKOS; do not escalate to equivalence.
      └─ Different modeling granularity: alignment bridge § 5.3.

Need their axioms AND to add more axioms to their terms?
  └─ Refactor: subclass their term locally and add axioms to the subclass.
     Propose the upstream axiom if applicable.
```

## 7. Anti-patterns specific to modularization

| Anti-pattern | Symptom | Fix |
|---|---|---|
| **Kitchen-sink module** | One module covers three domains with no internal structure. | Split on a natural boundary (BFO branch, domain, profile). |
| **Premature split** | Modules created without a split trigger; each is thin. | Merge back; layer internally per § 2. |
| **Axioms-on-import** | Edit file adds axioms to imported classes. | Refactor as local subclass per § 4.1. |
| **Bridge as dumping ground** | Bridge file holds new domain classes. | Move new classes to the proper domain module; bridge contains only bridge axioms. |
| **Unreasoned bridge** | Bridge published without merged reasoning. | Run § 5.4. |
| **Identity via SSSOM + implicit OWL promotion** | SSSOM says `skos:exactMatch`, consumer parses as `owl:equivalentClass` | Pick one: publish SSSOM only (SKOS) *or* publish an equivalence bridge. Do not let the consumer choose. |

## 8. Worked examples

See (Wave 4):

- [`worked-examples/ensemble/scout.md`](worked-examples/ensemble/scout.md) — reusing MIMO for instruments: MIREOT vs. full import decision.
- [`worked-examples/ensemble/conceptualizer.md`](worked-examples/ensemble/conceptualizer.md) — layering music-core + performance-extension in one repo.
- [`worked-examples/microgrid/scout.md`](worked-examples/microgrid/scout.md) — importing OEO vs. bridging to `schema.org`.
- [`worked-examples/microgrid/architect.md`](worked-examples/microgrid/architect.md) — equivalence-bridge failure when two upstream ontologies disagree on inverter-as-object vs. inverter-as-function.

## 9. References

- [OWL 2 import semantics (W3C)](https://www.w3.org/TR/owl2-syntax/#Ontology_IRI_and_Version_IRI) — import IRI and versioning.
- [ROBOT extract](http://robot.obolibrary.org/extract) — MIREOT/STAR/BOT/TOP.
- [ODK documentation](https://github.com/INCATools/ontology-development-kit) — module extraction in managed projects.
- [`odk-and-imports.md`](odk-and-imports.md) — import mechanics + manifest schema.
