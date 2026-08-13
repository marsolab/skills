---
name: go-dev
description: >-
  Go development for backends, microservices, APIs, CLI tools, daemons,
  workers, data pipelines, and libraries. Use when writing, reviewing,
  refactoring, debugging, or designing Go code; working with .go files,
  go.mod, the Go toolchain or standard library; or handling Chi, sqlc,
  goose, slog, goroutines, channels, context, generics, linting, or tests.
  Routes work to focused sibling Go skills. Skip tasks with no Go component.
metadata:
  version: "2.1.1"
  tags: "go, golang, umbrella"
---

# Go Dev (umbrella)

This skill exists to make sure the agent has Go context loaded as soon as
the conversation involves Go. It is intentionally short. Its job is to
route: pick the focused sibling skill(s) that own the deep reference
material for the task at hand.

## Routing directives — load focused skills

For each task signal below, load the named sibling skill before writing code
when it is installed. Do not answer Go questions from this umbrella's fallback
cheat sheet if an available sibling owns the topic.

- Naming, packages, generics, interfaces, iterators → `go-style`
- Wrapping errors, `errors.Is` / `errors.As` / `errors.Join`, log-or-return → `go-errors`
- Goroutines, channels, `context`, `errgroup`, `sync` → `go-concurrency`
- `log/slog`, structured logging, observability → `go-logging`
- Tests, `t.Helper`, `httptest`, table-driven, fixtures → `go-testing`
- HTTP services, Chi router, middleware, graceful shutdown → `go-http`
- CLI tools, `flag.NewFlagSet`, subcommands, exit codes → `go-cli`
- sqlc, goose migrations, transactions, `database/sql` → `go-sql`
- `golangci-lint`, `.golangci.yml`, `gofmt`, `goimports` → `go-lint`

If the task spans multiple rows, load two or three siblings. If no matching
sibling is installed, continue with the fallback cheat sheet below.

## Fallback cheat sheet (only if no sibling applies)

### NAMING

- Packages: lowercase, singular, no underscores
- Variables: short names for short scope, longer for wider scope
- Exported: PascalCase; unexported: camelCase
- Acronyms: consistent case (URL not Url, ID not Id)
- Getters: no Get prefix; setters: Set prefix

### STRUCTURE

- Check returned errors immediately after the call
- Return early with guard clauses; keep the success path left-aligned
- Group imports: stdlib, external, internal
- Define interfaces at the consumption site; keep them 1–3 methods
- Accept interfaces, return concrete types

### MODERN GO (1.18+)

- Generics: use for data structures and utilities, not behavior abstraction
- `log/slog`: pass as a dependency; `InfoContext` / `ErrorContext`; JSON in prod
- `errors.Join`: combine multiple errors; supports `errors.Is` / `errors.As`
- Iterators (`iter.Seq` / `iter.Seq2`): lazy, composable pipelines
- Range-over-int (`for i := range n`) since Go 1.22
- Prefer `slices` / `maps` / `cmp` over hand-rolled helpers

### CRITICAL PITFALLS

- Loop variable capture in closures (pre-1.22): pass to closure or shadow
- Nil interface check: interface with a nil concrete value is NOT nil
- Variable shadowing inside if/for: use `=` not `:=` when reassigning
- `defer` in a loop: wrap the body in a closure for per-iteration cleanup
- Writes to a nil map: always initialize with `make()`

## MCP

Use Context7 MCP to fetch up-to-date library docs when working with
third-party Go packages.
