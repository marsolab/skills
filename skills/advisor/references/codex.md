# Codex adapter

Read the available tool schema before calling it. These examples apply to
Codex runtimes exposing `collaboration.spawn_agent`. Other runtimes need
equivalent explicit model selection and a channel that returns the advisor's
response to the requester. Keep the original model responsible for the task.

## Spawn an advisor

Select the advisor using the skill's model-selection guidance and the runtime's
exposed identifiers. For this tool, use `fork_turns: "none"` when overriding
the model: a full-history fork inherits the parent's model. Provide all relevant
context explicitly in `message`.

Record the requested model and effort, the runtime-accepted selection, and the
returned agent identifier. Preserve any runtime-reported effective values;
otherwise leave execution identity unknown. An echoed model name in the
advisor's answer does not establish which backend served the request.

This example selects Sol for a requester for which Sol is more capable.
Replace the bracketed message with
[a complete consultation](consultation.md), including its mode and evidence:

```json
{
  "task_name": "advisor_sol",
  "model": "gpt-6.1-sol",
  "fork_turns": "none",
  "message": "[complete consultation from consultation.md]"
}
```

For an Astra consultation, use `model: "gpt-6-astra"` and a unique task name
such as `advisor_astra`. For another model, use its actual exposed identifier.
Set `reasoning_effort` only when needed and supported by the selected model;
use the default only when no effort was required or selected. If a required
effort is unsupported, report the limitation and preserve the requirement;
substitute only within authorized alternatives. A higher effort on the same
model is not a different, more capable model.

Include the resolved path to this skill's `SKILL.md` when the advisor needs the
full instructions. Resolve it from the installation, not a host-specific path.

## Return advice to the requester's context

Retain the identifier returned by `spawn_agent`. In a `collaboration` runtime,
wait with `wait_agent` until the agent's actual response is delivered to this
conversation. Read the delivered message or final answer before resuming the
dependent work. A timeout or an acknowledgement is not a consultation result.
If the runtime instead exposes a result-retrieval tool, retrieve the response
and read its text here. Check its question, coverage, recommendation, and any
missing context using the consultation contract; receipt alone is not quality
validation.

On a wait timeout, keep the existing consultation pending and wait again within
applicable limits; do not launch a duplicate. If the agent fails, is cancelled,
or exceeds the permitted waiting budget, report that no advice was received.
Interrupt any still-running advisor before abandoning the consultation, then
continue independent work or report the unresolved blocker.

Use `send_message` to clarify an active advisor's question, and `followup_task`
to give an idle advisor concrete new evidence or validation feedback. If the
user cancels or changes the question, steer or interrupt the advisor too.

If a nesting limit prevents the requester from spawning, return the brief to
its existing parent, including the original requester's identifier and model
when exposed. The parent acts only as a broker and selects relative to the
original requester, rather than the parent's model. It spawns the advisor and
relays the actual advice to that same requester with `send_message` if active
or `followup_task` if idle. Include the response, model used, and any relevant
evidence and selection metadata. Do not replace the requester with a new
developer or ask it to read a separate chat.

The requester evaluates the advice, makes any changes, and performs validation.
The advisor's final response arrives through the native agent channel; it does
not need an additional user-facing chat or an artifact file to carry the advice.

## Capability limits

`agents/openai.yaml` provides interface metadata, not execution-model selection.
Portable installation in Claude Code or Cursor does not itself grant access to
OpenAI models. Adapt to the native tools and available stronger models there.
Report a missing capability without editing global configuration automatically.

Use a runtime-provided read-only profile when available. A read-only instruction
in the prompt is not an enforced sandbox; do not invent permission arguments or
claim the tool restrictions are enforced when only the brief requests them.

Consult the official [Codex subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)
when runtime configuration or result-delivery behavior needs clarification.
