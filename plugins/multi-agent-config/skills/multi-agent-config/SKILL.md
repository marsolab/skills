---
name: multi-agent-config
description: "Manage multi-agent AI code configurations across platforms (OpenAI Codex, Claude Code, Cursor, Gemini). Use when: (1) initializing new multi-agent projects, (2) syncing configurations (MCP servers, skills, rules, subagents) across platforms, (3) translating configurations between different agent platforms, (4) migrating from one agent platform to another, or (5) maintaining consistent agent configurations across development teams using different tools."
version: 1.0.0
---

# Multi-Agent Configuration Manager

Manage and sync AI code agent configurations across OpenAI Codex, Claude Code,
Cursor, and Gemini.

## Overview

This skill enables you to maintain consistent AI agent configurations across
multiple platforms. It handles translation between different configuration
formats (TOML ↔ JSON), directory structures, and platform-specific conventions.

**Supported platforms:**

- OpenAI Codex (config.toml, AGENTS.md, skills)
- Claude Code (config.json, .claude/, subagents, hooks)
- Cursor (.cursorrules, partial support)
- Gemini (placeholder for future support)

## Quick Start

### Initialize a New Multi-Agent Project

```bash
python scripts/init_project.py /path/to/project
```

This creates:

- `.agent-config/` - Shared source of truth
- `.codex/` - Codex-specific structure
- `.claude/` - Claude Code-specific structure
- `.cursor/` - Cursor-specific structure
- Platform-specific config files

### Sync Existing Configuration

```bash
# Sync all configurations to all platforms
python scripts/sync_config.py --to all

# Sync to specific platform
python scripts/sync_config.py --to claude-code

# Sync only MCP servers
python scripts/sync_config.py --mcp-only --to codex
```

## Core Operations

### 1. Initialize Multi-Agent Project

**When to use:** Starting a new project that will be used with multiple AI code
agents.

**Process:**

1. Run the initialization script
1. Edit shared configuration files
1. Sync to target platforms

**Example:**

```bash
# Initialize project
python scripts/init_project.py ./my-project

# Edit shared configuration
cd my-project
vim .agent-config/rules.md
vim .agent-config/mcp-servers.json

# Sync to all platforms
python scripts/sync_config.py --to all
```

### 2. Sync Configurations

**When to use:** After editing shared configs or when switching between agent
platforms.

**What gets synced:**

- MCP server configurations
- Custom instructions/rules
- Skills (Agent Skills standard)
- Agents/subagents

**Sync options:**

```bash
# All configurations to all platforms
python scripts/sync_config.py --to all

# Specific platform
python scripts/sync_config.py --to codex
python scripts/sync_config.py --to claude-code

# Specific config type
python scripts/sync_config.py --mcp-only
python scripts/sync_config.py --rules-only
python scripts/sync_config.py --skills-only
python scripts/sync_config.py --agents-only
```

### 3. Add MCP Servers

**Process:**

1. Edit `.agent-config/mcp-servers.json`
1. Add server configuration
1. Sync to platforms

**Example MCP server config:**

```json
{
  "servers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "env": {},
      "enabled": true,
      "description": "Developer documentation MCP"
    }
  }
}
```

### 4. Add Skills

**Process:**

1. Create skill in `.agent-config/skills/`
1. Follow Agent Skills standard
1. Sync to platforms

**Example:**

```bash
# Create skill directory
mkdir -p .agent-config/skills/my-skill

# Create SKILL.md
cat > .agent-config/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: Description of when to use this skill
---

# My Skill

Instructions for using this skill.
EOF

# Sync to platforms
python scripts/sync_config.py --skills-only
```

### 5. Translate Configurations

**When to use:** Migrating from one platform to another or understanding config
differences.

**Platform reference docs:**

- `references/codex.md` - Codex configuration format
- `references/claude-code.md` - Claude Code configuration
- `references/cursor.md` - Cursor format (partial)
- `references/translation-mappings.md` - Cross-platform mappings
- `references/docker-mcp-gateway.md` - Docker MCP Gateway

**Manual translation example:**

```python
from scripts.translate_utils import ConfigTranslator, load_toml, save_json

# Load Codex config
codex_config = load_toml('~/.codex/config.toml')

# Translate MCP servers
translator = ConfigTranslator()
claude_mcp = translator.toml_mcp_to_json(codex_config)

# Save to Claude Code config
save_json(claude_mcp, '.claude/config.json')
```

### 6. Migrate to Docker MCP Gateway (Recommended)

**When to use:** Want centralized MCP management with better security and
isolation.

**Benefits:**

- ✅ Centralized configuration across all AI clients
- ✅ Secure secrets management (no API keys in config files)
- ✅ Container isolation for each MCP server
- ✅ Built-in OAuth flows
- ✅ No dependency management (npx, uvx, python)

