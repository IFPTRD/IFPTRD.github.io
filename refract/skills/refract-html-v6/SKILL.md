---
name: refract-guide-authoring
description: Transform user-supplied documents into a polished, reader-centred, self-contained and editable Refract HTML guide. Adapt the guide's structure to the document's purpose, audience, and tasks, whether procedural, technical, educational, operational, policy, reference, or executive. Use the bundled validator and renderer; deliver downloadable HTML.
---

# Refract — Adaptive Guide Authoring (v6)

## Mission

Your goal is **not to summarize a document or recreate its table of contents**. Your goal is to use reasoning to make its information **clearer, easier to find, easier to understand, and more useful for the reader**. Create a complete standalone HTML guide using the packaged Refract renderer. The resulting HTML must remain editable through Refract Studio's Import HTML workflow.

**Do not default to an executive playbook.** That was one application, not the product's universal structure. Do not automatically add "Your Role," "Decision Aid," "Governance," "Escalation," "Incident Timeline," "Partners," or "Quick Reference." Choose those only where the source and reader's actual needs warrant them.

Read `references/adaptive-editorial.md`, `references/format.md`, `references/design-standard.md` and `references/refract-schema.json` before planning the output.

## 1. Reason from the material: private editorial plan

Read all accessible relevant source documents. Before creating guide content, silently determine:

1. **Who is this for?** Their role, familiarity, accessibility and subject knowledge. If audience is not specified, infer conservatively from the source, without inventing a narrow role.
2. **Why would someone open it?** To learn concepts, perform tasks, navigate policy, troubleshoot, make decisions, coordinate work, find facts, or prepare for an event? It may serve more than one purpose.
3. **What is essential?** Distinguish core information, actionable requirements, background, exceptions, supporting detail and reference material.
4. **What is the natural structure?** Organize by task, question, workflow, concept, topic or reference lookup. The document's existing section order is evidence, not a required website navigation structure.
5. **Which format communicates each idea best?** Plain prose, a meaningful table, steps, an accurate timeline, a genuinely supported diagram, cards or definitions. Avoid decorative components.
6. **What must never be altered or lost?** Specific facts, numbers, mandatory requirements, conditions, exceptions, version/scope distinctions, responsibilities, uncertainty and source terminology.

Select an **adaptive organizing pattern** (or combination): tutorial/onboarding, step-by-step procedure, policy/rules, conceptual explainer, reference directory, decision aid, executive briefing, technical handbook, issue/troubleshooting, project guide, study guide or timeline. The examples in `references/adaptive-editorial.md` are suggestions, not templates to copy.

If the user provides a specific audience, outcome, structure or tone, honor it. Ask a question only when a missing fact prevents a meaningful accurate guide; otherwise proceed with a sensible, noncommittal default.

## 2. Transform content through editorial judgment

- **Synthesize and simplify.** Remove duplication, combine dispersed but related facts, use clear headings, move detail to the place it will be needed, and convert difficult prose into more usable structured material where justified.
- **Preserve substance.** Do not replace nuanced source material with broad generic advice. Condense repetitive wording, not essential meanings, exceptions, caveats or dependencies.
- **Prioritize retrieval.** The opening should answer the reader's most urgent question or establish the concept needed to use the rest. It need not be a hero, role statement or checklist.
- **Allow appropriate depth.** Use focused pages and useful subpages as needed; never target an arbitrary page count, uniformly short page length or fixed block count. Complex sources can remain detailed.
- **Write for expertise.** A novice may need definitions, sequence and worked context. A specialist may need exact parameters and constraints. A senior leader may need decisions and escalation paths—but only if relevant.
- **Do not over-format.** Plain text is often best. Avoid repeated cards, one-item lists, oversized callouts, generic "Context"/"Considerations" headings and unnecessary numbered prompts.
- **Do not invent interactivity.** Navigation, search, glossaries and print are provided by Refract. Do not manufacture quizzes, calculators, forms or decision rules the source does not establish or the renderer cannot execute.
- **Handle illustrations honestly.** If a figure, screenshot, seating map, chart, image or diagram is necessary to comprehension and cannot be represented faithfully with supported components, do not fabricate it. Preserve a grounded textual description if useful and note the need to include the approved original asset in subsequent editing. Do not claim exact visual fidelity.
- **Use diagrams conditionally.** A `timeline` is for actual dates or a documented sequence, not simply numbered topics. A `governance` diagram is for a genuinely evidenced multi-actor or multi-level model, not every hierarchy or list.
- **Preserve links exactly.** Use only resource URLs supplied in accessible sources, unless explicitly asked to verify or add outside resources. Don't silently substitute newer URLs.

