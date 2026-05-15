# Missing Permissions

**Source:** [https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/698384464](https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/698384464)

## Summary
Provides best practices for displaying missing permissions messages in the Dynatrace platform when users are denied access to functionality due to policy or permission restrictions.

## Mandatory Rules

### DO
- Show missing permission messages next to affected elements
- Keep UI elements visible but disabled (never hide UI controls)
- Specify which permissions are missing using a CodeSnippet component (condensed, copyable)
- Include copyable details: Message, Missing permissions, Environment ID, App name, User email, User ID
- Use line breaks in code snippets for legibility
- Use `aria-disabled` to make disabled buttons accessible
- Use overlays with a "View details" button for non-critical blocked actions
- Open a modal with CodeSnippet when user clicks "View details"
- Combine multiple missing permissions into one MessageContainer

### DON'T
- Disclose details about policy boundaries
- Hide UI controls that require permissions
- Leave users guessing about which permissions are missing
- Interrupt user flow with modals or alerts for non-critical actions
- Show buttons as enabled then display permission errors only after click
- Add "call to action" buttons inside tooltips (tooltips are not interactive)
- Show multiple message containers for different permissions
- Disclose conditional access conditions (say "No data available" instead)
- Use Read-only chip for IAM permission scenarios (only for document sharing)

## Scenarios

### Scenario 1: Complete Access Denied (HIGH/Red)
**When:** User lacks permissions for core data or core actions (app cannot provide value)

**Required behavior:**
- Use EmptyState component with message: "You'll need some additional permissions to access `<app name>`"
- Pair with CodeSnippet component containing:
  ```
  Message: You'll need some additional permissions to access <app name>
  Missing permissions: PERMISSION-1, PERMISSION-2;
  Environment: ENVIRONMENT_ID
  App name: APP_NAME
  User email: USER_EMAIL
  User ID: USER_ID
  ```
- Include a "Try Playground" call-to-action

### Scenario 2: Access Denied to Perform Action (LOW/Yellow)
**When:** User is restricted from performing a non-critical action (form controls like TextInput, Select, Radio, Checkbox, Switch)

**Required behavior:**
- Show element as disabled with `aria-disabled` and "not-allowed" cursor
- Display overlay on hover or Enter key press
- Use message: "You'll need some additional permissions to `<action>`"
- Clicking "View details" opens modal with copyable CodeSnippet

### Scenario 3: Optional Extra Nudge
**When:** User is blocked from an important (but not core) action

**Required behavior:**
- Use MessageContainer + overlay on disabled elements
- Banners are non-dismissable (issue is expected to be resolved by admin)
- Do not use for permanent permission restrictions

### Scenario 4: Conditional Access Denied
**When:** Data exists but conditional access prevents user from seeing it

**Required behavior:**
- Display: "No `<entity>` available" (e.g., "No logs available")
- Do NOT reveal that data exists but is restricted

### Special Case: Read-only Chip
**When:** View-only access based on document sharing (Notebooks, Dashboards)

**Required behavior:**
- Only use for document sharing scenarios
- Do NOT use for IAM permission scenarios

---

## Open Questions / Ambiguities

1. **Mixed scenarios undefined**: No specific guidance on handling mixed scenarios where user has partial access to some features but not others.

2. **Timeout behavior unspecified**: No guidance on what to display if permission check fails due to timeout or error.

3. **"Try Playground" undefined**: The "Try Playground" call-to-action is mentioned but not defined - what should it link to or do?
