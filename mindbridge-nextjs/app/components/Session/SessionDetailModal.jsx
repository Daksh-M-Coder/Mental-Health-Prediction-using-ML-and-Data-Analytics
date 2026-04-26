"use client";

/**
 * SessionDetailModal.jsx — Full session detail view when clicking a session card.
 * Shows: snippet, risk, scores, empathy map, source, timestamp.
 * This is the "session restore" UX — displays all captured data for a past session.
 */

const riskColor = {
  high:   { bg: "rgba(248,113,113,0.12)",  border: "rgba(248,113,113,0.35)", text: "#ef4444" },
  medium: { bg: "rgba(251,191,36,0.12)",   border: "rgba(251,191,36,0.35)",  text: "#f59e0b" },
  low:    { bg: "rgba(74,222,128,0.12)",   border: "rgba(74,222,128,0.35)",  text: "#22c55e" },
};

function timeAgo(ts) {
  const diff = Date.now() - ts;
  const mins  = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days  = Math.floor(diff / 86400000);
  if (mins < 1)    return "just now";
  if (mins < 60)   return `${mins}m ago`;
  if (hours < 24)  return `${hours}h ago`;
  if (days === 1)  return "yesterday";
  if (days < 7)    return `${days}d ago`;
  return new Date(ts).toLocaleString("en-IN", { month: "short", day: "numeric", year: "numeric" });
}

function ScoreRow({ label, value, max, color }) {
  const pct = max ? Math.min(100, Math.round((value / max) * 100)) : null;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "6px 0", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
      <span style={{ width: 110, fontSize: 12, color: "var(--text-muted)", flexShrink: 0 }}>{label}</span>
      {pct !== null ? (
        <>
          <div style={{ flex: 1, height: 6, background: "rgba(255,255,255,0.07)", borderRadius: 3, overflow: "hidden" }}>
            <div style={{ width: `${pct}%`, height: "100%", background: color || "var(--accent)", borderRadius: 3, transition: "width 0.8s cubic-bezier(0.4,0,0.2,1)" }} />
          </div>
          <span style={{ fontSize: 12, fontWeight: 700, color: color || "var(--accent)", minWidth: 38, textAlign: "right" }}>
            {value}/{max}
          </span>
        </>
      ) : (
        <span style={{ fontSize: 12, fontWeight: 700, color: color || "var(--text)", flex: 1 }}>{value}</span>
      )}
    </div>
  );
}

