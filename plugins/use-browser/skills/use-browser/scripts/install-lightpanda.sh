#!/usr/bin/env bash
set -euo pipefail

# Install the Lightpanda headless browser system-wide.
# Lightpanda is the default browser for the use-browser skill; it is
# driven by playwright-cli over CDP (see references/lightpanda.md).
#
# Usage:
#   ./install-lightpanda.sh            # install the latest nightly
#   ./install-lightpanda.sh v0.2.5     # install a specific release
#
# POSIX/bash-3.2 friendly (default macOS bash is 3.2).

VERSION="${1:-}"
INSTALL_DIR="${LIGHTPANDA_INSTALL_DIR:-$HOME/.local/bin}"
NIGHTLY_BASE="https://github.com/lightpanda-io/browser/releases/download/nightly"

# --- already installed? -------------------------------------------------
if command -v lightpanda >/dev/null 2>&1; then
    echo "✅ lightpanda already installed: $(command -v lightpanda)"
    lightpanda version 2>/dev/null || true
    exit 0
fi

echo "🔧 Installing Lightpanda..."

os_type="${OSTYPE:-$(uname -s)}"
arch="$(uname -m)"

verify() {
    if command -v lightpanda >/dev/null 2>&1; then
        echo "✅ lightpanda installed: $(command -v lightpanda)"
        lightpanda version 2>/dev/null || true
        return 0
    fi
    if [ -x "$INSTALL_DIR/lightpanda" ]; then
        echo "✅ lightpanda installed at $INSTALL_DIR/lightpanda"
        echo "   Add it to your PATH:  export PATH=\"$INSTALL_DIR:\$PATH\""
        "$INSTALL_DIR/lightpanda" version 2>/dev/null || true
        return 0
    fi
    return 1
}

# --- preferred path: official one-liner ---------------------------------
have_one_liner_deps() {
    command -v curl >/dev/null 2>&1 || return 1
    command -v jq >/dev/null 2>&1 || return 1
    command -v sha256sum >/dev/null 2>&1 || command -v shasum >/dev/null 2>&1 || return 1
    return 0
}

install_one_liner() {
    echo "📦 Installing via the official installer (pkg.lightpanda.io)..."
    if [ -n "$VERSION" ]; then
        curl -fsSL https://pkg.lightpanda.io/install.sh | bash -s "$VERSION"
    else
        curl -fsSL https://pkg.lightpanda.io/install.sh | bash
    fi
}

# --- fallback: direct binary download -----------------------------------
direct_asset() {
    case "$os_type" in
        darwin*)
            case "$arch" in
                arm64|aarch64) echo "lightpanda-aarch64-macos" ;;
                *) echo "" ;;   # no Intel-mac build
            esac
            ;;
        linux*)
            case "$arch" in
                x86_64|amd64) echo "lightpanda-x86_64-linux" ;;
                aarch64|arm64) echo "lightpanda-aarch64-linux" ;;
                *) echo "" ;;
            esac
            ;;
        *) echo "" ;;
    esac
}

install_direct() {
    asset="$(direct_asset)"
    if [ -z "$asset" ]; then
        echo "❌ No prebuilt Lightpanda binary for $os_type/$arch."
        case "$os_type" in
            darwin*) echo "   Intel macs have no native build — use Docker or build from source:" ;;
            *) echo "   Use Docker or build from source:" ;;
        esac
        echo "   https://lightpanda.io/docs/run-locally/installation/"
        return 1
    fi
    echo "📦 Downloading $asset into $INSTALL_DIR ..."
    mkdir -p "$INSTALL_DIR"
    curl -L -o "$INSTALL_DIR/lightpanda" "$NIGHTLY_BASE/$asset"
    chmod +x "$INSTALL_DIR/lightpanda"
}

# --- run ----------------------------------------------------------------
if have_one_liner_deps; then
    install_one_liner || echo "⚠️  one-liner failed; trying direct download..."
else
    echo "⚠️  Missing curl/jq/sha256sum — skipping one-liner, trying direct download..."
fi

if ! verify; then
    install_direct || true
fi

if verify; then
    echo ""
    echo "🎉 Done. Disable telemetry with: export LIGHTPANDA_DISABLE_TELEMETRY=true"
    echo "   Start the CDP server:  lightpanda serve --host 127.0.0.1 --port 9222"
    exit 0
fi

echo "❌ Failed to install Lightpanda. See https://lightpanda.io/docs/"
exit 1
