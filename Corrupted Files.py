#!/usr/bin/env python3
# Corrupted Files.py — Offline JSON reader for Termux/no-root Python.
# Standard library only.

import json, os, sys, textwrap, random, re, subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DB_DIR = APP_DIR / "Corrupted Files Database"
MEDIA_DIR = APP_DIR / "Corrupted Files Media"
EXPORT_DIR = APP_DIR / "Corrupted Files Exports"
EXPORT_DIR.mkdir(exist_ok=True)

UI = {
    "en": {
        "title":"Corrupted Files Offline Reader",
        "loading":"Loading JSON database...",
        "loaded":"Loaded {n} cases.",
        "menu":"\n[1] Search\n[2] Browse by country/year\n[3] Display all folders by year\n[4] Random case\n[5] Export all cases to TXT\n[6] Database stats\n[0] Exit\nChoice: ",
        "search":"Search text: ","none":"No results.","select":"Select number, Enter to go back: ",
        "country":"Country (USA/Greece/all): ","year":"Year or all: ","back":"Press Enter to continue...",
        "exported":"Exported to: {p}","lang":"Choose language / Διάλεξε γλώσσα: [1] English  [2] Ελληνικά : ",
        "images":"Images:","sources":"Source trail / proof:","invalid":"Invalid choice.",
        "stats":"Cases: {n}\nYears: {a}-{b}\nCountries: {c}\nDatabase files: {d}\nMedia references: {m}",
        "openimg":"Open image number with gallery/app, or Enter to skip: ",
        "opening":"Opening: {p}",
        "openfail":"Could not open automatically. Path is printed above. In Termux, install/open Termux:API or use a file manager.",
        "folders":"Available folders by year",
        "case_count":"{n} case(s)"
    },
    "el": {
        "title":"Corrupted Files Offline Reader",
        "loading":"Φόρτωση βάσης JSON...",
        "loaded":"Φορτώθηκαν {n} υποθέσεις.",
        "menu":"\n[1] Αναζήτηση\n[2] Περιήγηση ανά χώρα/έτος\n[3] Εμφάνιση όλων των φακέλων ανά έτος\n[4] Τυχαία υπόθεση\n[5] Εξαγωγή όλων σε TXT\n[6] Στατιστικά βάσης\n[0] Έξοδος\nΕπιλογή: ",
        "search":"Κείμενο αναζήτησης: ","none":"Δεν βρέθηκαν αποτελέσματα.","select":"Διάλεξε αριθμό, Enter για πίσω: ",
        "country":"Χώρα (ΗΠΑ/Ελλάδα/all): ","year":"Έτος ή all: ","back":"Πάτα Enter για συνέχεια...",
        "exported":"Έγινε εξαγωγή στο: {p}","lang":"Choose language / Διάλεξε γλώσσα: [1] English  [2] Ελληνικά : ",
        "images":"Εικόνες:","sources":"Πηγές / τεκμηρίωση:","invalid":"Λάθος επιλογή.",
        "stats":"Υποθέσεις: {n}\nΈτη: {a}-{b}\nΧώρες: {c}\nΑρχεία βάσης: {d}\nΑναφορές media: {m}",
        "openimg":"Άνοιγμα εικόνας με αριθμό σε gallery/app ή Enter για παράλειψη: ",
        "opening":"Άνοιγμα: {p}",
        "openfail":"Δεν άνοιξε αυτόματα. Το path φαίνεται παραπάνω. Στο Termux μπορείς να χρησιμοποιήσεις Termux:API ή file manager.",
        "folders":"Διαθέσιμοι φάκελοι ανά έτος",
        "case_count":"{n} υπόθεση/υποθέσεις"
    }
}

def clear():
    os.system('clear' if os.name != 'nt' else 'cls')

def load_db():
    entries=[]
    if not DB_DIR.exists():
        print("Database folder not found:", DB_DIR); sys.exit(1)
    for p in sorted(DB_DIR.glob("Corrupted Files Database *.json")):
        try:
            data=json.loads(p.read_text(encoding='utf-8'))
            entries.extend(data.get('entries', []))
        except Exception as e:
            print("Failed to read", p, e)
    # dedupe in memory, preserving first copy
    out=[]; seen=set()
    for e in entries:
        eid=e.get('id')
        if eid and eid not in seen:
            seen.add(eid); out.append(e)
    return out

