# Performance optimization requires measurement first

## Prove slowness with benchmarks before optimizing

Dave Cheney warns: **"So many crimes against maintainability are committed in
the name of performance."** Optimization couples code tightly, tears down
abstractions, and exposes internals. Only pay that cost when benchmarks prove
necessity.

```go
func BenchmarkProcess(b *testing.B) {
    data := generateTestData()
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```

## Preallocate slices and maps with known sizes

When size is known or estimable, preallocate:

```go
// GOOD: preallocate
results := make([]Result, 0, len(inputs))
for _, input := range inputs {
    results = append(results, process(input))
}

// Map with size hint
cache := make(map[string]Value, expectedSize)
```

But don't over-allocate—wasted memory harms performance too.

## Use strings.Builder for iterative string construction

```go
// GOOD: efficient for multiple appends
var b strings.Builder
for _, part := range parts {
    b.WriteString(part)
}
result := b.String()

// GOOD: simple concatenation
key := "prefix:" + id

// GOOD: formatting
msg := fmt.Sprintf("%s [%s:%d]", name, host, port)
```

## Hot-path optimizations (CockroachDB guidance)

On critical paths, `strconv` outperforms `fmt`:

```go
// Candidate for a measured hot path.
s := strconv.Itoa(n)

// Convenient formatting; benchmark before replacing it.
s := fmt.Sprint(n)
```

Convert strings to bytes once when writing repeatedly:

```go
// GOOD: convert once
data := []byte("fixed string")
for i := 0; i < n; i++ {
    w.Write(data)
}
```
