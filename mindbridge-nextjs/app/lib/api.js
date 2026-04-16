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
