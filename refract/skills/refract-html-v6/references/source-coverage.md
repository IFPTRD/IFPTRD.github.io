# Source coverage and document replacement review

## Principle

Refract's default is **source-equivalent re-presentation**: a better organized and accessible substitute for the full document, not an additional summary or generic guidance layered onto it. Preserve scope, genre, intended function, distinctions, and document-specific substance. "Simplify" means make the material clear and navigable, not omit large sections.

## Meeting e-binders: what to retain

A binder usually warrants a meeting-focused home page with actual meeting identity, date, time, location and agenda **where specified**; then pages for each meaningful agenda item or issue with its associated briefings, factual background, existing recommendations/positions, requested decisions, discussion material **if the source actually contains it**, and references. Keep annex material accessible through nested pages and links. Do not create new interventions, coaching on handling difficult exchanges, talking points or tactical advice absent from the source. Do not substitute a "What to say" page for the actual issue-specific briefing notes.

Example structure (conditional):
- **Meeting** — actual schedule, attendees, purpose and agenda; do not invent missing meeting logistics
  - **Agenda item A** — source briefing note, background, issue, evidence, options, required action where available
  - **Agenda item B** — its own distinct briefing and supporting material
  - **Supporting documents** — annexes, reference tables, attachments, glossary as relevant

The HTML should let the reader operate using *only this guide*. That means the main detail lives inside the pages rather than being replaced by links back to the original document. Use links for actual independent resources and originals that require exact reproduction.

## Inventory before drafting

For each substantive content unit create one entry with:
- `id`: unique stable string
- `heading`: source section or agenda / issue / annex title
- `kind`: descriptive kind such as `agenda`, `issue-brief`, `meeting`, `annex`, `reference`, `procedure`, `section`
- `target_page_ids`: at least one actual page ID where the information is represented
- `status`: `included`, `merged`, or `excluded`
- `reason`: required only when excluded; exclusion is limited to duplicates, blank/noninformative material, or user-explicitly out-of-scope content

Inventory file example (private intermediate, not embedded in or automatically appended to the public reader-facing guide):

```json
{
  "source_title": "Example source document",
  "units": [
    {"id":"agenda","heading":"Agenda","kind":"agenda","status":"included","target_page_ids":["meeting-agenda"]},
    {"id":"issue-a","heading":"Issue A briefing note","kind":"issue-brief","status":"included","target_page_ids":["issue-a"]},
    {"id":"annex","heading":"Supporting Annex","kind":"annex","status":"merged","target_page_ids":["supporting-references"]}
  ]
}
```

Create the inventory by reading the source, not by relying only on an extracted TOC or model guesses. If there are many nested notes, inventory them separately. Output `guide.json` with the agreed Refract schema; do **not** inject inventory fields into the guide's root or reader-facing text.

Run:

```bash
python scripts/check_coverage.py source-inventory.json guide.json
python scripts/validate_refract.py guide.json
python scripts/render_refract.py guide.json --output guide.html --fail-on-warnings
```

The coverage script checks missing mappings, duplicate IDs, unsupported exclusions and references to nonexistent pages. **It cannot verify the completeness of an inventory that the model itself created**, nor prove that every fact in an assigned section was preserved. Independently cross-check source section headings, briefing details, meeting agenda items, numbers, dates, attachments and necessary nuance. Don't falsely claim full fidelity when source figures or files were not transferred.

For long material, work in chunks and assemble a complete guide before rendering. If the model/tool environment cannot access all pages, treat that as incomplete rather than silently dropping material.
