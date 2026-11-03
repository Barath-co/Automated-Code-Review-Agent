import asyncio
import difflib
import time
import uuid
from collections import Counter
from datetime import datetime
from typing import List, Optional, Tuple

from ..config import config
from ..models.schemas import (
    ReviewRequest,
    FinalReviewReport,
    TaskClassification,
    CandidateOutput,
    ExecutionMetrics,
    ReviewFinding,
    OrchestrationState,
    ResponseDeliveryMeta
)
from ..adapters.gemini_adapter import GeminiAdapter
from ..adapters.simulated_adapter import SimulatedConsensusAdapter
from ..validators.code_validator import CodeValidator
from ..consensus.analyzer import ConsensusAnalyzer

# Per-agent timeout in seconds. If a single agent exceeds this, it is skipped gracefully.
AGENT_TIMEOUT_SECONDS = 30
# Overall orchestration timeout (should be >= AGENT_TIMEOUT_SECONDS)
ORCHESTRATION_TIMEOUT_SECONDS = config.TIMEOUT_SECONDS


class NCIOOrchestrator:
    """
    Neural Consensus Intelligence Orchestrator (NCIO)
    Implements Figures 4.1, 4.2, and 4.3 from the academic report.
    Coordinates multi-agent persona dispatches, deterministic validations,
    consensus reconciliation, and traceable response synthesis.

    Key fixes applied in this version:
    - FIX C3: Refactor selection now validates all candidate refactors and scores them
      by security safety, syntax validity, and consensus agreement before selecting.
    - FIX H7: Per-agent asyncio.wait_for() timeout prevents a hung agent from
      stalling the entire pipeline.
    - FIX H3: Orchestration step count is tracked via actual increments, not hardcoded.
    - FIX H4: privacy_and_secrets_redacted is set to False (honest) since no active
      redaction is performed in this version.
    """

    PERSONAS = [
        {
            "name": "Gemini Code Security Specialist",
            "instruction": (
                "You are a senior Application Security Engineer specializing in OWASP Top 10, "
                "CWE vulnerabilities, memory safety, injection prevention, and zero-trust defensive coding."
            )
        },
        {
            "name": "Gemini Performance Architect",
            "instruction": (
                "You are a Principal Systems & Performance Architect specializing in algorithmic "
                "complexity, concurrency, I/O efficiency, memory footprint, and low-latency code."
            )
        },
        {
            "name": "Gemini Reliability & Clean Code Reviewer",
            "instruction": (
                "You are a Lead Software Architect focusing on code readability, robust exception "
                "handling, resource management, SOLID principles, and type safety."
            )
        }
    ]

    @classmethod
    async def execute_review(cls, request: ReviewRequest) -> FinalReviewReport:
        task_id = f"NCIO-{uuid.uuid4().hex[:8].upper()}"
        start_overall = time.time()
        step_count = 0

        # ──────────────────────────────────────────────────────────────────────
        # STEP 1: Task Intake & Classification (FR-01, FR-02)
        # ──────────────────────────────────────────────────────────────────────
        step_count += 1
        code = request.code.strip()
        if not code:
            raise ValueError("Task input code cannot be empty.")
        if len(code) > 100_000:
            raise ValueError("Code submission exceeds maximum size limit (100,000 characters).")

        language = (request.language or "python").lower()
        loc = len(code.split("\n"))
        complexity = "high" if loc > 80 else ("medium" if loc > 25 else "low")

        warrants_multi = request.mode in ["consensus", "deep_audit"] or complexity in ["medium", "high"]

        classification = TaskClassification(
            language=language,
            loc=loc,
            complexity=complexity,
            warrants_multi_agent=warrants_multi,
            recommended_strategy="multi_agent_consensus" if warrants_multi else "fast_single_model"
        )

        # ──────────────────────────────────────────────────────────────────────
        # STEP 2: Preflight Deterministic Validation (before calling any AI)
        # ──────────────────────────────────────────────────────────────────────
        step_count += 1
        preflight_validation = CodeValidator.validate(code=code, language=language)

        # ──────────────────────────────────────────────────────────────────────
        # STEP 3: Setup Adapters & Dispatch Agents (FR-03, FR-09)
        # ──────────────────────────────────────────────────────────────────────
        step_count += 1
        active_api_key = request.api_key or config.GEMINI_API_KEY
        use_real_gemini = bool(active_api_key)

        gemini_adapter = (
            GeminiAdapter(default_model=request.model_override or config.DEFAULT_MODEL)
            if use_real_gemini else None
        )

        selected_personas = cls.PERSONAS if warrants_multi else [cls.PERSONAS[0]]
        candidates: List[CandidateOutput] = []
        agent_failures: List[str] = []

        async def fetch_candidate(p_meta: dict) -> Optional[CandidateOutput]:
            """
            Dispatches a single agent with an individual timeout guard (FIX H7).
            Returns None on failure so one bad agent doesn't crash the pipeline.
            """
            persona_name = p_meta["name"]
            instruction = p_meta["instruction"]
            if request.custom_rules:
                instruction += f"\nCustom Rule Enforcements: {request.custom_rules}"

            try:
                if use_real_gemini and gemini_adapter:
                    coro = gemini_adapter.evaluate_code(
                        code=code,
                        language=language,
                        persona=persona_name,
                        system_instruction=instruction,
                        api_key=active_api_key,
                        model_name=request.model_override
                    )
                else:
                    sim = SimulatedConsensusAdapter(agent_persona=persona_name)
                    coro = sim.evaluate_code(code, language, persona_name, instruction)

                # FIX H7: Per-agent timeout — prevents one hung agent from stalling all
                result = await asyncio.wait_for(coro, timeout=AGENT_TIMEOUT_SECONDS)
                return result

            except asyncio.TimeoutError:
                agent_failures.append(
                    f"{persona_name}: timed out after {AGENT_TIMEOUT_SECONDS}s"
                )
                # Graceful degradation: fall back to simulation if real Gemini timed out
                if use_real_gemini:
                    try:
                        sim = SimulatedConsensusAdapter(agent_persona=persona_name)
                        res = await asyncio.wait_for(
                            sim.evaluate_code(code, language, persona_name, instruction),
                            timeout=10
                        )
                        res.overall_assessment += " [Note: Gemini API timed out — simulated fallback used]"
                        return res
                    except Exception:
                        pass
                return None

            except Exception as ex:
                agent_failures.append(f"{persona_name}: {str(ex)[:120]}")
                # Graceful degradation to simulated agent
                if use_real_gemini:
                    try:
                        sim = SimulatedConsensusAdapter(agent_persona=persona_name)
                        res = await asyncio.wait_for(
                            sim.evaluate_code(code, language, persona_name, instruction),
                            timeout=10
                        )
                        res.overall_assessment += f" [Note: Provider API fallback triggered: {str(ex)[:80]}]"
                        return res
                    except Exception:
                        pass
                return None

        # Execute all agents concurrently with asyncio.gather (now truly concurrent — FIX C1/C2)
        raw_results = await asyncio.gather(*[fetch_candidate(p) for p in selected_personas])
        candidates = [r for r in raw_results if r is not None]

        if not candidates:
            raise RuntimeError(
                "All AI agents failed to produce results. "
                f"Failures: {'; '.join(agent_failures) or 'unknown'}. "
                "Check your API key and network connection."
            )

        # ──────────────────────────────────────────────────────────────────────
        # STEP 4: Consensus & Conflict Analysis (FR-05, Figure 4.3)
        # ──────────────────────────────────────────────────────────────────────
        step_count += 1
        consensus_summary, consolidated_findings = ConsensusAnalyzer.analyze(
            candidates=candidates,
            deterministic_validation=preflight_validation
        )

        # ──────────────────────────────────────────────────────────────────────
        # STEP 5: Refactor Selection with Validation (FIX C3)
        #
        # Old behaviour: blindly pick the first non-identical proposed refactor.
        # New behaviour:
        #   1. Collect all candidate refactors.
        #   2. Validate each one (syntax + security) with the postflight AST check.
        #   3. Score each by: (a) compiles clean, (b) no new security vulns introduced,
        #      (c) how many agents proposed it (consensus proxy).
        #   4. Select the highest-scoring valid refactor.
        #   5. If no candidate passes, keep the original code and flag it.
        # ──────────────────────────────────────────────────────────────────────
        step_count += 1
        best_refactored_code, refactor_selection_notes = cls._select_best_refactor(
            original_code=code,
            language=language,
            candidates=candidates
        )

        # Postflight validation: validate the selected refactored code
        postflight_validation = CodeValidator.validate(
            code=code,
            language=language,
            refactored_code=best_refactored_code if best_refactored_code != code else None
        )

        # ──────────────────────────────────────────────────────────────────────
        # STEP 6: Generate Unified Diff
        # ──────────────────────────────────────────────────────────────────────
        diff_lines = list(difflib.unified_diff(
            code.splitlines(keepends=True),
            best_refactored_code.splitlines(keepends=True),
            fromfile="Original Code",
            tofile="NCIO Validated Refactor",
            lineterm=""
        ))
        unified_diff_str = "".join(diff_lines) if diff_lines else "No alterations proposed."

        # ──────────────────────────────────────────────────────────────────────
        # STEP 7: Compute Execution & Financial Metrics (Table 4.4)
        # ──────────────────────────────────────────────────────────────────────
        total_latency_ms = int((time.time() - start_overall) * 1000)
        # Only count real token integers (ignore simulation _note field)
        total_tokens = sum(
            v for c in candidates
            for k, v in c.token_usage.items()
            if k == "total_tokens" and isinstance(v, int)
        )
        prompt_tokens = sum(
            v for c in candidates
            for k, v in c.token_usage.items()
            if k == "prompt_tokens" and isinstance(v, int)
        )
        completion_tokens = sum(
            v for c in candidates
            for k, v in c.token_usage.items()
            if k == "completion_tokens" and isinstance(v, int)
        )

        cost_inr = round((total_tokens / 1000.0) * config.ESTIMATED_INR_PER_1K_TOKENS, 4)
        cost_usd = round(cost_inr / 86.5, 5)

        metrics = ExecutionMetrics(
            total_latency_ms=total_latency_ms,
            agents_dispatched=len(candidates),
            total_tokens=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            estimated_cost_inr=cost_inr,
            estimated_cost_usd=cost_usd,
            execution_mode="multi_agent_consensus" if warrants_multi else "single_model_baseline",
            provider_used=(
                "Google Gemini 2.5 Flash (Direct API)" if use_real_gemini
                else "NCIO Simulation Engine (Demo Mode)"
            )
        )

        # ──────────────────────────────────────────────────────────────────────
        # STEP 8: Executive Verdict & Orchestration State
        # ──────────────────────────────────────────────────────────────────────
        critical_count = sum(1 for f in consolidated_findings if f.severity in ["CRITICAL", "HIGH"])
        needs_human = (
            critical_count > 0
            or not postflight_validation.syntax_valid
            or consensus_summary.strength == "HIGH_DIVERGENCE_FLAGGED"
            or not postflight_validation.refactor_compiles
        )

        verdict_parts = [
            f"Review completed across {len(candidates)} specialist agent(s) "
            f"with {consensus_summary.consensus_score}% consensus.",
            f"Found {len(consolidated_findings)} actionable issue(s) ({critical_count} critical/high).",
            f"Original syntax: {'valid' if preflight_validation.syntax_valid else 'INVALID'}.",
            f"Proposed refactor: {'syntax-valid' if postflight_validation.refactor_compiles else 'SYNTAX ERROR — original retained'}.",
        ]
        if agent_failures:
            verdict_parts.append(f"Agent failures: {len(agent_failures)} ({', '.join(agent_failures[:2])}).")
        if refactor_selection_notes:
            verdict_parts.append(f"Refactor selection: {refactor_selection_notes}")

        verdict = " ".join(verdict_parts)

        orchestration_state = OrchestrationState(
            task_id=task_id,
            current_stage="completed",
            call_budget_tokens=config.MAX_TOKENS_PER_TASK,
            tokens_consumed=total_tokens,
            deadline_seconds=config.TIMEOUT_SECONDS,
            elapsed_ms=total_latency_ms,
            completion_status="COMPLETED_SUCCESS" if not agent_failures else "COMPLETED_WITH_PARTIAL_FAILURES",
            workflow_selected=(
                "MULTI_AGENT_CONSENSUS_AND_VALIDATION" if warrants_multi
                else "SINGLE_MODEL_BASELINE"
            ),
            max_steps_policy_enforced=True,
            current_step_count=step_count,   # FIX H3: actual step count, not hardcoded 5
            max_steps_allowed=10,
            loop_guard_tripped=False
        )

        # FIX H4: privacy_and_secrets_redacted must be honest.
        # We perform a secrets scan (via code_validator) but do NOT rewrite/redact source code.
        # Source code is stored as-is in the DB. Set to False to reflect reality.
        delivery_meta = ResponseDeliveryMeta(
            human_approval_required=needs_human,
            human_approval_status="AWAITING_HUMAN_SIGN_OFF" if needs_human else "AUTOMATICALLY_VERIFIED",
            privacy_and_secrets_redacted=False  # Honest: scan performed but no active redaction applied
        )

        return FinalReviewReport(
            task_id=task_id,
            created_at=datetime.utcnow().isoformat() + "Z",
            status="completed",
            classification=classification,
            orchestration_state=orchestration_state,
            delivery_meta=delivery_meta,
            candidates=candidates,
            consensus=consensus_summary,
            validation=postflight_validation,
            consolidated_findings=consolidated_findings,
            refactored_code=best_refactored_code,
            unified_diff=unified_diff_str,
            metrics=metrics,
            human_review_required=needs_human,
            executive_verdict=verdict
        )

    @classmethod
    def _select_best_refactor(
        cls,
        original_code: str,
        language: str,
        candidates: List[CandidateOutput]
    ) -> Tuple[str, str]:
        """
        FIX C3: Select the best valid refactor from all agent proposals.

        Scoring rubric (higher = better):
          +3  — proposed code compiles clean (syntax-valid via AST)
          +2  — proposed code introduces zero NEW security vulnerabilities
                (compared to original's vuln count)
          +1  — more than one agent proposed the same (or near-identical) refactor
          -99 — proposed code fails syntax check (disqualified)

        Returns:
          (best_code, selection_notes) — original code if no valid proposal found.
        """
        # Baseline: security vuln count in original
        original_val = CodeValidator.validate(original_code, language)
        original_vuln_count = len(original_val.static_vulnerabilities_detected)

        scored: List[Tuple[int, str, str]] = []  # (score, proposed_code, agent_name)

        for candidate in candidates:
            proposed = candidate.proposed_code
            if not proposed or proposed.strip() == original_code.strip():
                continue

            val = CodeValidator.validate(proposed, language, refactored_code=None)

            # Disqualify if syntax-invalid
            if not val.syntax_valid:
                continue

            score = 3  # base: compiles
            new_vuln_count = len(val.static_vulnerabilities_detected)
            if new_vuln_count <= original_vuln_count:
                score += 2  # doesn't introduce new security issues
            else:
                score -= 1  # penalty for introducing new vulnerabilities

            scored.append((score, proposed, candidate.persona))

        if not scored:
            return original_code, (
                "No valid refactor found — all proposals failed syntax or security checks. "
                "Original code retained."
            )

        # Bonus for consensus: if multiple agents proposed identical code, boost its score
        code_counts = Counter(code for _, code, _ in scored)
        boosted = [
            (score + (1 if code_counts[code] > 1 else 0), code, persona)
            for score, code, persona in scored
        ]

        best_score, best_code, best_persona = max(boosted, key=lambda x: x[0])
        return best_code, f"Selected refactor from '{best_persona}' (score={best_score})."
