#!/usr/bin/env python3
"""Validate and optionally normalize Refract JSON without external packages."""
import argparse
import json
import re
import sys
from pathlib import Path

TYPES={"hero","paragraph","note","checks","cards","steps","bullets","table","resources","glossary","governance","timeline"}
def normalize(data):
    if not isinstance(data,dict):return data
    for page in data.get("pages",[]):
        if not isinstance(page,dict):continue
        for b in page.get("blocks",[]):
            if not isinstance(b,dict):continue
            if b.get("type")=="note" and "label" not in b and "title" in b:b["label"]=b.pop("title")
            if b.get("type")=="checks" and isinstance(b.get("items"),list):
                b["items"]=[{"title":"Check "+str(i),"detail":x} if isinstance(x,str) else x for i,x in enumerate(b["items"],1)]
            if b.get("type")=="resources" and isinstance(b.get("items"),list):
                items=b["items"]
                if items and all(isinstance(x,dict) and not x.get("url") for x in items):
                    b["type"]="bullets"
                    b["items"]=[" — ".join(str(x.get(k,"")) for k in ("title","text") if x.get(k)) for x in items]
    return data

def check(data):
    errors,warnings=[],[]
    def err(where,message):errors.append(where+": "+message)
    def string(x):return isinstance(x,str) and bool(x.strip())
    if not isinstance(data,dict):return ["root: expected object"],[]
    meta=data.get("meta")
    if not isinstance(meta,dict) or not string(meta.get("title")):err("meta.title","required string")
    if isinstance(meta,dict):
        for bad in ("source","sources","provenance","classification","filename","disclaimer"):
            if bad in meta:warnings.append("meta."+bad+": remove generated document provenance")
    pages=data.get("pages")
    if not isinstance(pages,list) or not pages:return errors+["pages: expected nonempty array"],warnings
    # No arbitrary page-count warning: large source-equivalent binders may legitimately require many pages.
    ids=set()
    for i,p in enumerate(pages):
        loc="pages["+str(i)+"]"
        if not isinstance(p,dict):err(loc,"expected object");continue
        pid=p.get("id")
        if not isinstance(pid,str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",pid):err(loc+".id","must be kebab-case")
        elif pid in ids:err(loc+".id","duplicate ID "+pid)
        else:ids.add(pid)
        if not string(p.get("title")):err(loc+".title","required nonempty string")
        blocks=p.get("blocks")
        if not isinstance(blocks,list):err(loc+".blocks","expected array");continue
        for j,b in enumerate(blocks):
            where=loc+".blocks["+str(j)+"]"
            if not isinstance(b,dict):err(where,"expected object");continue
            typ=b.get("type")
            if typ not in TYPES:err(where+".type","unsupported type");continue
            if typ=="note":
                if not string(b.get("label")):err(where+".label","note needs label, not title")
                if not string(b.get("text")):err(where+".text","required")
            else:
                if not string(b.get("title")):err(where+".title","required")
            if typ in ("hero","paragraph") and not string(b.get("text")):err(where+".text","required")
            if typ=="table":
                cols,rows=b.get("columns"),b.get("rows")
                if not isinstance(cols,list) or not cols or not all(isinstance(c,str) for c in cols):err(where+".columns","must be array of strings")
                if not isinstance(rows,list):err(where+".rows","must be array")
                elif isinstance(cols,list):
                    for k,row in enumerate(rows):
                        if not isinstance(row,list) or len(row)!=len(cols) or not all(isinstance(c,str) for c in row):err(where+".rows["+str(k)+"]","wrong number/type of cells")
            if typ=="governance":
                cols=b.get("columns")
                if not isinstance(cols,list) or len(cols)<2 or len(cols)>4:err(where+".columns","governance requires 2–4 columns")
                else:
                    for k,column in enumerate(cols):
                        cw=where+".columns["+str(k)+"]"
                        if not isinstance(column,dict) or not string(column.get("title")):err(cw,"requires a title");continue
                        nodes=column.get("items")
                        if not isinstance(nodes,list) or not nodes:err(cw+".items","requires nonempty items")
                        else:
                            for n,node in enumerate(nodes):
                                if not isinstance(node,dict) or not string(node.get("title")):err(cw+".items["+str(n)+"]","requires a title")
            if typ in ("checks","steps","cards","glossary","resources","bullets","timeline"):
                items=b.get("items")
                if not isinstance(items,list):err(where+".items","expected array");continue
                for k,item in enumerate(items):
                    il=where+".items["+str(k)+"]"
                    if typ=="bullets":
                        if not isinstance(item,str):err(il,"must be a string")
                        continue
                    if not isinstance(item,dict):err(il,"requires an object");continue
                    keys={"checks":("title","detail"),"steps":("title","text"),"cards":("title","text"),"glossary":("term","definition"),"resources":("title","url"),"timeline":("period","title","text")}[typ]
                    if any(not string(item.get(key)) for key in keys):err(il,"required fields: "+", ".join(keys))
                    if typ=="resources" and string(item.get("url")) and not re.match(r"https?://",item["url"],re.I):err(il+".url","must be HTTP(S)")
    for i,p in enumerate(pages):
        if not isinstance(p,dict):continue
        if p.get("parent") and p["parent"] not in ids:err("pages["+str(i)+"].parent","unknown page")
        for j,b in enumerate(p.get("blocks",[])):
            if isinstance(b,dict) and b.get("type")=="cards":
                for k,item in enumerate(b.get("items",[])):
                    if isinstance(item,dict) and item.get("link") and item["link"] not in ids:err("pages["+str(i)+"].blocks["+str(j)+"].items["+str(k)+"].link","unknown page")
    glossary=data.get("glossary",[])
    if not isinstance(glossary,list):err("glossary","expected array")
    else:
        for i,term in enumerate(glossary):
            if not isinstance(term,dict) or not string(term.get("term")) or not string(term.get("definition")):err("glossary["+str(i)+"]","term and definition required")
    suspicious_heading=re.compile(r"^(?:sources?|source and distribution|document provenance|source document|generated from|prepared using)$",re.I)
    suspicious_text=re.compile(r"(?:based on [^.\n]{0,130}\.(?:docx|pdf|pptx)|linked documents were not used|unclassified\s*/\s*non classifi[eé])",re.I)
    for i,p in enumerate(pages):
        if not isinstance(p,dict):continue
        if suspicious_heading.match(str(p.get("title","")).strip()):warnings.append("pages["+str(i)+"]: remove source attribution page")
        for j,b in enumerate(p.get("blocks",[])):
            if not isinstance(b,dict):continue
            if suspicious_heading.match(str(b.get("title",b.get("label",""))).strip()) or suspicious_text.search(str(b.get("text",""))):
                warnings.append("pages["+str(i)+"].blocks["+str(j)+"]: remove generated provenance notice")
    return errors,warnings

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file",type=Path)
    parser.add_argument("--normalize",action="store_true")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:data=json.loads(args.file.read_text(encoding="utf-8-sig"))
    except (OSError,json.JSONDecodeError) as exc:print("INVALID JSON:",exc,file=sys.stderr);return 1
    if args.normalize:normalize(data)
    errors,warnings=check(data)
    for warning in warnings:print("WARNING:",warning,file=sys.stderr)
    for error in errors:print("ERROR:",error,file=sys.stderr)
    if errors:return 1
    if args.output:args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("VALID:",len(data["pages"]),"pages")
    return 0
if __name__=="__main__":sys.exit(main())
