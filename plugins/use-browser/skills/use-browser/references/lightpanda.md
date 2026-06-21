# Lightpanda: install, serve, attach, limits

[Lightpanda](https://lightpanda.io) is the default browser for this
skill — a fast, low-memory headless browser for AI and automation that
speaks the Chrome DevTools Protocol (CDP). `playwright-cli` drives it by
attaching to its CDP server.

## Install

Easiest: run the bundled script (idempotent — skips if already
installed):

```bash
scripts/install-lightpanda.sh
```

It uses Lightpanda's official one-liner under the hood:

```bash
# Linux / macOS — requires curl, jq, and sha256sum (or shasum)
curl -fsSL https://pkg.lightpanda.io/install.sh | bash
```

Pin a specific release instead of the latest nightly:

```bash
curl -fsSL https://pkg.lightpanda.io/install.sh | bash -s "v0.2.5"
```

Direct binary download (Apple Silicon macOS — there is no Intel-mac
build; use Docker or build from source on Intel):

```bash
curl -L -o lightpanda \
  https://github.com/lightpanda-io/browser/releases/download/nightly/lightpanda-aarch64-macos
chmod +x ./lightpanda
```

Linux x86_64 direct binary (also the WSL2 path on Windows):

```bash
curl -L -o lightpanda \
  https://github.com/lightpanda-io/browser/releases/download/nightly/lightpanda-x86_64-linux
chmod +x ./lightpanda
```

Homebrew also packages it (`lightpanda`). Verify the install:

```bash
lightpanda version
```

> Note: `lightpanda` has no `--version` flag — use the `version`
> subcommand. Other subcommands: `serve`, `fetch`, `mcp`, `help`.

### Telemetry

Lightpanda collects usage telemetry by default. Disable it by exporting:

```bash
export LIGHTPANDA_DISABLE_TELEMETRY=true
```

The bundled `serve` examples set this inline.

## Run the CDP server

```bash
LIGHTPANDA_DISABLE_TELEMETRY=true lightpanda serve --host 127.0.0.1 --port 9222 &
```

`serve` options (defaults shown):

| Flag | Default | Meaning |
|---|---|---|
| `--host <HOST>` | `127.0.0.1` | Listen address |
| `--port <INT>` | `9222` | Listen port |
| `--advertise-host <HOST>` | `--host` | Host advertised in `/json/version` (use when `--host 0.0.0.0`) |
| `--cdp-max-connections <INT>` | `16` | Max simultaneous CDP connections |
| `--cookie <PATH>` | none | Load cookies from a JSON file (read-only) |

Common options (also valid on `fetch`): `--obey-robots`,
`--disable-subframes`, `--disable-workers`, and
`--insecure-disable-tls-host-verification` (disables TLS host
verification — only with understood risk).

The endpoint is a CDP WebSocket. Check it is up:

```bash
curl -fsS http://127.0.0.1:9222/json/version
# {"Browser":"Lightpanda/1.0","Protocol-Version":"1.3",
#  "webSocketDebuggerUrl":"ws://127.0.0.1:9222/"}
```

## Attach with playwright-cli

```bash
playwright-cli attach --cdp=ws://127.0.0.1:9222
# then drive normally:
playwright-cli goto https://example.com
playwright-cli snapshot
playwright-cli close
```

Equivalent raw Playwright (for reference / custom scripts):

```js
import { chromium } from 'playwright-core';
const browser = await chromium.connectOverCDP('ws://127.0.0.1:9222');
const context = await browser.newContext({});
const page = await context.newPage();
await page.goto('https://example.com/');
console.log(await page.title());
await browser.close();
```

## One-shot fetch (no playwright-cli)

For quick scraping without a session, Lightpanda can dump a page itself:

```bash
lightpanda fetch https://example.com --dump markdown
lightpanda fetch https://example.com --dump semantic_tree_text --strip-mode ui
lightpanda fetch https://example.com --json     # status + content as JSON
```

## Cloud (optional)

Lightpanda offers a hosted CDP endpoint; connect with a token instead of
running `serve` locally:

```js
const browser = await chromium.connectOverCDP(
  'wss://euwest.cloud.lightpanda.io/ws?token=' + process.env.LPD_TOKEN
);
```

## Limits and known issues

Lightpanda implements a **subset** of full-browser behavior. Fall back to
Chromium (see [browsers.md](browsers.md)) when:

- **`SslConnectError` on navigation.** Lightpanda's outbound TLS fails.
  This happens in some restricted, proxied, or sandboxed networks (where
  `curl` may still work because it is allowlisted or uses the proxy).
  `--insecure-disable-tls-host-verification` addresses *host
  verification* failures, but not a blocked/failed TLS *connection* —
  if `lightpanda fetch https://… --json` returns `"http_status":0`, the
  connection itself isn't getting through; use a full browser.
- **Plain `http://` URLs** may report `UnsupportedProtocol`; prefer
  `https://`.
- **Navigation hangs to timeout** or **`snapshot` returns empty** — the
  page likely relies on rendering or web APIs Lightpanda doesn't support.
- You need **pixel-accurate screenshots, video, or visual regression**.

When you hit any of these, stop retrying Lightpanda, tell the user, and
offer `playwright-cli open --browser=chromium`.
