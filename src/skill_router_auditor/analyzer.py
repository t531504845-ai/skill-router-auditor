from __future__ import annotations

import re
from collections import defaultdict

from .models import AuditReport, Finding, Overlap, Skill

GENERIC_TERMS = {
    "automate",
    "automation",
    "help",
    "use",
    "tool",
    "tools",
    "task",
    "tasks",
    "workflow",
    "workflows",
    "agent",
    "ai",
}

NEGATIVE_HINTS = (
    "do not use",
    "don't use",
    "not use",
    "avoid",
    "unless",
    "instead",
    "only when",
    "not for",
)

CATEGORY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("browser", ("browser", "chrome", "edge", "webpage", "website", "click", "tab", "localhost")),
    ("developer-tools", ("git", "github", "repository", "pull request", "issue", "ci", "code review")),
    (
        "social-data",
        (
            "xquik",
            "x-twitter-scraper",
            "twitter",
            "tweet",
            "timeline",
            "follower",
            "social-media",
            "social media",
            "x data",
        ),
    ),
    ("data", ("spreadsheet", "excel", "csv", "table", "database", "sql", "analytics")),
    ("documents", ("document", "pdf", "markdown", "docx", "presentation", "slides")),
    ("media", ("image", "video", "audio", "design", "canvas", "thumbnail")),
    ("platform-automation", ("api", "crm", "slack", "feishu", "notion", "jira", "sap")),
    ("operations", ("deploy", "docker", "server", "config", "monitor", "logs")),
)


def analyze(skills: tuple[Skill, ...], overlap_threshold: float = 0.34) -> AuditReport:
    findings = _find_quality_issues(skills)
    overlaps = _find_overlaps(skills, threshold=overlap_threshold)
    categories = _categorize(skills)
    routing_policy = build_routing_policy(categories, skills)
    return AuditReport(
        skills=skills,
        categories=categories,
        findings=tuple(findings),
        overlaps=tuple(overlaps),
        routing_policy=routing_policy,
    )


def build_routing_policy(categories: dict[str, tuple[str, ...]], skills: tuple[Skill, ...]) -> str:
    descriptions = {skill.name: skill.description for skill in skills}
    lines = [
        "# Skill Routing Policy",
        "",
        "When a user request may require a skill, route in two stages:",
        "",
        "1. Select the closest category from the skill tree.",
        "2. Recall at most five candidate skills from that category.",
        "3. Exclude any skill whose negative conditions apply.",
        "4. Prefer the most specific skill over broad automation skills.",
        "5. If required inputs or credentials are missing, ask a concise question.",
        "",
        "## Skill Tree",
        "",
    ]
    for category in sorted(categories):
        lines.append(f"- {category}")
        for name in sorted(categories[category]):
            description = descriptions.get(name, "")
            suffix = f": {description}" if description else ""
            lines.append(f"  - {name}{suffix}")
    return "\n".join(lines).strip()


def _find_quality_issues(skills: tuple[Skill, ...]) -> list[Finding]:
    findings: list[Finding] = []
    seen_names: dict[str, int] = defaultdict(int)
    for skill in skills:
        seen_names[skill.name] += 1
        description_words = tokenize(skill.description)

        if not skill.name:
            findings.append(
                Finding(
                    severity="high",
                    skill=str(skill.path),
                    message="Missing skill name.",
                    suggestion="Add a frontmatter name that is short, stable, and specific.",
                )
            )
        if not skill.description:
            findings.append(
                Finding(
                    severity="high",
                    skill=skill.name or str(skill.path),
                    message="Missing skill description.",
                    suggestion="Add a description with trigger scenarios, required inputs, and exclusions.",
                )
            )
            continue
        if len(description_words) < 8:
            findings.append(
                Finding(
                    severity="medium",
                    skill=skill.name,
                    message="Description is very short.",
                    suggestion="Mention the task type, typical user wording, and when not to use it.",
                )
            )
        if _generic_ratio(description_words) > 0.45:
            findings.append(
                Finding(
                    severity="medium",
                    skill=skill.name,
                    message="Description uses mostly generic terms.",
                    suggestion="Replace broad words with concrete triggers and domain nouns.",
                )
            )
        if not _has_negative_guidance(skill.description, skill.body):
            findings.append(
                Finding(
                    severity="medium",
                    skill=skill.name,
                    message="No negative-trigger guidance found.",
                    suggestion="Add a short 'Do not use when...' rule to reduce false positives.",
                )
            )

    for name, count in seen_names.items():
        if count > 1:
            findings.append(
                Finding(
                    severity="high",
                    skill=name,
                    message=f"Duplicate skill name appears {count} times.",
                    suggestion="Make names unique so routing and reports are stable.",
                )
            )
    return findings


def _find_overlaps(skills: tuple[Skill, ...], threshold: float) -> list[Overlap]:
    overlaps: list[Overlap] = []
    token_sets = {
        skill.path: tokenize(f"{skill.name} {skill.description} {skill.body[:1000]}")
        for skill in skills
    }

    for index, left in enumerate(skills):
        for right in skills[index + 1 :]:
            left_terms = token_sets[left.path]
            right_terms = token_sets[right.path]
            if not left_terms or not right_terms:
                continue
            shared = left_terms & right_terms
            union = left_terms | right_terms
            score = len(shared) / len(union)
            if score >= threshold:
                overlaps.append(
                    Overlap(
                        left=left.name,
                        right=right.name,
                        score=round(score, 3),
                        shared_terms=tuple(sorted(shared)[:12]),
                    )
                )
    return sorted(overlaps, key=lambda item: item.score, reverse=True)


def _categorize(skills: tuple[Skill, ...]) -> dict[str, tuple[str, ...]]:
    categories: dict[str, list[str]] = defaultdict(list)
    for skill in skills:
        haystack = f"{skill.name} {skill.description} {skill.body[:1200]}".lower()
        category = "general"
        best_hits = 0
        for candidate, terms in CATEGORY_RULES:
            hits = sum(1 for term in terms if term in haystack)
            if hits > best_hits:
                category = candidate
                best_hits = hits
        categories[category].append(skill.name)
    return {key: tuple(values) for key, values in categories.items()}


def _generic_ratio(words: set[str]) -> float:
    if not words:
        return 1.0
    return len(words & GENERIC_TERMS) / len(words)


def _has_negative_guidance(description: str, body: str) -> bool:
    combined = f"{description}\n{body}".lower()
    return any(hint in combined for hint in NEGATIVE_HINTS)


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())
    return {word for word in words if word not in GENERIC_TERMS}
