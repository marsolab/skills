# The Comprehensive Go Style Guide

This guide synthesizes guidance from Go's official documentation, Google's
internal standards, and battle-tested production codebases at CockroachDB,
GitLab, and Thanos. It serves both human developers seeking idiomatic Go
patterns and AI coding agents requiring structured, actionable rules. **The core
philosophy is clear: Go code should be readable, maintainable, and
explicit**—favoring clarity over cleverness in every design decision.

---

## Foundational principles that shape every guideline

Go's design philosophy flows from a single insight: **"Software engineering is
what happens to programming when you add time and other programmers."** Code
will be read far more than written, maintained by people who didn't write it,
and debugged under pressure at 3 AM. Every guideline here serves readability and
maintainability.

The Zen of Go, articulated by Dave Cheney, captures ten engineering values that
should guide decisions:

1. **Each package fulfills a single purpose**—name it with an elevator pitch
  using one word
1. **Handle errors explicitly**—the verbosity of `if err != nil` outweighs the
  value of deliberately handling each failure
1. **Return early rather than nesting deeply**—keep the success path to the left
1. **Leave concurrency to the caller**—don't force async on consumers
1. **Before launching a goroutine, know when it will stop**—goroutines own
  resources
1. **Avoid package-level state**—reduce coupling and spooky action at a distance
1. **Simplicity matters**—simple doesn't mean crude; it means readable and
  maintainable
1. **Write tests to lock in API behavior**—tests are contracts written in code
1. **Prove slowness with benchmarks before optimizing**—crimes against
  maintainability are committed in the name of performance
1. **Moderation is a virtue**—use goroutines, channels, interfaces in moderation

---

## Naming conventions establish code clarity

**Poor naming is symptomatic of poor design.** Good names are concise,
descriptive, and predictable—readers should know how to use something without
consulting documentation.

### Package names should be lowercase, singular, and unique

Packages must be lowercase single words without underscores or mixedCaps. The
package name becomes a prefix for all exported identifiers, so avoid redundancy:

```go
// BAD: redundant package prefix
package chubby
type ChubbyFile struct{}  // caller writes chubby.ChubbyFile

// GOOD: package name provides context
package chubby
type File struct{}  // caller writes chubby.File
```

Avoid meaningless names like `util`, `common`, `misc`, `api`, `types`, or
`helpers`. If two packages seem to need the same name, either they overlap in
responsibility or the name is too generic. Production codebases enforce unique
package names across the entire project to prevent `goimports`
confusion—CockroachDB uses parent-prefixed names like `server/serverpb`,
`kv/kvserver`, and `util/contextutil`.

### Variable length should correlate with scope distance

The distance between declaration and final use determines appropriate name
length. Short names work when context is clear and scope is small:

```go
// Short scope: short name
for i, v := range items {
    process(v)
}

// Longer scope: longer name
customerOrderHistory := fetchOrdersForCustomer(customerID)
// ... many lines later ...
processOrderHistory(customerOrderHistory)
```

**Use `var` for zero-value declarations, `:=` for initializations.** The `var`
keyword signals deliberate use of the zero value:

```go
var players int              // deliberately zero
things := make([]Thing, 0)   // initialized to specific state
```

### Exported names follow strict conventions

Getters omit `Get` prefix; setters use `Set` prefix:

```go
// GOOD
owner := obj.Owner()
obj.SetOwner(user)

// BAD
owner := obj.GetOwner()
```

Acronyms maintain consistent casing—`URL` appears as `URL` or `url`, never
`Url`. Write `ServeHTTP` not `ServeHttp`, `xmlHTTPRequest` not `XmlHttpRequest`,
and `appID` not `appId`.

### Interfaces name the behavior with an -er suffix

One-method interfaces derive names from the method plus `-er`: `Reader`,
`Writer`, `Formatter`, `CloseNotifier`. When implementing well-known interfaces,
match the established signature exactly—name your string converter `String()`
not `ToString()`.

### Constants avoid SCREAMING_CASE

