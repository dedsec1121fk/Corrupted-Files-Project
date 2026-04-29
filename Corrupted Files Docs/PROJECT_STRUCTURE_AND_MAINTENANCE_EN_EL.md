# Project structure and maintenance / Δομή project και συντήρηση

This file is the maintainer map for the offline reader. Keep it updated when folders, shard rules, or validation rules change.

Αυτό το αρχείο είναι ο χάρτης συντήρησης για τον offline reader. Ενημέρωσέ το όταν αλλάζουν φάκελοι, κανόνες shards ή κανόνες ελέγχου.

---

## 1. Top-level structure / Κεντρική δομή

```text
Corrupted_Files_Project/
├── Corrupted Files.py
├── README.md
├── Corrupted Files Database/
│   ├── manifest.json
│   └── Corrupted Files Database N.json
├── Corrupted Files Media/
│   ├── expansion_v26/
│   ├── expansion_v27/
│   └── ...
├── Corrupted Files Docs/
│   ├── PROJECT_STRUCTURE_AND_MAINTENANCE_EN_EL.md
│   ├── DATABASE_STRUCTURE_EN_EL.txt
│   ├── EVIDENCE_LEVELS_EN_EL.txt
│   ├── NO_DUPLICATES_TRANSLATION_RULES_EN_EL.txt
│   └── GALLERY_AND_YEAR_BROWSER_EN_EL.txt
└── Corrupted Files Exports/
    └── created by the app, not committed
```

| Path | English role | Ελληνικός ρόλος |
| --- | --- | --- |
| `Corrupted Files.py` | The only app launcher. Standard-library Python only. | Ο μοναδικός launcher. Μόνο Python standard library. |
| `README.md` | User-facing install/open guide. | Οδηγός χρήσης, εγκατάστασης και ανοίγματος. |
| `Corrupted Files Database/` | Split JSON database shards and manifest. | Χωρισμένα JSON shards και manifest. |
| `Corrupted Files Media/` | Local cards/images referenced by JSON entries. | Τοπικές κάρτες/εικόνες που δείχνουν οι JSON εγγραφές. |
| `Corrupted Files Docs/` | Maintainer rules, evidence rules, validation notes. | Κανόνες συντήρησης, τεκμηρίωσης και ελέγχου. |
| `Corrupted Files Exports/` | Runtime TXT export output; delete after testing. | Έξοδος TXT από την εφαρμογή· σβήνεται μετά τα tests. |

---

## 2. Database shard rules / Κανόνες database shards

Use this naming pattern:

```text
Corrupted Files Database/Corrupted Files Database 19.json
```

The app loads only files matching:

```text
Corrupted Files Database *.json
```

Each shard must contain:

```json
{
  "project": "Corrupted Files Project",
  "format": "bilingual-json-reader",
  "version": "short-version-label",
  "entries": []
}
```

Required bilingual fields for every entry:

| Field | Rule |
| --- | --- |
| `id` | Stable unique id: `greece_<year>_<topic>` or `usa_<year>_<topic>`. |
| `country` | Must be `{ "en": "Greece", "el": "Ελλάδα" }` or `{ "en": "USA", "el": "ΗΠΑ" }`. |
| `title` | Must have non-empty `en` and `el`. |
| `category` | Must have non-empty `en` and `el`. |
| `evidence_level` | Must have non-empty `en` and `el`. |
| `article` | Full bilingual article text. |
| `proof_dossier` | Bilingual evidence/proof section. |
| `source_trail` | Bilingual source trail. |
| `reading_report` | Bilingual reading guidance. |
| `images` | Relative local paths only. |

Κάθε νέο shard πρέπει να έχει σταθερή δομή, μοναδικά IDs και πλήρη `en` / `el` πεδία. Μην προσθέτεις εγγραφή μόνο στα αγγλικά ή μόνο στα ελληνικά.

---

## 3. Media rules / Κανόνες media

Preferred layout for new expansion assets:

```text
Corrupted Files Media/expansion_v32/
├── greece_YYYY_topic_cover.svg
├── greece_YYYY_topic_proof_map.svg
├── usa_YYYY_topic_cover.svg
└── usa_YYYY_topic_proof_map.svg
```

Rules:

- Use original generated SVG cards when possible.
- Do not copy copyrighted news photos or articles.
- JSON image paths must be relative to the project root.
- Every path listed in `images` must exist.
- SVG files must parse as XML.

