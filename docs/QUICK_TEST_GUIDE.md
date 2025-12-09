# Quick Test Guide for Phase 3

## 🚀 TL;DR - Quick Start

You already have preprocessed data, so you can start testing immediately!

### Option 1: Full Training (Recommended)
```powershell
# Run the full training pipeline (takes 15-45 min on CPU, 3-10 min on GPU)
.\scripts\run_transformer_local.ps1

# After training, run all tests
.\scripts\test_phase3.ps1
```

### Option 2: Quick Test (1 Epoch)
```powershell
# 1. Edit config for quick test
# Open config/config_transformer.yaml and change:
#   num_train_epochs: 1  (instead of 3)

# 2. Run training
.\scripts\run_transformer_local.ps1

# 3. Run tests
.\scripts\test_phase3.ps1
```

---

## 📋 Step-by-Step Testing

### Step 1: Verify Prerequisites ✅

You already have:
- ✅ Preprocessed data in `data/processed/`
- ✅ Configuration file `config/config_transformer.yaml`
- ✅ Training script `src/models/transformer_training.py`

Just need to check dependencies:
```powershell
python -c "import torch, transformers, datasets; print('✅ All dependencies installed')"
```

If this fails, install dependencies:
```powershell
pip install torch transformers datasets
```

### Step 2: Run Training

**For Quick Test (1 epoch, ~10-20 minutes):**
1. Open `config/config_transformer.yaml`
2. Change line 14: `num_train_epochs: 1`
3. Run: `.\scripts\run_transformer_local.ps1`

**For Full Training (3 epochs, ~30-60 minutes):**
```powershell
.\scripts\run_transformer_local.ps1
```

### Step 3: Verify Training Completed

Check that these files exist:
```powershell
Get-ChildItem models\transformer\distilbert
```

Should see:
- ✅ `config.json`
- ✅ `pytorch_model.bin`
- ✅ `tokenizer_config.json`
- ✅ `vocab.txt`
- ✅ `labels.json`
- ✅ `training_info.json`

### Step 4: Run Tests

**Run all tests:**
```powershell
.\scripts\test_phase3.ps1
```

**Or run individual tests:**
```powershell
# Test 1: Model loading
python tests\test_model_loading.py

# Test 2: Inference
python tests\test_inference.py

# Test 3: Metrics validation
python tests\test_metrics.py
```

---

## 🎯 What Each Test Does

### Test 1: Model Loading (`test_model_loading.py`)
- ✅ Loads tokenizer from saved model
- ✅ Loads model from saved weights
- ✅ Loads label mappings
- ✅ Runs a simple inference test
- ✅ Verifies training info exists

### Test 2: Inference (`test_inference.py`)
- ✅ Tests inference on multiple sample texts
- ✅ Shows predicted labels and confidence scores
- ✅ Displays probability distributions
- ✅ Measures inference speed

### Test 3: Metrics Validation (`test_metrics.py`)
- ✅ Validates all metrics are in valid ranges
- ✅ Checks training and inference times
- ✅ Verifies class information
- ✅ Provides performance assessment

---

## 📊 Expected Output

### During Training:
```
==========================================
Starting Transformer Training Pipeline
==========================================
Configuration loaded from: config/config_transformer.yaml
Random seed set to: 42
Using device: cuda (or cpu)
Loading training data...
Train samples: XXXX
Validation samples: XXXX
Test samples: XXXX
Encoding labels...
Number of classes: X
Tokenizing data...
Training started...
[Progress bars showing epochs and steps]
Training completed in XX.XX seconds
Evaluating model on test set...
Test Accuracy: 0.XXXX
Test F1 (Macro): 0.XXXX
Model saved to: models/transformer/distilbert
==========================================
Training pipeline completed successfully!
==========================================
```

### After Tests:
```
==========================================
Phase 3 Testing Suite
==========================================

Running Test 1: Model Loading...
✅ ALL TESTS PASSED!

Running Test 2: Inference...
✅ Inference test completed successfully!

Running Test 3: Metrics Validation...
✅ ALL VALIDATION CHECKS PASSED!

==========================================
✅ ALL TESTS PASSED!
Phase 3 is working correctly!
==========================================
```

---

## 🐛 Common Issues & Solutions

### Issue: "CUDA out of memory"
**Solution:** Reduce batch size in config:
```yaml
training:
  train_batch_size: 8  # or even 4
  eval_batch_size: 16
```

### Issue: "Training is too slow"
**Solutions:**
1. Use 1 epoch for testing: `num_train_epochs: 1`
2. Reduce sequence length: `max_seq_length: 64`
3. Use CPU if GPU is causing issues: `device: "cpu"`

### Issue: "Module not found"
**Solution:**
```powershell
pip install torch transformers datasets scikit-learn pandas numpy pyyaml
```

### Issue: "Data files not found"
**Solution:** Run preprocessing first:
```powershell
.\scripts\run_preprocess_local.ps1
```

---

## ✅ Success Criteria

Phase 3 is successful if:

1. ✅ Training completes without errors
2. ✅ Model files are saved in `models/transformer/distilbert/`
3. ✅ All three test scripts pass
4. ✅ Metrics are reasonable:
   - Accuracy > 0.75
   - F1 Macro > 0.65
   - Training time is logged
   - Inference time < 100ms per sample

---

## 📈 Performance Benchmarks

### Expected Results (Toxic Comment Dataset):

**Quick Test (1 epoch):**
- ⏱️ Time: 10-20 min (CPU), 2-5 min (GPU)
- 📊 Accuracy: ~80-85%
- 📊 F1 Macro: ~65-75%

**Full Training (3 epochs):**
- ⏱️ Time: 30-60 min (CPU), 5-15 min (GPU)
- 📊 Accuracy: ~85-92%
- 📊 F1 Macro: ~75-85%
- 📊 F1 Weighted: ~85-92%

---

## 🎉 After Successful Testing

Once all tests pass:

1. ✅ Document your results
2. ✅ Compare with baseline models (Phase 2)
3. ✅ Ready to move to Phase 4 (FastAPI server)
4. ✅ Optional: Experiment with hyperparameters

---

## 💡 Pro Tips

1. **Start with 1 epoch** to verify everything works
2. **Save training logs**: `.\scripts\run_transformer_local.ps1 > training_log.txt 2>&1`
3. **Monitor resource usage** during training
4. **Compare with baselines** to ensure improvement
5. **Keep the best model** for deployment

---

## 📞 Need Help?

If tests fail:
1. Check the error messages in the output
2. Review `TESTING_PHASE3.md` for detailed troubleshooting
3. Verify all prerequisites are met
4. Check that data preprocessing completed successfully

Good luck! 🚀
