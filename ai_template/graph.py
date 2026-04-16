#!/usr/bin/env python3
"""
graph.py — Universal LangGraph StateGraph (Planner → Executor → Reflector)
===========================================================================
This is the heart of the AI agent. A LangGraph StateGraph that autonomously:
  1. Plans an investigation (3-5 ordered steps)
  2. Executes each step using available tools
  3. Reflects on evidence quality and decides: continue or produce final answer

Cloned and generalized from FundTrace AI (FraudSense) — April 2026.

Graph topology:
  START → planner_node → executor_node → reflector_node
                              ↑                |
                      (should_continue)        | "continue"
                              └────────────────┘
                                               | "done" or iterations >= MAX
                                               ↓
                                             END

Nodes:
  planner_node   — LLM creates ordered investigation plan (temp=0.3, creative)
  executor_node  — LLM picks tool + generates query, runs it (temp=0.1, precise)
  reflector_node — LLM evaluates evidence, produces final answer (temp=0.2)

# [CUSTOMIZE] Look for all [CUSTOMIZE] markers in this file — they show exactly
#             what to change to adapt this to your domain.

Entry point:
  from graph import run_analysis
  result = run_analysis(task="...", entity_code="ENT-001", backend="groq")
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import TypedDict, List, Optional, Literal

# ─── LANGGRAPH IMPORTS ────────────────────────────────────────────────────────
from langgraph.graph import StateGraph, START, END

# ─── LOCAL IMPORTS — always import from core/, never from agent.py ────────────
sys.path.insert(0, str(Path(__file__).parent))

from core.llm_client     import call_llm, extract_json_from_response
from core.context_builder import load_relevant_episodes, load_entity_profile
from core.memory_writer   import write_episode, update_entity_profile
from tools.db_tool        import run_query
from tools.log_reader     import read_logs

# ─── GRAPH CONFIG ─────────────────────────────────────────────────────────────

MAX_GRAPH_ITERATIONS = 8   # Safety: max executor loops before forcing done

# [CUSTOMIZE] Update this path to point to your database file
DB_PATH = Path(__file__).parent.parent / "server" / "fundtrace.db"


# ─── AGENT STATE — Single source of truth flowing through the graph ────────────

class AgentState(TypedDict):
    """
    The complete state for one investigation run.
    Every node receives this state and returns a PARTIAL update dict.
    LangGraph merges the partial updates — nodes do NOT return the full state.

    Inputs (set once at run_analysis() call time, never modified):
      task         — The investigation task description
      entity_code  — The primary entity/account being investigated  [CUSTOMIZE: your ID format]
      pattern      — Hint about what type of issue to look for       [CUSTOMIZE: your categories]
      alert_id     — Reference ID of the triggering alert/event
      user_id      — Numeric user/entity ID in the database
      backend      — LLM backend to use ("groq"|"ollama"|"gemini")
      model        — LLM model override (None = use backend default)
      preload      — Pre-fetched context data passed in from caller

    Graph tracking (updated by nodes as investigation progresses):
      plan         — List of step strings from planner_node
      current_step — Which plan step executor is currently on (0-indexed)
      tool_history — All tool calls: {tool, input, output, finding, thought}
      working_notes — Accumulating investigation notes in plain text
      reflection   — Reflector's latest decision string ("continue"|"done")
      iterations   — Safety counter for max executor loops

    Outputs (final results):
      final_answer — Structured result dict when reflector says done
      status       — "planning"|"executing"|"reflecting"|"done"|"error"
      error        — Error message if status == "error"
      start_time   — Unix timestamp when run_analysis() was called
    """
    # ── Inputs ────────────────────────────────────────────────────────────────
    task:         str
    entity_code:  Optional[str]
    pattern:      Optional[str]
    alert_id:     Optional[str]
    user_id:      Optional[int]
    backend:      Optional[str]
    model:        Optional[str]
    preload:      dict

    # ── Graph tracking ────────────────────────────────────────────────────────
    plan:          List[str]
    current_step:  int
    tool_history:  List[dict]
    working_notes: str
    reflection:    str
    iterations:    int

    # ── Outputs ────────────────────────────────────────────────────────────────
    final_answer:  Optional[dict]
    status:        str
    error:         Optional[str]
    start_time:    float


# ─── TOOL RUNNER — Used by executor_node ──────────────────────────────────────

def _run_tool(tool_name: str, tool_input: str) -> str:
    """
    Execute a named tool and return the result as a string.

    This is the boundary between the LLM and the real world.
    The LLM specifies a tool name and input string; this function
    dispatches to the actual tool implementation and returns results.

    Available tools (teach the LLM about these in EXECUTOR_SYSTEM prompt):
      query_db            — Safe read-only SQL SELECT against your database
      read_logs           — Read entity event logs
      read_entity_profile — Read persistent per-entity investigation profile
      none                — No tool needed; LLM reasons from existing context

    # [CUSTOMIZE] Add your own domain-specific tools here.
    #             Each tool case should:
    #               a) call the actual tool function
    #               b) format the result as a readable string
    #               c) return the string (not a dict)

    Args:
        tool_name:  One of the supported tool strings
        tool_input: Tool-specific input (SQL string, log params, entity code, etc.)

    Returns:
        str: Tool result as a plain string for the LLM to read
    """
    try:
        if tool_name == "query_db":
            # [CUSTOMIZE] This is your database query tool.
            # The LLM generates a SQL SELECT; run_query() validates + executes it.
            result = run_query(tool_input)
            if result["success"]:
                rows  = result["rows"]
                count = result["count"]
                return f"Query returned {count} rows:\n{json.dumps(rows[:20], indent=2, default=str)}"
            else:
                return f"Query error: {result['error']}"

        elif tool_name == "read_logs":
            # Parse pipe-separated params: "entity_code=ENT-001|hours=48|limit=30"
            # [CUSTOMIZE] Change param names to match your log reader's signature
            params = {}
            for part in tool_input.split("|"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    params[k.strip()] = v.strip()
            result = read_logs(
                entity_code=params.get("entity_code"),
                hours=int(params.get("hours", 48)),
                limit=int(params.get("limit", 30))
            )
            return result.get("summary", "No log events found")

        elif tool_name == "read_entity_profile":
            # [CUSTOMIZE] Change to match your entity ID format
            safe         = tool_input.strip().upper()
            profile_path = Path(__file__).parent / "memory" / "entities" / f"{safe}.md"
            if profile_path.exists():
                return profile_path.read_text(encoding="utf-8")[:2000]
            return f"No entity profile found for {safe}"

        elif tool_name == "none":
            return "No tool used — analysis from existing context."

        return f"Unknown tool: {tool_name}"

    except Exception as e:
        return f"Tool error [{tool_name}]: {str(e)}"


# ─── PLANNER NODE ─────────────────────────────────────────────────────────────
#
# [CUSTOMIZE] The PLANNER_SYSTEM prompt defines the investigation domain.
# Change "financial fraud investigation" to your domain.
# Change the tool list to match your available tools.
# The output format (JSON with "plan" array) should stay the same.

PLANNER_SYSTEM = """You are an expert investigation planner.
Your job: given an investigation task, produce a CONCISE ordered investigation plan (3-5 steps).

