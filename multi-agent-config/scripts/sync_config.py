#!/usr/bin/env python3
"""
Sync configurations across AI code agent platforms.

This script propagates configuration from a shared source or from one platform to others.
Supports syncing:
- MCP servers
- Custom instructions/rules
- Skills
- Agents/subagents
"""

import argparse
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import translation utilities
import sys
sys.path.insert(0, str(Path(__file__).parent))
from translate_utils import (
    ConfigTranslator,
    load_json,
    save_json,
    load_toml,
    save_toml,
    TOML_AVAILABLE
)


class ConfigSyncer:
    """Sync configurations across platforms."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.shared_dir = project_path / '.agent-config'
        self.translator = ConfigTranslator()
    
    def sync_mcp_servers(self, target_platforms: List[str]) -> None:
        """
        Sync MCP servers to target platforms.
        
        Args:
            target_platforms: List of platforms to sync to
        """
        print("🔄 Syncing MCP servers...")
        
        # Load shared MCP config
        mcp_file = self.shared_dir / 'mcp-servers.json'
        if not mcp_file.exists():
            print("   ⚠️  No shared MCP config found")
            return
        
        shared_mcp = load_json(mcp_file)
        servers = shared_mcp.get('servers', {})
        
        if not servers:
            print("   ⚠️  No MCP servers configured")
            return
        
        print(f"   Found {len(servers)} MCP server(s)")
        
        # Sync to Codex
        if 'codex' in target_platforms:
            self._sync_mcp_to_codex(servers)
        
        # Sync to Claude Code
        if 'claude-code' in target_platforms:
            self._sync_mcp_to_claude_code(servers)
        
        # Sync to Cursor
        if 'cursor' in target_platforms:
            self._sync_mcp_to_cursor(servers)
        
        # Sync to Gemini
        if 'gemini' in target_platforms:
            self._sync_mcp_to_gemini(servers)
    
    def _sync_mcp_to_codex(self, servers: Dict[str, Any]) -> None:
        """Sync MCP servers to Codex config.toml."""
        config_file = Path.home() / '.codex' / 'config.toml'
        
        if not TOML_AVAILABLE:
            print("   ⚠️  Cannot sync to Codex: tomli/tomli_w not installed")
            return
        
        # Load existing config or create new
        if config_file.exists():
            config = load_toml(config_file)
        else:
            config = {}
        
        # Convert and merge MCP servers
        if 'mcp_servers' not in config:
            config['mcp_servers'] = {}
        
        for name, server in servers.items():
            if not server.get('enabled', True):
                continue
                
            config['mcp_servers'][name] = {
                'command': server.get('command'),
                'args': server.get('args', [])
            }
            
            if 'env' in server and server['env']:
                config['mcp_servers'][name]['env'] = server['env']
            
            if 'url' in server:
                config['mcp_servers'][name]['url'] = server['url']
        
        # Save
        config_file.parent.mkdir(parents=True, exist_ok=True)
        save_toml(config, config_file)
        print(f"   ✅ Synced to Codex: {config_file}")
    
    def _sync_mcp_to_claude_code(self, servers: Dict[str, Any]) -> None:
        """Sync MCP servers to Claude Code config.json."""
        config_file = self.project_path / '.claude' / 'config.json'
        
        # Load existing config or create new
        if config_file.exists():
            config = load_json(config_file)
        else:
            config = {}
        
        # Convert and merge MCP servers
        if 'mcpServers' not in config:
            config['mcpServers'] = {}
        
        for name, server in servers.items():
            if not server.get('enabled', True):
                continue
            
            server_config = {
                'command': server.get('command'),
                'args': server.get('args', [])
            }
            
            if 'env' in server and server['env']:
                server_config['env'] = server['env']
            
            if 'url' in server:
                server_config['url'] = server['url']
                server_config['transport'] = 'sse'
            
            config['mcpServers'][name] = server_config
        
        # Save
        config_file.parent.mkdir(parents=True, exist_ok=True)
        save_json(config, config_file)
        print(f"   ✅ Synced to Claude Code: {config_file}")
    
    def _sync_mcp_to_cursor(self, servers: Dict[str, Any]) -> None:
        """Sync MCP servers to Cursor (placeholder)."""
        print("   ⚠️  Cursor MCP sync not yet implemented (format TBD)")
    
    def _sync_mcp_to_gemini(self, servers: Dict[str, Any]) -> None:
        """Sync MCP servers to Gemini (placeholder)."""
        print("   ⚠️  Gemini MCP sync not yet implemented (format TBD)")
    
    def sync_rules(self, target_platforms: List[str]) -> None:
        """
        Sync custom instructions/rules to target platforms.
        
        Args:
            target_platforms: List of platforms to sync to
        """
        print("\n🔄 Syncing rules/instructions...")
        
        # Load shared rules
        rules_file = self.shared_dir / 'rules.md'
        if not rules_file.exists():
            print("   ⚠️  No shared rules found")
            return
        
        rules_content = rules_file.read_text()
        
        # Sync to Codex (AGENTS.md)
        if 'codex' in target_platforms:
            agents_file = self.project_path / 'AGENTS.md'
            
            # Preserve existing content if any
            existing = ""
            if agents_file.exists():
                existing = agents_file.read_text()
                if "# Shared Configuration" not in existing:
                    existing = existing + "\n\n---\n\n"
            
            content = existing + "# Shared Configuration\n\n" + rules_content
            agents_file.write_text(content)
            print(f"   ✅ Synced to Codex: {agents_file}")
        
        # Sync to Claude Code (rules.md)
        if 'claude-code' in target_platforms:
            claude_rules = self.project_path / '.claude' / 'rules.md'
            
            # Preserve existing content if any
            existing = ""
            if claude_rules.exists():
                existing = claude_rules.read_text()
                if "# Shared Configuration" not in existing:
                    existing = existing + "\n\n---\n\n"
            
            content = existing + "# Shared Configuration\n\n" + rules_content
            claude_rules.parent.mkdir(parents=True, exist_ok=True)
            claude_rules.write_text(content)
            print(f"   ✅ Synced to Claude Code: {claude_rules}")
        
        # Sync to Cursor (.cursorrules)
        if 'cursor' in target_platforms:
            cursorrules = self.project_path / '.cursorrules'
            
            # Preserve existing content if any
            existing = ""
            if cursorrules.exists():
                existing = cursorrules.read_text()
                if "# Shared Configuration" not in existing:
                    existing = existing + "\n\n---\n\n"
            
            content = existing + "# Shared Configuration\n\n" + rules_content
            cursorrules.write_text(content)
            print(f"   ✅ Synced to Cursor: {cursorrules}")
        
        if 'gemini' in target_platforms:
            print("   ⚠️  Gemini rules sync not yet implemented (format TBD)")
    
    def sync_skills(self, target_platforms: List[str]) -> None:
        """
        Sync skills to target platforms.
        
        Args:
            target_platforms: List of platforms to sync to
        """
        print("\n🔄 Syncing skills...")
        
        shared_skills = self.shared_dir / 'skills'
        if not shared_skills.exists() or not list(shared_skills.iterdir()):
            print("   ⚠️  No shared skills found")
            return
        
        skill_dirs = [d for d in shared_skills.iterdir() if d.is_dir()]
        print(f"   Found {len(skill_dirs)} skill(s)")
        
        # Sync to Codex
        if 'codex' in target_platforms:
            target = self.project_path / '.codex' / 'skills'
            target.mkdir(parents=True, exist_ok=True)
            
            for skill_dir in skill_dirs:
                dest = target / skill_dir.name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(skill_dir, dest)
            
            print(f"   ✅ Synced to Codex: {target}")
        
        # Sync to Claude Code
        if 'claude-code' in target_platforms:
            target = self.project_path / '.claude' / 'skills'
            target.mkdir(parents=True, exist_ok=True)
            
            for skill_dir in skill_dirs:
                dest = target / skill_dir.name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(skill_dir, dest)
            
            print(f"   ✅ Synced to Claude Code: {target}")
        
        # Sync to Cursor
        if 'cursor' in target_platforms:
            target = self.project_path / '.cursor' / 'skills'
            target.mkdir(parents=True, exist_ok=True)
            
            for skill_dir in skill_dirs:
                dest = target / skill_dir.name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(skill_dir, dest)
            
            print(f"   ✅ Synced to Cursor: {target}")
        
        if 'gemini' in target_platforms:
            print("   ⚠️  Gemini skills sync not yet implemented")
    
    def sync_agents(self, target_platforms: List[str]) -> None:
        """
        Sync agents/subagents to target platforms.
        
        Args:
            target_platforms: List of platforms to sync to
        """
        print("\n🔄 Syncing agents/subagents...")
        
        shared_agents = self.shared_dir / 'agents'
        if not shared_agents.exists() or not list(shared_agents.glob('*.md')):
            print("   ⚠️  No shared agents found")
            return
        
        agent_files = list(shared_agents.glob('*.md'))
        print(f"   Found {len(agent_files)} agent(s)")
        
        # Sync to Claude Code (native support)
        if 'claude-code' in target_platforms:
            target = self.project_path / '.claude' / 'agents'
            target.mkdir(parents=True, exist_ok=True)
            
            for agent_file in agent_files:
                dest = target / agent_file.name
                shutil.copy2(agent_file, dest)
            
            print(f"   ✅ Synced to Claude Code: {target}")
        
        # For Codex, convert to skills if appropriate
        if 'codex' in target_platforms:
            print("   ℹ️  Codex uses skills paradigm (agents would need conversion)")
        
        if 'cursor' in target_platforms:
            print("   ⚠️  Cursor agent sync not yet implemented (format TBD)")
        
        if 'gemini' in target_platforms:
            print("   ⚠️  Gemini agent sync not yet implemented")
    
    def sync_all(self, target_platforms: List[str]) -> None:
        """
        Sync all configuration types to target platforms.
        
        Args:
            target_platforms: List of platforms to sync to
        """
        self.sync_mcp_servers(target_platforms)
        self.sync_rules(target_platforms)
        self.sync_skills(target_platforms)
        self.sync_agents(target_platforms)
    
    def migrate_to_docker_mcp_gateway(self, source_platform: str = 'auto') -> None:
        """
        Migrate MCP server configurations to Docker MCP Gateway.
        
        Args:
            source_platform: Platform to migrate from (auto, codex, claude-code)
        """
        print("\n🐳 Migrating to Docker MCP Gateway...")
        
        # Auto-detect source platform if needed
        if source_platform == 'auto':
            if (self.project_path / '.codex').exists():
                source_platform = 'codex'
            elif (self.project_path / '.claude').exists():
                source_platform = 'claude-code'
            else:
                print("   ⚠️  Could not auto-detect source platform")
                return
        
        print(f"   Source platform: {source_platform}")
        
        # Extract MCP servers from source platform
        servers = self._extract_mcp_servers(source_platform)
        
        if not servers:
            print("   ⚠️  No MCP servers found to migrate")
            return
        
        print(f"   Found {len(servers)} MCP server(s)")
        
        # Generate Docker MCP Gateway setup instructions
        self._generate_docker_mcp_instructions(servers)
        
        # Update client configs to use gateway
        self._update_clients_for_gateway()
    
    def _extract_mcp_servers(self, platform: str) -> Dict[str, Any]:
        """Extract MCP server configurations from a platform."""
        servers = {}
        
        if platform == 'codex':
            config_file = Path.home() / '.codex' / 'config.toml'
            if config_file.exists() and TOML_AVAILABLE:
                config = load_toml(config_file)
                servers = config.get('mcp_servers', {})
        
        elif platform == 'claude-code':
            config_file = self.project_path / '.claude' / 'config.json'
            if not config_file.exists():
                config_file = Path.home() / '.claude' / 'config.json'
            
            if config_file.exists():
                config = load_json(config_file)
                servers = config.get('mcpServers', {})
        
        return servers
    
    def _generate_docker_mcp_instructions(self, servers: Dict[str, Any]) -> None:
        """Generate Docker MCP Gateway setup instructions."""
        instructions_file = self.project_path / 'DOCKER_MCP_SETUP.md'
        
        instructions = """# Docker MCP Gateway Setup Instructions

