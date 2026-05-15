# Ready-made Dashboards

**Source:** [https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/785187419](https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/785187419)

## Summary
Quality standards for ready-made dashboards that demonstrate Dynatrace value, are immediately useful, and show dashboard capabilities. Mandatory for all dashboards published on Playground or production environments.

## Mandatory Rules

### DO
- Ensure dashboards contain no errors or warnings in their default configuration
- Set all values, entities, references, DQL code correctly in default state, cluster, and timeframe
- Include both entity ID field (e.g., dt.entity.host) and name field (e.g., host.name) in DQL results for intents to work
- Configure variables, segments, visualization settings, query limits, query options, and timeframe correctly by default
- Ensure variables contain more than one option and are referenced at least once
- Use industry-standard names for options and variables (e.g., `Yes`, `No` with capital letter, not ALLCAPS)
- Include a markdown tile with H3 title (`###`) limited to 50 characters
- Add a short value statement limited to 300 characters using default font style
- Provide 1-2 important links to data onboarding/getting started
- Keep introduction and links in one line without scrolling inside markdown tile
- Use sentence case for titles (per Dynatrace Content Style Guide)
- Prioritize most relevant data above the fold (~768px to 1080px high)
- Use WCAG 2.0 AA accessible color coding:
  - Red threshold: `#c4233b` (Colors.Theme.Critical.70)
  - Green threshold: `#2f6863` (Colors.Theme.Success.70)
  - Yellow threshold: `#ECA440` (Colors.Theme.Warning.70)
- Use white for trends/values displayed over color-coded backgrounds
- Use graph charts for trends over time, tables for details
- Use all screen real estate without horizontal gaps
- Ensure responsive layout works at 650px mobile breakpoint
- Limit to max 6 "simple" tiles (single values) per row
- Limit to max 4 "heavy" tiles (charts, tables, markdown) per row
- Limit to 1 tile requiring horizontal scrolling per row
- Use H3 (`###`) for section titles, H5 (`#####`) for subtitles if needed
- Use one full-width empty markdown tile to separate section title from previous section
- Use the **Description** feature (not markdown) to describe a single tile
- Add comments to DQL code explaining what and why
- Add a footer with expanded explanations, documentation links, and learning resources

### DON'T
- Make users troubleshoot dashboard, variables, or timeframes to resolve errors
- Start with error state, "No options available", or "Select an option" state
- Use confusing names or internal jargon
- Skip the introduction and getting started links
- Use generic names (e.g., "Technology overview")
- Repeat the dashboard name in the title
- Have empty space or less relevant data above the fold
- Use enormous tiles or values above the fold
- Fill entire space with a single tile
- Use color combinations that fail WCAG 2.0 contrast checks
- Create gaps in the layout
- Use more than 6 horizontal elements in a row
- Use markdown to describe a single tile
- Give users a blank slate dashboard without help
- Overwhelm users with content available in documentation

## Scenarios

### Playground Environment
- Double-check for permission-related errors
- Contact Playground team for resolution

### Variable Naming Conventions
- Use `*` symbol (provided by Dashboards UI) to show all data
- Use `Yes`, `No` (capitalized, not ALLCAPS)

---

## Open Questions / Ambiguities

1. **Grid system undefined**: Document references a "6-column grid as a starting reference" but doesn't specify exact pixel widths for columns.

2. **Fold height range too broad**: The fold height range (768px to 1080px) is broad - unclear which specific height should be the target for "above the fold" content.

3. **Maximum dashboard length unspecified**: No specific guidance on maximum dashboard length/scroll depth.

4. **"Medium-height information density" subjective**: Referenced without specific metrics or examples.
