from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Finding(BaseModel):
    severity: Severity
    category: str
    title: str
    description: str
    recommendation: str
    line: int | None = None
    rule_id: str | None = None


class ReviewResult(BaseModel):
    findings: list[Finding] = Field(default_factory=list)
    summary: str = "No issues found."
    model: str | None = None


class ReviewRequest(BaseModel):
    filename: str = "source.txt"
    code: str
    use_ai: bool = True
