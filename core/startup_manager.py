"""
Startup Manager Module
Handles Windows startup registration and desktop shortcut creation.
"""

import os
import sys
import winreg


APP_NAME = "BatteryAlarm"


def _exe_path() -> str:
    """Get the path to the current executable or script."""
    if getattr(sys, "frozen", False):
        return sys.executable
    else:
        return os.path.abspath(sys.argv[0])


# ---------------------------------------------------------------------------
# Windows Startup (Registry)
# ---------------------------------------------------------------------------

_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def is_startup_enabled() -> bool:
    """Check if the app is registered to run on Windows startup."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY, 0,
                            winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except FileNotFoundError:
        return False
    except OSError:
        return False


def enable_startup():
    """Register the app to run on Windows startup."""
    exe = _exe_path()
    if getattr(sys, "frozen", False):
        cmd = f'"{exe}"'
    else:
        cmd = f'"{sys.executable}" "{exe}"'
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY, 0,
                            winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
    except OSError:
        pass


def disable_startup():
    """Remove the app from Windows startup."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY, 0,
                            winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
    except FileNotFoundError:
        pass
    except OSError:
        pass


def set_startup(enabled: bool):
    """Enable or disable startup."""
    if enabled:
        enable_startup()
    else:
        disable_startup()


# ---------------------------------------------------------------------------
# Desktop Shortcut
# ---------------------------------------------------------------------------

def create_desktop_shortcut():
    """Create a .lnk shortcut on the user's Desktop."""
    try:
        import ctypes.wintypes
        # Use Windows COM to create a proper .lnk
        import subprocess

        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop, f"{APP_NAME}.lnk")

        if os.path.exists(shortcut_path):
            return shortcut_path  # Already exists

        exe = _exe_path()
        if getattr(sys, "frozen", False):
            target = exe
            arguments = ""
        else:
            target = sys.executable
            arguments = f'"{exe}"'

        icon = exe if getattr(sys, "frozen", False) else ""
        work_dir = os.path.dirname(exe)

        # Use PowerShell to create the shortcut (avoids pywin32 dependency)
        ps_script = f"""
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut('{shortcut_path}')
$sc.TargetPath = '{target}'
$sc.Arguments = '{arguments}'
$sc.WorkingDirectory = '{work_dir}'
$sc.Description = 'Battery Alarm - Charge smart. Battery lasts longer.'
$sc.Save()
"""
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True, timeout=10,
        )
        return shortcut_path if os.path.exists(shortcut_path) else None

    except Exception:
        return None
