---
name: things-todo
description: >-
  Capture tasks into Things 3 on macOS via the things:/// URL scheme. ALWAYS
  use this skill when the user mentions Things (the Cultured Code app), Things
  3, Things Inbox, or asks to add/create/capture to-dos, tasks, reminders, or
  todos in Things. Also use when the user invokes the /mytodo slash command,
  dictates a stream-of-consciousness list they want turned into tasks, or asks
  to push items to Things by project or area. Covers: generalizing free text
  into atomic to-dos, batch-adding via things:///json, scheduling (today,
  anytime, someday, specific date), targeting projects or areas, tags, and
  checklist items. Not for other to-do apps — if the user mentions Reminders,
  Todoist, OmniFocus, or anything non-Things, do not use this skill.
version: 1.0.0
tags:
  - things
  - things3
  - todo
  - tasks
  - productivity
  - macos
  - url-scheme
---

# Things To-Do

Capture unstructured thought into well-formed Things to-dos and push them to
the app in a single batch. Built around the `things:///json` URL scheme, which
accepts a JSON array of items and requires no auth token for creating new
to-dos — only for updating existing ones.

The skill is designed for dictation workflows: the user speaks or types a
rambling brain-dump, and Claude turns it into a tidy list. Two modes:

| Mode | Invocation | What Claude does |
| --- | --- | --- |
| Interactive | `/mytodo <text>` or skill triggers naturally | Parse → show list → ask for edits → ask project/area → ask schedule → submit |
| Quick | `/mytodo --quick <text>` | Parse → submit to Inbox. No questions. |

## Interactive workflow

Follow these five steps in order. The point of the interview is to let the user
catch misparses *before* the data lands in Things, where cleanup is annoying.

### 1. Parse free text into atomic to-dos

Each to-do should be a single concrete action. Short, imperative titles (≤80
characters). Rules that make the output feel right:

- **Strip filler**: "I need to remember to email Alex" → title `Email Alex`.
- **Preserve specifics**: names, dates, dollar amounts, file names belong in
  either the title (if short) or the `notes` field (if detail would make the
  title unwieldy).
- **Split compound items carefully**: "buy milk and eggs" is one shopping
  trip → keep as `Buy milk and eggs`. But "email Alex and book a flight" is
  two distinct actions → split.
- **Lift context into notes**: "prepare a 10-minute presentation for the
  all-hands next Thursday covering key metrics and customer wins" → title
  `Prepare all-hands presentation`, notes contain the duration, date, and
  topic list.
- **Suggest a schedule when obvious**: "tomorrow I need to..." → propose
  `when: tomorrow` for those items. The user still confirms.

### 2. Present the proposed list

Show a numbered markdown list. For each to-do:

```
1. **Email Alex about Q2 roadmap**
2. **Book flight for Austin trip**
   — departing week of the 15th, find morning options
3. **Submit expense report from last week**
```

Keep it scannable. Don't include JSON, parameter names, or "the skill will
send...". The user is reviewing *content*, not plumbing.

### 3. Ask for edits

Use a single open question: *"Anything to add, remove, or reword?"*
Loop until the user approves ("looks good", "ship it", silence after
confirmation). Keep edits minimal — do not rewrite items the user hasn't
touched.

### 4. Ask destination, then schedule

Two short questions, in order:

1. **Project or area?** Accept a free-text name (e.g. `Work`, `Home
   Renovation`), or `Inbox` / `skip` to leave it in Inbox. If the user names
   something that doesn't exist in Things, the app creates the item in Inbox
   and silently ignores the unknown list — warn the user of this, don't pretend
   it landed in a project that doesn't exist.
2. **When?** Offer: `today`, `tomorrow`, `anytime`, `someday`, a specific date
   (`2026-05-01`), or `skip` to leave unscheduled.

Apply both to every item in the batch unless the user specified per-item
scheduling in step 1.

### 5. Submit via the helper script

