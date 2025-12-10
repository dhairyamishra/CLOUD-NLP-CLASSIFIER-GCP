# Full-Scale Training Quick Start Guide

## 🎯 What Was Fixed

**Problem:** Baseline models trained in seconds (too fast!)  
**Cause:** Code wasn't using the comprehensive configuration parameters  
**Solution:** Enhanced `BaselineTextClassifier` to use all config settings  

**Now training will take 5-15 minutes for baselines (expected for 10k features + trigrams)**

---

## 🚀 Run Training Now

### Option 1: Train All Models (Recommended)

```bash
python train_all_models.py
```

This will train **3 models sequentially:**
1. ✅ Baseline Models (Logistic Regression + Linear SVM) - 5-15 min
2. ✅ DistilBERT Standard (256 seq, 15 epochs) - 30-60 min (GPU) / 4-8 hrs (CPU)
3. ✅ DistilBERT Intensive (512 seq, 25 epochs) - 2-4 hrs (GPU) / 10-20 hrs (CPU)

**Total Time:** 2-6 hours (GPU) or 12-24 hours (CPU)

### Option 2: Train Individual Models

#### Baseline Models Only:
```bash
python run_baselines.py
```

#### Transformer Standard Only:
```bash
python run_transformer.py
```

#### Transformer Intensive Only:
```bash
python -m src.models.transformer_training --config config/config_transformer_fullscale.yaml
```

### Option 3: PowerShell (Windows)

```powershell
# All models
.\scripts\train_all_models.ps1

# Skip confirmation prompt
.\scripts\train_all_models.ps1 -SkipConfirmation

# Continue even if one model fails
.\scripts\train_all_models.ps1 -ContinueOnFailure
```

---

## 📊 What to Expect

### Baseline Models (FIXED - Now Proper Training)

**Before Fix:**
- ⚠️ Training: 2-5 seconds (too fast!)
- ⚠️ Features: ~2000 (default)
- ⚠️ Solver: lbfgs (hardcoded)
- ⚠️ No parallelization

**After Fix:**
- ✅ Training: 5-15 minutes (proper full-scale)
- ✅ Features: 10,000 (from config)
- ✅ N-grams: 1-3 (unigrams, bigrams, trigrams)
- ✅ Solver: saga (from config)
- ✅ Parallel: All CPU cores (`n_jobs=-1`)
- ✅ Verbose: Shows progress

**Console Output You'll See:**
```
Training logistic with tfidf vectorizer...
Training samples: 21124
[Parallel(n_jobs=-1)]: Using backend LokyBackend with 8 concurrent workers.
[Parallel(n_jobs=-1)]: Done   1 out of   1 | elapsed:    8.3s finished
Training complete!
```

### Transformer Models

**Standard Configuration:**
- Sequence length: 256 tokens
- Epochs: 15 (with early stopping, patience=5)
- Expected: 30-60 min (GPU), 4-8 hrs (CPU)
- Target accuracy: 90-93%

**Intensive Configuration:**
- Sequence length: 512 tokens (full context)
- Epochs: 25 (with early stopping, patience=8)
- Expected: 2-4 hrs (GPU), 10-20 hrs (CPU)
- Target accuracy: 92-95%

---

## 📁 Output Files

After training completes:

```
models/
├── baselines/
│   ├── logistic_regression_tfidf.joblib    (NEW - larger size ~50-100 MB)
│   ├── linear_svm_tfidf.joblib             (NEW - larger size ~50-100 MB)
│   └── tfidf_vectorizer.pkl
├── transformer/
│   ├── distilbert/                          (Standard config)
│   │   ├── pytorch_model.bin
│   │   ├── config.json
│   │   └── training_info.json
│   └── distilbert_fullscale/                (Intensive config)
│       ├── pytorch_model.bin
│       ├── config.json
│       └── training_info.json

training_report.json                          (Summary of all training)
```

---

## ✅ Verification Checklist

After baseline training, verify the fix worked:

- [ ] Training took 5-15 minutes (not seconds)
- [ ] Console shows parallel processing: `[Parallel(n_jobs=-1)]`
- [ ] Model files are 50-100 MB (not 5-10 MB)
- [ ] Logs show "10000 features"
- [ ] Verbose output shows iteration progress

