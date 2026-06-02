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

Use it as a CI gate:

```bash
skill-router-audit path/to/skills \
  --format markdown \
  --output skill-router-report.md \
  --policy-output AGENTS.skill-routing.md \
  --fail-on medium \
  --max-overlaps 0
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

## Reporting Conflicts

If two skills are hard for an agent to distinguish, open a "Skill routing
conflict" issue and include:

- The two skill names or paths.
- The shortest user request that routes poorly.
- Which skill should have been selected.
- Any relevant audit output or current descriptions.

That feedback is especially useful because routing quality is easiest to improve
when ambiguity is captured as a small, repeatable example.

## Recommended workflow

1. Run the audit on the current skill catalog.
2. Fix high priority description and negative-trigger issues.
3. Add the generated routing policy to `AGENTS.md`.
4. Re-run the audit before adding new skills.
5. Track overlap scores in CI so new skills do not blur existing boundaries.

## CI Gating

`--fail-on` turns findings into a lint-style gate:

- `--fail-on high` fails on missing descriptions and duplicate skill names.
- `--fail-on medium` also fails on weak descriptions and missing negative
  triggers.
- `--fail-on low` is reserved for future low-severity checks.
- `--fail-on none` keeps report-only behavior.

`--max-overlaps` limits likely routing conflicts. For mature catalogs, start
with the current overlap count as a baseline, then lower it as descriptions
improve.

`--policy-output` writes only the generated routing policy so maintainers can
commit or review it separately from the full audit report.

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
