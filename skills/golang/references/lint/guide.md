# Go Lint

Run `gofmt`, `goimports`, and `golangci-lint` on every commit. The
formatters fix style automatically; the linter catches the bugs the
compiler doesn't.

For the comprehensive reference, see [linting.md](linting.md). The
bundled [v2 config](../../assets/lint/golangci.yml) and
[setup helper](../../scripts/lint/setup_golangci_lint.sh) are opt-in tooling.

## Setup script

Copy the bundled config into a Go module. Run the helper by its installed path:

```bash
/path/to/golang/scripts/lint/setup_golangci_lint.sh /path/to/project
```

The script preserves existing configuration by default. Use `--force` to
replace it, `--hook` to install a pre-commit hook, and `--force-hook` with
`--hook` to replace an existing hook. Git worktrees and `core.hooksPath` are
resolved through Git. It does not install packages or edit Makefiles.

The asset uses golangci-lint **v2**. Install a compatible, pinned tool version
as part of the target repository's tooling setup. Check the binary and schema:

```bash
golangci-lint version
golangci-lint config verify --config .golangci.yml
```

## Day-to-day commands

Run the portable helper from the target Go project's root when available:

```bash
/path/to/golang/scripts/lint/run_lint.sh
```

Or run the underlying commands directly:

```bash
# Run every enabled linter
golangci-lint run ./...

# Auto-fix what's fixable
golangci-lint run --fix ./...

# Lint a subset
golangci-lint run ./internal/...

# Show which linters are active
golangci-lint linters

# Format Go code (always before commit)
gofmt -w .
goimports -w .          # sorts and removes unused imports
```

## Required tools

- **gofmt** / **goimports**: non-negotiable. `goimports` is a strict
  superset of `gofmt`.
- **go vet**: built into the toolchain; catches misuse of stdlib types.
- **golangci-lint**: the meta-linter; runs many analyzers in parallel
  with shared parsing.

## Linters worth enabling

The bundled `.golangci.yml` turns these on:

| Linter | What it catches |
|---|---|
| `errcheck` | Unchecked errors |
| `govet` | Stdlib misuse, shadowing, struct tag typos |
| `staticcheck` | The biggest set of static-analysis rules |
| `unused` | Dead code |
| `misspell` | Typos in comments and strings |
| `prealloc` | Slices that should be preallocated |
| `gosec` | Common security issues |
| `revive` | Successor to golint; readable rules |
| `gocritic` | Many opinionated readability checks |
| `bodyclose` | Unclosed `http.Response.Body` |
| `nilnil` | Ambiguous simultaneous nil value and nil error |
| `errorlint` | `%w` and wrapping mistakes |

## Suppressing findings

Prefer fixing over suppressing. When you must suppress, do so narrowly
and explain why:

```go
//nolint:gosec // not user input — read from a generated config file
buf, err := os.ReadFile(path)
```

`//nolint` without a linter name disables every linter on that line —
avoid it. Always name the linter and add a comment.

`//nolint:errcheck` is almost never legitimate. A flagged unchecked error
— usually a deferred `Close`, `Flush`, or `Write` — is an error to
handle, not noise to silence. The bundled config enables `check-blank`,
so `_ = f.Close()` is reported, and it never applies golangci-lint's
`std-error-handling` exclusion preset, so a bare `f.Close()` is flagged
too. Handle them with a named return and a deferred `errors.Join` (see
the [Errors](../errors/guide.md) guide) instead of suppressing.

## Pre-commit integration

With `--hook`, the setup script writes a Git hook that checks the module's
working tree with `golangci-lint run ./...`. It does not lint an isolated
snapshot of staged files. Preserve repository-owned hooks unless replacement
is requested; adjust a failing rule or the affected code before committing.

## CI integration

```yaml
# After installing the repository's pinned golangci-lint v2 binary:
- name: Verify lint configuration
  run: golangci-lint config verify
- name: Lint Go
  run: golangci-lint run --timeout=5m ./...
```

Pin the version and make sure its build supports the target Go version.
Floating `latest` can introduce new findings. The bundled asset includes test
files and infers the language version from `go.mod`; review strict analyzers
such as `wrapcheck`, `mnd`, and `wsl_v5` against the repository's conventions.

See the [official installation guide](https://golangci-lint.run/docs/welcome/install/)
and [configuration reference](https://golangci-lint.run/docs/configuration/file/).

## Related guides

| Task | Guide |
|---|---|
| Why a rule fires (the underlying idiom) | [Style](../style/guide.md) |
| Catching shadowed `ctx` from `:=` | [Style](../style/guide.md) (pitfalls) |
| Tests that should run alongside lint | [Testing](../testing/guide.md) |
| HTTP handlers that frequently trigger `bodyclose` | [HTTP](../http/guide.md) |
