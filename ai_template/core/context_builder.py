#!/usr/bin/env python3
"""
context_builder.py — Episodic Memory Context Loader
====================================================
Loads relevant past investigation episodes and entity profiles from the
persistent memory store to provide historical context to the LangGraph nodes.

This enables the AI to remember:
  - Previous investigations of the same entity
  - Previously detected patterns
  - Prior recommendations and their outcomes

Memory store locations (created automatically on first write):
  memory/episodes/episodes.jsonl   — all investigation episodes, chronological
  memory/entities/<CODE>.md        — per-entity markdown profile files

Cloned and generalized from FundTrace AI — April 2026.

# [CUSTOMIZE] markers show what to adapt for your domain.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

# ─── MEMORY PATHS ─────────────────────────────────────────────────────────────
_BASE_DIR      = Path(__file__).parent.parent          # ai_template/ root
_MEMORY_DIR    = _BASE_DIR / "memory"
_EPISODES_FILE = _MEMORY_DIR / "episodes" / "episodes.jsonl"
_ENTITIES_DIR  = _MEMORY_DIR / "entities"


def load_relevant_episodes(entity_code: str = None, pattern: str = None,
                            limit: int = 3) -> str:
    """
    Load the most relevant past investigation episodes for LLM context.

    Relevance is determined by:
      1. Same entity_code (highest priority)
      2. Same pattern type
      3. Recency (newer episodes first)

    The returned string is formatted for direct injection into an LLM prompt.
    It is intentionally compact — only the most useful fields are included.

    # [CUSTOMIZE] Change the displayed fields to match your episode schema.
    #             See memory_writer.py for what fields are stored.

    Args:
        entity_code: Filter for this entity's episodes
        pattern:     Filter for this pattern type
        limit:       Max episodes to return (default 3)

    Returns:
        str: Formatted text for LLM context injection, empty string if no history
    """
    if not _EPISODES_FILE.exists():
        return ""

    try:
        episodes = []
        with open(_EPISODES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        episodes.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

        if not episodes:
            return ""

        # Score and sort by relevance
        def relevance_score(ep: dict) -> int:
            score = 0
            if entity_code and ep.get("entity_code", "").upper() == entity_code.upper():
                score += 100   # Same entity = highly relevant
            if pattern and ep.get("pattern") == pattern:
                score += 50    # Same pattern type = relevant
            return score

        # Sort: primary = relevance score (desc), secondary = timestamp (desc)
        sorted_eps = sorted(episodes, key=lambda e: (relevance_score(e), e.get("timestamp", "")),
                            reverse=True)
        top = sorted_eps[:limit]

        if not top:
            return ""

        lines = ["RELEVANT PAST INVESTIGATIONS:"]
        for ep in top:
            ts  = ep.get("timestamp", "unknown")[:10]  # date only
            eid = ep.get("entity_code", "unknown")
            # [CUSTOMIZE] Change the field names below to match your episode schema
            lines.append(
                f"  [{ts}] Entity: {eid} | "
                f"Risk: {ep.get('risk_score', '?')}/100 | "
                f"Recommendation: {ep.get('recommendation', '?')} | "
                f"Summary: {ep.get('output_summary', '')[:120]}"
            )

        return "\n".join(lines)

    except Exception as e:
        print(f"   ⚠️  Episode load error: {e}")
        return ""


def load_entity_profile(entity_code: str) -> str:
    """
    Load the persistent markdown profile for an entity.

    Entity profiles are written by memory_writer.update_entity_profile() after
    each investigation. They accumulate over time, storing behavioral patterns,
    risk history, and open questions from previous investigations.

    # [CUSTOMIZE] The profile format is defined in memory_writer.py.
    #             This function just reads whatever is stored there.

    Args:
        entity_code: The entity's unique code string

    Returns:
        str: Markdown profile content, or empty string if no profile exists yet
    """
    if not entity_code:
        return ""

    profile_path = _ENTITIES_DIR / f"{entity_code.strip().upper()}.md"
    if not profile_path.exists():
        return ""

    try:
        content = profile_path.read_text(encoding="utf-8")
        # Return up to 2000 chars — enough context without flooding the LLM prompt
        return content[:2000]
    except Exception as e:
        print(f"   ⚠️  Entity profile load error ({entity_code}): {e}")
        return ""