def get(e, field, lang):
    val=e.get(field, '')
    if isinstance(val, dict):
        return val.get(lang) or val.get('en') or val.get('el') or ''
    return str(val or '')

def wrap(s, width=88):
    out=[]
    for para in str(s).split('\n'):
        if not para.strip(): out.append(''); continue
        if len(para) < width or para.startswith('- ') or re.match(r'^\s*\d+[.)]', para):
            out.append(para)
        else:
            out.extend(textwrap.wrap(para, width=width, replace_whitespace=False, drop_whitespace=True))
    return '\n'.join(out)

def media_path(path_text):
    p=Path(str(path_text))
    if p.is_absolute():
        return p
    # JSON paths are usually "Corrupted Files Media/..."
    return APP_DIR / p

def open_media(path_text):
    p=media_path(path_text)
    if not p.exists():
        print("Missing:", p)
        return False
    cmds=[
        ["termux-open", str(p)],
        ["am", "start", "-a", "android.intent.action.VIEW", "-d", "file://"+str(p)],
        ["xdg-open", str(p)]
    ]
    for cmd in cmds:
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=6)
            return True
        except Exception:
            pass
    return False

def show_images(e, lang):
    imgs=e.get('images') or []
    if not imgs:
        return
    print('\n'+'-'*90)
    print(UI[lang]['images'])
    for i, im in enumerate(imgs, 1):
        p=media_path(im)
        status="OK" if p.exists() else "MISSING"
        print(f"[{i}] {im} ({status})")
    choice=input(UI[lang]['openimg']).strip()
    if choice.isdigit() and 1 <= int(choice) <= len(imgs):
        p=media_path(imgs[int(choice)-1])
        print(UI[lang]['opening'].format(p=p))
        if not open_media(imgs[int(choice)-1]):
            print(UI[lang]['openfail'])

def show_case(e, lang):
    clear()
    title=get(e,'title',lang)
    country=get(e,'country',lang)
    year=e.get('year','')
    print('='*90)
    print(f"{title}\n{country} / {year}")
    cat=get(e,'category',lang); ev=get(e,'evidence_level',lang)
    if cat: print(f"Category: {cat}")
    if ev: print(f"Evidence: {ev}")
    print('='*90)
    text=get(e,'article',lang)
    print(wrap(text))
    proof=get(e,'proof_dossier',lang)
    sources=get(e,'source_trail',lang)
    report=get(e,'reading_report',lang)
    if proof or sources or report:
        print('\n'+'-'*90)
        print(UI[lang]['sources'])
        if proof: print('\n[PROOF]\n'+wrap(proof))
        if sources: print('\n[SOURCES]\n'+wrap(sources))
        if report: print('\n[READING REPORT]\n'+wrap(report))
    show_images(e, lang)
    input('\n'+UI[lang]['back'])

def export_case(e, lang, folder=EXPORT_DIR):
    title=get(e,'title',lang)
    slug=re.sub(r'[^A-Za-z0-9Α-Ωα-ωΆ-ώ]+','_',title).strip('_')[:80] or e.get('id','case')
    p=folder / f"{e.get('year','0000')}_{slug}.txt"
    parts=[title, '='*len(title), f"Country: {get(e,'country',lang)}", f"Year: {e.get('year','')}", '']
    for name,field in [('Article','article'),('Proof dossier','proof_dossier'),('Source trail','source_trail'),('Reading report','reading_report')]:
        val=get(e,field,lang)
        if val:
            parts += [name, '-'*len(name), val, '']
    if e.get('images'):
        parts += ['Images','------'] + list(e['images'])
    p.write_text('\n'.join(parts),encoding='utf-8')
    return p

def list_results(results, lang, limit=60):
    for i,e in enumerate(results[:limit],1):
        print(f"[{i}] {e.get('year')} | {get(e,'country',lang)} | {get(e,'title',lang)[:90]}")
    if len(results)>limit: print(f"... {len(results)-limit} more")

