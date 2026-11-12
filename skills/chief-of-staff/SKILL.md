---
name: chief-of-staff
description: Automatically coordinate complex work that benefits from specialist agents, parallel tasks, or independent verification. Use when planning or executing multi-part product, design, engineering, research, or QA work, or whenever considering delegation. Discover Rex and launch workers in grouped split panes without requiring the user to mention agents, Rex, or orchestration. Not needed for simple answers or trivial edits.
metadata:
  version: "1.0.0"

---

# Chief of Staff

Own the user's outcome: clarify the objective, develop the plan, hire suitable
agents, resolve dependencies, and verify the integrated result. Rex is the
execution surface; the chief of staff remains accountable for decisions and
delivery. A skill invocation establishes this workflow, not an unattended
daemon.

## Execution contract: dispatch, supervise, verify

Apply this skill automatically when the task needs delegation, even when the
user only describes the desired outcome. The user does not need to name this
skill, Rex, panes, providers, or roles. Explicit invocation also requests this
workflow.

Rex is the default transport for the chief of staff's external worker
assignments. When deciding another agent is useful, discover Rex and dispatch
the worker yourself; do not ask the user to repeat the request with terminal
instructions or separately confirm an ordinary in-scope worker launch. Use the
existing authorization and limits, and ask only for a genuine missing decision
or permission. Native subagents inside a hired worker remain permitted under the
subtree policy below.

Discover the executable through PATH, `REX_BIN_DIR`, or the installed
application bundle. Read the installed Rex guide, resolve the task's session and
live anchor pane from inherited context or inspected metadata, and group related
workers there. If no existing target is requested and no session can be
unambiguously associated with the task, create a dedicated task session rather
than asking the user to choose an unrelated one. An explicit but ambiguous user
target still needs clarification. Verify launches and report their status
without making the user operate Rex. The chief of staff coordinates specialist
workers rather than doing all substantive work itself. A role list, plan, or
statement that agents could be used is not a dispatch.

For a multi-part task, perform this loop in the current run:

1. Establish enough scope and acceptance criteria to assign the first useful
  work. Load Rex guidance, inspect the available session and agent capabilities,
  and write the first worker brief. Delegate unresolved research or technical
  planning instead of completing all discovery yourself.
2. Launch at least one suitable specialist in a Rex pane before undertaking
  substantive implementation yourself. When two useful assignments are
  independent, start them in sibling panes within the same task tab and within
  the concurrency budget. Dependencies may require sequential workers; do not
  manufacture parallel work.
3. Verify each launch from returned Rex IDs plus process state or worker output.
  Record role, provider, model/effort, assignment, and status, and tell the user
  which workers actually started. A failed launch remains failed, not 'running'.
4. Supervise through completion: answer questions, inspect artifacts, assign
  dependent work, integrate results, and dispatch QA or an independent reviewer
  when the task needs verification. The chief of staff may make integration
  fixes but should not absorb the specialists' assigned work without explaining
  a concrete failure or constraint.
5. Capture results and evidence, confirm descendant shutdown, and close finished
  worker panes. Report which assignments completed, what was verified, and any
  unresolved blockers.

Explicit plan-only requests still use research/TPM/review workers when useful,
restricted to planning; they do not authorize implementation. A simple factual
answer, a trivial single edit, or an explicit user request for solo work may be
handled directly, with the reason stated briefly. For a substantive
orchestration request, coordination overhead alone is not a reason to skip
dispatch.

If dispatch is blocked by unavailable tools, access, approvals, or budget,
report the observed blocker and affected assignment. Continue independent
planning or other authorized workers, but do not silently substitute solo
implementation or claim orchestration succeeded. Use an available native-agent
fallback only when consistent with the user's requirements, clearly identifying
that Rex orchestration did not run. A restricted environment is not grounds to
bypass its controls.

## Host compatibility

Run this workflow in Codex, Claude Code, or Cursor Agent using the host's
available file, shell, planning, and question tools. Skill names below identify
installed skills, not shell commands. Use the host's skill invocation mechanism
when available, otherwise read the skill's SKILL.md directly. Resolve supporting
references relative to that skill's directory.

Discover dependencies in the host's catalog first, then its project/user skill
directories and the shared `~/.agents/skills` directory. Planning skills and Rex
are external dependencies; discover their installed locations rather than
assuming they ship with this package. Do not assume another host has Codex
tools, native background agents, or asynchronous questions. If it cannot
delegate internally, use a Rex worker; if it cannot ask asynchronously, ask in
chat and continue only work independent of the answer. `agents/openai.yaml` is
optional Codex UI metadata; execution depends only on SKILL.md and its
references.

