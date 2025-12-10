# Cross-Platform Python Scripts Guide

## 🌍 Overview

We've created **cross-platform Python wrapper scripts** that work on **Windows, Linux, and Mac** without modification. These scripts replace the need for platform-specific shell scripts (`.ps1`, `.sh`).

## ✨ Benefits

- ✅ **Works everywhere**: Windows, Linux, Mac
- ✅ **No shell knowledge needed**: Just Python
- ✅ **Built-in checks**: Validates dependencies and data
- ✅ **Better error messages**: Clear, colored output
- ✅ **Consistent experience**: Same commands on all platforms

## 📝 Available Scripts

### 1. `run_preprocess.py` - Data Preprocessing

Preprocesses raw data and creates train/val/test splits.

**Usage:**
```bash
python run_preprocess.py
```

**What it does:**
- ✓ Checks if dependencies are installed
- ✓ Verifies raw data exists (`data/raw/dataset.csv`)
- ✓ Runs preprocessing pipeline
- ✓ Creates processed splits in `data/processed/`

**Output:**
- `data/processed/train.csv`
- `data/processed/val.csv`
- `data/processed/test.csv`

---

### 2. `run_baselines.py` - Baseline Model Training

Trains classical ML models (TF-IDF + Logistic Regression/SVM).

**Usage:**
```bash
python run_baselines.py
```

**What it does:**
- ✓ Checks if dependencies are installed
- ✓ Verifies processed data exists
- ✓ Trains baseline models
- ✓ Saves models to `models/baselines/`

**Output:**
- `models/baselines/*.joblib` (trained models)
- Performance metrics in console

---

### 3. `run_transformer.py` - Transformer Model Training

Fine-tunes DistilBERT for text classification.

**Usage:**
```bash
python run_transformer.py
```

**What it does:**
- ✓ Checks if all dependencies are installed (torch, transformers, etc.)
- ✓ Verifies processed data exists
- ✓ Runs transformer training pipeline
- ✓ Saves model to `models/transformer/distilbert/`

**Output:**
- `models/transformer/distilbert/` (model, tokenizer, labels)
- `training_info.json` (metrics and timing)

**Time estimates:**
- CPU: 30-60 minutes (full training)
- GPU: 5-15 minutes (full training)

---

### 4. `run_tests.py` - Test Suite

Runs all Phase 3 tests to verify the trained model.

**Usage:**
```bash
python run_tests.py
```

**What it does:**
- ✓ Runs model loading test
- ✓ Runs inference test
- ✓ Runs metrics validation test
- ✓ Provides summary of results

**Tests included:**
1. Model Loading - Verifies model can be loaded
2. Inference - Tests predictions on sample texts
3. Metrics Validation - Checks training metrics are valid

---

## 🚀 Complete Workflow

Here's the complete workflow using the cross-platform scripts:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download dataset (if needed)
python scripts/download_dataset.py

# 3. Preprocess data
python run_preprocess.py

# 4. Train baseline models
python run_baselines.py

# 5. Train transformer model
python run_transformer.py

# 6. Run tests
python run_tests.py
```

---

## 🎨 Features

### Colored Output

All scripts provide colored output for better readability:
- 🔵 **Cyan**: Headers and section titles
- 🟢 **Green**: Success messages
- 🔴 **Red**: Error messages
- 🟡 **Yellow**: Warnings and test names

### Dependency Checking

Each script automatically checks if required dependencies are installed:

```
Checking dependencies...
  ✓ PyTorch installed
  ✓ Transformers installed
  ✓ Datasets installed
  ✓ scikit-learn installed
  ✓ Pandas installed
  ✓ NumPy installed
  ✓ PyYAML installed

✓ All dependencies installed!
```

If dependencies are missing:
```
  ✗ Transformers NOT installed

❌ Missing dependencies: Transformers

Please install them using:
  pip install -r requirements.txt
```

### Data Validation

Scripts verify that required data files exist before running:

```
Checking data files...
  ✓ data/processed/train.csv exists
  ✓ data/processed/val.csv exists
  ✓ data/processed/test.csv exists

