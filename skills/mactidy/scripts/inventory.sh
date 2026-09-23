#!/bin/bash

# Read-only inventory of common reproducible development artifacts and
# suspicious long-lived development processes on macOS.

set -u

usage() {
    echo "Usage: $0 ROOT [ROOT ...]" >&2
    echo "Example: $0 \"$HOME/Code\" \"$HOME/.codex/worktrees\"" >&2
}

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "mactidy inventory supports macOS only" >&2
    exit 2
fi

if [[ "$#" -eq 0 ]]; then
    usage
    exit 2
fi

now_epoch=$(date +%s)

echo "Mactidy inventory (read-only)"
echo
echo "Physical filesystem baseline"
df -h /System/Volumes/Data 2>/dev/null || df -h /

echo
printf "CATEGORY\tAPPROX_KIB\tAGE_DAYS\tPATH\n"

for root in "$@"; do
    if [[ ! -d "$root" ]]; then
        echo "warning: skipping missing root: $root" >&2
        continue
    fi

    resolved_root=$(cd "$root" 2>/dev/null && pwd -P)
    if [[ -z "$resolved_root" ]]; then
        echo "warning: cannot resolve root: $root" >&2
        continue
    fi

    case "$resolved_root" in
        /|/System|/System/Volumes|/System/Volumes/Data)
            echo "warning: refusing broad system root: $resolved_root" >&2
            continue
            ;;
    esac

    find "$resolved_root" \
        \( -type d \( -name .git -o -name .Trash \) -prune \) -o \
        \( -type d \( \
            -name node_modules -o \
            -name .venv -o \
            -name target -o \
            -name .next -o \
            -name .nuxt -o \
            -name .svelte-kit -o \
            -name .turbo -o \
            -name coverage -o \
            -name .pytest_cache -o \
            -name __pycache__ -o \
            -name DerivedData \
        \) -prune -print0 \) 2>/dev/null |
        while IFS= read -r -d '' candidate; do
            name=$(basename "$candidate")
            case "$name" in
                node_modules|.venv)
                    category="dependency"
                    ;;
                .pytest_cache|__pycache__)
                    category="cache"
                    ;;
                *)
                    category="build-output"
                    ;;
            esac

            size_kib=$(du -sk "$candidate" 2>/dev/null | awk '{print $1}')
            [[ -n "$size_kib" ]] || size_kib="unknown"

            modified_epoch=$(stat -f '%m' "$candidate" 2>/dev/null || true)
            if [[ "$modified_epoch" =~ ^[0-9]+$ ]]; then
                age_days=$(( (now_epoch - modified_epoch) / 86400 ))
            else
                age_days="unknown"
            fi

            printf "%s\t%s\t%s\t%s\n" \
                "$category" "$size_kib" "$age_days" "$candidate"
        done
done

echo
echo "Detached-process review candidates (not proven orphans)"
printf "PID\tPPID\tTTY\tELAPSED\tRSS_KIB\tEXECUTABLE\tCOMMAND\n"
ps -axo pid=,ppid=,tty=,etime=,rss=,ucomm=,command= 2>/dev/null |
    awk '
        BEGIN {
            tool_names = "^(node|nodejs|bun|deno|vite|webpack|"
            tool_names = tool_names "playwright|claude|cursor-agent|codex)$"
        }
        $2 == 1 && $3 == "??" {
            executable = tolower($6)
            if (executable ~ tool_names) {
                print
            }
        }
    '

echo
echo "No files were deleted and no processes were signalled."
echo "Directory sizes are logical estimates; verify physical recovery with df."
