import React from "react";
import { CheckCircle2, Loader2 } from "lucide-react";

export default function OrchestrationProgress({ currentStep, isDone }) {
  const steps = [
    { id: 1, title: "Classifying task", desc: "Analyzing complexity" },
    { id: 2, title: "Scanning for security risks", desc: "Checking OWASP & secrets" },
    { id: 3, title: "Checking performance", desc: "Detecting bottlenecks" },
    { id: 4, title: "Validating syntax", desc: "AST compiler checks" },
    { id: 5, title: "Synthesizing fix", desc: "Generating diff" }
  ];

  return (
    <div className="card clean-progress-card">
      <div className="clean-progress-header">
        <span className="clean-progress-state">
          {isDone ? "Review complete" : `Stage ${currentStep} of 5: ${steps[currentStep - 1]?.title || "Processing"}...`}
        </span>
        <span className="clean-progress-percentage">
          {isDone ? "100%" : `${Math.round((currentStep / 5) * 100)}%`}
        </span>
      </div>

      <div className="clean-progress-bar-track">
        <div 
          className="clean-progress-bar-fill" 
          style={{ width: `${isDone ? 100 : (currentStep / 5) * 100}%` }}
        ></div>
      </div>

      <div className="clean-progress-steps">
        {steps.map((st) => {
          const isCompleted = isDone || currentStep > st.id;
          const isCurrent = !isDone && currentStep === st.id;

          return (
            <div 
              key={st.id} 
              className={`clean-step-item ${isCompleted ? "is-complete" : ""} ${isCurrent ? "is-current" : ""}`}
            >
              <div className="clean-step-dot">
                {isCompleted ? (
                  <CheckCircle2 size={13} className="text-green" />
                ) : isCurrent ? (
                  <Loader2 size={13} className="animate-spin text-brand" />
                ) : (
                  <span>{st.id}</span>
                )}
              </div>
              <span className="clean-step-name">{st.title}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
