# 🎨 Streamlit UI - Visual Overview & Quick Reference

## 📊 Project Summary

**Goal**: Add an interactive Streamlit web interface to the Cloud NLP Classifier for real-time sentiment analysis with a chat-style user experience.

---

## 🎯 Core Features

### 1. **Sidebar - Model Selection** 🎛️
```
┌─────────────────────────┐
│  🤖 Cloud NLP Classifier│
├─────────────────────────┤
│ Select Model:           │
│ ┌─────────────────────┐ │
│ │ DistilBERT (DL)  ▼ │ │
│ └─────────────────────┘ │
│                         │
│ 📊 Model Info:          │
│ • Type: Transformer     │
│ • Accuracy: 92.5%       │
│ • F1 Score: 0.91        │
│ • Speed: ~50ms          │
│                         │
│ ⚙️ Settings:            │
│ [ ] Show probabilities  │
│ [Clear History]         │
└─────────────────────────┘
```

**Available Models**:
- 🔵 **Logistic Regression + TF-IDF** (Baseline)
- 🔵 **Linear SVM + TF-IDF** (Baseline)
- 🟢 **DistilBERT** (Transformer)

---

### 2. **Chat Interface** 💬
```
┌────────────────────────────────────────────────┐
│  💬 Sentiment Analysis Chat                    │
├────────────────────────────────────────────────┤
│                                                │
│  You: "I love this product!"                   │
│  ┌──────────────────────────────────────────┐ │
│  │ 🤖 Bot: ✅ Non-Hate Speech                │ │
│  │ Confidence: 98.5%                         │ │
│  │ ⏱️ Inference: 45ms                        │ │
│  │                                           │ │
│  │ 📊 Probabilities:                         │ │
│  │ ████████████████████ Non-Hate: 98.5%     │ │
│  │ ██ Hate: 1.5%                            │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  You: "This is terrible and offensive"         │
│  ┌──────────────────────────────────────────┐ │
│  │ 🤖 Bot: ⚠️ Hate Speech                    │ │
│  │ Confidence: 87.3%                         │ │
│  │ ⏱️ Inference: 48ms                        │ │
│  └──────────────────────────────────────────┘ │
│                                                │
├────────────────────────────────────────────────┤
│ 💭 Enter your text here...                     │
│ ┌────────────────────────────────────────────┐│
│ │                                            ││
│ └────────────────────────────────────────────┘│
│                                    [Submit] 🚀 │
└────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│                   (src/ui/streamlit_app.py)              │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼──────────┐           ┌─────────▼─────────┐
│  Model Manager   │           │ Inference Handler │
│  (Load Models)   │           │  (Predictions)    │
└───────┬──────────┘           └─────────┬─────────┘
        │                                 │
        └────────────────┬────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼──────────┐           ┌─────────▼─────────┐
│ Baseline Models  │           │ Transformer Model │
│ (LogReg, SVM)    │           │   (DistilBERT)    │
└──────────────────┘           └───────────────────┘
```

---

## 📁 File Structure

```
src/ui/
├── __init__.py
├── streamlit_app.py              # Main application entry point
├── components/
│   ├── __init__.py
│   ├── sidebar.py                # Model selection sidebar
│   ├── chat_interface.py         # Chat UI and history
│   ├── results_display.py        # Results formatting
│   └── header.py                 # App header
└── utils/
    ├── __init__.py
    ├── model_manager.py          # Model loading & caching
    ├── inference_handler.py      # Prediction logic
    ├── state_manager.py          # Session state management
    └── helpers.py                # Utility functions

.streamlit/
└── config.toml                   # Streamlit configuration

scripts/
├── run_streamlit_local.sh        # Linux/Mac run script
├── run_streamlit_local.ps1       # Windows run script
└── run_streamlit.py              # Cross-platform runner

docs/
├── STREAMLIT_UI_TASK_LIST.md     # Detailed task breakdown
├── STREAMLIT_UI_GUIDE.md         # Installation & usage guide
└── UI_USER_GUIDE.md              # End-user documentation
```

