#!/usr/bin/env bash
# Installation script for Claude Code TaskNotifier Skill
# Uses gum for interactive prompts and copies files instead of symlinks

set -e  # Exit on error

# =============================================================================
# Configuration
# =============================================================================

SKILL_NAME="task-notifier"
SKILL_DIR="$HOME/.claude/skills/$SKILL_NAME"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Gum styles
GUM_HEADER="🎨 Claude Code Skill - TaskNotifier"
GUM_CONFIRM_STYLE="foreground:212 bold"  # Pink/purple for confirm
GUM_INFO_STYLE="foreground:111"          # Blue for info
GUM_SUCCESS_STYLE="foreground:82"        # Green for success
GUM_WARN_STYLE="foreground:226"          # Yellow for warning
GUM_ERROR_STYLE="foreground:196"         # Red for error
GUM_INPUT_STYLE="foreground:255"         # White for input
GUM_BORDER="double"                      # Border style
GUM_PADDING="1 1"                        # Padding
GUM_WIDTH="80"                           # Width

# Colors for fallback output (if gum not available)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

gum_input() {
    gum input -- "$@"
}

gum_format() {
    local style="$1"
    shift
    gum format --"$style" "$@"
}

gum_style() {
    local style="$1"
    shift
    gum style --"$style" "$@"
}

# =============================================================================
# Functions
# =============================================================================

print_header() {
    clear
    gum style \
        --border "$GUM_BORDER" \
        --border-foreground 212 \
        --align center \
        --margin "1 0" \
        --padding "$GUM_PADDING" \
        "$GUM_HEADER" ""
}

print_step() {
    gum style --foreground 111 "📍 $1"
    echo ""
}

print_success() {
    gum style --foreground 82 "✅ $1"
    echo ""
}

print_warn() {
    gum style --foreground 226 "⚠️  $1"
    echo ""
}

print_error() {
    gum style --foreground 196 "❌ $1"
    echo ""
}

print_info() {
    gum format -- foreground=255 -- "    $1"
}

# =============================================================================
# Installation
# =============================================================================

print_header

# Show installation info
gum format \
    --type=template \
    -- "Repository: {{Foreground \"255\" \"$REPO_DIR\"}}" \
    -- "Target:      {{Foreground \"255\" \"$SKILL_DIR\"}}"
echo ""

# Step 1: Check existing installation
if [ -d "$SKILL_DIR" ]; then
    print_step "Existing Installation Found"

    gum format --type=template \
        -- "An existing installation was detected at:" \
        -- "{{Foreground \"226\" \"$SKILL_DIR\"}}"
    echo ""

    if gum_confirm "Remove and reinstall the skill?" "No"; then
        print_error "Installation cancelled"
        exit 0
    fi

    print_step "Removing existing installation..."
    rm -rf "$SKILL_DIR"
    print_success "Removed existing installation"
fi

# Step 2: Verify repository structure
print_step "Verifying repository structure..."

if [ ! -f "$REPO_DIR/SKILL.md" ]; then
    print_error "SKILL.md not found in repository root"
    exit 1
fi

if [ ! -d "$REPO_DIR/scripts" ]; then
    print_error "scripts/ directory not found"
    exit 1
fi

if [ ! -f "$REPO_DIR/config.example.json" ]; then
    print_error "config.example.json not found"
    exit 1
fi

print_success "Repository structure verified"

# Step 3: Copy files to skill directory
print_step "Copying files to skill directory..."

mkdir -p "$SKILL_DIR"

# Copy SKILL.md
cp "$REPO_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"
print_info "SKILL.md"

