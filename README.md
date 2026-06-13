<div align="center">
  <h1>Corrupted Files Project</h1>
  <p><strong>Offline incident archive and bilingual research reader for Greece and the USA</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Archive-443%20incidents-blue.svg" alt="443 incidents">
    <img src="https://img.shields.io/badge/Media-981%20references-brightgreen.svg" alt="981 media references">
    <img src="https://img.shields.io/badge/Dashboards-3%20SVGs-blueviolet.svg" alt="3 SVG dashboards">
    <img src="https://img.shields.io/badge/Interface-English%20%7C%20Greek-lightgrey.svg" alt="English and Greek interface">
    <img src="https://img.shields.io/badge/Dependencies-Standard%20Library-yellow.svg" alt="Python standard library only">
  </p>
</div>

---

## English

### What this project is

The **Corrupted Files Project** is a portable archive of public-interest incidents, disasters, institutional failures, corruption-related cases, surveillance controversies, historical dossiers, and public-trust disputes connected mainly to **Greece** and the **United States**.

The project can be used in two ways:

- browse the country, date, and incident folders manually;
- run `Corrupted Files.py` for ranked search, filtering, comparison, bookmarks, exports, statistics, and integrity checks.

The reader uses only Python's standard library. It does not need an account, web server, API key, or permanent internet connection.

### Important research warning

A passing integrity check means that the archive's files, JSON records, indexes, and media paths agree. It **does not** mean that every historical, political, legal, or scientific claim has been independently verified.

The current quality report deliberately identifies remaining editorial work:

- some Greek records are complete enough for practical reading, while others remain mixed or need human translation review;
- many source trails still contain general research guidance rather than case-specific direct citations.
- some generated bilingual cards now explicitly flag Greek fields that still need review instead of pretending unfinished text is complete.

Read `RESEARCH_STANDARDS.md` before treating a dossier as a source. Facts, allegations, reported claims, contested interpretations, and unknowns should remain clearly separated.

### Main reader features

- accent-insensitive English and Greek ranked search;
- exact and partial ID search;
- operators such as `country:`, `year:`, `category:`, `evidence:`, `source:`, and `id:`;
- advanced country, year-range, category, evidence, source-quality, and translation filters;
- timeline, category, evidence, and date-folder browsing;
- pagination for large result lists;
- random incident selection;
- local bookmarks and reading history;
- two-record comparison;
- media opening on Termux, Linux, macOS, and Windows when supported;
- TXT, Markdown, JSON, and CSV exports;
- non-interactive command-line search and statistics;
- built-in structural and editorial-quality reporting.
- original SVG snapshot cards automatically generated for incident folders that previously had only one media visual;
- project and country SVG dashboards for quick archive inspection;
- media manifest files for easier maintenance and browsing;
- 9 downloaded event-related images with explicit source, author, license, checksum, and attribution records;


### Event-image attribution

Downloaded event images are tracked in:

- `00 - Event Image Attribution.json`
- `00 - Event Image Attribution.csv`
- `00 - Event Image Attribution.txt`

The current distributed set contains **9 verified event-image files** across Tulsa Race Massacre and January 6 incident variants. Each record includes the source page, source-file URL, author, license or public-domain statement, checksum, and file size. The validation command is:

```bash
python "Corrupted Files Tools/validate_event_image_attribution.py"
```

Earlier web-imported files without preserved provenance were removed from this build rather than being silently redistributed.

### Download

#### GitHub ZIP

Open the repository, press **Code**, choose **Download ZIP**, and extract it.

#### Termux clone

```bash
git clone https://github.com/dedsec1121fk/Corrupted-Files-Project.git
cd Corrupted-Files-Project
```

### Requirements

- Python 3.10 or newer;
- no third-party Python packages;
- `termux-open` is optional and used only for opening media from Termux.

In Termux:

```bash
pkg update
pkg install python git
```

### Start the reader

```bash
python "Corrupted Files.py"
```

### Search from the command line

```bash
python "Corrupted Files.py" --lang en --search "watergate country:usa" --limit 10
```

More examples:

```bash
python "Corrupted Files.py" --search "year:2023 country:greece"
python "Corrupted Files.py" --search "surveillance source:linked"
python "Corrupted Files.py" --search "category:corruption evidence:documented"
python "Corrupted Files.py" --search "id:tempi" --export-results tempi-results.json
```

