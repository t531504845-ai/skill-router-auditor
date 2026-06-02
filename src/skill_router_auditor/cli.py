from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analyzer import analyze
from .models import AuditReport
from .parser import load_skills
from .report import render_report

SEVERITY_RANK = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skill-router-audit",
        description="Audit Agent SKILL.md catalogs for routing quality.",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Directory containing SKILL.md files, or a single SKILL.md file.",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json", "policy"),
        default="markdown",
        help="Report format.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write report to a file instead of stdout.",
    )
    parser.add_argument(
        "--overlap-threshold",
        type=float,
        default=0.34,
        help="Jaccard threshold for reporting likely routing conflicts.",
    )
    parser.add_argument(
        "--policy-output",
        type=Path,
        help="Write the generated routing policy to a separate file.",
    )
    parser.add_argument(
        "--fail-on",
        choices=("none", "high", "medium", "low"),
        default="none",
        help="Exit with code 2 when findings at or above this severity exist.",
    )
    parser.add_argument(
        "--max-overlaps",
        type=int,
        help="Exit with code 2 when potential routing conflicts exceed this count.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.path.exists():
        parser.error(f"path does not exist: {args.path}")

    skills = load_skills(args.path)
    if not skills:
        parser.error("no SKILL.md files found")

    report = analyze(skills, overlap_threshold=args.overlap_threshold)
    output = render_report(report, args.format)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    if args.policy_output:
        args.policy_output.write_text(report.routing_policy + "\n", encoding="utf-8")

    failures = evaluate_gates(report, args.fail_on, args.max_overlaps)
    if failures:
        for failure in failures:
            print(f"audit failed: {failure}", file=sys.stderr)
        return 2
    return 0


def evaluate_gates(
    report: AuditReport,
    fail_on: str = "none",
    max_overlaps: int | None = None,
) -> list[str]:
    failures: list[str] = []
    threshold = SEVERITY_RANK[fail_on]
    if threshold:
        matching = [
            finding
            for finding in report.findings
            if SEVERITY_RANK[finding.severity] >= threshold
        ]
        if matching:
            failures.append(
                f"{len(matching)} finding(s) at or above severity '{fail_on}'"
            )
    if max_overlaps is not None and len(report.overlaps) > max_overlaps:
        failures.append(
            f"{len(report.overlaps)} overlap(s), allowed maximum is {max_overlaps}"
        )
    return failures
