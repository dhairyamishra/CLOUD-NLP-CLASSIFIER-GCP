# Docker Compose Quick Start Guide

**Last Updated:** 2025-12-10  
**Status:** ✅ READY  
**Components:** Streamlit UI + FastAPI Backend + 4 ML Models

---

## Overview

This guide shows you how to quickly deploy the complete Cloud NLP Classifier stack (UI + API) using Docker Compose with support for all 4 models including the toxicity classifier.

### What You Get

- **Streamlit UI** (Port 8501) - Interactive web interface
- **FastAPI Backend** (Port 8000) - REST API with 4 models
- **4 ML Models:**
  1. DistilBERT - Sentiment classification (90-93% accuracy)
  2. Toxicity Classifier - Multi-label toxicity detection (95% accuracy)
  3. Logistic Regression - Fast sentiment (85-88% accuracy)
  4. Linear SVM - Ultra-fast sentiment (85-88% accuracy)

---

## Prerequisites

- **Docker Desktop** installed and running
- **docker-compose** installed (usually comes with Docker Desktop)
- **4-6 GB RAM** available
- **10 GB disk space** for images

---

## Quick Start (3 Steps)

### 1. Build and Start

**Option A: Using the PowerShell script (Recommended for Windows)**
```powershell
.\scripts\docker-compose-up.ps1 -Build
```

**Option B: Using docker-compose directly**
```bash
docker-compose up -d --build
```

### 2. Access the Applications

Once started, open your browser:

- **Streamlit UI:** http://localhost:8501
- **FastAPI Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health

### 3. Stop the Services

```powershell
# Using the script
.\scripts\docker-compose-up.ps1 -Down

# Or directly
docker-compose down
```

---

## Detailed Usage

### Build Options

```powershell
# First time build (with cache)
.\scripts\docker-compose-up.ps1 -Build

# Clean rebuild (no cache) - use if you have issues
.\scripts\docker-compose-up.ps1 -Rebuild

# Just start (if already built)
.\scripts\docker-compose-up.ps1
```

### View Logs

```powershell
# All services
.\scripts\docker-compose-up.ps1 -Logs

# Specific service (API)
.\scripts\docker-compose-up.ps1 -Logs -Service api

# Specific service (UI)
.\scripts\docker-compose-up.ps1 -Logs -Service ui
```

### Service Management

```powershell
# Stop services
.\scripts\docker-compose-up.ps1 -Down

# Restart services
docker-compose restart

# Check status
docker-compose ps

# View resource usage
docker stats
```

---

## Using the UI

### 1. Open Streamlit UI
Navigate to http://localhost:8501

### 2. Select a Model
Choose from the sidebar:
- 🔵 Logistic Regression (Baseline)
- 🟢 Linear SVM (Baseline)
- 🟣 DistilBERT (Transformer)
- 🟠 Toxicity Classifier (Multi-label)

### 3. Analyze Text
- Type your message in the text area
- Click "🚀 Analyze"
- View results with confidence scores and probabilities

### 4. Chat History
- All analyses are saved in chat history
- Clear history with "🗑️ Clear Chat History" button

---

## Using the API

### List Available Models

```bash
curl http://localhost:8000/models
```

### Switch Models

```bash
curl -X POST http://localhost:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "toxicity"}'
```

### Make Predictions

**Sentiment Analysis:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!"}'
```

**Toxicity Detection:**
```bash
# First switch to toxicity model
curl -X POST http://localhost:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "toxicity"}'

# Then predict
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test message"}'
```

---

## Configuration

### Environment Variables

Edit `docker-compose.yml` to customize:

```yaml
services:
  api:
    environment:
      - DEFAULT_MODEL=distilbert  # Change default model
      - LOG_LEVEL=info            # Logging level
      - WORKERS=1                 # Number of workers
```

### Resource Limits

Adjust memory and CPU limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 3G    # Increase if needed
    reservations:
      cpus: '1.0'
      memory: 2G
```

---

## Troubleshooting

### Issue: Services won't start

**Check Docker is running:**
```powershell
docker info
```

**Check logs:**
```powershell
docker-compose logs
```

### Issue: Out of memory

**Increase Docker memory:**
1. Open Docker Desktop
2. Settings → Resources
3. Increase Memory to 6-8 GB
4. Apply & Restart

**Or reduce models loaded:**
- Comment out toxicity model in Dockerfile
- Rebuild: `.\scripts\docker-compose-up.ps1 -Rebuild`

