#!/usr/bin/env python3
"""Validate Refract structure and links without third-party dependencies."""
import argparse
import base64
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA_PATH = Path(__file__).resolve().parent.parent / 'references/refract-schema.json'
ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')

def normalize(data):
    """Explicit opt-in compatibility repairs; never discard unrecognized fields."""
    if not isinstance(data, dict): return data
    pages = data.get('pages', [])
    for page in pages if isinstance(pages, list) else []:
        if not isinstance(page, dict) or not isinstance(page.get('blocks'), list): continue
        for b in page['blocks']:
            if not isinstance(b, dict): continue
            if b.get('type') == 'note' and 'label' not in b and 'title' in b:
                b['label'] = b.pop('title')
    return data

def strings(value):
    """Reader-facing strings only; no IDs, URLs or hidden metadata."""
    if isinstance(value, str): yield value
    elif isinstance(value, list):
        for v in value: yield from strings(v)
    elif isinstance(value, dict):
        for k,v in value.items():
            if k not in ('id','type','parent','link','url','src'): yield from strings(v)

def valid_url(value):
    if not isinstance(value,str) or re.search(r'\s|[<>"\\]',value): return False
    try:
        u=urlsplit(value)
        return u.scheme.lower() in ('http','https') and bool(u.hostname) and u.username is None and u.password is None and (u.port is None or 0 < u.port <= 65535)
    except ValueError: return False

def valid_image(value):
    if not isinstance(value,str): return False
    m=re.fullmatch(r'data:image/(png|jpeg|gif|webp);base64,([A-Za-z0-9+/]+={0,2})',value)
    if not m: return False
    try: raw=base64.b64decode(m[2],validate=True)
    except ValueError: return False
    return {'png':raw.startswith(b'\x89PNG\r\n\x1a\n'),'jpeg':raw.startswith(b'\xff\xd8\xff'),
            'gif':raw[:6] in (b'GIF87a',b'GIF89a'),'webp':raw[:4]==b'RIFF' and raw[8:12]==b'WEBP'}[m[1]]

def schema_errors(value, schema, path='root'):
    errors=[]
    if 'oneOf' in schema:
        choices=schema['oneOf']
        selected=next((s for s in choices if isinstance(value,dict) and s.get('properties',{}).get('type',{}).get('const')==value.get('type')),None)
        return schema_errors(value,selected,path) if selected else [path+'.type: unsupported or missing block type']
    typ=schema.get('type')
    correct={'object':isinstance(value,dict),'array':isinstance(value,list),'string':isinstance(value,str)}
    if typ and not correct.get(typ,True):return [path+': expected '+typ]
    if 'const' in schema and value!=schema['const']:errors.append(path+': unexpected value')
    if typ=='object':
        props=schema.get('properties',{})
        for k in schema.get('required',[]):
            if k not in value:errors.append(path+'.'+k+': required field')
        for k,v in value.items():
            if k not in props:
                if schema.get('additionalProperties') is False:errors.append(path+'.'+k+': unsupported field; move its content to a supported field or block')
            else:errors.extend(schema_errors(v,props[k],path+'.'+k))
    elif typ=='array':
        if len(value)<schema.get('minItems',0):errors.append(path+': too few items')
        if len(value)>schema.get('maxItems',float('inf')):errors.append(path+': too many items')
        for i,v in enumerate(value):errors.extend(schema_errors(v,schema.get('items',{}),f'{path}[{i}]'))
    elif typ=='string':
        if schema.get('pattern') and not re.search(schema['pattern'],value):errors.append(path+': invalid format')
    return errors

