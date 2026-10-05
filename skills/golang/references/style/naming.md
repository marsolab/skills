# Naming conventions establish code clarity

**Poor naming is symptomatic of poor design.** Good names are concise,
descriptive, and predictable—readers should know how to use something without
consulting documentation.

## Package names should be lowercase, singular, and unique

Packages must be lowercase single words without underscores or mixedCaps. The
package name becomes a prefix for all exported identifiers, so avoid redundancy:

```go
// BAD: redundant package prefix
package chubby
type ChubbyFile struct{}  // caller writes chubby.ChubbyFile

// GOOD: package name provides context
package chubby
type File struct{}  // caller writes chubby.File
```

Avoid meaningless names like `util`, `common`, `misc`, `api`, `types`, or
`helpers`. If two packages seem to need the same name, either they overlap in
responsibility or the name is too generic. Production codebases enforce unique
package names across the entire project to prevent `goimports`
confusion—CockroachDB uses parent-prefixed names like `server/serverpb`,
`kv/kvserver`, and `util/contextutil`.

## Variable length should correlate with scope distance

The distance between declaration and final use determines appropriate name
length. Short names work when context is clear and scope is small:

```go
// Short scope: short name
for i, v := range items {
    process(v)
}

// Longer scope: longer name
customerOrderHistory := fetchOrdersForCustomer(customerID)
// ... many lines later ...
processOrderHistory(customerOrderHistory)
```

**Use `var` for zero-value declarations, `:=` for initializations.** The `var`
keyword signals deliberate use of the zero value:

```go
var players int              // deliberately zero
things := make([]Thing, 0)   // initialized to specific state
```

## Exported names follow strict conventions

Getters omit `Get` prefix; setters use `Set` prefix:

```go
// GOOD
owner := obj.Owner()
obj.SetOwner(user)

// BAD
owner := obj.GetOwner()
```

Acronyms maintain consistent casing—`URL` appears as `URL` or `url`, never
`Url`. Write `ServeHTTP` not `ServeHttp`, `xmlHTTPRequest` not `XmlHttpRequest`,
and `appID` not `appId`.

## Interfaces name the behavior with an -er suffix

One-method interfaces derive names from the method plus `-er`: `Reader`,
`Writer`, `Formatter`, `CloseNotifier`. When implementing well-known interfaces,
match the established signature exactly—name your string converter `String()`
not `ToString()`.

## Constants avoid SCREAMING_CASE

Go uses mixedCaps for constants, matching other identifiers:

```go
// GOOD
const maxConnections = 100
const DefaultTimeout = 30 * time.Second

// BAD (not idiomatic Go)
const MAX_CONNECTIONS = 100
```

Use `iota` for enumerated constants, typically skipping zero if it could mask
missing initialization:

```go
type Status int
const (
    _             Status = iota  // skip zero
    StatusPending                // 1
    StatusActive                 // 2
    StatusClosed                 // 3
)
```