RULES:
- Each step must be a specific, actionable investigation action
- Include tool-use steps: "Query DB for X", "Read logs for Y", "Check entity profile"
- Include an analysis step: "Analyze patterns in collected data"
- Include a conclusion step: "Synthesize findings into a structured assessment"
- DO NOT include vague steps like "investigate further" — be specific
- Step count: 3 minimum, 5 maximum

Respond ONLY with valid JSON:
{"plan": ["step 1 description", "step 2 description", "step 3 description"]}"""


def planner_node(state: AgentState) -> dict:
    """
    Planner node: creates the investigation plan for this run.

    Reads: task, entity_code, pattern (from state inputs)
    Also loads: relevant past episodes + entity profile from memory
    Writes: plan (list of step strings), status="executing", current_step=0

    Temperature: 0.3 (slightly creative to generate good varied plans)
    Fallback: hardcoded 3-step default plan if LLM fails or returns bad JSON
    """
    print(f"   🗺️  [PLANNER] Generating investigation plan...")

    task        = state["task"]
    entity_code = state.get("entity_code")
    pattern     = state.get("pattern")

    # Load memory context for this entity
    # [CUSTOMIZE] Change the parameters to match your context_builder.py signatures
    recent_eps  = load_relevant_episodes(entity_code, pattern, limit=3)
    entity_info = load_entity_profile(entity_code) if entity_code else ""

    planner_prompt = f"""INVESTIGATION TASK: {task}

Entity under investigation: {entity_code or "None specified"}
Investigation category: {pattern or "None specified"}

