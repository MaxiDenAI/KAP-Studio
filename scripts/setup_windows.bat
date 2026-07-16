@echo off
cd /d "%~dp0\.."
py -3.11 -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e .
echo Setup complete.
pause
