# DistilBERT Training Stall - Diagnosis & Solutions

## 🔍 Common Causes of Training "Stalls"

### 1. **Tokenization Phase (Most Likely)**

**What's happening:**
The training appears to stall during the **tokenization phase**, which happens BEFORE actual training begins.

**Why it seems stuck:**
- Tokenizing 21,000+ samples with `max_length=256` or `max_length=512` takes time
- With our updated config: **256 tokens per sample** (Standard) or **512 tokens** (Intensive)
- No progress bar is shown during tokenization by default
- CPU-intensive operation that can take 2-10 minutes

**Expected Duration:**
- **Standard config (256 seq):** 2-5 minutes for tokenization
- **Intensive config (512 seq):** 5-10 minutes for tokenization

**What you'll see in console:**
```
Tokenizing data...
[APPEARS TO HANG HERE - BUT IT'S WORKING!]
Tokenization complete!
```

### 2. **Model Download (First Run Only)**

**What's happening:**
First time running, DistilBERT model (~250 MB) is downloaded from HuggingFace.

**Expected Duration:** 1-3 minutes (depending on internet speed)

**What you'll see:**
```
Loading model: distilbert-base-uncased
Downloading: 100%|████████| 268M/268M [00:45<00:00, 5.95MB/s]
```

### 3. **First Training Step (Compilation)**

**What's happening:**
PyTorch compiles the model on first forward pass.

**Expected Duration:** 30-60 seconds

**What you'll see:**
```
Starting training...
[Brief pause while model compiles]
Epoch 1/15: 0%|          | 0/330 [00:00<?, ?it/s]
```

### 4. **DataLoader Workers (Windows Issue)**

**What's happening:**
On Windows, `dataloader_num_workers > 0` can cause hangs due to multiprocessing issues.

**Our config has:**
- Standard: `dataloader_num_workers: 2`
- Intensive: `dataloader_num_workers: 4`

**This can cause indefinite hangs on Windows!**

---

## ✅ How to Diagnose

### Check Console Output

Look for the **last message** you see:

#### Scenario A: Stuck at "Tokenizing data..."
```
Tokenizing data...
[STUCK HERE]
```
**Diagnosis:** Tokenization in progress (normal, wait 2-10 minutes)  
**Action:** Be patient, it's working!

#### Scenario B: Stuck at "Starting training..."
```
Starting training...
[STUCK HERE - NO PROGRESS BAR]
```
**Diagnosis:** DataLoader worker issue (Windows) or model compilation  
**Action:** See Fix #1 below

#### Scenario C: Stuck at "0/330 [00:00<?, ?it/s]"
```
Epoch 1/15: 0%|          | 0/330 [00:00<?, ?it/s]
[STUCK HERE]
```
**Diagnosis:** DataLoader worker deadlock (Windows)  
**Action:** See Fix #1 below

#### Scenario D: Progress bar moving but VERY slow
```
Epoch 1/15: 1%|▏         | 3/330 [05:23<9:45:12, 107.36s/it]
```
**Diagnosis:** CPU training (expected, very slow)  
**Action:** See Performance section below

---

## 🔧 Immediate Fixes

### Fix #1: Disable DataLoader Workers (Windows)

**Problem:** Windows multiprocessing causes hangs with `num_workers > 0`

**Solution:** Set `dataloader_num_workers: 0` in config

#### For Standard Config:
```bash
# Edit config/config_transformer.yaml
# Change line 33:
dataloader_num_workers: 0  # Was: 2
```

#### For Intensive Config:
```bash
# Edit config/config_transformer_fullscale.yaml
# Change line 77:
dataloader_num_workers: 0  # Was: 4
```

#### Quick Fix Script:
```powershell
# Run this in PowerShell to fix both configs
(Get-Content config\config_transformer.yaml) -replace 'dataloader_num_workers: 2', 'dataloader_num_workers: 0' | Set-Content config\config_transformer.yaml

(Get-Content config\config_transformer_fullscale.yaml) -replace 'dataloader_num_workers: 4', 'dataloader_num_workers: 0' | Set-Content config\config_transformer_fullscale.yaml
```