Recent investigation history:
{recent_eps}

{entity_info[:500] if entity_info else ""}

Create a 3-5 step investigation plan. Be specific about what data to query."""

    time.sleep(1.0)   # Rate-limit guard — avoid hitting LLM APIs too fast
    result = call_llm(
        prompt=planner_prompt,
        system=PLANNER_SYSTEM,
        backend=state.get("backend"),
        model=state.get("model")
    )

    if not result.get("success"):
        print(f"   ❌ [PLANNER] LLM failed: {result.get('error')}")
        # Fallback: simple but functional 3-step plan
        return {
            "plan": [
                f"1. Query {entity_code or 'subject'} profile and recent activity from database",
                "2. Analyze patterns and anomalies in collected data",
                "3. Synthesize findings into a risk assessment with recommendation"
            ],
            "status":       "executing",
            "current_step": 0
        }

    parsed = extract_json_from_response(result.get("text", ""))
    plan   = parsed.get("plan", [])

    # Fallback plan if JSON parsing failed
    if not plan or not isinstance(plan, list):
        plan = [
            f"1. Query {entity_code or 'subject'} profile and activity from the database",
            "2. Analyze patterns for suspicious or anomalous behavior",
            "3. Check for known risk patterns and historical context",
            "4. Synthesize all findings into a comprehensive assessment"
        ]

    print(f"   ✅ [PLANNER] Plan created: {len(plan)} steps")
    for i, step in enumerate(plan):
        print(f"      Step {i+1}: {step[:80]}")

    return {
        "plan":          plan,
        "status":        "executing",
        "current_step":  0,
        "tool_history":  [],
        "working_notes": "",
        "reflection":    "",
        "iterations":    0
    }


# ─── EXECUTOR NODE ─────────────────────────────────────────────────────────────
#
# [CUSTOMIZE] The EXECUTOR_SYSTEM prompt must describe:
#   1. Available tools and exactly how to call each one
#   2. Your database schema (table names, column names, data types)
#   3. Any domain-specific SQL rules (date formats, ID formats, etc.)
# The JSON output format (thought/tool/tool_input/finding) should stay the same.

EXECUTOR_SYSTEM = """You are an expert analyst executing ONE specific investigation step.
You have access to these tools:

  - query_db:            Run a SELECT SQL query against the SQLite database
  - read_logs:           Read entity event logs (params: "entity_code=ENT-XXX|hours=48|limit=30")
  - read_entity_profile: Read stored entity profile (param: entity code like "ENT-XXX")
  - none:                No tool needed — derive answer from existing context

DATABASE TABLES (SQLite):
  [CUSTOMIZE: Replace this section with YOUR actual database schema]
  - entities:     id, name, code (ENT-XXXXXX), status, balance, created_at, last_active
  - events:       id, event_id, entity_id, amount, type, status, risk_score, flagged, created_at
  - alerts:       id, alert_id, entity_id, event_id, risk_score, pattern_type, status, created_at

CRITICAL SQL RULES:
  - Only SELECT statements are allowed
  - Always add LIMIT (max 25)
  - Use datetime(created_at, 'unixepoch') to display timestamps if stored as Unix time
  - Entity codes are case-sensitive — use UPPER() when matching

Respond ONLY with valid JSON:
{
  "thought":    "what I'm doing and why",
  "tool":       "query_db | read_logs | read_entity_profile | none",
  "tool_input": "the SQL query or params string (empty string if none)",
  "finding":    "what I expect to discover / what this will tell us"
}"""


def executor_node(state: AgentState) -> dict:
    """
    Executor node: LLM decides which tool to use and generates the exact query.

    This implements "Option B" agentic behavior: the LLM generates its OWN SQL
    instead of picking from a predefined query library. This allows investigating
    questions that were never anticipated when the tools were built.

    Reads:  plan, current_step, tool_history, working_notes from state
    Writes: tool_history (appended), working_notes (appended),
            current_step (incremented), status="reflecting", iterations (incremented)

    Temperature: 0.1 (low = deterministic, precise SQL generation)
    """
    plan          = state.get("plan", [])
    current_step  = state.get("current_step", 0)
    tool_history  = list(state.get("tool_history", []))
    working_notes = state.get("working_notes", "")
    iterations    = state.get("iterations", 0)

    # Safety: step out of range → move to reflection
    if not plan or current_step >= len(plan):
        print(f"   ⚠️  [EXECUTOR] No more plan steps (step {current_step}/{len(plan)})")
        return {"status": "reflecting", "iterations": iterations + 1}

    current_step_text = plan[current_step]
    print(f"   🔧 [EXECUTOR] Step {current_step + 1}/{len(plan)}: {current_step_text[:70]}")

    # Build minimal context: current step + last 3 tool results (keeps token count low)
    recent_tools = tool_history[-3:] if tool_history else []
    tool_context = ""
    if recent_tools:
        tool_context = "\n\nPREVIOUS FINDINGS:\n"
        for t in recent_tools:
            tool_context += f"Tool: {t['tool']} | Input: {t['input'][:100]}\n"
            tool_context += f"Output (first 300 chars): {str(t['output'])[:300]}\n\n"

    entity_code = state.get("entity_code", "")
    pattern     = state.get("pattern", "")

    executor_prompt = f"""CURRENT INVESTIGATION STEP: {current_step_text}

