---
name: refract-guide-authoring
description: Convert documents supplied by a user into a polished, task-oriented, standalone Refract HTML guide, using the packaged fixed renderer and structured content schema. Use for executive playbooks, decision aids, field guides, reference tools, operating manuals and similar interactive guides. Deliver downloadable HTML and preserve full Refract Studio editability.
---

# Refract Guide Authoring — v5

## Primary contract

When the user attaches or selects accessible source document(s) and requests a guide, read them and create a **finished, downloadable, standalone HTML file**, not a JSON response. Generate valid Refract JSON internally, validate it, and run the packaged Python HTML renderer. Never write HTML/CSS/JavaScript freehand, never produce a Word/PDF substitute, and never narrate your plan or implementation. If file execution is unavailable, provide valid JSON in one `json` code fence with a brief explanation that HTML file delivery is unavailable; never pretend to have created a file.

Never publish user documents or generated guides to GitHub. The public Refract builder and this reusable skill contain **only generic code and design rules**. Follow the organization's information-handling controls; the tool's public source code does not make generated material public.

## Information architecture — the most important quality requirement

**Your task is to design the reader's working interface, not merely reformat or summarize the source document.** Read source documents fully. Identify the actual audience, their prior expertise, what decisions or actions they must take, and which material is reference-only. Distinguish the source's facts from assumptions and unconfirmed proposals.

1. **Start with the reader's job.** For a senior decision-maker, the first page should usually state the practical role, 3–6 priorities, and the operational context in concise language, followed by a compact decision aid. Do not start with a generic introduction or a sprawling table of contents if the source supports a more useful opening.
2. **Structure around lookup tasks.** Give distinct pages to materially different uses: role, decision aid, governance, responsibilities, escalation, exercise/program design, timeline, partner capabilities, and references *only when supported by the documents*. Use short navigation labels and nested pages (`parent`) for detail. Order by what readers will consult most. Do not mechanically copy annex/chapter headings into pages.
3. **Short, purposeful pages.** Prefer a useful hierarchy of focused pages over a few overloaded pages or dozens of thin ones. A page should generally address one question or task; long technical tables and detailed legislative references belong deeper in the hierarchy. Do not impose a fixed page count.
4. **Avoid generic extraction artifacts.** Never generate repeated headings like "Context", "Considerations", "Quick reference", or one-item bullet blocks for every sentence. Merge related ideas into coherent paragraphs, tables or concise multi-item lists, with specific headings. Do not create duplicate pages/blocks.
5. **Selective components.** Use executive `checks` for short decision tests, `cards` mainly for meaningful navigation and concise peer concepts, `steps` for real procedures, and `table` when columns materially help comparison. Use `timeline` for chronological stages; use `governance` for a genuine multi-actor or multi-level structure. Do not invent a diagram when the source lacks a model. Use `note` sparingly for truly important boundaries or exceptions.
6. **Respect the reader's experience.** Avoid patronizing reminders, basic explanations of familiar legal/clinical distinctions, generic questions, long disclaimers, or verbose scene-setting. Make precise, concrete and complete statements; preserve mandates, uncertainty, dependencies, decision rights and implementation responsibilities.
7. **Differentiate established from proposed.** Do not claim a proposed governance model is active/authorized unless established in the material. Explain what the exercise, project or policy is actually testing when relevant. Avoid treating coordination as transferred authority.
8. **Faithfulness and privacy.** Never invent names, clinical decisions, dates, plans, powers, URLs, causal claims or source images. Keep unresolved issues clear. Use original resource links as provided only when functional. When scenario information is not meant for participant distribution, omit specific unreleased injects and preserve broad topics only where authorized.

## Editorial exclusions

Do not automatically add any reader-facing "Sources", "Source and distribution", "Based on [filename]", "Generated from", "Document provenance", "Unclassified / Non classifié", model/process description, public/private sharing caution, or verification-status note. Do not put these into page intros, metadata, blocks, footnotes or a references page. Keep **functional reference links** and substantive decision-relevant legal/authority limits as needed. Add formal attribution only when the user requests it.

## Design system and supported content

The packaged renderer implements Refract's polished executive design: light header, quiet nested navigation, measured typography, compact tables, accessible interactive search, named previous/next pages, mobile layouts and thoughtful print rules. Do not choose custom colours or manually insert HTML to force visual styling. Use structured blocks to communicate meaning.

Read `references/format.md`, `references/refract-schema.json`, and `references/design-standard.md`. The JSON root has `meta`, `pages`, and `glossary`. Pages have unique lowercase-hyphenated IDs, `title`, optional `intro`, optional `parent`, and `blocks`.

Supported blocks: `hero`, `paragraph`, `note`, `checks`, `cards`, `steps`, `bullets`, `table`, `resources`, `glossary`, `governance`, `timeline`. The last two are special layouts:

- `governance`: `{ "type":"governance", "title":"Proposed Governance", "intro":"...", "columns":[{"title":"Strategic direction","text":"...","items":[{"title":"Decision forum","text":"Role"}]}], "caption":"Illustrative model" }`. Use 2–4 columns only when justified by the source; usually 3.
- `timeline`: `{ "type":"timeline", "title":"Incident Timeline", "items":[{"period":"Month 1","title":"Initial response","text":"..."}] }`. Use chronology only where dates or stages are genuinely supported.

Use `checks.items` as objects of `{title, detail}`; `bullets.items` as strings; `note.label` instead of `note.title`; and only real source-provided URLs in `resources.items` (otherwise use bullets). Never include Markdown escaping such as `\[` outside strings. Link cards and page parents to existing page IDs. Use `[[TERM]]` for hover glossary definitions as appropriate.

## Production workflow

1. Read all accessible source files and create a concise page plan based on the intended reader. Preserve source terminology and cross-document consistency. If source access is missing, report it rather than invent content.
2. Generate a complete valid Refract JSON file internally (for example `guide.json`). It must be standard JSON, not Markdown or Python dictionary syntax. Resolve the editor's content hierarchy and real external links.
3. If code execution is available, run:
   - `python scripts/validate_refract.py guide.json` — inspect all errors and editorial warnings; revise until validated.
   - `python scripts/render_refract.py guide.json --output guide.html --fail-on-warnings` — create the standalone HTML using the packaged `references/guide-template.html`.
4. Verify the HTML file exists, contains `id="guide-data"`, and opens as a usable guide. When available, test page navigation, links, search, narrow widths and print rendering. Return the **downloadable HTML file** with one concise sentence. Users can import the file into Refract Studio for subsequent editing.
5. If code execution or file downloads are unavailable, do not claim success. Return one complete `json` code block as a fallback and explain in a sentence why direct HTML delivery could not be used.

## Output quality gate (silent)

Before sending: is the first page genuinely useful for the intended reader; are the sections coherent and sufficiently differentiated; are repeated generic headings eliminated; is the governance/timeline structure faithful; are technical references grouped as reference material; are all source claims grounded; are URL strings unchanged; has all unwanted provenance boilerplate been omitted; does JSON validate; does the HTML remain editable, printable, searchable, responsive and self-contained? Correct any deficiency before delivering.