#!/usr/bin/env python3
"""
Initialize a multi-agent project with directory structures for all platforms.

This script creates the necessary folders and template files for:
- OpenAI Codex
- Claude Code  
- Cursor
- Gemini (when supported)
- Shared configuration source
"""

import argparse
from pathlib import Path
from typing import List


def create_directory_structure(project_path: Path, platforms: List[str]) -> None:
    """
    Create directory structure for specified platforms.
    
    Args:
        project_path: Root path for the project
        platforms: List of platforms to initialize
    """
    print(f"🚀 Initializing multi-agent project at: {project_path}")
    print(f"   Platforms: {', '.join(platforms)}\n")
    
    # Create shared config directory
    shared_dir = project_path / '.agent-config'
    shared_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created shared config: {shared_dir}")
    
    # Create shared subdirectories
    (shared_dir / 'skills').mkdir(exist_ok=True)
    (shared_dir / 'agents').mkdir(exist_ok=True)
    
    # Create shared files
    create_shared_config_files(shared_dir)
    
    # Platform-specific initialization
    if 'codex' in platforms:
        create_codex_structure(project_path)
    
    if 'claude-code' in platforms:
        create_claude_code_structure(project_path)
    
    if 'cursor' in platforms:
        create_cursor_structure(project_path)
    
    if 'gemini' in platforms:
        create_gemini_structure(project_path)
    
    # Create README
    create_readme(project_path, platforms)
    
    print("\n✅ Multi-agent project initialized successfully!")
    print("\n📝 Next steps:")
    print("   1. Edit .agent-config/rules.md with your project instructions")
    print("   2. Configure MCP servers in .agent-config/mcp-servers.json")
    print("   3. Run sync script to propagate to all platforms")


def create_shared_config_files(shared_dir: Path) -> None:
    """Create shared configuration template files."""
    
    # rules.md
    rules_file = shared_dir / 'rules.md'
    rules_file.write_text("""# Project Rules

## Coding Standards

- TODO: Add your coding standards here
- Example: Use TypeScript for new files
- Example: Write tests for new features

## Workflow

- TODO: Add workflow guidelines
- Example: Run tests before committing
- Example: Update documentation when changing APIs

## Architecture

- TODO: Document architecture decisions
- Example: Use microservices pattern
- Example: Follow REST conventions
""")
    print(f"   Created: {rules_file.name}")
    
    # mcp-servers.json
    mcp_file = shared_dir / 'mcp-servers.json'
    mcp_file.write_text("""{
  "servers": {
    "example-server": {
      "command": "npx",
      "args": ["-y", "@package/name"],
      "env": {},
      "enabled": true,
      "description": "Example MCP server - replace with your servers"
    }
  }
}
""")
    print(f"   Created: {mcp_file.name}")
    
    # README for shared config
    readme = shared_dir / 'README.md'
    readme.write_text("""# Shared Agent Configuration

This directory contains platform-agnostic AI agent configuration that serves as the
source of truth for all platforms.

## Files

- **rules.md**: Custom instructions and project guidelines
- **mcp-servers.json**: MCP server configurations
- **skills/**: Shared skills (Agent Skills standard)
- **agents/**: Agent/subagent definitions

## Workflow

1. Edit configurations here
2. Run sync script to propagate to platform-specific directories
3. Platform-specific configs are generated from these shared files

## Adding Skills

```bash
mkdir -p skills/my-skill
cd skills/my-skill
# Create SKILL.md following Agent Skills standard
```

## Adding Agents

Create agent definition files in `agents/` directory.
Format follows Claude Code subagent format (most comprehensive).
""")
    print(f"   Created: {readme.name}")


def create_codex_structure(project_path: Path) -> None:
    """Create Codex directory structure."""
    skills_dir = project_path / '.agents' / 'skills'
    skills_dir.mkdir(parents=True, exist_ok=True)
    
    # AGENTS.md
    agents_file = project_path / 'AGENTS.md'
    if not agents_file.exists():
        agents_file.write_text("""# Project Instructions for Codex

This file will be populated from .agent-config/rules.md during sync.

You can also add Codex-specific instructions here.
""")
    
    print(f"✅ Created Codex skills directory: {skills_dir}")