## Overview

This file contains the commands needed to migrate your MCP servers to Docker MCP Gateway.

## Prerequisites

1. Install Docker Desktop
2. Enable MCP Toolkit in Docker Desktop settings
3. Initialize the Docker MCP catalog:
   ```bash
   docker mcp catalog init
   ```

## Migration Steps

### 1. Enable MCP Servers

"""
        
        for server_name in servers.keys():
            instructions += f"# Enable {server_name}\n"
            instructions += f"docker mcp server enable {server_name}\n\n"
        
        instructions += """
### 2. Configure Secrets

"""
        
        for server_name, config in servers.items():
            if 'env' in config:
                for env_key, env_value in config['env'].items():
                    if 'key' in env_key.lower() or 'token' in env_key.lower() or 'secret' in env_key.lower():
                        secret_name = f"{server_name}-{env_key.lower()}"
                        instructions += f"# Create secret for {server_name}\n"
                        instructions += f"docker mcp secret create {secret_name} \"YOUR_{env_key}_HERE\"\n\n"
        
        instructions += """
### 3. Configure Servers

Create server configuration file:

```bash
docker mcp config write 'servers:
"""
        
        for server_name, config in servers.items():
            if 'env' in config:
                instructions += f"  {server_name}:\n"
                instructions += f"    env:\n"
                for env_key in config['env'].keys():
                    if 'key' in env_key.lower() or 'token' in env_key.lower() or 'secret' in env_key.lower():
                        secret_name = f"{server_name}-{env_key.lower()}"
                        instructions += f"      {env_key}: secret://{secret_name}\n"
        
        instructions += """'
```

