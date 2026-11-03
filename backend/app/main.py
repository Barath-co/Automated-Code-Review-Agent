from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, List, Dict, Any
import os
from .config import config
from .models.schemas import ReviewRequest, FinalReviewReport
from .orchestrator.ncio_engine import NCIOOrchestrator
from .validators.code_validator import CodeValidator
from .db.storage import ReviewStorage
from .samples.test_cases import SAMPLE_TEST_CASES

app = FastAPI(
    title=config.PROJECT_NAME,
    version=config.PROJECT_VERSION,
    description="Neural Consensus Intelligence Orchestrator (NCIO) for Multi-Agent Code Review & Deterministic Validation"
)

# FIX C6: Restrict CORS to known origins instead of wildcard.
# allow_origins=["*"] combined with allow_credentials=True is rejected by browsers and is insecure.
# In production set ALLOWED_ORIGINS env var to your actual frontend domain.
import os as _os
_raw_origins = _os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:8000,http://localhost:5173,http://localhost:8000")
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=False,     # set True only if you add session cookies
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# FIX M1: Request body size limit (100 KB for code review tasks).
# Prevents memory exhaustion from extremely large code pastes.
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse

class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    MAX_BODY_BYTES = 200_000  # 200 KB

    async def dispatch(self, request: StarletteRequest, call_next):
        if request.method == "POST":
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.MAX_BODY_BYTES:
                return StarletteResponse(
                    content='{"detail": "Request body too large. Maximum 200 KB allowed."}',
                    status_code=413,
                    media_type="application/json"
                )
        return await call_next(request)

app.add_middleware(MaxBodySizeMiddleware)

@app.on_event("startup")
def startup_event():
    ReviewStorage.init_db()

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "system": config.PROJECT_NAME,
        "institution": config.ACADEMIC_INSTITUTION,
        "authors": config.AUTHORS,
        "guide": config.INTERNAL_GUIDE,
        "head_of_dept": config.HEAD_OF_DEPT,
        "default_gemini_model": config.DEFAULT_MODEL,
        "has_env_api_key": bool(config.GEMINI_API_KEY)
    }

@app.get("/api/samples")
def get_sample_test_cases():
    return SAMPLE_TEST_CASES

@app.post("/api/review", response_model=FinalReviewReport)
async def submit_code_review(request: ReviewRequest):
    try:
        report = await NCIOOrchestrator.execute_review(request)
        ReviewStorage.save_report(report)
        return report
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration failure: {str(e)}")

@app.post("/api/validate-only")
def validate_code_deterministically(payload: Dict[str, Any]):
    code = payload.get("code", "")
    language = payload.get("language", "python")
    if not code:
        raise HTTPException(status_code=400, detail="Code cannot be empty.")
    result = CodeValidator.validate(code, language)
    return result

@app.get("/api/history")
def get_review_history(limit: int = 15):
    return ReviewStorage.get_recent_tasks(limit)

@app.get("/api/report/{task_id}")
def get_report(task_id: str):
    report_dict = ReviewStorage.get_report_by_id(task_id)
    if not report_dict:
        raise HTTPException(status_code=404, detail="Review task not found.")
    return report_dict

