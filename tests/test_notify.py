#!/usr/bin/env python3
"""
Comprehensive tests for scripts/notify.py
Uses only Python standard library (unittest, unittest.mock)
"""

import unittest
import json
import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock, call
from urllib.error import HTTPError, URLError

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import notify


class TestConfigPath(unittest.TestCase):
    """Test configuration path detection."""

    def test_get_config_path(self):
        """Test that config path is correctly resolved."""
        result = notify.get_config_path()
        self.assertIsInstance(result, Path)
        self.assertTrue(result.name == "config.json")
        self.assertIn("scripts", str(result))


class TestLoadConfig(unittest.TestCase):
    """Test configuration loading."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = Path(self.temp_dir) / "config.json"

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    @patch('notify.get_config_path')
    def test_load_config_success(self, mock_get_config_path):
        """Test successful config loading."""
        test_config = {
            "bark_server": "https://test.example.com",
            "bark_key": "test_key_123",
            "sound_enabled": True,
            "system_notify_enabled": False
        }
        mock_get_config_path.return_value = self.test_config_path

        with open(self.test_config_path, 'w') as f:
            json.dump(test_config, f)

        result = notify.load_config()
        self.assertEqual(result["bark_server"], "https://test.example.com")
        self.assertEqual(result["bark_key"], "test_key_123")
        self.assertTrue(result["sound_enabled"])
        self.assertFalse(result["system_notify_enabled"])

    @patch('notify.get_config_path')
    @patch('sys.stderr', new_callable=MagicMock)
    def test_load_config_file_not_found(self, mock_stderr, mock_get_config_path):
        """Test loading config when file doesn't exist."""
        mock_get_config_path.return_value = Path("/nonexistent/config.json")

        with self.assertRaises(SystemExit) as context:
            notify.load_config()
        self.assertEqual(context.exception.code, 1)

    @patch('notify.get_config_path')
    @patch('sys.stderr', new_callable=MagicMock)
    def test_load_config_invalid_json(self, mock_stderr, mock_get_config_path):
        """Test loading config with invalid JSON."""
        mock_get_config_path.return_value = self.test_config_path

        with open(self.test_config_path, 'w') as f:
            f.write("{ invalid json }")

        with self.assertRaises(SystemExit) as context:
            notify.load_config()
        self.assertEqual(context.exception.code, 1)

    @patch('notify.get_config_path')
    @patch('sys.stderr', new_callable=MagicMock)
    @patch('builtins.open', side_effect=PermissionError("Access denied"))
    def test_load_config_permission_error(self, mock_open, mock_stderr, mock_get_config_path):
        """Test loading config with permission error."""
        mock_get_config_path.return_value = self.test_config_path

        with self.assertRaises(SystemExit) as context:
            notify.load_config()
        self.assertEqual(context.exception.code, 1)


