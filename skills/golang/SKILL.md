---
name: golang
description: >-
  Build, review, refactor, debug, and test Go applications and libraries.
  Use for .go files, go.mod, Go tooling, HTTP services, CLI tools, SQL data
  access, concurrency, error handling, structured logging, generics, tests,
  benchmarks, or linting. Includes detailed guides for idiomatic Go, Chi,
  sqlc, goose, slog, and golangci-lint. Skip tasks with no Go component.
metadata:
  version: "1.0.0"
  tags: "go, golang, backend, cli, concurrency, sql, testing, tooling"
---

# Golang

Use this skill for the complete Go development workflow. Detailed guidance,
examples, and reusable tooling live inside this directory. Read the guide for
the task and follow its links when more detail is needed; independent Go
skills are not required.

## Start with the repository

1. Read its instructions, `go.mod`, any `go.work`, and the affected packages.
   Check the declared Go version, dependencies, generated code, existing test
   style, and CI commands before choosing language features or tools.
1. Read [development](references/development/guide.md) for module work,
   debugging, architecture, dependency changes, or build/release questions.
   Select the technical guides below for the concrete task.
1. Preserve the existing public API, architecture, and conventions unless the
   requested change needs them to move. Build a coherent change that satisfies
   the requested behavior.
1. Verify observable behavior with the relevant tests and tooling. Report what
   actually ran, including integration tests that skipped and race checks
   unavailable on the target platform.

## Topic guides

| Topic | Read when working on |
| --- | --- |
| Development | [Modules and tools](references/development/guide.md) |
| Style | [Idioms and language features](references/style/guide.md) |
| Errors | [Matching and cleanup](references/errors/guide.md) |
| Concurrency | [Workers and cancellation](references/concurrency/guide.md) |
| Logging | [slog and request attributes](references/logging/guide.md) |
| Testing | [Tests, fuzzing, benchmarks](references/testing/guide.md) |
| HTTP | [Services and clients](references/http/guide.md) |
| CLI | [Flags, help, exit codes](references/cli/guide.md) |
| SQL | [sqlc, goose, transactions](references/sql/guide.md) |
| Lint | [Formatting and analyzers](references/lint/guide.md) |

For work spanning topics, combine the relevant guides. For example:

- PostgreSQL HTTP API: HTTP + SQL + errors + testing; logging for request
  diagnostics and concurrency for lifecycle coordination.
- File-processing CLI: CLI + errors + testing; style for configuration and
  package boundaries.
- Concurrent cache or worker: concurrency + style + testing; errors for
  failure propagation and logging for operational events.

Each topic's `guide.md` contains its working patterns and links to deeper
references. The [style index](references/style/idioms.md) separates naming,
packages, interfaces, documentation, performance, configuration, modules,
design choices, and modern language features into individual files.

## Shared engineering rules

### Structure and dependencies

- Start with a few packages; add `cmd/` and `internal/` where actual boundaries
  require them. Keep domain logic independent of HTTP, CLI, and SQL adapters.
- Define small interfaces at the consumer. Return concrete types unless the
  API intentionally abstracts interchangeable implementations.
- Configure dependencies in the application entrypoint and pass them through
  constructors. Avoid hidden globals, package-level flags, and initialization
  side effects.
- Prefer the standard library where it fits. For new projects, Chi, sqlc,
  goose, and `slog` are the detailed defaults in this skill. Keep an existing
  stack when it already meets the task.
- Check third-party APIs against the version in `go.mod`; use official docs or
  a documentation tool already available in the environment. No MCP is required.

### Errors and resources

- Check returned errors promptly and wrap them with operation context. Use
  `%w` when callers need `errors.Is` or `errors.As`; translate infrastructure
  errors into domain errors at the boundary.
- Handle an error once: return it to an owner or handle it here. Do not log and
  return the same failure through several layers.
- Check `Close`, `Flush`, and `Write` errors. A named error return and deferred
  `errors.Join` preserve both an operation failure and a cleanup failure. See
  [deferred cleanup](references/errors/guide.md#deferred-cleanup-capture-the-close-error).
- Keep transactions short. Roll back uncommitted work and distinguish expected
  already-closed errors from real rollback failures.
- Validate external input and use parameterized SQL. Keep secrets and internal
  errors out of responses and logs.

### Concurrency and lifecycle

- Give every goroutine a termination condition and an owner that waits for it.
  Propagate cancellation into blocking work; cancellation alone does not join
  the worker.
- Pass `context.Context` as the first argument to request-scoped I/O. Cancel
  contexts you create and keep cancellation scopes explicit.
- Bound fan-out and queues to match capacity. The producer coordinator closes
  channels after all senders stop; consumers handle closed channels explicitly.
- Protect shared mutable state and do not copy values containing locks. Prefer
  synchronous library APIs so callers control concurrency.
- Wait for HTTP shutdown and background work before returning from the process
  entrypoint. Use a fresh timeout context for shutdown after cancellation.

### Tests and operational proof

- Test contracts, boundary conditions, and failure paths. Use narrow fakes for
  consumer interfaces and real dependencies for integration claims.
- Use stdlib `testing` in projects without extra dependencies. For new tests
  where an assertion library is wanted, this skill documents `go-testdeep`.
  Follow the repository's existing test stack during unrelated changes.
- Keep test helpers explicit with `t.Helper`, `t.Cleanup`, and `t.TempDir`.
  Parallel tests must not share mutable globals, environment, or working dir.
- Use race checks for concurrent code and benchmarks/profiles before optimizing.
  A passing race run covers exercised paths, not every possible execution.
- Keep unit, integration, CI, deployment, and production evidence distinct.

## Go version compatibility

Use the version declared by the project, not the newest installed compiler.

| Feature | Minimum Go version |
| --- | --- |
| Type parameters and `any` | 1.18 |
| `errors.Join` | 1.20 |
| `log/slog`, `slices`, `maps`, `cmp` | 1.21 |
| Range over integers, per-iteration variables declared by loops | 1.22 |
| `iter.Seq`, `iter.Seq2`, range over functions | 1.23 |
| `testing.B.Loop`, `sync.WaitGroup.Go` | 1.24 and 1.25 respectively |

When a feature is unavailable, use the established compatible pattern rather
than changing `go.mod` as a side effect. Timer behavior, loop variables, and
HTTP transport details also depend on the project/toolchain version.

## Reusable tooling

Run helpers from the target Go project's root. Resolve their absolute paths
from this skill's installed location; none requires a host-specific alias.

- [Set up lint configuration](scripts/lint/setup_golangci_lint.sh): copies the
  bundled v2 configuration. Existing configuration and hooks require an
  explicit replacement flag; Git-hook installation is opt-in.
- [Run lint](scripts/lint/run_lint.sh): invokes `golangci-lint run ./...` and
  preserves its exit status.
- [Run tests](scripts/testing/run_tests.sh): invokes
  `go test -race -cover ./...` and preserves its exit status.
- [Lint configuration](assets/lint/golangci.yml): a configurable starting point;
  align the Go version and enabled checks with the target repository.

Typical direct checks, scoped to the change:

```bash
gofmt -l .
go vet ./...
go test ./...
go test -race ./...
golangci-lint run ./...
```

Use the repository's commands when they differ. Tool installation, module
updates, SQL generation, formatting, and optional hooks are task-driven actions;
loading this skill alone does not run them.
