#!/usr/bin/env python3
"""
Universal runner for task-notifier scripts
Ensures consistent invocation pattern (even with zero dependencies)
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Main runner for task-notifier scripts"""
    if len(sys.argv) < 2:
        print("Usage: python run.py <script_name> [args...]")
        print("\nAvailable scripts:")
        print("  notify.py - Send notification (success/error/info)")
        sys.exit(1)

    script_name = sys.argv[1]
    script_args = sys.argv[2:]

    # Handle both "scripts/script.py" and "script.py" formats
    if script_name.startswith('scripts/'):
        script_name = script_name[8:]  # Remove 'scripts/' prefix

    # Ensure .py extension
    if not script_name.endswith('.py'):
        script_name += '.py'

    # Get script path (scripts/ is relative to this run.py file)
    script_path = Path(__file__).parent / script_name

    if not script_path.exists():
        print(f"❌ Script not found: {script_name}")
        print(f"   Skill directory: {Path(__file__).parent.parent}")
        print(f"   Looked for: {script_path}")
        sys.exit(1)

    # Execute the script (no venv needed - zero dependency design)
    cmd = [sys.executable, str(script_path)] + script_args

    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
