import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.validators.code_validator import CodeValidator
from app.consensus.analyzer import ConsensusAnalyzer
from app.models.schemas import CandidateOutput, ReviewFinding, DeterministicValidation

class TestNCIO(unittest.TestCase):
    def test_sql_injection(self):
        code = 'def test(x):\n    query = f"SELECT * FROM users WHERE name = \'{x}\'"\n    cursor.execute(query)'
        res = CodeValidator.validate(code, "python")
        self.assertTrue(res.syntax_valid)
        names = [v["name"] for v in res.static_vulnerabilities_detected]
        self.assertIn("SQL_INJECTION_RISK", names)

    def test_syntax_failure(self):
        code = 'def broken(:\n    pass'
        res = CodeValidator.validate(code, "python")
        self.assertFalse(res.syntax_valid)

if __name__ == "__main__":
    unittest.main()
