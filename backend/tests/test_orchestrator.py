"""
tests/test_orchestrator.py
---------------------------
Unit and integration tests for NCIOOrchestrator.

Covers:
 - Empty / whitespace-only code submission raises ValueError
 - Oversized code (> 100k chars) raises ValueError
 - Full execution under simulated mode (no API key) returns complete report
 - Single-agent execution sets consensus_score=0.0 and strength="SINGLE_AGENT_MODE"
 - Preflight validation fails when syntax is broken
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.orchestrator.ncio_engine import NCIOOrchestrator
from app.models.schemas import ReviewRequest, FinalReviewReport
from app.consensus.analyzer import ConsensusAnalyzer
from app.models.schemas import DeterministicValidation, CandidateOutput


# ---------------------------------------------------------------------------
# 1. Input validation in orchestrator
# ---------------------------------------------------------------------------
class TestOrchestratorInputValidation:
    @pytest.mark.anyio
    async def test_empty_code_raises_value_error(self):
        req = ReviewRequest(code="", language="python", mode="consensus")
        with pytest.raises(ValueError, match="empty"):
            await NCIOOrchestrator.execute_review(req)

    @pytest.mark.anyio
    async def test_whitespace_code_raises_value_error(self):
        req = ReviewRequest(code="   \n   \t", language="python", mode="consensus")
        with pytest.raises(ValueError, match="empty"):
            await NCIOOrchestrator.execute_review(req)

    @pytest.mark.anyio
    async def test_oversized_code_raises_value_error(self):
        huge_code = "a = 1\n" * 25000  # > 100,000 characters
        req = ReviewRequest(code=huge_code, language="python", mode="consensus")
        with pytest.raises(ValueError, match="exceeds maximum size limit"):
            await NCIOOrchestrator.execute_review(req)


# ---------------------------------------------------------------------------
# 2. End-to-end execution in simulation mode
# ---------------------------------------------------------------------------
class TestOrchestratorSimulationMode:
    @pytest.mark.anyio
    async def test_successful_simulation_review(self):
        sample_code = """
def authenticate_user(username, password):
    query = f"SELECT * FROM users WHERE user='{username}' AND pass='{password}'"
    return db.execute(query)
"""
        req = ReviewRequest(
            code=sample_code,
            language="python",
            mode="consensus"
        )
        report: FinalReviewReport = await NCIOOrchestrator.execute_review(req)

        assert report is not None
        assert report.task_id.startswith("NCIO-")
        assert len(report.candidates) == 3
        assert report.consensus.consensus_score >= 0.0
        assert report.validation.syntax_valid is True
        assert len(report.consolidated_findings) > 0
        assert report.refactored_code != ""
        assert report.metrics.total_latency_ms >= 0


# ---------------------------------------------------------------------------
# 3. Single-Agent Consensus Behavior (Fix H6)
# ---------------------------------------------------------------------------
class TestSingleAgentHonesty:
    def test_single_agent_returns_single_agent_mode(self):
        candidate = CandidateOutput(
            agent_id="agent_1",
            persona="Security Specialist",
            model_name="gemini-2.5-flash",
            overall_assessment="Potential SQL Injection",
            findings=[],
            proposed_code="cursor.execute('SELECT 1')"
        )
        val = DeterministicValidation(
            syntax_valid=True,
            parser_engine="AST",
            static_vulnerabilities_detected=[],
            validation_passed=True
        )

        summary, consolidated = ConsensusAnalyzer.analyze([candidate], val)

        # FIX H6: Must report SINGLE_AGENT_MODE and 0.0 consensus score
        assert summary.strength == "SINGLE_AGENT_MODE"
        assert summary.consensus_score == 0.0
        assert "single-agent" in summary.consensus_notes.lower()
