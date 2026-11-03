# Refract design and quality standard — adaptable, restrained interface

- Use the stable Refract template, not custom freeform HTML/CSS in the LLM's answer. The template ensures self-contained deployment, search, responsive navigation, print layout and re-import into Studio.
- Choose **information architecture before visual components**. Labels should describe what the reader finds, not generic headings. Avoid repeated hero panels, dense tables, decorative cards and long uniform grids.
- Use a calm, professional visual system appropriate to work, training and reference contexts. The existing template is style-consistent; changing the output genre should change the information hierarchy and wording, not invent unsupported visual styles.
- Use `paragraph` for real prose, `steps` only where order is material, `checks` only for actual checks, `table` only where comparison improves scanning, `governance` and `timeline` only for source-supported visual relationships.
- Keep navigation to a manageable number of clear groupings, with nested subpages for detail. No arbitrary page-count targets; both a two-page quick reference and a substantial multi-section guide may be appropriate.
- Preserve specific source terms, values, exceptions, limits and caveats. Simplify redundancy rather than eliminating important information.
- For technical manuals with necessary diagrams, screenshots or exact figures, Refract's structured components cannot reproduce arbitrary artwork or native interactions. Do not fake them. The editor can be used to incorporate approved assets where supported in future revisions.
- Do not embed user source material into the public Refract site, and do not add provenance or distribution boilerplate to reader-facing pages unless requested.
- Test meaningful navigation, print layout, mobile width and browser use when tools permit. Check all internal links, exact external URL strings, and source-supported content.
