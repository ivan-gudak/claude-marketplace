# Design: Split `/impl` — test-writing, docs, and Jira-driven workflows

**Date:** 2026-04-30 (updated 2026-05-01)
**Status:** Approved — ready for implementation
**Scope:** `plugins/dev-workflows` only

---

## 1. Problem

The `/impl` command serves two fundamentally different contexts:

- **Code changes** — tests should be written for new/changed behavior; none are currently written
- **Documentation changes** — branching, code review, and test suites are irrelevant noise

Additionally, a third workflow is needed: Jira-driven documentation and Epic writing, which is a multi-source aggregation pipeline bearing no resemblance to either of the above.

---

## 2. Decisions

**Split `/impl` into five commands:**

| Command | Purpose |
|---|---|
| `/impl` | Backward-compatible alias → `/impl:code` |
| `/impl:code` | Full code workflow + test-writing phase (new) |
| `/impl:docs` | One-shot doc editing (simple markdown, READMEs, Obsidian notes) |
| `/impl:jira:docs` | Jira hierarchy + PR diffs → feature documentation |
| `/impl:jira:epics` | Jira VI + code scan → child Epic writing |

**Why not a single command with context detection:** Ambiguity risk is too high (`.yaml`, `.sh`, `.json` — code or config?). The Jira workflow is a multi-source aggregation pipeline that shares nothing meaningful with `/impl:docs`.

**Why `/impl:jira:docs` and `/impl:jira:epics` are separate from `/impl:docs`:** The Jira-driven workflows involve multi-repo parallel analysis, structured handoff schemas between agents, and Jira hierarchy traversal. Merging into `/impl:docs` would force it to carry conditional bloat for an unrelated workflow.

---

## 3. Architecture

### New command files

```
plugins/dev-workflows/commands/
  impl/
    code.md               ← canonical full code workflow + test-writing phase   → /impl:code
    docs.md               ← one-shot doc editing workflow                        → /impl:docs
    jira/
      docs.md             ← Jira + PR diffs → feature documentation              → /impl:jira:docs
      epics.md            ← Jira VI + code scan → Epic writing                   → /impl:jira:epics
```

Namespaced slash commands are loaded via **directory convention** (`commands/<parent>/<child>.md` → `/<parent>:<child>`). This avoids `:` in filenames, which is forbidden on Windows filesystems; the repo must remain clone-able on Windows.

### New agent files

```
plugins/dev-workflows/agents/
  test-writer.md          ← writes tests for new/changed code behavior
  doc-reviewer.md         ← reviews docs for correctness, completeness, audience fit
  doc-fixer.md            ← fixes BLOCKER/MAJOR doc review findings
  jira-reader.md          ← reads Jira markdown hierarchy from vault
  code-diff-summarizer.md ← summarizes PR diffs per repo (parallel, use case A)
  code-scanner.md         ← scans code for reuse/gaps (parallel, use case B)
```

### Modified files

```
plugins/dev-workflows/
  commands/
    impl.md               ← alias notice + full body duplicated from impl/code.md (see §3 alias pattern)
  .claude-plugin/
    plugin.json           ← register all new commands + introduce `version` field
  agents/
    impl-maintenance.md   ← extend to recognise all /impl:* sub-commands (see §3 impl-maintenance update)
  hooks/
    preload-context.*     ← extend to handle the new /impl:* variants (see §3 hook scope)
  README.md               ← update command and agent tables
  CHANGELOG.md            ← add entry
.claude-plugin/
  marketplace.json        ← introduce `version` field on the dev-workflows entry and bump it
```

### Versioning (introduced by this change)

Neither `plugin.json` nor `marketplace.json` currently carry a `version` field — there is nothing to bump in the existing schema. This change introduces semantic versioning for the `dev-workflows` plugin:

- Add `"version": "<semver>"` to `plugins/dev-workflows/.claude-plugin/plugin.json`.
- Add `"version": "<semver>"` to the `plugins[]` entry for `dev-workflows` in `.claude-plugin/marketplace.json`.
- Initial value: `"1.0.0"` (representing the pre-split state captured in git); this change bumps it to `"1.1.0"` (additive commands, no breaking changes to `/impl`).
- Other plugins in the marketplace are not required to adopt versioning as part of this change but should follow the same convention when they next see substantive edits.

### `impl.md` alias pattern

`/impl` must continue to work as it did before this change — i.e. users who invoke `/impl <description>` get the full code-workflow experience (what is now `/impl:code`).

The alias is implemented by **duplicating the full content** of `commands/impl/code.md` into `commands/impl.md`, prefixed with a short alias notice:

```markdown
<!-- KEEP IN SYNC WITH commands/impl/code.md -->
<!-- /impl is a backward-compatible alias for /impl:code. -->
<!-- For doc edits, use /impl:docs. For Jira-driven feature docs, use /impl:jira:docs. -->
<!-- For writing child Epics, use /impl:jira:epics. -->
<!-- Any change to impl/code.md MUST be reflected here verbatim; CI should diff and fail on drift. -->

Implement the following: $ARGUMENTS

…(rest of the canonical /impl:code workflow copied verbatim)…
```

**Why duplication, not runtime delegation:** Slash command files are not directly executable from inside another command. "Read file X and follow it as if it were this command's body" is fragile when plugin paths change. A verbatim duplicate is deterministic; the drift risk is managed by the `KEEP IN SYNC` marker plus the CHANGELOG entry noting the obligation.

### Hook scope (`preload-context`)

