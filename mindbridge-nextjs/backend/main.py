"""
main.py -- Mental Health Risk Detection FastAPI Backend
HTTP server exposing the Empathy Agent + DTC prediction pipeline.

Endpoints:
  GET  /health          -- System status (Ollama + model + available models)
  POST /interview       -- Single Empathy Map interview turn (auto-triggers scoring)
  POST /score           -- Convert full conversation to 13 clinical features
  POST /predict         -- DTC prediction from 13 features
  POST /predict-direct  -- Manual form prediction (bypasses interview layer)
  GET  /models          -- List available Ollama models
  POST /hybrid-turn     -- Single structured hybrid interview turn (auto-triggers scoring)
  POST /hybrid-analyze  -- Personalized empathy analysis
  POST /hybrid-score    -- Extract 13 features + run DTC from hybrid interview
  POST /retrain         -- Trigger model retraining
  GET  /retrain-status  -- Poll retrain progress
  POST /set-model       -- Switch Ollama model at runtime

Auto-trigger behavior:
  /interview:   When LLM returns ready_to_score=True, immediately chains to
                SCORING_SYSTEM_PROMPT + DTC. Returns prediction in same response.
  /hybrid-turn: When LLM returns all_factors_complete=True, immediately chains
                to HYBRID_SCORER_PROMPT + DTC. Returns prediction in same response.

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
import asyncio
import subprocess
import threading
import time as _time

# Force UTF-8 output on Windows to avoid cp1252 errors
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Local modules
import llm_client
from llm_client import call_ollama, extract_json, check_ollama_health, list_available_models
from ml_predictor import load_models, predict, get_metrics
from prompts import (
    INTERVIEWER_SYSTEM_PROMPT,
    SCORING_SYSTEM_PROMPT,
    CRISIS_RESOURCES,
    HYBRID_INTERVIEWER_PROMPT,
    HYBRID_ANALYZER_PROMPT,
    HYBRID_SCORER_PROMPT,
)
import database as db     # MongoDB + Redis — optional/graceful-degradation

# ─── APP SETUP ───────────────────────────────────────────────────────────────

_model_loaded = False

@asynccontextmanager
async def lifespan(app_):
    # ── Startup ──
    global _model_loaded
    print("\n" + "=" * 55)
    print("  Mental Health Risk Detection Backend Starting...")
    print("=" * 55)
    _model_loaded = load_models()
    ollama_status = check_ollama_health()
    print(f"  Ollama : {'Online' if ollama_status['available'] else 'Offline'}")
    print(f"  Model  : {llm_client.OLLAMA_MODEL}")
    print(f"  DTC    : {'Loaded' if _model_loaded else 'Using fallback predictor'}")
    print("=" * 55)
    print("  Endpoints:")
    print("    GET  http://localhost:5002/health")
    print("    POST http://localhost:5002/interview      (auto-scores when ready)")
    print("    POST http://localhost:5002/score")
    print("    POST http://localhost:5002/predict")
    print("    POST http://localhost:5002/predict-direct")
    print("    GET  http://localhost:5002/models")
    print("    POST http://localhost:5002/hybrid-turn    (auto-scores when complete)")
    print("    POST http://localhost:5002/hybrid-analyze")
    print("    POST http://localhost:5002/hybrid-score")
    print("=" * 55 + "\n")
    yield
    # ── Shutdown (nothing to clean up) ──

app = FastAPI(
    title="Mental Health Risk Detection Backend",
    description="Empathy-First Mental Health Risk Prediction API",
    version="2.1.0",
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
    message: str                         = Field(..., description="User's latest message")
    conversation_history: List[Message]  = Field(default=[], description="Previous turns")
    model: Optional[str]                 = Field(None, description="Override Ollama model")

class ScoreRequest(BaseModel):
    conversation_history: List[Message]  = Field(..., description="Full conversation to score")
    empathy_map: Optional[Dict]          = Field(None, description="Accumulated empathy map")
    model: Optional[str]                 = Field(None, description="Override Ollama model")

class PredictRequest(BaseModel):
    age:                    float = Field(25,  ge=18, le=65)
    gender:                 str   = Field("Male")
    employment_status:      str   = Field("Employed")
    work_environment:       str   = Field("On-site")
    mental_health_history:  str   = Field("No")
    seeks_treatment:        str   = Field("No")
    stress_level:           float = Field(5,   ge=1,  le=10)
    sleep_hours:            float = Field(7,   ge=2,  le=12)
    physical_activity_days: float = Field(3,   ge=0,  le=7)
    depression_score:       float = Field(10,  ge=0,  le=30)
    anxiety_score:          float = Field(7,   ge=0,  le=21)
    social_support_score:   float = Field(50,  ge=0,  le=100)
    productivity_score:     float = Field(60,  ge=0,  le=100)

class DirectPredictRequest(PredictRequest):
    """Manual form prediction — same as PredictRequest, named for clarity."""
    pass


# ─── INTERNAL HELPERS ────────────────────────────────────────────────────────

# Crisis keyword list used as a hard-safety backup regardless of LLM output
_CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die",
    "kms", "drink bleach", "self harm", "cutting", "overdose",
    "sab khatam", "want to disappear", "khud ko khatam",
    "end it all", "no point living", "better off dead",
]


def _keyword_crisis_check(text: str) -> bool:
    """Hard-coded crisis keyword check as safety backup layer."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in _CRISIS_KEYWORDS)


