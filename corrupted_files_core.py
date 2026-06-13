#!/usr/bin/env python3
"""Shared, dependency-free utilities for the Corrupted Files Project.

The module intentionally uses only Python's standard library so the archive remains
portable on Termux, Linux, macOS, and Windows.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence

PROJECT_NAME = "Corrupted Files Project"
COUNTRIES = ("Greece", "USA")
DB_GLOB = "Database Shard *.json"

REQUIRED_ROOT_ITEMS = (
    "Greece",
    "USA",
    "Corrupted Files Database",
    "Corrupted Files Tools",
    "00 - Master Incident Index.txt",
    "00 - Master Incident Index.json",
    "00 - Master Incident Index.csv",
    "00 - Dates by Country.txt",
    "00 - Statistics.txt",
    "00 - Quality Report.txt",
    "00 - Quality Report.json",
    "00 - Editorial Work Queue.csv",
    "00 - Editorial Work Queue.json",
    "00 - Source Link Index.csv",
    "00 - Source Link Index.json",
    "00 - Category Summary.csv",
    "README.md",
    "Corrupted Files.py",
)

REQUIRED_INCIDENT_FILES = (
    "00 - Incident Overview.txt",
    "00A - Summary EN.txt",
    "00B - Summary EL.txt",
    "01 - Article EN.txt",
    "02 - Article EL.txt",
    "03 - Proof Dossier EN.txt",
    "04 - Proof Dossier EL.txt",
    "05 - Source Trail EN.txt",
    "06 - Source Trail EL.txt",
    "07 - Reading Report EN.txt",
    "08 - Reading Report EL.txt",
    "09 - Search Keywords.txt",
    "10 - Metadata.json",
    "11 - Media Index.txt",
    "12 - Full Record.json",
    "13 - Incident File List.txt",
)

LANGUAGE_FIELDS = (
    "country",
    "title",
    "category",
    "evidence_level",
    "article",
    "proof_dossier",
    "source_trail",
    "reading_report",
)

_ESCAPED_UNICODE_RE = re.compile(r"#U([0-9A-Fa-f]{4})")
_DATE_FOLDER_RE = re.compile(r"^(\d{2})-(\d{2})-(\d{4})$")


@dataclass(frozen=True)
class IncidentRef:
    incident_id: str
    path: Path
    relative_path: str
    metadata: dict[str, Any]
    full_record: dict[str, Any]


@dataclass
class DatabaseLoadResult:
    entries: list[dict[str, Any]]
    shard_paths: list[Path]
    errors: list[str]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def atomic_write_text(path: Path, text: str, *, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(text, encoding=encoding)
    temp.replace(path)


def atomic_write_json(path: Path, data: Any) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def decode_escaped_unicode(value: str) -> str:
    """Decode literal filename escapes such as ``#U2014`` into Unicode."""

    def replace(match: re.Match[str]) -> str:
        try:
            return chr(int(match.group(1), 16))
        except (ValueError, OverflowError):
            return match.group(0)

    return _ESCAPED_UNICODE_RE.sub(replace, value)


def localize(entry: Mapping[str, Any], field: str, lang: str = "en") -> str:
    value = entry.get(field, "")
    if isinstance(value, Mapping):
        preferred = value.get(lang)
        if preferred not in (None, ""):
            return str(preferred)
        for fallback in ("en", "el"):
            candidate = value.get(fallback)
            if candidate not in (None, ""):
                return str(candidate)
        return ""
    return str(value or "")


def detect_country(entry: Mapping[str, Any]) -> str:
    country_en = localize(entry, "country", "en").casefold()
    country_el = localize(entry, "country", "el").casefold()
    if "greece" in country_en or "ελλά" in country_el or "ελλα" in country_el:
        return "Greece"
    if "usa" in country_en or "united states" in country_en or "ηπα" in country_el.replace(".", ""):
        return "USA"
    incident_id = str(entry.get("id", "")).casefold()
    return "Greece" if incident_id.startswith("greece_") else "USA"


