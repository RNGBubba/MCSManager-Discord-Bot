@echo off
setlocal enabledelayedexpansion
title UnOffical MCSManager Discord Bot - by Mr Bubba (Discord ID: 1130162662907580456)
cd /d "%~dp0"
chcp 437 > nul

:: Set color scheme
color 0B

echo ######################################################
echo #          UnOfficial MCSManager Discord Bot         #
echo ######################################################
echo.
echo ######################################################
echo #               Developed by Mr Bubba                #
echo #                                                    #
echo # Discord Username : Mr Bubba                        #
echo # Discord Tag      : exbubba                         #
echo # Discord ID       : 1130162662907580456             #
echo #                                                    #
echo #      Please respect the developer's work!           #
echo ######################################################

set REQUIRED_PYTHON_VERSION=3.12.10
set PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe

echo Checking for Python 3.12.10...
py -3.12 --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%V in ('py -3.12 --version 2^>^&1') do (
        set PYTHON_VERSION=%%V
        echo Detected Python version: !PYTHON_VERSION!
        
        REM Check if it's exactly 3.12.10
        if "!PYTHON_VERSION!"=="3.12.10" (
            echo Found Python 3.12.10. Using this version.
            set PYTHON_CMD=py -3.12
            goto :python_found
        )
    )
)

python3.12 --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%V in ('python3.12 --version 2^>^&1') do (
        set PYTHON_VERSION=%%V
        echo Detected Python version: !PYTHON_VERSION!
        
        REM Check if it's exactly 3.12.10
        if "!PYTHON_VERSION!"=="3.12.10" (
            echo Found Python 3.12.10. Using this version.
            set PYTHON_CMD=python3.12
            goto :python_found
        )
    )
)

python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%V in ('python --version 2^>^&1') do (
        set PYTHON_VERSION=%%V
        echo Detected Python version: !PYTHON_VERSION!
        
        REM Check if it's exactly 3.12.10
        if "!PYTHON_VERSION!"=="3.12.10" (
            echo Found Python 3.12.10. Using this version.
            set PYTHON_CMD=python
            goto :python_found
        ) else (
            echo Python is installed but not version 3.12.10 (found !PYTHON_VERSION!).
        )
    )
) else (
    echo Python is not installed on this system.
)

echo This bot requires Python 3.12.10 specifically.
echo.

set /p install_python="Would you like to install Python %REQUIRED_PYTHON_VERSION% now? (Y/N): "
if /i "!install_python!"=="Y" (
    echo.
    echo Downloading Python %REQUIRED_PYTHON_VERSION% installer...
    
    REM Create a temporary directory for the download
    mkdir temp 2>nul
    
    REM Download Python installer
    powershell -Command "& {Invoke-WebRequest -Uri '%PYTHON_INSTALLER_URL%' -OutFile 'temp\python_installer.exe'}"
    if %errorlevel% neq 0 (
        echo Failed to download Python installer. Please check your internet connection.
        pause
        exit /b 1
    )
    
    echo.
    echo Installing Python %REQUIRED_PYTHON_VERSION%...
    echo This may take a few minutes. Please wait...
    
    REM Run the installer with recommended settings (including PATH)
    temp\python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    
    REM Clean up
    del /Q temp\python_installer.exe
    rmdir temp
    
    echo.
    echo Python %REQUIRED_PYTHON_VERSION% installation completed.
    echo Please restart this script to continue.
    pause
    exit /b 0
) else (
    echo.
    echo Python installation skipped. Python %REQUIRED_PYTHON_VERSION% is required to run the Discord bot.
    echo Please install Python %REQUIRED_PYTHON_VERSION% manually and run this script again.
    pause
    exit /b 1
)

echo Python 3.12.10 found and will be used to run the bot.
echo.

echo Checking for pip installation...
!PYTHON_CMD! -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Pip is not available for Python 3.12.10. Attempting to install pip...
    !PYTHON_CMD! -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo Failed to install pip. Trying alternative method...
        
        REM Create a temporary directory for the get-pip script
        mkdir temp 2>nul
        
        REM Download get-pip.py
        echo Downloading pip installer...
        powershell -Command "& {Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'temp\get-pip.py'}"
        
        REM Run get-pip.py
        echo Installing pip...
        !PYTHON_CMD! temp\get-pip.py
        
        REM Clean up
        del /Q temp\get-pip.py
        rmdir temp
        
        REM Check if pip installation was successful
        !PYTHON_CMD! -m pip --version >nul 2>&1
        if %errorlevel% neq 0 (
            echo Failed to install pip. Please install pip manually.
            pause
            exit
        ) else (
            echo Pip installed successfully.
        )
    ) else (
        echo Pip installed successfully.
    )
) else (
    echo Pip is already installed.
)

echo Checking requirements...

if not exist "%~dp0requirements.txt" (
    echo.
    echo WARNING: requirements.txt file not found!
    echo This script needs a requirements.txt file to install dependencies.
    echo.
    set /p create_req="Would you like to create a basic requirements.txt file? (Y/N): "
    if /i "!create_req!"=="Y" (
        echo Creating basic requirements.txt file...
        echo discord.py==2.4.0 > "%~dp0requirements.txt"
        echo python-dotenv >> "%~dp0requirements.txt"
        echo requests >> "%~dp0requirements.txt"
        echo psutil >> "%~dp0requirements.txt"
        echo asyncio >> "%~dp0requirements.txt"
        echo aiohttp >> "%~dp0requirements.txt"
        echo pillow >> "%~dp0requirements.txt"
        echo pytz >> "%~dp0requirements.txt"
        echo youtube-dl >> "%~dp0requirements.txt"
        echo PyNaCl >> "%~dp0requirements.txt"
        echo pycparser >> "%~dp0requirements.txt"
        echo cffi >> "%~dp0requirements.txt"
        echo.
        echo Basic requirements.txt file created. You may need to edit it later.
    ) else (
        echo.
        echo Cannot continue without requirements.txt file.
        pause
        exit
    )
) else (
    echo requirements.txt found.
)

