#!/usr/bin/env python3
"""Tests for scripts/run.py — the universal runner."""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import run


class TestRunMain(unittest.TestCase):
    """Test the run.py main entry point."""

    @patch("sys.argv", ["run.py"])
    def test_no_arguments_exits(self):
        """Test that no arguments prints usage and exits."""
        with self.assertRaises(SystemExit) as ctx:
            run.main()
        self.assertEqual(ctx.exception.code, 1)

    @patch("sys.argv", ["run.py", "nonexistent_script"])
    def test_script_not_found_exits(self):
        """Test exit when script does not exist."""
        with self.assertRaises(SystemExit) as ctx:
            run.main()
        self.assertEqual(ctx.exception.code, 1)

    @patch("sys.argv", ["run.py", "scripts/notify.py", "success", "test"])
    @patch("run.subprocess.run")
    def test_strips_scripts_prefix(self, mock_run):
        """Test that 'scripts/' prefix is stripped from script name."""
        mock_run.return_value = MagicMock(returncode=0)
        with self.assertRaises(SystemExit) as ctx:
            run.main()
        self.assertEqual(ctx.exception.code, 0)
        call_args = mock_run.call_args[0][0]
        # Should resolve to scripts/notify.py (not scripts/scripts/notify.py)
        self.assertIn("notify.py", call_args[1])

    @patch("sys.argv", ["run.py", "notify", "success", "test"])
    @patch("run.subprocess.run")
    def test_adds_py_extension(self, mock_run):
        """Test that .py extension is added when missing."""
        mock_run.return_value = MagicMock(returncode=0)
        with self.assertRaises(SystemExit) as ctx:
            run.main()
        self.assertEqual(ctx.exception.code, 0)
        call_args = mock_run.call_args[0][0]
        self.assertTrue(call_args[1].endswith("notify.py"))

    @patch("sys.argv", ["run.py", "notify.py", "success", "msg"])
    @patch("run.subprocess.run")
    def test_success_returns_zero(self, mock_run):
        """Test successful execution returns zero."""
        mock_run.return_value = MagicMock(returncode=0)
        with self.assertRaises(SystemExit) as ctx:
            run.main()
        self.assertEqual(ctx.exception.code, 0)

    @patch("sys.argv", ["run.py", "notify.py", "success", "msg"])
    @patch("run.subprocess.run")
    def test_nonzero_returncode_forwarded(self, mock_run):
        """Test that non-zero return code is forwarded."""
        mock_run.return_value = MagicMock(returncode=42)
        with self.assertRaises(SystemExit) as ctx:
            run.main()
        self.assertEqual(ctx.exception.code, 42)

    @patch("sys.argv", ["run.py", "notify.py", "success", "msg"])
    @patch("run.subprocess.run", side_effect=KeyboardInterrupt)
    def test_keyboard_interrupt(self, mock_run):
        """Test keyboard interrupt handling."""
        with self.assertRaises(SystemExit) as ctx:
            run.main()
        self.assertEqual(ctx.exception.code, 130)

    @patch("sys.argv", ["run.py", "notify.py", "success", "msg"])
    @patch("run.subprocess.run", side_effect=OSError("spawn failed"))
    def test_generic_exception(self, mock_run):
        """Test generic exception handling."""
        with self.assertRaises(SystemExit) as ctx:
            run.main()
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
