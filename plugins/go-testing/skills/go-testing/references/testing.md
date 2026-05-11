# Testing reference

Carved from the comprehensive Go style guide. Covers table-driven tests,
useful failure messages, `t.Helper()`, integration test gating, and the
third-party-frameworks debate.

---

## Use table-driven tests with named fields

Table-driven tests are the Go standard for comprehensive coverage with minimal
duplication. Use `map[string]tcase` so the case name becomes the subtest name
automatically and the compiler enforces unique keys:

```go
func TestParseHost(t *testing.T) {
    type tcase struct {
        input        string
        expectedHost string
        expectedPort string
        expectedErr  bool
    }

    tests := map[string]tcase{
        "host and port": {
            input:        "example.com:8080",
            expectedHost: "example.com",
            expectedPort: "8080",
        },
        "host only": {
            input:        "example.com",
            expectedHost: "example.com",
            expectedPort: "",
        },
        "invalid format": {
            input:       ":::invalid",
            expectedErr: true,
        },
    }

    for name, tc := range tests {
        t.Run(name, func(t *testing.T) {
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

Use **named struct fields** for readability when test cases span multiple lines.
The variable conventions across production codebases: test map named `tests`,
case type named `tcase` (or `testCase`), loop variables `name, tc`.

## Write useful failure messages

Test failures should identify what went wrong, with what inputs, what was
expected, and what was received:

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

The convention is `got, want` order matching
`Errorf("got %v, want %v", got, want)`.

## Mark test helpers with t.Helper()

Helper functions should call `t.Helper()` so failure line numbers point to the
actual test:

```go
func assertNoError(t *testing.T, err error) {
    t.Helper()
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
}
```

Use `t.Fatal` for setup failures that prevent continuation, `t.Error` with
`continue` in table tests to run remaining cases.

## Skip integration tests with environment checks, not build tags

Peter Bourgon's evolved recommendation (2021): **Build tags hide test failures
and are non-discoverable.** Use environment variable checks instead:

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

The `t.Skip` approach surfaces in test output, making it clear when tests are
skipped and why.

## Assertion libraries: go-testdeep or stdlib, never testify

Pick the assertion stack by what the project allows:

- **Dependency-free projects** (libraries, very small tools, embedded
  use): standard library `testing` only. No third-party assertions.
- **Projects that allow dependencies**: use
  [`go-testdeep`](https://github.com/maxatome/go-testdeep). Its
  matcher operators (`td.Cmp`, `td.Struct`, `td.Smuggle`, `td.Between`,
  `td.Re`, …) compose, produce precise field-level diffs, and integrate
  cleanly with `*testing.T`.

```go
import (
    "testing"

    "github.com/maxatome/go-testdeep/td"
)

func TestUser(t *testing.T) {
    got := loadUser(1)

    td.Cmp(t, got, td.Struct(User{}, td.StructFields{
        "ID":        int64(1),
        "Email":     td.Re(`^.+@.+\..+$`),
        "CreatedAt": td.Between(time.Now().Add(-time.Minute), time.Now()),
    }))
}
```

**Do not use testify.** Its `assert` vs `require` split invites test
continuation past fatal failures, its messages are vague, and it relies
on `reflect.DeepEqual` against `interface{}` without the composable
matchers `go-testdeep` provides. Within Google's codebase testify is
banned outright. Migrate existing testify use when you touch the tests
— don't add new uses.

Ginkgo and other BDD frameworks layer a DSL on top of `testing` —
not worth the cognitive cost.
