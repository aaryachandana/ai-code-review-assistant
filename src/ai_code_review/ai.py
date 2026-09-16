from __future__ import annotations

import json
import os

from .models import Finding, ReviewResult, Severity

SYSTEM_PROMPT = """You are a senior software engineer performing a careful code review.
Identify concrete bugs, security risks, correctness problems, performance problems,
and maintainability issues. Do not invent issues. Prefer actionable findings with
specific line numbers when available. Return ONLY valid JSON matching the requested schema."""

SCHEMA = {
    "type": "object",
    "properties": {
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {"type": "string", "enum": ["critical", "high", "medium", "low", "info"]},
                    "category": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "recommendation": {"type": "string"},
                    "line": {"type": ["integer", "null"]},
                    "rule_id": {"type": ["string", "null"]},
                },
                "required": ["severity", "category", "title", "description", "recommendation", "line", "rule_id"],
                "additionalProperties": False,
            },
        },
        "summary": {"type": "string"},
    },
    "required": ["findings", "summary"],
    "additionalProperties": False,
}


def ai_review(code: str, filename: str = "source.txt", model: str | None = None) -> ReviewResult:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    from openai import OpenAI

    model = model or os.getenv("AI_REVIEW_MODEL", "gpt-5.6-luna")
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=f"Review this file: {filename}\n\n```\n{code}\n```",
        text={"format": {"type": "json_schema", "name": "code_review", "strict": True, "schema": SCHEMA}},
    )
    data = json.loads(response.output_text)
    return ReviewResult(model=model, **data)
