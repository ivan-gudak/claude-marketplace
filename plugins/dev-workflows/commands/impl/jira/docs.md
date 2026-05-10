<!-- STUB — Increment D. Full workflow per design spec §6. -->

`/impl:jira:docs` is under construction.

This command will be the Jira-driven feature-documentation workflow: reads a Jira hierarchy from `$VAULT_PATH/jira-products/<JIRA_KEY>/`, resolves PR URLs to local repos under `/repos/`, spawns parallel `code-diff-summarizer` agents, runs `doc-location-finder` + `doc-planner`, writes product docs to the cwd (a docs repo), style-checks with `docs-style-checker`, and gates on `doc-reviewer` (Opus).

Depends on eight subagents that will be added in Increment D: `jira-reader`, `code-diff-summarizer`, `doc-location-finder`, `doc-planner`, `docs-style-checker`, `doc-reviewer`, `doc-fixer`, plus the shared `impl-maintenance`.

**Until this stub is replaced**, feature documentation must be written manually.

For now, this file exists so Claude Code can load the plugin's new namespaced command layout without error. Invoking `/impl:jira:docs <JIRA_KEY>` prints this notice.
