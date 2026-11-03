import asyncio
import time
import json
import re
from typing import Optional, Dict, Any, List
import httpx
from google import genai
from google.genai import types

from .base import BaseModelAdapter
from ..models.schemas import CandidateOutput, ReviewFinding
from ..config import config

class GeminiAdapter(BaseModelAdapter):
    """
    Adapter for Google Gemini API models (e.g. gemini-2.5-flash, gemini-1.5-flash, gemini-2.5-pro).
    Translates task requests to Gemini Generative Model calls and normalizes responses
    into the NCIO common schema.

    FIX (C1): The Gemini SDK's generate_content() is synchronous. Placing it directly inside
    an `async def` blocks the event loop and prevents asyncio.gather() from running agents
    concurrently. We wrap it in asyncio.to_thread() so the blocking call runs in a thread
    pool while the event loop stays free for other work.
    """

    def __init__(self, default_model: Optional[str] = None):
        self.default_model = default_model or config.DEFAULT_MODEL

    async def evaluate_code(
        self,
        code: str,
        language: str,
        persona: str,
        system_instruction: str,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> CandidateOutput:
        active_key = api_key or config.GEMINI_API_KEY
        active_model = model_name or self.default_model

        if not active_key:
            raise ValueError("GEMINI_API_KEY is not configured. Please supply an API key in request or environment.")

        start_time = time.time()

        prompt = f"""You are the {persona} in the Neural Consensus Intelligence Orchestrator (NCIO).
Review the following {language} code snippet.

```{language}
{code}
```

Respond STRICTLY in valid JSON matching this schema:
{{
  "overall_assessment": "Summary of your analysis from the perspective of {persona}",
  "findings": [
    {{
      "id": "ISSUE-1",
      "title": "Concise issue title",
      "category": "Security | Performance | Reliability | Style | Architecture",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
      "line_start": 1,
      "line_end": 5,
      "snippet": "relevant code line",
      "explanation": "Detailed explanation of why this is a concern",
      "suggested_fix": "How to fix this issue",
      "confidence": 0.95
    }}
  ],
  "proposed_code": "The complete rewritten, secure, and optimized {language} code snippet"
}}
Do NOT enclose your output in markdown ```json blocks if possible, just return raw JSON.
"""

        def _blocking_api_call():
            """Synchronous Gemini call — must run in a thread via asyncio.to_thread()."""
            client = genai.Client(api_key=active_key)
            return client.models.generate_content(
                model=active_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )

        try:
            # Run the blocking SDK call in a thread pool — preserves async concurrency
            response = await asyncio.to_thread(_blocking_api_call)

            latency_ms = int((time.time() - start_time) * 1000)

            # Parse JSON
            raw_text = response.text.strip()
            # Clean markdown fences if any
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?\n?", "", raw_text)
                raw_text = re.sub(r"\n?```$", "", raw_text)

            data = json.loads(raw_text)

            findings: List[ReviewFinding] = []
            for item in data.get("findings", []):
                findings.append(ReviewFinding(
                    id=str(item.get("id", f"F-{len(findings)+1}")),
                    title=str(item.get("title", "Detected Code Concern")),
                    category=str(item.get("category", "Reliability")),
                    severity=str(item.get("severity", "MEDIUM")).upper(),
                    line_start=item.get("line_start"),
                    line_end=item.get("line_end"),
                    snippet=item.get("snippet"),
                    explanation=str(item.get("explanation", "")),
                    suggested_fix=str(item.get("suggested_fix", "")),
                    confidence=float(item.get("confidence", 0.90)),
                    reported_by=[persona]
                ))

            # Token usage extraction
            usage = getattr(response, "usage_metadata", None)
            tokens = {
                "prompt_tokens": getattr(usage, "prompt_token_count", 0) if usage else 0,
                "completion_tokens": getattr(usage, "candidates_token_count", 0) if usage else 0,
                "total_tokens": getattr(usage, "total_token_count", 0) if usage else 0,
            }

            return CandidateOutput(
                agent_id=f"gemini_{persona.lower().replace(' ', '_')}",
                persona=persona,
                model_name=active_model,
                overall_assessment=data.get("overall_assessment", "Code review completed."),
                findings=findings,
                proposed_code=data.get("proposed_code", code),
                latency_ms=latency_ms,
                token_usage=tokens
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            raise RuntimeError(f"Gemini API call failed for persona '{persona}': {str(e)}")
