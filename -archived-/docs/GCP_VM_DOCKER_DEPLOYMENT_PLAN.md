# 🚀 GCP Compute Engine VM + Docker Compose Deployment Plan

## 📋 Executive Summary

**Deployment Strategy**: Single GCP Compute Engine VM with Docker Compose  
**Complexity**: ⭐⭐ Low (Much simpler than GKE)  
**Current Status**: ✅ Production Ready (Docker images tested locally)  
**Estimated Time**: 3-5 hours (vs 15-25 hours for GKE)  
**Estimated Cost**: $50-80/month (vs $150-180 for GKE)  
**Maintenance**: You own all ops (updates, scaling, backups)

---

## ✅ Why This Approach?

### Advantages
- ✅ **Simple Setup**: Just SSH and run docker-compose
- ✅ **Persistent Storage**: Native disk mounting (no PVC complexity)
- ✅ **No Cold Starts**: Always-on, instant response
- ✅ **Full Control**: Root access, install anything
- ✅ **Lower Cost**: ~$50-80/month vs $150-180 for GKE
- ✅ **Easier Debugging**: Direct access to logs, files, containers
- ✅ **Your Existing Setup**: Already have docker-compose.yml working!

### Trade-offs
- ⚠️ **Manual Scaling**: No auto-scaling (but can upgrade VM size)
- ⚠️ **Single Point of Failure**: One VM (can add load balancer later)
- ⚠️ **Manual Updates**: You handle OS updates, security patches
- ⚠️ **Manual Backups**: You own backup strategy
- ⚠️ **Ops Responsibility**: You're on-call for issues

### Perfect For:
- ✅ MVP and early-stage deployments
- ✅ Predictable traffic patterns
- ✅ Small to medium workloads (<1000 req/hour)
- ✅ Learning and experimentation
- ✅ Cost-conscious deployments

---

## 🎯 Architecture Overview

```
Internet
    ↓
External IP (Static)
    ↓
GCP Firewall (Ports 80, 443, 8000, 8501)
    ↓
Compute Engine VM (e2-standard-2)
    ↓
Docker Compose
    ├── API Container (Port 8000)
    ├── UI Container (Port 8501)
    └── (Optional) Nginx Reverse Proxy (Port 80/443)
    ↓
Persistent Disk (50GB SSD)
    ├── /models (3-5GB)
    ├── /logs (1-2GB)
    └── /data (1GB)
```

---

## 📝 DETAILED TASK LIST

### **PHASE 1: GCP Project Setup** (Est. 15-30 min)

#### Task 1.1: GCP Project Configuration
- [ ] Create or select GCP project
- [ ] Enable billing
- [ ] Set up billing alerts ($50, $80, $100)
- [ ] Install/update gcloud CLI
- [ ] Authenticate gcloud

**Commands:**
```bash
# Set project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable Compute Engine API
gcloud services enable compute.googleapis.com

# Set up billing alert
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="NLP VM Budget" \
  --budget-amount=100USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100
```

#### Task 1.2: Reserve Static External IP
- [ ] Reserve static IP address
- [ ] Note the IP for DNS configuration

**Commands:**
```bash
# Reserve static IP
gcloud compute addresses create nlp-classifier-ip \
  --region=us-central1

# Get the IP address
gcloud compute addresses describe nlp-classifier-ip \
  --region=us-central1 \
  --format="get(address)"

# Save this IP - you'll use it for DNS and firewall rules
export STATIC_IP=$(gcloud compute addresses describe nlp-classifier-ip \
  --region=us-central1 \
  --format="get(address)")

echo "Your static IP: $STATIC_IP"
```

---

### **PHASE 2: Create and Configure VM** (Est. 30-45 min)

#### Task 2.1: Create Compute Engine VM
- [ ] Choose VM specifications
- [ ] Create VM with persistent disk
- [ ] Assign static IP
- [ ] Configure firewall rules

**Recommended VM Specs:**
- **Machine Type**: e2-standard-2 (2 vCPU, 8GB RAM) - $50/month
- **Boot Disk**: 50GB SSD ($8/month)
- **OS**: Ubuntu 22.04 LTS
- **Region**: us-central1 (Iowa) - cheapest
- **Total**: ~$58/month

