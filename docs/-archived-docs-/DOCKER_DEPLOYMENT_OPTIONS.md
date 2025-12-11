# Docker Deployment Options Guide

## 🎯 Overview

Multiple Docker Compose configurations for different deployment scenarios.

---

## 📋 Available Configurations

### **1. Full Stack (API + UI)** - Recommended ⭐
Deploy both backend API and frontend UI together.

**File:** `docker-compose.full.yml`

```powershell
# Deploy everything
docker-compose -f docker-compose.full.yml up -d

# With rebuild
docker-compose -f docker-compose.full.yml up -d --build

# Stop
docker-compose -f docker-compose.full.yml down
```

**Services:**
- ✅ FastAPI Backend (port 8000)
- ✅ Streamlit UI (port 8501)
- ✅ Shared network for communication
- ✅ Health checks enabled

---

### **2. API Only**
Deploy just the backend API (for programmatic access).

**File:** `docker-compose.api-only.yml`

```powershell
docker-compose -f docker-compose.api-only.yml up -d
```

**Services:**
- ✅ FastAPI Backend (port 8000)
- ✅ Swagger UI at /docs
- ✅ 3 models available

---

### **3. UI Only**
Deploy just the Streamlit UI (requires API running separately).

**File:** `docker-compose.ui.yml`

```powershell
docker-compose -f docker-compose.ui.yml up -d
```

**Services:**
- ✅ Streamlit UI (port 8501)
- ⚠️ Requires API on port 8000

---

## 🚀 Quick Start with Automated Script

### **PowerShell Script** (Recommended)

```powershell
# Full deployment (API + UI)
.\scripts\docker-deploy.ps1 -Mode full

# With specific model
.\scripts\docker-deploy.ps1 -Mode full -DefaultModel logistic_regression

# Force rebuild
.\scripts\docker-deploy.ps1 -Mode full -Build

# API only
.\scripts\docker-deploy.ps1 -Mode api-only

# UI only
.\scripts\docker-deploy.ps1 -Mode ui-only

# Stop all
.\scripts\docker-deploy.ps1 -Mode stop

# View logs
.\scripts\docker-deploy.ps1 -Mode logs -Follow

# Check status
.\scripts\docker-deploy.ps1 -Mode status
```

---

## 📊 Comparison Table

| Configuration | API | UI | Use Case | Command |
|---------------|-----|----|-----------| --------|
| **Full Stack** | ✅ | ✅ | Complete application | `docker-compose -f docker-compose.full.yml up -d` |
| **API Only** | ✅ | ❌ | Backend development, REST API | `docker-compose -f docker-compose.api-only.yml up -d` |
| **UI Only** | ❌ | ✅ | Frontend development | `docker-compose -f docker-compose.ui.yml up -d` |

---

## 🎮 Common Operations

### **Start Services**

```powershell
# Full stack
docker-compose -f docker-compose.full.yml up -d

# With logs
docker-compose -f docker-compose.full.yml up

# Rebuild and start
docker-compose -f docker-compose.full.yml up -d --build
```

### **Stop Services**

```powershell
# Stop containers (keep volumes)
docker-compose -f docker-compose.full.yml stop

# Stop and remove containers
docker-compose -f docker-compose.full.yml down

# Stop and remove everything (including volumes)
docker-compose -f docker-compose.full.yml down -v
```

### **View Logs**

```powershell
# All services
docker-compose -f docker-compose.full.yml logs

# Follow logs
docker-compose -f docker-compose.full.yml logs -f

# Specific service
docker-compose -f docker-compose.full.yml logs -f api
docker-compose -f docker-compose.full.yml logs -f ui

# Last 50 lines
docker-compose -f docker-compose.full.yml logs --tail=50
```

### **Check Status**

```powershell
# List running containers
docker-compose -f docker-compose.full.yml ps

# Check health
curl http://localhost:8000/health
curl http://localhost:8501/_stcore/health
```