Go uses mixedCaps for constants, matching other identifiers:

```go
// GOOD
const maxConnections = 100
const DefaultTimeout = 30 * time.Second

// BAD (not idiomatic Go)
const MAX_CONNECTIONS = 100
```

Use `iota` for enumerated constants, typically skipping zero if it could mask
missing initialization:

```go
type Status int
const (
    _             Status = iota  // skip zero
    StatusPending                // 1
    StatusActive                 // 2
    StatusClosed                 // 3
)
```

---

## Code organization emerges from simplicity

### Start small and add structure only when needed

Peter Bourgon advises: **"Most projects start as a few files in package main at
the root, staying that way until they become a couple thousand lines."** Go's
lightweight feel should be preserved. Rigid a priori project structure typically
harms more than helps—requirements diverge, grow, and mutate.

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

### Packages should fulfill a single purpose

Create packages when you have self-contained functionality, need protobuf
definitions, find a package grown too large (slow tests, insufficient
encapsulation), or have reusable code another team needs. Orient packages around
**business domains rather than implementation accidents**—prefer `package user`
over `package models`.

Google's guidance on file organization: **"There is no 'one type, one file'
convention."** Files should be focused enough that maintainers know where to
find things, and small enough to navigate easily. The standard library's
`net/http` package demonstrates this: `client.go`, `server.go`, `cookie.go`,
`transport.go`.

### Import grouping follows a standard order

Separate imports into groups: standard library, external dependencies, internal
packages:

```go
import (
    "context"
    "fmt"
    "time"

    "github.com/pkg/errors"
    "go.uber.org/zap"

    "github.com/yourorg/project/pkg/storage"
)
```

Always use fully-qualified import paths, never relative imports. GitLab enforces
this with `goimports -local gitlab.com/gitlab-org`.

---

## Error handling demands explicit attention

### Handle each error exactly once

Dave Cheney's rule: **"You should only make one decision in response to a single
error."** Don't log and return—choose one:

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

### Error strings should be lowercase and unpunctuated

Error messages get wrapped and concatenated; capitalization and periods disrupt
the flow:

```go
// GOOD
return fmt.Errorf("connecting to database: %w", err)
// Produces: "processing request: connecting to database: connection refused"

// BAD
return fmt.Errorf("Failed to connect to database: %w", err)
// Produces: "processing request: Failed to connect to database: Connection refused."
```

Avoid prefixes like "failed to" or "error occurred while"—they're redundant in
error context.

### Choose between %v and %w deliberately

Use `%w` when callers need programmatic access via `errors.Is` and `errors.As`.
Use `%v` for simple annotation or when you want to hide implementation details:

```go
// Expose underlying error for programmatic handling
return fmt.Errorf("database operation: %w", err)

// Hide implementation details
return fmt.Errorf("service unavailable: %v", err)
```

Thanos and CockroachDB prefer explicit `errors.Wrap` over `fmt.Errorf + %w` for
clarity, using `github.com/pkg/errors` or `github.com/cockroachdb/errors`
respectively.

### Structure error checks with early returns

The "line of sight" pattern keeps the success path at minimal indentation:

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

### Never panic in library code

Panics crash the entire program and cascade through distributed systems.
CockroachDB explicitly bans panics as a source of cascading failures. **Always
return errors and let callers decide**:

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

Acceptable panic uses: API misuse in internal code (like `reflect` package),
truly unrecoverable initialization errors in `main`, or marking unreachable code
paths. Google prefers `log.Fatal` over `panic` for startup failures since
deferred functions during panic can deadlock.

---

## Testing follows straightforward patterns

### Use table-driven tests with named fields

Table-driven tests are the Go standard for comprehensive coverage with minimal
duplication:

