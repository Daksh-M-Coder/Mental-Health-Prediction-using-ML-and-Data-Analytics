# MindBridge AI — Next.js + Empathy Agent Implementation Plan

## Overview

We are building a **full-stack Next.js application** that wraps the existing trained Decision Tree Classifier (DTC) with an **Empathy-First AI interview layer**. The AI acts like a compassionate clinician: it listens, maps emotions via the **Empathy Map** framework, digs deeper using the **5 Whys** technique, then auto-fills the 13 clinical features and runs the DTC.

**Stack:**
- **Frontend**: Next.js 14 (App Router) — preserving exact UI from `mindbridge-ai.jsx`
- **AI Backend**: Python FastAPI — adapted from `ai_template/` with Ollama as primary LLM
- **ML Backend**: Existing `mental_health_model.pkl` + `label_encoders.pkl` (no retraining)
- **LLM**: Ollama (local, private) — primary; Groq as fallback

---

## Architecture: 3-Layer System

```
User (Browser)
    ↓  ↑
[Next.js Frontend — Port 3000]
  ├─ "/" Chat Tab     → Empathy Interview UI (new)
  └─ "/assess" Tab    → Manual Form UI (existing mindbridge-ai.jsx preserved)
    ↓  ↑
[Python FastAPI Backend — Port 5002]
  ├─ POST /interview   → Empathy Map + 5 Whys loop (LLM Call #1)
  ├─ POST /score       → Convert conversation → 13 JSON features (LLM Call #2)
  └─ POST /predict     → DTC prediction using saved_models/
    ↓  ↑
[Ollama — Port 11434]  (local LLM, no API keys needed)
  └─ Model: llama3.2:3b  (or llama3.1:8b for better quality)
```

---

## User Review Required

> [!IMPORTANT]
> **Ollama Model Choice**: The system uses Ollama locally. You need to have `ollama serve` running and a model pulled. We'll default to `llama3.2:3b` (fast, 2GB) or `llama3.1:8b` (better quality, 5GB). Please confirm which you have or want to pull.

> [!WARNING]
> **No API Keys Needed by Default**: Since you said "using Ollama as backend," the Python backend will use Ollama exclusively. The ai_template's Groq support is preserved as a fallback but won't be the default.

> [!IMPORTANT]
> **Project Location**: The Next.js app will be created at:
> `c:\Users\daksh\Programmer\Learning\COMP TECH SKILL\LOW CODE PROJECTS\Heathcare ML Pred\mindbridge-nextjs\`
> A separate subfolder in the same project directory.

---

## Proposed Changes

### 1. Python Backend (FastAPI + ML + Empathy Agent)

#### [NEW] `mindbridge-nextjs/backend/main.py`
The FastAPI server — replaces `ai_template/agent.py` with a healthcare-specific version.

**Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Backend + Ollama + model status |
| `POST` | `/interview` | Single-turn Empathy Map interview step |
| `POST` | `/score` | Convert full conversation history → 13 JSON features |
| `POST` | `/predict` | Load DTC + predict risk from 13 features |
| `POST` | `/predict-direct` | Skip interview, predict directly from manual form values |

**`/interview` Flow:**
```
User message → INTERVIEWER_SYSTEM_PROMPT → LLM →
{
  "reply": "Empathetic follow-up question",
  "empathy_map": { "says": [...], "thinks": [...], "does": [...], "feels": [...] },
  "ready_to_score": false,
  "crisis_detected": false
}
```

**`/score` Flow:**
```
Full conversation history → SCORING_SYSTEM_PROMPT → LLM →
{
  "age": 25, "depression_score": 28, "anxiety_score": 18,
  "sleep_hours": 3, "stress_level": 9, "social_support_score": 15,
  "physical_activity_days": 0, "mental_health_history": "Yes",
  "seeks_treatment": "No", "employment_status": "Employed",
  "work_environment": "On-site", "gender": "Male", "productivity_score": 20
}
```

**`/predict` Flow:**
```
13 JSON features → load mental_health_model.pkl → DTC prediction →
{
  "risk": "High", "confidence": 98.0,
  "depression_factor": 93, "anxiety_factor": 86,
  "social_factor": 85, "stress_factor": 90,
  "summary": "...", "recommendations": [...]
}
```

#### [NEW] `mindbridge-nextjs/backend/llm_client.py`
Simplified version of `ai_template/core/llm_client.py` — Ollama-only, no Groq key management needed. Just the `call_ollama()` function.

#### [NEW] `mindbridge-nextjs/backend/ml_predictor.py`
Wraps the existing `saved_models/` pkl files. Handles feature encoding, prediction, and confidence extraction.

#### [NEW] `mindbridge-nextjs/backend/prompts.py`
The two system prompts:
- `INTERVIEWER_SYSTEM_PROMPT` — Empathy Map + 5 Whys conversational agent
- `SCORING_SYSTEM_PROMPT` — Clinical scorer that outputs 13-feature JSON

#### [NEW] `mindbridge-nextjs/backend/requirements.txt`
```
fastapi
uvicorn
scikit-learn
pandas
numpy
joblib
```

---

### 2. Next.js Frontend

#### [NEW] `mindbridge-nextjs/` (Next.js 14 App)
Created via `npx create-next-app@latest ./`.

#### [NEW] `mindbridge-nextjs/src/app/page.js`
The main app shell — tabs:
- **🤝 AI Interview** (new, default tab) — Empathy chat interface
- **⚕ Manual Assess** — The existing mindbridge-ai.jsx form, preserved 1:1
- **📋 History** — Assessment history
- **📊 Analytics** — Model performance stats

#### [NEW] `mindbridge-nextjs/src/components/EmpathyChat.jsx`
The new conversational interview UI:
```
┌─────────────────────────────────────────────────────┐
│  🧠 MindBridge AI — Empathy Interview                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [Chat messages — empathetic AI + user turns]       │
│                                                     │
│  ┌── Empathy Map Live Tracker ──────────────────┐   │
│  │  SAYS | THINKS | DOES | FEELS               │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  [Text input] ─────────────────── [Send →]         │
│                                                     │
│  [⚠️ Crisis Resources if detected]                  │
└─────────────────────────────────────────────────────┘
```

**Key features:**
- Live Empathy Map sidebar updating as AI extracts data
- "5 Whys" depth indicator showing conversation depth
- Crisis detection → auto-show resources (no prediction)
- "Ready to Score" detection → auto-trigger `/score` then `/predict`
- Typing animation for AI responses
- Hinglish/slang-aware display

#### [NEW] `mindbridge-nextjs/src/components/ManualAssess.jsx`
The existing `mindbridge-ai.jsx` converted to a Next.js component — functionally identical, calling `/predict-direct` instead of Anthropic directly.

#### [NEW] `mindbridge-nextjs/src/components/ResultCard.jsx`
Shared result display (RiskBadge, CircularProgress rings, recommendations) — used by both chat and manual modes.

#### [NEW] `mindbridge-nextjs/src/app/globals.css`
Global styles — preserves all the glassmorphism, animations, DM Sans font, color tokens from the original.

#### [NEW] `mindbridge-nextjs/src/lib/api.js`
Frontend API client — thin wrapper for all fetch calls to the Python backend.

---

### 3. Configuration

#### [NEW] `mindbridge-nextjs/.env.local`
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:5002
```

