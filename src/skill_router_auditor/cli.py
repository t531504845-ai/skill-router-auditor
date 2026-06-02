from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analyzer import analyze
from .parser import load_skills
from .report import render_report


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
    return 0

