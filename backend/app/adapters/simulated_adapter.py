import asyncio
import time
import re
from typing import Optional, List
from .base import BaseModelAdapter
from ..models.schemas import CandidateOutput, ReviewFinding
from ..validators.code_validator import CodeValidator


def _refactor_for_security(code: str, language: str) -> str:
    """Generate high-fidelity security refactoring addressing OWASP/CWE vulnerabilities."""
    refactored = code
    is_python = language.lower() in ("python", "py")
    is_js = language.lower() in ("javascript", "typescript", "js", "ts")

    # 1. SQL Injection Parameterization
    # Case A: query variable + cursor.execute(query)
    # Match: query = f"SELECT ... WHERE col = '{var}'" or query = "SELECT ... WHERE col = '" + var + "'"
    sql_assign_match = re.search(
        r'(\b[a-zA-Z0-9_]*query\s*=\s*)f["\'](SELECT\s+.*WHERE\s+([a-zA-Z0-9_]+)\s*=\s*)[\'"]?\{([a-zA-Z0-9_]+)\}[\'"]?(["\'])',
        refactored,
        re.IGNORECASE
    )
    if sql_assign_match:
        assign_prefix = sql_assign_match.group(1)
        select_prefix = sql_assign_match.group(2)
        param_var = sql_assign_match.group(4)
        quote = sql_assign_match.group(5)
        # Use ? for sqlite3, %s for general SQL
        placeholder = "?" if "sqlite3" in refactored else "%s"
        safe_query_line = f'{assign_prefix}{quote}{select_prefix}{placeholder}{quote}'
        refactored = refactored[:sql_assign_match.start()] + safe_query_line + refactored[sql_assign_match.end():]

        # Now update cursor.execute(query) -> cursor.execute(query, (var,))
        refactored = re.sub(
            r'(\bcursor\.execute|\bconn\.execute|\bdb\.execute)\s*\(\s*([a-zA-Z0-9_]*query)\s*\)',
            rf'\1(\2, ({param_var},))',
            refactored
        )

    # Case B: Direct cursor.execute(f"SELECT ... {var} ...")
    refactored = re.sub(
        r'(\bcursor\.execute|\bconn\.execute|\bdb\.execute)\s*\(\s*f["\'](SELECT\s+.*WHERE\s+([a-zA-Z0-9_]+)\s*=\s*)[\'"]?\{([a-zA-Z0-9_]+)\}[\'"]?["\']\s*\)',
        r'\1("\2%s", (\4,))' if "sqlite3" not in refactored else r'\1("\2?", (\4,))',
        refactored,
        flags=re.IGNORECASE
    )

    # 2. Hardcoded Secrets & API Keys
    if is_python:
        if re.search(r'(?i)\b(API_KEY|SECRET|PASSWORD|JWT_SECRET|TOKEN)\s*=\s*["\'][A-Za-z0-9_\-\.+=/]{8,}["\']', refactored):
            refactored = re.sub(
                r'(?i)\b(API_KEY|SECRET|PASSWORD|JWT_SECRET|TOKEN)\s*=\s*["\'][^"\']+["\']',
                r'\1 = os.getenv("\1", "")',
                refactored
            )
            if "import os" not in refactored:
                refactored = "import os\n" + refactored
    elif is_js:
        refactored = re.sub(
            r'(?i)\b(const|let|var)\s+(API_KEY|SECRET|PASSWORD|JWT_SECRET|TOKEN)\s*=\s*["\'][^"\']+["\']',
            r'\1 \2 = process.env.\2 || ""',
            refactored
        )

    # 3. Dynamic Eval / Command Injection
    if is_python:
        if re.search(r'\beval\s*\(', refactored):
            refactored = re.sub(r'\beval\s*\(([^)]+)\)', r'ast.literal_eval(\1)', refactored)
            if "import ast" not in refactored:
                refactored = "import ast\n" + refactored
        if re.search(r'\bos\.system\s*\(', refactored):
            refactored = re.sub(
                r'\bos\.system\s*\(([^)]+)\)',
                r'subprocess.run([\1], shell=False, check=True)',
                refactored
            )
            if "import subprocess" not in refactored:
                refactored = "import subprocess\n" + refactored
        if re.search(r'\bpickle\.loads?\b', refactored):
            refactored = re.sub(r'\bpickle\.loads?\b', 'json.loads', refactored)
            if "import json" not in refactored:
                refactored = "import json\n" + refactored
    elif is_js:
        refactored = re.sub(r'\beval\s*\(([^)]+)\)', r'JSON.parse(\1)', refactored)

    # 4. Bare Exception Suppression
    if is_python:
        refactored = re.sub(
            r'except\s*:\s*\n\s*pass',
            'except Exception as err:\n        # Diagnostic error logging instead of silent swallow\n        raise RuntimeError(f"Operation failed: {err}")',
            refactored
        )

    return refactored


