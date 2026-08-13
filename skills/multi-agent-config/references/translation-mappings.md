# Cross-Platform Translation Mappings

Use these mappings for the portable configuration shared by Codex, Claude Code,
and Cursor. Verify current vendor documentation before translating MCP, hooks,
permissions, or experimental agent features.

## Skills

| Platform | Project location | Format |
| --- | --- | --- |
| Codex | `.agents/skills/<name>/` | Agent Skills |
| Claude Code | `.claude/skills/<name>/` | Agent Skills |
| Cursor | `.agents/skills/<name>/` | Agent Skills |

Cursor also supports `.cursor/skills/<name>/`, but `.agents/skills/` is the
shared choice for Codex and Cursor.

Copy a complete skill directory without converting `SKILL.md`. Preserve its
scripts, references, assets, evaluations, and optional agent metadata. Portable
frontmatter uses the Agent Skills fields and keeps arbitrary release data under
the string-valued `metadata` map.

## Project Instructions

| Platform | Primary project file | Notes |
| --- | --- | --- |
| Codex | `AGENTS.md` | Supports hierarchical discovery |
| Claude Code | `CLAUDE.md` | Supports additional `.claude/rules/*.md` |
| Cursor | `AGENTS.md` | Supports additional `.cursor/rules/` |

Use one shared `AGENTS.md` for Codex and Cursor. Generate `CLAUDE.md` from the
same source when Claude Code is a target. Keep host-specific scoping rules in
their native directories rather than pretending they translate exactly.

## MCP Servers

| Platform | Shared or primary configuration | Format |
| --- | --- | --- |
| Codex | `~/.codex/config.toml` | TOML tables |
| Claude Code | `.mcp.json` | JSON `mcpServers` object |
| Cursor | Check current Cursor MCP documentation | JSON |

Translate server names, commands, arguments, environment mappings, URLs, and
headers explicitly. Do not copy a TOML file to a JSON location. Never put
secrets directly into a generated project file; preserve environment-variable
references or the target platform's secret mechanism.

Example semantic source:

```json
{
  "servers": {
    "example": {
      "command": "npx",
      "args": ["-y", "@package/name"],
      "env": {},
      "enabled": true
    }
  }
}
```

The sync helper converts this model for supported targets. If the target format
is not implemented, stop and direct the user to current platform documentation
instead of writing a guessed configuration.

## Subagents, Hooks, and Commands

These features are not part of the portable skill contract:

- A skill is loaded into the current agent context; a subagent has a separate
  role and context. Do not mechanically convert one into the other.
- Automatic hook schemas and event names vary by host. Preserve hook scripts as
  optional skill helpers unless the user explicitly asks for host integration.
- A command alias is optional convenience, not a skill identity. Skills must be
  discoverable from `name` and `description` without one.

## Shared Source Layout

```text
project/
├── .agent-config/
│   ├── agents/
│   ├── mcp-servers.json
│   ├── rules.md
│   └── skills/
├── .agents/skills/       # Codex and Cursor output
├── .claude/skills/       # Claude Code output
├── AGENTS.md             # Codex and Cursor instructions
├── CLAUDE.md             # Claude Code instructions
└── .mcp.json             # Claude Code project MCP output
```

The `.agent-config/` tree may be the team's authoring source. The generated
platform directories are discovery locations, not registries with separate
metadata.

## Safe Sync Sequence

1. Validate every source skill before copying it.
2. Resolve the target platform and documented discovery path.
3. Preserve unrelated target files.
4. Copy the entire skill directory atomically where practical.
5. Translate instructions and MCP separately.
6. Validate discovery in each installed agent.
7. Report any feature with no portable mapping rather than silently dropping it.
