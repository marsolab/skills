# Dependency management with Go modules

## Choose module distribution and vendoring deliberately

Prefer normal module requirements for distributable libraries. A dependency's
vendor directory is not inherited by consumers. Application repositories can
choose vendoring for their build process; commit and regenerate it consistently
when that is the established model.

## Use the internal package for private code

Code in `internal/` is only importable by packages rooted at the parent of
`internal/`. This enforces API boundaries:

```text
project/
    cmd/server/main.go     # can import internal/
    internal/
        auth/auth.go       # private to this module
    pkg/
        api/api.go         # public API
```
