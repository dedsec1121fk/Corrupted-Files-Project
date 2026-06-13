#!/usr/bin/env python3
"""Refresh 00 - Quality Report.txt and 00 - Quality Report.json."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from corrupted_files_core import audit_project, write_quality_report  # noqa: E402


def main() -> int:
    report = audit_project(ROOT)
    write_quality_report(ROOT, report)
    print(f"Quality reports refreshed. Result: {'PASS' if report['ok'] else 'FAIL'}")
    print(f"Errors: {len(report['errors'])}; warnings: {len(report['warnings'])}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
