# Corrupted Files Project

Corrupted Files Project is an offline bilingual research database and reader for cases where public trust breaks: state corruption, intelligence operations, institutional failure, propaganda, surveillance, public scandals, disasters, cover-up allegations, social-control systems, unexplained public mysteries, and documented abuses of power.

The project is designed to work like the Offline Survival database style: everything important is stored locally, split into JSON files, and readable from a simple Termux Python launcher without root, pip, internet, or a server. The goal is not to force one conclusion on the reader. The goal is to collect each case in a structured way so someone can read the background, timeline, claims, evidence level, source trail, competing explanations, and impact before deciding what makes sense.

## What this project contains

- `Corrupted Files.py` — the offline Termux/no-root Python reader.
- `Corrupted Files Database/` — split bilingual JSON database files with English and Greek fields.
- `Corrupted Files Media/` — local images, original SVG cover cards, and proof-map cards referenced by database records.
- `Corrupted Files Updates/` — audit reports, changelogs, and expansion notes.
- `Corrupted Files Docs/` — explanation files for evidence levels, translation rules, structure, and future expansion.
- `Corrupted Files Exports/` — created by the reader when you export cases into TXT files.

## How the reader works

The launcher loads every JSON database file, combines the records in memory, and lets you search or browse by country and year. Each record is meant to be one event/case, not a random paragraph dump. A good record should include a clear title, country, year, category, evidence level, long article text, proof dossier, source trail, reading report, and local media references.

## Evidence philosophy

The database separates documented cases from disputed claims. Official documents, court records, parliamentary records, government archives, public investigations, and direct institutional admissions should be treated as stronger evidence. Rumors, folklore, supernatural claims, psychological panic, and conspiracy narratives should be labeled as weaker or disputed unless stronger records exist.

This matters because a database about corruption becomes useless if every story is treated the same. A proven court case, a declassified intelligence program, a documented public-health scandal, and an internet rumor are not equal. They can all be included, but they must be labeled honestly.

## Translation philosophy

English and Greek should stay fully parallel. Greek text should not be a broken machine-style copy of English. Proper names, agency names, archive names, acronyms, source titles, URLs, and legal case names may remain in English when translating them would reduce clarity.

## Termux use

```bash
cd ~/DedSec/Scripts/Corrupted_Files_Project
python "Corrupted Files.py"
```

No pip packages are required.

## Repository purpose

This repository is meant to become the main public home of the Corrupted Files Project. Future updates should add more cases, improve existing records, add better media, clean duplicates, improve Greek parity, and keep the database usable offline on Android phones.