```go
func TestParseHost(t *testing.T) {
    tests := []struct {
        name         string
        input        string
        expectedHost string
        expectedPort string
        expectedErr  bool
    }{
        {
            name:         "host and port",
            input:        "example.com:8080",
            expectedHost: "example.com",
            expectedPort: "8080",
        },
        {
            name:         "host only",
            input:        "example.com",
            expectedHost: "example.com",
            expectedPort: "",
        },
        {
            name:        "invalid format",
            input:       ":::invalid",
            expectedErr: true,
        },
    }

    for _, tc := range tests {
        t.Run(tc.name, func(t *testing.T) {
            host, port, err := ParseHost(tc.input)
            if tc.expectedErr {
                if err == nil {
                    t.Fatal("expected error, got nil")
                }
                return
            }
            if err != nil {
                t.Fatalf("unexpected error: %v", err)
            }
            if host != tc.expectedHost {
                t.Errorf("host = %q, want %q", host, tc.expectedHost)
            }
            if port != tc.expectedPort {
                t.Errorf("port = %q, want %q", port, tc.expectedPort)
            }
        })
    }
}
```

Use **named struct fields** for readability when test cases span multiple lines.
The variable conventions across production codebases: test slice named `tests`,
loop variable `tc` or `tt`, description field `name`.

### Write useful failure messages

Test failures should identify what went wrong, with what inputs, what was
expected, and what was received:

```go
// GOOD: actionable failure message
if got != want {
    t.Errorf("Square(%d) = %d; want %d", input, got, want)
}

// BAD: unhelpful failure
if got != want {
    t.Error("test failed")
}
```

The convention is `got, want` order matching
`Errorf("got %v, want %v", got, want)`.

### Mark test helpers with t.Helper()

Helper functions should call `t.Helper()` so failure line numbers point to the
actual test:

```go
func assertNoError(t *testing.T, err error) {
    t.Helper()
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
}
```

Use `t.Fatal` for setup failures that prevent continuation, `t.Error` with
`continue` in table tests to run remaining cases.

### Skip integration tests with environment checks, not build tags

Peter Bourgon's evolved recommendation (2021): **Build tags hide test failures
and are non-discoverable.** Use environment variable checks instead:

```go
// GOOD: discoverable skip
func TestDatabaseIntegration(t *testing.T) {
    dsn := os.Getenv("TEST_DATABASE_URL")
    if dsn == "" {
        t.Skip("set TEST_DATABASE_URL to run this test")
    }
    db, err := sql.Open("postgres", dsn)
    // ...
}

// AVOID: build tags hide tests
// +build integration
func TestDatabaseIntegration(t *testing.T) {
    // ...
}
```

The `t.Skip` approach surfaces in test output, making it clear when tests are
skipped and why.

### Google prohibits third-party testing frameworks

Within Google's codebase, assertion libraries like testify and testing
frameworks like ginkgo are explicitly banned. The standard `testing` package
suffices. GitLab permits testify but follows the expected-first convention:
`require.Equal(t, want, got)`.

---

## Concurrency requires disciplined goroutine management

### Never start a goroutine without knowing when it will stop

This is the single most important concurrency guideline, repeated across all
sources. Goroutines own resources—locks, memory, connections—that only get freed
when the goroutine exits:

```go
// BAD: goroutine may never terminate
func startWorker() {
    go func() {
        for {
            process(<-workChan)  // blocked forever if workChan abandoned
        }
    }()
}

// GOOD: explicit termination
func startWorker(ctx context.Context) {
    go func() {
        for {
            select {
            case work := <-workChan:
                process(work)
            case <-ctx.Done():
                return
            }
        }
    }()
}
```

### Leave concurrency to the caller

Don't force async execution on consumers. Let them choose whether to run your
code in a goroutine:

```go
// BAD: forces concurrency
func ListFiles(dir string) <-chan string {
    ch := make(chan string)
    go func() {
        filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
            ch <- path
            return nil
        })
        close(ch)
    }()
    return ch
}

// GOOD: caller decides
func ListFiles(dir string, fn func(string) error) error {
    return filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
        if err != nil {
            return err
        }
        return fn(path)
    })
}
```

The bad pattern can't distinguish errors from empty directories and forces
callers to drain the channel even when they've found their answer.

