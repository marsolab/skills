---
name: go-logging
description: >-
  Structured logging in Go with `log/slog`. Triggers when the user is
  writing or reviewing logging code in Go: `slog.Logger`, `slog.Handler`,
  `slog.With`, `slog.Group`, `LogValuer`, `InfoContext`/`ErrorContext`,
  JSON vs text handlers, log level configuration, request-scoped logging
  via context, or migrating from `log`, `zap`, `zerolog`, or `logrus`.
  Also load when the user mentions log fields, log levels, contextual
  logging, or "what should I log here?"
version: 1.0.0
tags:
  - go
  - golang
  - logging
  - slog
  - observability
---

# Go Logging with log/slog

`log/slog` (Go 1.21+) is the stdlib structured logger. Use it.
Third-party loggers (zap, zerolog, logrus) are no longer needed for
most cases.

For long-form rationale, read `references/logging.md`.

## Core principles

1. **Pass `*slog.Logger` as an explicit dependency.** No package-level
   globals.
2. **Use `slog.With` to add common attributes at construction time.**
   Don't repeat yourself in every log line.
3. **Use context-aware methods (`InfoContext`, `ErrorContext`)** so
   middleware can attach request-scoped attributes via context.
4. **Use `slog.Group`** for nested attributes that belong together
   (e.g., HTTP request fields).

## Constructor injection

Loggers travel as constructor parameters, never as package globals:

```go
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

`slog.With(...)` returns a new logger with those attributes attached
to every subsequent log line — much cleaner than repeating
`slog.String("component", "order-service")` everywhere.

## Handler configuration in main

Pick the handler at startup based on environment:

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
    // ... wire logger into services
}
```

- **JSON handler** for production. Machine-parseable, ships to log
  aggregators cleanly.
- **Text handler** for local dev. Human-readable.

## InfoContext vs Info

Always use the `*Context` variants. They let middleware attach
request-scoped attributes (request ID, user ID, trace ID) that flow
into every subsequent log line:

```go
// Middleware attaches request_id via slog.NewContext
ctx = slogctx.NewContext(ctx, logger.With("request_id", reqID))

// Handler logs with that context — request_id is included automatically
slog.InfoContext(ctx, "user signed in", "user_id", uid)
```

If you don't have a context-attribute middleware yet, the `*Context`
variants still work — they just don't pull anything extra. Costs
nothing to be ready for it.

## Attributes

Use the typed `slog.String`, `slog.Int64`, `slog.Float64`,
`slog.Time`, `slog.Duration`, `slog.Bool`, `slog.Any` for performance
(skips reflection):

```go
logger.Info("order placed",
    slog.Int64("user_id", uid),
    slog.String("item", "widget"),
    slog.Duration("elapsed", elapsed),
    slog.Float64("amount", amount),
)
```

The shorter `key, value` form also works and is fine for casual
logging:

```go
logger.Info("order placed", "user_id", uid, "item", "widget")
```

Pick a style and stay consistent within a project.

## slog.Group for nested attributes

Group related fields:

```go
logger.Info("http request",
    slog.Group("req",
        slog.String("method", r.Method),
        slog.String("path", r.URL.Path),
        slog.String("remote", r.RemoteAddr),
    ),
    slog.Group("res",
        slog.Int("status", status),
        slog.Duration("elapsed", elapsed),
    ),
)
```

JSON output:

```json
{"msg":"http request","req":{"method":"GET","path":"/api"},"res":{"status":200}}
```

This is much cleaner than flat `req_method`, `req_path`,
`req_remote` keys.

## LogValuer for expensive or sensitive values

If a value is expensive to compute or contains sensitive data, wrap
it in a `LogValuer`. The `LogValue()` method only runs if the log
level is enabled:

```go
type LazyJSON struct{ v any }

func (l LazyJSON) LogValue() slog.Value {
    data, _ := json.Marshal(l.v)
    return slog.StringValue(string(data))
}

logger.Debug("request body", slog.Any("body", LazyJSON{req}))
// Marshal only happens at debug level.
```

For redaction:

```go
type SafeUser User

func (u SafeUser) LogValue() slog.Value {
    return slog.GroupValue(
        slog.Int64("id", u.ID),
        slog.String("email", maskEmail(u.Email)),
        // password, tokens, etc. omitted
    )
}
```

## Log levels: keep it simple

- **Debug** — investigation. Off in production by default.
- **Info** — operational events ("server started", "order placed").
- **Warn** — degraded mode, recoverable problem.
- **Error** — exceptional, attention-required.

Avoid finer-grained levels (trace, fatal, etc.). They add cognitive
load without proportional value.

## What to log

Logging is expensive (CPU + storage + ingestion cost). Log only
what's actionable:

- Request start/end with key fields (method, path, status, duration).
- Errors with sufficient context to diagnose.
- Important state changes (order placed, payment captured).

Don't log:

- Function entry/exit (use tracing for that).
- Loop iterations (you'll regret it under load).
- Anything you wouldn't read at 3 AM during an incident.

Metrics are the cheap, high-volume option. Logs are the expensive
narrative for selected events. Distributed tracing is the third leg
of the stool.

## Library code

Library code should accept a `*slog.Logger` (or use
`slog.Default()`), but **never** define its own log levels, formats,
or handlers. The application owns all logging configuration.

If your library is small, consider a no-op default so callers don't
have to pass one:

```go
type Service struct {
    logger *slog.Logger
}

func New(opts Options) *Service {
    if opts.Logger == nil {
        opts.Logger = slog.New(slog.NewTextHandler(io.Discard, nil))
    }
    return &Service{logger: opts.Logger}
}
```

## Quick reference

- Inject `*slog.Logger` into constructors. No globals.
- `slog.With` for static fields per component.
- `*Context` methods (`InfoContext`, `ErrorContext`) so middleware can
  add request-scoped attributes.
- `slog.Group` for nested fields.
- `LogValuer` for lazy or redacted values.
- Levels: Debug / Info / Warn / Error. Nothing finer.
- Library code: accept a logger, never configure levels/handlers.
