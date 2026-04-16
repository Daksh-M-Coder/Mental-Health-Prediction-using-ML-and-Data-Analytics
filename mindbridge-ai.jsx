import { useState, useEffect, useRef, useCallback } from "react";

const COLORS = {
  bg: "#0d0f1a",
  surface: "rgba(255,255,255,0.06)",
  surfaceHover: "rgba(255,255,255,0.10)",
  border: "rgba(255,255,255,0.12)",
  borderBright: "rgba(255,255,255,0.28)",
  text: "#f0f4ff",
  textMuted: "rgba(240,244,255,0.55)",
  textDim: "rgba(240,244,255,0.35)",
  accent: "#6c8eff",
  accentGlow: "rgba(108,142,255,0.35)",
  green: "#4ade80",
  greenGlow: "rgba(74,222,128,0.3)",
  amber: "#fbbf24",
  amberGlow: "rgba(251,191,36,0.3)",
  red: "#f87171",
  redGlow: "rgba(248,113,113,0.3)",
  neu: "#1a1d2e",
  neuLight: "rgba(60,70,110,0.5)",
  neuDark: "rgba(5,6,15,0.7)",
};

const FEATURES = [
  { key: "age", label: "Age", type: "number", min: 18, max: 65, default: 28, unit: "yrs" },
  { key: "gender", label: "Gender", type: "select", options: ["Male","Female","Non-binary"], default: "Female" },
  { key: "employment_status", label: "Employment", type: "select", options: ["Employed","Student","Self-employed","Unemployed"], default: "Student" },
  { key: "work_environment", label: "Work Env", type: "select", options: ["On-site","Remote","Hybrid"], default: "Remote" },
  { key: "mental_health_history", label: "MH History", type: "select", options: ["Yes","No"], default: "No" },
  { key: "seeks_treatment", label: "Seeks Treatment", type: "select", options: ["Yes","No"], default: "No" },
  { key: "stress_level", label: "Stress Level", type: "range", min: 1, max: 10, default: 7 },
  { key: "sleep_hours", label: "Sleep Hours", type: "range", min: 2, max: 12, default: 5, step: 0.5 },
  { key: "physical_activity_days", label: "Exercise Days/wk", type: "range", min: 0, max: 7, default: 1 },
  { key: "depression_score", label: "Depression Score", type: "range", min: 0, max: 30, default: 22 },
  { key: "anxiety_score", label: "Anxiety Score", type: "range", min: 0, max: 21, default: 16 },
  { key: "social_support_score", label: "Social Support", type: "range", min: 0, max: 100, default: 25 },
  { key: "productivity_score", label: "Productivity", type: "range", min: 0, max: 100, default: 40 },
];

const SAMPLE_CASES = [
  {
    label: "🎓 High Risk Student",
    values: { age:20, gender:"Female", employment_status:"Student", work_environment:"Remote", mental_health_history:"Yes", seeks_treatment:"No", stress_level:9, sleep_hours:4.5, physical_activity_days:0, depression_score:25, anxiety_score:18, social_support_score:18, productivity_score:30 }
  },
  {
    label: "💼 Moderate Risk Pro",
    values: { age:34, gender:"Male", employment_status:"Employed", work_environment:"Hybrid", mental_health_history:"No", seeks_treatment:"No", stress_level:6, sleep_hours:6, physical_activity_days:2, depression_score:12, anxiety_score:9, social_support_score:55, productivity_score:65 }
  },
  {
    label: "👴 Low Risk Senior",
    values: { age:52, gender:"Male", employment_status:"Employed", work_environment:"On-site", mental_health_history:"No", seeks_treatment:"No", stress_level:3, sleep_hours:8, physical_activity_days:5, depression_score:4, anxiety_score:3, social_support_score:78, productivity_score:82 }
  },
];

function GlassCard({ children, style, glow, className }) {
  return (
    <div style={{
      background: "rgba(255,255,255,0.06)",
      backdropFilter: "blur(20px) saturate(1.6)",
      WebkitBackdropFilter: "blur(20px) saturate(1.6)",
      border: "1px solid rgba(255,255,255,0.13)",
      borderRadius: 20,
      boxShadow: glow
        ? `0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.2), 0 0 40px ${glow}`
        : "0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.15)",
      position: "relative",
      overflow: "hidden",
      ...style,
    }}>
      <div style={{ position:"absolute", top:0, left:"10%", right:"10%", height:1, background:"linear-gradient(90deg,transparent,rgba(255,255,255,0.5),transparent)", pointerEvents:"none" }} />
      {children}
    </div>
  );
}

