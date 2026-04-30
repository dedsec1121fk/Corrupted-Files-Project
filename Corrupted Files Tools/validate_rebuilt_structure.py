#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DB_DIR = ROOT / 'Corrupted Files Database'

def fail(msg):
    raise SystemExit(msg)

required_root = [
    'Greece',
    'USA',
    '00 - Master Incident Index.txt',
    '00 - Master Incident Index.json',
    '00 - Master Incident Index.csv',
    '00 - Dates by Country.txt',
    '00 - Statistics.txt',
    'README.md',
    'Corrupted Files.py',
]
for name in required_root:
    if not (ROOT / name).exists():
        fail(f'Missing root item: {name}')

for name in ['Corrupted Files Library','Corrupted Files Media','Corrupted Files Docs','Corrupted Files Updates','__pycache__']:
    if (ROOT / name).exists():
        fail(f'Old folder still exists: {name}')

db_files = sorted(DB_DIR.glob('Database Shard *.json'))
if not db_files:
    fail('No rebuilt database shards found.')
entries=[]
media_refs=0
for db in db_files:
    payload = json.loads(db.read_text(encoding='utf-8'))
    for e in payload.get('entries',[]):
        entries.append(e)
        for img in e.get('images') or []:
            media_refs += 1
            if not (ROOT / img).exists():
                fail(f'Missing media file referenced in database: {img}')

manifest = json.loads((DB_DIR/'manifest.json').read_text(encoding='utf-8'))
if manifest.get('records') != len(entries):
    fail(f"Manifest record mismatch: {manifest.get('records')} != {len(entries)}")
if manifest.get('media_references') != media_refs:
    fail(f"Manifest media mismatch: {manifest.get('media_references')} != {media_refs}")

print(f'OK: {len(entries)} incidents, {len(db_files)} database shards, {media_refs} media references. Structure looks good.')
