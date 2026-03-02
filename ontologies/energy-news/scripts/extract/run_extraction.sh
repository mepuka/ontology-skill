#!/usr/bin/env bash
# Run effect-langextract on a corpus with one or more models.
#
# Usage:
#   ./scripts/extract/run_extraction.sh [test|full] [model_spec...]
#
# Examples:
#   ./scripts/extract/run_extraction.sh test                          # test set, default model
#   ./scripts/extract/run_extraction.sh test openai:gpt-4.1-nano      # test set, specific model
#   ./scripts/extract/run_extraction.sh test openai:gpt-4.1-nano openai:gpt-4o-mini gemini:gemini-2.5-flash
#   ./scripts/extract/run_extraction.sh full openai:gpt-4.1-nano      # full corpus
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
LANGEXTRACT_DIR="/Users/pooks/Dev/effect-langextract"
LANGEXTRACT_BIN="$LANGEXTRACT_DIR/dist/src/main.js"
EXAMPLES_FILE="$SCRIPT_DIR/extraction-examples.json"

# Defaults
MODE="${1:-test}"
shift || true

# Default models if none specified
if [[ $# -eq 0 ]]; then
    MODELS=("openai:gpt-4.1-nano")
else
    MODELS=("$@")
fi

# Input file based on mode
if [[ "$MODE" == "test" ]]; then
    INPUT_FILE="$PROJECT_DIR/data/test-set-50.ndjson"
    BATCH_LENGTH=10
    BATCH_CONCURRENCY=2
    PROVIDER_CONCURRENCY=4
elif [[ "$MODE" == "full" ]]; then
    INPUT_FILE="$PROJECT_DIR/data/corpus-succeeded.ndjson"
    BATCH_LENGTH=20
    BATCH_CONCURRENCY=4
    PROVIDER_CONCURRENCY=8
else
    echo "Unknown mode: $MODE (use 'test' or 'full')" >&2
    exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Input file not found: $INPUT_FILE" >&2
    echo "For test mode, run: uv run python scripts/extract/build_test_set.py" >&2
    exit 1
fi

if [[ ! -f "$EXAMPLES_FILE" ]]; then
    echo "Examples file not found: $EXAMPLES_FILE" >&2
    echo "Run RLM first or copy examples: cp /tmp/extraction-examples.json $EXAMPLES_FILE" >&2
    exit 1
fi

if [[ ! -f "$LANGEXTRACT_BIN" ]]; then
    echo "effect-langextract not found at $LANGEXTRACT_BIN" >&2
    echo "Build it: cd $LANGEXTRACT_DIR && pnpm build" >&2
    exit 1
fi

PROMPT="Extract energy sector entities and relationships from this article. \
Entity classes: Organization, RegulatoryBody, GeographicEntity, GridZone, \
EnergyProject, PowerPlant, RenewableInstallation, EnergyTechnology, \
PolicyInstrument, CapacityMeasurement, PriceDataPoint, EnergyEvent, Person. \
For relationships, use extractionClass 'Relationship' with attributes \
{relationshipType, subject, object}. ONLY use these relationshipType values: \
operatedBy, locatedIn, hasCapacity, hasStatus, jurisdiction, developedThrough, \
hasTechnology, mentionsOrganization. Do NOT invent other relationship types. \
Extract ALL mentions of organizations, geographic entities, projects, \
technologies, policies, capacity measurements, and prices. Include charInterval positions."

ARTICLE_COUNT=$(wc -l < "$INPUT_FILE" | tr -d ' ')
echo "=== Energy News Extraction ==="
echo "Mode: $MODE"
echo "Input: $INPUT_FILE ($ARTICLE_COUNT articles)"
echo "Examples: $EXAMPLES_FILE"
echo "Models: ${MODELS[*]}"
echo ""

OUTPUT_DIR="$PROJECT_DIR/data/extraction-results"
mkdir -p "$OUTPUT_DIR"

for provider_model in "${MODELS[@]}"; do
    provider="${provider_model%%:*}"
    model="${provider_model##*:}"
    output_path="$OUTPUT_DIR/${MODE}-${provider}-${model}.jsonl"

    echo "--- Running: $provider/$model ---"
    echo "  Output: $output_path"

    bun "$LANGEXTRACT_BIN" extract \
        --input "$INPUT_FILE" \
        --input-format jsonl \
        --text-field text \
        --id-field url \
        --context-field domain \
        --context-field date \
        --examples-file "$EXAMPLES_FILE" \
        --prompt "$PROMPT" \
        --provider "$provider" \
        --model-id "$model" \
        --output jsonl \
        --output-path "$output_path" \
        --max-char-buffer 8000 \
        --batch-length "$BATCH_LENGTH" \
        --batch-concurrency "$BATCH_CONCURRENCY" \
        --provider-concurrency "$PROVIDER_CONCURRENCY" \
        --extraction-passes 1

    result_count=$(wc -l < "$output_path" 2>/dev/null | tr -d ' ')
    echo "  Done: $result_count results written"
    echo ""
done

echo "=== All extractions complete ==="
echo "Results in: $OUTPUT_DIR/"
ls -lh "$OUTPUT_DIR/"*.jsonl 2>/dev/null
