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
    return Finding(severity=severity, category=category, title=title,
                   description=description, recommendation=recommendation,
                   line=line, rule_id=rule_id)


def run_static_rules(code: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = code.splitlines()
    secret = re.compile(r"(?i)\b(password|passwd|api[_-]?key|secret|token)\b\s*=\s*['\"][^'\"]{4,}['\"]")
    sql_inline = re.compile(r"(?i)(execute|executemany)\s*\(\s*[f]?['\"].*\{.*\}")
    sql_assignment = re.compile(r"(?i)^\s*(\w+)\s*=\s*f?['\"].*(select|insert|update|delete).*[\{\}]")
    process_call = re.compile(r"(?i)(os\.system|subprocess\.(run|call|Popen))\s*\(")
    process_input = re.compile(r"(?i)(input\(|request\.|argv|command)")
    sql_vars: dict[str, int] = {}

    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if secret.search(line) and not stripped.startswith(("#", "//")):
            findings.append(_finding(Severity.CRITICAL, "security", "Hard-coded credential detected",
                "A credential-like value is assigned directly in source code.",
                "Load secrets from environment variables or a dedicated secret manager.", number, "hardcoded-secret"))

        assignment = sql_assignment.search(line)
        if assignment:
            sql_vars[assignment.group(1)] = number
        if sql_inline.search(line) or re.search(r"(?i)(execute|executemany)\s*\(\s*(\w+)", line) and any(
            var in line for var in sql_vars
        ):
            findings.append(_finding(Severity.HIGH, "security", "Potential SQL injection",
                "A formatted SQL statement appears to reach a database execution call.",
                "Use parameterized queries and pass user-controlled values as parameters.", number, "sql-injection"))

        if process_call.search(line):
            suspicious = process_input.search(line) or "os.system" in line.lower()
            if suspicious:
                findings.append(_finding(Severity.HIGH, "security", "Potential command injection",
                    "Input or a dynamically constructed command appears to reach a process execution API.",
                    "Avoid shell execution where possible and validate or allowlist arguments before execution.", number, "shell-injection"))

        if stripped == "except:":
            findings.append(_finding(Severity.MEDIUM, "quality", "Bare exception handling",
                "A bare except catches every exception and can hide unexpected failures.",
                "Catch the expected exception types and preserve useful error context.", number, "bare-except"))

        if re.search(r"\bprint\s*\(", stripped) and not stripped.startswith("#"):
            findings.append(_finding(Severity.LOW, "quality", "Debug print in application code",
                "Direct console output may leak implementation details or create noisy logs.",
                "Use structured logging and remove temporary debugging statements.", number, "debug-print"))
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
