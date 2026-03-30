# Cross-Platform Translation Mappings

This reference shows how to translate configurations between different AI code
agent platforms.

## Conceptual Mappings

### Custom Instructions / Rules

| Platform | Location | Format | Notes |
|----------|----------|--------|-------|
| **Codex** | `AGENTS.md` (hierarchical) | Markdown | Supports hierarchy with `.override.md` |
| **Claude Code** | `.claude/rules.md` | Markdown | Single file per project |
| **Cursor** | `.cursorrules` | Text/Markdown | Single file at root |
| **Gemini** | TBD | TBD | Research needed |
| **Docker MCP Gateway** | N/A | N/A | No custom instructions (MCP servers only) |

**Translation strategy**:

- Merge hierarchical AGENTS.md files into single file for Claude Code/Cursor
- Split single file into root + optional overrides for Codex
- Docker MCP Gateway doesn't use custom instructions

### MCP Server Configuration

| Platform | Location | Format | Key Differences |
|----------|----------|--------|-----------------|
| **Codex** | `~/.codex/config.toml` | TOML | `[mcp_servers.name]` tables |
| **Claude Code** | `~/.claude/config.json` | JSON | `"mcpServers": {}` object |
| **Cursor** | Settings JSON | JSON | TBD - verify structure |
| **Gemini** | TBD | TBD | Research needed |
| **Docker MCP Gateway** | `~/.docker/mcp/` | YAML | Centralized gateway with `docker-mcp.yaml`, `registry.yaml`, `config.yaml` |

**Translation strategy**:

```python
# Traditional MCP (Codex/Claude Code) → Docker MCP Gateway
# Instead of configuring individual servers in each client,
# configure once in Docker MCP Gateway and reference gateway

# Codex TOML (traditional)
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp"]
env = { API_KEY = "secret" }

# Becomes ↓ Docker MCP Gateway setup
$ docker mcp server enable context7
$ docker mcp secret create context7-key "secret"

# Then Codex config just references gateway
[mcp_servers.docker-gateway]
command = "docker"
args = ["mcp", "gateway", "run"]

# Claude Code JSON (traditional)
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}

# Becomes ↓ Claude Code with gateway
{
  "mcpServers": {
    "docker-gateway": {
      "command": "docker",
      "args": ["mcp", "gateway", "run"]
    }
  }
}
```

### Skills

| Platform | Location | Format | Structure |
|----------|----------|--------|-----------|
| **Codex** | `.codex/skills/` | Agent Skills | `SKILL.md` + resources |
| **Claude Code** | `.claude/skills/` | Agent Skills | Same as Codex |
| **Cursor** | `.cursor/skills/` | TBD | Likely similar |
| **Gemini** | TBD | TBD | Research needed |

**Translation strategy**:

- Agent Skills format is compatible between Codex and Claude Code
- Direct copy when moving skills between these platforms
- May need format conversion for Cursor/Gemini

### Subagents / Agents

| Platform | Concept | Location | Format |
|----------|---------|----------|--------|
| **Codex** | Skills (implicit delegation) | `.codex/skills/` | SKILL.md |
| **Claude Code** | Subagents (explicit) | `.claude/agents/` | MD + YAML frontmatter |
| **Cursor** | Subagents? | TBD | TBD |
| **Gemini** | TBD | TBD | TBD |

**Translation strategy**:

- **Codex → Claude Code**: Convert skills to subagents when they represent
  delegation

  ```markdown
  # Codex skill that acts like a subagent
  ---
  name: code-reviewer
  description: Use proactively for code review
  ---
  Instructions...

  # Becomes Claude Code subagent ↓
  ---
  name: code-reviewer
  description: Use proactively for code review
  tools: Read, Grep, Glob, Bash
  model: sonnet
  ---
  Instructions...
  ```

- **Claude Code → Codex**: Convert subagents to skills
  - Remove `tools`, `model`, `permissionMode` fields (not applicable)
  - Keep `description` and instructions

### Hooks

| Platform | Support | Location | Format |
|----------|---------|----------|--------|
| **Codex** | ❌ No | N/A | N/A |
| **Claude Code** | ✅ Yes | `.claude/hooks/` | TypeScript/JavaScript |
| **Cursor** | ❓ Unknown | TBD | TBD |
| **Gemini** | ❓ Unknown | TBD | TBD |

