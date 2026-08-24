"""
Create Windows 11 Desktop Shortcuts for AI Attendance System
"""

import os
import sys

def create_shortcuts():
    try:
        import win32com.client
    except ImportError:
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "pywin32"], check=False)
        import win32com.client

    base_dir = os.path.dirname(os.path.abspath(__file__))
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")

    shell = win32com.client.Dispatch("WScript.Shell")

    # 1. Desktop Shortcut for Control Panel (XAMPP style)
    cp_shortcut_path = os.path.join(desktop, "📸 AI Attendance Control Panel.lnk")
    cp_target = os.path.join(base_dir, "OPEN_CONTROL_PANEL.bat")
    cp_shortcut = shell.CreateShortCut(cp_shortcut_path)
    cp_shortcut.TargetPath = cp_target
    cp_shortcut.WorkingDirectory = base_dir
    cp_shortcut.Description = "Open AI Attendance System Desktop Control Panel"
    cp_shortcut.save()
    print(f"[OK] Created Desktop Shortcut: {cp_shortcut_path}")

    # 2. Desktop Shortcut for 1-Click App Launcher
    app_shortcut_path = os.path.join(desktop, "🚀 Start AI Attendance System.lnk")
    app_target = os.path.join(base_dir, "START_ATTENDANCE_APP.bat")
    app_shortcut = shell.CreateShortCut(app_shortcut_path)
    app_shortcut.TargetPath = app_target
    app_shortcut.WorkingDirectory = base_dir
    app_shortcut.Description = "1-Click Start AI Attendance Web Portal"
    app_shortcut.save()
    print(f"[OK] Created Desktop Shortcut: {app_shortcut_path}")

if __name__ == "__main__":
    create_shortcuts()
