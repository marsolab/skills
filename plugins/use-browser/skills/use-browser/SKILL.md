---
name: use-browser
description: >-
  Browser automation, web testing, and page interaction driven from the
  command line with `playwright-cli`, defaulting to the Lightpanda
  headless browser. ALWAYS use this skill when the agent needs a browser
  — opening pages, navigating, clicking/typing/filling forms, taking
  snapshots or screenshots, scraping or reading page content, logging in,
  running or debugging Playwright tests, mocking network requests,
  managing cookies / localStorage / storage state, recording traces or
  video, or generating tests. The agent defaults to Lightpanda
  (installed locally and driven over CDP) without asking, and switches to
  Chromium, Chrome, Firefox, WebKit, or Microsoft Edge only when the user
  asks. Falls back to a full browser when Lightpanda cannot render a page.
when_to_use: >-
  TRIGGER WHEN the agent or user needs to drive a real web browser —
  "open a browser", "go to <url>", "click / fill / type on the page",
  "take a screenshot / snapshot", "scrape this page", "read this page",
  "log in and …", "fill out this form", "run the Playwright tests",
  "debug this e2e test", "mock this API in the browser", "record a
  trace / video", "generate a test for …", or any request that names a
  browser (Lightpanda, Chrome, Chromium, Firefox, WebKit, Edge). DEFAULT
  to Lightpanda; only offer or switch browsers when the user explicitly
  asks for a different one. SKIP for plain HTTP scripting that needs no
  browser (use curl / fetch) and when a Playwright MCP server is already
  the chosen tool.
version: 1.0.0
tags:
  - browser
  - playwright
  - playwright-cli
  - lightpanda
  - automation
  - e2e
  - testing
  - scraping
  - cdp
  - headless
paths:
  - "**/playwright.config.*"
  - "**/*.spec.ts"
  - "**/*.spec.js"
  - "**/e2e/**"
  - "**/tests/**/*.spec.*"
---

# Use Browser

