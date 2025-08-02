@echo off
echo 🜂 Advanced Djinn Council Launcher (CISM Enabled)
echo ====================================================

echo.
echo Council Invocation State Machine (CISM) Features:
echo   • State Management: IDLE → ASSEMBLING → DELIBERATING → CONSENSUS → OUTPUT → LOGGED
echo   • Integrity Safeguards: Recursion depth tracking, divergence monitoring
echo   • Advanced Consensus: Confidence scoring, weighted roles, deliberative loops
echo   • Security Controls: Prompt injection detection, input sanitization
echo   • Performance: Persistent worker threads, parallel execution
echo.

echo Available modes:
echo   1. Interactive mode (default) - Full CISM with state transitions
echo   2. System status - View council health and configuration
echo   3. Single query mode - Direct invocation with consensus algorithm
echo   4. Test mode - Run integrity and consensus tests
echo.

set /p choice="Select mode (1-4) or press Enter for interactive: "

if "%choice%"=="2" (
    echo.
    echo 🜂 Checking Advanced Council Status...
    python advanced_djinn_council.py --status
    pause
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Available consensus modes:
    echo   • majority_vote - Simple majority consensus
    echo   • confidence_scoring - Confidence-weighted selection  
    echo   • weighted_roles - Role-priority weighted consensus
    echo   • deliberative_loop - Multi-iteration deliberation
    echo   • hybrid - Present all responses for manual selection
    echo.
    set /p mode="Enter consensus mode (default: weighted_roles): "
    if "%mode%"=="" set mode=weighted_roles
    
    set /p query="Enter your query: "
    echo.
    echo 🜂 Invoking Advanced Council with %mode% consensus...
    python advanced_djinn_council.py --mode %mode% "%query%"
    pause
    goto end
)

if "%choice%"=="4" (
    echo.
    echo 🜂 Running Council Tests...
    echo Testing basic invocation...
    python advanced_djinn_council.py "Test council functionality and response quality"
    echo.
    echo Testing different consensus modes...
    python advanced_djinn_council.py --mode confidence_scoring "Compare confidence scoring vs weighted roles"
    pause
    goto end
)

echo.
echo 🜂 Starting Advanced Interactive Djinn Council...
echo.
echo Commands:
echo   • Type your query directly
echo   • 'quit' or 'exit' to terminate
echo   • 'status' to view council status
echo   • Consensus modes: majority_vote, confidence_scoring, weighted_roles, deliberative_loop, hybrid
echo.
echo State Machine Flow: IDLE → ASSEMBLING → DELIBERATING → CONSENSUS → OUTPUT → LOGGED → IDLE
echo Security Level: BASIC (Prompt injection detection enabled)
echo.
python advanced_djinn_council.py

:end
echo.
echo 🜂 Advanced Council session ended
echo State: IDLE (Ready for next invocation)
pause