### Use sync.WaitGroup for goroutine coordination

```go
var wg sync.WaitGroup
for _, item := range items {
    wg.Add(1)
    go func(item Item) {
        defer wg.Done()
        process(item)
    }(item)  // pass by value to avoid closure capture bug
}
wg.Wait()
```

### Context must be the first parameter

```go
func ProcessRequest(ctx context.Context, req *Request) (*Response, error) {
    // ...
}
```

Never store context in structs—pass it explicitly through each call. The
cancellation of a context argument implies interruption of the function
receiving it.

### Channel buffer sizes should be zero or one

CockroachDB's rule: **any buffer size other than 0 or 1 requires scrutiny**.
Larger buffers often mask synchronization bugs. When you need buffering,
document why that specific size was chosen.

---

## Interface design emphasizes small, consumer-defined contracts

### Define interfaces at the consumption site, not the implementation

Go's structural typing means interfaces should be defined where they're used,
not where implementations live:

```go
// GOOD: interface defined by consumer
package storage

type Reader interface {
    Read(ctx context.Context, key string) ([]byte, error)
}

func NewCache(r Reader) *Cache {
    return &Cache{backend: r}
}

// BAD: interface defined by implementor
package database

type Database interface {  // don't do this
    Read(ctx context.Context, key string) ([]byte, error)
    Write(ctx context.Context, key string, value []byte) error
    Delete(ctx context.Context, key string) error
}

func New() Database { return &db{} }
```

The consuming package declares only the methods it actually needs, enabling easy
mocking and loose coupling.

### Prefer one-method interfaces

Small interfaces compose better and describe precise behavioral contracts. The
standard library exemplifies this: `io.Reader`, `io.Writer`, `io.Closer`,
`fmt.Stringer`. Thanos explicitly recommends **1-3 methods maximum**:

```go
// GOOD: narrow interfaces
type Compactor interface {
    Compact(ctx context.Context) error
}

type MetaFetcher interface {
    Fetch(ctx context.Context) ([]Meta, error)
}

// BAD: kitchen-sink interface
type Service interface {
    Compact(ctx context.Context) error
    Fetch(ctx context.Context) ([]Meta, error)
    Store(ctx context.Context, data []byte) error
    Delete(ctx context.Context, id string) error
    List(ctx context.Context) ([]string, error)
    // ... more methods
}
```

### Accept interfaces, return concrete types

Functions should accept interface parameters for flexibility but return concrete
types so implementations can add methods without breaking callers:

```go
// GOOD
func NewServer(logger Logger) *Server {
    return &Server{logger: logger}
}

// The hash library exception: when multiple implementations exist
// for a common interface, returning the interface makes sense
func NewSHA256() hash.Hash { return &sha256{} }
```

### The empty interface says nothing

`interface{}` (or `any`) communicates zero information about expected behavior.
Use specific interfaces when possible, and when using empty interface, document
what types are actually expected.

---

## Documentation follows godoc conventions

### Comment every exported symbol with the symbol's name

Comments become godoc output. Start with the identifier name:

```go
// Server handles incoming HTTP requests for the API.
// It maintains connection pools and manages request routing.
type Server struct {
    // ...
}

// ListenAndServe starts the server on the given address.
// It blocks until the server is shut down or an error occurs.
func (s *Server) ListenAndServe(addr string) error {
    // ...
}
```

### Comments must be complete sentences

Start with uppercase, end with a period. This is enforced by linters in Thanos
and other production codebases.

### Document the why, not the obvious what

Good comments explain **why** something is done, not **what** the code literally
does:

```go
// BAD: restates the code
// Increment counter by one.
counter++

// GOOD: explains rationale
// Track total requests for rate limiting decisions.
// This counter resets hourly via the cleanup goroutine.
counter++
```

### Package documentation goes in doc.go or any file

Place a package comment immediately before the `package` declaration:

```go
// Package storage provides a unified interface for persisting
// application data across multiple backend implementations.
//
// The primary types are Store for read-write access and
// ReadOnlyStore for cached, read-only views.
package storage
```

For commands, use `// Command myapp ...` or simply `// Myapp ...`.

---

## Performance optimization requires measurement first

### Prove slowness with benchmarks before optimizing

Dave Cheney warns: **"So many crimes against maintainability are committed in
the name of performance."** Optimization couples code tightly, tears down
abstractions, and exposes internals. Only pay that cost when benchmarks prove
necessity.

```go
func BenchmarkProcess(b *testing.B) {
    data := generateTestData()
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```

### Preallocate slices and maps with known sizes

When size is known or estimable, preallocate:

```go
// GOOD: preallocate
results := make([]Result, 0, len(inputs))
for _, input := range inputs {
    results = append(results, process(input))
}

// Map with size hint
cache := make(map[string]Value, expectedSize)
```

But don't over-allocate—wasted memory harms performance too.

### Use strings.Builder for iterative string construction

```go
// GOOD: efficient for multiple appends
var b strings.Builder
for _, part := range parts {
    b.WriteString(part)
}
result := b.String()

// GOOD: simple concatenation
key := "prefix:" + id

// GOOD: formatting
msg := fmt.Sprintf("%s [%s:%d]", name, host, port)
```

### Hot-path optimizations (CockroachDB guidance)

On critical paths, `strconv` outperforms `fmt`:

```go
// Hot path: 64 ns/op, 1 alloc
s := strconv.Itoa(n)

// Cold path okay: 143 ns/op, 2 allocs
s := fmt.Sprint(n)
```

Convert strings to bytes once when writing repeatedly:

```go
// GOOD: convert once
data := []byte("fixed string")
for i := 0; i < n; i++ {
    w.Write(data)
}
```

---

## Common pitfalls every Go developer encounters

### Loop variable capture in closures

The most common Go bug: closures capture loop variables by reference, seeing the
final value:

```go
// BAD: all goroutines see same value
for _, item := range items {
    go func() {
        process(item)  // captures reference, sees final item
    }()
}

// GOOD: pass as parameter
for _, item := range items {
    go func(item Item) {
        process(item)
    }(item)
}

// GOOD: shadow with local copy
for _, item := range items {
    item := item  // shadow
    go func() {
        process(item)
    }()
}
```

### Nil interface vs nil value in interface

An interface is only nil when **both** type and value are nil. A nil pointer
stored in an interface is not a nil interface:

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

### Variable shadowing silently breaks logic

The `:=` operator creates new variables, potentially shadowing outer scope:

```go
// BAD: ctx gets shadowed
func handle(ctx context.Context) {
    if needsTimeout {
        ctx, cancel := context.WithTimeout(ctx, time.Second)  // shadows!
        defer cancel()
    }
    // ctx here is the ORIGINAL, not the timeout version
    doWork(ctx)
}

// GOOD: declare cancel separately
func handle(ctx context.Context) {
    if needsTimeout {
        var cancel func()
        ctx, cancel = context.WithTimeout(ctx, time.Second)  // assigns
        defer cancel()
    }
    doWork(ctx)
}
```

Use `go vet -shadow` to detect shadowing.

### Defer timing and argument evaluation

Defer arguments evaluate immediately; the deferred function executes at function
end:

```go
// Arguments evaluated NOW, function runs LATER
func example() {
    i := 1
    defer fmt.Println(i)  // captures 1
    i = 2
    // prints: 1
}

// Defers run at function end, not block end
for _, f := range files {
    file, _ := os.Open(f)
    defer file.Close()  // ALL close at function end, not loop iteration
}

// CORRECT: use closure for per-iteration cleanup
for _, f := range files {
    func() {
        file, _ := os.Open(f)
        defer file.Close()  // closes after this iteration
        process(file)
    }()
}
```

### Map operations require initialization and aren't thread-safe

