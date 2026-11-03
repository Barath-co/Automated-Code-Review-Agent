import React from "react";
import { CheckCircle, Clock, Cpu, Coins, ShieldCheck, Scale, Database, HelpCircle } from "lucide-react";
import ConsensusMatrix from "./ConsensusMatrix";
import OrchestrationModuleView from "./OrchestrationModuleView";
import ModelAdaptersView from "./ModelAdaptersView";

export default function TechnicalDetailsSection({ report, language }) {
  if (!report) return null;

  const metrics = report.metrics || {};
  const validation = report.validation || {};

  return (
    <div className="card tech-details-container">
      {/* Telemetry Metrics Bar */}
      <div className="tech-telemetry-row">
        <div className="tech-stat">
          <div className="tech-stat-icon text-blue">
            <Clock size={16} />
          </div>
          <div className="tech-stat-meta">
            <span className="tech-stat-label">Response Time</span>
            <span className="tech-stat-val">{metrics.total_latency_ms || 0} ms</span>
          </div>
        </div>

        <div className="tech-stat">
          <div className="tech-stat-icon text-purple">
            <Cpu size={16} />
          </div>
          <div className="tech-stat-meta">
            <span className="tech-stat-label">Reviewers Dispatched</span>
            <span className="tech-stat-val">{metrics.agents_dispatched || 3} Specialists</span>
          </div>
        </div>

        <div className="tech-stat">
          <div className="tech-stat-icon text-green">
            <Database size={16} />
          </div>
          <div className="tech-stat-meta">
            <span className="tech-stat-label">Token Footprint</span>
            <span className="tech-stat-val">{(metrics.total_tokens || 0).toLocaleString()} tokens</span>
          </div>
        </div>

        <div className="tech-stat">
          <div className="tech-stat-icon text-amber">
            <Coins size={16} />
          </div>
          <div className="tech-stat-meta">
            <span className="tech-stat-label">Estimated Cost</span>
            <span className="tech-stat-val">₹{metrics.estimated_cost_inr || 0} INR</span>
          </div>
        </div>
      </div>

      {/* Consensus & AST Verification */}
      <div className="tech-consensus-strip">
        <div className="strip-item">
          <span className="strip-label">Consensus Score:</span>
          <span className="strip-value font-bold">{report.consensus?.consensus_score ?? 100}%</span>
          <span className="strip-sub">({report.consensus?.strength?.replace(/_/g, " ")})</span>
        </div>
        <div className="strip-divider"></div>
        <div className="strip-item">
          <span className="strip-label">Deterministic AST:</span>
          <span className={`strip-pill ${validation.syntax_valid ? "pill-pass" : "pill-warn"}`}>
            {validation.syntax_valid ? "Syntax Valid" : "Syntax Flagged"}
          </span>
        </div>
        <div className="strip-divider"></div>
        <div className="strip-item">
          <span className="strip-label">Task Identifier:</span>
          <code className="strip-code">{report.task_id}</code>
        </div>
      </div>

      {/* Consensus & Disagreements Breakdown */}
      <ConsensusMatrix
        consensus={report.consensus}
        validation={report.validation}
        humanReviewRequired={report.human_review_required}
        executiveVerdict={report.executive_verdict}
      />
    </div>
  );
}
