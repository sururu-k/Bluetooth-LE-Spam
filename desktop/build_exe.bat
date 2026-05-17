@echo off
echo Building BLE Spam for Windows...
pip install -r requirements.txt
pyinstaller --onefile --name BLESpam --console ble_spam.py --add-data "payloads.py;."
echo Done! Output: dist\BLESpam.exe
pause
