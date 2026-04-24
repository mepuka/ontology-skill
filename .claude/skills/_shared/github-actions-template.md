# GitHub Actions CI Template

**Referenced by:** `ontology-validator` (CI-level execution of its
L0–L6 gates), `ontology-curator` (release-infra change category).
**Related:** [`owl-profile-playbook.md`](owl-profile-playbook.md),
[`robot-template-preflight.md`](robot-template-preflight.md),
[`mapping-evaluation.md`](mapping-evaluation.md),
[`provenance-and-publication.md`](provenance-and-publication.md).

CI enforces the same gates the human validator runs locally. The skill
pipeline is not enforced only at review time — every commit on a
protected branch runs the full gate pack. This file gives a template
CI workflow that implements the validator's `L0 → L1 → L2 → L4 → L3 →
L4.5 → L5.5 → L6` command order, plus the mapping-set gates and the
release-publication check.

## 1. What CI must do

| Gate | Tool | Owner skill (on failure) | Failure class |
|---|---|---|---|
| Routing-validator | `scripts/validate_description_routing.py` | governance | `routing_collision` |
| Python lint | `ruff check .` | code | — |
| Python format | `ruff format --check .` | code | — |
| Python types | `mypy src/` | code | — |
| L0: Turtle syntax | `robot validate` | architect | `syntax` |
| L0: profile | `robot validate-profile` | architect | `profile_violation` |
| L0: import closure | `robot merge --collapse-import-closure` | curator | `stale_import` |
| L1: reasoner | `robot reason --reasoner {ELK|HermiT}` | architect | `unsatisfiable_class` |
| L2: ROBOT report | `robot report --fail-on ERROR` | source skill | severity ERROR |
| L3: SHACL | `pyshacl --fail-on Violation` | architect | `shacl_violation` |
| L4: CQ suite | `robot verify --queries tests/` | architect / sparql | per CQ |
| L4.5: CQ manifest | `scripts/cq_manifest_check.py` | requirements / sparql | `missing_cq_link` / `sparql_shape` |
| L5.5: anti-patterns | `robot query` pack | conceptualizer / architect | `anti_pattern` |
| Mapping: SSSOM validate | `sssom validate` | mapper | `missing_semapv` |
| Mapping: clique | `robot query` clique-check | mapper | `mapping_clique` |
| Release: publication check | `scripts/publication_check.py` | curator | `release_gate` |

Each gate corresponds to a step in the skill Core Workflows; see the
Level 8 routing table in
[`ontology-validator/SKILL.md`](../ontology-validator/SKILL.md).

## 2. Template workflow

Paste this into `.github/workflows/ontology-ci.yml`. Comment and
uncomment per-ontology blocks as projects are added.

```yaml
name: ontology-ci

