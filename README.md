# Corrupted Files Project

> **Termux-only bilingual historical research archive for Android.**

> Για να μεταβείτε στην πλήρη Ελληνική έκδοση, συνεχίστε [Πατώντας Εδώ](#corrupted-files-project--ελληνικά).

The **Corrupted Files Project** is an offline bilingual research archive created for **Android + Termux**. It organizes public-interest cases from Greece and the United States into readable dossiers with stories, timelines, evidence warnings, disputed claims, source trails, images, research questions, and personal study tools.

The program is not a verdict machine and it does not present every allegation as fact. Each record separates documented material, interpretation, uncertainty, rumor, and open research questions.

This project is **Termux on Android only**.

## Sections

Open any bullet below to view that section. Every collapsible section is closed by default.

<details>
<summary><strong>• Installation</strong></summary>

Install the required Termux packages:

```bash
pkg update -y
pkg install python git unzip -y
termux-setup-storage
```

Allow Android storage access when requested. Clone and launch the repository:

```bash
cd ~
git clone https://github.com/dedsec1121fk/Corrupted-Files-Project.git
cd Corrupted-Files-Project
python "Offline Survival Project.py"
```

The project is supported only inside Termux on Android.

</details>

<details>
<summary><strong>• Repository Structure</strong></summary>

The root remains intentionally simple:

```text
Greek/
USA/
README.md
Offline Survival Project.py
```

Each country folder contains its case database, image library, image-credit registry, full offline dossier articles, an offline-material manifest and, where available, redistributable historical documents, imported media and local video briefings. The Python launcher reads both databases and provides one unified interface.

Current expansion content: **410 bilingual dossiers** (**180 Greece + 230 USA**), **410 local full dossier articles**, **5 official historical/primary-source documents**, **6 additional redistributable historical images**, and **4 local MP4 visual briefings**. `offline_materials.json` records the bundled material inventory and hashes for each region.

</details>

<details>
<summary><strong>• What Every Case Contains</strong></summary>

Every dossier can include:

- Bilingual title, category, evidence label, summary and case brief
- Full story, additional details and deep-dive analysis
- Timeline and key facts
- Aftermath and long-term legacy
- Accountability map and primary-record targets
- **People and institutions map**
- **Evidence conflicts and uncertainty review**
- **Media framing and public-memory review**
- **Step-by-step next reading path**
- Rumors, misconceptions and disputed claims with status labels
- Direct sources, source-discovery leads and official research portals
- Android Gallery images with credits where required
- Related cases, personal notes, bookmark and read status
- A full local Markdown dossier article plus indexed offline files (documents, historical media and video where available)

</details>

<details>
<summary><strong>• Main Features</strong></summary>

The Termux reader provides:

- Accent-insensitive English and Greek search
- Browsing by country, decade, category and evidence level
- Guided thematic collections
- Chronology explorer
- Random case and recently added cases
- Rumor and disputed-claim browser
- Research-priority queue and source audit
- Case comparison and related-case ranking
- Reading progress and study quizzes
- Private research notebook
- TXT and standalone HTML dossier exports
- Full searchable HTML archive index
- Built-in validation and Termux system doctor
- **`F` Offline files** inside a dossier to open its local article, documents, imported images or video briefing directly with Android/Termux

</details>

<details>
<summary><strong>• Expansion 7.0 — Offline Historical Pack</strong></summary>

Version 7.0 expands the archive while keeping schema compatibility at `6.0`:

- **20 newly researched dossiers**: 10 Greece and 10 USA
- A **full local bilingual Markdown dossier article for every one of the 410 cases**, so core reading works without opening a browser
- Local official/primary-source documents for selected cases
- Additional historical images only when redistribution status is sufficiently clear; credits include source, creator, license and SHA-256
- Local MP4 briefings are **project-created visual summaries**, clearly distinguished from archival footage
- `related_case_ids` and bilingual archive-context notes connect older dossiers to relevant cases
- `offline_article`, `offline_materials`, `content_version`, audit date and expansion metadata are stored in the case data
- Regional `offline_materials.json` manifests provide a machine-checkable inventory
- The validator verifies path safety, existence, non-empty files, file type and SHA-256 integrity for indexed offline material

The archive does **not** silently copy copyrighted third-party articles or documentary/news footage. Full offline articles in `Articles/` are project-authored research syntheses generated from the dossier data and its cited/source-gap context. Where direct case-specific sourcing is still absent in a legacy record, that gap remains visibly flagged rather than being disguised with a generic citation.

</details>

<details>
<summary><strong>• Android Gallery</strong></summary>

Inside a case press **`G`**. The program copies the complete case album to:

```text
/storage/emulated/0/Pictures/Corrupted Files Project/
```

It refreshes Android media indexing and opens the selected image with `termux-open`, allowing Gallery, Google Photos or another viewer. Each album includes an `IMAGE-CREDITS.txt` file.

</details>

<details>
<summary><strong>• Evidence and Rumors</strong></summary>

Evidence labels describe the present archive state, not absolute truth. A source-backed case has attached case-specific links; a limited-source case needs stronger triangulation; a research-scaffold case offers structured leads but should not be cited as fully verified.

Rumor cards identify whether an item is a documented circulating claim, disputed interpretation, common misconception, analytical caution or unsupported allegation. The assessment explains what evidence supports, weakens or leaves the claim unresolved.

</details>

<details>
<summary><strong>• Research Workflow</strong></summary>

Recommended workflow:

1. Read the case brief and full story.
2. Inspect the evidence label and source-strength warning.
3. Open the timeline, facts, people/institutions map and accountability map.
4. Review direct sources before source-discovery portals.
5. Record contradictions instead of deleting inconvenient versions.
6. Inspect rumor status and evidence assessment.
7. Use the primary-record targets and next reading path.
8. Save findings in research notes.
9. Export a dossier only after checking citations and image licenses.

</details>

<details>
<summary><strong>• Commands</strong></summary>

```bash
python "Offline Survival Project.py"
python "Offline Survival Project.py" --validate
python "Offline Survival Project.py" --stats
python "Offline Survival Project.py" --quality-report
python "Offline Survival Project.py" --termux-check
python "Offline Survival Project.py" --new-cases
python "Offline Survival Project.py" --collections
python "Offline Survival Project.py" --progress
python "Offline Survival Project.py" --case CASE_ID
python "Offline Survival Project.py" --gallery CASE_ID
python "Offline Survival Project.py" --export-html CASE_ID
python "Offline Survival Project.py" --export-index en
python "Offline Survival Project.py" --backup-state
```

</details>

<details>
<summary><strong>• Personal Data</strong></summary>

Bookmarks, read status, history, notes and study scores are stored outside the repository in `~/.corrupted_files_project_state.json`. They are not uploaded by the project. Use `--backup-state` before reinstalling or replacing the repository.

Restore a saved state backup with:

```bash
python "Offline Survival Project.py" --restore-state "/storage/emulated/0/Download/Corrupted Files Exports/State Backups/BACKUP.json"
```

</details>

<details>
<summary><strong>• Troubleshooting</strong></summary>

Run:

```bash
python "Offline Survival Project.py" --termux-check
```

If Gallery or exports fail, run `termux-setup-storage` again and verify that `~/storage/downloads` and `~/storage/pictures` exist. If the database does not load, run `--validate`. If the project was extracted inside Downloads and Android blocks execution, move it to Termux home with `cp -r` and run it from `~/Corrupted-Files-Project`.

</details>

<details>
<summary><strong>• Contributing</strong></summary>

Useful contributions add verifiable value: primary documents, independent sources, corrected dates, stronger Greek translations, lawful image credits, clearly labeled uncertainty, or carefully documented new cases. Do not add copied articles, fabricated quotations, unsourced accusations, duplicate cases, AI filler, private personal data or images without permission/license information.

</details>

<details>
<summary><strong>• Disclaimer</strong></summary>

This repository is for education, historical research, media literacy and source evaluation. It is not legal advice, professional historical certification or proof of criminal responsibility. Users must verify claims against original records and current authoritative sources before publication or formal use.

**Created for the DedSec Project community — Termux on Android only.**

</details>

---

# Corrupted Files Project — Ελληνικά

> Για να επιστρέψετε στην πλήρη Αγγλική έκδοση, συνεχίστε [Πατώντας Εδώ](#corrupted-files-project).

Το **Corrupted Files Project** είναι ένα offline δίγλωσσο ερευνητικό αρχείο για **Android + Termux**. Οργανώνει υποθέσεις δημόσιου ενδιαφέροντος από την Ελλάδα και τις Ηνωμένες Πολιτείες σε αναγνώσιμους φακέλους με αφηγήσεις, χρονολόγια, προειδοποιήσεις τεκμηρίωσης, αμφισβητούμενους ισχυρισμούς, διαδρομές πηγών, εικόνες, ερευνητικά ερωτήματα και προσωπικά εργαλεία μελέτης.

Το πρόγραμμα δεν λειτουργεί ως μηχανή έκδοσης ετυμηγορίας και δεν παρουσιάζει κάθε καταγγελία ως γεγονός. Κάθε εγγραφή διαχωρίζει το τεκμηριωμένο υλικό, την ερμηνεία, την αβεβαιότητα, τη φήμη και τα ανοικτά ερευνητικά ερωτήματα.

Το project λειτουργεί **μόνο Termux σε Android**.

## Ενότητες

Άνοιξε οποιαδήποτε κουκκίδα παρακάτω για να δεις την αντίστοιχη ενότητα. Κάθε αναπτυσσόμενη ενότητα είναι κλειστή από προεπιλογή.

<details>
<summary><strong>• Εγκατάσταση</strong></summary>

Εγκατέστησε τα απαραίτητα πακέτα στο Termux:

```bash
pkg update -y
pkg install python git unzip -y
termux-setup-storage
```

Δώσε άδεια πρόσβασης στην αποθήκευση όταν το ζητήσει το Android. Κάνε clone και εκκίνησε το αποθετήριο:

```bash
cd ~
git clone https://github.com/dedsec1121fk/Corrupted-Files-Project.git
cd Corrupted-Files-Project
python "Offline Survival Project.py"
```

Το project υποστηρίζεται μόνο μέσα από Termux σε Android.

</details>

<details>
<summary><strong>• Δομή Αποθετηρίου</strong></summary>

Η ρίζα του αποθετηρίου παραμένει σκόπιμα απλή:

```text
Greek/
USA/
README.md
Offline Survival Project.py
```

Κάθε φάκελος χώρας περιέχει τη βάση υποθέσεων, τη βιβλιοθήκη εικόνων, το αρχείο δικαιωμάτων εικόνων, πλήρη offline άρθρα φακέλων, manifest offline υλικού και, όπου είναι διαθέσιμα, αναδιανεμήσιμα ιστορικά έγγραφα, εισαγόμενο υλικό και τοπικά video briefings. Το Python launcher διαβάζει και τις δύο βάσεις και προσφέρει ένα ενιαίο περιβάλλον.

Η τρέχουσα επέκταση περιέχει **410 δίγλωσσους φακέλους** (**180 Ελλάδα + 230 ΗΠΑ**), **410 πλήρη τοπικά άρθρα φακέλων**, **5 επίσημα ιστορικά/πρωτογενή έγγραφα**, **6 επιπλέον αναδιανεμήσιμες ιστορικές εικόνες** και **4 τοπικά MP4 οπτικά briefings**. Το `offline_materials.json` καταγράφει το πακεταρισμένο υλικό και τα hashes ανά περιοχή.

</details>

<details>
<summary><strong>• Τι Περιέχει Κάθε Υπόθεση</strong></summary>

Κάθε φάκελος μπορεί να περιλαμβάνει:

- Δίγλωσσο τίτλο, κατηγορία, ένδειξη τεκμηρίωσης, περίληψη και σύντομο δελτίο
- Πλήρη αφήγηση, πρόσθετες λεπτομέρειες και εμβάθυνση
- Χρονολόγιο και βασικά στοιχεία
- Συνέπειες και μακροχρόνια κληρονομιά
- Χάρτη λογοδοσίας και στόχους πρωτογενών τεκμηρίων
- **Χάρτη προσώπων και θεσμών**
- **Έλεγχο συγκρούσεων τεκμηρίων και αβεβαιότητας**
- **Έλεγχο πλαισίωσης από τα μέσα και δημόσιας μνήμης**
- **Βήμα-βήμα επόμενη διαδρομή μελέτης**
- Φήμες, παρανοήσεις και αμφισβητούμενους ισχυρισμούς με σαφή κατάσταση
- Άμεσες πηγές, διαδρομές εντοπισμού πηγών και επίσημες ερευνητικές πύλες
- Εικόνες για Android Gallery με αναφορά δικαιωμάτων όπου απαιτείται
- Σχετικές υποθέσεις, προσωπικές σημειώσεις, σελιδοδείκτη και κατάσταση ανάγνωσης
- Πλήρες τοπικό Markdown άρθρο φακέλου και ευρετηριασμένα offline αρχεία (έγγραφα, ιστορικό υλικό και video όπου υπάρχουν)

</details>

<details>
<summary><strong>• Βασικές Λειτουργίες</strong></summary>

Το πρόγραμμα στο Termux προσφέρει:

- Αναζήτηση στα Αγγλικά και Ελληνικά χωρίς πρόβλημα με τόνους
- Περιήγηση ανά χώρα, δεκαετία, κατηγορία και επίπεδο τεκμηρίωσης
- Θεματικές συλλογές
- Εξερεύνηση χρονολογίας
- Τυχαία υπόθεση και πρόσφατα προστεθειμένες υποθέσεις
- Περιήγηση σε φήμες και αμφισβητούμενους ισχυρισμούς
- Ουρά ερευνητικής προτεραιότητας και έλεγχο πηγών
- Σύγκριση υποθέσεων και κατάταξη σχετικών φακέλων
- Πρόοδο ανάγνωσης και κουίζ μελέτης
- Ιδιωτικό ερευνητικό σημειωματάριο
- Εξαγωγή φακέλων σε TXT και αυτόνομο HTML
- Πλήρες αναζητήσιμο HTML ευρετήριο
- Ενσωματωμένο validation και Termux system doctor
- **`F` Offline files** μέσα σε έναν φάκελο για άμεσο άνοιγμα του τοπικού άρθρου, εγγράφων, εισαγόμενων εικόνων ή video briefing μέσω Android/Termux

</details>

<details>
<summary><strong>• Επέκταση 7.0 — Offline Ιστορικό Πακέτο</strong></summary>

Η έκδοση 7.0 επεκτείνει το αρχείο διατηρώντας συμβατότητα schema στο `6.0`:

- **20 νέοι ερευνημένοι φάκελοι**: 10 Ελλάδα και 10 ΗΠΑ
- **Πλήρες τοπικό δίγλωσσο Markdown άρθρο για καθεμία από τις 410 υποθέσεις**, ώστε η βασική μελέτη να λειτουργεί χωρίς browser
- Τοπικά επίσημα/πρωτογενή έγγραφα για επιλεγμένες υποθέσεις
- Πρόσθετες ιστορικές εικόνες μόνο όταν το καθεστώς αναδιανομής είναι αρκετά σαφές· τα credits περιλαμβάνουν πηγή, δημιουργό, άδεια και SHA-256
- Τα τοπικά MP4 briefings είναι **οπτικές περιλήψεις που δημιουργήθηκαν για το project** και διαχωρίζονται σαφώς από αρχειακό footage
- Τα `related_case_ids` και οι δίγλωσσες σημειώσεις archive context συνδέουν και τους παλαιότερους φακέλους με σχετικές υποθέσεις
- Τα `offline_article`, `offline_materials`, `content_version`, ημερομηνία audit και metadata επέκτασης αποθηκεύονται στα δεδομένα κάθε υπόθεσης
- Τα περιφερειακά `offline_materials.json` δίνουν machine-checkable inventory
- Ο validator ελέγχει ασφαλή paths, ύπαρξη, μη κενά αρχεία, τύπο αρχείου και SHA-256 ακεραιότητα για το ευρετηριασμένο offline υλικό

Το αρχείο **δεν** αντιγράφει κρυφά copyrighted άρθρα τρίτων ή documentary/news footage. Τα πλήρη offline άρθρα στο `Articles/` είναι ερευνητικές συνθέσεις του project βασισμένες στα δεδομένα των φακέλων και στο υπάρχον πλαίσιο πηγών/source gaps. Όπου ένας παλαιότερος φάκελος δεν έχει ακόμη άμεση case-specific πηγή, το κενό παραμένει εμφανώς επισημασμένο αντί να καλύπτεται με γενική παραπομπή.

</details>

<details>
<summary><strong>• Συλλογή Android</strong></summary>

Μέσα σε μία υπόθεση πάτησε **`G`**. Το πρόγραμμα αντιγράφει ολόκληρο το άλμπουμ της υπόθεσης στο:

```text
/storage/emulated/0/Pictures/Corrupted Files Project/
```

Ανανεώνει την ευρετηρίαση πολυμέσων του Android και ανοίγει την επιλεγμένη εικόνα με `termux-open`, ώστε να χρησιμοποιήσεις Gallery, Google Photos ή άλλο viewer. Κάθε άλμπουμ περιλαμβάνει αρχείο `IMAGE-CREDITS.txt`.

</details>

<details>
<summary><strong>• Τεκμήρια και Φήμες</strong></summary>

Οι ενδείξεις τεκμηρίωσης περιγράφουν την τρέχουσα κατάσταση του αρχείου και όχι απόλυτη αλήθεια. Μία υπόθεση με πηγές έχει άμεσους συνδέσμους ειδικά για το θέμα· μία υπόθεση περιορισμένων πηγών χρειάζεται ισχυρότερη διασταύρωση· ένας ερευνητικός σκελετός παρέχει οργανωμένες διαδρομές αλλά δεν πρέπει να χρησιμοποιείται ως πλήρως επαληθευμένη αναφορά.

Οι κάρτες φημών δηλώνουν αν πρόκειται για καταγεγραμμένο ισχυρισμό που κυκλοφόρησε, αμφισβητούμενη ερμηνεία, κοινή παρανόηση, αναλυτική προειδοποίηση ή ατεκμηρίωτη καταγγελία. Η αξιολόγηση εξηγεί ποια τεκμήρια τον στηρίζουν, τον αποδυναμώνουν ή τον αφήνουν άλυτο.

</details>

<details>
<summary><strong>• Ροή Έρευνας</strong></summary>

Προτεινόμενη ροή:

1. Διάβασε το σύντομο δελτίο και την πλήρη αφήγηση.
2. Έλεγξε την ένδειξη τεκμηρίωσης και την προειδοποίηση ισχύος πηγών.
3. Άνοιξε το χρονολόγιο, τα βασικά στοιχεία, τον χάρτη προσώπων/θεσμών και τον χάρτη λογοδοσίας.
4. Έλεγξε πρώτα τις άμεσες πηγές και μετά τις ερευνητικές πύλες.
5. Κατέγραψε τις αντιφάσεις αντί να διαγράφεις τις άβολες εκδοχές.
6. Έλεγξε την κατάσταση της φήμης και την αξιολόγηση τεκμηρίων.
7. Χρησιμοποίησε τους στόχους πρωτογενών τεκμηρίων και την επόμενη διαδρομή μελέτης.
8. Αποθήκευσε τα ευρήματα στις ερευνητικές σημειώσεις.
9. Εξήγαγε έναν φάκελο μόνο αφού ελέγξεις παραπομπές και άδειες εικόνων.

</details>

<details>
<summary><strong>• Εντολές</strong></summary>

```bash
python "Offline Survival Project.py"
python "Offline Survival Project.py" --validate
python "Offline Survival Project.py" --stats
python "Offline Survival Project.py" --quality-report
python "Offline Survival Project.py" --termux-check
python "Offline Survival Project.py" --new-cases
python "Offline Survival Project.py" --collections
python "Offline Survival Project.py" --progress
python "Offline Survival Project.py" --case CASE_ID
python "Offline Survival Project.py" --gallery CASE_ID
python "Offline Survival Project.py" --export-html CASE_ID
python "Offline Survival Project.py" --export-index el
python "Offline Survival Project.py" --backup-state
```

Οι επιλογές CLI χρησιμοποιούν τις ίδιες βάσεις δεδομένων και τις ίδιες προειδοποιήσεις τεκμηρίωσης με το διαδραστικό μενού.

</details>

<details>
<summary><strong>• Προσωπικά Δεδομένα</strong></summary>

Οι σελιδοδείκτες, η κατάσταση ανάγνωσης, το ιστορικό, οι σημειώσεις και οι βαθμολογίες μελέτης αποθηκεύονται έξω από το αποθετήριο στο `~/.corrupted_files_project_state.json`. Το project δεν τα ανεβάζει. Χρησιμοποίησε `--backup-state` πριν από επανεγκατάσταση ή αντικατάσταση του αποθετηρίου.

Επαναφορά αποθηκευμένου backup:

```bash
python "Offline Survival Project.py" --restore-state "/storage/emulated/0/Download/Corrupted Files Exports/State Backups/BACKUP.json"
```

</details>

<details>
<summary><strong>• Αντιμετώπιση Προβλημάτων</strong></summary>

Εκτέλεσε:

```bash
python "Offline Survival Project.py" --termux-check
```

Αν αποτυγχάνει το Gallery ή η εξαγωγή, εκτέλεσε ξανά `termux-setup-storage` και έλεγξε ότι υπάρχουν τα `~/storage/downloads` και `~/storage/pictures`. Αν δεν φορτώνεται η βάση, εκτέλεσε `--validate`. Αν το project βρίσκεται στο Download και το Android εμποδίζει την εκτέλεση, αντέγραψέ το στο Termux home με `cp -r` και τρέξ’ το από `~/Corrupted-Files-Project`.

</details>

<details>
<summary><strong>• Συνεισφορά</strong></summary>

Χρήσιμες συνεισφορές προσθέτουν επαληθεύσιμη αξία: πρωτογενή έγγραφα, ανεξάρτητες πηγές, διορθωμένες ημερομηνίες, καλύτερες ελληνικές μεταφράσεις, νόμιμες αναφορές εικόνων, σαφώς επισημασμένη αβεβαιότητα ή προσεκτικά τεκμηριωμένες νέες υποθέσεις. Μην προσθέτεις αντιγραμμένα άρθρα, κατασκευασμένα αποσπάσματα, κατηγορίες χωρίς πηγές, διπλότυπες υποθέσεις, κείμενο-γέμισμα από AI, ιδιωτικά προσωπικά δεδομένα ή εικόνες χωρίς άδεια/στοιχεία δικαιωμάτων.

</details>

<details>
<summary><strong>• Αποποίηση Ευθύνης</strong></summary>

Το αποθετήριο προορίζεται για εκπαίδευση, ιστορική έρευνα, παιδεία στα μέσα και αξιολόγηση πηγών. Δεν αποτελεί νομική συμβουλή, επαγγελματική ιστορική πιστοποίηση ή απόδειξη ποινικής ευθύνης. Οι χρήστες πρέπει να επαληθεύουν τους ισχυρισμούς στα πρωτότυπα αρχεία και σε σύγχρονες έγκυρες πηγές πριν από δημοσίευση ή επίσημη χρήση.

**Δημιουργήθηκε για την κοινότητα του DedSec Project — μόνο Termux σε Android.**

</details>
