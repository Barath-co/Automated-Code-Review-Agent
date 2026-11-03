# CODE REVIEW AGENT
## Neural Consensus Intelligence Orchestrator (NCIO)

**Department of Computer Science and Engineering**  
**School of Computing**  
**SATHYABAMA INSTITUTE OF SCIENCE AND TECHNOLOGY**  
*(Deemed to be University • Accredited "A++" by NAAC • Approved by AICTE)*  
Chennai – 600119, Tamil Nadu, India • November 2026  

---

### Project Bonafide Credentials
- **Project Title**: CODE REVIEW AGENT
- **Case Study & Core Architecture**: Neural Consensus Intelligence Orchestrator (NCIO)
- **Degree Award**: Bachelor of Engineering (B.E.) in Computer Science and Engineering
- **Student Investigators**:
  - **Barath Babu** (Register No: 44110102)
  - **Araveeti Shravanth Reddy** (Register No: 44110063)
- **Internal Guide**: **Dr. NANCY NOELLA, M.E., Ph.D.**
- **Head of the Department / Dean**: **Dr. L. LAKSHMANAN, M.E., Ph.D.**
- **Professional Training**: Agentic AI Certification, Credo Systemz (Candidate ID: CSZ260824)

---

## 1. Project Overview & Problem Statement
Modern automated code review tools predominantly rely on a single Large Language Model (LLM) query. Single-model approaches suffer from hallucinated security flaws, unverified suggestions, and subtle shared blind spots. 

The **Neural Consensus Intelligence Orchestrator (NCIO)** solves this by implementing an Agentic AI workflow based on the principles established in Figures 4.1, 4.2, and 4.3 of the project report:
1. **Multi-Agent Specialist Personas**: Dispatches concurrent specialized AI reviewers (Application Security Specialist, Performance & Concurrency Architect, Reliability & Clean Code Engineer).
2. **Consensus & Conflict Analysis**: Normalizes candidate findings, groups issues by semantic vector and line proximity, calculates a consensus agreement score, and explicitly flags material disagreements without forcing artificial consensus.
3. **Deterministic AST & Static Validation Gate**: Integrates programmatic Abstract Syntax Tree (AST) analysis and regex heuristic checks to verify code syntax, detect OWASP/CWE injection patterns, and ensure refactored code compiles cleanly without LLM bias.
4. **Traceable Response Synthesis**: Delivers unified side-by-side git diffs, actionable recommendations, and full telemetry (latency, token consumption, and INR/USD cost estimation as detailed in Report Table 4.4).

---

## 2. System Architecture

```
+-------------------------------------------------------------------------+
|                              USER INTERFACE                             |
|    Modern Light-Theme Executive IDE & Interactive Architecture Explorer |
+------------------------------------+------------------------------------+
                                     | HTTP REST / JSON
                                     v
+-------------------------------------------------------------------------+
|                               API GATEWAY                               |
|        FastAPI Backend (Port: 8000) • CORS Guard • MaxBodySize (200KB)  |
+------------------------------------+------------------------------------+
                                     | Task Envelope
                                     v
+-------------------------------------------------------------------------+
|                        PREFLIGHT VALIDATION GATE                        |
|       AST Syntax Check • Basic Security Heuristics • Input Bounds       |
+------------------------------------+------------------------------------+
                                     | Validated AST Payload
                                     v
+-------------------------------------------------------------------------+
|                              ORCHESTRATOR                               |
|   Task Classifier • Budget Controller • Per-Agent Async Execution Engine|
+-----------------+-------------------+-------------------+---------------+
                  |                   |                   |
                  v                   v                   v
+-------------------------------------------------------------------------+
|                             MODEL ADAPTERS                              |
|   Gemini Security Persona | Gemini Perf Persona | Gemini Style Persona  |
|         (Powered by Google Gemini 2.5 Flash / 1.5 Pro / Pro)            |
|         [Async non-blocking threads with 30s per-agent timeout]         |
+-----------------+-------------------+-------------------+---------------+
                  \                   |                   /
                   \                  |                  /
                    v                 v                 v
+-------------------------------------------------------------------------+
|                     VALIDATION & CONSENSUS ENGINE                       |
|   • Semantic Grouping & Consensus Dial Calculation (0-100%)             |
|   • Material Discrepancy Mediation & Contested Risk Reporting           |
|   • Multi-Candidate Refactor Scoring (Syntax + Security Delta + Bonus)  |
|   • Postflight AST Validation of Selected Refactor                      |
+------------------------------------+------------------------------------+
                                     | Validated Result
                                     v
+-------------------------------------------------------------------------+
|                       RESPONSE DELIVERY & STORAGE                       |
|   • Unified Side-by-Side Diff Viewer (Original vs. Refactored Code)     |
|   • SQLite Task Audit Log & Markdown Viva Dossier Export                |
|   • Telemetry: Latency, Token Usage, and Cost Estimate (INR / USD)     |
+-------------------------------------------------------------------------+
```

