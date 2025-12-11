# Bug Fix: Probability Chart Showing Generic Class Labels

**Date:** 2025-12-10  
**Status:** ✅ FIXED (2 parts)  
**Severity:** Medium (UI Display Issue)

## Problem

The probability chart in the Streamlit UI was displaying generic labels instead of meaningful class names:
1. **First issue:** Chart showed "Class 0", "Class 1", etc. instead of actual labels
2. **Second issue:** Chart showed numeric IDs "0", "1" instead of "Regular Speech", "Hate Speech"

### Screenshot of Issue
- Chart showed: "Class 0", "Class 1", "Class 2", etc.
- Expected: Actual label names from the model

## Root Causes

### Issue 1: UI Not Parsing API Response Correctly

**Location:** `src/ui/components/results_display.py` (lines 198-200)

The API returns probabilities in this format:
```python
{
  "scores": [
    {"label": "toxic", "score": 0.198},
    {"label": "severe_toxic", "score": 0.015},
    ...
  ]
}
```

However, the UI code was checking if `probabilities` was a list and then treating it as a simple list of numbers:

```python
if isinstance(probabilities, list):
    # OLD CODE - assumed list of numbers
    prob_dict = {f"Class {i}": score for i, score in enumerate(probabilities)}
```

This created generic labels "Class 0", "Class 1", etc., overwriting the actual labels from the API.

### Issue 2: API Returning Numeric Labels for Baseline Models

**Location:** `src/api/server.py` (lines 251-283, 402-443)

The baseline sklearn models were trained with numeric labels (0, 1) from the dataset. The API was returning these numeric labels directly instead of mapping them to meaningful names like "Regular Speech" and "Hate Speech".

```python
# OLD CODE - returned numeric labels
self.classes = [str(label) for label in classifier.classes_.tolist()]  # ["0", "1"]
```

## Solutions

### Fix 1: Update UI to Parse List of Dictionaries

**File:** `src/ui/components/results_display.py` (lines 198-207)

```python
if isinstance(probabilities, list):
    # Check if it's a list of dicts (API format)
    if probabilities and isinstance(probabilities[0], dict):
        # Extract label-score pairs from list of dicts
        for item in probabilities:
            if 'label' in item and 'score' in item:
                prob_dict[item['label']] = item['score']
    else:
        # Fallback: List of numbers
        prob_dict = {f"Class {i}": score for i, score in enumerate(probabilities)}
```

### Fix 2: Map Numeric Labels to Meaningful Names in API

**File:** `src/api/server.py` (lines 251-283)

Added label name mapping for baseline models:

```python
# Map numeric labels to meaningful names
# Hate speech dataset: 0 = Regular, 1 = hate
label_name_mapping = {
    0: "Regular Speech",
    1: "Hate Speech"
}

# Convert to strings with meaningful names
self.classes = [label_name_mapping.get(int(label), str(label)) for label in raw_classes]

# Create label mappings (use meaningful names)
self.id2label = {i: label_name_mapping.get(int(raw_classes[i]), str(raw_classes[i])) 
                 for i in range(len(raw_classes))}
```

**File:** `src/api/server.py` (lines 402-443)

Updated prediction method to use meaningful labels:

```python
# Make prediction (returns numeric label like 0 or 1)
predicted_label_raw = self.pipeline.predict([text])[0]
predicted_idx = int(predicted_label_raw)

# Convert numeric prediction to meaningful label name
predicted_label = self.id2label[predicted_idx]
```

## Files Modified

1. **src/ui/components/results_display.py** (lines 198-207)
   - Added check for list of dictionaries format
   - Extracts actual labels from API response
   - Maintains backward compatibility with plain list format

2. **src/api/server.py** (lines 251-283)
   - Added label name mapping for baseline models
   - Maps 0 → "Regular Speech", 1 → "Hate Speech"
   - Updates id2label and label2id dictionaries

3. **src/api/server.py** (lines 402-443)
   - Updated _predict_baseline to convert numeric predictions to meaningful labels
   - Uses id2label mapping for label conversion

## Testing

After the fix, the probability chart should display:

**For Toxicity Model:**
- ✅ "toxic" instead of "Class 0"
- ✅ "severe_toxic" instead of "Class 1"
- ✅ "obscene" instead of "Class 2"
- ✅ "threat" instead of "Class 3"
- ✅ "insult" instead of "Class 4"
- ✅ "identity_hate" instead of "Class 5"

**For Baseline Models (Logistic Regression, Linear SVM):**
- ✅ "Regular Speech" instead of "0"
- ✅ "Hate Speech" instead of "1"

**For DistilBERT Model:**
- ✅ "Hate Speech" instead of "Class 0"
- ✅ "Regular Speech" instead of "Class 1"

## Deployment

To apply the fixes to the deployed application:

### Step 1: Redeploy API Backend (for Fix 2)

```powershell
# Rebuild and redeploy the API container with label mapping fix
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

This will:
1. Upload latest code to GCS
2. Pull code on VM
3. Rebuild API Docker image with label mapping
4. Restart API container

### Step 2: Redeploy UI Frontend (for Fix 1)

```powershell
# Rebuild and redeploy the UI container
.\scripts\gcp-deploy-ui.ps1
```

This will:
1. Pull latest code changes (including UI fix)
2. Rebuild the Streamlit Docker image
3. Restart the UI container
4. Verify the fix is working

**Note:** Both API and UI need to be redeployed for the complete fix to work.

## Verification

1. Open the UI: http://35.232.76.140:8501
2. Select any model (toxicity, distilbert, logistic_regression, linear_svm)
3. Enter text and analyze
4. Check the probability chart - should show actual label names
5. Try switching models - all should show proper labels

## Impact

- **User Experience:** ✅ Improved - users can now see meaningful label names
- **Functionality:** ✅ No change - predictions still work correctly
- **Performance:** ✅ No impact - same processing speed
- **Backward Compatibility:** ✅ Maintained - still handles plain list format

## Related

- API endpoint: `/predict` returns `scores` as list of dicts
- UI component: `results_display.py` renders probability charts
- Models affected: All models (toxicity, distilbert, baselines)
