#!/usr/bin/env python3
"""Refresh data/publications.json from the PI's public ORCID record + Crossref metadata.
Usage: python3 scripts/update_pubs.py   (needs internet; then run `hugo --minify`)"""
import json, re, html, urllib.request
ORCID = "0000-0001-9488-3964"
FIX = {'ACS NANO':'ACS Nano','ADVANCED FUNCTIONAL MATERIALS':'Advanced Functional Materials','MATTER':'Matter',
       'ADVANCED MATERIALS':'Advanced Materials','ADVANCED MATERIALS TECHNOLOGIES':'Advanced Materials Technologies',
       'NANO RESEARCH':'Nano Research','NANO ENERGY':'Nano Energy'}
def get(url, accept='application/json'):
    req = urllib.request.Request(url, headers={'Accept': accept, 'User-Agent': 'labsite/1.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))
# keep hand-added fields (e.g. "image", "image_alt") when refreshing
KEEP = ('image', 'image_alt')
try:
    old = json.load(open('data/publications.json'))
except Exception:
    old = []
def _key(d): return (d.get('doi') or '').lower() or re.sub(r'\W+', '', (d.get('title') or '').lower())
extra = {_key(d): {k: d[k] for k in KEEP if d.get(k)} for d in old}
works = get(f"https://pub.orcid.org/v3.0/{ORCID}/works")
out = []
for g in works['group']:
    s = g['work-summary'][0]
    doi = next((e['external-id-value'].lower() for e in (g.get('external-ids') or {}).get('external-id', [])
                if e['external-id-type'] == 'doi'), None)
    title = s['title']['title']['value']
    journal = (s.get('journal-title') or {}).get('value')
    year = ((s.get('publication-date') or {}).get('year') or {}).get('value')
    authors, vol, pages = [], None, None
    if doi:
        try:
            m = get('https://api.crossref.org/works/' + doi)['message']
            authors = [(a.get('given', '') + ' ' + a.get('family', '')).strip() for a in m.get('author', [])]
            journal = (m.get('container-title') or [journal])[0]
            title = (m.get('title') or [title])[0]
            vol, pages = m.get('volume'), m.get('page') or m.get('article-number')
        except Exception as e:
            print('Crossref failed for', doi, e)
    title = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', title))).replace('\u2010', '-').strip()
    if title.isupper(): title = title.capitalize()
    journal = FIX.get(journal, html.unescape(journal or ''))
    authors = [a.title() if a.isupper() else re.sub(r'\s+', ' ', a) for a in authors]
    out.append(dict(title=title, journal=journal, year=int(year) if year else None, doi=doi,
                    authors=authors, volume=vol, pages=pages))
for d in out:
    d.update(extra.get(_key(d), {}))
out.sort(key=lambda x: -(x['year'] or 0))
json.dump(out, open('data/publications.json', 'w'), ensure_ascii=False, indent=1)
print(len(out), 'publications written')
