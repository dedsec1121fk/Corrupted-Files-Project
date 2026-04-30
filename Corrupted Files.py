#!/usr/bin/env python3
import json, os, random, re, subprocess, textwrap
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DB_DIR = APP_DIR / "Corrupted Files Database"
EXPORT_DIR = APP_DIR / "Corrupted Files Exports"
EXPORT_DIR.mkdir(exist_ok=True)

UI = {
    "en": {
        "title":"Corrupted Files Offline Reader",
        "loading":"Loading database...",
        "loaded":"Loaded {n} incidents.",
        "menu":"\n[1] Search\n[2] Browse by country/date\n[3] Browse by year\n[4] Display all date folders\n[5] Random incident\n[6] Export all to TXT\n[7] Stats\n[0] Exit\nChoice: ",
        "search":"Search text: ",
        "country":"Country (Greece/USA/all): ",
        "date":"Date folder (DD-MM-YYYY or all): ",
        "year":"Year or all: ",
        "none":"No results.",
        "select":"Select number, Enter to go back: ",
        "back":"Press Enter to continue...",
        "invalid":"Invalid choice.",
        "images":"Images:",
        "openimg":"Open image number or Enter to skip: ",
        "opening":"Opening: {p}",
        "openfail":"Could not open automatically. Path is shown above.",
        "folders":"Available date folders",
        "exported":"Exported to: {p}",
        "stats":"Incidents: {n}\nCountries: {c}\nYears: {y}\nDate folders: {d}\nDatabase files: {f}\nMedia references: {m}",
    },
    "el": {
        "title":"Corrupted Files Offline Reader",
        "loading":"Φόρτωση βάσης...",
        "loaded":"Φορτώθηκαν {n} υποθέσεις.",
        "menu":"\n[1] Αναζήτηση\n[2] Περιήγηση ανά χώρα/ημερομηνία\n[3] Περιήγηση ανά έτος\n[4] Εμφάνιση όλων των φακέλων ημερομηνίας\n[5] Τυχαία υπόθεση\n[6] Εξαγωγή όλων σε TXT\n[7] Στατιστικά\n[0] Έξοδος\nΕπιλογή: ",
        "search":"Κείμενο αναζήτησης: ",
        "country":"Χώρα (Ελλάδα/ΗΠΑ/all): ",
        "date":"Φάκελος ημερομηνίας (DD-MM-YYYY ή all): ",
        "year":"Έτος ή all: ",
        "none":"Δεν βρέθηκαν αποτελέσματα.",
        "select":"Διάλεξε αριθμό, Enter για πίσω: ",
        "back":"Πάτα Enter για συνέχεια...",
        "invalid":"Λάθος επιλογή.",
        "images":"Εικόνες:",
        "openimg":"Άνοιγμα εικόνας με αριθμό ή Enter για παράλειψη: ",
        "opening":"Άνοιγμα: {p}",
        "openfail":"Δεν άνοιξε αυτόματα. Το path φαίνεται παραπάνω.",
        "folders":"Διαθέσιμοι φάκελοι ημερομηνίας",
        "exported":"Έγινε εξαγωγή στο: {p}",
        "stats":"Υποθέσεις: {n}\nΧώρες: {c}\nΈτη: {y}\nΦάκελοι ημερομηνίας: {d}\nΑρχεία βάσης: {f}\nΑναφορές media: {m}",
    }
}

def clear():
    if os.name == "nt":
        os.system("cls")
    elif os.environ.get("TERM"):
        os.system("clear")


def localize(entry, field, lang):
    value = entry.get(field, "")
    if isinstance(value, dict):
        return str(value.get(lang) or value.get("en") or value.get("el") or "")
    return str(value or "")

def detect_country(entry):
    en = localize(entry, "country", "en").lower()
    el = localize(entry, "country", "el").lower()
    if "greece" in en or "ελλά" in el or "ελλα" in el:
        return "Greece"
    return "USA"

def parse_date_folder(entry):
    year = str(entry.get("year") or "0000")
    for key in ("date", "event_date", "date_iso"):
        raw = entry.get(key)
        if isinstance(raw, str):
            s = raw.strip()
            m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
            if m:
                y, mo, d = m.groups(); return f"{d}-{mo}-{y}"
            m = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", s)
            if m:
                d, mo, y = m.groups(); return f"{int(d):02d}-{int(mo):02d}-{y}"
        elif isinstance(raw, dict):
            d, mo, y = raw.get("day"), raw.get("month"), raw.get("year") or year
            if str(d).isdigit() and str(mo).isdigit() and str(y).isdigit():
                return f"{int(d):02d}-{int(mo):02d}-{int(y):04d}"
    return f"00-00-{year}"

