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


## Additions in generator v6.3 (format v1, backward-compatible optional fields)

Every block may have an optional stable kebab-case `id`; assign one for newly authored guides. IDs are unique within each page. Older blocks without an ID use `section-1`, `section-2`, etc.; Studio gives these IDs explicit values before reordering.

- Internal card links may target `page-id#block-id` as well as a whole page.
- Inline `[[page-id#block-id|Readable label]]` creates a section link; `[[page-id|Label]]` creates a page link. `[[TERM]]` still means a glossary definition. Do not use Markdown/HTML links in plain text fields.
- `table.footnotes` is an optional array of strings, rendered immediately below the table. Preserve source footnote markers in the relevant cells and note text.
- `image`: `{type:"image", id?:"original-chart", title:"Original chart", src:"data:image/png;base64,...", alt:"Description of information conveyed", caption?:"Original caption"}`. Use specific meaningful source visuals cropped to their relevant region; do not use whole PDF-page screenshots or images of prose/ordinary tables as conversion substitutes. PNG, JPEG, GIF and WebP are accepted. SVG, remote images and file paths are not accepted; embedded bytes keep the guide self-contained.
- Plain text line breaks are preserved. Arbitrary Markdown, HTML, nested lists, merged cells and mathematical notation are not interpreted. Do not invent schema fields to hold substantive material: unknown fields are rejected to avoid invisible content.
