from __future__ import annotations

from pathlib import Path

from .models import Skill


def discover_skill_files(root: Path) -> list[Path]:
    """Find SKILL.md files under a root path."""

    if root.is_file():
        return [root] if root.name.lower() == "skill.md" else []
    return sorted(path for path in root.rglob("SKILL.md") if path.is_file())


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse a small YAML-like frontmatter block without external dependencies."""

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    metadata: dict[str, str] = {}
    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = _clean_scalar(value.strip())

    if end_index is None:
        return {}, text

    body = "\n".join(lines[end_index + 1 :]).strip()
    return metadata, body


def parse_skill_file(path: Path) -> Skill:
    text = path.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(text)
    fallback_name = path.parent.name if path.parent.name else path.stem
    name = metadata.get("name") or fallback_name
    description = metadata.get("description") or ""
    return Skill(
        name=name.strip(),
        description=description.strip(),
        path=path,
        body=body,
        metadata=metadata,
    )


def load_skills(root: Path) -> tuple[Skill, ...]:
    return tuple(parse_skill_file(path) for path in discover_skill_files(root))


def _clean_scalar(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value

