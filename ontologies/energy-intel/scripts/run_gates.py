"""Run robot merge / reason / report gates per module + top-level.

Outputs per-module logs under ``validation/`` and a summary to stdout.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DIR = PROJECT_ROOT / "validation"
VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

ROBOT = Path("/Users/pooks/Dev/ontology_skill/.local/bin/robot")

MODULES = [
    ("agent", PROJECT_ROOT / "modules" / "agent.ttl"),
    ("media", PROJECT_ROOT / "modules" / "media.ttl"),
    ("measurement", PROJECT_ROOT / "modules" / "measurement.ttl"),
    ("data", PROJECT_ROOT / "modules" / "data.ttl"),
    ("top-level", PROJECT_ROOT / "energy-intel.ttl"),
]


def run(cmd: list[str], log_path: Path) -> int:
    print(f"  $ {' '.join(cmd)}")
    with log_path.open("w") as f:
        proc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, check=False)  # noqa: S603  # cmd is always a fixed list of strings built above; no shell interpolation.
    return proc.returncode


def gate_module(name: str, source: Path) -> dict[str, object]:
    merged = VALIDATION_DIR / f"merged-{name}.ttl"
    reasoned = VALIDATION_DIR / f"reasoned-{name}.ttl"
    report_tsv = VALIDATION_DIR / f"report-{name}.tsv"
    merge_log = VALIDATION_DIR / f"merge-{name}.log"
    reason_log = VALIDATION_DIR / f"reason-{name}.log"
    report_log = VALIDATION_DIR / f"report-{name}.log"

    result = {"module": name, "source": str(source)}

    catalog = PROJECT_ROOT / "catalog-v001.xml"
    # ---- merge ----
    rc = run(
        [
            str(ROBOT),
            "merge",
            "--catalog",
            str(catalog),
            "--input",
            str(source),
            "--output",
            str(merged),
        ],
        merge_log,
    )
    result["merge_exit"] = rc
    if rc != 0:
        result["status"] = "merge_failed"
        return result

    # ---- reason ----
    rc = run(
        [
            str(ROBOT),
            "reason",
            "--reasoner",
            "hermit",
            "--input",
            str(merged),
            "--output",
            str(reasoned),
        ],
        reason_log,
    )
    result["reason_exit"] = rc
    if rc != 0:
        result["status"] = "reasoner_failed"
        return result

    # ---- report ----
    rc = run(
        [
            str(ROBOT),
            "report",
            "--input",
            str(merged),
            "--output",
            str(report_tsv),
        ],
        report_log,
    )
    result["report_exit"] = rc

    # Count severity levels
    if report_tsv.exists():
        errors = warns = infos = 0
        with report_tsv.open() as f:
            next(f, None)  # header
            for line in f:
                level = line.split("\t", 1)[0]
                if level == "ERROR":
                    errors += 1
                elif level == "WARN":
                    warns += 1
                elif level == "INFO":
                    infos += 1
        result["report_errors"] = errors
        result["report_warns"] = warns
        result["report_infos"] = infos

    result["status"] = "ok"
    return result


def main() -> None:
    all_results = []
    for name, source in MODULES:
        print(f"\n=== gate: {name} ({source.name}) ===")
        all_results.append(gate_module(name, source))

    print("\n\n=== SUMMARY ===")
    any_bad = False
    for r in all_results:
        status = r.get("status", "?")
        errs = r.get("report_errors", "n/a")
        warns = r.get("report_warns", "n/a")
        infos = r.get("report_infos", "n/a")
        merge_exit = r.get("merge_exit", "?")
        reason_exit = r.get("reason_exit", "?")
        print(
            f"  {r['module']:<12} status={status:<14} "
            f"merge_exit={merge_exit} reason_exit={reason_exit} "
            f"errors={errs} warns={warns} infos={infos}"
        )
        if status != "ok":
            any_bad = True
    sys.exit(1 if any_bad else 0)


if __name__ == "__main__":
    main()
