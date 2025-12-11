# Testing Phase 10 Advanced Training Features

This guide will help you test the new advanced training features locally before deploying to the cloud.

---

## 🚀 Quick Start (5 minutes)

### Option 1: Interactive Quick Test (Recommended)

```bash
# Run the interactive test script
python quick_test_training.py
```

This will:
- Check if data is ready
- Let you choose test mode (quick/standard/FP16/custom)
- Run a minimal training session (1-2 epochs)
- Verify all Phase 10 features work correctly

### Option 2: Direct Command Line Test

```bash
# Simplest test - 1 epoch with small batch
python -m src.models.transformer_training --epochs 1 --batch-size 16
```

**Expected output:**
```
================================================================================
Starting Transformer Training Pipeline
================================================================================
Training mode: local
Configuration loaded from: config/config_transformer.yaml
...
Using learning rate scheduler: linear
FP16 mixed precision training enabled (or disabled if no GPU)
Early stopping enabled with patience: 3
...
Training completed successfully!
Model saved to: models/transformer/distilbert
```

---

## 📋 Prerequisites

Before testing, ensure you have:

1. **Data preprocessed**:
   ```bash
   # If not done yet
   python scripts/download_dataset.py
   python run_preprocess.py
   ```

2. **Dependencies installed**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Virtual environment activated** (recommended):
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

---

## 🧪 Test Scenarios

### Test 1: Basic CLI Interface ✅

**What it tests**: CLI argument parsing, basic training flow

```bash
python -m src.models.transformer_training \
  --epochs 1 \
  --batch-size 16
```

**Expected duration**: 5-10 minutes  
**Expected output**: Model saved to `models/transformer/distilbert/`

---

### Test 2: FP16 Mixed Precision ✅

**What it tests**: Mixed precision training, GPU detection

```bash
python -m src.models.transformer_training \
  --epochs 1 \
  --batch-size 16 \
  --fp16
```

**Expected behavior**:
- **With GPU**: "FP16 mixed precision training enabled"
- **Without GPU**: "FP16 requested but CUDA not available, disabling FP16"

**Expected duration**: 3-8 minutes (GPU) or 10-15 minutes (CPU)

---

### Test 3: Learning Rate Schedulers ✅

**What it tests**: Different LR scheduler types

#### Test 3a: Linear Scheduler (Default)
```bash
python -m src.models.transformer_training \
  --epochs 1 \
  --batch-size 16
```

#### Test 3b: Cosine Scheduler
```bash
# Edit config/config_transformer.yaml:
# lr_scheduler:
#   type: "cosine"

python -m src.models.transformer_training \
  --epochs 1 \
  --batch-size 16
```

#### Test 3c: Constant Scheduler
```bash
# Edit config/config_transformer.yaml:
# lr_scheduler:
#   type: "constant"

python -m src.models.transformer_training \
  --epochs 1 \
  --batch-size 16
```

**Expected output**: Check logs for "Using learning rate scheduler: [type]"

---

### Test 4: Early Stopping ✅

**What it tests**: Early stopping functionality

#### Test 4a: With Early Stopping (Default)
```bash
python -m src.models.transformer_training \
  --epochs 3 \
  --batch-size 16
```

**Expected**: May stop before 3 epochs if no improvement

#### Test 4b: Without Early Stopping
```bash
python -m src.models.transformer_training \
  --epochs 3 \
  --batch-size 16 \
  --no-early-stopping
```

**Expected**: Runs all 3 epochs regardless of performance

---

### Test 5: Cloud Configuration (Local Mode) ✅

**What it tests**: Cloud config file with local execution

```bash
python -m src.models.transformer_training \
  --config config/config_transformer_cloud.yaml \
  --mode local \
  --epochs 1 \
  --batch-size 16
```

**Expected**: Uses cloud settings (cosine scheduler, etc.) but runs locally

---

### Test 6: Custom Hyperparameters ✅

**What it tests**: CLI parameter overrides

```bash
python -m src.models.transformer_training \
  --epochs 2 \
  --batch-size 32 \
  --learning-rate 3e-5 \
  --output-dir models/transformer/custom_test \
  --seed 123
```