**Commands:**
```bash
# Create VM with Docker pre-installed
gcloud compute instances create nlp-classifier-vm \
  --zone=us-central1-a \
  --machine-type=e2-standard-2 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-ssd \
  --address=$STATIC_IP \
  --tags=http-server,https-server,nlp-api,nlp-ui \
  --metadata=startup-script='#!/bin/bash
    # Update system
    apt-get update
    apt-get upgrade -y
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    
    # Install Docker Compose
    apt-get install -y docker-compose-plugin
    
    # Create app user
    useradd -m -s /bin/bash appuser
    usermod -aG docker appuser
    
    # Create directories
    mkdir -p /opt/nlp-classifier
    chown -R appuser:appuser /opt/nlp-classifier
  '

# Wait for VM to be ready (2-3 minutes)
echo "Waiting for VM to start..."
sleep 120
```

#### Task 2.2: Configure Firewall Rules
- [ ] Allow HTTP (80)
- [ ] Allow HTTPS (443)
- [ ] Allow API (8000)
- [ ] Allow UI (8501)
- [ ] Allow SSH (22) - already enabled by default

**Commands:**
```bash
# Create firewall rules
gcloud compute firewall-rules create allow-nlp-api \
  --allow=tcp:8000 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=nlp-api \
  --description="Allow NLP API traffic"

gcloud compute firewall-rules create allow-nlp-ui \
  --allow=tcp:8501 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=nlp-ui \
  --description="Allow NLP UI traffic"

gcloud compute firewall-rules create allow-http \
  --allow=tcp:80 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=http-server \
  --description="Allow HTTP traffic"

gcloud compute firewall-rules create allow-https \
  --allow=tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=https-server \
  --description="Allow HTTPS traffic"

# Verify firewall rules
gcloud compute firewall-rules list --filter="targetTags:nlp-*"
```

---

### **PHASE 3: Setup VM Environment** (Est. 30-45 min)

#### Task 3.1: SSH into VM and Verify Setup
- [ ] SSH into VM
- [ ] Verify Docker is installed
- [ ] Verify Docker Compose is installed
- [ ] Check disk space

**Commands:**
```bash
# SSH into VM
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# Once inside VM, run these commands:
# Verify Docker
docker --version
docker ps

# Verify Docker Compose
docker compose version

# Check disk space
df -h

# Check system resources
free -h
nproc
```

#### Task 3.2: Create Directory Structure
- [ ] Create application directory
- [ ] Create models directory
- [ ] Create logs directory
- [ ] Set permissions

**Commands (on VM):**
```bash
# Create directories
sudo mkdir -p /opt/nlp-classifier/{models,logs,data}
sudo chown -R $USER:$USER /opt/nlp-classifier

# Create subdirectories for models
mkdir -p /opt/nlp-classifier/models/{transformer/distilbert,baselines,toxicity_multi_head}

# Create logs directory
mkdir -p /opt/nlp-classifier/logs

# Verify
ls -la /opt/nlp-classifier/
```

---

### **PHASE 4: Transfer Application Files** (Est. 30-60 min)

#### Task 4.1: Transfer Code and Configuration
- [ ] Clone repository OR transfer files
- [ ] Transfer docker-compose.yml
- [ ] Transfer Dockerfiles
- [ ] Transfer .env file (if any)

**Option A: Clone from Git (Recommended)**
```bash
# On VM
cd /opt/nlp-classifier
git clone https://github.com/YOUR_USERNAME/CLOUD-NLP-CLASSIFIER-GCP.git .

# Or if private repo
git clone https://YOUR_TOKEN@github.com/YOUR_USERNAME/CLOUD-NLP-CLASSIFIER-GCP.git .
```

**Option B: Transfer from Local Machine**
```bash
# From your local machine
# Transfer entire project
gcloud compute scp --recurse \
  --zone=us-central1-a \
  ./* nlp-classifier-vm:/opt/nlp-classifier/

# Or transfer specific files
gcloud compute scp --zone=us-central1-a \
  docker-compose.yml \
  docker-compose.prod.yml \
  Dockerfile \
  Dockerfile.streamlit \
  .dockerignore \
  requirements.txt \
  nlp-classifier-vm:/opt/nlp-classifier/
```

#### Task 4.2: Transfer Model Files
- [ ] Transfer trained models to VM
- [ ] Verify model files integrity
- [ ] Set correct permissions

