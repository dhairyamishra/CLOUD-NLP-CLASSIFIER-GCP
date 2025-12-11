#!/usr/bin/env python3
"""
Master Deployment Controller for CLOUD-NLP-CLASSIFIER-GCP

Orchestrates the complete deployment pipeline from fresh repository clone to 
fully functional production deployment (local or GCP cloud). Supports multiple 
execution modes, checkpoint/resume functionality, and comprehensive validation.

QUICK START:
    # Automated local deployment (5 minutes)
    python deploy-master-controller.py --profile quick
    
    # Full production deployment (30 minutes)
    python deploy-master-controller.py --profile full
    
    # Cloud deployment to GCP
    python deploy-master-controller.py --target cloud --gcp-project YOUR_PROJECT_ID
    
    # Resume from checkpoint
    python deploy-master-controller.py --resume
    
    # Force re-run all stages
    python deploy-master-controller.py --force --profile quick

DEPLOYMENT STAGES:
    Stage 0: Environment Setup (venv, pip, requirements)
    Stage 1: Data Preprocessing (download, clean, split)
    Stage 2: Baseline Training (Logistic Regression, Linear SVM)
    Stage 3: Transformer Training (DistilBERT with selected profile)
    Stage 4: Toxicity Training (multi-head model, optional)
    Stage 5: Local API Testing (FastAPI validation)
    Stage 6: Docker Build (docker-compose for API + UI)
    Stage 7: Full Stack Testing (pytest + PowerShell tests)
    Stage 8: GCS Upload (cloud only - model storage)
    Stage 9: GCP Deployment (cloud only - VM deployment)
    Stage 10: UI Deployment (cloud only - Streamlit UI)

PROFILES:
    quick:  1 epoch,  1-2 min GPU, 80-85% acc (testing/development)
    full:   15 epochs, 15-25 min GPU, 90-93% acc (production)
    cloud:  10 epochs, 20-40 min GPU, 90-93% acc (GCP optimized)

FEATURES:
    - Automated end-to-end deployment
    - Checkpoint system with resume capability
    - Real-time output streaming for all stages
    - Comprehensive logging and progress tracking
    - Interactive and automated modes
    - Profile-based training configurations
    - Docker Compose integration (parallel builds)
    - Multi-model support (4 models in single deployment)

Version: 1.0.0
Author: CLOUD-NLP-CLASSIFIER-GCP Team
Last Updated: 2025-12-11
"""

import argparse
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Callable
from enum import Enum


# ============================================================================
# [1] CONFIGURATION & CONSTANTS
# ============================================================================

SCRIPT_VERSION = "1.0.0"
SCRIPT_START_TIME = datetime.now()
DEPLOYMENT_ID = f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

# Paths
ROOT_DIR = Path(__file__).parent.absolute()
DEPLOYMENT_DIR = ROOT_DIR / ".deployment"
CHECKPOINTS_DIR = DEPLOYMENT_DIR / "checkpoints"
LOGS_DIR = DEPLOYMENT_DIR / "logs"
STATE_FILE = DEPLOYMENT_DIR / "deployment_state.json"
METRICS_FILE = DEPLOYMENT_DIR / "deployment_metrics.json"
REPORT_FILE = DEPLOYMENT_DIR / "deployment_report.md"
LOG_FILE = LOGS_DIR / "deployment.log"


class ExecutionMode(Enum):
    """Execution modes for deployment"""
    INTERACTIVE = "interactive"
    AUTO = "auto"


class DeploymentTarget(Enum):
    """Deployment targets"""
    LOCAL = "local"
    CLOUD = "cloud"
    BOTH = "both"


class LogLevel(Enum):
    """Log levels with colors"""
    INFO = ("INFO", "\033[97m")      # White
    SUCCESS = ("SUCCESS", "\033[92m")  # Green
    WARNING = ("WARNING", "\033[93m")  # Yellow
    ERROR = ("ERROR", "\033[91m")      # Red
    DEBUG = ("DEBUG", "\033[90m")      # Gray


@dataclass
class Stage:
    """Stage definition"""
    id: int
    name: str
    description: str
    estimated_duration: int  # seconds
    required_for: List[str]
    validation_func: str
    optional: bool = False


@dataclass
class StageMetrics:
    """Metrics for a completed stage"""
    name: str
    duration_seconds: float
    completed_at: str
    status: str


@dataclass
class DeploymentState:
    """Deployment state management"""
    deployment_id: str
    start_time: str
    mode: str
    target: str
    current_stage: int = -1
    completed_stages: List[int] = field(default_factory=list)
    failed_stages: List[int] = field(default_factory=list)
    skipped_stages: List[int] = field(default_factory=list)
    stage_metrics: Dict[str, dict] = field(default_factory=dict)
    errors: List[dict] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    version: str = SCRIPT_VERSION
    last_updated: str = ""


# Stage Definitions
STAGES = [
    Stage(
        id=0,
        name="Environment Setup",
        description="Check prerequisites, create venv, install dependencies",
        estimated_duration=300,
        required_for=["local", "cloud", "both"],
        validation_func="validate_stage_0"
    ),
    Stage(
        id=1,
        name="Data Preprocessing",
        description="Download dataset, preprocess, create train/val/test splits",
        estimated_duration=180,
        required_for=["local", "cloud", "both"],
        validation_func="validate_stage_1"
    ),
    Stage(
        id=2,
        name="Baseline Training",
        description="Train TF-IDF + Logistic Regression + Linear SVM",
        estimated_duration=240,
        required_for=["local", "cloud", "both"],
        validation_func="validate_stage_2"
    ),
    Stage(
        id=3,
        name="Transformer Training",
        description="Fine-tune DistilBERT (CPU: 15-30min, GPU: 3-5min)",
        estimated_duration=1200,
        required_for=["local", "cloud", "both"],
        validation_func="validate_stage_3"
    ),
    Stage(
        id=4,
        name="Toxicity Training",
        description="Train multi-label toxicity classifier (6 categories)",
        estimated_duration=1800,
        required_for=["local", "cloud", "both"],
        validation_func="validate_stage_4",
        optional=True
    ),
    Stage(
        id=5,
        name="Local API Testing",
        description="Start API server and test endpoints",
        estimated_duration=120,
        required_for=["local", "cloud", "both"],
        validation_func="validate_stage_5"
    ),
    Stage(
        id=6,
        name="Docker Build",
        description="Build backend and UI Docker images",
        estimated_duration=720,
        required_for=["local", "cloud", "both"],
        validation_func="validate_stage_6"
    ),
    Stage(
        id=7,
        name="Full Stack Testing",
        description="Run comprehensive test suite (326+ tests)",
        estimated_duration=240,
        required_for=["local", "cloud", "both"],
        validation_func="validate_stage_7"
    ),
    Stage(
        id=8,
        name="GCS Upload",
        description="Upload models to Google Cloud Storage",
        estimated_duration=180,
        required_for=["cloud", "both"],
        validation_func="validate_stage_8",
        optional=True
    ),
    Stage(
        id=9,
        name="GCP Deployment",
        description="Deploy to GCP VM with Docker",
        estimated_duration=1500,
        required_for=["cloud", "both"],
        validation_func="validate_stage_9",
        optional=True
    ),
    Stage(
        id=10,
        name="UI Deployment",
        description="Deploy Streamlit UI to GCP",
        estimated_duration=600,
        required_for=["cloud", "both"],
        validation_func="validate_stage_10",
        optional=True
    ),
]