def _run_scorer(
    conversation_history: List[Message],
    empathy_map: Optional[Dict],
    model: Optional[str],
    endpoint_label: str,
) -> dict:
    """
    Internal helper: run the SCORING LLM call + DTC prediction chain.

    Called when ready_to_score or all_factors_complete fires.
    Returns: {"features": {...}, "prediction": {...}, "scorer_elapsed_ms": int}
    """
    convo_text = "\n".join(
        f"{m.role.upper()}: {m.content}"
        for m in conversation_history
        if m.role in ("user", "assistant")
    )

    emp_ctx = ""
    if empathy_map:
        emp_ctx = f"\n\nACCUMULATED EMPATHY MAP:\n{str(empathy_map)}"

    score_prompt = (
        f"Please review the following mental health interview conversation "
        f"and extract the 13 clinical scores.\n\n"
        f"CONVERSATION:\n{convo_text}{emp_ctx}\n\n"
        f"Based on everything shared, output the 13 clinical features as JSON."
    )

    print(f"\n🔗 Auto-trigger: scoring from {endpoint_label}")

    scorer_result = call_ollama(
        prompt=score_prompt,
        system=SCORING_SYSTEM_PROMPT,
        model=model,
        context_state={
            "endpoint":   f"{endpoint_label}→auto-score",
            "phase":      "scoring",
            "crisis_flag": False,
        },
    )

    if not scorer_result["success"]:
        return {
            "features":          None,
            "prediction":        None,
            "scorer_elapsed_ms": scorer_result.get("elapsed_ms", 0),
            "scorer_error":      scorer_result.get("error", "Scorer LLM failed"),
        }

    features = extract_json(scorer_result["text"])
    if not features:
        return {
            "features":          None,
            "prediction":        None,
            "scorer_elapsed_ms": scorer_result["elapsed_ms"],
            "scorer_error":      "Scorer returned invalid JSON",
        }

    features = _validate_features(features)
    prediction = predict(features)

    return {
        "features":          features,
        "prediction":        prediction,
        "scorer_elapsed_ms": scorer_result["elapsed_ms"],
        "scorer_error":      None,
    }