echo Checking if pip is up to date...
!PYTHON_CMD! -m pip install --upgrade pip >nul 2>&1

echo Checking requirements...
echo Comparing installed packages with requirements.txt...

REM Create temporary files to store package information
if exist temp_req.txt del /q temp_req.txt
if exist temp_installed.txt del /q temp_installed.txt
if exist temp_missing.txt del /q temp_missing.txt

REM Extract package names from requirements.txt (strip version info)
for /f "tokens=1 delims=<>=~!" %%a in (requirements.txt) do (
    echo %%a >> temp_req.txt
)

REM Get list of installed packages
!PYTHON_CMD! -m pip list > pip_list_full.txt
for /f "skip=2 tokens=1" %%a in (pip_list_full.txt) do (
    echo %%a >> temp_installed.txt
)

REM Find missing packages
set missing_packages=0
set missing_list=
for /f "tokens=*" %%a in (temp_req.txt) do (
    set package_name=%%a
    REM Remove any whitespace
    set package_name=!package_name: =!
    if not "!package_name!"=="" (
        findstr /i /c:"!package_name!" temp_installed.txt >nul
        if !errorlevel! neq 0 (
            echo !package_name! >> temp_missing.txt
            set /a missing_packages+=1
            set missing_list=!missing_list! !package_name!
        )
    )
)

REM Check if any packages are missing
if !missing_packages! gtr 0 (
    echo.
    echo Found !missing_packages! missing packages: !missing_list!
    
    set /p install_req="Would you like to install missing requirements now? (Y/N): "
    if /i "!install_req!"=="Y" (
        echo.
        echo Installing missing requirements...
        
        !PYTHON_CMD! -m pip install -r requirements.txt
        if !errorlevel! neq 0 (
            echo.
            echo Failed to install requirements. Please check your internet connection and try again.
            pause
            exit
        )
        
        echo.
        echo Requirements installed successfully.
    ) else (
        echo.
        echo Requirements installation skipped. The bot may not work correctly if dependencies are missing.
        echo.
    )
) else (
    echo All required packages are already installed.
)

REM Clean up temporary files
del /q temp_req.txt temp_installed.txt temp_missing.txt pip_list_full.txt 2>nul

if not exist "%~dp0.env" (
    echo.
    echo No .env file found. This file is needed for bot configuration.
    set /p create_env="Would you like to create and configure the .env file now? (Y/N): "
    if /i "!create_env!"=="Y" (
        echo.
        echo === Bot Configuration Setup ===
        echo.
        echo Please enter the required information:
        echo.
        
        set "discord_token="
        set /p discord_token="Enter your Discord Bot Token: "
        
        set "mcs_address="
        set /p mcs_address="Enter your MCSManager Address (URL): "
        
        set "mcs_api_key="
        set /p mcs_api_key="Enter your MCSManager API Key: "
        
        echo.
        echo Creating .env file with your configuration...
        
        echo DISCORD_BOT_TOKEN="!discord_token!" #Bot Token > "%~dp0.env"
        echo MCSMANAGER_ADDRESS="!mcs_address!" #URL to connect to your MCS Manager >> "%~dp0.env"
        echo MCSMANAGER_API_KEY="!mcs_api_key!" #Your MCS Manager API Key >> "%~dp0.env"
        echo EPHEMERAL_MESSAGE=true >> "%~dp0.env"
        echo OUT_PUT_SIZE="1000" >> "%~dp0.env"
        echo PAGE_SIZE="20" >> "%~dp0.env"
        echo PAGE="1" >> "%~dp0.env"
        echo. >> "%~dp0.env"
        echo.

        echo .env file created successfully with your configuration!
        echo.
        
        set /p review_file="Would you like to review the .env file in Notepad? (Y/N): "
        if /i "!review_file!"=="Y" (
            notepad "%~dp0.env"
        )
    ) else (
        echo.
        echo WARNING: The bot requires a properly configured .env file to function.
        echo You will need to create this file manually before the bot can run correctly.
        echo.
    )
) else (
    echo .env file found.
)

echo.
echo ######################################################
echo #         Ready to start the Discord Bot             #
echo ######################################################
echo.
echo Press Ctrl+C to stop the bot when it's running.
echo.
echo Starting bot in 3 seconds...
timeout /t 3 >nul
echo ######################################################
echo #          UnOfficial MCSManager Discord Bot         #
echo ######################################################
echo.
echo ######################################################
echo #               Developed by Mr Bubba                #
echo #                                                    #
echo # Discord Username : Mr Bubba                        #
echo # Discord Tag      : exbubba                         #
echo # Discord ID       : 1130162662907580456             #
echo #                                                    #
echo #      Please respect the developer's work!           #
echo ######################################################
echo.
echo ######################################################
echo #              Bot is now starting...                #
echo ######################################################
echo.
cd /d "%~dp0"
!PYTHON_CMD! __init__.py
set bot_exit_code=%errorlevel%
echo.
echo ######################################################
if %bot_exit_code% neq 0 (
echo #           Bot exited with error code: %bot_exit_code%            #
echo #     Check the error messages above for details.    #
) else (
    echo #                Bot has stopped.                    #
)
echo ######################################################

echo.
echo Press any key to exit...
pause
