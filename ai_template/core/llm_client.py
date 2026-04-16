#!/usr/bin/env python3
"""
llm_client.py — Universal Multi-Backend LLM Interface
======================================================
Template version of the FraudSense llm_client.py.
Supports Groq (multi-key rotation), Ollama (local), and Google Gemini.

Features:
  - Multi-backend: groq | ollama | gemini (switch via env var or per-call param)
  - Groq: N API keys loaded from groq_key.txt, randomly rotated per call
  - Rate-limit aware: 429/401 on one key → auto-retry with next key
  - Full AI logging: every call → JSON file + Markdown file in logs/
  - Naming: 0000_20260322_001500_key1_modelname.{json,md}
  - Strips <think>...</think> reasoning blocks (for Qwen3, DeepSeek-R1, etc.)
  - Multi-turn conversation support (messages list)

Endpoints exposed (called internally, not HTTP):
  call_llm(prompt, system, backend, model, messages) → dict
  extract_json_from_response(text) → dict
  get_key_pool_status() → dict
  check_ollama_available() → dict

# [CUSTOMIZE] Section markers show what to change for your domain.

Usage:
  from core.llm_client import call_llm, extract_json_from_response
  result = call_llm("Analyze this data", system="You are an analyst...", backend="groq")
  print(result["text"])
"""

import json
import os
import re
import time
import random
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from typing import Optional

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
#
# [CUSTOMIZE] Change AGENT_BACKEND env var or edit defaults here.
#   "groq"   = Groq cloud (fast, free tier, multi-key) ← recommended
#   "ollama" = Local Ollama (private, needs ollama serve running)
#   "gemini" = Google Gemini (free tier, needs GEMINI_API_KEY)

BACKEND = os.environ.get("AGENT_BACKEND", "groq")

# ─── Ollama config ────────────────────────────────────────────────────────────
OLLAMA_URL   = os.environ.get("OLLAMA_URL", "http://localhost:11434")
# [CUSTOMIZE] Change to whichever model you have pulled in Ollama
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")

# ─── Gemini config ────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL   = "gemini-1.5-flash"   # free tier model

# ─── Groq config ─────────────────────────────────────────────────────────────
# [CUSTOMIZE] Change to preferred model. Options on Groq free tier (April 2026):
#   "llama-3.3-70b-versatile"  — fast, great for tool use
#   "qwen/qwen3-32b"           — best reasoning quality (used in FundTrace)
#   "mixtral-8x7b-32768"       — good for long context
GROQ_MODEL    = os.environ.get("GROQ_MODEL", "qwen/qwen3-32b")

# Token limits — adjust based on your model and use case
MAX_TOKENS    = 8192   # qwen3-32b supports long context
TEMPERATURE   = 0.2    # low = deterministic; higher = creative

# ─── AI LOGGING DIRECTORIES ───────────────────────────────────────────────────
# All LLM calls are logged here. Never deletes old logs — append only.
_BASE_DIR     = Path(__file__).parent.parent        # ai_template/ root
_LOG_DIR      = _BASE_DIR / "logs"
_LOG_JSON_DIR = _LOG_DIR / "json"                   # machine-readable logs
_LOG_MD_DIR   = _LOG_DIR / "md"                     # human-readable logs


def _ensure_log_dirs():
    """Create log directories if they do not exist."""
    _LOG_JSON_DIR.mkdir(parents=True, exist_ok=True)
    _LOG_MD_DIR.mkdir(parents=True, exist_ok=True)


def _get_seq() -> int:
    """
    Return next global log sequence number.
    Reads all existing log files to find the current max, then returns max+1.
    Sequence is monotonically increasing across both json/ and md/ folders.
    """
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
    """Make model name filesystem-safe by replacing non-alphanumeric chars."""
    return re.sub(r"[^a-zA-Z0-9\-]", "-", model)[:40]