function EmpathyQuadrant({ icon, label, items, color }) {
  if (!items || items.length === 0) return null;
  return (
    <div style={{ padding: "10px 14px", background: `${color}0d`, border: `1px solid ${color}22`, borderRadius: 12 }}>
      <div style={{ fontSize: 10, fontWeight: 800, letterSpacing: 1.2, color, marginBottom: 8 }}>
        {icon} {label}
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
        {items.map((item, i) => (
          <span key={i} style={{
            background: `${color}15`, border: `1px solid ${color}30`,
            borderRadius: 20, padding: "2px 10px", fontSize: 11, color,
          }}>
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function SessionDetailModal({ session, onClose, onNewConversation }) {
  if (!session) return null;

  const riskKey  = session.risk?.toLowerCase?.() || null;
  const riskStyle = riskColor[riskKey] || { bg: "rgba(108,142,255,0.1)", border: "rgba(108,142,255,0.3)", text: "var(--accent)" };
  const empathy  = session.empathy_map || {};
  const feats    = session.features    || {};
  const pred     = session.prediction  || {};
  const confidence = pred.confidence ?? session.confidence ?? null;

  const scoreRows = [
    feats.depression_score !== undefined && { label: "Depression",  value: feats.depression_score,       max: 30, color: "#f87171" },
    feats.anxiety_score    !== undefined && { label: "Anxiety",     value: feats.anxiety_score,          max: 21, color: "#fb923c" },
    feats.stress_level     !== undefined && { label: "Stress",      value: feats.stress_level,           max: 10, color: "#fbbf24" },
    feats.sleep_hours      !== undefined && { label: "Sleep",       value: feats.sleep_hours,            max: 12, color: "#38bdf8" },
    feats.social_support_score !== undefined && { label: "Social Support", value: feats.social_support_score, max: 100, color: "#a78bfa" },
    feats.physical_activity_days !== undefined && { label: "Activity",   value: feats.physical_activity_days, max: 7,   color: "#4ade80" },
    feats.productivity_score     !== undefined && { label: "Productivity",value: feats.productivity_score, max: 100, color: "#6c8eff" },
  ].filter(Boolean);

  return (
    <div
      className="session-detail-overlay"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Session detail"
    >
      <div
        className="session-detail-modal glass"
        onClick={e => e.stopPropagation()}
      >
        {/* ── Header ── */}
        <div className="sdm-header">
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
              <span style={{ fontSize: 18 }}>
                {session.source === "hybrid" ? "🧠" : session.source === "empathy-chat" ? "💬" : "⚕️"}
              </span>
              <span className="sdm-title">Past Session</span>
              {session.crisis && (
                <span className="crisis-badge">🚨 crisis flagged</span>
              )}
            </div>
            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
              {timeAgo(session.timestamp)}
              {session.userName && <span> · {session.userName}</span>}
              {session.source && (
                <span style={{ marginLeft: 8, background: "rgba(255,255,255,0.06)", padding: "1px 8px", borderRadius: 20 }}>
                  {session.source === "hybrid" ? "Hybrid Assessment" : session.source === "empathy-chat" ? "Empathy Chat" : "Manual Form"}
                </span>
              )}
            </div>
          </div>
          <button
            className="sdm-close-btn"
            onClick={onClose}
            aria-label="Close"
          >✕</button>
        </div>

        {/* ── Snippet ── */}
        {session.snippet && (
          <div className="sdm-snippet">
            <span style={{ fontSize: 14, color: "var(--text-dim)", marginRight: 8 }}>💬</span>
            <span style={{ fontSize: 13, color: "var(--text-muted)", fontStyle: "italic" }}>
              "{session.snippet}"
            </span>
          </div>
        )}

        <div className="sdm-body">

          {/* ── Risk + Confidence ── */}
          {riskKey && (
            <div style={{ background: riskStyle.bg, border: `1px solid ${riskStyle.border}`, borderRadius: 14, padding: "16px 20px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div>
                <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 1, color: riskStyle.text, marginBottom: 4 }}>RISK LEVEL</div>
                <div style={{ fontSize: 26, fontWeight: 800, color: riskStyle.text, textTransform: "uppercase" }}>
                  {session.risk}
                </div>
              </div>
              {confidence !== null && (
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 10, color: "var(--text-dim)", letterSpacing: 1, marginBottom: 4 }}>CONFIDENCE</div>
                  <div style={{ fontSize: 26, fontWeight: 800, color: "var(--text)" }}>
                    {Math.round(confidence)}%
                  </div>
                </div>
              )}
              {(pred.summary || session.summary) && (
                <div style={{ flex: 1, marginLeft: 20, fontSize: 12, color: "var(--text-muted)", lineHeight: 1.5 }}>
                  {(pred.summary || session.summary)?.slice(0, 140)}…
                </div>
              )}
            </div>
          )}

          {/* ── Clinical Scores ── */}
          {scoreRows.length > 0 && (
            <div>
              <div className="sdm-section-label">📊 Clinical Scores</div>
              <div style={{ padding: "4px 0" }}>
                {scoreRows.map(r => <ScoreRow key={r.label} {...r} />)}
              </div>
            </div>
          )}

          {/* ── Empathy Map ── */}
          {Object.values(empathy).some(a => a?.length > 0) && (
            <div>
              <div className="sdm-section-label">📡 Empathy Map</div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                <EmpathyQuadrant icon="💬" label="SAYS"   items={empathy.says}   color="#6c8eff" />
                <EmpathyQuadrant icon="🧠" label="THINKS" items={empathy.thinks} color="#a78bfa" />
                <EmpathyQuadrant icon="🏃" label="DOES"   items={empathy.does}   color="#fbbf24" />
                <EmpathyQuadrant icon="❤️" label="FEELS"  items={empathy.feels}  color="#f87171" />
              </div>
            </div>
          )}
        </div>

        {/* ── Footer actions ── */}
        <div className="sdm-footer">
          <button className="neu-btn" onClick={onClose} style={{ padding: "9px 18px", fontSize: 13 }}>
            ← Back
          </button>
          <button
            className="btn-primary"
            onClick={() => { onClose(); onNewConversation?.(); }}
            style={{ padding: "10px 22px", fontSize: 13 }}
            id="sdm-new-convo-btn"
          >
            ✨ New Conversation
          </button>
        </div>
      </div>
    </div>
  );
}
