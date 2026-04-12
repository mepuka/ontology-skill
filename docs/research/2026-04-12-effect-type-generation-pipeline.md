# Effect Type Generation Pipeline: SHACL → TypeScript

**Date:** 2026-04-12
**Target repo:** `skygest-cloudflare`
**Source repo:** `ontology_skill/ontologies/skygest-energy-vocab`
**Current artifact:** `src/domain/profile/energyVariableProfile.ts` (hand-maintained, lives alongside a stub `src/domain/generated/` directory)

## 1. Executive summary

Split the pipeline in two. The **Python side** (rdflib) reads SHACL shapes plus SKOS vocabulary JSON and writes a single neutral `shacl-manifest.json` under `ontologies/skygest-energy-vocab/build/`, versioned with a content hash and provenance. The **TypeScript side** (a small `scripts/generate-energy-profile.ts` inside `skygest-cloudflare`, built on `effect/unstable/cli` + `effect` `FileSystem`/`Path` exactly like the existing `sync-vocabulary.ts`) reads the manifest, **decodes it through an Effect Schema** to validate the contract, then emits `src/domain/generated/energyVariableProfile.ts` using `SchemaRepresentation.toCodeDocument` for the enum-shaped parts and a thin hand-written emitter for the tuple/predicate extras. CI enforces freshness with the same `bun run <cmd> && git diff --exit-code` pattern already used for `cf:types`. This keeps RDF parsing in the language with the best tooling (Python/rdflib), keeps TypeScript emission inside Effect's own codegen primitives, and keeps drift detection identical to the pattern the repo already has in production.

## 2. Effect-native findings

All paths below are under `.reference/effect/packages/` and were read directly.

### 2.1 Schema has a first-class, serializable code-generation layer

`effect/src/SchemaRepresentation.ts` (3400+ lines) is an explicit IR between `SchemaAST` and external formats. Module header (lines 1–87) documents it as the bridge for "code generation, serialized JSON, JSON Schema." Relevant exports:

- `fromAST(ast)` / `fromASTs([...])` — `SchemaAST` → `Document` / `MultiDocument` (lines 35–37 of the module header, implementation delegates to `InternalRepresentation`).
- `toCodeDocument(multiDocument, { reviver? })` — **the key primitive**. Defined at `SchemaRepresentation.ts:2288`. It returns:
  ```ts
  type CodeDocument = {
    readonly codes: ReadonlyArray<{ readonly runtime: string; readonly Type: string }>
    readonly references: {
      readonly nonRecursives: ReadonlyArray<{ $ref: string; code: Code }>
      readonly recursives: { [$ref: string]: Code }
    }
    readonly artifacts: ReadonlyArray<Artifact>   // Symbol | Enum | Import
  }
  ```
  `Code.runtime` is the executable `Schema.Struct(...)` expression; `Code.Type` is the corresponding TypeScript `type` declaration. `artifacts` collects `import` statements needed by the generated code (`SchemaRepresentation.ts:2206–2250`).
- `fromJsonSchemaDocument` / `fromJsonSchemaMultiDocument` (lines 2898, 2927) — lets us round-trip through JSON Schema. That means the Python side could write *JSON Schema* as the neutral format and the TS side would reconstruct a full `Document` via `fromJsonSchemaDocument`, then call `toCodeDocument` — zero hand-templated TS strings for the enum parts.
- `toSchema(document)` — reconstructs a runtime `Schema` from a `Document`, useful for in-process validation before emit.

### 2.2 `Schema.Literals` is a runtime-constructible closed union

`effect/src/Schema.ts:3530`:

```ts
export function Literals<const L extends ReadonlyArray<AST.LiteralValue>>(literals: L): Literals<L> {
  const members = literals.map(Literal) as { ... }
  return make(AST.union(members, "anyOf", undefined), { ... })
}
```

The function is generic over a `const` tuple, so the generated TypeScript does **not** need any type annotations — passing the tuple by `as const` is enough to produce a fully typed `Schema.Literals<["stock", "flow", ...]>`. This means the emitted file can use `Schema.Literals([...] as const)` and derive `type X = Schema.Schema.Type<typeof X>` without per-enum type gymnastics. `SchemaAST.Literal` is defined at `SchemaAST.ts:1069` and its `LiteralValue = string | number | boolean | bigint` (`SchemaAST.ts:1044`).

