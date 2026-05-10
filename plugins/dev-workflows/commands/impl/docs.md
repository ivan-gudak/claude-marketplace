<!-- STUB — Increment C. Full workflow per design spec §5. -->

`/impl:docs` is under construction.

This command will carry a simplified one-shot documentation-editing workflow: no feature branch, no test baseline, no Opus review, no git commits. The user manages git manually. All four Phase 4 maintenance agents still run, with `change_type: docs`.

**Until this stub is replaced**, do doc edits either manually or with the existing `/impl` command (which will do more than needed but won't break anything — you can skip its test/branch prompts).

For now, this file exists so Claude Code can load the plugin's new namespaced command layout without error. Invoking `/impl:docs <description>` prints this notice.
