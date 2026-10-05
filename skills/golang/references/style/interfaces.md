# Interface design emphasizes small, consumer-defined contracts

## Define interfaces at the consumption site, not the implementation

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

## Prefer one-method interfaces

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

## Accept interfaces, return concrete types

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

## The empty interface says nothing

`interface{}` (or `any`) communicates zero information about expected behavior.
Use specific interfaces when possible, and when using empty interface, document
what types are actually expected.
