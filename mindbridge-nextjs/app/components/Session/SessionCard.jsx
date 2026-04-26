"use client";
import SessionMenu from "./SessionMenu";

/**
 * SessionCard.jsx — Individual session preview in the sidebar.
 * Shows: snippet of first user message, timestamp, risk badge, crisis flag.
 * Has 3-dot menu: Rename, Export JSON, Delete.
 */

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
  return new Date(ts).toLocaleDateString("en-IN", { month: "short", day: "numeric" });
}

export default function SessionCard({ session, isActive, onClick, onDelete, onRename, appTheme }) {
  const riskLevel = session.risk?.toLowerCase?.() || null;

  return (
    <div
      className={`session-card${isActive ? " active" : ""}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={e => e.key === "Enter" && onClick()}
      aria-current={isActive ? "true" : undefined}
    >
      {/* Snippet — first user message */}
      <div className="session-card-snippet">
        {session.snippet || "New conversation"}
      </div>

      {/* Meta row */}
      <div className="session-card-meta">
        <span className="session-card-time">{timeAgo(session.timestamp)}</span>

        {/* Source badge */}
        <span style={{ fontSize: 9, color: "var(--warm-stone)", background: "rgba(201,100,66,0.08)", padding: "1px 6px", borderRadius: 20 }}>
          {session.source === "hybrid" ? "🧠" : "💬"}
        </span>

        {/* Risk badge */}
        {riskLevel && (
          <span className={`risk-badge ${riskLevel}`}>
            {riskLevel}
          </span>
        )}

        {/* Crisis flag */}
        {session.crisis && (
          <span className="crisis-badge">🚨 crisis</span>
        )}

        {/* 3-dot menu — right-aligned */}
        <div style={{ marginLeft: "auto" }}>
          <SessionMenu
            session={session}
            onDelete={onDelete}
            onRename={onRename}
            appTheme={appTheme}
          />
        </div>
      </div>
    </div>
  );
}
