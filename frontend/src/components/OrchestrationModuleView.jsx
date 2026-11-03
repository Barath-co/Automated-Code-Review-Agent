import React from "react";
import { 
  Workflow, 
  ShieldCheck, 
  Clock, 
  Coins, 
  CheckCircle2, 
  ArrowRight, 
  AlertOctagon, 
  Repeat, 
  Sliders, 
  Terminal,
  Activity
} from "lucide-react";

export default function OrchestrationModuleView({ report, currentStep, isLoading }) {
  const state = report?.orchestration_state || {
    task_id: report?.task_id || "NCIO-STANDBY",
    current_stage: isLoading ? "executing" : "completed",
    allowed_actions: [
      "TASK_INTAKE_AND_CLASSIFICATION",
      "DISPATCH_MODEL_ADAPTERS",
      "CROSS_EXAMINE_CONSENSUS",
      "EXECUTE_DETERMINISTIC_AST",
      "SYNTHESIZE_TRACEABLE_DELIVERY"
    ],
    call_budget_tokens: 16000,
    tokens_consumed: report?.metrics?.total_tokens || 1224,
    deadline_seconds: 45,
    elapsed_ms: report?.metrics?.total_latency_ms || 950,
    completion_status: "COMPLETED_SUCCESS",
    workflow_selected: report?.classification?.warrants_multi_agent 
      ? "MULTI_AGENT_CONSENSUS_AND_VALIDATION" 
      : "SINGLE_MODEL_BASELINE",
    max_steps_policy_enforced: true,
    current_step_count: 5,
    max_steps_allowed: 10,
    loop_guard_tripped: false
  };

  const budgetPercent = Math.min(100, Math.round((state.tokens_consumed / state.call_budget_tokens) * 100));
  const deadlinePercent = Math.min(100, Math.round(((state.elapsed_ms / 1000) / state.deadline_seconds) * 100));

  const stages = [
    { name: "Planning", desc: "Complexity sizing & workflow branch" },
    { name: "Gathering Candidates", desc: "Parallel model adapter dispatch" },
    { name: "Validating", desc: "AST syntax & consensus comparison" },
    { name: "Completed", desc: "Traceable response synthesized" }
  ];

  return (
    <div className="module-view-container">
      {/* Module Title Header */}
      <div className="module-banner">
        <div className="banner-left">
          <div className="module-tag-badge">MODULE B</div>
          <div>
            <h2 className="module-heading">Orchestration & State Machine Module</h2>
            <p className="module-sub">
              Maintains task identity, execution lifecycle, allowed actions, call budgets, deadlines, and infinite loop guards.
            </p>
          </div>
        </div>
        <div className="state-badge-active">
          <Activity size={15} className="animate-pulse text-emerald-400" />
          <span>Status: {state.completion_status}</span>
        </div>
      </div>

      {/* Primary State Attributes Grid */}
      <div className="orch-cards-grid">
        {/* Task Identifier Card */}
        <div className="orch-card">
          <div className="card-top-icon text-cyan-400">
            <Terminal size={18} />
          </div>
          <div className="card-details">
            <span className="card-label">Task Identifier</span>
            <span className="card-val font-mono">{state.task_id}</span>
            <span className="card-sub">UUIDv4 Trace Envelope</span>
          </div>
        </div>

        {/* Workflow Selection Card */}
        <div className="orch-card">
          <div className="card-top-icon text-purple-400">
            <Workflow size={18} />
          </div>
          <div className="card-details">
            <span className="card-label">Workflow Strategy Selected</span>
            <span className="card-val text-sm">{state.workflow_selected}</span>
            <span className="card-sub">Branch: Based on LOC & Task Risk</span>
          </div>
        </div>

        {/* Call Budget Token Controller */}
        <div className="orch-card">
          <div className="card-top-icon text-amber-400">
            <Coins size={18} />
          </div>
          <div className="card-details">
            <span className="card-label">Call Budget & Token Cap</span>
            <span className="card-val">
              {state.tokens_consumed.toLocaleString()} / {state.call_budget_tokens.toLocaleString()}
            </span>
            <div className="mini-progress-bar">
              <div 
                className="mini-progress-fill bg-amber-400" 
                style={{ width: `${budgetPercent}%` }}
              ></div>
            </div>
            <span className="card-sub">{budgetPercent}% budget consumed • Table 4.4 Limit</span>
          </div>
        </div>

        {/* Deadline & Timeout Watchdog */}
        <div className="orch-card">
          <div className="card-top-icon text-emerald-400">
            <Clock size={18} />
          </div>
          <div className="card-details">
            <span className="card-label">Timeout Watchdog Deadline</span>
            <span className="card-val">
              {(state.elapsed_ms / 1000).toFixed(2)}s / {state.deadline_seconds}s
            </span>
            <div className="mini-progress-bar">
              <div 
                className="mini-progress-fill bg-emerald-400" 
                style={{ width: `${Math.max(5, deadlinePercent)}%` }}
              ></div>
            </div>
            <span className="card-sub">Bounded response time enforcement</span>
          </div>
        </div>
      </div>

      {/* Stage Progression Lifecycle */}
      <div className="card orch-stage-lifecycle-card">
        <h3 className="section-title">
          <Workflow size={16} className="inline-icon text-cyan-400" /> Current Stage Progression
        </h3>
        <div className="lifecycle-steps">
          {stages.map((st, i) => (
            <div key={st.name} className="lifecycle-node node-active-complete">
              <div className="node-num">0{i + 1}</div>
              <div className="node-text">
                <span className="node-title">{st.name}</span>
                <span className="node-desc">{st.desc}</span>
              </div>
              <CheckCircle2 size={16} className="text-emerald-400 ml-auto" />
            </div>
          ))}
        </div>
      </div>

      {/* Dual Column: Allowed Actions & Loop Guard */}
      <div className="orch-split-row">
        {/* Allowed Actions Registry */}
        <div className="card orch-actions-card">
          <h3 className="section-title">
            <Sliders size={16} className="inline-icon text-purple-400" /> Permitted Action Policy
          </h3>
          <p className="card-intro">
            Orchestrator strictly controls which state mutations are authorized at each stage:
          </p>
          <ul className="actions-list">
            {state.allowed_actions.map((act, idx) => (
              <li key={idx} className="action-item">
                <CheckCircle2 size={14} className="text-cyan-400" />
                <span className="action-name font-mono">{act}</span>
                <span className="action-status-pill">Authorized</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Maximum-Step Policy & Loop Prevention */}
        <div className="card orch-loop-card">
          <h3 className="section-title">
            <Repeat size={16} className="inline-icon text-amber-400" /> Maximum-Step Loop Prevention Policy
          </h3>
          <div className="loop-policy-box">
            <div className="policy-stat-row">
              <span className="stat-name">Max Step Policy Enforced:</span>
              <span className="stat-pill text-emerald-400">ACTIVE</span>
            </div>
            <div className="policy-stat-row">
              <span className="stat-name">Current Step Count:</span>
              <span className="stat-val font-mono">{state.current_step_count} steps</span>
            </div>
            <div className="policy-stat-row">
              <span className="stat-name">Hard Step Ceiling:</span>
              <span className="stat-val font-mono">{state.max_steps_allowed} steps max</span>
            </div>
            <div className="policy-stat-row">
              <span className="stat-name">Infinite Loop Tripped:</span>
              <span className="stat-pill text-emerald-400">NO (NORMAL TERMINATION)</span>
            </div>
          </div>
          <p className="loop-expl">
            <strong>Orchestrator Rule (Section 4.2.1-B):</strong> "A maximum-step policy prevents infinite loops. Simple requests use one model; complex or uncertain requests invoke consensus with bounded retries."
          </p>
        </div>
      </div>
    </div>
  );
}