# ─── GET /health ─────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """
    System health check.
    Returns Ollama status, model availability, DTC load status, DB status.
    """
    ollama  = check_ollama_health()
    models  = list_available_models()
    metrics = get_metrics()

    return {
        "status":           "ok",
        "ollama":           ollama,
        "current_model":    llm_client.OLLAMA_MODEL,
        "available_models": models,
        "dtc_loaded":       _model_loaded,
        "dtc_metrics":      metrics,
        "version":          "2.1.0",
        "mongodb":          db.mongo_status(),
        "redis":            db.redis_status(),
    }


# ─── GET /sessions ───────────────────────────────────────────────────────────

@app.get("/sessions")
async def get_sessions(limit: int = 50, skip: int = 0):
    """
    Return persisted sessions from MongoDB (newest first).
    Falls back to empty list if MongoDB is not running.
    """
    return {
        "sessions": db.get_sessions(limit=limit, skip=skip),
        "stats":    db.get_session_stats(),
        "source":   "mongodb" if db._mongo_ok else "localStorage-only",
    }


@app.delete("/sessions")
async def clear_sessions():
    """Delete all session documents from MongoDB."""
    if not db._mongo_ok:
        return {"success": False, "message": "MongoDB not connected"}
    try:
        result = db._mongo_db.sessions.delete_many({})
        return {"success": True, "deleted": result.deleted_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a single session by its ID (and its conversation if stored)."""
    deleted = db.delete_session_by_id(session_id)
    # Also delete conversation record if exists
    if db._mongo_ok:
        try:
            db._mongo_db.conversations.delete_one({"session_id": session_id})
        except Exception:
            pass
    return {"success": deleted, "session_id": session_id}


class RenameRequest(BaseModel):
    name: str = Field(..., description="New display name / snippet for the session")


@app.patch("/sessions/{session_id}")
async def rename_session(session_id: str, req: RenameRequest):
    """Rename/relabel a session (updates the snippet field)."""
    updated = db.update_session(session_id, {"snippet": req.name, "renamed": True})
    return {"success": updated, "session_id": session_id, "new_name": req.name}


# ─── POST /conversations/save ─────────────────────────────────────────────────

class ConversationSaveRequest(BaseModel):
    session_id:  str           = Field(..., description="Unique session ID")
    messages:    List[Dict]    = Field(default=[], description="Full message history [{role, content}]")
    empathy_map: Optional[Dict] = Field(None)
    source:      Optional[str]  = Field(None)
    snippet:     Optional[str]  = Field(None)
    user_name:   Optional[str]  = Field(None)


@app.post("/conversations/save")
async def save_conversation(req: ConversationSaveRequest):
    """
    Persist the full conversation message history for a session to MongoDB.
    Called by the frontend when a chat session completes.
    """
    meta = {
        "source":    req.source,
        "snippet":   req.snippet,
        "user_name": req.user_name,
    }
    success = db.save_conversation(
        session_id=req.session_id,
        messages=req.messages,
        empathy_map=req.empathy_map,
        meta={k: v for k, v in meta.items() if v is not None},
    )
    return {"success": success, "session_id": req.session_id}


@app.get("/conversations/{session_id}")
async def get_conversation(session_id: str):
    """Retrieve stored conversation messages + empathy map for a session."""
    data = db.get_conversation(session_id)
    if not data:
        return {"found": False, "session_id": session_id, "messages": [], "empathy_map": {}}
    return {"found": True, **data}


# ─── POST /cache/flush ───────────────────────────────────────────────────────

@app.post("/cache/flush")
async def flush_cache():
    """Flush all Redis-cached LLM responses."""
    count = db.cache_flush()
    return {"success": True, "flushed": count, "redis_ok": db._redis_ok}



# ─── GET /models ─────────────────────────────────────────────────────────────

@app.get("/models")
async def get_models():
    """Return all Ollama models available for switching."""
    return {
        "models":        list_available_models(),
        "current_model": llm_client.OLLAMA_MODEL,
    }


# ─── POST /interview ─────────────────────────────────────────────────────────

