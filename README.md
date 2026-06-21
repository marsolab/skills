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
| [front-dev][3] | Development | Modern web apps |
| [go-dev][4] | Development | Go umbrella; routes to go-* siblings |
| [go-style][5] | Development | Idiomatic Go: naming, generics, interfaces |
| [go-errors][6] | Development | Error wrapping, errors.Join, panic discipline |
| [go-concurrency][7] | Development | Goroutines, channels, context, errgroup |
| [go-logging][8] | Development | Structured logging with log/slog |
| [go-testing][9] | Development | Table-driven tests, helpers, integration gating |
| [go-http][10] | Development | HTTP services with Chi router |
| [go-cli][11] | Development | CLI tools with the stdlib flag package |
| [go-sql][12] | Development | sqlc + goose migrations |
| [go-lint][13] | Development | golangci-lint config and tooling |
| [landing-page-breakdown][14] | Design | Page analysis |
| [multi-agent-config][15] | DevOps | Multi-agent configs |
| [sys-arch][16] | Architecture | System design |
| [things][17] | Productivity | Capture tasks into Things 3 |
| [use-browser][18] | Development | Browser automation, default Lightpanda |

[1]: plugins/apple-dev/skills/apple-dev/SKILL.md
[2]: plugins/copy/skills/copy/SKILL.md
[3]: plugins/front-dev/skills/front-dev/SKILL.md
[4]: plugins/go-dev/skills/go-dev/SKILL.md
[5]: plugins/go-style/skills/go-style/SKILL.md
[6]: plugins/go-errors/skills/go-errors/SKILL.md
[7]: plugins/go-concurrency/skills/go-concurrency/SKILL.md
[8]: plugins/go-logging/skills/go-logging/SKILL.md
[9]: plugins/go-testing/skills/go-testing/SKILL.md
[10]: plugins/go-http/skills/go-http/SKILL.md
[11]: plugins/go-cli/skills/go-cli/SKILL.md
[12]: plugins/go-sql/skills/go-sql/SKILL.md
[13]: plugins/go-lint/skills/go-lint/SKILL.md
[14]: plugins/landing-page-breakdown/skills/landing-page-breakdown/SKILL.md
[15]: plugins/multi-agent-config/skills/multi-agent-config/SKILL.md
[16]: plugins/sys-arch/skills/sys-arch/SKILL.md
[17]: plugins/things/skills/things/SKILL.md
[18]: plugins/use-browser/skills/use-browser/SKILL.md

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
