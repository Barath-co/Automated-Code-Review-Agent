import React from "react";
import { CheckCircle, Code2, ShieldAlert, Sparkles, ArrowRight } from "lucide-react";
import { BENCHMARK_PRESETS } from "../utils/presets";

export default function EmptyReviewState({ onSelectPreset }) {
  return (
    <div className="card empty-state-panel">
      <div className="empty-state-inner">
        <div className="empty-icon-circle">
          <Code2 size={28} className="text-brand" />
        </div>
        <h3 className="empty-state-heading">Ready to review your code</h3>
        <p className="empty-state-copy">
          Paste your code on the left and click <strong>Review code</strong>, or try one of these common vulnerability examples:
        </p>

        <div className="example-cards-grid">
          {BENCHMARK_PRESETS.map((preset) => (
            <div 
              key={preset.id} 
              onClick={() => onSelectPreset(preset)}
              className="example-preset-card"
            >
              <div className="preset-card-top">
                <span className={`preset-badge badge-${preset.badge.toLowerCase()}`}>
                  {preset.badge}
                </span>
                <span className="preset-lang">{preset.language}</span>
              </div>
              <h4 className="preset-name">{preset.title}</h4>
              <p className="preset-description">{preset.description}</p>
              <div className="preset-cta-row">
                <span>Load example</span>
                <ArrowRight size={13} />
              </div>
            </div>
          ))}
        </div>

        <div className="empty-guarantee-row">
          <div className="guarantee-item">
            <CheckCircle size={14} className="text-green" />
            <span>3 specialized reviewers (Security, Performance, Quality)</span>
          </div>
          <div className="guarantee-item">
            <CheckCircle size={14} className="text-green" />
            <span>Deterministic AST syntax checks</span>
          </div>
          <div className="guarantee-item">
            <CheckCircle size={14} className="text-green" />
            <span>Ready-to-copy code fixes</span>
          </div>
        </div>
      </div>
    </div>
  );
}
