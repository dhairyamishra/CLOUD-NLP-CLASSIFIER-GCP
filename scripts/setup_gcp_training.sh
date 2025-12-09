#!/bin/bash
# Setup script for GCP GPU VM training environment
# Run this script once after creating a new GCP VM instance

set -e  # Exit on error

echo "=========================================="
echo "GCP Training Environment Setup"
echo "=========================================="

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.11 (if not already installed)
echo "Installing Python 3.11..."
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install CUDA drivers (if GPU instance)
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected!"
    nvidia-smi
    
    # Install CUDA toolkit (if not already installed)
    if ! command -v nvcc &> /dev/null; then
        echo "Installing CUDA toolkit..."
        # For Ubuntu 20.04/22.04
        wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb
        sudo dpkg -i cuda-keyring_1.0-1_all.deb
        sudo apt-get update
        sudo apt-get -y install cuda-toolkit-12-1
        
        # Add CUDA to PATH
        echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
        echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
        source ~/.bashrc
    fi
else
    echo "No GPU detected. Training will use CPU."
fi

# Install Git (if not already installed)
echo "Installing Git..."
sudo apt-get install -y git

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y build-essential libssl-dev libffi-dev

# Clone repository (if not already cloned)
if [ ! -d "CLOUD-NLP-CLASSIFIER-GCP" ]; then
    echo "Cloning repository..."
    git clone https://github.com/YOUR_USERNAME/CLOUD-NLP-CLASSIFIER-GCP.git
    cd CLOUD-NLP-CLASSIFIER-GCP
else
    echo "Repository already exists. Pulling latest changes..."
    cd CLOUD-NLP-CLASSIFIER-GCP
    git pull
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install PyTorch with CUDA support (if GPU available)
if command -v nvidia-smi &> /dev/null; then
    echo "Installing PyTorch with CUDA support..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
else
    echo "Installing PyTorch (CPU version)..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Install project requirements
echo "Installing project requirements..."
pip install -r requirements.txt

# Download dataset (if not already downloaded)
if [ ! -f "data/processed/train.csv" ]; then
    echo "Downloading and preprocessing dataset..."
    python scripts/download_dataset.py
    python run_preprocess.py
else
    echo "Dataset already exists."
fi

# Verify installation
echo "Verifying installation..."
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import transformers; print(f'Transformers version: {transformers.__version__}')"

echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start training, run:"
echo "  ./scripts/run_gcp_training.sh"
echo ""
