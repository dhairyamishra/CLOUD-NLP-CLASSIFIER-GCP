# 🎨 Streamlit UI Implementation Task List

## 📋 Overview

This task list outlines the implementation of a **minimal Streamlit web interface** for the Cloud NLP Classifier project. The UI will provide an interactive chat-like interface for sentiment/hate speech analysis with model selection capabilities.

---

## 🎯 Feature Requirements

### Core Features
- ✅ **Sidebar**: Model selection dropdown (Baseline models + Transformer)
- ✅ **Chat Interface**: Text input area for user queries
- ✅ **Results Display**: Sentiment analysis results with confidence scores
- ✅ **Chat History**: Conversation-style display of queries and responses
- ✅ **Model Info**: Display loaded model details and performance metrics

### User Experience
- Clean, modern UI with intuitive navigation
- Real-time inference with loading indicators
- Color-coded sentiment results (positive/negative/neutral)
- Responsive design for different screen sizes
- Error handling with user-friendly messages

---

## 📦 Phase 1: Project Setup & Dependencies

### 1.1 Update Dependencies
- [ ] **Add Streamlit to requirements.txt**
  - [ ] Add `streamlit>=1.28.0` to `requirements.txt`
  - [ ] Add `plotly>=5.17.0` for interactive visualizations (optional)
  - [ ] Add `pandas>=2.0.0` (already present, verify version)
  
### 1.2 Create Streamlit Directory Structure
- [ ] **Create UI module structure**
  - [ ] Create `src/ui/` directory
  - [ ] Create `src/ui/__init__.py`
  - [ ] Create `src/ui/streamlit_app.py` (main application)
  - [ ] Create `src/ui/components/` directory for reusable components
  - [ ] Create `src/ui/components/__init__.py`
  - [ ] Create `src/ui/utils/` directory for helper functions
  - [ ] Create `src/ui/utils/__init__.py`

### 1.3 Create Configuration
- [ ] **Create Streamlit config**
  - [ ] Create `.streamlit/` directory in project root
  - [ ] Create `.streamlit/config.toml` with theme and server settings
  - [ ] Configure page title, icon, and layout
  - [ ] Set up color theme (primary, background, text colors)

---

## 🏗️ Phase 2: Model Loading & Management

### 2.1 Create Model Manager
- [ ] **Implement ModelManager class** (`src/ui/utils/model_manager.py`)
  - [ ] Create `ModelManager` class to handle all model operations
  - [ ] Implement `load_baseline_models()` method
    - [ ] Load Logistic Regression model from `models/baselines/logistic_regression_tfidf.joblib`
    - [ ] Load Linear SVM model from `models/baselines/linear_svm_tfidf.joblib`
    - [ ] Handle missing model files gracefully
  - [ ] Implement `load_transformer_model()` method
    - [ ] Load DistilBERT model from `models/transformer/distilbert/`
    - [ ] Load tokenizer from same directory
    - [ ] Load label mappings from `labels.json`
    - [ ] Detect GPU/CPU and set device
  - [ ] Implement `get_available_models()` method
    - [ ] Return list of successfully loaded models
    - [ ] Include model metadata (type, size, performance)
  - [ ] Implement caching with `@st.cache_resource` decorator
  - [ ] Add error handling and logging

### 2.2 Create Inference Handler
- [ ] **Implement InferenceHandler class** (`src/ui/utils/inference_handler.py`)
  - [ ] Create `InferenceHandler` class for predictions
  - [ ] Implement `predict_baseline(text, model_name)` method
    - [ ] Preprocess text (lowercase, clean)
    - [ ] Vectorize with TF-IDF
    - [ ] Get prediction and confidence scores
    - [ ] Return formatted results
  - [ ] Implement `predict_transformer(text)` method
    - [ ] Tokenize input text
    - [ ] Run inference on GPU/CPU
    - [ ] Get prediction probabilities
    - [ ] Map prediction to label
    - [ ] Return formatted results with all class scores
  - [ ] Implement `measure_inference_time()` decorator
  - [ ] Add input validation and error handling

---

## 🎨 Phase 3: UI Components

### 3.1 Create Sidebar Component
- [ ] **Implement sidebar** (`src/ui/components/sidebar.py`)
  - [ ] Create `render_sidebar()` function
  - [ ] Add project title and logo/icon
  - [ ] Implement model selection dropdown
    - [ ] List all available models (Baselines + Transformer)
    - [ ] Show model type badges (ML/DL)
    - [ ] Display model status (loaded/not loaded)
  - [ ] Add model information section
    - [ ] Show selected model details
    - [ ] Display performance metrics (accuracy, F1)
    - [ ] Show inference speed estimate
  - [ ] Add settings section (optional)
    - [ ] Confidence threshold slider
    - [ ] Show/hide probabilities toggle
    - [ ] Clear chat history button
  - [ ] Add footer with project info and links

