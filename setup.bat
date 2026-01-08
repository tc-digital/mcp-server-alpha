@echo off
REM
REM Automated setup script for mcp-server-alpha (Windows)
REM This script creates a virtual environment, installs dependencies, and can start the server.
REM

setlocal enabledelayedexpansion

echo === MCP Server Alpha - Automated Setup ===
echo.

REM Get the directory where the script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo Working directory: %SCRIPT_DIR%
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.10 or higher from python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Get version info directly from Python for reliability
for /f "delims=" %%i in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"') do set PYTHON_VERSION=%%i
for /f "delims=" %%i in ('python -c "import sys; print(sys.version_info.major)"') do set PYTHON_MAJOR=%%i
for /f "delims=" %%i in ('python -c "import sys; print(sys.version_info.minor)"') do set PYTHON_MINOR=%%i

echo [OK] Python %PYTHON_VERSION% detected
echo.

if %PYTHON_MAJOR% LSS 3 (
    echo ERROR: Python 3.10 or higher is required. Found: %PYTHON_VERSION%
    pause
    exit /b 1
)
if %PYTHON_MAJOR% EQU 3 if %PYTHON_MINOR% LSS 10 (
    echo ERROR: Python 3.10 or higher is required. Found: %PYTHON_VERSION%
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [WARNING] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip 2>nul
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
) else (
    echo [OK] pip upgraded
)
echo.

REM Install dependencies
echo Installing dependencies...
pip install -e .[dev]
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully
echo.

REM Check for environment variables
echo Checking environment variables...
if not defined OPENAI_API_KEY (
    echo [WARNING] OPENAI_API_KEY not set
    echo   To use the research assistant, set your OpenAI API key:
    echo     set OPENAI_API_KEY=sk-...
    echo   Or add it to your system environment variables
) else (
    echo [OK] OPENAI_API_KEY is set
)

if not defined POWER_AUTOMATE_WEBHOOK_URL (
    echo [WARNING] POWER_AUTOMATE_WEBHOOK_URL not set ^(optional^)
    echo   To use the send_email tool, set your Power Automate webhook URL:
    echo     set POWER_AUTOMATE_WEBHOOK_URL=https://...
    echo   Or add it to your system environment variables
) else (
    echo [OK] POWER_AUTOMATE_WEBHOOK_URL is set
)
echo.

echo [SUCCESS] Setup complete!
echo.
echo Next steps:
echo.
echo   1. To activate the virtual environment manually:
echo      venv\Scripts\activate
echo.
echo   2. To run an example:
echo      python examples\research_example.py
echo.
echo   3. To start the MCP server ^(for Claude Desktop integration^):
echo      python -m mcp_server_alpha.server
echo.
echo   4. To run tests:
echo      pytest
echo.

REM Ask if user wants to start the server
set /p START_SERVER="Would you like to start the MCP server now? (y/N): "
if /i "!START_SERVER!"=="y" (
    echo.
    echo Starting MCP server...
    echo   ^(Press Ctrl+C to stop^)
    echo.
    python -m mcp_server_alpha.server
)

endlocal