### 2.3 `effect/unstable/cli` is the modern CLI module (not `@effect/cli`)

The Effect v4 monorepo moved CLI out of a separate package. It now lives at `packages/effect/src/unstable/cli/` with `Command.ts`, `Flag.ts`, `Argument.ts`, `Param.ts`, `Primitive.ts`, `Prompt.ts`, `CliError.ts`, `CliOutput.ts`, `HelpDoc.ts`, and an `internal/` lexer+parser. `Command.ts` (line 4 onward) imports `FileSystem`, `Path`, `Terminal`, `ChildProcessSpawner` — so CLIs get FS access as a Layer dependency.

Critically, **`skygest-cloudflare/scripts/sync-vocabulary.ts` already uses exactly this module**: `import { Command, Flag } from "effect/unstable/cli"` and `import { Console, Effect, FileSystem, Path, Result } from "effect"`. It composes `Command.make(name, { flags }, handler)` and runs via `Command.runWith(cmd, { version })`. That is the template to clone for the new generator.

### 2.4 Platform-node FileSystem

`platform-node/src/NodeFileSystem.ts` and the abstract interface in `effect/src/FileSystem.ts` expose `readFileString(path, encoding?)` (`FileSystem.ts:243`), `writeFileString(path, data)` (line 359), `makeDirectory(path, { recursive })` (line 158), `exists`, `copyFile`. The existing `sync-vocabulary.ts` demonstrates the effect-idiomatic usage (`fs.exists`, `fs.readFileString`, `fs.copyFile` wrapped in `Effect.mapError`). skygest-cloudflare, however, runs scripts on **Bun** (`BunRuntime.runMain` + `BunServices.layer` — see `src/platform/ScriptRuntime.ts`), which provides the same `FileSystem` and `Path` services. The new generator should use `scriptPlatformLayer` for consistency, not `NodeFileSystem` directly.

### 2.5 Effect's own codegen scripts

`.reference/effect/scripts/` contains `analyze-jsdoc.mjs`, `codemod.mjs`, `codemod-ts-fence.mjs`, `docs.mjs`, `version.mjs`, and a `codemods/` directory. These are all `.mjs` plain-Node scripts — Effect itself does not dogfood `unstable/cli` for its own build scripts. That tells us two things: (a) `unstable/cli` is production-ready but is targeted at end-user CLIs, not internal build tooling; (b) plain Bun scripts are equally acceptable for generator code, as demonstrated by `scripts/generate-worker-types.ts`, which is pure imperative Bun + `node:fs`. We should still prefer the Effect-shaped variant because `sync-vocabulary.ts` has already set that precedent for vocabulary-adjacent tooling, and the generator is a peer of that script.

## 3. Approach comparison

| # | Approach | Source of truth | Intermediate format | TS emission | Pros | Cons |
|---|----------|----------------|---------------------|-------------|------|------|
| A | Python writes `.ts` directly (current PoC: `generate_types_from_shacl.py`) | SHACL Turtle | none | string templates in Python | Fewest moving parts; single language to run | Python writing TS quoting/imports is fragile; Python has no way to call `SchemaRepresentation.toCodeDocument`; drift detection requires Python in CI; loses Effect-native guarantees |
| B | Python writes JSON manifest; TS generator reads via Effect Schema | SHACL Turtle (+ vocab JSON) | `shacl-manifest.json` (hand schema) | hand-written emitter in TS | Clean language split; TS owns TS emission; CI already runs Bun | Hand emitter is still string templating; doesn't leverage `toCodeDocument` |
| C | Python writes **JSON Schema** (draft-2020-12) manifest; TS reads via `SchemaRepresentation.fromJsonSchemaDocument` → `toCodeDocument` | SHACL Turtle (+ vocab JSON) | JSON Schema `$defs` with `enum` / `const` / `type` | `SchemaRepresentation.toCodeDocument` | Reuses Effect's own codegen primitive; no bespoke TS-string templating for the enum core; JSON Schema is a portable, spec'd interchange format | Python must emit valid draft-2020-12; tuple/predicate extras still need a thin hand-written emitter because they aren't "a schema" |
| D | Move all parsing to TS with a TS RDF library | SHACL Turtle | none (in-process) | `SchemaRepresentation.toCodeDocument` | Single language, zero cross-repo FS | Best TS RDF libs (`n3`, `rdflib.js`) are meaningfully less capable than Python `rdflib` for SHACL `sh:in` with RDF collections and SPARQL targets; adds large RT dep |
| E | Effect's own IR on both sides: Python writes a serialized `Document` via `DocumentFromJson` codec | SHACL Turtle | `Document` JSON (Effect-internal format) | `SchemaRepresentation.toCodeDocument` | Even tighter Effect round-trip | Python must emit a format whose shape is controlled by an Effect internal module — high coupling to Effect version |