**Commands:**
```bash
# From local machine - transfer models
# This will take 5-15 minutes depending on model size (3-5GB)

# Transfer DistilBERT model
gcloud compute scp --recurse --zone=us-central1-a \
  models/transformer/distilbert \
  nlp-classifier-vm:/opt/nlp-classifier/models/transformer/

# Transfer baseline models
gcloud compute scp --recurse --zone=us-central1-a \
  models/baselines \
  nlp-classifier-vm:/opt/nlp-classifier/models/

# Transfer toxicity model
gcloud compute scp --recurse --zone=us-central1-a \
  models/toxicity_multi_head \
  nlp-classifier-vm:/opt/nlp-classifier/models/

# Verify on VM
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a --command="ls -lh /opt/nlp-classifier/models/transformer/distilbert/"
```

**Alternative: Use Cloud Storage (Faster for large files)**
```bash
# From local machine - upload to Cloud Storage
gsutil -m cp -r models gs://$PROJECT_ID-nlp-models/

# On VM - download from Cloud Storage
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a
gsutil -m cp -r gs://$PROJECT_ID-nlp-models/models /opt/nlp-classifier/
```

---

### **PHASE 5: Configure Docker Compose** (Est. 15-30 min)

#### Task 5.1: Create Production Docker Compose File
- [ ] Create docker-compose.prod.yml
- [ ] Configure volume mounts
- [ ] Set environment variables
- [ ] Configure restart policies

**Create file: `docker-compose.prod.yml`**
```yaml
version: '3.8'

services:
  # FastAPI Backend
  api:
    build:
      context: .
      dockerfile: Dockerfile
    image: nlp-classifier-api:latest
    container_name: nlp-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DEFAULT_MODEL=distilbert
      - LOG_LEVEL=info
      - WORKERS=2
    volumes:
      # Mount models from host (persistent disk)
      - /opt/nlp-classifier/models:/app/models:ro
      # Mount logs for persistence
      - /opt/nlp-classifier/logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 3G
        reservations:
          cpus: '0.5'
          memory: 2G

  # Streamlit UI
  ui:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    image: nlp-classifier-ui:latest
    container_name: nlp-ui
    restart: unless-stopped
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    volumes:
      # Mount models from host (read-only)
      - /opt/nlp-classifier/models:/app/models:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2.5G
        reservations:
          cpus: '0.5'
          memory: 1.5G

  # Optional: Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: nlp-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      # For HTTPS (optional)
      # - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
      - ui
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  default:
    name: nlp-network
```

#### Task 5.2: Create Nginx Configuration (Optional)
- [ ] Create nginx.conf for reverse proxy
- [ ] Configure routing (/ → UI, /api → API)
- [ ] Add rate limiting
- [ ] Add caching headers

**Create file: `nginx.conf`**
```nginx
events {
    worker_connections 1024;
}

http {
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=ui_limit:10m rate=50r/m;

    # Upstream services
    upstream api_backend {
        server api:8000;
    }

    upstream ui_backend {
        server ui:8501;
    }

    # Main server
    server {
        listen 80;
        server_name _;

        # Increase timeouts for Streamlit WebSocket
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # API routes
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://api_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Streamlit UI (WebSocket support)
        location / {
            limit_req zone=ui_limit burst=10 nodelay;
            
            proxy_pass http://ui_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support for Streamlit
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }

        # Streamlit specific routes
        location /_stcore/ {
            proxy_pass http://ui_backend/_stcore/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }
    }
}
```

---

### **PHASE 6: Build and Deploy** (Est. 30-60 min)

#### Task 6.1: Build Docker Images on VM
- [ ] Build API image
- [ ] Build UI image
- [ ] Verify images are created

**Commands (on VM):**
```bash
# Navigate to project directory
cd /opt/nlp-classifier

# Build images (this will take 10-15 minutes)
docker compose -f docker-compose.prod.yml build

# Verify images
docker images | grep nlp-classifier

# Should see:
# nlp-classifier-api    latest
# nlp-classifier-ui     latest
```

#### Task 6.2: Start Services
- [ ] Start Docker Compose
- [ ] Verify containers are running
- [ ] Check logs for errors

**Commands (on VM):**
```bash
# Start services in detached mode
docker compose -f docker-compose.prod.yml up -d

# Check container status
docker compose -f docker-compose.prod.yml ps

# Should see all containers as "Up" and "healthy"

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Or view individual service logs
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f ui
```

#### Task 6.3: Verify Services are Running
- [ ] Check API health endpoint
- [ ] Check UI health endpoint
- [ ] Test API prediction
- [ ] Test UI in browser