Entity: {entity_code or "Not specified"} | Category: {pattern or "None"}
{tool_context}
Working notes so far: {working_notes[:400] if working_notes else "None yet"}

Execute this specific step. Choose the best tool and generate the exact query/params."""

    time.sleep(1.5)   # Rate-limit guard — executor loops fastest, needs more delay
    result = call_llm(
        prompt=executor_prompt,
        system=EXECUTOR_SYSTEM,
        backend=state.get("backend"),
        model=state.get("model")
    )

    new_history = list(tool_history)
    new_notes   = working_notes

    if not result.get("success"):
        print(f"   ❌ [EXECUTOR] LLM error: {result.get('error')}")
        new_history.append({
            "step":    current_step + 1,
            "tool":    "error",
            "input":   current_step_text,
            "output":  f"LLM error: {result.get('error')}",
            "finding": "Step failed due to LLM error"
        })
    else:
        parsed     = extract_json_from_response(result.get("text", ""))
        tool_name  = parsed.get("tool", "none")
        tool_input = str(parsed.get("tool_input", "") or "")
        finding    = parsed.get("finding", "")
        thought    = parsed.get("thought", "")

        print(f"      → Tool: {tool_name}")
        if tool_input:
            print(f"      → Input: {tool_input[:100]}")

        # Execute the tool
        if tool_name != "none":
            tool_output = _run_tool(tool_name, tool_input)
            print(f"      → Output: {len(tool_output)} chars")
        else:
            tool_output = "No tool used — reasoning from context."

        new_history.append({
            "step":    current_step + 1,
            "tool":    tool_name,
            "input":   tool_input[:300],
            "output":  tool_output[:1000],
            "finding": finding[:500],
            "thought": thought[:300]
        })

        # Accumulate working notes for reflector context
        if finding:
            new_notes += f"\nStep {current_step + 1}: {finding}"
        if tool_output and tool_output != "No tool used — reasoning from context.":
            new_notes += f"\nData: {tool_output[:300]}"

    return {
        "tool_history":  new_history,
        "working_notes": new_notes,
        "current_step":  current_step + 1,
        "status":        "reflecting",
        "iterations":    iterations + 1
    }


# ─── REFLECTOR NODE ────────────────────────────────────────────────────────────
#
# [CUSTOMIZE] The REFLECTOR_SYSTEM prompt defines the output schema.
# Replace "risk_score", "recommendation" etc. with your domain's output fields.
# The decision/reason/final_answer JSON structure should stay the same.

REFLECTOR_SYSTEM = """You are a senior analyst reviewing an investigation in progress.
Your job: evaluate collected evidence and decide if the investigation is complete.

DECISION OPTIONS:
  - "continue": More investigation steps remain AND they would meaningfully improve the assessment
  - "done":     Enough evidence to produce a confident, well-supported final assessment

When "done", you MUST provide the final_answer with these fields:
  [CUSTOMIZE: Replace this section with YOUR output schema fields]
  - risk_score:        0-100 (0=no risk, 100=certain issue)
  - risk_level:        "low" | "medium" | "high" | "critical"
  - patterns_detected: list of detected issue patterns (strings)
  - evidence:          list of specific evidence items (cite real IDs, amounts, dates)
  - reasoning:         clear explanation of the assessment
  - recommendation:    "monitor" | "review" | "escalate" | "close"
  - confidence:        0-100 (how confident are you in this assessment)
  - open_questions:    list of unanswered questions (can be empty list)

