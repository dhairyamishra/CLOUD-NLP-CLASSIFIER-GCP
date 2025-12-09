# 🐳 Docker Guide for Streamlit UI

## 📋 Overview

This guide covers Docker deployment for the Streamlit interactive UI of the Cloud NLP Classifier project.

---

## 🎯 Quick Start

### Option 1: Run UI Only

```bash
# Build and run Streamlit UI
docker-compose -f docker-compose.ui.yml up -d

# Access at http://localhost:8501
```

### Option 2: Run Both API and UI

```bash
# Build and run both services
docker-compose up -d

# Access:
# - API: http://localhost:8000
# - UI:  http://localhost:8501
```

### Option 3: Build Manually

```bash
# Build Streamlit UI image
docker build -f Dockerfile.streamlit -t cloud-nlp-classifier-ui:latest .

# Run container
docker run -d -p 8501:8501 --name nlp-ui cloud-nlp-classifier-ui:latest

# Access at http://localhost:8501
```

---

## 🏗️ Architecture

### Container Structure

```
Dockerfile.streamlit
├── Base: python:3.11-slim
├── Size: ~2.5 GB (with models)
├── Port: 8501
├── User: appuser (non-root)
├── PYTHONPATH: /app (for module imports)
└── Health Check: /_stcore/health
```

**Key Configuration:**
- `PYTHONPATH=/app` ensures `src` module is importable
- Non-root user (UID 1000) for security
- Optimized layer caching for fast rebuilds

### Services

```
docker-compose.yml
├── api (FastAPI)      → Port 8000
├── ui (Streamlit)     → Port 8501
└── nlp-network        → Bridge network
```

---

## 📦 Build Options

### Production Build

```bash
# Build optimized image
docker build -f Dockerfile.streamlit \
  -t cloud-nlp-classifier-ui:latest \
  --no-cache .

# Build time: ~5-8 minutes (first build)
# Image size: ~2.5 GB
```

### Development Build

```bash
# Build with cache
docker build -f Dockerfile.streamlit \
  -t cloud-nlp-classifier-ui:dev .

# Build time: ~1-2 minutes (cached)
```

### Multi-stage Build (Optional)

```bash
# For smaller image size
docker build -f Dockerfile.streamlit \
  --target production \
  -t cloud-nlp-classifier-ui:slim .
```

---

## 🚀 Running Containers

### Using Docker Compose (Recommended)

#### Start All Services

```bash
# Start API + UI
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f ui

# Stop services
docker-compose down
```

#### Start UI Only

```bash
# Development mode with hot reload
docker-compose -f docker-compose.ui.yml up

# Production mode
docker-compose up ui
```

#### Start with Custom Config

```bash
# Override environment variables
docker-compose up -d \
  -e STREAMLIT_SERVER_PORT=8502

# Use specific compose file
docker-compose -f docker-compose.yml \
  -f docker-compose.ui.yml up -d
```

### Using Docker Run

#### Basic Run

```bash
docker run -d \
  --name nlp-ui \
  -p 8501:8501 \
  cloud-nlp-classifier-ui:latest
```

#### Run with Volume Mounts

```bash
docker run -d \
  --name nlp-ui \
  -p 8501:8501 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/src/ui:/app/src/ui \
  cloud-nlp-classifier-ui:latest
```

#### Run with Environment Variables

```bash
docker run -d \
  --name nlp-ui \
  -p 8501:8501 \
  -e STREAMLIT_SERVER_PORT=8501 \
  -e STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
  cloud-nlp-classifier-ui:latest
```

#### Run with Resource Limits

```bash
docker run -d \
  --name nlp-ui \
  -p 8501:8501 \
  --cpus="2.0" \
  --memory="2.5g" \
  cloud-nlp-classifier-ui:latest
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STREAMLIT_SERVER_PORT` | `8501` | Port for Streamlit server |
| `STREAMLIT_SERVER_ADDRESS` | `0.0.0.0` | Bind address |
| `STREAMLIT_SERVER_HEADLESS` | `true` | Run in headless mode |
| `STREAMLIT_BROWSER_GATHER_USAGE_STATS` | `false` | Disable telemetry |
| `STREAMLIT_SERVER_RUN_ON_SAVE` | `false` | Auto-reload on file changes |

