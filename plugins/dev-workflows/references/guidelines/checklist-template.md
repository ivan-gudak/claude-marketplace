# GUIDEline Compliance Checklist

**App/Component:** _________________
**Reviewer:** _________________
**Date:** _________________

---

## AppHeader (if applicable)

- [ ] AppHeader component is used
- [ ] App logo present and navigates to app home
- [ ] Help menu is included (mandatory)
- [ ] Settings icon present (if app has settings)
- [ ] Menu order: settings before help
- [ ] Tooltips on icon-only buttons
- [ ] Tabs used for multiple high-level features (if applicable)

**Notes:**

---

## DataTable (if applicable)

- [ ] Loading state implemented
- [ ] Empty state implemented
- [ ] Keyboard navigation supported
- [ ] Selection behavior is consistent
- [ ] Sorting indicators visible
- [ ] Pagination implemented for large datasets

**Notes:**

---

## FilterField (if applicable)

- [ ] NOT combined with FilterBar for same dataset
- [ ] Positioned above filtered content
- [ ] Debounce implemented (300ms minimum)
- [ ] Suggestions are cached
- [ ] Syntax validation provides feedback
- [ ] Links to public documentation in footer

**Notes:**

---

## Connection Experiences (if applicable)

- [ ] Clear connection status indicators
- [ ] Error states are informative
- [ ] Retry mechanisms available
- [ ] Credentials handled securely
- [ ] OAuth flows follow standard patterns

**Notes:**

---

## Missing Permissions (if applicable)

- [ ] Permission errors are clearly communicated
- [ ] Users understand what permission is missing
- [ ] Guidance provided on how to obtain access
- [ ] Graceful degradation when partial access

**Notes:**

---

## Settings (if applicable)

- [ ] Settings accessible from AppHeader
- [ ] All settings have descriptions
- [ ] Validation feedback is immediate
- [ ] Changes are saved appropriately
- [ ] Default values are sensible

**Notes:**

---

## Dashboards (if applicable)

- [ ] Dashboard follows ready-made quality standards
- [ ] Tiles are properly sized and arranged
- [ ] Data refresh indicators present
- [ ] Empty states handled

**Notes:**

---

## Terminology

- [ ] "Alert" used for signals requiring user action
- [ ] "Notification" used for messages not requiring action
- [ ] Consistent with Dynatrace Content Style Guide

**Notes:**

---

## Grail Naming (if applicable)

- [ ] Table names follow naming scheme
- [ ] View names follow naming scheme
- [ ] Names clearly communicate content

**Notes:**

---

## Accessibility (WCAG)

- [ ] All images have alt text
- [ ] Icon-only buttons have aria-labels
- [ ] Keyboard navigation works throughout
- [ ] Focus indicators are visible
- [ ] Color contrast meets WCAG AA
- [ ] Screen reader compatible

**Notes:**

---

## Summary

| Category | Status | Critical Issues |
|----------|--------|-----------------|
| AppHeader | Pass/Fail/N/A | |
| DataTable | Pass/Fail/N/A | |
| FilterField | Pass/Fail/N/A | |
| Connections | Pass/Fail/N/A | |
| Permissions | Pass/Fail/N/A | |
| Settings | Pass/Fail/N/A | |
| Dashboards | Pass/Fail/N/A | |
| Terminology | Pass/Fail/N/A | |
| Grail Naming | Pass/Fail/N/A | |
| Accessibility | Pass/Fail/N/A | |

**Overall Status:** _________________

**Blocking Issues:**

**Recommendations:**
