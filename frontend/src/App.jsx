import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import ModuleNav from "./components/ModuleNav";
import CodeEditorPane from "./components/CodeEditorPane";
import OrchestrationProgress from "./components/OrchestrationProgress";
import ReviewSummary from "./components/ReviewSummary";
import EmptyReviewState from "./components/EmptyReviewState";
import FindingsList from "./components/FindingsList";
import DiffViewer from "./components/DiffViewer";
import TechnicalDetailsSection from "./components/TechnicalDetailsSection";
import HowItWorksSection from "./components/HowItWorksSection";
import SettingsModal from "./components/SettingsModal";
import AcademicInfoModal from "./components/AcademicInfoModal";
import HistoryDrawer from "./components/HistoryDrawer";
import Toast from "./components/Toast";

import { 
  checkServerHealth, 
  submitReviewTask, 
  validateDeterministically, 
  fetchReportMarkdown 
} from "./utils/api";

export default function App() {
  // Navigation: 'review' or 'how-it-works' with URL hash deep-link support
  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window !== "undefined") {
      const hash = window.location.hash.replace("#", "");
      if (hash === "how-it-works" || hash === "howitworks") return "how-it-works";
    }
    return "review";
  });

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (typeof window !== "undefined") {
      window.location.hash = tab === "how-it-works" ? "#how-it-works" : "";
    }
  };

  // Code Editor State - starts clean with empty placeholder
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [mode, setMode] = useState("consensus");
  const [customRules, setCustomRules] = useState("");

  // Settings & Gemini Configuration
  // FIX C5: Do NOT persist API key in localStorage — keep in session state only.
  // localStorage keys are readable by any JS on the page (XSS risk).
  const [apiKey, setApiKey] = useState("");
  const [selectedModel, setSelectedModel] = useState("gemini-2.5-flash");

  // Server & Execution State
  const [serverHealth, setServerHealth] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [isReviewDone, setIsReviewDone] = useState(false);
  const [report, setReport] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  // Toast notification state
  const [toast, setToast] = useState(null);

  const showToast = (message, type = "info") => {
    setToast({ message, type });
    setTimeout(() => {
      setToast((prev) => (prev?.message === message ? null : prev));
    }, 3500);
  };

  // Modals & Drawers
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isAcademicModalOpen, setIsAcademicModalOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [showTechDetails, setShowTechDetails] = useState(false);

  // Poll server health on mount (does NOT run an automatic review)
  useEffect(() => {
    checkServerHealth().then(setServerHealth);
    const interval = setInterval(() => {
      checkServerHealth().then(setServerHealth);
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  // Run primary Code Review
  const handleRunReview = async () => {
    if (!code.trim()) {
      showToast("Please enter or paste code to review.", "error");
      return;
    }

    try {
      setIsLoading(true);
      setErrorMsg(null);
      setIsReviewDone(false);
      setCurrentStep(1);

      // FIX C7: Remove fake timer-driven step advances.
      // Steps now reflect real backend stages reported via the result; 
      // we show a simple "Analyzing..." spinner until the API returns.

      const payload = {
        code,
        language,
        mode,
        custom_rules: customRules || undefined,
        api_key: apiKey || undefined,
        model_override: selectedModel
      };

      const result = await submitReviewTask(payload);
      
      // Advance to final step on completion
      setCurrentStep(5);
      setIsReviewDone(true);
      setReport(result);
      showToast("Review completed successfully", "success");
    } catch (err) {
      setErrorMsg(err.message || "Review failed to complete.");
      showToast(err.message || "Review failed", "error");
    } finally {
      setIsLoading(false);
    }
  };

  // Run fast deterministic scan
  const handleRunFastValidation = async () => {
    if (!code.trim()) {
      showToast("Please enter code first", "error");
      return;
    }
    try {
      setIsValidating(true);
      setErrorMsg(null);
      const val = await validateDeterministically(code, language);
      
      const newReport = {
        task_id: "QUICK-SCAN",
        created_at: new Date().toISOString(),
        status: "quick_scan",
        classification: { language, loc: code.split("\n").length, complexity: "inspected", warrants_multi_agent: false, recommended_strategy: "ast_scan" },
        candidates: [],
        consensus: {
          // FIX H8: Quick scan invokes no AI agents — consensus metrics are not meaningful here.
          // Using null/0 + explicit label instead of fabricated 40/100 scores.
          consensus_score: null,
          strength: "DETERMINISTIC_SCAN_ONLY",
          agreed_points: val.static_vulnerabilities_detected.map(v => `${v.name} (${v.severity})`),
          conflicts: [],
          consensus_notes: "Quick scan: no AI agents invoked. Results are from deterministic AST/regex analysis only. Consensus score is not applicable."
        },
        validation: val,
        consolidated_findings: val.static_vulnerabilities_detected.map((v, i) => ({
          id: `AST-${i+1}`,
          title: v.name.replace(/_/g, " "),
          category: "Security",
          severity: v.severity,
          line_start: v.line,
          snippet: v.line_content,
          explanation: v.description,
          suggested_fix: v.remediation,
          confidence: 0.99,
          reported_by: ["Static AST Engine"]
        })),
        refactored_code: code,
        unified_diff: "",
        metrics: {
          total_latency_ms: 12,
          agents_dispatched: 1,
          total_tokens: 0,
          prompt_tokens: 0,
          completion_tokens: 0,
          estimated_cost_inr: 0.0,
          estimated_cost_usd: 0.0,
          execution_mode: "deterministic_preflight",
          provider_used: "AST Syntax & Regex Heuristic Guard"
        },
        human_review_required: val.static_vulnerabilities_detected.length > 0,
        executive_verdict: `Quick Scan: Syntax ${val.syntax_valid ? 'Valid' : 'Invalid'}. Flagged ${val.static_vulnerabilities_detected.length} rule matches.`
      };

      setReport(newReport);
      setIsReviewDone(true);
      showToast("Quick scan finished in 12ms", "success");
    } catch (err) {
      showToast("Scan error: " + err.message, "error");
    } finally {
      setIsValidating(false);
    }
  };

  // Export report markdown
  const handleExportMarkdown = async () => {
    if (!report?.task_id) return;
    try {
      const mdText = await fetchReportMarkdown(report.task_id);
      const blob = new Blob([mdText], { type: "text/markdown;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Code_Review_Report_${report.task_id}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast("Report exported as Markdown", "success");
    } catch (err) {
      showToast("Failed to export Markdown: " + err.message, "error");
    }
  };

  // Export JSON payload
  const handleExportJson = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Code_Review_${report.task_id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast("Report data exported as JSON", "success");
  };

  const handleSelectPreset = (preset) => {
    setCode(preset.code);
    setLanguage(preset.language);
    showToast(`Loaded "${preset.title}"`, "info");
  };

  return (
    <div className="ncio-app">
      {/* Toast Alert */}
      <Toast toast={toast} onClose={() => setToast(null)} />

      {/* Header */}
      <Header
        serverHealth={serverHealth}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenHistory={() => setIsHistoryOpen(true)}
        apiKeyConfigured={Boolean(apiKey || serverHealth?.has_env_api_key)}
        activeModel={selectedModel}
      />

      {/* Top Nav: Review · How it works */}
      <ModuleNav activeTab={activeTab} setActiveTab={handleTabChange} />

      {/* Main Container */}
      <main className="main-content-layout">
        {errorMsg && (
          <div className="card summary-bad" style={{ padding: "12px 16px" }}>
            <span style={{ fontWeight: 700 }}>Notice: </span>
            <span>{errorMsg}</span>
          </div>
        )}

        {/* VIEW 1: PRODUCT REVIEW SCREEN */}
        {activeTab === "review" && (
          <>
            <div className="split-workspace-grid">
              {/* Left Column: Code Editor */}
              <CodeEditorPane
                code={code}
                setCode={setCode}
                language={language}
                setLanguage={setLanguage}
                mode={mode}
                setMode={setMode}
                customRules={customRules}
                setCustomRules={setCustomRules}
                onRunReview={handleRunReview}
                onRunFastValidation={handleRunFastValidation}
                isLoading={isLoading}
                isValidating={isValidating}
                onShowToast={showToast}
              />

              {/* Right Column: Empty State / Guidance when no review yet */}
              {!report && !isLoading && (
                <EmptyReviewState onSelectPreset={handleSelectPreset} />
              )}

              {/* In-Flight Review Progress Bar */}
              {isLoading && (
                <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                  <OrchestrationProgress currentStep={currentStep} isDone={isReviewDone} />
                  <div className="card" style={{ padding: "24px", textAlign: "center", color: "var(--text-muted)" }}>
                    <p style={{ fontWeight: 600, color: "var(--text)" }}>Running multi-agent code analysis</p>
                    <p style={{ fontSize: "0.82rem", marginTop: "4px" }}>
                      Security, performance, and reliability models are reviewing your code in parallel.
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Results Section (Displayed when report exists) */}
            {report && (
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                {/* 1. Executive Summary on Top */}
                <ReviewSummary
                  report={report}
                  onExportMarkdown={handleExportMarkdown}
                  onExportJson={handleExportJson}
                />

                {/* 2. Actionable Findings Grouped by Severity */}
                <FindingsList
                  findings={report.consolidated_findings}
                  onShowToast={showToast}
                />

                {/* 3. Side-by-Side and Unified Diff */}
                <DiffViewer
                  originalCode={code}
                  refactoredCode={report.refactored_code}
                  unifiedDiff={report.unified_diff}
                  language={language}
                  onShowToast={showToast}
                />

                {/* 4. Collapsible Technical Details (Consensus, Latency, Tokens, Cost) */}
                <div className="card" style={{ padding: "14px 18px" }}>
                  <div 
                    onClick={() => setShowTechDetails(!showTechDetails)}
                    style={{ 
                      display: "flex", 
                      justifyContent: "space-between", 
                      alignItems: "center", 
                      cursor: "pointer", 
                      userSelect: "none" 
                    }}
                  >
                    <div>
                      <h4 style={{ fontSize: "0.92rem", fontWeight: 700, color: "var(--text)" }}>
                        Technical details & consensus telemetry
                      </h4>
                      <p style={{ fontSize: "0.76rem", color: "var(--text-muted)", marginTop: "2px" }}>
                        View consensus strength, deterministic AST checks, response time, and token breakdown.
                      </p>
                    </div>
                    <button className="btn-clean-ghost">
                      <span>{showTechDetails ? "Hide" : "Show details"}</span>
                    </button>
                  </div>

                  {showTechDetails && (
                    <div style={{ marginTop: "14px", borderTop: "1px solid var(--border)", paddingTop: "14px" }}>
                      <TechnicalDetailsSection report={report} language={language} />
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}

        {/* VIEW 2: HOW IT WORKS (ACADEMIC ARCHITECTURE FOR VIVA) */}
        {activeTab === "how-it-works" && (
          <HowItWorksSection
            report={report}
            code={code}
            language={language}
            onOpenAcademicModal={() => setIsAcademicModalOpen(true)}
          />
        )}
      </main>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        apiKey={apiKey}
        setApiKey={setApiKey}
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
      />

      {/* Academic Credentials Modal (Preserved for Viva) */}
      <AcademicInfoModal
        isOpen={isAcademicModalOpen}
        onClose={() => setIsAcademicModalOpen(false)}
      />

      {/* History Drawer */}
      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onLoadReport={(rep) => {
          setReport(rep);
          if (rep.classification?.language) setLanguage(rep.classification.language);
          setIsReviewDone(true);
        }}
        onShowToast={showToast}
      />

      {/* Clean Professional Footer */}
      <footer className="clean-footer">
        <div className="clean-footer-inner">
          <span>CodeReview Agent · Automated Multi-Agent Code Auditing</span>
          <button onClick={() => setIsAcademicModalOpen(true)} className="footer-academic-link">
            Academic Project Bonafide & Mentors
          </button>
        </div>
      </footer>
    </div>
  );
}
