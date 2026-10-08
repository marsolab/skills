---
name: mactidy
description: >-
  Audit and safely clean macOS disk, process, cache, and Git-worktree leftovers
  created by AI coding agents and development tools. Use when a Mac is low on
  space or memory, agent worktrees and build artifacts have accumulated, stale
  development processes remain, the user invokes /mactidy tidy or
  /mactidy inspect, or the user wants a recurring cleanup plan.
  Do not use for general malware removal or indiscriminate system cleaning.
metadata:
  version: "1.2.0"
  tags: "macos, cleanup, disk-space, worktrees, caches, processes, ai-agents"
---

# Mactidy

Reclaim macOS disk space and memory left behind by agentic development without
losing source code, uncommitted work, credentials, databases, or active agent
state. Treat cleanup as an evidence-backed operational change: inventory,
classify, check authorization, clean, then verify the physical result. Use the
bundled Rust CLI for repeatable inventory and guarded cleanup so the agent
does not reconstruct filesystem logic on every run.

## Commands

Treat these slash commands as skill requests. Accept `$mactidy tidy` and
`$mactidy inspect` with the same behavior on hosts that use dollar invocation.
These modes route the workflow; they are not executable CLI subcommands.

| Command | Behavior |
| --- | --- |
| `/mactidy tidy` | Inventory and clean all proven disposable development leftovers within the established scope, then verify disk and memory changes. |
| `/mactidy inspect` | Show what can be cleaned, its occupied space, cleanup method, recovery, and risk. Do not delete files, prune stores, retire worktrees, or signal processes. |

Both modes check for the CLI, install it if missing, and use it as described
below. A bare Mactidy invocation defaults to `inspect` unless the user has
already requested cleanup.

For `inspect`, report total Data-volume usage and free space, candidate paths
and sizes, totals by category, and uncertain or active items that must be kept.
Separate logical candidate bytes from estimated physical recovery; show
process RSS separately from disk space. Finish with the available cleanup plan.

For `tidy`, the command authorizes cleanup of proven disposable items within
the established development scope. Present the concrete plan, then carry out
authorized batches without asking the user to approve the same scope again.
Keep uncertain items and request approval only for actions beyond that scope,
such as deleting unique data, emptying Trash, or adding persistent automation.
"All" means all verified candidates in scope, not every large or old file on
the Mac. Installation alone does not authorize cleanup in `inspect` mode.

## CLI first

The bundled `mactidy-cli` project installs an executable named `mactidy`.
Resolve bundled paths relative to this `SKILL.md`. Check `command -v mactidy`,
then `~/.local/bin/mactidy` if it is not on `PATH`. Verify the executable with
`help` and use it for the requested workflow.

If missing, install the bundled source to `~/.local/bin/mactidy` automatically
using [references/cli.md](references/cli.md). CLI setup is part of both modes;
it does not need a separate confirmation. Use the resolved executable path
directly if its directory is absent from `PATH`; do not edit shell profiles or
use `sudo`. If an existing executable fails verification, preserve it and
report the conflict rather than overwrite it.

Use one structured audit to collect the routine evidence:

```bash
mactidy audit \
  --root ~/Code \
  --root ~/.codex/worktrees \
  --repo ~/Code/example \
  --min-age-days 0 \
  --min-size-mib 0 \
  --json
```

The CLI scans only explicit roots, deduplicates hardlinked files while
estimating size, inventories Git worktree safety state, reports narrowly
matched detached development processes, and records Data-volume free space. It
never signals a process. Its two mutation commands have no force or permanent
delete mode:

```bash
mactidy trash --root /exact/root --path /exact/artifact
mactidy retire-worktree \
  --repo /exact/repo \
  --path /exact/worktree \
  --merged-into origin/main
```

Both prompt for the canonical path. Use `--confirm /canonical/path` only for a
verified target covered by the user's cleanup authorization, including `tidy`.
Read [references/cli.md](references/cli.md) when building, invoking, or extending
the CLI. If installation is blocked by a missing Rust toolchain or permissions,
report the blocker and use `scripts/inventory.sh` only as a partial read-only
fallback for explicit roots. Do not claim that the CLI was installed or that
cleanup completed.

## Safety contract

- Audit is the default. Before any deletion, process signal, package-store
  prune, worktree removal, Docker prune, or persistent automation, show the
  exact targets and check the user's existing authorization. `tidy` covers
  proven disposable development leftovers in scope; obtain approval when a
  proposed action goes beyond that authorization. `inspect` authorizes CLI
  setup and read-only inspection only.
- Never delete source, `.git`, untracked or unpushed work, credentials, agent
  history, session state, databases, Docker volumes, signing material, or
  system-managed files merely because they are large or old.
