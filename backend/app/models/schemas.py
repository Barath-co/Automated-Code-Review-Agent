from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class TaskClassification(BaseModel):
    language: str = "python"
    loc: int = 0
    complexity: str = "medium"  # low, medium, high
    warrants_multi_agent: bool = True
    recommended_strategy: str = "multi_agent_consensus"

class ReviewFinding(BaseModel):
    id: str
    title: str
    category: str  # Security, Performance, Reliability, Style, Architecture
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    snippet: Optional[str] = None
    explanation: str
    suggested_fix: str
    confidence: float = 0.90
    reported_by: List[str] = Field(default_factory=list)

class CandidateOutput(BaseModel):
    agent_id: str
    persona: str
    model_name: str
    overall_assessment: str
    findings: List[ReviewFinding] = Field(default_factory=list)
    proposed_code: str
    latency_ms: int = 0
    token_usage: Dict[str, Any] = Field(default_factory=dict)

class ConflictItem(BaseModel):
    topic: str
    agent_claims: Dict[str, str] = Field(default_factory=dict)
    conflict_type: str  # contradiction, severity_discrepancy, omission
    resolution: str
    resolved_by_validation: bool = False

class ConsensusSummary(BaseModel):
    consensus_score: float = 0.0  # 0.0 - 100.0%
    strength: str = "MODERATE_AGREEMENT"  # STRONG_AGREEMENT, MODERATE_AGREEMENT, HIGH_DIVERGENCE
    agreed_points: List[str] = Field(default_factory=list)
    conflicts: List[ConflictItem] = Field(default_factory=list)
    consensus_notes: str = ""

class DeterministicValidation(BaseModel):
    syntax_valid: bool = True
    parser_engine: str = "python-ast / regex-heuristics"
    ast_metrics: Dict[str, Any] = Field(default_factory=dict)
    static_vulnerabilities_detected: List[Dict[str, Any]] = Field(default_factory=list)
    refactor_compiles: bool = True
    validation_passed: bool = True
    caveats: List[str] = Field(default_factory=list)

class OrchestrationState(BaseModel):
    task_id: str
    current_stage: str = "completed"  # planning, gathering_candidates, validating, completed
    allowed_actions: List[str] = Field(default_factory=lambda: [
        "TASK_INTAKE_AND_CLASSIFICATION",
        "DISPATCH_MODEL_ADAPTERS",
        "CROSS_EXAMINE_CONSENSUS",
        "EXECUTE_DETERMINISTIC_AST",
        "SYNTHESIZE_TRACEABLE_DELIVERY"
    ])
    call_budget_tokens: int = 16000
    tokens_consumed: int = 0
    deadline_seconds: int = 45
    elapsed_ms: int = 0
    completion_status: str = "COMPLETED_SUCCESS"
    workflow_selected: str = "MULTI_AGENT_CONSENSUS_AND_VALIDATION"
    max_steps_policy_enforced: bool = True
    current_step_count: int = 5
    max_steps_allowed: int = 10
    loop_guard_tripped: bool = False

class ResponseDeliveryMeta(BaseModel):
    what_was_checked: List[str] = Field(default_factory=lambda: [
        "Programmatic Python AST syntax verification",
        "SQL injection / string formatting vulnerability analysis",
        "Hardcoded credentials, API keys, and sensitive tokens check",
        "Cyclomatic complexity and nested iteration profiling",
        "Resource descriptor leaks (unmanaged file & connection lifecycles)",
        "Bare exception catch-all suppression detection"
    ])
    important_limitations: List[str] = Field(default_factory=lambda: [
        "Consensus indicates statistical agreement across specialist agents, not mathematical infallibility.",
        "Deterministic AST and static checks verify local syntax and known CWE patterns, not external network integration.",
        "High-risk enterprise code with financial or sensitive implications mandates final human engineer sign-off."
    ])
    privacy_and_secrets_redacted: bool = True
    human_approval_required: bool = False
    human_approval_status: str = "AWAITING_REVIEW"

class ExecutionMetrics(BaseModel):
    total_latency_ms: int = 0
    agents_dispatched: int = 0
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_inr: float = 0.0  # As detailed in Table 4.4
    estimated_cost_usd: float = 0.0
    execution_mode: str = "multi_agent"
    provider_used: str = "Google Gemini API"

class ReviewRequest(BaseModel):
    code: str
    language: Optional[str] = "python"
    mode: Optional[str] = "consensus"  # 'fast', 'consensus', 'deep_audit'
    custom_rules: Optional[str] = None
    api_key: Optional[str] = None
    model_override: Optional[str] = None

class FinalReviewReport(BaseModel):
    task_id: str
    created_at: str
    status: str = "completed"
    classification: TaskClassification
    orchestration_state: Optional[OrchestrationState] = None
    delivery_meta: Optional[ResponseDeliveryMeta] = None
    candidates: List[CandidateOutput] = Field(default_factory=list)
    consensus: ConsensusSummary
    validation: DeterministicValidation
    consolidated_findings: List[ReviewFinding] = Field(default_factory=list)
    refactored_code: str
    unified_diff: str = ""
    metrics: ExecutionMetrics
    human_review_required: bool = False
    executive_verdict: str = ""
    disclaimer: str = "Neural Consensus Intelligence Orchestrator (NCIO): Agreement between AI models indicates statistical alignment but does not guarantee mathematical infallibility. High-impact production systems require deterministic validation and peer human verification."
