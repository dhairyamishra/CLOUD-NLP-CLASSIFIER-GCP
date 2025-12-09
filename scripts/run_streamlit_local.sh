#!/usr/bin/env bash
# Bash script to run Streamlit UI locally (Linux/Mac)

set -e

echo "========================================"
echo "  Cloud NLP Classifier - Streamlit UI  "
echo "========================================"
echo ""

# Check if streamlit is installed
echo "Checking dependencies..."
if ! python -m streamlit --version &> /dev/null; then
    echo "✗ Streamlit is not installed!"
    echo ""
    echo "Installing Streamlit..."
    pip install streamlit>=1.28.0 plotly>=5.17.0
    echo "✓ Streamlit installed successfully"
else
    STREAMLIT_VERSION=$(python -m streamlit --version 2>&1)
    echo "✓ Streamlit is installed: $STREAMLIT_VERSION"
fi

echo ""

# Check if models exist
echo "Checking for trained models..."

MODELS_EXIST=false

if [ -f "models/baselines/logistic_regression_tfidf.joblib" ]; then
    echo "✓ Logistic Regression model found"
    MODELS_EXIST=true
fi

if [ -f "models/baselines/linear_svm_tfidf.joblib" ]; then
    echo "✓ Linear SVM model found"
    MODELS_EXIST=true
fi

if [ -f "models/transformer/distilbert/pytorch_model.bin" ]; then
    echo "✓ DistilBERT transformer model found"
    MODELS_EXIST=true
fi

if [ "$MODELS_EXIST" = false ]; then
    echo ""
    echo "⚠ WARNING: No trained models found!"
    echo "Please train models first:"
    echo "  python run_baselines.py"
    echo "  python run_transformer.py"
    echo ""
    echo "The UI will start but may not work without models."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 1
    fi
fi

echo ""
echo "========================================"
echo "Starting Streamlit UI..."
echo "========================================"
echo ""
echo "The UI will open in your browser at:"
echo "  http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run Streamlit
streamlit run src/ui/streamlit_app.py --server.port 8501
