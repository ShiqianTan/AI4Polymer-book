#!/usr/bin/env python3
"""Check the newly built full PDF and render pages for CI visual diagnostics."""
from pathlib import Path
import argparse
import json
import re
import fitz

CHAPTERS = list(range(1, 17))
APPENDIX = 90


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    directory = args.directory
    report = json.loads((directory / 'AI4Polymer-Book-build.json').read_text())
    numbers = [n for n in report['chapters'] if n != APPENDIX]
    if numbers != CHAPTERS:
        raise SystemExit(f'Expected all 16 chapters, got {numbers}')
    doc = fitz.open(directory / 'AI4Polymer-Book.pdf')
    if len(doc) < 16:
        raise SystemExit('PDF is unexpectedly short')
    chapter_entries = [r for r in doc.get_toc() if r[0] == 1]
    if len(chapter_entries) < 16:
        raise SystemExit('PDF is missing chapter bookmarks')
    text = ''.join(page.get_text() for page in doc)
    if 'AI4Polymer' not in text or '端到端' not in text or '\ufffd' in text:
        raise SystemExit('PDF text/title/last chapter check failed')
    fatal = [w for w in report['warnings'] if 'Missing character:' in w or 'undefined references' in w]
    if fatal:
        raise SystemExit('Font/reference errors:\n' + '\n'.join(fatal))
    # This repository ships no pinned CJK fonts, so the preamble falls back to
    # system faces (Songti SC + Heiti SC on CI, Songti SC + PingFang HK locally).
    # Check the font families the book needs, not exact PostScript names.
    fonts = sorted({
        span['font']
        for page in doc
        for block in page.get_text('dict')['blocks']
        for line in block.get('lines', [])
        for span in line['spans']
    })

    def has(pattern):
        return any(re.search(pattern, font, re.I) for font in fonts)

    families = {
        'CJK text': r'Songti|SourceHanSans|NotoSansCJK',
        'CJK sans (headings/captions)': r'Heiti|PingFang|SourceHanSans|ArialUnicode|NotoSansCJK',
        'Latin serif': r'LMRoman|LatinModern',
        'Latin sans': r'LMSans|Helvetica',
        'math': r'LatinModernMath|STIX|MSAM',
        'monospace': r'Menlo|DejaVuSansMono',
    }
    missing = [name for name, pattern in families.items() if not has(pattern)]
    if missing:
        raise SystemExit(f'PDF font parity failed: missing families={missing}, fonts={fonts}')
    pages = sorted({0, min(8, len(doc)-1), len(doc)//2, len(doc)-1})
    for number in pages:
        doc[number].get_pixmap(matrix=fitz.Matrix(1, 1)).save(directory / f'preview-{number+1:03}.png')
    result = dict(passed=True, pages=len(doc), chapters=report['chapters'],
                  figures=report['figure_count'], source_ref=report['source_ref'],
                  fonts=fonts, font_families=families,
                  layout_warnings=report['warnings'], preview_pages=[p+1 for p in pages])
    (directory / 'pdf-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(f'PASS: {len(doc)} pages, 16 chapters, readable text, fonts and references')


if __name__ == '__main__':
    main()
