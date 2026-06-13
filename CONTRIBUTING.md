# Contributing

Contributions are welcome when they improve accuracy, sourcing, translation, accessibility, or software reliability.

## Before editing

- Read `RESEARCH_STANDARDS.md` and `DATA_SCHEMA.md`.
- Keep the existing incident ID stable.
- Preserve both English and Greek fields even when one still needs review.
- Never delete warnings merely to make the quality report look cleaner.
- Do not add media without a clear origin and permission-compatible use.

## Adding an incident

1. Create the country/date/incident folder using the standard file set.
2. Give the incident a unique lowercase ID with underscores.
3. Write cautious evidence language and distinguish facts from allegations.
4. Add case-specific sources whenever possible.
5. Add the matching record to a database shard.
6. Run repair, rebuild, validation, and tests.

## Required checks

```bash
python "Corrupted Files Tools/repair_paths.py" --apply
python "Corrupted Files Tools/rebuild_indexes.py"
python "Corrupted Files Tools/validate_rebuilt_structure.py" --write-report
python "Corrupted Files Tools/run_tests.py"
```

## Pull request description

Explain:

- which incidents changed;
- which primary or secondary sources were added;
- whether English and Greek were both reviewed;
- whether any folder or media paths changed;
- the output of the validator and tests.
