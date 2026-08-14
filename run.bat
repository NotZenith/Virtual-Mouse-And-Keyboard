@echo off
setlocal enabledelayedexpansion

REM Try direct path first to bypass alias
if exist "C:\Users\notze\.local\bin\python3.14.exe" (
    echo Running with C:\Users\notze\.local\bin\python3.14.exe
    "C:\Users\notze\.local\bin\python3.14.exe" "%~dp0main.py"
    exit /b %ERRORLEVEL%
)

REM Check if python3.14 is in PATH
where python3.14 > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Running with python3.14
    python3.14 "%~dp0main.py"
    exit /b %ERRORLEVEL%
)

REM Try python3
where python3 > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Running with python3
    python3 "%~dp0main.py"
    exit /b %ERRORLEVEL%
)

REM Try python (with alias disabled)
where python > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Running with python
    python "%~dp0main.py"
    exit /b %ERRORLEVEL%
)

echo Python not found! Please install Python or check your environment.
pause
