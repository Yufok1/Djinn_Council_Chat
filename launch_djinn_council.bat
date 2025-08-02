@echo off
echo 🜂 Djinn Council Launcher
echo =====================

echo.
echo Available modes:
echo   1. Interactive mode (default)
echo   2. Status check
echo   3. Single query mode
echo.

set /p choice="Select mode (1-3) or press Enter for interactive: "

if "%choice%"=="2" (
    echo.
    echo 🜂 Checking Council Status...
    python djinn_council.py --status
    pause
    goto end
)

if "%choice%"=="3" (
    echo.
    set /p query="Enter your query: "
    echo.
    echo 🜂 Invoking Council...
    python djinn_council.py "%query%"
    pause
    goto end
)

echo.
echo 🜂 Starting Interactive Djinn Council...
echo Type 'quit' to exit, 'status' for council status
echo.
python djinn_council.py

:end
echo.
echo 🜂 Council session ended
pause