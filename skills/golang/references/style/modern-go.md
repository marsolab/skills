# Modern Go patterns (1.18+)

## Generics: when and how to use type parameters

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

## Iterators and range-over-func (Go 1.23+)

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

## Range-over-int (Go 1.22+)

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
