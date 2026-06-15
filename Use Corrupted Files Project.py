#!/usr/bin/env python3
"""Corrupted Files Project — offline bilingual case archive and Android gallery reader.

Required repository layout:
  Greek/records.json + Greek/Images/ + Greek/image_credits.json
  USA/records.json   + USA/Images/   + USA/image_credits.json
  Use Corrupted Files Project.py

The program uses only Python's standard library. Personal bookmarks, history and
exports are stored outside the repository so archive files remain clean.
"""
from __future__ import annotations

import argparse
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
import webbrowser
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

APP_DIR = Path(__file__).resolve().parent
DATA_FILES = [APP_DIR / "Greek" / "records.json", APP_DIR / "USA" / "records.json"]
CREDIT_FILES = [APP_DIR / "Greek" / "image_credits.json", APP_DIR / "USA" / "image_credits.json"]
STATE_FILE = Path.home() / ".corrupted_files_project_state.json"
EXPORT_DIR = (
    Path.home() / "storage" / "downloads" / "Corrupted Files Exports"
    if os.environ.get("TERMUX_VERSION")
    else Path.home() / "Downloads" / "Corrupted Files Exports"
)
GALLERY_FOLDER_NAME = "Corrupted Files Project"
GALLERY_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
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


def local_list(record: dict, field: str, lang: str) -> list[str]:
    value = record.get(field, {})
    if not isinstance(value, dict):
        return []
    return [str(item) for item in (value.get(lang) or value.get("en") or [])]


def clear() -> None:
    os.system("clear" if os.name != "nt" else "cls")


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


