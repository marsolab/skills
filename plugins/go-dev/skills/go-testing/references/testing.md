# Go Testing — Deep Reference

Long-form rationale and edge cases behind the rules in `SKILL.md`.

---

## Use table-driven tests with named fields

Table-driven tests are the Go standard for comprehensive coverage with
minimal duplication:

```go
func TestParseHost(t *testing.T) {
    tests := []struct {
        name         string
        input        string
        expectedHost string
        expectedPort string
        expectedErr  bool
    }{
        {
            name:         "host and port",
            input:        "example.com:8080",
            expectedHost: "example.com",
            expectedPort: "8080",
        },
        {
            name:         "host only",
            input:        "example.com",
            expectedHost: "example.com",
            expectedPort: "",
        },
        {
            name:        "invalid format",
            input:       ":::invalid",
            expectedErr: true,
        },
    }

    for _, tc := range tests {
        t.Run(tc.name, func(t *testing.T) {
            host, port, err := ParseHost(tc.input)
            if tc.expectedErr {
                if err == nil {
                    t.Fatal("expected error, got nil")
                }
                return
            }
            if err != nil {
                t.Fatalf("unexpected error: %v", err)
            }
            if host != tc.expectedHost {
                t.Errorf("host = %q, want %q", host, tc.expectedHost)
            }
            if port != tc.expectedPort {
                t.Errorf("port = %q, want %q", port, tc.expectedPort)
            }
        })
    }
}
```

Conventions across production codebases:

- Test slice named `tests`.
- Loop variable `tc` or `tt`.
- Description field `name`.
- Use **named struct fields** when test cases span multiple lines —
  reading `expectedErr: true` is much clearer than counting
  positional fields.

---

## Write useful failure messages

Test failures should identify what went wrong, with what inputs, what
was expected, and what was received:

```go
// GOOD: actionable failure message
if got != want {
    t.Errorf("Square(%d) = %d; want %d", input, got, want)
}

// BAD: unhelpful failure
if got != want {
    t.Error("test failed")
}
```

The convention is `got, want` order matching `Errorf("got %v, want
%v", got, want)`. Reversing this is one of the most common code review
nits — the format string and argument order should match.

---

## Mark test helpers with t.Helper()

Helper functions should call `t.Helper()` so failure line numbers
point to the actual test:

```go
func assertNoError(t *testing.T, err error) {
    t.Helper()
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
}
```

Use `t.Fatal` for setup failures that prevent continuation, `t.Error`
with `continue` in table tests to run remaining cases.

---

## Skip integration tests with environment checks, not build tags

Peter Bourgon's evolved recommendation (2021): **Build tags hide test
failures and are non-discoverable.** Use environment variable checks
instead:

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

// AVOID: build tags hide tests
// +build integration
func TestDatabaseIntegration(t *testing.T) {
    // ...
}
```

The `t.Skip` approach surfaces in test output with `-v`, making it
clear when tests are skipped and why. Build tags require remembering
to add `-tags=integration` to your CI command, and tests that don't
run silently rot.

---

## Google prohibits third-party testing frameworks

Within Google's codebase, assertion libraries like testify and testing
frameworks like ginkgo are explicitly banned. The standard `testing`
package suffices.

GitLab permits testify but follows the expected-first convention:
`require.Equal(t, want, got)`.

Peter Bourgon: testing DSLs increase cognitive burden without
proportional value. If you reach for testify, ask whether the test
would actually be unclear without it.

---

## Prove slowness with benchmarks before optimizing

Dave Cheney warns: **"So many crimes against maintainability are
committed in the name of performance."** Optimization couples code
tightly, tears down abstractions, and exposes internals. Only pay
that cost when benchmarks prove necessity.

```go
func BenchmarkProcess(b *testing.B) {
    data := generateTestData()
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```

Run benchmarks with `-benchmem` to see allocations:

```bash
go test -bench=. -benchmem ./...
```

Use `benchstat` to compare runs. Don't trust a single sample.

---

## Loop variable capture in subtests (pre-Go 1.22)

Before Go 1.22, this bug bit hard:

```go
// BAD pre-1.22: all parallel subtests see the last tc
for _, tc := range tests {
    t.Run(tc.name, func(t *testing.T) {
        t.Parallel()
        // tc here might be the last iteration's value
    })
}

// GOOD: shadow
for _, tc := range tests {
    tc := tc
    t.Run(tc.name, func(t *testing.T) {
        t.Parallel()
        // tc is per-iteration
    })
}
```

Go 1.22+ scopes loop variables per-iteration, so the shadow is no
longer required for `for range`. But it remains good defensive
practice if your project supports older Go.

---

## Cleanup with t.Cleanup

Use `t.Cleanup()` for per-test teardown — it runs in LIFO order at
test/subtest end:

```go
func setupDB(t *testing.T) *sql.DB {
    t.Helper()
    db := mustOpen(t)
    t.Cleanup(func() { db.Close() })
    return db
}
```

This is cleaner than `defer` in setup helpers, which only runs when
the helper returns — too early.
