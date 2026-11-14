# Rex workers

## Discover the environment

Load the installed `rex` skill and execute `rex __internal skill`; if that
version lacks the guide, use `rex whoami --json` and command help. Follow the
installed guide over cached examples. If `rex` is absent from PATH, check
`REX_BIN_DIR` or the installed application bundle without changing shell
configuration. Locate any bundled executable from the actual installed
application; paths and app names vary. Prefer the executable matching the active
server.

Use the explicit user target, otherwise the session where the skill was
invoked, identified by inherited `REX_SESSION`/`REX_BLOCK` or startup context.
Validate full IDs with `rex session inspect` and `rex block inspect`. Capture
that session and pane as the protected coordinator location; do not replace
it with whichever session the app happens to display later.

If IDs are missing or stale, inspect `rex whoami --json` and `rex ls --json`,
then inspect candidate metadata to resolve the invoking session. A stale block
with a valid session needs a new tab in that session, not a new session. Do not
choose a target from focus, a generated label, or a shared working directory
alone. If the invocation is known to be inside Rex but its session cannot be
resolved, report that routing blocker rather than creating another session.
Only create a dedicated session when running outside Rex with no resolvable
invoking session, or when the user explicitly requests a new session. An
explicit but ambiguous target needs clarification. Remote hosts require an
explicit target and their own paths, tools, and authorization.

Before dispatch, record the invoking session/pane and existing window/block IDs
as the baseline. Record every task-created session, window, and block ID as it
is returned, including starter shells and failed launches. Track cleanup
ownership separately: using an existing session does not make it task-owned.
Pass the selected full session ID explicitly with `-s` on every tab, split,
observation, and pane/tab cleanup command. Do not rely on focus or tab positions.

Discover agent executables with `command -v`. Inspect version/help and only the
necessary non-secret authentication/model status. Installed does not mean
authenticated, model-accessible, or ready. Keep account details and tokens out
of prompts and logs. Use supported status commands; report unknown readiness
rather than launching a billable probe solely to test credentials.

## Provider adapters and reasoning

These are discovery starting points, not frozen launch recipes. Recheck
installed help before use, including prompt input, working directory, output
format, permissions, model selection, effort, and resume behavior.

| Harness | Discovery | Selection guidance |
| --- | --- | --- |
| Codex CLI | `codex --help`, `codex exec --help` | `--model` selects a model. Verify the installed configuration schema or current official docs for reasoning configuration and accepted values. ChatGPT account availability does not prove CLI authentication. |
| Claude Code | `claude --help` | Verify `--model`, `--effort`, print mode, and supported budget controls. Model-specific effort support can differ from the CLI's accepted syntax. |
| Hermes | `hermes --help`, `hermes chat --help` | Verify model/provider and single-query options. Discover reasoning controls for the chosen backend; avoid changing global defaults. |
| OpenCode | `opencode --help`, `opencode run --help`, `opencode models` | Verify provider/model IDs and any model variant controls. OpenCode is a harness, not a model family. |
| Cursor Agent | `agent --help`, `agent models` | Confirm this binary identifies itself as Cursor Agent. `cursor` may be the editor launcher. Verify model IDs and any supported effort overrides. |
| Other agents | Executable help and primary documentation | Add only when available, authorized, and useful; follow the same dispatch contract. |

Use current model listings and official documentation when needed. Never invent
IDs, assume a vendor's universal superiority, or pass a generic reasoning flag
to every CLI. Treat effort levels as provider/model-specific. If no supported
control exists, record `default / not configurable`; a prompt asking for careful
reasoning is not an actual runtime setting.

Routine extraction, bounded edits, and straightforward checks usually suit a
fast model with low/default effort. Multi-file implementation and synthesis
usually need a capable general model with moderate effort. Ambiguous
architecture, elusive failures, and consequential review justify a stronger
model with high effort. Escalate based on observed failure or risk. Honor
user-selected providers/models and explicit budgets. Prefer an already
authorized account; ask before new subscriptions, installation, credential
changes, or a material unapproved cost increase.

## Avoid empty starter tabs

Prepare the first worker command before opening a tab. In the invoking session,
use `rex window new -s "$task_session"` with the command as shown below; do not
use `rex new` for ordinary worker dispatch. Launch useful work immediately,
without a placeholder shell. Record the returned window and new block IDs, then
split that worker pane for related agents. A distinct workstream still belongs
in another tab of this session, not in a separate session.

For the dedicated-session exception above, use
`rex new TASK --window WORKSTREAM -c WORKDIR --keep-open --json -- COMMAND ARGS`
with verified arguments. Record its full session, window, and block IDs and mark
the session as task-created. Session creation alone is not a successful launch.

If a task-owned session was already created with a default shell, inspect its
process and capture first. Reuse that confirmed idle starter shell for the first
worker through the installed Rex guide's send/send-key mechanism, or launch a
worker split and close the unused starter block after verifying the launch.
Do not leave a generic Runtime/Terminal tab solely as a placeholder or anchor.
A tab label or an empty-looking screen alone does not prove it is unused.

On launch failure and task completion, reconcile all recorded task-owned blocks
and windows, including starter shells, rather than only registered workers.
After saving evidence and stopping descendants, remove unused starter panes and
completed worker panes. If a dedicated session created by this task contains no
needed work, close its remaining task-owned windows/session too, after checking
that no user or other agent has added work. Preserve the coordinator's own
session and unrelated resources. Do not keep a shell alive just to preserve a
split anchor; discover a live anchor or create a useful worker when needed.

## Group panes and clean up finished workers

