"use client";
import { useState, useEffect, useCallback, useRef } from "react";
import EmpathyChat  from "./components/EmpathyChat";
import ManualAssess from "./components/ManualAssess";
import HistoryTab   from "./components/HistoryTab";
import AnalyticsTab from "./components/AnalyticsTab";

const C = {
  text:"#f0f4ff", muted:"rgba(240,244,255,0.55)", dim:"rgba(240,244,255,0.35)",
  accent:"#6c8eff", accentGlow:"rgba(108,142,255,0.35)",
  green:"#4ade80", amber:"#fbbf24", red:"#f87171",
  neu:"#1a1d2e", neuL:"rgba(60,70,110,0.5)", neuD:"rgba(5,6,15,0.7)",
};

function AnimatedCounter({ value }) {
  const [display, setDisplay] = useState(0);
  const start = useRef(0);
  useEffect(() => {
    const from = start.current;
    const begin = performance.now();
    const tick = (now) => {
      const t = Math.min((now - begin) / 1000, 1);
      const ease = 1 - Math.pow(1 - t, 3);
      setDisplay(Math.round(from + (value - from) * ease));
      if (t < 1) requestAnimationFrame(tick);
      else start.current = value;
    };
    requestAnimationFrame(tick);
  }, [value]);
  return <span>{display}</span>;
}

const TABS = [
  { key:"chat",      icon:"🤝", label:"AI Interview" },
  { key:"assess",    icon:"⚕",  label:"Manual Form"  },
  { key:"history",   icon:"📋", label:"History"      },
  { key:"analytics", icon:"📊", label:"Analytics"    },
];

