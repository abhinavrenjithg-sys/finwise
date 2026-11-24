@echo off
REM ============================================================
REM  FinWise - Smart Financial Calculator : one-click start
REM  Double-click this file. First run installs everything.
REM ============================================================
setlocal
title FinWise - Smart Financial Calculator
cd /d "%~dp0"

set "PY="

REM 1) Python launcher "py" (installed with python.org Python)
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>nul
if %errorlevel%==0 set "PY=py -3"
if defined PY goto run

REM 2) "python" on PATH (skips the Microsoft Store placeholder)
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>nul
if %errorlevel%==0 set "PY=python"
if defined PY goto run

REM 3) Python installed earlier by this script (per-user location)
for %%V in (313 312 311 310) do (
    if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" set PY="%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
)
if defined PY goto run

REM 4) No Python found: install it automatically with winget
echo.
echo  Python 3.9+ was not found on this computer.
where winget >nul 2>nul
if not %errorlevel%==0 goto nopython
echo  Installing Python 3.12 automatically (about 1-2 minutes)...
echo.
winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set PY="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if defined PY goto run

:nopython
echo.
echo  Please install Python from https://www.python.org/downloads/
echo  IMPORTANT: tick "Add python.exe to PATH" during installation.
echo  Then double-click run.bat again.
start "" https://www.python.org/downloads/
pause
exit /b 1

:run
%PY% launcher.py
if not %errorlevel%==0 pause
endlocal
