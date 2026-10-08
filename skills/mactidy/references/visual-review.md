# Visual review and cleanup selection

Use after read-only inventory and candidate classification. The result should
help the user see what occupies space, who owns it, and decide what to remove.
Generate it from the current audit; a prior cleanup report is a dated comparison,
not evidence that today's targets are unchanged.

## Data and accounting

Build a compact display model from the CLI JSON and scoped supplemental checks.
Each target needs a stable review ID mapped to an exact canonical path, full
container ID, volume name plus context, or PID plus identity. Include its owner,
resource kind, measured size and basis, evidence timestamp, proposed operation,
recovery method, and status: `verified`, `protected`, or `needs_review`.
CLI audit candidates start as `needs_review`; the scanner does not prove safety.
Keep secrets, environment variables, raw logs, and full process arguments out of
the display model. Include only necessary, sanitized ownership evidence.

Keep these measurements separate:

| View | Source and units | What it means |
| --- | --- | --- |
| Physical disk | `df`, GiB | Used/available on the Data volume |
| Audited paths | CLI/`du`, GiB | Logical size in the explicit scope |
| Docker | Daemon accounting, GiB | Images, layers, cache, volumes |
| Process memory | RSS/Docker stats, MiB | Reported per process/container |

Do not add Docker size to its backing VM file, add a worktree total to its nested
artifacts, or count a shared volume once per container. Deduplicate exact target
identities and omit overlapping parent totals from additive views. If overlap
or APFS sharing cannot be resolved, show individual estimates without a summed
recovery claim. Never subtract logical path sizes from physical `df` usage to
invent an "other" slice. Unknown sizes are unknown, not zero. Use zero only
after measuring an empty resource. Never fabricate owner or category sizes.

## Visual structure

Use the user's language. Show the audit time and explicit roots/context. Start
with a small used/available bar from `df`, then a separate horizontal bar chart
of audited logical sizes grouped by owning project or tool. Label the latter
"Измеренные ресурсы в выбранных
каталогах"; it is not a breakdown of the entire Mac. If whole-disk categories
were not measured, label that coverage gap.

For many nested resources, a treemap can support project → resource type →
target drill-down. Give small or zero-size items a readable list alternative;
essential details must remain accessible without hovering. Show Docker data
and memory in separate labeled panels only when those systems were audited.
Keep images, build cache, container layers, and volumes distinguishable.

For memory, follow [memory.md](memory.md). Show pressure/swap observations over
the sampled interval and separate ranked process bars. Keep host RAM, process
RSS, and container memory distinct; a memory chart must not imply that summing
RSS yields unique RAM or guaranteed recovery. Let the user choose eligible
"Остановить" actions separately from file/volume deletion.

Clicking a category or mark reveals its targets and ownership evidence. The
details should show exact identity, size basis, why it can or cannot be removed,
removal effect, and recovery. Use status text alongside color:

- `verified`: decisive safety checks passed; eligible for a proposed batch.
- `protected`: active, dirty, unpushed, database/credential/session state, or
  another known reason to retain; cleanup selection disabled.
- `needs_review`: evidence incomplete; may be selected for investigation, not
  for deletion. Do not label an unreferenced database as a safe cache.

Group large sets into homogeneous review batches while retaining their exact
membership list. An expansion or equivalent accessible detail must reveal
which identities the batch covers. A group must not silently select protected
or unreviewed children. Never offer a blanket "delete everything" action.

## Interaction and delivery

If the available `visualize` skill supports an inline interactive visual, read
it and follow its current rendering and accessibility contract. Do not depend
on a hard-coded plugin version or host API. If it is absent, use a self-contained
local HTML report with embedded sanitized data and no external data uploads, or
a static SVG/chart with a Markdown review table. Rendering failure must fall
back to the table rather than bypass the user's choice.

Use native checkboxes for eligible cleanup targets, all unchecked initially.
Update a selected-target count, the proposed operations, and logical size by
measurement basis. Call this "Выбрано для плана",
not "Будет освобождено".
Keep a concise list/text alternative for keyboard and touch users. The visual
must fit narrow screens, preserve readable labels, and make every essential
detail available without hover. Unknown sizes remain visible in the selection.

The visual only prepares a plan. It must have no direct filesystem, shell,
Docker, process-signal, or remote deletion capability. A local fallback can
display an exact-target choice for the user to copy into chat. An inline host
with an explicit follow-up-message API may offer
"Отправить выбранный план";
include the audit ID/time, selected exact identities and operations, and ask the
agent to recheck them. Label the action's consequences accurately.

Saved checkbox/widget state is only a preference draft: it may be stale and
delivery to the agent is not guaranteed. The user must explicitly submit their
choice. For hundreds of targets, send compact stable review IDs plus a local
manifest reference; resolve the IDs against that same manifest before acting.
Do not upload a manifest or share it with an external service.

## Ask and act

After the visual, ask one short selection question using the available
user-input surface or normal chat. Give 2–3 meaningful choices bound to
concrete batches, plus a way to keep everything or specify individual items.
For example: "Что удалить: проверенные кэши
(A1–A4), кэши и старые сборки
(A1–A7), или ничего?" Include exact targets, approximate logical size,
recovery, and
material consequences before the question, so the choice is reviewable.

If the user already authorized that exact batch or concrete tool-native
operation, show its scope and do not repeat the question unless they requested
a new selection step. For a broad cleanup/audit, no reply means retain the
resources. Continue only independent read-only investigation while waiting.

Only a submitted explicit choice authorizes its mapped actions. Ambiguous
replies or a choice to investigate do not authorize cleanup. Before acting,
re-resolve selected identities and repeat decisive checks; skip/reclassify
targets that became active or drifted. A request to remove files via Trash does
not authorize emptying Trash, and choosing to stop a stack does not authorize
deleting its volumes. Ask only for genuinely new scope or changed consequences.

After the bounded batch, update the review with completed/skipped/retained
status and fresh physical `df` measurements. Report actual free-space change
separately from the selected logical estimate and tool-reported reclaimed size.
If another process changed disk usage during the interval, say that the `df`
delta is the observed interval change rather than a perfectly isolated measure.
