# Rex workers

## Discover the environment

Load the installed `rex` skill and execute `rex __internal skill`; if that
version lacks the guide, use `rex whoami --json` and command help. Follow the
installed guide over cached examples. If `rex` is absent from PATH, check
`REX_BIN_DIR` or the installed application bundle without changing shell
configuration. Locate any bundled executable from the actual installed
application; paths and app names vary. Prefer the executable matching the active
server.

Use the explicit user target, otherwise inherited `REX_SESSION`/`REX_BLOCK`.
Outside Rex, inspect `whoami` and `ls --json`; resolve ambiguity before touching
an existing session. A dedicated new task session is suitable when the user has
not requested an existing session. Record full returned IDs, never rely on focus
or tab positions. Remote hosts require an explicit target and their own paths,
tools, and authorization.

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

## Group panes and clean up finished workers

Treat a Rex window as a tab and a block as a pane (panel). Prefer one task tab
with several related worker panes. Inspect its layout and split an existing task
pane with `rex split`, using its full block ID. Choose right/below placement and
proportions to keep active agents readable. Keep the user's focus with
`--focus=false`. Create a new tab only for a distinct workstream or when further
splits would make the current tab impractical; do not create one tab per agent
by default. Native subagents remain within their parent agent unless the
platform itself requires another surface.

Record the task tab and worker block IDs. When the pane used as a split anchor
is closed, inspect the remaining layout and choose a live task pane before the
next dispatch. Keep the chief of staff's pane available.

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
worker block, never a shared tab containing other agents, the chief of staff, or
unrelated processes. Follow up on any worker or descendant that cannot be
stopped before transferring its write ownership.

## Launch, observe, recover

Write the worker brief to a file and use a verified stdin/file mechanism or a
carefully quoted argument. Pass command arguments separately; never interpolate
untrusted prompts into shell code. Prefer a noninteractive mode with durable
output and exit status when it supports the assignment. Use interactive mode
when necessary, and inspect the pane before sending input.

The installed Rex guide currently supports this shape; replace placeholders with
verified values and a real command, never run them literally:

```sh
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
