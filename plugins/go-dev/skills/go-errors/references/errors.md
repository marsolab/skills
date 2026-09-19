# Go Error Handling — Deep Reference

The full rationale behind the rules in `SKILL.md`, with examples and
points of disagreement across major production codebases (Google,
Thanos, CockroachDB, GitLab).

---

## Handle each error exactly once

Dave Cheney's rule: **"You should only make one decision in response to
a single error."** Don't log and return — choose one:

```go
// BAD: handles error twice
if err != nil {
    log.Printf("failed to process: %v", err)  // logs it
    return err                                  // also returns it (caller might log again)
}

// GOOD: add context and return
if err != nil {
    return fmt.Errorf("process request: %w", err)
}

// GOOD: handle completely here
if err != nil {
    log.Printf("process request failed, using default: %v", err)
    return defaultValue, nil
}
```

The cost of double-handling: log spam, lost context (each layer
truncates), and obscured root cause. The wrapper-then-return pattern
preserves the full chain; the top of the stack decides what to log.

---

## Error strings: lowercase, unpunctuated

Error messages get wrapped and concatenated; capitalization and
periods disrupt the flow:

```go
// GOOD
return fmt.Errorf("connecting to database: %w", err)
// Produces: "processing request: connecting to database: connection refused"

// BAD
return fmt.Errorf("Failed to connect to database: %w", err)
// Produces: "processing request: Failed to connect to database: Connection refused."
```

Avoid prefixes like "failed to" or "error occurred while" — they're
redundant in error context. The presence of an error already means
something failed.

---

## Choose between %v and %w deliberately

Use `%w` when callers need programmatic access via `errors.Is` and
`errors.As`. Use `%v` for simple annotation or when you want to hide
implementation details:

```go
// Expose underlying error for programmatic handling
return fmt.Errorf("database operation: %w", err)

// Hide implementation details
return fmt.Errorf("service unavailable: %v", err)
```

Thanos and CockroachDB prefer explicit `errors.Wrap` over `fmt.Errorf
+ %w` for clarity, using `github.com/pkg/errors` or
`github.com/cockroachdb/errors` respectively. The consensus across all
sources: use *some* form of wrapping — the specific library matters
less than consistent application.

---

## Structure error checks with early returns

The "line of sight" pattern keeps the success path at minimal
indentation:

```go
// GOOD: guard clauses return early
func ProcessFile(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return fmt.Errorf("open %s: %w", path, err)
    }
    defer f.Close()

    data, err := io.ReadAll(f)
    if err != nil {
        return fmt.Errorf("read %s: %w", path, err)
    }

    return process(data)
}

// BAD: nested else blocks
func ProcessFile(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return err
    } else {
        defer f.Close()
        data, err := io.ReadAll(f)
        if err != nil {
            return err
        } else {
            return process(data)
        }
    }
}
```

---

## Never panic in library code

Panics crash the entire program and cascade through distributed
systems. CockroachDB explicitly bans panics as a source of cascading
failures. **Always return errors and let callers decide**:

```go
// BAD: library panicking
func ParseConfig(data []byte) *Config {
    var cfg Config
    if err := json.Unmarshal(data, &cfg); err != nil {
        panic(err)  // crashes caller's program
    }
    return &cfg
}

// GOOD: return error
func ParseConfig(data []byte) (*Config, error) {
    var cfg Config
    if err := json.Unmarshal(data, &cfg); err != nil {
        return nil, fmt.Errorf("parse config: %w", err)
    }
    return &cfg, nil
}
```

Acceptable panic uses: API misuse in internal code (like `reflect`
package), truly unrecoverable initialization errors in `main`, or
marking unreachable code paths. Google prefers `log.Fatal` over
`panic` for startup failures — deferred functions during panic can
deadlock.

---

## errors.Join for combining multiple errors (Go 1.20+)

When collecting errors from parallel or batch operations, use
`errors.Join` instead of concatenating strings or using third-party
multi-error libraries:

```go
func ValidateConfig(cfg Config) error {
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

    return errors.Join(errs...) // returns nil if errs is empty
}
```

The joined error supports `errors.Is` and `errors.As` — each
constituent error can be matched individually:

```go
err := ValidateConfig(cfg)
if errors.Is(err, ErrInvalidPort) {
    // handles one specific sub-error
}
```

Use `errors.Join` for cleanup patterns too:

```go
func cleanup(db *sql.DB, file *os.File) error {
    return errors.Join(db.Close(), file.Close())
}
```

---

## Nil interface vs nil value in interface

An interface is only nil when **both** type and value are nil. A nil
pointer stored in an interface is not a nil interface:

```go
func returnsInterface() error {
    var err *MyError = nil
    return err  // NOT nil! Type is *MyError, value is nil
}

if err := returnsInterface(); err != nil {
    fmt.Println("error:", err)  // prints "error: <nil>"
}

// CORRECT: return explicit nil
func returnsInterface() error {
    var err *MyError = nil
    if err == nil {
        return nil  // explicit nil interface
    }
    return err
}
```

---

## Points of disagreement — error wrapping libraries

Sources disagree on error library choice:

- **Standard library**: Google recommends `fmt.Errorf` with `%w`.
- **pkg/errors**: Thanos prefers explicit `errors.Wrap`.
- **cockroachdb/errors**: CockroachDB uses their own superset with
  redaction support.

Consensus: use *some* form of wrapping; the specific library matters
less than consistent application. Within a single project, pick one
and stick with it.
