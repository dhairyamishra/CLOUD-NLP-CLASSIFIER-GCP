# Fast Testing Configuration

## 🚀 Optimizations Applied

The configurations have been optimized for **fast end-to-end testing**. This allows you to quickly validate the entire pipeline works before running full training.

---

## ⚡ Transformer Config Changes

**File:** `config/config_transformer.yaml`

| Parameter | Original | Optimized | Impact |
|-----------|----------|-----------|--------|
| `max_seq_length` | 128 | **64** | 2x faster tokenization & training |
| `train_batch_size` | 16 | **32** | 2x faster training |
| `eval_batch_size` | 32 | **64** | 2x faster evaluation |
| `num_train_epochs` | 3 | **1** | 3x faster (most important!) |
| `learning_rate` | 2e-5 | **3e-5** | Faster convergence |
| `warmup_ratio` | 0.1 | **0.05** | Less warmup time |
| `early_stopping` | enabled | **disabled** | No early stop overhead |
| `logging_steps` | 50 | **25** | More frequent updates |
| `eval_steps` | 100 | **200** | Less frequent eval |
| `save_steps` | 100 | **500** | Less frequent saves |
| `save_total_limit` | 3 | **1** | Only best checkpoint |

**Expected Training Time:**
- **CPU**: ~5-10 minutes (down from 30-60 min)
- **GPU**: ~1-3 minutes (down from 5-15 min)

**Expected Performance (1 epoch):**
- Accuracy: ~80-85%
- F1 Macro: ~65-75%

---

## ⚡ Baseline Config Changes

**File:** `config/config_baselines.yaml`

| Parameter | Original | Optimized | Impact |
|-----------|----------|-----------|--------|
| `max_features` | 10000 | **5000** | 2x faster vectorization |
| `ngram_range` | [1, 2] | **[1, 1]** | No bigrams = faster |
| `max_iter` (LR) | 1000 | **500** | 2x faster training |
| `max_iter` (SVM) | 1000 | **500** | 2x faster training |

**Expected Training Time:**
- **Both models**: ~1-2 minutes (down from 3-5 min)

**Expected Performance:**
- Accuracy: ~85-90%
- F1 Macro: ~70-80%

---

## 📊 Overall Pipeline Speed

### Before Optimization:
```
Preprocess:  ~2-3 min
Baselines:   ~3-5 min
Transformer: ~30-60 min (CPU) / ~5-15 min (GPU)
Tests:       ~1-2 min
─────────────────────────
Total:       ~36-70 min (CPU) / ~11-25 min (GPU)
```

### After Optimization:
```
Preprocess:  ~2-3 min
Baselines:   ~1-2 min
Transformer: ~5-10 min (CPU) / ~1-3 min (GPU)
Tests:       ~1-2 min
─────────────────────────
Total:       ~9-17 min (CPU) / ~5-10 min (GPU)
```

**Speed Improvement: 3-4x faster!** 🚀

---

## 🎯 Quick Testing Workflow

Run the entire pipeline quickly:

```bash
# 1. Preprocess (if not done already)
python run_preprocess.py

# 2. Train baselines (~1-2 min)
python run_baselines.py

# 3. Train transformer (~5-10 min CPU, ~1-3 min GPU)
python run_transformer.py

# 4. Run tests (~1-2 min)
python run_tests.py
```

**Total time: ~9-17 minutes on CPU, ~5-10 minutes on GPU**

---

## 🔄 Reverting to Full Training

When you're ready for full training with better performance, edit the configs:

### Transformer (`config/config_transformer.yaml`):
```yaml
model:
  max_seq_length: 128  # Change from 64

training:
  train_batch_size: 16  # Change from 32
  eval_batch_size: 32   # Change from 64
  num_train_epochs: 3   # Change from 1
  learning_rate: 2.0e-5 # Change from 3e-5
  warmup_ratio: 0.1     # Change from 0.05
  
  early_stopping:
    enabled: true       # Change from false
  
  logging_steps: 50     # Change from 25
  eval_steps: 100       # Change from 200
  save_steps: 100       # Change from 500
  save_total_limit: 3   # Change from 1
```

### Baselines (`config/config_baselines.yaml`):
```yaml
vectorizer:
  max_features: 10000   # Change from 5000
  ngram_range: [1, 2]   # Change from [1, 1]

logistic_regression:
  max_iter: 1000        # Change from 500

linear_svm:
  max_iter: 1000        # Change from 500
```

---

## 📈 Performance Trade-offs

### Fast Testing Config (Current):
- ✅ **Very fast** - Complete pipeline in ~10-15 minutes
- ✅ **Good enough** - 80-85% accuracy
- ✅ **Quick validation** - Verify everything works
- ⚠️ **Lower performance** - Not production-ready

### Full Training Config:
- ⏱️ **Slower** - 30-60 minutes on CPU
- ✅ **Better performance** - 85-92% accuracy
- ✅ **Production-ready** - Suitable for deployment
- ✅ **More robust** - Better generalization

---

## 💡 Recommendations

1. **Use fast config for:**
   - Initial testing and validation
   - Debugging the pipeline
   - Quick iterations during development
   - CI/CD pipeline testing

2. **Use full config for:**
   - Final model training
   - Production deployment
   - Performance benchmarking
   - Research and experimentation

3. **Current status:**
   - ✅ Configs are set to **FAST mode**
   - Ready for quick end-to-end testing
   - Run `python run_transformer.py` now!

---

## 🎉 Ready to Test!

Your configs are now optimized for fast testing. Run:

```bash
python run_transformer.py
```

Expected time: **~5-10 minutes on CPU, ~1-3 minutes on GPU**

After training completes, run tests:

```bash
python run_tests.py
```

Good luck! 🚀