class TestBarkNotification(unittest.TestCase):
    """Test Bark notification functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "bark_server": "https://api.day.app",
            "bark_key": "test_key_123",
            "bark_group": "TestGroup",
            "icons": {
                "success": "https://example.com/success.png",
                "error": "https://example.com/error.png",
                "info": "https://example.com/info.png"
            },
            "sound_enabled": True,
            "system_notify_enabled": True
        }

    @patch('notify.urllib.request.urlopen')
    @patch('builtins.print')
    def test_send_bark_notification_success(self, mock_print, mock_urlopen):
        """Test successful Bark notification."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"code": 200, "message": "success"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = notify.send_bark_notification(self.config, "success", "Test message")

        self.assertTrue(result)
        mock_urlopen.assert_called_once()
        # Verify URL construction (Request object has full_url attribute)
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        url = request.full_url
        self.assertIn("test_key_123", url)
        self.assertIn("Test%20message", url)
        self.assertIn("group=TestGroup", url)
        self.assertIn("icon=https%3A%2F%2Fexample.com%2Fsuccess.png", url)

    @patch('notify.urllib.request.urlopen')
    @patch('builtins.print')
    def test_send_bark_notification_custom_icons(self, mock_print, mock_urlopen):
        """Test Bark notification with custom icons."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"code": 200, "message": "success"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = notify.send_bark_notification(self.config, "error", "Error message")

        self.assertTrue(result)
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        url = request.full_url
        self.assertIn("icon=https%3A%2F%2Fexample.com%2Ferror.png", url)

    @patch('notify.urllib.request.urlopen')
    @patch('builtins.print')
    def test_send_bark_notification_icon_fallback(self, mock_print, mock_urlopen):
        """Test Bark notification with icon fallback to info."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"code": 200, "message": "success"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config_no_icon = {
            "bark_server": "https://api.day.app",
            "bark_key": "test_key_123",
            "icons": {
                "info": "https://example.com/info.png"
            }
        }

        result = notify.send_bark_notification(config_no_icon, "success", "Test message")

        self.assertTrue(result)
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        url = request.full_url
        # Should fallback to info icon
        self.assertIn("icon=https%3A%2F%2Fexample.com%2Finfo.png", url)

    @patch('notify.urllib.request.urlopen')
    @patch('builtins.print')
    def test_send_bark_notification_no_icons(self, mock_print, mock_urlopen):
        """Test Bark notification without icons config."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"code": 200, "message": "success"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config_no_icons = {
            "bark_server": "https://api.day.app",
            "bark_key": "test_key_123"
        }

        result = notify.send_bark_notification(config_no_icons, "success", "Test message")

        self.assertTrue(result)
        # Should still work, just without custom icon (using default from BARK_CONFIG)
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        url = request.full_url
        self.assertIn("test_key_123", url)

    @patch('notify.urllib.request.urlopen')
    @patch('builtins.print')
    def test_send_bark_notification_default_group(self, mock_print, mock_urlopen):
        """Test Bark notification with default group."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"code": 200, "message": "success"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config_no_group = {
            "bark_server": "https://api.day.app",
            "bark_key": "test_key_123"
        }

        result = notify.send_bark_notification(config_no_group, "success", "Test message")

        self.assertTrue(result)
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        url = request.full_url
        self.assertIn("group=Claude+Code", url)

    @patch('builtins.print')
    def test_send_bark_notification_empty_key(self, mock_print):
        """Test Bark notification with empty key."""
        config = self.config.copy()
        config["bark_key"] = ""

        result = notify.send_bark_notification(config, "success", "Test message")

        self.assertFalse(result)

    @patch('builtins.print')
    def test_send_bark_notification_whitespace_key(self, mock_print):
        """Test Bark notification with whitespace-only key."""
        config = self.config.copy()
        config["bark_key"] = "   "

        result = notify.send_bark_notification(config, "success", "Test message")

        self.assertFalse(result)

    @patch('notify.urllib.request.urlopen')
    @patch('builtins.print')
    def test_send_bark_notification_http_error(self, mock_print, mock_urlopen):
        """Test Bark notification with HTTP error."""
        mock_urlopen.side_effect = HTTPError("url", 500, "Internal Server Error", {}, None)

        result = notify.send_bark_notification(self.config, "success", "Test message")

        self.assertFalse(result)

    @patch('notify.urllib.request.urlopen')
    @patch('builtins.print')
    def test_send_bark_notification_url_error(self, mock_print, mock_urlopen):
        """Test Bark notification with URL error."""
        mock_urlopen.side_effect = URLError("Connection refused")

        result = notify.send_bark_notification(self.config, "success", "Test message")

        self.assertFalse(result)

    @patch('notify.urllib.request.urlopen')
    @patch('builtins.print')
    def test_send_bark_notification_timeout(self, mock_print, mock_urlopen):
        """Test Bark notification with timeout."""
        mock_urlopen.side_effect = TimeoutError("Request timed out")

        result = notify.send_bark_notification(self.config, "success", "Test message")

        self.assertFalse(result)

    @patch('notify.urllib.request.urlopen')
    @patch('builtins.print')
    def test_send_bark_notification_error_response(self, mock_print, mock_urlopen):
        """Test Bark notification with error response from server."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"code": 400, "message": "Bad Request"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = notify.send_bark_notification(self.config, "success", "Test message")

        self.assertFalse(result)

    @patch('notify.urllib.request.urlopen')
    @patch('builtins.print')
    def test_send_bark_notification_all_levels(self, mock_print, mock_urlopen):
        """Test Bark notification for all levels."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"code": 200, "message": "success"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        levels = ["success", "error", "info"]
        for level in levels:
            result = notify.send_bark_notification(self.config, level, f"Test {level}")
            self.assertTrue(result)

        self.assertEqual(mock_urlopen.call_count, 3)

    @patch('notify.urllib.request.urlopen')
    @patch('builtins.print')
    def test_send_bark_notification_unknown_level(self, mock_print, mock_urlopen):
        """Test Bark notification with unknown level (should default to info)."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"code": 200, "message": "success"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = notify.send_bark_notification(self.config, "unknown", "Test message")

        self.assertTrue(result)


class TestSystemNotification(unittest.TestCase):
    """Test system notification functionality."""

    @patch('notify.platform.system')
    @patch('notify._send_macos_notification')
    @patch('builtins.print')
    def test_send_system_notification_macos(self, mock_print, mock_send_macos, mock_system):
        """Test system notification on macOS."""
        mock_system.return_value = "Darwin"
        mock_send_macos.return_value = True

        result = notify.send_system_notification("success", "Test message")

        self.assertTrue(result)
        mock_send_macos.assert_called_once_with("✅ Task Completed", "Test message")

    @patch('notify.platform.system')
    @patch('notify._send_linux_notification')
    @patch('builtins.print')
    def test_send_system_notification_linux(self, mock_print, mock_send_linux, mock_system):
        """Test system notification on Linux."""
        mock_system.return_value = "Linux"
        mock_send_linux.return_value = True

        result = notify.send_system_notification("error", "Test message")

        self.assertTrue(result)
        mock_send_linux.assert_called_once_with("❌ Task Failed", "Test message")

    @patch('notify.platform.system')
    @patch('notify._send_windows_notification')
    @patch('builtins.print')
    def test_send_system_notification_windows(self, mock_print, mock_send_windows, mock_system):
        """Test system notification on Windows."""
        mock_system.return_value = "Windows"
        mock_send_windows.return_value = True

        result = notify.send_system_notification("info", "Test message")

        self.assertTrue(result)
        mock_send_windows.assert_called_once_with("ℹ️ Task Notification", "Test message")

    @patch('notify.platform.system')
    @patch('builtins.print')
    def test_send_system_notification_unsupported_os(self, mock_print, mock_system):
        """Test system notification on unsupported OS."""
        mock_system.return_value = "FreeBSD"

        result = notify.send_system_notification("success", "Test message")

        self.assertFalse(result)

    @patch('notify.subprocess.run')
    @patch('builtins.print')
    def test_send_macos_notification_success(self, mock_print, mock_run):
        """Test macOS notification success."""
        mock_run.return_value = MagicMock()

        result = notify._send_macos_notification("Test Title", "Test message")

        self.assertTrue(result)
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        self.assertEqual(call_args[0][0], ["osascript", "-e", 'display notification "Test message" with title "Test Title"'])

    @patch('notify.subprocess.run')
    @patch('builtins.print')
    def test_send_macos_notification_failure(self, mock_print, mock_run):
        """Test macOS notification failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "osascript", stderr=b"Error")

        result = notify._send_macos_notification("Test Title", "Test message")

        self.assertFalse(result)

    @patch('notify.subprocess.run')
    @patch('builtins.print')
    def test_send_linux_notification_success(self, mock_print, mock_run):
        """Test Linux notification success."""
        mock_run.return_value = MagicMock()

        result = notify._send_linux_notification("Test Title", "Test message")

        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ["notify-send", "Test Title", "Test message"],
            check=True,
            capture_output=True,
            timeout=5
        )

    @patch('notify.subprocess.run')
    @patch('builtins.print')
    def test_send_linux_notification_not_found(self, mock_print, mock_run):
        """Test Linux notification when notify-send is not found."""
        mock_run.side_effect = FileNotFoundError()

        result = notify._send_linux_notification("Test Title", "Test message")

        self.assertFalse(result)

    @patch('notify.subprocess.run')
    @patch('builtins.print')
    def test_send_linux_notification_failure(self, mock_print, mock_run):
        """Test Linux notification failure."""
        error = subprocess.CalledProcessError(1, "notify-send")
        error.stderr = b"Error message"
        mock_run.side_effect = error

        result = notify._send_linux_notification("Test Title", "Test message")

        self.assertFalse(result)

    @patch('notify.subprocess.run')
    @patch('builtins.print')
    def test_send_windows_notification_success(self, mock_print, mock_run):
        """Test Windows notification success."""
        mock_run.return_value = MagicMock()

        result = notify._send_windows_notification("Test Title", "Test message")

        self.assertTrue(result)
        mock_run.assert_called_once()
        self.assertIn("powershell", mock_run.call_args[0][0])

    @patch('notify.subprocess.run')
    @patch('builtins.print')
    def test_send_windows_notification_failure(self, mock_print, mock_run):
        """Test Windows notification failure."""
        error = subprocess.CalledProcessError(1, "powershell")
        error.stderr = b"Error message"
        mock_run.side_effect = error

        result = notify._send_windows_notification("Test Title", "Test message")

        self.assertFalse(result)


