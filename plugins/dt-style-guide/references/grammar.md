# Dynatrace grammar rules

Sentence structure, contractions, active voice, and verb usage.
Source: styleguide.dynatrace.com/docs/style/grammar

---

## Sentences and fragments

- A sentence is a grammatically complete idea with a subject and predicate.
- Shorter sentences are easier to read and translate.
- Sentences end with a period, question mark, or (rarely) exclamation mark.
- When a sentence is used as a title or heading, omit closing punctuation.

### Sentence fragments

Fragments (no verb or incomplete predicate) must not end with a period.
Fragments work well for **definitions**:

- ✅ TCP connect time: The time taken to establish the TCP connection
- ✅ TCP connect time: The time taken to establish the TCP connection—if there
  are multiple connections, this is the total time.

---

## Active voice (default)

Structure: [actor] + [verb] + [receiver]

- ✅ The monitoring system identified the problem.
- ❌ The problem was identified by the monitoring system.
- ✅ All three formats support the same request payloads.
- ❌ The same request payloads are supported in all three formats.

### When passive voice is acceptable

Use passive when the actor is unimportant or unknown:
- ✅ Deletion cannot be reversed. (warning)
- ✅ The use of dynamic identifiers is not supported. (system limitation)
- ✅ An alert was triggered when the threshold was exceeded. (definition)

---

## Contractions

### Allowed contractions
- I'm, it's, what's, that's, we're, they're, let's
- aren't, can't, don't, isn't, didn't, wasn't, doesn't, hasn't, haven't

### Banned contractions (awkward or unclear)
- ❌ it'll, it'd, they'd, there'd, mustn't, shan't
- ❌ would've, could've, should've, needn't, mayn't, who'd

### Negative contractions in warnings/alerts
Spell out negative contractions for maximum clarity in warnings, alerts,
and system-limitation statements:

- ✅ Do not use a metric expression to convert the unit.
- ❌ Don't use a metric expression to convert the unit.
- ✅ Deletion cannot be reversed!
- ❌ Deletion can't be reversed!
- ✅ API Edge for Private Cloud is not supported.
- ❌ API Edge for Private Cloud isn't supported.

---

## Plural nouns as adjectives

When a noun is used as an adjective, keep it **singular**:

- ✅ metric browser — ❌ metrics browser
- ✅ management-zone configuration — ❌ management-zones configuration
- ✅ root cause analysis — ❌ root causes analysis
- ✅ credential vault — ❌ credentials vault
- ✅ host group autodiscovery — ❌ host groups autodiscovery

**Exception**: Page names and tab labels that exist in plural form:
- ✅ **Services** page
- ✅ **Frequency and locations** tab

---

## Transitive and intransitive verbs

**Transitive verbs** require a direct object. Don't use them without one:

- ❌ Wait till the image renders.
- ✅ Wait till the image is rendered.
- ✅ Wait till the browser renders the image.

- ❌ Wait till the software installs.
- ✅ Wait till the software is installed.
- ✅ Wait till the wizard installs the software.

**Intransitive verbs** stand alone:
- ✅ The system crashed unexpectedly. (no object needed)

---

## Pronouns

### Second person ("you")
- ✅ You can configure your dashboard.
- ❌ The user can configure their dashboard.
- ❌ Users should configure their dashboards.

### Gender-neutral pronouns
- ✅ their, them, they (singular or plural)
- ❌ he, she, his, her, his or her

---

## Tense

- Use **present tense** for current behaviour and instructions.
- Use **past tense** for completed actions and release notes.
- Avoid **future tense** where present tense works:
  - ✅ The system restarts after the update.
  - ❌ The system will restart after the update.