Respond ONLY with valid JSON:
{
  "decision":     "continue" or "done",
  "reason":       "one sentence explaining your decision",
  "final_answer": null when continuing, or the full assessment dict when done
}"""


def reflector_node(state: AgentState) -> dict:
    """
    Reflector node: evaluates accumulated evidence and decides next action.

    When decision == "done": synthesizes the final_answer structured output.
    When decision == "continue": returns None for final_answer (executor runs again).

    Force-done conditions (overrides LLM decision):
      - All plan steps have been executed (current_step >= len(plan))
      - Safety limit reached (iterations >= MAX_GRAPH_ITERATIONS)

    Reads:  plan, current_step, tool_history, working_notes, iterations from state
    Writes: reflection ("continue"|"done"), final_answer (dict|None), status

    Temperature: 0.2 (balanced — needs reasoning but consistent risk scores)
    """
    plan          = state.get("plan", [])
    current_step  = state.get("current_step", 0)
    tool_history  = state.get("tool_history", [])
    working_notes = state.get("working_notes", "")
    iterations    = state.get("iterations", 0)
    entity_code   = state.get("entity_code", "")
    pattern       = state.get("pattern", "")

    print(f"   🪞 [REFLECTOR] Evaluating evidence (iteration {iterations}, step {current_step}/{len(plan)})...")

    # Check if we must force done
    force_done = (current_step >= len(plan)) or (iterations >= MAX_GRAPH_ITERATIONS)

    # Summarize all findings for reflector context
    findings_summary = ""
    for item in tool_history:
        findings_summary += f"\n[Step {item.get('step', '?')}] Tool: {item['tool']}\n"
        if item.get("finding"):
            findings_summary += f"  Finding: {item['finding'][:200]}\n"
        if item.get("output") and item["tool"] not in ("none", "error"):
            findings_summary += f"  Data: {item['output'][:300]}\n"

    remaining_steps = plan[current_step:] if current_step < len(plan) else []

    reflector_prompt = f"""INVESTIGATION SUMMARY:
Task: {state.get('task', '')}
Entity: {entity_code or 'None'} | Category: {pattern or 'None'}
Steps completed: {current_step}/{len(plan)}
Iterations used: {iterations}/{MAX_GRAPH_ITERATIONS}

COLLECTED EVIDENCE:
{findings_summary if findings_summary else "No tool data collected yet"}

WORKING NOTES:
{working_notes[:600] if working_notes else "None"}

REMAINING PLAN STEPS:
{chr(10).join(f'  - {s}' for s in remaining_steps) if remaining_steps else "All steps completed"}

{'IMPORTANT: All plan steps complete OR max iterations reached. You MUST output decision=done.' if force_done else 'Evaluate: is the current evidence sufficient for a confident assessment, or should we continue?'}