```go
// PANIC: nil map write
var m map[string]int
m["key"] = 1  // panic!

// CORRECT
m := make(map[string]int)
m["key"] = 1

// Check existence with comma-ok
if val, ok := m["key"]; ok {
    use(val)
}

// Concurrent access requires sync.Mutex or sync.Map
```

### Range returns copies, not references

```go
// BAD: modifies copy
for _, item := range items {
    item.count++  // doesn't affect original
}

// GOOD: use index
for i := range items {
    items[i].count++
}
```

### Slice reslicing shares backing array

```go
// DANGER: modifying one affects the other
original := []byte("AAAA/BBBBB")
first := original[:4]
first = append(first, "XXX"...)  // overwrites original[4:]!

// SAFE: full slice expression limits capacity
first := original[:4:4]  // [low:high:max]
first = append(first, "XXX"...)  // allocates new array
```

### HTTP response bodies must be closed and drained

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
`io.Copy(io.Discard, resp.Body)`.

---

## Logging and observability patterns

### Loggers are explicit dependencies

Never use package-level loggers. Pass loggers as constructor parameters:

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

### Use structured logging in production

All production codebases require structured logging. GitLab uses Logrus via
LabKit, Thanos uses go-kit/log:

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

Log keys should be camelCase and consistent across the codebase. Messages should
be lowercase.

### Log levels: info and debug usually suffice

Peter Bourgon's guidance: **avoid fine-grained log levels**. Info for important
operational events, debug for investigation. Warn and error for exceptional
situations requiring attention.

Logging is expensive. Log only actionable information that a human or machine
will actually read.

### Instrument everything, investigate selectively

Metrics are cheap; logging is expensive. Instrument all significant components
with:

- **USE method** for resources: Utilization, Saturation, Error count
- **RED method** for endpoints: Request count, Error count, Duration

Investment order: basic metrics first, then structured logging, then distributed
tracing at scale.

---

## Configuration follows explicit patterns

### Only main() decides command-line flags

Library code never defines flags directly. Parameters come through constructors:

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

This makes the configuration surface explicit and self-documenting via `-h`.

### Flags take priority over environment variables

Support multiple configuration sources, but establish clear precedence:

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

### Use struct literal initialization

Avoid multiple assignment statements that can leave objects in invalid states:

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

---

## Dependency management with Go modules

### Libraries must never vendor dependencies

Vendoring is for binaries only. Libraries with vendored dependencies are
impossible to use because consumers face dependency conflicts. From the binary
author's perspective, vendoring ensures reproducible builds.

### Use the internal package for private code

Code in `internal/` is only importable by packages rooted at the parent of
`internal/`. This enforces API boundaries:

```text
project/
    cmd/server/main.go     # can import internal/
    internal/
        auth/auth.go       # private to this module
    pkg/
        api/api.go         # public API
```

---

## Tooling and linting requirements

### Required tools across production codebases

- **gofmt** / **goimports**: Non-negotiable formatting
- **go vet**: Catches common mistakes
- **golangci-lint**: Meta-linter running multiple checks

GitLab's CI configuration:

```yaml
lint:
  image: golangci/golangci-lint:v1.56.2
  script:
    - golangci-lint run --out-format code-climate:gl-code-quality-report.json
```

### Commonly enabled linters

- **errcheck**: Ensures errors aren't ignored
- **govet**: Official Go analyzer
- **staticcheck**: Comprehensive static analysis
- **unused**: Finds unused code
- **misspell**: Catches typos in comments and strings
- **prealloc**: Suggests slice preallocation
- **gosec**: Security-focused analysis

---

## Points of disagreement and alternative approaches

### Error wrapping libraries

Sources disagree on error library choice:

- **Standard library**: Google recommends `fmt.Errorf` with `%w`
- **pkg/errors**: Thanos prefers explicit `errors.Wrap`
- **cockroachdb/errors**: CockroachDB uses their own superset with redaction
  support

The consensus: use *some* form of wrapping; the specific library matters less
than consistent application.

### Project structure

- **Peter Bourgon (2016)**: Recommended cmd/pkg structure
- **Peter Bourgon (2018)**: Softened stance—start simple, add structure only
  when needed