### 3.2 Create Chat Interface Component
- [ ] **Implement chat interface** (`src/ui/components/chat_interface.py`)
  - [ ] Create `render_chat_interface()` function
  - [ ] Implement chat input area
    - [ ] Text area for user input
    - [ ] Character counter (optional)
    - [ ] Submit button with keyboard shortcut (Enter)
  - [ ] Implement chat history display
    - [ ] User message bubbles (right-aligned, blue)
    - [ ] Bot response bubbles (left-aligned, gray)
    - [ ] Timestamp for each message
    - [ ] Scrollable container
  - [ ] Add example prompts section
    - [ ] Quick-start example texts
    - [ ] Click to populate input
  - [ ] Implement auto-scroll to latest message

### 3.3 Create Results Display Component
- [ ] **Implement results display** (`src/ui/components/results_display.py`)
  - [ ] Create `render_results()` function
  - [ ] Implement sentiment badge display
    - [ ] Color-coded badges (red=hate, green=non-hate)
    - [ ] Confidence percentage
    - [ ] Emoji indicators (optional)
  - [ ] Implement probability scores display
    - [ ] Horizontal bar chart for all classes
    - [ ] Percentage labels
    - [ ] Color gradient based on confidence
  - [ ] Add inference time display
    - [ ] Show milliseconds taken
    - [ ] Performance indicator (fast/medium/slow)
  - [ ] Add explanation section (optional)
    - [ ] Brief description of prediction
    - [ ] Model reasoning (if available)

### 3.4 Create Header Component
- [ ] **Implement header** (`src/ui/components/header.py`)
  - [ ] Create `render_header()` function
  - [ ] Add main title with icon
  - [ ] Add subtitle/description
  - [ ] Add status indicators
    - [ ] Models loaded count
    - [ ] API status (if applicable)
  - [ ] Add navigation tabs (optional)
    - [ ] Chat tab
    - [ ] Analytics tab
    - [ ] About tab

---

## 💻 Phase 4: Main Application Logic

### 4.1 Create Main App File
- [ ] **Implement main application** (`src/ui/streamlit_app.py`)
  - [ ] Set up page configuration
    - [ ] Page title: "Cloud NLP Classifier"
    - [ ] Page icon: 🤖 or 💬
    - [ ] Layout: wide
    - [ ] Initial sidebar state: expanded
  - [ ] Initialize session state
    - [ ] `chat_history`: List of messages
    - [ ] `selected_model`: Currently selected model
    - [ ] `model_manager`: Cached model manager instance
    - [ ] `inference_count`: Track number of predictions
  - [ ] Implement main layout
    - [ ] Render sidebar
    - [ ] Render header
    - [ ] Render chat interface
  - [ ] Implement event handlers
    - [ ] Handle model selection change
    - [ ] Handle text submission
    - [ ] Handle clear history
  - [ ] Add error boundaries and exception handling

### 4.2 Create Session State Manager
- [ ] **Implement state management** (`src/ui/utils/state_manager.py`)
  - [ ] Create `initialize_session_state()` function
  - [ ] Implement `add_message(role, content, metadata)` function
  - [ ] Implement `clear_chat_history()` function
  - [ ] Implement `get_chat_history()` function
  - [ ] Implement `update_model_selection(model_name)` function
  - [ ] Add state persistence (optional)
    - [ ] Save to local storage
    - [ ] Load on app restart

### 4.3 Create Utility Functions
- [ ] **Implement helper functions** (`src/ui/utils/helpers.py`)
  - [ ] Create `format_timestamp()` function
  - [ ] Create `format_confidence(score)` function
  - [ ] Create `get_sentiment_color(label)` function
  - [ ] Create `get_sentiment_emoji(label)` function
  - [ ] Create `truncate_text(text, max_length)` function
  - [ ] Create `validate_input(text)` function
  - [ ] Add text preprocessing helpers

---

## 🎯 Phase 5: Advanced Features (Optional)