**Expected**: Uses custom parameters, saves to custom directory

---

### Test 7: Full Feature Test ✅

**What it tests**: All features combined

```bash
python -m src.models.transformer_training \
  --config config/config_transformer.yaml \
  --mode local \
  --epochs 2 \
  --batch-size 32 \
  --learning-rate 2e-5 \
  --fp16 \
  --output-dir models/transformer/full_test \
  --seed 42
```

**Expected duration**: 10-20 minutes  
**Expected**: All features working together

---

## 🔍 Verification Checklist

After running tests, verify:

### 1. Check Training Logs

```bash
# Look for these key messages in the output:
✓ "Training mode: local"
✓ "Using learning rate scheduler: [type]"
✓ "FP16 mixed precision training enabled" (if GPU)
✓ "Early stopping enabled with patience: X"
✓ "Training completed successfully!"
```

### 2. Check Model Files

```bash
# Verify model artifacts were created
ls -la models/transformer/distilbert/

# Should see:
✓ config.json
✓ pytorch_model.bin
✓ tokenizer_config.json
✓ vocab.txt
✓ labels.json
✓ training_info.json
```

### 3. Check Training Info

```bash
# View training results
cat models/transformer/distilbert/training_info.json

# Should contain:
✓ metrics (accuracy, f1_macro, etc.)
✓ training_time_seconds
✓ avg_inference_time_ms
✓ num_classes
```

### 4. Check Training Configuration

```bash
# Verify configuration was logged correctly
cat models/transformer/distilbert/logs/*/events.out.tfevents.*

# Or check console output for:
✓ "Training Configuration:"
✓ "  Epochs: X"
✓ "  Train Batch Size: X"
✓ "  Learning Rate: X"
✓ "  LR Scheduler: X"
```

---

## 🐛 Troubleshooting

### Issue: "Training data not found"

**Solution**:
```bash
# Download and preprocess data
python scripts/download_dataset.py
python run_preprocess.py

# Verify data exists
ls data/processed/
# Should see: train.csv, val.csv, test.csv
```

---

### Issue: "CUDA out of memory"

**Solution**:
```bash
# Reduce batch size
python -m src.models.transformer_training --batch-size 8

# Or use gradient accumulation (edit config):
# gradient_accumulation_steps: 2
```

---

### Issue: "FP16 not working"

**Solution**:
```bash
# Check GPU availability
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Check GPU capability (need >= 7.0 for Tensor Cores)
python -c "import torch; print(torch.cuda.get_device_capability())"

# If no GPU, FP16 will auto-disable (this is normal)
```

---

### Issue: "Module not found"

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify transformers version
pip show transformers
# Should be >= 4.30.0
```

---

### Issue: Training is very slow

**Solution**:
```bash
# Use smaller batch size for testing
python -m src.models.transformer_training --batch-size 8 --epochs 1

# Or reduce sequence length (edit config):
# max_seq_length: 64

# Or use fewer training samples (edit config):
# Add data sampling logic if needed
```

---

## 📊 Expected Performance

### Local CPU (Intel i7)
- **1 epoch**: 20-30 minutes
- **Batch size**: 8-16
- **FP16**: Not applicable

### Local GPU (RTX 3060)
- **1 epoch**: 5-10 minutes
- **Batch size**: 32-64
- **FP16**: 2x speedup

### Local GPU (RTX 4090)
- **1 epoch**: 2-5 minutes
- **Batch size**: 64-128
- **FP16**: 2x speedup

---

## 🎯 Success Criteria

Your test is successful if:

1. ✅ Training completes without errors
2. ✅ Model files are created in output directory
3. ✅ `training_info.json` contains valid metrics
4. ✅ Console shows correct configuration (scheduler, FP16, etc.)
5. ✅ Test accuracy is > 70% (even with 1 epoch)

---

## 📝 Example Test Session

Here's what a successful test looks like:

```bash
$ python quick_test_training.py

================================================================================
QUICK TEST: Phase 10 Advanced Training
================================================================================

This will run a quick 1-epoch training to test the new features.
Expected duration: 5-10 minutes (depending on CPU/GPU)

