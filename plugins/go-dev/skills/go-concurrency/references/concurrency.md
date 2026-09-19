# Go Concurrency — Deep Reference

Long-form rationale and edge cases behind the rules in `SKILL.md`.

---

## Never start a goroutine without knowing when it will stop

This is the single most important concurrency guideline, repeated
across all sources. Goroutines own resources — locks, memory,
connections — that only get freed when the goroutine exits:

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

A leaked goroutine isn't merely idle — it pins memory referenced by
its closure, holds open file descriptors, and accumulates over time
into out-of-memory errors that are extremely painful to debug.

---

## Leave concurrency to the caller

Don't force async execution on consumers. Let them choose whether to
run your code in a goroutine:

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

The bad pattern can't distinguish errors from empty directories and
forces callers to drain the channel even when they've found their
answer.

---

## Use sync.WaitGroup for goroutine coordination

```go
var wg sync.WaitGroup
for _, item := range items {
    wg.Add(1)
    go func(item Item) {
        defer wg.Done()
        process(item)
    }(item)  // pass by value to avoid closure capture bug (pre-1.22)
}
wg.Wait()
```

For goroutines that can return errors, prefer `errgroup`:

```go
import "golang.org/x/sync/errgroup"

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

`errgroup.WithContext` cancels the shared context as soon as any
goroutine returns an error — the others see `ctx.Done()` and can stop
early.

---

## Context must be the first parameter

```go
func ProcessRequest(ctx context.Context, req *Request) (*Response, error) {
    // ...
}
```

Never store context in structs — pass it explicitly through each call.
The cancellation of a context argument implies interruption of the
function receiving it.

The few exceptions in the stdlib (e.g., `http.Request.Context()`)
predate the convention; new code follows the rule.

---

## Channel buffer sizes should be zero or one

CockroachDB's rule: **any buffer size other than 0 or 1 requires
scrutiny**. Larger buffers often mask synchronization bugs. When you
need buffering, document why that specific size was chosen.

The mental model:

- Buffer 0 — synchronous handoff. The act of receiving is the
  signal that processing happened.
- Buffer 1 — fire-and-forget for one message; producer doesn't wait
  for the consumer.
- Buffer N — you're either implementing a queue (use a real queue
  with proper backpressure) or hiding a race (which will surface as a
  hang or memory bloat in production).

---

## Iterators and range-over-func (Go 1.23+)

Go 1.23 introduced iterator functions via the `iter` package. An
iterator is a function that calls a yield function for each element.
This enables lazy evaluation without channels or goroutines.

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

- Use iterators when the full collection is expensive to compute or
  unbounded.
- Use iterators for composable pipelines (filter → map → take).
- Use plain slices when the data is already materialized and small.
- Don't use iterators just because you can — concrete slices are
  simpler.

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

The `bool` returned by `yield` reports whether the consumer wants
more values — propagate it correctly so consumers can break out
early.

---

## Range-over-int (Go 1.22+)

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

## Loop variable capture in closures

The most common pre-1.22 Go bug: closures capture loop variables by
reference, seeing the final value.

```go
// BAD pre-1.22: all goroutines see same value
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

Go 1.22+ fixes this for `for range` loops. C-style `for` loops still
have the issue.

---

## Variable shadowing silently breaks logic

The `:=` operator creates new variables, potentially shadowing outer
scope:

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

---

## Defer timing and argument evaluation

Defer arguments evaluate immediately; the deferred function executes
at function end:

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

---

## Map operations require initialization and aren't thread-safe

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
```

Concurrent map access requires `sync.Mutex` or `sync.Map`. Most code
should use a regular map plus a mutex; `sync.Map` is optimized for a
narrow set of access patterns and is often the wrong default.

---

## Range returns copies, not references

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

---

## Slice reslicing shares the backing array

```go
// DANGER: modifying one affects the other
original := []byte("AAAA/BBBBB")
first := original[:4]
first = append(first, "XXX"...)  // overwrites original[4:]!

// SAFE: full slice expression limits capacity
first := original[:4:4]  // [low:high:max]
first = append(first, "XXX"...)  // allocates new array
```
