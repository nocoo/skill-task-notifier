#!/usr/bin/env python3
"""
Task Notifier - Multi-channel notification script
Zero dependency: Uses only Python standard library
"""

import sys
import os
import json
import platform
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path


# =============================================================================
# Constants
# =============================================================================

# Bark notification configuration per level
BARK_CONFIG = {
    "success": {
        "group": "Claude_Success",
        "icon": "https://via.placeholder.com/80/4CAF50/FFFFFF?text=✓",
        "sound": "bell"
    },
    "error": {
        "group": "Claude_Error",
        "icon": "https://via.placeholder.com/80/F44336/FFFFFF?text=✕",
        "sound": "alarm"
    },
    "info": {
        "group": "Claude_Info",
        "icon": "https://via.placeholder.com/80/2196F3/FFFFFF?text=i",
        "sound": "bell"
    }
}

# Sound files per level (macOS system sounds)
SOUND_MAP = {
    "success": "Glass",
    "error": "Basso",
    "info": "Ping"
}


# =============================================================================
# Configuration
# =============================================================================

def get_config_path():
    """Get the path to config.json in the same directory as this script."""
    script_dir = Path(__file__).parent.resolve()
    return script_dir / "config.json"


def load_config():
    """Load configuration from config.json."""
    config_path = get_config_path()

    if not config_path.exists():
        example_path = config_path.parent / "config.example.json"
        print(f"[ERROR] Config file not found: {config_path}", file=sys.stderr)
        print(f"[INFO]  Please copy the example config:", file=sys.stderr)
        print(f"        cp {example_path} {config_path}", file=sys.stderr)
        print(f"[INFO]  Then edit config.json and fill in your bark_key", file=sys.stderr)
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in config.json: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to read config.json: {e}", file=sys.stderr)
        sys.exit(1)


# =============================================================================
# Bark Notification
# =============================================================================

