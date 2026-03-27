# OpenAI Codex Configuration Reference

Complete reference for Codex configuration structure, file locations, and formats.

## Configuration File

**Location**: `~/.codex/config.toml`
**Format**: TOML

## Core Configuration Structure

### MCP Servers

```toml
[mcp_servers.server_name]
# STDIO servers
command = "npx"
args = ["-y", "@package/name"]
cwd = "/path/to/working/dir"  # Optional
env = { KEY = "value" }
env_vars = ["VAR1", "VAR2"]  # Additional env vars to whitelist
enabled = true
enabled_tools = ["tool1", "tool2"]  # Optional whitelist
disabled_tools = ["tool3"]  # Optional blacklist
startup_timeout_sec = 10
tool_timeout_sec = 60

# HTTP servers
[mcp_servers.http_server]
url = "https://mcp.example.com/mcp"
bearer_token_env_var = "AUTH_TOKEN"  # Optional
env_http_headers = { "X-Custom" = "HEADER_ENV_VAR" }
http_headers = { "X-Static" = "value" }
```

### Skills

**Locations** (in precedence order):
1. `$CWD/.codex/skills` - Current working directory (REPO scope)
2. `$CWD/../.codex/skills` - Parent folder in git repo (REPO scope)
3. `$REPO_ROOT/.codex/skills` - Repository root (REPO scope)
4. `$CODEX_HOME/skills` - User-level (`~/.codex/skills`) (USER scope)
5. `/etc/codex/skills` - Admin/system-level (ADMIN scope)
6. Built-in system skills (SYSTEM scope)

**Format**: Each skill is a folder containing `SKILL.md`:

```markdown
---
name: skill-name
description: Description that helps Codex select the skill
metadata:
  short-description: Optional user-facing description
---

# Skill Name

Skill instructions for the Codex agent to follow.

## Usage

Instructions here...
```

**Structure**:
```
skill-name/
├── SKILL.md (required)
├── scripts/ (optional)
├── references/ (optional)
└── assets/ (optional)
```

### AGENTS.md (Custom Instructions)

**Discovery order**:
1. **Global scope**: `~/.codex/AGENTS.override.md` or `~/.codex/AGENTS.md`
2. **Project scope**: Walk from repo root to CWD, checking each directory for:
   - `AGENTS.override.md`
   - `AGENTS.md`
   - Fallback filenames from `project_doc_fallback_filenames` config

**Configuration**:
```toml
project_doc_fallback_filenames = ["TEAM_GUIDE.md", ".agents.md"]
project_doc_max_bytes = 32768  # Default: 32 KiB
```

**Format**: Plain Markdown

```markdown
# Project Instructions

## Working agreements
- Always run tests after changes
- Prefer pnpm for dependencies

## Repository expectations
- Document public utilities
- Run lint before PRs
```

### Model Configuration

```toml
model = "gpt-5-codex"
model_provider = "openai"
model_context_window = 200000
model_verbosity = "medium"  # low | medium | high

[model_providers.custom]
name = "Custom Provider"
base_url = "https://api.example.com"
env_key = "CUSTOM_API_KEY"
wire_api = "chat"  # chat | responses
http_headers = { "X-Custom" = "value" }
env_http_headers = { "X-Auth" = "AUTH_ENV_VAR" }
```

### Features

```toml
[features]
skills = true  # Enable skills discovery
unified_exec = true  # PTY-backed exec tool
shell_tool = true  # Enable shell command execution
parallel = true  # Parallel tool calls
exec_policy = true  # Enforce exec policy checks
warnings = true  # Send tool-usage warnings
```

### Sandbox Mode

```toml
sandbox_mode = "workspace-write"  # read-only | workspace-write | danger-full-access

[sandbox_workspace_write]
network_access = true
writable_roots = ["/additional/path"]
exclude_slash_tmp = false
exclude_tmpdir_env_var = false
```

## Translation Notes

### To Claude Code

| Codex | Claude Code | Notes |
|-------|-------------|-------|
| `config.toml` | `~/.claude/config.json` | Format change: TOML → JSON |
| `~/.codex/` | `~/.claude/` | Home directory |
| `.codex/skills/` | `.claude/skills/` | Same structure |
| `AGENTS.md` | `.claude/rules.md` | Custom instructions |
| MCP servers in config | MCP in config | Same structure |
| Skills (no subagents) | Subagents (`.claude/agents/`) | Concept mapping |

### To Cursor

| Codex | Cursor | Notes |
|-------|--------|-------|
| `AGENTS.md` | `.cursorrules` | Single file |
| Skills | `.cursor/skills/` | Check for support |
| MCP config.toml | Cursor settings | May differ |

### Key Differences

**Codex-specific features**:
- TOML configuration format
- Hierarchical AGENTS.md discovery
- Skill-based architecture (no separate subagent concept)
- Extensive sandbox configuration
- Profile support in config
