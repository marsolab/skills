# Go development workflow

Use this guide for module/toolchain changes, package design, debugging,
profiling, or building a Go application or library. Technical implementations
live in the [topic index](../../SKILL.md#topic-guides).

## Establish the module and toolchain

Inspect `go.mod`, `go.sum`, `go.work` where present, CI, and local build scripts.
The `go` directive governs language compatibility; a `toolchain` directive may
request a different compiler. Preserve both unless the task calls for an upgrade.

```bash
go version
go env GOMOD GOWORK GOOS GOARCH CGO_ENABLED
go list ./...
go list -m all
```

Run module commands in the module they affect. In a multi-module workspace,
identify every changed module and the workspace's test/build entrypoints.
Do not assume that root-level `go test ./...` covers all modules in `go.work`.

For dependency changes, choose a version deliberately and inspect the resulting
module diff. `go mod tidy` can add and remove requirements unrelated to the
requested dependency; review those changes rather than accepting them blindly.

```bash
go get example.com/library@v1.2.3
go mod tidy
go mod verify
git diff -- go.mod go.sum
```

Commit `go.sum` with module changes. Keep local `replace` directives and local
workspace paths out of distributable libraries unless the repository requires
them. Use vendoring only where the project has chosen that distribution model.

## Package and API boundaries

Keep small programs small. Introduce packages for cohesive responsibilities,
reuse, or separate dependency ownership rather than copying an elaborate layout.
For an application with several entrypoints, a useful shape is:

```text
project/
├── cmd/server/main.go
├── cmd/tool/main.go
├── internal/user/
├── internal/storage/
├── go.mod
└── go.sum
```

Keep configuration and wiring in the entrypoint. Domain code accepts explicit
dependencies and returns domain values/errors; adapters translate HTTP, SQL,
CLI, and log concerns. Use [style](../style/guide.md) for interface and naming
decisions. Generated sqlc code is an adapter, not the public domain API.

For libraries, document zero-value behavior, ownership, cancellation, concurrent
safety, and error contracts. Changing exported functions, interfaces, sentinel
errors, or serialization is an API change even when the code still compiles.

## Implement and review

Trace the caller, state transitions, and existing tests before editing. Include
validation, successful behavior, and relevant failure paths in the change.
Avoid speculative abstractions; create an interface where a consumer needs a
substitutable behavior or a boundary genuinely needs one.

- Input boundary: validate format, size, ranges, and authorization assumptions.
- Resource boundary: identify who owns files, response bodies, transactions,
  connections, timers, and shutdown.
- Concurrency boundary: identify shared state, cancellation, bounded work, and
  who waits for workers.
- Error boundary: preserve useful matching and translate private implementation
  errors before returning to users.
- Data boundary: prefer parameterized queries and explicit DTO/domain mappings.

Use the [HTTP](../http/guide.md), [CLI](../cli/guide.md),
[SQL](../sql/guide.md), and [concurrency](../concurrency/guide.md) guides as
needed. Follow repository conventions before adding dependencies.

## Debugging from evidence

Reproduce a reported failure with the smallest representative command or test.
Capture expected behavior, actual behavior, toolchain, platform, and relevant
configuration. Inspect errors and stack traces before proposing a fix.

```bash
go test ./internal/user -run '^TestCreateUser$' -count=1 -v
go test -race ./internal/user
go test ./internal/user -run '^TestCreateUser$' -count=20
```

Use repeated runs only to investigate nondeterminism. For deadlocks or worker
leaks, inspect goroutine stacks and every blocking operation's cancellation and
termination path. A timeout proves the test stalled; it does not identify the
cause. For SQL failures, verify pool limits, context deadlines, and transaction
ownership before tuning them.

## Profiling and performance

Measure a real bottleneck. Keep workload, compiler, hardware, and configuration
comparable; distinguish throughput, tail latency, allocations, and retained heap.

```bash
go test ./internal/user -run '^$' -bench . -benchmem -count=5
go test ./internal/user -run '^$' -bench . -cpuprofile cpu.out
go test ./internal/user -run '^$' -bench . -memprofile heap.out
go tool pprof cpu.out
go test ./internal/user -trace trace.out
go tool trace trace.out
```

Read [performance](../style/performance.md) and
[benchmarking](../testing/perf-and-parallel.md) for allocation patterns and
test setup. Keep diagnostics access limited to the intended development or
operations surface when adding `net/http/pprof` to an application.

## Build and release checks

Use the repository's supported platforms and CGO settings. Cross-compilation
with CGO may need a target compiler; `CGO_ENABLED=0` is valid only when the
application and dependencies support it. Build into an output directory rather
than overwriting unrelated files in the checkout.

```bash
go build ./...
go build -o ./dist/tool ./cmd/tool
```

Keep application version injection and packaging aligned with the repository's
existing process. Report compiler checks, tests, artifact creation, deployment,
and runtime confirmation as separate results. Verify the actual target before
claiming cross-platform support.

## Finish with the relevant checks

Format changed Go files, run focused tests, then the module's normal gates.
For concurrent changes include `-race` where supported. Run integration tests
against an isolated dependency and record required configuration or skips.
For SQL changes regenerate the output and review it together with migrations.

Read [testing](../testing/guide.md) and [lint](../lint/guide.md) for the detailed
commands and reusable helpers. Do not treat successful compilation as proof of
behavior or skipped integration tests as exercised coverage.