- Never run recursive deletion against `/`, a home directory, a workspace
  root, an unresolved variable, command substitution, wildcard, or broad
  `find` result. Resolve and re-check every target immediately before acting.
- Do not rewrite lockfiles, CI, package-manager choice, global instructions, or
  application settings as a side effect of cleanup. Offer such changes as a
  separate task when they would prevent recurrence.
- Prefer application- or tool-owned cleanup commands. Use Trash when recovery
  matters and the size is practical; explain that space is not reclaimed until
  Trash is emptied. Emptying Trash or permanently deleting uncertain data needs
  approval that names the targets.
- Treat age, path names, PID 1, missing TTY, and large size only as clues. None
  proves that an artifact or process is disposable.

## Workflow

### 1. Establish scope and a baseline

Establish the macOS host, development roots and agent tools from the request
and available context. `tidy` covers disk and memory cleanup; `inspect` covers
both inventories. Ask about scope only when it cannot be established from
context. Do not silently scan unrelated user data.

Record physical free space before cleanup:

```bash
df -h /System/Volumes/Data
```

On APFS, `du` is a useful per-path estimate but can double-count clones and
hardlinks. Do not promise that its total equals recoverable disk space.

### 2. Inventory without mutation

Run one CLI audit for the explicit roots and known repositories. For a complete
scoped inventory in either command mode, pass `--min-age-days 0` and
`--min-size-mib 0`; the default filters would omit recent or small candidates.
If the user requests filters, include them in the report. Neither age nor size
authorizes removal. Use the shell fallback only when the CLI cannot be
installed. Then inspect only relevant systems the CLI does not cover:

- Tool caches through their own status or cache-path commands.
- Docker or local VM storage only when those tools are in scope.
- Reported process candidates with per-PID inspection through `lsof`.
- Known temporary bundles only after identifying the owning application.

Read [references/candidate-catalog.md](references/candidate-catalog.md) for the
candidate type being investigated. Do not load or apply unrelated cleanup
recipes.

### 3. Prove each candidate is disposable

For every candidate, establish all applicable facts:

- the exact canonical path or PID;
- approximate size or resident memory and last activity;
- which tool created it and whether that tool is currently running;
- whether it contains unique, dirty, untracked, unpushed, or credential data;
- the supported removal method and how it can be restored or rebuilt;
- dependencies, open files, listeners, mounts, and owning processes.

For worktrees, check status, untracked files, upstream divergence, and the
repository's current worktree registry. Remove through `git worktree remove`,
not filesystem deletion. Never use `--force` to bypass unexplained state.

For processes, capture PID, parent, elapsed time, full command, cwd, open files,
and listening ports. A process is safe to stop only when its purpose is known
and no live task depends on it.

### 4. Present the cleanup plan

Show a compact table with one row per target or homogeneous batch:

| Target | Evidence | Approximate gain | Removal | Recovery | Risk |
| --- | --- | ---: | --- | --- | --- |

Separate high-confidence reproducible artifacts from uncertain items. Keep
uncertain items in the report rather than deleting them. State whether each
size is logical (`du`) or expected physical recovery (`df`).

In `inspect` mode, stop after reporting this plan. In `tidy` mode, proceed with
proven candidates covered by the command's authorization. Request approval
only for additional actions that need it.

### 5. Clean in bounded batches

For each authorized batch, re-resolve each exact target and repeat the decisive
safety check. Then use the narrowest supported action:

- tool-native prune for shared stores and caches;
- `mactidy retire-worktree` for a clean worktree whose HEAD is already
  reachable from an explicitly chosen retained ref;
- `mactidy trash` for an allow-listed reproducible artifact below an exact
  cleanup root;
- `SIGTERM` for a verified stale process, followed by a bounded wait and
  re-check. Escalate only with separate evidence that the same PID survived.

Stop the batch on target drift, permission errors, an active owner, unexpected
contents, or a command that would broaden scope. Do not substitute `sudo`,
`--force`, a different account, or a wider deletion.

### 6. Verify the outcome

After every batch:

1. Confirm the approved paths or PIDs are gone and unapproved ones remain.
1. Re-run the relevant worktree, cache, process, or application check.
1. Re-run `df -h /System/Volumes/Data` and report the actual physical change.
1. Smoke-test any application or development tool that owned the data.

Report logical candidate size, physical space reclaimed, memory released, and
anything skipped as separate facts. A successful command alone is not proof
that cleanup helped or that the Mac remains healthy.

## Prevention mode

When asked to keep the Mac tidy over time, first recommend low-risk habits:
non-watch test commands, explicit worktree retirement, bounded artifact
retention, and periodic read-only inventory. Install a `launchd` job or other
automatic deletion/kill policy only after the user reviews the exact script,
scope, interval, logs, and uninstall procedure. Scheduled audits are safer than
scheduled deletion.
