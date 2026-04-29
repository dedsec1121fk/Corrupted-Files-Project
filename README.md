<div align="center">
  <img src="https://raw.githubusercontent.com/dedsec1121fk/dedsec1121fk.github.io/47ad8e5cbaaee04af552ae6b90edc49cd75b324b/Assets/Images/Logos/Black%20Purple%20Butterfly%20Logo.jpeg" alt="DedSec Project Logo" width="150"/>
  <h1>Corrupted Files Project</h1>
  <p>
    <img src="https://img.shields.io/badge/Purpose-Offline%20Research-purple.svg" alt="Purpose: Offline Research">
    <img src="https://img.shields.io/badge/Platform-Android%20(Termux)-brightgreen.svg" alt="Platform: Android (Termux)">
    <img src="https://img.shields.io/badge/Language-Python-yellow.svg" alt="Language: Python">
    <img src="https://img.shields.io/badge/Database-JSON-blue.svg" alt="Database: JSON">
  </p>
</div>

---

Corrupted Files Project is an offline bilingual research database and Termux reader for cases where public trust breaks: corruption, intelligence operations, state failure, propaganda, surveillance, institutional negligence, public scandals, disasters, cover-up allegations, unexplained public mysteries, and documented abuse of power.

The project follows the same idea as the Offline Survival database style: the important material is stored locally in split JSON files, loaded by a simple Python launcher, and readable without root, pip packages, internet, or a server. It is built for Android phones and low-end devices, while still keeping long dossiers, proof sections, source trails, reading reports, and local images/proof cards.

## Quick overview / Γρήγορη εικόνα

| English | Ελληνικά |
| --- | --- |
| Offline bilingual research reader for Greece and USA public-trust cases. | Offline δίγλωσσος αναγνώστης ερευνητικών φακέλων για υποθέσεις δημόσιας εμπιστοσύνης σε Ελλάδα και ΗΠΑ. |
| Runs with Python only: no root, no pip packages, no server, no internet. | Τρέχει μόνο με Python: χωρίς root, χωρίς pip packages, χωρίς server, χωρίς internet. |
| Each record can include article text, proof dossier, source trail, reading report, and local SVG media cards. | Κάθε εγγραφή μπορεί να έχει άρθρο, φάκελο τεκμηρίωσης, πηγές, αναφορά ανάγνωσης και τοπικές SVG κάρτες. |
| Documented facts, disputed claims, and conspiracy theories must be separated clearly. | Τα τεκμηριωμένα γεγονότα, οι αμφισβητούμενοι ισχυρισμοί και οι θεωρίες συνωμοσίας πρέπει να χωρίζονται καθαρά. |

## ▶️ How to Download and Open in Termux / Λήψη και άνοιγμα στο Termux

<details>
<summary><strong>🇬🇧 English</strong></summary>

Download the repository ZIP from GitHub, or place the project ZIP in your internal storage **Downloads** folder. The ZIP should contain the full project folder.

Open **Termux** and run:

```bash
mkdir -p ~/DedSec/Scripts && unzip -o "/storage/emulated/0/Download/Corrupted_Files_Project.zip" -d ~/DedSec/Scripts
```

Then open the project:

```bash
cd ~/DedSec/Scripts/Corrupted_Files_Project
python "Corrupted Files.py"
```

### What the app can do

- Choose English or Greek.
- Search all cases.
- Browse by country and year.
- Display all available case folders grouped by year.
- Open available images/SVG cards with the Android gallery or a file app when Termux can launch them.
- Read the full article, proof dossier, source trail, and reading report for every record.
- Export all cases into TXT files for offline reading.

### Important notes

- No pip packages are required.
- The database is local and offline.
- The project includes original written dossiers and safe generated SVG media cards.
- News photos or copyrighted articles are not copied into the project.
- Evidence levels matter. A court record, an official archive, a declassified file, a parliamentary record, a regulator report, and a rumor are not equal.

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

