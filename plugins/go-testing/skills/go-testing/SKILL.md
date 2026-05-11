---
name: go-testing
description: >-
  Idiomatic Go testing with the stdlib `testing` package and the
  go-testdeep assertion library. ALWAYS use this skill when writing or
  reviewing Go tests — table-driven tests with `map[string]testCase`,
  `t.Run` subtests, `t.Helper()` for assertion helpers, `t.Cleanup`,
  `t.Parallel`, integration test gating with environment variables,
  benchmarks (`testing.B`), fuzz tests, go-testdeep operators
  (`td.Cmp`, `td.CmpError`, `td.CmpNoError`, `td.Struct`, `td.Smuggle`,
  `td.Between`, `td.Re`, `td.Require`), and the third-party-frameworks
  debate (go-testdeep when deps are allowed, stdlib-only for
  dependency-free projects, never testify). Pair with go-sql for
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

Pick the assertion stack by what your project allows:

- **Dependency-free project** — use the standard library `testing`
  package only. No third-party assertions.
- **Project that allows deps** — use
  [`go-testdeep`](https://github.com/maxatome/go-testdeep). Its
  composable operators (`td.Cmp`, `td.CmpStruct`, `td.Smuggle`,
  `td.Between`, etc.) produce precise diffs and read naturally.
- **Never use testify.** Its `assert`/`require` split, vague failure
  messages, and reliance on `interface{}` comparisons are worse than
  either alternative above.

For the comprehensive reference, see `references/testing.md`.

## Table-driven with named cases

`map[string]testCase` makes the case name the subtest name automatically.
Assertions use `td.Cmp`, `td.CmpError`, `td.CmpNoError`:

```go
import (
    "testing"

    "github.com/maxatome/go-testdeep/td"
)

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
            if tc.wantErr {
                td.CmpError(t, err)
                return
            }
            td.CmpNoError(t, err)
            td.Cmp(t, got, tc.want)
        })
    }
}
```

On a dependency-free project, swap the `td.*` calls for plain
`if got != tc.want { t.Errorf(...) }` checks — the loop and table shape
stay the same.

## Helpers must call t.Helper()

Use `td.Require(t)` inside helpers when a setup step must succeed before
the rest of the test can run. `t.Helper()` keeps the failure line pointed
at the caller:

```go
func mustOpen(t *testing.T, path string) *os.File {
    t.Helper()
    f, err := os.Open(path)
    td.Require(t).CmpNoError(err)
    t.Cleanup(func() { f.Close() })
    return f
}
```

`td.Require(t)` returns a `*td.T` whose failing assertions call
`t.Fatal` (vs `td.Cmp(t, ...)` which calls `t.Error`). `t.Cleanup` runs
in LIFO order at the end of the test (or subtest) and is the preferred
replacement for `defer` in test setup helpers.

## Failure messages

testdeep generates structured field-level diffs automatically. You
write the comparison; the library produces the message:

```go
td.Cmp(t, got, want)
// On failure prints something like:
//   DATA: Field "Email"
//        got: "ada@example.com "
//   expected: "ada@example.com"
```

For more expressive comparisons, use operators:

```go
td.Cmp(t, user, td.Struct(User{}, td.StructFields{
    "ID":    int64(1),
    "Email": td.Re(`^.+@.+\..+$`),
    "Tags":  td.Bag("go", "testing"),  // unordered set match
}))
```

On a **dependency-free project**, include inputs, expected, and actual
in the message yourself:

```go
if got != want {
    t.Errorf("Square(%d) = %d, want %d", input, got, want)
}
```

Convention for stdlib: `got` first, `want` second. Never write
`t.Error("test failed")` — it tells the next person reading the failure
nothing.

## t.Fatal vs t.Error (and td.Require vs td.Cmp)

- `t.Fatal` / `t.Fatalf` — stop this test immediately. Use when later
  assertions can't run (setup failure, nil result you'd dereference).
- `t.Error` / `t.Errorf` — record failure, keep running. Use when later
  assertions still produce useful information.
- `td.Require(t).Cmp(...)` is testdeep's `Fatal` equivalent;
  `td.Cmp(t, ...)` is the `Error` equivalent.

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

**Use `go-testdeep` when the project allows third-party dependencies.**
It builds expressive matchers on top of `testing.T`:

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

The failure output is a precise diff of the failing fields — not a stack
trace, not "expected X to equal Y".

**Use the stdlib `testing` package** when the project must stay
dependency-free (libraries, very small tools, embedded use). Plain
`if got != want { t.Errorf(...) }` with table-driven tests covers most
needs.

**Do not use testify.** Its split between `assert` and `require` invites
test continuation after fatal failures, its messages are vague, and its
comparison semantics rely on `reflect.DeepEqual` against `interface{}`
without the matcher composability `go-testdeep` gives you. If a project
already depends on testify, migrate when you touch the tests; don't add
new uses.

Ginkgo and other BDD frameworks add a DSL layer on top of testing — not
worth the cognitive cost.

## When to load a sibling skill

| Task | Skill |
|---|---|
| Mocking a sqlc-generated `Querier` | go-sql |
| Testing HTTP handlers with `httptest` | go-http |
| Testing concurrent code, race detector | go-concurrency |
| Asserting on wrapped errors with `errors.Is`/`errors.As` | go-errors |
| General Go idioms and naming | go-style |