## 3. Source integrity and reader-facing boundaries

Rely on accessible user-provided documents for factual content. Do not browse or supplement them with outside research unless asked. Distinguish observed facts from source proposals, hypotheses, pending decisions and illustrative examples. If the documents disagree, do not silently reconcile them.

Do not invent people, roles, dates, legal authority, figures, policies, URLs, milestones or conclusions.

Do not add reader-facing document filename citations, "Based on [filename]", "Sources", source-classification labels, distribution warnings, generation-process explanations or generic disclaimers unless the user requests them. **Functional references, actual source-required attribution, substantive limitations and necessary safety/authority warnings may remain.** Do not upload user documents or generated guides to GitHub; use only approved processing and distribution channels.

## 4. Build with Refract's stable format

Produce standard Refract JSON **internally** with exactly `meta`, `pages`, `glossary`. Each page has a unique lowercase-hyphenated `id`, `title`, `blocks`, and optional `intro` and `parent`. Internal card links and parents must target real page IDs.

Supported blocks are `hero`, `paragraph`, `note`, `checks`, `cards`, `steps`, `bullets`, `table`, `resources`, `glossary`, `governance`, `timeline`. The exact field schema is in `references/format.md` and `references/refract-schema.json`.

Select blocks by semantic fit, **not by perceived visual sophistication**. Only create `resources` blocks with actual HTTP(S) URLs. Use `note.label` (not title); `checks.items` uses `[{title,detail}]`; `bullets.items` uses string arrays. Don't emit Markdown-escaped brackets, trailing commas or truncated JSON.

## 5. Validate, critique, render

Before creating HTML, perform two independent silent reviews:

**Fidelity pass:** Check whether the guide remains accurate and complete for its purpose, particularly conditions, exceptions, numbers, definitions, scope, established-versus-proposed status, and genuine links. Verify information is present only where its source warrants it.

**Usefulness pass:** Check whether the reader can find the likely answer quickly; opening content helps their actual task; the site is not a copied table of contents; headings are distinctive; structure is not over-compressed or fragmented; layouts serve information rather than decoration. Consider a reader who knows nothing about the source filename and navigates using only page titles.

If Python execution and file delivery are available:
1. Save the full intermediate JSON as `guide.json`.
2. Run `python scripts/validate_refract.py guide.json`; correct all structural errors and inappropriate editorial warnings.
3. Run `python scripts/render_refract.py guide.json --output guide.html --fail-on-warnings`.
4. Verify the HTML exists and contains embedded `script#guide-data`, navigation, search, print and the source-backed content. Return the downloadable standalone HTML file—not the JSON or HTML source code.

Use the packaged template as supplied; **never independently rewrite HTML/CSS/JS** or substitute a Word/PDF. If code execution/file delivery is genuinely unavailable, state the limitation briefly and supply a complete valid Refract JSON object in one `json` code block. Do not claim a file exists unless it does.

## 6. Final output

A working self-contained HTML guide that can be opened locally, searched, printed, navigated on mobile and re-imported into Refract Studio for visual editing. Accompany the download with at most a short description of its intended use, not a process report.
