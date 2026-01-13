#!/usr/bin/env bash
# Installation script for Claude Code TaskNotifier
# Interactive configuration for Skill/Hook modes

set -e

# =============================================================================
# Configuration
# =============================================================================

SKILL_NAME="task-notifier"
SKILL_DIR="$HOME/.claude/skills/$SKILL_NAME"
GLOBAL_SETTINGS="$HOME/.claude/settings.json"
PROJECT_SETTINGS=".claude/settings.json"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# =============================================================================
# Gum Check
# =============================================================================

if ! command -v gum &> /dev/null; then
    echo "❌ gum is required. Install: brew install gum"
    exit 1
fi

gum_confirm() {
    gum confirm --affirmative="Yes" --negative="No" --default="$2" -- "$1"
}

# =============================================================================
# Print Functions
# =============================================================================

print_header() {
    clear
    gum style \
        --border double \
        --border-foreground 212 \
        --align center \
        --padding "1 1" \
        "🎨 Claude Code - TaskNotifier Installer"
}

print_info() {
    gum style --foreground 255 "  $1"
}

# =============================================================================
# Configuration Input Functions
# =============================================================================

input_bark_key() {
    gum style --foreground 111 "🔑 Bark Key"
    echo ""
    gum format --type=template \
        -- "{{Foreground \"255\" \"Get your key from the Bark app on iOS\"}}"
    echo ""

    local key
    key=$(gum input --placeholder "Enter your Bark key (press Enter to skip)" --width 60)

    # Confirm key if provided
    if [ -n "$key" ]; then
        echo ""
        gum format --type=template \
            -- "{{Foreground \"226\" \"Key:\"}} {{Foreground \"255\" \"$key\"}}"
        echo ""

        if ! gum_confirm "Use this key?" "Yes"; then
            return 1
        fi
    fi

    BARK_KEY_RESULT="$key"
}

input_bark_server() {
    gum style --foreground 111 "🌐 Bark Server"
    echo ""
    gum format --type=template \
        -- "{{Foreground \"255\" \"Default: https://api.day.app\"}}"
    echo ""

    local server
    server=$(gum input --placeholder "Enter Bark server URL (press Enter for default)" --width 60 --value "https://api.day.app")

    # Confirm if custom
    if [ "$server" != "https://api.day.app" ] && [ -n "$server" ]; then
        echo ""
        gum format --type=template \
            -- "{{Foreground \"226\" \"Server:\"}} {{Foreground \"255\" \"$server\"}}"
        echo ""

        if ! gum_confirm "Use this server?" "Yes"; then
            return 1
        fi
    fi

    BARK_SERVER_RESULT="${server:-https://api.day.app}"
}

input_sound_enabled() {
    gum style --foreground 111 "🔊 Sound Notifications"
    echo ""

    if gum_confirm "Enable sound alerts?" "Yes"; then
        SOUND_ENABLED_RESULT="true"
    else
        SOUND_ENABLED_RESULT="false"
    fi
}

input_system_notify_enabled() {
    gum style --foreground 111 "🖥️  System Notifications"
    echo ""

    if gum_confirm "Enable desktop notifications?" "Yes"; then
        SYSTEM_NOTIFY_ENABLED_RESULT="true"
    else
        SYSTEM_NOTIFY_ENABLED_RESULT="false"
    fi
}

# Use default icons - no user input needed
get_default_icons() {
    # Default icons from config.example.json
    echo '"icons": {
    "success": "https://img.icons8.com/color/96/verified-account.png",
    "error": "https://img.icons8.com/color/96/high-priority.png",
    "info": "https://img.icons8.com/color/96/command-line.png"
  },'
}

# =============================================================================
# Installation Functions
# =============================================================================

