#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'USAGE'
Usage: setup_golangci_lint.sh [project-root] [--force] [--hook] [--force-hook]

Copy the bundled golangci-lint v2 configuration into a Go project.
  --force       Replace an existing .golangci.yml or .golangci.yaml.
  --hook        Install a pre-commit hook in the repository's Git hook path.
  --force-hook  Replace an existing pre-commit hook (requires --hook).

Tools are not installed and Makefiles are not changed by this helper.
USAGE
}

project_arg=.
project_set=false
force=false
install_hook=false
force_hook=false
for arg in "$@"; do
    case "$arg" in
        --force) force=true ;;
        --hook) install_hook=true ;;
        --force-hook) force_hook=true ;;
        -h|--help) usage; exit 0 ;;
        --*) echo "Unknown option: $arg" >&2; usage >&2; exit 2 ;;
        *)
            if "$project_set"; then
                echo "Only one project root may be specified" >&2
                exit 2
            fi
            project_arg=$arg
            project_set=true
            ;;
    esac
done

if "$force_hook" && ! "$install_hook"; then
    echo "--force-hook requires --hook" >&2
    exit 2
fi
if [[ ! -d "$project_arg" ]]; then
    echo "Project directory not found: $project_arg" >&2
    exit 2
fi
project_root=$(cd "$project_arg" && pwd)
if [[ ! -f "$project_root/go.mod" ]]; then
    echo "Run setup in the target Go module (go.mod is required)" >&2
    exit 2
fi
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
config_source="$script_dir/../../assets/lint/golangci.yml"
config_target="$project_root/.golangci.yml"
alternate_config="$project_root/.golangci.yaml"
if ! "$force" && { [[ -e "$config_target" || -L "$config_target" ]] || [[ -e "$alternate_config" || -L "$alternate_config" ]]; }; then
    echo "Existing lint configuration preserved; use --force to replace it" >&2
    exit 2
fi

hook_path=
if "$install_hook"; then
    if ! git -C "$project_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        echo "Hook installation requires a Git worktree" >&2
        exit 2
    fi
    hook_dir=$(cd "$project_root" && git rev-parse --git-path hooks)
    if [[ "$hook_dir" != /* ]]; then
        hook_dir="$project_root/$hook_dir"
    fi
    hook_path="$hook_dir/pre-commit"
    if ! "$force_hook" && [[ -e "$hook_path" || -L "$hook_path" ]]; then
        echo "Existing hook preserved; use --force-hook with --hook to replace it" >&2
        exit 2
    fi
fi

cp "$config_source" "$config_target"
if "$force" && [[ -e "$alternate_config" || -L "$alternate_config" ]]; then
    rm "$alternate_config"
fi
printf 'Copied configuration to %s\n' "$config_target"
if "$install_hook"; then
    mkdir -p "$(dirname "$hook_path")"
    cat > "$hook_path" <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail
exec golangci-lint run --config=.golangci.yml ./...
HOOK
    chmod +x "$hook_path"
    printf 'Installed pre-commit hook at %s\n' "$hook_path"
fi
printf 'Use a compatible golangci-lint v2 installation and align settings with go.mod.\n'
