#!/usr/bin/env bash
# Script to run data preprocessing locally

set -e  # Exit on error

echo "=========================================="
echo "Running Data Preprocessing"
echo "=========================================="

# Run preprocessing
python -m src.data.preprocess

echo "=========================================="
echo "Preprocessing Complete!"
echo "=========================================="
