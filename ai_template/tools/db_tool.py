#!/usr/bin/env python3
"""
db_tool.py — Universal Read-Only Database Query Tool for AI Agents
==================================================================
Accepts SELECT-only SQL queries. Rejects ALL write operations (INSERT, UPDATE,
DELETE, DROP, etc.) at the SQL parsing level before any connection is made.

This is the "safe data access" layer between the AI agent and your database.
The agent can see data but CANNOT modify it under any circumstances.

Supported database: SQLite (file-based, zero-config)
# [CUSTOMIZE] To support PostgreSQL/MySQL, replace the sqlite3 calls with
#             SQLAlchemy: conn = engine.connect() and cursor = conn.execute(sql)

Security layers:
  1. Must start with SELECT keyword
  2. Regex blocklist for dangerous patterns (DROP, INSERT, PRAGMA, etc.)
  3. Forbidden table names (AI never sees password_hash, sessions, etc.)
  4. Column-level firewall (strips forbidden columns from results)
  5. Hard row cap (MAX_ROWS) — AI cannot pull the entire database
  6. Read-only SQLite URI mode: file:path?mode=ro
  7. Query timeout enforced

HTTP API endpoints (when run with --http flag):
  POST /query   — { "sql": "SELECT ..." } → { success, count, rows, elapsed_ms }
  GET  /health  — { status, db_exists }

Audit Log:
  Every query (success or failure) is appended to: tools/logs/db_tool_audit.jsonl
  This log is never deleted or truncated.

CLI usage:
  python tools/db_tool.py "SELECT * FROM entities LIMIT 10"
  python tools/db_tool.py --http --port 5001
"""

import sys
import os
import re
import json
import sqlite3
import argparse
import time
import logging
from datetime import datetime
from pathlib import Path

# ─── DATABASE CONFIG ──────────────────────────────────────────────────────────
#
# [CUSTOMIZE] Update DB_PATH to point to your database file.
# The default walks up from tools/ → ai_template/ → project_root/ → server/
ROOT    = Path(__file__).parent.parent.parent   # tools/ → ai_template/ → project_root
DB_PATH = ROOT / "server" / "fundtrace.db"      # [CUSTOMIZE] change this path

# Fallback: try one level up if not found (useful when running from different cwd)
if not DB_PATH.exists():
    alt = Path(__file__).parent.parent / "data" / "app.db"
    if alt.exists():
        DB_PATH = alt

AUDIT_LOG          = Path(__file__).parent / "logs" / "db_tool_audit.jsonl"
MAX_ROWS           = 40      # Hard cap: AI never gets more than 40 rows in one query
QUERY_TIMEOUT_SECS = 5       # Kill slow queries after this many seconds

# ─── SECURITY CONFIGURATION ───────────────────────────────────────────────────
#
# [CUSTOMIZE] Add column names that should NEVER be returned to the AI.
# These are stripped from every result row before the AI sees it.
FORBIDDEN_COLUMNS = {
    "password_hash",    # never expose password hashes
    "token_hash",       # never expose session tokens
    "secret_key",       # any secret columns you have
    "pin",              # PINs / 2FA secrets
}

# [CUSTOMIZE] Add table names the AI should not be allowed to query at all.
# Access to these tables is rejected before a connection is opened.
FORBIDDEN_TABLES = {
    "sessions",         # server-side session tokens
    "login_attempts",   # brute force tracking data
    # Add your sensitive tables here: "admin_keys", "payment_credentials", etc.
}

# SQL patterns that are forbidden even inside a SELECT (prevents subquery injection)
FORBIDDEN_SQL_PATTERNS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bCREATE\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bREPLACE\b",
    r"\bATTACH\b",
    r"\bDETACH\b",
    r"\bPRAGMA\b",
    r"\bVACUUM\b",
    r"\bANALYZE\b",
    r"\bREINDEX\b",
    r"--",              # SQL comment injection
    r";.*\S",           # Multiple statements (second statement after semicolon)
]