Treat a Rex window as a tab and a block as a pane (panel). Open one worker tab
in the invoking session, with several related worker panes. Inspect its layout
and split an existing task pane with `rex split`, using its full block ID.
Choose right/below placement and proportions to keep active agents readable. Keep the user's focus with
`--focus=false`. Create a new tab only for a distinct workstream or when further
splits would make the current tab impractical; do not create one tab per agent
by default. Native subagents remain within their parent agent unless the
platform itself requires another surface.

Record the task tab and worker block IDs. When the pane used as a split anchor
is closed, inspect the remaining layout and choose a live task pane before the
next dispatch. If none remains, launch useful work in a new tab in the same
session. Keep the coordinator's pane available.

As each worker finishes:

1. Save its final result, useful terminal output, artifacts, and provider resume
  ID in the task ledger or output files. Record whether its result is verified
  or still needs integration; a closed pane does not imply accepted work.
2. Confirm its native descendants have stopped. If an interactive agent remains
  idle after finishing, exit it using the provider's supported mechanism and
  verify process state. A final message alone does not prove process exit.
3. Close that task-owned worker pane with `rex block close -s "$task_session"
  "$worker_block"` and verify its removal. If it already closed automatically,
  record that fact. Preserve failed-worker diagnostics before closing failed
  panes as well.

Do this during supervision, not only at final delivery. Leave a pane open only
when the user requests it or it still hosts needed work. Close only the finished
worker block, never a shared tab containing other agents, the coordinator, or
unrelated processes. Follow up on any worker or descendant that cannot be
stopped before transferring its write ownership.

## Final tab and session cleanup

After all assigned agents and descendants have stopped, and on cancellation or
launch failure after stopping owned workers, reconcile the complete resource
ledger against a fresh Rex inventory. Save results and diagnostics first.

1. Inspect all task-created tabs and close any remaining finished panes or
   confirmed unused starter shells. Close a whole tab only if every remaining
   pane is task-owned and finished; preserve any work added by the user or
   another task. Verify removal with `rex session inspect`.
2. Inspect each task-created fallback session again. If it contains no windows,
   remove the empty session explicitly with `rex kill "$created_session"`.
   Closing the final pane or tab does not guarantee session removal. If it still
   contains windows, close only confirmed finished task-owned resources first;
   do not kill a session containing unrelated or needed work.
3. Run `rex ls --json` again and verify removed session IDs are absent. Compare
   the remaining windows/blocks with the baseline and ledger. Preserve the
   invoking session and coordinator pane, even when no workers remain. A
   pre-existing session is not eligible for automatic deletion merely because
   it is empty; retrospective cleanup requires user scope and fresh inspection.
4. Record closed pane/tab/session IDs, verified absence, and every retained
   resource with its reason. Report a cleanup failure as an outstanding blocker;
   do not claim the workflow is fully cleaned up while owned junk remains.

Use the installed command help if syntax differs. These commands operate at
different scopes; closing a tab or session also closes everything inside it:

```sh
rex window close -s "$task_session" "$finished_task_window"
rex session inspect "$created_session" --json
# Only after confirming this task created it and it is empty:
rex kill "$created_session"
rex ls --json
```

## Launch, observe, recover

Write the worker brief to a file and use a verified stdin/file mechanism or a
carefully quoted argument. Pass command arguments separately; never interpolate
untrusted prompts into shell code. Prefer a noninteractive mode with durable
output and exit status when it supports the assignment. Use interactive mode
when necessary, and inspect the pane before sending input.

The installed Rex guide currently supports this shape; replace placeholders with
verified values and a real command, never run them literally:

```sh
rex window new -s "$task_session" "$workstream" -c "$worker_dir" --keep-open --focus=false --json -- COMMAND ARGUMENTS
rex split -s "$task_session" -b "$anchor_block" --split=right -c "$worker_dir" --label "$worker_label" --keep-open --focus=false --json -- COMMAND ARGUMENTS
rex capture -s "$task_session" -b "$worker_block" --trim --unwrap
rex block call -s "$task_session" -b "$worker_block" process
rex wait -s "$task_session" "$worker_block" --for 30s --json
```

`--keep-open` preserves output only until results are collected; close the
finished pane using the lifecycle above. Save returned block/window IDs
immediately and confirm the worker started in the intended directory with the
selected configuration. Keep stdout/stderr or provider result files when
scrollback is insufficient. A successful Rex launch proves only process
creation. Require the agent result, exit state, produced artifacts, and
appropriate checks before marking verified.

Keep existing permission protections. Do not use blanket bypass flags,
auto-trust hooks/workspaces, or globally rewrite agent settings merely to make
dispatch unattended. For an approval-blocked worker, inspect the requested
action and whether existing authorization covers it, then use the provider's
supported approval path or return the concrete decision to the user.

After a timed-out launch, inspect the saved session and labeled blocks before
retrying. Resume an exact recorded provider session ID, not an ambiguous
'latest' session. Check artifact freshness and revision before reuse. Before
replacing a writer, stop it and verify it has exited so two workers cannot keep
modifying the same files. Interrupt only owned worker blocks; preserve partial
work and record the reason.

If Rex or a provider is unavailable, explain the precise gap and continue
planning or independent work. An available alternative may be used when
consistent with the user's requirements; disclose the substitution. Never
describe built-in subagents as Claude, Hermes, or another external provider
without an actual verified launch.

Reference: [Rex agent
integration](https://www.superlogical.com/rex/docs/automate/agent-skill) and
[Rex CLI concepts](https://www.superlogical.com/rex/docs/automate/cli).
Installed help remains authoritative for command syntax.
