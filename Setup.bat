@echo off

SETLOCAL EnableDelayedExpansion

echo === Windows Log Analyzer: venv setup ===

REM Detect Python (prefer py -3)
where py >nul 2>nul
if %errorlevel%==0 (
	set "PY=py -3"
) else (
	where python >nul 2>nul
	if %errorlevel%==0 (
		set "PY=python"
	) else (
		echo ERROR: Python 3 not found on PATH. Please install Python 3 and try again.
		pause
		exit /b 1
	)
)

REM Optionally recreate the venv
if /I "%1"=="recreate" (
	if exist ".venv" (
		echo Removing existing .venv...
		rmdir /s /q ".venv"
	)
)

if not exist ".venv" (
	echo Creating virtual environment in .venv...
	%PY% -m venv ".venv"
	if errorlevel 1 (
		echo ERROR: Failed to create virtual environment. Ensure the 'venv' module is available.
		pause
		exit /b 1
	)
) else (
	echo .venv already exists. Skipping creation.
)

echo Activating .venv...
call ".venv\Scripts\activate"
if "%VIRTUAL_ENV%"=="" (
	echo ERROR: Failed to activate the virtual environment.
	pause
	exit /b 1
)

echo Upgrading pip in .venv...
python -m pip install --upgrade pip

if not exist "requirements.txt" (
	echo No requirements.txt found; skipping package installation.
) else (
	echo Installing packages from requirements.txt...
	python -m pip install -r requirements.txt
	if errorlevel 1 (
		echo WARNING: Some packages failed to install. Review errors above.
	) else (
		echo Packages installed successfully.
	)
)

echo Setup finished
pause

ENDLOCAL