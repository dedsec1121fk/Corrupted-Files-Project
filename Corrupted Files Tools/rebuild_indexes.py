#!/usr/bin/env python3
"""Rebuild every root, country, date, manifest, and quality index."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from corrupted_files_core import (  # noqa: E402
    atomic_write_json,
    audit_project,
    build_manifest,
    build_master_records,
    load_database,
    write_quality_report,
    write_research_indexes,
    write_root_indexes,
)


def main() -> int:
    database = load_database(ROOT, strict=True)
    records = build_master_records(ROOT)
    write_root_indexes(ROOT, records)
    write_research_indexes(ROOT, database.entries)
    manifest = build_manifest(ROOT, database.entries, len(database.shard_paths))
    atomic_write_json(ROOT / "Corrupted Files Database" / "manifest.json", manifest)

    report = audit_project(ROOT)
    write_quality_report(ROOT, report)
    print(
        f"Rebuilt indexes for {len(records)} incidents across "
        f"{len(database.shard_paths)} database shards."
    )
    if report["warnings"]:
        print(f"Quality report contains {len(report['warnings'])} editorial warning(s).")
    if not report["ok"]:
        print(f"Rebuild completed, but validation found {len(report['errors'])} error(s).")
        for error in report["errors"][:20]:
            print(f"ERROR: {error}")
        return 1
    print("Structural validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