### 4. Test Gateway

```bash
# Run gateway
docker mcp gateway run

# In another terminal, test tools
docker mcp tools ls
```

### 5. Update Client Configurations

Your client configurations have been updated to use the Docker MCP Gateway.
See the updated config files in .codex/ and .claude/ directories.

## Verification

After completing these steps:

1. Start your AI code assistant
2. Verify that MCP tools are available
3. Test a few tool calls to ensure everything works

## Rollback

If you need to rollback:

1. Restore the backup config files (*.backup)
2. Restart your AI code assistant

## Next Steps

- Enable additional servers from Docker MCP catalog: `docker mcp catalog show docker-mcp`
- Configure OAuth for servers that need it: `docker mcp oauth --help`
- Set up custom access policies: `docker mcp policy --help`
"""
        
        instructions_file.write_text(instructions)
        print(f"\n   ✅ Generated setup instructions: {instructions_file}")
    
    def _update_clients_for_gateway(self) -> None:
        """Update client configurations to use Docker MCP Gateway."""
        # Update Codex config
        codex_config = Path.home() / '.codex' / 'config.toml'
        if codex_config.exists() and TOML_AVAILABLE:
            # Backup existing config
            backup_file = codex_config.parent / 'config.toml.backup'
            shutil.copy2(codex_config, backup_file)
            print(f"   ✅ Backed up Codex config: {backup_file}")
            
            # Update to use gateway
            config = load_toml(codex_config)
            config['mcp_servers'] = {
                'docker-gateway': {
                    'command': 'docker',
                    'args': ['mcp', 'gateway', 'run']
                }
            }
            save_toml(config, codex_config)
            print(f"   ✅ Updated Codex config: {codex_config}")
        
        # Update Claude Code config
        claude_config = self.project_path / '.claude' / 'config.json'
        if not claude_config.exists():
            claude_config = Path.home() / '.claude' / 'config.json'
        
        if claude_config.exists():
            # Backup existing config
            backup_file = claude_config.parent / 'config.json.backup'
            shutil.copy2(claude_config, backup_file)
            print(f"   ✅ Backed up Claude Code config: {backup_file}")
            
            # Update to use gateway
            config = load_json(claude_config)
            config['mcpServers'] = {
                'docker-gateway': {
                    'command': 'docker',
                    'args': ['mcp', 'gateway', 'run']
                }
            }
            save_json(config, claude_config)
            print(f"   ✅ Updated Claude Code config: {claude_config}")


def main():
    parser = argparse.ArgumentParser(
        description='Sync AI agent configurations across platforms'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Project path (default: current directory)'
    )
    parser.add_argument(
        '--to',
        nargs='+',
        choices=['codex', 'claude-code', 'cursor', 'gemini', 'all'],
        default=['all'],
        help='Target platforms to sync to (default: all)'
    )
    parser.add_argument(
        '--mcp-only',
        action='store_true',
        help='Sync only MCP servers'
    )
    parser.add_argument(
        '--rules-only',
        action='store_true',
        help='Sync only rules/instructions'
    )
    parser.add_argument(
        '--skills-only',
        action='store_true',
        help='Sync only skills'
    )
    parser.add_argument(
        '--agents-only',
        action='store_true',
        help='Sync only agents/subagents'
    )
    parser.add_argument(
        '--migrate-to-docker-mcp',
        action='store_true',
        help='Migrate MCP servers to Docker MCP Gateway'
    )
    parser.add_argument(
        '--from',
        dest='from_platform',
        choices=['auto', 'codex', 'claude-code'],
        default='auto',
        help='Source platform for Docker MCP migration (default: auto)'
    )
    
    args = parser.parse_args()
    
    project_path = Path(args.path).resolve()
    
    # Expand 'all' to all platforms
    if 'all' in args.to:
        target_platforms = ['codex', 'claude-code', 'cursor', 'gemini']
    else:
        target_platforms = args.to
    
    # Create syncer
    syncer = ConfigSyncer(project_path)
    
    # Handle Docker MCP migration
    if args.migrate_to_docker_mcp:
        print("🐳 Migrating to Docker MCP Gateway\n")
        syncer.migrate_to_docker_mcp_gateway(args.from_platform)
        print("\n✅ Migration preparation complete!")
        print("\n📝 Next steps:")
        print("   1. Review DOCKER_MCP_SETUP.md")
        print("   2. Run the docker mcp commands")
        print("   3. Test your AI code assistant")
        return
    
    print(f"📦 Syncing configurations to: {', '.join(target_platforms)}\n")
    
    # Sync based on flags
    if args.mcp_only:
        syncer.sync_mcp_servers(target_platforms)
    elif args.rules_only:
        syncer.sync_rules(target_platforms)
    elif args.skills_only:
        syncer.sync_skills(target_platforms)
    elif args.agents_only:
        syncer.sync_agents(target_platforms)
    else:
        # Sync everything
        syncer.sync_all(target_platforms)
    
    print("\n✅ Sync complete!")


if __name__ == '__main__':
    main()
