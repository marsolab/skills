# Go HTTP

Build HTTP services with the stdlib `net/http` and
[Chi](https://github.com/go-chi/chi) for routing. Chi is small, has
zero dependencies, and is fully `net/http`-compatible.

For handler tests with `httptest`, see [Testing](../testing/guide.md). For the data layer,
see [SQL](../sql/guide.md).

## Project layout

```text
myservice/
├── cmd/server/main.go
├── internal/
│   ├── handler/         # HTTP-specific code: decoding, status codes
│   ├── service/         # business logic, no HTTP dependencies
│   └── storage/         # data access (sqlc-generated)
├── db/
│   ├── migrations/
│   └── queries/
├── go.mod
├── Makefile
└── .golangci.yml
```

The handler depends on the service; the service depends on storage.
Reverse direction is wrong and Chi types should never appear below
`internal/handler`.

## main.go pattern: flags + graceful shutdown

Keep `main` thin. The application owner waits for both the listener and the
shutdown operation; returning when `ListenAndServe` unblocks would cut off
in-flight requests before `Shutdown` finishes.

```go
func main() {
    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
    if err := run(logger); err != nil {
        logger.Error("server", slog.Any("err", err))
        os.Exit(1)
    }
}

func run(logger *slog.Logger) error {
    addr := flag.String("addr", ":8080", "listen address")
    flag.Parse()
    ctx, stop := signal.NotifyContext(context.Background(),
        os.Interrupt, syscall.SIGTERM)
    defer stop()

    srv := &http.Server{
        Addr:              *addr,
        Handler:           setupRoutes(logger),
        ReadHeaderTimeout: 10 * time.Second,
        ReadTimeout:       30 * time.Second,
        WriteTimeout:      30 * time.Second,
        IdleTimeout:       120 * time.Second,
    }
    return runServer(ctx, srv)
}

func runServer(ctx context.Context, srv *http.Server) error {
    serveErr := make(chan error, 1)
    go func() { serveErr <- srv.ListenAndServe() }()

    select {
    case err := <-serveErr:
        if errors.Is(err, http.ErrServerClosed) {
            return nil
        }
        return fmt.Errorf("listen: %w", err)
    case <-ctx.Done():
    }

    shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    shutdownErr := srv.Shutdown(shutdownCtx)
    if shutdownErr != nil {
        // Force closure only after graceful shutdown fails.
        shutdownErr = errors.Join(shutdownErr, srv.Close())
    }
    err := <-serveErr // join the listener goroutine before returning
    if errors.Is(err, http.ErrServerClosed) {
        err = nil
    }
    return errors.Join(shutdownErr, err)
}
```

The shutdown context must not inherit the already-cancelled signal context.
Coordinate application workers and upgraded connections (such as WebSockets)
separately; `Shutdown` does not wait for those. See
[Server.Shutdown](https://pkg.go.dev/net/http#Server.Shutdown).

## Routes with Chi

```go
func setupRoutes(logger *slog.Logger) http.Handler {
    r := chi.NewRouter()

    r.Use(middleware.RequestID)
    r.Use(middleware.Recoverer)
    r.Use(middleware.Timeout(30 * time.Second))
    r.Use(loggingMiddleware(logger))

    r.Get("/healthz", healthz)

    r.Route("/api/v1", func(r chi.Router) {
        r.Get("/users", listUsers)
        r.Post("/users", createUser)
        r.Get("/users/{id}", getUser)
    })
    return r
}
```

Common Chi middleware: `RequestID`, `RealIP`, `Logger` (or your own
slog-based one), `Recoverer`, `Timeout`, `Compress`. Apply auth middleware
inside `r.Group` or `r.Route` for the routes that need it. Trust forwarded
client-IP headers only behind a proxy whose forwarding behavior is controlled.

## Handler signature

```go
func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest
    r.Body = http.MaxBytesReader(w, r.Body, 1<<20)
    decoder := json.NewDecoder(r.Body)
    decoder.DisallowUnknownFields()
    if err := decoder.Decode(&req); err != nil {
        writeError(w, http.StatusBadRequest, "invalid json")
        return
    }
    if err := decoder.Decode(&struct{}{}); !errors.Is(err, io.EOF) {
        writeError(w, http.StatusBadRequest, "expected one json value")
        return
    }
    // No `defer r.Body.Close()` — the server closes the request body for
    // you; a handler-side Close adds a bare unchecked error for nothing.

    user, err := h.svc.CreateUser(r.Context(), req.Email, req.Name)
    if err != nil {
        writeServiceError(w, err)
        return
    }
    writeJSON(w, http.StatusCreated, user)
}
```

Pass `r.Context()` down to the service. That context is cancelled if the
client disconnects or the timeout middleware fires.

## URL parameters

```go
id := chi.URLParam(r, "id")
```

For typed values, parse and validate explicitly:

```go
id, err := strconv.ParseInt(chi.URLParam(r, "id"), 10, 64)
if err != nil {
    writeError(w, http.StatusBadRequest, "invalid id")
    return
}
```

## Mapping errors to status codes

Use typed errors from the service layer; the handler translates:

```go
func writeServiceError(w http.ResponseWriter, err error) {
    var verr *service.ValidationError
    switch {
    case errors.Is(err, service.ErrNotFound):
        writeError(w, http.StatusNotFound, "not found")
    case errors.As(err, &verr):
        writeError(w, http.StatusBadRequest, verr.Error())
    default:
        // log unexpected; never leak the inner error
        slog.Default().Error("internal", slog.Any("err", err))
        writeError(w, http.StatusInternalServerError, "internal error")
    }
}
```

The service layer doesn't know about HTTP. The handler is the only
layer that maps errors to status codes.

## JSON helpers

```go
func writeJSON(w http.ResponseWriter, status int, v any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    if err := json.NewEncoder(w).Encode(v); err != nil {
        // Status and headers are already on the wire, so you can't change
        // the response — but the write failed, so log it rather than
        // discarding with `_ =`. This is the rare spot you handle by
        // logging because returning the error is no longer possible.
        slog.Default().Error("encode response", slog.Any("err", err))
    }
}

func writeError(w http.ResponseWriter, status int, msg string) {
    writeJSON(w, status, map[string]string{"error": msg})
}
```

Everywhere else, propagate the error instead of logging it. Writers like
`bufio.Writer` also need `Flush` checked before the handler returns — see
the [Errors](../errors/guide.md) guide for the named-return + deferred `errors.Join` form.

## Testing handlers

```go
func TestCreateUser(t *testing.T) {
    h := &UserHandler{svc: &fakeSvc{user: User{ID: 1, Name: "ada"}}}
    r := chi.NewRouter()
    r.Post("/users", h.Create)

    body := strings.NewReader(`{"email":"a@b.c","name":"ada"}`)
    req := httptest.NewRequest(http.MethodPost, "/users", body)
    rec := httptest.NewRecorder()
    r.ServeHTTP(rec, req)

    if rec.Code != http.StatusCreated {
        t.Fatalf("status = %d, want %d", rec.Code, http.StatusCreated)
    }
}
```

`httptest.NewRequest` constructs a request without a network listener.
`httptest.NewRecorder` captures the response.

## Timeouts

Always set them. The defaults (`0`) mean "no timeout" — a slowloris
attack waits forever. A safe baseline:

| Timeout | Value | Why |
|---|---|---|
| `ReadTimeout` | 30s | Limits time to read full request |
| `WriteTimeout` | 30s | Limits time to write response |
| `IdleTimeout` | 120s | Closes idle keep-alive connections |
| `ReadHeaderTimeout` | 10s | Tighter than `ReadTimeout` for headers alone |

For uploads and streams, design the route's deadlines together with server
read/write timeouts. A handler context deadline does not reset a connection's
write deadline, and a timeout wrapper does not terminate work that ignores its
context. `http.TimeoutHandler` buffers output and is unsuitable for streaming.
Use a dedicated server or `http.ResponseController` where per-response deadline
control is needed, and test the actual streaming behavior.

## Outbound HTTP clients

Reuse a configured client/transport rather than constructing one per request.
Use `http.NewRequestWithContext`, bound the total operation or its phases, and
check status codes explicitly: a non-2xx status is not a `Client.Do` error.

```go
func fetch(ctx context.Context, client *http.Client, url string) (data []byte, rErr error) {
    req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
    if err != nil {
        return nil, fmt.Errorf("create request: %w", err)
    }
    resp, err := client.Do(req)
    if err != nil {
        return nil, fmt.Errorf("send request: %w", err)
    }
    defer func() {
        if err := resp.Body.Close(); err != nil {
            rErr = errors.Join(rErr, fmt.Errorf("close response: %w", err))
        }
    }()
    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("unexpected status: %d", resp.StatusCode)
    }
    const maxBody = 1 << 20
    data, err = io.ReadAll(io.LimitReader(resp.Body, maxBody+1))
    if err != nil {
        return nil, fmt.Errorf("read response: %w", err)
    }
    if len(data) > maxBody {
        return nil, errors.New("response exceeds size limit")
    }
    return data, nil
}
```

Read successful bodies to EOF and close them for connection reuse. For errors
or oversized bodies, prefer a bounded read/close over unbounded draining of
untrusted input. Retry only when the request can be replayed safely, within the
original deadline, with bounded attempts and backoff. Test cancellation,
unexpected status, malformed payloads, and oversized bodies with `httptest`.
See [Client.Do](https://pkg.go.dev/net/http#Client.Do).

## Related guides

| Task | Guide |
|---|---|
| Database queries via sqlc | [SQL](../sql/guide.md) |
| Request-scoped slog with attrs from context | [Logging](../logging/guide.md) |
| Typed errors and status mapping | [Errors](../errors/guide.md) |
| Handler tests with `httptest` | [Testing](../testing/guide.md) |
| Per-request goroutines, errgroup | [Concurrency](../concurrency/guide.md) |