### Fix #2: Add Verbose Tokenization

To see progress during tokenization, we can add a progress indicator.

**Create a quick test script:**
```python
# test_tokenization.py
import yaml
from transformers import DistilBertTokenizer
from datasets import Dataset
import pandas as pd

# Load config
with open('config/config_transformer.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Load data
train_df = pd.read_csv('data/processed/train.csv')
print(f"Loaded {len(train_df)} samples")

# Load tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
print("Tokenizer loaded")

# Create dataset
dataset = Dataset.from_dict({'text': train_df['text'].tolist()})
print("Dataset created")

# Tokenize with progress
print("Tokenizing... (this may take 2-5 minutes)")
tokenized = dataset.map(
    lambda x: tokenizer(x['text'], padding='max_length', truncation=True, max_length=256),
    batched=True,
    desc="Tokenizing"  # Shows progress bar
)
print("Tokenization complete!")
```

Run: `python test_tokenization.py`

---

## 📊 Expected Training Times

### Standard Configuration (256 seq, 15 epochs)

| Hardware | Tokenization | First Epoch | Total Training |
|----------|--------------|-------------|----------------|
| CPU (8 cores) | 3-5 min | 15-20 min | 4-8 hours |
| GPU (RTX 3060) | 2-3 min | 2-3 min | 30-60 min |
| GPU (T4) | 2-3 min | 3-4 min | 45-75 min |

### Intensive Configuration (512 seq, 25 epochs)

| Hardware | Tokenization | First Epoch | Total Training |
|----------|--------------|-------------|----------------|
| CPU (8 cores) | 5-10 min | 30-40 min | 10-20 hours |
| GPU (RTX 3060) | 3-5 min | 5-8 min | 2-4 hours |
| GPU (T4) | 3-5 min | 6-10 min | 3-5 hours |

### Signs Training is Working (Not Stalled)

✅ **CPU Usage:** Should be 80-100% (CPU training) or 10-30% (GPU training)  
✅ **Memory Usage:** Gradually increasing to 8-12 GB  
✅ **GPU Usage:** 90-100% if using GPU  
✅ **Disk Activity:** Occasional writes (checkpoints)  

---

## 🚨 How to Tell if ACTUALLY Stuck

### Use Task Manager / Resource Monitor

**Windows:**
1. Open Task Manager (Ctrl+Shift+Esc)
2. Go to "Performance" tab
3. Check:
   - **CPU:** Should be 50-100% usage
   - **Memory:** Should be increasing
   - **GPU:** Should be 80-100% if using GPU

**If ALL are at 0% for 5+ minutes:** Process is actually stuck

### Check Python Process

```powershell
# Check if Python is using CPU
Get-Process python | Select-Object CPU, WorkingSet, ProcessName

# If CPU is 0 for 5+ minutes, it's stuck
```

---

## 🔄 Recovery Steps

### If Training is Actually Stuck:

#### Step 1: Kill the Process
```powershell
# Find Python processes
Get-Process python

# Kill all Python processes
Stop-Process -Name python -Force
```

#### Step 2: Apply Fix #1 (Disable DataLoader Workers)
```powershell
# Fix both configs
(Get-Content config\config_transformer.yaml) -replace 'dataloader_num_workers: 2', 'dataloader_num_workers: 0' | Set-Content config\config_transformer.yaml

(Get-Content config\config_transformer_fullscale.yaml) -replace 'dataloader_num_workers: 4', 'dataloader_num_workers: 0' | Set-Content config\config_transformer_fullscale.yaml
```

#### Step 3: Restart Training
```bash
python train_all_models.py
```

---

## 🎯 Recommended Approach

### Option 1: Quick Test First (Recommended)

