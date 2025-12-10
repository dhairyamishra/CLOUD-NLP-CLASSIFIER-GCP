# Testing Phase 3: Transformer Model Training

## ✅ Prerequisites Check

Before testing Phase 3, verify you have:

1. **Preprocessed Data** ✅ (You have this!)
   - `data/processed/train.csv`
   - `data/processed/val.csv`
   - `data/processed/test.csv`

2. **Dependencies Installed**
   ```powershell
   pip install torch transformers datasets scikit-learn pandas numpy pyyaml
   ```

3. **Configuration File**
   - `config/config_transformer.yaml` ✅ (Already exists)

---

## 🧪 Testing Options

### Option 1: Quick Test with Reduced Settings (Recommended First)

For a quick test to verify everything works, temporarily modify the config:

1. **Create a test config** (optional):
   ```powershell
   Copy-Item config\config_transformer.yaml config\config_transformer_test.yaml
   ```

2. **Edit test settings** in `config/config_transformer_test.yaml`:
   ```yaml
   training:
     num_train_epochs: 1  # Reduce from 3 to 1
     train_batch_size: 8  # Reduce if memory issues
     eval_batch_size: 16
   ```

3. **Modify the script temporarily** to use test config (or just reduce epochs in main config)

### Option 2: Full Training Run

Run the complete training pipeline with default settings.

---

## 🚀 Step-by-Step Testing

### Step 1: Verify Environment

```powershell
# Check Python version (should be 3.8+)
python --version

# Check if PyTorch is installed
python -c "import torch; print(f'PyTorch: {torch.__version__}')"

# Check if transformers is installed
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"

# Check CUDA availability (optional, for GPU)
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Step 2: Quick Import Test

Create a simple test to verify imports work:

```powershell
python -c "from src.models.transformer_training import main; print('✅ Import successful!')"
```

### Step 3: Run Training (Quick Test - 1 Epoch)

**Option A: Modify config temporarily**

Edit `config/config_transformer.yaml` and change:
```yaml
training:
  num_train_epochs: 1  # Change from 3 to 1 for quick test
```

Then run:
```powershell
.\scripts\run_transformer_local.ps1
```

**Option B: Test with smaller dataset (create a test script)**

I can create a test script that uses only a subset of data for quick validation.

### Step 4: Monitor Training

Watch for these key outputs:

```
==========================================
Starting Transformer Training Pipeline
==========================================
Configuration loaded from: config/config_transformer.yaml
Random seed set to: 42
Using device: cuda (or cpu)
Loading training data from: data/processed/train.csv
Train samples: XXXX
Validation samples: XXXX
Test samples: XXXX
Encoding labels...
Number of classes: X
Classes: ['class1', 'class2', ...]
Tokenizing data...
Loading model: distilbert-base-uncased
Training started...
[Progress bars and training logs]
Training completed in XX.XX seconds
Evaluating model on test set...
Model and tokenizer saved!
```

### Step 5: Verify Outputs

After training completes, check that these files were created:

```powershell
# Check if model directory exists
Test-Path models\transformer\distilbert

# List all saved files
Get-ChildItem models\transformer\distilbert -Recurse
```

Expected files:
- ✅ `config.json` - Model configuration
- ✅ `pytorch_model.bin` - Trained weights
- ✅ `tokenizer_config.json` - Tokenizer config
- ✅ `vocab.txt` - Vocabulary
- ✅ `labels.json` - Label mappings
- ✅ `training_info.json` - Metrics and timing
- ✅ `checkpoint-*/` - Training checkpoints

### Step 6: Inspect Results

```powershell
# View training info
Get-Content models\transformer\distilbert\training_info.json | ConvertFrom-Json | ConvertTo-Json -Depth 10

# View label mappings
Get-Content models\transformer\distilbert\labels.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

## 🔍 Validation Tests

### Test 1: Check Model Loading

Create a test script to verify the model can be loaded:

```python
# test_model_loading.py
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import json

model_path = "models/transformer/distilbert"

# Load tokenizer
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
print("✅ Tokenizer loaded successfully")

# Load model
model = DistilBertForSequenceClassification.from_pretrained(model_path)
print("✅ Model loaded successfully")

# Load labels
with open(f"{model_path}/labels.json", 'r') as f:
    labels = json.load(f)
print(f"✅ Labels loaded: {labels['classes']}")

# Test inference
text = "This is a test sentence"
inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
outputs = model(**inputs)
print(f"✅ Inference successful! Output shape: {outputs.logits.shape}")
```

Run it:
```powershell
python test_model_loading.py
```

### Test 2: Quick Inference Test

```python
# test_inference.py
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import json
import numpy as np

model_path = "models/transformer/distilbert"

# Load model and tokenizer
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
model = DistilBertForSequenceClassification.from_pretrained(model_path)
model.eval()

# Load labels
with open(f"{model_path}/labels.json", 'r') as f:
    label_info = json.load(f)
id2label = {int(k): v for k, v in label_info['id2label'].items()}

# Test samples
test_texts = [
    "I love this product, it's amazing!",
    "This is terrible, worst experience ever.",
    "It's okay, nothing special."
]

print("\n" + "="*60)
print("Testing Inference")
print("="*60)

for text in test_texts:
    # Tokenize
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    
    # Predict
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)
        pred_class = torch.argmax(probs, dim=1).item()
        confidence = probs[0][pred_class].item()
    
    print(f"\nText: {text}")
    print(f"Predicted: {id2label[pred_class]} (confidence: {confidence:.4f})")
    print(f"All probabilities: {probs.numpy()}")

print("\n" + "="*60)
print("✅ Inference test completed successfully!")
print("="*60)
```

