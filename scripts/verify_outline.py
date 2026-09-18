#!/usr/bin/env python3
"""Check the outline structure, anchors, and reference links."""
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit
import csv
import hashlib
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUTLINES = ROOT / 'archive/outlines'
REVISION = ROOT / 'research/outline-revision-2026-09-16'
errors = []
warnings = []
PLANNED = ('manuscripts/', 'experiments/', 'calculations/', 'case-studies/')


def check(condition, message):
    if not condition:
        errors.append(message)


def anchors(path):
    text = path.read_text()
    found = re.findall(r'\bid=["\']([^"\']+)', text)
    if path.suffix == '.md':
        seen = Counter()
        for heading in re.findall(r'^#{1,6} (.+)', text, re.M):
            heading = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', heading)
            heading = re.sub(r'<[^>]+>', '', heading)
            slug = re.sub(r'[^\w\-\s]', '', heading.lower(), flags=re.U).replace(' ', '-')
            count = seen[slug]
            seen[slug] += 1
            found.append(slug + (f'-{count}' if count else ''))
    return set(found)


catalog = json.loads((OUTLINES / 'chapters.json').read_text())
check([c['number'] for c in catalog] == list(range(1, len(catalog) + 1)), 'Chapter catalog order')
check({c['file'] for c in catalog} == {p.name for p in OUTLINES.glob('[0-9][0-9]-*.md')}, 'Chapter file set')
counts = Counter()
all_labs, all_figures, all_sections = set(), set(), set()

for c in catalog:
    n = c['number']
    p = OUTLINES / c['file']
    s = p.read_text()
    check(s.startswith(f'# 第 {n} 章 {c["title"]}\n'), f'{p.name}: title')
    check(all(0 < prior < n for prior in c['prerequisites']), f'{p.name}: forward prerequisite')
    for label in ['本章判断', '前置与交付', '阅读安排', '## 本章的设计决定', '## 写作资料']:
        check(label in s, f'{p.name}: missing {label}')
    sections = re.findall(r'^## (\d+\.\d+) ', s, re.M)
    check(sections == [f'{n}.{i}' for i in range(1, len(sections) + 1)], f'{p.name}: section numbering')
    subs = []
    for sec in sections:
        found = re.findall(r'^### (' + re.escape(sec) + r'\.\d+) ', s, re.M)
        check(found == [f'{sec}.{i}' for i in range(1, len(found) + 1)], f'{p.name}: subsection numbering {sec}')
        subs.extend(found)
    all_sections.update(sections + subs)
    for word, key, target in [('实验', 'experiments', all_labs), ('图', 'figures', all_figures)]:
        ids = re.findall(r'^> \*\*' + word + r' (\d+-\d+)', s, re.M)
        check(ids == [f'{n}-{i}' for i in range(1, len(ids) + 1)], f'{p.name}: {word} order')
        target.update(ids)
        counts[key] += len(ids)
    cores = re.findall(r'^> \*\*实验 (\d+-\d+)[^\n]*〔核心〕', s, re.M)
    check(sorted(cores) == sorted(c['core_experiments']) and len(cores) == 3, f'{p.name}: core selection')
    check(len(re.findall(r'^> \*\*实验 [^\n]*〔(?:核心|延伸)〕', s, re.M)) == len(re.findall(r'^> \*\*实验 ', s, re.M)),
          f'{p.name}: lab classification')
    counts.update(sections=len(sections), subsections=len(subs), core=len(cores))
    companion = OUTLINES / 'extensions' / c['file']
    check(companion.exists(), f'{p.name}: companion')
    if companion.exists():
        text = companion.read_text()
        for sec in sections + subs:
            check(f'id="detail-{sec}"' in text, f'{p.name}: companion anchor {sec}')

for c in catalog:
    companion_text = (OUTLINES / 'extensions' / c['file']).read_text()
    for key, word, target in [('supplementary_experiments', '实验', all_labs), ('supplementary_figures', '图', all_figures)]:
        for identifier in c.get(key, []):
            check(identifier not in target, f'Duplicate body/supplement identifier: {identifier}')
            check(re.search(r'^> \*\*' + word + ' ' + re.escape(identifier) + r'\b', companion_text, re.M),
                  f'Missing supplementary {word}: {identifier}')
            target.add(identifier)

for p in OUTLINES.glob('[0-9][0-9]-*.md'):
    text = p.read_text()
    for word, valid in [('实验', all_labs), ('图', all_figures)]:
        for identifier in re.findall(word + r' (\d+-\d+)', text):
            check(identifier in valid, f'{p.name}: undefined {word} {identifier}')

active = [ROOT / 'README.md', *OUTLINES.rglob('*.md'), ROOT / 'references/README.md']
anchor_cache = {}
link_count = 0
for p in active:
    if not p.exists():
        continue
    s = p.read_text()
    urls = re.findall(r'\]\(([^)]+)\)', s)
    for url in urls:
        url = html.unescape(url).strip('<>')
        if re.match(r'\w+:|//', url):
            continue
        parts = urlsplit(url)
        target = (p.parent / unquote(parts.path)).resolve() if parts.path else p
        link_count += 1
        rel = None
        try:
            rel = str(target.relative_to(ROOT))
        except ValueError:
            pass
        if not target.exists():
            if rel and rel.startswith(PLANNED):
                warnings.append(f'{p.relative_to(ROOT)}: planned link {url}')
            else:
                errors.append(f'{p.relative_to(ROOT)}: missing link {url}')
        elif parts.fragment and target.suffix in ('.md', '.html'):
            if target not in anchor_cache:
                anchor_cache[target] = anchors(target)
            check(unquote(parts.fragment) in anchor_cache[target], f'{p.relative_to(ROOT)}: missing anchor {url}')

sources = ROOT / 'references/sources.tsv'
manifest = ROOT / 'references/manifest.json'
hash_count = 0
if sources.exists() and manifest.exists():
    with sources.open() as f:
        catalog_sources = {r['id']: [int(n) for n in r['chapters'].split(',')] for r in csv.DictReader(f, delimiter='\t')}
    for source in json.loads(manifest.read_text()):
        if source['id'] in catalog_sources:
            check(source['chapters'] == catalog_sources[source['id']], f'Catalog mismatch {source["id"]}')
        if source.get('file') and source.get('sha256'):
            fp = ROOT / 'references' / source['file']
            if fp.exists():
                check(hashlib.sha256(fp.read_bytes()).hexdigest() == source['sha256'], f'Source changed {fp}')
                hash_count += 1

report = dict(status='passed' if not errors else 'failed', chapters=len(catalog), **counts,
              local_links_checked=link_count, reference_hashes_checked=hash_count,
              planned_links=len(warnings), errors=errors, warnings=warnings)
REVISION.mkdir(parents=True, exist_ok=True)
(REVISION / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'warnings'}, ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))
