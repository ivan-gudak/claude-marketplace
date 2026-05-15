# Creating Settings

**Source:** [https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/1263767075](https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/1263767075)

## Summary
Defines rules for creating settings pages in the Dynatrace Settings app, ensuring consistent UX for configurations that affect platform operation and multiple users.

## Mandatory Rules

### DO
- Base new settings pages on a schema(s) in the settings service
- Make settings pages ready for internationalization (translatable/translated strings on deployment)
- Implement a widget in the Settings app for each new settings page
- Use the `<WidgetWrapper />` from the settings component library
- Use a concise and descriptive title consistent with the setting name in Settings app navigation
- Provide a brief description of the widget's intended use (~2 lines max)
- Provide a link to documentation if it exists and applies directly to the widget content
- Adhere to Dynatrace Content Style Guide (sentence case for titles, grammar, punctuation, linking, tone)
- Use a sheet or modal when displaying additional content for adding/editing top-level configurations
- Use a sheet when there is a lot of content; use a modal when there is less content
- Require users to explicitly confirm changes (including table ranking, inline changes, sort order modifications)
- Present complex lists as a table (`DataTableV2`)
- Configure tables with: `contained` mode, `rowDensity` = `default`, `horizontalDividers` = true
- Make the first column an identifier (e.g., "Name")
- Make the last column the "Actions" column
- Provide "Edit" (with `EditIcon`) and "Delete" (with `DeleteIcon`) actions in each row menu
- Mark delete actions as "destructive" and trigger a confirmation modal
- Show success toast after confirming destructive actions; show error toast if action fails
- Opening a row or edit action must open item details in a modal or sheet
- Place "New item" button at top right of list using `DataTableV2.TableActions` slot
- Style the "New item" button with `primary` `accent` style and "+" icon prefix (e.g., `+ New connection`)
- Show success toast after successful item creation
- Place search on the left in `DataTableV2.TableActions` slot
- Keep configurable content at the top; place non-configurable content below
- Display an Empty State (with mandatory title and primary action button) when no settings exist and the table is the only page element

### DON'T
- Add call to actions in the title bar (place them in the content area below)
- Remove the divider under the title (unless using tabs that include a divider)
- Use unnecessarily small default page size for tables

## Scenarios

### Empty State Requirements
- **Title**: Mandatory - strong call to action promoting creation of first item
- **Details**: Optional - additional context or relevant links
- **Actions**: Mandatory - CTA button in `primary` `accent` style matching the table's top-right button copy
- **Footer**: Optional - secondary links (documentation, support articles)

### Table Configuration
- Set `zebraStripes` to false
- Set `verticalDividers` to false (unless required by use case)
- Keep `defaultPageSize` unset unless use case requires smaller number
- Sort table to highlight most important rows (e.g., items with bad "Health" listed first)
- Use FilterBar component for filtering lists

### Modal vs Sheet Selection
- **Modal**: For quick one-step creation of new item (size 'medium')
- **Sheet**: For multi-step configuration processes

---

## Open Questions / Ambiguities

1. **Auto-hiding behavior in flux**: The behavior of automatically hiding settings pages when a user has no read permissions is noted as "currently being reconsidered and may be revised in a later version."

2. **Legacy settings scope unclear**: Standard notes it "does not yet apply to all classic settings pages" - scope of legacy compliance is unclear.

3. **User preferences excluded**: User preferences (configurations affecting only current user) are explicitly excluded from this standard version - separate standard needed?
