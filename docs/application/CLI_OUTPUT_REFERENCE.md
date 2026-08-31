# APPLICATION / PRODUCT LAYER — CLI OUTPUT REFERENCE SPECIFICATION

## Output Modes

### 1. Human-Readable Output Format (`--format human`)
```text
=== Quantum Compiler CLI [COMPILE] ===
Operation    : compile
Status       : SUCCESS
Exit Code    : 0 (SUCCESS)
Request ID   : REQ_CLI_COMPILE
Response Hash: a1b2c3d4e5f67890...
--- Artifact References ---
  logical_circuit_id: LOG_CIRC_DEFAULT
  backend_id: LOCAL_REFERENCE
--- Evidence & Result Payload ---
  compiled: True
  qubits: 2
```

### 2. Machine-Readable JSON Output Format (`--format json`)
```json
{
  "request_id": "REQ_CLI_COMPILE",
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
    "compiled": true,
    "qubits": 2
  },
  "diagnostics": {
    "compilation_mode": "STANDARD"
  },
  "response_hash": "a1b2c3d4e5f67890..."
}
```
