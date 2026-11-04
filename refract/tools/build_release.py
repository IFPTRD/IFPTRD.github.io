#!/usr/bin/env python3
"""Build the Studio template, shared validator, and reproducible Copilot ZIP.

Run from any directory. --check verifies tracked release outputs without writing.
"""
import argparse
import base64
import io
import json
import re
import sys
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'skills/refract-html'
VERSION='6.4'
FILES=['SKILL.md']+[str(p.relative_to(PACKAGE)) for folder in ('references','scripts') for p in sorted((PACKAGE/folder).glob('*')) if p.is_file() and p.suffix in ('.md','.json','.html','.py')]

def outputs():
    template=(PACKAGE/'references/guide-template.html').read_text(encoding='utf-8')
    runtime=(ROOT/'renderer/viewer.js').read_text(encoding='utf-8')
    start=template.index('<script>')+len('<script>');end=template.index('</script>',start)
    template=template[:start]+'\n'+runtime+'\n'+template[end:]
    schema=json.loads((PACKAGE/'references/refract-schema.json').read_text())
    validator='// BEGIN SHARED VALIDATOR\nconst refractSchema='+json.dumps(schema,ensure_ascii=False,separators=(',',':'))+';\n'+(ROOT/'renderer/validate.js').read_text()+'// END SHARED VALIDATOR\n'
    studio=(ROOT/'index.html').read_text()
    studio=re.sub(r"const viewerTemplate=.*?;\nconst defaultData=",lambda _:"const viewerTemplate=new TextDecoder('utf-8').decode(Uint8Array.from(atob('"+base64.b64encode(template.encode()).decode()+"'),c=>c.charCodeAt(0)));\nconst defaultData=",studio,count=1)
    if '// BEGIN SHARED VALIDATOR' in studio:
        studio=re.sub(r'// BEGIN SHARED VALIDATOR.*?// END SHARED VALIDATOR\n',lambda _:validator,studio,count=1,flags=re.S)
    else:
        a=studio.index('function validate(data){');b=studio.index("let parseNotice=",a);studio=studio[:a]+validator+studio[b:]
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
        for name in FILES:
            content=template.encode() if name=='references/guide-template.html' else (PACKAGE/name).read_bytes()
            info=zipfile.ZipInfo(name,date_time=(2026,11,4,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,content)
    return {PACKAGE/'references/guide-template.html':template.encode(),ROOT/'renderer/guide-template.html':template.encode(),ROOT/'index.html':studio.encode(),ROOT/f'Refract_Copilot_HTML_Generator_v{VERSION}.zip':buf.getvalue()}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args();bad=[]
    for path,content in outputs().items():
        if a.check:
            if not path.exists() or path.read_bytes()!=content:bad.append(str(path.relative_to(ROOT)))
        else:path.write_bytes(content)
    if bad:print('Release outputs out of sync: '+', '.join(bad));return 1
    print('Release outputs synchronized' if not a.check else 'Release outputs match canonical source');return 0
if __name__=='__main__':sys.exit(main())