Run it:
```powershell
python test_inference.py
```

### Test 3: Verify Metrics

Check that the saved metrics make sense:

```python
# test_metrics.py
import json

with open("models/transformer/distilbert/training_info.json", 'r') as f:
    info = json.load(f)

print("\n" + "="*60)
print("Training Metrics Summary")
print("="*60)

metrics = info['metrics']
print(f"\n📊 Performance Metrics:")
print(f"  Accuracy:        {metrics['accuracy']:.4f}")
print(f"  F1 Macro:        {metrics['f1_macro']:.4f}")
print(f"  F1 Weighted:     {metrics['f1_weighted']:.4f}")
print(f"  Precision Macro: {metrics['precision_macro']:.4f}")
print(f"  Recall Macro:    {metrics['recall_macro']:.4f}")

if 'roc_auc' in metrics:
    print(f"  ROC-AUC:         {metrics['roc_auc']:.4f}")
elif 'roc_auc_ovr' in metrics:
    print(f"  ROC-AUC (OvR):   {metrics['roc_auc_ovr']:.4f}")

print(f"\n⏱️  Timing:")
print(f"  Training time:   {info['training_time_minutes']:.2f} minutes")
print(f"  Inference time:  {info['avg_inference_time_ms']:.2f} ms/sample")

print(f"\n🎯 Model Info:")
print(f"  Number of classes: {info['num_classes']}")
print(f"  Classes: {info['classes']}")

print("\n" + "="*60)

# Sanity checks
assert 0 <= metrics['accuracy'] <= 1, "❌ Accuracy out of range"
assert 0 <= metrics['f1_macro'] <= 1, "❌ F1 macro out of range"
assert info['training_time_seconds'] > 0, "❌ Invalid training time"
assert info['avg_inference_time_ms'] > 0, "❌ Invalid inference time"

print("✅ All metrics are valid!")
print("="*60)
```

Run it:
```powershell
python test_metrics.py
```

---

## 🐛 Troubleshooting

### Issue 1: Out of Memory Error

**Symptoms:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**
1. Reduce batch size in config:
   ```yaml
   training:
     train_batch_size: 4  # Reduce from 16
     eval_batch_size: 8   # Reduce from 32
   ```

2. Reduce sequence length:
   ```yaml
   model:
     max_seq_length: 64  # Reduce from 128
   ```

3. Use CPU instead:
   ```yaml
   device: "cpu"
   ```

### Issue 2: Training Too Slow

**If on CPU:**
- Expected: 30-60 minutes for full training
- Quick test: Use 1 epoch (~10-20 minutes)

**Solutions:**
1. Reduce epochs for testing:
   ```yaml
   training:
     num_train_epochs: 1
   ```

2. Use a subset of data (create a test script)

3. Consider using Google Colab with free GPU

### Issue 3: Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'transformers'
```

**Solution:**
```powershell
pip install torch transformers datasets
```

### Issue 4: Data Not Found

**Symptoms:**
```
FileNotFoundError: data/processed/train.csv not found
```

**Solution:**
Run preprocessing first:
```powershell
.\scripts\run_preprocess_local.ps1
```

---

## 📊 Expected Results

### For Toxic Comment Classification Dataset:

**Quick Test (1 epoch):**
- Training time: 5-15 minutes (CPU), 1-3 minutes (GPU)
- Accuracy: ~80-85%
- F1 Macro: ~65-75%

**Full Training (3 epochs):**
- Training time: 15-45 minutes (CPU), 3-10 minutes (GPU)
- Accuracy: ~85-92%
- F1 Macro: ~75-85%
- F1 Weighted: ~85-92%

---

## ✅ Success Checklist

After testing, verify:

- [ ] Training completes without errors
- [ ] Model files are saved in `models/transformer/distilbert/`
- [ ] `labels.json` contains correct label mappings
- [ ] `training_info.json` shows reasonable metrics
- [ ] Model can be loaded successfully
- [ ] Inference works on test samples
- [ ] Metrics are in valid ranges (0-1)
- [ ] Training time is logged
- [ ] Inference time is measured

---

## 🚀 Quick Start Command

For a complete test run:

```powershell
# 1. Quick test (1 epoch) - modify config first
# Edit config/config_transformer.yaml: num_train_epochs: 1

# 2. Run training
.\scripts\run_transformer_local.ps1

# 3. Verify outputs
Get-ChildItem models\transformer\distilbert

# 4. Check metrics
Get-Content models\transformer\distilbert\training_info.json | ConvertFrom-Json
```

---

## 📝 Next Steps After Testing

Once Phase 3 testing is successful:

1. ✅ Compare results with baseline models (Phase 2)
2. ✅ Document performance metrics
3. ✅ Move to Phase 4: FastAPI inference server
4. ✅ Experiment with hyperparameters if needed

---

## 💡 Pro Tips

1. **Start with 1 epoch** for quick validation
2. **Monitor GPU/CPU usage** during training
3. **Save logs** for debugging: `.\scripts\run_transformer_local.ps1 > training_log.txt 2>&1`
4. **Compare with baselines** to ensure transformer performs better
5. **Use tensorboard** (optional) for detailed training visualization

Good luck with testing! 🎉
