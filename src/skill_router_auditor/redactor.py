from __future__ import annotations

import re
from pathlib import Path


SENSITIVE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "<EMAIL>"),
    (re.compile(r"\b(?:gh[pousr]|github_pat)_[A-Za-z0-9_]{20,}\b"), "<TOKEN>"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "<TOKEN>"),
    (re.compile(r"\bxox[pbar]-[A-Za-z0-9-]{20,}\b"), "<TOKEN>"),
    (re.compile(r"\bou_[A-Za-z0-9_-]{16,}\b"), "<ID>"),
    (re.compile(r"\b(app_secret|client_secret|access_token|refresh_token|api_key)=([^&\s]+)", re.I), r"\1=<REDACTED>"),
    (re.compile(r"([?&](?:token|key|secret|signature|sig|access_token)=)([^&\s]+)", re.I), r"\1<REDACTED>"),
)


def redact_text(text: str, roots: list[Path] | None = None) -> str:
    """Redact local paths and common secret-like values from generated reports."""

    redacted = text
    replacements = _path_replacements(roots or [])
    for needle, replacement in replacements:
        redacted = redacted.replace(needle, replacement)
    for pattern, replacement in SENSITIVE_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def _path_replacements(roots: list[Path]) -> list[tuple[str, str]]:
    replacements: list[tuple[str, str]] = []
    home = Path.home()
    for raw, label in [(home, "<HOME>"), *[(root, "<SKILL_ROOT>") for root in roots]]:
        try:
            path = raw.expanduser().resolve()
        except OSError:
            path = raw.expanduser()
        forms = {
            str(path),
            str(path).replace("\\", "/"),
            str(path).replace("\\", "\\\\"),
        }
        for form in forms:
            replacements.append((form, label))
    return sorted(replacements, key=lambda item: len(item[0]), reverse=True)
