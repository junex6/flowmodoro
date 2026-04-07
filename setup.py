"""
py2app setup — packages flowmodoro.py into a standalone macOS .app bundle.

Usage:
  python setup.py py2app
"""

from setuptools import setup

APP       = ["flowmodoro.py"]
DATA_FILES = []

OPTIONS = {
    "argv_emulation": False,          # required False for menu bar apps
    "plist": {
        "LSUIElement": True,          # hides the Dock icon — menu bar only
        "CFBundleName": "Flowmodoro",
        "CFBundleDisplayName": "Flowmodoro",
        "CFBundleIdentifier": "com.local.flowmodoro",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "NSHumanReadableCopyright": "MIT",
        # Allow macOS notifications
        "NSUserNotificationAlertStyle": "alert",
    },
    "packages": ["rumps"],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)