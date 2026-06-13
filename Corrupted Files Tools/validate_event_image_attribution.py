#!/usr/bin/env python3
"""Validate event-image attribution records and file checksums."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / '00 - Event Image Attribution.json'
IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.webp'}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    errors: list[str] = []
    if not MANIFEST.is_file():
        print('ERROR: missing attribution manifest')
        return 1

    payload = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if not isinstance(payload, list):
        print('ERROR: attribution manifest is not a list')
        return 1

    actual = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob('*Event Image*')
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    }
    tracked: set[str] = set()

    for index, item in enumerate(payload, 1):
        if not isinstance(item, dict):
            errors.append(f'Row {index}: not an object')
            continue
        rel = str(item.get('file') or '')
        if not rel:
            errors.append(f'Row {index}: missing file path')
            continue
        if rel in tracked:
            errors.append(f'Duplicate manifest path: {rel}')
        tracked.add(rel)
        path = ROOT / rel
        if not path.is_file():
            errors.append(f'Missing attributed image: {rel}')
            continue
        if item.get('rights_status') != 'verified':
            errors.append(f'Unverified rights status: {rel}')
        for field in ('source_page', 'source_file', 'author', 'license'):
            if not str(item.get(field) or '').strip():
                errors.append(f'Missing {field}: {rel}')
        expected_hash = str(item.get('sha256') or '')
        actual_hash = sha256(path)
        if expected_hash != actual_hash:
            errors.append(f'Checksum mismatch: {rel}')
        if int(item.get('size_bytes') or 0) != path.stat().st_size:
            errors.append(f'File-size mismatch: {rel}')

    for rel in sorted(actual - tracked):
        errors.append(f'Untracked event image: {rel}')
    for rel in sorted(tracked - actual):
        errors.append(f'Manifest points to non-event image or missing file: {rel}')

    print(f'Event image files: {len(actual)}')
    print(f'Attribution records: {len(payload)}')
    print(f'Errors: {len(errors)}')
    for error in errors:
        print(f'ERROR: {error}')
    if errors:
        return 1
    print('Event-image attribution validation: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