@app.delete("/api/report/{task_id}")
def delete_report(task_id: str):
    """Delete a stored review report. Returns 404 if the task_id does not exist."""
    deleted = ReviewStorage.delete_report(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found.")
    return {"status": "deleted", "task_id": task_id}

@app.get("/api/export/{task_id}/markdown", response_class=PlainTextResponse)
def export_report_markdown(task_id: str):
    report_dict = ReviewStorage.get_report_by_id(task_id)
    if not report_dict:
        raise HTTPException(status_code=404, detail="Review task not found.")

    p = report_dict
    md = f"""# SATHYABAMA INSTITUTE OF SCIENCE AND TECHNOLOGY
## DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING
### PROFESSIONAL TRAINING I: CODE REVIEW AGENT REPORT
**Neural Consensus Intelligence Orchestrator (NCIO)**

- **Task Identifier**: `{p.get('task_id')}`
- **Execution Timestamp**: {p.get('created_at')}
- **Target Language**: {p.get('classification', {}).get('language', '').upper()}
- **Lines of Code (LOC)**: {p.get('classification', {}).get('loc')}
- **Consensus Score**: {p.get('consensus', {}).get('consensus_score')}% ({p.get('consensus', {}).get('strength')})
- **Human Review Escalation**: {'REQUIRED' if p.get('human_review_required') else 'PASSED'}

---

## 1. Executive Verdict
{p.get('executive_verdict')}

---

## 2. Multi-Agent Consensus Analysis (NCIO Workflow)
- **Consensus Summary**: {p.get('consensus', {}).get('consensus_notes')}

### Confirmed Points of Agreement:
"""
    for pt in p.get('consensus', {}).get('agreed_points', []):
        md += f"- [x] {pt}\n"

    conflicts = p.get('consensus', {}).get('conflicts', [])
    if conflicts:
        md += "\n### Material Discrepancies & Mediation:\n"
        for c in conflicts:
            md += f"- **Topic**: {c.get('topic')}\n"
            md += f"  - Resolution: {c.get('resolution')}\n"

    md += "\n---\n\n## 3. Consolidated Findings\n"
    for idx, f in enumerate(p.get('consolidated_findings', []), 1):
        md += f"### {idx}. [{f.get('severity')}] {f.get('title')}\n"
        md += f"- **Category**: {f.get('category')} | **Confidence**: {int(f.get('confidence', 0)*100)}%\n"
        if f.get('line_start'):
            md += f"- **Line Range**: {f.get('line_start')}-{f.get('line_end', f.get('line_start'))}\n"
        md += f"- **Explanation**: {f.get('explanation')}\n"
        md += f"- **Remediation**: `{f.get('suggested_fix')}`\n\n"

    md += "---\n\n## 4. Deterministic AST & Safety Validation\n"
    val = p.get('validation', {})
    md += f"- **Syntax Validity**: {'VALID' if val.get('syntax_valid') else 'INVALID'}\n"
    md += f"- **Parser Engine**: {val.get('parser_engine')}\n"
    md += f"- **Static Rule Violations Detected**: {len(val.get('static_vulnerabilities_detected', []))}\n"
    for cv in val.get('caveats', []):
        md += f"  - Caveat: {cv}\n"

    md += "\n---\n\n## 5. Validated Code Refactor\n```" + p.get('classification', {}).get('language', '') + "\n"
    md += p.get('refactored_code', '') + "\n```\n\n"

    md += "---\n\n## 6. Execution & Cost Telemetry (Table 4.4)\n"
    met = p.get('metrics', {})
    md += f"- **Total Latency**: {met.get('total_latency_ms')} ms\n"
    md += f"- **Agents Dispatched**: {met.get('agents_dispatched')}\n"
    md += f"- **Total Tokens**: {met.get('total_tokens')}\n"
    md += f"- **Estimated Cost**: ₹{met.get('estimated_cost_inr')} INR (${met.get('estimated_cost_usd')} USD)\n"
    md += f"- **Provider Layer**: {met.get('provider_used')}\n"

    md += f"\n---\n*Report generated by {config.PROJECT_NAME} | Developed by {', '.join(config.AUTHORS)} under guidance of {config.INTERNAL_GUIDE}.*\n"
    return md

@app.get("/api/academic/download/pdf")
def download_academic_pdf():
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "reports", "Code_Review_Agent_Report.pdf"))
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Academic PDF report not found.")
    return FileResponse(pdf_path, media_type="application/pdf", filename="Sathyabama_BE_CodeReviewAgent_Report.pdf")

@app.get("/api/academic/download/docx")
def download_academic_docx():
    docx_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "reports", "Code_Review_Agent_Report.docx"))
    if not os.path.exists(docx_path):
        raise HTTPException(status_code=404, detail="Academic DOCX report not found.")
    return FileResponse(docx_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="Sathyabama_BE_CodeReviewAgent_Report.docx")

# Mount production frontend build if available
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        # Serve static file if exists, else return index.html
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

