@echo off
REM Build a standalone Windows executable of the Skyrim INI Editor.
REM Requires Python 3.8+ and Nuitka installed in the current Python environment.

set PYTHON="C:\Program Files\Python313\python.exe"
if not exist %PYTHON% (
  echo Python not found at %PYTHON%. Update the path to the Python executable you want to use.
  exit /b 1
)

%PYTHON% -m nuitka --standalone --onefile --windows-console-mode=disable --assume-yes-for-downloads --enable-plugin=tk-inter --output-dir=dist skyrim_ini_editor.py
if errorlevel 1 (
  echo Build failed.
  exit /b %errorlevel%
)
echo Build finished. The executable is available in dist\skyrim_ini_editor.exe
