# Go Logging

Use `log/slog` (stdlib since Go 1.21) for structured logging. Pass the
logger as an explicit dependency; the package-level global is a code
smell.

For the comprehensive reference, see [logging.md](logging.md).

## Three rules

1. **Logger is a dependency**, not a global. Inject `*slog.Logger`
   through constructors.
2. **Structured everything.** No `fmt.Sprintf` into the message — put the
   variables in attributes so they're queryable.
3. **Log or return, not both.** If you `return err`, the caller logs.
   The lowest layer that *handles* the error logs once.

## Constructor injection

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

func (s *OrderService) PlaceOrder(ctx context.Context, o Order) error {
    s.logger.InfoContext(ctx, "placing order",
        slog.Int64("user_id", o.UserID),
        slog.String("item", o.Item),
        slog.Float64("total", o.Total),
    )
    // ...
}
```

`logger.With(...)` returns a new logger with the given attributes baked
in — use it at construction time so every line from this component is
tagged.

## Configure once in main

```go
func main() {
    var h slog.Handler
    if os.Getenv("ENV") == "production" {
        h = slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
            Level: slog.LevelInfo,
        })
    } else {
        h = slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{
            Level: slog.LevelDebug,
        })
    }
    logger := slog.New(h)
    slog.SetDefault(logger) // for libraries that fall back to slog.Default()
}
```

JSON in production (machine-readable for log aggregators), text in
development (human-readable in terminals).

## Context-aware methods

`InfoContext` / `ErrorContext` / etc. give middleware a hook to enrich
the record with request-scoped attributes (request ID, user, trace ID):

```go
func (s *OrderService) PlaceOrder(ctx context.Context, o Order) error {
    s.logger.InfoContext(ctx, "placing order", slog.Int64("user_id", o.UserID))
    // ...
}
```

A simple middleware that pulls request ID into every log line via a
context handler:

```go
type ctxHandler struct{ slog.Handler }

func (h ctxHandler) Handle(ctx context.Context, r slog.Record) error {
    if id, ok := ctx.Value(reqIDKey).(string); ok {
        r.AddAttrs(slog.String("request_id", id))
    }
    return h.Handler.Handle(ctx, r)
}

func (h ctxHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
    return ctxHandler{Handler: h.Handler.WithAttrs(attrs)}
}

func (h ctxHandler) WithGroup(name string) slog.Handler {
    return ctxHandler{Handler: h.Handler.WithGroup(name)}
}
```

Use a private typed context key. Wrapping `WithAttrs` and `WithGroup` keeps the
context enrichment when a caller derives a logger with `With` or `WithGroup`.
Context-aware logging does not automatically serialize all context values.
See the [Handler contract](https://pkg.go.dev/log/slog#Handler).

## LogValuer — defer expensive formatting

Don't pay to format an attribute that won't be emitted. `LogValuer` is
called only if the level is enabled:

```go
type LazyJSON struct{ v any }

func (l LazyJSON) LogValue() slog.Value {
    data, err := json.Marshal(l.v)
    if err != nil {
        return slog.StringValue("<unserializable>")
    }
    return slog.StringValue(string(data))
}

logger.Debug("request body", slog.Any("body", LazyJSON{req}))
```

Only log an explicitly redacted representation. Credentials, cookies, tokens,
and arbitrary request bodies should not become attributes.

## Levels — keep it simple

Peter Bourgon's guidance: avoid fine-grained levels.

| Level | Use for |
|---|---|
| `Debug` | Investigation aids, off in production |
| `Info` | Important operational events |
| `Warn` | Unusual but not failing |
| `Error` | Something failed and was not handled here |

If you're using `Trace`, `Verbose`, `Notice`, `Critical` — you don't
need them.

## Attributes, keys, messages

- **Message**: lowercase, no period, describes the action: `"placing order"`,
  `"compaction completed"`.
- **Keys**: `snake_case` (or `camelCase` — pick one and stay consistent).
- **Values**: typed. Prefer `slog.Int64`, `slog.String`, `slog.Duration`
  over `slog.Any` so handlers can format them well.
- **Group**: nest related attributes:

```go
logger.Info("http request",
    slog.Group("req",
        slog.String("method", r.Method),
        slog.String("path", r.URL.Path),
    ),
    slog.Int("status", status),
    slog.Duration("latency", d),
)
```

## Observability beyond logs

Logging is expensive; metrics are cheap. Instrument significant
components with metrics, log only actionable events.

- **USE** for resources: Utilization, Saturation, Errors.
- **RED** for endpoints: Rate, Errors, Duration.
- Investment order: metrics → structured logs → distributed tracing.

## Related guides

| Task | Guide |
|---|---|
| Deciding to log vs return an error | [Errors](../errors/guide.md) |
| Request-scoped logger middleware in Chi handlers | [HTTP](../http/guide.md) |
| Goroutine context propagation | [Concurrency](../concurrency/guide.md) |
| General Go idioms and naming | [Style](../style/guide.md) |
