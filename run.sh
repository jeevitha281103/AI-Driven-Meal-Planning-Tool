#!/bin/bash
echo "===================================="
echo "  NutriFit - Indian Food Classifier"
echo "===================================="
echo ""

echo "[1/2] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install dependencies."
    exit 1
fi

echo ""
echo "[2/2] Starting NutriFit server..."
echo "Server will open at http://127.0.0.1:5000"
echo "Press Ctrl+C to stop."
echo ""
python app.py
