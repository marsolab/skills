---
description: Add to-dos to Things 3. Bare command is interactive (asks for project/area + schedule). `--quick` drops straight into Inbox.
allowed-tools: Bash, Read
---

Use the `things` skill to capture to-dos in Things 3.

Raw input: $ARGUMENTS

Mode selection:

- If the arguments start with `--quick` or `-q`, strip the flag and run **quick
  mode**: generalize the remaining text into atomic to-dos and add them all to
  the Things Inbox with no follow-up questions. Reply with a single-line
  confirmation like `Added N to-dos to Inbox.`
- Otherwise run **interactive mode**: parse, show the numbered list, ask
  whether anything needs editing, ask for a project/area (or Inbox), ask for a
  schedule, then submit.
- If the arguments are empty, ask: `What's on your mind? (prefix with --quick
  to skip confirmation and dump straight into Inbox.)` and wait.

Always submit via the bundled helper — never build `things:///` URLs inline in
Bash:

```
python3 plugins/things/skills/things/scripts/things_add.py --stdin
```

Refer to `plugins/things/skills/things/SKILL.md` for the parsing
rules, JSON schema, and failure modes.
