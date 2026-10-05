# Go SQL

Use [sqlc](https://sqlc.dev/) to generate type-safe Go code from SQL
queries, and [goose](https://github.com/pressly/goose) for migrations.
Write SQL, get Go.

This combo gives you:
- Compile-time checking of column names and types.
- Real SQL in your editor, no DSL or ORM to learn.
- A `Querier` interface auto-generated for mocking in tests.

## Project layout

```text
myservice/
├── db/
│   ├── migrations/
│   │   └── 001_create_users.sql
│   └── queries/
│       └── users.sql
├── internal/
│   └── db/                # sqlc output goes here
│       ├── db.go
│       ├── models.go
│       ├── querier.go
│       └── users.sql.go
├── sqlc.yaml
└── go.mod
```

## sqlc.yaml

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
        emit_interface: true       # generates Querier interface for mocking
        emit_empty_slices: true    # nil-free :many results
        sql_package: "database/sql" # matches the sql.DB/sql.Tx examples below
```

`emit_interface: true` is important — it gives you `db.Querier` for
unit tests, so handlers and services can depend on the interface and
real DB connections only show up in integration tests.

## Migrations with goose

```sql
-- db/migrations/001_create_users.sql
-- +goose Up
CREATE TABLE users (
    id         BIGSERIAL PRIMARY KEY,
    email      TEXT NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- +goose Down
DROP TABLE users;
```

Run with:

```bash
goose -dir db/migrations postgres "$DATABASE_URL" up
goose -dir db/migrations postgres "$DATABASE_URL" status
goose -dir db/migrations postgres "$DATABASE_URL" down
```

Always write a `Down` migration unless the change is impossible to
reverse (and even then, write a comment explaining the impossibility).

## Query annotations

```sql
-- db/queries/users.sql

-- name: GetUser :one
SELECT id, email, name, created_at
FROM users
WHERE id = $1;

-- name: ListUsers :many
SELECT id, email, name, created_at
FROM users
ORDER BY created_at DESC
LIMIT $1 OFFSET $2;

-- name: CreateUser :one
INSERT INTO users (email, name)
VALUES ($1, $2)
RETURNING id, email, name, created_at;

-- name: DeleteUser :exec
DELETE FROM users WHERE id = $1;

-- name: UpdateUserName :execrows
UPDATE users SET name = $1 WHERE id = $2;
```

| Annotation | Returns |
|---|---|
| `:one` | Single row, or the driver's no-rows error |
| `:many` | Slice of rows |
| `:exec` | No rows; only `error` |
| `:execrows` | Rows-affected count plus `error` |
| `:execresult` | Full `sql.Result` (driver-dependent) |

## Generate

```bash
sqlc generate
```

Re-run after every change to migrations or queries. Commit the generated
files — code review benefits from seeing the diff.

## Calling generated code

```go
type Service struct {
    pool    *sql.DB
    queries db.Querier
}

func (s *Service) GetUser(ctx context.Context, id int64) (db.User, error) {
    user, err := s.queries.GetUser(ctx, id)
    if errors.Is(err, sql.ErrNoRows) {
        return db.User{}, ErrNotFound
    }
    if err != nil {
        return db.User{}, fmt.Errorf("get user %d: %w", id, err)
    }
    return user, nil
}
```

Wrap `sql.ErrNoRows` into a domain error at the data-layer boundary —
upstream code shouldn't depend on `database/sql`.

## Transactions with database/sql

Use the `database/sql` generation setting for `*sql.DB` and `*sql.Tx`. Generate
transaction-bound queries with `db.New(tx)`. If you keep a concrete
`*db.Queries`, `Queries.WithTx(tx)` is an equivalent binding helper.

```go
func (s *Service) Transfer(ctx context.Context, from, to int64, amount int64) (rErr error) {
    tx, err := s.pool.BeginTx(ctx, nil)
    if err != nil {
        return fmt.Errorf("begin transfer: %w", err)
    }
    defer func() {
        err := tx.Rollback()
        if err != nil && !errors.Is(err, sql.ErrTxDone) {
            rErr = errors.Join(rErr, fmt.Errorf("rollback transfer: %w", err))
        }
    }()

    q := db.New(tx)
    if err := q.Debit(ctx, from, amount); err != nil {
        return fmt.Errorf("debit: %w", err)
    }
    if err := q.Credit(ctx, to, amount); err != nil {
        return fmt.Errorf("credit: %w", err)
    }
    if err := tx.Commit(); err != nil {
        return fmt.Errorf("commit transfer: %w", err)
    }
    return nil
}
```

`sql.ErrTxDone` after commit/rollback is expected; other cleanup errors remain
observable. Query exclusively through the transaction-bound queries until
commit, and avoid RPC or HTTP work while holding the database connection.

## Using pgx/v5

For native pgx, set `sql_package: "pgx/v5"` and use `pgxpool.Pool`, `pgx.Tx`, and
`pgx.ErrNoRows`. These types do not mix with the `database/sql` example above.
The generated transaction binding accepts a `pgx.Tx`; pgx transaction methods
also take a context.

```go
func inPGXTx(ctx context.Context, pool *pgxpool.Pool, work func(pgx.Tx) error) (rErr error) {
    tx, err := pool.BeginTx(ctx, pgx.TxOptions{})
    if err != nil {
        return fmt.Errorf("begin: %w", err)
    }
    defer func() {
        // Rollback still needs a usable context if the request was cancelled.
        cleanupCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
        defer cancel()
        err := tx.Rollback(cleanupCtx)
        if err != nil && !errors.Is(err, pgx.ErrTxClosed) {
            rErr = errors.Join(rErr, fmt.Errorf("rollback: %w", err))
        }
    }()
    if err := work(tx); err != nil {
        return err
    }
    if err := tx.Commit(ctx); err != nil {
        return fmt.Errorf("commit: %w", err)
    }
    return nil
}
```

Choose a driver first, then keep generated types, no-rows matching, and
transaction lifecycle consistent. See the
[sqlc transaction guide](https://docs.sqlc.dev/en/latest/howto/transactions.html).

## Connections, cancellation, and query results

Create pools at application startup and close them during coordinated shutdown.
Set connection limits from database capacity and measured workload; a pool is a
resource budget, not a cure for slow queries. Pass request contexts into query
and transaction operations. PostgreSQL and SQLite have different concurrency
and isolation behavior; use the engine's contract when choosing an isolation
level or retrying a transaction.

For manual `database/sql` queries, close rows, check `Scan` errors and
`rows.Err()` after iteration, and check `RowsAffected` when it is part of the
contract. Do not interpolate values into SQL strings. Dynamic identifiers need
an allowlist; query parameters represent values, not table or column names.

## Testing

Two approaches, used together:

**Unit tests** — mock the `Querier` interface:

```go
type fakeQuerier struct {
    db.Querier             // embed for unimplemented methods
    user db.User
    err  error
}

func (f *fakeQuerier) GetUser(ctx context.Context, id int64) (db.User, error) {
    return f.user, f.err
}

func TestServiceGetUser(t *testing.T) {
    svc := &Service{queries: &fakeQuerier{user: db.User{ID: 1, Name: "ada"}}}
    u, err := svc.GetUser(context.Background(), 1)
    // ...
}
```

**Integration tests** — real database, gated by env var:

```go
func TestUsersIntegration(t *testing.T) {
    dsn := os.Getenv("TEST_DATABASE_URL")
    if dsn == "" {
        t.Skip("set TEST_DATABASE_URL")
    }
    pool, err := pgxpool.New(context.Background(), dsn)
    // ...
}
```

Run migrations against a throwaway database (testcontainers, a CI
ephemeral Postgres) before each integration run.

## NULL handling

Nullable columns map to driver-specific wrappers, with pointer support
depending on the selected sqlc driver and type:

| SQL | Go (database/sql) | Go (pgx) |
|---|---|---|
| `INT NULL` | `sql.NullInt64` | `pgtype.Int8` |
| `TEXT NULL` | `sql.NullString` | `pgtype.Text` |
| `TIMESTAMPTZ NULL` | `sql.NullTime` | `pgtype.Timestamptz` |

For PostgreSQL with supported pgx generation,
`emit_pointers_for_null_types: true` can emit pointers instead. For
`database/sql`, inspect generated types and use supported sqlc overrides where
needed; do not assume the pointer option applies to every driver.

## Common pitfalls

- **Forgetting to regenerate.** Add `sqlc generate` to your `Makefile`
  and CI lint step.
- **Using `:exec` when you wanted `:one RETURNING`** — `:exec` discards
  the returned row.
- **Passing `database/sql` types into the service layer.** Wrap or
  translate at the storage boundary.
- **Long-running transactions.** Hold transactions only for the work
  that must be atomic; release the connection before any RPC or HTTP
  call.

## Related guides

| Task | Guide |
|---|---|
| Translating `sql.ErrNoRows` into HTTP 404 | [HTTP](../http/guide.md) + [Errors](../errors/guide.md) |
| Mocking the `Querier` interface in tests | [Testing](../testing/guide.md) |
| Logging slow queries with attrs | [Logging](../logging/guide.md) |
| Connection pool lifecycle, graceful shutdown | [Concurrency](../concurrency/guide.md) |
| General Go idioms and naming | [Style](../style/guide.md) |
