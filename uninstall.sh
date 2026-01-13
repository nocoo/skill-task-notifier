#!/usr/bin/env bash
# Uninstallation script for Claude Code TaskNotifier
# Detects and removes both Skill and Hook installations

set -e  # Exit on error

# =============================================================================
# Configuration
# =============================================================================

SKILL_NAME="task-notifier"
SKILL_DIR="$HOME/.claude/skills/$SKILL_NAME"
PROJECT_SKILL_DIR="$(pwd)/.claude/skills/$SKILL_NAME"
GLOBAL_SETTINGS="$HOME/.claude/settings.json"
PROJECT_SETTINGS=".claude/settings.json"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Installation detection flags
HAS_GLOBAL_SKILL=false
HAS_PROJECT_SKILL=false
HAS_GLOBAL_HOOK=false
HAS_PROJECT_HOOK=false

# Gum styles
GUM_HEADER="🗑️  Claude Code - TaskNotifier Uninstaller"
GUM_BORDER="double"
GUM_PADDING="1 1"

# =============================================================================
# Gum Wrapper Functions
# =============================================================================

# Check if gum is available
if ! command -v gum &> /dev/null; then
    echo "❌ gum is required but not installed."
    echo ""
    echo "Install gum:"
    echo "  brew install gum"
    echo ""
    echo "Or download from: https://github.com/charmbracelet/gum"
    exit 1
fi

gum_confirm() {
    gum confirm \
        --affirmative="Yes" \
        --negative="No" \
        --default="$2" \
        -- "$1"
}

# =============================================================================
# Print Functions
# =============================================================================

print_header() {
    clear
    gum style \
        --border "$GUM_BORDER" \
        --border-foreground 196 \
        --align center \
        --margin "1 0" \
        --padding "$GUM_PADDING" \
        "$GUM_HEADER" ""
}

print_step() {
    echo ""
    gum style --foreground 111 "📍 $1"
    echo ""
}

print_success() {
    echo ""
    gum style --foreground 82 "✅ $1"
}

print_error() {
    echo ""
    gum style --foreground 196 "❌ $1"
}

print_warn() {
    echo ""
    gum style --foreground 226 "⚠️  $1"
}

print_info() {
    gum style --foreground 255 "    $1"
}

# =============================================================================
# Detection Functions
# =============================================================================

detect_installations() {
    # Check global skill
    if [ -d "$SKILL_DIR" ]; then
        HAS_GLOBAL_SKILL=true
        gum format --type=template \
            -- "{{Foreground \"82\" \"✓\"}} {{Foreground \"255\" \"Global Skill\"}}: $SKILL_DIR"
    fi

    # Check project skill
    if [ -d "$PROJECT_SKILL_DIR" ]; then
        HAS_PROJECT_SKILL=true
        gum format --type=template \
            -- "{{Foreground \"82\" \"✓\"}} {{Foreground \"255\" \"Project Skill\"}}: $PROJECT_SKILL_DIR"
    fi

    # Check global hook
    if [ -f "$GLOBAL_SETTINGS" ]; then
        if command -v jq &> /dev/null; then
            if jq -e '.hooks.Stop[].hooks[].command' "$GLOBAL_SETTINGS" 2>/dev/null | grep -q "notify.py"; then
                HAS_GLOBAL_HOOK=true
                gum format --type=template \
                    -- "{{Foreground \"82\" \"✓\"}} {{Foreground \"255\" \"Global Hook\"}}: $GLOBAL_SETTINGS"
            fi
        else
            # Fallback: grep check
            if grep -q "notify.py" "$GLOBAL_SETTINGS" 2>/dev/null; then
                HAS_GLOBAL_HOOK=true
                gum format --type=template \
                    -- "{{Foreground \"82\" \"✓\"}} {{Foreground \"255\" \"Global Hook\"}}: $GLOBAL_SETTINGS"
            fi
        fi
    fi

    # Check project hook
    if [ -f "$PROJECT_SETTINGS" ]; then
        if command -v jq &> /dev/null; then
            if jq -e '.hooks.Stop[].hooks[].command' "$PROJECT_SETTINGS" 2>/dev/null | grep -q "notify.py"; then
                HAS_PROJECT_HOOK=true
                gum format --type=template \
                    -- "{{Foreground \"82\" \"✓\"}} {{Foreground \"255\" \"Project Hook\"}}: $PROJECT_SETTINGS"
            fi
        else
            # Fallback: grep check
            if grep -q "notify.py" "$PROJECT_SETTINGS" 2>/dev/null; then
                HAS_PROJECT_HOOK=true
                gum format --type=template \
                    -- "{{Foreground \"82\" \"✓\"}} {{Foreground \"255\" \"Project Hook\"}}: $PROJECT_SETTINGS"
            fi
        fi
    fi

    # If nothing found
    if [ "$HAS_GLOBAL_SKILL" = false ] && [ "$HAS_PROJECT_SKILL" = false ] && \
       [ "$HAS_GLOBAL_HOOK" = false ] && [ "$HAS_PROJECT_HOOK" = false ]; then
        print_info "No installations found - nothing to uninstall."
        exit 0
    fi
}

# =============================================================================
# Uninstallation Functions
# =============================================================================

