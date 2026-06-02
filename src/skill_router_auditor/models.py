from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Skill:
    """A parsed Agent skill document."""

    name: str
    description: str
    path: Path
    body: str = ""
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Finding:
    """A routing quality issue found during analysis."""

    severity: str
    skill: str
    message: str
    suggestion: str


@dataclass(frozen=True)
class Overlap:
    """A likely routing conflict between two skills."""

    left: str
    right: str
    score: float
    shared_terms: tuple[str, ...]


@dataclass(frozen=True)
class AuditReport:
    """Full analysis result for a skill catalog."""

    skills: tuple[Skill, ...]
    categories: dict[str, tuple[str, ...]]
    findings: tuple[Finding, ...]
    overlaps: tuple[Overlap, ...]
    routing_policy: str

