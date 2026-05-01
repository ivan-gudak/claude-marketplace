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
  impl:code.md          ← canonical full code workflow + test-writing phase
  impl:docs.md          ← one-shot doc editing workflow
  impl:jira:docs.md     ← Jira + PR diffs → feature documentation
  impl:jira:epics.md    ← Jira VI + code scan → Epic writing
```

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
    impl.md               ← alias note + delegates to impl:code.md
  .claude-plugin/
    plugin.json           ← register all new commands
  README.md               ← update command and agent tables
  CHANGELOG.md            ← add entry
.claude-plugin/
  marketplace.json        ← version bump
```

### `impl.md` alias pattern

`impl.md` opens with:

> **Alias:** This command is equivalent to `/impl:code`. For documentation/markdown changes, use `/impl:docs`. For Jira-driven feature docs, use `/impl:jira:docs`. For writing child Epics, use `/impl:jira:epics`.

Then reads and executes `~/.claude/plugins/data/dev-workflows@ihudak-claude-plugins/commands/impl:code.md` with `$ARGUMENTS` forwarded.

---

## 4. `/impl:code` — workflow changes

All existing phases from `impl.md` are preserved. Two insertions are made.

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

1. Invoke `test-writer` agent (Section 6).
2. If test-writer returns `Framework: not detected`:
   ```
   choices: ["Specify test command to use", "Skip tests for this run (document why in Phase 5 report)", "Cancel"]
   ```
3. Run linters/builds.
4. Invoke `test-baseline` in verify mode against the captured baseline.
5. If regressions or new test failures: fix, re-run verify (max 2 attempts). If still failing: surface to user with `choices: ["Investigate further", "Accept regressions and proceed", "Cancel"]`.

#### For SIGNIFICANT/HIGH-RISK (inside Phase 3B):

- **After step 4** (implementation complete), **before step 5** (diff capture):
  - Invoke `test-writer` agent.
  - If `Framework: not detected`: note it, include in handoff to Opus.
- **Step 5 diff** now includes test files → Opus reviews code and tests together (test adequacy is already a review dimension in `code-review.md`).
- Phase 3.5 runs **after** the review gate clears (non-BLOCK verdict), replacing steps 8–10 of the original Phase 3B (run tests, fix failures, re-run).

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
2. Resolve `<JIRA_KEY>` from `$ARGUMENTS`; validate `$VAULT_PATH/_archive/jira-products/<JIRA_KEY>/` exists. If not: stop with error.

### Phase 1 — Clarification

Ask (one question per message, `choices` arrays, last choice always `"Other… (describe)"`):
- Output filename / sub-path under cwd (default: `<KEY>-<slug>.md`)
- PR status filter (MERGED only (Recommended) / all / specific list)
- Repo refresh policy: `fetch only` (Recommended) / `fetch + pull default branch` / `no refresh`

Also detect and show: resolved cwd absolute path, write context (obsidian / git_repo / plain_dir — see Section 11), whether branching will happen.

### Phase 1.5 — Classify

Jira-driven feature docs are typically **SIGNIFICANT** (large blast radius if wrong — published documentation). State classification and reason. SIGNIFICANT → no Opus planning (Jira read is the plan); but doc-reviewer gate is mandatory.

### Phase 2 — Plan + approval

Present: resolved JIRA_KEY, output file path, repos to examine, PRs in scope, parallelism plan. Ask for approval.

### Phase 3 — Read Jira hierarchy

Invoke `jira-reader` agent (Section 12) with `depth: full`. Wait for handoff.

### Phase 4 — Resolve repos

From the `jira-reader` handoff `pull_requests` list:
1. Parse each PR URL: `https://bitbucket.lab.dynatrace.org/projects/<PROJECT>/repos/<REPO>/pull-requests/<PR_ID>` → extract `<REPO>`.
2. Filter by `status_marker` per Phase 1 setting (default: MERGED only).
3. For each unique repo, check `<repos_base>/<REPO>` exists (default `/repos`; ask at Phase 1 if different path needed).
4. If any repos missing:
   ```
   choices: ["Mount the missing repos and retry", "Skip missing repos and proceed with available ones", "Cancel the run", "Use a different /repos path"]
   ```
   List missing repos explicitly.

### Phase 5 — Parallel diff summarization

Spawn one `code-diff-summarizer` instance per repo simultaneously (single Agent message, all in parallel). Wait for all to return. Handle `status: REPO_MISSING`, `DIRTY_TREE`, `REFRESH_BLOCKED` per Section 13 escalation rules.