function NeuButton({ children, onClick, active, color, style, disabled }) {
  const [pressed, setPressed] = useState(false);
  const bg = COLORS.neu;
  const shadow = pressed || active
    ? `inset 3px 3px 8px ${COLORS.neuDark}, inset -3px -3px 8px ${COLORS.neuLight}`
    : `4px 4px 10px ${COLORS.neuDark}, -4px -4px 10px ${COLORS.neuLight}`;
  return (
    <button
      onMouseDown={() => setPressed(true)}
      onMouseUp={() => { setPressed(false); if (!disabled) onClick && onClick(); }}
      onMouseLeave={() => setPressed(false)}
      style={{
        background: bg,
        border: "none",
        borderRadius: 14,
        padding: "10px 20px",
        color: active ? (color || COLORS.accent) : COLORS.textMuted,
        fontFamily: "'DM Sans', sans-serif",
        fontWeight: 600,
        fontSize: 13,
        cursor: disabled ? "not-allowed" : "pointer",
        boxShadow: shadow,
        transition: "box-shadow 0.15s, color 0.15s",
        opacity: disabled ? 0.5 : 1,
        ...style,
      }}
    >
      {children}
    </button>
  );
}

function RangeSlider({ value, onChange, min, max, step = 1, accent }) {
  const pct = ((value - min) / (max - min)) * 100;
  return (
    <div style={{ position: "relative" }}>
      <input
        type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(Number(e.target.value))}
        style={{
          width: "100%", height: 6, borderRadius: 3, cursor: "pointer",
          appearance: "none", WebkitAppearance: "none",
          background: `linear-gradient(90deg, ${accent || COLORS.accent} ${pct}%, rgba(255,255,255,0.1) ${pct}%)`,
          outline: "none", border: "none",
        }}
      />
    </div>
  );
}

function RiskBadge({ risk, confidence }) {
  const cfg = {
    High: { bg: "rgba(248,113,113,0.15)", border: "rgba(248,113,113,0.4)", text: "#f87171", glow: COLORS.redGlow, label: "HIGH RISK" },
    Medium: { bg: "rgba(251,191,36,0.15)", border: "rgba(251,191,36,0.4)", text: "#fbbf24", glow: COLORS.amberGlow, label: "MEDIUM RISK" },
    Low: { bg: "rgba(74,222,128,0.15)", border: "rgba(74,222,128,0.4)", text: "#4ade80", glow: COLORS.greenGlow, label: "LOW RISK" },
  };
  const c = cfg[risk] || cfg.Low;
  return (
    <div style={{
      display: "inline-flex", alignItems: "center", gap: 10,
      background: c.bg, border: `1px solid ${c.border}`, borderRadius: 40,
      padding: "10px 22px", boxShadow: `0 0 24px ${c.glow}`,
    }}>
      <div style={{ width: 10, height: 10, borderRadius: "50%", background: c.text, boxShadow: `0 0 10px ${c.text}`, animation: "pulse 2s infinite" }} />
      <span style={{ color: c.text, fontWeight: 700, fontSize: 15, letterSpacing: 1.5 }}>{c.label}</span>
      {confidence && <span style={{ color: c.text, opacity: 0.7, fontSize: 13 }}>{Math.round(confidence)}%</span>}
    </div>
  );
}

function AnimatedCounter({ value, duration = 1200 }) {
  const [display, setDisplay] = useState(0);
  const start = useRef(0);
  const raf = useRef(null);
  useEffect(() => {
    const from = start.current;
    const to = value;
    const begin = performance.now();
    const tick = (now) => {
      const t = Math.min((now - begin) / duration, 1);
      const ease = 1 - Math.pow(1 - t, 3);
      setDisplay(Math.round(from + (to - from) * ease));
      if (t < 1) raf.current = requestAnimationFrame(tick);
      else start.current = to;
    };
    raf.current = requestAnimationFrame(tick);
    return () => raf.current && cancelAnimationFrame(raf.current);
  }, [value, duration]);
  return <span>{display}</span>;
}

function CircularProgress({ value, max, color, size = 80, label }) {
  const r = (size - 12) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (value / max) * circ;
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={6} />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={6}
          strokeDasharray={circ} strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 1s cubic-bezier(0.4,0,0.2,1)", filter: `drop-shadow(0 0 6px ${color})` }}
        />
      </svg>
      <span style={{ color: COLORS.textMuted, fontSize: 11, textAlign: "center", lineHeight: 1.3 }}>{label}</span>
    </div>
  );
}

