@echo off

cd /d "%~dp0"

SETLOCAL EnableDelayedExpansion

:: Adding escape sign for terminal color management
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
  set "ESC=%%b"
)

:: Check for and activate .venv
if exist .venv\Scripts\activate.bat (
    call ".venv\Scripts\activate.bat"
) else (
    echo [ERROR] .venv not found. Have you run the Setup.bat?
    pause
    exit /b 1
)

:: Handle user targeting .bat instead of main.py with arguments
if "%~1" neq "" (
    echo Run WinSentry with arguments: %*
    python main.py %*
    goto :END
)

:MENU
:: Check if application is set to autostart
schtasks /query /TN "WinSentry" >nul 2>&1

if %errorlevel% equ 0 (
    :: Set green
    set "autostart_status=ACTIVE (Task Scheduler)"
    set "color=!ESC![92m"
) else (
    ::Set red
    set "autostart_status=NOT ACTIVE"
    set "color=!ESC![91m"
)
:TEST
:: Menu handling
cls
echo ==========================================
echo                WinSentry    
echo ==========================================
echo.
echo  1. Run standard mode using all modules
echo  2. Show help page
echo  3. Run with your own arguments
echo  4. Add to Windows startup
echo  5. Remove from Windows startup
echo  6. Quit
echo.
echo Autostart: !color!!autostart_status!!ESC![0m
echo.
set /p choice="Choose (1-6): "

if "%choice%"=="1" goto RUN_STANDARD_MODE
if "%choice%"=="2" goto RUN_HELP
if "%choice%"=="3" goto RUN_CUSTOM
if "%choice%"=="4" goto RUN_AUTOSTART
if "%choice%"=="5" goto RUN_UNAUTOSTART
if "%choice%"=="6" goto END

echo Not a valid choice
pause
goto MENU

:RUN_STANDARD_MODE
python main.py -s
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

:END
echo.
if "%choice%"=="1" pause

ENDLOCAL