Build a JSON array and pipe it to the bundled helper:

```bash
python3 plugins/things-todo/skills/things-todo/scripts/things_add.py --stdin <<'JSON'
[
  {"type":"to-do","attributes":{"title":"Email Alex about Q2 roadmap","when":"today","list":"Work"}},
  {"type":"to-do","attributes":{"title":"Book flight for Austin trip","notes":"Departing week of the 15th","when":"today","list":"Work"}}
]
JSON
```

The helper handles URL encoding and calls `open` on macOS. Report the result
as one line: `Added 3 to-dos to Work (scheduled today).`

## Quick workflow

`/mytodo --quick <text>`:

1. Parse the text into atomic to-dos (same rules as step 1 above).
2. Call the helper with no `when` or `list` on any item. Things routes
   untargeted items to Inbox.
3. Reply with a one-line confirmation: `Added 4 to-dos to Inbox.` Do not list
   them back — the point of quick mode is that it's quick.

Do not ask questions. If the input is empty or gibberish, say so and stop;
don't invent tasks.

## JSON batch format

The helper expects a JSON array. Each element is either a to-do or a project.
Minimal to-do:

```json
{"type":"to-do","attributes":{"title":"Buy milk"}}
```

Commonly used attributes:

| Field | Purpose |
| --- | --- |
| `title` | Required. Task name. |
| `notes` | Free-text detail. Supports newlines. |
| `when` | `today`, `tomorrow`, `evening`, `anytime`, `someday`, `yyyy-mm-dd`, or `yyyy-mm-dd@HH:mm`. |
| `deadline` | `yyyy-mm-dd`. Distinct from `when`. |
| `tags` | Array of existing tag names. Unknown tags are silently dropped by Things. |
| `checklist-items` | Array of `{"type":"checklist-item","attributes":{"title":"..."}}`. |
| `list` | Project or area name. Omit for Inbox. |
| `heading` | Section name within a project. |

For the full parameter list and project-creation schema, read
`references/things-url-scheme.md`.

## Auth token

The `add` and `json`-create commands do **not** require an auth token. The
helper only appends `&auth-token=...` when an item carries
`"operation": "update"` (future use). The token lives in the
`THINGS_AUTH_TOKEN` environment variable.

To obtain it: **Things → Settings → General → Enable Things URLs → Manage**.
Tell the user this if they later ask to complete or edit existing to-dos —
that's when the token starts to matter.

## Platform notes

- **macOS**: the helper runs `open "things:///json?..."`. Things launches and
  the items appear.
- **iOS**: the URL scheme works, but there's no `open` CLI. Print the URL and
  ask the user to tap it.
- **Linux / anywhere else**: Things isn't installed. The helper exits 2 and
  prints the URL so the user knows the call was well-formed but couldn't
  execute. Mention this in the reply rather than claiming success.

## Failure modes to anticipate

- **URL too long**: Things URLs are capped around 2000 characters after
  encoding. If a batch exceeds this, split into chunks and call the helper
  multiple times.
- **Things not installed or URL scheme disabled**: `open` returns non-zero.
  Surface the error; the fix is enabling Things URLs in settings.
- **Unknown project/area name**: Things silently drops the `list` and routes
  to Inbox. The helper can't detect this — warn the user that names must
  match exactly.
- **Unknown tag**: same silent drop. Tags must already exist in Things.

## Reference guides

- `references/things-url-scheme.md` — condensed URL-scheme reference: all
  parameters, the `json` schema, auth rules, encoding, rate limits.

## Quick reference

- Interactive mode: 5 steps (parse → show → edit → destination → submit).
- Quick mode: `--quick` flag, no questions, Inbox only.
- Submit via `scripts/things_add.py --stdin` — never build `things:///` URLs
  inline in Bash.
- No auth token needed for adding. Token only matters for updates.
- macOS only for execution; helper prints URL elsewhere.
