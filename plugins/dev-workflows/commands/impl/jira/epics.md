<!-- STUB — Increment D. Full workflow per design spec §7. -->

`/impl:jira:epics` is under construction.

This command will be the Jira-driven Epic-writing workflow: requires cwd inside `$VAULT_PATH`; reads the VI plus its existing Epics via `jira-reader` (depth `vi-plus-epics`); optionally scans code repos with `code-scanner`; drafts child Epic markdown files to `$VAULT_PATH/jira-drafts/<VI-KEY>/`; gates on `epic-reviewer` (Opus). Never branches, never commits — vault git management is the user's responsibility.

Depends on five subagents that will be added in Increment D: `jira-reader`, `code-scanner`, `epic-reviewer`, `doc-fixer`, plus the shared `impl-maintenance`.

**Until this stub is replaced**, Epic drafts must be written manually into `$VAULT_PATH/jira-drafts/<VI-KEY>/`.

For now, this file exists so Claude Code can load the plugin's new namespaced command layout without error. Invoking `/impl:jira:epics <JIRA_KEY>` prints this notice.
