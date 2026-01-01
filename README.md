# 🎉 Claude Code Skill - TaskNotifier

> Multi-channel notification tool for Claude Code - sends alerts via Bark (iOS push), desktop notifications, and sound alerts!

[![Skill](https://img.shields.io/badge/Claude_Code-Skill-blue)](https://claude.com/claude-code)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-47%20Passed-brightgreen)](#testing)

---

**[简体中文](./README.zh-CN.md) | English**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **📱 Bark Push** | iOS push notifications with custom icons and sounds |
| **💻 System Notify** | Desktop notifications on macOS/Linux/Windows |
| **🔊 Sound Alert** | Cross-platform sound with different tones per level |
| **🚀 Zero Dependency** | Pure Python standard library - no pip install needed |
| **🤖 Smart Trigger** | Auto-detects task success/failure status |

## 🎯 Notification Levels

| Level | Icon | Sound | Use Case |
|-------|------|-------|----------|
| `success` | ✅ | Glass | Build success, tests passed, deployment complete |
| `error` | ❌ | Basso | Build failed, tests failed, command error |
| `info` | ℹ️ | Ping | Task started, status update, warning |

## 📋 Prerequisites

- **Python 3.6+** (pre-installed on macOS/Linux)
- **Bark App** (iOS push, optional but recommended)
  - Download: [App Store](https://apps.apple.com/cn/app/bark-customed-notifications/id1403750366)
  - GitHub: [Finb/Bark](https://github.com/Finb/Bark)

## 🚀 Installation

### Step 1: Clone or Download

```bash
git clone https://github.com/nocoo/skill-task-notifier.git
cd skill-task-notifier
```

### Step 2: Configure Bark Key (Optional but Recommended)

1. Open Bark App and copy your push key
2. Create configuration file:

```bash
cp config.example.json config.json
```

3. Edit `config.json` in the skill root and add your Bark Key:

```json
{
  "bark_server": "https://api.day.app",
  "bark_key": "YOUR_BARK_KEY_HERE",
  "bark_group": "Claude Code",
  "sound_enabled": true,
  "system_notify_enabled": true
}
```

> 💡 **Tip:** If you don't configure Bark Key, system notifications and sound alerts will still work.

### Step 3: Run Installer

```bash
./install.sh
```

The installer will automatically:
- Create `~/.claude/skills/task-notifier/` directory
- Create symbolic links to skill files
- Set executable permissions
- Verify installation integrity

## 📖 Usage

### Enable in Claude Code

Add to your global config file `~/.claude/CLAUDE.md`:

```markdown
## Task Notifications

When completing tasks that take more than 1 minute, or when I explicitly ask for notification:
- Use the TaskNotifier skill to send me a notification
- Use 'success' level if the task completed without errors
- Use 'error' level if any command failed (exit code != 0)
- Use 'info' level for status updates

Example:
```
python3 ~/.claude/skills/task-notifier/scripts/notify.py success "Build completed in 2m 15s"
```
```

### Example Prompts

```
# Let Claude notify you after build
"Build the project and notify me when done"

# Notify after tests
"Run all tests and send me a notification when finished"

# Notify after long task
"Deploy to production and notify me of the result"

# Explicit notification request
"Run the migration and tell me when it's done"
```

### Manual Testing

```bash
# Test success notification
python3 ~/.claude/skills/task-notifier/scripts/notify.py success "Test notification"

# Test error notification
python3 ~/.claude/skills/task-notifier/scripts/notify.py error "Test error"

# Test info notification
python3 ~/.claude/skills/task-notifier/scripts/notify.py info "Test info"
```

## 📁 Project Structure

```
skill-task-notifier/
├── .gitignore              # Git ignore rules
├── config.example.json     # Configuration template
├── install.sh              # Installation script
├── README.md               # This file (English)
├── README.zh-CN.md         # Chinese version
├── requirements.txt        # Zero dependency declaration
├── run_tests.sh            # Test runner script
├── SKILL.md                # Skill definition (used by Claude)
├── config.json             # Your configuration (not in git)
└── scripts/
    ├── notify.py           # Core notification logic (zero-dep Python)
    └── run.py              # Unified entry point (for consistency)
```

## 🔧 How It Works

```
┌─────────────────┐
│  Claude Code    │
│  (Task Done)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  TaskNotifier Skill                     │
│  ──────────────────────────────────     │
│  ┌─────────────────────────────────┐   │
│  │  1. Read config.json (root)     │   │
│  │  2. Determine level             │   │
│  │  3. Send Bark Push (iOS)        │   │
│  │  4. Show System Notification    │   │
│  │  5. Play Sound                  │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │   Bark   │  │  Desktop │  │  Sound │ │
│  │   (iOS)  │  │  (macOS) │  │ (afplay)│ │
│  └──────────┘  └──────────┘  └────────┘ │
└─────────────────────────────────────────┘
```

## 🧪 Testing

```bash
# Run all tests
./run_tests.sh

# Or use unittest directly
python3 -m unittest discover -s tests -p 'test_*.py' -v

# With coverage report (requires: pip install coverage)
coverage run --source='scripts' -m unittest discover -s tests
coverage report -m
coverage html
```

### Test Coverage

| Metric | Value |
|--------|-------|
| **Tests** | 47 |
| **Pass Rate** | 100% |
| **Code Coverage** | 90% |
| **Lines** | ~200 |

## 🔧 Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bark_server` | string | `https://api.day.app` | Bark server URL |
| `bark_key` | string | `""` | Your Bark push key |
| `bark_group` | string | `"Claude Code"` | Message group name |
| `sound_enabled` | boolean | `true` | Enable sound alerts |
| `system_notify_enabled` | boolean | `true` | Enable desktop notifications |

## ❓ Troubleshooting

### No notifications received?

1. **Check Bark Key**: Verify `bark_key` is correctly set in `config.json` (skill root)
2. **Check Sound**: Ensure system volume is up on macOS
3. **Check Permissions**: Ensure `notify.py` has execute permission (`chmod +x scripts/notify.py`)

### macOS notification permission denied

```bash
# Grant Terminal notification permission
# System Settings → Notifications → Terminal → Allow Notifications
```

### Linux notify-send not found

```bash
# Ubuntu/Debian
sudo apt install libnotify-bin

# Fedora/RHEL
sudo dnf install libnotify

# Arch Linux
sudo pacman -S libnotify
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 👨‍💻 Author

Created by [@nocoo](https://github.com/nocoo)

## 🙏 Acknowledgments

- [Bark](https://github.com/Finb/Bark) - iOS push notification service
- [Claude Code](https://claude.com/claude-code) - AI programming assistant

---

**[简体中文](./README.zh-CN.md) | English**