def _strip_think_tags(text: str) -> str:
    """
    Remove <think>...</think> chain-of-thought blocks emitted by reasoning models
    (Qwen3, DeepSeek-R1, etc.). Keeps only the actual answer after the think block.

    NOTE: The raw text (including think blocks) is still logged to the JSON log
    so you can inspect the model's reasoning if needed.
    """
    import re as _re
    cleaned = _re.sub(r'<think>[\s\S]*?</think>', '', text, flags=_re.IGNORECASE)
    cleaned = _re.sub(r'</?think>', '', cleaned, flags=_re.IGNORECASE)
    return cleaned.strip()


def _write_ai_log(seq: int, key_num: int, model: str, messages_sent: list,
                  response_text: str, success: bool, error: str,
                  elapsed_ms: int, backend: str, tokens: dict = None):
    """
    Write comprehensive AI call log to both JSON and Markdown files.

    JSON log: machine-readable, contains full request + response + metadata.
    MD log:   human-readable, formatted for easy review.

    Args:
        seq:            Global sequence number (monotonically increasing)
        key_num:        Which API key was used (1-indexed; 0 for non-Groq)
        model:          Model name string
        messages_sent:  Full list of message dicts sent to the LLM
        response_text:  Raw LLM response (before think-tag stripping)
        success:        Whether the call succeeded
        error:          Error message if not success
        elapsed_ms:     Time taken in milliseconds
        backend:        "groq" | "ollama" | "gemini"
        tokens:         Dict with prompt/completion/total token counts (or None)
    """
    try:
        _ensure_log_dirs()
        now       = datetime.now()
        ts        = now.strftime("%Y%m%d_%H%M%S")
        model_safe = _safe_model_name(model)
        base_name  = f"{seq:04d}_{ts}_key{key_num}_{model_safe}"

        # Extract message parts for log summary
        system_msg     = next((m["content"] for m in messages_sent if m.get("role") == "system"), "")
        user_msgs      = [m for m in messages_sent if m.get("role") == "user"]
        assistant_msgs = [m for m in messages_sent if m.get("role") == "assistant"]

        # ── JSON LOG ──────────────────────────────────────────────────────────
        log_entry = {
            "seq":          seq,
            "timestamp":    now.isoformat(),
            "backend":      backend,
            "model":        model,
            "key_number":   key_num,
            "success":      success,
            "elapsed_ms":   elapsed_ms,
            "error":        error or None,
            "tokens":       tokens,    # {prompt: N, completion: N, total: N} or None
            "messages_sent": messages_sent,
            "response":     response_text,
            "meta": {
                "system_prompt_chars": len(system_msg),
                "user_messages":       len(user_msgs),
                "history_turns":       len(assistant_msgs),
                "response_chars":      len(response_text),
                "total_messages":      len(messages_sent),
                "tokens_per_second": (
                    round(tokens["completion"] / (elapsed_ms / 1000), 1)
                    if tokens and tokens.get("completion") and elapsed_ms > 0
                    else None
                )
            }
        }
        json_path = _LOG_JSON_DIR / f"{base_name}.json"
        json_path.write_text(json.dumps(log_entry, indent=2, ensure_ascii=False), encoding="utf-8")

        # ── MARKDOWN LOG ──────────────────────────────────────────────────────
        status_icon = "✅" if success else "❌"
        tokens_line = ""
        if tokens:
            tps = log_entry["meta"]["tokens_per_second"]
            tokens_line = (
                f"**Tokens:** prompt={tokens.get('prompt','?')} "
                f"/ completion={tokens.get('completion','?')} "
                f"/ total={tokens.get('total','?')}"
                + (f" | **Speed:** {tps} tok/s" if tps else "")
                + "\n"
            )
        md = f"""# {status_icon} AI Call #{seq:04d}

**Date/Time:** {now.strftime('%Y-%m-%d %H:%M:%S')}
**Backend:** {backend} | **Model:** `{model}` | **Key:** #{key_num}
**Status:** {"SUCCESS" if success else f"FAILED — {error}"}
**Elapsed:** {elapsed_ms}ms | **Response length:** {len(response_text)} chars
{tokens_line}
---

## 🔧 System Prompt

```
{system_msg[:3000]}{"..." if len(system_msg) > 3000 else ""}
```

---

## 💬 Conversation History ({len(assistant_msgs)} prior turns)

"""
        for i, m in enumerate(messages_sent):
            role    = m.get("role", "?")
            content = m.get("content", "")
            if role == "system":
                continue
            icon  = "👤" if role == "user" else "🤖"
            label = "USER" if role == "user" else "ASSISTANT"
            md += f"### {icon} {label} (message {i})\n\n"
            md += f"```\n{content[:2000]}{'...' if len(content) > 2000 else ''}\n```\n\n"

        md += f"""---

## 🤖 AI Response

```
{response_text[:5000]}{"..." if len(response_text) > 5000 else ""}
```

---

## 📊 Metadata

| Field | Value |
|-------|-------|
| Sequence | #{seq:04d} |
| Timestamp | {now.isoformat()} |
| Model | {model} |
| Key # | {key_num} |
| Elapsed | {elapsed_ms}ms |
| Prompt tokens | {tokens.get('prompt', 'N/A') if tokens else 'N/A'} |
| Completion tokens | {tokens.get('completion', 'N/A') if tokens else 'N/A'} |
| Total tokens | {tokens.get('total', 'N/A') if tokens else 'N/A'} |
| Tokens/sec | {log_entry['meta']['tokens_per_second'] or 'N/A'} |
| System prompt chars | {len(system_msg)} |
| User messages | {len(user_msgs)} |
| History turns | {len(assistant_msgs)} |
| Response chars | {len(response_text)} |
| Success | {success} |
"""
        md_path = _LOG_MD_DIR / f"{base_name}.md"
        md_path.write_text(md, encoding="utf-8")

    except Exception as log_err:
        print(f"   ⚠️  AI log write failed: {log_err}")


