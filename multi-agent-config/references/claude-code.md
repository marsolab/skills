# Claude Code Configuration Reference

Complete reference for Claude Code configuration structure, file locations, and formats.

## Configuration File

**Location**: `~/.claude/config.json`
**Format**: JSON

## Core Configuration Structure

### MCP Servers

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@package/name"],
      "env": {
        "KEY": "value"
      }
    },
    "http-server": {
      "url": "https://mcp.example.com/mcp",
      "transport": "sse"
    }
  }
}
```

### Subagents

**Locations** (in precedence order):
1. `.claude/agents/` - Project-level subagents (highest priority)
2. `~/.claude/agents/` - User-level subagents
3. Plugin agents (from plugins)

**Format**: Each subagent is a Markdown file with YAML frontmatter:

```markdown
---
name: subagent-name
description: When this subagent should be invoked
tools: Read, Edit, Bash, Grep  # Optional - inherits all if omitted
model: sonnet  # sonnet | opus | haiku | inherit
permissionMode: default  # default | acceptEdits | bypassPermissions | plan | ignore
skills: skill1, skill2  # Optional - skills to auto-load
---

System prompt for the subagent.

Detailed instructions about the subagent's role, capabilities,
and approach to solving problems.
```

**Built-in subagents**:
- `general-purpose` - Complex multi-step tasks with Sonnet
- `plan` - Research mode with Read/Grep/Glob/Bash
- `explore` - Fast read-only codebase search with Haiku

### Skills

**Locations**:
- `.claude/skills/` - Project-level
- `~/.claude/skills/` - User-level  
- Plugin skills (from plugins)

**Format**: Follows Agent Skills standard (same as Codex):

```markdown
---
name: skill-name
description: Description that helps Claude select the skill
---

# Skill instructions

Instructions for using this skill.
```

**Structure**:
```
skill-name/
├── SKILL.md (required)
├── scripts/ (optional)
├── references/ (optional)
└── assets/ (optional)
```

### Rules (Custom Instructions)

**Location**: `.claude/rules.md`
**Format**: Plain Markdown

```markdown
# Project Rules

## Coding Standards
- Use TypeScript for new files
- Run tests before committing

## Workflow
- Always explain changes before applying
```

### Plugins

**Location**: `.claude/plugins/`

**Plugin structure**:
```
plugin-name/
├── manifest.json
├── agents/ (optional)
│   └── agent-name.md
├── skills/ (optional)
│   └── skill-name/
│       └── SKILL.md
└── hooks/ (optional)
    └── hook-name.ts
```

**manifest.json**:
```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "Plugin description",
  "agents": ["agents/agent-name.md"],
  "skills": ["skills/skill-name"],
  "hooks": ["hooks/hook-name.ts"]
}
```

### Hooks

**Location**: `.claude/hooks/`

Hooks are TypeScript/JavaScript files that run on specific events:

```typescript
// .claude/hooks/pre-edit.ts
export default async function (context) {
  // Run before edits are applied
  return { allow: true };
}
```

**Hook types**:
- `pre-edit.ts` - Before applying edits
- `post-edit.ts` - After edits applied
- `pre-command.ts` - Before running commands
- `post-command.ts` - After commands run

### Output Styles

**Location**: `.claude/styles/`

Custom output formatting styles:

```markdown
---
name: style-name
description: When to use this style
---

# Style instructions

Format output according to these guidelines.
```

## Translation Notes

### From Codex

| Codex | Claude Code | Notes |
|-------|-------------|-------|
| `config.toml` | `config.json` | Format: TOML → JSON |
| `~/.codex/` | `~/.claude/` | Home directory |
| `.codex/skills/` | `.claude/skills/` | Same structure |
| `AGENTS.md` | `.claude/rules.md` | Custom instructions |
| Skills (implicit) | `.claude/agents/` | Map to subagents |
| N/A | `.claude/hooks/` | Claude Code specific |
| N/A | `.claude/plugins/` | Claude Code specific |

### To Cursor

| Claude Code | Cursor | Notes |
|-------------|--------|-------|
| `.claude/rules.md` | `.cursorrules` | Single file |
| `.claude/agents/` | Cursor subagents? | Check support |
| `.claude/skills/` | `.cursor/skills/` | May differ |
| Hooks | N/A | Claude Code specific |

### Key Differences

**Claude Code-specific features**:
- JSON configuration format
- Subagent architecture with separate context windows
- Plugin system with agents/skills/hooks
- Output styles
- Hooks for event-driven automation
- Permission modes for subagents
- Resume capability for subagents

**Subagent vs Skill distinction**:
- **Subagents**: Separate AI instances with own context, can delegate tasks
- **Skills**: Instructions/resources loaded into existing context
