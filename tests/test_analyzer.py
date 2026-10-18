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

if __name__ == "__main__":
    unittest.main()
