#!/usr/bin/env python3
"""
agent.py — Universal AI Agent HTTP Server
==========================================
The HTTP server that exposes the LangGraph investigation pipeline as REST endpoints.
Cloned and generalized from FundTrace AI (FraudSense agent.py) — April 2026.

This file is the integration boundary between your frontend/backend and the AI.
Everything in graph.py / core / tools is internal implementation detail.
This file is the ONLY thing your Node.js / frontend / external system calls.

HTTP Endpoints:
  POST /analyze   — Full LangGraph Planner→Executor→Reflector investigation
  POST /chat      — Smart natural language Q&A over the database
  POST /forensic  — Deep forensic analysis of a single entity
  GET  /health    — System health check (backend, keys, model, db status)

Default port: 5002 (override with --port or AGENT_PORT env var)

# [CUSTOMIZE] markers show exactly what to change for your domain.

Start server:
  python agent.py --http --port 5002

Test:
  curl http://localhost:5002/health
  curl -X POST http://localhost:5002/analyze \\
       -H "Content-Type: application/json" \\
       -d '{"task": "Analyze entity ENT-001 for suspicious patterns"}'
"""

import sys
import json
import time
import argparse
import traceback
from pathlib import Path
from http.server  import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# ─── PATH SETUP — critical: must be before any local imports ──────────────────
sys.path.insert(0, str(Path(__file__).parent))

# ─── LOCAL IMPORTS ────────────────────────────────────────────────────────────
from graph               import run_analysis
from core.llm_client     import call_llm, extract_json_from_response, get_key_pool_status
from core.context_builder import load_relevant_episodes, load_entity_profile
from tools.db_tool        import run_query, DB_PATH

# ─── SERVER CONFIG ────────────────────────────────────────────────────────────
import os
DEFAULT_PORT = int(os.environ.get("AGENT_PORT", 5002))

# ─── PRE-LOAD HELPER ─────────────────────────────────────────────────────────

def preload_entity_data(entity_code: str = None, user_id: int = None) -> dict:
    """
    Pre-fetch entity context data before the LangGraph run.

    This is called at the start of /analyze to gather basic context
    that is injected into the initial agent state as 'preload'.
    It avoids the planner having to spend a step just fetching basics.

    # [CUSTOMIZE] Update the SQL queries to match your database schema.
    # Add/remove any pre-fetch queries relevant to your domain.

    Args:
        entity_code: The entity's unique code string (e.g., "ENT-001")
        user_id:     The entity's numeric database ID

    Returns:
        dict with pre-fetched context data (may be empty on failure)
    """
    preload = {}

    if entity_code:
        # [CUSTOMIZE] Fetch entity profile row
        res = run_query(
            f"SELECT * FROM entities WHERE UPPER(code) = UPPER('{entity_code}') LIMIT 1"
        )
        if res["success"] and res["rows"]:
            preload["entity_profile"] = res["rows"][0]

        # [CUSTOMIZE] Fetch recent activity for this entity
        res = run_query(
            f"""SELECT * FROM events
                WHERE entity_id = (SELECT id FROM entities WHERE UPPER(code) = UPPER('{entity_code}'))
                ORDER BY created_at DESC LIMIT 10"""
        )
        if res["success"]:
            preload["recent_events"] = res["rows"]

    elif user_id:
        # [CUSTOMIZE] Fetch by numeric ID if code not available
        res = run_query(f"SELECT * FROM entities WHERE id = {user_id} LIMIT 1")
        if res["success"] and res["rows"]:
            preload["entity_profile"] = res["rows"][0]
            entity_code = res["rows"][0].get("code", "")

    # Load memory context (past investigations of this entity)
    if entity_code:
        preload["past_episodes"] = load_relevant_episodes(entity_code, None, limit=2)
        preload["entity_memory"] = load_entity_profile(entity_code)

    return preload


# ─── SMART CHAT MODE ─────────────────────────────────────────────────────────

