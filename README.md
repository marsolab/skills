# Marsolab Skills Marketplace

A dual-compatible plugin marketplace for **Claude Code**
and **OpenAI Codex**, providing curated skills for AI
coding agents.

## Installation

### Claude Code

```shell
/plugin marketplace add marsolab/skills
```

Then install individual plugins:

```shell
/plugin install go-dev@marsolab-skills
/plugin install sys-arch@marsolab-skills
```

### OpenAI Codex

Clone this repository into your project and Codex will
discover plugins from `.agents/plugins/marketplace.json`
automatically.

## Available Plugins

| Plugin | Category | Description |
|--------|----------|-------------|
| [apple-dev][1] | Development | Swift, SwiftUI, HIG |
| [copy][2] | Writing | SaaS copywriting |
| [go-dev][3] | Development | Go backends, CLIs |
| [landing-page-breakdown][4] | Design | Page analysis |
| [multi-agent-config][5] | DevOps | Multi-agent configs |
| [sys-arch][6] | Architecture | System design |
| [front-dev][7] | Development | Modern web apps |

[1]: plugins/apple-dev/skills/apple-dev/SKILL.md
[2]: plugins/copy/skills/copy/SKILL.md
[3]: plugins/go-dev/skills/go-dev/SKILL.md
[4]: plugins/landing-page-breakdown/skills/landing-page-breakdown/SKILL.md
[5]: plugins/multi-agent-config/skills/multi-agent-config/SKILL.md
[6]: plugins/sys-arch/skills/sys-arch/SKILL.md
[7]: plugins/front-dev/skills/front-dev/SKILL.md

## Adding a New Plugin

1. Create the plugin directory structure:

   ```text
   plugins/<plugin-name>/
   ├── .claude-plugin/plugin.json
   ├── .codex-plugin/plugin.json
   └── skills/<skill-name>/
       ├── SKILL.md
       └── references/    (optional)
   ```

1. Add the SKILL.md with YAML frontmatter:

   ```yaml
   ---
   name: my-skill
   description: What this skill does.
   version: 1.0.0
   tags:
     - tag1
     - tag2
   ---
   ```

1. Run the sync script to regenerate manifests:

   ```bash
   uv run scripts/sync-manifests.py
   ```

1. Update the category and display name mappings in
   `scripts/sync-manifests.py` if needed.

1. Commit all changes and push to `main`.

## Repository Structure

```text
.claude-plugin/marketplace.json    # Claude Code
.agents/plugins/marketplace.json   # Codex
plugins/
  <plugin-name>/
    .claude-plugin/plugin.json
    .codex-plugin/plugin.json
    skills/<skill-name>/
      SKILL.md
      references/
      assets/
      scripts/
scripts/
  sync-manifests.py
```

## Manifest Sync

SKILL.md frontmatter is the single source of truth.
All JSON manifests are generated from it:

```bash
# Regenerate all manifests
uv run scripts/sync-manifests.py

# Check for drift (used in CI)
uv run scripts/sync-manifests.py --check
```
