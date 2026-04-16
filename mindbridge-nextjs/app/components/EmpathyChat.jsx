"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import { sendInterviewMessage, scoreConversation, predictFromFeatures } from "../lib/api";
import { ResultCard } from "./ManualAssess";

const C = {
  text: "#f0f4ff", muted: "rgba(240,244,255,0.55)", dim: "rgba(240,244,255,0.35)",
  accent: "#6c8eff", accentGlow: "rgba(108,142,255,0.35)",
  green: "#4ade80", amber: "#fbbf24", red: "#f87171", purple: "#a78bfa",
  surface: "rgba(255,255,255,0.06)", border: "rgba(255,255,255,0.12)",
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

function EmpathyMapPanel({ empathyMap, confidencePct, turnCount }) {
  const hasData = Object.values(empathyMap).some(arr => arr.length > 0);
  return (
    <div className="glass" style={{ padding:20, height:"100%", display:"flex", flexDirection:"column", gap:16 }}>
      {/* Header */}
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between" }}>
        <div style={{ fontSize:13, fontWeight:700, color:C.muted, letterSpacing:1 }}>📡 EMPATHY MAP</div>
        <div style={{ fontSize:11, color:C.dim }}>{turnCount} turns</div>
      </div>

      {/* 4 quadrants */}
      {Object.entries(EMPATHY_CONFIG).map(([key, cfg]) => (
        <div key={key}>
          <div style={{ display:"flex", alignItems:"center", gap:6, marginBottom:8 }}>
            <span style={{ fontSize:13 }}>{cfg.icon}</span>
            <span style={{ fontSize:11, fontWeight:700, color:cfg.color, letterSpacing:0.8 }}>{cfg.label}</span>
            <span style={{ fontSize:10, color:C.dim }}>{cfg.desc}</span>
          </div>
          <div style={{ minHeight:28, display:"flex", flexWrap:"wrap", gap:4 }}>
            {(empathyMap[key] || []).length > 0
              ? (empathyMap[key] || []).map((item, i) => (
                  <span key={i} className="emp-tag" style={{ borderColor:`${cfg.color}33`, color:cfg.color }}>
                    {item}
                  </span>
                ))
              : <span style={{ fontSize:11, color:C.dim, fontStyle:"italic" }}>Listening...</span>
            }
          </div>
        </div>
      ))}

      {/* Confidence meter */}
      <div style={{ marginTop:"auto" }}>
        <div style={{ display:"flex", justifyContent:"space-between", marginBottom:6 }}>
          <span style={{ fontSize:11, color:C.dim }}>Data Confidence</span>
          <span style={{ fontSize:12, color:C.accent, fontWeight:600 }}>{confidencePct}%</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width:`${confidencePct}%`, background:`linear-gradient(90deg, ${C.accent}, ${C.purple})`, boxShadow:`0 0 8px ${C.accentGlow}` }}/>
        </div>
        {confidencePct >= 60 && (
          <div style={{ marginTop:8, fontSize:11, color:C.green, display:"flex", alignItems:"center", gap:5 }}>
            <span style={{ display:"inline-block", width:6, height:6, borderRadius:"50%", background:C.green, animation:"pulse 2s infinite" }}/>
            Enough data to score
          </div>
        )}
      </div>

      {/* 5 Whys depth */}
      <div>
        <div style={{ fontSize:11, color:C.dim, marginBottom:6 }}>5 Whys Depth</div>
        <div style={{ display:"flex", gap:4 }}>
          {[0,1,2,3,4].map(i => (
            <div key={i} style={{ flex:1, height:4, borderRadius:2, background: i < Math.min(turnCount, 5) ? C.purple : "rgba(255,255,255,0.1)", transition:"background 0.4s", boxShadow: i < Math.min(turnCount, 5) ? `0 0 6px ${C.purple}` : "none" }}/>
          ))}
        </div>
      </div>

      {!hasData && (
        <div style={{ textAlign:"center", color:C.dim, fontSize:12, fontStyle:"italic" }}>
          Share how you're feeling to begin mapping...
        </div>
      )}
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

export default function EmpathyChat({ onNewResult }) {
  const [messages, setMessages] = useState([OPENING_MESSAGE]);
  const [input, setInput]       = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [phase, setPhase]       = useState("interview"); // interview | scoring | predicting | result
  const [empathyMap, setEmpathyMap] = useState({ says:[], thinks:[], does:[], feels:[] });
  const [confidencePct, setConfidencePct] = useState(0);
  const [features, setFeatures] = useState(null);
  const [result, setResult]     = useState(null);
  const [crisisDetected, setCrisisDetected] = useState(false);
  const [error, setError]       = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);
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

      if (res.crisis_detected) {
        setCrisisDetected(true);
        setPhase("crisis");
      } else if (res.ready_to_score) {
        setPhase("scoring");
        // Auto-trigger scoring
        await triggerScore([...history, aiMsg]);
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
      onNewResult?.({ ...features, ...predRes, timestamp:Date.now(), source:"empathy-chat" });
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
    setCrisisDetected(false); setError(null);
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  return (
    <div style={{ display:"grid", gridTemplateColumns:"1fr 300px", gap:20, height:"75vh", minHeight:600 }} className="fade-up">

      {/* LEFT: Chat panel */}
      <div className="glass" style={{ display:"flex", flexDirection:"column", overflow:"hidden" }}>
        {/* Chat header */}
        <div style={{ padding:"16px 20px", borderBottom:"1px solid var(--border)", display:"flex", alignItems:"center", justifyContent:"space-between", flexShrink:0 }}>
          <div style={{ display:"flex", alignItems:"center", gap:10 }}>
            <div style={{ width:10, height:10, borderRadius:"50%", background:C.green, boxShadow:`0 0 10px ${C.green}`, animation:"pulse 2s infinite" }}/>
            <span style={{ fontSize:14, fontWeight:600 }}>Empathy Interview</span>
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
                {msg.role === "user" ? "You" : "MindBridge AI"}
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

          {/* Crisis panel */}
          {crisisDetected && (
            <div className="glass" style={{ padding:20, border:"1px solid rgba(248,113,113,0.4)", boxShadow:`0 0 30px rgba(248,113,113,0.2)` }}>
              <div style={{ color:C.red, fontWeight:700, fontSize:15, marginBottom:12 }}>🚨 You're Not Alone — Crisis Support</div>
              <p style={{ fontSize:13, color:C.muted, lineHeight:1.6, marginBottom:16 }}>
                What you're feeling is real and it matters. Please reach out to one of these trained professionals right now:
              </p>
              {CRISIS_RESOURCES.map(r => (
                <div key={r.name} style={{ display:"flex", justifyContent:"space-between", padding:"8px 12px", background:"rgba(248,113,113,0.08)", borderRadius:10, marginBottom:8, fontSize:13 }}>
                  <span style={{ color:C.muted }}>{r.name}</span>
                  <span style={{ color:C.red, fontWeight:700 }}>{r.contact}</span>
                </div>
              ))}
            </div>
          )}

          {/* Result */}
          {phase === "result" && result && (
            <div className="glass" style={{ padding:24 }}>
              <ResultCard result={result}/>
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
                placeholder={crisisDetected ? "Please use the resources above..." : "Share how you're feeling... (Hinglish works too!)"}
                disabled={isTyping || crisisDetected}
                rows={2}
                style={{
                  flex:1, background:"rgba(255,255,255,0.05)", border:"1px solid var(--border)", borderRadius:14,
                  padding:"12px 16px", color:C.text, fontFamily:"'DM Sans',sans-serif", fontSize:14,
                  outline:"none", resize:"none", lineHeight:1.5,
                  opacity: crisisDetected ? 0.4 : 1,
                }}
              />
              <button
                className="btn-primary"
                onClick={sendMessage}
                disabled={!input.trim() || isTyping || crisisDetected}
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
          {phase === "result" && (
            <div style={{ display:"flex", gap:12, justifyContent:"center" }}>
              <button className="btn-primary" onClick={resetChat} style={{ padding:"12px 24px", fontSize:14 }}>
                🔄 Start New Interview
              </button>
            </div>
          )}
          {/* Hint */}
          {phase === "interview" && !crisisDetected && (
            <div style={{ marginTop:8, fontSize:11, color:C.dim, textAlign:"center" }}>
              Press Enter to send · Shift+Enter for new line · Your data is private
            </div>
          )}
        </div>
      </div>

      {/* RIGHT: Empathy Map panel */}
      <EmpathyMapPanel empathyMap={empathyMap} confidencePct={confidencePct} turnCount={turnCount}/>
    </div>
  );
}
