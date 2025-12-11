# 🐳 Docker Deployment Guide

This guide provides comprehensive instructions for containerizing and deploying the Cloud NLP Classifier using Docker.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Building the Docker Image](#building-the-docker-image)
4. [Running the Container](#running-the-container)
5. [Testing the API](#testing-the-api)
6. [Container Management](#container-management)
7. [Advanced Configuration](#advanced-configuration)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

## Overview

This project provides two Docker containers:

### 1. FastAPI Server (`Dockerfile`)
- **Base Image**: `python:3.11-slim` (lightweight, secure)
- **Web Server**: FastAPI + Uvicorn
- **Port**: 8000
- **Model**: Pre-trained DistilBERT transformer
- **Security**: Non-root user, minimal attack surface
- **Health Checks**: Automatic health monitoring
- **Size**: ~2 GB (optimized with multi-stage caching)

### 2. Streamlit UI (`Dockerfile.streamlit`)
- **Base Image**: `python:3.11-slim`
- **Web Framework**: Streamlit
- **Port**: 8501
- **Features**: Interactive chat interface, model selection
- **Security**: Non-root user, headless mode
- **Health Checks**: Streamlit health endpoint
- **Size**: ~2.5 GB (includes models)

**📚 For Streamlit UI Docker guide, see**: [`DOCKER_STREAMLIT_GUIDE.md`](./DOCKER_STREAMLIT_GUIDE.md)

## Prerequisites

### Required

1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
   - [Install Docker](https://docs.docker.com/get-docker/)
   - Verify: `docker --version`

2. **Trained Model**
   - Model must exist at: `models/transformer/distilbert/`
   - Train with: `python run_transformer.py`

3. **Disk Space**
   - At least 3 GB free space for image + layers

### Optional

- **Docker Compose** (for multi-container setups)
- **Docker Hub account** (for pushing images)

## Building the Docker Image

### Basic Build

```bash
# Build with default tag
docker build -t cloud-nlp-classifier .

# Build time: 5-10 minutes (first build)
# Subsequent builds: 1-2 minutes (with cache)
```

### Build with Version Tag

```bash
# Semantic versioning
docker build -t cloud-nlp-classifier:1.0.0 .
docker build -t cloud-nlp-classifier:latest .

# Date-based versioning
docker build -t cloud-nlp-classifier:2024-12-09 .
```

### Build Options

```bash
# No cache (clean rebuild)
docker build --no-cache -t cloud-nlp-classifier .

# Show build progress
docker build --progress=plain -t cloud-nlp-classifier .

# Build with specific Dockerfile
docker build -f Dockerfile.prod -t cloud-nlp-classifier .

# Build with build arguments
docker build --build-arg PYTHON_VERSION=3.11 -t cloud-nlp-classifier .
```

### Verify Build

```bash
# List images
docker images cloud-nlp-classifier

# Expected output:
# REPOSITORY              TAG       IMAGE ID       CREATED         SIZE
# cloud-nlp-classifier    latest    abc123def456   2 minutes ago   2.1GB

# Inspect image details
docker inspect cloud-nlp-classifier

# View image layers
docker history cloud-nlp-classifier
```

## Running the Container

### Basic Run

```bash
# Foreground (see logs)
docker run -p 8000:8000 cloud-nlp-classifier

# Background (detached)
docker run -d -p 8000:8000 --name nlp-api cloud-nlp-classifier
```

### Run with Options

```bash
# Custom port mapping
docker run -d -p 9000:8000 --name nlp-api cloud-nlp-classifier

# With restart policy (auto-restart on failure)
docker run -d -p 8000:8000 --name nlp-api --restart unless-stopped cloud-nlp-classifier

# With memory limit
docker run -d -p 8000:8000 --name nlp-api --memory="2g" --memory-swap="2g" cloud-nlp-classifier

# With CPU limit (50% of one core)
docker run -d -p 8000:8000 --name nlp-api --cpus="0.5" cloud-nlp-classifier

# With environment variables
docker run -d -p 8000:8000 --name nlp-api \
  -e LOG_LEVEL=debug \
  -e MAX_WORKERS=2 \
  cloud-nlp-classifier

# Interactive mode (for debugging)
docker run -it -p 8000:8000 cloud-nlp-classifier /bin/bash
```

### Run with Volume Mounts (Development)

```bash
# Mount source code for live development
docker run -d -p 8000:8000 --name nlp-api \
  -v $(pwd)/src:/app/src \
  cloud-nlp-classifier

# Mount logs directory
docker run -d -p 8000:8000 --name nlp-api \
  -v $(pwd)/logs:/app/logs \
  cloud-nlp-classifier
```

## Testing the API

### Health Check

```bash
# Basic health check
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "model_loaded": true,
#   "num_classes": 3
# }

# Check with verbose output
curl -v http://localhost:8000/health
```

### Prediction Endpoint

```bash
# Simple prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test message"}'

# Expected response:
# {
#   "predicted_label": "neither",
#   "confidence": 0.95,
#   "all_scores": {...},
#   "inference_time_ms": 45.2
# }

# Multiple predictions
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!"}'

curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is offensive content"}'
```

### Interactive Documentation

```bash
# Open in browser
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Load Testing

```bash
# Using Apache Bench (if installed)
ab -n 100 -c 10 -p request.json -T application/json http://localhost:8000/predict

# Using Python script
python scripts/client_example.py
```

## Container Management

### View Containers

```bash
# Running containers
docker ps

# All containers (including stopped)
docker ps -a

# Filter by name
docker ps -f name=nlp-api

# Show container resource usage
docker stats nlp-api
```

### View Logs

```bash
# View all logs
docker logs nlp-api

# Follow logs in real-time
docker logs -f nlp-api

# Last 100 lines
docker logs --tail 100 nlp-api

# Logs since 10 minutes ago
docker logs --since 10m nlp-api

# Logs with timestamps
docker logs -t nlp-api
```

### Control Container

```bash
# Stop container (graceful shutdown)
docker stop nlp-api

# Start stopped container
docker start nlp-api

# Restart container
docker restart nlp-api

# Pause container (freeze processes)
docker pause nlp-api

# Unpause container
docker unpause nlp-api

# Kill container (force stop)
docker kill nlp-api
```

### Execute Commands in Container

```bash
# Open bash shell
docker exec -it nlp-api /bin/bash

# Run Python command
docker exec nlp-api python -c "import torch; print(torch.__version__)"

# Check disk usage
docker exec nlp-api df -h

# View running processes
docker exec nlp-api ps aux
```

### Remove Container

```bash
# Remove stopped container
docker rm nlp-api

# Force remove running container
docker rm -f nlp-api

# Remove all stopped containers
docker container prune
```

### Remove Image

```bash
# Remove image
docker rmi cloud-nlp-classifier

# Force remove (even if containers exist)
docker rmi -f cloud-nlp-classifier

# Remove all unused images
docker image prune -a
```

## Advanced Configuration

### Multi-Worker Setup

```bash
# Run with multiple Uvicorn workers
docker run -d -p 8000:8000 --name nlp-api \
  cloud-nlp-classifier \
  uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Custom Entrypoint

```bash
# Override CMD
docker run -d -p 8000:8000 --name nlp-api \
  cloud-nlp-classifier \
  uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --log-level debug

# Override ENTRYPOINT
docker run -it --entrypoint /bin/bash cloud-nlp-classifier
```

### Network Configuration

```bash
# Create custom network
docker network create nlp-network

# Run container on custom network
docker run -d --name nlp-api --network nlp-network cloud-nlp-classifier

# Connect existing container to network
docker network connect nlp-network nlp-api
```

### Health Check Configuration

```bash
# Run with custom health check
docker run -d -p 8000:8000 --name nlp-api \
  --health-cmd="curl -f http://localhost:8000/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  --health-start-period=40s \
  cloud-nlp-classifier

# Check health status
docker inspect --format='{{.State.Health.Status}}' nlp-api
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker logs nlp-api

# Run in interactive mode
docker run -it -p 8000:8000 cloud-nlp-classifier

# Check if port is already in use
netstat -an | grep 8000  # Linux/Mac
netstat -an | findstr 8000  # Windows

# Use different port
docker run -d -p 8001:8000 --name nlp-api cloud-nlp-classifier
```

### Model Not Found Error

```bash
# Verify model files exist before building
ls -la models/transformer/distilbert/

# Required files:
# - config.json
# - model.safetensors
# - tokenizer files
# - labels.json

# If missing, train the model first
python run_transformer.py
```

### Out of Memory

```bash
# Check Docker memory limit
docker info | grep Memory

# Increase memory in Docker Desktop:
# Settings → Resources → Memory → Increase to 4GB+

# Run with explicit memory limit
docker run -d -p 8000:8000 --name nlp-api \
  --memory="2g" --memory-swap="2g" \
  cloud-nlp-classifier
```

### Slow Performance

```bash
# Check resource usage
docker stats nlp-api

# Increase CPU allocation
docker run -d -p 8000:8000 --name nlp-api \
  --cpus="2.0" \
  cloud-nlp-classifier

# Use GPU (if available)
docker run -d -p 8000:8000 --name nlp-api \
  --gpus all \
  cloud-nlp-classifier
```

### Permission Errors

```bash
# Container runs as non-root user (appuser)
# If you need root access for debugging:
docker exec -it --user root nlp-api /bin/bash

# Fix file permissions
docker exec --user root nlp-api chown -R appuser:appuser /app
```

### Network Issues

```bash
# Test connectivity from inside container
docker exec nlp-api curl http://localhost:8000/health

# Check if port is exposed
docker port nlp-api

# Inspect network settings
docker inspect nlp-api | grep -A 20 NetworkSettings
```

## Best Practices

### Security

1. **Non-root user**: Container runs as `appuser` (UID 1000)
2. **Minimal base image**: Using `python:3.11-slim`
3. **No secrets in image**: Pass sensitive data via environment variables
4. **Regular updates**: Rebuild image with updated dependencies

### Performance

1. **Layer caching**: Order Dockerfile commands from least to most frequently changed
2. **Multi-stage builds**: Consider using multi-stage builds for smaller images
3. **Resource limits**: Set appropriate memory and CPU limits
4. **Health checks**: Enable health checks for production deployments

### Monitoring

1. **Log aggregation**: Use `docker logs` or external logging service
2. **Metrics collection**: Monitor with `docker stats` or Prometheus
3. **Health checks**: Regularly check `/health` endpoint
4. **Alerts**: Set up alerts for container failures

### Production Deployment

1. **Use specific tags**: Avoid `latest` tag in production
2. **Restart policy**: Use `--restart unless-stopped`
3. **Resource limits**: Always set memory and CPU limits
4. **Orchestration**: Consider Kubernetes or Docker Swarm for scaling
5. **Load balancing**: Use reverse proxy (nginx, Traefik) for multiple instances

### Development Workflow

1. **Volume mounts**: Mount source code for live development
2. **Hot reload**: Use `--reload` flag for Uvicorn
3. **Debug mode**: Run with `-e LOG_LEVEL=debug`
4. **Interactive shell**: Use `docker exec -it` for debugging

---

## Quick Reference

```bash
# Build
docker build -t cloud-nlp-classifier .

# Run
docker run -d -p 8000:8000 --name nlp-api cloud-nlp-classifier

# Test
curl http://localhost:8000/health

# Logs
docker logs -f nlp-api

# Stop
docker stop nlp-api

# Remove
docker rm nlp-api
docker rmi cloud-nlp-classifier
```

---

**For more information, see:**
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Project README](../README.md)
