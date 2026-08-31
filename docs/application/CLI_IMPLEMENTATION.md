# APPLICATION / PRODUCT LAYER — PRODUCTION CLI ENGINE IMPLEMENTATION SPECIFICATION

## 1. Executable Entrypoint

The production CLI executable is implemented in `src/application/cli/main.py` and exported via `src/application/cli/__init__.py`.

### Architectural Position:
```
  CLI Entrypoint (main.py) -> CLIRequestAdapter -> ApplicationContractService -> Frozen Core (Modules 1–7)
```

- **Executable Entrypoint**: `quantum-compiler` (`src/application/cli/main.py:main`)
- **Version**: `v1.0.0`
- **Output Formats**: `--format human` (default text) or `--format json` (machine-readable JSON).

---

## 2. Invariant Compliance
- **Core Freeze**: Modules 1–7 source code contains ZERO edits. `CORE MUTATION = NONE`.
- **Dependency Direction**: `CLI -> Application Contract -> Core`. Zero direct imports of `src/module1` .. `src/module7` in `src/application/cli/`.
- **Security & Credential Isolation**: Zero secret tokens stored in request/response payloads or CLI outputs. Non-sensitive `credential_ref` only.
- **Execution Limits**: `CLOUD EXECUTION = 0%`, `HARDWARE EXECUTION = 0%`, `NOISE SIMULATION = 0%`.