def search(entries, lang):
    q=input(UI[lang]['search']).strip().lower()
    if not q: return
    terms=[t for t in q.split() if t]
    res=[]
    for e in entries:
        hay=' '.join([get(e,'title',lang), get(e,'category',lang), get(e,'evidence_level',lang), get(e,'article',lang), get(e,'source_trail',lang)]).lower()
        if all(t in hay for t in terms): res.append(e)
    if not res: print(UI[lang]['none']); input(UI[lang]['back']); return
    list_results(res,lang)
    s=input(UI[lang]['select']).strip()
    if s.isdigit() and 1<=int(s)<=min(60,len(res)): show_case(res[int(s)-1],lang)

def browse(entries, lang):
    c=input(UI[lang]['country']).strip().lower()
    y=input(UI[lang]['year']).strip().lower()
    res=[]
    for e in entries:
        ce=get(e,'country','en').lower(); cel=get(e,'country','el').lower()
        okc=(not c or c=='all' or c in ce or c in cel or (c in ['ηπα','hpa','usa'] and ce=='usa') or (c in ['greece','ελλάδα','ελλαδα'] and ce=='greece'))
        oky=(not y or y=='all' or str(e.get('year'))==y)
        if okc and oky: res.append(e)
    res.sort(key=lambda e:(int(e.get('year',0)) if str(e.get('year','')).isdigit() else 0,get(e,'title',lang)))
    if not res: print(UI[lang]['none']); input(UI[lang]['back']); return
    list_results(res,lang,80)
    s=input(UI[lang]['select']).strip()
    if s.isdigit() and 1<=int(s)<=min(80,len(res)): show_case(res[int(s)-1],lang)

def display_folders_by_year(entries, lang):
    clear()
    print(UI[lang]['folders'])
    print('='*90)
    by={}
    for e in entries:
        by.setdefault(e.get('year','Unknown'),[]).append(e)
    for year in sorted(by, key=lambda x: int(x) if str(x).isdigit() else 999999):
        cases=sorted(by[year], key=lambda e:(get(e,'country',lang), get(e,'title',lang)))
        print(f"\n{year} — {UI[lang]['case_count'].format(n=len(cases))}")
        print('-'*90)
        for e in cases:
            folder=e.get('id','')
            print(f"  [{get(e,'country',lang)}] {folder}")
            print(f"      {get(e,'title',lang)}")
    input('\n'+UI[lang]['back'])

def stats(entries, lang, db_files):
    years=[int(e.get('year')) for e in entries if str(e.get('year')).isdigit()]
    countries=sorted(set(get(e,'country',lang) for e in entries))
    media=sum(len(e.get('images') or []) for e in entries)
    print(UI[lang]['stats'].format(n=len(entries),a=min(years),b=max(years),c=', '.join(countries),d=db_files,m=media))
    input(UI[lang]['back'])

def main():
    print(UI['en']['lang'], end='')
    ch=input().strip()
    lang='el' if ch=='2' else 'en'
    clear(); print(UI[lang]['title']); print(UI[lang]['loading'])
    entries=load_db()
    db_files=len(list(DB_DIR.glob('Corrupted Files Database *.json')))
    print(UI[lang]['loaded'].format(n=len(entries)))
    while True:
        choice=input(UI[lang]['menu']).strip()
        if choice=='1': search(entries,lang)
        elif choice=='2': browse(entries,lang)
        elif choice=='3': display_folders_by_year(entries,lang)
        elif choice=='4': show_case(random.choice(entries),lang)
        elif choice=='5':
            folder=EXPORT_DIR / ('English' if lang=='en' else 'Greek')
            folder.mkdir(parents=True,exist_ok=True)
            for e in entries: export_case(e,lang,folder)
            print(UI[lang]['exported'].format(p=folder)); input(UI[lang]['back'])
        elif choice=='6': stats(entries,lang,db_files)
        elif choice=='0': break
        else: print(UI[lang]['invalid'])

if __name__ == '__main__':
    main()