---

## 🔧 Configuration Summary

### Baseline Models (`config/config_baselines.yaml`)

```yaml
vectorizer:
  max_features: 10000      # Rich vocabulary
  ngram_range: [1, 3]      # Unigrams + bigrams + trigrams
  sublinear_tf: true       # TF scaling
  use_idf: true            # IDF weighting
  smooth_idf: true         # Smooth IDF
  norm: "l2"               # L2 normalization

logistic_regression:
  C: 1.0
  max_iter: 1000           # Full convergence
  solver: "saga"           # Supports L1/L2
  penalty: "l2"
  n_jobs: -1               # All CPU cores
  verbose: 1               # Show progress

linear_svm:
  C: 1.0
  max_iter: 2000           # Full convergence
  loss: "squared_hinge"
  penalty: "l2"
  verbose: 1               # Show progress
```

### Transformer Standard (`config/config_transformer.yaml`)

```yaml
model:
  max_seq_length: 256
  dropout: 0.1

training:
  num_train_epochs: 15
  train_batch_size: 32
  learning_rate: 3.0e-5
  gradient_accumulation_steps: 2
  
  early_stopping:
    enabled: true
    patience: 5
    metric: "eval_f1_macro"
  
  lr_scheduler:
    type: "cosine_with_restarts"
    num_cycles: 3
```

### Transformer Intensive (`config/config_transformer_fullscale.yaml`)

```yaml
model:
  max_seq_length: 512      # Maximum context
  dropout: 0.15

training:
  num_train_epochs: 25
  train_batch_size: 16
  learning_rate: 2.0e-5
  gradient_accumulation_steps: 4
  fp16: true               # Mixed precision
  
  early_stopping:
    enabled: true
    patience: 8            # Very patient
    metric: "eval_f1_macro"
  
  lr_scheduler:
    type: "cosine_with_restarts"
    num_cycles: 5
  
  label_smoothing_factor: 0.1
```

---

## 📈 Expected Performance

| Model | Accuracy | F1 Score | Training Time | Inference |
|-------|----------|----------|---------------|-----------|
| Logistic Regression | 85-88% | 0.83-0.86 | 5-10 min | 0.5-1 ms |
| Linear SVM | 85-88% | 0.83-0.86 | 5-10 min | 0.5-1 ms |
| DistilBERT Standard | 90-93% | 0.88-0.91 | 30-60 min (GPU) | 5-10 ms |
| DistilBERT Intensive | 92-95% | 0.90-0.93 | 2-4 hrs (GPU) | 8-15 ms |

---

## 🎯 Next Steps After Training

1. **Check Training Report:**
   ```bash
   cat training_report.json
   ```

2. **Test Models:**
   ```bash
   python scripts/client_example.py
   ```

3. **Run Evaluation:**
   ```bash
   python run_tests.py
   ```

4. **Build Docker Image:**
   ```bash
   docker build -t cloud-nlp-classifier .
   ```

5. **Deploy:**
   - See `docs/DOCKER_GUIDE.md`
   - See `docs/MULTI_MODEL_DOCKER_GUIDE.md`

---

## 📚 Documentation

- **Full Training Guide:** `docs/FULL_SCALE_TRAINING_GUIDE.md`
- **Fix Details:** `docs/TRAINING_FIX_SUMMARY.md`
- **Docker Guide:** `docs/DOCKER_GUIDE.md`
- **Multi-Model Guide:** `docs/MULTI_MODEL_DOCKER_GUIDE.md`

---

## 🆘 Troubleshooting

### Training Still Too Fast?
- Check console output for parallel processing messages
- Verify config file is being loaded correctly
- Check model file sizes after training

### Out of Memory?
- Reduce batch size in config
- Reduce max_seq_length for transformers
- Enable fp16 for GPU training

### Training Too Slow?
- Enable fp16 for GPU
- Increase batch size if memory allows
- Reduce num_train_epochs

---

**Ready to train? Run:** `python train_all_models.py`

**Questions?** Check `docs/FULL_SCALE_TRAINING_GUIDE.md` for detailed information.
