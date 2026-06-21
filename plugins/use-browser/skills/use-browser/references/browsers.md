# Choosing and switching browsers

This skill drives browsers with `playwright-cli`. The **default browser
is Lightpanda**, used over the Chrome DevTools Protocol (CDP). Other
browsers are used **only when the user asks**.

## The rule

1. **Default to Lightpanda. Don't prompt.** When you need a browser,
   start `lightpanda serve` and `playwright-cli attach --cdp=ws://127.0.0.1:9222`
   (see [lightpanda.md](lightpanda.md)). Just do it — no question.
2. **Switch only on request.** If the user asks for a specific browser
   ("use Chrome", "open it in Firefox", "use a real browser"), or asks
   you to choose, switch to that browser with `playwright-cli open
   --browser=<name>`.
3. **Offer a choice when asked.** If the user asks "which browser can I
   use?" or wants to pick, present the options below. In Claude Code use
   the **AskUserQuestion** tool with **Lightpanda** preselected as the
   recommended default; elsewhere, ask in plain text.
4. **Fall back when Lightpanda can't render.** If a Lightpanda
   `goto`/`snapshot` errors or times out, stop retrying Lightpanda, tell
   the user, and offer Chromium (`playwright-cli open --browser=chromium`).

## Options to present

| Option | Engine | Command | Best for |
|---|---|---|---|
| **Lightpanda** ⭐ default | Lightpanda (custom) | `lightpanda serve …` + `playwright-cli attach --cdp=ws://127.0.0.1:9222` | Fast, low-memory scraping and automation; CI; simple/medium pages |
| Chromium | Chromium | `playwright-cli open --browser=chromium` | Heavy SPAs, anything Lightpanda can't render, full fidelity |
| Chrome | Chrome channel | `playwright-cli open --browser=chrome` | Behavior of real Google Chrome |
| Firefox | Gecko | `playwright-cli open --browser=firefox` | Cross-browser verification |
| WebKit | WebKit | `playwright-cli open --browser=webkit` | Safari-engine verification |
| Microsoft Edge | Edge channel | `playwright-cli open --browser=msedge` | Behavior of real Edge |

You can also attach to an already-running browser instead of launching
one:

```bash
playwright-cli attach --cdp=ws://127.0.0.1:9222   # Lightpanda (default)
playwright-cli attach --cdp=http://localhost:9222  # any CDP endpoint
playwright-cli attach --cdp=chrome                 # running Chrome by channel
playwright-cli attach --cdp=msedge                 # running Edge by channel
playwright-cli attach --extension=chrome           # via Playwright extension
```

## Lightpanda vs full browsers — tradeoffs

**Lightpanda** is a purpose-built headless browser for AI and automation.
It is dramatically faster and lighter than Chromium (no rendering/paint,
much lower RAM), which makes it ideal for scraping, navigation, and
DOM/automation work at scale. It speaks CDP, so `playwright-cli attach
--cdp=…` and Playwright's `chromium.connectOverCDP(...)` both work.

Because it is lightweight, Lightpanda implements a **subset** of full
browser behavior. Expect to fall back to Chromium when:

- A page is a heavy single-page app that needs full rendering or
  unsupported web APIs.
- Navigation fails with `SslConnectError` / a TLS error (some
  restricted, proxied, or sandboxed networks block Lightpanda's outbound
  TLS even when `curl` works — see [lightpanda.md](lightpanda.md)).
- A `goto` hangs until timeout, or `snapshot` comes back empty.
- You need pixel-accurate screenshots, video, or visual regression.

For those, a full browser (Chromium first) is the right tool. Everything
else in this skill — refs, snapshots, clicks, fills, storage, network
mocking, tracing — works the same regardless of which browser is behind
the session.

## Switching mid-task

`playwright-cli` keeps a session. To move from Lightpanda to a full
browser:

```bash
playwright-cli close              # close the Lightpanda-backed session
playwright-cli open --browser=chromium https://example.com
```

Or run them side by side with named sessions (`-s=<name>`); see
[session-management.md](session-management.md).