- **Google**: No prescribed structure; organize by maintainability

The consensus: avoid premature structure, but cmd/pkg works when complexity
warrants it.

### Test assertions

- **Google**: Forbids assertion libraries; use standard testing package
- **GitLab**: Permits testify for assertions
- **Peter Bourgon**: Testing DSLs increase cognitive burden

The consensus: the standard library suffices; third-party frameworks are
optional convenience.

### Receiver type consistency

- **Google Code Review Comments**: Don't mix receiver types on one type
- **Effective Go**: Choose based on method needs

Practical guidance: if any method needs a pointer receiver (mutation, large
struct, sync primitives), use pointer receivers for all methods on that type.

---

## Quick reference for AI coding agents

When generating Go code, apply these rules:

### NAMING

- Packages: lowercase, singular, no underscores
- Variables: short names for short scope, longer for wider scope
- Exported: PascalCase; unexported: camelCase
- Acronyms: consistent case (URL not Url, ID not Id)
- Getters: no Get prefix; setters: Set prefix

### STRUCTURE

- Error check immediately after call
- Return early with guard clauses
- Keep success path left-aligned
- Group imports: stdlib, external, internal

### ERRORS

- Always check returned errors
- Wrap with context: `fmt.Errorf("operation: %w", err)`
- Lowercase, no punctuation in messages
- Handle exactly once: log OR return, not both
- Never panic in libraries

### CONCURRENCY

- Context as first parameter
- Know when every goroutine stops
- Use sync.WaitGroup for coordination
- Don't force concurrency on callers

### INTERFACES

- Define at consumption site
- Keep small (1-3 methods)
- Accept interfaces, return concrete types

### TESTING

- Table-driven with named fields
- Use t.Run for subtests
- Call t.Helper() in helpers
- Message format: `got X, want Y`

### MODERN GO (1.18+)

- Generics: use for data structures and utilities, not behavior abstraction
- `log/slog`: pass as dependency, use `InfoContext`/`ErrorContext`, JSON in prod
- `errors.Join`: combine multiple errors, supports `errors.Is`/`errors.As`
- Iterators (`iter.Seq`/`iter.Seq2`): lazy evaluation, composable pipelines
- Range-over-int: `for i := range n` (Go 1.22+)
- `slices`/`maps`/`cmp` packages: prefer over hand-written utilities

### CRITICAL PITFALLS TO AVOID

- Loop variable capture: pass to closure or shadow
- Nil interface check: interface with nil value ≠ nil
- Variable shadowing: use = not := when reassigning
- Defer in loops: wrap in closure for per-iteration cleanup
- Map writes to nil: always initialize with make()

---

## Modern Go patterns (1.18+)

### Generics: when and how to use type parameters

Go 1.18 introduced type parameters. The key principle: **generics reduce
duplication without sacrificing readability**. If a generic version is harder
to understand than two concrete versions, skip generics.

**When to use generics:**

- Data structures that work across element types (caches, trees, pools)
- Utility functions on slices, maps, or channels (filter, map, reduce)
- When type constraints eliminate runtime type assertions

**When NOT to use generics:**

- The function body would need type assertions anyway
- A concrete type or `any` works fine
- The generic version is harder to read for marginal DRY benefit
- You're abstracting over behavior, not data shape — use interfaces instead

```go
// GOOD: generic data structure
type Cache[K comparable, V any] struct {
    mu    sync.RWMutex
    items map[K]cacheItem[V]
}

type cacheItem[V any] struct {
    value     V
    expiresAt time.Time
}

func NewCache[K comparable, V any]() *Cache[K, V] {
    return &Cache[K, V]{items: make(map[K]cacheItem[V])}
}

func (c *Cache[K, V]) Get(key K) (V, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    item, ok := c.items[key]
    if !ok || time.Now().After(item.expiresAt) {
        var zero V
        return zero, false
    }
    return item.value, true
}
```

