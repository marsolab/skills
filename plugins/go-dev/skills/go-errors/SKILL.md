---
name: go-errors
description: >-
  Idiomatic error handling in Go. Triggers when the user is writing or
  reviewing Go error code: wrapping with `fmt.Errorf` and `%w`, comparing
  with `errors.Is`/`errors.As`, combining with `errors.Join`, formatting
  error messages, deciding between log-and-return, returning early with
  guard clauses, defining sentinel or typed errors, or auditing a Go
  codebase for missing error checks. Also load when the user mentions
  `if err != nil`, error wrapping, error chains, sentinel errors, or
  asks "should I panic here?" in Go.
version: 1.0.0
tags:
  - go
  - golang
  - errors
  - error-handling
---

# Go Error Handling

Errors are values. Handle them explicitly, exactly once, with enough
context that the caller can debug without source access.

For the long-form rationale and edge cases, read
`references/errors.md`.

## The four-question decision

Before every `if err != nil`:

1. **Can I handle this completely here?** → Log a degraded-mode message
   and continue with a sensible default. Do not return.
2. **Does the caller need programmatic access (`errors.Is`/`As`)?** →
   Wrap with `%w`.
3. **Should I hide implementation details from the caller?** → Wrap
   with `%v` or use a sanitized sentinel.
4. **Is this library code?** → Never log, always return. Logging is the
   binary's job.

```go
// Wrap with context — caller can still inspect with errors.Is.
if err != nil {
    return fmt.Errorf("connect to database %s: %w", dsn, err)
}
```

## Error string style

Lowercase. No trailing punctuation. No "failed to" prefix — the word
"error" already implies failure. The wrapping caller adds its own
prefix and the messages compose cleanly:

```text
process request: connect to database postgres://...: connection refused
```

```go
// GOOD
return fmt.Errorf("read config: %w", err)

// BAD: capital + period + redundant "failed to"
return fmt.Errorf("Failed to read config: %w.", err)
```

## Handle each error exactly once

Log **or** return — never both. Logging at every level produces stack
trace soup. Wrap with context and return; let the top of the call
stack decide what to log.

```go
// BAD: handled twice, caller logs again
if err != nil {
    log.Printf("process failed: %v", err)
    return err
}

// GOOD: add context, return, let caller log once
if err != nil {
    return fmt.Errorf("process request: %w", err)
}
```

## %w vs %v

- **`%w` (wrap)** — preserves the chain. Callers can use `errors.Is`
  and `errors.As`. Use for errors that crossed a meaningful boundary.
- **`%v` (format)** — flattens to a string. Use when the underlying
  error is an implementation detail you want to hide.

```go
// Expose for programmatic handling.
return fmt.Errorf("query users: %w", err)

// Hide.
return fmt.Errorf("service unavailable: %v", err)
```

## errors.Is / errors.As

Compare with `errors.Is` for sentinel errors, `errors.As` for typed
errors:

```go
if errors.Is(err, sql.ErrNoRows) {
    return nil, ErrNotFound
}

var netErr *net.OpError
if errors.As(err, &netErr) {
    // inspect netErr.Op, netErr.Net, etc.
}
```

Never compare with `==` for wrapped errors — it only matches the outer
layer.

## errors.Join for batch errors (Go 1.20+)

When validating multiple fields or running parallel operations, collect
all errors, join at the end:

```go
func Validate(cfg Config) error {
    var errs []error
    if cfg.Host == "" {
        errs = append(errs, errors.New("host is required"))
    }
    if cfg.Port < 1 || cfg.Port > 65535 {
        errs = append(errs, fmt.Errorf("invalid port: %d", cfg.Port))
    }
    if cfg.Timeout <= 0 {
        errs = append(errs, errors.New("timeout must be positive"))
    }
    return errors.Join(errs...) // nil if no errors
}
```

The joined error supports `errors.Is`/`errors.As` per constituent.
Also great for paired cleanup:

```go
func Close(db *sql.DB, file *os.File) error {
    return errors.Join(db.Close(), file.Close())
}
```

## Sentinel and typed errors

Define sentinels at package level for stable, exported failure modes:

```go
var (
    ErrNotFound      = errors.New("not found")
    ErrAlreadyExists = errors.New("already exists")
)
```

Define typed errors when callers need structured detail:

```go
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation: %s: %s", e.Field, e.Message)
}
```

Wrap them when returning so callers can both `errors.Is(err,
ErrNotFound)` and read additional context.

## Never panic in library code

Panics crash the entire program and cascade. Library code returns
errors and lets callers decide:

```go
// BAD
func ParseConfig(b []byte) *Config {
    var c Config
    if err := json.Unmarshal(b, &c); err != nil {
        panic(err)
    }
    return &c
}

// GOOD
func ParseConfig(b []byte) (*Config, error) {
    var c Config
    if err := json.Unmarshal(b, &c); err != nil {
        return nil, fmt.Errorf("parse config: %w", err)
    }
    return &c, nil
}
```

Acceptable panics: API misuse in internal code, truly unrecoverable
init in `main`, marking unreachable paths. In `main`, prefer
`log.Fatal` over `panic` — deferred functions during panic can
deadlock.

## Nil interface vs nil value

A typed nil stored in an interface is **not** a nil interface. Always
return explicit `nil`:

```go
// BAD: returns non-nil error containing a nil pointer
func find() error {
    var e *MyError
    return e
}

// GOOD
func find() error {
    var e *MyError
    if e == nil {
        return nil
    }
    return e
}
```

## Quick reference

- `if err != nil` → handle here, wrap with `%w`, or wrap with `%v`.
  Never log+return.
- Error strings: lowercase, no period, no "failed to".
- `errors.Is` for sentinels, `errors.As` for types, `errors.Join` for
  batches.
- Sentinels: `var Err... = errors.New(...)`.
- Libraries return errors; binaries log them.
- Watch out for nil-interface-with-nil-value when returning custom
  error types.
