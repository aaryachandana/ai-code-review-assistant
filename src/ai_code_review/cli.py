from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzer import review_code, review_diff


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI-powered code review assistant")
    sub = parser.add_subparsers(dest="command", required=True)

    review = sub.add_parser("review", help="Review a source file")
    review.add_argument("path", type=Path)
    review.add_argument("--no-ai", action="store_true", help="Use deterministic checks only")
    review.add_argument("--format", choices=("text", "json"), default="text")

    diff = sub.add_parser("diff", help="Review a unified diff")
    diff.add_argument("path", type=Path)
    diff.add_argument("--no-ai", action="store_true")
    diff.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _print(result, output_format: str) -> None:
    if output_format == "json":
        print(result.model_dump_json(indent=2))
        return
    if not result.findings:
        print("✓ No issues found.")
        return
    for finding in result.findings:
        location = f"line {finding.line}" if finding.line else "location unavailable"
        print(f"{finding.severity.value.upper():8} {finding.category:12} {location}")
        print(f"  {finding.title}")
        print(f"  {finding.description}")
        print(f"  → {finding.recommendation}\n")
    print(f"Summary: {result.summary}")


def main() -> None:
    args = _build_parser().parse_args()
    content = args.path.read_text(encoding="utf-8")
    if args.command == "review":
        result = review_code(content, args.path.name, use_ai=not args.no_ai)
    else:
        result = review_diff(content, use_ai=not args.no_ai)
    _print(result, args.format)


if __name__ == "__main__":
    main()
