@echo off
cd /d "%~dp0"
set PYTHONUTF8=1
where py >nul 2>nul
if not errorlevel 1 (
  py -3 launcher.py
) else (
  python launcher.py
)
if errorlevel 1 (
  echo If Python is missing, install Python 3.12-3.14 from https://www.python.org/downloads/windows/
  echo Enable the Python launcher during installation, then run this file again.
  pause
)