def check(data):
    schema=json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
    errors=schema_errors(data,schema)
    warnings=[]
    # Stop after schema errors so malformed input always returns diagnostics, not a traceback.
    if errors:return errors,warnings
    def err(path,message):errors.append(path+': '+message)
    pages=data['pages']; ids={}; anchors={}
    for i,p in enumerate(pages):
        loc=f'pages[{i}]'
        if p['id'] in ids:err(loc+'.id','duplicate page ID')
        ids[p['id']]=p
        if not p['title'].strip():err(loc+'.title','must not be blank')
        seen=set()
        for j,b in enumerate(p['blocks']):
            key=b.get('id',f'section-{j+1}')
            if key in seen:err(loc+'.blocks','duplicate section ID '+key)
            seen.add(key)
        anchors[p['id']]=seen
    if not data['meta']['title'].strip():err('meta.title','must not be blank')
    terms=set()
    for i,g in enumerate(data['glossary']):
        if not g['term'].strip() or not g['definition'].strip():err(f'glossary[{i}]','term and definition must not be blank')
        term=g['term'].strip().casefold()
        if term in terms:err(f'glossary[{i}]','duplicate term')
        terms.add(term)
    def target_ok(target):
        pid,sep,bid=target.partition('#')
        return pid in ids and (not sep or bid in anchors[pid])
    for i,p in enumerate(pages):
        loc=f'pages[{i}]'
        parent=p.get('parent')
        if parent:
            if parent not in ids:err(loc+'.parent','unknown parent page')
            visited={p['id']}; cursor=parent
            while cursor in ids:
                if cursor in visited:err(loc+'.parent','parent cycle');break
                visited.add(cursor);cursor=ids[cursor].get('parent')
        if not p['blocks'] and not any(x.get('parent')==p['id'] for x in pages):
            warnings.append(loc+': empty page; add substantive content or use as a parent group')
        for j,b in enumerate(p['blocks']):
            where=f'{loc}.blocks[{j}]';typ=b['type']
            for required in ('title','text','label'):
                if required in b and not b[required].strip():err(where+'.'+required,'must not be blank')
            if typ=='table':
                if not b['columns']:err(where+'.columns','requires at least one column')
                for k,row in enumerate(b['rows']):
                    if len(row)!=len(b['columns']):err(f'{where}.rows[{k}]','cell count differs from columns')
            if typ=='image' and (not b['alt'].strip() or not valid_image(b['src'])):err(where,'image needs descriptive alt text and an embedded PNG/JPEG/GIF/WebP data URL')
            if typ=='governance' and not 2<=len(b['columns'])<=4:err(where+'.columns','requires 2–4 columns')
            for k,item in enumerate(b.get('items',[])):
                if not isinstance(item,dict):continue
                for field in ('title','text','detail','term','definition','period'):
                    if field in item and not item[field].strip():err(f'{where}.items[{k}].{field}','must not be blank')
                if typ=='resources' and not valid_url(item['url']):err(f'{where}.items[{k}].url','requires a complete HTTP(S) URL with a hostname')
                if typ=='cards' and item.get('link') and not target_ok(item['link']):err(f'{where}.items[{k}].link','unknown page or section')
        for text in strings({'title':p['title'],'intro':p.get('intro',''),'blocks':p['blocks']}):
            for ref in re.findall(r'\[\[(.*?)\]\]',text):
                if '|' in ref:
                    target,label=ref.split('|',1)
                    if not label.strip() or not target_ok(target):err(loc,'unresolved cross-reference '+ref)
                elif ref.strip().casefold() not in terms:err(loc,'undefined glossary term '+ref)
    suspicious=re.compile(r'^(?:source and distribution|document provenance|source document|generated from|prepared using)$',re.I)
    for i,p in enumerate(pages):
        for b in p['blocks']:
            if suspicious.fullmatch(b.get('title',b.get('label','')).strip()):warnings.append(f'pages[{i}]: review generated provenance notice; retain only if requested or substantively required')
    return errors,warnings

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file',type=Path);parser.add_argument('--normalize',action='store_true');parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:data=json.loads(args.file.read_text(encoding='utf-8-sig'))
    except (OSError,json.JSONDecodeError) as exc:print('INVALID JSON:',exc,file=sys.stderr);return 1
    if args.normalize:normalize(data)
    errors,warnings=check(data)
    for w in warnings:print('WARNING:',w,file=sys.stderr)
    for e in errors:print('ERROR:',e,file=sys.stderr)
    if errors:return 1
    if args.output:args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('VALID:',len(data['pages']),'pages');return 0
if __name__=='__main__':sys.exit(main())
