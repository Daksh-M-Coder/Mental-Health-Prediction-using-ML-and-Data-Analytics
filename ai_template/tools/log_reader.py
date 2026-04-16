#!/usr/bin/env python3
"""
log_reader.py — Entity Event Log Reader Tool for AI Agents
===========================================================
Reads and summarizes event logs for a specific entity within a time window.
This tool is called by the executor node in graph.py when the LLM requests
"read_logs" as its tool choice.

The log reader provides a different data dimension than the DB tool:
  - DB tool:   structured relational data (table rows, balances, etc.)
  - Log reader: chronological event audit trail (what happened and when)

For the default implementation, logs are read from the database events table.

# [CUSTOMIZE] If your system uses file-based logs (e.g., application logs,
#             audit JSONL files), adapt the query in read_logs() to read from
#             those files instead of the database.

Cloned and generalized from FundTrace AI — April 2026.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ─── CONFIG ───────────────────────────────────────────────────────────────────

# [CUSTOMIZE] Point this to your database file
ROOT    = Path(__file__).parent.parent.parent
DB_PATH = ROOT / "server" / "fundtrace.db"

# Fallback DB path (if running from inside template directory)
if not DB_PATH.exists():
    alt = Path(__file__).parent.parent / "data" / "app.db"
    if alt.exists():
        DB_PATH = alt


def read_logs(entity_code: str = None, hours: int = 48, limit: int = 30) -> dict:
    """
    Read and summarize event log entries for a specific entity.

    This is the "read_logs" tool called by the executor node.
    It returns a human-readable summary string that the LLM can interpret.

    # [CUSTOMIZE] The SQL query below reads from an 'events' table.
    #             Update table/column names to match YOUR schema.
    #             The 'summary' string format can also be customized.

    Args:
        entity_code: The entity code to filter by (e.g., "ENT-001").
                     If None, returns recent events from all entities.
        hours:       How many hours back to look (default: 48)
        limit:       Max events to return (default: 30)

    Returns:
        dict: {
            "success":      bool,
            "event_count":  int,
            "summary":      str,   # formatted text for LLM context
            "events":       list,  # raw event records
        }
    """
    if not DB_PATH.exists():
        return {
            "success":     False,
            "event_count": 0,
            "summary":     f"Database not found at {DB_PATH}",
            "events":      []
        }

    # Calculate the cutoff timestamp
    cutoff_ts = (datetime.now(timezone.utc) - timedelta(hours=hours)).timestamp()

    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=5)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # [CUSTOMIZE] Update this query to match your schema.
        # Key fields to include: entity identifier, timestamp, event type, amount/value, status, notes
        if entity_code:
            cursor.execute("""
                SELECT
                    e.id,
                    e.event_id,
                    datetime(e.created_at, 'unixepoch') AS timestamp,
                    e.type,
                    e.amount,
                    e.status,
                    e.risk_score,
                    e.flagged,
                    ent.name      AS entity_name,
                    ent.code      AS entity_code
                FROM events e
                JOIN entities ent ON e.entity_id = ent.id
                WHERE UPPER(ent.code) = UPPER(?)
                  AND e.created_at >= ?
                ORDER BY e.created_at DESC
                LIMIT ?
            """, (entity_code, cutoff_ts, limit))
        else:
            cursor.execute("""
                SELECT
                    e.id,
                    e.event_id,
                    datetime(e.created_at, 'unixepoch') AS timestamp,
                    e.type,
                    e.amount,
                    e.status,
                    e.risk_score,
                    e.flagged,
                    ent.name      AS entity_name,
                    ent.code      AS entity_code
                FROM events e
                JOIN entities ent ON e.entity_id = ent.id
                WHERE e.created_at >= ?
                ORDER BY e.created_at DESC
                LIMIT ?
            """, (cutoff_ts, limit))

        rows   = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not rows:
            scope = f"entity {entity_code}" if entity_code else "all entities"
            return {
                "success":     True,
                "event_count": 0,
                "summary":     f"No events found for {scope} in the last {hours} hours.",
                "events":      []
            }

        # ── Build human-readable summary for LLM ────────────────────────────
        # [CUSTOMIZE] Update the summary format to use your field names and terminology.
        summary_lines = [
            f"EVENT LOG — {entity_code or 'All Entities'} | Last {hours} hours | {len(rows)} events"
        ]
        summary_lines.append("-" * 60)

        flagged_count  = sum(1 for r in rows if r.get("flagged"))
        total_amount   = sum(r.get("amount", 0) or 0 for r in rows)
        types_seen     = list({r.get("type", "?") for r in rows})

        summary_lines.append(f"Total events: {len(rows)} | Flagged: {flagged_count}")
        summary_lines.append(f"Total amount: {total_amount:,.2f}")
        summary_lines.append(f"Event types:  {', '.join(types_seen)}")
        summary_lines.append("")

        for r in rows[:15]:  # Show at most 15 event lines
            flag  = "⚠️" if r.get("flagged") else "  "
            score = f"[score:{r.get('risk_score', 0)}]" if r.get("risk_score") else ""
            summary_lines.append(
                f"{flag} {r.get('timestamp', '?')} | "
                f"{r.get('type', '?')} | "
                f"₹{r.get('amount', 0):,.0f} | "
                f"{r.get('status', '?')} {score}"
            )

        if len(rows) > 15:
            summary_lines.append(f"... and {len(rows) - 15} more events (showing first 15)")

        return {
            "success":     True,
            "event_count": len(rows),
            "summary":     "\n".join(summary_lines),
            "events":      rows
        }

    except Exception as e:
        return {
            "success":     False,
            "event_count": 0,
            "summary":     f"Log read error: {str(e)}",
            "events":      []
        }


# ─── FILE-BASED LOG READER (alternative implementation) ───────────────────────

def read_file_logs(log_file: Path, entity_code: str = None,
                   hours: int = 48, limit: int = 30) -> dict:
    """
    Alternative log reader for file-based logs (JSONL format).

    Use this instead of read_logs() if your application writes logs to
    files rather than storing them in the database.

    # [CUSTOMIZE] Activate this by calling it from _run_tool() in graph.py
    #             instead of read_logs().

    Args:
        log_file:    Path to the JSONL log file
        entity_code: Filter to this entity's events
        hours:       How far back to look
        limit:       Max lines to return

    Returns:
        Same format as read_logs()
    """
    if not log_file.exists():
        return {
            "success": False, "event_count": 0,
            "summary": f"Log file not found: {log_file}", "events": []
        }

    cutoff_dt = datetime.now(timezone.utc) - timedelta(hours=hours)
    events    = []

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    # [CUSTOMIZE] Update the timestamp field name ("ts" here)
                    ts_str = entry.get("ts", "")
                    if ts_str:
                        ts = datetime.fromisoformat(ts_str.rstrip("Z"))
                        if ts.replace(tzinfo=timezone.utc) < cutoff_dt:
                            continue
                    # [CUSTOMIZE] Update the entity code field name
                    if entity_code and entry.get("entity_code", "").upper() != entity_code.upper():
                        continue
                    events.append(entry)
                except Exception:
                    continue

        events = events[-limit:]  # Most recent first

        if not events:
            return {
                "success": True, "event_count": 0,
                "summary": f"No log entries found for {entity_code or 'all'} in last {hours}h",
                "events": []
            }

        summary = f"FILE LOG: {len(events)} entries from {log_file.name}\n"
        for e in events[:10]:
            summary += f"  {e.get('ts', '?')} | {json.dumps(e)[:150]}\n"

        return {"success": True, "event_count": len(events), "summary": summary, "events": events}

    except Exception as ex:
        return {"success": False, "event_count": 0, "summary": str(ex), "events": []}


# ─── STANDALONE TEST ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    """Test: python tools/log_reader.py"""
    print("Testing log reader...")
    result = read_logs(hours=168, limit=10)
    print(f"Success: {result['success']} | Events: {result['event_count']}")
    print(result["summary"])