**Migration process:**

```bash
# 1. Migrate existing MCP servers to Docker MCP Gateway
python scripts/sync_config.py --migrate-to-docker-mcp

# 2. Follow generated instructions in DOCKER_MCP_SETUP.md
# This will show you exactly which docker commands to run

# 3. Example commands (generated by migration):
docker mcp catalog init
docker mcp server enable context7 github filesystem
docker mcp secret create context7-key "your-api-key"
docker mcp secret create github-token "ghp_token"

# 4. Configure servers
docker mcp config write 'servers:
  filesystem:
    config:
      allowed_paths: ["/home/user/projects"]
  context7:
    env:
      CONTEXT7_API_KEY: secret://context7-key'

# 5. Test the gateway
docker mcp tools ls
```

**Result:** All your AI clients now use a single gateway instead of individual
MCP servers.

**Before (traditional):**

```toml
# Codex config - managing individual servers
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp"]
env = { API_KEY = "exposed-in-config" }

[mcp_servers.github]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
env = { GITHUB_TOKEN = "exposed-in-config" }
```

**After (Docker MCP Gateway):**

```toml
# Codex config - single gateway
[mcp_servers.docker-gateway]
command = "docker"
args = ["mcp", "gateway", "run"]
```

All MCP configuration now managed through Docker MCP CLI:

```bash
docker mcp server ls              # List enabled servers
docker mcp secret ls              # List secrets (secure)
docker mcp config read            # View configuration
```

## Workflow Examples

### Team Standardization

```bash
# Initialize shared project config
python scripts/init_project.py ~/team-project

# Edit shared rules
vim ~/team-project/.agent-config/rules.md

# Sync to all platforms
cd ~/team-project
python scripts/sync_config.py --to all
```

### Platform Migration

```bash
# Currently using Codex, want to try Claude Code
cd ~/my-codex-project

# Initialize Claude Code structure
python scripts/init_project.py . --platforms claude-code

# Copy Codex config to shared
cp AGENTS.md .agent-config/rules.md

# Sync to Claude Code
python scripts/sync_config.py --to claude-code
```

### Docker MCP Gateway Migration (Recommended)

```bash
# Step 1: Migrate existing MCP servers to Docker MCP Gateway
cd ~/my-project
python scripts/sync_config.py --migrate-to-docker-mcp

# This generates DOCKER_MCP_SETUP.md with specific commands for your setup
# Example output:

# Step 2: Initialize Docker MCP
docker mcp catalog init

# Step 3: Enable your MCP servers
docker mcp server enable context7 github filesystem

# Step 4: Store secrets securely
docker mcp secret create context7-key "sk-..."
docker mcp secret create github-token "ghp_..."

# Step 5: Configure servers
docker mcp config write 'servers:
  context7:
    env:
      CONTEXT7_API_KEY: secret://context7-key
  github:
    env:
      GITHUB_TOKEN: secret://github-token
  filesystem:
    config:
      allowed_paths:
        - /home/user/projects'

# Step 6: Test the gateway
docker mcp tools ls
docker mcp tools call read_file '{"path": "README.md"}'

# Step 7: Your client configs are already updated!
# All AI clients now use the Docker MCP Gateway
```

**Benefits of Docker MCP Gateway:**

- All AI clients (Codex, Claude Code, Cursor) use the same MCP configuration
- API keys stored securely in Docker Desktop, not in config files
- Each MCP server runs in an isolated container
- Easy to enable/disable servers without editing configs
- OAuth flows handled automatically

### Multi-Transport Docker MCP Gateway

```bash
# Option 1: stdio (default) - one gateway per client
# Each client starts its own gateway process
# No additional setup needed

# Option 2: SSE - shared gateway for all clients
# Start gateway once
docker mcp gateway run --port 8080 --transport sse

# Update client configs to use shared gateway
cat > ~/.codex/config.toml << EOF
[mcp_servers.docker-gateway]
url = "http://localhost:8080"
EOF

cat > ~/.claude/config.json << EOF
{
  "mcpServers": {
    "docker-gateway": {
      "url": "http://localhost:8080",
      "transport": "sse"
    }
  }
}
EOF

# Option 3: streaming - high-performance shared gateway
docker mcp gateway run --port 8080 --transport streaming
```

## Reference Documentation

For detailed platform formats and translations:

- `references/codex.md` - OpenAI Codex configuration
- `references/claude-code.md` - Claude Code configuration
- `references/cursor.md` - Cursor configuration (partial)
- `references/gemini.md` - Gemini configuration (placeholder)
- `references/docker-mcp-gateway.md` - Docker MCP Gateway (recommended)
- `references/translation-mappings.md` - Cross-platform mappings
