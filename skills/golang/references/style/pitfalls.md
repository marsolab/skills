# Common pitfalls every Go developer encounters

Carved from the comprehensive Go style guide. The traps below catch
people repeatedly; assume any unfamiliar Go reviewer will catch them too.

---

## Loop variable capture in closures

Under pre-1.22 language semantics, closures share the loop variable and can see
its final value. Go 1.22+ fixes variables declared by the loop, but a loop that
assigns an existing variable with `=` still shares it. Check the module's Go
version before prescribing an explicit copy:

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

## Nil interface vs nil value in interface

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

## Variable shadowing silently breaks logic

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

The standard `go vet` command does not expose a `-shadow` flag. Configure the
`shadow` analyzer in golangci-lint's `govet` settings, or install the standalone
`golang.org/x/tools/go/analysis/passes/shadow/cmd/shadow` analyzer when needed.

## Defer timing and argument evaluation

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
    file, err := os.Open(f)
    if err != nil {
        continue
    }
    defer file.Close()  // ALL close at function end, not loop iteration
}

// CORRECT: give each iteration its own function so the defer runs
// per-iteration. That function is also where the Close error gets
// handled — named return + errors.Join; see the [Errors](../errors/guide.md) guide.
for _, f := range files {
    if err := readOne(f); err != nil {
        return err
    }
}
```

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

// Concurrent access requires sync.Mutex or sync.Map
```

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

## Slice reslicing shares backing array

```go
// DANGER: modifying one affects the other
original := []byte("AAAA/BBBBB")
first := original[:4]
first = append(first, "XXX"...)  // overwrites original[4:]!

// SAFE: full slice expression limits capacity
first := original[:4:4]  // [low:high:max]
first = append(first, "XXX"...)  // allocates new array
```

## HTTP response bodies must be closed

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

```

These snippets leave `Close` unchecked to isolate the ordering-and-nil
lesson; under the bundled `errcheck` config a bare `resp.Body.Close()` is
still flagged. Close the body via the named-return + deferred
`errors.Join` form — see the [Errors](../errors/guide.md) guide.

On `Client.Do` errors, a non-nil response occurs for redirect failures and its
body is already closed. Check the error before scheduling cleanup of a successful
response. For reliable reuse across supported versions, read a successful body
to EOF and close it; bound reads of untrusted bodies. Do not assume an internal
transport drain limit is a stable public guarantee. See
[Client.Do](https://pkg.go.dev/net/http#Client.Do).
