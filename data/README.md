# Data Directory

This directory contains the datasets used for training and evaluation.

## Directory Structure

```
data/
├── raw/              # Original, unprocessed datasets
│   └── dataset.csv   # Raw hate speech dataset
├── processed/        # Preprocessed and split datasets
│   ├── train.csv     # Training set (80% of data)
│   ├── val.csv       # Validation set (10% of data)
│   └── test.csv      # Test set (10% of data)
└── README.md         # This file
```

## Dataset Schema

### Raw Dataset (`raw/dataset.csv`)

The raw dataset should contain at least the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `text` | string | The text content to classify |
| `label` | int/string | The class label (0=non-hate, 1=hate or similar) |

**Example:**
```csv
text,label
"This is a normal comment",0
"This contains hate speech",1
```

### Processed Datasets (`processed/*.csv`)

After preprocessing, the datasets maintain the same schema but with:
- Cleaned text (lowercase, URLs removed, etc.)
- No missing values
- Consistent label encoding
- Stratified splits maintaining class distribution

## Dataset Information

### Hate Speech Dataset

**Source:** [Will be specified after download]

**Description:** 
- Binary or multi-class classification of hate speech
- Text from social media or online comments
- Labeled for hate speech detection

**Statistics:**
- Total samples: [To be filled]
- Number of classes: [To be filled]
- Class distribution: [To be filled]
- Average text length: [To be filled]

**Preprocessing Steps:**
1. Text cleaning (lowercase, remove URLs, mentions, etc.)
2. Remove empty or invalid samples
3. Stratified train/val/test split (80/10/10)

## Usage

### Download Dataset

Run the download script to fetch the hate speech dataset:

```bash
python scripts/download_dataset.py
```

### Preprocess Dataset

After downloading, preprocess the data:

```bash
python -m src.data.preprocess
```

Or use the shell script:

```bash
bash scripts/run_preprocess_local.sh
```

## Notes

- Large CSV files are gitignored to avoid repository bloat
- Always keep a backup of the raw dataset
- Document any manual data cleaning steps
- Update this README with actual dataset statistics after download
