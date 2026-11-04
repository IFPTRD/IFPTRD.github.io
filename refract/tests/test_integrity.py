"""Regression checks for silent loss, exact anchors, navigation and HTML round trips."""
import base64
import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PKG=ROOT/'skills/refract-html'
sys.path.insert(0,str(PKG/'scripts'))
from validate_refract import check
from check_coverage import check_coverage
from render_refract import render

PNG='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aRXsAAAAASUVORK5CYII='

def guide():
    return {'meta':{'title':'Meeting binder','subtitle':'Synthetic regression material','audience':'Participants'},'pages':[
        {'id':'agenda','title':'Meeting agenda','blocks':[{'type':'cards','id':'items','title':'Agenda items','items':[{'title':'Capacity','text':'Full issue briefing','link':'capacity#requirements'}]}]},
        {'id':'capacity','parent':'agenda','title':'Capacity briefing','blocks':[
            {'type':'paragraph','id':'requirements','title':'Requirements','text':'Requests must not exceed 12.5 mg/kg.\nSubmit by 12:00 on 4 November 2026. See [[capacity#evidence|supporting evidence]].'},
            {'type':'table','id':'evidence','title':'Evidence','columns':['Item','Value'],'rows':[['Limit¹','12.5 mg/kg']],'footnotes':['¹ Applies only to the specified population.']},
            {'type':'image','id':'chart','title':'Original figure','src':PNG,'alt':'Synthetic reference image','caption':'Original caption retained.'}
        ]}], 'glossary':[]}

def inventory():
    return {'units':[{'id':'brief','heading':'Capacity briefing','kind':'issue-brief','source_location':'Synthetic binder, capacity briefing, paragraphs 1–2','status':'included','target_blocks':[{'page_id':'capacity','block_id':'requirements'}],'required_text':['must not exceed 12.5 mg/kg.','Submit by 12:00 on 4 November 2026.']} ]}