def media_path(path_text):
    p = Path(str(path_text))
    return p if p.is_absolute() else APP_DIR / p

def open_media(path_text):
    p = media_path(path_text)
    if not p.exists():
        print("Missing:", p)
        return False
    commands = [
        ["termux-open", str(p)],
        ["am", "start", "-a", "android.intent.action.VIEW", "-d", "file://" + str(p)],
        ["xdg-open", str(p)],
    ]
    for cmd in commands:
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=6)
            return True
        except Exception:
            pass
    return False

def wrap(text, width=88):
    out = []
    for para in str(text).split("\n"):
        if not para.strip():
            out.append("")
            continue
        lines = textwrap.wrap(para, width=width, replace_whitespace=False, drop_whitespace=True)
        out.extend(lines or [""])
    return "\n".join(out)

def load_db():
    entries = []
    seen = set()
    db_files = sorted(p for p in DB_DIR.glob("Database Shard *.json"))
    for p in db_files:
        data = json.loads(p.read_text(encoding="utf-8"))
        for entry in data.get("entries", []):
            entry_id = entry.get("id")
            if entry_id and entry_id not in seen:
                seen.add(entry_id)
                entries.append(entry)
    return entries, len(db_files)

def list_results(results, lang, limit=80):
    for i, e in enumerate(results[:limit], 1):
        print(f"[{i}] {parse_date_folder(e)} | {detect_country(e)} | {e.get('year','')} | {localize(e,'title',lang)[:90]}")
    if len(results) > limit:
        print(f"... {len(results)-limit} more")

def show_images(entry, lang):
    imgs = entry.get("images") or []
    if not imgs:
        return
    print("\n" + "-" * 90)
    print(UI[lang]["images"])
    for i, img in enumerate(imgs, 1):
        p = media_path(img)
        status = "OK" if p.exists() else "MISSING"
        print(f"[{i}] {img} ({status})")
    choice = input(UI[lang]["openimg"]).strip()
    if choice.isdigit() and 1 <= int(choice) <= len(imgs):
        p = media_path(imgs[int(choice)-1])
        print(UI[lang]["opening"].format(p=p))
        if not open_media(imgs[int(choice)-1]):
            print(UI[lang]["openfail"])

def show_case(entry, lang):
    clear()
    print("=" * 90)
    print(localize(entry, "title", lang))
    print(f"{detect_country(entry)} / {parse_date_folder(entry)} / {entry.get('year','')}")
    print("=" * 90)
    print(wrap(localize(entry, "article", lang)))
    proof = localize(entry, "proof_dossier", lang).strip()
    sources = localize(entry, "source_trail", lang).strip()
    report = localize(entry, "reading_report", lang).strip()
    if proof:
        print("\n" + "-" * 90 + "\nPROOF\n")
        print(wrap(proof))
    if sources:
        print("\n" + "-" * 90 + "\nSOURCES\n")
        print(wrap(sources))
    if report:
        print("\n" + "-" * 90 + "\nREADING REPORT\n")
        print(wrap(report))
    show_images(entry, lang)
    input("\n" + UI[lang]["back"])

def search(entries, lang):
    q = input(UI[lang]["search"]).strip().lower()
    if not q:
        return
    terms = [t for t in q.split() if t]
    results = []
    for e in entries:
        hay = " ".join([
            e.get("id",""),
            localize(e, "title", "en"),
            localize(e, "title", "el"),
            localize(e, "category", "en"),
            localize(e, "category", "el"),
            localize(e, "article", "en"),
            localize(e, "article", "el"),
            localize(e, "source_trail", "en"),
            localize(e, "source_trail", "el"),
            str(e.get("year","")),
            parse_date_folder(e),
            detect_country(e),
        ]).lower()
        if all(t in hay for t in terms):
            results.append(e)
    if not results:
        print(UI[lang]["none"])
        input(UI[lang]["back"])
        return
    list_results(results, lang)
    s = input(UI[lang]["select"]).strip()
    if s.isdigit() and 1 <= int(s) <= min(80, len(results)):
        show_case(results[int(s)-1], lang)

