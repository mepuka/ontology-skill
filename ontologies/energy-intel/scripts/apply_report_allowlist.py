"""Filter ``validation/report-top-level.tsv`` against the upstream allow-list.

Reads ``validation/report-top-level.tsv`` and ``validation/report-allowlist.tsv``.
Emits ``validation/report-top-level-filtered.tsv`` with allow-listed rows
removed, and ``validation/report-project-errors.tsv`` keyed to remaining
ERRORs that are not upstream.

Exit 0 if zero project-origin ERRORs remain; exit 1 otherwise. This is the
CI-facing gate.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VALIDATION = PROJECT_ROOT / "validation"
REPORT = VALIDATION / "report-top-level.tsv"
ALLOWLIST = VALIDATION / "report-allowlist.tsv"
FILTERED = VALIDATION / "report-top-level-filtered.tsv"
PROJECT_ERRORS = VALIDATION / "report-project-errors.tsv"


def _load_allowlist() -> list[tuple[str, str]]:
    with ALLOWLIST.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        return [(row["rule"], row["subject_prefix"]) for row in reader]


def _row_allowed(rule: str, subject: str, allowlist: list[tuple[str, str]]) -> bool:
    return any(rule == a_rule and subject.startswith(a_prefix) for a_rule, a_prefix in allowlist)


def main() -> int:
    allowlist = _load_allowlist()

    # Headers: Level, Rule Name, Subject, Property, Value
    with (
        REPORT.open() as src,
        FILTERED.open("w") as filt,
        PROJECT_ERRORS.open("w") as proj,
    ):
        reader = csv.reader(src, delimiter="\t")
        f_writer = csv.writer(filt, delimiter="\t")
        p_writer = csv.writer(proj, delimiter="\t")

        header = next(reader)
        f_writer.writerow(header)
        p_writer.writerow(header)

        proj_error_count = 0
        filtered_count = 0
        allowed_count = 0
        for row in reader:
            if not row or len(row) < 3:
                continue
            level, rule, subject = row[0], row[1], row[2]
            if level == "ERROR" and _row_allowed(rule, subject, allowlist):
                allowed_count += 1
                continue
            f_writer.writerow(row)
            filtered_count += 1
            if level == "ERROR":
                proj_error_count += 1
                p_writer.writerow(row)

    print(f"allow-listed ERRORs suppressed: {allowed_count}")
    print(f"rows passing through filter:   {filtered_count}")
    print(f"project-origin ERRORs:         {proj_error_count}")
    return 1 if proj_error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