✓ All data files found!
```

### Progress Tracking

Clear progress indicators throughout execution:

```
==========================================
Starting Transformer Training Pipeline
==========================================

Checking dependencies...
✓ All dependencies installed!

Checking data files...
✓ All data files found!

==========================================
Running training...
==========================================
[Training output...]
```

---

## 🔧 Troubleshooting

### Issue: "No module named 'transformers'"

**Solution:**
```bash
pip install -r requirements.txt
```

Or install specific packages:
```bash
pip install torch transformers datasets
```

### Issue: "Data files not found"

**Solution:**
Run preprocessing first:
```bash
python run_preprocess.py
```

### Issue: "Raw data not found"

**Solution:**
Download the dataset:
```bash
python scripts/download_dataset.py
```

Or manually place your dataset at `data/raw/dataset.csv` with columns: `text`, `label`

### Issue: Script doesn't have execute permissions (Linux/Mac)

**Solution:**
```bash
chmod +x run_transformer.py
./run_transformer.py
```

Or just use Python directly:
```bash
python run_transformer.py
```

---

## 📊 Comparison with Shell Scripts

### Old Way (Platform-Specific)

**Windows:**
```powershell
.\scripts\run_transformer_local.ps1
```

**Linux/Mac:**
```bash
bash scripts/run_transformer_local.sh
```

**Problems:**
- Different commands for different platforms
- No dependency checking
- Basic error messages
- Requires shell knowledge

### New Way (Cross-Platform)

**All Platforms:**
```bash
python run_transformer.py
```

**Benefits:**
- Same command everywhere
- Built-in dependency checking
- Clear, colored error messages
- Works with just Python knowledge

---

## 🎯 Best Practices

### 1. Always Check Dependencies First

Before running any script, ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

### 2. Run Scripts in Order

Follow the workflow order:
1. Preprocess → 2. Baselines → 3. Transformer → 4. Tests

### 3. Use Virtual Environments

Always use a virtual environment:
```bash
# Create
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Check Outputs

After each script, verify the outputs:
```bash
# After preprocessing
ls data/processed/

# After baseline training
ls models/baselines/

# After transformer training
ls models/transformer/distilbert/
```

### 5. Save Logs

Save script output for debugging:
```bash
python run_transformer.py > training_log.txt 2>&1
```

---

## 💡 Advanced Usage

### Running with Custom Python

If you have multiple Python versions:
```bash
python3 run_transformer.py
# or
python3.11 run_transformer.py
```

### Running in Background (Linux/Mac)

```bash
nohup python run_transformer.py > training.log 2>&1 &
```

### Running with Environment Variables

```bash
# Set device to CPU
export DEVICE=cpu
python run_transformer.py
```

---

## 📝 Script Internals

Each script follows this structure:

1. **Import dependencies**
2. **Define helper functions** (colored output, checks)
3. **Check prerequisites** (dependencies, data)
4. **Run main task** (training, testing, etc.)
5. **Handle errors** (graceful error messages)
6. **Provide next steps** (what to do after success)

Example structure:
```python
#!/usr/bin/env python3
"""Cross-platform script description"""

def print_header(message):
    """Print colored header"""
    
def check_dependencies():
    """Check if dependencies are installed"""
    
def check_data():
    """Check if data exists"""
    
def run_main_task():
    """Run the main task"""
    
def main():
    """Main entry point"""
    
if __name__ == "__main__":
    main()
```

---

## ✅ Summary

The new cross-platform Python scripts provide:

- ✅ **Universal compatibility**: Works on all platforms
- ✅ **Better UX**: Colored output, clear messages
- ✅ **Built-in validation**: Checks dependencies and data
- ✅ **Error handling**: Graceful error messages
- ✅ **Consistent workflow**: Same commands everywhere

**Recommended usage:**
```bash
# Use these instead of shell scripts
python run_preprocess.py
python run_baselines.py
python run_transformer.py
python run_tests.py
```

The old shell scripts (`.ps1`, `.sh`) are still available but the Python scripts are now the **recommended way** to run the pipeline! 🚀
