---
name: mactidy
description: >-
  Audit macOS disk and memory pressure, and safely clean process, cache, and
  Git-worktree leftovers created by AI coding agents and development tools.
  Use when a Mac is low on
  space or memory, agent worktrees and build artifacts have accumulated, stale
  development processes or Docker stacks remain, or the user wants a recurring
  cleanup plan. Visualize audited usage and help the user choose what to remove.
  Do not use for general malware removal or indiscriminate system cleaning.
metadata:
  version: "1.3.0"
  tags: "macos, cleanup, disk-space, memory, worktrees, caches, processes, ai-agents"
---

# Mactidy

Reclaim macOS disk space and memory left behind by agentic development without
losing source code, uncommitted work, credentials, databases, or active agent
state. Treat cleanup as an evidence-backed operational change: inventory,
classify, visualize, choose, clean, then verify the physical result. Prefer the
bundled Rust CLI for repeatable inventory and guarded cleanup so the agent does
not reconstruct filesystem logic on every run.

## CLI first

Resolve bundled paths relative to this `SKILL.md`. If `mactidy` is already on
`PATH`, use it. Otherwise, build the dependency-free source to a user-approved
location; do not install it globally without permission:

```bash
rustc --edition=2021 -O \
  /absolute/path/to/mactidy/scripts/mactidy-cli/src/main.rs \
  -o /approved/output/path/mactidy
```

Use one structured audit to collect the routine evidence:

```bash
mactidy audit \
  --root ~/Code \
  --root ~/.codex/worktrees \
  --repo ~/Code/example \
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

Both prompt for the canonical path. Use `--confirm /canonical/path` only after
the user approves that exact target in the current conversation. Read
[references/cli.md](references/cli.md) when building, invoking, or extending
the CLI. If Rust is unavailable, `scripts/inventory.sh` remains a read-only
fallback for explicit roots.

## Safety contract

- Audit and visual review are the default. For a general cleanup request, show
  usage and verified candidates, then ask the user which targets to remove.
  Selecting chart marks or checking boxes only drafts a plan; it never deletes
  anything. Before mutation, match the user's explicit choice to exact targets.
  If an exact batch or a concrete operation such as `docker system prune` is
  already authorized, honor that scope without asking again, unless the user
  explicitly requires a new selection step. Permission for one operation does
  not authorize other targets or uncertain data.
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
  Trash is emptied. Direct permanent deletion needs approval that names the
  targets.
- Treat age, path names, PID 1, missing TTY, and large size only as clues. None
  proves that an artifact or process is disposable.

## Workflow

### 1. Establish scope and a baseline

Confirm the macOS host, the development roots and agent tools in scope, and
whether the user wants disk cleanup, memory cleanup, or both. Do not silently
scan unrelated user data.

Record user-protected paths and workloads for this audit, and exclude them from
all proposed cleanup/stop batches. Show those exclusions in the review; do not
persist new global protection settings without a separate request.

Record physical free space before cleanup:

```bash
df -h /System/Volumes/Data
```

On APFS, `du` is a useful per-path estimate but can double-count clones and
hardlinks. Do not promise that its total equals recoverable disk space.

### 2. Inventory without mutation

Run one CLI audit for the explicit roots and known repositories. Use the shell
fallback only when the CLI cannot be built. Then inspect only relevant systems
the CLI does not cover:

- Tool caches through their own status or cache-path commands.
- Docker or local VM storage only when those tools are in scope.
- Reported process candidates with per-PID inspection through `lsof`.
- Known temporary bundles only after identifying the owning application.

Read [references/candidate-catalog.md](references/candidate-catalog.md) for the
candidate type being investigated. Do not load or apply unrelated cleanup
recipes.

For Docker cleanup, read [references/docker.md](references/docker.md). It covers
local-context checks, Compose and BuildKit ownership, volume classification,
bounded prune operations, and host-space verification.

For memory usage or stale processes, read
[references/memory.md](references/memory.md). The disk CLI's detached-process
list is not a full RAM inventory. Use the bundled dependency-free, read-only
collector for pressure, VM statistics, swap, and top processes across owners:

```bash
python3 scripts/memory-audit.py --samples 3 --interval 10 --top 30
```

Resolve the script relative to this skill. This is bounded observation, not a
background monitor or process killer. Use `--jsonl` to receive each snapshot
immediately. Supplement Docker/container memory only when Docker is in scope.

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

For processes, capture PID, start time, executable, UID, parent, elapsed time,
cwd, open files, and listening ports. Inspect arguments only when needed and
redact secrets before displaying or storing them. A process is safe to stop
only when its purpose is known and no live task depends on it. High RSS, swap,
or low free RAM alone never authorizes stopping a process.

### 4. Visualize usage and ask what to remove

Read [references/visual-review.md](references/visual-review.md). Show a visual
overview of what occupies space, grouped by project or owning tool, with exact
targets available as details. Prefer an interactive diagram when grouping,
drill-down, or selecting several targets helps the decision; use a static chart
and table when interaction is unavailable or the batch is small. Keep physical
disk usage, logical candidate sizes, Docker accounting, and process memory in
separate views.

Show a compact table with one row per target or homogeneous batch:

| Target | Evidence | Approximate gain | Removal | Recovery | Risk |
| --- | --- | ---: | --- | --- | --- |

Separate high-confidence reproducible artifacts from uncertain items. Keep
uncertain items in the report rather than deleting them. State whether each
size is logical (`du`) or expected physical recovery (`df`).

For an audit or a general cleanup request, ask one concrete question in the
user's language, for example:
"Что удалить из проверенных кандидатов:
только кэши, кэши и выбранные сборки,
или ничего?" Map every offered choice to an exact list of targets and
operations. Let the user choose individual items or keep
everything. Stop before mutation until the user explicitly submits that choice;
no selection, a saved widget state, or elapsed time is not approval. For a batch
already authorized, show the review and proceed within that scope.

### 5. Clean in bounded batches

After approval, re-resolve each exact target and repeat the decisive safety
check. Then use the narrowest supported action:

- tool-native prune for shared stores and caches;
- `mactidy retire-worktree` for a clean worktree whose HEAD is already
  reachable from an explicitly chosen retained ref;
- `mactidy trash` for an allow-listed reproducible artifact below an exact
  cleanup root;
- `SIGTERM` for a verified stale process, followed by a bounded wait and
  re-check. Prefer the owning application's normal stop/quit operation first.
  Recheck PID plus start time/executable before signalling; stop on PID reuse,
  new dependencies, or restart by a supervisor. Escalation needs separate
  evidence and authorization covering its increased consequences.

Stop the batch on target drift, permission errors, an active owner, unexpected
contents, or a command that would broaden scope. Do not substitute `sudo`, a
different account, or a wider deletion. A tool's confirmation-only `--force`
flag may be used for an already authorized prune; never use force to bypass
dependency, dirty-worktree, or in-use checks.

### 6. Verify the outcome

After every batch:

1. Confirm the approved paths or PIDs are gone and unapproved ones remain.
1. Re-run the relevant worktree, cache, process, or application check.
1. Re-run `df -h /System/Volumes/Data` and report the actual physical change.
1. Smoke-test any application or development tool that owned the data.

Refresh the visual with measured before/after free space and completed,
retained, or skipped targets. Keep the original snapshot timestamp visible.

Report logical candidate size, physical space reclaimed, memory released, and
anything skipped as separate facts. A successful command alone is not proof
that cleanup helped or that the Mac remains healthy.

For memory actions, compare pressure, compressor occupancy, swap activity, and
remaining processes in fresh snapshots. Report the stopped processes' previous
RSS separately from observed host changes; shared pages and VM accounting mean
that RSS totals are not guaranteed reclaimed RAM.

## Prevention mode

When asked to keep the Mac tidy over time, first recommend low-risk habits:
non-watch test commands, explicit worktree retirement, bounded artifact
retention, and periodic read-only inventory. Install a `launchd` job or other
automatic deletion/kill policy only after the user reviews the exact script,
scope, interval, logs, and uninstall procedure. Scheduled audits are safer than
scheduled deletion.

Memory monitoring follows the same rule: bounded read-only samples first. Do
not install a persistent watcher, auto-killer, or RAM-purge schedule merely
because the user asks to improve memory awareness.

Read [references/cleanmymac-notes.md](references/cleanmymac-notes.md) only when
comparing cleanup design or evaluating ideas from CleanMyMac CLI. It records
the inspected public behavior and the limits of the available implementation
evidence; it is not authorization to install or run another cleanup tool.