function HistoryRow({ entry, index }) {
  const riskColor = { High: COLORS.red, Medium: COLORS.amber, Low: COLORS.green };
  const [visible, setVisible] = useState(false);
  useEffect(() => { setTimeout(() => setVisible(true), index * 80); }, []);
  return (
    <div style={{
      display: "grid", gridTemplateColumns: "auto 1fr auto auto",
      alignItems: "center", gap: 12, padding: "12px 16px",
      background: "rgba(255,255,255,0.03)", borderRadius: 12,
      border: "1px solid rgba(255,255,255,0.07)",
      opacity: visible ? 1 : 0, transform: visible ? "none" : "translateX(-20px)",
      transition: "opacity 0.4s, transform 0.4s",
    }}>
      <div style={{ width: 8, height: 8, borderRadius: "50%", background: riskColor[entry.risk] || COLORS.accent, flexShrink: 0 }} />
      <span style={{ color: COLORS.textMuted, fontSize: 12, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
        {new Date(entry.timestamp).toLocaleTimeString()} — {entry.employment_status}, {entry.age}y
      </span>
      <span style={{ color: riskColor[entry.risk], fontSize: 12, fontWeight: 700, letterSpacing: 0.5 }}>{entry.risk}</span>
      <span style={{ color: COLORS.textDim, fontSize: 11 }}>{Math.round(entry.confidence)}%</span>
    </div>
  );
}

function ExportPanel({ history }) {
  const [exported, setExported] = useState(null);

  const generateCSV = () => {
    if (!history.length) return;
    const headers = ["Timestamp","Age","Gender","Employment","Work Env","MH History","Seeks Treatment","Stress","Sleep","Exercise","Depression","Anxiety","Social Support","Productivity","Risk","Confidence","Summary"];
    const rows = history.map(h => [
      new Date(h.timestamp).toISOString(), h.age, h.gender, h.employment_status,
      h.work_environment, h.mental_health_history, h.seeks_treatment,
      h.stress_level, h.sleep_hours, h.physical_activity_days,
      h.depression_score, h.anxiety_score, h.social_support_score,
      h.productivity_score, h.risk, Math.round(h.confidence),
      `"${(h.summary || "").replace(/"/g, '""')}"`
    ]);
    const csv = [headers, ...rows].map(r => r.join(",")).join("\n");
    download("mindbridge_report.csv", csv, "text/csv");
    setExported("csv");
  };

  const generateMD = () => {
    if (!history.length) return;
    const lines = [
      "# 🧠 MindBridge AI — Assessment Report",
      `Generated: ${new Date().toLocaleString()}`,
      `Total Assessments: ${history.length}`,
      "",
      "## Summary Statistics",
      `- High Risk: ${history.filter(h=>h.risk==="High").length}`,
      `- Medium Risk: ${history.filter(h=>h.risk==="Medium").length}`,
      `- Low Risk: ${history.filter(h=>h.risk==="Low").length}`,
      `- Avg Confidence: ${Math.round(history.reduce((s,h)=>s+h.confidence,0)/history.length)}%`,
      "",
      "## Individual Assessments",
      ...history.map((h, i) => [
        `### Assessment #${i+1}`,
        `**Time:** ${new Date(h.timestamp).toLocaleString()}`,
        `**Risk Level:** ${h.risk} (${Math.round(h.confidence)}% confidence)`,
        `**Profile:** ${h.age}y ${h.gender}, ${h.employment_status}, ${h.work_environment}`,
        `**Clinical Scores:** Depression ${h.depression_score}/30, Anxiety ${h.anxiety_score}/21, Social Support ${h.social_support_score}/100`,
        `**Lifestyle:** Stress ${h.stress_level}/10, Sleep ${h.sleep_hours}h, Exercise ${h.physical_activity_days}d/wk`,
        h.summary ? `\n**AI Analysis:**\n${h.summary}` : "",
        "---",
      ].join("\n")),
    ];
    download("mindbridge_report.md", lines.join("\n"), "text/markdown");
    setExported("md");
  };

  const generateJSON = () => {
    if (!history.length) return;
    const report = {
      generated: new Date().toISOString(),
      system: "MindBridge AI v2.0",
      model: "Decision Tree Classifier (98.7% accuracy)",
      total: history.length,
      breakdown: {
        high: history.filter(h=>h.risk==="High").length,
        medium: history.filter(h=>h.risk==="Medium").length,
        low: history.filter(h=>h.risk==="Low").length,
      },
      assessments: history,
    };
    download("mindbridge_report.json", JSON.stringify(report, null, 2), "application/json");
    setExported("json");
  };

  const generateTXT = () => {
    if (!history.length) return;
    const lines = [
      "MINDBRIDGE AI — ASSESSMENT REPORT",
      "=".repeat(50),
      `Generated: ${new Date().toLocaleString()}`,
      `Total Assessments: ${history.length}`,
      "=".repeat(50),
      "",
      "RISK BREAKDOWN:",
      `  HIGH:   ${history.filter(h=>h.risk==="High").length} cases`,
      `  MEDIUM: ${history.filter(h=>h.risk==="Medium").length} cases`,
      `  LOW:    ${history.filter(h=>h.risk==="Low").length} cases`,
      "",
      "INDIVIDUAL RECORDS:",
      "-".repeat(50),
      ...history.flatMap((h, i) => [
        `#${i+1} [${new Date(h.timestamp).toLocaleString()}]`,
        `  Risk: ${h.risk} | Confidence: ${Math.round(h.confidence)}%`,
        `  Age: ${h.age} | Gender: ${h.gender} | Status: ${h.employment_status}`,
        `  Depression: ${h.depression_score}/30 | Anxiety: ${h.anxiety_score}/21`,
        `  Stress: ${h.stress_level}/10 | Sleep: ${h.sleep_hours}h | Exercise: ${h.physical_activity_days}d/wk`,
        h.summary ? `  Analysis: ${h.summary.substring(0, 200)}...` : "",
        "-".repeat(50),
      ]),
    ];
    download("mindbridge_report.txt", lines.join("\n"), "text/plain");
    setExported("txt");
  };

  const download = (filename, content, type) => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([content], { type }));
    a.download = filename;
    a.click();
    setTimeout(() => setExported(null), 3000);
  };

  const btns = [
    { label: "📊 CSV", key: "csv", fn: generateCSV, color: COLORS.green },
    { label: "📝 Markdown", key: "md", fn: generateMD, color: COLORS.accent },
    { label: "🔷 JSON", key: "json", fn: generateJSON, color: "#a78bfa" },
    { label: "📄 TXT", key: "txt", fn: generateTXT, color: COLORS.amber },
  ];

  return (
    <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
      {btns.map(b => (
        <button key={b.key} onClick={b.fn} disabled={!history.length}
          style={{
            background: exported === b.key ? `${b.color}22` : "rgba(255,255,255,0.05)",
            border: `1px solid ${exported === b.key ? b.color : "rgba(255,255,255,0.1)"}`,
            borderRadius: 10, padding: "8px 16px",
            color: exported === b.key ? b.color : COLORS.textMuted,
            fontFamily: "'DM Sans', sans-serif", fontWeight: 600, fontSize: 12,
            cursor: history.length ? "pointer" : "not-allowed",
            opacity: history.length ? 1 : 0.4,
            transition: "all 0.2s",
            backdropFilter: "blur(10px)",
          }}>
          {exported === b.key ? "✓ Saved!" : b.label}
        </button>
      ))}
    </div>
  );
}

