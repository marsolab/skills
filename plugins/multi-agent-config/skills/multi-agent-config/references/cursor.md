# Cursor Configuration Reference

Configuration reference for Cursor IDE with AI features.

## Configuration Files

**Location**: Workspace and user settings
**Format**: Various (rules, settings JSON, skills)

## Known Configuration Elements

### .cursorrules

**Location**: Project root
**Format**: Plain text / Markdown

```markdown
# Project Rules

Your cursor rules go here.
These are custom instructions for Cursor.
```

### Skills

**Location**: `.cursor/skills/` (tentative - needs verification)
**Format**: TBD - likely similar to Agent Skills standard

### Subagents

**Location**: TBD - needs verification
**Format**: TBD

### MCP Integration

**Location**: Cursor settings (TBD)
**Format**: JSON in Cursor settings

### Commands

Custom commands can be defined in Cursor settings.

## Translation Notes

### From Codex

| Codex | Cursor | Status |
|-------|--------|--------|
| `AGENTS.md` | `.cursorrules` | Known |
| `.codex/skills/` | `.cursor/skills/` | Needs verification |
| MCP config.toml | Cursor settings | Needs verification |

### From Claude Code

| Claude Code | Cursor | Status |
|-------------|--------|--------|
| `.claude/rules.md` | `.cursorrules` | Known |
| `.claude/agents/` | TBD | Needs verification |
| `.claude/skills/` | `.cursor/skills/` | Needs verification |

## Research Needed

To complete this reference, we need to research:

1. Full Cursor settings.json structure
1. MCP server configuration in Cursor
1. Skills/Subagents support and format
1. Commands configuration
1. Any Cursor-specific features

## Placeholder Notes

This is a placeholder reference. When completing:

- Search Cursor documentation for configuration details
- Check Cursor GitHub discussions/issues
- Examine actual Cursor project files
- Update translation mappings with accurate paths and formats
