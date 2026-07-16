@echo off
cd /d "%~dp0\.."
call .venv\Scripts\activate
pip install pyinstaller
pyinstaller --noconfirm --clean --windowed ^
  --name "KAP Studio" ^
  --add-data "data;data" ^
  src\kap_studio\main.py
echo EXE: dist\KAP Studio\KAP Studio.exe
pause
