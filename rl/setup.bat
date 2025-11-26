@echo off
REM Setup script for RL Test Generation Environment (Windows)

echo ==========================================
echo RL Test Gen Environment Setup
echo ==========================================

REM check python version
echo.
echo Checking Python version...
python --version
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.11+
    exit /b 1
)

REM create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv

REM activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM install requirements
echo.
echo Installing requirements...
pip install -r requirements.txt

REM check docker
echo.
echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo X Docker is not installed. Please install Docker Desktop.
    exit /b 1
) else (
    echo + Docker is installed
)

docker ps >nul 2>&1
if errorlevel 1 (
    echo X Docker daemon is not running. Please start Docker Desktop.
    exit /b 1
) else (
    echo + Docker daemon is running
)

REM build docker image
echo.
echo Building test runner Docker image...
docker build -f Dockerfile.testrunner -t testrunner:latest .

REM create problems directory if it doesn't exist
echo.
echo Setting up directories...
if not exist "problems" mkdir problems
echo + Created 'problems' directory for dataset

echo.
echo ==========================================
echo Setup complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate.bat
echo.
echo 2. Place your problem JSON files in the 'problems' directory
echo.
echo 3. Run the example:
echo    python example_usage.py
echo.
pause

