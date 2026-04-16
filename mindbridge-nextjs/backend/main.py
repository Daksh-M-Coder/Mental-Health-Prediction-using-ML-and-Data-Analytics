"""
main.py -- MindBridge AI FastAPI Backend
HTTP server exposing the Empathy Agent + DTC prediction pipeline.

Endpoints:
  GET  /health          -- System status (Ollama + model + available models)
  POST /interview       -- Single Empathy Map interview turn
  POST /score           -- Convert full conversation to 13 clinical features
  POST /predict         -- DTC prediction from 13 features
  POST /predict-direct  -- Manual form prediction (bypasses interview layer)
  GET  /models          -- List available Ollama models

Start:
  python main.py
    or
  uvicorn main:app --host 0.0.0.0 --port 5002 --reload
"""

import os
import sys
from pathlib import Path

# Load .env before anything else
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn
from contextlib import asynccontextmanager
import sys
# Force UTF-8 output on Windows to avoid cp1252 errors
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Local modules
from llm_client import call_ollama, extract_json, check_ollama_health, list_available_models, OLLAMA_MODEL
from ml_predictor import load_models, predict, get_metrics
from prompts import INTERVIEWER_SYSTEM_PROMPT, SCORING_SYSTEM_PROMPT, CRISIS_RESOURCES

# ─── APP SETUP ───────────────────────────────────────────────────────────────

_model_loaded = False

@asynccontextmanager
async def lifespan(app_):
    # ── Startup ──
    global _model_loaded
    print("\n" + "=" * 55)
    print("  MindBridge AI Backend Starting...")
    print("=" * 55)
    _model_loaded = load_models()
    ollama_status = check_ollama_health()
    print(f"  Ollama : {'Online' if ollama_status['available'] else 'Offline'}")
    print(f"  Model  : {OLLAMA_MODEL}")
    print(f"  DTC    : {'Loaded' if _model_loaded else 'Using fallback predictor'}")
    print("=" * 55)
    print("  Endpoints:")
    print("    GET  http://localhost:5002/health")
    print("    POST http://localhost:5002/interview")
    print("    POST http://localhost:5002/score")
    print("    POST http://localhost:5002/predict")
    print("    POST http://localhost:5002/predict-direct")
    print("    GET  http://localhost:5002/models")
    print("=" * 55 + "\n")
    yield
    # ── Shutdown (nothing to clean up) ──

