# BUG: rlm assistant prefill error with claude-sonnet-4-6 and claude-haiku-4-5

**Type:** bug
**Priority:** 2 (medium)
**Status:** open
**Created:** 2026-02-28

## Summary

The `recursive-llm` (rlm) CLI tool fails when using `claude-sonnet-4-6` or
`claude-haiku-4-5-20251001` as model/sub-model because these models do not
support assistant message prefill.

## Error

```
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "This model does not support assistant message prefill. The conversation must end with a user message."
  }
}
```

## Reproduction

```bash
rlm \
  --provider anthropic \
  --model claude-sonnet-4-6 \
  --sub-model claude-haiku-4-5-20251001 \
  --sub-delegation-enabled \
  --input "file=/path/to/file.json" \
  "Analyze this file"
```

## Analysis

- rlm uses assistant message prefill internally for its code execution and
  delegation protocol
- Claude 4.5/4.6 models (sonnet-4-6, haiku-4-5) do NOT support assistant
  message prefill via the Anthropic API
- The error occurs on sub-delegated calls (depth=1+), suggesting the bridge
  protocol uses prefill
- The top-level agent (depth=0) also eventually fails after retries

## Workaround

Use older model IDs that support prefill:
- `claude-sonnet-4-5-20241022` or `claude-3-5-sonnet-20241022`
- `claude-3-5-haiku-20241022`

Or disable sub-delegation and use a single model.

## Resolution

Either:
1. rlm needs to be updated to not use assistant prefill with models that
   don't support it
2. Use compatible model IDs until rlm is updated
