"use client";
import { useState, useEffect, useRef } from "react";
import { predictDirect } from "../lib/api";

// ── Color tokens (mirrored from globals.css) ──────────────────────────────
const C = {
  // adaptive — light/dark via CSS vars
  bg:"var(--bg)", surface:"var(--c-surface)", border:"var(--c-border)",
  text:"var(--c-text)", muted:"var(--c-muted)", dim:"var(--c-dim)",
  // status — stay vivid
  accent:"var(--accent)", accentGlow:"var(--accent-glow)",
  green:"var(--green)",   greenGlow:"var(--green-glow)",
  amber:"var(--amber)",   amberGlow:"var(--amber-glow)",
  red:"var(--red)",       redGlow:"var(--red-glow)",
  purple:"var(--purple)", neu:"var(--neu)",
  neuL:"var(--neu-light)", neuD:"var(--neu-dark)",
};

const FEATURES = [
  { key:"age",                    label:"Age",             type:"number", min:18, max:65, default:28,  unit:"yrs" },
  { key:"gender",                 label:"Gender",          type:"select", options:["Male","Female","Non-binary"],           default:"Male" },
  { key:"employment_status",      label:"Employment",      type:"select", options:["Employed","Student","Self-employed","Unemployed"], default:"Employed" },
  { key:"work_environment",       label:"Work Env",        type:"select", options:["On-site","Remote","Hybrid"],            default:"On-site" },
  { key:"mental_health_history",  label:"MH History",      type:"select", options:["Yes","No"],                            default:"No" },
  { key:"seeks_treatment",        label:"Seeks Treatment", type:"select", options:["Yes","No"],                            default:"No" },
  // higher = bad (red)
  { key:"stress_level",           label:"Stress Level",    type:"range",  min:1,  max:10,  default:5 },
  { key:"depression_score",       label:"Depression Score",type:"range",  min:0,  max:30,  default:10 },
  { key:"anxiety_score",          label:"Anxiety Score",   type:"range",  min:0,  max:21,  default:7 },
  // higher = good (green) — inverted
  { key:"sleep_hours",            label:"Sleep Hours",     type:"range",  min:2,  max:12,  default:7,  step:0.5, inverted:true },
  { key:"physical_activity_days", label:"Exercise Days/wk",type:"range",  min:0,  max:7,   default:3,  inverted:true },
  { key:"social_support_score",   label:"Social Support",  type:"range",  min:0,  max:100, default:50, inverted:true },
  { key:"productivity_score",     label:"Productivity",    type:"range",  min:0,  max:100, default:60, inverted:true },
];

const SAMPLES = [
  { label:"🎓 High Risk Student",  values:{ age:20,gender:"Female",employment_status:"Student",work_environment:"Remote",mental_health_history:"Yes",seeks_treatment:"No",stress_level:9,sleep_hours:4.5,physical_activity_days:0,depression_score:25,anxiety_score:18,social_support_score:18,productivity_score:30 }},
  { label:"💼 Moderate Risk Pro",  values:{ age:34,gender:"Male",employment_status:"Employed",work_environment:"Hybrid",mental_health_history:"No",seeks_treatment:"No",stress_level:6,sleep_hours:6,physical_activity_days:2,depression_score:12,anxiety_score:9,social_support_score:55,productivity_score:65 }},
  { label:"👴 Low Risk Senior",    values:{ age:52,gender:"Male",employment_status:"Employed",work_environment:"On-site",mental_health_history:"No",seeks_treatment:"No",stress_level:3,sleep_hours:8,physical_activity_days:5,depression_score:4,anxiety_score:3,social_support_score:78,productivity_score:82 }},
];

function GlassCard({ children, style, glow }) {
  return (
    <div className="glass" style={{ boxShadow: glow ? `0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.2), 0 0 40px ${glow}` : undefined, ...style }}>
      {children}
    </div>
  );
}