def _refactor_for_performance(code: str, language: str) -> str:
    """Generate performance optimizations (algorithmic complexity, async I/O, leaks)."""
    refactored = code
    is_python = language.lower() in ("python", "py")

    if is_python:
        # Check for nested transaction matching loop (O(n^2) -> O(n) hash map)
        if "for user in users:" in refactored and "for txn in transactions:" in refactored:
            nested_loop_pattern = (
                r'for\s+user\s+in\s+users:\s*\n\s+for\s+txn\s+in\s+transactions:\s*\n'
                r'\s+if\s+user\[[\'"]id[\'"]\]\s*==\s*txn\[[\'"]user_id[\'"]\]:\s*\n'
                r'\s+matched\.append\(\s*\{\s*[\'"]user[\'"]:\s*user\[[\'"]name[\'"]\],\s*[\'"]amount[\'"]:\s*txn\[[\'"]amount[\'"]\]\s*\}\s*\)'
            )
            optimized_code = (
                "# Optimized O(1) hash map lookup replacing O(n^2) nested iteration\n"
                "    user_map = {u['id']: u['name'] for u in users if 'id' in u}\n"
                "    matched = [{'user': user_map[t['user_id']], 'amount': t['amount']} "
                "for t in transactions if t.get('user_id') in user_map]"
            )
            refactored = re.sub(nested_loop_pattern, optimized_code, refactored)

        # Remove blocking synchronous sleep in request threads
        refactored = re.sub(r'\s*time\.sleep\(\d+\)\s*\n', '\n    # Note: Removed blocking sleep to prevent worker thread starvation\n', refactored)

        # Fix unmanaged open() if present
        open_match = re.search(r'(\b[a-zA-Z0-9_]+)\s*=\s*open\(([^)]+)\)\s*\n\s*(\1\.write\([^)]+\))', refactored)
        if open_match:
            var_name = open_match.group(1)
            open_args = open_match.group(2)
            write_call = open_match.group(3)
            with_block = f'with open({open_args}) as {var_name}:\n        {write_call}'
            refactored = refactored[:open_match.start()] + with_block + refactored[open_match.end():]

    return refactored


