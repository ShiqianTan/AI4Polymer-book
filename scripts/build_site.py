#!/usr/bin/env python3
"""Stage authoritative Markdown and referenced images, then build the reading site."""
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'build/docs'
REPO = 'https://github.com/ShiqianTan/AI4Polymer-book'
CHAPTERS = 16
CHAPTER_TITLES = {
    1: '初识 AI4Polymer',
    2: '高分子表示与描述符',
    3: '数据、基准与可复现性',
    4: '高分子物理与结构–性能关系',
    5: '分子模拟与多尺度计算',
    6: '性质预测模型',
    7: '多任务、迁移与物理信息学习',
    8: '表征、成像与光谱的 AI 分析',
    9: '生成模型与高分子序列设计',
    10: '逆向设计与多目标材料设计',
    11: '主动学习、贝叶斯优化与强化学习',
    12: '反应预测、聚合建模与可合成性',
    13: '自驱动实验室与高通量自动化',
    14: '高分子基础模型与智能体系统',
    15: '可持续高分子与环境应用',
    16: '端到端案例与工程实践',
}


def stage():
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)
    ref = os.environ.get('BOOK_SOURCE_REF') or subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    catalog = []
    for path in sorted((ROOT / 'manuscripts').glob('[0-9][0-9]-*.md')):
        number = int(path.name[:2])
        if 1 <= number <= CHAPTERS:
            heading = path.read_text(encoding='utf-8').splitlines()[0]
            parsed = re.sub(r'^#\s*第\s*\d+\s*章\s*', '', heading).strip()
            title = parsed or CHAPTER_TITLES[number]
            catalog.append({'number': number, 'title': title, 'file': path.name})
    found = [c['number'] for c in catalog]
    if found != list(range(1, CHAPTERS + 1)):
        missing = sorted(set(range(1, CHAPTERS + 1)) - set(found))
        raise ValueError(
            f'Expected manuscript chapters 1–{CHAPTERS} in manuscripts/; '
            f'found {found or "none"}; missing {missing}')
    # The reading site carries only the book itself; repository and build notes stay on GitHub.
    sources = {ROOT / 'website/index.md': Path('index.md')}
    for folder in ('manuscripts',):
        for chapter in catalog:
            path = ROOT / folder / chapter['file']
            if not path.is_file():
                raise FileNotFoundError(path)
            sources[path] = path.relative_to(ROOT)
    preface = ROOT / 'manuscripts/00-前言.md'
    if not preface.is_file():
        raise FileNotFoundError(f'Missing preface: expected {preface}')
    sources[preface] = Path('manuscripts/00-前言.md')
    appendix = ROOT / 'manuscripts/90-附录.md'
    if appendix.is_file():
        sources[appendix] = Path('manuscripts/90-附录.md')

    def rewrite(source, output, url, image=False):
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return url
        target = (source.parent / unquote(parsed.path)).resolve()
        if not target.is_relative_to(ROOT):
            raise ValueError(f'Link escapes repository: {source}: {url}')
        if not target.exists():
            raise FileNotFoundError(f'{source.relative_to(ROOT)}: {url}')
        fragment = ('#' + parsed.fragment) if parsed.fragment else ''
        if target in sources:
            return quote(os.path.relpath(sources[target], output.parent), safe='/.-') + fragment
        if image:
            relative = target.relative_to(ROOT)
            dest = DOCS / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            if target.read_bytes().startswith(b'version https://git-lfs.github.com/spec/v1'):
                raise ValueError(f'Image is an LFS pointer; run git lfs pull: {relative}')
            shutil.copy2(target, dest)
            return quote(os.path.relpath(relative, output.parent), safe='/.-') + fragment
        return f'{REPO}/blob/{quote(ref, safe="")}/{quote(target.relative_to(ROOT).as_posix(), safe="/")}' + fragment

    for source, output in sources.items():
        content = source.read_text(encoding='utf-8')
        # Historical unused note definitions otherwise emit broken backlink anchors.
        used_notes = set(re.findall(r'\[\^([^\]]+)\](?!:)', content))
        content = re.sub(
            r'^\[\^([^\]]+)\]:[^\n]*(?:\n(?:[ \t]+[^\n]*|(?=\n[ \t])[^\n]*))*',
            lambda m: m[0] if m[1] in used_notes else '', content, flags=re.M)

        def inline(match):
            prefix, url = match.groups()
            return prefix + '(' + rewrite(source, output, url.strip('<>'), prefix.startswith('!')) + ')'
        content = re.sub(r'(!?\[[^\]\n]*\])\((<?[^)\n]+>?)\)', inline, content)
        def reference(match):
            return match[1] + rewrite(source, output, match[2].strip('<>')) + match[3]
        content = re.sub(r'^(\[(?!\^)[^\]\n]+\]:\s*)(\S+)(.*)$', reference, content, flags=re.M)
        dest = DOCS / output
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding='utf-8')
    (DOCS / 'assets').mkdir(exist_ok=True)
    for name in ('math.js', 'reading.css'):
        shutil.copy2(ROOT / 'website' / name, DOCS / 'assets' / name)
    # JSON is valid YAML and avoids quoting problems in Chinese chapter titles.
    # One flat list: 首页, 前言, then the sixteen chapters, so the reading order is the navigation.
    nav = [{'首页': 'index.md'}, {'前言': 'manuscripts/00-前言.md'}] + [
        {f'{c["number"]}. {c["title"]}': f'manuscripts/{c["file"]}'} for c in catalog]
    if (ROOT / 'manuscripts/90-附录.md').is_file():
        nav.append({'附录': 'manuscripts/90-附录.md'})
    # mkdocs.yml ends with a placeholder nav; replace it with the generated one.
    config = (ROOT / 'mkdocs.yml').read_text(encoding='utf-8').split('\nnav:')[0].rstrip('\n')
    config = config + '\nnav: ' + json.dumps(nav, ensure_ascii=False) + '\n'
    # Config stays at the root so docs_dir/site_dir remain relative to the repository.
    (ROOT / '.mkdocs-build.yml').write_text(config, encoding='utf-8')
    print(f'Staged {len(sources)} Markdown pages from source ref {ref}.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serve', action='store_true', help='Preview at http://127.0.0.1:8000')
    args = parser.parse_args()
    stage()
    command = [sys.executable, '-m', 'mkdocs', 'serve' if args.serve else 'build',
               '--strict', '-f', str(ROOT / '.mkdocs-build.yml')]
    subprocess.run(command, cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
