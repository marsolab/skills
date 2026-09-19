---
name: go-services
description: >-
  Building HTTP services and CLI tools in Go. Triggers when the user is
  building a server, daemon, microservice, REST API, or command-line
  tool: `net/http`, Chi router, middleware, graceful shutdown, signal
  handling, `flag` and `flag.NewFlagSet` for CLI subcommands, configuration
  precedence (flags > env vars > defaults), `cmd/`/`internal/` project
  layout, project bootstrapping, or runnable binaries. Also load when the
  user asks "how should I structure this Go service?" or wants to set up
  a new Go HTTP server or CLI from scratch.
version: 1.0.0
tags:
  - go
  - golang
  - http
  - chi
  - cli
  - services
---

# Go Services and CLIs

Patterns for the two most common Go binaries: HTTP services and
command-line tools. Both share a configuration story (flags + env
vars), a logging story (`log/slog` — see `go-logging` skill), and a
project layout.

For long-form rationale, read `references/services.md`.

## HTTP service: project structure

```text
myservice/
├── cmd/
│   └── server/
│       └── main.go             # entry point — flags, wiring, signals
├── internal/
│   ├── handler/                # HTTP handlers (one file per resource)
│   ├── service/                # business logic
│   └── storage/                # DB access (or use go-databases skill's layout)
├── db/                         # if using sqlc — see go-databases skill
│   ├── migrations/
│   └── queries/
├── go.mod
├── Makefile
└── .golangci.yml
```

`main.go` owns the wiring; everything else is decoupled and
testable.

## main.go pattern

```go
package main

import (
    "context"
    "errors"
    "flag"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"
)

func main() {
    addr := flag.String("addr", ":8080", "listen address")
    flag.Parse()

    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

    srv := &http.Server{
        Addr:              *addr,
        Handler:           setupRoutes(logger),
        ReadTimeout:       30 * time.Second,
        ReadHeaderTimeout: 10 * time.Second,
        WriteTimeout:      30 * time.Second,
        IdleTimeout:       120 * time.Second,
    }

    // Graceful shutdown.
    shutdownCtx, stop := signal.NotifyContext(context.Background(),
        os.Interrupt, syscall.SIGTERM)
    defer stop()

    go func() {
        <-shutdownCtx.Done()
        ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
        defer cancel()
        if err := srv.Shutdown(ctx); err != nil {
            logger.Error("server shutdown", "err", err)
        }
    }()

    logger.Info("server starting", "addr", *addr)
    if err := srv.ListenAndServe(); !errors.Is(err, http.ErrServerClosed) {
        logger.Error("server error", "err", err)
        os.Exit(1)
    }
    logger.Info("server stopped")
}
```

Key points:

- **Always set `ReadHeaderTimeout`** — without it, slowloris attacks
  trivially exhaust the server.
- **Use `signal.NotifyContext`** instead of manually wiring a
  channel; cancellation propagates to handlers via context.
- **`http.ErrServerClosed`** is the expected error after a graceful
  shutdown; don't treat it as failure.

## Routing with Chi