def parse_date_folder(entry: Mapping[str, Any]) -> str:
    explicit = str(entry.get("date_folder") or "").strip()
    if _DATE_FOLDER_RE.fullmatch(explicit):
        return explicit

    year = str(entry.get("year") or "0000")
    for key in ("date", "event_date", "date_iso"):
        raw = entry.get(key)
        if isinstance(raw, str):
            value = raw.strip()
            match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", value)
            if match:
                y, month, day = match.groups()
                return f"{day}-{month}-{y}"
            match = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", value)
            if match:
                day, month, y = match.groups()
                return f"{int(day):02d}-{int(month):02d}-{int(y):04d}"
        elif isinstance(raw, Mapping):
            day = raw.get("day")
            month = raw.get("month")
            y = raw.get("year") or year
            if all(str(item).isdigit() for item in (day, month, y)):
                return f"{int(day):02d}-{int(month):02d}-{int(y):04d}"
    return f"00-00-{year}"


def normalize_text(value: Any) -> str:
    """Case- and accent-insensitive search normalization for Greek and Latin text."""
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.casefold().replace("ς", "σ")
    return re.sub(r"[^0-9a-zα-ω]+", " ", text).strip()


def safe_filename(value: str, *, max_length: int = 120) -> str:
    value = decode_escaped_unicode(value)
    value = re.sub(r"[\\/:*?\"<>|\x00-\x1f]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return (value[:max_length].rstrip(" .") or "incident")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_database(root: Path, *, strict: bool = False) -> DatabaseLoadResult:
    db_dir = root / "Corrupted Files Database"
    shard_paths = sorted(db_dir.glob(DB_GLOB))
    entries: list[dict[str, Any]] = []
    errors: list[str] = []
    seen: set[str] = set()

    if not shard_paths:
        errors.append("No database shards were found.")

    for shard in shard_paths:
        try:
            payload = load_json(shard)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{shard.name}: invalid JSON ({exc})")
            continue
        shard_entries = payload.get("entries") if isinstance(payload, Mapping) else None
        if not isinstance(shard_entries, list):
            errors.append(f"{shard.name}: missing entries list")
            continue
        for position, item in enumerate(shard_entries, 1):
            if not isinstance(item, dict):
                errors.append(f"{shard.name}: entry {position} is not an object")
                continue
            incident_id = str(item.get("id") or "").strip()
            if not incident_id:
                errors.append(f"{shard.name}: entry {position} has no id")
                continue
            if incident_id in seen:
                errors.append(f"Duplicate database id: {incident_id}")
                continue
            seen.add(incident_id)
            entries.append(item)

    if strict and errors:
        raise ValueError("\n".join(errors))
    return DatabaseLoadResult(entries=entries, shard_paths=shard_paths, errors=errors)


def iter_incident_dirs(root: Path) -> Iterator[Path]:
    for country in COUNTRIES:
        country_dir = root / country
        if not country_dir.is_dir():
            continue
        for date_dir in sorted(path for path in country_dir.iterdir() if path.is_dir()):
            for incident_dir in sorted(path for path in date_dir.iterdir() if path.is_dir()):
                yield incident_dir


def discover_incidents(root: Path) -> tuple[dict[str, IncidentRef], list[str]]:
    incidents: dict[str, IncidentRef] = {}
    errors: list[str] = []
    for incident_dir in iter_incident_dirs(root):
        metadata_path = incident_dir / "10 - Metadata.json"
        full_record_path = incident_dir / "12 - Full Record.json"
        try:
            metadata = load_json(metadata_path)
        except Exception as exc:  # reports all malformed/missing metadata consistently
            errors.append(f"{metadata_path.relative_to(root)}: {exc}")
            continue
        try:
            full_record = load_json(full_record_path)
        except Exception as exc:
            errors.append(f"{full_record_path.relative_to(root)}: {exc}")
            full_record = {}
        incident_id = str(metadata.get("id") or full_record.get("id") or "").strip()
        if not incident_id:
            errors.append(f"{incident_dir.relative_to(root)}: no incident id")
            continue
        if incident_id in incidents:
            errors.append(f"Duplicate incident folder id: {incident_id}")
            continue
        relative_path = incident_dir.relative_to(root).as_posix()
        incidents[incident_id] = IncidentRef(
            incident_id=incident_id,
            path=incident_dir,
            relative_path=relative_path,
            metadata=metadata,
            full_record=full_record,
        )
    return incidents, errors


def media_paths_for_incident(root: Path, incident: IncidentRef) -> list[str]:
    media_dir = incident.path / "Media"
    if not media_dir.is_dir():
        return []
    return [path.relative_to(root).as_posix() for path in sorted(media_dir.iterdir()) if path.is_file()]


def archive_paths_for_incident(root: Path, incident: IncidentRef) -> dict[str, list[str]]:
    names = {
        "en": (
            "01 - Article EN.txt",
            "03 - Proof Dossier EN.txt",
            "05 - Source Trail EN.txt",
            "07 - Reading Report EN.txt",
        ),
        "el": (
            "02 - Article EL.txt",
            "04 - Proof Dossier EL.txt",
            "06 - Source Trail EL.txt",
            "08 - Reading Report EL.txt",
        ),
    }
    media = media_paths_for_incident(root, incident)
    result: dict[str, list[str]] = {}
    for lang, filenames in names.items():
        paths = [
            (incident.path / filename).relative_to(root).as_posix()
            for filename in filenames
            if (incident.path / filename).is_file()
        ]
        language_marker = " EN " if lang == "en" else " EL "
        paths.extend(path for path in media if language_marker in f" {Path(path).name} ")
        result[lang] = paths
    return result


def _script_ratios(text: str) -> tuple[float, float]:
    greek = sum(1 for char in text if "GREEK" in unicodedata.name(char, ""))
    latin = sum(1 for char in text if "LATIN" in unicodedata.name(char, ""))
    total = greek + latin
    if total == 0:
        return 0.0, 0.0
    return greek / total, latin / total


def translation_status(entry: Mapping[str, Any]) -> dict[str, Any]:
    statuses: dict[str, str] = {}
    for field in ("title", "category", "evidence_level", "article"):
        en = localize(entry, field, "en").strip()
        el = localize(entry, field, "el").strip()
        if not en or not el:
            statuses[field] = "missing"
            continue
        if normalize_text(en) == normalize_text(el):
            statuses[field] = "same-as-english"
            continue
        greek_ratio, latin_ratio = _script_ratios(el)
        if field == "article" and greek_ratio < 0.35 and latin_ratio > 0.55:
            statuses[field] = "partial-greek"
        elif greek_ratio >= 0.35:
            statuses[field] = "greek-present"
        else:
            statuses[field] = "mixed-or-neutral"
    overall = "good"
    if "missing" in statuses.values():
        overall = "missing-fields"
    elif "same-as-english" in statuses.values() or "partial-greek" in statuses.values():
        overall = "needs-review"
    return {"overall": overall, "fields": statuses}


def source_trail_status(entry: Mapping[str, Any]) -> dict[str, Any]:
    en = localize(entry, "source_trail", "en").strip()
    urls = re.findall(r"https?://[^\s)\]>]+", en)
    normalized = normalize_text(en)
    generic_markers = (
        "source trail recovery note use official records",
        "use official records court material parliamentary records",
    )
    generic = any(marker in normalized for marker in generic_markers)
    if urls:
        level = "specific-links"
    elif generic or len(en) < 220:
        level = "generic-guidance"
    else:
        level = "descriptive-no-links"
    return {"level": level, "url_count": len(urls)}


def calculate_entry_quality(entry: Mapping[str, Any], *, media_ok: bool = True) -> dict[str, Any]:
    return {
        "translation": translation_status(entry),
        "source_trail": source_trail_status(entry),
        "media_paths": "verified" if media_ok else "missing",
    }


def build_master_records(root: Path) -> list[dict[str, Any]]:
    incidents, errors = discover_incidents(root)
    if errors:
        raise ValueError("Cannot build indexes:\n" + "\n".join(errors))
    records: list[dict[str, Any]] = []
    for incident in incidents.values():
        metadata = incident.metadata
        images = media_paths_for_incident(root, incident)
        records.append(
            {
                "country": detect_country(metadata),
                "date_folder": incident.path.parent.name,
                "year": metadata.get("year", ""),
                "incident_folder": incident.path.name,
                "incident_path": incident.relative_path,
                "id": incident.incident_id,
                "title_en": localize(metadata, "title", "en"),
                "title_el": localize(metadata, "title", "el"),
                "category_en": localize(metadata, "category", "en"),
                "category_el": localize(metadata, "category", "el"),
                "evidence_en": localize(metadata, "evidence_level", "en"),
                "evidence_el": localize(metadata, "evidence_level", "el"),
                "media_count": len(images),
            }
        )
    records.sort(key=lambda row: (row["country"], str(row["year"]), row["date_folder"], row["title_en"].casefold()))
    return records


def write_root_indexes(root: Path, records: Sequence[Mapping[str, Any]]) -> None:
    text_lines = [
        f"{record['country']} :: {record['date_folder']} :: {record['incident_folder']} :: {record['id']}"
        for record in records
    ]
    atomic_write_text(root / "00 - Master Incident Index.txt", "\n".join(text_lines) + "\n")
    atomic_write_json(root / "00 - Master Incident Index.json", list(records))

    csv_path = root / "00 - Master Incident Index.csv"
    temp_csv = csv_path.with_name(csv_path.name + ".tmp")
    with temp_csv.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "Country",
            "DateFolder",
            "Year",
            "IncidentFolder",
            "IncidentPath",
            "ID",
            "TitleEN",
            "TitleEL",
            "CategoryEN",
            "CategoryEL",
            "EvidenceEN",
            "EvidenceEL",
            "MediaCount",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "Country": record["country"],
                    "DateFolder": record["date_folder"],
                    "Year": record["year"],
                    "IncidentFolder": record["incident_folder"],
                    "IncidentPath": record["incident_path"],
                    "ID": record["id"],
                    "TitleEN": record["title_en"],
                    "TitleEL": record["title_el"],
                    "CategoryEN": record["category_en"],
                    "CategoryEL": record["category_el"],
                    "EvidenceEN": record["evidence_en"],
                    "EvidenceEL": record["evidence_el"],
                    "MediaCount": record["media_count"],
                }
            )
    temp_csv.replace(csv_path)

    by_country: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for record in records:
        by_country[str(record["country"])][str(record["date_folder"])] += 1
    date_lines: list[str] = []
    for country in COUNTRIES:
        date_lines.extend((country, "=" * len(country)))
        for date_folder, count in sorted(by_country[country].items()):
            date_lines.append(f"{date_folder} :: {count} incident(s)")
        date_lines.append("")
    atomic_write_text(root / "00 - Dates by Country.txt", "\n".join(date_lines).rstrip() + "\n")

    years = {str(record["year"]) for record in records if str(record["year"]).strip()}
    categories = {str(record["category_en"]) for record in records if str(record["category_en"]).strip()}
    total_media = sum(int(record["media_count"]) for record in records)
    country_counts = Counter(str(record["country"]) for record in records)
    stats_lines = [
        PROJECT_NAME,
        "=" * len(PROJECT_NAME),
        f"Incidents: {len(records)}",
        f"Countries: {len(country_counts)} ({', '.join(f'{key}: {value}' for key, value in sorted(country_counts.items()))})",
        f"Years represented: {len(years)}",
        f"Date folders: {sum(len(value) for value in by_country.values())}",
        f"Unique English categories: {len(categories)}",
        f"Media files referenced: {total_media}",
        f"Last rebuilt (UTC): {utc_now_iso()}",
    ]
    atomic_write_text(root / "00 - Statistics.txt", "\n".join(stats_lines) + "\n")

    for country in COUNTRIES:
        country_records = [record for record in records if record["country"] == country]
        lines = [f"{country} Incident Index", "=" * (len(country) + 15), ""]
        for record in country_records:
            lines.append(f"{record['date_folder']} :: {record['title_en']} :: {record['id']}")
        atomic_write_text(root / country / "00 - Country Index.txt", "\n".join(lines) + "\n")

        grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for record in country_records:
            grouped[str(record["date_folder"])].append(record)
        for date_folder, date_records in grouped.items():
            date_dir = root / country / date_folder
            lines = [f"{country} / {date_folder}", "=" * (len(country) + len(date_folder) + 3), ""]
            for record in date_records:
                lines.append(f"{record['incident_folder']} :: {record['id']}")
            atomic_write_text(date_dir / "00 - Date Index.txt", "\n".join(lines) + "\n")



