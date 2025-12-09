#!/usr/bin/env bash
# Script to run transformer training locally

set -e

echo "=========================================="
echo "Starting Transformer Training Pipeline"
echo "=========================================="

# Run transformer training
python -m src.models.transformer_training

echo "=========================================="
echo "Transformer Training Complete!"
echo "=========================================="