---

## 3. Technology Stack

- **Frontend**: React 19, Vite, Tailwind-style modular CSS, Lucide Icons, JetBrains Mono typography.
- **Backend**: Python 3.12+, FastAPI, Uvicorn, Pydantic v2.
- **AI Model Engine**: Google Gemini API via official `google-genai` SDK (`gemini-2.5-flash`, `gemini-1.5-flash`, `gemini-2.5-pro`).
- **Resilience Layer**: High-fidelity virtual consensus fallback simulator for offline Viva Voce demonstrations.
- **Validation Engine**: Python `ast` syntax parser, branch count metric, OWASP/CWE regex heuristic engine.
- **Persistence**: SQLite audit database (`reviews.db`) with complete error logging and soft-delete/hard-delete endpoints.

---

## 4. Architectural & Production Improvements

This codebase has undergone a rigorous architectural audit and hardening process:

| Issue Fixed | Category | Description |
|---|---|---|
| **C1: Non-Blocking Async Gemini Execution** | Concurrency | Synchronous SDK calls inside `async def` wrapped in `asyncio.to_thread` to achieve true concurrent execution during `asyncio.gather()`. |
| **C2: Async Simulation Sleep** | Concurrency | Replaced blocking `time.sleep` with `await asyncio.sleep` in simulated adapter. |
| **C3: Multi-Candidate Refactor Selection** | AI Safety | Replaced blind first-candidate pick with multi-criteria rubric: syntax validation (+3), security delta vs original (+2), consensus agreement (+1), invalid syntax disqualification (-99). Falls back to original code if all candidates fail. |
| **C4: Orthogonal Syntax & Security Logic** | Validation | Fixed `validation_passed` logic so that security vulnerabilities are never hidden just because the code parses cleanly. |
| **C5: In-Memory API Key Session Security** | Security | Eliminated persistent storage of plain API keys in browser `localStorage`. Keys are maintained only in active React session memory. |
| **C6: Origin-Restricted CORS** | Security | Replaced insecure wildcard CORS (`*` with credentials) with configurable allowed origins (`ALLOWED_ORIGINS`). |
| **C7: Real Telemetry Progression** | UX / Accuracy | Eliminated synthetic JavaScript `setTimeout` progress timers; UI reflects genuine server-reported execution. |
| **M1: Request Body Size Middleware** | Resilience | Enforced 200 KB request body limit to protect against denial-of-service from memory exhaustion. |
| **H1: McCabe Complexity Honesty** | Metrics | Renamed `estimated_branch_complexity` to `branch_count` with explicit documentation that it is a branch tally, not McCabe M = E - N + 2P. |
| **H2: Non-Python Heuristic Caveat** | Transparency | Clear caveats emitted when reviewing non-Python languages, clarifying that parser checks are limited to bracket heuristics. |
| **H6: Single-Agent Honesty** | Transparency | Single-agent mode returns `consensus_score = 0.0` and strength `"SINGLE_AGENT_MODE"` instead of fabricated 100% agreement. |
| **M2: SQLite Error Handling & Deletion** | Persistence | Wrapped database operations in try/except blocks with structured logging and added `DELETE /api/report/{task_id}` endpoint. |

