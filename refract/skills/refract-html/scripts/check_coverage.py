#!/usr/bin/env python3
"""Check source-to-content mappings and exact precision anchors, not semantic fidelity.

Use --strict for new conversions. Legacy page mappings remain accepted otherwise.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from validate_refract import strings


def plain(value):
    text=' '.join(strings(value))
    # Cross-reference display labels and glossary wrappers do not change source wording.
    text=re.sub(r'\[\[(?:[^|\]]+\|)?([^\]]+)\]\]',r'\1',text)
    return ' '.join(unicodedata.normalize('NFC',text).split())


def check_coverage(inventory,guide,strict=False):
    errors=[]
    if not isinstance(inventory,dict) or not isinstance(inventory.get('units'),list) or not inventory['units']:
        return ['source inventory requires a nonempty units array']
    if not isinstance(guide,dict) or not isinstance(guide.get('pages'),list):return ['guide requires pages']
    pages={p['id']:p for p in guide['pages'] if isinstance(p,dict) and isinstance(p.get('id'),str)}
    units=inventory['units'];seen=set()
    all_units={u.get('id') for u in units if isinstance(u,dict) and isinstance(u.get('id'),str)}
    for i,u in enumerate(units):
        loc=f'units[{i}]'
        if not isinstance(u,dict):errors.append(loc+': expected object');continue
        for key in ('id','heading','kind'):
            if not isinstance(u.get(key),str) or not u[key].strip():errors.append(loc+'.'+key+': required text')
        uid=u.get('id')
        if isinstance(uid,str):
            if uid in seen:errors.append(loc+': duplicate unit ID')
            seen.add(uid)
        if strict and (not isinstance(u.get('source_location'),str) or not u['source_location'].strip()):errors.append(loc+': source_location must identify the document and section/page')
        status=u.get('status')
        if status not in ('included','merged','excluded'):errors.append(loc+': invalid status');continue
        if status=='excluded':
            code=u.get('exclusion_code')
            if code not in ('duplicate','blank','noninformative','user-excluded'):errors.append(loc+': use explicit exclusion_code: duplicate, blank, noninformative or user-excluded')
            if not isinstance(u.get('reason'),str) or not u['reason'].strip():errors.append(loc+': exclusion requires a reason')
            if code=='duplicate' and (not isinstance(u.get('duplicate_of'),str) or u.get('duplicate_of') not in all_units or u.get('duplicate_of')==uid or not any(isinstance(other,dict) and other.get('id')==u.get('duplicate_of') and other.get('status') in ('included','merged') for other in units)):errors.append(loc+': duplicate_of must name another inventoried unit')
            if code=='user-excluded' and not u.get('user_scope_reference'):errors.append(loc+': record the user instruction authorizing exclusion')
            if u.get('target_page_ids') or u.get('target_blocks'):errors.append(loc+': excluded unit cannot claim coverage')
            continue
        selected=[]
        mappings=u.get('target_blocks')
        if strict and (not isinstance(mappings,list) or not mappings):errors.append(loc+': strict coverage requires target_blocks')
        if mappings is not None:
            if not isinstance(mappings,list) or not mappings:errors.append(loc+': target_blocks must be nonempty');continue
            for target in mappings:
                if not isinstance(target,dict):errors.append(loc+': malformed block mapping');continue
                p=pages.get(target.get('page_id')) if isinstance(target.get('page_id'),str) else None
                block=next((b for j,b in enumerate(p.get('blocks',[])) if isinstance(b,dict) and b.get('id',f'section-{j+1}')==target.get('block_id')),None) if p else None
                if block is None:errors.append(loc+': unknown destination block '+str(target));continue
                if not plain({k:v for k,v in block.items() if k not in ('title','label','kicker')}):errors.append(loc+': mapped block has no substantive content')
                selected.append(block)
        else:
            targets=u.get('target_page_ids')
            if not isinstance(targets,list) or not targets:errors.append(loc+': source unit has no destination');continue
            for pid in targets:
                p=pages.get(pid) if isinstance(pid,str) else None
                if not p:errors.append(loc+': unknown destination page '+str(pid));continue
                if not p.get('blocks'):errors.append(loc+': destination page is empty')
                selected.extend(p.get('blocks',[]))
        exact=u.get('required_text',[])
        if not isinstance(exact,list) or any(not isinstance(t,str) or not t.strip() for t in exact):errors.append(loc+': required_text must contain nonempty exact source passages');continue
        # Check each anchor within one block; do not join separate passages into false matches.
        for text in exact:
            needle=plain(text)
            if not any(needle in plain(block) for block in selected):errors.append(loc+': missing or changed precision anchor '+repr(text))
    return errors


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('inventory',type=Path);p.add_argument('guide',type=Path);p.add_argument('--strict',action='store_true');a=p.parse_args()
    try:inventory=json.loads(a.inventory.read_text(encoding='utf-8-sig'));guide=json.loads(a.guide.read_text(encoding='utf-8-sig'))
    except (OSError,json.JSONDecodeError) as e:print('ERROR:',e,file=sys.stderr);return 2
    errors=check_coverage(inventory,guide,a.strict)
    for e in errors:print('ERROR:',e,file=sys.stderr)
    if errors:return 1
    print('PASS: inventoried mappings and supplied precision anchors checked.')
    print('This does not prove extraction, inventory completeness, or semantic fidelity; compare with the original source.')
    return 0
if __name__=='__main__':sys.exit(main())