**Translation strategy**:

- Hooks are Claude Code-specific
- Cannot translate to Codex (no equivalent)
- Include hooks when syncing TO Claude Code from other platforms (create
  templates)

## File Structure Mappings

### Project Structure Comparison

```text
# Codex Project
project/
├── .codex/
│   ├── skills/
│   │   └── skill-name/
│   │       └── SKILL.md
│   └── (no agents - uses skills)
├── AGENTS.md
└── AGENTS.override.md (optional)

# Claude Code Project
project/
├── .claude/
│   ├── agents/
│   │   └── agent-name.md
│   ├── skills/
│   │   └── skill-name/
│   │       └── SKILL.md
│   ├── hooks/
│   │   └── pre-edit.ts
│   ├── plugins/
│   └── styles/
└── .claude/rules.md

# Cursor Project
project/
├── .cursor/
│   └── skills/ (tentative)
└── .cursorrules

# Gemini Project
project/
└── TBD
```

## Sync Workflow Recommendations

### 1. Initialize Multi-Platform Project

Create directory structure for all platforms:

```bash
project/
├── .codex/
├── .claude/
├── .cursor/
├── .gemini/ (TBD)
└── .agent-config/  # Shared source of truth
    ├── mcp-servers.json
    ├── skills/
    ├── rules.md
    └── agents/
```

### 2. Sync Direction Strategies

**Strategy A: Single Source of Truth**

- Maintain configs in one platform
- Sync one-way to others
- Example: Codex → Claude Code → Cursor

**Strategy B: Shared Source**

- Maintain platform-agnostic configs in `.agent-config/`
- Generate platform-specific configs from shared source
- Best for teams using multiple platforms

**Strategy C: Bidirectional Sync**

- Changes in any platform sync to others
- Requires conflict resolution
- Most complex but most flexible

## Common Translation Patterns

### MCP Server: TOML → JSON

```python
def toml_mcp_to_json(toml_config):
    """Convert Codex TOML MCP config to Claude Code JSON"""
    mcp_servers = {}
    for name, config in toml_config.get('mcp_servers', {}).items():
        mcp_servers[name] = {
            'command': config.get('command'),
            'args': config.get('args', []),
            'env': config.get('env', {})
        }
        if 'url' in config:
            mcp_servers[name]['url'] = config['url']
    return {'mcpServers': mcp_servers}
```

### Skill Translation

Skills using Agent Skills standard can be copied directly between:

- Codex ↔ Claude Code
- Codex → Cursor (if supported)

### Rules / Instructions

```python
def merge_agents_md_to_rules(agents_files):
    """Merge hierarchical AGENTS.md files to single rules.md"""
    content = []
    for file_path in sorted(agents_files):
        with open(file_path) as f:
            content.append(f"# From: {file_path}\n\n{f.read()}\n")
    return "\n---\n\n".join(content)
```

## Docker MCP Gateway Integration

### Why Use Docker MCP Gateway

**Benefits over traditional MCP server configuration**:

1. **Centralized configuration** - Configure once, use from all AI clients
1. **Secure secrets** - API keys stored in Docker Desktop secrets, not config
  files
1. **Container isolation** - Each MCP server runs in isolated Docker container
1. **No dependency management** - No need for npx, uvx, or python environments
1. **OAuth support** - Built-in OAuth flows for GitHub, Google, etc.
1. **Unified access control** - Manage which servers and tools are available
  globally

### Traditional MCP vs Docker MCP Gateway

**Traditional approach (per-client configuration)**:

```text
AI Client 1 (Codex)     AI Client 2 (Claude Code)     AI Client 3 (Cursor)
      ↓                           ↓                            ↓
  MCP Server 1              MCP Server 1                 MCP Server 1
  MCP Server 2              MCP Server 2                 MCP Server 2
  (each with own           (each with own               (each with own
   secrets in config)       secrets in config)           secrets in config)
```

**Docker MCP Gateway approach**:

```text
AI Client 1 (Codex) ──┐
AI Client 2 (Claude) ─┤──→ Docker MCP Gateway ──→ MCP Servers (containers)
AI Client 3 (Cursor) ─┘                              ↓
                                                   Secrets (secure store)
```

