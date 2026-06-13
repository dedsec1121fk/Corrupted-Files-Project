#!/usr/bin/env python3
"""Generate visual dashboards and media manifests for the archive."""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
import html
import textwrap

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from corrupted_files_core import (  # noqa: E402
    load_database,
    localize,
    detect_country,
    translation_status,
    source_trail_status,
)

BG = '#0b0b0f'
PANEL = '#11131a'
PURPLE = '#b78cff'
TEAL = '#8affc1'
WHITE = '#f5f7fb'
MUTED = '#9aa4b2'
ACCENT = '#1a1e29'


def wrap(text: str, width: int) -> list[str]:
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False) or ['—']


def svg_lines(x: int, y: int, lines: list[str], size: int, color: str, *, step_mult: float = 1.35, weight: str = '400') -> tuple[str, int]:
    parts: list[str] = []
    step = int(size * step_mult)
    cy = y
    for line in lines:
        parts.append(f'<text x="{x}" y="{cy}" fill="{color}" font-family="monospace" font-size="{size}" font-weight="{weight}">{html.escape(line)}</text>')
        cy += step
    return ''.join(parts), cy


def panel(x: int, y: int, w: int, h: int, title: str, stroke: str = PURPLE) -> list[str]:
    return [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#0d1016" stroke="{stroke}" stroke-width="1.5"/>',
        f'<text x="{x+20}" y="{y+32}" fill="{stroke}" font-family="monospace" font-size="22" font-weight="700">{html.escape(title)}</text>',
    ]


def write_svg(path: Path, body: str, width: int = 1600, height: int = 900) -> None:
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f'<rect width="{width}" height="{height}" fill="{BG}"/>'
        f'<rect x="32" y="32" width="{width-64}" height="{height-64}" rx="20" fill="none" stroke="{PURPLE}" stroke-width="4"/>'
        f'<rect x="60" y="60" width="{width-120}" height="{height-120}" rx="18" fill="{PANEL}" stroke="{TEAL}" stroke-width="2"/>'
        f'{body}</svg>',
        encoding='utf-8',
    )


def top_categories(entries: list[dict[str, Any]], limit: int = 5) -> list[tuple[str, int]]:
    counter = Counter(localize(entry, 'category', 'en') or 'unknown' for entry in entries)
    return counter.most_common(limit)


def make_project_dashboard(entries: list[dict[str, Any]]) -> str:
    countries = Counter(detect_country(entry) for entry in entries)
    translations = Counter(translation_status(entry)['overall'] for entry in entries)
    sources = Counter(source_trail_status(entry)['level'] for entry in entries)
    years = [int(entry.get('year') or 0) for entry in entries if str(entry.get('year') or '').isdigit()]
    media_count = sum(len(entry.get('images') or []) for entry in entries)
    generated_snapshots = sum(1 for entry in entries if any(str(x).endswith('02 - Bilingual Snapshot.svg') for x in entry.get('images') or []))
    attribution_path = ROOT / '00 - Event Image Attribution.json'
    verified_event_images = 0
    if attribution_path.is_file():
        try:
            verified_event_images = sum(
                1 for item in json.loads(attribution_path.read_text(encoding='utf-8'))
                if isinstance(item, dict) and item.get('rights_status') == 'verified'
            )
        except (OSError, json.JSONDecodeError):
            verified_event_images = 0
    categories = top_categories(entries)

    parts = [
        f'<text x="92" y="118" fill="{PURPLE}" font-family="monospace" font-size="26" font-weight="700">PROJECT DASHBOARD</text>',
        f'<text x="92" y="170" fill="{WHITE}" font-family="monospace" font-size="60" font-weight="700">Corrupted Files Project</text>',
        f'<text x="92" y="205" fill="{MUTED}" font-family="monospace" font-size="20">Visual summary of the offline archive state after the latest polish pass.</text>',
    ]
    parts += panel(92, 240, 420, 235, 'CORE METRICS')
    lines = [
        f'Records: {len(entries)}',
        f'Media references: {media_count}',
        f'Generated snapshot cards: {generated_snapshots}',
        f'Verified event images: {verified_event_images}',
        f'Countries: {len(countries)}',
        f'Year range: {min(years)} - {max(years)}',
    ]
    text, _ = svg_lines(116, 285, lines, 24, WHITE)
    parts.append(text)

    parts += panel(540, 240, 420, 235, 'COUNTRY SPLIT', TEAL)
    lines = [f'{country}: {count}' for country, count in countries.items()]
    text, _ = svg_lines(564, 285, lines, 24, WHITE)
    parts.append(text)

    parts += panel(988, 240, 520, 235, 'QUALITY OVERVIEW')
    lines = [
        f'Translation good: {translations.get("good", 0)}',
        f'Translation needs review: {translations.get("needs-review", 0)}',
        f'Sources generic-guidance: {sources.get("generic-guidance", 0)}',
        f'Sources specific-links: {sources.get("specific-links", 0)}',
        f'Sources descriptive-no-links: {sources.get("descriptive-no-links", 0)}',
    ]
    text, _ = svg_lines(1012, 285, lines, 22, WHITE)
    parts.append(text)

    parts += panel(92, 510, 650, 290, 'TOP CATEGORIES', TEAL)
    y = 555
    for index, (category, count) in enumerate(categories, 1):
        lines = wrap(f'{index}. {category} ({count})', 40)
        text, y = svg_lines(116, y, lines, 24, WHITE, step_mult=1.25, weight='700' if index == 1 else '400')
        parts.append(text)
        y += 8

    parts += panel(780, 510, 728, 290, 'NOTES')
    notes = [
        '• Dashboard values are derived from the synchronized database shards.',
        '• Snapshot cards are generated from project text, not copied from external media.',
        '• A structural PASS means paths and files agree; it does not fact-check every claim.',
        '• Use the editorial queue and source index for the next human review pass.',
    ]
    text, _ = svg_lines(804, 555, notes, 22, WHITE, step_mult=1.4)
    parts.append(text)
    parts.append(f'<text x="92" y="844" fill="{MUTED}" font-family="monospace" font-size="16">Generated locally from project data. No external images copied.</text>')
    return ''.join(parts)


