#!/usr/bin/env bash
# Bash script to run FastAPI server locally

set -e

echo "=========================================="
echo "Starting FastAPI Server"
echo "=========================================="

# Run FastAPI server with uvicorn
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload

echo "=========================================="
echo "Server stopped"
echo "=========================================="
