# 🧠 MindBridge AI: Mental Health Risk Prediction System

> **A revolutionary two-stage mental health screening platform** that combines clinical machine learning with adaptive conversational AI — making mental health assessment accessible, stigma-free, and human-centered.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python) 
![Scikit-learn](https://img.shields.io/badge/Scikit--Learn-Decision%20Tree-orange?logo=scikit-learn) 
![Gradio](https://img.shields.io/badge/UI-Gradio-red?logo=gradio) 
![DTC Accuracy](https://img.shields.io/badge/DTC%20Accuracy-98.7%25-brightgreen) 
![Stage 1](https://img.shields.io/badge/Stage%201-Complete-green) 
![Stage 2](https://img.shields.io/badge/Stage%202-In%20Design-yellow)

---

## 📋 Table of Contents

- [Executive Summary](#-executive-summary)
- [The Problem We're Solving](#-the-problem-were-solving)
- [Our Two-Stage Solution](#-our-two-stage-solution)
  - [Stage 1: Clinical Risk Engine (✅ Complete)](#stage-1-clinical-risk-engine--complete)
  - [Stage 2: Conversational AI Bridge (🔜 In Design)](#stage-2-conversational-ai-bridge--in-design)
- [System Architecture](#-system-architecture)
- [Quick Start Guide](#-quick-start-guide)
- [Project Structure](#-project-structure)
- [Documentation Hub](#-documentation-hub)
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

**Stage 1 ✅ COMPLETE:**
- Decision Tree Classifier trained on 10,000 patient records
- 98.7% accuracy on structured clinical data
- Production-ready Gradio interface
- HIPAA-compliant, privacy-preserving design

**Stage 2 🔜 IN DESIGN:**
- Specialized LLM for text-to-score conversion
- Expert consultation phase (model selection pending)
- Adaptive learning architecture planned
- **No development until expert approval** (learned from Phase 1 keyword failure)

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
│  STAGE 2: Conversational AI Bridge (In Design)              │
│  • Understands context, slang, emotions                     │
│  • Infers psychological factors from natural language       │
│  • Handles typos, code-switching, cultural expressions      │
│  • Adapts and learns from every interaction                 │
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

## Stage 2: Conversational AI Bridge 🔜 In Design

### The Challenge

Stage 1 requires **numeric scores** as input (depression: 22/30, anxiety: 14/21). But humans don't talk in numbers — we express feelings through language:

- "I feel like drowning yaar"
- "kms rn" (kill myself right now)
- "My brain is mush, can't focus on anything"
- "Sab khatam hai" (Hinglish: everything is over)

**The Gap:**
We need a bridge that converts **free text** → **clinical scores** while handling:
- ✅ Slang and abbreviations ("kms", "fml", "idwl")
- ✅ Typos and misspellings ("depresed", "anxios", "suisidal")
- ✅ Code-switching (Hinglish, Spanglish, mixed languages)
- ✅ Cultural idioms of distress
- ✅ Emojis and emoticons ("feeling like 💀", "mental health 📉")
- ✅ Context-dependent meaning ("dying for coffee" ≠ suicidal)

### What Went Wrong Before (Phase 1 Lesson Learned)

**Keyword Matching Approach (❌ FAILED):**
- Generated 14,300+ keywords across 13 psychological factors
- Built semantic clusters, intensity amplifiers, crisis detection
- Worked on clean clinical text
- **Catastrophic failure on real-world noisy text:**

| Test Input | Expected Score | Keyword Score | Result |
|------------|---------------|---------------|--------|
| "kms rn" | 9.0/10 | 0.0/10 | ❌ Crisis missed |
| "wan die bro" | 8.5/10 | 0.0/10 | ❌ Typo not matched |
| "yaar sab khatam hai" | 8.0/10 | 0.0/10 | ❌ Hinglish failed |
| "feeling like 💀" | 6.0/10 | 0.0/10 | ❌ Emoji not understood |

**Root Cause:**
Keywords are **lookup tables**. Human language requires **understanding**.

Substring matching can't handle:
- Infinite variations of expression
- Novel slang combinations
- Phonetic spellings
- Cultural context shifts

**Lesson:** You can't pattern-match your way to language understanding. We need a model that **learns representations**, not one that matches strings.

### The Solution: Specialized LLM for Mental Health

**What We Need (Not Yet Built):**

A **fine-tuned language model** specifically trained for psychological assessment that:

1. **Understands Logical Reasoning**
   - Connects symptoms: "can't sleep" + "no energy" + "withdrawing from friends" → depression pattern
   - Distinguishes grief ("my son died, can't stop crying") from depression ("everything feels pointless")
   - Recognizes cognitive distortions ("everyone thinks I'm a loser" → mind reading)

2. **Recognizes Psychological Patterns**
   - Grief vs depression vs burnout vs adjustment disorder
   - Acute stress vs PTSD vs anxiety disorders
   - Postpartum depression specific markers
   - Substance use comorbidity indicators

3. **Generalizes Across Expressions**
   - "kms rn" = suicidal ideation ✅
   - "dying for coffee" ≠ suicidal ✅
   - "wan die" (typo) = same as "want to die" ✅
   - "dead inside" (metaphor) = emotional numbness ✅

4. **Has Context Awareness**
   - "baby" in postpartum context vs general harm context
   - "work is killing me" (stress) vs "I'm going to kill myself" (crisis)
   - "I'm fine" (genuine) vs "I'm fine" (masking pain)

5. **Is Adaptive and Learns**
   - Gets better with each interaction
   - Learns from mistakes (like Claude's training approach)
   - Updates understanding based on expert feedback
   - Improves without requiring full retraining

6. **Handles Multiple Languages/Dialects**
   - Hinglish (Hindi + English code-switching)
   - Spanglish (Spanish + English)
   - AAVE (African American Vernacular English)
   - Gen-Z internet slang
   - Regional expressions of distress

**What It Doesn't Need:**
- ❌ Coding ability (irrelevant for this task)
- ❌ General world knowledge (focused only on mental health domain)
- ❌ Creative writing capability (assessment, not generation)

### Technical Requirements (Planned)

**Model Architecture Options (Under Expert Review):**

| Candidate | Parameters | Pros | Cons | Status |
|-----------|-----------|------|------|--------|
| DistilBERT-base | 66M | Fast, lightweight, good baseline | Not domain-specific | ⏳ Pending review |
| MentalBERT | ~110M | Pre-trained on mental health data | Less documented | ⏳ Pending review |
| TinyLLaMA | 1.1B | Strong reasoning, multilingual | Larger, slower inference | ⏳ Pending review |
| Custom Transformer | TBD | Tailored exactly to our needs | Requires more training data | ⏳ Pending review |

**Training Strategy (Expert-Guided):**

Inspired by Claude's approach:
1. **Create Explicit Rules Document**
   - Define psychological factor definitions
   - List known expressions per condition
   - Document edge cases (grief vs depression)
   - Specify crisis detection criteria

2. **Curate Training Dataset**
   - Reddit r/SuicideWatch posts (labeled by therapists)
   - Twitter mental health tweets
   - Kaggle depression/suicide datasets
   - Include both correct examples AND common mistakes

3. **Train with Reinforcement**
   - Model makes prediction → compare against rules
   - Expert provides feedback on errors
   - Model updates weights to avoid repeating mistakes
   - Iterative refinement over multiple epochs

4. **Validate Reasoning Capability**
   - Not just accuracy metrics
   - Test on novel expressions not in training set
   - Verify it understands why, not just what
   - Ensure generalization beyond pattern matching

**Expected Capabilities (After Training):**

| Capability | Target | Current (Keywords) | Gap |
|------------|--------|-------------------|-----|
| Formal English accuracy | >92% | 94% | ✅ On track |
| Slang/abbreviations | >85% | 0% | ❌ Critical gap |
| Code-switching (Hinglish) | >80% | 0% | ❌ Critical gap |
| Typo tolerance | >85% | 0% | ❌ Critical gap |
| Crisis detection sensitivity | 100% | 100% | ✅ Maintained |
| False positive rate | <5% | 3.2% | ✅ Acceptable |
| Inference latency | <500ms | N/A | New requirement |

### Development Protocol (CRITICAL)

**NO BLIND DEVELOPMENT ANYMORE.**

Every action must follow this protocol:

1. **Document Understanding**
   - Write detailed problem analysis
   - Identify knowledge gaps
   - Research existing approaches

2. **Consult Expert**
   - Present specific questions to hired ML expert
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

### End-to-End Flow

```
┌─────────────────────────────────────────────────────────────┐
│  USER INTERFACE (Gradio Web App)                            │
│  http://localhost:7860                                      │
│                                                             │
│  Tab 1: Manual DTC Input                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Age: [25 ▼]  Gender: [Male ▼]                      │    │
│  │ Depression Score: [━━━━━━━━━○━━━] 22/30            │    │
│  │ Anxiety Score: [━━━━━━○━━━━━━━] 14/21              │    │
│  │ ... (13 total features)                             │    │
│  │                                                     │    │
│  │ [PREDICT RISK]                                      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  Tab 2: Text Assessment (Future)                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Q1: How have you been feeling lately?              │    │
│  │ [I feel like drowning yaar. Can't get out of bed.] │    │
│  │                                                     │    │
│  │ Q2: How has your sleep been?                       │    │
│  │ [Terrible, waking up at 3am thinking about...]     │    │
│  │                                                     │    │
│  │ [ANALYZE & PREDICT]                                 │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: Conversational AI Bridge (In Design)              │
│                                                             │
│  User Text → Preprocessing → LLM Encoder → Factor Scores   │
│                                                             │
│  Output: {                                                  │
│    depression_score: 22/30,                                 │
│    anxiety_score: 14/21,                                    │
│    social_support: 28/100,                                  │
│    crisis_flag: TRUE                                        │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: Clinical Risk Engine (✅ Complete)                │
│                                                             │
│  Decision Tree Classifier traverses nodes:                  │
│                                                             │
│  root: depression_score <= 15? NO (22 > 15)                 │
│  ├─ node 1: depression_score <= 22? YES                     │
│  │  └─ node 2: social_support <= 35? YES (28 ≤ 35)         │
│  │     └─ node 3: sleep_hours <= 5? YES                     │
│  │        └─ LEAF: "High Risk" (91% confidence)             │
│                                                             │
│  Crisis Check: crisis_flag == TRUE → Override to HIGH       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  OUTPUT DISPLAY                                             │
│                                                             │
│  ╔═══════════════════════════════════════════════════╗     │
│  ║  ⚠️  PREDICTION: HIGH RISK (91% confidence)       ║     │
│  ╚═══════════════════════════════════════════════════╝     │
│                                                             │
│  Contributing Factors:                                      │
│  ✓ Elevated depression (22/30)                              │
│  ✓ Low social support (28/100)                              │
│  ✓ Sleep disturbance                                        │
│                                                             │
│  ⚠️  Crisis Alert:                                          │
│  📞 Helpline: +91-80-25497777                               │
│  💡 Recommendations: Seek professional help...              │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction

```python
# Simplified flow (current Stage 1 only)

from mental_health_ml_system import MentalHealthPredictor

# Initialize
predictor = MentalHealthPredictor()

# Stage 1: Direct numeric input (working now)
input_numeric = {
    "age": 42,
    "depression_score": 18,
    "anxiety_score": 9,
    # ... all 13 features
}
result = predictor.predict_single(input_numeric)
# Returns: {"risk_level": "High", "confidence": 0.91}

# Future: Stage 2 integration
text_input = "I feel like drowning yaar"
scores = stage2_llm.analyze(text_input)  # Not yet implemented
# Returns: {"depression_score": 22, "anxiety_score": 14, ...}
result = predictor.predict_single(scores)
```

---

## ⚡ Quick Start Guide

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (for cloning repository)

### Installation

**1. Clone the Repository**
```bash
git clone <repository-url>
cd "Heathcare ML Pred"
```

**2. Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**Requirements include:**
- gradio>=3.50.0 (web interface)
- pandas>=1.5.0 (data processing)
- numpy>=1.21.0 (numerical operations)
- scikit-learn>=1.3.0 (machine learning)
- joblib>=1.2.0 (model persistence)
- colorama>=0.4.6 (colored terminal output)

### Running the Application

**Launch:**
```bash
python mental_health_ml_system.py
```

**Access:**
- Opens automatically in browser at `http://localhost:7860`
- Or manually navigate to the URL shown in terminal

**Using Stage 1 (Manual Input):**
1. Select **"DTC Prediction"** tab
2. Adjust 13 sliders/dropdowns:
   - Demographics: age, gender, employment, work environment
   - Clinical history: mental_health_history, seeks_treatment
   - Current state: stress_level, sleep_hours, physical_activity_days
   - Psychological scores: depression_score (0-30), anxiety_score (0-21), etc.
3. Click **"Predict Risk"**
4. View results:
   - Risk level (Low/Medium/High)
   - Confidence percentage
   - Contributing factors
   - Personalized recommendations
   - Crisis resources (if triggered)

**Testing with Sample Cases:**

The app includes preset test cases:
- **Grieving Parent**: High risk (depression, loss)
- **Burnt-Out Executive**: Medium risk (occupational stress)
- **Isolated Teenager**: Medium-High risk (social anxiety)
- **Recovering Patient**: Low risk (maintenance check-in)

Click any preset to auto-fill the form and see predictions.

### Troubleshooting

**Port Already in Use:**
```
Error: Cannot bind to port 7860
Solution: App will automatically use 7861, 7862, etc.
```

**Model Not Found:**
```
Error: saved_models/mental_health_model.pkl not found
Solution: Ensure you're running from project root directory
```

**Dependencies Missing:**
```bash
pip install --upgrade -r requirements.txt
```

---

## 📁 Project Structure

```
Heathcare ML Pred/
│
├── 📘 README.md                           # This comprehensive guide
├── 📄 mental_health_ml_system.py          # Main application (STABLE - DO NOT MODIFY)
├── 📄 requirements.txt                    # Python dependencies
│
├── 📊 saved_models/                       # FROZEN: Production model files
│   ├── mental_health_model.pkl            # Trained Decision Tree (9.3 KB)
│   ├── label_encoders.pkl                 # Categorical encoders (1.5 KB)
│   ├── feature_columns.pkl                # Feature order (0.2 KB)
│   └── model_metrics.pkl                  # Performance metrics (0.5 KB)
│
├── 📚 explainer/                          # Documentation hub
│   ├── 00_EXPLAINER_DIRECTORY_README.md   # Navigation guide
│   ├── 01_COMPLETE_PROJECT_EXPLANATION.md # Full project overview
│   ├── 02_STARTUP_PITCH_DECK.md           # 16-slide investor pitch
│   ├── 03_TECHNICAL_ARCHITECTURE.md       # Engineering deep dive
│   ├── 04_USER_JOURNEY_SCENARIOS.md       # 5 real-world user personas
│   └── 05_EXPLAINER_CREATION_SUMMARY.md   # Documentation summary
│
├── 📝 PROGRESS_LOG/                       # Development phase documentation
│   ├── 00_README.md                       # Rules & protocols (CRITICAL)
│   ├── dev_01/                            # Stage 1 development (archived)
│   ├── dev_02/                            # Keyword matching phase (archived)
│   ├── dev_03/                            # Pipeline integration (archived)
│   └── dev_04/                            # LLM development (future)
│       ├── 04_detailed_report.md          # Deep-dive documentation
│       ├── codes/                         # Code snapshots
│       ├── imgs/                          # Metrics graphs
│       ├── metrics/                       # Performance data
│       └── mod/                           # Model modifications
│
├── 🗂️ KEYWORDS/                          # Archived keyword files (Stage 1 reference)
│   ├── 00_KEYWORDS_EXPLAINER.md           # What each file is, why archived
│   ├── 01_depression_keywords.json        # ~1,112 TP/TN/FP/FN keywords
│   ├── 02_sleep_keywords.json             # ~1,038 keywords
│   └── ... (13 total factor files)        # 14,300+ keywords total
│
├── 📦 ARCHIVE/                            # Historical development files
│   ├── old_dataset/                       # Original 10K training CSV
│   ├── old_dev/                           # 34 early iteration files
│   ├── progress_old/                      # 10 development logs from Stage 1
│   ├── text_processing/                   # Complete keyword engine source
│   └── insights/                          # Original research docs
│
└── 🛠️ ENV_SETUP/                         # Environment setup scripts
    ├── README_SETUP.md                    # How to use each script
    ├── setup_windows.bat                  # Windows setup with live output
    ├── setup_linux.sh                     # Linux setup with tee logging
    └── setup_macos.sh                     # macOS setup with Homebrew detection
```

**Important Notes:**
- `mental_health_ml_system.py` is **STABLE** — do not modify
- All experimental code goes in `PROGRESS_LOG/dev_X/` folders
- Root directory contains **ONLY** essential files (README, requirements, main app)
- Documentation lives in `explainer/` and `PROGRESS_LOG/`

---

## 📖 Documentation Hub

### For First-Time Readers

Start here: [`explainer/01_COMPLETE_PROJECT_EXPLANATION.md`](explainer/01_COMPLETE_PROJECT_EXPLANATION.md)
- Executive summary
- Problem statement
- Two-stage solution overview
- Development journey
- Future roadmap

### For Investors

Pitch deck: [`explainer/02_STARTUP_PITCH_DECK.md`](explainer/02_STARTUP_PITCH_DECK.md)
- 16 complete slides
- Market opportunity ($21.8B TAM)
- Business model (SaaS tiers, $500-5K/month)
- Financial projections ($180K → $6M revenue)
- Competitive landscape
- Team & ask ($500K pre-seed)

### For Engineers

Technical architecture: [`explainer/03_TECHNICAL_ARCHITECTURE.md`](explainer/03_TECHNICAL_ARCHITECTURE.md)
- System architecture diagrams
- Component specifications
- API design with function signatures
- Data flow (9-step pipeline)
- Security & compliance (HIPAA checklist)
- Performance optimization (25ms latency)

### For Clinicians & Designers

User scenarios: [`explainer/04_USER_JOURNEY_SCENARIOS.md`](explainer/04_USER_JOURNEY_SCENARIOS.md)
- 5 detailed user personas:
  - Priya (42, grieving parent, India)
  - Alex (16, isolated teenager, Ohio)
  - David (38, burnt-out executive, SF)
  - Sarah (31, postpartum mother, Texas)
  - Marcus (29, recovering patient, Chicago)
- Exact user inputs with system analysis
- Clinical interpretations (DSM-5 considerations)
- Tailored recommendations

### For Development Team

Rules & protocols: [`PROGRESS_LOG/00_README.md`](PROGRESS_LOG/00_README.md)
- Non-negotiable development rules
- Documentation depth requirements
- Expert consultation protocol
- Sacred files (what not to modify)
- Common pitfalls to avoid

**All documentation follows sequential numbering** within each directory for easy tracking and reference.

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

**Stage 2: Conversational AI Bridge 🔜 In Design**
- Q3 2026: Expert consultation (model selection, training strategy)
- Q3 2026: Dataset curation (Reddit, Twitter, Kaggle sources)
- Q4 2026: Model fine-tuning (DistilBERT/MentalBERT/TinyLLaMA)
- Q4 2026: Validation on real-world noisy text
- Q1 2027: Integration with Stage 1
- Q1 2027: Beta launch with pilot customers

**Protocol:**
- NO blind development (learned from keyword failure)
- Expert approval required before coding
- Every iteration documented in PROGRESS_LOG/dev_04/

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
Interested in integrating MindBridge AI? See [`explainer/02_STARTUP_PITCH_DECK.md`](explainer/02_STARTUP_PITCH_DECK.md) for partnership details.

**For Healthcare Institutions:**
Pilot program applications open Q3 2026. Contact maintainers for early access.

**For Researchers:**
Collaboration opportunities available for validation studies. See [`PROGRESS_LOG/00_README.md`](PROGRESS_LOG/00_README.md) for research protocol.

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

**Last Updated:** March 2026  
**Version:** 2.0 (Complete restructure with Stage 1/Stage 2 clarity)  
**Maintained By:** MindBridge AI Development Team  
**Status:** Stage 1 Production-Ready | Stage 2 In Design (Expert-Guided)

*P.S. — If you're reading this and struggling, please reach out. The resources above are real, and the people on the other end care. You matter.* 💙
