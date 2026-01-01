---
name: task-notifier
description: Multi-channel notification tool (Bark/System/Sound) with zero dependencies
---

# TaskNotifier

## Description
Multi-channel notification tool that sends alerts via Bark (iOS push notification), desktop notifications (macOS/Linux/Windows), and sound alerts. Requires zero external dependencies.

## Usage Rules

### Trigger Levels

| Level | Use Case | Icon | Sound |
|-------|----------|------|-------|
| `success` | Task completed successfully, build passed, tests passed, deployment succeeded | ✓ (Green) | Glass |
| `error` | Task failed, build broke, tests failed, deployment failed, command returned non-zero exit code | ✕ (Red) | Basso |
| `info` | Task started, intermediate status, general updates, warnings | ℹ (Blue) | Ping |

### When to Use

**MANDATORY** - Always call this Skill in the following scenarios:

1. **On User Request**
   - User explicitly asks for notification: "notify me when done", "tell me when it finishes"
   - User asks for task completion alert

2. **After Long-Running Tasks** (> 1 minute)
   - Build processes (npm run build, cargo build, make, etc.)
   - Test suites (pytest, npm test, cargo test, etc.)
   - Deployment operations
   - Large file operations
   - Data processing/migration tasks
   - ANY task that takes more than 1 minute to complete

3. **On Failure/Errors**
   - **CRITICAL**: If ANY command returns exit code != 0, MUST call `error` level
   - Build failures, test failures, deployment failures
   - Script execution errors
   - Network errors that prevent task completion

### Determining the Level

```
Previous Step Exit Code = 0  → Use 'success'
Previous Step Exit Code != 0 → Use 'error'
Ambiguous/Status Update        → Use 'info'
```

## Command Examples

```bash
# Success - Task completed successfully
python3 scripts/notify.py success "Build completed in 2m 15s"

# Error - Task failed
python3 scripts/notify.py error "Build failed: dependency not found"

# Info - General status update
python3 scripts/notify.py info "Running tests... (15 test suites)"

# Success - With detailed context
python3 scripts/notify.py success "Tests passed: 127 passed, 0 failed"

# Error - With command output
python3 scripts/notify.py error "Deployment failed: timeout waiting for response"
```

## Configuration

The Skill reads `config.json` in the skill root directory. Ensure it exists before use:

```bash
cp config.example.json config.json
# Then edit config.json and add your bark_key
```

## Implementation Notes

- The script uses only Python standard library (zero dependencies)
- Cross-platform: works on macOS, Linux, and Windows
- Falls back gracefully if a notification channel fails
- All channels execute in parallel for immediate feedback