def make_country_dashboard(country: str, entries: list[dict[str, Any]]) -> str:
    translations = Counter(translation_status(entry)['overall'] for entry in entries)
    sources = Counter(source_trail_status(entry)['level'] for entry in entries)
    years = sorted(int(entry.get('year') or 0) for entry in entries if str(entry.get('year') or '').isdigit())
    media_count = sum(len(entry.get('images') or []) for entry in entries)
    verified_event_images = sum(
        1
        for entry in entries
        for image in (entry.get('images') or [])
        if 'Event Image' in str(image)
    )
    categories = top_categories(entries, 6)
    recent = sorted(entries, key=lambda entry: int(entry.get('year') or 0), reverse=True)[:5]

    parts = [
        f'<text x="92" y="118" fill="{PURPLE}" font-family="monospace" font-size="26" font-weight="700">COUNTRY DASHBOARD</text>',
        f'<text x="92" y="170" fill="{WHITE}" font-family="monospace" font-size="64" font-weight="700">{html.escape(country)}</text>',
        f'<text x="92" y="205" fill="{MUTED}" font-family="monospace" font-size="20">Incident count, category spread, and quality signals for this country archive.</text>',
    ]
    parts += panel(92, 240, 420, 215, 'AT A GLANCE', TEAL)
    lines = [
        f'Records: {len(entries)}',
        f'Media references: {media_count}',
        f'Verified event images: {verified_event_images}',
        f'Year range: {years[0]} - {years[-1]}' if years else 'Year range: n/a',
        f'Translation needs review: {translations.get("needs-review", 0)}',
    ]
    text, _ = svg_lines(116, 285, lines, 24, WHITE)
    parts.append(text)

    parts += panel(540, 240, 420, 215, 'SOURCE QUALITY')
    lines = [
        f'generic-guidance: {sources.get("generic-guidance", 0)}',
        f'specific-links: {sources.get("specific-links", 0)}',
        f'descriptive-no-links: {sources.get("descriptive-no-links", 0)}',
    ]
    text, _ = svg_lines(564, 285, lines, 24, WHITE)
    parts.append(text)

    parts += panel(988, 240, 520, 215, 'TRANSLATION STATUS')
    lines = [
        f'good: {translations.get("good", 0)}',
        f'needs-review: {translations.get("needs-review", 0)}',
    ]
    text, _ = svg_lines(1012, 285, lines, 24, WHITE)
    parts.append(text)

    parts += panel(92, 490, 700, 320, 'TOP CATEGORIES', TEAL)
    y = 535
    for idx, (category, count) in enumerate(categories, 1):
        lines = wrap(f'{idx}. {category} ({count})', 44)
        text, y = svg_lines(116, y, lines, 23, WHITE, step_mult=1.25)
        parts.append(text)
        y += 4

    parts += panel(824, 490, 684, 320, 'RECENT-YEAR RECORDS')
    y = 535
    for entry in recent:
        title = localize(entry, 'title', 'en')
        lines = wrap(f'{entry.get("year")}: {title}', 45)
        text, y = svg_lines(848, y, lines, 22, WHITE, step_mult=1.25)
        parts.append(text)
        y += 6

    parts.append(f'<text x="92" y="844" fill="{MUTED}" font-family="monospace" font-size="16">Generated locally from archive data.</text>')
    return ''.join(parts)


def write_media_manifest(entries: list[dict[str, Any]]) -> None:
    records: list[dict[str, Any]] = []
    for entry in entries:
        images = [str(item) for item in entry.get('images') or []]
        records.append(
            {
                'id': entry.get('id'),
                'country': detect_country(entry),
                'year': entry.get('year'),
                'incident_folder': entry.get('incident_folder'),
                'title_en': localize(entry, 'title', 'en'),
                'media_count': len(images),
                'has_generated_snapshot': any(path.endswith('02 - Bilingual Snapshot.svg') for path in images),
                'media_files': images,
            }
        )
    (ROOT / '00 - Media Manifest.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with (ROOT / '00 - Media Manifest.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['id', 'country', 'year', 'incident_folder', 'title_en', 'media_count', 'has_generated_snapshot', 'media_files'])
        writer.writeheader()
        for record in records:
            flat = dict(record)
            flat['media_files'] = ' | '.join(record['media_files'])
            writer.writerow(flat)


def main() -> int:
    database = load_database(ROOT, strict=True)
    entries = database.entries
    write_svg(ROOT / '00 - Project Dashboard.svg', make_project_dashboard(entries))
    by_country: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        by_country[detect_country(entry)].append(entry)
    for country, country_entries in by_country.items():
        write_svg(ROOT / country / '00 - Country Dashboard.svg', make_country_dashboard(country, country_entries))
    write_media_manifest(entries)
    print('Generated project dashboard, country dashboards, and media manifests.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