@app.post("/interview")
async def interview(req: InterviewRequest):
    """
    Single Empathy Map interview turn.

    Takes user message + conversation history.
    Returns AI reply, updated empathy_map, crisis_detected, ready_to_score flags.

    Auto-trigger: If ready_to_score = True (and crisis_detected = False),
    immediately chains to SCORING_SYSTEM_PROMPT + DTC and returns prediction
    in the same response — no extra frontend round-trip needed.
    """
    # Assemble conversation messages for LLM
    messages = [{"role": m.role, "content": m.content} for m in req.conversation_history]
    messages.append({"role": "user", "content": req.message})

    # Hard crisis safety check on raw user input
    user_crisis = _keyword_crisis_check(req.message)

    turn_num = len(req.conversation_history) // 2 + 1
    print(f"\n📥 /interview | turn {turn_num} | model: {req.model or llm_client.OLLAMA_MODEL}")

    result = call_ollama(
        system=INTERVIEWER_SYSTEM_PROMPT,
        messages=messages,
        model=req.model,
        context_state={
            "endpoint":      "/interview",
            "phase":         "interview",
            "turn_number":   turn_num,
            "crisis_flag":   user_crisis,
        },
    )

    if not result["success"]:
        raise HTTPException(status_code=503, detail=f"Ollama error: {result['error']}")

    # Parse JSON response from LLM
    parsed = extract_json(result["text"])

    if not parsed:
        # Graceful fallback — LLM didn't return valid JSON
        parsed = {
            "reply":          result["text"][:500] if result["text"] else "I'm here to listen. Can you tell me more about how you're feeling?",
            "empathy_map":    {"says": [], "thinks": [], "does": [], "feels": []},
            "crisis_detected": user_crisis,
            "ready_to_score": False,
            "confidence_pct": 0,
        }

    # Hard override: if keyword check fired, force crisis_detected = True
    if user_crisis:
        parsed["crisis_detected"] = True

    # Crisis NEVER allows ready_to_score — enforce this unconditionally
    if parsed.get("crisis_detected"):
        parsed["ready_to_score"] = False

    crisis_detected  = parsed.get("crisis_detected", False)
    ready_to_score   = parsed.get("ready_to_score", False)
    empathy_map      = parsed.get("empathy_map", {"says": [], "thinks": [], "does": [], "feels": []})
    user_name        = parsed.get("user_name") or None   # name the user shared, or None

    response = {
        "success":         True,
        "reply":           parsed.get("reply", "I'm here. Tell me more."),
        "user_name":       user_name,
        "empathy_map":     empathy_map,
        "crisis_detected": crisis_detected,
        "ready_to_score":  ready_to_score,
        "confidence_pct":  parsed.get("confidence_pct", 0),
        "model_used":      result["model"],
        "elapsed_ms":      result["elapsed_ms"],
        # Auto-trigger results will be added below if applicable
        "features":        None,
        "prediction":      None,
    }

    # Attach crisis resources if crisis detected
    if crisis_detected:
        response["crisis_resources"] = CRISIS_RESOURCES

    # ── AUTO-TRIGGER: Score + Predict when interview is complete ──────────────
    if ready_to_score and not crisis_detected:
        print(f"   ⚡ ready_to_score=True — auto-triggering scorer + DTC...")

        # Build full conversation including current turn for the scorer
        full_history = list(req.conversation_history) + [
            Message(role="user", content=req.message),
            Message(role="assistant", content=response["reply"]),
        ]

        scorer = _run_scorer(full_history, empathy_map, req.model, "/interview")
        response["features"]          = scorer["features"]
        response["prediction"]        = scorer["prediction"]
        response["scorer_elapsed_ms"] = scorer["scorer_elapsed_ms"]

        if scorer["scorer_error"]:
            response["scorer_warning"] = scorer["scorer_error"]

        # ── Persist to MongoDB (fire-and-forget, no blocking) ──
        if scorer["prediction"]:
            db.save_session({
                "source":     "empathy-chat",
                "risk":       scorer["prediction"].get("risk"),
                "confidence": scorer["prediction"].get("confidence"),
                "crisis":     crisis_detected,
                "user_name":  user_name,
                "features":   scorer["features"],
                "prediction": scorer["prediction"],
                "empathy_map": empathy_map,
                "turn_count": turn_num,
                "timestamp":  int(__import__("time").time() * 1000),
                "snippet":    req.message[:120],
            })

    # ── Log crisis event to MongoDB ──
    if crisis_detected:
        db.save_crisis_log(user_name, turn_num, req.message[:200])

    return response



