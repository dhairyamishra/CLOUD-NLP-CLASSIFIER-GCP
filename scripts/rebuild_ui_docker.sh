#!/bin/bash
# Bash script to rebuild and restart Streamlit UI Docker container
# This script ensures all models are included and properly loaded

set -e

echo "========================================="
echo "  Rebuild Streamlit UI Docker Container"
echo "========================================="
echo ""

# Step 1: Check if models exist locally
echo "Step 1: Checking for trained models..."
if ! python scripts/check_models.py; then
    echo ""
    echo "WARNING: Some models are missing!"
    echo "It's recommended to train all models before building Docker image."
    echo ""
    read -p "Do you want to continue anyway? (y/N): " response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 1
    fi
fi

echo ""
echo "Step 2: Stopping existing container..."
docker-compose -f docker-compose.ui.yml down

echo ""
echo "Step 3: Rebuilding Docker image (no cache)..."
docker-compose -f docker-compose.ui.yml build --no-cache

echo ""
echo "Step 4: Starting container..."
docker-compose -f docker-compose.ui.yml up -d

echo ""
echo "Step 5: Waiting for container to be ready..."
sleep 10

echo ""
echo "Step 6: Checking container logs..."
docker logs nlp-ui-dev

echo ""
echo "========================================="
echo "  Deployment Complete!"
echo "========================================="
echo ""
echo "Access the Streamlit UI at:"
echo "  http://localhost:8501"
echo ""
echo "To view logs:"
echo "  docker logs -f nlp-ui-dev"
echo ""
echo "To stop the container:"
echo "  docker-compose -f docker-compose.ui.yml down"
echo ""