**Recommendation: Approach C** for the enum schemes (StatisticType, Aggregation, UnitFamily, Frequency-if-closed) plus **Approach B** style hand emission for the non-schema artifacts (`FACET_KEYS`, `REQUIRED_FACET_KEYS`, `*Canonicals` open vocabularies). JSON Schema as the wire format because it is already a first-class citizen of `SchemaRepresentation`, is widely understood, and does not couple the ontology project to Effect internals. Approach D is tempting long-term but not today — `oxigraph-js` / `n3` SHACL support is not comparable to Python rdflib + pyshacl.

## 4. Recommended pipeline

### 4.1 File layout

**Ontology repo (`ontology_skill`):**
```
ontologies/skygest-energy-vocab/
├── scripts/
│   ├── generate_types_from_shacl.py        # PoC — keep for demo, gate with --print
│   └── build_type_manifest.py               # NEW: writes deterministic JSON Schema manifest
├── build/                                    # NEW, gitignored
│   └── shacl-manifest.json                   # committed? see §4.4
└── shapes/skygest-energy-vocab-shapes.ttl    # source of truth (read-only to build)
```

**TS repo (`skygest-cloudflare`):**
```
scripts/
├── sync-vocabulary.ts                        # existing
└── generate-energy-profile.ts                # NEW
src/domain/generated/
└── energyVariableProfile.ts                  # NEW; the real "generated" file (replaces hand-maintained profile/energyVariableProfile.ts)
references/energy-profile/
└── shacl-manifest.json                       # NEW; committed copy of the Python output
```

### 4.2 Python side: `build_type_manifest.py`

Pure rdflib, no external deps beyond what the ontology project already has. Responsibilities:

1. Parse `shapes/skygest-energy-vocab-shapes.ttl` with `rdflib.Graph`.
2. For each shape in a declared `SHAPE_TO_TS_TYPE` map (the PoC already has this), extract `sh:in` values via `rdflib.collection.Collection` (PoC does this correctly at `generate_types_from_shacl.py:84`).
3. Cross-reference `data/vocabulary/*.json` to also surface the full `{canonical, surfaceForm}` mapping tables (these feed the `*Canonicals` exports and the future surface-form indexes).
4. Extract `sh:minCount` per property from shapes targeting `EnergyVariableShape` (for `REQUIRED_FACET_KEYS`) — the PoC does not yet do this.
5. Extract the `qb:DataStructureDefinition` / `qb:component` chain from `skygest-energy-vocab.ttl` to derive `FACET_KEYS` in dimension order. Use SPARQL via rdflib:
   ```sparql
   SELECT ?dim ?order WHERE { sevocab:EnergyVariableDSD qb:component ?c . ?c qb:dimension ?dim ; qb:order ?order } ORDER BY ?order
   ```
6. Emit a JSON document with this shape:
   ```json
   {
     "$schema": "https://json-schema.org/draft/2020-12/schema",
     "$id": "https://skygest.dev/vocab/energy/manifest/v1",
     "generatedAt": "2026-04-12T...Z",
     "sourceCommit": "<git rev-parse HEAD of ontology repo>",
     "shapesFileHash": "sha256:...",
     "facetKeys": ["measuredProperty", ...],
     "requiredFacetKeys": ["measuredProperty", "statisticType"],
     "closedEnums": {
       "StatisticType": { "type": "string", "enum": ["stock", "flow", ...] },
       "Aggregation":   { "type": "string", "enum": [...] },
       "UnitFamily":    { "type": "string", "enum": [...] }
     },
     "openVocabularies": {
       "MeasuredProperty": { "canonicals": [...], "provenance": "vocabulary/measured-property.json" },
       ...
     }
   }
   ```