Κατέβασε το ZIP του repository από το GitHub ή βάλε το project ZIP στον φάκελο **Downloads** της εσωτερικής μνήμης. Το ZIP πρέπει να περιέχει ολόκληρο τον φάκελο του project.

Άνοιξε το **Termux** και τρέξε:

```bash
mkdir -p ~/DedSec/Scripts && unzip -o "/storage/emulated/0/Download/Corrupted_Files_Project.zip" -d ~/DedSec/Scripts
```

Μετά άνοιξε το project:

```bash
cd ~/DedSec/Scripts/Corrupted_Files_Project
python "Corrupted Files.py"
```

### Τι μπορεί να κάνει η εφαρμογή

- Επιλογή Αγγλικών ή Ελληνικών.
- Αναζήτηση σε όλες τις υποθέσεις.
- Περιήγηση ανά χώρα και έτος.
- Εμφάνιση όλων των διαθέσιμων φακέλων υποθέσεων ανά έτος.
- Άνοιγμα διαθέσιμων εικόνων/SVG καρτών με gallery ή file app, όταν το Termux μπορεί να τις ανοίξει.
- Ανάγνωση πλήρους άρθρου, φακέλου τεκμηρίωσης, πηγών και αναφοράς ανάγνωσης για κάθε εγγραφή.
- Εξαγωγή όλων των υποθέσεων σε TXT για offline ανάγνωση.

### Σημαντικές σημειώσεις

- Δεν απαιτούνται pip packages.
- Η βάση λειτουργεί τοπικά και offline.
- Το project περιέχει πρωτότυπα γραμμένα dossiers και ασφαλείς generated SVG κάρτες.
- Δεν αντιγράφονται copyrighted άρθρα ή φωτογραφίες ειδησεογραφικών πρακτορείων.
- Τα επίπεδα τεκμηρίωσης έχουν σημασία. Δικαστικό αρχείο, επίσημο αρχείο, αποχαρακτηρισμένο έγγραφο, κοινοβουλευτικό υλικό, έκθεση αρχής και φήμη δεν είναι το ίδιο πράγμα.

</details>

---

## 📁 Project Structure / Δομή Project

```text
Corrupted_Files_Project/
├── Corrupted Files.py
├── Corrupted Files Database/
├── Corrupted Files Library/
├── Corrupted Files Media/
├── Corrupted Files Tools/
├── Corrupted Files Updates/
├── Corrupted Files Docs/
└── Corrupted Files Exports/   # created after export
```

For the full maintenance map, naming rules, expansion workflow, and validation commands, read:

Για πλήρη χάρτη συντήρησης, κανόνες ονοματοδοσίας, workflow επέκτασης και εντολές ελέγχου, διάβασε:

- [`Corrupted Files Docs/PROJECT_STRUCTURE_AND_MAINTENANCE_EN_EL.md`](Corrupted%20Files%20Docs/PROJECT_STRUCTURE_AND_MAINTENANCE_EN_EL.md)

Human-friendly country/date mirror:

Ανθρώπινο mirror ανά χώρα/ημερομηνία:

- `Corrupted Files Library/Greece/YYYY/00-00-YYYY/<record-id>__<title>.txt`
- `Corrupted Files Library/USA/YYYY/00-00-YYYY/<record-id>__<title>.txt`
- Current records usually only know the year, so `00-00-YYYY` means unknown day/month. If a future record has a full date, the mirror can use `DD-MM-YYYY`.
- Οι σημερινές εγγραφές συνήθως ξέρουν μόνο το έτος, άρα `00-00-YYYY` σημαίνει άγνωστη ημέρα/μήνας. Αν μελλοντική εγγραφή έχει πλήρη ημερομηνία, το mirror μπορεί να χρησιμοποιεί `DD-MM-YYYY`.

## 🧠 Research Philosophy / Φιλοσοφία Έρευνας

<details>
<summary><strong>🇬🇧 English</strong></summary>

The project is not designed to force one conclusion. It is designed to make each case readable enough that the user can decide what makes sense. Every case should separate:

- confirmed facts
- allegations
- official explanations
- disputed claims
- public impact
- source trails
- unanswered questions