Κανόνες:

- Προτίμησε πρωτότυπες generated SVG κάρτες.
- Μην αντιγράφεις copyrighted φωτογραφίες ειδήσεων ή άρθρα.
- Τα paths μέσα στο JSON πρέπει να είναι σχετικά με το root του project.
- Κάθε path που μπαίνει στο `images` πρέπει να υπάρχει.
- Τα SVG πρέπει να είναι έγκυρο XML.

---

## 4. Manifest rules / Κανόνες manifest

`Corrupted Files Database/manifest.json` is not loaded by the reader, but it is the maintainer count file.

Update these after every expansion:

```json
{
  "database_files": 18,
  "records": 456,
  "media_references": 901
}
```

Το `manifest.json` δεν φορτώνεται από τον reader, αλλά πρέπει να δείχνει σωστά πόσα shards, records και media references υπάρχουν.

---

## 5. Export rules / Κανόνες export

Exports are runtime output and should not be committed:

```text
Corrupted Files Exports/
```

Export filenames include both year and stable record id to avoid collisions:

```text
<year>_<record_id>_<title_slug>.txt
```

Τα exports είναι αποτέλεσμα εκτέλεσης και δεν πρέπει να μπαίνουν στο repository. Το filename έχει και `record_id` ώστε δύο ίδιες/παρόμοιες υποθέσεις να μην γράφουν η μία πάνω στην άλλη.

---

## 6. Required validation / Υποχρεωτικός έλεγχος

Run these checks before pushing to `main`.

Τρέξε αυτούς τους ελέγχους πριν κάνεις push στο `main`.

```bash
python3 - <<'PY'
from pathlib import Path
import ast, json, sys
import xml.etree.ElementTree as ET

root = Path('.')
ast.parse((root / 'Corrupted Files.py').read_text(encoding='utf-8'))

fields = ['country','title','category','evidence_level','article','proof_dossier','source_trail','reading_report']
db_files = sorted((root / 'Corrupted Files Database').glob('Corrupted Files Database *.json'))
ids = []
records = 0
media_refs = 0
missing = []
bad_bilingual = []
countries = set()

for db_file in db_files:
    payload = json.loads(db_file.read_text(encoding='utf-8'))
    for entry in payload.get('entries', []):
        records += 1
        ids.append(entry.get('id'))
        countries.add(entry.get('country', {}).get('en'))
        for field in fields:
            value = entry.get(field)
            if not isinstance(value, dict) or not value.get('en') or not value.get('el'):
                bad_bilingual.append((db_file.name, entry.get('id'), field))
        for image in entry.get('images') or []:
            media_refs += 1
            if not (root / image).exists():
                missing.append((entry.get('id'), image))

duplicates = sorted({entry_id for entry_id in ids if ids.count(entry_id) > 1})
manifest = json.loads((root / 'Corrupted Files Database/manifest.json').read_text(encoding='utf-8'))
assert manifest['database_files'] == len(db_files)
assert manifest['records'] == records
assert manifest['media_references'] == media_refs
assert not duplicates, duplicates[:10]
assert not missing, missing[:10]
assert not bad_bilingual, bad_bilingual[:10]
assert countries <= {'Greece', 'USA'}, countries

for svg_file in sorted((root / 'Corrupted Files Media').glob('**/*.svg')):
    ET.parse(svg_file)

print(f'OK: {len(db_files)} shards, {records} records, {media_refs} media references')
PY
```

Optional runtime smoke test:

```bash
printf '1\n6\n\n0\n' | TERM=xterm python3 "Corrupted Files.py"
printf '2\n6\n\n0\n' | TERM=xterm python3 "Corrupted Files.py"
```

Export count check:

```bash
printf '1\n5\n\n0\n' | TERM=xterm python3 "Corrupted Files.py"
python3 - <<'PY'
from pathlib import Path
exports = sorted(Path('Corrupted Files Exports/English').glob('*.txt'))
print(len(exports))
PY
rm -rf "Corrupted Files Exports"
```

---

## 7. Push policy / Πολιτική push

Push completed work to:

```text
main
```

Do not keep extra work branches for normal expansion passes unless a maintainer explicitly asks for a branch.

Μην κρατάς δεύτερα branches για συνηθισμένες επεκτάσεις, εκτός αν ζητηθεί ρητά. Το τελικό project πρέπει να είναι καθαρό στο `main`.
