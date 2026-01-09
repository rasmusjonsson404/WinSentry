@echo off

:: =========================================================
::  AUTO-ELEVATION (Force Admin Privileges)
:: =========================================================
net session >nul 2>&1
if %errorlevel% equ 0 goto :START

echo Requesting Administrator privileges...
if "%~1"=="" (
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
) else (
    powershell -Command "Start-Process '%~dpnx0' -ArgumentList '%*' -Verb RunAs"
)
exit

:START
:: =========================================================
::  MAIN SCRIPT
:: =========================================================
cd /d "%~dp0"
SETLOCAL EnableDelayedExpansion

for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
  set "ESC=%%b"
)

if exist .venv\Scripts\activate.bat (
    call ".venv\Scripts\activate.bat"
) else (
    echo [ERROR] .venv not found. Have you run the Setup.bat?
    pause
    exit /b 1
)

if "%~1" neq "" (
    echo Run WinSentry with arguments: %*
    python main.py %*
    goto :END
)

:MENU
schtasks /query /TN "WinSentry" >nul 2>&1
if %errorlevel% equ 0 (
    set "autostart_status=ACTIVE (System Startup)"
    set "color=!ESC![92m"
) else (
    set "autostart_status=NOT ACTIVE"
    set "color=!ESC![91m"
)

cls
echo ==========================================
echo                WinSentry    
echo ==========================================
echo.
echo  1. Run WinSentry (Dashboard Mode)
echo  2. Run WinSentry (Terminal Mode)
echo  3. Show help page
echo  4. Run with your own arguments
echo  5. Add to Windows startup (Runs hidden at boot)
echo  6. Remove from Windows startup
echo  7. Stop background service (Kill process)
echo  8. Run Test Script (Generate Events)
echo  9. Reset Windows Security Log (Sets Count to 0)
echo  10. Check current version
echo  11. Quit
echo.
echo Autostart: !color!!autostart_status!!ESC![0m
echo.
set /p choice="Choose (1-10): "

if "%choice%"=="1" goto RUN_DASHBOARD
if "%choice%"=="2" goto RUN_TERMINAL
if "%choice%"=="3" goto RUN_HELP
if "%choice%"=="4" goto RUN_CUSTOM
if "%choice%"=="5" goto RUN_AUTOSTART
if "%choice%"=="6" goto RUN_UNAUTOSTART
if "%choice%"=="7" goto RUN_STOP
if "%choice%"=="8" goto RUN_TEST
if "%choice%"=="9" goto RUN_RESET_LOGS
if "%choice%"=="10" goto CHECK_VERSION
if "%choice%"=="11" goto END

echo Not a valid choice
pause
goto MENU

:RUN_DASHBOARD
python main.py -d
pause
goto MENU

:RUN_TERMINAL
python main.py -t
goto END

:RUN_HELP
python main.py -h
pause
goto MENU

:RUN_CUSTOM
set /p arguments="Write out your arguments: "
python main.py !arguments!
goto END

:RUN_AUTOSTART
python main.py -a
pause
goto MENU

:RUN_UNAUTOSTART
python main.py -u
pause
goto MENU

:RUN_STOP
python main.py --stop
pause
goto MENU

:RUN_TEST
echo.
echo Launching Test Script...
python tests/generate_events.py
pause
goto MENU

:RUN_RESET_LOGS
echo.
python tests/reset_security_log.py
pause
goto MENU

:CHECK_VERSION 
echo.
python main.py -v
pause
goto MENU

:END
echo.
if "%choice%"=="1" pause
ENDLOCAL