def banner(lang: str) -> None:
    clear()
    line("═")
    title = color("title", "CORRUPTED FILES PROJECT")
    padding = len(C["title"]) + len(C["reset"]) if USE_COLOR else 0
    print(title.center(WIDTH + padding))
    subtitle = (
        "Offline evidence archive • Greece & USA • Android gallery ready"
        if lang == "en"
        else "Offline αρχείο τεκμηρίων • Ελλάδα & ΗΠΑ • Έτοιμο για Android Gallery"
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
    for field in ("full_story", "details", "timeline", "facts", "key_questions", "investigation_plan", "verification_notes"):
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
    score += 6 if len(record.get("images") or []) >= 4 else 0
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
    if os.environ.get("TERMUX_VERSION") and shutil.which("termux-open-url"):
        try:
            subprocess.Popen(
                ["termux-open-url", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        except OSError:
            pass
    webbrowser.open(url)


def open_path(path: Path) -> bool:
    path = Path(path)
    if not path.exists():
        print(color("bad", "File not found / Το αρχείο δεν βρέθηκε."))
        return False
    commands: list[list[str]] = []
    if os.environ.get("TERMUX_VERSION"):
        commands.extend([["termux-open", "--view", str(path)], ["termux-open", str(path)]])
    if sys.platform.startswith("linux"):
        commands.append(["xdg-open", str(path)])
    elif sys.platform == "darwin":
        commands.append(["open", str(path)])
    elif os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
        return True
    for command in commands:
        if not shutil.which(command[0]):
            continue
        try:
            subprocess.Popen(
                command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return True
        except OSError:
            continue
    print(path)
    return False


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
    if not os.environ.get("TERMUX_VERSION"):
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
    if os.environ.get("TERMUX_VERSION") and shutil.which("termux-open"):
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
    if os.environ.get("TERMUX_VERSION"):
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
        wrap(("Status: " if lang == "en" else "Κατάσταση: ") + str(rumor.get("status", "unknown")), "   ")
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
                f"- {local(rumor, 'claim', lang)} [{rumor.get('status', '')}]",
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
    print(color("good", f"Exported: {path}"))


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
        print(
            f"Archive completeness: {archive_completeness(record)}% • "
            f"Images: {len(record.get('images') or [])} • Credited photos: {photo_count}"
        )
        print("Bookmark: " + (color("good", "YES") if bookmarked else "No"))
        print("\n" + textwrap.fill(local(record, "summary", lang), WIDTH))
        items("Details" if lang == "en" else "Λεπτομέρειες", local_list(record, "details", lang))
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
        print("[B] Bookmark  [G] Gallery app  [S] Source  [E] Export case")
        print("[R] Related cases  [N] Research notes  [O] Open gallery album")
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
        elif choice == "g" and images:
            image_menu(record, lang, credits)
        elif choice == "c" and images:
            show_image_credits(record, lang, credits)
        elif choice == "s" and record.get("sources"):
            pick = input("Source number: ").strip()
            if pick.isdigit() and 1 <= int(pick) <= len(record["sources"]):
                open_url(record["sources"][int(pick) - 1])
            pause()
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


def help_screen(lang: str) -> None:
    banner(lang)
    text_en = """This is an offline historical and public-interest archive, not a verdict machine. “Documented” means the event or institutional record is established; it does not mean every interpretation is proven. Rumor cards separate a circulating claim from the archive's assessment. Generated dossier cards and research guides are explanatory graphics, not event photographs. Credited photographs retain their author, license and source-page details."""
    text_el = """Πρόκειται για offline ιστορικό αρχείο δημόσιου ενδιαφέροντος και όχι για μηχανή έκδοσης ετυμηγοριών. Το «τεκμηριωμένο» σημαίνει ότι το γεγονός ή το θεσμικό αρχείο είναι επιβεβαιωμένο· δεν σημαίνει ότι κάθε ερμηνεία έχει αποδειχθεί. Οι κάρτες φημών διαχωρίζουν τον ισχυρισμό από την αξιολόγηση του αρχείου. Οι παραγόμενες κάρτες φακέλων και οι οδηγοί έρευνας είναι επεξηγηματικά γραφικά και όχι φωτογραφίες γεγονότων. Οι τεκμηριωμένες φωτογραφίες διατηρούν στοιχεία δημιουργού, άδειας και πηγής."""
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
    pause()


def choose_language() -> str:
    print("1. English\n2. Ελληνικά")
    return "el" if input("> ").strip() == "2" else "en"


def interactive(records: list[dict], credits: dict[str, dict]) -> None:
    lang = choose_language()
    state = load_state()
    by_id = {record["id"]: record for record in records}
    while True:
        banner(lang)
        print("1. Search / Αναζήτηση")
        print("2. Browse archive / Περιήγηση αρχείου")
        print("3. Image gallery / Συλλογή εικόνων")
        print("4. Rumors & disputed claims / Φήμες & αμφισβητούμενοι ισχυρισμοί")
        print("5. Random case / Τυχαία υπόθεση")
        print("6. Bookmarks / Σελιδοδείκτες")
        print("7. Recently viewed / Πρόσφατα")
        print("8. Research priority queue / Ουρά ερευνητικής προτεραιότητας")
        print("9. Compare two cases / Σύγκριση δύο υποθέσεων")
        print("10. Chronology explorer / Χρονολογική εξερεύνηση")
        print("11. Statistics / Στατιστικά")
        print("12. Help, methodology & Gallery setup / Βοήθεια και ρύθμιση Gallery")
        print("13. Change language / Αλλαγή γλώσσας")
        print("0. Exit / Έξοδος")
        choice = input("> ").strip()
        if choice == "1":
            query = input("Search / Αναζήτηση: ").strip()
            choose(search(records, query), lang, state, credits, f"Search: {query}")
        elif choice == "2":
            browse(records, lang, state, credits)
        elif choice == "3":
            choose(
                [record for record in records if record.get("images")],
                lang,
                state,
                credits,
                "Image gallery / Συλλογή εικόνων",
            )
        elif choice == "4":
            choose(
                [record for record in records if record.get("rumors")],
                lang,
                state,
                credits,
                "Rumors & disputed claims",
            )
        elif choice == "5":
            show_record(random.choice(records), lang, state, credits)
        elif choice == "6":
            choose(
                [by_id[item] for item in state.get("bookmarks", []) if item in by_id],
                lang,
                state,
                credits,
                "Bookmarks",
            )
        elif choice == "7":
            choose(
                [by_id[item] for item in state.get("history", []) if item in by_id],
                lang,
                state,
                credits,
                "Recently viewed",
            )
        elif choice == "8":
            research_queue(records, lang, state, credits)
        elif choice == "9":
            compare_cases(records, lang)
        elif choice == "10":
            chronology_explorer(records, lang, state, credits)
        elif choice == "11":
            stats(records, lang, credits)
        elif choice == "12":
            help_screen(lang)
        elif choice == "13":
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
            ("full_story", 6), ("details", 6), ("timeline", 5), ("facts", 6),
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
                    if field in ("full_story", "details") and len(normalized.split()) >= 18:
                        prose_index.setdefault((lang, normalized), []).append(record_id)
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
    root_names = sorted(path.name for path in APP_DIR.iterdir() if path.name != "__pycache__")
    expected = ["Greek", "USA", "Use Corrupted Files Project.py"]
    if root_names != expected: errors.append(f"unexpected repository root items: {root_names}")
    return {
        "records": len(records),
        "full_story_bilingual": sum(bool(local_list(r, "full_story", "en") and local_list(r, "full_story", "el")) for r in records),
        "timeline_bilingual": sum(bool(local_list(r, "timeline", "en") and local_list(r, "timeline", "el")) for r in records),
        "facts_bilingual": sum(bool(local_list(r, "facts", "en") and local_list(r, "facts", "el")) for r in records),
        "rumor_or_misconception_cards": sum(len(r.get("rumors") or []) for r in records),
        "case_specific_rumor_cards": case_rumor_cards,
        "analytical_caution_cards": analytical_cards,
        "records_without_direct_sources": source_less,
        "image_references": len(seen_images),
        "credited_photos": len(credits),
        "errors": errors,
        "warnings": warnings,
        "ok": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Offline bilingual Corrupted Files Project reader"
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
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args()

    global USE_COLOR
    if args.no_color:
        USE_COLOR = False

    records = load_records()
    credits = load_credits()
    global GLOBAL_RECORDS
    GLOBAL_RECORDS = list(records)
    by_id = {record["id"]: record for record in records}
    if args.country:
        records = [record for record in records if record.get("country") == args.country]
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
                    "merged_duplicate_records": sum(len(record.get("merged_from_ids") or []) for record in records),
                    "evidence_matrix_images": sum(any("Evidence-Matrix" in image for image in record.get("images") or []) for record in records),
                    "research_portal_links": sum(len(record.get("research_portals") or []) for record in records),
                    "source_discovery_leads": sum(len(record.get("source_leads") or []) for record in records),
                    "full_story_english": sum(bool(local_list(record, "full_story", "en")) for record in records),
                    "full_story_greek": sum(bool(local_list(record, "full_story", "el")) for record in records),
                    "timeline_bilingual": sum(bool(local_list(record, "timeline", "en") and local_list(record, "timeline", "el")) for record in records),
                    "facts_bilingual": sum(bool(local_list(record, "facts", "en") and local_list(record, "facts", "el")) for record in records),
                    "research_notebook_ready": True,
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