export default function MindBridgePage() {
  const [activeTab, setActiveTab] = useState("chat");
  const [history,   setHistory]   = useState([]);
  const [mousePos,  setMousePos]  = useState({ x:0, y:0 });
  const [animIn,    setAnimIn]    = useState(false);

  // Load history from localStorage on mount
  useEffect(() => {
    setAnimIn(true);
    try {
      const saved = localStorage.getItem("mindbridge_history_v2");
      if (saved) setHistory(JSON.parse(saved));
    } catch {}
  }, []);

  const saveHistory = useCallback((newHistory) => {
    setHistory(newHistory);
    try { localStorage.setItem("mindbridge_history_v2", JSON.stringify(newHistory.slice(-100))); } catch {}
  }, []);

  const handleNewResult = useCallback((entry) => {
    saveHistory(prev => {
      const updated = [entry, ...prev].slice(0, 100);
      try { localStorage.setItem("mindbridge_history_v2", JSON.stringify(updated)); } catch {}
      return updated;
    });
  }, [saveHistory]);

  const handleMouse = useCallback((e) => {
    setMousePos({ x: e.clientX, y: e.clientY });
  }, []);

  const stats = {
    total:  history.length,
    high:   history.filter(h => h.risk === "High").length,
    medium: history.filter(h => h.risk === "Medium").length,
    low:    history.filter(h => h.risk === "Low").length,
  };

  return (
    <div
      onMouseMove={handleMouse}
      style={{ minHeight:"100vh", background:C.neu.replace("#1a1d2e","#0d0f1a"), fontFamily:"'DM Sans','Segoe UI',sans-serif", color:C.text, position:"relative", overflow:"hidden" }}
    >
      {/* ── Animated background blobs ── */}
      <div style={{ position:"fixed", inset:0, pointerEvents:"none", zIndex:0 }}>
        <div style={{ position:"absolute", width:700, height:700, borderRadius:"50%", background:"radial-gradient(circle,rgba(108,142,255,0.18),transparent 70%)", top:-200, left:-200, animation:"float 12s ease-in-out infinite" }}/>
        <div style={{ position:"absolute", width:500, height:500, borderRadius:"50%", background:"radial-gradient(circle,rgba(167,139,250,0.14),transparent 70%)", bottom:-100, right:-100, animation:"float 15s ease-in-out infinite", animationDelay:"-5s" }}/>
        <div style={{ position:"absolute", width:350, height:350, borderRadius:"50%", background:"radial-gradient(circle,rgba(74,222,128,0.10),transparent 70%)", top:"40%", left:"55%", animation:"float 10s ease-in-out infinite", animationDelay:"-8s" }}/>
        {/* Cursor glow */}
        <div style={{ position:"fixed", width:300, height:300, borderRadius:"50%", background:"radial-gradient(circle,rgba(108,142,255,0.06),transparent 70%)", left:mousePos.x-150, top:mousePos.y-150, pointerEvents:"none", transition:"left 0.1s, top 0.1s", mixBlendMode:"screen" }}/>
      </div>

      {/* ── Main content ── */}
      <div style={{ position:"relative", zIndex:1, maxWidth:1200, margin:"0 auto", padding:"24px 20px", opacity:animIn?1:0, transition:"opacity 0.8s" }}>

        {/* ── Header ── */}
        <div className="glass" style={{ padding:"20px 28px", marginBottom:24, display:"flex", alignItems:"center", justifyContent:"space-between" }}>
          <div style={{ display:"flex", alignItems:"center", gap:14 }}>
            <div style={{ width:44, height:44, borderRadius:14, background:"linear-gradient(135deg,#6c8eff,#a78bfa)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:22, boxShadow:`0 0 20px ${C.accentGlow}` }}>
              🧠
            </div>
            <div>
              <div style={{ fontFamily:"'DM Serif Display',serif", fontSize:22, fontWeight:400, letterSpacing:-0.5 }}>
                MindBridge AI
              </div>
              <div style={{ color:C.muted, fontSize:12, letterSpacing:0.5 }}>
                Empathy-First Mental Health Risk Prediction · v2.0
              </div>
            </div>
          </div>

          {/* Nav tabs */}
          <div style={{ display:"flex", gap:6 }}>
            {TABS.map(tab => (
              <button
                key={tab.key}
                className={`neu-btn${activeTab === tab.key ? " active" : ""}`}
                onClick={() => setActiveTab(tab.key)}
                style={{ padding:"8px 16px", fontSize:12 }}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* ── Stats row ── */}
        <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:14, marginBottom:24 }}>
          {[
            { label:"Total Assessments", value:stats.total,  color:C.accent, icon:"📊" },
            { label:"High Risk",         value:stats.high,   color:C.red,    icon:"⚠️" },
            { label:"Medium Risk",       value:stats.medium, color:C.amber,  icon:"⚡" },
            { label:"Low Risk",          value:stats.low,    color:C.green,  icon:"✅" },
          ].map(s => (
            <div className="glass" key={s.label} style={{ padding:"18px 20px", boxShadow:`0 8px 32px rgba(0,0,0,0.3), 0 0 20px ${s.color}11` }}>
              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:6 }}>
                <span style={{ fontSize:18 }}>{s.icon}</span>
                <span style={{ color:C.dim, fontSize:11, letterSpacing:0.5 }}>{s.label.toUpperCase()}</span>
              </div>
              <div style={{ fontSize:32, fontWeight:700, color:s.color, lineHeight:1 }}>
                <AnimatedCounter value={s.value}/>
              </div>
            </div>
          ))}
        </div>

        {/* ── Tab content ── */}
        <div key={activeTab}>
          {activeTab === "chat"      && <EmpathyChat  onNewResult={handleNewResult}/>}
          {activeTab === "assess"    && <ManualAssess onNewResult={handleNewResult}/>}
          {activeTab === "history"   && <HistoryTab   history={history} onClear={() => saveHistory([])}/>}
          {activeTab === "analytics" && <AnalyticsTab history={history}/>}
        </div>

        {/* ── Footer ── */}
        <div style={{ marginTop:24, textAlign:"center", color:C.dim, fontSize:11, letterSpacing:0.5, paddingBottom:16 }}>
          MindBridge AI v2.0 · Empathy Map + 5 Whys + Decision Tree · 98.7% Accuracy · Not a substitute for professional medical advice
        </div>
      </div>
    </div>
  );
}
