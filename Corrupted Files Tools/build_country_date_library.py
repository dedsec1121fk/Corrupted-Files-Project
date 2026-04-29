#!/usr/bin/env python3
"""Build a human-browsable country/date mirror from the JSON database.

The reader app continues to use the JSON shards as the source of truth. This
script creates a maintenance-friendly file tree for people who prefer browsing
by country and date.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_DIR = ROOT / "Corrupted Files Database"
LIBRARY_DIR = ROOT / "Corrupted Files Library"

FIELDS = [
    ("Article", "article"),
    ("Proof dossier", "proof_dossier"),
    ("Source trail", "source_trail"),
    ("Reading report", "reading_report"),
]


def localized(value, lang: str) -> str:
    if isinstance(value, dict):
        return str(value.get(lang) or value.get("en") or value.get("el") or "")
    return str(value or "")


def slug(text: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9Α-Ωα-ωΆ-ώ]+", "_", text).strip("_")
    return (cleaned or fallback)[:90]


def date_folder(entry: dict) -> str:
    """Return DD-MM-YYYY when exact date exists, otherwise 00-00-YYYY.

    Current records mostly contain only a year. Using 00-00-YYYY makes the
    missing day/month visible while preserving the country/date browsing model.
    """
    year = str(entry.get("year") or "0000")
    raw_date = entry.get("date") or entry.get("event_date")

    if isinstance(raw_date, str):
        match = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", raw_date.strip())
        if match:
            day, month, raw_year = match.groups()
            return f"{int(day):02d}-{int(month):02d}-{raw_year}"

    if isinstance(raw_date, dict):
        day = raw_date.get("day")
        month = raw_date.get("month")
        raw_year = raw_date.get("year") or year
        if str(day).isdigit() and str(month).isdigit() and str(raw_year).isdigit():
            return f"{int(day):02d}-{int(month):02d}-{int(raw_year):04d}"

    return f"00-00-{year}"


def render_entry(entry: dict, lang: str) -> str:
    title = localized(entry.get("title"), lang)
    country = localized(entry.get("country"), lang)
    category = localized(entry.get("category"), lang)
    evidence = localized(entry.get("evidence_level"), lang)
    lines = [
        title,
        "=" * len(title),
        "",
        f"ID: {entry.get('id', '')}",
        f"Country: {country}",
        f"Year: {entry.get('year', '')}",
        f"Category: {category}",
        f"Evidence: {evidence}",
        "",
    ]

    for label, field in FIELDS:
        text = localized(entry.get(field), lang)
        if text:
            lines.extend([label, "-" * len(label), text, ""])

    images = entry.get("images") or []
    if images:
        lines.extend(["Images", "------", *map(str, images), ""])

    return "\n".join(lines).rstrip() + "\n"


def load_entries() -> list[dict]:
    entries: list[dict] = []
    seen: set[str] = set()
    for db_file in sorted(DB_DIR.glob("Corrupted Files Database *.json")):
        payload = json.loads(db_file.read_text(encoding="utf-8"))
        for entry in payload.get("entries", []):
            entry_id = entry.get("id")
            if entry_id and entry_id not in seen:
                seen.add(entry_id)
                entries.append(entry)
    return entries


def build_library() -> None:
    entries = load_entries()
    if LIBRARY_DIR.exists():
        shutil.rmtree(LIBRARY_DIR)

    counts = {"Greece": 0, "USA": 0}
    for entry in entries:
        country_en = localized(entry.get("country"), "en")
        if country_en not in counts:
            continue

        year = str(entry.get("year") or "0000")
        folder = LIBRARY_DIR / country_en / year / date_folder(entry)
        folder.mkdir(parents=True, exist_ok=True)

        entry_id = str(entry.get("id"))
        title_en = localized(entry.get("title"), "en")
        filename = f"{entry_id}__{slug(title_en, entry_id)}.txt"
        (folder / filename).write_text(render_entry(entry, "en"), encoding="utf-8")

        title_el = localized(entry.get("title"), "el")
        filename_el = f"{entry_id}__EL__{slug(title_el, entry_id)}.txt"
        (folder / filename_el).write_text(render_entry(entry, "el"), encoding="utf-8")

        counts[country_en] += 1

    readme = LIBRARY_DIR / "README.md"
    readme.write_text(
        "# Corrupted Files Library\n\n"
        "Human-browsable mirror generated from the JSON database.\n\n"
        "This folder is organized by country, year, and date folder:\n\n"
        "```text\n"
        "Corrupted Files Library/<Greece|USA>/<YYYY>/<DD-MM-YYYY>/\n"
        "```\n\n"
        "Most current records only have a year, so they use `00-00-YYYY` to show that exact day/month is unknown.\n\n"
        "The JSON database remains the source of truth for the app. Regenerate this mirror with:\n\n"
        "```bash\n"
        "python3 \"Corrupted Files Tools/build_country_date_library.py\"\n"
        "```\n\n"
        f"- Greece records mirrored: {counts['Greece']}\n"
        f"- USA records mirrored: {counts['USA']}\n"
        f"- Total records mirrored: {sum(counts.values())}\n",
        encoding="utf-8",
    )
    print(f"Mirrored {sum(counts.values())} records into {LIBRARY_DIR}")
    print(f"Greece: {counts['Greece']}")
    print(f"USA: {counts['USA']}")


if __name__ == "__main__":
    build_library()
