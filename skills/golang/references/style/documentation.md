# Documentation follows godoc conventions

## Comment every exported symbol with the symbol's name

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

## Comments must be complete sentences

Start with uppercase, end with a period. This is enforced by linters in Thanos
and other production codebases.

## Document the why, not the obvious what

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

## Package documentation goes in doc.go or any file

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
