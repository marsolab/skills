---
name: go-testing
description: >-
  Idiomatic Go testing patterns. Triggers when the user is writing,
  reviewing, or fixing Go tests — `_test.go` files, `go test`, table-driven
  tests, subtests with `t.Run`, test helpers with `t.Helper()`, integration
  test gating, benchmarks, fuzz tests, fixtures, or `testing.T`/`testing.B`
  usage. Also load when the user asks about test coverage, parallel tests,
  failure messages, mocking, or "how do I test this Go function?"
version: 1.0.0
tags:
  - go
  - golang
  - testing
  - tests
  - benchmarks
---

# Go Testing

Tests are contracts written in code. Use the stdlib `testing` package.
No third-party assertion frameworks unless the project already uses
one — testify is tolerable, ginkgo is not.

For long-form rationale and edge cases, read `references/testing.md`.

## Table-driven tests

The Go standard. Two forms — pick by readability:

**Map form** (descriptive names, no separate `name` field):

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

## Failure messages

Test failures should identify what went wrong, with what input, what
was expected, what was received:

```go
// GOOD
if got != want {
    t.Errorf("Square(%d) = %d; want %d", input, got, want)
}

// BAD
if got != want {
    t.Error("test failed")
}
```

Convention: `got, want` order. Format: `Errorf("got %v, want %v", got,
want)`.

## t.Fatal vs t.Error

- `t.Fatal*` — stop this test (e.g., setup failed, no point checking
  outputs).
- `t.Error*` — record failure but keep going (e.g., one of several
  assertions in a single case).

In a table test loop, `t.Fatal` inside a subtest stops only that
subtest, which is usually what you want.

## t.Helper() in helpers

Helper functions should call `t.Helper()` so failure line numbers
point to the actual test, not the helper:

```go
func assertNoError(t *testing.T, err error) {
    t.Helper()
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
}
```

Without `t.Helper()`, failures point to the line inside `assertNoError`
— useless when the same helper is called from many tests.

## Integration tests: env-var gates, not build tags

Build tags hide tests and are non-discoverable. Use environment
variables instead — they show up in test output as skips:

```go
// GOOD: discoverable skip
func TestDatabaseIntegration(t *testing.T) {
    dsn := os.Getenv("TEST_DATABASE_URL")
    if dsn == "" {
        t.Skip("set TEST_DATABASE_URL to run this test")
    }
    db, err := sql.Open("postgres", dsn)
    // ...
}

// AVOID: build tag silently excludes the test from default runs
// +build integration
func TestDatabaseIntegration(t *testing.T) { /* ... */ }
```

`t.Skip` surfaces in `go test -v` output, making it obvious when
tests are skipped and why.

## Parallel tests

Mark independent subtests with `t.Parallel()`:

```go
for name, tc := range tests {
    tc := tc // shadow for closure capture (pre-Go 1.22)
    t.Run(name, func(t *testing.T) {
        t.Parallel()
        // ...
    })
}
```

In Go 1.22+ the loop-variable shadow is no longer needed for `for
range` — but it's still defensive against older Go versions and other
closure capture cases. See `go-concurrency` skill for the full rule.

## Benchmarks

Use `*testing.B`. `b.ResetTimer()` after expensive setup. Don't time
data generation:

```go
func BenchmarkProcess(b *testing.B) {
    data := generateTestData() // not timed
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```

Run with `go test -bench=. -benchmem`. Don't optimize without a
benchmark — most "performance fixes" make code worse without
measurable gain.

## Fixtures with testdata/

Go reserves the directory name `testdata/` — `go build` ignores it.
Put fixture files there and read them with `os.ReadFile`:

```go
golden, err := os.ReadFile("testdata/expected.json")
```

Update fixtures behind a flag for golden-file tests:

```go
var update = flag.Bool("update", false, "update golden files")

if *update {
    os.WriteFile("testdata/expected.json", got, 0o644)
}
```

## Pitfalls in tests

- **Loop variable capture in subtests**: pre-Go 1.22, shadow with
  `tc := tc` before `t.Parallel()`. See `go-concurrency`.
- **Deferred cleanup runs at function end**, not per loop iteration.
  If you need per-case cleanup, use `t.Cleanup()` inside the subtest
  closure.
- **`t.Run` inside loops** — fine. But mixing parallel and serial
  subtests with shared state needs explicit coordination.

## Quick reference

- Table-driven with `map[string]testCase` (or named-struct slice).
- Use `t.Run(name, ...)` for subtests.
- Format failures: `got X, want Y`.
- Helpers call `t.Helper()`.
- Integration tests gate on `os.Getenv`, never build tags.
- `t.Parallel()` for independent subtests.
- Benchmarks: `b.ResetTimer()` after setup; verify gains before
  optimizing.