def write_research_indexes(root: Path, entries: Sequence[Mapping[str, Any]]) -> None:
    """Write editorial-priority, direct-source, and category summary indexes."""
    editorial_rows: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    category_groups: dict[str, dict[str, Any]] = {}

    for entry in entries:
        quality = entry.get("quality") if isinstance(entry.get("quality"), Mapping) else calculate_entry_quality(entry)
        translation = str((quality.get("translation") or {}).get("overall", "unknown"))
        source_info = quality.get("source_trail") or {}
        source_level = str(source_info.get("level", "unknown"))
        url_count = int(source_info.get("url_count", 0) or 0)
        if translation != "good" and source_level == "generic-guidance":
            priority = "high"
        elif translation != "good" or source_level == "generic-guidance":
            priority = "medium"
        else:
            priority = "low"
        editorial_rows.append(
            {
                "priority": priority,
                "id": str(entry.get("id", "")),
                "country": detect_country(entry),
                "year": entry.get("year", ""),
                "title_en": localize(entry, "title", "en"),
                "title_el": localize(entry, "title", "el"),
                "translation_status": translation,
                "source_status": source_level,
                "direct_url_count": url_count,
                "incident_path": str(entry.get("incident_folder", "")),
            }
        )

        combined_sources = "\n".join(
            [localize(entry, "source_trail", "en"), localize(entry, "source_trail", "el")]
        )
        urls = list(dict.fromkeys(re.findall(r"https?://[^\s)\]>]+", combined_sources)))
        for url in urls:
            source_rows.append(
                {
                    "id": str(entry.get("id", "")),
                    "country": detect_country(entry),
                    "year": entry.get("year", ""),
                    "title_en": localize(entry, "title", "en"),
                    "title_el": localize(entry, "title", "el"),
                    "url": url.rstrip(".,;"),
                }
            )

        category = localize(entry, "category", "en").strip() or "(unknown)"
        group = category_groups.setdefault(
            category,
            {"category_en": category, "total": 0, "greece": 0, "usa": 0, "years": []},
        )
        group["total"] += 1
        group["greece" if detect_country(entry) == "Greece" else "usa"] += 1
        try:
            group["years"].append(int(entry.get("year")))
        except (TypeError, ValueError):
            pass

    priority_order = {"high": 0, "medium": 1, "low": 2}
    editorial_rows.sort(
        key=lambda row: (priority_order.get(str(row["priority"]), 9), str(row["country"]), int(row["year"] or 0), str(row["title_en"]).casefold())
    )
    source_rows.sort(key=lambda row: (str(row["country"]), int(row["year"] or 0), str(row["title_en"]).casefold(), str(row["url"])))
    category_rows = []
    for group in category_groups.values():
        years = group.pop("years")
        group["first_year"] = min(years) if years else ""
        group["last_year"] = max(years) if years else ""
        category_rows.append(group)
    category_rows.sort(key=lambda row: (-int(row["total"]), str(row["category_en"]).casefold()))

    atomic_write_json(root / "00 - Editorial Work Queue.json", editorial_rows)
    atomic_write_json(root / "00 - Source Link Index.json", source_rows)

    def write_csv(path: Path, rows: Sequence[Mapping[str, Any]], fields: Sequence[str]) -> None:
        temp = path.with_name(path.name + ".tmp")
        with temp.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(fields))
            writer.writeheader()
            writer.writerows(rows)
        temp.replace(path)

    write_csv(
        root / "00 - Editorial Work Queue.csv",
        editorial_rows,
        (
            "priority",
            "id",
            "country",
            "year",
            "title_en",
            "title_el",
            "translation_status",
            "source_status",
            "direct_url_count",
            "incident_path",
        ),
    )
    write_csv(
        root / "00 - Source Link Index.csv",
        source_rows,
        ("id", "country", "year", "title_en", "title_el", "url"),
    )
    write_csv(
        root / "00 - Category Summary.csv",
        category_rows,
        ("category_en", "total", "greece", "usa", "first_year", "last_year"),
    )

