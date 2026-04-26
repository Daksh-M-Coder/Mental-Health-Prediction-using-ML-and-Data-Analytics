"""
llm_client.py — Mental Health Risk Detection: Ollama LLM Client
================================================================
Multi-model Ollama client with:
  - Easy model switching (deepseek-r1, llama3, mistral, etc.)
  - Multi-turn conversation support (messages list)
  - Robust JSON extraction from LLM responses (handles markdown fences)
  - Comprehensive dual-format logging (JSON machine-truth + MD human-truth)
    for future RLHF / fine-tuning / safety auditing

Log schema captures:
  - Full input: system_prompt, messages, parameters
  - Full output: raw_response (incl. <think> tags), clean_response
  - Context state: endpoint, phase, crisis_flag, why_depth, empathy_map_snapshot
  - Metadata: seq, timestamp, model, elapsed_ms, success/error

Add a new model: just change OLLAMA_MODEL in .env or pass model= per call.
"""

import json
import re
import time
import os
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from typing import Optional

# ─── CONFIG ──────────────────────────────────────────────────────────────────

OLLAMA_URL   = os.environ.get("OLLAMA_URL",   "http://localhost:11434")

# ── Active model — uncomment ONE line to switch ──────────────────────────────
# Local models (fast, private, no internet)
# OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "deepseek-r1:7b")
# OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "deepseek-r1:14b")
# OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
# OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
# OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral:7b")
# OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "granite3.1-moe:3b")

# Cloud models via Ollama (require Ollama cloud access)
# OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:31b-cloud")
# OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gpt-oss:20b-cloud")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gpt-oss:120b-cloud")
# OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "nemotron-3-super:cloud")
# OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3.5:cloud")
# OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3.5:397b-cloud")
# OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "deepseek-v3.2:cloud")
# OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "glm-5.1:cloud")
# OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "cogito-2.1:671b-cloud")
# ─────────────────────────────────────────────────────────────────────────────

TEMPERATURE  = float(os.environ.get("OLLAMA_TEMPERATURE", "0.3"))
MAX_TOKENS   = int(os.environ.get("OLLAMA_MAX_TOKENS",    "2048"))

# ─── LOGGING DIRECTORIES ─────────────────────────────────────────────────────

_BASE_DIR     = Path(__file__).parent
_LOG_DIR      = _BASE_DIR / "logs"
_LOG_JSON_DIR = _LOG_DIR / "json"
_LOG_MD_DIR   = _LOG_DIR / "md"


def _ensure_log_dirs():
    _LOG_JSON_DIR.mkdir(parents=True, exist_ok=True)
    _LOG_MD_DIR.mkdir(parents=True, exist_ok=True)


def _get_seq() -> int:
    """Scan both log dirs for the highest sequence number, return next."""
    _ensure_log_dirs()
    max_seq = -1
    for f in list(_LOG_JSON_DIR.glob("*.json")) + list(_LOG_MD_DIR.glob("*.md")):
        try:
            n = int(f.stem.split("_")[0])
            if n > max_seq:
                max_seq = n
        except (ValueError, IndexError):
            pass
    return max_seq + 1


def _safe_model_name(model: str) -> str:
    """Sanitize model name for use in filenames."""
    return re.sub(r"[^a-zA-Z0-9\-]", "-", model)[:40]


