from __future__ import annotations

import json

from .models import AuditReport


def render_report(report: AuditReport, fmt: str) -> str:
    if fmt == "json":
        return render_json(report)
    if fmt == "policy":
        return report.routing_policy + "\n"
    return render_markdown(report)


def render_json(report: AuditReport) -> str:
    payload = {
        "skills": [
            {
                "name": skill.name,
                "description": skill.description,
                "path": str(skill.path),
            }
            for skill in report.skills
        ],
        "categories": report.categories,
        "findings": [
            {
                "severity": finding.severity,
                "skill": finding.skill,
                "message": finding.message,
                "suggestion": finding.suggestion,
            }
            for finding in report.findings
        ],
        "overlaps": [
            {
                "left": overlap.left,
                "right": overlap.right,
                "score": overlap.score,
                "shared_terms": list(overlap.shared_terms),
            }
            for overlap in report.overlaps
        ],
        "routing_policy": report.routing_policy,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def render_markdown(report: AuditReport) -> str:
    lines = [
        "# Skill Router Audit",
        "",
        "## Catalog",
        "",
        f"- Skills found: {len(report.skills)}",
        f"- Categories: {', '.join(sorted(report.categories)) or 'none'}",
        "",
        "## Findings",
        "",
    ]
    if report.findings:
        for finding in sorted(report.findings, key=_finding_sort_key):
            lines.append(f"- [{finding.severity}] {finding.skill}: {finding.message}")
            lines.append(f"  Suggestion: {finding.suggestion}")
    else:
        lines.append("- No routing quality findings.")

    lines.extend(["", "## Potential Routing Conflicts", ""])
    if report.overlaps:
        for overlap in report.overlaps:
            terms = ", ".join(overlap.shared_terms)
            lines.append(
                f"- {overlap.left} <-> {overlap.right}: score {overlap.score:.3f}"
            )
            if terms:
                lines.append(f"  Shared terms: {terms}")
    else:
        lines.append("- No high-overlap skill pairs found.")

    lines.extend(["", "## Skill Tree", ""])
    for category in sorted(report.categories):
        lines.append(f"- {category}")
        for skill in sorted(report.categories[category]):
            lines.append(f"  - {skill}")

    lines.extend(["", "## Generated Routing Policy", "", report.routing_policy, ""])
    return "\n".join(lines)


def _finding_sort_key(finding: object) -> tuple[int, str]:
    severity = getattr(finding, "severity", "")
    skill = getattr(finding, "skill", "")
    order = {"high": 0, "medium": 1, "low": 2}
    return (order.get(severity, 9), skill)

