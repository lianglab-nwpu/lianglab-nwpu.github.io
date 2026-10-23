#!/usr/bin/env python3
"""Build an offline (open-from-disk) copy of the site and zip it as Lionel_Liang_Lab_website.zip."""
import os, re, shutil, subprocess, sys, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = '/tmp/lll_offline'; OUT = os.path.join(TMP, 'Lionel_Liang_Lab_website')
shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP)
cfg = os.path.join(TMP, 'offline.toml')
open(cfg, 'w').write('baseURL = "/"\nrelativeURLs = true\nuglyURLs = true\n')
subprocess.run(['hugo', '--minify', '--source', ROOT, '--config', os.path.join(ROOT, 'hugo.toml') + ',' + cfg,
                '--destination', OUT], check=True)
pages = {os.path.splitext(f)[0] for f in os.listdir(OUT) if f.endswith('.html')}
def fix(m):
    attr, q, url = m.group(1), m.group(2), m.group(3)
    if re.match(r'^(https?:|mailto:|#|data:)', url): return m.group(0)
    u = url
    mm = re.match(r'^(\.{1,2}/|/)?([A-Za-z0-9_-]*)/?(#.*)?$', u)
    if mm and (mm.group(2) == '' or mm.group(2) in pages) and not re.search(r'\.\w+(#|$)', u):
        name = mm.group(2) or 'index'; frag = mm.group(3) or ''
        u = './' + name + '.html' + frag
    return f'{attr}={q}{u}{q}'
for f in os.listdir(OUT):
    if f.endswith('.html'):
        p = os.path.join(OUT, f); s = open(p, encoding='utf-8').read()
        s = re.sub(r'(href)=(["\']?)([^"\'\s>]+)\2', fix, s)
        s = re.sub(r"url\(('|\"|&#39;)?/(?!/)", lambda m: 'url(' + (m.group(1) or '') + './', s)
        open(p, 'w', encoding='utf-8').write(s)
# verify links
bad = []
for f in os.listdir(OUT):
    if not f.endswith('.html'): continue
    s = open(os.path.join(OUT, f), encoding='utf-8').read()
    for url in re.findall(r'(?:href|src)=["\']?([^"\'\s>]+)', s) + re.findall(r"url\('?([^')]+)'?\)", s):
        url = html.unescape(url)
        if re.match(r'^(https?:|mailto:|#|data:)', url): continue
        path = url.split('#')[0]
        if not path: continue
        if not os.path.exists(os.path.normpath(os.path.join(OUT, path))): bad.append((f, url))
css = open(os.path.join(OUT, 'css/style.css')).read()
for url in re.findall(r'url\(([^)]+)\)', css):
    if not os.path.exists(os.path.normpath(os.path.join(OUT, 'css', url.strip('"\'')))): bad.append(('style.css', url))
print('broken links:', bad if bad else 'none')
zp = os.path.join(ROOT, 'Lionel_Liang_Lab_website')
if os.path.exists(zp + '.zip'): os.remove(zp + '.zip')
shutil.make_archive(zp, 'zip', TMP, 'Lionel_Liang_Lab_website')
print('zip:', zp + '.zip', os.path.getsize(zp + '.zip') // 1024, 'KB')
sys.exit(1 if bad else 0)