**Commands (on VM):**
```bash
# Test API health
curl http://localhost:8000/health

# Test API prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test message"}'

# Test UI health
curl http://localhost:8501/_stcore/health

# Test models endpoint
curl http://localhost:8000/models

# If using Nginx
curl http://localhost/health
curl http://localhost/api/health
```

---

### **PHASE 7: External Access Testing** (Est. 15-30 min)

#### Task 7.1: Test External Access
- [ ] Test API from your local machine
- [ ] Test UI from browser
- [ ] Test all 3 models
- [ ] Verify model switching

**Commands (from your local machine):**
```bash
# Get your VM's external IP
export VM_IP=$(gcloud compute addresses describe nlp-classifier-ip \
  --region=us-central1 \
  --format="get(address)")

echo "VM IP: $VM_IP"

# Test API health
curl http://$VM_IP:8000/health

# Test API prediction
curl -X POST http://$VM_IP:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test message from external network"}'

# Test model switching
curl -X POST http://$VM_IP:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "logistic_regression"}'

# Test with new model
curl -X POST http://$VM_IP:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Testing logistic regression model"}'
```

**Browser Testing:**
```
API Docs:  http://YOUR_VM_IP:8000/docs
API:       http://YOUR_VM_IP:8000/health
UI:        http://YOUR_VM_IP:8501
Nginx:     http://YOUR_VM_IP/  (if enabled)
```

---

### **PHASE 8: Configure Auto-Start on Boot** (Est. 15 min)

#### Task 8.1: Create Systemd Service
- [ ] Create systemd service file
- [ ] Enable service to start on boot
- [ ] Test service restart

**Create file on VM: `/etc/systemd/system/nlp-classifier.service`**
```bash
# On VM, create systemd service
sudo tee /etc/systemd/system/nlp-classifier.service > /dev/null <<EOF
[Unit]
Description=NLP Classifier Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/nlp-classifier
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable nlp-classifier.service

# Start service
sudo systemctl start nlp-classifier.service

# Check status
sudo systemctl status nlp-classifier.service
```

#### Task 8.2: Test Auto-Start
- [ ] Reboot VM
- [ ] Verify services start automatically
- [ ] Test endpoints after reboot

**Commands:**
```bash
# Reboot VM
sudo reboot

# Wait 2-3 minutes, then SSH back in
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# Check if containers are running
docker ps

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8501/_stcore/health
```

---

### **PHASE 9: Monitoring and Logging** (Est. 30-45 min)

#### Task 9.1: Set Up Log Rotation
- [ ] Configure Docker log rotation
- [ ] Configure application log rotation
- [ ] Test log rotation

**Create file on VM: `/etc/docker/daemon.json`**
```bash
# Configure Docker logging
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# Restart Docker
sudo systemctl restart docker

# Restart containers
cd /opt/nlp-classifier
docker compose -f docker-compose.prod.yml restart
```

#### Task 9.2: Create Monitoring Script
- [ ] Create health check script
- [ ] Set up cron job for monitoring
- [ ] Configure email alerts (optional)

**Create file on VM: `/opt/nlp-classifier/monitor.sh`**
```bash
#!/bin/bash
# Health monitoring script

LOG_FILE="/opt/nlp-classifier/logs/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check API health
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$API_STATUS" != "200" ]; then
    echo "[$DATE] ERROR: API health check failed (HTTP $API_STATUS)" >> $LOG_FILE
    # Restart API container
    docker compose -f /opt/nlp-classifier/docker-compose.prod.yml restart api
fi

# Check UI health
UI_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/_stcore/health)
if [ "$UI_STATUS" != "200" ]; then
    echo "[$DATE] ERROR: UI health check failed (HTTP $UI_STATUS)" >> $LOG_FILE
    # Restart UI container
    docker compose -f /opt/nlp-classifier/docker-compose.prod.yml restart ui
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "[$DATE] WARNING: Disk usage is at ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2 {printf "%.0f", $3*100/$2}')
if [ "$MEM_USAGE" -gt 90 ]; then
    echo "[$DATE] WARNING: Memory usage is at ${MEM_USAGE}%" >> $LOG_FILE
fi

echo "[$DATE] Health check completed. API: $API_STATUS, UI: $UI_STATUS" >> $LOG_FILE
```