### Phase 6 — Write documentation

Using `jira-reader` output + diff summaries as source of truth. Every claim must be traceable — cite the originating Jira key (`[[MGD-1127]]`) and PR URL inline. Write to cwd (see Section 11 for branch/write policy).

### Phase 6.5 — Branch setup (conditional)

Only when write context = `git_repo` AND user confirmed branching at plan approval. Never for `obsidian` or `plain_dir`.

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
- NEVER call Bitbucket/GitHub REST APIs — PR URLs are identifiers only; all resolution is pure local git
- NEVER write inside _archive/ — that path is read-only by convention
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

Ask:
- Output path under cwd (default: `<VI-KEY>/<NEW-EPIC-SLUG>.md` per Epic)
- Code examination on/off (default: ON) — if ON, ask which repos under `/repos` to scan (defaults: repos referenced by sibling/parent Epics in the index; otherwise user lists them)
- Repo refresh policy: `fetch + pull default branch` (Recommended) / `fetch only` / `no refresh`

### Phase 1.5 — Classify

Epic writing is typically **MODERATE** (bounded scope, single VI). State classification.

### Phase 2 — Plan + approval

Present: VI summary, existing Epics identified (will not duplicate), repos to scan, output file layout. Ask for approval.

### Phase 3 — Read Jira hierarchy

Invoke `jira-reader` agent with `depth: vi-only`. Identify already-linked Epics to avoid duplicate scope.

### Phase 4 — Resolve repos (conditional)

If code scan ON: verify each repo exists at `/repos/<REPO>`. Escalate missing repos per Section 13.

### Phase 5 — Parallel code scanning (conditional)

If code scan ON: spawn one `code-scanner` instance per repo simultaneously. Wait for all to return. Each instance gets: capability themes from `jira-reader` output + VI goal as search seeds.

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

Same as `/impl:jira:docs`.

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

**Tools:** Read, Glob, Grep, LS

**Inputs:** Written doc file path(s), Jira directory path (for cross-check), diff summaries or code-scanner output, `doc_type: product-docs | jira-epic`.

**Review dimensions:**

| Dimension | product-docs | jira-epic |
|---|---|---|
| Factual correctness | Matches Jira + code diffs | Matches Jira + code scan |
| Completeness | All changed behavior covered | All gaps identified; no scope missing |
| Audience fit | End-user clarity | Engineering handoff clarity |
| Structural integrity | Headings, links, `[[wikilinks]]` | Headings, links, `[[wikilinks]]` |
| Actionability | N/A | Acceptance criteria testable; gaps specified |
| Source traceability | Claims cite Jira keys + PRs | Claims cite Jira keys + code paths |

**Verdict:** PASS (no findings above MINOR), PASS WITH RECOMMENDATIONS (MAJOR/MINOR/NIT only), BLOCK (at least one BLOCKER). Same output shape as `code-review.md`.

---

## 10. Agent: `doc-fixer.md`

**Purpose:** Applies targeted fixes for BLOCKER and MAJOR doc review findings. Analogous to `review-fixer.md`.

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

When branching (only `git_repo`): reuse the clean-tree check and slug derivation from `impl:code.md` Pre-Phase 3. Default branch prefix: `docs/`.

Always show at plan approval: resolved absolute output path, detected context, whether branching+commit will happen.

---

## 12. Agent: `jira-reader.md`

**Purpose:** Reads the pre-exported Jira markdown hierarchy from the vault. Read-only — never modifies vault files.

**Tools:** Read, Glob, Grep, LS

**Inputs:**
```yaml
vault_path: <absolute path>
jira_key:   <e.g. PRODUCT-14902>
depth:      full | vi-only
```

**Process:**
1. Read `<vault_path>/_archive/jira-products/<jira_key>/<jira_key>-index.md` — parse the work-items table (`| Key | Type | Status | Summary | Role |`).
2. If `depth: full` — read `<KEY>/<KEY>.md` for every linked item; parse YAML frontmatter; extract Description body; collect PR URLs from `## Pull Requests` section.
3. If `depth: vi-only` — read only the VI's own `<KEY>.md` plus the index.
4. Extract capability themes (2–4 short bullets summarizing recurring topics) for use by `code-scanner`.

**PR URL format to parse:**
```
https://bitbucket.lab.dynatrace.org/projects/<PROJECT_KEY>/repos/<REPO_NAME>/pull-requests/<PR_ID>
```
Also parse the `Branch:` line and status marker (`**MERGED**` / `**OPEN**` / `**DECLINED**`).

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
    repo:        <repo name extracted from URL>
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

