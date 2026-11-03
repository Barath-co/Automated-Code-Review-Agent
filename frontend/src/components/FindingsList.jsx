import React, { useState } from "react";
import { 
  ShieldAlert, 
  Zap, 
  Wrench, 
  Layers, 
  Check, 
  Copy, 
  ChevronDown, 
  ChevronUp, 
  Code2
} from "lucide-react";

export default function FindingsList({ findings, onShowToast }) {
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [copiedId, setCopiedId] = useState(null);
  const [expandedId, setExpandedId] = useState(null);

  if (!findings || findings.length === 0) {
    return null;
  }

  const severities = ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"];

  const filtered = findings.filter(f => {
    return severityFilter === "ALL" || f.severity === severityFilter;
  });

  const handleCopyFix = (id, fix, e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(fix);
    setCopiedId(id);
    if (onShowToast) onShowToast("Fix copied to clipboard", "success");
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getCategoryIcon = (cat) => {
    switch (cat?.toLowerCase()) {
      case "security": return <ShieldAlert size={14} className="cat-icon-sec" />;
      case "performance": return <Zap size={14} className="cat-icon-perf" />;
      case "reliability": return <Wrench size={14} className="cat-icon-rel" />;
      default: return <Layers size={14} className="cat-icon-def" />;
    }
  };

  return (
    <div className="card clean-findings-card">
      <div className="clean-findings-header">
        <div className="findings-title-group">
          <h3 className="clean-findings-title">Identified issues ({filtered.length})</h3>
          <p className="clean-findings-sub">Review each issue and apply the recommended fix.</p>
        </div>

        <div className="clean-filter-tabs">
          {severities.map(s => (
            <button
              key={s}
              onClick={() => setSeverityFilter(s)}
              className={`filter-tab ${severityFilter === s ? "active" : ""}`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="clean-findings-list">
        {filtered.map((item, idx) => {
          const findingId = item.id || `f-${idx}`;
          const isExpanded = expandedId === null || expandedId === findingId;
          const sev = item.severity?.toLowerCase() || "medium";

          return (
            <div key={findingId} className={`clean-finding-row border-sev-${sev}`}>
              <div 
                className="finding-row-header"
                onClick={() => setExpandedId(expandedId === findingId ? null : findingId)}
              >
                <div className="row-header-left">
                  <span className={`clean-sev-badge badge-sev-${sev}`}>
                    {item.severity}
                  </span>
                  <span className="finding-row-title">{item.title}</span>
                  {item.line_start && (
                    <span className="clean-line-tag">
                      Line {item.line_start}
                    </span>
                  )}
                </div>

                <div className="row-header-right">
                  <span className="clean-category-tag">
                    {getCategoryIcon(item.category)}
                    <span>{item.category}</span>
                  </span>
                  <button className="clean-toggle-icon">
                    {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>
                </div>
              </div>

              {item.snippet && (
                <div className="clean-snippet-box">
                  <code>{item.snippet}</code>
                </div>
              )}

              {isExpanded && (
                <div className="finding-expanded-content">
                  <p className="clean-explanation">{item.explanation}</p>

                  {item.suggested_fix && (
                    <div className="clean-fix-container">
                      <div className="fix-bar">
                        <span className="fix-bar-label">Suggested fix:</span>
                        <button
                          onClick={(e) => handleCopyFix(findingId, item.suggested_fix, e)}
                          className="btn-copy-fix"
                        >
                          {copiedId === findingId ? (
                            <>
                              <Check size={12} className="text-green" />
                              <span className="text-green font-medium">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy size={12} />
                              <span>Copy fix</span>
                            </>
                          )}
                        </button>
                      </div>
                      <pre className="fix-code-pre">
                        <code>{item.suggested_fix}</code>
                      </pre>
                    </div>
                  )}

                  {item.reported_by && item.reported_by.length > 0 && (
                    <div className="clean-reporters-footer">
                      <span className="reporters-label">Flagged by:</span>
                      {item.reported_by.map((r, ri) => (
                        <span key={ri} className="reporter-pill">{r}</span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
