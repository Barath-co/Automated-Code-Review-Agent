# Automated Code Review Agent

A student project in the Agentic AI domain. It reviews submitted source code, flags likely issues, provides recommendations, and exports a JSON report.

## Features
- Browser-based code editor and source-file upload
- Language selection for Python, JavaScript, TypeScript, Java, C, C++, C#, Go, PHP and Ruby
- Local heuristic checks for common risky patterns and maintainability issues
- Optional AI review through the OpenAI API
- Severity counts, a quality indicator, findings by line, strengths, next steps
- JSON report export
- Responsive interface; no database required

## Requirements
- Python 3.10+
- pip
- Optional: OpenAI API key for AI-assisted review

## Run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000.

The local rule-based review works without an API key. To enable AI-assisted review, copy `.env.example` to `.env`, set `OPENAI_API_KEY`, then export the variables in your terminal or use a dotenv loader of your choice. For example on macOS/Linux:
```bash
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4o-mini"
python app.py
```
On Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="your-key"
$env:OPENAI_MODEL="gpt-4o-mini"
python app.py
```
Never commit API keys or submit private/proprietary code to an external AI service without permission.

## Project architecture
1. **Input layer** — editor or uploaded UTF-8 source file.
2. **Review orchestration** — Flask API validates language and size, then runs the review pipeline.
3. **Local analysis agent** — rule-based checks produce actionable findings.
4. **AI reviewer (optional)** — uses a configured model to add contextual suggestions; failures fall back to local analysis.
5. **Report layer** — severity counts, quality indicator, recommendations and JSON export.

## API
- `GET /` — UI
- `POST /api/review` — JSON body: `{"code":"...", "language":"python"}`
- `POST /api/upload` — multipart form field `file`
- `POST /api/export` — JSON body: `{"report": {...}}`, downloads JSON

## Limitations
- The score is a simple prioritization indicator, not a certified quality metric.
- The local engine uses pattern-based heuristics; it is not a full compiler or static-analysis engine.
- AI findings can be wrong. The app does not execute submitted code.
- The OpenAI API is optional and may incur usage charges.

## Suggested project report sections
Abstract, problem statement, objectives, existing system, proposed system, architecture, modules, implementation, test cases, results/screenshots, limitations, future enhancements and conclusion.
