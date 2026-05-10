---
name: go-testing
description: >-
  Idiomatic Go testing with the stdlib `testing` package. ALWAYS use this
  skill when writing or reviewing Go tests — table-driven tests with
  `map[string]testCase` or `[]struct{name string; ...}`, `t.Run` subtests,
  `t.Helper()` for assertion helpers, `t.Cleanup`, `t.Parallel`, integration
  test gating with environment variables, useful failure messages
  (`got %v, want %v`), benchmarks (`testing.B`), fuzz tests, and the
  third-party-frameworks debate (testify, ginkgo). Pair with go-sql for
  testing DB code with sqlc's `Querier` interface, go-http for `httptest`
  patterns, and go-concurrency for race-detector usage.
version: 1.0.0
tags:
  - go
  - golang
  - testing
  - table-driven-tests
  - benchmarks
---

# Go Testing

Use the standard library `testing` package. Skip the assertion DSLs —
they trade tiny syntactic wins for cognitive overhead and worse failure
messages.

For the comprehensive reference, see `references/testing.md`.

## Table-driven with named cases

`map[string]testCase` makes the case name the subtest name automatically:

```go
func TestProcess(t *testing.T) {
    type testCase struct {
        input   string
        want    string
        wantErr bool
    }

    tests := map[string]testCase{
        "valid input": {
            input: "hello",
            want:  "HELLO",
        },
        "empty input returns error": {
            input:   "",
            wantErr: true,
        },
    }

    for name, tc := range tests {
        t.Run(name, func(t *testing.T) {
            got, err := Process(tc.input)
            if (err != nil) != tc.wantErr {
                t.Fatalf("Process() error = %v, wantErr %v", err, tc.wantErr)
            }
            if got != tc.want {
                t.Errorf("Process() = %q, want %q", got, tc.want)
            }
        })
    }
}
```

The `[]struct{name string; ...}` form is also fine; choose one and stay
consistent in a package.

## Helpers must call t.Helper()

```go
func mustOpen(t *testing.T, path string) *os.File {
    t.Helper()
    f, err := os.Open(path)
    if err != nil {
        t.Fatalf("open %s: %v", path, err)
    }
    t.Cleanup(func() { f.Close() })
    return f
}
```

`t.Helper()` makes failure line numbers point at the caller. `t.Cleanup`
runs in LIFO order at the end of the test (or subtest) and is the
preferred replacement for `defer` in test setup helpers.

## Failure messages must be actionable

```go
// GOOD
if got != want {
    t.Errorf("Square(%d) = %d, want %d", input, got, want)
}

// BAD
if got != want {
    t.Error("test failed")
}
```

Convention: `got %v, want %v` — `got` first, then `want`. With
`require`-style libraries the order is `(want, got)`; pick whichever
matches your tooling and don't mix them.

## t.Fatal vs t.Error

- `t.Fatal` / `t.Fatalf` — stop this test immediately. Use when later
  assertions can't run (setup failure, nil result you'd dereference).
- `t.Error` / `t.Errorf` — record failure, keep running. Use when later
  assertions still produce useful information.

## Integration tests: env vars, not build tags

Build tags hide tests; environment variables surface them in the
`t.Skip` output:

```go
func TestDatabaseIntegration(t *testing.T) {
    dsn := os.Getenv("TEST_DATABASE_URL")
    if dsn == "" {
        t.Skip("set TEST_DATABASE_URL to run this test")
    }
    db, err := sql.Open("postgres", dsn)
    // ...
}
```

`go test ./...` then runs unit tests cleanly while skipping integration
ones — and the skip lines tell you what to set.

## Parallel tests

Mark independent tests with `t.Parallel()` to use multiple cores. Inside
a table-driven loop, capture the case variable to avoid the loop-var
capture bug (Go 1.22+ fixes the loop case but `t.Parallel` still benefits
from explicit capture for clarity):

```go
for name, tc := range tests {
    name, tc := name, tc
    t.Run(name, func(t *testing.T) {
        t.Parallel()
        // ...
    })
}
```

## Benchmarks

```go
func BenchmarkProcess(b *testing.B) {
    data := generateTestData()
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```

Run with `go test -bench=. -benchmem`. Use `b.ReportAllocs()` and
`b.ResetTimer()` to keep setup out of the measurement.

## Race detector

Run `go test -race ./...` regularly — it catches concurrent map writes,
unsynchronized field access, and other heisenbugs. CI should always run
with `-race`.

## Third-party frameworks

- Google bans testify and ginkgo internally; the stdlib suffices.
- GitLab permits testify with `(want, got)` argument order.
- Peter Bourgon: testing DSLs increase cognitive burden.

Default to the stdlib. Reach for `testify/require` only if your team has
already standardized on it.

## When to load a sibling skill

| Task | Skill |
|---|---|
| Mocking a sqlc-generated `Querier` | go-sql |
| Testing HTTP handlers with `httptest` | go-http |
| Testing concurrent code, race detector | go-concurrency |
| Asserting on wrapped errors with `errors.Is`/`errors.As` | go-errors |
| General Go idioms and naming | go-style |
