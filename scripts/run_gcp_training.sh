#!/bin/bash
# GCP Cloud Training Script
# Run transformer training on GCP GPU VM with optimized settings

set -e  # Exit on error

echo "=========================================="
echo "GCP Cloud Training - DistilBERT"
echo "=========================================="

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
else
    echo "Error: Virtual environment not found!"
    echo "Please run setup_gcp_training.sh first"
    exit 1
fi

# Check GPU availability
echo ""
echo "Checking GPU availability..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi
    echo ""
else
    echo "Warning: No GPU detected. Training will use CPU (slower)."
    echo ""
fi

# Set environment variables for optimal performance
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export CUDA_LAUNCH_BLOCKING=0  # Async CUDA operations for speed

# Training configuration
CONFIG_FILE="${1:-config/config_transformer_cloud.yaml}"
MODE="${2:-cloud}"
OUTPUT_DIR="${3:-models/transformer/distilbert_cloud}"

echo "Configuration:"
echo "  Config file: $CONFIG_FILE"
echo "  Training mode: $MODE"
echo "  Output directory: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Start training with cloud-optimized settings
echo "Starting training..."
echo "=========================================="
python -m src.models.transformer_training \
    --config "$CONFIG_FILE" \
    --mode "$MODE" \
    --output-dir "$OUTPUT_DIR" \
    --fp16 \
    2>&1 | tee "${OUTPUT_DIR}/training.log"

# Check if training was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Training completed successfully!"
    echo "=========================================="
    echo ""
    echo "Model saved to: $OUTPUT_DIR"
    echo "Training log: ${OUTPUT_DIR}/training.log"
    echo ""
    
    # Display model info
    if [ -f "${OUTPUT_DIR}/training_info.json" ]; then
        echo "Training Summary:"
        cat "${OUTPUT_DIR}/training_info.json"
        echo ""
    fi
    
    # Optionally copy model to Google Cloud Storage
    # Uncomment and configure if you want to backup to GCS
    # GCS_BUCKET="gs://your-bucket-name/models"
    # echo "Copying model to GCS: $GCS_BUCKET"
    # gsutil -m cp -r "$OUTPUT_DIR" "$GCS_BUCKET/"
    
else
    echo ""
    echo "=========================================="
    echo "Training failed! Check logs for details."
    echo "=========================================="
    exit 1
fi