### Volume Mounts

```yaml
volumes:
  # Models directory (recommended for production)
  - ./models:/app/models

  # Source code (for development hot reload)
  - ./src/ui:/app/src/ui

  # Configuration
  - ./.streamlit:/app/.streamlit
  - ./config:/app/config
```

### Port Mapping

```yaml
ports:
  - "8501:8501"  # Streamlit UI
  - "8000:8000"  # FastAPI (if running both)
```

---

## 🧪 Testing

### Health Check

```bash
# Check container health
docker ps --filter name=nlp-ui

# Test health endpoint
curl http://localhost:8501/_stcore/health

# Expected: HTTP 200 OK
```

### Functionality Test

```bash
# Access UI in browser
open http://localhost:8501

# Or use curl
curl -I http://localhost:8501

# Expected: HTTP 200 OK
```

### Load Test

```bash
# Check resource usage
docker stats nlp-ui

# Expected:
# - CPU: < 50% (idle)
# - Memory: ~1.5-2GB
```

---

## 📊 Monitoring

### View Logs

```bash
# Follow logs
docker logs -f nlp-ui

# Last 100 lines
docker logs --tail 100 nlp-ui

# Since specific time
docker logs --since 10m nlp-ui
```

### Resource Usage

```bash
# Real-time stats
docker stats nlp-ui

# Container inspect
docker inspect nlp-ui
```

### Health Status

```bash
# Check health
docker inspect --format='{{.State.Health.Status}}' nlp-ui

# Health log
docker inspect --format='{{json .State.Health}}' nlp-ui | jq
```

---

## 🐛 Troubleshooting

### Issue 1: Container Won't Start

**Symptoms:**
```
Error: Container nlp-ui exited with code 1
```

**Solutions:**
```bash
# Check logs
docker logs nlp-ui

# Common causes:
# 1. Port already in use
lsof -i :8501  # Check port
docker stop $(docker ps -q --filter "publish=8501")  # Stop conflicting container

# 2. Missing models
ls -la models/  # Verify models exist

# 3. Permission issues
docker run --rm -it cloud-nlp-classifier-ui:latest ls -la /app/models
```

### Issue 2: UI Not Accessible

**Symptoms:**
```
Cannot connect to http://localhost:8501
```

**Solutions:**
```bash
# 1. Check container is running
docker ps | grep nlp-ui

# 2. Check port mapping
docker port nlp-ui

# 3. Check firewall
# Windows: Allow port 8501 in Windows Firewall
# Linux: sudo ufw allow 8501

# 4. Try different port
docker run -d -p 8502:8501 --name nlp-ui-alt cloud-nlp-classifier-ui:latest
```

### Issue 3: Module Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'src'
```

**Solutions:**
```bash
# 1. Verify PYTHONPATH is set
docker exec nlp-ui env | grep PYTHONPATH
# Expected: PYTHONPATH=/app

# 2. Check Dockerfile has PYTHONPATH
grep PYTHONPATH Dockerfile.streamlit
# Expected: ENV PYTHONPATH=/app

# 3. Rebuild with latest Dockerfile
docker build -f Dockerfile.streamlit \
  --no-cache \
  -t cloud-nlp-classifier-ui:latest .
```

### Issue 4: Models Not Loading

**Symptoms:**
```
⚠️ No models found!
```

**Solutions:**
```bash
# 1. Check models in container
docker exec nlp-ui ls -la /app/models

# 2. Mount models directory
docker run -d -p 8501:8501 \
  -v $(pwd)/models:/app/models \
  --name nlp-ui cloud-nlp-classifier-ui:latest

# 3. Rebuild with models
docker build -f Dockerfile.streamlit \
  --no-cache \
  -t cloud-nlp-classifier-ui:latest .
```

### Issue 4: High Memory Usage

**Symptoms:**
```
Container using > 3GB memory
```

**Solutions:**
```bash
# 1. Set memory limit
docker update --memory="2.5g" nlp-ui

