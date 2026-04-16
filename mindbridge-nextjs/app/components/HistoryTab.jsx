"use client";
import { useState, useEffect } from "react";

const C = {
  text:"#f0f4ff", muted:"rgba(240,244,255,0.55)", dim:"rgba(240,244,255,0.35)",
  accent:"#6c8eff", green:"#4ade80", amber:"#fbbf24", red:"#f87171",
};
const riskColor = { High:C.red, Medium:C.amber, Low:C.green };

function HistoryRow({ entry, index }) {
  const [visible, setVisible] = useState(false);
  useEffect(() => { setTimeout(() => setVisible(true), index * 60); }, [index]);
  const color = riskColor[entry.risk] || C.accent;
  const src = entry.source === "empathy-chat" ? "🤝 Chat" : "⚕ Manual";
  return (
    <div style={{
      display:"grid", gridTemplateColumns:"auto 1fr auto auto auto", alignItems:"center", gap:12,
      padding:"12px 16px", background:"rgba(255,255,255,0.03)", borderRadius:12,
      border:"1px solid rgba(255,255,255,0.07)",
      opacity:visible?1:0, transform:visible?"none":"translateX(-20px)",
      transition:"opacity 0.4s, transform 0.4s",
    }}>
      <div style={{ width:8, height:8, borderRadius:"50%", background:color, flexShrink:0, boxShadow:`0 0 8px ${color}` }}/>
      <div style={{ overflow:"hidden" }}>
        <span style={{ color:C.muted, fontSize:12, whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis" }}>
          {new Date(entry.timestamp).toLocaleTimeString()} — {entry.employment_status || "Unknown"}, {entry.age || "?"}y
        </span>
      </div>
      <span style={{ fontSize:11, color:C.dim, background:"rgba(255,255,255,0.05)", borderRadius:20, padding:"2px 8px" }}>{src}</span>
      <span style={{ color, fontSize:12, fontWeight:700, letterSpacing:0.5 }}>{entry.risk}</span>
      <span style={{ color:C.dim, fontSize:11 }}>{Math.round(entry.confidence)}%</span>
    </div>
  );
}

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
    const headers = ["Timestamp","Source","Age","Gender","Employment","Depression","Anxiety","Sleep","Stress","Social","Productivity","Risk","Confidence"];
    const rows = history.map(h => [
      new Date(h.timestamp).toISOString(), h.source||"manual",
      h.age,h.gender,h.employment_status,
      h.depression_score,h.anxiety_score,h.sleep_hours,h.stress_level,
      h.social_support_score,h.productivity_score,h.risk,Math.round(h.confidence),
    ]);
    download("mindbridge_report.csv", [headers,...rows].map(r=>r.join(",")).join("\n"), "text/csv");
    setExported("csv");
  };

  const exportJSON = () => {
    if (!history.length) return;
    const report = {
      generated:new Date().toISOString(), system:"MindBridge AI v2.0",
      model:"Decision Tree Classifier (98.7% accuracy)", total:history.length,
      breakdown:{ high:history.filter(h=>h.risk==="High").length, medium:history.filter(h=>h.risk==="Medium").length, low:history.filter(h=>h.risk==="Low").length },
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
      "","## Summary",
      `- High: ${history.filter(h=>h.risk==="High").length}`,
      `- Medium: ${history.filter(h=>h.risk==="Medium").length}`,
      `- Low: ${history.filter(h=>h.risk==="Low").length}`,
      "","## Assessments",
      ...history.map((h,i)=>[
        `### #${i+1} — ${h.risk} Risk (${Math.round(h.confidence)}%)`,
        `**Time:** ${new Date(h.timestamp).toLocaleString()}`,
        `**Source:** ${h.source||"manual"}`,
        `**Profile:** ${h.age}y ${h.gender}, ${h.employment_status}`,
        `**Depression:** ${h.depression_score}/30 | **Anxiety:** ${h.anxiety_score}/21`,
        h.summary ? `**Summary:** ${h.summary}` : "", "---",
      ].join("\n")),
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
            transition:"all 0.2s", backdropFilter:"blur(10px)",
          }}>
          {exported===b.key ? "✓ Saved!" : b.label}
        </button>
      ))}
    </div>
  );
}

export default function HistoryTab({ history, onClear }) {
  return (
    <div className="fade-up">
      <div className="glass" style={{ padding:28 }}>
        <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:20 }}>
          <h2 style={{ margin:0, fontSize:18, fontWeight:600 }}>Assessment History</h2>
          <div style={{ display:"flex", gap:12, alignItems:"center" }}>
            <ExportPanel history={history}/>
            {history.length > 0 && (
              <button className="neu-btn" onClick={onClear} style={{ padding:"8px 14px", fontSize:12 }}>
                Clear All
              </button>
            )}
          </div>
        </div>

        {history.length === 0 ? (
          <div style={{ textAlign:"center", padding:"60px 0", color:C.dim }}>
            <div style={{ fontSize:40, marginBottom:16 }}>📋</div>
            <div>No assessments yet. Complete an interview or manual assessment first.</div>
          </div>
        ) : (
          <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
            {history.map((entry, i) => (
              <HistoryRow key={entry.timestamp} entry={entry} index={i}/>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
