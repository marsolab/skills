#!/bin/bash
set -euo pipefail

# PostToolUse hook: runs Go tests with race detection and coverage after edits.
# Exits non-zero so Claude sees failures and fixes them.

if ! command -v go &>/dev/null; then
    echo "go not found in PATH, skipping tests"
    exit 0
fi

# Only run if there are .go files in the project.
if ! find . -maxdepth 1 -name '*.go' -o -name 'go.mod' | grep -q .; then
    exit 0
fi

echo "Running go test -race -cover ./..."
go test -race -cover ./...