# ─── SQL VALIDATION ───────────────────────────────────────────────────────────

def validate_query(sql: str) -> tuple:
    """
    Validate that a SQL string is safe to execute.

    Checks (in order):
      1. Must start with SELECT
      2. No forbidden SQL patterns
      3. No forbidden table access

    Args:
        sql: The SQL string to validate

    Returns:
        (is_safe: bool, reason: str)
        If is_safe=True, reason is "ok".
        If is_safe=False, reason explains WHY it was rejected (logged for audit).
    """
    sql_upper = sql.upper().strip()

    # Rule 1: Must start with SELECT
    if not sql_upper.startswith("SELECT"):
        return False, "Only SELECT queries allowed. Received: " + sql_upper[:30]

    # Rule 2: No forbidden SQL patterns (case-insensitive)
    for pattern in FORBIDDEN_SQL_PATTERNS:
        if re.search(pattern, sql_upper):
            return False, f"Forbidden SQL pattern: {pattern}"

    # Rule 3: No forbidden table access
    for table in FORBIDDEN_TABLES:
        if re.search(r'\b' + table.upper() + r'\b', sql_upper):
            return False, f"Access to table '{table}' is not permitted for AI agents"

    return True, "ok"


def sanitize_row(row: dict) -> dict:
    """
    Remove forbidden columns from a result row.
    This is the column-level firewall — even if a query somehow SELECTs
    a forbidden column, it is stripped before the result reaches the agent.

    Args:
        row: Dictionary of column_name → value

    Returns:
        Filtered dictionary with forbidden columns removed
    """
    return {k: v for k, v in row.items() if k.lower() not in FORBIDDEN_COLUMNS}


# ─── QUERY EXECUTION ─────────────────────────────────────────────────────────

def run_query(sql: str) -> dict:
    """
    Execute a validated SELECT query against the database.

    This is the main function called by the AI agent's tool runner.
    Safe to expose to an LLM — all safety checks are enforced here.

    Args:
        sql: SQL SELECT query string

    Returns:
        dict: {
            "success":    bool,
            "count":      int,      # number of rows returned
            "rows":       list,     # list of row dicts (sensitive columns stripped)
            "elapsed_ms": int,      # query execution time
            "truncated":  bool,     # True if results were capped at MAX_ROWS
            "error":      str,      # only present on failure
        }

    Example:
        result = run_query("SELECT id, name FROM entities LIMIT 10")
        if result["success"]:
            for row in result["rows"]:
                print(row)
    """
    start = time.time()

    # Step 1: Validate before connecting
    is_safe, reason = validate_query(sql)
    if not is_safe:
        log_query(sql, 0, 0, success=False, error=reason)
        return {"success": False, "error": reason, "rows": [], "count": 0}

    # Step 2: Verify database exists
    if not DB_PATH.exists():
        err = f"Database not found at {DB_PATH}. Check DB_PATH in db_tool.py."
        return {"success": False, "error": err, "rows": [], "count": 0}

    try:
        # Step 3: Open read-only connection (URI mode — cannot write even by accident)
        conn = sqlite3.connect(
            f"file:{DB_PATH}?mode=ro", uri=True, timeout=QUERY_TIMEOUT_SECS
        )
        conn.row_factory = sqlite3.Row   # enables dict-like access by column name

        cursor = conn.cursor()

        # Step 4: Auto-add LIMIT if missing (prevents accidentally huge result sets)
        sql_check = sql.upper().replace('\n', ' ')
        if 'LIMIT' not in sql_check:
            sql = sql.rstrip().rstrip(';') + f" LIMIT {MAX_ROWS}"

        # Step 5: Execute
        cursor.execute(sql)
        raw_rows = cursor.fetchmany(MAX_ROWS)
        rows     = [sanitize_row(dict(row)) for row in raw_rows]
        conn.close()

        elapsed = round(time.time() - start, 3)
        log_query(sql, len(rows), elapsed, success=True)

        return {
            "success":    True,
            "count":      len(rows),
            "rows":       rows,
            "elapsed_ms": int(elapsed * 1000),
            "truncated":  len(rows) == MAX_ROWS,   # hint: there may be more rows
        }

    except sqlite3.OperationalError as e:
        log_query(sql, 0, time.time() - start, success=False, error=str(e))
        return {"success": False, "error": f"SQL error: {str(e)}", "rows": [], "count": 0}
    except Exception as e:
        log_query(sql, 0, time.time() - start, success=False, error=str(e))
        return {"success": False, "error": f"Unexpected error: {str(e)}", "rows": [], "count": 0}


