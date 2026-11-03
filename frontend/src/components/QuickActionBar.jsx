import React from "react";
import { Sparkles, ShieldCheck, Zap, HelpCircle } from "lucide-react";

export default function QuickActionBar({ 
  onSelectSample, 
  onRunFastValidation, 
  onRunReview, 
  isLoading, 
  isValidating,
  codeEmpty
}) {
  return (
    <div className="quick-action-hero">
      <div className="hero-text-zone">
        <div className="hero-badge">
          <Sparkles size={14} className="text-cyan-400" />
          <span>Interactive AI Code Review Assistant</span>
        </div>
        <h2 className="hero-heading">Instant Multi-Agent Code Audit</h2>
        <p className="hero-desc">
          Choose a pre-built vulnerability sample or paste your own code below. In 1 click, 3 specialized AI agents audit security, performance, and reliability with deterministic AST validation.
        </p>
      </div>

      <div className="hero-quick-steps">
        <div className="step-card">
          <span className="step-num">Step 1</span>
          <span className="step-label">Select Sample or Paste Code</span>
        </div>
        <div className="step-arrow">→</div>
        <div className="step-card">
          <span className="step-num">Step 2</span>
          <span className="step-label">Run AST Pre-flight or Review</span>
        </div>
        <div className="step-arrow">→</div>
        <div className="step-card highlight-step">
          <span className="step-num">Step 3</span>
          <span className="step-label">Inspect Consensus & Copy Clean Fix</span>
        </div>
      </div>
    </div>
  );
}