Features being tested:
  ✓ CLI argument parsing
  ✓ Early stopping
  ✓ Learning rate scheduler (linear)
  ✓ FP16 mixed precision (if GPU available)
  ✓ Configuration system
================================================================================

✅ Training data found!

Choose test mode:
  1. Quick test (1 epoch, small batch) - ~5 minutes
  2. Standard test (2 epochs, normal batch) - ~10-15 minutes
  3. FP16 test (1 epoch with mixed precision) - ~5 minutes
  4. Custom (enter your own parameters)

Enter choice (1-4) [default: 1]: 1

================================================================================
Running: Quick Test (1 epoch, batch=16)
================================================================================
Command: python -m src.models.transformer_training --epochs 1 --batch-size 16

Starting training...

================================================================================
Starting Transformer Training Pipeline
================================================================================
Training mode: local
Configuration loaded from: config/config_transformer.yaml
Random seed set to: 42
Using device: cuda
Loading training data from: data/processed/train.csv
Train samples: 24783
Validation samples: 3000
Test samples: 3000
Encoding labels...
Number of classes: 3
Classes: ['hate_speech', 'offensive_language', 'neither']
Loading tokenizer: distilbert-base-uncased
Tokenizing data...
Tokenization complete!
Loading model: distilbert-base-uncased
Setting up training...
Using learning rate scheduler: linear
FP16 mixed precision training enabled
Early stopping enabled with patience: 3
Monitoring metric: eval_f1_macro (max)
============================================================
Training Configuration:
  Epochs: 1
  Train Batch Size: 16
  Eval Batch Size: 32
  Learning Rate: 2.0e-5
  Weight Decay: 0.01
  Warmup Ratio: 0.1
  LR Scheduler: linear
  Gradient Accumulation Steps: 1
  Max Grad Norm: 1.0
  FP16: True
============================================================
Starting training...
Training started...
[1549/1549 05:23, Epoch 1/1]
Step    Training Loss    Validation Loss    Accuracy    F1 Macro
500     0.5234          0.4123            0.8234      0.7891
1000    0.3456          0.3567            0.8567      0.8234
1549    0.2789          0.3234            0.8789      0.8456

Training completed in 323.45 seconds (5.39 minutes)
Evaluating model on test set...
Measuring inference time...
Average inference time: 45.23 ms per sample

================================================================================
Training Summary
================================================================================
Model: distilbert-base-uncased
Number of classes: 3
Training time: 323.45s (5.39 min)
Average inference time: 45.23 ms/sample
Test Accuracy: 0.8789
Test F1 (Macro): 0.8456
Test F1 (Weighted): 0.8678
Model saved to: models/transformer/distilbert
================================================================================
Training pipeline completed successfully!
================================================================================

================================================================================
✅ TEST PASSED - Training completed successfully!
================================================================================

📊 Check the results:
  - Model: models/transformer/distilbert/
  - Training info: models/transformer/distilbert/training_info.json
  - Logs: models/transformer/distilbert/logs/

🎉 Phase 10 features are working correctly!

================================================================================
```

---

## 🚀 Next Steps After Testing

Once local testing is successful:

1. **Train a better model locally**:
   ```bash
   python -m src.models.transformer_training --epochs 3 --batch-size 32 --fp16
   ```

2. **Try cloud configuration locally**:
   ```bash
   python -m src.models.transformer_training \
     --config config/config_transformer_cloud.yaml \
     --mode local \
     --epochs 2
   ```

3. **Deploy to GCP for production training**:
   - Follow the GCP training guide in README.md
   - Use `scripts/setup_gcp_training.sh`
   - Train with `scripts/run_gcp_training.sh`

4. **Experiment with hyperparameters**:
   - Try different learning rates (1e-5, 2e-5, 3e-5, 5e-5)
   - Test different schedulers (linear, cosine, polynomial)
   - Adjust batch sizes based on your hardware

---

## 📞 Need Help?

If you encounter issues:

1. Check the troubleshooting section above
2. Review the error messages carefully
3. Verify all prerequisites are met
4. Check `docs/PHASE10_ADVANCED_TRAINING_SUMMARY.md` for detailed documentation
5. Review the main `README.md` for setup instructions

---

**Happy Testing! 🎉**
