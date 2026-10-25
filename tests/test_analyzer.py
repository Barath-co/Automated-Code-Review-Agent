import unittest
from analyzer import review_code

class AnalyzerTests(unittest.TestCase):
    def test_detects_python_bare_except(self):
        result = review_code("try:\n    run()\nexcept:\n    pass", "python")
        self.assertTrue(any(f["title"] == "Bare exception handler" for f in result["findings"]))

    def test_detects_possible_secret(self):
        result = review_code('API_KEY = "sk_test_123456789"', "python")
        self.assertTrue(any(f["severity"] == "critical" for f in result["findings"]))

    def test_empty_findings_are_valid(self):
        result = review_code("public class Main {}", "java")
        self.assertIn("score", result)
        self.assertIn("findings", result)

    def test_no_api_key_no_error(self):
        """When no API key is set, ai_error should not appear in result."""
        import os
        from unittest.mock import patch
        env_without_keys = {k: v for k, v in os.environ.items()
                            if k not in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY")}
        with patch.dict("os.environ", env_without_keys, clear=True):
            result = review_code("x = 1", "python")
        self.assertNotIn("ai_error", result)
        self.assertEqual(result["engine"], "Local heuristic review")

    def test_invalid_gemini_key_surfaces_error(self):
        """When a bad Gemini key is set, ai_error must be present and engine must stay local."""
        from unittest.mock import patch, MagicMock
        with patch.dict("os.environ", {"GEMINI_API_KEY": "bad_key"}, clear=False), \
             patch("google.genai.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.models.generate_content.side_effect = Exception("400 API key not valid")
            mock_client_cls.return_value = mock_client

            result = review_code("x = 1", "python")
            self.assertIn("ai_error", result)
            self.assertIn("Gemini API error", result["ai_error"])
            self.assertEqual(result["engine"], "Local heuristic review")

    def test_gemini_review_integration(self):
        """Successful Gemini review merges AI findings with heuristic findings."""
        from unittest.mock import patch, MagicMock
        mock_response = MagicMock()
        mock_response.text = (
            '{"summary": "Looks good overall.", '
            '"findings": [{"title": "Consider Type Annotations", "severity": "info", '
            '"line": 1, "message": "Add type hints.", "suggestion": "Use typing", '
            '"category": "Quality", "snippet": "def add(a, b):"}], '
            '"strengths": ["Clean logic"], "next_steps": ["Add tests"]}'
        )

        with patch.dict("os.environ", {"GEMINI_API_KEY": "dummy_test_key", "GEMINI_MODEL": "gemini-2.5-flash"}), \
             patch("google.genai.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_response
            mock_client_cls.return_value = mock_client

            result = review_code("def add(a, b):\n    return a + b", "python")
            self.assertIn("Gemini review", result["engine"])
            self.assertEqual(result["summary"], "Looks good overall.")
            self.assertTrue(any(f["title"] == "Consider Type Annotations" for f in result["findings"]))
            self.assertIn("Clean logic", result["strengths"])
            self.assertNotIn("ai_error", result)          # no error on success
            self.assertNotIn("_engine_name", result)      # internal key must not leak

if __name__ == "__main__":
    unittest.main()