```go
// GOOD: constrained utility
type Ordered interface {
    ~int | ~int8 | ~int16 | ~int32 | ~int64 |
    ~uint | ~uint8 | ~uint16 | ~uint32 | ~uint64 |
    ~float32 | ~float64 | ~string
}

func Min[T Ordered](a, b T) T {
    if a < b {
        return a
    }
    return b
}
```

```go
// BAD: unnecessary generic — just use the concrete type
func ProcessUser[T User](u T) error { ... }

// BAD: generic with type assertions — defeats the purpose
func Handle[T any](v T) {
    switch v := any(v).(type) { ... }
}
```

**Use `cmp.Ordered` and `slices`/`maps` packages** (Go 1.21+) instead of
writing your own constraints and utilities:

```go
import (
    "cmp"
    "slices"
)

slices.Sort(items)
slices.SortFunc(items, func(a, b Item) int {
    return cmp.Compare(a.Priority, b.Priority)
})
idx, found := slices.BinarySearch(sorted, target)
```

### Structured logging with log/slog

Go 1.21 added `log/slog` to the standard library, replacing the need for
third-party structured logging libraries like zap, zerolog, or logrus for most
use cases.

**Core principles:**

1. Pass `*slog.Logger` as an explicit dependency — never use package globals
2. Use `slog.With` to add common attributes at construction time
3. Use context-aware methods (`InfoContext`, `ErrorContext`) to propagate
   request-scoped data via middleware
4. Use `slog.Group` for nested attributes

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

### errors.Join for combining multiple errors (Go 1.20+)

When collecting errors from parallel or batch operations, use `errors.Join`
instead of concatenating strings or using third-party multi-error libraries:

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

The joined error supports `errors.Is` and `errors.As` — each constituent
error can be matched individually:

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

### Iterators and range-over-func (Go 1.23+)

Go 1.23 introduced iterator functions via the `iter` package. An iterator is
a function that calls a yield function for each element. This enables lazy
evaluation without channels or goroutines.

**Basic patterns:**

```go
import "iter"

// Single-value iterator
func Positive(nums []int) iter.Seq[int] {
    return func(yield func(int) bool) {
        for _, n := range nums {
            if n > 0 {
                if !yield(n) {
                    return
                }
            }
        }
    }
}

// Key-value iterator
func Enumerate[T any](s []T) iter.Seq2[int, T] {
    return func(yield func(int, T) bool) {
        for i, v := range s {
            if !yield(i, v) {
                return
            }
        }
    }
}

// Consuming iterators — they work with range
for v := range Positive(data) {
    fmt.Println(v)
}
for i, v := range Enumerate(items) {
    fmt.Printf("%d: %v\n", i, v)
}
```

**When to use iterators vs slices:**

- Use iterators when the full collection is expensive to compute or unbounded
- Use iterators for composable pipelines (filter → map → take)
- Use plain slices when the data is already materialized and small
- Don't use iterators just because you can — concrete slices are simpler

**Chaining iterators:**

```go
func Filter[T any](seq iter.Seq[T], pred func(T) bool) iter.Seq[T] {
    return func(yield func(T) bool) {
        for v := range seq {
            if pred(v) {
                if !yield(v) {
                    return
                }
            }
        }
    }
}

func Take[T any](seq iter.Seq[T], n int) iter.Seq[T] {
    return func(yield func(T) bool) {
        i := 0
        for v := range seq {
            if i >= n {
                return
            }
            if !yield(v) {
                return
            }
            i++
        }
    }
}
```

### Range-over-int (Go 1.22+)

A small but welcome simplification:

```go
// Go 1.22+
for i := range 10 {
    fmt.Println(i) // 0, 1, 2, ..., 9
}

// Before Go 1.22
for i := 0; i < 10; i++ {
    fmt.Println(i)
}
```

Use this in new code — it's cleaner and less error-prone.

---

This guide represents the synthesis of Go's most authoritative sources—apply
these patterns consistently to write idiomatic, maintainable Go code.
