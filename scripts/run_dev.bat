@echo off
cd /d "%~dp0\.."
call .venv\Scripts\activate
python -m kap_studio.main