# ─── MULTI-KEY POOL ───────────────────────────────────────────────────────────

def _load_all_groq_keys() -> list:
    """
    Load ALL Groq API keys from three sources (in priority order):
      1. groq_key.txt  — one key per line (supports multiple keys)
      2. .env file     — GROQ_API_KEY= line
      3. Environment   — GROQ_API_KEY system env var

    Returns a deduplicated list of valid key strings.
    Each key should start with 'gsk_'.
    Get free keys at: https://console.groq.com
    """
    keys     = []
    base_dir = _BASE_DIR

    # Source 1: groq_key.txt (one key per line — best for multiple keys)
    key_file = base_dir / "groq_key.txt"
    if key_file.exists():
        for line in key_file.read_text(encoding="utf-8").splitlines():
            k = line.strip()
            if k and not k.startswith("#") and k.startswith("gsk_") and k not in keys:
                keys.append(k)

    # Source 2: .env file
    env_file = base_dir / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("GROQ_API_KEY="):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
                if k and k.startswith("gsk_") and k not in keys:
                    keys.append(k)

    # Source 3: System environment variable
    env_key = os.environ.get("GROQ_API_KEY", "").strip()
    if env_key and env_key not in keys:
        keys.append(env_key)

    return keys


# Load all keys at module startup (once)
_ALL_GROQ_KEYS = _load_all_groq_keys()
GROQ_API_KEY   = _ALL_GROQ_KEYS[0] if _ALL_GROQ_KEYS else ""  # compat alias


def _pick_groq_key() -> tuple:
    """
    Pick a random Groq API key from the pool for load distribution.
    Returns (key_index_1based, api_key_string).
    Random (not round-robin) because it distributes better across concurrent calls.
    """
    if not _ALL_GROQ_KEYS:
        return (0, "")
    idx = random.randint(0, len(_ALL_GROQ_KEYS) - 1)
    return (idx + 1, _ALL_GROQ_KEYS[idx])


def _get_next_key(exclude_idx: int) -> tuple:
    """
    Get a different Groq key, excluding the one that just failed.
    Used for automatic failover on rate limit or auth errors.
    """
    available = [(i, k) for i, k in enumerate(_ALL_GROQ_KEYS) if i != (exclude_idx - 1)]
    if not available:
        return (exclude_idx, _ALL_GROQ_KEYS[exclude_idx - 1] if _ALL_GROQ_KEYS else "")
    i, k = random.choice(available)
    return (i + 1, k)


# ─── OLLAMA BACKEND ───────────────────────────────────────────────────────────

