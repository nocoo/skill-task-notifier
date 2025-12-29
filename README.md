# Claude Code Skill - TaskNotifier

> 多端任务通知工具，让 Claude Code 在任务完成时通过 Bark 推送、系统弹窗、声音提醒你

[![Skill](https://img.shields.io/badge/Claude_Code-Skill-blue)](https://claude.com/claude-code)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Features

| 功能 | 说明 |
|------|------|
| **Bark 推送** | iOS 推送通知，支持自定义图标和声音 |
| **系统通知** | macOS/Linux/Windows 桌面弹窗 |
| **声音提醒** | 跨平台声音播放，根据任务级别使用不同音效 |
| **零依赖** | 仅使用 Python 标准库，无需 pip install |
| **智能触发** | 自动检测任务成功/失败状态 |

## Notification Levels

| 级别 | 图标 | 声音 | 使用场景 |
|------|------|------|----------|
| `success` | ✓ (绿) | Glass | 构建成功、测试通过、部署完成 |
| `error` | ✕ (红) | Basso | 构建失败、测试失败、命令报错 |
| `info` | ℹ (蓝) | Ping | 任务开始、状态更新、警告 |

## Prerequisites

- **Python 3.6+** (macOS/Linux 自带)
- **Bark App** (iOS 推送，可选)
  - 下载: [App Store](https://apps.apple.com/cn/app/bark-customed-notifications/id1403750366)
  - GitHub: [Finb/Bark](https://github.com/Finb/Bark)

## Installation

### Step 1: Clone or Download

```bash
git clone https://github.com/YOUR_USERNAME/claude-skill-task-notifier.git
cd claude-skill-task-notifier
```

### Step 2: Configure Bark Key (Optional but Recommended)

1. 打开 Bark App，复制你的推送密钥
2. 创建配置文件：

```bash
cp config.example.json scripts/config.json
```

3. 编辑 `scripts/config.json`，填入你的 Bark Key：

```json
{
  "bark_server": "https://api.day.app",
  "bark_key": "YOUR_BARK_KEY_HERE",
  "sound_enabled": true,
  "system_notify_enabled": true
}
```

> 如果不配置 Bark Key，系统通知和声音提醒仍然可用。

### Step 3: Run Installer

```bash
./install.sh
```

安装脚本会自动：
- 创建 `~/.claude/skills/task-notifier/` 目录
- 创建软链接到 Skill 文件
- 设置可执行权限
- 验证安装完整性

## Usage

### Enable in Claude Code

在你的全局配置文件 `~/.claude/CLAUDE.md` 中添加：

```markdown
## Task Notifications

When completing tasks that take more than 1 minute, or when I explicitly ask for notification:
- Use the TaskNotifier skill to send me a notification
- Use 'success' level if the task completed without errors
- Use 'error' level if any command failed (exit code != 0)
- Use 'info' level for status updates

Example usage:
```
python3 ~/.claude/skills/task-notifier/scripts/notify.py success "Build completed in 2m 15s"
```
```

### Example Prompts

```
# 让 Claude 在构建完成后通知你
"Build the project and notify me when done"

# 让 Claude 在测试完成后通知你
"Run all tests and send me a notification when finished"

# 让 Claude 在长时间任务后通知你
"Deploy to production and notify me of the result"

# 显式要求通知
"Run the migration and tell me when it's done"
```

### Manual Testing

测试通知功能是否正常：

```bash
# 测试成功通知
python3 ~/.claude/skills/task-notifier/scripts/notify.py success "Test notification"

# 测试错误通知
python3 ~/.claude/skills/task-notifier/scripts/notify.py error "Test error"

# 测试信息通知
python3 ~/.claude/skills/task-notifier/scripts/notify.py info "Test info"
```

## File Structure

```
claude-skill-task-notifier/
├── .gitignore              # Git ignore rules
├── config.example.json     # Configuration template
├── install.sh              # Installation script
├── README.md               # This file
├── SKILL.md                # Skill definition (used by Claude)
└── scripts/
    ├── notify.py           # Core notification logic (zero-dep Python)
    └── .gitkeep
```

## How It Works

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
│  │  1. Read config.json            │   │
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

## Troubleshooting

### No notifications received?

1. **Check Bark Key**: 确认 `scripts/config.json` 中的 `bark_key` 已正确填入
2. **Check Sound**: macOS 确保系统音量已打开
3. **Check Permissions**: 确保 `notify.py` 有可执行权限 (`chmod +x scripts/notify.py`)

### macOS notification permission denied

```bash
# 确保终端有通知权限
# 系统设置 → 通知 → 终端 → 允许通知
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

## Contributing

欢迎提交 Issue 和 Pull Request！

## License

MIT License - 详见 [LICENSE](LICENSE) 文件

## Author

Created by [@nocoli](https://github.com/nocoli)

## Acknowledgments

- [Bark](https://github.com/Finb/Bark) - iOS 推送通知服务
- [Claude Code](https://claude.com/claude-code) - AI 编程助手