7. Write it deterministically (sorted keys, stable array ordering) to `ontologies/skygest-energy-vocab/build/shacl-manifest.json`.

Command: `uv run python ontologies/skygest-energy-vocab/scripts/build_type_manifest.py --out build/shacl-manifest.json`.

### 4.3 TS side: `scripts/generate-energy-profile.ts`

Model after `sync-vocabulary.ts` line-for-line:

```ts
import { Command, Flag } from "effect/unstable/cli"
import { Console, Effect, FileSystem, Path, Schema, SchemaRepresentation } from "effect"
import { runScriptMain, scriptPlatformLayer } from "../src/platform/ScriptRuntime"

// 1. Manifest contract — lives in src, imported by the script
const ClosedEnum = Schema.Struct({
  type: Schema.Literal("string"),
  enum: Schema.Array(Schema.String).pipe(Schema.minItems(1))
})
const ManifestSchema = Schema.Struct({
  $id: Schema.String,
  generatedAt: Schema.String,
  sourceCommit: Schema.String,
  shapesFileHash: Schema.String,
  facetKeys: Schema.Array(Schema.String).pipe(Schema.minItems(1)),
  requiredFacetKeys: Schema.Array(Schema.String),
  closedEnums: Schema.Record({ key: Schema.String, value: ClosedEnum }),
  openVocabularies: Schema.Record({
    key: Schema.String,
    value: Schema.Struct({ canonicals: Schema.Array(Schema.String), provenance: Schema.String })
  })
})
```

Handler (inside `Effect.fn("generate-energy-profile.run")`):

1. `fs.readFileString(options.manifest)` → `Schema.decodeUnknownSync(ManifestSchema)(JSON.parse(...))`. Any drift in the Python-side shape fails here with a typed error — this is the "Effect-integrated" moment that Approach A cannot provide.
2. For each entry in `closedEnums`, build a runtime schema: `const S = Schema.Literals(entry.enum as const)`, then feed `S.ast` into `SchemaRepresentation.fromAST` → `toMultiDocument` → `toCodeDocument`. Take `codeDoc.codes[0].runtime` and `codeDoc.codes[0].Type` as the emitted strings; accumulate `codeDoc.artifacts` for imports.
3. For the tuple/open-vocab extras, hand-emit:
   ```ts
   `export const FACET_KEYS = ${JSON.stringify(manifest.facetKeys)} as const`
   `export type FacetKey = typeof FACET_KEYS[number]`
   `export const REQUIRED_FACET_KEYS = ${JSON.stringify(manifest.requiredFacetKeys)} as const`
   `export const isRequiredFacetKey: Predicate.Refinement<FacetKey, RequiredFacetKey> = (k): k is RequiredFacetKey => REQUIRED_FACET_KEYS.includes(k as RequiredFacetKey)`
   ```
4. Assemble the final file with a provenance header:
   ```ts
   // AUTO-GENERATED from skygest-energy-vocab
   // source: https://skygest.dev/vocab/energy/manifest/v1
   // sourceCommit: <sha>
   // shapesFileHash: sha256:<hex>
   // generator: scripts/generate-energy-profile.ts
   // Do not edit by hand. Run `bun run gen:energy-profile` to regenerate.
   ```
5. `fs.writeFileString(options.output, rendered)` to `src/domain/generated/energyVariableProfile.ts`.
6. Flags: `--manifest` (defaults to `references/energy-profile/shacl-manifest.json`), `--output` (defaults to the generated path), `--check` (read-only mode that diffs against the existing file and exits non-zero if they differ — same as `git diff --exit-code` but self-contained and usable locally without git).

Register as a Bun script in `package.json`: `"gen:energy-profile": "bun run scripts/generate-energy-profile.ts"`.

### 4.4 Where does the manifest live?

Two options:

- **4.4a** Commit the manifest to `skygest-cloudflare` under `references/energy-profile/shacl-manifest.json`. `sync-vocabulary.ts` already does this for vocabulary files (it copies from the ontology repo into `references/vocabulary/`). Extending it with a new facet is the smallest possible change and keeps `skygest-cloudflare` self-contained — CI does not need Python.
- **4.4b** Publish the manifest as a GitHub Release asset from the ontology repo and pin by URL + hash.

