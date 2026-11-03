import React from "react";
import { Clock, Cpu, Coins, ShieldCheck, Download, FileText, Database } from "lucide-react";

export default function MetricsBar({ metrics, taskId, onExportMarkdown, onExportJson }) {
  if (!metrics) return null;

  return (
    <div className="card metrics-bar-card">
      <div className="metrics-grid">
        {/* Latency */}
        <div className="metric-box">
          <div className="metric-icon-wrap text-cyan-400">
            <Clock size={16} />
          </div>
          <div className="metric-content">
            <span className="metric-label">Execution Latency</span>
            <span className="metric-value">{metrics.total_latency_ms} ms</span>
          </div>
        </div>

        {/* Agents Dispatched */}
        <div className="metric-box">
          <div className="metric-icon-wrap text-purple-400">
            <Cpu size={16} />
          </div>
          <div className="metric-content">
            <span className="metric-label">Agents Dispatched</span>
            <span className="metric-value">{metrics.agents_dispatched} Specialists</span>
          </div>
        </div>

        {/* Token Usage */}
        <div className="metric-box">
          <div className="metric-icon-wrap text-emerald-400">
            <Database size={16} />
          </div>
          <div className="metric-content">
            <span className="metric-label">Token Footprint</span>
            <span className="metric-value">
              {metrics.total_tokens.toLocaleString()} <span className="metric-sub-value">({metrics.prompt_tokens} in / {metrics.completion_tokens} out)</span>
            </span>
          </div>
        </div>

        {/* Cost Telemetry (Table 4.4) */}
        <div className="metric-box">
          <div className="metric-icon-wrap text-amber-400">
            <Coins size={16} />
          </div>
          <div className="metric-content">
            <span className="metric-label">Estimated Cost (INR / Table 4.4)</span>
            <span className="metric-value">
              ₹{metrics.estimated_cost_inr} <span className="metric-sub-value">(${metrics.estimated_cost_usd} USD)</span>
            </span>
          </div>
        </div>
      </div>

      {/* Export Report Actions */}
      <div className="metrics-actions-row">
        <span className="task-id-badge">Task ID: {taskId}</span>
        <div className="export-btns-group">
          <button 
            onClick={onExportMarkdown} 
            className="btn-export"
            title="Download full project markdown audit report for Viva Voce"
          >
            <FileText size={14} />
            <span>Export Viva Report (.md)</span>
          </button>
          <button 
            onClick={onExportJson} 
            className="btn-export-secondary"
            title="Export full JSON schema payload"
          >
            <Download size={14} />
            <span>JSON</span>
          </button>
        </div>
      </div>
    </div>
  );
}