def create_claude_code_structure(project_path: Path) -> None:
    """Create Claude Code directory structure."""
    claude_dir = project_path / '.claude'
    claude_dir.mkdir(exist_ok=True)
    
    # Subdirectories
    (claude_dir / 'agents').mkdir(exist_ok=True)
    (claude_dir / 'skills').mkdir(exist_ok=True)
    (claude_dir / 'hooks').mkdir(exist_ok=True)
    (claude_dir / 'output-styles').mkdir(exist_ok=True)
    
    # CLAUDE.md
    rules_file = project_path / 'CLAUDE.md'
    if not rules_file.exists():
        rules_file.write_text("""# Project Rules for Claude Code

This file will be populated from .agent-config/rules.md during sync.

You can also add Claude Code-specific rules here.
""")

    # Project-scoped MCP configuration
    config_file = project_path / '.mcp.json'
    if not config_file.exists():
        config_file.write_text("""{
  "mcpServers": {}
}
""")
    
    print(f"✅ Created Claude Code structure: {claude_dir}")


def create_cursor_structure(project_path: Path) -> None:
    """Create Cursor directory structure."""
    skills_dir = project_path / '.agents' / 'skills'
    skills_dir.mkdir(parents=True, exist_ok=True)

    # Cursor and Codex both discover AGENTS.md. Avoid overwriting a file that
    # Codex initialization (or the project) already created.
    agents_file = project_path / 'AGENTS.md'
    if not agents_file.exists():
        agents_file.write_text("""# Project Instructions

This file will be populated from .agent-config/rules.md during sync.
""")

    print(f"✅ Created Cursor skills directory: {skills_dir}")


def create_gemini_structure(project_path: Path) -> None:
    """Create Gemini directory structure (placeholder)."""
    gemini_dir = project_path / '.gemini'
    gemini_dir.mkdir(exist_ok=True)
    
    # Placeholder README
    readme = gemini_dir / 'README.md'
    readme.write_text("""# Gemini Configuration

Placeholder for Gemini AI Code configuration.

Structure will be added when Gemini configuration format is documented.
""")
    
    print(f"✅ Created Gemini structure: {gemini_dir} (placeholder)")


def create_readme(project_path: Path, platforms: List[str]) -> None:
    """Create project README."""
    readme = project_path / 'MULTI-AGENT-README.md'
    
    content = f"""# Multi-Agent AI Code Project

This project is configured to work with multiple AI code agent platforms:
{chr(10).join(f'- {p}' for p in platforms)}

## Directory Structure

- `.agent-config/` - Shared configuration (source of truth)
- `.agents/skills/` - Shared Codex and Cursor skills
- `.claude/skills/` - Claude Code skills
- `.claude/` - Other Claude Code-specific files
- `.gemini/` - Gemini specific files (when supported)

## Workflow

### 1. Edit Shared Configuration

```bash
# Edit shared rules
vim .agent-config/rules.md

# Edit MCP servers
vim .agent-config/mcp-servers.json

# Add skills
mkdir -p .agent-config/skills/my-skill
vim .agent-config/skills/my-skill/SKILL.md
```

### 2. Sync to Platforms

Resolve the bundled `scripts/sync_config.py` from the installed
`multi-agent-config` skill, then run it with this project as the path. Pass
`--to all` for every supported target or, for example, `--to claude-code` for
one target.

### 3. Use Your Preferred Agent

Launch your preferred AI code agent - it will have access to the synced configuration.

## Configuration Management

The `.agent-config/` directory is the single source of truth. Platform-specific
directories are generated from this shared configuration.

### Manual Platform-Specific Customization

You can add platform-specific customizations to:
- `AGENTS.md` (Codex and Cursor)
- `CLAUDE.md` (Claude Code only)

These customizations are preserved; sync replaces only its delimited shared-rules block.

## Skills

Skills follow the Agent Skills standard and are compatible with Codex, Claude Code,
and Cursor.
Add skills to `.agent-config/skills/` and they'll be synced to all platforms.

## MCP Servers

MCP server formats differ by platform. Edit `.agent-config/mcp-servers.json` and
sync only to targets the helper reports as implemented; follow current vendor
documentation for targets it marks unsupported.
"""
    
    readme.write_text(content)
    print(f"\n✅ Created: {readme.name}")


def main():
    parser = argparse.ArgumentParser(
        description='Initialize multi-agent project structure'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Project path (default: current directory)'
    )
    parser.add_argument(
        '--platforms',
        nargs='+',
        choices=['codex', 'claude-code', 'cursor', 'gemini', 'all'],
        default=['all'],
        help='Platforms to initialize (default: all)'
    )
    
    args = parser.parse_args()
    
    project_path = Path(args.path).resolve()
    
    # Expand 'all' to all platforms
    if 'all' in args.platforms:
        platforms = ['codex', 'claude-code', 'cursor', 'gemini']
    else:
        platforms = args.platforms
    
    # Create structure
    create_directory_structure(project_path, platforms)


if __name__ == '__main__':
    main()
