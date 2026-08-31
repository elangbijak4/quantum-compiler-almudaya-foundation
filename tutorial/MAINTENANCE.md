# Tutorial Maintenance Guidelines

How to maintain documentation accuracy as the compiler evolves.

---

## Maintenance Protocol

Whenever CLI commands, options, or Application Contracts are modified:
1. **Help Audit**: Run `python -m src.application.cli.main --help` and verify `tutorial/01_command_reference.md`.
2. **Example Execution**: Run `python -W ignore -m unittest discover -s tests/application -p "test_tutorial_examples.py"`.
3. **Tutorial Verification**: Ensure all code snippets in markdown remain copy-paste executable.
