import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.validators.code_validator import CodeValidator
from app.consensus.analyzer import ConsensusAnalyzer
from app.models.schemas import CandidateOutput, ReviewFinding, DeterministicValidation

def test_code_validator_sql_injection():
    vulnerable_code = """
def search_user(name):
    query = f"SELECT * FROM users WHERE username = '{name}'"
    cursor.execute(query)
"""
    result = CodeValidator.validate(vulnerable_code, "python")
    assert result.syntax_valid is True
    assert len(result.static_vulnerabilities_detected) > 0
    vuln_names = [v["name"] for v in result.static_vulnerabilities_detected]
    assert "SQL_INJECTION_RISK" in vuln_names

def test_code_validator_hardcoded_secret():
    secret_code = 'API_KEY = "sk-live-1234567890abcdef123456"'
    result = CodeValidator.validate(secret_code, "python")
    assert any(v["name"] == "HARDCODED_CREDENTIALS" for v in result.static_vulnerabilities_detected)

def test_code_validator_syntax_error():
    broken_code = "def invalid_syntax(:\n    return True"
    result = CodeValidator.validate(broken_code, "python")
    assert result.syntax_valid is False
    assert len(result.caveats) > 0

def test_consensus_analyzer_agreement():
    f1 = ReviewFinding(
        id="F1",
        title="SQL Injection Risk",
        category="Security",
        severity="CRITICAL",
        line_start=3,
        explanation="Untrusted dynamic query interpolation",
        suggested_fix="Use parameterized queries",
        confidence=0.95,
        reported_by=["Agent A"]
    )
    f2 = ReviewFinding(
        id="F2",
        title="SQL Injection Risk",
        category="Security",
        severity="CRITICAL",
        line_start=3,
        explanation="SQL query formed with string formatting",
        suggested_fix="Parameterized execution",
        confidence=0.96,
        reported_by=["Agent B"]
    )
    c1 = CandidateOutput(
        agent_id="agent_a",
        persona="Agent A",
        model_name="gemini-2.5-flash",
        overall_assessment="Critical vulnerability found",
        findings=[f1],
        proposed_code="cursor.execute('SELECT * FROM users WHERE username = %s', (name,))"
    )
    c2 = CandidateOutput(
        agent_id="agent_b",
        persona="Agent B",
        model_name="gemini-2.5-flash",
        overall_assessment="High risk query detected",
        findings=[f2],
        proposed_code="cursor.execute('SELECT * FROM users WHERE username = %s', (name,))"
    )
    val = DeterministicValidation(
        syntax_valid=True,
        parser_engine="AST",
        static_vulnerabilities_detected=[{"name": "SQL_INJECTION_RISK", "line": 3, "description": "SQL injection"}],
        validation_passed=True
    )

    summary, consolidated = ConsensusAnalyzer.analyze([c1, c2], val)
    assert summary.consensus_score == 100.0
    assert summary.strength == "STRONG_AGREEMENT"
    assert len(consolidated) == 1
    assert "Agent A" in consolidated[0].reported_by
    assert "Agent B" in consolidated[0].reported_by
