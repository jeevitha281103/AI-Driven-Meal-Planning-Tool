#!/bin/bash
set -e

echo "=== NutriFit Startup ==="
echo "Time: $(date)"
echo "PORT: ${PORT:-5000}"

MODEL="Model/model_v1_inceptionV3.h5"

# Check if model exists and is an LFS pointer
if [ -f "$MODEL" ]; then
    SIZE=$(wc -c < "$MODEL")
    echo "Model file: $SIZE bytes"
    if [ "$SIZE" -lt 1000 ]; then
        echo "LFS pointer detected. Pulling actual model file..."
        git lfs install --skip-smudge 2>/dev/null || true
        git lfs pull 2>&1 || echo "WARNING: git lfs pull failed"
        NEW_SIZE=$(wc -c < "$MODEL" 2>/dev/null || echo "0")
        echo "Model file after LFS pull: $NEW_SIZE bytes"
        if [ "$NEW_SIZE" -lt 1000 ]; then
            echo "ERROR: Model file is still an LFS pointer. Prediction will fail."
        fi
    fi
else
    echo "Model file not found at $MODEL. Attempting git lfs pull..."
    git lfs install 2>/dev/null || true
    git lfs pull 2>&1 || true
fi

# Ensure uploads directory exists
mkdir -p uploads

# Start gunicorn
echo "Starting gunicorn on port ${PORT:-5000}..."
exec gunicorn app:app \
    --timeout 120 \
    --workers 1 \
    --threads 2 \
    --bind 0.0.0.0:${PORT:-5000} \
    --access-logfile - \
    --error-logfile - \
    --log-level info
