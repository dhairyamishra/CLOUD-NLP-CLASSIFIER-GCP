# 🚀 Streamlit UI - Quick Reference Card

## 📋 Documents Created

1. **`STREAMLIT_UI_TASK_LIST.md`** - Comprehensive task breakdown (10 phases, 100+ tasks)
2. **`STREAMLIT_UI_OVERVIEW.md`** - Visual overview and architecture
3. **`STREAMLIT_UI_QUICK_REF.md`** - This quick reference (you are here)

---

## 🎯 What We're Building

**A minimal Streamlit web UI with:**
- 🎛️ **Sidebar**: Model selection (3 models: LogReg, SVM, DistilBERT)
- 💬 **Chat Interface**: Text input + conversation history
- 📊 **Results Display**: Sentiment analysis with confidence scores
- ⚡ **Real-time Inference**: < 2 seconds per prediction

---

## 📁 Files to Create

### Core Files (Required)
```
src/ui/
├── streamlit_app.py              # Main app (150-200 lines)
├── components/
│   ├── sidebar.py                # Model selection (80-100 lines)
│   ├── chat_interface.py         # Chat UI (100-120 lines)
│   └── results_display.py        # Results formatting (60-80 lines)
└── utils/
    ├── model_manager.py          # Model loading (120-150 lines)
    ├── inference_handler.py      # Predictions (100-120 lines)
    └── helpers.py                # Utilities (50-80 lines)

.streamlit/
└── config.toml                   # Theme config (20-30 lines)

scripts/
├── run_streamlit_local.sh        # Linux/Mac (10 lines)
├── run_streamlit_local.ps1       # Windows (10 lines)
└── run_streamlit.py              # Cross-platform (15 lines)
```

**Total Code**: ~900-1200 lines across 10 files

---

## ⚡ Quick Start (After Implementation)

### Install
```bash
pip install streamlit>=1.28.0
```

### Run
```bash
# Windows
.\scripts\run_streamlit_local.ps1

# Linux/Mac
bash scripts/run_streamlit_local.sh

# Direct
streamlit run src/ui/streamlit_app.py
```

### Access
```
http://localhost:8501
```

---

## 🏗️ Implementation Order

### Phase 1: Setup (30 min)
```bash
# 1. Update requirements.txt
echo "streamlit>=1.28.0" >> requirements.txt

# 2. Create directories
mkdir -p src/ui/components src/ui/utils .streamlit

# 3. Create __init__.py files
touch src/ui/__init__.py
touch src/ui/components/__init__.py
touch src/ui/utils/__init__.py
```

### Phase 2: Model Loading (1-2 hours)
- Create `model_manager.py` - Load all 3 models
- Create `inference_handler.py` - Handle predictions
- Implement caching with `@st.cache_resource`

### Phase 3: UI Components (2-3 hours)
- Create `sidebar.py` - Model selection dropdown
- Create `chat_interface.py` - Text input + history
- Create `results_display.py` - Format results

### Phase 4: Main App (1-2 hours)
- Create `streamlit_app.py` - Wire everything together
- Implement session state management
- Handle user interactions

### Phase 5: Testing (1 hour)
- Test all 3 models
- Test edge cases
- Manual UI testing

### Phase 6: Documentation (1 hour)
- Create user guide
- Update README
- Add screenshots

---

## 🎨 Key Code Snippets

### Model Loading (model_manager.py)
```python
import streamlit as st
import joblib
from transformers import AutoModelForSequenceClassification, AutoTokenizer

@st.cache_resource
def load_models():
    """Load all models and cache them"""
    models = {}
    
    # Baseline models
    models['logreg'] = joblib.load('models/baselines/logistic_regression_tfidf.joblib')
    models['svm'] = joblib.load('models/baselines/linear_svm_tfidf.joblib')
    
    # Transformer
    models['distilbert'] = {
        'model': AutoModelForSequenceClassification.from_pretrained('models/transformer/distilbert/'),
        'tokenizer': AutoTokenizer.from_pretrained('models/transformer/distilbert/')
    }
    
    return models
```

### Sidebar (sidebar.py)
```python
def render_sidebar(models):
    """Render model selection sidebar"""
    st.sidebar.title("🤖 Cloud NLP Classifier")
    
    # Model selection
    model_options = {
        'Logistic Regression (Baseline)': 'logreg',
        'Linear SVM (Baseline)': 'svm',
        'DistilBERT (Transformer)': 'distilbert'
    }
    
    selected = st.sidebar.selectbox(
        "Select Model:",
        options=list(model_options.keys())
    )
    
    return model_options[selected]
```

### Chat Interface (chat_interface.py)
```python
def render_chat_interface():
    """Render chat input and history"""
    # Display chat history
    for msg in st.session_state.chat_history:
        if msg['role'] == 'user':
            st.chat_message("user").write(msg['content'])
        else:
            st.chat_message("assistant").write(msg['content'])
    
    # Input area
    user_input = st.chat_input("Enter text to analyze...")
    
    return user_input
```

