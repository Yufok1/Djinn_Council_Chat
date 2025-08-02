@echo off
echo 🜂 Djinn Council GUI Launcher
echo =============================

echo.
echo Launching Djinn Council Visual Interface...
echo.
echo Features:
echo   • Visual model selection for each djinn role
echo   • Real-time response display with confidence meters
echo   • Interactive consensus voting
echo   • Configuration save/load
echo   • Chat history and session metrics
echo   • NO TIMEOUTS - Models have unlimited time to think deeply
echo.

echo Checking requirements...

python -c "import tkinter" 2>nul
if errorlevel 1 (
    echo ❌ Error: tkinter not available
    echo Please ensure you have Python with tkinter support
    pause
    exit /b 1
)

python -c "import ollama" 2>nul
if errorlevel 1 (
    echo ❌ Error: ollama module not found
    echo Please install: pip install ollama
    pause
    exit /b 1
)

echo ✅ Requirements check passed
echo.

echo 🜂 Starting Djinn Council GUI...
python djinn_council_gui.py

if errorlevel 1 (
    echo.
    echo ❌ GUI failed to start
    echo Check that:
    echo   1. Ollama is running (ollama serve)
    echo   2. You have at least one model installed (ollama pull llama3.2)
    echo   3. All Python dependencies are installed
    pause
)

echo.
echo 🜂 GUI session ended
pause