**Set up cron job:**
```bash
# Make script executable
chmod +x /opt/nlp-classifier/monitor.sh

# Add to crontab (run every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/nlp-classifier/monitor.sh") | crontab -

# Verify crontab
crontab -l
```

#### Task 9.3: Enable Cloud Logging (Optional)
- [ ] Install Cloud Logging agent
- [ ] Configure log forwarding
- [ ] View logs in Cloud Console

**Commands (on VM):**
```bash
# Install Cloud Logging agent
curl -sSO https://dl.google.com/cloudagents/add-logging-agent-repo.sh
sudo bash add-logging-agent-repo.sh --also-install

# Configure logging
sudo tee /etc/google-fluentd/config.d/nlp-classifier.conf > /dev/null <<EOF
<source>
  @type tail
  format json
  path /opt/nlp-classifier/logs/*.log
  pos_file /var/lib/google-fluentd/pos/nlp-classifier.pos
  read_from_head true
  tag nlp-classifier
</source>
EOF

# Restart agent
sudo service google-fluentd restart
```

---

### **PHASE 10: Backup Strategy** (Est. 30 min)

#### Task 10.1: Create Backup Script
- [ ] Create backup script for models
- [ ] Create backup script for logs
- [ ] Test backup and restore

**Create file on VM: `/opt/nlp-classifier/backup.sh`**
```bash
#!/bin/bash
# Backup script for NLP Classifier

BACKUP_DIR="/opt/nlp-classifier/backups"
DATE=$(date '+%Y%m%d_%H%M%S')
PROJECT_ID="your-project-id"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup models to Cloud Storage
echo "Backing up models..."
gsutil -m rsync -r /opt/nlp-classifier/models gs://$PROJECT_ID-nlp-backups/models-$DATE/

# Backup logs
echo "Backing up logs..."
tar -czf $BACKUP_DIR/logs-$DATE.tar.gz /opt/nlp-classifier/logs/

# Upload logs to Cloud Storage
gsutil cp $BACKUP_DIR/logs-$DATE.tar.gz gs://$PROJECT_ID-nlp-backups/logs/

# Keep only last 7 days of local backups
find $BACKUP_DIR -name "logs-*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

**Set up automated backups:**
```bash
# Make script executable
chmod +x /opt/nlp-classifier/backup.sh

# Create Cloud Storage bucket
gsutil mb -l us-central1 gs://$PROJECT_ID-nlp-backups

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/nlp-classifier/backup.sh") | crontab -
```

#### Task 10.2: Create Disk Snapshot Schedule
- [ ] Create snapshot schedule
- [ ] Attach to VM disk
- [ ] Test snapshot restore

**Commands (from local machine):**
```bash
# Create snapshot schedule (daily at 3 AM)
gcloud compute resource-policies create snapshot-schedule nlp-daily-backup \
  --region=us-central1 \
  --max-retention-days=7 \
  --on-source-disk-delete=keep-auto-snapshots \
  --daily-schedule \
  --start-time=03:00

# Attach schedule to VM disk
gcloud compute disks add-resource-policies nlp-classifier-vm \
  --zone=us-central1-a \
  --resource-policies=nlp-daily-backup

# List snapshots
gcloud compute snapshots list --filter="sourceDisk:nlp-classifier-vm"
```

---

### **PHASE 11: Security Hardening** (Est. 30-45 min)

#### Task 11.1: Configure UFW Firewall
- [ ] Enable UFW
- [ ] Allow only necessary ports
- [ ] Enable SSH rate limiting

**Commands (on VM):**
```bash
# Install UFW
sudo apt-get install -y ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (with rate limiting)
sudo ufw limit ssh

# Allow API and UI
sudo ufw allow 8000/tcp
sudo ufw allow 8501/tcp

# Allow HTTP/HTTPS (if using Nginx)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable UFW
sudo ufw --force enable

# Check status
sudo ufw status verbose
```

#### Task 11.2: Set Up Automatic Security Updates
- [ ] Enable unattended upgrades
- [ ] Configure update schedule
- [ ] Set up reboot policy

**Commands (on VM):**
```bash
# Install unattended-upgrades
sudo apt-get install -y unattended-upgrades

# Enable automatic updates
sudo dpkg-reconfigure -plow unattended-upgrades

# Configure (edit if needed)
sudo nano /etc/apt/apt.conf.d/50unattended-upgrades
```

#### Task 11.3: Restrict SSH Access
- [ ] Disable password authentication
- [ ] Use SSH keys only
- [ ] Change default SSH port (optional)

**Commands (on VM):**
```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Set these values:
# PasswordAuthentication no
# PubkeyAuthentication yes
# PermitRootLogin no