The existing `preload-context` hook injects git context and a model-routing reminder for `/impl`, `/vuln`, `/upgrade`. After this change it must match the new command shape:

| Command | Context injection |
|---|---|
| `/impl` (alias) | Full — same as `/impl:code` |
| `/impl:code` | Full — git context + model-routing reminder |
| `/impl:docs` | **None** — user manages git manually; model-routing is not triggered |
| `/impl:jira:docs` | `$VAULT_PATH` and `<repos_base>` (default `/repos`); git branch context **only if** cwd is inside a git repo |
| `/impl:jira:epics` | Same as `/impl:jira:docs` |

The hook should pattern-match against `/impl` and all `/impl:*` variants rather than each one literally, to avoid regressions when future sub-commands are added.

### `impl-maintenance` update

Every command that runs Phase 4 (code) or Phase 8 (Jira) maintenance invokes `impl-maintenance` via the session-handoff block. After this split, the handoff block must include an explicit **`Command run:` field** so the agent's "Command workflow improvements" section can suggest changes against the right command variant:

```
Command run: /impl:code | /impl:docs | /impl:jira:docs | /impl:jira:epics
```

The existing `agents/impl-maintenance.md` prompt must also be updated in two places:

1. The **Inputs** section adds `Command run` to the expected session-handoff fields.
2. The **"Command workflow improvements"** output sub-section, currently fixed to `"Command: [/impl | /vuln | /upgrade]"`, is broadened to `"Command: [/impl | /impl:code | /impl:docs | /impl:jira:docs | /impl:jira:epics | /vuln | /upgrade]"`.

Without this update, maintenance suggestions from the three new Jira/docs commands would be labelled against the wrong command and silently misdirected.

---

## 4. `/impl:code` — workflow changes

All existing phases from the current `impl.md` (which becomes `commands/impl/code.md` under the new directory layout — see §3) are preserved. Two insertions are made.

### Insertion 1 — Pre-Phase 3.5: Capture test baseline

Placed **after** branch creation (Pre-Phase 3), **before** any file edits:

```
→ Agent (subagent_type: "dev-workflows:test-baseline"):
  Mode: capture
  Project root: [absolute path]
```

Store the returned `## Test Baseline` block. If `Framework: not detected`, note it but continue — Phase 3.5 will surface this to the user explicitly.

### Insertion 2 — Phase 3.5: Write and verify tests

#### For SIMPLE/MODERATE (after Phase 3A implementation):

1. Invoke `test-writer` agent (Section 8).
2. If `test-writer` returns `Framework: not detected`:
   ```
   choices: ["Specify test command to use", "Skip tests for this run (document why in Phase 5 report)", "Cancel"]
   ```
3. Run linters/builds.
4. Invoke `test-baseline` in verify mode against the captured baseline.
5. **Fix loop** — if regressions or new test failures are reported:
   - The **session model** (not a subagent) applies fixes using the `test-baseline` verify report as the authoritative list of regressions. No `review-fixer`-style indirection is used here — the scope is narrow and the context is already fully in-session.
   - After each fix attempt, re-capture the diff (`git add -N . && git diff`) and re-run `test-baseline` in verify mode against the **original** baseline (never re-baseline mid-loop).
   - Cap at **2 fix attempts**. If regressions remain, surface to user with `choices: ["Investigate further", "Accept regressions and proceed", "Cancel"]`.

#### For SIGNIFICANT/HIGH-RISK (inside Phase 3B):

- **After step 4** (implementation complete), **before step 5** (diff capture):
  - Invoke `test-writer` agent.
  - If `test-writer` returns `Framework: not detected`: **before** invoking Opus review, ask the user (mirrors the SIMPLE/MODERATE branch):
    ```
    choices: ["Specify test command to use", "Skip tests for this run (document why in Phase 5 report)", "Cancel"]
    ```
    This keeps the Opus-review input deterministic — the reviewer is never asked to reason about an unknown test strategy — and ensures the "Skip" decision is an explicit, logged choice.
- **Step 5 diff** now includes test files → Opus reviews code and tests together (test adequacy is already a review dimension in `code-review.md`).
- Phase 3.5 runs **after** the review gate clears (non-BLOCK verdict), replacing steps 8–10 of the original Phase 3B (run tests, fix failures, re-run). The fix loop here uses the same pattern as Phase 3B review-fix handling: the session model applies fixes; if fixes are non-trivial the Opus review is re-invoked on the delta (unless the reviewer was down-classified in step 7).

### New invariants for `/impl:code`

```
- ALWAYS capture test baseline (Pre-Phase 3.5) before writing any file
- NEVER skip Phase 3.5 — if no test framework detected, ask the user rather than silently skipping
- NEVER run tests for SIGNIFICANT/HIGH-RISK before Opus review returns non-BLOCK (preserved)
```

---

## 5. `/impl:docs` — one-shot doc editing

### What is removed vs `/impl:code`

| Removed | Reason |
|---|---|
| Pre-Phase 3 (branch creation, clean-tree check, git operations) | No branching; user manages git manually |
| Pre-Phase 3.5 (baseline capture) | No tests |
| Phase 3B (SIGNIFICANT/HIGH-RISK code path) | Docs changes are never SIGNIFICANT in this command |
| Phase 3.5 (test writing + verify) | No tests |
| Opus planning / Opus review | Never warranted for one-shot doc edits |
| Git commit | User manages manually |

### Scope

`/impl:docs` handles only **one-shot doc editing**: minor edits, formatting, small updates to existing pages, single-file additions where the content comes from the user's description alone. All classification is SIMPLE or MODERATE.

