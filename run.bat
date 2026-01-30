@echo off
setlocal

if "%1"=="install" (
    echo Installing dependencies...
    pip install -r requirements.txt
) else if "%1"=="run" (
    echo Starting CLI Interview Coach...
    python main.py
) else if "%1"=="ui" (
    echo Starting Streamlit UI...
    streamlit run streamlit_app.py
) else if "%1"=="validate" (
    echo Validating log for scenario %2...
    if "%2"=="" (
        python validate_logs.py interview_log_1.json
    ) else (
        python validate_logs.py interview_log_%2.json
    )
) else if "%1"=="test" (
    echo Running smoke tests...
    python smoke_test.py
) else (
    echo Available commands:
    echo   run.bat install    - Install requirements
    echo   run.bat ui         - Run Web Interface (Recommended)
    echo   run.bat run        - Run CLI Interface
    echo   run.bat validate N - Validate log (e.g., validate 1)
)
