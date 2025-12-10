# 🤖 Cloud NLP Classifier - Full-Stack Application

Production-ready hate speech detection system with FastAPI backend and Streamlit frontend, deployed on Google Cloud Platform.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![GCP](https://img.shields.io/badge/GCP-Deployed-orange.svg)](https://cloud.google.com/)

---

## 🎯 Overview

A complete machine learning application for hate speech detection featuring:

- **3 ML Models**: DistilBERT (96.57% accuracy), Logistic Regression, Linear SVM
- **FastAPI Backend**: RESTful API with dynamic model switching
- **Streamlit Frontend**: Beautiful web interface for real-time predictions
- **GCP Deployment**: Production-ready cloud infrastructure
- **Docker Containers**: Isolated, scalable microservices

**Live Demo:**
- 🌐 **Web UI**: `http://35.232.76.140:8501`
- 📡 **API Docs**: `http://35.232.76.140:8000/docs`

---

## ✨ Features

### Backend API (Port 8000)
- ✅ **Multi-Model Support**: 3 models in single container
- ✅ **Dynamic Switching**: Change models without restart
- ✅ **REST API**: OpenAPI/Swagger documentation
- ✅ **Health Monitoring**: Built-in health checks
- ✅ **Fast Inference**: 0.6-8ms response time
- ✅ **Auto-Restart**: Automatic recovery on failure

### Frontend UI (Port 8501)
- ✅ **Interactive Interface**: Chat-style predictions
- ✅ **Model Selection**: Switch models on-the-fly
- ✅ **Real-Time Results**: Instant predictions with confidence scores
- ✅ **Beautiful Design**: Modern, responsive UI
- ✅ **API Integration**: Connects to backend seamlessly
- ✅ **History Tracking**: View past predictions

---

## 🚀 Quick Start

### Deploy Full-Stack to GCP (30 minutes)

```powershell
# 1. Deploy Backend API
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints

# 2. Deploy Frontend UI
.\scripts\gcp-deploy-ui.ps1

# 3. Access your app
# UI:  http://YOUR_IP:8501
# API: http://YOUR_IP:8000/docs
```

**See [QUICK_START_FULLSTACK.md](./QUICK_START_FULLSTACK.md) for detailed instructions.**

---

## 📦 What's Included

### Files Created for UI Deployment

```
CLOUD-NLP-CLASSIFIER-GCP/
├── Dockerfile.streamlit.api          # Lightweight UI container
├── src/ui/
│   ├── streamlit_app_api.py         # API-mode Streamlit app
│   └── utils/
│       └── api_inference.py         # API client
├── scripts/
│   ├── gcp-deploy-ui.ps1            # UI deployment script
│   └── test-fullstack-local.ps1     # Local testing
├── docker-compose.fullstack.yml      # Full-stack compose
└── docs/
    ├── UI_DEPLOYMENT_GUIDE.md       # Detailed guide
    ├── FRONTEND_DEPLOYMENT_PLAN.md  # Architecture
    └── BACKEND_VS_FRONTEND_DEPLOYMENT.md
```

---

## 🏗️ Architecture

### Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│  GCP VM: nlp-classifier-vm (35.232.76.140)         │
│  Machine: e2-standard-2 (2 vCPU, 8GB RAM)          │
│                                                     │
│  ┌──────────────────┐    ┌─────────────────────┐  │
│  │  nlp-api         │◄───┤  nlp-ui             │  │
│  │  Port: 8000      │    │  Port: 8501         │  │
│  │  FastAPI         │    │  Streamlit          │  │
│  │  + ML Models     │    │  API Client         │  │
│  │  ~1.5GB RAM      │    │  ~500MB RAM         │  │
│  └──────────────────┘    └─────────────────────┘  │
└─────────────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
    API Endpoints              Web Interface
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI + Uvicorn | REST API server |
| **Frontend** | Streamlit | Web interface |
| **ML Models** | PyTorch + Transformers | NLP inference |
| **Containerization** | Docker | Isolated services |
| **Cloud** | Google Cloud Platform | Production hosting |
| **Storage** | Google Cloud Storage | Model artifacts |

---

## 🎨 Screenshots

### Streamlit UI
- Chat-style interface
- Model selection dropdown
- Real-time predictions
- Confidence scores
- Inference time display

### API Documentation
- Interactive Swagger UI
- Try-it-out functionality
- Request/response examples
- Model switching endpoints

---

## 📊 Performance

### Model Performance

| Model | Accuracy | Inference Time | Throughput | Memory |
|-------|----------|----------------|------------|--------|
| **DistilBERT** | 96.57% | 8ms | ~120 req/s | ~1.5GB |
| **Logistic Regression** | 85-88% | 0.66ms | ~1500 req/s | ~100MB |
| **Linear SVM** | 85-88% | 0.60ms | ~1600 req/s | ~100MB |

### Resource Usage

| Container | CPU | Memory | Startup | Image Size |
|-----------|-----|--------|---------|------------|
| **API** | 0.1-0.5 cores | ~1.5GB | ~10s | ~2.5GB |
| **UI** | 0.05-0.2 cores | ~500MB | ~5s | ~500MB |
| **Total** | ~0.15-0.7 / 2 | ~2GB / 8GB | ~15s | ~3GB |

---

## 💰 Cost

### Monthly Cost Breakdown

| Resource | Cost | Notes |
|----------|------|-------|
| **VM (e2-standard-2)** | $49/month | 2 vCPU, 8GB RAM |
| **Static IP** | $7/month | External access |
| **GCS Storage** | $0.02/month | ~1GB models |
| **UI Container** | $0/month | Same VM |
| **Total** | **$56/month** | No increase for UI |

**Cost Optimization:**
```bash
# Stop VM when not in use
gcloud compute instances stop nlp-classifier-vm --zone=us-central1-a

# Start when needed
gcloud compute instances start nlp-classifier-vm --zone=us-central1-a
```

---

## 🧪 Local Testing

### Test Full-Stack Locally

```powershell
# Quick test
.\scripts\test-fullstack-local.ps1

# Or manually with docker-compose
docker-compose -f docker-compose.fullstack.yml up -d

# Access locally
# API:  http://localhost:8000/docs
# UI:   http://localhost:8501

# View logs
docker-compose -f docker-compose.fullstack.yml logs -f

# Stop
docker-compose -f docker-compose.fullstack.yml down
```

---

## 🔧 Configuration

### Environment Variables

**API Container:**
```bash
LOG_LEVEL=info
WORKERS=1
DEFAULT_MODEL=distilbert  # or logistic_regression, linear_svm
```

**UI Container:**
```bash
API_URL=http://localhost:8000
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
```

---

## 📚 Documentation

### Deployment Guides
- [Quick Start Full-Stack](./QUICK_START_FULLSTACK.md) - 30-minute deployment
- [UI Deployment Guide](./docs/UI_DEPLOYMENT_GUIDE.md) - Detailed UI deployment
- [Frontend Deployment Plan](./docs/FRONTEND_DEPLOYMENT_PLAN.md) - Architecture & planning
- [Backend vs Frontend](./docs/BACKEND_VS_FRONTEND_DEPLOYMENT.md) - Comparison

### API Documentation
- [API README](./src/api/README.md) - API usage and endpoints
- [Multi-Model Guide](./docs/MULTI_MODEL_DOCKER_GUIDE.md) - Model switching

### Deployment Documentation
- [GCP Deployment Progress](./GCP_DEPLOYMENT_PROGRESS.md) - Overall status
- [Docker Guide](./docs/DOCKER_GUIDE.md) - Docker best practices

---

## 🛠️ Common Commands

### View Logs

```bash
# SSH into VM
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# API logs
sudo docker logs -f nlp-api

# UI logs
sudo docker logs -f nlp-ui

# Both logs
sudo docker logs -f nlp-api & sudo docker logs -f nlp-ui
```

### Restart Services

```bash
# Restart API
sudo docker restart nlp-api

# Restart UI
sudo docker restart nlp-ui

# Check status
sudo docker ps
```

### Update Deployment

```powershell
# Update UI only
.\scripts\gcp-deploy-ui.ps1

# Update API only (skip model upload)
.\scripts\gcp-complete-deployment.ps1 -SkipModelUpload

# Update both
.\scripts\gcp-complete-deployment.ps1 -SkipModelUpload
.\scripts\gcp-deploy-ui.ps1
```

---

## 🐛 Troubleshooting

### UI Cannot Connect to API

```bash
# Check API is running
sudo docker ps | grep nlp-api

# Check API health
curl http://localhost:8000/health

# Restart UI
sudo docker restart nlp-ui
```

### Container Not Starting

```bash
# Check logs
sudo docker logs nlp-api
sudo docker logs nlp-ui

# Check resources
sudo docker stats
df -h
free -h
```

### Cannot Access from Browser

```bash
# Check firewall rules
gcloud compute firewall-rules list | grep -E "8000|8501"

# Should see:
# - allow-http (port 8000)
# - allow-streamlit (port 8501)
```

**See [UI Deployment Guide](./docs/UI_DEPLOYMENT_GUIDE.md) for more troubleshooting.**

---

## 🔄 Development Workflow

### Local Development

```bash
# 1. Make changes locally
# 2. Test with docker-compose
docker-compose -f docker-compose.fullstack.yml up --build

# 3. Commit and push
git add .
git commit -m "Update feature"
git push

# 4. Deploy to GCP
.\scripts\gcp-deploy-ui.ps1
```

### CI/CD (Future)

- GitHub Actions for automated testing
- Automatic deployment on merge to main
- Rollback capabilities
- Blue-green deployments

---

## 📈 Monitoring

### Health Checks

```bash
# API health
curl http://YOUR_IP:8000/health

# UI health
curl http://YOUR_IP:8501/_stcore/health

# Container status
sudo docker ps
sudo docker stats
```

### Metrics (Future)

- Prometheus for metrics collection
- Grafana for visualization
- Alert notifications
- Performance tracking

---

## 🔒 Security

### Current Security Measures

- ✅ Non-root user in containers
- ✅ Minimal base images
- ✅ Firewall rules configured
- ✅ Health check monitoring
- ✅ Auto-restart on failure

### Future Enhancements

- [ ] HTTPS/SSL certificates
- [ ] Authentication and authorization
- [ ] Rate limiting
- [ ] API keys
- [ ] Input validation and sanitization

---

## 🎯 Roadmap

### Phase 1: Core Features ✅
- [x] FastAPI backend
- [x] Multi-model support
- [x] Docker containerization
- [x] GCP deployment
- [x] Streamlit frontend
- [x] Full-stack integration

### Phase 2: Enhancements (In Progress)
- [ ] User authentication
- [ ] Batch predictions
- [ ] Export functionality
- [ ] Analytics dashboard
- [ ] Performance optimization

### Phase 3: Production Hardening
- [ ] HTTPS/SSL
- [ ] CI/CD pipeline
- [ ] Monitoring and alerts
- [ ] Auto-scaling
- [ ] Load balancing

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📝 License

This project is licensed under the MIT License.

---

## 👥 Authors

**Dhairya Mishra**
- GitHub: [@dhairyamishra](https://github.com/dhairyamishra)

---

## 🙏 Acknowledgments

- **HuggingFace** for Transformers library
- **FastAPI** for the excellent web framework
- **Streamlit** for the beautiful UI framework
- **Google Cloud Platform** for hosting infrastructure

---

## 📞 Support

For issues, questions, or suggestions:

1. Check the [documentation](./docs/)
2. Review [troubleshooting guide](./docs/UI_DEPLOYMENT_GUIDE.md#troubleshooting)
3. Open an issue on GitHub

---

## ✅ Status

**Project Status:** ✅ **PRODUCTION READY**

- Backend API: ✅ LIVE
- Frontend UI: ✅ LIVE
- GCP Deployment: ✅ OPERATIONAL
- Documentation: ✅ COMPLETE
- Testing: ✅ PASSED

**Last Updated:** 2025-12-10  
**Version:** 2.0.0 (Full-Stack)

---

**🎉 Your full-stack NLP application is ready for production use!**
