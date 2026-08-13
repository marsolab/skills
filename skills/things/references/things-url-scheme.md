# Things URL Scheme Reference

Condensed reference for the `things:///` URL scheme. Full documentation at
<https://culturedcode.com/things/support/articles/2803573/>.

All commands take the shape `things:///<command>?<query-string>`. Opening the
URL launches Things and runs the command.

## Commands at a glance

| Command | Purpose | Auth token? |
| --- | --- | --- |
| `add` | Create one to-do | No |
| `add-project` | Create one project | No |
| `json` | Batch create/update multiple items | Only for updates |
| `update` | Modify existing to-do by ID | Yes |
| `update-project` | Modify existing project by ID | Yes |
| `show` | Navigate to a list/project/tag/to-do | No |
| `search` | Open search UI | No |
| `version` | Report app + scheme versions | No |

Prefer `json` for anything beyond a one-off — batch is cheaper and atomic.

## `add` parameters

Every parameter below goes into the query string. Strings must be URL-encoded
(`%20` for space, `%0a` for newline).

| Name | Value |
| --- | --- |
| `title` | To-do name. Max 4,000 unencoded chars. |
| `titles` | Multiple titles separated by `%0a`. Creates one to-do per line. |
| `notes` | Free-text description. Max 10,000 unencoded chars. |
| `when` | `today`, `tomorrow`, `evening`, `anytime`, `someday`, `yyyy-mm-dd`, or `yyyy-mm-dd@HH:mm`. |
| `deadline` | `yyyy-mm-dd`. Distinct from `when`. |
| `tags` | Comma-separated tag names. Unknown tags are dropped silently. |
| `checklist-items` | Lines separated by `%0a`. Max 100 items. |
| `list` | Target project or area *name*. Omit for Inbox. |
| `list-id` | Target project or area *ID*. Takes precedence over `list`. |
| `heading` | Section within a project. |
| `completed` | `true` / `false`. |
| `canceled` | `true` / `false`. Overrides `completed`. |
| `creation-date` | ISO8601 datetime. |
| `completion-date` | ISO8601 datetime. |
| `show-quick-entry` | `true` opens the quick-entry dialog instead of adding. |
| `reveal` | `true` navigates to the new to-do after creating it. |

**Inbox targeting**: omit both `when` and `list-id` (a bare `list` that doesn't
match anything also falls back to Inbox).

## `json` command

Accepts one URL-encoded parameter, `data`, which is a JSON array. Each element
is an object with `type` and `attributes`.

### Supported `type` values

- `to-do`
- `project`
- `heading` — only inside a project's `items`
- `checklist-item` — only inside a to-do's `checklist-items`

### To-do shape

```json
{
  "type": "to-do",
  "attributes": {
    "title": "Buy milk",
    "notes": "Oat, 2L",
    "when": "today",
    "deadline": "2026-05-01",
    "tags": ["Errand"],
    "list": "Groceries",
    "heading": "Dairy",
    "checklist-items": [
      {"type": "checklist-item", "attributes": {"title": "Oat"}},
      {"type": "checklist-item", "attributes": {"title": "2L jug"}}
    ],
    "completed": false
  }
}
```

### Project shape

```json
{
  "type": "project",
  "attributes": {
    "title": "Kitchen reno",
    "area": "Home",
    "deadline": "2026-07-01",
    "items": [
      {"type": "heading", "attributes": {"title": "Demo"}},
      {"type": "to-do", "attributes": {"title": "Remove upper cabinets"}},
      {"type": "to-do", "attributes": {"title": "Patch drywall"}}
    ]
  }
}
```

### Update operation

```json
{
  "type": "to-do",
  "operation": "update",
  "id": "ABC123-def-456",
  "attributes": {"completed": true}
}
```

Obtain IDs via **Share → Copy Link** on a to-do. `update` requires the auth
token.

### Encoding

1. Serialize the JSON with no extra whitespace (`json.dumps(items,
   separators=(",", ":"))` in Python).
2. URL-encode the entire string, quoting every reserved character.
3. Assemble: `things:///json?data=<encoded>` (+ `&auth-token=<token>` if any
   item is an update).

## Auth token

- Needed for: `update`, `update-project`, and `json` when it contains any
  `"operation": "update"` items.
- Not needed for: `add`, `add-project`, read-only commands, and `json` that
  only creates new items.
- Obtain: **Things → Settings → General → Enable Things URLs → Manage**.
- The skill reads it from the `THINGS_AUTH_TOKEN` env var.

## Rate limit

250 items per 10-second window. Chunk large imports.

## Built-in list IDs (for `show` only)

`inbox`, `today`, `anytime`, `upcoming`, `someday`, `logbook`, `tomorrow`,
`deadlines`, `repeating`, `all-projects`, `logged-projects`.

These are *navigation targets*. They don't work as the `list` parameter on
`add` — for `add`, `list` only matches user-created projects and areas by
name.

## Platform notes

| | Mac | iOS |
| --- | --- | --- |
| Launch a URL | `open "things:///..."` | Tap a link or share sheet |
| Get an ID | Control-click → Share → Copy Link | Tap to-do → toolbar → Share → Copy Link |
| Enable URLs | Settings → General → Enable Things URLs | Settings → General → Things URLs |

Things is not available on Linux, Windows, or Android.
