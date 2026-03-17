# BUG: rlm sub-delegation JSON parse error on backtick characters

**Type:** bug
**Priority:** 2 (medium)
**Status:** open
**Created:** 2026-02-28
**Related:** docs/issues/001-rlm-prefill-error.md

## Summary

When using `claude-sonnet-4-6` with `claude-haiku-4-5-20251001` sub-delegation,
the RLM enters an infinite error loop where sub-delegated `llm_query` calls fail
with a JSON parse error on backtick characters.

## Error

```
Error: SandboxError: Error: Failed to parse JSON: JSON Parse error: Unrecognized token '`'
    at KIB (/$bunfs/root/rlm:308:1303)
    at Scheduler.runInternal (/$bunfs/root/rlm:310:2781)
```

## Reproduction

```bash
rlm \
  --provider anthropic \
  --model claude-sonnet-4-6 \
  --sub-model claude-haiku-4-5-20251001 \
  --sub-delegation-enabled \
  --max-iterations 20 \
  --input "data=/path/to/file.txt" \
  "Analyze this data and produce a technical output with code examples"
```

## Observed Behavior

1. Top-level agent reads files successfully (iterations 1-2)
2. Agent calls `llm_query()` for sub-delegation
3. Sub-model returns response containing backtick characters (markdown code blocks)
4. Bridge protocol fails to parse the response as JSON
5. Agent retries with different escaping strategies but keeps hitting same error
6. All iterations consumed on retries, no output produced
7. `__vars` state is also lost between iterations (likely IPC frame overflow)

## Root Cause

**Filed as:** https://github.com/mepuka/recursive-llm/issues/14

Traced to `JsonSchemaValidator.ts:168` called from `Scheduler.ts:1185`.

When `llm_query()` is called with `responseFormat` (requesting JSON), the host
calls `parseAndValidateJson()` with `strict: true`. In strict mode, fence-stripping
stages 2a/2b are **skipped** — only the full-fence stage 1 runs. When the
sub-model wraps JSON in markdown fences or adds prose with backticks, `JSON.parse()`
fails on the backtick character.

**The bug is NOT in the IPC/bridge serialization layer** (which uses structured
objects via `Bun.spawn` IPC). The bug is that `parseAndValidateJson` with
`strict: true` doesn't strip markdown fences before parsing.

Fix: enable fence extraction in strict mode (`JsonSchemaValidator.ts`).

## Environment

- rlm version: 0.0.0 (recursive-llm)
- Provider: anthropic
- Models: claude-sonnet-4-6 / claude-haiku-4-5-20251001
- Platform: macOS Darwin 25.2.0

## Workaround

Use `--disable-sub-delegation` to avoid the bridge protocol:

```bash
rlm \
  --provider anthropic \
  --model claude-sonnet-4-6 \
  --disable-sub-delegation \
  --max-iterations 20 \
  --input "data=/path/to/file.txt" \
  "Analyze this data"
```
