#!/usr/bin/env python3
"""
Translation utilities for converting configurations between AI code agent platforms.

This module provides functions to translate:
- MCP server configurations (TOML ↔ JSON)
- Custom instructions/rules
- Skills (Agent Skills standard)
- Subagents/agents
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import tomli
    import tomli_w
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False
    print("Warning: tomli/tomli_w not available. Install with: pip install tomli tomli-w")


class ConfigTranslator:
    """Translate configurations between different platforms."""
    
    @staticmethod
    def toml_mcp_to_json(toml_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Codex TOML MCP config to Claude Code JSON format.
        
        Args:
            toml_config: Parsed TOML config dict
            
        Returns:
            JSON-compatible dict with mcpServers
        """
        mcp_servers = {}
        
        for name, config in toml_config.get('mcp_servers', {}).items():
            server_config = {}
            
            # STDIO server
            if 'command' in config:
                server_config['command'] = config['command']
                if 'args' in config:
                    server_config['args'] = config['args']
                if 'env' in config:
                    server_config['env'] = config['env']
                if 'cwd' in config:
                    server_config['cwd'] = config['cwd']
            
            # HTTP server
            if 'url' in config:
                server_config['url'] = config['url']
                server_config['transport'] = 'sse'
                if 'bearer_token_env_var' in config:
                    # Note: format may differ
                    server_config['bearer_token_env_var'] = config['bearer_token_env_var']
            
            mcp_servers[name] = server_config
        
        return {'mcpServers': mcp_servers}
    
    @staticmethod
    def json_mcp_to_toml(json_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Claude Code JSON MCP config to Codex TOML format.
        
        Args:
            json_config: JSON config dict
            
        Returns:
            TOML-compatible dict with mcp_servers
        """
        mcp_servers = {}
        
        for name, config in json_config.get('mcpServers', {}).items():
            server_config = {}
            
            # STDIO server
            if 'command' in config:
                server_config['command'] = config['command']
                if 'args' in config:
                    server_config['args'] = config['args']
                if 'env' in config:
                    server_config['env'] = config['env']
                if 'cwd' in config:
                    server_config['cwd'] = config['cwd']
            
            # HTTP server  
            if 'url' in config:
                server_config['url'] = config['url']
                if 'bearer_token_env_var' in config:
                    server_config['bearer_token_env_var'] = config['bearer_token_env_var']
            
            mcp_servers[name] = server_config
        
        return {'mcp_servers': mcp_servers}
    
    @staticmethod
    def merge_agents_md_files(agents_files: List[Path]) -> str:
        """
        Merge hierarchical AGENTS.md files into a single rules file.
        
        Args:
            agents_files: List of AGENTS.md file paths (in order)
            
        Returns:
            Merged content as string
        """
        sections = []
        
        for file_path in agents_files:
            if file_path.exists():
                with open(file_path) as f:
                    content = f.read().strip()
                    if content:
                        sections.append(f"# From: {file_path.name}\n\n{content}")
        
        return "\n\n---\n\n".join(sections)
    
    @staticmethod
    def skill_to_subagent(skill_md_path: Path) -> Optional[Dict[str, Any]]:
        """
        Convert a Codex skill to Claude Code subagent format.
        
        Only converts skills that have descriptions suggesting delegation.
        
        Args:
            skill_md_path: Path to SKILL.md file
            
        Returns:
            Dict with subagent config or None if not suitable
        """
        if not skill_md_path.exists():
            return None
        
        with open(skill_md_path) as f:
            content = f.read()
        
        # Parse frontmatter
        if not content.startswith('---'):
            return None
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None
        
        frontmatter = parts[1].strip()
        body = parts[2].strip()
        
        # Simple YAML parsing (name and description)
        name = None
        description = None
        
        for line in frontmatter.split('\n'):
            if line.startswith('name:'):
                name = line.split(':', 1)[1].strip()
            elif line.startswith('description:'):
                description = line.split(':', 1)[1].strip()
        
        if not name or not description:
            return None
        
        # Check if this skill should be a subagent
        delegation_keywords = ['use proactively', 'delegate', 'specialist', 'expert']
        should_convert = any(kw in description.lower() for kw in delegation_keywords)
        
        if not should_convert:
            return None
        
        return {
            'name': name,
            'description': description,
            'frontmatter': frontmatter,
            'body': body
        }
    
    @staticmethod
    def create_subagent_md(name: str, description: str, body: str, 
                          tools: Optional[List[str]] = None,
                          model: str = 'sonnet') -> str:
        """
        Create Claude Code subagent .md content.
        
        Args:
            name: Subagent name
            description: When to invoke
            body: System prompt content
            tools: Optional list of tools (None = inherit all)
            model: Model to use (sonnet|opus|haiku|inherit)
            
        Returns:
            Complete .md file content
        """
        frontmatter_lines = [
            '---',
            f'name: {name}',
            f'description: {description}'
        ]
        
        if tools:
            frontmatter_lines.append(f"tools: {', '.join(tools)}")
        
        frontmatter_lines.append(f'model: {model}')
        frontmatter_lines.append('---')
        
        return '\n'.join(frontmatter_lines) + '\n\n' + body


def load_toml(file_path: Path) -> Dict[str, Any]:
    """Load TOML file."""
    if not TOML_AVAILABLE:
        raise ImportError("tomli not available. Install with: pip install tomli")
    
    with open(file_path, 'rb') as f:
        return tomli.load(f)


def save_toml(data: Dict[str, Any], file_path: Path) -> None:
    """Save TOML file."""
    if not TOML_AVAILABLE:
        raise ImportError("tomli_w not available. Install with: pip install tomli-w")
    
    with open(file_path, 'wb') as f:
        tomli_w.dump(data, f)


def load_json(file_path: Path) -> Dict[str, Any]:
    """Load JSON file."""
    with open(file_path) as f:
        return json.load(f)


def save_json(data: Dict[str, Any], file_path: Path, indent: int = 2) -> None:
    """Save JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=indent)
        f.write('\n')


if __name__ == '__main__':
    # Example usage
    print("Translation utilities loaded.")
    print("Use this module to convert between platform formats.")
    
    if not TOML_AVAILABLE:
        print("\nNote: Install tomli and tomli_w for TOML support:")
        print("  pip install tomli tomli-w")
