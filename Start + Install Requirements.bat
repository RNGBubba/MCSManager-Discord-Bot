@echo off
setlocal enabledelayedexpansion

echo ===================================
echo Unofficial MCSManager Discord Bot - All-In-One
echo Made by Mr Bubba
echo Discord ID: 1130162662907580456
echo ===================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed on this system.
    echo.
    
    set /p install_python="Would you like to install Python now? (Y/N): "
    if /i "!install_python!"=="Y" (
        echo.
        echo Downloading Python installer...
        
        REM Create a temporary directory for the download
        mkdir temp 2>nul
        
        REM Download Python installer (latest version)
        powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe' -OutFile 'temp\python_installer.exe'}"
        
        echo.
        echo Installing Python...
        echo This may take a few minutes. Please wait...
        
        REM Run the installer with recommended settings (including PATH)
        temp\python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
        
        REM Clean up
        del /Q temp\python_installer.exe
        rmdir temp
        
        echo.
        echo Python installation completed.
        echo Please restart this script to continue.
        pause
        exit
    ) else (
        echo.
        echo Python installation skipped. Python is required to run the Discord bot.
        echo Please install Python manually and run this script again.
        pause
        exit
    )
)

echo Python is installed. Checking version...
for /f "tokens=2" %%V in ('python --version 2^>^&1') do (
    echo Detected Python version: %%V
)
echo.

REM Check if pip is installed
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Pip is not available. Attempting to install pip...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo Failed to install pip. Please install pip manually.
        pause
        exit
    )
)

echo Checking requirements...

REM Check if requirements are already installed
set requirements_needed=0
for /f "tokens=1" %%p in (requirements.txt) do (
    set package=%%p
    set package=!package:==!
    python -c "import importlib.util; print('1' if importlib.util.find_spec('!package!') is None else '0')" > temp.txt
    set /p check_result=<temp.txt
    del temp.txt
    
    if !check_result!==1 (
        set requirements_needed=1
        goto install_req
    )
)

:install_req
if %requirements_needed%==1 (
    echo Some requirements are missing. Installing requirements...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install requirements. Please check your internet connection and try again.
        pause
        exit
    )
    echo Requirements installed successfully.
) else (
    echo All requirements are already installed.
)

echo.
echo ===================================
echo Starting Discord Bot...
echo ===================================
echo.
echo Press Ctrl+C to stop the bot.
echo.

python __init__.py

pause