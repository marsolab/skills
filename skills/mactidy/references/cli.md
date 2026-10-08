# Mactidy CLI

Read this reference when building, invoking, testing, or extending the bundled
Rust utility. The source is dependency-free and lives at
`scripts/mactidy-cli/src/main.rs`.

## Build and install

The project directory is named `mactidy-cli`; its executable is `mactidy`.
Before either skill mode, check `command -v mactidy`, then the executable at
`~/.local/bin/mactidy`. Run the resolved executable's `help` and confirm it
supports `audit`, `trash`, and `retire-worktree`. Reuse a working installation.
Preserve and report an incompatible or broken executable rather than replace
it automatically.

If absent, install the bundled source to the user-owned `~/.local/bin` without
a separate confirmation. Set `MACTIDY_SKILL_DIR` to the resolved directory
containing this skill's `SKILL.md`; no repository checkout is required. With
`rustc` available, build and verify in a temporary directory before installing:

```bash
MACTIDY_SKILL_DIR="/absolute/path/to/installed/mactidy"
MACTIDY_BIN="$HOME/.local/bin/mactidy"
MACTIDY_BUILD_DIR=$(mktemp -d "${TMPDIR:-/tmp}/mactidy-build.XXXXXX") || exit 1
rustc --edition=2021 -O \
  "$MACTIDY_SKILL_DIR/scripts/mactidy-cli/src/main.rs" \
  -o "$MACTIDY_BUILD_DIR/mactidy" &&
  "$MACTIDY_BUILD_DIR/mactidy" help &&
  mkdir -p "$HOME/.local/bin" &&
  install -m 755 "$MACTIDY_BUILD_DIR/mactidy" "$MACTIDY_BIN" &&
  "$MACTIDY_BIN" help
```

If Cargo is available but `rustc` is not on `PATH`, build with it instead:

```bash
cargo build --release --locked \
  --manifest-path "$MACTIDY_SKILL_DIR/scripts/mactidy-cli/Cargo.toml" \
  --target-dir "$MACTIDY_BUILD_DIR/target"
```

Verify `"$MACTIDY_BUILD_DIR/target/release/mactidy" help` and install that
executable to the same destination. Remove only the temporary build directory
created for this setup after verification.

Use `"$MACTIDY_BIN"` for subsequent commands if `~/.local/bin` is not on `PATH`.
Do not change shell startup files, use `sudo`, overwrite another executable,
or download an unrelated package with a similar name. If neither compiler is
available or installation fails, report the missing prerequisite or error;
the shell inventory fallback produces only a partial read-only report.

For a repository-local validation build:

```bash
cargo test --manifest-path scripts/mactidy-cli/Cargo.toml
cargo build --release --manifest-path scripts/mactidy-cli/Cargo.toml
RUSTFLAGS="-Dwarnings" cargo clippy \
  --manifest-path scripts/mactidy-cli/Cargo.toml \
  --all-targets --all-features --locked
```

Cargo writes `target/` beside the manifest unless `CARGO_TARGET_DIR` or
`--target-dir` points to an explicit temporary directory. Do not leave that
build output inside an installed skill.

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

The example filters out small or recent artifacts. For a complete scoped
inventory in `/mactidy inspect` or `/mactidy tidy`, use `--min-age-days 0` and
`--min-size-mib 0` instead. These thresholds affect discovery, not cleanup
authorization.

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

For a verified canonical target covered by the user's cleanup authorization
(including `/mactidy tidy` within scope), an agent may use non-interactive
confirmation. `/mactidy inspect` never authorizes this operation:

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

An agent may pass `--confirm /canonical/worktree/path` after proving the exact
target is disposable and covered by the user's authorization. The skill's
`tidy` mode can supply that authorization; `inspect` cannot.

## Exit behavior

- Exit `0`: the audit or exact requested operation completed.
- Exit `2`: invalid input, incomplete evidence, failed safety check, missing
  tool, or command failure.

Treat any warning or non-zero exit as incomplete cleanup. Do not retry with a
broader root, `sudo`, filesystem deletion, or force flags.
