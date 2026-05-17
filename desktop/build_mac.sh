#!/bin/bash
echo "Building BLE Spam for macOS..."
pip3 install -r requirements.txt
pyinstaller --onefile --name BLESpam --console ble_spam.py --add-data "payloads.py:."
echo "Done! Output: dist/BLESpam"
