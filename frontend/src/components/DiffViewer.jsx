import React from "react";
import { Check, Copy, Download, GitCompare, Columns, AlignJustify } from "lucide-react";

export default function DiffViewer({ originalCode, refactoredCode, unifiedDiff, language, onShowToast }) {
  const [viewMode, setViewMode] = React.useState("split");
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(refactoredCode || "");
    setCopied(true);
    if (onShowToast) onShowToast("Refactored code copied to clipboard", "success");
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = language === "python" ? "py" : (language === "javascript" ? "js" : (language === "typescript" ? "ts" : "txt"));
    const blob = new Blob([refactoredCode || ""], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `reviewed_code.${ext}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    if (onShowToast) onShowToast(`Downloaded reviewed_code.${ext}`, "success");
  };

  return (
    <div className="card clean-diff-card">
      <div className="clean-diff-header">
        <div className="diff-header-title">
          <GitCompare size={16} className="text-brand" />
          <h3 className="diff-title-text">Suggested Code Changes</h3>
          <span className="clean-badge-green">Validated</span>
        </div>

        <div className="diff-header-actions">
          <div className="diff-view-toggle">
            <button
              onClick={() => setViewMode("split")}
              className={`toggle-tab ${viewMode === "split" ? "active" : ""}`}
            >
              <Columns size={13} />
              <span>Side-by-side</span>
            </button>
            <button
              onClick={() => setViewMode("unified")}
              className={`toggle-tab ${viewMode === "unified" ? "active" : ""}`}
            >
              <AlignJustify size={13} />
              <span>Unified diff</span>
            </button>
          </div>

          <button onClick={handleCopy} className="btn-clean-ghost">
            {copied ? <Check size={13} className="text-green" /> : <Copy size={13} />}
            <span>{copied ? "Copied" : "Copy fix"}</span>
          </button>
          <button onClick={handleDownload} className="btn-clean-ghost">
            <Download size={13} />
            <span>Download</span>
          </button>
        </div>
      </div>

      {viewMode === "split" ? (
        <div className="clean-split-grid">
          <div className="split-column original-column">
            <div className="column-bar original-bar">
              <span>Original code</span>
            </div>
            <pre className="code-pre original-pre">
              <code>{originalCode || "// No code provided"}</code>
            </pre>
          </div>

          <div className="split-column refactor-column">
            <div className="column-bar refactor-bar">
              <span>Cleaned & verified code</span>
            </div>
            <pre className="code-pre refactor-pre">
              <code>{refactoredCode || "// Refactor pending"}</code>
            </pre>
          </div>
        </div>
      ) : (
        <div className="clean-unified-box">
          <pre className="code-pre unified-pre">
            {unifiedDiff ? (
              unifiedDiff.split("\n").map((line, idx) => {
                const isAdd = line.startsWith("+") && !line.startsWith("+++");
                const isRem = line.startsWith("-") && !line.startsWith("---");
                const isHdr = line.startsWith("@@") || line.startsWith("---") || line.startsWith("+++");
                return (
                  <div
                    key={idx}
                    className={`clean-diff-line ${isAdd ? "diff-add" : ""} ${isRem ? "diff-rem" : ""} ${isHdr ? "diff-hdr" : ""}`}
                  >
                    <span className="diff-marker">{line[0] || " "}</span>
                    <span className="diff-text">{line.substring(1)}</span>
                  </div>
                );
              })
            ) : (
              <span className="text-muted">No changes between versions.</span>
            )}
          </pre>
        </div>
      )}
    </div>
  );
}
