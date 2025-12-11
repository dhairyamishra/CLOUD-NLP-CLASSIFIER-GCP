# 🐳 Docker Compose Guide

Complete guide for using Docker Compose with the Cloud NLP Classifier project.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Available Configurations](#available-configurations)
3. [Quick Start](#quick-start)
4. [Configuration Files](#configuration-files)
5. [Common Commands](#common-commands)
6. [Environment Variables](#environment-variables)
7. [Scaling](#scaling)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)

---

## Overview

Docker Compose simplifies running the NLP classifier by managing container lifecycle, networking, and configuration in a single file.

**Benefits**:
- ✅ Single command to start/stop services
- ✅ Easy environment configuration
- ✅ Network isolation
- ✅ Volume management
- ✅ Service dependencies
- ✅ Resource limits

---

## Available Configurations

### 1. `docker-compose.yml` (Default)
**Purpose**: Standard deployment  
**Use Case**: Local testing, single-instance deployment

```bash
docker-compose up -d
```

### 2. `docker-compose.dev.yml` (Development)
**Purpose**: Development with hot-reload  
**Use Case**: Active development, debugging

```bash
docker-compose -f docker-compose.dev.yml up
```

### 3. `docker-compose.prod.yml` (Production)
**Purpose**: Production-ready with multiple workers  
**Use Case**: Production deployment, high traffic

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Quick Start

### Basic Usage

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart
```

### Development Mode

```bash
# Start with hot-reload
docker-compose -f docker-compose.dev.yml up

# Code changes will automatically reload the server
```

### Production Mode

```bash
# Start production configuration
docker-compose -f docker-compose.prod.yml up -d

# Scale to multiple instances (if using swarm)
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

---

## Configuration Files

### docker-compose.yml (Default)

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    image: cloud-nlp-classifier:latest
    container_name: nlp-api
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
      - WORKERS=1
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - nlp-network
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
```

**Features**:
- Single worker for simplicity
- Health checks enabled
- Resource limits set
- Persistent logs
- Auto-restart on failure

---

## Common Commands

### Starting Services

```bash
# Start in background (detached)
docker-compose up -d

# Start in foreground (see logs)
docker-compose up

# Start specific service
docker-compose up api

# Start with rebuild
docker-compose up -d --build

# Start with specific file
docker-compose -f docker-compose.prod.yml up -d
```

### Stopping Services

```bash
# Stop services (keep containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v

# Stop specific service
docker-compose stop api
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs api

# Last 100 lines
docker-compose logs --tail=100

# Logs since 10 minutes ago
docker-compose logs --since 10m
```

### Managing Services

```bash
# List running services
docker-compose ps

# Restart services
docker-compose restart

# Restart specific service
docker-compose restart api

# Execute command in service
docker-compose exec api /bin/bash

# View service configuration
docker-compose config

# Validate compose file
docker-compose config --quiet
```

### Building

```bash
# Build images
docker-compose build

# Build without cache
docker-compose build --no-cache

# Build specific service
docker-compose build api

# Pull latest images
docker-compose pull
```

---

## Environment Variables

### Setting Variables

**Method 1: In docker-compose.yml**
```yaml
environment:
  - LOG_LEVEL=info
  - WORKERS=2
```

**Method 2: .env file**
```bash
# Create .env file
LOG_LEVEL=info
WORKERS=2
API_PORT=8000
```

```yaml
# Reference in docker-compose.yml
environment:
  - LOG_LEVEL=${LOG_LEVEL}
  - WORKERS=${WORKERS}
ports:
  - "${API_PORT}:8000"
```

**Method 3: Command line**
```bash
LOG_LEVEL=debug docker-compose up
```

### Available Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `info` | Logging level (debug, info, warning, error) |
| `WORKERS` | `1` | Number of Uvicorn workers |
| `API_PORT` | `8000` | External port mapping |
| `MAX_BATCH_SIZE` | `32` | Maximum batch size for predictions |
| `MODEL_PATH` | `/app/models/transformer/distilbert` | Model directory |

---

## Scaling

### Horizontal Scaling

```bash
# Scale to 3 instances
docker-compose up -d --scale api=3

# Note: You'll need a load balancer (nginx) for this to work properly
```

### Vertical Scaling (Resource Limits)

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # Maximum 4 CPU cores
      memory: 4G       # Maximum 4GB RAM
    reservations:
      cpus: '2.0'      # Minimum 2 CPU cores
      memory: 2G       # Minimum 2GB RAM
```

### Multi-Worker Configuration

```yaml
environment:
  - WORKERS=4  # Run 4 Uvicorn workers
```

**Worker Calculation**:
```
Recommended workers = (2 × CPU cores) + 1
Example: 2 cores → 5 workers
```

---

## Monitoring

### Resource Usage

```bash
# View resource stats
docker-compose stats

# Continuous monitoring
watch docker-compose stats
```

### Health Checks

```bash
# Check health status
docker-compose ps

# View health check logs
docker inspect nlp-api | grep -A 10 Health
```

### Logs Analysis

```bash
# Search for errors
docker-compose logs | grep ERROR

# Count requests
docker-compose logs | grep "POST /predict" | wc -l

# Monitor in real-time
docker-compose logs -f --tail=50
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs api

# Validate configuration
docker-compose config

# Rebuild and start
docker-compose up -d --build --force-recreate
```

### Port Already in Use

```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead

# Or use environment variable
API_PORT=8001 docker-compose up -d
```

### Container Keeps Restarting

```bash
# Check logs for errors
docker-compose logs --tail=100 api

# Run in foreground to see startup issues
docker-compose up api

# Check health status
docker-compose ps
```

### Out of Memory

```bash
# Increase memory limit
deploy:
  resources:
    limits:
      memory: 4G  # Increase to 4GB

# Or use Docker Desktop settings
```

### Network Issues

```bash
# Recreate network
docker-compose down
docker network prune
docker-compose up -d

# Check network connectivity
docker-compose exec api ping google.com
```

### Volume Permissions

```bash
# Fix permissions (Linux/Mac)
sudo chown -R $USER:$USER ./logs

# Windows: Run Docker Desktop as administrator
```

---

## Advanced Usage

### Multiple Compose Files

```bash
# Combine base + override
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Base + production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Custom Networks

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access

services:
  api:
    networks:
      - frontend
      - backend
```

### Health Check Configuration

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s       # Check every 30 seconds
  timeout: 10s        # Timeout after 10 seconds
  retries: 3          # Retry 3 times before unhealthy
  start_period: 40s   # Grace period on startup
```

### Persistent Volumes

```yaml
volumes:
  # Named volume
  model-data:
    driver: local

services:
  api:
    volumes:
      - model-data:/app/models
      - ./logs:/app/logs  # Bind mount
```

---

## Production Best Practices

### 1. Use Specific Image Tags

```yaml
image: cloud-nlp-classifier:1.0.0  # Not :latest
```

### 2. Set Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
```

### 3. Configure Restart Policy

```yaml
restart: always  # or unless-stopped
```

### 4. Use Health Checks

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
```

### 5. Separate Secrets

```bash
# Use .env file (not committed to git)
echo ".env" >> .gitignore
```

### 6. Enable Logging

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 7. Use Networks

```yaml
networks:
  nlp-network:
    driver: bridge
```

---

## Example Workflows

### Development Workflow

```bash
# 1. Start development environment
docker-compose -f docker-compose.dev.yml up

# 2. Make code changes (auto-reload)

# 3. View logs
docker-compose -f docker-compose.dev.yml logs -f

# 4. Stop when done
docker-compose -f docker-compose.dev.yml down
```

### Testing Workflow

```bash
# 1. Build fresh image
docker-compose build --no-cache

# 2. Start services
docker-compose up -d

# 3. Run tests
curl http://localhost:8000/health
python scripts/client_example.py

# 4. Check logs
docker-compose logs

# 5. Clean up
docker-compose down
```

### Production Deployment

```bash
# 1. Build production image
docker-compose -f docker-compose.prod.yml build

# 2. Start services
docker-compose -f docker-compose.prod.yml up -d

# 3. Verify health
docker-compose -f docker-compose.prod.yml ps

# 4. Monitor logs
docker-compose -f docker-compose.prod.yml logs -f

# 5. Scale if needed
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

---

## Quick Reference

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Status
docker-compose ps

# Restart
docker-compose restart

# Rebuild
docker-compose up -d --build

# Shell access
docker-compose exec api /bin/bash

# Stats
docker-compose stats
```

---

## Related Documentation

- [Docker Guide](./DOCKER_GUIDE.md) - Comprehensive Docker documentation
- [Docker Quick Start](./DOCKER_QUICK_START.md) - Quick reference
- [README](../README.md) - Project overview

---

**Docker Compose Version**: 3.8  
**Tested With**: Docker Desktop 4.x, Docker Engine 20.x

---

*Simplified container orchestration for the Cloud NLP Classifier! 🐳*
