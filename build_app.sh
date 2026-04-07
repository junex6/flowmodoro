#!/bin/bash
# build_app.sh

set -e

PYTHON=$(which python)
APP_DIR="dist/Flowmodoro.app"
MACOS_DIR="${APP_DIR}/Contents/MacOS"
RES_DIR="${APP_DIR}/Contents/Resources"

echo "Building Flowmodoro.app..."

rm -rf dist
mkdir -p "${MACOS_DIR}" "${RES_DIR}"

# Generate the wave emoji icon
echo "Generating app icon..."
"${PYTHON}" make_icon.py
cp Flowmodoro.icns "${RES_DIR}/Flowmodoro.icns"

cp flowmodoro.py "${RES_DIR}/flowmodoro.py"

cat > "${MACOS_DIR}/Flowmodoro" << PYEOF
#!${PYTHON}
import os, sys, traceback

LOG = "/tmp/flowmodoro.log"

try:
    resources = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Resources')
    sys.path.insert(0, os.path.realpath(resources))
    import flowmodoro
    flowmodoro.FlowmodoroApp().run()
except Exception:
    with open(LOG, "w") as f:
        traceback.print_exc(file=f)
    raise
PYEOF

chmod +x "${MACOS_DIR}/Flowmodoro"

cat > "${APP_DIR}/Contents/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key>
  <string>Flowmodoro</string>
  <key>CFBundleDisplayName</key>
  <string>Flowmodoro</string>
  <key>CFBundleIdentifier</key>
  <string>com.local.flowmodoro</string>
  <key>CFBundleVersion</key>
  <string>1.0.0</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0.0</string>
  <key>CFBundleExecutable</key>
  <string>Flowmodoro</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleIconFile</key>
  <string>Flowmodoro</string>
  <key>LSUIElement</key>
  <true/>
  <key>NSUserNotificationAlertStyle</key>
  <string>alert</string>
  <key>NSHighResolutionCapable</key>
  <true/>
</dict>
</plist>
PLIST

# Patch conda Python's Info.plist for rumps.notification()
CONDA_PLIST="$(dirname ${PYTHON})/Info.plist"
if [ ! -f "${CONDA_PLIST}" ]; then
  /usr/libexec/PlistBuddy -c 'Add :CFBundleIdentifier string "com.local.flowmodoro"' "${CONDA_PLIST}"
  /usr/libexec/PlistBuddy -c 'Add :CFBundleName string "Flowmodoro"' "${CONDA_PLIST}"
  /usr/libexec/PlistBuddy -c 'Add :NSUserNotificationAlertStyle string "alert"' "${CONDA_PLIST}"
  echo "Patched conda Python plist."
else
  echo "Conda plist already exists, skipping."
fi

echo ""
echo "Done. Run:"
echo "  pkill -f flowmodoro.py 2>/dev/null; cp -r dist/Flowmodoro.app /Applications/ && xattr -cr /Applications/Flowmodoro.app && open /Applications/Flowmodoro.app"
