#!/usr/bin/env python3
"""Reject checked-in HTML, including force-added files ignored by Git.

The reference archive keeps original HTML snapshots under `references/files/`
for sources that have no PDF form; their searchable text lives in
`references/text/`. Those snapshots are the only permitted HTML in the tree.
"""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
ARCHIVE = 'references/files/'
paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
forbidden = [
    p for p in paths
    if Path(p).suffix.lower() in ('.html', '.htm')
    and not p.startswith(ARCHIVE)
    and (root / p).exists()
]
if forbidden:
    raise SystemExit('HTML must only be a build artifact:\n' + '\n'.join(forbidden))
print('PASS: no tracked HTML source files')
