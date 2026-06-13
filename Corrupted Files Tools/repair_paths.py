#!/usr/bin/env python3
"""Repair escaped Unicode folder names and synchronize every stored archive path.

Run without ``--apply`` for a preview. The operation is idempotent: a second applied
run should report no modified files when the archive has not changed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from corrupted_files_core import (  # noqa: E402
    archive_paths_for_incident,
    calculate_entry_quality,
    decode_escaped_unicode,
    detect_country,
    discover_incidents,
    localize,
    media_paths_for_incident,
    utc_now_iso,
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--apply", action="store_true", help="rename folders and write synchronized paths")
    return result


def json_text(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def write_text_if_changed(path: Path, text: str, apply: bool) -> bool:
    try:
        current = path.read_text(encoding="utf-8")
    except OSError:
        current = None
    if current == text:
        return False
    if apply:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + ".tmp")
        temp.write_text(text, encoding="utf-8")
        temp.replace(path)
    return True


def write_json_if_changed(path: Path, data: Any, apply: bool) -> bool:
    return write_text_if_changed(path, json_text(data), apply)


def rename_escaped_folders(apply: bool) -> list[tuple[str, str]]:
    changes: list[tuple[str, str]] = []
    for country in ("Greece", "USA"):
        country_dir = ROOT / country
        if not country_dir.is_dir():
            continue
        for date_dir in sorted(path for path in country_dir.iterdir() if path.is_dir()):
            for incident_dir in sorted(path for path in date_dir.iterdir() if path.is_dir()):
                decoded_name = decode_escaped_unicode(incident_dir.name)
                if decoded_name == incident_dir.name:
                    continue
                target = incident_dir.with_name(decoded_name)
                if target.exists() and target != incident_dir:
                    raise SystemExit(f"Cannot rename; target already exists: {target}")
                changes.append((incident_dir.relative_to(ROOT).as_posix(), target.relative_to(ROOT).as_posix()))
                if apply:
                    incident_dir.rename(target)
    return changes


def synchronize_incident_files(apply: bool) -> tuple[dict[str, dict[str, Any]], list[str]]:
    incidents, errors = discover_incidents(ROOT)
    if errors:
        raise SystemExit("\n".join(errors))

    synchronized: dict[str, dict[str, Any]] = {}
    modified_files: list[str] = []
    for incident_id, incident in incidents.items():
        media = media_paths_for_incident(ROOT, incident)
        archive_paths = archive_paths_for_incident(ROOT, incident)
        country = detect_country(incident.metadata)
        date_folder = incident.path.parent.name
        year = incident.metadata.get("year") or incident.full_record.get("year") or date_folder[-4:]

        metadata = dict(incident.metadata)
        metadata.update(
            {
                "id": incident_id,
                "country": metadata.get("country") or incident.full_record.get("country") or {
                    "en": country,
                    "el": "Ελλάδα" if country == "Greece" else "ΗΠΑ",
                },
                "year": year,
                "date_folder": date_folder,
                "incident_folder": incident.relative_path,
                "images": media,
            }
        )

        full_record = dict(incident.full_record)
        for key, value in metadata.items():
            full_record[key] = value
        full_record["source_archive_paths"] = archive_paths
        full_record["quality"] = calculate_entry_quality(full_record, media_ok=True)
        audit = dict(full_record.get("audit") or {})
        audit["path_integrity"] = "verified"
        audit["path_repair_version"] = 2
        if not audit.get("path_repair_utc"):
            audit["path_repair_utc"] = utc_now_iso()
        full_record["audit"] = audit
        synchronized[incident_id] = full_record

        title_en = localize(full_record, "title", "en")
        title_el = localize(full_record, "title", "el")
        category_en = localize(full_record, "category", "en")
        category_el = localize(full_record, "category", "el")
        evidence_en = localize(full_record, "evidence_level", "en")
        evidence_el = localize(full_record, "evidence_level", "el")

        overview = "\n".join(
            [
                f"Incident ID: {incident_id}",
                f"Country: {country}",
                f"Date Folder: {date_folder}",
                f"Year: {year}",
                "",
                f"Title EN: {title_en}",
                f"Title EL: {title_el}",
                "",
                f"Category EN: {category_en}",
                f"Category EL: {category_el}",
                "",
                f"Evidence EN: {evidence_en}",
                f"Evidence EL: {evidence_el}",
                "",
                "This folder groups the incident text, metadata, quality signals, and media for offline browsing.",
                "The evidence label describes the archive's own editorial classification; it is not a substitute",
                "for reading the source trail and independently checking primary records.",
                "",
            ]
        )
        keywords = [
            incident_id,
            country,
            date_folder,
            str(year),
            title_en,
            title_el,
            category_en,
            category_el,
            evidence_en,
            evidence_el,
        ]
        keywords_text = "\n".join(item for item in dict.fromkeys(item.strip() for item in keywords) if item) + "\n"
        media_text = "\n".join(media) + ("\n" if media else "")
        file_list = "\n".join(sorted(path.name for path in incident.path.iterdir())) + "\n"

        candidates: list[tuple[Path, str | dict[str, Any]]] = [
            (incident.path / "00 - Incident Overview.txt", overview),
            (incident.path / "09 - Search Keywords.txt", keywords_text),
            (incident.path / "11 - Media Index.txt", media_text),
            (incident.path / "13 - Incident File List.txt", file_list),
            (incident.path / "10 - Metadata.json", metadata),
            (incident.path / "12 - Full Record.json", full_record),
        ]
        for path, content in candidates:
            changed = (
                write_json_if_changed(path, content, apply)
                if isinstance(content, dict)
                else write_text_if_changed(path, content, apply)
            )
            if changed:
                modified_files.append(path.relative_to(ROOT).as_posix())

    return synchronized, modified_files


def synchronize_shards(records: dict[str, dict[str, Any]], apply: bool) -> tuple[int, int]:
    synchronized = 0
    modified = 0
    db_dir = ROOT / "Corrupted Files Database"
    for shard_path in sorted(db_dir.glob("Database Shard *.json")):
        payload = json.loads(shard_path.read_text(encoding="utf-8"))
        output_entries = []
        for entry in payload.get("entries", []):
            incident_id = str(entry.get("id") or "")
            replacement = records.get(incident_id)
            if replacement is None:
                raise SystemExit(f"No folder record found for database id: {incident_id}")
            output_entries.append(replacement)
        updated = dict(payload)
        updated["format"] = "bilingual-offline-incident-records"
        updated["version"] = 2
        updated["entries"] = output_entries
        if write_json_if_changed(shard_path, updated, apply):
            modified += 1
        synchronized += len(output_entries)
    return synchronized, modified


def main() -> int:
    args = parser().parse_args()
    renames = rename_escaped_folders(args.apply)
    records, modified_files = synchronize_incident_files(args.apply)
    synchronized_count, modified_shards = synchronize_shards(records, args.apply)

    mode = "Applied" if args.apply else "Preview"
    print(f"{mode}: {len(renames)} folder rename(s)")
    for old, new in renames[:20]:
        print(f"  {old} -> {new}")
    if len(renames) > 20:
        print(f"  ... {len(renames) - 20} more")
    print(f"{mode}: checked {len(records)} incident folders and {synchronized_count} database records")
    print(f"{mode}: {len(modified_files)} incident-side file change(s), {modified_shards} shard change(s)")
    if not args.apply and (renames or modified_files or modified_shards):
        print("No files were changed. Run again with --apply to perform the repair.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
