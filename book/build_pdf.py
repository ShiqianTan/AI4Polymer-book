#!/usr/bin/env python3
"""Build ElegantBook PDFs from the canonical manuscripts (Pandoc + XeLaTeX)."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MANUSCRIPTS = ROOT / 'manuscripts'
OUTLINES = ROOT / 'archive/outlines'
REPO = 'ShiqianTan/AI4Polymer-book'
BOOK_TITLE = 'AI4Polymer：人工智能驱动的高分子材料设计'
BOOK_AUTHOR = 'Shiqian Tan'
CHAPTER_NUMBERS = range(1, 17)


def run(command, *, cwd=HERE, log=None):
    if log:
        with log.open('w') as stream:
            result = subprocess.run(command, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT)
        if result.returncode:
            raise SystemExit(f'Build failed; see {log}\n' + log.read_text(errors='replace')[-6000:])
    else:
        subprocess.run(command, cwd=cwd, check=True)


def chapter_source(number, base=MANUSCRIPTS):
    matches = sorted(base.glob(f'{number:02}-*.md'))
    if not matches:
        raise FileNotFoundError(
            f'Missing manuscript for chapter {number}: expected {base}/{number:02}-*.md')
    return matches[0]


def strip_outline_scaffolding(text):
    """Turn an archived outline into readable prose for the preview PDF.

    The outline keeps editorial fields (judgement, prerequisites, reading plan),
    a design ledger and a source map. None of that belongs in the delivered book,
    so the preview build removes it and promotes figure notes into numbered
    captions. The outline files themselves stay the complete editorial source.
    """
    text = re.sub(r'^> 写作大纲 · [^\n]*\n', '', text, flags=re.M)
    text = re.sub(r'^开篇安排：[^\n]*\n', '', text, flags=re.M)
    for label in ('本章判断', '前置与交付', '阅读安排'):
        text = re.sub(rf'^\*\*{label}：\*\*[^\n]*\n', '', text, flags=re.M)
    for heading in ('本章的设计决定', '写作资料'):
        text = re.sub(rf'^## {heading}\n.*?(?=^## |\Z)', '', text, flags=re.M | re.S)

    def figure(match):
        number, title, body, path = match.group(1), match.group(2).strip(), match.group(3), match.group(4)
        notes = []
        for line in body.splitlines():
            line = re.sub(r'^>\s?', '', line).strip()
            if line and not line.startswith('已制作：'):
                notes.append(line)
        desc = ' '.join(notes)
        desc = re.sub(r'[^。]*见提纲。', '', desc).strip()
        caption = re.sub(r'。+$', '。', f'图 {number}　{title}。{desc}')
        return f'![{caption}]({path})'
    text = re.sub(r'^> \*\*图 ([\d-]+)：([^\n]+?)（已配正文图）\*\*\n((?:>[^\n]*\n)+)\n+!\[[^\n]*\]\(([^)]+)\)',
                  figure, text, flags=re.M)

    text = re.sub(r'^> \*\*实验 ([\d-]+) ★〔(核心|延伸)〕：',
                  lambda m: f'> **练习 {m.group(1)}〔{m.group(2)}〕：', text, flags=re.M)
    text = re.sub(r'(?:^> *\n)*^> \*\*记录结果（[^）]+）：\*\*[^\n]*\n', '', text, flags=re.M)
    return re.sub(r'\n{3,}', '\n\n', text)


def prepare(source, dest, assets, source_ref=None, strict=True, outline=False):
    text = source.read_text()
    number = int(source.name[:2])
    if outline:
        text = strip_outline_scaffolding(text)
    if number == 0:
        text = re.sub(r'^# 前言$', '# 前言 {.unnumbered}', text, flags=re.M)
        text = re.sub(r'^(## .+)$', r'\1 {.unnumbered}', text, flags=re.M)
    if number == 90:
        text = re.sub(r'^# 附录$', '# 附录 {.unnumbered}', text, flags=re.M)
        text = re.sub(r'^(## .+)$', r'\1 {.unnumbered}', text, flags=re.M)
    text = re.sub(r'^# 第\s*\d+\s*章\s*(.*)$', rf'# \1 {{#chapter-{number}}}', text, flags=re.M)
    text = re.sub(r'<a id="([^"]+)"></a>\s*\n+(#{1,6} [^\n]+)',
                  lambda m: m[2]+' {#'+m[1]+'}', text)
    # Manuscripts repeat image alt text as the following italic caption. Merge them.
    text = re.sub(r'!\[[^\n]*\]\(([^)]+)\)\s*\n\s*\*([^\n]+)\*',
                  lambda m: f'![{m[2]}]({m[1]})', text)

    def image(match):
        original = (source.parent / match[2]).resolve()
        selected = original.with_suffix('.pdf') if original.with_suffix('.pdf').exists() else original.with_suffix('.png')
        if not selected.exists():
            if not strict:
                return ''
            raise FileNotFoundError(original)
        if selected.read_bytes().startswith(b'version https://git-lfs.github.com/spec/v1'):
            raise ValueError(f'Figure is an LFS pointer; run git lfs pull: {selected}')
        assets.append(selected)
        return f'![{match[1]}]({selected.as_posix()})'
    text = re.sub(r'!\[([^\n]*)\]\(([^)]+)\)', image, text)
    # Prefix ordinary links with their real relative location from the delivered PDF.
    def link(match):
        target = match[2]
        if re.match(r'[a-z]+:|#', target):
            return match[0]
        from urllib.parse import unquote
        resolved = (source.parent / unquote(target.split('#')[0])).resolve()
        if resolved.is_relative_to(ROOT):
            fragment = '#' + target.split('#',1)[1] if '#' in target else ''
            relative = resolved.relative_to(ROOT).as_posix()
            if source_ref:
                from urllib.parse import quote
                return f'[{match[1]}](https://github.com/{REPO}/blob/{quote(source_ref, safe="")}/{quote(relative, safe="/")}{fragment})'
            return f'[{match[1]}](../{relative}{fragment})'
        return match[0]
    text = re.sub(r'(?<!!)\[([^\]]*)\]\(([^)]+)\)', link, text)
    dest.write_text(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chapter', type=int, choices=CHAPTER_NUMBERS,
                        help='Build one chapter with its original chapter number')
    parser.add_argument('--output-dir', type=Path, default=HERE, help='Output directory relative to book/ (default: book/)')
    parser.add_argument('--source-ref', help='Git commit for portable GitHub links in released PDFs')
    parser.add_argument('--from-outline', action='store_true',
                        help='Preview the archived outline (archive/outlines) instead of the manuscript')
    args = parser.parse_args()
    output_dir = (HERE / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    strict = not args.from_outline
    base = OUTLINES if args.from_outline else MANUSCRIPTS
    name = f'AI4Polymer-Book-Chapter-{args.chapter:02}' if args.chapter else 'AI4Polymer-Book'
    if args.from_outline:
        name += '-Outline'
    work = HERE / 'build' / name
    work.mkdir(parents=True, exist_ok=True)
    numbers = [args.chapter] if args.chapter else CHAPTER_NUMBERS
    sources = [chapter_source(n, base) for n in numbers]
    appendix = MANUSCRIPTS / '90-附录.md'
    if not args.chapter and not args.from_outline and appendix.is_file():
        sources.append(appendix)
    inputs, assets = [], []
    for source in sources:
        target = work / source.name
        prepare(source,target,assets,args.source_ref,strict=strict,outline=args.from_outline)
        inputs.append(target)
    before = work / 'frontmatter.tex'
    if args.from_outline:
        edition = '提纲样张'
    else:
        edition = f'第 {args.chapter} 章排版样张' if args.chapter else 'v1.0'
    before.write_text('\\renewcommand{\\BookEdition}{'+edition+'}\n\\input{cover.tex}\n'
                     '\\pagenumbering{Roman}\n')
    front_sources = []
    if not args.chapter:
        preface = MANUSCRIPTS / '00-前言.md'
        if not preface.is_file():
            raise FileNotFoundError(f'Missing preface: expected {preface}')
        prepared_preface = work / preface.name
        prepare(preface, prepared_preface, assets, args.source_ref, strict=strict)
        preface_tex = work / 'preface.tex'
        run(['pandoc', str(prepared_preface), '--to=latex',
             '--lua-filter='+str(HERE/'layout.lua'),
             '--top-level-division=chapter', '-o', str(preface_tex)],
            log=work / 'preface-pandoc.log')
        before.write_text(before.read_text() + '\\input{' + str(preface_tex) + '}\n\\clearpage\n')
        front_sources.append(preface)
    # mainmatter starts after the TOC, immediately before the first source chapter.
    first = inputs[0]
    first.write_text('```{=latex}\n\\clearpage\n\\pagenumbering{arabic}\n'
                     f'\\setcounter{{chapter}}{{{(args.chapter or 1)-1}}}\n```\n\n'+first.read_text())
    tex = work / 'book.tex'
    command = ['pandoc', *map(str,inputs), '--file-scope', '--standalone',
               '--from=markdown+lists_without_preceding_blankline', '--to=latex',
               '--top-level-division=chapter', '--toc', '--toc-depth=2', '--number-sections',
               '--lua-filter='+str(HERE/'layout.lua'),
               '-V','documentclass=elegantbook', '-V','classoption=lang=cn',
               '-V','classoption=nofont', '-V','classoption=cyan', '-V','classoption=device=normal',
               '-V','author='+BOOK_AUTHOR, '--metadata','title-meta='+BOOK_TITLE,
               '--metadata','author-meta='+BOOK_AUTHOR, '-H', str(HERE/'preamble.tex'),
               '--include-before-body='+str(before), '--highlight-style=kate',
               '--columns=100', '-o',str(tex)]
    run(command,log=work/'pandoc.log')
    # XeLaTeX runs from book/ so imported series template and cover resolve locally.
    for iteration in range(1,4):
        run(['xelatex','-interaction=nonstopmode','-halt-on-error', '-file-line-error',
             '-output-directory='+str(work),str(tex)],log=work/f'xelatex-{iteration}.log')
    output = output_dir / f'{name}.pdf'
    staged_output = output.with_suffix('.pdf.tmp')
    shutil.copy2(work/'book.pdf',staged_output)
    staged_output.replace(output)
    log = (work/'book.log').read_text(errors='replace')
    warnings = [line for line in log.splitlines() if any(x in line for x in ['Overfull','Missing character:','undefined references','LaTeX Warning:'])]
    report = dict(output=str(output), source_ref=args.source_ref, chapters=[int(s.name[:2]) for s in sources],
                  engine='Pandoc + XeLaTeX / ElegantBook (AI Agent Book series template)',
                  sources=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in front_sources + sources],
                  figure_count=len(assets),warnings=warnings)
    (output_dir/f'{name}-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    if not args.chapter and shutil.which('pdfseparate') and shutil.which('pdftoppm'):
        if shutil.which('gs'):
            run(['gs','-q','-dBATCH','-dNOPAUSE','-sDEVICE=pdfwrite','-dFirstPage=1','-dLastPage=1',
                 '-sOutputFile='+str(output_dir/'AI4Polymer-Book-Cover.pdf'),str(output)])
        else:
            run(['pdfseparate','-f','1','-l','1',str(output),str(output_dir/'AI4Polymer-Book-Cover.pdf')])
        run(['pdftoppm','-f','1','-l','1','-scale-to','1600','-png','-singlefile',
             str(output),str(output_dir/'AI4Polymer-Book-Cover')])
    print(output)
    print(f'{len(sources)} chapters, {len(assets)} figures; {len(warnings)} layout/font warnings; details: {work}/book.log')


if __name__ == '__main__':
    main()
