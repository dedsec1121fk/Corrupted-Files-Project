#!/usr/bin/env python3
"""Dependency-free offline reader for the Corrupted Files Project.

Interactive mode is designed for Termux and ordinary terminals. Command-line mode is
useful for scripting, quick searches, exports, and integrity checks.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import shutil
import subprocess
import sys
import textwrap
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from corrupted_files_core import (
    PROJECT_NAME,
    audit_project,
    calculate_entry_quality,
    detect_country,
    load_database,
    localize,
    normalize_text,
    parse_date_folder,
    safe_filename,
)

APP_DIR = Path(__file__).resolve().parent
EXPORT_DIR = APP_DIR / "Corrupted Files Exports"
STATE_FILE = APP_DIR / ".corrupted_files_state.json"
PAGE_SIZE = 15

UI: dict[str, dict[str, str]] = {
    "en": {
        "reader": "Corrupted Files Offline Research Reader",
        "loading": "Loading database...",
        "loaded": "Loaded {records} incidents from {shards} database shards.",
        "load_errors": "The database loaded with {count} warning(s).",
        "main_menu": (
            "\n[1] Smart search\n[2] Advanced filters\n[3] Browse timeline\n"
            "[4] Browse categories and evidence\n[5] Browse date folders\n[6] Random incident\n"
            "[7] Bookmarks and history\n[8] Compare two incidents\n[9] Export archive data\n"
            "[10] Statistics\n[11] Integrity report\n[12] Reload database\n[0] Exit\nChoice: "
        ),
        "search_prompt": "Search words or operators: ",
        "search_help": (
            "Operators: country:greece, country:usa, year:2023, category:corruption, "
            "evidence:documented, source:linked, id:partial_id"
        ),
        "no_results": "No matching incidents were found.",
        "results": "Results: {count}",
        "result_line": "[{number}] {date} | {country} | {title}",
        "page_prompt": "Number=open, n=next, p=previous, e=export page, Enter=back: ",
        "invalid": "Invalid choice.",
        "continue": "Press Enter to continue...",
        "country_filter": "Country [all/Greece/USA]: ",
        "year_filter": "Year or range (example: 2000-2020, all): ",
        "category_filter": "Category contains (all): ",
        "evidence_filter": "Evidence label contains (all): ",
        "source_filter": "Source trail [all/linked/generic/descriptive]: ",
        "translation_filter": "Greek coverage [all/good/review]: ",
        "sort_filter": "Sort [1=year ascending, 2=year descending, 3=title]: ",
        "choose_group": "Choose a number or press Enter to go back: ",
        "bookmarked": "Bookmark saved.",
        "unbookmarked": "Bookmark removed.",
        "history_empty": "Reading history is empty.",
        "bookmarks_empty": "No bookmarks yet.",
        "bookmark_menu": "\n[1] Bookmarks\n[2] Reading history\n[3] Clear history\n[0] Back\nChoice: ",
        "history_cleared": "Reading history cleared.",
        "case_actions": (
            "\n[b] Bookmark/unbookmark  [m] Media  [x] Export  [f] Open folder  "
            "[s] Show record metadata  [Enter] Back: "
        ),
        "media_none": "No media files are listed for this incident.",
        "media_prompt": "Media number to open, or Enter to return: ",
        "open_failed": "Could not open automatically. The path is shown below.",
        "missing_file": "Missing file: {path}",
        "export_format": "Format [1=TXT, 2=Markdown, 3=JSON]: ",
        "exported": "Exported to: {path}",
        "export_menu": (
            "\n[1] Export all incidents as JSON\n[2] Export compact CSV index\n"
            "[3] Export all readable TXT files\n[4] Export bookmarks\n[0] Back\nChoice: "
        ),
        "compare_first": "Search/select the first incident.",
        "compare_second": "Search/select the second incident.",
        "select_search": "Search text: ",
        "cancelled": "Cancelled.",
        "integrity_pass": "Structural integrity: PASS",
        "integrity_fail": "Structural integrity: FAIL",
        "reloaded": "Database reloaded.",
        "language": "Language",
        "article": "ARTICLE",
        "proof": "PROOF DOSSIER",
        "sources": "SOURCE TRAIL",
        "report": "READING REPORT",
        "quality": "QUALITY SIGNALS",
        "metadata": "RECORD METADATA",
        "category": "Category",
        "evidence": "Evidence label",
        "source_status": "Source trail",
        "translation_status": "Greek coverage",
        "media_status": "Media paths",
        "timeline_title": "Timeline by year",
        "categories_title": "Categories",
        "evidence_title": "Evidence labels",
        "date_title": "Date folders",
    },
    "el": {
        "reader": "Corrupted Files Offline Ερευνητικός Αναγνώστης",
        "loading": "Φόρτωση βάσης δεδομένων...",
        "loaded": "Φορτώθηκαν {records} υποθέσεις από {shards} database shards.",
        "load_errors": "Η βάση φορτώθηκε με {count} προειδοποίηση/προειδοποιήσεις.",
        "main_menu": (
            "\n[1] Έξυπνη αναζήτηση\n[2] Σύνθετα φίλτρα\n[3] Περιήγηση σε χρονολόγιο\n"
            "[4] Περιήγηση σε κατηγορίες και τεκμηρίωση\n[5] Περιήγηση σε φακέλους ημερομηνιών\n"
            "[6] Τυχαία υπόθεση\n[7] Σελιδοδείκτες και ιστορικό\n[8] Σύγκριση δύο υποθέσεων\n"
            "[9] Εξαγωγή δεδομένων αρχείου\n[10] Στατιστικά\n[11] Αναφορά ακεραιότητας\n"
            "[12] Επαναφόρτωση βάσης\n[0] Έξοδος\nΕπιλογή: "
        ),
        "search_prompt": "Λέξεις αναζήτησης ή operators: ",
        "search_help": (
            "Operators: country:greece, country:usa, year:2023, category:corruption, "
            "evidence:documented, source:linked, id:μέρος_id"
        ),
        "no_results": "Δεν βρέθηκαν υποθέσεις που να ταιριάζουν.",
        "results": "Αποτελέσματα: {count}",
        "result_line": "[{number}] {date} | {country} | {title}",
        "page_prompt": "Αριθμός=άνοιγμα, n=επόμενα, p=προηγούμενα, e=εξαγωγή σελίδας, Enter=πίσω: ",
        "invalid": "Μη έγκυρη επιλογή.",
        "continue": "Πάτησε Enter για συνέχεια...",
        "country_filter": "Χώρα [all/Greece/USA]: ",
        "year_filter": "Έτος ή εύρος (παράδειγμα: 2000-2020, all): ",
        "category_filter": "Η κατηγορία περιέχει (all): ",
        "evidence_filter": "Η τεκμηρίωση περιέχει (all): ",
        "source_filter": "Πηγές [all/linked/generic/descriptive]: ",
        "translation_filter": "Ελληνική κάλυψη [all/good/review]: ",
        "sort_filter": "Ταξινόμηση [1=έτος αύξον, 2=έτος φθίνον, 3=τίτλος]: ",
        "choose_group": "Διάλεξε αριθμό ή πάτησε Enter για πίσω: ",
        "bookmarked": "Ο σελιδοδείκτης αποθηκεύτηκε.",
        "unbookmarked": "Ο σελιδοδείκτης αφαιρέθηκε.",
        "history_empty": "Το ιστορικό ανάγνωσης είναι κενό.",
        "bookmarks_empty": "Δεν υπάρχουν ακόμη σελιδοδείκτες.",
        "bookmark_menu": "\n[1] Σελιδοδείκτες\n[2] Ιστορικό ανάγνωσης\n[3] Καθαρισμός ιστορικού\n[0] Πίσω\nΕπιλογή: ",
        "history_cleared": "Το ιστορικό ανάγνωσης καθαρίστηκε.",
        "case_actions": (
            "\n[b] Σελιδοδείκτης  [m] Media  [x] Εξαγωγή  [f] Άνοιγμα φακέλου  "
            "[s] Metadata εγγραφής  [Enter] Πίσω: "
        ),
        "media_none": "Δεν υπάρχουν καταχωρημένα media για αυτή την υπόθεση.",
        "media_prompt": "Αριθμός media για άνοιγμα ή Enter για επιστροφή: ",
        "open_failed": "Δεν μπόρεσε να ανοίξει αυτόματα. Η διαδρομή εμφανίζεται παρακάτω.",
        "missing_file": "Λείπει το αρχείο: {path}",
        "export_format": "Μορφή [1=TXT, 2=Markdown, 3=JSON]: ",
        "exported": "Έγινε εξαγωγή στο: {path}",
        "export_menu": (
            "\n[1] Εξαγωγή όλων των υποθέσεων σε JSON\n[2] Εξαγωγή compact CSV index\n"
            "[3] Εξαγωγή όλων σε αναγνώσιμα TXT\n[4] Εξαγωγή σελιδοδεικτών\n[0] Πίσω\nΕπιλογή: "
        ),
        "compare_first": "Αναζήτησε/διάλεξε την πρώτη υπόθεση.",
        "compare_second": "Αναζήτησε/διάλεξε τη δεύτερη υπόθεση.",
        "select_search": "Κείμενο αναζήτησης: ",
        "cancelled": "Ακυρώθηκε.",
        "integrity_pass": "Δομική ακεραιότητα: PASS",
        "integrity_fail": "Δομική ακεραιότητα: FAIL",
        "reloaded": "Η βάση επαναφορτώθηκε.",
        "language": "Γλώσσα",
        "article": "ΑΡΘΡΟ",
        "proof": "ΦΑΚΕΛΟΣ ΤΕΚΜΗΡΙΩΣΗΣ",
        "sources": "ΔΙΑΔΡΟΜΗ ΠΗΓΩΝ",
        "report": "ΑΝΑΦΟΡΑ ΑΝΑΓΝΩΣΗΣ",
        "quality": "ΣΗΜΑΤΑ ΠΟΙΟΤΗΤΑΣ",
        "metadata": "METADATA ΕΓΓΡΑΦΗΣ",
        "category": "Κατηγορία",
        "evidence": "Επίπεδο τεκμηρίωσης",
        "source_status": "Κατάσταση πηγών",
        "translation_status": "Ελληνική κάλυψη",
        "media_status": "Διαδρομές media",
        "timeline_title": "Χρονολόγιο ανά έτος",
        "categories_title": "Κατηγορίες",
        "evidence_title": "Επίπεδα τεκμηρίωσης",
        "date_title": "Φάκελοι ημερομηνιών",
    },
}


def terminal_width() -> int:
    return max(72, min(120, shutil.get_terminal_size((92, 24)).columns))


def clear_screen() -> None:
    if not sys.stdout.isatty():
        return
    command = "cls" if os.name == "nt" else "clear"
    if os.name == "nt" or os.environ.get("TERM"):
        os.system(command)


def wrap_text(value: Any, width: int | None = None) -> str:
    width = width or terminal_width()
    output: list[str] = []
    for paragraph in str(value or "").splitlines():
        if not paragraph.strip():
            output.append("")
            continue
        output.extend(
            textwrap.wrap(
                paragraph,
                width=width,
                replace_whitespace=False,
                drop_whitespace=True,
                break_long_words=False,
                break_on_hyphens=False,
            )
            or [""]
        )
    return "\n".join(output)


def divider(char: str = "=") -> str:
    return char * terminal_width()


def year_as_int(entry: Mapping[str, Any]) -> int:
    try:
        return int(entry.get("year") or 0)
    except (TypeError, ValueError):
        return 0


def parse_year_filter(value: str) -> tuple[int | None, int | None]:
    value = value.strip().casefold()
    if not value or value == "all":
        return None, None
    match = re.fullmatch(r"(\d{3,4})\s*[-:]\s*(\d{3,4})", value)
    if match:
        start, end = map(int, match.groups())
        return (min(start, end), max(start, end))
    if value.isdigit():
        year = int(value)
        return year, year
    return None, None


def open_path(path: Path) -> bool:
    if not path.exists():
        return False
    commands: list[list[str]] = []
    if shutil.which("termux-open"):
        commands.append(["termux-open", str(path)])
    if shutil.which("xdg-open"):
        commands.append(["xdg-open", str(path)])
    if sys.platform == "darwin" and shutil.which("open"):
        commands.append(["open", str(path)])
    if os.name == "nt":
        try:
            os.startfile(str(path))  # type: ignore[attr-defined]
            return True
        except OSError:
            pass
    for command in commands:
        try:
            completed = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=8,
                check=False,
            )
            if completed.returncode == 0:
                return True
        except (OSError, subprocess.SubprocessError):
            continue
    return False


def parse_query(query: str) -> tuple[list[str], dict[str, str]]:
    filters: dict[str, str] = {}
    terms: list[str] = []
    for raw in re.findall(r'[^\s"]+|"[^"]*"', query):
        token = raw.strip('"').strip()
        if not token:
            continue
        if ":" in token:
            key, value = token.split(":", 1)
            key = key.casefold()
            if key in {"country", "year", "category", "evidence", "source", "id"} and value:
                filters[key] = value
                continue
        terms.append(token)
    return terms, filters


def search_score(entry: Mapping[str, Any], terms: Sequence[str]) -> int | None:
    if not terms:
        return 1
    normalized_terms = [normalize_text(term) for term in terms if normalize_text(term)]
    if not normalized_terms:
        return 1

    fields = {
        "id": normalize_text(entry.get("id", "")),
        "title_en": normalize_text(localize(entry, "title", "en")),
        "title_el": normalize_text(localize(entry, "title", "el")),
        "category_en": normalize_text(localize(entry, "category", "en")),
        "category_el": normalize_text(localize(entry, "category", "el")),
        "evidence_en": normalize_text(localize(entry, "evidence_level", "en")),
        "evidence_el": normalize_text(localize(entry, "evidence_level", "el")),
        "article_en": normalize_text(localize(entry, "article", "en")),
        "article_el": normalize_text(localize(entry, "article", "el")),
        "sources_en": normalize_text(localize(entry, "source_trail", "en")),
        "sources_el": normalize_text(localize(entry, "source_trail", "el")),
        "country": normalize_text(detect_country(entry)),
        "year": normalize_text(entry.get("year", "")),
        "date": normalize_text(parse_date_folder(entry)),
    }
    all_text = " ".join(fields.values())
    if any(term not in all_text for term in normalized_terms):
        return None

    score = 0
    phrase = normalize_text(" ".join(terms))
    if phrase and phrase in fields["title_en"]:
        score += 120
    if phrase and phrase in fields["title_el"]:
        score += 120
    for term in normalized_terms:
        if fields["id"] == term:
            score += 150
        elif term in fields["id"]:
            score += 45
        if term in fields["title_en"]:
            score += 55
        if term in fields["title_el"]:
            score += 55
        if term in fields["category_en"] or term in fields["category_el"]:
            score += 25
        if term in fields["evidence_en"] or term in fields["evidence_el"]:
            score += 18
        if term in fields["country"] or term in fields["year"] or term in fields["date"]:
            score += 20
        if term in fields["sources_en"] or term in fields["sources_el"]:
            score += 10
        if term in fields["article_en"] or term in fields["article_el"]:
            score += 5
    return score


def filter_entries(
    entries: Sequence[dict[str, Any]],
    *,
    country: str = "all",
    year_text: str = "all",
    category: str = "all",
    evidence: str = "all",
    source: str = "all",
    translation: str = "all",
) -> list[dict[str, Any]]:
    country_n = normalize_text(country)
    category_n = normalize_text(category)
    evidence_n = normalize_text(evidence)
    source_n = normalize_text(source)
    translation_n = normalize_text(translation)
    start_year, end_year = parse_year_filter(year_text)
    results: list[dict[str, Any]] = []

    for entry in entries:
        if country_n not in {"", "all"}:
            entry_country = normalize_text(detect_country(entry))
            aliases = {"ελλαδα": "greece", "ηπα": "usa", "united states": "usa"}
            expected = aliases.get(country_n, country_n)
            if expected not in entry_country:
                continue
        year = year_as_int(entry)
        if start_year is not None and not (start_year <= year <= (end_year or start_year)):
            continue
        if category_n not in {"", "all"}:
            category_blob = normalize_text(
                localize(entry, "category", "en") + " " + localize(entry, "category", "el")
            )
            if category_n not in category_blob:
                continue
        if evidence_n not in {"", "all"}:
            evidence_blob = normalize_text(
                localize(entry, "evidence_level", "en") + " " + localize(entry, "evidence_level", "el")
            )
            if evidence_n not in evidence_blob:
                continue
        quality = entry.get("quality") if isinstance(entry.get("quality"), Mapping) else calculate_entry_quality(entry)
        source_level = normalize_text((quality.get("source_trail") or {}).get("level", ""))
        translation_level = normalize_text((quality.get("translation") or {}).get("overall", ""))
        if source_n not in {"", "all"}:
            source_alias = {"linked": "specific links", "generic": "generic guidance", "descriptive": "descriptive no links"}
            if source_alias.get(source_n, source_n) not in source_level:
                continue
        if translation_n not in {"", "all"}:
            if translation_n == "good" and translation_level != "good":
                continue
            if translation_n in {"review", "needs review"} and translation_level == "good":
                continue
        results.append(entry)
    return results


class Reader:
    def __init__(self, lang: str = "en") -> None:
        self.lang = "el" if lang == "el" else "en"
        self.entries: list[dict[str, Any]] = []
        self.by_id: dict[str, dict[str, Any]] = {}
        self.shard_count = 0
        self.load_errors: list[str] = []
        self.state = self._load_state()
        self.reload()

    @property
    def t(self) -> dict[str, str]:
        return UI[self.lang]

    def _load_state(self) -> dict[str, list[str]]:
        default = {"bookmarks": [], "history": []}
        try:
            payload = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                return default
            return {
                "bookmarks": [str(item) for item in payload.get("bookmarks", [])],
                "history": [str(item) for item in payload.get("history", [])],
            }
        except (OSError, json.JSONDecodeError):
            return default

    def _save_state(self) -> None:
        temp = STATE_FILE.with_name(STATE_FILE.name + ".tmp")
        temp.write_text(json.dumps(self.state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temp.replace(STATE_FILE)

    def reload(self) -> None:
        result = load_database(APP_DIR)
        self.entries = result.entries
        self.by_id = {str(entry.get("id")): entry for entry in self.entries}
        self.shard_count = len(result.shard_paths)
        self.load_errors = result.errors
        self.state["bookmarks"] = [item for item in self.state["bookmarks"] if item in self.by_id]
        self.state["history"] = [item for item in self.state["history"] if item in self.by_id][:100]
        self._save_state()

    def header(self, title: str | None = None) -> None:
        clear_screen()
        print(divider())
        print(title or self.t["reader"])
        print(divider())

    def pause(self) -> None:
        input("\n" + self.t["continue"])

    def run(self) -> None:
        self.header()
        print(self.t["loaded"].format(records=len(self.entries), shards=self.shard_count))
        if self.load_errors:
            print(self.t["load_errors"].format(count=len(self.load_errors)))
        if not self.entries:
            self.pause()
            return
        while True:
            choice = input(self.t["main_menu"]).strip()
            if choice == "1":
                self.smart_search()
            elif choice == "2":
                self.advanced_filters()
            elif choice == "3":
                self.browse_timeline()
            elif choice == "4":
                self.browse_categories()
            elif choice == "5":
                self.browse_dates()
            elif choice == "6":
                self.show_case(random.choice(self.entries))
            elif choice == "7":
                self.bookmarks_history()
            elif choice == "8":
                self.compare_cases()
            elif choice == "9":
                self.export_menu()
            elif choice == "10":
                self.show_stats()
            elif choice == "11":
                self.show_integrity()
            elif choice == "12":
                self.reload()
                print(self.t["reloaded"])
            elif choice == "0":
                break
            else:
                print(self.t["invalid"])

    def smart_search(self) -> None:
        self.header(self.t["reader"] + " - Search")
        print(self.t["search_help"])
        query = input("\n" + self.t["search_prompt"]).strip()
        if not query:
            return
        terms, query_filters = parse_query(query)
        results: list[tuple[int, dict[str, Any]]] = []
        for entry in self.entries:
            filtered = filter_entries(
                [entry],
                country=query_filters.get("country", "all"),
                year_text=query_filters.get("year", "all"),
                category=query_filters.get("category", "all"),
                evidence=query_filters.get("evidence", "all"),
                source=query_filters.get("source", "all"),
            )
            if not filtered:
                continue
            id_filter = normalize_text(query_filters.get("id", ""))
            if id_filter and id_filter not in normalize_text(entry.get("id", "")):
                continue
            score = search_score(entry, terms)
            if score is not None:
                results.append((score, entry))
        results.sort(key=lambda item: (-item[0], year_as_int(item[1]), localize(item[1], "title", self.lang).casefold()))
        self.paginate([entry for _, entry in results], export_name="search-results")

    def advanced_filters(self) -> None:
        self.header(self.t["reader"] + " - Filters")
        country = input(self.t["country_filter"]).strip() or "all"
        year_text = input(self.t["year_filter"]).strip() or "all"
        category = input(self.t["category_filter"]).strip() or "all"
        evidence = input(self.t["evidence_filter"]).strip() or "all"
        source = input(self.t["source_filter"]).strip() or "all"
        translation = input(self.t["translation_filter"]).strip() or "all"
        sort_choice = input(self.t["sort_filter"]).strip()
        results = filter_entries(
            self.entries,
            country=country,
            year_text=year_text,
            category=category,
            evidence=evidence,
            source=source,
            translation=translation,
        )
        if sort_choice == "2":
            results.sort(key=lambda entry: (-year_as_int(entry), localize(entry, "title", self.lang).casefold()))
        elif sort_choice == "3":
            results.sort(key=lambda entry: localize(entry, "title", self.lang).casefold())
        else:
            results.sort(key=lambda entry: (year_as_int(entry), localize(entry, "title", self.lang).casefold()))
        self.paginate(results, export_name="filtered-results")

    def paginate(self, results: Sequence[dict[str, Any]], *, export_name: str = "results") -> dict[str, Any] | None:
        if not results:
            print("\n" + self.t["no_results"])
            self.pause()
            return None
        page = 0
        while True:
            self.header(self.t["results"].format(count=len(results)))
            start = page * PAGE_SIZE
            end = min(start + PAGE_SIZE, len(results))
            for index, entry in enumerate(results[start:end], start + 1):
                print(
                    self.t["result_line"].format(
                        number=index,
                        date=parse_date_folder(entry),
                        country=detect_country(entry),
                        title=localize(entry, "title", self.lang)[: max(30, terminal_width() - 35)],
                    )
                )
            print(f"\nPage {page + 1}/{max(1, (len(results) + PAGE_SIZE - 1) // PAGE_SIZE)}")
            choice = input(self.t["page_prompt"]).strip().casefold()
            if not choice:
                return None
            if choice == "n" and end < len(results):
                page += 1
            elif choice == "p" and page > 0:
                page -= 1
            elif choice == "e":
                path = self.export_result_set(results[start:end], export_name)
                print(self.t["exported"].format(path=path))
                self.pause()
            elif choice.isdigit() and 1 <= int(choice) <= len(results):
                entry = results[int(choice) - 1]
                self.show_case(entry)
            else:
                print(self.t["invalid"])

    def show_case(self, entry: dict[str, Any]) -> None:
        incident_id = str(entry.get("id"))
        history = [item for item in self.state["history"] if item != incident_id]
        self.state["history"] = [incident_id] + history[:99]
        self._save_state()
        while True:
            self.header(localize(entry, "title", self.lang))
            print(
                f"{detect_country(entry)} | {parse_date_folder(entry)} | ID: {incident_id}\n"
                f"{self.t['category']}: {localize(entry, 'category', self.lang)}\n"
                f"{self.t['evidence']}: {localize(entry, 'evidence_level', self.lang)}"
            )
            sections = (
                (self.t["article"], localize(entry, "article", self.lang)),
                (self.t["proof"], localize(entry, "proof_dossier", self.lang)),
                (self.t["sources"], localize(entry, "source_trail", self.lang)),
                (self.t["report"], localize(entry, "reading_report", self.lang)),
            )
            for heading, content in sections:
                if content.strip():
                    print("\n" + divider("-"))
                    print(heading)
                    print(divider("-"))
                    print(wrap_text(content))

            quality = entry.get("quality") if isinstance(entry.get("quality"), Mapping) else calculate_entry_quality(entry)
            print("\n" + divider("-"))
            print(self.t["quality"])
            print(divider("-"))
            print(f"{self.t['source_status']}: {(quality.get('source_trail') or {}).get('level', 'unknown')}")
            print(f"{self.t['translation_status']}: {(quality.get('translation') or {}).get('overall', 'unknown')}")
            print(f"{self.t['media_status']}: {quality.get('media_paths', 'unknown')}")

            action = input(self.t["case_actions"]).strip().casefold()
            if not action:
                return
            if action == "b":
                if incident_id in self.state["bookmarks"]:
                    self.state["bookmarks"].remove(incident_id)
                    print(self.t["unbookmarked"])
                else:
                    self.state["bookmarks"].append(incident_id)
                    print(self.t["bookmarked"])
                self._save_state()
                self.pause()
            elif action == "m":
                self.show_media(entry)
            elif action == "x":
                self.export_single_prompt(entry)
            elif action == "f":
                folder = APP_DIR / str(entry.get("incident_folder") or "")
                if not open_path(folder):
                    print(self.t["open_failed"])
                    print(folder)
                    self.pause()
            elif action == "s":
                self.header(self.t["metadata"])
                metadata = {key: value for key, value in entry.items() if key not in {"article", "proof_dossier", "reading_report"}}
                print(json.dumps(metadata, ensure_ascii=False, indent=2))
                self.pause()
            else:
                print(self.t["invalid"])

    def show_media(self, entry: Mapping[str, Any]) -> None:
        images = [str(item) for item in entry.get("images") or []]
        if not images:
            print(self.t["media_none"])
            self.pause()
            return
        self.header(localize(entry, "title", self.lang) + " - Media")
        for index, relative in enumerate(images, 1):
            path = APP_DIR / relative
            status = "OK" if path.is_file() else "MISSING"
            print(f"[{index}] {relative} ({status})")
        choice = input("\n" + self.t["media_prompt"]).strip()
        if not choice:
            return
        if choice.isdigit() and 1 <= int(choice) <= len(images):
            path = APP_DIR / images[int(choice) - 1]
            if not path.is_file():
                print(self.t["missing_file"].format(path=path))
            elif not open_path(path):
                print(self.t["open_failed"])
                print(path)
            self.pause()

    def browse_timeline(self) -> None:
        counts = Counter(year_as_int(entry) for entry in self.entries)
        years = sorted(year for year in counts if year)
        self.header(self.t["timeline_title"])
        for index, year in enumerate(years, 1):
            print(f"[{index}] {year} ({counts[year]})")
        choice = input("\n" + self.t["choose_group"]).strip()
        if choice.isdigit() and 1 <= int(choice) <= len(years):
            selected = years[int(choice) - 1]
            results = [entry for entry in self.entries if year_as_int(entry) == selected]
            results.sort(key=lambda entry: (detect_country(entry), localize(entry, "title", self.lang).casefold()))
            self.paginate(results, export_name=f"timeline-{selected}")

    def browse_categories(self) -> None:
        mode = input("[1] " + self.t["categories_title"] + "  [2] " + self.t["evidence_title"] + ": ").strip()
        field = "evidence_level" if mode == "2" else "category"
        title = self.t["evidence_title"] if mode == "2" else self.t["categories_title"]
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for entry in self.entries:
            label = localize(entry, field, self.lang).strip() or "(unknown)"
            groups[label].append(entry)
        ordered = sorted(groups, key=lambda label: (-len(groups[label]), label.casefold()))
        self.header(title)
        for index, label in enumerate(ordered, 1):
            print(f"[{index}] {label} ({len(groups[label])})")
        choice = input("\n" + self.t["choose_group"]).strip()
        if choice.isdigit() and 1 <= int(choice) <= len(ordered):
            label = ordered[int(choice) - 1]
            results = sorted(groups[label], key=lambda entry: (year_as_int(entry), localize(entry, "title", self.lang).casefold()))
            self.paginate(results, export_name=safe_filename(label, max_length=60))

    def browse_dates(self) -> None:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for entry in self.entries:
            key = f"{detect_country(entry)} / {parse_date_folder(entry)}"
            groups[key].append(entry)
        ordered = sorted(groups, key=lambda key: (key.split(" / ")[0], key.split(" / ")[1]))
        self.header(self.t["date_title"])
        for index, label in enumerate(ordered, 1):
            print(f"[{index}] {label} ({len(groups[label])})")
        choice = input("\n" + self.t["choose_group"]).strip()
        if choice.isdigit() and 1 <= int(choice) <= len(ordered):
            label = ordered[int(choice) - 1]
            self.paginate(groups[label], export_name=safe_filename(label, max_length=60))

    def bookmarks_history(self) -> None:
        while True:
            choice = input(self.t["bookmark_menu"]).strip()
            if choice == "1":
                results = [self.by_id[item] for item in self.state["bookmarks"] if item in self.by_id]
                if not results:
                    print(self.t["bookmarks_empty"])
                    self.pause()
                else:
                    self.paginate(results, export_name="bookmarks")
            elif choice == "2":
                results = [self.by_id[item] for item in self.state["history"] if item in self.by_id]
                if not results:
                    print(self.t["history_empty"])
                    self.pause()
                else:
                    self.paginate(results, export_name="reading-history")
            elif choice == "3":
                self.state["history"] = []
                self._save_state()
                print(self.t["history_cleared"])
            elif choice == "0":
                return
            else:
                print(self.t["invalid"])

    def select_one(self, prompt: str) -> dict[str, Any] | None:
        self.header(prompt)
        query = input(self.t["select_search"]).strip()
        if not query:
            return None
        terms, filters = parse_query(query)
        scored: list[tuple[int, dict[str, Any]]] = []
        for entry in self.entries:
            if filters and not filter_entries(
                [entry],
                country=filters.get("country", "all"),
                year_text=filters.get("year", "all"),
                category=filters.get("category", "all"),
                evidence=filters.get("evidence", "all"),
                source=filters.get("source", "all"),
            ):
                continue
            score = search_score(entry, terms)
            if score is not None:
                scored.append((score, entry))
        scored.sort(key=lambda item: -item[0])
        candidates = [entry for _, entry in scored[:30]]
        if not candidates:
            print(self.t["no_results"])
            self.pause()
            return None
        self.header(prompt)
        for index, entry in enumerate(candidates, 1):
            print(f"[{index}] {year_as_int(entry)} | {localize(entry, 'title', self.lang)}")
        choice = input("\n" + self.t["choose_group"]).strip()
        if choice.isdigit() and 1 <= int(choice) <= len(candidates):
            return candidates[int(choice) - 1]
        return None

    def compare_cases(self) -> None:
        first = self.select_one(self.t["compare_first"])
        if first is None:
            print(self.t["cancelled"])
            return
        second = self.select_one(self.t["compare_second"])
        if second is None:
            print(self.t["cancelled"])
            return
        self.header("Incident comparison")
        rows = (
            ("Title", localize(first, "title", self.lang), localize(second, "title", self.lang)),
            ("ID", str(first.get("id")), str(second.get("id"))),
            ("Country", detect_country(first), detect_country(second)),
            ("Date", parse_date_folder(first), parse_date_folder(second)),
            (self.t["category"], localize(first, "category", self.lang), localize(second, "category", self.lang)),
            (self.t["evidence"], localize(first, "evidence_level", self.lang), localize(second, "evidence_level", self.lang)),
            (
                self.t["source_status"],
                str(((first.get("quality") or {}).get("source_trail") or {}).get("level", "unknown")),
                str(((second.get("quality") or {}).get("source_trail") or {}).get("level", "unknown")),
            ),
        )
        for label, left, right in rows:
            print(divider("-"))
            print(label)
            print(f"A: {wrap_text(left, terminal_width() - 3)}")
            print(f"B: {wrap_text(right, terminal_width() - 3)}")
        self.pause()

    def export_single_prompt(self, entry: Mapping[str, Any]) -> None:
        choice = input(self.t["export_format"]).strip()
        extension = {"1": "txt", "2": "md", "3": "json"}.get(choice)
        if not extension:
            print(self.t["invalid"])
            self.pause()
            return
        path = self.export_entry(entry, extension)
        print(self.t["exported"].format(path=path))
        self.pause()

    def entry_document(self, entry: Mapping[str, Any], *, markdown: bool = False) -> str:
        title = localize(entry, "title", self.lang)
        heading = f"# {title}" if markdown else title + "\n" + "=" * min(len(title), terminal_width())
        section_prefix = "## " if markdown else ""
        section_underline = "" if markdown else "\n" + "-" * 24
        lines = [
            heading,
            "",
            f"ID: {entry.get('id', '')}",
            f"Country: {detect_country(entry)}",
            f"Date: {parse_date_folder(entry)}",
            f"{self.t['category']}: {localize(entry, 'category', self.lang)}",
            f"{self.t['evidence']}: {localize(entry, 'evidence_level', self.lang)}",
        ]
        for heading_text, field in (
            (self.t["article"], "article"),
            (self.t["proof"], "proof_dossier"),
            (self.t["sources"], "source_trail"),
            (self.t["report"], "reading_report"),
        ):
            content = localize(entry, field, self.lang).strip()
            if content:
                lines.extend(("", section_prefix + heading_text + section_underline, "", content))
        lines.extend(("", self.t["quality"], json.dumps(entry.get("quality") or calculate_entry_quality(entry), ensure_ascii=False, indent=2)))
        return "\n".join(lines).strip() + "\n"

    def export_entry(self, entry: Mapping[str, Any], extension: str) -> Path:
        language_dir = EXPORT_DIR / ("English" if self.lang == "en" else "Greek")
        language_dir.mkdir(parents=True, exist_ok=True)
        filename = safe_filename(f"{parse_date_folder(entry)} - {localize(entry, 'title', self.lang)}")
        path = language_dir / f"{filename}.{extension}"
        if extension == "json":
            path.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        else:
            path.write_text(self.entry_document(entry, markdown=extension == "md"), encoding="utf-8")
        return path

    def export_result_set(self, results: Sequence[Mapping[str, Any]], name: str) -> Path:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        path = EXPORT_DIR / f"{safe_filename(name, max_length=70)}.json"
        path.write_text(json.dumps(list(results), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def export_menu(self) -> None:
        while True:
            choice = input(self.t["export_menu"]).strip()
            EXPORT_DIR.mkdir(parents=True, exist_ok=True)
            if choice == "1":
                path = EXPORT_DIR / "all-incidents.json"
                path.write_text(json.dumps(self.entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            elif choice == "2":
                path = EXPORT_DIR / "compact-index.csv"
                with path.open("w", newline="", encoding="utf-8") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(["ID", "Country", "Date", "Year", "TitleEN", "TitleEL", "CategoryEN", "CategoryEL"])
                    for entry in self.entries:
                        writer.writerow(
                            [
                                entry.get("id", ""),
                                detect_country(entry),
                                parse_date_folder(entry),
                                entry.get("year", ""),
                                localize(entry, "title", "en"),
                                localize(entry, "title", "el"),
                                localize(entry, "category", "en"),
                                localize(entry, "category", "el"),
                            ]
                        )
            elif choice == "3":
                for entry in self.entries:
                    self.export_entry(entry, "txt")
                path = EXPORT_DIR / ("English" if self.lang == "en" else "Greek")
            elif choice == "4":
                results = [self.by_id[item] for item in self.state["bookmarks"] if item in self.by_id]
                path = self.export_result_set(results, "bookmarks")
            elif choice == "0":
                return
            else:
                print(self.t["invalid"])
                continue
            print(self.t["exported"].format(path=path))
            self.pause()

    def show_stats(self) -> None:
        self.header("Archive statistics")
        country_counts = Counter(detect_country(entry) for entry in self.entries)
        years = [year_as_int(entry) for entry in self.entries if year_as_int(entry)]
        categories = Counter(localize(entry, "category", self.lang) or "(unknown)" for entry in self.entries)
        evidence = Counter(localize(entry, "evidence_level", self.lang) or "(unknown)" for entry in self.entries)
        source_levels = Counter(
            str(((entry.get("quality") or {}).get("source_trail") or {}).get("level", "unknown"))
            for entry in self.entries
        )
        translation_levels = Counter(
            str(((entry.get("quality") or {}).get("translation") or {}).get("overall", "unknown"))
            for entry in self.entries
        )
        media_count = sum(len(entry.get("images") or []) for entry in self.entries)
        print(f"Incidents: {len(self.entries)}")
        print(f"Database shards: {self.shard_count}")
        print(f"Countries: {dict(country_counts)}")
        print(f"Year range: {min(years) if years else '-'} - {max(years) if years else '-'}")
        print(f"Unique years: {len(set(years))}")
        print(f"Media references: {media_count}")
        print(f"Source trail status: {dict(source_levels)}")
        print(f"Greek coverage: {dict(translation_levels)}")
        print("\nTop categories:")
        for label, count in categories.most_common(12):
            print(f"- {label}: {count}")
        print("\nTop evidence labels:")
        for label, count in evidence.most_common(12):
            print(f"- {label}: {count}")
        self.pause()

    def show_integrity(self) -> None:
        self.header("Integrity report")
        report = audit_project(APP_DIR)
        print(self.t["integrity_pass"] if report["ok"] else self.t["integrity_fail"])
        for key, value in report["metrics"].items():
            if isinstance(value, (str, int, float)):
                print(f"{key}: {value}")
        if report["errors"]:
            print("\nErrors:")
            for item in report["errors"]:
                print(f"- {item}")
        if report["warnings"]:
            print("\nEditorial warnings:")
            for item in report["warnings"]:
                print(f"- {item}")
        self.pause()


def cli_search(entries: Sequence[dict[str, Any]], query: str, lang: str, limit: int) -> list[dict[str, Any]]:
    terms, filters = parse_query(query)
    results: list[tuple[int, dict[str, Any]]] = []
    for entry in entries:
        if filters and not filter_entries(
            [entry],
            country=filters.get("country", "all"),
            year_text=filters.get("year", "all"),
            category=filters.get("category", "all"),
            evidence=filters.get("evidence", "all"),
            source=filters.get("source", "all"),
        ):
            continue
        id_filter = normalize_text(filters.get("id", ""))
        if id_filter and id_filter not in normalize_text(entry.get("id", "")):
            continue
        score = search_score(entry, terms)
        if score is not None:
            results.append((score, entry))
    results.sort(key=lambda item: (-item[0], year_as_int(item[1]), localize(item[1], "title", lang).casefold()))
    return [entry for _, entry in results[:limit]]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", choices=("en", "el"), default=None, help="interface/output language")
    parser.add_argument("--search", metavar="QUERY", help="run a non-interactive ranked search")
    parser.add_argument("--limit", type=int, default=20, help="maximum CLI search results")
    parser.add_argument("--stats", action="store_true", help="print compact archive statistics")
    parser.add_argument("--validate", action="store_true", help="run structural validation")
    parser.add_argument("--export-results", metavar="PATH", help="write CLI search results to JSON")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    lang = args.lang
    if lang is None and not any((args.search, args.stats, args.validate)):
        selection = input("Choose language / Διάλεξε γλώσσα: [1] English  [2] Ελληνικά : ").strip()
        lang = "el" if selection == "2" else "en"
    lang = lang or "en"

    if args.validate:
        report = audit_project(APP_DIR)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 1

    database = load_database(APP_DIR)
    if database.errors:
        for error in database.errors:
            print(f"WARNING: {error}", file=sys.stderr)
    if not database.entries:
        print("No database entries could be loaded.", file=sys.stderr)
        return 1

    if args.stats:
        countries = Counter(detect_country(entry) for entry in database.entries)
        years = [year_as_int(entry) for entry in database.entries if year_as_int(entry)]
        output = {
            "records": len(database.entries),
            "database_shards": len(database.shard_paths),
            "countries": dict(countries),
            "year_min": min(years) if years else None,
            "year_max": max(years) if years else None,
            "media_references": sum(len(entry.get("images") or []) for entry in database.entries),
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0

    if args.search:
        results = cli_search(database.entries, args.search, lang, max(1, args.limit))
        for index, entry in enumerate(results, 1):
            print(
                f"{index}. {parse_date_folder(entry)} | {detect_country(entry)} | "
                f"{localize(entry, 'title', lang)} | {entry.get('id')}"
            )
        if args.export_results:
            path = Path(args.export_results).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"Exported {len(results)} result(s) to {path}")
        return 0 if results else 2

    Reader(lang).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