class TestSoundNotification(unittest.TestCase):
    """Test sound notification functionality."""

    @patch('notify.platform.system')
    @patch('notify._play_macos_sound')
    @patch('builtins.print')
    def test_play_sound_macos(self, mock_print, mock_play_macos, mock_system):
        """Test sound playback on macOS."""
        mock_system.return_value = "Darwin"
        mock_play_macos.return_value = True

        result = notify.play_sound("success")

        self.assertTrue(result)
        mock_play_macos.assert_called_once_with("success")

    @patch('notify.platform.system')
    @patch('notify._play_linux_sound')
    @patch('builtins.print')
    def test_play_sound_linux(self, mock_print, mock_play_linux, mock_system):
        """Test sound playback on Linux."""
        mock_system.return_value = "Linux"
        mock_play_linux.return_value = True

        result = notify.play_sound("error")

        self.assertTrue(result)
        mock_play_linux.assert_called_once_with("error")

    @patch('notify.platform.system')
    @patch('notify._play_windows_sound')
    @patch('builtins.print')
    def test_play_sound_windows(self, mock_print, mock_play_windows, mock_system):
        """Test sound playback on Windows."""
        mock_system.return_value = "Windows"
        mock_play_windows.return_value = True

        result = notify.play_sound("info")

        self.assertTrue(result)
        mock_play_windows.assert_called_once_with("info")

    @patch('notify.platform.system')
    @patch('builtins.print')
    def test_play_sound_unsupported_os(self, mock_print, mock_system):
        """Test sound playback on unsupported OS."""
        mock_system.return_value = "FreeBSD"

        result = notify.play_sound("success")

        self.assertFalse(result)

    @patch('notify.os.path.exists')
    @patch('notify.subprocess.run')
    @patch('builtins.print')
    def test_play_macos_sound_success(self, mock_print, mock_run, mock_exists):
        """Test macOS sound playback success."""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock()

        result = notify._play_macos_sound("success")

        self.assertTrue(result)
        mock_run.assert_called_once()
        self.assertIn("afplay", mock_run.call_args[0][0])

    @patch('notify.os.path.exists')
    @patch('builtins.print')
    def test_play_macos_sound_not_found(self, mock_print, mock_exists):
        """Test macOS sound when file not found."""
        mock_exists.return_value = False

        result = notify._play_macos_sound("success")

        self.assertFalse(result)

    @patch('notify.os.path.exists')
    @patch('notify.subprocess.run')
    @patch('builtins.print')
    def test_play_macos_sound_failure(self, mock_print, mock_run, mock_exists):
        """Test macOS sound playback failure."""
        mock_exists.return_value = True
        mock_run.side_effect = subprocess.CalledProcessError(1, "afplay")

        result = notify._play_macos_sound("success")

        self.assertFalse(result)

    @patch('notify.os.path.exists')
    @patch('notify.subprocess.run')
    @patch('builtins.print')
    def test_play_linux_sound_success(self, mock_print, mock_run, mock_exists):
        """Test Linux sound playback success."""
        # First sound file exists, paplay succeeds
        mock_exists.side_effect = lambda x: "/freedesktop/" in x
        mock_run.return_value = MagicMock()

        result = notify._play_linux_sound("success")

        self.assertTrue(result)

    @patch('notify.os.path.exists')
    @patch('notify.subprocess.run')
    @patch('builtins.print')
    def test_play_linux_sound_no_files(self, mock_print, mock_run, mock_exists):
        """Test Linux sound when no sound files found."""
        mock_exists.return_value = False

        result = notify._play_linux_sound("success")

        self.assertFalse(result)

    @patch('notify.subprocess.run')
    @patch('builtins.print')
    def test_play_windows_sound_success(self, mock_print, mock_run):
        """Test Windows sound playback success."""
        mock_run.return_value = MagicMock()

        result = notify._play_windows_sound("error")

        self.assertTrue(result)
        mock_run.assert_called_once()
        self.assertIn("powershell", mock_run.call_args[0][0])

    @patch('notify.subprocess.run')
    @patch('builtins.print')
    def test_play_windows_sound_failure(self, mock_print, mock_run):
        """Test Windows sound playback failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "powershell")

        result = notify._play_windows_sound("success")

        self.assertFalse(result)


class TestMainFunction(unittest.TestCase):
    """Test main entry point."""

    @patch('sys.argv', ['notify.py'])
    @patch('sys.stderr', new_callable=MagicMock)
    def test_main_no_arguments(self, mock_stderr):
        """Test main with no arguments."""
        with self.assertRaises(SystemExit) as context:
            notify.main()
        self.assertEqual(context.exception.code, 1)

    @patch('sys.argv', ['notify.py', 'invalid_level', 'test'])
    @patch('notify.load_config')
    @patch('sys.stderr', new_callable=MagicMock)
    def test_main_invalid_level(self, mock_stderr, mock_load_config):
        """Test main with invalid level."""
        mock_load_config.return_value = {}

        with self.assertRaises(SystemExit) as context:
            notify.main()
        self.assertEqual(context.exception.code, 1)

    @patch('sys.argv', ['notify.py', 'success', 'Test message'])
    @patch('notify.load_config')
    @patch('notify.send_bark_notification')
    @patch('notify.send_system_notification')
    @patch('notify.play_sound')
    @patch('sys.stderr', new_callable=MagicMock)
    def test_main_success_all_channels(self, mock_stderr, mock_play_sound, mock_system_notify, mock_bark, mock_load_config):
        """Test main with success and all channels enabled."""
        mock_load_config.return_value = {
            "bark_key": "test_key",
            "sound_enabled": True,
            "system_notify_enabled": True
        }
        mock_bark.return_value = True
        mock_system_notify.return_value = True
        mock_play_sound.return_value = True

        notify.main()

        mock_bark.assert_called_once()
        mock_system_notify.assert_called_once()
        mock_play_sound.assert_called_once()

    @patch('sys.argv', ['notify.py', 'error', 'Error message'])
    @patch('notify.load_config')
    @patch('notify.send_bark_notification')
    @patch('notify.send_system_notification')
    @patch('notify.play_sound')
    @patch('sys.stderr', new_callable=MagicMock)
    def test_main_error_level(self, mock_stderr, mock_play_sound, mock_system_notify, mock_bark, mock_load_config):
        """Test main with error level."""
        mock_load_config.return_value = {
            "bark_key": "test_key",
            "sound_enabled": True,
            "system_notify_enabled": True
        }
        mock_bark.return_value = True
        mock_system_notify.return_value = True
        mock_play_sound.return_value = True

        notify.main()

        mock_bark.assert_called_once_with(
            mock_load_config.return_value, "error", "Error message"
        )

    @patch('sys.argv', ['notify.py', 'info', 'Info message'])
    @patch('notify.load_config')
    @patch('notify.send_bark_notification')
    @patch('notify.send_system_notification')
    @patch('notify.play_sound')
    @patch('sys.stderr', new_callable=MagicMock)
    def test_main_info_level(self, mock_stderr, mock_play_sound, mock_system_notify, mock_bark, mock_load_config):
        """Test main with info level."""
        mock_load_config.return_value = {
            "bark_key": "test_key",
            "sound_enabled": True,
            "system_notify_enabled": True
        }
        mock_bark.return_value = True
        mock_system_notify.return_value = True
        mock_play_sound.return_value = True

        notify.main()

        mock_bark.assert_called_once()

    @patch('sys.argv', ['notify.py', 'success', 'Test message'])
    @patch('notify.load_config')
    @patch('notify.send_bark_notification')
    @patch('notify.send_system_notification')
    @patch('notify.play_sound')
    @patch('sys.stderr', new_callable=MagicMock)
    def test_main_sound_disabled(self, mock_stderr, mock_play_sound, mock_system_notify, mock_bark, mock_load_config):
        """Test main with sound disabled."""
        mock_load_config.return_value = {
            "bark_key": "test_key",
            "sound_enabled": False,
            "system_notify_enabled": True
        }
        mock_bark.return_value = True
        mock_system_notify.return_value = True

        notify.main()

        mock_bark.assert_called_once()
        mock_system_notify.assert_called_once()
        mock_play_sound.assert_not_called()

    @patch('sys.argv', ['notify.py', 'success', 'Test message'])
    @patch('notify.load_config')
    @patch('notify.send_bark_notification')
    @patch('notify.send_system_notification')
    @patch('notify.play_sound')
    @patch('sys.stderr', new_callable=MagicMock)
    def test_main_system_notify_disabled(self, mock_stderr, mock_play_sound, mock_system_notify, mock_bark, mock_load_config):
        """Test main with system notification disabled."""
        mock_load_config.return_value = {
            "bark_key": "test_key",
            "sound_enabled": True,
            "system_notify_enabled": False
        }
        mock_bark.return_value = True
        mock_play_sound.return_value = True

        notify.main()

        mock_bark.assert_called_once()
        mock_play_sound.assert_called_once()
        mock_system_notify.assert_not_called()

    @patch('sys.argv', ['notify.py', 'success', 'Test message'])
    @patch('notify.load_config')
    @patch('notify.send_bark_notification')
    @patch('notify.send_system_notification')
    @patch('notify.play_sound')
    @patch('sys.stderr', new_callable=MagicMock)
    def test_main_all_channels_failed(self, mock_stderr, mock_play_sound, mock_system_notify, mock_bark, mock_load_config):
        """Test main when all channels fail."""
        mock_load_config.return_value = {
            "bark_key": "test_key",
            "sound_enabled": True,
            "system_notify_enabled": True
        }
        mock_bark.return_value = False
        mock_system_notify.return_value = False
        mock_play_sound.return_value = False

        notify.main()

        # Should still call all channels even if they fail
        mock_bark.assert_called_once()
        mock_system_notify.assert_called_once()
        mock_play_sound.assert_called_once()


class TestConstants(unittest.TestCase):
    """Test constant definitions."""

    def test_bark_config_has_all_levels(self):
        """Test that BARK_CONFIG has all required levels."""
        required_levels = ["success", "error", "info"]
        for level in required_levels:
            self.assertIn(level, notify.BARK_CONFIG)
            self.assertIn("group", notify.BARK_CONFIG[level])
            self.assertIn("icon", notify.BARK_CONFIG[level])
            self.assertIn("sound", notify.BARK_CONFIG[level])

    def test_sound_map_has_all_levels(self):
        """Test that SOUND_MAP has all required levels."""
        required_levels = ["success", "error", "info"]
        for level in required_levels:
            self.assertIn(level, notify.SOUND_MAP)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
