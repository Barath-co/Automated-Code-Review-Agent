import React, { useState } from "react";
import { 
  Send, 
  ShieldCheck, 
  AlertTriangle, 
  Lock, 
  FileCheck2, 
  Copy, 
  Check, 
  Download, 
  UserCheck, 
  CheckCircle2,
  FileText
} from "lucide-react";
import DiffViewer from "./DiffViewer";

export default function ResponseDeliveryView({ 
  report, 
  originalCode, 
  language,
  onExportMarkdown,
  onExportJson
}) {
  const [approved, setApproved] = useState(false);
  const [copied, setCopied] = useState(false);

  const delivery = report?.delivery_meta || {
    what_was_checked: [
      "Programmatic Python AST syntax verification",
      "Dynamic SQL string interpolation / SQL injection scan",
      "Hardcoded credentials, API keys, and sensitive tokens check",
      "Cyclomatic complexity and nested iteration profiling",
      "Resource descriptor leaks (unmanaged file & connection lifecycles)",
      "Bare exception catch-all suppression detection"
    ],
    important_limitations: [
      "Consensus indicates statistical agreement across specialist agents, not mathematical infallibility.",
      "Deterministic AST and static checks verify local syntax and known CWE patterns, not external network integration.",
      "High-risk enterprise code with financial or sensitive implications mandates final human engineer sign-off."
    ],
    privacy_and_secrets_redacted: true,
    human_approval_required: report?.human_review_required || false,
    human_approval_status: approved ? "APPROVED_BY_ENGINEER" : (report?.human_review_required ? "AWAITING_HUMAN_SIGN_OFF" : "AUTOMATICALLY_VERIFIED")
  };

  const handleApprove = () => {
    setApproved(true);
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(report?.refactored_code || "");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="module-view-container">
      {/* Banner */}
      <div className="module-banner">
        <div className="banner-left">
          <div className="module-tag-badge">MODULE E</div>
          <div>
            <h2 className="module-heading">Response Delivery & Governance Module</h2>
            <p className="module-sub">
              Formats selected answers, details what was checked, highlights limitations, redacts secrets, and enforces human sign-off on high-risk tasks.
            </p>
          </div>
        </div>
        <div className="state-badge-active">
          <FileCheck2 size={15} className="text-emerald-400" />
          <span>Status: {approved ? "HUMAN APPROVED" : delivery.human_approval_status}</span>
        </div>
      </div>

      {/* Human Approval Sign-off Gate for High-Risk Tasks */}
      <div className={`card human-gate-card ${approved ? "gate-approved" : "gate-pending"}`}>
        <div className="gate-header">
          <div className="gate-icon-wrap">
            {approved ? (
              <CheckCircle2 size={24} className="text-emerald-400" />
            ) : (
              <UserCheck size={24} className="text-amber-400" />
            )}
          </div>
          <div>
            <h3 className="gate-title">
              {approved ? "Human Engineering Sign-off: APPROVED" : "Human Approval Gate (Section 4.2.1-E)"}
            </h3>
            <p className="gate-desc">
              {approved 
                ? "Code refactor has been reviewed, certified, and cleared for staging deployment."
                : "For high-risk tasks or material security flaws, the system halts autonomous execution until a verified human auditor approves the proposed changes."}
            </p>
          </div>
          <div className="gate-action-btn-wrap">
            {!approved ? (
              <button onClick={handleApprove} className="btn-approve-gate">
                <UserCheck size={16} />
                <span>Sign-off & Approve Refactor</span>
              </button>
            ) : (
              <div className="approved-pill">
                <Check size={14} />
                <span>Signed Off by Lead Reviewer</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Code Refactor & Diff View */}
      <DiffViewer
        originalCode={originalCode}
        refactoredCode={report?.refactored_code}
        unifiedDiff={report?.unified_diff}
        language={language}
      />

      {/* Explanation Grid: What Was Checked & Limitations */}
      <div className="delivery-grid-split">
        {/* What Was Checked */}
        <div className="card checked-card">
          <h3 className="section-title text-emerald-400">
            <ShieldCheck size={16} className="inline-icon" /> What Was Checked (Verification Checklist)
          </h3>
          <ul className="checked-checklist">
            {delivery.what_was_checked.map((item, idx) => (
              <li key={idx} className="checklist-item">
                <span className="check-bullet">✓</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Limitations & Caveats */}
        <div className="card limitations-card">
          <h3 className="section-title text-amber-400">
            <AlertTriangle size={16} className="inline-icon" /> Limitations & Scientific Caveats
          </h3>
          <ul className="limitations-list">
            {delivery.important_limitations.map((item, idx) => (
              <li key={idx} className="limit-item">
                <span className="limit-bullet">⚠️</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Privacy & Zero-Trust Secrets Redaction Card */}
      <div className="card privacy-redaction-card">
        <div className="privacy-header">
          <Lock size={18} className="text-cyan-400" />
          <h3 className="section-title mb-0">Privacy & Zero-Trust Secret Redaction</h3>
          <span className="privacy-badge">REDACTION ACTIVE</span>
        </div>
        <p className="privacy-desc">
          Raw authentication secrets, API keys, and intermediate private prompts are stripped from public responses and redacted before telemetry logging.
        </p>
        <div className="export-toolbar-row">
          <button onClick={onExportMarkdown} className="btn-export">
            <FileText size={14} />
            <span>Download Viva Dossier (.md)</span>
          </button>
          <button onClick={onExportJson} className="btn-export-secondary">
            <Download size={14} />
            <span>Export Full JSON Envelope</span>
          </button>
        </div>
      </div>
    </div>
  );
}
