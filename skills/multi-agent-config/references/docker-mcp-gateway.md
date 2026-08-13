# Docker MCP Gateway Reference

Complete reference for Docker MCP Gateway configuration and usage with AI code
agents.

## Overview

Docker MCP Gateway is a CLI plugin and gateway service that:

- Runs MCP servers as isolated Docker containers
- Provides a unified interface for AI clients to access multiple MCP servers
- Handles secrets, OAuth flows, and server lifecycle management
- Supports multiple transports (stdio, SSE, streaming)
- Integrates with Docker Desktop's secrets management

**Repository**: <https://github.com/docker/mcp-gateway>

## Installation

### Prerequisites

- Docker Desktop (with MCP Toolkit feature enabled)

### Installation as Docker CLI Plugin

```bash
# Docker Desktop users - already installed
docker mcp --help

# Build from source
git clone https://github.com/docker/mcp-gateway.git
cd mcp-gateway
mkdir -p "$HOME/.docker/cli-plugins/"
make docker-mcp
```

## Configuration Structure

### Configuration Directory

**Location**: `~/.docker/mcp/`

**Files**:

- `docker-mcp.yaml` - Server catalog defining available MCP servers
- `registry.yaml` - Registry of enabled servers
- `config.yaml` - Configuration per server
- `tools.yaml` - Enabled tools per server

### docker-mcp.yaml (Server Catalog)

Defines available MCP servers from Docker Hub MCP Catalog.

```yaml
servers:
  context7:
    image: docker.io/upstash/context7:latest
    description: "Developer documentation MCP"
    config_schema:
      type: object
      properties:
        api_key:
          type: string
          description: "API key for Context7"

  filesystem:
    image: docker.io/modelcontextprotocol/filesystem:latest
    description: "Filesystem access MCP"
    config_schema:
      type: object
      properties:
        allowed_paths:
          type: array
          items:
            type: string
```

### registry.yaml (Enabled Servers)

Tracks which servers are enabled for the default gateway configuration.

```yaml
enabled:
  - context7
  - filesystem
  - github
```

### config.yaml (Server Configuration)

Runtime configuration for each enabled server.

```yaml
servers:
  context7:
    env:
      CONTEXT7_API_KEY: secret://context7-key

  filesystem:
    config:
      allowed_paths:
        - /home/user/projects
        - /home/user/documents

  github:
    oauth:
      provider: github
      scopes:
        - repo
        - read:org
```

### tools.yaml (Tool Filtering)

Control which tools from each server are exposed.

```yaml
servers:
  filesystem:
    enabled_tools:
      - read_file
      - write_file
    disabled_tools:
      - delete_file

  github:
    # Omit to enable all tools
```

## Docker MCP CLI Commands

### Catalog Management

```bash
# Initialize the default Docker MCP Catalog
docker mcp catalog init

# List available catalogs
docker mcp catalog ls

# Show all servers in a catalog
docker mcp catalog show docker-mcp

# Add a custom catalog
docker mcp catalog add mycatalog https://example.com/catalog.yaml
```

### Gateway Operations

```bash
# Run gateway with stdio transport (single client)
docker mcp gateway run

# Run gateway with SSE transport (multiple clients)
docker mcp gateway run --port 8080 --transport sse

# Run gateway with streaming transport
docker mcp gateway run --port 8080 --transport streaming

# Run with specific server configuration
docker mcp gateway run --config custom-config.yaml
```

### Server Management

```bash
# List enabled servers
docker mcp server ls

# Enable one or more servers
docker mcp server enable context7 github filesystem

# Disable servers
docker mcp server disable context7

# Get detailed information about a server
docker mcp server inspect context7

# Reset (disable all servers)
docker mcp server reset
```

### Configuration Management

```bash
# Read current configuration
docker mcp config read

# Write new configuration
docker mcp config write '<yaml-config>'

# Edit configuration interactively
docker mcp config edit

# Reset configuration to defaults
docker mcp config reset
```

### Secrets Management

```bash
# Create a secret
docker mcp secret create context7-key "your-api-key-here"

# List secrets
docker mcp secret ls

# Delete a secret
docker mcp secret rm context7-key

# Export secrets for Docker Cloud (temporary workaround)
docker mcp secret export server1 server2
```

### OAuth Management

```bash
# Start OAuth flow for a server
docker mcp oauth login github

# Check OAuth status
docker mcp oauth status github

# Revoke OAuth token
docker mcp oauth logout github
```

### Tools Management

```bash
# List all available tools
docker mcp tools ls

# List tools in JSON format
docker mcp tools ls --format=json

# Count available tools
docker mcp tools count

# Inspect a specific tool
docker mcp tools inspect read_file

# Call a tool directly (for testing)
docker mcp tools call read_file '{"path": "/path/to/file"}'
```

### Client Integration

```bash
# Connect gateway to Claude Code
docker mcp client connect claude-code --global

# Connect to Cursor
docker mcp client connect cursor --global

# Disconnect client
docker mcp client disconnect claude-code
```

## Integration Patterns

### Pattern 1: Global Gateway for All AI Clients

Run a single gateway instance that all AI clients connect to:

```bash
# Start gateway on port 8080
docker mcp gateway run --port 8080 --transport sse

# Configure clients to connect to http://localhost:8080
```

**Codex config.toml**:

```toml
[mcp_servers.docker-gateway]
url = "http://localhost:8080"
```

**Claude Code `.mcp.json`**:

```json
{
  "mcpServers": {
    "docker-gateway": {
      "url": "http://localhost:8080",
      "transport": "sse"
    }
  }
}
```