---

## 5. API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System health, academic credentials, and Gemini configuration status |
| `GET` | `/api/samples` | Built-in benchmark test cases from project report |
| `POST` | `/api/review` | Submit code for multi-agent consensus review and refactoring |
| `POST` | `/api/validate-only` | Run preflight deterministic AST and regex checks without AI |
| `GET` | `/api/history` | Retrieve recent audit logs (configurable limit, default 15) |
| `GET` | `/api/report/{task_id}` | Fetch detailed JSON report for a specific review task |
| `DELETE` | `/api/report/{task_id}` | Delete a stored review task from database |
| `GET` | `/api/export/{task_id}/markdown` | Export formatted academic Markdown report |
| `GET` | `/api/academic/download/pdf` | Download official B.E. Project Report (PDF) |
| `GET` | `/api/academic/download/docx` | Download official B.E. Project Report (DOCX) |

---

## 6. Quick Start & Execution

### Prerequisites
- Python 3.10+
- Node.js 18+ (only needed if rebuilding the frontend)

### Option A: 1-Click Launch (Recommended)
Simply double-click `start.bat` or run:
```powershell
.\start.bat
```
Then open your browser at:
👉 **`http://127.0.0.1:8000`**

The FastAPI backend automatically serves both the API and the compiled React production frontend!

### Option B: Running Backend & Frontend Separately (Development Mode)

1. **Start Backend**:
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Backend API will be accessible at `http://127.0.0.1:8000` and Swagger docs at `http://127.0.0.1:8000/docs`.

2. **Start Frontend (Vite Dev Server)**:
```powershell
cd frontend
npm run dev
```
Frontend will be accessible at `http://localhost:5173`.

---

## 7. Google Gemini API Configuration

1. You can configure your API key either in `backend/.env`:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
ALLOWED_ORIGINS=http://127.0.0.1:8000,http://localhost:5173
```
2. **Or directly in the Web UI**:
   - Click the **Configure** or **Model Pill** in the top navigation bar.
   - Enter your Gemini API key and choose your desired model (`gemini-2.5-flash`, `gemini-1.5-flash`, `gemini-2.5-pro`).
   - If no key is entered, the app gracefully runs in **Virtual Consensus Simulation Mode** with realistic AST-grounded multi-agent reviews.

> [!NOTE]
> When live mode is active, submitted source code snippets are sent to Google's Gemini API for analysis. In compliance with enterprise data handling practices, API keys are held in browser memory only and never stored to disk or localStorage.

---

## 8. Automated Testing

Run the full automated test suite (57 tests across 5 modules):
```powershell
cd backend
python -m pytest tests/ -v
```

Test modules:
- `tests/test_validator.py` (24 tests): AST syntax, regex security checks, command injection, credentials, complexity branch count, non-Python heuristics.
- `tests/test_refactor_selection.py` (7 tests): Refactor candidate scoring, invalid proposal rejection, consensus boost, fallback to original code.
- `tests/test_api.py` (17 tests): Health, review validation, max body size limits, history, report retrieval, and deletion.
- `tests/test_orchestrator.py` (5 tests): Input bounds, simulation end-to-end orchestration, single-agent honesty.
- `tests/test_ncio.py` (4 tests): Core validation baseline and consensus analysis.

---

## 9. Academic References & Citations
- [1] Brown, T. B., et al. "Language Models are Few-Shot Learners." NeurIPS, 2020.
- [2] Vaswani, A., et al. "Attention Is All You Need." NeurIPS, 2017.
- [3] Yao, S., et al. "ReAct: Synergizing Reasoning and Acting in Language Models." ICLR, 2023.
- [4] Lewis, P., et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." NeurIPS, 2020.
- [5] NIST. Artificial Intelligence Risk Management Framework (AI RMF 1.0), 2023.
