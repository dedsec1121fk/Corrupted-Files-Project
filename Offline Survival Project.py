#!/usr/bin/env python3
"""Corrupted Files Project — offline bilingual case archive and Android gallery reader.

Required repository layout:
  Greek/records.json + Greek/Images/ + Greek/image_credits.json
  USA/records.json   + USA/Images/   + USA/image_credits.json
  README.md
  Offline Survival Project.py

The program uses only Python's standard library. Personal bookmarks, history and
exports are stored outside the repository so archive files remain clean.
"""

# =============================================================================
# MAINTENANCE NOTES
# =============================================================================
# Keep this file as the single repository entry point. Before every release:
#   1. Preserve unique/stable case IDs; never recycle an ID for another event.
#   2. Keep English (en) and Greek (el) fields in parity when editing a dossier.
#   3. Keep claims, interpretation, rumors and source gaps explicitly separated.
#   4. When bundled files change, update their paths, licenses/credits and SHA-256.
#   5. Do not add third-party media unless its redistribution terms are recorded.
#   6. Keep personal state outside the repository; repository data stays immutable.
#   7. Run: python "Offline Survival Project.py" --validate
#   8. Run: python "Offline Survival Project.py" --stats
#   9. Run: python -m py_compile "Offline Survival Project.py"
# JSON does not support real comments. The six repository JSON files therefore
# use a reserved `_maintenance` metadata field as a parse-safe maintenance note.
# The validator checks that these notes remain present.
# =============================================================================

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import random
import re
import shutil
import subprocess
import sys
import textwrap
import unicodedata
from html import escape
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

APP_DIR = Path(__file__).resolve().parent
IS_TERMUX = bool(os.environ.get("TERMUX_VERSION")) or Path("/data/data/com.termux/files/usr").exists()
DATA_FILES = [APP_DIR / "Greek" / "records.json", APP_DIR / "USA" / "records.json"]
CREDIT_FILES = [APP_DIR / "Greek" / "image_credits.json", APP_DIR / "USA" / "image_credits.json"]
OFFLINE_MANIFEST_FILES = [APP_DIR / "Greek" / "offline_materials.json", APP_DIR / "USA" / "offline_materials.json"]
JSON_MAINTENANCE_FILES = DATA_FILES + CREDIT_FILES + OFFLINE_MANIFEST_FILES
STATE_FILE = Path.home() / ".corrupted_files_project_state.json"
EXPORT_DIR = Path.home() / "storage" / "downloads" / "Corrupted Files Exports"
GALLERY_FOLDER_NAME = "Corrupted Files Project"
GALLERY_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogv", ".mkv", ".m4v"}
ARTICLE_EXTENSIONS = {".md", ".txt", ".html", ".htm"}
DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".md", ".html", ".htm"}
GLOBAL_RECORDS: list[dict] = []
WIDTH = max(62, min(100, shutil.get_terminal_size((90, 24)).columns))
USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

C = {
    "title": "\033[95m",
    "accent": "\033[96m",
    "good": "\033[92m",
    "warn": "\033[93m",
    "bad": "\033[91m",
    "dim": "\033[2m",
    "reset": "\033[0m",
}


def color(name: str, text: object) -> str:
    value = str(text)
    return f"{C[name]}{value}{C['reset']}" if USE_COLOR else value


