# 🧠 MindBridge AI: Mental Health Risk Prediction System

> **An empathy-first mental health companion** combining clinical machine learning with conversational AI — featuring a Claude-inspired sanctuary interface where users feel understood, not analyzed.

![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python) 
![MongoDB](https://img.shields.io/badge/MongoDB-Primary-green?logo=mongodb)
![Redis](https://img.shields.io/badge/Redis-Cache-red?logo=redis)
![DTC Accuracy](https://img.shields.io/badge/DTC%20Accuracy-98.7%25-brightgreen) 
![Status](https://img.shields.io/badge/Status-Active%20Development-orange)

---

## 📋 Table of Contents

- [Executive Summary](#-executive-summary)
- [The Problem We're Solving](#-the-problem-were-solving)
- [Our Two-Stage Solution](#-our-two-stage-solution)
  - [Stage 1: Clinical Risk Engine (✅ Complete)](#stage-1-clinical-risk-engine--complete)
  - [Stage 2: Conversational AI Bridge (✅ LIVE)](#stage-2-conversational-ai-bridge--live)
- [System Architecture](#-system-architecture)
- [Quick Start Guide](#-quick-start-guide)
- [Project Structure](#-project-structure)
- [Performance Metrics](#-performance-metrics)
- [Development Roadmap](#-development-roadmap)
- [Team & Acknowledgments](#-team--acknowledgments)
- [License & Citation](#-license--citation)

---

## 🎯 Executive Summary

This is a **production-ready mental health risk prediction system** designed for real-world deployment in telemedicine, employee wellness programs, schools, and healthcare clinics.

### What Makes This Different

Traditional mental health tools ask people to **rate themselves on clinical scales** (0-10 depression, 0-10 anxiety). This feels:
- ❌ Cold and robotic
- ❌ Shameful (admitting "I'm suicidal" to a checkbox)
- ❌ Inaccessible (requires insight into your own symptoms)

**Our Innovation:**
People type natural answers → AI understands psychological meaning → Predicts risk level with 98.7% accuracy

**Example:**
```
User types: "I feel like drowning yaar. Can't get out of bed most days."
↓
AI infers: depression_score = 22/30, social_support = 28/100
↓
System predicts: HIGH RISK (91% confidence) + Crisis resources
```

### Current Status

**✅ PRODUCTION-READY:**
- **Decision Tree Classifier**: 98.7% accuracy on clinical data
- **Conversational AI**: Live LLM integration via Ollama
- **Modern Stack**: Next.js 15 + FastAPI + MongoDB + Redis
- **Claude-Inspired UI**: Warm, empathetic design with 💬/🧠 mode toggle
- **Dual Mode System**: Direct Chat + ML+Hybrid assessment
- **100% Backward Compatible**: localStorage for anonymous users

**🔄 ACTIVE DEVELOPMENT:**
- JWT-based account system (upcoming)
- Cross-device session sync (planned)
- Progressive enhancement from anonymous → authenticated

---

## 💔 The Problem We're Solving

### The Mental Health Crisis

**Global Scale:**
- 1 billion+ people live with mental health conditions worldwide
- 75% never receive treatment due to stigma, cost, or inaccessibility
- Average delay between symptom onset and treatment: **11 years**

**Why Existing Tools Fail:**

1. **Stigma Barrier**
   - Asking someone to rate their depression 0-10 feels clinical and exposing
   - Admitting suicidal thoughts to a checkbox is terrifying
   - People mask symptoms when interfaces feel judgmental

2. **Communication Mismatch**
   - Traditional tools: _"On a scale of 0-30, how depressed are you?"_
   - Real humans: _"I feel like dead weight, bro. Everything's pointless."_
   - Existing digital tools fail on slang, typos, abbreviations, code-switching

3. **Accessibility Gap**
   - Professional consultations cost $100-300/session
   - Waiting lists: 4-8 weeks for non-emergency cases
   - Geographic barriers (rural areas, developing countries have 1 psychiatrist per 100K people)

4. **Early Detection Failure**
   - Subclinical cases (not "bad enough" for help) go undetected
   - Prevention opportunities missed
   - Issues escalate to crisis before intervention

**The Result:**
Mental health issues remain hidden until they become emergencies. We need a system that **listens first**, judges never, and connects people to help before it's too late.

---

## 🚀 Our Two-Stage Solution

We built a **two-stage architecture** that separates clinical prediction (what we predict) from human communication (how people express it).

```
┌─────────────────────────────────────────────────────────────┐
│                    USER EXPERIENCE                          │
│  "I haven't been sleeping. Work is crushing me. I feel      │
│   like I'm failing everyone."                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: Conversational AI Bridge (✅ LIVE via Ollama)        │
│  • LLM-powered text understanding                         │
│  • Empathy-driven conversation                            │
│  • Real-time feature extraction                           │
│  • Mode toggle: 💬 Chat / 🧠 ML+Hybrid                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: Clinical Risk Engine (✅ Complete)                │
│  • Decision Tree Classifier (98.7% accuracy)                │
│  • 13 clinical features → Low/Medium/High risk              │
│  • Interpretable predictions (exact decision rules)         │
│  • Crisis detection + resource matching                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    HIGH RISK (87%)
                    + Crisis Resources
```

---

## Stage 1: Clinical Risk Engine ✅ Complete

### What It Is

A **Decision Tree Classifier** trained on 10,000 patient records to predict mental health risk levels (Low / Medium / High) based on 13 clinical and demographic features.

### Technical Specifications

**Model Configuration:**
```python
DecisionTreeClassifier(
    max_depth=12,              # Captures complex patterns without overfitting
    min_samples_split=10,      # Prevents memorization of small samples
    min_samples_leaf=5,        # Ensures robust decision boundaries
    class_weight='balanced',   # Handles class imbalance automatically
    ccp_alpha=0.001            # Cost-complexity pruning for generalization
)
```

**Training Data:**
- **Dataset**: `ARCHIVE/old_dataset/mental_health_dataset.csv`
- **Samples**: 10,000 individuals
- **Features**: 13 clinical + demographic variables
- **Target**: `mental_health_risk` (Low: 17.4%, Medium: 58.9%, High: 23.7%)

**Feature Set:**

| Feature | Type | Range/Values | Importance |
|---------|------|--------------|------------|
| Age | Numerical | 18-65 | 0.7% |
| Gender | Categorical | Male/Female/Non-binary | 0.4% |
| Employment Status | Categorical | Employed/Student/Self-employed/Unemployed | 1.2% |
| Work Environment | Categorical | On-site/Remote/Hybrid | 0.2% |
| Mental Health History | Binary | Yes/No | 1.8% |
| Seeks Treatment | Binary | Yes/No | 0.1% |
| Stress Level | Ordinal | 1-10 | 8.9% |
| Sleep Hours | Continuous | 2-12 | 5.4% |
| Physical Activity Days | Discrete | 0-7 | <0.1% |
| **Depression Score** | Continuous | **0-30** | **34.2%** ⭐ |
| **Anxiety Score** | Continuous | **0-21** | **28.7%** ⭐ |
| **Social Support Score** | Continuous | **0-100** | **15.6%** ⭐ |
| Productivity Score | Continuous | 0-100 | 3.1% |

⭐ Top 3 predictors account for 78.5% of decision importance

### Performance Metrics

**Overall Performance (Test Set: 2,000 samples):**
```
Accuracy:   98.70%  ← Excellent for medical applications
Precision:  97.98%  ← High prediction quality
Recall:     99.13%  ← Comprehensive case detection
F1-Score:   98.54%  ← Balanced performance
```

**Per-Class Performance:**
| Risk Level | Precision | Recall | F1-Score |
|------------|-----------|--------|----------|
| Low | 96.38% | 99.43% | 97.88% |
| Medium | 99.83% | 97.96% | 98.88% |
| High | 97.73% | 100.00% | 98.85% |

**Key Insights:**
- ✅ 100% recall on High risk → **No crisis cases missed**
- ✅ Balanced performance across all classes
- ✅ Fast inference: < 1ms per prediction
- ✅ Fully interpretable: can show exact decision path

### Why Decision Tree?

We tested alternatives and rejected them:

| Model | Why Rejected |
|-------|-------------|
| Random Forest | Loses interpretability (black box ensemble) |
| Logistic Regression | Assumes linear relationships — mental health isn't linear |
| SVM | Requires feature scaling, harder to explain to non-technical users |
| KNN | O(n) inference — too slow for real-time, memory-hungry |

**Decision Tree Advantages:**
1. **Interpretable**: Every prediction traces back to exact if/else rules
2. **Mixed data types**: Handles categorical + numerical without scaling
3. **Fast inference**: O(log n) complexity — instant predictions
4. **Mirrors clinical reasoning**: Risk assessment follows if/else logic just like doctors

### Crisis Detection Protocol

The system includes **real-time crisis monitoring**:

**Detection Triggers:**
- Direct statements: "I want to kill myself", "I'm going to end it all"
- Passive ideation: "Everyone would be better off without me"
- Indirect warnings: "I won't be around much longer", "This is the last time"

**Response Protocol:**
```
IF crisis_detected OR risk_harm_score > threshold:
    1. Override prediction to HIGH RISK (regardless of DTC output)
    2. Display emergency alert banner (red)
    3. Show location-specific crisis resources
    4. Provide immediate helpline numbers
    5. Encourage professional help-seeking
```

**Example Output:**
```
╔═══════════════════════════════════════════════════════════╗
║  ⚠️  CRISIS ALERT: We're concerned about your safety     ║
╚═══════════════════════════════════════════════════════════╝

Based on what you shared, we're detecting significant distress.
Please reach out for support right now:

🚨 Emergency: Call 112 (India) / 911 (US) / 999 (UK)
📞 Suicide Helpline: +91-80-25497777 (24/7)
💬 Crisis Text Line: Text HOME to 741741

You don't have to go through this alone. Help is available.
```

### How to Use Stage 1

**Option A: Manual Input (Direct Scores)**
```bash
# Launch the application
python mental_health_ml_system.py

# Opens at http://localhost:7860
# Select "DTC Prediction" tab
# Enter 13 values via sliders/dropdowns
# Click "Predict Risk"
```

**Option B: Programmatic API**
```python
from mental_health_ml_system import MentalHealthPredictor

predictor = MentalHealthPredictor()

input_data = {
    "age": 42,
    "gender": "Female",
    "employment_status": "Employed",
    "depression_score": 18,
    "anxiety_score": 9,
    "social_support_score": 22,
    # ... all 13 features
}

result = predictor.predict_single(input_data)
# Returns: {"risk_level": "High", "confidence": 0.91, ...}
```

**Saved Model Files:**
```
saved_models/
├── mental_health_model.pkl      # Trained Decision Tree (9.3 KB)
├── label_encoders.pkl           # Categorical encoders (1.5 KB)
├── feature_columns.pkl          # Feature order (0.2 KB)
└── model_metrics.pkl            # Performance metrics (0.5 KB)
```

All models are **frozen and production-ready**. Do not modify.

---

## Stage 2: Conversational AI Bridge ✅ LIVE

### The Solution: LLM-Powered Text Understanding

**What We Built:**
A working conversational AI that converts **free text** → **clinical scores** using local LLMs via Ollama:

| Input | AI Understanding | Output |
|-------|-----------------|--------|
| "I feel like drowning yaar" | Depression pattern detected | depression_score: 22/30 |
| "kms rn" | Crisis slang recognized | crisis_flag: TRUE |
| "wan die bro" | Typo-tolerant inference | suicidal_ideation: 9/10 |
| "sab khatam hai" | Hinglish code-switching handled | hopelessness: high |
| "work is killing me" | Context-aware (stress ≠ suicidal) | stress_level: 8/10 |

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  USER INTERFACE (Next.js 15 + Claude-Inspired Design)       │
│  http://localhost:3000                                      │
│                                                             │
│  💬 Direct Chat Mode    →  "Just talk, no analysis"          │
│  🧠 ML+Hybrid Mode    →  "Understand patterns together"    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  FASTAPI BACKEND (Python)                                   │
│  • Empathy-driven LLM prompts                               │
│  • Real-time feature extraction                             │
│  • Crisis detection & safety protocols                      │
│  • MongoDB persistence (optional)                         │
│  • Redis caching for LLM responses                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  OLLAMA (Local LLM)                                         │
│  • qwen2.5:7b (default) - fast, empathetic                  │
│  • llama3.2 (fallback) - English-optimized                  │
│  • Customizable model selection                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: DTC Risk Engine (98.7% accuracy)                  │
│  • Risk prediction: Low / Medium / High                     │
│  • 13 clinical features extracted from conversation         │
│  • Crisis override: Always HIGH if crisis detected          │
└─────────────────────────────────────────────────────────────┘
```

### Mode System

**💬 Direct Chat Mode:**
- Pure conversational support
- Empathy-first responses
- No clinical analysis unless requested
- Crisis detection active in background

**🧠 ML+Hybrid Mode:**
- Structured assessment (5 Whys technique)
- Real-time empathy map visualization
- Progressive feature extraction
- Final DTC prediction with compassionate delivery

### Technical Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | Next.js 15, React 19, Tailwind | Claude-inspired UI |
| Backend | FastAPI, Python 3.9+ | API + ML orchestration |
| LLM | Ollama (qwen2.5:7b, llama3.2) | Text understanding |
| Database | MongoDB | Session persistence |
| Cache | Redis | LLM response caching |
| ML | scikit-learn DTC | Risk prediction |

### Performance

- LLM inference: 500ms-2s (local GPU/CPU)
- DTC prediction: <1ms
- Crisis detection: Real-time (keyword + LLM dual check)
- UI mode switch: <100ms
   - Get recommendations on model choice
   - Validate training strategy
   - Review dataset curation approach

3. **Get Approval**
   - Expert signs off on approach
   - Document expert's recommendations
   - Create detailed implementation plan

4. **Then (and Only Then) Code**
   - Implement approved approach
   - Document every iteration
   - Test rigorously on real-world cases
   - Compare against requirements

**This protocol exists because:**
We wasted effort on keyword matching (14,300+ keywords, 4 engine versions) that failed catastrophically on real text. Never again.

### Current Status

**Where We Are:**
- ✅ Problem clearly defined
- ✅ Requirements documented
- ✅ Past failures analyzed and understood
- ✅ Expert hired and ready to consult
- ⏳ Model selection pending expert review
- ⏳ Training strategy pending expert approval
- ⏳ Dataset sourcing in progress

**Next Steps (In Order):**
1. Expert consultation call (schedule date)
2. Present model options, get recommendation
3. Finalize training dataset sources
4. Get approval on architecture
5. Begin implementation (documented in PROGRESS_LOG/dev_04/)

**Timeline (Estimated):**
- Expert consultation: 1-2 weeks
- Model selection & dataset prep: 2-3 weeks
- Fine-tuning & validation: 4-6 weeks
- Integration & testing: 2-3 weeks
- **Total: 9-14 weeks to MVP**

---

## 🏗️ System Architecture

### Current Architecture (mindbridge-nextjs/)

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (Next.js 15)                                      │
│  http://localhost:3000                                      │
│                                                             │
│  🧠 MindBridge AI                    [💬 🧠 Mode Toggle]  👤  │
│                                                             │
│  ┌────────────┬────────────────────────────────────────┐   │
│  │ Sidebar    │  Welcome Screen / Chat Interface        │   │
│  │ • Sessions │                                        │   │
│  │ • Mode     │  "Hi [Name], I'm here to listen..."      │   │
│  │ • New Chat │                                        │   │
│  │ • Stats    │  [✨ New Conversation]                   │   │
│  │ • Actions  │                                        │   │
│  └────────────┴────────────────────────────────────────┘   │
│                                                             │
│  Claude-Inspired Design System:                             │
│  • Warm parchment palette (#f5f4ed)                         │
│  • Serif headlines + sans UI                                │
│  • Empathy-first micro-interactions                         │
│  • 100% backward compatible (localStorage)                  │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP / WebSocket
┌─────────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI)                                          │
│  http://localhost:8000                                      │
│                                                             │
│  Endpoints:                                                 │
│  • GET  /health          → System status                  │
│  • POST /interview       → Chat message handling          │
│  • POST /score           → Feature extraction             │
│  • POST /predict         → DTC risk prediction            │
│  • GET  /sessions        → MongoDB session history        │
│  • POST /hybrid-turn     → Hybrid mode interview          │
│  • POST /hybrid-analyze  → Full conversation analysis     │
│                                                             │
│  Components:                                                │
│  • llm_client.py    → Ollama integration                  │
│  • ml_predictor.py  → DTC model inference                 │
│  • database.py      → MongoDB + Redis                     │
│  • prompts.py       → Empathy-driven system prompts       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────┬──────────────────┬──────────────────┐
│  OLLAMA (LLM)       │  MongoDB         │  Redis           │
│  • qwen2.5:7b       │  • Sessions      │  • LLM cache     │
│  • llama3.2         │  • Crisis logs   │  • TTL: 1 hour   │
│  • Custom models    │  • Stats         │  • Graceful      │
│                     │  • Optional      │    fallback      │
└─────────────────────┴──────────────────┴──────────────────┘
```

### Mode System Flow

```
USER ARRIVES
     ↓
┌─────────────┐
│ Welcome     │ ← Personalized (first-time / returning / post-crisis)
│ Screen      │
└─────────────┘
     ↓
┌─────────────┐     ┌─────────────┐
│ 💬 Direct   │←──→│ 🧠 ML+Hybrid │  ← Mode toggle (top bar)
│ Chat        │     │ Mode        │
└─────────────┘     └─────────────┘
     │                     │
     ↓                     ↓
┌─────────────┐     ┌─────────────┐
│ Empathy     │     │ 5 Whys      │
│ Chat        │     │ Interview   │
│ (no ML)     │     │ (structured)│
└─────────────┘     └─────────────┘
     │                     │
     ↓                     ↓
┌─────────────┐     ┌─────────────┐
│ User can    │     │ Real-time   │
│ REQUEST     │     │ empathy map │
│ analysis    │     │ + DTC score │
└─────────────┘     └─────────────┘
     │                     │
     └──────────┬──────────┘
                ↓
        ┌─────────────┐
        │ Session     │ ← Persisted to MongoDB (if available)
        │ Saved       │ ← Always saved to localStorage
        └─────────────┘
```

### Component Interaction

```javascript
// Frontend: Start conversation
const response = await fetch('http://localhost:8000/interview', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "I feel like drowning yaar. Can't get out of bed.",
    history: [],
    userName: "Priya"
  })
});

// Returns: {
//   reply: "That sounds incredibly difficult...",
//   empathy_map: { says: "...", thinks: "...", feels: "..." },
//   crisis_detected: false,
//   ready_to_score: true,
//   prediction: { risk: "High", confidence: 0.91 }
// }
```

```python
# Backend: Process conversation
@app.post("/interview")
async def interview(req: InterviewRequest):
    # 1. Get LLM response
    reply = await llm_client.chat(req.message, req.history)
    
    # 2. Check for crisis keywords
    crisis = keyword_crisis_check(req.message)
    
    # 3. Extract empathy map (LLM-powered)
    empathy = await extract_empathy(req.message)
    
    # 4. Check if ready to score (LLM decides)
    ready = await llm_client.is_ready_to_score(req.history)
    
    # 5. If ready, extract features and predict
    if ready:
        features = await llm_client.extract_features(req.history)
        prediction = ml_predictor.predict(features)
        
        # 6. Persist to MongoDB
        db.save_session({
            "source": "empathy-chat",
            "risk": prediction["risk"],
            "features": features,
            "timestamp": datetime.now()
        })
    
    return InterviewResponse(...)
```

---

## ⚡ Quick Start Guide

### Prerequisites

- **Node.js 18+** (for Next.js frontend)
- **Python 3.9+** (for FastAPI backend)
- **Ollama** (for local LLM inference)
- **MongoDB** (optional, for session persistence)
- **Redis** (optional, for LLM caching)

### 1. Install Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows (PowerShell - Admin)
winget install Ollama.Ollama
```

Pull the default model:
```bash
ollama pull qwen2.5:7b
```

### 2. Start the Backend

```bash
cd mindbridge-nextjs/backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`
Health check: http://localhost:8000/health

### 3. Start the Frontend

```bash
cd mindbridge-nextjs

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### 4. (Optional) Start MongoDB + Redis

```bash
# Using Docker
docker run -d -p 27017:27017 --name mindbridge-mongo mongo:latest
docker run -d -p 6379:6379 --name mindbridge-redis redis:latest
```

These are optional — the app works 100% with localStorage if databases aren't running.

### Using the App

**First Visit:**
1. Open `http://localhost:3000`
2. See personalized welcome screen
3. Click **"✨ New Conversation"**

**Choose Your Mode:**
- **💬 Direct Chat** — Just talk, no clinical analysis
- **🧠 ML+Hybrid** — Structured assessment with DTC prediction

**During Chat:**
- Type naturally (supports Hinglish, slang, typos)
- Watch empathy map update in real-time (Hybrid mode)
- Crisis detection runs automatically
- Session saves to localStorage (and MongoDB if available)

**Access History:**
- Sessions appear in left sidebar
- Grouped by: Today → Yesterday → This Week → Older
- Click any session to view details

### Troubleshooting

**Backend not connecting:**
```
Ensure uvicorn is running on port 8000
Check: http://localhost:8000/health
```

**Ollama not responding:**
```bash
# Check Ollama status
ollama list

# Restart Ollama service
ollama serve
```

**Port conflicts:**
```bash
# Frontend (Next.js) auto-finds available port
# Backend: edit --port flag in uvicorn command
```

---

## 📁 Project Structure

### 🎯 Active Project: `mindbridge-nextjs/`

The main application is now in the `mindbridge-nextjs/` folder with a modern stack:

```
mindbridge-nextjs/
│
├── � Frontend (Next.js 15)
│   ├── app/
│   │   ├── page.jsx                 # Main app shell
│   │   ├── layout.jsx               # Root layout
│   │   ├── globals.css              # Design system (Claude-inspired)
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   │   ├── Sidebar.jsx      # Claude-style left sidebar
│   │   │   │   └── ModeToggle.jsx   # 💬/🧠 segmented control
│   │   │   ├── Chat/
│   │   │   │   └── WelcomeScreen.jsx # Personalized welcome variants
│   │   │   ├── Session/
│   │   │   │   └── SessionCard.jsx  # Session list items
│   │   │   ├── EmpathyChat.jsx      # Direct chat interface
│   │   │   ├── HybridAssess.jsx     # ML+Hybrid interview flow
│   │   │   ├── ManualAssess.jsx     # 13-field form (modal)
│   │   │   ├── HistoryTab.jsx       # Session history view
│   │   │   ├── AnalyticsTab.jsx     # Stats dashboard
│   │   │   └── ControlPanel.jsx     # Settings & configuration
│   │   └── lib/
│   │       └── api.js               # Backend API client
│   ├── package.json                 # Node dependencies
│   └── next.config.ts               # Next.js configuration
│
├── 🔧 Backend (FastAPI)
│   ├── backend/
│   │   ├── main.py                  # FastAPI app + endpoints
│   │   ├── llm_client.py            # Ollama integration
│   │   ├── ml_predictor.py          # DTC model inference
│   │   ├── database.py              # MongoDB + Redis
│   │   ├── prompts.py               # Empathy-driven prompts
│   │   └── requirements.txt         # Python dependencies
│   └── start.bat                    # Launch both frontend + backend
│
└── 📊 Saved Models (from root)
    └── saved_models/
        ├── mental_health_model.pkl  # DTC model (9.3 KB)
        ├── label_encoders.pkl       # Categorical encoders
        ├── feature_columns.pkl      # Feature order
        └── model_metrics.pkl        # Performance metrics
```

### 📚 Legacy Files
```
Heathcare ML Pred/
├── 📄 mental_health_ml_system.py      # ORIGINAL Gradio app (legacy)
├── � ARCHIVE/                        # Historical development files
└── 🗂️  Other folders                 # Past experiments (archived)
```

**Key Notes:**
- **Active development** happens in `mindbridge-nextjs/`
- **Legacy Gradio app** (`mental_health_ml_system.py`) is frozen but functional
- Archive folders contain past experiments and are not part of the active codebase

---

## 🔗 Repository

**GitHub:** [https://github.com/Daksh-M-Coder/Mental-Health-Prediction-using-ML-and-Data-Analytics](https://github.com/Daksh-M-Coder/Mental-Health-Prediction-using-ML-and-Data-Analytics)

---

## 📊 Performance Metrics

### Stage 1: Decision Tree Classifier

**Test Set Performance (2,000 held-out samples):**

| Metric | Score | Interpretation |
|--------|-------|----------------|
| **Accuracy** | **98.70%** | Excellent for medical applications |
| **Precision (Macro)** | **97.98%** | High prediction quality |
| **Recall (Macro)** | **99.13%** | Comprehensive case detection |
| **F1-Score (Macro)** | **98.54%** | Balanced precision/recall |

**Per-Class Breakdown:**

| Risk Level | Precision | Recall | F1-Score | Support |
|------------|-----------|--------|----------|---------|
| Low | 96.38% | 99.43% | 97.88% | 348 samples |
| Medium | 99.83% | 97.96% | 98.88% | 1,178 samples |
| High | 97.73% | 100.00% | 98.85% | 474 samples |

**Critical Success Factor:**
- ✅ **100% recall on High risk** → No crisis cases missed
- This is non-negotiable for safety-critical systems

**Feature Importance (Top 5):**
1. Depression Score (34.2%) — strongest predictor
2. Anxiety Score (28.7%) — second most important
3. Social Support Score (15.6%) — protective factor
4. Stress Level (8.9%) — acute distress indicator
5. Sleep Hours (5.4%) — physiological marker

**Inference Speed:**
- Single prediction: < 1ms
- Batch predictions (100 samples): 5.5ms per sample
- Suitable for real-time deployment

### Stage 2: Text Understanding (Targets)

**Performance Goals (Under Expert Review):**

| Capability | Target | Rationale |
|------------|--------|-----------|
| Formal English accuracy | >92% | Match human clinician agreement |
| Slang/abbreviations | >85% | Handle real-world youth communication |
| Code-switching (Hinglish) | >80% | Serve multilingual populations |
| Typo tolerance | >85% | Robust to common misspellings |
| Crisis detection sensitivity | 100% | Zero false negatives on suicidal ideation |
| False positive rate | <5% | Avoid overloading crisis resources |
| Inference latency | <500ms | Real-time user experience |

**Current Gap (Keyword Approach):**
- Slang: 0% (catastrophic failure)
- Code-switching: 0% (catastrophic failure)
- Typos: 0% (catastrophic failure)

**This is why we need a specialized LLM, not more keywords.**

---

## 🗺️ Development Roadmap

### Completed Milestones

**Stage 1: Clinical Risk Engine ✅**
- Q1 2026: DTC model trained and validated (98.7% accuracy)
- Q1 2026: Gradio interface deployed
- Q1 2026: Crisis detection protocol implemented
- Q2 2026: Pipeline integration complete (Fixes A+B+C)
- Q2 2026: Production deployment (stable version frozen)

**Lessons Learned:**
- ✅ Interpretability > marginal accuracy gains (healthcare needs explainability)
- ✅ Crisis detection must integrate with prediction (not separate override)
- ✅ Real-world testing is critical (lab performance ≠ field performance)

### Current Phase

**Stage 2: Conversational AI Bridge ✅ LIVE**
- April 2026: Next.js + FastAPI architecture complete
- April 2026: Ollama LLM integration (qwen2.5:7b, llama3.2)
- April 2026: Claude-inspired UI with mode toggle
- April 2026: MongoDB + Redis integration
- May 2026: JWT account system (planned)
- May 2026: Cross-device session sync (planned)

**Protocol:**
- ✅ LLM approach validated (vs keyword failure)
- ✅ Empathy-first design implemented
- ✅ Graceful degradation (works without DB)
- Progress documented in PROGRESS_LOG/

### Future Enhancements (Post-Stage 2)

**Specific Condition Prediction:**
- Currently: Only predicts risk level (Low/Medium/High)
- Future: Predict specific conditions:
  - Major Depressive Disorder
  - Generalized Anxiety Disorder
  - PTSD
  - Adjustment Disorders
  - Postpartum Depression
  - Substance Use Disorders

**Adaptive Learning:**
- Learn from every interaction
- Update model weights based on expert feedback
- Improve without full retraining
- Personalize to user's communication style over time

**Multi-Language Support:**
- Spanish translation
- Hindi translation
- Mandarin translation
- Culturally-adapted expressions of distress

**Integration Capabilities:**
- EHR integration (Epic, Cerner APIs)
- Telemedicine platforms (Teladoc, Amwell)
- Employee benefits systems (Workday, SAP SuccessFactors)
- Crisis hotline databases

---

## 👥 Team & Acknowledgments

### Development Team

**Built with guidance from:**
- Machine Learning Engineers (DTC optimization, transformer fine-tuning)
- Licensed Clinical Psychologists (DSM-5 criteria, crisis protocols)
- Healthcare AI Ethics Advisors (bias mitigation, fairness auditing)
- Early Beta Testers (provided real-world feedback on usability)

### Special Thanks

To everyone who:
- Participated in beta testing and provided honest feedback
- Shared their mental health journey to help train this system
- Reviewed documentation and caught inconsistencies
- Believed in the vision of stigma-free mental health screening

### In Memoriam

This project exists because mental health issues remain hidden until they become crises. Dedicated to anyone who suffered in silence because existing tools didn't listen to how they actually talked.

---

## 📜 License & Citation

### License

**MIT License** — Free for educational and research use

```
Copyright (c) 2026 MindBridge AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Commercial Use:**
For commercial licensing or partnership inquiries, please contact the maintainers.

### Citation

If you use this system in your research, please cite:

```bibtex
@software{mindbridge_ai_2026,
  author = {MindBridge AI Team},
  title = {MindBridge AI: Mental Health Risk Prediction System},
  year = {2026},
  url = {https://github.com/your-repo-url},
  version = {1.0.0}
}
```

### Ethical Use Guidelines

**APPROPRIATE USES:**
- ✅ Mental health screening in telemedicine platforms
- ✅ Employee wellness program assessments
- ✅ School/university mental health monitoring
- ✅ Research on AI-assisted mental health assessment
- ✅ Educational demonstrations of healthcare AI

**INAPPROPRIATE USES:**
- ❌ Replacing licensed mental health professionals
- ❌ Making diagnostic determinations without clinical oversight
- ❌ Using for insurance underwriting or employment decisions
- ❌ Deploying in crisis situations without human backup
- ❌ Any use that violates local healthcare regulations

**DISCLAIMER:**
This system is a **screening tool**, not a diagnostic instrument. All high-risk predictions should trigger human clinician review. Do not rely solely on automated predictions for critical decisions.

---

## 📞 Contact & Support

### Getting Help

**Technical Issues:**
- Open GitHub issue with tag `bug`
- Include error messages and steps to reproduce
- Attach logs from terminal (if available)

**Feature Requests:**
- Open GitHub issue with tag `enhancement`
- Describe use case and expected behavior
- Explain business/clinical value

**Clinical Questions:**
- Contact clinical advisory board (contact info in documentation)
- Do NOT use GitHub issues for patient-specific consultations

### Partnership Opportunities

**For Telemedicine Platforms:**
Interested in integrating MindBridge AI? Contact maintainers for partnership details.

**For Healthcare Institutions:**
Pilot program applications open Q3 2026. Contact maintainers for early access.

**For Researchers:**
Collaboration opportunities available for validation studies. Contact maintainers for research protocol details.

### Crisis Resources

**If you're experiencing a mental health crisis:**

🚨 **Emergency:** Call your local emergency number (911/112/999)

📞 **Suicide Hotlines:**
- US: 988 (Suicide & Crisis Lifeline)
- UK: 116 123 (Samaritans)
- India: +91-80-25497777 (iCall)
- International: https://findahelpline.com

💬 **Crisis Text Lines:**
- US/Canada: Text HOME to 741741
- UK: Text SHOUT to 85258
- India: Text HELP to 50909

**This system is not a substitute for emergency services.**

---

## 💙 Final Note

This system was built because **mental health is health**, and everybody deserves access to screening that feels human — even when it's powered by AI.

We learned the hard way that:
- Pattern matching can't replace understanding
- Blind development wastes effort (14,300 keywords taught us that)
- Stigma reduction requires intentional design
- Safety-critical systems need expert guidance

But we also learned that:
- Technology can reduce barriers to care
- Early detection saves lives
- Non-judgmental interfaces help people open up
- The right tool at the right time changes trajectories

**The Future We're Building:**
_A world where nobody suffers in silence because an AI listened first._

Thank you for being part of this journey.

---

**Last Updated:** April 2026  
**Version:** 3.0 (Next.js + FastAPI + MongoDB + Redis + Claude UI)  
**Repository:** [github.com/Daksh-M-Coder/Mental-Health-Prediction-using-ML-and-Data-Analytics](https://github.com/Daksh-M-Coder/Mental-Health-Prediction-using-ML-and-Data-Analytics)  
**Maintained By:** MindBridge AI Development Team  
**Status:** ✅ Stage 1 Production-Ready | ✅ Stage 2 LIVE | 🔄 Active Development

*P.S. — If you're reading this and struggling, please reach out. The resources above are real, and the people on the other end care. You matter.* 💙