def _strip_think_tags(text: str) -> str:
    """Strip <think>...</think> reasoning blocks from DeepSeek-R1 and similar models."""
    cleaned = re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE)
    cleaned = re.sub(r'</?think>', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


# ─── DUAL-FORMAT LOG WRITER ──────────────────────────────────────────────────

def _write_log(
    seq:            int,
    model:          str,
    messages:       list,
    raw_response:   str,
    clean_response: str,
    success:        bool,
    error:          str,
    elapsed_ms:     int,
    context_state:  Optional[dict] = None,
):
    """
    Write a comprehensive dual-format AI call log.

    JSON file  → machine-readable, for RLHF / fine-tuning / dataset building
    MD file    → human-readable, for auditing / safety review / labelling

    context_state dict (all fields optional):
        endpoint           str   — which API endpoint was called
        phase              str   — "demographics" | "clinical" | None
        current_factor     str   — "sleep" | "anxiety" | ... | None
        why_depth          int   — 0-5, depth into current factor
        empathy_map_snapshot dict — current SAYS/THINKS/DOES/FEELS state
        crisis_flag        bool  — was crisis detected this turn
        ready_to_score     bool  — interview complete flag
        all_factors_complete bool — hybrid interview complete flag
    """
    try:
        _ensure_log_dirs()
        now        = datetime.now()
        ts         = now.strftime("%Y%m%d_%H%M%S")
        model_safe = _safe_model_name(model)
        base_name  = f"{seq:04d}_{ts}_{model_safe}"

        # Extract system prompt separately from message list for clarity
        system_prompt = next(
            (m["content"] for m in messages if m.get("role") == "system"), ""
        )
        convo_messages = [m for m in messages if m.get("role") != "system"]

        # ── JSON LOG (The Machine Truth) ──────────────────────────────────────
        log = {
            "seq":       seq,
            "timestamp": now.isoformat(),
            "model":     model,
            "backend":   "ollama",
            "success":   success,
            "elapsed_ms": elapsed_ms,
            "error":     error or None,

            # Full input payload — enough to replay the exact call
            "input": {
                "system_prompt": system_prompt,
                "messages":      convo_messages,
                "parameters": {
                    "temperature": TEMPERATURE,
                    "max_tokens":  MAX_TOKENS,
                },
            },

            # Full output payload — raw (with <think>) and clean
            "output": {
                "raw_response":   raw_response,
                "clean_response": clean_response,
            },

            # Context state — everything the system knew at this moment
            # This is what makes this log useful for RL training:
            # State (context_state) + Action (clean_response) = one training sample
            "context_state": context_state or {},
        }

        (_LOG_JSON_DIR / f"{base_name}.json").write_text(
            json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # ── MARKDOWN LOG (The Human Truth) ───────────────────────────────────
        status = "✅" if success else "❌"
        ctx    = context_state or {}

        # Build context state table rows
        ctx_rows = []
        if ctx.get("endpoint"):
            ctx_rows.append(f"| Endpoint | `{ctx['endpoint']}` |")
        if ctx.get("phase"):
            factor = ctx.get("current_factor") or ""
            ctx_rows.append(f"| Phase | `{ctx['phase']}`{' (' + factor + ')' if factor else ''} |")
        if ctx.get("why_depth") is not None:
            ctx_rows.append(f"| Why Depth | {ctx['why_depth']} / 5 |")
        crisis_val = ctx.get("crisis_flag", False)
        ctx_rows.append(f"| Crisis Detected | {'🚨 **TRUE**' if crisis_val else 'False'} |")
        if "ready_to_score" in ctx:
            ctx_rows.append(f"| Ready to Score | {ctx['ready_to_score']} |")
        if "all_factors_complete" in ctx:
            ctx_rows.append(f"| All Factors Complete | {ctx['all_factors_complete']} |")

        ctx_table = ""
        if ctx_rows:
            ctx_table = "\n## 📊 Context State\n| Field | Value |\n|-------|-------|\n"
            ctx_table += "\n".join(ctx_rows)

        # Build empathy map section if snapshot present
        emp_section = ""
        emp = ctx.get("empathy_map_snapshot")
        if emp:
            emp_section = "\n## 🗺️ Empathy Map Snapshot\n"
            for quadrant in ("says", "thinks", "does", "feels"):
                items = emp.get(quadrant, [])
                if items:
                    emp_section += f"**{quadrant.upper()}:** {' · '.join(items[:5])}\n"

        # Build conversation turns
        convo_md = ""
        for i, m in enumerate(convo_messages, 1):
            icon  = "👤" if m["role"] == "user" else "🤖"
            label = f"{icon} {m['role'].upper()} (Turn {i})"
            convo_md += f"\n### {label}\n```\n{m['content'][:2000]}\n```\n"

        md = f"""# {status} AI Call #{seq:04d}

**Date:** {now.strftime('%Y-%m-%d %H:%M:%S')} | **Model:** `{model}` | **Duration:** {elapsed_ms}ms
**Status:** {"SUCCESS" if success else f"FAILED — {error}"}

---

## 🔧 System Prompt
```
{system_prompt[:3000]}
```

---

## 💬 Conversation History
{convo_md if convo_md else "_No conversation messages._"}

---

## 🤖 AI Response
**Raw output (with think tags if any):**
```
{raw_response[:4000]}
```

**Clean response shown to user:**
```
{clean_response[:4000]}
```
{ctx_table}
{emp_section}
---

## 📈 Technical Stats
| Field | Value |
|-------|-------|
| Sequence | #{seq:04d} |
| Model | `{model}` |
| Elapsed | {elapsed_ms}ms |
| Success | {success} |
"""

        (_LOG_MD_DIR / f"{base_name}.md").write_text(md, encoding="utf-8")

    except Exception as e:
        print(f"   ⚠️  Log write failed: {e}")


# ─── CORE CALL ───────────────────────────────────────────────────────────────

def call_ollama(
    prompt:        Optional[str]  = None,
    system:        Optional[str]  = None,
    messages:      Optional[list] = None,
    model:         Optional[str]  = None,
    context_state: Optional[dict] = None,
) -> dict:
    """
    Call Ollama with full multi-turn conversation support.

    Args:
        prompt:        Single user message (used if messages not provided)
        system:        System prompt (prepended to messages)
        messages:      Full conversation history [{role, content}, ...]
        model:         Override model (e.g. "llama3.2:3b", "mistral:7b")
                       Default: OLLAMA_MODEL from env
        context_state: Optional dict capturing the system state at this call:
                       {endpoint, phase, current_factor, why_depth,
                        empathy_map_snapshot, crisis_flag, ready_to_score, ...}
                       Written to both JSON and MD logs for audit/RL use.

    Returns:
        {
          "success":    bool,
          "text":       str,   # clean response (think tags stripped)
          "raw":        str,   # original response (includes think blocks)
          "model":      str,
          "elapsed_ms": int,
          "error":      str    # only on failure
        }
    """
    use_model = model or OLLAMA_MODEL
    seq       = _get_seq()

    # Build message list
    msg_list = []
    if system:
        msg_list.append({"role": "system", "content": system})
    if messages:
        for m in messages:
            if m.get("role") != "system":
                msg_list.append(m)
    elif prompt:
        msg_list.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model":    use_model,
        "messages": msg_list,
        "stream":   False,
        "options":  {
            "temperature": TEMPERATURE,
            "num_predict": MAX_TOKENS,
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data       = json.loads(resp.read().decode("utf-8"))
            raw_text   = data.get("message", {}).get("content", "")
            clean_text = _strip_think_tags(raw_text)
            elapsed_ms = int((time.time() - t0) * 1000)

            _write_log(seq, use_model, msg_list, raw_text, clean_text,
                       True, "", elapsed_ms, context_state)
            print(f"   🦙 Ollama | {use_model} | {elapsed_ms}ms | log #{seq:04d}")

            return {
                "success":    True,
                "text":       clean_text,
                "raw":        raw_text,
                "model":      use_model,
                "elapsed_ms": elapsed_ms,
            }

    except urllib.error.URLError as e:
        elapsed_ms = int((time.time() - t0) * 1000)
        err = f"Ollama not reachable at {OLLAMA_URL}. Is 'ollama serve' running? Detail: {e}"
        _write_log(seq, use_model, msg_list, "", "", False, err, elapsed_ms, context_state)
        print(f"   ❌ Ollama unreachable | log #{seq:04d}")
        return {"success": False, "error": err, "text": "", "model": use_model, "elapsed_ms": elapsed_ms}

    except Exception as e:
        elapsed_ms = int((time.time() - t0) * 1000)
        err = str(e)
        _write_log(seq, use_model, msg_list, "", "", False, err, elapsed_ms, context_state)
        print(f"   ❌ Ollama error: {err[:100]} | log #{seq:04d}")
        return {"success": False, "error": err, "text": "", "model": use_model, "elapsed_ms": elapsed_ms}


# ─── JSON EXTRACTION ─────────────────────────────────────────────────────────

def extract_json(text: str) -> dict:
    """
    Robustly extract JSON from LLM response.

    Despite the strict JSON-only prompts, local models sometimes still add
    markdown fences or conversational filler. This function handles all cases:
      Strategy 1: Direct parse (ideal — model obeyed the prompt)
      Strategy 2: ```json ... ``` fence strip
      Strategy 3: Any {...} block anywhere in the text
      Strategy 4: Greedy last-resort — find outermost { ... }

    Returns {} on total failure.
    """
    if not text:
        return {}

    # Remove think tags before JSON extraction
    text = _strip_think_tags(text)

    # Strategy 1: direct — model output raw JSON as instructed
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Strategy 2: ```json ... ``` or ``` ... ```
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 3: first complete JSON object found anywhere
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Strategy 4: find the outermost braces (handles trailing text after })
    start = text.find('{')
    end   = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    return {}


# ─── HEALTH CHECK ────────────────────────────────────────────────────────────

def check_ollama_health() -> dict:
    """Check if Ollama is running and the configured model is available."""
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data        = json.loads(resp.read().decode("utf-8"))
            models      = [m["name"] for m in data.get("models", [])]
            target      = OLLAMA_MODEL
            model_ready = any(target.split(":")[0] in m for m in models)
            return {
                "available":    True,
                "models":       models,
                "target_model": target,
                "model_ready":  model_ready,
            }
    except Exception as e:
        return {"available": False, "error": str(e)}


def list_available_models() -> list:
    """Return list of all models pulled in Ollama."""
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []
