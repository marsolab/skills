#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Regenerate all marketplace and plugin manifest files from SKILL.md frontmatter.

Usage:
    uv run scripts/sync-manifests.py           # regenerate
    uv run scripts/sync-manifests.py --check   # exit 1 if any file would change (CI)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

CATEGORIES: dict[str, str] = {
    "apple-dev": "development",
    "copy": "writing",
    "front-dev": "development",
    "go-cli": "development",
    "go-concurrency": "development",
    "go-dev": "development",
    "go-errors": "development",
    "go-http": "development",
    "go-lint": "development",
    "go-logging": "development",
    "go-sql": "development",
    "go-style": "development",
    "go-testing": "development",
    "kinde": "development",
    "landing-page-breakdown": "design",
    "multi-agent-config": "devops",
    "sqlite": "development",
    "sys-arch": "architecture",
    "things": "productivity",
}

DISPLAY_NAMES: dict[str, str] = {
    "apple-dev": "Apple Dev",
    "copy": "SaaS Copywriting",
    "front-dev": "Front Dev",
    "go-cli": "Go CLI",
    "go-concurrency": "Go Concurrency",
    "go-dev": "Go Dev",
    "go-errors": "Go Errors",
    "go-http": "Go HTTP",
    "go-lint": "Go Lint",
    "go-logging": "Go Logging",
    "go-sql": "Go SQL",
    "go-style": "Go Style",
    "go-testing": "Go Testing",
    "kinde": "Kinde",
    "landing-page-breakdown": "Landing Page Breakdown",
    "multi-agent-config": "Multi-Agent Config",
    "sqlite": "SQLite",
    "sys-arch": "Sys Arch",
    "things": "Things",
}

CATEGORY_DISPLAY: dict[str, str] = {
    "development": "Development",
    "writing": "Writing",
    "design": "Design",
    "devops": "DevOps",
    "architecture": "Architecture",
    "productivity": "Productivity",
}


def parse_frontmatter(path: Path) -> dict:
    """Extract YAML frontmatter from a SKILL.md file."""
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    end = text.index("---", 3)
    raw = text[3:end]
    data = yaml.safe_load(raw) or {}
    return {
        "name": data.get("name", ""),
        "description": data.get("description", ""),
        "version": str(data.get("version", "1.0.0")),
        "tags": data.get("tags", []),
    }


def short_description(desc: str, limit: int = 120) -> str:
    """Return the first sentence, truncated to *limit* chars."""
    first = desc.split(". ")[0]
    if not first.endswith("."):
        first += "."
    if len(first) > limit:
        return first[: limit - 3] + "..."
    return first


def write_json(path: Path, obj: dict | list, *, check: bool) -> bool:
    """Write *obj* as indented JSON. Returns True when the file changed."""
    content = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text() == content:
        return False
    if check:
        print(f"DRIFT: {path.relative_to(REPO_ROOT)}")
        return True
    path.write_text(content)
    print(f"Updated: {path.relative_to(REPO_ROOT)}")
    return True


def discover_hooks(plugin_dir_name: str) -> list[str]:
    """Return relative paths to hook scripts for a plugin."""
    hooks_dir = REPO_ROOT / "plugins" / plugin_dir_name / "hooks"
    if not hooks_dir.is_dir():
        return []
    return sorted(
        f"hooks/{p.name}"
        for p in hooks_dir.iterdir()
        if p.is_file() and p.suffix == ".sh"
    )


def discover_plugins() -> list[tuple[str, dict]]:
    """Return sorted (plugin_dir_name, frontmatter) pairs."""
    plugins: list[tuple[str, dict]] = []
    for skill_md in sorted(REPO_ROOT.glob("plugins/*/skills/*/SKILL.md")):
        plugin_dir = skill_md.parent.parent.parent.name
        fm = parse_frontmatter(skill_md)
        if fm.get("name"):
            plugins.append((plugin_dir, fm))
    return plugins


def main() -> int:
    check = "--check" in sys.argv[1:]
    drift = False
    plugins = discover_plugins()

    claude_entries: list[dict] = []
    codex_entries: list[dict] = []

    for plugin_dir, fm in plugins:
        name = fm["name"]
        desc = fm["description"]
        ver = fm["version"]
        tags = fm["tags"]
        category = CATEGORIES.get(plugin_dir, "development")
        display = DISPLAY_NAMES.get(plugin_dir, name)
        cat_display = CATEGORY_DISPLAY.get(category, category)
        short_desc = short_description(desc)

        # Per-plugin: Claude Code
        claude_plugin: dict = {"name": name, "description": desc, "version": ver}
        hooks = discover_hooks(plugin_dir)
        if hooks:
            claude_plugin["hooks"] = hooks
        p = REPO_ROOT / "plugins" / plugin_dir / ".claude-plugin" / "plugin.json"
        if write_json(p, claude_plugin, check=check):
            drift = True

        # Per-plugin: Codex
        codex_plugin = {
            "name": name,
            "version": ver,
            "description": desc,
            "skills": "./skills/",
            "interface": {
                "displayName": display,
                "shortDescription": short_desc,
                "category": cat_display,
            },
        }
        p = REPO_ROOT / "plugins" / plugin_dir / ".codex-plugin" / "plugin.json"
        if write_json(p, codex_plugin, check=check):
            drift = True

        # Collect marketplace entries
        claude_entries.append(
            {
                "name": name,
                "source": f"./plugins/{plugin_dir}",
                "description": desc,
                "version": ver,
                "keywords": tags,
                "category": category,
            }
        )
        codex_entries.append(
            {
                "name": name,
                "source": {"source": "local", "path": f"./plugins/{plugin_dir}"},
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": cat_display,
            }
        )

    # Root: Claude Code marketplace
    claude_marketplace = {
        "name": "marsolab-skills",
        "owner": {"name": "marsolab"},
        "metadata": {
            "description": "Curated skills for AI coding agents by marsolab",
            "version": "1.0.0",
            "pluginRoot": "./plugins",
        },
        "plugins": claude_entries,
    }
    p = REPO_ROOT / ".claude-plugin" / "marketplace.json"
    if write_json(p, claude_marketplace, check=check):
        drift = True

    # Root: Codex marketplace
    codex_marketplace = {
        "name": "marsolab-skills",
        "interface": {"displayName": "Marsolab Skills"},
        "plugins": codex_entries,
    }
    p = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
    if write_json(p, codex_marketplace, check=check):
        drift = True

    if drift:
        print()
        print("ERROR: Manifests are out of sync with SKILL.md frontmatter.")
        print("Run: uv run scripts/sync-manifests.py")
        return 1

    print("All manifests are up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