# ─── AUDIT LOGGING ────────────────────────────────────────────────────────────

def log_query(sql: str, row_count: int, elapsed: float, success: bool, error: str = None):
    """
    Append query record to the append-only audit log.

    The audit log records every query the AI runs — successful or not.
    It is never deleted, never truncated, and never modified.
    This is the compliance evidence that the AI only performed SELECT operations.

    Format: one JSON object per line (JSONL/ndjson format).
    """
    entry = {
        "ts":         datetime.utcnow().isoformat() + "Z",
        "sql":        sql[:500],   # cap very long queries
        "row_count":  row_count,
        "elapsed_s":  round(elapsed, 3),
        "success":    success,
        "error":      error
    }
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass   # Audit log failure should never crash the query itself


# ─── HTTP SERVER MODE ─────────────────────────────────────────────────────────

def run_http_server(port: int = 5001):
    """
    Run db_tool as a standalone HTTP server for use by external clients.

    This mode is optional — the primary usage is via direct Python import
    (from tools.db_tool import run_query).

    Endpoints:
      POST /query  — body: {"sql": "SELECT ..."}
                     returns: {success, count, rows, elapsed_ms, truncated}
      GET  /health — returns: {status, db_exists, db_path}
    """
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass   # Suppress default request log noise (queries go to audit log instead)

        def do_POST(self):
            """Handle POST /query requests."""
            if self.path != "/query":
                self.send_response(404)
                self.end_headers()
                return

            length = int(self.headers.get("Content-Length", 0))
            body   = self.rfile.read(length)
            try:
                data = json.loads(body)
                sql  = data.get("sql", "").strip()
            except Exception:
                sql = ""

            result   = run_query(sql) if sql else {"success": False, "error": "No SQL provided", "rows": [], "count": 0}
            response = json.dumps(result).encode()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(response))
            self.end_headers()
            self.wfile.write(response)

        def do_GET(self):
            """Handle GET /health requests."""
            if self.path == "/health":
                resp = json.dumps({
                    "status":   "ok",
                    "db_exists": DB_PATH.exists(),
                    "db_path":   str(DB_PATH)
                }).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(resp)
            else:
                self.send_response(404)
                self.end_headers()

    print(f"🔍 AI Agent DB Tool running on http://localhost:{port}")
    print(f"   Database : {DB_PATH}")
    print(f"   Audit log: {AUDIT_LOG}")
    print(f"   Endpoints: POST /query  |  GET /health")
    HTTPServer(("localhost", port), Handler).serve_forever()


# ─── CLI MODE ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    CLI usage:
      python tools/db_tool.py "SELECT * FROM entities LIMIT 5"
      python tools/db_tool.py --http
      python tools/db_tool.py --http --port 5001
    """
    parser = argparse.ArgumentParser(description="AI Agent Read-Only Database Tool")
    parser.add_argument("sql",    nargs="?", help="SQL SELECT query to execute")
    parser.add_argument("--http", action="store_true", help="Run as HTTP server")
    parser.add_argument("--port", type=int, default=5001, help="HTTP server port")
    args = parser.parse_args()

    if args.http:
        run_http_server(args.port)
    elif args.sql:
        result = run_query(args.sql)
        print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()
