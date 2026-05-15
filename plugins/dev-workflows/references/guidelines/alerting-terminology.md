# Alerting Terminology

**Source:** [https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/1273200887](https://dt-rnd.atlassian.net/wiki/spaces/PLAT/pages/1273200887)

## Summary
Defines consistent terminology for alerts and notifications across all Dynatrace apps to ensure users find familiar DEV/DEVOPS terminology and easily discover expected functionality.

## Mandatory Rules

### DO
- Differentiate terminology based on functionality and required response
- Use "alert" when the user must take timely action in response
- Use "notification" when the feature sends a message without necessarily requiring timely action
- Adhere to the Dynatrace Content Style Guide (CST) for all terminology
- Update related documentation when renaming features to comply with this GUIDEline

### DON'T
- Use "alert" and "notification" interchangeably
- Use different names for the same functionality across apps
- Use the same name to mean different things in different contexts

## Definitions

**Alert**
A signal condition within a scope that requires timely action from a notified user or an automation. Alerting is available in the Dynatrace observability, security, and business domains.

**Notification**
A message sent to a Dynatrace user through a defined notification channel such as email, Dynatrace UI, Dynatrace mobile app, or third-party messaging system like Slack. Notifications typically don't require a timely response.

---

## Open Questions / Ambiguities

1. **CST link broken**: The standard references the Dynatrace Content Style Guide for "Notification" but the original document's link appears to be broken/incomplete (shows only "#").

2. **Edge cases undefined**: No guidance provided for edge cases where a feature might blur the line between requiring "timely action" vs not requiring timely action.

3. **Documentation update process**: Rule says to "update related documentation" but doesn't specify who is responsible or what process to follow.
