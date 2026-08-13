# Repository Guidelines

## Project Structure

This repository is a portable Agent Skills registry for OpenAI Codex, Claude
Code, and Cursor. The only registry is the directory tree under `skills/`:

```text
skills/<name>/
├── SKILL.md
├── agents/       # optional agent-specific presentation metadata
├── assets/       # optional
├── evals/        # optional
├── references/   # optional
└── scripts/      # optional
```

Do not add plugin wrappers, marketplace JSON, generated manifests, or another
canonical catalog. Root automation belongs in `scripts/`; CI lives in
`.github/workflows/release-skills.yml`.

## Build and Validation Commands

There is no build step. Validate and lint the canonical files directly:

- `uv run scripts/validate-skills.py`: validate registry layout, frontmatter,
  versions, portability constraints, and relative links.
- `uvx ruff check scripts/`: lint Python utilities.
- `uvx ruff format --check scripts/`: verify Python formatting.
- `mado check README.md CLAUDE.md AGENTS.md`: lint root documentation when mado
  is available.
- `npx skills add . --list`: confirm standard installer discovery.

## Skill and Code Conventions

The directory name must exactly match the `name` in `SKILL.md`. Use lowercase
kebab-case. Portable frontmatter requires `name` and `description`; keep the
quoted semantic version at `metadata.version`. Metadata keys and values are
strings.

Descriptions state both capability and trigger conditions. Keep detailed or
rarely needed material in `references/`, and refer to supporting files with
paths relative to the skill directory. Do not depend on host-only command
aliases, automatic hooks, or namespaced skill identifiers.

Use Python 3.11+ for root utilities, four-space indentation, and type hints where
they improve clarity. Keep Markdown concise, use fenced code blocks with
languages, and wrap prose near 80 characters.

## Testing Guidelines

Run the registry validator after every structural or frontmatter change. When a
skill contains executable helpers, also run the relevant syntax or focused
behavior checks. When a skill has evaluations, update and review them alongside
behavior changes. Confirm that external discovery still lists every expected
skill after changing the registry layout.

## CI and Releases

Pull requests validate the complete registry. On `main`, the release workflow
detects changed `skills/<name>/` directories, reads `metadata.version`, and can
publish a standalone archive tagged `<skill>-v<version>`. The skill directory is
the archive's sole top-level entry. Releases are distribution artifacts and are
not a registry.

## Commit and Pull Request Guidelines

Use short, imperative commit subjects and keep each commit scoped to one logical
change. Pull requests should name the affected skills, explain any version bump,
and include the relevant validation output. Preserve unrelated worktree changes.
