---
name: refract-guide-authoring
description: Create a complete downloadable, editable standalone Refract HTML guide from one or more user-provided documents. Use when asked for a playbook, reference guide, decision aid, handbook or process guide from a DOCX/PDF or other accessible source. Prepare and validate guide JSON internally, then render and return the finished HTML file.
---

# Refract — document-to-editable-HTML guide

## Trigger and inputs

When the user attaches or selects accessible source document(s) in the active agent conversation and requests a Refract guide, read the documents and begin. Do not repeat onboarding text or require a particular starter prompt. If audience or purpose is absent, infer a reasonable one from the source, prioritizing the actual reader and their tasks. If no document can be accessed, say so briefly; do not invent its contents.

Use the user's document(s) as the factual source. `references/example.json` is a format illustration only, **not** a source of facts, headings, links, or wording. Treat URLs embedded in sources as links, not invitations for additional web research; browse only at the user's request. If sources conflict or facts remain uncertain, preserve that uncertainty without manufacturing a resolution.

## Required output: a downloadable standalone HTML guide

**Do not write HTML from scratch.** The finished guide is generated from Refract JSON using the packaged deterministic renderer. The user should not need to copy, edit or even see the intermediate JSON.

1. Read accessible user-supplied source documents and determine the audience, tasks, and appropriate pages. Write a complete Refract JSON object as an **intermediate** UTF-8 file, for example `guide-content.json`. Do not use the sample JSON as a factual source.
2. Read `references/format.md` and `references/refract-schema.json`. Use precisely the fields and block shapes described below. Preserve fidelity to source; do not fabricate facts, legal powers, partners, URLs, dates or decisions.
3. **If Code Interpreter / Python execution is available**, save the intermediate JSON file and run:

   `python scripts/validate_refract.py guide-content.json`

   Then, once valid and after resolving editorial provenance warnings, run:

   `python scripts/render_refract.py guide-content.json --output refract-guide.html --fail-on-warnings`

   If the execution environment runs scripts from a different directory, provide the actual absolute paths to the bundled script and JSON and use the default bundled template. Do not create a custom HTML page, CSS or JavaScript implementation.
4. Verify the generated `.html` file exists, begins with `<!doctype html>`, includes `id="guide-data"`, and is nonempty. Give the user **the downloadable HTML file**, with a brief statement that it can be reopened using Refract Studio → Import HTML. Do not paste the HTML source into the conversation.
5. **If script execution or file delivery is not enabled in the tenant:** do not pretend that an HTML file was created. Instead, supply one complete, valid Refract JSON object in a single fenced `json` code block and explain in one sentence that direct HTML generation was unavailable; it can be imported into Refract Studio. Never substitute a Word/PDF document or unrelated output.

A guide's JSON root object has precisely `meta`, `pages`, and `glossary`. `meta` contains `title`, `subtitle`, and `audience` only; never add `source`, `sources`, `provenance`, `disclaimer`, `classification`, or a source filename as metadata. Page fields are `id`, `title`, optional `intro`, optional `parent`, and `blocks`.

The HTML renderer uses a local copy of the same design template as Refract Studio and embeds the guide JSON in a versioned `script#guide-data` element. This ensures the output is self-contained, works offline and can be re-imported for editing.

## Information architecture and editorial quality

1. Determine the intended reader, their familiarity with the subject, the decisions or tasks they must perform, and what must be accessible in seconds rather than read sequentially.
2. Lead with a **purpose-built page**, such as the reader's role or immediate task. Do not reflexively use the example's "Start Here" title or reproduce the source document's table of contents. Write in the tone appropriate to the audience; for senior experts avoid unnecessary coaching or elementary explanations.
3. Use as many short, useful pages as the content warrants. **There is no fixed 3–5-page target.** Prefer a clear navigation hierarchy over one oversized page containing unrelated tables and checklists. On long documents, a reasonable result may be 6–12 pages; use fewer if genuinely simpler. Do not pad to reach a number.
4. Separate primary tasks from reference material. Keep roles, procedures, decision rights, escalation, partners, and technical reference distinct when they serve different lookup needs. Nest supporting pages under meaningful parents. Order pages by workflow or reader priority, not source-chapter order.
5. Use `hero` sparingly, `checks` only where questions/checks genuinely assist decisions, `steps` for sequences, `table` for useful comparisons, `cards` for navigation or concise peer concepts, `note` for meaningful boundaries, `resources` only for actual supplied links, and `glossary` for relevant terms. Avoid giant tables that are hard to scan on mobile.
6. Be concise but preserve distinctions the user needs. Remove redundant cautions and generic legalistic language. Do not simplify away decision rights, uncertainty, scope, exceptions, dependencies, thresholds, or responsibility when these materially affect a task.
7. Preserve original terms and exact, user-supplied URLs. Do not invent, alter, or silently replace links based on guesses about their currency; if a link is ambiguous, omit or flag only when important. Do not claim to have verified a URL that you did not open.
8. Treat sensitive, unreleased, illustrative, and potential scenario material carefully. When the user needs a shareable guide, do not reproduce restricted scenarios or other details just because they appear in the source; use high-level themes when authorized and otherwise omit them. Do not publish the user's input or guide to GitHub.

