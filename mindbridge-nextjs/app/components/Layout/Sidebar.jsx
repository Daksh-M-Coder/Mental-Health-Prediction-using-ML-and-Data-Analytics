"use client";
import { useState } from "react";
import ModeToggle from "./ModeToggle";
import SessionCard from "../Session/SessionCard";

/**
 * Sidebar.jsx — Claude-style left sidebar
 * - Mode toggle (💬 / 🧠)
 * - New Conversation button
 * - Session list from localStorage history
 * - Bottom actions: Analytics, Manual Form, Control Panel, Theme
 */
export default function Sidebar({
  collapsed,
  mode,
  onModeChange,
  sessions,           // array from localStorage/MongoDB history
  activeSessionId,
  onSessionClick,
  onNewConversation,
  onShowAnalytics,
  onShowManual,
  onShowControlPanel,
  onThemeToggle,
  appTheme,
  onDeleteSession,
  onRenameSession,
}) {
  const [showAllSessions, setShowAllSessions] = useState(false);

  // Group sessions by recency
  const now = Date.now();
  const DAY = 86400000;

  const groupLabel = (ts) => {
    const diff = now - ts;
    if (diff < DAY)       return "Today";
    if (diff < 2 * DAY)   return "Yesterday";
    if (diff < 7 * DAY)   return "This Week";
    if (diff < 30 * DAY)  return "This Month";
    return "Older";
  };

  const grouped = {};
  const visibleSessions = showAllSessions ? sessions : sessions.slice(0, 20);
  for (const s of visibleSessions) {
    const label = groupLabel(s.timestamp);
    if (!grouped[label]) grouped[label] = [];
    grouped[label].push(s);
  }
  const groupOrder = ["Today", "Yesterday", "This Week", "This Month", "Older"];

  // Stats
  const totalSessions = sessions.length;
  const highRisk   = sessions.filter(s => s.risk?.toLowerCase() === "high").length;
  const crisisCount = sessions.filter(s => s.crisis).length;

  return (
    <div className={`sidebar${collapsed ? " collapsed" : ""}`} data-app-theme={appTheme} aria-label="Session sidebar">

      {/* ── Logo ── */}
      <div className="sidebar-logo">
        <span style={{ fontSize: 22 }}>🧠</span>
        <span className="sidebar-logo-text">MindBridge</span>
      </div>

      {/* ── Mode Toggle ── */}
      <ModeToggle mode={mode} onChange={onModeChange} />

      {/* ── New Conversation ── */}
      <button className="new-convo-btn" onClick={onNewConversation} id="sidebar-new-convo-btn">
        ✨ New Conversation
      </button>

      {/* ── Session List ── */}
      <div className="sidebar-section-label">Sessions</div>

      <div className="sidebar-sessions">
        {sessions.length === 0 ? (
          <div style={{ padding: "12px 12px 0", fontSize: 12, color: "var(--warm-stone)", fontStyle: "italic", lineHeight: 1.6 }}>
            Your conversations will appear here after your first session.
          </div>
        ) : (
          groupOrder
            .filter(g => grouped[g])
            .map(group => (
              <div key={group}>
                <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 0.8, color: "var(--warm-stone)", padding: "10px 12px 4px", textTransform: "uppercase" }}>
                  {group}
                </div>
                {grouped[group].map(session => (
                  <SessionCard
                    key={session.id}
                    session={session}
                    isActive={session.id === activeSessionId}
                    onClick={() => onSessionClick(session)}
                    onDelete={onDeleteSession}
                    onRename={onRenameSession}
                    appTheme={appTheme}
                  />
                ))}
              </div>
            ))
        )}

        {sessions.length > 20 && !showAllSessions && (
          <button
            onClick={() => setShowAllSessions(true)}
            style={{ width: "100%", padding: "8px", fontSize: 11, color: "var(--warm-terracotta)", background: "transparent", border: "1px dashed rgba(201,100,66,0.25)", borderRadius: 8, cursor: "pointer", marginTop: 4 }}
          >
            View all {sessions.length} sessions →
          </button>
        )}
      </div>

      {/* ── Stats strip ── */}
      {totalSessions > 0 && (
        <div style={{ padding: "8px 16px", display: "flex", gap: 12, fontSize: 11, color: "var(--warm-stone)", borderTop: "1px solid rgba(201,100,66,0.1)", flexShrink: 0 }}>
          <span>📊 {totalSessions} sessions</span>
          {highRisk > 0 && <span style={{ color: "#ef4444" }}>⚠️ {highRisk} high</span>}
          {crisisCount > 0 && <span style={{ color: "#ef4444" }}>🚨 {crisisCount} crisis</span>}
        </div>
      )}

      {/* ── Bottom Actions ── */}
      <div className="sidebar-bottom">
        <button className="sidebar-action-btn" onClick={onShowAnalytics} id="sidebar-analytics-btn">
          <span>📊</span> <span>Analytics</span>
        </button>
        <button className="sidebar-action-btn" onClick={onShowManual} id="sidebar-manual-btn">
          <span>📋</span> <span>Manual Assessment</span>
        </button>
        <button className="sidebar-action-btn" onClick={onShowControlPanel} id="sidebar-control-btn">
          <span>⚙️</span> <span>Control Panel</span>
        </button>
        <button className="sidebar-action-btn" onClick={onThemeToggle} id="sidebar-theme-btn">
          <span>{appTheme === "dark" ? "☀️" : "🌙"}</span>
          <span>{appTheme === "dark" ? "Light Mode" : "Dark Mode"}</span>
        </button>
      </div>
    </div>
  );
}
