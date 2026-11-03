import React, { useState } from "react";
import { 
  Play, 
  RotateCcw, 
  Sliders, 
  ChevronDown, 
  ChevronUp, 
  Upload, 
  Copy, 
  Check, 
  FileCode,
  Zap
} from "lucide-react";
import { BENCHMARK_PRESETS } from "../utils/presets";

export default function CodeEditorPane({
  code,
  setCode,
  language,
  setLanguage,
  mode,
  setMode,
  customRules,
  setCustomRules,
  onRunReview,
  onRunFastValidation,
  isLoading,
  isValidating,
  onShowToast
}) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [copied, setCopied] = useState(false);

  const loc = code ? code.split("\n").length : 0;
  const chars = code ? code.length : 0;

  const handleCopy = () => {
    if (!code) return;
    navigator.clipboard.writeText(code);
    setCopied(true);
    if (onShowToast) onShowToast("Code copied to clipboard", "success");
    setTimeout(() => setCopied(false), 2000);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result;
      if (typeof content === "string") {
        setCode(content);
        const ext = file.name.split('.').pop()?.toLowerCase();
        if (ext === 'py') setLanguage('python');
        else if (ext === 'js') setLanguage('javascript');
        else if (ext === 'ts') setLanguage('typescript');
        else if (ext === 'go') setLanguage('go');
        else if (ext === 'cpp' || ext === 'c') setLanguage('cpp');
        else if (ext === 'sql') setLanguage('sql');
        if (onShowToast) onShowToast(`Loaded ${file.name}`, "info");
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="card editor-clean-card">
      {/* Top clean controls bar */}
      <div className="editor-clean-bar">
        <div className="clean-bar-left">
          <div className="select-pill">
            <span className="pill-label">Language:</span>
            <select 
              value={language} 
              onChange={(e) => setLanguage(e.target.value)} 
              className="clean-select"
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="typescript">TypeScript</option>
              <option value="go">Go</option>
              <option value="cpp">C++</option>
              <option value="sql">SQL</option>
            </select>
          </div>

          <div className="select-pill">
            <span className="pill-label">Mode:</span>
            <select 
              value={mode} 
              onChange={(e) => setMode(e.target.value)} 
              className="clean-select"
            >
              <option value="consensus">Full team review (3 reviewers)</option>
              <option value="deep_audit">Deep security audit</option>
              <option value="fast">Single reviewer</option>
            </select>
          </div>
        </div>

        <div className="clean-bar-right">
          <label className="btn-clean-ghost" title="Upload local file">
            <Upload size={13} />
            <span>Upload</span>
            <input type="file" onChange={handleFileUpload} style={{ display: "none" }} accept=".py,.js,.ts,.go,.cpp,.c,.sql,.txt" />
          </label>

          <button onClick={handleCopy} className="btn-clean-ghost" title="Copy code">
            {copied ? <Check size={13} className="text-green" /> : <Copy size={13} />}
            <span>{copied ? "Copied" : "Copy"}</span>
          </button>

          <button 
            type="button" 
            onClick={() => setShowAdvanced(!showAdvanced)} 
            className={`btn-clean-ghost ${showAdvanced ? "btn-active" : ""}`}
            title="Custom guidelines"
          >
            <Sliders size={13} />
            <span>Rules</span>
          </button>

          {code && (
            <button 
              onClick={() => { setCode(""); if (onShowToast) onShowToast("Editor cleared", "info"); }} 
              className="btn-clean-ghost" 
              title="Clear editor"
            >
              <RotateCcw size={13} />
              <span>Clear</span>
            </button>
          )}
        </div>
      </div>

      {/* Advanced Rules Drawer */}
      {showAdvanced && (
        <div className="advanced-rules-strip">
          <label className="rules-label">
            Custom rules or constraints:
          </label>
          <input 
            type="text" 
            value={customRules} 
            onChange={(e) => setCustomRules(e.target.value)} 
            placeholder="e.g., Enforce OWASP Top 10, no raw SQL, require type annotations..."
            className="rules-clean-input"
          />
        </div>
      )}

      {/* Editor Surface */}
      <div className="editor-clean-surface">
        <div className="editor-clean-gutter">
          {Array.from({ length: Math.max(loc, 10) }).map((_, i) => (
            <div key={i} className="clean-line-num">{i + 1}</div>
          ))}
        </div>
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder={`// Paste your ${language} code here to review...`}
          className="clean-textarea"
          spellCheck="false"
          rows={14}
        />
      </div>

      {/* Action Footer */}
      <div className="editor-clean-footer">
        <div className="editor-meta-stats">
          <span>{loc} lines</span>
          <span className="meta-dot">·</span>
          <span>{chars} characters</span>
        </div>

        <div className="editor-action-buttons">
          <button
            onClick={onRunFastValidation}
            disabled={!code.trim() || isValidating || isLoading}
            className="btn-secondary-clean"
            title="Fast local syntax and security check"
          >
            <Zap size={14} />
            <span>{isValidating ? "Scanning..." : "Quick scan"}</span>
          </button>

          <button
            onClick={onRunReview}
            disabled={!code.trim() || isLoading}
            className="btn-primary-clean"
            title="Start automated multi-agent code review"
          >
            {isLoading ? (
              <>
                <div className="clean-spinner"></div>
                <span>Reviewing code...</span>
              </>
            ) : (
              <>
                <Play size={14} fill="currentColor" />
                <span>Review code</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
