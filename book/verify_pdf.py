#!/usr/bin/env python3
"""Validate delivered PDF content, embedded fonts, page bounds and build warnings."""
from pathlib import Path
import json
import re
import subprocess
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent


def output(*args):
    return subprocess.check_output(args, text=True)


def verify(name):
    path = HERE / (name+'.pdf')
    build = json.loads((HERE/(name+'-build.json')).read_text())
    info = output('pdfinfo',str(path))
    text = output('pdftotext','-layout',str(path),'-')
    font_output = output('pdffonts',str(path))
    fonts = [row.split() for row in font_output.splitlines()[2:] if row.strip()]
    # Columns have variable-length font types; final six columns are fixed.
    unembedded = [row[0] for row in fonts if row[-5] != 'yes']
    bounds = ET.fromstring(output('pdftotext','-bbox',str(path),'-'))
    ns = {'x':'http://www.w3.org/1999/xhtml'}
    page_count=int(re.search(r'Pages:\s+(\d+)',info)[1])
    rotations={int(n):int(angle) for n,angle in re.findall(r'Page\s+(\d+) rot:\s+(\d+)',output('pdfinfo','-f','1','-l',str(page_count),str(path)))}
    outside=[]
    for i,page in enumerate(bounds.findall('.//x:page',ns),1):
        width,height=float(page.attrib['width']),float(page.attrib['height'])
        # Poppler's word coordinates include page rotation; its XML dimensions do not.
        if rotations.get(i,0) % 180 == 90: width,height=height,width
        for word in page.findall('.//x:word',ns):
            a=word.attrib
            if (float(a['xMin']) < -2 or float(a['yMin']) < -2 or
                float(a['xMax']) > width+2 or float(a['yMax']) > height+2):
                outside.append(dict(page=i,text=word.text))
    critical=[w for w in build['warnings'] if any(s in w for s in ['Missing character','Overfull','undefined'])]
    checks={
        'title_and_author': 'AI4Polymer' in text and '谭诗乾' in text,
        'all_chapters': all(re.search(rf'第\s*{n}\s*章',text) for n in build['chapters']),
        'all_fonts_embedded': not unembedded,
        'all_pages_portrait': all(angle == 0 for angle in rotations.values()) and all(float(p.attrib['height']) > float(p.attrib['width']) for p in bounds.findall('.//x:page',ns)),
        'text_within_pages': not outside,
        'no_missing_glyphs_overflow_or_undefined_references': not critical,
    }
    return dict(pdf=path.name,pages=int(re.search(r'Pages:\s+(\d+)',info)[1]),
                figures=build['figure_count'],checks=checks,
                unembedded_fonts=unembedded,outside_page_text=outside,
                critical_warnings=critical,other_warnings=build['warnings'])


if __name__=='__main__':
    reports=[verify(n) for n in ['AI4Polymer-Book','AI4Polymer-Book-Chapter-02']]
    (HERE/'pdf-validation.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(reports,ensure_ascii=False,indent=2))
    raise SystemExit(not all(all(r['checks'].values()) for r in reports))
