# obsidian-llm-wiki — Claude Code Instructions

LLM Wiki pattern for an active Obsidian vault. Compiles knowledge from meetings,
projects, daily notes, and raw sources into a persistent, cross-referenced wiki at
`wiki/`. Supports both Claude Code (slash commands) and GitHub Copilot
(natural language prefixes). Wiki sessions from both agents accumulate into the same
wiki — switching between them mid-project is seamless.

---

## Vault Path

Default vault: `~/obsidian_vault` (Linux/Mac). WSL users with vault on Windows side must set
`VAULT_PATH=/mnt/c/Users/<name>/obsidian_vault`. Override with the `VAULT_PATH` env var.

All file paths in skill instructions are relative to the vault root unless they start
with `skills/` (which are relative to this plugin's installation directory).

---

## Commands

| Slash Command | Description |
|---------------|-------------|
| `/wiki-ingest @filepath` | Ingest one source file into the wiki |
| `/wiki-scan [directory]` | Scan directory for unprocessed files, batch-ingest new/changed |
| `/wiki-query <question>` | Answer from the compiled wiki with citations |
| `/wiki-save` | Save current conversation as a wiki page |
| `/wiki-lint` | Run wiki health check, produce lint report |
| `/wiki-hot` | Manually refresh the hot cache |
| `/wiki-tags-refresh` | Sync wiki tags with vault's tag-index.md |
| `/wiki-init` | Initialize vault integration (first run or after plugin update) |

---

## Wiki Schema

Before any wiki operation, the relevant skill will read `skills/wiki-schema/SKILL.md`
for full vault conventions: three-layer source model, page types, frontmatter schemas,
tag rules, cross-linking rules, and file formats.

---

## Boundary Rules

Wiki operations MUST NEVER write to or delete files from:
`Meetings/`, `Daily/`, `Projects/`, `Customers/`, `People/`, `Clippings/`, `Research/`

The wiki layer reads these directories. It never modifies them.

The only directory wiki may clean up is `.raw/` — by moving processed files to
`.raw/_processed/YYYY-MM/` after successful ingest.

The existing task system (`/task`, `/impl`, etc.) is completely separate. Wiki
operations do not create tasks, do not touch `Tasks.md`, and do not modify project
files in `Projects/`.

---

## Tags

Only use tags from `.obsidian/copilot/tag-index.md`. Never invent new tags. If a
concept needs a tag that does not exist, flag it with `tag-needed: <proposed>` in the
log entry and let the user approve it via `/wiki-tags-refresh`.

---

## Hot Cache

`wiki/hot.md` is a rolling ≤300-word session-continuity cache. Claude Code
auto-reads it at session start (SessionStart hook) and auto-updates it at session end
(Stop hook). Manually refresh with `/wiki-hot` if the cache is stale or missing.