on:
  push:
    branches: [main, refactor/**]
  pull_request:

jobs:
  lint-and-types:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --group dev
      - name: Routing validator
        run: uv run python scripts/validate_description_routing.py
      - name: Ruff lint
        run: uv run ruff check .
      - name: Ruff format (check-only)
        run: uv run ruff format --check .
      - name: Mypy
        run: uv run mypy src/

  ontology-gates:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        ontology: [ensemble, microgrid, skygest-energy-vocab]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - uses: actions/setup-java@v4
        with: {distribution: temurin, java-version: 17}
      - name: Install ROBOT
        run: |
          mkdir -p .local/bin
          curl -L https://github.com/ontodev/robot/releases/latest/download/robot.jar \
            -o .local/bin/robot.jar
          cat > .local/bin/robot <<'EOF'
          #!/usr/bin/env bash
          exec java -jar "$(dirname "$0")/robot.jar" "$@"
          EOF
          chmod +x .local/bin/robot
          echo "$PWD/.local/bin" >> "$GITHUB_PATH"
      - name: Sync deps
        run: uv sync --group dev

      # ── Validator L0 ───────────────────────────────────────────────
      - name: L0a — Turtle syntax
        run: robot validate --input ontologies/${{ matrix.ontology }}/${{ matrix.ontology }}.ttl
      - name: L0b — Merge + profile validate
        run: |
          mkdir -p ontologies/${{ matrix.ontology }}/validation
          robot merge \
            --input ontologies/${{ matrix.ontology }}/${{ matrix.ontology }}.ttl \
            --input ontologies/${{ matrix.ontology }}/imports/*.ttl \
            --output ontologies/${{ matrix.ontology }}/validation/merged.ttl
          robot validate-profile \
            --profile $(uv run python scripts/read_declared_profile.py --ontology ${{ matrix.ontology }}) \
            --input ontologies/${{ matrix.ontology }}/validation/merged.ttl \
            --output ontologies/${{ matrix.ontology }}/validation/profile-validate.txt

      # ── Validator L1 ───────────────────────────────────────────────
      - name: L1 — Reasoner (profile-matched)
        run: |
          REASONER=$(uv run python scripts/read_declared_reasoner.py --ontology ${{ matrix.ontology }})
          robot reason --reasoner "$REASONER" \
            --input ontologies/${{ matrix.ontology }}/validation/merged.ttl \
            --output ontologies/${{ matrix.ontology }}/validation/reasoned.ttl \
            --dump-unsatisfiable ontologies/${{ matrix.ontology }}/validation/unsat.txt
          test ! -s ontologies/${{ matrix.ontology }}/validation/unsat.txt

      # ── Validator L2 ───────────────────────────────────────────────
      - name: L2 — ROBOT report
        run: |
          robot report \
            --input ontologies/${{ matrix.ontology }}/validation/merged.ttl \
            --fail-on ERROR \
            --output ontologies/${{ matrix.ontology }}/validation/robot-report.tsv

      # ── Validator L4 (CQ) ──────────────────────────────────────────
      - name: L4 — CQ verify
        run: |
          robot verify \
            --input ontologies/${{ matrix.ontology }}/validation/reasoned.ttl \
            --queries ontologies/${{ matrix.ontology }}/tests/ \
            --output-dir ontologies/${{ matrix.ontology }}/test-results/

      # ── Validator L3 (SHACL) ───────────────────────────────────────
      - name: L3 — SHACL
        run: |
          if [ -d ontologies/${{ matrix.ontology }}/shapes ]; then
            uv run pyshacl \
              -s ontologies/${{ matrix.ontology }}/shapes/${{ matrix.ontology }}-shapes.ttl \
              --inference rdfs \
              -f human \
              --fail-on Violation \
              ontologies/${{ matrix.ontology }}/${{ matrix.ontology }}.ttl
          fi

      # ── Validator L4.5 (manifest audit) ────────────────────────────
      - name: L4.5 — CQ manifest audit
        run: |
          uv run python scripts/cq_manifest_check.py \
            --manifest ontologies/${{ matrix.ontology }}/tests/cq-test-manifest.yaml \
            --ontology ontologies/${{ matrix.ontology }}/${{ matrix.ontology }}.ttl \
            --axiom-plan ontologies/${{ matrix.ontology }}/docs/axiom-plan.yaml \
            --out ontologies/${{ matrix.ontology }}/validation/cq-manifest-audit.json

      # ── Validator L5.5 (anti-pattern pack) ─────────────────────────
      - name: L5.5 — Anti-pattern probes
        run: |
          mkdir -p ontologies/${{ matrix.ontology }}/validation/anti-pattern-results
          for probe in sparql/anti-patterns/*.sparql; do
            name=$(basename "$probe" .sparql)
            robot query \
              --input ontologies/${{ matrix.ontology }}/validation/merged.ttl \
              --query "$probe" \
              --output ontologies/${{ matrix.ontology }}/validation/anti-pattern-results/${name}.csv
          done
          uv run python scripts/assert_anti_pattern_zero.py \
            --results-dir ontologies/${{ matrix.ontology }}/validation/anti-pattern-results \
            --review ontologies/${{ matrix.ontology }}/docs/anti-pattern-review.md

      # ── Mapping gates ──────────────────────────────────────────────
      - name: Mapping — SSSOM validate + clique check
        run: |
          if ls ontologies/${{ matrix.ontology }}/mappings/*.sssom.tsv 2>/dev/null; then
            for f in ontologies/${{ matrix.ontology }}/mappings/*.sssom.tsv; do
              uv run sssom validate "$f"
            done
            uv run python scripts/validate_sssom.py --clique-check \
              ontologies/${{ matrix.ontology }}/mappings/
          fi

      # ── Artifacts + summary ───────────────────────────────────────
      - name: Upload validation artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.ontology }}-validation
          path: ontologies/${{ matrix.ontology }}/validation/
          retention-days: 30
```

## 3. Release-only gate (Step 5.6 publication check)

Add a release-publication job that runs on tagged commits only. This
mirrors `ontology-curator` Step 5.6 and consumes
[`provenance-and-publication.md § 5`](provenance-and-publication.md).

```yaml
  publication-check:
    if: startsWith(github.ref, 'refs/tags/release-')
    needs: ontology-gates
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --group dev
      - name: Publication metadata check
        run: |
          ONTO=$(echo "${{ github.ref_name }}" | awk -F- '{print $2}')
          VER=$(echo  "${{ github.ref_name }}" | awk -F- '{print $3}')
          uv run python scripts/publication_check.py \
            --ontology "$ONTO" --version "$VER" \
            --out "ontologies/$ONTO/release/${VER}-publication-check.yaml"
          uv run python scripts/assert_publication_check_passes.py \
            --check "ontologies/$ONTO/release/${VER}-publication-check.yaml"
```

The `assert_publication_check_passes.py` helper parses the YAML from
[`provenance-and-publication.md § 5`](provenance-and-publication.md)
and exits non-zero on any `false` row without a matching `waivers` row.

## 4. Stop-on-ERROR semantics

Each step uses GitHub's implicit `continue-on-error: false`. The first
ERROR-severity failure halts the job — subsequent gates do not run.
This matches the validator's L0 → L1 rule: reasoning on an unresolved
closure is misleading, so CI must stop at L0 failure.

If a project needs to collect multiple gate results before failing
(e.g., release PR reviews), split the gates into separate jobs with
`needs:` edges and `if: always()` uploads. Do NOT set
`continue-on-error: true` on an individual gate — the validator rule
is not "run them all and look"; it is "stop on first ERROR."

## 5. Secrets and caches

- No secrets required for the public gate pack.
- ROBOT download is unauthenticated; no GitHub PAT needed.
- Cache `uv` venv via `actions/setup-uv@v3` (handles this automatically).
- Do NOT cache `ontologies/*/validation/` — caching stale validation
  results defeats the purpose.

## 6. Failure routing

When CI fails, the workflow `name:` and failing step tell the author
which gate tripped. Map back to the Level 8 routing table:

| Failing step | Owner skill |
|---|---|
| `L0a/L0b` | `ontology-architect` (syntax / profile) or `ontology-curator` (import closure) |
| `L1` | `ontology-architect` |
| `L2` | source skill of the offending axiom (trace via `robot report` columns) |
| `L3` | `ontology-architect` |
| `L4` | `ontology-architect` (axiom) or `sparql-expert` (query) — classify from the per-CQ output |
| `L4.5` | `ontology-requirements` (missing link) or `sparql-expert` (shape) |
| `L5.5` | `ontology-conceptualizer` |
| Mapping gates | `ontology-mapper` |
| `publication-check` | `ontology-curator` |

The validator worked examples
([`worked-examples/ensemble/validator.md`](worked-examples/ensemble/validator.md),
[`worked-examples/microgrid/validator.md`](worked-examples/microgrid/validator.md))
show the same routing applied to human-facing validation reports.

## 7. Running the same gates locally

Authors should run the gates locally before pushing. `just ci` (or a
Makefile equivalent) should invoke the same commands:

```makefile
# Justfile (excerpt)
ci: lint types ontology-gates

ontology-gates:
  for o in ensemble microgrid skygest-energy-vocab; do \
    just validate-ontology "$$o" ; \
  done

validate-ontology name:
  robot merge --input ontologies/{{name}}/{{name}}.ttl --input ontologies/{{name}}/imports/*.ttl --output ontologies/{{name}}/validation/merged.ttl
  robot validate-profile --profile $$(uv run python scripts/read_declared_profile.py --ontology {{name}}) --input ontologies/{{name}}/validation/merged.ttl
  robot reason --reasoner $$(uv run python scripts/read_declared_reasoner.py --ontology {{name}}) --input ontologies/{{name}}/validation/merged.ttl --dump-unsatisfiable ontologies/{{name}}/validation/unsat.txt
  robot report --input ontologies/{{name}}/validation/merged.ttl --fail-on ERROR
  uv run python scripts/cq_manifest_check.py --manifest ontologies/{{name}}/tests/cq-test-manifest.yaml --ontology ontologies/{{name}}/{{name}}.ttl
```

CI uses the same commands as the local workflow. Divergence between
local `just ci` and CI is an anti-pattern.

## 8. Anti-patterns

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Gate silently `continue-on-error` | CI green but ontology broken downstream | Remove `continue-on-error: true`; split jobs if multi-fail reporting is needed. |
| Different command between local + CI | "works on my machine" | Wrap commands in `just` / `scripts/`; CI calls the same wrapper. |
| Reasoner mismatched with profile | ELK on a DL ontology silently passes | Read declared profile + reasoner from per-ontology config. |
| Uploading reasoned graph to prod without diff | Breaking-change ships silently | Add a `robot diff` step that fails when the change log classification doesn't match. |

## 9. References

- [`ontology-validator/SKILL.md`](../ontology-validator/SKILL.md) — human execution of the same gates.
- [`provenance-and-publication.md`](provenance-and-publication.md) — Step 5.6 publication check schema.
- [GitHub Actions matrix docs](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs).
- [ROBOT CI examples](http://robot.obolibrary.org/command) — canonical invocations.
