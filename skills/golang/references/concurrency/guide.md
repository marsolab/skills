# Go Concurrency

Goroutines are cheap; goroutine *lifecycle* is the hard part. Every
goroutine you start owns resources (memory, locks, file descriptors) until
it exits.

For the comprehensive reference, see [concurrency.md](concurrency.md).

## The single most important rule

**Never start a goroutine without knowing when it will stop.**

```go
// BAD: leaks if workChan is abandoned
go func() {
    for {
        process(<-workChan)
    }
}()

// GOOD: terminates on context cancellation
go func() {
    for {
        select {
        case <-ctx.Done():
            return
        case work, ok := <-workChan:
            if !ok {
                return
            }
            process(work)
        }
    }
}()
```

If you can't answer "when does this goroutine exit?", don't write it.

## Context

- `context.Context` is the **first** parameter on every function that may
  block, do I/O, or call something that does.
- Never store a context in a struct.
- Cancel contexts you create: `defer cancel()`.
- Pass `ctx` through; don't replace it with `context.Background()`
  partway down the call stack.

```go
ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
defer cancel()

if err := db.QueryRowContext(ctx, q, id).Scan(&u); err != nil {
    return fmt.Errorf("load user: %w", err)
}
```

## Leave concurrency to the caller

Library functions should be synchronous. Let the caller decide whether
to launch a goroutine.

```go
// BAD: forces async, hides errors, requires draining
func ListFiles(dir string) <-chan string { ... }

// GOOD: synchronous walk; caller can wrap in `go` if they want
func ListFiles(dir string, fn func(string) error) error {
    return filepath.Walk(dir, func(p string, _ os.FileInfo, err error) error {
        if err != nil {
            return err
        }
        return fn(p)
    })
}
```

## WaitGroup for fan-out

```go
var wg sync.WaitGroup
for _, item := range items {
    wg.Add(1)
    go func(item Item) {       // pass item to avoid capture bug
        defer wg.Done()
        process(item)
    }(item)
}
wg.Wait()
```

## errgroup for fan-out with errors

When goroutines can fail, `golang.org/x/sync/errgroup` handles
cancellation and the first-error collection:

```go
g, ctx := errgroup.WithContext(ctx)
for _, item := range items {
    item := item
    g.Go(func() error {
        return process(ctx, item)
    })
}
if err := g.Wait(); err != nil {
    return fmt.Errorf("processing batch: %w", err)
}
```

The shared `ctx` cancels as soon as one goroutine returns an error, so
the others can short-circuit.

## Channels

- Buffer size **0 or 1**, anything larger needs justification — large
  buffers mask synchronization bugs.
- The sender closes the channel; never the receiver.
- Closing a closed channel panics. So does sending on a closed channel.
- Receiving from a closed channel returns the zero value immediately.

```go
ch := make(chan Result)
go func() {
    defer close(ch)              // owner closes
    for _, x := range inputs {
        select {
        case ch <- compute(x):
        case <-ctx.Done():
            return
        }
    }
}()
for r := range ch { ... }
```

## Mutex patterns

- Keep critical sections small. Compute outside the lock, write inside.
- Use `sync.Mutex` by default; consider `sync.RWMutex` for a measured
  read-heavy workload. Read/write ratio alone does not establish a benefit.
- Don't copy a struct that contains a `sync.Mutex` (the linter `copylocks`
  catches this).

```go
type Cache struct {
    mu    sync.RWMutex
    items map[string]Item
}

func (c *Cache) Get(k string) (Item, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    i, ok := c.items[k]
    return i, ok
}
```

## Common bugs

- **Loop variable capture** — with pre-1.22 language semantics, pass the value
  or shadow it. Go 1.22+ gives variables declared by the loop a fresh value
  per iteration; variables assigned with `=` still share storage.
- **Forgetting `defer cancel()`** — leaks the context's resources.
- **Map writes from multiple goroutines** — Go's runtime detects and
  panics. Use a mutex or `sync.Map`.
- **Repeated timers** — `time.After` allocates a timer per call. Go 1.23+
  collects unreachable timers; older behavior retains them until they fire.
  Reuse a timer for measured allocation pressure or explicit reset/stop control,
  following the target version's stop/drain rules.

See the [timer documentation](https://pkg.go.dev/time#NewTimer).

## Bound fan-out and wait for workers

Set a concurrency limit before starting an `errgroup`. Bound the work by the
capacity of its dependencies, such as an HTTP service or database pool:

```go
g, groupCtx := errgroup.WithContext(ctx)
g.SetLimit(maxConcurrent) // validate maxConcurrent > 0 before this
for _, item := range items {
    item := item // compatible with modules using older loop semantics
    g.Go(func() error {
        if err := groupCtx.Err(); err != nil {
            return err
        }
        return process(groupCtx, item)
    })
}
if err := g.Wait(); err != nil {
    return fmt.Errorf("process batch: %w", err)
}
```

`Go` may block at the limit. Workers must respect cancellation so that blocked
submission can progress. Do not change the limit while workers run, and do not
reuse the group's context after `Wait`: the group cancels it when `Wait` returns.

For a streaming worker pool, explicitly own the producer and channel lifecycle:

- A bounded number of workers consume `jobs` using `job, ok := <-jobs`.
- A producer selects between sending and `ctx.Done()`, then closes `jobs`.
- Each worker returns on cancellation or a closed channel.
- A coordinator waits for every worker before closing a shared results channel.
- The result consumer can cancel early without leaving a sender blocked.

Cancellation signals intent; `Wait` or a completion channel proves termination.
Test empty input, a closed queue, an early consumer exit, and a failing worker.

## Version-specific coordination

On Go 1.25+, `sync.WaitGroup.Go` combines starting a goroutine and task
accounting. Its function must not panic. Keep the `Add`/`Done` pattern shown
above for older modules, and call `Add` before launching the goroutine.
Use `errgroup` when errors and cancellation need coordination.

Read [WaitGroup](https://pkg.go.dev/sync#WaitGroup) and
[errgroup](https://pkg.go.dev/golang.org/x/sync/errgroup) for the installed APIs.

## Related guides

| Task | Guide |
|---|---|
| Returning errors out of goroutines, wrapping with context | [Errors](../errors/guide.md) |
| Logging from concurrent code with request-scoped attrs | [Logging](../logging/guide.md) |
| Per-request cancellation in HTTP handlers | [HTTP](../http/guide.md) |
| General Go idioms and naming | [Style](../style/guide.md) |
