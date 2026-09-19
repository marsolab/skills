---
name: go-concurrency
description: >-
  Concurrency, context, and lazy iteration in Go. Triggers when the user
  is writing or reviewing concurrent Go code: goroutines, channels,
  `sync.Mutex`/`sync.RWMutex`/`sync.WaitGroup`, `context.Context`
  propagation, worker pools, fan-out/fan-in, background workers, graceful
  goroutine shutdown, race conditions. Also covers `iter.Seq`/`iter.Seq2`
  iterators (Go 1.23+) and range-over-int (Go 1.22+). Load when the user
  mentions goroutine leaks, deadlocks, race detector, channel buffering,
  or "how do I cancel this?"
version: 1.0.0
tags:
  - go
  - golang
  - concurrency
  - goroutines
  - context
  - iterators
---

# Go Concurrency

Goroutines own resources. Always know when one will stop. Pass
`context.Context` through everything that might block or take long.

For long-form rationale and edge cases, read
`references/concurrency.md`.

## The single most important rule

**Never start a goroutine without knowing how it will stop.** If you
can't answer "what makes this `go func()` exit?", don't start it.

```go
// BAD: goroutine may never terminate
go func() {
    for {
        process(<-workChan) // blocked forever if workChan abandoned
    }
}()

// GOOD: explicit termination via context
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
```

## Context as the first parameter, always

```go
func ProcessRequest(ctx context.Context, req *Request) (*Response, error) {
    // ...
}
```

Never store `context.Context` in a struct. Pass it through each call.
The cancellation of a context implies the function should stop work
and return.

```go
ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
defer cancel()

if err := db.QueryContext(ctx, ...); err != nil {
    return fmt.Errorf("query: %w", err)
}
```

## Don't force concurrency on callers

Let the caller decide whether to run your code concurrently:

```go
// BAD: forces a goroutine on the caller, hides errors, leaks if
// caller stops draining
func ListFiles(dir string) <-chan string {
    ch := make(chan string)
    go func() {
        filepath.Walk(dir, func(p string, _ os.FileInfo, _ error) error {
            ch <- p
            return nil
        })
        close(ch)
    }()
    return ch
}

// GOOD: synchronous, caller decides
func ListFiles(dir string, fn func(string) error) error {
    return filepath.Walk(dir, func(p string, _ os.FileInfo, err error) error {
        if err != nil {
            return err
        }
        return fn(p)
    })
}
```

## sync.WaitGroup for coordination

Pass items by value into the goroutine to avoid loop variable capture
bugs (Go ≤ 1.21). Go 1.22+ scopes loop variables per iteration so this
is no longer strictly required, but explicit pass-by-value is still
clearer:

```go
var wg sync.WaitGroup
for _, item := range items {
    wg.Add(1)
    go func(item Item) {
        defer wg.Done()
        process(item)
    }(item)
}
wg.Wait()
```

If goroutines can return errors, use `golang.org/x/sync/errgroup`:

```go
g, ctx := errgroup.WithContext(ctx)
for _, item := range items {
    item := item
    g.Go(func() error {
        return process(ctx, item)
    })
}
if err := g.Wait(); err != nil {
    return fmt.Errorf("process batch: %w", err)
}
```

## Channel buffer sizes: 0 or 1

CockroachDB's rule: any buffer size other than 0 or 1 requires
scrutiny. Larger buffers usually mask synchronization bugs. When you
need buffering, document why that specific size was chosen.

- **Unbuffered (0)** — synchronous handoff. Sender blocks until
  receiver is ready. Default choice.
- **Buffer 1** — decouple a single producer/consumer pair without
  blocking the producer.

If you find yourself reaching for `make(chan T, 100)`, you probably
want a worker pool, not a buffered channel.

## Worker pool pattern

```go
func worker(ctx context.Context, jobs <-chan Job, results chan<- Result) {
    for {
        select {
        case <-ctx.Done():
            return
        case job, ok := <-jobs:
            if !ok {
                return
            }
            results <- process(job)
        }
    }
}

// Caller:
ctx, cancel := context.WithCancel(ctx)
defer cancel()

jobs := make(chan Job)
results := make(chan Result)

var wg sync.WaitGroup
for range n {
    wg.Add(1)
    go func() {
        defer wg.Done()
        worker(ctx, jobs, results)
    }()
}

go func() {
    wg.Wait()
    close(results)
}()
```

Note `for range n` — Go 1.22+ range-over-int syntax replacing
`for i := 0; i < n; i++`.

## sync.Mutex vs sync.RWMutex

- **`sync.Mutex`** — exclusive lock. Default choice; cheaper than
  RWMutex when contention is low.
- **`sync.RWMutex`** — many readers, occasional writers. Only worth
  the overhead when reads vastly outnumber writes (e.g., 100:1+).

Always defer the unlock:

```go
mu.Lock()
defer mu.Unlock()
// critical section
```

## Iterators (Go 1.23+)

Iterators are functions that call a `yield` function for each element.
They enable lazy evaluation without channels or goroutines.

```go
import "iter"

// Single-value iterator
func Positive(nums []int) iter.Seq[int] {
    return func(yield func(int) bool) {
        for _, n := range nums {
            if n > 0 && !yield(n) {
                return
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

// Consume with range
for v := range Positive(data) {
    fmt.Println(v)
}
```

When to use iterators:

- The full collection is expensive to compute or unbounded.
- You're building a composable pipeline (filter → map → take).

When NOT to use them:

- Data is already materialized and small — a slice is simpler.

## Range-over-int (Go 1.22+)

```go
// Go 1.22+
for i := range 10 {
    fmt.Println(i) // 0, 1, ..., 9
}
```

Use this in new code. Cleaner and harder to off-by-one.

## Pitfalls

### Loop variable capture (pre-Go 1.22)

```go
// BAD pre-1.22
for _, item := range items {
    go func() {
        process(item) // captures by reference, sees final value
    }()
}

// GOOD: pass as parameter
for _, item := range items {
    go func(item Item) {
        process(item)
    }(item)
}
```

Go 1.22+ scopes loop variables per iteration, fixing this for `for
range`. Older versions still need the parameter pass or `item := item`
shadow.

### Defer in loops

`defer` runs at function return, **not** loop iteration:

```go
// BAD: all files held open until function returns
for _, f := range files {
    file, _ := os.Open(f)
    defer file.Close()
    process(file)
}

// GOOD: scope each iteration in a closure
for _, f := range files {
    func() {
        file, _ := os.Open(f)
        defer file.Close()
        process(file)
    }()
}
```

### Map operations

Maps are not safe for concurrent use. Either guard with `sync.Mutex`
or use `sync.Map` (rarely the right answer — usually a mutex is
fine).

```go
// PANIC: nil map write
var m map[string]int
m["k"] = 1 // panic

// CORRECT
m := make(map[string]int)
m["k"] = 1
```

### Range returns copies

```go
// BAD: modifies the copy, not the slice
for _, item := range items {
    item.count++
}

// GOOD: index-based
for i := range items {
    items[i].count++
}
```

## Quick reference

- Context first parameter, always.
- Know how every goroutine stops before you start it.
- Channel buffer 0 or 1; anything else needs justification.
- `sync.WaitGroup` for coordination, `errgroup` when errors matter.
- `sync.Mutex` first; `sync.RWMutex` only when reads dominate.
- `for range n` and iterators in new code.
- Pitfalls: loop capture (pre-1.22), defer in loops, nil maps, range
  copies.
