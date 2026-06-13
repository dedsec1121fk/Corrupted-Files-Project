# Research and Editorial Standards

This project is an offline research archive, not a court judgment, official finding, or replacement for primary sources. A structurally valid record can still contain an incomplete translation, an outdated interpretation, or insufficient sourcing.

## Required separation

Every dossier should clearly separate:

1. **What is documented** — facts supported by primary records or multiple reliable independent sources.
2. **What is reported** — claims attributed to a named source but not independently established by the archive.
3. **What is alleged** — accusations, legal claims, testimony, or political statements that remain disputed.
4. **What is interpretation** — the archive author's analysis, pattern comparison, or historical framing.
5. **What is unknown** — gaps, unresolved questions, missing records, and contradictory evidence.

## Source priority

Use the strongest available material in this order:

1. Court decisions, legislation, official inquiries, parliamentary records, regulator reports, declassified files, and original datasets.
2. Peer-reviewed research, university archives, professional historical collections, and recognized investigative organizations.
3. Reputable reporting that names sources and links documents.
4. Secondary summaries only when stronger material is unavailable, with that limitation stated.

Avoid presenting social-media posts, anonymous claims, screenshots without provenance, or recycled summaries as established fact.

## Source trail requirements

A mature incident should include case-specific citations, not only general advice. For every source, record enough information to relocate it offline or online:

- institution or author;
- document/article title;
- publication or decision date;
- URL or archive location;
- access date when relevant;
- which claim the source supports;
- whether the source is primary, secondary, disputed, or superseded.

## Evidence labels

Evidence labels must describe certainty, not emotional importance. Prefer wording such as:

- documented by official record;
- supported by multiple independent sources;
- reported but not independently verified;
- contested interpretation;
- allegation under investigation;
- historical dispute with incomplete archive;
- unsupported or disproven claim included for context.

## Translation standards

English and Greek versions should communicate the same claim strength, dates, names, caveats, and source status. Do not translate uncertainty into certainty. Human review is required before marking a record as fully translated.

## Updating a record

When adding or changing an incident:

```bash
python "Corrupted Files Tools/repair_paths.py" --apply
python "Corrupted Files Tools/rebuild_indexes.py"
python "Corrupted Files Tools/validate_rebuilt_structure.py" --write-report
python "Corrupted Files Tools/run_tests.py"
```

A passing validator confirms structural integrity only. Editorial warnings should be reviewed rather than deleted or hidden.
