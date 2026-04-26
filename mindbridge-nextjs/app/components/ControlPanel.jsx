"use client";
import { useState, useEffect, useRef, useCallback } from "react";

const API = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5002";

// Known models — shown even if not in `ollama list` (cloud models etc.)
const KNOWN_CLOUD_MODELS = [
  // Cloud
  "gpt-oss:120b-cloud",
  "gpt-oss:20b-cloud",
  "gemma4:31b-cloud",
  "deepseek-v3.2:cloud",
  "glm-5.1:cloud",
  "cogito-2.1:671b-cloud",
  "nemotron-3-super:cloud",
  "qwen3.5:cloud",
  "qwen3.5:397b-cloud",
  // Local
  "deepseek-r1:7b",
  "deepseek-r1:14b",
  "llama3.2:3b",
  "llama3.1:8b",
  "mistral:7b",
  "granite3.1-moe:3b",
];

// ── helpers ──────────────────────────────────────────────────────────────────
const get  = (url) => fetch(`${API}${url}`).then(r => r.json());
const post = (url, body) => fetch(`${API}${url}`, {
  method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)
}).then(r => r.json());

function Section({ title, icon, children }) {
  return (
    <div className="glass" style={{ padding:24, marginBottom:18 }}>
      <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:18, borderBottom:"1px solid var(--border)", paddingBottom:14 }}>
        <span style={{ fontSize:20 }}>{icon}</span>
        <span style={{ fontWeight:700, fontSize:15, color:"var(--text)", letterSpacing:0.3 }}>{title}</span>
      </div>
      {children}
    </div>
  );
}

function StatusDot({ ok }) {
  return (
    <span style={{
      display:"inline-block", width:8, height:8, borderRadius:"50%",
      background: ok ? "var(--green)" : "var(--red)",
      boxShadow: ok ? "0 0 8px var(--green-glow)" : "0 0 8px var(--red-glow)",
      animation:"pulse 2s infinite", marginRight:6,
    }}/>
  );
}

function MetricRow({ label, value, color }) {
  return (
    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", padding:"8px 0", borderBottom:"1px solid var(--border)" }}>
      <span style={{ color:"var(--text-muted)", fontSize:13 }}>{label}</span>
      <span style={{ color: color || "var(--accent)", fontSize:13, fontWeight:700 }}>{value ?? "—"}</span>
    </div>
  );
}