# Restart SSH
sudo systemctl restart sshd
```

---

### **PHASE 12: DNS Configuration** (Est. 15-30 min)

#### Task 12.1: Configure DNS (Optional)
- [ ] Get external IP
- [ ] Create A records in DNS provider
- [ ] Test DNS resolution

**DNS Configuration:**
```
# Add these A records in your DNS provider:
nlp.yourdomain.com        A    YOUR_VM_IP
api.yourdomain.com        A    YOUR_VM_IP
ui.yourdomain.com         A    YOUR_VM_IP
```

**Using Cloud DNS (GCP):**
```bash
# Create DNS zone
gcloud dns managed-zones create nlp-zone \
  --dns-name="yourdomain.com." \
  --description="NLP Classifier DNS"

# Add A record
gcloud dns record-sets create nlp.yourdomain.com \
  --zone=nlp-zone \
  --type=A \
  --ttl=300 \
  --rrdatas=$VM_IP
```

---

### **PHASE 13: SSL/HTTPS Setup** (Est. 30-60 min, Optional)

#### Task 13.1: Install Certbot
- [ ] Install Certbot
- [ ] Obtain SSL certificate
- [ ] Configure Nginx for HTTPS
- [ ] Set up auto-renewal

**Commands (on VM):**
```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate (requires domain name)
sudo certbot --nginx -d nlp.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run

# Auto-renewal is set up via cron automatically
```

---

### **PHASE 14: Performance Optimization** (Est. 30 min)

#### Task 14.1: Optimize Docker Images
- [ ] Review image sizes
- [ ] Remove unnecessary files
- [ ] Use multi-stage builds

#### Task 14.2: Configure Swap Space
- [ ] Create swap file (4GB)
- [ ] Enable swap
- [ ] Configure swappiness

**Commands (on VM):**
```bash
# Create 4GB swap file
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Set swappiness (lower = less swap usage)
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

---

## 📊 Cost Breakdown

### Monthly Costs (us-central1)

| Component | Specification | Monthly Cost |
|-----------|--------------|--------------|
| **VM Instance** | e2-standard-2 (2 vCPU, 8GB RAM) | $49.28 |
| **Boot Disk** | 50GB SSD | $8.50 |
| **Static IP** | Reserved external IP | $7.30 |
| **Egress** | 10-50GB/month | $1-6 |
| **Snapshots** | 7 days retention (~50GB) | $2-3 |
| **Cloud Storage** | Backups (optional) | $1-2 |
| **TOTAL** | | **$69-76/month** |

### Cost Optimization Tips

1. **Use Standard Persistent Disk**: Save $4/month (vs SSD)
   ```bash
   --boot-disk-type=pd-standard  # $2.40/month vs $8.50
   ```

2. **Use Preemptible VM**: Save 60-80% (~$15-20/month)
   - Trade-off: VM can be terminated any time
   - Good for dev/staging, not production

3. **Use Spot VM**: Save up to 91% (~$5-10/month)
   - Similar to preemptible but better availability

4. **Smaller VM**: Use e2-small (0.5 vCPU, 2GB RAM) - $15/month
   - Only if traffic is very low

5. **Release Static IP**: Save $7/month
   - Use ephemeral IP (changes on restart)

### Cost Comparison

| Deployment | Monthly Cost | Pros | Cons |
|------------|--------------|------|------|
| **VM + Docker** | $70-80 | Simple, full control | Manual ops |
| **GKE** | $150-180 | Auto-scaling, HA | Complex, expensive |
| **Cloud Run** | $15-50 | Serverless, cheap | Cold starts, no PVCs |

---

## 🔧 Maintenance Procedures

### Daily Tasks (Automated)
- ✅ Health checks (every 5 min via cron)
- ✅ Log rotation (Docker handles)
- ✅ Disk snapshots (automated)

### Weekly Tasks (Manual)
- [ ] Review logs for errors
- [ ] Check disk usage
- [ ] Review cost dashboard
- [ ] Test backups

### Monthly Tasks (Manual)
- [ ] Update Docker images
- [ ] Apply security patches
- [ ] Review and optimize resources
- [ ] Test disaster recovery