### 5.1 Analytics Dashboard
- [ ] **Create analytics tab** (`src/ui/components/analytics.py`)
  - [ ] Implement prediction statistics
    - [ ] Total predictions count
    - [ ] Predictions by model
    - [ ] Predictions by sentiment
  - [ ] Add visualizations
    - [ ] Pie chart: Sentiment distribution
    - [ ] Bar chart: Model usage
    - [ ] Line chart: Predictions over time
  - [ ] Add performance metrics
    - [ ] Average inference time
    - [ ] Model comparison table

### 5.2 Batch Processing
- [ ] **Implement batch inference** (`src/ui/components/batch_processor.py`)
  - [ ] Add file upload widget (CSV/TXT)
  - [ ] Implement batch prediction
  - [ ] Show progress bar
  - [ ] Display results table
  - [ ] Add download button for results (CSV)

### 5.3 Model Comparison
- [ ] **Implement side-by-side comparison** (`src/ui/components/model_comparison.py`)
  - [ ] Allow selecting multiple models
  - [ ] Run inference on all selected models
  - [ ] Display results in comparison table
  - [ ] Highlight differences
  - [ ] Show performance metrics comparison

### 5.4 Export & Sharing
- [ ] **Implement export features**
  - [ ] Export chat history to JSON/CSV
  - [ ] Generate shareable link (if deployed)
  - [ ] Export results as PDF report
  - [ ] Copy results to clipboard

---

## 🧪 Phase 6: Testing & Validation

### 6.1 Create Test Suite
- [ ] **Create UI tests** (`tests/test_streamlit_ui.py`)
  - [ ] Test model loading
  - [ ] Test inference with sample inputs
  - [ ] Test error handling
  - [ ] Test session state management
  - [ ] Test component rendering (if possible)

### 6.2 Manual Testing Checklist
- [ ] **Test all features manually**
  - [ ] Model selection works correctly
  - [ ] Baseline models produce predictions
  - [ ] Transformer model produces predictions
  - [ ] Chat history displays correctly
  - [ ] Results are accurate and formatted properly
  - [ ] Error messages appear for invalid inputs
  - [ ] UI is responsive on different screen sizes
  - [ ] Performance is acceptable (< 2s inference)

### 6.3 Edge Cases
- [ ] **Test edge cases**
  - [ ] Empty input
  - [ ] Very long input (> 512 tokens)
  - [ ] Special characters and emojis
  - [ ] Multiple rapid submissions
  - [ ] Model not loaded scenario
  - [ ] Network errors (if API mode)

---

## 📝 Phase 7: Documentation

### 7.1 Create UI Documentation
- [ ] **Create comprehensive docs** (`docs/STREAMLIT_UI_GUIDE.md`)
  - [ ] Installation instructions
  - [ ] Running the UI locally
  - [ ] Feature overview with screenshots
  - [ ] Troubleshooting guide
  - [ ] Configuration options
  - [ ] Deployment instructions

### 7.2 Update Main README
- [ ] **Update project README.md**
  - [ ] Add Streamlit UI section
  - [ ] Add quick start command
  - [ ] Add screenshot/GIF of UI
  - [ ] Update architecture diagram
  - [ ] Add UI to feature list

### 7.3 Create User Guide
- [ ] **Create user guide** (`docs/UI_USER_GUIDE.md`)
  - [ ] How to use the chat interface
  - [ ] How to switch models
  - [ ] How to interpret results
  - [ ] Tips for best results
  - [ ] FAQ section

---

## 🚀 Phase 8: Deployment & Scripts

### 8.1 Create Run Scripts
- [ ] **Create execution scripts**
  - [ ] Create `scripts/run_streamlit_local.sh` (Linux/Mac)
    ```bash
    #!/usr/bin/env bash
    set -e
    streamlit run src/ui/streamlit_app.py --server.port 8501
    ```
  - [ ] Create `scripts/run_streamlit_local.ps1` (Windows)
    ```powershell
    streamlit run src/ui/streamlit_app.py --server.port 8501
    ```
  - [ ] Create `run_streamlit.py` (cross-platform)
    ```python
    import subprocess
    subprocess.run(["streamlit", "run", "src/ui/streamlit_app.py"])
    ```
  - [ ] Make scripts executable

### 8.2 Docker Integration
- [ ] **Add Streamlit to Docker** (Optional)
  - [ ] Create `Dockerfile.streamlit`
  - [ ] Add Streamlit service to `docker-compose.yml`
  - [ ] Expose port 8501
  - [ ] Test Docker deployment
  - [ ] Update Docker documentation

### 8.3 Cloud Deployment
- [ ] **Deploy to cloud** (Optional)
  - [ ] Deploy to Streamlit Cloud (free tier)
  - [ ] Or deploy to GCP Cloud Run
  - [ ] Configure secrets management
  - [ ] Set up custom domain (optional)
  - [ ] Document deployment process