### Statistics and validation

```bash
python "Corrupted Files.py" --stats
python "Corrupted Files.py" --validate
```

Full maintenance checks:

```bash
python "Corrupted Files Tools/repair_paths.py" --apply
python "Corrupted Files Tools/rebuild_indexes.py"
python "Corrupted Files Tools/validate_rebuilt_structure.py" --write-report
python "Corrupted Files Tools/run_tests.py"
```

### Project structure

```text
Corrupted-Files-Project/
├── Greece/
├── USA/
├── Corrupted Files Database/
├── Corrupted Files Tools/
├── Corrupted Files.py
├── corrupted_files_core.py
├── 00 - Master Incident Index.txt
├── 00 - Master Incident Index.json
├── 00 - Master Incident Index.csv
├── 00 - Dates by Country.txt
├── 00 - Statistics.txt
├── 00 - Quality Report.txt
├── 00 - Quality Report.json
├── 00 - Editorial Work Queue.csv
├── 00 - Editorial Work Queue.json
├── 00 - Source Link Index.csv
├── 00 - Source Link Index.json
├── 00 - Category Summary.csv
├── DATA_SCHEMA.md
├── RESEARCH_STANDARDS.md
├── CONTRIBUTING.md
└── CHANGELOG.md
```

Each incident folder contains English and Greek reading files, metadata, a full JSON record, search keywords, a media index, and a `Media/` folder. See `DATA_SCHEMA.md` for the exact contract.

### Maintenance tools

| Tool | Purpose |
|---|---|
| `repair_paths.py` | Decodes escaped Unicode names and synchronizes every stored path. |
| `rebuild_indexes.py` | Rebuilds root, country, date, manifest, statistics, and quality indexes. |
| `validate_rebuilt_structure.py` | Checks JSON, IDs, required files, metadata, media, paths, manifest, and indexes. |
| `quality_report.py` | Refreshes the human-readable and JSON quality reports. |
| `run_tests.py` | Runs core, search, filter, CLI, and integrity smoke tests. |
| `push_fixed_rebuild.sh` | Runs repair/rebuild/validation before committing and pushing. |

Generated research indexes include a 443-row editorial work queue, a direct-source-link index, and a category summary so incomplete translation and sourcing work can be prioritized instead of hidden.

### Local data created by the reader

The reader may create:

- `Corrupted Files Exports/` for exports;
- `.corrupted_files_state.json` for bookmarks and reading history.

Both are ignored by Git.

---

## Ελληνικά

### Τι είναι αυτό το project

Το **Corrupted Files Project** είναι ένα φορητό offline αρχείο υποθέσεων δημόσιου ενδιαφέροντος, καταστροφών, θεσμικών αποτυχιών, υποθέσεων διαφθοράς, ζητημάτων παρακολούθησης, ιστορικών φακέλων και ρήξεων δημόσιας εμπιστοσύνης που συνδέονται κυρίως με την **Ελλάδα** και τις **Ηνωμένες Πολιτείες**.

Το project χρησιμοποιείται με δύο τρόπους:

- χειροκίνητη περιήγηση στους φακέλους χώρας, ημερομηνίας και υπόθεσης·
- εκτέλεση του `Corrupted Files.py` για ταξινομημένη αναζήτηση, φίλτρα, σύγκριση, σελιδοδείκτες, εξαγωγές, στατιστικά και ελέγχους ακεραιότητας.

Ο αναγνώστης χρησιμοποιεί μόνο τη standard library της Python. Δεν χρειάζεται λογαριασμό, web server, API key ή μόνιμη σύνδεση στο διαδίκτυο.

### Σημαντική ερευνητική προειδοποίηση

Ένας επιτυχής έλεγχος ακεραιότητας σημαίνει ότι συμφωνούν τα αρχεία, τα JSON records, τα indexes και οι διαδρομές των media. **Δεν** σημαίνει ότι κάθε ιστορικός, πολιτικός, νομικός ή επιστημονικός ισχυρισμός έχει επαληθευτεί ανεξάρτητα.

Η τωρινή quality report εμφανίζει σκόπιμα την εργασία που απομένει:

- ορισμένα ελληνικά records είναι αρκετά ολοκληρωμένα για πρακτική ανάγνωση, ενώ άλλα παραμένουν μικτά ή χρειάζονται ανθρώπινο έλεγχο μετάφρασης·
- πολλά source trails περιέχουν ακόμη γενικές οδηγίες έρευνας αντί για άμεσες, συγκεκριμένες πηγές ανά υπόθεση.

Διάβασε το `RESEARCH_STANDARDS.md` πριν χρησιμοποιήσεις έναν φάκελο ως πηγή. Τα τεκμηριωμένα γεγονότα, οι καταγγελίες, οι αναφερόμενοι ισχυρισμοί, οι αμφισβητούμενες ερμηνείες και τα άγνωστα στοιχεία πρέπει να παραμένουν ξεχωριστά.

### Βασικές δυνατότητες του reader

- ταξινομημένη αναζήτηση σε αγγλικά και ελληνικά χωρίς πρόβλημα από τόνους ή κεφαλαία·
- αναζήτηση με ολόκληρο ή τμήμα του ID·
- operators `country:`, `year:`, `category:`, `evidence:`, `source:` και `id:`·
- σύνθετα φίλτρα χώρας, εύρους ετών, κατηγορίας, τεκμηρίωσης, ποιότητας πηγών και μετάφρασης·
- περιήγηση ανά χρονολόγιο, κατηγορία, επίπεδο τεκμηρίωσης και φάκελο ημερομηνίας·
- pagination για μεγάλα αποτελέσματα·
- τυχαία υπόθεση·
- τοπικοί σελιδοδείκτες και ιστορικό ανάγνωσης·
- σύγκριση δύο records·
- άνοιγμα media σε Termux, Linux, macOS και Windows όπου υποστηρίζεται·
- εξαγωγή TXT, Markdown, JSON και CSV·
- non-interactive αναζήτηση και στατιστικά από command line·
- ενσωματωμένη αναφορά δομικής ακεραιότητας και editorial ποιότητας.

### Κατέβασμα

#### ZIP από GitHub

Άνοιξε το repository, πάτησε **Code**, διάλεξε **Download ZIP** και κάνε extract.

#### Clone στο Termux

```bash
git clone https://github.com/dedsec1121fk/Corrupted-Files-Project.git
cd Corrupted-Files-Project
```

### Απαιτήσεις

- Python 3.10 ή νεότερη·
- κανένα third-party Python package·
- το `termux-open` είναι προαιρετικό και χρησιμοποιείται μόνο για άνοιγμα media στο Termux.

Στο Termux:

```bash
pkg update
pkg install python git
```

### Εκκίνηση

```bash
python "Corrupted Files.py"
```

### Αναζήτηση από command line

```bash
python "Corrupted Files.py" --lang el --search "Τέμπη country:greece" --limit 10
```

Παραδείγματα:

```bash
python "Corrupted Files.py" --search "year:2023 country:greece"
python "Corrupted Files.py" --search "παρακολούθηση source:linked"
python "Corrupted Files.py" --search "category:corruption evidence:documented"
python "Corrupted Files.py" --search "id:tempi" --export-results tempi-results.json
```

### Στατιστικά και έλεγχος

```bash
python "Corrupted Files.py" --stats
python "Corrupted Files.py" --validate
```

Πλήρης διαδικασία συντήρησης:

```bash
python "Corrupted Files Tools/repair_paths.py" --apply
python "Corrupted Files Tools/rebuild_indexes.py"
python "Corrupted Files Tools/validate_rebuilt_structure.py" --write-report
python "Corrupted Files Tools/run_tests.py"
```

### Τοπικά αρχεία που δημιουργεί ο reader

Ο reader μπορεί να δημιουργήσει:

- `Corrupted Files Exports/` για exports·
- `.corrupted_files_state.json` για σελιδοδείκτες και ιστορικό ανάγνωσης.

Και τα δύο αγνοούνται από το Git.

---

## Documentation

- `DATA_SCHEMA.md` — folder and JSON contract.
- `RESEARCH_STANDARDS.md` — evidence, sourcing, uncertainty, and translation rules.
- `CONTRIBUTING.md` — safe contribution workflow.
- `CHANGELOG.md` — repaired defects and new capabilities.
- `00 - Quality Report.txt` — current human-readable integrity and editorial status.
- `00 - Quality Report.json` — machine-readable quality report.
