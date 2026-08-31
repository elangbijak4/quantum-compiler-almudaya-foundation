# MODULE 7 STAGE 5 — FAILURE TAXONOMY & ERROR HANDLING

| Error Code | Trigger Condition | Outcome Decision |
| :--- | :--- | :---: |
| `RESULT_RETRIEVAL_FAILURE` | Missing or malformed provider execution result. | `INCONCLUSIVE` |
| `INSUFFICIENT_SHOTS` | Observed shots $N_{\text{observed}} < N_{\text{min}}$. | `INCONCLUSIVE` |
| `REFERENCE_MISMATCH` | Reference distribution native circuit hash does not match execution result. | `INCONCLUSIVE` |
| `BITSTRING_AMBIGUITY` | Bitstring ordering or width mismatch between result and reference. | `INCONCLUSIVE` |
| `THRESHOLD_EXCEEDED` | Hellinger or KS distance strictly exceeds configured policy threshold. | `REJECTED` |
| `NUMERICAL_ERROR` | `NaN` or infinite probability values encountered. | `INCONCLUSIVE` |
