@echo off
echo ====================================
echo   NutriFit - Indian Food Classifier
echo ====================================
echo.

echo [1/2] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [2/2] Starting NutriFit server...
echo Server will open at http://127.0.0.1:5000
echo Press Ctrl+C to stop.
echo.
python app.py
