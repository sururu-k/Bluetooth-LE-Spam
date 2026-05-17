#!/bin/bash
set -e
echo "Building BLE Spam for macOS..."
pip3 install -r requirements.txt
pyinstaller --onefile \
    --name BLESpam \
    --console \
    --add-data "payloads.py:." \
    --hidden-import payloads \
    ble_spam.py
echo "Done! Output: dist/BLESpam"
