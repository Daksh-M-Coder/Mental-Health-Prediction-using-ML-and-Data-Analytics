"use client";
import { useState, useEffect, useCallback, useRef } from "react";
import dynamic from "next/dynamic";
import { deleteSession as apiDeleteSession, renameSession as apiRenameSession } from "./lib/api";


// ── Layout components ──────────────────────────────────────────────
import Sidebar from "./components/Layout/Sidebar";
import WelcomeScreen from "./components/Chat/WelcomeScreen";
import SessionDetailModal from "./components/Session/SessionDetailModal";

// ── Feature components (lazy-loaded to keep initial bundle lean) ───
const EmpathyChat   = dynamic(() => import("./components/EmpathyChat"),   { ssr: false });
const HybridAssess  = dynamic(() => import("./components/HybridAssess"),  { ssr: false });
const ManualAssess  = dynamic(() => import("./components/ManualAssess"),  { ssr: false });
const HistoryTab    = dynamic(() => import("./components/HistoryTab"),     { ssr: false });
const AnalyticsTab  = dynamic(() => import("./components/AnalyticsTab"),  { ssr: false });
const ControlPanel  = dynamic(() => import("./components/ControlPanel"),   { ssr: false });

// ─── localStorage helpers ──────────────────────────────────────────
const LS_HISTORY  = "mindbridge_results";
const LS_THEME    = "mindbridge_theme";
const LS_USERNAME = "mindbridge_username";
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5002";

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(LS_HISTORY) || "[]");
  } catch {
    return [];
  }
}

function saveToHistory(result) {
  try {
    const history = loadHistory();
    const session = {
      id:        result.id || `sess_${Date.now()}`,
      timestamp: result.timestamp || Date.now(),
      source:    result.source || "chat",
      snippet:   result.snippet || result.firstMessage || "Conversation",
      risk:      result.risk   || null,
      crisis:    result.crisis || false,
      userName:  result.userName || null,
      ...result,
    };
    const updated = [session, ...history].slice(0, 100);
    localStorage.setItem(LS_HISTORY, JSON.stringify(updated));
    return updated;
  } catch {
    return loadHistory();
  }
}

// ─── Toast system ───────────────────────────────────────────────────
let _toastId = 0;

function useToast() {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = "info", duration = 3500) => {
    const id = ++_toastId;
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), duration);
  }, []);

  const ToastContainer = () => (
    <div className="toast-container" aria-live="polite">
      {toasts.map(t => (
        <div key={t.id} className={`toast toast-${t.type}`}>
          <span>{t.message}</span>
          <button
            onClick={() => setToasts(prev => prev.filter(x => x.id !== t.id))}
            className="toast-close"
            aria-label="Dismiss"
          >×</button>
        </div>
      ))}
    </div>
  );

  return { addToast, ToastContainer };
}

// ─── Mode switch confirm dialog (replaces window.confirm) ──────────
function ModeSwitchConfirm({ newMode, onConfirm, onCancel }) {
  return (
    <div className="mode-confirm-overlay" onClick={onCancel}>
      <div className="mode-confirm-dialog glass" onClick={e => e.stopPropagation()}>
        <div style={{ fontSize: 24, marginBottom: 12 }}>
          {newMode === "hybrid" ? "🧠" : "💬"}
        </div>
        <div style={{ fontSize: 15, fontWeight: 700, color: "var(--text)", marginBottom: 8 }}>
          Switch to {newMode === "hybrid" ? "ML + Hybrid" : "Chat"} mode?
        </div>
        <div style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 20, lineHeight: 1.6 }}>
          Your current conversation will end and a new session will begin.
        </div>
        <div style={{ display: "flex", gap: 10, justifyContent: "center" }}>
          <button className="neu-btn" onClick={onCancel} style={{ padding: "9px 20px", fontSize: 13 }}>
            Cancel
          </button>
          <button className="btn-primary" onClick={onConfirm} style={{ padding: "9px 22px", fontSize: 13 }} id="mode-switch-confirm-btn">
            Switch Mode
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Sync Status Indicator ─────────────────────────────────────────
function SyncIndicator({ status }) {
  // status: "idle" | "syncing" | "synced" | "offline"
  const cfg = {
    idle:    { dot: "#8890b8", label: "",           show: false },
    syncing: { dot: "#fbbf24", label: "Syncing…",   show: true  },
    synced:  { dot: "#4ade80", label: "Synced",     show: true  },
    offline: { dot: "#f87171", label: "Local only", show: true  },
  }[status] || { dot: "#8890b8", label: "", show: false };

  if (!cfg.show) return null;

  return (
    <div className="sync-indicator" title={`MongoDB: ${cfg.label}`}>
      <div style={{ width: 6, height: 6, borderRadius: "50%", background: cfg.dot, flexShrink: 0,
        boxShadow: status === "syncing" ? `0 0 8px ${cfg.dot}` : "none",
        animation: status === "syncing" ? "pulse 1s infinite" : "none" }} />
      <span>{cfg.label}</span>
    </div>
  );
}