---

## 🚀 Quick Start Commands

### Installation
```bash
# Add Streamlit to dependencies
pip install streamlit>=1.28.0

# Or update requirements.txt and reinstall
pip install -r requirements.txt
```

### Running the UI

**Windows:**
```powershell
.\scripts\run_streamlit_local.ps1
```

**Linux/Mac:**
```bash
bash scripts/run_streamlit_local.sh
```

**Cross-Platform:**
```bash
python run_streamlit.py
```

**Direct:**
```bash
streamlit run src/ui/streamlit_app.py --server.port 8501
```

### Access the UI
Open browser: **http://localhost:8501**

---

## 🎨 UI Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    User Opens Browser                    │
│                  http://localhost:8501                   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Streamlit App Initializes                   │
│  • Load page config                                      │
│  • Initialize session state                              │
│  • Cache and load models                                 │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Render UI Components                    │
│  ┌─────────────┐  ┌──────────────────────────────────┐ │
│  │   Sidebar   │  │        Main Content Area         │ │
│  │             │  │  ┌────────────────────────────┐  │ │
│  │ • Model     │  │  │        Header              │  │ │
│  │   Selection │  │  └────────────────────────────┘  │ │
│  │             │  │  ┌────────────────────────────┐  │ │
│  │ • Model     │  │  │     Chat History           │  │ │
│  │   Info      │  │  │  (Previous conversations)  │  │ │
│  │             │  │  └────────────────────────────┘  │ │
│  │ • Settings  │  │  ┌────────────────────────────┐  │ │
│  │             │  │  │      Text Input            │  │ │
│  └─────────────┘  │  │  [Submit Button]           │  │ │
│                   │  └────────────────────────────┘  │ │
│                   └──────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              User Enters Text & Submits                  │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Inference Pipeline                      │
│  1. Validate input                                       │
│  2. Get selected model                                   │
│  3. Preprocess text                                      │
│  4. Run inference                                        │
│  5. Format results                                       │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Display Results                         │
│  • Add to chat history                                   │
│  • Show sentiment badge                                  │
│  • Display confidence score                              │
│  • Show probability bars                                 │
│  • Display inference time                                │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              User Can Continue Chatting                  │
│  • Enter new text                                        │
│  • Switch models                                         │
│  • Clear history                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Implementation Phases

### ✅ **Phase 1: Setup** (30 min)
- Add dependencies
- Create directory structure
- Configure Streamlit

### ✅ **Phase 2: Model Loading** (1-2 hours)
- ModelManager class
- InferenceHandler class
- Caching implementation

### ✅ **Phase 3: UI Components** (2-3 hours)
- Sidebar component
- Chat interface
- Results display
- Header

### ✅ **Phase 4: Main App** (1-2 hours)
- Main application logic
- Session state management
- Event handling

### ✅ **Phase 5: Testing** (1-2 hours)
- Unit tests
- Manual testing
- Edge case validation

### ✅ **Phase 6: Documentation** (1-2 hours)
- User guide
- Installation guide
- Update README

### ✅ **Phase 7: Scripts** (1 hour)
- Run scripts for all platforms
- Docker integration (optional)

---

## 🎯 Key Features Breakdown

### Model Selection
- **Dropdown Menu**: Choose between 3 models
- **Model Info Card**: Shows accuracy, F1, speed
- **Dynamic Loading**: Models loaded on demand
- **Status Indicators**: Visual feedback for loaded models

### Chat Interface
- **Text Input**: Multi-line text area
- **Submit Button**: Trigger prediction
- **Chat History**: Scrollable conversation view
- **Message Bubbles**: User (right) vs Bot (left)
- **Timestamps**: Track when predictions were made

### Results Display
- **Sentiment Badge**: Color-coded (red/green)
- **Confidence Score**: Percentage display
- **Probability Bars**: Visual representation of all classes
- **Inference Time**: Performance metric
- **Emoji Indicators**: Visual feedback (✅/⚠️)

