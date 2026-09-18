#!/usr/bin/env python3
"""Check current chapter endings, references, figure indices and new derivations."""
from pathlib import Path
from urllib.parse import unquote,urlsplit
import re,json,hashlib
ROOT=Path(__file__).resolve().parents[1];M=ROOT/'manuscripts';R=ROOT/'build/reviews/core-principles-revision'
CHAPTERS=16
errors=[];rows=[]
def check(ok,msg):
 if not ok:errors.append(msg)
def chapter_path(n):
 matches=sorted(M.glob(f'{n:02}-*.md'))
 if not matches:
  errors.append(f'{n}: missing manuscript {n:02}-*.md')
  return None
 return matches[0]
for n in range(1,CHAPTERS+1):
 p=chapter_path(n)
 if p is None:continue
 s=p.read_text()
 headings=re.findall(r'^## (.+)$',s,re.M)
 check(headings[-1]=='本章小结' and headings.count('本章小结')==1,f'{n}: final summary')
 check(not any(any(w in h for w in ['参考资料','参考文献','资料说明','资料与','注释与','文献与','参考与']) for h in headings),f'{n}: reference sections removed')
 defined=set(re.findall(r'^\[\^([^\]]+)\]:',s,re.M));used=set(re.findall(r'\[\^([^\]]+)\](?!:)',s));check(used<=defined,f'{n}: unresolved footnotes {used-defined}')
 for url in re.findall(r'\]\(([^)]+)\)',s):
  u=urlsplit(url.strip('<>'))
  if not u.scheme and u.path:check((p.parent/unquote(u.path)).exists(),f'{n}: missing local link {url}')
 assets=re.findall(r'!\[[^\n]*\]\(([^)]+)\)',s)
 index_path=M/f'ch{n:02}/figure-index.json'
 if not index_path.is_file():
  errors.append(f'{n}: missing figure index {index_path.relative_to(ROOT)}')
 else:
  index=json.loads(index_path.read_text())
  got=[r.get('asset') or f'ch{n:02}/'+(r.get('file') or r['name']+'.svg') for r in index]
  check(got==assets,f'{n}: active figure index')
 # The before/ snapshot is optional: only compare exercise identifiers when it exists.
 before_dir=R/'before'/'manuscripts'
 if before_dir.is_dir():
  matches=sorted(before_dir.glob(f'{n:02}-*.md'))
  if matches:
   before=matches[0].read_text()
   # Removing references must not remove exercises or alter their identifiers.
   exercise=lambda x:re.findall(r'^> \*\*(?:练习|实验) (\d+-\d+)',x,re.M)
   check(exercise(s)==exercise(before),f'{n}: preserved exercise identifiers')
 rows.append(dict(chapter=n,last_section=headings[-1],figures=len(assets),footnotes=len(defined)))
# Optional counterfactual data; only checked when the owning agent has produced it.
d_path=ROOT/'calculations/results/core-principles.json'
new_figures=0
if d_path.is_file():
 d=json.loads(d_path.read_text())
 new_figures=d.get('new_figures',0)
 for source in d.get('sources',[]):
  check(hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()==source['sha256'],'counterfactual source hash')
report=dict(passed=not errors,chapters=rows,new_figures=new_figures,total_figures=sum(r['figures'] for r in rows),errors=errors)
R.mkdir(parents=True,exist_ok=True)
(R/'core-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(bool(errors))
