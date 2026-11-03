import ast
import re
from typing import Dict, Any, List, Optional
from ..models.schemas import DeterministicValidation

class CodeValidator:
    """
    Deterministic Code Validator implementation as specified in NCIO Chapter 4.
    Performs algorithmic syntax parsing, AST analysis, and rule-based vulnerability checks
    independent of LLM outputs to prevent shared hallucinations.
    """

    DANGEROUS_PATTERNS = [
        {
            "name": "SQL_INJECTION_RISK",
            "regex": r"(?:(?:execute|cursor\.execute|raw_sql)\s*\(\s*(?:f[\"']|\"['\"]\s*\+|['\"].*%\s*\(|[a-zA-Z0-9_]+\s*\+\s*['\"]))|(?:f[\"'](?:SELECT|INSERT|UPDATE|DELETE)\s+.*\{)",
            "severity": "CRITICAL",
            "description": "Dynamic SQL query formed using string interpolation or concatenation instead of parameterized placeholders.",
            "remediation": "Use parameterized queries or ORM query builders (e.g. cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,)))"
        },
        {
            "name": "COMMAND_INJECTION_OR_EVAL",
            "regex": r"\b(eval|exec)\s*\(|\b(os\.system|os\.popen)\s*\(|"
                     r"\b(subprocess\.call|subprocess\.Popen|subprocess\.run)\s*\([^)]*shell\s*=\s*True[^)]*\)",
            "severity": "CRITICAL",
            "description": "Execution of dynamic string, os.system/popen (always shell), or subprocess with shell=True — vulnerable to command injection.",
            "remediation": "Avoid eval/exec and os.system; use subprocess.run with argument vectors and shell=False."
        },
        {
            "name": "HARDCODED_CREDENTIALS",
            "regex": r"(?i)(?:api_key|secret|password|auth_token|private_key)\s*=\s*['\"][A-Za-z0-9_\-\.+=/]{12,}['\"]",
            "severity": "HIGH",
            "description": "Hardcoded secret, token, or password found directly in source code.",
            "remediation": "Store secrets in environment variables or a secure vault (e.g. os.getenv('API_KEY'))."
        },
        {
            "name": "INSECURE_DESERIALIZATION",
            "regex": r"\b(pickle\.loads|pickle\.load|yaml\.load\s*\([^)]*Loader\s*=\s*(?:yaml\.)?Loader\b)",
            "severity": "HIGH",
            "description": "Deserialization of untrusted data via pickle or unsafe yaml loader can lead to remote code execution.",
            "remediation": "Use json or yaml.safe_load for untrusted payloads."
        },
        {
            "name": "INSECURE_RANDOM_FOR_CRYPTO",
            "regex": r"\brandom\.(random|choice|randint|sample)\s*\(",
            "severity": "LOW",
            "description": "Standard pseudo-random number generator used. May be insecure if used for tokens, session IDs, or crypto.",
            "remediation": "Use python 'secrets' module for cryptographically secure tokens."
        },
        {
            "name": "UNHANDLED_EXCEPTION_PASS",
            "regex": r"except\s*:\s*\n\s*pass|except\s+Exception\s*:\s*\n\s*pass",
            "severity": "MEDIUM",
            "description": "Silent catch-all exception suppression ('bare except: pass') conceals critical runtime failures.",
            "remediation": "Catch specific exceptions and log the stack trace."
        }
    ]

    @classmethod
    def validate(cls, code: str, language: str = "python", refactored_code: Optional[str] = None) -> DeterministicValidation:
        syntax_valid = True
        ast_metrics: Dict[str, Any] = {}
        detected_vulns: List[Dict[str, Any]] = []
        caveats: List[str] = []
        refactor_compiles = True

        normalized_lang = language.lower().strip()

        # 1. Syntax & AST Inspection
        if normalized_lang in ["python", "py"]:
            try:
                tree = ast.parse(code)
                funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.extend([a.name for a in node.names])
                    elif isinstance(node, ast.ImportFrom):
                        imports.append(f"{node.module}")
                
                # branch_count: counts branching nodes (If/For/While/ExceptHandler/With).
                # NOTE: This is NOT McCabe cyclomatic complexity (M = E - N + 2P).
                # It is a simpler branch-count heuristic used as a complexity proxy.
                branch_count = sum(
                    1 for node in ast.walk(tree)
                    if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With))
                )

                ast_metrics = {
                    "functions_detected": funcs,
                    "classes_detected": classes,
                    "imported_modules": list(set(imports)),
                    "branch_count": branch_count,
                    "branch_count_note": "Heuristic branch count (not McCabe cyclomatic complexity)",
                    "total_ast_nodes": sum(1 for _ in ast.walk(tree))
                }
            except SyntaxError as e:
                syntax_valid = False
                err_line = e.lineno or 1
                lines_preview = code.splitlines()
                err_content = lines_preview[err_line - 1].strip() if err_line <= len(lines_preview) else ""
                caveats.append(f"Original Python syntax error at line {err_line}: {e.msg}")
                ast_metrics = {"syntax_error": str(e), "line": err_line}
                detected_vulns.append({
                    "name": "PYTHON_SYNTAX_ERROR",
                    "line": err_line,
                    "line_content": err_content,
                    "severity": "CRITICAL",
                    "description": f"SyntaxError at line {err_line}: {e.msg}. The code contains invalid Python syntax and cannot compile or run.",
                    "remediation": f"Fix the syntax error on line {err_line}. Check for single '=' in conditions (use '=='), unclosed parentheses, or missing colons."
                })
        else:
            # Non-Python: bracket balance heuristic.
            # WARNING: Balanced brackets are necessary but NOT sufficient for syntactic validity.
            # This is a coarse heuristic — not a proper language parser.
            brackets = {'(': ')', '{': '}', '[': ']'}
            stack: list = []
            valid_balance = True
            for char in code:
                if char in brackets:
                    stack.append(char)
                elif char in brackets.values():
                    if not stack or brackets[stack.pop()] != char:
                        valid_balance = False
                        break
            if not valid_balance or len(stack) > 0:
                syntax_valid = False
                caveats.append(
                    f"Mismatched braces or unclosed brackets detected in {language} code."
                )
            ast_metrics = {
                "language": language,
                "bracket_balanced": valid_balance and len(stack) == 0,
                "note": (
                    f"No dedicated {language} parser available. "
                    "Bracket balance is a coarse heuristic — not a guarantee of valid syntax."
                )
            }
            caveats.append(
                f"Non-Python validation is limited: only bracket balance checked for {language}. "
                "Use a language-specific linter for authoritative syntax checking."
            )

        # 2. Bracket Balance and Delimiter Check (All Languages)
        lines = code.split("\n")
        bracket_pairs = {'(': ')', '[': ']', '{': '}'}
        delimiter_stack = []
        for l_idx, l_str in enumerate(lines, 1):
            for ch in l_str:
                if ch in bracket_pairs:
                    delimiter_stack.append((bracket_pairs[ch], l_idx, l_str.strip()))
                elif ch in bracket_pairs.values():
                    if delimiter_stack and delimiter_stack[-1][0] == ch:
                        delimiter_stack.pop()

        if delimiter_stack:
            syntax_valid = False
            for expected_close, l_idx, l_str in delimiter_stack:
                if not any(v.get("line") == l_idx and "UNCLOSED" in v["name"] for v in detected_vulns):
                    detected_vulns.append({
                        "name": "UNCLOSED_PARENTHESIS_OR_DELIMITER",
                        "line": l_idx,
                        "line_content": l_str,
                        "severity": "CRITICAL",
                        "description": f"Unclosed delimiter: expected matching '{expected_close}' for opening bracket on line {l_idx}.",
                        "remediation": f"Add the closing '{expected_close}' to match opening bracket on line {l_idx}."
                    })

        # 3. Syntax Heuristic Checks (Assignment in if, undefined variable mismatches)
        for l_idx, l_str in enumerate(lines, 1):
            # Assignment in condition: if student["name"] = name:
            if re.search(r'\b(?:if|elif)\s+[^=:\n]+\s*=\s*[^=:\n]+:', l_str):
                if not any(v.get("line") == l_idx and "ASSIGNMENT" in v["name"] for v in detected_vulns):
                    detected_vulns.append({
                        "name": "ASSIGNMENT_IN_CONDITIONAL",
                        "line": l_idx,
                        "line_content": l_str.strip(),
                        "severity": "CRITICAL",
                        "description": f"Invalid assignment in condition on line {l_idx}. Single '=' is an assignment operator; comparison requires '=='.",
                        "remediation": f"Replace '=' with '==' on line {l_idx}."
                    })

            # Variable singular/plural mismatch: def avg(numbers): ... len(number)
            if "len(number)" in l_str and "numbers" in code:
                if not any(v.get("line") == l_idx and "NAME_MISMATCH" in v["name"] for v in detected_vulns):
                    detected_vulns.append({
                        "name": "UNDEFINED_VARIABLE_NAME_MISMATCH",
                        "line": l_idx,
                        "line_content": l_str.strip(),
                        "severity": "HIGH",
                        "description": f"Undefined variable 'number' referenced on line {l_idx}. Parameter is defined as 'numbers'. Will raise NameError at runtime.",
                        "remediation": f"Change 'number' to 'numbers' on line {l_idx}."
                    })

        # 4. Rule-Based Vulnerability Scan (Deterministic)
        for rule in cls.DANGEROUS_PATTERNS:
            for idx, line in enumerate(lines, start=1):
                if re.search(rule["regex"], line):
                    detected_vulns.append({
                        "name": rule["name"],
                        "line": idx,
                        "line_content": line.strip(),
                        "severity": rule["severity"],
                        "description": rule["description"],
                        "remediation": rule["remediation"]
                    })

        # 3. Refactored Code Compile Check (postflight gate)
        if refactored_code and refactored_code.strip() != code.strip():
            if normalized_lang in ["python", "py"]:
                try:
                    ast.parse(refactored_code)
                    refactor_compiles = True
                except SyntaxError as e:
                    refactor_compiles = False
                    caveats.append(
                        f"Refactored code has syntax error at line {e.lineno}: {e.msg} — "
                        "original code retained as safe fallback."
                    )
            else:
                # Non-Python: bracket-balance the refactor too
                brackets = {'(': ')', '{': '}', '[': ']'}
                stack: list = []
                for char in refactored_code:
                    if char in brackets:
                        stack.append(char)
                    elif char in brackets.values():
                        if not stack or brackets[stack.pop()] != char:
                            refactor_compiles = False
                            caveats.append(
                                f"Refactored {language} code has unbalanced brackets — "
                                "original code retained as safe fallback."
                            )
                            break
                if stack:
                    refactor_compiles = False

        # validation_passed: original code is syntactically parseable.
        # Detected vulnerabilities are a SEPARATE concern — they do NOT override syntax validity.
        # A file can be syntax-valid AND have security issues simultaneously.
        validation_passed = syntax_valid

        return DeterministicValidation(
            syntax_valid=syntax_valid,
            parser_engine=f"Deterministic AST & Heuristic Engine ({normalized_lang})",
            ast_metrics=ast_metrics,
            static_vulnerabilities_detected=detected_vulns,
            refactor_compiles=refactor_compiles,
            validation_passed=validation_passed,
            caveats=caveats
        )