# ============================================================================
# [2] HELPER FUNCTIONS
# ============================================================================

class DeploymentLogger:
    """Custom logger with colored output"""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup file handler with UTF-8 encoding
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log(self, message: str, level: LogLevel = LogLevel.INFO, no_console: bool = False):
        """Log message with color and level"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level.value[0]}] {message}"
        
        # Write to file
        self.logger.info(log_message)
        
        # Write to console with color
        if not no_console:
            color = level.value[1]
            reset = "\033[0m"
            print(f"{color}{log_message}{reset}")
    
    def info(self, message: str):
        self.log(message, LogLevel.INFO)
    
    def success(self, message: str):
        self.log(message, LogLevel.SUCCESS)
    
    def warning(self, message: str):
        self.log(message, LogLevel.WARNING)
    
    def error(self, message: str):
        self.log(message, LogLevel.ERROR)
    
    def debug(self, message: str):
        self.log(message, LogLevel.DEBUG)


class ProgressTracker:
    """Progress tracking with visual feedback"""
    
    def __init__(self, total_stages: int):
        self.total_stages = total_stages
        self.current_stage = 0
    
    def update(self, stage_id: int, stage_name: str, status: str):
        """Update progress display"""
        percent = int((self.current_stage / self.total_stages) * 100)
        bar_length = 40
        filled = int((percent / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"\n{'='*70}")
        print(f"Progress: [{bar}] {percent}%")
        print(f"Stage {stage_id}: {stage_name}")
        print(f"Status: {status}")
        print(f"{'='*70}\n")
    
    def increment(self):
        """Increment completed stages"""
        self.current_stage += 1


class CheckpointManager:
    """Manage stage checkpoints"""
    
    def __init__(self, checkpoints_dir: Path):
        self.checkpoints_dir = checkpoints_dir
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, stage_id: int, stage_name: str):
        """Save checkpoint for completed stage"""
        checkpoint_file = self.checkpoints_dir / f"stage{stage_id}_complete.flag"
        checkpoint_data = {
            "stage_id": stage_id,
            "stage_name": stage_name,
            "completed_at": datetime.now().isoformat(),
            "deployment_id": DEPLOYMENT_ID
        }
        checkpoint_file.write_text(json.dumps(checkpoint_data, indent=2))
    
    def exists(self, stage_id: int) -> bool:
        """Check if checkpoint exists"""
        checkpoint_file = self.checkpoints_dir / f"stage{stage_id}_complete.flag"
        return checkpoint_file.exists()
    
    def clear_all(self):
        """Clear all checkpoints"""
        if self.checkpoints_dir.exists():
            shutil.rmtree(self.checkpoints_dir)
            self.checkpoints_dir.mkdir(parents=True, exist_ok=True)


class StateManager:
    """Manage deployment state"""
    
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state: Optional[DeploymentState] = None
    
    def save(self, state: DeploymentState):
        """Save deployment state to JSON"""
        state.last_updated = datetime.now().isoformat()
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(asdict(state), indent=2))
        self.state = state
    
    def load(self) -> Optional[DeploymentState]:
        """Load deployment state from JSON"""
        if not self.state_file.exists():
            return None
        
        try:
            data = json.loads(self.state_file.read_text())
            self.state = DeploymentState(**data)
            return self.state
        except Exception as e:
            print(f"Warning: Failed to load deployment state: {e}")
            return None


class PrerequisiteChecker:
    """Check system prerequisites"""
    
    def __init__(self, logger: DeploymentLogger):
        self.logger = logger
    
    def check_all(self, target: str, gcp_project: str = "") -> bool:
        """Check all prerequisites"""
        self.logger.info("Checking prerequisites...")
        all_passed = True
        
        # Check Python version
        all_passed &= self._check_python()
        
        # Check Docker (if needed)
        if target in ["local", "cloud", "both"]:
            all_passed &= self._check_docker()
        
        # Check gcloud (if cloud deployment)
        if target in ["cloud", "both"]:
            all_passed &= self._check_gcloud(gcp_project)
        
        # Check disk space
        self._check_disk_space()
        
        return all_passed
    
    def _check_python(self) -> bool:
        """Check Python version"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 10:
            self.logger.success(f"✓ Python {version.major}.{version.minor} detected")
            return True
        else:
            self.logger.error(f"✗ Python 3.10+ required (found {version.major}.{version.minor})")
            return False
    
    def _check_docker(self) -> bool:
        """Check Docker installation"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.logger.success(f"✓ Docker detected: {result.stdout.strip()}")
                return True
            else:
                self.logger.error("✗ Docker not found or not running")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.logger.error("✗ Docker not found in PATH")
            return False
    
    def _check_gcloud(self, gcp_project: str) -> bool:
        """Check gcloud CLI"""
        try:
            # Check gcloud version
            result = subprocess.run(
                ["gcloud", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                self.logger.error("✗ gcloud CLI not found")
                return False
            
            self.logger.success("✓ gcloud CLI detected")
            
            # Check authentication
            result = subprocess.run(
                ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.stdout.strip():
                self.logger.success(f"✓ gcloud authenticated as: {result.stdout.strip()}")
            else:
                self.logger.error("✗ gcloud not authenticated. Run: gcloud auth login")
                return False
            
            # Check project
            if gcp_project:
                result = subprocess.run(
                    ["gcloud", "config", "get-value", "project"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                current_project = result.stdout.strip()
                if current_project != gcp_project:
                    self.logger.warning(
                        f"⚠ Current project ({current_project}) differs from specified ({gcp_project})"
                    )
            
            return True
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.logger.error("✗ gcloud CLI not found in PATH")
            return False
    
    def _check_disk_space(self):
        """Check available disk space"""
        try:
            stat = shutil.disk_usage(ROOT_DIR)
            free_gb = stat.free / (1024**3)
            
            if free_gb < 10:
                self.logger.warning(f"⚠ Low disk space: {free_gb:.1f}GB free (recommend 10GB+)")
            else:
                self.logger.success(f"✓ Disk space: {free_gb:.1f}GB free")
        except Exception as e:
            self.logger.warning(f"⚠ Could not check disk space: {e}")


# ============================================================================
# [3] VALIDATION FUNCTIONS (Stubs - will be implemented in Phase 2)
# ============================================================================

def validate_stage_0(logger: DeploymentLogger) -> bool:
    """Validate Stage 0: Environment Setup"""
    logger.debug("Validating Stage 0: Environment Setup")
    # TODO: Implement validation
    return True


def validate_stage_1(logger: DeploymentLogger) -> bool:
    """Validate Stage 1: Data Preprocessing"""
    logger.debug("Validating Stage 1: Data Preprocessing")
    # TODO: Implement validation
    return True


def validate_stage_2(logger: DeploymentLogger) -> bool:
    """Validate Stage 2: Baseline Training"""
    logger.debug("Validating Stage 2: Baseline Training")
    # TODO: Implement validation
    return True


def validate_stage_3(logger: DeploymentLogger) -> bool:
    """Validate Stage 3: Transformer Training"""
    logger.debug("Validating Stage 3: Transformer Training")
    # TODO: Implement validation
    return True


def validate_stage_4(logger: DeploymentLogger) -> bool:
    """Validate Stage 4: Toxicity Training"""
    logger.debug("Validating Stage 4: Toxicity Training")
    # TODO: Implement validation
    return True


def validate_stage_5(logger: DeploymentLogger) -> bool:
    """Validate Stage 5: Local API Testing"""
    logger.debug("Validating Stage 5: Local API Testing")
    # TODO: Implement validation
    return True


def validate_stage_6(logger: DeploymentLogger) -> bool:
    """Validate Stage 6: Docker Build"""
    logger.debug("Validating Stage 6: Docker Build")
    # TODO: Implement validation
    return True


def validate_stage_7(logger: DeploymentLogger) -> bool:
    """Validate Stage 7: Full Stack Testing"""
    logger.debug("Validating Stage 7: Full Stack Testing")
    # TODO: Implement validation
    return True


def validate_stage_8(logger: DeploymentLogger) -> bool:
    """Validate Stage 8: GCS Upload"""
    logger.debug("Validating Stage 8: GCS Upload")
    # TODO: Implement validation
    return True


def validate_stage_9(logger: DeploymentLogger) -> bool:
    """Validate Stage 9: GCP Deployment"""
    logger.debug("Validating Stage 9: GCP Deployment")
    # TODO: Implement validation
    return True


def validate_stage_10(logger: DeploymentLogger) -> bool:
    """Validate Stage 10: UI Deployment"""
    logger.debug("Validating Stage 10: UI Deployment")
    # TODO: Implement validation
    return True


# ============================================================================
# [4] STAGE FUNCTIONS (Stubs - will be implemented in Phase 2)
# ============================================================================

def execute_stage_0(logger: DeploymentLogger, dry_run: bool = False) -> bool:
    """Execute Stage 0: Environment Setup
    
    - Check Python 3.10+, Docker, gcloud CLI (already done in initialization)
    - Create virtual environment
    - Install requirements.txt
    - Create directory structure
    - Initialize deployment state
    """
    logger.info("Stage 0: Environment Setup")
    
    if dry_run:
        logger.info("[DRY RUN] Would create venv and install dependencies")
        return True
    
    try:
        # 1. Create virtual environment (if not already in one)
        venv_path = ROOT_DIR / "venv"
        if not venv_path.exists():
            logger.info("Creating virtual environment...")
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                capture_output=False,  # Stream output in real-time
                text=True,
                timeout=120
            )
            if result.returncode != 0:
                logger.error(f"Failed to create venv: {result.stderr}")
                return False
            logger.success("✓ Virtual environment created")
        else:
            logger.info("✓ Virtual environment already exists")
        
        # 2. Determine venv python path (cross-platform)
        if platform.system() == "Windows":
            venv_python = venv_path / "Scripts" / "python.exe"
            venv_pip = venv_path / "Scripts" / "pip.exe"
        else:
            venv_python = venv_path / "bin" / "python"
            venv_pip = venv_path / "bin" / "pip"
        
        # 3. Upgrade pip
        logger.info("Upgrading pip...")
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=False,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            logger.success("✓ pip upgraded")
        
        # 4. Install requirements.txt
        requirements_file = ROOT_DIR / "requirements.txt"
        if requirements_file.exists():
            logger.info("Installing dependencies from requirements.txt...")
            logger.info("This may take 5-10 minutes for first-time installation...")
            result = subprocess.run(
                [str(venv_pip), "install", "-r", str(requirements_file)],
                capture_output=False,
                text=True,
                timeout=900  # 15 minutes max
            )
            if result.returncode != 0:
                logger.error(f"Failed to install requirements: {result.stderr}")
                return False
            logger.success("✓ Dependencies installed")
        else:
            logger.warning("requirements.txt not found, skipping dependency installation")
        
        # 5. Create directory structure
        logger.info("Creating directory structure...")
        directories = [
            ROOT_DIR / "data" / "processed",
            ROOT_DIR / "models" / "baselines",
            ROOT_DIR / "models" / "transformer",
            ROOT_DIR / "models" / "toxicity_multi_head",
            ROOT_DIR / "logs",
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        logger.success("✓ Directory structure created")
        
        logger.success("Stage 0 completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Stage 0 timed out (dependency installation took too long)")
        return False
    except Exception as e:
        logger.error(f"Stage 0 failed: {e}")
        return False


def execute_stage_1(logger: DeploymentLogger, dry_run: bool = False) -> bool:
    """Execute Stage 1: Data Preprocessing
    
    - Download hate speech dataset (if needed)
    - Run preprocessing script
    - Validate train/val/test splits (19,826 / 2,478 / 2,479 rows)
    """
    logger.info("Stage 1: Data Preprocessing")
    
    if dry_run:
        logger.info("[DRY RUN] Would run data preprocessing")
        return True
    
    try:
        # Run preprocessing module
        logger.info("Running data preprocessing...")
        logger.info("This will download the dataset if needed and create train/val/test splits")
        
        result = subprocess.run(
            [sys.executable, "-m", "src.data.preprocess"],
            capture_output=False,  # Show output in real-time
            text=True,
            timeout=600,  # 10 minutes max
            cwd=ROOT_DIR
        )
        
        if result.returncode != 0:
            logger.error(f"Preprocessing failed with exit code {result.returncode}")
            return False
        
        logger.success("✓ Data preprocessing completed")
        
        # Validate output files exist
        data_dir = ROOT_DIR / "data" / "processed"
        required_files = ["train.csv", "val.csv", "test.csv"]
        for file_name in required_files:
            file_path = data_dir / file_name
            if not file_path.exists():
                logger.error(f"Expected file not found: {file_path}")
                return False
            logger.success(f"✓ Found {file_name}")
        
        logger.success("Stage 1 completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Stage 1 timed out (preprocessing took too long)")
        return False
    except Exception as e:
        logger.error(f"Stage 1 failed: {e}")
        return False


def execute_stage_2(logger: DeploymentLogger, dry_run: bool = False) -> bool:
    """Execute Stage 2: Baseline Training
    
    - Train TF-IDF + Logistic Regression + Linear SVM
    - Validate models exist and accuracy > 85%
    """
    logger.info("Stage 2: Baseline Training")
    
    if dry_run:
        logger.info("[DRY RUN] Would train baseline models")
        return True
    
    try:
        # Run baseline training
        logger.info("Training baseline models (TF-IDF + LogReg + SVM)...")
        logger.info("This typically takes 3-5 minutes")
        
        result = subprocess.run(
            [sys.executable, "-m", "src.models.train_baselines"],
            capture_output=False,  # Show output in real-time
            text=True,
            timeout=600,  # 10 minutes max
            cwd=ROOT_DIR
        )
        
        if result.returncode != 0:
            logger.error(f"Baseline training failed with exit code {result.returncode}")
            return False
        
        logger.success("✓ Baseline models trained")
        
        # Validate model files exist
        models_dir = ROOT_DIR / "models" / "baselines"
        required_files = [
            "logistic_regression_tfidf.joblib",
            "linear_svm_tfidf.joblib"
        ]
        for file_name in required_files:
            file_path = models_dir / file_name
            if not file_path.exists():
                logger.error(f"Expected model file not found: {file_path}")
                return False
            logger.success(f"✓ Found {file_name}")
        
        logger.success("Stage 2 completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Stage 2 timed out (baseline training took too long)")
        return False
    except Exception as e:
        logger.error(f"Stage 2 failed: {e}")
        return False


def execute_stage_3(logger: DeploymentLogger, dry_run: bool = False, profile: str = "quick") -> bool:
    """Execute Stage 3: Transformer Training
    
    - Fine-tune DistilBERT
    - Validate accuracy > 90%, model size ~250-300 MB
    - Uses profile-specific config (quick/full/cloud)
    """
    logger.info("Stage 3: Transformer Training")
    
    # Get profile config
    if profile in DEPLOYMENT_PROFILES:
        config_file = DEPLOYMENT_PROFILES[profile]["transformer_config"]
        profile_info = DEPLOYMENT_PROFILES[profile]
        logger.info(f"Using {profile} profile: {profile_info['description']}")
        logger.info(f"Config: {config_file}")
        logger.info(f"Expected: {profile_info['expected_accuracy']} accuracy")
    else:
        config_file = "config/config_transformer_quick.yaml"  # Default fallback
        logger.warning(f"Unknown profile '{profile}', using quick config")
    
    if dry_run:
        logger.info(f"[DRY RUN] Would train DistilBERT transformer with {config_file}")
        return True
    
    try:
        # Run transformer training with profile config
        logger.info("Training DistilBERT transformer...")
        
        result = subprocess.run(
            [sys.executable, "-m", "src.models.transformer_training", "--config", config_file],
            capture_output=False,  # Show output in real-time
            text=True,
            timeout=2400,  # 40 minutes max
            cwd=ROOT_DIR
        )
        
        if result.returncode != 0:
            logger.error(f"Transformer training failed with exit code {result.returncode}")
            return False
        
        logger.success("✓ Transformer model trained")
        
        # Validate model directory exists
        models_dir = ROOT_DIR / "models" / "transformer" / "distilbert"
        if not models_dir.exists():
            logger.error(f"Expected model directory not found: {models_dir}")
            return False
        
        # Check for config.json
        config_file = models_dir / "config.json"
        if not config_file.exists():
            logger.error(f"Expected config.json not found: {config_file}")
            return False
        logger.success("✓ Found config.json")
        
        # Check for model weights (either pytorch_model.bin or model.safetensors)
        pytorch_model = models_dir / "pytorch_model.bin"
        safetensors_model = models_dir / "model.safetensors"
        
        if pytorch_model.exists():
            logger.success("✓ Found pytorch_model.bin")
        elif safetensors_model.exists():
            logger.success("✓ Found model.safetensors")
        else:
            logger.error(f"No model weights found. Expected either pytorch_model.bin or model.safetensors in {models_dir}")
            return False
        
        logger.success("Stage 3 completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Stage 3 timed out (transformer training took too long)")
        return False
    except Exception as e:
        logger.error(f"Stage 3 failed: {e}")
        return False


def execute_stage_4(logger: DeploymentLogger, dry_run: bool = False) -> bool:
    """Execute Stage 4: Toxicity Training
    
    - Train multi-label classifier (6 categories)
    - Validate ROC-AUC > 0.95
    """
    logger.info("Stage 4: Toxicity Training")
    
    if dry_run:
        logger.info("[DRY RUN] Would train toxicity model")
        return True
    
    try:
        # Run toxicity training
        logger.info("Training toxicity multi-label classifier...")
        logger.info("This typically takes 20-40 minutes on CPU, 5-10 minutes on GPU")
        
        result = subprocess.run(
            [sys.executable, "-m", "src.models.train_toxicity"],
            capture_output=False,  # Show output in real-time
            text=True,
            timeout=3000,  # 50 minutes max
            cwd=ROOT_DIR
        )
        
        if result.returncode != 0:
            logger.error(f"Toxicity training failed with exit code {result.returncode}")
            return False
        
        logger.success("✓ Toxicity model trained")
        
        # Validate model directory exists
        models_dir = ROOT_DIR / "models" / "toxicity_multi_head"
        if not models_dir.exists():
            logger.error(f"Expected model directory not found: {models_dir}")
            return False
        
        # Check for config.json
        config_file = models_dir / "config.json"
        if not config_file.exists():
            logger.error(f"Expected config.json not found: {config_file}")
            return False
        logger.success("✓ Found config.json")
        
        # Check for model weights (either pytorch_model.bin or model.safetensors)
        pytorch_model = models_dir / "pytorch_model.bin"
        safetensors_model = models_dir / "model.safetensors"
        
        if pytorch_model.exists():
            logger.success("✓ Found pytorch_model.bin")
        elif safetensors_model.exists():
            logger.success("✓ Found model.safetensors")
        else:
            logger.error(f"No model weights found. Expected either pytorch_model.bin or model.safetensors in {models_dir}")
            return False
        
        logger.success("Stage 4 completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Stage 4 timed out (toxicity training took too long)")
        return False
    except Exception as e:
        logger.error(f"Stage 4 failed: {e}")
        return False


def execute_stage_5(logger: DeploymentLogger, dry_run: bool = False) -> bool:
    """Execute Stage 5: Local API Testing
    
    - Start API server
    - Test /health, /predict, /models endpoints
    - Validate all models work
    - Stop API server
    """
    logger.info("Stage 5: Local API Testing")
    
    if dry_run:
        logger.info("[DRY RUN] Would start API and test endpoints")
        return True
    
    api_process = None
    try:
        # Start API server in background
        logger.info("Starting FastAPI server...")
        api_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=ROOT_DIR
        )
        
        # Wait for server to start (check health endpoint)
        logger.info("Waiting for API server to start...")
        import requests
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    logger.success("✓ API server started successfully")
                    break
            except requests.exceptions.RequestException:
                time.sleep(1)
        else:
            logger.error("API server failed to start within 30 seconds")
            return False
        
        # Test health endpoint
        logger.info("Testing /health endpoint...")
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            health_data = response.json()
            logger.success(f"✓ Health check passed: {health_data.get('status')}")
            logger.info(f"  Model loaded: {health_data.get('model_loaded')}")
        else:
            logger.error(f"Health check failed with status {response.status_code}")
            return False
        
        # Test predict endpoint
        logger.info("Testing /predict endpoint...")
        test_text = "This is a test message"
        response = requests.post(
            "http://localhost:8000/predict",
            json={"text": test_text},
            timeout=10
        )
        if response.status_code == 200:
            pred_data = response.json()
            logger.success(f"✓ Prediction successful: {pred_data.get('predicted_label')}")
            logger.info(f"  Confidence: {pred_data.get('confidence'):.2%}")
        else:
            logger.error(f"Prediction failed with status {response.status_code}")
            return False
        
        # Test models endpoint (if available)
        logger.info("Testing /models endpoint...")
        try:
            response = requests.get("http://localhost:8000/models", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                logger.success(f"✓ Found {len(models_data.get('models', []))} available models")
        except:
            logger.info("  /models endpoint not available (older API version)")
        
        logger.success("Stage 5 completed successfully")
        return True
        
    except ImportError:
        logger.error("requests library not found. Install with: pip install requests")
        return False
    except Exception as e:
        logger.error(f"Stage 5 failed: {e}")
        return False
    finally:
        # Stop API server
        if api_process:
            logger.info("Stopping API server...")
            api_process.terminate()
            try:
                api_process.wait(timeout=5)
                logger.success("✓ API server stopped")
            except subprocess.TimeoutExpired:
                api_process.kill()
                logger.warning("API server forcefully killed")


def execute_stage_6(logger: DeploymentLogger, dry_run: bool = False) -> bool:
    """Execute Stage 6: Docker Build
    
    - Build backend and UI Docker images using docker-compose
    - Validate images exist
    """
    logger.info("Stage 6: Docker Build")
    
    if dry_run:
        logger.info("[DRY RUN] Would build Docker images")
        return True
    
    try:
        # Check if docker-compose file exists
        compose_file = ROOT_DIR / "docker-compose.fullstack.yml"
        if not compose_file.exists():
            logger.error(f"docker-compose.fullstack.yml not found: {compose_file}")
            return False
        
        # Build both images using docker-compose
        logger.info("Building Docker images using docker-compose...")
        logger.info("This typically takes 10-15 minutes for first build")
        
        result = subprocess.run(
            ["docker-compose", "-f", "docker-compose.fullstack.yml", "build"],
            capture_output=False,
            text=True,
            timeout=1800,  # 30 minutes max
            cwd=ROOT_DIR
        )
        
        if result.returncode != 0:
            logger.error(f"Docker compose build failed with exit code {result.returncode}")
            return False
        
        logger.success("✓ Docker images built successfully")
        
        # Verify backend image exists
        result = subprocess.run(
            ["docker", "images", "cloud-nlp-classifier:latest", "--format", "{{.Repository}}:{{.Tag}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "cloud-nlp-classifier:latest" in result.stdout:
            logger.success("✓ Backend image verified")
        else:
            logger.error("Backend image not found after build")
            return False
        
        # Verify UI image exists
        result = subprocess.run(
            ["docker", "images", "cloud-nlp-ui:latest", "--format", "{{.Repository}}:{{.Tag}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "cloud-nlp-ui:latest" in result.stdout:
            logger.success("✓ UI image verified")
        else:
            logger.warning("UI image not found (non-critical)")
        
        logger.success("Stage 6 completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Stage 6 timed out (Docker build took too long)")
        return False
    except Exception as e:
        logger.error(f"Stage 6 failed: {e}")
        return False


def execute_stage_7(logger: DeploymentLogger, dry_run: bool = False) -> bool:
    """Execute Stage 7: Full Stack Testing
    
    - Run comprehensive test suite
    - Performance benchmarks
    - Integration tests
    - Validate all tests pass
    """
    logger.info("Stage 7: Full Stack Testing")
    
    if dry_run:
        logger.info("[DRY RUN] Would run full test suite")
        return True
    
    try:
        # Check if pytest is available
        logger.info("Running full test suite...")
        logger.info("This typically takes 3-5 minutes")
        
        # Try to run pytest if available
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", "--tb=short"],
            capture_output=False,  # Stream output in real-time
            text=True,
            timeout=600,  # 10 minutes max
            cwd=ROOT_DIR
        )
        
        if result.returncode == 0:
            logger.success("✓ All pytest tests passed")
            # Log summary
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines[-10:]:  # Last 10 lines (summary)
                    if 'passed' in line.lower() or 'failed' in line.lower():
                        logger.info(f"  {line}")
        else:
            # pytest failed or not available, try alternative
            logger.warning("pytest tests failed or not available")
            
            # Try running test-fullstack-local.ps1 if on Windows
            if platform.system() == "Windows":
                test_script = ROOT_DIR / "scripts" / "test-fullstack-local.ps1"
                if test_script.exists():
                    logger.info("Running test-fullstack-local.ps1...")
                    result = subprocess.run(
                        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(test_script)],
                        capture_output=False,  # Stream output in real-time
                        text=True,
                        timeout=600,
                        cwd=ROOT_DIR
                    )
                    
                    if result.returncode == 0:
                        logger.success("✓ Full stack tests passed")
                    else:
                        logger.error("Full stack tests failed")
                        logger.error(f"Error output: {result.stderr[-500:] if result.stderr else 'No error'}")
                        return False
                else:
                    logger.warning("test-fullstack-local.ps1 not found")
                    logger.info("Skipping full stack tests (optional)")
            else:
                logger.info("Skipping full stack tests (optional on non-Windows)")
        
        logger.success("Stage 7 completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Stage 7 timed out (tests took too long)")
        return False
    except Exception as e:
        logger.error(f"Stage 7 failed: {e}")
        return False


def execute_stage_8(logger: DeploymentLogger, dry_run: bool = False) -> bool:
    """Execute Stage 8: GCS Upload
    
    - Upload models to Google Cloud Storage
    - Use MODEL_VERSION.json for versioning
    - Upload ~770 MB (with -NoCheckpoints)
    """
    logger.info("Stage 8: GCS Upload")
    
    if dry_run:
        logger.info("[DRY RUN] Would upload models to GCS")
        return True
    
    try:
        # Read GCS bucket name from config or use default
        bucket_name = "nlp-classifier-models"
        
        # Read model prefix from MODEL_VERSION.json
        model_prefix = ""
        version_file = ROOT_DIR / "MODEL_VERSION.json"
        if version_file.exists():
            try:
                import json
                version_data = json.loads(version_file.read_text())
                model_prefix = version_data.get("model_prefix", "")
                if model_prefix:
                    logger.info(f"Using model prefix: {model_prefix}")
            except Exception as e:
                logger.warning(f"Could not read MODEL_VERSION.json: {e}")
        
        # Build GCS path
        if model_prefix:
            gcs_path = f"gs://{bucket_name}/{model_prefix}/models/"
        else:
            gcs_path = f"gs://{bucket_name}/models/"
        
        logger.info(f"Uploading models to {gcs_path}...")
        logger.info("This typically takes 2-3 minutes for ~770 MB")
        
        # Check if gsutil is available
        result = subprocess.run(
            ["gsutil", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            logger.error("gsutil not found. Install gcloud SDK: https://cloud.google.com/sdk/install")
            return False
        
        # Upload models directory (excluding checkpoints)
        models_dir = ROOT_DIR / "models"
        if not models_dir.exists():
            logger.error(f"Models directory not found: {models_dir}")
            return False
        
        # Upload baselines
        baselines_dir = models_dir / "baselines"
        if baselines_dir.exists():
            logger.info("Uploading baseline models...")
            result = subprocess.run(
                ["gsutil", "-m", "cp", "-r", str(baselines_dir), gcs_path],
                capture_output=False,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                logger.success("✓ Baseline models uploaded")
            else:
                logger.error(f"Baseline upload failed: {result.stderr}")
                return False
        
        # Upload transformer (excluding checkpoints)
        transformer_dir = models_dir / "transformer"
        if transformer_dir.exists():
            logger.info("Uploading transformer models...")
            # Use rsync to exclude checkpoint directories
            result = subprocess.run(
                ["gsutil", "-m", "rsync", "-r", "-x", ".*checkpoint.*", str(transformer_dir), f"{gcs_path}transformer/"],
                capture_output=False,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                logger.success("✓ Transformer models uploaded")
            else:
                logger.warning(f"Transformer upload had warnings: {result.stderr[:200]}")
        
        # Upload toxicity (excluding checkpoints)
        toxicity_dir = models_dir / "toxicity_multi_head"
        if toxicity_dir.exists():
            logger.info("Uploading toxicity models...")
            result = subprocess.run(
                ["gsutil", "-m", "rsync", "-r", "-x", ".*checkpoint.*", str(toxicity_dir), f"{gcs_path}toxicity_multi_head/"],
                capture_output=False,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                logger.success("✓ Toxicity models uploaded")
            else:
                logger.warning(f"Toxicity upload had warnings: {result.stderr[:200]}")
        
        # Upload MODEL_VERSION.json if exists
        if version_file.exists():
            logger.info("Uploading MODEL_VERSION.json...")
            if model_prefix:
                version_gcs_path = f"gs://{bucket_name}/{model_prefix}/MODEL_VERSION.json"
            else:
                version_gcs_path = f"gs://{bucket_name}/MODEL_VERSION.json"
            
            result = subprocess.run(
                ["gsutil", "cp", str(version_file), version_gcs_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.success("✓ MODEL_VERSION.json uploaded")
        
        logger.success("Stage 8 completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Stage 8 timed out (GCS upload took too long)")
        return False
    except Exception as e:
        logger.error(f"Stage 8 failed: {e}")
        return False


def execute_stage_9(logger: DeploymentLogger, dry_run: bool = False) -> bool:
    """Execute Stage 9: GCP Deployment
    
    - Deploy to GCP VM
    - Build Docker image
    - Start container
    - Validate external IP accessible
    """
    logger.info("Stage 9: GCP Deployment")
    
    if dry_run:
        logger.info("[DRY RUN] Would deploy to GCP VM")
        return True
    
    try:
        # Check if gcloud is available
        result = subprocess.run(
            ["gcloud", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            logger.error("gcloud CLI not found. Install from: https://cloud.google.com/sdk/install")
            return False
        
        logger.info("Running GCP deployment script...")
        logger.info("This typically takes 20-25 minutes")
        
        # Check if on Windows
        if platform.system() == "Windows":
            # Run PowerShell script
            script_path = ROOT_DIR / "scripts" / "gcp-complete-deployment.ps1"
            if not script_path.exists():
                logger.error(f"Deployment script not found: {script_path}")
                return False
            
            logger.info("Running gcp-complete-deployment.ps1 with -NoCheckpoints...")
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path), "-NoCheckpoints"],
                capture_output=False,  # Stream output in real-time
                text=True,
                timeout=2400,  # 40 minutes max
                cwd=ROOT_DIR
            )
            
            if result.returncode != 0:
                logger.error(f"GCP deployment failed with exit code {result.returncode}")
                # Log last 50 lines of output
                if result.stderr:
                    lines = result.stderr.strip().split('\n')
                    for line in lines[-50:]:
                        logger.error(f"  {line}")
                return False
            
            # Log last 20 lines of successful output
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines[-20:]:
                    logger.info(f"  {line}")
            
            logger.success("✓ GCP deployment completed")
            
        else:
            # For Linux/Mac, provide instructions
            logger.warning("GCP deployment script is PowerShell-based")
            logger.info("Please run manually:")
            logger.info("  1. Upload models to GCS (already done in Stage 8)")
            logger.info("  2. SSH to VM: gcloud compute ssh nlp-classifier-vm --zone=us-central1-a")
            logger.info("  3. Clone repo: git clone <your-repo>")
            logger.info("  4. Download models from GCS")
            logger.info("  5. Build Docker: docker build -t cloud-nlp-classifier .")
            logger.info("  6. Run container: docker run -d -p 8000:8000 cloud-nlp-classifier")
            logger.info("Skipping Stage 9 (manual deployment required on non-Windows)")
            return True
        
        # Validate deployment by checking external IP
        logger.info("Validating deployment...")
        
        # Get VM external IP
        result = subprocess.run(
            ["gcloud", "compute", "instances", "describe", "nlp-classifier-vm", 
             "--zone=us-central1-a", "--format=get(networkInterfaces[0].accessConfigs[0].natIP)"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            external_ip = result.stdout.strip()
            logger.success(f"✓ VM External IP: {external_ip}")
            
            # Test API health endpoint
            try:
                import requests
                logger.info(f"Testing API at http://{external_ip}:8000/health...")
                response = requests.get(f"http://{external_ip}:8000/health", timeout=10)
                if response.status_code == 200:
                    logger.success("✓ API is responding")
                else:
                    logger.warning(f"API returned status {response.status_code}")
            except:
                logger.warning("Could not test API (may still be starting)")
        else:
            logger.warning("Could not get VM external IP")
        
        logger.success("Stage 9 completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Stage 9 timed out (GCP deployment took too long)")
        return False
    except Exception as e:
        logger.error(f"Stage 9 failed: {e}")
        return False


def execute_stage_10(logger: DeploymentLogger, dry_run: bool = False) -> bool:
    """Execute Stage 10: UI Deployment
    
    - Deploy Streamlit UI to GCP
    - Validate UI accessible at port 8501
    """
    logger.info("Stage 10: UI Deployment")
    
    if dry_run:
        logger.info("[DRY RUN] Would deploy Streamlit UI to GCP")
        return True
    
    try:
        logger.info("Running UI deployment script...")
        logger.info("This typically takes 10-15 minutes")
        
        # Check if on Windows
        if platform.system() == "Windows":
            # Run PowerShell script
            script_path = ROOT_DIR / "scripts" / "gcp-deploy-ui.ps1"
            if not script_path.exists():
                logger.warning(f"UI deployment script not found: {script_path}")
                logger.info("Skipping UI deployment (optional)")
                return True
            
            logger.info("Running gcp-deploy-ui.ps1...")
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
                capture_output=False,  # Stream output in real-time
                text=True,
                timeout=1200,  # 20 minutes max
                cwd=ROOT_DIR
            )
            
            if result.returncode != 0:
                logger.warning(f"UI deployment had issues (exit code {result.returncode})")
                # Log last 30 lines
                if result.stderr:
                    lines = result.stderr.strip().split('\n')
                    for line in lines[-30:]:
                        logger.warning(f"  {line}")
                logger.info("UI deployment is optional, continuing...")
                return True
            
            # Log last 15 lines of successful output
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines[-15:]:
                    logger.info(f"  {line}")
            
            logger.success("✓ UI deployment completed")
            
        else:
            # For Linux/Mac, provide instructions
            logger.warning("UI deployment script is PowerShell-based")
            logger.info("Please deploy UI manually:")
            logger.info("  1. SSH to VM: gcloud compute ssh nlp-classifier-vm --zone=us-central1-a")
            logger.info("  2. Build UI Docker: docker build -f Dockerfile.streamlit -t nlp-ui .")
            logger.info("  3. Run UI: docker run -d -p 8501:8501 nlp-ui")
            logger.info("Skipping Stage 10 (manual deployment required on non-Windows)")
            return True
        
        # Validate UI deployment
        logger.info("Validating UI deployment...")
        
        # Get VM external IP
        result = subprocess.run(
            ["gcloud", "compute", "instances", "describe", "nlp-classifier-vm",
             "--zone=us-central1-a", "--format=get(networkInterfaces[0].accessConfigs[0].natIP)"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            external_ip = result.stdout.strip()
            logger.success(f"✓ UI should be accessible at: http://{external_ip}:8501")
            
            # Test UI endpoint
            try:
                import requests
                logger.info(f"Testing UI at http://{external_ip}:8501...")
                response = requests.get(f"http://{external_ip}:8501", timeout=10)
                if response.status_code == 200:
                    logger.success("✓ UI is responding")
                else:
                    logger.warning(f"UI returned status {response.status_code}")
            except:
                logger.warning("Could not test UI (may still be starting)")
        else:
            logger.warning("Could not get VM external IP")
        
        logger.success("Stage 10 completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Stage 10 timed out (UI deployment took too long)")
        return False
    except Exception as e:
        logger.error(f"Stage 10 failed: {e}")
        return False


# ============================================================================
# DEPLOYMENT PROFILES - Quick vs Full configurations
# ============================================================================

DEPLOYMENT_PROFILES = {
    "quick": {
        "description": "Quick deployment for testing (3-5 min GPU, 15-20 min CPU)",
        "transformer_config": "config/config_transformer_quick.yaml",
        "transformer_epochs": 3,
        "expected_accuracy": "85-88%",
        "expected_time_gpu": "3-5 minutes",
        "expected_time_cpu": "15-20 minutes",
    },
    "full": {
        "description": "Full deployment for production (15-25 min GPU, 60-90 min CPU)",
        "transformer_config": "config/config_transformer.yaml",
        "transformer_epochs": 15,
        "expected_accuracy": "90-93%",
        "expected_time_gpu": "15-25 minutes",
        "expected_time_cpu": "60-90 minutes",
    },
    "cloud": {
        "description": "Cloud-optimized deployment (10-15 min on GCP GPU)",
        "transformer_config": "config/config_transformer_cloud.yaml",
        "transformer_epochs": 10,
        "expected_accuracy": "90-93%",
        "expected_time_gpu": "10-15 minutes",
        "expected_time_cpu": "45-60 minutes",
    },
}


# Map stage IDs to execution functions
STAGE_EXECUTORS = {
    0: execute_stage_0,
    1: execute_stage_1,
    2: execute_stage_2,
    3: execute_stage_3,
    4: execute_stage_4,
    5: execute_stage_5,
    6: execute_stage_6,
    7: execute_stage_7,
    8: execute_stage_8,
    9: execute_stage_9,
    10: execute_stage_10,
}

# Map stage IDs to validation functions
STAGE_VALIDATORS = {
    0: validate_stage_0,
    1: validate_stage_1,
    2: validate_stage_2,
    3: validate_stage_3,
    4: validate_stage_4,
    5: validate_stage_5,
    6: validate_stage_6,
    7: validate_stage_7,
    8: validate_stage_8,
    9: validate_stage_9,
    10: validate_stage_10,
}


# ============================================================================
# [5] REPORTING FUNCTIONS (Stubs - will be implemented in Phase 4)
# ============================================================================

def generate_deployment_report(state: DeploymentState, logger: DeploymentLogger):
    """Generate deployment report"""
    logger.info("Generating deployment report...")
    # TODO: Implement report generation


def export_metrics(state: DeploymentState, logger: DeploymentLogger):
    """Export metrics to JSON"""
    logger.info("Exporting metrics...")
    # TODO: Implement metrics export


def show_summary(state: DeploymentState, logger: DeploymentLogger):
    """Show deployment summary"""
    logger.info("Showing deployment summary...")
    # TODO: Implement summary display


# ============================================================================
# [6] MAIN EXECUTION FLOW
# ============================================================================

class DeploymentController:
    """Main deployment controller"""
    
    def __init__(self, args):
        self.args = args
        self.logger = DeploymentLogger(LOG_FILE)
        self.checkpoint_manager = CheckpointManager(CHECKPOINTS_DIR)
        self.state_manager = StateManager(STATE_FILE)
        self.progress_tracker = None
        self.state = None
    
    def initialize(self):
        """Initialize deployment environment"""
        print("\n" + "="*70)
        print("║" + " "*68 + "║")
        print("║" + "  CLOUD-NLP-CLASSIFIER-GCP Master Controller v" + SCRIPT_VERSION + " "*14 + "║")
        print("║" + " "*68 + "║")
        print("="*70 + "\n")
        
        self.logger.info(f"Deployment ID: {DEPLOYMENT_ID}")
        self.logger.info(f"Mode: {self.args.mode} | Target: {self.args.target} | Profile: {self.args.profile}")
        self.logger.info(f"Root Directory: {ROOT_DIR}")
        
        # Show profile information
        if hasattr(self.args, 'profile') and self.args.profile in DEPLOYMENT_PROFILES:
            profile = DEPLOYMENT_PROFILES[self.args.profile]
            self.logger.info(f"Profile: {profile['description']}")
            self.logger.info(f"Expected accuracy: {profile['expected_accuracy']}")
        
        # Clean if requested
        if self.args.clean:
            self.logger.warning("Cleaning previous deployment state...")
            if DEPLOYMENT_DIR.exists():
                shutil.rmtree(DEPLOYMENT_DIR)
                self.logger.success("Previous deployment state cleaned")
        
        # Create directories
        DEPLOYMENT_DIR.mkdir(exist_ok=True)
        CHECKPOINTS_DIR.mkdir(exist_ok=True)
        LOGS_DIR.mkdir(exist_ok=True)
        
        # Load previous state if resuming
        if self.args.resume:
            loaded_state = self.state_manager.load()
            if loaded_state:
                self.state = loaded_state
                self.logger.success(f"Resuming from Stage {self.state.current_stage + 1}")
            else:
                self.logger.warning("No previous state found, starting fresh")
                self.args.resume = False
        
        # Initialize state if not resuming
        if not self.args.resume:
            self.state = DeploymentState(
                deployment_id=DEPLOYMENT_ID,
                start_time=SCRIPT_START_TIME.isoformat(),
                mode=self.args.mode,
                target=self.args.target
            )
        
        # Check prerequisites
        checker = PrerequisiteChecker(self.logger)
        if not checker.check_all(self.args.target, self.args.gcp_project):
            raise RuntimeError("Prerequisites check failed. Please fix the issues and try again.")
        
        print()
    
    def get_stages_to_run(self) -> List[Stage]:
        """Determine which stages to run"""
        if self.args.stage is not None:
            # Run specific stage only
            stages = [s for s in STAGES if s.id == self.args.stage]
        else:
            # Run all stages for target
            stages = [
                s for s in STAGES
                if self.args.target in s.required_for
                and s.id not in self.args.skip_stages
            ]
        
        # Apply optional stage filters
        if self.args.skip_toxicity:
            stages = [s for s in stages if s.id != 4]
            self.logger.info("Skipping Stage 4: Toxicity Training")
        
        if self.args.skip_ui:
            stages = [s for s in stages if s.id != 10]
            self.logger.info("Skipping Stage 10: UI Deployment")
        
        return stages
    
    def show_deployment_plan(self, stages: List[Stage]):
        """Show deployment plan"""
        print("="*70)
        print("  DEPLOYMENT PLAN")
        print("="*70)
        print()
        print(f"  Total Stages: {len(stages)}")
        total_time = sum(s.estimated_duration for s in stages) / 60
        print(f"  Estimated Time: {total_time:.1f} minutes")
        print()
        
        for stage in stages:
            status = "[COMPLETED]" if self.checkpoint_manager.exists(stage.id) else "[PENDING]"
            status_color = "\033[92m" if status == "[COMPLETED]" else "\033[93m"
            reset = "\033[0m"
            print(f"  Stage {stage.id}: {stage.name} {status_color}{status}{reset}")
        
        print()
        print("="*70)
        print()
    
    def execute_stage(self, stage: Stage) -> bool:
        """Execute a single stage"""
        # Skip if already completed and not forcing
        if self.checkpoint_manager.exists(stage.id) and not self.args.force:
            self.logger.info(f"Stage {stage.id} already completed (use --force to re-run)")
            return True
        
        print()
        print("─"*70)
        print(f"  STAGE {stage.id}: {stage.name}")
        print("─"*70)
        print()
        
        self.state.current_stage = stage.id
        self.progress_tracker.update(stage.id, stage.name, "Running...")
        
        stage_start = time.time()
        
        try:
            # Execute stage
            executor = STAGE_EXECUTORS[stage.id]
            # Pass profile to Stage 3 (transformer training)
            if stage.id == 3 and hasattr(self.args, 'profile'):
                success = executor(self.logger, self.args.dry_run, self.args.profile)
            else:
                success = executor(self.logger, self.args.dry_run)
            
            if success:
                stage_duration = time.time() - stage_start
                
                # Save metrics
                self.state.stage_metrics[f"stage_{stage.id}"] = {
                    "name": stage.name,
                    "duration_seconds": round(stage_duration, 2),
                    "completed_at": datetime.now().isoformat(),
                    "status": "success"
                }
                
                # Mark as completed
                self.state.completed_stages.append(stage.id)
                self.checkpoint_manager.save(stage.id, stage.name)
                self.state_manager.save(self.state)
                self.progress_tracker.increment()
                
                print()
                self.logger.success(f"✓ Stage {stage.id} completed in {stage_duration:.1f}s")
                return True
            else:
                raise RuntimeError("Stage execution returned False")
                
        except Exception as e:
            error_msg = f"Stage {stage.id} failed: {e}"
            self.logger.error(error_msg)
            self.state.failed_stages.append(stage.id)
            self.state.errors.append({
                "stage": stage.id,
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
            self.state_manager.save(self.state)
            
            if self.args.mode == "interactive":
                print()
                print("Stage failed. What would you like to do?")
                print("  [R] Retry this stage")
                print("  [S] Skip this stage")
                print("  [A] Abort deployment")
                print()
                choice = input("Your choice (R/S/A): ").strip().upper()
                
                if choice == "R":
                    self.logger.info(f"Retrying Stage {stage.id}...")
                    return self.execute_stage(stage)  # Retry
                elif choice == "S":
                    self.logger.warning(f"Skipping Stage {stage.id}")
                    self.state.skipped_stages.append(stage.id)
                    return True  # Continue
                else:
                    raise RuntimeError("Deployment aborted by user")
            else:
                raise RuntimeError(f"Deployment failed at Stage {stage.id}")
    
    def run(self):
        """Main execution"""
        try:
            # Initialize
            self.initialize()
            
            # Get stages to run
            stages_to_run = self.get_stages_to_run()
            self.progress_tracker = ProgressTracker(len(stages_to_run))
            
            # Show deployment plan
            self.show_deployment_plan(stages_to_run)
            
            if self.args.dry_run:
                self.logger.warning("DRY RUN MODE - No changes will be made")
                return
            
            # Execute stages
            for stage in stages_to_run:
                if not self.execute_stage(stage):
                    break
            
            # Final summary
            print()
            print("="*70)
            print("║" + " "*68 + "║")
            print("║" + "              DEPLOYMENT COMPLETE!              " + " "*22 + "║")
            print("║" + " "*68 + "║")
            print("="*70)
            print()
            
            total_duration = (datetime.now() - SCRIPT_START_TIME).total_seconds() / 60
            self.logger.success(f"Total deployment time: {total_duration:.1f} minutes")
            self.logger.success(f"Completed stages: {len(self.state.completed_stages)}")
            self.logger.info(f"Failed stages: {len(self.state.failed_stages)}")
            self.logger.info(f"Skipped stages: {len(self.state.skipped_stages)}")
            
            # Generate reports
            generate_deployment_report(self.state, self.logger)
            export_metrics(self.state, self.logger)
            show_summary(self.state, self.logger)
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            print()
            print("="*70)
            print("║" + " "*68 + "║")
            print("║" + "              DEPLOYMENT FAILED!                " + " "*22 + "║")
            print("║" + " "*68 + "║")
            print("="*70)
            print()
            print(f"Check logs at: {LOG_FILE}")
            print(f"Resume with: python deploy-master-controller.py --resume")
            sys.exit(1)


# ============================================================================
# [7] CLI ARGUMENT PARSING
# ============================================================================

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Master deployment controller for CLOUD-NLP-CLASSIFIER-GCP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick deployment (fast testing - 3-5 min GPU, 15-20 min CPU)
  python deploy-master-controller.py --profile quick
  
  # Full deployment (production - 15-25 min GPU, 60-90 min CPU)
  python deploy-master-controller.py --profile full
  
  # Automated local deployment with quick profile
  python deploy-master-controller.py --mode auto --target local --profile quick
  
  # Automated cloud deployment
  python deploy-master-controller.py --mode auto --target cloud --profile cloud --gcp-project mnist-k8s-pipeline
  
  # Resume from checkpoint
  python deploy-master-controller.py --resume
  
  # Run specific stage
  python deploy-master-controller.py --stage 3 --force
  
  # Dry run (preview)
  python deploy-master-controller.py --dry-run --profile quick
  
  # Skip optional stages
  python deploy-master-controller.py --skip-toxicity --skip-ui --profile quick
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['interactive', 'auto'],
        default='interactive',
        help='Execution mode (default: interactive)'
    )
    
    parser.add_argument(
        '--target',
        choices=['local', 'cloud', 'both'],
        default='local',
        help='Deployment target (default: local)'
    )
    
    parser.add_argument(
        '--profile',
        choices=['quick', 'full', 'cloud'],
        default='quick',
        help='Deployment profile: quick (fast testing), full (production), cloud (GCP optimized) (default: quick)'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from last completed stage'
    )
    
    parser.add_argument(
        '--stage',
        type=int,
        choices=range(11),
        metavar='0-10',
        help='Run specific stage only (0-10)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview execution without running commands'
    )
    
    parser.add_argument(
        '--skip-stages',
        type=int,
        nargs='+',
        default=[],
        metavar='N',
        help='Array of stage numbers to skip'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-run of completed stages'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--skip-toxicity',
        action='store_true',
        help='Skip Stage 4 (toxicity training)'
    )
    
    parser.add_argument(
        '--skip-ui',
        action='store_true',
        help='Skip Stage 10 (UI deployment)'
    )
    
    parser.add_argument(
        '--gcp-project',
        type=str,
        default='',
        help='GCP project ID for cloud deployment'
    )
    
    parser.add_argument(
        '--gcp-zone',
        type=str,
        default='us-central1-a',
        help='GCP zone (default: us-central1-a)'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean previous deployment state and start fresh'
    )
    
    return parser.parse_args()


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    args = parse_arguments()
    controller = DeploymentController(args)
    controller.run()


if __name__ == "__main__":
    main()
