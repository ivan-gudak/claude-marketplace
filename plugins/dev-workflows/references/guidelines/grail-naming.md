# Grail Naming Scheme

**Source:** [https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/1274413320](https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/1274413320)

## Summary
Outlines naming restrictions for tables and views in Grail to provide customers a unified, guided experience when interacting with Grail storage.

## Mandatory Rules

### DO
- Use descriptive names that clearly communicate the content and expected data/information
- Provide names that help customers understand what they will get when accessing tables or invoking views
- Follow the naming schemes documented in Dynatrace Developer
- Apply rules only to new items

### DON'T
- Create inconsistent naming between capabilities and solutions
- Change existing items (due to high risk of customer impact)

---

## Open Questions / Ambiguities

1. **CRITICAL - Actual rules are external**: The concrete naming rules, patterns, formats, and conventions are NOT included in this guideline. They are referenced externally: "All restrictions and considerations for naming tables and views are documented in Dynatrace Developer (Table view naming schemes)."

2. **No actionable specifications**: Without the external documentation, this guideline provides no specific naming patterns to validate against.

3. **Recommendation**: The actual naming rules from Dynatrace Developer should be incorporated into this reference for the reviewer to be effective. Use dt-app MCP to query for "table view naming schemes" to retrieve the actual rules.
