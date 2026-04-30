<div align="center">
  <h1>Corrupted Files Project</h1>
  <p><strong>Bilingual offline incident archive for Greece and the USA</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Purpose-Offline%20Research-blue.svg" alt="Purpose: Offline Research">
    <img src="https://img.shields.io/badge/Interface-EN%20%7C%20GR-lightgrey.svg" alt="Interface: EN | GR">
    <img src="https://img.shields.io/badge/Formats-TXT%20%7C%20JSON%20%7C%20CSV-brightgreen.svg" alt="Formats: TXT | JSON | CSV">
    <img src="https://img.shields.io/badge/Use-Termux%20%7C%20Manual-yellow.svg" alt="Use: Termux | Manual">
  </p>
</div>

---

<details>
<summary><strong>🇬🇧 English</strong></summary>

The **Corrupted Files Project** is a structured offline archive of public-interest incidents, institutional-failure cases, public-trust ruptures, disasters, corruption-related files, and historical dossiers focused on **Greece** and the **USA**. Each incident folder is organized so a reader can browse an event manually, search it offline, or use the included Python tool and database shards.

This README is intentionally **bilingual**, using separate **English** and **Greek** sections in the same style as your uploaded example.

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

Το **Corrupted Files Project** είναι ένα δομημένο offline αρχείο υποθέσεων δημόσιου ενδιαφέροντος, θεσμικών αποτυχιών, ρήξεων δημόσιας εμπιστοσύνης, καταστροφών, φακέλων που σχετίζονται με διαφθορά και ιστορικών dossiers με έμφαση στην **Ελλάδα** και τις **ΗΠΑ**. Κάθε φάκελος υπόθεσης είναι οργανωμένος ώστε ο αναγνώστης να μπορεί να περιηγηθεί χειροκίνητα στο γεγονός, να το αναζητήσει offline ή να χρησιμοποιήσει το παρεχόμενο Python εργαλείο και τα database shards.

Αυτό το README είναι σκόπιμα **δίγλωσσο**, με ξεχωριστές ενότητες **English** και **Greek**, στο ίδιο ύφος με το παράδειγμα που ανέβασες.

</details>

## 📋 Table of Contents

