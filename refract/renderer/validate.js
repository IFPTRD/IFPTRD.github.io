// Schema is embedded from the same source used by the Python validator.
function validate(data){
 const errors=[],warnings=[];
 const error=(path,message)=>errors.push(path+': '+message);
 function walk(value,schema,path){
  if(schema.oneOf){const branch=schema.oneOf.find(s=>value&&s.properties?.type?.const===value.type);if(branch)walk(value,branch,path);else error(path+'.type','unsupported or missing block type');return}
  const type=schema.type;
  if(type==='object'&&(!value||typeof value!=='object'||Array.isArray(value))||type==='array'&&!Array.isArray(value)||type==='string'&&typeof value!=='string'){error(path,'expected '+type);return}
  if('const' in schema&&value!==schema.const)error(path,'unexpected value');
  if(type==='object'){const props=schema.properties||{};for(const key of schema.required||[])if(!(key in value))error(path+'.'+key,'required field');for(const [k,v]of Object.entries(value)){if(props[k])walk(v,props[k],path+'.'+k);else if(schema.additionalProperties===false)error(path+'.'+k,'unsupported field; move its content to a supported field or block')}}
  if(type==='array'){if(value.length<(schema.minItems||0))error(path,'too few items');if(schema.maxItems!==undefined&&value.length>schema.maxItems)error(path,'too many items');value.forEach((v,i)=>walk(v,schema.items||{},path+'['+i+']'))}
  if(type==='string'&&schema.pattern&&!new RegExp(schema.pattern).test(value))error(path,'invalid format');
 }
 walk(data,refractSchema,'root');if(errors.length)return {errors,warnings};
 const ids=new Map(),anchors=new Map(),terms=new Set();
 for(const [i,p]of data.pages.entries()){
  if(ids.has(p.id))error('pages['+i+'].id','duplicate page ID');ids.set(p.id,p);
  if(!p.title.trim())error('pages['+i+'].title','must not be blank');
  const seen=new Set();p.blocks.forEach((b,j)=>{const key=b.id||'section-'+(j+1);if(seen.has(key))error('pages['+i+'].blocks','duplicate section ID '+key);seen.add(key)});anchors.set(p.id,seen);
 }
 if(!data.meta.title.trim())error('meta.title','must not be blank');
 data.glossary.forEach((g,i)=>{if(!g.term.trim()||!g.definition.trim())error('glossary['+i+']','term and definition must not be blank');const term=g.term.trim().toLowerCase();if(terms.has(term))error('glossary['+i+']','duplicate term');terms.add(term)});
 const targetOk=t=>{const [pid,...rest]=t.split('#');return ids.has(pid)&&(!rest.length||rest.length===1&&anchors.get(pid).has(rest[0]))};
 const textStrings=value=>typeof value==='string'?[value]:Array.isArray(value)?value.flatMap(textStrings):value&&typeof value==='object'?Object.entries(value).filter(([k])=>!['id','type','parent','link','url','src'].includes(k)).flatMap(([,v])=>textStrings(v)):[];
 for(const [i,p]of data.pages.entries()){
  const path='pages['+i+']';if(p.parent){if(!ids.has(p.parent))error(path+'.parent','unknown parent page');const seen=new Set([p.id]);let cursor=p.parent;while(ids.has(cursor)){if(seen.has(cursor)){error(path+'.parent','parent cycle');break}seen.add(cursor);cursor=ids.get(cursor).parent}}
  if(!p.blocks.length&&!data.pages.some(x=>x.parent===p.id))warnings.push(path+': empty page; add substantive content or use as a parent group');
  p.blocks.forEach((b,j)=>{const loc=path+'.blocks['+j+']';for(const k of ['title','label','text'])if(k in b&&!b[k].trim())error(loc+'.'+k,'must not be blank');
   if(b.type==='table'){if(!b.columns.length)error(loc+'.columns','requires at least one column');b.rows.forEach((row,n)=>{if(row.length!==b.columns.length)error(loc+'.rows['+n+']','cell count differs from columns')})}
   if(b.type==='governance'&&(b.columns.length<2||b.columns.length>4))error(loc+'.columns','requires 2–4 columns');
   if(b.type==='image'){let valid=false;try{const m=b.src.match(/^data:image\/(png|jpeg|gif|webp);base64,([A-Za-z0-9+/]+={0,2})$/);if(m){const raw=atob(m[2]);valid={png:raw.startsWith('\x89PNG\r\n\x1a\n'),jpeg:raw.startsWith('\xff\xd8\xff'),gif:/^GIF8[79]a/.test(raw),webp:raw.startsWith('RIFF')&&raw.slice(8,12)==='WEBP'}[m[1]]}}catch{}if(!valid||!b.alt.trim())error(loc,'image needs descriptive alt text and an embedded PNG/JPEG/GIF/WebP data URL')}
   for(const [k,item]of (b.items||[]).entries()){if(!item||typeof item!=='object')continue;for(const key of ['title','text','detail','term','definition','period'])if(key in item&&!item[key].trim())error(loc+'.items['+k+'].'+key,'must not be blank');
    if(b.type==='cards'&&item.link&&!targetOk(item.link))error(loc+'.items['+k+'].link','unknown page or section');
    if(b.type==='resources'){try{const u=new URL(item.url);if(!/^https?:$/.test(u.protocol)||!u.hostname||u.username||u.password||/[\s<>"\\]/.test(item.url))throw Error()}catch{error(loc+'.items['+k+'].url','requires a complete HTTP(S) URL with a hostname')}}
   }
   if(/^(source and distribution|document provenance|source document|generated from|prepared using)$/i.test((b.title||b.label||'').trim()))warnings.push(path+': review generated provenance notice; retain only if requested or substantively required');
  });
  for(const text of textStrings({title:p.title,intro:p.intro||'',blocks:p.blocks}))for(const m of text.matchAll(/\[\[(.*?)\]\]/g)){const ref=m[1];if(ref.includes('|')){const at=ref.indexOf('|');if(!ref.slice(at+1).trim()||!targetOk(ref.slice(0,at)))error(path,'unresolved cross-reference '+ref)}else if(!terms.has(ref.trim().toLowerCase()))error(path,'undefined glossary term '+ref)}
 }
 return {errors,warnings};
}
