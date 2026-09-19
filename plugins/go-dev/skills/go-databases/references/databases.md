# Go Databases (sqlc + goose) — Deep Reference

Long-form rationale and edge cases behind the rules in `SKILL.md`.

---

## Why sqlc instead of an ORM?

ORMs in Go (gorm, ent, bun) trade SQL clarity for "convenience":

- They obscure the actual query running, making performance debugging
  harder.
- They generate suboptimal SQL (N+1 queries, missing indexes).
- They couple your domain model to the persistence model in ways
  that resist refactoring.
- They reinvent the type system in struct tags.

sqlc inverts the trade. You write SQL — the language you actually need
to know to operate a database — and sqlc generates the boring
plumbing. The query you wrote is the query that runs. There is no
"what happens when I add `Preload`?" mystery.

The cost: you write more SQL, and the generated code is just
parameter binding + scanning.

---

## sqlc.yaml options worth knowing

```yaml
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
        emit_prepared_queries: false
        emit_pointers_for_null_types: true
        sql_package: "pgx/v5"
```

- `emit_interface: true` — generates a `Querier` interface for
  mocking. Always on for testable code.
- `emit_pointers_for_null_types: true` — `*string` instead of
  `sql.NullString`. Easier to compose, easier to JSON-marshal.
- `emit_json_tags: true` — adds `json:"field_name"` tags. Useful when
  generated structs flow into HTTP responses; harmless when they
  don't.
- `emit_prepared_queries: false` — turn it on if your DB driver
  benefits from prepared statements (rarely matters with pgx).
- `sql_package: "pgx/v5"` — pgx is faster, supports more PostgreSQL
  features, and has better error types than `database/sql`.

---

## Goose migration ordering

Two filename conventions are common:

**Sequential numeric**: `001_create_users.sql`, `002_add_email_index.sql`.
Simple, but merge conflicts are inevitable when two branches both add
`003_*`. Pick one to renumber on merge — annoying but correct.

**Timestamped**: `20240115093000_create_users.sql`. Avoids merge
conflicts entirely. Goose sorts lexically, so timestamps work as long
as you generate them with `goose create name sql`.

Pick one and stay with it. Mixing styles in one project means
ordering depends on character-by-character lex comparison, which
will surprise you.

---

## Always handle pgx.ErrNoRows / sql.ErrNoRows

`:one` queries return an error when zero rows match. Wrap it into a
domain error:

```go
user, err := q.GetUser(ctx, id)
if err != nil {
    if errors.Is(err, pgx.ErrNoRows) {
        return db.User{}, ErrNotFound
    }
    return db.User{}, fmt.Errorf("get user %d: %w", id, err)
}
```

The `errors.Is` form survives wrapping at lower layers — `errors.As`
likewise — so callers can detect "not found" without depending on the
SQL driver.

---

## Transactions and the deferred rollback

Idiomatic transaction:

```go
tx, err := pool.Begin(ctx)
if err != nil {
    return fmt.Errorf("begin: %w", err)
}
defer tx.Rollback(ctx) // ignored after Commit

qtx := q.WithTx(tx)
// ... operations on qtx ...

if err := tx.Commit(ctx); err != nil {
    return fmt.Errorf("commit: %w", err)
}
```

Why `defer tx.Rollback` even though we Commit? If any of the
operations between `Begin` and `Commit` returns early, the deferred
rollback releases the transaction. After a successful `Commit`,
`Rollback` is a documented no-op — safe.

For pgx specifically, `tx.Rollback(ctx)` returns
`pgx.ErrTxClosed` when called post-commit. You can ignore the error;
the rollback was unnecessary.

---

## emit_interface and the Querier mock

With `emit_interface: true`, sqlc generates:

```go
type Querier interface {
    GetUser(ctx context.Context, id int64) (User, error)
    ListUsers(ctx context.Context) ([]User, error)
    CreateUser(ctx context.Context, arg CreateUserParams) (User, error)
    // ... one method per query
}
```

Your service code accepts `db.Querier` instead of `*db.Queries`. In
tests, embed the interface and override only the methods you exercise:

```go
type mockQueries struct {
    db.Querier
    getUser func(context.Context, int64) (db.User, error)
}

func (m *mockQueries) GetUser(ctx context.Context, id int64) (db.User, error) {
    return m.getUser(ctx, id)
}
```

The embedded `Querier` panics if a non-overridden method is called —
exactly what you want; tests should fail loudly if a code path hits
unmocked queries.

---

## Integration test pitfalls

**Database state bleed between tests.** Two reasonable approaches:

1. Wrap each test in a transaction and roll it back at the end.
   Fastest, no setup cost, but constrains tests from observing
   committed state from another connection.
2. Truncate tables in `t.Cleanup`. Slightly slower; allows
   multi-connection scenarios.

Avoid spinning a fresh DB per test — the cost adds up quickly.

**Time-based assertions.** Tests that compare `created_at == time.Now()`
are flaky. Either freeze time (inject a clock), assert on a window
(`time.Now().Add(-1*time.Second).Before(got)`), or just check that
the field is set.

**Migration ordering in tests.** Run `goose.Up` against the test DB
in `TestMain` so all tests start from the latest schema:

```go
func TestMain(m *testing.M) {
    dsn := os.Getenv("TEST_DATABASE_URL")
    if dsn == "" {
        os.Exit(m.Run())
    }
    db, err := sql.Open("pgx", dsn)
    if err != nil {
        log.Fatalf("connect: %v", err)
    }
    if err := goose.Up(db, "db/migrations"); err != nil {
        log.Fatalf("migrate: %v", err)
    }
    db.Close()
    os.Exit(m.Run())
}
```

---

## Don't fight sqlc when SQL fights back

Some queries are awkward to express in sqlc:

- Dynamic IN clauses with variable-length lists (sqlc supports
  `pgx.NamedArgs` arrays in PostgreSQL: `WHERE id = ANY(@ids::int[])`).
- Conditional WHERE clauses (`WHERE name = COALESCE($1, name)`).
- Full-text search where the user supplies the query.

For these, drop to `database/sql`/`pgx` directly. sqlc and raw SQL
coexist fine in one project — keep generated code in `internal/db/`,
hand-written queries in service files where the dynamic logic lives.

---

## Driver choice: pgx vs database/sql + lib/pq

For new PostgreSQL projects in 2026, pgx is the better choice:

- Faster (binary protocol, fewer round trips).
- Better type support (`numeric`, `bytea`, arrays, `jsonb`).
- Better error types — distinguish unique-violation from
  foreign-key-violation cleanly.
- Active development; lib/pq is in maintenance mode.

`database/sql` + lib/pq is fine if you need driver-agnostic code
(supporting both Postgres and MySQL via the same interface).
Otherwise, pick pgx and don't look back.