# [CUSTOMIZE] Update intent patterns to match your database schema and domain.
# Each pattern is: (list_of_keywords_to_match, sql_query_to_run)
# The first matching pattern wins.
CHAT_INTENT_PATTERNS = [
    # Pattern → SQL
    (["biggest", "largest", "highest", "top", "most"],
     "SELECT e.code, e.name, SUM(ev.amount) as total FROM events ev JOIN entities e ON ev.entity_id = e.id GROUP BY e.id ORDER BY total DESC LIMIT 10"),

    (["recent", "latest", "new", "last"],
     "SELECT ev.*, e.name, e.code FROM events ev JOIN entities e ON ev.entity_id = e.id ORDER BY ev.created_at DESC LIMIT 15"),

    (["flagged", "suspicious", "fraud", "alert"],
     "SELECT a.*, e.name, e.code FROM alerts a JOIN entities e ON a.entity_id = e.id ORDER BY a.risk_score DESC LIMIT 15"),

    (["dormant", "inactive", "sleeping"],
     "SELECT code, name, last_active FROM entities WHERE datetime('now') - datetime(last_active, 'unixepoch') > 2592000 ORDER BY last_active ASC LIMIT 15"),

    (["high risk", "critical", "score"],
     "SELECT a.*, e.code FROM alerts a JOIN entities e ON a.entity_id = e.id WHERE a.risk_score >= 70 ORDER BY a.risk_score DESC LIMIT 15"),

    (["channel", "type", "breakdown"],
     "SELECT type, COUNT(*) as count, SUM(amount) as total_amount FROM events GROUP BY type ORDER BY count DESC"),

    (["new", "created", "joined", "registered"],
     "SELECT code, name, created_at FROM entities ORDER BY created_at DESC LIMIT 15"),

    (["status", "frozen", "active", "blocked"],
     "SELECT status, COUNT(*) as count FROM entities GROUP BY status"),
]

# [CUSTOMIZE] Change this system prompt to match your domain's knowledge base.
CHAT_SYSTEM = """You are an intelligent analyst assistant.
You answer questions about data from the application database.
You have access to database query results provided in [DATABASE RESULTS] blocks.
Be concise, professional, and specific. Cite actual values from the data (IDs, amounts, dates).
If the data doesn't contain enough information to answer fully, say so clearly.
Never make up data that isn't in the provided results."""


def smart_chat(message: str, session_id: str = None, backend: str = None, model: str = None) -> dict:
    """
    Natural language Q&A over the database.

    Flow:
      1. Match message against CHAT_INTENT_PATTERNS using keyword detection
      2. If match found: run the associated SQL, inject results into LLM context
      3. Call LLM with enriched context to produce a natural language answer
      4. Return the answer + metadata about whether DB was queried

    # [CUSTOMIZE] Add more intent patterns to CHAT_INTENT_PATTERNS above.
    # [CUSTOMIZE] Update the fallback SQL query below to match your main data table.

    Args:
        message:    User's natural language question
        session_id: Optional session ID for logging
        backend:    LLM backend override
        model:      Model override

    Returns:
        dict: {success, response, db_query_used, matched_intent}
    """
    msg_lower = message.lower()

    # Detect intent and run matching SQL
    db_results_text = ""
    db_query_used   = False
    matched_intent  = None

    for keywords, sql in CHAT_INTENT_PATTERNS:
        if any(kw in msg_lower for kw in keywords):
            res = run_query(sql)
            if res["success"] and res["rows"]:
                db_results_text = (
                    f"\n[DATABASE RESULTS]\n"
                    f"Query matched {len(res['rows'])} records:\n"
                    f"{json.dumps(res['rows'], indent=2, default=str)[:3000]}\n"
                )
                db_query_used  = True
                matched_intent = keywords[0]
            break

    # Fallback: if no pattern matched, run a general recent events query
    if not db_results_text:
        res = run_query("SELECT ev.*, e.name FROM events ev JOIN entities e ON ev.entity_id = e.id ORDER BY ev.created_at DESC LIMIT 10")
        if res["success"] and res["rows"]:
            db_results_text = (
                f"\n[DATABASE RESULTS — Recent Events]\n"
                f"{json.dumps(res['rows'], indent=2, default=str)[:2000]}\n"
            )

    # Build enriched prompt
    enriched_message = message
    if db_results_text:
        enriched_message = message + "\n" + db_results_text

    result = call_llm(
        prompt=enriched_message,
        system=CHAT_SYSTEM,
        backend=backend,
        model=model
    )

    if result.get("success"):
        return {
            "success":        True,
            "response":       result["text"],
            "db_query_used":  db_query_used,
            "matched_intent": matched_intent
        }
    else:
        return {
            "success": False,
            "error":   result.get("error", "LLM call failed"),
            "response": "I encountered an error processing your request. Please try again."
        }


