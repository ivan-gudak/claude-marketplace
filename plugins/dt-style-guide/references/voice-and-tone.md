# Dynatrace voice and tone

The three pillars of Dynatrace voice: confidence, approachability, empowerment.
Source: styleguide.dynatrace.com/docs/style/voice-and-tone

---

## Confidence

Write with authority. Be clear, concrete, and honest.

- **Be direct.** State facts without hedging. Avoid "we believe," "we think,"
  "it seems," "arguably."
- **Be concrete.** Use specific numbers, names, and examples. Avoid vague
  qualifiers like "various," "numerous," "a lot of."
- **Be pragmatic.** Focus on what the reader can do, not on abstract theory.
- **Use active voice.** The subject performs the action.
  - ✅ The monitoring system identified the problem.
  - ❌ The problem was identified by the monitoring system.
- **Be honest.** Acknowledge limitations transparently.

---

## Approachability

Write like a knowledgeable colleague, not a textbook.

- **Use familiar terminology.** Avoid jargon and acronyms the reader might not
  know. If a term is necessary, define it on first use.
- **Write in plain English.** Short sentences, common words, simple structure.
- **Use contractions.** They mimic conversational speech and reduce formality.
  - ✅ it's, don't, you're, can't, isn't, we're
  - ❌ it'll, it'd, they'd, mustn't, shan't, would've
- **Address the reader directly.** Use "you" and "your."
  - ✅ You can configure your dashboard.
  - ❌ The user can configure their dashboard.
  - ❌ One can configure the dashboard.
- **Spell out negative contractions in warnings/alerts** for maximum clarity:
  - ✅ Do not use a metric expression to convert the unit.
  - ❌ Don't use a metric expression to convert the unit.

---

## Empowerment

Help the reader succeed. Write from their perspective.

- **Be helpful.** Provide context, not just instructions. Explain *why*
  something matters, not just *how* to do it.
- **Write from the user's perspective.** Focus on what they can achieve,
  not on what the product does.
  - ✅ You can monitor up to 100 hosts.
  - ❌ Dynatrace supports monitoring of up to 100 hosts.
- **Be accessible.** Write so that anyone — regardless of experience level,
  language background, or ability — can understand.
- **Avoid jargon.** If you must use a technical term, define it.
- **Don't patronise.** Avoid words like "simply," "just," "easy," "obvious."
  What's easy for one reader isn't easy for another.

---

## When passive voice is acceptable

Passive voice is preferred when the actor is less important than the action:

- ✅ Deletion cannot be reversed. (warning — action matters, not actor)
- ✅ An alert was triggered when the threshold was exceeded. (glossary definition)
- ✅ The use of dynamic identifiers is not supported. (system limitation)

---

## Anti-patterns to watch for

| Pattern | Problem | Fix |
|---|---|---|
| "We believe that…" | Hedge word | State the fact directly |
| "It should be noted that…" | Filler | Delete; state the point |
| "In order to…" | Wordy | Replace with "To…" |
| "Leverage" (as verb) | Jargon | Use "use" or "take advantage of" |
| "Utilize" | Pretentious | Use "use" |
| "Please" in instructions | Unnecessary politeness | Omit |
| "Simply" / "just" / "easy" | Patronising | Omit |
| "Various" / "numerous" | Vague | Be specific |
| Exclamation marks | Overenthusiastic | Use sparingly or not at all |
