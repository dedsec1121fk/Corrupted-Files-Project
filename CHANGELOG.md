# Changelog

## 2.4 — Verified event-image provenance pass

### Added

- Added 9 verified event-image files across three Tulsa Race Massacre records and three January 6 records.
- Added `00 - Event Image Attribution.json`, `.csv`, and `.txt`.
- Added `validate_event_image_attribution.py` to verify source metadata, rights status, checksums, file sizes, missing files, and untracked files.

### Improved

- Every distributed event image now has an explicit source page, direct source-file URL, author, license/public-domain statement, checksum, and size.
- Removed the 8 earlier event-image imports whose exact provenance had not been preserved well enough.
- Updated dashboards, media manifests, tests, and the Termux maintenance script to include attribution validation.

### Current result

- 981 total media references.
- 9 verified downloaded event-image files.
- 0 untracked event-image files.
- 0 event-image attribution errors.

## 2.3 — First real event-image import pass

### Added

- Added 8 downloaded event-related reference images to the archive.
- Added real event-image coverage for two incidents: Watergate and Hurricane Katrina.
- Added `00 - Added Event Images.txt` and `00 - Added Event Images.csv` to track imported web-derived images.

### Improved

- Watergate now includes actual related reference visuals beyond generated cards.
- Hurricane Katrina now includes multiple real flood, satellite, radar, and storm-reference images.
- Re-synchronized database media lists and indexes after importing the external reference images.

## 2.2 — Dashboard and QA polish pass

### Added

- Added `00 - Project Dashboard.svg` plus `Greece/00 - Country Dashboard.svg` and `USA/00 - Country Dashboard.svg`.
- Added `00 - Media Manifest.json` and `00 - Media Manifest.csv` for maintenance and browsing.
- Added `generate_visual_indexes.py` to regenerate the dashboards and media manifest locally.

### Improved

- Snapshot cards now regenerate cleanly even after the first media-expansion pass.
- Snapshot cards now show a small quality badge for translation/source status.
- Greek-side snapshot summaries now warn when a record still needs Greek review instead of silently mirroring unfinished text.
- Smoke tests now verify that the dashboard and media-manifest outputs exist.

## 2.1 — Media expansion

### Added

- Added 94 original SVG snapshot cards to incident folders that previously had only one media item.
- Increased total media references from 878 to 972.
- Added `generate_snapshot_cards.py` so the media expansion can be regenerated or extended later.

### Improved

- Every single-image incident folder now has an additional visual summary card for offline browsing.
- The new cards summarize title, country, year, category, evidence level, core story, and timeline in a consistent dark neon style.
- Re-synchronized Media Index files, incident metadata, Full Record JSON files, database shards, and root indexes after the media expansion.

## 2.0 — Archive integrity and reader expansion

### Fixed

- Repaired 39 escaped Unicode incident-folder names.
- Synchronized database, metadata, Full Record, Media Index, source archive, and incident-folder paths.
- Eliminated 127 broken media references.
- Regenerated root, country, and date indexes from the incident folders.
- Replaced the minimal validator with a comprehensive structural audit.

### Added

- Ranked accent-insensitive English/Greek search.
- Search operators for country, year, category, evidence, source status, and ID.
- Advanced filtering and multiple sort modes.
- Pagination for large result sets.
- Timeline, category, evidence, and date-folder browsing.
- Bookmarks and recent-reading history stored locally and ignored by Git.
- Side-by-side incident comparison.
- TXT, Markdown, JSON, CSV, bookmark, and complete-archive exports.
- Non-interactive CLI search, statistics, validation, and JSON export.
- Built-in quality signals for Greek coverage, source-trail specificity, and media integrity.
- Machine-readable and human-readable quality reports.
- Editorial work queue with high/medium/low priorities for all 443 records.
- Direct source-link index and category summary.
- Path repair utility, complete index rebuilder, quality-report utility, and smoke-test suite.
- Data schema, editorial standards, and contributor documentation.

### Transparency

- The quality report now explicitly identifies records that need Greek-language review.
- The quality report distinguishes case-specific source links from generic source guidance.
- Structural validation does not claim to fact-check every historical or political assertion.