**Recommendation: 4.4a**. It preserves the existing cross-repo sync model, avoids any Python in the skygest-cloudflare CI lane, and lets the ontology repo do its own `uv run pytest` + drift checks in its own CI.

## 5. CI/CD integration

### 5.1 skygest-cloudflare (`.github/workflows/ci.yml`)

Add a step to the existing `typecheck` job, directly below the `cf:types` verification at lines 29–32:

```yaml
      - name: Verify generated energy profile
        run: |
          bun run gen:energy-profile
          git diff --exit-code -- src/domain/generated/energyVariableProfile.ts references/energy-profile/shacl-manifest.json
```

This is an intentional copy of the `cf:types` idiom: run the generator, fail if it changed anything on disk. No new actions, no Python toolchain, no extra checkout. The generator itself runs via Bun which is already installed via `oven-sh/setup-bun@v2`.

### 5.2 ontology_skill repo

The ontology repo should have its own workflow that, on push to `main` or PR, runs:

```yaml
- uses: astral-sh/setup-uv@v3
- run: uv sync --group dev
- run: uv run python ontologies/skygest-energy-vocab/scripts/build_type_manifest.py \
         --out ontologies/skygest-energy-vocab/build/shacl-manifest.json
- run: git diff --exit-code -- ontologies/skygest-energy-vocab/build/shacl-manifest.json
- run: uv run pytest ontologies/skygest-energy-vocab/tests/
```

This gives the ontology side its own drift check, so when a shape changes the ontology PR itself is the one that fails if the committed manifest is stale — you never have a situation where skygest-cloudflare CI fails because of an ontology change that slipped through.

### 5.3 Cross-repo hand-off

`sync-vocabulary.ts` already follows the pattern: Python writes to `ontologies/skygest-energy-vocab/data/vocabulary/*.json`, a dev runs `bun run sync:vocab --apply` in skygest-cloudflare to pull the files into `references/vocabulary/`, commits the copy, PR lands. The new manifest uses the same flow with a second destination path. No additional infrastructure needed.

## 6. Migration path

**Phase 1 — introduce the manifest without breaking anything (no behaviour change).**
1. Write `build_type_manifest.py` in the ontology repo. Emit the manifest at `ontologies/skygest-energy-vocab/build/shacl-manifest.json`. Commit it.
2. Add a pytest that re-runs the generator in-memory and asserts the committed manifest matches byte-for-byte (drift check on the ontology side).
3. Extend `sync-vocabulary.ts` to also copy the manifest into `references/energy-profile/`. Run `bun run sync:vocab --apply`. Commit.

**Phase 2 — introduce the TS generator producing an equivalent file.**
4. Write `scripts/generate-energy-profile.ts`. Make it emit to `src/domain/generated/energyVariableProfile.ts` — **not** yet touching the existing `src/domain/profile/energyVariableProfile.ts`.
5. Add a `test/generated/energyVariableProfile.test.ts` that imports **both** files and asserts `FACET_KEYS`, `REQUIRED_FACET_KEYS`, `StatisticTypeMembers`, `AggregationMembers`, `UnitFamilyMembers` are deeply equal. This catches any semantic drift between the hand file and the generated file.
6. Add `bun run gen:energy-profile` to `package.json` and wire the CI drift check.

**Phase 3 — cutover.**
7. Delete `src/domain/profile/energyVariableProfile.ts`. Update all importers to point at `src/domain/generated/energyVariableProfile.ts`. A single codemod: `rg -l "profile/energyVariableProfile" | xargs sed -i ''  's|profile/energyVariableProfile|generated/energyVariableProfile|g'`.
8. Remove the equality test from Phase 2 step 5 (nothing to compare against). Replace with golden snapshot tests over a checked-in expected file if desired, though the manifest-drift + CI-drift checks already cover this.

**Phase 4 — retire the PoC.**
9. Keep `generate_types_from_shacl.py` as a read-only diagnostic (gate its emission behind `--print-only`) or delete it. The build script is the production path.

## 7. Open questions

