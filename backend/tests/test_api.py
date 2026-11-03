"""
tests/test_api.py
-----------------
Integration tests for the FastAPI application using TestClient.

Covers:
 - GET /api/health → 200
 - POST /api/review with empty code → 400
 - POST /api/review with oversized code → 413
 - POST /api/validate-only with SQL injection code → returns vulns
 - GET /api/history → 200, returns list
 - DELETE /api/report/{nonexistent} → 404
 - GET /api/samples → 200
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Health check
# ---------------------------------------------------------------------------
class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_has_status_online(self):
        response = client.get("/api/health")
        data = response.json()
        assert data.get("status") == "online"

    def test_health_has_expected_fields(self):
        response = client.get("/api/health")
        data = response.json()
        assert "system" in data
        assert "has_env_api_key" in data
        assert "default_gemini_model" in data


# ---------------------------------------------------------------------------
# 2. Samples endpoint
# ---------------------------------------------------------------------------
class TestSamplesEndpoint:
    def test_samples_returns_200(self):
        response = client.get("/api/samples")
        assert response.status_code == 200

    def test_samples_is_list(self):
        response = client.get("/api/samples")
        data = response.json()
        assert isinstance(data, list)


# ---------------------------------------------------------------------------
# 3. Validate-only endpoint
# ---------------------------------------------------------------------------
class TestValidateOnlyEndpoint:
    def test_validate_sql_injection(self):
        code = "def foo(name):\n    q = f\"SELECT * FROM users WHERE name='{name}'\"\n    db.execute(q)"
        response = client.post("/api/validate-only", json={"code": code, "language": "python"})
        assert response.status_code == 200
        data = response.json()
        assert "syntax_valid" in data
        assert "static_vulnerabilities_detected" in data
        vuln_names = [v["name"] for v in data["static_vulnerabilities_detected"]]
        assert "SQL_INJECTION_RISK" in vuln_names

    def test_validate_empty_code_400(self):
        response = client.post("/api/validate-only", json={"code": "", "language": "python"})
        assert response.status_code == 400

    def test_validate_valid_python(self):
        response = client.post("/api/validate-only", json={
            "code": "def add(a, b):\n    return a + b",
            "language": "python"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["syntax_valid"] is True


# ---------------------------------------------------------------------------
# 4. Review endpoint — validation errors
# ---------------------------------------------------------------------------
class TestReviewEndpointValidation:
    def test_empty_code_returns_400(self):
        response = client.post("/api/review", json={
            "code": "",
            "language": "python",
            "mode": "consensus"
        })
        assert response.status_code == 400

    def test_whitespace_only_code_returns_400(self):
        response = client.post("/api/review", json={
            "code": "   \n\t  ",
            "language": "python",
            "mode": "consensus"
        })
        assert response.status_code == 400

    def test_oversized_code_returns_413(self):
        """FIX M1: Body size middleware must reject payloads > 200KB."""
        huge_code = "x = 1\n" * 50_000  # well over 200KB
        response = client.post(
            "/api/review",
            content=f'{{"code": "{huge_code}", "language": "python", "mode": "consensus"}}'.encode(),
            headers={"Content-Type": "application/json", "Content-Length": str(len(huge_code) + 100)}
        )
        # Either 413 from middleware or 400 from orchestrator size check
        assert response.status_code in (400, 413)


# ---------------------------------------------------------------------------
# 5. History endpoint
# ---------------------------------------------------------------------------
class TestHistoryEndpoint:
    def test_history_returns_200(self):
        response = client.get("/api/history")
        assert response.status_code == 200

    def test_history_is_list(self):
        response = client.get("/api/history")
        data = response.json()
        assert isinstance(data, list)

    def test_history_limit_param(self):
        response = client.get("/api/history?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3


# ---------------------------------------------------------------------------
# 6. Report retrieval and deletion
# ---------------------------------------------------------------------------
class TestReportEndpoints:
    def test_get_nonexistent_report_404(self):
        response = client.get("/api/report/nonexistent-task-xyz-9999")
        assert response.status_code == 404

    def test_delete_nonexistent_report_404(self):
        response = client.delete("/api/report/nonexistent-task-xyz-9999")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# 7. Export endpoint
# ---------------------------------------------------------------------------
class TestExportEndpoint:
    def test_export_nonexistent_task_404(self):
        response = client.get("/api/export/nonexistent-xyz/markdown")
        assert response.status_code == 404
