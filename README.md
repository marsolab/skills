# Marsolab Skills

Portable agent skills for OpenAI Codex, Claude Code, and Cursor.

The stable registry is the `skills/` directory itself. Every entry is a
self-contained Agent Skill; this repository has no plugin manifests, generated
marketplace files, or platform-specific plugin registry.

## Install

Install every skill into all three agents with the open source Skills CLI:

```shell
npx skills add marsolab/skills \
  --skill '*' \
  -a codex -a claude-code -a cursor \
  --copy -y
```

To inspect the registry or install one skill:

```shell
npx skills add marsolab/skills --list
npx skills add marsolab/skills --skill golang -a codex
```

For a manual project installation, copy or symlink a complete skill directory
to the relevant location:

| Agent | Project skill directory |
| --- | --- |
| Codex | `.agents/skills/<name>/` |
| Claude Code | `.claude/skills/<name>/` |
| Cursor | `.agents/skills/<name>/` or `.cursor/skills/<name>/` |

Keep the whole directory together so references, scripts, assets, evaluations,
and optional agent metadata remain available.

## Registry

| Skill | Focus |
| --- | --- |
| [golang](skills/golang/SKILL.md) | Go development, testing, and tooling |
| [mactidy](skills/mactidy/SKILL.md) | Safe macOS agent-development cleanup |
| [sqlite](skills/sqlite/SKILL.md) | Production SQLite engineering |
| [things](skills/things/SKILL.md) | Capture tasks in Things 3 |

The `golang` skill contains the complete Go workflow in one portable directory.
Its entrypoint routes to topic folders under `references/`: development, style,
errors, concurrency, logging, testing, HTTP, CLI, SQL, and lint. Executable
helpers live under `scripts/lint/` and `scripts/testing/`, with the bundled
golangci-lint configuration under `assets/lint/`.

If an installation still contains the former individual Go skills, remove
those installed copies when switching to `golang` to avoid duplicate guidance.

## Registry Contract

Each registry entry has this shape:

```text
skills/<name>/
├── SKILL.md
├── agents/       # optional agent-specific presentation metadata
├── assets/       # optional
├── evals/        # optional
├── references/   # optional
└── scripts/      # optional
```

`SKILL.md` uses portable Agent Skills frontmatter. `name` and `description` are
required. A quoted semantic version lives under the string-valued `metadata`
map so the top-level schema stays portable:

```yaml
---
name: my-skill
description: Explain what the skill does and when an agent should use it.
metadata:
  version: "1.0.0"
---
```

The directory name must exactly match `name`. Use lowercase kebab-case, keep
relative links inside the skill directory, and avoid host-specific invocation
syntax in the skill instructions. Files such as `agents/openai.yaml` are
optional enhancements, not registry entries or wrappers.

## Contributing

Add or change the canonical files directly under `skills/`, then validate them:

```shell
uv run scripts/validate-skills.py
uvx ruff check scripts/
uvx ruff format --check scripts/
RUSTFLAGS="-Dwarnings" cargo clippy \
  --manifest-path skills/mactidy/scripts/mactidy-cli/Cargo.toml \
  --all-targets --all-features --locked
```

The release workflow validates every pull request. On `main`, a changed skill
can be packaged as a standalone archive and released under the tag
`<skill>-v<version>`; releases do not define the registry.

To recover missed releases, run **Validate and Release Skills** manually on
`main` with `skill_folder` set to `all` (the default) or a single skill name.
Existing version tags are skipped. Bump `metadata.version` before releasing a
skill whose packaged files have changed since its last release. Archives contain
only the committed files in that skill directory.
