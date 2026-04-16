"""
llm_client.py — MindBridge Ollama LLM Client
=============================================
Multi-model Ollama client with:
  - Easy model switching (deepseek-r1, llama3, mistral, etc.)
  - Multi-turn conversation support (messages list)
  - Robust JSON extraction from LLM responses
  - Structured logging to logs/

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

# ─── CONFIG ─────────────────────────────────────────────────────────────────

OLLAMA_URL   = os.environ.get("OLLAMA_URL",   "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "deepseek-r1:7b")  # default model
TEMPERATURE  = float(os.environ.get("OLLAMA_TEMPERATURE", "0.3"))
MAX_TOKENS   = int(os.environ.get("OLLAMA_MAX_TOKENS",    "2048"))

# ─── LOGGING ─────────────────────────────────────────────────────────────────

_BASE_DIR     = Path(__file__).parent
_LOG_DIR      = _BASE_DIR / "logs"
_LOG_JSON_DIR = _LOG_DIR / "json"
_LOG_MD_DIR   = _LOG_DIR / "md"


def _ensure_log_dirs():
    _LOG_JSON_DIR.mkdir(parents=True, exist_ok=True)
    _LOG_MD_DIR.mkdir(parents=True, exist_ok=True)


def _get_seq() -> int:
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
    return re.sub(r"[^a-zA-Z0-9\-]", "-", model)[:40]


def _strip_think_tags(text: str) -> str:
    """Strip <think>...</think> reasoning blocks from DeepSeek-R1 and similar models."""
    cleaned = re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE)
    cleaned = re.sub(r'</?think>', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def _write_log(seq: int, model: str, messages: list, raw_response: str,
               clean_response: str, success: bool, error: str, elapsed_ms: int):
    """Write AI call log to JSON and MD files."""
    try:
        _ensure_log_dirs()
        now        = datetime.now()
        ts         = now.strftime("%Y%m%d_%H%M%S")
        model_safe = _safe_model_name(model)
        base_name  = f"{seq:04d}_{ts}_{model_safe}"

        log = {
            "seq":          seq,
            "timestamp":    now.isoformat(),
            "model":        model,
            "backend":      "ollama",
            "success":      success,
            "elapsed_ms":   elapsed_ms,
            "error":        error or None,
            "messages":     messages,
            "raw_response": raw_response,
            "clean_response": clean_response,
        }
        (_LOG_JSON_DIR / f"{base_name}.json").write_text(
            json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        status = "✅" if success else "❌"
        system_msg = next((m["content"] for m in messages if m.get("role") == "system"), "")
        md = f"""# {status} AI Call #{seq:04d}

**Time:** {now.strftime('%Y-%m-%d %H:%M:%S')}  
**Model:** `{model}` | **Elapsed:** {elapsed_ms}ms  
**Status:** {"SUCCESS" if success else f"FAILED — {error}"}

---

## System Prompt
```
{system_msg[:2000]}
```

## Conversation
"""
        for m in messages:
            if m.get("role") == "system":
                continue
            icon = "👤" if m["role"] == "user" else "🤖"
            md += f"\n### {icon} {m['role'].upper()}\n```\n{m['content'][:1500]}\n```\n"

        md += f"\n## Response\n```\n{clean_response[:3000]}\n```\n"
        (_LOG_MD_DIR / f"{base_name}.md").write_text(md, encoding="utf-8")

    except Exception as e:
        print(f"   ⚠️  Log write failed: {e}")


# ─── CORE CALL ───────────────────────────────────────────────────────────────

def call_ollama(
    prompt: Optional[str] = None,
    system: Optional[str] = None,
    messages: Optional[list] = None,
    model: Optional[str] = None,
) -> dict:
    """
    Call Ollama with full multi-turn conversation support.

    Args:
        prompt:   Single user message (used if messages not provided)
        system:   System prompt (prepended to messages)
        messages: Full conversation history [{role, content}, ...]
        model:    Override model (e.g. "llama3.2:3b", "mistral:7b")
                  Default: OLLAMA_MODEL from env

    Returns:
        {
          "success": bool,
          "text":    str,   # clean response (think tags stripped)
          "raw":     str,   # original response (includes think blocks)
          "model":   str,
          "elapsed_ms": int,
          "error":   str    # only on failure
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

            _write_log(seq, use_model, msg_list, raw_text, clean_text, True, "", elapsed_ms)
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
        _write_log(seq, use_model, msg_list, "", "", False, err, elapsed_ms)
        print(f"   ❌ Ollama unreachable | log #{seq:04d}")
        return {"success": False, "error": err, "text": "", "model": use_model}

    except Exception as e:
        elapsed_ms = int((time.time() - t0) * 1000)
        err = str(e)
        _write_log(seq, use_model, msg_list, "", "", False, err, elapsed_ms)
        print(f"   ❌ Ollama error: {err[:100]} | log #{seq:04d}")
        return {"success": False, "error": err, "text": "", "model": use_model}


# ─── JSON EXTRACTION ─────────────────────────────────────────────────────────

def extract_json(text: str) -> dict:
    """
    Robustly extract JSON from LLM response.
    Tries: direct parse → markdown fence → regex extraction.
    Returns {} on failure.
    """
    if not text:
        return {}

    # Strategy 1: direct
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Strategy 2: ```json ... ```
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 3: any JSON object
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
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
                "available":   True,
                "models":      models,
                "target_model": target,
                "model_ready": model_ready,
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