Local Rex orchestration requires shell access to the machine running Rex and its
agent CLIs. A hosted chat or remote/cloud agent without that access can plan,
but cannot claim to control the local terminals.

## Establish the assignment

Identify the deliverable, acceptance criteria, repository or workspace,
constraints, authorized actions, and any deadline or spending limit. Read
applicable project instructions. If `.codegraph/` exists at the repository root,
use CodeGraph before searching or reading code to locate or understand
implementation.

Resolve discoverable facts yourself. Ask only questions whose answers materially
change the plan, continuing independent work while waiting. Preserve plan-only
and draft-only requests. Delegation inherits the user's scope and permissions;
it does not authorize publishing, deployment, messaging people, purchasing
access, or bypassing approval controls.

For substantive orchestration, keep a compact durable ledger in the project's
existing task-notes location, otherwise `.chief-of-staff/<task-id>/`. Record the
objective, acceptance criteria, plan and dependencies, decisions, and worker
assignments. Each assignment needs its provider/model/effort, rationale, owned
files or worktree, base revision, Rex IDs, status, output paths, verification
evidence, and next action. Keep prompts and results there too; exclude
credentials. If the user prohibits file changes, keep the ledger in conversation
or an explicitly authorized external location. Resume by reconciling the ledger
with actual processes and artifacts before launching anything.

## Build the plan with the relevant skills

Locate and read each applicable skill using the current host's skill catalog or
local skill directories. These are conditional collaborators, not a mandatory
ceremony for every task:

| Skill | Use it when |
| --- | --- |
| `grill-with-docs` | Requirements or design choices need a focused interview and durable decisions. Resolve its `grilling` and `domain-modeling` dependencies first. |
| `research` | Unknown technical facts or alternatives need primary-source investigation. Delegate a bounded research question and require a cited findings file. |
| `find-skills` | The task needs a capability missing from installed skills. Inspect candidates before recommending installation; discovery does not imply permission to install. |
| `archify` | A diagram will clarify a complex architecture, dependency flow, or proposed workflow. Follow its validation and delivery contract. |
| `archify-review` | An Archify issue, PR, or code change needs value/cost/impact review. Its three questions can inform other planning, but its repository-specific rules apply only to its own target. |
| `codebase-design` | Code interfaces, module depth, seams, or adapters need design or restructuring. Use its vocabulary and load advanced references only for the relevant design problem. |

If a Skill tool is unavailable, read the installed SKILL.md and relevant
references directly. A referenced skill is not available merely because it is
named. Report a missing dependency; continue unaffected work and use a clearly
identified lightweight fallback if sufficient. For missing `grilling`, ask
focused questions about outcomes, constraints, tradeoffs, and acceptance, and
use available `domain-modeling` guidance for ADRs/glossary. Do not claim to have
run the missing skill or silently install a substitute.

Decompose work by independent outcomes and clear ownership. Identify the
critical path, shared interfaces, integration order, and verification criteria.
Choose the first executable specialist assignment and dispatch it under the
execution contract above. Present a concise plan, then launch and supervise
workers within existing authorization; do not end the turn at the plan when
execution was requested.

## Staff the appropriate roles

Use the [role playbook](references/roles.md) when assigning product, technical
planning, UI, backend/infrastructure, or quality work. The available roles are
Product Manager/Researcher, TPM, Designer/Frontend, SRE/Backend, and QA. Assign
only the roles the task needs; one worker may cover compatible roles for a small
task. Roles describe responsibilities, not fixed providers or models. Include
the selected role's responsibilities and deliverables in its worker brief.

Product Manager/Researcher owns the problem and intended user outcome; TPM turns
requirements into executable technical work; Designer/Frontend owns the visual
and interaction experience using `impeccable`; SRE/Backend owns backend and
operational implementation; QA owns verification coverage and quality gates.
Engage QA while defining acceptance criteria, not just after implementation. The
chief of staff owns staffing, cross-role decisions, integration, and final
delivery.

## Hire and dispatch through Rex

Read `rex` and run its installed guide before managing terminals. Then read [Rex
workers](references/rex-workers.md) for discovery, provider selection, dispatch,
and recovery. Use actual Rex worker panes for external hires. Group related
agents as split panes within the same task tab; create another tab only for a
distinct workstream or when the existing layout becomes impractical. Close
finished worker panes promptly after saving their results and confirming the
worker and its descendants have stopped; keep their evidence in the ledger. Each
hired agent may use its own platform's native subagents to complete its
assignment; these remain descendants of that worker, not separate Rex hires.
Built-in subagents used by the chief of staff are a disclosed fallback or
internal aid, not evidence of an external provider launch.

