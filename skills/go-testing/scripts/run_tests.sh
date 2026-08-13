#!/usr/bin/env bash
set -euo pipefail

if ! command -v go >/dev/null 2>&1; then
    echo "go not found in PATH" >&2
    exit 2
fi

if [ ! -f go.mod ] && ! find . -name '*.go' -print -quit | grep -q .; then
    echo "no Go module or Go files found" >&2
    exit 2
fi

go test -race -cover ./...