install_skill() {
    local target_dir="$1"
    local bark_key="$2"
    local bark_server="$3"
    local sound_enabled="$4"
    local system_notify_enabled="$5"

    mkdir -p "$target_dir/scripts"

    # Copy files
    cp "$REPO_DIR/SKILL.md" "$target_dir/"
    cp "$REPO_DIR/scripts"/*.py "$target_dir/scripts/"
    cp "$REPO_DIR/config.example.json" "$target_dir/"

    # Generate config.json using jq
    jq -n \
        --arg server "$bark_server" \
        --arg key "$bark_key" \
        --argjson sound "$sound_enabled" \
        --argjson notify "$system_notify_enabled" \
        '{
            "bark_server": $server,
            "bark_key": $key,
            "icons": {
                "success": "https://img.icons8.com/color/96/verified-account.png",
                "error": "https://img.icons8.com/color/96/high-priority.png",
                "info": "https://img.icons8.com/color/96/command-line.png"
            },
            "sound_enabled": $sound,
            "system_notify_enabled": $notify
        }' > "$target_dir/config.json"

    # Set permissions
    chmod +x "$target_dir/scripts/notify.py"

    gum style --foreground 82 "✓ Skill installed to: $target_dir"
}

install_hook() {
    local settings_file="$1"
    local bark_key="$2"
    local bark_server="$3"
    local sound_enabled="$4"
    local system_notify_enabled="$5"

    # Generate config.json in repo root (notify.py looks in parent of scripts/)
    jq -n \
        --arg server "$bark_server" \
        --arg key "$bark_key" \
        --argjson sound "$sound_enabled" \
        --argjson notify "$system_notify_enabled" \
        '{
            "bark_server": $server,
            "bark_key": $key,
            "icons": {
                "success": "https://img.icons8.com/color/96/verified-account.png",
                "error": "https://img.icons8.com/color/96/high-priority.png",
                "info": "https://img.icons8.com/color/96/command-line.png"
            },
            "sound_enabled": $sound,
            "system_notify_enabled": $notify
        }' > "$REPO_DIR/config.json"

    # Ensure settings directory exists
    mkdir -p "$(dirname "$settings_file")"

    # Create settings file if not exists
    if [ ! -f "$settings_file" ]; then
        echo "{}" > "$settings_file"
    fi

    # Get absolute path to notify.py
    local abs_notify_path
    abs_notify_path=$(cd "$REPO_DIR/scripts" && pwd)/notify.py

    local hook_command="python3 \"$abs_notify_path\" \"Task completed\""

    # Add hook using jq - correct format for Stop (no matcher needed)
    if command -v jq &> /dev/null; then
        jq --arg cmd "$hook_command" '
            if .hooks.Stop then
                .hooks.Stop += [{"hooks": [{"type": "command", "command": $cmd}]}]
            else
                .hooks.Stop = [{"hooks": [{"type": "command", "command": $cmd}]}]
            end
        ' "$settings_file" > "$settings_file.tmp" && mv "$settings_file.tmp" "$settings_file"

        gum style --foreground 82 "✓ Hook installed to: $settings_file"
    else
        gum style --foreground 196 "✗ jq required: brew install jq"
        return 1
    fi
}

# =============================================================================
# Main Installation Flow
# =============================================================================

print_header
echo ""

# ============================================================================
# Step 1: Installation Scope
# ============================================================================
gum style --foreground 212 "Step 1: Installation Scope"
echo ""
gum format --type=template \
    -- "{{Foreground \"255\" \"Global\"}}  - All projects (~/.claude/)" \
    -- "{{Foreground \"255\" \"Project\"}} - Current project only (./.claude/)"
echo ""

INSTALL_SCOPE=$(gum choose --header="Choose scope:" "Global" "Project")

if [ "$INSTALL_SCOPE" = "Global" ]; then
    SKILL_TARGET="$SKILL_DIR"
    SETTINGS_TARGET="$GLOBAL_SETTINGS"
else
    SKILL_TARGET="$(pwd)/.claude/skills/$SKILL_NAME"
    SETTINGS_TARGET="$PROJECT_SETTINGS"
fi

# ============================================================================
# Step 2: Installation Type
# ============================================================================
echo ""
gum style --foreground 212 "Step 2: Installation Type"
echo ""
gum format --type=template \
    -- "{{Foreground \"255\" \"Skill\"}} - Manual invocation (call notify.py directly)" \
    -- "{{Foreground \"255\" \"Hook\"}}  - Auto-run after each task completion"
echo ""

INSTALL_TYPE=$(gum choose --header="Choose type:" "Skill" "Hook")

# ============================================================================
# Step 3: Configure Options
# ============================================================================
echo ""
gum style --foreground 212 "Step 3: Configuration"
echo ""

# Get all configuration values (stored in global variables)
input_bark_key
input_bark_server
input_sound_enabled
input_system_notify_enabled

# ============================================================================
# Step 4: Perform Installation
# ============================================================================
echo ""
gum style --foreground 212 "Step 4: Installing..."
echo ""

if [ "$INSTALL_TYPE" = "Skill" ]; then
    install_skill "$SKILL_TARGET" "$BARK_KEY_RESULT" "$BARK_SERVER_RESULT" "$SOUND_ENABLED_RESULT" "$SYSTEM_NOTIFY_ENABLED_RESULT"
    CONFIG_PATH="$SKILL_TARGET/config.json"
else
    install_hook "$SETTINGS_TARGET" "$BARK_KEY_RESULT" "$BARK_SERVER_RESULT" "$SOUND_ENABLED_RESULT" "$SYSTEM_NOTIFY_ENABLED_RESULT"
    CONFIG_PATH="$REPO_DIR/config.json"
fi

# ============================================================================
# Installation Complete
# ============================================================================
echo ""
gum style --foreground 82 "✅ Installation Complete!"
echo ""

gum format --type=template \
    -- "{{Foreground \"82\" \"✓\"}} Type:   {{Foreground \"255\" \"$INSTALL_TYPE\"}}" \
    -- "{{Foreground \"82\" \"✓\"}} Scope:  {{Foreground \"255\" \"$INSTALL_SCOPE\"}}" \
    -- "{{Foreground \"82\" \"✓\"}} Config: {{Foreground \"255\" \"$CONFIG_PATH\"}}"
echo ""

gum style --foreground 111 "💡 Uninstall anytime: ./uninstall.sh"
echo ""
