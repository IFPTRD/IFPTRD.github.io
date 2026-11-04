(()=>{'use strict';
const data=JSON.parse(document.getElementById('guide-data').textContent);
const pages=data.pages||[],gloss=Array.isArray(data.glossary)?data.glossary:[];
const editPreview=__EDITOR_MODE__,initialPageId=__EDITOR_PAGE__;
const $=id=>document.getElementById(id);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const id=p=>String(p.id||'').replace(/[^a-z0-9-]/gi,'');
const blockId=(b,i)=>b.id||'section-'+(i+1);
const sectionId=(pid,bid)=>'section-'+pid+'--'+bid;
const pageById=new Map(pages.map(p=>[id(p),p]));
function targetExists(t){const [pid,bid]=t.split('#');const p=pageById.get(pid);return !!p&&(!bid||p.blocks.some((b,i)=>blockId(b,i)===bid))}
function fmt(s){return String(s??'').split(/(\[\[[^\]]+\]\])/g).map(part=>{
 const m=part.match(/^\[\[(.*?)\]\]$/);if(!m)return esc(part);
 const pipe=m[1].indexOf('|');if(pipe>=0){const target=m[1].slice(0,pipe),label=m[1].slice(pipe+1);return targetExists(target)?'<a href="#'+esc(target)+'">'+esc(label)+'</a>':esc(label)}
 const term=m[1].trim(),g=gloss.find(x=>String(x.term||'').toLowerCase()===term.toLowerCase());
 return g?'<abbr tabindex="0" title="'+esc(g.definition)+'" aria-label="'+esc(term+': '+g.definition)+'">'+esc(term)+'</abbr>':esc(term)
 }).join('')}
const internalLink=(target,text)=>targetExists(target)?'<a href="#'+esc(target)+'">'+fmt(text)+'</a>':fmt(text);
function validHref(url){try{const u=new URL(url);return /^https?:$/.test(u.protocol)&&u.hostname&&!u.username&&!u.password&&!/[\s<>"\\]/.test(url)?url:''}catch{return ''}}
function notifyStudio(type,details){if(editPreview&&window.parent!==window)window.parent.postMessage(Object.assign({source:'refract-preview',type},details),'*')}
function renderBlock(b){if(!b||typeof b!=='object')return'';const title=b.title?'<h2>'+fmt(b.title)+'</h2>':'';const list=Array.isArray(b.items)?b.items:[];
switch(b.type){
case 'hero':return '<div class="section-block hero">'+(b.kicker?'<span class="kicker">'+fmt(b.kicker)+'</span>':'')+'<h2>'+fmt(b.title)+'</h2><p>'+fmt(b.text)+'</p></div>';
case 'paragraph':return '<section class="section-block">'+title+'<p>'+fmt(b.text)+'</p></section>';
case 'note':return '<aside class="section-block note"><strong>'+fmt(b.label||'Note')+'</strong><p>'+fmt(b.text)+'</p></aside>';
case 'cards':return '<section class="section-block">'+title+'<div class="card-grid">'+list.map(x=>'<article class="content-card"><h3>'+(x.link?internalLink(x.link,x.title):fmt(x.title))+'</h3><p>'+fmt(x.text)+'</p></article>').join('')+'</div></section>';
case 'checks':return '<section class="section-block">'+title+'<div class="checks" style="--check-rows:'+Math.ceil(list.length/2)+'">'+list.map((x,i)=>'<div class="check"><div class="check-number">'+String(i+1).padStart(2,'0')+'</div><div><h3>'+fmt(x.title)+'</h3><p>'+fmt(x.detail)+'</p></div></div>').join('')+'</div></section>';
case 'steps':return '<section class="section-block">'+title+'<ol class="steps">'+list.map(x=>'<li><h3>'+fmt(x.title)+'</h3><p>'+fmt(x.text)+'</p></li>').join('')+'</ol></section>';
case 'bullets':return '<section class="section-block">'+title+'<ul class="bullets">'+list.map(x=>'<li>'+fmt(x)+'</li>').join('')+'</ul></section>';
case 'table':{const cols=Array.isArray(b.columns)?b.columns:[];const rows=Array.isArray(b.rows)?b.rows:[];return '<section class="section-block">'+title+'<div class="table-wrap"><table><thead><tr>'+cols.map(c=>'<th scope="col">'+fmt(c)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+cols.map((_,i)=>'<td>'+fmt((r||[])[i])+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>'+((b.footnotes||[]).length?'<div class="table-footnotes">'+b.footnotes.map(t=>'<p>'+fmt(t)+'</p>').join('')+'</div>':'')+'</section>'}
case 'governance':{const lanes=Array.isArray(b.columns)?b.columns:[];return '<section class="section-block">'+title+(b.intro?'<p class="page-intro">'+fmt(b.intro)+'</p>':'')+'<div class="gov-model">'+lanes.map(l=>'<article class="gov-lane"><div class="gov-lane-title">'+fmt(l.title)+'</div>'+(l.text?'<p class="gov-lane-desc">'+fmt(l.text)+'</p>':'')+'<div class="gov-lane-list">'+(Array.isArray(l.items)?l.items:[]).map(x=>'<div class="gov-node"><strong>'+fmt(x.title)+'</strong>'+(x.text?'<p>'+fmt(x.text)+'</p>':'')+'</div>').join('')+'</div></article>').join('')+'</div>'+(b.caption?'<p class="gov-caption">'+fmt(b.caption)+'</p>':'')+'</section>'}
case 'timeline':return '<section class="section-block">'+title+'<div class="timeline">'+list.map(x=>'<article class="timeline-item"><span class="timeline-period">'+fmt(x.period)+'</span><h3>'+fmt(x.title)+'</h3><p>'+fmt(x.text)+'</p></article>').join('')+'</div></section>';
case 'image':return '<figure class="section-block source-figure">'+title+(/^data:image\/(png|jpeg|gif|webp);base64,/.test(b.src||'')?'<button type="button" class="image-enlarge" aria-label="Enlarge image: '+esc(b.title)+'"><img src="'+esc(b.src)+'" alt="'+esc(b.alt)+'" loading="eager"></button>':'')+(b.caption?'<figcaption>'+fmt(b.caption)+'</figcaption>':'')+'</figure>';
case 'resources':return '<section class="section-block resources">'+title+'<ul>'+list.map(x=>{const u=validHref(x.url);return '<li>'+(u?'<a href="'+esc(u)+'" target="_blank" rel="noopener noreferrer">'+fmt(x.title)+'</a>':fmt(x.title))+(x.note?'<small>'+fmt(x.note)+'</small>':'')+'</li>'}).join('')+'</ul></section>';
case 'glossary':return '<section class="section-block">'+title+'<dl class="glossary">'+list.map(x=>'<div><dt>'+fmt(x.term)+'</dt><dd>'+fmt(x.definition)+'</dd></div>').join('')+'</dl></section>';
default:return ''}}

function mainHtml(p,i){const blocks=Array.isArray(p.blocks)?p.blocks:[];
 const contents=blocks.length>4?'<details class="page-contents"><summary>On this page</summary><ul>'+blocks.map((b,j)=>'<li><a href="#'+esc(id(p)+'#'+blockId(b,j))+'">'+fmt(b.title||b.label)+'</a></li>').join('')+'</ul></details>':'';
 return '<section class="page" id="page-'+esc(id(p))+'" aria-labelledby="title-'+esc(id(p))+'"><h1 id="title-'+esc(id(p))+'" tabindex="-1">'+fmt(p.title)+'</h1>'+(p.intro?'<p class="page-intro">'+fmt(p.intro)+'</p>':'')+contents+blocks.map((b,j)=>'<div id="'+esc(sectionId(id(p),blockId(b,j)))+'" tabindex="'+(editPreview?'0':'-1')+'"'+(editPreview?' class="rf-edit-zone" data-rf-block="'+j+'"':'')+'>'+renderBlock(b)+'</div>').join('')+'<div class="page-footer">'+(i?'<a class="footlink" href="#'+esc(id(pages[i-1]))+'"><span class="foot-label">Previous</span><span class="footname">← '+fmt(pages[i-1].title)+'</span></a>':'<span></span>')+(i<pages.length-1?'<a class="footlink" href="#'+esc(id(pages[i+1]))+'"><span class="foot-label">Next</span><span class="footname">'+fmt(pages[i+1].title)+' →</span></a>':'')+'</div></section>'}
const children=new Map();pages.forEach(p=>{const parent=pageById.has(p.parent)&&p.parent!==p.id?p.parent:'';if(!children.has(parent))children.set(parent,[]);children.get(parent).push(p)});
function navHtml(parent='',seen=new Set()){
 return (children.get(parent)||[]).filter(p=>!seen.has(p.id)).map(p=>{const branch=new Set(seen);branch.add(p.id);const link='<a href="#'+esc(id(p))+'">'+fmt(p.title)+'</a>';
 return children.has(p.id)?'<details class="nav-group" data-parent="'+esc(id(p))+'"><summary><span>'+fmt(p.title)+'</span></summary><div class="nav-children">'+link+navHtml(p.id,branch)+'</div></details>':link}).join('')
}
$('brand').textContent=data.meta?.title||'Reference Guide';$('subtitle').textContent=data.meta?.subtitle||'';document.title=data.meta?.title||'Reference Guide';
$('main').innerHTML=pages.map(mainHtml).join('');$('nav').innerHTML=navHtml();
let currentTarget=editPreview?initialPageId:null;
function readTarget(){try{return decodeURIComponent(location.hash.slice(1))}catch{return ''}}
function select({focus=false}={}){
 const target=currentTarget||readTarget(),parts=target.split('#');const pid=pageById.has(parts[0])?parts[0]:id(pages[0]||{});
 document.querySelectorAll('.page').forEach(el=>el.classList.toggle('active',el.id==='page-'+pid));
 document.querySelectorAll('#nav a').forEach(a=>{if(a.getAttribute('href')==='#'+pid){a.setAttribute('aria-current','page');let ancestor=a.parentElement;while(ancestor&&ancestor!==$('nav')){if(ancestor.tagName==='DETAILS')ancestor.open=true;ancestor=ancestor.parentElement}}else a.removeAttribute('aria-current')});
 const title=pageById.get(pid)?.title||'Contents';$('nav-toggle').textContent=title;$('nav-toggle').setAttribute('aria-expanded','false');$('nav').classList.remove('mobile-open');
 $('search-panel').classList.remove('visible');
 const section=parts[1]&&$(sectionId(pid,parts[1]));
 if(section){section.scrollIntoView({block:'start'});if(focus)section.focus({preventScroll:true})}
 else{window.scrollTo(0,0);if(focus)$('title-'+pid)?.focus({preventScroll:true})}
 notifyStudio('page',{pageId:pid});if(section){const blockIndex=pageById.get(pid).blocks.findIndex((b,i)=>blockId(b,i)===parts[1]);notifyStudio('block',{pageId:pid,blockIndex})}
}
function go(target){if(!targetExists(target))return;if(editPreview||location.protocol==='about:'){currentTarget=target;select({focus:true})}else if(readTarget()===target)select({focus:true});else location.hash=target}
$('nav-toggle').addEventListener('click',()=>{const expanded=$('nav-toggle').getAttribute('aria-expanded')!=='true';$('nav-toggle').setAttribute('aria-expanded',String(expanded));$('nav').classList.toggle('mobile-open',expanded)});
document.addEventListener('click',e=>{
 const imageButton=e.target.closest('.image-enlarge');if(imageButton){const source=imageButton.querySelector('img');let dialog=$('image-viewer');if(!dialog){dialog=document.createElement('dialog');dialog.id='image-viewer';dialog.className='image-viewer';dialog.innerHTML='<button type="button">Close image</button><img alt="">';dialog.querySelector('button').addEventListener('click',()=>dialog.close());document.body.append(dialog)}dialog.querySelector('img').src=source.src;dialog.querySelector('img').alt=source.alt;dialog.showModal()}
 const a=e.target.closest('a[href^="#"]');if(a){e.preventDefault();go(a.getAttribute('href').slice(1));return}
 if(editPreview){const block=e.target.closest('[data-rf-block]');if(block){const active=block.closest('.page');notifyStudio('block',{pageId:active.id.slice(5),blockIndex:Number(block.dataset.rfBlock)});document.querySelectorAll('.rf-selected').forEach(el=>el.classList.remove('rf-selected'));block.classList.add('rf-selected')}}
});
window.addEventListener('hashchange',()=>{if(!editPreview)currentTarget=null;select({focus:true})});
if(editPreview){window.addEventListener('message',e=>{if(e.source!==window.parent)return;const m=e.data;if(!m||m.source!=='refract-studio'||m.type!=='select')return;
 if(m.pageId&&pageById.has(m.pageId)){currentTarget=m.pageId;select()}
 document.querySelectorAll('.rf-selected').forEach(el=>el.classList.remove('rf-selected'));
 if(Number.isInteger(m.blockIndex)){const b=document.querySelector('#page-'+CSS.escape(m.pageId||String(currentTarget).split('#')[0])+' [data-rf-block="'+m.blockIndex+'"]');if(b){b.classList.add('rf-selected');b.scrollIntoView({block:'nearest'})}}
 });document.addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&e.target.matches('[data-rf-block]')){e.preventDefault();e.target.click()}})}
function visibleText(value){if(typeof value==='string')return value.replace(/\[\[(?:[^|\]]+\|)?([^\]]+)\]\]/g,'$1');if(Array.isArray(value))return value.map(visibleText).join(' ');if(value&&typeof value==='object')return Object.entries(value).filter(([k])=>!['id','type','parent','link','url','src'].includes(k)).map(([,v])=>visibleText(v)).join(' ');return ''}
const records=[];pages.forEach(p=>{records.push({target:p.id,title:p.title,context:'Page',text:[p.title,p.intro||''].join(' ')});p.blocks.forEach((b,i)=>records.push({target:p.id+'#'+blockId(b,i),title:b.title||b.label,context:p.title,text:visibleText(b)}))});
function marked(text,tokens){const pattern=new RegExp(tokens.map(t=>t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('|'),'ig');let out='',last=0;for(const m of text.matchAll(pattern)){out+=esc(text.slice(last,m.index))+'<mark>'+esc(m[0])+'</mark>';last=m.index+m[0].length}return out+esc(text.slice(last))}
function search(){const q=$('search').value.trim().toLowerCase();if(!q){$('search-panel').classList.remove('visible');return}const tokens=[...new Set(q.split(/\s+/))];
 const terms=gloss.filter(g=>tokens.every(t=>(g.term+' '+g.definition).toLowerCase().includes(t))).slice(0,4);
 const hits=records.filter(r=>tokens.every(t=>r.text.toLowerCase().includes(t))).map(r=>({...r,score:r.title.toLowerCase()===q?3:r.title.toLowerCase().includes(q)?2:1})).sort((a,b)=>b.score-a.score);
 const glossaryPage=pages.find(p=>p.blocks.some(b=>b.type==='glossary'));
 const termHtml=terms.map(g=>{const content='<span class="search-type">Term</span><strong>'+marked(g.term,tokens)+'</strong><small>'+marked(g.definition,tokens)+'</small>';return glossaryPage?'<a href="#'+esc(glossaryPage.id)+'">'+content+'</a>':'<div class="search-term">'+content+'</div>'}).join('');
 $('search-panel').innerHTML=termHtml+hits.slice(0,20-terms.length).map(r=>{const at=Math.min(...tokens.map(t=>r.text.toLowerCase().indexOf(t)).filter(n=>n>=0));const start=Math.max(0,at-65),snippet=(start?'…':'')+r.text.slice(start,start+210)+(start+210<r.text.length?'…':'');return '<a href="#'+esc(r.target)+'"><span class="search-type">'+esc(r.context)+'</span><strong>'+marked(r.title,tokens)+'</strong><small>'+marked(snippet,tokens)+'</small></a>'}).join('')+(!terms.length&&!hits.length?'<p>No matching content</p>':hits.length>20-terms.length?'<p>Showing the first '+(20-terms.length)+' of '+hits.length+' section and page matches. Refine your search.</p>':'');
 $('search-panel').classList.add('visible')
}
$('search').addEventListener('input',search);
$('search-panel').addEventListener('click',e=>{if(e.target.closest('a')){$('search').value='';$('search-panel').classList.remove('visible')}});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){$('search-panel').classList.remove('visible');$('search').focus();return}if(!['ArrowDown','ArrowUp'].includes(e.key)||!$('search-panel').classList.contains('visible'))return;
 const links=[...$('search-panel').querySelectorAll('a')];if(e.target!==$('search')&&!links.includes(e.target))return;e.preventDefault();const index=links.indexOf(document.activeElement),step=e.key==='ArrowDown'?1:-1;links[(index+step+links.length)%links.length]?.focus()
});
$('print').addEventListener('click',()=>window.print());select();
})();
