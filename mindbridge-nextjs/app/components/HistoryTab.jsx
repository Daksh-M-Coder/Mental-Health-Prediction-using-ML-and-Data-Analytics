"use client";
import { useState, useEffect, useCallback } from "react";
import { getConversation } from "../lib/api";
import SessionMenu from "./Session/SessionMenu";

const C = {
  text:  "var(--c-text)",
  muted: "var(--c-muted)",
  dim:   "var(--c-dim)",
  accent:"var(--accent)",
  green: "var(--green)",
  amber: "var(--amber)",
  red:   "var(--red)",
};
const riskColor = {
  High:"var(--red)", Medium:"var(--amber)", Low:"var(--green)",
  high:"var(--red)", medium:"var(--amber)", low:"var(--green)",
};

function sourceLabel(source) {
  if (source === "empathy-chat") return "💬 Chat";
  if (source === "hybrid")       return "🧠 Hybrid";
  return "⚕ Manual";
}

// ── Conversation message thread (expandable) ───────────────────────────────
function ConversationThread({ sessionId, localMessages }) {
  const [messages, setMessages] = useState(localMessages || []);
  const [loading, setLoading]   = useState(false);
  const [loaded, setLoaded]     = useState(!!localMessages?.length);

  useEffect(() => {
    if (loaded || !sessionId) return;
    setLoading(true);
    getConversation(sessionId)
      .then(data => {
        if (data?.messages?.length) {
          setMessages(data.messages);
        }
        setLoaded(true);
      })
      .catch(() => setLoaded(true))
      .finally(() => setLoading(false));
  }, [sessionId, loaded]);

  if (loading) {
    return (
      <div style={{ padding: "12px 16px", textAlign: "center", color: C.dim, fontSize: 12 }}>
        Loading conversation…
      </div>
    );
  }

  if (!messages.length) {
    return (
      <div style={{ padding: "10px 16px", color: C.dim, fontSize: 12, fontStyle: "italic" }}>
        No conversation messages saved for this session.
      </div>
    );
  }

  return (
    <div style={{ padding: "10px 16px 14px", display: "flex", flexDirection: "column", gap: 8, borderTop: "1px solid rgba(255,255,255,0.06)" }}>
      <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 1, color: C.dim, marginBottom: 2 }}>CONVERSATION</div>
      {messages.map((msg, i) => {
        const isUser = msg.role === "user";
        return (
          <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: isUser ? "flex-end" : "flex-start" }}>
            <div style={{
              maxWidth: "88%",
              padding: "8px 12px",
              borderRadius: isUser ? "14px 14px 4px 14px" : "14px 14px 14px 4px",
              background: isUser ? "rgba(108,142,255,0.15)" : "rgba(255,255,255,0.04)",
              border: `1px solid ${isUser ? "rgba(108,142,255,0.25)" : "rgba(255,255,255,0.08)"}`,
              fontSize: 12,
              color: C.muted,
              lineHeight: 1.5,
              whiteSpace: "pre-wrap",
            }}>
              {msg.content}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ── Expandable History Row ─────────────────────────────────────────────────
function HistoryRow({ entry, index, onDelete, onRename, appTheme }) {
  const [visible, setVisible]   = useState(false);
  const [expanded, setExpanded] = useState(false);
  useEffect(() => { setTimeout(() => setVisible(true), index * 60); }, [index]);
  const color = riskColor[entry.risk] || C.accent;

  return (
    <div style={{
      border: "1px solid rgba(255,255,255,0.07)",
      borderRadius: 12,
      overflow: "hidden",
      opacity: visible ? 1 : 0,
      transform: visible ? "none" : "translateX(-20px)",
      transition: "opacity 0.4s, transform 0.4s",
      background: "rgba(255,255,255,0.03)",
    }}>
      {/* ── Summary row ── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "auto 1fr auto auto auto auto",
          alignItems: "center",
          gap: 10,
          padding: "12px 16px",
          cursor: "pointer",
        }}
        onClick={() => setExpanded(v => !v)}
      >
        {/* Risk dot */}
        <div style={{ width: 8, height: 8, borderRadius: "50%", background: color, flexShrink: 0, boxShadow: `0 0 8px ${color}` }}/>

        {/* Snippet */}
        <div style={{ overflow: "hidden" }}>
          <span style={{ color: C.muted, fontSize: 12, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", display: "block" }}>
            {entry.snippet
              ? entry.snippet.slice(0, 60)
              : `${new Date(entry.timestamp).toLocaleString()} — ${entry.employment_status || "Session"}`
            }
          </span>
        </div>

        {/* Expand chevron */}
        <span style={{ fontSize: 11, color: C.dim, transition: "transform 0.2s", transform: expanded ? "rotate(90deg)" : "none", userSelect: "none" }}>▶</span>

        {/* Source */}
        <span style={{ fontSize: 11, color: C.dim, background: "rgba(255,255,255,0.05)", borderRadius: 20, padding: "2px 8px" }}>
          {sourceLabel(entry.source)}
        </span>

        {/* Risk label */}
        <span style={{ color, fontSize: 12, fontWeight: 700, letterSpacing: 0.5 }}>{entry.risk || "—"}</span>

        {/* 3-dot menu */}
        <div onClick={e => e.stopPropagation()}>
          <SessionMenu session={entry} onDelete={onDelete} onRename={onRename} appTheme={appTheme} />
        </div>
      </div>

      {/* ── Expanded: conversation thread ── */}
      {expanded && (
        <ConversationThread sessionId={entry.id} localMessages={entry.messages} />
      )}
    </div>
  );
}

// ── Export Panel ───────────────────────────────────────────────────────────
function ExportPanel({ history }) {
  const [exported, setExported] = useState(null);

  const download = (filename, content, type) => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([content], { type }));
    a.download = filename; a.click();
    setTimeout(() => setExported(null), 3000);
  };

  const exportCSV = () => {
    if (!history.length) return;
    const headers = ["Timestamp","Source","Snippet","Risk","Confidence","Crisis"];
    const rows = history.map(h => [
      new Date(h.timestamp).toISOString(),
      h.source||"manual",
      `"${(h.snippet||"").replace(/"/g,"'")} "`,
      h.risk||"",
      Math.round(h.confidence||0),
      h.crisis?"yes":"no",
    ]);
    download("mindbridge_report.csv", [headers,...rows].map(r=>r.join(",")).join("\n"), "text/csv");
    setExported("csv");
  };

  const exportJSON = () => {
    if (!history.length) return;
    const report = {
      generated:new Date().toISOString(), system:"MindBridge AI v2.0",
      model:"Decision Tree Classifier (98.7% accuracy)", total:history.length,
      breakdown:{
        high:history.filter(h=>["High","high"].includes(h.risk)).length,
        medium:history.filter(h=>["Medium","medium"].includes(h.risk)).length,
        low:history.filter(h=>["Low","low"].includes(h.risk)).length,
      },
      assessments:history,
    };
    download("mindbridge_report.json", JSON.stringify(report,null,2), "application/json");
    setExported("json");
  };

  const exportMD = () => {
    if (!history.length) return;
    const lines = [
      "# 🧠 MindBridge AI — Assessment Report",
      `Generated: ${new Date().toLocaleString()}`, `Total: ${history.length}`,
      "","## Sessions",
      ...history.map((h,i)=>[
        `### #${i+1} — ${h.risk||"?"} Risk`,
        `**Time:** ${new Date(h.timestamp).toLocaleString()}`,
        `**Source:** ${h.source||"manual"}`,
        h.snippet ? `**Snippet:** ${h.snippet}` : "",
        h.crisis ? "⚠️ **Crisis flagged**" : "", "---",
      ].filter(Boolean).join("\n")),
    ];
    download("mindbridge_report.md", lines.join("\n"), "text/markdown");
    setExported("md");
  };

  const btns = [
    { label:"📊 CSV",  key:"csv",  fn:exportCSV,  color:C.green  },
    { label:"🔷 JSON", key:"json", fn:exportJSON, color:C.accent },
    { label:"📝 MD",   key:"md",   fn:exportMD,   color:"#a78bfa"},
  ];

  return (
    <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
      {btns.map(b => (
        <button key={b.key} onClick={b.fn} disabled={!history.length}
          style={{
            background:exported===b.key ? `${b.color}22` : "rgba(255,255,255,0.05)",
            border:`1px solid ${exported===b.key ? b.color : "rgba(255,255,255,0.1)"}`,
            borderRadius:10, padding:"8px 16px",
            color:exported===b.key ? b.color : C.muted,
            fontFamily:"'DM Sans',sans-serif", fontWeight:600, fontSize:12,
            cursor:history.length?"pointer":"not-allowed", opacity:history.length?1:0.4,
            transition:"all 0.2s",
          }}>
          {exported===b.key ? "✓ Saved!" : b.label}
        </button>
      ))}
    </div>
  );
}

// ── Main ───────────────────────────────────────────────────────────────────
export default function HistoryTab({ results, onClear, onDelete, onRename, appTheme }) {
  const history = results || [];

  return (
    <div className="fade-up">
      <div className="glass" style={{ padding:28 }}>
        <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:20 }}>
          <h2 style={{ margin:0, fontSize:18, fontWeight:600 }}>Session History ({history.length})</h2>
          <div style={{ display:"flex", gap:12, alignItems:"center" }}>
            <ExportPanel history={history}/>
            {history.length > 0 && (
              <button className="neu-btn" onClick={onClear} style={{ padding:"8px 14px", fontSize:12 }}>
                Clear All
              </button>
            )}
          </div>
        </div>

        <div style={{ fontSize:11, color:C.dim, marginBottom:16 }}>
          💡 Click any row to expand conversation messages
        </div>

        {history.length === 0 ? (
          <div style={{ textAlign:"center", padding:"60px 0", color:C.dim }}>
            <div style={{ fontSize:40, marginBottom:16 }}>📋</div>
            <div>No sessions yet. Complete an interview or assessment first.</div>
          </div>
        ) : (
          <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
            {history.map((entry, i) => (
              <HistoryRow
                key={entry.id || entry.timestamp}
                entry={entry}
                index={i}
                onDelete={onDelete}
                onRename={onRename}
                appTheme={appTheme}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
