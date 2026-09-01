# Cleanup Candidate Catalog

Read only the section that matches the current cleanup target. Commands shown
here are discovery or supported cleanup entry points; they are not permission
to mutate the machine.

## Git worktrees and agent checkouts

Agent-created worktrees can contain unique commits or files even when their
task looks finished. Discover them from the repository rather than assuming a
tool-specific directory layout:

```bash
git -C /path/to/repo worktree list --porcelain
git -C /path/to/worktree status --short --branch
git -C /path/to/worktree ls-files --others --exclude-standard
git -C /path/to/worktree log --oneline '@{upstream}..HEAD'
```

An absent upstream is a finding, not permission to remove the worktree. Check
whether its branch or detached commit is reachable from a retained ref. Remove
only an approved clean worktree:

```bash
git -C /path/to/repo worktree remove /exact/worktree/path
git -C /path/to/repo worktree prune --dry-run
```

Run metadata pruning separately and only after the path state is understood.
Do not remove a worktree directory directly or use `--force` to hide dirty or
locked state.

## Reproducible dependencies and build output

Common candidates include `node_modules`, `.venv`, `target`, `.next`, `.nuxt`,
`.svelte-kit`, `.turbo`, `coverage`, `.pytest_cache`, `__pycache__`, and Xcode
Derived Data. A familiar name alone is insufficient: verify the surrounding
project manifest, lockfile, and build tool, and confirm no live process has its
cwd or open files there.

Treat generic names such as `build`, `dist`, `out`, `cache`, `data`, and
`artifacts` as ambiguous. They may contain source assets, release packages, or
customer data. Do not include them in bulk deletion without project-specific
proof.

Prefer deleting a dependency directory over changing a repository's package
manager. Migration between npm, pnpm, Yarn, or Bun changes source and CI and is
a separate engineering task.

## Package stores and download caches

First ask the installed tool for the active cache or store path. Do not assume
the default path and do not delete a shared store by hand.

For pnpm, inspect the current shared store and use its supported prune command
only after approval:

```bash
pnpm store path
pnpm store prune
```

The store may serve many projects and worktrees. Record `df` before and after;
hardlinks make per-directory `du` totals misleading. For npm, Yarn, Bun,
Homebrew, language toolchains, and browser automation packages, inspect the
installed version's help and use its official verify, clean, or prune command.
Avoid a generic `rm -rf` against a cache root.

## Agent and browser temporary bundles

AI browser automation can leave temporary profiles, browser downloads, and
macOS code-sign clone bundles. One known pattern is
`com.google.Chrome.code_sign_clone` below `/private/var/folders`, but the path
must be rediscovered on the current host:

```bash
find /private/var/folders -type d \
  -name com.google.Chrome.code_sign_clone -prune -print 2>/dev/null
```

Before removal, close the owning browser and automation sessions, verify no
matching process or open file remains, and approve the exact discovered roots.
These APFS clones can have a large logical `du` size but a much smaller physical
effect. Measure recovery with `df -h /System/Volumes/Data`.

Do not treat the contents of `~/.codex`, `~/.claude`, Cursor application data,
or browser profiles as disposable caches. They may include credentials,
history, configuration, session recovery, or active task state. Clean only a
documented subdirectory whose ownership and rebuild behavior are known.

## Processes and listeners

Start with a review list, not a killer heuristic:

```bash
ps -axo pid=,ppid=,tty=,etime=,rss=,command=
lsof -a -p <pid> -d cwd
lsof -nP -a -p <pid> -i
```

PPID 1, no TTY, an old elapsed time, or a command containing `node`, `bun`,
`deno`, `vite`, `playwright`, `claude`, `cursor`, or `codex` can help locate a
candidate. None proves it is orphaned. Check the associated task, cwd, open
files, ports, and logs.

After approval, send `SIGTERM` to the exact PID, wait briefly, and verify it has
exited. Before escalating, verify the PID still represents the same command to
avoid PID-reuse mistakes. Never install a broad automatic process killer by
default; long-running agents, MCP servers, indexers, and local databases often
look idle while remaining intentional.

## Docker, virtual machines, and simulators

Use the owning tool's inventory first, such as `docker system df`, before
proposing cleanup. Images and stopped containers may be reproducible; named or
anonymous volumes can hold the only copy of databases. Never include volumes
in a general prune batch.

For Apple simulators, identify unavailable devices and inspect runtime usage
with the installed Xcode tools. Simulator deletion, runtime removal, archives,
and signing assets are separate actions with different recovery costs. Do not
delete Xcode Archives, provisioning profiles, certificates, or device support
data merely because they are old.

## Logs and retention

Logs are useful only after identifying their owner, retention policy, and
active file handles. Prefer application-native rotation or a size-and-age cap.
Never truncate a log being used to diagnose the current task, and never delete
crash reports, audit evidence, or session transcripts solely by age.

For persistent maintenance, keep a record of:

- roots included and excluded;
- minimum age and size thresholds;
- exact candidate types;
- dry-run output and log location;
- stop conditions and uninstall steps.

Automate inventory first. Automatic mutation requires a separately reviewed,
reversible policy with narrow targets.