#### [NEW] `mindbridge-nextjs/backend/.env`
```
AGENT_BACKEND=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
ML_MODEL_PATH=../../saved_models/mental_health_model.pkl
```

---

## Data Flow: Full Empathy Interview → Prediction

```
1. User opens app → "AI Interview" tab active
2. AI sends opening message: "Hi, I'm MindBridge. How are you feeling today?"
3. User types: "Bro, sab khatam hai. Can't sleep, don't wanna eat."
4. Frontend → POST /interview { message, conversation_history }
5. Backend → Ollama (INTERVIEWER_SYSTEM_PROMPT + conversation)
6. Ollama →  {
     reply: "That sounds really heavy. When you say 'sab khatam hai', 
             what specifically feels like it's ending for you?",
     empathy_map: { says: ["sab khatam hai"], thinks: ["hopelessness"], 
                    does: ["insomnia", "appetite loss"], feels: ["despair"] },
     ready_to_score: false,
     crisis_detected: false
   }
7. Frontend shows reply + updates Empathy Map sidebar
8. [2-3 more turns...]
9. When ready_to_score: true →
10. Frontend → POST /score { conversation_history }
11. Backend → Ollama (SCORING_SYSTEM_PROMPT) → 13 JSON features
12. Frontend → POST /predict { features }
13. Backend → DTC prediction → { risk: "High", confidence: 98, ... }
14. Frontend shows ResultCard with risk badge, factor rings, recommendations
15. If crisis_detected → show iCall/Vandrevala resources immediately
```

---

## Empathy Map Live Tracker Design

The right panel of the chat shows a live-updating Empathy Map:

```
┌──────────────────────────────┐
│  📡 EMPATHY MAP              │
├──────────┬───────────────────┤
│ 💬 SAYS  │ "sab khatam hai"  │
│          │ "can't sleep"     │
├──────────┼───────────────────┤
│ 🧠 THINKS│ Hopelessness      │
│          │ Worthlessness     │
├──────────┼───────────────────┤
│ 🏃 DOES  │ Insomnia          │
│          │ Appetite loss     │
├──────────┼───────────────────┤
│ ❤️ FEELS │ Despair           │
│          │ Exhaustion        │
└──────────┴───────────────────┘
  [5 Whys depth: ●●●○○]
  [Ready to score: 60%]
```

---

## Verification Plan

### Automated Tests
1. `curl http://localhost:5002/health` — confirms backend + Ollama + model status
2. `curl -X POST http://localhost:5002/predict-direct -d '{...}'` — manual form path works
3. Full chat flow test: 3-turn conversation → scoring → prediction

### Manual Verification
1. Open `http://localhost:3000` — UI matches mindbridge-ai.jsx aesthetic
2. Type "I feel really anxious lately" → AI responds empathetically
3. Complete 3-turn interview → AI detects readiness → auto-scores → shows prediction
4. Switch to "Manual Assess" tab → original form still works
5. Test crisis detection with "I want to disappear" → shows resources, no prediction
6. History tab shows both AI-interview and manual assessments
7. Export functionality works (CSV, JSON, MD, TXT)

---

## Build Order

1. ✅ Create `mindbridge-nextjs/` with Next.js
2. ✅ Build Python FastAPI backend (main.py + llm_client.py + ml_predictor.py + prompts.py)
3. ✅ Test backend standalone (`/health`, `/predict-direct`)
4. ✅ Build ManualAssess component (port mindbridge-ai.jsx → Next.js)
5. ✅ Build EmpathyChat component with Empathy Map tracker
6. ✅ Wire frontend → backend APIs
7. ✅ Polish animations, crisis detection, export panel
8. ✅ End-to-end test full flow