def norm(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return " ".join(
        "".join(ch for ch in text if not unicodedata.combining(ch)).casefold().split()
    )


def local(record: dict, field: str, lang: str) -> str:
    value = record.get(field, {})
    if isinstance(value, dict):
        return str(value.get(lang) or value.get("en") or "")
    return str(value or "")


def rumor_status_text(rumor: dict, lang: str) -> str:
    value = rumor.get("status", "unknown")
    if isinstance(value, dict):
        return str(value.get(lang) or value.get("en") or "unknown")
    return str(value)


def local_list(record: dict, field: str, lang: str) -> list[str]:
    value = record.get(field, {})
    if not isinstance(value, dict):
        return []
    return [str(item) for item in (value.get(lang) or value.get("en") or [])]


def clear() -> None:
    os.system("clear")


def pause(message: str = "Press Enter / Πάτησε Enter...") -> None:
    input("\n" + message)


def line(character: str = "─") -> None:
    print(character * WIDTH)


def wrap(text: object, indent: str = "") -> None:
    print(
        textwrap.fill(
            str(text),
            width=WIDTH,
            initial_indent=indent,
            subsequent_indent=indent,
        )
    )


def load_json(path: Path, default: object) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def has_json_maintenance_note(path: Path) -> bool:
    """Return True when a repository JSON carries its parse-safe upkeep note."""
    data = load_json(path, None)
    if isinstance(data, dict):
        note = data.get("_maintenance")
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        note = data[0].get("_maintenance")
    else:
        return False
    return isinstance(note, dict) and bool(note.get("purpose")) and bool(note.get("update_checklist"))


def load_records() -> list[dict]:
    records: list[dict] = []
    for path in DATA_FILES:
        data = load_json(path, None)
        if not isinstance(data, list):
            raise SystemExit(f"Invalid or missing database: {path}")
        records.extend(data)
    ids = [record.get("id") for record in records]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate record IDs detected.")
    return records


def load_credits() -> dict[str, dict]:
    index: dict[str, dict] = {}
    for path in CREDIT_FILES:
        data = load_json(path, [])
        if not isinstance(data, list):
            continue
        for entry in data:
            if isinstance(entry, dict) and entry.get("file"):
                index[str(entry["file"]).replace("\\", "/")] = entry
    return index


def load_state() -> dict:
    state = load_json(STATE_FILE, {})
    return state if isinstance(state, dict) else {}


def save_state(state: dict) -> None:
    try:
        STATE_FILE.write_text(
            json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except OSError:
        pass


def termux_environment_report() -> dict:
    """Return a Termux-focused environment and storage health report."""
    storage = Path.home() / "storage"
    downloads = storage / "downloads"
    pictures = storage / "pictures"
    commands = {name: bool(shutil.which(name)) for name in ("python", "termux-open", "termux-open-url", "am", "getprop")}
    repository = {
        "Greek/records.json": (APP_DIR / "Greek" / "records.json").is_file(),
        "Greek/Images": (APP_DIR / "Greek" / "Images").is_dir(),
        "USA/records.json": (APP_DIR / "USA" / "records.json").is_file(),
        "USA/Images": (APP_DIR / "USA" / "Images").is_dir(),
        "README.md": (APP_DIR / "README.md").is_file(),
    }
    report = {
        "termux_detected": IS_TERMUX,
        "termux_version": os.environ.get("TERMUX_VERSION", "detected-by-path" if IS_TERMUX else "not-detected"),
        "python_version": ".".join(map(str, sys.version_info[:3])),
        "python_supported": sys.version_info >= (3, 9),
        "storage_shortcuts_exist": storage.is_dir(),
        "downloads_ready": downloads.is_dir() and os.access(downloads, os.W_OK),
        "pictures_ready": pictures.is_dir() and os.access(pictures, os.W_OK),
        "commands": commands,
        "repository": repository,
    }
    report["reader_ready"] = bool(
        report["termux_detected"]
        and report["python_supported"]
        and all(repository.values())
    )
    report["gallery_ready"] = bool(
        report["reader_ready"]
        and report["pictures_ready"]
        and commands["termux-open"]
    )
    fixes = []
    if not report["storage_shortcuts_exist"]:
        fixes.append("Run: termux-setup-storage")
    if not commands["python"]:
        fixes.append("Run: pkg install python -y")
    if not commands["termux-open"] or not commands["termux-open-url"]:
        fixes.append("Run: pkg update -y && pkg upgrade -y")
    if not all(repository.values()):
        fixes.append("Re-extract the complete project ZIP into one folder")
    report["recommended_fixes"] = fixes
    return report


def show_termux_check(lang: str) -> dict:
    report = termux_environment_report()
    banner(lang)
    print(color("title", "TERMUX SYSTEM CHECK" if lang == "en" else "ΕΛΕΓΧΟΣ ΣΥΣΤΗΜΑΤΟΣ TERMUX"))
    line()
    labels = [
        ("Termux detected", "Εντοπίστηκε Termux", report["termux_detected"]),
        ("Python 3.9+", "Python 3.9+", report["python_supported"]),
        ("Storage shortcuts", "Συντομεύσεις αποθήκευσης", report["storage_shortcuts_exist"]),
        ("Downloads writable", "Εγγραφή στις Λήψεις", report["downloads_ready"]),
        ("Pictures writable", "Εγγραφή στις Εικόνες", report["pictures_ready"]),
        ("Android file opener", "Άνοιγμα αρχείων Android", report["commands"]["termux-open"]),
        ("Android URL opener", "Άνοιγμα συνδέσμων Android", report["commands"]["termux-open-url"]),
        ("Repository structure", "Δομή αποθετηρίου", all(report["repository"].values())),
    ]
    for en, el, ok in labels:
        name = en if lang == "en" else el
        print(f"[{color('good','OK') if ok else color('bad','FIX')}] {name}")
    print()
    print(color("accent", "Reader ready / Ο reader είναι έτοιμος:"), report["reader_ready"])
    print(color("accent", "Gallery ready / Το Gallery είναι έτοιμο:"), report["gallery_ready"])
    if report["recommended_fixes"]:
        print("\n" + color("warn", "Recommended fixes / Προτεινόμενες διορθώσεις"))
        for fix in report["recommended_fixes"]:
            print("• " + fix)
    return report


def backup_state_to_downloads(announce: bool = True) -> Path | None:
    downloads = Path.home() / "storage" / "downloads"
    if not downloads.is_dir() or not os.access(downloads, os.W_OK):
        if announce:
            print(color("bad", "Downloads access is not ready / Δεν υπάρχει πρόσβαση στις Λήψεις."))
            print("Run first: termux-setup-storage")
        return None
    try:
        target = EXPORT_DIR / "State Backups"
        target.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        destination = target / f"corrupted-files-state-{timestamp}.json"
        payload = load_state()
        destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if announce:
            print(color("good", "State backup created / Δημιουργήθηκε αντίγραφο ασφαλείας:"))
            print(destination)
        return destination
    except OSError as exc:
        if announce:
            print(color("bad", f"Backup failed / Αποτυχία αντιγράφου: {exc}"))
        return None


def restore_state_from_backup(source: Path, announce: bool = True) -> bool:
    source = Path(source).expanduser()
    data = load_json(source, None)
    if not isinstance(data, dict):
        if announce:
            print(color("bad", "Invalid state backup / Μη έγκυρο αντίγραφο κατάστασης."))
        return False
    allowed = {"bookmarks", "history", "notes", "read_cases", "study_sessions", "study_correct", "study_total"}
    cleaned = {key: value for key, value in data.items() if key in allowed}
    try:
        if STATE_FILE.exists():
            safety = STATE_FILE.with_suffix(f".before-restore-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
            shutil.copy2(STATE_FILE, safety)
        STATE_FILE.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if announce:
            print(color("good", "State restored / Η κατάσταση επαναφέρθηκε:"))
            print(source)
        return True
    except OSError as exc:
        if announce:
            print(color("bad", f"Restore failed / Αποτυχία επαναφοράς: {exc}"))
        return False


def choose_state_backup(lang: str) -> None:
    folder = EXPORT_DIR / "State Backups"
    backups = sorted(folder.glob("corrupted-files-state-*.json"), reverse=True) if folder.is_dir() else []
    if not backups:
        print(color("warn", "No state backups found / Δεν βρέθηκαν αντίγραφα κατάστασης."))
        print(folder)
        pause()
        return
    banner(lang)
    print(color("title", "RESTORE STATE" if lang == "en" else "ΕΠΑΝΑΦΟΡΑ ΚΑΤΑΣΤΑΣΗΣ"))
    line()
    for index, path in enumerate(backups[:20], 1):
        print(f"{index}. {path.name}")
    print("[Enter] Back / Πίσω")
    choice = input("> ").strip()
    if not choice:
        return
    try:
        selected = backups[int(choice) - 1]
    except (ValueError, IndexError):
        print(color("bad", "Invalid selection / Μη έγκυρη επιλογή.")); pause(); return
    restore_state_from_backup(selected)
    pause()


def require_termux() -> bool:
    if IS_TERMUX or os.environ.get("CFP_ALLOW_NON_TERMUX") == "1":
        return True
    print("Corrupted Files Project supports Termux on Android only.")
    print("Το Corrupted Files Project υποστηρίζεται μόνο σε Termux για Android.")
    return False


def banner(lang: str) -> None:
    clear()
    line("═")
    title = color("title", "CORRUPTED FILES PROJECT")
    padding = len(C["title"]) + len(C["reset"]) if USE_COLOR else 0
    print(title.center(WIDTH + padding))
    subtitle = (
        "Termux-only offline archive • Greece & USA • Android Gallery ready"
        if lang == "en"
        else "Offline αρχείο μόνο για Termux • Ελλάδα & ΗΠΑ • Έτοιμο για Android Gallery"
    )
    print(subtitle.center(WIDTH))
    line("═")


def evidence_label(level: str, lang: str) -> str:
    names = {
        "documented/mixed-record": (
            "DOCUMENTED / MIXED RECORD",
            "ΤΕΚΜΗΡΙΩΜΕΝΟ / ΜΙΚΤΟ ΑΡΧΕΙΟ",
        ),
        "mixed/disputed": ("MIXED / DISPUTED", "ΜΙΚΤΟ / ΑΜΦΙΣΒΗΤΟΥΜΕΝΟ"),
        "rumor-focused": ("RUMOR-FOCUSED", "ΕΣΤΙΑΣΗ ΣΕ ΦΗΜΕΣ"),
        "needs-sources": (
            "NEEDS MORE SOURCES",
            "ΧΡΕΙΑΖΕΤΑΙ ΠΕΡΙΣΣΟΤΕΡΕΣ ΠΗΓΕΣ",
        ),
    }
    return names.get(level, (level, level))[0 if lang == "en" else 1]


def record_text(record: dict) -> str:
    values: list[object] = [
        record.get("id", ""),
        record.get("country", ""),
        record.get("year", ""),
        record.get("evidence_level", ""),
    ]
    for field in ("title", "category", "evidence", "summary"):
        values.extend([local(record, field, "en"), local(record, field, "el")])
    for field in ("full_story", "details", "deep_dive", "aftermath_legacy", "accountability_map", "primary_record_targets", "people_institutions", "evidence_conflicts", "media_memory", "next_reading_path", "timeline", "facts", "key_questions", "investigation_plan", "verification_notes"):
        values.extend(local_list(record, field, "en"))
        values.extend(local_list(record, field, "el"))
    values.extend([local(record, "source_gap", "en"), local(record, "source_gap", "el")])
    values.extend(record.get("aliases", []))
    values.extend(record.get("sources", []))
    values.extend(record.get("research_queries", []))
    for portal in record.get("research_portals", []):
        values.extend([local(portal, "name", "en"), local(portal, "name", "el"), local(portal, "purpose", "en"), local(portal, "purpose", "el"), portal.get("url", "")])
    for lead in record.get("source_leads", []):
        values.extend([local(lead, "label", "en"), local(lead, "label", "el"), lead.get("url", ""), lead.get("query", "")])
    for rumor in record.get("rumors", []):
        values.extend(
            [
                local(rumor, "claim", "en"),
                local(rumor, "claim", "el"),
                local(rumor, "assessment", "en"),
                local(rumor, "assessment", "el"),
                rumor.get("status", ""),
            ]
        )
    return norm(" ".join(map(str, values)))


def search(records: list[dict], query: str) -> list[dict]:
    words = [norm(token) for token in query.split() if norm(token)]
    if not words:
        return []
    ranked: list[tuple[int, dict]] = []
    for record in records:
        haystack = record_text(record)
        if not all(word in haystack for word in words):
            continue
        title = norm(local(record, "title", "en") + " " + local(record, "title", "el"))
        aliases = norm(" ".join(record.get("aliases", [])))
        queries = norm(" ".join(record.get("research_queries", [])))
        score = sum(
            10 if word in title else 5 if word in aliases else 3 if word in queries else 1
            for word in words
        )
        ranked.append((score, record))
    ranked.sort(
        key=lambda item: (
            -item[0],
            -int(item[1].get("year", 0)),
            local(item[1], "title", "en"),
        )
    )
    return [record for _, record in ranked]


def safe_filename(value: str, limit: int = 90) -> str:
    cleaned = re.sub(r"[^\w .()\-]+", "_", value, flags=re.UNICODE).strip(" ._")
    return (cleaned or "case")[:limit]


def source_host(url: str) -> str:
    try:
        return urlparse(url).netloc.removeprefix("www.") or url
    except Exception:
        return url


def image_kind(relative_path: str, credits: dict[str, dict]) -> str:
    if relative_path in credits:
        return "EVENT / SOURCE PHOTO"
    name = Path(relative_path).name.casefold()
    if "research-guide" in name:
        return "GENERATED RESEARCH GUIDE"
    return "GENERATED ARCHIVE VISUAL"


def archive_completeness(record: dict) -> int:
    score = 15
    score += min(22, len(record.get("sources") or []) * 5)
    score += 10 if len(local_list(record, "full_story", "en")) >= 6 else 0
    score += 8 if local_list(record, "details", "en") else 0
    score += 8 if local_list(record, "timeline", "en") else 0
    score += 8 if local_list(record, "facts", "en") else 0
    score += 8 if len(local_list(record, "full_story", "el")) >= 6 else 0
    score += 5 if local_list(record, "details", "el") else 0
    score += 5 if local_list(record, "timeline", "el") else 0
    score += 5 if local_list(record, "facts", "el") else 0
    score += 6 if local_list(record, "key_questions", "en") and local_list(record, "key_questions", "el") else 0
    score += 6 if local_list(record, "investigation_plan", "en") and local_list(record, "investigation_plan", "el") else 0
    score += 6 if local(record, "source_gap", "en") and local(record, "source_gap", "el") else 0
    score += 4 if local_list(record, "aftermath_legacy", "en") and local_list(record, "aftermath_legacy", "el") else 0
    score += 4 if local_list(record, "accountability_map", "en") and local_list(record, "accountability_map", "el") else 0
    score += 4 if local_list(record, "primary_record_targets", "en") and local_list(record, "primary_record_targets", "el") else 0
    score += 6 if len(record.get("images") or []) >= 4 else 3 if len(record.get("images") or []) >= 3 else 0
    sources = len(record.get("sources") or [])
    cap = 72 if sources == 0 else 84 if sources == 1 else 92 if sources == 2 else 100
    return min(cap, score)


def research_priority(record: dict) -> int:
    priority = 0
    if not record.get("sources"):
        priority += 8
    elif len(record.get("sources") or []) == 1:
        priority += 3
    if not local_list(record, "details", "en"):
        priority += 3
    if not local_list(record, "timeline", "en"):
        priority += 3
    if not local_list(record, "facts", "en"):
        priority += 3
    if not local_list(record, "details", "el"):
        priority += 2
    if not local_list(record, "timeline", "el"):
        priority += 2
    if not local_list(record, "facts", "el"):
        priority += 2
    if record.get("evidence_level") == "needs-sources":
        priority += 5
    return priority


def open_url(url: str) -> None:
    """Open a URL through Android from Termux."""
    if shutil.which("termux-open-url"):
        try:
            subprocess.Popen(
                ["termux-open-url", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        except OSError:
            pass
    print(color("warn", "Could not launch Android browser / Δεν άνοιξε ο browser."))
    print(url)


def open_path(path: Path) -> bool:
    """Open a file with Android's app chooser from Termux."""
    path = Path(path)
    if not path.exists():
        print(color("bad", "File not found / Το αρχείο δεν βρέθηκε."))
        return False
    if shutil.which("termux-open"):
        for command in (["termux-open", "--chooser", "--view", str(path)], ["termux-open", "--view", str(path)], ["termux-open", str(path)]):
            try:
                subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except OSError:
                continue
    print(color("warn", "termux-open is unavailable. File path:"))
    print(path)
    return False

def local_project_path(relative: object) -> Path | None:
    """Resolve a repository-relative path without allowing directory traversal."""
    text = str(relative or "").strip()
    if not text or Path(text).is_absolute():
        return None
    try:
        path = (APP_DIR / text).resolve()
        path.relative_to(APP_DIR.resolve())
    except (OSError, ValueError):
        return None
    return path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def offline_material_menu(record: dict, lang: str) -> None:
    """List and open the local article, documents, images and videos attached to a case."""
    materials = list(record.get("offline_materials") or [])
    if not materials:
        print("No offline files / Δεν υπάρχουν offline αρχεία.")
        pause()
        return
    while True:
        banner(lang)
        print(color("accent", "Offline case files" if lang == "en" else "Offline αρχεία υπόθεσης"))
        print(color("title", local(record, "title", lang)))
        line()
        for index, item in enumerate(materials, 1):
            relative = str(item.get("path", ""))
            path = local_project_path(relative)
            status = "OK" if path and path.is_file() and path.stat().st_size > 0 else "MISSING"
            kind = str(item.get("type", "file")).upper()
            title = local(item, "title", lang) or Path(relative).name
            print(f"{index:>2}. [{kind}] {title} — {status}")
            description = local(item, "description", lang)
            if description:
                wrap(description, "    ")
            license_text = str(item.get("license", "")).strip()
            if license_text:
                wrap(("Rights/license: " if lang == "en" else "Δικαιώματα/άδεια: ") + license_text, "    ")
            wrap(relative, "    ")
        line()
        print("Number = open file / Αριθμός = άνοιγμα αρχείου  [Enter] Back")
        choice = input("> ").strip()
        if not choice:
            return
        if choice.isdigit() and 1 <= int(choice) <= len(materials):
            item = materials[int(choice) - 1]
            path = local_project_path(item.get("path"))
            if path and path.is_file():
                open_path(path)
            else:
                print(color("bad", "Offline file missing / Το offline αρχείο λείπει."))
            pause()


def public_pictures_root() -> Path | None:
    candidates = [
        Path.home() / "storage" / "pictures",
        Path("/storage/emulated/0/Pictures"),
    ]
    for candidate in candidates:
        try:
            if candidate.exists() and candidate.is_dir() and os.access(candidate, os.W_OK):
                return candidate
        except OSError:
            continue
    return None


def scan_media(path: Path) -> None:
    if not IS_TERMUX:
        return
    uri = path.resolve().as_uri()
    if shutil.which("am"):
        try:
            subprocess.Popen(
                [
                    "am",
                    "broadcast",
                    "-a",
                    "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
                    "-d",
                    uri,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError:
            pass


def write_album_notes(
    album: Path,
    record: dict,
    copied: list[tuple[str, Path]],
    credits: dict[str, dict],
) -> None:
    lines = [
        local(record, "title", "en"),
        "=" * 72,
        f"ID: {record.get('id')}",
        f"Country: {record.get('country')} | Year: {record.get('year')}",
        "",
        "IMAGE NOTES AND CREDITS",
        "- Generated archive visuals are explanatory graphics, not event photographs.",
        "- Credited photographs retain the license shown below.",
        "",
    ]
    for relative, destination in copied:
        entry = credits.get(relative)
        lines.append(destination.name)
        if entry:
            lines.extend(
                [
                    f"  Description: {entry.get('description', entry.get('event', ''))}",
                    f"  Author: {entry.get('author', 'Unknown')}",
                    f"  License: {entry.get('license', 'See source page')}",
                    f"  Source: {entry.get('source_page', '')}",
                ]
            )
        else:
            lines.append("  Generated by the Corrupted Files Project visual system.")
        lines.append("")
    try:
        (album / "IMAGE-CREDITS.txt").write_text("\n".join(lines), encoding="utf-8")
    except OSError:
        pass


def export_case_images(
    record: dict, credits: dict[str, dict], announce: bool = True
) -> list[tuple[str, Path]]:
    root = public_pictures_root()
    if root is None:
        if announce:
            print(
                color(
                    "warn",
                    "Phone Pictures access is not ready. In Termux run: termux-setup-storage",
                )
            )
            print(
                "Then allow storage access and try again. Direct opening will still be attempted."
            )
        return []
    album_name = safe_filename(
        f"{record.get('year')} - {local(record, 'title', 'en')} - {record.get('id')}"
    )
    album = root / GALLERY_FOLDER_NAME / album_name
    album.mkdir(parents=True, exist_ok=True)
    copied: list[tuple[str, Path]] = []
    for index, relative in enumerate(record.get("images") or [], 1):
        source = APP_DIR / relative
        if not source.is_file():
            continue
        destination = album / f"{index:02d} - {safe_filename(source.name, 120)}"
        try:
            if not destination.exists() or destination.stat().st_size != source.stat().st_size:
                shutil.copy2(source, destination)
            copied.append((relative, destination))
            scan_media(destination)
        except OSError:
            continue
    write_album_notes(album, record, copied, credits)
    if announce and copied:
        print(color("good", f"Gallery album prepared: {album}"))
        print("The first image will open; swipe in your gallery to view the rest.")
    return copied


def open_image_with_gallery(path: Path, chooser: bool = True) -> bool:
    path = Path(path)
    if not path.is_file():
        print(color("bad", "Image not found / Η εικόνα δεν βρέθηκε."))
        return False
    mime = mimetypes.guess_type(path.name)[0] or "image/*"
    if IS_TERMUX and shutil.which("termux-open"):
        commands = []
        if chooser:
            commands.append(
                [
                    "termux-open",
                    "--chooser",
                    "--view",
                    "--content-type",
                    mime,
                    str(path),
                ]
            )
        commands.extend(
            [
                ["termux-open", "--view", "--content-type", mime, str(path)],
                ["termux-open", "--view", str(path)],
            ]
        )
        for command in commands:
            try:
                subprocess.Popen(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except OSError:
                continue
    return open_path(path)


def open_case_gallery(
    record: dict,
    credits: dict[str, dict],
    image_index: int = 0,
    chooser: bool = True,
) -> bool:
    images = record.get("images") or []
    if not images:
        print(color("warn", "This case has no images / Δεν υπάρχουν εικόνες."))
        return False
    image_index = max(0, min(image_index, len(images) - 1))
    if IS_TERMUX:
        copied = export_case_images(record, credits, announce=True)
        if copied:
            index = min(image_index, len(copied) - 1)
            return open_image_with_gallery(copied[index][1], chooser=chooser)
    return open_image_with_gallery(APP_DIR / images[image_index], chooser=chooser)


def items(title: str, values: list[str]) -> None:
    if not values:
        return
    print("\n" + color("accent", title))
    line()
    for value in values:
        wrap("• " + value)


def rumors_block(record: dict, lang: str) -> None:
    rumors = record.get("rumors") or []
    if not rumors:
        return
    heading = (
        "RUMORS, MISCONCEPTIONS & DISPUTED CLAIMS"
        if lang == "en"
        else "ΦΗΜΕΣ, ΠΑΡΑΝΟΗΣΕΙΣ & ΑΜΦΙΣΒΗΤΟΥΜΕΝΟΙ ΙΣΧΥΡΙΣΜΟΙ"
    )
    print("\n" + color("warn", heading))
    line()
    method = local(record, "rumor_method", lang)
    if method:
        wrap(method)
        print()
    for index, rumor in enumerate(rumors, 1):
        kind = str(rumor.get("type", "case-specific-rumor"))
        wrap(f"{index}. {local(rumor, 'claim', lang)}")
        wrap(("Type: " if lang == "en" else "Τύπος: ") + kind, "   ")
        wrap(("Status: " if lang == "en" else "Κατάσταση: ") + rumor_status_text(rumor, lang), "   ")
        wrap(local(rumor, "assessment", lang), "   ")
        if index < len(rumors):
            print()


def export_record(record: dict, lang: str) -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    safe = safe_filename(str(record["id"]))
    path = EXPORT_DIR / f"{safe}-{lang}.txt"
    output = [
        local(record, "title", lang),
        "=" * 72,
        f"ID: {record['id']}",
        f"Country: {record.get('country')} | Year: {record.get('year')}",
        f"Category: {local(record, 'category', lang)}",
        f"Evidence: {local(record, 'evidence', lang)}",
        f"Tier: {evidence_label(record.get('evidence_level', ''), lang)}",
        f"Archive completeness: {archive_completeness(record)}%",
        "",
        local(record, "summary", lang),
    ]
    labels = {
        "full_story": ("Full story", "Πλήρης αφήγηση"),
        "details": ("Details", "Λεπτομέρειες"),
        "deep_dive": ("Deep dive", "Εμβάθυνση"),
        "aftermath_legacy": ("Aftermath and legacy", "Συνέπειες και κληρονομιά"),
        "accountability_map": ("Accountability map", "Χάρτης λογοδοσίας"),
        "primary_record_targets": ("Primary-record targets", "Στόχοι πρωτογενών τεκμηρίων"),
        "people_institutions": ("People and institutions", "Πρόσωπα και θεσμοί"),
        "evidence_conflicts": ("Evidence conflicts and uncertainty", "Συγκρούσεις τεκμηρίων και αβεβαιότητα"),
        "media_memory": ("Media framing and public memory", "Μέσα ενημέρωσης και δημόσια μνήμη"),
        "next_reading_path": ("Next reading path", "Επόμενη διαδρομή μελέτης"),
        "timeline": ("Timeline", "Χρονολόγιο"),
        "facts": ("Key facts", "Βασικά στοιχεία"),
        "key_questions": ("Questions to test", "Ερωτήματα προς έλεγχο"),
        "investigation_plan": ("Investigation plan", "Σχέδιο έρευνας"),
        "verification_notes": ("Verification safeguards", "Κανόνες επαλήθευσης"),
    }
    for field, (english, greek) in labels.items():
        values = local_list(record, field, lang)
        if values:
            output += ["", english if lang == "en" else greek] + ["- " + item for item in values]
    gap = local(record, "source_gap", lang)
    if gap:
        output += ["", "Source gap" if lang == "en" else "Κενό πηγών", gap]
    if record.get("merged_from_ids"):
        output += ["", "Merged archive records / Συγχωνευμένες εγγραφές"] + [
            "- " + str(item) for item in record.get("merged_from_ids", [])
        ]
    if record.get("rumors"):
        output += [
            "",
            "Rumors & disputed claims" if lang == "en" else "Φήμες & αμφισβητούμενοι ισχυρισμοί",
        ]
        for rumor in record["rumors"]:
            output += [
                f"- {local(rumor, 'claim', lang)} [{rumor_status_text(rumor, lang)}]",
                "  " + local(rumor, "assessment", lang),
            ]
    if record.get("research_queries"):
        output += ["", "Research queries / Ερωτήματα έρευνας"] + [
            "- " + str(query) for query in record["research_queries"]
        ]
    if record.get("source_leads"):
        output += ["", "Source discovery leads / Αφετηρίες εντοπισμού πηγών"]
        for lead in record.get("source_leads", []):
            label = local(lead, "label", lang)
            value = lead.get("url") or lead.get("query") or ""
            output.append(f"- {label}: {value}")
    if record.get("research_portals"):
        output += ["", "Research portals / Ερευνητικές πύλες"]
        for portal in record.get("research_portals", []):
            output += [
                f"- {local(portal, 'name', lang)}: {portal.get('url', '')}",
                "  " + local(portal, "purpose", lang),
            ]
    if record.get("sources"):
        output += ["", "Sources / Πηγές"] + list(record["sources"])
    path.write_text("\n".join(output) + "\n", encoding="utf-8")
    html_path = export_record_html(record, lang)
    print(color("good", f"Text exported: {path}"))
    print(color("good", f"HTML dossier exported: {html_path}"))


def show_image_credits(record: dict, lang: str, credits: dict[str, dict]) -> None:
    banner(lang)
    print(color("title", local(record, "title", lang)))
    print(color("accent", "IMAGE DETAILS / ΣΤΟΙΧΕΙΑ ΕΙΚΟΝΩΝ"))
    line()
    for index, relative in enumerate(record.get("images") or [], 1):
        print(f"{index}. {Path(relative).name}")
        print(f"   Type: {image_kind(relative, credits)}")
        entry = credits.get(relative)
        if entry:
            if entry.get("description"):
                wrap("Description: " + str(entry["description"]), "   ")
            if entry.get("author"):
                wrap("Author: " + str(entry["author"]), "   ")
            if entry.get("license"):
                wrap("License: " + str(entry["license"]), "   ")
            if entry.get("source_page"):
                wrap("Source page: " + str(entry["source_page"]), "   ")
        else:
            wrap(
                "Generated explanatory visual; it is not presented as a photograph of the event.",
                "   ",
            )
        print()
    pause()


def image_menu(record: dict, lang: str, credits: dict[str, dict]) -> None:
    images = record.get("images") or []
    while True:
        banner(lang)
        print(color("title", local(record, "title", lang)))
        print(
            color(
                "accent",
                "OPEN WITH PHONE GALLERY"
                if lang == "en"
                else "ΑΝΟΙΓΜΑ ΜΕ ΤΗ ΣΥΛΛΟΓΗ ΤΟΥ ΚΙΝΗΤΟΥ",
            )
        )
        line()
        for index, relative in enumerate(images, 1):
            kind = image_kind(relative, credits)
            print(f"{index:>2}. {Path(relative).name} [{kind}]")
        line()
        print("Enter a number to open that image in the Gallery app.")
        print("[A] Export all images to Pictures and open as an album")
        print("[C] Image credits and license details")
        print("[Enter] Back")
        choice = input("> ").strip().lower()
        if not choice:
            return
        if choice.isdigit() and 1 <= int(choice) <= len(images):
            open_case_gallery(record, credits, int(choice) - 1, chooser=True)
            pause("Gallery launch requested. Press Enter to return...")
        elif choice == "a":
            open_case_gallery(record, credits, 0, chooser=True)
            pause("Gallery album prepared. Press Enter to return...")
        elif choice == "c":
            show_image_credits(record, lang, credits)



def related_cases(record: dict, limit: int = 8) -> list[dict]:
    title_words = set(norm(local(record, "title", "en") + " " + local(record, "category", "en")).split())
    weak = {"greece", "usa", "case", "state", "event", "public", "political", "and", "the", "of", "in"}
    title_words -= weak
    ranked: list[tuple[float, dict]] = []
    for other in GLOBAL_RECORDS:
        if other.get("id") == record.get("id"):
            continue
        other_words = set(norm(local(other, "title", "en") + " " + local(other, "category", "en")).split()) - weak
        shared = len(title_words & other_words)
        category_match = 2 if norm(local(other, "category", "en")) == norm(local(record, "category", "en")) else 0
        country_match = 1 if other.get("country") == record.get("country") else 0
        year_distance = abs(int(other.get("year", 0)) - int(record.get("year", 0)))
        proximity = max(0.0, 2.0 - min(year_distance, 40) / 20)
        score = shared * 3 + category_match + country_match + proximity
        if score >= 3:
            ranked.append((score, other))
    ranked.sort(key=lambda item: (-item[0], abs(int(item[1].get("year", 0)) - int(record.get("year", 0))), local(item[1], "title", "en")))
    return [item[1] for item in ranked[:limit]]


def research_notebook(record: dict, lang: str, state: dict) -> None:
    notes = state.setdefault("notes", {}).setdefault(record["id"], [])
    while True:
        banner(lang)
        print(color("title", local(record, "title", lang)))
        print(color("accent", "RESEARCH NOTEBOOK" if lang == "en" else "ΣΗΜΕΙΩΜΑΤΑΡΙΟ ΕΡΕΥΝΑΣ"))
        line()
        if notes:
            for index, entry in enumerate(notes, 1):
                stamp = entry.get("time", "") if isinstance(entry, dict) else ""
                text = entry.get("text", "") if isinstance(entry, dict) else str(entry)
                wrap(f"{index}. [{stamp}] {text}")
        else:
            print("No notes yet / Δεν υπάρχουν σημειώσεις.")
        line()
        print("[A] Add note  [D] Delete one  [X] Clear all  [Enter] Back")
        choice = input("> ").strip().lower()
        if not choice:
            save_state(state)
            return
        if choice == "a":
            text = input("Note / Σημείωση: ").strip()
            if text:
                notes.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "text": text})
                save_state(state)
        elif choice == "d" and notes:
            pick = input("Number / Αριθμός: ").strip()
            if pick.isdigit() and 1 <= int(pick) <= len(notes):
                notes.pop(int(pick) - 1)
                save_state(state)
        elif choice == "x" and notes:
            confirm = input("Type CLEAR / Γράψε CLEAR: ").strip()
            if confirm == "CLEAR":
                notes.clear()
                save_state(state)


def chronology_explorer(records: list[dict], lang: str, state: dict, credits: dict[str, dict]) -> None:
    banner(lang)
    print("1. Greece / Ελλάδα\n2. USA / ΗΠΑ\n3. Both / Και τα δύο")
    choice = input("> ").strip()
    selected = records
    if choice == "1":
        selected = [r for r in records if r.get("country") == "Greece"]
    elif choice == "2":
        selected = [r for r in records if r.get("country") == "USA"]
    start = input("Start year / Έτος αρχής (blank = all): ").strip()
    end = input("End year / Έτος τέλους (blank = all): ").strip()
    if start.isdigit():
        selected = [r for r in selected if int(r.get("year", 0)) >= int(start)]
    if end.isdigit():
        selected = [r for r in selected if int(r.get("year", 0)) <= int(end)]
    selected.sort(key=lambda r: (int(r.get("year", 0)), r.get("country", ""), local(r, "title", "en")))
    choose(selected, lang, state, credits, "Chronology / Χρονολόγιο")

def show_record(record: dict, lang: str, state: dict, credits: dict[str, dict]) -> None:
    history = state.setdefault("history", [])
    if record["id"] in history:
        history.remove(record["id"])
    history.insert(0, record["id"])
    del history[50:]
    save_state(state)

    while True:
        banner(lang)
        print(color("title", local(record, "title", lang)))
        line()
        bookmarked = record["id"] in state.get("bookmarks", [])
        photo_count = sum(1 for image in record.get("images", []) if image in credits)
        print(f"ID: {record.get('id')}")
        print(f"{record.get('country')} • {record.get('year')} • {local(record, 'category', lang)}")
        print(color("warn", evidence_label(record.get("evidence_level", ""), lang)))
        narrative_level = str(record.get("narrative_level", "unknown"))
        print(("Narrative level: " if lang == "en" else "Επίπεδο αφήγησης: ") + narrative_level)
        is_read = record["id"] in state.get("read_cases", [])
        print(
            f"Archive completeness: {archive_completeness(record)}% • "
            f"Reading: {reading_minutes(record, lang)} min • "
            f"Images: {len(record.get('images') or [])} • Credited photos: {photo_count} • "
            f"Offline files: {len(record.get('offline_materials') or [])}"
        )
        print(("Source strength: " if lang == "en" else "Ισχύς πηγών: ") + source_strength_label(record, lang))
        print(("Topics: " if lang == "en" else "Θέματα: ") + ", ".join(topic_names(record, lang)))
        print("Bookmark: " + (color("good", "YES") if bookmarked else "No") + " • " + ("Read: " if lang == "en" else "Διαβάστηκε: ") + (color("good", "YES") if is_read else "No"))
        print("\n" + textwrap.fill(local(record, "summary", lang), WIDTH))
        case_brief_block(record, lang)
        items("Full story" if lang == "en" else "Πλήρης αφήγηση", local_list(record, "full_story", lang))
        items("Details" if lang == "en" else "Λεπτομέρειες", local_list(record, "details", lang))
        items("Deep dive" if lang == "en" else "Εμβάθυνση", local_list(record, "deep_dive", lang))
        items("Aftermath and legacy" if lang == "en" else "Συνέπειες και κληρονομιά", local_list(record, "aftermath_legacy", lang))
        items("Accountability map" if lang == "en" else "Χάρτης λογοδοσίας", local_list(record, "accountability_map", lang))
        items("Primary-record targets" if lang == "en" else "Στόχοι πρωτογενών τεκμηρίων", local_list(record, "primary_record_targets", lang))
        items("People and institutions" if lang == "en" else "Πρόσωπα και θεσμοί", local_list(record, "people_institutions", lang))
        items("Evidence conflicts and uncertainty" if lang == "en" else "Συγκρούσεις τεκμηρίων και αβεβαιότητα", local_list(record, "evidence_conflicts", lang))
        items("Media framing and public memory" if lang == "en" else "Μέσα ενημέρωσης και δημόσια μνήμη", local_list(record, "media_memory", lang))
        items("Next reading path" if lang == "en" else "Επόμενη διαδρομή μελέτης", local_list(record, "next_reading_path", lang))
        items("Timeline" if lang == "en" else "Χρονολόγιο", local_list(record, "timeline", lang))
        items("Key facts" if lang == "en" else "Βασικά στοιχεία", local_list(record, "facts", lang))
        items("Questions to test" if lang == "en" else "Ερωτήματα προς έλεγχο", local_list(record, "key_questions", lang))
        items("Investigation plan" if lang == "en" else "Σχέδιο έρευνας", local_list(record, "investigation_plan", lang))
        items("Verification safeguards" if lang == "en" else "Κανόνες επαλήθευσης", local_list(record, "verification_notes", lang))
        gap = local(record, "source_gap", lang)
        if gap:
            print("\n" + color("warn", "Source gap" if lang == "en" else "Κενό πηγών"))
            line()
            wrap(gap)
        rumors_block(record, lang)
        aliases = [str(alias) for alias in record.get("aliases", [])]
        items("Aliases" if lang == "en" else "Εναλλακτικές ονομασίες", aliases)
        items(
            "Research starters" if lang == "en" else "Αφετηρίες έρευνας",
            [str(query) for query in record.get("research_queries", [])],
        )
        items(
            "Merged archive records" if lang == "en" else "Συγχωνευμένες αρχειακές εγγραφές",
            [str(item) for item in record.get("merged_from_ids", [])],
        )
        if record.get("research_portals"):
            print("\n" + color("accent", "Research portals" if lang == "en" else "Ερευνητικές πύλες"))
            line()
            for index, portal in enumerate(record.get("research_portals", []), 1):
                wrap(f"{index}. {local(portal, 'name', lang)} — {portal.get('url', '')}")
                wrap(local(portal, "purpose", lang), "   ")
        if record.get("source_leads"):
            print("\n" + color("accent", "Source-discovery leads" if lang == "en" else "Αφετηρίες εντοπισμού πηγών"))
            line()
            for index, lead in enumerate(record.get("source_leads", []), 1):
                label = local(lead, "label", lang)
                target = lead.get("url") or lead.get("query") or ""
                wrap(f"{index}. {label} — {target}")
        editorial = record.get("editorial_review", {})
        if isinstance(editorial, dict):
            note = editorial.get("note", {})
            text = note.get(lang) or note.get("en") if isinstance(note, dict) else ""
            if text:
                print("\n" + color("dim", "Editorial review / Συντακτικός έλεγχος"))
                wrap(text)
        if record.get("sources"):
            print("\n" + color("accent", "Sources" if lang == "en" else "Πηγές"))
            line()
            for index, source in enumerate(record["sources"], 1):
                wrap(f"{index}. [{source_host(source)}] {source}")
        images = record.get("images") or []
        if images:
            print("\n" + color("accent", "Images" if lang == "en" else "Εικόνες"))
            line()
            for index, relative in enumerate(images, 1):
                print(f"{index}. {Path(relative).name} — {image_kind(relative, credits)}")
        line("═")
        print("[B] Bookmark  [M] Mark read/unread  [G] Gallery app  [S] Source")
        print("[F] Offline files  [E] Export TXT + HTML  [R] Related cases  [N] Research notes")
        print("[O] Open gallery album")
        print("[P] Research portal")
        print("[C] Image credits  [Enter] Back")
        choice = input("> ").strip().lower()
        if not choice:
            return
        if choice == "b":
            bookmarks = state.setdefault("bookmarks", [])
            record_id = record["id"]
            if record_id in bookmarks:
                bookmarks.remove(record_id)
                print("Bookmark removed / Ο σελιδοδείκτης αφαιρέθηκε")
            else:
                bookmarks.append(record_id)
                print("Bookmark added / Προστέθηκε σελιδοδείκτης")
            save_state(state)
            pause()
        elif choice == "m":
            read_cases = state.setdefault("read_cases", [])
            if record["id"] in read_cases:
                read_cases.remove(record["id"])
                print("Marked unread / Σημειώθηκε ως αδιάβαστη")
            else:
                read_cases.append(record["id"])
                print("Marked read / Σημειώθηκε ως διαβασμένη")
            save_state(state)
            pause()
        elif choice == "g" and images:
            image_menu(record, lang, credits)
        elif choice == "c" and images:
            show_image_credits(record, lang, credits)
        elif choice == "s" and record.get("sources"):
            pick = input("Source number: ").strip()
            if pick.isdigit() and 1 <= int(pick) <= len(record["sources"]):
                open_url(record["sources"][int(pick) - 1])
            pause()
        elif choice == "f":
            offline_material_menu(record, lang)
        elif choice == "e":
            export_record(record, lang)
            pause()
        elif choice == "r":
            choose(related_cases(record), lang, state, credits, "Related cases / Σχετικές υποθέσεις")
        elif choice == "n":
            research_notebook(record, lang, state)
        elif choice == "o" and images:
            copied = export_case_images(record, credits, announce=True)
            if copied:
                open_path(copied[0][1].parent)
            pause()
        elif choice == "p" and record.get("research_portals"):
            pick = input("Portal number / Αριθμός πύλης: ").strip()
            portals = record.get("research_portals", [])
            if pick.isdigit() and 1 <= int(pick) <= len(portals):
                open_url(str(portals[int(pick) - 1].get("url", "")))
            pause()


def choose(
    records: list[dict],
    lang: str,
    state: dict,
    credits: dict[str, dict],
    title: str = "Results",
) -> None:
    if not records:
        print("\nNo results / Δεν βρέθηκαν αποτελέσματα.")
        pause()
        return
    offset = 0
    size = 12
    while True:
        banner(lang)
        print(color("accent", f"{title} — {len(records)}"))
        page = records[offset : offset + size]
        for index, record in enumerate(page, 1):
            rumor = " ⚠" if record.get("rumors") else ""
            event_photo = " 📷" if any(image in credits for image in record.get("images", [])) else ""
            completeness = archive_completeness(record)
            print(
                f"{index:>2}. [{record.get('year')}] {local(record, 'title', lang)}"
                f"{rumor}{event_photo} [{completeness}%]"
            )
        line()
        print("[N] Next  [P] Previous  [Enter] Back")
        choice = input("> ").strip().lower()
        if not choice:
            return
        if choice == "n" and offset + size < len(records):
            offset += size
        elif choice == "p" and offset > 0:
            offset = max(0, offset - size)
        elif choice.isdigit() and 1 <= int(choice) <= len(page):
            show_record(page[int(choice) - 1], lang, state, credits)


def browse(records: list[dict], lang: str, state: dict, credits: dict[str, dict]) -> None:
    banner(lang)
    print("1. Greece / Ελλάδα\n2. USA / ΗΠΑ\n3. Both / Και τα δύο")
    choice = input("> ").strip()
    country = {"1": "Greece", "2": "USA"}.get(choice)
    pool = [record for record in records if not country or record.get("country") == country]
    banner(lang)
    print("1. By decade / Ανά δεκαετία")
    print("2. By category / Ανά κατηγορία")
    print("3. By evidence tier / Ανά επίπεδο τεκμηρίωσης")
    print("4. With credited event photographs / Με τεκμηριωμένες φωτογραφίες")
    print("5. All chronological / Όλα χρονολογικά")
    mode = input("> ").strip()
    if mode == "1":
        decades = sorted({(int(record.get("year", 0)) // 10) * 10 for record in pool})
        for index, decade in enumerate(decades, 1):
            print(f"{index}. {decade}s")
        selected = input("> ").strip()
        if selected.isdigit() and 1 <= int(selected) <= len(decades):
            decade = decades[int(selected) - 1]
            choose(
                [record for record in pool if decade <= int(record.get("year", 0)) < decade + 10],
                lang,
                state,
                credits,
                f"{decade}s",
            )
    elif mode == "2":
        categories = Counter(local(record, "category", lang) for record in pool)
        choices = [category for category, _ in categories.most_common()]
        for index, category in enumerate(choices, 1):
            print(f"{index}. {category} ({categories[category]})")
        selected = input("> ").strip()
        if selected.isdigit() and 1 <= int(selected) <= len(choices):
            category = choices[int(selected) - 1]
            choose(
                [record for record in pool if local(record, "category", lang) == category],
                lang,
                state,
                credits,
                category,
            )
    elif mode == "3":
        tiers = sorted({record.get("evidence_level", "") for record in pool})
        for index, tier in enumerate(tiers, 1):
            print(f"{index}. {evidence_label(tier, lang)}")
        selected = input("> ").strip()
        if selected.isdigit() and 1 <= int(selected) <= len(tiers):
            tier = tiers[int(selected) - 1]
            choose(
                [record for record in pool if record.get("evidence_level") == tier],
                lang,
                state,
                credits,
                evidence_label(tier, lang),
            )
    elif mode == "4":
        choose(
            [record for record in pool if any(image in credits for image in record.get("images", []))],
            lang,
            state,
            credits,
            "Credited event photographs",
        )
    elif mode == "5":
        choose(
            sorted(pool, key=lambda record: (record.get("year", 0), local(record, "title", lang))),
            lang,
            state,
            credits,
        )


def stats(records: list[dict], lang: str, credits: dict[str, dict]) -> None:
    banner(lang)
    print(color("title", "ARCHIVE STATISTICS" if lang == "en" else "ΣΤΑΤΙΣΤΙΚΑ ΑΡΧΕΙΟΥ"))
    line()
    image_paths = [image for record in records for image in (record.get("images") or [])]
    gallery_ready = sum(Path(image).suffix.casefold() in GALLERY_EXTENSIONS for image in image_paths)
    print(f"Cases / Υποθέσεις: {len(records)}")
    print(f"Greece / Ελλάδα: {sum(record.get('country') == 'Greece' for record in records)}")
    print(f"USA / ΗΠΑ: {sum(record.get('country') == 'USA' for record in records)}")
    print(f"Rumor cards / Κάρτες φημών: {sum(len(record.get('rumors') or []) for record in records)}")
    print(f"Image references / Αναφορές εικόνων: {len(image_paths)}")
    print(f"Gallery-compatible images / Εικόνες συμβατές με Gallery: {gallery_ready}")
    print(f"Credited event/source photos / Φωτογραφίες με άδεια: {len(credits)}")
    print(f"Cases with sources / Υποθέσεις με πηγές: {sum(bool(record.get('sources')) for record in records)}")
    print(f"New in v6.0 / Νέα στην v6.0: {sum(str(record.get('added_in_version', '')) == '6.0' for record in records)}")
    print(f"Aftermath sections / Ενότητες συνεπειών: {sum(bool(local_list(record, 'aftermath_legacy', 'en') and local_list(record, 'aftermath_legacy', 'el')) for record in records)}")
    print(f"Accountability maps / Χάρτες λογοδοσίας: {sum(bool(local_list(record, 'accountability_map', 'en') and local_list(record, 'accountability_map', 'el')) for record in records)}")
    print(f"Primary-record target sets / Σύνολα στόχων τεκμηρίων: {sum(bool(local_list(record, 'primary_record_targets', 'en') and local_list(record, 'primary_record_targets', 'el')) for record in records)}")
    print(f"People/institution maps / Χάρτες προσώπων και θεσμών: {sum(bool(local_list(record, 'people_institutions', 'en') and local_list(record, 'people_institutions', 'el')) for record in records)}")
    print(f"Evidence-conflict reviews / Έλεγχοι συγκρούσεων τεκμηρίων: {sum(bool(local_list(record, 'evidence_conflicts', 'en') and local_list(record, 'evidence_conflicts', 'el')) for record in records)}")
    print(f"Media-memory reviews / Έλεγχοι δημόσιας μνήμης: {sum(bool(local_list(record, 'media_memory', 'en') and local_list(record, 'media_memory', 'el')) for record in records)}")
    print(f"Reading paths / Διαδρομές μελέτης: {sum(bool(local_list(record, 'next_reading_path', 'en') and local_list(record, 'next_reading_path', 'el')) for record in records)}")
    average = round(sum(archive_completeness(record) for record in records) / max(1, len(records)), 1)
    print(f"Average archive completeness / Μέση πληρότητα: {average}%")
    print("\nEvidence tiers / Επίπεδα:")
    for key, value in Counter(record.get("evidence_level") for record in records).most_common():
        print(f"• {evidence_label(str(key), lang)}: {value}")
    pause()


def research_queue(records: list[dict], lang: str, state: dict, credits: dict[str, dict]) -> None:
    prioritized = sorted(
        [record for record in records if research_priority(record) > 0],
        key=lambda record: (-research_priority(record), record.get("year", 0)),
    )
    choose(
        prioritized,
        lang,
        state,
        credits,
        "Research priority queue / Ουρά ερευνητικής προτεραιότητας",
    )


def select_record(
    records: list[dict], lang: str, prompt: str
) -> dict | None:
    query = input(prompt).strip()
    matches = search(records, query)
    if not matches:
        print("No results / Δεν βρέθηκαν αποτελέσματα.")
        return None
    for index, record in enumerate(matches[:10], 1):
        print(f"{index}. [{record.get('year')}] {local(record, 'title', lang)}")
    selected = input("> ").strip()
    if selected.isdigit() and 1 <= int(selected) <= min(10, len(matches)):
        return matches[int(selected) - 1]
    return None


def compare_cases(records: list[dict], lang: str) -> None:
    banner(lang)
    first = select_record(records, lang, "First case search / Πρώτη υπόθεση: ")
    if not first:
        pause()
        return
    second = select_record(records, lang, "Second case search / Δεύτερη υπόθεση: ")
    if not second:
        pause()
        return
    banner(lang)
    print(color("title", "CASE COMPARISON / ΣΥΓΚΡΙΣΗ ΥΠΟΘΕΣΕΩΝ"))
    line()
    for label, record in (("A", first), ("B", second)):
        print(color("accent", f"{label}. {local(record, 'title', lang)}"))
        print(
            f"{record.get('country')} • {record.get('year')} • {local(record, 'category', lang)}"
        )
        print(
            f"Tier: {evidence_label(record.get('evidence_level', ''), lang)} | "
            f"Sources: {len(record.get('sources') or [])} | "
            f"Images: {len(record.get('images') or [])} | "
            f"Rumors: {len(record.get('rumors') or [])} | "
            f"Completeness: {archive_completeness(record)}%"
        )
        wrap(local(record, "summary", lang))
        print()
    year_gap = abs(int(first.get("year", 0)) - int(second.get("year", 0)))
    first_words = set(norm(local(first, "category", "en")).split())
    second_words = set(norm(local(second, "category", "en")).split())
    common = sorted(first_words & second_words)
    line()
    print(f"Year gap / Διαφορά ετών: {year_gap}")
    print("Shared category terms / Κοινοί όροι: " + (", ".join(common) if common else "none / κανένας"))
    pause()



COLLECTION_LABELS = {
    "surveillance-secrecy": ("Surveillance & secrecy", "Επιτήρηση & μυστικότητα"),
    "corruption-money": ("Corruption & public money", "Διαφθορά & δημόσιο χρήμα"),
    "state-violence": ("State violence & policing", "Κρατική βία & αστυνόμευση"),
    "disasters-safety": ("Disasters & safety failures", "Καταστροφές & αποτυχίες ασφάλειας"),
    "public-health": ("Public health & medical ethics", "Δημόσια υγεία & ιατρική ηθική"),
    "civil-rights": ("Civil rights & discrimination", "Πολιτικά δικαιώματα & διακρίσεις"),
    "war-foreign-policy": ("War, coups & foreign policy", "Πόλεμος, πραξικοπήματα & εξωτερική πολιτική"),
    "media-information": ("Media, propaganda & information", "Μέσα, προπαγάνδα & πληροφορία"),
    "technology-data": ("Technology, data & infrastructure", "Τεχνολογία, δεδομένα & υποδομές"),
    "labor-economy": ("Labor, economy & inequality", "Εργασία, οικονομία & ανισότητα"),
    "institutions-accountability": ("Institutions & accountability", "Θεσμοί & λογοδοσία"),
    "rumor-unexplained": ("Rumors, unexplained claims & public psychology", "Φήμες, ανεξήγητοι ισχυρισμοί & δημόσια ψυχολογία"),
}


def topic_keys(record: dict) -> list[str]:
    value = record.get("topic_tags", {})
    if isinstance(value, dict):
        return [str(item) for item in value.get("keys", [])]
    return []


def topic_names(record: dict, lang: str) -> list[str]:
    value = record.get("topic_tags", {})
    if isinstance(value, dict):
        names = value.get(lang) or value.get("en") or []
        return [str(item) for item in names]
    return []


def source_strength_label(record: dict, lang: str) -> str:
    value = record.get("source_strength", {})
    if isinstance(value, dict):
        label = value.get("label", {})
        if isinstance(label, dict):
            return str(label.get(lang) or label.get("en") or "")
    return ""


def reading_minutes(record: dict, lang: str) -> int:
    value = record.get("reading_metrics", {})
    if isinstance(value, dict):
        minutes = value.get("minutes", {})
        if isinstance(minutes, dict):
            try:
                return max(1, int(minutes.get(lang) or minutes.get("en") or 1))
            except (TypeError, ValueError):
                pass
    words = len(record_text(record).split())
    return max(1, (words + 209) // 210)


def case_brief_block(record: dict, lang: str) -> None:
    brief = record.get("case_brief", {})
    if not isinstance(brief, dict):
        return
    labels = {
        "focus": ("Core focus", "Κεντρικό θέμα"),
        "record_status": ("Record status", "Κατάσταση φακέλου"),
        "why_it_matters": ("Why it matters", "Γιατί έχει σημασία"),
        "disputed_or_missing": ("Disputed or missing", "Αμφισβητούμενα ή ελλιπή στοιχεία"),
        "next_step": ("Best next research step", "Καλύτερο επόμενο βήμα έρευνας"),
    }
    print("\n" + color("accent", "CASE BRIEF" if lang == "en" else "ΣΥΝΟΠΤΙΚΟΣ ΦΑΚΕΛΟΣ"))
    line()
    for key, pair in labels.items():
        value = brief.get(key, {})
        if isinstance(value, dict):
            text = str(value.get(lang) or value.get("en") or "").strip()
        else:
            text = str(value or "").strip()
        if text:
            print(color("dim", pair[0 if lang == "en" else 1] + ":"))
            wrap(text, "  ")


def html_list(title: str, values: list[str]) -> str:
    if not values:
        return ""
    lis = "".join(f"<li>{escape(str(item))}</li>" for item in values)
    return f"<section><h2>{escape(title)}</h2><ul>{lis}</ul></section>"


def export_record_html(record: dict, lang: str, credits: dict[str, dict] | None = None) -> Path:
    credits = credits or load_credits()
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    safe = safe_filename(str(record["id"]))
    folder = EXPORT_DIR / f"{safe}-{lang}-html"
    image_dir = folder / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    copied_images: list[tuple[str, str]] = []
    for index, relative in enumerate(record.get("images") or [], 1):
        source = APP_DIR / relative
        if not source.is_file():
            continue
        target = image_dir / f"{index:02d}-{safe_filename(source.name, 120)}"
        try:
            shutil.copy2(source, target)
            copied_images.append((relative, target.name))
        except OSError:
            continue
    title = local(record, "title", lang)
    labels = {
        "full_story": "Full story" if lang == "en" else "Πλήρης αφήγηση",
        "details": "Details" if lang == "en" else "Λεπτομέρειες",
        "deep_dive": "Deep dive" if lang == "en" else "Εμβάθυνση",
        "aftermath_legacy": "Aftermath and legacy" if lang == "en" else "Συνέπειες και κληρονομιά",
        "accountability_map": "Accountability map" if lang == "en" else "Χάρτης λογοδοσίας",
        "primary_record_targets": "Primary-record targets" if lang == "en" else "Στόχοι πρωτογενών τεκμηρίων",
        "people_institutions": "People and institutions" if lang == "en" else "Πρόσωπα και θεσμοί",
        "evidence_conflicts": "Evidence conflicts and uncertainty" if lang == "en" else "Συγκρούσεις τεκμηρίων και αβεβαιότητα",
        "media_memory": "Media framing and public memory" if lang == "en" else "Μέσα ενημέρωσης και δημόσια μνήμη",
        "next_reading_path": "Next reading path" if lang == "en" else "Επόμενη διαδρομή μελέτης",
        "timeline": "Timeline" if lang == "en" else "Χρονολόγιο",
        "facts": "Key facts" if lang == "en" else "Βασικά στοιχεία",
        "key_questions": "Questions to test" if lang == "en" else "Ερωτήματα προς έλεγχο",
        "investigation_plan": "Investigation plan" if lang == "en" else "Σχέδιο έρευνας",
        "verification_notes": "Verification safeguards" if lang == "en" else "Κανόνες επαλήθευσης",
    }
    body = [
        f"<h1>{escape(title)}</h1>",
        f"<p class='meta'><strong>ID:</strong> {escape(str(record.get('id')))} · "
        f"<strong>{'Country' if lang == 'en' else 'Χώρα'}:</strong> {escape(str(record.get('country')))} · "
        f"<strong>{'Year' if lang == 'en' else 'Έτος'}:</strong> {escape(str(record.get('year')))} · "
        f"<strong>{'Reading time' if lang == 'en' else 'Χρόνος ανάγνωσης'}:</strong> {reading_minutes(record, lang)} min</p>",
        f"<p class='summary'>{escape(local(record, 'summary', lang))}</p>",
        f"<p><strong>{'Source strength' if lang == 'en' else 'Ισχύς πηγών'}:</strong> {escape(source_strength_label(record, lang))}</p>",
        f"<p><strong>{'Topics' if lang == 'en' else 'Θέματα'}:</strong> {escape(', '.join(topic_names(record, lang)))}</p>",
    ]
    brief = record.get("case_brief", {})
    if isinstance(brief, dict):
        body.append("<section><h2>" + ("Case brief" if lang == "en" else "Συνοπτικός φάκελος") + "</h2>")
        for key in ("focus", "record_status", "why_it_matters", "disputed_or_missing", "next_step"):
            value = brief.get(key, {})
            text = value.get(lang) or value.get("en") if isinstance(value, dict) else value
            if text:
                body.append(f"<p><strong>{escape(key.replace('_', ' ').title())}:</strong> {escape(str(text))}</p>")
        body.append("</section>")
    for field, label in labels.items():
        body.append(html_list(label, local_list(record, field, lang)))
    gap = local(record, "source_gap", lang)
    if gap:
        body.append(f"<section><h2>{'Source gap' if lang == 'en' else 'Κενό πηγών'}</h2><p>{escape(gap)}</p></section>")
    if record.get("rumors"):
        rows=[]
        for rumor in record.get("rumors") or []:
            rows.append(
                "<article class='rumor'><h3>" + escape(local(rumor, "claim", lang)) + "</h3>"
                + f"<p><strong>Status:</strong> {escape(rumor_status_text(rumor, lang))}</p>"
                + f"<p>{escape(local(rumor, 'assessment', lang))}</p></article>"
            )
        body.append("<section><h2>" + ("Rumors, misconceptions & disputed claims" if lang == "en" else "Φήμες, παρανοήσεις & αμφισβητούμενοι ισχυρισμοί") + "</h2>" + "".join(rows) + "</section>")
    if record.get("sources"):
        links = "".join(f"<li><a href='{escape(str(url), quote=True)}'>{escape(str(url))}</a></li>" for url in record.get("sources") or [])
        body.append(f"<section><h2>{'Direct sources' if lang == 'en' else 'Άμεσες πηγές'}</h2><ol>{links}</ol></section>")
    if record.get("source_leads"):
        leads=[]
        for lead in record.get("source_leads") or []:
            label = local(lead, "label", lang)
            target = lead.get("url") or lead.get("query") or ""
            leads.append(f"<li>{escape(label)} — {escape(str(target))}</li>")
        body.append(f"<section><h2>{'Source-discovery leads' if lang == 'en' else 'Αφετηρίες εντοπισμού πηγών'}</h2><ul>{''.join(leads)}</ul></section>")
    if copied_images:
        cards=[]
        for relative, filename in copied_images:
            entry=credits.get(relative, {})
            caption = entry.get("description") or image_kind(relative, credits)
            credit=""
            if entry:
                credit=f"<small>{escape(str(entry.get('author','')))} · {escape(str(entry.get('license','')))}</small>"
            cards.append(f"<figure><img src='images/{escape(filename, quote=True)}' alt='{escape(str(caption), quote=True)}'><figcaption>{escape(str(caption))}{credit}</figcaption></figure>")
        body.append(f"<section><h2>{'Images' if lang == 'en' else 'Εικόνες'}</h2><div class='gallery'>{''.join(cards)}</div></section>")
    style="""
    :root{color-scheme:dark}body{margin:0;background:#090b0f;color:#e8edf2;font-family:system-ui,sans-serif;line-height:1.65}main{max-width:980px;margin:auto;padding:28px}h1,h2{color:#d58cff}h2{border-bottom:1px solid #343946;padding-bottom:6px}a{color:#75d8ff}.meta,.summary,section{background:#11151d;border:1px solid #2a3140;padding:16px;margin:16px 0}.summary{font-size:1.08rem}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}.gallery figure{margin:0;background:#0c1017;border:1px solid #2a3140;padding:9px}.gallery img{width:100%;height:auto;display:block}.gallery small{display:block;color:#aab4c3}.rumor{border-left:4px solid #dba642;padding-left:12px;margin:14px 0}footer{color:#9aa6b5;margin-top:30px}
    """
    document="<!doctype html><html lang='" + ("el" if lang == "el" else "en") + "'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>" + escape(title) + "</title><style>" + style + "</style></head><body><main>" + "".join(body) + "<footer>Corrupted Files Project · Offline export · Generated " + datetime.now().strftime("%Y-%m-%d %H:%M") + "</footer></main></body></html>"
    path=folder/"index.html"
    path.write_text(document, encoding="utf-8")
    return path


def export_archive_index(records: list[dict], lang: str = "en") -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORT_DIR / f"Corrupted-Files-Archive-Index-{lang}.html"
    cards=[]
    for record in sorted(records, key=lambda r: (r.get("country", ""), int(r.get("year", 0)), local(r, "title", "en"))):
        tags=", ".join(topic_names(record, lang))
        cards.append(
            f"<article data-search='{escape(norm(' '.join([str(record.get('id','')), str(record.get('country','')), str(record.get('year','')), local(record,'title','en'), local(record,'title','el'), local(record,'summary','en'), local(record,'summary','el'), ' '.join(record.get('aliases',[])), ' '.join(topic_names(record,'en')), ' '.join(topic_names(record,'el'))])), quote=True)}'>"
            f"<h2>{escape(local(record,'title',lang))}</h2>"
            f"<p class='meta'>{escape(str(record.get('country')))} · {escape(str(record.get('year')))} · {archive_completeness(record)}% · {reading_minutes(record,lang)} min</p>"
            f"<p>{escape(local(record,'summary',lang))}</p><p class='tags'>{escape(tags)}</p>"
            f"<code>{escape(str(record.get('id')))}</code></article>"
        )
    heading="Corrupted Files Project — Archive Index" if lang=="en" else "Corrupted Files Project — Ευρετήριο αρχείου"
    placeholder="Search titles, subjects, years or IDs" if lang=="en" else "Αναζήτηση τίτλων, θεμάτων, ετών ή ID"
    doc=f"""<!doctype html><html lang='{lang}'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{escape(heading)}</title><style>:root{{color-scheme:dark}}body{{background:#080a0e;color:#edf1f5;font-family:system-ui;margin:0}}main{{max-width:1050px;margin:auto;padding:24px}}h1,h2{{color:#d58cff}}input{{width:100%;box-sizing:border-box;padding:14px;background:#10151d;color:#fff;border:1px solid #374151;font-size:1rem;position:sticky;top:0}}article{{border:1px solid #28303c;background:#10141b;padding:16px;margin:12px 0}}article h2{{margin-top:0}}.meta,.tags,code{{color:#9fb1c5}}code{{word-break:break-all}}</style></head><body><main><h1>{escape(heading)}</h1><p>{len(records)} cases · Greece and USA · offline searchable index</p><input id='q' placeholder='{escape(placeholder, quote=True)}' autofocus><div id='cards'>{''.join(cards)}</div></main><script>const q=document.getElementById('q');const cards=[...document.querySelectorAll('article')];q.addEventListener('input',()=>{{const v=q.value.toLowerCase().trim();cards.forEach(c=>c.hidden=v&&!c.dataset.search.includes(v));}});</script></body></html>"""
    path.write_text(doc,encoding="utf-8")
    print(color("good", f"Archive index exported: {path}"))
    return path


def guided_collections(records: list[dict], lang: str, state: dict, credits: dict[str, dict]) -> None:
    while True:
        banner(lang)
        print(color("title", "GUIDED COLLECTIONS" if lang == "en" else "ΘΕΜΑΤΙΚΕΣ ΣΥΛΛΟΓΕΣ"))
        available=[]
        for key, labels in COLLECTION_LABELS.items():
            pool=[r for r in records if key in topic_keys(r)]
            if pool:
                available.append((key,labels,pool))
        for index, (_, labels, pool) in enumerate(available,1):
            print(f"{index}. {labels[0 if lang=='en' else 1]} ({len(pool)})")
        print("[Enter] Back")
        pick=input("> ").strip()
        if not pick: return
        if pick.isdigit() and 1<=int(pick)<=len(available):
            key,labels,pool=available[int(pick)-1]
            pool.sort(key=lambda r:(int(r.get('year',0)),local(r,'title','en')))
            choose(pool,lang,state,credits,labels[0 if lang=='en' else 1])


def progress_dashboard(records: list[dict], lang: str, state: dict, credits: dict[str, dict]) -> None:
    by_id={r['id']:r for r in records}
    while True:
        read_ids=[item for item in state.get('read_cases',[]) if item in by_id]
        unread=[r for r in records if r['id'] not in set(read_ids)]
        sessions=int(state.get('study_sessions',0)); total=int(state.get('study_total',0)); correct=int(state.get('study_correct',0))
        banner(lang)
        print(color('title','READING PROGRESS' if lang=='en' else 'ΠΡΟΟΔΟΣ ΑΝΑΓΝΩΣΗΣ'))
        line()
        print(f"{'Read' if lang=='en' else 'Διαβασμένες'}: {len(read_ids)}/{len(records)} ({round(len(read_ids)*100/max(1,len(records)),1)}%)")
        print(f"{'Unread' if lang=='en' else 'Αδιάβαστες'}: {len(unread)}")
        print(f"{'Bookmarks' if lang=='en' else 'Σελιδοδείκτες'}: {len(state.get('bookmarks',[]))}")
        print(f"{'Notebook cases' if lang=='en' else 'Υποθέσεις με σημειώσεις'}: {sum(bool(v) for v in state.get('notes',{}).values())}")
        score=round(correct*100/max(1,total),1) if total else 0
        print(f"{'Study sessions' if lang=='en' else 'Συνεδρίες μελέτης'}: {sessions} · {correct}/{total} ({score}%)")
        line()
        print("1. Unread cases / Αδιάβαστες υποθέσεις")
        print("2. Read cases / Διαβασμένες υποθέσεις")
        print("3. Study mode / Λειτουργία μελέτης")
        print("4. Reset reading progress / Μηδενισμός προόδου")
        print("[Enter] Back")
        choice=input("> ").strip()
        if not choice:return
        if choice=='1': choose(unread,lang,state,credits,'Unread / Αδιάβαστες')
        elif choice=='2': choose([by_id[i] for i in read_ids],lang,state,credits,'Read / Διαβασμένες')
        elif choice=='3': study_mode(records,lang,state,credits)
        elif choice=='4':
            confirm=input('Type RESET / Γράψε RESET: ').strip()
            if confirm=='RESET': state['read_cases']=[]; save_state(state)


def study_mode(records: list[dict], lang: str, state: dict, credits: dict[str, dict] | None = None) -> None:
    if len(records)<4:
        pause('Not enough cases / Δεν υπάρχουν αρκετές υποθέσεις.')
        return
    banner(lang)
    print('1. 5 questions\n2. 10 questions\n3. 20 questions')
    count={'1':5,'2':10,'3':20}.get(input('> ').strip(),5)
    count=min(count,len(records))
    pool=random.sample(records,count)
    correct=0
    for qnum,record in enumerate(pool,1):
        banner(lang)
        qtype=random.choice(['year','country','title'])
        if qtype=='year':
            question=(f"In which year is this archive case indexed?\n{local(record,'title',lang)}" if lang=='en' else f"Σε ποιο έτος είναι καταχωρισμένη αυτή η υπόθεση;\n{local(record,'title',lang)}")
            answer=str(record.get('year'))
            distractors={str(r.get('year')) for r in random.sample(records,min(len(records),20)) if str(r.get('year'))!=answer}
            options=[answer]+list(distractors)[:3]
        elif qtype=='country':
            question=(f"Which archive section contains this case?\n{local(record,'title',lang)}" if lang=='en' else f"Σε ποια ενότητα του αρχείου ανήκει η υπόθεση;\n{local(record,'title',lang)}")
            answer=str(record.get('country'))
            options=['Greece','USA']
        else:
            question=(f"Which case matches the year {record.get('year')} and this summary?\n{local(record,'summary',lang)}" if lang=='en' else f"Ποια υπόθεση αντιστοιχεί στο έτος {record.get('year')} και σε αυτή τη σύνοψη;\n{local(record,'summary',lang)}")
            answer=local(record,'title',lang)
            others=[r for r in records if r.get('id')!=record.get('id')]
            options=[answer]+[local(r,'title',lang) for r in random.sample(others,3)]
        random.shuffle(options)
        print(color('title',f"{qnum}/{count}")); line(); wrap(question)
        for i,opt in enumerate(options,1): print(f"{i}. {opt}")
        pick=input('> ').strip()
        selected=options[int(pick)-1] if pick.isdigit() and 1<=int(pick)<=len(options) else ''
        if selected==answer:
            print(color('good','Correct / Σωστό')); correct+=1
        else:
            print(color('bad','Incorrect / Λάθος')); wrap(('Answer: ' if lang=='en' else 'Απάντηση: ')+answer)
        input('Enter...')
    state['study_sessions']=int(state.get('study_sessions',0))+1
    state['study_total']=int(state.get('study_total',0))+count
    state['study_correct']=int(state.get('study_correct',0))+correct
    save_state(state)
    banner(lang)
    print(color('title',f"{correct}/{count} — {round(correct*100/max(1,count),1)}%"))
    pause()


def source_audit(records: list[dict], lang: str, state: dict, credits: dict[str, dict]) -> None:
    while True:
        no_sources=[r for r in records if not r.get('sources')]
        one=[r for r in records if len(r.get('sources') or [])==1]
        multi=[r for r in records if len(r.get('sources') or [])>=3]
        domains=Counter(source_host(url) for r in records for url in (r.get('sources') or []))
        banner(lang)
        print(color('title','SOURCE AUDIT' if lang=='en' else 'ΕΛΕΓΧΟΣ ΠΗΓΩΝ'))
        line()
        print(f"0 direct links: {len(no_sources)}")
        print(f"1 direct link: {len(one)}")
        print(f"3+ direct links: {len(multi)}")
        print(f"Unique source domains: {len(domains)}")
        print('\nTop domains:')
        for host,count in domains.most_common(10): print(f"  {count:>3}  {host}")
        line(); print('1. Browse unsourced / Χωρίς άμεσες πηγές')
        print('2. Browse single-source / Μία πηγή')
        print('3. Browse multi-source / Πολλαπλές πηγές')
        print('[Enter] Back')
        choice=input('> ').strip()
        if not choice:return
        if choice=='1': choose(sorted(no_sources,key=lambda r:-research_priority(r)),lang,state,credits,'Unsourced / Χωρίς άμεσες πηγές')
        elif choice=='2': choose(one,lang,state,credits,'Single-source / Μία πηγή')
        elif choice=='3': choose(multi,lang,state,credits,'Multi-source / Πολλαπλές πηγές')


def my_archive_menu(records: list[dict], lang: str, state: dict, credits: dict[str, dict]) -> None:
    by_id={r['id']:r for r in records}
    while True:
        banner(lang); print(color('title','MY ARCHIVE' if lang=='en' else 'ΤΟ ΑΡΧΕΙΟ ΜΟΥ')); line()
        print('1. Bookmarks / Σελιδοδείκτες')
        print('2. Recently viewed / Πρόσφατα')
        print('3. Reading progress / Πρόοδος ανάγνωσης')
        print('4. Study mode / Λειτουργία μελέτης')
        print('[Enter] Back')
        choice=input('> ').strip()
        if not choice:return
        if choice=='1': choose([by_id[i] for i in state.get('bookmarks',[]) if i in by_id],lang,state,credits,'Bookmarks / Σελιδοδείκτες')
        elif choice=='2': choose([by_id[i] for i in state.get('history',[]) if i in by_id],lang,state,credits,'Recently viewed / Πρόσφατα')
        elif choice=='3': progress_dashboard(records,lang,state,credits)
        elif choice=='4': study_mode(records,lang,state,credits)


def new_in_expansion(records: list[dict], lang: str, state: dict, credits: dict[str, dict]) -> None:
    pool = [record for record in records if str(record.get("added_in_version", "")) == "6.0"]
    pool.sort(key=lambda record: (record.get("country", ""), int(record.get("year", 0)), local(record, "title", "en")))
    choose(pool, lang, state, credits, "New in v6.0 / Νέα στην έκδοση 6.0")


def research_tools_menu(records: list[dict], lang: str, state: dict, credits: dict[str, dict]) -> None:
    while True:
        banner(lang); print(color('title','RESEARCH TOOLS' if lang=='en' else 'ΕΡΓΑΛΕΙΑ ΕΡΕΥΝΑΣ')); line()
        print('1. Research priority queue / Ουρά προτεραιότητας')
        print('2. Source audit / Έλεγχος πηγών')
        print('3. Compare two cases / Σύγκριση δύο υποθέσεων')
        print('4. Chronology explorer / Χρονολογική εξερεύνηση')
        print('5. Export searchable HTML index / Εξαγωγή ευρετηρίου HTML')
        print('6. New in this expansion / Νέα σε αυτή την επέκταση')
        print('[Enter] Back')
        choice=input('> ').strip()
        if not choice:return
        if choice=='1': research_queue(records,lang,state,credits)
        elif choice=='2': source_audit(records,lang,state,credits)
        elif choice=='3': compare_cases(records,lang)
        elif choice=='4': chronology_explorer(records,lang,state,credits)
        elif choice=='5':
            path=export_archive_index(records,lang)
            if input('Open now? / Άνοιγμα τώρα; [y/N]: ').strip().lower() in {'y','yes','ν','ναι'}: open_path(path)
        elif choice=='6': new_in_expansion(records,lang,state,credits)


def termux_support_menu(lang: str) -> None:
    while True:
        banner(lang)
        print(color("title", "TERMUX SETUP & SUPPORT" if lang == "en" else "ΡΥΘΜΙΣΗ & ΥΠΟΣΤΗΡΙΞΗ TERMUX"))
        line()
        print("1. Run Termux system check / Έλεγχος συστήματος Termux")
        print("2. Back up personal state / Αντίγραφο προσωπικών δεδομένων")
        print("3. Restore personal state / Επαναφορά προσωπικών δεδομένων")
        print("4. Open bilingual README / Άνοιγμα δίγλωσσου README")
        print("5. Show storage setup command / Εντολή άδειας αποθήκευσης")
        print("[Enter] Back / Πίσω")
        choice = input("> ").strip()
        if not choice:
            return
        if choice == "1":
            show_termux_check(lang); pause()
        elif choice == "2":
            backup_state_to_downloads(); pause()
        elif choice == "3":
            choose_state_backup(lang)
        elif choice == "4":
            open_path(APP_DIR / "README.md"); pause()
        elif choice == "5":
            print("\ntermux-setup-storage")
            print("Allow the Android permission, restart Termux, and run the check again.")
            pause()


def glossary_screen(lang: str) -> None:
    banner(lang)
    print(color('title','EVIDENCE GLOSSARY' if lang=='en' else 'ΓΛΩΣΣΑΡΙ ΤΕΚΜΗΡΙΩΣΗΣ'))
    line()
    entries_en=[
        ('Direct source','A case-specific URL attached to the record. A link is not automatically reliable; inspect authorship, date and context.'),
        ('Source-discovery lead','A search or archive starting point. It helps locate material but is not counted as direct evidence.'),
        ('Source-backed narrative','The dossier has direct case-specific links. Individual claims can still remain disputed.'),
        ('Limited-source narrative','The dossier has only a narrow direct source trail and needs independent confirmation.'),
        ('Research scaffold','The dossier is useful for navigation and questions but lacks a direct attached source.'),
        ('Case-specific rumor','A claim historically associated with the event. The assessment explains what the record supports or fails to support.'),
        ('Analytical caution','A warning against a misleading simplification. It is not presented as proof that the wording circulated historically.'),
        ('Generated archive visual','An explanatory card created for navigation; not a photograph of the historical event.'),
    ]
    entries_el=[
        ('Άμεση πηγή','Σύνδεσμος που αφορά ειδικά την υπόθεση. Ο σύνδεσμος δεν είναι αυτομάτως αξιόπιστος· έλεγξε δημιουργό, ημερομηνία και πλαίσιο.'),
        ('Αφετηρία εντοπισμού πηγών','Αναζήτηση ή αρχειακή πύλη που βοηθά στον εντοπισμό υλικού, αλλά δεν μετρά ως άμεσο τεκμήριο.'),
        ('Αφήγηση με πηγές','Ο φάκελος διαθέτει άμεσους συνδέσμους. Επιμέρους ισχυρισμοί μπορεί να παραμένουν αμφισβητούμενοι.'),
        ('Αφήγηση περιορισμένων πηγών','Η άμεση διαδρομή πηγών είναι στενή και χρειάζεται ανεξάρτητη επιβεβαίωση.'),
        ('Ερευνητικός σκελετός','Ο φάκελος είναι χρήσιμος για πλοήγηση και ερωτήματα, αλλά δεν διαθέτει συνδεδεμένη άμεση πηγή.'),
        ('Ειδική φήμη υπόθεσης','Ισχυρισμός που συνδέθηκε ιστορικά με το γεγονός. Η αξιολόγηση εξηγεί τι στηρίζει ή δεν στηρίζει το αρχείο.'),
        ('Αναλυτική προειδοποίηση','Προειδοποίηση κατά μιας παραπλανητικής απλούστευσης· δεν παρουσιάζεται ως απόδειξη ότι η διατύπωση κυκλοφόρησε ιστορικά.'),
        ('Παραγόμενο αρχειακό γραφικό','Επεξηγηματική κάρτα πλοήγησης και όχι φωτογραφία του ιστορικού γεγονότος.'),
    ]
    for term,definition in (entries_en if lang=='en' else entries_el):
        print(color('accent',term)); wrap(definition,'  '); print()
    pause()

def help_screen(lang: str) -> None:
    banner(lang)
    text_en = """This is a Termux-only offline historical and public-interest archive, not a verdict machine. “Documented” means the event or institutional record is established; it does not mean every interpretation is proven. Rumor cards separate a circulating claim from the archive's assessment. Generated dossier cards and research guides are explanatory graphics, not event photographs. Credited photographs retain their author, license and source-page details."""
    text_el = """Πρόκειται για offline ιστορικό αρχείο δημόσιου ενδιαφέροντος αποκλειστικά για Termux και όχι για μηχανή έκδοσης ετυμηγοριών. Το «τεκμηριωμένο» σημαίνει ότι το γεγονός ή το θεσμικό αρχείο είναι επιβεβαιωμένο· δεν σημαίνει ότι κάθε ερμηνεία έχει αποδειχθεί. Οι κάρτες φημών διαχωρίζουν τον ισχυρισμό από την αξιολόγηση του αρχείου. Οι παραγόμενες κάρτες φακέλων και οι οδηγοί έρευνας είναι επεξηγηματικά γραφικά και όχι φωτογραφίες γεγονότων. Οι τεκμηριωμένες φωτογραφίες διατηρούν στοιχεία δημιουργού, άδειας και πηγής."""
    wrap(text_en if lang == "en" else text_el)
    print("\nResearch portals are discovery tools, not proof by themselves; verify the specific document, date, authorship and context before treating a result as evidence.")
    print("\n" + color("accent", "ANDROID GALLERY SETUP / ΡΥΘΜΙΣΗ ANDROID GALLERY"))
    line()
    print("1. In Termux run once: termux-setup-storage")
    print("2. Allow file access when Android asks.")
    print("3. Open a case and press [G] Gallery app.")
    print(f"4. Albums are copied to Pictures/{GALLERY_FOLDER_NAME}/")
    print("5. The system app chooser lets you select Gallery, Google Photos or another viewer.")
    print("\nNo Termux:API add-on is required for the archive reader.")
    print("\nREADME.md contains the full English and Greek installation, feature, evidence and troubleshooting guide.")
    print("The reader also includes guided topic collections, reading progress, study mode, source auditing, new-expansion browsing, aftermath and legacy analysis, accountability maps, primary-record targets and HTML dossier exports.")
    pause()


def choose_language() -> str:
    print("1. English\n2. Ελληνικά")
    return "el" if input("> ").strip() == "2" else "en"


def interactive(records: list[dict], credits: dict[str, dict]) -> None:
    lang = choose_language()
    state = load_state()
    while True:
        banner(lang)
        print("1. Search / Αναζήτηση")
        print("2. Browse archive / Περιήγηση αρχείου")
        print("3. Guided collections / Θεματικές συλλογές")
        print("4. Image gallery / Συλλογή εικόνων")
        print("5. Rumors & disputed claims / Φήμες & αμφισβητούμενοι ισχυρισμοί")
        print("6. Random case / Τυχαία υπόθεση")
        print("7. My archive / Το αρχείο μου")
        print("8. Research tools / Εργαλεία έρευνας")
        print("9. Statistics / Στατιστικά")
        print("10. Termux setup, help & glossary / Ρύθμιση Termux, βοήθεια & γλωσσάρι")
        print("11. Change language / Αλλαγή γλώσσας")
        print("0. Exit / Έξοδος")
        choice = input("> ").strip()
        if choice == "1":
            query = input("Search / Αναζήτηση: ").strip()
            choose(search(records, query), lang, state, credits, f"Search: {query}")
        elif choice == "2":
            browse(records, lang, state, credits)
        elif choice == "3":
            guided_collections(records, lang, state, credits)
        elif choice == "4":
            choose([record for record in records if record.get("images")], lang, state, credits, "Image gallery / Συλλογή εικόνων")
        elif choice == "5":
            choose([record for record in records if record.get("rumors")], lang, state, credits, "Rumors & disputed claims / Φήμες & ισχυρισμοί")
        elif choice == "6":
            show_record(random.choice(records), lang, state, credits)
        elif choice == "7":
            my_archive_menu(records, lang, state, credits)
        elif choice == "8":
            research_tools_menu(records, lang, state, credits)
        elif choice == "9":
            stats(records, lang, credits)
        elif choice == "10":
            termux_support_menu(lang)
            help_screen(lang)
            glossary_screen(lang)
        elif choice == "11":
            lang = choose_language()
        elif choice == "0":
            return


def validation_report(records: list[dict], credits: dict[str, dict]) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    seen_images: set[str] = set()
    ids: set[str] = set()
    prose_index: dict[tuple[str, str], list[str]] = {}
    source_less = 0
    analytical_cards = 0
    case_rumor_cards = 0
    for record in records:
        record_id = str(record.get("id", "?"))
        if record_id in ids:
            errors.append(f"duplicate record ID: {record_id}")
        ids.add(record_id)
        required = (
            "id", "country", "year", "title", "category", "evidence", "summary",
            "full_story", "details", "timeline", "facts", "evidence_level",
            "key_questions", "investigation_plan", "verification_notes", "source_gap",
            "research_portals", "source_leads", "rumors", "editorial_note",
            "schema_version", "topic_tags", "source_strength", "reading_metrics",
            "case_brief", "editorial_review", "deep_dive",
            "aftermath_legacy", "accountability_map", "primary_record_targets", "people_institutions", "evidence_conflicts", "media_memory", "next_reading_path",
        )
        for key in required:
            if key not in record or record.get(key) in (None, "", [], {}):
                errors.append(f"{record_id}: missing or empty {key}")
        for field in ("title", "category", "evidence", "summary", "editorial_note"):
            for lang in ("en", "el"):
                value = local(record, field, lang).strip()
                if not value:
                    errors.append(f"{record_id}: missing {field}.{lang}")
                if field == "summary" and len(norm(value).split()) < 12:
                    errors.append(f"{record_id}: {field}.{lang} is too short")
        for field, minimum in (
            ("full_story", 6), ("details", 6), ("deep_dive", 4),
            ("aftermath_legacy", 4), ("accountability_map", 4), ("primary_record_targets", 4), ("people_institutions", 4), ("evidence_conflicts", 4), ("media_memory", 4), ("next_reading_path", 4),
            ("timeline", 5), ("facts", 6),
            ("key_questions", 3), ("investigation_plan", 3), ("verification_notes", 2),
        ):
            for lang in ("en", "el"):
                values = local_list(record, field, lang)
                if len(values) < minimum:
                    errors.append(f"{record_id}: {field}.{lang} has {len(values)}, needs {minimum}")
                local_seen: set[str] = set()
                for line_value in values:
                    normalized = norm(line_value)
                    if not normalized:
                        errors.append(f"{record_id}: blank line in {field}.{lang}")
                    elif normalized in local_seen:
                        errors.append(f"{record_id}: repeated line in {field}.{lang}: {line_value[:80]}")
                    local_seen.add(normalized)
                    if field in ("full_story", "details", "deep_dive", "aftermath_legacy", "accountability_map", "primary_record_targets") and len(normalized.split()) >= 18:
                        prose_index.setdefault((lang, normalized), []).append(record_id)
        if str(record.get("schema_version")) != "6.0":
            errors.append(f"{record_id}: unexpected schema version")
        if not topic_keys(record):
            errors.append(f"{record_id}: no topic collection tags")
        if reading_minutes(record, "en") < 1 or reading_minutes(record, "el") < 1:
            errors.append(f"{record_id}: invalid reading metrics")
        brief = record.get("case_brief", {})
        if not isinstance(brief, dict) or any(not brief.get(key) for key in ("focus", "record_status", "why_it_matters", "disputed_or_missing", "next_step")):
            errors.append(f"{record_id}: incomplete case brief")
        if not record.get("sources"):
            source_less += 1
            warnings.append(f"{record_id}: no direct case-specific sources; source gap remains visible")
        for rumor in record.get("rumors") or []:
            rtype = rumor.get("type", "case-specific-rumor")
            if rtype == "analytical-caution": analytical_cards += 1
            else: case_rumor_cards += 1
            for lang in ("en", "el"):
                if not local(rumor, "claim", lang).strip() or not local(rumor, "assessment", lang).strip():
                    errors.append(f"{record_id}: incomplete rumor card in {lang}")
        offline_article = str(record.get("offline_article", "")).strip()
        offline_materials = record.get("offline_materials") or []
        if not offline_article:
            errors.append(f"{record_id}: missing offline_article")
        if not isinstance(offline_materials, list) or not offline_materials:
            errors.append(f"{record_id}: missing offline_materials")
            offline_materials = []
        material_paths: set[str] = set()
        for material in offline_materials:
            if not isinstance(material, dict):
                errors.append(f"{record_id}: invalid offline material entry")
                continue
            relative_material = str(material.get("path", "")).strip()
            material_type = str(material.get("type", "")).strip().casefold()
            path = local_project_path(relative_material)
            if path is None:
                errors.append(f"{record_id}: unsafe offline material path {relative_material}")
                continue
            material_paths.add(relative_material)
            if not path.is_file():
                errors.append(f"{record_id}: missing offline material {relative_material}")
                continue
            if path.stat().st_size <= 0:
                errors.append(f"{record_id}: empty offline material {relative_material}")
            expected_hash = str(material.get("sha256", "")).strip().casefold()
            if expected_hash and sha256_file(path).casefold() != expected_hash:
                errors.append(f"{record_id}: offline material hash mismatch {relative_material}")
            suffix = path.suffix.casefold()
            if material_type == "video" and suffix not in VIDEO_EXTENSIONS:
                errors.append(f"{record_id}: unsupported offline video format {relative_material}")
            elif material_type == "article" and suffix not in ARTICLE_EXTENSIONS:
                errors.append(f"{record_id}: unsupported offline article format {relative_material}")
            elif material_type == "document" and suffix not in DOCUMENT_EXTENSIONS:
                errors.append(f"{record_id}: unsupported offline document format {relative_material}")
            elif material_type == "image" and suffix not in GALLERY_EXTENSIONS:
                errors.append(f"{record_id}: unsupported offline image format {relative_material}")
        if offline_article and offline_article not in material_paths:
            errors.append(f"{record_id}: offline_article is not indexed in offline_materials")
        article_path = local_project_path(offline_article) if offline_article else None
        if offline_article and (article_path is None or not article_path.is_file()):
            errors.append(f"{record_id}: offline article missing {offline_article}")
        for relative in record.get("images", []):
            path = APP_DIR / relative
            if not path.is_file(): errors.append(f"{record_id}: missing image {relative}")
            if Path(relative).suffix.casefold() not in GALLERY_EXTENSIONS:
                errors.append(f"{record_id}: image is not Gallery compatible: {relative}")
            if relative in seen_images: warnings.append(f"image referenced more than once: {relative}")
            seen_images.add(relative)
    repeated = [(lang, text, ids_) for (lang, text), ids_ in prose_index.items() if len(ids_) > 1]
    if repeated:
        errors.append(f"repeated long narrative/detail blocks: {len(repeated)}")
    for relative in credits:
        if not (APP_DIR / relative).is_file(): errors.append(f"credit entry points to missing file: {relative}")
    # JSON maintenance notes are intentionally data fields, not non-standard comments.
    # This keeps every JSON file valid for Python and external tooling.
    for maintenance_path in JSON_MAINTENANCE_FILES:
        if not has_json_maintenance_note(maintenance_path):
            errors.append(f"missing JSON maintenance metadata: {maintenance_path.relative_to(APP_DIR)}")

    root_names = sorted(path.name for path in APP_DIR.iterdir() if path.name != "__pycache__")
    expected = ["Greek", "Offline Survival Project.py", "README.md", "USA"]
    if root_names != expected: errors.append(f"unexpected repository root items: {root_names}")
    readme = APP_DIR / "README.md"
    if not readme.is_file():
        errors.append("missing README.md")
    else:
        readme_text = readme.read_text(encoding="utf-8", errors="replace")
        for required_heading in ("# Corrupted Files Project", "## Sections", "# Corrupted Files Project — Ελληνικά", "## Ενότητες", "Termux on Android only", "μόνο Termux σε Android", "termux-setup-storage", "--validate", "--termux-check", "--backup-state", "--restore-state"):
            if required_heading not in readme_text:
                errors.append(f"README.md missing required guide section: {required_heading}")
        for forbidden in ("Run on Windows", "Run on Linux", "macOS", "PowerShell"):
            if forbidden in readme_text:
                errors.append(f"README.md contains non-Termux platform guidance: {forbidden}")
    return {
        "records": len(records),
        "full_story_bilingual": sum(bool(local_list(r, "full_story", "en") and local_list(r, "full_story", "el")) for r in records),
        "timeline_bilingual": sum(bool(local_list(r, "timeline", "en") and local_list(r, "timeline", "el")) for r in records),
        "facts_bilingual": sum(bool(local_list(r, "facts", "en") and local_list(r, "facts", "el")) for r in records),
        "aftermath_legacy_bilingual": sum(bool(local_list(r, "aftermath_legacy", "en") and local_list(r, "aftermath_legacy", "el")) for r in records),
        "accountability_map_bilingual": sum(bool(local_list(r, "accountability_map", "en") and local_list(r, "accountability_map", "el")) for r in records),
        "primary_record_targets_bilingual": sum(bool(local_list(r, "primary_record_targets", "en") and local_list(r, "primary_record_targets", "el")) for r in records),
        "new_in_version_6": sum(str(r.get("added_in_version", "")) == "6.0" for r in records),
        "new_in_version_7": sum(str(r.get("added_in_version", "")) == "7.0" for r in records),
        "rumor_or_misconception_cards": sum(len(r.get("rumors") or []) for r in records),
        "case_specific_rumor_cards": case_rumor_cards,
        "analytical_caution_cards": analytical_cards,
        "records_without_direct_sources": source_less,
        "image_references": len(seen_images),
        "credited_photos": len(credits),
        "offline_articles": sum(1 for r in records if str(r.get("offline_article", "")).strip()),
        "offline_material_files": sum(len(r.get("offline_materials") or []) for r in records),
        "offline_documents": sum(sum(1 for item in (r.get("offline_materials") or []) if str(item.get("type", "")).casefold() == "document") for r in records),
        "offline_videos": sum(sum(1 for item in (r.get("offline_materials") or []) if str(item.get("type", "")).casefold() == "video") for r in records),
        "errors": errors,
        "warnings": warnings,
        "ok": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Termux-only bilingual Corrupted Files Project reader"
    )
    parser.add_argument("--search")
    parser.add_argument("--country", choices=["Greece", "USA"])
    parser.add_argument("--case", help="Print one case by exact ID")
    parser.add_argument("--gallery", help="Open a case image album by exact ID")
    parser.add_argument("--export-images", help="Copy a case's images to the phone Pictures folder")
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--rumors", action="store_true")
    parser.add_argument("--quality-report", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--export-index", nargs="?", const="en", choices=["en", "el"], help="Export searchable HTML archive index")
    parser.add_argument("--export-html", metavar="CASE_ID", help="Export one case as a standalone HTML dossier")
    parser.add_argument("--collections", action="store_true", help="List guided topic collections")
    parser.add_argument("--new-cases", action="store_true", help="List cases added in the latest expansion")
    parser.add_argument("--progress", action="store_true", help="Print reading and study progress")
    parser.add_argument("--termux-check", action="store_true", help="Check Termux, storage and Android integration")
    parser.add_argument("--backup-state", action="store_true", help="Back up notes, bookmarks and progress to Downloads")
    parser.add_argument("--restore-state", metavar="FILE", help="Restore notes, bookmarks and progress from a backup JSON")
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args()

    global USE_COLOR
    if args.no_color:
        USE_COLOR = False

    if not require_termux():
        return 3
    if args.termux_check:
        report = termux_environment_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["reader_ready"] else 1
    if args.backup_state:
        return 0 if backup_state_to_downloads(announce=True) else 1
    if args.restore_state:
        return 0 if restore_state_from_backup(Path(args.restore_state), announce=True) else 1

    records = load_records()
    credits = load_credits()
    global GLOBAL_RECORDS
    GLOBAL_RECORDS = list(records)
    by_id = {record["id"]: record for record in records}
    if args.country:
        records = [record for record in records if record.get("country") == args.country]
    if args.export_index:
        export_archive_index(records, args.export_index)
        return 0
    if args.export_html:
        record = by_id.get(args.export_html)
        if not record:
            print(f"Unknown case ID: {args.export_html}", file=sys.stderr)
            return 2
        path = export_record_html(record, "en", credits)
        print(path)
        return 0
    if args.new_cases:
        for record in sorted((r for r in records if str(r.get("added_in_version", "")) == "7.0"), key=lambda r: (r.get("country", ""), int(r.get("year", 0)), local(r, "title", "en"))):
            print(f"{record.get('id')} | {record.get('country')} | {record.get('year')} | {local(record, 'title', 'en')} | {local(record, 'title', 'el')}")
        return 0
    if args.collections:
        for key, labels in COLLECTION_LABELS.items():
            count = sum(key in topic_keys(record) for record in records)
            print(f"{key} | {count} | {labels[0]} | {labels[1]}")
        return 0
    if args.progress:
        state = load_state()
        read_ids = set(state.get("read_cases", []))
        print(json.dumps({
            "read_cases": sum(record.get("id") in read_ids for record in records),
            "total_cases": len(records),
            "bookmarks": len(state.get("bookmarks", [])),
            "study_sessions": int(state.get("study_sessions", 0)),
            "study_correct": int(state.get("study_correct", 0)),
            "study_total": int(state.get("study_total", 0)),
        }, ensure_ascii=False, indent=2))
        return 0
    if args.validate:
        report = validation_report(records, credits)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 1
    if args.stats:
        print(
            json.dumps(
                {
                    "records": len(records),
                    "countries": dict(Counter(record.get("country") for record in records)),
                    "rumor_cards": sum(len(record.get("rumors") or []) for record in records),
                    "image_references": sum(len(record.get("images") or []) for record in records),
                    "credited_photos": len(credits),
                    "offline_articles": sum(1 for record in records if record.get("offline_article")),
                    "offline_material_files": sum(len(record.get("offline_materials") or []) for record in records),
                    "offline_videos": sum(sum(1 for item in (record.get("offline_materials") or []) if str(item.get("type", "")).casefold() == "video") for record in records),
                    "offline_documents": sum(sum(1 for item in (record.get("offline_materials") or []) if str(item.get("type", "")).casefold() == "document") for record in records),
                    "merged_duplicate_records": sum(len(record.get("merged_from_ids") or []) for record in records),
                    "evidence_matrix_images": sum(any("Evidence-Matrix" in image for image in record.get("images") or []) for record in records),
                    "research_portal_links": sum(len(record.get("research_portals") or []) for record in records),
                    "source_discovery_leads": sum(len(record.get("source_leads") or []) for record in records),
                    "full_story_english": sum(bool(local_list(record, "full_story", "en")) for record in records),
                    "full_story_greek": sum(bool(local_list(record, "full_story", "el")) for record in records),
                    "timeline_bilingual": sum(bool(local_list(record, "timeline", "en") and local_list(record, "timeline", "el")) for record in records),
                    "facts_bilingual": sum(bool(local_list(record, "facts", "en") and local_list(record, "facts", "el")) for record in records),
                    "aftermath_legacy_bilingual": sum(bool(local_list(record, "aftermath_legacy", "en") and local_list(record, "aftermath_legacy", "el")) for record in records),
                    "accountability_map_bilingual": sum(bool(local_list(record, "accountability_map", "en") and local_list(record, "accountability_map", "el")) for record in records),
                    "primary_record_targets_bilingual": sum(bool(local_list(record, "primary_record_targets", "en") and local_list(record, "primary_record_targets", "el")) for record in records),
                    "new_in_version_6": sum(str(record.get("added_in_version", "")) == "6.0" for record in records),
                    "new_in_version_7": sum(str(record.get("added_in_version", "")) == "7.0" for record in records),
                    "research_notebook_ready": True,
                    "schema_version": "6.0",
                    "guided_collections": len(COLLECTION_LABELS),
                    "topic_tag_assignments": sum(len(topic_keys(record)) for record in records),
                    "source_strength_levels": dict(Counter(str(record.get("source_strength", {}).get("key", "unknown")) for record in records)),
                    "average_completeness": round(
                        sum(archive_completeness(record) for record in records) / max(1, len(records)),
                        1,
                    ),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if args.case:
        record = by_id.get(args.case)
        if not record:
            print(f"Unknown case ID: {args.case}", file=sys.stderr)
            return 2
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0
    if args.gallery:
        record = by_id.get(args.gallery)
        if not record:
            print(f"Unknown case ID: {args.gallery}", file=sys.stderr)
            return 2
        return 0 if open_case_gallery(record, credits) else 1
    if args.export_images:
        record = by_id.get(args.export_images)
        if not record:
            print(f"Unknown case ID: {args.export_images}", file=sys.stderr)
            return 2
        copied = export_case_images(record, credits, announce=True)
        return 0 if copied else 1
    if args.quality_report:
        for record in sorted(records, key=lambda item: (-research_priority(item), item.get("year", 0))):
            print(
                f"{research_priority(record):02d} | {archive_completeness(record):03d}% | "
                f"{record.get('id')} | {local(record, 'title', 'en')}"
            )
        return 0
    if args.search:
        for record in search(records, args.search)[:50]:
            print(
                f"{record.get('year')} | {record.get('country')} | "
                f"{archive_completeness(record)}% | {local(record, 'title', 'en')}"
            )
        return 0
    if args.rumors:
        for record in records:
            for rumor in record.get("rumors") or []:
                print(
                    f"{record.get('year')} | {local(record, 'title', 'en')} | "
                    f"{local(rumor, 'claim', 'en')} [{rumor.get('status')}]"
                )
        return 0
    interactive(records, credits)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