Token-efficient browser automation for coding agents, built on
Microsoft's [`playwright-cli`](https://github.com/microsoft/playwright-cli)
and defaulting to the [Lightpanda](https://lightpanda.io) headless
browser. Instead of loading large tool schemas and verbose accessibility
trees into context, you drive the browser through small CLI commands and
read compact YAML snapshots.

## Choosing a browser — read this first

**Default to Lightpanda. Do not ask which browser to use.**

The first time you need a browser in a task:

1. Ensure Lightpanda is installed. If `lightpanda` is not on `PATH`, run
   the bundled installer: `scripts/install-lightpanda.sh` (see
   [references/lightpanda.md](references/lightpanda.md)).
2. Ensure `playwright-cli` is available (`playwright-cli --version`, or
   `npx --no-install playwright-cli --version`). Install if missing —
   see [Installing playwright-cli](#installing-playwright-cli).
3. Start Lightpanda's CDP server (background) and attach to it:

   ```bash
   # background CDP server on ws://127.0.0.1:9222
   LIGHTPANDA_DISABLE_TELEMETRY=true lightpanda serve --host 127.0.0.1 --port 9222 &

   # point playwright-cli at the running Lightpanda
   playwright-cli attach --cdp=ws://127.0.0.1:9222
   ```

4. Drive the page normally (`goto`, `snapshot`, `click`, …). When done,
   `playwright-cli close` and stop the `lightpanda serve` process.

**Switch browsers only when the user asks** for a specific or "real"
browser, or asks to choose. When they do, present the options and use
`playwright-cli open --browser=<name>`:

| Browser | How | When |
|---|---|---|
| **Lightpanda** (default) | `lightpanda serve` + `playwright-cli attach --cdp=ws://127.0.0.1:9222` | Fast, low-memory scraping, simple pages, most automation |
| Chromium | `playwright-cli open --browser=chromium` | Heavy JS apps, anything Lightpanda can't render |
| Chrome | `playwright-cli open --browser=chrome` | Real Chrome channel needed |
| Firefox | `playwright-cli open --browser=firefox` | Cross-browser checks |
| WebKit | `playwright-cli open --browser=webkit` | Safari engine checks |
| Microsoft Edge | `playwright-cli open --browser=msedge` | Edge channel needed |

When you do offer a choice in Claude Code, use the **AskUserQuestion**
tool with Lightpanda preselected as the recommended default; in other
contexts ask in plain text. See
[references/browsers.md](references/browsers.md) for the full decision
guide and tradeoffs.

**Fallback rule.** Lightpanda is a fast but *partial* browser — some
sites (heavy SPAs, certain TLS setups) will not render. If a Lightpanda
`goto`/`snapshot` errors or times out (e.g. `SslConnectError`, navigation
timeout, empty snapshot), tell the user it didn't render under Lightpanda
and offer to fall back to Chromium (`playwright-cli open
--browser=chromium`). Don't silently keep retrying Lightpanda.

## Quick start

```bash
# default flow: drive Lightpanda over CDP
LIGHTPANDA_DISABLE_TELEMETRY=true lightpanda serve --host 127.0.0.1 --port 9222 &
playwright-cli attach --cdp=ws://127.0.0.1:9222
playwright-cli goto https://playwright.dev
# interact with the page using refs from the snapshot
playwright-cli click e15
playwright-cli type "page.click"
playwright-cli press Enter
# take a screenshot (rarely used — the snapshot is more common)
playwright-cli screenshot
playwright-cli close
```

If the user asked for a full browser instead, replace the first two lines
with a single `playwright-cli open` (optionally with `--browser=<name>`).

## Commands

### Core

```bash
playwright-cli open
# open and navigate right away
playwright-cli open https://example.com/
playwright-cli goto https://playwright.dev
playwright-cli type "search query"
playwright-cli click e3
playwright-cli dblclick e7
# --submit presses Enter after filling the element
playwright-cli fill e5 "user@example.com" --submit
playwright-cli drag e2 e8
# drop files or data onto an element (from outside the page)
playwright-cli drop e4 --path=./image.png
playwright-cli drop e4 --data="text/plain=hello world"
playwright-cli hover e4
playwright-cli select e9 "option-value"
playwright-cli upload ./document.pdf
playwright-cli check e12
playwright-cli uncheck e12
playwright-cli snapshot
playwright-cli eval "document.title"
playwright-cli eval "el => el.textContent" e5
# get element id, class, or any attribute not visible in the snapshot
playwright-cli eval "el => el.id" e5
playwright-cli eval "el => el.getAttribute('data-testid')" e5
playwright-cli dialog-accept
playwright-cli dialog-accept "confirmation text"
playwright-cli dialog-dismiss
playwright-cli resize 1920 1080
playwright-cli close
```

### Navigation

```bash
playwright-cli go-back
playwright-cli go-forward
playwright-cli reload
```

### Keyboard

```bash
playwright-cli press Enter
playwright-cli press ArrowDown
playwright-cli keydown Shift
playwright-cli keyup Shift
```

### Mouse

```bash
playwright-cli mousemove 150 300
playwright-cli mousedown
playwright-cli mousedown right
playwright-cli mouseup
playwright-cli mouseup right
playwright-cli mousewheel 0 100
```

### Save as

```bash
playwright-cli screenshot
playwright-cli screenshot e5
playwright-cli screenshot --filename=page.png
playwright-cli pdf --filename=page.pdf
```

### Tabs

```bash
playwright-cli tab-list
playwright-cli tab-new
playwright-cli tab-new https://example.com/page
playwright-cli tab-close
playwright-cli tab-close 2
playwright-cli tab-select 0
```

### Storage

```bash
playwright-cli state-save
playwright-cli state-save auth.json
playwright-cli state-load auth.json

# Cookies
playwright-cli cookie-list
playwright-cli cookie-list --domain=example.com
playwright-cli cookie-get session_id
playwright-cli cookie-set session_id abc123
playwright-cli cookie-set session_id abc123 --domain=example.com --httpOnly --secure
playwright-cli cookie-delete session_id
playwright-cli cookie-clear

# LocalStorage
playwright-cli localstorage-list
playwright-cli localstorage-get theme
playwright-cli localstorage-set theme dark
playwright-cli localstorage-delete theme
playwright-cli localstorage-clear

# SessionStorage
playwright-cli sessionstorage-list
playwright-cli sessionstorage-get step
playwright-cli sessionstorage-set step 3
playwright-cli sessionstorage-delete step
playwright-cli sessionstorage-clear
```

More: [references/storage-state.md](references/storage-state.md).

### Network

```bash
playwright-cli route "**/*.jpg" --status=404
playwright-cli route "https://api.example.com/**" --body='{"mock": true}'
playwright-cli route-list
playwright-cli unroute "**/*.jpg"
playwright-cli unroute
```

More: [references/request-mocking.md](references/request-mocking.md).

### DevTools

```bash
playwright-cli console
playwright-cli console warning
playwright-cli requests
playwright-cli request 5
playwright-cli run-code "async page => await page.context().grantPermissions(['geolocation'])"
playwright-cli run-code --filename=script.js
playwright-cli tracing-start
playwright-cli tracing-stop
playwright-cli video-start video.webm
playwright-cli video-chapter "Chapter Title" --description="Details" --duration=2000
playwright-cli video-stop

# annotate each subsequent action with a callout naming it and highlighting the target
playwright-cli video-show-actions --duration=600 --position=top-right
playwright-cli video-hide-actions

# launch the dashboard for UI review / design feedback
playwright-cli show --annotate

# generate a Playwright locator for an element from its ref or selector
playwright-cli generate-locator e5 --raw

# persistent highlight overlay for an element, optionally with custom style
playwright-cli highlight e5
playwright-cli highlight e5 --style="outline: 3px dashed red"
playwright-cli highlight e5 --hide
playwright-cli highlight --hide
```

## Raw output

The global `--raw` option strips page status, generated code, and
snapshot sections from the output, returning only the result value. Use
it to pipe command output into other tools. Commands that don't produce
output return nothing.

```bash
playwright-cli --raw eval "JSON.stringify(performance.timing)" | jq '.loadEventEnd - .navigationStart'
playwright-cli --raw eval "JSON.stringify([...document.querySelectorAll('a')].map(a => a.href))" > links.json
playwright-cli --raw snapshot > before.yml
playwright-cli click e5
playwright-cli --raw snapshot > after.yml
diff before.yml after.yml
TOKEN=$(playwright-cli --raw cookie-get session_id)
playwright-cli --raw localstorage-get theme
```

For structured output wrapping every reply as JSON, pass `--json`:

```bash
playwright-cli list --json
```

## Open / attach parameters

```bash
# DEFAULT browser is Lightpanda over CDP — prefer attach (see top of file):
LIGHTPANDA_DISABLE_TELEMETRY=true lightpanda serve --host 127.0.0.1 --port 9222 &
playwright-cli attach --cdp=ws://127.0.0.1:9222

# Connect to any running browser via a CDP endpoint
playwright-cli attach --cdp=http://localhost:9222
# Connect to a running Chrome or Edge by channel name
playwright-cli attach --cdp=chrome
playwright-cli attach --cdp=msedge
# Connect via the Playwright browser extension
playwright-cli attach --extension=chrome

# Full browsers (only when the user asks for one):
playwright-cli open --browser=chromium
playwright-cli open --browser=chrome
playwright-cli open --browser=firefox
playwright-cli open --browser=webkit
playwright-cli open --browser=msedge

# Persistent profile (by default the profile is in-memory)
playwright-cli open --persistent
playwright-cli open --profile=/path/to/profile

# Start with a config file
playwright-cli open --config=my-config.json

# Close / detach / delete
playwright-cli close
# detach leaves an attached external browser (e.g. Lightpanda) running
playwright-cli -s=default detach
playwright-cli delete-data
```

## Snapshots

After each command, `playwright-cli` provides a snapshot of the current
browser state.

```bash
> playwright-cli goto https://example.com
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
### Snapshot
[Snapshot](.playwright-cli/page-2026-02-14T19-22-42-679Z.yml)
```

You can take a snapshot on demand; options combine freely.

```bash
playwright-cli snapshot                         # timestamped file
playwright-cli snapshot --filename=after-click.yaml
playwright-cli snapshot "#main"                 # element subtree
playwright-cli snapshot --depth=4               # limit depth
playwright-cli snapshot e34                      # subtree of a ref
playwright-cli snapshot --boxes                  # include [box=x,y,width,height]
```

## Targeting elements

By default, use refs from the snapshot to interact with page elements.

```bash
playwright-cli snapshot       # get refs (e3, e15, …)
playwright-cli click e15
```

CSS selectors and Playwright locators also work:

```bash
playwright-cli click "#main > button.submit"
playwright-cli click "getByRole('button', { name: 'Submit' })"
playwright-cli click "getByTestId('submit-button')"
```

Reading attributes not shown in the snapshot:
[references/element-attributes.md](references/element-attributes.md).

## Browser sessions

```bash
# named session with persistent profile
playwright-cli -s=mysession open example.com --persistent
playwright-cli -s=mysession click e6
playwright-cli -s=mysession close
playwright-cli -s=mysession delete-data

playwright-cli list           # list sessions
playwright-cli close-all       # close all browsers
playwright-cli kill-all        # force-kill all browser processes
```

More: [references/session-management.md](references/session-management.md).

## Installing playwright-cli

If a project-local copy exists, prefer it:

```bash
npx --no-install playwright-cli --version
```

Otherwise install globally:

```bash
npm install -g @playwright/cli@latest
```

For installing the Lightpanda browser, see
[references/lightpanda.md](references/lightpanda.md) or run the bundled
[`scripts/install-lightpanda.sh`](scripts/install-lightpanda.sh).

## Examples

```bash
# Form submission (Lightpanda default)
lightpanda serve --host 127.0.0.1 --port 9222 &
playwright-cli attach --cdp=ws://127.0.0.1:9222
playwright-cli goto https://example.com/form
playwright-cli snapshot
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3
playwright-cli snapshot
playwright-cli close
```

```bash
# Debugging with DevTools
playwright-cli goto https://example.com
playwright-cli tracing-start
playwright-cli click e4
playwright-cli fill e7 "test"
playwright-cli console
playwright-cli requests
playwright-cli tracing-stop
playwright-cli close
```

## Specific tasks

* **Choosing / switching browsers, Lightpanda vs full browsers** [references/browsers.md](references/browsers.md)
* **Lightpanda: install, serve, attach, limits** [references/lightpanda.md](references/lightpanda.md)
* **Running and debugging Playwright tests** [references/playwright-tests.md](references/playwright-tests.md)
* **Request mocking** [references/request-mocking.md](references/request-mocking.md)
* **Running Playwright code** [references/running-code.md](references/running-code.md)
* **Browser session management** [references/session-management.md](references/session-management.md)
* **Spec-driven testing (plan / generate / heal)** [references/spec-driven-testing.md](references/spec-driven-testing.md)
* **Storage state (cookies, localStorage)** [references/storage-state.md](references/storage-state.md)
* **Test generation** [references/test-generation.md](references/test-generation.md)
* **Tracing** [references/tracing.md](references/tracing.md)
* **Video recording** [references/video-recording.md](references/video-recording.md)
* **Inspecting element attributes** [references/element-attributes.md](references/element-attributes.md)

---

The `playwright-cli` command reference and the `references/*.md` files
marked above (all except `browsers.md` and `lightpanda.md`) are adapted
from Microsoft's `playwright-cli` project, used under the Apache-2.0
license. See [NOTICE](NOTICE).
