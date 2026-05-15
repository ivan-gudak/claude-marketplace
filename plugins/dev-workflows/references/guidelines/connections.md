# Connection Experiences

**Source:** [https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/775290921](https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/775290921)

## Summary
Defines how to build consistent connection experiences for third-party integrations in Dynatrace, covering Settings app placement, schema definitions, naming conventions, and workflow actions.

## Mandatory Rules

### DO
- Place connections that ingest data in the "Collect and capture" section of the Settings app
- Place connections that do NOT ingest data in the "Connections" section of the Settings app
- Use headless apps ("Connectors") to deliver settings schemas for connections and workflow automations
- App ID must end with `.connector` (e.g., `dynatrace.github.connector`)
- App-Settings must have `connection` in their schema ID (e.g., `app:dynatrace.github.connector:connection`)
- Set schema attributes: `multiObject` = true, `ordered` = false
- Set `allowedScopes` to not be preset or set to `["tenant"]`
- Include schema `metadata` with: `type` = connector, `subtype` (e.g., `ingest` or `automation`), `vendor`, `product`
- Schema must have a mandatory and unique `name` field with `text` type
- Use vendor terminology for vendor-focused attribute names (don't normalize between vendors)
- Use Dynatrace terminology for Dynatrace attribute names
- Headless app for only a connection and workflow automation must have "Connector" at the end of its name
- Combine connections in the same connector if multiple connection types exist for the same product
- Name connectors according to third-party vendors and their products
- Combine connectors under the same product names
- Use specific, concise names for workflow actions (max 40 characters)
- Use sentence case capitalization for workflow action names
- Use service name followed by ":" as prefix when applicable (e.g., `System Manager: List commands`)
- Include descriptions that are concise, single sentence, without a period at the end

### DON'T
- Place connections that ingest data in the "Connections" section
- Hide connections from settings
- Place "connection" or "connector" suffixes in settings pages titles
- Name connectors by use cases or technologies
- Use internal jargon or code in workflow action names
- Leave workflow action descriptions empty or include more than a single sentence

## Scenarios

### Empty State (No Connections Exist)
- Display EmptyState component with CTA to create first connection
- Include links to documentation in description and footer
- Add external link for feedback to Dynatrace Community in footer

### Creating a Connection
- Use a modal for one-step creation (use Stepper for complex multi-step processes)
- Use medium-sized modal
- Include message container for status/security information
- If user did not fill any fields: modal can close without confirmation
- If user started filling fields:
  - Clicking outside modal does not close it
  - Clicking Cancel or X triggers confirmation: "Are you sure you want to...?"
  - Clicking Save performs checks, creates connection, closes modal
- Show success toast message on completion

### Editing a Connection
- Use DataTableV2 in contained style to list connections
- Place Search on left, "+ New connection" primary button on right
- Name column on left, Actions column on right (can add more columns)
- Rows are interactive/clickable with Edit and Delete actions
- Edit modal title: "Edit connection"
- Delete button placed on left as Neutral/Emphasized tertiary action
- Cancel (Default style) and Save (Accent/Primary) on right
- If user made changes:
  - Clicking outside modal does not close it
  - Cancel/X triggers small confirmation modal
- Show success toast on completion

### Deleting a Connection
- Show small confirmation modal with title: "Are you sure you want to delete [name]?"
- Include description about permanent deletion and reviewing dependent use cases
- Provide Cancel and "Delete connection" actions
- Show success toast on completion
- Remove deleted connection from table

### Managing Permissions
- Display missing permissions at top with message container
- Disable "Create new connection" button with tooltip when no permission
- Replace "Edit" with "View" when no edit permission
- Disable "Delete" with tooltip when no permission
- Clicking "Missing permissions" shows modal with list of missing permissions
- In edit modal: show missing permissions message, disable Save and Delete with tooltips

---

## Open Questions / Ambiguities

1. **`allowedScopes` ambiguous**: Rule states "must not be preset or set to `["tenant"]`" - unclear if "not preset" means the field should be omitted entirely or just not set to a different value.

2. **Validation errors unaddressed**: No explicit guidance on handling connection validation errors during create/edit flows.

3. **Pagination unspecified**: No specific guidance on pagination for large numbers of connections in the table.
