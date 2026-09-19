---
name: go-dev
description: >-
  Index for Go development. Triggers on any Go or Golang task like writing,
  reviewing, or refactoring `.go` files, `go.mod`, `go test`, or anything
  involving Go tools (golangci-lint, sqlc, goose).
version: 1.0.0
tags:
  - go
  - golang
  - backend
  - cli
  - api
  - grpc
  - server
---

# Go Development

Write Go that is readable, maintainable, and production-ready. This skill
is the entry point — load it for any Go task and let it route you to the
right topic skill below.

## Topic skills

When the task narrows to a specific area, the matching topic skill loads
its own focused reference:

- **go-errors** — `if err != nil`, `%w` vs `%v`, `errors.Join`,
  `errors.Is/As`, error string style, no panic in libraries.
- **go-testing** — table-driven tests, `t.Helper`, `t.Run`,
  integration-test gating, benchmarks, useful failure messages.
- **go-concurrency** — goroutine lifecycle, `context.Context` first
  parameter, `sync.WaitGroup`, channel buffer sizing, iterators
  (`iter.Seq`), range-over-int, loop-variable capture.
- **go-types** — interfaces (consumer-defined, accept-iface
  return-concrete, small surface), generics (when/when-not),
  `cmp.Ordered`, `slices`/`maps`.
- **go-logging** — `log/slog` patterns: dependency injection,
  `InfoContext`/`ErrorContext`, `slog.With`, `slog.Group`, `LogValuer`,
  JSON vs text handler.
- **go-databases** — sqlc + goose workflow, query annotations,
  `Querier` interface for tests, migration patterns.
- **go-services** — HTTP services with Chi, graceful shutdown, flag/env
  config precedence, CLI tools with `flag.NewFlagSet`.

## MCP

Use Context7 MCP to fetch current docs for Go libraries (Chi, sqlc,
goose, etc.) — your training data may not reflect recent releases.

## Libraries (defaults across all skills)

- HTTP routing: [Chi](https://github.com/go-chi/chi).
- Logging: `log/slog` (stdlib since Go 1.21).
- Configuration: flags or env vars — no external config frameworks.
- Database access: [sqlc](https://sqlc.dev/) (typesafe SQL → Go).
- Migrations: [goose](https://github.com/pressly/goose).
- Testing: stdlib `testing`. No third-party assertion libraries.

Prefer well-maintained, zero-dependency libraries from awesome-go.

## Core idioms (always)

**Naming.** Packages: lowercase, singular, no underscores. Avoid
`util`/`common`/`misc`/`api`/`types`. Getters omit `Get`; setters use
`Set`. Acronyms keep consistent case (`URL`, `appID`, `ServeHTTP`).
Constants in mixedCaps, not `SCREAMING_CASE`.

**Variable length scales with scope.** Short names (`i`, `v`) for tight
loops; descriptive names when declaration and use are far apart. Use
`var` for zero-value declarations, `:=` for initializations.

**Imports** are grouped using `goimports` automatically.

**Structure.** Return early with guard clauses. Keep the success path
left-aligned. Single struct-literal initialization rather than multiple
field assignments that can leave objects half-built.

**Project layout.** Start as a few files in `package main`. When
complexity demands it, use `cmd/<binary>/main.go` for entry points and
`internal/` for private code. Don't impose `cmd/pkg` prematurely.

**Doc comments** start with the symbol name and are complete sentences.
Comment exported symbols. Document the *why*, not the obvious *what*.

## Linting

Set up `golangci-lint` with the bundled config:

```bash
./scripts/setup_golangci_lint.sh /path/to/project
```

This copies `assets/golangci.yml` into the project and installs a pre-commit hook. 
Then:

```bash
golangci-lint run ./...        # run all linters
golangci-lint run --fix ./...  # auto-fix
```

Run `goimports` before committing to keep imports formatted.

The bundled config enables errcheck, govet, staticcheck, errorlint,
gosec, prealloc, revive, gocognit, gocyclo, wsl_v5, and more — strict
enough to flag real issues without drowning in noise.
