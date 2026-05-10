<!-- STUB — Increment B. Full workflow per design spec §4 (2026-04-30-impl-split-and-test-writing-design.md). -->

`/impl:code` is under construction.

This command will carry the full structured code-implementation workflow (classification → optional Opus planning → feature branch → pre-change test baseline → implementation → test-writing → optional Opus review → test verification → Phase 4 maintenance → Phase 5 report), with test-writing inserted at Phase 3.5.

**Until this stub is replaced**, use the existing `/impl $ARGUMENTS` command — it still behaves as the canonical code-implementation workflow. The top-level `/impl` is the backward-compatible alias for `/impl:code`; once `/impl:code` is fully written, `/impl` will be kept in sync via verbatim duplication.

For now, this file exists so Claude Code can load the plugin's new namespaced command layout without error. Invoking `/impl:code <description>` prints this notice.