The database includes both heavily documented cases and weaker/disputed public narratives, but they must be labeled honestly. This is important because a corruption database becomes useless if everything is treated with the same confidence.

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

Το project δεν είναι φτιαγμένο για να επιβάλλει ένα συμπέρασμα. Είναι φτιαγμένο ώστε κάθε υπόθεση να είναι αρκετά ξεκάθαρη για να αποφασίζει ο αναγνώστης τι βγάζει νόημα. Κάθε υπόθεση πρέπει να ξεχωρίζει:

- επιβεβαιωμένα γεγονότα
- καταγγελίες
- επίσημες εξηγήσεις
- αμφισβητούμενους ισχυρισμούς
- δημόσια επίδραση
- πηγές
- αναπάντητα ερωτήματα

Η βάση περιέχει και πολύ τεκμηριωμένες υποθέσεις και πιο αδύναμες/αμφισβητούμενες δημόσιες αφηγήσεις, αλλά πρέπει να σημαίνονται με ειλικρίνεια. Αυτό είναι σημαντικό γιατί μια βάση για διαφθορά γίνεται άχρηστη αν όλα παρουσιάζονται με την ίδια βεβαιότητα.

</details>

## ✅ Current Expansion Focus / Τρέχουσα επέκταση

| English | Ελληνικά |
| --- | --- |
| The database now focuses on Greece and USA cases only. | Η βάση πλέον εστιάζει μόνο σε υποθέσεις Ελλάδας και ΗΠΑ. |
| Recent expansion passes add deeper records around state violence, surveillance, police failures, public disasters, intelligence files, financial scandals, media pressure, labor abuse, medical/technology failures, and institutional accountability. | Οι πρόσφατες επεκτάσεις προσθέτουν βαθύτερους φακέλους για κρατική βία, παρακολουθήσεις, αστυνομικές αποτυχίες, δημόσιες καταστροφές, αρχεία υπηρεσιών πληροφοριών, οικονομικά σκάνδαλα, πίεση στα ΜΜΕ, εργασιακή κακοποίηση, ιατρικές/τεχνολογικές αποτυχίες και θεσμική λογοδοσία. |
| The reader remains offline and standard-library only, so it stays usable in Termux without root. | Ο αναγνώστης παραμένει offline και βασισμένος μόνο στην standard library, ώστε να δουλεύει στο Termux χωρίς root. |

## Bilingual data rules / Κανόνες δίγλωσσων δεδομένων

| English | Ελληνικά |
| --- | --- |
| Every reader-facing field should contain both `en` and `el`: country, title, category, evidence level, article, proof dossier, source trail, and reading report. | Κάθε πεδίο που βλέπει ο αναγνώστης πρέπει να έχει και `en` και `el`: χώρα, τίτλο, κατηγορία, επίπεδο τεκμηρίωσης, άρθρο, φάκελο αποδείξεων, πηγές και αναφορά ανάγνωσης. |
| Generated SVG cards are original reading aids, not documentary photos or copied news images. | Οι παραγόμενες SVG κάρτες είναι πρωτότυπα βοηθήματα ανάγνωσης, όχι φωτογραφίες-ντοκουμέντα ή αντιγραμμένες ειδησεογραφικές εικόνες. |
| Conspiracy theories can be included only when labeled as theory/rumor and separated from documented anchors. | Οι θεωρίες συνωμοσίας μπορούν να περιλαμβάνονται μόνο όταν χαρακτηρίζονται ως θεωρία/φήμη και χωρίζονται από τα τεκμηριωμένα σημεία. |
| Stronger evidence means court records, official archives, declassified files, parliamentary material, regulator reports, named investigations, and primary documents. | Ισχυρότερη τεκμηρίωση σημαίνει δικαστικά αρχεία, επίσημα αρχεία, αποχαρακτηρισμένα έγγραφα, κοινοβουλευτικό υλικό, πορίσματα αρχών, επώνυμες έρευνες και πρωτογενή έγγραφα. |