### Update Procedure
```bash
# SSH into VM
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# Pull latest code
cd /opt/nlp-classifier
git pull

# Rebuild images
docker compose -f docker-compose.prod.yml build

# Restart services (zero downtime with rolling restart)
docker compose -f docker-compose.prod.yml up -d --no-deps --build api
docker compose -f docker-compose.prod.yml up -d --no-deps --build ui

# Check status
docker compose -f docker-compose.prod.yml ps
```

---

## 🚨 Troubleshooting Guide

### Issue: Containers won't start
```bash
# Check logs
docker compose -f docker-compose.prod.yml logs

# Check disk space
df -h

# Check memory
free -h

# Restart Docker
sudo systemctl restart docker
```

### Issue: High memory usage
```bash
# Check container stats
docker stats

# Restart specific container
docker compose -f docker-compose.prod.yml restart api

# Clear Docker cache
docker system prune -a
```

### Issue: Can't access from external IP
```bash
# Check firewall rules
gcloud compute firewall-rules list

# Check if containers are running
docker ps

# Check if ports are listening
sudo netstat -tlnp | grep -E '8000|8501'

# Test locally first
curl http://localhost:8000/health
```

### Issue: VM is slow
```bash
# Check CPU usage
top

# Check disk I/O
iostat -x 1

# Check memory
free -h

# Consider upgrading VM
gcloud compute instances set-machine-type nlp-classifier-vm \
  --zone=us-central1-a \
  --machine-type=e2-standard-4
```

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] GCP project created and billing enabled
- [ ] gcloud CLI installed and authenticated
- [ ] All models trained and tested locally
- [ ] Docker Compose tested locally
- [ ] Budget alerts configured

### Deployment
- [ ] VM created with correct specs
- [ ] Static IP reserved and assigned
- [ ] Firewall rules configured
- [ ] Application files transferred
- [ ] Models transferred (3-5GB)
- [ ] Docker images built
- [ ] Services started and healthy
- [ ] External access tested

### Post-Deployment
- [ ] Auto-start configured (systemd)
- [ ] Monitoring script set up
- [ ] Backup strategy implemented
- [ ] Security hardening completed
- [ ] DNS configured (optional)
- [ ] SSL/HTTPS enabled (optional)
- [ ] Documentation updated

---

## 🎯 Success Criteria

- [ ] API responds at http://YOUR_IP:8000/health
- [ ] UI loads at http://YOUR_IP:8501
- [ ] All 3 models are accessible
- [ ] Model switching works
- [ ] Services restart automatically on reboot
- [ ] Logs are being written and rotated
- [ ] Backups are running daily
- [ ] Monitoring is active
- [ ] Cost is under $80/month

---

## 📚 Quick Reference Commands

### Start/Stop Services
```bash
# Start
docker compose -f docker-compose.prod.yml up -d

# Stop
docker compose -f docker-compose.prod.yml down

# Restart
docker compose -f docker-compose.prod.yml restart

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

### Monitoring
```bash
# Container stats
docker stats

# Disk usage
df -h

# Memory usage
free -h

# Check health
curl http://localhost:8000/health
```

### Maintenance
```bash
# Update and restart
git pull
docker compose -f docker-compose.prod.yml up -d --build

# Clean up
docker system prune -a

# Backup
/opt/nlp-classifier/backup.sh
```

---

## 🎓 Next Steps After Deployment

### Immediate (Week 1)
1. Monitor costs daily
2. Test all endpoints thoroughly
3. Set up alerts for downtime
4. Document any issues

### Short-term (Month 1)
1. Optimize resource usage
2. Set up proper monitoring dashboard
3. Implement CI/CD (optional)
4. Add more comprehensive logging

### Long-term (Month 2+)
1. Consider adding load balancer for HA
2. Set up staging environment
3. Implement blue-green deployments
4. Add more advanced monitoring (Prometheus/Grafana)

---

## 📞 Support Resources

- **GCP Compute Engine Docs**: https://cloud.google.com/compute/docs
- **Docker Compose Docs**: https://docs.docker.com/compose/
- **Your Project README**: See local README.md for API details

---

**Document Version**: 1.0  
**Created**: 2025-12-10  
**Estimated Total Time**: 5-8 hours  
**Estimated Monthly Cost**: $70-80  
**Complexity**: ⭐⭐ Low-Medium  
**Recommended For**: MVP, Small-Medium Workloads, Learning

---

**READY TO DEPLOY! 🚀**
