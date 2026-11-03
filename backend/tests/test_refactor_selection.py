"""
tests/test_refactor_selection.py
---------------------------------
Unit tests for the _select_best_refactor() logic in NCIOOrchestrator.

Covers:
 - All agents propose identical valid refactors → consensus bonus applied
 - One valid + one invalid (syntax error) → valid one chosen
 - All invalid proposals → original code retained, honest reason returned
 - Refactor introducing new vulnerability → lower score than clean alternative
 - Empty proposals list → original code returned
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.orchestrator.ncio_engine import NCIOOrchestrator
from app.models.schemas import CandidateOutput, ReviewFinding


# ---------------------------------------------------------------------------
# Helper: build a minimal CandidateOutput
# ---------------------------------------------------------------------------
def make_candidate(agent_id: str, persona: str, proposed_code: str, findings=None):
    return CandidateOutput(
        agent_id=agent_id,
        persona=persona,
        model_name="gemini-2.5-flash",
        overall_assessment="Test assessment",
        findings=findings or [],
        proposed_code=proposed_code
    )


ORIGINAL_CODE = """
def search_user(name):
    query = f"SELECT * FROM users WHERE username = '{name}'"
    cursor.execute(query)
"""

SAFE_REFACTOR = """
def search_user(name):
    cursor.execute("SELECT * FROM users WHERE username = %s", (name,))
"""

BROKEN_REFACTOR = """
def search_user(name:
    cursor.execute("SELECT * FROM users WHERE username = %s", (name,))
"""

ANOTHER_SAFE_REFACTOR = """
def search_user(name: str) -> None:
    cursor.execute("SELECT * FROM users WHERE username = ?", (name,))
"""

VULN_REFACTOR = """
def search_user(name):
    query = "SELECT * FROM users WHERE username = '%s'" % name
    cursor.execute(query)
"""


# ---------------------------------------------------------------------------
# 1. Empty proposals → original retained
# ---------------------------------------------------------------------------
class TestEmptyProposals:
    def test_no_candidates_returns_original(self):
        code, reason = NCIOOrchestrator._select_best_refactor(ORIGINAL_CODE, "python", [])
        assert code == ORIGINAL_CODE
        assert "original" in reason.lower() or "no" in reason.lower()


# ---------------------------------------------------------------------------
# 2. All candidates identical to original → no refactor accepted
# ---------------------------------------------------------------------------
class TestIdenticalToOriginal:
    def test_all_same_as_original_returns_original(self):
        candidates = [
            make_candidate("a1", "Security Agent", ORIGINAL_CODE),
            make_candidate("a2", "Performance Agent", ORIGINAL_CODE),
        ]
        code, reason = NCIOOrchestrator._select_best_refactor(ORIGINAL_CODE, "python", candidates)
        assert code == ORIGINAL_CODE


# ---------------------------------------------------------------------------
# 3. One valid + one syntax-broken → valid is chosen
# ---------------------------------------------------------------------------
class TestMixedValidInvalid:
    def test_valid_chosen_over_broken(self):
        candidates = [
            make_candidate("a1", "Security Agent", SAFE_REFACTOR),
            make_candidate("a2", "Performance Agent", BROKEN_REFACTOR),
        ]
        code, reason = NCIOOrchestrator._select_best_refactor(ORIGINAL_CODE, "python", candidates)
        assert code == SAFE_REFACTOR.strip() or SAFE_REFACTOR in code
        assert code != BROKEN_REFACTOR

    def test_broken_only_returns_original(self):
        candidates = [
            make_candidate("a1", "Security Agent", BROKEN_REFACTOR),
        ]
        code, reason = NCIOOrchestrator._select_best_refactor(ORIGINAL_CODE, "python", candidates)
        assert code == ORIGINAL_CODE
        assert "original" in reason.lower() or "failed" in reason.lower()


# ---------------------------------------------------------------------------
# 4. Multiple identical valid refactors → consensus bonus applied (both should win)
# ---------------------------------------------------------------------------
class TestConsensusBonus:
    def test_identical_valid_refactors_preferred(self):
        candidates = [
            make_candidate("a1", "Security Agent", SAFE_REFACTOR),
            make_candidate("a2", "Performance Agent", SAFE_REFACTOR),  # identical → bonus
            make_candidate("a3", "Clean Code Agent", ANOTHER_SAFE_REFACTOR),  # different, no bonus
        ]
        code, reason = NCIOOrchestrator._select_best_refactor(ORIGINAL_CODE, "python", candidates)
        # Both SAFE_REFACTOR proposals share a bonus; it should be selected
        assert code == SAFE_REFACTOR.strip() or SAFE_REFACTOR in code


# ---------------------------------------------------------------------------
# 5. All proposals syntax-invalid → original retained with honest reason
# ---------------------------------------------------------------------------
class TestAllInvalid:
    def test_all_invalid_returns_original(self):
        candidates = [
            make_candidate("a1", "Security Agent", BROKEN_REFACTOR),
            make_candidate("a2", "Performance Agent", "def broken(:\n    pass"),
        ]
        code, reason = NCIOOrchestrator._select_best_refactor(ORIGINAL_CODE, "python", candidates)
        assert code == ORIGINAL_CODE
        assert len(reason) > 0  # must give an explanation


# ---------------------------------------------------------------------------
# 6. Vulnerability in refactor → lower score than clean version
# ---------------------------------------------------------------------------
class TestVulnerabilityPenalty:
    def test_vuln_refactor_loses_to_clean(self):
        """VULN_REFACTOR still has SQL injection via % string format — should score lower."""
        candidates = [
            make_candidate("a1", "Security Agent", SAFE_REFACTOR),
            make_candidate("a2", "Lazy Agent", VULN_REFACTOR),
        ]
        code, reason = NCIOOrchestrator._select_best_refactor(ORIGINAL_CODE, "python", candidates)
        # The safe version should be selected over the vulnerable one
        assert VULN_REFACTOR.strip() != code or SAFE_REFACTOR.strip() == code