[Chi](https://github.com/go-chi/chi) is a small, stdlib-compatible
router. No magic, idiomatic middleware:

```go
import (
    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
)

func setupRoutes(logger *slog.Logger) http.Handler {
    r := chi.NewRouter()

    r.Use(middleware.RequestID)
    r.Use(middleware.RealIP)
    r.Use(middleware.Recoverer)
    r.Use(middleware.Timeout(60 * time.Second))

    r.Route("/api/v1", func(r chi.Router) {
        r.Get("/health", healthHandler)

        r.Route("/users", func(r chi.Router) {
            r.Post("/", createUser)
            r.Get("/{id}", getUser)
            r.Get("/", listUsers)
        })
    })

    return r
}
```

URL parameters: `chi.URLParam(r, "id")`. Mount sub-routers with
`r.Route` to keep handler files focused.

## Handler shape

Handlers are plain `http.HandlerFunc`s. Keep them small — parse,
delegate, render:

```go
func (h *UserHandler) Get(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()
    idStr := chi.URLParam(r, "id")
    id, err := strconv.ParseInt(idStr, 10, 64)
    if err != nil {
        http.Error(w, "invalid id", http.StatusBadRequest)
        return
    }

    user, err := h.service.Get(ctx, id)
    if err != nil {
        if errors.Is(err, ErrNotFound) {
            http.Error(w, "not found", http.StatusNotFound)
            return
        }
        h.logger.ErrorContext(ctx, "get user", "err", err, "id", id)
        http.Error(w, "internal", http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    if err := json.NewEncoder(w).Encode(user); err != nil {
        h.logger.ErrorContext(ctx, "encode user", "err", err)
    }
}
```

Don't bury business logic in handlers — call into a service layer
that doesn't import `net/http`.

## Configuration precedence

1. Command-line flags (highest).
2. Environment variables.
3. Configuration file (if used).
4. Defaults (lowest).

```go
addr := flag.String("addr", "", "listen address")
flag.Parse()

if *addr == "" {
    *addr = os.Getenv("SERVER_ADDR")
}
if *addr == "" {
    *addr = ":8080"
}
```

`flag.Parse()` runs only in `main()`. Library code never declares
flags — accept config via constructor:

```go
// service/service.go
type Config struct {
    Addr    string
    Timeout time.Duration
}

func New(cfg Config) *Service { ... }
```

This keeps `-h` self-documenting and library code reusable.

## CLI tool: project structure

```text
mycli/
├── main.go             # or cmd/mycli/main.go for multi-binary repos
├── internal/
│   └── command/        # one file per subcommand
├── go.mod
└── .golangci.yml
```

For single-binary CLIs, `main.go` at the root is fine. Don't impose
`cmd/` until you have a second binary.

## Subcommands with flag.NewFlagSet

For CLIs with subcommands (`mytool fetch`, `mytool list`), use the
stdlib `flag.NewFlagSet`. Cobra is fine when you're already invested,
but stdlib flag covers most needs without a dependency:

```go
func main() {
    if len(os.Args) < 2 {
        usage()
        os.Exit(2)
    }

    switch os.Args[1] {
    case "fetch":
        cmdFetch(os.Args[2:])
    case "list":
        cmdList(os.Args[2:])
    case "version":
        fmt.Println(version)
    case "-h", "--help", "help":
        usage()
    default:
        fmt.Fprintf(os.Stderr, "unknown command: %s\n", os.Args[1])
        usage()
        os.Exit(2)
    }
}

func cmdFetch(args []string) {
    fs := flag.NewFlagSet("fetch", flag.ExitOnError)
    var (
        url     = fs.String("url", "", "URL to fetch")
        timeout = fs.Duration("timeout", 30*time.Second, "request timeout")
    )
    fs.Parse(args)

    if *url == "" {
        fmt.Fprintln(os.Stderr, "fetch: --url is required")
        os.Exit(2)
    }
    if err := fetch(*url, *timeout); err != nil {
        fmt.Fprintf(os.Stderr, "fetch: %v\n", err)
        os.Exit(1)
    }
}
```

## CLI conventions

- **Errors to stderr, output to stdout.** Pipes work; redirection
  works.
- **Exit code 0** on success. **2** on usage error (bad flags). **1**
  on operational error.
- **`-h`/`--help`** prints usage and exits 0.
- **`--version`** prints version and exits 0.

## Pitfalls

### HTTP response bodies must be closed and drained

```go
// WRONG: defer position
resp, err := http.Get(url)
defer resp.Body.Close()  // resp may be nil!
if err != nil {
    return err
}

// CORRECT
resp, err := http.Get(url)
if err != nil {
    return err
}
defer resp.Body.Close()

// BEST: handle redirect failures (both resp and err non-nil)
resp, err := http.Get(url)
if resp != nil {
    defer resp.Body.Close()
}
if err != nil {
    return err
}
```

Drain the body to enable connection reuse:

```go
io.Copy(io.Discard, resp.Body)
```

### Default mux is a footgun

`http.HandleFunc` registers on `http.DefaultServeMux`, which is
package-global. Anyone in your binary (including dependencies) can
add routes you didn't authorize. Use an explicit `http.NewServeMux()`
or Chi's `chi.NewRouter()`.

### main() panics or os.Exits

`os.Exit` skips deferred functions — don't `defer` cleanup in `main()`
and then `os.Exit(1)` on error. Either return from `main` (no exit
code beyond 0/1 success/failure based on log.Fatal) or arrange for
explicit cleanup before exit.

```go
// BAD: defers don't run
func main() {
    f, _ := os.Create("out.log")
    defer f.Close()         // never runs
    if err := work(); err != nil {
        os.Exit(1)
    }
}

// GOOD: separate exit-coded run from main
func main() {
    if err := run(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}

func run() error {
    f, err := os.Create("out.log")
    if err != nil {
        return err
    }
    defer f.Close()  // runs on every return
    return work()
}
```

## Quick reference

- `cmd/<binary>/main.go` for entry points; `internal/` for private
  code.
- `signal.NotifyContext` + `srv.Shutdown(ctx)` for graceful HTTP
  shutdown.
- Always set `ReadHeaderTimeout` on `http.Server`.
- Chi for routing; small middleware chain at the top.
- Flags > env > defaults. `flag.Parse()` only in `main()`.
- For CLIs: `flag.NewFlagSet` per subcommand; errors to stderr; exit
  codes 0/1/2.
- Pitfalls: HTTP body close ordering, default mux, `os.Exit` skipping
  defers.
