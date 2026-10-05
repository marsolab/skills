# Go CLI

Build small CLI tools with the stdlib `flag` package first. Reach for cobra or urfave-cli
only when the help output or subcommand tree exceeds what `flag` can
present cleanly.

## Project layout

For a single binary:

```text
mycli/
├── main.go
├── go.mod
└── .golangci.yml
```

For multi-binary repos or tools that grow subcommand modules:

```text
mycli/
├── cmd/mycli/main.go
├── internal/command/
│   ├── add.go
│   ├── list.go
│   └── remove.go
├── go.mod
└── .golangci.yml
```

## Single-command CLI

```go
func main() {
    addr := flag.String("addr", ":8080", "listen address")
    verbose := flag.Bool("v", false, "verbose output")
    flag.Parse()

    if err := run(*addr, *verbose, flag.Args()); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}

func run(addr string, verbose bool, args []string) error {
    // ...
}
```

The `run` indirection makes the body testable — `main` becomes a thin
wrapper that turns errors into exit codes.

## Subcommands with flag.NewFlagSet

Each subcommand owns its own `FlagSet`. Dispatch on `os.Args[1]`:

```go
func main() {
    if len(os.Args) < 2 {
        usage()
        os.Exit(2)
    }

    cmd, args := os.Args[1], os.Args[2:]

    var err error
    switch cmd {
    case "add":
        err = runAdd(args)
    case "list":
        err = runList(args)
    case "remove":
        err = runRemove(args)
    case "-h", "--help", "help":
        usage()
        return
    default:
        fmt.Fprintf(os.Stderr, "unknown command: %s\n", cmd)
        usage()
        os.Exit(2)
    }

    if err != nil {
        if errors.Is(err, flag.ErrHelp) {
            return
        }
        fmt.Fprintln(os.Stderr, err)
        if errors.Is(err, ErrUsage) {
            os.Exit(2)
        }
        os.Exit(1)
    }
}

var ErrUsage = errors.New("invalid arguments")

func runAdd(args []string) error {
    fs := flag.NewFlagSet("add", flag.ContinueOnError)
    project := fs.String("project", "", "project to add to")
    if err := fs.Parse(args); err != nil {
        if errors.Is(err, flag.ErrHelp) {
            return err
        }
        return fmt.Errorf("%w: %v", ErrUsage, err)
    }

    return command.Add(*project, fs.Args())
}
```

`ContinueOnError` keeps parsing testable and leaves exit-code ownership with
`main`; `ExitOnError` can terminate a test process. Test help, unknown flags,
missing arguments, and successful parsing separately. A configured `FlagSet`
can direct usage to an injected writer for deterministic tests.

## Exit codes

Adopt the BSD/sysexits convention or a project-specific subset, but
**document them** in `--help`. Common pattern:

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Generic failure |
| `2` | Usage error (bad flags, missing args) |
| `3+` | Tool-specific failure modes |

Use `os.Exit` only from `main` (or a top-level helper). Library code
returns errors.

## Stdout vs stderr

- **Stdout**: the data the tool produces. Pipe-friendly. Don't write
  status messages to stdout.
- **Stderr**: usage, errors, progress, diagnostic logs.

```go
fmt.Println("user-1234")                              // result → stdout
fmt.Fprintln(os.Stderr, "warning: deprecated flag")   // status → stderr
```

This lets `mycli list | jq .` work without filtering noise.

## Reading stdin

```go
if flag.NArg() == 0 {
    // no positional args — read from stdin
    if err := process(os.Stdin); err != nil {
        return err
    }
    return nil
}
for _, path := range flag.Args() {
    if err := processPath(path); err != nil {
        return err
    }
}

// ... elsewhere, at package scope. A per-path helper gives each file its
// own defer (no accumulation across the loop) and reports the Close error
// instead of dropping it.
func processPath(path string) (rErr error) {
    f, err := os.Open(path)
    if err != nil {
        return fmt.Errorf("open %s: %w", path, err)
    }
    defer func() {
        if err := f.Close(); err != nil {
            rErr = errors.Join(rErr, fmt.Errorf("close %s: %w", path, err))
        }
    }()
    if err := process(f); err != nil {
        return fmt.Errorf("process %s: %w", path, err)
    }
    return nil
}
```

Conventional Unix tools accept paths as positional args and fall back
to stdin when none are given.

## Signal handling

```go
ctx, cancel := signal.NotifyContext(context.Background(),
    os.Interrupt, syscall.SIGTERM)
defer cancel()

if err := run(ctx); err != nil {
    fmt.Fprintln(os.Stderr, err)
    os.Exit(1)
}
```

`signal.NotifyContext` (Go 1.16+) gives you a context that cancels on
the listed signals — ideal for "stop this long-running operation when
the user hits Ctrl-C."

## Configuration sources

Same precedence as services: flag → env → default. Don't pull in a
config-file framework for a CLI; if you need one, document the schema
and keep it minimal.

```go
addr := flag.String("addr", "", "server address")
flag.Parse()

if *addr == "" {
    *addr = os.Getenv("MYCLI_ADDR")
}
if *addr == "" {
    *addr = "localhost:8080"
}
```

## When third-party CLI libraries make sense

Reach for cobra or urfave-cli when:

- You have many subcommands (5+) with their own flags and help text.
- You need shell-completion generation.
- You need man-page generation.
- You're building a tool family with consistent UX (e.g. `kubectl`-style).

For everything smaller, the stdlib `flag` keeps dependencies tiny and
the binary slim.

## Related guides

| Task | Guide |
|---|---|
| Reading SQL data inside the CLI | [SQL](../sql/guide.md) |
| Structured slog output (or `--json` flag) | [Logging](../logging/guide.md) |
| Error wrapping and exit-code mapping | [Errors](../errors/guide.md) |
| Table-driven tests for subcommand parsing | [Testing](../testing/guide.md) |
| General Go idioms and naming | [Style](../style/guide.md) |
