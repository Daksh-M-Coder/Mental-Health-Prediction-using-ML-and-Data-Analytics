#!/usr/bin/env python3
"""
memory_writer.py — Persistent Investigation Memory Writer
==========================================================
Writes investigation results to two persistent memory stores:

  1. Episodic Memory  — JSONL file, one record per investigation
                         (memory/episodes/episodes.jsonl)

  2. Entity Profiles  — Per-entity Markdown files that accumulate over time
                         (memory/entities/<CODE>.md)

The episodic memory is loaded by context_builder.load_relevant_episodes()
to give the LLM historical context about previous findings.

Entity profiles are loaded by context_builder.load_entity_profile()
to give the LLM a summary of prior investigation history for this entity.

Both stores grow over time and are never deleted — they represent the AI's
accumulated investigative intelligence.

Cloned and generalized from FundTrace AI — April 2026.

# [CUSTOMIZE] markers show what to adapt for your domain.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone

# ─── MEMORY PATHS ─────────────────────────────────────────────────────────────
_BASE_DIR      = Path(__file__).parent.parent          # ai_template/ root
_MEMORY_DIR    = _BASE_DIR / "memory"
_EPISODES_FILE = _MEMORY_DIR / "episodes" / "episodes.jsonl"
_ENTITIES_DIR  = _MEMORY_DIR / "entities"


def _ensure_dirs():
    """Create memory directories if they do not exist."""
    _EPISODES_FILE.parent.mkdir(parents=True, exist_ok=True)
    _ENTITIES_DIR.mkdir(parents=True, exist_ok=True)


def _next_episode_id() -> str:
    """
    Generate a unique, chronological episode ID.

    Format: EP-YYYY-MM-DD-NNN
    Example: EP-2026-04-15-007 (7th episode on April 15, 2026)

    IDs are unique per day and monotonically increasing.
    They can be used as reference IDs in reports and alerts.
    """
    today = datetime.now().strftime("%Y-%m-%d")

    # Count existing episodes with today's date prefix
    count = 0
    if _EPISODES_FILE.exists():
        with open(_EPISODES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    ep = json.loads(line.strip())
                    if ep.get("episode_id", "").startswith(f"EP-{today}"):
                        count += 1
                except Exception:
                    pass

    return f"EP-{today}-{count + 1:03d}"


def write_episode(
    entity_code:    str,
    task:           str,
    trigger:        str,
    input_summary:  str,
    output_summary: str,
    risk_score:     int  = None,
    recommendation: str  = None,
    patterns:       list = None,
    evidence:       list = None,
    open_questions: list = None,
    # [CUSTOMIZE] Add any extra domain-specific fields here
    **extra_fields
) -> str:
    """
    Append one investigation episode to the episodic memory store.

    Called by run_analysis() in graph.py after each successful investigation.
    The episode is immediately available for future investigations of the same entity.

    # [CUSTOMIZE] Add or remove fields to match your domain's investigation output.
    #             Add extra domain fields as keyword arguments (**extra_fields).

    Args:
        entity_code:    The entity's unique code (e.g., "ENT-001")
        task:           Type of task run (e.g., "fraud_analysis", "compliance_check")
        trigger:        What triggered this investigation (e.g., "alert", "scheduled")
        input_summary:  Brief summary of what was investigated
        output_summary: Brief summary of the findings
        risk_score:     Numeric risk score 0-100
        recommendation: Action taken ("monitor", "review", "escalate", "close")
        patterns:       List of detected patterns (strings)
        evidence:       List of evidence items (strings)
        open_questions: List of unanswered questions (strings)
        **extra_fields: Any additional domain-specific fields

    Returns:
        str: The episode_id of the newly created episode
    """
    _ensure_dirs()
    ep_id = _next_episode_id()
    now   = datetime.now(timezone.utc).isoformat()

    episode = {
        "episode_id":     ep_id,
        "timestamp":      now,
        "entity_code":    entity_code or "unknown",
        "task":           task,
        "trigger":        trigger,
        "input_summary":  input_summary[:500] if input_summary else "",
        "output_summary": output_summary[:500] if output_summary else "",
        # [CUSTOMIZE] Rename these fields to match your domain's risk vocabulary
        "risk_score":     risk_score,
        "recommendation": recommendation,
        "patterns":       patterns or [],
        "evidence":       evidence[:10] if evidence else [],     # Cap at 10 items
        "open_questions": open_questions or [],
        **extra_fields    # Domain-specific extra fields merged in
    }

    try:
        with open(_EPISODES_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(episode, ensure_ascii=False) + "\n")
        print(f"   💾 Episode written: {ep_id}")
    except Exception as e:
        print(f"   ⚠️  Episode write error: {e}")

    return ep_id


def update_entity_profile(entity_code: str, investigation_result: dict):
    """
    Update (or create) the persistent markdown profile for an entity.

    The profile is a Markdown file that accumulates investigation history.
    It starts from an empty file and grows with each investigation.
    The LLM reads this profile at investigation start to understand the
    entity's behavioral history.

    Profile format:
      # Entity Profile: <CODE>
      ## Investigation History
        - [date] Risk: N/100 | Recommendation: X | Patterns: [Y, Z]
          Summary: ...
      ## Current Risk Assessment
        Risk Score: N/100 | Level: X | Recommendation: Y
      ## Open Questions
        - ...
      ## Detected Patterns History
        - ...

    # [CUSTOMIZE] Change the field names to match your investigation_result schema.
    #             The keys accessed here must match what graph.py's reflector produces.

    Args:
        entity_code:          The entity's unique code (e.g., "ENT-001")
        investigation_result: The final_answer dict from the reflector node
    """
    if not entity_code:
        return

    _ensure_dirs()
    safe_code    = entity_code.strip().upper()
    profile_path = _ENTITIES_DIR / f"{safe_code}.md"
    now          = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Extract fields from investigation result
    # [CUSTOMIZE] Update these field names to match your reflector output schema
    risk_score      = investigation_result.get("risk_score", "?")
    risk_level      = investigation_result.get("risk_level", "unknown")
    recommendation  = investigation_result.get("recommendation", "unknown")
    patterns        = investigation_result.get("patterns_detected", [])
    evidence        = investigation_result.get("evidence", [])
    open_questions  = investigation_result.get("open_questions", [])
    reasoning       = investigation_result.get("reasoning", "")[:500]

    # New investigation entry to prepend
    new_entry = f"""