# ─── FORENSIC ANALYSIS MODE ───────────────────────────────────────────────────

# [CUSTOMIZE] Update this system prompt to describe your forensic report structure.
FORENSIC_SYSTEM = """You are a senior forensic analyst producing a comprehensive entity investigation report.
Structure your report with these sections:
  1. Entity Overview — profile, status, activity summary
  2. Activity Analysis — volume, patterns, counterparties
  3. Anomalous Patterns — what stands out as unusual
  4. Risk Assessment — overall risk level with specific evidence
  5. Recommended Actions — concrete next steps

Write in professional, precise language. Cite specific IDs, amounts, and dates from the data.
Be thorough but not repetitive."""


def forensic_analyze(entity_code: str, backend: str = None, model: str = None) -> dict:
    """
    Deep forensic analysis of a single entity.

    Unlike the LangGraph pipeline (which is iterative), forensic mode:
    1. Pre-computes a comprehensive evidence package (all available data)
    2. Sends it all to the LLM in one structured prompt
    3. Returns a full markdown forensic report

    This is better for scheduled deep-dives than real-time alert response.

    # [CUSTOMIZE] Update the SQL queries below to pull relevant data from YOUR schema.

    Args:
        entity_code: The entity to analyze (e.g., "ENT-001")
        backend:     LLM backend override
        model:       Model override

    Returns:
        dict: {success, report (markdown string), entity_code, elapsed_s}
    """
    start = time.time()
    entity_code = entity_code.strip().upper()

    # ── Collect all available evidence ───────────────────────────────────────

    data = {}

    # [CUSTOMIZE] Update these queries to your schema
    res = run_query(f"SELECT * FROM entities WHERE UPPER(code) = '{entity_code}' LIMIT 1")
    data["profile"] = res["rows"][0] if res["success"] and res["rows"] else {}

    entity_id = data["profile"].get("id")
    if not entity_id:
        return {"success": False, "error": f"Entity {entity_code} not found"}

    res = run_query(
        f"SELECT ev.*, e.name as counterparty FROM events ev "
        f"JOIN entities e ON ev.entity_id = e.id "
        f"WHERE ev.entity_id = {entity_id} ORDER BY ev.created_at DESC LIMIT 40"
    )
    data["all_events"] = res["rows"] if res["success"] else []

    res = run_query(
        f"SELECT * FROM alerts WHERE entity_id = {entity_id} ORDER BY risk_score DESC LIMIT 20"
    )
    data["alerts"] = res["rows"] if res["success"] else []

    # Activity statistics
    res = run_query(
        f"SELECT type, COUNT(*) as count, SUM(amount) as total, AVG(amount) as avg_amount "
        f"FROM events WHERE entity_id = {entity_id} GROUP BY type"
    )
    data["stats"] = res["rows"] if res["success"] else []

    # ── Build structured evidence prompt ─────────────────────────────────────
    forensic_prompt = f"""FORENSIC ANALYSIS REQUEST
Entity Code: {entity_code}
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

ENTITY PROFILE:
{json.dumps(data['profile'], indent=2, default=str)}

ACTIVITY STATISTICS:
{json.dumps(data['stats'], indent=2, default=str)}

RECENT EVENTS (last 40):
{json.dumps(data['all_events'][:20], indent=2, default=str)}

FRAUD ALERTS:
{json.dumps(data['alerts'], indent=2, default=str)}

Produce a comprehensive forensic investigation report covering all sections."""

    result = call_llm(prompt=forensic_prompt, system=FORENSIC_SYSTEM, backend=backend, model=model)

    elapsed = round(time.time() - start, 2)

    if result.get("success"):
        return {
            "success":     True,
            "report":      result["text"],
            "entity_code": entity_code,
            "elapsed_s":   elapsed
        }
    else:
        return {
            "success":   False,
            "error":     result.get("error", "LLM call failed"),
            "elapsed_s": elapsed
        }