### **Restart Services**

```powershell
# Restart all
docker-compose -f docker-compose.full.yml restart

# Restart specific service
docker-compose -f docker-compose.full.yml restart api
docker-compose -f docker-compose.full.yml restart ui
```

---

## 🔧 Configuration Options

### **Environment Variables**

Set in compose file or via command line:

```yaml
environment:
  - DEFAULT_MODEL=distilbert          # or logistic_regression, linear_svm
  - LOG_LEVEL=info                    # debug, info, warning, error
  - STREAMLIT_SERVER_PORT=8501
```

**Command line:**
```powershell
$env:DEFAULT_MODEL="logistic_regression"
docker-compose -f docker-compose.full.yml up -d
```

### **Resource Limits**

Adjust in compose file:

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

## 🌐 Access Points

After deployment:

| Service | URL | Description |
|---------|-----|-------------|
| **Streamlit UI** | http://localhost:8501 | Interactive web interface |
| **API** | http://localhost:8000 | REST API endpoint |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **API ReDoc** | http://localhost:8000/redoc | Alternative docs |
| **Health Check** | http://localhost:8000/health | API health status |

---

## 🐛 Troubleshooting

### **Port Already in Use**

```powershell
# Find process using port
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or change port in compose file
ports:
  - "9000:8000"  # Use port 9000 instead
```

### **Container Won't Start**

```powershell
# Check logs
docker-compose -f docker-compose.full.yml logs api
docker-compose -f docker-compose.full.yml logs ui

# Rebuild
docker-compose -f docker-compose.full.yml up -d --build --force-recreate
```

### **Models Not Found**

```powershell
# Ensure models are trained
python run_baselines.py
python run_transformer.py

# Rebuild with models
docker-compose -f docker-compose.full.yml build --no-cache
```

### **UI Can't Connect to API**

```powershell
# Check API is running
curl http://localhost:8000/health

# Check network
docker network inspect nlp-network

# Restart both
docker-compose -f docker-compose.full.yml restart
```

---

## 📈 Performance Tips

### **1. Use Pre-built Images**

```powershell
# Build once
docker-compose -f docker-compose.full.yml build

# Run without rebuilding
docker-compose -f docker-compose.full.yml up -d
```

### **2. Choose Right Model**

```powershell
# Fast inference (10x faster)
$env:DEFAULT_MODEL="logistic_regression"
docker-compose -f docker-compose.full.yml up -d

# Best accuracy
$env:DEFAULT_MODEL="distilbert"
docker-compose -f docker-compose.full.yml up -d
```

### **3. Adjust Resources**

Edit compose file based on your system:

```yaml
# For low-memory systems
deploy:
  resources:
    limits:
      memory: 1.5G

# For high-performance
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 4G
```

---

## 🎯 Best Practices

1. **Development**: Use `docker-compose.full.yml` with volume mounts for hot reload
2. **Testing**: Use `docker-compose.full.yml` without volumes
3. **Production**: Use `docker-compose.full.yml` with resource limits and health checks
4. **CI/CD**: Use `docker-compose.api-only.yml` for automated testing

---

## 📚 Additional Resources

- **Main README**: `../README.md`
- **Multi-Model Guide**: `MULTI_MODEL_DOCKER_GUIDE.md`
- **Streamlit Guide**: `DOCKER_STREAMLIT_GUIDE.md`
- **API Documentation**: http://localhost:8000/docs

---

## ✅ Quick Reference

```powershell
# Deploy everything
.\scripts\docker-deploy.ps1 -Mode full

# Stop everything
.\scripts\docker-deploy.ps1 -Mode stop

# View status
.\scripts\docker-deploy.ps1 -Mode status

# View logs
.\scripts\docker-deploy.ps1 -Mode logs -Follow

# Restart
.\scripts\docker-deploy.ps1 -Mode restart
```

---

**Built with ❤️ for flexible Docker deployment**