def send_bark_notification(config, level, message):
    """Send push notification via Bark."""
    bark_key = config.get("bark_key", "").strip()
    if not bark_key:
        print("[WARN]  bark_key is empty, skipping Bark notification", file=sys.stderr)
        return False

    bark_server = config.get("bark_server", "https://api.day.app").rstrip("/")

    level_config = BARK_CONFIG.get(level, BARK_CONFIG["info"])

    # Build URL parameters (use custom group from config, default to "Claude Code")
    params = {
        "group": config.get("bark_group", "Claude Code"),
        "icon": level_config["icon"],
        "sound": level_config["sound"],
        "level": level.lower()
    }

    # Construct URL
    url = f"{bark_server}/{bark_key}/{urllib.parse.quote(message)}"
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"

    try:
        req = urllib.request.Request(
            full_url,
            method="GET",
            headers={"User-Agent": "Claude-Task-Notifier/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                if data.get("code") == 200:
                    print(f"[OK]    Bark notification sent (level: {level})")
                    return True
                else:
                    print(f"[WARN]  Bark response: {data.get('message', 'Unknown error')}", file=sys.stderr)
            return False
    except urllib.error.HTTPError as e:
        print(f"[WARN]  Bark HTTP error: {e.code} - {e.reason}", file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        print(f"[WARN]  Bark connection error: {e.reason}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[WARN]  Bark notification failed: {e}", file=sys.stderr)
        return False


# =============================================================================
# System Notification
# =============================================================================

def send_system_notification(level, message):
    """Send desktop notification based on OS."""
    system = platform.system()

    title_map = {
        "success": "✅ Task Completed",
        "error": "❌ Task Failed",
        "info": "ℹ️ Task Notification"
    }
    title = title_map.get(level, "Task Notification")

    if system == "Darwin":  # macOS
        return _send_macos_notification(title, message)
    elif system == "Linux":
        return _send_linux_notification(title, message)
    elif system == "Windows":
        return _send_windows_notification(title, message)
    else:
        print(f"[WARN]  Unsupported OS for system notification: {system}", file=sys.stderr)
        return False


def _send_macos_notification(title, message):
    """Send notification on macOS using osascript."""
    script = f'display notification "{message}" with title "{title}"'
    try:
        subprocess.run(
            ["osascript", "-e", script],
            check=True,
            capture_output=True,
            timeout=5
        )
        print(f"[OK]    System notification sent (macOS)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[WARN]  macOS notification failed: {e.stderr.decode().strip()}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[WARN]  macOS notification error: {e}", file=sys.stderr)
        return False


def _send_linux_notification(title, message):
    """Send notification on Linux using notify-send."""
    try:
        subprocess.run(
            ["notify-send", title, message],
            check=True,
            capture_output=True,
            timeout=5
        )
        print(f"[OK]    System notification sent (Linux)")
        return True
    except FileNotFoundError:
        print("[WARN]  notify-send not found. Install: sudo apt install libnotify-bin", file=sys.stderr)
        return False
    except subprocess.CalledProcessError as e:
        print(f"[WARN]  Linux notification failed: {e.stderr.decode().strip()}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[WARN]  Linux notification error: {e}", file=sys.stderr)
        return False


def _send_windows_notification(title, message):
    """Send notification on Windows using PowerShell BurntToast."""
    ps_script = f'''
    Add-Type -AssemblyName Windows.UI.Notifications
    Add-Type -AssemblyName Windows.Data.Xml.Dom

    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null

    $template = @"
    <toast>
        <visual>
            <binding template="ToastGeneric">
                <text>{title}</text>
                <text>{message}</text>
            </binding>
        </visual>
    </toast>
"@

    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml($template)
    $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Claude Task Notifier").Show($toast)
    '''

    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            check=True,
            capture_output=True,
            timeout=10
        )
        print(f"[OK]    System notification sent (Windows)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[WARN]  Windows notification failed: {e.stderr.decode().strip()}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[WARN]  Windows notification error: {e}", file=sys.stderr)
        return False


# =============================================================================
# Sound Notification
# =============================================================================

def play_sound(level):
    """Play sound based on notification level and OS."""
    system = platform.system()

    if system == "Darwin":  # macOS
        return _play_macos_sound(level)
    elif system == "Linux":
        return _play_linux_sound(level)
    elif system == "Windows":
        return _play_windows_sound(level)
    else:
        print(f"[WARN]  Unsupported OS for sound: {system}", file=sys.stderr)
        return False


def _play_macos_sound(level):
    """Play system sound on macOS using afplay."""
    sound_name = SOUND_MAP.get(level, "Ping")
    sound_path = f"/System/Library/Sounds/{sound_name}.aiff"

    if not os.path.exists(sound_path):
        print(f"[WARN]  Sound not found: {sound_path}", file=sys.stderr)
        return False

    try:
        subprocess.run(
            ["afplay", sound_path],
            check=True,
            capture_output=True,
            timeout=5
        )
        print(f"[OK]    Sound played: {sound_name}")
        return True
    except subprocess.CalledProcessError:
        print(f"[WARN]  Failed to play sound: {sound_name}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[WARN]  Sound playback error: {e}", file=sys.stderr)
        return False


def _play_linux_sound(level):
    """Play sound on Linux using aplay or paplay."""
    # Try paplay (PulseAudio) first, then aplay (ALSA)
    commands = ["paplay", "aplay"]

    # Sound files (standard system sounds)
    sound_files = [
        "/usr/share/sounds/freedesktop/stereo/complete.oga",
        "/usr/share/sounds/freedesktop/stereo/message.oga",
        "/usr/share/sounds/freedesktop/stereo/dialog-information.oga"
    ]

    for cmd in commands:
        for sound_file in sound_files:
            if not os.path.exists(sound_file):
                continue
            try:
                subprocess.run(
                    [cmd, sound_file],
                    check=True,
                    capture_output=True,
                    timeout=5
                )
                print(f"[OK]    Sound played: {os.path.basename(sound_file)}")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

    print("[WARN]  No sound files found. Install: sudo apt install freedesktop-sound-theme", file=sys.stderr)
    return False


def _play_windows_sound(level):
    """Play sound on Windows using PowerShell."""
    sound_map = {
        "success": "System.Asterisk",
        "error": "System.Hand",
        "info": "System.Default"
    }
    sound_name = sound_map.get(level, "System.Default")

    ps_script = f'''
    $sound = New-Object System.Media.SystemSound::{sound_name}
    $sound.Play()
    '''

    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            check=True,
            capture_output=True,
            timeout=5
        )
        print(f"[OK]    Sound played: {sound_name}")
        return True
    except subprocess.CalledProcessError:
        print(f"[WARN]  Failed to play Windows sound", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[WARN]  Windows sound error: {e}", file=sys.stderr)
        return False


# =============================================================================
# Main Entry
# =============================================================================

def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print(f"Usage: python3 {os.path.basename(__file__)} <level> <message>", file=sys.stderr)
        print("", file=sys.stderr)
        print("  level:   success | error | info", file=sys.stderr)
        print("  message: Notification message (use quotes for spaces)", file=sys.stderr)
        print("", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print(f"  python3 {os.path.basename(__file__)} success \"Build completed!\"", file=sys.stderr)
        print(f"  python3 {os.path.basename(__file__)} error \"Tests failed!\"", file=sys.stderr)
        print(f"  python3 {os.path.basename(__file__)} info \"Task in progress...\"", file=sys.stderr)
        sys.exit(1)

    level = sys.argv[1].lower()
    message = sys.argv[2]

    # Validate level
    if level not in BARK_CONFIG:
        print(f"[ERROR] Invalid level: {level}", file=sys.stderr)
        print(f"[INFO]  Valid levels: {', '.join(BARK_CONFIG.keys())}", file=sys.stderr)
        sys.exit(1)

    # Load configuration
    config = load_config()

    # Send notifications based on configuration
    results = []

    # Bark notification (always attempt if configured)
    bark_result = send_bark_notification(config, level, message)
    results.append(("Bark", bark_result))

    # System notification
    if config.get("system_notify_enabled", True):
        system_result = send_system_notification(level, message)
        results.append(("System", system_result))

    # Sound notification
    if config.get("sound_enabled", True):
        sound_result = play_sound(level)
        results.append(("Sound", sound_result))

    # Print summary
    print("", file=sys.stderr)
    success_count = sum(1 for _, r in results if r)
    print(f"[SUMMARY] Notification complete: {success_count}/{len(results)} channels succeeded")


if __name__ == "__main__":
    main()
