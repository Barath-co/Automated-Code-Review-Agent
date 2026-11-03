import asyncio
import time
import re
from typing import Optional, List
from .base import BaseModelAdapter
from ..models.schemas import CandidateOutput, ReviewFinding
from ..validators.code_validator import CodeValidator

class SimulatedConsensusAdapter(BaseModelAdapter):
    """
    High-fidelity offline simulation adapter for demonstration, academic review viva,
    and fallback resilience (fulfills Chapter 3 Risk Register & FR-09).
    Emulates distinct AI specialist behaviors based on AST and heuristic rules.

    FIX (C2): Replaced time.sleep() with await asyncio.sleep() so the event loop
    is not blocked and asyncio.gather() can provide genuine concurrency.

    FIX (H5): Token counts in simulation mode are clearly labeled as estimated/simulated
    rather than real API counts.
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

        normalized_lang = language.lower()

        # Run static validation detection to ground simulation in real code inspection
        val_result = CodeValidator.validate(code, language)

        if "Security" in persona:
            # Focus on security, sanitization, secrets, dangerous calls
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
                # Add general security hygiene finding if code is clean or simple
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
            
            # Simple automatic mitigation replacements for proposed code
            proposed_code = re.sub(
                r'cursor\.execute\(f"SELECT\s+\*\s+FROM\s+([a-zA-Z0-9_]+)\s+WHERE\s+([a-zA-Z0-9_]+)\s*=\s*\'?\{([a-zA-Z0-9_]+)\}\'?"\)',
                r'cursor.execute("SELECT * FROM \1 WHERE \2 = %s", (\3,))',
                code
            )
            proposed_code = re.sub(
                r'eval\(([^)]+)\)',
                r'# FIXED: Removed unsafe eval call\njson.loads(\1)',
                proposed_code
            )
            proposed_code = re.sub(
                r'API_KEY\s*=\s*["\'][^"\']+["\']',
                'API_KEY = os.getenv("API_KEY", "default-fallback-key")',
                proposed_code
            )

        elif "Performance" in persona:
            # Focus on algorithmic efficiency, memory leaks, I/O blocking
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

        else:
            # Reliability, Style, Exception Handling
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

        latency_ms = int((time.time() - start_time) * 1000)
        # FIX (H5): Token counts for simulation mode are estimated, not real API counts.
        # They are labelled accordingly and should not be compared to live Gemini token usage.
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
            proposed_code=proposed_code if proposed_code != code else code + "\n# Validated and formatted by NCIO Agent",
            latency_ms=latency_ms,
            token_usage=tokens
        )
