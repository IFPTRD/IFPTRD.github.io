# Refract design and quality standard — adaptable, restrained interface

- Use the stable Refract template, not custom freeform HTML/CSS in the LLM's answer. The template ensures self-contained deployment, search, responsive navigation, print layout and re-import into Studio.
- Choose **information architecture before visual components**. Labels should describe what the reader finds, not generic headings. Avoid repeated hero panels, dense tables, decorative cards and long uniform grids.
- Use a calm, professional visual system appropriate to work, training and reference contexts. The existing template is style-consistent; changing the output genre should change the information hierarchy and wording, not invent unsupported visual styles.
- Use `paragraph` for real prose, `steps` only where order is material, `checks` only for actual checks, `table` only where comparison improves scanning, `governance` and `timeline` only for source-supported visual relationships.
- Keep navigation to a manageable number of clear groupings, with nested subpages for detail. No arbitrary page-count targets; both a two-page quick reference and a substantial multi-section guide may be appropriate.
- Preserve specific source terms, values, exceptions, limits and caveats. Simplify redundancy rather than eliminating important information.
- For technical manuals with necessary diagrams, screenshots or exact figures, Refract's structured components cannot reproduce arbitrary artwork or native interactions. Do not fake them. Use embedded image blocks for original PNG/JPEG/GIF/WebP assets where available. Complex editable artwork remains outside the format.
- Do not embed user source material into the public Refract site, and do not add provenance or distribution boilerplate to reader-facing pages unless requested.
- Test meaningful navigation, print layout, mobile width and browser use when tools permit. Check all internal links, exact external URL strings, and source-supported content.

## Mandatory contrast and accessibility requirements

- **Text contrast is a hard quality gate**, not a style preference: 4.5:1 minimum for standard text and 3:1 for large text (WCAG AA), including muted labels, sidebar items, captions and footer links. Do not rely on an appealing palette alone.
- The shared renderer's **hero banner** has a dark navy gradient. Force the hero heading, body copy, and kicker to white/very light values *after* general page heading rules so a dark page-heading colour cannot cascade onto a dark banner. On the prior exercise guide, the text “Turn operating pressure into an actionable decision” failed due to this cascade.
- For small secondary text on light backgrounds, choose dark slate or another verified AA-safe colour rather than pale grey. Check every interactive state including selected navigation and hover/disabled treatments.
- Maintain high-contrast focus indicators, link distinctions, readable table headers and print text. In print, dark-on-white takes precedence over coloured panels.
- The authoring agent must use the bundled template; it must not invent arbitrary theme CSS or colour attributes in the JSON. Verify generated HTML if browser or CSS inspection is available.

Dense guides use collapsible navigation groups and a compact mobile contents button. Keep primary content expanded; within-page contents aid longer pages. Search should open the matching section with a relevant excerpt. Check print with long tables, footnotes and images as well as short examples.

## Editorial quality and images

A full-coverage text dump is not a successful conversion. Rework dense writing into a clear reading path with specific headings and appropriate components; keep ordinary prose when it serves the material. Original image blocks are for specific meaningful visuals, cropped to the visual and its necessary caption/legend. Do not use full PDF-page screenshots, document thumbnails or images of prose/ordinary tables as substitutes for editable content. Do not duplicate source text and page facsimiles. Preserve precision and qualifications while improving expression; retain verbatim wording only where exact wording itself matters.
