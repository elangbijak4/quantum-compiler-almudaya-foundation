# 09. JSON & Automation Guide

Learn how to use `--format json` for machine-readable integration and automated research scripts.

---

## Machine-Readable JSON Invocations

Add `--format json` before any command:

```bash
python -m src.application.cli.main --format json compile "x = 5"
```

---

## JSON Structure

```json
{
  "request_id": "REQ_COMPILE_12345",
  "intent": "compile",
  "status": "SUCCESS",
  "exit_code": 0,
  "error_code": null,
  "error_message": null,
  "artifact_references": {
    "logical_circuit_id": "LOG_CIRC_DEFAULT",
    "backend_id": "LOCAL_REFERENCE"
  },
  "result_payload": {
    "compiled": true
  },
  "diagnostics": {
    "compilation_mode": "STANDARD"
  },
  "response_hash": "a1b2c3d4e5f67890..."
}
```

Use JSON output to parse exit codes and artifact IDs directly in Python, Bash, or CI/CD pipelines.
