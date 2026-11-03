import React from "react";
import { CheckCircle2, AlertTriangle, XCircle, ShieldCheck, Download, FileText, ChevronRight } from "lucide-react";

export default function ReviewSummary({ report, onExportMarkdown, onExportJson }) {
  if (!report) return null;

  const findings = report.consolidated_findings || [];
  const count = (s) => findings.filter(f => f.severity?.toLowerCase() === s).length;
  const critical = count("critical");
  const high = count("high");
  const medium = count("medium");
  const low = count("low") + count("info");

  const verdict = (critical > 0 || high > 0)
    ? { 
        text: "Not ready to merge", 
        tone: "bad", 
        icon: XCircle,
        subtext: "Critical security or stability risks must be fixed prior to deployment." 
      }
    : medium > 0
    ? { 
        text: "Merge after fixes", 
        tone: "warn", 
        icon: AlertTriangle,
        subtext: "Code has maintainability or performance issues recommended for cleanup." 
      }
    : { 
        text: "Looks safe to merge", 
        tone: "good", 
        icon: CheckCircle2,
        subtext: "Code meets safety, reliability, and syntax validation standards." 
      };

  const VerdictIcon = verdict.icon;

  return (
    <div className={`card summary-card summary-${verdict.tone}`}>
      <div className="summary-main-row">
        <div className="summary-left">
          <div className="verdict-icon-bubble">
            <VerdictIcon size={24} />
          </div>
          <div className="verdict-text-block">
            <div className="verdict-heading-row">
              <h2 className="verdict-title">{verdict.text}</h2>
              <span className={`verdict-pill verdict-pill-${verdict.tone}`}>
                {report.consensus?.consensus_score ?? 100}% Reviewer Agreement
              </span>
            </div>
            <p className="verdict-subtitle">
              {findings.length === 0 ? "No issues detected" : `${findings.length} issues identified`} · {verdict.subtext}
            </p>
          </div>
        </div>

        <div className="summary-actions">
          <button 
            onClick={onExportMarkdown} 
            className="btn-export-clean"
            title="Download complete report for your team"
          >
            <FileText size={14} />
            <span>Export report</span>
          </button>
          <button 
            onClick={onExportJson} 
            className="btn-export-subtle"
            title="Export raw JSON data"
          >
            <Download size={14} />
            <span>JSON</span>
          </button>
        </div>
      </div>

      <div className="summary-breakdown-row">
        <div className="sev-pills-row">
          <span className={`sev-tag sev-critical ${critical === 0 ? "sev-zero" : ""}`}>
            <strong>{critical}</strong> Critical
          </span>
          <span className={`sev-tag sev-high ${high === 0 ? "sev-zero" : ""}`}>
            <strong>{high}</strong> High
          </span>
          <span className={`sev-tag sev-medium ${medium === 0 ? "sev-zero" : ""}`}>
            <strong>{medium}</strong> Medium
          </span>
          {low > 0 && (
            <span className="sev-tag sev-low">
              <strong>{low}</strong> Low / Info
            </span>
          )}
        </div>

        {report.human_review_required && (
          <div className="human-review-note">
            <AlertTriangle size={14} />
            <span>Human sign-off recommended before release</span>
          </div>
        )}
      </div>
    </div>
  );
}
