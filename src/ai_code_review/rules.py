from __future__ import annotations

import re
from collections.abc import Iterable

from .models import Finding, Severity


RULES = (
    "hardcoded-secret",
    "sql-injection",
    "shell-injection",
    "bare-except",
    "debug-print",
)


def _finding(severity: Severity, category: str, title: str, description: str,
             recommendation: str, line: int, rule_id: str) -> Finding:
    return Finding(
        severity=severity,
        category=category,
        title=title,
        description=description,
        recommendation=recommendation,
        line=line,
        rule_id=rule_id,
    )


def run_static_rules(code: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = code.splitlines()

    secret = re.compile(r"(?i)\b(password|passwd|api[_-]?key|secret|token)\b\s*=\s*['\"][^'\"]{4,}['\"]")
    sql = re.compile(r"(?i)(execute|executemany)\s*\(\s*[f]?['\"].*\{.*\}")
    shell = re.compile(r"(?i)(os\.system|subprocess\.(run|call|Popen))\s*\(.*(input\(|request\.|argv)")

    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if secret.search(line) and not stripped.startswith(("#", "//")):
            findings.append(_finding(
                Severity.CRITICAL, "security", "Hard-coded credential detected",
                "A credential-like value is assigned directly in source code.",
                "Load secrets from environment variables or a dedicated secret manager.",
                number, "hardcoded-secret",
            ))
        if sql.search(line):
            findings.append(_finding(
                Severity.HIGH, "security", "Potential SQL injection",
                "A formatted string appears to reach a database execution call.",
                "Use parameterized queries and pass user-controlled values as parameters.",
                number, "sql-injection",
            ))
        if shell.search(line):
            findings.append(_finding(
                Severity.HIGH, "security", "Potential command injection",
                "Untrusted input appears to be passed to a shell/process execution API.",
                "Avoid shell execution where possible and validate inputs before using a process API.",
                number, "shell-injection",
            ))
        if stripped == "except:":
            findings.append(_finding(
                Severity.MEDIUM, "quality", "Bare exception handling",
                "A bare except catches every exception and can hide unexpected failures.",
                "Catch the expected exception types and preserve useful error context.",
                number, "bare-except",
            ))
        if re.search(r"\bprint\s*\(", stripped) and not stripped.startswith("#"):
            findings.append(_finding(
                Severity.LOW, "quality", "Debug print in application code",
                "Direct console output may leak implementation details or create noisy logs.",
                "Use structured logging and remove temporary debugging statements.",
                number, "debug-print",
            ))
    return findings


def findings_summary(findings: Iterable[Finding]) -> str:
    findings = list(findings)
    if not findings:
        return "No issues found."
    counts = {severity.value: 0 for severity in Severity}
    for finding in findings:
        counts[finding.severity.value] += 1
    parts = [f"{len(findings)} finding(s)"]
    for severity in (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW):
        if counts[severity.value]:
            parts.append(f"{counts[severity.value]} {severity.value}")
    return " | ".join(parts)