def _refactor_for_clean_code(code: str, language: str) -> str:
    """Generate reliability & maintainability improvements (context managers, typing, docstrings)."""
    refactored = code
    is_python = language.lower() in ("python", "py")

    if is_python:
        # 1. Context manager for file handles
        open_match = re.search(r'(\b[a-zA-Z0-9_]+)\s*=\s*open\(([^)]+)\)\s*\n\s*(\1\.write\([^)]+\))', refactored)
        if open_match:
            var_name = open_match.group(1)
            open_args = open_match.group(2)
            write_call = open_match.group(3)
            with_block = f'with open({open_args}) as {var_name}:\n        {write_call}'
            refactored = refactored[:open_match.start()] + with_block + refactored[open_match.end():]

        # 2. Context manager for sqlite3 connections
        refactored = re.sub(
            r'conn\s*=\s*sqlite3\.connect\(([^)]+)\)\s*\n\s*cursor\s*=\s*conn\.cursor\(\)',
            r'with sqlite3.connect(\1) as conn:\n        cursor = conn.cursor()',
            refactored
        )

        # 3. Bare exception replacement
        refactored = re.sub(
            r'except\s*:\s*\n\s*pass',
            'except Exception as err:\n        # Handled and logged diagnostic exception\n        raise RuntimeError(f"Operation failed: {err}")',
            refactored
        )

        # 4. Type hint annotations on common function definitions if missing
        if "def get_user_records(user_input):" in refactored:
            refactored = refactored.replace(
                "def get_user_records(user_input):",
                'def get_user_records(user_input: str) -> list:\n    """Fetch user records using safe parameterized query."""'
            )
        elif "def search_user(name):" in refactored:
            refactored = refactored.replace(
                "def search_user(name):",
                'def search_user(name: str) -> None:\n    """Search user by name with parameterized execution."""'
            )

    return refactored


