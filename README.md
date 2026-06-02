# Skill Router Auditor

Skill Router Auditor is a small CLI for maintainers who manage many Agent
skills. It scans `SKILL.md` files, finds weak descriptions and likely routing
conflicts, groups skills into a category tree, and emits an `AGENTS.md`-ready
routing policy.

The goal is simple: when a skill catalog grows from a dozen entries to hundreds,
routing becomes a retrieval problem. This project gives maintainers a repeatable
way to inspect that routing layer before users hit flaky skill selection.

## What it checks

- Missing or weak `name` and `description` frontmatter.
- Descriptions that are too short, too generic, or lack trigger context.
- Skills with high lexical overlap that may compete for the same user intent.
- Missing "do not use" or negative-trigger guidance.
- Category placement for a first-pass skill tree.
- A final routing policy suitable for `AGENTS.md` or a system prompt.

## Install

From a checkout:

```bash
python -m pip install -e .
```

No runtime dependencies are required.

## Quick Start

Analyze the included example skills:

```bash
skill-router-audit examples/sample-skills --format markdown
```

Write a JSON report:

```bash
skill-router-audit path/to/skills --format json --output report.json
```

Generate only the routing policy:

```bash
skill-router-audit path/to/skills --format policy
```

## Example Output

```text
Skill Router Audit

Catalog
- Skills found: 3
- Categories: browser, data, developer-tools

High Priority Findings
- browser-control: description has no negative-trigger guidance.
- github-automation and browser-control overlap on repository/browser terms.

Skill Tree
- browser
  - browser-control
- data
  - spreadsheet-cleanup
- developer-tools
  - github-automation
```

## Why this matters

Large skill catalogs fail in quiet ways:

- The model selects a broad skill instead of the specialized one.
- Similar skills compete because their descriptions use the same words.
- A skill fires when it should not, because the description never says what to
  exclude.
- The system loads too many candidates, wasting context and making the decision
  noisier.

Skill Router Auditor treats this as an engineering problem. It helps maintainers
make the catalog easier to search, route, and review.

## Recommended workflow

1. Run the audit on the current skill catalog.
2. Fix high priority description and negative-trigger issues.
3. Add the generated routing policy to `AGENTS.md`.
4. Re-run the audit before adding new skills.
5. Track overlap scores in CI so new skills do not blur existing boundaries.

## Roadmap

- Configurable category taxonomy.
- CI output with pass/fail thresholds.
- Embedding-based similarity as an optional plugin.
- Pull request comments for skill catalog changes.
- Baseline tracking for routing quality over time.

## OpenAI Codex for Open Source

This repository is designed to be useful for real open-source maintenance work:
reviewing skills, triaging routing failures, and improving agent workflows. It
does not guarantee acceptance into any external program. If you apply to a grant
or credits program, describe the project's real usage, maintenance role, and
impact honestly.

## License

MIT

