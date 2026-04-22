"""Validate SKILL.md description rewrites preserve routing-relevant tokens.

Enforces invariant #4 of the 2026-04 ontology-skills refactor:

    Every token in the baseline description (except generic English words and
    boilerplate) must appear in the refactored description.

Also detects routing collisions by reporting pairs of skills whose descriptions
overlap on more than ``COLLISION_THRESHOLD`` non-generic tokens.

Usage:
    uv run python scripts/validate_description_routing.py
    uv run python scripts/validate_description_routing.py --baseline wave-0-baseline
    uv run python scripts/validate_description_routing.py --skills-dir .claude/skills
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIRS = [
    "ontology-requirements",
    "ontology-scout",
    "ontology-conceptualizer",
    "ontology-architect",
    "ontology-mapper",
    "ontology-validator",
    "ontology-curator",
    "sparql-expert",
]

# Tokens that appear in almost any description and do not carry routing signal.
GENERIC_TOKENS = frozenset(
    {
        "a",
        "an",
        "and",
        "any",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "in",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "the",
        "this",
        "to",
        "use",
        "used",
        "uses",
        "using",
        "when",
        "where",
        "while",
        "with",
        "that",
        "via",
        "which",
        "whose",
        "you",
        "your",
        "new",
        "existing",
        "user",
        "users",
        "work",
        "working",
        "manages",
        "manage",
        "handles",
        "handle",
        "runs",
        "run",
        "creates",
        "create",
        "generates",
        "generate",
        "validates",
        "validate",
        "specializes",
        "specialized",
        "expert",
        "comprehensive",
        "system",
        "ontology",
        "ontological",
        "ontologies",
        "cross",
    }
)

# Pairs of skills whose descriptions are expected to share many tokens.
# Each pair can share up to COLLISION_THRESHOLD tokens without being flagged.
COLLISION_THRESHOLD = 6

# Pairs that are expected to overlap structurally (e.g., architect + conceptualizer
# both discuss axioms). Overlap counts up to this number are acceptable for them.
EXPECTED_OVERLAP: dict[frozenset[str], int] = {
    frozenset({"ontology-architect", "ontology-conceptualizer"}): 10,
    frozenset({"ontology-validator", "ontology-architect"}): 10,
    frozenset({"ontology-mapper", "ontology-validator"}): 8,
    frozenset({"ontology-validator", "sparql-expert"}): 8,
    frozenset({"ontology-requirements", "sparql-expert"}): 8,
    frozenset({"ontology-curator", "ontology-mapper"}): 8,
    frozenset({"ontology-scout", "ontology-architect"}): 8,
    frozenset({"ontology-conceptualizer", "ontology-scout"}): 8,
}


DESC_RE = re.compile(
    r"^description:\s*>\s*\n((?:^[ \t]+.*\n)+)",
    re.MULTILINE,
)


def extract_description(text: str) -> str:
    """Extract the YAML ``description: >`` block's content, joined on whitespace."""
    match = DESC_RE.search(text)
    if not match:
        return ""
    # Strip leading indentation and join
    lines = [line.strip() for line in match.group(1).splitlines() if line.strip()]
    return " ".join(lines)


def tokenize(text: str) -> set[str]:
    """Return the set of lowercase tokens with length >= 2, excluding generics."""
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_\-]*", text.lower())
    return {t for t in tokens if len(t) >= 2 and t not in GENERIC_TOKENS}


def read_baseline_description(git_ref: str, skill: str) -> str:
    """Read the description from a given git ref for the given skill."""
    try:
        output = subprocess.run(  # noqa: S603  # args are constants
            [  # noqa: S607  # git resolved via PATH in dev env
                "git",
                "show",
                f"{git_ref}:.claude/skills/{skill}/SKILL.md",
            ],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except subprocess.CalledProcessError as exc:
        msg = f"cannot read baseline {skill}@{git_ref}: {exc.stderr.strip()}"
        raise SystemExit(f"FAIL  {msg}") from exc
    return extract_description(output)


def read_current_description(skills_dir: Path, skill: str) -> str:
    """Read the description from the working-tree SKILL.md."""
    path = skills_dir / skill / "SKILL.md"
    return extract_description(path.read_text())


def check_keyword_preservation(
    baseline: str,
    current: str,
    skill: str,
) -> list[str]:
    """Return list of baseline tokens missing from current."""
    baseline_tokens = tokenize(baseline)
    current_tokens = tokenize(current)
    missing = sorted(baseline_tokens - current_tokens)
    return [
        f"MISSING-TOKEN  {skill}: baseline token {token!r} absent from rewrite" for token in missing
    ]


def check_collisions(descriptions: dict[str, str]) -> list[str]:
    """Return warnings for skill pairs whose non-generic token overlap exceeds threshold."""
    warnings = []
    names = list(descriptions)
    tokens = {name: tokenize(desc) for name, desc in descriptions.items()}
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            shared = tokens[a] & tokens[b]
            limit = EXPECTED_OVERLAP.get(frozenset({a, b}), COLLISION_THRESHOLD)
            if len(shared) > limit:
                warnings.append(
                    f"COLLISION  {a} vs {b}: {len(shared)} shared tokens (limit {limit}): "
                    f"{sorted(shared)[:12]}..."
                )
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--baseline",
        default="wave-0-baseline",
        help="Git ref for the pre-refactor baseline (default: wave-0-baseline).",
    )
    parser.add_argument(
        "--skills-dir",
        default=".claude/skills",
        type=Path,
        help="Directory containing the 8 skill folders.",
    )
    parser.add_argument(
        "--skip-missing-baseline",
        action="store_true",
        help="Continue if the baseline ref is unavailable (e.g., in CI on a fresh clone).",
    )
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    current_descs: dict[str, str] = {}

    for skill in SKILL_DIRS:
        try:
            current = read_current_description(args.skills_dir, skill)
        except FileNotFoundError as exc:
            errors.append(f"MISSING-FILE   {skill}: {exc}")
            continue
        if not current:
            errors.append(f"EMPTY-DESC     {skill}: no description block found")
            continue
        current_descs[skill] = current

        try:
            baseline = read_baseline_description(args.baseline, skill)
        except SystemExit as exc:
            if args.skip_missing_baseline:
                warnings.append(f"SKIP-BASELINE  {skill}: {exc}")
                continue
            raise
        if not baseline:
            warnings.append(
                f"NO-BASELINE    {skill}: baseline description empty at {args.baseline}"
            )
            continue
        errors.extend(check_keyword_preservation(baseline, current, skill))

    warnings.extend(check_collisions(current_descs))

    for w in warnings:
        print(w, file=sys.stderr)
    for e in errors:
        print(e, file=sys.stderr)

    summary_fail = f"\nFAIL — {len(errors)} routing issue(s); {len(warnings)} warning(s)"
    summary_ok = (
        f"OK — all {len(SKILL_DIRS)} descriptions preserve baseline tokens "
        f"({len(warnings)} warning(s))"
    )
    if errors:
        print(summary_fail, file=sys.stderr)
        return 1
    print(summary_ok)
    return 0


if __name__ == "__main__":
    sys.exit(main())
