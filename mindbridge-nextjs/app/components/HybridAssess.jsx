"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import { ResultCard } from "./ManualAssess";
import { sendHybridTurn, sendHybridAnalyze, sendHybridScore, saveConversation } from "../lib/api";



const C = {
  text:"var(--c-text)", muted:"var(--c-muted)", dim:"var(--c-dim)",
  surface:"var(--c-surface)", border:"var(--c-border)",
  accent:"var(--accent)", accentGlow:"var(--accent-glow)",
  green:"var(--green)", amber:"var(--amber)", red:"var(--red)", purple:"var(--purple)",
};

const FACTORS = ["productivity","anxiety","social_support","depression","exercise","stress","sleep"];
const FACTOR_META = {
  productivity: { icon:"💼", label:"Productivity",    color:"#6c8eff" },
  anxiety:      { icon:"😰", label:"Anxiety",         color:"#f87171" },
  social_support:{ icon:"🤝", label:"Social Support", color:"#4ade80" },
  depression:   { icon:"🌧️", label:"Mood / Depression", color:"#a78bfa" },
  exercise:     { icon:"🏃", label:"Exercise",        color:"#fbbf24" },
  stress:       { icon:"🔥", label:"Stress",          color:"#fb923c" },
  sleep:        { icon:"🌙", label:"Sleep",            color:"#38bdf8" },
};

const OPENING = {
  role: "assistant",
  content: "Hi! I'm MindBridge Hybrid — a structured clinical interviewer. 🌿\n\nBefore we begin, could I get your name? I'd love to address you properly throughout our conversation.",
};