uninstall_global_skill() {
    # Warn about config backup
    if [ -f "$SKILL_DIR/config.json" ]; then
        gum format --type=template \
            -- "{{Foreground \"226\" \"💡\"}} Backup tip: {{Foreground \"255\" \"cp $SKILL_DIR/config.json ~/config.json.backup\"}}"
        echo ""

        if ! gum_confirm "Remove Global Skill?" "No"; then
            return 0
        fi
    fi

    rm -rf "$SKILL_DIR"
    gum style --foreground 82 "✓ Global Skill removed"
}

uninstall_project_skill() {
    # Warn about config backup
    if [ -f "$PROJECT_SKILL_DIR/config.json" ]; then
        gum format --type=template \
            -- "{{Foreground \"226\" \"💡\"}} Backup tip: {{Foreground \"255\" \"cp $PROJECT_SKILL_DIR/config.json ~/config.json.backup\"}}"
        echo ""

        if ! gum_confirm "Remove Project Skill?" "No"; then
            return 0
        fi
    fi

    rm -rf "$PROJECT_SKILL_DIR"
    gum style --foreground 82 "✓ Project Skill removed"
}

uninstall_global_hook() {
    if command -v jq &> /dev/null; then
        # Remove hooks that contain notify.py (new format: .hooks.Stop[].hooks[])
        jq 'del(.hooks.Stop[]? | select(.hooks[].command | contains("notify.py")))' "$GLOBAL_SETTINGS" > "$GLOBAL_SETTINGS.tmp" && mv "$GLOBAL_SETTINGS.tmp" "$GLOBAL_SETTINGS"

        # Clean up empty hooks.Stop array
        jq 'if .hooks.Stop == [] then del(.hooks.Stop) else . end' "$GLOBAL_SETTINGS" > "$GLOBAL_SETTINGS.tmp" && mv "$GLOBAL_SETTINGS.tmp" "$GLOBAL_SETTINGS"

        # Clean up empty hooks object
        jq 'if .hooks == {} then del(.hooks) else . end' "$GLOBAL_SETTINGS" > "$GLOBAL_SETTINGS.tmp" && mv "$GLOBAL_SETTINGS.tmp" "$GLOBAL_SETTINGS"
    else
        gum style --foreground 196 "✗ jq required: brew install jq"
        return 1
    fi

    gum style --foreground 82 "✓ Global Hook removed"
}

uninstall_project_hook() {
    if command -v jq &> /dev/null; then
        # Remove hooks that contain notify.py (new format: .hooks.Stop[].hooks[])
        jq 'del(.hooks.Stop[]? | select(.hooks[].command | contains("notify.py")))' "$PROJECT_SETTINGS" > "$PROJECT_SETTINGS.tmp" && mv "$PROJECT_SETTINGS.tmp" "$PROJECT_SETTINGS"

        # Clean up empty hooks.Stop array
        jq 'if .hooks.Stop == [] then del(.hooks.Stop) else . end' "$PROJECT_SETTINGS" > "$PROJECT_SETTINGS.tmp" && mv "$PROJECT_SETTINGS.tmp" "$PROJECT_SETTINGS"

        # Clean up empty hooks object
        jq 'if .hooks == {} then del(.hooks) else . end' "$PROJECT_SETTINGS" > "$PROJECT_SETTINGS.tmp" && mv "$PROJECT_SETTINGS.tmp" "$PROJECT_SETTINGS"
    else
        gum style --foreground 196 "✗ jq required: brew install jq"
        return 1
    fi

    gum style --foreground 82 "✓ Project Hook removed"
}

# =============================================================================
# Main Uninstallation Flow
# =============================================================================

print_header

# Detect all installations
detect_installations

# Count what to uninstall
UNINSTALL_COUNT=0
[ "$HAS_GLOBAL_SKILL" = true ] && ((UNINSTALL_COUNT++)) || true
[ "$HAS_PROJECT_SKILL" = true ] && ((UNINSTALL_COUNT++)) || true
[ "$HAS_GLOBAL_HOOK" = true ] && ((UNINSTALL_COUNT++)) || true
[ "$HAS_PROJECT_HOOK" = true ] && ((UNINSTALL_COUNT++)) || true

# Confirm uninstall
echo ""
gum style --foreground 196 "Remove $UNINSTALL_COUNT installation(s)?"
echo ""

if ! gum_confirm "Proceed with uninstall?" "No"; then
    gum style --foreground 111 "Cancelled"
    exit 0
fi

# Execute uninstall
REMOVED_COUNT=0

if [ "$HAS_GLOBAL_SKILL" = true ]; then
    if uninstall_global_skill; then
        ((REMOVED_COUNT++)) || true
    fi
fi

if [ "$HAS_PROJECT_SKILL" = true ]; then
    if uninstall_project_skill; then
        ((REMOVED_COUNT++)) || true
    fi
fi

if [ "$HAS_GLOBAL_HOOK" = true ]; then
    if uninstall_global_hook; then
        ((REMOVED_COUNT++)) || true
    fi
fi

if [ "$HAS_PROJECT_HOOK" = true ]; then
    if uninstall_project_hook; then
        ((REMOVED_COUNT++)) || true
    fi
fi

# =============================================================================
# Uninstallation Complete
# =============================================================================
echo ""
gum style --foreground 82 "✅ Removed $REMOVED_COUNT/$UNINSTALL_COUNT installation(s)"
echo ""
gum style --foreground 111 "💡 Reinstall anytime with: ./install.sh"
echo ""
