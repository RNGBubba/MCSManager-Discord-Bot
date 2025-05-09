@echo off
setlocal enabledelayedexpansion

echo ===================================
echo Unofficial MCSManager Discord Bot
echo Made by Mr Bubba
echo Discord ID: 1130162662907580456
echo ===================================
echo.

REM Define required Python version
set RECOMMENDED_PYTHON_VERSION=3.11.8
set MINIMUM_PYTHON_VERSION=3.11.0
set PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed on this system.
    echo This bot requires Python 3.13 or higher.
    echo.
    
    set /p install_python="Would you like to install Python %RECOMMENDED_PYTHON_VERSION% now? (Y/N): "
    if /i "!install_python!"=="Y" (
        echo.
        echo Downloading Python %RECOMMENDED_PYTHON_VERSION% installer...
        
        REM Create a temporary directory for the download
        mkdir temp 2>nul
        
        REM Download Python installer
        powershell -Command "& {Invoke-WebRequest -Uri '%PYTHON_INSTALLER_URL%' -OutFile 'temp\python_installer.exe'}"
        
        echo.
        echo Installing Python %RECOMMENDED_PYTHON_VERSION%...
        echo This may take a few minutes. Please wait...
        
        REM Run the installer with recommended settings (including PATH)
        temp\python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
        
        REM Clean up
        del /Q temp\python_installer.exe
        rmdir temp
        
        echo.
        echo Python %RECOMMENDED_PYTHON_VERSION% installation completed.
        echo Please restart this script to continue.
        pause
        exit
    ) else (
        echo.
        echo Python installation skipped. Python %RECOMMENDED_PYTHON_VERSION% is required to run the Discord bot.
        echo Please install Python manually and run this script again.
        pause
        exit
    )
)

echo Python is installed. Checking version...
echo Python found, checking version >> debug_log.txt

set PYTHON_VERSION_OK=0
for /f "tokens=2" %%V in ('!PYTHON_CMD! --version 2^>^&1') do (
    set PYTHON_VERSION=%%V
    echo Detected Python version: !PYTHON_VERSION!
    echo Detected Python version: !PYTHON_VERSION! >> debug_log.txt
    
    for /f "tokens=1,2,3 delims=." %%a in ("!PYTHON_VERSION!") do (
        set PY_MAJOR=%%a
        set PY_MINOR=%%b
        set PY_PATCH=%%c
        echo Python version components: Major=!PY_MAJOR!, Minor=!PY_MINOR!, Patch=!PY_PATCH! >> debug_log.txt
    )
    
    if !PY_MAJOR! EQU 3 (
        if !PY_MINOR! GEQ 11 (
            if !PY_MINOR! LSS 13 (
                set PYTHON_VERSION_OK=1
                echo Python version is compatible >> debug_log.txt
            )
        )
    )
)

if %PYTHON_VERSION_OK%==0 (
    echo.
    echo WARNING: You are not using Python 3.11 - 3.12.
    echo This bot requires Python 3.11 - 3.12.
    echo.
    set /p install_correct_version="Would you like to install Python %RECOMMENDED_PYTHON_VERSION% now? (Y/N): "
    if /i "!install_correct_version!"=="Y" (
        echo.
        echo Downloading Python %RECOMMENDED_PYTHON_VERSION% installer...
        
        REM Create a temporary directory for the download
        mkdir temp 2>nul
        
        REM Download Python installer
        powershell -Command "& {Invoke-WebRequest -Uri '%PYTHON_INSTALLER_URL%' -OutFile 'temp\python_installer.exe'}"
        
        echo.
        echo Installing Python %RECOMMENDED_PYTHON_VERSION%...
        echo This may take a few minutes. Please wait...
        
        REM Run the installer with recommended settings (including PATH)
        temp\python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
        
        REM Clean up
        del /Q temp\python_installer.exe
        rmdir temp
        
        echo.
        echo Python %RECOMMENDED_PYTHON_VERSION% installation completed.
        echo Please restart this script to continue.
        pause
        exit
    ) else (
        echo.
        echo Python 3.13 or higher is required to run the Discord bot.
        echo Please install a compatible Python version manually and run this script again.
        pause
        exit
    )
) else (
    echo Python version check passed. You have Python 3.13 or higher installed.
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
