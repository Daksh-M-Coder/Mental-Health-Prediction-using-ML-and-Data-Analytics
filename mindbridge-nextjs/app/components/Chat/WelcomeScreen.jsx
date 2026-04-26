"use client";

/**
 * WelcomeScreen.jsx — Claude-inspired welcome/home screen shown when no session is active.
 *
 * Three variants from the plan:
 *   first-time    → "Welcome. I'm MindBridge..." (no history)
 *   returning     → "Welcome back, [Name]." (has history, no recent crisis)
 *   post-crisis   → "Thank you for coming back, [Name]." (last session had crisis)
 */

function daysSince(ts) {
  return Math.floor((Date.now() - ts) / 86400000);
}

export default function WelcomeScreen({
  userName,
  sessions,             // full history array from localStorage
  mode,
  onNewConversation,
  onSessionClick,
}) {
  const isFirstTime = sessions.length === 0;
  const lastSession = sessions[0] || null;
  const lastWascrisis = lastSession?.crisis === true;
  const daysSinceLast = lastSession ? daysSince(lastSession.timestamp) : null;

  // ── Welcome message text ──
  let headline, subtext;

  if (isFirstTime) {
    headline = "Welcome. I'm MindBridge.";
    subtext  = `I'm not a doctor, and I'm not human —\nbut I'm here to listen, 24/7, without judgment.\n\nYou can share anything, in your own words, even if it doesn't make sense.\nEven if it's dark. Especially if it's dark.\n\nTake your time. I'm not going anywhere.`;
  } else if (lastWascrisis) {
    headline = `${userName ? `${userName}, thank` : "Thank"} you for coming back.`;
    subtext  = `I know the last time we talked was hard.\nYou don't have to talk about it if you don't want to.\n\nYou're here. That matters.\nHow can I support you right now?`;
  } else if (daysSinceLast !== null && daysSinceLast >= 2) {
    headline = `Welcome back${userName ? `, ${userName}` : ""}.`;
    subtext  = `I see it's been ${daysSinceLast === 1 ? "a day" : `${daysSinceLast} days`} since we talked.\nNo pressure to explain where you've been —\nI'm just glad you're here now.\n\nHow are you feeling today?`;
  } else {
    headline = `Good to see you${userName ? `, ${userName}` : ""}.`;
    subtext  = `I'm here and ready to listen.\nHow are you feeling right now?`;
  }

  const recentSessions = sessions.slice(0, 5);

  return (
    <div className="welcome-screen">
      {/* ── Hero Text ── */}
      <div style={{ fontSize: 28, marginBottom: 16 }}>🧠</div>
      <h1 className="welcome-hero-text">{headline}</h1>
      <p className="welcome-sub-text" style={{ whiteSpace: "pre-line" }}>{subtext}</p>

      {/* ── CTA Button ── */}
      <button
        className="btn-primary warm-pulse"
        onClick={onNewConversation}
        id="welcome-new-convo-btn"
        style={{ padding: "16px 36px", fontSize: 15, borderRadius: 18 }}
      >
        ✨ {isFirstTime ? "Start a Conversation" : "New Conversation"}
      </button>

      {/* ── Mode hint ── */}
      <p style={{ marginTop: 12, fontSize: 12, color: "var(--warm-stone)" }}>
        {mode === "chat"
          ? "💬 Chat mode — just talk, no clinical analysis"
          : "🧠 ML+Hybrid mode — structured assessment with DTC prediction"}
      </p>

      {/* ── Recent Sessions ── */}
      {recentSessions.length > 0 && (
        <div className="recent-sessions-section">
          <div className="recent-section-label">Recent Conversations</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {recentSessions.map(session => (
              <div
                key={session.id}
                className="warm-card"
                onClick={() => onSessionClick(session)}
                style={{ padding: "14px 18px", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, transition: "all 0.18s" }}
                role="button"
                tabIndex={0}
                onKeyDown={e => e.key === "Enter" && onSessionClick(session)}
              >
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, color: "var(--warm-charcoal)", lineHeight: 1.4, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    🗨 &nbsp;{session.snippet || "Conversation"}
                  </div>
                  <div style={{ display: "flex", gap: 8, marginTop: 4, alignItems: "center" }}>
                    <span style={{ fontSize: 11, color: "var(--warm-stone)" }}>
                      {new Date(session.timestamp).toLocaleDateString("en-IN", { month: "short", day: "numeric" })}
                    </span>
                    {session.risk && (
                      <span className={`risk-badge ${session.risk.toLowerCase()}`}>
                        {session.risk}
                      </span>
                    )}
                    {session.crisis && <span className="crisis-badge">🚨 crisis</span>}
                  </div>
                </div>
                <span style={{ fontSize: 16, color: "var(--warm-stone)", flexShrink: 0 }}>→</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
