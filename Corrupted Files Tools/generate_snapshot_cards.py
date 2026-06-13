#!/usr/bin/env python3
"""Generate original SVG snapshot cards for incident folders that only have one media image.

The cards are informational visuals derived from the project's own text files.
No external copyrighted photographs are copied.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from corrupted_files_core import (  # noqa: E402
    discover_incidents,
    localize,
    media_paths_for_incident,
    translation_status,
    source_trail_status,
)

WIDTH = 1600
HEIGHT = 900
BG = '#0b0b0f'
PANEL = '#11131a'
PURPLE = '#b78cff'
TEAL = '#8affc1'
WHITE = '#f5f7fb'
MUTED = '#9aa4b2'
ACCENT = '#1a1e29'
WARNING = '#ffcf70'


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--apply', action='store_true', help='write files instead of previewing only')
    p.add_argument('--limit', type=int, default=0, help='optional limit for testing')
    return p


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", ' ', text.replace('\xa0', ' ')).strip()


def extract_between(text: str, start_markers: list[str], end_markers: list[str]) -> str:
    lower = text.lower()
    start = -1
    matched_marker = ''
    for marker in start_markers:
        idx = lower.find(marker.lower())
        if idx != -1 and (start == -1 or idx < start):
            start = idx
            matched_marker = marker
    if start == -1:
        return ''
    start += len(matched_marker)
    segment = text[start:]
    seg_lower = segment.lower()
    end_positions = []
    for marker in end_markers:
        idx = seg_lower.find(marker.lower())
        if idx != -1:
            end_positions.append(idx)
    if end_positions:
        segment = segment[:min(end_positions)]
    return normalize_spaces(segment.strip(" :=-\n\t"))


def extract_summary(incident_dir: Path, lang: str) -> str:
    filename = '00A - Summary EN.txt' if lang == 'en' else '00B - Summary EL.txt'
    path = incident_dir / filename
    if not path.is_file():
        filename = '01 - Article EN.txt' if lang == 'en' else '02 - Article EL.txt'
        path = incident_dir / filename
    try:
        text = path.read_text(encoding='utf-8')
    except OSError:
        return ''
    section = extract_between(
        text,
        ['Core story', 'Κεντρική ιστορία'],
        ['What happened', 'Τι συνέβη', 'Timeline', 'Χρονολόγιο', 'Key facts', 'Γιατί αυτή η υπόθεση'],
    )
    if not section:
        section = normalize_spaces(text[:700])
    section = re.sub(r'^(=|\-|\s)+', '', section).strip()
    if lang == 'el':
        section = section.replace('Η υπόθεση αφορά:', '').replace('Πλήρες πλαίσιο:', '').strip()
    if len(section) > 460:
        section = section[:460].rstrip(' .') + '…'
    return section


def extract_timeline(incident_dir: Path) -> list[str]:
    candidates = [incident_dir / '00A - Summary EN.txt', incident_dir / '01 - Article EN.txt']
    text = ''
    for path in candidates:
        if path.is_file():
            try:
                text = path.read_text(encoding='utf-8')
                break
            except OSError:
                pass
    if not text:
        return []
    chunk = extract_between(
        text,
        ['Timeline', 'Χρονολόγιο'],
        ['Key facts', 'Why this case matters', 'Competing explanations', 'Source trail', 'V21'],
    )
    if not chunk:
        return []
    chunk = chunk.replace(' - ', '\n- ')
    bullets = []
    for piece in chunk.splitlines():
        piece = normalize_spaces(piece)
        if not piece:
            continue
        if piece.startswith('- '):
            item = piece[2:].strip()
            if item:
                bullets.append(item)
        elif re.match(r'^[0-9]{4}:', piece):
            bullets.append(piece)
        if len(bullets) >= 4:
            break
    return bullets[:4]


def wrap_text(text: str, width: int) -> list[str]:
    if not text:
        return ['—']
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)


def svg_text_lines(x: int, y: int, lines: list[str], size: int, color: str, *, line_height: float = 1.35, weight: str = '400') -> tuple[str, int]:
    parts = []
    current_y = y
    step = int(size * line_height)
    for line in lines:
        parts.append(
            f'<text x="{x}" y="{current_y}" fill="{color}" font-family="monospace" font-size="{size}" font-weight="{weight}">{html.escape(line)}</text>'
        )
        current_y += step
    return ''.join(parts), current_y


def safe_el_text(entry: dict, fallback_en: str, field: str) -> str:
    quality = translation_status(entry)
    status = quality['fields'].get(field, '')
    value = localize(entry, field, 'el').strip()
    if field == 'article':
        if status in {'partial-greek', 'same-as-english', 'missing'}:
            return 'Το ελληνικό κείμενο χρειάζεται ακόμη έλεγχο. Χρησιμοποίησε προσωρινά την αγγλική ενότητα ή το πλήρες άρθρο μέχρι να γίνει καθαρότερη ελληνική επιμέλεια.'
    elif status in {'same-as-english', 'missing'}:
        return f'{fallback_en} [EL review needed]'
    return value or fallback_en


def make_card(
    title_en: str,
    title_el: str,
    country_en: str,
    country_el: str,
    year: str,
    category_en: str,
    category_el: str,
    evidence_en: str,
    evidence_el: str,
    summary_en: str,
    summary_el: str,
    timeline: list[str],
    incident_id: str,
    quality_badge: str,
) -> str:
    title_en_lines = wrap_text(title_en, 34)
    title_el_lines = wrap_text(title_el, 36)
    summary_en_lines = wrap_text(summary_en, 46)[:8]
    summary_el_lines = wrap_text(summary_el, 46)[:8]
    timeline = timeline or ['No timeline points were extracted automatically.']
    timeline_lines: list[str] = []
    for item in timeline[:4]:
        timeline_lines.extend(wrap_text('• ' + item, 62))

    chunks: list[str] = []
    chunks.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">')
    chunks.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}"/>')
    chunks.append(f'<rect x="32" y="32" width="{WIDTH-64}" height="{HEIGHT-64}" rx="20" fill="none" stroke="{PURPLE}" stroke-width="4"/>')
    chunks.append(f'<rect x="60" y="60" width="{WIDTH-120}" height="{HEIGHT-120}" rx="18" fill="{PANEL}" stroke="{TEAL}" stroke-width="2"/>')
    chunks.append(f'<text x="92" y="118" fill="{PURPLE}" font-family="monospace" font-size="26" font-weight="700">CASE SNAPSHOT / ΣΤΙΓΜΙΟΤΥΠΟ ΥΠΟΘΕΣΗΣ</text>')
    chunks.append(f'<text x="92" y="168" fill="{WHITE}" font-family="monospace" font-size="72" font-weight="700">{html.escape(str(year))}</text>')
    chunks.append(f'<rect x="1290" y="82" width="190" height="34" rx="12" fill="{ACCENT}" stroke="{WARNING}" stroke-width="1.5"/>')
    chunks.append(f'<text x="1304" y="104" fill="{WARNING}" font-family="monospace" font-size="16">{html.escape(quality_badge)}</text>')

    badges = [
        f'Country: {country_en} / {country_el}',
        f'Category: {category_en} / {category_el}',
        f'Evidence: {evidence_en} / {evidence_el}',
    ]
    bx = 470
    by = 126
    widths = [720, 1000, 1000]
    strokes = [PURPLE, PURPLE, TEAL]
    for idx, badge in enumerate(badges):
        y = by + idx * 40
        chunks.append(f'<rect x="{bx}" y="{y-24}" width="{widths[idx]}" height="30" rx="12" fill="{ACCENT}" stroke="{strokes[idx]}" stroke-width="1.5"/>')
        chunks.append(f'<text x="{bx+14}" y="{y-2}" fill="{WHITE}" font-family="monospace" font-size="18">{html.escape(badge[:150])}</text>')

    chunks.append(f'<rect x="92" y="205" width="670" height="150" rx="14" fill="#0d1016" stroke="{PURPLE}" stroke-width="1.5"/>')
    chunks.append(f'<rect x="838" y="205" width="670" height="150" rx="14" fill="#0d1016" stroke="{TEAL}" stroke-width="1.5"/>')
    chunks.append(f'<text x="116" y="240" fill="{MUTED}" font-family="monospace" font-size="20">EN TITLE</text>')
    chunks.append(f'<text x="862" y="240" fill="{MUTED}" font-family="monospace" font-size="20">ΤΙΤΛΟΣ EL</text>')
    part, _ = svg_text_lines(116, 285, title_en_lines[:3], 30, WHITE, line_height=1.25, weight='700')
    chunks.append(part)
    part, _ = svg_text_lines(862, 285, title_el_lines[:3], 28, WHITE, line_height=1.25, weight='700')
    chunks.append(part)

    chunks.append(f'<rect x="92" y="385" width="670" height="308" rx="14" fill="#0d1016" stroke="#394255" stroke-width="1.5"/>')
    chunks.append(f'<rect x="838" y="385" width="670" height="308" rx="14" fill="#0d1016" stroke="#394255" stroke-width="1.5"/>')
    chunks.append(f'<text x="116" y="420" fill="{PURPLE}" font-family="monospace" font-size="22" font-weight="700">EN SUMMARY</text>')
    chunks.append(f'<text x="862" y="420" fill="{TEAL}" font-family="monospace" font-size="22" font-weight="700">ΣΥΝΟΨΗ EL</text>')
    part, _ = svg_text_lines(116, 460, summary_en_lines, 22, WHITE, line_height=1.4)
    chunks.append(part)
    part, _ = svg_text_lines(862, 460, summary_el_lines, 22, WHITE, line_height=1.4)
    chunks.append(part)

    chunks.append(f'<rect x="92" y="722" width="1416" height="120" rx="14" fill="#0d1016" stroke="{PURPLE}" stroke-width="1.5"/>')
    chunks.append(f'<text x="116" y="756" fill="{WHITE}" font-family="monospace" font-size="22" font-weight="700">TIMELINE / ΧΡΟΝΟΛΟΓΙΟ</text>')
    part, _ = svg_text_lines(116, 792, timeline_lines[:3], 19, TEAL, line_height=1.3)
    chunks.append(part)

    chunks.append(f'<text x="92" y="874" fill="{MUTED}" font-family="monospace" font-size="16">Generated from project text for offline reference. No external copyrighted news image copied. ID: {html.escape(incident_id)}</text>')
    chunks.append('</svg>')
    return ''.join(chunks)


def main() -> int:
    args = parser().parse_args()
    incidents, errors = discover_incidents(ROOT)
    if errors:
        raise SystemExit('\n'.join(errors))

    targets = []
    for incident_id, incident in incidents.items():
        media = media_paths_for_incident(ROOT, incident)
        # Regenerate only folders that originally needed extra image help,
        # but also overwrite existing snapshot cards when they are already present.
        if len(media) == 1 or (incident.path / 'Media' / '02 - Bilingual Snapshot.svg').exists():
            targets.append((incident_id, incident))
    if args.limit > 0:
        targets = targets[:args.limit]

    created = 0
    for incident_id, incident in targets:
        out = incident.path / 'Media' / '02 - Bilingual Snapshot.svg'
        title_en = localize(incident.full_record, 'title', 'en') or incident.path.name
        title_el = safe_el_text(incident.full_record, title_en, 'title')
        country_en = localize(incident.full_record, 'country', 'en') or incident.path.parts[0]
        country_el = localize(incident.full_record, 'country', 'el') or country_en
        year = str(incident.full_record.get('year') or incident.path.parent.name[-4:])
        category_en = localize(incident.full_record, 'category', 'en') or 'unknown'
        category_el = safe_el_text(incident.full_record, category_en, 'category')
        evidence_en = localize(incident.full_record, 'evidence_level', 'en') or 'unspecified'
        evidence_el = safe_el_text(incident.full_record, evidence_en, 'evidence_level')
        summary_en = extract_summary(incident.path, 'en')
        summary_el = extract_summary(incident.path, 'el')
        article_quality = translation_status(incident.full_record)['fields'].get('article', '')
        if article_quality in {'partial-greek', 'same-as-english', 'missing'} or not summary_el:
            summary_el = safe_el_text(incident.full_record, summary_en, 'article')
        timeline = extract_timeline(incident.path)
        t_quality = translation_status(incident.full_record)['overall']
        s_quality = source_trail_status(incident.full_record)['level']
        quality_badge = f'TR {t_quality} | SRC {s_quality}'
        svg = make_card(
            title_en,
            title_el,
            country_en,
            country_el,
            year,
            category_en,
            category_el,
            evidence_en,
            evidence_el,
            summary_en,
            summary_el,
            timeline,
            incident_id,
            quality_badge,
        )
        if args.apply:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(svg, encoding='utf-8')
        created += 1

    mode = 'Created' if args.apply else 'Would create'
    print(f'{mode} {created} snapshot card(s).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
