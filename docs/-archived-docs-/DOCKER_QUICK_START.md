# 🚀 Docker Quick Start Guide

A quick reference for building and running the Cloud NLP Classifier container.

## Prerequisites Checklist

- [ ] Docker installed and running
- [ ] Model trained at `models/transformer/distilbert/`
- [ ] At least 3 GB free disk space

## 5-Minute Quick Start

### Step 1: Build the Image (5-10 minutes)

```bash
docker build -t cloud-nlp-classifier .
```

**What's happening?**
- Installing Python 3.11 and dependencies
- Copying your trained model
- Setting up security and health checks
- Final image: ~2.1 GB

### Step 2: Run the Container (5 seconds)

```bash
docker run -d -p 8000:8000 --name nlp-api cloud-nlp-classifier
```

**What's happening?**
- Container starts in background (`-d`)
- Port 8000 mapped to your machine
- Named `nlp-api` for easy management

### Step 3: Test the API (instant)

```bash
# Health check
curl http://localhost:8000/health

# Make a prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test message"}'
```

**Expected response:**
```json
{
  "predicted_label": "neither",
  "confidence": 0.95,
  "all_scores": {...},
  "inference_time_ms": 45.2
}
```

### Step 4: View Logs

```bash
docker logs -f nlp-api
```

Press `Ctrl+C` to stop following logs.

### Step 5: Stop and Clean Up

```bash
# Stop the container
docker stop nlp-api

# Remove the container
docker rm nlp-api

# (Optional) Remove the image
docker rmi cloud-nlp-classifier
```

---

## Common Commands

```bash
# View running containers
docker ps

# View all containers
docker ps -a

# Check container health
docker inspect --format='{{.State.Health.Status}}' nlp-api

# Execute command in container
docker exec -it nlp-api /bin/bash

# View resource usage
docker stats nlp-api

# Restart container
docker restart nlp-api
```

---

## Troubleshooting

### Build fails with "model not found"
```bash
# Train the model first
python run_transformer.py

# Verify it exists
ls models/transformer/distilbert/model.safetensors
```

### Port 8000 already in use
```bash
# Use a different port
docker run -d -p 8001:8000 --name nlp-api cloud-nlp-classifier
```

### Container exits immediately
```bash
# Check the logs
docker logs nlp-api

# Run interactively to debug
docker run -it -p 8000:8000 cloud-nlp-classifier
```

### Out of memory
```bash
# Increase Docker memory in Settings → Resources → Memory
# Or run with explicit limit
docker run -d -p 8000:8000 --memory="2g" --name nlp-api cloud-nlp-classifier
```

---

## Next Steps

1. **Test thoroughly**: Try different text inputs
2. **Check documentation**: See `docs/DOCKER_GUIDE.md` for advanced usage
3. **Deploy to cloud**: Ready for GCP Cloud Run deployment
4. **Monitor performance**: Use `docker stats` to track resources

---

## Interactive API Documentation

Once running, open in your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

**Need help?** See the comprehensive [Docker Guide](./DOCKER_GUIDE.md) for detailed documentation.