For net-new documentation created from Jira hierarchy + code repos, use `/impl:jira:docs` or `/impl:jira:epics`.

### Phase 2A plan template change

Replace "Tests" section with "Validation" — spot-check steps (link integrity, heading structure, broken `[[wikilinks]]`).

### Phase 3 implementation

Make edits; run validation checks from plan; no test step; no git commit.

### Phase 4 and Phase 5

All four Phase 4 maintenance agents run unchanged. Phase 5 report: no branch, no test results, no Opus review. Add `### Validation` section.

### Invariants

```
- NEVER create a git branch
- NEVER run tests
- NEVER invoke Opus
- NEVER commit — user manages git manually
- ALWAYS run Phase 4 maintenance agents
```

---

## 6. `/impl:jira:docs` — Jira-driven feature documentation

### Purpose

Given a Jira Value Increment key, reads the full Jira hierarchy from pre-exported markdown files in the vault, resolves PR URLs to local git repos, runs parallel PR diff summaries, synthesizes product documentation, reviews, and writes output to cwd.

### Phase 0 — Load and dispatch

1. Resolve `$VAULT_PATH` (env var → ask if unset → validate existence).
2. Resolve `<JIRA_KEY>` from `$ARGUMENTS`; validate `$VAULT_PATH/jira-products/<JIRA_KEY>/` exists. If not: stop with error.

### Phase 1 — Clarification

Ask (grouped where possible, `choices` arrays, last choice always `"Other… (describe)"`):

- Output filename / sub-path under cwd (default: `<KEY>-<slug>.md`).
- PR status filter (MERGED only `(Recommended)` / all / specific list).
- Repo refresh policy: `fetch only` `(Recommended)` / `fetch + pull default branch` / `no refresh`.
- **Repos base path** — detect `/repos` (check existence) and ask:
  ```
  choices: ["Use /repos (Recommended)", "Use a different path (you'll be prompted)", "Cancel"]
  ```
  If "different path", follow up with a free-text entry and validate that at least one directory exists under it.

Also detect and show: resolved cwd absolute path, write context (obsidian / git_repo / plain_dir — see Section 11), whether branching will happen, and the resolved `<repos_base>`.

### Phase 1.5 — Classify

Jira-driven feature docs are typically **SIGNIFICANT** (large blast radius if wrong — published documentation). State classification and reason. SIGNIFICANT → no Opus planning (Jira read is the plan); but doc-reviewer gate is mandatory.

### Phase 2 — Plan + approval

Present: resolved JIRA_KEY, output file path, repos to examine, PRs in scope, parallelism plan. Ask for approval.

### Phase 3 — Read Jira hierarchy

Invoke `jira-reader` agent (Section 12) with `depth: full`. Wait for handoff.

### Phase 4 — Resolve repos

From the `jira-reader` handoff `pull_requests` list:
1. Parse each PR URL. Two hosts are supported (per §13 resolver selection):
   - `https://bitbucket.lab.dynatrace.org/projects/<PROJECT>/repos/<REPO>/pull-requests/<PR_ID>` → extract `<REPO>`.
   - `https://github.com/<OWNER>/<REPO>/pull/<PR_ID>` → extract `<REPO>` (and `<OWNER>` for `gh` use).
2. Filter by `status_marker` per Phase 1 setting (default: MERGED only).
3. For each unique repo, check `<repos_base>/<REPO>` exists using the path resolved at Phase 1.
4. If any repos missing, escalate using the rules in Section 15 (choices include "Skip and continue without its PRs", "I'll clone it — wait", "Cancel", and "Re-resolve with a different `<repos_base>`"). List missing repos explicitly.

### Phase 5 — Parallel diff summarization

Spawn `code-diff-summarizer` instances **in batches of up to 4 concurrent agents** (single Agent message per batch). Wait for all instances in a batch to return before spawning the next batch. If fewer than 4 repos remain, the final batch is smaller.

Rationale: Claude Code's practical parallel-subagent limit is ~4–5; going above that causes silent serialisation or rate-limiting. Capping at 4 makes runtime deterministic and keeps handoff latency predictable.

Handle `status: REPO_MISSING`, `DIRTY_TREE`, `REFRESH_BLOCKED`, `NO_PRS_RESOLVED`, or `PARTIAL` per Section 13 escalation rules.

### Phase 6 — Write documentation

Using `jira-reader` output + diff summaries as source of truth. Every claim must be traceable — cite the originating Jira key (`[[MGD-1127]]`) and PR URL inline. Write to cwd (see Section 11 for branch/write policy).

### Phase 6.5 — Branch setup (conditional)

Only when write context = `git_repo` AND user confirmed branching at plan approval. Never for `obsidian` or `plain_dir`.

Before creating the branch, run the same **clean-tree check** defined in `commands/impl/code.md` Pre-Phase 3: `git status --porcelain`, and if non-empty present the user with `choices: ["Stash changes and continue (Recommended)", "Proceed anyway — pre-existing changes will appear in the diff", "Cancel"]`. This avoids silently committing unrelated user work alongside the generated documentation. Branch prefix default: `docs/` (see §11).

### Phase 7 — Doc review gate

Invoke `doc-reviewer` agent (Section 9). Act on verdict:
- **BLOCK** → invoke `doc-fixer` (BLOCKER findings). Re-invoke `doc-reviewer` once. If still BLOCK: surface to user. Cap: one fix cycle + one re-review.
- **PASS WITH RECOMMENDATIONS** → invoke `doc-fixer` (MAJOR findings only). MINOR/NIT deferred to Phase 9 report.
- **PASS** → proceed.