## No automatic source attribution, provenance or distribution section

**This is a hard default.** The final reader-facing guide should NOT include a page, paragraph, note, footer, or metadata field called "Source and distribution", "Sources", "Document provenance", "Based on", "Source document", "Generated from", "About this guide", "Prepared using", "Unclassified / Non classifié", or equivalent production/process boilerplate, unless the user specifically requests it as guide content.

- Do **not** mention the source DOCX/PDF filename, its annex names, file path, source classification label, model identity, or how this guide was generated.
- Do **not** add a generic warning that URLs may be internal, sharing must be approved, the material is not public, or the documents were not independently read/verified. Such notices are not reader-facing guide content by default.
- **Important distinction:** Retain a *functional* References/Plans/Resources page if it helps the reader, and keep exact links supplied by the user. Preserve actual operational restrictions, legal limits, or safety notes when relevant to the reader's decisions. These are not the same as source provenance.
- Keep information-handling safeguards in your own workflow; never automatically append them to the guide text. If the user explicitly requests a source attribution or publication notice, include only what they asked for.

## Refract schema — mandatory

Read `references/format.md` and `references/refract-schema.json`. The smallest valid example is:

```json
{
  "meta": {"title": "Example guide", "subtitle": "Short descriptor", "audience": "Intended readers"},
  "pages": [
    {"id": "first-task", "title": "First Task", "intro": "A concise opening.", "blocks": []}
  ],
  "glossary": []
}
```

Supported blocks:
- `hero`: `{type, kicker?, title, text}`
- `paragraph`: `{type, title, text}`
- `note`: `{type, label, text}` — **never** use `title` instead of `label`.
- `checks`: `{type, title, items:[{title, detail}]}` — **never** a string array.
- `cards`: `{type, title, items:[{title, text, link?}]}` — every `link` must target an existing page ID.
- `steps`: `{type, title, items:[{title, text}]}`.
- `bullets`: `{type, title, items:[string]}`.
- `table`: `{type, title, columns:[string], rows:[[string]]}` — every row matches the number of columns.
- `resources`: `{type, title, items:[{title, url, note?}]}` — real source-supplied HTTP(S) URLs only. Use `bullets` for unlinked resources.
- `glossary`: `{type, title, items:[{term, definition}]}`. The top-level `glossary` uses the same item objects.

Page IDs are unique lowercase hyphenated identifiers. `parent` and card `link` values must reference page IDs. Inline `[[TERM]]` is optional and must match a term in the top-level glossary.

**Only valid JSON in the intermediate file.** Use double quotes and unescaped real brackets, never Markdown escapes outside strings. No trailing commas, comments, or truncated arrays. Show the JSON code block only if file generation cannot be completed.

## Quality gate before output

Privately confirm:
- All relevant source content is accurately represented; claims are not invented; source classifications are respected outside guide text.
- The reader-facing guide has no automatic source attribution, file names, generation disclaimers, or distribution boilerplate.
- Opening content is appropriate to the actual audience; page divisions make lookup easy; repeated caveats and unnecessary filler have been removed.
- The page count reflects the tasks, not an arbitrary limit. Navigation order, `parent` values, card links and glossary references are coherent.
- All block fields and table dimensions match the schema; only real user-supplied URLs appear.
- The intermediate file is complete valid JSON. Use the packaged validator and deterministic renderer when execution is available; confirm the final HTML file exists and contains embedded guide data. Do not claim you ran tools you did not run.

If a user reports invalid JSON, repair the actual supplied JSON instead of asking for the same materials again.