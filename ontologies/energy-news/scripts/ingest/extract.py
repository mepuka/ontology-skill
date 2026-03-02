"""Stage 1: Extract posts from SkyGent store or NDJSON file."""

from __future__ import annotations

import json
import subprocess
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


def extract_from_skygent(
    store: str = "energy-news",
    *,
    limit: int | None = None,
) -> Iterator[dict[str, Any]]:
    """Stream posts from SkyGent CLI as an iterator of dicts.

    Args:
        store: SkyGent store name.
        limit: Maximum number of posts to yield (None = all).

    Yields:
        Parsed JSON dicts, one per post.
    """
    cmd = ["skygent", "query", store, "--full", "--format", "ndjson"]
    if limit:
        cmd.extend(["--limit", str(limit)])

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)  # noqa: S603
    if proc.stdout is None:
        raise RuntimeError("Failed to capture subprocess stdout")

    skipped = 0
    try:
        for raw in proc.stdout:
            stripped = raw.strip()
            if stripped:
                try:
                    yield json.loads(stripped)
                except json.JSONDecodeError:
                    skipped += 1
    finally:
        if skipped:
            print(f"Warning: skipped {skipped} malformed NDJSON lines", file=sys.stderr)
        proc.stdout.close()
        proc.wait()
        if proc.returncode != 0:
            stderr = proc.stderr.read() if proc.stderr else ""
            print(f"Warning: skygent exited with code {proc.returncode}: {stderr}", file=sys.stderr)
            if proc.stderr:
                proc.stderr.close()


def extract_from_file(path: Path) -> Iterator[dict[str, Any]]:
    """Stream posts from an NDJSON file as an iterator of dicts.

    Args:
        path: Path to the NDJSON file.

    Yields:
        Parsed JSON dicts, one per post.
    """
    skipped = 0
    with path.open(encoding="utf-8") as f:
        for raw in f:
            stripped = raw.strip()
            if stripped:
                try:
                    yield json.loads(stripped)
                except json.JSONDecodeError:
                    skipped += 1
    if skipped:
        print(f"Warning: skipped {skipped} malformed NDJSON lines from {path}", file=sys.stderr)
