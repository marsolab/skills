# Go Logging — Deep Reference

Long-form rationale and edge cases behind the rules in `SKILL.md`.

---

## Loggers are explicit dependencies

Never use package-level loggers. Pass loggers as constructor
parameters:

```go
// BAD: global logger
package service

var logger = log.New(os.Stderr, "", log.LstdFlags)

func Process() {
    logger.Println("processing")  // hidden dependency
}

// GOOD: explicit dependency
type Service struct {
    logger *log.Logger
}

func NewService(logger *log.Logger) *Service {
    if logger == nil {
        logger = log.New(io.Discard, "", 0)  // no-op default
    }
    return &Service{logger: logger}
}
```

Globals make tests harder (every test sees the same logger),
configuration unpredictable (which `init()` ran first?), and dependency
tracking impossible.

---

## Use structured logging in production

All production codebases require structured logging. The pre-stdlib
options:

```go
// Thanos style: go-kit/log
level.Info(logger).Log(
    "msg", "compaction completed",
    "duration", elapsed,
    "blocks", blockCount,
)

// GitLab style: Logrus
logrus.WithFields(logrus.Fields{
    "duration": elapsed,
    "blocks":   blockCount,
}).Info("compaction completed")
```

Since Go 1.21, `log/slog` covers this in the stdlib:

```go
slog.Info("compaction completed",
    slog.Duration("duration", elapsed),
    slog.Int("blocks", blockCount),
)
```

Log keys should be camelCase or snake_case (pick one) and consistent
across the codebase. Messages should be lowercase.

---

## Structured logging with log/slog

Go 1.21 added `log/slog` to the standard library, replacing the need
for third-party structured logging libraries like zap, zerolog, or
logrus for most use cases.

**Core principles:**

1. Pass `*slog.Logger` as an explicit dependency — never use package
   globals.
2. Use `slog.With` to add common attributes at construction time.
3. Use context-aware methods (`InfoContext`, `ErrorContext`) to
   propagate request-scoped data via middleware.
4. Use `slog.Group` for nested attributes.

```go
// Constructor injection
type OrderService struct {
    logger *slog.Logger
    db     *sql.DB
}

func NewOrderService(logger *slog.Logger, db *sql.DB) *OrderService {
    return &OrderService{
        logger: logger.With(slog.String("component", "order-service")),
        db:     db,
    }
}

func (s *OrderService) PlaceOrder(ctx context.Context, order Order) error {
    s.logger.InfoContext(ctx, "placing order",
        slog.Int64("user_id", order.UserID),
        slog.String("item", order.Item),
        slog.Float64("total", order.Total),
    )
    // ...
}
```

**Handler configuration in main:**

```go
func main() {
    var handler slog.Handler
    if os.Getenv("ENV") == "production" {
        handler = slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
            Level: slog.LevelInfo,
        })
    } else {
        handler = slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{
            Level: slog.LevelDebug,
        })
    }
    logger := slog.New(handler)
    slog.SetDefault(logger) // for libraries that use slog.Default()
}
```

**LogValuer for expensive computations:**

```go
type LazyJSON struct{ v any }

func (l LazyJSON) LogValue() slog.Value {
    data, _ := json.Marshal(l.v)
    return slog.StringValue(string(data))
}

// Only marshals if the log level is enabled
logger.Debug("request body", slog.Any("body", LazyJSON{req}))
```

---

## Log levels: info and debug usually suffice

Peter Bourgon's guidance: **avoid fine-grained log levels**. Info for
important operational events, debug for investigation. Warn and error
for exceptional situations requiring attention.

`slog` exposes:

- `slog.LevelDebug` (-4)
- `slog.LevelInfo`  (0)
- `slog.LevelWarn`  (4)
- `slog.LevelError` (8)

You can define custom levels (`slog.Level(12)` for "critical") but you
probably shouldn't. Adding levels invites endless debate over which to
use; sticking to the four built-ins forces clearer choices.

---

## Logging is expensive — instrument everything, log selectively

Metrics are cheap; logging is expensive. Instrument all significant
components with:

- **USE method** for resources: Utilization, Saturation, Error count
- **RED method** for endpoints: Request count, Error count, Duration

Investment order: basic metrics first, then structured logging, then
distributed tracing at scale.

When you do log, log information that a human or machine will
actually read. "Entering function X" is noise; "rejected payment due
to insufficient funds, user_id=42, amount=1.23" is signal.

---

## LogValue contract

`LogValuer` is the slog equivalent of `fmt.Stringer`. The interface:

```go
type LogValuer interface {
    LogValue() Value
}
```

Three useful patterns:

**Lazy computation** — the value is expensive (JSON marshal, hash,
DB lookup). slog only calls `LogValue()` if the record's level is
enabled.

```go
type LazyJSON struct{ v any }

func (l LazyJSON) LogValue() slog.Value {
    data, _ := json.Marshal(l.v)
    return slog.StringValue(string(data))
}
```

**Redaction** — the value contains secrets. Replace with a sanitized
representation.

```go
type Token string

func (t Token) LogValue() slog.Value {
    if len(t) < 8 {
        return slog.StringValue("<token>")
    }
    return slog.StringValue(string(t[:4]) + "..." + string(t[len(t)-4:]))
}
```

**Custom formatting** — render a complex value as a group:

```go
type User struct { ID int64; Email string; Password string }

func (u User) LogValue() slog.Value {
    return slog.GroupValue(
        slog.Int64("id", u.ID),
        slog.String("email", maskEmail(u.Email)),
        // Password omitted on purpose.
    )
}
```

---

## Library logging policy

Libraries should accept a `*slog.Logger` from callers and use it
sparingly. They must not:

- Configure handlers (that's the application's job).
- Pick levels for the application.
- Log at info+ level by default — you don't know what the host is
  trying to surface.
- Use `slog.Default()` if there's any way to pass a logger
  explicitly.

A safe library pattern:

```go
type Options struct {
    Logger *slog.Logger
    // ...
}

func New(opts Options) *Service {
    logger := opts.Logger
    if logger == nil {
        logger = slog.New(slog.NewTextHandler(io.Discard, nil))
    }
    return &Service{logger: logger}
}
```

A no-op default means callers who don't care about library logging
get silence rather than noise.
