#!/bin/bash
set -euo pipefail

# PostToolUse hook: runs golangci-lint after edits.
# Exits non-zero so Claude sees lint failures and fixes them.

if ! command -v golangci-lint &>/dev/null; then
    echo "golangci-lint not found in PATH, skipping lint"
    exit 0
fi

# Only run if there are .go files in the project.
if ! find . -maxdepth 1 -name '*.go' -o -name 'go.mod' | grep -q .; then
    exit 0
fi

echo "Running golangci-lint run ./..."
golangci-lint run ./...