def call_ollama(prompt: str, system: str = None, model_override: Optional[str] = None,
                messages: list = None) -> dict:
    """
    Call a local Ollama instance.

    Requires: `ollama serve` running on localhost:11434 (or configured OLLAMA_URL).
    Pull models with: `ollama pull llama3.2:3b`

    Supports both single-turn (prompt) and multi-turn (messages) conversations.
    Logs every call to logs/json/ and logs/md/.

    Returns:
        dict with keys: success (bool), text (str), model (str),
                        backend ("ollama"), log_seq (int), tokens (dict|None),
                        error (str, only on failure)
    """
    model = model_override or OLLAMA_MODEL
    seq   = _get_seq()

    # Build message list — same structure as Groq for compatibility
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
        "model":   model,
        "messages": msg_list,
        "stream":  False,
        "options": {"temperature": TEMPERATURE, "num_predict": MAX_TOKENS}
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data     = json.loads(resp.read().decode("utf-8"))
            text     = data.get("message", {}).get("content", "")
            elapsed_ms = int((time.time() - t0) * 1000)

            # Ollama token counts
            tokens = None
            p_tok  = data.get("prompt_eval_count")
            c_tok  = data.get("eval_count")
            if p_tok is not None:
                tokens = {"prompt": p_tok, "completion": c_tok,
                          "total": (p_tok or 0) + (c_tok or 0)}

            _write_ai_log(seq, 0, model, msg_list, text, True, "", elapsed_ms, "ollama", tokens=tokens)
            tok_info = f" | {tokens['total']} tok" if tokens else ""
            print(f"   🦙 Ollama | model: {model} | {elapsed_ms}ms{tok_info} | log #{seq:04d}")
            return {"success": True, "text": text, "model": model,
                    "backend": "ollama", "log_seq": seq, "tokens": tokens}

    except urllib.error.URLError:
        elapsed_ms = int((time.time() - t0) * 1000)
        err = f"Ollama not reachable at {OLLAMA_URL}. Is 'ollama serve' running?"
        _write_ai_log(seq, 0, model, msg_list, "", False, err, elapsed_ms, "ollama")
        print(f"   ❌ Ollama unreachable | log #{seq:04d}")
        return {"success": False, "error": err, "text": "", "backend": "ollama"}
    except Exception as e:
        elapsed_ms = int((time.time() - t0) * 1000)
        err = str(e)
        _write_ai_log(seq, 0, model, msg_list, "", False, err, elapsed_ms, "ollama")
        print(f"   ❌ Ollama error: {err[:80]} | log #{seq:04d}")
        return {"success": False, "error": err, "text": "", "backend": "ollama"}


# ─── GROQ BACKEND (multi-key rotation + retry + full logging) ─────────────────

