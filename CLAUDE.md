# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Repository Purpose

This is a portable Agent Skills registry for OpenAI Codex, Claude Code, and
Cursor. The canonical registry is the set of directories under `skills/`.
There are no generated manifests or secondary registries to synchronize.

## Commands

```shell
# Validate the registry layout, frontmatter, versions, and local links
uv run scripts/validate-skills.py

# Check Python utilities
uvx ruff check scripts/
uvx ruff format --check scripts/

# Check root Markdown when mado is available
mado check README.md CLAUDE.md AGENTS.md

# Confirm that a standard installer discovers the registry
npx skills add . --list
```

## Architecture

Every registry entry lives at `skills/<name>/SKILL.md`. Optional supporting
files stay inside the same skill directory:

- `references/` for material loaded only when needed
- `scripts/` for executable helpers
- `assets/` for templates and other output resources
- `evals/` for evaluation cases
- `agents/openai.yaml` for optional Codex presentation metadata

Agent-specific metadata is an enhancement to a skill, not a wrapper or a
separate registry entry. Do not add marketplace JSON, generated manifests, or a
second canonical catalog.

## Frontmatter Contract

Use portable Agent Skills fields. `name` and `description` are required. Keep
the stable semantic version under `metadata.version`:

```yaml
---
name: example-skill
description: Explain what the skill does and when to use it.
metadata:
  version: "1.0.0"
---
```

The skill directory and `name` must match exactly. Names use lowercase
kebab-case. Keep metadata keys and values as strings, descriptions below 1024
characters, and relative links within the skill directory.

## Adding or Updating a Skill

1. Create or edit `skills/<name>/` directly.
1. Keep `SKILL.md` focused and place detailed material in supporting files.
1. Run the validation and lint commands above.
1. If behavior changed, update evaluations where the skill has them.
1. Bump `metadata.version` when the published skill contract changes.

## CI and Releases

Pull requests validate the entire registry. Pushes to `main` also detect changed
skill directories and package each selected skill with that directory as the
archive's single top-level entry. Release tags use `<skill>-v<version>`.
GitHub releases are distribution artifacts; `skills/` remains the registry.

## Conventions

- Preserve existing content outside the skill being changed.
- Use relative paths that resolve from the skill directory.
- Describe optional helpers explicitly; do not rely on one host's automatic
  hooks, commands, or namespaced invocation syntax.
- Use POSIX-compatible shell where practical. If Bash is required, declare it
  explicitly and avoid features unavailable in macOS Bash 3.2.
