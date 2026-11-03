# Refract format v1

The intermediate JSON is never the primary user-facing deliverable. It is validated and rendered to standalone HTML using scripts/render_refract.py.

Root: `{"meta":{"title":"...","subtitle":"...","audience":"..."},"pages":[...],"glossary":[]}`.

Pages have a unique kebab-case `id`, a `title`, an optional `intro`, an optional `parent` referring to an existing ID, and `blocks`. Their order determines sidebar and printed order. Each card link must reference an existing page id.

Allowed block shapes:

- hero: `{"type":"hero","kicker":"...","title":"...","text":"..."}`
- paragraph: `{"type":"paragraph","title":"...","text":"..."}`
- note: `{"type":"note","label":"...","text":"..."}` (not title)
- checks: `{"type":"checks","title":"...","items":[{"title":"...","detail":"..."}]}`
- cards: `{"type":"cards","title":"...","items":[{"title":"...","text":"...","link":"existing-page-id"}]}`
- steps: `{"type":"steps","title":"...","items":[{"title":"...","text":"..."}]}`
- bullets: `{"type":"bullets","title":"...","items":["..."]}`
- table: `{"type":"table","title":"...","columns":["..."],"rows":[["..."]]}` (equal cells per row)
- resources: `{"type":"resources","title":"...","items":[{"title":"...","url":"https://verified-link","note":"..."}]}`
- glossary: `{"type":"glossary","title":"...","items":[{"term":"...","definition":"..."}]}`

Top-level glossary is an array of `{"term":"...","definition":"..."}` entries. Use `[[TERM]]` in prose to provide hover definitions. Avoid invented URLs. For unlinked documents use bullets.

Never include source filenames, classification statements or process attribution in the reader-facing guide unless expressly requested. Retain genuine reader-relevant reference links and authority constraints.

Generated HTML contains `<script type="application/json" id="guide-data">` with embedded safe JSON, and meta tag `refract-format-version=1`. Refract Studio can import and re-edit it. Direct export is one HTML file, no external libraries.
