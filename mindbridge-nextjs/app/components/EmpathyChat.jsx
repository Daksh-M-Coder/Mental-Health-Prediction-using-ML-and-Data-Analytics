"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import { sendInterviewMessage, scoreConversation, predictFromFeatures, saveConversation } from "../lib/api";
import { ResultCard } from "./ManualAssess";

// ── Empathy Map Export helper ─────────────────────────────────────────────────
function exportEmpathyMap(empathyMap, format) {
  const ts = new Date().toISOString().slice(0,10);
  if (format === "json") {
    const blob = new Blob([JSON.stringify(empathyMap, null, 2)], { type: "application/json" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
    a.download = `empathy_map_${ts}.json`; a.click();
  } else if (format === "csv") {
    const rows = [["quadrant","entry"]];
    for (const [k, items] of Object.entries(empathyMap)) {
      for (const item of (items || [])) rows.push([k, `"${item.replace(/"/g, "'")}"`]);
    }
    const blob = new Blob([rows.map(r=>r.join(",")).join("\n")], { type: "text/csv" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
    a.download = `empathy_map_${ts}.csv`; a.click();
  } else if (format === "md") {
    const icons = { says:"💬", thinks:"🧠", does:"🏃", feels:"❤️" };
    const lines = ["# 📡 Empathy Map Export", `Generated: ${new Date().toLocaleString()}`, ""];
    for (const [k, items] of Object.entries(empathyMap)) {
      lines.push(`## ${icons[k]||""} ${k.toUpperCase()}`);
      for (const item of (items || [])) lines.push(`- ${item}`);
      lines.push("");
    }
    const blob = new Blob([lines.join("\n")], { type: "text/markdown" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
    a.download = `empathy_map_${ts}.md`; a.click();
  }
}

const C = {
  // These are CSS var() refs — auto-adapt to light/dark theme
  text:   "var(--c-text)",
  muted:  "var(--c-muted)",
  dim:    "var(--c-dim)",
  surface:"var(--c-surface)",
  border: "var(--c-border)",
  // Status colours — stay vivid in both themes
  accent: "var(--accent)",  accentGlow: "var(--accent-glow)",
  green:  "var(--green)",   amber: "var(--amber)",
  red:    "var(--red)",     purple: "var(--purple)",
};

const EMPATHY_CONFIG = {
  says:   { icon:"💬", label:"SAYS",   color:C.accent,  desc:"Key phrases & slang" },
  thinks: { icon:"🧠", label:"THINKS", color:C.purple,  desc:"Beliefs & distortions" },
  does:   { icon:"🏃", label:"DOES",   color:C.amber,   desc:"Behaviors & actions" },
  feels:  { icon:"❤️", label:"FEELS",  color:C.red,     desc:"Emotional state" },
};

const CRISIS_RESOURCES = [
  { name:"iCall (India)",          contact:"+91-9152987821" },
  { name:"Vandrevala Foundation",  contact:"1860-2662-345" },
  { name:"AASRA",                  contact:"+91-22-27546669" },
  { name:"Crisis Text Line (US)",  contact:"Text HOME to 741741" },
];

const OPENING_MESSAGE = {
  role: "assistant",
  content: "Hi, I'm MindBridge. I'm here to listen without any judgment. 🌱\n\nHow have you been feeling lately? You can share anything — in your own words, even if it's in Hindi, Hinglish, or whatever feels natural.",
};

function TypingIndicator() {
  return (
    <div style={{ display:"flex", alignItems:"center", gap:6, padding:"12px 18px", background:"rgba(108,142,255,0.08)", border:"1px solid rgba(108,142,255,0.2)", borderRadius:"18px 18px 18px 4px", width:"fit-content" }}>
      <span style={{ color:C.muted, fontSize:12, marginRight:4 }}>MindBridge is thinking</span>
      {[0,1,2].map(i => <span key={i} className="typing-dot" style={{ animationDelay:`${i*0.15}s` }}/>)}
    </div>
  );
}

// ── Premium Animated Empathy Map Panel ───────────────────────────────────────

const ANIM_DURATION = 320;
const PANEL_W = 292;

function EmpathyTag({ item, color, isNew, delay = 0 }) {
  return (
    <span
      className="emp-tag"
      style={{
        borderColor: `${color}40`,
        color,
        background: `${color}0d`,
        fontWeight: 500,
        animation: isNew
          ? `empTagPop 0.5s cubic-bezier(0.34,1.56,0.64,1) ${delay}ms both`
          : "none",
      }}
    >
      {item}
    </span>
  );
}

function EmpathyMapPanel({ empathyMap, confidencePct, turnCount, visible, onToggle }) {
  const prevMapRef = useRef({});
  const [flashKeys, setFlashKeys] = useState({});

  // Detect newly added items per quadrant → glow flash
  useEffect(() => {
    const newFlash = {};
    for (const key of ["says","thinks","does","feels"]) {
      const prev = prevMapRef.current[key] || [];
      const curr = empathyMap[key] || [];
      if (curr.length > prev.length) newFlash[key] = true;
    }
    if (Object.keys(newFlash).length > 0) {
      setFlashKeys(newFlash);
      const t = setTimeout(() => {
        setFlashKeys({});
        prevMapRef.current = {
          says:   [...(empathyMap.says   || [])],
          thinks: [...(empathyMap.thinks || [])],
          does:   [...(empathyMap.does   || [])],
          feels:  [...(empathyMap.feels  || [])],
        };
      }, 1000);
      return () => clearTimeout(t);
    }
  }, [empathyMap]);

  // New-item sets for staggered tag animation
  const newItemSets = {};
  for (const key of ["says","thinks","does","feels"]) {
    const prev = new Set(prevMapRef.current[key] || []);
    newItemSets[key] = (empathyMap[key] || []).filter(x => !prev.has(x));
  }

  const hasData = Object.values(empathyMap).some(a => a.length > 0);
  const totalTags = Object.values(empathyMap).reduce((s,a) => s + a.length, 0);

  return (
    // Wrapper: flex row — toggle pill + panel slide
    <div style={{ display:"flex", alignItems:"stretch", flexShrink:0 }}>

      {/* ── Toggle pill — ALWAYS rendered outside overflow:hidden ── */}
      <button
        onClick={onToggle}
        title={visible ? "Collapse Empathy Map" : "Expand Empathy Map"}
        aria-label={visible ? "Collapse empathy map" : "Expand empathy map"}
        style={{
          alignSelf: "center",
          width: 24,
          height: 72,
          background: visible
            ? `linear-gradient(180deg, ${C.purple}, ${C.accent})`
            : `linear-gradient(180deg, ${C.accent}, ${C.purple})`,
          border: "none",
          borderRadius: visible ? "8px 0 0 8px" : "0 8px 8px 0",
          color: "#fff",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 11,
          writingMode: "vertical-rl",
          letterSpacing: 1,
          boxShadow: visible
            ? `0 0 16px ${C.purple}55`
            : `0 0 16px ${C.accent}55`,
          transition: "all 0.3s cubic-bezier(0.4,0,0.2,1)",
          flexShrink: 0,
          order: visible ? 0 : 1,
        }}
      >
        {visible ? "▶" : "◀"}
      </button>

      {/* ── Sliding panel ── */}
      <div style={{
        width: visible ? PANEL_W : 0,
        minWidth: visible ? PANEL_W : 0,
        overflow: "hidden",
        transition: `width ${ANIM_DURATION}ms cubic-bezier(0.4,0,0.2,1), min-width ${ANIM_DURATION}ms cubic-bezier(0.4,0,0.2,1)`,
        flexShrink: 0,
      }}>
        <div
          className="glass"
          style={{
            width: PANEL_W,
            height: "100%",
            display: "flex",
            flexDirection: "column",
            gap: 10,
            padding: "16px 14px",
            overflow: "hidden",
            opacity: visible ? 1 : 0,
            transition: `opacity ${ANIM_DURATION}ms ease`,
            background: "linear-gradient(160deg, rgba(108,142,255,0.07) 0%, rgba(167,139,250,0.05) 100%)",
          }}
        >
          {/* ── Header ── */}
          <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", flexShrink:0 }}>
            <div style={{ display:"flex", alignItems:"center", gap:6 }}>
              <span style={{ fontSize:14 }}>📡</span>
              <span style={{ fontSize:11, fontWeight:800, color:C.accent, letterSpacing:1.2 }}>EMPATHY MAP</span>
            </div>
            <div style={{ display:"flex", gap:8, alignItems:"center" }}>
              {totalTags > 0 && (
                <span style={{ fontSize:10, color:C.purple, background:`${C.purple}18`, padding:"1px 8px", borderRadius:20, fontWeight:600 }}>
                  {totalTags} signals
                </span>
              )}
              <span style={{ fontSize:10, color:C.dim }}>{turnCount}t</span>
            </div>
          </div>

          {/* ── 4 Quadrants ── */}
          <div style={{ display:"flex", flexDirection:"column", gap:8, flex:1, overflow:"hidden" }}>
            {Object.entries(EMPATHY_CONFIG).map(([key, cfg]) => {
              const items = empathyMap[key] || [];
              const isFlashing = flashKeys[key];
              const newItems = new Set(newItemSets[key] || []);
              return (
                <div
                  key={key}
                  style={{
                    borderRadius: 12,
                    padding: "9px 11px",
                    background: isFlashing
                      ? `linear-gradient(135deg, ${cfg.color}22, ${cfg.color}0a)`
                      : "rgba(255,255,255,0.03)",
                    border: `1px solid ${isFlashing ? cfg.color + "66" : cfg.color + "18"}`,
                    boxShadow: isFlashing ? `0 0 16px ${cfg.color}33, inset 0 0 12px ${cfg.color}11` : "none",
                    transition: "all 0.45s cubic-bezier(0.4,0,0.2,1)",
                    flex: items.length > 2 ? "1 1 auto" : "0 0 auto",
                  }}
                >
                  {/* Quadrant header */}
                  <div style={{ display:"flex", alignItems:"center", gap:5, marginBottom:6 }}>
                    <span style={{ fontSize:13 }}>{cfg.icon}</span>
                    <span style={{
                      fontSize:9, fontWeight:800, letterSpacing:1.2,
                      color: cfg.color,
                      textShadow: isFlashing ? `0 0 8px ${cfg.color}` : "none",
                    }}>
                      {cfg.label}
                    </span>
                    {isFlashing && (
                      <span style={{
                        fontSize:8, color:cfg.color, fontWeight:700,
                        background:`${cfg.color}22`, padding:"1px 5px", borderRadius:10,
                        animation:"pulse 0.6s infinite",
                      }}>
                        ● NEW
                      </span>
                    )}
                  </div>
                  {/* Tags */}
                  <div style={{ display:"flex", flexWrap:"wrap", gap:4, minHeight:20 }}>
                    {items.length > 0
                      ? items.map((item, i) => (
                          <EmpathyTag
                            key={`${key}-${item}`}
                            item={item}
                            color={cfg.color}
                            isNew={newItems.has(item)}
                            delay={i * 40}
                          />
                        ))
                      : <span style={{ fontSize:9, color:C.dim, fontStyle:"italic" }}>Listening…</span>
                    }
                  </div>
                </div>
              );
            })}
          </div>

          {/* ── Confidence bar ── */}
          <div style={{ flexShrink:0, paddingTop:4 }}>
            <div style={{ display:"flex", justifyContent:"space-between", marginBottom:5 }}>
              <span style={{ fontSize:9, color:C.dim, fontWeight:600, letterSpacing:0.8 }}>CONFIDENCE</span>
              <span style={{
                fontSize:11, fontWeight:800, color:C.accent,
                textShadow: confidencePct >= 60 ? `0 0 8px ${C.accent}` : "none",
              }}>
                {confidencePct}%
              </span>
            </div>
            <div style={{ height:8, borderRadius:4, background:"rgba(255,255,255,0.06)", overflow:"hidden", position:"relative" }}>
              <div style={{
                height:"100%", borderRadius:4,
                background: `linear-gradient(90deg, ${C.accent}, ${C.purple})`,
                width:`${confidencePct}%`,
                boxShadow: `0 0 12px ${C.accentGlow}`,
                transition: "width 1s cubic-bezier(0.4,0,0.2,1)",
              }}/>
              {/* Sheen effect */}
              <div style={{
                position:"absolute", top:0, left:0, right:0, height:"50%",
                background:"linear-gradient(180deg,rgba(255,255,255,0.15),transparent)",
                borderRadius:"4px 4px 0 0", pointerEvents:"none",
              }}/>
            </div>
            {confidencePct >= 60 && (
              <div style={{ marginTop:5, fontSize:9, color:C.green, display:"flex", alignItems:"center", gap:4, fontWeight:600 }}>
                <span style={{ width:5, height:5, borderRadius:"50%", background:C.green, display:"inline-block", animation:"pulse 2s infinite" }}/>
                Ready to score
              </div>
            )}
          </div>

          {/* ── 5 Whys depth track ── */}
          <div style={{ flexShrink:0 }}>
            <div style={{ fontSize:9, color:C.dim, marginBottom:5, fontWeight:600, letterSpacing:0.8 }}>DEPTH</div>
            <div style={{ display:"flex", gap:3 }}>
              {[0,1,2,3,4].map(i => {
                const lit = i < Math.min(turnCount, 5);
                return (
                  <div key={i} style={{
                    flex:1, height:5, borderRadius:3,
                    background: lit ? C.purple : "rgba(255,255,255,0.08)",
                    boxShadow: lit ? `0 0 8px ${C.purple}` : "none",
                    transition: "background 0.5s, box-shadow 0.5s",
                  }}/>
                );
              })}
            </div>
          </div>

          {/* Empty state */}
          {!hasData && (
            <div style={{ textAlign:"center", color:C.dim, fontSize:10, fontStyle:"italic", paddingBottom:4 }}>
              Share how you're feeling to begin…
            </div>
          )}

          {/* ── Empathy Map Export ── */}
          {hasData && (
            <div style={{ flexShrink: 0, paddingTop: 6, borderTop: "1px solid rgba(255,255,255,0.06)" }}>
              <div style={{ fontSize: 9, color: C.dim, fontWeight: 600, letterSpacing: 0.8, marginBottom: 6 }}>EXPORT MAP</div>
              <div style={{ display: "flex", gap: 5 }}>
                {["json","csv","md"].map(fmt => (
                  <button
                    key={fmt}
                    onClick={() => exportEmpathyMap(empathyMap, fmt)}
                    style={{
                      flex: 1, padding: "4px 0", borderRadius: 8, fontSize: 9, fontWeight: 700,
                      background: "rgba(108,142,255,0.08)", border: "1px solid rgba(108,142,255,0.2)",
                      color: C.accent, cursor: "pointer", transition: "all 0.15s", letterSpacing: 0.5,
                    }}
                    title={`Export empathy map as .${fmt}`}
                  >
                    .{fmt.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ScoringOverlay({ features, onPredict }) {
  return (
    <div style={{ border:"1px solid rgba(108,142,255,0.3)", borderRadius:16, padding:20, background:"rgba(108,142,255,0.06)", marginBottom:16 }}>
      <div style={{ fontWeight:700, fontSize:14, marginBottom:12, color:C.accent }}>⚡ Clinical Scores Extracted</div>
      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:8, marginBottom:14 }}>
        {[
          ["Depression", `${features.depression_score}/30`],
          ["Anxiety",    `${features.anxiety_score}/21`],
          ["Sleep",      `${features.sleep_hours}h/night`],
          ["Stress",     `${features.stress_level}/10`],
          ["Social",     `${features.social_support_score}/100`],
          ["Activity",   `${features.physical_activity_days}d/wk`],
        ].map(([k, v]) => (
          <div key={k} style={{ display:"flex", justifyContent:"space-between", fontSize:12, padding:"4px 8px", background:"rgba(255,255,255,0.04)", borderRadius:8 }}>
            <span style={{ color:C.muted }}>{k}</span>
            <span style={{ color:C.accent, fontWeight:600 }}>{v}</span>
          </div>
        ))}
      </div>
      <button className="btn-primary" style={{ width:"100%", padding:"12px 20px", fontSize:14 }} onClick={onPredict}>
        🎯 Run DTC Prediction
      </button>
    </div>
  );
}

// ── Progress Celebration Banner ──────────────────────────────────────────────

function ProgressCelebration({ current, previous }) {
  if (!previous || !current) return null;

  const depDelta  = (previous.depression_score ?? null) !== null ? Math.round((previous.depression_score - (current.depression_score ?? previous.depression_score))) : 0;
  const anxDelta  = (previous.anxiety_score    ?? null) !== null ? Math.round((previous.anxiety_score    - (current.anxiety_score    ?? previous.anxiety_score)))    : 0;
  const sleepDelta= (previous.sleep_hours      ?? null) !== null ? Math.round(((current.sleep_hours ?? previous.sleep_hours) - previous.sleep_hours) * 10) / 10 : 0;

  const improvements = [
    depDelta  >= 3 && { icon: "🧠", label: "Depression",  delta: `−${depDelta} pts`, positive: true },
    anxDelta  >= 2 && { icon: "💛", label: "Anxiety",     delta: `−${anxDelta} pts`, positive: true },
    sleepDelta >= 0.5 && { icon: "😴", label: "Sleep",   delta: `+${sleepDelta}h`,  positive: true },
  ].filter(Boolean);

  if (improvements.length === 0) return null;

  return (
    <div className="progress-celebration" style={{ marginTop: 16, marginBottom: 4 }}>
      <div className="progress-celebration-icon">🎉</div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: C.green, marginBottom: 6 }}>
          Progress since last session!
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {improvements.map((item, i) => (
            <div key={i} style={{
              display: "flex", alignItems: "center", gap: 5,
              background: `${C.green}15`, border: `1px solid ${C.green}30`,
              borderRadius: 20, padding: "3px 12px", fontSize: 11,
            }}>
              <span>{item.icon}</span>
              <span style={{ color: C.green, fontWeight: 600 }}>{item.label}: {item.delta}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function EmpathyChat({ onNewResult, previousSessions = [] }) {
  const [messages, setMessages] = useState([OPENING_MESSAGE]);
  const [input, setInput]       = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [phase, setPhase]       = useState("interview"); // interview | scoring | predicting | result
  const [empathyMap, setEmpathyMap] = useState({ says:[], thinks:[], does:[], feels:[] });
  const [confidencePct, setConfidencePct] = useState(0);
  const [features, setFeatures] = useState(null);
  const [result, setResult]     = useState(null);
  const [crisisDetected, setCrisisDetected] = useState(false);
  const [crisisDismissed, setCrisisDismissed] = useState(false); // user clicked "I'm safe"
  const [crisisExpanded, setCrisisExpanded]  = useState(false);  // user clicked "I need help"
  const [error, setError]       = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);
  const [userName, setUserName] = useState(null); // collected from LLM
  const [mapVisible, setMapVisible] = useState(true); // empathy map collapsible
  const chatEndRef = useRef(null);
  const inputRef   = useRef(null);

  const turnCount = messages.filter(m => m.role === "user").length;

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior:"smooth" });
  }, [messages, isTyping]);

  // Merge empathy map updates (accumulate, don't replace)
  const mergeEmpathyMap = useCallback((incoming) => {
    if (!incoming) return;
    setEmpathyMap(prev => {
      const next = { ...prev };
      for (const key of ["says","thinks","does","feels"]) {
        const newItems = (incoming[key] || []).filter(item => !prev[key].includes(item));
        next[key] = [...prev[key], ...newItems].slice(-8); // keep last 8 per quadrant
      }
      return next;
    });
  }, []);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || isTyping || phase !== "interview") return;

    const userMsg = { role:"user", content:text };
    const history = [...messages, userMsg];
    setMessages(history);
    setInput("");
    setIsTyping(true);
    setError(null);

    try {
      const res = await sendInterviewMessage(text, history, selectedModel);

      mergeEmpathyMap(res.empathy_map);
      setConfidencePct(res.confidence_pct || 0);

      const aiMsg = { role:"assistant", content:res.reply };
      setMessages(prev => [...prev, aiMsg]);

      // Track user name once the LLM collects it
      if (res.user_name && !userName) setUserName(res.user_name);

      if (res.crisis_detected) {
        setCrisisDetected(true);
        // Don't change phase — conversation continues per project philosophy
      } else if (res.ready_to_score) {
        if (res.prediction) {
          // Auto-triggered by backend — result already in response
          setFeatures(res.features);
          setResult(res.prediction);
          setPhase("result");
          onNewResult?.({
            ...res.features, ...res.prediction,
            timestamp: Date.now(), source: "empathy-chat",
            userName: res.user_name || userName,
            snippet: messages.find(m => m.role === "user")?.content?.slice(0, 80) || "Chat session",
            crisis: false,
          });
        } else {
          setPhase("scoring");
          await triggerScore([...history, aiMsg]);
        }
      }
    } catch (e) {
      setError(`Interview error: ${e.message}`);
      // Add fallback message
      setMessages(prev => [...prev, { role:"assistant", content:"I'm here with you. Could you tell me a bit more about how you've been feeling?" }]);
    }
    setIsTyping(false);
    inputRef.current?.focus();
  };

  const triggerScore = async (conversationHistory) => {
    setPhase("scoring");
    setIsTyping(true);

    try {
      const scoreRes = await scoreConversation(conversationHistory, empathyMap, selectedModel);
      setFeatures(scoreRes.features);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "I've gathered enough to understand your situation. Let me now analyze your patterns and generate a clinical assessment... 🔬",
      }]);
      setPhase("review");
    } catch (e) {
      setError(`Scoring error: ${e.message}`);
      setPhase("interview");
    }
    setIsTyping(false);
  };

  const runPrediction = async () => {
    if (!features) return;
    setPhase("predicting");

    try {
      const predRes = await predictFromFeatures(features);
      setResult(predRes);
      setPhase("result");
      const sessionId = `sess_${Date.now()}`;
      const resultData = {
        ...features, ...predRes,
        id: sessionId,
        timestamp: Date.now(), source: "empathy-chat",
        userName,
        snippet: messages.find(m => m.role === "user")?.content?.slice(0, 80) || "Chat session",
        crisis: crisisDetected,
        empathy_map: empathyMap,
      };
      onNewResult?.(resultData);
      // Persist full conversation to MongoDB
      saveConversation(
        sessionId,
        messages,
        empathyMap,
        { source: "empathy-chat", snippet: resultData.snippet, user_name: userName }
      ).catch(() => {}); // fire-and-forget
      setMessages(prev => [...prev, {
        role: "assistant",
        content: `Based on everything you shared, here's your assessment. Risk level: **${predRes.risk}** with ${Math.round(predRes.confidence)}% confidence.\n\n${predRes.summary}`,
      }]);
    } catch (e) {
      setError(`Prediction error: ${e.message}`);
      setPhase("review");
    }
  };

  const resetChat = () => {
    setMessages([OPENING_MESSAGE]);
    setInput(""); setIsTyping(false); setPhase("interview");
    setEmpathyMap({ says:[], thinks:[], does:[], feels:[] });
    setConfidencePct(0); setFeatures(null); setResult(null);
    setCrisisDetected(false); setCrisisDismissed(false); setCrisisExpanded(false);
    setError(null);
    // Note: we intentionally keep userName across sessions so we don't ask every time
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  return (
    <div style={{ display:"flex", gap:20, height:"75vh", minHeight:600, position:"relative" }} className="fade-up">

      {/* LEFT: Chat panel — takes remaining space */}
      <div className="glass" style={{ display:"flex", flexDirection:"column", overflow:"hidden", flex:1, minWidth:0 }}>
        {/* Chat header */}
        <div style={{ padding:"16px 20px", borderBottom:"1px solid var(--border)", display:"flex", alignItems:"center", justifyContent:"space-between", flexShrink:0 }}>
          <div style={{ display:"flex", alignItems:"center", gap:10 }}>
            <div style={{ width:10, height:10, borderRadius:"50%", background:C.green, boxShadow:`0 0 10px ${C.green}`, animation:"pulse 2s infinite" }}/>
            <span style={{ fontSize:14, fontWeight:600 }}>Empathy Interview{userName ? ` — ${userName}` : ""}</span>
            <span style={{ fontSize:11, color:C.dim, background:"rgba(255,255,255,0.05)", borderRadius:20, padding:"2px 10px" }}>
              {phase === "interview" ? `Turn ${turnCount}` : phase.toUpperCase()}
            </span>
          </div>
          <button className="neu-btn" onClick={resetChat} style={{ padding:"6px 14px", fontSize:12 }}>
            New Chat
          </button>
        </div>

        {/* Messages */}
        <div style={{ flex:1, overflowY:"auto", padding:"20px", display:"flex", flexDirection:"column", gap:16 }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ display:"flex", flexDirection:"column", alignItems:msg.role === "user" ? "flex-end" : "flex-start" }}>
              <div style={{ fontSize:10, color:C.dim, marginBottom:4, padding:"0 4px" }}>
                {msg.role === "user" ? (userName || "You") : "MindBridge AI"}
              </div>
              <div className={msg.role === "user" ? "chat-bubble-user" : "chat-bubble-ai"}>
                <p style={{ fontSize:14, lineHeight:1.6, color:C.text, whiteSpace:"pre-wrap", margin:0 }}>
                  {msg.content}
                </p>
              </div>
            </div>
          ))}

          {isTyping && (
            <div style={{ display:"flex", flexDirection:"column", alignItems:"flex-start" }}>
              <div style={{ fontSize:10, color:C.dim, marginBottom:4, paddingLeft:4 }}>MindBridge AI</div>
              <TypingIndicator/>
            </div>
          )}

          {/* Scoring overlay */}
          {phase === "review" && features && (
            <div style={{ margin:"8px 0" }}>
              <ScoringOverlay features={features} onPredict={runPrediction}/>
            </div>
          )}

          {/* Error */}
          {error && (
            <div style={{ padding:"12px 16px", background:"rgba(248,113,113,0.1)", border:"1px solid rgba(248,113,113,0.25)", borderRadius:12, color:C.red, fontSize:13 }}>
              ⚠️ {error}
            </div>
          )}

          {/* Crisis panel — 3-button design from plan */}
          {crisisDetected && !crisisDismissed && (
            <div className="crisis-panel">
              <div style={{ color:C.red, fontWeight:700, fontSize:15, marginBottom:8 }}>🚨 I'm really concerned about you right now.</div>
              <p style={{ fontSize:13, color:C.muted, lineHeight:1.6, marginBottom:0 }}>
                Are you safe? Do you have someone nearby?
              </p>

              {/* 3-button row */}
              <div className="crisis-actions">
                <button
                  className="crisis-btn safe"
                  onClick={() => { setCrisisDismissed(true); setCrisisExpanded(false); }}
                >✅ I'm safe</button>
                <button
                  className="crisis-btn"
                  onClick={() => setCrisisExpanded(true)}
                >🆘 I need help</button>
                <button
                  className="crisis-btn talk"
                  onClick={() => { setCrisisDismissed(true); inputRef.current?.focus(); }}
                >💬 Talk to me</button>
              </div>

              {/* Expanded resources */}
              {crisisExpanded && (
                <div>
                  <div style={{ fontSize:12, color:C.muted, marginBottom:10, fontWeight:600 }}>Resources that can help right now:</div>
                  {CRISIS_RESOURCES.map(r => (
                    <div key={r.name} style={{ display:"flex", justifyContent:"space-between", padding:"8px 12px", background:"rgba(248,113,113,0.08)", borderRadius:10, marginBottom:8, fontSize:13 }}>
                      <span style={{ color:C.muted }}>{r.name}</span>
                      <span style={{ color:C.red, fontWeight:700 }}>{r.contact}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Result + Session Close Ritual */}
          {phase === "result" && result && (
            <div className="glass" style={{ padding:24 }}>
              <ResultCard result={result}/>
              {/* Progress celebration (if prior sessions exist) */}
              {previousSessions.length > 0 && features && (
                <ProgressCelebration
                  current={features}
                  previous={previousSessions.find(s => s.depression_score !== undefined) || null}
                />
              )}
              {/* Closing ritual */}
              <div className="close-ritual" style={{ marginTop:18 }}>
                <div className="close-ritual-emoji">
                  {result.risk?.toLowerCase() === "high" ? "🌙" :
                   crisisDetected ? "🌙" : "💙"}
                </div>
                <p className="close-ritual-text">
                  {crisisDetected
                    ? `${userName ? `${userName}, you` : "You"} shared some heavy things today.\nThat takes courage.\n\nYou got through today. That's enough. Rest now.`
                    : `${userName ? `I'll save this for you, ${userName}.` : "I'll save this conversation for you."}\n\nYou're not alone in this. Come back anytime — I'll be here.\n\nTake care of yourself. 💙`
                  }
                </p>
                <button className="btn-primary" onClick={resetChat} style={{ padding:"12px 28px", fontSize:14 }}>
                  🔄 Start New Interview
                </button>
              </div>
            </div>
          )}

          <div ref={chatEndRef}/>
        </div>

        {/* Input area */}
        <div style={{ padding:"16px 20px", borderTop:"1px solid var(--border)", flexShrink:0 }}>
          {phase === "interview" && (
            <div style={{ display:"flex", gap:12, alignItems:"flex-end" }}>
              <textarea
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKey}
                placeholder={crisisDetected && !crisisDismissed ? "Use the options above, or type here..." : "Share how you're feeling... (Hinglish works too!)"}
                disabled={isTyping}
                rows={2}
                style={{
                  flex:1, background:"rgba(255,255,255,0.05)", border:"1px solid var(--border)", borderRadius:14,
                  padding:"12px 16px", color:C.text, fontFamily:"'DM Sans',sans-serif", fontSize:14,
                  outline:"none", resize:"none", lineHeight:1.5,
                }}
              />
              <button
                className="btn-primary"
                onClick={sendMessage}
                disabled={!input.trim() || isTyping}
                style={{ padding:"14px 22px", borderRadius:14, fontSize:18, flexShrink:0 }}
              >
                →
              </button>
            </div>
          )}
          {(phase === "scoring" || phase === "predicting") && (
            <div style={{ textAlign:"center", color:C.muted, fontSize:13, display:"flex", alignItems:"center", justifyContent:"center", gap:10 }}>
              <span style={{ display:"inline-block", width:14, height:14, border:"2px solid rgba(108,142,255,0.3)", borderTop:"2px solid var(--accent)", borderRadius:"50%", animation:"spin 0.8s linear infinite" }}/>
              {phase === "scoring" ? "Extracting clinical scores..." : "Running prediction model..."}
            </div>
          )}
          {/* In result phase, the close ritual has its own New Interview button */}
          {/* Hint */}
          {phase === "interview" && !crisisDetected && (
            <div style={{ marginTop:8, fontSize:11, color:C.dim, textAlign:"center" }}>
              Press Enter to send · Shift+Enter for new line · Your data is private
            </div>
          )}
        </div>
      </div>

      {/* RIGHT: Empathy Map panel — collapsible */}
      <EmpathyMapPanel
        empathyMap={empathyMap}
        confidencePct={confidencePct}
        turnCount={turnCount}
        visible={mapVisible}
        onToggle={() => setMapVisible(v => !v)}
      />
    </div>
  );
}