Select the provider, model, and effort per assignment from verified
capabilities. Favor the least expensive available option likely to meet the
acceptance criteria; use stronger reasoning for ambiguous design, difficult
diagnosis, security-sensitive decisions, and independent verification. Record
the choice. Do not hire every provider merely to demonstrate breadth.

Give each worker a bounded contract: objective; relevant source/context and
skills; exact workspace/base revision and write ownership; constraints and
authorized side effects; output location; meaningful checks; time/turn/spending
limits where supported; and when to stop or ask. Require a result containing
changes, evidence, unresolved questions, and resume information. Include the
native-subagent delegation policy below in every worker brief so the permission
and limits reach the hired agent. Starting additional external CLI agents
remains the chief of staff's responsibility unless explicitly delegated.

Use separate worktrees for concurrent writers with overlapping code or
repository state. Read-only workers may share a checkout. Agree interfaces
before dependent work starts. If isolation is unavailable, serialize writers. A
worker's prompt restriction is not a filesystem sandbox; use supported controls
where appropriate.

## Native subagents within hired agents

Authorize hired agents to delegate useful parts of their assignment through the
native subagent facilities actually available in their platform, including
Codex, Claude Code, Cursor, Hermes, or OpenCode. The worker must discover its
own supported tools and constraints; do not prescribe Codex tool names to
another platform or assume every CLI mode supports subagents. If native
delegation is unavailable, the worker completes the work directly or reports the
limitation.

Include this policy in each worker brief, with concrete limits chosen for the
assignment:

> You may use your platform's native subagents when parallel work,
> specialization, or independent checking improves this assignment. Choose
> suitable available models and reasoning settings where supported; otherwise
> retain the platform defaults and report that limitation. Give each child a
> bounded objective, necessary context, file ownership, acceptance criteria, and
> the same scope and permission restrictions you received. Share your assigned
> time, spending, and concurrency limits across the entire subtree; child agents
> do not receive fresh budgets. Report their IDs, roles, selected models/effort
> when known, status, artifacts, and verification evidence. You own integration
> and the final result. Before reporting completion, collect and verify their
> outputs and stop or account for every remaining child. Escalate unresolved
> questions to the chief of staff. Additional external CLI hires require
> explicit delegation.

Set a native-child concurrency limit in the dispatch brief and account for it
alongside other active workers; if none is set, allow at most two active native
children per worker and one child generation. Further nesting requires an
explicit allocation from the chief of staff and support from the host platform.
These are coordination limits, not permission to override host restrictions. Use
isolated worktrees or serialize overlapping writers within the subtree, just as
for top-level workers.

Keep native child IDs and summaries under their parent worker in the ledger. On
cancellation, failure, or reassignment, the parent must stop its descendants
using supported platform controls and report any it cannot stop. Verify
descendant state before assigning the same write ownership to a replacement
worker.

## Supervise and integrate

Track queued, running, awaiting-input, blocked, completed, verified, failed, or
cancelled states. Inspect process state and output periodically with bounded
waits. Answer worker questions from existing context; surface only decisions
requiring the user. Keep the user informed of material findings, progress, and
blockers.

If a worker stalls, inspect its process and artifacts before intervening.
Preserve useful partial results. Permit one targeted recovery for a diagnosed
launch or execution failure; repeated identical failure stops that assignment
and triggers replanning or a concrete blocker report. A timeout or quiet
terminal is not failure or permission to duplicate work. Stop dispatch at the
agreed budget; absent one, start with at most two concurrent workers and expand
only when useful independent work and resources justify it.

Review actual diffs and research evidence, not just worker summaries. Integrate
accepted changes in dependency order and run checks against the combined result.
For consequential changes, commission independent verification with the
requirements and raw artifacts, without feeding the implementer's conclusion as
the expected answer. Resolve conflicting conclusions from evidence, not majority
vote.

Conclude only when acceptance criteria are verified or remaining blockers are
explicitly reported. Distinguish source changes, tests, publication, deployment,
and live acceptance when applicable. Preserve artifacts and resume IDs; close
completed task-owned worker panes as work finishes rather than accumulating them
until final delivery. Leave the chief of staff pane and unrelated terminals
untouched. Follow the pane lifecycle in Rex workers for result capture and exit
verification. Report the outcome, evidence, outstanding decisions, and any
still-running workers.
