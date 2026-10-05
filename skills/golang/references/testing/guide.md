# Go Testing

Pick the assertion stack by what your project allows:

- **Dependency-free project** — stdlib `testing` only. No third-party
  assertions.
- **Project that allows deps** — use
  [`go-testdeep`](https://github.com/maxatome/go-testdeep). Composable
  operators (`td.Cmp`, `td.Struct`, `td.Smuggle`, `td.Between`, …)
  produce precise diffs.
- Prefer these two choices for new projects. Preserve an existing assertion
  framework for unrelated changes; choosing a new dependency or migrating
  tests should serve the requested work.

References: [testing.md](testing.md) for the carved style guide,
[perf-and-parallel.md](perf-and-parallel.md) for parallel tests, benchmarks, and
the race detector.

## Table-driven with named cases

`map[string]testCase` makes the case name the subtest name
automatically:

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
`if got != tc.want { t.Errorf(...) }` checks — the table shape stays
the same.

## Helpers must call t.Helper()

```go
func mustOpen(t *testing.T, path string) *os.File {
    t.Helper()
    f, err := os.Open(path)
    td.Require(t).CmpNoError(err)
    t.Cleanup(func() {
        if err := f.Close(); err != nil {
            t.Errorf("close %s: %v", path, err)
        }
    })
    return f
}
```

`td.Require(t)` returns a `*td.T` whose failing assertions call
`t.Fatal`; `td.Cmp(t, ...)` is the `t.Error` equivalent. `t.Cleanup`
runs in LIFO order at the end of the test and replaces `defer` in
setup helpers.

## Failure messages

testdeep generates field-level diffs automatically — write the
comparison and let the library produce the message. Compose operators
for richer assertions:

```go
td.Cmp(t, user, td.Struct(User{}, td.StructFields{
    "ID":    int64(1),
    "Email": td.Re(`^.+@.+\..+$`),
    "Tags":  td.Bag("go", "testing"),  // unordered set match
}))
```

On stdlib-only projects, include inputs, expected, and actual yourself
— `got` first, `want` second:

```go
if got != want {
    t.Errorf("Square(%d) = %d, want %d", input, got, want)
}
```

Never write `t.Error("test failed")`. See [testing.md](testing.md) for
the full discussion.

## t.Fatal vs t.Error (and td.Require vs td.Cmp)

- `t.Fatal` / `td.Require(t).Cmp(...)` — stop this test immediately.
  Use when later assertions can't run (setup failure, nil that would
  be dereferenced).
- `t.Error` / `td.Cmp(t, ...)` — record failure, keep running so
  remaining assertions still produce useful information.

## Integration tests: env vars, not build tags

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

Build tags hide tests; the `t.Skip` line surfaces in normal `go test`
output and tells you exactly what to set.

## Parallel, benchmarks, race detector

The headlines:

- Mark independent tests with `t.Parallel()`. Re-bind the loop
  variables before passing to a subtest closure.
- Benchmarks live in `func BenchmarkXxx(b *testing.B)` and run with
  `go test -bench=. -benchmem`. Use `b.ResetTimer()` after setup.
- Run CI with `go test -race ./...`. The race detector finds the
  bugs you can't reproduce.

From the target Go project's root, run the portable opt-in helper for the same
race-and-coverage gate:

```bash
/path/to/golang/scripts/testing/run_tests.sh
```

Full discussion: [perf-and-parallel.md](perf-and-parallel.md).

## Fuzz contracts at input boundaries

Seed a fuzz target with representative valid, invalid, and boundary inputs.
Assert the parser's contract rather than the absence of a particular error
message. Go 1.18+ fuzzing stores reproducing inputs for failures.

```go
func FuzzParsePort(f *testing.F) {
    for _, seed := range []string{"80", "", "-1", "65536"} {
        f.Add(seed)
    }
    f.Fuzz(func(t *testing.T, input string) {
        port, err := ParsePort(input)
        if err == nil && (port < 1 || port > 65535) {
            t.Errorf("ParsePort(%q) = %d without error", input, port)
        }
    })
}
```

```bash
go test ./internal/config -run '^$' -fuzz '^FuzzParsePort$' -fuzztime=10s
```

Fuzz one package/target at a time. Keep the target deterministic and bounded;
avoid network dependencies or shared mutable state. Ordinary `go test` runs
seed cases but does not replace a timed fuzz campaign. For returned errors,
test `errors.Is`/`errors.As` when callers depend on matching, not full strings.

## Related guides

| Task | Guide |
|---|---|
| Mocking a sqlc-generated `Querier` | [SQL](../sql/guide.md) |
| Testing HTTP handlers with `httptest` | [HTTP](../http/guide.md) |
| Testing concurrent code, race detector | [Concurrency](../concurrency/guide.md) |
| Asserting on wrapped errors with `errors.Is`/`errors.As` | [Errors](../errors/guide.md) |
| General Go idioms and naming | [Style](../style/guide.md) |