### Phase 8 — Maintenance

All four Phase 4 maintenance agents (docs, knowledge base, instructions, session report). `change_type: docs` in session handoff.

### Phase 9 — Final report

Standard Phase 5 structure plus:
- `### Jira hierarchy summary`
- `### Repos analysed`
- `### PRs in scope`
- `### Output file(s)`
- `### Doc review verdict`

### Invariants

```
- NEVER call Bitbucket REST APIs — Bitbucket URLs are identifiers only; all resolution is pure local git
- GitHub URLs may use the `gh` CLI for head/base SHA resolution (see §13 GitHub resolver); no direct REST calls outside `gh`
- NEVER write inside _archive/ — that path is read-only by convention
- NEVER write inside jira-products/ — that path is read-only by convention
- NEVER write outside cwd unless user provides explicit absolute path
- ALWAYS escalate missing repos before proceeding — never silent skip
- ALWAYS invoke doc-reviewer before Phase 8
- Cap review/fix cycles: 1 fix + 1 re-review max
- All written claims must be traceable to Jira keys or PR diffs
```

---

## 7. `/impl:jira:epics` — Jira-driven Epic writing

### Purpose

Given a Jira Value Increment key, reads the VI and its existing Epics, optionally scans code repos to identify reusable code and gaps, drafts child Epic definitions in markdown, reviews, and writes output to cwd.

**Key distinction from `/impl:jira:docs`:** The VI being Epic-ized is NOT yet implemented — there are no PRs to diff. Code scanning is a plain filesystem search to understand what exists and what needs to be built.

### Phase 0 — Load

Same as `/impl:jira:docs`: resolve `$VAULT_PATH` and `<JIRA_KEY>`.

### Phase 1 — Clarification

Ask (grouped where possible, `choices` arrays, last choice always `"Other… (describe)"`):

- Output path under cwd (default: `<VI-KEY>/<NEW-EPIC-SLUG>.md` per Epic).
- Code examination on/off (default: ON) — if ON, ask which repos under `<repos_base>` to scan (defaults: repos referenced by sibling/parent Epics in the index; otherwise user lists them).
- Repo refresh policy: `fetch + pull default branch` `(Recommended)` / `fetch only` / `no refresh`.
- **Repos base path** — detect `/repos` (check existence) and ask:
  ```
  choices: ["Use /repos (Recommended)", "Use a different path (you'll be prompted)", "Cancel"]
  ```
  If "different path", follow up with a free-text entry and validate that at least one directory exists under it.

Also detect and show: resolved cwd absolute path, write context, whether branching will happen, and the resolved `<repos_base>`.

### Phase 1.5 — Classify

Epic writing is typically **MODERATE** (bounded scope, single VI). State classification.

### Phase 2 — Plan + approval

Present: VI summary, existing Epics identified (will not duplicate), repos to scan, output file layout. Ask for approval.

### Phase 3 — Read Jira hierarchy

