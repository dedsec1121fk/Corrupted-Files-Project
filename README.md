# Corrupted Files Project v24 — JSON Reader

This is an Offline-Survival-style rebuild of the Corrupted Files archive.

## Contents

- `Corrupted Files.py` — Termux/no-root Python reader.
- `Corrupted Files Database/` — split bilingual JSON database files.
- `Corrupted Files Media/` — images and original SVG proof/cover cards referenced by the JSON records.
- `Corrupted Files Updates/` — audit report and research-method guide.
- `Corrupted Files Exports/` — TXT exports created by the reader.

## Termux use

```bash
cd ~/DedSec/Scripts/Corrupted_Files_Project_v24_JSON_Reader
python "Corrupted Files.py"
```

No pip packages are required.

## What v24 fixed

- Converted the old folder archive into JSON records.
- Merged duplicate event folder variants.
- Removed repeated boilerplate from individual files.
- Kept one event per JSON record.
- Kept English and Greek fields in each record.
- Kept images as local media references.