### Session Management
- **Chat History**: Persists during session
- **Model Selection**: Remembers choice
- **Clear History**: Reset conversation
- **State Persistence**: Maintains UI state

---

## 🔧 Technical Details

### Model Loading Strategy
```python
@st.cache_resource
def load_models():
    """Load all models once and cache"""
    models = {}
    
    # Load baseline models
    models['logreg'] = joblib.load('models/baselines/logistic_regression_tfidf.joblib')
    models['svm'] = joblib.load('models/baselines/linear_svm_tfidf.joblib')
    
    # Load transformer
    models['distilbert'] = AutoModelForSequenceClassification.from_pretrained(
        'models/transformer/distilbert/'
    )
    
    return models
```

### Inference Flow
```python
def predict(text, model_name):
    """Run inference on input text"""
    # 1. Validate input
    if not text or len(text) < 3:
        return error_response("Text too short")
    
    # 2. Get model
    model = get_model(model_name)
    
    # 3. Preprocess
    processed_text = preprocess(text)
    
    # 4. Predict
    start_time = time.time()
    prediction = model.predict(processed_text)
    inference_time = (time.time() - start_time) * 1000
    
    # 5. Format results
    return {
        'label': prediction['label'],
        'confidence': prediction['confidence'],
        'probabilities': prediction['probabilities'],
        'inference_time_ms': inference_time
    }
```

### Session State Structure
```python
{
    'chat_history': [
        {
            'role': 'user',
            'content': 'I love this!',
            'timestamp': '2025-12-09 08:30:00'
        },
        {
            'role': 'bot',
            'content': {
                'label': 'non-hate',
                'confidence': 0.985,
                'inference_time': 45
            },
            'timestamp': '2025-12-09 08:30:01'
        }
    ],
    'selected_model': 'distilbert',
    'inference_count': 42,
    'show_probabilities': True
}
```

---

## 📈 Performance Expectations

| Metric | Target | Notes |
|--------|--------|-------|
| **UI Load Time** | < 5 seconds | First load with model caching |
| **Inference Time (Baseline)** | < 10ms | TF-IDF + LogReg/SVM |
| **Inference Time (Transformer)** | < 100ms | DistilBERT on CPU |
| **Inference Time (GPU)** | < 50ms | DistilBERT on GPU |
| **Memory Usage** | < 2GB | All models loaded |
| **Concurrent Users** | 5-10 | Local deployment |

---

## 🎨 Color Scheme

```
Primary Colors:
• Main: #0066CC (Blue)
• Success: #28A745 (Green) - Non-hate speech
• Warning: #FFC107 (Yellow) - Uncertain
• Danger: #DC3545 (Red) - Hate speech

Background:
• Light: #F8F9FA
• Dark: #212529

Text:
• Primary: #212529
• Secondary: #6C757D
```

---

## ✅ Success Criteria

- [x] **Functional**: All models work correctly
- [x] **Fast**: Inference < 2 seconds
- [x] **Intuitive**: Easy to use without instructions
- [x] **Responsive**: Works on desktop and mobile
- [x] **Reliable**: No crashes during normal use
- [x] **Documented**: Clear guides for users and developers

---

## 🚀 Next Steps

1. **Review** this overview and the detailed task list
2. **Approve** the scope and features
3. **Prioritize** which phases to implement first
4. **Begin** implementation with Phase 1 (Setup)
5. **Iterate** and test after each phase
6. **Deploy** once core features are complete

---

## 📝 Notes

- **Model Availability**: Ensure all 3 models are trained before starting
- **Performance**: Transformer may be slow on CPU (consider GPU or optimization)
- **Deployment**: Streamlit Cloud has 1GB RAM limit (may need to deploy only 1 model)
- **Alternative**: Gradio is a lighter alternative if Streamlit is too heavy

---

**Ready to proceed?** Review the detailed task list at `docs/STREAMLIT_UI_TASK_LIST.md` and let me know when you're ready to start implementation! 🚀