def call_groq(prompt: str, system: str = None, model_override: Optional[str] = None,
              messages: list = None) -> dict:
    """
    Call Groq API with automatic key rotation and retry logic.

    Key rotation strategy:
      - Pick a random key from the pool for each call (random = better load distribution)
      - If that key gets a 429 (rate limit) → immediately try a different key
      - Retry up to min(len(keys), 3) times before giving up
      - Log every attempt (success and failure)

    Returns:
        dict with keys: success (bool), text (str), model (str), backend ("groq"),
                        key_used (int), log_seq (int), tokens (dict|None),
                        error (str, only on failure)
    """
    if not _ALL_GROQ_KEYS:
        return {
            "success": False,
            "error": "No Groq API keys found. Add keys to groq_key.txt (one per line).",
            "text": "", "backend": "groq"
        }

    try:
        from groq import Groq
    except ImportError:
        return {
            "success": False,
            "error": "groq SDK not installed. Run: pip install groq",
            "text": "", "backend": "groq"
        }

    model = model_override or GROQ_MODEL
    seq   = _get_seq()

    def _build_msg_list() -> list:
        """Build final messages list with system prompt always at position 0."""
        msg_list = []
        if system:
            msg_list.append({"role": "system", "content": system})
        if messages:
            for m in messages:
                if m.get("role") != "system":
                    msg_list.append(m)
        elif prompt:
            msg_list.append({"role": "user", "content": prompt})
        return msg_list

    # ── Key rotation retry loop ───────────────────────────────────────────────
    key_idx, key = _pick_groq_key()
    tried_keys   = {key_idx}
    last_error   = ""

    for attempt in range(min(len(_ALL_GROQ_KEYS), 3)):
        msg_list = _build_msg_list()
        t0 = time.time()
        try:
            client     = Groq(api_key=key)
            completion = client.chat.completions.create(
                model=model,
                messages=msg_list,
                temperature=TEMPERATURE,
                max_completion_tokens=MAX_TOKENS,
                stream=False,
            )
            raw_text   = completion.choices[0].message.content or ""
            text       = _strip_think_tags(raw_text)   # clean think blocks for reasoning models
            elapsed_ms = int((time.time() - t0) * 1000)

            # Extract token usage
            tokens = None
            if hasattr(completion, "usage") and completion.usage:
                tokens = {
                    "prompt":     completion.usage.prompt_tokens,
                    "completion": completion.usage.completion_tokens,
                    "total":      completion.usage.total_tokens
                }

            # Log raw_text so reasoning chain is preserved in logs
            _write_ai_log(seq, key_idx, model, msg_list, raw_text, True, "", elapsed_ms, "groq", tokens=tokens)
            tok_info = f" | {tokens['total']} tok ({tokens['completion']} out)" if tokens else ""
            print(f"   🔑 Groq key #{key_idx} | model: {model} | {elapsed_ms}ms{tok_info} | log #{seq:04d}")
            return {
                "success": True, "text": text, "model": model,
                "backend": "groq", "key_used": key_idx, "log_seq": seq, "tokens": tokens
            }

        except Exception as e:
            elapsed_ms = int((time.time() - t0) * 1000)
            err_str    = str(e)
            last_error = err_str

            # Rate limit → try next key
            if "429" in err_str or "rate_limit" in err_str.lower():
                print(f"   ⚠️  Key #{key_idx} rate limited. Trying another key...")
                _write_ai_log(seq, key_idx, model, msg_list, "", False,
                              f"Rate limited: {err_str}", elapsed_ms, "groq")
                key_idx, key = _get_next_key(key_idx)
                while key_idx in tried_keys and len(tried_keys) < len(_ALL_GROQ_KEYS):
                    key_idx, key = _get_next_key(key_idx)
                tried_keys.add(key_idx)
                continue
            else:
                _write_ai_log(seq, key_idx, model, msg_list, "", False, err_str, elapsed_ms, "groq")
                return {
                    "success": False, "error": f"Groq error: {err_str}",
                    "text": "", "backend": "groq", "key_used": key_idx
                }

    # All keys exhausted
    _write_ai_log(seq, key_idx, model, _build_msg_list(), "", False,
                  f"All keys exhausted: {last_error}", 0, "groq")
    return {"success": False, "error": f"All Groq keys rate limited: {last_error}",
            "text": "", "backend": "groq"}


# ─── GEMINI BACKEND ───────────────────────────────────────────────────────────

def call_gemini(prompt: str, system: str = None) -> dict:
    """
    Call Google Gemini API (free tier — gemini-1.5-flash).

    Requires: GEMINI_API_KEY environment variable.
    Note: Gemini does not natively support multi-turn messages in this simple wrapper.
    For multi-turn with Gemini, use the official google-generativeai SDK instead.

    Returns:
        dict with keys: success (bool), text (str), model (str),
                        backend ("gemini"), error (str, only on failure)
    """
    if not GEMINI_API_KEY:
        return {"success": False, "error": "GEMINI_API_KEY not set in .env or environment",
                "text": "", "backend": "gemini"}

    full_prompt = (system + "\n\n" + prompt) if system else prompt
    payload = json.dumps({
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {"temperature": TEMPERATURE, "maxOutputTokens": MAX_TOKENS}
    }).encode("utf-8")

    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}")
    req = urllib.request.Request(url, data=payload,
                                  headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"success": True, "text": text, "model": GEMINI_MODEL, "backend": "gemini"}
    except Exception as e:
        return {"success": False, "error": str(e), "text": "", "backend": "gemini"}


