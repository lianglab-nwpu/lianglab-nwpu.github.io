# Lionel Liang Lab website (Hugo, English)

中文修改指南见 [修改说明.md](修改说明.md)。

Static research-group website built with [Hugo](https://gohugo.io) (v0.140.2 extended; built automatically by GitHub Actions) and a small
self-written theme in `themes/lab/`. **No external resources**: no Google Fonts, no CDNs, no analytics, no maps —
fonts are system font stacks, icons are inline SVG, JS is one tiny local file. It therefore loads equally well in
mainland China and abroad.

## Folder layout
```
hugo.toml               site title, group name, PI name, email, menu
content/_index.md       Home page "About the lab" text
content/research.md     Research page intro text
content/join.md         Join Us (recruiting) page
content/contact.md      Contact page
content/people.md, publications.md, news.md   page titles/subtitles only
data/research.yaml      research directions (title, summary, bullet points, image, representative DOIs)
data/people.yaml        PI bio/CV/projects + student cards
data/news.yaml          news items (newest first)
data/publications.json  publication list (generated, can also be edited by hand)
static/img/             images (pi.png, campus.jpg, hero.svg, research/*.svg placeholders)
scripts/update_pubs.py  refresh publications from ORCID + Crossref
themes/lab/             layouts + CSS (style.css) + JS
.github/workflows/deploy.yml  GitHub Actions: builds with Hugo and publishes to GitHub Pages on every push
```

## Editing content
- **PI welcome note (Home)**: `content/_index.md` → `welcome:` (drafted for the PI to personalise).
- **Life in the Lab photos**: put photos in `static/img/life/` and update `data/life.yaml`.
- **Colours / fonts**: `themes/lab/static/css/style.css` (`:root` variables). Fonts Fredoka (headings) + Source Sans 3 (body) are self-hosted in `themes/lab/static/fonts/` (SIL OFL).
- **Text pages**: edit the Markdown files in `content/`.
- **News**: add an entry at the top of `data/news.yaml` (`date`, `title`, optional `doi`).
- **People**: edit `data/people.yaml`. For a student photo, put `static/img/people/name.jpg` and add `photo: "img/people/name.jpg"` to that member.
- **Research illustrations**: the three pillar images and the framework/hero image (`static/img/research/pillar_*.webp`, `hero_framework.webp`) are AI-generated illustrations made for this site (no publisher figures were used). To swap in your own TOC graphics or figures, export them as JPG/WebP (~1200–1600 px wide, 16:9, <300 KB), put them in `static/img/research/`, and change the `image:` field in `data/research.yaml` (and the hero image in `themes/lab/layouts/index.html`). Only use figures you hold the rights to — journal-published figures are usually copyrighted by the publisher, so use your own original artwork or check the journal's reuse policy.
- **Publications**: `python3 scripts/update_pubs.py` (needs internet), or edit `data/publications.json` directly. The PI's name is bolded automatically.
- **Group name / tagline / email**: `hugo.toml` → `[params]`.

## Offline copy (zip)
`python3 scripts/build_offline.py` builds a version that opens directly from disk (double-click `index.html`) into `Lionel_Liang_Lab_website.zip`.

## Build & preview
```bash
hugo server            # live preview at http://localhost:1313
hugo --minify          # production build into ./public
```
`relativeURLs = true`, so `public/` works from any domain or sub-folder (even opened from disk).

## Deployment options
1. **School server / NWPU homepage system** – ask the network center for a static-hosting directory; upload the contents of `public/` (SFTP/rsync). Best institutional credibility, accessible worldwide.
2. **Hong Kong VPS** (Alibaba Cloud / Tencent Cloud Lighthouse HK, no ICP filing needed):
   ```bash
   sudo apt install nginx
   rsync -avz --delete public/ user@SERVER:/var/www/lab/
   # nginx: server { listen 80; server_name your.domain; root /var/www/lab; index index.html; }
   sudo certbot --nginx -d your.domain   # free HTTPS
   ```
3. **OSS + CDN in mainland China** (Alibaba OSS / Tencent COS static website hosting): requires a domain with ICP filing (1–2 weeks). Upload `public/` with `ossutil cp -r public/ oss://bucket/ --update` (or `coscmd upload -rs public/ /`), set index document `index.html`, bind the CDN domain. Fastest inside China.
4. **GitHub Pages** (free, but can be slow/unstable from mainland China): push this folder to a repo and use the official Hugo GitHub Actions workflow, or push `public/` to a `gh-pages` branch. Good as an overseas mirror.

Tip: host the primary copy on the school server or HK VPS, and optionally mirror on GitHub Pages.