class Integrity(unittest.TestCase):
    def test_valid_dense_guide(self):
        self.assertEqual(check(guide()),([],[]));self.assertEqual(check_coverage(inventory(),guide(),True),[])
    def test_empty_page_cannot_claim_coverage(self):
        d=guide();d['pages'][1]['blocks']=[]
        i=inventory();i['units'][0].pop('target_blocks');i['units'][0]['target_page_ids']=['capacity']
        self.assertTrue(check_coverage(i,d));self.assertTrue(check_coverage(i,d,True))
    def test_changed_precision_and_negation(self):
        for old,new in [('12.5','125'),('mg/kg','mg'),('must not','must'),('12:00','14:00')]:
            d=guide();d['pages'][1]['blocks'][0]['text']=d['pages'][1]['blocks'][0]['text'].replace(old,new)
            self.assertTrue(check_coverage(inventory(),d,True),old)
    def test_anchor_must_be_in_mapped_block(self):
        i=inventory();i['units'][0]['target_blocks'][0]['block_id']='evidence'
        self.assertTrue(check_coverage(i,guide(),True))
    def test_strict_locations(self):
        i=inventory();i['units'][0].pop('source_location');self.assertTrue(check_coverage(i,guide(),True))
    def test_unsupported_fields_rejected(self):
        d=guide();d['pages'][1]['blocks'][0]['supporting_detail']='Essential annex'
        self.assertTrue(any('supporting_detail' in e for e in check(d)[0]))
    def test_hierarchy_cycles(self):
        d=guide();d['pages'][0]['parent']='capacity';self.assertTrue(check(d)[0])
        d=guide();d['pages'][1]['parent']='capacity';self.assertTrue(check(d)[0])
    def test_broken_and_duplicate_sections(self):
        d=guide();d['pages'][1]['blocks'][1]['id']='requirements';self.assertTrue(check(d)[0])
        d=guide();d['pages'][0]['blocks'][0]['items'][0]['link']='capacity#missing';self.assertTrue(check(d)[0])
    def test_urls(self):
        for url in ['https://','https://host name/a','javascript:alert(1)','https://example.org:99999','https://user:password@example.org']:
            d=guide();d['pages'][0]['blocks']=[{'type':'resources','title':'Links','items':[{'title':'Reference','url':url}]}];self.assertTrue(check(d)[0],url)
        d['pages'][0]['blocks'][0]['items'][0]['url']='https://example.org/document?id=a%20b&view=1';self.assertFalse(check(d)[0])
    def test_undefined_glossary(self):
        d=guide();d['pages'][1]['intro']='[[UNKNOWN]]';self.assertTrue(check(d)[0])
    def test_images(self):
        for src in ['https://example.org/image.png','data:image/svg+xml;base64,AAAA','data:image/png;base64,AAAA']:
            d=guide();d['pages'][1]['blocks'][2]['src']=src;self.assertTrue(check(d)[0])
    def test_malformed_types_return_errors(self):
        for value in [None,[],{}, {'meta':{},'pages':[None],'glossary':[]}, {'meta':{'title':'x'},'pages':[{'id':'a','title':'A','blocks':5}],'glossary':[]}]:self.assertTrue(check(value)[0])
        i=inventory();i['units'][0]['target_blocks'][0]['page_id']=[];self.assertTrue(check_coverage(i,guide(),True))
    def test_no_page_limit(self):
        d=guide();d['pages'] += [{'id':f'annex-{i}','title':f'Annex {i}','parent':'agenda','blocks':[{'type':'paragraph','title':'Detail','text':'Substantive supporting material'}]} for i in range(60)]
        self.assertEqual(check(d),([],[]))
    def test_exclusion_requires_evidence(self):
        i=inventory();u=i['units'][0];u.update(status='excluded',reason='too long',target_blocks=[]);self.assertTrue(check_coverage(i,guide(),True))
        u.update(exclusion_code='duplicate',duplicate_of='brief');self.assertTrue(check_coverage(i,guide(),True))
    def test_lossless_embed_and_studio_build(self):
        d=guide();d['pages'][1]['blocks'][0]['text']+=' Literal <tag> & $& </script> \u2028 [[capacity#evidence|Evidence]]'
        html=render(d);embedded=re.search(r'<script[^>]*id="guide-data"[^>]*>(.*?)</script>',html,re.S)[1]
        self.assertEqual(json.loads(embedded),d)
        studio=(ROOT/'index.html').read_text()
        build=studio[studio.index('function build('):studio.index('\nfunction prepare(')]
        harness="const viewerTemplate="+json.dumps((PKG/'references/guide-template.html').read_text())+";const visualState={};\n"+build+";process.stdout.write(build("+json.dumps(d)+"));"
        actual=subprocess.check_output(['node','-e',harness],text=True)
        actual_data=re.search(r'<script[^>]*id="guide-data"[^>]*>(.*?)</script>',actual,re.S)[1]
        self.assertEqual(json.loads(actual_data),d)
    def test_python_javascript_validation_agreement(self):
        cases=[guide()]
        for field,value in [('parent','capacity'),('intro','[[MISSING]]')]:
            d=guide();d['pages'][1][field]=value;cases.append(d)
        d=guide();d['pages'][1]['blocks'][0]['unexpected']='Do not silently lose me';cases.append(d)
        d=guide();d['pages'][1]['blocks'][1]['rows'][0].append('extra');cases.append(d)
        d=guide();d['pages'][0]['blocks'][0]['items'][0]['link']='capacity#missing';cases.append(d)
        schema=(PKG/'references/refract-schema.json').read_text();js=(ROOT/'renderer/validate.js').read_text()
        harness='const refractSchema='+schema+';\n'+js+'\nconsole.log(JSON.stringify('+json.dumps(cases)+'.map(x=>validate(x).errors.length>0)));'
        results=json.loads(subprocess.check_output(['node','-e',harness],text=True))
        self.assertEqual(results,[bool(check(x)[0]) for x in cases])
    def test_render_refuses_changed_anchor(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);d=guide();d['pages'][1]['blocks'][0]['text']='Altered briefing.'
            (td/'guide.json').write_text(json.dumps(d));(td/'inventory.json').write_text(json.dumps(inventory()))
            result=subprocess.run([sys.executable,str(PKG/'scripts/render_refract.py'),str(td/'guide.json'),'--inventory',str(td/'inventory.json'),'--output',str(td/'guide.html')],capture_output=True)
            self.assertNotEqual(result.returncode,0);self.assertFalse((td/'guide.html').exists())
    def test_release_sync(self):
        subprocess.run([sys.executable,str(ROOT/'tools/build_release.py'),'--check'],check=True,capture_output=True)

if __name__=='__main__':unittest.main()
