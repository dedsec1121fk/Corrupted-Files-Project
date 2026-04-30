#!/usr/bin/env python3
"""Compatibility helper for the rebuilt project.
This no longer rebuilds the old Corrupted Files Library/Corrupted Files Media layout.
It only refreshes the new indexes for the current country/date/incident structure.
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / 'Corrupted Files Tools' / 'rebuild_indexes.py'
raise SystemExit(subprocess.call([sys.executable, str(script)]))
