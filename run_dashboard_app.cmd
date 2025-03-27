@echo off
:: WhatsApp Automation Launcher
:: Searches for and runs the Streamlit dashboard

setlocal enabledelayedexpansion

:: Configure these variables
set APP_NAME=app_dashboard_client_credits_manager.py
set START_DIR=%CD%
set FOUND=0

title Client Credits Manager Launcher
color 07

echo #############################################
echo #  Client Credits Manager Auto-Launcher   #
echo #############################################
echo.

:: Search function
echo Searching for %APP_NAME% in %START_DIR% and subfolders...
echo.

for /r "%START_DIR%" %%f in (*%APP_NAME%) do (
    if "%%f" neq "" (
        set APP_PATH=%%f
        set FOUND=1
        echo Found application at: %%f
        goto :runapp
    )
)

:runapp
if %FOUND% equ 1 (
    echo.
    echo Starting Client Credits Manager...
    echo.
    
    :: Change to the app directory
    pushd "%~dp0"
    cd /d "!APP_PATH:\%APP_NAME%=!"
    
    :: Run Streamlit
    start "" /B cmd /c "streamlit run "!APP_PATH!" && pause"
    
    popd
) else (
    echo.
    echo Error: Could not find %APP_NAME%
    echo Searched in: %START_DIR% and subfolders
)

echo.
pause