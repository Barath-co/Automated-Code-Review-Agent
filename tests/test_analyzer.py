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

    def test_gemini_review_integration(self):
        from unittest.mock import patch, MagicMock
        mock_response = MagicMock()
        mock_response.text = '{"summary": "Looks good overall.", "findings": [{"title": "Consider Type Annotations", "severity": "info", "line": 1, "message": "Add type hints.", "suggestion": "Use typing", "category": "Quality", "snippet": "def add(a, b):"}], "strengths": ["Clean logic"], "next_steps": ["Add tests"]}'
        
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

if __name__ == "__main__":
    unittest.main()
