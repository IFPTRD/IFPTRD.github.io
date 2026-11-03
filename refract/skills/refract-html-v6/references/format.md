# Refract structured content format — adaptive guides

The JSON is an internal interchange format used to generate a complete standalone HTML guide. It is not normally delivered to users.

The root object is `{"meta":{"title":"...","subtitle":"...","audience":"..."},"pages":[...],"glossary":[]}`. Pages are ordered as intended in navigation and have unique `id` (lowercase words separated by hyphens), `title`, optional `intro`, optional `parent` referencing another page, and `blocks`.

| Block | Fields | Best used for |
| --- | --- | --- |
| hero | type, title, text, optional kicker | A meaningful opening, only if needed |
| paragraph | type, title, text | Explanations and narrative |
| note | type, label, text | Critical exception, constraint or qualification |
| checks | type, title, items: [{title, detail}] | Real verification criteria or decision checks |
| cards | type, title, items: [{title, text, link?}] | Brief, distinct concepts or navigation |
| steps | type, title, items: [{title, text}] | A real ordered process or procedure |
| bullets | type, title, items: [string] | Short related points |
| table | type, title, columns: [string], rows: [[string]] | Comparisons and lookup data |
| resources | type, title, items: [{title, url, note?}] | Genuine source-provided HTTP(S) links |
| glossary | type, title, items: [{term, definition}] | Specialized terms |
| governance | type, title, intro?, columns: [{title,text?,items:[{title,text?}]}], caption? | Grounded multi-actor or multi-level responsibilities |
| timeline | type, title, items: [{period,title,text}] | Source-grounded chronology or staged sequence |

Top-level glossary is an array of `{term,definition}` objects. `[[TERM]]` in prose can expose hover definitions.

All table rows have exactly as many string cells as the table's columns. Every card `link` and page `parent` references an actual page ID. Do not invent URLs, chronology, actor relationships or numerical data. Use unlinked `bullets` for named resources without actual URLs.

The renderer and Studio editor share these block types. Layout choices are content-led and must match the source, not a fixed executive example.