function RangeSlider({ value, onChange, min, max, step = 1, color }) {
  const pct = ((value - min) / (max - min)) * 100;
  return (
    <input type="range" min={min} max={max} step={step} value={value}
      onChange={e => onChange(Number(e.target.value))}
      style={{ background: `linear-gradient(90deg, ${color} ${pct}%, rgba(255,255,255,0.1) ${pct}%)` }}
    />
  );
}

function CircularProgress({ value, max, color, size = 72, label }) {
  const r = (size - 12) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (value / max) * circ;
  const pct = Math.round((value / max) * 100);
  return (
    <div style={{ display:"flex", flexDirection:"column", alignItems:"center", gap:6 }}>
      <div style={{ position:"relative", width:size, height:size }}>
        <svg width={size} height={size} style={{ transform:"rotate(-90deg)", position:"absolute", top:0, left:0 }}>
          <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={6}/>
          <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={6}
            strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round"
            style={{ transition:"stroke-dashoffset 1s cubic-bezier(0.4,0,0.2,1)", filter:`drop-shadow(0 0 6px ${color})` }}
          />
        </svg>
        <div style={{ position:"absolute", inset:0, display:"flex", alignItems:"center", justifyContent:"center" }}>
          <span style={{ color, fontSize:size > 70 ? 13 : 11, fontWeight:700 }}>{pct}%</span>
        </div>
      </div>
      <span style={{ color:C.muted, fontSize:11, textAlign:"center", lineHeight:1.3 }}>{label}</span>
    </div>
  );
}

function RiskBadge({ risk, confidence }) {
  const cfg = {
    High:   { bg:"rgba(248,113,113,0.15)", border:"rgba(248,113,113,0.4)", text:C.red,    glow:C.redGlow,   label:"HIGH RISK"   },
    Medium: { bg:"rgba(251,191,36,0.15)",  border:"rgba(251,191,36,0.4)",  text:C.amber,  glow:C.amberGlow, label:"MEDIUM RISK" },
    Low:    { bg:"rgba(74,222,128,0.15)",  border:"rgba(74,222,128,0.4)",  text:C.green,  glow:C.greenGlow, label:"LOW RISK"    },
  };
  const c = cfg[risk] || cfg.Low;
  return (
    <div style={{ display:"inline-flex", alignItems:"center", gap:10, background:c.bg, border:`1px solid ${c.border}`, borderRadius:40, padding:"10px 22px", boxShadow:`0 0 24px ${c.glow}` }}>
      <div style={{ width:10, height:10, borderRadius:"50%", background:c.text, boxShadow:`0 0 10px ${c.text}`, animation:"pulse 2s infinite" }}/>
      <span style={{ color:c.text, fontWeight:700, fontSize:15, letterSpacing:1.5 }}>{c.label}</span>
      {confidence && <span style={{ color:c.text, opacity:0.7, fontSize:13 }}>{Math.round(confidence)}%</span>}
    </div>
  );
}

