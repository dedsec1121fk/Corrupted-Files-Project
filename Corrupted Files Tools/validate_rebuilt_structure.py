#!/usr/bin/env python3
"""Perform a comprehensive structural and editorial-quality audit."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from corrupted_files_core import audit_project, write_quality_report  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the complete report as JSON")
    parser.add_argument("--write-report", action="store_true", help="refresh the root quality report files")
    parser.add_argument(
        "--warnings-as-errors",
        action="store_true",
        help="return a failure code when editorial warnings remain",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = audit_project(ROOT)
    if args.write_report:
        write_quality_report(ROOT, report)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        metrics = report["metrics"]
        print("Corrupted Files Project validation")
        print("=" * 34)
        print(f"Result: {'PASS' if report['ok'] else 'FAIL'}")
        print(f"Database records: {metrics.get('database_records', 0)}")
        print(f"Incident folders: {metrics.get('incident_folders', 0)}")
        print(f"Database shards: {metrics.get('database_shards', 0)}")
        print(f"JSON files checked: {metrics.get('json_files_checked', 0)}")
        print(f"Invalid JSON files: {metrics.get('invalid_json_files', 0)}")
        print(f"Media references: {metrics.get('media_references', 0)}")
        print(f"Missing media references: {metrics.get('missing_media_references', 0)}")
        print(f"Missing source archive paths: {metrics.get('missing_source_archive_paths', 0)}")
        print(f"Path mismatches: {metrics.get('path_mismatches', 0)}")
        print(f"Index mismatches: {metrics.get('index_mismatches', 0)}")
        print(f"Missing/empty required files: {metrics.get('missing_required_files', 0) + metrics.get('empty_required_files', 0)}")
        print(f"Escaped Unicode folders: {metrics.get('escaped_unicode_folders', 0)}")
        print(f"Translation status: {metrics.get('translation_status', {})}")
        print(f"Source trail status: {metrics.get('source_trail_status', {})}")

        if report["errors"]:
            print(f"\nErrors ({len(report['errors'])})")
            for error in report["errors"]:
                print(f"- {error}")
        if report["warnings"]:
            print(f"\nWarnings ({len(report['warnings'])})")
            for warning in report["warnings"]:
                print(f"- {warning}")
        if not report["errors"]:
            print("\nAll JSON, folder, index, metadata, and media-path checks passed.")

    failed = not report["ok"] or (args.warnings_as_errors and bool(report["warnings"]))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