# ─── POST /score ─────────────────────────────────────────────────────────────

@app.post("/score")
async def score(req: ScoreRequest):
    """
    Convert full conversation history → 13 clinical feature JSON.
    This is LLM Call #2 (the Clinical Scorer).
    Can be called manually; also auto-called by /interview when ready_to_score fires.
    """
    convo_text = "\n".join(
        f"{m.role.upper()}: {m.content}"
        for m in req.conversation_history
        if m.role in ("user", "assistant")
    )

    emp_ctx = ""
    if req.empathy_map:
        emp_ctx = f"\n\nACCUMULATED EMPATHY MAP:\n{str(req.empathy_map)}"

    prompt = (
        f"Please review the following mental health interview conversation "
        f"and extract the 13 clinical scores.\n\n"
        f"CONVERSATION:\n{convo_text}{emp_ctx}\n\n"
        f"Based on everything shared, output the 13 clinical features as JSON."
    )

    print(f"\n📥 /score | {len(req.conversation_history)} messages | model: {req.model or llm_client.OLLAMA_MODEL}")

    result = call_ollama(
        prompt=prompt,
        system=SCORING_SYSTEM_PROMPT,
        model=req.model,
        context_state={
            "endpoint": "/score",
            "phase":    "scoring",
        },
    )

    if not result["success"]:
        raise HTTPException(status_code=503, detail=f"Ollama error: {result['error']}")

    features = extract_json(result["text"])

    if not features:
        raise HTTPException(
            status_code=422,
            detail="Scorer LLM did not return valid JSON. Try again or use manual form."
        )

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
    Mirrors the original form flow.
    """
    features = req.model_dump()
    print(f"\n📥 /predict-direct | dep={features.get('depression_score')} anx={features.get('anxiety_score')}")

    result = predict(features)
    return {"success": True, **result}


# ─── HYBRID ENDPOINTS ────────────────────────────────────────────────────────

class HybridTurnRequest(BaseModel):
    message:              str          = Field(..., description="User message")
    conversation_history: List[Message] = Field(default=[])
    empathy_map:          Optional[Dict] = Field(None)
    model:                Optional[str]  = Field(None)

class HybridAnalyzeRequest(BaseModel):
    conversation_history: List[Message] = Field(...)
    empathy_map:          Optional[Dict] = Field(None)
    model:                Optional[str]  = Field(None)

class HybridScoreRequest(BaseModel):
    conversation_history: List[Message] = Field(...)
    empathy_map:          Optional[Dict] = Field(None)
    model:                Optional[str]  = Field(None)


@app.post("/hybrid-turn")
async def hybrid_turn(req: HybridTurnRequest):
    """
    Single structured hybrid interview turn (Demographics → 5-Whys clinical).

    Auto-trigger: If all_factors_complete = True (and crisis_detected = False),
    immediately chains to HYBRID_SCORER_PROMPT + DTC and returns prediction
    in the same response — no extra frontend round-trip needed.
    """
    messages = [{"role": m.role, "content": m.content} for m in req.conversation_history]
    messages.append({"role": "user", "content": req.message})

    # Hard crisis safety check on raw user input
    user_crisis = _keyword_crisis_check(req.message)

    turn_num = len(req.conversation_history) // 2 + 1
    print(f"\n📥 /hybrid-turn | turn {turn_num}")

    result = call_ollama(
        system=HYBRID_INTERVIEWER_PROMPT,
        messages=messages,
        model=req.model,
        context_state={
            "endpoint":    "/hybrid-turn",
            "phase":       "hybrid",
            "turn_number": turn_num,
            "crisis_flag": user_crisis,
        },
    )

    if not result["success"]:
        raise HTTPException(status_code=503, detail=f"Ollama error: {result['error']}")

    parsed = extract_json(result["text"])

    if not parsed:
        parsed = {
            "reply":         result["text"][:500] or "Tell me more.",
            "phase":         "demographics",
            "current_factor": None,
            "why_depth":     0,
            "factor_progress": {
                k: False for k in
                ["productivity", "anxiety", "social_support", "depression", "exercise", "stress", "sleep"]
            },
            "demographics_complete": False,
            "empathy_map":   {"says": [], "thinks": [], "does": [], "feels": []},
            "key_insight":   None,
            "crisis_detected": user_crisis,
            "all_factors_complete": False,
        }

    # Hard override: if keyword check fired, force crisis_detected = True
    if user_crisis:
        parsed["crisis_detected"] = True

    # Crisis NEVER allows all_factors_complete — enforce this unconditionally
    if parsed.get("crisis_detected"):
        parsed["all_factors_complete"] = False

    crisis_detected       = parsed.get("crisis_detected", False)
    all_factors_complete  = parsed.get("all_factors_complete", False)
    empathy_map           = parsed.get("empathy_map", {"says": [], "thinks": [], "does": [], "feels": []})
    user_name             = parsed.get("user_name") or None   # name the user shared, or None

    response = {
        "success":              True,
        "reply":                parsed.get("reply", "Tell me more."),
        "user_name":            user_name,
        "phase":                parsed.get("phase", "demographics"),
        "current_factor":       parsed.get("current_factor"),
        "why_depth":            parsed.get("why_depth", 0),
        "factor_progress":      parsed.get("factor_progress", {}),
        "demographics_complete": parsed.get("demographics_complete", False),
        "empathy_map":          empathy_map,
        "key_insight":          parsed.get("key_insight"),
        "crisis_detected":      crisis_detected,
        "all_factors_complete": all_factors_complete,
        "model_used":           result["model"],
        "elapsed_ms":           result["elapsed_ms"],
        # Auto-trigger results will be added below if applicable
        "features":             None,
        "prediction":           None,
    }

    # Attach crisis resources if crisis detected
    if crisis_detected:
        response["crisis_resources"] = CRISIS_RESOURCES

    # ── AUTO-TRIGGER: Score + Predict when all factors are complete ───────────
    if all_factors_complete and not crisis_detected:
        print(f"   ⚡ all_factors_complete=True — auto-triggering hybrid scorer + DTC...")

        # Build full conversation including current turn for the scorer
        full_history = list(req.conversation_history) + [
            Message(role="user", content=req.message),
            Message(role="assistant", content=response["reply"]),
        ]

        scorer = _run_scorer(full_history, empathy_map, req.model, "/hybrid-turn")
        response["features"]          = scorer["features"]
        response["prediction"]        = scorer["prediction"]
        response["scorer_elapsed_ms"] = scorer["scorer_elapsed_ms"]

        if scorer["scorer_error"]:
            response["scorer_warning"] = scorer["scorer_error"]

        # ── Persist to MongoDB ──
        if scorer["prediction"]:
            db.save_session({
                "source":     "hybrid",
                "risk":       scorer["prediction"].get("risk"),
                "confidence": scorer["prediction"].get("confidence"),
                "crisis":     crisis_detected,
                "user_name":  user_name,
                "features":   scorer["features"],
                "prediction": scorer["prediction"],
                "empathy_map": empathy_map,
                "turn_count": turn_num,
                "timestamp":  int(__import__("time").time() * 1000),
                "snippet":    req.message[:120],
            })

    # ── Log crisis event ──
    if crisis_detected:
        db.save_crisis_log(user_name, turn_num, req.message[:200])

    return response



@app.post("/hybrid-analyze")
async def hybrid_analyze(req: HybridAnalyzeRequest):
    """Personalized empathy analysis after all factors are complete."""
    convo   = "\n".join(f"{m.role.upper()}: {m.content}" for m in req.conversation_history if m.role in ("user", "assistant"))
    emp_ctx = f"\n\nEMPATHY MAP:\n{req.empathy_map}" if req.empathy_map else ""
    prompt  = f"Interview transcript:\n{convo}{emp_ctx}\n\nWrite the personalized response now."

    print(f"\n📥 /hybrid-analyze | {len(req.conversation_history)} msgs")

    result = call_ollama(
        prompt=prompt,
        system=HYBRID_ANALYZER_PROMPT,
        model=req.model,
        context_state={
            "endpoint": "/hybrid-analyze",
            "phase":    "analysis",
        },
    )

    if not result["success"]:
        raise HTTPException(status_code=503, detail=f"Ollama error: {result['error']}")

    return {
        "success":    True,
        "analysis":   result["text"],
        "model_used": result["model"],
        "elapsed_ms": result["elapsed_ms"],
    }


@app.post("/hybrid-score")
async def hybrid_score(req: HybridScoreRequest):
    """
    Extract 13 clinical features + run DTC prediction from hybrid interview.
    Can be called manually; also auto-called by /hybrid-turn when all_factors_complete fires.
    """
    convo   = "\n".join(f"{m.role.upper()}: {m.content}" for m in req.conversation_history if m.role in ("user", "assistant"))
    emp_ctx = f"\n\nEMPATHY MAP:\n{req.empathy_map}" if req.empathy_map else ""
    prompt  = f"Interview transcript:\n{convo}{emp_ctx}\n\nExtract the 13 clinical scores as JSON."

    print(f"\n📥 /hybrid-score | {len(req.conversation_history)} msgs")

    result = call_ollama(
        prompt=prompt,
        system=HYBRID_SCORER_PROMPT,
        model=req.model,
        context_state={
            "endpoint": "/hybrid-score",
            "phase":    "scoring",
        },
    )

    if not result["success"]:
        raise HTTPException(status_code=503, detail=f"Ollama error: {result['error']}")

    features = extract_json(result["text"])

    if not features:
        raise HTTPException(status_code=422, detail="Scorer returned invalid JSON.")

    features = _validate_features(features)
    pred     = predict(features)

    return {
        "success":    True,
        "features":   features,
        "prediction": pred,
        "model_used": result["model"],
        "elapsed_ms": result["elapsed_ms"],
    }


# ─── POST /retrain ───────────────────────────────────────────────────────────

_retrain_state = {
    "running":     False,
    "log":         [],
    "started_at":  None,
    "finished_at": None,
    "success":     None,
    "metrics":     {},
}


def _run_training_script(script_path: str):
    """Run training script in a background thread, auto-installing deps first."""
    global _retrain_state
    _retrain_state["log"] = []
    _retrain_state["started_at"] = _time.strftime("%H:%M:%S")

    import sys as _sys
    python_exe = _sys.executable

    try:
        # ── Step 1: auto-install dependencies ───────────────────────────────
        _retrain_state["log"].append("[pip] Checking / installing required packages...")
        print("[retrain] Installing dependencies...")

        dep_packages = ["gradio", "colorama", "scikit-learn", "pandas", "numpy", "joblib"]

        pip_proc = subprocess.run(
            [python_exe, "-m", "pip", "install", "--quiet", "--upgrade"] + dep_packages,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if pip_proc.returncode == 0:
            _retrain_state["log"].append("[pip] All dependencies ready.")
        else:
            for l in pip_proc.stdout.strip().splitlines()[-10:]:
                _retrain_state["log"].append(f"[pip] {l}")
            _retrain_state["log"].append(f"[pip] Warning: some installs may have failed (code {pip_proc.returncode})")

        print("[retrain] Dependencies done. Starting training script...")
        _retrain_state["log"].append("[train] Launching mental_health_ml_system.py ...")

        # ── Step 2: run the actual training script ───────────────────────────
        proc = subprocess.Popen(
            [python_exe, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=str(Path(script_path).parent),
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        for line in proc.stdout:
            line = line.rstrip()
            _retrain_state["log"].append(line)
            print(f"[retrain] {line}")

        proc.wait()
        _retrain_state["success"]     = proc.returncode == 0
        _retrain_state["finished_at"] = _time.strftime("%H:%M:%S")

        if _retrain_state["success"]:
            load_models()
            _retrain_state["metrics"] = get_metrics()
            _retrain_state["log"].append("[System] Model reloaded successfully.")
        else:
            _retrain_state["log"].append(f"[System] Script exited with code {proc.returncode}")

    except Exception as e:
        _retrain_state["log"].append(f"[System ERROR] {e}")
        _retrain_state["success"]     = False
        _retrain_state["finished_at"] = _time.strftime("%H:%M:%S")
    finally:
        _retrain_state["running"] = False


@app.post("/retrain")
async def retrain():
    """
    Trigger model retraining by running mental_health_ml_system.py.
    Returns immediately; poll /retrain-status for progress.
    """
    global _retrain_state
    if _retrain_state["running"]:
        return {"success": False, "message": "Retrain already in progress", "state": _retrain_state}

    script_path = Path(__file__).parent.parent / "mental_health_ml_system.py"
    if not script_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Training script not found at: {script_path}"
        )

    _retrain_state["running"] = True
    _retrain_state["success"] = None
    _retrain_state["log"]     = ["[System] Starting retrain..."]
    _retrain_state["metrics"] = {}

    t = threading.Thread(target=_run_training_script, args=(str(script_path),), daemon=True)
    t.start()

    return {"success": True, "message": "Retrain started", "script": str(script_path)}


@app.get("/retrain-status")
async def retrain_status():
    """Poll retrain progress."""
    return {
        "running":     _retrain_state["running"],
        "success":     _retrain_state["success"],
        "log":         _retrain_state["log"],
        "started_at":  _retrain_state["started_at"],
        "finished_at": _retrain_state["finished_at"],
        "metrics":     _retrain_state["metrics"],
        "log_count":   len(_retrain_state["log"]),
    }


# ─── POST /set-model ─────────────────────────────────────────────────────────

class SetModelRequest(BaseModel):
    model: str = Field(..., description="Ollama model name to switch to, e.g. 'deepseek-r1:7b'")

@app.post("/set-model")
async def set_model(req: SetModelRequest):
    """Switch the active Ollama model at runtime (no restart needed)."""
    previous = llm_client.OLLAMA_MODEL
    llm_client.OLLAMA_MODEL = req.model
    return {
        "success":        True,
        "previous_model": previous,
        "current_model":  llm_client.OLLAMA_MODEL,
        "message":        f"Model switched from '{previous}' → '{req.model}'",
    }


# ─── FEATURE VALIDATION ──────────────────────────────────────────────────────

def _validate_features(f: dict) -> dict:
    """Clamp all numeric features to valid DTC input ranges."""
    clamps = {
        "age":                    (18, 65, 25),
        "stress_level":           (1, 10, 5),
        "sleep_hours":            (2, 12, 7),
        "physical_activity_days": (0, 7, 3),
        "depression_score":       (0, 30, 10),
        "anxiety_score":          (0, 21, 7),
        "social_support_score":   (0, 100, 50),
        "productivity_score":     (0, 100, 60),
    }
    valid_genders    = {"Male", "Female", "Non-binary"}
    valid_employment = {"Employed", "Student", "Self-employed", "Unemployed"}
    valid_work_env   = {"On-site", "Remote", "Hybrid"}
    valid_yn         = {"Yes", "No"}

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
