# Linting reference

Carved from the comprehensive Go style guide. Covers required tools
across production codebases and the common linter set.

---

## Required tools across production codebases

- **gofmt** / **goimports**: Non-negotiable formatting
- **go vet**: Catches common mistakes
- **golangci-lint**: Meta-linter running multiple checks

For a CI runner with a pinned golangci-lint v2 installation:

```yaml
- name: Validate configuration
  run: golangci-lint config verify
- name: Lint
  run: golangci-lint run ./...
```

## Commonly enabled linters

See [the working guide](guide.md) for the bundled configuration, helper paths,
suppression rules, and optional Git-hook behavior. v1 configuration and output
flags are not interchangeable with v2; use the installed version's docs.

- **errcheck**: Ensures errors aren't ignored
- **govet**: Official Go analyzer
- **staticcheck**: Comprehensive static analysis
- **unused**: Finds unused code
- **misspell**: Catches typos in comments and strings
- **prealloc**: Suggests slice preallocation
- **gosec**: Security-focused analysis
