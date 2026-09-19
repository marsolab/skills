# Go Services and CLIs — Deep Reference

Long-form rationale and edge cases behind the rules in `SKILL.md`.

---

## Project structure: start small, add structure when needed

Peter Bourgon advises: **"Most projects start as a few files in
package main at the root, staying that way until they become a couple
thousand lines."** Go's lightweight feel should be preserved. Rigid a
priori project structure typically harms more than helps —
requirements diverge, grow, and mutate.

When structure becomes necessary, the `cmd/pkg` layout works well for
applications with multiple binaries:

```text
github.com/yourorg/project/
    cmd/
        server/
            main.go
        cli/
            main.go
    pkg/
        storage/
            storage.go
            storage_test.go
        api/
            api.go
```

The `pkg/` layout (publicly importable code) is appropriate for
libraries; the `internal/` layout is appropriate for code that should
not be importable outside this module:

```text
project/
    cmd/server/main.go     # can import internal/
    internal/
        auth/auth.go       # private to this module
    pkg/
        api/api.go         # public API
```

Both are conventions, not language requirements. The Go language
treats `internal/` specially (import restrictions); `pkg/` is purely
human convention.

---

## Only main() decides command-line flags

Library code never defines flags directly. Parameters come through
constructors:

```go
// main.go
func main() {
    addr := flag.String("addr", ":8080", "listen address")
    timeout := flag.Duration("timeout", 30*time.Second, "request timeout")
    flag.Parse()

    server := service.New(service.Config{
        Addr:    *addr,
        Timeout: *timeout,
    })
}

// service/service.go
type Config struct {
    Addr    string
    Timeout time.Duration
}

func New(cfg Config) *Service {
    // ...
}
```

This makes the configuration surface explicit and self-documenting
via `-h`. Tests can construct services with arbitrary configs; you
don't have to manipulate global flag state.

---

## Flags take priority over environment variables

Support multiple configuration sources, but establish clear
precedence:

1. Command-line flags (highest priority)
1. Environment variables
1. Configuration files
1. Default values

```go
addr := flag.String("addr", "", "listen address")
flag.Parse()

if *addr == "" {
    *addr = os.Getenv("SERVER_ADDR")
}
if *addr == "" {
    *addr = ":8080"  // default
}
```

For more than a few options, consider a small Config struct populated
from each source in priority order, with one path through validation.

---

## Use struct literal initialization

Avoid multiple assignment statements that can leave objects in invalid
states:

```go
// GOOD: single initialization
server := &Server{
    Addr:         addr,
    ReadTimeout:  30 * time.Second,
    WriteTimeout: 30 * time.Second,
    Handler:      mux,
}

// BAD: multiple statements
server := &Server{}
server.Addr = addr
server.ReadTimeout = 30 * time.Second
// Oops, forgot WriteTimeout - partially initialized
```

The struct-literal form fails compilation if you mistype a field
name; the field-by-field form happily silently misconfigures.

---

## HTTP server timeouts

Default `http.Server{}` has **no** timeouts. A misbehaving client can
hold a connection forever, exhausting your file descriptors. Always
set:

- `ReadHeaderTimeout` — slowloris prevention. Critical.
- `ReadTimeout` — full request body read, including upload.
- `WriteTimeout` — response write.
- `IdleTimeout` — keepalive connections.

```go
srv := &http.Server{
    Addr:              ":8080",
    Handler:           h,
    ReadHeaderTimeout: 10 * time.Second,
    ReadTimeout:       30 * time.Second,
    WriteTimeout:      30 * time.Second,
    IdleTimeout:       120 * time.Second,
}
```

`ReadHeaderTimeout` is the most important. Without it, a slowloris
attack with no body and one byte of header per minute keeps a
connection alive for hours.

---

## HTTP response bodies must be closed and drained

```go
// WRONG position for defer
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

Always drain the body to enable connection reuse:

```go
io.Copy(io.Discard, resp.Body)
```

If you don't drain, the underlying connection is closed and a new
TCP+TLS handshake is required for the next request — a real
performance hit on hot paths.

---

## Graceful shutdown anatomy

```go
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

if err := srv.ListenAndServe(); !errors.Is(err, http.ErrServerClosed) {
    return err
}
```

What's happening:

1. `signal.NotifyContext` returns a context that's canceled when
   SIGINT or SIGTERM arrives. Cleaner than wiring a channel
   manually.
2. The shutdown goroutine waits for that signal, then calls
   `srv.Shutdown(timeoutCtx)`. `Shutdown` stops accepting new
   connections and waits for in-flight requests to complete or the
   timeout to expire.
3. `ListenAndServe` returns `http.ErrServerClosed` once `Shutdown`
   completes — that's the expected exit, not an error.

The timeout on the shutdown context exists because some clients are
slow or stuck. After 15 seconds, in-flight requests are forcibly
dropped and the server exits.

---

## CLI conventions: stderr, exit codes, --help

Standard Unix CLI conventions:

- Output to stdout, errors and progress to stderr. Pipelines that
  process data should be uncluttered by status messages.
- Exit 0 for success.
- Exit 1 for "the operation failed but the invocation was valid"
  (network down, file not found).
- Exit 2 for "the invocation itself was wrong" (bad flag, missing
  required argument).
- `-h` / `--help` / `help` print usage and exit 0.
- `--version` prints version and exits 0.

`flag.NewFlagSet(name, flag.ExitOnError)` does the right thing for
flag errors: prints usage to stderr and exits 2.

---

## Avoid http.DefaultServeMux

`http.HandleFunc` and `http.Handle` register on
`http.DefaultServeMux`. Any package in your binary — including
dependencies — can register routes there. This has caused real
incidents: a misconfigured pprof package exposed `/debug/pprof/` on
production HTTP servers because someone called
`expvar`/`net/http/pprof` in `init()`.

Use an explicit mux:

```go
mux := http.NewServeMux()
mux.HandleFunc("/health", healthHandler)
srv := &http.Server{Addr: ":8080", Handler: mux}
```

Or Chi:

```go
r := chi.NewRouter()
r.Get("/health", healthHandler)
srv := &http.Server{Addr: ":8080", Handler: r}
```

Either way, you control the routes. No surprise endpoints.

---

## main() shouldn't have defers

`os.Exit` and `log.Fatal` don't run deferred functions. If your
`main()` has cleanup defers, they don't run when the program exits
on error. The standard pattern is to delegate to a `run()` function
that returns an error:

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

`run()` can use deferred cleanup safely; `main` is reduced to error
formatting and exit code selection.
