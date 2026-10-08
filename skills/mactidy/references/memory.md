# Memory pressure and unused processes

Use when the user asks about RAM, a slow Mac, memory monitoring, or stopping
unused development workloads. Keep this workflow separate from disk cleanup:
deleting caches does not by itself release a running process's memory.

## Bounded read-only monitoring

Run the bundled collector from its absolute skill path:

```bash
python3 scripts/memory-audit.py --samples 3 --interval 10 --top 30
```

It uses Python's standard library and query-only macOS commands. `--samples`
accepts 1–6 and `--interval` 1–10 seconds; there is no endless daemon or kill
mode. `--jsonl` prints one snapshot at a time. Store reports only in the current
task's local output directory. Missing/unsupported measurements are `null`
with warnings, not fabricated zeroes. Tests run with:

```bash
python3 -B scripts/test-memory-audit.py
```

Each snapshot records physical RAM, pressure observations, VM counters, swap,
and the largest processes, including their UID, parent, executable, start time,
elapsed time and RSS. It collects `comm`, not full process arguments or
environments. Its `needs_review` status is deliberate: no memory measurement
proves that a process is safe to stop.

The query sources are `sysctl -n hw.memsize`, `vm_stat`,
`sysctl -n vm.swapusage`, `sysctl -n kern.memorystatus_vm_pressure_level`,
`memory_pressure -Q`, and `ps`. `memory_pressure` without a verified query flag
is not a safe substitute: `-l`, `-p`, and `-S` can create/simulate pressure.
If `-Q` is unavailable, keep its measurement unknown rather than trying another
mode. Do not run `purge`, allocate RAM to force eviction, or remove swap files
as a default optimization.

## Interpret observations

Prefer sustained pressure and changing swap/pageout counters over a single low
free-memory reading. Inactive/file caches are managed by macOS and may be
reusable; their size alone is not a problem. Swap usage can remain after pressure
subsides. Compare samples before claiming an ongoing problem.

Read VM page size from `vm_stat`; do not hard-code 4 KiB or 16 KiB. Distinguish
physical compressor occupancy from the uncompressed pages stored in it. Several
VM counters overlap, and process RSS includes shared pages: do not add all of
them into a fake physical RAM total or estimate guaranteed recovery from summed
RSS. Keep raw pressure-level codes raw unless their mapping for this macOS
source is verified; the percentage printed by `memory_pressure` is not an
Activity Monitor pressure grade.

For Docker, use `docker stats --no-stream` on the verified local context. Show
container memory separately from the Docker/OrbStack VM's host RSS: summing both
counts the same workload twice. Do not stop the VM if retained containers or
Linux machines depend on it. Group application helpers only when executable
bundle paths or parent links establish their owner; call any RSS sum a reported
process-family estimate, not unique physical memory.

## Establish stoppable targets

For each candidate, gather the exact `(PID, start time, executable, UID)` and
inspect only what is needed:

```bash
ps -p EXACT_PID -o pid=,ppid=,uid=,lstart=,etime=,rss=,comm=
lsof -a -p EXACT_PID -d cwd
lsof -nP -a -p EXACT_PID -i
```

Check its known task, working directory, open files, external clients, child
processes, and owning app/tool or supervisor. A missing worktree and absent
clients support investigation, but do not alone prove that a server is unused.
Consider upcoming/ongoing tests, previews, queued builds, and saved app state.

Protect system processes, other users' processes, the active agent and its
ancestors/MCP/tool servers, live editors, builds, tests, simulators, database
services, and apps with unsaved work. Do not kill `kernel_task`, `launchd`, or
`WindowServer`. An old process, PPID 1, no TTY, low CPU, or large RSS is a clue,
not a cleanup decision. If ownership or dependencies are uncertain, keep it as
`needs_review`; ask to investigate rather than offering termination.

Known abandoned development servers or completed test/build workers can become
`verified` only after checking their original task and current dependencies.
Mark which normal stop/restart operation is available and what stopping would
interrupt. A stop action is separate from deleting the process's files, app
state, containers, or volumes.

## Visual selection, stop, and verify

Include a separate memory view in [visual-review.md](visual-review.md): pressure
and swap over the captured interval, then ranked process-family/PID bars in
MiB/GiB. Show each candidate's owner, previous RSS, CPU observation, status,
purpose, restart method, and proposed stop effect. Label the action
"Остановить процесс", not "Удалить".
Verified stop candidates start unchecked; protected and unknown workloads are
not selectable for termination.

For a general request, ask which verified workloads to stop. Existing exact
authorization is sufficient, but a request to delete files does not imply
permission to close apps. Immediately before stopping, repeat identity and
dependency checks and ensure it is not the active agent's process tree.

Prefer the tool's normal shutdown: Compose/buildx stop for its exact workload,
the dev server's control channel, or an app's normal quit when losing unsaved
work is ruled out. Otherwise send `SIGTERM` to the exact verified PID and wait
briefly while communicating progress. Never signal a process group, use broad
`pkill`/`killall`, or escalate to `SIGKILL` based only on timeout. If it respawns,
identify its supervisor instead of repeatedly killing children; changing a
launch agent/service policy is a distinct action.

Confirm target exit, expected port closure, preserved parent/child workloads,
and health of retained services. Capture 2–3 fresh memory snapshots. Report the
before/after observations and the stopped workload's previous RSS separately.
Do not promise that swap disappears immediately or that a one-time snapshot
proves performance improved. Schedule only read-only monitoring when the user
explicitly asks and has reviewed scope, interval, logs, and uninstall steps.