### Main App (streamlit_app.py)
```python
import streamlit as st
from components.sidebar import render_sidebar
from components.chat_interface import render_chat_interface
from utils.model_manager import load_models
from utils.inference_handler import predict

# Page config
st.set_page_config(
    page_title="Cloud NLP Classifier",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Load models
models = load_models()

# Render UI
selected_model = render_sidebar(models)
user_input = render_chat_interface()

# Handle input
if user_input:
    # Add user message
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_input
    })
    
    # Get prediction
    result = predict(user_input, selected_model, models)
    
    # Add bot response
    st.session_state.chat_history.append({
        'role': 'assistant',
        'content': result
    })
    
    st.rerun()
```

---

## 📊 Estimated Time

| Phase | Core Features | With Optional |
|-------|--------------|---------------|
| **Setup** | 30 min | 30 min |
| **Model Loading** | 1-2 hours | 1-2 hours |
| **UI Components** | 2-3 hours | 3-4 hours |
| **Main App** | 1-2 hours | 2-3 hours |
| **Testing** | 1 hour | 1-2 hours |
| **Documentation** | 1 hour | 2 hours |
| **Scripts** | 30 min | 1 hour |
| **TOTAL** | **6-10 hours** | **12-20 hours** |

---

## ✅ Checklist

### Before Starting
- [ ] All 3 models are trained and saved
- [ ] FastAPI server works (for reference)
- [ ] Python environment is set up
- [ ] Review task list and approve scope

### Core Implementation
- [ ] Phase 1: Setup (dependencies, structure)
- [ ] Phase 2: Model loading (ModelManager)
- [ ] Phase 3: UI components (sidebar, chat, results)
- [ ] Phase 4: Main app (wire everything)
- [ ] Phase 5: Testing (all models work)
- [ ] Phase 6: Documentation (guides)
- [ ] Phase 7: Scripts (run commands)

### Optional Enhancements
- [ ] Analytics dashboard
- [ ] Batch processing
- [ ] Model comparison
- [ ] Export functionality
- [ ] Docker integration
- [ ] Cloud deployment

---

## 🎯 Success Criteria

- ✅ UI loads in < 5 seconds
- ✅ All 3 models work correctly
- ✅ Inference < 2 seconds per request
- ✅ Chat history displays properly
- ✅ Results are accurate and well-formatted
- ✅ No crashes during normal use
- ✅ Intuitive and easy to use

---

## 🚨 Common Issues & Solutions

### Issue: Models not loading
**Solution**: Check file paths, ensure models are trained

### Issue: Slow inference
**Solution**: Use GPU, reduce max_seq_length, or use baseline models

### Issue: Memory errors
**Solution**: Load only one model at a time, or use smaller batch size

### Issue: UI not updating
**Solution**: Use `st.rerun()` after state changes

### Issue: Streamlit Cloud deployment fails
**Solution**: Reduce memory usage, deploy only transformer model

---

## 📚 Resources

### Documentation
- **Streamlit Docs**: https://docs.streamlit.io/
- **Streamlit API Reference**: https://docs.streamlit.io/library/api-reference
- **Streamlit Cheat Sheet**: https://docs.streamlit.io/library/cheatsheet

### Examples
- **Streamlit Gallery**: https://streamlit.io/gallery
- **Chat Apps**: https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps

### Deployment
- **Streamlit Cloud**: https://streamlit.io/cloud (Free tier available)
- **Docker**: Use existing Dockerfile as reference
- **GCP Cloud Run**: Similar to FastAPI deployment

---

## 🎨 UI Preview (Mockup)

```
┌─────────────────────────────────────────────────────────────────┐
│ 🤖 Cloud NLP Classifier                                          │
├─────────────┬───────────────────────────────────────────────────┤
│             │  💬 Sentiment Analysis Chat                        │
│ Select      │                                                     │
│ Model:      │  You: "I love this product!"                       │
│ ┌─────────┐│  ┌───────────────────────────────────────────────┐│
│ │DistilBERT││  │ 🤖 Bot: ✅ Non-Hate Speech                    ││
│ │    ▼    ││  │ Confidence: 98.5% | ⏱️ 45ms                   ││
│ └─────────┘│  │ ████████████████████ Non-Hate: 98.5%          ││
│             │  │ ██ Hate: 1.5%                                 ││
│ 📊 Model    │  └───────────────────────────────────────────────┘│
│ Info:       │                                                     │
│ • Accuracy: │  ┌───────────────────────────────────────────────┐│
│   92.5%     │  │ 💭 Enter your text here...                    ││
│ • F1: 0.91  │  └───────────────────────────────────────────────┘│
│ • Speed:    │                                          [Submit] 🚀│
│   ~50ms     │                                                     │
│             │                                                     │
│ [Clear      │                                                     │
│  History]   │                                                     │
└─────────────┴───────────────────────────────────────────────────┘
```

---

## 📞 Next Steps

1. **Review** the detailed task list: `docs/STREAMLIT_UI_TASK_LIST.md`
2. **Check** the visual overview: `docs/STREAMLIT_UI_OVERVIEW.md`
3. **Approve** the scope and features
4. **Start** with Phase 1 (Setup)
5. **Iterate** through phases 2-7
6. **Test** and polish
7. **Deploy** and document

---

**Ready to start?** Let me know and we'll begin with Phase 1! 🚀

---

**Document Version**: 1.0  
**Created**: 2025-12-09  
**Status**: Ready for Review ✅
