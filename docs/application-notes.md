# Application Notes

Use this document as a truthful starting point if applying for open-source
support programs. Do not invent usage numbers or claim maintainer roles you do
not have.

## Short project description

Skill Router Auditor helps maintainers of large Agent skill catalogs improve
skill routing quality. It scans `SKILL.md` files, flags ambiguous or weak
descriptions, groups skills into a routing tree, and generates an `AGENTS.md`
policy that reduces misfires when many skills are available.

## Why the repository may qualify

- It targets a real maintenance workflow: reviewing and improving agent skill
  catalogs.
- It helps reduce review load by surfacing routing conflicts automatically.
- It can be used in pull request review before new skills are merged.
- It supports Codex and other coding agents that rely on skill descriptions,
  tool routing, and repository-level instructions.

## Evidence to collect over time

- GitHub stars and forks.
- Issues or pull requests opened by external users.
- Number of skill catalogs audited.
- CI runs using the tool.
- Examples where the report prevented a routing conflict.
- Mentions from maintainers or agent framework projects.

## Honest application answer draft

I am the primary maintainer of Skill Router Auditor, a CLI that helps open-source
maintainers audit large Agent skill catalogs. The project scans `SKILL.md`
metadata, detects weak descriptions and overlapping skills, builds a skill tree,
and generates routing guidance for `AGENTS.md`. I would use Codex to review pull
requests, add CI integrations, improve routing heuristics, and maintain examples
for real OSS agent workflows.

