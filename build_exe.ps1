# Build a standalone Windows executable of the Skyrim INI Editor.
# Requires Python 3.8+ and Nuitka installed in the current Python environment.
# This script uses Nuitka's onefile mode and downloads Dependency Walker automatically.

$python = "C:/Program Files/Python313/python.exe"
if (-not (Test-Path $python)) {
    Write-Host "Python not found at $python. Update the path to the Python executable you want to use." -ForegroundColor Yellow
    exit 1
}

& $python -m nuitka --standalone --onefile --windows-console-mode=disable --assume-yes-for-downloads --enable-plugin=tk-inter --output-dir=dist skyrim_ini_editor.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed (exit code $LASTEXITCODE)." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "Build finished. The executable is available in dist\skyrim_ini_editor.exe" -ForegroundColor Green
