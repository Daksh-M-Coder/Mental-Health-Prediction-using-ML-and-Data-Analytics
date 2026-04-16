# 🤖 Universal LangGraph AI Agent Template
## Cloned and generalized from FundTrace AI (FraudSense) — April 2026

---

> **Purpose:** This template is a clean, universal, fully-documented clone of the FraudSense
> AI system. It provides a production-ready starting point for any domain that requires:
> - An autonomous LLM agent that investigates data and produces structured reports
> - A multi-backend LLM client (Groq, Ollama, Gemini) with key rotation
> - Persistent memory (episodic + entity profiles)
> - A safe read-only database query tool
> - A LangGraph Planner→Executor→Reflector pipeline
> - An HTTP API server for integration with any frontend or backend
> - Comprehensive AI call logging (JSON + Markdown)
>
> **To adapt this template to your domain:**
> Search for every comment marked with `# [CUSTOMIZE]` across all files.
> These are the only places you need to change to make this work for your use case.

---

## 📁 Template Structure

```
ai_template/
├── README.md                    ← You are here
├── requirements.txt             ← Python dependencies
├── config.env.template          ← Environment variable template (copy → .env)
│
├── agent.py                     ← HTTP server + all API endpoints (port 5002)
│                                  Endpoints: POST /analyze, POST /chat,
│                                             POST /forensic, GET /health
│
├── graph.py                     ← LangGraph StateGraph
│                                  Nodes: planner_node, executor_node, reflector_node
│                                  Flow: START → planner → executor → reflector → (loop|END)
│
├── core/
│   ├── llm_client.py            ← Multi-backend LLM interface (Groq/Ollama/Gemini)
│   │                              Key rotation, AI logging, think-tag stripping
│   ├── context_builder.py       ← Loads episodic memory + entity profiles for LLM context
│   └── memory_writer.py         ← Writes investigation results to persistent memory
│
└── tools/
    ├── db_tool.py               ← Safe read-only database query tool (SQL validation)
    └── log_reader.py            ← Event log reader tool
```

---

## ⚡ Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp config.env.template .env
# Edit .env — add your Groq API keys and database path
```

### 3. Add Groq API keys
Create `groq_key.txt` with one key per line:
```
gsk_xxxxxxxxxxxxxxxxxxxxxxxx
gsk_yyyyyyyyyyyyyyyyyyyyyyyy
```
Get free keys at https://console.groq.com

### 4. Start the agent server
```bash
python agent.py --http --port 5002
```

### 5. Test it
```bash
curl http://localhost:5002/health
curl -X POST http://localhost:5002/analyze \
  -H "Content-Type: application/json" \
  -d '{"task": "Analyze account X for suspicious activity", "entity_code": "ENT-001"}'
```

---

## 🔧 Customization Guide

You need to change **only these things** to adapt this template to your domain:

| What to change | Where | What to do |
|----------------|-------|------------|
| Domain terminology | `graph.py` — system prompts | Replace "fraud investigator" with your role |
| Database schema | `graph.py` — EXECUTOR_SYSTEM | Update table/column names |
| Database path | `.env` or `core/db_tool.py` | Point to your database file |
| Entity code format | Throughout | Replace `ENT-XXXXXX` with your ID format |
| Forbidden tables | `tools/db_tool.py` | Tables AI should never access |
| Analysis tools | `graph.py` — `_run_tool()` | Add domain-specific tools |
| Output schema | `graph.py` — REFLECTOR_SYSTEM | Change `risk_score` etc. to your fields |
| LLM backend | `.env` — `AGENT_BACKEND` | groq / ollama / gemini |
| Port | `.env` — `AGENT_PORT` | Default: 5002 |

---

## 🔁 How the LangGraph Pipeline Works

```
POST /analyze  →  run_analysis()  →  build_graph()
                                           │
                                    [PLANNER NODE]
                                    LLM generates 3-5 step plan
                                           │
                                    [EXECUTOR NODE]
                                    LLM picks tool + generates query
                                    Tool runs → result stored
                                           │
                                    [REFLECTOR NODE]
                                    Evaluates evidence quality
                                    Decision: "continue" or "done"
                                           │
                              ┌────────────┴────────────┐
                              │ "continue"              │ "done"
                        back to EXECUTOR              [END]
                                                    write_episode()
                                                    update_entity_profile()
                                                    return structured result
```

---

## 📡 API Reference

### `GET /health`
Returns system status, backend info, key pool status.
```json
{"status": "ok", "backend": "groq", "total_keys": 3, "model": "qwen/qwen3-32b"}
```

### `POST /analyze`
Run the full LangGraph investigation pipeline.
```json
// Request
{"task": "Investigate entity X for pattern Y", "entity_code": "ENT-001", "backend": "groq"}

// Response
{"success": true, "final_answer": {"risk_score": 75, "recommendation": "review", ...},
 "iterations": 3, "tool_calls": 4, "elapsed_s": 18.2, "_graph_plan": [...], "_tool_trace": [...]}
```

### `POST /chat`
Natural language Q&A over your database.
```json
// Request
{"message": "Show me the top 10 entities by activity", "session_id": "optional"}

// Response
{"success": true, "response": "Here are the top 10 entities...", "db_query_used": true}
```

### `POST /forensic`
Deep forensic analysis of a single entity.
```json
// Request
{"entity_code": "ENT-001", "backend": "groq"}

// Response
{"success": true, "report": "# Forensic Report\n## Entity Overview\n..."}
```

---

## 📝 Logging

Every LLM call generates two log files in `logs/`:
- `logs/json/NNNN_YYYYMMDD_HHMMSS_keyN_modelname.json` — machine-readable full log
- `logs/md/NNNN_YYYYMMDD_HHMMSS_keyN_modelname.md` — human-readable formatted log

Sequence numbers are globally monotonic. Log #0042 always refers to the same call.

---

## 💾 Memory System

After each `analyze` call, the system writes:
1. **Episode:** `memory/episodes/episodes.jsonl` — timestamped record of the investigation
2. **Entity profile:** `memory/entities/ENT-XXXXXX.md` — per-entity markdown profile

On the next investigation of the same entity, both are loaded as LLM context.
This creates persistent investigative intelligence that improves over time.

---

*Template generated from: FundTrace AI — FraudSense Agent (Production System)*
*Original system built: February–April 2026*
*Template version: 1.0 | April 15, 2026*
