#!/usr/bin/env python3
"""Sync the chapter index in archive/outlines/README.md and the source map."""
from pathlib import Path
import csv
import html
import json
import re
from urllib.parse import quote

R = Path(__file__).resolve().parents[1]
O = R / 'archive/outlines'

catalog = json.loads((O / 'chapters.json').read_text())
assert [c['number'] for c in catalog] == list(range(1, len(catalog) + 1)), 'chapter numbering'
assert {c['file'] for c in catalog} == {p.name for p in O.glob('[0-9][0-9]-*.md')}, 'chapter file set'

chapters = []
for entry in catalog:
    p = O / entry['file']
    s = p.read_text()
    s = re.sub(r'([^\n])\n(#{2,3} )', r'\1\n\n\2', s)
    p.write_text(s)
    n = int(p.name[:2])
    secs = []
    for m in re.finditer(r'^## (\d+\.\d+) ([^\n]+)\n(.*?)(?=^## |\Z)', s, re.M | re.S):
        body = m[3]
        subs = [dict(num=x[1], title=x[2], body=x[3].strip())
                for x in re.finditer(r'^### (\d+\.\d+\.\d+) ([^\n]+)\n(.*?)(?=^### |\Z)', body, re.M | re.S)]
        secs.append(dict(num=m[1], title=m[2], intro=body.split('### ', 1)[0].strip(), subs=subs))
    title = s.splitlines()[0].split('章 ', 1)[1]
    assert title == entry['title'] and n == entry['number'], (p.name, title)
    core = re.findall(r'^> \*\*实验 (\d+-\d+)[^\n]*〔核心〕', s, re.M)
    assert sorted(core) == sorted(entry['core_experiments']) and len(core) == 3, (p.name, core)
    chapters.append(dict(n=n, path=p, title=title, sections=secs,
                         subcount=sum(len(x['subs']) for x in secs),
                         labs=len(re.findall(r'^> \*\*实验 ', s, re.M)),
                         figs=len(re.findall(r'^> \*\*图 ', s, re.M))))

counts = dict(sections=sum(len(c['sections']) for c in chapters),
              subsections=sum(c['subcount'] for c in chapters),
              experiments=sum(c['labs'] for c in chapters),
              figures=sum(c['figs'] for c in chapters))
summary = (f'共 {len(chapters)} 章、{counts["sections"]} 节、{counts["subsections"]} 个小节、'
           f'{counts["experiments"]} 项实验与计算、{counts["figures"]} 项配图计划')

readme = O / 'README.md'
s = readme.read_text()
entries = '\n'.join(f'{c["n"]}. [{c["title"]}]({quote(c["path"].name)}): '
                    f'{next(e["summary"] for e in catalog if e["number"] == c["n"])}'
                    for c in chapters)
s = re.sub(r'<!-- CHAPTERS:START -->.*?<!-- CHAPTERS:END -->',
           '<!-- CHAPTERS:START -->\n' + entries + '\n<!-- CHAPTERS:END -->', s, flags=re.S)
s = re.sub(r'共 \d+ 章、\d+ 节、\d+ 个小节、\d+ 项实验与计算、\d+ 项配图计划', summary, s)
readme.write_text(s)

# Source map: one row per archived source, marked by the chapters whose outline cites it.
sources = R / 'references/sources.tsv'
source_map = O / 'source-map.md'
if sources.exists() and source_map.exists():
    rows = list(csv.DictReader(sources.open(), delimiter='\t'))
    body = ['# 来源落点', '', '本表由 `scripts/render_outline.py` 生成：列出归档来源及其在大纲中的使用章节。', '',
            '| 来源 | 标题 | 类别 | 使用章节 | 说明 |', '| --- | --- | --- | --- | --- |']
    for row in rows:
        body.append(f'| `{row["id"]}` | {row["title"]} | {row["category"]} | {row["chapters"]} | {row["note"]} |')
    source_map.write_text('\n'.join(body) + '\n')

print(summary)