* [What This Project Is About](#-what-this-project-is-about)
* [How To Download](#-how-to-download)
* [How To Use](#-how-to-use)
* [Project Structure](#-project-structure)
* [Validation And Rebuild](#-validation-and-rebuild)
* [Notes](#-notes)

---

## 📚 What This Project Is About

<details>
<summary><strong>🇬🇧 English</strong></summary>

This repository stores incidents as **country -> year folder -> incident folder**. Inside each incident you get paired **EN / EL** text files, metadata, a full JSON record, media references, and index files for faster browsing.

The goal is not to force one conclusion. The goal is to give the reader a cleaner offline structure for comparing public records, reported events, institutional responses, and long-term patterns.

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

Αυτό το repository αποθηκεύει τις υποθέσεις ως **χώρα -> φάκελος έτους -> φάκελος υπόθεσης**. Μέσα σε κάθε υπόθεση υπάρχουν ζευγαρωμένα αρχεία **EN / EL**, metadata, πλήρες JSON record, media references και index files για γρηγορότερη περιήγηση.

Ο στόχος δεν είναι να επιβάλει ένα μόνο συμπέρασμα. Ο στόχος είναι να δώσει στον αναγνώστη μια πιο καθαρή offline δομή για να συγκρίνει δημόσια αρχεία, καταγεγραμμένα γεγονότα, θεσμικές αντιδράσεις και μακροχρόνια μοτίβα.

</details>

---

## ⬇️ How To Download

<details>
<summary><strong>🇬🇧 English</strong></summary>

### Option 1: Download from GitHub

- Open the repository page.
- Tap **Code**.
- Choose **Download ZIP**.
- Extract it anywhere you want.

### Option 2: Clone with Termux

```bash
git clone https://github.com/dedsec1121fk/Corrupted-Files-Project.git
```

Then enter the folder:

```bash
cd Corrupted-Files-Project
```

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

### Επιλογή 1: Κατέβασμα από GitHub

- Άνοιξε τη σελίδα του repository.
- Πάτησε **Code**.
- Διάλεξε **Download ZIP**.
- Κάνε extract όπου θέλεις.

### Επιλογή 2: Clone με Termux

```bash
git clone https://github.com/dedsec1121fk/Corrupted-Files-Project.git
```

Μετά μπες στον φάκελο:

```bash
cd Corrupted-Files-Project
```

</details>

---

## ▶️ How To Use

<details>
<summary><strong>🇬🇧 English</strong></summary>

You can use the project in two ways.

### 1. Manual browsing

Open the **Greece** or **USA** folder, choose a year folder, then open any incident folder. Every incident includes paired English and Greek files plus JSON records and media references.

### 2. Run the main script in Termux

```bash
python "Corrupted Files.py"
```

This is useful if you want a more guided way to browse the archive from the terminal.

### Helpful files at the root

- `00 - Master Incident Index.txt`
- `00 - Master Incident Index.json`
- `00 - Master Incident Index.csv`
- `00 - Dates by Country.txt`
- `00 - Statistics.txt`

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

Μπορείς να χρησιμοποιήσεις το project με δύο τρόπους.

### 1. Χειροκίνητη περιήγηση

Άνοιξε τον φάκελο **Greece** ή **USA**, διάλεξε έναν φάκελο έτους και μετά άνοιξε οποιονδήποτε φάκελο υπόθεσης. Κάθε υπόθεση περιλαμβάνει ζευγαρωμένα αρχεία English και Greek, μαζί με JSON records και media references.

### 2. Τρέξιμο του main script στο Termux

```bash
python "Corrupted Files.py"
```

Αυτό είναι χρήσιμο αν θέλεις έναν πιο καθοδηγούμενο τρόπο περιήγησης του archive από το terminal.

### Χρήσιμα αρχεία στη ρίζα

- `00 - Master Incident Index.txt`
- `00 - Master Incident Index.json`
- `00 - Master Incident Index.csv`
- `00 - Dates by Country.txt`
- `00 - Statistics.txt`

</details>

---

## 🗂️ Project Structure

<details>
<summary><strong>🇬🇧 English</strong></summary>

### Root folders

- `Greece/`
- `USA/`
- `Corrupted Files Database/`
- `Corrupted Files Tools/`

### Standard incident contents

- `00 - Incident Overview.txt`
- `00A - Summary EN.txt`
- `00B - Summary EL.txt`
- `01 - Article EN.txt`
- `02 - Article EL.txt`
- `03 - Proof Dossier EN.txt`
- `04 - Proof Dossier EL.txt`
- `05 - Source Trail EN.txt`
- `06 - Source Trail EL.txt`
- `07 - Reading Report EN.txt`
- `08 - Reading Report EL.txt`
- `09 - Search Keywords.txt`
- `10 - Metadata.json`
- `11 - Media Index.txt`
- `12 - Full Record.json`
- `13 - Incident File List.txt`
- `Media/`

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

### Φάκελοι ρίζας

- `Greece/`
- `USA/`
- `Corrupted Files Database/`
- `Corrupted Files Tools/`

### Τυπικά περιεχόμενα κάθε υπόθεσης

- `00 - Incident Overview.txt`
- `00A - Summary EN.txt`
- `00B - Summary EL.txt`
- `01 - Article EN.txt`
- `02 - Article EL.txt`
- `03 - Proof Dossier EN.txt`
- `04 - Proof Dossier EL.txt`
- `05 - Source Trail EN.txt`
- `06 - Source Trail EL.txt`
- `07 - Reading Report EN.txt`
- `08 - Reading Report EL.txt`
- `09 - Search Keywords.txt`
- `10 - Metadata.json`
- `11 - Media Index.txt`
- `12 - Full Record.json`
- `13 - Incident File List.txt`
- `Media/`

</details>

---

## 🧪 Validation And Rebuild

<details>
<summary><strong>🇬🇧 English</strong></summary>

Validate the current structure with:

```bash
python "Corrupted Files Tools/validate_rebuilt_structure.py"
```

Rebuild the indexes with:

```bash
python "Corrupted Files Tools/rebuild_indexes.py"
```

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

Έλεγξε τη δομή με:

```bash
python "Corrupted Files Tools/validate_rebuilt_structure.py"
```

Κάνε rebuild τα indexes με:

```bash
python "Corrupted Files Tools/rebuild_indexes.py"
```

</details>

---

## 📝 Notes

<details>
<summary><strong>🇬🇧 English</strong></summary>

This cleaned archive was repacked to reduce duplicate incident folders, keep the bilingual EN/EL layout, and preserve the root indexes and database structure used by the project.

</details>

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

Αυτό το καθαρισμένο archive ξανασυσκευάστηκε ώστε να μειώσει duplicate incident folders, να κρατήσει το δίγλωσσο EN/EL layout και να διατηρήσει τα root indexes και τη database structure που χρησιμοποιεί το project.

</details>
