# Cursor Configuration Reference

Use this reference when translating portable skills and project instructions to
Cursor. Check the [current Cursor documentation](https://cursor.com/docs/skills)
before changing features outside this scope.

## Skills

Cursor discovers Agent Skills from either of these project locations:

1. `.agents/skills/<name>/SKILL.md`
2. `.cursor/skills/<name>/SKILL.md`

Prefer `.agents/skills/` when the same skill collection should also work in
Codex. Use `.cursor/skills/` only when the project intentionally keeps a
Cursor-specific copy.

A portable skill directory contains `SKILL.md` and may contain supporting
scripts, references, and assets. Keep all relative links within that directory.

```yaml
---
name: example-skill
description: Explain what the skill does and when Cursor should use it.
metadata:
  version: "1.0.0"
---

# Example Skill

Instructions for the agent.
```

Do not translate a portable skill into a command alias. Cursor can discover the
skill directly from its description and the user can request it by name.

## Project Instructions

Cursor supports `AGENTS.md` for project instructions. This is the most portable
choice when Codex uses the same repository. Cursor also supports its native
rules under `.cursor/rules/` when scoped or Cursor-only behavior is needed.

Avoid creating the legacy `.cursorrules` file in new projects.

## Cross-Platform Mapping

| Portable concept | Codex | Claude Code | Cursor |
| --- | --- | --- | --- |
| Project skills | `.agents/skills/` | `.claude/skills/` | `.agents/skills/` |
| Project instructions | `AGENTS.md` | `CLAUDE.md` | `AGENTS.md` |
| Native alternative | — | — | `.cursor/skills/`, `.cursor/rules/` |

When syncing skills, copy the whole skill directory. Do not rewrite portable
frontmatter or strip unknown supporting directories for any one host.