// ─── Modal wrapper ─────────────────────────────────────────────────
function Modal({ title, onClose, children }) {
  useEffect(() => {
    const handler = (e) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [onClose]);

  return (
    <div
      style={{ position:"fixed", inset:0, background:"rgba(0,0,0,0.55)", zIndex:1000, display:"flex", alignItems:"center", justifyContent:"center", padding:20 }}
      onClick={onClose}
    >
      <div
        className="glass"
        style={{ background:"var(--bg)", maxWidth:960, width:"100%", maxHeight:"90vh", overflow:"auto", borderRadius:20, padding:0 }}
        onClick={e => e.stopPropagation()}
      >
        <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"16px 24px", borderBottom:"1px solid var(--border)" }}>
          <span style={{ fontWeight:700, fontSize:16, color:"var(--text)" }}>{title}</span>
          <button
            onClick={onClose}
            style={{ background:"none", border:"none", fontSize:20, cursor:"pointer", color:"var(--text-muted)", lineHeight:1, padding:"4px 8px", borderRadius:8 }}
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>
        <div style={{ padding:24 }}>
          {children}
        </div>
      </div>
    </div>
  );
}

// ─── Main App ──────────────────────────────────────────────────────
export default function App() {
  const { addToast, ToastContainer } = useToast();

  // ── Theme ──
  const [appTheme, setAppTheme] = useState("dark");

  // ── Mode (chat | hybrid) ──
  const [mode, setMode] = useState("chat");
  const [pendingMode, setPendingMode] = useState(null); // for confirm dialog

  // ── Session / view state ──
  const [activeView, setActiveView]     = useState("welcome");
  const [activeSessionId, setActiveSessionId] = useState(null);

  // ── History (localStorage + MongoDB merged) ──
  const [history, setHistory] = useState([]);
  const [syncStatus, setSyncStatus] = useState("idle"); // "idle"|"syncing"|"synced"|"offline"

  // ── User name ──
  const [userName, setUserName] = useState(null);

  // ── Sidebar ──
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // ── Modals ──
  const [modal, setModal] = useState(null); // "analytics"|"manual"|"control"|"history"|null
  const [selectedSession, setSelectedSession] = useState(null); // for SessionDetailModal

  // ── Chat reset key ──
  const chatKey = useRef(0);
  const [currentChatKey, setCurrentChatKey] = useState(0);

  // ─── Load persisted state + sync MongoDB ──────────────────────────
  useEffect(() => {
    const savedTheme = localStorage.getItem(LS_THEME) || "dark";
    setAppTheme(savedTheme);
    document.documentElement.setAttribute("data-theme",     savedTheme === "light" ? "light" : "default");
    document.documentElement.setAttribute("data-app-theme", savedTheme);

    const savedName = localStorage.getItem(LS_USERNAME);
    if (savedName) setUserName(savedName);

    const local = loadHistory();
    setHistory(local);

    // Try to fetch from MongoDB and merge
    fetchAndMergeSessions(local);
  }, []);

  // ─── MongoDB session fetch + merge ──────────────────────────────
  const fetchAndMergeSessions = useCallback(async (currentLocal = null) => {
    setSyncStatus("syncing");
    try {
      const res = await fetch(`${BACKEND_URL}/sessions?limit=100`, { signal: AbortSignal.timeout(4000) });
      if (!res.ok) throw new Error("Non-2xx");
      const data = await res.json();

      if (data.source === "localStorage-only" || !data.sessions?.length) {
        // MongoDB offline or empty — use localStorage
        setSyncStatus("offline");
        return;
      }

      // Merge: build map by id, MongoDB data wins for known sessions
      const local = currentLocal ?? loadHistory();
      const merged = new Map();

      // Seed with local (oldest priority)
      for (const s of local) {
        merged.set(s.id || `ls_${s.timestamp}`, s);
      }

      // Overwrite/add MongoDB sessions
      for (const s of data.sessions) {
        const key = s.id || `db_${s.timestamp}`;
        const existing = merged.get(key);
        // Prefer MongoDB record as it has more data (features, empathy_map, etc.)
        merged.set(key, { ...existing, ...s, id: key });
      }

      // Sort by timestamp desc
      const sorted = [...merged.values()].sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0)).slice(0, 100);

      setHistory(sorted);
      // Persist merged list to localStorage as cache
      try { localStorage.setItem(LS_HISTORY, JSON.stringify(sorted)); } catch {}
      setSyncStatus("synced");

      // Auto-hide "synced" badge after 4s
      setTimeout(() => setSyncStatus("idle"), 4000);
    } catch {
      setSyncStatus("offline");
    }
  }, []);

  // ─── Theme toggle ──────────────────────────────────────────────
  const toggleTheme = useCallback(() => {
    const next = appTheme === "dark" ? "light" : "dark";
    setAppTheme(next);
    localStorage.setItem(LS_THEME, next);
    document.documentElement.setAttribute("data-theme",     next === "light" ? "light" : "default");
    document.documentElement.setAttribute("data-app-theme", next);
  }, [appTheme]);

  // ─── Mode switch (with inline confirm dialog instead of window.confirm) ──
  const handleModeChange = useCallback((newMode) => {
    if (newMode === mode) return;
    if (activeView === "chat" || activeView === "hybrid") {
      setPendingMode(newMode); // show confirm dialog
    } else {
      applyModeSwitch(newMode);
    }
  }, [mode, activeView]);

  const applyModeSwitch = useCallback((newMode) => {
    setMode(newMode);
    setActiveView("welcome");
    setActiveSessionId(null);
    setPendingMode(null);
    addToast(`Switched to ${newMode === "hybrid" ? "ML + Hybrid 🧠" : "Chat 💬"} mode`, "info");
  }, [addToast]);

  // ─── Session delete ──────────────────────────────────────────
  const handleDeleteSession = useCallback((sessionId) => {
    // Remove from local state + localStorage
    setHistory(prev => {
      const updated = prev.filter(s => s.id !== sessionId);
      try { localStorage.setItem(LS_HISTORY, JSON.stringify(updated)); } catch {}
      return updated;
    });
    // Remove from MongoDB (fire-and-forget)
    apiDeleteSession(sessionId).catch(() => {});
    addToast("Session deleted", "info");
  }, [addToast]);

  // ─── Session rename ──────────────────────────────────────────
  const handleRenameSession = useCallback((sessionId, newName) => {
    setHistory(prev => {
      const updated = prev.map(s => s.id === sessionId ? { ...s, snippet: newName } : s);
      try { localStorage.setItem(LS_HISTORY, JSON.stringify(updated)); } catch {}
      return updated;
    });
    // Persist rename to MongoDB (fire-and-forget)
    apiRenameSession(sessionId, newName).catch(() => {});
    addToast(`Renamed to "${newName}"`, "success");
  }, [addToast]);


  const handleNewConversation = useCallback(() => {
    chatKey.current += 1;
    setCurrentChatKey(chatKey.current);
    setActiveSessionId(null);
    setActiveView(mode === "hybrid" ? "hybrid" : "chat");
  }, [mode]);

  // ─── Session click → show SessionDetailModal ───────────────────
  const handleSessionClick = useCallback((session) => {
    setSelectedSession(session);
  }, []);

  // ─── New result from any assessment ───────────────────────────
  const handleNewResult = useCallback((result) => {
    const snippet = result.firstMessage || result.snippet || "Assessment completed";

    if (result.userName && !userName) {
      setUserName(result.userName);
      localStorage.setItem(LS_USERNAME, result.userName);
    }

    const enriched = {
      ...result,
      id:       `sess_${Date.now()}`,
      snippet,
      userName: result.userName || userName,
    };

    const updated = saveToHistory(enriched);
    setHistory(updated);

    // ── Progress celebration check ──
    const prev = updated.filter(s => s.id !== enriched.id && s.risk && s.depression_score !== undefined);
    if (prev.length >= 1 && enriched.depression_score !== undefined) {
      const lastDepression = prev[0].depression_score;
      const delta = lastDepression - enriched.depression_score;
      if (delta >= 3) {
        addToast(`🎉 Progress! Depression score down by ${Math.round(delta)} points since last session`, "success", 6000);
      }
      const lastAnxiety = prev[0].anxiety_score;
      const anxDelta = lastAnxiety - enriched.anxiety_score;
      if (lastAnxiety !== undefined && anxDelta >= 2) {
        addToast(`✨ Anxiety score improved by ${Math.round(anxDelta)} points`, "success", 5000);
      }
    }

    // Re-sync with MongoDB
    setTimeout(() => fetchAndMergeSessions(), 800);
  }, [userName, addToast, fetchAndMergeSessions]);

  // ── Session list for sidebar ──
  const sidebarSessions = history.slice(0, 50);

  // ── Render main content ──
  const renderMainContent = () => {
    if (activeView === "welcome") {
      return (
        <WelcomeScreen
          userName={userName}
          sessions={sidebarSessions}
          mode={mode}
          onNewConversation={handleNewConversation}
          onSessionClick={handleSessionClick}
        />
      );
    }

    if (activeView === "chat") {
      return (
        <div style={{ flex:1, overflow:"hidden", padding:"20px 24px 24px", display:"flex", flexDirection:"column" }}>
          <EmpathyChat
            key={currentChatKey}
            onNewResult={handleNewResult}
            previousSessions={history}
          />
        </div>
      );
    }

    if (activeView === "hybrid") {
      return (
        <div style={{ flex:1, overflow:"hidden", padding:"20px 24px 24px", display:"flex", flexDirection:"column" }}>
          <HybridAssess
            key={currentChatKey}
            onNewResult={handleNewResult}
          />
        </div>
      );
    }

    return null;
  };

  return (
    <div
      className="app-shell"
      data-app-theme={appTheme}
      data-theme={appTheme === "light" ? "light" : "default"}
    >
      {/* ════════════════ SIDEBAR ════════════════ */}
      <Sidebar
        collapsed={!sidebarOpen}
        mode={mode}
        onModeChange={handleModeChange}
        sessions={sidebarSessions}
        activeSessionId={activeSessionId}
        onSessionClick={handleSessionClick}
        onNewConversation={handleNewConversation}
        onShowAnalytics={() => setModal("analytics")}
        onShowManual={() => setModal("manual")}
        onShowControlPanel={() => setModal("control")}
        onThemeToggle={toggleTheme}
        appTheme={appTheme}
        onDeleteSession={handleDeleteSession}
        onRenameSession={handleRenameSession}
      />

      {/* ════════════════ MAIN CONTENT ════════════════ */}
      <div className="main-content" data-app-theme={appTheme}>

        {/* ── Top Bar ── */}
        <div className="top-bar">
          <div className="top-bar-left">
            {/* Hamburger */}
            <button
              className="hamburger-btn"
              onClick={() => setSidebarOpen(prev => !prev)}
              aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
              id="hamburger-btn"
            >
              <span/><span/><span/>
            </button>

            {/* Title */}
            <span className="top-bar-title">
              {activeView === "welcome" && "MindBridge AI"}
              {activeView === "chat"    && "💬 Chat"}
              {activeView === "hybrid"  && "🧠 ML+Hybrid"}
            </span>

            {/* Session phase badge */}
            {(activeView === "chat" || activeView === "hybrid") && (
              <span style={{ fontSize:11, color:"var(--warm-terracotta)", background:"rgba(201,100,66,0.1)", padding:"3px 10px", borderRadius:20, fontWeight:600 }}>
                Active Session
              </span>
            )}
          </div>

          {/* Right side: sync indicator + quick actions */}
          <div style={{ display:"flex", alignItems:"center", gap:10 }}>
            <SyncIndicator status={syncStatus} />

            {userName && (
              <span style={{ fontSize:12, color:"var(--warm-stone)" }}>
                👤 {userName}
              </span>
            )}
            <button
              className="neu-btn"
              onClick={() => setModal("history")}
              style={{ padding:"6px 14px", fontSize:12 }}
              id="top-bar-history-btn"
            >
              📋 History
            </button>
            <button
              className="neu-btn"
              onClick={() => setActiveView("welcome")}
              style={{ padding:"6px 14px", fontSize:12 }}
              disabled={activeView === "welcome"}
              id="top-bar-home-btn"
            >
              🏠 Home
            </button>
          </div>
        </div>

        {/* ── Main View ── */}
        <div style={{ flex:1, overflow:"hidden", display:"flex", flexDirection:"column" }}>
          {renderMainContent()}
        </div>
      </div>

      {/* ════════════════ MODALS ════════════════ */}

      {modal === "analytics" && (
        <Modal title="📊 Analytics & Insights" onClose={() => setModal(null)}>
          <AnalyticsTab results={history}/>
        </Modal>
      )}

      {modal === "manual" && (
        <Modal title="📋 Manual Assessment" onClose={() => setModal(null)}>
          <ManualAssess onNewResult={(r) => { handleNewResult(r); setModal(null); }}/>
        </Modal>
      )}

      {modal === "control" && (
        <Modal title="⚙️ Control Panel" onClose={() => setModal(null)}>
          <ControlPanel
            results={history}
            onClearHistory={() => {
              localStorage.setItem(LS_HISTORY, "[]");
              setHistory([]);
              addToast("History cleared", "info");
            }}
          />
        </Modal>
      )}

      {modal === "history" && (
        <Modal title="📋 Session History" onClose={() => setModal(null)}>
          <HistoryTab
            results={history}
            onDelete={handleDeleteSession}
            onRename={handleRenameSession}
            appTheme={appTheme}
            onClear={() => {
              localStorage.setItem(LS_HISTORY, "[]");
              setHistory([]);
              addToast("History cleared", "info");
            }}
          />
        </Modal>
      )}

      {/* ════════════ SESSION DETAIL (restore) ════════════ */}
      {selectedSession && (
        <SessionDetailModal
          session={selectedSession}
          onClose={() => setSelectedSession(null)}
          onNewConversation={handleNewConversation}
        />
      )}

      {/* ════════════ MODE SWITCH CONFIRM ════════════ */}
      {pendingMode && (
        <ModeSwitchConfirm
          newMode={pendingMode}
          onConfirm={() => applyModeSwitch(pendingMode)}
          onCancel={() => setPendingMode(null)}
        />
      )}

      {/* ════════════ TOAST CONTAINER ════════════ */}
      <ToastContainer />
    </div>
  );
}
