# Corrupted Files Project

> **Termux-only bilingual historical research archive for Android.**

## English

The paired bilingual sections below follow the same expandable English/Greek format used in the DedSec Sponsors documentation. This project is **Termux on Android only**.

## Ελληνικά

Οι παρακάτω δίγλωσσες ενότητες ακολουθούν την ίδια αναπτυσσόμενη μορφή Αγγλικών/Ελληνικών που χρησιμοποιείται στην τεκμηρίωση των Sponsors του DedSec Project. Το project λειτουργεί **μόνο Termux σε Android**.

---

<details>
<summary><strong>🇬🇧 English</strong></summary>

The **Corrupted Files Project** is an offline bilingual research archive created for **Android + Termux**. It organizes public-interest cases from Greece and the United States into readable dossiers with stories, timelines, evidence warnings, disputed claims, source trails, images, research questions, and personal study tools.

The program is not a verdict machine and it does not present every allegation as fact. Each record separates documented material, interpretation, uncertainty, rumor, and open research questions.

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

Το **Corrupted Files Project** είναι ένα offline δίγλωσσο ερευνητικό αρχείο για **Android + Termux**. Οργανώνει υποθέσεις δημόσιου ενδιαφέροντος από την Ελλάδα και τις Ηνωμένες Πολιτείες σε αναγνώσιμους φακέλους με αφηγήσεις, χρονολόγια, προειδοποιήσεις τεκμηρίωσης, αμφισβητούμενους ισχυρισμούς, διαδρομές πηγών, εικόνες, ερευνητικά ερωτήματα και προσωπικά εργαλεία μελέτης.

Το πρόγραμμα δεν λειτουργεί ως μηχανή έκδοσης ετυμηγορίας και δεν παρουσιάζει κάθε καταγγελία ως γεγονός. Κάθε εγγραφή διαχωρίζει το τεκμηριωμένο υλικό, την ερμηνεία, την αβεβαιότητα, τη φήμη και τα ανοικτά ερευνητικά ερωτήματα.

</details>

## Table of Contents / Πίνακας Περιεχομένων

