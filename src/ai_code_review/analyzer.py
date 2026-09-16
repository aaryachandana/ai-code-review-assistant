from __future__ import annotations

from .ai import ai_review
from .models import ReviewResult
from .rules import findings_summary, run_static_rules


def review_code(code: str, filename: str = "source.txt", use_ai: bool = True) -> ReviewResult:
    static_findings = run_static_rules(code)
    if use_ai:
        try:
            result = ai_review(code, filename)
            # Static rules are deterministic and useful even when the model misses a signal.
            existing = {(f.rule_id, f.line, f.title) for f in result.findings}
            for finding in static_findings:
                key = (finding.rule_id, finding.line, finding.title)
                if key not in existing:
                    result.findings.append(finding)
            result.summary = findings_summary(result.findings) if result.findings else result.summary
            return result
        except RuntimeError:
            pass
    return ReviewResult(findings=static_findings, summary=findings_summary(static_findings))


def review_diff(diff: str, use_ai: bool = True) -> ReviewResult:
    # Keep added lines only for focused reviews while preserving approximate line numbers.
    chunks: list[str] = []
    current_line = 1
    for raw in diff.splitlines():
        if raw.startswith("@@"):
            import re
            match = re.search(r"\+(\d+)", raw)
            if match:
                current_line = int(match.group(1))
            continue
        if raw.startswith("+++") or raw.startswith("---"):
            continue
        if raw.startswith("+"):
            chunks.append(f"{current_line}: {raw[1:]}")
            current_line += 1
        elif raw.startswith(" "):
            current_line += 1
    return review_code("\n".join(chunks), "pull-request.diff", use_ai=use_ai)