# ─── MAIN INTERFACE (use this in your code) ──────────────────────────────────

def call_llm(prompt: str, system: str = None, backend: Optional[str] = None,
             model: Optional[str] = None, messages: list = None) -> dict:
    """
    Primary interface — routes to the configured backend.

    This is the ONLY function your agent/graph code should call.
    Never call call_groq(), call_ollama(), or call_gemini() directly.

    Args:
        prompt:   User prompt (required for single-turn; ignored if messages provided)
        system:   System prompt (optional but strongly recommended)
        backend:  Override backend for this call ("groq"|"ollama"|"gemini"|None=use default)
        model:    Override model for this call (None = use backend default)
        messages: Full conversation history list for multi-turn use

    Returns:
        dict: {
            "success": bool,
            "text":    str,    # clean response (think blocks stripped)
            "model":   str,
            "backend": str,
            "error":   str,    # only on failure
            "tokens":  dict,   # {prompt, completion, total} or None
            "log_seq": int,    # which log file number this call is
        }

    Example:
        result = call_llm(
            "Analyze account FT-001 for fraud",
            system="You are a fraud investigator. Respond in JSON.",
            backend="groq",
            model="qwen/qwen3-32b"
        )
        if result["success"]:
            print(result["text"])
    """
    use_backend = (backend or BACKEND).lower()
    if use_backend == "groq":
        return call_groq(prompt, system, model_override=model, messages=messages)
    elif use_backend == "gemini":
        return call_gemini(prompt, system)
    else:   # ollama or any unrecognized backend defaults to ollama
        return call_ollama(prompt, system, model_override=model, messages=messages)


def extract_json_from_response(text: str) -> dict:
    """
    Robustly extract a JSON object from an LLM response.

    Tries multiple strategies in order:
      1. Direct json.loads(text)  — clean JSON responses
      2. Extract from ```json ... ``` markdown fences
      3. Extract from { ... } with regex
    Returns empty dict {} if all strategies fail.

    Use this instead of json.loads() for all LLM response parsing.
    """
    if not text:
        return {}
    # Strategy 1: clean JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    # Strategy 2: markdown code fence
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    # Strategy 3: largest JSON-like substring
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {}


def check_ollama_available() -> dict:
    """
    Check if Ollama is running and the target model is available.

    Returns:
        dict: {available: bool, models: list, target_model: str, model_ready: bool}
    """
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data        = json.loads(resp.read().decode("utf-8"))
            models      = [m["name"] for m in data.get("models", [])]
            model_ready = any(OLLAMA_MODEL.split(":")[0] in m for m in models)
            return {"available": True, "models": models,
                    "target_model": OLLAMA_MODEL, "model_ready": model_ready}
    except Exception as e:
        return {"available": False, "error": str(e)}


def get_key_pool_status() -> dict:
    """
    Return info about the loaded Groq API key pool.
    Keys are masked for safe display (first 8 + last 4 chars shown).

    Returns:
        dict: {total_keys: int, keys: list[str], model: str, backend: str}
    """
    return {
        "total_keys": len(_ALL_GROQ_KEYS),
        "keys":  [f"key#{i+1}: {k[:8]}...{k[-4:]}" for i, k in enumerate(_ALL_GROQ_KEYS)],
        "model": GROQ_MODEL,
        "backend": BACKEND
    }


# ─── STANDALONE TEST ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Run as a standalone test: python core/llm_client.py
    Tests the key pool status and makes one test LLM call.
    """
    print(f"Backend: {BACKEND}")
    status = get_key_pool_status()
    print(f"Groq keys loaded: {status['total_keys']}")
    for k in status["keys"]:
        print(f"  {k}")
    print(f"Model: {status['model']}")

    if _ALL_GROQ_KEYS:
        print("\nSending test prompt to Groq...")
        result = call_llm(
            'Respond ONLY with this exact JSON: {"status": "ok", "message": "Agent ready"}',
            system="You are a JSON-only responder. Output ONLY valid JSON, nothing else.",
            backend="groq"
        )
        print(json.dumps(result, indent=2))
