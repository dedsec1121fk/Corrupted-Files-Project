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

## ▶️ How to Download and Open in Termux

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
├── Corrupted Files Media/
├── Corrupted Files Updates/
├── Corrupted Files Docs/
└── Corrupted Files Exports/   # created after export
```

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

## ✅ Current Expansion Focus

This version adds more records and deeper detail around Greece and USA cases, including **Giorgos Karaivaz**, **Tempi**, surveillance, police failures, state violence, public disasters, intelligence files, financial scandals, and institutional accountability cases.

Η παρούσα έκδοση προσθέτει περισσότερες εγγραφές και βαθύτερη λεπτομέρεια για υποθέσεις Ελλάδας και ΗΠΑ, συμπεριλαμβανομένων **Γιώργου Καραϊβάζ**, **Τεμπών**, παρακολουθήσεων, αστυνομικών αποτυχιών, κρατικής βίας, δημόσιων καταστροφών, αρχείων υπηρεσιών πληροφοριών, οικονομικών σκανδάλων και θεσμικής λογοδοσίας.