# Copy scripts directory (exclude config.json if exists)
mkdir -p "$SKILL_DIR/scripts"
cp "$REPO_DIR/scripts"/*.py "$SKILL_DIR/scripts/" 2>/dev/null || true
print_info "scripts/"

# Remove any old config.json in scripts/
rm -f "$SKILL_DIR/scripts/config.json"

# Copy config.example.json
cp "$REPO_DIR/config.example.json" "$SKILL_DIR/config.example.json"
print_info "config.example.json"

# Copy requirements.txt if exists
if [ -f "$REPO_DIR/requirements.txt" ]; then
    cp "$REPO_DIR/requirements.txt" "$SKILL_DIR/requirements.txt"
    print_info "requirements.txt"
fi

# Copy README if exists
if [ -f "$REPO_DIR/README.md" ]; then
    cp "$REPO_DIR/README.md" "$SKILL_DIR/README.md"
    print_info "README.md"
fi

echo ""
print_success "All files copied"

# Step 4: Set executable permissions
print_step "Setting executable permissions..."

chmod +x "$SKILL_DIR/scripts/notify.py"
chmod +x "$SKILL_DIR/scripts/run.py" 2>/dev/null || true
print_success "Permissions set"

# Step 5: Configure Bark Key
print_step "Bark Key Configuration"

# Check if config.json already exists
if [ -f "$SKILL_DIR/config.json" ]; then
    gum format --type=template \
        -- "Existing {{Foreground \"226\" \"config.json\"}} found."

    # Extract current bark_key
    CURRENT_KEY=$(grep -o '"bark_key"[[:space:]]*:[[:space:]]*"[^"]*"' "$SKILL_DIR/config.json" | cut -d'"' -f4)

    if [ -n "$CURRENT_KEY" ] && [ "$CURRENT_KEY" != "" ]; then
        gum format --type=template \
            -- "Current Bark Key: {{Foreground \"82\" \"✓ Configured\"}}"
        echo ""

        if gum_confirm "Update Bark Key?" "No"; then
            NEW_KEY=$(gum_input --placeholder "Enter your Bark Key" --width 60)
            if [ -n "$NEW_KEY" ]; then
                # Update bark_key in config.json
                sed -i.bak "s/\"bark_key\":[[:space:]]*\"[^\"]*\"/\"bark_key\": \"$NEW_KEY\"/" "$SKILL_DIR/config.json"
                rm -f "$SKILL_DIR/config.json.bak"
                print_success "Bark Key updated"
            fi
        fi
    else
        gum format --type=template \
            -- "{{Foreground \"196\" \"✗ No Bark Key configured\"}}"
        echo ""

        if gum_confirm "Configure Bark Key now?" "Yes"; then
            NEW_KEY=$(gum_input --placeholder "Enter your Bark Key" --width 60)
            if [ -n "$NEW_KEY" ]; then
                sed -i.bak "s/\"bark_key\":[[:space:]]*\"[^\"]*\"/\"bark_key\": \"$NEW_KEY\"/" "$SKILL_DIR/config.json"
                rm -f "$SKILL_DIR/config.json.bak"
                print_success "Bark Key configured"
            else
                print_warn "Skipping Bark Key configuration"
            fi
        fi
    fi
else
    # Create config.json from example
    gum format --type=template \
        -- "No {{Foreground \"255\" \"config.json\"}} found."
    echo ""

    if gum_confirm "Configure Bark Key now?" "Yes"; then
        NEW_KEY=$(gum_input --placeholder "Enter your Bark Key" --width 60)

        # Copy example to config
        cp "$SKILL_DIR/config.example.json" "$SKILL_DIR/config.json"

        if [ -n "$NEW_KEY" ]; then
            sed -i.bak "s/\"bark_key\":[[:space:]]*\"[^\"]*\"/\"bark_key\": \"$NEW_KEY\"/" "$SKILL_DIR/config.json"
            rm -f "$SKILL_DIR/config.json.bak"
            print_success "Bark Key configured"
        else
            print_warn "Created empty config.json (please configure bark_key manually)"
        fi
    else
        # Copy example without key
        cp "$SKILL_DIR/config.example.json" "$SKILL_DIR/config.json"
        print_warn "Created config.json (please configure bark_key manually)"
    fi
fi

# =============================================================================
# Completion
# =============================================================================

echo ""
gum style \
    --border "$GUM_BORDER" \
    --border-foreground 82 \
    --align center \
    --margin "1 0" \
    --padding "$GUM_PADDING" \
    --foreground 82 \
    "Installation Complete! 🎉" ""
echo ""

gum format \
    --type=template \
    -- "Skill Directory: {{Foreground \"255\" \"$SKILL_DIR\"}}" \
    -- "Repository:      {{Foreground \"255\" \"$REPO_DIR\"}}"
echo ""

# Test notification
gum style --foreground 111 "Test Notification"
echo ""

if gum_confirm "Send a test notification?" "Yes"; then
    echo ""
    gum format -- foreground=255 -- "Running test notification..."
    echo ""

    if "$SKILL_DIR/scripts/notify.py" info "TaskNotifier skill installed successfully!" 2>&1; then
        print_success "Test notification sent!"
    else
        print_warn "Test notification had issues (check your configuration)"
    fi
fi

echo ""
gum style --foreground 111 "────────────────────────────────────────────"
echo ""

gum format \
    --type=template \
    -- "{{Foreground \"82\" \"✓\"}} Skill is now available in Claude Code" \
    -- "{{Foreground \"82\" \"✓\"}} Claude will automatically use it for task notifications" \
    -- "" \
    -- "{{Foreground \"226\" \"ℹ️\"}}  Configure Bark: {{Foreground \"255\" \"nano $SKILL_DIR/config.json\"}}" \
    -- "{{Foreground \"226\" \"ℹ️\"}}  Get Bark Key:  {{Foreground \"255\" \"https://github.com/Finb/Bark\"}}"
echo ""

gum style --foreground 111 "────────────────────────────────────────────"
echo ""
