# APPLICATION / PRODUCT LAYER — CLI ERROR & EXIT CODE REFERENCE

## Exit Code Taxonomy

| Exit Code | Name | Description | Example Core Error Codes |
| :---: | :--- | :--- | :--- |
| `0` | `SUCCESS` | Successful execution | None |
| `1` | `INVALID_USER_INPUT` | Command-line argument error or invalid user input | `INVALID_ARGUMENT`, `INPUT_MISSING` |
| `2` | `COMPUTATIONAL_FAILURE` | Core compilation, mapping, or lowering failure | `QUANTUM_MAPPING_FAILURE`, `LOWERING_FAILURE` |
| `3` | `EXECUTION_FAILURE` | Simulator or backend provider submission failure | `SUBMISSION_FAILURE`, `BACKEND_UNSUPPORTED` |
| `4` | `VERIFICATION_REJECTED` | Statistical verification decision REJECTED | `VERIFICATION_REJECTED` |
| `5` | `VERIFICATION_INCONCLUSIVE` | Statistical verification decision INCONCLUSIVE | `INCONCLUSIVE` |
| `99` | `INTERNAL_ERROR` | Unexpected application or internal exception | `UNHANDLED_EXCEPTION` |