Invoke `jira-reader` agent with `depth: vi-plus-epics` (reads the index + the VI's own `.md` + every Epic `.md` linked to the VI; Stories/Sub-tasks/Research/RFA are skipped). This depth is specifically designed for Epic-writing: richer than `vi-only` so themes extracted for `code-scanner` are not starved of context, lighter than `full` so the agent does not read dozens of already-closed child Stories. Identify already-linked Epics to avoid duplicate scope.

### Phase 4 — Resolve repos (conditional)

If code scan ON: verify each repo exists at `<repos_base>/<REPO>` (using the path resolved at Phase 1). Escalate missing repos per Section 15.

### Phase 5 — Parallel code scanning (conditional)

If code scan ON: spawn `code-scanner` instances **in batches of up to 4 concurrent agents** (single Agent message per batch). Wait for all instances in a batch to return before spawning the next batch. Each instance gets: capability themes from `jira-reader` output + VI goal as search seeds.

If code scan OFF: skip Phase 5.

### Phase 6 — Write Epics

Draft child Epic definitions — one file per Epic:
- `goal` (1 sentence)
- `business value` (1–2 sentences)
- `scope` (in / out)
- `acceptance criteria` (testable)
- `dependencies` (other Epics, repos, teams)
- `suggested stories` (high-level breakdown)
- `references` (Jira links, code paths if code scan was run)

Write to cwd (branch/write policy per Section 11). Show resolved absolute paths at plan approval.

### Phase 6.5 — Branch setup (conditional)

Same as `/impl:jira:docs` Phase 6.5 — including the pre-branch clean-tree check from `commands/impl/code.md` Pre-Phase 3 and the `docs/` branch prefix.

### Phase 7 — Doc review gate

Invoke `doc-reviewer` with `doc_type: jira-epic`. Same verdict handling as `/impl:jira:docs`.

### Phase 8 — Maintenance

All four Phase 4 maintenance agents. `change_type: docs`.

### Phase 9 — Final report

Standard structure plus:
- `### VI summary`
- `### Existing Epics (not duplicated)`
- `### New Epics written`
- `### Repos scanned`
- `### Doc review verdict`

---

## 8. Agent: `test-writer.md`

**Purpose:** Writes tests for new or changed behavior. Does NOT run tests.

**Model:** inherits session (no `model:` override in frontmatter).

**Tools:** Read, Glob, Grep, LS, Write, Edit

**Inputs:** Task description, plan, diff (`git diff` output), project root, baseline snapshot.

**Steps:**
1. Detect framework (same logic as `test-baseline`). If not detected: return "not detected" report immediately.
2. Map changed behavior from diff — identify new functions, changed logic, new branches, new API surface. Skip: pre-existing untested code, renames, comment-only changes.
3. Discover test patterns from 2–3 representative test files (naming, assertions, fixtures).
4. Write tests covering new/changed behavior only. Follow existing style exactly.

**Output:**
```markdown
## Test Writer Report
- **Framework**: [name | "not detected"]
- **Tests written**: [N]

### Tests added
- `[test name]` in `[file:line]` — covers [what behavior]

### Skipped (pre-existing untested code)
[list or "none"]

### Notes
[anything unusual or "none"]
```

---

## 9. Agent: `doc-reviewer.md`

**Purpose:** Reviews documentation for correctness, completeness, and fitness for purpose. Returns PASS / PASS WITH RECOMMENDATIONS / BLOCK.

**Model:** `opus` (declared in frontmatter). Mirrors the Opus-backed gate role of `code-review` — this agent decides whether to BLOCK the run, so it needs the strongest reasoning model available. Do NOT down-grade to session model.

**Tools:** Read, Glob, Grep, LS

**Inputs:** Written doc file path(s), Jira directory path (for cross-check), diff summaries or code-scanner output, `doc_type: product-docs | jira-epic`.

**Review dimensions:**

| Dimension | product-docs | jira-epic |
|---|---|---|
| Factual correctness | Matches Jira + code diffs | Matches Jira + code scan |
| Completeness | All changed behavior covered | All gaps identified; no scope missing |
| Audience fit | End-user clarity | Engineering handoff clarity |
| Structural integrity | Headings, links, `[[wikilinks]]` | Headings, links, `[[wikilinks]]` |
| Actionability | Examples runnable; commands copyable verbatim; links resolve | Acceptance criteria testable; gaps specified |
| Source traceability | Claims cite Jira keys + PRs | Claims cite Jira keys + code paths |

**Verdict:** PASS (no findings above MINOR), PASS WITH RECOMMENDATIONS (MAJOR/MINOR/NIT only), BLOCK (at least one BLOCKER). Same output shape as `code-review.md`.

---

## 10. Agent: `doc-fixer.md`

**Purpose:** Applies targeted fixes for BLOCKER and MAJOR doc review findings. Analogous to `review-fixer.md`.

**Model:** inherits session (no `model:` override in frontmatter). Mirrors `review-fixer` — fixes are targeted, no deep reasoning required.

**Tools:** Read, Glob, Grep, LS, Write, Edit

**Inputs:** Doc file path(s), full `doc-reviewer` output, severities to fix.

**Hard rules:**
- NEVER rewrite whole sections when only a targeted edit is needed.
- NEVER fix MINOR or NIT findings.
- NEVER modify files not referenced in the review findings.

---

## 11. Branch and write policy (Jira commands)

Output is always written to **cwd** (where Claude Code was started). Branch behavior is determined by inspecting cwd:

| Detected context | Branch | Commit |
|---|---|---|
| **Obsidian vault** — `.obsidian/` found at any ancestor of cwd | NEVER | NEVER |
| **Other git repo** — `git rev-parse --show-toplevel` succeeds AND no `.obsidian/` ancestor (e.g. Dynatrace docs repo) | YES (opt-in confirmed at plan approval) | YES |
| **Not in any git repo** | NEVER | NEVER |

**Detection algorithm:**
```bash
# 1. Walk up from cwd looking for .obsidian/ — if found, treat as Obsidian (no git ops)
dir="$(pwd)"
while [ "$dir" != "/" ]; do
  [ -d "$dir/.obsidian" ] && { context=obsidian; break; }
  dir="$(dirname "$dir")"
done

# 2. Otherwise check git repo
[ -z "$context" ] && git rev-parse --show-toplevel >/dev/null 2>&1 \
  && context=git_repo || context=plain_dir
```

When branching (only `git_repo`): reuse the clean-tree check and slug derivation from `commands/impl/code.md` Pre-Phase 3. Default branch prefix: `docs/`.

Always show at plan approval: resolved absolute output path, detected context, whether branching+commit will happen.

---

## 12. Agent: `jira-reader.md`

**Purpose:** Reads the pre-exported Jira markdown hierarchy from the vault. Read-only — never modifies vault files.

**Model:** inherits session (no `model:` override in frontmatter).

**Tools:** Read, Glob, Grep, LS

**Inputs:**
```yaml
vault_path: <absolute path>
jira_key:   <e.g. PRODUCT-14902>
depth:      full | vi-plus-epics | vi-only
```

**Process:**

**Phase 0 — Validate `jira_key`.** Accept only `^[A-Z][A-Z0-9_]*-\d+$` (Jira key convention: uppercase letters / digits / underscores, a dash, digits). On mismatch, return `status: NOT_FOUND` with a clear message naming the invalid key — caller surfaces the Section 15 `Jira key dir not found` choices to the user.

1. Read `<vault_path>/jira-products/<jira_key>/<jira_key>-index.md`. **Header validation:** the first data table in the file must have header row `| Key | Type | Status | Summary | Role |` exactly. If the header differs (e.g. Jira-to-Obsidian exporter changed its output format), return `status: EMPTY` with a message naming the mismatched columns — do **not** try to parse rows with an unknown schema. Document the assumed exporter version in the plugin README.
2. If `depth: full` — for every linked item (including the root VI itself, which lives in its own sub-directory), read `<vault_path>/jira-products/<jira_key>/<LINKED_KEY>/<LINKED_KEY>.md`. Parse YAML frontmatter, extract the Description body, and collect PR URLs from the `## Pull Requests` section.
3. If `depth: vi-plus-epics` — read the VI's own file at `<vault_path>/jira-products/<jira_key>/<jira_key>/<jira_key>.md` **plus** every Epic `.md` directly linked to the VI (filter the linked-items table to `type == Epic`). Skip Stories, Sub-tasks, Research, Request for Assistance. This gives Epic-writing workflows enough context to extract meaningful themes for `code-scanner` without reading the entire hierarchy.
4. If `depth: vi-only` — read only the VI's own file at `<vault_path>/jira-products/<jira_key>/<jira_key>/<jira_key>.md` plus the index. Every linked item is nested under the root export directory; never look for `<vault_path>/jira-products/<LINKED_KEY>/<LINKED_KEY>.md` (that path does not exist).
5. Extract capability themes (2–4 short bullets summarizing recurring topics) for use by `code-scanner`. Themes may be sparse for `depth: vi-only`; callers that need richer themes should request `vi-plus-epics` or `full`.

**Ignored by default:** sibling `<KEY>-comments.md` files and `attachments/` sub-directories inside each item's folder. Rationale: comments and image attachments are occasionally useful for decision-history context but are noisy, rarely authoritative for user-facing docs, and easy to revisit manually when needed. Keeping them out of the default read path also keeps `jira-reader` fast on large VIs. No user-facing toggle is provided in this iteration.

**PR URL formats to parse:**

Two hosts are recognised; any other URL is recorded as-is with `status: UNKNOWN` and is surfaced later by `code-diff-summarizer` as `unresolved`.

- Bitbucket Server (Dynatrace instance):
  ```
  https://bitbucket.lab.dynatrace.org/projects/<PROJECT_KEY>/repos/<REPO_NAME>/pull-requests/<PR_ID>
  ```
- GitHub Cloud:
  ```
  https://github.com/<OWNER>/<REPO_NAME>/pull/<PR_ID>
  ```

**Assumption:** `bitbucket.lab.dynatrace.org` is the only supported Bitbucket Server host in this iteration; other self-hosted Bitbucket instances would need an additional resolver. Also parse the `Branch:` line and status marker (`**MERGED**` / `**OPEN**` / `**DECLINED**`) — present in both formats.

**Output (structured handoff):**
```yaml
status: OK | EMPTY | NOT_FOUND
jira_key: <key>
value_increment:
  key:     <key>
  summary: <text>
  status:  <text>
  goal:    <2–3 sentence extraction from Description>
linked_items:
  - key: <key>
    type: ValueIncrement | Epic | Story | Sub-task | Research | "Request for Assistance"
    status: <text>
    summary: <text>
    parent: <key | null>
    role:   root | linked | epic_child
pull_requests:
  - url:         <full URL>
    host:        bitbucket.lab.dynatrace.org | github.com | other
    repo:        <repo name extracted from URL>
    owner:       <for github.com only — the <OWNER> path segment; null for bitbucket>
    pr_id:       <id>
    status:      MERGED | OPEN | DECLINED | UNKNOWN
    source_item: <Jira key the URL was found in>
    title:       <link text from markdown>
    branch_from: <feature branch, from Branch: line>
    branch_to:   <target branch, from Branch: line>
themes:
  - <2–4 short bullet points summarising recurring topics across items>
```

---

## 13. Agent: `code-diff-summarizer.md`

**Purpose:** Reads a single code repository's PR diff and returns a documentation-focused summary. Designed for parallel invocation — one instance per repo, capped at 4 concurrent (see §6 Phase 5 / §7 Phase 5).

**Model:** inherits session (no `model:` override in frontmatter).

**Tools:** Read, Glob, Grep, LS, Bash

**Inputs:**
```yaml
repo_path:   <absolute, e.g. /repos/cluster>
pr_refs:
  - url:         <full PR URL>
    host:        bitbucket.lab.dynatrace.org | github.com | other
    repo:        <repo name>
    owner:       <github only; null for bitbucket>
    pr_id:       <id>
    branch_from: <feature branch from jira-reader>
    branch_to:   <target branch from jira-reader>
    title:       <link text>
    status:      MERGED | OPEN | DECLINED | UNKNOWN
context: |
  <what this repo's PRs relate to, for doc focus>
refresh:
  fetch: true   # default true
  pull:  false  # default false — historical PR diffs do not need the current branch tip;
                # pulling risks moving HEAD away from the merge commit we want to reach.
                # (Asymmetry with code-scanner, which pulls by default — it targets present-day
                # capability scans. See §14.)
```

**Resolver selection by host:**

Before attempting any git operation, inspect `pr_refs[*].host` and route per-PR to the matching resolver:

| Host | Resolver | Notes |
|---|---|---|
| `bitbucket.lab.dynatrace.org` | **Bitbucket local-git resolver** (below) — pure local git, no HTTPS calls | Strategies 1–4 cascade; Strategies 2 and 3 are the workhorse |
| `github.com` | **GitHub resolver via `gh` CLI** (below) — `gh` handles HTTPS + auth; head/base SHAs come back as structured JSON | Requires `gh auth login` on the host; see §17 prerequisites |
| anything else | Record as `unresolved` with `reason: unsupported host <host>`; caller escalates | Non-Bitbucket-Server, non-GitHub hosts are out of scope for this iteration |

**URL parse note:** for Bitbucket URLs, extract **only** `<REPO_NAME>` for the local-lookup path `<repos_base>/<REPO_NAME>`. The `<PROJECT_KEY>` prefix (`RX`, `sus`, etc.) identifies the Bitbucket project namespace on the server and plays no role in local resolution — do not confuse the two or try to match both. For GitHub URLs, `<REPO_NAME>` is similarly the only piece used for the repo path; `<OWNER>` is passed to `gh --repo <OWNER>/<REPO>` but not used in the filesystem path.

**Bitbucket local-git resolver (pure local git — NO HTTPS calls ever):**

The default Bitbucket Server clone does **not** fetch `refs/pull-requests/*/from` refs — so Strategy 1 below is an optimistic first attempt that rarely hits unless the user has pre-configured the extra refspec and run `git fetch` manually. **Strategies 2 and 3 are the real workhorse** for Bitbucket repos; treat Strategy 1 as best-effort and fall through silently when it misses.

1. **Strategy 1 — Bitbucket Server PR refs (optimistic; usually absent).** Try `git rev-parse refs/pull-requests/<pr_id>/from`. If present, use as head; derive base via `git merge-base <target_branch> <head>`. If the ref does not exist (the default for a fresh clone), fall through to Strategy 2. Do **not** attempt to configure the refspec or fetch it at runtime — that is an explicit opt-in step for the user, not an automatic side effect.
2. **Strategy 2 — Branch search.** `git branch -a --list "*<pr_id>*"` and `git branch -a --list "*<issue_key>*"`. If unique match → use as head.
3. **Strategy 3 — Merge-commit search.** `git log --all -E --grep="[Pp]ull[ _-]?[Rr]equest[ _-]?#?<pr_id>\b" -n 5` and `git log --all -E --grep="<title_keyword>" -n 5`. The primary pattern matches the Bitbucket / GitHub merge-commit title format `Pull request #<PR_ID>: …` (note the `#` separator — a previous draft used `pull[- ]request[- ]<pr_id>` which did not match). For a merge commit: head = `<commit>^2`, base = `<commit>^1`.
4. **Strategy 4 — Last resort.** `git log --all --grep="<issue_key>" --oneline` to surface candidates. Do NOT auto-pick; record under `unresolved_prs`.

If none resolve: record as `unresolved` and continue (caller escalates).

**Note on non-MERGED PRs:** The default filter is MERGED-only. If the caller opts into OPEN / DECLINED / UNKNOWN PRs, expect a high rate of `unresolved`: DECLINED PRs often have no merge commit (Strategy 3 fails) and feature branches may have been deleted after decline (Strategy 2 fails). Surface the unresolved count clearly in `aggregate_summary` so the documentation writer knows what's missing.

**GitHub resolver (via `gh` CLI):**

1. **Resolve head/base SHAs.** Run `gh pr view <pr_id> --repo <owner>/<repo> --json headRefOid,baseRefOid,state,title,mergeCommit`. This is the single authoritative call. `gh` handles authentication via `gh auth login` (configured once on the host; see §17).
2. **Ensure commits are local.** If `headRefOid` or `baseRefOid` is missing from the local clone (`git cat-file -e <sha>` returns non-zero), run `git fetch origin <headRefOid> <baseRefOid>`. If fetch is rejected (server refuses direct-SHA fetch), fall back to `gh pr checkout <pr_id> --repo <owner>/<repo>` which fetches the branches.
3. **Produce diff.** `git diff <baseRefOid>..<headRefOid>`. Set `resolved_via: gh_cli`.
4. **Failure modes:** `gh` not installed → `status: REFRESH_BLOCKED` with reason `gh CLI not found`. Not authenticated → `status: REFRESH_BLOCKED` with reason `gh auth required`. PR not found (deleted, private, wrong repo) → record in `unresolved_prs` with the gh error.

**Output:**
```yaml
status:   OK | REPO_MISSING | DIRTY_TREE | REFRESH_BLOCKED | NO_PRS_RESOLVED | PARTIAL
repo:      <short repo name — the basename of repo_path>
repo_path: <absolute path as received in input, so callers can reference the source tree>
per_pr:
  - pr_id: <id>
    resolved_via: pr_ref | branch_search | merge_commit | issue_grep | gh_cli | unresolved
    summary: |
      <prose; 3–8 sentences: new behavior, changed behavior, API surface>
unresolved_prs:
  - pr_id: <id>
    reason: <why resolution failed>
    candidates: [<sha — first line, if Strategy 4 found any>]
aggregate_summary: |
  <1–2 paragraphs: what this repo contributed to the feature. If any non-MERGED PRs were
  in scope and ended up unresolved, state the count explicitly so the doc writer knows.>
```

---

## 14. Agent: `code-scanner.md`

**Purpose:** Scans a single code repo for existing capabilities and gaps relative to a set of themes from a Value Increment / Epic. Used for Epic writing where there are no PRs (feature not yet implemented). Designed for parallel invocation — one instance per repo, capped at 4 concurrent (see §7 Phase 5).

**Model:** inherits session (no `model:` override in frontmatter).

**Tools:** Read, Glob, Grep, LS, Bash

**Inputs:**
```yaml
repo_path:   <absolute, e.g. /repos/cluster>
capability_themes:
  - <short phrase, e.g. "ActiveGate auto-update windows">
context: |
  <3–5 sentences: VI goal, what the Epic-set is meant to achieve>
search_hints:
  symbols:  [<class/function names>]
  paths:    [<directory globs, e.g. "**/autoupdate/**">]
  keywords: [<grep keywords>]
refresh:
  switch_to_default_branch: true
  pull: true   # default true — capability scans target present-day code and want the
               # default-branch tip. (Asymmetry with code-diff-summarizer, which keeps
               # pull: false because it targets historical merged commits. See §13.)
```

**Process:**
1. Verify repo exists. If not → return `status: REPO_MISSING`.
2. Prep step: `git status --porcelain` → if dirty and refresh is true → return `status: DIRTY_TREE`. Switch to default branch + `git pull --ff-only` if configured.
3. Scan — pure filesystem (`grep`/`glob`/`read`), no git involvement. For each theme: search by keywords, symbols, paths. Collect file paths and top-level symbols.
4. Read head (~80 lines) of top candidate files per theme to characterize the capability.
5. Classify each theme: `present` (clear existing implementation), `partial` (related but incomplete), `absent` (gap).

**Output:**
```yaml
status:    OK | PARTIAL | REPO_MISSING | DIRTY_TREE | REFRESH_BLOCKED | EMPTY
repo:      <short repo name — the basename of repo_path>
repo_path: <absolute path as received in input>
capability_map:
  - theme: <theme text>
    classification: present | partial | absent | error
    evidence:
      - path: <relative to repo>
        symbols: [<names>]
        note: <one-line characterisation>
    gap_summary: |
      <only when partial/absent — what's missing>
    error: <only when classification == error — one-line reason>
reusable_components: |
  <1–2 paragraphs: what existing code the new Epic can build on>
gap_summary: |
  <1–2 paragraphs: what needs to be implemented from scratch>
```

`PARTIAL` is returned when some themes completed successfully but at least one failed (e.g. permission error on a sub-tree, file-read error, timeout). Failing themes are marked `classification: error` in the `capability_map` with a one-line reason; the overall scan is not aborted. This mirrors `code-diff-summarizer`'s `PARTIAL` status so callers have a consistent recovery pattern.

---

## 15. Escalation rules (both Jira commands)

| Situation | Choices |
|---|---|
| `$VAULT_PATH` unset | "Set to detected path (Recommended)", "Enter manually", "Cancel" |
| Jira key dir not found | "Re-enter key", "Cancel" |
| Repo missing under `/repos/` | "Skip and continue without its PRs", "I'll clone it — wait", "Cancel", "Use different /repos path" |
| `git fetch` failed | "Continue with current local state", "Skip this repo", "Cancel" |
| `unresolved_prs` returned | "Show candidates and let me pick", "Skip this PR", "Skip this repo", "Cancel" |
| Use case B with no repos derivable from index | "List repos to scan manually", "Proceed without code scan", "Cancel" |
| `doc-reviewer` BLOCK after one fix cycle | For each unresolved BLOCKER, ask individually: `["Provide manual fix notes (you'll be prompted)", "Defer to a follow-up issue (record in Phase 9 report)", "Override and accept the finding", "Cancel the whole run"]`. "Cancel" aborts. "Override" records the override + rationale in the Phase 9 `### Deferred items` section. "Defer" records the finding there without an override flag. "Manual fix notes" lets the user type the fix text, which is then applied by `doc-fixer` in a bounded one-shot pass. |
| Output file already exists | "Write with -v2 suffix (Recommended — non-destructive)", "Append", "Overwrite", "Cancel" |

---

## 16. Success criteria

1. `/impl:code` on a code change produces a passing test for the new behavior before marking done.
2. `/impl:docs` on a simple doc change does not trigger tests, branching, or code review.
3. `/impl:jira:docs` on a VI key reads the vault markdown, summarizes merged PR diffs from local repos, writes traceable documentation, and passes doc-reviewer.
4. `/impl:jira:epics` on a VI key reads the vault markdown, scans code repos for reuse/gaps, writes child Epics with testable acceptance criteria, and passes doc-reviewer.
5. All existing regression baseline behavior from the original `/impl` is preserved unchanged.
6. All new/modified files follow existing `dev-workflows` plugin conventions.
7. `/impl` continues to work without modification to existing invocations.

---

## 17. Out of scope

- Standalone `/write-tests` command (test-writer is internal pipeline agent only)
- HTTPS/REST API calls to Bitbucket Server (pure local git + filesystem only; GitHub is the sole exception — it's handled via the `gh` CLI wrapper, not raw HTTPS)
- PR creation (branch + commit only; PR is a future task)
- Rewriting Jira items (jira-reader is read-only)
- Cloning missing repos (escalate to user instead)
- Non-`bitbucket.lab.dynatrace.org` Bitbucket Server hosts, and Git hosts other than `github.com` (deferred — would need an additional resolver)
- Changes outside `plugins/dev-workflows` (flag before touching)

### Environment prerequisites

- **`gh auth login`** must be run once on the host before `/impl:jira:docs` or `/impl:jira:epics` will resolve GitHub PRs. The GitHub resolver shells out to `gh` and relies on its configured credentials; without an authenticated session, the resolver returns `status: REFRESH_BLOCKED` with reason `gh auth required`.
- **Recommended environment: AI Container.** These commands work best when the agent is run inside the [ihudak/ai-containers](https://github.com/ihudak/ai-containers) environment, which:
  - Mounts `/repos` with all relevant code repositories already cloned, so the default `<repos_base>` just works.
  - Installs `gh` automatically.
  - Mounts `~/.config/gh` from the host, so `gh` authentication carries over transparently — `gh auth login` on the host is sufficient, no re-auth inside the container.

  Outside this environment the commands still function, but the user must manage `<repos_base>`, `gh` installation, and `gh auth login` themselves.