# ─── HTTP REQUEST HANDLER ─────────────────────────────────────────────────────

class AgentHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for the AI Agent server.

    Routes:
      GET  /health   → system health check
      POST /analyze  → LangGraph investigation pipeline
      POST /chat     → smart natural language Q&A
      POST /forensic → deep forensic analysis

    All endpoints return JSON with at minimum: {success: bool}.
    On error: {success: false, error: "message"}.
    CORS headers are added to all responses for browser compatibility.
    """

    def log_message(self, format, *args):
        """Override to use our own log format instead of Apache-style."""
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"   [{ts}] {self.path} — {args[0] if args else ''}")

    def _set_headers(self, status: int = 200):
        """Send standard JSON response headers with CORS."""
        self.send_response(status)
        self.send_header("Content-Type",                "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")             # Allow all origins
        self.send_header("Access-Control-Allow-Headers", "Content-Type") # For POST requests
        self.end_headers()

    def _read_body(self) -> dict:
        """Read and parse JSON request body. Returns empty dict on failure."""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return {}

    def _send_json(self, data: dict, status: int = 200):
        """Serialize and send a JSON response."""
        self._set_headers(status)
        self.wfile.write(json.dumps(data, default=str, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self._set_headers(204)

    # ── GET /health ────────────────────────────────────────────────────────────

    def do_GET(self):
        """
        GET /health — System health check endpoint.

        Returns:
            {
              "status":      "ok",
              "backend":     "groq",
              "total_keys":  3,
              "model":       "qwen/qwen3-32b",
              "db_exists":   true,
              "db_path":     "/path/to/db",
              "timestamp":   "2026-04-15T14:00:00"
            }
        """
        if self.path == "/health":
            key_status = get_key_pool_status()
            self._send_json({
                "status":     "ok",
                "backend":    key_status["backend"],
                "total_keys": key_status["total_keys"],
                "keys":       key_status["keys"],
                "model":      key_status["model"],
                "db_exists":  DB_PATH.exists(),
                "db_path":    str(DB_PATH),
                "timestamp":  datetime.now().isoformat()
            })
        else:
            self._send_json({"error": "Not found"}, status=404)

    # ── POST routing ───────────────────────────────────────────────────────────

    def do_POST(self):
        """Route POST requests to the appropriate handler."""
        body = self._read_body()

        if self.path == "/analyze":
            self._handle_analyze(body)
        elif self.path == "/chat":
            self._handle_chat(body)
        elif self.path == "/forensic":
            self._handle_forensic(body)
        else:
            self._send_json({"error": "Unknown endpoint"}, status=404)

    # ── POST /analyze ──────────────────────────────────────────────────────────

    def _handle_analyze(self, body: dict):
        """
        POST /analyze — Run the full LangGraph investigation pipeline.

        Request body:
          {
            "task":        "string (required) — what to investigate",
            "entity_code": "string (optional) — entity code like ENT-001",
            "alert_id":    "string (optional) — triggering alert ID",
            "user_id":     int (optional) — numeric entity ID,
            "pattern":     "string (optional) — hint: 'circular_flow' etc.",
            "backend":     "string (optional) — 'groq'|'ollama'|'gemini'",
            "model":       "string (optional) — model override"
          }

        Response: {success, episode_id, final_answer, iterations, tool_calls,
                   elapsed_s, model, backend, _graph_plan, _tool_trace}
        """
        task        = body.get("task", "").strip()
        entity_code = body.get("entity_code", "").strip() or None
        alert_id    = body.get("alert_id",    "").strip() or None
        user_id     = body.get("user_id")
        pattern     = body.get("pattern",     "").strip() or None
        backend     = body.get("backend")
        model       = body.get("model")

        if not task:
            self._send_json({"success": False, "error": "Missing required field: task"}, status=400)
            return

        print(f"\n📥 POST /analyze — entity={entity_code} | alert={alert_id} | pattern={pattern}")

        # Pre-load entity context
        preload = {}
        try:
            preload = preload_entity_data(entity_code=entity_code, user_id=user_id)
        except Exception as e:
            print(f"   ⚠️  Preload warning: {e}")

        # Run the LangGraph pipeline
        try:
            result = run_analysis(
                task=task,
                entity_code=entity_code,
                pattern=pattern,
                alert_id=alert_id,
                user_id=user_id,
                backend=backend,
                model=model,
                preload=preload
            )
            self._send_json(result)
        except Exception as e:
            traceback.print_exc()
            self._send_json({"success": False, "error": str(e)}, status=500)

    # ── POST /chat ─────────────────────────────────────────────────────────────

    def _handle_chat(self, body: dict):
        """
        POST /chat — Natural language Q&A over the database.

        Request body:
          {
            "message":    "string (required) — natural language question",
            "session_id": "string (optional) — for logging",
            "backend":    "string (optional)",
            "model":      "string (optional)"
          }

        Response: {success, response, db_query_used, matched_intent}
        """
        message    = body.get("message", "").strip()
        session_id = body.get("session_id")
        backend    = body.get("backend")
        model      = body.get("model")

        if not message:
            self._send_json({"success": False, "error": "Missing required field: message"}, status=400)
            return

        print(f"\n📥 POST /chat — message: {message[:60]}")

        try:
            result = smart_chat(message, session_id=session_id, backend=backend, model=model)
            self._send_json(result)
        except Exception as e:
            traceback.print_exc()
            self._send_json({"success": False, "error": str(e)}, status=500)

    # ── POST /forensic ─────────────────────────────────────────────────────────

    def _handle_forensic(self, body: dict):
        """
        POST /forensic — Deep forensic analysis of a single entity.

        Request body:
          {
            "entity_code": "string (required) — entity code like ENT-001",
            "backend":     "string (optional)",
            "model":       "string (optional)"
          }

        Response: {success, report (markdown string), entity_code, elapsed_s}
        """
        entity_code = body.get("entity_code", "").strip()
        backend     = body.get("backend")
        model       = body.get("model")

        if not entity_code:
            self._send_json({"success": False, "error": "Missing required field: entity_code"}, status=400)
            return

        print(f"\n📥 POST /forensic — entity={entity_code}")

        try:
            result = forensic_analyze(entity_code, backend=backend, model=model)
            self._send_json(result)
        except Exception as e:
            traceback.print_exc()
            self._send_json({"success": False, "error": str(e)}, status=500)


# ─── SERVER STARTUP ───────────────────────────────────────────────────────────

def run_http_server(port: int = DEFAULT_PORT):
    """
    Start the AI Agent HTTP server.

    Prints startup banner with key pool status, model, and endpoint list.
    Runs until Ctrl+C or SIGTERM.
    """
    key_status = get_key_pool_status()

    print("\n" + "═" * 60)
    print("  🤖 AI AGENT SERVER")
    print("═" * 60)
    print(f"  Port    : {port}")
    print(f"  Backend : {key_status['backend'].upper()}")
    print(f"  Model   : {key_status['model']}")
    print(f"  Keys    : {key_status['total_keys']} loaded")
    for k in key_status["keys"]:
        print(f"            {k}")
    print(f"  DB      : {DB_PATH} {'✅' if DB_PATH.exists() else '❌ NOT FOUND'}")
    print("═" * 60)
    print(f"  Endpoints:")
    print(f"    GET  http://localhost:{port}/health")
    print(f"    POST http://localhost:{port}/analyze")
    print(f"    POST http://localhost:{port}/chat")
    print(f"    POST http://localhost:{port}/forensic")
    print("═" * 60 + "\n")

    HTTPServer(("localhost", port), AgentHandler).serve_forever()


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal AI Agent Server")
    parser.add_argument("--http",  action="store_true", help="Start HTTP server (recommended)")
    parser.add_argument("--port",  type=int, default=DEFAULT_PORT, help=f"Server port (default: {DEFAULT_PORT})")
    parser.add_argument("--test",  action="store_true", help="Run a quick self-test instead of starting server")
    args = parser.parse_args()

    if args.test:
        print("Running self-test...")
        result = run_analysis(
            task="Quick health check — confirm AI pipeline is working",
            entity_code=None,
            backend="groq"
        )
        print(json.dumps(result, indent=2, default=str))
    elif args.http:
        run_http_server(args.port)
    else:
        parser.print_help()