- [Installation / Εγκατάσταση](#installation--εγκατάσταση)
- [Repository Structure / Δομή Αποθετηρίου](#repository-structure--δομή-αποθετηρίου)
- [What Every Case Contains / Τι Περιέχει Κάθε Υπόθεση](#what-every-case-contains--τι-περιέχει-κάθε-υπόθεση)
- [Main Features / Βασικές Λειτουργίες](#main-features--βασικές-λειτουργίες)
- [Android Gallery / Συλλογή Android](#android-gallery--συλλογή-android)
- [Evidence and Rumors / Τεκμήρια και Φήμες](#evidence-and-rumors--τεκμήρια-και-φήμες)
- [Research Workflow / Ροή Έρευνας](#research-workflow--ροή-έρευνας)
- [Commands / Εντολές](#commands--εντολές)
- [Personal Data / Προσωπικά Δεδομένα](#personal-data--προσωπικά-δεδομένα)
- [Troubleshooting / Αντιμετώπιση Προβλημάτων](#troubleshooting--αντιμετώπιση-προβλημάτων)
- [Contributing / Συνεισφορά](#contributing--συνεισφορά)
- [Disclaimer / Αποποίηση Ευθύνης](#disclaimer--αποποίηση-ευθύνης)

## Installation / Εγκατάσταση

<details>
<summary><strong>🇬🇧 English</strong></summary>

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
python "Use Corrupted Files Project.py"
```

The project is supported only inside Termux on Android.

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

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
python "Use Corrupted Files Project.py"
```

Το project υποστηρίζεται μόνο μέσα από Termux σε Android.

</details>

## Repository Structure / Δομή Αποθετηρίου

<details>
<summary><strong>🇬🇧 English</strong></summary>

The root remains intentionally simple:

```text
Greek/
USA/
README.md
Use Corrupted Files Project.py
```

Each country folder contains its case database, image library, and image-credit registry. The Python launcher reads both databases and provides one unified interface.

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

Η ρίζα του αποθετηρίου παραμένει σκόπιμα απλή:

```text
Greek/
USA/
README.md
Use Corrupted Files Project.py
```

Κάθε φάκελος χώρας περιέχει τη βάση υποθέσεων, τη βιβλιοθήκη εικόνων και το αρχείο πνευματικών δικαιωμάτων εικόνων. Το Python launcher διαβάζει και τις δύο βάσεις και προσφέρει ένα ενιαίο περιβάλλον.

</details>

## What Every Case Contains / Τι Περιέχει Κάθε Υπόθεση

<details>
<summary><strong>🇬🇧 English</strong></summary>

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

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

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

</details>

## Main Features / Βασικές Λειτουργίες

<details>
<summary><strong>🇬🇧 English</strong></summary>

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

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

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

</details>

## Android Gallery / Συλλογή Android

<details>
<summary><strong>🇬🇧 English</strong></summary>

Inside a case press **`G`**. The program copies the complete case album to:

```text
/storage/emulated/0/Pictures/Corrupted Files Project/
```

It refreshes Android media indexing and opens the selected image with `termux-open`, allowing Gallery, Google Photos or another viewer. Each album includes an `IMAGE-CREDITS.txt` file.

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

Μέσα σε μία υπόθεση πάτησε **`G`**. Το πρόγραμμα αντιγράφει ολόκληρο το άλμπουμ της υπόθεσης στο:

```text
/storage/emulated/0/Pictures/Corrupted Files Project/
```

Ανανεώνει την ευρετηρίαση πολυμέσων του Android και ανοίγει την επιλεγμένη εικόνα με `termux-open`, ώστε να χρησιμοποιήσεις Gallery, Google Photos ή άλλο viewer. Κάθε άλμπουμ περιλαμβάνει αρχείο `IMAGE-CREDITS.txt`.

</details>

## Evidence and Rumors / Τεκμήρια και Φήμες

<details>
<summary><strong>🇬🇧 English</strong></summary>

Evidence labels describe the present archive state, not absolute truth. A source-backed case has attached case-specific links; a limited-source case needs stronger triangulation; a research-scaffold case offers structured leads but should not be cited as fully verified.

Rumor cards identify whether an item is a documented circulating claim, disputed interpretation, common misconception, analytical caution or unsupported allegation. The assessment explains what evidence supports, weakens or leaves the claim unresolved.

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

Οι ενδείξεις τεκμηρίωσης περιγράφουν την τρέχουσα κατάσταση του αρχείου και όχι απόλυτη αλήθεια. Μία υπόθεση με πηγές έχει άμεσους συνδέσμους ειδικά για το θέμα· μία υπόθεση περιορισμένων πηγών χρειάζεται ισχυρότερη διασταύρωση· ένας ερευνητικός σκελετός παρέχει οργανωμένες διαδρομές αλλά δεν πρέπει να χρησιμοποιείται ως πλήρως επαληθευμένη αναφορά.

Οι κάρτες φημών δηλώνουν αν πρόκειται για καταγεγραμμένο ισχυρισμό που κυκλοφόρησε, αμφισβητούμενη ερμηνεία, κοινή παρανόηση, αναλυτική προειδοποίηση ή ατεκμηρίωτη καταγγελία. Η αξιολόγηση εξηγεί ποια τεκμήρια τον στηρίζουν, τον αποδυναμώνουν ή τον αφήνουν άλυτο.

</details>

## Research Workflow / Ροή Έρευνας

<details>
<summary><strong>🇬🇧 English</strong></summary>

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
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

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

## Commands / Εντολές

<details>
<summary><strong>🇬🇧 English</strong></summary>

```bash
python "Use Corrupted Files Project.py"
python "Use Corrupted Files Project.py" --validate
python "Use Corrupted Files Project.py" --stats
python "Use Corrupted Files Project.py" --quality-report
python "Use Corrupted Files Project.py" --termux-check
python "Use Corrupted Files Project.py" --new-cases
python "Use Corrupted Files Project.py" --collections
python "Use Corrupted Files Project.py" --progress
python "Use Corrupted Files Project.py" --case CASE_ID
python "Use Corrupted Files Project.py" --gallery CASE_ID
python "Use Corrupted Files Project.py" --export-html CASE_ID
python "Use Corrupted Files Project.py" --export-index en
python "Use Corrupted Files Project.py" --backup-state
```

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

```bash
python "Use Corrupted Files Project.py"
python "Use Corrupted Files Project.py" --validate
python "Use Corrupted Files Project.py" --stats
python "Use Corrupted Files Project.py" --quality-report
python "Use Corrupted Files Project.py" --termux-check
python "Use Corrupted Files Project.py" --new-cases
python "Use Corrupted Files Project.py" --collections
python "Use Corrupted Files Project.py" --progress
python "Use Corrupted Files Project.py" --case CASE_ID
python "Use Corrupted Files Project.py" --gallery CASE_ID
python "Use Corrupted Files Project.py" --export-html CASE_ID
python "Use Corrupted Files Project.py" --export-index el
python "Use Corrupted Files Project.py" --backup-state
```

Οι επιλογές CLI χρησιμοποιούν τις ίδιες βάσεις δεδομένων και τις ίδιες προειδοποιήσεις τεκμηρίωσης με το διαδραστικό μενού.

</details>

## Personal Data / Προσωπικά Δεδομένα

<details>
<summary><strong>🇬🇧 English</strong></summary>

Bookmarks, read status, history, notes and study scores are stored outside the repository in `~/.corrupted_files_project_state.json`. They are not uploaded by the project. Use `--backup-state` before reinstalling or replacing the repository.

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

Οι σελιδοδείκτες, η κατάσταση ανάγνωσης, το ιστορικό, οι σημειώσεις και οι βαθμολογίες μελέτης αποθηκεύονται έξω από το αποθετήριο στο `~/.corrupted_files_project_state.json`. Το project δεν τα ανεβάζει. Χρησιμοποίησε `--backup-state` πριν από επανεγκατάσταση ή αντικατάσταση του αποθετηρίου.

</details>



Restore a saved state backup / Επαναφορά αποθηκευμένου backup:

```bash
python "Use Corrupted Files Project.py" --restore-state "/storage/emulated/0/Download/Corrupted Files Exports/State Backups/BACKUP.json"
```

## Troubleshooting / Αντιμετώπιση Προβλημάτων

<details>
<summary><strong>🇬🇧 English</strong></summary>

Run:

```bash
python "Use Corrupted Files Project.py" --termux-check
```

If Gallery or exports fail, run `termux-setup-storage` again and verify that `~/storage/downloads` and `~/storage/pictures` exist. If the database does not load, run `--validate`. If the project was extracted inside Downloads and Android blocks execution, move it to Termux home with `cp -r` and run it from `~/Corrupted-Files-Project`.

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

Εκτέλεσε:

```bash
python "Use Corrupted Files Project.py" --termux-check
```

Αν αποτυγχάνει το Gallery ή η εξαγωγή, εκτέλεσε ξανά `termux-setup-storage` και έλεγξε ότι υπάρχουν τα `~/storage/downloads` και `~/storage/pictures`. Αν δεν φορτώνεται η βάση, εκτέλεσε `--validate`. Αν το project βρίσκεται στο Download και το Android εμποδίζει την εκτέλεση, αντέγραψέ το στο Termux home με `cp -r` και τρέξ’ το από `~/Corrupted-Files-Project`.

</details>

## Contributing / Συνεισφορά

<details>
<summary><strong>🇬🇧 English</strong></summary>

Useful contributions add verifiable value: primary documents, independent sources, corrected dates, stronger Greek translations, lawful image credits, clearly labeled uncertainty, or carefully documented new cases. Do not add copied articles, fabricated quotations, unsourced accusations, duplicate cases, AI filler, private personal data or images without permission/license information.

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

Χρήσιμες συνεισφορές προσθέτουν επαληθεύσιμη αξία: πρωτογενή έγγραφα, ανεξάρτητες πηγές, διορθωμένες ημερομηνίες, καλύτερες ελληνικές μεταφράσεις, νόμιμες αναφορές εικόνων, σαφώς επισημασμένη αβεβαιότητα ή προσεκτικά τεκμηριωμένες νέες υποθέσεις. Μην προσθέτεις αντιγραμμένα άρθρα, κατασκευασμένα αποσπάσματα, κατηγορίες χωρίς πηγές, διπλότυπες υποθέσεις, κείμενο-γέμισμα από AI, ιδιωτικά προσωπικά δεδομένα ή εικόνες χωρίς άδεια/στοιχεία δικαιωμάτων.

</details>

## Disclaimer / Αποποίηση Ευθύνης

<details>
<summary><strong>🇬🇧 English</strong></summary>

This repository is for education, historical research, media literacy and source evaluation. It is not legal advice, professional historical certification or proof of criminal responsibility. Users must verify claims against original records and current authoritative sources before publication or formal use.

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

Το αποθετήριο προορίζεται για εκπαίδευση, ιστορική έρευνα, παιδεία στα μέσα και αξιολόγηση πηγών. Δεν αποτελεί νομική συμβουλή, επαγγελματική ιστορική πιστοποίηση ή απόδειξη ποινικής ευθύνης. Οι χρήστες πρέπει να επαληθεύουν τους ισχυρισμούς στα πρωτότυπα αρχεία και σε σύγχρονες έγκυρες πηγές πριν από δημοσίευση ή επίσημη χρήση.

</details>

---

**Created for the DedSec Project community — Termux on Android only.**