### Pattern 2: Per-Client Gateway (stdio)

Run separate gateway instances per client using stdio transport:

**Codex**:

```toml
[mcp_servers.docker-gateway]
command = "docker"
args = ["mcp", "gateway", "run"]
```

**Claude Code**:

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

### Pattern 3: Selective Server Access

Different clients can access different sets of servers:

```bash
# Create project-specific configurations
mkdir -p ~/.docker/mcp/profiles/

# Profile for frontend work
cat > ~/.docker/mcp/profiles/frontend.yaml << EOF
servers:
  figma:
    enabled: true
  filesystem:
    enabled: true
EOF

# Profile for backend work
cat > ~/.docker/mcp/profiles/backend.yaml << EOF
servers:
  github:
    enabled: true
  filesystem:
    enabled: true
  postgres:
    enabled: true
EOF

# Run gateway with specific profile
docker mcp gateway run --profile frontend
```

## Environment Variables

- `CLAUDE_CONFIG_DIR` - Override Claude Code config directory
- `CURSOR_CONFIG_DIR` - Override Cursor config directory (if supported)
- `DOCKER_MCP_CONFIG_DIR` - Override Docker MCP config directory (default:
  ~/.docker/mcp/)

## Docker MCP Gateway vs Traditional MCP

### Traditional MCP Server Configuration

**Claude Code (traditional)**:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "env": {
        "CONTEXT7_API_KEY": "your-key"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    }
  }
}
```

### Docker MCP Gateway Approach

**Enable servers in Docker MCP**:

```bash
docker mcp server enable context7 filesystem
docker mcp secret create context7-key "your-key"
docker mcp config write 'servers:
  filesystem:
    config:
      allowed_paths: ["/path/to/dir"]'
```

**Claude Code (gateway)**:

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

**Benefits**:

- ✅ Centralized secrets management
- ✅ Consistent configuration across all clients
- ✅ Container isolation for security
- ✅ No need to manage node/python dependencies
- ✅ OAuth flow handling
- ✅ Easy server enable/disable without editing configs

## Security Features

### Secrets Management

Secrets are stored in Docker Desktop's secure secrets store, not in config
files:

```bash
# Store API key securely
docker mcp secret create github-token "ghp_xxxxxxxxxxxx"

# Reference in config
docker mcp config write 'servers:
  github:
    env:
      GITHUB_TOKEN: secret://github-token'
```

### Container Isolation

Each MCP server runs in an isolated Docker container with:

- Limited host access
- Controlled network permissions
- Defined volume mounts
- Resource limits

### OAuth Access Policies

Control which servers can access OAuth tokens:

```bash
# Grant GitHub OAuth access to specific servers
docker mcp policy grant github-oauth server:github
docker mcp policy grant github-oauth server:copilot

# List policies
docker mcp policy ls

# Revoke access
docker mcp policy revoke github-oauth server:github
```

## Troubleshooting

### Check Gateway Status

```bash
# List running gateway processes
docker mcp gateway status

# View logs
docker mcp gateway logs

# Inspect server health
docker mcp server inspect --health context7
```

### Common Issues

**Server won't start**:

```bash
# Check if server is enabled
docker mcp server ls

# Check configuration
docker mcp config read

# Inspect server details
docker mcp server inspect <server-name>
```

**Tools not available**:

```bash
# List available tools
docker mcp tools ls

# Check if tools are disabled
docker mcp config read | grep disabled_tools
```

**Secret not found**:

```bash
# List secrets
docker mcp secret ls

# Verify secret reference in config
docker mcp config read
```

## Migration from Traditional MCP

### Step 1: Inventory Current MCP Servers

```bash
# List current project MCP servers from Claude Code config
jq '.mcpServers' .mcp.json
```

### Step 2: Enable Equivalent Docker MCP Servers

```bash
# Initialize Docker MCP catalog
docker mcp catalog init

# Find available servers
docker mcp catalog show docker-mcp

# Enable servers
docker mcp server enable <server-names>
```

### Step 3: Migrate Secrets

```bash
# Create secrets in Docker MCP
docker mcp secret create context7-key "your-api-key"
docker mcp secret create github-token "ghp_token"
```

### Step 4: Configure Servers

```bash
# Set server-specific configuration
docker mcp config write 'servers:
  filesystem:
    config:
      allowed_paths: ["/home/user/projects"]
  github:
    oauth:
      provider: github'
```

### Step 5: Update Client Configurations

Replace individual MCP server entries with single gateway entry:

**Before (Claude Code)**:

```json
{
  "mcpServers": {
    "context7": { "command": "npx", "args": [...] },
    "github": { "command": "npx", "args": [...] },
    "filesystem": { "command": "npx", "args": [...] }
  }
}
```

**After (Claude Code)**:

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

## Best Practices

1. **Use Docker MCP Gateway for production** - Better isolation and secrets
  management
1. **Enable only needed servers** - Reduces attack surface and improves
  performance
1. **Store secrets in Docker Desktop** - Never commit API keys to config files
1. **Use profiles for different contexts** - Frontend vs backend vs data science
1. **Monitor gateway logs** - Track usage and troubleshoot issues
1. **Keep servers updated** - Regularly update catalog and server images
1. **Use streaming transport for multiple clients** - More efficient than
  starting multiple gateway instances

## Resources

- [Docker MCP Gateway GitHub](https://github.com/docker/mcp-gateway)
- [Docker MCP Catalog](https://hub.docker.com/mcp)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Docker Desktop MCP Toolkit](https://docs.docker.com/ai/mcp-catalog-and-toolkit/toolkit/)
