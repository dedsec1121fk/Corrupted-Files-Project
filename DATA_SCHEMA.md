# Corrupted Files Project — Data Schema

The archive is intentionally readable without software. Each database record mirrors one incident folder.

## Folder layout

```text
Country/
└── DD-MM-YYYY/
    └── Incident title/
        ├── 00 - Incident Overview.txt
        ├── 00A - Summary EN.txt
        ├── 00B - Summary EL.txt
        ├── 01 - Article EN.txt
        ├── 02 - Article EL.txt
        ├── 03 - Proof Dossier EN.txt
        ├── 04 - Proof Dossier EL.txt
        ├── 05 - Source Trail EN.txt
        ├── 06 - Source Trail EL.txt
        ├── 07 - Reading Report EN.txt
        ├── 08 - Reading Report EL.txt
        ├── 09 - Search Keywords.txt
        ├── 10 - Metadata.json
        ├── 11 - Media Index.txt
        ├── 12 - Full Record.json
        ├── 13 - Incident File List.txt
        └── Media/
```

## Required database fields

| Field | Type | Purpose |
|---|---|---|
| `id` | string | Stable unique identifier. Never reuse an ID for another incident. |
| `country` | object | `en` and `el` country labels. |
| `year` | integer | Primary filing year. |
| `date_folder` | string | `DD-MM-YYYY`; unknown day/month use `00`. |
| `incident_folder` | string | Project-relative POSIX path to the incident folder. |
| `title` | object | English and Greek titles. |
| `category` | object | English and Greek editorial category. |
| `evidence_level` | object | English and Greek evidence/uncertainty label. |
| `article` | object | Main English and Greek reading text. |
| `proof_dossier` | object | Supporting evidence notes. |
| `source_trail` | object | Case-specific sources or an explicit note that sourcing is incomplete. |
| `reading_report` | object | Comparative reading guidance. |
| `images` | array | Project-relative paths to existing media files. |
| `source_archive_paths` | object | Language-specific paths to source text and media files. |
| `quality` | object | Machine-generated translation, source, and media-path signals. |
| `audit` | object | Maintenance history and integrity markers. |

## Quality signals

`quality.translation.overall` is a heuristic, not a human certification:

- `good`: Greek script is substantially present and no required bilingual field is obviously duplicated.
- `needs-review`: one or more fields are identical to English or the Greek article remains heavily mixed.
- `missing-fields`: a required bilingual field is missing.

`quality.source_trail.level`:

- `specific-links`: at least one direct source URL is present.
- `descriptive-no-links`: a case-specific trail exists but has no direct URL.
- `generic-guidance`: only general sourcing advice is present.

## Path rules

- Store all paths relative to the repository root.
- Use `/` separators in JSON on every operating system.
- Do not store literal escape artifacts such as `#U2014` in folder names.
- Every path in `images`, metadata, Full Record, Media Index, and database shards must agree.
- Run the repair, rebuild, validation, and tests after changing folders.
