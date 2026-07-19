#!/bin/bash
# Startup script: ensure LFS model is pulled, then start gunicorn

echo "=== NutriFit Startup ==="

# Check if model is an LFS pointer (small file)
MODEL="Model/model_v1_inceptionV3.h5"
if [ -f "$MODEL" ]; then
    SIZE=$(wc -c < "$MODEL")
    echo "Model file size: $SIZE bytes"
    if [ "$SIZE" -lt 1000 ]; then
        echo "Model is an LFS pointer. Pulling actual file..."
        git lfs install
        git lfs pull
        echo "New model size: $(wc -c < "$MODEL") bytes"
    fi
else
    echo "Model file not found. Attempting git lfs pull..."
    git lfs install
    git lfs pull
fi

# Ensure uploads directory exists
mkdir -p uploads

# Start gunicorn
echo "Starting gunicorn..."
exec gunicorn app:app --timeout 120 --workers 1 --threads 2 --bind 0.0.0.0:$PORT
