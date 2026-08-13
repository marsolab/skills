# Claude Code Configuration Reference

Use this reference for the portable parts of a Claude Code project. Check the
[current Claude Code documentation](https://code.claude.com/docs/en/claude-directory)
before translating settings, hooks, permissions, or MCP transports.

## Project Files

| Purpose | Project location |
| --- | --- |
| Instructions | `CLAUDE.md` or `.claude/CLAUDE.md` |
| Topic-scoped rules | `.claude/rules/*.md` |
| Skills | `.claude/skills/<name>/SKILL.md` |
| Subagents | `.claude/agents/*.md` |
| Settings | `.claude/settings.json` |
| Local settings | `.claude/settings.local.json` |
| Shared MCP servers | `.mcp.json` |
| Output styles | `.claude/output-styles/*.md` |

User-level skills and settings use the corresponding paths under `~/.claude/`.

## Skills

Claude Code reads Agent Skills from `.claude/skills/` at project scope. Copy the
whole portable skill directory:

```text
.claude/skills/example-skill/
├── SKILL.md
├── assets/       # optional
├── references/   # optional
└── scripts/      # optional
```

The portable entrypoint requires `name` and `description`. Keep release data in
the string-valued `metadata` map:

```yaml
---
name: example-skill
description: Explain what the skill does and when Claude should use it.
metadata:
  version: "1.0.0"
---
```

Claude can select a skill from its description or the user can invoke it by
name. A cross-agent skill should not require a slash-command alias.

## MCP Servers

Project-scoped MCP servers belong in `.mcp.json` at the repository root:

```json
{
  "mcpServers": {
    "example": {
      "command": "npx",
      "args": ["-y", "@package/name"],
      "env": {}
    }
  }
}
```

Do not put project MCP servers in `.claude/config.json`; that is not a current
Claude Code project configuration path.

## Instructions and Rules

Use `CLAUDE.md` for broad project instructions. Use files under
`.claude/rules/` when instructions need topic or path scoping. Hooks are
configured under the `hooks` key in a settings file rather than discovered from
a standalone hook directory.

## Cross-Platform Mapping

| Portable concept | Codex | Claude Code | Cursor |
| --- | --- | --- | --- |
| Project skills | `.agents/skills/` | `.claude/skills/` | `.agents/skills/` |
| Project instructions | `AGENTS.md` | `CLAUDE.md` | `AGENTS.md` |
| Shared MCP config | Codex TOML | `.mcp.json` | Cursor MCP config |

Skills can be copied without conversion. Instructions and MCP configuration
need platform-specific file names and, for MCP, format translation.