1. **Should the manifest include non-closed open vocabularies, or should those stay on the JSON vocabulary files?** The current `energyVariableProfile.ts` pulls `*Canonicals` from `references/vocabulary/*.json` via `import` statements. We could keep that split (manifest is shapes-only, vocab JSON is runtime data) or unify everything into the manifest. Simpler and more auditable to keep the split, but then the generator has to emit `import ... from "../../../references/vocabulary/..."` statements and the consumer still loads JSON at runtime. Recommended: keep the split for Phase 1, evaluate consolidation later.

2. **What happens when the ontology adds a new closed-enum value?** The TS build fails at typecheck time for any exhaustive `match` over the enum — which is exactly what we want. The question is whether we want a soft landing: emit a deprecation comment in the generated file rather than hard-adding the value. Probably no — the whole point of a closed enum is that a new value is a breaking change. But we need to decide whether the ontology PR is allowed to land before skygest-cloudflare is ready to consume it. Proposed policy: tag the ontology with a SemVer, the manifest carries `$id` with the version, and skygest-cloudflare pins the version in `references/energy-profile/shacl-manifest.json`.

3. **Do we want a `Predicate.Refinement` for every enum, or just `Schema.Literals`?** `Schema.Literals([...]).is` already gives us a refinement via `Schema.is(S)`. We probably don't need to emit separate predicates — one `isStatisticType` etc. derived from the schema in a non-generated helper file is cleaner and doesn't require the generator to know about `Predicate.Refinement`.

4. **Should the generator use `toCodeDocument` or hand-emit `Schema.Literals([...] as const)`?** `toCodeDocument` is the Effect-canonical path but its output for a single `Literals` schema is roughly `Schema.Union([Schema.Literal("stock"), Schema.Literal("flow"), ...])`, which is more verbose than `Schema.Literals([...] as const)` and loses the nice tuple-literal ergonomics. For **one-off closed enums**, hand-emitting `Schema.Literals` is probably clearer; `toCodeDocument` earns its keep when the shapes get more complex (Structs, nested unions, refinements). Proposed: start with hand-emitted `Schema.Literals` for Phase 2, adopt `toCodeDocument` in Phase 3+ when we start generating `EnergyVariableShape` itself (Struct with cross-facet constraints).

5. **Python version in ontology CI.** Already pinned to `>=3.12` in `CLAUDE.md`. No change needed.

6. **Breaking-change detection across versions.** Not in scope for v1, but worth flagging: `robot diff` on the shapes file would give us a structural diff between two versions of the manifest, and we could gate with "if any `closedEnums.*.enum` lost a value, block the PR." That's a Phase 4+ concern.

---

## Anchor citations (all under `.reference/effect/`)

- `packages/effect/src/SchemaRepresentation.ts:1-104` — module overview and `toCodeDocument` in task list
- `packages/effect/src/SchemaRepresentation.ts:2178-2250` — `Code`, `Artifact`, `CodeDocument` types
- `packages/effect/src/SchemaRepresentation.ts:2288-2333` — `toCodeDocument` implementation
- `packages/effect/src/SchemaRepresentation.ts:2898-2927` — `fromJsonSchemaDocument` / `fromJsonSchemaMultiDocument`
- `packages/effect/src/Schema.ts:3491-3550` — `Literals` interface + constructor
- `packages/effect/src/SchemaAST.ts:1044-1104` — `LiteralValue`, `Literal` AST node
- `packages/effect/src/FileSystem.ts:158,243,359` — `makeDirectory`, `readFileString`, `writeFileString`
- `packages/effect/src/unstable/cli/Command.ts:1-80` — `Command.make` signature and imports (FileSystem/Path via Layer)
- `scripts/` — Effect's internal build scripts are plain `.mjs`; confirmation that build-tooling does not need `unstable/cli`

## Anchor citations in skygest-cloudflare

- `scripts/sync-vocabulary.ts:1-17` — canonical example of the `effect/unstable/cli` + `FileSystem`/`Path` pattern this generator should clone
- `scripts/generate-worker-types.ts:1-201` — canonical example of the "write file then `git diff --exit-code` in CI" drift pattern
- `src/platform/ScriptRuntime.ts` — `scriptPlatformLayer`, `runScriptMain`, Bun-based runtime that every script uses
- `.github/workflows/ci.yml:29-32` — the existing `cf:types` drift check this report proposes to mirror
- `src/domain/profile/energyVariableProfile.ts` — the current hand-maintained file (note: **not** under `generated/`; the `generated/` dir is empty)
