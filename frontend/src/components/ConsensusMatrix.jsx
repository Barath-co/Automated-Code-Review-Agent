import React, { useState } from "react";
import { CheckCircle, AlertTriangle, Scale, ShieldCheck, HelpCircle, ChevronDown, ChevronUp, Info } from "lucide-react";

export default function ConsensusMatrix({ consensus, validation, humanReviewRequired, executiveVerdict }) {
  const [showConflictDetails, setShowConflictDetails] = useState(true);

  if (!consensus) return null;

  const score = consensus.consensus_score ?? 100;
  const strengthClass = 
    consensus.strength === "STRONG_AGREEMENT" ? "strength-strong" :
    consensus.strength === "MODERATE_AGREEMENT" ? "strength-moderate" : "strength-divergent";

  return (
    <div className="card consensus-card">
      <div className="consensus-top-row">
        {/* Score & Gauge Section */}
        <div className="consensus-dial-zone">
          <div className="score-container">
            <span className="score-number">{score}%</span>
            <span className="score-label">Consensus Score</span>
          </div>
          <div className="strength-wrapper">
            <span className={`strength-badge ${strengthClass}`}>
              <Scale size={13} className="inline-icon" />
              {consensus.strength?.replace(/_/g, " ")}
            </span>
            <span className="consensus-sub">
              Cross-model evaluation across specialist personas
            </span>
          </div>
        </div>

        {/* AST Gate Indicator */}
        <div className="ast-gate-zone">
          <div className={`ast-status-box ${validation?.syntax_valid ? "ast-valid" : "ast-invalid"}`}>
            <ShieldCheck size={20} />
            <div>
              <span className="ast-title">Deterministic AST Engine</span>
              <span className="ast-desc">
                {validation?.syntax_valid ? "Syntax Valid • Rules Grounded" : "Syntax Issues Flagged"}
              </span>
            </div>
          </div>
        </div>

        {/* Human Escalation Flag */}
        {humanReviewRequired && (
          <div className="escalation-alert-zone">
            <div className="escalation-pill">
              <AlertTriangle size={16} />
              <div>
                <span className="escalation-title">Human Verification Advised</span>
                <span className="escalation-desc">Critical issues or contested claims require peer review</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Executive Verdict Banner */}
      {executiveVerdict && (
        <div className="executive-verdict-banner">
          <div className="verdict-icon">
            <Info size={16} />
          </div>
          <p className="verdict-text">{executiveVerdict}</p>
        </div>
      )}

      {/* Agreed Findings Grid */}
      <div className="consensus-body-grid">
        <div className="agreed-points-col">
          <div className="col-header">
            <CheckCircle size={15} className="text-emerald-400" />
            <span>Mutual Agent Agreement ({consensus.agreed_points?.length || 0})</span>
          </div>
          {consensus.agreed_points && consensus.agreed_points.length > 0 ? (
            <ul className="agreed-list">
              {consensus.agreed_points.map((pt, idx) => (
                <li key={idx} className="agreed-item">
                  <span className="checkmark-bullet">✓</span>
                  <span>{pt}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty-notice">No overlapping concerns found across multiple agents.</p>
          )}
        </div>

        {/* Contested / Divergent Issues Section */}
        <div className="conflicts-col">
          <div className="col-header">
            <AlertTriangle size={15} className="text-amber-400" />
            <span>Material Discrepancies & Mediation ({consensus.conflicts?.length || 0})</span>
          </div>
          {consensus.conflicts && consensus.conflicts.length > 0 ? (
            <div className="conflicts-container">
              {consensus.conflicts.map((conf, idx) => (
                <div key={idx} className="conflict-card">
                  <div className="conflict-topic">
                    <span className="conflict-type-pill">{conf.conflict_type}</span>
                    <span className="topic-text">{conf.topic}</span>
                  </div>
                  <div className="agent-positions">
                    {Object.entries(conf.agent_claims || {}).map(([agent, claim]) => (
                      <div key={agent} className="agent-claim-row">
                        <span className="claim-agent">{agent}:</span>
                        <span className="claim-content">{claim}</span>
                      </div>
                    ))}
                  </div>
                  <div className="conflict-resolution">
                    <span className="resolution-label">NCIO Mediation:</span>
                    <span className="resolution-text">{conf.resolution}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-notice text-emerald-400">
              No contentious contradictions detected among candidate agent streams.
            </p>
          )}
        </div>
      </div>

      {/* Academic Methodology Citation Callout */}
      <div className="academic-footnote">
        <HelpCircle size={13} className="text-slate-400" />
        <span>
          <strong>NCIO Principle (Section 2.4 & 4.3):</strong> "Agreement alone does not prove correctness. 
          Consensus serves as a prioritization signal combined with deterministic AST validation to suppress shared hallucinations."
        </span>
      </div>
    </div>
  );
}