def browse_country_date(entries, lang):
    c = input(UI[lang]["country"]).strip().lower()
    d = input(UI[lang]["date"]).strip().lower()
    results = []
    for e in entries:
        country = detect_country(e).lower()
        date_folder = parse_date_folder(e).lower()
        okc = (not c or c == "all" or c in country or (c in ("ελλάδα","ελλαδα") and country == "greece") or (c in ("ηπα","hpa") and country == "usa"))
        okd = (not d or d == "all" or d == date_folder)
        if okc and okd:
            results.append(e)
    if not results:
        print(UI[lang]["none"])
        input(UI[lang]["back"])
        return
    results.sort(key=lambda e: (detect_country(e), parse_date_folder(e), localize(e, "title", lang)))
    list_results(results, lang)
    s = input(UI[lang]["select"]).strip()
    if s.isdigit() and 1 <= int(s) <= min(80, len(results)):
        show_case(results[int(s)-1], lang)

def browse_year(entries, lang):
    y = input(UI[lang]["year"]).strip().lower()
    results = []
    for e in entries:
        ey = str(e.get("year","")).lower()
        if not y or y == "all" or y == ey:
            results.append(e)
    if not results:
        print(UI[lang]["none"])
        input(UI[lang]["back"])
        return
    results.sort(key=lambda e: (str(e.get("year","")), detect_country(e), parse_date_folder(e), localize(e, "title", lang)))
    list_results(results, lang)
    s = input(UI[lang]["select"]).strip()
    if s.isdigit() and 1 <= int(s) <= min(80, len(results)):
        show_case(results[int(s)-1], lang)

def display_date_folders(entries, lang):
    clear()
    print(UI[lang]["folders"])
    print("=" * 90)
    mapping = {}
    for e in entries:
        mapping.setdefault(detect_country(e), {}).setdefault(parse_date_folder(e), 0)
        mapping[detect_country(e)][parse_date_folder(e)] += 1
    for country in ("Greece", "USA"):
        print(f"\n{country}")
        print("-" * 90)
        for date_folder, count in sorted(mapping.get(country, {}).items()):
            print(f"{date_folder} — {count} incident(s)")
    input("\n" + UI[lang]["back"])

def export_all(entries, lang):
    folder = EXPORT_DIR / ("English" if lang == "en" else "Greek")
    folder.mkdir(parents=True, exist_ok=True)
    for e in entries:
        title = re.sub(r"[^A-Za-z0-9Α-Ωα-ωΆ-ώ ]+", " ", localize(e, "title", lang)).strip()
        title = re.sub(r"\s+", " ", title)[:80] or e.get("id","incident")
        path = folder / f"{parse_date_folder(e)} - {title}.txt"
        content = [
            localize(e, "title", lang),
            "=" * len(localize(e, "title", lang)),
            "",
            wrap(localize(e, "article", lang)),
            "",
            "PROOF",
            "-----",
            wrap(localize(e, "proof_dossier", lang)),
            "",
            "SOURCES",
            "-------",
            wrap(localize(e, "source_trail", lang)),
            "",
            "READING REPORT",
            "--------------",
            wrap(localize(e, "reading_report", lang)),
        ]
        path.write_text("\n".join(content), encoding="utf-8")
    print(UI[lang]["exported"].format(p=folder))
    input(UI[lang]["back"])

def stats(entries, db_files, lang):
    countries = sorted(set(detect_country(e) for e in entries))
    years = sorted({str(e.get("year","")) for e in entries if str(e.get("year","")).strip()})
    dates = sorted(set(parse_date_folder(e) for e in entries))
    media_refs = sum(len(e.get("images") or []) for e in entries)
    print(UI[lang]["stats"].format(n=len(entries), c=", ".join(countries), y=(", ".join(years[:10]) + (" ..." if len(years) > 10 else "")), d=len(dates), f=db_files, m=media_refs))
    input(UI[lang]["back"])

def main():
    lang_choice = input("Choose language / Διάλεξε γλώσσα: [1] English  [2] Ελληνικά : ").strip()
    lang = "el" if lang_choice == "2" else "en"
    clear()
    print(UI[lang]["title"])
    print(UI[lang]["loading"])
    entries, db_files = load_db()
    print(UI[lang]["loaded"].format(n=len(entries)))
    while True:
        choice = input(UI[lang]["menu"]).strip()
        if choice == "1": search(entries, lang)
        elif choice == "2": browse_country_date(entries, lang)
        elif choice == "3": browse_year(entries, lang)
        elif choice == "4": display_date_folders(entries, lang)
        elif choice == "5": show_case(random.choice(entries), lang)
        elif choice == "6": export_all(entries, lang)
        elif choice == "7": stats(entries, db_files, lang)
        elif choice == "0": break
        else: print(UI[lang]["invalid"])

if __name__ == "__main__":
    main()
