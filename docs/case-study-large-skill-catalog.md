# Case Study: Auditing a Large Skill Catalog

This case study summarizes a redacted audit of a local Agent skill catalog. The
raw report was not committed because it was large and environment-specific. The
published data below keeps only aggregate counts and representative anonymized
findings.

Command used:

```bash
skill-router-audit <SKILL_ROOT> \
  --format json \
  --output audit.redacted.json \
  --redact
```

## Catalog Shape

- Skills discovered by the auditor: 911
- Categories detected: 8
- Findings: 808
- Potential overlaps at the default threshold: 287,912

Category distribution:

| Category | Skills |
| --- | ---: |
| operations | 790 |
| developer-tools | 48 |
| browser | 22 |
| platform-automation | 15 |
| media | 14 |
| documents | 13 |
| data | 6 |
| general | 3 |

Finding distribution:

| Severity | Count |
| --- | ---: |
| high | 1 |
| medium | 807 |

Most common findings:

| Finding | Count |
| --- | ---: |
| No negative-trigger guidance found. | 800 |
| Description is very short. | 4 |
| Description uses mostly generic terms. | 3 |
| Duplicate skill name appears 2 times. | 1 |

## What The Audit Revealed

The most important signal was not missing names or broken files. It was boundary
quality. Most skills had enough positive description to be discoverable, but did
not say when they should not be used. In a small catalog that can be survivable.
In a catalog with hundreds of tools, it makes routing noisy.

The overlap results also showed a common catalog pattern: many automation skills
share a generated instruction template. That is useful for consistent behavior,
but it creates very high lexical similarity. If routing uses plain descriptions
or naive keyword retrieval, the common template can overwhelm the few words that
actually distinguish one integration from another.

Representative top overlap pairs from the redacted run:

| Left | Right | Score | Shared signal |
| --- | --- | ---: | --- |
| artifacts-builder | web-artifacts-builder | 0.971 | artifact, build, bundle, avoid |
| abstract-automation | composio-automation | 0.955 | api, app, auth, client |
| abyssale-automation | composio-automation | 0.955 | api, app, auth, client |
| acculynx-automation | composio-automation | 0.955 | api, app, auth, client |
| affinity-automation | composio-automation | 0.955 | api, app, auth, client |

## Practical Remediation Plan

1. Add negative-trigger guidance to every high-traffic skill.
2. Split generated boilerplate from routing descriptions, so retrieval focuses
   on the domain-specific part.
3. Add a category-first routing policy and only recall candidates inside the
   selected category.
4. Treat duplicate skill names as high priority because they make reports and
   routing explanations ambiguous.
5. Track overlap count as a CI baseline. Do not require zero conflicts on a
   mature catalog immediately; reduce the baseline as descriptions improve.

## Example CI Gate

For an existing large catalog, start with a report-only run:

```bash
skill-router-audit <SKILL_ROOT> \
  --format markdown \
  --output skill-router-report.md \
  --redact
```

After the first cleanup pass, enable a conservative gate:

```bash
skill-router-audit <SKILL_ROOT> \
  --format markdown \
  --output skill-router-report.md \
  --redact \
  --fail-on high
```

Once high-priority problems are fixed, tighten the gate by setting a known
overlap baseline:

```bash
skill-router-audit <SKILL_ROOT> \
  --format markdown \
  --output skill-router-report.md \
  --redact \
  --fail-on high \
  --max-overlaps <CURRENT_BASELINE>
```

## Redaction Notes

The report was generated with `--redact`, then scanned for local usernames,
absolute Windows home paths, common email domains from the environment, GitHub
tokens, OpenAI-style keys, and organization/user IDs. No raw report is published
with this repository.

