# ROBOT Template Preflight

**Referenced by:** `ontology-architect`, `ontology-validator`.

ROBOT templates are the preferred way to author repetitive class and
property axioms in this monorepo. They are also where silent mistakes
concentrate — a missing required cell or an unresolved CURIE emits a
valid-looking TTL with silently wrong content. Always preflight before
running `robot template`.

## 1. What a ROBOT template is

A TSV (or CSV) where:

- **Row 1** is the header: human-readable column names.
- **Row 2** is the template-string row: ROBOT directives that declare how
  each cell maps to an axiom.
- **Rows 3+** are data rows.

Example (instrument families):

```
ID	Label	Parent	Definition
ID	LABEL	SC %	A IAO:0000115
ex:Violin	violin	ex:StringInstrument	A bowed string instrument with four strings…
ex:Viola	viola	ex:StringInstrument	A bowed string instrument slightly larger than a violin…
```

Key directives:

- `ID` — the subject CURIE.
- `LABEL` — populates `rdfs:label`.
- `SC %` — "subclass-of %" where `%` is substituted with the cell value.
- `A IAO:0000115` — "annotation property IAO:0000115 (definition)".
- `SPLIT=|` — split cell value on `|` to produce multi-value axioms.

See [ROBOT template docs](http://robot.obolibrary.org/template) for the
full directive list.

## 2. Preflight checklist

Run these checks on every template TSV before `robot template`:

- [ ] **Headers match directives.** Column count, names, and order are
      consistent; directive row is well-formed.
- [ ] **Required cells present.** For every `SC %`, `A %`, `EC %`, the
      cell is not empty (or is empty intentionally).
- [ ] **CURIEs resolve.** Every CURIE in data rows resolves via the
      project's prefix map (`namespaces.json`).
- [ ] **No stray commas or tabs** in cells that would be interpreted as
      extra columns.
- [ ] **SPLIT character matches.** If using `SPLIT=|`, no `|` appears
      inside a cell intended as a single value.
- [ ] **Language tags correct.** String cells that need `@en` tags have
      them; `LABEL` column defaults to a language tag via the template
      directive.
- [ ] **No URL scheme mismatches.** `http://` vs `https://` must match
      the ontology's declared base.
- [ ] **Parent terms exist.** Run `runoak info` for every class in the
      `SC %` column (or the reasoner will classify as equivalent-to-Thing
      after template run).
- [ ] **Merge mode explicit.** `robot template --merge-before` vs
      `--merge-after` vs neither is a load-bearing decision; pick
      intentionally.

## 3. Preflight helper script (Python)

Reference implementation (expanded in worked examples):

```python
"""Preflight a ROBOT template TSV before `robot template`."""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

CURIE_RE = re.compile(r"^([A-Za-z][\w-]*):([\w/.\-#]+)$")

def load_prefix_map(path: Path) -> dict[str, str]:
    import json
    return json.loads(path.read_text())

def preflight(tsv_path: Path, prefix_map: dict[str, str]) -> int:
    errors: list[str] = []
    with tsv_path.open(newline="") as fh:
        reader = csv.reader(fh, delimiter="\t")
        header = next(reader)
        directives = next(reader)
        for i, row in enumerate(reader, start=3):
            for j, (col, cell) in enumerate(zip(header, row, strict=True)):
                directive = directives[j]
                if directive.endswith("%") and not cell.strip():
                    errors.append(f"row {i}: column {col} is empty but directive is {directive!r}")
                # CURIE resolution
                if CURIE_RE.match(cell):
                    prefix = cell.split(":", 1)[0]
                    if prefix not in prefix_map:
                        errors.append(f"row {i}: unknown prefix {prefix!r} in cell {cell!r}")
    for err in errors:
        print(f"FAIL  {err}", file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    prefix_map = load_prefix_map(Path(".claude/skills/_shared/namespaces.json"))
    sys.exit(preflight(Path(sys.argv[1]), prefix_map))
```

Drop this into `ontologies/{name}/scripts/preflight_template.py` when
a new template is added.

## 4. Common failure patterns

### 4.1 Empty cell under `SC %`

Symptom: the template emits no `SubClassOf` axiom for that row. No error
from ROBOT. The new class becomes a top-level class (equivalent to
`owl:Thing`).

Fix: either provide a parent, or use `SC %{1}` to make the substitution
optional, or omit the column entirely.

### 4.2 Unresolved CURIE

Symptom: the CURIE is emitted as a literal string, or is resolved against
an unintended prefix. Classification silently wrong.

Fix: run the preflight script; ensure every prefix appears in
`namespaces.json`.

### 4.3 `SPLIT=|` misuse

Symptom: a cell intended as a single value contains a `|` character;
ROBOT splits it into two axioms.

Fix: escape or remove the `|`; use a different split character if the
cell value legitimately contains `|`.

### 4.4 Language tag on wrong column

Symptom: `rdfs:label` has no language tag; `skos:definition` has `@en`
but other annotations don't.

Fix: set `LABEL` directive with `@en`; apply `A IAO:0000115@en` to the
definition column explicitly.

### 4.5 `merge` mode mismatch

Symptom: `robot template --merge-before` overwrites axioms from the
edit file; or omitting merge flags produces a file that is not a
superset.

Fix: for additive templates, use `--merge-after` (template output
merged after the edit file). For replacement, use `--merge-before` and
confirm the intent in `docs/axiom-plan.yaml`.

## 5. Retry gate

After `robot template` runs, validate:

```bash
.local/bin/robot template \
  --template ontologies/{name}/templates/{name}-template.tsv \
  --output /tmp/template-out.ttl

# Assert zero CURIE errors
grep -E "^(ERROR|FAIL)" /tmp/template-out.log

# Merge into edit file, reason, report
.local/bin/robot merge --input ontologies/{name}/{name}-edit.ttl --input /tmp/template-out.ttl --output /tmp/merged.ttl
.local/bin/robot reason --input /tmp/merged.ttl --output /tmp/reasoned.ttl
.local/bin/robot report --input /tmp/reasoned.ttl --output /tmp/report.tsv --fail-on ERROR
```

Failure routes to `ontology-architect` with `failure_type: robot_template_error`
per [`iteration-loopbacks.md`](iteration-loopbacks.md).

## 6. Worked examples

- [`worked-examples/ensemble/architect.md`](worked-examples/ensemble/architect.md) — instrument-family template with preflight catching an unresolved CURIE.
- [`worked-examples/microgrid/architect.md`](worked-examples/microgrid/architect.md) — ChargeState value-partition template.

## 7. References

- [ROBOT template documentation](http://robot.obolibrary.org/template)
- [ROBOT GitHub templates page](https://github.com/ontodev/robot/blob/master/docs/template.md) — canonical directive reference.
