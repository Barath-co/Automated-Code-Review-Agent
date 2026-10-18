"""Rule-based code review with an optional OpenAI-powered review stage."""
import os, re
from collections import Counter

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}

def add(findings, title, severity, line, message, suggestion, category="Quality", snippet=""):
    findings.append({
        "id": f"F{len(findings)+1:03d}", "title": title, "severity": severity,
        "line": max(1, int(line)), "message": message, "suggestion": suggestion,
        "category": category, "snippet": snippet[:180]
    })

def heuristic_review(code, language):
    findings = []
    lines = code.splitlines() or [""]
    lower = language.lower()

    # General patterns that are meaningful across several languages.
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.search(r'\b(TODO|FIXME|XXX)\b', line, re.I):
            add(findings, "Unresolved TODO/FIXME", "low", i,
                "This line marks work that may still be incomplete.",
                "Resolve the item or create a tracked issue.", "Maintainability", stripped)
        if re.search(r'\b(password|passwd|api[_-]?key|secret|access[_-]?token)\s*[:=]\s*[\'"][^\'"]{4,}[\'"]', line, re.I):
            add(findings, "Possible hard-coded secret", "critical", i,
                "A value resembling a credential is embedded in source code. This is a heuristic warning; verify whether it is a real secret.",
                "Move credentials to environment variables or a secret manager, rotate exposed credentials, and avoid committing them.", "Security", stripped)
        if re.search(r'\beval\s*\(', line) and lower in ("python", "javascript", "typescript", "php", "ruby"):
            add(findings, "Dynamic eval usage", "high", i,
                "Dynamic evaluation can execute input as code and may create an injection vulnerability.",
                "Avoid eval where possible. Use a safe parser or explicit mapping, and never evaluate untrusted input.", "Security", stripped)
        if re.search(r'\b(exec|os\.system|subprocess\.Popen)\s*\(', line) and lower == "python":
            add(findings, "Command execution call", "medium", i,
                "This call may be risky if any command or argument comes from untrusted input.",
                "Prefer subprocess.run with an argument list and shell=False; validate input and handle errors.", "Security", stripped)
        if re.search(r'==\s*(None|True|False)\b', line) and lower == "python":
            add(findings, "Non-idiomatic Python comparison", "low", i,
                "Python style generally uses identity checks for None and direct truth tests for booleans.",
                "Use `is None` for None checks and simplify boolean conditions where appropriate.", "Style", stripped)
        if re.search(r'\bexcept\s*:', line) and lower == "python":
            add(findings, "Bare exception handler", "medium", i,
                "A bare except can hide unexpected errors and make debugging difficult.",
                "Catch the specific exception types you expect, and log or re-raise unexpected errors.", "Reliability", stripped)
        if re.search(r'\bconsole\.log\s*\(', line) and lower in ("javascript", "typescript"):
            add(findings, "Debug logging", "info", i,
                "Console logging may be leftover development instrumentation.",
                "Remove it or replace it with a configurable logger if it is needed in production.", "Maintainability", stripped)
        if re.search(r'\bSELECT\b.*\bFROM\b', line, re.I) and re.search(r'\+\s*.*(input|request|query|user)', line, re.I):
            add(findings, "Possible SQL query concatenation", "high", i,
                "Building SQL with string concatenation can lead to SQL injection if input is untrusted.",
                "Use parameterized queries or prepared statements.", "Security", stripped)
        if len(line) > 120:
            add(findings, "Long source line", "low", i,
                f"This line has {len(line)} characters, which may be difficult to scan.",
                "Consider extracting expressions or wrapping the line for readability.", "Maintainability", stripped)

    # Language-specific checks.
    if lower == "python":
        for i, line in enumerate(lines, 1):
            if re.match(r'^\s*print\s*\(', line) and not line.strip().startswith("#"):
                add(findings, "Print statement in application code", "info", i,
                    "Print output can be useful during development but is often not a suitable application logging strategy.",
                    "Use logging with appropriate levels if this is production code.", "Maintainability", line.strip())
        if not re.search(r'\bdef\s+\w+\s*\(', code) and len(lines) > 25:
            add(findings, "Large script without functions", "low", 1,
                "The script appears to contain many lines without function definitions.",
                "Consider separating responsibilities into small functions or classes.", "Design", lines[0].strip())
    elif lower in ("javascript", "typescript"):
        for i, line in enumerate(lines, 1):
            if re.search(r'\bvar\s+', line):
                add(findings, "Legacy var declaration", "low", i,
                    "`var` has function scope and can make variable behavior harder to reason about.",
                    "Prefer `const` by default and `let` when reassignment is required.", "Style", line.strip())
            if re.search(r'==(?!=)', line):
                add(findings, "Loose equality comparison", "low", i,
                    "Loose equality performs type coercion and may lead to surprising comparisons.",
                    "Use strict equality (`===`) unless coercion is explicitly intended.", "Reliability", line.strip())
    elif lower in ("java", "c", "cpp", "csharp", "go", "php", "ruby"):
        if not code.strip():
            pass

    # Avoid duplicate findings that point to the same line/title.
    unique, seen = [], set()
    for f in findings:
        key = (f["title"], f["line"])
        if key not in seen:
            seen.add(key); unique.append(f)
    unique.sort(key=lambda f: (SEVERITY_ORDER.get(f["severity"], 9), f["line"]))
    for idx, finding in enumerate(unique, 1):
        finding["id"] = f"F{idx:03d}"
    return unique

