#!/usr/bin/env python3
"""Compatibility entry point that rebuilds the current archive indexes."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Corrupted Files Tools" / "rebuild_indexes.py"
raise SystemExit(subprocess.call([sys.executable, str(SCRIPT)]))
