---
name: go-dev
description: >-
  Go development skill for writing, reviewing, and improving Go code. ALWAYS use this skill when the user's task involves Go or Golang in any way — writing new Go code, reviewing existing Go code, building Go services, creating Go CLI tools, working with Go tests, setting up Go linting, using sqlc for database access, or anything else Go-related. This includes requests mentioning: Go, Golang, .go files, go.mod, go test, golangci-lint, Chi router, sqlc, goose migrations, Go generics, goroutines, channels, Go interfaces, Go error handling, Go concurrency, table-driven tests, or any Go package/tool. Even if the user doesn't say "best practices" — if they're writing Go, use this skill. Covers backend services, APIs, CLI tools, database layers, testing patterns, error handling, concurrency, generics, structured logging with slog, and project structure.
version: 1.1.0
tags:
  - go
  - golang
  - backend
  - cli
  - api
  - sqlc
  - database
---

# Go Development

Write Go code that is readable, maintainable, and production-ready using
battle-tested patterns from major production codebases.

For comprehensive coverage of all idioms, patterns, and pitfalls, read
`references/go-styleguide.md`. This file focuses on quick decisions and
workflows.

## MCP

Always use Context7 MCP to fetch the latest documentation.

## Libraries

- Prefer well-maintained, zero-dependency libraries from the awesome-go list.
- HTTP routing: [Chi](https://github.com/go-chi/chi).
- Logging: `log/slog` (structured, leveled, stdlib since Go 1.21).
- Configuration: flags or environment variables — no external config frameworks.
- Database access: [sqlc](https://sqlc.dev/) for typesafe SQL code generation.
- Migrations: [goose](https://github.com/pressly/goose).
- Testing: stdlib `testing` package. Avoid third-party assertion libraries.

## Linters

Run `golangci-lint` on every commit and pull request. Use the bundled
`.golangci.yml` config:

```bash
# Setup linting for a project
scripts/setup_golangci_lint.sh /path/to/project

# Run all linters
golangci-lint run ./...

# Auto-fix
golangci-lint run --fix ./...
```

Run `goimports` before committing to keep imports formatted.

## Quick Decision Trees

### When to use generics?

Use generics (Go 1.18+) when:

- Writing data structures (trees, caches, pools) that work across types.
- Utility functions that operate on slices, maps, or channels of any type.
- Type constraints reduce duplication without sacrificing readability.

Avoid generics when:

- A concrete type or `any` suffices.
- The function body would need type assertions anyway.
- It makes the code harder to read for marginal DRY benefit.

```go
// GOOD: generic utility
func Map[T, U any](s []T, f func(T) U) []U {
    result := make([]U, len(s))
    for i, v := range s {
        result[i] = f(v)
    }
    return result
}

// GOOD: constrained type
type Number interface {
    ~int | ~int64 | ~float64
}

func Sum[T Number](nums []T) T {
    var total T
    for _, n := range nums {
        total += n
    }
    return total
}
```

### When to use interfaces?

Define interfaces at the consumption site, not the implementation:

```go
// GOOD: consumer defines what it needs
package storage

type Store interface {
    Get(key string) ([]byte, error)
}

// BAD: implementation forces interface on consumers
package postgres

type PostgresStore interface { ... }
```

Interface size: 1 method is perfect, 2-3 if cohesive, 4+ consider splitting.
Larger interfaces are acceptable for SaaS/enterprise products; keep them small
for libraries.

Accept interfaces, return concrete types.

### How to handle errors?

1. Can I handle this completely here? → Log and continue.
2. Does caller need programmatic access? → `%w` wrapping.
3. Should I hide implementation details? → `%v` wrapping.
4. Is this a library? → Never log, always return.

```go
// Wrap with context
if err != nil {
    return fmt.Errorf("connect to database: %w", err)
}
```

Error strings: lowercase, no punctuation, no "failed to" prefix. Handle each
error exactly once — log OR return, never both.

Use `errors.Join` (Go 1.20+) to combine multiple independent errors:

```go
var errs []error
for _, item := range items {
    if err := process(item); err != nil {
        errs = append(errs, err)
    }
}
if err := errors.Join(errs...); err != nil {
    return fmt.Errorf("processing batch: %w", err)
}
```

### When to use concurrency?

Leave concurrency to the caller unless building a server/daemon, worker pool,
or managing background operations.

Before launching a goroutine, know when it will stop:

```go
ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
defer cancel()

go func() {
    for {
        select {
        case <-ctx.Done():
            return
        case work := <-ch:
            process(work)
        }
    }
}()
```

Context as first parameter. Always.

### Iterators (Go 1.23+)

Use `iter.Seq` and `iter.Seq2` for lazy iteration:

```go
// Iterator that yields values
func FilterPositive(nums []int) iter.Seq[int] {
    return func(yield func(int) bool) {
        for _, n := range nums {
            if n > 0 {
                if !yield(n) {
                    return
                }
            }
        }
    }
}

// Consuming an iterator
for v := range FilterPositive(data) {
    fmt.Println(v)
}
```

Use range-over-int (Go 1.22+): `for i := range n` instead of
`for i := 0; i < n; i++`.

### Structured logging with slog

Use `log/slog` for all logging. Pass the logger as a dependency, never as a
package-level global:

```go
type Server struct {
    logger *slog.Logger
}

func NewServer(logger *slog.Logger) *Server {
    return &Server{logger: logger}
}

func (s *Server) HandleRequest(ctx context.Context, req *Request) {
    s.logger.InfoContext(ctx, "handling request",
        slog.String("method", req.Method),
        slog.String("path", req.Path),
    )
}
```

Use `slog.With` to add common attributes. Use `LogValuer` for expensive
values that should only be computed when the log level is enabled.

## Testing

Table-driven tests with `map[string]testCase` for descriptive names:

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

Test helpers call `t.Helper()` so failure line numbers point to the actual test.

Integration tests skip when environment is not set:

```go
func TestIntegration(t *testing.T) {
    if os.Getenv("INTEGRATION_TESTS") == "" {
        t.Skip("skipping integration tests")
    }
}
```

## Common Workflows

### Creating a new HTTP service

**Project structure:**

```text
myservice/
├── cmd/server/main.go
├── internal/
│   ├── handler/
│   ├── service/
│   └── storage/
├── db/
│   ├── migrations/
│   └── queries/
├── go.mod
├── Makefile
└── .golangci.yml
```

**main.go pattern — flags, graceful shutdown:**

```go
func main() {
    addr := flag.String("addr", ":8080", "listen address")
    flag.Parse()

    srv := &http.Server{
        Addr:         *addr,
        Handler:      setupRoutes(),
        ReadTimeout:  30 * time.Second,
        WriteTimeout: 30 * time.Second,
    }

    go func() {
        sigint := make(chan os.Signal, 1)
        signal.Notify(sigint, os.Interrupt)
        <-sigint

        ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
        defer cancel()
        srv.Shutdown(ctx)
    }()

    log.Printf("listening on %s", *addr)
    if err := srv.ListenAndServe(); err != http.ErrServerClosed {
        log.Fatalf("server error: %v", err)
    }
}
```

### Working with SQL databases using sqlc

sqlc generates typesafe Go code from SQL queries. Write SQL, get Go.

**1. Install and configure:**

```yaml
# sqlc.yaml
version: "2"
sql:
  - schema: "db/migrations"
    queries: "db/queries"
    engine: "postgresql"
    gen:
      go:
        package: "db"
        out: "internal/db"
        emit_json_tags: true
        emit_interface: true
```

**2. Write migrations (with goose):**

```sql
-- db/migrations/001_create_users.sql
-- +goose Up
CREATE TABLE users (
    id    BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name  TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- +goose Down
DROP TABLE users;
```

**3. Write queries with annotations:**

```sql
-- db/queries/users.sql

-- name: GetUser :one
SELECT id, email, name, created_at
FROM users
WHERE id = $1;

-- name: ListUsers :many
SELECT id, email, name, created_at
FROM users
ORDER BY created_at DESC;

-- name: CreateUser :one
INSERT INTO users (email, name)
VALUES ($1, $2)
RETURNING id, email, name, created_at;

-- name: DeleteUser :exec
DELETE FROM users WHERE id = $1;
```

**4. Generate and use:**

```bash
sqlc generate
```

```go
// internal/db/ now contains typesafe Go code
func (s *Service) GetUser(ctx context.Context, id int64) (db.User, error) {
    return s.queries.GetUser(ctx, id)
}
```

**5. Testing with sqlc:**

Enable `emit_interface: true` in sqlc.yaml to get a `Querier` interface for
mocking in unit tests. Use a real database for integration tests.

### Creating a CLI tool

```text
mycli/
├── main.go
├── internal/command/
├── go.mod
└── .golangci.yml
```

Use `flag.NewFlagSet` for subcommands. Write errors to stderr, exit non-zero
on failure.

## Quick Reference

**Naming:** packages lowercase/singular, no `Get` prefix on getters, acronyms
consistent case (`URL` not `Url`), constants in mixedCaps.

**Structure:** return early with guard clauses, success path left-aligned,
imports grouped: stdlib → external → internal.

**Critical pitfalls:** loop variable capture in closures, nil interface vs nil
value in interface, defer in loops (wrap in closure), map writes to nil map.

For the full reference on all patterns, see `references/go-styleguide.md`.

## Linting Setup

Run the setup script to configure golangci-lint for a project:

```bash
scripts/setup_golangci_lint.sh /path/to/your/project
```

This copies the bundled `.golangci.yml` and optionally installs a pre-commit
hook. Common commands:

```bash
golangci-lint run ./...         # run all linters
golangci-lint run --fix ./...   # auto-fix issues
golangci-lint run ./internal/...# lint specific paths
```