// ── Factor Progress Bar ──────────────────────────────────────────────────────
function FactorTree({ progress, currentFactor, whyDepth, phase, demoComplete }) {
  return (
    <div className="glass" style={{ padding:20 }}>
      {/* Demographics strip */}
      <div style={{ marginBottom:18 }}>
        <div style={{ fontSize:11, color:C.muted, fontWeight:700, letterSpacing:0.8, marginBottom:10 }}>
          PHASE 1 — DEMOGRAPHICS
        </div>
        <div style={{
          display:"flex", alignItems:"center", gap:8, padding:"10px 14px", borderRadius:10,
          background: demoComplete ? "rgba(74,222,128,0.08)" : phase==="demographics" ? "rgba(108,142,255,0.1)" : "var(--c-surface)",
          border: `1px solid ${demoComplete ? "rgba(74,222,128,0.3)" : phase==="demographics" ? "rgba(108,142,255,0.3)" : "var(--c-border)"}`,
          transition:"all 0.3s",
        }}>
          <span style={{ fontSize:16 }}>{demoComplete ? "✅" : phase==="demographics" ? "🔵" : "⬜"}</span>
          <div>
            <div style={{ fontSize:12, fontWeight:600, color:C.text }}>Background Info</div>
            <div style={{ fontSize:10, color:C.dim }}>Age, gender, employment, work env, MH history</div>
          </div>
        </div>
      </div>

      {/* Clinical factors */}
      <div style={{ fontSize:11, color:C.muted, fontWeight:700, letterSpacing:0.8, marginBottom:10 }}>
        PHASE 2 — CLINICAL DEEP DIVE
      </div>
      <div style={{ display:"flex", flexDirection:"column", gap:6 }}>
        {FACTORS.map((f, idx) => {
          const meta = FACTOR_META[f];
          const done = progress[f];
          const active = currentFactor === f && !done;
          const locked = !demoComplete && !done && !active;
          return (
            <div key={f} style={{
              padding:"10px 14px", borderRadius:10, transition:"all 0.3s",
              background: done ? "rgba(74,222,128,0.06)" : active ? `${meta.color}18` : "var(--c-surface)",
              border: `1px solid ${done ? "rgba(74,222,128,0.25)" : active ? `${meta.color}55` : "var(--c-border)"}`,
              opacity: locked ? 0.4 : 1,
            }}>
              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between" }}>
                <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                  <span style={{ fontSize:15 }}>{meta.icon}</span>
                  <div>
                    <div style={{ fontSize:12, fontWeight:600, color: done ? "var(--green)" : active ? meta.color : C.text }}>
                      {meta.label}
                    </div>
                    {active && <div style={{ fontSize:10, color:C.dim }}>depth {whyDepth}/3</div>}
                    {done && <div style={{ fontSize:10, color:"var(--green)" }}>Complete ✓</div>}
                  </div>
                </div>
                {active && (
                  <div style={{ display:"flex", gap:3 }}>
                    {[0,1,2].map(i => (
                      <div key={i} style={{
                        width:6, height:6, borderRadius:"50%",
                        background: i < whyDepth ? meta.color : "rgba(255,255,255,0.1)",
                        transition:"background 0.3s",
                        boxShadow: i < whyDepth ? `0 0 6px ${meta.color}` : "none",
                      }}/>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Empathy Map Panel ────────────────────────────────────────────────────────
function EmpathyPanel({ map, insights }) {
  const quads = [
    { key:"says",   icon:"💬", label:"SAYS",   color:"var(--accent)"  },
    { key:"thinks", icon:"🧠", label:"THINKS", color:"var(--purple)"  },
    { key:"does",   icon:"🏃", label:"DOES",   color:"var(--amber)"   },
    { key:"feels",  icon:"❤️", label:"FEELS",  color:"var(--red)"     },
  ];
  const hasData = quads.some(q => (map[q.key]||[]).length > 0);
  const ts = new Date().toISOString().slice(0,10);

  const exportMap = (fmt) => {
    if (!hasData) return;
    if (fmt === "json") {
      const blob = new Blob([JSON.stringify(map, null, 2)], { type: "application/json" });
      const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
      a.download = `empathy_map_${ts}.json`; a.click();
    } else if (fmt === "csv") {
      const rows = [["quadrant","entry"]];
      for (const [k, items] of Object.entries(map)) {
        for (const item of (items||[])) rows.push([k, `"${item.replace(/"/g,"'")}"` ]);
      }
      const blob = new Blob([rows.map(r=>r.join(",")).join("\n")], { type: "text/csv" });
      const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
      a.download = `empathy_map_${ts}.csv`; a.click();
    } else if (fmt === "md") {
      const icons = { says:"💬", thinks:"🧠", does:"🏃", feels:"❤️" };
      const lines = ["# 📡 Empathy Map", `Generated: ${new Date().toLocaleString()}`, ""];
      for (const [k, items] of Object.entries(map)) {
        lines.push(`## ${icons[k]||""} ${k.toUpperCase()}`);
        for (const item of (items||[])) lines.push(`- ${item}`);
        lines.push("");
      }
      const blob = new Blob([lines.join("\n")], { type: "text/markdown" });
      const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
      a.download = `empathy_map_${ts}.md`; a.click();
    }
  };

  return (
    <div className="glass" style={{ padding:20, display:"flex", flexDirection:"column", gap:14 }}>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between" }}>
        <div style={{ fontSize:12, fontWeight:700, color:C.muted, letterSpacing:1 }}>📡 EMPATHY MAP</div>
        {hasData && (
          <div style={{ display:"flex", gap:4 }}>
            {["json","csv","md"].map(fmt => (
              <button key={fmt} onClick={() => exportMap(fmt)} style={{
                padding:"2px 8px", borderRadius:6, fontSize:9, fontWeight:700,
                background:"rgba(108,142,255,0.08)", border:"1px solid rgba(108,142,255,0.2)",
                color:C.accent, cursor:"pointer"
              }}>↓{fmt.toUpperCase()}</button>
            ))}
          </div>
        )}
      </div>
      {quads.map(({ key, icon, label, color }) => (
        <div key={key}>
          <div style={{ display:"flex", alignItems:"center", gap:6, marginBottom:6 }}>
            <span style={{ fontSize:12 }}>{icon}</span>
            <span style={{ fontSize:10, fontWeight:700, color, letterSpacing:0.8 }}>{label}</span>
          </div>
          <div style={{ display:"flex", flexWrap:"wrap", gap:4, minHeight:22 }}>
            {(map[key]||[]).length === 0
              ? <span style={{ fontSize:10, color:C.dim, fontStyle:"italic" }}>Listening…</span>
              : (map[key]||[]).map((item,i) => (
                  <span key={i} className="emp-tag" style={{ borderColor:`${color}33`, color }}>
                    {item}
                  </span>
                ))
            }
          </div>
        </div>
      ))}
      {insights.length > 0 && (
        <div style={{ marginTop:6, borderTop:"1px solid var(--c-border)", paddingTop:12 }}>
          <div style={{ fontSize:10, fontWeight:700, color:C.dim, letterSpacing:0.8, marginBottom:8 }}>KEY INSIGHTS</div>
          {insights.slice(-3).map((ins,i) => (
            <div key={i} style={{ fontSize:11, color:C.muted, padding:"4px 0", borderBottom:"1px solid var(--c-border)", lineHeight:1.5 }}>
              💡 {ins}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Main ─────────────────────────────────────────────────────────────────────
export default function HybridAssess({ onNewResult }) {
  const [messages,       setMessages]       = useState([OPENING]);
  const [input,          setInput]          = useState("");
  const [loading,        setLoading]        = useState(false);
  const [phase,          setPhase]          = useState("demographics"); // demographics|clinical|analyzing|scoring|result
  const [currentFactor,  setCurrentFactor]  = useState(null);
  const [whyDepth,       setWhyDepth]       = useState(0);
  const [factorProgress, setFactorProgress] = useState(Object.fromEntries(FACTORS.map(f=>[f,false])));
  const [demoComplete,   setDemoComplete]   = useState(false);
  const [empathyMap,     setEmpathyMap]     = useState({says:[],thinks:[],does:[],feels:[]});
  const [insights,       setInsights]       = useState([]);
  const [analysis,       setAnalysis]       = useState(null);
  const [result,         setResult]         = useState(null);
  const [features,       setFeatures]       = useState(null);
  const [crisis,         setCrisis]         = useState(false);
  const [crisisExpanded, setCrisisExpanded] = useState(false);
  const [crisisDismissed,setCrisisDismissed]= useState(false);
  const [userName,       setUserName]       = useState(null);
  const [error,          setError]          = useState(null);
  const chatEndRef = useRef(null);
  const inputRef   = useRef(null);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior:"smooth" }); }, [messages, loading]);

  const mergeEmpathy = useCallback((incoming) => {
    if (!incoming) return;
    setEmpathyMap(prev => {
      const next = {...prev};
      for (const k of ["says","thinks","does","feels"]) {
        const fresh = (incoming[k]||[]).filter(x => !prev[k].includes(x));
        next[k] = [...prev[k], ...fresh].slice(-8);
      }
      return next;
    });
  }, []);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading || phase === "analyzing" || phase === "scoring" || phase === "result") return;

    const userMsg = { role:"user", content:text };
    const history = [...messages, userMsg];
    setMessages(history);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const res = await sendHybridTurn(
        text,
        history.slice(0,-1),
        empathyMap,
        null,
      );

      if (!res.success) throw new Error(res.detail || "API error");

      mergeEmpathy(res.empathy_map);
      if (res.user_name && !userName) setUserName(res.user_name);
      if (res.key_insight) setInsights(prev => [...prev, res.key_insight].slice(-10));
      // ── Phase / factor state ── Trust the backend directly every turn
      if (res.demographics_complete) setDemoComplete(true);
      if (res.phase) setPhase(res.phase); // always trust backend phase
      if (res.current_factor) setCurrentFactor(res.current_factor);
      if (res.why_depth != null) setWhyDepth(res.why_depth);
      if (res.factor_progress) setFactorProgress(res.factor_progress);
      if (res.crisis_detected) setCrisis(true);

      const aiMsg = { role:"assistant", content:res.reply };
      setMessages(prev => [...prev, aiMsg]);
      const fullHistory = [...history, aiMsg];

      if (res.all_factors_complete) {
        // Auto-scored by backend? use result directly
        if (res.prediction) {
          setFeatures(res.features);
          setResult(res.prediction);
          setPhase("result");
          const sessionId = `sess_${Date.now()}`;
          const rd = {
            ...res.features, ...res.prediction,
            id: sessionId,
            timestamp: Date.now(), source: "hybrid",
            userName: res.user_name || userName,
            snippet: messages.find(m => m.role === "user")?.content?.slice(0,80) || "Hybrid session",
            crisis, empathy_map: empathyMap,
          };
          onNewResult?.(rd);
          saveConversation(sessionId, [...history, aiMsg], empathyMap,
            { source: "hybrid", snippet: rd.snippet, user_name: rd.userName }
          ).catch(() => {});
        } else {
          setPhase("analyzing");
          setTimeout(() => triggerAnalysis(fullHistory), 400);
        }
      }

    } catch(e) {
      setError(`Error: ${e.message}`);
      setMessages(prev => [...prev, { role:"assistant", content:"I'm still here. Could you try sharing that again?" }]);
    }
    setLoading(false);
    inputRef.current?.focus();
  };

  const triggerAnalysis = async (history) => {
    setMessages(prev => [...prev, { role:"assistant", content:"🔬 All factors mapped. Generating your personalized analysis…" }]);
    try {
      const res = await sendHybridAnalyze(history, empathyMap, null);
      setAnalysis(res.analysis);
      setMessages(prev => [...prev, { role:"assistant", content:res.analysis }]);
      setPhase("scoring");
      setTimeout(() => triggerScore(history), 600);
    } catch(e) {
      setError(`Analysis error: ${e.message}`);
      setPhase("clinical");
    }
  };

  const triggerScore = async (history) => {
    setMessages(prev => [...prev, { role:"assistant", content:"⏳ Running clinical scoring and DTC prediction…" }]);
    try {
      const res = await sendHybridScore(history, empathyMap, null);
      setFeatures(res.features);
      setResult(res.prediction);
      setPhase("result");
      const sessionId = `sess_${Date.now()}`;
      const rd = {
        ...res.features, ...res.prediction,
        id: sessionId,
        timestamp: Date.now(), source: "hybrid",
        userName,
        snippet: messages.find(m => m.role === "user")?.content?.slice(0,80) || "Hybrid session",
        crisis, empathy_map: empathyMap,
      };
      onNewResult?.(rd);
      saveConversation(sessionId, history, empathyMap,
        { source: "hybrid", snippet: rd.snippet, user_name: userName }
      ).catch(() => {});
    } catch(e) {
      setError(`Scoring error: ${e.message}`);
      setPhase("clinical");
    }
  };

  const reset = () => {
    setMessages([OPENING]); setInput(""); setLoading(false); setPhase("demographics");
    setCurrentFactor(null); setWhyDepth(0);
    setFactorProgress(Object.fromEntries(FACTORS.map(f=>[f,false])));
    setDemoComplete(false); setEmpathyMap({says:[],thinks:[],does:[],feels:[]});
    setInsights([]); setAnalysis(null); setResult(null); setFeatures(null);
    setCrisis(false); setCrisisExpanded(false); setCrisisDismissed(false);
    setError(null);
    // Keep userName across sessions
  };

  const allDone = FACTORS.every(f => factorProgress[f]);
  const completedCount = FACTORS.filter(f => factorProgress[f]).length;

  // ── Chat bubble ────────────────────────────────────────────────────────
  const renderMsg = (msg, i) => {
    const isUser = msg.role === "user";
    return (
      <div key={i} style={{ display:"flex", flexDirection:"column", alignItems:isUser?"flex-end":"flex-start" }}>
        <div style={{ fontSize:10, color:C.dim, marginBottom:4, padding:"0 4px" }}>
          {isUser ? (userName || "You") : "MindBridge Hybrid"}
        </div>
        <div className={isUser ? "chat-bubble-user" : "chat-bubble-ai"}>
          <p style={{ fontSize:14, lineHeight:1.65, color:C.text, whiteSpace:"pre-wrap", margin:0 }}>
            {msg.content}
          </p>
        </div>
      </div>
    );
  };

  return (
    <div style={{ display:"grid", gridTemplateColumns:"1fr 280px 280px", gap:16, height:"78vh", minHeight:600 }} className="fade-up">

      {/* ── LEFT: Chat ── */}
      <div className="glass" style={{ display:"flex", flexDirection:"column", overflow:"hidden" }}>
        {/* Header */}
        <div style={{ padding:"14px 20px", borderBottom:"1px solid var(--border)", display:"flex", alignItems:"center", justifyContent:"space-between", flexShrink:0 }}>
          <div style={{ display:"flex", alignItems:"center", gap:12 }}>
            <div style={{ width:9, height:9, borderRadius:"50%", background:"var(--green)", boxShadow:"0 0 10px var(--green-glow)", animation:"pulse 2s infinite" }}/>
            <span style={{ fontSize:14, fontWeight:700 }}>Hybrid Interview{userName ? ` — ${userName}` : ""}</span>
            <span style={{
              fontSize:10, color: phase==="result" ? "var(--green)" : "var(--accent)",
              background:"rgba(108,142,255,0.1)", padding:"2px 10px", borderRadius:20,
            }}>
              {phase === "demographics" && "Demographics"}
              {phase === "clinical"     && `Factor ${completedCount+1}/${FACTORS.length}`}
              {phase === "analyzing"    && "Analyzing…"}
              {phase === "scoring"      && "Scoring…"}
              {phase === "result"       && "Complete ✓"}
            </span>
          </div>
          <button className="neu-btn" onClick={reset} style={{ padding:"5px 14px", fontSize:12 }}>New Session</button>
        </div>

        {/* Messages */}
        <div style={{ flex:1, overflowY:"auto", padding:20, display:"flex", flexDirection:"column", gap:14 }}>
          {messages.map(renderMsg)}

          {loading && (
            <div style={{ display:"flex", flexDirection:"column", alignItems:"flex-start" }}>
              <div style={{ fontSize:10, color:C.dim, marginBottom:4, paddingLeft:4 }}>MindBridge Hybrid</div>
              <div style={{ display:"flex", alignItems:"center", gap:6, padding:"12px 18px", background:"rgba(108,142,255,0.08)", border:"1px solid rgba(108,142,255,0.2)", borderRadius:"18px 18px 18px 4px" }}>
                <span style={{ color:C.muted, fontSize:12 }}>Thinking</span>
                {[0,1,2].map(i => <span key={i} className="typing-dot" style={{ animationDelay:`${i*0.15}s` }}/>)}
              </div>
            </div>
          )}

          {error && (
            <div style={{ padding:"10px 14px", background:"rgba(248,113,113,0.1)", border:"1px solid rgba(248,113,113,0.25)", borderRadius:10, color:"var(--red)", fontSize:13 }}>
              ⚠️ {error}
            </div>
          )}

          {crisis && (
            <div className="crisis-panel">
              <div style={{ color:"var(--red)", fontWeight:700, fontSize:14, marginBottom:10 }}>🚨 I'm really concerned about you right now.</div>
              <p style={{ fontSize:13, color:C.muted, lineHeight:1.6, marginBottom:0 }}>Are you safe? Do you have someone nearby?</p>
              <div className="crisis-actions">
                <button className="crisis-btn safe" onClick={() => { setCrisisDismissed(true); setCrisisExpanded(false); }}>✅ I'm safe</button>
                <button className="crisis-btn" onClick={() => setCrisisExpanded(true)}>🆘 I need help</button>
                <button className="crisis-btn talk" onClick={() => { setCrisisDismissed(true); inputRef.current?.focus(); }}>💬 Talk to me</button>
              </div>
              {crisisExpanded && (
                <div>
                  <div style={{ fontSize:12, color:C.muted, marginBottom:10, fontWeight:600 }}>Resources that can help right now:</div>
                  {[
                    { name:"iCall (India)", contact:"+91-9152987821" },
                    { name:"Vandrevala Foundation", contact:"1860-2662-345" },
                    { name:"AASRA", contact:"+91-22-27546669" },
                  ].map(r => (
                    <div key={r.name} style={{ display:"flex", justifyContent:"space-between", padding:"7px 10px", background:"rgba(248,113,113,0.07)", borderRadius:8, marginBottom:6, fontSize:13 }}>
                      <span style={{ color:C.muted }}>{r.name}</span>
                      <span style={{ color:"var(--red)", fontWeight:700 }}>{r.contact}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {phase === "result" && result && (
            <div className="glass" style={{ padding:22 }}>
              <ResultCard result={result}/>
              {features && (
                <div style={{ marginTop:16, display:"grid", gridTemplateColumns:"1fr 1fr", gap:8 }}>
                  {[ ["Depression", `${features.depression_score}/30`],
                     ["Anxiety",    `${features.anxiety_score}/21`],
                     ["Sleep",      `${features.sleep_hours}h`],
                     ["Stress",     `${features.stress_level}/10`],
                     ["Social",     `${features.social_support_score}/100`],
                     ["Activity",   `${features.physical_activity_days}d/wk`],
                  ].map(([k,v]) => (
                    <div key={k} style={{ display:"flex", justifyContent:"space-between", padding:"6px 10px", background:"var(--c-surface)", borderRadius:8, fontSize:12 }}>
                      <span style={{ color:C.muted }}>{k}</span>
                      <span style={{ color:"var(--accent)", fontWeight:700 }}>{v}</span>
                    </div>
                  ))}
                </div>
              )}
              {/* Session close ritual */}
              <div className="close-ritual" style={{ marginTop:18 }}>
                <div className="close-ritual-emoji">
                  {result.risk?.toLowerCase() === "high" ? "🌙" : crisis ? "🌙" : "💙"}
                </div>
                <p className="close-ritual-text">
                  {crisis
                    ? `${userName ? `${userName}, you` : "You"} shared some heavy things today.\nThat takes courage.\n\nYou got through today. That's enough. Rest now.`
                    : `${userName ? `I'll save this for you, ${userName}.` : "I'll save this conversation for you."}\n\nYou're not alone in this. Come back anytime — I'll be here. 💙`
                  }
                </p>
              </div>
            </div>
          )}

          <div ref={chatEndRef}/>
        </div>

        {/* Input */}
        <div style={{ padding:"14px 20px", borderTop:"1px solid var(--border)", flexShrink:0 }}>
          {(phase === "demographics" || phase === "clinical") && !crisis && (
            <div style={{ display:"flex", gap:10, alignItems:"flex-end" }}>
              <textarea
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if(e.key==="Enter" && !e.shiftKey){ e.preventDefault(); sendMessage(); } }}
                placeholder={
                  phase==="demographics"
                    ? "Tell me about yourself… (Hinglish is fine too)"
                    : currentFactor
                      ? `Sharing about ${FACTOR_META[currentFactor]?.label || currentFactor}…`
                      : "Share your thoughts…"
                }
                disabled={loading}
                rows={2}
                style={{
                  flex:1, background:"var(--c-surface)", border:"1px solid var(--border)", borderRadius:14,
                  padding:"11px 14px", color:C.text, fontFamily:"'DM Sans',sans-serif",
                  fontSize:14, outline:"none", resize:"none", lineHeight:1.5,
                }}
              />
              <button
                className="btn-primary"
                onClick={sendMessage}
                disabled={!input.trim() || loading}
                style={{ padding:"13px 20px", borderRadius:14, fontSize:18, flexShrink:0 }}
              >→</button>
            </div>
          )}
          {(phase === "analyzing" || phase === "scoring") && (
            <div style={{ textAlign:"center", color:C.muted, fontSize:13, display:"flex", alignItems:"center", justifyContent:"center", gap:10 }}>
              <span style={{ display:"inline-block", width:14, height:14, border:"2px solid rgba(108,142,255,0.3)", borderTop:"2px solid var(--accent)", borderRadius:"50%", animation:"spin 0.8s linear infinite" }}/>
              {phase==="analyzing" ? "Generating personalized analysis…" : "Running DTC prediction…"}
            </div>
          )}
          {phase === "result" && (
            <button className="btn-primary" onClick={reset} style={{ width:"100%", padding:"12px 0" }}>
              🔄 Start New Hybrid Interview
            </button>
          )}
          {(phase === "demographics" || phase === "clinical") && !crisis && (
            <div style={{ marginTop:7, fontSize:11, color:C.dim, textAlign:"center" }}>
              Enter · Shift+Enter for new line · {FACTORS.length - completedCount} factor{FACTORS.length-completedCount!==1?"s":""} remaining
            </div>
          )}
        </div>
      </div>

      {/* ── MIDDLE: Factor Tree ── */}
      <div style={{ overflowY:"auto" }}>
        <FactorTree
          progress={factorProgress}
          currentFactor={currentFactor}
          whyDepth={whyDepth}
          phase={phase}
          demoComplete={demoComplete}
        />
      </div>

      {/* ── RIGHT: Empathy Map ── */}
      <div style={{ overflowY:"auto" }}>
        <EmpathyPanel map={empathyMap} insights={insights}/>
      </div>
    </div>
  );
}