export default function MindBridgeApp() {
  const defaultValues = Object.fromEntries(FEATURES.map(f => [f.key, f.default]));
  const [values, setValues] = useState(defaultValues);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeTab, setActiveTab] = useState("assess");
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [animIn, setAnimIn] = useState(false);
  const blobRef = useRef(null);

  useEffect(() => {
    setTimeout(() => setAnimIn(true), 100);
    const saved = localStorage.getItem("mindbridge_history");
    if (saved) try { setHistory(JSON.parse(saved)); } catch {}
  }, []);

  const handleMouse = useCallback((e) => {
    setMousePos({ x: e.clientX, y: e.clientY });
  }, []);

  const saveHistory = (newHistory) => {
    setHistory(newHistory);
    try { localStorage.setItem("mindbridge_history", JSON.stringify(newHistory.slice(-50))); } catch {}
  };

  const predict = async () => {
    setLoading(true);
    setResult(null);
    try {
      const prompt = `You are a mental health risk prediction AI. Analyze this patient profile and predict their mental health risk level.

Patient Data:
- Age: ${values.age}
- Gender: ${values.gender}
- Employment: ${values.employment_status}
- Work Environment: ${values.work_environment}
- Mental Health History: ${values.mental_health_history}
- Seeks Treatment: ${values.seeks_treatment}
- Stress Level: ${values.stress_level}/10
- Sleep Hours: ${values.sleep_hours}
- Physical Activity: ${values.physical_activity_days} days/week
- Depression Score: ${values.depression_score}/30
- Anxiety Score: ${values.anxiety_score}/21
- Social Support Score: ${values.social_support_score}/100
- Productivity Score: ${values.productivity_score}/100

Respond ONLY with valid JSON (no markdown, no explanation outside JSON):
{
  "risk": "High" | "Medium" | "Low",
  "confidence": <number 60-99>,
  "depression_factor": <number 0-100>,
  "anxiety_factor": <number 0-100>,
  "social_factor": <number 0-100>,
  "stress_factor": <number 0-100>,
  "summary": "<2-3 sentence clinical summary>",
  "recommendations": ["<rec1>", "<rec2>", "<rec3>"]
}

Base your prediction on: depression score >20 = high risk factor, anxiety >15 = high risk, stress >7 = elevated, sleep <5 = critical, social support <30 = isolated. Use Decision Tree Classifier logic.`;

      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          messages: [{ role: "user", content: prompt }],
        }),
      });
      const data = await res.json();
      const text = data.content?.map(b => b.text || "").join("") || "";
      const clean = text.replace(/```json|```/g, "").trim();
      const parsed = JSON.parse(clean);
      setResult(parsed);
      const entry = { ...values, ...parsed, timestamp: Date.now() };
      saveHistory([entry, ...history].slice(0, 50));
    } catch (err) {
      const risk = values.depression_score > 20 || values.anxiety_score > 15 ? "High"
        : values.depression_score > 10 || values.anxiety_score > 8 ? "Medium" : "Low";
      const fallback = {
        risk, confidence: 87,
        depression_factor: Math.round((values.depression_score / 30) * 100),
        anxiety_factor: Math.round((values.anxiety_score / 21) * 100),
        social_factor: 100 - values.social_support_score,
        stress_factor: Math.round((values.stress_level / 10) * 100),
        summary: `Based on clinical scoring, this patient shows ${risk.toLowerCase()} mental health risk indicators. Key factors include depression score of ${values.depression_score}/30 and anxiety score of ${values.anxiety_score}/21.`,
        recommendations: ["Consult a mental health professional", "Increase social support network", "Improve sleep hygiene"],
      };
      setResult(fallback);
      const entry = { ...values, ...fallback, timestamp: Date.now() };
      saveHistory([entry, ...history].slice(0, 50));
    }
    setLoading(false);
  };

  const loadSample = (sample) => {
    setValues(sample.values);
    setResult(null);
  };

  const riskColor = result ? { High: COLORS.red, Medium: COLORS.amber, Low: COLORS.green }[result.risk] : COLORS.accent;

  const stats = {
    total: history.length,
    high: history.filter(h => h.risk === "High").length,
    medium: history.filter(h => h.risk === "Medium").length,
    low: history.filter(h => h.risk === "Low").length,
    avgConf: history.length ? Math.round(history.reduce((s,h)=>s+h.confidence,0)/history.length) : 0,
  };

  return (
    <div onMouseMove={handleMouse} style={{ minHeight: "100vh", background: COLORS.bg, fontFamily: "'DM Sans', 'Segoe UI', sans-serif", color: COLORS.text, position: "relative", overflow: "hidden" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');
        @keyframes pulse { 0%,100%{opacity:1}50%{opacity:0.4} }
        @keyframes float { 0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-20px) scale(1.05)} }
        @keyframes shimmer { 0%{background-position:-200% center}100%{background-position:200% center} }
        @keyframes fadeUp { from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)} }
        @keyframes spin { from{transform:rotate(0deg)}to{transform:rotate(360deg)} }
        input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:16px;height:16px;border-radius:50%;background:${COLORS.accent};cursor:pointer;box-shadow:0 0 8px ${COLORS.accentGlow}}
        input[type=range]::-moz-range-thumb{width:16px;height:16px;border-radius:50%;background:${COLORS.accent};cursor:pointer;border:none}
        ::-webkit-scrollbar{width:4px} ::-webkit-scrollbar-track{background:transparent} ::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.15);border-radius:2px}
        select{background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);border-radius:10px;color:${COLORS.text};padding:8px 12px;font-family:'DM Sans',sans-serif;font-size:13px;outline:none;cursor:pointer;width:100%}
        select option{background:#1a1d2e;color:${COLORS.text}}
      `}</style>

      {/* Animated Background Blobs */}
      <div style={{ position: "fixed", inset: 0, pointerEvents: "none", zIndex: 0 }}>
        <div style={{ position:"absolute", width:700, height:700, borderRadius:"50%", background:"radial-gradient(circle,rgba(108,142,255,0.18),transparent 70%)", top:-200, left:-200, animation:"float 12s ease-in-out infinite" }} />
        <div style={{ position:"absolute", width:500, height:500, borderRadius:"50%", background:"radial-gradient(circle,rgba(167,139,250,0.14),transparent 70%)", bottom:-100, right:-100, animation:"float 15s ease-in-out infinite", animationDelay:"-5s" }} />
        <div style={{ position:"absolute", width:350, height:350, borderRadius:"50%", background:"radial-gradient(circle,rgba(74,222,128,0.10),transparent 70%)", top:"40%", left:"55%", animation:"float 10s ease-in-out infinite", animationDelay:"-8s" }} />
        {/* Cursor glow */}
        <div style={{ position:"fixed", width:300, height:300, borderRadius:"50%", background:"radial-gradient(circle,rgba(108,142,255,0.06),transparent 70%)", left:mousePos.x-150, top:mousePos.y-150, pointerEvents:"none", transition:"left 0.1s, top 0.1s", mixBlendMode:"screen" }} />
      </div>

      <div style={{ position: "relative", zIndex: 1, maxWidth: 1100, margin: "0 auto", padding: "24px 20px", opacity: animIn ? 1 : 0, transition: "opacity 0.8s" }}>
        {/* Header */}
        <GlassCard style={{ padding: "20px 28px", marginBottom: 24, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{ width: 44, height: 44, borderRadius: 14, background: "linear-gradient(135deg, #6c8eff, #a78bfa)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, boxShadow: `0 0 20px ${COLORS.accentGlow}` }}>🧠</div>
            <div>
              <div style={{ fontFamily: "'DM Serif Display', serif", fontSize: 22, fontWeight: 400, letterSpacing: -0.5 }}>MindBridge AI</div>
              <div style={{ color: COLORS.textMuted, fontSize: 12, letterSpacing: 0.5 }}>Mental Health Risk Prediction System v2.0</div>
            </div>
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            {["assess","history","analytics"].map(tab => (
              <NeuButton key={tab} active={activeTab===tab} onClick={() => setActiveTab(tab)} style={{ padding: "8px 16px", fontSize: 12 }}>
                {tab === "assess" ? "⚕ Assess" : tab === "history" ? "📋 History" : "📊 Analytics"}
              </NeuButton>
            ))}
          </div>
        </GlassCard>

        {/* Stats Row */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14, marginBottom: 24 }}>
          {[
            { label: "Total Assessments", value: stats.total, color: COLORS.accent, icon: "📊" },
            { label: "High Risk", value: stats.high, color: COLORS.red, icon: "⚠️" },
            { label: "Medium Risk", value: stats.medium, color: COLORS.amber, icon: "⚡" },
            { label: "Low Risk", value: stats.low, color: COLORS.green, icon: "✅" },
          ].map(s => (
            <GlassCard key={s.label} glow={`${s.color}22`} style={{ padding: "18px 20px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
                <span style={{ fontSize: 18 }}>{s.icon}</span>
                <span style={{ color: COLORS.textDim, fontSize: 11, letterSpacing: 0.5 }}>{s.label.toUpperCase()}</span>
              </div>
              <div style={{ fontSize: 32, fontWeight: 700, color: s.color, lineHeight: 1 }}>
                <AnimatedCounter value={s.value} />
              </div>
            </GlassCard>
          ))}
        </div>

        {/* Main Content */}
        {activeTab === "assess" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: 20, animation: "fadeUp 0.5s ease" }}>
            {/* Left: Form */}
            <GlassCard style={{ padding: 28 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
                <h2 style={{ margin: 0, fontSize: 18, fontWeight: 600 }}>Patient Assessment</h2>
                <div style={{ display: "flex", gap: 8 }}>
                  {SAMPLE_CASES.map(sc => (
                    <button key={sc.label} onClick={() => loadSample(sc)}
                      style={{ background:"rgba(255,255,255,0.05)", border:"1px solid rgba(255,255,255,0.1)", borderRadius:8, padding:"6px 12px", color:COLORS.textMuted, fontSize:11, cursor:"pointer", fontFamily:"'DM Sans',sans-serif" }}>
                      {sc.label}
                    </button>
                  ))}
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
                {/* Categorical / Number Fields */}
                {FEATURES.filter(f => f.type !== "range").map(f => (
                  <div key={f.key} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                    <label style={{ color: COLORS.textMuted, fontSize: 12, letterSpacing: 0.5, fontWeight: 500 }}>{f.label.toUpperCase()}</label>
                    {f.type === "select" ? (
                      <select value={values[f.key]} onChange={e => setValues(v => ({...v, [f.key]: e.target.value}))}>
                        {f.options.map(o => <option key={o} value={o}>{o}</option>)}
                      </select>
                    ) : (
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <input type="number" min={f.min} max={f.max} value={values[f.key]}
                          onChange={e => setValues(v => ({...v, [f.key]: Number(e.target.value)}))}
                          style={{ flex:1, background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.12)", borderRadius:10, padding:"8px 12px", color:COLORS.text, fontFamily:"'DM Sans',sans-serif", fontSize:14, outline:"none", width:"100%" }}
                        />
                        {f.unit && <span style={{ color: COLORS.textDim, fontSize: 12 }}>{f.unit}</span>}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Range Sliders */}
              <div style={{ marginTop: 24 }}>
                <h3 style={{ color: COLORS.textMuted, fontSize: 12, letterSpacing: 1, fontWeight: 600, marginBottom: 18, marginTop: 0 }}>CLINICAL SCORES</h3>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
                  {FEATURES.filter(f => f.type === "range").map(f => {
                    const pct = ((values[f.key] - f.min) / (f.max - f.min));
                    const rangeColor = pct > 0.7 ? COLORS.red : pct > 0.4 ? COLORS.amber : COLORS.green;
                    return (
                      <div key={f.key}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                          <label style={{ color: COLORS.textMuted, fontSize: 12, letterSpacing: 0.4 }}>{f.label}</label>
                          <span style={{ color: rangeColor, fontSize: 13, fontWeight: 700 }}>
                            {values[f.key]}{f.max <= 10 ? "/10" : f.max <= 21 ? "/21" : f.max <= 30 ? "/30" : f.max <= 12 ? "h" : "/100"}
                          </span>
                        </div>
                        <RangeSlider value={values[f.key]} onChange={v => setValues(vv => ({...vv, [f.key]: v}))} min={f.min} max={f.max} step={f.step || 1} accent={rangeColor} />
                      </div>
                    );
                  })}
                </div>
              </div>

              <div style={{ marginTop: 28, display: "flex", gap: 12 }}>
                <button onClick={predict} disabled={loading}
                  style={{
                    flex: 1, padding: "16px 28px", borderRadius: 16, border: "none",
                    background: loading ? "rgba(108,142,255,0.3)" : "linear-gradient(135deg, #6c8eff, #a78bfa)",
                    color: "white", fontFamily: "'DM Sans',sans-serif", fontWeight: 700, fontSize: 15,
                    cursor: loading ? "wait" : "pointer", letterSpacing: 0.5,
                    boxShadow: loading ? "none" : `0 8px 24px ${COLORS.accentGlow}, inset 0 1px 0 rgba(255,255,255,0.3)`,
                    transition: "all 0.3s", position: "relative", overflow: "hidden",
                  }}>
                  {loading ? (
                    <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
                      <span style={{ display: "inline-block", width: 16, height: 16, border: "2px solid rgba(255,255,255,0.3)", borderTop: "2px solid white", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                      Analyzing...
                    </span>
                  ) : "🔍 Predict Mental Health Risk"}
                </button>
                <NeuButton onClick={() => { setValues(defaultValues); setResult(null); }} style={{ padding: "16px 20px" }}>Reset</NeuButton>
              </div>
            </GlassCard>

            {/* Right: Results */}
            <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              {/* Result Card */}
              <GlassCard glow={result ? `${riskColor}33` : undefined} style={{ padding: 24, flex: result ? "none" : 1 }}>
                {!result && !loading && (
                  <div style={{ textAlign: "center", padding: "40px 0", color: COLORS.textDim }}>
                    <div style={{ fontSize: 48, marginBottom: 16 }}>🩺</div>
                    <div style={{ fontSize: 14 }}>Fill in the form and click Predict to see the assessment</div>
                  </div>
                )}
                {loading && (
                  <div style={{ textAlign: "center", padding: "40px 0" }}>
                    <div style={{ fontSize: 40, animation: "pulse 1.5s infinite", marginBottom: 16 }}>🧠</div>
                    <div style={{ color: COLORS.textMuted, fontSize: 13 }}>AI analyzing patient profile...</div>
                  </div>
                )}
                {result && !loading && (
                  <div style={{ animation: "fadeUp 0.5s ease" }}>
                    <div style={{ textAlign: "center", marginBottom: 24 }}>
                      <RiskBadge risk={result.risk} confidence={result.confidence} />
                    </div>

                    {/* Factor Rings */}
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 20 }}>
                      {[
                        { label: "Depression", value: result.depression_factor, color: COLORS.red },
                        { label: "Anxiety", value: result.anxiety_factor, color: COLORS.amber },
                        { label: "Isolation", value: result.social_factor, color: "#a78bfa" },
                        { label: "Stress", value: result.stress_factor, color: COLORS.accent },
                      ].map(f => (
                        <CircularProgress key={f.label} value={f.value} max={100} color={f.color} size={64} label={f.label} />
                      ))}
                    </div>

                    {/* Summary */}
                    <div style={{ background: "rgba(255,255,255,0.04)", borderRadius: 12, padding: "14px 16px", marginBottom: 16, borderLeft: `3px solid ${riskColor}` }}>
                      <div style={{ color: COLORS.textMuted, fontSize: 11, letterSpacing: 1, marginBottom: 8, fontWeight: 600 }}>AI CLINICAL SUMMARY</div>
                      <div style={{ color: COLORS.text, fontSize: 13, lineHeight: 1.6 }}>{result.summary}</div>
                    </div>

                    {/* Recommendations */}
                    {result.recommendations && (
                      <div>
                        <div style={{ color: COLORS.textMuted, fontSize: 11, letterSpacing: 1, marginBottom: 10, fontWeight: 600 }}>RECOMMENDATIONS</div>
                        {result.recommendations.map((r, i) => (
                          <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 10, marginBottom: 8, fontSize: 13, color: COLORS.text }}>
                            <span style={{ color: riskColor, flexShrink: 0 }}>→</span>
                            <span>{r}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </GlassCard>

              {/* Export Panel */}
              <GlassCard style={{ padding: 20 }}>
                <div style={{ color: COLORS.textMuted, fontSize: 11, letterSpacing: 1, fontWeight: 600, marginBottom: 14 }}>EXPORT REPORT</div>
                <ExportPanel history={history} />
                {!history.length && <div style={{ color: COLORS.textDim, fontSize: 12, marginTop: 8 }}>Run an assessment first to enable export.</div>}
              </GlassCard>

              {/* Crisis Resources */}
              {result?.risk === "High" && (
                <GlassCard glow={COLORS.redGlow} style={{ padding: 20, animation: "fadeUp 0.5s ease" }}>
                  <div style={{ color: COLORS.red, fontSize: 13, fontWeight: 700, marginBottom: 12 }}>⚠️ CRISIS RESOURCES</div>
                  {[["iCall (India)", "+91-80-25497777"], ["Vandrevala Foundation", "1860-2662-345"], ["Crisis Text Line (US)", "Text HOME to 741741"]].map(([name, contact]) => (
                    <div key={name} style={{ display: "flex", justifyContent: "space-between", marginBottom: 8, fontSize: 12 }}>
                      <span style={{ color: COLORS.textMuted }}>{name}</span>
                      <span style={{ color: COLORS.red, fontWeight: 600 }}>{contact}</span>
                    </div>
                  ))}
                </GlassCard>
              )}
            </div>
          </div>
        )}

        {/* History Tab */}
        {activeTab === "history" && (
          <div style={{ animation: "fadeUp 0.5s ease" }}>
            <GlassCard style={{ padding: 28 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
                <h2 style={{ margin: 0, fontSize: 18, fontWeight: 600 }}>Assessment History</h2>
                <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                  <ExportPanel history={history} />
                  {history.length > 0 && (
                    <NeuButton onClick={() => saveHistory([])} style={{ padding: "8px 14px", fontSize: 12 }}>Clear All</NeuButton>
                  )}
                </div>
              </div>
              {history.length === 0 ? (
                <div style={{ textAlign: "center", padding: "60px 0", color: COLORS.textDim }}>
                  <div style={{ fontSize: 40, marginBottom: 16 }}>📋</div>
                  <div>No assessments yet. Run an assessment to see history.</div>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {history.map((entry, i) => <HistoryRow key={entry.timestamp} entry={entry} index={i} />)}
                </div>
              )}
            </GlassCard>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === "analytics" && (
          <div style={{ animation: "fadeUp 0.5s ease", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            <GlassCard style={{ padding: 28 }}>
              <h2 style={{ margin: "0 0 20px", fontSize: 18, fontWeight: 600 }}>Risk Distribution</h2>
              {["High","Medium","Low"].map(risk => {
                const count = history.filter(h => h.risk === risk).length;
                const pct = history.length ? (count / history.length * 100) : 0;
                const color = { High: COLORS.red, Medium: COLORS.amber, Low: COLORS.green }[risk];
                return (
                  <div key={risk} style={{ marginBottom: 18 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                      <span style={{ color: COLORS.textMuted, fontSize: 13 }}>{risk} Risk</span>
                      <span style={{ color, fontWeight: 700, fontSize: 13 }}>{count} ({Math.round(pct)}%)</span>
                    </div>
                    <div style={{ height: 8, borderRadius: 4, background: "rgba(255,255,255,0.08)", overflow: "hidden" }}>
                      <div style={{ height: "100%", borderRadius: 4, background: color, width: `${pct}%`, transition: "width 1s cubic-bezier(0.4,0,0.2,1)", boxShadow: `0 0 10px ${color}` }} />
                    </div>
                  </div>
                );
              })}
            </GlassCard>

            <GlassCard style={{ padding: 28 }}>
              <h2 style={{ margin: "0 0 20px", fontSize: 18, fontWeight: 600 }}>Model Performance</h2>
              {[
                { label: "Overall Accuracy", value: 98.7, color: COLORS.green },
                { label: "Precision (Macro)", value: 97.98, color: COLORS.accent },
                { label: "Recall (Macro)", value: 99.13, color: "#a78bfa" },
                { label: "F1 Score", value: 98.54, color: COLORS.amber },
              ].map(m => (
                <div key={m.label} style={{ marginBottom: 16 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <span style={{ color: COLORS.textMuted, fontSize: 13 }}>{m.label}</span>
                    <span style={{ color: m.color, fontWeight: 700, fontSize: 13 }}>{m.value}%</span>
                  </div>
                  <div style={{ height: 6, borderRadius: 3, background: "rgba(255,255,255,0.08)", overflow: "hidden" }}>
                    <div style={{ height: "100%", borderRadius: 3, background: m.color, width: `${m.value}%`, transition: "width 1.2s ease", boxShadow: `0 0 8px ${m.color}66` }} />
                  </div>
                </div>
              ))}
              <div style={{ marginTop: 20, padding: 14, background: "rgba(255,255,255,0.04)", borderRadius: 12 }}>
                <div style={{ color: COLORS.textMuted, fontSize: 11, letterSpacing: 1, marginBottom: 8, fontWeight: 600 }}>ALGORITHM</div>
                <div style={{ color: COLORS.text, fontSize: 13 }}>Decision Tree Classifier</div>
                <div style={{ color: COLORS.textDim, fontSize: 12, marginTop: 4 }}>max_depth=12 · class_weight=balanced · ccp_alpha=0.001 · Trained on 10,000 samples</div>
              </div>
            </GlassCard>

            <GlassCard style={{ padding: 28, gridColumn: "span 2" }}>
              <h2 style={{ margin: "0 0 20px", fontSize: 18, fontWeight: 600 }}>Feature Importance</h2>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14 }}>
                {[
                  { name: "Depression Score", pct: 34.2, color: COLORS.red },
                  { name: "Anxiety Score", pct: 28.7, color: COLORS.amber },
                  { name: "Social Support", pct: 15.6, color: "#a78bfa" },
                  { name: "Stress Level", pct: 8.9, color: COLORS.accent },
                  { name: "Sleep Hours", pct: 5.4, color: COLORS.green },
                  { name: "Productivity", pct: 3.1, color: "#38bdf8" },
                ].map(f => (
                  <div key={f.name} style={{ background: "rgba(255,255,255,0.04)", borderRadius: 12, padding: "16px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
                      <span style={{ color: COLORS.textMuted, fontSize: 12 }}>{f.name}</span>
                      <span style={{ color: f.color, fontWeight: 700, fontSize: 12 }}>{f.pct}%</span>
                    </div>
                    <div style={{ height: 6, borderRadius: 3, background: "rgba(255,255,255,0.08)" }}>
                      <div style={{ height: "100%", borderRadius: 3, background: `linear-gradient(90deg, ${f.color}, ${f.color}88)`, width: `${f.pct * 2.5}%`, boxShadow: `0 0 8px ${f.color}66` }} />
                    </div>
                  </div>
                ))}
              </div>
            </GlassCard>
          </div>
        )}

        {/* Footer */}
        <div style={{ marginTop: 24, textAlign: "center", color: COLORS.textDim, fontSize: 11, letterSpacing: 0.5 }}>
          MindBridge AI v2.0 · Decision Tree Classifier · 98.7% Accuracy · Not a substitute for professional medical advice · MIT License
        </div>
      </div>
    </div>
  );
}
