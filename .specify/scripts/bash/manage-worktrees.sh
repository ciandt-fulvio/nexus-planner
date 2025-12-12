#!/usr/bin/env bash
# Manage worktrees for Spec-Kit workflow

set -e

SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

COMMAND="${1:-list}"

case "$COMMAND" in
    list)
        # List all active worktrees
        echo "Active Git Worktrees:"
        git worktree list
        echo ""
        echo "Registered in Spec-Kit:"
        registry=$(get_worktree_registry_path)
        if [ -f "$registry" ]; then
            cat "$registry" | jq -r '.worktrees | to_entries[] | "\(.key): \(.value.path) (\(.value.status))"'
        else
            echo "No worktrees registered"
        fi
        ;;

    cleanup)
        # Remove merged/stale worktrees
        echo "Pruning stale worktree metadata..."
        git worktree prune
        echo "Done"
        ;;

    remove)
        # Remove specific worktree
        BRANCH_NAME="$2"
        if [ -z "$BRANCH_NAME" ]; then
            echo "Usage: $0 remove <branch-name>" >&2
            exit 1
        fi

        registry=$(get_worktree_registry_path)
        if [ -f "$registry" ] && command -v jq >/dev/null 2>&1; then
            WORKTREE_PATH=$(jq -r ".worktrees[\"$BRANCH_NAME\"].path // empty" "$registry")
            if [ -n "$WORKTREE_PATH" ]; then
                echo "Removing worktree: $WORKTREE_PATH"
                git worktree remove "$WORKTREE_PATH"

                # Update registry
                temp_file=$(mktemp)
                jq "del(.worktrees[\"$BRANCH_NAME\"])" "$registry" > "$temp_file"
                mv "$temp_file" "$registry"
                echo "Done"
            else
                echo "Worktree not found in registry: $BRANCH_NAME" >&2
                exit 1
            fi
        else
            echo "Registry not found or jq not installed" >&2
            exit 1
        fi
        ;;

    *)
        echo "Usage: $0 {list|cleanup|remove <branch>}"
        echo ""
        echo "Commands:"
        echo "  list              List all active worktrees (Git and Spec-Kit registry)"
        echo "  cleanup           Prune stale worktree metadata"
        echo "  remove <branch>   Remove a specific worktree by branch name"
        exit 1
        ;;
esac