### Migration Workflow

**Step 1: Identify current MCP servers**

```bash
# Extract from Codex config
grep -A 5 "\[mcp_servers\." ~/.codex/config.toml

# Extract from Claude Code config
jq '.mcpServers' ~/.claude/config.json
```

**Step 2: Initialize Docker MCP**

```bash
# Install Docker Desktop if not already installed
# Enable MCP Toolkit in Docker Desktop settings

# Initialize catalog
docker mcp catalog init

# List available servers
docker mcp catalog show docker-mcp
```

**Step 3: Enable servers in Docker MCP**

```bash
# Enable servers (no more per-client config!)
docker mcp server enable context7 github filesystem

# Store secrets securely
docker mcp secret create context7-key "your-api-key"
docker mcp secret create github-token "ghp_token"
```

**Step 4: Configure servers**

```bash
# Server-specific configuration
docker mcp config write 'servers:
  filesystem:
    config:
      allowed_paths:
        - /home/user/projects
  github:
    oauth:
      provider: github
      scopes: [repo, read:org]
  context7:
    env:
      CONTEXT7_API_KEY: secret://context7-key'
```

**Step 5: Update client configurations**

**Codex** - Replace all MCP servers with gateway:

```toml
# Before (multiple servers)
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp"]

[mcp_servers.github]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]

# After (single gateway)
[mcp_servers.docker-gateway]
command = "docker"
args = ["mcp", "gateway", "run"]
```

**Claude Code** - Replace all MCP servers with gateway:

```json
{
  "mcpServers": {
    "docker-gateway": {
      "command": "docker",
      "args": ["mcp", "gateway", "run"]
    }
  }
}
```

### Docker MCP Gateway Configuration Files

**~/.docker/mcp/docker-mcp.yaml** - Server catalog:

```yaml
servers:
  context7:
    image: docker.io/upstash/context7:latest
    description: "Developer documentation"
  github:
    image: docker.io/modelcontextprotocol/github:latest
    description: "GitHub integration"
```

**~/.docker/mcp/registry.yaml** - Enabled servers:

```yaml
enabled:
  - context7
  - github
  - filesystem
```

**~/.docker/mcp/config.yaml** - Server configuration:

```yaml
servers:
  context7:
    env:
      CONTEXT7_API_KEY: secret://context7-key
  filesystem:
    config:
      allowed_paths:
        - /home/user/projects
  github:
    oauth:
      provider: github
```

### Integration with multi-agent-config Skill

The skill can help manage Docker MCP Gateway configurations:

**Initialize project with Docker MCP Gateway**:

```bash
# Initialize multi-agent project
python scripts/init_project.py ~/my-project

# Set up Docker MCP instead of traditional MCP
docker mcp server enable context7 github

# Configure secrets
docker mcp secret create context7-key "key"

# Generate gateway configs for all platforms
python scripts/sync_config.py --to all --docker-mcp
```

**Sync Docker MCP Gateway to clients**:

```bash
# This updates all client configs to use Docker MCP Gateway
# instead of individual MCP servers
python scripts/sync_config.py --docker-mcp --to all
```

### Advanced: Hybrid Approach

You can use both Docker MCP Gateway and traditional MCP servers:

```toml
# Codex config with hybrid approach
[mcp_servers.docker-gateway]
command = "docker"
args = ["mcp", "gateway", "run"]

# Keep some servers traditional (e.g., local development)
[mcp_servers.local-dev]
command = "/path/to/local/mcp-server"
```

### Docker MCP Gateway with Different Transports

**stdio (default)** - One gateway per client:

```bash
# Each client starts its own gateway process
command = "docker"
args = ["mcp", "gateway", "run"]
```

**SSE (Server-Sent Events)** - Shared gateway:

```bash
# Start gateway once
docker mcp gateway run --port 8080 --transport sse

# All clients connect to same gateway
[mcp_servers.docker-gateway]
url = "http://localhost:8080"
```

**streaming** - High-performance shared gateway:

```bash
# Start gateway with streaming transport
docker mcp gateway run --port 8080 --transport streaming

# Clients connect via streaming
[mcp_servers.docker-gateway]
url = "http://localhost:8080"
```
