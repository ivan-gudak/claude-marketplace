# DataTable

**Source:** [https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/775421955](https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/775421955)

## Summary
Specifies interaction patterns for the DataTableV2 component, defining when and how to use table, column, row, cell, and in-cell interactions for data-heavy and structured list use cases.

## Mandatory Rules

### DO
- Use `DataTableV2` component (not the deprecated `DataTable`)
- Wrap `DataTableV2` with `DataTableV2CellInteractionPattern` for compliance
- Use out-of-the-box features, slots, and mechanisms provided by the DataTable component
- Place custom actions in `DataTableV2.TableActions` slot
- Enable Line wrap, Column settings, and Download data for data-heavy tables
- Provide search/filter capability via `DataTableV2.TableActions` slot for structured lists
- Enable column sorting and column resizing for all DataTable use cases
- Enable column reordering, column line wrap, and column visibility for data-heavy tables
- Place custom column actions in `DataTableV2.ColumnActions` slot
- Maintain column actions order: Custom actions → `TableActionsMenu.ColumnOrder` → `TableActionsMenu.LineWrap` → `TableActionsMenu.HideColumn`
- Use row interactivity (row click) for presenting in-context information (Page detail view, Modals, Overlays)
- Enable row interactivity for data-heavy tables even without a primary action (to highlight the row)
- Place row actions in `DataTableV2.RowActions` slot
- Place selected row interactions in `DataTableV2.SelectedRowsActions` slot
- Place cell interactions in `DataTableV2.CellActions` slot
- Enable copy cell content (`TableActionsMenu.CopyItem`) as the first cell action for data-heavy tables
- Use `Link` or `ExternalLink` components for navigating to a different context (different page)

### DON'T
- Create alternatives or overrides to existing interaction patterns (mouse, touch, keyboard)
- Move or overwrite out-of-the-box actions
- Use row interactivity to move users to a different context (different page)
- Use `Link` or `ExternalLink` for presenting in-context information (Page detail view, Modals, Overlays)
- Show row-related actions as cell interactions

## Scenarios

### Scenario 1: Table Interactions
Actions affecting the entire table (line wrap, column settings, download, custom search/filter).
- Custom actions must use `DataTableV2.TableActions` slot

### Scenario 2: Column Interactions
Actions affecting a column (sorting, resizing, reordering, line wrap, visibility).
- Custom actions must use `DataTableV2.ColumnActions` slot with prescribed order

### Scenario 3: Interactive Rows (Row Click)
Row click triggers in-context information display only (detail views, modals, overlays).
- Data-heavy tables must enable row interactivity even without primary actions

### Scenario 4: Row Interactions
Actions affecting a row (delete, duplicate).
- Must use `DataTableV2.RowActions` slot
- Can include Button, SelectV2, Switch, or Menu components

### Scenario 5: Selected Row Interactions
Actions affecting multiple selected rows.
- Must use `DataTableV2.SelectedRowsActions` slot

### Scenario 6: Cell Interactions
Actions affecting a specific cell.
- Must use `DataTableV2.CellActions` slot
- Data-heavy tables require copy functionality as first action

### Scenario 7: Interactive Content in Cells
Clickable elements inside cells.
- Use Link/ExternalLink only for context-switching navigation

---

## Open Questions / Ambiguities

1. **Temporary wrapper**: The document mentions wrapping with `DataTableV2CellInteractionPattern` is "temporary" but doesn't specify when it will become obsolete or what will replace it.

2. **Data-heavy vs structured list**: No explicit criteria for when a table qualifies as "data-heavy" vs "structured list" beyond general descriptions. This affects which features are mandatory.

3. **Incomplete code example**: Line 31 shows "js" which appears to be an incomplete code snippet for the import example.
