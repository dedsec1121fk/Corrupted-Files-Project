#!/usr/bin/env python3
from pathlib import Path
import json, csv

ROOT = Path(__file__).resolve().parents[1]
records = []
for country in ('Greece','USA'):
    cdir = ROOT / country
    if not cdir.exists():
        continue
    for ddir in sorted([p for p in cdir.iterdir() if p.is_dir()]):
        for idir in sorted([p for p in ddir.iterdir() if p.is_dir()]):
            meta = idir / '10 - Metadata.json'
            if meta.exists():
                data = json.loads(meta.read_text(encoding='utf-8'))
                records.append({
                    'country':country,
                    'date_folder':ddir.name,
                    'incident_folder':idir.name,
                    'id':data.get('id',''),
                    'title_en':data.get('title',{}).get('en',''),
                    'title_el':data.get('title',{}).get('el',''),
                    'year':data.get('year',''),
                    'media_count':len(data.get('images') or []),
                })

(ROOT / '00 - Master Incident Index.txt').write_text('\n'.join(f"{r['country']} :: {r['date_folder']} :: {r['incident_folder']} :: {r['id']}" for r in records)+'\n', encoding='utf-8')
(ROOT / '00 - Master Incident Index.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
with (ROOT / '00 - Master Incident Index.csv').open('w', newline='', encoding='utf-8') as f:
    w=csv.writer(f)
    w.writerow(['Country','DateFolder','Year','IncidentFolder','ID','TitleEN','TitleEL','MediaCount'])
    for r in records:
        w.writerow([r['country'],r['date_folder'],r['year'],r['incident_folder'],r['id'],r['title_en'],r['title_el'],r['media_count']])
print(f'Rebuilt indexes for {len(records)} incidents.')