// ── Main ─────────────────────────────────────────────────────────────────────
export default function ControlPanel() {
  const [health,       setHealth]       = useState(null);
  const [models,       setModels]       = useState([]);
  const [activeModel,  setActiveModel]  = useState("");
  const [switchStatus, setSwitchStatus] = useState(null);
  const [customModel,  setCustomModel]  = useState("");
  const [retrain,      setRetrain]      = useState({ running:false, log:[], success:null, started_at:null, finished_at:null, metrics:{} });
  const [loading,      setLoading]      = useState(true);
  const [error,        setError]        = useState(null);
  const logRef = useRef(null);
  const pollRef = useRef(null);

  // ── fetch health ────────────────────────────────────────────────────────
  const fetchHealth = useCallback(async () => {
    try {
      const h = await get("/health");
      setHealth(h);
      // Always sync active model from backend (not just on first load)
      if (h.current_model) setActiveModel(h.current_model);
      // Merge Ollama API models with our known list (deduplicated)
      const apiModels = h.available_models || [];
      const merged = [...new Set([...apiModels, ...KNOWN_CLOUD_MODELS])];
      setModels(merged);
      setError(null);
    } catch {
      setError("Backend offline — start the backend server first.");
      setModels(KNOWN_CLOUD_MODELS);
    } finally {
      setLoading(false);
    }
  }, []); // no deps — always reads fresh from backend

  useEffect(() => { fetchHealth(); }, []);

  // ── auto-scroll log ─────────────────────────────────────────────────────
  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [retrain.log]);

  // ── poll retrain status ─────────────────────────────────────────────────
  const startPolling = useCallback(() => {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const s = await get("/retrain-status");
        setRetrain(s);
        if (!s.running) {
          clearInterval(pollRef.current);
          fetchHealth(); // refresh metrics after retrain
        }
      } catch {}
    }, 1500);
  }, [fetchHealth]);

  useEffect(() => () => clearInterval(pollRef.current), []);

  // ── actions ─────────────────────────────────────────────────────────────
  const handleSwitchModel = async (model) => {
    setSwitchStatus({ loading:true, msg:"" });
    try {
      const r = await post("/set-model", { model });
      if (r.success) {
        setActiveModel(model);  // immediately update UI
        setHealth(h => h ? { ...h, current_model: model } : h); // sync health card
      }
      setSwitchStatus({ loading:false, msg: r.success ? `✅ Switched to ${model}` : `❌ ${r.detail || "Failed"}`, ok: r.success });
      setTimeout(() => setSwitchStatus(null), 3000);
    } catch (e) {
      setSwitchStatus({ loading:false, msg:`❌ ${e.message}`, ok:false });
    }
  };

  const handleRetrain = async () => {
    setRetrain(r => ({ ...r, running:true, log:["Starting retrain..."], success:null }));
    try {
      const r = await post("/retrain", {});
      if (!r.success) {
        setRetrain(s => ({ ...s, running:false, log:[`❌ ${r.message || r.detail}`], success:false }));
        return;
      }
      startPolling();
    } catch (e) {
      setRetrain(s => ({ ...s, running:false, log:[`❌ ${e.message}`], success:false }));
    }
  };

  // ── UI ───────────────────────────────────────────────────────────────────
  if (loading) return (
    <div style={{ textAlign:"center", padding:80, color:"var(--text-muted)" }}>
      <div style={{ fontSize:36, marginBottom:12, animation:"pulse 1.5s infinite" }}>⚙️</div>
      <div>Connecting to backend...</div>
    </div>
  );

  if (error) return (
    <div className="glass" style={{ padding:36, textAlign:"center" }}>
      <div style={{ fontSize:36, marginBottom:12 }}>🔴</div>
      <div style={{ color:"var(--red)", fontSize:15, fontWeight:600, marginBottom:8 }}>Backend Offline</div>
      <div style={{ color:"var(--text-muted)", fontSize:13, marginBottom:20 }}>{error}</div>
      <button className="btn-primary" style={{ padding:"12px 28px" }} onClick={fetchHealth}>Retry Connection</button>
    </div>
  );

  const dtcMetrics = health?.dtc_metrics || {};
  const ollama = health?.ollama || {};

  return (
    <div className="fade-up" style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:18 }}>

      {/* ── Left column ── */}
      <div>
        {/* System Status */}
        <Section title="System Status" icon="🖥️">
          <MetricRow label="Backend"      value={<><StatusDot ok={true}/> Online</>} />
          <MetricRow label="Ollama"       value={<><StatusDot ok={ollama.available}/>{ollama.available ? "Running" : "Offline"}</>} />
          <MetricRow label="Active Model" value={health?.current_model || "—"} color="var(--accent)" />
          <MetricRow label="DTC Model"    value={<><StatusDot ok={health?.dtc_loaded}/>{health?.dtc_loaded ? "Loaded" : "Fallback"}</>} />
          <MetricRow label="API Version"  value={health?.version} />
          <div style={{ marginTop:14 }}>
            <button
              className="neu-btn"
              style={{ width:"100%", padding:"10px 0", fontSize:13 }}
              onClick={fetchHealth}
            >
              🔄 Refresh Status
            </button>
          </div>
        </Section>

        {/* DTC Metrics */}
        <Section title="DTC Model Metrics" icon="📈">
          {Object.keys(dtcMetrics).length === 0 ? (
            <div style={{ color:"var(--text-muted)", fontSize:13 }}>No metrics available</div>
          ) : (
            <>
              {dtcMetrics.accuracy     != null && <MetricRow label="Accuracy"         value={`${(dtcMetrics.accuracy * 100).toFixed(1)}%`}         color="var(--green)" />}
              {dtcMetrics.precision_macro != null && <MetricRow label="Precision (Macro)" value={`${(dtcMetrics.precision_macro * 100).toFixed(1)}%`} color="var(--accent)" />}
              {dtcMetrics.recall_macro   != null && <MetricRow label="Recall (Macro)"    value={`${(dtcMetrics.recall_macro * 100).toFixed(1)}%`}   color="var(--accent)" />}
              {dtcMetrics.f1_macro       != null && <MetricRow label="F1-Score (Macro)"  value={`${(dtcMetrics.f1_macro * 100).toFixed(1)}%`}       color="var(--purple)" />}
              {dtcMetrics.mse            != null && <MetricRow label="MSE"               value={dtcMetrics.mse?.toFixed(4)}                          color="var(--amber)"  />}
              {dtcMetrics.mae            != null && <MetricRow label="MAE"               value={dtcMetrics.mae?.toFixed(4)}                          color="var(--amber)"  />}
              {dtcMetrics.r2_score       != null && <MetricRow label="R² Score"          value={dtcMetrics.r2_score?.toFixed(4)}                     color="var(--green)"  />}
              {["Low","Medium","High"].filter(l => dtcMetrics[`precision_${l}`] != null).map(l => (
                <MetricRow key={l} label={`F1 — ${l} Risk`} value={`${(dtcMetrics[`f1_${l}`]*100).toFixed(1)}%`}
                  color={l==="High"?"var(--red)":l==="Medium"?"var(--amber)":"var(--green)"} />
              ))}
            </>
          )}
        </Section>
      </div>

      {/* ── Right column ── */}
      <div>
        {/* Model Switcher */}
        <Section title="Ollama Model Switcher" icon="🤖">
          <div style={{ color:"var(--text-muted)", fontSize:12, marginBottom:14, lineHeight:1.6 }}>
            Switch the LLM used for interviews and scoring without restarting the backend.
            Currently active: <strong style={{ color:"var(--accent)" }}>{health?.current_model}</strong>
          </div>

          {models.length === 0 ? (
            <div style={{ color:"var(--text-dim)", fontSize:13 }}>
              No Ollama models found. Run: <code style={{ background:"rgba(255,255,255,0.08)", padding:"2px 6px", borderRadius:4 }}>ollama pull deepseek-r1:7b</code>
            </div>
          ) : (
            <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
              {models.map(m => (
                <div
                  key={m}
                  style={{
                    display:"flex", alignItems:"center", justifyContent:"space-between",
                    padding:"10px 14px", borderRadius:12,
                    background: m === activeModel ? "rgba(108,142,255,0.12)" : "var(--surface)",
                    border: `1px solid ${m === activeModel ? "rgba(108,142,255,0.35)" : "var(--border)"}`,
                    transition:"all 0.2s",
                  }}
                >
                  <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                    {m === activeModel && <StatusDot ok={true}/>}
                    <span style={{ color:"var(--text)", fontSize:13, fontWeight: m === activeModel ? 700 : 400 }}>{m}</span>
                    {m === activeModel && <span style={{ fontSize:10, color:"var(--accent)", background:"rgba(108,142,255,0.12)", padding:"2px 8px", borderRadius:10 }}>ACTIVE</span>}
                  </div>
                  {m !== activeModel && (
                    <button
                      className="neu-btn"
                      style={{ padding:"6px 14px", fontSize:12 }}
                      disabled={switchStatus?.loading}
                      onClick={() => handleSwitchModel(m)}
                    >
                      Use
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}

          {switchStatus && (
            <div style={{
              marginTop:12, padding:"10px 14px", borderRadius:10, fontSize:13,
              background: switchStatus.ok ? "rgba(74,222,128,0.1)" : "rgba(248,113,113,0.1)",
              border: `1px solid ${switchStatus.ok ? "rgba(74,222,128,0.3)" : "rgba(248,113,113,0.3)"}`,
              color: switchStatus.ok ? "var(--green)" : "var(--red)",
            }}>
              {switchStatus.loading ? "Switching..." : switchStatus.msg}
            </div>
          )}

          {/* Custom model input */}
          <div style={{ marginTop:14, borderTop:"1px solid var(--border)", paddingTop:14 }}>
            <div style={{ color:"var(--text-muted)", fontSize:11, letterSpacing:0.5, marginBottom:8, fontWeight:600 }}>
              CUSTOM MODEL NAME
            </div>
            <div style={{ display:"flex", gap:8 }}>
              <input
                type="text"
                placeholder="e.g. llama3.3:70b-cloud"
                value={customModel}
                onChange={e => setCustomModel(e.target.value)}
                onKeyDown={e => e.key === "Enter" && customModel.trim() && handleSwitchModel(customModel.trim())}
                style={{
                  flex:1, background:"var(--surface)", border:"1px solid var(--border)",
                  borderRadius:10, padding:"8px 12px", color:"var(--text)",
                  fontFamily:"'DM Sans',sans-serif", fontSize:13, outline:"none",
                }}
              />
              <button
                className="neu-btn"
                style={{ padding:"8px 16px", fontSize:12, whiteSpace:"nowrap" }}
                disabled={!customModel.trim() || switchStatus?.loading}
                onClick={() => customModel.trim() && handleSwitchModel(customModel.trim())}
              >
                Use
              </button>
            </div>
            <div style={{ color:"var(--text-dim)", fontSize:11, marginTop:6 }}>
              Type any model name and press Enter or Use. Works for any Ollama local or cloud model.
            </div>
          </div>
        </Section>

        {/* Retrain */}
        <Section title="Retrain Model" icon="🔁">
          <div style={{ color:"var(--text-muted)", fontSize:12, lineHeight:1.6, marginBottom:16 }}>
            Runs <code style={{ background:"rgba(255,255,255,0.08)", padding:"2px 6px", borderRadius:4 }}>mental_health_ml_system.py</code> to retrain the DTC from scratch on the dataset.
            Model is hot-reloaded on completion. Training takes ~30–60 seconds.
          </div>

          <button
            className="btn-primary"
            style={{ width:"100%", marginBottom:14, opacity: retrain.running ? 0.6 : 1 }}
            disabled={retrain.running}
            onClick={handleRetrain}
          >
            {retrain.running
              ? <span style={{ display:"flex", alignItems:"center", justifyContent:"center", gap:10 }}>
                  <span style={{ display:"inline-block", width:16, height:16, border:"2px solid rgba(255,255,255,0.3)", borderTop:"2px solid #fff", borderRadius:"50%", animation:"spin 0.8s linear infinite" }}/>
                  Training in progress...
                </span>
              : "🚀 Start Retrain"}
          </button>

          {/* Status strip */}
          {(retrain.success !== null || retrain.running) && (
            <div style={{
              padding:"8px 14px", borderRadius:10, fontSize:12, marginBottom:10,
              background: retrain.running ? "rgba(108,142,255,0.08)"
                        : retrain.success ? "rgba(74,222,128,0.10)"
                        : "rgba(248,113,113,0.10)",
              border: `1px solid ${retrain.running ? "rgba(108,142,255,0.25)"
                                 : retrain.success ? "rgba(74,222,128,0.3)"
                                 : "rgba(248,113,113,0.3)"}`,
              color: retrain.running ? "var(--accent)"
                   : retrain.success ? "var(--green)" : "var(--red)",
            }}>
              {retrain.running
                ? `⏳ Running since ${retrain.started_at || "just now"}...`
                : retrain.success
                  ? `✅ Completed at ${retrain.finished_at} · Accuracy: ${retrain.metrics?.accuracy != null ? (retrain.metrics.accuracy*100).toFixed(1)+"%" : "see metrics"}`
                  : `❌ Failed at ${retrain.finished_at}`}
            </div>
          )}

          {/* Log console */}
          {retrain.log.length > 0 && (
            <div
              ref={logRef}
              style={{
                background:"rgba(0,0,0,0.35)", borderRadius:12, padding:"12px 14px",
                maxHeight:220, overflowY:"auto", fontFamily:"'Courier New',monospace", fontSize:11,
                lineHeight:1.7, border:"1px solid var(--border)",
              }}
            >
              {retrain.log.map((line, i) => {
                const isErr = line.toLowerCase().includes("error") || line.includes("❌");
                const isOk  = line.includes("✅") || line.includes("[MindBridge] Model reloaded");
                return (
                  <div key={i} style={{ color: isErr ? "var(--red)" : isOk ? "var(--green)" : "rgba(200,210,255,0.8)" }}>
                    {line}
                  </div>
                );
              })}
              {retrain.running && (
                <div style={{ display:"flex", gap:4, marginTop:6 }}>
                  <span className="typing-dot"/>
                  <span className="typing-dot"/>
                  <span className="typing-dot"/>
                </div>
              )}
            </div>
          )}
        </Section>
      </div>
    </div>
  );
}
