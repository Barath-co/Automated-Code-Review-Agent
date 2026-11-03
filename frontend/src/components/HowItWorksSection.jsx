import React, { useState } from "react";
import { 
  ShieldCheck, 
  Award, 
  Workflow, 
  Network, 
  Scale, 
  Terminal, 
  Clock, 
  Coins, 
  CheckCircle2, 
  AlertTriangle, 
  FileCode2, 
  ArrowRight, 
  Cpu, 
  Download, 
  ExternalLink,
  ChevronRight,
  Info,
  BookOpen,
  Sparkles,
  Zap,
  HelpCircle
} from "lucide-react";

export default function HowItWorksSection({ report, code, language, onOpenAcademicModal }) {
  const [activeTab, setActiveTab] = useState("overview");
  const [selectedStage, setSelectedStage] = useState(1);
  const [showPrompts, setShowPrompts] = useState(false);

  // Pipeline stages metadata for the interactive diagram
  const stages = [
    {
      step: 1,
      title: "1. Intake & AST Guard",
      shortTitle: "AST Guard",
      badge: "Zero-Token",
      tagColor: "blue",
      latency: "12 ms",
      cost: "$0.00",
      description: "Fast deterministic syntax pre-validation via Python ast.parse / JS parser.",
      details: {
        module: "Module A & D (Pre-flight Validation Gate)",
        input: "Raw source code snippet and declared programming language.",
        action: "Parses abstract syntax tree deterministically before dispatching any AI models. If syntax fails or critical blacklisted calls appear, execution fast-fails with zero token expenditure.",
        output: "Validated AST tree, token count, syntax validity boolean, and static rule flags.",
        vivaQuestion: "Why run an AST check before calling the AI models?",
        vivaAnswer: "Calling LLMs on syntactically invalid code wastes expensive API tokens and induces hallucinations. Deterministic AST checking takes under 15ms and provides 100% ground-truth syntax certainty."
      }
    },
    {
      step: 2,
      title: "2. Multi-Agent Dispatch",
      shortTitle: "Agent Dispatch",
      badge: "Parallel AI",
      tagColor: "purple",
      latency: "320-380 ms",
      cost: "1,220 tokens",
      description: "Fanning out tasks to 3 specialized Gemini 2.5 personas in parallel.",
      details: {
        module: "Module C (Model Adapter & Provider Hub)",
        input: "Task envelope containing isolated code context and persona-specific system instructions.",
        action: "Dispatches 3 specialized review agents concurrently: Security Specialist (OWASP/CWE), Performance Architect (Big-O & I/O), and Clean Code Reviewer (SOLID & Reliability).",
        output: "3 independent candidate assessments with normalized findings and proposed code refactorings.",
        vivaQuestion: "Why use 3 specialist personas instead of a single prompt?",
        vivaAnswer: "Single prompts suffer from attention dilution and bias toward general stylistic comments. Specialized personas with dedicated temperature and role instructions achieve significantly higher recall on obscure vulnerabilities."
      }
    },
    {
      step: 3,
      title: "3. Consensus Mediation",
      shortTitle: "Consensus Engine",
      badge: "Cross-Examination",
      tagColor: "amber",
      latency: "45 ms",
      cost: "$0.00 (Local)",
      description: "Semantic cross-examination, agreement scoring, and contradiction detection.",
      details: {
        module: "Module D (Consensus & Discrepancy Matrix)",
        input: "Array of candidate reviews from the 3 independent personas.",
        action: "Applies mathematical clustering across finding locations and categories. Classifies claims into Unanimous (3/3), Majority (2/3), or Contested (1/3). Computes holistic consensus score.",
        output: "Unified agreement list, flagged contradictions, and human-in-the-loop escalation signal if critical contested findings exist.",
        vivaQuestion: "Is consensus considered ground truth in this architecture?",
        vivaAnswer: "No. As formulated in Chapter 2.4, consensus is a prioritization heuristic, not ground truth. When independent models agree, confidence increases, but edge-case security warnings are never suppressed simply because other models missed them."
      }
    },
    {
      step: 4,
      title: "4. AST Patch Gate",
      shortTitle: "AST Refactor Gate",
      badge: "Deterministic",
      tagColor: "emerald",
      latency: "15 ms",
      cost: "$0.00 (Local)",
      description: "Compiling and verifying proposed code fixes before rendering.",
      details: {
        module: "Module D (Deterministic Code Compiler Gate)",
        input: "Refactored code candidate proposed by consensus synthesizer.",
        action: "Re-runs the deterministic AST parser against the proposed code fix. If the AI patch introduced a syntax regression or import error, the patch is rejected and marked invalid.",
        output: "Verified refactored code and unified diff ready for user inspection.",
        vivaQuestion: "How do you guarantee the AI's suggested fix doesn't break syntax?",
        vivaAnswer: "By gating delivery behind an automated AST compile step. The engine parses the refactored string; if ast.parse fails, the system halts delivery and flags the regression."
      }
    },
    {
      step: 5,
      title: "5. Traceable Delivery",
      shortTitle: "Delivery & Sign-off",
      badge: "Executive Verdict",
      tagColor: "indigo",
      latency: "8 ms",
      cost: "$0.00",
      description: "Synthesizing executive verdict, unified diff, and peer review gates.",
      details: {
        module: "Module E (Traceable Response Delivery)",
        input: "Consolidated findings, consensus telemetry, AST verification token, and runtime metrics.",
        action: "Generates an actionable summary: Merge Verdict (Ready / Fix Required / Reject), categorized finding cards with code locations, side-by-side diff, and downloadable reports.",
        output: "User-facing dashboard payload, persistent audit record in SQLite, and downloadable reports.",
        vivaQuestion: "What is the purpose of the human review requirement?",
        vivaAnswer: "High-risk security vulnerabilities (Critical severity) or contested recommendations automatically set human_review_required: true, preventing automated CI/CD merges without human sign-off."
      }
    }
  ];

  const currentStageData = stages[selectedStage - 1];

  return (
    <div className="how-it-works-wrapper">
      {/* 1. HERO HEADER */}
      <div className="card how-hero-card">
        <div className="how-hero-content">
          <div className="how-hero-badge-row">
            <span className="how-pill-tag">
              <Sparkles size={12} />
              <span>Multi-Agent System Architecture</span>
            </span>
            <span className="how-pill-secondary">Modules A · B · C · D · E</span>
            <span className="how-pill-secondary">AST Zero-Token Guard</span>
          </div>

          <h1 className="how-hero-title">How the Code Review Agent Works</h1>
          <p className="how-hero-subtitle">
            An agentic architecture combining three specialized LLM personas, mathematical consensus clustering, 
            and deterministic AST compilation to deliver trustworthy code reviews without hallucinations.
          </p>

          <div className="how-hero-actions">
            <button onClick={onOpenAcademicModal} className="btn-hero-academic">
              <Award size={15} />
              <span>Academic Credentials & Mentors</span>
            </button>
            <a href="/api/academic/download/pdf" download="Sathyabama_BE_CodeReviewAgent_Report.pdf" className="btn-hero-download">
              <Download size={14} />
              <span>Download Report (PDF)</span>
            </a>
            <a href="/api/academic/download/docx" download="Sathyabama_BE_CodeReviewAgent_Report.docx" className="btn-hero-ghost">
              <Download size={14} />
              <span>Report (DOCX)</span>
            </a>
          </div>
        </div>
      </div>

      {/* 2. SUBTABS NAVIGATION */}
      <div className="how-nav-tabs">
        <button
          onClick={() => setActiveTab("overview")}
          className={`how-tab-btn ${activeTab === "overview" ? "active" : ""}`}
        >
          <Workflow size={15} />
          <span>Interactive Pipeline</span>
        </button>
        <button
          onClick={() => setActiveTab("personas")}
          className={`how-tab-btn ${activeTab === "personas" ? "active" : ""}`}
        >
          <Network size={15} />
          <span>3 Specialist Personas</span>
        </button>
        <button
          onClick={() => setActiveTab("consensus")}
          className={`how-tab-btn ${activeTab === "consensus" ? "active" : ""}`}
        >
          <Scale size={15} />
          <span>Consensus & AST Guard</span>
        </button>
        <button
          onClick={() => setActiveTab("orchestrator")}
          className={`how-tab-btn ${activeTab === "orchestrator" ? "active" : ""}`}
        >
          <Cpu size={15} />
          <span>State Machine & Safeguards</span>
        </button>
        <button
          onClick={() => setActiveTab("academic")}
          className={`how-tab-btn ${activeTab === "academic" ? "active" : ""}`}
        >
          <BookOpen size={15} />
          <span>Viva Voce & University</span>
        </button>
      </div>

      {/* 3. TAB CONTENT VIEWS */}
      <div className="how-tab-content">
        {/* ======================================================== */}
        {/* VIEW 1: INTERACTIVE ARCHITECTURE PIPELINE */}
        {/* ======================================================== */}
        {activeTab === "overview" && (
          <div className="how-pipeline-view">
            {/* Visual Stepper Diagram */}
            <div className="card pipeline-stepper-card">
              <div className="stepper-header">
                <div>
                  <h3 className="stepper-title">5-Stage Agentic Pipeline (Figure 4.1 & 4.2)</h3>
                  <p className="stepper-subtitle">
                    Click any stage to inspect its inputs, actions, latency metrics, and viva examination defense.
                  </p>
                </div>
                <span className="stepper-pill">Interactive Flow Inspector</span>
              </div>

              <div className="pipeline-flow-track">
                {stages.map((st) => {
                  const isSelected = selectedStage === st.step;
                  return (
                    <div 
                      key={st.step} 
                      onClick={() => setSelectedStage(st.step)}
                      className={`pipeline-stage-node ${isSelected ? "selected" : ""}`}
                    >
                      <div className="stage-node-top">
                        <span className={`stage-number-badge tag-${st.tagColor}`}>
                          {st.step}
                        </span>
                        <span className="stage-latency-pill">{st.latency}</span>
                      </div>
                      <span className="stage-node-name">{st.shortTitle}</span>
                      <span className="stage-node-badge">{st.badge}</span>
                      {isSelected && <div className="stage-active-indicator" />}
                    </div>
                  );
                })}
              </div>

              {/* Stage Deep Dive Inspector */}
              <div className="stage-inspector-panel">
                <div className="inspector-top-bar">
                  <div className="inspector-title-zone">
                    <span className={`inspector-tag tag-${currentStageData.tagColor}`}>
                      STAGE {currentStageData.step} OF 5
                    </span>
                    <h4 className="inspector-heading">{currentStageData.title}</h4>
                  </div>
                  <div className="inspector-metrics-pill">
                    <span>Latency: <strong>{currentStageData.latency}</strong></span>
                    <span className="pill-dot">·</span>
                    <span>Cost: <strong>{currentStageData.cost}</strong></span>
                  </div>
                </div>

                <p className="inspector-summary">{currentStageData.description}</p>

                <div className="inspector-grid">
                  <div className="inspector-col">
                    <span className="inspector-label">System Module Responsibility</span>
                    <p className="inspector-val">{currentStageData.details.module}</p>

                    <span className="inspector-label" style={{ marginTop: "12px" }}>Input Schema</span>
                    <p className="inspector-val font-mono-sub">{currentStageData.details.input}</p>
                  </div>

                  <div className="inspector-col">
                    <span className="inspector-label">Core Action & Algorithmic Transformation</span>
                    <p className="inspector-val">{currentStageData.details.action}</p>

                    <span className="inspector-label" style={{ marginTop: "12px" }}>Output Result</span>
                    <p className="inspector-val font-mono-sub">{currentStageData.details.output}</p>
                  </div>
                </div>

                {/* Viva Defense Box */}
                <div className="inspector-viva-box">
                  <div className="viva-box-header">
                    <HelpCircle size={15} className="viva-icon" />
                    <span>Viva Voce Defense & Justification</span>
                  </div>
                  <p className="viva-question"><strong>Q: {currentStageData.details.vivaQuestion}</strong></p>
                  <p className="viva-answer">A: {currentStageData.details.vivaAnswer}</p>
                </div>
              </div>
            </div>

            {/* 3 Core Architectural Advantages Grid */}
            <div className="advantages-grid">
              <div className="card advantage-card">
                <div className="adv-icon adv-blue">
                  <ShieldCheck size={20} />
                </div>
                <h4 className="adv-title">Zero-Token Fast Fail</h4>
                <p className="adv-desc">
                  Invalid syntax or blacklisted commands are intercepted in 12ms before touching any LLM. 
                  Saves 100% of compute and tokens on broken submissions.
                </p>
              </div>

              <div className="card advantage-card">
                <div className="adv-icon adv-purple">
                  <Network size={20} />
                </div>
                <h4 className="adv-title">Parallel Multi-Persona Fan-out</h4>
                <p className="adv-desc">
                  Each reviewer acts as an independent specialist (Security, Performance, Clean Code) with strict 
                  domain prompts, eliminating prompt dilution.
                </p>
              </div>

              <div className="card advantage-card">
                <div className="adv-icon adv-amber">
                  <Scale size={20} />
                </div>
                <h4 className="adv-title">Mathematical Consensus Heuristic</h4>
                <p className="adv-desc">
                  Findings are cross-examined to calculate confidence. Contradictions trigger automated peer 
                  escalation without suppressing lone security warnings.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* VIEW 2: 3 SPECIALIST PERSONAS (MODULE C) */}
        {/* ======================================================== */}
        {activeTab === "personas" && (
          <div className="how-personas-view">
            <div className="card persona-intro-card">
              <div className="persona-intro-header">
                <div>
                  <h3 className="section-block-title">Module C: Multi-Persona Model Adapters</h3>
                  <p className="section-block-sub">
                    Instead of a generic review prompt, three fine-tuned personas analyze the snippet from distinct perspectives.
                  </p>
                </div>
                <button 
                  onClick={() => setShowPrompts(!showPrompts)} 
                  className="btn-toggle-prompts"
                >
                  <Terminal size={14} />
                  <span>{showPrompts ? "Hide system prompts" : "Inspect system prompts"}</span>
                </button>
              </div>
            </div>

            <div className="personas-cards-grid">
              {/* Persona 1: Security Specialist */}
              <div className="card persona-detail-card card-sec">
                <div className="persona-card-header">
                  <div className="persona-badge-icon badge-sec">
                    <ShieldCheck size={22} />
                  </div>
                  <div>
                    <span className="persona-id-tag">ADAPTER-SEC</span>
                    <h4 className="persona-title">Security & Vulnerability Specialist</h4>
                  </div>
                </div>

                <div className="persona-specs-row">
                  <span className="spec-pill">Model: <strong>Gemini 2.5 Flash</strong></span>
                  <span className="spec-pill">Temp: <strong>0.1 (Strict)</strong></span>
                  <span className="spec-pill">Schema: <strong>CWE / OWASP</strong></span>
                </div>

                <div className="persona-body">
                  <p className="persona-desc">
                    Examines source code specifically for exploit surfaces, injection vulnerabilities, privilege escalation, 
                    and cryptographic weaknesses.
                  </p>

                  <div className="persona-focus-tags">
                    <span className="focus-tag">OWASP Top 10</span>
                    <span className="focus-tag">CWE-89 (SQLi)</span>
                    <span className="focus-tag">CWE-79 (XSS)</span>
                    <span className="focus-tag">Secret Exposure</span>
                    <span className="focus-tag">Input Sanitization</span>
                  </div>

                  {showPrompts && (
                    <div className="system-prompt-box">
                      <span className="prompt-label">System Directive Excerpt:</span>
                      <code>
                        {`"You are a Principal Application Security Auditor. Analyze the provided code strictly for vulnerabilities, injection vectors, memory corruption, and credential leakage. Output findings mapped to standard CWE identifiers."`}
                      </code>
                    </div>
                  )}

                  <div className="persona-viva-takeaway">
                    <strong>Viva Defense:</strong> Temperature is restricted to 0.1 to prevent creative speculation and ensure strict adherence to standardized vulnerability definitions.
                  </div>
                </div>
              </div>

              {/* Persona 2: Performance Architect */}
              <div className="card persona-detail-card card-perf">
                <div className="persona-card-header">
                  <div className="persona-badge-icon badge-perf">
                    <Zap size={22} />
                  </div>
                  <div>
                    <span className="persona-id-tag">ADAPTER-PERF</span>
                    <h4 className="persona-title">Performance & Concurrency Architect</h4>
                  </div>
                </div>

                <div className="persona-specs-row">
                  <span className="spec-pill">Model: <strong>Gemini 2.5 Flash</strong></span>
                  <span className="spec-pill">Temp: <strong>0.2 (Balanced)</strong></span>
                  <span className="spec-pill">Schema: <strong>Big-O & Concurrency</strong></span>
                </div>

                <div className="persona-body">
                  <p className="persona-desc">
                    Analyzes runtime algorithmic complexity, memory allocation overhead, event-loop blocking operations, 
                    and resource leaks.
                  </p>

                  <div className="persona-focus-tags">
                    <span className="focus-tag">Asymptotic O(n²)</span>
                    <span className="focus-tag">Memory Leaks</span>
                    <span className="focus-tag">Database N+1</span>
                    <span className="focus-tag">Async / Blocking I/O</span>
                    <span className="focus-tag">Connection Pools</span>
                  </div>

                  {showPrompts && (
                    <div className="system-prompt-box">
                      <span className="prompt-label">System Directive Excerpt:</span>
                      <code>
                        {`"You are a High-Throughput Performance Architect. Identify algorithmic bottlenecks, redundant iterations, unclosed file descriptors, and non-blocking stream violations. Suggest amortized optimal algorithms."`}
                      </code>
                    </div>
                  )}

                  <div className="persona-viva-takeaway">
                    <strong>Viva Defense:</strong> Discovers quadratic string concatenations, unbounded buffer reads, and missing connection teardowns that pass traditional linters.
                  </div>
                </div>
              </div>

              {/* Persona 3: Clean Code Reviewer */}
              <div className="card persona-detail-card card-clean">
                <div className="persona-card-header">
                  <div className="persona-badge-icon badge-clean">
                    <CheckCircle2 size={22} />
                  </div>
                  <div>
                    <span className="persona-id-tag">ADAPTER-CLEAN</span>
                    <h4 className="persona-title">Reliability & Clean Code Reviewer</h4>
                  </div>
                </div>

                <div className="persona-specs-row">
                  <span className="spec-pill">Model: <strong>Gemini 2.5 Flash</strong></span>
                  <span className="spec-pill">Temp: <strong>0.2 (Balanced)</strong></span>
                  <span className="spec-pill">Schema: <strong>SOLID & PEP-8</strong></span>
                </div>

                <div className="persona-body">
                  <p className="persona-desc">
                    Evaluates maintainability, defensive exception boundaries, type safety, modular design, and standard idiom compliance.
                  </p>

                  <div className="persona-focus-tags">
                    <span className="focus-tag">SOLID Principles</span>
                    <span className="focus-tag">Exception Boundaries</span>
                    <span className="focus-tag">Type Annotations</span>
                    <span className="focus-tag">DRY & Modularity</span>
                    <span className="focus-tag">PEP-8 / Standard</span>
                  </div>

                  {showPrompts && (
                    <div className="system-prompt-box">
                      <span className="prompt-label">System Directive Excerpt:</span>
                      <code>
                        {`"You are a Lead Software Craftsperson. Review code readability, modular cohesion, boundary exceptions, and type safety. Propose clean idiomatic refactorings maintaining functional equivalence."`}
                      </code>
                    </div>
                  )}

                  <div className="persona-viva-takeaway">
                    <strong>Viva Defense:</strong> Ensures the refactored solution is readable, testable, and conforms to production engineering best practices.
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* VIEW 3: CONSENSUS & AST GUARD (MODULE D) */}
        {/* ======================================================== */}
        {activeTab === "consensus" && (
          <div className="how-consensus-view">
            {/* Academic Theoretical Foundation Callout */}
            <div className="card consensus-quote-card">
              <div className="quote-icon">
                <Scale size={24} />
              </div>
              <div className="quote-body">
                <h4 className="quote-title">Theoretical Grounding (Section 2.4 of Project Report)</h4>
                <blockquote className="quote-text">
                  “Consensus is a prioritization heuristic, not ground truth. When independent specialist models agree on an issue, 
                  the probability of false-positive hallucination decreases exponentially. However, high-severity security findings 
                  are never discarded simply because performance or clean code agents did not observe them.”
                </blockquote>
              </div>
            </div>

            {/* Discrepancy Mediation Rules Table */}
            <div className="card consensus-table-card">
              <div className="table-header-row">
                <h3 className="section-block-title">Discrepancy Mediation Logic & Conflict Matrix</h3>
                <span className="table-badge">Table 4.3 Implementation</span>
              </div>

              <div className="custom-table-container">
                <table className="how-table">
                  <thead>
                    <tr>
                      <th>Agreement Tier</th>
                      <th>Agent Participation</th>
                      <th>Confidence Level</th>
                      <th>Orchestrator Resolution Action</th>
                      <th>Human Gate Required</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>
                        <span className="tier-badge tier-unanimous">Unanimous</span>
                      </td>
                      <td>3 of 3 Personas</td>
                      <td><strong>98% Confidence</strong></td>
                      <td>Auto-included in P1 Consolidated Findings; Refactored fix applied automatically.</td>
                      <td><span className="gate-no">Optional</span></td>
                    </tr>
                    <tr>
                      <td>
                        <span className="tier-badge tier-majority">Majority</span>
                      </td>
                      <td>2 of 3 Personas</td>
                      <td><strong>85% Confidence</strong></td>
                      <td>Synthesizer merges findings with supporting rationale from dissenting model.</td>
                      <td><span className="gate-no">Optional</span></td>
                    </tr>
                    <tr>
                      <td>
                        <span className="tier-badge tier-contested">Contested</span>
                      </td>
                      <td>1 of 3 (Contradicted by another)</td>
                      <td><strong>55% Confidence</strong></td>
                      <td>Contradiction flagged in consensus matrix; both arguments retained for inspection.</td>
                      <td><span className="gate-yes">Yes (Escalated)</span></td>
                    </tr>
                    <tr>
                      <td>
                        <span className="tier-badge tier-lone-sec">Lone Security Voice</span>
                      </td>
                      <td>1 of 3 (Security Specialist Only)</td>
                      <td><strong>90% Priority</strong></td>
                      <td>Overriding heuristic: Critical security findings are elevated even without clean code consensus.</td>
                      <td><span className="gate-yes">Yes (Advised)</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Deterministic AST vs LLM Benchmark */}
            <div className="card benchmark-card">
              <h3 className="section-block-title">Deterministic AST Engine vs LLM Roundtrip Benchmark</h3>
              <p className="section-block-sub">
                Demonstrates why hybrid AI + compiler systems drastically outperform pure LLM wrappers.
              </p>

              <div className="benchmark-bars-zone">
                <div className="benchmark-bar-group">
                  <div className="bar-labels">
                    <span className="bar-title">Deterministic AST Engine (ast.parse)</span>
                    <span className="bar-metric">12 ms · $0.00 Cost</span>
                  </div>
                  <div className="bar-track">
                    <div className="bar-fill bar-fill-fast" style={{ width: "3%" }} />
                  </div>
                  <span className="bar-note">Instant syntax verification and vulnerability pattern matching.</span>
                </div>

                <div className="benchmark-bar-group">
                  <div className="bar-labels">
                    <span className="bar-title">Full Multi-Agent LLM Roundtrip (3x Gemini 2.5 Flash)</span>
                    <span className="bar-metric">950 ms · 1,220 tokens</span>
                  </div>
                  <div className="bar-track">
                    <div className="bar-fill bar-fill-llm" style={{ width: "100%" }} />
                  </div>
                  <span className="bar-note">Deep semantic reasoning, root cause explanation, and unified diff synthesis.</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* VIEW 4: ORCHESTRATOR STATE MACHINE (MODULE B) */}
        {/* ======================================================== */}
        {activeTab === "orchestrator" && (
          <div className="how-orchestrator-view">
            <div className="card orch-intro-card">
              <h3 className="section-block-title">Module B: Orchestration & Bounded State Machine</h3>
              <p className="section-block-sub">
                Guarantees predictable execution, enforces resource budgets, prevents infinite loops, and maintains state traceability.
              </p>

              <div className="orch-guardrails-grid">
                <div className="guardrail-card">
                  <div className="guardrail-top">
                    <Coins size={18} className="text-amber-500" />
                    <span className="guardrail-title">Token Budget Controller</span>
                  </div>
                  <span className="guardrail-limit">16,000 Tokens Max</span>
                  <p className="guardrail-desc">
                    Limits maximum cumulative token consumption across all adapters per review task to prevent runaway API billing.
                  </p>
                  <div className="budget-bar-track">
                    <div className="budget-bar-fill" style={{ width: "8%" }} />
                  </div>
                  <span className="budget-label">Typical consumption: ~1,220 tokens (8%)</span>
                </div>

                <div className="guardrail-card">
                  <div className="guardrail-top">
                    <Clock size={18} className="text-blue-500" />
                    <span className="guardrail-title">Deadline Watchdog</span>
                  </div>
                  <span className="guardrail-limit">45 Seconds Hard Timeout</span>
                  <p className="guardrail-desc">
                    Active asyncio watchdog aborts hung network requests, gracefully falling back to deterministic local AST results.
                  </p>
                  <div className="budget-bar-track">
                    <div className="budget-bar-fill bar-fill-green" style={{ width: "3%" }} />
                  </div>
                  <span className="budget-label">Typical execution: 0.95s (2.1% of deadline)</span>
                </div>

                <div className="guardrail-card">
                  <div className="guardrail-top">
                    <Workflow size={18} className="text-purple-500" />
                    <span className="guardrail-title">Infinite Loop Guard</span>
                  </div>
                  <span className="guardrail-limit">10 Max State Steps</span>
                  <p className="guardrail-desc">
                    Enforces finite state transitions. If consensus refactoring requires more than 3 iterative repairs, task exits safely.
                  </p>
                  <div className="budget-bar-track">
                    <div className="budget-bar-fill bar-fill-purple" style={{ width: "50%" }} />
                  </div>
                  <span className="budget-label">State transitions executed: 5 steps</span>
                </div>
              </div>
            </div>

            {/* State Transition Flow Card */}
            <div className="card state-flow-card">
              <h4 className="state-flow-title">Deterministic State Transition Path</h4>
              <div className="state-nodes-row">
                <div className="state-box state-done">
                  <span className="state-tag">STEP 1</span>
                  <span className="state-name">TASK_INTAKE</span>
                </div>
                <ArrowRight size={16} className="state-arrow" />

                <div className="state-box state-done">
                  <span className="state-tag">STEP 2</span>
                  <span className="state-name">DISPATCH_ADAPTERS</span>
                </div>
                <ArrowRight size={16} className="state-arrow" />

                <div className="state-box state-done">
                  <span className="state-tag">STEP 3</span>
                  <span className="state-name">CROSS_EXAMINE</span>
                </div>
                <ArrowRight size={16} className="state-arrow" />

                <div className="state-box state-done">
                  <span className="state-tag">STEP 4</span>
                  <span className="state-name">EXECUTE_AST_GATE</span>
                </div>
                <ArrowRight size={16} className="state-arrow" />

                <div className="state-box state-active">
                  <span className="state-tag">STEP 5</span>
                  <span className="state-name">TRACEABLE_DELIVERY</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* VIEW 5: VIVA VOCE & ACADEMIC CREDENTIALS */}
        {/* ======================================================== */}
        {activeTab === "academic" && (
          <div className="how-academic-view">
            <div className="card academic-details-card">
              <div className="academic-badge-row">
                <span className="academic-inst-badge">SATHYABAMA INSTITUTE OF SCIENCE AND TECHNOLOGY</span>
                <span className="academic-grade-badge">NAAC A++ Accredited</span>
              </div>

              <h2 className="academic-project-title">
                Professional Training I: Neural Consensus Intelligence Orchestrator (NCIO)
              </h2>
              <p className="academic-project-sub">
                Department of Computer Science and Engineering · School of Computing · Final Year Project
              </p>

              <div className="academic-meta-grid">
                <div className="meta-block">
                  <span className="meta-title">Internal Guide</span>
                  <p className="meta-val">Dr. Nancy Noella, M.E., Ph.D.</p>
                  <span className="meta-dept">Assistant Professor, Dept of CSE</span>
                </div>

                <div className="meta-block">
                  <span className="meta-title">Industry Training Partner</span>
                  <p className="meta-val">Credo Systemz, Chennai</p>
                  <span className="meta-dept">Full Stack Development & AI Engineering</span>
                </div>

                <div className="meta-block">
                  <span className="meta-title">Project Code & ID</span>
                  <p className="meta-val font-mono">CSE-PT1-2026-NCIO</p>
                  <span className="meta-dept">Phase-1 Implementation Ready</span>
                </div>
              </div>

              {/* Download Buttons Bar */}
              <div className="academic-downloads-bar">
                <div className="dl-info">
                  <h4 className="dl-title">Official 30-Page B.E. Project Report</h4>
                  <p className="dl-sub">Includes Bonafide Certificate, Literature Survey, Figures 4.1–4.4, and Table 4.4 Telemetry.</p>
                </div>
                <div className="dl-buttons-group">
                  <a href="/api/academic/download/pdf" download="Sathyabama_BE_CodeReviewAgent_Report.pdf" className="btn-academic-download-pdf">
                    <Download size={15} />
                    <span>Download PDF</span>
                  </a>
                  <a href="/api/academic/download/docx" download="Sathyabama_BE_CodeReviewAgent_Report.docx" className="btn-academic-download-docx">
                    <Download size={15} />
                    <span>Download DOCX</span>
                  </a>
                </div>
              </div>
            </div>

            {/* Viva Voce Quick Prep Cards */}
            <div className="card viva-prep-card">
              <h3 className="section-block-title">Top Viva Voce Questions & Evaluator Defense</h3>
              <p className="section-block-sub">Crisp, mathematically grounded answers for external examiners.</p>

              <div className="viva-qa-list">
                <div className="viva-qa-item">
                  <h4 className="viva-q">1. How does NCIO eliminate AI hallucination during code refactoring?</h4>
                  <p className="viva-a">
                    Through a <strong>deterministic compiler gate (Module D)</strong>. No code suggestion is rendered to the user until it successfully compiles via Python's local <code>ast.parse</code> or language AST. If the model invents non-existent syntax, the compiler gate trips and invalidates the candidate.
                  </p>
                </div>

                <div className="viva-qa-item">
                  <h4 className="viva-q">2. Why is consensus treated as a heuristic rather than ground truth?</h4>
                  <p className="viva-a">
                    Because multiple LLMs can share collective biases or miss domain-specific zero-day vulnerabilities. NCIO gives unilateral escalation power to the Security Specialist persona for critical vulnerabilities even when the style and clean code models disagree.
                  </p>
                </div>

                <div className="viva-qa-item">
                  <h4 className="viva-q">3. What prevents infinite recursive loops when agents suggest conflicting fixes?</h4>
                  <p className="viva-a">
                    Module B enforces a <strong>bounded finite state machine</strong> with a maximum step limit of 10 and a hard 45-second deadline watchdog. Iterative refactoring is limited to 2 repair cycles before falling back to a human-in-the-loop review flag.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}