Test with minimal config to verify everything works:

```bash
# Train with just 3 epochs to test
python -m src.models.transformer_training --epochs 3 --batch-size 32
```

**Expected time:** 15-30 min (GPU) or 1-2 hours (CPU)

If this works, proceed to full training.

### Option 2: Train Models Separately

Instead of training all at once, train individually:

```bash
# 1. Baseline models (5-15 min)
python run_baselines.py

# 2. Standard transformer (30-60 min GPU)
python run_transformer.py

# 3. Intensive transformer (2-4 hours GPU)
python -m src.models.transformer_training --config config/config_transformer_fullscale.yaml
```

This way, if one stalls, you don't lose progress on others.

### Option 3: Use CPU-Friendly Config

Create a CPU-optimized config:

```yaml
# config/config_transformer_cpu.yaml
training:
  train_batch_size: 16  # Smaller batch
  num_train_epochs: 5   # Fewer epochs
  dataloader_num_workers: 0  # No workers
  gradient_accumulation_steps: 1  # No accumulation
  
model:
  max_seq_length: 128  # Shorter sequences
```

Run: `python -m src.models.transformer_training --config config/config_transformer_cpu.yaml`

---

## 📝 Monitoring Commands

### Real-Time Monitoring

```powershell
# Monitor CPU/Memory every 2 seconds
while ($true) {
    Get-Process python | Select-Object CPU, WorkingSet, ProcessName
    Start-Sleep -Seconds 2
}
```

### Check GPU (if available)

```bash
# Install nvidia-smi if you have NVIDIA GPU
nvidia-smi -l 1  # Update every 1 second
```

---

## 🎓 Understanding the Training Process

### Phase 1: Initialization (1-3 minutes)
- Load configuration
- Download model (first time only)
- Load data files
- Initialize tokenizer

### Phase 2: Tokenization (2-10 minutes) ⚠️ APPEARS TO HANG
- Convert text to tokens
- Pad/truncate to max_length
- Create attention masks
- **NO PROGRESS BAR BY DEFAULT**

### Phase 3: Model Setup (30-60 seconds)
- Initialize model
- Setup optimizer
- Setup learning rate scheduler
- Setup callbacks

### Phase 4: Training (30 min - 20 hours)
- **Shows progress bar**
- Logs every N steps
- Evaluates every N steps
- Saves checkpoints

### Phase 5: Evaluation (1-2 minutes)
- Test set evaluation
- Inference time measurement
- Save results

---

## ✅ Verification Checklist

Before assuming it's stuck, verify:

- [ ] Waited at least 5 minutes after "Tokenizing data..." message
- [ ] Checked Task Manager - CPU/Memory usage is active
- [ ] No error messages in console
- [ ] Python process is still running
- [ ] Disk space available (need ~2-5 GB)
- [ ] Not running other heavy processes

---

## 🆘 Still Stuck? Try This

### Emergency Minimal Test

```python
# minimal_test.py - Test if transformers work at all
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch

print("Loading tokenizer...")
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
print("✓ Tokenizer loaded")

print("Loading model...")
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
print("✓ Model loaded")

print("Testing tokenization...")
text = "This is a test sentence"
tokens = tokenizer(text, return_tensors='pt', padding='max_length', max_length=128)
print("✓ Tokenization works")

print("Testing forward pass...")
with torch.no_grad():
    output = model(**tokens)
print("✓ Forward pass works")

print("\n✅ All basic operations work!")
```

Run: `python minimal_test.py`

If this fails, there's a deeper issue with your environment.

---

## 📞 Summary

**Most likely:** Training is NOT stuck, it's in the tokenization phase (2-10 min)

**Quick fix:** Set `dataloader_num_workers: 0` in both config files

**Patience required:** First epoch takes longest (model compilation + warmup)

**Monitor:** Use Task Manager to verify CPU/Memory activity

**Alternative:** Train models separately instead of all at once
