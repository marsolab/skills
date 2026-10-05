# Configuration follows explicit patterns

## Only main() decides command-line flags

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

## Flags take priority over environment variables

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

## Use struct literal initialization

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