Provide your decision and {'the full final_answer assessment' if force_done else 'reason'}."""

    time.sleep(1.0)   # Rate-limit guard
    result = call_llm(
        prompt=reflector_prompt,
        system=REFLECTOR_SYSTEM,
        backend=state.get("backend"),
        model=state.get("model")
    )

    if not result.get("success"):
        print(f"   ❌ [REFLECTOR] LLM error: {result.get('error')}")
        return {
            "reflection":   "done",
            "final_answer": _make_fallback_answer(entity_code, pattern, tool_history, working_notes),
            "status":       "done"
        }

    parsed       = extract_json_from_response(result.get("text", ""))
    decision     = parsed.get("decision", "done" if force_done else "continue")
    reason       = parsed.get("reason", "")
    final_answer = parsed.get("final_answer")

    print(f"   {'✅' if decision == 'done' else '🔄'} [REFLECTOR] Decision: {decision} — {reason[:80]}")

    if decision == "done" or force_done:
        if not final_answer:
            final_answer = _make_fallback_answer(entity_code, pattern, tool_history, working_notes)
        return {
            "reflection":   "done",
            "final_answer": final_answer,
            "status":       "done"
        }
    else:
        return {
            "reflection":   "continue",
            "final_answer": None,
            "status":       "executing"
        }


def _make_fallback_answer(entity_code: str, pattern: str,
                           tool_history: list, working_notes: str) -> dict:
    """
    Generate a conservative fallback answer when the LLM fails to produce one.

    Uses keyword scanning on the accumulated tool history and working notes
    to infer a reasonable risk level. Always returns a valid output structure
    — the caller never receives an exception.

    # [CUSTOMIZE] Update the keyword lists and output fields to match your domain.
    """
    combined = json.dumps(tool_history, default=str).lower() + working_notes.lower()

    # [CUSTOMIZE] Change these detection terms to match your domain's risk indicators
    has_high_risk    = any(kw in combined for kw in ["critical", "high risk", "flagged", "fraud"])
    has_medium_risk  = any(kw in combined for kw in ["suspicious", "anomaly", "unusual", "review"])
    has_pattern      = bool(pattern)

    detected = []
    if has_high_risk:   detected.append("high_risk_indicators")
    if has_medium_risk: detected.append("suspicious_activity")
    if pattern and pattern not in detected:
        detected.append(pattern)

    # [CUSTOMIZE] Change risk thresholds and recommendation values
    if has_high_risk:
        risk_score    = 75
        risk_level    = "high"
        recommendation = "escalate"
    elif has_medium_risk:
        risk_score    = 55
        risk_level    = "medium"
        recommendation = "review"
    else:
        risk_score    = 35
        risk_level    = "low"
        recommendation = "monitor"

    return {
        "risk_score":        risk_score,
        "risk_level":        risk_level,
        "patterns_detected": detected or [pattern or "unknown"],
        "evidence":          [f"Collected {len(tool_history)} data points during investigation"],
        "reasoning": (
            f"Analysis of {entity_code or 'subject'} based on {len(tool_history)} "
            f"investigation steps. {working_notes[:300] if working_notes else 'Limited data collected.'}"
        ),
        "recommendation":    recommendation,
        "confidence":        45,   # conservative — fallback means LLM was unavailable
        "open_questions":    ["Manual review recommended to confirm automated findings"]
    }


# ─── CONDITIONAL EDGE — Routes reflector output ────────────────────────────────

def should_continue(state: AgentState) -> Literal["continue", "done"]:
    """
    Conditional edge function — determines graph flow after reflector_node.

    Returns "continue" → graph loops back to executor_node
    Returns "done"     → graph exits to END

    Logic:
      - If reflector said "done" → exit
      - If status is "error" → exit
      - If safety limit reached → exit
      - Otherwise → continue
    """
    reflection = state.get("reflection", "done")
    iterations = state.get("iterations", 0)
    status     = state.get("status", "done")

    if status == "error":               return "done"
    if reflection == "done":            return "done"
    if iterations >= MAX_GRAPH_ITERATIONS: return "done"
    return "continue"


# ─── GRAPH ASSEMBLY ───────────────────────────────────────────────────────────

def build_graph():
    """
    Assemble and compile the LangGraph StateGraph.

    Graph structure:
      START → planner → executor → reflector → (conditional) → executor (loop) or END

    Returns a compiled graph that can be invoked with an initial state dict.
    Call build_graph() once per run_analysis() call (not at module level)
    to avoid any potential state leakage between runs.
    """
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("planner",  planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("reflector", reflector_node)

    # Fixed edges: START → planner → executor → reflector
    graph.add_edge(START,      "planner")
    graph.add_edge("planner",  "executor")
    graph.add_edge("executor", "reflector")

    # Conditional edge: reflector → executor (continue) or END (done)
    graph.add_conditional_edges(
        "reflector",
        should_continue,
        {
            "continue": "executor",
            "done":     END
        }
    )

    return graph.compile()


# ─── ENTRY POINT — Called by agent.py HTTP server ────────────────────────────

def run_analysis(
    task:        str,
    entity_code: str  = None,
    pattern:     str  = None,
    alert_id:    str  = None,
    user_id:     int  = None,
    backend:     str  = None,
    model:       str  = None,
    preload:     dict = None
) -> dict:
    """
    Main entry point for the LangGraph investigation pipeline.

    Called by agent.py when POST /analyze is received.
    Returns the same response format every time — success or failure.
    After the graph completes, saves results to episodic + entity memory.

    Args:
        task:        Natural language investigation task description
        entity_code: Primary entity code to investigate (e.g., "ENT-001")
        pattern:     Hint about what to look for (e.g., "circular_flow")
        alert_id:    ID of the triggering alert (for memory recording)
        user_id:     Numeric database user/entity ID
        backend:     LLM backend override ("groq"|"ollama"|"gemini")
        model:       LLM model override
        preload:     Pre-fetched data to inject into context (optional)

    Returns:
        dict: {
            "success":      bool,
            "episode_id":   str,       # ID of the memory episode written
            "final_answer": dict,      # structured assessment (see REFLECTOR_SYSTEM)
            "iterations":   int,       # how many executor loops ran
            "tool_calls":   int,       # total tool executions
            "elapsed_s":    float,     # total wall time
            "model":        str,
            "backend":      str,
            "_graph_plan":  list,      # the plan that was generated (for debugging)
            "_tool_trace":  list,      # abbreviated tool execution trace (for debugging)
        }
    """
    start_time = time.time()

    print(f"\n🤖 Agent [LangGraph] starting...")
    print(f"   Task:   {task[:80]}")
    print(f"   Entity: {entity_code} | Pattern: {pattern}")

    # Build and run the graph
    compiled_graph = build_graph()

    initial_state: AgentState = {
        "task":          task,
        "entity_code":   entity_code,
        "pattern":       pattern,
        "alert_id":      alert_id,
        "user_id":       user_id,
        "backend":       backend,
        "model":         model,
        "preload":       preload or {},
        "plan":          [],
        "current_step":  0,
        "tool_history":  [],
        "working_notes": "",
        "reflection":    "",
        "iterations":    0,
        "final_answer":  None,
        "status":        "planning",
        "error":         None,
        "start_time":    start_time
    }

    try:
        final_state = compiled_graph.invoke(initial_state)
    except Exception as e:
        print(f"   ❌ Graph execution error: {e}")
        import traceback; traceback.print_exc()
        return {
            "success":   False,
            "error":     f"Graph error: {str(e)}",
            "iterations": 0,
            "elapsed_s": round(time.time() - start_time, 2)
        }

    elapsed      = round(time.time() - start_time, 2)
    final_answer = final_state.get("final_answer") or {}
    tool_history = final_state.get("tool_history", [])
    iterations   = final_state.get("iterations", 0)

    # Last-resort fallback if no final_answer was produced
    if not final_answer:
        final_answer = {
            "risk_score":        50,
            "risk_level":        "medium",
            "patterns_detected": [pattern] if pattern else [],
            "evidence":          [],
            "reasoning":         "Agent completed without producing a final assessment. Manual review recommended.",
            "recommendation":    "review",
            "confidence":        20,
            "open_questions":    ["Inconclusive — manual review required"]
        }

    print(f"\n   ✅ Graph complete | risk={final_answer.get('risk_score')}/100 | {iterations} iterations | {elapsed}s")

    # ── Save to persistent memory ─────────────────────────────────────────────
    ep_id = None
    try:
        ep_id = write_episode(
            entity_code=entity_code,
            task="analysis",
            trigger="alert",
            input_summary=f"Alert {alert_id or 'unknown'} | pattern={pattern} | {task[:200]}",
            output_summary=(
                f"Risk {final_answer.get('risk_score')}/100 | "
                f"{final_answer.get('recommendation')} | "
                f"{', '.join(final_answer.get('patterns_detected', []))}"
            ),
            risk_score=final_answer.get("risk_score"),
            recommendation=final_answer.get("recommendation"),
            patterns=final_answer.get("patterns_detected"),
            evidence=final_answer.get("evidence"),
            open_questions=final_answer.get("open_questions")
        )
        if entity_code:
            update_entity_profile(entity_code, final_answer)
    except Exception as e:
        print(f"   ⚠️  Memory write error: {e}")

    return {
        "success":      True,
        "episode_id":   ep_id,
        "final_answer": final_answer,
        "iterations":   iterations,
        "tool_calls":   len(tool_history),
        "elapsed_s":    elapsed,
        "model":        model,
        "backend":      backend,
        # Bonus fields for debugging — frontend can optionally display
        "_graph_plan":  final_state.get("plan", []),
        "_tool_trace":  [
            {"step": t.get("step"), "tool": t["tool"], "finding": t.get("finding", "")}
            for t in tool_history
        ]
    }


# ─── STANDALONE TEST ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Quick test: python graph.py
    Verifies that the graph builds and runs without errors.
    """
    print("Testing graph build...")
    g = build_graph()
    print(f"✅ Graph built: {g}")

    print("\nRunning test analysis...")
    result = run_analysis(
        task="Check for any suspicious patterns in the data",
        entity_code=None,
        pattern=None,
        backend="groq"
    )
    print("\nResult:")
    print(json.dumps(result, indent=2, default=str))