def try_ai_review(code, language, existing):
    """Optional enhancement. Local review still works without an API key or SDK."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        prompt = (
            "Review this source code for correctness, security, reliability, and maintainability. "
            "Return JSON only with keys summary (string), findings (array of objects with title, severity "
            "(critical/high/medium/low/info), line (integer), message, suggestion, category, snippet), "
            "strengths (array of strings), and next_steps (array of strings). Do not claim code was executed. "
            "Avoid speculative findings; line numbers must refer to the supplied code. "
            f"Language: {language}\nSOURCE CODE:\n{code[:30000]}"
        )
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "system", "content": "You are a careful senior software code reviewer."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        import json
        payload = json.loads(response.choices[0].message.content)
        return payload
    except Exception:
        # Fail safely to local findings rather than failing the whole app.
        return None

def review_code(code, language):
    findings = heuristic_review(code, language)
    ai = try_ai_review(code, language, findings)
    engine = "Local heuristic review"
    summary = "Review completed using local rule-based checks. Findings are suggestions to verify, not proof of a defect."
    strengths = []
    next_steps = [
        "Verify each finding against the intended behavior.",
        "Run the language's formatter, linter, and automated tests.",
        "Review security-sensitive code before deployment."
    ]
    if ai:
        engine = "Hybrid local + AI review"
        summary = str(ai.get("summary") or summary)
        # AI findings are accepted as advisory findings; deduplicate title/line.
        seen = {(f["title"].lower(), f["line"]) for f in findings}
        for item in ai.get("findings", [])[:60]:
            try:
                title = str(item.get("title", "AI review finding"))[:120]
                line = max(1, min(len(code.splitlines()) or 1, int(item.get("line", 1))))
                if (title.lower(), line) in seen:
                    continue
                severity = str(item.get("severity", "medium")).lower()
                if severity not in SEVERITY_ORDER: severity = "medium"
                findings.append({
                    "id": f"F{len(findings)+1:03d}", "title": title, "severity": severity,
                    "line": line, "message": str(item.get("message", ""))[:1000],
                    "suggestion": str(item.get("suggestion", ""))[:1000],
                    "category": str(item.get("category", "AI review"))[:80],
                    "snippet": str(item.get("snippet", ""))[:180]
                })
                seen.add((title.lower(), line))
            except (ValueError, TypeError):
                continue
        strengths = [str(x)[:300] for x in ai.get("strengths", [])[:10]]
        next_steps = [str(x)[:300] for x in ai.get("next_steps", [])[:10]] or next_steps

    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f["severity"], 9), f["line"]))
    for idx, finding in enumerate(findings, 1):
        finding["id"] = f"F{idx:03d}"
    counts = Counter(f["severity"] for f in findings)
    return {
        "summary": summary,
        "findings": findings,
        "counts": {s: counts.get(s, 0) for s in ["critical", "high", "medium", "low", "info"]},
        "score": max(0, 100 - counts.get("critical",0)*25 - counts.get("high",0)*15 - counts.get("medium",0)*7 - counts.get("low",0)*3),
        "strengths": strengths,
        "next_steps": next_steps,
        "engine": engine,
        "disclaimer": "Automated findings can be false positives or miss issues. This tool does not execute the submitted code and is not a substitute for tests, expert review, or security auditing."
    }
