---
name: go-types
description: >-
  Interface and generic type design in Go. Triggers when the user is
  defining or reviewing Go interfaces, generics (type parameters), type
  constraints, struct receiver types, or asks "should this be an
  interface or a concrete type?", "should I use generics here?",
  "accept interfaces vs return interfaces", `cmp.Ordered`, `slices.Sort`,
  or how to design type APIs in Go. Also covers when NOT to use
  interfaces or generics (most of the time).
version: 1.0.0
tags:
  - go
  - golang
  - interfaces
  - generics
  - types
---

# Go Type Design

Interfaces and generics exist to reduce duplication. Use them when
they earn their keep; resist them when a concrete type is clearer.

For long-form rationale, read `references/types.md`.

## Interface design

### Define interfaces at the consumption site

Go's structural typing means the consumer declares only the methods it
needs:

```go
// GOOD: consumer-defined
package cache

type Reader interface {
    Read(ctx context.Context, key string) ([]byte, error)
}

func New(r Reader) *Cache { return &Cache{backend: r} }

// BAD: implementation forces a kitchen-sink interface on consumers
package storage

type Storage interface {
    Read(...) (...)
    Write(...) (...)
    Delete(...) (...)
    List(...) (...)
    // ... ten more methods
}
```

Implementations satisfy interfaces implicitly — there is no `implements`
keyword. So the consumer is free to declare a tiny interface and
existing types satisfy it without modification.

### Keep interfaces small (1–3 methods)

The standard library is the model: `io.Reader`, `io.Writer`,
`io.Closer`, `fmt.Stringer`. Each is a behavioral contract you can
compose.

| Methods | Verdict |
|---------|---------|
| 1       | Perfect. |
| 2–3     | Acceptable when methods are cohesive (read+close). |
| 4+      | Probably wants splitting. SaaS/service interfaces sometimes legitimately need this; libraries almost never do. |

### Accept interfaces, return concrete types

```go
// Accept interface — flexibility for caller.
func NewServer(logger Logger) *Server { ... }

// Return concrete — implementation can grow methods without breaking
// callers.
func New() *Server { ... }
```

Returning interfaces locks future implementations into the original
contract and forces every caller to switch on type for capabilities
beyond it.

The standard library exception: when there are several implementations
of one well-known interface (`hash.Hash`, `image.Image`), returning
the interface is the convention.

### One-method interfaces use the `-er` suffix

```go
type Reader interface { Read(...) (...) }
type Writer interface { Write(...) (...) }
type Stringer interface { String() string }
```

When implementing well-known stdlib interfaces, match the established
signature exactly. Name your converter `String() string`, not
`ToString()`.

### The empty interface communicates nothing

`interface{}` (or `any`) means "I gave up on typing." Use a specific
interface when possible. When you must use `any`, document what
concrete types are actually expected.

## Generics

Generics (Go 1.18+) reduce duplication for type-shape-only operations.
Don't reach for them to abstract over behavior — that's what
interfaces are for.

### When to use generics

- **Data structures** that work across element types: caches, trees,
  pools, sets.
- **Utility functions** on slices, maps, or channels: filter, map,
  reduce.
- **Type constraints** that eliminate runtime type assertions.

```go
// GOOD: generic data structure
type Cache[K comparable, V any] struct {
    mu    sync.RWMutex
    items map[K]cacheItem[V]
}

func NewCache[K comparable, V any]() *Cache[K, V] { ... }

// GOOD: generic utility
func Map[T, U any](s []T, f func(T) U) []U {
    result := make([]U, len(s))
    for i, v := range s {
        result[i] = f(v)
    }
    return result
}
```

### When NOT to use generics

- The body needs type assertions anyway — generics didn't buy you
  anything.
- A concrete type or `any` works.
- You're abstracting over behavior, not shape — use an interface.
- The generic version is harder to read than two concrete copies.

```go
// BAD: unnecessary generic
func ProcessUser[T User](u T) error { ... }

// BAD: generic with type assertions defeats the purpose
func Handle[T any](v T) {
    switch v := any(v).(type) { ... }
}
```

### Use cmp.Ordered and stdlib utility packages

Go 1.21+ added `cmp`, `slices`, `maps` packages. Prefer them over
hand-written constraints and utilities:

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

minVal := slices.Min(nums)
total := slices.Index(items, target)
```

Don't define your own `Ordered` constraint — `cmp.Ordered` is the
canonical one.

### Custom constraints with `~`

Use `~` to allow named types based on a primitive:

```go
type Number interface {
    ~int | ~int64 | ~float64
}

type Celsius float64

// Sum works on []Celsius because Celsius's underlying type is float64.
func Sum[T Number](nums []T) T {
    var total T
    for _, n := range nums {
        total += n
    }
    return total
}
```

Without `~`, only the exact primitive types match.

## Struct receivers

Choose between value and pointer receivers per type, not per method.
If any method on a type needs a pointer receiver (mutation, large
struct, sync primitives), use pointer receivers for **all** methods on
that type.

```go
// Mixed receivers — confusing, error-prone
func (s Server) Addr() string  { return s.addr }
func (s *Server) SetAddr(a string) { s.addr = a }
```

Pick one and apply consistently. This is one of the few places where
the Effective Go and Google guides actually agree.

## Quick reference

- Define interfaces where they're used; keep them to 1–3 methods.
- Accept interfaces, return concrete types.
- Empty interface (`any`) is a signal you owe the reader docs.
- Generics for data shapes and utilities, not behavior.
- Prefer `cmp`, `slices`, `maps` from stdlib over custom utilities.
- Use `~` in constraints to accept named types.
- Be consistent with receiver types per struct.
