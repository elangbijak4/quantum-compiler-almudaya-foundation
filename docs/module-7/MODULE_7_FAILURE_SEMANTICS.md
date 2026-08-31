# MODULE 7 — FAILURE SEMANTICS & TAXONOMY

## 1. Disambiguated Failure Taxonomy

1. `BACKEND_UNSUPPORTED`: Selected backend is unregistered or invalid.
2. `BACKEND_CAPABILITY_MISMATCH`: Logical circuit exceeds backend qubit limit, shots limit, or gate capabilities.
3. `LOWERING_FAILURE`: Transpilation decomposition or routing pass fails.
4. `TOPOLOGY_FAILURE`: Routing pass fails to satisfy device connectivity graph.
5. `SUBMISSION_FAILURE`: Network/API failure during job submission.
6. `QUEUE_FAILURE`: Backend queue timeout or job cancellation.
7. `EXECUTION_FAILURE`: Virtual simulator or physical device execution crash.
8. `RESULT_RETRIEVAL_FAILURE`: Failure to download measurement shot counts.
9. `RESULT_VERIFICATION_FAILURE`: Measured shot distribution exceeds statistical error bounds.
10. `AUTHENTICATION_FAILURE`: Network API authentication failure.
11. `CREDENTIAL_FAILURE`: Invalid or revoked provider credential reference.
12. `PROVIDER_UNAVAILABLE`: Target provider endpoint offline or unreachable.
13. `INCONCLUSIVE`: Insufficient evidence to complete execution or verification.

---

## 2. Inconclusive & Failure Policy

- Execution failure does NOT invalidate upstream compilation certification.
- Statistical mismatch does NOT alter Module 4 semantic verification status.
- All execution failures generate explicit failure reports logged to Stage 11 append-only lineage.
