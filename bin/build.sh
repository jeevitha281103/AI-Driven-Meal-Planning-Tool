#!/bin/bash
set -e

echo "=== NutriFit Build ==="

# Install Python dependencies
pip install -r requirements.txt

# Ensure git lfs is installed and pull large files
echo "Checking Git LFS..."
if command -v git-lfs &> /dev/null; then
    git lfs install
    git lfs pull
    echo "LFS files pulled successfully"
else
    echo "WARNING: git-lfs not found in PATH"
fi

# Verify model file
MODEL="Model/model_v1_inceptionV3.h5"
if [ -f "$MODEL" ]; then
    SIZE=$(wc -c < "$MODEL")
    echo "Model file size: $SIZE bytes"
    if [ "$SIZE" -lt 1000 ]; then
        echo "WARNING: Model file appears to be an LFS pointer"
    fi
else
    echo "WARNING: Model file not found"
fi

echo "Build complete"
