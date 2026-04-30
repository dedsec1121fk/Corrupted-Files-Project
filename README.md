# Corrupted Files Project

This fully fixed rebuild removes the old split structure and uses a clearer layout:

- `Greece/`
- `USA/`
- inside each country: `DD-MM-YYYY/`
- inside each date folder: one incident folder per case
- inside each incident folder: text files, metadata, full record snapshot, and `Media/`

## What was removed

- `Corrupted Files Library`
- `Corrupted Files Media`
- `Corrupted Files Docs`
- `Corrupted Files Updates`
- `__pycache__/`

## What remains

- `Corrupted Files.py`
- `Corrupted Files Database/`
- `Corrupted Files Tools/`
- `Greece/`
- `USA/`
- root index files

## Incident folder files

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

## Root index files

- `00 - Master Incident Index.txt`
- `00 - Master Incident Index.json`
- `00 - Master Incident Index.csv`
- `00 - Dates by Country.txt`
- `00 - Statistics.txt`

## Database

The rebuilt database uses `Database Shard 01.json` style names and all `images` paths now point to the new incident-level media folders.

- Incidents: 456
- Media references: 901
- Database shards: 19

## Termux

Run the app with:

```bash
python "Corrupted Files.py"
```

Validate the rebuild with:

```bash
python "Corrupted Files Tools/validate_rebuilt_structure.py"
```
