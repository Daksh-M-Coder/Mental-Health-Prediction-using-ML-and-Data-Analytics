/**
 * api.js — MindBridge Frontend API Client
 * All backend calls go through here. Change BACKEND_URL in .env.local to switch environments.
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5002";

async function apiFetch(path, options = {}) {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API error ${res.status}`);
  }
  return res.json();
}

/** GET /health — backend + ollama + model status */
export async function getHealth() {
  return apiFetch("/health");
}

/** GET /models — list available Ollama models */
export async function getModels() {
  return apiFetch("/models");
}

/**
 * POST /interview — single Empathy Map interview turn
 * @param {string} message — user's latest message
 * @param {Array}  conversationHistory — [{role, content}]
 * @param {string} model — optional model override
 */
export async function sendInterviewMessage(message, conversationHistory = [], model = null) {
  return apiFetch("/interview", {
    method: "POST",
    body: JSON.stringify({ message, conversation_history: conversationHistory, model }),
  });
}

/**
 * POST /score — convert conversation → 13 clinical features
 * @param {Array}  conversationHistory — full [{role, content}] array
 * @param {Object} empathyMap — accumulated empathy map
 * @param {string} model — optional model override
 */
export async function scoreConversation(conversationHistory, empathyMap = null, model = null) {
  return apiFetch("/score", {
    method: "POST",
    body: JSON.stringify({
      conversation_history: conversationHistory,
      empathy_map: empathyMap,
      model,
    }),
  });
}

/**
 * POST /predict — DTC prediction from 13 features (after /score)
 * @param {Object} features — the 13 clinical feature values
 */
export async function predictFromFeatures(features) {
  return apiFetch("/predict", {
    method: "POST",
    body: JSON.stringify(features),
  });
}

/**
 * POST /predict-direct — manual form path, bypasses interview
 * @param {Object} features — the 13 clinical feature values
 */
export async function predictDirect(features) {
  return apiFetch("/predict-direct", {
    method: "POST",
    body: JSON.stringify(features),
  });
}

/**
 * POST /hybrid-turn — single hybrid interview turn
 * @param {string} message
 * @param {Array}  conversationHistory
 * @param {Object} empathyMap
 * @param {string} model
 */
export async function sendHybridTurn(message, conversationHistory = [], empathyMap = null, model = null) {
  return apiFetch("/hybrid-turn", {
    method: "POST",
    body: JSON.stringify({
      message,
      conversation_history: conversationHistory,
      empathy_map: empathyMap,
      model,
    }),
  });
}

/**
 * POST /hybrid-analyze — empathetic narrative from full hybrid interview
 * @param {Array}  conversationHistory
 * @param {Object} empathyMap
 * @param {string} model
 */
export async function sendHybridAnalyze(conversationHistory, empathyMap = null, model = null) {
  return apiFetch("/hybrid-analyze", {
    method: "POST",
    body: JSON.stringify({ conversation_history: conversationHistory, empathy_map: empathyMap, model }),
  });
}

/**
 * POST /hybrid-score — extract features + DTC predict from hybrid interview
 * @param {Array}  conversationHistory
 * @param {Object} empathyMap
 * @param {string} model
 */
export async function sendHybridScore(conversationHistory, empathyMap = null, model = null) {
  return apiFetch("/hybrid-score", {
    method: "POST",
    body: JSON.stringify({ conversation_history: conversationHistory, empathy_map: empathyMap, model }),
  });
}

/**
 * POST /set-model — switch active Ollama model at runtime
 * @param {string} model — e.g. "deepseek-r1:7b"
 */
export async function setModel(model) {
  return apiFetch("/set-model", {
    method: "POST",
    body: JSON.stringify({ model }),
  });
}

/** GET /sessions — persisted sessions from MongoDB */
export async function getSessions(limit = 50, skip = 0) {
  return apiFetch(`/sessions?limit=${limit}&skip=${skip}`);
}

/** DELETE /sessions — wipe all MongoDB sessions */
export async function clearSessions() {
  return apiFetch("/sessions", { method: "DELETE" });
}

/** DELETE /sessions/:id — delete one session by ID */
export async function deleteSession(sessionId) {
  return apiFetch(`/sessions/${encodeURIComponent(sessionId)}`, { method: "DELETE" });
}

/** PATCH /sessions/:id — rename a session */
export async function renameSession(sessionId, newName) {
  return apiFetch(`/sessions/${encodeURIComponent(sessionId)}`, {
    method: "PATCH",
    body: JSON.stringify({ name: newName }),
  });
}

/**
 * POST /conversations/save — persist full chat messages + empathy map
 * @param {string} sessionId
 * @param {Array}  messages — [{role, content}]
 * @param {Object} empathyMap
 * @param {Object} meta — { source, snippet, user_name }
 */
export async function saveConversation(sessionId, messages, empathyMap = null, meta = {}) {
  return apiFetch("/conversations/save", {
    method: "POST",
    body: JSON.stringify({
      session_id:  sessionId,
      messages,
      empathy_map: empathyMap,
      ...meta,
    }),
  });
}

/** GET /conversations/:id — retrieve stored conversation messages */
export async function getConversation(sessionId) {
  return apiFetch(`/conversations/${encodeURIComponent(sessionId)}`);
}

/** POST /cache/flush — clear Redis LLM cache */
export async function flushCache() {
  return apiFetch("/cache/flush", { method: "POST" });
}
