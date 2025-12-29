#!/usr/bin/env bash
# Test runner for claude-skill-task-notifier
# Runs all tests and generates coverage report

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  TaskNotifier Test Runner${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if coverage is available
if command -v coverage &> /dev/null; then
    USE_COVERAGE=true
    echo -e "${GREEN}[INFO]${NC}  Using coverage module"
else
    USE_COVERAGE=false
    echo -e "${YELLOW}[WARN]${NC}  coverage module not found. Install with: pip install coverage"
    echo -e "${YELLOW}[INFO]${NC}  Running tests without coverage..."
fi

echo ""
echo -e "${BLUE}[STEP]${NC}  Running tests..."
echo ""

if [ "$USE_COVERAGE" = true ]; then
    # Run with coverage
    cd "$SCRIPT_DIR"
    coverage run --source='scripts' -m unittest discover -s tests -p 'test_*.py' -v
    echo ""
    echo -e "${BLUE}[STEP]${NC}  Generating coverage report..."
    echo ""
    coverage report -m
    echo ""
    echo -e "${BLUE}[STEP]${NC}  Generating HTML coverage report..."
    coverage html
    echo -e "${GREEN}[OK]${NC}   HTML report: ${BLUE}file://$SCRIPT_DIR/htmlcov/index.html${NC}"
else
    # Run without coverage
    cd "$SCRIPT_DIR"
    python3 -m unittest discover -s tests -p 'test_*.py' -v
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Tests Complete! 🎉${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