---

## 📊 Phase 9: Performance Optimization

### 9.1 Caching Strategy
- [ ] **Implement caching**
  - [ ] Use `@st.cache_resource` for model loading
  - [ ] Use `@st.cache_data` for static data
  - [ ] Implement LRU cache for recent predictions
  - [ ] Clear cache button in settings

### 9.2 Loading Optimization
- [ ] **Optimize load times**
  - [ ] Lazy load models (only when selected)
  - [ ] Show loading spinners
  - [ ] Preload most common model
  - [ ] Optimize imports
  - [ ] Minimize session state size

### 9.3 UI Performance
- [ ] **Optimize rendering**
  - [ ] Limit chat history display (last 50 messages)
  - [ ] Implement virtual scrolling for long chats
  - [ ] Debounce input validation
  - [ ] Optimize re-renders with keys

---

## ✅ Phase 10: Final Polish

### 10.1 UI/UX Enhancements
- [ ] **Polish the interface**
  - [ ] Add loading animations
  - [ ] Add success/error notifications
  - [ ] Improve color scheme consistency
  - [ ] Add tooltips for complex features
  - [ ] Implement keyboard shortcuts
  - [ ] Add dark mode support (optional)

### 10.2 Accessibility
- [ ] **Improve accessibility**
  - [ ] Add ARIA labels
  - [ ] Ensure keyboard navigation works
  - [ ] Test with screen readers
  - [ ] Ensure sufficient color contrast
  - [ ] Add alt text for images

### 10.3 Final Testing
- [ ] **Comprehensive testing**
  - [ ] Test on different browsers
  - [ ] Test on mobile devices
  - [ ] Test with different models
  - [ ] Performance testing with load
  - [ ] User acceptance testing

---

## 📋 Summary & Checklist

### Core Deliverables
- [ ] ✅ Functional Streamlit UI with chat interface
- [ ] ✅ Model selection sidebar (3 models: LogReg, SVM, DistilBERT)
- [ ] ✅ Real-time sentiment analysis
- [ ] ✅ Chat history with formatted results
- [ ] ✅ Confidence scores and probability display
- [ ] ✅ Error handling and validation
- [ ] ✅ Documentation and user guide
- [ ] ✅ Run scripts for all platforms

### Optional Enhancements
- [ ] 🎯 Analytics dashboard
- [ ] 🎯 Batch processing
- [ ] 🎯 Model comparison view
- [ ] 🎯 Export functionality
- [ ] 🎯 Cloud deployment

### Success Criteria
- [ ] ✅ UI loads in < 5 seconds
- [ ] ✅ Inference completes in < 2 seconds
- [ ] ✅ All models work correctly
- [ ] ✅ No crashes or errors during normal use
- [ ] ✅ Intuitive and easy to use
- [ ] ✅ Responsive on desktop and mobile

---

## 🎯 Estimated Timeline

| Phase | Estimated Time | Priority |
|-------|---------------|----------|
| Phase 1: Setup | 30 minutes | High |
| Phase 2: Model Loading | 1-2 hours | High |
| Phase 3: UI Components | 2-3 hours | High |
| Phase 4: Main App | 1-2 hours | High |
| Phase 5: Advanced Features | 2-4 hours | Medium |
| Phase 6: Testing | 1-2 hours | High |
| Phase 7: Documentation | 1-2 hours | High |
| Phase 8: Deployment | 1 hour | Medium |
| Phase 9: Optimization | 1-2 hours | Medium |
| Phase 10: Polish | 1-2 hours | Low |

**Total Core Implementation**: 6-10 hours  
**Total with Optional Features**: 12-20 hours

---

## 🚀 Next Steps

1. **Review this task list** and approve the scope
2. **Prioritize phases** (recommend focusing on Phases 1-4, 6-7 first)
3. **Begin implementation** starting with Phase 1
4. **Iterate and test** after each phase
5. **Deploy and document** once core features are complete

---

## 📝 Notes

- **Model Availability**: Ensure all models are trained before UI implementation
- **Dependencies**: Streamlit requires Python 3.8+
- **Performance**: Transformer inference may be slow on CPU (2-5 seconds)
- **Deployment**: Streamlit Cloud has 1GB RAM limit (may need optimization)
- **Alternatives**: Can use Gradio as a lighter alternative to Streamlit

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-09  
**Status**: Ready for Review ✅
