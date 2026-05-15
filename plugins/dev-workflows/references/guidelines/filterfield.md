# FilterField

**Source:** [https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/1072628369](https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/1072628369)

## Summary
Harmonizes the FilterField experience across apps to ensure consistent filtering behavior. Use FilterField when users need to filter large, complex datasets with advanced filtering features like AND/OR operators, complex comparisons, or partial matches.

## Mandatory Rules

### DO
- Ensure FilterField implementation aligns with public FilterField documentation
- Use FilterField when filtering large, complex datasets with many data points
- Use FilterField when users need AND/OR operators, complex comparison operators, or partial matches (starts-with, contains, ends-with)
- Always place FilterField above the content it influences
- Place FilterField as close as possible to the filterable content
- Debounce callback logic (wait at least 300ms after user stops typing before fetching suggestions)
- Use caching for previously loaded suggestions
- Limit payload size from backend
- Cancel outdated requests (e.g., use AbortController)
- Keep input responsive; avoid blocking UI on slow network responses
- Wrap FilterField in a FormField with FormFieldMessages context to display validation messages accessibly
- Use validatorMap property to define valid keys, comparison operators, and values
- Show custom error messages (backend timeouts, permission issues)
- Match suggestion label with what will be inserted (except escaped characters)
- Show matching suggestions case-insensitively
- Order key and value suggestions from most relevant to least relevant
- Rank matching suggestions: 1) Exact matches, 2) Starts-with matches, 3) Other partial matches
- Indicate data type with an icon for key suggestions
- Show comparison operator suggestions after users select a key or enter a space
- Show value suggestions after users select a comparison operator or enter a space
- Show OR suggestion when a filter statement has been completed (below key suggestions)
- Apply filters case-insensitively for values, but keep keys case-sensitive
- Require additional confirmation before applying filters when "clear all" is clicked
- Include a dedicated Apply button near the FilterField
- Use neutral colored, emphasized Button when filters are empty or already applied
- Use primary-colored accent Button when filters have changed and haven't been applied
- Include ProgressCircle in Button.Prefix and change to cancel button while loading
- Always keep the Apply button clickable (never disable it)
- Trigger refresh/apply on Cmd+Enter (macOS) / Ctrl+Enter (Windows/Linux)
- Trigger form submission when users press Enter while input is focused

### DON'T
- Alter features, behavior, or syntax from the public documentation
- Use FilterField for simple filter scenarios without customizable operators (use FilterBar instead)
- Combine FilterField and FilterBar for the same dataset
- Request data on every keystroke without debounce
- Run complex logic synchronously in the suggestion callback
- Explicitly add AND operators unless users entered them
- Automatically add OR operators (users must explicitly enter them)
- Automatically connect multiple values of the same key with OR (use `in ()` syntax instead)
- Interfere with FilterField's automatic suggestions (recently used, pinned, search)
- Include escape characters in suggestions unless part of actual key/value
- Let previous/subsequent filter statements affect or limit shown suggestions
- Show comparison operator suggestions not supported for the key's data type
- Auto-insert a comparison operator after a key
- Change default order of comparison operator suggestions unless first suggestion won't lead to useful results
- Suggest the AND operator (it is implicit and handled automatically)
- Use groups to add generic labels like "Key suggestions"
- Apply filters automatically while users are typing (always wait for explicit user action)

## Scenarios

### Value Suggestion Exceptions
Don't show value suggestions when:
- Comparison operator is starts-with, ends-with, contains, exists, or matches phrase
- Value is a duration or number
- Only show in these cases if truly helpful for users

### Filter Statement Suggestions (Optional)
If implementing filter statement suggestions:
- Place them below key suggestions
- Suggest full filter statements (key + comparison operator + typed value)
- Suggest filter statements with matching values above those for commonly used keys

---

## Open Questions / Ambiguities

1. **"Relevance" undefined**: Ordering suggestions by "relevance" is described as domain-specific with no universal definition provided.

2. **"Truly helpful" is subjective**: Value suggestion exceptions say to show suggestions "if truly helpful" - left to implementer judgment with no criteria.

3. **Payload size limits unspecified**: Rule says to "limit payload size" but provides no specific limits or recommendations.
