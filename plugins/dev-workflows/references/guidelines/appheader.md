# AppHeader

**Source:** [https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/636715031](https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/636715031)

## Summary
Defines mandatory requirements for implementing a consistent AppHeader component that provides first-level navigation across all platform apps. The AppHeader must contain the app logo, tabs (if applicable), and menus (settings if available, help menu always required).

## Mandatory Rules

### DO
- Include the app logo, any available tabs, and menus (settings if applicable, help menu always)
- Take users to the app's home page when the app logo is clicked
- Take users to the first tab when the app logo is clicked (if the AppHeader contains tabs)
- Place menus in the top-right corner with help menu on the rightmost side and settings on the left
- Provide hover states, `aria-label`, and tooltips for menu items
- Use the template from the Help menu guideline for the help menu
- Hide unavailable help menu options (e.g., Keyboard shortcuts or Try in Playground if not available)
- Include a visible entry point to settings in the AppHeader for apps with customizable settings
- Redirect settings to the relevant section of the Settings app (if available)
- Use the `neutral-emphasized` variant and relevant Strato prefix icons for app-wide actions

### DON'T
- Use the app logo as a separate independent tab
- Change icons or order of menu items
- Add labels to default action items
- Disable hover states on menus
- Create a custom design for the help menu
- Change the help menu item order or icons
- Use suffix and prefix icons simultaneously in the help menu
- Add more than two app-wide actions
- Duplicate the help menu
- Use `primary` or `accent` variants for app-wide actions

## Scenarios

### Scenario 1: Apps without tabs
Use when the app has only one primary flow, use case, or way to explore data.
- Required components: `AppHeader.Logo`, `AppHeader.Menus` (with `AppHeader.HelpMenu`)
- Clicking app logo takes user to app's starting page

### Scenario 2: Apps with two, three, or more tabs
Use when the app has several high-level features, personas with different goals, or access levels.
- Required components: `AppHeader.Logo`, `AppHeader.Navigation`, `AppHeader.Menus`
- Clicking app logo takes user to first tab
- Each tab must be clickable and show active state when selected

### Scenario 3: Apps with app-wide actions (optional recommendation)
Use when one or two actions need to be always visible on any page.
- **Note**: This scenario is a recommendation and will NOT be enforced or tested
- Components: `AppHeader.Logo`, `AppHeader.Navigation` (if applicable), `AppHeader.ActionItem`, `AppHeader.Menus`
- Maximum of two app-wide actions allowed

---

## Open Questions / Ambiguities

1. **Help menu template not defined**: The rules reference "the template from the Help menu guideline" but the specific required items (What's new, Getting started, Documentation, Share feedback, About this app) appear only in testing criteria, not as explicit mandatory rules.

2. **Settings behavior undefined**: No guidance on what to do when the "Settings app" is not available but the app has settings.

3. **Version compatibility unclear**: Document mentions "Version 1.3.0 and above recommended" but doesn't clarify if older versions are non-compliant.

4. **Help menu required items**: Testing criteria mention specific items but the main rules only say "use the template" - which items are truly mandatory?