# 2. Restart container
docker restart nlp-ui

# 3. Use docker-compose with limits
docker-compose up -d  # Uses limits from compose file
```

### Issue 5: Slow Performance

**Symptoms:**
```
Inference taking > 2 seconds
```

**Solutions:**
```bash
# 1. Check CPU allocation
docker update --cpus="2.0" nlp-ui

# 2. Use GPU (if available)
docker run -d -p 8501:8501 \
  --gpus all \
  --name nlp-ui-gpu \
  cloud-nlp-classifier-ui:latest

# 3. Check model loading
docker logs nlp-ui | grep "Loaded"
```

---

## 🔒 Security

### Best Practices

1. **Non-root User**
   ```dockerfile
   USER appuser  # Already configured
   ```

2. **Read-only Filesystem**
   ```bash
   docker run -d -p 8501:8501 \
     --read-only \
     --tmpfs /tmp \
     --name nlp-ui cloud-nlp-classifier-ui:latest
   ```

3. **No Privileged Mode**
   ```bash
   # Never use --privileged
   # Never use --cap-add=ALL
   ```

4. **Network Isolation**
   ```bash
   # Use custom network
   docker network create nlp-secure
   docker run -d --network nlp-secure nlp-ui
   ```

5. **Secrets Management**
   ```bash
   # Use Docker secrets (Swarm mode)
   docker secret create api_key api_key.txt
   docker service create --secret api_key nlp-ui
   ```

---

## 🚀 Production Deployment

### Docker Compose Production

```bash
# Use production compose file
docker-compose -f docker-compose.yml up -d

# Scale UI instances
docker-compose up -d --scale ui=3

# Update without downtime
docker-compose up -d --no-deps --build ui
```

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml nlp-stack

# Scale service
docker service scale nlp-stack_ui=3

# Update service
docker service update --image cloud-nlp-classifier-ui:v2 nlp-stack_ui
```

### Kubernetes (Optional)

```bash
# Create deployment
kubectl create deployment nlp-ui \
  --image=cloud-nlp-classifier-ui:latest

# Expose service
kubectl expose deployment nlp-ui \
  --type=LoadBalancer \
  --port=8501

# Scale
kubectl scale deployment nlp-ui --replicas=3
```

---

## 📈 Performance Optimization

### Image Size Optimization

```dockerfile
# Use multi-stage build
FROM python:3.11-slim as builder
# ... build steps ...

FROM python:3.11-slim
COPY --from=builder /app /app
```

### Layer Caching

```bash
# Order Dockerfile for better caching:
# 1. System dependencies (rarely change)
# 2. Python requirements (change occasionally)
# 3. Application code (change frequently)
```

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2.5G
    reservations:
      cpus: '1.0'
      memory: 1.5G
```

---

## 🔄 Updates & Maintenance

### Update Container

```bash
# Pull latest code
git pull

# Rebuild image
docker-compose build ui

# Restart with new image
docker-compose up -d ui
```

### Backup Models

```bash
# Backup models from container
docker cp nlp-ui:/app/models ./models-backup

# Restore models
docker cp ./models-backup nlp-ui:/app/models
```

### Clean Up

```bash
# Stop and remove container
docker-compose down

# Remove images
docker rmi cloud-nlp-classifier-ui:latest

# Clean up volumes
docker volume prune

# Clean up everything
docker system prune -a
```

---

## 📚 Additional Resources

### Documentation
- [Streamlit Docker Docs](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Related Files
- `Dockerfile.streamlit` - UI container definition
- `docker-compose.yml` - Multi-service orchestration
- `docker-compose.ui.yml` - UI development setup
- `.dockerignore` - Build context optimization

---

## 🎯 Quick Reference

### Common Commands

```bash
# Build
docker-compose build ui

# Start
docker-compose up -d ui

# Stop
docker-compose stop ui

# Restart
docker-compose restart ui

# Logs
docker-compose logs -f ui

# Shell access
docker exec -it nlp-ui bash

# Health check
curl http://localhost:8501/_stcore/health

# Stats
docker stats nlp-ui
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-09  
**Status**: Production Ready ✅
