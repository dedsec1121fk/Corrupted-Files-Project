# Corrupted Files Library

Human-browsable mirror generated from the JSON database.

This folder is organized by country, year, and date folder:

```text
Corrupted Files Library/<Greece|USA>/<YYYY>/<DD-MM-YYYY>/
```

Most current records only have a year, so they use `00-00-YYYY` to show that exact day/month is unknown.

The JSON database remains the source of truth for the app. Regenerate this mirror with:

```bash
python3 "Corrupted Files Tools/build_country_date_library.py"
```

- Greece records mirrored: 206
- USA records mirrored: 250
- Total records mirrored: 456