function ResultCard({ result }) {
  const riskColor = { High:C.red, Medium:C.amber, Low:C.green }[result.risk] || C.accent;
  return (
    <div className="fade-up">
      <div style={{ textAlign:"center", marginBottom:24 }}>
        <RiskBadge risk={result.risk} confidence={result.confidence}/>
      </div>
      {/* Factor rings */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:12, marginBottom:20 }}>
        {[
          { label:"Depression", value:result.depression_factor, color:C.red    },
          { label:"Anxiety",    value:result.anxiety_factor,    color:C.amber  },
          { label:"Isolation",  value:result.social_factor,     color:C.purple },
          { label:"Stress",     value:result.stress_factor,     color:C.accent },
        ].map(f => (
          <CircularProgress key={f.label} value={f.value} max={100} color={f.color} size={64} label={f.label}/>
        ))}
      </div>
      {/* Summary */}
      <div style={{ background:"rgba(255,255,255,0.04)", borderRadius:12, padding:"14px 16px", marginBottom:16, borderLeft:`3px solid ${riskColor}` }}>
        <div style={{ color:C.muted, fontSize:11, letterSpacing:1, marginBottom:8, fontWeight:600 }}>AI CLINICAL SUMMARY</div>
        <div style={{ color:C.text, fontSize:13, lineHeight:1.6 }}>{result.summary}</div>
      </div>
      {/* Recommendations */}
      {result.recommendations && (
        <div>
          <div style={{ color:C.muted, fontSize:11, letterSpacing:1, marginBottom:10, fontWeight:600 }}>RECOMMENDATIONS</div>
          {result.recommendations.map((r,i) => (
            <div key={i} style={{ display:"flex", alignItems:"flex-start", gap:10, marginBottom:8, fontSize:13, color:C.text }}>
              <span style={{ color:riskColor, flexShrink:0 }}>→</span>
              <span>{r}</span>
            </div>
          ))}
        </div>
      )}
      {/* Crisis resources */}
      {result.risk === "High" && (
        <div className="glass" style={{ padding:"16px 20px", marginTop:16, border:"1px solid rgba(248,113,113,0.3)", boxShadow:`0 0 20px ${C.redGlow}` }}>
          <div style={{ color:C.red, fontSize:13, fontWeight:700, marginBottom:12 }}>⚠️ CRISIS RESOURCES</div>
          {[["iCall (India)","+91-9152987821"],["Vandrevala Foundation","1860-2662-345"],["Crisis Text Line (US)","Text HOME to 741741"]].map(([n,c]) => (
            <div key={n} style={{ display:"flex", justifyContent:"space-between", marginBottom:8, fontSize:12 }}>
              <span style={{ color:C.muted }}>{n}</span>
              <span style={{ color:C.red, fontWeight:600 }}>{c}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function ManualAssess({ onNewResult }) {
  const defaults = Object.fromEntries(FEATURES.map(f => [f.key, f.default]));
  const [values, setValues] = useState(defaults);
  const [loading, setLoading] = useState(false);
  const [result, setResult]   = useState(null);
  const [error, setError]     = useState(null);

  const riskColor = result ? { High:C.red, Medium:C.amber, Low:C.green }[result.risk] : C.accent;
  const set = (k, v) => setValues(vv => ({ ...vv, [k]: v }));

  const predict = async () => {
    setLoading(true); setResult(null); setError(null);
    try {
      const res = await predictDirect(values);
      setResult(res);
      onNewResult?.({ ...values, ...res, timestamp: Date.now(), source: "manual" });
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  };

  return (
    <div style={{ display:"grid", gridTemplateColumns:"1fr 380px", gap:20 }} className="fade-up">
      {/* Left: Form */}
      <GlassCard style={{ padding:28 }}>
        <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:24 }}>
          <h2 style={{ margin:0, fontSize:18, fontWeight:600 }}>Patient Assessment</h2>
          <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
            {SAMPLES.map(s => (
              <button key={s.label} onClick={() => { setValues(s.values); setResult(null); }}
                style={{ background:"rgba(255,255,255,0.05)", border:"1px solid rgba(255,255,255,0.1)", borderRadius:8, padding:"6px 12px", color:C.muted, fontSize:11, cursor:"pointer", fontFamily:"'DM Sans',sans-serif" }}>
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {/* Categorical / number inputs */}
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:20 }}>
          {FEATURES.filter(f => f.type !== "range").map(f => (
            <div key={f.key} style={{ display:"flex", flexDirection:"column", gap:8 }}>
              <label style={{ color:C.muted, fontSize:12, letterSpacing:0.5, fontWeight:500 }}>{f.label.toUpperCase()}</label>
              {f.type === "select" ? (
                <select value={values[f.key]} onChange={e => set(f.key, e.target.value)}>
                  {f.options.map(o => <option key={o} value={o}>{o}</option>)}
                </select>
              ) : (
                <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                  <input type="number" min={f.min} max={f.max} value={values[f.key]}
                    onChange={e => set(f.key, Number(e.target.value))}
                    style={{ flex:1, background:"rgba(255,255,255,0.06)", border:"1px solid var(--border)", borderRadius:10, padding:"8px 12px", color:C.text, fontFamily:"'DM Sans',sans-serif", fontSize:14, outline:"none" }}
                  />
                  {f.unit && <span style={{ color:C.dim, fontSize:12 }}>{f.unit}</span>}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Range sliders */}
        <div style={{ marginTop:24 }}>
          <h3 style={{ color:C.muted, fontSize:12, letterSpacing:1, fontWeight:600, marginBottom:18, marginTop:0 }}>CLINICAL SCORES</h3>
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:20 }}>
            {FEATURES.filter(f => f.type === "range").map(f => {
              const pct = (values[f.key] - f.min) / (f.max - f.min);
              // Inverted: more = good (sleep, exercise, social, productivity)
              // Normal:   more = bad (stress, depression, anxiety)
              const color = f.inverted
                ? (pct > 0.6 ? C.green : pct > 0.3 ? C.amber : C.red)
                : (pct > 0.6 ? C.red   : pct > 0.3 ? C.amber : C.green);
              const pctLabel = Math.round(pct * 100);
              const suffix = f.max <= 10 ? "/10" : f.max <= 21 ? "/21" : f.max <= 12 ? "h" : f.max <= 30 ? "/30" : "/100";
              return (
                <div key={f.key}>
                  <div style={{ display:"flex", justifyContent:"space-between", marginBottom:8 }}>
                    <label style={{ color:C.muted, fontSize:12 }}>{f.label}</label>
                    <div style={{ display:"flex", alignItems:"center", gap:6 }}>
                      <span style={{ color, fontSize:13, fontWeight:700 }}>{values[f.key]}{suffix}</span>
                      <span style={{ color, fontSize:10, opacity:0.7, background:`${color}22`, borderRadius:10, padding:"1px 6px" }}>{pctLabel}%</span>
                    </div>
                  </div>
                  <RangeSlider value={values[f.key]} onChange={v => set(f.key, v)} min={f.min} max={f.max} step={f.step||1} color={color}/>
                </div>
              );
            })}
          </div>
        </div>

        {/* Error */}
        {error && <div style={{ marginTop:16, padding:"12px 16px", background:"rgba(248,113,113,0.1)", border:"1px solid rgba(248,113,113,0.3)", borderRadius:12, color:C.red, fontSize:13 }}>⚠️ {error}</div>}

        <div style={{ marginTop:28, display:"flex", gap:12 }}>
          <button className="btn-primary" onClick={predict} disabled={loading} style={{ flex:1 }}>
            {loading
              ? <span style={{ display:"flex", alignItems:"center", justifyContent:"center", gap:10 }}>
                  <span style={{ display:"inline-block", width:16, height:16, border:"2px solid rgba(255,255,255,0.3)", borderTop:"2px solid #fff", borderRadius:"50%", animation:"spin 0.8s linear infinite" }}/>
                  Analyzing...
                </span>
              : "🔍 Predict Mental Health Risk"}
          </button>
          <button className="neu-btn" onClick={() => { setValues(defaults); setResult(null); setError(null); }} style={{ padding:"16px 20px" }}>
            Reset
          </button>
        </div>
      </GlassCard>

      {/* Right: Results */}
      <div style={{ display:"flex", flexDirection:"column", gap:18 }}>
        <GlassCard glow={result ? `${riskColor}33` : undefined} style={{ padding:24 }}>
          {!result && !loading && (
            <div style={{ textAlign:"center", padding:"48px 0", color:C.dim }}>
              <div style={{ fontSize:48, marginBottom:16 }}>🩺</div>
              <div style={{ fontSize:14 }}>Fill in the form and click Predict</div>
            </div>
          )}
          {loading && (
            <div style={{ textAlign:"center", padding:"48px 0" }}>
              <div style={{ fontSize:40, animation:"pulse 1.5s infinite", marginBottom:16 }}>🧠</div>
              <div style={{ color:C.muted, fontSize:13 }}>AI analyzing patient profile...</div>
            </div>
          )}
          {result && !loading && <ResultCard result={result}/>}
        </GlassCard>
      </div>
    </div>
  );
}

// Export ResultCard for use in EmpathyChat too
export { ResultCard, RiskBadge, CircularProgress };
