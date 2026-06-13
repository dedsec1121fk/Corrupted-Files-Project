#!/usr/bin/env python3
"""Simple offline reader for the Corrupted Files Project.

Maintenance note: keep this launcher dependency-free. The user should only need
Python 3 and the Data/ + Media/ folders beside this file.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import unicodedata
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "Data" / "incidents.json"
STATE_FILE = APP_DIR / ".user_state.json"


# Text normalization makes English and Greek searches accent-insensitive.
def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(text.casefold().split())


# Data is read once at startup so searches remain fast on phones and Termux.
def load_records() -> list[dict]:
    try:
        payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not load {DATA_FILE}: {exc}")
    if not isinstance(payload, list):
        raise SystemExit("The incident database has an invalid format.")
    return payload


# Personal state stays separate from the archive and is safe to delete anytime.
def load_state() -> dict:
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return state if isinstance(state, dict) else {"bookmarks": []}
    except (OSError, json.JSONDecodeError):
        return {"bookmarks": []}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def local(record: dict, field: str, lang: str) -> str:
    value = record.get(field, {})
    if isinstance(value, dict):
        return str(value.get(lang) or value.get("en") or "")
    return str(value or "")


def local_list(record: dict, field: str, lang: str) -> list[str]:
    value = record.get(field, {})
    if isinstance(value, dict):
        selected = value.get(lang) or value.get("en") or []
        return [str(item) for item in selected]
    return []


def searchable_text(record: dict) -> str:
    values = [
        record.get("id", ""), record.get("country", ""), record.get("year", ""),
        local(record, "title", "en"), local(record, "title", "el"),
        local(record, "category", "en"), local(record, "category", "el"),
        local(record, "summary", "en"), local(record, "summary", "el"),
    ]
    values.extend(local_list(record, "details", "en"))
    values.extend(local_list(record, "details", "el"))
    values.extend(record.get("sources", []))
    return normalize(" ".join(str(item) for item in values))


def search(records: list[dict], query: str) -> list[dict]:
    words = [normalize(word) for word in query.split() if normalize(word)]
    if not words:
        return []
    ranked = []
    for record in records:
        haystack = searchable_text(record)
        if not all(word in haystack for word in words):
            continue
        title = normalize(local(record, "title", "en") + " " + local(record, "title", "el"))
        score = sum(5 if word in title else 1 for word in words)
        ranked.append((score, record))
    ranked.sort(key=lambda pair: (-pair[0], pair[1].get("year", 0), local(pair[1], "title", "en")))
    return [record for _, record in ranked]


def choose_language() -> str:
    print("\n1. English")
    print("2. Ελληνικά")
    return "el" if input("Choose language / Επιλογή γλώσσας: ").strip() == "2" else "en"


def pause() -> None:
    input("\nPress Enter / Πάτησε Enter...")


def open_file(path: Path) -> None:
    if not path.is_file():
        print("File not found.")
        return
    commands = []
    if os.environ.get("TERMUX_VERSION"):
        commands.append(["termux-open", str(path)])
    if sys.platform.startswith("linux"):
        commands.append(["xdg-open", str(path)])
    elif sys.platform == "darwin":
        commands.append(["open", str(path)])
    elif os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
        return
    for command in commands:
        try:
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except OSError:
            continue
    print(path)


def print_items(title: str, items: list[str]) -> None:
    if not items:
        return
    print(f"\n{title}")
    print("-" * len(title))
    for item in items:
        print(f"• {item}")


def show_record(record: dict, lang: str, state: dict) -> None:
    title = local(record, "title", lang)
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)
    print(f"ID: {record.get('id')}")
    print(f"Country: {record.get('country')} | Year: {record.get('year')}")
    print(f"Category: {local(record, 'category', lang)}")
    print(f"Evidence: {local(record, 'evidence', lang)}")
    summary = local(record, "summary", lang)
    if summary:
        print(f"\n{summary}")
    print_items("Details" if lang == "en" else "Λεπτομέρειες", local_list(record, "details", lang))
    print_items("Timeline" if lang == "en" else "Χρονολόγιο", local_list(record, "timeline", lang))
    print_items("Key facts" if lang == "en" else "Βασικά στοιχεία", local_list(record, "facts", lang))
    print_items("Sources" if lang == "en" else "Πηγές", [str(item) for item in record.get("sources", [])])

    images = [str(item) for item in record.get("images", [])]
    if images:
        print("\nImages / Εικόνες")
        for index, image in enumerate(images, 1):
            print(f"{index}. {Path(image).name}")
    print("\nB. Bookmark / Σελιδοδείκτης")
    print("Enter. Back / Πίσω")
    choice = input("> ").strip()
    if choice.lower() == "b":
        bookmarks = state.setdefault("bookmarks", [])
        record_id = record.get("id")
        if record_id in bookmarks:
            bookmarks.remove(record_id)
            print("Bookmark removed.")
        else:
            bookmarks.append(record_id)
            print("Bookmark added.")
        save_state(state)
    elif choice.isdigit() and 1 <= int(choice) <= len(images):
        open_file(APP_DIR / images[int(choice) - 1])
        pause()


def choose_record(records: list[dict], lang: str, state: dict) -> None:
    if not records:
        print("No results / Δεν βρέθηκαν αποτελέσματα.")
        pause()
        return
    page_size = 15
    offset = 0
    while True:
        page = records[offset:offset + page_size]
        print(f"\nResults {offset + 1}-{offset + len(page)} of {len(records)}")
        for index, record in enumerate(page, 1):
            print(f"{index}. [{record.get('year')}] {local(record, 'title', lang)}")
        print("N. Next | P. Previous | Enter. Back")
        choice = input("> ").strip().lower()
        if choice == "n" and offset + page_size < len(records):
            offset += page_size
        elif choice == "p" and offset > 0:
            offset = max(0, offset - page_size)
        elif choice.isdigit() and 1 <= int(choice) <= len(page):
            show_record(page[int(choice) - 1], lang, state)
        elif not choice:
            return


def browse(records: list[dict], lang: str, state: dict) -> None:
    countries = sorted({str(record.get("country")) for record in records})
    for index, country in enumerate(countries, 1):
        print(f"{index}. {country}")
    choice = input("> ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(countries):
        return
    country = countries[int(choice) - 1]
    years = sorted({int(record.get("year", 0)) for record in records if record.get("country") == country})
    print("\nType a year, or press Enter for all years.")
    year_text = input("> ").strip()
    selected = [record for record in records if record.get("country") == country]
    if year_text.isdigit():
        selected = [record for record in selected if int(record.get("year", 0)) == int(year_text)]
    selected.sort(key=lambda item: (item.get("year", 0), local(item, "title", lang)))
    choose_record(selected, lang, state)


def bookmarks_menu(records: list[dict], lang: str, state: dict) -> None:
    ids = set(state.get("bookmarks", []))
    selected = [record for record in records if record.get("id") in ids]
    choose_record(selected, lang, state)


def interactive(records: list[dict]) -> None:
    lang = choose_language()
    state = load_state()
    while True:
        print("\n=== CORRUPTED FILES ===")
        print("1. Search / Αναζήτηση")
        print("2. Browse / Περιήγηση")
        print("3. Random case / Τυχαία υπόθεση")
        print("4. Bookmarks / Σελιδοδείκτες")
        print("5. Statistics / Στατιστικά")
        print("6. Change language / Αλλαγή γλώσσας")
        print("0. Exit / Έξοδος")
        choice = input("> ").strip()
        if choice == "1":
            query = input("Search: ").strip()
            choose_record(search(records, query), lang, state)
        elif choice == "2":
            browse(records, lang, state)
        elif choice == "3":
            show_record(random.choice(records), lang, state)
        elif choice == "4":
            bookmarks_menu(records, lang, state)
        elif choice == "5":
            countries = {}
            for record in records:
                countries[record.get("country")] = countries.get(record.get("country"), 0) + 1
            print(f"\nRecords: {len(records)}")
            print(f"Images: {sum(len(record.get('images', [])) for record in records)}")
            for country, count in sorted(countries.items()):
                print(f"{country}: {count}")
            pause()
        elif choice == "6":
            lang = choose_language()
        elif choice == "0":
            return


def main() -> int:
    parser = argparse.ArgumentParser(description="Simple offline Corrupted Files reader")
    parser.add_argument("--search", help="search without opening the menu")
    parser.add_argument("--stats", action="store_true", help="print basic JSON statistics")
    args = parser.parse_args()
    records = load_records()
    if args.stats:
        print(json.dumps({
            "records": len(records),
            "images": sum(len(record.get("images", [])) for record in records),
            "countries": sorted({record.get("country") for record in records}),
        }, ensure_ascii=False, indent=2))
        return 0
    if args.search:
        for record in search(records, args.search)[:30]:
            print(f"{record.get('year')} | {record.get('country')} | {local(record, 'title', 'en')}")
        return 0
    interactive(records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