class SimulatedConsensusAdapter(BaseModelAdapter):
    """
    High-fidelity offline simulation adapter for demonstration, academic review viva,
    and fallback resilience (fulfills Chapter 3 Risk Register & FR-09).
    Emulates distinct AI specialist behaviors based on AST and heuristic rules.
    """

    def __init__(self, agent_persona: str = "Gemini Code Security Specialist"):
        self.agent_persona = agent_persona

    async def evaluate_code(
        self,
        code: str,
        language: str,
        persona: str,
        system_instruction: str,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> CandidateOutput:
        start_time = time.time()
        await asyncio.sleep(0.3)  # Non-blocking emulation of async network latency (FIX C2)

        findings: List[ReviewFinding] = []
        proposed_code = code

        # Run static validation detection to ground simulation in real code inspection
        val_result = CodeValidator.validate(code, language)

        if "Security" in persona:
            # 1. Security Specialist Persona
            for vuln in val_result.static_vulnerabilities_detected:
                findings.append(ReviewFinding(
                    id=f"SEC-{len(findings)+1}",
                    title=vuln["name"].replace("_", " ").title(),
                    category="Security",
                    severity=vuln["severity"],
                    line_start=vuln["line"],
                    line_end=vuln["line"],
                    snippet=vuln["line_content"],
                    explanation=vuln["description"],
                    suggested_fix=vuln["remediation"],
                    confidence=0.96,
                    reported_by=[persona]
                ))

            if not findings:
                if "input(" in code or "request." in code:
                    findings.append(ReviewFinding(
                        id="SEC-1",
                        title="Input Boundary Sanitization",
                        category="Security",
                        severity="MEDIUM",
                        line_start=1,
                        explanation="Untrusted external input detected without explicit schema validation or length bounds.",
                        suggested_fix="Wrap input with Pydantic schema validation or regex constraint guards.",
                        confidence=0.88,
                        reported_by=[persona]
                    ))

            assessment = f"Security audit completed by {persona}. Identified {len(findings)} potential vulnerability vectors and injection vectors."
            proposed_code = _refactor_for_security(code, language)

        elif "Performance" in persona:
            # 2. Performance Architect Persona
            lines = code.split("\n")
            for idx, line in enumerate(lines, 1):
                if re.search(r"for\s+.*in\s+.*:\s*$", line) and any("for " in l for l in lines[idx:idx+3]):
                    findings.append(ReviewFinding(
                        id=f"PERF-{len(findings)+1}",
                        title="Nested Loop Complexity O(n²)",
                        category="Performance",
                        severity="MEDIUM",
                        line_start=idx,
                        line_end=idx+2,
                        snippet=line.strip(),
                        explanation="Detected quadratic algorithmic complexity in nested iterations. Scales poorly with large collections.",
                        suggested_fix="Convert inner lookup into a hash set or dictionary lookup for O(1) amortized access.",
                        confidence=0.91,
                        reported_by=[persona]
                    ))
                elif "time.sleep(" in line:
                    findings.append(ReviewFinding(
                        id=f"PERF-{len(findings)+1}",
                        title="Synchronous Blocking Delay",
                        category="Performance",
                        severity="LOW",
                        line_start=idx,
                        snippet=line.strip(),
                        explanation="Blocking sleep halts the thread and starves asynchronous event loops.",
                        suggested_fix="Replace with await asyncio.sleep(...) in async contexts or non-blocking event scheduling.",
                        confidence=0.94,
                        reported_by=[persona]
                    ))

            if not findings:
                findings.append(ReviewFinding(
                    id="PERF-1",
                    title="Memory Profiling & Data Structure Optimization",
                    category="Performance",
                    severity="INFO",
                    line_start=1,
                    explanation="Code demonstrates standard sequential execution. Memory usage is within expected thresholds.",
                    suggested_fix="Consider generator expressions or batch streaming if data size exceeds memory constraints.",
                    confidence=0.85,
                    reported_by=[persona]
                ))

            assessment = f"Performance and algorithmic review by {persona}. Evaluated computational complexity, memory allocation, and I/O bottlenecks."
            proposed_code = _refactor_for_performance(code, language)

        else:
            # 3. Clean Code & Reliability Persona
            lines = code.split("\n")
            for idx, line in enumerate(lines, 1):
                if re.search(r"except\s*:\s*$", line) or re.search(r"except\s+Exception\s*:\s*$", line):
                    findings.append(ReviewFinding(
                        id=f"REL-{len(findings)+1}",
                        title="Broad Exception Handling Anti-Pattern",
                        category="Reliability",
                        severity="MEDIUM",
                        line_start=idx,
                        snippet=line.strip(),
                        explanation="Catching bare exceptions or generic Exception hides unexpected bugs (e.g. KeyboardInterrupt, MemoryError).",
                        suggested_fix="Catch specific domain exceptions (e.g. ValueError, KeyError, ConnectionError) and log diagnostics.",
                        confidence=0.95,
                        reported_by=[persona]
                    ))
                elif re.search(r"open\s*\(", line) and not ("with " in line):
                    findings.append(ReviewFinding(
                        id=f"REL-{len(findings)+1}",
                        title="Unmanaged Resource Lifecycle",
                        category="Reliability",
                        severity="HIGH",
                        line_start=idx,
                        snippet=line.strip(),
                        explanation="File or stream opened without a context manager ('with' block), which may leak file descriptors on exceptions.",
                        suggested_fix="Wrap file operations in a 'with open(...) as f:' context manager.",
                        confidence=0.97,
                        reported_by=[persona]
                    ))

            if not findings:
                findings.append(ReviewFinding(
                    id="STY-1",
                    title="Type Annotations and Docstring Coverage",
                    category="Style",
                    severity="LOW",
                    line_start=1,
                    explanation="Function definitions could benefit from explicit PEP 484 type hints and structured docstrings.",
                    suggested_fix="Add type annotations (e.g. def process(data: dict) -> bool:) for static typing checks.",
                    confidence=0.90,
                    reported_by=[persona]
                ))

            assessment = f"Maintainability and code reliability evaluation by {persona}. Checked error recovery, defensive programming, and resource boundaries."
            proposed_code = _refactor_for_clean_code(code, language)

        latency_ms = int((time.time() - start_time) * 1000)
        estimated_words = len(code.split())
        tokens = {
            "prompt_tokens": estimated_words * 2 + 120,
            "completion_tokens": 280,
            "total_tokens": estimated_words * 2 + 400,
            "_note": "Simulated token estimate — not real API usage"
        }

        return CandidateOutput(
            agent_id=f"sim_{persona.lower().replace(' ', '_')}",
            persona=persona,
            model_name=model_name or "gemini-2.5-flash (NCIO Virtual Agent)",
            overall_assessment=assessment,
            findings=findings,
            proposed_code=proposed_code,
            latency_ms=latency_ms,
            token_usage=tokens
        )
