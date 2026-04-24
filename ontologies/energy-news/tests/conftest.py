"""Configure sys.path so ingest package is importable in tests."""

from __future__ import annotations

import sys
from pathlib import Path

# Add the energy-news/scripts directory to sys.path so that
# `from ingest.transform import ...` works in tests.
_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)