app = FastAPI(
    title="MindBridge AI Backend",
    description="Empathy-First Mental Health Risk Prediction API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── REQUEST / RESPONSE MODELS ───────────────────────────────────────────────

class Message(BaseModel):
    role: str    # "user" | "assistant" | "system"
    content: str

class InterviewRequest(BaseModel):
    message: str                          = Field(..., description="User's latest message")
    conversation_history: List[Message]  = Field(default=[], description="Previous turns")
    model: Optional[str]                 = Field(None, description="Override Ollama model")

class ScoreRequest(BaseModel):
    conversation_history: List[Message]  = Field(..., description="Full conversation to score")
    empathy_map: Optional[Dict]          = Field(None, description="Accumulated empathy map")
    model: Optional[str]                 = Field(None, description="Override Ollama model")

class PredictRequest(BaseModel):
    age: float                          = Field(25,   ge=18, le=65)
    gender: str                         = Field("Male")
    employment_status: str              = Field("Employed")
    work_environment: str               = Field("On-site")
    mental_health_history: str          = Field("No")
    seeks_treatment: str                = Field("No")
    stress_level: float                 = Field(5,    ge=1,  le=10)
    sleep_hours: float                  = Field(7,    ge=2,  le=12)
    physical_activity_days: float       = Field(3,    ge=0,  le=7)
    depression_score: float             = Field(10,   ge=0,  le=30)
    anxiety_score: float                = Field(7,    ge=0,  le=21)
    social_support_score: float         = Field(50,   ge=0,  le=100)
    productivity_score: float           = Field(60,   ge=0,  le=100)

class DirectPredictRequest(PredictRequest):
    """Manual form prediction — same as PredictRequest, named for clarity."""
    pass


# ─── GET /health ─────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """
    System health check.
    Returns Ollama status, model availability, DTC load status.
    """
    ollama = check_ollama_health()
    models = list_available_models()
    metrics = get_metrics()

    return {
        "status":       "ok",
        "ollama":       ollama,
        "current_model": OLLAMA_MODEL,
        "available_models": models,
        "dtc_loaded":   _model_loaded,
        "dtc_metrics":  metrics,
        "version":      "2.0.0",
    }


# ─── GET /models ─────────────────────────────────────────────────────────────

@app.get("/models")
async def get_models():
    """Return all Ollama models available for switching."""
    return {
        "models":        list_available_models(),
        "current_model": OLLAMA_MODEL,
    }


# ─── POST /interview ─────────────────────────────────────────────────────────

@app.post("/interview")
async def interview(req: InterviewRequest):
    """
    Single Empathy Map interview turn.

    Takes user message + conversation history.
    Returns AI reply, updated empathy_map, crisis_detected, ready_to_score flags.
    """
    # Build conversation messages for LLM
    messages = []
    for m in req.conversation_history:
        messages.append({"role": m.role, "content": m.content})

    # Add the new user message
    messages.append({"role": "user", "content": req.message})

    print(f"\n📥 /interview | turn {len(req.conversation_history)//2 + 1} | model: {req.model or OLLAMA_MODEL}")

    result = call_ollama(
        system=INTERVIEWER_SYSTEM_PROMPT,
        messages=messages,
        model=req.model,
    )

    if not result["success"]:
        raise HTTPException(status_code=503, detail=f"Ollama error: {result['error']}")

    # Parse JSON response from LLM
    parsed = extract_json(result["text"])

    if not parsed:
        # Graceful fallback — LLM didn't return valid JSON
        parsed = {
            "reply": result["text"][:500] if result["text"] else "I'm here to listen. Can you tell me more about how you're feeling?",
            "empathy_map": {"says": [], "thinks": [], "does": [], "feels": []},
            "crisis_detected": False,
            "ready_to_score": False,
            "confidence_pct": 0,
        }

    # Safety check: keyword-level crisis detection as backup
    crisis_keywords = [
        "suicide", "kill myself", "end my life", "want to die",
        "kms", "drink bleach", "self harm", "cutting", "overdose",
        "sab khatam", "want to disappear", "khud ko khatam",
    ]
    msg_lower = req.message.lower()
    if any(kw in msg_lower for kw in crisis_keywords):
        parsed["crisis_detected"] = True

    response = {
        "success":        True,
        "reply":          parsed.get("reply", "I'm here. Tell me more."),
        "empathy_map":    parsed.get("empathy_map", {"says": [], "thinks": [], "does": [], "feels": []}),
        "crisis_detected": parsed.get("crisis_detected", False),
        "ready_to_score": parsed.get("ready_to_score", False),
        "confidence_pct": parsed.get("confidence_pct", 0),
        "model_used":     result["model"],
        "elapsed_ms":     result["elapsed_ms"],
    }

    if response["crisis_detected"]:
        response["crisis_resources"] = CRISIS_RESOURCES

    return response


# ─── POST /score ─────────────────────────────────────────────────────────────

@app.post("/score")
async def score(req: ScoreRequest):
    """
    Convert full conversation history → 13 clinical feature JSON.
    This is LLM Call #2 (the Clinical Scorer).
    """
    # Build the full conversation context for the scorer
    convo_text = "\n".join(
        f"{m.role.upper()}: {m.content}"
        for m in req.conversation_history
        if m.role in ("user", "assistant")
    )

    empathy_context = ""
    if req.empathy_map:
        empathy_context = f"\n\nACCUMULATED EMPATHY MAP:\n{str(req.empathy_map)}"

    prompt = f"""Please review the following mental health interview conversation and extract the 13 clinical scores.

CONVERSATION:
{convo_text}
{empathy_context}

Based on everything shared, output the 13 clinical features as JSON."""

    print(f"\n📥 /score | {len(req.conversation_history)} messages | model: {req.model or OLLAMA_MODEL}")

    result = call_ollama(
        prompt=prompt,
        system=SCORING_SYSTEM_PROMPT,
        model=req.model,
    )

    if not result["success"]:
        raise HTTPException(status_code=503, detail=f"Ollama error: {result['error']}")

    features = extract_json(result["text"])

    if not features:
        raise HTTPException(
            status_code=422,
            detail="Scorer LLM did not return valid JSON. Try again or use manual form."
        )

    # Validate & clamp ranges
    features = _validate_features(features)

    return {
        "success":    True,
        "features":   features,
        "model_used": result["model"],
        "elapsed_ms": result["elapsed_ms"],
    }


# ─── POST /predict ───────────────────────────────────────────────────────────

@app.post("/predict")
async def predict_route(req: PredictRequest):
    """
    Run DTC prediction from 13 clinical features.
    Used after /score in the interview flow.
    """
    features = req.model_dump()
    print(f"\n📥 /predict | dep={features.get('depression_score')} anx={features.get('anxiety_score')}")

    result = predict(features)
    return {"success": True, **result}


# ─── POST /predict-direct ────────────────────────────────────────────────────

@app.post("/predict-direct")
async def predict_direct(req: DirectPredictRequest):
    """
    Manual form path — skip interview, run DTC directly.
    Mirrors the original mindbridge-ai.jsx form flow.
    """
    features = req.model_dump()
    print(f"\n📥 /predict-direct | dep={features.get('depression_score')} anx={features.get('anxiety_score')}")

    result = predict(features)
    return {"success": True, **result}


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _validate_features(f: dict) -> dict:
    """Clamp all numeric features to valid ranges."""
    clamps = {
        "age":                   (18, 65, 25),
        "stress_level":          (1, 10, 5),
        "sleep_hours":           (2, 12, 7),
        "physical_activity_days": (0, 7, 3),
        "depression_score":      (0, 30, 10),
        "anxiety_score":         (0, 21, 7),
        "social_support_score":  (0, 100, 50),
        "productivity_score":    (0, 100, 60),
    }
    valid_genders     = {"Male", "Female", "Non-binary"}
    valid_employment  = {"Employed", "Student", "Self-employed", "Unemployed"}
    valid_work_env    = {"On-site", "Remote", "Hybrid"}
    valid_yn          = {"Yes", "No"}

    for col, (mn, mx, default) in clamps.items():
        try:
            f[col] = max(mn, min(mx, float(f.get(col, default))))
        except (TypeError, ValueError):
            f[col] = default

    if f.get("gender") not in valid_genders:
        f["gender"] = "Male"
    if f.get("employment_status") not in valid_employment:
        f["employment_status"] = "Employed"
    if f.get("work_environment") not in valid_work_env:
        f["work_environment"] = "On-site"
    if f.get("mental_health_history") not in valid_yn:
        f["mental_health_history"] = "No"
    if f.get("seeks_treatment") not in valid_yn:
        f["seeks_treatment"] = "No"

    return f


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5002, reload=True)