### Issue: Port already in use

**Change ports in docker-compose.yml:**
```yaml
ports:
  - "8502:8501"  # Change 8501 to 8502
  - "8001:8000"  # Change 8000 to 8001
```

### Issue: Build fails

**Clean rebuild:**
```powershell
# Remove old containers and images
docker-compose down --rmi all

# Rebuild from scratch
.\scripts\docker-compose-up.ps1 -Rebuild
```

### Issue: Toxicity model not loading

**Check logs:**
```powershell
docker-compose logs api | Select-String "toxicity"
```

**Expected behavior:**
- If toxicity model fails to load, it's skipped gracefully
- Other 3 models will still work
- Check if `models/toxicity_multi_head/` exists

---

## Performance Tips

### 1. Allocate Enough Resources

**Recommended:**
- CPU: 2+ cores
- RAM: 4-6 GB
- Disk: 10 GB

### 2. Use Fast Models for Development

Switch to faster models for quick testing:
```bash
curl -X POST http://localhost:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "logistic_regression"}'
```

### 3. Monitor Resource Usage

```bash
# Real-time stats
docker stats

# Container resource usage
docker-compose top
```

---

## Production Deployment

### Using docker-compose.prod.yml

For production with additional features:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Enable Monitoring (Optional)

Uncomment in `docker-compose.yml`:
- Prometheus (metrics)
- Grafana (dashboards)
- Nginx (reverse proxy)

### SSL/TLS

Add nginx with SSL certificates:
1. Uncomment nginx service
2. Add SSL certificates to `./ssl/`
3. Configure nginx.conf

---

## Architecture

```
┌─────────────────────────────────────────────┐
│         Docker Compose Network              │
│                                             │
│  ┌──────────────┐      ┌─────────────────┐ │
│  │ Streamlit UI │      │   FastAPI       │ │
│  │  Port 8501   │◄────►│   Port 8000     │ │
│  │              │      │                 │ │
│  │  - Chat UI   │      │  - 4 Models     │ │
│  │  - Model     │      │  - REST API     │ │
│  │    Selector  │      │  - Health Check │ │
│  └──────────────┘      └─────────────────┘ │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │         Shared Models Volume        │   │
│  │  - DistilBERT                       │   │
│  │  - Toxicity Classifier              │   │
│  │  - Logistic Regression              │   │
│  │  - Linear SVM                       │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## Next Steps

1. **Test the deployment:**
   ```powershell
   .\scripts\docker-compose-up.ps1 -Build
   ```

2. **Open the UI:**
   - Navigate to http://localhost:8501
   - Try different models
   - Test with various inputs

3. **Explore the API:**
   - Visit http://localhost:8000/docs
   - Try the interactive API documentation
   - Test model switching

4. **Monitor performance:**
   ```bash
   docker stats
   ```

5. **Review logs:**
   ```powershell
   .\scripts\docker-compose-up.ps1 -Logs
   ```

---

## Common Commands Reference

| Task | Command |
|------|---------|
| **Build and start** | `.\scripts\docker-compose-up.ps1 -Build` |
| **Start (already built)** | `.\scripts\docker-compose-up.ps1` |
| **Stop** | `.\scripts\docker-compose-up.ps1 -Down` |
| **View logs** | `.\scripts\docker-compose-up.ps1 -Logs` |
| **Rebuild (clean)** | `.\scripts\docker-compose-up.ps1 -Rebuild` |
| **Check status** | `docker-compose ps` |
| **Restart** | `docker-compose restart` |
| **Remove everything** | `docker-compose down --rmi all -v` |

---

## Support

### Documentation
- Full Docker Guide: `docs/DOCKER_GUIDE.md`
- Toxicity Deployment: `docs/DOCKER_TOXICITY_DEPLOYMENT.md`
- API Documentation: http://localhost:8000/docs (when running)

### Logs
```powershell
# All logs
docker-compose logs

# API logs only
docker-compose logs api

# UI logs only
docker-compose logs ui

# Follow logs in real-time
docker-compose logs -f
```

---

## Conclusion

You now have a complete NLP classification stack running with Docker Compose! The system includes:

- ✅ Interactive Streamlit UI
- ✅ Production-ready FastAPI backend
- ✅ 4 ML models (including toxicity classifier)
- ✅ Easy deployment and management
- ✅ Health checks and monitoring

**Status:** ✅ Production Ready  
**Testing:** ✅ Comprehensive  
**Documentation:** ✅ Complete
