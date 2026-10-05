# Go Style

Write Go code that is readable, maintainable, and predictable. Favour
clarity over cleverness; the language is small on purpose.

For the comprehensive idiomatic reference, see [idioms.md](idioms.md). For
the catalogue of language gotchas, see [pitfalls.md](pitfalls.md).

## Decision shortcuts

### Naming

- Packages: lowercase, singular, no underscores, no `util` / `common` /
  `helpers`. Name describes purpose.
- Variable length tracks scope: `i` in a tight loop, `customerOrderHistory`
  across a long function.
- Getters omit `Get`; setters use `Set`. `obj.Owner()`, `obj.SetOwner(u)`.
- Acronyms keep consistent case: `URL`, `ID`, `HTTP` — never `Url`, `Id`,
  `Http`.
- Constants are `mixedCaps`, not `SCREAMING_CASE`.
- Interfaces with one method end in `-er`: `Reader`, `Closer`, `Stringer`.

### Use generics when

- Building a data structure that works across types (cache, tree, pool).
- Writing slice/map/channel utilities (filter, map, reduce).
- Type constraints remove runtime assertions.

Skip generics when the body would need type assertions anyway, when a
concrete type works, or when the result is harder to read. Prefer
`slices`, `maps`, and `cmp` (Go 1.21+) over hand-rolled utilities.

### Interfaces

- Define interfaces at the **consumption site**, not next to the
  implementation. The consumer declares only the methods it needs.
- Aim for 1 method, accept 2–3 if cohesive, split at 4+. Larger interfaces
  are tolerable inside a SaaS product; keep them tiny in libraries.
- **Accept interfaces, return concrete types.**
- `any` says nothing. Use a real interface or document the expected type.

### Code organization

- Start as a few files in `package main`. Add structure only when growth
  demands it.
- `cmd/` for binaries, `internal/` for code only this module may import,
  `pkg/` (or top-level packages) for the public API.
- One package, one purpose. Orient packages around a domain
  (`package user`), not an implementation accident (`package models`).
- Imports group as: stdlib → external → internal, blank-line separated.

### Documentation

- Every exported symbol gets a comment that starts with the symbol's name
  and forms a complete sentence ending with a period.
- Document **why**, not what the code already says.
- Package docs go above the `package` clause in any one file (often
  `doc.go`).

## Modern Go quick reference

```go
// Range over int (Go 1.22+)
for i := range 10 { ... }

// Generic data structure (Go 1.18+)
type Cache[K comparable, V any] struct { ... }

// Iterator (Go 1.23+)
func Positive(nums []int) iter.Seq[int] {
    return func(yield func(int) bool) {
        for _, n := range nums {
            if n > 0 && !yield(n) {
                return
            }
        }
    }
}

// Prefer stdlib utilities
slices.Sort(items)
slices.SortFunc(items, func(a, b Item) int {
    return cmp.Compare(a.Priority, b.Priority)
})
```

## Configuration patterns

- Only `main()` defines flags. Libraries take their config through a
  constructor, never `flag.String` at package scope.
- Precedence: flags → environment → config file → default.
- Initialize structs with literals in one shot — never leave a struct
  partially populated across multiple statements.

```go
server := &http.Server{
    Addr:         addr,
    ReadTimeout:  30 * time.Second,
    WriteTimeout: 30 * time.Second,
    Handler:      mux,
}
```

## Common pitfalls

Read [pitfalls.md](pitfalls.md) for the full set.

- **Loop variable capture in closures** — pass or shadow variables for
  pre-1.22 language semantics. Loops that assign existing variables still share
  them; Go 1.22+ fixes variables declared by the loop.
- **Nil interface vs nil value** — an interface holding a typed nil is
  not nil. Return explicit `nil` when the underlying value is nil.
- **Variable shadowing with `:=`** inside `if` blocks silently drops the
  inner result. Use `=` to reassign.
- **Defer in loops** — defers fire at function exit, not loop iteration.
  Wrap the body in a closure when you need per-iteration cleanup.
- **Nil map writes panic.** Always `make(map[K]V)` before writing.
- **Range copies values.** Mutate via index: `for i := range items { items[i].x++ }`.
- **Slice reslicing shares the backing array.** Use the three-index form
  `s[:n:n]` to force a fresh allocation when needed.

## Related guides

| Task | Guide |
|---|---|
| Wrapping or matching errors, `errors.Join` | [Errors](../errors/guide.md) |
| Goroutines, channels, context, errgroup | [Concurrency](../concurrency/guide.md) |
| `log/slog`, structured logging, observability | [Logging](../logging/guide.md) |
| Table-driven tests, `t.Helper`, integration gating | [Testing](../testing/guide.md) |
| HTTP services, Chi router, graceful shutdown | [HTTP](../http/guide.md) |
| CLI tools, subcommands, `flag.NewFlagSet` | [CLI](../cli/guide.md) |
| sqlc, goose migrations, transactions | [SQL](../sql/guide.md) |
| `golangci-lint`, `.golangci.yml`, formatting | [Lint](../lint/guide.md) |

## Performance — measure first

Don't optimize without benchmarks. Once you have data:

- Preallocate when size is known: `make([]T, 0, n)`, `make(map[K]V, n)`.
- Use `strings.Builder` for iterative concatenation.
- On hot paths, `strconv.Itoa` beats `fmt.Sprint`.
- Convert string→[]byte once outside the loop.

```go
func BenchmarkProcess(b *testing.B) {
    data := generateTestData()
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```

## Dependencies

- Prefer modules for library distribution. Vendoring is a repository/build
  choice; consumers do not inherit a library's vendor directory.
- `internal/` is enforced by the compiler — only packages rooted at the
  parent directory may import it. Use it to keep an API surface small.
