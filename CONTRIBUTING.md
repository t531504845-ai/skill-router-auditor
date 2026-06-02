# Contributing

Contributions are welcome, especially from people maintaining real agent skill
catalogs.

Good first issues:

- Add examples of ambiguous skill pairs.
- Improve category detection rules.
- Add report formats used by CI systems.
- Add tests for frontmatter edge cases.

Before opening a pull request:

```bash
python -m unittest discover -s tests
skill-router-audit examples/sample-skills --format markdown
```

Please keep the project dependency-light. Optional integrations are welcome, but
the core CLI should remain useful with the Python standard library.

