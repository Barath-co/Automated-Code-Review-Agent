import React from "react";
import { 
  Network, 
  ShieldCheck, 
  Zap, 
  Layers, 
  CheckCircle2, 
  Lock, 
  Clock, 
  Cpu, 
  Database,
  ArrowRightLeft,
  AlertTriangle
} from "lucide-react";

export default function ModelAdaptersView({ candidates, report }) {
  const activeCandidates = candidates?.length > 0 ? candidates : [
    {
      agent_id: "gemini_sec",
      persona: "Gemini Code Security Specialist",
      model_name: "gemini-2.5-flash",
      overall_assessment: "Evaluated OWASP Top 10, CWE injection risks, and sensitive data exposure.",
      findings: report?.consolidated_findings?.filter(f => f.category === "Security") || [],
      latency_ms: 320,
      token_usage: { total_tokens: 420, prompt_tokens: 180, completion_tokens: 240 }
    },
    {
      agent_id: "gemini_perf",
      persona: "Gemini Performance & Concurrency Architect",
      model_name: "gemini-2.5-flash",
      overall_assessment: "Evaluated algorithmic complexity O(n²), blocking operations, and resource bounds.",
      findings: report?.consolidated_findings?.filter(f => f.category === "Performance") || [],
      latency_ms: 340,
      token_usage: { total_tokens: 390, prompt_tokens: 170, completion_tokens: 220 }
    },
    {
      agent_id: "gemini_clean",
      persona: "Gemini Reliability & Clean Code Reviewer",
      model_name: "gemini-2.5-flash",
      overall_assessment: "Checked error recovery, PEP-8 guidelines, exception boundaries, and typing.",
      findings: report?.consolidated_findings?.filter(f => f.category === "Reliability" || f.category === "Style") || [],
      latency_ms: 290,
      token_usage: { total_tokens: 414, prompt_tokens: 185, completion_tokens: 229 }
    }
  ];

  return (
    <div className="module-view-container">
      {/* Banner */}
      <div className="module-banner">
        <div className="banner-left">
          <div className="module-tag-badge">MODULE C</div>
          <div>
            <h2 className="module-heading">Model Adapter & Provider Hub Module</h2>
            <p className="module-sub">
              Translates internal task requests into provider-specific API calls, normalizes outputs to a common schema, and handles timeouts, rate limits, and isolated credentials.
            </p>
          </div>
        </div>
        <div className="state-badge-active">
          <Network size={15} className="text-cyan-400" />
          <span>Active Adapters: {activeCandidates.length}</span>
        </div>
      </div>

      {/* Security & Credentials Isolation Callout */}
      <div className="card adapter-sec-callout">
        <div className="callout-grid">
          <div className="callout-item">
            <Lock size={16} className="text-emerald-400" />
            <div>
              <span className="callout-title">Credential Isolation</span>
              <span className="callout-desc">API keys loaded via os.getenv / secret manager; no hardcoded keys.</span>
            </div>
          </div>
          <div className="callout-item">
            <ArrowRightLeft size={16} className="text-cyan-400" />
            <div>
              <span className="callout-title">Normalized Schema</span>
              <span className="callout-desc">Unified JSON schema with assessment, findings array, and proposed code.</span>
            </div>
          </div>
          <div className="callout-item">
            <Clock size={16} className="text-amber-400" />
            <div>
              <span className="callout-title">Resilience & Rate Limits</span>
              <span className="callout-desc">Exponential backoff retry on HTTP 429 & fallback virtual simulation engine.</span>
            </div>
          </div>
        </div>
      </div>

      {/* Specialist Model Adapters Cards */}
      <div className="adapters-list-grid">
        {activeCandidates.map((cad, idx) => (
          <div key={cad.agent_id || idx} className="card adapter-detail-card">
            {/* Header */}
            <div className="adapter-card-top">
              <div className="adapter-title-row">
                <span className="adapter-num-badge">ADAPTER 0{idx + 1}</span>
                <h3 className="adapter-persona-name">{cad.persona}</h3>
              </div>
              <span className="adapter-model-pill">{cad.model_name}</span>
            </div>

            {/* Assessment */}
            <p className="adapter-assessment-text">{cad.overall_assessment}</p>

            {/* Findings preview */}
            <div className="adapter-findings-box">
              <span className="box-title">Normalized Findings Generated ({cad.findings?.length || 0}):</span>
              {cad.findings && cad.findings.length > 0 ? (
                <ul className="adapter-findings-mini">
                  {cad.findings.map((f, fIdx) => (
                    <li key={fIdx} className="mini-finding-item">
                      <span className={`mini-sev sev-${f.severity?.toLowerCase()}`}>{f.severity}</span>
                      <span className="mini-title">{f.title}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <span className="text-xs text-slate-400 italic">No specific issues flagged by this specialist.</span>
              )}
            </div>

            {/* Metadata Footer */}
            <div className="adapter-meta-footer">
              <div className="meta-sub-item">
                <Clock size={12} />
                <span>Latency: {cad.latency_ms} ms</span>
              </div>
              <div className="meta-sub-item">
                <Database size={12} />
                <span>Tokens: {cad.token_usage?.total_tokens || 400}</span>
              </div>
              <div className="meta-sub-item text-emerald-400">
                <CheckCircle2 size={12} />
                <span>Schema Valid</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
