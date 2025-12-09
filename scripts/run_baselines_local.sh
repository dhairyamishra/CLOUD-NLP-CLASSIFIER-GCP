#!/usr/bin/env bash
# Script to run baseline model training locally

set -e  # Exit on error

echo "=========================================="
echo "Training Baseline Models"
echo "=========================================="

# Run baseline training
python -m src.models.train_baselines

echo "=========================================="
echo "Baseline Training Complete!"
echo "=========================================="
