# Repository Guidelines

## Project Structure & Module Organization

This repository is a plugin marketplace for Claude Code and OpenAI Codex.
Primary content lives under `plugins/<plugin-name>/`. Each plugin contains
platform manifests in `.claude-plugin/` and `.codex-plugin/`, plus one skill at
`skills/<skill-name>/SKILL.md`. Optional supporting material belongs in
`references/`, `assets/`, or `scripts/` under that skill directory. Root-level
automation lives in `scripts/`, and CI is defined in
`.github/workflows/release-skills.yml`.

`SKILL.md` frontmatter is the source of truth. Do not hand-edit generated files
such as `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`,
or per-plugin `plugin.json` files.

## Build, Test, and Development Commands

There is no separate build step; contributors mainly regenerate and validate
manifests.

- `uv run scripts/sync-manifests.py`: regenerate marketplace and plugin JSON.
- `uv run scripts/sync-manifests.py --check`: fail if generated manifests drift.
- `uvx ruff check scripts/`: lint Python utility scripts.
- `uvx ruff format --check scripts/`: verify Python formatting.
- `python3 scripts/fix-markdown.py`: normalize common Markdown lint issues in
  plugin docs.
- `mado check README.md CLAUDE.md`: lint root documentation before submission.

## Coding Style & Naming Conventions

Use Python 3.11+ for repository scripts and standard 4-space indentation.
Prefer small, direct functions and type hints where they improve clarity.
Plugin and skill directory names should use kebab-case and align with the
`name:` value in `SKILL.md` frontmatter, for example `plugins/go-dev/`.

Keep Markdown concise, use fenced code blocks with languages, and wrap prose
near 80 characters to match the existing lint settings.

## Testing Guidelines

There is no dedicated unit-test suite yet. Treat validation as:
`sync-manifests.py --check`, Ruff checks for `scripts/`, and a review of any
generated JSON diffs. When adding a plugin, verify the release workflow can find
`plugins/<name>/skills/*/SKILL.md` and parse `version:` from frontmatter.

## Commit & Pull Request Guidelines

Recent history uses short, imperative commit subjects such as `Add skills`,
`Remove outdated CHANGELOG.md files`, and `Migrate workflows to Blacksmith`.
Follow that pattern and keep each commit scoped to one logical change.

Pull requests should describe the affected plugin(s), mention whether manifests
were regenerated, and include relevant command output for validation. Include
screenshots only when documentation visuals materially changed.
