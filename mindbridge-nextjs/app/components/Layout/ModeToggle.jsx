"use client";

/**
 * ModeToggle.jsx — Segmented Control for 💬 Chat / 🧠 ML+Hybrid
 * Exact spec from new dev plan Part 6.
 */
export default function ModeToggle({ mode, onChange }) {
  return (
    <div className="mode-toggle" role="tablist" aria-label="Interaction mode">
      <button
        role="tab"
        aria-selected={mode === "chat"}
        className={`mode-option${mode === "chat" ? " active" : ""}`}
        onClick={() => onChange("chat")}
        title="Direct Chat — just talk, no clinical analysis"
      >
        💬 Chat
      </button>
      <button
        role="tab"
        aria-selected={mode === "hybrid"}
        className={`mode-option${mode === "hybrid" ? " active" : ""}`}
        onClick={() => onChange("hybrid")}
        title="ML + Hybrid — structured assessment + DTC prediction"
      >
        🧠 ML+Hybrid
      </button>
    </div>
  );
}
