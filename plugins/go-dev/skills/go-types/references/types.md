# Go Type Design — Deep Reference

Long-form rationale and edge cases behind the rules in `SKILL.md`.

---

## Define interfaces at the consumption site, not the implementation

Go's structural typing means interfaces should be defined where
they're used, not where implementations live:

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

The consuming package declares only the methods it actually needs,
enabling easy mocking and loose coupling. The implementation package
exposes a concrete type with potentially more methods than any single
consumer needs.

---

## Prefer one-method interfaces

Small interfaces compose better and describe precise behavioral
contracts. The standard library exemplifies this: `io.Reader`,
`io.Writer`, `io.Closer`, `fmt.Stringer`. Thanos explicitly
recommends **1-3 methods maximum**:

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

A kitchen-sink interface forces every implementation to provide every
method, even ones it doesn't naturally support. That's why the
stdlib's `io.Reader`/`io.Writer`/`io.Closer` are separate types —
files are all three; pipes are usually two; some are just one.

---

## Accept interfaces, return concrete types

Functions should accept interface parameters for flexibility but
return concrete types so implementations can add methods without
breaking callers:

```go
// GOOD
func NewServer(logger Logger) *Server {
    return &Server{logger: logger}
}

// The hash library exception: when multiple implementations exist
// for a common interface, returning the interface makes sense
func NewSHA256() hash.Hash { return &sha256{} }
```

The asymmetry: the function author knows what behaviors it needs
(narrow interface input). Once the function returns, callers may
discover useful methods the concrete type provides — so don't hide
them behind an interface they didn't ask for.

---

## The empty interface says nothing

`interface{}` (or `any`) communicates zero information about expected
behavior. Use specific interfaces when possible, and when using empty
interface, document what types are actually expected.

`any` is appropriate for genuinely heterogeneous data —
`encoding/json`'s `Unmarshal` target, generic containers — but if
your function only accepts `*User` or `*Account`, take a real type.

---

## Generics: when and how to use type parameters

Go 1.18 introduced type parameters. The key principle: **generics
reduce duplication without sacrificing readability**. If a generic
version is harder to understand than two concrete versions, skip
generics.

**When to use generics:**

- Data structures that work across element types (caches, trees,
  pools)
- Utility functions on slices, maps, or channels (filter, map,
  reduce)
- When type constraints eliminate runtime type assertions

**When NOT to use generics:**

- The function body would need type assertions anyway
- A concrete type or `any` works fine
- The generic version is harder to read for marginal DRY benefit
- You're abstracting over behavior, not data shape — use interfaces
  instead

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

**Use `cmp.Ordered` and `slices`/`maps` packages** (Go 1.21+) instead
of writing your own constraints and utilities:

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

---

## Receiver type consistency

- **Google Code Review Comments**: Don't mix receiver types on one type.
- **Effective Go**: Choose based on method needs.

Practical guidance: if any method needs a pointer receiver (mutation,
large struct, sync primitives), use pointer receivers for all methods
on that type. Mixing causes subtle bugs:

```go
type Counter struct {
    count int
}

// Mutates — must be pointer receiver.
func (c *Counter) Inc() { c.count++ }

// Reads only — could be value receiver, but...
func (c Counter) Value() int { return c.count }

var c Counter
c.Inc()         // OK: addressable variable, automatic & taken.
c.Value()       // OK: copies the struct.

m := map[string]Counter{"a": {}}
m["a"].Inc()    // ERROR: map elements are not addressable.
```

If `Counter` had `Inc` as a value receiver too, `m["a"].Inc()` would
compile — and silently do nothing because it'd mutate a copy. Both
options bite; consistency picks one and avoids the mixed-mode trap.

---

## Quick reference for interface and generic decisions

| Question | Default |
|----------|---------|
| Should this be an interface? | Probably no. Define one only when a consumer actually needs alternative implementations. |
| How many methods? | 1 ideal, 2–3 acceptable, 4+ split or reconsider. |
| Where do I define it? | Where it's used (consumer side). |
| Should I return an interface? | No — return concrete unless multiple implementations of a well-known interface exist. |
| Should this be generic? | Probably no. Generics are for data-shape abstractions; interfaces handle behavior. |
| Should I write my own `Ordered`? | No — use `cmp.Ordered`. |
| Should I write my own `Sort`/`Min`/`BinarySearch`? | No — use the `slices` package. |