def build_manifest(root: Path, entries: Sequence[Mapping[str, Any]], shard_count: int) -> dict[str, Any]:
    media_refs = sum(len(entry.get("images") or []) for entry in entries)
    translation_counts = Counter(translation_status(entry)["overall"] for entry in entries)
    source_counts = Counter(source_trail_status(entry)["level"] for entry in entries)
    return {
        "project": PROJECT_NAME,
        "format_version": 2,
        "database_files": shard_count,
        "records": len(entries),
        "media_references": media_refs,
        "languages": ["en", "el"],
        "root_folders": list(COUNTRIES),
        "translation_status": dict(sorted(translation_counts.items())),
        "source_trail_status": dict(sorted(source_counts.items())),
        "last_rebuilt_utc": utc_now_iso(),
        "notes": (
            "Country/date/incident archive with synchronized database paths, "
            "machine-readable indexes, and integrity metadata. Translation and source "
            "coverage are reported as quality signals rather than assumed complete."
        ),
    }


def audit_project(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, Any] = {}

    for item in REQUIRED_ROOT_ITEMS:
        if not (root / item).exists():
            errors.append(f"Missing root item: {item}")

    json_files = [
        path
        for path in root.rglob("*.json")
        if "Corrupted Files Exports" not in path.parts and path.name != ".corrupted_files_state.json"
    ]
    invalid_json = 0
    for path in json_files:
        try:
            load_json(path)
        except Exception as exc:
            invalid_json += 1
            errors.append(f"Invalid JSON: {path.relative_to(root)} ({exc})")
    metrics["json_files_checked"] = len(json_files)
    metrics["invalid_json_files"] = invalid_json

    database = load_database(root)
    errors.extend(database.errors)
    entries = database.entries
    incidents, incident_errors = discover_incidents(root)
    errors.extend(incident_errors)

    metrics["database_records"] = len(entries)
    metrics["incident_folders"] = len(incidents)
    metrics["database_shards"] = len(database.shard_paths)

    db_ids = {str(entry.get("id")) for entry in entries}
    folder_ids = set(incidents)
    for incident_id in sorted(db_ids - folder_ids):
        errors.append(f"Database record has no incident folder: {incident_id}")
    for incident_id in sorted(folder_ids - db_ids):
        errors.append(f"Incident folder has no database record: {incident_id}")

    missing_required = 0
    empty_required = 0
    escaped_names = 0
    media_refs = 0
    missing_media = 0
    missing_archive_paths = 0
    path_mismatches = 0
    metadata_mismatches = 0
    full_record_mismatches = 0
    index_mismatches = 0

    by_id = {str(entry.get("id")): entry for entry in entries}
    translation_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()

    for incident_id, incident in incidents.items():
        if _ESCAPED_UNICODE_RE.search(incident.path.name):
            escaped_names += 1
            warnings.append(f"Escaped Unicode remains in folder name: {incident.relative_path}")

        for filename in REQUIRED_INCIDENT_FILES:
            path = incident.path / filename
            if not path.exists():
                missing_required += 1
                errors.append(f"Missing incident file: {path.relative_to(root)}")
            elif path.stat().st_size == 0:
                empty_required += 1
                errors.append(f"Empty incident file: {path.relative_to(root)}")

        country_index = incident.path.parents[1] / "00 - Country Index.txt"
        date_index = incident.path.parent / "00 - Date Index.txt"
        if not country_index.is_file():
            index_mismatches += 1
            errors.append(f"Missing country index: {country_index.relative_to(root)}")
        if not date_index.is_file():
            index_mismatches += 1
            errors.append(f"Missing date index: {date_index.relative_to(root)}")

        entry = by_id.get(incident_id)
        if entry is None:
            continue
        expected_folder = incident.relative_path
        expected_media = media_paths_for_incident(root, incident)

        if str(entry.get("incident_folder") or "") != expected_folder:
            path_mismatches += 1
            errors.append(f"Database incident path mismatch for {incident_id}")
        actual_images = [str(item) for item in entry.get("images") or []]
        media_refs += len(actual_images)
        for image in actual_images:
            if not (root / image).is_file():
                missing_media += 1
                errors.append(f"Missing media reference: {image}")
        if actual_images != expected_media:
            path_mismatches += 1
            errors.append(f"Database media list mismatch for {incident_id}")

        source_archive_paths = entry.get("source_archive_paths") or {}
        if not isinstance(source_archive_paths, Mapping):
            path_mismatches += 1
            errors.append(f"Invalid source_archive_paths object for {incident_id}")
        else:
            for lang, paths in source_archive_paths.items():
                if not isinstance(paths, list):
                    path_mismatches += 1
                    errors.append(f"Invalid source archive path list for {incident_id}/{lang}")
                    continue
                for stored_path in paths:
                    if not (root / str(stored_path)).is_file():
                        missing_archive_paths += 1
                        errors.append(f"Missing source archive path: {stored_path}")

        metadata = incident.metadata
        if str(metadata.get("id") or "") != incident_id:
            metadata_mismatches += 1
            errors.append(f"Metadata id mismatch for {incident_id}")
        if str(metadata.get("incident_folder") or "") != expected_folder:
            metadata_mismatches += 1
            errors.append(f"Metadata incident path mismatch for {incident_id}")
        if [str(item) for item in metadata.get("images") or []] != expected_media:
            metadata_mismatches += 1
            errors.append(f"Metadata media list mismatch for {incident_id}")

        full_record = incident.full_record
        if str(full_record.get("id") or "") != incident_id:
            full_record_mismatches += 1
            errors.append(f"Full Record id mismatch for {incident_id}")
        if str(full_record.get("incident_folder") or "") != expected_folder:
            full_record_mismatches += 1
            errors.append(f"Full Record incident path mismatch for {incident_id}")
        if [str(item) for item in full_record.get("images") or []] != expected_media:
            full_record_mismatches += 1
            errors.append(f"Full Record media list mismatch for {incident_id}")

        media_index_path = incident.path / "11 - Media Index.txt"
        if media_index_path.is_file():
            listed = [line.strip() for line in media_index_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            if listed != expected_media:
                index_mismatches += 1
                errors.append(f"Media Index mismatch for {incident_id}")

        translation_counts[translation_status(entry)["overall"]] += 1
        source_counts[source_trail_status(entry)["level"]] += 1

    metrics.update(
        {
            "missing_required_files": missing_required,
            "empty_required_files": empty_required,
            "escaped_unicode_folders": escaped_names,
            "media_references": media_refs,
            "missing_media_references": missing_media,
            "missing_source_archive_paths": missing_archive_paths,
            "path_mismatches": path_mismatches,
            "metadata_mismatches": metadata_mismatches,
            "full_record_mismatches": full_record_mismatches,
            "index_mismatches": index_mismatches,
            "translation_status": dict(sorted(translation_counts.items())),
            "source_trail_status": dict(sorted(source_counts.items())),
        }
    )

    if len(entries) != len(incidents):
        errors.append(f"Record/folder count mismatch: {len(entries)} database records vs {len(incidents)} folders")

    manifest_path = root / "Corrupted Files Database" / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest = load_json(manifest_path)
            if manifest.get("records") != len(entries):
                errors.append(f"Manifest record mismatch: {manifest.get('records')} != {len(entries)}")
            if manifest.get("database_files") != len(database.shard_paths):
                errors.append(
                    f"Manifest shard mismatch: {manifest.get('database_files')} != {len(database.shard_paths)}"
                )
            if manifest.get("media_references") != media_refs:
                errors.append(f"Manifest media mismatch: {manifest.get('media_references')} != {media_refs}")
        except Exception as exc:
            errors.append(f"Invalid manifest.json: {exc}")
    else:
        errors.append("Missing Corrupted Files Database/manifest.json")

    master_json = root / "00 - Master Incident Index.json"
    if master_json.is_file():
        try:
            master_records = load_json(master_json)
            if not isinstance(master_records, list):
                errors.append("Master JSON index is not a list")
            else:
                master_ids = {str(record.get("id")) for record in master_records if isinstance(record, Mapping)}
                if len(master_records) != len(incidents) or master_ids != folder_ids:
                    errors.append("Master JSON index does not match incident folders")
                for record in master_records:
                    if not isinstance(record, Mapping):
                        continue
                    incident_id = str(record.get("id") or "")
                    incident = incidents.get(incident_id)
                    if incident and str(record.get("incident_path") or "") != incident.relative_path:
                        index_mismatches += 1
                        errors.append(f"Master JSON path mismatch for {incident_id}")
        except Exception as exc:
            errors.append(f"Invalid master JSON index: {exc}")

    master_txt = root / "00 - Master Incident Index.txt"
    if master_txt.is_file():
        line_count = sum(1 for line in master_txt.read_text(encoding="utf-8").splitlines() if line.strip())
        if line_count != len(incidents):
            errors.append(f"Master TXT index count mismatch: {line_count} != {len(incidents)}")

    master_csv = root / "00 - Master Incident Index.csv"
    if master_csv.is_file():
        try:
            with master_csv.open(newline="", encoding="utf-8") as handle:
                row_count = sum(1 for _ in csv.DictReader(handle))
            if row_count != len(incidents):
                errors.append(f"Master CSV index count mismatch: {row_count} != {len(incidents)}")
        except Exception as exc:
            errors.append(f"Invalid master CSV index: {exc}")

    metrics["index_mismatches"] = index_mismatches

    if translation_counts.get("needs-review", 0):
        warnings.append(
            f"{translation_counts['needs-review']} records contain same-as-English or heavily mixed Greek fields."
        )
    if translation_counts.get("missing-fields", 0):
        warnings.append(f"{translation_counts['missing-fields']} records have missing bilingual fields.")
    if source_counts.get("generic-guidance", 0):
        warnings.append(
            f"{source_counts['generic-guidance']} records use generic source guidance instead of case-specific links."
        )

    return {
        "project": PROJECT_NAME,
        "checked_at_utc": utc_now_iso(),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
    }

def quality_report_text(report: Mapping[str, Any]) -> str:
    metrics = report.get("metrics", {})
    lines = [
        f"{PROJECT_NAME} - Quality and Integrity Report",
        "=" * 55,
        f"Checked at (UTC): {report.get('checked_at_utc', '')}",
        f"Result: {'PASS' if report.get('ok') else 'FAIL'}",
        "",
        "Core metrics",
        "------------",
    ]
    for key in (
        "database_records",
        "incident_folders",
        "database_shards",
        "json_files_checked",
        "invalid_json_files",
        "media_references",
        "missing_media_references",
        "missing_source_archive_paths",
        "missing_required_files",
        "empty_required_files",
        "escaped_unicode_folders",
        "path_mismatches",
        "metadata_mismatches",
        "full_record_mismatches",
        "index_mismatches",
    ):
        lines.append(f"{key.replace('_', ' ').title()}: {metrics.get(key, 0)}")

    lines.extend(("", "Translation status (heuristic)", "------------------------------"))
    for key, value in sorted((metrics.get("translation_status") or {}).items()):
        lines.append(f"{key}: {value}")

    lines.extend(("", "Source trail status", "-------------------"))
    for key, value in sorted((metrics.get("source_trail_status") or {}).items()):
        lines.append(f"{key}: {value}")

    errors = list(report.get("errors") or [])
    warnings = list(report.get("warnings") or [])
    lines.extend(("", f"Errors ({len(errors)})", "-----------"))
    lines.extend(f"- {item}" for item in errors) if errors else lines.append("None")
    lines.extend(("", f"Warnings ({len(warnings)})", "-------------"))
    lines.extend(f"- {item}" for item in warnings) if warnings else lines.append("None")
    lines.extend(
        (
            "",
            "Interpretation",
            "--------------",
            "A PASS means the files, JSON records, indexes, and media references are structurally consistent.",
            "It does not independently verify every historical claim. Translation and source-trail warnings",
            "identify editorial work that still benefits from human review and case-specific citations.",
        )
    )
    return "\n".join(lines) + "\n"


def write_quality_report(root: Path, report: Mapping[str, Any]) -> None:
    atomic_write_text(root / "00 - Quality Report.txt", quality_report_text(report))
    atomic_write_json(root / "00 - Quality Report.json", report)
