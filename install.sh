#!/usr/bin/env bash
# Installation script for Claude Code TaskNotifier Skill
# This script creates symlinks in ~/.claude/skills/task-notifier

set -e  # Exit on error

# =============================================================================
# Configuration
# =============================================================================

SKILL_NAME="task-notifier"
SKILL_DIR="$HOME/.claude/skills/$SKILL_NAME"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Functions
# =============================================================================

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Claude Code Skill - TaskNotifier Installer${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC}   $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "       $1"
}

# =============================================================================
# Installation
# =============================================================================

print_header

# Step 1: Check/Create skill directory
print_step "Creating skill directory..."
if [ -d "$SKILL_DIR" ]; then
    print_warn "Directory already exists: $SKILL_DIR"
    read -p "       Remove existing installation? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$SKILL_DIR"
        print_success "Removed existing installation"
    else
        print_error "Installation cancelled"
        exit 1
    fi
fi

mkdir -p "$SKILL_DIR"
print_success "Created directory: $SKILL_DIR"

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

print_success "Repository structure verified"

# Step 3: Create symbolic links
print_step "Creating symbolic links..."

# Link SKILL.md
ln -s "$REPO_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"
print_success "Linked: SKILL.md"

# Link scripts directory
ln -s "$REPO_DIR/scripts" "$SKILL_DIR/scripts"
print_success "Linked: scripts/"

# Link config file (prefer config.json, fallback to config.example.json)
if [ -f "$REPO_DIR/config.json" ]; then
    ln -s "$REPO_DIR/config.json" "$SKILL_DIR/config.json"
    print_success "Linked: config.json"
elif [ -f "$REPO_DIR/config.example.json" ]; then
    ln -s "$REPO_DIR/config.example.json" "$SKILL_DIR/config.json"
    print_warn "Using config.example.json (please rename to config.json and configure)"
else
    print_error "No configuration file found!"
    exit 1
fi

# Step 4: Set executable permissions
print_step "Setting executable permissions..."

chmod +x "$REPO_DIR/scripts/notify.py"
print_success "Made notify.py executable"

# Step 5: Verify installation
print_step "Verifying installation..."

if [ ! -L "$SKILL_DIR/SKILL.md" ]; then
    print_error "SKILL.md link verification failed"
    exit 1
fi

# Check if scripts directory link exists
if [ ! -L "$SKILL_DIR/scripts" ]; then
    print_error "scripts/ link verification failed"
    exit 1
fi

# Check if notify.py exists and is executable through the symlink
if [ ! -x "$SKILL_DIR/scripts/notify.py" ]; then
    print_error "scripts/notify.py not found or not executable"
    exit 1
fi

print_success "All links verified"

# =============================================================================
# Completion
# =============================================================================

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Installation Complete! 🎉${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Installation Details:${NC}"
print_info "Skill Directory:    $SKILL_DIR"
print_info "Repository Source:  $REPO_DIR"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Configure your Bark Key${NC}"
echo ""
print_info "1. Edit the configuration file:"
echo -e "       ${BLUE}nano $SKILL_DIR/config.json${NC}"
echo ""
print_info "2. Fill in your bark_key:"
echo -e "       {"
echo -e "         \"bark_server\": \"https://api.day.app\","
echo -e "         \"bark_key\": \"YOUR_BARK_KEY_HERE\",  ← Add your key"
echo -e "         \"sound_enabled\": true,"
echo -e "         \"system_notify_enabled\": true"
echo -e "       }"
echo ""
print_info "3. Get your Bark key from: https://github.com/Finb/Bark"
echo ""
echo -e "${BLUE}────────────────────────────────────────────────────────────────────────────${NC}"
print_info "Skill is now available in Claude Code!"
print_info "Usage: Claude will automatically use it for task completion notifications."
echo -e "${BLUE}────────────────────────────────────────────────────────────────────────────${NC}"
echo ""