**Purpose:** Reads a single code repository's PR diff and returns a documentation-focused summary. Designed for parallel invocation — one instance per repo.

**Tools:** Read, Glob, Grep, LS, Bash

**Inputs:**
```yaml
repo_path:   <absolute, e.g. /repos/cluster>
pr_refs:
  - url:         <full PR URL — identifier only, never fetched via HTTPS>
    pr_id:       <id>
    branch_from: <feature branch from jira-reader>
    branch_to:   <target branch from jira-reader>
    title:       <link text>
    status:      MERGED | OPEN | DECLINED | UNKNOWN
context: |
  <what this repo's PRs relate to, for doc focus>
refresh:
  fetch: true   # default true
  pull:  false  # default false
```

**PR resolution (pure local git — NO HTTPS calls ever):**

1. **Strategy 1 — Bitbucket Server PR refs.** Try `git rev-parse refs/pull-requests/<pr_id>/from`. If present, use as head; derive base via `git merge-base <target_branch> <head>`.
2. **Strategy 2 — Branch search.** `git branch -a --list "*<pr_id>*"` and `git branch -a --list "*<issue_key>*"`. If unique match → use as head.
3. **Strategy 3 — Merge-commit search.** `git log --all --grep="pull[- ]request[- ]<pr_id>" -n 5` and `git log --all --grep="<title_keyword>" -n 5`. For merge commit: head = `<commit>^2`, base = `<commit>^1`.
4. **Strategy 4 — Last resort.** `git log --all --grep="<issue_key>" --oneline` to surface candidates. Do NOT auto-pick; record under `unresolved_prs`.

If none resolve: record as `unresolved` and continue (caller escalates).

**Output:**
```yaml
status: OK | REPO_MISSING | DIRTY_TREE | REFRESH_BLOCKED | NO_PRS_RESOLVED | PARTIAL
repo: <repo name>
per_pr:
  - pr_id: <id>
    resolved_via: pr_ref | branch_search | merge_commit | issue_grep | unresolved
    summary: |
      <prose; 3–8 sentences: new behavior, changed behavior, API surface>
unresolved_prs:
  - pr_id: <id>
    reason: <why resolution failed>
    candidates: [<sha — first line, if Strategy 4 found any>]
aggregate_summary: |
  <1–2 paragraphs: what this repo contributed to the feature>
```

---

## 14. Agent: `code-scanner.md`

**Purpose:** Scans a single code repo for existing capabilities and gaps relative to a set of themes from a Value Increment / Epic. Used for Epic writing where there are no PRs (feature not yet implemented). Designed for parallel invocation.

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
  pull: true
```

**Process:**
1. Verify repo exists. If not → return `status: REPO_MISSING`.
2. Prep step: `git status --porcelain` → if dirty and refresh is true → return `status: DIRTY_TREE`. Switch to default branch + `git pull --ff-only` if configured.
3. Scan — pure filesystem (`grep`/`glob`/`read`), no git involvement. For each theme: search by keywords, symbols, paths. Collect file paths and top-level symbols.
4. Read head (~80 lines) of top candidate files per theme to characterize the capability.
5. Classify each theme: `present` (clear existing implementation), `partial` (related but incomplete), `absent` (gap).

**Output:**
```yaml
status: OK | REPO_MISSING | DIRTY_TREE | REFRESH_BLOCKED | EMPTY
repo: <repo name>
capability_map:
  - theme: <theme text>
    classification: present | partial | absent
    evidence:
      - path: <relative to repo>
        symbols: [<names>]
        note: <one-line characterisation>
    gap_summary: |
      <only when partial/absent — what's missing>
reusable_components: |
  <1–2 paragraphs: what existing code the new Epic can build on>
gap_summary: |
  <1–2 paragraphs: what needs to be implemented from scratch>
```

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
| `doc-reviewer` BLOCK after one fix cycle | Ask per unresolved BLOCKER with direct fix question + "Defer", "Override" |
| Output file already exists | "Overwrite", "Append", "Write with -v2 suffix", "Cancel" |

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
- Any HTTPS/REST API calls to Bitbucket or Jira (pure local git + filesystem only)
- PR creation (branch + commit only; PR is a future task)
- Rewriting Jira items (jira-reader is read-only)
- Cloning missing repos (escalate to user instead)
- Handling non-Bitbucket PR URL formats (deferred)
- Changes outside `plugins/dev-workflows` (flag before touching)
