@echo off
echo Building BLE Spam for Windows...
pip install -r requirements.txt
pyinstaller --onefile --name BLESpam --console --add-data "payloads.py;." --hidden-import payloads ble_spam.py
echo Done! Output: dist\BLESpam.exe
pause
