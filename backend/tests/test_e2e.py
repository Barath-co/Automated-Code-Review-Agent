import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.orchestrator.ncio_engine import NCIOOrchestrator
from app.models.schemas import ReviewRequest

async def main():
    test_code = '''import os
API_KEY = "sk-live-1234567890abcdef123456"

def query_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    try:
        return cursor.fetchall()
    except:
        pass
'''
    req = ReviewRequest(code=test_code, language="python", mode="consensus")
    report = await NCIOOrchestrator.execute_review(req)
    print("SUCCESS: Review Task Executed!")
    print(f"Task ID: {report.task_id}")
    print(f"Language: {report.classification.language} | LOC: {report.classification.loc}")
    print(f"Consensus Score: {report.consensus.consensus_score}% ({report.consensus.strength})")
    print(f"Candidates Dispatched: {len(report.candidates)}")
    print(f"Consolidated Findings: {len(report.consolidated_findings)}")
    print(f"AST Syntax Valid: {report.validation.syntax_valid}")
    print(f"Estimated Cost: INR {report.metrics.estimated_cost_inr}")
    print(f"Human Review Flag: {report.human_review_required}")

if __name__ == "__main__":
    asyncio.run(main())
