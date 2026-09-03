# Mactidy CLI

Read this reference when building, invoking, testing, or extending the bundled
Rust utility. The source is dependency-free and lives at
`scripts/mactidy-cli/src/main.rs`.

## Build and install

For a repository-local validation build:

```bash
cargo test --manifest-path scripts/mactidy-cli/Cargo.toml
cargo build --release --manifest-path scripts/mactidy-cli/Cargo.toml
RUSTFLAGS="-Dwarnings" cargo clippy \
  --manifest-path scripts/mactidy-cli/Cargo.toml \
  --all-targets --all-features --locked
```

Cargo writes `target/` beside the manifest unless `CARGO_TARGET_DIR` points to
an explicit temporary directory. Do not leave that build output inside an
installed skill. For a compact single binary without Cargo build artifacts:

```bash
rustc --edition=2021 -O \
  scripts/mactidy-cli/src/main.rs \
  -o /approved/output/path/mactidy
```

Choose the output path with the user. Building or copying into
`~/.local/bin`, `~/.cargo/bin`, or another global location is an installation
and requires permission.

## Read-only audit

At least one explicit root is required:

```bash
mactidy audit \
  --root ~/Code \
  --root ~/.codex/worktrees \
  --repo ~/Code/project \
  --min-age-days 14 \
  --min-size-mib 50 \
  --json
```

Repeat `--root` and `--repo` as needed. A root controls artifact discovery; a
repo enables Git worktree inspection. The command does not auto-discover every
repository because doing so would create a broad, expensive scan.

The default text format is concise for humans. Prefer `--json` for agents and
automation. Its top-level fields are:

| Field | Meaning |
| --- | --- |
| `read_only` | Always `true` for audit output |
| `disk` | Data-volume total, used, available, and capacity values |
| `artifacts` | Allow-listed artifact kind, bytes, age, and canonical path |
| `processes` | Narrow PPID-1 and TTY-less process review candidates |
| `worktrees` | HEAD, branch, lock, dirty, upstream, and ahead evidence |
| `warnings` | Paths or repositories that could not be fully inspected |

Directory bytes are approximate. The scanner counts each hardlinked inode once
within a candidate, but APFS clones can still make logical size differ from
physical recovery. Worktree `clean`, `ahead`, and age are evidence, not an
automatic deletion decision. Process rows are review candidates and the CLI
has no process-kill command.

## Move an artifact to Trash

`trash` accepts only these exact directory names:

- dependencies: `node_modules`, `.venv`;
- caches: `.pytest_cache`, `__pycache__`;
- build output: `target`, `.next`, `.nuxt`, `.svelte-kit`, `.turbo`,
  `coverage`, `DerivedData`.

The exact artifact must resolve strictly below the exact cleanup root. The CLI
refuses system-wide roots, the home directory as a cleanup root, symlinks,
unknown names, open files, target drift, cross-volume copy/delete fallbacks,
and destination overwrite.

Interactive use prompts the operator to type the canonical path:

```bash
mactidy trash \
  --root /Users/me/Code/project \
  --path /Users/me/Code/project/node_modules
```

After the user approves the exact canonical target in the current
conversation, an agent may use non-interactive confirmation:

```bash
mactidy trash \
  --root /Users/me/Code/project \
  --path /Users/me/Code/project/node_modules \
  --confirm /Users/me/Code/project/node_modules
```

The artifact is renamed into `~/.Trash`; it is not permanently deleted. Space
is not physically reclaimed until Trash is emptied. Emptying Trash remains a
separate destructive action.

## Retire a linked worktree

Retirement requires an explicit retained ref:

```bash
mactidy retire-worktree \
  --repo /Users/me/Code/project \
  --path /Users/me/.codex/worktrees/example/project \
  --merged-into origin/main
```

The CLI requires the target to be a registered linked worktree, not the main
worktree; clean and unlocked; and already reachable from `--merged-into`. It
re-checks status, HEAD, and ancestry after confirmation, then runs ordinary
`git worktree remove` without `--force`. The ref choice remains a user or
repository-policy decision; do not invent `origin/main` when another retained
ref is authoritative.

## Exit behavior

- Exit `0`: the audit or exact requested operation completed.
- Exit `2`: invalid input, incomplete evidence, failed safety check, missing
  tool, or command failure.

Treat any warning or non-zero exit as incomplete cleanup. Do not retry with a
broader root, `sudo`, filesystem deletion, or force flags.
