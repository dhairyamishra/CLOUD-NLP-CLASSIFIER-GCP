#!/bin/bash
# Docker entrypoint script for Streamlit UI
# Checks models before starting the application

set -e

echo "=========================================="
echo "  Cloud NLP Classifier - Streamlit UI"
echo "=========================================="
echo ""

# Run model check
echo "🔍 Checking for trained models..."
python scripts/check_models.py

echo ""
echo "=========================================="
echo "  Starting Streamlit Application"
echo "=========================================="
echo ""

# Start Streamlit
exec streamlit run src/ui/streamlit_app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
