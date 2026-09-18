#!/usr/bin/env python3
"""Verify all generated internal page, fragment and asset links."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1] / 'build/site'
CHAPTERS = 16

class Links(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.ids, self.links = path, set(), []
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])

pages = {p.resolve(): Links(p) for p in ROOT.rglob('*.html')}
errors = []
for path, page in pages.items():
    for link in page.links:
        u = urlsplit(link)
        if u.scheme or u.netloc or u.path.startswith('/'):
            continue
        target = (path.parent / unquote(u.path)).resolve() if u.path else path
        if target.is_dir():
            target /= 'index.html'
        if not target.exists():
            errors.append(f'{path.relative_to(ROOT)}: missing {link}')
        elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:
            errors.append(f'{path.relative_to(ROOT)}: missing anchor {link}')
chapters = [p for p in (ROOT / 'manuscripts').glob('[0-9][0-9]-*.html') if 1 <= int(p.name[:2]) <= CHAPTERS]
if not (ROOT / 'manuscripts/00-前言.html').exists():
    errors.append('Missing preface')
if len(chapters) != CHAPTERS:
    errors.append(f'Expected {CHAPTERS} chapters, got {len(chapters)}')
if not (ROOT / 'search/search_index.json').exists():
    errors.append('Missing search index')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'PASS: {len(pages)} pages, {CHAPTERS} chapters, search index, internal links and images')