### Investigation — {now}
- **Risk Score:** {risk_score}/100 | **Level:** {risk_level} | **Recommendation:** {recommendation}
- **Patterns:** {', '.join(patterns) if patterns else 'none detected'}
- **Evidence:** {'; '.join(str(e) for e in evidence[:3]) if evidence else 'none recorded'}
- **Reasoning:** {reasoning}
"""
    if open_questions:
        new_entry += f"- **Open Questions:** {'; '.join(str(q) for q in open_questions[:3])}\n"

    # Build or update the profile file
    if profile_path.exists():
        existing = profile_path.read_text(encoding="utf-8")
        # Insert new entry after the ## Investigation History heading
        if "## Investigation History" in existing:
            updated = existing.replace(
                "## Investigation History",
                f"## Investigation History{new_entry}"
            )
        else:
            updated = existing + "\n" + new_entry

        # Update the "Current Risk Assessment" section
        current_section = f"""## Current Risk Assessment
- **Risk Score:** {risk_score}/100
- **Risk Level:** {risk_level}
- **Recommendation:** {recommendation}
- **Last Updated:** {now}
"""
        if "## Current Risk Assessment" in updated:
            # Replace existing current risk section
            lines   = updated.split("\n")
            new_lines = []
            skip    = False
            for line in lines:
                if line.startswith("## Current Risk Assessment"):
                    new_lines.append(current_section)
                    skip = True
                elif skip and line.startswith("##"):
                    skip = False
                    new_lines.append(line)
                elif not skip:
                    new_lines.append(line)
            updated = "\n".join(new_lines)
        else:
            updated += "\n" + current_section

    else:
        # Create new profile from scratch
        updated = f"""# Entity Profile: {safe_code}
**Created:** {now}

## Current Risk Assessment
- **Risk Score:** {risk_score}/100
- **Risk Level:** {risk_level}
- **Recommendation:** {recommendation}
- **Last Updated:** {now}

## Investigation History
{new_entry}

## Detected Patterns History
{chr(10).join(f'- {p}' for p in patterns) if patterns else '- None detected yet'}
"""

    try:
        profile_path.write_text(updated, encoding="utf-8")
        print(f"   📝 Entity profile updated: {safe_code}.md")
    except Exception as e:
        print(f"   ⚠️  Entity profile write error ({safe_code}): {e}")
