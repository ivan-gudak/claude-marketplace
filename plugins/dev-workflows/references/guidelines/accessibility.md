# WCAG Accessibility

**Source:** [https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/1372782826](https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/1372782826)

## Summary
Ensures WCAG 2.1 AA compliance (with forward alignment to WCAG 2.2) for Dynatrace apps. Provides a curated set of accessibility rules based on audit findings, regulatory requirements (WCAG / Section 508 / EN 301 549), and existing best practices.

## Mandatory Rules

### DO
- Use the Strato Design System components for out-of-the-box accessibility
- For custom components, reference W3C or Deque patterns
- Provide accessible names for all interactive controls
- Ensure screen readers announce control states (expanded/collapsed)
- Use color in combination with text labels or icons to convey status
- Provide visible and persistent labels for all input fields
- Include placeholder text in all input fields
- Provide alt text for informative images

### DON'T
- Let tooltip text and aria-label differ for icon-only buttons
- Add alt text to icons when accompanying text already describes the control
- Leave controls blank with no aria-label
- Use vague hyperlink text like "Click here" or "More"
- Skip announcing a control's state before announcing dialogs
- Use color alone to convey status meaning
- Rely on placeholder text as the only field label (it disappears when typing)
- Add alt text to decorative images (use `alt=""` instead)
- Use images as the only means of conveying instructions or informative text

## Key Requirements by Category

### Accessible Controls

**Icon-only controls:**
- Set SVG role to `img` and add `aria-hidden="true"`
- Add `aria-label` to the control
- Match tooltip text with `aria-label`
- Consider adding tooltips for non-universal icons

**Text + icon controls:**
- Set SVG role to `img` and add `aria-hidden="true"`
- Ensure visible text matches accessible name
- Do not add alt text to the icon

**Text-only controls:**
- Ensure visible text matches accessible name
- Leave aria-label blank if text content describes purpose
- Use meaningful link text, not generic phrases

**State announcement:**
- Ensure screen readers announce expanded/collapsed states
- Announce state before announcing associated dialogs

### Accessible Statuses
- Always combine color with text labels or icons
- Add icons only when text doesn't describe the status
- Never rely solely on color to communicate meaning

### Accessible FormFields

**Search and FilterField:**
- Use `SearchInput` component (provides persistent search icon)
- Use funnel icon prefix for FilterField components
- Never rely on placeholder text as the only label

**Click-to-rename fields:**
- Provide an alternative method (e.g., overflow menu)
- Use aria-label with format: `"Rename [item type]: <current name>"`

**Generic input fields:**
- Always include visible, persistent labels (text and/or icon)
- Don't assume section titles serve as field labels
- All input fields require an associated label

**Placeholder text:**
- Required for all input fields (enables WCAG color contrast exception)
- Use default Strato placeholders if no context-specific text available
- Components requiring placeholders: DateTimePicker, NumberInput, PasswordInput, Select, CodeEditor, FilterField, TextArea, TextInput

### Multimedia

**Images:**
- Classify images as decorative or informative
- Provide alt text only for informative images
- Use empty alt (`alt=""`) for decorative images
- Never use images as the sole means of conveying instructions
- Render informative text as HTML, not embedded in images

---

## Open Questions / Ambiguities

1. **State announcement in flux**: Document notes that "final amendments are in progress within the Strato Design System" for state announcement rules - implementation may change.

2. **Tooltip recommendation unclear**: For icon-only controls, tooltips are "strongly recommended but not mandatory" - no specific criteria for when an icon is "universally understood" enough to skip the tooltip.

3. **Icon as label verification**: When an icon is used as a persistent label, guidance says to "verify it's understood for the use case" - no specific testing criteria provided.
