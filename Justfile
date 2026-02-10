# Ontology Skill Workspace - Task Runner
# Usage: just <recipe>
# Requires: https://github.com/casey/just

set dotenv-load

# Default recipe
default:
    @just --list

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

# Install all dependencies (production + dev)
install:
    uv sync --group dev

# Update all dependencies
update:
    uv lock --upgrade
    uv sync --group dev

# ---------------------------------------------------------------------------
# Quality
# ---------------------------------------------------------------------------

# Run all checks (lint, typecheck, test)
check: lint typecheck test

# Lint with ruff
lint:
    uv run ruff check .

# Lint and auto-fix
fix:
    uv run ruff check --fix .
    uv run ruff format .

# Format code
fmt:
    uv run ruff format .

# Format check (no changes)
fmt-check:
    uv run ruff format --check .

# Type check with mypy
typecheck:
    uv run mypy src/

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------

# Run all tests
test *ARGS:
    uv run pytest {{ARGS}}

# Run tests with coverage
test-cov:
    uv run pytest --cov=src/ontology_skill --cov-report=html --cov-report=term

# Run only unit tests
test-unit:
    uv run pytest tests/unit/

# Run only integration tests
test-integration:
    uv run pytest tests/integration/ -m integration

# ---------------------------------------------------------------------------
# Pre-commit
# ---------------------------------------------------------------------------

# Install pre-commit hooks
hooks-install:
    uv run pre-commit install

# Run pre-commit on all files
hooks-run:
    uv run pre-commit run --all-files

# ---------------------------------------------------------------------------
# Ontology Tools
# ---------------------------------------------------------------------------

# Check ROBOT is available
robot-check:
    @which robot > /dev/null 2>&1 && robot --version || echo "ROBOT not installed. Run: just robot-install"

# Install ROBOT CLI
robot-install:
    mkdir -p {{justfile_directory()}}/.local/bin {{justfile_directory()}}/.local/share
    curl -sL https://github.com/ontodev/robot/releases/latest/download/robot.jar \
        -o {{justfile_directory()}}/.local/share/robot.jar
    curl -sL https://raw.githubusercontent.com/ontodev/robot/master/bin/robot \
        -o {{justfile_directory()}}/.local/bin/robot
    chmod +x {{justfile_directory()}}/.local/bin/robot
    @echo "ROBOT installed to .local/bin/robot"
    @echo "Add to PATH: export PATH=\"{{justfile_directory()}}/.local/bin:\$PATH\""

# Validate an ontology file
validate ONTOLOGY:
    uv run python -c "from pyshacl import validate; print('pySHACL available')"
    robot reason --reasoner ELK --input {{ONTOLOGY}}
    robot report --input {{ONTOLOGY}} --fail-on ERROR

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

# Remove all generated files
clean:
    rm -rf .mypy_cache .pytest_cache .ruff_cache htmlcov .coverage
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
